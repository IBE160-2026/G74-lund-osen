---
title: 'Story 3.5 (3.5a): start med dobbeltklikk med uv, uten Docker'
type: 'feature'
created: '2026-10-23'
status: 'in-review'
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

*Lagt til 2026-10-23:* kjørt på `1d46532` og igjen på `6287033` etter rettingene, i en klon med `core.autocrlf=false` som ble slettet etterpå, med `tests/test_dobbeltklikk.py`. Alle ble fanget begge gangene. `.gitattributes` gir `start.ps1` CRLF også med `core.autocrlf=false`, så fila ble sammenlignet med `git hash-object` mot `HEAD:<sti>`, og sha256 av fila var lik kopien før:

| # | Mutant | Fanget av |
|---|---|---|
| M1 | Serveren på 0.0.0.0 i `start.ps1` | `test_skriptene_bruker_kommandoene_i_readme[start.ps1]`, og `test_webserveren_binder_bare_127_0_0_1` |
| M2 | Nøkkelen skrevet ut i `start.sh` | `test_noekkelen_og_miljoeet_skrives_aldri_ut[start.sh]` |
| M3 | `FLASK_DEBUG=1` i `start.ps1` | `test_aldri_debug_eller_down_v[start.ps1]` |

## Gjennomgangen 23.10

Gjennomgang 23.10 etter hele settet, på `b4b6316` på main og diffen `b4b6316..1d46532` på grenen. Linsene var Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 13 funn) og Verification Gap (VG, 11 funn), hver for seg og uten å endre noe i repoet. 40 funn ble 27 rader. De små funnene er rettet med en gang (svaret 23.10 kl. 15:53), i `03addee` (skriptene), `f886dd9` (README-en og hjelpen) og `6287033` (testene).

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | stderr fra `uv` kunne stoppe `start.ps1` med `$ErrorActionPreference = 'Stop'` når utskriften er omdirigert | high og medium etter linsene, avvist | prøvd lokalt 23.10 med samme omdirigering som CI (`Start-Process` med `-RedirectStandardOutput` og `-RedirectStandardError`): `uv sync` skrev til stderr, og skriptet gikk videre til webserveren. CI på `windows-latest` er den andre prøven |
| BH2 | En server som stopper av seg selv, lukket vinduet uten beskjed | medium | rettet i `03addee`: koden etter `WaitForExit()` og `wait` gir beskjeden |
| BH3, ECH2 | Etter 120 s uten svar sto waitress igjen i `start.ps1` | medium | rettet i `03addee`: `Stopp` stopper serveren med `taskkill /T /F` |
| BH4, VG2 | En feil skriptet ikke har ventet, lukket vinduet uten beskjed | low og medium | rettet i `03addee`: `trap` gir beskjeden på norsk |
| BH5, ECH8 | Ctrl+C i ventesløyfa på Mac ga «appen svarte ikke», og HUP var ikke med | low | rettet i `03addee`: `trap 'exit 130' INT TERM HUP` |
| BH6 | `.env.ny` fikk rettighetene fra umask | low | rettet i `03addee`: `umask 077` |
| BH7, ECH5, VG10 | Nøkkelen ble renset ulikt på Windows og Mac | low og nit | rettet i `03addee`: alle mellomrom og linjeskift tas bort på begge |
| BH8 | Koden fra installasjonen av uv ble ikke sjekket på Windows | nit | rettet i `03addee` |
| BH9 | Ctrl+C i et `.cmd`-vindu spør om satsvis jobb skal avbrytes | nit | uten endring: vinduet sier at det kan lukkes, og det stopper appen |
| BH10, ECH10, VG7 | CI prøver installasjonen av uv bare hvis maskinen ikke har uv | low | se loggen fra CI-kjøringen i Utført-linja |
| BH11 | Testen for æ godtok «Første» | nit | rettet i `6287033`: æ, ø og å i det vinduet sier, og en melding med æ |
| BH12, VG4, VG11 | Testen for nøkkelen var lett å gå rundt | low og nit | rettet i `6287033`: nøkkelen under et annet navn, flere måter å skrive til fil og miljøet på |
| BH13 | Linjeskiftene i arbeidskopien er ikke testet | low | uten endring: `.gitattributes` gjelder «Download ZIP», og testen leser den |
| BH14 | Hjelpen ga bare stoppkommandoen for demoen | nit | rettet i `f886dd9`: `docker compose --profile demo down` stopper begge, som README-en sier |
| BH15 | Godkjenningen på Mac kan være en annen i nyere macOS | nit | uten endring: ikke slått opp her. Står under «Åpent», til prøven på en Mac |
| BH16, ECH7 | Bare 200 talte som opptatt port | nit og low | rettet i `03addee`: alt som svarer på porten |
| VG1, ECH9 | Ingen vakt mot regel 22 i den ekte versjonen | medium og low | rettet i `03addee`: med `.git` startes den ekte versjonen bare fra main. Prøvd i en klon på grenen: stoppet før noe ble hentet, uten `.env` |
| VG3 | Rekkefølgen demo.py eller hentingen før serveren var ikke testet | medium | rettet i `6287033`: `test_rekkefoelgen_demo_eller_henting_foer_serveren` |
| VG5 | Et nei til installasjonen var ikke testet | low | rettet i `6287033` |
| VG6 | Nettleseren etter svaret og registreringssiden bare uten nøkkel var ikke testet | low | rettet i `6287033`: `test_nettleseren_aapnes_etter_at_siden_svarer`. «0 kall» står på vaktene i `src/fetch_prices.py` |
| VG8, ECH4 | Kode 1 fra hentingen på dagtid så ut som en feil | low | rettet i `03addee`: beskjeden viser til linjene over. Nye forsøk for aksjer som mangler, følger 2.3b |
| VG9 | En overflødig linje i testen av startfilene | nit | rettet i `6287033` |
| ECH3 | En feil nøkkel ble aldri spurt etter på nytt | medium | rettet i `03addee` og `f886dd9`: vinduet, README-en og hjelpen sier at verdien slettes i `.env` |
| ECH6 | `EODHD_API_KEY= abc` med mellomrom regnes som manglende | low | uten endring: `.env.example` har linja uten mellomrom, og vinduet spør da på nytt |
| ECH11 | Demobasen lages på nytt ved hver start | low | uten endring: som `demo-lag` i Docker |
| ECH12 | `start.ps1` hadde LF i arbeidskopien før `.gitattributes` | nit | uten endring: en ny utsjekk og ZIP-en får CRLF |
| ECH13 | `Copy-Item` og `Test-Path` uten `-LiteralPath` | nit | rettet i `03addee` |

