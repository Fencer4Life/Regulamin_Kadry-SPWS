from __future__ import annotations

import re
import unittest
from pathlib import Path

from narzedzia.docx_model import parse_regulation_source

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "regulamin-wspolzawodnictwa"
    / ("Regulamin-wspolzawodnictwa-sportowego-w-kategorii-Weteran_2026-2027.md")
)


class CompetitionRegulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        cls.model = parse_regulation_source(SOURCE)

    def test_has_complete_ztp_structure_and_continuous_sections(self):
        expected_chapters = (
            "Postanowienia ogólne",
            "Kalendarz i organizacja zawodów",
            "Uczestnicy i osoby funkcyjne",
            "PPW i indywidualne MPW",
            "Drużynowe MPW",
            "Ranking i klasyfikacje",
            "Wyniki, protokoły i dane",
            "Postanowienia końcowe",
        )
        self.assertEqual(tuple(chapter.title for chapter in self.model.chapters), expected_chapters)
        numbers = [int(value) for value in re.findall(r"^### § (\d+) —", self.text, re.MULTILINE)]
        self.assertEqual(numbers, list(range(1, 26)))
        identifiers = re.findall(r"<!-- (?:chapter|section|unit):([^ ]+) -->", self.text)
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_scope_is_domestic_and_preserves_core_operational_rules(self):
        for fragment in (
            "Pucharu Polski Weteranów",
            "indywidualnych Mistrzostw Polski Weteranów",
            "Drużynowych Mistrzostw Polski Weteranów",
            "komunikat organizacyjny",
            "opiekę medyczną",
            "Komisja Techniczna",
            "sędziów",
            "dwie rundy grupowe",
            "protokół zawodów",
            "kompletne protokoły wszystkich rozegranych walk",
        ):
            self.assertIn(fragment, self.text)
        self.assertIn(
            "nie określa zasad kwalifikowania ani powoływania zawodników do reprezentacji",
            self.text,
        )

    def test_combined_classification_is_limited_to_first_group_round(self):
        section = self.text.split("### § 14 — Klasyfikacja łączona", 1)[1].split("### § 15 —", 1)[0]
        for fragment in (
            "wyłącznie do rozstawienia zawodników w pierwszej rundzie grupowej",
            "w chwili wygenerowania pliku XML",
            "rzeczywiste miejsce w Rankingu",
            "MV0, MV1, MV2, MV3, MV4, KV0, KV1, KV2, KV3, KV4",
            "najpierw mężczyzn, a następnie kobiety",
            "od najmłodszych do najstarszych",
            "wyników pierwszej rundy grupowej",
        ):
            self.assertIn(fragment, section)
        self.assertIn("nie stanowią podstawy powołania", section)

    def test_domestic_ranking_rule_and_v0_are_explicit(self):
        for fragment in (
            "dwa najlepsze wyniki punktowe zawodnika uzyskane w PPW",
            "obowiązkową pozycję MPW przyjmuje się 0 punktów",
            "filtrowanym podzbiorem Rankingu",
            "V0 obejmuje zawodników w wieku od 30 do 39 lat",
            "PPW, MPW, PPS i MPS",
            "nie uwzględnia się punktów z zawodów EVF ani FIE",
            "nie stanowią podstawy powołania do reprezentacji",
        ):
            self.assertIn(fragment, self.text)
        self.assertNotIn("brak startu w MPW nie powoduje usunięcia", self.text)

    def test_online_results_are_fetched_and_only_corrections_are_sent(self):
        self.assertIn(
            "najpóźniej do 7 dni po zawodach publikuje je w serwisie internetowym używanym do obsługi zawodów",
            self.text,
        )
        self.assertIn("W przypadku pomyłki w protokole internetowym", self.text)
        self.assertIn("organizator przekazuje skorygowany plik do SPWS", self.text)
        self.assertNotIn("przekazuje SPWS pliki wynikowe", self.text)
        self.assertNotIn("przekazuje je SPWS", self.text)
        self.assertNotIn("w ciągu 3 dni roboczych", self.text)

    def test_safety_rules_do_not_hide_responsibility(self):
        safety = self.text.split("### § 25 — Zasady bezpieczeństwa i wejście w życie", 1)[1]
        for fragment in (
            "Organizator odpowiada za przygotowanie bezpiecznego miejsca zawodów",
            "Zawodnik odpowiada za stan i zgodność używanego sprzętu",
            "nie wyłącza odpowiedzialności wynikającej z przepisów prawa",
            "rejestruje wypadek",
        ):
            self.assertIn(fragment, safety)


if __name__ == "__main__":
    unittest.main(verbosity=2)
