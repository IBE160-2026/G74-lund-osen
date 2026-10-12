---
title: 'Story 3.4: Demoversjonen'
type: 'feature'
created: '2026-10-10'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b294a9514aca2d455e72b6da3942abe7fff49910'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3-readme-slik-kjoerer-du-den.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kan bare prøves med en egen EODHD-nøkkel. Faglærer, sensor og medstudenter skal kunne se hvordan den virker uten konto, og demoen er hovedveien for vurderingen (FR-411, svaret fra hjelpelæreren 05.10).

**Approach:** En egen kommando lager `data/db/demo.db` med 15 oppdiktede selskaper, kurser etter en skrevet regel med fast frø, og én vurdering per aksje og børsdag regnet med `vurder()`. Basen er merket som demobase, og merket avgjør «Eksempeltall» på sidene. Én bryter velger hvilken base webserveren åpner. Vaktene hindrer at demobasen og den ekte basen blandes, begge veier.

## Planen

Planen er vist i chatten 10.10 og ført i `docs/ai-prompts/2026-10-10.md` (instruksjonen kl. 12:06 og Utført-linjen). Gruppen sa ja kl. 12:27 med disse svarene, som er beslutninger:

1. **Navnene.** Joakim kontrollerte de 15 tickerne for hånd mot lista over aksjer i Oslo hos Euronext 10.10 kl. 12:25, og ingen av dem står der. Rådet søkte samme dag på nettet etter de 15 navnene, nøyaktig skrevet, og fant ingen selskaper med de navnene. Programmet henter aldri lista.
2. **Port 5000 for demoen.** App og demo kan ikke kjøre samtidig. `docker compose down` stopper også demotjenestene, og README-en sier hvordan man bytter (PR 2).
3. **Fast sluttdato, fredag 2026-10-09.**
4. **To pull requests.** PR 1 er demoen med uv. PR 2, med Docker og README, bygges på en ny gren fra main etter at PR 1 er flettet.

I tillegg, fra instruksjonen:
- Normalfordelingen og volumene lages fra `random()` med Box–Muller, fordi Python bare lover at `Random.random()` gir samme rekke med samme frø på tvers av versjoner.
- En base som ikke finnes eller ikke kan leses, regnes ikke som demobase i vakten i hentingen, og hentingen går videre som i dag.
- Demobaser lages bare i midlertidige mapper og prøveprosjekter, aldri i `data/db/` i repoet (regel 22).

## Boundaries & Constraints

**Always:**
- `DEMOUNIVERS` har de 15 i tabellen under. Ingen symbol eller ticker står i `AKSJEUNIVERS`.
- Kursene: 195 handelsdager fra 2026-01-02 til 2026-10-09 etter `boersdag.er_boersdag`. Hver aksje har sitt eget frø, `FROE * 100 + nummeret i lista`. Daglig logavkastning er drift + volatilitet · z, der z er normalfordelt fra Box–Muller på `random()`. Drift og volatilitet følger sektoren. Volumet er et nivå per aksje ganger `exp(0,3 · z)`, og med sannsynlighet 0,04 per dag tre ganger det. `adjusted_close` er lik `close`. Kursene avrundes til to desimaler, volumet til heltall. Siste dag faller Brattfjell Energi 6 % med tre ganger volumet, så minst én aksje skiller seg ut.
- Tilstandene: Varde Systemer har bare de siste 30 dagene (nylig notert, «signalet kunne ikke regnes» og «Trenger 51 dager»), Tareøy Havbruk mangler siste dag («ingen kurs fra dagen»), og Matfjord Merkevarer har ingen kurser («Uten data i denne kilden»).
  *Rettet 2026-10-10 kl. 14:48:* Tareøy Havbruk har siste dag etter gruppens beslutning, se Spec Change Log.
- Hver børsdag i serien har én rad i `vurdering` per aksje, lik det `vurder()` gir for serien fram til dagen, skrevet med `SqliteVurderingslager.skriv` uendret og lagerets klokke stilt på dagen (`AD-7`).
- Merket er `PRAGMA application_id = 0x4F534544`. Bare demokommandoen setter det.
- Demokommandoen nekter en fil uten merket, også en tom fil. En demobase lages på nytt fra bunnen.
- Hentekommandoen og `--les-inn` nekter en demobase før noe annet. En base som ikke finnes eller ikke kan leses, regnes ikke som demobase.
- Bryteren er `OSE_DEMO=1`, eller `--demo` til `python src/app.py`. Med bryteren åpner webserveren `demo.db` ved siden av `ose.db` og lager den aldri. Mangler den, viser siden kommandoen som lager den. Uten bryteren åpnes `ose.db` som før.
- «Eksempeltall» står på hver side som viser en base med merket, og på ingen side med en base uten. Merket leses fra basen, ikke fra bryteren.
- Portene som skriver, tar lista som parameter, med `AKSJEUNIVERS` som standard. Testen som holder `aksje` lik `AKSJEUNIVERS` i den ekte basen, står (`AD-21`).

| Ticker | Navn | Sektor |
|---|---|---|
| BRFE | Brattfjell Energi | Energi |
| HVDO | Havdyp Olje | Energi |
| NLYS | Nordlysfeltet | Energi |
| SLVP | Sølvbank Petroleum | Energi |
| FJSB | Fjellheim Sparebank | Finans |
| TRHF | Trygghavn Forsikring | Finans |
| VRDS | Varde Systemer | Industri |
| KVST | Kvitstein Mineral | Materialer |
| JGRD | Jordgrøde Gjødsel | Materialer |
| BLGT | Bølgetopp Tankers | Shipping |
| LSTF | Lastfjord Container | Shipping |
| SGNT | Signalnett | Telekom |
| LKSV | Laksevik Sjømat | Sjømat |
| TROY | Tareøy Havbruk | Sjømat |
| MTFJ | Matfjord Merkevarer | Konsum |

**PR 1 (denne grenen, 3-4):** `src/demo.py`, merket, vaktene begge veier, lista som parameter i skriveportene, bryteren og siden når demobasen mangler, «Eksempeltall» og testene.

**PR 2 (ny gren fra main etter PR 1):** demotjenestene `demo-lag` og `demo` i profilen `demo`, volumet `ose-demo`, CI-steget, «Kom i gang» med demoen først og hvordan man bytter, testen for kommandoene, `docs/kvalitetssikring.md` klar for README-prøven, og merknader i spinen.

**Never:**
- KI-tekstene (3.4b), hovedindeksen (2.8), lista som kan byttes (2.11) og resten av punkt 4.4 i endringsforslaget 08.10, som ikke er bygget.
- Demokommandoen gjør ingen nettkall, leser ingen nøkkel og importerer verken `requests`, `eodhd` eller `fetch_prices`.
- Ingen demobase i `data/db/` i repoet under byggingen. `hent` kjøres aldri gjennom compose lokalt.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ny demobase | `demo.db` finnes ikke | lages med merket, 15 aksjer, 195 dager, 2 925 vurderinger | — |
| Demobase finnes | `demo.db` med merket | lages på nytt, lik den forrige | — |
| Fil uten merket | `demo.db` uten merket, også tom | ingenting skrives, kode 1 | Utskriften sier hvorfor |
| Henting mot demobase | `ose.db` med merket | 0 kall, kode 1 | Utskriften sier hvorfor |
| Henting uten base | `ose.db` finnes ikke eller kan ikke leses | som i dag | — |
| Bryteren, ingen demobase | `OSE_DEMO=1`, `demo.db` mangler | siden viser `DEMOKOMMANDO`, ingen fil lages | — |

</frozen-after-approval>

## Planen for PR 2

Fra instruksjonen kl. 15:23 i `docs/ai-prompts/2026-10-10.md`, på grenen `3-4-docker` fra main etter `0ed87be`.

**Prøven først, 10.10 mellom kl. 15:23 og 15:26 (etter at instruksjonen ble committet, før planen ble skrevet), Docker Desktop 4.91.0, motor 29.8.0 og Compose v5.5.1.** I egne prosjekter (`ose-proeve-down`, `ose-proeve-env`, `ose-proeve-dep`) med `python:3.13.15-slim` som allerede lå på maskinen, og bare deres egne volumer er fjernet:
- `docker compose down` uten profilen stopper **ikke** demoen. Den går med kode 0, demo-containeren kjører videre, og nettverket blir stående («Resource is still in use»). Svar 2 i Planen sier at `docker compose down` også stopper demotjenestene. Det stemmer ikke med denne Compose-versjonen.
- `docker compose --profile demo down` stopper demoen, og også `app` når den kjører. `docker compose down demo` stopper også demoen.
- En tjeneste i en annen profil med `env_file: .env`, som `hent`, hindrer ikke `docker compose up demo` når `.env` mangler.
- `depends_on` med `condition: service_completed_successfully` mellom to tjenester i profilen `demo` starter `demo-lag` først, og `demo` når den er ferdig.

