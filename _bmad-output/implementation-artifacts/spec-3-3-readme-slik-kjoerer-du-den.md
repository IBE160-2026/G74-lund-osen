---
title: 'Story 3.3: README — «Slik kjører du den»'
type: 'feature'
created: '2026-10-09'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '13090feddeeb716ffa748c81d151d6fadda4ac34'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-2-to-volumer-og-ingenting-uerstattelig-i-imaget.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** «Kom i gang» i README-en viser bare uv, mens Docker er hovedmåten etter rettelsen 05.10 og svaret fra hjelpelæreren. Den tomme siden viser uv-kommandoen også i containeren (oppføringen fra 2.2), flagg til `hent` erstatter kommandoen (ECH7 fra 3.1), og README-en sier ikke at `docker compose down -v` tar med seg det som ikke kan hentes på nytt (3.2).

**Approach:** «Kom i gang» skrives helt på nytt med Docker først og uv som alternativ, og sier bare det som stemmer nå. Den tomme siden velger kommando fra to konstanter etter miljøet, og testene holder README-en og siden like. `hent` får `entrypoint`, så flagg legges til.

## Planen

Planen er vist i chatten 09.10 og ført i `docs/ai-prompts/2026-10-09.md` (instruksjonen kl. 22:57 og Utført-linjen). Gruppen sa ja kl. 23:13 med disse svarene, som er beslutninger:

1. **Dockerfile setter `ENV OSE_I_DOCKER=1`.** Den tomme siden viser `HENTEKOMMANDO_DOCKER` («docker compose run --rm hent») når variabelen er satt, og `HENTEKOMMANDO` ellers. Malen bruker bare `{{ hentekommando }}`, README-en har begge, og de to CI-stegene krever Docker-kommandoen på siden. **Avvik fra storyen:** kontrollpunktet «Kommandoen i tom-tilstanden kommer fra én konstant» blir to konstanter, én for hver måte å kjøre på. Grunnen: Docker er hovedmåten og uv alternativet, og én kommando ville vært feil på den ene av dem.
2. **`hent` får `entrypoint: ["python", "src/fetch_prices.py"]` og ingen `command`,** så flagg legges til. Testen fra 3.1 krever i stedet at ingen `entrypoint` eller `command` migrerer.
3. **README-en viser ikke `--hent-foer-kl-22`.** Den råder til å hente etter kl. 22 på en børsdag eller i helgen, og sier hva som skjer på dagtid: hentingen stopper med 0 kall og forklarer hvorfor.

## Boundaries & Constraints

**Always:**
- «Kom i gang» med Docker først: `git clone`, kopi av `.env.example` til `.env` med egen gratisnøkkel, `docker compose up --build` på http://127.0.0.1:5000, `docker compose run --rm hent` og `docker compose down`. uv er alternativet.
- Teksten om `down -v` og basen (`AD-7`, `AD-11`): stopp med `docker compose down`, aldri `-v`.
- Kommandoene virker i PowerShell og på macOS og Linux.
- «Status» stemmer når 3.3 er flettet, med demoen (3.4) og KI-laget som det neste. «Mappestruktur» får `Dockerfile`, `compose.yaml` og `.dockerignore`.
- `.env` med den ekte nøkkelen røres aldri. Ingen kommando skriver ut miljøet til `hent` i repoet. Prøvene kjøres i en ren eksport av grenen uten `.env` og `data/`, med en oppdiktet verdi og egne prosjektnavn.

**Never:**
- Demoen og demokommandoen (3.4), KI og den lokale modellen (10.2), egne nøkler til KI (10.7), skjermbilder med ekte data.
- `--hent-foer-kl-22` i README-en.
- `src/fetch_prices.py` endres ikke.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Tom side i Docker | `OSE_I_DOCKER=1`, tom base | «Ingen kurser i basen ennå. Hent dem med `docker compose run --rm hent`.» | — |
| Tom side med uv | ingen `OSE_I_DOCKER` | samme tekst med `uv run python src/fetch_prices.py` | — |
| Flagg til `hent` | `docker compose run --rm hent --les-inn FIL` | `python src/fetch_prices.py --les-inn FIL` | — |

</frozen-after-approval>

## Code Map

- `src/app.py` -- `HENTEKOMMANDO` (linje 54) og de to `render_template` med `hentekommando=` (linje ~217 og ~231). Ny `HENTEKOMMANDO_DOCKER` og en funksjon som velger etter `OSE_I_DOCKER`.
- `src/templates/index.html` -- linje 127, `{{ hentekommando }}`. Endres ikke.
- `tests/test_app.py` -- `test_kommandoen_paa_den_tomme_siden_staar_i_readme` (linje ~545) og testene som krever `HENTEKOMMANDO` i siden.
- `Dockerfile` -- `ENV OSE_I_DOCKER=1`. `compose.yaml` -- `hent` med `entrypoint`, uten `command`.
- `tests/test_docker.py` -- `test_hent_kjoerer_hentekommandoen` og `test_ingen_migrering_i_eget_steg` endres for `entrypoint`.
- `.github/workflows/tester.yml` -- de to stegene som krever `fetch_prices.py` på siden (linje ~94 og ~147).
- `README.md` -- «Status», «Kom i gang» og «Mappestruktur».
- Spinen, `AD-10` -- datert merknad. `epics.md` -- datert linje under 3.3 om de to konstantene.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- oppføringene fra 2.2 (linje 84), ECH7 fra 3.1 og `down -v` fra 3.2.

