from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from narzedzia.regulation_registry import all_regulations, get_regulation, load_registry

ROOT = Path(__file__).resolve().parents[1]


class RegulationRegistryTests(unittest.TestCase):
    def test_registry_defines_two_unique_documents(self):
        regulations = all_regulations()

        self.assertEqual([item.identifier for item in regulations], ["reprezentacja", "zawody"])
        self.assertEqual(len({item.markdown for item in regulations}), 2)
        self.assertEqual(len({item.docx for item in regulations}), 2)
        self.assertEqual(len({item.label for item in regulations}), 2)
        self.assertEqual(len({item.artifact for item in regulations}), 2)
        self.assertEqual(
            [item.label for item in regulations],
            ["Regulamin: Reprezentacja", "Regulamin: Zawody"],
        )

    def test_paths_are_relative_safe_and_have_expected_extensions(self):
        for regulation in all_regulations():
            self.assertFalse(regulation.markdown.is_absolute())
            self.assertFalse(regulation.docx.is_absolute())
            self.assertNotIn("..", regulation.markdown.parts)
            self.assertNotIn("..", regulation.docx.parts)
            self.assertEqual(regulation.markdown.suffix, ".md")
            self.assertEqual(regulation.docx.suffix, ".docx")
            self.assertEqual(regulation.markdown.with_suffix(""), regulation.docx.with_suffix(""))
            self.assertTrue(regulation.source_path().is_file())
            self.assertTrue(regulation.docx_path().is_file())

    def test_unknown_document_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Nieznany dokument"):
            get_regulation("inny")

    def test_duplicate_and_escaping_paths_are_rejected(self):
        invalid = {
            "schema_version": 1,
            "regulations": [
                {
                    "id": "powtorzony",
                    "title": "Pierwszy",
                    "label": "Regulamin: Pierwszy",
                    "markdown": "../poza.md",
                    "docx": "dokument.docx",
                    "artifact": "regulamin-pierwszy-candidate",
                    "validators": ["ztp"],
                },
                {
                    "id": "powtorzony",
                    "title": "Drugi",
                    "label": "Regulamin: Drugi",
                    "markdown": "drugi.md",
                    "docx": "drugi.docx",
                    "artifact": "regulamin-drugi-candidate",
                    "validators": ["ztp"],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "regulations.json"
            path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bezpieczną ścieżką|powtarza się"):
                load_registry(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