**Delene, med commit og push etter hver:**
1. `compose.yaml`: `demo-lag` med `entrypoint: ["python", "src/demo.py"]`, som `hent`, og `demo` med `environment: OSE_DEMO: "1"` og `depends_on` på `demo-lag`. Begge har profilen `demo`, `build: .`, `image: ose-signal`, `pull_policy: build`, `init`, `read_only`, `tmpfs /tmp` og bare `ose-demo:/app/data/db`. `demo` har `127.0.0.1:5000:5000`. Testene i `tests/test_docker.py`.
2. `src/app.py`: `DEMOKOMMANDO_DOCKER = "docker compose run --rm demo-lag"` og `demokommando()`, valgt med `OSE_I_DOCKER` som `hentekommando()` (ECH7). Siden og feilsiden bruker den.
3. CI: et steg i jobben `docker` med prosjektet `ose-ci-34`, uten `.env`: `docker compose -p ose-ci-34 up -d --build demo`, siden svarer 200 med «Eksempeltall», så stoppkommandoen fra README-en, og ingen container igjen. Bare `ose-ci-34_ose-demo` fjernes. Steget med `config --services` får profilen `demo`.
4. README, «Kom i gang»: demoen først med `docker compose up --build demo`, så den ekte versjonen som i 3.3, og at siden lastes på nytt etter hentingen. Byttet: demoen stoppes med `docker compose --profile demo down`, fordi `docker compose down` ikke gjør det. uv-veien med `--demo`. Status og Mappestruktur. En test krever at kommandoene i README-en er de samme som i koden og `compose.yaml`.
5. `docs/kvalitetssikring.md`: avsnittet for README-prøven 13.–16.10.
6. Spinen: merknader under `AD-9`, `AD-10` og `AD-11`.

**Avvik fra punktene i instruksjonen:** ingen. At `docker compose down` ikke stopper demoen, er dekket av instruksjonen: README-en gir `docker compose --profile demo down` der den forklarer byttet. Svar 2 i Planen står, og denne linjen sier hva som gjelder.

*Rettet 2026-10-10 kl. 16:18:* «Svar 2 i Planen står» over er upresist. Delen av svar 2 som sier at `docker compose down` også stopper demotjenestene, stemmer ikke uten `-p`. Port 5000 og at README-en sier hvordan man bytter, gjelder. Den frosne teksten endres ikke uten gruppen (BH2).

*Rettet 2026-10-10 kl. 16:18:* funnet etter gjennomgangen, i egne prosjekter: med `-p NAVN` stopper `docker compose -p NAVN down` også demoen. Uten `-p`, med prosjektnavnet fra `name:` i fila, stopper den ikke demoen. Prøvd begge veier samme ettermiddag med Compose v5.5.1. README-en bruker ikke `-p`, så det er den oppførselen brukeren får. CI-steget brukte først `-p ose-ci-34` og bruker nå `-f` mot en kopi av `compose.yaml` med `name: ose-ci-34`, og prøver at `down` uten profilen lar demoen kjøre (`2fa6f9f`).

## Planen for PR 3

Fra instruksjonen kl. 16:54 i `docs/ai-prompts/2026-10-11.md` (planen) og kl. 20:32 (ja, med svar og endringer), på grenen `3-4-readme` fra main etter `5665f5c`.

**Målet:** en som aldri har brukt Docker eller et terminalvindu, starter demoen bare ved å følge README-en, på Windows og på Mac.

**Beslutninger (svarene kl. 20:32):**
1. Koden hentes med «Download ZIP». Har noen fått koden som mappe eller ZIP fra før, pakker de ut og går til steg 4.
2. Linjene fra terminalen står som tekst.
3. Mac står som «ikke prøvd» i §9 til noen har prøvd stegene på en Mac.
4. Ingen bilder nå. Forbudet fra 3.3 og `test_ingen_bilder_utenom_ci_merket` står. Bilder kan tas inn senere, tidligst bildet av demosiden etter 8.0d, og da bare fra `docs/bilder/readme/`, med alt-tekst, og aldri av den ekte versjonen. Marian bekrefter «Engine running», «Pakk ut alle», «Windows PowerShell» og om en sti med mellomrom får anførselstegn, før gjennomgangen.
5. Flettes før PR #28 og 8.0b: i kveld hvis den er klar og kontrollert, ellers mandag på dagtid. Aldri mellom kl. 21:40 og slutten av hentingen.

**Marians ønske kl. 17:08:** «Før du begynner» øverst. Hvert steg begynner med det man skal gjøre, i én kort setning, og sier så hva man ser når det har gått bra. «Hvis noe går galt» blir en kort FAQ rett etter stegene, og steg 1, 2 og 6 peker dit.

**Boundaries for PR 3:**
- Én kommando per kodeblokk, og ingen `#` på en kommandolinje i hele «Kom i gang».
- Linjene som viser at demoen er klar, er kopiert fra en kjøring 11.10 i prosjektet `ose-readme-pr3` (se Implementation Notes).
- Den ekte versjonen, byttet og uv står som før, med kommandoene delt opp og kommentarene flyttet til teksten. Punktet «Når du henter» (PR #28) og Status-linja (8.0b) røres ikke.
- Merket steg 7 siterer, er det samme som i malene, og en test krever det.
- §9 i `docs/kvalitetssikring.md` følger stegene i samme commit, med en datert linje under tabellen.

**Delene, med commit og push etter hver:** a) README «Kom i gang» med §9 og de testene som må følge med, b) de nye testene.
*Lagt til 2026-10-11 kl. 21:14:* c) steg 3, steg 4 og FAQ-en etter Marians svar kl. 21:14 (`docs/ai-prompts/2026-10-11.md`), d) rettingene etter gjennomgangen.

**Marians svar kl. 21:14**, før gjennomgangen, som beslutning 4 ba om:
- «Engine running» står nederst i vinduet.
- «Pakk ut alle» (Extract All) stemmer, og det ble en mappe med samme navn inni. En åpnet ZIP-fil ser ut som en vanlig mappe uten å være pakket ut, så steg 3 sier at man må trykke «Pakk ut alle», og FAQ-en har et punkt om det.
- Windows viser filene som README og compose, uten filendelse.
- «Windows PowerShell» stemmer, men «Windows PowerShell ISE» står også i lista, og den skal ikke velges.
- En sti med mellomrom får anførselstegn når mappa dras inn i PowerShell.

## Code Map

- `src/kursdata.py` -- `kontroller_skriving` (linje 162) sjekker mot `AKSJEUNIVERS`. Får `univers` som parameter.
- `src/lagring_sqlite.py` -- `SqliteKurslager` (118), `SYMBOLER` og `_kontroller_noekkel` (192, 213) i vurderingslageret. Får `univers`. Nytt: `DEMOMERKE`, `er_demobase(sti)` og `demo_sti()` ved siden av `BASE_STI`.
- `src/fetch_prices.py` -- `kjoer` (547) og `les_inn` (775) får vakten først.
- `src/app.py` -- `_aapne_basen` (118) og `_migrer_en_gang`, rutene `markedsoversikt` og `aksjedetalj`. Bryteren, `DEMOKOMMANDO` og «Eksempeltall» gjennom en context processor.
- `src/templates/index.html`, `aksje.html`, `basefeil.html` -- merket etter `<body>`, og teksten når demobasen mangler.
- `src/signalberegning.py` -- `vurder` og `nodvendige_dager` (51), uendret.
- `tests/conftest.py` -- flytter `BASE_STI` til `tmp_path`, så `demo_sti()` følger med.

## Tasks & Acceptance

**Execution (PR 1):**
- [x] `src/kursdata.py`, `src/lagring_sqlite.py` -- lista som parameter, merket og `er_demobase`.
- [x] `src/demo.py` -- `DEMOUNIVERS`, regelen og demokommandoen.
- [x] `src/fetch_prices.py` -- vakten i `kjoer` og `les_inn`.
- [x] `src/app.py` og malene -- bryteren, siden når demobasen mangler, «Eksempeltall».
- [x] `tests/test_demo.py` -- kontrollpunktene.

**Execution (PR 2):**
- [x] `compose.yaml` -- `demo-lag`, `demo` og `ose-demo` (`e9199f2`).
- [x] `src/app.py`, `src/demo.py` -- `DEMOKOMMANDO_DOCKER` og `demokommando()` (`cbbad89`).
- [x] `.github/workflows/tester.yml` -- demosteget og profilen `demo` i `config --services` (`957c90d`, `2fa6f9f`).
- [x] `README.md` -- «Kom i gang» med demoen først, byttet og uv med `--demo` (`27d7241`).
- [x] `docs/kvalitetssikring.md` -- §9 for README-prøven (`ea1c7d2`).
- [x] Spinen -- merknader under `AD-9`, `AD-10` og `AD-11` (`fe22cd3`).

**Acceptance Criteria:**
- Given to kjøringer av demokommandoen, then er basene like rad for rad.
- Given en demobase og bryteren av, then sier sidene «Eksempeltall». Given en ekte base og bryteren på, then gjør de det ikke.
- Given en demobase som `ose.db`, when hentingen eller `--les-inn` kjøres, then stopper den før noe annet med kode 1.

## Implementation Notes

- **Skriveportene:** `kontroller_skriving`, `SqliteKurslager` og `SqliteVurderingslager` (`skriv` og `les`) tar lista som skrives, med `AKSJEUNIVERS` som standard. Med standardlista er feilteksten den samme som før («ikke et symbol i AKSJEUNIVERS»), fordi to tester krever den.
- **Merket:** `DEMOMERKE = 0x4F534544` («OSED») i `lagring_sqlite.py`. `er_demobase` åpner med `aapne_base(..., kjoer_migrasjoner=False, skrivebeskyttet=True)` (`mode=ro`), fordi testen fra 2.1b krever at ingen annen kode i `src/` kaller `sqlite3.connect`.
- **Demokommandoen** skriver med `PRAGMA synchronous = OFF` på sin egen tilkobling. Med fsync per transaksjon tok de 2 925 vurderingene 34 sekunder på Windows, uten 2,7. Demobasen kan alltid lages på nytt. En demobase som finnes, slettes med `-wal` og `-shm` og lages fra bunnen.
- **Vakten i hentingen** er `nekt_demobase(base_sti, skriv)`, første linje i `kjoer` og `les_inn`. Den kommer før klokka: en test gir et øyeblikk uten sone og får kode 1, ikke `ValueError`. En base som ikke finnes, eller en fil som ikke er en SQLite-base, gir ingen stopp. Alle 190 testene i `tests/test_fetch_prices.py` er grønne uendret.
- **Endringer i `src/fetch_prices.py`:** bare `nekt_demobase` og kallet til den i `kjoer` og `les_inn`, og et avsnitt i docstringen til `kjoer`.
- **Webserveren:** med bryteren migreres og lages demobasen aldri. Mangler `demo.db`, får oversikten `DEMOKOMMANDO`, og aksjedetaljen gir 404. «Eksempeltall» kommer fra en context processor som leser `g.eksempeltall`, satt fra merket i basen ved hver forespørsel. Feilsiden viser navnet på basen bryteren valgte.
- **«samme frø gir like baser»** sammenligner `aksje`, `kurs`, `kursserie`, `vurdering`, merket og `skjema_versjon` uten kolonnen `anvendt`, som er tidspunktet migrasjonen ble kjørt.
- **Regel 22:** alle demobaser under byggingen er laget i `tmp_path` eller i scratch-mappa for økta. `data/db/` har ingen `demo.db`.

