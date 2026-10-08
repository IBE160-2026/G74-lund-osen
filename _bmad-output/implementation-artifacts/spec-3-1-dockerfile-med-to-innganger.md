---
title: 'Story 3.1: Dockerfile med to innganger'
type: 'feature'
created: '2026-10-08'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '0f084ee6c3435706a864e7b03e04f42477f21283'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Løsningen kan bare kjøres på en maskin med Python og uv satt opp som hos oss. Sensor og faglærer skal kunne bygge og kjøre den fra repoet alene, og leveransen er «kildekode og docker fil» (merknaden under story 3.1 i `epics.md`).

**Approach:** Én Dockerfile gir ett image med to innganger: webserveren som standard, og hentekommandoen som eget valg mot samme image (`AD-10`, `AD-17`). En compose-fil har tjenestene `app` og `hent` og de navngitte volumene `ose-db` og `ose-raa`. Imaget har aldri data eller nøkler (`AD-9`, `AD-12`), og migrasjonene går gjennom `aapne_base` som før (2.1b).

## Planen

Planen er vist i chatten 08.10 og ført i `docs/ai-prompts/2026-10-08.md` (instruksjonen kl. 22:39 og Utført-linjen). Gruppen sa ja kl. 22:45 med disse svarene, som er beslutninger:

1. **Webserveren i containeren er waitress**, ikke Flasks egen server. Imaget er det sensor kjører, og Flasks server skriver selv ut at den ikke skal brukes slik. waitress legges i `uv.lock`, og debug er aldri på i containeren.
2. **To tjenester fra samme image.** `app` er webserveren, uten nøkkel og uten `env_file`. `hent` kjører `python src/fetch_prices.py`, har `env_file: .env` og ligger i profilen `hent`, så `docker compose up` bare starter webserveren. Hentingen startes med `docker compose run --rm hent`, som passer med «docker run … hent» i `AD-17`. Ingen ny kode. En test krever at `app` ikke har nøkkelen, og at `hent` har den.
3. **CI bygger imaget** i en egen jobb uten hemmeligheter.

## Boundaries & Constraints

**Always:**
- Grunnbildet er `python:3.13-slim` med fast versjon, samme Python 3.13 som CI. Avhengighetene kommer fra `uv.lock` med `uv sync --locked --no-dev`. `tzdata` kommer fra låsefila, så `ZoneInfo("Europe/Oslo")` virker uten tidssonedatabase i bildet (`AD-20`).
- `.dockerignore` holder ute `data/`, `.env` og `.env.*` (ikke `.env.example`), `_privat/`, `.git`, `*.db`, `*-raa-*.json`, `.venv`, cacher og `local-tests/`. Imaget har ingen rådata og ingen base (`AD-9`).
- Webserveren starter med waitress mot `app:app`, lytter på `0.0.0.0:5000` inne i containeren, og compose binder porten bare til `127.0.0.1:5000` på maskinen (betingelsen fra EODHD 21.09: lokalt, ikke publisert). Den gjør null nettkall (`AD-10`) og starter uten nøkkel.
- Migrasjonene har ikke noe eget steg: ingen `RUN`, `command` eller `entrypoint` migrerer. Begge inngangene går gjennom `aapne_base` (2.1b).
- `EODHD_API_KEY` står aldri i Dockerfile eller compose-fila som verdi, og aldri som `ENV` eller `ARG`. Bare `hent` får `.env`, gjennom `env_file`.
- Volumene er navngitte (`ose-db` på `/app/data/db`, `ose-raa` på `/app/data/raa`). Ingen bind-mount av `./data`, så ingen container rører `data/db/ose.db` på maskinen (regel 22).
- Appen kjører som en bruker som ikke er root, og `/app/data/db` og `/app/data/raa` eies av den, så volumene får riktig eier første gang.

**Never:**
- Ollama og volumet `ollama` (10.2), README-teksten og en ny `HENTEKOMMANDO` (3.3), demobasen (3.4), arbeidskopien til den faste jobben etter 2.3.
- `hent` kjøres aldri med den ekte nøkkelen. Prøves den, er det uten `.env` og med `--network none`. Prøvekjøringene bruker et eget compose-prosjektnavn, og volumene deres fjernes etterpå.
- `src/fetch_prices.py` endres ikke, og `app.py` får ingen ny kode utover det waitress trenger (ingen).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Webserveren, tomt volum | `docker compose up`, `ose-db` finnes ikke | `/` svarer 200 med den tomme siden, basen migreres ved første forespørsel | Basefeil gir 503 som før |
| Webserveren uten nett | `--network none` | `/` svarer 200 | — |
| Hentingen uten nøkkel | `hent` uten `.env`, `--network none` | Stopper før første kall, med kode og utskrift som i 2.3 | Ingen traceback med nøkkel |
| Imaget | ren bygging fra repoet | ingen `*.db`, `*-raa-*.json`, `.env` eller filer under `/app/data` | — |

