from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from narzedzia.normalize_regulamin_markdown import normalize_source
from narzedzia.regulation_registry import Regulation
from narzedzia.regulations import build_regulations, select_regulations, verify_regulations
from tests.test_docx_current_contract import CANONICAL_SOURCE

COMPETITION_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "regulamin-wspolzawodnictwa"
    / "Regulamin-wspolzawodnictwa-sportowego-w-kategorii-Weteran_2026-2027.md"
)


def regulation(identifier: str, directory: str) -> Regulation:
    stem = Path(directory) / identifier
    return Regulation(
        identifier=identifier,
        title=identifier,
        label=f"Regulamin: {identifier}",
        markdown=stem.with_suffix(".md"),
        docx=stem.with_suffix(".docx"),
        artifact=f"regulamin-{identifier}-candidate",
        validators=("ztp", "docx"),
    )


class MultiDocumentBuildTests(unittest.TestCase):
    def test_normalization_preserves_publication_blocks_without_points_annex(self):
        normalized = normalize_source(COMPETITION_SOURCE)

        self.assertIn("<!-- publication:annex-heading -->", normalized)
        self.assertIn("<!-- publication:annex-note -->", normalized)

    def test_selects_one_or_all_registered_documents(self):
        first = regulation("reprezentacja", "a")
        second = regulation("zawody", "b")
        registered = (first, second)

        self.assertEqual(select_regulations(registered, identifiers=("zawody",)), (second,))
        self.assertEqual(select_regulations(registered, all_documents=True), registered)
        with self.assertRaisesRegex(ValueError, "Wybierz dokumenty albo --all"):
            select_regulations(registered)
        with self.assertRaisesRegex(ValueError, "Nieznany dokument"):
            select_regulations(registered, identifiers=("inny",))

    def test_builds_and_verifies_two_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            documents = (regulation("reprezentacja", "a"), regulation("zawody", "b"))
            for item in documents:
                item.source_path(root).parent.mkdir(parents=True, exist_ok=True)
                item.source_path(root).write_bytes(CANONICAL_SOURCE.read_bytes())

            outputs = build_regulations(documents, root=root)

            self.assertEqual(
                outputs,
                tuple(item.docx_path(root).resolve() for item in documents),
            )
            self.assertTrue(all(path.is_file() for path in outputs))
            verify_regulations(documents, root=root)

    def test_failure_of_second_source_preserves_every_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = regulation("reprezentacja", "a")
            second = regulation("zawody", "b")
            for item in (first, second):
                item.source_path(root).parent.mkdir(parents=True, exist_ok=True)
                item.source_path(root).write_bytes(CANONICAL_SOURCE.read_bytes())
                item.docx_path(root).write_bytes(f"old-{item.identifier}".encode())
            second.source_path(root).write_text("niepoprawny Markdown", encoding="utf-8")
            before = {
                path: path.read_bytes()
                for item in (first, second)
                for path in (item.source_path(root), item.docx_path(root))
            }

            with self.assertRaises(ValueError):
                build_regulations((first, second), root=root)

            self.assertEqual({path: path.read_bytes() for path in before}, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
