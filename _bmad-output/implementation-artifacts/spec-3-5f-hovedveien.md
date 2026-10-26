---
title: 'Story 3.5 (3.5f): hovedveien i «Kom i gang»'
type: 'docs'
created: '2026-10-26'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'ab85068'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5a-dobbeltklikk-med-uv.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** «Kom i gang» har Docker Desktop som hovedmåten. Dobbeltklikket uten Docker (3.5a) står bak en pil under «Mer for den som vil», og tabellen og «Du trenger» sier at Docker trengs.

**Løsningen:** dobbeltklikket blir den anbefalte hovedveien og en egen del først i «Kom i gang». Docker blir den andre veien og uv i terminalen den tredje, med en liste «Velg vei etter hva du har» som lenker rett inn til hver av dem.

**Grunnlaget:** avgjørelsen 25.10 kl. 11:32 under story 3.5 i `epics.md` (punkt a), innspillet kl. 11:26 (tre veier etter behov, og dobbeltklikket som egen del) og avgjørelsen kl. 11:49 (dobbeltklikket bruker bare uv, også når Docker kjører). Dockerfilen og `compose.yaml` leveres som før.

## Slik er det i dag (slått opp 26.10 på `ab85068`)

- **`README.md`:** `## Kom i gang` med tabellen (raden «Trenger»: «Bare Docker Desktop» og «Docker Desktop og en gratis nøkkel fra EODHD»), «Du trenger» med Docker Desktop, så `### Felles for begge` med steg 1–4 og tre bilder, «Slik limer du inn en kommando», «Velg vei», pilene til demoen og den ekte versjonen, «Står du fast?» og «Mer for den som vil». Dobbeltklikket står i pila «Start med dobbeltklikk, uten Docker» under «Mer for den som vil», og begynner med «Øverst i mappa, når den er pakket ut som i steg 2, ligger fire filer».
- **«Til faglærer»** viser til demoen etter steg 1–4 (`#felles-for-begge`).
- **«Mappestruktur»** nevner `src/`, `tests/`, `docs/`, bildene, `_bmad-output/`, `.github/`, Docker-filene, `start/` med `.gitattributes`, og `_bmad/` med `.claude/skills/`. `CLAUDE.md`, `pyproject.toml`, `uv.lock`, `README.md`, `.env.example`, `.gitignore`, `.mailmap` og de fire startfilene står ikke der.
- **`docs/hjelp.md`** sier at stegene 1–4 er felles for begge versjonene, har «Start med dobbeltklikk» etter «Stopp», og «Hvordan starter jeg neste gang?» nevner bare Docker.
- **§9 i `docs/kvalitetssikring.md`:** tabellen i Prøve 1 begynner med Docker Desktop (rad 1–16) og har uv i rad 17–21. Dobbeltklikket står ikke der.
- **Hjelpetekstene i appen** (`src/hjelpetekster.py`, malene, `src/ki_tekst.py`) nevner verken Docker som hovedmåten eller «Kom i gang». `ki_tekst.py` viser til «Den lokale modellen» og «Egen nøkkel til Gemini, Anthropic eller OpenAI» i README-en, som står. Den tomme siden viser uv-kommandoen utenfor Docker (`HENTEKOMMANDO`).
- **Testene for den gamle rekkefølgen:** `tests/test_docker.py` (blant annet `test_demoen_foerst_og_zip_foer_kommandoene`, `test_tabellen_nevner_begge_og_hvilken_som_er_anbefalt`, `test_til_faglaerer_begynner_med_demoen_den_ekte_versjonen_og_testene` og hjelperne `_kom_i_gang`, `_seksjon` og `VELG_VEI`) og `tests/test_dobbeltklikk.py::test_readme_og_hjelpen_har_advarselen_og_godkjenningen`, som krever at «Kom i gang» ikke nevner skriptene.

## Kontrollpunktene

- a) Overskriften er «Kom i gang: nedlasting og installasjon», og ankeret `kom-i-gang` virker fortsatt. Under tabellen står «Velg vei etter hva du har» med en lenke rett inn til hver vei, i rekkefølgen «Enklest: dobbeltklikk, uten Docker» (anbefalt), «Med Docker Desktop» og «Uten Docker, med uv» under «Mer for den som vil».
- b) Dobbeltklikket er en egen del først, ikke bak en pil: last ned med den direkte lenken `https://github.com/IBE160-2026/G74-lund-osen/archive/refs/heads/main.zip` eller «Code» og «Download ZIP», pakk ut, finn de fire filene øverst i mappa og dobbeltklikk «Start demoen». Resten av teksten står.
- c) «Felles for begge» heter «Med Docker Desktop», med stegene, bildene og kommandoene som før. Steg 2 har også lenken, og «Velg vei» der heter «Velg versjon». Tabellen og «Du trenger» sier ikke at Docker trengs, og «Til faglærer» viser først til dobbeltklikket og så til Docker.
- d) «Mappestruktur» forklarer hver fil og mappe i rota som git sporer, også `CLAUDE.md`, `pyproject.toml` og `uv.lock`.
- `docs/hjelp.md` følger hovedveien (regel 19). Lista i §9 følger hovedveien i samme commit, med Docker som reserve.
- Testene: «Ville feilet hvis» dobbeltklikket ikke sto først, Docker-veien eller en kommando manglet, en lenke var død, ZIP-lenken gikk til feil gren eller repo, eller noe i rota manglet i «Mappestruktur».

## Valg som er gjort her

- **Ankeret.** GitHub lager ankeret av hele overskriften, `kom-i-gang-nedlasting-og-installasjon`. En linje `<a name="kom-i-gang"></a>` rett over overskriften beholder `#kom-i-gang`, så «Innhold» og lenker utenfra virker som før.
- **Dobbeltklikket som punktliste, ikke nummerert.** «Steg 1–4» og «steg 4» betyr Docker-stegene i README-en, i `docs/hjelp.md` og i §9. Med egne tall i dobbeltklikket ville «steg 4» bety to ting.
- **Pila «Uten Docker, med uv»** får ankeret `uten-docker-med-uv` i `<summary>`, som pilene til demoen og den ekte versjonen, så lista kan lenke rett inn.
- **§9 får en ny tabell først i Prøve 1,** «Hovedveien: dobbeltklikket», med radene D1–D6. Tabellen med Docker og uv står som reserve, med en datert linje. Ingen rad fjernes, fordi instruksjonen ikke lar linjer fjernes fra andre dokumenter enn README-en og `docs/hjelp.md`.
- **Hjelpetekstene i appen endres ikke:** de nevner ikke hovedveien (slått opp over).

## Planen

1. Spesifikasjonen.
2. README-en, `docs/hjelp.md`, §9 og testene i samme commit (regel 19 og instruksjonen).

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: Docker-delen tatt ut av «Kom i gang».

## Gjennomgangen

Fylles ut etter hele settet.

## Åpent

## Det som ikke endres

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `.env` i repoet røres ikke.
- Skriptene i `start/`, Dockerfilen og `compose.yaml` endres ikke.
- PR #99 (8.6b) røres ikke.
