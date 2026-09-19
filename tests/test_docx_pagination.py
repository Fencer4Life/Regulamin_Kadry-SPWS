from __future__ import annotations

import sys
import unittest
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


DEFAULT_DOCUMENT = Path(__file__).resolve().parents[1] / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx"
)
MAX_ATOMIC_TABLE_ROWS = 18


class PaginationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = (
            Path(sys.argv[1])
            if len(sys.argv) == 2 and sys.argv[1].lower().endswith(".docx")
            else DEFAULT_DOCUMENT
        )
        cls.document = Document(path)

    def test_each_chapter_starts_on_new_page(self):
        chapters = [p for p in self.document.paragraphs if p.text.startswith("Rozdział ")]
        self.assertGreater(len(chapters), 0, "Dokument nie zawiera nagłówków rozdziałów")
        for chapter in chapters:
            with self.subTest(chapter=chapter.text):
                self.assertIs(
                    chapter.paragraph_format.page_break_before,
                    True,
                    f"{chapter.text} nie ma wymuszonego początku nowej strony",
                )

    def test_each_later_section_in_chapter_starts_on_new_page(self):
        section_seen_in_chapter = False
        later_sections = []
        for paragraph in self.document.paragraphs:
            if paragraph.text.startswith("Rozdział "):
                section_seen_in_chapter = False
            elif paragraph.text.startswith("§ "):
                if section_seen_in_chapter:
                    later_sections.append(paragraph)
                section_seen_in_chapter = True

        self.assertGreater(len(later_sections), 0, "Dokument nie zawiera kolejnych paragrafów w rozdziałach")
        for section in later_sections:
            with self.subTest(section=section.text):
                self.assertIs(
                    section.paragraph_format.page_break_before,
                    True,
                    f"{section.text} nie ma wymuszonego początku nowej strony",
                )

    def test_definitions_and_purpose_each_start_on_a_new_page(self):
        paragraphs = self.document.paragraphs
        headings = ("§ 2", "§ 3")
        for heading in headings:
            paragraph = next(p for p in paragraphs if p.text == heading)
            with self.subTest(heading=heading):
                self.assertIs(paragraph.paragraph_format.page_break_before, True)

    def test_each_table_is_small_enough_to_fit_on_one_page(self):
        for index, table in enumerate(self.document.tables, start=1):
            with self.subTest(table=index, first_cell=table.rows[0].cells[0].text):
                self.assertLessEqual(
                    len(table.rows),
                    MAX_ATOMIC_TABLE_ROWS,
                    f"Tabela {index} ma {len(table.rows)} wierszy i może przejść na następną stronę",
                )

    def test_each_table_row_is_indivisible(self):
        missing = []
        for table_index, table in enumerate(self.document.tables, start=1):
            for row_index, row in enumerate(table.rows, start=1):
                properties = row._tr.get_or_add_trPr()
                if properties.find(qn("w:cantSplit")) is None:
                    missing.append((table_index, row_index))
        self.assertEqual(missing, [], f"Podzielne wiersze tabel: {missing[:20]}")

    def test_table_rows_are_kept_together(self):
        missing = []
        for table_index, table in enumerate(self.document.tables, start=1):
            for row_index, row in enumerate(table.rows[:-1], start=1):
                for cell_index, cell in enumerate(row.cells, start=1):
                    for paragraph_index, paragraph in enumerate(cell.paragraphs, start=1):
                        if paragraph.paragraph_format.keep_with_next is not True:
                            missing.append((table_index, row_index, cell_index, paragraph_index))
        self.assertEqual(missing, [], f"Brak keep-with-next w tabelach: {missing[:20]}")

    def test_annex_still_contains_every_score_from_4_to_40(self):
        annex_tables = [
            table
            for table in self.document.tables
            if table.rows[0].cells[0].text == "Liczba zawodników w stawce"
        ]
        cells = set()
        for table in annex_tables:
            places = [int(cell.text) for cell in table.rows[0].cells[1:]]
            for row in table.rows[1:]:
                participants = int(row.cells[0].text)
                for place, cell in zip(places, row.cells[1:]):
                    if cell.text != "—":
                        cells.add((participants, place))
        expected = {
            (participants, place)
            for participants in range(4, 41)
            for place in range(1, participants + 1)
        }
        self.assertEqual(cells, expected)


if __name__ == "__main__":
    # Ścieżka dokumentu jest argumentem testów, nie nazwą testu dla unittest.
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".docx"):
        document_argument = sys.argv.pop(1)
        sys.argv.append(document_argument)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
