---
title: 'Story 3.5 (3.5d): funnene fra forprøven av den ekte versjonen 24.10'
type: 'bugfix'
created: '2026-10-24'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7b784f0'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5a-dobbeltklikk-med-uv.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** forprøven av den ekte versjonen 24.10 kl. 12:14–12:18 gikk gjennom fra nøkkelen til siden, med åtte funn. Vinduet sa ikke hvor nøkkelen står hos EODHD eller hvordan den limes inn, meldingene fra hentingen og demoen hadde oe, aa og ae, webserveren skrev «Task queue depth», en annen versjon av OSE Signal på porten stoppet starten, og en beskjed viste bare til README-en.

**Grunnlaget:** gruppens svar 24.10 kl. 12:04–12:18, avgjørelsene kl. 12:04 og 12:11 under story 3.5 i `epics.md`, og instruksjonen 24.10 kl. 16:26 i dagsfila.

## Forprøven 24.10 kl. 12:14–12:18

Den ekte versjonen i en ZIP-kopi på gruppens PC med egen testkonto (avgjort kl. 12:11), gjennom fra nøkkelen til siden. Funnene står her slik instruksjonen 24.10 kl. 16:26 grupperer dem. Ordlyden i svarene kl. 12:14–12:18 ligger ikke i repoet.

| Funn | Hva | Punkt |
|---|---|---|
| 1–3 | Nøkkelen: hvor den står hos EODHD, hvordan den limes inn, og hvordan den vises | a) |
| 4–5 | Det brukeren ser fra `src/fetch_prices.py` og `src/demo.py` hadde oe, aa og ae, og linja om hovedindeksen sa ikke hvorfor andre dager enn 2026 ikke lagres (U4) | b) |
| 6 | Webserveren skrev «Task queue depth» | c) |
| 7 | Noe svarte allerede på 127.0.0.1:8000 | d) |
| 8 | En beskjed i vinduet viste bare til README-en | e) |

## Slik er det i dag (slått opp 24.10 på `7b784f0`)

- **Nøkkelen:** vinduet sier «Lag en gratis konto, kopier nøkkelen (API key), og lim den inn her.», og spørsmålet sier «(den vises ikke)» på begge. `start.ps1` leser med `Read-Host -AsSecureString`, `start.sh` med `read -r -s`.
- **Meldingene:** strengene i `src/fetch_prices.py` og `src/demo.py` er skrevet med oe, aa og ae, for eksempel «Ingenting aa hente», «boersdagen» og «KI-tekst for … aksjer paa siste dag». Linja om hovedindeksen er «… lagret N dager, tok bort M som ikke er boersdager i 2026.» (`skriv_indeksen_til_basen`, årene fra `boersdag.DEKKEDE_AAR`).
- **Webserveren:** `waitress-serve --listen=127.0.0.1:8000 app:app` i begge skriptene og README-en, og `waitress-serve --listen=0.0.0.0:8000 app:app` i `Dockerfile`, uten `--threads`, så waitress bruker standarden på 4 tråder.
- **Porten:** sjekkes etter uv og før `uv sync`. Svarer noe, stopper skriptet med «noe svarer allerede på http://127.0.0.1:8000. Stopp det først: …», uansett hva det er. `start.sh` sjekker med curl.
- **Beskjedene:** `stopp` og `Stopp` legger alltid til «Se «Står du fast?» i README-en, eller docs/hjelp.md.». «uv er ikke installert. Installer uv slik «Tester» i README-en sier» viser bare til README-en, og «appen svarte ikke på 127.0.0.1:8000.», «demobasen kunne ikke lages» og «installasjonen av uv feilet» sier ikke hva man gjør.
- **Prosessen på porten (prøvd 24.10 på Windows med en testapp i Temp, ikke appen):** `uv run waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app` lytter i `python.exe` med kommandolinja `"…\.venv\Scripts\python.exe" "…\.venv\Scripts\waitress-serve.exe" --listen=127.0.0.1:8000 --threads=8 app:app`.

## Kontrollpunktene