- **PR 3, kjøringen som linja i steg 6 er kopiert fra** (11.10, ca. kl. 20:34): Docker Engine 29.8.0 og Compose v5.5.1. En kopi av `compose.yaml` i repoet, `compose-pr3.yaml`, med `name: ose-readme-pr3`, `image: ose-readme-pr3` og porten `127.0.0.1:5098:5000`, fordi Marians demo, `ose-signal-demo-1`, brukte port 5000. Kommandoen var `docker compose -p ose-readme-pr3 -f compose-pr3.yaml up --build demo`. Den viste `Attaching to demo-1`, ikke loggen fra demo-lag, og til sist `demo-1  | INFO:waitress:Serving on http://0.0.0.0:5000`. Utskriften gikk til en fil, ikke til et terminalvindu, så en eventuell linje med valg fra Compose i et ekte vindu er ikke sett. Etterpå ble bare det kjøringen startet, fjernet: `--profile demo down`, volumet `ose-readme-pr3_ose-demo`, imaget `ose-readme-pr3` og kopien av `compose.yaml`. Sjekket etterpå: ingen container eller image fra `ose-readme-pr3`. `ose-signal-demo-1` og `ose-signal_ose-demo` sto urørt.
- **PR 3, bilder:** ingen (beslutning 4). `test_ingen_bilder_utenom_ci_merket` står.

## Spec Change Log

- **2026-10-10 kl. 12:45, Tareøy Havbruk (avvik fra planen):** Boundaries sier at Tareøy Havbruk mangler siste dag, for å vise «ingen kurs fra dagen». Det virket ikke: oversikten leser vurderingen for datoen til nyeste kurs for hver aksje, så Tareøy viste vurderingen for 08.10, og datoen over tabellen ble 2026-10-08, fordi den er den eldste nyeste datoen (story 8.0). Regelen er tatt ut, og alle 14 med kurser har siste dag. «ingen kurs fra dagen» er ikke blant tilstandene demoen viser, som «hentingen feilet». En test krever at datoen over tabellen er 2026-10-09. **Til gruppen:** avviket står her og i PR-en, og kan tas tilbake før flettingen.

- **Gruppen godtok avviket** i instruksjonen kl. 14:46 i `docs/ai-prompts/2026-10-10.md`, sammen med ja til flettingen av PR #26: datoen over tabellen er den eldste av datoene til nyeste kurs (story 8.0), så en aksje uten siste dag kan ikke vise «ingen kurs fra dagen» uten å flytte datoen for hele siden. Demoen viser ikke den tilstanden, slik den heller ikke viser «hentingen feilet».

- **2026-10-11, PR 3 (README-en for en som aldri har brukt Docker):** Marian prøvde demoen etter README-en 11.10 og fant ikke ut hvor kommandoene skulle skrives. Hun limte dem inn i Docker Desktop og i en tom PowerShell-linje, og to kommandoer havnet på samme linje. README-prøven 13.–16.10 skal kunne gjøres av en som aldri har brukt Docker eller et terminalvindu, så «Kom i gang» skrives om i nummererte steg, med én kommando per boks og en FAQ. Planen og svarene står i «Planen for PR 3».

- **2026-10-11 kl. 21:53, PR 3 i kortere form:** Marian syntes kl. 21:22 at demodelen av «Kom i gang» var for lang og så komplisert ut. Kl. 21:37 godkjente hun en kortere form: én linje om hva man trenger, seks steg på én til to linjer, «Stopp», og «Står du fast?» med spørsmålene som `<details>` med `<summary>`, sortert etter steget. Alt fra de åtte stegene og «Hvis noe går galt» som ikke er med i de seks stegene, er flyttet dit, og fem spørsmål er nye. Grunnen: målgruppen er en som aldri har brukt Docker eller et terminalvindu, og en lang side gjorde det vanskeligere å se hva man skal gjøre. «Steg 1, 2 og 6 peker dit» fra Marians ønske kl. 17:08 er erstattet av én lenke til «Står du fast?» i linja øverst. Commit `50e6c2e`.
- **Rettet samme kveld, etter gjennomgangen av den korte formen:**
  - «fem spørsmål er nye» over gjelder de fem instruksjonen kl. 21:53 nevner. Bare «Mappa lar seg ikke dra inn i vinduet» har nytt innhold. De fire andre, og spørsmålene «Hva skjer under installasjonen?», «Jeg finner ikke ZIP-fila på Mac.», «Hvilket vindu skal jeg åpne?», «Hva betyr cd, og hvordan ser jeg at det gikk?», «Hva skal jeg se etter i vinduet?», «Terminal spør om tilgang til Nedlastinger (Mac).» og «Jeg har fått koden fra før.», er nye overskrifter over innhold fra de åtte stegene.
  - Stegnumrene i «Planen for PR 3» gjelder den første formen med åtte steg. I den korte formen er «går til steg 4» i beslutning 1 steg 3, og «merket steg 7 siterer» er merket i steg 6.
  - Marians ønske kl. 17:08 om at hvert steg sier hva man ser når det har gått bra, gjelder fortsatt. Hvert av de seks stegene har en slik sjekk etter `9dd0f48`.
- **2026-10-11 kl. 22:32, «Kom i gang» helhetlig og kort:** Marian kl. 22:21: README-en skal vise de to versjonene med forskjellen forklart, anbefale den ekte, ha lite informasjon, og FAQ-en var for lang. «Kom i gang» har nå en tabell over de to versjonene, felles steg 1–4, den ekte versjonen (steg 5–9) før demoen (steg 5–7), og «Står du fast?» med 8 spørsmål. De 28 spørsmålene og punktene om nøkkelen, hentingen, tom oversikt, dataene og porten er flyttet til `docs/hjelp.md`, ordrett og sortert etter steg. Den ekte versjonen står nå før demoen, så kravet fra PR 2 om at demoen er den første kommandoen gjelder ikke lenger, og testen med det navnet krever i stedet «Download ZIP» før `cp .env.example .env`. Commitene `706b9f5` og `4ae6a30`. **Til gruppen:** punktet «Når du henter», som PR #28 endrer, står nå i `docs/hjelp.md` under «Når kan jeg hente?». Flettes PR #28 etter denne, må endringen dens føres der.
  - *Rettet samme kveld, etter gjennomgangen:* «ordrett» over stemmer ikke helt. Det som er flyttet til `docs/hjelp.md`, er 28 spørsmål og 5 punkter, 33 i alt. 7 av spørsmålene står også i README-en, og «Oversikten er tom.» er det åttende spørsmålet der. Endret ved flyttingen, for at svarene skal stemme med den nye formen:
    - henvisningene til steg i «Hva betyr cd …», «Hva skal jeg se etter i vinduet?» og «Hvordan starter jeg neste gang?»
    - «Nei.» foran svaret om porten
    - subjektet «Dataene», som falt ut og er satt inn igjen
    - etter gjennomgangen: kontoen hos EODHD, Ledetekst for den ekte versjonen, «Siden åpnes ikke.» for begge versjonene, og setningen om et lukket vindu, som hadde falt bort

