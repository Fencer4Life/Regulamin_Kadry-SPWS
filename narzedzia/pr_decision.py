"""Apply the single decision in a labelled PR using trusted automation code."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from narzedzia.decision_patch import apply_decision
from narzedzia.prepare_regulamin import verify
from narzedzia.pr_docx_link import gh_api, publish, SOURCE, DOCX

ROOT = Path(__file__).resolve().parents[1]


def load_discussion(repo, number):
    owner, name = repo.split('/')
    result = json.loads(command([
        'gh', 'api', 'graphql', '-f',
        'query=query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){discussion(number:$number){title body url createdAt}}}',
        '-f', f'owner={owner}', '-f', f'name={name}', '-F', f'number={number}',
    ]))
    data = result['data']['repository']['discussion']
    return {'title': data['title'], 'body': data['body'], 'html_url': data['url'],
            'created_at': data['createdAt']}


def refresh_from_discussion(card, repo):
    from narzedzia.create_decision_from_discussion import render_card
    text = card.read_text(encoding='utf-8')
    if '<!-- applied-source-sha256:' in text:
        return
    front = text.split('---', 2)[1]
    def value(key):
        match = re.search(rf'^{key}: (.*)$', front, re.MULTILINE)
        return match[1].strip().strip('"') if match else ''
    url = value('discussion_url')
    match = re.fullmatch(r'https://github.com/' + re.escape(repo) + r'/discussions/(\d+)', url)
    if not match:
        raise ValueError('Dyskusja źródłowa musi należeć do tego repozytorium')
    discussion = load_discussion(repo, int(match[1]))
    if discussion['html_url'] != url:
        raise ValueError('Niezgodny adres dyskusji źródłowej')
    rendered = render_card(discussion, value('id'), value('pr_url'))
    if value('typ') == 'redakcyjna':
        rendered = rendered.replace('typ: merytoryczna', 'typ: redakcyjna', 1)
    card.write_text(rendered, encoding='utf-8')


def select_card(files):
    paths = [f['filename'] for f in files if f.get('status') != 'removed'
             and re.fullmatch(r'_decyzje/DR-\d{3}-[^/]+\.md', f['filename'])]
    if len(paths) != 1:
        raise ValueError('PR musi zawierać dokładnie jedną zmienioną kartę DR')
    return paths[0]


def check_changed_paths(files, card):
    allowed = {card, SOURCE, DOCX}
    if any(f['filename'] not in allowed or f.get('previous_filename', f['filename']) not in allowed
           for f in files):
        raise ValueError('Etykieta wdrażaj obsługuje tylko kartę DR, Markdown i DOCX; kod wymaga osobnego PR')


def dispatch_ci(repo, branch):
    command(['gh', 'workflow', 'run', 'validate.yml', '--repo', repo, '--ref', branch])


def check_pr(pr, repo):
    if (pr['state'] != 'open' or pr['head']['repo']['full_name'] != repo
            or pr['head']['ref'] == pr['base']['ref'] or pr['base']['ref'] != 'main'):
        raise ValueError('Wymagany otwarty PR z tego repozytorium do main')
    if 'wdrażaj' not in {label['name'] for label in pr['labels']}:
        raise ValueError('PR nie ma już etykiety wdrażaj')
    if not re.fullmatch(r'[a-f0-9]{40}', pr['head']['sha']):
        raise ValueError('Niepoprawny SHA gałęzi PR')


def apply_once(card, source, output):
    if re.search(r'<!-- applied-source-sha256:[a-f0-9]{64} -->', card.read_text(encoding='utf-8')):
        verify(source, output)
        return False
    apply_decision(card, source, output)
    verify(source, output)
    return True


def command(args, *, cwd=ROOT, env=None):
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True,
                          stdout=subprocess.PIPE).stdout.strip()


def candidate_checks(docx, source):
    # Never execute scripts supplied by the PR; only trusted tests from this checkout.
    env = {**os.environ, 'REGULAMIN_SOURCE_PATH': str(source), 'REGULAMIN_DOCX_PATH': str(docx)}
    for script in ('test_approved_sections_02_03.py', 'test_docx_pagination.py'):
        command([sys.executable, str(ROOT / 'tests' / script), str(docx)], env=env)
    command([sys.executable, '-m', 'unittest', 'tests.test_docx_publication_safety', '-v'], env=env)


def run(repo, number, run_url):
    endpoint = f'repos/{repo}/pulls/{number}'
    pr = gh_api(endpoint)
    check_pr(pr, repo)
    pages = json.loads(command(['gh', 'api', endpoint + '/files?per_page=100', '--paginate', '--slurp']))
    files = [f for page in pages for f in page]
    card_path = select_card(files)
    check_changed_paths(files, card_path)
    sha, branch = pr['head']['sha'], pr['head']['ref']
    command(['git', 'fetch', 'origin', sha])
    with tempfile.TemporaryDirectory(prefix='decision-pr-') as directory:
        checkout = Path(directory) / 'proposal'
        command(['git', 'worktree', 'add', '--detach', str(checkout), sha])
        try:
            for relative in (card_path, SOURCE, DOCX):
                path = checkout / relative
                if not path.is_file() or not path.resolve().is_relative_to(checkout.resolve()) or path.is_symlink():
                    raise ValueError('Pliki decyzji i dokumentu muszą być zwykłymi plikami wewnątrz PR')
            refresh_from_discussion(checkout / card_path, repo)
            changed = apply_once(checkout / card_path, checkout / SOURCE, checkout / DOCX)
            candidate_checks(checkout / DOCX, checkout / SOURCE)
            latest = gh_api(endpoint)
            check_pr(latest, repo)
            if latest['head']['sha'] != sha:
                raise ValueError('PR zmienił się podczas generowania; nadaj etykietę ponownie')
            if changed:
                command(['git', 'add', '--', card_path, SOURCE, DOCX], cwd=checkout)
                command(['git', 'diff', '--cached', '--check'], cwd=checkout)
                command(['git', '-c', 'user.name=github-actions[bot]', '-c',
                         'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                         'commit', '-m', f'docs: apply decision in PR #{number}'], cwd=checkout)
                sha = command(['git', 'rev-parse', 'HEAD'], cwd=checkout)
                command(['git', 'push', 'origin', f'HEAD:refs/heads/{branch}'], cwd=checkout)
            publish(repo, number, sha, run_url, wait_for_sha=True)
            # GITHUB_TOKEN commits do not reliably start required pull_request CI.
            # Explicit dispatch starts read-only validation without a human action.
            dispatch_ci(repo, branch)
            print(f'PR #{number}: ' + ('wdrożono decyzję i opublikowano DOCX' if changed
                                      else 'decyzja już wdrożona; bez kolejnej zmiany plików'))
        finally:
            # Only the temporary worktree created above; never a user checkout.
            command(['git', 'worktree', 'remove', '--force', str(checkout)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('pr', type=int)
    parser.add_argument('--run-url', default='')
    args = parser.parse_args()
    run(args.repo, args.pr, args.run_url)


if __name__ == '__main__':
    main()
