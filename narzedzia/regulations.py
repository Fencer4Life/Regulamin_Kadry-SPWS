from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from narzedzia.build_regulamin_docx import build_document
from narzedzia.normalize_regulamin_markdown import normalize_source
from narzedzia.prepare_regulamin import verify
from narzedzia.regulation_registry import ROOT, Regulation, all_regulations


def select_regulations(
    registered: tuple[Regulation, ...],
    *,
    identifiers: tuple[str, ...] = (),
    all_documents: bool = False,
) -> tuple[Regulation, ...]:
    if all_documents == bool(identifiers):
        raise ValueError("Wybierz dokumenty albo --all")
    if all_documents:
        return registered
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Dokument został wskazany więcej niż raz")
    known = {item.identifier: item for item in registered}
    unknown = [identifier for identifier in identifiers if identifier not in known]
    if unknown:
        raise ValueError(f"Nieznany dokument: {', '.join(unknown)}")
    selected = set(identifiers)
    return tuple(item for item in registered if item.identifier in selected)


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(content)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def build_regulations(
    regulations: tuple[Regulation, ...], *, root: Path = ROOT
) -> tuple[Path, ...]:
    if not regulations:
        raise ValueError("Nie wskazano dokumentów do zbudowania")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    prepared: list[tuple[Path, Path, bytes, bytes]] = []

    with tempfile.TemporaryDirectory(prefix=".regulations-", dir=root) as directory:
        staging = Path(directory)
        for index, regulation in enumerate(regulations):
            source = regulation.source_path(root)
            output = regulation.docx_path(root)
            if not source.is_file():
                raise ValueError(f"Brak źródła dokumentu {regulation.identifier}: {source}")
            normalized = normalize_source(source).encode("utf-8")
            staged_source = staging / f"{index}-{regulation.identifier}.md"
            candidate = staging / f"{index}-{regulation.identifier}.docx"
            staged_source.write_bytes(normalized)
            build_document(staged_source, candidate)
            prepared.append((source, output, normalized, candidate.read_bytes()))

        paths = [path for source, output, _, _ in prepared for path in (source, output)]
        backups = {path: path.read_bytes() if path.exists() else None for path in paths}
        try:
            for source, output, normalized, candidate in prepared:
                if source.read_bytes() != normalized:
                    _atomic_write(source, normalized)
                _atomic_write(output, candidate)
        except BaseException:
            for path, content in backups.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    _atomic_write(path, content)
            raise

    return tuple(regulation.docx_path(root) for regulation in regulations)


def verify_regulations(regulations: tuple[Regulation, ...], *, root: Path = ROOT) -> None:
    if not regulations:
        raise ValueError("Nie wskazano dokumentów do sprawdzenia")
    for regulation in regulations:
        verify(regulation.source_path(root), regulation.docx_path(root))


def main() -> None:
    parser = argparse.ArgumentParser(description="Buduje i sprawdza regulaminy z rejestru")
    parser.add_argument("mode", choices=("normalize-and-build", "verify"))
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--document", action="append", default=[])
    selection.add_argument("--all", action="store_true", dest="all_documents")
    arguments = parser.parse_args()

    regulations = select_regulations(
        all_regulations(),
        identifiers=tuple(arguments.document),
        all_documents=arguments.all_documents,
    )
    if arguments.mode == "normalize-and-build":
        for output in build_regulations(regulations):
            print(output)
    else:
        verify_regulations(regulations)
        print("OK: wszystkie wskazane Markdown i DOCX są zgodne")


if __name__ == "__main__":
    main()
