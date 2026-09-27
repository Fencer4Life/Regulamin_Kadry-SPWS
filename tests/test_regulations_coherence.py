from __future__ import annotations

import unittest

from narzedzia.regulation_coherence import coherence_issues, load_regulation_texts


class RegulationsCoherenceTests(unittest.TestCase):
    def setUp(self):
        self.texts = load_regulation_texts()

    def test_both_current_regulations_satisfy_shared_invariants(self):
        self.assertEqual(coherence_issues(self.texts), [])

    def test_every_shared_rule_is_checked_in_both_regulations(self):
        changed = dict(self.texts)
        changed["zawody"] = changed["zawody"].replace(
            "dwa najlepsze wyniki punktowe zawodnika uzyskane w PPW",
            "trzy dowolne wyniki krajowe",
            1,
        )
        self.assertTrue(
            any(
                issue.startswith("zawody: brak wspólnego inwariantu")
                for issue in coherence_issues(changed)
            )
        )

    def test_combined_classification_cannot_leak_into_selection_regulation(self):
        changed = dict(self.texts)
        changed["reprezentacja"] += "\nKlasyfikacja łączona\n"
        self.assertIn(
            "reprezentacja: Klasyfikacja łączona nie może określać powołań",
            coherence_issues(changed),
        )

    def test_second_group_round_cannot_use_the_ranking_seeding(self):
        changed = dict(self.texts)
        changed["zawody"] = changed["zawody"].replace(
            "Rozstawienie do drugiej rundy grupowej ustala się wyłącznie na podstawie wyników "
            "pierwszej rundy grupowej",
            "Rozstawienie do drugiej rundy grupowej ustala się ponownie na podstawie Rankingu",
            1,
        )
        self.assertTrue(
            any(
                "brak ograniczenia Klasyfikacji łączonej" in issue
                for issue in coherence_issues(changed)
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
