from __future__ import annotations

import os
import unittest
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = ROOT / "regulamin" / (
    "Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx"
)
DOCUMENT = Path(os.environ.get("REGULAMIN_DOCX_PATH", DEFAULT_DOCUMENT))
ALLOWED_EDITOR = "Komisja regulaminowa SPWS"

CORE_NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
}
WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


class DocxPublicationSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = ZipFile(DOCUMENT)

    @classmethod
    def tearDownClass(cls):
        cls.archive.close()

    def test_document_contains_no_comments(self):
        comment_parts = [name for name in self.archive.namelist() if "comments" in name.lower()]
        self.assertEqual(comment_parts, [], f"DOCX zawiera komentarze: {comment_parts}")

    def test_document_contains_no_tracked_changes(self):
        document = etree.fromstring(self.archive.read("word/document.xml"))
        tracked_tags = ("ins", "del", "moveFrom", "moveTo")
        found = {
            tag: len(document.xpath(f"//w:{tag}", namespaces=WORD_NS))
            for tag in tracked_tags
        }
        self.assertEqual(found, {tag: 0 for tag in tracked_tags})

    def test_public_metadata_uses_commission_role_not_personal_name(self):
        core = etree.fromstring(self.archive.read("docProps/core.xml"))
        creator = core.findtext("dc:creator", namespaces=CORE_NS)
        last_modified_by = core.findtext("cp:lastModifiedBy", namespaces=CORE_NS)
        self.assertEqual(creator, ALLOWED_EDITOR)
        self.assertEqual(last_modified_by, ALLOWED_EDITOR)


if __name__ == "__main__":
    unittest.main(verbosity=2)
