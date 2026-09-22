# Regulamin Kadry SPWS

Publiczne repozytorium prac nad **Regulaminem powoływania reprezentacji Polski weteranów w szermierce** na sezon 2026/2027. Łączy aktualny dokument Word, narzędzia kontrolujące jego strukturę oraz Rejestr Decyzji wyjaśniający przyjęte rozwiązania i rozważane alternatywy.

## Status projektu

| Pole | Wartość |
|---|---|
| Sezon | 2026/2027 |
| Wersja dokumentu | 0.2 |
| Status | projekt do konsultacji |
| Stan treści | treść przyjęta redakcyjnie do projektu, bez pozostałych brudnopisów; wymaga przyjęcia przez Zarząd SPWS |

> **Ważne:** dokument znajdujący się w tym repozytorium jest projektem. Regulamin przyjmuje Zarząd SPWS w drodze uchwały, która określa termin wejścia w życie.

## Najważniejsze dokumenty

- [Aktualny projekt regulaminu w formacie MS Word](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/regulamin/Regulamin-powolywania-reprezentacji-Polski-weteran%C3%B3w-w-szermierce_2026.docx)
- [Rejestr Decyzji — widok HTML](https://html-preview.github.io/?url=https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/index.html)
- [Załącznik nr 1 — pełna tabela punktacji dla stawek od 4 do 300 zawodników](https://html-preview.github.io/?url=https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/zalaczniki/Zalacznik-1-tabela-punktacji-SPWS_2026-2027.html)
- [Informacja o zatwierdzonych wydaniach](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/wydania/README.md)
- [Kalkulator punktów SPWS](https://fencer4life.github.io/spws-automated-ranklist/kalkulator-punktow.html?lang=pl)
- [Zasady prowadzenia Rejestru Decyzji](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/ZASADY_REJESTRU.md)
- [Przewodnik: jak pracujemy nad regulaminem](https://html-preview.github.io/?url=https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/przewodnik.html)
- [Decyzje architektoniczne projektu](https://fencer4life.github.io/Regulamin_Kadry-SPWS/dokumentacja/adr/)
- [Projekt automatu Markdown → DOCX](https://html-preview.github.io/?url=https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/plany/2026-09-16-wdrozenie-automatu-md-docx-design.html)
- [Zasady współpracy](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/CONTRIBUTING.md)

## Role SPWS i PZSz

**Stowarzyszenie Polskich Weteranów Szermierki (SPWS)** przygotowuje projekt, prowadzi konsultacje i dokumentuje decyzje podejmowane podczas prac.

**Zarząd SPWS** przyjmuje regulamin w drodze uchwały. Samo opublikowanie projektu ani połączenie zmian z gałęzią `main` nie oznacza przyjęcia regulaminu.

**Polski Związek Szermierczy (PZSz)** akceptuje proponowane składy reprezentacji zgodnie z przepisami regulaminu; nie jest organem przyjmującym regulamin.

## Źródło aktualnej treści i automatyzacja

Kontrolowany Markdown w `regulamin/` jest jedynym źródłem kanonicznym. DOCX jest wynikiem generatora i nie służy do ręcznego wprowadzania zmian. Markdown zapisuje semantyczną hierarchię ZTP: rozdział, paragraf, ustęp, punkt, literę, tiret i podwójne tiret. Każda jednostka ma stabilny identyfikator, dlatego automat może przenumerować dokument i poprawić odesłania bez zmiany słów przepisu.

Właściwy [źródłowy Markdown](regulamin/Regulamin-powolywania-reprezentacji-Polski-weteranow-w-szermierce_2026.md) zawiera treść okładki, spis treści, tabelę rozdziałów, przepisy, pełne tabele załącznika, historię wersji, nagłówki i stopki. Redaguje się ten jeden plik. Bloki `<!-- publication:... -->` wskazują przeznaczenie treści; `<!-- unit:... -->` zachowują tożsamość przepisów. Odesłania i terminy mają widoczne brzmienie oraz komentarz techniczny, np. `T−75<!-- term:karty -->`. Numerację i odesłania aktualizuje normalizacja; zmiana celu odesłania wymaga zmiany jego identyfikatora. Wartości stron w spisie treści i stopce odpowiadają zapisanym polom wzorca; Word może je odświeżyć przy otwarciu. Tekstów dokumentu nie trzeba szukać w metadanych ani w osobnym podglądzie. Jedynym dokumentem wynikowym jest DOCX; raporty kontroli są artefaktami CI.

CI publikuje artefakt `source-evidence`: raport HTML/JSON, odtworzony DOCX, ponowne odtworzenie oraz kopię `E2E_TEST.docx`. Test pokrycia sprawdza każdy niepusty akapit i komórkę wzorca. E2E stosuje kartę stary/nowy wyłącznie do kopii źródła: dopuszcza jedną dosłowną zmianę w tym samym miejscu XML i żadnych zmian w pozostałych częściach DOCX. Materiał E2E nie jest wersją regulaminu do publikacji.

Redaktor wypełnia w [szablonie decyzji](szablony/nowa-decyzja.md) pola **Stary fragment Markdown** oraz **Nowy fragment Markdown**. Są przenoszone również z formularza dyskusji. Na **Pull Requeście** (nie na dyskusji) nadaj etykietę **`wdrażaj`**. Automat sam ustala gałąź i jedyną kartę DR, wykonuje dokładną zamianę, normalizuje ZTP, generuje i sprawdza DOCX. Na górze opisu PR umieszcza sekcję **DOCX do sprawdzenia** z linkiem przypiętym do commita. Nie wybierasz workflow ani numeru DR. Ponowne nadanie etykiety nie stosuje wdrożonej decyzji drugi raz; może odtworzyć link. Przegląd i scalenie pozostają ręczne. Ręczny workflow **Wdrożenie dokładnej zmiany z decyzji** pozostaje opcją techniczną. Wymagany jest status `przyjęta`; puste lub wieloznaczne zmiany zatrzymują automat. Instrukcja i ograniczenia: [ADR-003](dokumentacja/adr/ADR-003-deterministyczny-markdown.html).

Automat normalizuje strukturę Markdown przed generowaniem DOCX. Może poprawić numery, oznaczenia wyliczeń, wcięcia, interpunkcję techniczną i odesłania. Nie może samodzielnie parafrazować ani zmieniać znaczenia. Gdy struktura jest niejednoznaczna i wymaga decyzji merytorycznej, build zatrzymuje się, a poprzedni prawidłowy DOCX pozostaje bez zmian.

W dokumencie obowiązują trzy jawne statusy treści:

- `accepted` — treść przyjęta, renderowana czarną czcionką;
- `source-draft` — nieopracowana treść starego źródła, renderowana ciemnoszaro i poprzedzona etykietą **BRUDNOPIS ZE ŹRÓDŁA — DO OPRACOWANIA**;
- `placeholder` — jawne miejsce wymagające nowej decyzji.

Prywatny dokument użyty do jednorazowej migracji nie jest przechowywany w GitHubie. Publiczna [mapa migracji](dokumentacja/migracja/2026-09-19-mapa-tresci-zrodlowej.html) zawiera jego nazwę, hash i status każdego rozpoznanego fragmentu, ale nie zawiera surowych komentarzy autora ani pełnej ekstrakcji.

Każdy Pull Request zmieniający treść zawiera razem Markdown, kartę decyzji i wygenerowany DOCX. CI sprawdza kanoniczną postać Markdown, tworzy drugi kandydat, uruchamia testy treści, ZTP, stronicowania i bezpieczeństwa, porównuje go z DOCX z PR oraz udostępnia plik jako artefakt runu.

**Akceptacja następuje przed Release:** Redaktor pobiera artefakt `regulamin-candidate.docx` z runu CI albo otwiera DOCX dołączony do PR w Microsoft Word. Następnie wybiera `Approve` i scala PR albo wybiera `Request changes`/zamyka PR. Dopóki PR nie zostanie scalony, `main` i jego DOCX nie zmieniają się. Release uruchamia się dopiero po scaleniu i publikuje już zaakceptowaną wersję; nie jest osobnym miejscem akceptacji albo odrzucenia dokumentu.

W pełnej ścieżce Redaktor sam opracowuje brzmienie Markdown na podstawie decyzji komisji, ponieważ zmiana może wymagać oceny i zmieniać sens przepisu. Szybka ścieżka `redakcja-bez-zmiany-sensu` służy wyłącznie korekcie, której dokładne stare i nowe brzmienie podano w dyskusji. Po dodaniu tej etykiety automat sam stosuje jednoznaczną zamianę i tworzy draft PR. Automat odrzuci brak albo wielokrotne wystąpienie fragmentu, a nieudany build nie zmieni żadnego DOCX na `main`.

## Struktura repozytorium

| Ścieżka | Przeznaczenie |
|---|---|
| `regulamin/` | kanoniczny Markdown oraz aktualna, wygenerowana z niego migawka DOCX |
| `wydania/` | formalnie zatwierdzone, niezmienne wersje sezonowe |
| `_decyzje/` | źródłowe karty decyzji w Markdown |
| `dokumentacja/adr/` | trwałe decyzje architektoniczne dotyczące automatyzacji i publikacji projektu |
| `zalaczniki/` | publiczne załączniki i materiały stanowiące część projektu |
| `narzedzia/` | kod Python do tworzenia i kontrolowanych zmian DOCX |
| `tests/` | testy treści, stronicowania, bezpieczeństwa DOCX i kompletności rejestru |
| `_layouts/`, `_includes/`, `assets/` | szablony strony Rejestru Decyzji |
| `.github/` | formularze współpracy i automatyczna walidacja |

Automatyczne kopie DOCX, pliki blokady Worda, wynik `_site/` oraz środowisko `.venv/` nie są wersjonowane.

## Jak współpracować

Zmianę rozpoczyna dyskusja ze wskazanym Koordynatorem dyskusji i opisem problemu. Po uzgodnieniu wyniku Koordynator wybiera jedną z dwóch ścieżek etykietą. `rozstrzygnięta` uruchamia pełną ścieżkę, w której Redaktor przekłada decyzję na Markdown. `redakcja-bez-zmiany-sensu` uruchamia szybką ścieżkę i automat stosuje dokładną zamianę podaną w dyskusji. W obu przypadkach powstaje roboczy Pull Request, a CI udostępnia kandydacki DOCX do kontroli w Wordzie.

Skrócony przebieg:

1. zgłoszenie problemu w GitHub Discussions;
2. dyskusja komisji nad wariantami i konsekwencjami;
3. wybór pełnej albo szybkiej ścieżki przez Koordynatora;
4. automatyczne przygotowanie karty decyzji i draft Pull Requestu;
5. opracowanie Markdown przez Redaktora w pełnej ścieżce albo automatyczna dokładna zamiana w szybkiej;
6. automatyczne zbudowanie i przetestowanie DOCX oraz kontrola pliku w Wordzie;
7. przegląd i scalenie dokumentacji oraz treści;
8. publikacja i ocena skutków po zakończeniu sezonu.

Pełny proces opisuje [przewodnik dla komisji](https://html-preview.github.io/?url=https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/przewodnik.html), reguły dokumentowania zawierają [Zasady prowadzenia Rejestru Decyzji](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/ZASADY_REJESTRU.md), a instrukcję techniczną przygotowania zmian — [CONTRIBUTING.md](https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/blob/main/CONTRIBUTING.md).

## Praca z dokumentem Word

- Otwieraj DOCX w Microsoft Word do kontroli treści i układu; zmiany wracają do kanonicznego Markdown, a DOCX jest generowany ponownie.
- Nie zapisuj ręcznych poprawek w śledzonym DOCX, ponieważ następny build je zastąpi.
- Przed publikacją uruchom skrypt oczyszczający metadane i komplet testów.
- Nie commituj plików `~$*.docx` ani `*.backup-*.docx`.
- Nie uruchamiaj historycznych skryptów `apply_*.py` na aktualnym dokumencie bez sprawdzenia ich warunków wejściowych i wykonania kopii poza repozytorium.

Oczyszczenie publicznych metadanych:

```bash
python narzedzia/sanitize_docx_metadata.py
```

## Narzędzia i testy

Wymagany jest Python 3.11 lub nowszy. Z katalogu głównego repozytorium:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r narzedzia/requirements-docx.txt
python -m unittest discover -s tests -v
```

Testy sprawdzają między innymi zaakceptowane brzmienie chronionych postanowień, reguły stronicowania, niepodzielność tabel, brak komentarzy i śledzonych zmian w publicznym DOCX oraz kompletność Rejestru Decyzji.

`prepare_regulamin.py` jest bieżącym wejściem do normalizacji i budowania. `generate_regulamin_docx.py` oraz skrypty `apply_*.py` dokumentują historyczne etapy pracy i nie są źródłem aktualnej treści.

### Edycja terminarza, osi czasu i tabel

Wszystkie te elementy znajdują się w kanonicznym Markdown w `regulamin/`. Sekcja TOML `[milestones]` definiuje liczbę dni przed początkiem zawodów: `otwarcie = 90`, `karty = 75`, `propozycja = 60`, `zawody = 0`. Znacznik `{{term:karty}}` wyświetla `T−75`, a `{{days:karty}}` wyświetla `75`. Zmiana wartości w jednym miejscu aktualizuje terminy w przepisach i tabelach przy kolejnym generowaniu DOCX. W podglądzie Markdown na GitHubie znaczniki pozostają widoczne jako odwołania do tych definicji.

Blok `{{table:timeline-process}}` poprzedza zwykłą tabelę Markdown z kolumnami `Termin`, `Zdarzenie`, `Zakres`. Każdy wiersz to etap. W DOCX generator obraca tę tabelę w poziomy schemat: etapy są kolumnami, z kolorowymi terminami u góry. To edytowalne komórki Worda, bez obrazu i bez dodatkowego HTML. Schemat pokazuje kolejność etapów, nie odległości w skali czasu. Obsługuje 2–4 etapy, mieszczące się na szerokości strony; terminy muszą występować w kolejności chronologicznej.

Pozostałe bloki `{{table:process}}`, `{{table:responsibilities}}` i `{{table:data-sources}}` są tabelami Markdown renderowanymi jako tabele Worda. Obsługiwane są 2–4 kolumny. Zmiany wprowadza się w Markdown; ręczna edycja DOCX zostanie zastąpiona kolejnym buildem.

Po zmianie uruchom `python -m narzedzia.prepare_regulamin normalize-and-build <źródło.md> <wynik.docx>`. Nieznany termin, niepoprawna liczba dni, nierówne wiersze tabeli albo błędna kolejność etapów zatrzymują generowanie. Poprzedni DOCX pozostaje zachowany. CI wykonuje te same kontrole i publikuje kandydacki dokument do przeglądu.

## Wersjonowanie i wydania

- Katalog `regulamin/` zawiera jedną aktualną wersję roboczą.
- Numer wersji i status są zapisane również wewnątrz dokumentu.
- Katalog `wydania/` otrzymuje kopię dopiero po formalnym zatwierdzeniu regulaminu.
- Nazwa zatwierdzonego pliku wskazuje sezon i wersję, a odpowiadający jej tag Git pozwala odtworzyć kod, testy oraz Rejestr Decyzji z chwili publikacji.
- Zatwierdzonego wydania nie zastępuje się w miejscu; korekta otrzymuje nowy numer wersji.

## Jawność, prywatność i licencja

Repozytorium jest publiczne. Nie wolno publikować prywatnej korespondencji, danych kontaktowych, danych wrażliwych ani materiałów osób trzecich bez potwierdzenia prawa do ich publikacji.

Przed dodaniem DOCX należy sprawdzić komentarze, śledzone zmiany i metadane. W kartach decyzji zapisujemy uzgodnione streszczenia argumentów, nie prywatne transkrypcje rozmów.

Repozytorium nie ma obecnie licencji. Publiczna widoczność kodu i dokumentów nie oznacza automatycznie udzielenia zgody na ich kopiowanie albo ponowne wykorzystanie.

## Strona publiczna

[Otwórz Rejestr Decyzji w GitHub Pages](https://fencer4life.github.io/Regulamin_Kadry-SPWS/?strona=1&na_stronie=20)
