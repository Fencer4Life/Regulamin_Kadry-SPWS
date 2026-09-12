from __future__ import annotations

import unittest

from narzedzia.create_decision_from_discussion import next_decision_id
from narzedzia.sync_discussions import normalize_discussions


class DiscussionSnapshotTests(unittest.TestCase):
    def test_next_decision_id_uses_highest_existing_number(self):
        self.assertEqual(next_decision_id(["DR-002-a.md", "DR-016-b.md"]), "DR-017")
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
