---
title: 'Story 3.3 (3.3f): bildene av appen bak en knapp, i en egen mappe'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '88b305d'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3b-readme-for-sensor.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3e-bildet-uv-og-variablene.md'
---

## Intent

**Problem:** bildet av oversikten i demoen står under «Til faglærer» i README-en, i `docs/bilder/readme/` sammen med bildene fra «Kom i gang». Appen endres hele tiden, og det kommer flere bilder og senere en video av den.

**Grunnlaget:** gruppens svar 18.10 kl. 23:03 og instruksjonen 19.10 kl. 11:11. Det endrer plassen fra svaret 18.10 kl. 00:20 og svar 4 i spesifikasjonen for 3.4 (11.10).

## Kontrollpunktene

- a) Mappa: `docs/appen/` for bilder og video av appen, bare av demoen (regel 16). `oversikten-demo.png` flyttes dit med `git mv`, og testene og feilmeldingen om hvordan bildet tas, følger med. Bildene fra «Kom i gang» blir i `docs/bilder/readme/`. «Mappestruktur» nevner mappa.
- b) Knappen: rett under beskrivelsen, før «Innhold», en knapp «Bilder av appen (demoen)», lukket som de andre. Den har bildet av oversikten og et nytt bilde av aksjesiden for KVST i demoen, med grafen og KI-teksten, hvert med alt-tekst og en kort tekst under om at det er demoen med oppdiktede tall. Bildet under «Til faglærer» står ikke der lenger. Aksjesiden tas med samme fremgangsmåte, 1280 px bred og så høy at KI-teksten er med, uten sti, brukernavn eller tekstfelt i fila, og får sitt eget avtrykk av filene bak, så testen blir rød når siden endres, til bildet er tatt på nytt.
- c) Testene, med «Ville feilet hvis»: knappen står rett under beskrivelsen og er lukket; begge bildene ligger i `docs/appen/`, med alt-tekst og teksten under; bildene i README-en er de tre i «Kom i gang», disse to og CI-merket, og ingen flere; avtrykket for hvert bilde; mappa har bare bilde- og videofiler. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: en endret mal bak aksjesiden uten nytt bilde, knappen åpen som standard, og et bilde av appen utenfor `docs/appen/`.

## Planen, én commit per punkt

