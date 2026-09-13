from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommissionGuideTests(unittest.TestCase):
    def test_decision_cards_and_discussion_form_have_public_return_links(self):
        decision = (ROOT / "_layouts/decision.html").read_text(encoding="utf-8")
        discussion_form = (ROOT / ".github/DISCUSSION_TEMPLATE/propozycje-zmian-regulaminu.yml").read_text(encoding="utf-8")
        self.assertEqual(decision.count("/?strona=1&amp;na_stronie=20"), 2)
        self.assertEqual(decision.count("Powrót do Rejestru Decyzji"), 2)
        self.assertIn("https://fencer4life.github.io/Regulamin_Kadry-SPWS/dyskusje/", discussion_form)

    def test_new_discussion_receives_persistent_return_link(self):
        workflow = ROOT / ".github/workflows/welcome-discussion.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        for value in (
            "types: [created]",
            "propozycje-zmian-regulaminu",
            "discussions: write",
            "https://fencer4life.github.io/Regulamin_Kadry-SPWS/dyskusje/",
            "addDiscussionComment",
        ):
            self.assertIn(value, text)

    def test_discussion_form_has_only_two_required_fields(self):
        text = (ROOT / ".github/DISCUSSION_TEMPLATE/propozycje-zmian-regulaminu.yml").read_text(encoding="utf-8")
        self.assertEqual(text.count("required: true"), 2)
        for value in ("Koordynator dyskusji", "Problem", "Priorytet", "Obszar", "Proponowane rozwiązanie", "Powiązane decyzje"):
            self.assertIn(value, text)
        self.assertNotIn("Dlaczego warto", text)
        self.assertNotIn("Czy temat dotyczy obecnego sezonu", text)

    def test_public_guide_explains_roles_sync_and_full_process(self):
        guide = ROOT / "przewodnik.html"
        self.assertTrue(guide.is_file())
        text = guide.read_text(encoding="utf-8") + (ROOT / "_includes/process-diagrams.html").read_text(encoding="utf-8")
        for value in ("Koordynator dyskusji", "Redaktor regulaminu", "co 15 minut", "Rozstrzygnięta", "FORMULARZ-ROZSTRZYGNIECIA", "swimlane", "Tak / Nie?", "DOKUMENTACJA<br>DECYZJI"):
            self.assertIn(value, text)
        self.assertNotIn("Redaktor prowadzący", text)

    def test_public_guide_preserves_both_approved_diagrams_and_legend(self):
        guide = (ROOT / "przewodnik.html").read_text(encoding="utf-8")
        self.assertIn("{% include process-diagrams.html %}", guide)
        text = (ROOT / "_includes/process-diagrams.html").read_text(encoding="utf-8")
        for value in (
            "grid-template-columns:150px repeat(7,1fr)",
            'aria-label="Diagram statusów dyskusji"',
            "Formularz wyniku",
            "GitHub: OUTDATED · bez DR",
            "GitHub: DUPLICATE · bez nowej DR",
            "Artefakty, które powstają",
            "Zmieniony regulamin DOCX",
            "Notacja",
        ):
            self.assertIn(value, text)

    def test_resolution_template_exists_and_is_linked_from_guide(self):
        template = ROOT / "szablony/formularz-rozstrzygniecia.md"
        guide = (ROOT / "przewodnik.html").read_text(encoding="utf-8") if (ROOT / "przewodnik.html").exists() else ""
        self.assertTrue(template.is_file())
        self.assertIn("formularz-rozstrzygniecia.md", guide)


if __name__ == "__main__":
    unittest.main(verbosity=2)
