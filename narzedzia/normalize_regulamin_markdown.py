from __future__ import annotations

import argparse
import re
from pathlib import Path

from narzedzia.docx_model import RegulationDocument, TableBlock, ZtpUnit, parse_regulation_source


REFERENCE_RE = re.compile(r"\{\{ref:([a-z0-9-]+)/([a-z0-9-]+)}}")
INDENTS = {"paragraph": 0, "ust": 0, "pkt": 3, "lit": 6, "tiret": 9, "double-tiret": 12}


def _markdown_text(unit: ZtpUnit) -> str:
    return "".join(f"**{run.text}**" if run.bold else run.text for run in unit.runs)


def _unit_marker(unit: ZtpUnit, index: int) -> str:
    if unit.kind == "paragraph":
        return ""
    if unit.kind == "ust":
        return f"{index}. "
    if unit.kind == "pkt":
        return f"{index}) "
    if unit.kind == "lit":
        if index > 26:
            raise ValueError("Jedno wyliczenie nie może zawierać więcej niż 26 liter")
        return f"{chr(96 + index)}) "
    if unit.kind == "tiret":
        return "- "
    if unit.kind == "double-tiret":
        return "-- "
    raise ValueError(f"Nieobsługiwany rodzaj jednostki: {unit.kind}")


def _canonical_punctuation(text: str, unit: ZtpUnit, index: int, total: int) -> str:
    stem = text.rstrip().rstrip(".,;:")
    if unit.children:
        ending = ":"
    elif unit.kind == "pkt":
        ending = ";" if index < total else "."
    elif unit.kind in {"lit", "tiret", "double-tiret"}:
        ending = "," if index < total else "."
    else:
        ending = "."
    return stem + ending


def _serialize_unit(unit: ZtpUnit, index: int, total: int, lines: list[str]) -> None:
    status = "" if unit.status == "accepted" else f" [status:{unit.status}]"
    indent = " " * INDENTS[unit.kind]
    lines.append(
        f"{indent}{_unit_marker(unit, index)}[unit:{unit.identifier}]{status} "
        f"{_canonical_punctuation(_markdown_text(unit), unit, index, total)}"
    )
    child_total = len(unit.children)
    for child_index, child in enumerate(unit.children, start=1):
        _serialize_unit(child, child_index, child_total, lines)


def serialize_regulation(model: RegulationDocument) -> str:
    lines = ["+++", model.metadata_source, "+++", ""]
    for chapter in model.chapters:
        lines.extend(
            [
                f"## [chapter:{chapter.identifier}] {chapter.title}",
                f"<!-- scope: {chapter.scope} -->",
                "",
            ]
        )
        for section in chapter.sections:
            heading = f"### [section:{section.identifier}]"
            if section.title:
                heading += f" {section.title}"
            lines.extend([heading, ""])
            unit_blocks = [block for block in section.blocks if isinstance(block, ZtpUnit)]
            unit_index = 0
            for block in section.blocks:
                if isinstance(block, ZtpUnit):
                    unit_index += 1
                    _serialize_unit(block, unit_index, len(unit_blocks), lines)
                elif isinstance(block, TableBlock):
                    lines.extend(["", f"{{{{table:{block.name}}}}}", ""])
                    lines.append("| " + " | ".join(block.rows[0]) + " |")
                    lines.append("| " + " | ".join("---" for _ in block.rows[0]) + " |")
                    for row in block.rows[1:]:
                        lines.append("| " + " | ".join(row) + " |")
                else:
                    raise ValueError(f"Nieobsługiwany blok: {type(block).__name__}")
                lines.append("")
        if lines[-1] != "":
            lines.append("")
    if model.has_points_annex:
        lines.extend(["{{annex:points}}", ""])
    return "\n".join(lines).rstrip() + "\n"


def normalize_source(path: Path) -> str:
    return serialize_regulation(parse_regulation_source(path))


def _reference_index(model: RegulationDocument) -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    section_number = 0
    for chapter in model.chapters:
        for section in chapter.sections:
            section_number += 1
            prefix = f"§ {section_number}"

            def visit(unit: ZtpUnit, parents: list[tuple[str, int]], number: int) -> None:
                current = parents + [(unit.kind, number)]
                labels = {"ust": "ust.", "pkt": "pkt", "lit": "lit."}
                suffix: list[str] = []
                for kind, visible in current:
                    if kind in labels:
                        value = chr(96 + visible) if kind == "lit" else str(visible)
                        suffix.extend((labels[kind], value))
                    elif kind == "tiret":
                        suffix.extend(("tiret", str(visible)))
                    elif kind == "double-tiret":
                        suffix.extend(("podwójne tiret", str(visible)))
                index[(section.identifier, unit.identifier)] = " ".join([prefix, *suffix])
                for child_number, child in enumerate(unit.children, start=1):
                    visit(child, current, child_number)

            unit_number = 0
            for block in section.blocks:
                if isinstance(block, ZtpUnit):
                    unit_number += 1
                    visit(block, [], unit_number)
    return index


def resolve_references(model: RegulationDocument, text: str) -> str:
    references = _reference_index(model)

    def replace(match: re.Match[str]) -> str:
        key = (match.group(1), match.group(2))
        try:
            return references[key]
        except KeyError as error:
            raise ValueError(f"Nieznane odwołanie: {match.group(0)}") from error

    return REFERENCE_RE.sub(replace, text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalizuje semantyczny Markdown regulaminu do ZTP")
    parser.add_argument("source", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    normalized = normalize_source(arguments.source)
    current = arguments.source.read_text(encoding="utf-8")
    if arguments.check:
        if current != normalized:
            raise SystemExit("Markdown nie jest znormalizowany; uruchom z --write")
        print(f"OK: {arguments.source}")
        return
    arguments.source.write_text(normalized, encoding="utf-8")
    print(arguments.source)


if __name__ == "__main__":
    main()