- **2026-10-11, instruksjonen kl. 23:48, «Kom i gang» øverst og «Status» kortere:** Marian kl. 23:41–23:46: README-en begynner med beskrivelsen, så «Til faglærer», så «Kom i gang», så «Status». «Status» er i vanlige ord, uten storynumre og uten demokommandoen, som sto uten stegene før den. Tabellen i «Kom i gang» sier det de to punktene om versjonene sa. Etter gjennomgangen står også at kursene hentes fra EODHD hver børsdag og at dagens vurdering lagres per aksje. At sidene leser fra basen, står ikke lenger i README-en. Steg 5 i den ekte versjonen sier ikke hvor nøkkelen står hos EODHD, fordi Marian ikke husker det (svaret kl. 23:55 i `docs/ai-prompts/2026-10-11.md`). Commitene `85cad6a` og `56d886f`.
  - **Konfliktene ved flettingen** (rettes når de oppstår, ikke nå):
    - Grenen 8-0b (PR #29) endrer den gamle statuslinja, som begynte med «Børsdagskontrollen (2.3) …». Den finnes ikke lenger etter PR 3. Når 8-0b henter main, må den nye statuslinja i stedet si at hjelpen bak «?» er ferdig.
    - PR #28 (2.3b) endrer punktet «Når du henter» i README-en. Det står nå i `docs/hjelp.md` under «Når kan jeg hente?», og endringen må føres der.
    - Generelt: den som fletter 2.3b, 8.0b, 8.0c eller 8.0d, flytter saken fra «Neste» til «Flettet til main» i statuslinja. Grenen 8-0b sin egen statuslinje sier også at 2.3b er flettet. Det føres bare hvis PR #28 faktisk er flettet først.
    - 8.0d står i statuslinja og i `epics.md`, men ikke i `sprint-status.yaml` før den planlegges (instruksjonen kl. 15:57). Derfor lenker statuslinja også til `epics.md`.

- **2026-10-12, instruksjonen kl. 00:22, ny beskrivelse øverst:** Marian godkjente 11.10 kl. 23:50 en ny beskrivelse under gruppelinja. Den sier hva appen viser for en som ikke kjenner den: 15 aksjer som omsettes mye, de tre sjekkene ved navn, signalstyrken fra 0 til 3, og at appen ikke gir råd om å kjøpe eller selge (NFR-06). Den gamle sa «15 likvide Oslo Børs-aksjer» og nevnte verken sjekkene eller rådet. `test_beskrivelsen_foelger_koden_og_gir_ikke_raad` henter antallet aksjer fra `AKSJEUNIVERS`, og antallet sjekker og navnene deres fra `signalberegning.py`, så README-en må følge når lista endres (2.11 og 2.12). §9 er ikke rørt.
  - Mutantene, hele testsettet for hver, med koden satt tilbake fra en kopi: B1 (rådet tatt ut), B2 (18 aksjer), B3 («Fire enkle sjekker»), B4 («fra 0 til 4») og B5 (en sjekk med feil navn) ble alle fanget av `test_beskrivelsen_foelger_koden_og_gir_ikke_raad`. B6 (en aksje tatt ut av `AKSJEUNIVERS`) ble stoppet underveis fordi maskinen hadde lite minne, og er ikke kjørt ferdig. Mutanten ble liggende i `src/kursdata.py`, ble satt tilbake fra kopien, og fila er lik HEAD.

- **2026-10-12, instruksjonen kl. 10:25, «Hvorfor bare 15 aksjer?»:** Marian lurte kl. 10:19–10:22 på om beskrivelsen øverst skulle si at kursene kommer fra gratisnivået hos EODHD. Hun valgte et spørsmål i `docs/hjelp.md` i stedet, så beskrivelsen holder seg kort. Det står under «Den ekte versjonen», rett etter «Hva med nøkkelen?». `test_hvorfor_bare_15_aksjer` henter tallet fra `AKSJEUNIVERS`. Mutantene A1 (16 i overskriften), A2 (16 i svaret), A3 (spørsmålet flyttet til «Demoen») og A4 (en aksje tatt ut av `AKSJEUNIVERS`) ble fanget, kjørt bare mot `tests/test_docker.py`. A4 ble også fanget av `test_beskrivelsen_foelger_koden_og_gir_ikke_raad`, som dermed er prøvd mot B6, mutanten som ble stoppet natt til 12.10.

- **2026-10-12, instruksjonen kl. 10:45, «en henting bruker 15»:** punkt 3 fra gjennomgangen av PR #31 (Marian kl. 10:38). Setningen i svaret på «Hva med nøkkelen?» i `docs/hjelp.md` var ikke knyttet til `AKSJEUNIVERS` i noen test, så den kunne bli stående med feil tall når lista endres (2.11 og 2.12). `test_hvorfor_bare_15_aksjer` krever nå «en henting bruker N», der N er lengden av lista. `docs/hjelp.md` er ikke endret. Mutantene: «en henting bruker 16» i hjelpen, og setningen tatt ut. Begge ble fanget, kjørt bare mot `tests/test_docker.py`. Punkt 2, om 16 kall når indeksen hentes, er ført i `deferred-work.md`, fordi det først kan gjøres med story 2.8.

- **2026-10-12, instruksjonen kl. 11:15, «Den er under utvikling og ikke ferdig.»:** Marian kl. 11:12: at appen er under utvikling, sto bare i «Status», som kommer etter hele «Kom i gang». Setningen står nå også i beskrivelsen øverst, rett etter «Appen gir ikke råd om å kjøpe eller selge.», og `test_beskrivelsen_foelger_koden_og_gir_ikke_raad` krever den. Mutantene, setningen tatt ut og setningen flyttet til «Status», ble begge fanget, kjørt bare mot `tests/test_docker.py`. **Ved innleveringen** ses setningen på igjen, sammen med linja nederst på sidene om at appen er under arbeid, og punktet i `docs/innlevering.md` om å bytte den. Begge er planlagt i 8.0c og finnes ikke ennå.

- **2026-10-12, instruksjonen kl. 20:43, «Til faglærer» øverst:** Marian kl. 12:12: briefen var gjemt langt nede i «Dokumentene». Under «Til faglærer:» står nå fire linjer: briefen (versjon 8, taggen `arbeidskrav-product-brief-v8`), plan og krav, leveranselista, og prosessen og KI-bruken. Ingen filer er flyttet, fordi stiene brukes i lenker, tagger og BMAD. `test_til_faglaerer_lenker_til_briefen_med_gjeldende_tag` henter taggen fra regel 17 i `CLAUDE.md`. Mutantene, v7 i lista og lenken til briefen tatt ut, ble begge fanget, kjørt bare mot `tests/test_docker.py`. `docs/innlevering.md` sier at statusen fra 05.10 er utdatert.

## Review Triage Log

Gjennomgang 1 av PR 1 (10.10 kl. 13:02–13:06, PR #26), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter. Rettelsene er `5bcdef0`, `f9bbdcd` og `680fcf6`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH2, ECH5, ECH2, ECH3 | En bygging som stopper halvveis, etterlater en halv base med merket, og en gammel `-journal` kan bli liggende | high | Stemmer. Merket ble satt før innholdet, i fila webserveren leser | patch: bygges i `demo.db.ny` og byttes inn med `os.replace`. `-journal`, `-wal` og `-shm` fjernes. Test og mutant M19 |
| BH6 | Uten bryteren migrerer webserveren en demobase som ligger som `ose.db` | medium | Stemmer. `_migrer_en_gang` kom før merket ble lest | patch: en demobase åpnes skrivebeskyttet og migreres ikke. Test med kallene, mutant M20 (overlevde først, fordi en migrering av en base på siste versjon ikke endrer en byte) |
| BH5 | Webserveren åpner demobasen skrivbar | medium | Stemmer, `mode=rw` | patch: `skrivebeskyttet=True` |
| VG1 | 503 med bryteren og en ulesbar `demo.db` er ikke prøvd, heller ikke navnet på feilsiden | medium | Stemmer | patch: test for begge rutene, som krever `demo.db` og `DEMOKOMMANDO`. Mutantene M21 og M23 |
| ECH6 | En demobase uten kurser viser hentekommandoen, som skriver til `ose.db` | medium | Stemmer | patch: `DEMOKOMMANDO` med bryteren. Mutant M22 |
| VG3 | `--demo` er bare prøvd som tekst | medium | Stemmer | patch: `les_flagg(argv)`, testet ved å kalle den. Testen lekket `OSE_DEMO` til testene etter, og det er også rettet |
| BH11 | At samme frø gir samme base på andre plattformer, er ikke prøvd | medium | Stemmer. `math.log`, `cos` og `exp` er ikke lovet like overalt | patch: et fingeravtrykk av `kurs` regnet på Windows. CI på Linux ga samme (kjøring 38047102791) |
| ECH1, ECH11 | Vakten slipper gjennom en låst demobase eller en med varm journal | low | Stemmer, den går videre ved enhver lesefeil | ikke endret: gruppens beslutning kl. 12:27 er at en base som ikke kan leses, ikke er en demobase, og hentingen går videre som før |
| VG2 | «Eksempeltall» på feilsiden er ikke prøvd | low | Stemmer | patch: test der lesingen feiler etter at demobasen er åpnet |
| ECH4 | `PermissionError` når `demo.db` er åpen i et annet program, gir traceback | low | Stemmer på Windows | patch: `main` fanger `OSError` med kode 1 |
| ECH10, BH | `main(argv)` ser bort fra `argv` | low | Stemmer | patch: argparse. Test for et ukjent argument |
| ECH9 | En demobase på eldre skjema gir 503 uten råd | low | Stemmer | patch: feilsiden viser `DEMOKOMMANDO` med bryteren |
| ECH7 | I Docker viser siden uv-kommandoen for demoen | low | Stemmer | utsatt til PR 2, som har Docker-kommandoen |
| ECH8 | `demo.db` kan forsvinne mellom `is_file()` og åpningen | low | Med `os.replace` forsvinner den ikke under en ny bygging | ikke endret |
| BH1 | Kommentaren ved `DEMOKOMMANDO` sier at README og en test holder dem like | low | Stemmer ikke ennå | patch: kommentaren sier PR 2. Den ubrukte `README` i testen er fjernet |
| BH3 | Docstringen til `kjoer` sier at `ValueError` kommer før vakten | low | Stemmer ikke lenger | patch: en setning som sier at vakten for demobasen kommer før |
| BH9 | Feilteksten velges etter om det er samme objekt | low | Stemmer | patch: sammenligner innholdet |
| BH4 | Boundaries nevner fortsatt Tareøy uten siste dag | low | Står i Spec Change Log, og den frosne delen endres ikke uten gruppen | ikke endret |
| BH8 | Merket er kopiert i tre maler | low | Det finnes ingen felles mal. Tre korte blokker | ikke endret |
| BH10 | Varde Systemer har rader med grunn før den ble notert | low | Storyen krever én rad per aksje og børsdag. Oversikten leser datoen til nyeste kurs | ikke endret |
| BH12 | Linjenumrene i Code Map er utdatert, og statusen henger etter | low | Linjenumrene var riktige da planen ble skrevet | status satt til in-review. Linjenumrene står |

*Rettet 2026-10-10 kl. 13:23:* klokkeslettene i denne spesifikasjonen er ikke lest fra klokka: «kl. 12:45» i Spec Change Log, «12:49–12:58» for de første mutantene, «13:02–13:06» for gjennomgangen og «13:10–13:35» for mutantene etter den. Etter git log: avviket for Tareøy er committet kl. 12:47 (`a1f8e54`), de første mutantene gikk mellom 12:47 og 12:57 (`63c19cc`), gjennomgangen startet etter 12:57 og rettingene er fra 13:04 (`5bcdef0`, `f9bbdcd`), og mutantene etter den gikk mellom 13:04 og 13:22 (`680fcf6`).

*Rettet 2026-10-10 kl. 14:49:* «kl. 12:27» for gruppens ja, i Planen og i raden ECH1, ECH11, er ikke overskriften. Instruksjonen står under «## 12:28» i `docs/ai-prompts/2026-10-10.md`.

Gjennomgang av PR 2 (PR #27, etter `fe22cd3` kl. 15:35), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter mot en ren eksport av grenen. Rettelsene er `abaad78`, `4b0bfc0` og `2fa6f9f`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH1, ECH1 | Testen for `--demo` i `tests/test_docker.py` lekker `OSE_DEMO=1` til testene etter | high | Stemmer. `delenv` uten variabelen legger ingenting tilbake, og `les_flagg` setter `os.environ`. Med `test_docker.py` først feilet testene i `test_app.py`, og den første mutantkjøringen ble drept av lekkasjen | patch: `setenv("0")` først, som i `test_demo.py` (`abaad78`). Mutantene kjørt på nytt |
| VG1 | En demobase uten kurser i Docker er ikke prøvd | medium | Stemmer, det tredje kallet til `demokommando()` | patch: testen for en tom demobase prøver også Docker. Mutant P16 |
| VG2, BH4 | `docker compose run --rm demo-lag` mens demoen kjører, som README-en viser, er ikke prøvd | medium | Stemmer | patch: CI kjører den mellom to sjekker av sidene |
| VG5 | At `docker compose down` uten profilen lar demoen kjøre, er ikke prøvd | low | Stemmer, og prøven viste at det bare gjelder uten `-p` | patch: CI bruker `-f` og prøver det. Mutant C5 |
| VG4 | Porten fra maskinen er ikke prøvd | low | Stemmer | patch: `curl` mot `127.0.0.1:5000` fra maskinen i CI |
| VG9 | Aksjedetaljen i demoen er ikke prøvd i CI | low | Stemmer | patch: `/aksje/BRFE` med «Eksempeltall» |
| BH6 | `urlopen` uten tidsgrense, og feilen skjules | low | Stemmer | patch: `timeout=5`, og ruten og statusen skrives ut |
| ECH10 | Feiler `demo-lag`, viser CI ikke utskriften | low | Stemmer | patch: loggen til `demo-lag` før trap rydder |
| VG3 | Kommandoene i README-en sjekkes bare som tekst et sted | low | Stemmer | patch: hele linjer i kodeblokkene |
| VG6 | Tabellen i §9 følger ikke README-en av seg selv | medium | Stemmer | patch: en test krever hver kommando i tabellen. Mutant P17 |
| VG7 | Antall selskaper, sluttdatoen og `ose-demo` i README-en er ikke bundet til koden | low | Stemmer | patch: test mot `DEMOUNIVERS`, `SLUTTDATO` og `compose.yaml` |
| BH2 | Planen sier både at svar 2 ikke stemmer og at det står | medium | Stemmer | Rettet-linje under planen for PR 2 |
| ECH2 | To `demo-lag` samtidig deler `demo.db.ny` | low | Stemmer, men krever to byggekommandoer samtidig | utsatt: `deferred-work.md` |
| ECH3 | En ødelagt fil i `ose-demo` stopper demoen, og siden viser en kommando som nekter igjen | medium | Stemmer. `demo-lag` nekter en fil som ikke kan leses (PR 1, gruppens beslutning) | utsatt: `deferred-work.md`. Om `demo-lag` skal få skrive over en fil som ikke kan leses i `ose-demo`, er gruppens valg |
| BH3 | Status i README-en sier at demoen er flettet før PR-en er flettet | low | Som i 3.3: linjen blir sann ved flettingen | ikke endret |
| BH5 | «hver gang demoen starter» gjelder `up`, ikke `start` | low | README-en viser bare `up`. Prøvd med `down` og med `stop` før `up` | ikke endret |
| BH7, ECH11 | Sjekken av monteringene og parseren i testene er skjøre | low | De feiler høyt og ikke stille | ikke endret |
| BH8 | De nye tjenestene er ikke med i testene for `build`, `init`, `read_only` og `tmpfs` | low | Stemmer ikke. Testene går over alle tjenestene. Mutant P11 | ikke endret |
| BH9, ECH9 | `up --build demo` bygger samme image for to tjenester og merker `ose-signal` på nytt | low | Som for `app` og `hent` | ikke endret |
| BH10 | Testen skriver til `demo_sti()` | low | `tests/conftest.py` flytter `BASE_STI` til `tmp_path` | ikke endret |
| ECH7, ECH8 | README-en forklarer ikke feilen ved port i bruk, og volumet heter `ose-signal_ose-demo` | low | Byttet sier at bare én kan kjøre. Volumene er omtalt med kortnavn også for `ose-db` og `ose-raa` | ikke endret |
| VG8, VG10 | Rekkefølgen ved oppstart og spinen prøves ikke i drift | low | Betingelsen er testet statisk (mutant P6), og spinen er tekst | ikke endret |


**Gjennomgangen av PR 3** (11.10, diffen `5665f5c..86c4e28`). Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 21) og Verification Gap (VG, 2 hull og 4 andre). Like funn er slått sammen. Rettingene står i `b0deee4`.

| Funn | Hva | Dom | Rute |
|---|---|---|---|
| BH1, BH2, VG, ECH | Ledetekstene «Start så den du vil bruke:», «Demoen:» og «Den ekte versjonen:» ble stående foran de nye | medium | patch |
| BH3, ECH | Linux-setningen motsa seg selv og nevnte bare steg 6 og 8 | medium | patch: Docker Engine i stedet for steg 1 og 2. Docker-gruppen og sudo avvist: Linux er ikke målgruppen |
| BH4, ECH | Steg 5 sa ikke hvilken mappe når det er to, og sjekken passet for den ytre også | medium | patch: mappa der compose ligger, den innerste, ikke ZIP-fila |
| ECH | Sjekken i steg 5 («slutter med») stemmer ikke med `>` og `%` | medium | patch |
| ECH | Linja i steg 6 får en kopieringsknapp og kan limes inn ved en feil | medium | patch: «Den skal du ikke kopiere» |
| ECH | En linje med valg fra Compose kan komme under «Serving on» i et ekte vindu | maybe-false | patch i teksten («kan komme»). Ikke sett, fordi kjøringen skrev til en fil. Rad 6 i §9 spør |
| BH6, ECH | «nettadresse» om grensen hos Docker Hub, som gjelder IP-adressen | low | patch |
| BH7 | Ingenting om plass på disken | low | patch: «noen GB ledig plass». Versjonskrav til Windows og macOS er ikke slått opp og står ikke |
| BH8 | Ingen eksempel for Mac i punktet om mellomrom | low | patch |
| ECH | Safari kan pakke ut ZIP-fila selv | low | patch |
| ECH | Windows kan vise filendelsen | low | patch: «ofte uten» |
| ECH | Windows ARM har en egen nedlasting | low | patch |
| ECH | Mac kan be om passord ved første start | low | patch |
| ECH | Terminal på Mac kan spørre om tilgang til Nedlastinger | low | patch |
| ECH | Windows har andre feilmeldinger for en port i bruk | low | patch: «ports are not available». De andre ordlydene er ikke slått opp |
| BH9, BH10 | Spesifikasjonen viste til Implementation Notes uten en note om kjøringen, og hadde verken del c eller Marians svar | medium | patch: Implementation Notes og «Delene» |
| BH11, VG | §9 spør etter `git log` og mappa `G74-lund-osen`, som ikke passer med ZIP | medium | patch i den daterte linja. Feltene står, fordi PR #28 endrer linjene rett over |
| BH12 | Ingen rad sier om kopieringsknappen virket | low | patch i rad 6. Egne rader for «Mappa finnes fra før» og «Neste gang» avvist: rad 23 spør etter FAQ-en |
| BH13 | Kravet om ingen `.env` før demoen gjaldt bare kommandoene | medium | patch: `test_ingen_env_foer_demoen` |
| BH14 | Testen for linja i steg 6 så ikke om `demo` har egen `command` | medium | patch. Prefikset `demo-1` følger Compose og er kopiert fra v5.5.1, avvist |
| BH15, ECH | Overskrifter i kodeblokker ble regnet som ankre | low | patch. Like overskrifter med `-1` avvist: README-en har ingen |
| VG1 | Stegnumrene, henvisningene «steg N» og §9 var ikke bundet sammen, og den daterte linja i §9 kunne fylle inn for en rad | high | patch: `test_stegene_og_henvisningene_til_dem` og `_proevetabellen()` |
| VG2, ECH | En kodeblokk med språk slapp unna testene for `#` og én kommando | high | patch: `test_bare_kommandoer_og_en_tekstblokk` |
| VG | `test_docker_foerst_og_uv_som_alternativ` krevde fortsatt `git clone` | low | patch: krever «Download ZIP» |
| ECH | En mal uten merket ga `AttributeError` og ikke en tydelig feil | low | patch |
| BH5 | Tipset om `demo-lag` kommer etter at demoen er stoppet | low | avvist: avsnittet står etter steg 8 etter gruppens endring kl. 20:32 |
| ECH | Repoet kan være privat | false | `gh repo view` 11.10: `PUBLIC` |
| ECH | `cd` i Ledetekst bytter ikke stasjon uten `/d` | low | avvist: stegene er for PowerShell, og Ledetekst er bare nevnt som et alternativ som virker for demoen |
| VG | Adressen http://127.0.0.1:5000 hentes ikke fra `ports` i compose.yaml | low | avvist: fantes før PR 3, og `test_porten_er_bare_paa_maskinen` holder den |

**Gjennomgangen av den korte formen** (11.10, diffen `003ce36..19c0a5e`). Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 18) og Verification Gap (VG, 2 hull og 1 annet). Rettingene står i `9dd0f48`.

| Funn | Hva | Dom | Rute |
|---|---|---|---|
| BH, ECH | Steg 1 sa ikke lenger at Docker Desktop skal stå åpent | medium | patch: «La det være åpent» |
| BH, ECH | Steg 2, 3 og 4 hadde mistet sjekken etter steget, og steg 4 «fra Filutforsker eller Finder» | medium | patch |
| ECH | Steg 3 sa ikke hvordan Terminal åpnes på Mac, og ikke at ISE er feil valg | medium | patch: Cmd+mellomrom, og «ikke ISE» |
| ECH | Steg 5 viser `0.0.0.0:5000` uten å si at den ikke skal åpnes | medium | patch |
| ECH | Hvor kopieringsknappen er, og hvordan man limer inn | low | patch: «til høyre i boksen», Ctrl+V eller Cmd+V |
| ECH | Lenken i steg 6 åpnes i samme fane, og README-en med «Stopp» forsvinner | low | patch: «i en ny fane» |
| BH | Rad 7 i §9 (en aksje åpnes) hadde ingen instruks i stegene | low | patch: steg 6 sier at man klikker på et selskapsnavn |
| ECH | Mappa på Mac er bare én, så «den innerste» er uklart | low | patch: mappa der README og compose ligger |
| ECH | Stopp sa ikke hva man gjør når vinduet er lukket | medium | patch |
| BH, ECH | «Hvordan starter jeg neste gang?» utelot steg 6 og hvor Docker Desktop startes | low | patch: steg 3 til 6, Start-menyen eller Programmer |
| ECH | Den som har fått koden fra før, finner ikke svaret under «Mappa finnes fra før» | low | patch: eget spørsmål |
| BH, ECH | «Ingenting skjer når jeg limer inn» sto under steg 3 og 4, ikke steg 5 | low | patch: flyttet |
| ECH | «Første gang tar det en stund» om installasjonen falt bort | low | patch: i linja øverst |
| ECH | De engelske navnene (Downloads, Extract All) sto ikke første gang de ble nevnt | low | patch: i steg 2 |
| BH | «Ellers kan ikke Docker lese mappa» er ikke slått opp | low | patch: «Ellers får ikke Terminal åpne mappa» |
| BH | Linux har ingen linje om hvilke steg som gjelder | low | avvist: linja øverst sier Docker Engine med Compose i stedet for Docker Desktop, og målgruppen er Windows og Mac |
| BH, ECH | «fem spørsmål er nye» og stegnumrene i «Planen for PR 3» stemmer ikke med formen | low | patch i Spec Change Log |
| BH | Rettet-linja i §9 ble skrevet om, ikke lagt til | low | avvist: instruksjonen kl. 21:53 ba om at Rettet-linja fra PR 3 sier hvilke rader som er nye, og den har ikke vært på main. «Nye i PR 3» er presisert |
| BH | 60 ord er mer enn «én til to linjer» | low | avvist: grensen på 60 ord står i instruksjonen kl. 21:53 |
| BH | Boksen etter steg 5 er ikke rykket inn under steget, så lista brytes | low | avvist: GitHub viser «6.» riktig, og innrykkede bokser er nå forbudt fordi testene ikke ser dem (VG) |
| BH | Tomme linjer rundt svarene i `<details>` ble ikke krevd | medium | patch: `_sporsmaalene()` krever dem (K4) |
| BH | Like spørsmål ble ikke oppdaget, og `>= 20` var valgt fritt | low | patch: unike spørsmål (K14), og minst 16, som i «Hvis noe går galt» før |
| BH | Testen for linja i FAQ-en tok `tekst[0]` uten å sjekke antallet | low | patch |
| VG1 | `~~~` og ``` med innrykk er bokser for GitHub, men ikke for testene | high | patch: `test_ingen_bokser_testene_ikke_ser` (K9) |
| VG2 | Et spørsmål som vanlig avsnitt eller overskrift slapp gjennom | medium | patch: utenom `<details>` står bare ledeteksten og linja om resten (K3) |
| VG | Henvisningene «steg N» sjekkes bare mot 1–6, ikke mot riktig steg | low | avvist: alle er lest og stemmer, og en riktig-steg-sjekk krever en tabell over hva hvert steg handler om |

**Mutantene for den korte formen** (11.10, hele testsettet for hver, mot `9dd0f48`, koden satt tilbake fra en kopi med sha256 kontrollert). Alle 16 ble fanget.

| # | Mutanten | Fanget av |
|---|---|---|
| K1 | et sjuende steg | `test_seks_steg_med_hoeyst_60_ord`, `test_merket_i_steg_6_er_det_samme_som_i_malene` |
| K2 | steg 2 over 60 ord | `test_seks_steg_med_hoeyst_60_ord` |
| K3 | et spørsmål i fet skrift | `test_hvert_spoersmaal_er_details_med_summary` |
| K4 | ingen tom linje etter `</summary>` | `test_hvert_spoersmaal_er_details_med_summary`, `test_staar_du_fast_har_alt_som_ble_flyttet` |
| K5 | ankeret skrevet feil | `test_hver_lenke_til_et_avsnitt_finnes` |
| K6 | linja om resten tatt bort | `test_linja_om_resten_staar_foran_den_ekte_versjonen`, `test_hvert_spoersmaal_er_details_med_summary` |
| K7 | `#` i boksen i steg 5 | `test_ingen_kommentar_paa_kommandolinjene`, `test_demoen_er_den_foerste_kommandoen`, `test_readme_proeven_har_hver_kommando` |
| K8 | to kommandoer i Stopp | `test_en_kommando_per_boks`, `test_stopp_har_kommandoen` |
| K9 | `~~~`-boks med `#` og to kommandoer i FAQ-en | `test_ingen_bokser_testene_ikke_ser` |
| K10 | PowerShell og Terminal tatt ut av steg 3 | `test_stegene_nevner_powershell_og_terminal` |
| K11 | merket endret i `index.html` | `test_merket_i_steg_6_er_det_samme_som_i_malene` |
| K12 | «Download ZIP» tatt ut av steg 2 | `test_docker_foerst_og_uv_som_alternativ`, `test_demoen_er_den_foerste_kommandoen`, `test_zip_fila_maa_pakkes_ut` |
| K13 | «Steg 3:» tatt ut av §9 | `test_stegene_og_henvisningene_til_dem` |
| K14 | to like spørsmål | `test_hvert_spoersmaal_er_details_med_summary`, `test_staar_du_fast_har_alt_som_ble_flyttet` |
| K15 | porten i Dockerfile endret | `test_linja_som_viser_at_demoen_er_klar`, `test_webserveren_er_waitress_uten_debug` |
| K16 | AirPlay falt bort fra FAQ-en | `test_staar_du_fast_har_alt_som_ble_flyttet` |

**Testene etter den korte formen:** lokalt 1285 passed og 16 skipped, 1301 samlet. Før PR 3: lokalt 1269 passed og 16 skipped, i CI 1285.

**Gjennomgangen av den helhetlige formen** (11.10, diffen `76b68cb..d844238`). Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 14) og Verification Gap (VG, 5 hull og 2 andre). Rettingene står i `1d7e16f` og `dcc5e9e`.

