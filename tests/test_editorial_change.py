from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from narzedzia.apply_editorial_change import apply_editorial_change


def event(body: str) -> dict[str, object]:
    return {
        "discussion": {
            "html_url": "https://example.com/discussions/31",
            "title": "Korekta oczywistej literówki",
            "created_at": "2026-09-16T10:00:00Z",
            "body": body,
            "user": {"login": "koordynator"},
        }
    }


FORM = """### Koordynator dyskusji

@koordynator

### Problem

W tekście jest oczywista literówka.

### Obszar

Redakcja regulaminu

### Proponowane rozwiązanie

Poprawić literówkę bez zmiany sensu.

### Fragment Markdown do zastąpienia

stare brzmienie

### Nowe brzmienie Markdown

nowe brzmienie
"""


class EditorialChangeTests(unittest.TestCase):
    def test_applies_one_exact_replacement_and_creates_complete_editorial_card(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "regulamin.md"
            source.write_text("Początek\n\nstare brzmienie\n\nKoniec\n", encoding="utf-8")
            decisions = root / "decyzje"
            decisions.mkdir()
            event_path = root / "event.json"
            event_path.write_text(json.dumps(event(FORM)), encoding="utf-8")

            card_path, changed_source = apply_editorial_change(
                event_path, decisions, source
            )

            self.assertEqual(changed_source, source)
            self.assertEqual(
                source.read_text(encoding="utf-8"),
                "Początek\n\nnowe brzmienie\n\nKoniec\n",
            )
            card = card_path.read_text(encoding="utf-8")
            self.assertIn("typ: redakcyjna", card)
            self.assertIn("status: przyjęta", card)
            self.assertIn("- [x] **Tak**", card)
            self.assertIn("- [ ] **Nie**", card)
            self.assertIn("Korekta redakcyjna bez zmiany sensu", card)
            self.assertNotIn("Do uzupełnienia", card)
            self.assertIn("## Stary fragment Markdown", card)
            self.assertIn("## Nowy fragment Markdown", card)
            from narzedzia.decision_patch import read_fragments
            self.assertEqual(read_fragments(card), ("stare brzmienie", "nowe brzmienie"))

    def test_rejects_non_unique_fragment_without_changing_source_or_creating_card(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "regulamin.md"
            original = "stare brzmienie\n\nstare brzmienie\n"
            source.write_text(original, encoding="utf-8")
            decisions = root / "decyzje"
            decisions.mkdir()
            event_path = root / "event.json"
            event_path.write_text(json.dumps(event(FORM)), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "dokładnie raz"):
                apply_editorial_change(event_path, decisions, source)

            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual(list(decisions.iterdir()), [])

    def test_rejects_missing_fields_without_changing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "regulamin.md"
            original = "Treść regulaminu\n"
            source.write_text(original, encoding="utf-8")
            decisions = root / "decyzje"
            decisions.mkdir()
            event_path = root / "event.json"
            event_path.write_text(
                json.dumps(event("### Problem\n\nBrak danych zmiany\n")),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Fragment Markdown"):
                apply_editorial_change(event_path, decisions, source)

            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual(list(decisions.iterdir()), [])

    def test_fast_card_is_complete_when_optional_proposal_is_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "regulamin.md"
            source.write_text("stare brzmienie\n", encoding="utf-8")
            decisions = root / "decyzje"
            decisions.mkdir()
            event_path = root / "event.json"
            event_path.write_text(
                json.dumps(
                    event(FORM.replace("Poprawić literówkę bez zmiany sensu.", "_No response_"))
                ),
                encoding="utf-8",
            )

            card_path, _ = apply_editorial_change(event_path, decisions, source)

            card = card_path.read_text(encoding="utf-8")
            self.assertNotIn("Do uzupełnienia przez osobę przygotowującą", card)
            self.assertIn(
                "Zastąpić wskazany fragment Markdown dokładnie podanym nowym brzmieniem.",
                card,
            )
            self.assertIn("Korekta redakcyjna bez zmiany sensu", card)


if __name__ == "__main__":
    unittest.main(verbosity=2)