## Tasks & Acceptance

**Execution:**
- [x] `src/app.py`, `Dockerfile`, `tests/test_app.py` -- svar 1.
- [x] `compose.yaml`, `tests/test_docker.py` -- svar 2.
- [x] `.github/workflows/tester.yml` -- Docker-kommandoen på siden.
- [x] `README.md` -- «Status», «Kom i gang» med svar 3, `down -v`, «Mappestruktur», og tester for README-en.
- [x] Spinen, `epics.md` og `deferred-work.md`.

**Acceptance Criteria:**
- Given imaget og en tom base, when siden åpnes, then viser den `docker compose run --rm hent`, og README-en har den samme kommandoen.
- Given uv uten `OSE_I_DOCKER`, then viser siden `uv run python src/fetch_prices.py`, og README-en har den.
- Given `docker compose run --rm hent --hent-foer-kl-22`, then får `fetch_prices.py` flagget.
- Given README-en, then har den advarselen om `down -v`, rådet om tidspunkt, ingen `--hent-foer-kl-22` og ingen bildelenker utenom CI-merket.

## Implementation Notes

- **`hentekommando()`** i `app.py` gir `HENTEKOMMANDO_DOCKER` bare når `OSE_I_DOCKER` er `"1"`, og `HENTEKOMMANDO` ellers, også for `"0"` og tom verdi. Begge `render_template` bruker den. En autouse-fixture i `tests/test_app.py` fjerner variabelen, så testene ikke avhenger av miljøet på maskinen.
- **README-en** er kontrollert mot den gamle teksten (regel 13). Tre ting falt ut i første utkast og er lagt inn igjen: «før midnatt», hva hentingen gjør på en dag børsen er stengt, og at appen bare leser fra basen. `--hent-foer-kl-22` er tatt ut med vilje (svar 3). «Status» beholder setningene om begge versjonene, børsmeldingene og sprintstatusen.
- **Windows:** `cp .env.example .env` virker i PowerShell (`cp` er alias for `Copy-Item`), og `notepad .env` står i README-en. CRLF i `.env` er prøvd 09.10 kl. 23:17 i en ren eksport av grenen, med en oppdiktet verdi og prosjektnavnet `ose-proeve-33`, uten å kjøre `hent`: `docker compose --profile hent config` ga verdien uten `\r`, `app` hadde ingen `EODHD_API_KEY`, og `hent` hadde `entrypoint` uten `command`. Den oppdiktede `.env` er fjernet. `python-dotenv` i uv-veien leser også CRLF.
- **CI:** de to stegene som krevde `fetch_prices.py` på den tomme siden, krever nå `docker compose run --rm hent`, fordi imaget setter `OSE_I_DOCKER=1`. Alle ni stegene er grønne fra en ren eksport.

## Spec Change Log

## Review Triage Log

## Verification

**Mutantene, 09.10 kl. 23:21–23:24.** Statiske mot `tests/test_app.py`, `tests/test_docker.py` og `tests/test_readme.py`, 12 av 12 drept:

| Mutant | Testen som fanger den |
|---|---|
| R1 README og siden med hver sin kommando (konstanten endret) | `test_kommandoen_paa_den_tomme_siden_staar_i_readme` |
| R2 malen skriver kommandoen selv | den samme og to til |
| R3 Dockerfile uten `OSE_I_DOCKER` | `test_dockerfile_setter_variabelen_appen_leser` |
| R4 appen ser bort fra variabelen | `test_den_tomme_siden_i_docker_viser_docker_kommandoen`, `test_bare_verdien_1_gir_docker_kommandoen` |
| R5 enhver verdi gir Docker | `test_bare_verdien_1_gir_docker_kommandoen` |
| R6 `hent` med `command` | `test_hent_kjoerer_hentekommandoen` |
| R7 advarselen om `down -v` fjernet | `test_advarselen_om_down_v_og_basen` |
| R8 README med tjenesten `henting` | `test_tjenestene_i_readme_finnes_i_compose` |
| R9 README viser `--hent-foer-kl-22` | `test_raadet_om_tidspunkt_uten_flagget` |
| R10 skjermbilde i README | `test_ingen_bilder_utenom_ci_merket` og lenketesten |
| R11 uten `docker compose up --build` | `test_docker_foerst_og_uv_som_alternativ` |
| R12 `entrypoint` som migrerer | `test_ingen_migrering_i_eget_steg`, `test_hent_kjoerer_hentekommandoen` |

I CI fra en ren eksport: C1, imaget uten `OSE_I_DOCKER`, drept i steg 4 og 7 (siden viser uv-kommandoen).

**Suiten:** 1226 passed og 16 skipped, mot 1218 og 16 før.

**Commands:**
- `uv run pytest -q` -- expected: grønn.
- Stegene i jobben `docker`, kjørt lokalt fra en ren eksport med egne prosjektnavn.
