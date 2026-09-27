from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SOURCE = "regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md"
DOCX = "regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx"


def validate_changes(changes: dict[str, str]) -> None:
    if SOURCE not in changes:
        return
    missing: list[str] = []
    if DOCX not in changes:
        missing.append("wygenerowanego DOCX")
    initial_migration = changes[SOURCE] == "A"
    if not initial_migration and not any(
        path.startswith("_decyzje/DR-") and path.endswith(".md") for path in changes
    ):
        missing.append("karty decyzji DR")
    if missing:
        raise ValueError("Zmiana kanonicznego Markdown wymaga także " + " oraz ".join(missing))


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


def validate_pending_decisions(changes, root=Path(".")):
    for name, status in changes.items():
        if not name.startswith("_decyzje/DR-") or not name.endswith(".md") or status == "D":
            continue
        text = (root / name).read_text(encoding="utf-8")
        front = text.split("---", 2)[1]
        schema_match = re.search(r"^schema_version:\s*([23])\s*$", front, re.MULTILINE)
        if not schema_match:
            continue  # Preserve historical records; the new contract is versioned.
        schema = int(schema_match.group(1))
        from narzedzia.decision_patch import read_document_fragments, read_fragments

        has_marker = bool(re.search(r"<!-- applied-source-sha256:[a-f0-9]{64} -->", text))

        if "zmiana_regulaminu: true\n" in front:
            if schema == 2:
                read_fragments(text)
                required_paths = (SOURCE, DOCX)
            else:
                document_match = re.search(r"^dokumenty:\s*(\[.*\])\s*$", front, re.MULTILINE)
                if not document_match:
                    raise ValueError(f"{name}: brak listy dokumentów")
                try:
                    documents = json.loads(document_match.group(1))
                except json.JSONDecodeError as error:
                    raise ValueError(f"{name}: niepoprawna lista dokumentów") from error
                fragments = read_document_fragments(text)
                if not isinstance(documents, list) or set(documents) != set(fragments):
                    raise ValueError(f"{name}: fragmenty nie odpowiadają wskazanym dokumentom")
                from narzedzia.regulation_registry import get_regulation

                required_paths = tuple(
                    str(path)
                    for identifier in documents
                    for path in (
                        get_regulation(identifier).markdown,
                        get_regulation(identifier).docx,
                    )
                )
            if not has_marker:
                raise ValueError(
                    f"{name}: najpierw nadaj etykietę wdrażaj na PR i poczekaj na DOCX"
                )
            if any(path not in changes for path in required_paths):
                raise ValueError(f"{name}: wdrożenie wymaga zmienionego Markdown i DOCX w tym PR")
        elif "zmiana_regulaminu: false\n" in front:
            rejected = bool(re.search(r"^status:\s*[\"]?odrzucona[\"]?\s*$", front, re.MULTILINE))
            proposed = "proponowana_zmiana: true\n" in front
            has_fragments = "Stary fragment Markdown" in text or "Nowy fragment Markdown" in text
            if schema == 3 and rejected:
                if has_marker:
                    raise ValueError(f"{name}: decyzja odrzucona nie może mieć znacznika wdrożenia")
                if proposed != has_fragments:
                    raise ValueError(f"{name}: propozycja zmiany i jej fragmenty są niespójne")
            elif has_fragments:
                raise ValueError(f"{name}: sprzeczne oznaczenie zmiany dokumentu")
        else:
            raise ValueError(f"{name}: brak automatycznego oznaczenia zmiany dokumentu")


def main() -> None:
    changes = changed_paths(sys.argv[1])
    validate_changes(changes)
    validate_pending_decisions(changes)


if __name__ == "__main__":
    main()
