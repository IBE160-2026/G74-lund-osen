---
title: 'Story 3.5 (3.5d): funnene fra forprøven av den ekte versjonen 24.10'
type: 'bugfix'
created: '2026-10-24'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7b784f0'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5a-dobbeltklikk-med-uv.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** forprøven av den ekte versjonen 24.10 kl. 12:14–12:18 gikk gjennom fra nøkkelen til siden, med åtte funn. Vinduet sa ikke hvor nøkkelen står hos EODHD eller hvordan den limes inn, meldingene fra hentingen og demoen hadde oe, aa og ae, webserveren skrev «Task queue depth», en annen versjon av OSE Signal på porten stoppet starten, og en beskjed viste bare til README-en.

**Grunnlaget:** gruppens svar 24.10 kl. 12:04–12:18, avgjørelsene kl. 12:04 og 12:11 under story 3.5 i `epics.md`, og instruksjonen 24.10 kl. 16:26 i dagsfila.

## Forprøven 24.10 kl. 12:14–12:18

Den ekte versjonen i en ZIP-kopi på gruppens PC med egen testkonto (avgjort kl. 12:11), gjennom fra nøkkelen til siden. Funnene står her slik instruksjonen 24.10 kl. 16:26 grupperer dem. Ordlyden i svarene kl. 12:14–12:18 ligger ikke i repoet.

| Funn | Hva | Punkt |
|---|---|---|
| 1–3 | Nøkkelen: hvor den står hos EODHD, hvordan den limes inn, og hvordan den vises | a) |
| 4–5 | Det brukeren ser fra `src/fetch_prices.py` og `src/demo.py` hadde oe, aa og ae, og linja om hovedindeksen sa ikke hvorfor andre dager enn 2026 ikke lagres (U4) | b) |
| 6 | Webserveren skrev «Task queue depth» | c) |
| 7 | Noe svarte allerede på 127.0.0.1:8000 | d) |
| 8 | En beskjed i vinduet viste bare til README-en | e) |

## Slik er det i dag (slått opp 24.10 på `7b784f0`)

- **Nøkkelen:** vinduet sier «Lag en gratis konto, kopier nøkkelen (API key), og lim den inn her.», og spørsmålet sier «(den vises ikke)» på begge. `start.ps1` leser med `Read-Host -AsSecureString`, `start.sh` med `read -r -s`.
- **Meldingene:** strengene i `src/fetch_prices.py` og `src/demo.py` er skrevet med oe, aa og ae, for eksempel «Ingenting aa hente», «boersdagen» og «KI-tekst for … aksjer paa siste dag». Linja om hovedindeksen er «… lagret N dager, tok bort M som ikke er boersdager i 2026.» (`skriv_indeksen_til_basen`, årene fra `boersdag.DEKKEDE_AAR`).
- **Webserveren:** `waitress-serve --listen=127.0.0.1:8000 app:app` i begge skriptene og README-en, og `waitress-serve --listen=0.0.0.0:8000 app:app` i `Dockerfile`, uten `--threads`, så waitress bruker standarden på 4 tråder.
- **Porten:** sjekkes etter uv og før `uv sync`. Svarer noe, stopper skriptet med «noe svarer allerede på http://127.0.0.1:8000. Stopp det først: …», uansett hva det er. `start.sh` sjekker med curl.
- **Beskjedene:** `stopp` og `Stopp` legger alltid til «Se «Står du fast?» i README-en, eller docs/hjelp.md.». «uv er ikke installert. Installer uv slik «Tester» i README-en sier» viser bare til README-en, og «appen svarte ikke på 127.0.0.1:8000.», «demobasen kunne ikke lages» og «installasjonen av uv feilet» sier ikke hva man gjør.
- **Prosessen på porten (prøvd 24.10 på Windows med en testapp i Temp, ikke appen):** `uv run waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app` lytter i `python.exe` med kommandolinja `"…\.venv\Scripts\python.exe" "…\.venv\Scripts\waitress-serve.exe" --listen=127.0.0.1:8000 --threads=8 app:app`.

