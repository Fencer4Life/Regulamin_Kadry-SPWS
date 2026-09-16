from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


CHAPTER_RE = re.compile(r"^## \[chapter:([a-z0-9-]+)] (.+)$")
SECTION_RE = re.compile(r"^### \[section:([a-z0-9-]+)](?: (.*))?$")
SCOPE_RE = re.compile(r"^<!-- scope: (.+) -->$")


@dataclass(frozen=True)
class InlineRun:
    text: str
    bold: bool = False


@dataclass(frozen=True)
class ParagraphBlock:
    text: str
    draft: bool = False
    runs: tuple[InlineRun, ...] = ()


@dataclass(frozen=True)
class TableBlock:
    name: str
    rows: list[list[str]]


ContentBlock = ParagraphBlock | TableBlock


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
        "title",
        "subtitle",
        "version",
        "status",
        "project_date",
        "subject",
        "comments",
        "outline_intro",
        "toc_note",
        "history_scope",
        "prototype_note",
    }
    missing = sorted(required - metadata.keys())
    if missing:
        raise ValueError(f"Brak wymaganych metadanych: {missing}")

    lines = markdown.splitlines()
    chapters: list[RegulationChapter] = []
    current_chapter: RegulationChapter | None = None
    current_section: RegulationSection | None = None
    has_points_annex = False
    identifiers: set[str] = set()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
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
        draft = line.startswith("~ ")
        raw_text = line[2:] if draft else line
        plain_text, runs = _parse_inline_runs(raw_text)
        current_section.blocks.append(ParagraphBlock(text=plain_text, draft=draft, runs=runs))

    if not chapters or any(not chapter.sections for chapter in chapters):
        raise ValueError("Każdy dokument i rozdział musi zawierać co najmniej jeden paragraf")
    if any(not chapter.scope for chapter in chapters):
        raise ValueError("Każdy rozdział musi mieć opis zakresu")
    return RegulationDocument(
        metadata={key: str(value) for key, value in metadata.items()},
        chapters=chapters,
        has_points_annex=has_points_annex,
    )
