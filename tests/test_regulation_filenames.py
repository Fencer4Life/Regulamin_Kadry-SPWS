import unittest
from pathlib import Path

from narzedzia.validate_regulation_change import SOURCE, DOCX


class RegulationFilenameTests(unittest.TestCase):
    def test_source_and_docx_use_the_requested_shared_ascii_stem(self):
        stem = 'Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026'
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(SOURCE, f'regulamin/{stem}.md')
        self.assertEqual(DOCX, f'regulamin/{stem}.docx')
        self.assertTrue((root / SOURCE).is_file())
        self.assertTrue((root / DOCX).is_file())
