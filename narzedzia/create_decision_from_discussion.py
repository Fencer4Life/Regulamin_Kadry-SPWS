from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


def next_decision_id(names: list[str]) -> str:
    numbers = [int(match.group(1)) for name in names if (match := re.match(r"DR-(\d{3})", name))]
    return f"DR-{max(numbers, default=0) + 1:03d}"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:70] or "decyzja"


def create(event_path: Path, decisions_dir: Path) -> Path:
    discussion = json.loads(event_path.read_text(encoding="utf-8"))["discussion"]
    url = discussion["html_url"]
    if any(url in path.read_text(encoding="utf-8") for path in decisions_dir.glob("DR-*.md")):
        raise SystemExit("Ta dyskusja ma już kartę decyzji")
    decision_id = next_decision_id([path.name for path in decisions_dir.glob("DR-*.md")])
    title = discussion["title"]
    path = decisions_dir / f"{decision_id}-{slugify(title)}.md"
    date = discussion["created_at"][:10]
    author = (discussion.get("user") or {}).get("login", "autor dyskusji")
    body = discussion.get("body") or "Do uzupełnienia na podstawie dyskusji."
    content = f'''---
id: {decision_id}
tytul: "{title.replace(chr(34), chr(39))}"
typ: merytoryczna
status: do zatwierdzenia
stan_obowiązywania: nie dotyczy
data_inicjacji: {date}
data_decyzji: ""
sezon: 2026/2027
dotyczy: do uzupełnienia
decydenci: Komisja regulaminowa SPWS
discussion_url: {url}
pr_url: ""
zmienia: []
zmieniona_przez: []
zakres_zmiany: {{}}
zastepuje: []
zastapiona_przez: []
termin_oceny: do uzupełnienia
---

## Problem

{body}

## Kontekst

Do uzupełnienia na podstawie dyskusji prowadzonej przez {author}.

## Dyskusja

Zobacz dyskusję źródłową: [{url}]({url}).

## Rozważane warianty

Do uzupełnienia.

## Decyzja

Do zatwierdzenia.

## Uzasadnienie

Do uzupełnienia.

## Konsekwencje

Do uzupełnienia.

## Odrzucone alternatywy

Do uzupełnienia.

## Plan oceny

Do uzupełnienia.

## Ocena po sezonie

Nie dotyczy przed przyjęciem decyzji.

## Historia zmian

- {date} — karta utworzona z GitHub Discussion.
'''
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    print(create(Path(sys.argv[1]), Path(sys.argv[2])))
