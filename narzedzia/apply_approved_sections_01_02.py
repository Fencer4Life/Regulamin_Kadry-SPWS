from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from docx import Document


TARGET = Path(__file__).resolve().parents[1] / "regulamin" / (
    "Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx"
)

SECTION_1 = (
    "1. Regulamin określa zasady kwalifikowania i powoływania zawodników do reprezentacji "
    "Polski weteranów w szermierce na indywidualne i drużynowe zawody międzynarodowe "
    "rangi mistrzowskiej, w których liczba zawodników reprezentujących państwo podlega "
    "ograniczeniom określonym przez organizatora zawodów."
)

SECTION_2 = (
    "1. Celem zasad określonych w Regulaminie jest wyłonienie możliwie najsilniejszej "
    "reprezentacji Polski weteranów w szermierce, z zachowaniem przejrzystości procesu, "
    "równego traktowania zawodników oraz możliwości zweryfikowania podstaw podjętych decyzji."
)


def set_paragraph(paragraph, text: str, style: str) -> None:
    paragraph.style = style
    paragraph.text = text


def main() -> None:
    if not TARGET.is_file():
        raise SystemExit(f"Nie znaleziono dokumentu docelowego: {TARGET}")

    document = Document(TARGET)
    paragraphs = document.paragraphs

    expected = {
        23: "ROZDZIAŁ I",
        24: "Postanowienia ogólne",
        25: "§ 1",
        26: "1. [Cel regulaminu.]",
        27: "2. [Zakres spraw regulowanych dokumentem.]",
        28: "§ 2",
        29: "1. [Definicje pojęć używanych w regulaminie.]",
        31: "ROZDZIAŁ II",
        33: "§ 3",
        35: "§ 4",
        41: "§ 5",
        47: "§ 6",
        50: "§ 7",
        55: "§ 8",
        61: "§ 9",
        67: "§ 10",
    }
    for index, text in expected.items():
        if paragraphs[index].text != text:
            raise SystemExit(
                f"Dokument zmienił się w nieoczekiwanym miejscu {index}: "
                f"{paragraphs[index].text!r} zamiast {text!r}. Nie zapisano zmian."
            )

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_name(f"{TARGET.stem}.backup-przed-paragrafami-1-2-{timestamp}.docx")
    shutil.copy2(TARGET, backup)

    set_paragraph(paragraphs[25], "§ 1. Przedmiot regulaminu", "Paragraf")
    set_paragraph(paragraphs[26], SECTION_1, "Normal")
    set_paragraph(paragraphs[27], "§ 2. Cel regulaminu", "Paragraf")
    set_paragraph(paragraphs[28], SECTION_2, "Normal")
    set_paragraph(paragraphs[29], "§ 3. Definicje", "Paragraf")
    set_paragraph(paragraphs[30], "1. [Definicje pojęć używanych w Regulaminie.]", "Tekst roboczy")

    shifted_markers = {
        33: "§ 4",
        35: "§ 5",
        41: "§ 6",
        47: "§ 7",
        50: "§ 8",
        55: "§ 9",
        61: "§ 10",
        67: "§ 11",
    }
    for index, text in shifted_markers.items():
        paragraphs[index].text = text

    document.core_properties.comments = (
        "Projekt do konsultacji. Zatwierdzono i wprowadzono § 1 oraz § 2; "
        "pozostała treść normatywna nie została jeszcze uzgodniona."
    )

    temporary = TARGET.with_name(f".{TARGET.name}.tmp")
    document.save(temporary)
    os.replace(temporary, TARGET)

    print(f"TARGET={TARGET}")
    print(f"BACKUP={backup}")


if __name__ == "__main__":
    main()