- a) **Nøkkelen (funn 1–3):** vinduet sier at nøkkelen står som «API token» under «Dashboard» hos EODHD, med kopiknappen til høyre, og hvordan man limer inn: Ctrl+V eller høyreklikk på Windows, Cmd+V på Mac. På Windows vises den som stjerner, på Mac ikke. README-en og hjelpen sier det samme.
- b) **Æ, ø og å (funn 4 og 5):** det brukeren ser fra `src/fetch_prices.py` og `src/demo.py` har æ, ø og å, også i Windows PowerShell 5.1. Linja om hovedindeksen sier at børskalenderen i appen gjelder 2026, så andre dager ikke lagres (U4). Filnavnene (`-raa-`, `forsoek`) endres ikke.
- c) **Tråder (funn 6):** webserveren får `--threads=8` i begge skriptene, README-en og `Dockerfile`.
- d) **Porten (funn 7, svaret kl. 12:04):** før uv og hentingen. Svarer noe på 127.0.0.1:8000, og har prosessen kommandolinja fra skriptene (`waitress-serve`, `--listen=127.0.0.1:8000` og `app:app`), stopper skriptet den, venter til porten er ledig, sier det og går videre. Alt annet, også Docker og `python src/app.py`, stoppes aldri, og vinduet sier hvilket program og hva man gjør.
- e) **Beskjedene (funn 8):** ingen beskjed i vinduet viser bare til README-en; hver sier hva man gjør.
- **Testene,** med «Ville feilet hvis», uten nett: også med en fremmed lytter på 127.0.0.1:8000, som skal kjøre videre, og med en lytter med kommandolinja fra skriptene, som skal stoppes. CI-jobben `dobbeltklikk` krever æ, ø og å i utskriften fra «Start demoen».

## Valg som er gjort her

- **«API token» og «Dashboard»** står slik gruppen så dem i forprøven. Siden hos EODHD krever innlogging og er ikke slått opp her (under «Åpent»).
- **Kommandolinja** gjenkjennes på tre deler hver for seg: `waitress-serve` (også `waitress-serve.exe` med sti), `--listen=127.0.0.1:8000` og `app:app`. Da stoppes også en eldre kopi uten `--threads=8`, og en annen kopi av OSE Signal i en annen mappe. Er én av lytterne på porten noe annet, stoppes ingenting.
- **Windows** finner lytteren med `Get-NetTCPConnection` og kommandolinja med `Get-CimInstance Win32_Process`, og stopper med `taskkill /T /F`. **Mac** finner den med `lsof` og kommandolinja med `ps`, og stopper med `kill`. Uten `lsof` er programmet ukjent, og ingenting stoppes.
- **`start.sh` sjekker porten** med `/dev/tcp` i bash i stedet for curl, så sjekken ikke regner porten som opptatt når curl mangler.
- **Utskriften fra Python** får `PYTHONIOENCODING=utf-8` i `start.ps1`, så æ, ø og å også er riktige når utskriften går til en fil, som i CI. I et vanlig vindu skriver Python til konsollen uansett.
- **Hentingens filnavn** og nøklene i JSON endres ikke, bare tekstene brukeren leser.

## Planen, én commit per punkt

1. a) Nøkkelen: skriptene, README-en, hjelpen og testene.
2. b) Æ, ø og å: `src/fetch_prices.py`, `src/demo.py`, `start.ps1`, testene og CI-steget.
3. c) `--threads=8`: skriptene, README-en, `Dockerfile` og testene.
4. d) Porten: skriptene, README-en, hjelpen og testene.
5. e) Beskjedene: skriptene, README-en, hjelpen og testene.

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: sjekken av kommandolinja borte, så alt på porten stoppes.

*Mutanten 2026-10-24:* sjekken av kommandolinja borte i `start.ps1` (`Er-OseSignal` svarer alltid ja), kjørt én gang med `-x` mot `tests/test_dobbeltklikk.py` kl. 16:58:13–16:58:41 på `50ab5a6`. Fanget av `test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten[fremmed]`. Etterpå var sha256 lik kopien før, og `git hash-object` lik `HEAD:start/start.ps1`. Sjekken ble snevret inn etter gjennomgangen (`0ca3fcc`), og mutanten er ikke kjørt på nytt, fordi instruksjonen sier én.

