from __future__ import annotations

import argparse
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = ROOT / "regulamin" / (
    "Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx"
)
PUBLIC_EDITOR = "Komisja regulaminowa SPWS"

CORE_NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
}
WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def assert_safe_revision_state(archive: ZipFile) -> None:
    comment_parts = [name for name in archive.namelist() if "comments" in name.lower()]
    if comment_parts:
        raise RuntimeError(f"Dokument zawiera komentarze: {comment_parts}")

    document = etree.fromstring(archive.read("word/document.xml"))
    tracked_tags = ("ins", "del", "moveFrom", "moveTo")
    found = [
        tag
        for tag in tracked_tags
        if document.xpath(f"//w:{tag}", namespaces=WORD_NS)
    ]
    if found:
        raise RuntimeError(f"Dokument zawiera niezaakceptowane śledzone zmiany: {found}")


def sanitized_core_properties(xml: bytes) -> bytes:
    root = etree.fromstring(xml)
    creator = root.find("dc:creator", namespaces=CORE_NS)
    last_modified_by = root.find("cp:lastModifiedBy", namespaces=CORE_NS)
    if creator is None or last_modified_by is None:
        raise RuntimeError("DOCX nie zawiera wymaganych pól metadanych autora")
    creator.text = PUBLIC_EDITOR
    last_modified_by.text = PUBLIC_EDITOR
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def sanitize(path: Path) -> None:
    temporary = path.with_suffix(".sanitized.docx")
    try:
        with ZipFile(path, "r") as source:
            assert_safe_revision_state(source)
            core = sanitized_core_properties(source.read("docProps/core.xml"))
            with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as target:
                for item in source.infolist():
                    payload = core if item.filename == "docProps/core.xml" else source.read(item.filename)
                    target.writestr(item, payload)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Usuwa osobowe metadane autora z DOCX przeznaczonego do publikacji."
    )
    parser.add_argument("document", nargs="?", type=Path, default=DEFAULT_DOCUMENT)
    args = parser.parse_args()
    sanitize(args.document.resolve())
    print(args.document.resolve())


if __name__ == "__main__":
    main()
