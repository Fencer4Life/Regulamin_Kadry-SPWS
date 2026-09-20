from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

from narzedzia.create_decision_from_discussion import create, parse_discussion_form
from narzedzia.decision_patch import replace_exact


EMPTY_FORM_VALUES = {"", "_No response_"}
PLACEHOLDER = "> _Do uzupełnienia przez osobę przygotowującą decyzję._"


def apply_editorial_change(
    event_path: Path, decisions_dir: Path, source_path: Path
) -> tuple[Path, Path]:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    body = event["discussion"].get("body") or ""
    fields = parse_discussion_form(body)
    current = fields["fragment_markdown"]
    replacement = fields["nowe_brzmienie_markdown"]

    if current in EMPTY_FORM_VALUES:
        raise ValueError("Pole „Fragment Markdown do zastąpienia” jest wymagane")
    if replacement in EMPTY_FORM_VALUES:
        raise ValueError("Pole „Nowe brzmienie Markdown” jest wymagane")
    if current == replacement:
        raise ValueError("Nowe brzmienie musi różnić się od zastępowanego fragmentu")

    original = source_path.read_text(encoding="utf-8")
    changed = replace_exact(original, current, replacement)
    occurrences = original.count(current)
    if occurrences != 1:
        raise ValueError(
            "Fragment Markdown do zastąpienia musi występować dokładnie raz "
            f"(znaleziono: {occurrences})"
        )

    card_path = create(event_path, decisions_dir)
    try:
        card = card_path.read_text(encoding="utf-8")
        card = card.replace("typ: merytoryczna", "typ: redakcyjna", 1)
        if fields["propozycja"] in EMPTY_FORM_VALUES:
            empty_decision = fields["propozycja"] or PLACEHOLDER
            card = card.replace(
                f"## Decyzja\n\n{empty_decision}",
                "## Decyzja\n\nZastąpić wskazany fragment Markdown dokładnie podanym "
                "nowym brzmieniem.",
                1,
            )
        card = card.replace(
            f"## Uzasadnienie\n\n{PLACEHOLDER}",
            "## Uzasadnienie\n\nKorekta redakcyjna bez zmiany sensu; dokładne "
            "stare i nowe brzmienie zapisano w dyskusji źródłowej.",
            1,
        )
        card = card.replace("- [ ] **Tak**", "- [x] **Tak**", 1)
        card = card.replace(
            "po oznaczeniu dyskusji jako `rozstrzygnięta`",
            "po oznaczeniu dyskusji jako `redakcja-bez-zmiany-sensu`",
            1,
        )
        card += f"\n<!-- applied-source-sha256:{hashlib.sha256(original.encode('utf-8')).hexdigest()} -->\n"
        source_path.write_text(changed, encoding="utf-8")
        card_path.write_text(card, encoding="utf-8")
    except Exception:
        card_path.unlink(missing_ok=True)
        source_path.write_text(original, encoding="utf-8")
        raise

    return card_path, source_path


def main() -> None:
    card_path, source_path = apply_editorial_change(
        Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    )
    print(card_path)
    print(source_path)


if __name__ == "__main__":
    main()