Mutantene etter rettingene, på `6287033`: M1 `test_skriptene_bruker_kommandoene_i_readme[start.ps1]`, M2 `test_noekkelen_og_miljoeet_skrives_aldri_ut[start.sh]`, M3 `test_aldri_debug_eller_down_v[start.ps1]`.

*Lagt til 2026-10-23 (CI på PR #92):* på `d202cbe` var `dobbeltklikk (windows-latest)` rød i run 40027262304. Windows PowerShell 5.1 ble startet fra PowerShell 7 og arvet modulstiene derfra, og installasjonen av uv feilet på `Get-ExecutionPolicy`. `.cmd`-filene tømmer nå `PSModulePath` før PowerShell startes (`3af0882`). I run 40027845278 på `3af0882` var alle fire jobbene grønne, og loggen viser at skriptet installerte uv både på `windows-latest` og `macos-latest` («uv er ikke installert», så «everything's installed!»), så spørsmålet og installasjonen er prøvd i CI (BH10, ECH10, VG7).

## Åpent

- **Godkjenningen på Mac** (BH15): teksten i README-en og hjelpen er ikke prøvd på en Mac. Prøven før flettingen viser om høyreklikk og Åpne er nok, eller om Personvern og sikkerhet må komme først.

## Det som ikke endres

- «Kom i gang», til gruppen har valgt hovedvei (svaret kl. 16:37).
- `src/app.py`, `src/demo.py` og `src/fetch_prices.py`.
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` og `.env` på denne maskinen røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.

## Prøven før flettingen

Flettingen stopper alltid før gruppen har prøvd: «Download ZIP» av grenen på GitHub, pakk ut i en ny mappe, og dobbeltklikk «Start demoen». Den ekte versjonen prøves aldri med gruppens nøkkel i en kopi, men i README-prøven med testerens egen konto.
