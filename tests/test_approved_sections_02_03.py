from __future__ import annotations

import sys
import unittest
from pathlib import Path

from docx import Document


DEFAULT_DOCUMENT = Path(__file__).resolve().parents[1] / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx"
)

APPROVED_PURPOSE = (
    "1. Celem Regulaminu jest wyłonienie możliwie najsilniejszej reprezentacji Polski weteranów "
    "w szermierce. Równe traktowanie zawodników oraz przejrzystość zasad stanowią podstawę "
    "przyjętego procesu wyłaniania reprezentacji."
)

APPROVED_SECTION_2 = [
    "§ 2. Cel regulaminu",
    APPROVED_PURPOSE,
    "2. Proces wyłaniania reprezentacji opiera się na następujących zasadach:",
    "1) szerokiego wyboru zawodów – w rankingu indywidualnym uwzględnia się wyniki uzyskane w "
    "zawodach ujętych w kalendarzach SPWS, PZSz, EVF i FIE, na zasadach określonych w § 5;",
    "2) powołania do startów indywidualnych wyłącznie na podstawie rankingu – do startu "
    "indywidualnego powołuje się czterech najwyżej sklasyfikowanych zawodników w rankingu właściwym "
    "dla danej broni, płci i kategorii wiekowej. Zawodnik z zerowym dorobkiem punktowym nie może "
    "zostać powołany do reprezentacji. Wyjątek stanowi powołanie uzupełniające, o którym mowa "
    "w § 4 ust. 5.",
]

APPROVED_SECTION_3 = [
    "§ 3. Definicje",
    "Ilekroć w Regulaminie jest mowa o:",
    "1. SPWS – należy przez to rozumieć Stowarzyszenie Polskich Weteranów Szermierki;",
    "2. PZSz – należy przez to rozumieć Polski Związek Szermierczy;",
    "3. EVF – należy przez to rozumieć European Veterans Fencing;",
    "4. FIE – należy przez to rozumieć Fédération Internationale d’Escrime (Międzynarodową Federację Szermierczą);",
    "5. rankingu hybrydowym – należy przez to rozumieć ranking indywidualny, w którym wyniki są "
    "aktualizowane z zastosowaniem aktualizacji krokowej albo wygaszania kalendarzowego, zależnie "
    "od organizatora i rodzaju zawodów;",
    "6. aktualizacji krokowej – należy przez to rozumieć sposób aktualizacji wyników zawodów "
    "organizowanych przez SPWS, PZSz lub FIE, zgodnie z którym punkty za zawody z poprzedniego "
    "sezonu pozostają w rankingu do czasu uwzględnienia punktów za odpowiadające im zawody w "
    "sezonie bieżącym, po czym poprzedni wynik przestaje być uwzględniany;",
    "7. wygaszaniu kalendarzowym – należy przez to rozumieć sposób uwzględniania wyników zawodów "
    "organizowanych przez EVF, zgodnie z którym uzyskane punkty pozostają w rankingu przez okres "
    "właściwy dla danego rodzaju zawodów, liczony od dnia zakończenia zawodów, niezależnie od tego, "
    "czy zawody mają odpowiednik w kolejnym sezonie, a po upływie tego okresu przestają być uwzględniane;",
    "8. limitowanych zawodach międzynarodowych – należy przez to rozumieć indywidualne lub drużynowe "
    "zawody międzynarodowe rangi mistrzowskiej, w których liczba zawodników reprezentujących dane "
    "państwo jest ograniczona przepisami organizatora zawodów;",
    "9. powołaniu uzupełniającym – należy przez to rozumieć wyjątkowe powołanie do startu drużynowego "
    "zawodnika nieposiadającego dodatniego dorobku punktowego, dokonywane wyłącznie w celu "
    "uzupełnienia braków uniemożliwiających wystawienie kompletnej i zgodnej z przepisami drużyny.",
]


def section(document: Document, start: str, end: str) -> list[str]:
    paragraphs = document.paragraphs
    start_index = next(i for i, paragraph in enumerate(paragraphs) if paragraph.text == start)
    end_index = next(i for i, paragraph in enumerate(paragraphs) if paragraph.text == end)
    return [paragraph.text for paragraph in paragraphs[start_index:end_index] if paragraph.text]


class ApprovedContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = (
            Path(sys.argv[1])
            if len(sys.argv) == 2 and sys.argv[1].lower().endswith(".docx")
            else DEFAULT_DOCUMENT
        )
        cls.document = Document(path)

    def test_approved_purpose_is_literal_and_unique(self):
        matches = [p for p in self.document.paragraphs if p.text == APPROVED_PURPOSE]
        self.assertEqual(len(matches), 1, "Cel Regulaminu został zmieniony bez aktualizacji testu akceptacyjnego")

    def test_section_2_matches_approved_wording(self):
        self.assertEqual(section(self.document, "§ 2. Cel regulaminu", "§ 3. Definicje"), APPROVED_SECTION_2)

    def test_section_3_defines_all_abbreviations_and_terms(self):
        self.assertEqual(section(self.document, "§ 3. Definicje", "ROZDZIAŁ II"), APPROVED_SECTION_3)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".docx"):
        document_argument = sys.argv.pop(1)
        sys.argv.append(document_argument)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
