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

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn, med de nye testene i `tests/test_docker.py`.
- `docker build -t ose-signal:3-1 .` -- expected: bygger fra ren utsjekk.
- Kontrollene i CI-jobben `docker`, kjørt lokalt med eget prosjektnavn.
