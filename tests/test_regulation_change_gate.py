from __future__ import annotations

import unittest
from unittest.mock import patch

from narzedzia.validate_regulation_change import (
    DOCX,
    SOURCE,
    changed_paths,
    validate_changes,
)


class RegulationChangeGateTests(unittest.TestCase):
    def test_non_regulation_change_does_not_require_a_decision(self):
        validate_changes({"README.md": "M"})

    def test_markdown_change_requires_generated_docx_and_decision_card(self):
        with self.assertRaisesRegex(ValueError, "wygenerowanego DOCX.*karty decyzji DR"):
            validate_changes({SOURCE: "M"})

    def test_complete_regulation_change_is_accepted(self):
        validate_changes(
            {SOURCE: "M", DOCX: "M", "_decyzje/DR-018-korekta.md": "A"}
        )

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
