import unittest
from docx import Document
from tests.test_docx_current_contract import CURRENT_DOCUMENT


class TeamSelectionTests(unittest.TestCase):
    def test_european_team_has_closed_pool_and_shared_selector_role(self):
        texts = [p.text for p in Document(CURRENT_DOCUMENT).paragraphs]
        pool = '\n'.join(texts[texts.index('§ 12'):texts.index('§ 13')])
        team = '\n'.join(texts[texts.index('§ 14'):texts.index('§ 15')])
        self.assertIn('ośmiu zawodników nominowanych do startu indywidualnego', pool)
        self.assertIn('mają zapewnione miejsca w składzie drużyny — po jednym zawodniku z każdej kategorii', team)
        self.assertIn('Funkcję selekcjonera drużyny pełni zespół', team)
        self.assertIn('trzech kolejnych zawodników do składu drużyny oraz szóstego zawodnika jako rezerwowego', team)
        self.assertIn('wyłącznie spośród pozostałych sześciu zawodników', team)
        self.assertIn('dołącza Prezes SPWS', team)
        self.assertIn('Jeżeli Prezes SPWS nie może uczestniczyć w pracach zespołu, wyznacza inną osobę do udziału w tych pracach w swoim imieniu.', team)
        self.assertNotIn('Zarząd SPWS', team)
        self.assertNotIn('BRUDNOPIS', team)
        self.assertNotIn('większością', team)
        supplement = '\n'.join(texts[texts.index('§ 16'):texts.index('§ 17')])
        self.assertIn('nie stosuje się do Drużynowych Mistrzostw Europy', supplement)
