---
title: 'Story 3.1: Dockerfile med to innganger'
type: 'feature'
created: '2026-10-08'
status: 'in-review'
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
- [x] `pyproject.toml`, `uv.lock` -- `uv add waitress` -- webserveren i imaget.
- [x] `Dockerfile` -- grunnbilde, uv, `uv sync --locked --no-dev`, bruker, mapper, `CMD` med waitress.
- [x] `.dockerignore` -- mønstrene over.
- [x] `compose.yaml` -- tjenestene `app` og `hent`, profilen `hent`, porten på 127.0.0.1, volumene.
- [x] `tests/test_docker.py` -- statiske tester av de tre filene, uten Docker og uten nett.
- [x] `.github/workflows/tester.yml` -- jobben `docker`: bygg, ingen data i imaget, Python 3.13, Oslo-tid, webserveren med `--network none`, hentingen uten nøkkel med `--network none`.
- [x] Spinen -- merknaden under `AD-10`.

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
- **Lokale prøver 08.10, uten nøkkel og uten `data/`:** imaget har Python 3.13.15, brukeren `ose`, Oslo-tid og ingen `*.db`, `*-raa-*.json` eller `.env`. Webserveren med `--network none` svarte 200 med den tomme siden og migrerte basen i containeren. `python src/fetch_prices.py` med `--network none` og uten nøkkel stoppet med «EODHD_API_KEY mangler» og kode 1, etter tidskontrollen, basen og filvakten (kl. 22:5x). *Rettet 08.10 kl. 23:10 (BH9):* «kl. 22:5x» er ikke lest fra klokka. Prøven var mellom kl. 22:47, da instruksjonen ble lagret, og 22:55, da spinen fikk `updated` fra klokka. Med compose og `-p ose-proeve` var porten `127.0.0.1:5000`, `/` svarte 200, `app` hadde ingen `EODHD`-variabel, og volumene het `ose-proeve_ose-db` og `ose-proeve_ose-raa`. De er fjernet med `down -v`.
- **README** er ikke endret. Den nevner ikke Docker-filene, og «Kom i gang» med Docker er 3.3 (regel 19).
- **3.1 og 3.2 (BH7):** 3.1 lager compose-fila med de navngitte volumene `ose-db` og `ose-raa`, og testene her krever at de er navngitte og atskilte, uten bind-mount av `./data`. 3.2 prøver det med volumene i drift: at `ose-db` kan fjernes mens `ose-raa` står, at imaget starter uten volumer fra før, og hvorfor «du kan slette basen» er feil råd (`AD-11`, `AD-7`).
- **Etter gjennomgangen, 08.10 kl. 23:00–23:09** (`761df48`, `3869f77`): `hent` har `build: .` og `pull_policy: build`, så compose aldri henter et image som heter `ose-signal` fra et register og gir det `.env`. Begge har `init: true`. `.dockerignore` har filmønstrene også med `**/`: `src/__pycache__` fra maskinen kom med i imaget før rettingen. CI-jobben prøver hentingen med `--hent-foer-kl-22` og kode 1, Oslo-tid med `PYTHONTZPATH` tom, den tomme siden og basen i webserveren, og skrivetilgang i nye navngitte volumer. `ECH7` er utsatt til 3.3 (`deferred-work.md`).
- **compose-parseren** i `tests/test_docker.py` er laget for akkurat `compose.yaml`, så testene ikke trenger en YAML-pakke. CI-steget `docker compose config --services` prøver at fila er gyldig compose.

## Spec Change Log

- **2026-10-08, etter gjennomgangen (ECH11):** «`tzdata` kommer fra låsefila, så `ZoneInfo("Europe/Oslo")` virker uten tidssonedatabase i bildet» under Boundaries stemmer ikke helt: `python:3.13.15-slim` har `/usr/share/zoneinfo`, så sonen virket også uten pakken. Det som gjelder: pakken `tzdata` fra `uv.lock` er nok alene. CI-steget for Oslo-tid kjøres med `PYTHONTZPATH` tom, så `zoneinfo` bare kan bruke pakken, og mutanten I7 (pakken fjernet) fanges.
- **2026-10-08, nummereringen (BH6):** instruksjonen kl. 22:45 nummererer svarene 1, «2 og 3» og 4. «Planen» over har dem som 1, 2 og 3. Testene viser til instruksjonens nummer («svar 2 og 3»).
- **2026-10-08, `hent` og registeret (BH2, ECH6):** Boundaries sier ikke hvor imaget kommer fra. `hent` hadde bare `image: ose-signal` og kunne hente et fremmed image fra et register. Begge tjenestene bygger nå fra repoet med `pull_policy: build`.

## Review Triage Log

