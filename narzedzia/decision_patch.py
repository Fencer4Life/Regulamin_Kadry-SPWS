"""Apply an accepted decision literally, without inference or a language model."""

import argparse
import hashlib
import re
import tempfile
from pathlib import Path

from narzedzia.markdown_preview import preview_path
from narzedzia.prepare_regulamin import normalize_and_build, verify


OLD = "Stary fragment Markdown"
NEW = "Nowy fragment Markdown"


def format_fragments(old="", new=""):
    longest = max((len(x) for x in re.findall(r"`+", old + new)), default=0)
    fence = "`" * max(3, longest + 1)
    return (f"## {OLD}\n\nWklej dokładny fragment kanonicznego .md, ze znacznikami i wcięciami.\n\n"
            f"{fence}markdown\n{old}\n{fence}\n\n"
            f"## {NEW}\n\nWklej kompletną treść zastępującą stary fragment; zachowaj identyfikatory jednostek.\n\n"
            f"{fence}markdown\n{new}\n{fence}\n")


def read_fragments(card):
    result = {}
    heading = None
    fence = None
    buffer = []
    # Track all fences, so headings copied from source are not decision sections.
    for line in card.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        if fence is not None:
            if raw == fence:
                if heading in {OLD, NEW}:
                    if heading in result:
                        raise ValueError("Pole zmiany zawiera więcej niż jeden blok kodu")
                    result[heading] = "".join(buffer).removesuffix("\n")
                fence, buffer = None, []
            else:
                buffer.append(line)
        elif match := re.fullmatch(r"(`{3,})([a-zA-Z0-9_-]*)", raw):
            if heading in {OLD, NEW} and match.group(2) not in {"markdown", "md", ""}:
                raise ValueError("Fragment zmiany musi być blokiem kodu Markdown")
            fence = match.group(1)
        elif raw.startswith("## "):
            heading = raw[3:]
    if fence is not None or any(not result.get(key, "").strip() for key in (OLD, NEW)):
        raise ValueError("Wypełnij oba pola: Stary fragment Markdown i Nowy fragment Markdown")
    return result[OLD], result[NEW]


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
    if not front or not re.search(r'^status: [\"]?przyjęta[\"]?$', front[1], re.MULTILINE):
        raise ValueError("Automat wdraża wyłącznie decyzje o statusie przyjęta")
    if "<!-- applied-source-sha256:" in card:
        raise ValueError("Ta karta ma już zapis wdrożenia; przygotuj nową decyzję")
    original = source.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if require_source_hash is not None and digest != require_source_hash:
        raise ValueError("Źródło zmieniło się od przygotowania decyzji")
    old, new = read_fragments(card)
    changed = replace_exact(original.decode("utf-8"), old, new)
    paths = (source, output, preview_path(source), card_path)
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Źródło, DOCX, podgląd i karta muszą być osobnymi plikami")
    with tempfile.TemporaryDirectory() as directory:
        staged_source = Path(directory) / source.name
        staged_output = Path(directory) / output.name
        staged_source.write_text(changed, encoding="utf-8")
        normalize_and_build(staged_source, staged_output)
        verify(staged_source, staged_output)
        updated_card = card.rstrip() + f"\n\n<!-- applied-source-sha256:{digest} -->\n"
        contents = (staged_source.read_bytes(), staged_output.read_bytes(),
                    preview_path(staged_source).read_bytes(), updated_card.encode("utf-8"))
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
