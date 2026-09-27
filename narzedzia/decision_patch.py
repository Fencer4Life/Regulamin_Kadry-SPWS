"""Apply an accepted decision literally, without inference or a language model."""

import argparse
import hashlib
import re
import tempfile
from pathlib import Path

from narzedzia.prepare_regulamin import normalize_and_build, verify

OLD = "Stary fragment Markdown"
NEW = "Nowy fragment Markdown"
DOCUMENT_NAMES = {
    "reprezentacja": "Regulamin Reprezentacji",
    "zawody": "Regulamin Zawodów",
}


def format_fragments(old="", new="", *, instructions=True):
    longest = max((len(x) for x in re.findall(r"`+", old + new)), default=0)
    fence = "`" * max(3, longest + 1)
    old_hint = (
        "Wklej dokładny fragment kanonicznego .md, ze znacznikami i wcięciami.\n\n"
        if instructions
        else ""
    )
    new_hint = (
        "Wklej kompletną treść zastępującą stary fragment; zachowaj identyfikatory jednostek.\n\n"
        if instructions
        else ""
    )
    return (
        f"## {OLD}\n\n{old_hint}"
        f"{fence}markdown\n{old}\n{fence}\n\n"
        f"## {NEW}\n\n{new_hint}"
        f"{fence}markdown\n{new}\n{fence}\n"
    )


def format_document_fragments(identifier: str, old: str, new: str) -> str:
    try:
        title = DOCUMENT_NAMES[identifier]
    except KeyError as error:
        raise ValueError(f"Nieznany dokument w karcie decyzji: {identifier}") from error
    fragments = format_fragments(old, new, instructions=False)
    fragments = fragments.replace(f"## {OLD}", f"### {OLD}", 1)
    fragments = fragments.replace(f"## {NEW}", f"### {NEW}", 1)
    return f"## Zmiana — {title}\n\n{fragments}\n"


def read_fragments(card):
    changes = read_document_fragments(card)
    if len(changes) != 1:
        raise ValueError("Karta musi wskazywać dokładnie jeden dokument")
    return next(iter(changes.values()))


def read_document_fragments(card):
    result = {}
    heading = None
    document = "legacy"
    fence = None
    buffer = []
    # Track all fences, so headings copied from source are not decision sections.
    for line in card.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        if fence is not None:
            if raw == fence:
                if heading in {OLD, NEW}:
                    key = (document, heading)
                    if key in result:
                        raise ValueError("Pole zmiany zawiera więcej niż jeden blok kodu")
                    result[key] = "".join(buffer).removesuffix("\n")
                fence, buffer = None, []
            else:
                buffer.append(line)
        elif match := re.fullmatch(r"(`{3,})([a-zA-Z0-9_-]*)", raw):
            if heading in {OLD, NEW} and match.group(2) not in {"markdown", "md", ""}:
                raise ValueError("Fragment zmiany musi być blokiem kodu Markdown")
            fence = match.group(1)
        elif raw.startswith("## Zmiana — "):
            title = raw.removeprefix("## Zmiana — ")
            matches = [key for key, value in DOCUMENT_NAMES.items() if value == title]
            if len(matches) != 1:
                raise ValueError(f"Nieznany dokument w karcie decyzji: {title}")
            document = matches[0]
            heading = None
        elif raw.startswith(("## ", "### ")):
            heading = raw.lstrip("# ")
    documents = {key[0] for key in result}
    if fence is not None or not documents:
        raise ValueError("Wypełnij oba pola: Stary fragment Markdown i Nowy fragment Markdown")
    changes = {}
    for identifier in documents:
        values = tuple(result.get((identifier, heading), "") for heading in (OLD, NEW))
        if any(not value.strip() for value in values):
            raise ValueError("Wypełnij oba pola: Stary fragment Markdown i Nowy fragment Markdown")
        changes[identifier] = values
    return changes


def replace_exact(source, old, new):
    if not old.strip() or not new.strip() or old == new:
        raise ValueError("Stary i nowy fragment muszą być niepuste i różne")
    count = len(re.findall(r"(?=" + re.escape(old) + r")", source))
    if count != 1:
        raise ValueError(f"Stary fragment musi występować dokładnie raz (znaleziono: {count})")
    return source.replace(old, new, 1)


def apply_decision(card_path, source, output, *, require_source_hash=None):
    card = card_path.read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    if not front or not re.search(r"^status: [\"]?przyjęta[\"]?$", front[1], re.MULTILINE):
        raise ValueError("Automat wdraża wyłącznie decyzje o statusie przyjęta")
    if "<!-- applied-source-sha256:" in card:
        raise ValueError("Ta karta ma już zapis wdrożenia; przygotuj nową decyzję")
    original = source.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if require_source_hash is not None and digest != require_source_hash:
        raise ValueError("Źródło zmieniło się od przygotowania decyzji")
    old, new = read_fragments(card)
    changed = replace_exact(original.decode("utf-8"), old, new)
    paths = (source, output, card_path)
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Źródło, DOCX i karta muszą być osobnymi plikami")
    with tempfile.TemporaryDirectory() as directory:
        staged_source = Path(directory) / source.name
        staged_output = Path(directory) / output.name
        staged_source.write_text(changed, encoding="utf-8")
        normalize_and_build(staged_source, staged_output)
        verify(staged_source, staged_output)
        updated_card = card.replace(
            "Oczekuje na etykietę `wdrażaj` na PR.",
            "Wdrożono automatycznie; DOCX do kontroli znajduje się w opisie PR.",
        )
        updated_card = updated_card.rstrip() + f"\n\n<!-- applied-source-sha256:{digest} -->\n"
        contents = (
            staged_source.read_bytes(),
            staged_output.read_bytes(),
            updated_card.encode("utf-8"),
        )
        backups = [path.read_bytes() if path.exists() else None for path in paths]
        try:
            for path, content in zip(paths, contents):
                path.write_bytes(content)
        except BaseException:
            for path, content in zip(paths, backups):
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    apply_decision(args.decision, args.source, args.output)


if __name__ == "__main__":
    main()
