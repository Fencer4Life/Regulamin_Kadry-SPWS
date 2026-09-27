from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

FORM_LABELS = (
    "Koordynator dyskusji",
    "Problem",
    "Dokument",
    "Wynik decyzji",
    "Priorytet",
    "Obszar",
    "Proponowane rozwiązanie",
    "Uzasadnienie",
    "Fragment Markdown do zastąpienia",
    "Nowe brzmienie Markdown",
    "Wpływ na drugi regulamin",
    "Fragment Regulaminu Reprezentacji do zastąpienia",
    "Nowe brzmienie Regulaminu Reprezentacji",
    "Fragment Regulaminu Zawodów do zastąpienia",
    "Nowe brzmienie Regulaminu Zawodów",
    "Spójność obu regulaminów",
    "Inne rozważane podejścia",
    "Materiały lub przykłady",
    "Zależy od",
    "Powiązane decyzje",
)

DOCUMENT_SCOPE = {
    "Regulamin Reprezentacji": ("reprezentacja",),
    "Regulamin Zawodów": ("zawody",),
    "Bez zmiany dokumentu": (),
}
DECISION_RESULTS = {
    "Przyjęta": "przyjęta",
    "Odrzucona": "odrzucona",
    "Do rozstrzygnięcia": "do rozstrzygnięcia",
}


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


def parse_discussion_form(body: str, *, strict=True) -> dict[str, object]:
    zalezy_od = _discussion_field(body, "Zależy od", strict=strict) or _discussion_field(
        body, "Powiązane decyzje", strict=strict
    )
    generic_old = _discussion_fragment(body, "Fragment Markdown do zastąpienia", strict=strict)
    generic_new = _discussion_fragment(body, "Nowe brzmienie Markdown", strict=strict)
    shared_changes = {
        "reprezentacja": {
            "stary": _discussion_fragment(
                body, "Fragment Regulaminu Reprezentacji do zastąpienia", strict=strict
            ),
            "nowy": _discussion_fragment(
                body, "Nowe brzmienie Regulaminu Reprezentacji", strict=strict
            ),
        },
        "zawody": {
            "stary": _discussion_fragment(
                body, "Fragment Regulaminu Zawodów do zastąpienia", strict=strict
            ),
            "nowy": _discussion_fragment(body, "Nowe brzmienie Regulaminu Zawodów", strict=strict),
        },
    }
    is_shared = any(value for change in shared_changes.values() for value in change.values())
    document_value = _discussion_field(body, "Dokument", strict=strict)
    if is_shared:
        if document_value:
            raise ValueError("Wspólna zmiana nie może wskazywać pojedynczego dokumentu")
        documents = ("reprezentacja", "zawody")
        changes = shared_changes
    else:
        if document_value and document_value not in DOCUMENT_SCOPE:
            raise ValueError(f"Nieznany zakres dokumentu: {document_value}")
        documents = DOCUMENT_SCOPE.get(document_value, ("reprezentacja",))
        changes = {documents[0]: {"stary": generic_old, "nowy": generic_new}} if documents else {}
    result_value = _discussion_field(body, "Wynik decyzji", strict=strict)
    if result_value and result_value not in DECISION_RESULTS:
        raise ValueError(f"Nieznany wynik decyzji: {result_value}")

    return {
        "legacy": not document_value and not result_value and not is_shared,
        "koordynator": _discussion_field(body, "Koordynator dyskusji", strict=strict),
        "problem": _discussion_field(body, "Problem", strict=strict),
        "dokumenty": documents,
        "wynik": DECISION_RESULTS.get(result_value, "przyjęta"),
        "priorytet": _discussion_field(body, "Priorytet", strict=strict),
        "obszar": _discussion_field(body, "Obszar", strict=strict),
        "uzasadnienie": _discussion_field(body, "Uzasadnienie", strict=strict),
        "propozycja": _discussion_field(body, "Proponowane rozwiązanie", strict=strict),
        "fragment_markdown": generic_old,
        "nowe_brzmienie_markdown": generic_new,
        "zmiany": changes,
        "wplyw_na_drugi": _discussion_field(body, "Wpływ na drugi regulamin", strict=strict),
        "spojnosc": _discussion_field(body, "Spójność obu regulaminów", strict=strict),
        "alternatywy": _discussion_field(body, "Inne rozważane podejścia", strict=strict),
        "materialy": _discussion_field(body, "Materiały lub przykłady", strict=strict),
        "powiazane": zalezy_od,
        "zalezy_od": zalezy_od,
    }


def _discussion_fragment(body: str, label: str, *, strict=True) -> str:
    # Source section headings are content, not form boundaries. Preserve ZTP indentation.
    boundary = "|".join(re.escape(item) for item in FORM_LABELS)
    pattern = rf"^### {re.escape(label)}[ \t]*\r?\n(.*?)(?=^### (?:{boundary})[ \t]*\r?$|\Z)"
    matches = list(re.finditer(pattern, body, re.MULTILINE | re.DOTALL))
    if strict and len(matches) > 1:
        raise ValueError(f"Powtórzone pole dyskusji: {label}")
    match = matches[0] if matches else None
    value = match.group(1).strip("\r\n") if match else ""
    return "" if value.strip() in {"", "_No response_"} else value


