from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


CHAPTER_RE = re.compile(r"^## \[chapter:([a-z0-9-]+)] (.+)$")
SECTION_RE = re.compile(r"^### \[section:([a-z0-9-]+)](?: (.*))?$")
SCOPE_RE = re.compile(r"^<!-- scope: (.+) -->$")
UNIT_RE = re.compile(
    r"^(?P<indent> *)(?:(?P<ust>\d+)\.|(?P<pkt>\d+)\)|"
    r"(?P<lit>[a-z])\)|(?P<tiret>--|-))?\s*"
    r"\[unit:(?P<identifier>[a-z0-9-]+)]"
    r"(?: \[status:(?P<status>accepted|source-draft|placeholder)])?"
    r"\s+(?P<text>.+)$"
)

UNIT_LEVELS = {
    "paragraph": 0,
    "ust": 0,
    "pkt": 1,
    "lit": 2,
    "tiret": 3,
    "double-tiret": 4,
}


@dataclass(frozen=True)
class InlineRun:
    text: str
    bold: bool = False


@dataclass
class ZtpUnit:
    identifier: str
    kind: str
    text: str
    status: str = "accepted"
    runs: tuple[InlineRun, ...] = ()
    children: list["ZtpUnit"] = field(default_factory=list)

    @property
    def draft(self) -> bool:
        return self.status != "accepted"


ParagraphBlock = ZtpUnit


@dataclass(frozen=True)
class TableBlock:
    name: str
    rows: list[list[str]]


ContentBlock = ZtpUnit | TableBlock


def _parse_inline_runs(text: str) -> tuple[str, tuple[InlineRun, ...]]:
    if text.count("**") % 2:
        raise ValueError(f"Niedomknięte pogrubienie Markdown: {text}")
    runs: list[InlineRun] = []
    position = 0
    for match in re.finditer(r"\*\*(.+?)\*\*", text):
        if match.start() > position:
            runs.append(InlineRun(text=text[position : match.start()]))
        runs.append(InlineRun(text=match.group(1), bold=True))
        position = match.end()
    if position < len(text):
        runs.append(InlineRun(text=text[position:]))
    if not runs:
        runs.append(InlineRun(text=text))
    return "".join(run.text for run in runs), tuple(runs)


@dataclass
class RegulationSection:
    identifier: str
    title: str
    blocks: list[ContentBlock] = field(default_factory=list)


@dataclass
class RegulationChapter:
    identifier: str
    title: str
    scope: str = ""
    sections: list[RegulationSection] = field(default_factory=list)


@dataclass(frozen=True)
class RegulationDocument:
    metadata: dict[str, str]
    chapters: list[RegulationChapter]
    has_points_annex: bool
    metadata_source: str = ""


def _parse_markdown_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    index = start
    while index < len(lines) and lines[index].startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
        index += 1
    if len(rows) < 2:
        raise ValueError("Tabela Markdown musi zawierać nagłówek i co najmniej jeden wiersz")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Wszystkie wiersze tabeli Markdown muszą mieć tę samą szerokość")
    return rows, index


def _unit_kind(match: re.Match[str]) -> str:
    if match.group("ust") is not None:
        return "ust"
    if match.group("pkt") is not None:
        return "pkt"
    if match.group("lit") is not None:
        return "lit"
    if match.group("tiret") == "-":
        return "tiret"
    if match.group("tiret") == "--":
        return "double-tiret"
    return "paragraph"


def _append_unit(section: RegulationSection, unit: ZtpUnit, stack: dict[int, ZtpUnit]) -> None:
    level = UNIT_LEVELS[unit.kind]
    if level == 0:
        section.blocks.append(unit)
        stack.clear()
        stack[0] = unit
        return
    parent = stack.get(level - 1)
    if parent is None:
        raise ValueError(
            f"Jednostka {unit.identifier} ({unit.kind}) nie ma jednostki nadrzędnej"
        )
    if unit.status == "accepted" and parent.status != "accepted":
        unit.status = parent.status
    parent.children.append(unit)
    for stale_level in tuple(stack):
        if stale_level >= level:
            del stack[stale_level]
    stack[level] = unit


