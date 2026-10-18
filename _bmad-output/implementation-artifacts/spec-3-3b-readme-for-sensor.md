---
title: 'Story 3.3b: README-en for sensor'
type: 'docs'
created: '2026-10-16'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '1806484'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3-readme-slik-kjoerer-du-den.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md'
---

## Intent

**Problem:** README-en er det første sensor leser. «Status» sto stille fra 12.10 og nevnte ikke KI-delen på aksjesiden, ingen bilde viste hvordan appen ser ut, «Tester» sa ikke hvordan testene kjøres uten Docker, og «Kom i gang» sa ikke at demoen er veien for å se appen med en gang på dagtid en børsdag.

**Approach:** fem punkter, ett per commit, med testene for README-en rettet eller skrevet i samme commit.

## Beslutningene

Instruksjonen 16.10 kl. 15:59 (`docs/ai-prompts/2026-10-16.md`) sier at gruppen sa ja til de fem punktene 15.10 kl. 22:54. Svaret er ikke ført i dagsfila for 15.10 eller noe annet sted i repoet, så tidspunktet står her slik instruksjonen oppgir det. Punktene er beslutninger, med punkt d uten `--hent-foer-kl-22` etter svar 3 i [spesifikasjonen for 3.3](spec-3-3-readme-slik-kjoerer-du-den.md):

- **a) Statusen.** Det som er flettet siden sist, legges til med vanlige ord, og «Neste:» følger rekkefølgen i `epics.md`: resten av KI-laget først (svar 10 15.10 kl. 14:47), så rekkefølgen fra 14.10 kl. 22:19 og 22:25.
- **b) Et skjermbilde av oversikten i demoen,** 1280 px bredt (i `docs/bilder/readme/`, se «Mappa» under), med «Eksempeltall» synlig, i `docs/bilder/`, med en alt-tekst som sier at det er demoen. Demobasen lages i en midlertidig mappe, og serveren går på 127.0.0.1 med en ledig port, uten å stoppe servere som kjører. `test_ingen_bilder_utenom_ci_merket` godtar CI-merket og dette ene bildet, og ingen flere.
- **c) «Tester»:** hvordan testene kjøres på en ren maskin uten Docker, med uv og Python-versjonen fra `pyproject.toml`, `uv sync` og `uv run pytest`, og hva man skal se: alle består, og noen hoppes over på Windows, med grunnen. Ikke et fast testtall.
- **d) «Kom i gang»:** på dagtid en børsdag er demoen veien for å se appen med en gang. Steg 8 i den ekte versjonen og raden «Klar» i tabellen nevner også helgen, slik `docs/hjelp.md` gjør.
- **e) «Du trenger»:** versjonene, Docker Desktop slik den er prøvd, og Python for veien uten Docker.

*Lagt til 2026-10-16 kl. 16:34 (instruksjonen kl. 16:31):* ja-et 15.10 kl. 22:54 ble gitt i chatten med rådet, ikke i Claude Code, og derfor ikke ført i dagsfila. Kilden er instruksjonen 16.10 kl. 15:59 (`docs/ai-prompts/2026-10-16.md`). Dagsfila for 15.10 endres ikke.

Skjermbildet erstatter «uten bilder» (svar 4, 11.10). Regelen fra 25.09 står: bildet viser bare demoen, aldri ekte kurser (regel 16). Svar 3 i 3.3 står også: `--hent-foer-kl-22` står verken i README-en eller i `docs/hjelp.md`, fordi en henting før dagens kurser finnes, kan låse dagen.

**Plassen til bildet:** testen fra beslutningen kl. 23:41 (`test_til_faglaerer_og_kom_i_gang_foer_status`) krever at ingenting står mellom beskrivelsen og «Til faglærer». Bildet står derfor rett under lista «Til faglærer» og over «Kom i gang», øverst i README-en, og den beslutningen står.

**Bildet tas på nytt når oversikten endres.** Fremgangsmåten står under «Bildet», og en test feiler når malene eller demodataene bak bildet endres.

