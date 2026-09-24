from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommissionGuideTests(unittest.TestCase):
    def test_decision_cards_and_discussion_form_have_public_return_links(self):
        decision = (ROOT / "_layouts/decision.html").read_text(encoding="utf-8")
        links = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in ("_layouts/default.html", "dyskusje.html", "przewodnik.html"))
        self.assertEqual(decision.count("/?strona=1&amp;na_stronie=20"), 2)
        self.assertEqual(decision.count("Powrót do Rejestru Decyzji"), 2)
        self.assertEqual(links.count("discussions/new?category=propozycje-zmian-regulaminu\""), 3)
        self.assertNotIn("&amp;title=", links)
        self.assertNotIn("&amp;body=", links)

    def test_native_discussion_category_form_uses_supported_schema(self):
        form = ROOT / ".github/DISCUSSION_TEMPLATE/propozycje-zmian-regulaminu.yml"
        self.assertTrue(form.is_file())
        text = form.read_text(encoding="utf-8")
        top_level = {
            line.split(":", 1)[0]
            for line in text.splitlines()
            if line and not line.startswith((" ", "#")) and ":" in line
        }
        self.assertLessEqual(top_level, {"title", "labels", "body"})
        self.assertNotIn("name", top_level)
        self.assertNotIn("description", top_level)
        for value in (
            "title:",
            "body:",
            "id: coordinator",
            "label: Koordynator dyskusji",
            "id: problem",
            "label: Problem",
            "id: priority",
            "type: dropdown",
            "id: area",
            "id: current_markdown",
            "label: Fragment Markdown do zastąpienia",
            "id: replacement_markdown",
            "label: Nowe brzmienie Markdown",
            "id: related",
            "label: Zależy od",
        ):
            self.assertIn(value, text)

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

    def test_public_guide_explains_roles_sync_and_full_process(self):
        guide = ROOT / "przewodnik.html"
        self.assertTrue(guide.is_file())
        text = guide.read_text(encoding="utf-8") + (ROOT / "_includes/process-diagrams.html").read_text(encoding="utf-8")
        for value in ("Koordynator dyskusji", "Redaktor regulaminu", "co 15 minut", "Rozstrzygnięta", "Uzasadnienie", "swimlane", "Decyzja?", "DOKUMENTACJA<br>DECYZJI", "Zamknięte dyskusje i decyzje", "uruchamia Release jeszcze raz", "Odśwież dane", "cache GitHub Pages"):
            self.assertIn(value, text)
        self.assertNotIn("Redaktor prowadzący", text)

    def test_public_guide_documents_the_operational_docx_review(self):
        text = (ROOT / "przewodnik.html").read_text(encoding="utf-8")
        for value in (
            "Dwie ścieżki dokumentu: pełna i szybka",
            "Redaktor uzupełnia dane wyłącznie w dyskusji; karta powstaje automatycznie.",
            "sekcji <b>Artifacts</b>",
            "regulamin-candidate",
            "Request changes",
            "Release nie jest dodatkowym krokiem akceptacji",
        ):
            self.assertIn(value, text)
        self.assertNotIn("Planowana szybka ścieżka", text)

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

    def test_status_diagram_is_unchanged_and_decision_diagram_shows_both_docx_paths(self):
        text = (ROOT / "_includes/process-diagrams.html").read_text(encoding="utf-8")
        status = text.split('<h3>Status dyskusji</h3>', 1)[1].split(
            '<h3>Jak decyzja wybiera ścieżkę dokumentu</h3>', 1
        )[0]
        self.assertIn("OTWARTA", status)
        self.assertIn("DYSKUSJA", status)
        self.assertIn("ROZSTRZYGNIĘTA", status)
        self.assertIn("PORZUCONA", status)
        self.assertIn("DUPLIKAT", status)
        self.assertNotIn("redakcja-bez-zmiany-sensu", status)

        decision = text.split(
            '<h3>Jak decyzja wybiera ścieżkę dokumentu</h3>', 1
        )[1].split('<h3>Artefakty, które powstają</h3>', 1)[0]
        for value in (
            'aria-label="Diagram wyboru pełnej lub szybkiej ścieżki decyzji"',
            "Czy ma etykietę",
            "redakcja-bez-zmiany-sensu",
            "SZYBKA ŚCIEŻKA",
            "PEŁNA ŚCIEŻKA",
            "korekta bez zmiany sensu",
            "zmiana sensu lub potrzeba oceny",
            "Automat sam zmienia Markdown",
            "Automatyczna karta → wdrażaj na PR",
            "Artefakt DOCX",
            "Approve",
            "Request changes",
            "Release",
        ):
            self.assertIn(value, decision)

    def test_guide_uses_direct_card_creation_without_resolution_template(self):
        template = ROOT / "szablony/formularz-rozstrzygniecia.md"
        guide = (ROOT / "przewodnik.html").read_text(encoding="utf-8") if (ROOT / "przewodnik.html").exists() else ""
        self.assertFalse(template.exists())
        self.assertNotIn("formularz-rozstrzygniecia.md", guide)
        self.assertIn("Nie trzeba niczego przepisywać do komentarza.", guide)


if __name__ == "__main__":
    unittest.main(verbosity=2)
