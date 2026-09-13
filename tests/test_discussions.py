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
**Sposób potwierdzenia:** w dyskusji GitHub
**Koordynator:** @ala
**Zmiana regulaminu:** tak
- [x] Potwierdzam zgodność ze stanowiskiem komisji.
"""
        result = parse_resolution(comment)
        self.assertEqual(result["wynik"], "przyjęta")
        self.assertEqual(result["decyzja"], "Przyjmujemy wariant A.")
        self.assertTrue(result["potwierdzenie"])

    def test_rejects_incomplete_resolution_form(self):
        with self.assertRaisesRegex(ValueError, "Treść decyzji"):
            parse_resolution("<!-- FORMULARZ-ROZSTRZYGNIECIA -->\n**Wynik:** przyjęta")

    def test_generated_card_maps_resolution_fields_to_matching_sections(self):
        event = {"discussion": {"html_url": "https://example/7", "title": "Próba", "created_at": "2026-09-13T10:00:00Z", "body": "Problem źródłowy", "user": {"login": "ala"}}}
        resolution = """<!-- FORMULARZ-ROZSTRZYGNIECIA -->
**Wynik:** przyjęta
**Treść decyzji:** Treść A.
**Sposób potwierdzenia:** głosowanie
**Koordynator:** @ala
**Zmiana regulaminu:** tak
- [x] Potwierdzam zgodność ze stanowiskiem komisji.
### Informacje opcjonalne
**Uzasadnienie:** Uzasadnienie A.
**Rozważane warianty:** Wariant A i B.
**Odrzucone alternatywy:** Wariant B.
**Termin oceny:** po sezonie
"""
        comments = {"data": {"repository": {"discussion": {"comments": {"nodes": [{"body": resolution, "createdAt": "2026-09-13T12:00:00Z"}]}}}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_path, comments_path, decisions = root / "event.json", root / "comments.json", root / "decyzje"
            decisions.mkdir()
            event_path.write_text(json.dumps(event), encoding="utf-8")
            comments_path.write_text(json.dumps(comments), encoding="utf-8")
            card = create(event_path, decisions, comments_path).read_text(encoding="utf-8")
        self.assertIn("## Odrzucone alternatywy\n\nWariant B.", card)
        self.assertIn("## Plan oceny\n\npo sezonie", card)

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
