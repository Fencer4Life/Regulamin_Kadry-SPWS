from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "_decyzje"

REQUIRED_FIELDS = {
    "id", "tytul", "typ", "status", "data_inicjacji", "data_decyzji", "sezon",
    "dotyczy", "decydenci", "discussion_url", "pr_url", "stan_obowiązywania",
    "zmienia", "zmieniona_przez", "zakres_zmiany", "zastepuje",
    "zastapiona_przez", "termin_oceny",
}
REQUIRED_SECTIONS = (
    "## Problem", "## Kontekst", "## Dyskusja", "## Rozważane warianty", "## Decyzja",
    "## Uzasadnienie", "## Konsekwencje", "## Odrzucone alternatywy", "## Plan oceny",
    "## Ocena po sezonie", "## Historia zmian",
)
ALLOWED_TYPES = {"merytoryczna", "redakcyjna"}
ALLOWED_STATUSES = {"projekt", "w dyskusji", "do zatwierdzenia", "przyjęta", "odrzucona", "wstrzymana"}
ALLOWED_EFFECTS = {"nie dotyczy", "obowiązuje", "częściowo zmieniona", "zastąpiona"}


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


def structured(metadata: dict[str, str], field: str):
    return json.loads(metadata[field])


class DecisionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = sorted(DECISIONS.glob("DR-*.md"))

    def test_registry_preserves_migrated_decisions_and_has_no_number_gaps(self):
        actual = [path.name[:6] for path in self.paths]
        self.assertGreaterEqual(len(actual), 16)
        expected = [f"DR-{number:03d}" for number in range(1, len(actual) + 1)]
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
            if metadata.get("stan_obowiązywania") not in ALLOWED_EFFECTS:
                errors.append(f"{path.name}: niedozwolony stan obowiązywania")
            structured_fields = (
                ("zmienia", list), ("zmieniona_przez", list), ("zakres_zmiany", dict),
                ("zastepuje", list), ("zastapiona_przez", list),
            )
            for field, expected_type in structured_fields:
                try:
                    value = structured(metadata, field)
                    if not isinstance(value, expected_type):
                        errors.append(f"{path.name}: {field} ma zły typ")
                except (KeyError, json.JSONDecodeError):
                    errors.append(f"{path.name}: {field} nie jest poprawnym JSON/YAML inline")
            for date_field in ("data_inicjacji", "data_decyzji"):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata.get(date_field, "")):
                    errors.append(f"{path.name}: niepoprawne pole {date_field}")
            sections = (("## Decyzja", "## Uzasadnienie", "## Dyskusja", "## Wdrożenie")
                        if metadata.get('schema_version') == '2' else REQUIRED_SECTIONS)
            missing_sections = [section for section in sections if section not in body]
            if missing_sections:
                errors.append(f"{path.name}: brak sekcji {missing_sections}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_decision_numbers_and_initiation_dates_are_monotonic(self):
        pairs = []
        for path in self.paths:
            metadata, _ = read_record(path)
            pairs.append((int(metadata["id"][3:]), metadata["data_inicjacji"]))
        self.assertEqual(pairs, sorted(pairs))
        migrated, new = pairs[:16], pairs[16:]
        if new:
            self.assertGreaterEqual(new[0][1], max(date for _, date in migrated))
            self.assertEqual([date for _, date in new], sorted(date for _, date in new))

    def test_relationship_graph_is_consistent(self):
        records = {read_record(path)[0]["id"]: read_record(path)[0] for path in self.paths}
        inverse = {"zmienia": "zmieniona_przez", "zmieniona_przez": "zmienia", "zastepuje": "zastapiona_przez", "zastapiona_przez": "zastepuje"}
        errors = []
        for decision_id, metadata in records.items():
            for field, opposite in inverse.items():
                for target in structured(metadata, field):
                    if target == decision_id:
                        errors.append(f"{decision_id}: samoodwołanie w {field}")
                    elif target not in records:
                        errors.append(f"{decision_id}: brak decyzji {target}")
                    elif decision_id not in structured(records[target], opposite):
                        errors.append(f"{decision_id}: brak relacji odwrotnej {target}.{opposite}")
            effect = metadata["stan_obowiązywania"]
            if effect == "częściowo zmieniona":
                targets = structured(metadata, "zmieniona_przez")
                scopes = structured(metadata, "zakres_zmiany")
                if not targets or set(scopes) != set(targets):
                    errors.append(f"{decision_id}: niepełny zakres zmiany częściowej")
            if effect == "zastąpiona" and not structured(metadata, "zastapiona_przez"):
                errors.append(f"{decision_id}: brak decyzji zastępującej")
            if metadata["status"] != "przyjęta" and effect != "nie dotyczy":
                errors.append(f"{decision_id}: decyzja nieprzyjęta nie może obowiązywać")
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

    def test_ztp_and_source_migration_decisions_are_recorded(self):
        records = {read_record(path)[0]["id"]: read_record(path) for path in self.paths}
        self.assertIn("DR-017", records)
        self.assertIn("DR-018", records)
        ztp_metadata, ztp_body = records["DR-017"]
        migration_metadata, migration_body = records["DR-018"]
        self.assertEqual(ztp_metadata["status"], "przyjęta")
        self.assertEqual(migration_metadata["status"], "przyjęta")
        self.assertIn("DR-001", structured(ztp_metadata, "zmienia"))
        self.assertIn("cyframi arabskimi", ztp_body)
        self.assertIn("ciemnoszary", migration_body)
        self.assertIn("poza repozytorium", migration_body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