def render_card(discussion: dict, decision_id: str, pr_url: str = "") -> str:
    """An exact snapshot of structured discussion fields, never a guessed summary."""
    from narzedzia.decision_patch import format_document_fragments

    source = parse_discussion_form(discussion.get("body") or "")
    if "<!-- applied-source-sha256:" in (discussion.get("body") or ""):
        raise ValueError(
            "Znacznik wdrożenia jest zastrzeżony dla automatu; usuń go z opisu dyskusji"
        )
    if not source["uzasadnienie"]:
        raise ValueError(
            "Uzupełnij pole „Uzasadnienie” w opisie dyskusji; nie w karcie ani komentarzu"
        )
    if source["wynik"] == "do rozstrzygnięcia":
        raise ValueError("Przed utworzeniem karty wybierz wynik decyzji: Przyjęta albo Odrzucona")

    documents = source["dokumenty"]
    changes = source["zmiany"]
    proposed_change = False
    for identifier, change in changes.items():
        old, new = change["stary"], change["nowy"]
        if bool(old.strip()) != bool(new.strip()):
            raise ValueError(f"Uzupełnij oba fragmenty Markdown dla dokumentu: {identifier}")
        if old and old == new:
            raise ValueError(f"Nowe brzmienie dokumentu {identifier} musi różnić się od starego")
        proposed_change = proposed_change or bool(old)
    if not documents and (source["fragment_markdown"] or source["nowe_brzmienie_markdown"]):
        raise ValueError("Decyzja bez zmiany dokumentu nie może zawierać fragmentów Markdown")
    if len(documents) == 2:
        if not all(change["stary"] and change["nowy"] for change in changes.values()):
            raise ValueError("Wspólna zmiana wymaga dwóch kompletnych par fragmentów Markdown")
        if not source["spojnosc"]:
            raise ValueError("Uzupełnij pole „Spójność obu regulaminów”")
    elif documents and not source["legacy"] and not source["wplyw_na_drugi"]:
        raise ValueError("Uzupełnij pole „Wpływ na drugi regulamin”")
    if documents and not source["legacy"] and source["wynik"] == "przyjęta" and not proposed_change:
        raise ValueError("Przyjęta zmiana dokumentu wymaga kompletnej pary fragmentów Markdown")
    if not proposed_change and not source["propozycja"]:
        raise ValueError(
            "Decyzja bez zmiany dokumentu wymaga pola „Proponowane rozwiązanie” w dyskusji"
        )

    def clean(value):
        return "\n".join(line.rstrip() for line in value.splitlines()).strip()

    date = discussion["created_at"][:10]
    metadata = {
        "schema_version": 3,
        "id": decision_id,
        "tytul": discussion["title"],
        "typ": "merytoryczna",
        "status": source["wynik"],
        "stan_obowiązywania": ("obowiązuje" if source["wynik"] == "przyjęta" else "nie dotyczy"),
        "data_inicjacji": date,
        "data_decyzji": date,
        "sezon": "2026/2027",
        "dotyczy": source["obszar"] or "nie określono",
        "decydenci": "Komisja regulaminowa SPWS",
        "discussion_url": discussion["html_url"],
        "pr_url": pr_url,
        "dokumenty": list(documents),
        "zmiana_regulaminu": source["wynik"] == "przyjęta" and proposed_change,
        "proponowana_zmiana": proposed_change,
        "powiazane": source["powiazane"],
        "zmienia": [],
        "zmieniona_przez": [],
        "zakres_zmiany": {},
        "zastepuje": [],
        "zastapiona_przez": [],
        "termin_oceny": "po zakończeniu sezonu 2026/2027",
    }
    # Quote data, not YAML structure. Discussion text cannot inject metadata.
    unquoted = {"typ", "status", "stan_obowiązywania", "discussion_url", "pr_url"}
    front = "\n".join(
        f"{key}: " + (value if key in unquoted and value else json.dumps(value, ensure_ascii=False))
        for key, value in metadata.items()
    )
    resolution = (
        source["propozycja"]
        or "Zastąpić wskazany fragment Markdown dokładnie podanym nowym brzmieniem."
    )
    fragments = "\n".join(
        format_document_fragments(identifier, change["stary"], change["nowy"])
        for identifier, change in changes.items()
        if change["stary"]
    )
    coherence = source["spojnosc"] or source["wplyw_na_drugi"] or "Nie dotyczy."
    deployment = (
        "Oczekuje na etykietę `wdrażaj` na PR."
        if metadata["zmiana_regulaminu"]
        else (
            "Decyzja odrzucona; automat nie zmienia Markdown ani DOCX."
            if source["wynik"] == "odrzucona"
            else "Bez zmiany dokumentu; nie nadawaj etykiety `wdrażaj`."
        )
    )
    return (
        f"---\n{front}\n---\n\n"
        "Karta automatyczna. Dane poprawiaj wyłącznie w dyskusji źródłowej.\n\n"
        f"## Decyzja\n\n{clean(resolution)}\n\n"
        f"## Uzasadnienie\n\n{clean(source['uzasadnienie'])}\n\n"
        f"## Wpływ na spójność dokumentów\n\n{clean(coherence)}\n\n"
        f"{fragments}"
        f"## Dyskusja\n\n{discussion['html_url']}\n\n"
        + (f"Powiązania: {clean(source['powiazane'])}\n\n" if source["powiazane"] else "")
        + "## Wdrożenie\n\n"
        + deployment
        + "\n"
    )


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
