---
title: 'Story 3.5 (3.5f): hovedveien i «Kom i gang»'
type: 'docs'
created: '2026-10-26'
status: 'in-review'
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
- **Lenken i steg 2 står i teksten under bildet.** Steg 2 hadde 65 ord, grensen i `test_stegene_er_nummerert_og_har_hoeyst_65_ord`, så lenken i selve steget ga 70. Tittelen «Last ned koden.» er låst av `STEGENE_FOER_3_3H`. Teksten under bildet hører til steg 2 og telles for seg, høyst 25 ord. Den telles nå som stegene, med lenketeksten og uten adressen bak (svaret 13.10 kl. 23:50), og har 21 ord.
- **Mappestrukturen og startfilene.** Lenkene i «Mappestruktur» har stien som tekst, og en sti med mellomrom virker ikke som lenke på GitHub uten vinkelparenteser. De fire startfilene står derfor med navnet uten filendelsen, som før, og testen godtar dem slik.

## Planen

1. Spesifikasjonen.
2. README-en, `docs/hjelp.md`, §9 og testene i samme commit (regel 19 og instruksjonen).

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: Docker-delen tatt ut av «Kom i gang».

*Utfallet 26.10 kl. 13:13:54–13:13:55 på `b5e4faa`:* alt fra `### Med Docker Desktop` til `### Står du fast?` tatt ut av `README.md` (91 linjer), kjørt med `-x` mot `tests/test_docker.py`, `tests/test_dobbeltklikk.py` og `tests/test_readme.py`. Fanget av `TestCompose::test_porten_er_den_samme_overalt_og_ikke_5000`, som er eldre. Kjørt igjen kl. 13:14:04 med `-k TestHovedveien`: fanget av `test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil`. Fila var lik HEAD etter begge: samme sha256 som kopien, og samme git-objekt som `HEAD:README.md` (`47b5617`).

*Utfallet 26.10 kl. 13:28:50–13:28:51 på `a052c74`, etter rettelsene fra gjennomgangen:* den samme mutanten med `-k TestHovedveien` ble fanget av `test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil`, og fila var lik `HEAD:README.md` (`29bb197`) etterpå.

## Gjennomgangen

