from __future__ import annotations

import unittest
from pathlib import Path

from narzedzia.create_decision_from_discussion import parse_discussion_form
from narzedzia.sync_discussions import normalize_discussions

ROOT = Path(__file__).resolve().parents[1]


class DiscussionFormTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
