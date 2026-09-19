from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from narzedzia.docx_model import parse_regulation_source


METADATA = '''+++
title = "T"
subtitle = "S"
version = "1"
status = "projekt"
project_date = "2026-09-19"
subject = "S"
comments = "C"
outline_intro = "O"
toc_note = "N"
history_scope = "H"
prototype_note = "P"
+++
'''


class ZtpModelTests(unittest.TestCase):
    def parse(self, body: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.md"
            path.write_text(METADATA + body, encoding="utf-8")
            return parse_regulation_source(path)

    def test_parses_the_complete_ztp_hierarchy(self):
        model = self.parse(
            '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:zasady] Zasady
1. [unit:zasada] Ustęp.
   1) [unit:punkt] Punkt:
      a) [unit:litera] litera:
         - [unit:tiret] tiret:
            -- [unit:double-tiret] podwójne tiret.
'''
        )
        unit = model.chapters[0].sections[0].blocks[0]
        self.assertEqual(unit.kind, "ust")
        self.assertEqual(unit.children[0].kind, "pkt")
        self.assertEqual(unit.children[0].children[0].kind, "lit")
        self.assertEqual(unit.children[0].children[0].children[0].kind, "tiret")
        self.assertEqual(
            unit.children[0].children[0].children[0].children[0].kind,
            "double-tiret",
        )

    def test_single_thought_paragraph_has_no_artificial_subsection(self):
        model = self.parse(
            '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:zasada] Zasada
[unit:jedna-mysl] Jedna myśl.
'''
        )
        self.assertEqual(model.chapters[0].sections[0].blocks[0].kind, "paragraph")

    def test_preserves_source_draft_status(self):
        model = self.parse(
            '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:zasada] Zasada
[unit:szkic] [status:source-draft] Treść do pracy.
'''
        )
        self.assertEqual(
            model.chapters[0].sections[0].blocks[0].status,
            "source-draft",
        )

    def test_rejects_duplicate_unit_identifiers(self):
        with self.assertRaisesRegex(ValueError, "Powtórzony identyfikator"):
            self.parse(
                '''
## [chapter:ogolne] Ogólne
<!-- scope: zakres -->
### [section:zasada] Zasada
1. [unit:duplikat] Pierwszy.
2. [unit:duplikat] Drugi.
'''
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
