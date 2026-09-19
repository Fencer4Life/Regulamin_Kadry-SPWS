from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from narzedzia.normalize_regulamin_markdown import normalize_source, resolve_references
from narzedzia.prepare_regulamin import normalize_and_build, verify
from narzedzia.docx_model import parse_regulation_source
from tests.test_ztp_model import METADATA


BODY = '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:zasady] Zasady
8. [unit:pierwszy] Pierwszy ustęp:
   9) [unit:punkt-a] pierwszy punkt;
   4) [unit:punkt-b] drugi punkt.
2. [unit:drugi] Drugi ustęp odsyła do {{ref:zasady/punkt-a}}.
'''


class RegulationNormalizationTests(unittest.TestCase):
    def source(self, text: str = BODY) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "source.md"
        path.write_text(METADATA + text, encoding="utf-8")
        return path

    def test_replaces_input_numbers_with_canonical_sequence(self):
        normalized = normalize_source(self.source())
        self.assertIn("1. [unit:pierwszy]", normalized)
        self.assertIn("   1) [unit:punkt-a]", normalized)
        self.assertIn("   2) [unit:punkt-b]", normalized)
        self.assertIn("2. [unit:drugi]", normalized)

    def test_normalizes_technical_enumeration_punctuation(self):
        normalized = normalize_source(
            self.source(
                '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:zasady] Zasady
1. [unit:wprowadzenie] Wyliczenie.
   1) [unit:pierwszy] pierwszy punkt.
   2) [unit:drugi] drugi punkt;
'''
            )
        )
        self.assertIn("[unit:wprowadzenie] Wyliczenie:", normalized)
        self.assertIn("[unit:pierwszy] pierwszy punkt;", normalized)
        self.assertIn("[unit:drugi] drugi punkt.", normalized)

    def test_normalization_is_idempotent(self):
        first = normalize_source(self.source())
        second = normalize_source(self.source(first[len(METADATA):]))
        self.assertEqual(first, second)

    def test_resolves_stable_reference_to_current_visible_number(self):
        path = self.source()
        model = parse_regulation_source(path)
        self.assertEqual(
            resolve_references(model, "Zgodnie z {{ref:zasady/punkt-a}}."),
            "Zgodnie z § 1 ust. 1 pkt 1.",
        )

    def test_does_not_change_words(self):
        normalized = normalize_source(self.source())
        for phrase in (
            "Pierwszy ustęp:",
            "pierwszy punkt;",
            "drugi punkt.",
            "Drugi ustęp odsyła do {{ref:zasady/punkt-a}}.",
        ):
            self.assertIn(phrase, normalized)

    def test_verify_rebuilds_without_modifying_tracked_files(self):
        source = self.source()
        target = source.with_suffix(".docx")
        normalize_and_build(source, target)
        before = (source.read_bytes(), target.read_bytes())
        verify(source, target)
        self.assertEqual((source.read_bytes(), target.read_bytes()), before)

    def test_verify_rejects_noncanonical_markdown_without_writing(self):
        source = self.source()
        target = source.with_suffix(".docx")
        normalize_and_build(source, target)
        source.write_text(source.read_text(encoding="utf-8").replace("1. [unit:pierwszy]", "8. [unit:pierwszy]"), encoding="utf-8")
        before = (source.read_bytes(), target.read_bytes())
        with self.assertRaisesRegex(ValueError, "wymaga normalizacji"):
            verify(source, target)
        self.assertEqual((source.read_bytes(), target.read_bytes()), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