Gjennomgang 1 (08.10 kl. 23:02–23:05, PR #23), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter. Rettelsene er `761df48` og `3869f77`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH1, VG4, ECH5 | `docker compose --profile hent config` feiler i CI uten `.env` | false | Steget gikk grønt i CI på PR #23 (kjøring 37843689797), på en utsjekk uten `.env`. `config` krever ikke fila; `run` gjør det | ingen |
| BH2, ECH6 | `hent` har ingen `build`, så `compose run --rm hent` kan hente `ose-signal` fra et register og gi det `.env` | medium | Stemmer. Bare `app` bygget | patch: `build: .` og `pull_policy: build` på begge. Test og mutant D19 |
| BH3, VG1, ECH4 | CI-steget for hentingen avhenger av klokka og sjekker ikke koden | medium | Stemmer. Før kl. 22 på en børsdag stopper tidskontrollen med «0 kall brukt» og kode 0 | patch: `--hent-foer-kl-22`, bare «EODHD_API_KEY mangler», og kode 1. Mutant I8 |
| BH5, VG2 | Ingen sjekk av at `ose` kan skrive i nye volumer, særlig `data/raa` | medium | Stemmer. Webserveren skriver bare i `data/db`, og hentingen stopper før `data/raa` | patch: CI-steg med to nye navngitte volumer og `touch`, og en statisk test for `mkdir` og `chown`. Mutant D21 og I6 |
| VG3, ECH1 | Filmønstrene i `.dockerignore` gjelder bare roten, og `COPY src/ src/` tar med alt under `src/` | medium | Stemmer. `src/__pycache__` fra maskinen var i imaget | patch: mønstrene også med `**/`. Test og mutant D22, D24 |
| ECH11 | Oslo-tid i imaget kommer fra Debian, så `tzdata` fra `uv.lock` er ikke prøvd | medium | Stemmer. Slim-bildet har `/usr/share/zoneinfo` | patch: CI med `PYTHONTZPATH` tom. Mutant I7. Spec Change Log |
| BH4 | «Fast versjon, saa en ny bygging gir samme bilde» stemmer ikke for en tagg | low | Stemmer. Taggen kan bygges på nytt med Debian-oppdateringer | patch: kommentaren sier det. Ingen digest, fordi sikkerhetsoppdateringene bør komme med |
| BH6 | Svarnummereringen i spesifikasjonen og testene følger ikke instruksjonen | low | Stemmer | patch: testene viser til «svar 2 og 3». Spec Change Log |
| BH7 | Skillet mellom 3.1 og 3.2 står ikke i spesifikasjonen | low | Stemmer | patch: Implementation Notes |
| BH8, ECH2 | Funnsjekken i CI kjører som `ose` og har færre mønstre enn `.dockerignore` | low | Stemmer | patch: som root, med alle mønstrene og `__pycache__` under `/app` |
| BH9 | Avkrysningene står tomme, og «kl. 22:5x» er ikke lest fra klokka. «Planen» viser til en Utført-linje som ikke har planen | low | De to første stemmer. Den tredje er false: Utført-linjen kl. 22:39 i dagsfila sier hva planen tok med og de fire spørsmålene | patch: `[x]` og en Rettet-linje for klokkeslettet |
| BH10 | CI-steget for webserveren godtar enhver 200 | low | Stemmer | patch: krever `fetch_prices.py` i den tomme siden og en base i `/app/data/db`. Mutant I9 |
| ECH3 | Er containeren død, feiler `docker exec` før `docker logs` | low | Stemmer, med `bash -e` | patch: loggen skrives før `exec`, og `exec` har `\|\| echo` |
| ECH7 | `docker compose run --rm hent --hent-foer-kl-22` erstatter `command` | low | Stemmer. Flagget må gis med hele kommandoen | utsatt til 3.3, der README viser kommandoene (`deferred-work.md`) |
| ECH8 | waitress som PID 1 stopper ikke på SIGTERM, så `stop` venter 10 sekunder | low | Stemmer for PID 1 uten init | patch: `init: true` på begge. Test og mutant D20 |
| ECH9 | `USER root:root` slipper gjennom `test_ikke_root` | low | Stemmer | patch: delen før `:` sjekkes. Mutant D23 |
| ECH10 | En Dockerfile som slutter med `\` mister siste instruksjon i testene | low | Stemmer | patch: parseren feiler da |

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

**Etter gjennomgangen, 08.10 kl. 23:00–23:09.** Alle mutantene kjørt på nytt med de nye ankrene. Statiske: 24 av 24 drept, med de nye D19 `hent` uten `build` (`test_begge_bygger_fra_repoet_og_henter_aldri_imaget`), D20 uten `init` (`test_init_som_pid_1`), D21 bare `data/db` eies av `ose` (`test_mappene_til_volumene_eies_av_brukeren`; overlevde først, fordi testen godtok `data/db`), D22 `__pycache__` bare i roten og D24 `**/*-raa-*.json` fjernet (`test_filmoenstrene_gjelder_ogsaa_under_src`), og D23 `USER root:root` (`test_ikke_root`). I imaget, 9 av 9 drept:

| Mutant | Steget som feiler |
|---|---|
| I1–I4 som før | 2; 2 og 4; 4; 7 (compose er nå steg 7) |
| I5 `python:3.12-slim` | 1, byggingen |
| I6 bare `data/db` eies av `ose` | 6, skrivetilgang i nye volumer |
| I7 `tzdata` fjernet fra `/opt/venv` | 3, Oslo-tid med `PYTHONTZPATH` tom |
| I8 hentingen skriver ut «EODHD_API_KEY mangler» med kode 0 | 5. Første forsøk bygget ikke, fordi `sed` kjørte som `ose`. Flyttet før `USER ose` |
| I9 waitress serverer en tom Flask-app | 4, den tomme siden mangler |

**Suiten etter rettingene:** 1213 passed og 16 skipped (22 i `tests/test_docker.py`).

**Commands:**
- `uv run pytest -q` -- expected: grønn, med de nye testene i `tests/test_docker.py`.
- `docker build -t ose-signal:3-1 .` -- expected: bygger fra ren utsjekk.
- Kontrollene i CI-jobben `docker`, kjørt lokalt med eget prosjektnavn.
