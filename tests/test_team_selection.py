import unittest
from docx import Document
from tests.test_docx_current_contract import CURRENT_DOCUMENT


class TeamSelectionTests(unittest.TestCase):
    def test_world_and_european_team_rules_are_distinct_and_accepted(self):
        texts = [p.text for p in Document(CURRENT_DOCUMENT).paragraphs]
        world = '\n'.join(texts[texts.index('§ 14'):texts.index('§ 15')])
        europe = '\n'.join(texts[texts.index('§ 15'):texts.index('§ 16')])
        self.assertIn('Drużynowe Mistrzostwa Świata', world)
        self.assertIn('ośmiu zawodników', world)
        self.assertIn('w dniu poprzedzającym turniej drużynowy', world)
        self.assertIn('Nie wyznacza się zawodnika rezerwowego', world)
        self.assertIn('Trzej niewybrani zawodnicy nie uczestniczą', world)
        self.assertIn('dwunastu zawodników', europe)
        self.assertIn('pozostałych dziesięciu zawodników', europe)
        self.assertIn('wraz ze wskazaniem zawodnika rezerwowego przedstawia się PZSz do akceptacji', europe)
        self.assertIn('jego miejsce zajmuje nominowany zawodnik rezerwowy', europe)
        for section in (world, europe):
            self.assertIn('dołącza Prezes SPWS', section)
            self.assertIn('wyznacza inną osobę', section)
            self.assertNotIn('BRUDNOPIS', section)
            self.assertNotIn('większością', section)

    def test_removed_conditions_and_mandatory_review(self):
        text = '\n'.join(p.text for p in Document(CURRENT_DOCUMENT).paragraphs)
        self.assertNotIn('powołanie nie pozbawia miejsca', text)
        self.assertNotIn('przyczyny powołania zostaną wskazane', text)
        self.assertNotIn('pod warunkiem spełnienia jednakowych', text)
        self.assertIn('obowiązkowo przeprowadza się ocenę', text)
        self.assertIn('Komisja Regulaminowa SPWS', text)
