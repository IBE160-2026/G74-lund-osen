---
title: 'Story 3.5 (3.5a): start med dobbeltklikk med uv, uten Docker'
type: 'feature'
created: '2026-10-23'
status: 'done'
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

*Lagt til 2026-10-24 (gruppens svar 23.10 kl. 23:31, b):* i en mappe med `.git` stopper den ekte versjonen før uv, `.env` og hentingen, også på main, og viser til «Download ZIP» og egen nøkkel. Det erstatter vernet «bare fra main» (VG1 og ECH9). Jobben `dobbeltklikk` kjører også «Start den ekte versjonen» i klonen, før demoen, og krever kode 1 og ingen `.env` på Windows og Mac. Klonen har `.git`, så skriptet stopper før uv, og ingen nøkkel trengs.

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

*Lukket 2026-10-24 (gruppens svar 23.10 kl. 23:31):*
- **Lukket VG1, ECH9:** vernet «bare fra main» er erstattet etter svaret b). I en mappe med `.git` stopper den ekte versjonen før uv, `.env` og hentingen, også på main, og viser til «Download ZIP» og egen nøkkel (`ebbb657`). Testene er `test_den_ekte_versjonen_stopper_i_en_mappe_med_git`, `test_start_sh_stopper_den_ekte_versjonen_i_en_klon_paa_main` og `test_start_ps1_stopper_den_ekte_versjonen_i_en_klon_paa_main`, som kjører skriptet i en midlertidig mappe med `git init -b main`, og CI-jobben `dobbeltklikk` på Windows og Mac.
- **Lukket BH15:** slått opp 24.10. Apples hjelpeside på norsk (support.apple.com/no-no/guide/mac-help/mh40616/mac) gir Apple-menyen > Systeminnstillinger, Personvern og sikkerhet i sidepanelet, «Åpne likevel» under Sikkerhet og passordet, og knappen står i omtrent en time etter forsøket. At høyreklikk og Åpne ikke lenger overstyrer Gatekeeper fra macOS 15, står i Apples utviklermelding fra august 2024. Den er lest i omtaler (9to5mac og AppleInsider), ikke selv. README-en og hjelpen har Personvern og sikkerhet først, og høyreklikk bare for macOS 14 og eldre (`ebbb657`). Ikke prøvd på en Mac.

*Mutanten 2026-10-24:* vernet tilbake til «bare fra main» i begge skriptene, kjørt én gang med `-x` i arbeidskopien på `2a3dd7e`, med testene i denne commiten før de ble committet, og med kopi før og sha256 etter. Fanget av `test_den_ekte_versjonen_stopper_i_en_mappe_med_git[start.ps1]`. Etterpå var sha256 lik kopien, og `git hash-object` lik `HEAD:<sti>` for begge. Med `-x` stoppet kjøringen ved første feil, så om testene som kjører skriptene, også fanger den, er ikke prøvd med mutanten.

*Rettet 2026-10-24 (gjennomgangen 24.10, BH12):* Apples utviklermelding fra 6. august 2024 er lest i ettertid, på developer.apple.com/news/?id=saqachfa. Den sier at høyreklikk ikke lenger overstyrer Gatekeeper i macOS Sequoia, og at brukeren må gå til System Settings > Privacy & Security.

## Gjennomgangen 24.10

