from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "_data" / "regulations.json"
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9-]*$")
REQUIRED_FIELDS = {
    "id",
    "title",
    "label",
    "markdown",
    "docx",
    "artifact",
    "validators",
}


@dataclass(frozen=True)
class Regulation:
    identifier: str
    title: str
    label: str
    markdown: Path
    docx: Path
    artifact: str
    validators: tuple[str, ...]

    def source_path(self, root: Path = ROOT) -> Path:
        return root / self.markdown

    def docx_path(self, root: Path = ROOT) -> Path:
        return root / self.docx


def _safe_relative_path(value: object, *, suffix: str, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"Pole {field} musi zawierać ścieżkę")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.suffix.lower() != suffix:
        raise ValueError(f"Pole {field} musi być bezpieczną ścieżką względną {suffix}")
    return path


def _unique(regulations: tuple[Regulation, ...], attribute: str) -> None:
    values = [getattr(regulation, attribute) for regulation in regulations]
    if len(values) != len(set(values)):
        raise ValueError(f"Wartość pola {attribute} powtarza się w rejestrze")


def load_registry(path: Path = REGISTRY_PATH) -> tuple[Regulation, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("regulations"), list):
        raise ValueError("Rejestr dokumentów ma nieobsługiwany schemat")

    regulations = []
    for raw in payload["regulations"]:
        if not isinstance(raw, dict) or set(raw) != REQUIRED_FIELDS:
            raise ValueError("Wpis rejestru dokumentów ma nieprawidłowe pola")
        identifier = raw["id"]
        if not isinstance(identifier, str) or not IDENTIFIER_RE.fullmatch(identifier):
            raise ValueError("Identyfikator dokumentu jest nieprawidłowy")
        validators = raw["validators"]
        if (
            not isinstance(validators, list)
            or not validators
            or not all(
                isinstance(item, str) and IDENTIFIER_RE.fullmatch(item) for item in validators
            )
        ):
            raise ValueError("Profile walidacji dokumentu są nieprawidłowe")
        for field in ("title", "label", "artifact"):
            if not isinstance(raw[field], str) or not raw[field].strip():
                raise ValueError(f"Pole {field} nie może być puste")
        regulations.append(
            Regulation(
                identifier=identifier,
                title=raw["title"],
                label=raw["label"],
                markdown=_safe_relative_path(raw["markdown"], suffix=".md", field="markdown"),
                docx=_safe_relative_path(raw["docx"], suffix=".docx", field="docx"),
                artifact=raw["artifact"],
                validators=tuple(validators),
            )
        )

    result = tuple(regulations)
    if not result:
        raise ValueError("Rejestr dokumentów nie może być pusty")
    for attribute in ("identifier", "label", "markdown", "docx", "artifact"):
        _unique(result, attribute)
    return result


def all_regulations() -> tuple[Regulation, ...]:
    return load_registry()


def get_regulation(identifier: str) -> Regulation:
    for regulation in all_regulations():
        if regulation.identifier == identifier:
            return regulation
    raise ValueError(f"Nieznany dokument: {identifier}")
