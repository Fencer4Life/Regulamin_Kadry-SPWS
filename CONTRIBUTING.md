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

Wspólna redakcja Word odbywa się przez OneDrive. Do Git trafia uzgodniona migawka, nie każda automatyczna wersja pliku.

## Kontrola przed wysłaniem

```bash
source .venv/bin/activate
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
