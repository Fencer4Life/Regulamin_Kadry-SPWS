# Regulamin Kadry SPWS

Publiczne repozytorium prac nad **Regulaminem powoływania reprezentacji Polski weteranów w szermierce** na sezon 2026/2027. Łączy aktualny dokument Word, narzędzia kontrolujące jego strukturę oraz Rejestr Decyzji wyjaśniający przyjęte rozwiązania i rozważane alternatywy.

## Status projektu

| Pole | Wartość |
|---|---|
| Sezon | 2026/2027 |
| Wersja dokumentu | 0.1 |
| Status | projekt do konsultacji |
| Stan treści | zatwierdzono roboczo § 1–§ 6 oraz załącznik nr 1; dalsze postanowienia wymagają uzgodnienia |

> **Ważne:** dokument znajdujący się w tym repozytorium jest projektem. Nie stanowi obowiązującego regulaminu do czasu jego formalnego zatwierdzenia przez właściwy organ Polskiego Związku Szermierczego.

## Najważniejsze dokumenty

- [Aktualny projekt regulaminu w formacie MS Word](regulamin/Regulamin-powolywania-reprezentacji-Polski-weteranów-w-szermierce_2026.docx)
- [Rejestr Decyzji — widok HTML](index.html)
- [Załącznik nr 1 — pełna tabela punktacji dla stawek od 4 do 300 zawodników](zalaczniki/Zalacznik-1-tabela-punktacji-SPWS_2026-2027.html)
- [Informacja o zatwierdzonych wydaniach](wydania/README.md)
- [Kalkulator punktów SPWS](https://fencer4life.github.io/spws-automated-ranklist/kalkulator-punktow.html?lang=pl)
- [Zasady prowadzenia Rejestru Decyzji](ZASADY_REJESTRU.md)
- [Przewodnik: jak pracujemy nad regulaminem](przewodnik.html)
- [Zasady współpracy](CONTRIBUTING.md)

## Role SPWS i PZSz

**Stowarzyszenie Polskich Weteranów Szermierki (SPWS)** przygotowuje projekt, prowadzi konsultacje i dokumentuje decyzje podejmowane podczas prac.

**Polski Związek Szermierczy (PZSz)** jest podmiotem, któremu projekt ma zostać przedstawiony do formalnego zatwierdzenia przez właściwy organ. Samo opublikowanie projektu przez SPWS ani połączenie zmian z gałęzią `main` nie oznacza zatwierdzenia regulaminu przez PZSz.

## Źródło aktualnej treści

Wspólna redakcja treści odbywa się w programie Microsoft Word z wykorzystaniem OneDrive. Łącza i uprawnienia do dokumentu współdzielonego są przekazywane członkom zespołu poza publicznym repozytorium.

Plik w katalogu `regulamin/` jest zaakceptowaną migawką aktualnej wersji roboczej. GitHub przechowuje historię uzgodnionych migawek, kod i testy. Po zmianie dokonanej w Wordzie osoba przygotowująca Pull Request:

1. przyjmuje albo świadomie pozostawia śledzone zmiany;
2. usuwa komentarze i metadane nieprzeznaczone do publikacji;
3. zastępuje plik w `regulamin/` nową migawką;
4. aktualizuje właściwą kartę decyzji oraz testy;
5. opisuje w Pull Requeście zakres i podstawę zmiany.

Plik DOCX jest binarny i GitHub nie pokazuje jego zmian równie czytelnie jak zmian tekstowych. Dlatego każde rozstrzygnięcie dotyczące treści powinno mieć odpowiadającą mu kartę w Rejestrze Decyzji.

## Struktura repozytorium

| Ścieżka | Przeznaczenie |
|---|---|
| `regulamin/` | aktualna uzgodniona migawka projektu DOCX |
| `wydania/` | formalnie zatwierdzone, niezmienne wersje sezonowe |
| `_decyzje/` | źródłowe karty decyzji w Markdown |
| `zalaczniki/` | publiczne załączniki i materiały stanowiące część projektu |
| `narzedzia/` | kod Python do tworzenia i kontrolowanych zmian DOCX |
| `tests/` | testy treści, stronicowania, bezpieczeństwa DOCX i kompletności rejestru |
| `_layouts/`, `_includes/`, `assets/` | szablony strony Rejestru Decyzji |
| `.github/` | formularze współpracy i automatyczna walidacja |

Automatyczne kopie DOCX, pliki blokady Worda, wynik `_site/` oraz środowisko `.venv/` nie są wersjonowane.

## Jak współpracować

Zmianę rozpoczyna dyskusja ze wskazanym Koordynatorem dyskusji i opisem problemu. Po uzgodnieniu wyniku koordynator publikuje formularz rozstrzygnięcia. Automatyzacja waliduje formularz, nadaje trwały numer `DR-NNN` i tworzy roboczy Pull Request. Karta decyzji oraz — jeżeli decyzja tego wymaga — zmiana dokumentu Word są przeglądane razem.

Skrócony przebieg:

1. zgłoszenie problemu w GitHub Discussions;
2. dyskusja komisji nad wariantami i konsekwencjami;
3. formularz rozstrzygnięcia opublikowany przez koordynatora;
4. automatyczne przygotowanie karty decyzji i draft Pull Requestu;
5. wprowadzenie zmiany DOCX przez Redaktora regulaminu, jeżeli jest wymagana;
6. przegląd i scalenie dokumentacji oraz treści;
7. publikacja i ocena skutków po zakończeniu sezonu.

Pełny proces opisuje [przewodnik dla komisji](przewodnik.html), reguły dokumentowania zawierają [Zasady prowadzenia Rejestru Decyzji](ZASADY_REJESTRU.md), a instrukcję techniczną przygotowania zmian — [CONTRIBUTING.md](CONTRIBUTING.md).

## Praca z dokumentem Word

- Nie edytuj równolegle tej samej kopii DOCX poza uzgodnioną sesją OneDrive.
- Włącz kontrolę zmian, jeżeli dokument ma być przekazany do recenzji językowej lub prawnej.
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

`generate_regulamin_docx.py` jest generatorem pierwotnego prototypu, a kolejne skrypty `apply_*.py` dokumentują kontrolowane etapy dotychczasowej pracy. Aktualny DOCX zawiera również późniejsze poprawki wykonane w Wordzie, dlatego nie należy traktować samego generatora jako jedynego źródła całego dokumentu.

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
