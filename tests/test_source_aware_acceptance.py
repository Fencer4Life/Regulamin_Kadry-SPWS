"""Acceptance checks must follow the candidate source, not frozen legal text."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from docx import Document
from narzedzia.prepare_regulamin import normalize_and_build
from tests.test_docx_current_contract import CANONICAL_SOURCE


class SourceAwareAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.source = cls.root / 'candidate.md'
        text = CANONICAL_SOURCE.read_text()
        line = next(line for line in text.splitlines() if '<!-- unit:zasada-szeroki-wybor -->' in line)
        cls.source.write_text(text.replace(line, line.removesuffix(';') + ' lub zgłoszonych do kalendarza PZSz;'))
        cls.docx = cls.root / 'candidate.docx'
        normalize_and_build(cls.source, cls.docx)

    def check_document(self, document, source=None):
        return subprocess.run(
            [sys.executable, str(Path(__file__).with_name('test_approved_sections_02_03.py')), str(document)],
            env={**os.environ, 'REGULAMIN_SOURCE_PATH': str(source or self.source)},
            text=True, capture_output=True,
        )

    def test_changed_source_and_matching_docx_are_accepted(self):
        result = self.check_document(self.docx)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_docx_from_different_source_is_rejected(self):
        self.assertNotEqual(self.check_document(self.docx, CANONICAL_SOURCE).returncode, 0)

    def test_missing_duplicated_and_changed_paragraphs_are_rejected(self):
        for mutation in ('missing', 'duplicated', 'changed'):
            with self.subTest(mutation=mutation):
                document = Document(self.docx)
                paragraph = next(p for p in document.paragraphs if p.text.startswith('1) szerokiego wyboru'))
                if mutation == 'missing':
                    paragraph._p.getparent().remove(paragraph._p)
                elif mutation == 'duplicated':
                    from copy import deepcopy
                    paragraph._p.addnext(deepcopy(paragraph._p))
                else:
                    paragraph.text += ' NIEZATWIERDZONY DOPISEK'
                output = self.root / (mutation + '.docx')
                document.save(output)
                self.assertNotEqual(self.check_document(output).returncode, 0)

    def test_missing_source_is_not_silently_replaced_with_main(self):
        self.assertNotEqual(self.check_document(self.docx, self.root / 'missing.md').returncode, 0)

    def test_trusted_candidate_checks_receive_candidate_source(self):
        from narzedzia.pr_decision import candidate_checks
        with patch('narzedzia.pr_decision.command') as command:
            candidate_checks(self.docx, self.source)
        acceptance = command.call_args_list[0]
        self.assertEqual(acceptance.kwargs['env']['REGULAMIN_SOURCE_PATH'], str(self.source))
        self.assertNotIn(str(self.root), acceptance.args[0][1])
