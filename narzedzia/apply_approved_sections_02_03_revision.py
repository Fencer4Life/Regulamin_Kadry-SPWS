from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Cm


TARGET = Path(__file__).resolve().parents[1] / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx"
)


def find_unique(document: Document, text: str):
    matches = [paragraph for paragraph in document.paragraphs if paragraph.text == text]
    if len(matches) != 1:
        raise RuntimeError(f"Oczekiwano jednego akapitu, znaleziono {len(matches)}: {text!r}")
    return matches[0]


def replace_plain(paragraph, text: str):
    paragraph.clear()
    paragraph.add_run(text)


def replace_with_term(paragraph, number: str, term: str, definition: str):
    paragraph.clear()
    paragraph.add_run(number)
    paragraph.add_run(term).bold = True
    paragraph.add_run(definition)


def insert_after(paragraph, style=None):
    new_paragraph = paragraph._parent.add_paragraph(style=style or paragraph.style)
    paragraph._p.addnext(new_paragraph._p)
    return new_paragraph


def add_labeled_text(paragraph, prefix: str, label: str, rest: str):
    paragraph.add_run(prefix)
    paragraph.add_run(label).bold = True
    paragraph.add_run(rest)


document = Document(TARGET)

old_purpose = find_unique(
    document,
    "1. Celem zasad określonych w Regulaminie jest wyłonienie możliwie najsilniejszej "
    "reprezentacji Polski weteranów w szermierce, z zachowaniem przejrzystości procesu, "
    "równego traktowania zawodników oraz możliwości zweryfikowania podstaw podjętych decyzji.",
)
replace_plain(
    old_purpose,
    "1. Celem Regulaminu jest wyłonienie możliwie najsilniejszej reprezentacji Polski "
    "weteranów w szermierce. Równe traktowanie zawodników oraz przejrzystość zasad "
    "stanowią podstawę przyjętego procesu wyłaniania reprezentacji.",
)

old_principle = find_unique(
    document,
    "2. Regulamin zapewnia zawodnikom swobodę wyboru zawodów uwzględnianych w rankingu "
    "i nie wprowadza obowiązku udziału w zawodach krajowych, jednocześnie wykluczając, "
    "z wyjątkiem powołania uzupełniającego, możliwość powołania do reprezentacji zawodnika "
    "bez zweryfikowanego dorobku punktowego w rankingu indywidualnym.",
)
replace_plain(
    old_principle,
    "2. Proces wyłaniania reprezentacji opiera się na następujących zasadach:",
)

principle_1 = insert_after(old_principle)
add_labeled_text(
    principle_1,
    "1) ",
    "szerokiego wyboru zawodów",
    " – w rankingu indywidualnym uwzględnia się wyniki uzyskane w zawodach ujętych "
    "w kalendarzach SPWS, PZSz, EVF i FIE, na zasadach określonych w § 5;",
)
principle_2 = insert_after(principle_1)
add_labeled_text(
    principle_2,
    "2) ",
    "powołania do startów indywidualnych wyłącznie na podstawie rankingu",
    " – do startu indywidualnego powołuje się czterech najwyżej sklasyfikowanych zawodników "
    "w rankingu właściwym dla danej broni, płci i kategorii wiekowej. Zawodnik z zerowym "
    "dorobkiem punktowym nie może zostać powołany do reprezentacji. Wyjątek stanowi "
    "powołanie uzupełniające, o którym mowa w § 4 ust. 5.",
)
for paragraph in (principle_1, principle_2):
    paragraph.paragraph_format.left_indent = Cm(0.65)
    paragraph.paragraph_format.first_line_indent = Cm(-0.4)

old_definitions = [
    find_unique(
        document,
        "1. ranking hybrydowy – ranking indywidualny, w którym wyniki są aktualizowane "
        "z zastosowaniem aktualizacji krokowej albo wygaszania kalendarzowego, zależnie "
        "od organizatora i rodzaju zawodów;",
    ),
    find_unique(
        document,
        "2. aktualizacja krokowa – sposób aktualizacji wyników zawodów organizowanych przez "
        "SPWS, PZSz lub FIE, zgodnie z którym punkty za zawody z poprzedniego sezonu pozostają "
        "w rankingu do czasu uwzględnienia punktów za odpowiadające im zawody w sezonie bieżącym, "
        "po czym poprzedni wynik przestaje być uwzględniany;",
    ),
    find_unique(
        document,
        "3. wygaszanie kalendarzowe – sposób uwzględniania wyników zawodów organizowanych przez "
        "EVF, zgodnie z którym uzyskane punkty pozostają w rankingu przez okres właściwy dla danego "
        "rodzaju zawodów, liczony od dnia zakończenia zawodów, niezależnie od tego, czy zawody mają "
        "odpowiednik w kolejnym sezonie, a po upływie tego okresu przestają być uwzględniane;",
    ),
    find_unique(
        document,
        "4. limitowane zawody międzynarodowe – indywidualne lub drużynowe zawody międzynarodowe "
        "rangi mistrzowskiej, w których liczba zawodników reprezentujących dane państwo jest "
        "ograniczona przepisami organizatora zawodów;",
    ),
    find_unique(
        document,
        "5. powołanie uzupełniające – wyjątkowe powołanie do startu drużynowego zawodnika "
        "nieposiadającego dodatniego dorobku punktowego, dokonywane wyłącznie w celu uzupełnienia "
        "braków uniemożliwiających wystawienie kompletnej i zgodnej z przepisami drużyny.",
    ),
]