*Lagt til 2026-10-16 kl. 22:45:* gruppen tok 16.10 kl. 21:38 skjermbildet av oversikten i demoen ut av README-en igjen. Det snur punkt b i 3.3b (ja 15.10 kl. 22:54, flettet i `6b9dc2f`, PR #53). Bildet og teksten under det er tatt ut, `docs/bilder/readme/oversikten-demo.png` er slettet, og testene godtar igjen ingen bilder i README-en og i `docs/bilder/` utenom CI-merket (PR #54). Regelen står: bilder i README-en kommer bare fra `docs/bilder/readme/` og viser aldri den ekte versjonen. Bildene som kommer i «Kom i gang» søndag, er ikke berørt, men PR-en med dem må endre de to testene, med stien og alt-teksten som sier at det er demoen, og PR 1 for hovedindeksen trenger ikke ta bildet på nytt. Fremgangsmåten under «Bildet» og avtrykket `AVTRYKK_BAK_BILDET` gjelder ikke lenger, fordi bildet og testen er tatt ut.

## Boundaries & Constraints

- Ingen API-kall utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke.
- Bildet lages fra demobasen i en midlertidig mappe, aldri fra `data/db/ose.db` (regel 16 og 22).
- Ingen kode i `src/` endres.
- Ingen kommando i «Kom i gang» endres, så tabellene i §9 i `docs/kvalitetssikring.md` står.

## Bildet

*Opphevet 2026-10-16 (gruppen kl. 21:38, PR #54):* bildet og testene under er tatt ut. Fremgangsmåten og avtrykket under står som historikk.
*Lagt til 2026-10-18 (gruppens svar kl. 00:20, instruksjonen kl. 21:11):* bildet kommer tilbake i 3.3e (`spec-3-3e-bildet-uv-og-variablene.md`), tatt etter fremgangsmåten under.

`docs/bilder/readme/oversikten-demo.png` er toppen av oversikten i demoen, 1280 × 1000 px, tatt 16.10 med Edge uten vindu (headless). **Bildet tas på nytt når oversikten endres,** i samme commit som endringen, slik:

1. Lag demobasen i en midlertidig mappe (`tempfile.TemporaryDirectory()`), med `lagring_sqlite.BASE_STI` satt dit før `demo.lag_demobase(demo_sti())`, aldri i `data/`.
2. Sett `OSE_DEMO=1`, importer `app`, og start `waitress.server.create_server(app.app, host="127.0.0.1", port=...)` i en tråd, med en port som er ledig (`socket.bind(("127.0.0.1", 0))`). Ingen server som kjører, stoppes.
3. Sjekk at siden har «Eksempeltall», og ta bildet med `msedge --headless --disable-gpu --hide-scrollbars --window-size=1280,1000 --screenshot=<fil> http://127.0.0.1:<port>/`, med en egen `--user-data-dir` i den midlertidige mappa.
4. Lukk serveren. Den midlertidige mappa slettes med basen.

Testene i `TestSkjermbildet` krever at fila er en PNG som er 1280 px bred, at alt-teksten sier at det er demoen, at bildet står under «Til faglærer» og over «Kom i gang», og at `docs/bilder/` bare har dette bildet.

**Mappa:** svar 4 i spesifikasjonen for 3.4 (11.10) sier at bilder i README-en bare kommer fra `docs/bilder/readme/`, med alt-tekst, og aldri av den ekte versjonen. Instruksjonen sier `docs/bilder/`. Bildet ligger derfor i `docs/bilder/readme/`, som er i `docs/bilder/`, så begge stemmer.

**Avtrykket:** `test_bildet_tas_paa_nytt_naar_oversikten_endres` regner sha256 av `index.html`, `_ramme.html`, `_brikker.html`, `_bransjer.html`, `_hjelp.html` og `src/demo.py`, med LF, og sammenligner med `AVTRYKK_BAK_BILDET` i `tests/test_docker.py`. Endres noe av det, feiler testen til bildet er tatt på nytt og avtrykket er oppdatert, i samme commit.

## Kildene i README-en

- **Docker Desktop 4.91.0, motor 29.8.0 og Compose v5.5.1** er prøven 10.10 i [spesifikasjonen for 3.4](spec-3-4-demoversjonen.md), «Prøven først». Mac er «ikke prøvd» (svar 3 11.10, §9 i `docs/kvalitetssikring.md`). Python i imaget er `python:3.13.15-slim` i `Dockerfile`, og kravet `>=3.13` står i `pyproject.toml`.
- **Det som hoppes over** er `time.tzset` i `tests/test_fetch_prices.py`, AF_UNIX og `::1` i `tests/test_ingen_nettverk.py`, og testene som trenger git i `tests/test_ryddighet.py`. Lokalt 16.10: 16 for `time.tzset` og 1 for AF_UNIX.
- **Tidene for hentingen** følger `kjoer()` i `src/fetch_prices.py`: på en børsdag stopper den hele dagen før kl. 22 i Oslo, og en dag børsen er stengt, henter den bare hvis basen mangler forrige børsdag (`docs/hjelp.md`, «Når kan jeg hente?»).
- **«Neste:»** og storyene i rekkefølgen i `epics.md`: resten av KI-laget (10.2), hovedindeksen (2.8, 2.9, 2.9b), Min liste (8.3), innstillingene (8.10), periodene i kursgrafen (8.16, 8.17), historikken og signaldagene (2.7, 8.8), «Vis KI-tekst» i innstillingene (8.10b), KI-teksten om dagen (10.6), og å velge og bytte aksjer (2.11, 2.12).

## Gjennomgangen

Gjennomgang 16.10 på diffen `main...5072d78`, uten bildet, med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 10) og Verification Gap (VG, 5). Rettingene står i commiten etter `5072d78`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH | «Du trenger» sa at Python må installeres, «Tester» at uv henter den | medium | patch: «bare uv, som henter Python 3.13 eller nyere» begge steder |
| BH2 | `uv run pytest` sto to ganger under «Tester» | medium | patch: én rekkefølge, `uv sync` og så `uv run pytest`, og testen krever nøyaktig de to |
| BH3, VG3 | Vakten mot et fast testtall stoppet alle tall med tre sifre, men slapp gjennom «16 hoppes over» | low | patch: målrettet mot tall foran «tester», «hoppes» og lignende |
| BH4, ECH | `Thumbs.db` eller `.DS_Store` i `docs/bilder/` ville felt testen hos sensor | medium | patch: bare bildefiler telles |
| ECH | «på dagtid» stemte ikke: hentingen stopper hele børsdagen før kl. 22, og bare første gang mangler kursene | medium | patch: «Første gang før kl. 22 på en børsdag, også på dagtid» |
| BH5, ECH | Helgen var nevnt, men ikke andre dager børsen er stengt | low | patch: «i helgen og andre dager børsen er stengt» i steg 8 og raden «Klar» |
| BH6 | At bildet er demoen, sto bare i alt-teksten | medium | patch: synlig tekst under bildet, med test |
| BH7, VG2 | Høyden i spesifikasjonen var ikke testet | low | patch: 1280 × 1000 |
| BH8, VG1, ECH | Ingenting sørget for at bildet tas på nytt | medium | patch: avtrykket av malene og `demo.py`, se «Bildet» |
| BH9 | Versjonene hadde ingen dato | low | patch: «Vi prøvde 10.10», og kilden under «Kildene i README-en» |
| BH10, BH11, ECH | Testene leste `requires-python` på to måter, og en endret `FROM` ga `AttributeError` | low | patch: `_python_krav()` og en tydelig `assert` |
| BH12 | «Uten Docker, med uv» er ikke en lenke | low | patch: testen krever at boksen finnes. En lenke går ikke: GitHub lager ikke anker for `<summary>` |
| BH16 | Utpakkingen `(alt, sti), = …` ga en uklar feil | low | patch |
| ECH | «aksjesiden sier at dagen er uten KI-tekst» stemte ikke med teksten siden viser | low | patch: «aksjesiden viser ingen KI-tekst» |
| VG4 | Grunnen for `::1` manglet, og grunnene var ikke testet | low | patch: alle fire grunnene står og er testet |
| VG5 | «Neste:» var ikke koblet til storyene, og 8.10b manglet | medium | patch: «Vis KI-tekst» i innstillingene, og koblingen under «Kildene i README-en» |
| ECH | Linux er ikke nevnt som prøvd eller ikke prøvd | avvist | CI bygger og kjører imaget på Linux (jobben `docker` i `tester.yml`) |
| BH5 (del) | Tidssonen er ikke nevnt | avvist | README-en er for norske brukere, og `docs/hjelp.md` sier det samme |
| BH13 | Ja-et 15.10 kl. 22:54 er ikke ført noe sted | defer | står under «Beslutningene», og sies fra om til gruppen. Ingen funn må avgjøres av gruppen før flettingen, men linja for ja-et føres av gruppen |
| BH14 | `epics.md` sier `docs/bilder/` | avvist | `docs/bilder/readme/` er i `docs/bilder/`. Punkt b over og «Mappa» sier hvor |
| BH15 | «Status» er ett langt avsnitt | avvist | formen er besluttet kl. 23:41 («Status» i vanlige ord), og testen holder den |
| BH8 (del) | Skriptet er ikke committet | avvist | fremgangsmåten står under «Bildet», og avtrykket fanger at bildet må tas på nytt |

## Verifikasjonen

**Mutantene**, én om gangen med `-x` og bare `tests/test_docker.py`, med kopi før og sha256 mot HEAD etter hver, ble fanget alle, på `47ea051`: S1 et bilde til i README-en, S2 helgen borte fra steg 8, S3 helgen borte fra raden «Klar», S4 demoen før kl. 22 borte, S5 et fast testtall og S5b et tosifret testtall under «Tester», S6 «Neste:» i feil rekkefølge, S7 bildet borte, S8 alt-teksten uten demoen, S9 `uv sync` borte, S10 Mac ikke nevnt, S11 KI-delen ikke flettet, S12 grunnen uten git borte, S13 bildet flyttet mellom beskrivelsen og «Til faglærer», S14 teksten under bildet borte, S15 malen for oversikten endret uten nytt bilde, S16 8.10b borte fra «Neste:», S17 grunnen for `::1` borte, S18 den gamle blokken tilbake i «Tester», S19 «Du trenger» krever Python igjen, og S20 dager børsen er stengt borte fra steg 8. S1–S13 ble også kjørt og fanget på `5072d78`, før rettingene.

**Testene:** `uv run pytest -q` én gang på hele settet, etter gjennomgangene: 2140 bestått og 17 hoppet over på `47ea051`.

## Gjennomgangen av uttaket

*Lagt til 2026-10-16.* Gjennomgang av PR #54 (grenen `readme-uten-bilde`, uttaket av skjermbildet etter gruppen kl. 21:38), på diffen `main...bedb97b`, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, 2). Rettingene står i `26baa94` og `6990100`. Ingen funn må avgjøres av gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1, BH1, ECH | Regelen om `docs/bilder/readme/` og demoen står i dokumentene, men ingen test sjekker den, og søndagens bilder i «Kom i gang» feller begge testene | medium | patch: docstringene sier at testene bare sjekker at det ikke er noen bilder, og beslutningen sier at PR-en med bildene søndag endrer de to testene, med stien og alt-teksten |
| ECH, BH9 | Grenhashen `f9e6f59` blir borte ved squash-flettingen | medium | patch: PR #54 i de tre dokumentene |
| BH7 | «Avgjort … kl. 22:45» i spesifikasjonen ga skrivetidspunktet som beslutningstid | low | patch: «Lagt til», og 21:38 står i teksten |
| ECH, BH5 | «Bildet», avtrykket og punkt b i spesifikasjonen leses som gjeldende | low | patch: «Opphevet»-linje under «Bildet». Ingen linje fjernet |
| ECH, BH2, BH4 | Testen for `docs/bilder/` består når mappa mangler, og docstringen sa noe testen ikke sjekker | low | patch: docstringen sier at en tom mappe ikke finnes i git, og at testen sjekker at det ikke er bilder, ikke hvor de ligger |
| VG2, BH3 | Merket godtas på endelsen, og testen består uten merke | defer | uendret fra før denne PR-en. Tas med når testene endres for søndagens bilder |
| BH11 | Andre henvisninger til bildet | avvist | `git grep` etter filnavnet og konstantene: bare historikken i denne spesifikasjonen, som nå er merket opphevet |
| BH6 | `updated` i `epics.md` og spesifikasjonen | avvist | ingen av dem har feltet. `docs/vurderingsmatrise.md` har det, og det er satt fra klokka |
| BH8 | 22:54 mot 15:59 | avvist | begge stemmer: ja-et ble gitt 15.10 kl. 22:54 i chatten med rådet, og instruksjonen 16.10 kl. 15:59 er kilden (`ae55733`) |
| BH10 | Samme avsnitt på tre steder | avvist | instruksjonen 16.10 kl. 22:42 ber om alle tre |
| BH12 | Linja kl. 16:33 i matrisen sier i nåtid at README-en har bildet | avvist | matrisen fjerner ingen linjer uten en Rettet-linje. Linja kl. 22:45 under sier at bildet er borte når PR #54 flettes |
| BH13 | Rekkefølgetesten avhenger av at lista står tett under «Til faglærer:» | avvist | slik var testen før 3.3b (kl. 23:41), og den står |

Konflikt, ført her og ikke avgjort: bildene i «Kom i gang» søndag står bare i instruksjonen 16.10 kl. 22:42. `spec-3-4-demoversjonen.md` sier «PR 3, bilder: ingen (beslutning 4)». Den PR-en er flettet, så de to strider ikke, men ingen spesifikasjon beskriver søndagens bilder ennå (VG1).

*Lagt til 2026-10-18 (story 3.3d):* beslutningen 16.10 kl. 21:53–21:58 under story 3.3 i `epics.md` rydder delene 3.3b la til eller endret: «Status» blir to lister, «Ferdig» og «Neste», i stedet for avsnittet fra punkt a, og forklaringen under «Tester» fra punkt c legges delvis bak en knapp. Den bygges i `spec-3-3d-readme-ryddingen.md`.

*Rettet 2026-10-18 (gjennomgangen av 3.3d, VG12):* linja over sier at «Status» kom «fra punkt a». Avsnittet «Flettet til main» kom inn 12.10 i `4464a10` (PR #30), og punkt a i 3.3b oppdaterte det.
