"""Publish one idempotent GitHub Release for one merged decision."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from narzedzia.regulation_registry import get_regulation


@dataclass(frozen=True)
class ReleaseSpec:
    decision_id: str
    tag: str
    title: str
    files: tuple[Path, ...]


def _metadata(card: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", card, re.DOTALL)
    if not match:
        raise ValueError("Karta decyzji nie ma poprawnych metadanych")
    result = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            result[key.strip()] = value.strip().strip('"')
    return result


def release_spec(card_path: Path, root: Path) -> ReleaseSpec:
    metadata = _metadata(card_path.read_text(encoding="utf-8"))
    decision_id = metadata.get("id", "")
    if not re.fullmatch(r"DR-\d{3}", decision_id):
        raise ValueError("Karta decyzji ma niepoprawny identyfikator")
    files = [card_path]
    if metadata.get("zmiana_regulaminu") == "true":
        raw_documents = metadata.get("dokumenty", '["reprezentacja"]')
        try:
            documents = json.loads(raw_documents)
        except json.JSONDecodeError as error:
            raise ValueError("Karta decyzji ma niepoprawną listę dokumentów") from error
        if not isinstance(documents, list) or not documents:
            raise ValueError("Przyjęta zmiana nie wskazuje dokumentów")
        files.extend(get_regulation(identifier).docx_path(root) for identifier in documents)
    if any(not path.is_file() or path.is_symlink() for path in files):
        raise ValueError("Wydanie wymaga zwykłej karty i wszystkich wskazanych DOCX")
    return ReleaseSpec(
        decision_id=decision_id,
        tag=f"decyzja-{decision_id}",
        title=f"Decyzja {decision_id}",
        files=tuple(files),
    )


def publish_release(repo: str, sha: str, card_path: Path, root: Path, *, run=subprocess.run):
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("Niepoprawne repozytorium lub SHA wydania")
    spec = release_spec(card_path, root)
    view = run(
        ["gh", "release", "view", spec.tag, "--repo", repo],
        text=True,
        capture_output=True,
    )
    if view.returncode != 0:
        created = run(
            [
                "gh",
                "release",
                "create",
                spec.tag,
                "--repo",
                repo,
                "--target",
                sha,
                "--title",
                spec.title,
                "--notes",
                f"Karta i dokumenty objęte decyzją {spec.decision_id}.",
            ],
            text=True,
            capture_output=True,
        )
        if created.returncode != 0:
            raise RuntimeError(created.stderr or "Nie udało się utworzyć wydania")
    uploaded = run(
        [
            "gh",
            "release",
            "upload",
            spec.tag,
            *(str(path) for path in spec.files),
            "--clobber",
            "--repo",
            repo,
        ],
        text=True,
        capture_output=True,
    )
    if uploaded.returncode != 0:
        raise RuntimeError(uploaded.stderr or "Nie udało się dołączyć plików do wydania")
    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo")
    parser.add_argument("sha")
    parser.add_argument("card", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    spec = publish_release(args.repo, args.sha, args.card, args.root)
    print(spec.tag)


if __name__ == "__main__":
    main()
