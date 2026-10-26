---
title: 'Story 3.5 (3.5e): den andre versjonen stoppes rett før webserveren'
type: 'bugfix'
created: '2026-10-26'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'fd04a78'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5d-funn-fra-forproeven.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** kjører den andre versjonen av OSE Signal fra samme mappe, stopper skriptene den før uv, `uv sync`, nøkkelen og hentingen (3.5d, punkt d). Feiler noe av det, er den andre versjonen borte, og ingen av dem kjører (BH5 i triagen til 3.5d).

**Løsningen:** porten sjekkes fortsatt før uv, og et annet program stopper skriptet der som før. Den andre versjonen fra samme mappe stoppes først rett før webserveren startes, så den kjører videre hvis noe feiler før det.
  *Rettet 2026-10-26 (gjennomgangen, ECH1 og ECH2):* «hvis noe feiler før det» gjelder det som stopper skriptet: uv, `uv sync`, nøkkelen og demobasen. Feiler hentingen, starter appen likevel med det som er hentet før (3.5a), og da stoppes den andre versjonen rett før webserveren. Den kjører altså mens hentingen går og feiler, men ikke etterpå.

**Grunnlaget:** avgjørelsen 24.10 kl. 20:00 under story 3.5 i `epics.md`, ført 26.10 fra instruksjonen kl. 09:57 i dagsfila.

## Slik er det i dag (slått opp 26.10 på `fd04a78`)

- **`start/start.ps1`:** `Frigjoer-Porten` kalles etter vernet mot `.git` og før uv. Svarer noe på porten, leses lytterne med `Get-NetTCPConnection` og `Get-CimInstance`. Er en av dem ikke `waitress-serve` fra `.venv` i mappa (`Er-OseSignal`), eller finnes ingen lytter, stopper skriptet med beskjeden «et annet program svarer allerede på http://127.0.0.1:8000, og det er ikke OSE Signal fra denne mappa. …». Ellers stoppes lytterne med `Stop-Process`, skriptet venter opptil 30 sekunder på ledig port, og sier «Den andre versjonen er stoppet, og porten er ledig.».
- **`start/start.sh`:** det samme med `frigjoer_porten`, `lsof`, `ps` og `kill`.
- **Etter porten:** uv (spør før den installeres), `uv sync`, så `uv run python src/demo.py` for demoen, eller nøkkelen og `uv run python src/fetch_prices.py` for den ekte versjonen. Feiler hentingen, starter appen likevel. Så `uv run waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app`.
- **`src/demo.py`:** bygger basen i `demo.db.ny` og bytter den inn med `os.replace`. Feiler det med `OSError`, sier den «Er den åpen i et annet program, for eksempel webserveren?».
- **Appen** lukker tilkoblingen til basen etter hver forespørsel (`teardown_appcontext` i `src/app.py`).
- **Testene fra 3.5d** i `tests/test_dobbeltklikk.py`: `test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten` og `test_start_sh_…` (lyttere «oss», «annen_mappe» og «fremmed», uten uv), `test_porten_sjekkes_foer_uv_og_bare_oss_stoppes` (rekkefølgen i koden) og `test_sjekken_kjenner_bare_igjen_waitress_fra_mappa`. CI kjører `-k "porten or sjekken"` på Windows og Mac.
- **README-en** («Start med dobbeltklikk, uten Docker») og **`docs/hjelp.md`** («Vinduet sier at den andre versjonen av OSE Signal stoppes.») sier at skriptet stopper den andre versjonen, men ikke når.

## Kontrollpunktene

- Porten sjekkes før uv. Et program som ikke er OSE Signal fra mappa, stopper skriptet der med beskjeden fra 3.5d og stoppes aldri.
- Er det den andre versjonen fra mappa, sier vinduet det før uv, og at den stoppes rett før appen starter. Den stoppes ikke før da.
- Rett før webserveren: den andre versjonen stoppes, skriptet venter på ledig port og sier det. Svarer et annet program da, stoppes det ikke, og vinduet sier hva man gjør.
- Feiler uv, `uv sync` eller hentingen, kjører den andre versjonen fortsatt mens det skjer.
- README-en og `docs/hjelp.md` sier når den andre versjonen stoppes (regel 19).

## Valg som er gjort her

- **Ett unntak for demoen trengs ikke.** Instruksjonen åpner for å stoppe demoen før demobasen lages på nytt, hvis Windows ikke lar `demo.db` byttes mens demoen kjører. Prøvd 26.10 på Windows 11 i en midlertidig mappe: demobasen laget, waitress i gang mot den, fire sider hentet (`/`, `/boersometer`, `/aksje/BRFE`, `/min-liste`), og så `lag_demobase` på nytt mens serveren kjørte. `os.replace` gikk gjennom, og siden svarte 200 etterpå. Grunnen er at appen lukker tilkoblingen etter hver forespørsel, så fila er bare åpen mens en side lastes. Skjer byttet akkurat da, feiler `src/demo.py` med beskjeden sin, skriptet stopper, og den andre versjonen kjører videre, som ved en annen feil før webserveren.
- **Samme funksjon to ganger.** `Frigjoer-Porten` og `frigjoer_porten` får et argument: før uv sjekker de og sier fra, rett før webserveren stopper de. Beskjeden om et annet program er den samme begge steder, så vinduet sier hva man gjør også når et annet program har tatt porten underveis.