| Funn | Hva | Dom | Rute |
|---|---|---|---|
| BH, ECH | Stoppet i den ekte versjonen var «Ctrl+C eller denne», men sjekken «Removed» kommer bare etter kommandoen | medium | patch: Ctrl+C og så kommandoen, som i demoen |
| ECH | Setningen om et lukket vindu før stoppet falt bort | medium | patch: eget spørsmål i `docs/hjelp.md` |
| BH | Steg 8 mistet «og før midnatt» | medium | patch. Helgen første gang står i `docs/hjelp.md` |
| BH, ECH, VG | «Hvor ligger dataene?» mistet subjektet | low | patch |
| BH, ECH | Svaret om konto sa bare at demoen ikke trenger nøkkel | medium | patch: kontoen hos EODHD for den ekte versjonen |
| BH | Ledetekst virker ikke for `cp` i den ekte versjonen | medium | patch |
| BH, ECH | Port-svaret viste til «Bytte», som nå er lukket og står i en annen fil | low | patch |
| ECH | Port-svaret gjaldt bare den ekte versjonen, nå som den står først | low | patch: «den andre versjonen» |
| ECH | «Siden åpnes ikke.» sto bare under demoen | low | patch: egen del for begge versjonene |
| BH | «Hvordan starter jeg neste gang?» nevnte ikke hentingen | low | patch |
| BH | «Oversikten er tom.» hadde ulike svar i README-en og `docs/hjelp.md` | medium | patch, og `test_like_spoersmaal_har_samme_svar` |
| BH | §9 prøver ikke den ekte versjonen med nøkkel | low | patch: står åpent i §9 |
| BH, ECH | «ordrett» og antallet i Spec Change Log | low | patch |
| VG1 | Bare overskriftene ble sjekket etter flyttingen, ikke innholdet | high | patch: `test_svarene_beholdt_innholdet` |
| VG2 | Kommandoene i `docs/hjelp.md` slapp unna reglene for bokser og `--profile` | medium | patch: `test_boksene_i_hjelp_foelger_de_samme_reglene` og `--profile` over begge filene. Å kreve `wsl --update`, `git pull` og `nano .env` i §9 er avvist: prøven kan ikke kjøre dem |
| VG3 | «steg N i demoen» ble bare sjekket mot 1–9 | medium | patch |
| VG4 | Lenken i «Dokumentene» ble ikke testet | low | patch |
| VG5 | `test_siden_lastes_paa_nytt_etter_hentingen` leste alt etter overskriften | low | patch: steg 8 |
| BH | Testnavnet `test_demoen_er_den_foerste_kommandoen` sa det motsatte | low | patch: nytt navn |
| BH, ECH | Linux mangler redigeringskommando i steg 6 | low | avvist: `nano .env` står i `docs/hjelp.md`, og steg 6 er på 59 ord |
| ECH | Feilmeldingene fra hentingen har ingen svar | low | avvist: ny informasjon, som instruksjonen kl. 22:32 utelukker |
| ECH | «om kvelden» i tabellen strider mot helgen første gang | low | avvist: ordlyden står i instruksjonen kl. 22:32 |
| ECH | Linja «Serving on» for den ekte versjonen står ikke i `docs/hjelp.md` | low | avvist: den er ikke sett i en kjøring, og «ingen ny informasjon» |
| VG | `git pull` står i et svar mens README-en sier at git ikke trengs | low | avvist: svaret gjelder bare den som har brukt `git clone` |

