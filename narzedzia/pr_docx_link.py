"""Publish deterministic, commit-pinned DOCX review links without changing files."""
import argparse
import json
import re
import subprocess
from urllib.parse import quote

from narzedzia.validate_regulation_change import SOURCE, DOCX

START = '<!-- regulamin-docx:start -->'
END = '<!-- regulamin-docx:end -->'


def gh_api(endpoint, *, payload=None):
    args = ['gh', 'api', endpoint]
    if payload is not None:
        args += ['--method', 'PATCH', '--input', '-']
    result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                            check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def update_body(body, repo, sha, run_url):
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo) or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Niepoprawne repozytorium lub SHA dokumentu')
    if run_url and not re.fullmatch(r'https://github\.com/[\w./-]+', run_url):
        raise ValueError('Niepoprawny adres uruchomienia')
    body = body or ''
    if START in body or END in body:
        if body.count(START) != 1 or body.count(END) != 1 or body.index(END) < body.index(START):
            raise ValueError('Uszkodzona sekcja linku DOCX w opisie PR')
        begin, end = body.index(START), body.index(END) + len(END)
        tail = body[end:]
        if tail.startswith('\n\n'):
            tail = tail[2:]
        body = body[:begin] + tail
    base = f'https://github.com/{repo}'
    section = (f'{START}\n## DOCX do sprawdzenia\n\n'
               f'**[Pobierz DOCX]({base}/raw/{sha}/{quote(DOCX, safe="/")})**'
               f' · [Źródło Markdown]({base}/blob/{sha}/{quote(SOURCE, safe="/")})\n\n'
               f'Wersja dokumentu: `{sha}`. Otwórz DOCX w Wordzie przed zatwierdzeniem PR.\n')
    if run_url:
        section += f'\n[Uruchomienie automatu]({run_url})\n'
    return section + f'{END}\n\n' + body


def publish(repo, number, sha, run_url, *, api=gh_api):
    endpoint = f'repos/{repo}/pulls/{int(number)}'

    def check(pr):
        if pr['head']['sha'] != sha or pr['head']['repo']['full_name'] != repo:
            raise ValueError('PR zmienił wersję lub pochodzi z innego repozytorium')

    pr = api(endpoint)
    check(pr)
    tree = api(f'repos/{repo}/git/trees/{sha}?recursive=1')
    paths = {item['path'] for item in tree['tree'] if item['type'] == 'blob'}
    if tree.get('truncated') or not {SOURCE, DOCX}.issubset(paths):
        raise ValueError('Brak potwierdzonego Markdown lub DOCX w commicie')
    # Refresh immediately before writing: preserve recent human edits, reject stale results.
    pr = api(endpoint)
    check(pr)
    body = update_body(pr.get('body'), repo, sha, run_url)
    if body != (pr.get('body') or ''):
        api(endpoint, payload={'body': body})
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('pr', type=int)
    parser.add_argument('sha')
    parser.add_argument('--run-url', default='')
    args = parser.parse_args()
    publish(args.repo, args.pr, args.sha, args.run_url)
    print(f'Link DOCX opublikowany w PR #{args.pr}')


if __name__ == '__main__':
    main()
