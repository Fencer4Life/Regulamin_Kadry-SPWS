# Zasady prowadzenia Rejestru Decyzji

## Cel rejestru

Rejestr Decyzji dokumentuje, dlaczego przyjęto dane rozwiązanie regulaminowe, jakie warianty rozważono oraz według jakich kryteriów jego skutki będą oceniane po sezonie. Ułatwia również przygotowanie zmian na kolejne sezony bez utraty wcześniejszego kontekstu.

## Co jest decyzją regulaminową

Numer DR otrzymuje samodzielne rozstrzygnięcie dotyczące treści, konstrukcji albo interpretacji regulaminu, które ma własne uzasadnienie lub własny warunek ponownej oceny.

Numeru DR nie otrzymują poprawki literowe, zmiany fleksyjne, techniczne ponowienia zapisu, stronicowanie, wybór narzędzi, konfiguracja CI ani sposób publikowania strony. Takie zmiany są opisywane w commicie, Pull Requeście lub dokumentacji technicznej.

## Inicjowanie decyzji

1. Propozycja rozpoczyna się w GitHub Discussions.
2. Autor opisuje problem, kontekst, warianty i oczekiwany rezultat.
3. Komisja kwalifikuje propozycję jako decyzję regulaminową albo zmianę techniczną.
4. Po kwalifikacji komisja nadaje kolejny trwały numer `DR-NNN`.
5. Po oznaczeniu dyskusji etykietą `do rozstrzygnięcia` powstaje karta Markdown ze statusem `do zatwierdzenia` oraz roboczy Pull Request.
6. Scalenie Pull Requestu publikuje kartę, dodaje jej adres do dyskusji i zamyka dyskusję jako `rozwiązana`.

Dyskusję zakończoną bez rozstrzygnięcia zamyka się jako `nieaktualna` albo `duplikat`. Merytoryczne odrzucenie propozycji jest decyzją i otrzymuje kartę DR ze statusem `odrzucona`.

Numer raz nadany nie jest używany ponownie. Karta decyzji odrzuconej pozostaje w rejestrze.

## Statusy

- `projekt` — zapis roboczy przed rozpoczęciem formalnej dyskusji;
- `w dyskusji` — zbierane są argumenty i warianty;
- `do zatwierdzenia` — dyskusja została podsumowana, a proponowane rozstrzygnięcie oczekuje na decyzję;
- `przyjęta` — rozstrzygnięcie zostało zaakceptowane do projektu regulaminu;
- `odrzucona` — wariant nie został przyjęty, ale pozostaje w historii;
- `wstrzymana` — rozstrzygnięcie odłożono do czasu spełnienia wskazanego warunku;

Status opisuje wynik procesu i nie zmienia się tylko dlatego, że późniejsze rozstrzygnięcie wpłynęło na wcześniejsze.

## Stan obowiązywania i relacje

- `nie dotyczy` — decyzja nie została przyjęta;
- `obowiązuje` — aktualne ustalenie w pracach nad projektem;
- `częściowo zmieniona` — późniejsza decyzja zmieniła wskazaną część;
- `zastąpiona` — późniejsza decyzja przejęła całość rozstrzygnięcia.

Pola `zmienia`, `zmieniona_przez`, `zastepuje` i `zastapiona_przez` zawierają listy identyfikatorów decyzji. `zakres_zmiany` opisuje część zmienioną przez konkretną decyzję. Relacje muszą działać w obu kierunkach.

## Zawartość karty

Każda karta zawiera metadane identyfikujące decyzję oraz sekcje: Problem, Kontekst, Dyskusja, Rozważane warianty, Decyzja, Uzasadnienie, Konsekwencje, Odrzucone alternatywy, Plan oceny, Ocena po sezonie i Historia zmian.

Nie wolno uzupełniać uzasadnień z wyobraźni. Jeżeli argument nie został utrwalony w rozmowie, dokumencie, Discussion, Pull Requeście albo historii Git, zapisujemy: „nieodnotowane w materiale źródłowym”.

## Przyjęcie i zmiana decyzji

Zmiana merytoryczna przyjętej decyzji wymaga nowej decyzji. Zmiana częściowa korzysta z pól `zmienia` i `zmieniona_przez`; zmiana całkowita z pól `zastepuje` i `zastapiona_przez`.

Korekta oczywistej omyłki może zostać wykonana bez nowego numeru, jeżeli nie zmienia sensu rozstrzygnięcia. Zakres korekty należy opisać w historii zmian karty.

## Ocena po sezonie

Każda decyzja wymagająca weryfikacji zawiera mierzalny plan oceny i termin przeglądu. Po zakończeniu sezonu karta jest uzupełniana o obserwowane skutki, dane, problemy oraz rekomendację: utrzymać, zmienić albo zastąpić rozwiązanie.

## Odpowiedzialność

Komisja regulaminowa SPWS formalizuje rekordy i zmienia ich status. Publiczna dyskusja i recenzja pomagają przygotować rozstrzygnięcie, ale nie zastępują decyzji komisji ani formalnego zatwierdzenia regulaminu przez właściwy organ PZSz.
