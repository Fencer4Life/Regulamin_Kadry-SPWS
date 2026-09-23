import tempfile
import unittest
from pathlib import Path

from narzedzia.docx_model import parse_regulation_source
from narzedzia.normalize_regulamin_markdown import resolve_references
from narzedzia.publication_source import restore_tokens
from tests.test_ztp_model import METADATA


BODY = '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:a] Pierwszy
1. [unit:u1] Pierwszy:
   1) [unit:p1] pierwszy;
   2) [unit:p2] drugi.
2. [unit:u2] Drugi:
   1) [unit:p3] trzeci.
### [section:b] Drugi
1. [unit:u3] Inny paragraf.
'''


class ContextualReferenceTests(unittest.TestCase):
    def model(self, body=BODY):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.md'
            source.write_text(METADATA + body)
            return parse_regulation_source(source)

    def test_direction_and_shortest_unambiguous_address(self):
        model = self.model()
        for current, target, expected in (
            ('p2', 'a/p1', 'pkt 1 powyżej'),
            ('p1', 'a/p2', 'pkt 2 poniżej'),
            ('u1', 'a/u2', 'ust. 2 poniżej'),
            ('u2', 'a/u1', 'ust. 1 powyżej'),
            ('p3', 'a/p2', 'ust. 1 pkt 2 powyżej'),
            ('p1', 'a/p3', 'ust. 2 pkt 1 poniżej'),
            ('p1', 'b/u3', '§ 2 ust. 1'),
        ):
            with self.subTest(current=current, target=target):
                self.assertEqual(resolve_references(model, '{{ref:'+target+'}}', current_unit=current), expected)

    def test_missing_target_and_self_reference_fail(self):
        for target in ('a/missing', 'a/p1'):
            with self.assertRaises(ValueError):
                resolve_references(self.model(), '{{ref:'+target+'}}', current_unit='p1')

    def test_short_visible_forms_keep_the_hidden_target(self):
        for visible in ('pkt 2 powyżej', 'pkt 2 poniżej', 'ust. 1',
                        'ust. 1 pkt 2 powyżej', '§ 1 ust. 1 pkt 2'):
            self.assertEqual(restore_tokens(visible+'<!-- ref:a/p2 -->'), '{{ref:a/p2}}')

    def test_direction_follows_reordering_not_old_visible_numbers(self):
        body = BODY.replace('   1) [unit:p1] pierwszy;\n   2) [unit:p2] drugi.',
                            '   2) [unit:p2] drugi;\n   1) [unit:p1] pierwszy.')
        self.assertEqual(resolve_references(self.model(body), '{{ref:a/p1}}', current_unit='p2'),
                         'pkt 2 poniżej')

    def test_malformed_visible_reference_is_rejected_not_printed(self):
        with self.assertRaises(ValueError):
            restore_tokens('błędny tekst<!-- ref:a/p1 -->')

    def test_real_source_roundtrip_docx_and_coverage(self):
        from docx import Document
        from narzedzia.prepare_regulamin import normalize_and_build, verify
        from narzedzia.source_evidence import coverage
        from tests.test_docx_current_contract import CANONICAL_SOURCE
        with tempfile.TemporaryDirectory() as directory:
            source, docx = Path(directory) / 'source.md', Path(directory) / 'out.docx'
            source.write_bytes(CANONICAL_SOURCE.read_bytes())
            normalize_and_build(source, docx)
            first = source.read_bytes()
            verify(source, docx)
            normalize_and_build(source, docx)
            self.assertEqual(first, source.read_bytes())
            text = '\n'.join(p.text for p in Document(docx).paragraphs)
            for expected in ('ust. 5 poniżej', 'pkt 2 powyżej', 'ust. 2 poniżej', 'pkt 6 powyżej'):
                self.assertIn(expected, text)
                self.assertIn(expected, source.read_text())
            self.assertNotIn('<!--', text)
            self.assertEqual(coverage(source, docx)['missing'], [])