</frozen-after-approval>

## Code Map

- `src/app.py` -- `app` er WSGI-objektet waitress serverer. `app.run(debug=True, port=5000)` under `__main__` brukes ikke i containeren og endres ikke. `HENTEKOMMANDO` endres ikke (3.3).
- `src/fetch_prices.py` -- `main()` er hentingens inngang. Leser `EODHD_API_KEY` med `load_dotenv(PROSJEKTROT / ".env")` og `os.getenv`, så nøkkelen fra `env_file` virker uten `.env` i imaget.
- `src/lagring_sqlite.py` -- `aapne_base`, `BASE_STI = data/db/ose.db`. `src/lagring_fil.py` -- `PROSJEKTROT`, `RAA_KATALOG = data/raa`. I imaget blir det `/app/data/db` og `/app/data/raa`.
- `pyproject.toml`, `uv.lock` -- waitress legges til med `uv add`.
- `.github/workflows/tester.yml` -- får jobben `docker` ved siden av `pytest`, uten hemmeligheter.
- `tests/test_app.py::test_kommandoen_paa_den_tomme_siden_staar_i_readme` -- står uendret.
- Spinen, `AD-10` -- datert merknad om waitress og `docker compose run --rm hent`.

## Tasks & Acceptance

**Execution:**
- [ ] `pyproject.toml`, `uv.lock` -- `uv add waitress` -- webserveren i imaget.
- [ ] `Dockerfile` -- grunnbilde, uv, `uv sync --locked --no-dev`, bruker, mapper, `CMD` med waitress.
- [ ] `.dockerignore` -- mønstrene over.
- [ ] `compose.yaml` -- tjenestene `app` og `hent`, profilen `hent`, porten på 127.0.0.1, volumene.
- [ ] `tests/test_docker.py` -- statiske tester av de tre filene, uten Docker og uten nett.
- [ ] `.github/workflows/tester.yml` -- jobben `docker`: bygg, ingen data i imaget, Python 3.13, Oslo-tid, webserveren med `--network none`, hentingen uten nøkkel med `--network none`.
- [ ] Spinen -- merknaden under `AD-10`.

**Acceptance Criteria:**
- Given en ren utsjekk, when imaget bygges, then har det ingen rådata, ingen base og ingen `.env`.
- Given compose-fila, when `docker compose up` kjøres, then starter bare `app`, på `127.0.0.1:5000`, uten nøkkel.
- Given `docker compose run --rm hent`, then kjøres `python src/fetch_prices.py` med `.env` fra `env_file`.
- Given hvert kontrollpunkt, when en mutant bryter det, then feiler en test i pytest eller et steg i CI-jobben.

## Implementation Notes

- **Grunnbildet** er `python:3.13.15-slim` (laget 2026-09-19), og uv kopieres fra `ghcr.io/astral-sh/uv:0.12.15`, samme uv som lokalt. Avhengighetene ligger i `/opt/venv` (`UV_PROJECT_ENVIRONMENT`), med `--no-install-project`, fordi prosjektet ikke er en pakke. `PYTHONPATH=/app/src` gjør at `waitress-serve app:app` og `python src/fetch_prices.py` finner modulene som i pytest.
- **`UV_PYTHON_DOWNLOADS=never`** kom til etter mutanten I5: med `python:3.12-slim` lastet uv ned en egen 3.13 under byggingen, og CI-steget for versjonen gikk gjennom. Nå feiler byggingen.
- **Stiene:** `PROSJEKTROT` er `/app`, så basen er `/app/data/db/ose.db` og øyeblikksbildene `/app/data/raa/`, der volumene monteres. Mappene eies av brukeren `ose` (uid 10001), så et nytt navngitt volum får den eieren.
- **`.env` i `hent`:** `fetch_prices` leser `/app/.env` med `load_dotenv`, som ikke finnes i imaget, og så `os.getenv`. Nøkkelen fra `env_file` kommer gjennom miljøet. Uten `.env` nekter `docker compose run --rm hent` å starte (`env file … not found`), og `docker compose up` starter `app` som før (prøvd 08.10 med prosjektnavnet `ose-proeve` i en mappe uten `.env`).
- **Lokale prøver 08.10, uten nøkkel og uten `data/`:** imaget har Python 3.13.15, brukeren `ose`, Oslo-tid og ingen `*.db`, `*-raa-*.json` eller `.env`. Webserveren med `--network none` svarte 200 med den tomme siden og migrerte basen i containeren. `python src/fetch_prices.py` med `--network none` og uten nøkkel stoppet med «EODHD_API_KEY mangler» og kode 1, etter tidskontrollen, basen og filvakten (kl. 22:5x). Med compose og `-p ose-proeve` var porten `127.0.0.1:5000`, `/` svarte 200, `app` hadde ingen `EODHD`-variabel, og volumene het `ose-proeve_ose-db` og `ose-proeve_ose-raa`. De er fjernet med `down -v`.
- **README** er ikke endret. Den nevner ikke Docker-filene, og «Kom i gang» med Docker er 3.3 (regel 19).
- **compose-parseren** i `tests/test_docker.py` er laget for akkurat `compose.yaml`, så testene ikke trenger en YAML-pakke. CI-steget `docker compose config --services` prøver at fila er gyldig compose.

