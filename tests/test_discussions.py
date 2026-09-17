from __future__ import annotations

import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from narzedzia.create_decision_from_discussion import create, next_decision_id, parse_discussion_form
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
                {"number": 2, "title": "Starsza otwarta", "url": "https://example/2", "createdAt": "2026-09-10T10:00:00Z", "closedAt": None, "body": "### Koordynator dyskusji\n\n@ala\n\n### Zależy od\n\nDR-015", "author": {"login": "ala"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 3}, "labels": {"nodes": [{"name": "do rozstrzygnięcia"}]}},
                {"number": 3, "title": "Inna kategoria", "url": "https://example/3", "createdAt": "2026-09-12T10:00:00Z", "closedAt": None, "author": None, "category": {"slug": "ogolne"}, "comments": {"totalCount": 0}, "labels": {"nodes": []}},
                {"number": 4, "title": "Starsza zamknięta", "url": "https://example/4", "createdAt": "2026-09-09T10:00:00Z", "closedAt": "2026-09-12T08:00:00Z", "author": {"login": "jan"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 1}, "labels": {"nodes": [{"name": "PORZUCONA"}]}},
            ]}}}},
            {"data": {"repository": {"discussions": {"nodes": [
                {"number": 5, "title": "Nowsza zamknięta", "url": "https://example/5", "createdAt": "2026-09-11T10:00:00Z", "closedAt": "2026-09-13T08:00:00Z", "author": {"login": "ola"}, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 4}, "labels": {"nodes": [{"name": "rozstrzygnięta"}]}},
                {"number": 6, "title": "Nowsza otwarta", "url": "https://example/6", "createdAt": "2026-09-14T10:00:00Z", "closedAt": None, "body": "### Koordynator dyskusji\n\n_No response_", "author": None, "category": {"slug": "propozycje-zmian-regulaminu"}, "comments": {"totalCount": 2}, "labels": {"nodes": []}},
            ]}}}},
        ]
        result = normalize_discussions(payload, "2026-09-12T12:00:00Z")
        self.assertEqual([item["number"] for item in result["open_items"]], [2, 6])
        self.assertEqual([item["number"] for item in result["closed_items"]], [5, 4])
        self.assertEqual(result["open_items"][0]["labels"], ["do rozstrzygnięcia"])
        self.assertEqual(result["open_items"][0]["coordinator"], "ala")
        self.assertEqual(result["open_items"][0]["coordinator_avatar_url"], "https://github.com/ala.png?size=80")
        self.assertEqual(result["open_items"][0]["depends_on"], "DR-015")
        self.assertIsNone(result["open_items"][1]["coordinator"])
        self.assertIsNone(result["open_items"][1]["coordinator_avatar_url"])
        self.assertEqual(result["open_items"][1]["author"], "konto usunięte")
        self.assertEqual(result["closed_items"][0]["closed_at"], "2026-09-13T08:00:00Z")
        self.assertEqual(result["closed_items"][0]["labels"], ["rozstrzygnięta"])
        self.assertEqual(result["generated_at"], "2026-09-12T12:00:00Z")

    def test_parser_reads_new_dependency_heading_and_old_heading(self):
        current = parse_discussion_form("### Zależy od\n\n#29, DR-015")
        legacy = parse_discussion_form("### Powiązane decyzje\n\nDR-014")
        self.assertEqual(current["zalezy_od"], "#29, DR-015")
        self.assertEqual(legacy["zalezy_od"], "DR-014")

    def test_keeps_coordinator_name_when_it_has_no_github_avatar(self):
        payload = {"data": {"repository": {"discussions": {"nodes": [{
            "number": 7, "title": "Próba", "url": "https://example/7",
            "createdAt": "2026-09-10T10:00:00Z", "closedAt": None,
            "body": "### Koordynator dyskusji\n\nKomisja 2026",
            "author": {"login": "ala"}, "category": {"slug": "propozycje-zmian-regulaminu"},
            "comments": {"totalCount": 0}, "labels": {"nodes": []},
        }]}}}}
        item = normalize_discussions(payload, "2026-09-12T12:00:00Z")["open_items"][0]
        self.assertEqual(item["coordinator"], "Komisja 2026")
        self.assertIsNone(item["coordinator_avatar_url"])

    def test_sync_script_runs_the_same_way_as_release(self):
        payload = {"data": {"repository": {"discussions": {"nodes": []}}}}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            destination = Path(directory) / "snapshot.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "narzedzia/sync_discussions.py", str(source), str(destination)],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(destination.is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
