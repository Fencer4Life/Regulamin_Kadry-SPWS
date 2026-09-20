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


def _discussion_field(body: str, label: str) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=^###\s|\Z)"
    match = re.search(pattern, body, flags=re.MULTILINE | re.DOTALL)
    value = match.group(1).strip() if match else ""
    return "" if value in {"", "_No response_"} else value


def parse_discussion_form(body: str) -> dict[str, str]:
    zalezy_od = _discussion_field(body, "Zależy od") or _discussion_field(body, "Powiązane decyzje")
    return {
        "koordynator": _discussion_field(body, "Koordynator dyskusji"),
        "problem": _discussion_field(body, "Problem"),
        "priorytet": _discussion_field(body, "Priorytet"),
        "obszar": _discussion_field(body, "Obszar"),
        "propozycja": _discussion_field(body, "Proponowane rozwiązanie"),
        "fragment_markdown": _discussion_field(body, "Fragment Markdown do zastąpienia"),
        "nowe_brzmienie_markdown": _discussion_field(body, "Nowe brzmienie Markdown"),
        "alternatywy": _discussion_field(body, "Inne rozważane podejścia"),
        "materialy": _discussion_field(body, "Materiały lub przykłady"),
        "powiazane": zalezy_od,
        "zalezy_od": zalezy_od,
    }


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
    body = discussion.get("body") or ""
    source = parse_discussion_form(body)
    result = "przyjęta"
    effect = "obowiązuje"
    decision = source["propozycja"] or "> _Do uzupełnienia przez osobę przygotowującą decyzję._"
    rationale = "> _Do uzupełnienia przez osobę przygotowującą decyzję._"
    rejected = source["alternatywy"] or "Brak zgłoszonych alternatyw."
    context = "\n\n".join(part for part in (
        f"**Priorytet:** {source['priorytet']}" if source["priorytet"] else "",
        f"**Obszar:** {source['obszar']}" if source["obszar"] else "",
        f"**Materiały lub przykłady:** {source['materialy']}" if source["materialy"] else "",
        f"**Powiązane decyzje:** {source['powiazane']}" if source["powiazane"] else "",
    )) or "Do uzupełnienia na podstawie dyskusji."
    coordinator = source["koordynator"] or f"@{author}"
    people = coordinator
    problem = source["problem"] or "Do uzupełnienia na podstawie dyskusji."
    area = source["obszar"] or "do uzupełnienia"
    content = f'''---
id: {decision_id}
tytul: "{title.replace(chr(34), chr(39))}"
typ: merytoryczna
status: {result}
stan_obowiązywania: {effect}
data_inicjacji: {date}
data_decyzji: "{date}"
sezon: 2026/2027
dotyczy: {area}
decydenci: Komisja regulaminowa SPWS
discussion_url: {url}
pr_url: ""
zmienia: []
zmieniona_przez: []
zakres_zmiany: {{}}
zastepuje: []
zastapiona_przez: []
termin_oceny: po zakończeniu sezonu 2026/2027
---

## Problem

{problem}

## Kontekst

{context}

## Dyskusja

Zobacz dyskusję źródłową: [{url}]({url}).

**Koordynator dyskusji:** {coordinator}

**Uczestnicy:** {people}

## Rozważane warianty

{rejected}

## Decyzja

{decision}

## Uzasadnienie

{rationale}

## Konsekwencje

### Czy decyzja wymaga zmiany Regulaminu?

- [ ] **Tak** — należy przygotować zmianę Regulaminu i dołączyć ją do tego samego pull requestu.
- [ ] **Nie** — decyzja nie wymaga zmiany Regulaminu.

## Odrzucone alternatywy

{rejected}

## Plan oceny

Po zakończeniu sezonu 2026/2027.

## Ocena po sezonie

Nie dotyczy przed przyjęciem decyzji.

## Historia zmian

- {date} — robocza karta utworzona automatycznie po oznaczeniu dyskusji jako `rozstrzygnięta`.
'''
    # Import here to avoid coupling the form parser to document generation at import time.
    from narzedzia.decision_patch import format_fragments
    content = content.replace("## Uzasadnienie\n", format_fragments(
        source["fragment_markdown"], source["nowe_brzmienie_markdown"]
    ) + "\n## Uzasadnienie\n", 1)
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    print(create(Path(sys.argv[1]), Path(sys.argv[2])))
