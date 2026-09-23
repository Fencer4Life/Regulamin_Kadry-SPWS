---
id: DR-027
tytul: "Odsyłacze zależne od miejsca w dokumencie"
typ: redakcyjna
status: przyjęta
stan_obowiązywania: obowiązuje
data_inicjacji: 2026-09-23
data_decyzji: 2026-09-23
sezon: 2026/2027
dotyczy: odsyłacze wewnętrzne i deterministyczne generowanie DOCX
decydenci: Fencer4Life — zatwierdzenie redakcyjne w rozmowie roboczej
discussion_url: ""
pr_url: ""
zmienia: []
zmieniona_przez: []
zakres_zmiany: {}
zastepuje: []
zastapiona_przez: []
termin_oceny: po kolejnej zmianie numeracji przepisów
---

## Problem

Pełne odsyłacze powtarzały numer bieżącego paragrafu, utrudniając czytanie. Po ręcznym skróceniu generator drukował techniczne znaczniki odsyłaczy w DOCX.

## Kontekst

Markdown jest źródłem treści. Ukryty identyfikator wskazuje jednostkę niezależnie od jej aktualnego numeru. Workflow pozostaje bez zmian.

## Dyskusja

Ustalenie zatwierdzone przez Fencer4Life w rozmowie roboczej 23.09.2026. Nie zakładano dyskusji GitHub i nie jest to uchwała komisji ani przyjęcie Regulaminu przez organ SPWS.

## Rozważane warianty

Zachowanie ręcznie wpisanego tekstu z kontrolą jego zgodności albo automatyczne ustalanie numeru, zakresu i kierunku odsyłacza na podstawie stabilnego identyfikatora.

## Decyzja

Stosujemy automatyczne odsyłacze kontekstowe:

1. W tym samym ustępie odsyłacz do innego punktu nie powtarza numerów paragrafu i ustępu.
2. W tym samym paragrafie, lecz innym ustępie, odsyłacz zawiera numer ustępu i ewentualnych jednostek podrzędnych, bez numeru paragrafu.
3. Numer paragrafu występuje przy odwołaniu do innego paragrafu.
4. Dla odsyłaczy lokalnych kierunek wynika z położenia jednostek: aktualny punkt o większym numerze niż docelowy oznacza „powyżej”, o mniejszym — „poniżej”. Punkty porównujemy w ramach wspólnego ustępu; dla różnych ustępów najpierw porównujemy ustępy.
5. Generator aktualizuje widoczny Markdown oraz DOCX według tej samej reguły. Ukryty identyfikator pozostaje stały. Nieznany cel, samoodwołanie lub nieprawidłowy znacznik zatrzymują generowanie.

## Uzasadnienie

Czytelny tekst nie wymaga powtarzania adresu bieżącego paragrafu. Stabilne identyfikatory umożliwiają deterministyczną aktualizację numerów i kierunku bez LLM.

## Konsekwencje

- [x] **Tak** — zmiana redakcyjna czterech lokalnych odsyłaczy i regeneracja DOCX z main.
- [ ] **Nie** — decyzja nie wymaga zmiany Regulaminu.

Nie zmieniamy merytorycznej treści przepisów, uprawnień GitHub ani workflow. Przegląd i zgoda na scalenie pozostają ręczne.

### Zastosowanie w PR #72

W [PR #72](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/pull/72) zachowano redakcję Fencer4Life: pisownię nazwy na okładce, nagłówka „Konstrukcja Regulaminu”, pozycji 6 tabeli konstrukcji oraz rozwinięcie nazwy i określenie „Regulaminem” w § 1. Krótkie odsyłacze doprowadzono do reguł niniejszej decyzji, dodając „poniżej” w dwóch miejscach. DOCX odtworzono z Markdown; test oczekiwanego nagłówka dostosowano do nowej pisowni. Zapis dokumentuje zgodę redakcyjną Fencer4Life na integrację, nie uchwałę komisji.

## Odrzucone alternatywy

Pozostawienie pełnych adresów we wszystkich odsyłaczach oraz ręczne utrzymywanie numerów niezależnie od identyfikatorów.

## Plan oceny

Testy obu kierunków, różnych ustępów i paragrafów, zmiany kolejności, błędnych celów, idempotencji, zgodności Markdown–DOCX oraz pojedynczej zmiany E2E.

## Ocena po sezonie

Do przeprowadzenia w ramach przeglądu redakcyjnego.

## Historia zmian

- 2026-09-23 — zatwierdzenie reguł i zgoda Fencer4Life na zapis DR oraz integrację po testach.
- 2026-09-23 — zastosowanie generatora w PR #72 wraz z zachowaniem poprawek redakcyjnych autora i ponowną kontrolą zgodności Markdown–DOCX.
