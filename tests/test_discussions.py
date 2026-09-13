from __future__ import annotations

import unittest
import json
import tempfile
from pathlib import Path

from narzedzia.create_decision_from_discussion import create, next_decision_id, parse_resolution
from narzedzia.sync_discussions import normalize_discussions


class DiscussionSnapshotTests(unittest.TestCase):
    def test_next_decision_id_uses_highest_existing_number(self):
        self.assertEqual(next_decision_id(["DR-002-a.md", "DR-016-b.md"]), "DR-017")

    def test_parses_minimal_resolution_form_from_final_comment(self):
        comment = """<!-- FORMULARZ-ROZSTRZYGNIECIA -->
## Formularz rozstrzygnięcia dyskusji
**Wynik:** przyjęta
**Treść decyzji:** Przyjmujemy wariant A.
**Uzasadnienie:** Uzasadnienie A.
**Zmiana regulaminu:** tak
**Odrzucone alternatywy:** Wariant B.
- [x] Potwierdzam zgodność ze stanowiskiem komisji.
"""
        result = parse_resolution(comment)
        self.assertEqual(result["wynik"], "przyjęta")
        self.assertEqual(result["decyzja"], "Przyjmujemy wariant A.")
        self.assertEqual(result["uzasadnienie"], "Uzasadnienie A.")
        self.assertTrue(result["potwierdzenie"])

    def test_rejects_incomplete_resolution_form(self):
        with self.assertRaisesRegex(ValueError, "Treść decyzji"):
            parse_resolution("<!-- FORMULARZ-ROZSTRZYGNIECIA -->\n**Wynik:** przyjęta")

    def test_generated_card_maps_resolution_fields_to_matching_sections(self):
        event = {"discussion": {"html_url": "https://example/7", "title": "Próba", "created_at": "2026-09-13T10:00:00Z", "body": """### Koordynator dyskusji

@ala

### Problem

Problem źródłowy

### Priorytet

Średni

### Obszar

Punktacja

### Proponowane rozwiązanie

Wariant A

### Inne rozważane podejścia

Wariant B

### Materiały lub przykłady

https://example.com/material

### Powiązane decyzje

DR-002
""", "user": {"login": "ala"}}}
        resolution = """<!-- FORMULARZ-ROZSTRZYGNIECIA -->
**Wynik:** przyjęta
**Treść decyzji:** Treść A.
**Uzasadnienie:** Uzasadnienie A.
**Zmiana regulaminu:** tak
- [x] Potwierdzam zgodność ze stanowiskiem komisji.
**Odrzucone alternatywy:** Wariant B.
"""
        comments = {"data": {"repository": {"discussion": {"comments": {"nodes": [{"body": "Opinia", "createdAt": "2026-09-13T11:00:00Z", "author": {"login": "jan"}}, {"body": resolution, "createdAt": "2026-09-13T12:00:00Z", "author": {"login": "ala"}}]}}}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_path, comments_path, decisions = root / "event.json", root / "comments.json", root / "decyzje"
            decisions.mkdir()
            event_path.write_text(json.dumps(event), encoding="utf-8")
            comments_path.write_text(json.dumps(comments), encoding="utf-8")
            card = create(event_path, decisions, comments_path).read_text(encoding="utf-8")
        self.assertIn("## Odrzucone alternatywy\n\nWariant B.", card)
        self.assertIn("## Problem\n\nProblem źródłowy", card)
        self.assertIn("## Rozważane warianty\n\n**Proponowane rozwiązanie:** Wariant A\n\n**Inne rozważane podejścia:** Wariant B", card)
        self.assertIn("Punktacja", card)
        self.assertIn("https://example.com/material", card)
        self.assertIn("DR-002", card)
        self.assertIn("@ala, @jan", card)

    def test_resolution_template_contains_only_final_decision_fields(self):
        template = (Path(__file__).resolve().parents[1] / "szablony/formularz-rozstrzygniecia.md").read_text(encoding="utf-8")
        for value in ("**Wynik:**", "**Treść decyzji:**", "**Uzasadnienie:**", "**Zmiana regulaminu:**", "**Odrzucone alternatywy:**"):
            self.assertIn(value, template)
        for removed in ("**Sposób potwierdzenia:**", "**Koordynator:**", "**Uczestnicy:**", "**Rozważane warianty:**", "**Termin oceny:**", "**Redaktor regulaminu:**"):
            self.assertNotIn(removed, template)

    def test_keeps_only_open_regulation_proposals_and_sorts_newest_first(self):
        payload = {"data": {"repository": {"discussions": {"nodes": [
            {"number": 2, "title": "Starsza", "url": "https://example/2", "createdAt": "2026-09-10T10:00:00Z", "author": {"login": "ala"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 3}, "labels": {"nodes": [{"name": "do rozstrzygnięcia"}]}},
            {"number": 3, "title": "Inna", "url": "https://example/3", "createdAt": "2026-09-12T10:00:00Z", "author": None, "category": {"slug": "ogolne"}, "comments": {"totalCount": 0}, "labels": {"nodes": []}},
            {"number": 4, "title": "Nowsza", "url": "https://example/4", "createdAt": "2026-09-11T10:00:00Z", "author": {"login": "jan"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 1}, "labels": {"nodes": []}},
        ]}}}}
        result = normalize_discussions(payload, "2026-09-12T12:00:00Z")
        self.assertEqual([item["number"] for item in result["items"]], [4, 2])
        self.assertEqual(result["items"][1]["labels"], ["do rozstrzygnięcia"])
        self.assertEqual(result["generated_at"], "2026-09-12T12:00:00Z")


if __name__ == "__main__":
    unittest.main(verbosity=2)