## Kontrollpunktene

- a) **Nøkkelen (funn 1–3):** vinduet sier at nøkkelen står som «API token» under «Dashboard» hos EODHD, med kopiknappen til høyre, og hvordan man limer inn: Ctrl+V eller høyreklikk på Windows, Cmd+V på Mac. På Windows vises den som stjerner, på Mac ikke. README-en og hjelpen sier det samme.
- b) **Æ, ø og å (funn 4 og 5):** det brukeren ser fra `src/fetch_prices.py` og `src/demo.py` har æ, ø og å, også i Windows PowerShell 5.1. Linja om hovedindeksen sier at børskalenderen i appen gjelder 2026, så andre dager ikke lagres (U4). Filnavnene (`-raa-`, `forsoek`) endres ikke.
- c) **Tråder (funn 6):** webserveren får `--threads=8` i begge skriptene, README-en og `Dockerfile`.
- d) **Porten (funn 7, svaret kl. 12:04):** før uv og hentingen. Svarer noe på 127.0.0.1:8000, og har prosessen kommandolinja fra skriptene (`waitress-serve`, `--listen=127.0.0.1:8000` og `app:app`), stopper skriptet den, venter til porten er ledig, sier det og går videre. Alt annet, også Docker og `python src/app.py`, stoppes aldri, og vinduet sier hvilket program og hva man gjør.
- e) **Beskjedene (funn 8):** ingen beskjed i vinduet viser bare til README-en; hver sier hva man gjør.
- **Testene,** med «Ville feilet hvis», uten nett: også med en fremmed lytter på 127.0.0.1:8000, som skal kjøre videre, og med en lytter med kommandolinja fra skriptene, som skal stoppes. CI-jobben `dobbeltklikk` krever æ, ø og å i utskriften fra «Start demoen».

## Valg som er gjort her

- **«API token» og «Dashboard»** står slik gruppen så dem i forprøven. Siden hos EODHD krever innlogging og er ikke slått opp her (under «Åpent»).
- **Kommandolinja** gjenkjennes på tre deler hver for seg: `waitress-serve` (også `waitress-serve.exe` med sti), `--listen=127.0.0.1:8000` og `app:app`. Da stoppes også en eldre kopi uten `--threads=8`, og en annen kopi av OSE Signal i en annen mappe. Er én av lytterne på porten noe annet, stoppes ingenting.
- **Windows** finner lytteren med `Get-NetTCPConnection` og kommandolinja med `Get-CimInstance Win32_Process`, og stopper med `taskkill /T /F`. **Mac** finner den med `lsof` og kommandolinja med `ps`, og stopper med `kill`. Uten `lsof` er programmet ukjent, og ingenting stoppes.
- **`start.sh` sjekker porten** med `/dev/tcp` i bash i stedet for curl, så sjekken ikke regner porten som opptatt når curl mangler.
- **Utskriften fra Python** får `PYTHONIOENCODING=utf-8` i `start.ps1`, så æ, ø og å også er riktige når utskriften går til en fil, som i CI. I et vanlig vindu skriver Python til konsollen uansett.
- **Hentingens filnavn** og nøklene i JSON endres ikke, bare tekstene brukeren leser.

## Planen, én commit per punkt

1. a) Nøkkelen: skriptene, README-en, hjelpen og testene.
2. b) Æ, ø og å: `src/fetch_prices.py`, `src/demo.py`, `start.ps1`, testene og CI-steget.
3. c) `--threads=8`: skriptene, README-en, `Dockerfile` og testene.
4. d) Porten: skriptene, README-en, hjelpen og testene.
5. e) Beskjedene: skriptene, README-en, hjelpen og testene.

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: sjekken av kommandolinja borte, så alt på porten stoppes.

## Åpent

- **«API token» under «Dashboard»** hos EODHD er ikke slått opp, fordi siden krever innlogging. Teksten står slik gruppen så den i forprøven.

## Det som ikke endres

- «Kom i gang», til gruppen har valgt hovedvei (svaret 23.10 kl. 16:37).
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `.env` på denne maskinen røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
