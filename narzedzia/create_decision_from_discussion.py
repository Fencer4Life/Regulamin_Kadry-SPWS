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


def _discussion_field(body: str, label: str, *, strict=True) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=^###\s|\Z)"
    matches = list(re.finditer(pattern, body, flags=re.MULTILINE | re.DOTALL))
    if strict and len(matches) > 1:
        raise ValueError(f"Powtórzone pole dyskusji: {label}")
    match = matches[0] if matches else None
    value = match.group(1).strip() if match else ""
    return "" if value in {"", "_No response_"} else value


def parse_discussion_form(body: str, *, strict=True) -> dict[str, str]:
    zalezy_od = _discussion_field(body, "Zależy od", strict=strict) or _discussion_field(body, "Powiązane decyzje", strict=strict)
    return {
        "koordynator": _discussion_field(body, "Koordynator dyskusji", strict=strict),
        "problem": _discussion_field(body, "Problem", strict=strict),
        "priorytet": _discussion_field(body, "Priorytet", strict=strict),
        "obszar": _discussion_field(body, "Obszar", strict=strict),
        "uzasadnienie": _discussion_field(body, "Uzasadnienie", strict=strict),
        "propozycja": _discussion_field(body, "Proponowane rozwiązanie", strict=strict),
        "fragment_markdown": _discussion_fragment(body, "Fragment Markdown do zastąpienia", strict=strict),
        "nowe_brzmienie_markdown": _discussion_fragment(body, "Nowe brzmienie Markdown", strict=strict),
        "alternatywy": _discussion_field(body, "Inne rozważane podejścia", strict=strict),
        "materialy": _discussion_field(body, "Materiały lub przykłady", strict=strict),
        "powiazane": zalezy_od,
        "zalezy_od": zalezy_od,
    }


def _discussion_fragment(body: str, label: str, *, strict=True) -> str:
    # Source section headings are content, not form boundaries. Preserve ZTP indentation.
    labels = ('Koordynator dyskusji', 'Problem', 'Priorytet', 'Obszar',
              'Proponowane rozwiązanie', 'Uzasadnienie', 'Fragment Markdown do zastąpienia',
              'Nowe brzmienie Markdown', 'Inne rozważane podejścia',
              'Materiały lub przykłady', 'Zależy od', 'Powiązane decyzje')
    boundary = '|'.join(re.escape(item) for item in labels)
    pattern = rf'^### {re.escape(label)}[ \t]*\r?\n(.*?)(?=^### (?:{boundary})[ \t]*\r?$|\Z)'
    matches = list(re.finditer(pattern, body, re.MULTILINE | re.DOTALL))
    if strict and len(matches) > 1:
        raise ValueError(f"Powtórzone pole dyskusji: {label}")
    match = matches[0] if matches else None
    value = match.group(1).strip('\r\n') if match else ''
    return '' if value.strip() in {'', '_No response_'} else value


def render_card(discussion: dict, decision_id: str, pr_url: str = "") -> str:
    """An exact snapshot of structured discussion fields, never a guessed summary."""
    from narzedzia.decision_patch import format_fragments
    source = parse_discussion_form(discussion.get("body") or "")
    if '<!-- applied-source-sha256:' in (discussion.get('body') or ''):
        raise ValueError('Znacznik wdrożenia jest zastrzeżony dla automatu; usuń go z opisu dyskusji')
    old, new = source["fragment_markdown"], source["nowe_brzmienie_markdown"]
    if not source["uzasadnienie"]:
        raise ValueError("Uzupełnij pole „Uzasadnienie” w opisie dyskusji; nie w karcie ani komentarzu")
    if bool(old.strip()) != bool(new.strip()):
        raise ValueError("Uzupełnij oba pola w dyskusji: Fragment Markdown do zastąpienia i Nowe brzmienie Markdown")
    if old and old == new:
        raise ValueError("Nowe brzmienie musi różnić się od zastępowanego fragmentu")
    if not old and not source["propozycja"]:
        raise ValueError("Decyzja bez zmiany dokumentu wymaga pola „Proponowane rozwiązanie” w dyskusji")
    def clean(value):
        return "\n".join(line.rstrip() for line in value.splitlines()).strip()
    date = discussion["created_at"][:10]
    metadata = {
        "schema_version": 2, "id": decision_id, "tytul": discussion["title"],
        "typ": "merytoryczna", "status": "przyjęta", "stan_obowiązywania": "obowiązuje",
        "data_inicjacji": date, "data_decyzji": date, "sezon": "2026/2027",
        "dotyczy": source["obszar"] or "nie określono", "decydenci": "Komisja regulaminowa SPWS",
        "discussion_url": discussion["html_url"], "pr_url": pr_url,
        "zmiana_regulaminu": bool(old), "powiazane": source["powiazane"],
        "zmienia": [], "zmieniona_przez": [], "zakres_zmiany": {},
        "zastepuje": [], "zastapiona_przez": [], "termin_oceny": "po zakończeniu sezonu 2026/2027",
    }
    # Quote data, not YAML structure. Discussion text cannot inject metadata.
    unquoted = {"typ", "status", "stan_obowiązywania", "discussion_url", "pr_url"}
    front = "\n".join(f"{key}: " + (value if key in unquoted and value else json.dumps(value, ensure_ascii=False))
                      for key, value in metadata.items())
    resolution = (source["propozycja"] or
                  "Zastąpić wskazany fragment Markdown dokładnie podanym nowym brzmieniem.")
    fragments = format_fragments(old, new, instructions=False) if old else ""
    return (f"---\n{front}\n---\n\n"
            "Karta automatyczna. Dane poprawiaj wyłącznie w dyskusji źródłowej.\n\n"
            f"## Decyzja\n\n{clean(resolution)}\n\n"
            f"## Uzasadnienie\n\n{clean(source['uzasadnienie'])}\n\n"
            f"{fragments}\n"
            f"## Dyskusja\n\n{discussion['html_url']}\n\n"
            + (f"Powiązania: {clean(source['powiazane'])}\n\n" if source["powiazane"] else "")
            + "## Wdrożenie\n\n"
            + ("Oczekuje na etykietę `wdrażaj` na PR.\n" if old
               else "Bez zmiany dokumentu; nie nadawaj etykiety `wdrażaj`.\n"))


def create(event_path: Path, decisions_dir: Path) -> Path:
    discussion = json.loads(event_path.read_text(encoding="utf-8"))["discussion"]
    url = discussion["html_url"]
    if any(url in path.read_text(encoding="utf-8") for path in decisions_dir.glob("DR-*.md")):
        raise SystemExit("Ta dyskusja ma już kartę decyzji")
    decision_id = next_decision_id([path.name for path in decisions_dir.glob("DR-*.md")])
    content = render_card(discussion, decision_id)
    path = decisions_dir / f"{decision_id}-{slugify(discussion['title'])}.md"
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    print(create(Path(sys.argv[1]), Path(sys.argv[2])))
