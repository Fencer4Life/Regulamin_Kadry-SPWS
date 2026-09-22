---
id: DR-025
tytul: "[TEST E2E — NIE SCALAĆ] Automat bez dodatkowego podglądu"
typ: merytoryczna
status: przyjęta
stan_obowiązywania: obowiązuje
data_inicjacji: 2026-09-22
data_decyzji: "2026-09-22"
sezon: 2026/2027
dotyczy: Test techniczny automatu
decydenci: Komisja regulaminowa SPWS
discussion_url: https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/54
pr_url: ""
zmienia: []
zmieniona_przez: []
zakres_zmiany: {}
zastepuje: []
zastapiona_przez: []
termin_oceny: po zakończeniu sezonu 2026/2027
---

## Problem

Potwierdzenie pełnej ścieżki: dyskusja → etykieta → karta → dokładna zamiana Markdown → DOCX. Zmiana wyłącznie pola daty na okładce, w testowej gałęzi.

## Kontekst



**Obszar:** Test techniczny automatu





## Dyskusja

Zobacz dyskusję źródłową: [https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/54](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/54).

**Koordynator dyskusji:** @Fencer4Life

**Uczestnicy:** @Fencer4Life

## Rozważane warianty

Test na kopii lokalnej nie zastępuje sprawdzenia rzeczywistego zdarzenia GitHub.

## Decyzja

W testowym PR zastąpić wskazany wiersz daty. Po pobraniu i porównaniu DOCX zamknąć PR bez scalania. Nie zmieniać przepisów.

## Stary fragment Markdown

Wklej dokładny fragment kanonicznego .md, ze znacznikami i wcięciami.

```markdown
| Data projektu | [data] |
```

## Nowy fragment Markdown

Wklej kompletną treść zastępującą stary fragment; zachowaj identyfikatory jednostek.

```markdown
| Data projektu | [data] TEST-E2E-53 |
```

## Uzasadnienie

> _Do uzupełnienia przez osobę przygotowującą decyzję._

## Konsekwencje

### Czy decyzja wymaga zmiany Regulaminu?

- [ ] **Tak** — należy przygotować zmianę Regulaminu i dołączyć ją do tego samego pull requestu.
- [ ] **Nie** — decyzja nie wymaga zmiany Regulaminu.

## Odrzucone alternatywy

Test na kopii lokalnej nie zastępuje sprawdzenia rzeczywistego zdarzenia GitHub.

## Plan oceny

Po zakończeniu sezonu 2026/2027.

## Ocena po sezonie

Nie dotyczy przed przyjęciem decyzji.

## Historia zmian

- 2026-09-22 — robocza karta utworzona automatycznie po oznaczeniu dyskusji jako `rozstrzygnięta`.
