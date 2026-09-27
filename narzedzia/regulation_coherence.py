from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path

from narzedzia.regulation_registry import ROOT, all_regulations

COMMON_PHRASES = (
    "Ranking wyłaniania Reprezentacji Polski Weteranów",
    "osobno dla każdej broni, płci i kategorii wiekowej",
    "możliwie najsilniejszej reprezentacji Polski weteranów w szermierce",
    "Stowarzyszenie Polskich Weteranów Szermierki",
    "Polski Związek Szermierczy",
    "dwa najlepsze wyniki punktowe zawodnika uzyskane w PPW",
    "wynik punktowy uzyskany w MPW",
    "za każdą niewypełnioną pozycję PPW przyjmuje się 0 punktów",
    "za obowiązkową pozycję MPW przyjmuje się 0 punktów",
    "Klasyfikacja Pucharu Polski Weteranów",
    "filtrowanym podzbiorem Rankingu",
    "filtra obejmującego PPW i MPW",
)

V0_PHRASES = (
    "PPW, MPW, PPS i MPS",
    "nie uwzględnia się punktów z zawodów EVF ani FIE",
    "nie stanowią podstawy powołania do reprezentacji",
)


def load_regulation_texts(root: Path = ROOT) -> dict[str, str]:
    return {
        regulation.identifier: regulation.source_path(root).read_text(encoding="utf-8")
        for regulation in all_regulations()
    }


def coherence_issues(texts: Mapping[str, str]) -> list[str]:
    required_documents = {"reprezentacja", "zawody"}
    missing = required_documents - texts.keys()
    if missing:
        return [f"Brak dokumentów do kontroli: {', '.join(sorted(missing))}"]

    representation = texts["reprezentacja"]
    competition = texts["zawody"]
    issues = []
    for phrase in (*COMMON_PHRASES, *V0_PHRASES):
        for identifier, text in (("reprezentacja", representation), ("zawody", competition)):
            if phrase not in text:
                issues.append(f"{identifier}: brak wspólnego inwariantu: {phrase}")

    if "Klasyfikacja łączona" in representation:
        issues.append("reprezentacja: Klasyfikacja łączona nie może określać powołań")
    for phrase in (
        "wyłącznie do rozstawienia zawodników w pierwszej rundzie grupowej",
        "Rozstawienie do drugiej rundy grupowej ustala się wyłącznie na podstawie wyników "
        "pierwszej rundy grupowej",
        "w chwili wygenerowania pliku XML",
    ):
        if phrase not in competition:
            issues.append(f"zawody: brak ograniczenia Klasyfikacji łączonej: {phrase}")

    if "który w tych sprawach jest dokumentem nadrzędnym" not in competition:
        issues.append("zawody: brak nadrzędności regulaminu reprezentacji w sprawach Rankingu")
    if "Pozycje kategorii V0 nie stanowią podstawy powołania" not in representation:
        issues.append("reprezentacja: brak wyłączenia V0 z powołań")
    return issues


def assert_coherent(root: Path = ROOT) -> None:
    issues = coherence_issues(load_regulation_texts(root))
    if issues:
        raise ValueError("Niespójność regulaminów:\n- " + "\n- ".join(issues))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sprawdza jawne inwarianty wspólne dla obu regulaminów"
    )
    parser.parse_args()
    assert_coherent()
    print("OK: jawne inwarianty obu regulaminów są spójne")


if __name__ == "__main__":
    main()
