---
id: DR-017
tytul: Struktura ZTP i automatyczna numeracja jednostek
typ: redakcyjna
status: przyjęta
data_inicjacji: 2026-09-19
data_decyzji: 2026-09-19
sezon: 2026/2027
dotyczy: Cały regulamin
decydenci: Komisja regulaminowa SPWS — na etapie inicjalnym autor projektu
discussion_url: ""
pr_url: ""
stan_obowiązywania: obowiązuje
zmienia: ["DR-001"]
zmieniona_przez: []
zakres_zmiany: {"DR-001":"Widoczne numery paragrafów są nadawane automatycznie po pełnym uporządkowaniu struktury; zachowano kolejność Przedmiot, Definicje, Cel oraz zakaz § 0."}
zastepuje: []
zastapiona_przez: []
termin_oceny: przed przekazaniem projektu do PZSz
---

## Problem

Dotychczasowy Markdown przechowywał treść jako płaskie akapity z ręcznie wpisanymi oznaczeniami. Po przenoszeniu przepisów łatwo było pozostawić błędną numerację i odesłania.

## Kontekst

Regulamin ma być redagowany zgodnie z aktualnymi Zasadami techniki prawodawczej. Struktura musi być jednoznaczna dla generatora i czytelna dla prawnika.

## Dyskusja

Uzgodniono pełną hierarchię: rozdział, paragraf, ustęp, punkt, litera, tiret i podwójne tiret. Tytuł paragrafu ma charakter informacyjny i nie jest jednostką przywoływaną w odesłaniach.

## Rozważane warianty

1. Zachowanie ręcznej numeracji w tekście.
2. Automatyczna numeracja wyłącznie paragrafów.
3. Semantyczny Markdown i automatyczna numeracja wszystkich jednostek.

## Decyzja

Regulamin stosuje hierarchię ZTP. Rozdziały oznacza się cyframi arabskimi. Paragraf dzieli się kolejno na ustępy, punkty, litery, tiret i podwójne tiret. Paragraf zawierający jedną myśl nie otrzymuje sztucznego ustępu 1. Widoczne numery i odesłania nadaje automat na podstawie stabilnych identyfikatorów.

## Uzasadnienie

Semantyczna struktura usuwa ryzyko ręcznego rozjazdu numeracji, umożliwia bezpieczne przenoszenie przepisów i pozwala sprawdzić hierarchię testami.

## Konsekwencje

Markdown staje się jedynym źródłem treści. Automat może poprawiać numerację, wcięcia i interpunkcję techniczną, lecz nie może zmieniać słów ani sensu przepisu. Niejednoznaczność wymagająca oceny prawnej zatrzymuje build.

## Odrzucone alternatywy

Odrzucono cyfry rzymskie dla rozdziałów oraz ręczne utrzymywanie numerów w treści. Odrzucono także obowiązkowe tworzenie ustępu 1 w każdym paragrafie.

## Plan oceny

Przed przekazaniem projektu do PZSz sprawdzić numerację, odesłania, śródtytuły oraz zgodność wygenerowanego DOCX z Markdown.

## Ocena po sezonie

Nie dotyczy skutków sportowych; ocenie podlega liczba błędów redakcyjnych ujawnionych po automatycznej normalizacji.

## Historia zmian

- 2026-09-19 — decyzja przyjęta przed pełną migracją treści do struktury ZTP.