1. a) `git mv docs/bilder/readme/oversikten-demo.png docs/appen/`. `SKJERMBILDET` i `tests/test_docker.py` peker dit, så feilmeldingen følger med. Lenken i README-en og «Mappestruktur» får et eget punkt for `docs/appen/`, og testene for antallet punkter og lenker følger med. Bildet blir stående under «Til faglærer» til b.
2. b) Knappen `<details>` med `<summary>Bilder av appen (demoen)</summary>` mellom beskrivelsen og «Innhold», uten `open`, med de to bildene og en tekst under hvert. Bildet av aksjesiden heter `docs/appen/aksjesiden-kvst-demo.png` og tas med fremgangsmåten fra 3.3b: demobasen i en midlertidig mappe, `OSE_DEMO=1`, waitress på en ledig port og Edge uten vindu, 1280 px bred, med høyden målt til bunnen av KI-teksten. Avtrykket regnes som for oversikten, av filene bak aksjesiden: malen, delmalene, skriftene, demodataene med KI-tekstene, og modulene som lager tallene, grafen og tekstene, med hele `src/app.py`, fordi ruta bygger siden der.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Navnet på mappa** er `docs/appen/`, med bilder og video side om side, uten undermapper, så README-en lenker rett til fila.
- **Filtypene i mappa** er bilder (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`) og video (`.mp4`, `.webm`, `.mov`). Thumbs.db og .DS_Store hoppes over, som i `docs/bilder/`.
- **Bildet av aksjesiden** er tatt med KI på, som når siden åpnes første gang (FR-601), og med 6 mnd i grafen, siden slik den åpnes.

## Avgjort underveis

- **Bildet av aksjesiden** er 1280 × 1816. Høyden er målt i Edge uten vindu, etter at skriftene var lastet, til bunnen av grafen (`figure`, 1815,5 px), med bildeteksten. KI-teksten slutter ved 1144,6 px, så den er med. Målingen ga samme tall i et vindu på 1600 og 1816 px. Bildet ble tatt kl. 11:15 i b og på nytt kl. 11:22 etter rettingene (tidspunktene filene ble skrevet), likt byte for byte (sha256 `68c65a5fde0b2a5e…`). Bare avtrykket er nytt, fordi lista over filene ble lengre.
- **Teksten under bildet** står på linja rett under bildet, som under bildet av oversikten fra 3.3b og 3.3e, ikke som eget avsnitt som bildene i «Kom i gang».
- **«Innhold» rett under beskrivelsen** (3.3d, punkt f) står nå rett under knappen. Testen for rekkefølgen teller knappen som ett avsnitt.

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py` og `tests/test_readme.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. M1–M3 er fra instruksjonen og ble fanget på `1dee45a` og på nytt på `5891421`. N1 er for BH1 og ECH1, fanget på `5891421`:
- M1, en endret mal bak aksjesiden uten nytt bilde (lenketeksten øverst i `aksje.html`): `test_bildet_tas_paa_nytt_naar_aksjesiden_endres`.
- M2, knappen åpen som standard (`<details open>`): `test_knappen_staar_rett_under_beskrivelsen_og_er_lukket`.
- M3, et bilde av appen utenfor `docs/appen/` (bildet av aksjesiden flyttet til `docs/bilder/readme/`, med lenken): `test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket`.
- N1, `src/lagring_sqlite.py` ute av lista bak aksjesiden: `test_bildet_tas_paa_nytt_naar_aksjesiden_endres`, og for seg `test_avtrykket_dekker_modulene_appen_og_demoen_importerer`.

Første forsøk på å kjøre mutantene på nytt etter rettingene hadde en feil i mutantskriptet, så ingen mutant ble lagt inn, og alle testene gikk gjennom. Feilen ble funnet før noe ble ført, skriptet ble skrevet på nytt, og kjøringen over er den med mutantene lagt inn (`git status` viste endringen før hver kjøring).

## Gjennomgangen

Gjennomgang 19.10 på diffen `076305c..1dee45a`. Linsene var Blind Hunter (BH, 12 funn, bare diffen), Edge Case Hunter (ECH, 9, prøvd i en klon) og Verification Gap (VG, 5). Ingen av dem kjørte hele testsettet, en server eller et nettkall. To rader har dom medium, og begge er rettet i `c6006ac` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | Avtrykket for aksjesiden manglet lagringslaget og migrasjonene | medium | patch: `lagring_sqlite.py`, `migrering.py` og `migrasjoner/*.sql` med, og en test som krever at hver modul appen og demoen importerer, er med eller unntatt med grunn. N1 |
| VG1 | Mutantene var ikke ført | medium | patch: over |
| VG4 | Samme som BH1 | low | patch: se BH1. Avtrykket for oversikten har samme hull fra 3.3e og er ikke endret her |
| VG2, ECH6 | Docstringene sa at bildet står under «Til faglærer» | low | patch: docstringene sier hvor bildene står nå |
| VG3, ECH7 | Testen for «Mappestruktur» nevnte ikke `docs/appen/` | low | patch: punktet for mappa med begge bildene |
| VG5 | Vurderingsmatrisen sa sist at bildet står under «Til faglærer» | low | patch: datert linje i `5891421` |
| ECH5, BH8 | En video i `docs/appen/` godtas, men kan ikke lenkes uten at testene endres | low–medium | utsatt: videoen kommer før innleveringen. Da utvides testene for knappen og «Mappestruktur». Føres som åpent punkt |
| BH11 | Høyden er ikke testet mot innholdet | low–medium | avvist: høyden måles med fremgangsmåten, og endres innholdet, endres avtrykket, så bildet må tas og måles på nytt |
| BH2 | Testen for eget avtrykk er delvis dobbel | low | avvist: den sjekker at avtrykkene er ulike og at malen for hver side er med. Dekningen sjekkes nå av testen for modulene |
| BH3 | Teksten under bildet er ikke eget avsnitt | low | avvist: samme form som bildet av oversikten fra 3.3b, og avgjort over |
| BH4 | `<img>`, referanser og bilder etter «Mappestruktur» | low | avvist: README-testen godtar ikke `<img>` eller bilder med referanse (BH7 i 3.3c), og lista over alle bildene fanger et bilde til |
| BH5 | Feil i oppdelingen gir IndexError i stedet for en melding | low | avvist: testen feiler med navnet sitt og linja |
| BH6 | Sjekken for lukket godtar bare `<details>` | low | avvist: alle 11 i README-en er `<details>` (ECH8), og et annet attributt skal også ses på |
| BH7 | At bildet viser demoen, testes ikke på innholdet | low | avvist: bildet tas fra en demobase i en midlertidig mappe, og «Eksempeltall» står i stripa på bildet |
| BH9 | `TestBildeneIDocs` ser bare `docs/bilder/` | low | avvist: `docs/appen/` har sin egen test |
| BH10 | Rekkefølgetesten godtar hva som helst i knappen | low | avvist: innholdet testes i `TestBildeneAvAppen` |
| BH12 | Alt-teksten og teksten under sier det samme | low | avvist: som for bildet av oversikten i 3.3b. Alt-teksten er for skjermleseren, teksten under for den som ser bildet |
| ECH2 | `hovedindeks.py` og hele `app.py` gir falske alarmer | low | avvist: hele `app.py` står i spesifikasjonen, og `hovedindeks.py` er en modul appen importerer |
| ECH4 | `thumbs.db` med små bokstaver og `._`-filer | low | avvist: Windows skriver `Thumbs.db`, og `._`-filer kommer fra kopiering til exFAT, ikke fra git |
| ECH9 | `docs/` går med i byggekonteksten for Docker | low | avvist: utenfor 3.3f, og imaget får bare `src/` |
| ECH3 | CRLF og LF | – | ingen endring: samme avtrykk og samme svar på begge |
| ECH8 | Alle `<details>` er lukket | – | ingen endring |

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. Den ekte `.env` leses ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildene tas fra en demobase i en midlertidig mappe.
- Bildene viser bare demoen (regel 16).
- PR-en stopper før flettingen.
