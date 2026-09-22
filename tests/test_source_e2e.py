import tempfile
import unittest
from pathlib import Path

from tests.test_docx_current_contract import CANONICAL_SOURCE, CURRENT_DOCUMENT


class SourceE2ETests(unittest.TestCase):
    def test_decision_changes_exactly_one_xml_text_at_original_position(self):
        from narzedzia.source_evidence import prove
        before = CANONICAL_SOURCE.read_bytes(), CURRENT_DOCUMENT.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            result = prove(CANONICAL_SOURCE, CURRENT_DOCUMENT, Path(directory))
            self.assertEqual(result['coverage']['missing'], [])
            self.assertTrue(result['reference_package_equal'])
            self.assertTrue(result['repeated_build_equal'])
            self.assertEqual(result['e2e_changed_parts'], ['word/document.xml'])
            self.assertTrue(result['e2e_only_expected_replacement'])
            self.assertEqual(result['e2e_occurrences'], 1)
            self.assertEqual(list(Path(directory).glob('*.podglad.md')), [])
        self.assertEqual(before, (CANONICAL_SOURCE.read_bytes(), CURRENT_DOCUMENT.read_bytes()))
