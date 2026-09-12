---
id: DR-016
tytul: Tabela punktacji i publiczny kalkulator SPWS
typ: merytoryczna
status: przyjęta
data_inicjacji: 2026-09-11
data_decyzji: 2026-09-11
sezon: 2026/2027
dotyczy: § 6 ust. 3–4 i załącznik nr 1
decydenci: Komisja regulaminowa SPWS — na etapie inicjalnym autor projektu
discussion_url: ""
pr_url: https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/pull/4
zastepuje: ""
zastapiona_przez: ""
termin_oceny: po zakończeniu sezonu 2026/2027
---

## Problem

Pełna tabela dla miejsc i stawek od 4 do 300 zawodników jest zbyt obszerna dla dokumentu Word, lecz zawodnicy potrzebują łatwego sposobu sprawdzenia punktów.

## Kontekst

Minimalna liczba uczestników wynosi cztery. Punktacja ma być zgodna z kalkulatorem SPWS. W dokumencie Word można czytelnie umieścić tabelę tylko dla mniejszych stawek.

## Dyskusja

Uzgodniono tabelę 4–40 w załączniku do regulaminu oraz pełną tabelę 4–300 w samodzielnym HTML na stronie SPWS. W zdaniu o kalkulatorze usunięto słowa „internetowego” i „rankingowych”.

## Rozważane warianty

1. Pełna tabela 4–300 w DOCX.
2. Wyłącznie kalkulator bez tabeli.
3. Skrócona tabela w DOCX oraz pełna tabela i kalkulator dostępne publicznie.

## Decyzja

Załącznik nr 1 do regulaminu zawiera tabelę dla stawek od 4 do 40 zawodników. SPWS publikuje pełną tabelę dla stawek od 4 do 300 zawodników oraz zapewnia publiczny i nieodpłatny dostęp do kalkulatora punktów umożliwiającego sprawdzenie liczby punktów za konkretny wynik.

## Uzasadnienie

Podział zachowuje użyteczność drukowanego dokumentu, a zarazem zapewnia dostęp do pełnego zakresu wartości i możliwość sprawdzenia konkretnego przypadku.

## Konsekwencje

Tabela DOCX, HTML i kalkulator muszą korzystać z tego samego algorytmu. Każda zmiana punktacji wymaga testu zgodności wszystkich trzech form publikacji.

## Odrzucone alternatywy

Odrzucono tabelę 4–300 w Wordzie jako nieczytelną oraz pozostawienie wyłącznie kalkulatora bez tabeli stanowiącej załącznik.

## Plan oceny

Po sezonie sprawdzić zgłoszone rozbieżności, dostępność kalkulatora, użyteczność tabeli 4–40 i przypadki stawek większych niż 40.

## Ocena po sezonie

Do uzupełnienia po sezonie 2026/2027.

## Historia zmian

- 2026-09-11 — załącznik i odwołania utrwalone w commitach `f285df1`–`360e0d2`.
