# Automatyczna karta decyzji

Nie twórz ani nie uzupełniaj karty ręcznie. Wszystkie dane wpisz w opisie dyskusji:

- **Fragment Markdown do zastąpienia** — dokładny fragment z widoku Code lub Raw źródła, ze znacznikami i wcięciami.
- **Nowe brzmienie Markdown** — kompletne zastępstwo. Zachowaj identyfikatory; odsyłacz i komentarz ref pozostają razem.
- **Uzasadnienie** — uzgodniony powód decyzji; automat kopiuje tekst dosłownie, nie streszcza komentarzy.

Po etykiecie `rozstrzygnięta` na dyskusji automat tworzy kartę oraz draft PR.
Na PR nadaj `wdrażaj`. Przed wdrożeniem automat odświeża dane z dyskusji.
Nie zaznaczasz Tak/Nie i nie przepisujesz pól do karty.
Poczekaj na DOCX do sprawdzenia oraz zielone CI, otwórz dokument i dopiero potem scal PR.

Jedna decyzja zawiera jedną parę fragmentów; dla kilku zmian wybierz wspólny ciągły fragment.
Przy usuwaniu przepisu obejmij fragmentem sąsiednią treść, którą zachowasz w nowym polu.

Dla decyzji bez zmiany dokumentu pozostaw oba fragmenty puste oraz podaj **Proponowane rozwiązanie** i **Uzasadnienie**.
Nie nadawaj wtedy `wdrażaj`.

Po wdrożeniu kolejną zmianę zgłoś w nowej dyskusji. Historyczne karty zachowują stary format.
