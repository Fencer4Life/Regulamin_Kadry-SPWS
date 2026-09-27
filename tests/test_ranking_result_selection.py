from __future__ import annotations

import unittest
from pathlib import Path

from docx import Document

DOCUMENT = (
    Path(__file__).resolve().parents[1]
    / "regulamin"
    / ("Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx")
)

EXPECTED_SELECTION_RULES = [
    "3. Łączna liczba punktów zawodnika w Rankingu jest sumą punktów "
    "przypisanych do ośmiu pozycji wynikowych:",
    "1) trzech obowiązkowych pozycji krajowych;",
    "2) pięciu pozycji otwartych.",
    "4. Trzy obowiązkowe pozycje krajowe wypełnia się wynikami uzyskanymi w zawodach "
    "Pucharu Polski Weteranów w Szermierce oraz Mistrzostwach Polski Weteranów w Szermierce, "
    "według następujących zasad:",
    "1) dwie pozycje wypełniają dwa najlepsze wyniki punktowe zawodnika uzyskane w PPW;",
    "2) trzecią pozycję wypełnia wynik punktowy uzyskany w MPW;",
    "3) jeżeli zawodnik uzyskał mniej niż dwa wyniki w PPW, za każdą niewypełnioną pozycję "
    "PPW przyjmuje się 0 punktów;",
    "4) jeżeli zawodnik nie wystartował w MPW, za obowiązkową pozycję MPW przyjmuje się 0 punktów.",
    "5. Na pięć pozycji otwartych składa się pięć najwyżej punktowanych spośród pozostałych "
    "wyników zawodnika uwzględnianych w Rankingu.",
    "6. Najpierw wybiera się wyniki wypełniające trzy obowiązkowe pozycje krajowe, a następnie "
    "wyniki wypełniające pięć pozycji otwartych.",
    "7. Żaden wynik nie może zostać policzony dwukrotnie.",
    "8. W kategorii V0 w Rankingu uwzględnia się wyłącznie punkty z PPW, MPW, PPS i MPS; "
    "nie uwzględnia się punktów z zawodów EVF ani FIE. Kategorie V1–V4 prowadzi się na "
    "zasadach określonych w ust. 1–7.",
]


class RankingResultSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paragraphs = [paragraph.text for paragraph in Document(DOCUMENT).paragraphs]
        start = cls.paragraphs.index("§ 5")
        end = cls.paragraphs.index("§ 6")
        cls.section = [text for text in cls.paragraphs[start:end] if text]

    def test_section_contains_the_complete_eight_result_selection_rule(self):
        self.assertEqual(self.section[-len(EXPECTED_SELECTION_RULES) :], EXPECTED_SELECTION_RULES)

    def test_redundant_published_data_requirement_is_removed(self):
        self.assertNotIn(
            "8) opublikowane wyniki zawierają dane niezbędne do ich zweryfikowania oraz obliczenia "
            "punktów rankingowych.",
            self.section,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
