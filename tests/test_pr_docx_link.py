import unittest
from unittest.mock import Mock


class PrDocxLinkTests(unittest.TestCase):
    def test_both_existing_paths_publish_links_after_push(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for name in ('apply-decision.yml', 'create-decision.yml'):
            workflow = (root / '.github/workflows' / name).read_text()
            self.assertIn('python -m narzedzia.pr_docx_link', workflow)
            self.assertGreater(workflow.index('python -m narzedzia.pr_docx_link'), workflow.rindex('git push'))

    def test_section_is_first_preserves_description_and_is_idempotent(self):
        from narzedzia.pr_docx_link import update_body
        args = ('Fencer4Life/Regulamin_Kadry-SPWS', 'a' * 40, 'https://github.com/run/1')
        original = 'Opis Redaktora.\n\n- [x] Tak\n'
        once = update_body(original, *args)
        self.assertTrue(once.startswith('<!-- regulamin-docx:start -->'))
        self.assertIn('## DOCX do sprawdzenia', once)
        self.assertTrue(once.endswith(original))
        self.assertIn('/raw/' + 'a' * 40 + '/', once)
        self.assertIn('weteran%C3%B3w', once)
        self.assertEqual(update_body(once, *args), once)
        newer = update_body(once, args[0], 'b' * 40, args[2])
        self.assertEqual(newer.count('## DOCX do sprawdzenia'), 1)
        self.assertNotIn('a' * 40, newer)
        self.assertTrue(newer.endswith(original))

    def test_malformed_markers_and_invalid_sha_are_rejected(self):
        from narzedzia.pr_docx_link import update_body
        for body, sha in [('<!-- regulamin-docx:start -->', 'a' * 40), ('', 'main')]:
            with self.assertRaises(ValueError):
                update_body(body, 'owner/repo', sha, '')

    def test_publish_preserves_latest_body_and_rejects_stale_commit(self):
        from narzedzia.pr_docx_link import publish, SOURCE, DOCX
        sha = 'a' * 40
        pr = {'head': {'sha': sha, 'repo': {'full_name': 'owner/repo'}}, 'body': 'Opis'}
        tree = {'tree': [{'path': p, 'type': 'blob'} for p in (SOURCE, DOCX)]}
        api = Mock(side_effect=[pr, tree, {**pr, 'body': 'Nowszy opis'}, {}])
        publish('owner/repo', 57, sha, '', api=api)
        self.assertTrue(api.call_args.kwargs['payload']['body'].endswith('Nowszy opis'))
        stale = Mock(return_value={**pr, 'head': {**pr['head'], 'sha': 'b' * 40}})
        with self.assertRaises(ValueError):
            publish('owner/repo', 57, sha, '', api=stale)
        self.assertEqual(stale.call_count, 1)

    def test_missing_docx_prevents_publication(self):
        from narzedzia.pr_docx_link import publish
        pr = {'head': {'sha': 'a' * 40, 'repo': {'full_name': 'owner/repo'}}, 'body': ''}
        api = Mock(side_effect=[pr, {'tree': []}])
        with self.assertRaises(ValueError):
            publish('owner/repo', 57, 'a' * 40, '', api=api)
        self.assertEqual(api.call_count, 2)