**Mutantene for den helhetlige formen** (11.10, hele testsettet for hver, koden satt tilbake fra en kopi med sha256 kontrollert). Alle 16 ble fanget. H12 og H13 overlevde først, fordi testen for like svar leste bare ett spørsmål. Testen er rettet i `dcc5e9e`, og begge ble fanget etterpå.

| # | Mutanten | Fanget av |
|---|---|---|
| H1 | Demoen mangler i tabellen | `test_tabellen_nevner_begge_og_hvilken_som_er_anbefalt` |
| H2 | demoen anbefalt | `test_tabellen_nevner_begge_og_hvilken_som_er_anbefalt` |
| H3 | advarselen mot `down -v` i en `<details>` | `test_advarselen_mot_down_v_staar_synlig` |
| H4 | et niende spørsmål | `test_staar_du_fast_har_hoeyst_8_spoersmaal` |
| H5 | et tema borte fra `docs/hjelp.md` | `test_hvert_tema_staar_i_readme_eller_hjelp` |
| H6 | lenken til `docs/hjelp.md` brutt | `test_lenkene_virker`, `test_staar_du_fast_har_hoeyst_8_spoersmaal`, `test_hver_lenke_i_readme_peker_paa_noe_som_finnes` |
| H7 | steg 1 over 60 ord | `test_stegene_er_nummerert_og_har_hoeyst_60_ord` |
| H8 | `#` i boksen i steg 7 | `test_ingen_kommentar_paa_kommandolinjene`, `test_readme_proeven_har_hver_kommando` |
| H9 | merket endret i malen | `test_merket_i_demoen_er_det_samme_som_i_malene` |
| H10 | «Download ZIP» tatt ut | `test_ekte_versjonen_foerst_og_zip_foer_kommandoene`, `test_docker_foerst_og_uv_som_alternativ`, `test_zip_fila_maa_pakkes_ut` |
| H11 | to kommandoer i en boks i `docs/hjelp.md` | `test_boksene_i_hjelp_foelger_de_samme_reglene` |
| H12 | AirPlay borte fra svaret i `docs/hjelp.md` | `test_like_spoersmaal_har_samme_svar` (etter `dcc5e9e`) |
| H13 | ulikt svar i README-en og `docs/hjelp.md` | `test_like_spoersmaal_har_samme_svar` (etter `dcc5e9e`) |
| H14 | «steg 8 i demoen» | `test_henvisningene_og_proevetabellen` |
| H15 | «Dokumentene» uten lenken | `test_hjelp_har_frontmatter_og_er_nevnt_i_readme` |
| H16 | `notepad .env` mangler i §9 | `test_readme_proeven_har_hver_kommando` |

