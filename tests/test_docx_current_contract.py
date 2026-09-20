from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from docx import Document
from narzedzia.build_regulamin_docx import build_document
from narzedzia.docx_parity import document_content_contract


ROOT = Path(__file__).resolve().parents[1]
CURRENT_DOCUMENT = ROOT / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx"
)
CANONICAL_SOURCE = ROOT / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranow-w-szermierce_2026.md"
)
EXPECTED_HEADINGS = [
    "Spis treści",
    "Konstrukcja regulaminu",
    "Postanowienia ogólne",
    "§ 1", "Przedmiot regulaminu",
    "§ 2", "Definicje",
    "§ 3", "Cel i zasady wyłaniania reprezentacji",
    "Ranking indywidualny",
    "§ 4", "Rola rankingu indywidualnego",
    "§ 5", "Zawody uwzględniane w rankingu",
    "§ 6", "Zasady obliczania punktów",
    "§ 7", "Publikacja rankingu",
    "§ 8", "Wyniki w połączonych kategoriach wiekowych",
    "§ 9", "Zawodnicy uwzględniani w rankingu",
    "Powołania do startów indywidualnych",
    "§ 10", "Zasady powołań indywidualnych",
    "§ 11", "Rezygnacja i zastępstwo",
    "Dobór składu drużyny",
    "§ 12", "Pula kandydatów do drużyny",
    "§ 13", "Kategorie wiekowe w drużynie",
    "§ 14", "Drużynowe Mistrzostwa Europy",
    "§ 15", "Drużynowe Mistrzostwa Świata",
    "§ 16", "Powołanie uzupełniające",
    "Terminarz procesu powoływania",
    "§ 17", "Terminy procesu",
    "Ocena regulaminu i doskonalenie metody",
    "§ 18", "Ocena posezonowa",
    "Postanowienia końcowe",
    "§ 19", "Wejście w życie",
    "Tabela punktacji Pucharu Polski Weteranów w szermierce",
    "Miejsca 1–10 · stawka 4–20 zawodników",
    "Miejsca 1–10 · stawka 21–37 zawodników",
    "Miejsca 1–10 · stawka 38–40 zawodników",
    "Miejsca 11–20 · stawka 11–27 zawodników",
    "Miejsca 11–20 · stawka 28–40 zawodników",
    "Miejsca 21–30 · stawka 21–37 zawodników",
    "Miejsca 21–30 · stawka 38–40 zawodników",
    "Miejsca 31–40 · stawka 31–40 zawodników",
    "Historia wersji",
    "Informacja o prototypie",
]


class CurrentDocxContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = Document(CURRENT_DOCUMENT)
        cls.contract = document_content_contract(CURRENT_DOCUMENT)

    def test_current_document_shape_is_frozen_before_generator_work(self):
        self.assertEqual(len(self.document.paragraphs), 202)
        self.assertEqual(len(self.document.tables), 16)
        self.assertEqual(sum(len(table.rows) for table in self.document.tables), 145)
        self.assertEqual(len(self.contract["blocks"]), 218)

    def test_current_document_heading_order_is_explicit(self):
        headings = [
            paragraph.text
            for paragraph in self.document.paragraphs
            if paragraph.style.name in {"Heading 1", "Heading 2", "Paragraf", "Tytuł paragrafu"}
        ]
        self.assertEqual(headings, EXPECTED_HEADINGS)

    def test_current_document_matches_the_canonical_markdown_source(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.docx"
            build_document(CANONICAL_SOURCE, candidate)
            self.assertEqual(
                self.contract,
                document_content_contract(candidate),
                "Śledzony DOCX nie odpowiada kanonicznemu źródłu Markdown",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