## Planen, én commit per punkt

1. Spesifikasjonen.
2. a) Skriptene, README-en og `docs/hjelp.md`, med testene fra 3.5d som må følge med.
3. b) Testene med en falsk uv uten nett, på Windows og Mac i CI.

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: stoppen tilbake før uv.

*Utfallet 26.10 kl. 10:08:17–10:08:32 på `df6b0a0`:* `Frigjoer-Porten $false` byttet med `$true` i `start.ps1`, så den andre versjonen stoppes før uv, kjørt med `-x` mot `tests/test_dobbeltklikk.py`. Fanget av `test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten[oss]`. Fila var lik HEAD etterpå: samme sha256 som kopien, og samme git-objekt som HEAD.

*Utfallet 26.10 kl. 10:23:59–10:24:14 på `fd19b7f`, etter rettelsene fra gjennomgangen:* fanget av den samme testen, og fila var lik HEAD etterpå. Et forsøk kl. 10:23:05 satte ikke inn mutanten, fordi mønsteret krevde CRLF og fila har LF i arbeidskopien; testene kjørte da på uendret kode og telles ikke.

## Gjennomgangen

Gjennomgang 26.10 etter hele settet (3640 bestått, 24 hoppet over, 0 feilet, 10:08:49–10:14:38 på `df6b0a0`), av diffen `fd04a78..df6b0a0`, med Blind Hunter (BH, 8 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, ingen hull). Rettet i `d8cd7b8`, `48e6da3` og `fd19b7f`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1, ECH2 | «Kjører videre hvis uv, uv sync eller hentingen feiler» lovet for mye: feiler hentingen, starter appen likevel, og da stoppes den andre versjonen | medium | **rettet** i `d8cd7b8`: «hvis skriptet stopper før det», og README-en og `docs/hjelp.md` sier hva som skjer når hentingen feiler |
| BH2, ECH3 | `uv sync` går nå mens den andre versjonen bruker `.venv`, og på Windows kan den feile på åpne filer, med en beskjed om nettet | medium | **rettet** i `48e6da3`: da sier vinduet at den andre versjonen kan holde filene i `.venv` åpne, og ber om å lukke vinduet dens. Ikke prøvd med en `uv sync` som må bytte filer |
| BH7 | README-en sa ikke at porten sjekkes igjen rett før webserveren | low | **rettet** i `d8cd7b8` |
| BH5, ECH4 | Ingen test sjekket at beskjeden om den andre versjonen kommer før uv sync | low | **rettet** i `48e6da3`: beskjeden står før «Installerer pakkene» i alle tilfellene med den andre versjonen |
| BH6 | Testen for uv sync godtok meldingen fra begge skriptene | low | **rettet** i `48e6da3`: meldingen er den samme i begge nå, og testen krever den |
| BH4 | Vinduet sa «kjører allerede på …» både før uv og rett før webserveren | low | **rettet** i `fd19b7f`: den andre beskjeden sier bare at den stoppes nå |
| BH1 | Testtekstene fra 3.5d sa at den andre versjonen stoppes før uv | low | **rettet** i `fd19b7f` |
| CI | I den første kjøringen av grenen (40299393259) var port 8000 opptatt på Mac rett etter «Start demoen», så alle porttestene for `start.sh`, også de nye, ble hoppet over, og jobben var likevel grønn | medium | **rettet** i `fbcae5a`: steget venter opptil 120 s på ledig port og feiler hvis en porttest hoppes over fordi porten er i bruk. I kjøring 40299942312 var porten ledig etter 0 s, og 13 porttester besto på Mac. Funnet ved kontrollen av CI-loggen, ikke av linsene |
| BH3 | Hentingen skriver til `data/db/ose.db` mens den andre ekte versjonen kjører fra samme mappe | low | **under «Åpent»:** webserveren skriver bare merkingen i Min liste, og tilkoblingen venter opptil `VENTETID_SEKUNDER` (5 sekunder) på en lås. Ikke prøvd |
| BH8 | To vinduer startet nesten samtidig kommer begge forbi sjekken før uv, og den siste stopper den første rett før webserveren | low | **under «Åpent»:** det samme kunne skje før 3.5e, men tiden mellom sjekken og webserveren er lengre nå |

## Åpent

- **BH3:** hentingen mens den andre ekte versjonen kjører fra samme mappe, ikke prøvd.
- **BH8:** to vinduer startet nesten samtidig.

## Det som ikke endres

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. Testene bruker en falsk uv.
- `data/db/ose.db` og `.env` i repoet røres ikke. Demobasen i prøven over ble laget i en midlertidig mappe.
- Sjekken av kommandolinja (`Er-OseSignal`, `er_ose_signal`) og beskjedene fra 3.5d står som før.
- PR #99 (8.6b) røres ikke.
