from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from docx import Document
from narzedzia.docx_parity import document_content_contract


ROOT = Path(__file__).resolve().parents[1]
CURRENT_DOCUMENT = ROOT / "regulamin" / (
    "Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx"
)
EXPECTED_HEADINGS = [
    "Spis treści",
    "Konstrukcja regulaminu",
    "Postanowienia ogólne",
    "§ 1. Przedmiot regulaminu",
    "§ 2. Cel regulaminu",
    "§ 3. Definicje",
    "Ranking indywidualny",
    "§ 4. Rola rankingu indywidualnego",
    "§ 5. Zawody uwzględniane w rankingu",
    "§ 6. Zasady obliczania punktów",
    "Powołania do startów indywidualnych",
    "§ 7",
    "Dobór składu drużyny",
    "§ 8",
    "§ 9",
    "Terminarz procesu powoływania",
    "§ 10",
    "Ocena regulaminu i doskonalenie metody",
    "§ 11",
    "Postanowienia końcowe",
    "§ 12",
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


def contract_sha256(contract: dict[str, object]) -> str:
    payload = json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class CurrentDocxContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = Document(CURRENT_DOCUMENT)
        cls.contract = document_content_contract(CURRENT_DOCUMENT)

    def test_current_document_shape_is_frozen_before_generator_work(self):
        self.assertEqual(len(self.document.paragraphs), 129)
        self.assertEqual(len(self.document.tables), 12)
        self.assertEqual(sum(len(table.rows) for table in self.document.tables), 127)
        self.assertEqual(len(self.contract["blocks"]), 141)

    def test_current_document_heading_order_is_explicit(self):
        headings = [
            paragraph.text
            for paragraph in self.document.paragraphs
            if paragraph.style.name in {"Heading 1", "Heading 2", "Paragraf"}
        ]
        self.assertEqual(headings, EXPECTED_HEADINGS)

    def test_current_document_full_content_contract_is_frozen(self):
        self.assertEqual(
            contract_sha256(self.contract),
            "4d2a26722638fb6c21ee17d35a6db6451f691a95691248f5dbc1d88d56056b9a",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
