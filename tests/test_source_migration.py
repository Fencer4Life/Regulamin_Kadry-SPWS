from __future__ import annotations

import json
import unittest
from pathlib import Path

from docx import Document
from narzedzia.docx_model import ZtpUnit, parse_regulation_source


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "dokumentacja/migracja/2026-09-19-mapa-tresci-zrodlowej.json"
SOURCE = ROOT / "regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md"
DISCUSSIONS = ROOT / "dokumentacja/dyskusje/2026-09-19-propozycje-z-dokumentu-zrodlowego.md"
DOCX = ROOT / "regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx"


def walk(unit: ZtpUnit):
    yield unit
    for child in unit.children:
        yield from walk(child)


class SourceMigrationTests(unittest.TestCase):
    def test_manifest_accounts_for_every_identified_source_fragment(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            data["source_sha256"],
            "8b971d22f44a87874131e400e75409be8a5a350a60697416664dd9d069f02c83",
        )
        self.assertNotIn("/Users/", json.dumps(data, ensure_ascii=False))
        fragments = data["fragments"]
        self.assertEqual(len(fragments), 18)
        self.assertEqual(len({item["id"] for item in fragments}), 18)
        allowed = {"accepted", "source-draft", "replaced", "discussion-proposal"}
        self.assertTrue(all(item["status"] in allowed for item in fragments))
        self.assertTrue(all(item.get("destination") or item.get("reason") for item in fragments))

    def test_regulation_contains_labeled_drafts_but_not_the_author_comment(self):
        source_text = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("to chyba miałoby sens", source_text.lower())
        model = parse_regulation_source(SOURCE)
        statuses = {
            unit.status
            for chapter in model.chapters
            for section in chapter.sections
            for block in section.blocks
            if isinstance(block, ZtpUnit)
            for unit in walk(block)
        }
        self.assertEqual(statuses, {"accepted"})

    def test_accepted_ranking_rules_are_not_rendered_as_source_drafts(self):
        model = parse_regulation_source(SOURCE)
        units = {
            unit.identifier: unit
            for chapter in model.chapters
            for section in chapter.sections
            for block in section.blocks
            if isinstance(block, ZtpUnit)
            for unit in walk(block)
        }
        accepted_identifiers = (
            "publikacja-rankingu-zrodlo",
            "polaczone-kategorie-zrodlo",
            "ranking-warunek-startu-krajowego",
            "ranking-powolanie-obywatelstwo",
            "ranking-evf-fie-reprezentacja",
        )
        for identifier in accepted_identifiers:
            with self.subTest(identifier=identifier):
                self.assertIn(identifier, units)
                self.assertEqual(units[identifier].status, "accepted")

    def test_author_questions_are_routed_to_discussion_proposals(self):
        text = DISCUSSIONS.read_text(encoding="utf-8")
        self.assertIn("Drużynowe Mistrzostwa Świata", text)
        self.assertIn("kosztów podróży i pobytu", text)
        self.assertNotIn("to chyba miałoby sens", text.lower())

    def test_docx_marks_every_continuous_source_draft_section_visibly(self):
        document = Document(DOCX)
        labels = [
            paragraph for paragraph in document.paragraphs
            if paragraph.text == "BRUDNOPIS ZE ŹRÓDŁA — DO OPRACOWANIA"
        ]
        self.assertEqual(len(labels), 0)
        draft_texts = {
            "W przypadku rezygnacji zawodnika z udziału w zawodach indywidualnych jego miejsce przechodzi na kolejnego zawodnika zgodnie z aktualnym rankingiem indywidualnym.",
            "1. Regulamin przyjmuje Zarząd SPWS w drodze uchwały. Regulamin wchodzi w życie w terminie określonym w tej uchwale.",
        }
        paragraphs = {paragraph.text: paragraph for paragraph in document.paragraphs}
        for text in draft_texts:
            self.assertIn(text, paragraphs)
            colors = {str(run.font.color.rgb) for run in paragraphs[text].runs if run.text}
            self.assertNotIn("595959", colors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
