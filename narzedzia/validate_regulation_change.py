from __future__ import annotations

import subprocess
import sys
import re
from pathlib import Path


SOURCE = (
    "regulamin/"
    "Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md"
)
DOCX = (
    "regulamin/"
    "Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx"
)


def validate_changes(changes: dict[str, str]) -> None:
    if SOURCE not in changes:
        return
    missing: list[str] = []
    if DOCX not in changes:
        missing.append("wygenerowanego DOCX")
    initial_migration = changes[SOURCE] == "A"
    if not initial_migration and not any(
        path.startswith("_decyzje/DR-") and path.endswith(".md")
        for path in changes
    ):
        missing.append("karty decyzji DR")
    if missing:
        raise ValueError(
            "Zmiana kanonicznego Markdown wymaga także " + " oraz ".join(missing)
        )


def changed_paths(base_sha: str) -> dict[str, str]:
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotePath=false",
            "diff",
            "--name-status",
            f"{base_sha}...HEAD",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    changes: dict[str, str] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) >= 2:
            changes[fields[-1]] = fields[0][0]
    return changes


def validate_pending_decisions(changes, root=Path('.')):
    for name, status in changes.items():
        if not name.startswith('_decyzje/DR-') or not name.endswith('.md') or status == 'D':
            continue
        text = (root / name).read_text(encoding='utf-8')
        front = text.split('---', 2)[1]
        if 'schema_version: 2\n' not in front:
            continue  # Preserve historical records; the new contract is versioned.
        from narzedzia.decision_patch import read_fragments
        if 'zmiana_regulaminu: true\n' in front:
            read_fragments(text)
            if not re.search(r'<!-- applied-source-sha256:[a-f0-9]{64} -->', text):
                raise ValueError(f'{name}: najpierw nadaj etykietę wdrażaj na PR i poczekaj na DOCX')
            if SOURCE not in changes or DOCX not in changes:
                raise ValueError(f'{name}: wdrożenie wymaga zmienionego Markdown i DOCX w tym PR')
        elif 'zmiana_regulaminu: false\n' in front:
            if '## Stary fragment Markdown' in text or '## Nowy fragment Markdown' in text:
                raise ValueError(f'{name}: sprzeczne oznaczenie zmiany dokumentu')
        else:
            raise ValueError(f'{name}: brak automatycznego oznaczenia zmiany dokumentu')


def main() -> None:
    changes = changed_paths(sys.argv[1])
    validate_changes(changes)
    validate_pending_decisions(changes)


if __name__ == "__main__":
    main()
