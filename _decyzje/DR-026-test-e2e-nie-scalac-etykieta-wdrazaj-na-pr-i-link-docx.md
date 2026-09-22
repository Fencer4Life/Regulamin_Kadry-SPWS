---
id: DR-026
tytul: "[TEST E2E — NIE SCALAĆ] Etykieta wdrażaj na PR i link DOCX"
typ: merytoryczna
status: przyjęta
stan_obowiązywania: obowiązuje
data_inicjacji: 2026-09-22
data_decyzji: "2026-09-22"
sezon: 2026/2027
dotyczy: Test automatu
decydenci: Komisja regulaminowa SPWS
discussion_url: https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/59
pr_url: ""
zmienia: []
zmieniona_przez: []
zakres_zmiany: {}
zastepuje: []
zastapiona_przez: []
termin_oceny: po zakończeniu sezonu 2026/2027
---

## Problem

Sprawdzenie automatycznego wdrożenia z etykiety PR oraz bezpiecznego ponowienia.

## Kontekst



**Obszar:** Test automatu





## Dyskusja

Zobacz dyskusję źródłową: [https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/59](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/59).

**Koordynator dyskusji:** @Fencer4Life

**Uczestnicy:** @Fencer4Life

## Rozważane warianty

Test lokalny nie zastępuje zdarzenia etykiety GitHub.

## Decyzja

Wyłącznie w testowym PR zastąpić datę na okładce znacznikiem TEST-ETYKIETA-58. Sprawdzić DOCX i link w opisie, powtórzyć etykietę, zamknąć PR bez scalania.

## Stary fragment Markdown

Wklej dokładny fragment kanonicznego .md, ze znacznikami i wcięciami.

```markdown
| Data projektu | [data] |
```

## Nowy fragment Markdown

Wklej kompletną treść zastępującą stary fragment; zachowaj identyfikatory jednostek.

```markdown
| Data projektu | [data] TEST-ETYKIETA-58 |
```

## Uzasadnienie

> _Do uzupełnienia przez osobę przygotowującą decyzję._

## Konsekwencje

### Czy decyzja wymaga zmiany Regulaminu?

- [ ] **Tak** — należy przygotować zmianę Regulaminu i dołączyć ją do tego samego pull requestu.
- [ ] **Nie** — decyzja nie wymaga zmiany Regulaminu.

## Odrzucone alternatywy

Test lokalny nie zastępuje zdarzenia etykiety GitHub.

## Plan oceny

Po zakończeniu sezonu 2026/2027.

## Ocena po sezonie

Nie dotyczy przed przyjęciem decyzji.

## Historia zmian

- 2026-09-22 — robocza karta utworzona automatycznie po oznaczeniu dyskusji jako `rozstrzygnięta`.
