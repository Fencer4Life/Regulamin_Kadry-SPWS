from __future__ import annotations

import subprocess
import sys


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


def main() -> None:
    validate_changes(changed_paths(sys.argv[1]))


if __name__ == "__main__":
    main()
