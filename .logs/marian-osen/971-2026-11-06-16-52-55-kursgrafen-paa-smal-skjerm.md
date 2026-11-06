# Kursgrafen på smal skjerm

## 2026-11-06 kl. 16:52 — Marian Osen

### Oppgave
Story 8.2c etter gruppens svar 6.11 kl. 15:08: kursgrafen får egne mål på smal skjerm, så teksten i den ved 390 px er minst like stor som den minste teksten ellers på siden, uten vannrett rulling. Brede vinduer som før, og bildene ved 1280 px byte for byte de samme. På egen gren med PR, flettet før kl. 21:20 hvis alt er grønt.

### Plan
- Instruksjonen kl. 15:10 i dagsfila, avgjørelsen under story 8.2c, 8-2c in-progress og 9.2-punktet krysset av i `issues.md`.
- Grenen i en egen worktree. Oppslag i `src/graf.py`, `aksje.html`, `stil.css`, spørsmål 8 og ECH6 i spesifikasjonen 8.2b.
- Måling i Edge før og etter, med en demoserver og demobasen i en midlertidig mappe, ved de ti breddene fra 8.2b.
- Hele settet alene før hver commit med kode, mutant per commit med kode, gjennomgang med Blind Hunter, Edge Case Hunter og Verification Gap, CI, og fletting.
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-8-2c-kursgrafen-paa-smal-skjerm.md`.

### Resultat
- Main: `86febf83` (instruksjonen) og `abf65895` (avgjørelsen, 8-2c in-progress og 9.2-punktet krysset av).
- Grenen: `8bfc9885` (`graf.py`: `bygg_graf(smal=True)`, 280 × 250, forklaring under datoene, navn på aksen uten overlapp), `ccbbe0df` (siden viser den smale når figuren er smalere enn 690 px, og hjelpen), `b4cc5c44` (spesifikasjonen), `67596cb8` (rettingene etter gjennomgangen), `fbfd64db` (triagen), `b93bc5da` (siste børsdag i testen i nettleseren) og `25fa0b35` (standardsiden er 6 mnd, ikke siste børsdag).
- PR #115, squash-flettet kl. 16:29 i `b38617f9`, låst til head-en `25fa0b35`. Grenen er slettet på GitHub og lokalt, og worktreen er fjernet. Bildene til PR-en står på `pr-8-2c-bilder` (`146b2435`), bare fra demoen.
- Målt i Edge, standardsiden, siste børsdag, 01.10 og 1 uke for BRFE: teksten i grafen ved 390 px er 13,37 px (var 5,2), ved 360 px 12,09 (var 4,7) og ved 320 px 10,37 (var 4,03). Den minste teksten ellers er 11,5 px. Ingen tekst utenfor grafen, ingen overlapp og ingen vannrett rulling i noen av målingene.
- Hele settet: 4231, 4237, 4254 og 4257 bestått, 24 hoppet over, og bare porttester for `start.ps1` som feilet (7, 7, 3 og 2). Den første kjøringen før `ccbbe0df` feilet også i sju tester fordi endringene ikke var ferdige, og de ble rettet.
- Mutantene M1–M3 er fanget, og filene var lik HEAD etter hver.
- Gjennomgangen: Blind Hunter 13, Edge Case Hunter 5 og Verification Gap 3 funn, ingen på høy. Alle på middels er rettet, utenom BH3, som er avvist med oppslag. BH10, BH12 og ECH5 (lave) står med grunnen.
- Alle sju bildene i `docs/appen/` er tatt på nytt etter hver endring og er byte for byte de samme. Bare avtrykkene i `test_docker.py` er satt.
- CI grønn på head-en (42243101765) og på flettecommiten (42243561704). Etter flettingen: `de14f236` (spesifikasjonen done, Ferdig-linja under 8.2c, 8-2c done og radene i §3, §5 og vedlegget i kvalitetssikringen). `issues.md` hadde ingen åpne punkter om 8.2c.
- `src/fetch_prices.py` er ikke kjørt, og `data/db/ose.db`, oppgaven, worktreen `G74-lund-osen-jobb` og `_privat/` er ikke rørt. Demobasene lå i midlertidige mapper, og alle demoserverne er stoppet.

### Åpne punkter
- Gruppen kan se på valget i spesifikasjonen: i et vindu på om lag 451–767 px er den smale grafen 373 px bred og midtstilt, med luft på sidene, i stedet for den brede med tekst under 11,5 px.
- Ved 320 px er teksten i grafen 10,37 px, under 11,5 px (BH10). Kravet gjaldt 390 px.