**Testene etter den helhetlige formen:** lokalt 1290 passed og 16 skipped, 1306 samlet. Før instruksjonen kl. 22:32: lokalt 1285 passed og 16 skipped, i CI 1301. Før PR 3: lokalt 1269 passed og 16 skipped, i CI 1285.

**Gjennomgangen av rekkefølgen og «Status»** (12.10, diffen `d2cb634..d1e6639`). Blind Hunter (BH, 10 funn), Edge Case Hunter (ECH, 11) og Verification Gap (VG, 2 hull). Rettingene står i `0f7b42d`.

| Funn | Hva | Dom | Rute |
|---|---|---|---|
| BH, ECH | Tabellen sa ikke at kursene hentes fra EODHD hver børsdag og at dagens vurdering lagres per aksje, slik punktene som ble tatt ut, gjorde | medium | patch i tabellen. «Sidene leser fra basen» står ikke lenger, og det står i Spec Change Log |
| BH, ECH | «Ferdig» stemmer ikke med `review` i sprintstatusen | medium | patch: «Flettet til main», som git kan bekrefte når PR 3 er flettet |
| BH, ECH | 8.0d står ikke i sprintstatusen som statuslinja lenker til | low | patch: lenke også til planen i `epics.md` |
| BH, ECH | Konfliktnotatene manglet regelen for statuslinja ved hver fletting, og 8-0b sier at 2.3b er flettet | low | patch i Spec Change Log |
| BH, ECH, VG | Regelen for storynumre slapp gjennom «(10.1)», «8-0b» og «story 11.2», og kunne slå ut på datoer | medium | patch: parentes, bokstav bak, bindestrek og ordet story, men ikke datoer |
| VG, ECH | «Ingen kommando» sjekket bare ``` og `docker compose` | medium | patch: også `~~~`, kode i backticks, `docker-compose` og `uv run` |
| BH | Testen sjekket ikke innholdet Marian ba om i «Status» | medium | patch |
| BH, ECH | Rekkefølgetesten sjekket ikke «rett under beskrivelsen», og ga `ValueError` i stedet for en feilmelding | low | patch |
| BH | Ingen test for «lenger ned» | low | patch |
| BH | Tidsstemplet i Spec Change Log var eldre enn svaret det viser til | low | patch: «instruksjonen kl. 23:48» |
| BH | Steg 5 sier ikke hvor nøkkelen står hos EODHD | low | avvist: Marian husker ikke, og det er ikke slått opp (regel 3) |

**Mutantene for rekkefølgen og «Status»** (12.10, hele testsettet for hver, mot `0f7b42d`, koden satt tilbake fra en kopi med sha256 kontrollert). Alle 9 som brøt en regel, ble fanget. T9 er forkastet, fordi den la inn en ny linje som ikke het «Til faglærer:», mens den ekte linja ble stående. Den brøt derfor ingen regel. T9b flytter selve linja.

| # | Mutanten | Fanget av |
|---|---|---|
| T1 | «Status» før «Kom i gang» | `test_til_faglaerer_og_kom_i_gang_foer_status`, `test_status_uten_storynumre_og_uten_kommando` |
| T2 | et avsnitt mellom beskrivelsen og «Til faglærer» | `test_til_faglaerer_og_kom_i_gang_foer_status` |
| T3 | «(10.1–10.3)» i «Status» | `test_status_uten_storynumre_og_uten_kommando` |
| T4 | «(8-0b)» i «Status» | `test_status_uten_storynumre_og_uten_kommando` |
| T5 | `docker compose up --build demo` i «Status» | `test_status_uten_storynumre_og_uten_kommando` |
| T6 | en `~~~`-boks i «Status» | `test_status_uten_storynumre_og_uten_kommando` |
| T7 | «hjelp bak «?»» falt bort | `test_status_uten_storynumre_og_uten_kommando` |
| T8 | «lenger ned» borte | `test_lenken_til_staar_du_fast_sier_lenger_ned` |
| T9 | en ekstra linje under «Kom i gang» | forkastet, se over |
| T9b | «Til faglærer» flyttet under «Kom i gang» | `test_til_faglaerer_og_kom_i_gang_foer_status` |

**Testene etter rekkefølgen og «Status»:** lokalt 1293 passed og 16 skipped, 1309 samlet. Før instruksjonen kl. 23:48: lokalt 1290 passed og 16 skipped, i CI 1306.

## Verification

**Mutantene, 10.10 kl. 12:49–12:58.** Mot `tests/test_demo.py`, `tests/test_app.py`, `tests/test_fetch_prices.py` og `tests/test_aksje.py`. 18 av 18 drept:

| Mutant | Testen som fanger den |
|---|---|
| M1 merket følger bryteren | `test_merket_foelger_basen_ikke_bryteren` |
| M2 hentingen setter merket | `test_bare_demokommandoen_setter_merket` |
| M3 vakten i hentingen borte | `test_hentingen_nekter_en_demobase_foer_alt_annet` |
| M4 vakten i demokommandoen borte | `test_demokommandoen_nekter_en_ekte_base` |
| M5 nytt frø per kjøring | `test_samme_froe_gir_like_baser` |
| M6 serien på 120 dager | `test_serien_er_lang_nok_for_grafen_og_ma50` |
| M7 et navn fra `AKSJEUNIVERS` | `test_ingen_symboler_fra_den_ekte_lista` |
| M8 vurderingen regnes av hele serien | `test_hver_vurdering_er_det_vurder_gir` |
| M9 webserveren lager demobasen | `test_bryteren_uten_demobase_viser_kommandoen` |
| M10 «Eksempeltall» borte fra aksjedetaljen | `test_bryteren_med_demobase_viser_eksempeltall` |
| M11 `aksje` i en annen rekkefølge | `test_aksje_er_lik_demounivers` |
| M12 `gauss` i stedet for Box–Muller | `test_normalfordelingen_bruker_bare_random` |
| M13 en ulesbar base regnes som demobase | `test_en_base_som_mangler_eller_ikke_kan_leses_er_ikke_en_demobase` |
| M14 enhver verdi slår på bryteren | `test_bare_verdien_1_slaar_paa_bryteren` |
| M15 `les` sjekker mot `AKSJEUNIVERS` | `test_hver_vurdering_er_det_vurder_gir` |
| M16 siste dag uten fallet | `test_tilstandene_siste_dag` |
| M17 en tom fil godtas | `test_demokommandoen_nekter_en_tom_fil` |
| M18 `--demo` setter ikke bryteren | `test_demo_flagget_setter_bryteren` |

**Suiten:** 1250 passed og 16 skipped, mot 1226 og 16 før (24 i `tests/test_demo.py`).

**Etter gjennomgangen, 10.10 kl. 13:10–13:35.** Alle mutantene kjørt på nytt med de nye ankrene, 24 av 24 drept. Nye: M1b en demobase som `ose.db` følger bryteren, M19 byggingen rett i `demo.db`, M20 webserveren migrerer en demobase som `ose.db`, M21 feilsiden uten demokommandoen, M22 en tom demobase viser hentekommandoen, M23 feilsiden nevner `ose.db`. M1 er flyttet til grenen med bryteren, der merket faktisk leses. Første kjøring etter rettingene viste M1 og M20 som drept av en test i `test_app.py`. Det var `OSE_DEMO` som lekket fra testen for `--demo`, ikke mutantene. Etter rettingen ble M20 fanget først med testen som ser på kallene. M2 er bare fanget av en test som leser kildene. M12 og M16 fanges nå også av fingeravtrykket.

**Suiten etter rettingene:** 1257 passed og 16 skipped (31 i `tests/test_demo.py`). CI på `f9bbdcd`, kjøring 38047102791: `pytest` 1273 passed og `docker` grønn.

**Commands:**
- `uv run pytest -q` -- expected: grønn.

**Mutantene for PR 2, 10.10 etter `2fa6f9f` (15:51) og før `4a25835` (16:16).** Eksakt tekstbytting, og originalen lagt tilbake etter hver. De statiske mot `tests/test_docker.py`, `tests/test_demo.py`, `tests/test_app.py` og `tests/test_readme.py`. CI-mutantene med demosteget i jobben `docker`, kjørt fra en ren eksport av arbeidskopien uten `.env` og `data/`, i prosjektet `ose-ci-34`.

Den første kjøringen, før `abaad78`, viste alle som drept, men av lekkasjen av `OSE_DEMO` fra testen for `--demo` (BH1). Kjøringen under er etter rettingen. 28 av 28 drept:

| Mutant | Fanget av |
|---|---|
| P1 `ose-db` montert i demoen i tillegg | `test_demoen_har_bare_sitt_eget_volum` |
| P1b demo bruker `ose-db` i stedet for `ose-demo` | `test_demoen_har_bare_sitt_eget_volum` |
| P2 demo uten profilen | `test_demoen_ligger_i_profilen_og_lager_basen_foerst` |
| P2b demo-lag uten profilen | `test_demoen_ligger_i_profilen_og_lager_basen_foerst` |
| P3 ulik kommando i README og koden | `test_kommandoene_er_de_samme_som_i_koden_og_compose`, `test_readme_proeven_har_hver_kommando` |
| P3b README starter en tjeneste compose ikke har | `test_tjenestene_i_readme_finnes_i_compose`, `test_demoen_er_den_foerste_kommandoen` |
| P4 uv-kommandoen i Docker | `test_i_docker_viser_sidene_docker_kommandoen_for_demobasen` og to til |
| P4b uv-kommandoen på feilsiden i Docker | `test_i_docker_viser_sidene_docker_kommandoen_for_demobasen` |
| P5 demo uten bryteren | `test_demo_lag_kjoerer_demokommandoen_og_demo_har_bryteren` |
| P6 `depends_on` med `service_started` | `test_demoen_ligger_i_profilen_og_lager_basen_foerst` |
| P7 demo-lag kjører hentingen | `test_demo_lag_kjoerer_demokommandoen_og_demo_har_bryteren` |
| P8 `env_file` i demo-lag | `test_bare_hent_har_noekkelen` |
| P9 README stopper demoen med `docker compose down` | `test_stoppkommandoen_for_demoen` |
| P10 `.env` før demoen | `test_demoen_er_den_foerste_kommandoen` |
| P11 demo uten `read_only` | `test_skrivebeskyttet_rot_med_tmp_som_tmpfs` |
| P12 demoen på alle adresser | `test_porten_er_bare_paa_maskinen` |
| P13 README uten omlastingen | `test_siden_lastes_paa_nytt_etter_hentingen` |
| P14 README uten `--demo` | `test_uv_med_demo_flagget_som_appen_leser` |
| P15 CI stopper uten profilen | `test_stoppkommandoen_for_demoen` |
| P16 en tom demobase i Docker viser uv | `test_demobase_uten_kurser_viser_demokommandoen` |
| P17 README-prøven mangler en kommando | `test_readme_proeven_har_hver_kommando` |
| P18 CI med `-p` | `test_stoppkommandoen_for_demoen` |
| C1 CI stopper uten profilen | demosteget: containerne står igjen |
| C2 demo uten bryteren | demosteget: siden har ikke «Eksempeltall» |
| C3 `ose-db` montert i demoen | demosteget: sjekken av monteringene |
| C4 demo-lag lager ingen base | demosteget: siden har ikke kursene |
| C5 `-p` i stedet for `-f` ved `down` | demosteget: demoen kjører ikke etter `down` |
| C6 demo-lag nekter en demobase som finnes | demosteget: `run --rm demo-lag` gir kode 1 |

C3 la igjen volumet `ose-ci-34_ose-db`, fordi mutanten la til et volum trap ikke fjerner. Derfor stoppet C4–C6 første gang på sjekken av volumer fra før. Bare det volumet er fjernet, og C4–C6 er kjørt på nytt.

**Suiten etter PR 2:** 1269 passed og 16 skipped lokalt, mot 1257 og 16 før (33 i `tests/test_demo.py`, 43 i `tests/test_docker.py`). CI på `2fa6f9f`, kjøring 38057371770: `pytest` 1285 passed og `docker` grønn, også demosteget.

**PR 3, mutantene** (11.10, hele testsettet for hver, mot `b0deee4`, koden satt tilbake fra en kopi med sha256 kontrollert). P1–P11 ble også kjørt mot `ba81406`, før rettingene, og alle ble fanget der også.

| # | Mutanten | Fanget av |
|---|---|---|
| P1 | `# demoen` bak `docker compose up --build demo` | `test_ingen_kommentar_paa_kommandolinjene`, `test_demoen_er_den_foerste_kommandoen`, `test_readme_proeven_har_hver_kommando` |
| P2 | to kommandoer i boksen i steg 8 | `test_en_kommando_per_boks` |
| P3 | PowerShell tatt ut av steg 4 | `test_stegene_nevner_powershell_og_terminal` |
| P4 | «toomanyrequests» tatt ut av FAQ-en | `test_hvis_noe_gaar_galt` |
| P5 | ankeret til FAQ-en skrevet feil | `test_steg_1_2_og_6_peker_til_faqen`, `test_hver_lenke_til_et_avsnitt_finnes` |
| P6 | merket endret i `index.html` uten README-en | `test_merket_i_steg_7_er_det_samme_som_i_malene` |
| P7 | `uv sync` tatt ut av §9 | `test_readme_proeven_har_hver_kommando` |
| P8 | `demoen` i stedet for `demo` i Bytte | `test_tjenestene_i_readme_finnes_i_compose`, `test_readme_proeven_har_hver_kommando` |
| P9 | `git clone` som steg før demoen | `test_demoen_er_den_foerste_kommandoen` (og to til mot `b0deee4`) |
| P10 | porten i Dockerfile endret til 5001 | `test_linja_som_viser_at_demoen_er_klar`, `test_webserveren_er_waitress_uten_debug` |
| P11 | FAQ-en fikk en annen overskrift | `test_hvis_noe_gaar_galt`, `test_demoen_er_den_foerste_kommandoen`, `test_hver_lenke_til_et_avsnitt_finnes` |
| P12 | blokka i steg 8 med `powershell`, `#` og to kommandoer | `test_bare_kommandoer_og_en_tekstblokk` |
| P13 | «Gjør steg 9» i FAQ-en | `test_stegene_og_henvisningene_til_dem` |
| P14 | «Steg 2:» tatt ut av §9 | `test_stegene_og_henvisningene_til_dem` |
| P15 | `.env` nevnt i steg 2 | `test_ingen_env_foer_demoen` |
| P16 | `demo` får egen `command` i compose.yaml | `test_linja_som_viser_at_demoen_er_klar`, `test_demo_lag_kjoerer_demokommandoen_og_demo_har_bryteren` |
| P17 | rad 10 (steg 8) tatt ut av §9 | `test_stegene_og_henvisningene_til_dem`. Kommandoen står fortsatt i rad 16, så testen for kommandoene alene fanger den ikke |

**Testene etter PR 3:** lokalt 1281 passed og 16 skipped, 1297 samlet. Før PR 3: lokalt 1269 passed og 16 skipped, i CI 1285.
