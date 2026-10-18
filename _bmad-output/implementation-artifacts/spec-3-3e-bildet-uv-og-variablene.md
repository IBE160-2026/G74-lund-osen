---
title: 'Story 3.3e: bildet av oversikten, uv i «Tester» og variablene i .env'
type: 'docs'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a2965ba'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3b-readme-for-sensor.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** README-en har ikke lenger bildet av oversikten (tatt ut 16.10 kl. 21:38), «Tester» sier ikke hvordan uv installeres eller hvor lang tid testene tar, og ingenting forklarer variablene i `.env` samlet.

**Grunnlaget:** instruksjonen 18.10 kl. 21:11, gruppens svar 18.10 kl. 00:20 (bildet kommer tilbake etter 3.4b, i en README-PR som stopper før flettingen) og kl. 20:39 («Tester» står der den står, og får installasjonen av uv og tiden). PR-en stopper før flettingen og venter på ja.

*Rettet 2026-10-18 (gjennomgangen, VG11):* `baseline_commit` sier `a2965ba`, men grenen går ut fra `615e7b9`, der denne spesifikasjonen ble committet.

## Kontrollpunktene

- a) `docs/bilder/readme/oversikten-demo.png` er tatt etter fremgangsmåten under «Bildet» i spesifikasjonen for 3.3b, på en ledig port, uten å stoppe noen server eller røre åpne Edge-vinduer. Bare demoen, med «Eksempeltall» synlig, uten sti eller brukernavn. Plassen, alt-teksten og teksten under er som i 3.3b. Testene fra 3.3b er tilbake, med avtrykket av alt som endrer det bildet viser, også stilarket, og feilmeldingen sier hvordan bildet tas på nytt. Testene for bildene godtar de tre i «Kom i gang», dette og CI-merket, og ingen flere. «Mappestruktur» nevner det.
- b) «Tester» har installasjonen av uv før `uv sync`: én boks for Windows (PowerShell) og én for Mac (Terminal), fra https://docs.astral.sh/uv/getting-started/installation/, og et nytt vindu i mappa, som i steg 4, hvis uv ikke blir funnet. Etter kommandoene: første `uv sync` laster ned Python og pakkene, og hvor lenge testene tar, i hele minutter. «Uten Docker, med uv» viser til installasjonen i «Tester». `docs/hjelp.md` har spørsmålet om at uv ikke blir funnet, med samme svar.
- c) En knapp «Variablene i .env» under «Mer for den som vil», med en tabell over de tre i `.env.example`: variabelen, hva den gjør, standarden og når den trengs. Én setning om at `OSE_DEMO` og `OSE_I_DOCKER` settes av `compose.yaml` og `Dockerfile` og ikke skal i `.env`. Steg 6 i «Den ekte versjonen» viser dit.
- d) Testene, med «Ville feilet hvis», og mutantene: et bilde til i README-en, en mal endret uten nytt bilde, Mac-boksen tatt ut, og en variabel i `.env.example` som ikke står i tabellen.

## Planen, én commit per punkt

1. a) Bildet, testene for det og «Mappestruktur».
2. b) uv i «Tester», henvisningen fra «Uten Docker, med uv», og spørsmålet i `docs/hjelp.md`.
3. c) Tabellen over variablene og henvisningen fra steg 6.
4. d) Testene for b og c.

## Avgjort i spesifikasjonen

- **Avtrykket bak bildet** dekker malene oversikten bygges av (`index.html`, `_ramme.html` med stilarket i `<style>`, `_brikker.html`, `_bransjer.html` og `_hjelp.html`), skriftene i `src/static/`, demodataene (`src/demo.py`) og modulene som lager det oversikten viser (`markedsoversikt.py`, `oversiktsdata.py`, `hovedindeks.py` og `tallformat.py`). `app.py` er ikke med: den har ruter og logikk for alle sidene, og en endring der ville krevd et nytt bilde hver gang.
- **Tiden for testene** tas fra kjøringene av hele settet på denne maskinen i dag (dagsfila 18.10).

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe. Den ekte `.env` leses ikke.
- Ingen server som kjører, stoppes, og åpne Edge-vinduer røres ikke.

## Avgjort underveis