Gjennomgang 24.10 etter hele settet (3287 bestått og 17 hoppet over), av endringene i dag: `a56aac3..8f89f9f` på main og `9006a78..fd7548c` på grenen. Linsene var Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 9 funn) og Verification Gap (VG, 4 funn), hver for seg og uten å endre noe i repoet. 29 funn ble 21 rader. De små funnene er rettet med en gang (svaret 23.10 kl. 15:53), i `b857582` (skriptene, README-en og hjelpen) og `624bc2e` (testene og CI).

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | CI-steget skilte ikke vernet fra «bare fra main» i en PR: med løsrevet HEAD ga også det gamle vernet kode 1 og ingen `.env` | medium | rettet i `624bc2e`: steget krever beskjeden fra vernet og at «Appen trenger uv» ikke står i utskriften |
| BH1 | Vernet gjelder bare dobbeltklikket, men teksten kunne leses som om ingenting henter i en klon | medium | rettet i `b857582`: README-en sier at kommandoene under «Uten Docker, med uv» og Docker også henter i en klon |
| BH5, BH6 | Kjøretestene var ikke vist å fange noe, og den strenge PATH kunne stoppe skriptet før vernet | medium | rettet i `624bc2e`: en kontroll uten `.git` må komme forbi vernet til spørsmålet om uv, og hele beskjeden kreves. Mutanten er ikke kjørt på nytt, fordi instruksjonen sier én gang |
| BH2 | En ZIP av en gren kjører den ekte versjonen med grenens kode | medium etter linsen, low | uten endring: valgt i svaret b). En ZIP har sin egen `data/` og `.env`, og regel 22 gjelder basen på gruppens maskin |
| VG2, BH10, ECH2 | Klonen i testene var en ufødt gren, så `rev-parse` ga `HEAD`, og `git init -b` krever git 2.28 | low og nit | rettet i `624bc2e`: `git init`, `symbolic-ref` og en tom commit, og testen sjekker at grenen er main |
| VG3 | `.git` som fil, som i en worktree, var ikke prøvd | low | rettet i `624bc2e`: kjøretestene har også `.git` som fil |
| VG4, ECH8 | Kommentaren over jobben sa at den ekte versjonen ikke kjøres i CI | nit og low | rettet i `624bc2e` |
| BH7, ECH5 | Ingen tidsgrense på de nye stegene | low | rettet i `624bc2e`: 5 minutter per steg |
| BH8 | Den statiske testen så ikke om vernet stoppet | low | rettet i `624bc2e`: linja etter vernet må være `Stopp` eller `stopp` |
| BH9 | Testen av CI leste resten av fila, ikke bare jobben | low | rettet i `624bc2e` |
| ECH1 | uv i samme mappe som bash eller git ga en rød test | low | rettet i `624bc2e`: testen hoppes over |
| ECH4 | WSL-starteren i WindowsApps ble ikke holdt utenfor | nit | rettet i `624bc2e` |
| ECH6 | Et eget git-repo i en ZIP-kopi fikk beskjeden «en klon av repoet» | low | rettet i `b857582`: «mappa har .git (en klon av repoet eller et eget git-repo)» |
| BH4, ECH9 | README-en sa «en annen sin nøkkel», resten «gruppens nøkkel», og «aldri» er sterkere enn koden | low | rettet i `b857582`: «med nøkkelen som ligger i den». Linjene i FR-401, AD-10 og under story 3.5 står, fordi de gjelder et dobbeltklikk i en klon, som er det vernet sjekker |
| BH3 | En `.git` høyere opp, og om mappa er riktig før vernet | low | uten endring: skriptene går til mappa de ligger i før vernet (`Set-Location` og `cd`), og en `.git` høyere opp sjekkes ikke |
| BH11 | «Mer informasjon» og «Kjør likevel» har ingen kilde fra Microsoft | low | uten endring: navnene gruppen så på skjermen. Står under «Åpent» |
| BH12 | At høyreklikk ikke virker fra macOS 15, var bare lest i omtaler | low | rettet: Apples melding er lest, se linja over |
| BH13 | 0 kall i linja under FR-401 var ikke vist | low | uten endring: slått opp 24.10 i `src/fetch_prices.py`, der `kjoer()` sjekker basen før nøkkelen og kvoten. ECH fant det samme |
| BH14 | Gruppens prøve var før commitene i dag | low | rettet i linja under «Prøven før flettingen»: CI-jobben `dobbeltklikk` prøver demoen på head-en |
| BH15, BH16 | Utført-linja mangler, og BH15-punktet under «Åpent» ser åpent ut | nit | uten endring: Utført-linja skrives til slutt, og dokumentet legges bare til. Linja under punktet sier at det er lukket |
| ECH3, ECH7 | git kreves i testene, og sjekken av git er tatt bort | nit | uten endring: klonen trenger git for commiten (VG2), og sjekken av git er tatt bort med vilje |

## Åpent

- **Godkjenningen på Mac** (BH15): teksten i README-en og hjelpen er ikke prøvd på en Mac. Prøven før flettingen viser om høyreklikk og Åpne er nok, eller om Personvern og sikkerhet må komme først.

*Lagt til 2026-10-24:* BH15 er lukket etter oppslaget under «Gjennomgangen 23.10». Teksten er fortsatt ikke prøvd på en Mac.

- **Navnene i advarselen fra Windows:** «Windows beskyttet PC-en» står i gruppens svar 24.10 kl. 11:22 og 11:28. «Mer informasjon» og «Kjør likevel» står slik instruksjonen 24.10 kl. 12:31 gir navnene på skjermen. Ingen side fra Microsoft med de to knappenavnene på norsk ble funnet 24.10.

## Det som ikke endres

- «Kom i gang», til gruppen har valgt hovedvei (svaret kl. 16:37).
- `src/app.py`, `src/demo.py` og `src/fetch_prices.py`.
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` og `.env` på denne maskinen røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.

## Prøven før flettingen

Flettingen stopper alltid før gruppen har prøvd: «Download ZIP» av grenen på GitHub, pakk ut i en ny mappe, og dobbeltklikk «Start demoen». Den ekte versjonen prøves aldri med gruppens nøkkel i en kopi, men i README-prøven med testerens egen konto.

*Gruppens prøve 24.10 (svarene kl. 11:22 og 11:28):* «Download ZIP» av grenen, pakket ut i Nedlastinger, og «Start demoen» etter advarselen «Windows beskyttet PC-en». Siden med «Eksempeltall» var oppe på under ett minutt. Prøven var før commitene 24.10 på grenen, og de endrer bare den ekte versjonen, tekstene og testene, ikke veien til demoen.

*Lagt til 2026-10-24 (gjennomgangen 24.10, BH14):* at demoen starter fra head-en, viser CI-jobben `dobbeltklikk` på Windows og Mac. Kjøringen står i Utført-linja for instruksjonen 24.10 kl. 12:31.
