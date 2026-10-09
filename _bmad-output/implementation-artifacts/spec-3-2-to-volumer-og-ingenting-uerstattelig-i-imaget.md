---
title: 'Story 3.2: To volumer, og ingenting uerstattelig i imaget'
type: 'feature'
created: '2026-10-09'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '2ed4587301306658304b3a5906a23492da036386'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-1-dockerfile-med-to-innganger.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 3.1 prøver at compose-fila har to navngitte, atskilte volumer, men ikke at de oppfører seg slik i drift. Øyeblikksbildene i `ose-raa` er uerstattelige (NFR-07, `AD-6`), og `vurdering` i basen er det også (`AD-7`). Ett volum over hele `data/`, eller en tjeneste som skriver utenfor volumene, ville tatt med seg det som ikke kan hentes på nytt (`AD-11`).

**Approach:** Volumene prøves i drift i CI med et eget compose-prosjekt: oppstart uten volumer, `ose-db` fjernet mens `ose-raa` står med filene sine, og en ny, tom base etterpå. Begge tjenestene kjører med skrivebeskyttet rotfilsystem og `/tmp` som tmpfs, så ingenting som må overleve, kan skrives utenfor volumene. `app` mister `ose-raa`.

## Planen

Planen er vist i chatten 09.10 og ført i `docs/ai-prompts/2026-10-09.md` (instruksjonen kl. 20:37 og Utført-linjen). Gruppen sa ja kl. 20:46 med disse svarene, som er beslutninger:

1. **`app` mister `ose-raa`.** Webserveren leser ikke øyeblikksbildene, så den skal heller ikke kunne skrive der. Trenger en side dem senere, får den volumet skrivebeskyttet i den storyen.
2. **`read_only: true` for begge tjenestene, med `/tmp` som tmpfs i begge.** waitress lager en midlertidig fil når et svar som venter på å bli sendt, er større enn `outbuf_overflow`, og SQLite kan legge midlertidige filer i `/tmp`. Det som ligger i `/tmp`, forsvinner med containeren. Prøven med skrivebeskyttet rotfilsystem kjører med de samme innstillingene som compose-fila, og en mutant uten tmpfs hører med.
3. **`docker compose down -v`:** en advarsel i `compose.yaml` nå, og teksten i README-en i 3.3, ført i `deferred-work.md`.

## Boundaries & Constraints

**Always:**
- `ose-db` på `/app/data/db` og `ose-raa` på `/app/data/raa`, hver for seg, uten montering på `/app/data` eller `/app`. Bare `hent` har `ose-raa`.
- Begge tjenestene: `read_only: true` og `tmpfs: /tmp`.
- Kommentaren ved `ose-db` i `compose.yaml` sier at basen ikke kan slettes: `vurdering` ligger der og kan ikke lages på nytt (`AD-7`, `AD-11`). Advarselen om `down -v` står i fila.
- Prøvene bruker egne compose-prosjekter, og bare deres egne containere og volumer fjernes. Lokalt kjøres `hent` aldri gjennom compose, bare med `docker run` uten `--env-file` og med `--network none`.

**Never:**
- README-teksten (3.3), demobasen (3.4), volumet `ollama` (10.2), arbeidskopien til den faste jobben.
- Ingen kommando fjerner eller tømmer volumer i prosjektet `ose-signal`. Ingen container kjører mot `data/db/ose.db` (regel 22).
- `src/` endres ikke.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Første oppstart | `docker compose up -d app`, ingen volumer finnes | `/` svarer 200 med den tomme siden, `ose-db` lages | — |
| Basen fjernet | en fil i `ose-raa`, `app` stoppet, `ose-db` fjernet, `up` på nytt | `/` svarer 200 med en ny, tom base, fila i `ose-raa` står | — |
| Skrivebeskyttet rot | begge inngangene med `--read-only --tmpfs /tmp` og volumene | webserveren svarer 200, hentingen uten nøkkel stopper med kode 1 | Skriver noe utenfor volumene eller `/tmp`, feiler det |

