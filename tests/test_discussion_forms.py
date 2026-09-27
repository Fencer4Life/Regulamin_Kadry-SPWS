from __future__ import annotations

import unittest
from pathlib import Path

from narzedzia.create_decision_from_discussion import parse_discussion_form, render_card
from narzedzia.sync_discussions import normalize_discussions

ROOT = Path(__file__).resolve().parents[1]


class DiscussionFormTests(unittest.TestCase):
    def discussion(self, body: str) -> dict:
        return {
            "html_url": "https://example/101",
            "title": "Wspólna reguła",
            "created_at": "2026-09-27T10:00:00Z",
            "body": body,
        }

    def test_single_document_form_normalizes_scope_result_and_impact(self):
        parsed = parse_discussion_form(
            """### Dokument
Regulamin Zawodów
### Wynik decyzji
Przyjęta
### Uzasadnienie
Powód.
### Fragment Markdown do zastąpienia
Stary zapis.
### Nowe brzmienie Markdown
Nowy zapis.
### Wpływ na drugi regulamin
Nie wymaga zmiany Regulaminu Reprezentacji.
"""
        )

        self.assertEqual(parsed["dokumenty"], ("zawody",))
        self.assertEqual(parsed["wynik"], "przyjęta")
        self.assertEqual(parsed["wplyw_na_drugi"], "Nie wymaga zmiany Regulaminu Reprezentacji.")
        self.assertEqual(
            parsed["zmiany"],
            {"zawody": {"stary": "Stary zapis.", "nowy": "Nowy zapis."}},
        )

    def test_shared_form_normalizes_two_named_pairs(self):
        parsed = parse_discussion_form(
            """### Wynik decyzji
Odrzucona
### Uzasadnienie
Powód odrzucenia.
### Fragment Regulaminu Reprezentacji do zastąpienia
Stary R.
### Nowe brzmienie Regulaminu Reprezentacji
Nowy R.
### Fragment Regulaminu Zawodów do zastąpienia
Stary Z.
### Nowe brzmienie Regulaminu Zawodów
Nowy Z.
### Spójność obu regulaminów
Oba warianty używają tej samej nazwy Rankingu.
"""
        )

        self.assertEqual(parsed["dokumenty"], ("reprezentacja", "zawody"))
        self.assertEqual(parsed["wynik"], "odrzucona")
        self.assertEqual(set(parsed["zmiany"]), {"reprezentacja", "zawody"})
        self.assertEqual(parsed["spojnosc"], "Oba warianty używają tej samej nazwy Rankingu.")

    def test_legacy_form_defaults_to_accepted_representation_decision(self):
        parsed = parse_discussion_form(
            """### Uzasadnienie
Powód.
### Fragment Markdown do zastąpienia
Stary zapis.
### Nowe brzmienie Markdown
Nowy zapis.
"""
        )

        self.assertEqual(parsed["dokumenty"], ("reprezentacja",))
        self.assertEqual(parsed["wynik"], "przyjęta")

    def test_repository_contains_both_form_contracts(self):
        single = (ROOT / ".github/DISCUSSION_TEMPLATE/propozycje-zmian-regulaminu.yml").read_text(
            encoding="utf-8"
        )
        shared = (
            ROOT / ".github/DISCUSSION_TEMPLATE/wspolna-zmiana-obu-regulaminow.yml"
        ).read_text(encoding="utf-8")

        for fragment in (
            "label: Dokument",
            "Regulamin Reprezentacji",
            "Regulamin Zawodów",
            "Bez zmiany dokumentu",
            "label: Wynik decyzji",
            "label: Wpływ na drugi regulamin",
        ):
            self.assertIn(fragment, single)
        for fragment in (
            "Fragment Regulaminu Reprezentacji do zastąpienia",
            "Nowe brzmienie Regulaminu Reprezentacji",
            "Fragment Regulaminu Zawodów do zastąpienia",
            "Nowe brzmienie Regulaminu Zawodów",
            "label: Spójność obu regulaminów",
            "label: Wynik decyzji",
        ):
            self.assertIn(fragment, shared)

    def test_both_discussion_categories_enter_the_same_workflow_and_public_snapshot(self):
        shared_slug = "wspolna-zmiana-obu-regulaminow"
        for name in ("create-decision.yml", "welcome-discussion.yml"):
            workflow = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
            self.assertIn(shared_slug, workflow)

        node = {
            "number": 101,
            "title": "Wspólna zmiana",
            "url": "https://example/101",
            "createdAt": "2026-09-27T10:00:00Z",
            "closedAt": None,
            "body": "### Koordynator dyskusji\n\n@ala",
            "author": {"login": "ala"},
            "category": {"slug": shared_slug},
            "comments": {"totalCount": 0},
            "labels": {"nodes": []},
        }
        snapshot = normalize_discussions(
            {"data": {"repository": {"discussions": {"nodes": [node]}}}}, "now"
        )
        self.assertEqual([item["number"] for item in snapshot["open_items"]], [101])

    def test_single_document_card_uses_schema_three_and_document_scope(self):
        body = """### Dokument
Regulamin Zawodów
### Wynik decyzji
Przyjęta
### Proponowane rozwiązanie
Przyjąć zmianę.
### Uzasadnienie
Powód.
### Fragment Markdown do zastąpienia
Stary zapis.
### Nowe brzmienie Markdown
Nowy zapis.
### Wpływ na drugi regulamin
Regulamin Reprezentacji zachowuje nadrzędność.
"""

        card = render_card(self.discussion(body), "DR-999")

        self.assertIn("schema_version: 3", card)
        self.assertIn('dokumenty: ["zawody"]', card)
        self.assertIn("## Zmiana — Regulamin Zawodów", card)
        self.assertIn("## Wpływ na spójność dokumentów", card)
        self.assertIn("zmiana_regulaminu: true", card)

    def test_rejected_shared_card_records_both_proposals_without_authorizing_change(self):
        body = """### Wynik decyzji
Odrzucona
### Proponowane rozwiązanie
Nie przyjmować zmiany.
### Uzasadnienie
Powód odrzucenia.
### Fragment Regulaminu Reprezentacji do zastąpienia
Stary R.
### Nowe brzmienie Regulaminu Reprezentacji
Nowy R.
### Fragment Regulaminu Zawodów do zastąpienia
Stary Z.
### Nowe brzmienie Regulaminu Zawodów
Nowy Z.
### Spójność obu regulaminów
Propozycja używała wspólnej nazwy Rankingu.
"""

        card = render_card(self.discussion(body), "DR-999")

        self.assertIn("status: odrzucona", card)
        self.assertIn('dokumenty: ["reprezentacja", "zawody"]', card)
        self.assertIn("## Zmiana — Regulamin Reprezentacji", card)
        self.assertIn("## Zmiana — Regulamin Zawodów", card)
        self.assertIn("zmiana_regulaminu: false", card)
        self.assertIn("proponowana_zmiana: true", card)
        self.assertNotIn("Oczekuje na etykietę `wdrażaj`", card)

    def test_unresolved_result_and_incomplete_coherence_are_rejected(self):
        unresolved = """### Dokument
Regulamin Zawodów
### Wynik decyzji
Do rozstrzygnięcia
### Uzasadnienie
Powód.
### Fragment Markdown do zastąpienia
Stary.
### Nowe brzmienie Markdown
Nowy.
### Wpływ na drugi regulamin
Brak zmiany.
"""
        with self.assertRaisesRegex(ValueError, "wynik decyzji"):
            render_card(self.discussion(unresolved), "DR-999")

        shared_without_coherence = """### Wynik decyzji
Przyjęta
### Uzasadnienie
Powód.
### Fragment Regulaminu Reprezentacji do zastąpienia
Stary R.
### Nowe brzmienie Regulaminu Reprezentacji
Nowy R.
### Fragment Regulaminu Zawodów do zastąpienia
Stary Z.
### Nowe brzmienie Regulaminu Zawodów
Nowy Z.
"""
        with self.assertRaisesRegex(ValueError, "Spójność obu regulaminów"):
            render_card(self.discussion(shared_without_coherence), "DR-999")


if __name__ == "__main__":
    unittest.main(verbosity=2)
