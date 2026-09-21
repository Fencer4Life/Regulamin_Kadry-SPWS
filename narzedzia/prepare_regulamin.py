from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from narzedzia.build_regulamin_docx import build_document
from narzedzia.docx_parity import document_content_contract, document_layout_contract
from narzedzia.normalize_regulamin_markdown import normalize_source
from narzedzia.markdown_preview import preview_path, render_preview


def _atomic_write(path: Path, content: str) -> None:
    path = path.resolve()
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def normalize_and_build(source: Path, output: Path) -> Path:
    normalized = normalize_source(source)
    output = output.resolve()
    if source.resolve() == output or output.suffix.lower() != ".docx":
        raise ValueError("Wyjście musi być osobnym plikiem DOCX")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        candidate = Path(directory) / output.name
        staged_source = Path(directory) / "source.md"
        staged_source.write_text(normalized, encoding="utf-8")
        build_document(staged_source, candidate)
        preview = render_preview(candidate)
        paths = (source, output, preview_path(source))
        backups = [path.read_bytes() if path.exists() else None for path in paths]
        try:
            if source.read_text(encoding="utf-8") != normalized:
                _atomic_write(source, normalized)
            candidate.replace(output)
            _atomic_write(preview_path(source), preview)
        except BaseException:
            for path, content in zip(paths, backups):
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)
            raise
    return output


def verify(source: Path, tracked_docx: Path) -> None:
    before_source = source.read_bytes()
    before_docx = tracked_docx.read_bytes()
    normalized = normalize_source(source)
    if normalized.encode("utf-8") != before_source:
        raise ValueError("Kanoniczny Markdown wymaga normalizacji")
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory) / "regulamin-candidate.docx"
        build_document(source, candidate)
        if document_content_contract(candidate) != document_content_contract(tracked_docx):
            raise ValueError("Treść śledzonego DOCX nie odpowiada Markdown")
        if document_layout_contract(candidate) != document_layout_contract(tracked_docx):
            raise ValueError("Układ śledzonego DOCX nie odpowiada Markdown")
        if not preview_path(source).exists() or preview_path(source).read_text(encoding="utf-8") != render_preview(candidate):
            raise ValueError("Podgląd Markdown jest nieaktualny; wygeneruj dokument ponownie")
    if source.read_bytes() != before_source or tracked_docx.read_bytes() != before_docx:
        raise RuntimeError("Tryb verify zmodyfikował śledzony plik")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalizuje Markdown i bezpiecznie buduje Regulamin")
    subparsers = parser.add_subparsers(dest="mode", required=True)
    build = subparsers.add_parser("normalize-and-build")
    build.add_argument("source", type=Path)
    build.add_argument("output", type=Path)
    check = subparsers.add_parser("verify")
    check.add_argument("source", type=Path)
    check.add_argument("tracked_docx", type=Path)
    arguments = parser.parse_args()
    if arguments.mode == "normalize-and-build":
        print(normalize_and_build(arguments.source, arguments.output))
    else:
        verify(arguments.source, arguments.tracked_docx)
        print("OK: Markdown i DOCX są zgodne")


if __name__ == "__main__":
    main()
