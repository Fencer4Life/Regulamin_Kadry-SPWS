from __future__ import annotations

import unittest
from pathlib import Path

from docx import Document


DOCUMENT = Path(__file__).resolve().parents[1] / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx"
)

EXPECTED_SELECTION_RULES = [
    "3. Łączna liczba punktów zawodnika w rankingu indywidualnym jest sumą punktów "
    "przypisanych do ośmiu pozycji wynikowych:",
    "1) trzech obowiązkowych pozycji krajowych;",
    "2) pięciu pozycji otwartych.",
    "4. Trzy obowiązkowe pozycje krajowe wypełnia się wynikami uzyskanymi w zawodach "
    "Pucharu Polski Weteranów w Szermierce oraz Mistrzostwach Polski Weteranów w Szermierce, "
    "według następujących zasad:",
    "1) spośród wszystkich wyników uzyskanych przez zawodnika w tych zawodach wybiera się "
    "trzy wyniki, za które zawodnik otrzymał najwyższą liczbę punktów rankingowych;",
    "2) wyniki z Pucharu Polski Weteranów w Szermierce oraz Mistrzostw Polski Weteranów "
    "w Szermierce porównuje się łącznie, wyłącznie na podstawie liczby uzyskanych punktów "
    "rankingowych;",
    "3) uwzględnienie wyniku z Mistrzostw Polski Weteranów w Szermierce nie jest obowiązkowe;",
    "4) jeżeli zawodnik uzyskał mniej niż trzy wyniki w Pucharze Polski Weteranów w Szermierce "
    "lub Mistrzostwach Polski Weteranów w Szermierce, za każdą niewypełnioną obowiązkową "
    "pozycję krajową przyjmuje się zero punktów rankingowych.",
    "5. Pięć pozycji otwartych wypełnia się pięcioma najwyżej punktowanymi wynikami zawodnika, "
    "które nie zostały uwzględnione jako obowiązkowe pozycje krajowe. Przy wyborze wyników do "
    "pozycji otwartych uwzględnia się:",
    "1) pozostałe wyniki uzyskane w Pucharze Polski Weteranów w Szermierce oraz Mistrzostwach "
    "Polski Weteranów w Szermierce;",
    "2) wyniki uzyskane w Pucharach Polski Seniorów w Szermierce oraz Mistrzostwach Polski "
    "Seniorów w Szermierce;",
    "3) wyniki uzyskane w Pucharach Europy Weteranów w Szermierce oraz Mistrzostwach Europy "
    "Weteranów w Szermierce;",
    "4) wyniki uzyskane w Pucharach Świata Weteranów w Szermierce, jeżeli zawody tego cyklu "
    "zostaną rozegrane, oraz Mistrzostwach Świata Weteranów w Szermierce.",
    "6. Jeżeli po wybraniu trzech obowiązkowych pozycji krajowych zawodnik ma mniej niż pięć "
    "pozostałych wyników podlegających uwzględnieniu w pozycjach otwartych, za każdą "
    "niewypełnioną pozycję otwartą przyjmuje się zero punktów rankingowych.",
    "7. Najpierw wybiera się wyniki wypełniające trzy obowiązkowe pozycje krajowe, a następnie "
    "wyniki wypełniające pięć pozycji otwartych.",
    "8. Żaden wynik nie może zostać policzony dwukrotnie.",
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
