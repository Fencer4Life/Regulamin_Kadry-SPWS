"""Apply an accepted decision literally, without inference or a language model."""

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

from narzedzia.prepare_regulamin import normalize_and_build, verify
from narzedzia.regulation_registry import get_regulation

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


def _front_value(card: str, key: str) -> str:
    front = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    if not front:
        return ""
    match = re.search(rf"^{re.escape(key)}:\s*(.*)$", front.group(1), re.MULTILINE)
    return match.group(1).strip() if match else ""


def document_ids(card: str) -> tuple[str, ...]:
    changes = read_document_fragments(card)
    identifiers = tuple(changes)
    if identifiers == ("legacy",):
        return ("reprezentacja",)
    declared = _front_value(card, "dokumenty")
    if declared:
        try:
            metadata = json.loads(declared)
        except json.JSONDecodeError as error:
            raise ValueError("Niepoprawna lista dokumentów w karcie decyzji") from error
        if not isinstance(metadata, list) or set(metadata) != set(identifiers):
            raise ValueError("Fragmenty nie odpowiadają liście dokumentów w karcie decyzji")
    return identifiers


def registered_paths(card: str, root: Path) -> dict[str, tuple[Path, Path]]:
    return {
        identifier: (
            get_regulation(identifier).source_path(root),
            get_regulation(identifier).docx_path(root),
        )
        for identifier in document_ids(card)
    }


def _source_digest(originals: dict[str, bytes]) -> str:
    if set(originals) == {"legacy"}:
        return hashlib.sha256(originals["legacy"]).hexdigest()
    digest = hashlib.sha256()
    for identifier, content in sorted(originals.items()):
        digest.update(identifier.encode("utf-8") + b"\0" + content + b"\0")
    return digest.hexdigest()


def _apply_transaction(
    card_path: Path,
    targets: dict[str, tuple[Path, Path]],
    *,
    require_source_hash=None,
):
    card = card_path.read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    if not front or not re.search(r"^status: [\"]?przyjęta[\"]?$", front[1], re.MULTILINE):
        raise ValueError("Automat wdraża wyłącznie decyzje o statusie przyjęta")
    if "<!-- applied-source-sha256:" in card:
        raise ValueError("Ta karta ma już zapis wdrożenia; przygotuj nową decyzję")
    fragments = read_document_fragments(card)
    if set(targets) == {"legacy"} and len(fragments) == 1:
        fragments = {"legacy": next(iter(fragments.values()))}
    if set(fragments) == {"legacy"} and set(targets) == {"reprezentacja"}:
        fragments = {"reprezentacja": fragments["legacy"]}
    if set(fragments) != set(targets):
        raise ValueError("Fragmenty karty nie odpowiadają wskazanym dokumentom")
    paths = [path for pair in targets.values() for path in pair] + [card_path]
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Źródła, DOCX i karta muszą być osobnymi plikami")
    originals = {identifier: source.read_bytes() for identifier, (source, _) in targets.items()}
    digest = _source_digest(originals)
    if require_source_hash is not None and digest != require_source_hash:
        raise ValueError("Źródło zmieniło się od przygotowania decyzji")
    changed = {
        identifier: replace_exact(originals[identifier].decode("utf-8"), *fragments[identifier])
        for identifier in targets
    }
    with tempfile.TemporaryDirectory() as directory:
        staging = Path(directory)
        prepared = {}
        for identifier, (source, output) in targets.items():
            target = staging / identifier
            target.mkdir()
            staged_source = target / source.name
            staged_output = target / output.name
            staged_source.write_text(changed[identifier], encoding="utf-8")
            normalize_and_build(staged_source, staged_output)
            verify(staged_source, staged_output)
            prepared[identifier] = (staged_source.read_bytes(), staged_output.read_bytes())
        updated_card = card.replace(
            "Oczekuje na etykietę `wdrażaj` na PR.",
            "Wdrożono automatycznie; DOCX do kontroli znajduje się w opisie PR.",
        )
        updated_card = updated_card.rstrip() + f"\n\n<!-- applied-source-sha256:{digest} -->\n"
        contents = {
            path: content
            for identifier, pair in targets.items()
            for path, content in zip(pair, prepared[identifier])
        }
        contents[card_path] = updated_card.encode("utf-8")
        backups = {path: path.read_bytes() if path.exists() else None for path in paths}
        try:
            for path, content in contents.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        except BaseException:
            for path, content in backups.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)
            raise


def apply_decision(card_path, source, output, *, require_source_hash=None):
    _apply_transaction(
        card_path,
        {"legacy": (source, output)},
        require_source_hash=require_source_hash,
    )


def apply_registered_decision(card_path: Path, root: Path):
    root = root.resolve()
    card_is_symlink = card_path.is_symlink()
    card_path = card_path.resolve()
    if not card_path.is_relative_to(root) or card_is_symlink:
        raise ValueError("Karta decyzji musi być zwykłym plikiem w repozytorium")
    card = card_path.read_text(encoding="utf-8")
    targets = registered_paths(card, root)
    for source, output in targets.values():
        if any(
            path.is_symlink() or not path.resolve().is_relative_to(root)
            for path in (source, output)
        ):
            raise ValueError("Pliki regulaminów muszą być zwykłymi plikami w repozytorium")
    _apply_transaction(card_path, targets)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path)
    parser.add_argument("source", type=Path, nargs="?")
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--registered-root", type=Path)
    args = parser.parse_args()
    if args.registered_root is not None:
        if args.source is not None or args.output is not None:
            parser.error("--registered-root nie łączy się ze ścieżkami source/output")
        apply_registered_decision(args.decision, args.registered_root)
    elif args.source is None or args.output is None:
        parser.error("podaj source i output albo --registered-root")
    else:
        apply_decision(args.decision, args.source, args.output)


if __name__ == "__main__":
    main()