</frozen-after-approval>

## Code Map

- `compose.yaml` -- `app` uten `ose-raa`, `read_only` og `tmpfs` på begge, kommentarene om basen og `down -v`.
- `tests/test_docker.py` -- `_tjenester()` og `_verdier()` fra 3.1. `test_navngitte_volumer_aldri_data_paa_maskinen` krever i dag samme to volumer for begge tjenestene og må endres for `app`.
- `.github/workflows/tester.yml` -- jobben `docker`, med to nye steg: livsløpet med compose og skrivebeskyttet rot.
- `src/fetch_prices.py` -- skriver øyeblikksbildet med `open(fil, "x")` i `RAA_KATALOG`. `src/app.py` importerer ikke `lagring_fil`s `RAA_KATALOG` eller `SnapshotKilde`.
- `.venv/Lib/site-packages/waitress/adjustments.py` -- `outbuf_overflow = 1048576` og `inbuf_overflow = 524288` (waitress 3.0.2), `buffers.py` bruker `tempfile.TemporaryFile`.
- Spinen, `AD-11` -- datert merknad.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- README-teksten om `down -v` og basen, under 3.3.

## Tasks & Acceptance

**Execution:**
- [x] `compose.yaml` -- svarene 1–3.
- [x] `tests/test_docker.py` -- volumene per tjeneste, ingen overlapp, `read_only` og `tmpfs`, kommentarene.
- [x] `.github/workflows/tester.yml` -- livsløpet og skrivebeskyttet rot.
- [x] Spinen -- merknaden under `AD-11`.
- [x] `deferred-work.md` -- README-teksten for 3.3.

**Acceptance Criteria:**
- Given ingen volumer, when `app` startes med compose, then svarer `/` 200 og `ose-db` er laget.
- Given en fil i `ose-raa`, when `ose-db` fjernes og `app` startes på nytt, then står fila, og basen er ny og tom.
- Given begge inngangene med skrivebeskyttet rot og `/tmp` som tmpfs, then virker de, og uten tmpfs eller med en skriving utenfor volumene feiler prøven.

## Implementation Notes

- **waitress 3.0.2** i `.venv`: `outbuf_overflow = 1048576` og `inbuf_overflow = 524288` (`waitress/adjustments.py`), og `buffers.py` lager `tempfile.TemporaryFile("w+b")` når grensen nås. Verdien står i kommentaren i `compose.yaml`.
- **Livsløpet i CI** (steg 7) kjører `app` gjennom compose i prosjektet `ose-ci-32`, så `read_only`, `tmpfs` og volumene er de i `compose.yaml`. Det sjekker at ingen `ose-ci-32_*`-volumer finnes før `up`, at `/` svarer 200 med den tomme siden, at basen er laget, at `TemporaryFile` virker i `/tmp`, at `touch /home/ose/skrevet` feiler, at `app` bare har `/app/data/db` montert, og at en fil i `ose-raa` står etter at `ose-db` er fjernet og laget på nytt (merket i `ose-db` er borte). `trap` fjerner begge volumene i prosjektet, også når steget feiler.
- **`touch /app/...`** var første utgave av sjekken for skrivebeskyttet rot. Mutanten C3 (`app` uten `read_only`) overlevde, fordi `/app` eies av root, så `ose` kunne ikke skrive der uansett. Sjekken bruker nå `/home/ose`, som `ose` eier.
- **Oppryddingen i `trap`** sluttet først med `; true`. Under `bash -e` stoppet `docker volume rm` med feil når `down -v` alt hadde fjernet volumet, og steget fikk kode 1 selv om prøven gikk. Hver kommando har nå `|| true`, og mutantene C3 og C5 er kjørt på nytt etterpå.
- **Hentingen** (steg 8) prøves med `docker run --read-only --tmpfs /tmp` og to egne volumer, fordi CI ikke har `.env` og compose da nekter `hent`. `test_ci_proever_hent_med_de_samme_innstillingene` holder flaggene like med `hent` i `compose.yaml`.
- **Lokalt** er stegene kjørt fra en ren eksport av grenen (`git archive` av arbeidskopien) i en mappe uten `.env` og `data/`, så compose aldri leste nøkkelen. `hent` er aldri kjørt gjennom compose. Containeren `focused_booth` fra mutanten I3 i 3.1 (08.10 kl. 22:56) og volumene `ose-ci-32_ose-raa` og `ose-ci-32_ose-db` fra prøvene her lå igjen og er fjernet. Etter prøvene viser `docker volume ls` bare `ose-ki-ollama`.

