from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "_decyzje"

REQUIRED_FIELDS = {
    "id", "tytul", "typ", "status", "data_inicjacji", "data_decyzji", "sezon",
    "dotyczy", "decydenci", "discussion_url", "pr_url", "zastepuje",
    "zastapiona_przez", "termin_oceny",
}
REQUIRED_SECTIONS = (
    "## Problem", "## Kontekst", "## Dyskusja", "## Rozważane warianty", "## Decyzja",
    "## Uzasadnienie", "## Konsekwencje", "## Odrzucone alternatywy", "## Plan oceny",
    "## Ocena po sezonie", "## Historia zmian",
)
ALLOWED_TYPES = {"merytoryczna", "redakcyjna"}
ALLOWED_STATUSES = {"projekt", "w dyskusji", "do zatwierdzenia", "przyjęta", "odrzucona", "wstrzymana", "zastąpiona"}


def read_record(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, flags=re.DOTALL)
    if not match:
        raise AssertionError(f"{path.name}: brak poprawnego bloku metadanych")
    metadata = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise AssertionError(f"{path.name}: niepoprawna linia metadanych: {line}")
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, match.group(2)


class DecisionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = sorted(DECISIONS.glob("DR-*.md"))

    def test_registry_contains_exactly_the_migrated_decisions(self):
        expected = [f"DR-{number:03d}" for number in range(1, 17)]
        actual = [path.name[:6] for path in self.paths]
        self.assertEqual(actual, expected)

    def test_every_record_has_valid_metadata_and_sections(self):
        errors = []
        for path in self.paths:
            try:
                metadata, body = read_record(path)
            except AssertionError as error:
                errors.append(str(error))
                continue
            missing_fields = sorted(REQUIRED_FIELDS - metadata.keys())
            if missing_fields:
                errors.append(f"{path.name}: brak pól {missing_fields}")
            if metadata.get("id") != path.name[:6]:
                errors.append(f"{path.name}: ID nie odpowiada nazwie pliku")
            if metadata.get("typ") not in ALLOWED_TYPES:
                errors.append(f"{path.name}: niedozwolony typ {metadata.get('typ')!r}")
            if metadata.get("status") not in ALLOWED_STATUSES:
                errors.append(f"{path.name}: niedozwolony status {metadata.get('status')!r}")
            for date_field in ("data_inicjacji", "data_decyzji"):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata.get(date_field, "")):
                    errors.append(f"{path.name}: niepoprawne pole {date_field}")
            missing_sections = [section for section in REQUIRED_SECTIONS if section not in body]
            if missing_sections:
                errors.append(f"{path.name}: brak sekcji {missing_sections}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_first_record_preserves_the_approved_reasoning(self):
        self.assertTrue(self.paths, "Brak DR-001")
        _, body = read_record(self.paths[0])
        required_fragments = (
            "definicje powinny znaleźć się wcześniej, ale zdecydowanie nie jako „§ 0”",
            "§ 1. Przedmiot regulaminu",
            "§ 2. Definicje",
            "§ 3. Cel i zasady wyłaniania reprezentacji",
            "Numeracja przepisów powinna być ciągła i rozpoczynać się od § 1",
        )
        missing = [fragment for fragment in required_fragments if fragment not in body]
        self.assertEqual(missing, [], f"DR-001 nie zachowuje przyjętego uzasadnienia: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
