---
title: 'Story 3.5 (3.5a): start med dobbeltklikk med uv, uten Docker'
type: 'feature'
created: '2026-10-23'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b4b6316'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/README.md'
---

## Intent

**Problem:** demoen og den ekte versjonen startes i dag med Docker Desktop og kommandoer i PowerShell eller Terminal («Kom i gang»), eller med fem kommandoer med uv («Uten Docker, med uv» under «Mer for den som vil»). En bruker uten Docker må skrive kommandoene selv.

**Grunnlaget:** gruppens svar 23.10 kl. 16:16 og 16:37 under «Prioritering» og story 3.3, og story 3.5 i `epics.md`. 3.5a er veien med uv. Teksten under er fra instruksjonen 23.10 kl. 22:46 i dagsfila.

## Slik er det i dag (slått opp 23.10 på `b4b6316`)

- **Med uv** sier README-en: `uv sync`, `uv run python src/demo.py` og `uv run python src/app.py --demo` for demoen, og `cp .env.example .env`, `uv run python src/fetch_prices.py` og `uv run python src/app.py` for den ekte versjonen.
- **`src/app.py`** starter Flask selv med `app.run(debug=True, port=8000)` når den kjøres som skript. Den kan altså ikke brukes av skriptene, som aldri skal ha debug.
- **Docker** starter webserveren med `waitress-serve --listen=0.0.0.0:8000 app:app` og `PYTHONPATH=/app/src` (`Dockerfile`). `waitress` står i `pyproject.toml`. `waitress-serve` har ikke noe valg for kodemappa, så skriptene setter `PYTHONPATH=src`, som Docker.
- **Demoen** slås på med miljøvariabelen `OSE_DEMO=1` (`I_DEMO` i `src/app.py`), som `--demo` setter. `src/demo.py` lager `data/db/demo.db` på nytt, og stopper med kode 1 hvis fila finnes uten demomerket.
- **Nøkkelen** leses av `hent_api_nokkel` i `src/fetch_prices.py` med `load_dotenv(PROSJEKTROT / ".env")`. `.env.example` har linja `EODHD_API_KEY=` uten verdi.
- **uv** installeres med `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` på Windows og `curl -LsSf https://astral.sh/uv/install.sh | sh` på Mac («Tester» i README-en). Installasjonen legger uv i `.local/bin` i brukermappa.
- **CI** (`.github/workflows/tester.yml`) har jobbene `pytest` og `docker`, begge på `ubuntu-latest`, og kjører på push til main og pull request mot main.

## Kontrollpunktene

- a) Fire filer i rota: «Start demoen» og «Start den ekte versjonen», som `.cmd` for Windows og `.command` for Mac. De starter `start/start.ps1` og `start/start.sh`, som går til mappa de ligger i, sjekker uv og spør før den offisielle installasjonen, kjører `uv sync`, og starter webserveren med `waitress-serve` bare på 127.0.0.1:8000, aldri med debug. Nettleseren åpnes når siden svarer. Demoen lager demobasen med `src/demo.py`. Den ekte versjonen kjører hentingen først. Har `.env` ingen nøkkel, åpnes https://eodhd.com/register, og nøkkelen leses uten å vises og skrives bare til `.env`. Vinduet sier på norsk, med æ, ø og å, hvordan man stopper og hva man gjør hvis noe feiler. `.command`-filene og `start/start.sh` er kjørbare i git.
- b) README-en: «Kom i gang» endres ikke. Under «Mer for den som vil» kommer «Start med dobbeltklikk, uten Docker», med nøkkelen første gang i den ekte versjonen, advarselen fra Windows og godkjenningen på Mac. Advarselen og godkjenningen står også i `docs/hjelp.md`. «Mappestruktur» får skriptene (regel 19).
- c) CI: jobben `dobbeltklikk` kjører «Start demoen» på `windows-latest` og `macos-latest`, med `OSE_START_SVAR_JA=1`, som svarer ja, og `OSE_START_UTEN_NETTLESER=1`. Den venter til siden svarer 200 med «Eksempeltall», og stopper. Den ekte versjonen kjøres ikke i CI.
- d) Testene, med «Ville feilet hvis», uten nett: skriptene finnes for begge, bruker de samme kommandoene som README-en, binder bare 127.0.0.1, har aldri debug eller `down -v`, og skriver aldri ut nøkkelen eller miljøet.

## Valg som er gjort her

- **«De samme kommandoene som README-en»** er kommandoene i den nye delen «Start med dobbeltklikk, uten Docker»: `uv sync`, `uv run python src/demo.py`, `uv run python src/fetch_prices.py` og webserveren med `uv run waitress-serve --listen=127.0.0.1:8000 app:app`. De tre første er de samme som i «Uten Docker, med uv». Webserveren er ikke `uv run python src/app.py`, fordi den har debug. Testen krever at hver kommando i skriptene står i README-en.
- **Rota** har de fire filene, så de synes med en gang mappa er pakket ut. Logikken står i `start/`, én fil per system.
- **Linjeskift:** `.gitattributes` gir `.cmd` og `.ps1` CRLF og `.command` og `.sh` LF, også i «Download ZIP». `start.ps1` er lagret som UTF-8 med BOM, fordi Windows PowerShell 5.1 ellers leser æ, ø og å feil.
- **Port 8000 i bruk:** svarer noe allerede på 127.0.0.1:8000, for eksempel demoen i Docker, stopper skriptet med en beskjed før webserveren startes, så nettleseren aldri åpner en annen app.

## Planen, én commit per punkt

1. a) Skriptene, `.gitattributes` og kjørbar-biten.
2. b) README-en og `docs/hjelp.md`.
3. c) CI-jobben.
4. d) Testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: serveren på 0.0.0.0, nøkkelen skrevet ut, og debug på.

## Det som ikke endres

- «Kom i gang», til gruppen har valgt hovedvei (svaret kl. 16:37).
- `src/app.py`, `src/demo.py` og `src/fetch_prices.py`.
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` og `.env` på denne maskinen røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.

## Prøven før flettingen

Flettingen stopper alltid før gruppen har prøvd: «Download ZIP» av grenen på GitHub, pakk ut i en ny mappe, og dobbeltklikk «Start demoen». Den ekte versjonen prøves aldri med gruppens nøkkel i en kopi, men i README-prøven med testerens egen konto.