def parse_regulation_source(path: Path) -> RegulationDocument:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("+++\n"):
        raise ValueError("Brak otwierającego bloku metadanych TOML")
    try:
        metadata_text, markdown = text[4:].split("\n+++\n", 1)
    except ValueError as error:
        raise ValueError("Brak zamykającego bloku metadanych TOML") from error
    metadata = tomllib.loads(metadata_text)
    required = {
        "title", "subtitle", "version", "status", "project_date", "subject",
        "comments", "outline_intro", "toc_note", "history_scope", "prototype_note",
    }
    missing = sorted(required - metadata.keys())
    if missing:
        raise ValueError(f"Brak wymaganych metadanych: {missing}")

    lines = markdown.splitlines()
    chapters: list[RegulationChapter] = []
    current_chapter: RegulationChapter | None = None
    current_section: RegulationSection | None = None
    unit_stack: dict[int, ZtpUnit] = {}
    has_points_annex = False
    identifiers: set[str] = set()
    index = 0
    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()
        index += 1
        if not line:
            continue
        if match := CHAPTER_RE.fullmatch(line):
            identifier, title = match.groups()
            if identifier in identifiers:
                raise ValueError(f"Powtórzony identyfikator: {identifier}")
            identifiers.add(identifier)
            current_chapter = RegulationChapter(identifier=identifier, title=title)
            chapters.append(current_chapter)
            current_section = None
            unit_stack.clear()
            continue
        if match := SCOPE_RE.fullmatch(line):
            if current_chapter is None or current_section is not None:
                raise ValueError("Zakres musi wystąpić bezpośrednio w rozdziale")
            current_chapter.scope = match.group(1)
            continue
        if match := SECTION_RE.fullmatch(line):
            if current_chapter is None:
                raise ValueError("Paragraf musi należeć do rozdziału")
            identifier, title = match.groups()
            if identifier in identifiers:
                raise ValueError(f"Powtórzony identyfikator: {identifier}")
            identifiers.add(identifier)
            current_section = RegulationSection(identifier=identifier, title=title or "")
            current_chapter.sections.append(current_section)
            unit_stack.clear()
            continue
        if line == "{{table:rank-coefficients}}":
            if current_section is None:
                raise ValueError("Tabela współczynników musi należeć do paragrafu")
            while index < len(lines) and not lines[index].strip():
                index += 1
            rows, index = _parse_markdown_table(lines, index)
            current_section.blocks.append(TableBlock(name="rank-coefficients", rows=rows))
            continue
        if line == "{{annex:points}}":
            has_points_annex = True
            continue
        if line.startswith(("## ", "### ", "{{")):
            raise ValueError(f"Nieobsługiwana konstrukcja Markdown: {line}")
        if current_section is None:
            raise ValueError(f"Treść poza paragrafem: {line}")
        unit_match = UNIT_RE.fullmatch(raw_line)
        if unit_match is None:
            raise ValueError(
                "Treść jednostki musi zawierać stabilny identyfikator [unit:...]: "
                f"{line}"
            )
        identifier = unit_match.group("identifier")
        if identifier in identifiers:
            raise ValueError(f"Powtórzony identyfikator: {identifier}")
        identifiers.add(identifier)
        kind = _unit_kind(unit_match)
        plain_text, runs = _parse_inline_runs(unit_match.group("text"))
        unit = ZtpUnit(
            identifier=identifier,
            kind=kind,
            text=plain_text,
            status=unit_match.group("status") or "accepted",
            runs=runs,
        )
        _append_unit(current_section, unit, unit_stack)

    if not chapters or any(not chapter.sections for chapter in chapters):
        raise ValueError("Każdy dokument i rozdział musi zawierać co najmniej jeden paragraf")
    if any(not chapter.scope for chapter in chapters):
        raise ValueError("Każdy rozdział musi mieć opis zakresu")
    if any(not section.blocks for chapter in chapters for section in chapter.sections):
        raise ValueError("Każdy paragraf musi zawierać co najmniej jedną jednostkę")
    return RegulationDocument(
        metadata={key: str(value) for key, value in metadata.items()},
        chapters=chapters,
        has_points_annex=has_points_annex,
        metadata_source=metadata_text,
    )