replacement_definitions = [
    (
        "5. ",
        "rankingu hybrydowym",
        " – należy przez to rozumieć ranking indywidualny, w którym wyniki są aktualizowane "
        "z zastosowaniem aktualizacji krokowej albo wygaszania kalendarzowego, zależnie od "
        "organizatora i rodzaju zawodów;",
    ),
    (
        "6. ",
        "aktualizacji krokowej",
        " – należy przez to rozumieć sposób aktualizacji wyników zawodów organizowanych przez "
        "SPWS, PZSz lub FIE, zgodnie z którym punkty za zawody z poprzedniego sezonu pozostają "
        "w rankingu do czasu uwzględnienia punktów za odpowiadające im zawody w sezonie bieżącym, "
        "po czym poprzedni wynik przestaje być uwzględniany;",
    ),
    (
        "7. ",
        "wygaszaniu kalendarzowym",
        " – należy przez to rozumieć sposób uwzględniania wyników zawodów organizowanych przez "
        "EVF, zgodnie z którym uzyskane punkty pozostają w rankingu przez okres właściwy dla danego "
        "rodzaju zawodów, liczony od dnia zakończenia zawodów, niezależnie od tego, czy zawody mają "
        "odpowiednik w kolejnym sezonie, a po upływie tego okresu przestają być uwzględniane;",
    ),
    (
        "8. ",
        "limitowanych zawodach międzynarodowych",
        " – należy przez to rozumieć indywidualne lub drużynowe zawody międzynarodowe rangi "
        "mistrzowskiej, w których liczba zawodników reprezentujących dane państwo jest ograniczona "
        "przepisami organizatora zawodów;",
    ),
    (
        "9. ",
        "powołaniu uzupełniającym",
        " – należy przez to rozumieć wyjątkowe powołanie do startu drużynowego zawodnika "
        "nieposiadającego dodatniego dorobku punktowego, dokonywane wyłącznie w celu uzupełnienia "
        "braków uniemożliwiających wystawienie kompletnej i zgodnej z przepisami drużyny.",
    ),
]
for paragraph, (number, term, definition) in zip(old_definitions, replacement_definitions):
    replace_with_term(paragraph, number, term, definition)

first_definition = old_definitions[0]
intro = first_definition.insert_paragraph_before("Ilekroć w Regulaminie jest mowa o:")
intro.style = first_definition.style

abbreviations = [
    ("1. ", "SPWS", " – należy przez to rozumieć Stowarzyszenie Polskich Weteranów Szermierki;"),
    ("2. ", "PZSz", " – należy przez to rozumieć Polski Związek Szermierczy;"),
    ("3. ", "EVF", " – należy przez to rozumieć European Veterans Fencing;"),
    (
        "4. ",
        "FIE",
        " – należy przez to rozumieć Fédération Internationale d’Escrime "
        "(Międzynarodową Federację Szermierczą);",
    ),
]
for number, term, definition in abbreviations:
    paragraph = first_definition.insert_paragraph_before()
    paragraph.style = first_definition.style
    add_labeled_text(paragraph, number, term, definition)

document.core_properties.comments = (
    "Projekt do konsultacji. Zatwierdzono i wprowadzono § 1–§ 6 oraz załącznik nr 1. "
    "Cel Regulaminu w § 2 ust. 1 podlega zmianie wyłącznie po akceptacji autora projektu."
)

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = TARGET.with_name(f"{TARGET.stem}.backup-przed-rewizja-paragrafow-02-03-{timestamp}.docx")
shutil.copy2(TARGET, backup)
temporary = TARGET.with_suffix(".tmp.docx")
document.save(temporary)
os.replace(temporary, TARGET)

print(f"Zapisano: {TARGET}")
print(f"Kopia: {backup}")