## Spec Change Log

## Review Triage Log

Gjennomgang 1 (09.10 kl. 21:00–21:02, PR #24), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter. Rettelsene er `14a6384`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| VG1, BH2, BH1, ECH9, ECH10 | CI-steget for `hent` med skrivebeskyttet rot stopper ved nøkkelen før noe skrives, så det ser verken en manglende tmpfs eller en skriving utenfor volumene | medium | Stemmer. `kjoer` går ut i `hent_api_nokkel` før `open(fil, "x")` og basen | patch: steget skriver først det `hent` skriver, med de samme flaggene: `aapne_base` migrerer basen på `ose-db`, en fil i `ose-raa` og en `TemporaryFile` med `gettempdir() == '/tmp'`. Mutant C8 (uten tmpfs) feiler nå med «No usable temporary directory» |
| ECH1 | `trap` settes før forhåndssjekken, så finnes `ose-ci-32_*` fra før, fjerner oppryddingen dem | medium | Stemmer | patch: sjekken kjører før `trap`. Mutanten C5 la igjen volumet den laget, som vist |
| BH5, ECH11 | «Ny og tom base» sjekkes bare med merket og `test -s` | low | Stemmer | patch: siste skjemaversjon og 0 rader i `kurs` og `vurdering`, før og etter |
| BH6, ECH6, ECH7 | Testen som binder CI til compose, matcher løst: `--tmpfs /tmpx`, byttede volumer, og to `docker run` i samme steg | low | Stemmer. S8–S10 overlevde først | patch: hver `docker run` for seg, volumparene og `--tmpfs /tmp` med grense. S8, S9 og S10 drept |
| BH7 | `TemporaryFile` faller tilbake på andre mapper enn `/tmp` | low | Stemmer | patch: `tempfile.gettempdir() == '/tmp'` i begge stegene |
| ECH4 | Den negative `touch`-sjekken godtar enhver feil | low | Stemmer | patch: krever «Read-only file system» |
| ECH5 | `test -e merke` godtar enhver feil som «borte» | low | Stemmer | patch: kode 1 kreves |
| ECH2 | `docker volume ls \| grep -q` kan gi SIGPIPE under `pipefail` | low | Mulig med `pipefail`; GitHub bruker `bash -e` uten den som standard | patch: `--filter` og en variabel |
| BH10 | SQLite-skriving under `read_only` er ikke prøvd | low | Stemmer for `hent` | patch: dekket av VG1-rettingen (`aapne_base` med migrering). `app` migrerer ved første forespørsel i steg 7 |
| BH4 | At `ose-raa` står etter at `ose-db` er fjernet, kan ikke feile når `app` ikke har volumet | low | Stemmer. Skillet holdes av `test_volumene_overlapper_ikke` og volumtesten. Steget viser at `ose-raa` er et eget volum som overlever, ikke at compose skåner det | ikke endret. `down` uten `-v` er README-tekst i 3.3 |
| BH3 | Hentesteget avhenger av datoen: utenfor kalenderen i `boersdag.py` stopper det før nøkkelen | low | Stemmer, som steg 5 fra 3.1. Den ekte hentingen stopper da også (NFR-08) | ikke endret. Kalenderen må utvides før 2027 uansett |
| ECH3 | En lokal kjøring av steg 7 bygger og tagger `ose-signal` | low | Stemmer. `pull_policy: build` gjør at `ose-signal` bygges på nytt fra repoet ved neste `up` uansett | ikke endret |
| BH9 | Oppføringen i `deferred-work.md` leses som om README-en alt sier det | low | Lista er det som gjenstår, og oppføringen sier at teksten tas i 3.3 | ikke endret |
| BH8 | Spesifikasjonen henger etter arbeidet | false | `d48e57d` har Implementation Notes, avkrysningene og mutantene. Diffen var laget før den | ingen |
| VG2 | `tmpfs` kan vises i `.Mounts`, så monteringssjekken feiler | false | Steg 7 er grønt lokalt og i CI (kjøring 37977139490) med `/app/data/db` alene | ingen |
| ECH8 | Lang syntaks for volumer deles feil i testen | false | Fila bruker kort syntaks. Lang syntaks ville gi en feil i testen, ikke et stille bestått | ingen |

## Verification

**Mutantene, 09.10 kl. 20:52–20:59.** Statiske mot `tests/test_docker.py`, 8 av 8 drept:

| Mutant | Testen som fanger den |
|---|---|
| S1 ett volum over hele `data/` | `test_navngitte_volumer_aldri_data_paa_maskinen`, `test_volumene_overlapper_ikke` |
| S2 `ose-raa` på `/app/data/db` | de samme to |
| S3 `app` får `ose-raa` | `test_webserveren_har_ikke_oeyeblikksbildene` og volumtesten |
| S4 kommentaren om basen fjernet | `test_advarslene_om_basen_og_down_v` |
| S5 advarselen om `down -v` fjernet | `test_advarslene_om_basen_og_down_v` |
| S6 `app` uten `read_only` | `test_skrivebeskyttet_rot_med_tmp_som_tmpfs` |
| S7 `hent` uten `tmpfs` | `test_skrivebeskyttet_rot_med_tmp_som_tmpfs`, `test_ci_proever_hent_med_de_samme_innstillingene` |
| S8 CI-steget uten `--tmpfs /tmp` | `test_ci_proever_hent_med_de_samme_innstillingene` |

I CI, mot stegene i jobben `docker` fra en ren eksport, 7 av 7 drept etter rettingene over:

| Mutant | Steget som feiler |
|---|---|
| C1 `app` med ett volum over `/app/data` | 7 |
| C2 `app` uten tmpfs | 7, `TemporaryFile` |
| C3 `app` uten `read_only` | 7. Overlevde med `touch /app`, drept med `/home/ose` |
| C4 `app` med `ose-raa` | 7, monteringene |
| C5 volumene laget på forhånd | 7 |
| C6 webserveren skriver `/app/startet` før waitress | 7 |
| C7 `main()` i hentingen skriver `/home/ose/startet` | 8. Første forsøk med `sed` i Dockerfile bygget ikke, og `sitecustomize` overlevde, fordi Python bare skriver en melding når den feiler |

C8, CI-steget for hentingen uten `--tmpfs /tmp`, gir ingen feil i kjøringen: hentingen uten nøkkel skriver ikke i `/tmp`. Den fanges av S8.

**Suiten:** 1218 passed og 16 skipped, mot 1213 og 16 før (27 i `tests/test_docker.py`).

**Etter gjennomgangen, 09.10 kl. 21:02–21:05.** Statiske: S1–S10, 10 av 10 drept. S8 (CI-steget uten `--tmpfs /tmp` i hentekommandoen), S9 (volumene byttet) og S10 (`--tmpfs /tmpx`) overlevde først, fordi steget har to `docker run`, og testen godtok at én av dem var riktig. I CI: C1–C8, 8 av 8 drept med de rettede stegene, blant dem C8, `hent`-steget uten tmpfs («No usable temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', '/app']»), og C7 («Read-only file system: '/home/ose/startet'»). Alle ni stegene er grønne med det ekte imaget. Suiten: 1218 passed og 16 skipped.

**Commands:**
- `uv run pytest -q` -- expected: grønn.
- Stegene i jobben `docker`, kjørt lokalt med egne prosjektnavn.