Gjennomgang 26.10 etter hele settet (fil for fil, 49 filer: 3648 bestått, 24 hoppet over, 0 feilet, 13:14:22–13:22:46 på `b5e4faa`), av diffen `ab85068..b5e4faa`, med Blind Hunter (BH, 17 funn), Edge Case Hunter (ECH, 11) og Verification Gap (VG, 4, alle fem kravene i instruksjonen dekket). Dommen i tabellen er vår. Rettet i `a052c74`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | «Pakk ut alle» på Windows lager `G74-lund-osen-main` inne i en annen, og dobbeltklikket sa ikke «den innerste», så de fire filene ble ikke funnet | high | **rettet** i `a052c74`: «øverst i den innerste `G74-lund-osen-main`, der README ligger», D1 spør om det, og `docs/hjelp.md` har «Jeg finner ikke de fire filene.» |
| ECH2 | Et dobbeltklikk inne i ZIP-fila finner ikke `start/`, og vinduet lukkes uten beskjed | medium | **rettet** i `a052c74`: «Pakk ut først» i README-en, og «Vinduet lukkes med en gang.» i hjelpen. Slått opp i `Start demoen.cmd` (`%~dp0start\start.ps1`), ikke prøvd |
| BH2, ECH8 | Windows skjuler `.cmd`, men viser `.command`, og README-en sa ikke hvilken som skal tas | medium | **rettet** i `a052c74`: «På Windows tar du den som bare heter «Start demoen»», og et svar i hjelpen |
| BH3, ECH4 | «verken git, Docker eller konto» stemmer ikke for den ekte versjonen, som trenger konto hos EODHD | medium | **rettet** i `a052c74`: «verken git eller Docker, og demoen trenger ingen konto» |
| BH4 | «Mac er ikke prøvd ennå, bare i CI» sa ikke hva som er prøvd | medium | **rettet** i `a052c74`: Docker Desktop er ikke prøvd på Mac, og dobbeltklikket kjøres i CI på macOS (jobben `dobbeltklikk` i `tester.yml`, `macos-latest`) |
| BH8, ECH3 | Hjelpen hadde ingen svar for de vanligste feilene på hovedveien | medium | **rettet** i `a052c74`: tre spørsmål først under «Start med dobbeltklikk». Feil i installasjonen av uv står under «Åpent» |
| ECH5, BH6 | Feltene i Prøve 1 er for Docker, og den daterte linja sto rett under feltet for commiten | medium | **rettet** i `a052c74`: feltet «uv fra før» er lagt til, så den daterte linja står etter et eget felt for hovedveien |
| BH12 | D6 lager en `.env` uten nøkkel som reserven senere møter | low | **rettet** i `a052c74`: D6 sletter `.env` før reserven. D3 står som én rad |
| BH13, ECH11 | Testen for «Innhold» overskrev overskriften uten å sjekke den | low | **rettet** i `a052c74` |
| BH14, VG3 | Startfilene ble godtatt hvor som helst i «Mappestruktur» | low | **rettet** i `a052c74`: de kreves i punktet om `start/` |
| ECH9 | Mappa kan få tall i navnet etter en ny nedlasting | low | **rettet** i `a052c74`: «Pakk ut.» lenker til svaret i hjelpen |
| BH5 | Rad 1–23 i den daterte linja spriker med spesifikasjonen | low | **avvist:** tabellen har rad 1–23, Docker 1–16, uv 17–21 og to felles (ECH bekreftet det) |
| BH7 | Lenker til `#felles-for-begge` utenfor README-en | low | **avvist:** de to treffene, i `docs/ux-logg.md` og spesifikasjonen 3.3d, er sitater i historikken, ikke lenker |
| BH9 | «Klar: Med en gang» stemmer ikke for første start | low | **avvist:** raden gjelder dataene i demoen, og «Første gang tar det en stund» står i «Du trenger» |
| BH10 | Det tekniske avsnittet om skriptene står åpent | low | **avvist:** instruksjonen sier at resten av teksten står |
| BH11 | «anbefalt» om både demoen og dobbeltklikket | low | **avvist:** «(anbefalt)» ved dobbeltklikket står i instruksjonen |
| BH15 | ZIP-lenken gir main, så D1 før flettingen viser ikke 3.5f | low | **under «Åpent»** |
| BH16 | «Åpent» var tom | low | **rettet** her |
| BH17 | «Neste gang» nevner ikke bonuskvoten | low | **avvist:** «Når kan jeg hente?» i hjelpen og raden «Klar» sier det |
| VG1 | Ingen generell vakt for døde lenker til ankre | low | **avvist:** `test_lenkene_virker` sjekker ankeret i hver lenke i README-en og `docs/hjelp.md` |
| VG2 | Repoet og grenen står fast i testen | low | **avvist:** testen sjekker README-en mot GitHub-siden den selv lenker til, uten nett |
| VG4, ECH10 | Ordtellingen i bildeteksten uten adressen, og testen for rota hoppes over uten git | low | **avvist:** til opplysning; tellingen følger svaret 13.10, og CI har git |
| ECH6, ECH7 | Den daterte linja ved commit-feltet, og Safari som pakker ut selv | low | ECH6 **rettet** med ECH5. ECH7 **avvist:** «Jeg finner ikke ZIP-fila på Mac.» står i hjelpen |

## Åpent

- **BH15:** prøven av hovedveien (D1) må tas etter flettingen, fordi den direkte lenken gir main.
- **BH8:** hjelpen har ikke eget svar når installasjonen av uv feiler, for eksempel på en maskin uten lov til å installere. Hva vinduet sier da, er ikke slått opp her.
- **ECH2:** at vinduet lukkes inne i ZIP-fila, er slått opp i `Start demoen.cmd`, ikke prøvd.

## Det som ikke endres

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `.env` i repoet røres ikke.
- Skriptene i `start/`, Dockerfilen og `compose.yaml` endres ikke.
- PR #99 (8.6b) røres ikke.
