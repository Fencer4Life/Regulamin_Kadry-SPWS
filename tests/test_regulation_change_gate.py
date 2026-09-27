from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from narzedzia.decision_patch import format_document_fragments
from narzedzia.regulation_registry import get_regulation
from narzedzia.validate_regulation_change import (
    DOCX,
    SOURCE,
    changed_paths,
    validate_changes,
    validate_pending_decisions,
)


class RegulationChangeGateTests(unittest.TestCase):
    def test_non_regulation_change_does_not_require_a_decision(self):
        validate_changes({"README.md": "M"})

    def test_markdown_change_requires_generated_docx_and_decision_card(self):
        with self.assertRaisesRegex(ValueError, "wygenerowanego DOCX.*karty decyzji DR"):
            validate_changes({SOURCE: "M"})

    def test_complete_regulation_change_is_accepted(self):
        validate_changes({SOURCE: "M", DOCX: "M", "_decyzje/DR-018-korekta.md": "A"})

    def test_each_registered_markdown_requires_its_docx_and_a_decision(self):
        competition = get_regulation("zawody")
        source, docx = str(competition.markdown), str(competition.docx)
        with self.assertRaisesRegex(ValueError, "wygenerowanego DOCX.*karty decyzji DR"):
            validate_changes({source: "M"})
        validate_changes({source: "M", docx: "M", "_decyzje/DR-099-zawody.md": "A"})

    def test_card_cannot_authorize_changes_to_an_unlisted_regulation(self):
        representation = get_regulation("reprezentacja")
        competition = get_regulation("zawody")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            card = root / "_decyzje" / "DR-099-test.md"
            card.parent.mkdir()
            card.write_text(
                "---\nschema_version: 3\nstatus: przyjęta\n"
                'dokumenty: ["reprezentacja"]\nzmiana_regulaminu: true\n---\n\n'
                + format_document_fragments("reprezentacja", "stary", "nowy")
                + "\n<!-- applied-source-sha256:"
                + "a" * 64
                + " -->\n",
                encoding="utf-8",
            )
            changes = {
                str(card.relative_to(root)): "A",
                str(representation.markdown): "M",
                str(representation.docx): "M",
                str(competition.markdown): "M",
                str(competition.docx): "M",
            }
            with self.assertRaisesRegex(ValueError, "niewskazanych przez kartę"):
                validate_pending_decisions(changes, root)

    def test_initial_markdown_migration_requires_docx_but_not_decision(self):
        validate_changes({SOURCE: "A", DOCX: "M"})

        with self.assertRaisesRegex(ValueError, "wygenerowanego DOCX"):
            validate_changes({SOURCE: "A"})

    @patch("narzedzia.validate_regulation_change.subprocess.run")
    def test_git_diff_preserves_the_polish_docx_path(self, run):
        run.return_value.stdout = f"A\t{SOURCE}\nM\t{DOCX}\n"

        self.assertEqual(changed_paths("base"), {SOURCE: "A", DOCX: "M"})
        command = run.call_args.args[0]
        self.assertIn("core.quotePath=false", command)


if __name__ == "__main__":
    unittest.main(verbosity=2)
