from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "CONTRIBUTING.md",
    "ZASADY_REJESTRU.md",
    "regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx",
    "zalaczniki/Zalacznik-1-tabela-punktacji-SPWS_2026-2027.html",
    "narzedzia/requirements-docx.txt",
    "narzedzia/generate_regulamin_docx.py",
    "narzedzia/sanitize_docx_metadata.py",
    "tests/test_docx_pagination.py",
    "tests/test_approved_sections_02_03.py",
)

README_HEADINGS = (
    "# Regulamin Kadry SPWS",
    "## Status projektu",
    "## Najważniejsze dokumenty",
    "## Role SPWS i PZSz",
    "## Źródło aktualnej treści",
    "## Struktura repozytorium",
    "## Jak współpracować",
    "## Praca z dokumentem Word",
    "## Narzędzia i testy",
    "## Wersjonowanie i wydania",
    "## Jawność, prywatność i licencja",
)


class RepositoryStructureTests(unittest.TestCase):
    def test_required_project_files_exist(self):
        missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
        self.assertEqual(missing, [], f"Brak wymaganych plików: {missing}")

    def test_readme_has_all_agreed_sections(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        missing = [heading for heading in README_HEADINGS if heading not in readme]
        self.assertEqual(missing, [], f"README nie zawiera sekcji: {missing}")

    def test_readme_relative_links_point_to_existing_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", readme)
        broken = []
        for target in targets:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if path and not (ROOT / path).exists():
                broken.append(target)
        self.assertEqual(broken, [], f"Niedziałające odnośniki względne w README: {broken}")

    def test_repository_contains_no_working_backups_or_word_lock_files(self):
        tracked = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split("\0")
        forbidden = [
            path
            for path in tracked
            if path
            and (
                Path(path).name.startswith("~$")
                or ".backup-" in Path(path).name
                or Path(path).name == ".DS_Store"
            )
        ]
        self.assertEqual(forbidden, [], f"Pliki robocze nie mogą trafić do repozytorium: {forbidden}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