*Rettet 2026-10-24 (gjennomgangen, BH8, ECH9, VG7):* under «Valg som er gjort her» står at Windows stopper med `taskkill /T /F`. Koden stopper lytteren, `python.exe`, med `Stop-Process -Id … -Force`, og uv og `waitress-serve.exe` over den stopper når den stopper. `taskkill` brukes fortsatt av `Stopp-Serveren` for vinduets egen server. Grunnen til byttet var at testmiljøet uten `PATHEXT` ikke fant `taskkill.exe`.

*Rettet 2026-10-24 (gjennomgangen, BH3, ECH2):* under «Valg som er gjort her» står at også en annen kopi av OSE Signal i en annen mappe stoppes. Etter gjennomgangen stoppes bare `waitress-serve` fra `.venv` i mappa skriptet ligger i, `<mappa>\.venv\Scripts\waitress-serve(.exe)` på Windows og `<mappa>/.venv/bin/waitress-serve` på Mac, med `--listen=127.0.0.1:8000` og `app:app`. OSE Signal fra en annen mappe regnes som et annet program.

## Gjennomgangen 24.10

Gjennomgang 24.10 etter hele settet, av `01a5f8d..7b784f0` på main og `7b784f0..50ab5a6` på grenen. Linsene var Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 11 funn) og Verification Gap (VG, 7 funn), hver for seg og uten å endre noe i repoet. 32 funn ble 24 rader. Funnene er rettet med en gang (svaret 23.10 kl. 15:53), i `56eafe9`, `0ca3fcc`, `d000bdf`, `2bf788e`, `72dfe78` og `a5cdcb8`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1, ECH11 | Fem binære cachefiler fra Windows PowerShell kom med i `20ddc7f`. Kjøretestene startet PowerShell uten `LOCALAPPDATA`, `ProgramData` og `SystemDrive`, i repoet | high | rettet i `56eafe9`: filene er tatt ut, kjøretestene får mappene i `tmp_path` og kjøres derfra, og `.gitignore` har de to mappene. De kommer ikke til main, fordi grenen squash-flettes |
| BH3, ECH2 | Sjekken kjente igjen enhver `waitress-serve … app:app` på porten, også en annen app | medium | rettet i `0ca3fcc`: bare `waitress-serve` fra `.venv` i mappa |
| BH4, ECH10 | README-en og hjelpen lovet at bare en versjon fra «et av disse vinduene» stoppes | medium og low | rettet i `0ca3fcc`: de sier denne mappa, også en webserver startet med `uv run waitress-serve`, og at OSE Signal fra en annen mappe ikke stoppes |
| BH2 | Vinduet der appen ble stoppet, sa «Noe gikk galt … dobbeltklikk på nytt», så brukeren kunne stoppe den nye versjonen igjen | medium | rettet i `d000bdf`: vinduet sier at det kan lukkes hvis den andre versjonen ble startet, og hjelpen sier det samme |
| BH5 | Den andre versjonen stoppes før uv, `uv sync`, nøkkelen og hentingen, så den er borte hvis noe av det feiler | medium etter linsen, low | uten endring: instruksjonen sier «før uv og hentingen» i punkt d). Gruppen avgjør om stoppen skal flyttes til rett før webserveren |
| VG1 | Ingen test viste at hver av de tre delene trengs, og den statiske testen fant delene i linja som starter serveren | medium | rettet i `0ca3fcc`: `test_sjekken_kjenner_bare_igjen_waitress_fra_mappa` kjører sjekken alene med elleve kommandolinjer på Windows og ti i bash, og den statiske testen leser bare sjekken |
| VG2 | Den ekte kommandolinja på Windows, med sti i anførselstegn og `.exe`, var ikke testet | medium | rettet i `0ca3fcc`: den står først i tabellen |
| VG3 | Porttestene kjørte ikke på Windows og Mac i CI | medium | rettet i `a5cdcb8`: steget «Porten på Windows og Mac» i jobben `dobbeltklikk` |
| VG6 | KI-tekstene hentingen skriver ut, fra `src/ki_tekst.py`, hadde fortsatt oe, aa og ae | medium | rettet i `2bf788e`, også grunnene fra `src/ki_lokal.py` og `src/ki_sky.py`, og testen gjelder de tre filene. Feilmeldingene til programmereren i `boersdag.py`, `ki_modell.py` og `ki_kontroll.py` er ikke endret |
| BH11 | Linja om hovedindeksen kalte dagene utenfor 2026 «ikke børsdager» | low | rettet i `72dfe78`: «dager utenfor 2026 eller dager børsen var stengt» |
| BH8, ECH9, VG7 | Spesifikasjonen sa `taskkill /T /F`, koden har `Stop-Process` | low og nit | rettet: Rettet-linja over, og kommentaren i `start.ps1` i `d000bdf` |
| BH7 | Uten navn fra `ps` ble beskjeden «Programmet er  (prosess …)» | low | rettet i `d000bdf` |
| BH13 | En feilmelding uten punktum gikk i ett med «Lukk vinduet» | nit | rettet i `d000bdf` |
| BH14, ECH3 | En prosess startet som administrator gir ingen kommandolinje, og ble bare kalt et annet program | nit og low | rettet i `d000bdf`: beskjeden sier at kommandolinja ikke kunne leses |
| ECH4 | Lytteren kunne stoppe mellom sjekken av porten og oppslaget | low | rettet i `d000bdf`: da går skriptet videre |
| ECH8 | En lytter i testene som ikke fikk porten, ga en feil i stedet for å hoppes over | nit | rettet i `0ca3fcc` |
| BH6 | En prosess-ID kan gjenbrukes mellom oppslaget og stoppen | low | uten endring: tiden mellom oppslaget og stoppen er kort, og er ikke målt |
| BH9 | Testene bruker port 8000 på maskinen | low | uten endring: de hoppes over når porten er i bruk. En egen port for testene ville gitt skriptene en variabel for porten |
| BH10 | Testen for æ, ø og å er en liste med ord | low | delvis: lista har ordene fra KI-modulene. Ellers uten endring |
| BH12 | `svarer` bruker fortsatt curl | low | uten endring: curl følger med macOS, og installasjonen av uv bruker den også |
| ECH5 | `/dev/tcp` har ingen tidsgrense | low | uten endring: på 127.0.0.1 svarer en lukket port med en gang |
| ECH6 | Et annet program kan ta porten mens `uv sync` eller hentingen kjører | low | uten endring: løkka ser først om webserveren har stoppet |
| ECH7 | En feil fra `Stop-Process` eller `kill` vises ikke | nit | uten endring: etter 30 sekunder sier vinduet hva man gjør |
| VG4, VG5 | To lyttere samtidig, og grenen uten kjent lytter, er ikke testet | low | uten endring |

## Åpent

- **«API token» under «Dashboard»** hos EODHD er ikke slått opp, fordi siden krever innlogging. Teksten står slik gruppen så den i forprøven.
- **Kommandolinja på Mac** er ikke slått opp. Sjekken venter `<mappa>/.venv/bin/waitress-serve` med full sti, som på Windows. Står stien annerledes, regnes den andre versjonen som et annet program, og ingenting stoppes. Steget «Porten på Windows og Mac» i CI bruker testens egen lytter, ikke uv.
- **BH5:** om den andre versjonen skal stoppes rett før webserveren i stedet for før uv, er gruppens valg.

*Lagt til 2026-10-24:* gruppen så «API token» under «Dashboard» hos EODHD på skjermen 24.10 kl. 12:16, under forprøven. Bildet kommer senere på siden for den ekte versjonen.

## Det som ikke endres

- «Kom i gang», til gruppen har valgt hovedvei (svaret 23.10 kl. 16:37).
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `.env` på denne maskinen røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
