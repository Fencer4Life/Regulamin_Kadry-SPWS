from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from narzedzia.build_regulamin_docx import build_document
from narzedzia.docx_parity import (
    document_content_contract,
    document_layout_contract,
    normalized_package_sha256,
)
from tests.test_docx_current_contract import CURRENT_DOCUMENT


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranow-w-szermierce_2026.md"
)


class GeneratedDocxTests(unittest.TestCase):
    def test_markdown_source_builds_a_content_identical_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.docx"
            build_document(SOURCE, candidate)
            self.assertTrue(candidate.is_file())
            self.assertEqual(
                document_content_contract(candidate),
                document_content_contract(CURRENT_DOCUMENT),
            )
            self.assertEqual(
                document_layout_contract(candidate),
                document_layout_contract(CURRENT_DOCUMENT),
            )

    def test_build_never_overwrites_the_source_document_implicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.docx"
            before = CURRENT_DOCUMENT.read_bytes()
            build_document(SOURCE, candidate)
            self.assertEqual(CURRENT_DOCUMENT.read_bytes(), before)

    def test_two_builds_have_the_same_normalized_package(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.docx"
            second = Path(directory) / "second.docx"
            build_document(SOURCE, first)
            build_document(SOURCE, second)
            self.assertEqual(
                normalized_package_sha256(first),
                normalized_package_sha256(second),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