- **Bildet** er tatt 18.10 kl. 21:15 med fremgangsmåten under «Bildet» i spesifikasjonen 3.3b. Teksten der sier «tatt 16.10» om bildet fra før (gjennomgangen, VG3). Demobasen lå i en midlertidig mappe, waitress på en ledig port (63214), og Edge kjørte uten vindu med egen `--user-data-dir`. Ingen server ble stoppet, og `data/db/demo.db` ble ikke laget. Bildet er 1280 × 1000 px, med bare `IHDR`, `IDAT` og `IEND`.
- **Avtrykket bak bildet** dekker etter gjennomgangen også `signalberegning.py`, `hjelpetekster.py`, `boersdag.py`, `indeksdata.py` og `kursdata.py`, hver delmal (`_*.html`) og merket «Eksempeltall» fra `app.py`. Fra `src/static/` telles bare skriftfilene. Det endrer linja over om hva avtrykket dekker. Avtrykket fikk en ny verdi fordi det dekker flere filer, ikke fordi noe bildet viser er endret: ingen fil under `src/` er endret på grenen.
- **Tiden for testene:** commitmeldingen i `c145939` sa 219–434 s og «mellom 4 og 7 minutter». 434 s var den første kjøringen av hele settet for 3.4b, som ikke står med tid i dagsfila. Tidene som står der, er 219–385 s, og README-en sier nå «mellom 4 og 6 minutter» (gjennomgangen, BH1, VG2 og ECH5).

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. E1–E4 er fra instruksjonen, fanget på `1f99e3f` og `c779779`. E5–E7 er for funnene med dom medium, fanget på `c779779`:
- E1, et bilde til i README-en: `test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket`.
- E2, `index.html` endret uten nytt bilde: `test_bildet_tas_paa_nytt_naar_oversikten_endres`.
- E3, Mac-boksen tatt ut: `test_testene_uten_docker`.
- E4, en variabel i `.env.example` som ikke står i tabellen: `test_variablene_i_tabellen_er_de_i_env_example`.
- E5, `TERSKEL` endret i `signalberegning.py` uten nytt bilde (VG1, ECH1): `test_bildet_tas_paa_nytt_naar_oversikten_endres`. Første forsøk traff ikke linja, som har en kommentar etter tallet, og ble kjørt på nytt.
- E6, «mellom 4 og 7 minutter» tilbake (BH1, VG2): `test_installasjonen_av_uv_staar_foer_uv_sync`.
- E7, en feil standardadresse til Ollama i tabellen (BH3): `test_porten_er_den_samme_overalt_og_ikke_5000`, og `test_standardene_i_tabellen_er_de_i_koden` alene med `-k`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `615e7b9..1f99e3f`, med bildet som stat. Linsene var Blind Hunter (BH, 12 funn, bare diffen), Edge Case Hunter (ECH, 11, der ECH4 ikke fant noen feil) og Verification Gap (VG, 11). Ingen av dem kjørte pytest, en server, Edge eller Docker. Fem rader har dom medium. Fire er rettet i `c779779`, og BH11 er avvist med beviset under.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, VG2, ECH5 | «mellom 4 og 7 minutter» hadde ingen kilde for 7 | medium | patch: 4–6 minutter fra dagsfila, og testen låser tallene. E6 |
| BH6, VG1, ECH1, ECH2, ECH3 | Avtrykket manglet signalberegningen, hjelpetekstene og andre moduler, nye delmaler og merket, og tok med filer som ikke vises | medium | patch: over. E5 |
| BH2 | Standarden for `OSE_KI_TJENESTE` sa ikke hva som gjelder etter steg 6 | medium | patch: `av` etter steg 6, og en tom verdi gir ingen KI-tekst |
| BH3 | Standardene i tabellen var ikke testet | medium | patch: `test_standardene_i_tabellen_er_de_i_koden`. E7 |
| BH11 | Commitene for b og c skulle ha latt testene være røde | medium | avvist: `git show --stat c145939` og `5a97db5` endrer `tests/test_docker.py` i samme commit (17 og 4 linjer), og `1f99e3f` legger bare til de nye testene fra punkt d |
| BH4, ECH6 | Lesingen av `.env.example` og sjekken «leses i src/» | low | patch: `export` og mellomrom før `=`. At navnet kan stå i en docstring, er avvist: `src/` har ingen underpakker, og tabellen testes mot koden i BH3 |
| BH8, ECH10 | Ingen test for tekstfelt i PNG-fila | low | patch: `test_bildet_har_ingen_tekstfelt`. At siden viser årstallet fra 2027, er avvist: README-en leveres før det |
| VG3 | 3.3b sier «tatt 16.10» | low | patch: forklart over |
| VG4 | «Mappestruktur» ble ikke testet for bildet | low | patch |
| VG5, ECH7 | `--demo` med uv, og en tom verdi | low | patch: i tabellen og setningen under |
| VG7 | «med to kommandoer» under «Til faglærer» | low | patch: «etter at uv er installert» |
| VG8 | Mutantene var ikke ført | low | patch: over |
| VG10 | «kan ta noen minutter» om første `uv sync` hadde ingen kilde | low | patch: tatt ut |
| VG11 | `baseline_commit` | low | patch: Rettet-linje |
| ECH8 | Svaret om «is not recognized» nevnte ikke `uv` | low | patch: samme setning i README-en og `docs/hjelp.md`. Overskriften på engelsk står: det er meldingen slik den kommer |
| ECH11 | Docstringene sa tre bilder | low | patch. Vurderingsmatrisen og kvalitetssikringen får sine linjer når PR-en flettes |
| BH5 | Teksten under bildet står uten tom linje | low | avvist: som i 3.3b, slik instruksjonen sier |
| BH7 | Feilmeldingen gir den nye verdien | low | avvist: den sier også hvordan bildet tas, og gjennomgangen ser bildet i PR-en |
| BH9 | «som i steg 4» på Mac | low | avvist: steg 4 har både Windows og Mac |
| BH10, VG6, ECH9 | Lenken på `.env` går til overskriften | low | avvist: en `<details>` har ikke noe anker på GitHub, og steg 6 har 65 ord |
| BH12 | Bildet skyver «Kom i gang» ned | low | avvist: plassen er fra 3.3b, som instruksjonen sier |
| VG9 | Installasjonskommandoene kan ikke sjekkes uten nett | low | avvist: de er ordrett fra instruksjonen og siden den viser til |
