# Zasady współpracy

## Zakres

Repozytorium służy wspólnej pracy nad projektem regulaminu, jego załącznikami, Rejestrem Decyzji i narzędziami kontrolnymi. Zmiana techniczna nie otrzymuje numeru DR, jeżeli nie rozstrzyga treści, konstrukcji albo interpretacji regulaminu.

## Zanim rozpoczniesz zmianę

1. Sprawdź aktualne GitHub Discussions, otwarte Pull Requesty i Rejestr Decyzji.
2. Dla propozycji regulaminowej opisz problem, cel, rozważane warianty i przewidywane konsekwencje.
3. Nie nadawaj samodzielnie numeru DR, dopóki propozycja nie zostanie zakwalifikowana przez komisję.
4. Nie publikuj danych prywatnych ani materiałów zewnętrznych bez prawa do publikacji.

## Gałąź i Pull Request

- Utwórz krótką gałąź tematyczną z aktualnego `main`.
- Jeden Pull Request powinien przedstawiać jedno spójne rozstrzygnięcie albo jeden etap techniczny.
- W opisie wskaż problem, zmienione pliki, numer decyzji — jeżeli dotyczy — oraz wykonane testy.
- Nie łącz zmiany, jeżeli testy nie przechodzą albo dyskusja nad treścią nie została rozstrzygnięta.

## Zmiana treści regulaminu

Zmiana normatywna powinna obejmować łącznie:

1. zaktualizowany DOCX;
2. kartę decyzji albo wskazanie istniejącej decyzji;
3. test chroniący dokładne brzmienie lub inną mierzalną właściwość, jeżeli jest to zasadne;
4. aktualizację załącznika, README albo dokumentacji, jeżeli zmiana wpływa na te materiały.

Treść redaguje się wyłącznie w kanonicznym Markdown. DOCX służy do kontroli w Microsoft Word i jest zawsze generowany ponownie.

### Markdown → DOCX

Źródłem kanonicznym jest kontrolowany Markdown. Pull Request treściowy zawiera Markdown, kartę decyzji i wygenerowany z niego DOCX. CI tworzy dodatkowy kandydacki DOCX, uruchamia na nim testy oraz porównanie parytetu, a wynik udostępnia jako artefakt.

Recenzja dokumentu ma miejsce w Pull Requeście: Redaktor pobiera kandydat z Actions lub otwiera DOCX z PR w Microsoft Word, następnie wybiera `Approve` albo `Request changes`. Dopiero po `Merge` Release publikuje zaakceptowaną wersję. Release nie jest bramką do odrzucania pliku, ponieważ po scaleniu zmiana już znajduje się w `main`.

Pełna ścieżka zaczyna się od etykiety `rozstrzygnięta`. Automat tworzy kartę DR i draft PR, a Redaktor uzupełnia uzasadnienie, zaznacza `Tak` albo `Nie` i — gdy Regulamin ma się zmienić — opracowuje nowe brzmienie Markdown. Następnie uruchamia normalizację i generator:

```bash
python -m narzedzia.prepare_regulamin normalize-and-build \
  regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md \
  regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx
```

Przed commitem należy uruchomić tryb bez zapisu:

```bash
python -m narzedzia.prepare_regulamin verify \
  regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md \
  regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx
```

### Semantyczny Markdown ZTP

- Rozdział zapisuje się jako `## [chapter:stabilny-id] Tytuł`, a paragraf jako `### [section:stabilny-id] Tytuł`.
- Każda jednostka zawiera `[unit:stabilny-id]`. Widoczne numery są wynikiem normalizacji i nie stanowią tożsamości przepisu.
- Kolejne poziomy to: ustęp `1.`, punkt `1)`, litera `a)`, tiret `-` oraz podwójne tiret `--`.
- Paragraf zawierający jedną myśl zapisuje się bez sztucznego `1.`.
- Odesłanie ma postać `{{ref:id-paragrafu/id-jednostki}}`; generator wyświetla aktualny numer.
- `accepted` jest statusem domyślnym. `[status:source-draft]` oznacza ciemnoszary brudnopis ze źródła, a `[status:placeholder]` jawne miejsce wymagające decyzji.
- Automat może poprawiać strukturę, numerację i interpunkcję wyliczeń. Nie wolno używać go do samodzielnej zmiany słów lub sensu przepisu.

Szybka ścieżka zaczyna się od etykiety `redakcja-bez-zmiany-sensu`. W dyskusji muszą być wypełnione pola `Fragment Markdown do zastąpienia` i `Nowe brzmienie Markdown`. Automat wymaga dokładnie jednego wystąpienia starego fragmentu, sam zmienia Markdown, buduje i testuje DOCX, tworzy kartę DR oraz draft PR. Brak, wielokrotne wystąpienie, nieudany build albo test zatrzymują proces przed pushnięciem zmiany.

W obu ścieżkach Redaktor otwiera run `CI` przypisany do PR, pobiera `regulamin-candidate` z sekcji `Artifacts`, otwiera DOCX w Microsoft Word i sprawdza treść oraz układ. `Approve` i `Merge` przyjmują wersję; `Request changes` albo zamknięcie PR pozostawiają `main` bez zmian.

## Kontrola przed wysłaniem

```bash
source .venv/bin/activate
python -m narzedzia.prepare_regulamin verify \
  regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.md \
  regulamin/Regulamin-powolywania-Reprezentacji-Polski-Weteranow-w-szermierce_2026.docx
python narzedzia/sanitize_docx_metadata.py
python -m unittest discover -s tests -v
git diff --check
```

Przed commitem sprawdź, czy repozytorium nie zawiera `~$*.docx`, `*.backup-*.docx`, `.DS_Store`, prywatnych danych ani niezatwierdzonych materiałów źródłowych.

## Recenzja

Recenzent sprawdza osobno:

- zgodność proponowanego brzmienia z decyzją;
- spójność zmienionych postanowień z całym regulaminem;
- kompletność uzasadnienia i alternatyw;
- zgodność DOCX z testami i zasadami publikacji;
- brak niezamierzonych zmian technicznych lub redakcyjnych.
