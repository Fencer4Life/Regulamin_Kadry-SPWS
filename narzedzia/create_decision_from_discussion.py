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


def _field(body: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.*?)(?=\n\s*\*\*[^\n]+:\*\*|\n\s*###?\s|\n\s*- \[[ xX]\]|\Z)"
    match = re.search(pattern, body, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _discussion_field(body: str, label: str) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=^###\s|\Z)"
    match = re.search(pattern, body, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_discussion_form(body: str) -> dict[str, str]:
    return {
        "koordynator": _discussion_field(body, "Koordynator dyskusji"),
        "problem": _discussion_field(body, "Problem"),
        "priorytet": _discussion_field(body, "Priorytet"),
        "obszar": _discussion_field(body, "Obszar"),
        "propozycja": _discussion_field(body, "Proponowane rozwiązanie"),
        "alternatywy": _discussion_field(body, "Inne rozważane podejścia"),
        "materialy": _discussion_field(body, "Materiały lub przykłady"),
        "powiazane": _discussion_field(body, "Powiązane decyzje"),
    }


def parse_resolution(body: str) -> dict[str, str | bool]:
    if "FORMULARZ-ROZSTRZYGNIECIA" not in body:
        raise ValueError("Brak formularza rozstrzygnięcia")
    fields = {
        "wynik": _field(body, "Wynik").lower(),
        "decyzja": _field(body, "Treść decyzji"),
        "uzasadnienie": _field(body, "Uzasadnienie"),
        "zmiana_regulaminu": _field(body, "Zmiana regulaminu").lower(),
        "odrzucone": _field(body, "Odrzucone alternatywy"),
    }
    required = {
        "Wynik": fields["wynik"] if fields["wynik"] in {"przyjęta", "odrzucona"} else "",
        "Treść decyzji": fields["decyzja"],
        "Uzasadnienie": fields["uzasadnienie"],
        "Zmiana regulaminu": fields["zmiana_regulaminu"] if fields["zmiana_regulaminu"] in {"tak", "nie"} else "",
    }
    missing = [label for label, value in required.items() if not value]
    confirmed = bool(re.search(r"- \[[xX]\]\s+Potwierdzam zgodność", body))
    if not confirmed:
        missing.append("potwierdzenie zgodności ze stanowiskiem komisji")
    if missing:
        raise ValueError("Brak wymaganych pól: " + ", ".join(missing))
    fields["potwierdzenie"] = confirmed
    return fields


def resolution_from_comments(path: Path) -> tuple[dict[str, str | bool], str, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    nodes = payload.get("data", {}).get("repository", {}).get("discussion", {}).get("comments", {}).get("nodes", [])
    candidates = [comment for comment in nodes if "FORMULARZ-ROZSTRZYGNIECIA" in (comment.get("body") or "")]
    if not candidates:
        raise ValueError("Nie znaleziono formularza rozstrzygnięcia w komentarzach")
    comment = candidates[-1]
    participants = sorted({f"@{node['author']['login']}" for node in nodes if node.get("author") and node["author"].get("login")})
    return parse_resolution(comment["body"]), comment["createdAt"][:10], participants


def create(event_path: Path, decisions_dir: Path, comments_path: Path | None = None) -> Path:
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
    resolution, decision_date, participants = resolution_from_comments(comments_path) if comments_path else ({}, "", [])
    result = str(resolution.get("wynik", "do zatwierdzenia"))
    effect = "obowiązuje" if result == "przyjęta" else "nie dotyczy"
    decision = str(resolution.get("decyzja", "Do zatwierdzenia."))
    rationale = str(resolution.get("uzasadnienie") or "Do uzupełnienia.")
    variants = "\n\n".join(part for part in (
        f"**Proponowane rozwiązanie:** {source['propozycja']}" if source["propozycja"] else "",
        f"**Inne rozważane podejścia:** {source['alternatywy']}" if source["alternatywy"] else "",
    )) or "Do uzupełnienia."
    rejected = str(resolution.get("odrzucone") or "Do uzupełnienia.")
    context = "\n\n".join(part for part in (
        f"**Priorytet:** {source['priorytet']}" if source["priorytet"] else "",
        f"**Obszar:** {source['obszar']}" if source["obszar"] else "",
        f"**Materiały lub przykłady:** {source['materialy']}" if source["materialy"] else "",
        f"**Powiązane decyzje:** {source['powiazane']}" if source["powiazane"] else "",
    )) or "Do uzupełnienia na podstawie dyskusji."
    coordinator = source["koordynator"] or f"@{author}"
    people = ", ".join(sorted(set(participants + [coordinator])))
    problem = source["problem"] or "Do uzupełnienia na podstawie dyskusji."
    area = source["obszar"] or "do uzupełnienia"
    content = f'''---
id: {decision_id}
tytul: "{title.replace(chr(34), chr(39))}"
typ: merytoryczna
status: {result}
stan_obowiązywania: {effect}
data_inicjacji: {date}
data_decyzji: "{decision_date}"
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

{variants}

## Decyzja

{decision}

## Uzasadnienie

{rationale}

## Konsekwencje

Zmiana regulaminu: {resolution.get("zmiana_regulaminu", "do uzupełnienia")}.

## Odrzucone alternatywy

{rejected}

## Plan oceny

Po zakończeniu sezonu 2026/2027.

## Ocena po sezonie

Nie dotyczy przed przyjęciem decyzji.

## Historia zmian

- {date} — karta utworzona z GitHub Discussion na podstawie formularza rozstrzygnięcia.
'''
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    comments = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    print(create(Path(sys.argv[1]), Path(sys.argv[2]), comments))
