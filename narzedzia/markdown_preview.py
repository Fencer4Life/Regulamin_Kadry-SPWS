"""Deterministic, read-only Markdown view of all generated DOCX body content."""

from docx import Document
from docx.table import Table
from docx.text.hyperlink import Hyperlink


def _text(paragraph):
    parts = []
    for item in paragraph.iter_inner_content():
        if isinstance(item, Hyperlink) and item.address:
            parts.append(f"[{item.text}]({item.address})")
        else:
            parts.append(item.text)
    return "".join(parts)


def render_preview(docx_path):
    lines = ["> Podgląd generowany automatycznie z tego samego modelu co DOCX. "
             "Nie edytuj tego pliku — zmieniaj kanoniczny `.md` bez końcówki `.podglad`.", ""]
    for block in Document(docx_path).iter_inner_content():
        if isinstance(block, Table):
            for number, row in enumerate(block.rows):
                cells = ["<br>".join(_text(p) for p in cell.paragraphs)
                         .replace("|", "&#124;") for cell in row.cells]
                lines.append("| " + " | ".join(cells) + " |")
                if number == 0:
                    lines.append("| " + " | ".join("---" for _ in cells) + " |")
        else:
            text = _text(block)
            if not text.strip():
                continue
            style = block.style.name
            prefix = {"Title": "# ", "Heading 1": "## ", "Heading 2": "### ",
                      "Paragraf": "### ", "Tytuł paragrafu": "#### "}.get(style, "")
            lines.append(prefix + text)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def preview_path(source):
    return source.with_suffix(".podglad.md")
