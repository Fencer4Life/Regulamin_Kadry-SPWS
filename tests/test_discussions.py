from __future__ import annotations

import unittest
import json
import tempfile
from pathlib import Path

from narzedzia.create_decision_from_discussion import create, next_decision_id
from narzedzia.sync_discussions import normalize_discussions


class DiscussionSnapshotTests(unittest.TestCase):
    def test_next_decision_id_uses_highest_existing_number(self):
        self.assertEqual(next_decision_id(["DR-002-a.md", "DR-016-b.md"]), "DR-017")

    def test_generated_card_uses_discussion_form_and_leaves_only_human_fields_empty(self):
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
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_path, decisions = root / "event.json", root / "decyzje"
            decisions.mkdir()
            event_path.write_text(json.dumps(event), encoding="utf-8")
            card = create(event_path, decisions).read_text(encoding="utf-8")
        self.assertIn("## Odrzucone alternatywy\n\nWariant B", card)
        self.assertIn("## Problem\n\nProblem źródłowy", card)
        self.assertIn("## Decyzja\n\nWariant A", card)
        self.assertIn("status: przyjęta", card)
        self.assertIn("## Uzasadnienie\n\n> _Do uzupełnienia przez osobę przygotowującą decyzję._", card)
        self.assertIn("- [ ] **Tak**", card)
        self.assertIn("- [ ] **Nie**", card)
        self.assertIn("Punktacja", card)
        self.assertIn("https://example.com/material", card)
        self.assertIn("DR-002", card)
        self.assertIn("**Koordynator dyskusji:** @ala", card)

    def test_splits_all_paginated_regulation_proposals_and_sorts_each_state(self):
        payload = [
            {"data": {"repository": {"discussions": {"nodes": [
                {"number": 2, "title": "Starsza otwarta", "url": "https://example/2", "createdAt": "2026-09-10T10:00:00Z", "closedAt": None, "author": {"login": "ala"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 3}, "labels": {"nodes": [{"name": "do rozstrzygnięcia"}]}},
                {"number": 3, "title": "Inna kategoria", "url": "https://example/3", "createdAt": "2026-09-12T10:00:00Z", "closedAt": None, "author": None, "category": {"slug": "ogolne"}, "comments": {"totalCount": 0}, "labels": {"nodes": []}},
                {"number": 4, "title": "Starsza zamknięta", "url": "https://example/4", "createdAt": "2026-09-09T10:00:00Z", "closedAt": "2026-09-12T08:00:00Z", "author": {"login": "jan"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 1}, "labels": {"nodes": [{"name": "PORZUCONA"}]}},
            ]}}}},
            {"data": {"repository": {"discussions": {"nodes": [
                {"number": 5, "title": "Nowsza zamknięta", "url": "https://example/5", "createdAt": "2026-09-11T10:00:00Z", "closedAt": "2026-09-13T08:00:00Z", "author": {"login": "ola"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 4}, "labels": {"nodes": [{"name": "rozstrzygnięta"}]}},
                {"number": 6, "title": "Nowsza otwarta", "url": "https://example/6", "createdAt": "2026-09-14T10:00:00Z", "closedAt": None, "author": None, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 2}, "labels": {"nodes": []}},
            ]}}}},
        ]
        result = normalize_discussions(payload, "2026-09-12T12:00:00Z")
        self.assertEqual([item["number"] for item in result["open_items"]], [6, 2])
        self.assertEqual([item["number"] for item in result["closed_items"]], [5, 4])
        self.assertEqual(result["open_items"][1]["labels"], ["do rozstrzygnięcia"])
        self.assertEqual(result["open_items"][0]["author"], "konto usunięte")
        self.assertEqual(result["closed_items"][0]["closed_at"], "2026-09-13T08:00:00Z")
        self.assertEqual(result["closed_items"][0]["labels"], ["rozstrzygnięta"])
        self.assertEqual(result["generated_at"], "2026-09-12T12:00:00Z")


if __name__ == "__main__":
    unittest.main(verbosity=2)
