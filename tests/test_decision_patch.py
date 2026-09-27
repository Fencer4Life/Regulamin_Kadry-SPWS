import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from narzedzia.decision_patch import (
    apply_decision,
    apply_registered_decision,
    format_document_fragments,
    format_fragments,
    read_fragments,
    replace_exact,
)
from narzedzia.regulation_registry import all_regulations
from tests.test_docx_current_contract import CANONICAL_SOURCE, CURRENT_DOCUMENT


class DecisionPatchTests(unittest.TestCase):
    def test_shared_registered_change_is_atomic_when_second_build_fails(self):
        from narzedzia.decision_patch import normalize_and_build as real_build

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = {}
            for regulation in all_regulations():
                source = regulation.source_path(root)
                output = regulation.docx_path(root)
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(regulation.source_path().read_bytes())
                output.write_bytes(regulation.docx_path().read_bytes())
                sources[regulation.identifier] = source
            old_representation = "<!-- unit:cel-glowny -->"
            old_competition = "<!-- unit:cel-glowny -->"
            card = root / "DR-999.md"
            card.write_text(
                '---\nstatus: przyjęta\ndokumenty: ["reprezentacja", "zawody"]\n---\n\n'
                + format_document_fragments(
                    "reprezentacja", old_representation, old_representation + " [TEST R]"
                )
                + format_document_fragments(
                    "zawody", old_competition, old_competition + " [TEST Z]"
                ),
                encoding="utf-8",
            )
            protected = [
                path
                for regulation in all_regulations()
                for path in (regulation.source_path(root), regulation.docx_path(root))
            ] + [card]
            before = {path: path.read_bytes() for path in protected}
            calls = 0

            def fail_second(source, output):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise ValueError("second build")
                return real_build(source, output)

            with patch("narzedzia.decision_patch.normalize_and_build", side_effect=fail_second):
                with self.assertRaisesRegex(ValueError, "second build"):
                    apply_registered_decision(card, root)

            self.assertEqual({path: path.read_bytes() for path in protected}, before)
            apply_registered_decision(card, root)
            self.assertIn("[TEST R]", sources["reprezentacja"].read_text(encoding="utf-8"))
            self.assertIn("[TEST Z]", sources["zawody"].read_text(encoding="utf-8"))
            self.assertIn("applied-source-sha256:", card.read_text(encoding="utf-8"))

    def test_decision_before_after_changes_annex_table_without_preview(self):
        from docx import Document

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, docx, card = root / "source.md", root / "source.docx", root / "DR-999.md"
            source.write_bytes(CANONICAL_SOURCE.read_bytes())
            old = next(
                line for line in source.read_text().splitlines() if line.startswith("| 4 | 54,3 |")
            )
            new = old.replace("54,3", "54,4", 1)
            card.write_text("---\nstatus: przyjęta\n---\n" + format_fragments(old, new))
            apply_decision(card, source, docx)
            self.assertIn(new, source.read_text())
            self.assertFalse(source.with_suffix(".podglad.md").exists())
            self.assertTrue(
                any(
                    t.cell(1, 1).text == "54,4"
                    for t in Document(docx).tables
                    if len(t.columns) == 11
                )
            )

    def test_template_redirects_author_to_discussion_not_manual_card(self):
        template = (CANONICAL_SOURCE.parents[1] / "szablony/nowa-decyzja.md").read_text()
        self.assertIn("Nie twórz ani nie uzupełniaj karty ręcznie", template)
        self.assertIn("Fragment Markdown do zastąpienia", template)
        self.assertIn("Nowe brzmienie Markdown", template)
        self.assertIn("Uzasadnienie", template)
        self.assertIn("Na PR nadaj `wdrażaj`", template)
        with self.assertRaises(ValueError):
            read_fragments(template)

    def test_fragment_roundtrip_preserves_indent_and_headings(self):
        old = "### [section:test] Test\n   1) [unit:a] Dawne."
        new = "### [section:test] Test\n   1) [unit:a] Nowe."
        self.assertEqual(read_fragments(format_fragments(old, new)), (old, new))
        self.assertEqual(
            replace_exact("prefix\n" + old + "\nsuffix", old, new), "prefix\n" + new + "\nsuffix"
        )

    def test_missing_repeated_and_unchanged_fragments_are_rejected(self):
        for source, old, new in [
            ("aa aa", "aa", "bb"),
            ("aaa", "aa", "bb"),
            ("xx", "aa", "bb"),
            ("aa", "aa", "aa"),
            ("aa", "", "bb"),
        ]:
            with self.assertRaises(ValueError):
                replace_exact(source, old, new)

    def test_failed_generation_preserves_source_docx_and_card(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, docx, card = root / "source.md", root / "source.docx", root / "DR-999.md"
            source.write_bytes(CANONICAL_SOURCE.read_bytes())
            docx.write_bytes(CURRENT_DOCUMENT.read_bytes())
            card.write_text(
                "---\nstatus: przyjęta\n---\n"
                + format_fragments("weteraniszermierki.pl", "www.weteraniszermierki.pl")
            )
            original = [p.read_bytes() for p in (source, docx, card)]
            with patch(
                "narzedzia.decision_patch.normalize_and_build", side_effect=ValueError("build")
            ):
                with self.assertRaises(ValueError):
                    apply_decision(card, source, docx)
            self.assertEqual(original, [p.read_bytes() for p in (source, docx, card)])

    def test_accepted_card_builds_all_outputs_and_rejects_second_application(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, docx, card = root / "source.md", root / "source.docx", root / "DR-999.md"
            source.write_bytes(CANONICAL_SOURCE.read_bytes())
            old = "weteraniszermierki.pl"
            card.write_text("---\nstatus: przyjęta\n---\n" + format_fragments(old, "www." + old))
            apply_decision(card, source, docx)
            self.assertTrue(docx.is_file())
            self.assertIn("www." + old, source.read_text())
            self.assertFalse(source.with_suffix(".podglad.md").exists())
            with self.assertRaises(ValueError):
                apply_decision(card, source, docx)

    def test_workflow_updates_existing_pr_and_has_no_llm_dependency(self):
        workflow = (
            CANONICAL_SOURCE.parents[1] / ".github/workflows/apply-decision.yml"
        ).read_text()
        for expected in (
            "workflow_dispatch:",
            "decision_patch",
            "regulations verify --all",
            "unittest discover",
            "gh pr view",
            "--draft",
            'git add -- "$card" "${document_paths[@]}"',
            '"${doc_args[@]}"',
        ):
            self.assertIn(expected, workflow)
        for forbidden in (
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "curl",
            "--force",
            "git push origin main",
        ):
            self.assertNotIn(forbidden, workflow)

    def test_unaccepted_decision_cannot_modify_source(self):
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / "card.md"
            card.write_text("---\nstatus: projekt\n---\n" + format_fragments("a", "b"))
            with self.assertRaises(ValueError):
                apply_decision(card, CANONICAL_SOURCE, Path(directory) / "out.docx")

    def test_rejected_registered_decision_cannot_modify_a_document(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regulation = next(item for item in all_regulations() if item.identifier == "zawody")
            source, output = regulation.source_path(root), regulation.docx_path(root)
            source.parent.mkdir(parents=True)
            source.write_bytes(regulation.source_path().read_bytes())
            output.write_bytes(regulation.docx_path().read_bytes())
            card = root / "DR-999.md"
            card.write_text(
                '---\nstatus: odrzucona\ndokumenty: ["zawody"]\n---\n\n'
                + format_document_fragments("zawody", "PROJEKT", "PROJEKT ODRZUCONY"),
                encoding="utf-8",
            )
            before = source.read_bytes(), output.read_bytes(), card.read_bytes()
            with self.assertRaisesRegex(ValueError, "wyłącznie decyzje.*przyjęta"):
                apply_registered_decision(card, root)
            self.assertEqual(before, (source.read_bytes(), output.read_bytes(), card.read_bytes()))

    def test_workflow_does_not_require_uninstalled_ripgrep(self):
        workflow = (
            CANONICAL_SOURCE.parents[1] / ".github/workflows/apply-decision.yml"
        ).read_text()
        self.assertNotRegex(workflow, r"\brg\b")

    def test_ambiguous_or_unclosed_fields_are_rejected(self):
        for text in (
            format_fragments("old", "new") + format_fragments("other", "new"),
            format_fragments("old", "new").rsplit("```", 1)[0],
        ):
            with self.assertRaises(ValueError):
                read_fragments(text)

    def test_bad_structure_keeps_original_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, docx, card = root / "source.md", root / "source.docx", root / "card.md"
            source.write_bytes(CANONICAL_SOURCE.read_bytes())
            docx.write_bytes(CURRENT_DOCUMENT.read_bytes())
            card.write_text(
                "---\nstatus: przyjęta\n---\n"
                + format_fragments(
                    "<!-- unit:publikacja-rankingu-zrodlo -->", "<!-- unit:INVALID-ID -->"
                )
            )
            before = source.read_bytes(), docx.read_bytes(), card.read_bytes()
            with self.assertRaises(ValueError):
                apply_decision(card, source, docx)
            self.assertEqual(before, (source.read_bytes(), docx.read_bytes(), card.read_bytes()))