## Spec Change Log

## Review Triage Log

## Verification

**Mutantene, 08.10 rett før kl. 23:00.** Statiske mot `tests/test_docker.py`, 18 av 18 drept:

| Mutant | Testen som fanger den |
|---|---|
| D1 Python 3.12 | `test_python_er_313_som_ci` |
| D2 dev-gruppen med | `test_avhengighetene_kommer_fra_uv_lock_uten_dev` |
| D3 `COPY . .` | `test_bare_koden_kopieres` |
| D4 `EODHD_API_KEY` i `ENV` | `test_ingen_noekkel_i_imaget` |
| D5 `USER` fjernet | `test_ikke_root` |
| D6 Flasks egen server | `test_webserveren_er_waitress_uten_debug` |
| D7 migrering i et eget `RUN`-steg | `test_ingen_migrering_i_eget_steg` |
| D8 migrering i `command` for `app` | `test_ingen_migrering_i_eget_steg`, `test_app_er_standard_og_hent_ligger_i_profilen` |
| D9 `data/` ut av `.dockerignore` | `test_data_noekler_og_lokale_baser_holdes_ute` |
| D10 `"5000:5000"` | `test_porten_er_bare_paa_maskinen` |
| D11 `./data:/app/data` | `test_navngitte_volumer_aldri_data_paa_maskinen` |
| D12 `app` får `env_file` | `test_bare_hent_har_noekkelen` |
| D13 `hent` uten profil | `test_app_er_standard_og_hent_ligger_i_profilen` |
| D14 `hent` kjører noe annet | `test_hent_kjoerer_hentekommandoen` |
| D15 volumene med fast `name:` | `test_navngitte_volumer_aldri_data_paa_maskinen` |
| D16 Ollama i compose | `test_ingen_ollama_i_31` og to til |
| D17 waitress ut av avhengighetene | `test_waitress_er_en_avhengighet_ikke_dev` |
| D18 `UV_PYTHON_DOWNLOADS=never` fjernet | `test_uv_laster_aldri_ned_en_egen_python` |

I imaget, mot stegene i CI-jobben `docker`, kjørt lokalt med de samme kommandoene. 5 av 5 drept etter rettingen:

| Mutant | Steget som feiler |
|---|---|
| I1 en tom `kurser-raa-*.json` og `ose.db` lages i imaget | 2, ingen rådata eller base |
| I2 `EODHD_API_KEY` i miljøet til imaget | 2 og 4 |
| I3 webserveren starter ikke (`app:finnes_ikke`) | 4 |
| I4 `hent` uten profil | 6 |
| I5 `python:3.12-slim` | overlevde først (uv lastet ned 3.13). Etter `UV_PYTHON_DOWNLOADS=never`: 1, byggingen, og 3 |

Ingen mutant leste eller skrev `data/`. I1 lager tomme filer i imaget i stedet for å kopiere ekte data.

**Suiten:** 1209 passed og 16 skipped, mot 1191 og 16 før (18 nye i `tests/test_docker.py`).

**Commands:**
- `uv run pytest -q` -- expected: grønn, med de nye testene i `tests/test_docker.py`.
- `docker build -t ose-signal:3-1 .` -- expected: bygger fra ren utsjekk.
- Kontrollene i CI-jobben `docker`, kjørt lokalt med eget prosjektnavn.
