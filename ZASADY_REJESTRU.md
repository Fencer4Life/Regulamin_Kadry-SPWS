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
5. Powstaje karta Markdown ze statusem `w dyskusji` oraz Pull Request.

Numer raz nadany nie jest używany ponownie. Karta decyzji odrzuconej pozostaje w rejestrze.

## Statusy

- `projekt` — zapis roboczy przed rozpoczęciem formalnej dyskusji;
- `w dyskusji` — zbierane są argumenty i warianty;
- `do zatwierdzenia` — dyskusja została podsumowana, a proponowane rozstrzygnięcie oczekuje na decyzję;
- `przyjęta` — rozstrzygnięcie zostało zaakceptowane do projektu regulaminu;
- `odrzucona` — wariant nie został przyjęty, ale pozostaje w historii;
- `wstrzymana` — rozstrzygnięcie odłożono do czasu spełnienia wskazanego warunku;
- `zastąpiona` — późniejsza decyzja przejęła zakres wcześniejszej decyzji.

## Zawartość karty

Każda karta zawiera metadane identyfikujące decyzję oraz sekcje: Problem, Kontekst, Dyskusja, Rozważane warianty, Decyzja, Uzasadnienie, Konsekwencje, Odrzucone alternatywy, Plan oceny, Ocena po sezonie i Historia zmian.

Nie wolno uzupełniać uzasadnień z wyobraźni. Jeżeli argument nie został utrwalony w rozmowie, dokumencie, Discussion, Pull Requeście albo historii Git, zapisujemy: „nieodnotowane w materiale źródłowym”.

## Przyjęcie i zmiana decyzji

Zmiana merytoryczna przyjętej decyzji wymaga nowej decyzji albo jawnego wskazania decyzji zastępującej. Pola `zastepuje` i `zastapiona_przez` muszą tworzyć wzajemne powiązanie.

Korekta oczywistej omyłki może zostać wykonana bez nowego numeru, jeżeli nie zmienia sensu rozstrzygnięcia. Zakres korekty należy opisać w historii zmian karty.

## Ocena po sezonie

Każda decyzja wymagająca weryfikacji zawiera mierzalny plan oceny i termin przeglądu. Po zakończeniu sezonu karta jest uzupełniana o obserwowane skutki, dane, problemy oraz rekomendację: utrzymać, zmienić albo zastąpić rozwiązanie.

## Odpowiedzialność

Komisja regulaminowa SPWS formalizuje rekordy i zmienia ich status. Publiczna dyskusja i recenzja pomagają przygotować rozstrzygnięcie, ale nie zastępują decyzji komisji ani formalnego zatwierdzenia regulaminu przez właściwy organ PZSz.
