from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "regulamin"
    / ("Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md")
)


class RepresentationRankingAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")

    def test_uses_official_ranking_name(self):
        self.assertIn(
            "Ranking wyłaniania Reprezentacji Polski Weteranów",
            self.text,
        )
        self.assertIn("osobno dla każdej broni, płci i kategorii wiekowej", self.text)

    def test_domestic_positions_are_two_ppw_plus_required_mpw(self):
        for fragment in (
            "dwa najlepsze wyniki punktowe zawodnika uzyskane w PPW",
            "wynik punktowy uzyskany w MPW",
            "za każdą niewypełnioną pozycję PPW przyjmuje się 0 punktów",
            "za obowiązkową pozycję MPW przyjmuje się 0 punktów",
        ):
            self.assertIn(fragment, self.text)
        self.assertNotIn("brak startu w MPW nie powoduje usunięcia", self.text)

    def test_v0_is_domestic_only_and_cannot_be_used_for_selection(self):
        for fragment in (
            "V0 – od 30 do 39 lat",
            "wyłącznie punkty z PPW, MPW, PPS i MPS",
            "nie uwzględnia się punktów z zawodów EVF ani FIE",
            "nie stanowią podstawy powołania do reprezentacji",
        ):
            self.assertIn(fragment, self.text)

    def test_ppw_classification_is_a_filtered_subset(self):
        for fragment in (
            "Klasyfikacja Pucharu Polski Weteranów",
            "filtrowanym podzbiorem Rankingu",
            "filtra obejmującego PPW i MPW",
        ):
            self.assertIn(fragment, self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
