---
title: 'Story 2.13: målingen av omsetning som jobben kjører hver kveld'
type: 'feature'
created: '2026-10-28'
status: 'review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '4e98564'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
  - '{project-root}/src/fetch_prices.py'
  - '{project-root}/start/kveldshenting.ps1'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** målingen av omsetning er gjort for hånd med et skript utenfor repoet (§40–§52 i `malinger.md`), med en instruksjon hver gang. 83 «Common Stock» i lista over Oslo Børs er ennå ikke rangert (§52), og kallene som er igjen etter kveldshentingen, går tapt de kveldene ingen kjører målingen.

**Løsningen:** et eget valg i hentekommandoen, `--maal-omsetning`, som jobben fra 2.3d kjører etter hentingen hver kveld. Det måler de neste aksjene med alle kallene som er igjen den dagen i GMT og bruker aldri bonuskvoten. Tallet og datoen står i en ny tabell, og rådataene i `data/raa/`.

**Grunnlaget:** story 2.13 i `epics.md` og avgjørelsen 28.10 kl. 22:17 under 2.13 og 8.17 (`4e98564`): a) 2.13 bygges i natt; b) jobben kjører målingen etter hentingen med alle kallene som er igjen den dagen i GMT, også på dager børsen er stengt, hentingen og nye forsøk får kallene først, og bonuskvoten brukes aldri; c) når hele lista er målt, måles de eldste målingene på nytt først, og det går foran «etter 3 måneder» og «lar 2 stå igjen» i FR-413.

## Slik er det i dag (slått opp 28.10 på `4e98564`)

- **Story 2.13:** tallet og datoen i en egen tabell med ny migrasjon (AD-16), rådata i `data/raa/` (AD-6). Kommandoen nekter når dagens henting ikke er gjort eller har feilet, og bruker da 0 kall. Den leser `/api/user` før første kall og sier hvor mange kall den vil bruke. Den bruker aldri bonuskvoten: står `extraLimit` lavere etter første kall, stopper den. OBX først. Et eget valg i hentekommandoen, så Dockerfilen fortsatt har to innganger, og `allow_abbrev=False`. «Ville feilet hvis» målingen kunne startes fra nettsiden eller tok et kall fra bonuskvoten.
- **FR-413** (`prd.md`): valget kjøres for hånd etter en vellykket henting og aldri fra webserveren (AD-10). Det lar 2 kall stå igjen og måler hver aksje på nytt etter 3 måneder; begge erstattes av avgjørelsen kl. 22:17. Median omsetning regnes som i §3: `volume × close` per handelsdag, med medianen over tre måneder.
- **NFR-01:** bonuskvoten brukes bare til å fullføre kveldens henting, aldri til nye forsøk eller målingen (08.10 kl. 08:06).
- **AD-6:** hvert uttrekk skrives som `<prefiks>-raa-<ÅÅÅÅ-MM-DD>.json` og skrives aldri om. `nyeste_snapshot` lar datoen avgjøre alene, og ved lik dato vinner `KURSPRE`fda73fd``. **AD-16:** nummererte migrasjoner, `0001`–`0007` i dag. Den ekte basen står på versjon 7.
- **§40:** lista over aksjene på Oslo Børs, `data/proever/symbolliste-OL-2026-10-22.json` (lokal, ikke sporet), 304 rader, 297 «Common Stock». **§42, §50–§52:** de neste «Common Stock» i lista som ikke er rangert, i rekkefølgen i lista, hvor de som alt er rangert, hoppes over. Det er ett `/api/eod`-kall per symbol, i vinduet `2026-07-02`–`2026-10-02`. Dager med volum 0 tas med i medianen med omsetning 0. §51 og §52: kvoten leses før og etter hvert kall, og skriptet stopper hvis `apiRequestsDate` ikke er dagens dato, 20 kall er brukt eller `extraLimit` endrer seg. «Alle 206, rangert» i §50 har kolonnen «Målt i» med §-en hver aksje ble målt i. §51 og §52 la til 4 hver, så 214 er rangert.
- **2.3d:** `start/kveldshenting.ps1` kjører `uv run python src/fetch_prices.py` uten flagg og avslutter med koden fra hentingen. Jobben går kl. 22:15, 22:45, 23:15 og 23:45.
- **`src/fetch_prices.py`:** `hent_ett_symbol`, `hent_kvote`, `les_kvotetall`, `manglende_i_basen`, `nekt_demobase` og `_uten_noekkel`. Når hentingen har feilet for en aksje, mangler basen kursen for børsdagen, og hentingen gir kode 1.

## Kontrollpunktene

- a) Valget i hentekommandoen med utvalget og rekkefølgen fra §50–§52 og avgjørelsen kl. 22:17. Kvoten leses før og etter hvert kall, som i §51. Det stopper hvis `apiRequestsDate` ikke er dagens dato i GMT, `extraLimit` endrer seg, eller en aksje i lista mangler kursen for siste børsdag. Rådata i `data/raa/`, tallet og datoen i en ny tabell med migrasjon, og ingen kurser eller volumer i utskriften.
- b) `start/kveldshenting.ps1` kjører valget etter hentingen i hver kjøring, med loggen som før.
- c) README-en og `docs/hjelp.md` (regel 19), og en datert linje under FR-413 i `prd.md` om det som er endret kl. 22:17.
- d) Tester med «Ville feilet hvis» et kall gikk fra bonuskvoten, et kall ble gjort med en annen dato i GMT, det ble målt mens en aksje manglet kursen, en aksje ble målt to ganger før alle var målt, de eldste ikke kom først når alle var målt, eller migrasjonen endret en tabell som finnes.

## Valg som er gjort her

- **Navnet** er `--maal-omsetning`, i samme `argparse` med `allow_abbrev=False`. Det kan ikke kombineres med `--les-inn` eller `--uten-tidskontroll`. Logikken står i `src/omsetning.py`, og `main` i `fetch_prices.py` importerer den bare når valget er gitt. Nettfunksjonene, `hent_ett_symbol` og `hent_kvote`, blir i `fetch_prices.py` og gis inn som parametre, så testene aldri går mot nettet (AD-8).
- **Kandidatene** er «Common Stock» i lista over Oslo Børs, i rekkefølgen i fila, uten aksjene i appens liste (`AKSJEUNIVERS`), fordi de hentes hver kveld. Lista leses lokalt fra `data/proever/symbolliste-OL-2026-10-22.json`, uten kall. Mangler fila, eller kan den ikke leses, stopper valget med 0 kall og kode 1.
- **Hva som er målt:** en aksje med en rad i `omsetning`, eller en av de 214 som er rangert i `malinger.md` (`MAALT_I_MALINGER`, med §-en og datoen i overskriften til §-en). En test leser de 214 fra «Alle 206, rangert» i §50 og tabellene i §51 og §52, og holder dem like.
- **Rekkefølgen:** først de som aldri er målt, i rekkefølgen i lista, slik at målingen fortsetter etter HERMA, der §52 sluttet. Når alle er målt, kommer den eldste målingen først. Datoen er siste rad i `omsetning`, ellers datoen til §-en. Ved lik dato avgjør plassen i lista. Ingen aksje måles to ganger i samme kjøring. OBX først (FR-413) er oppfylt fordi alle i OBX er rangert i §17, så det står ingen egen OBX-liste i koden.
  *Rettet 2026-10-28 (gjennomgangen, VG11):* §17 sier at alle 25 i OBX er blant de 40 i §17, og de 40 står i §15–§17 i `MAALT_I_MALINGER`. En ny aksje i OBX som ikke er blant de 214, får ingen forrang (BH11, «Åpent»).
- **Kallene:** alle som er igjen av `dailyRateLimit` i dag i GMT, regnet fra `/api/user` før første kall. Før hvert kall må `apiRequests` være under `dailyRateLimit`, så kall nummer 21 aldri gjøres. Etter hvert kall må `apiRequests` ikke være over `dailyRateLimit`. Ingen kall holdes igjen (avgjørelsen kl. 22:17).
- **Stoppene:** før første kall stopper valget med 0 kall og kode 1 når basen er en demobase, når børsdagen ikke kan regnes (`UtenforKalenderen`), når en aksje i lista mangler kursen for børsdagen eller basen ikke kan leses, når lista over Oslo Børs mangler, og når kvoten ikke kan leses. Underveis stopper det, med kode 1, hvis `extraLimit` er en annen enn ved første lesing, hvis `apiRequestsDate` er en annen enn dagens dato i GMT etter et kall, hvis datoen i GMT på klokka har skiftet siden starten, eller hvis kvoten ikke kan leses. Det som alt er målt, lagres også da.
  *Lagt til 2026-10-28 (gruppens svar kl. 23:19, d):* fra kl. 23:45 i Oslo, jobbens siste kjøring, stopper ikke en manglende kurs målingen. Den går med kallene som er igjen etter nye forsøk, og utskriften sier hvor mange av de 15 som mangler. Før 23:45 venter den som før, og uten base venter den alltid.
- **Børsdagen** er `innevaerende_boersdag` av datoen i Oslo: i dag på en børsdag, ellers siste børsdag før. På en børsdag før hentingen har dagens kurser, stopper valget derfor ved kursvakten med 0 kall, så kallene står til hentingen og nye forsøk (avgjørelsen kl. 22:17, b).
- **Vinduet** er tre måneder til og med børsdagen: fra samme dag tre måneder før (siste dag i måneden når den dagen ikke finnes) til børsdagen, som i §40 (`2026-07-22`–`2026-10-22`). Vinduet står i raden. §42–§52 brukte det faste vinduet `2026-07-02`–`2026-10-02`. Se «Åpent».
- **Medianen:** `volume × close` per rad i vinduet. En rad med volum 0 tas med med omsetning 0, som i §42. En rad uten tall for `close` eller `volume` tas ikke med, men telles i `rader_uten_tall`. Gir ingen rad tall, eller feiler kallet, lagres raden med `feil` i stedet for medianen. Aksjen regnes da som målt den dagen, så en ticker som ikke gir rader, ikke tar kallene hver kveld.
  *Rettet 2026-10-28 (gjennomgangen, BH3, ECH1, BH9, ECH3):* bare et kall som feiler med `HTTP 404` (tickeren finnes ikke), gir en rad med `feil`. En annen feil fra kallet, som et tidsavbrudd eller 5xx, gir ingen rad, bare en linje i rådataene, så aksjen står først også neste gang. `dager_uten_volum` teller rader med volum 0, ikke omsetning 0. Et tall som er for stort for float, er en rad uten tall.
- **Tabellen** er `omsetning` i `0008_omsetning.sql`: `symbol`, `maalt` (starten av kjøringen i UTC med offset, som `hentet`), `fra`, `til`, `handelsdager`, `dager_uten_volum`, `rader_uten_tall`, `median_omsetning` i NOK, uavrundet (regel 21), og `feil`. Primærnøkkelen er `(symbol, maalt)`, så en ny måling legges til og skriver aldri over en gammel. Det er ingen trigger mot `aksje`, fordi aksjene ikke står i lista. Ingen tabell som finnes, endres.
- **Rådataene** står i `omsetning<n>-raa-<børsdag>.json` i `data/raa/`, med første `n` fra 1 som ikke finnes, skrevet med modus `x` (AD-6). Datoen er børsdagen, ikke kjøredagen, så fila aldri har nyere dato enn kursfila, og ved lik dato vinner kursfila (`nyeste_snapshot`). Fila skrives først, og så radene i basen. Feiler fila, skrives ingen rader.
  *Rettet 2026-10-28 (gjennomgangen, ECH3, ECH8):* det som er målt, lagres også når kjøringen avbrytes av noe annet enn en stopp, og så går avbruddet videre. Finnes navnet når fila åpnes, prøves neste `n`.
- **Utskriften** sier hvor mange kall valget bruker, hvilke aksjer, antall handelsdager og dager uten volum per aksje, og kvoten etter. Kurser, volumer og medianene skrives ikke ut. Medianene står i tabellen.
  *Rettet 2026-10-28 (gjennomgangen, VG5, BH7):* «og kvoten etter» var ikke bygget. Nå er siste linje «Kvoten etter: <brukt> av <grense> brukt <dato> i GMT, extraLimit <n>.». Startlinja sier hvor mange kall som blir igjen, når det er færre aksjer enn kall.
- *Lagt til 2026-10-28 (gjennomgangen, ECH6, BH10, ECH10):* klokka leses rett før hvert kall, etter kvoten, og grensen før og etter et kall er den laveste `dailyRateLimit` som er lest i kjøringen.
- **Jobben** kjører `uv run python src/fetch_prices.py --maal-omsetning` etter hentingen i hver kjøring, også når hentingen ga kode 1 eller 3. Valget sjekker selv om kursene finnes. Loggen får linja «Målingen avsluttet med kode <n>.», og jobben avslutter fortsatt med koden fra hentingen.

## Planen

1. Spesifikasjonen.
2. `src/omsetning.py`, `0008_omsetning.sql`, valget i `fetch_prices.py`, `start/kveldshenting.ps1`, testene, README-en, `docs/hjelp.md`, linja under FR-413 og 2.13 i `sprint-status.yaml` i én commit (regel 19).
3. Hele settet, mutanten, gjennomgangen og triagen her og i PR-en.

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: stoppen ved endret `extraLimit` tatt ut.

*Utfallet 28.10 kl. 23:06:17–23:06:19 på `ab7b967`:* begge linjene `if bonus_naa != bonus:` i `src/omsetning.py` byttet til `if False:`, kjørt med `-x` mot `tests/test_omsetning.py`: fanget av `test_stopper_naar_extraLimit_endres_etter_et_kall`. Fila var lik HEAD etterpå: samme sha256 som kopien (`a0027700…`), og samme git-objekt som `HEAD:src/omsetning.py` (`26cdcbc`).

*Utfallet 28.10 kl. 23:25:10–23:25:11 på `fda73fd`, etter rettingene fra gjennomgangen:* den samme mutanten ble fanget av den samme testen, og fila var lik `HEAD:src/omsetning.py` (`3697494`) etterpå, med samme sha256 som kopien.

*Mutanten 28.10 kl. 23:19 (svaret d), grensen kl. 23:45 tatt ut, med `-x`, kopi før og sha256 mot HEAD etter:* betingelsen byttet til `True`, så målingen alltid venter når en kurs mangler. 28.10 kl. 23:50:14–23:50:19 på `e744f87`: fanget av `test_gaar_fra_23_45_naar_en_kurs_mangler`, og fila var lik `HEAD:src/omsetning.py` (`39e1ebc`) med samme sha256 som kopien. 29.10 kl. 00:12:25–00:12:37 på `0640378`, etter rettingene fra gjennomgangen: fanget av samme test, og fila var lik `HEAD:src/omsetning.py` (`091f9da`) med samme sha256 som kopien.

## Gjennomgangen

Gjennomgang 28.10 etter hele settet (3849 bestått, 24 hoppet over, 0 feilet, 22:57:49–23:05:44 på `ab7b967`), av diffen `4e98564..ab7b967`, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 13) og Verification Gap (VG, 12). Dommen i tabellen er vår. Rettet i `fda73fd`. Hele settet på `fda73fd` (kjørt før commiten, på samme kode): 3861 bestått, 24 hoppet over, 0 feilet, 23:16:23–23:24:49.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH2 | Ingen lås: to målinger, eller en måling og en henting for hånd, samtidig kan begge lese 19 brukt, og kall nummer 21 går fra bonuskvoten. Kontrollen etter kallet ser det først etterpå | medium | **ikke rettet**, spørsmål til gruppen («Åpent»). Jobben starter ingen ny kjøring mens en går (2.3d), og gruppen avgjorde 28.10 kl. 11:34 ingen lås for en henting for hånd (BH6 i 2.3d) |
| BH1, ECH2 | *Svart 2026-10-28 kl. 23:19 (gruppens svar, c):* ingen lås, som for hentingen kl. 11:34: vi kjører ikke noe for hånd mens jobben går | medium | **avgjort**, ingen endring |
| BH3, ECH1 | En feil som går over (tidsavbrudd, 5xx, 429), ble lagret som en måling, så aksjen havnet bakerst | medium | **rettet** i `fda73fd`: bare `HTTP 404` gir en rad, og `test_en_feil_som_gaar_over_gir_ingen_rad` |
| ECH3 | Avbrytes kjøringen midt i, er kallene brukt og ingenting lagret. Et heltall for stort for float ga `OverflowError` | medium | **rettet** i `fda73fd`: det som er målt, lagres før avbruddet går videre, `_tall` og `regn_ut` tåler store tall, `test_det_som_er_maalt_lagres_naar_kjoeringen_avbrytes` og `test_kurs_null_er_ikke_en_dag_uten_volum_og_store_tall_stopper_ikke` |
| ECH4 | Mangler én av de 15 kursen for børsdagen hele kvelden (suspendert, hull hos EODHD), blir det ingen måling, heller ikke i helga | medium | **ikke rettet**, spørsmål til gruppen («Åpent»). Det er stoppen instruksjonen ber om |
| ECH4 | *Svart 2026-10-28 kl. 23:19 (gruppens svar, d):* mangler én av de 15 kursen, går målingen kl. 23:45 med kallene som er igjen. Nye forsøk får fortsatt kallene først | medium | **rettet** i `f58cf7b`: `TestKl2345` |
| BH4 | `fetch_prices.py` kjøres som `__main__`, og `omsetning` importerer den en gang til; den veien var ikke prøvd | medium | **rettet** i `fda73fd`: `test_valget_virker_naar_fetch_prices_kjoeres_som_skript` kjører fila med `runpy` som `__main__` |
| VG1 | Kontrollen før hvert kall (`brukt >= grense`) var ikke prøvd for seg | high | **rettet** i `fda73fd`: `test_ingen_kall_naar_kvoten_naar_20_underveis` |
| VG3 | Medianen kunne skrives ut i en annen form uten at testen så det | medium | **rettet** i `fda73fd`: `test_ingen_tall_fra_kildene_eller_medianen_i_utskriften`, ingen tall over 99 utenom datoer og `extraLimit` |
| VG4 | At valget sier hvor mange kall det bruker, var ikke prøvd | medium | **rettet** i `fda73fd`: `test_utskriften_sier_kallene_foer_foerste_kall_og_kvoten_etter` |
| VG5, BH7 | «og kvoten etter» var ikke bygget, og startlinja sa «ingen kall blir igjen» også med færre aksjer enn kall | medium | **rettet** i `fda73fd`, med samme test |
| VG6, BH13 | Datoen før første kall og vinduet avviker fra instruksjonen og §42–§52 | medium | **står** i «Åpent», gruppen avgjør før flettingen |
| VG6, BH13 | *Svart 2026-10-28 kl. 23:19 (gruppens svar, a og b):* gårsdagens dato godtas før første kall og leses som 0 brukt i dag, og etter hvert kall må datoen være dagens. Vinduet er tre måneder bakover fra børsdagen og står ved hvert tall | medium | **avgjort**, koden var slik: `TestSvarene2319` |
| BH5 | Hentingen med kode 3 (bare indeksen feilet) stopper ikke målingen | low | **avvist**: indeksen får ingen ny sjanse samme kveld (AD-15, 2.8), så kallene trengs ikke til den |
| BH2 | Et kall kunne bli to ved nye forsøk inne i `hent` | high | **avvist** etter oppslag: `hent_ett_symbol` gjør ett `requests.get` uten `Retry` eller adapter |
| BH6, ECH12 | Fila kan bli nyeste øyeblikksbilde når kursfila for dagen mangler | low | **avvist**: `nyeste_snapshot` og `nyeste_leser` kalles ikke fra noe annet i `src/` (slått opp), og fila heter etter børsdagen |
| BH8 | `kall` telles også når `hent` feilet før et kall, og antallet ble ikke skrevet ut når fila feilet | low | **delvis rettet** i `fda73fd`: «API-kall brukt» skrives alltid. Tellingen står: en feil fra `hent_ett_symbol` kommer fra et kall |
| BH9 | Kurs 0 med volum ble telt som dag uten volum | low | **rettet** i `fda73fd`. Doble datoer: avvist, EODHD gir én rad per dag |
| BH10, ECH10 | `dailyRateLimit` ble bare lest én gang | low | **rettet** i `fda73fd`: den laveste som er lest |
| BH11 | En ny aksje i OBX får ingen forrang | low | **står** i «Åpent» |
| BH12 | Testen for børsdagen før hentingen sjekket ikke grunnen, og andre kjøring hadde samme `maalt` | low | **rettet** i `fda73fd` |
| ECH5 | Flettes grenen mens jobben går, migrerer webserveren basen til 8, og kjøringene etter står på 7 | low | **står**: hentingen gir da 0 kall (slått opp av ECH5). Flett etter kl. 23:45 eller om dagen |
| ECH5 | *Svart 2026-10-28 kl. 23:22 (gruppens svar, e):* 2.13 flettes torsdag 29.10 kl. 23:50, etter jobbens siste kjøring, og ikke etter 23:59 | low | **avgjort** |
| ECH6 | Klokka ble lest før kvoten, ikke rett før kallet | low | **rettet** i `fda73fd` |
| ECH7 | Feiler radene etter at fila er skrevet, er de tapt, og aksjene måles på nytt | low | **utsatt**: rådataene står, og en innlesing fra fila er ikke en del av 2.13 |
| ECH8 | To kjøringer kan få samme filnavn | low | **rettet** i `fda73fd`: neste `n` ved `FileExistsError`, `test_et_navn_som_dukker_opp_skrives_ikke_over` |
| ECH9 | Kalenderen dekker bare 2026 | low | **avvist**: som hentingen (NFR-08) |
| ECH11 | En feil i målingen i skriptet kan sette koden jobben gir | low | **avvist**: `$ErrorActionPreference` er `Continue` rundt begge kommandoene, så en feil fra programmet stopper ikke skriptet |
| ECH13 | En `maalt` som ikke kan leses, ga en traceback | low | **rettet** i `fda73fd`: `ValueError` gir stopp med 0 kall |
| VG2 | Testen for nettsiden ser bare på importene i `app.py` | low | **avvist**: `test_webserveren_importerer_ikke_hentingen` i `tests/test_konsumentene.py` og AD-10 dekker resten |
| VG7 | Datoen etter kallet var bare prøvd med en senere dato | low | **rettet** i `fda73fd`: `test_stopper_naar_kvoten_staar_paa_gaarsdagen_etter_et_kall` |
| VG8 | «Rådataene først» var ikke prøvd | low | **rettet** i `fda73fd`: `test_ingen_rader_naar_raadataene_ikke_kan_skrives` |
| VG9 | En kvote som ikke kan leses underveis, var ikke prøvd | low | **rettet** i `fda73fd`: `test_det_som_er_maalt_lagres_naar_kvoten_ikke_kan_leses` |
| VG10 | Den statiske testen av skriptet godtok at `$kode` ble satt etter målingen | low | **rettet** i `fda73fd` |
| VG11 | Ordlyden om OBX i spesifikasjonen | low | **rettet** her |
| VG12 | Medianen var bare prøvd der `median`, `median_low` og `median_high` er like, og en kode to ganger i lista var ikke prøvd | low | **rettet** i `fda73fd`: `test_medianen_av_et_partall_rader_og_en_kode_to_ganger_i_lista` |

## Gjennomgangen 29.10

Gjennomgang 29.10 etter hele settet (3867 bestått, 24 hoppet over, 0 feilet, 23:50:30–23:59:07 på `e744f87`), av endringene etter `e6287bf` (diffen `cd1e64d..e744f87`, uten flettingen av main), med Blind Hunter (BH, 10 funn), Edge Case Hunter (ECH, 9) og Verification Gap (VG, 6). Ingen funn med dom high. Dommen i tabellen er vår. Rettet i `0640378`. Hele settet på samme kode før commiten: 3867 bestått, 24 hoppet over, 0 feilet, 29.10 kl. 00:04:10–00:12:08. BH-, ECH- og VG-numrene her er nye og gjelder bare denne gjennomgangen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH2, VG2, ECH3, ECH2 | Fra 23:45 går målingen også når alle 15 mangler kursen, for eksempel når hentingen feilet hele kvelden, eller basen er laget av webserveren uten kurser. Svaret kl. 23:19 sier «mangler én av de 15» | medium | **ikke rettet**, spørsmål til gruppen («Åpent») |
| BH2, VG2, ECH3, ECH2 | *Svart 2026-10-29 kl. 09:20 (gruppens svar, a):* fra kl. 23:45 går målingen uansett hvor mange av de 15 som mangler kursen, også når alle mangler. Nye forsøk i samme kjøring får fortsatt kallene først, og i helga går målingen selv om fredagen feilet | medium | **avgjort**, koden var slik (`f58cf7b`). `TestKl2345` prøver 2 av de 15 som mangler, ingen test prøver alle 15, og instruksjonen 29.10 har ingen kodeendring |
| BH2, VG2, ECH3, ECH2 | *Lagt til 2026-10-29:* `test_gaar_fra_23_45_ogsaa_naar_alle_15_mangler` i `TestKl2345` prøver at alle 15 mangler kursen for børsdagen og basen har eldre kurser: kl. 23:44:59 i Oslo venter målingen med 0 kall, og kl. 23:45:00 går den med de 4 kallene som er igjen, og utskriften sier at 15 av de 15 mangler | medium | **prøvd**, ingen endring i `src/`. Mutanten der målingen venter når alle mangler (`len(mangler) == len(lista)` i betingelsen), feilet i testen |
| ECH1, BH3 | Når målingen i kjøringen kl. 23:45 starter etter midnatt i Oslo, venter den, og ingen kjøring kommer etter | medium | **ikke rettet**, spørsmål til gruppen («Åpent»). Hentingen gjør ingen nye kall fra 23:50 (`KL_23_50`), så målingen starter normalt før midnatt |
| ECH1, BH3 | *Svart 2026-10-29 kl. 09:20 (gruppens svar, b):* starter målingen etter midnatt i Oslo, venter den som nå. Hentingen gjør ingen nye kall fra 23:50, så det skjer sjelden, og i verste fall går noen kall tapt den kvelden | medium | **avgjort**, ingen endring |
| VG1 | Vinduet fra børsdagen var bare prøvd på hverdager, så et vindu fra kalenderdagen ville overlevd | medium | **rettet** i `0640378`: lørdagen i `test_vinduet_staar_ved_hvert_tall` |
| BH1, ECH5, VG3 | Grensen er klokka da målingen starter, ikke kjøringen kl. 23:45. En kjøring kl. 23:15 som når målingen etter 23:45, eller en måling for hånd, går også | low | **rettet** i ordlyden i README-en og hjelpen: «startes kl. 23:45 eller senere». Ingen lås og ingen kjøring for hånd mens jobben går (svaret kl. 23:19, c) |
| ECH4 | En treg kjøring kl. 23:15 som fortsatt går kl. 23:45, gjør at kjøringen kl. 23:45 ikke starter (`IgnoreNew`) | low | **står**: gjelder også nye forsøk i hentingen, og er slik 2.3d er bygget |
| BH4, ECH6 | Uten base sa utskriften at hentingen og nye forsøk får kallene først, og testen sjekket ikke grunnen | low | **rettet**: egen linje «Basen finnes ikke …», og testen sjekker den |
| VG4, BH9 | Testen for 23:45 sjekket ikke symbolene eller at «venter» ikke står i utskriften, og docstringen nevnte bare EQNR | low | **rettet** |
| BH10 | Kodene fra kjøringene i testen for vinduet ble ikke sjekket | low | **rettet** |
| BH7 | Docstringen sa at den falske docker «svarer aldri». Den feiler med kode 1 | low | **rettet**: «feiler alltid» |
| ECH7 | Med fristen på 1 s kan `docker.cmd` drepes før den skriver `docker.txt` på en treg runner | low | **står**: skriptet spør to ganger, ved start og etter 5 s, og CI var grønn |
| ECH8 | Greinen «Fant ikke docker.» kjøres ikke lenger av noen test | low | **står** |
| VG6 | «Fant ikke Docker Desktop.» avhenger av om Docker Desktop kjører på maskinen | low | **står**: ingen test sjekker linja |
| BH5 | `exists()` kunne bli sann fordi `manglende_i_basen` lager basen | low | **avvist** etter oppslag: `manglende_i_basen` returnerer før basen åpnes når den mangler |
| BH6 | «Starter Ollama.» og «Stopper Ollama.» kunne ha en annen ordlyd i skriptet | low | **avvist** etter oppslag: begge står slik i `start/kveldshenting.ps1` |
| BH8, VG5 | At docker fantes på PATH på runneren, er sluttet fra loggen, ikke sett | low | **står** som i «Åpent»: loggen viser «Stopper Ollama.», som bare skjer når `docker info` svarte |
| ECH9 | Et siste argument som er ett siffer, leses som omdirigering i `docker.cmd` | low | **avvist**: ingen kall slutter på et siffer |

## Åpent

- **Datoen før første kall:** instruksjonen sier at valget stopper hvis `apiRequestsDate` ikke er dagens dato i GMT. På en dag uten henting, som en lørdag, står `apiRequestsDate` på gårsdagen til første kall (regel 15), så en streng stopp før første kall ville gitt 0 målinger på dager børsen er stengt, mot avgjørelsen kl. 22:17, b). Valget godtar derfor en tidligere dato før første kall og leser den som 0 brukt i dag, som `les_kvotetall` og regel 15. Etter hvert kall må datoen være dagens. En dato etter dagens i GMT stopper alltid. Gruppen avgjør før flettingen.
  *Avgjort 2026-10-28 kl. 23:19 (gruppens svar, a):* som bygget. `test_gaarsdagens_dato_foer_foerste_kall_er_0_brukt_i_dag` og `test_stopper_naar_kvoten_staar_paa_gaarsdagen_etter_et_kall`.
- **Vinduet:** tre måneder til og med børsdagen, som FR-413 og §40, ikke det faste vinduet `2026-07-02`–`2026-10-02` fra §42–§52. Med et fast vindu blir en ny måling av samme aksje lik den gamle, og c) i avgjørelsen kl. 22:17 gir ingen ny kunnskap. Tallene fra valget kan derfor ikke settes rett inn i rangeringen i §50–§52 uten at vinduet står ved dem. Gruppen avgjør før flettingen.
  *Avgjort 2026-10-28 kl. 23:19 (gruppens svar, b):* tre måneder bakover fra børsdagen, ved hvert tall. `test_vinduet_staar_ved_hvert_tall`. Rader med et annet vindu enn §50–§52 føres i egen tabell i `malinger.md` (svaret kl. 23:36, g).
- **De 15 i lista** måles ikke av valget. Omsetningen deres kan regnes av kursene i basen uten kall, men det er ikke en del av 2.13.
- **BH1, ECH2, lås (spørsmål til gruppen):** en måling for hånd samtidig med jobben, eller en henting for hånd samtidig med målingen, kan ta kall nummer 21 fra bonuskvoten før kontrollen etter kallet ser det. Skal valget ta en låsefil i `data/`?
  *Avgjort 2026-10-28 kl. 23:19 (gruppens svar, c):* ingen lås.
- **ECH4 (spørsmål til gruppen):** mangler én av de 15 kursen for børsdagen hele kvelden, blir det ingen måling den dagen og ikke i helga etter. Skal målingen gå når nye forsøk er brukt opp, for eksempel i kjøringen kl. 23:45?
  *Avgjort 2026-10-28 kl. 23:19 (gruppens svar, d):* ja, kl. 23:45. Bygget i `f58cf7b`.
- **BH11:** en ny aksje i OBX som ikke er blant de 214, måles i rekkefølgen i lista, uten forrang.
- **CI:** steget «Kveldshentingen på Windows» feilet på `ab7b967` (40777327364) fordi Docker svarte på runneren innen ett sekund, så skriptet startet og stoppet Ollama, mens `test_hele_jobben_uten_docker_henter_uten_ki_og_gir_koden_fra_hentingen` krever at det ikke skjer. Den delen av skriptet og påstanden er ikke endret i 2.13.
  *Rettet 2026-10-28 i `441b922`:* runneren har en docker på PATH (PATH i testen er den falske uv, mappa til git og System32). Feilen kom også på main på `1721d9f` (40770982416), som bare endret `epics.md` og `malinger.md`, så den kom ikke fra 2.13. Testene for jobben har nå en falsk docker først i PATH som aldri svarer og skriver kallene til `docker.txt`, og testen for hele jobben krever at den er spurt.
- **Lista over Oslo Børs** er fila fra 22.10. Nye noteringer kommer ikke med før lista hentes på nytt (avgjørelsen 22.10 kl. 23:14 under 2.12).
- *Lagt til 2026-10-29 (gjennomgangen, BH2, VG2, ECH3, ECH2, spørsmål til gruppen):* fra 23:45 går målingen også når alle 15 mangler kursen. Skal den vente når alle mangler, eller når basen ikke har noen kurs for børsdagen?
  *Avgjort 2026-10-29 kl. 09:20 (gruppens svar, a):* den går, også når alle mangler. Nye forsøk i samme kjøring får fortsatt kallene først, og i helga går målingen selv om fredagen feilet. Som bygget i `f58cf7b`.
- *Lagt til 2026-10-29 (gjennomgangen, ECH1, BH3, spørsmål til gruppen):* starter målingen i kjøringen kl. 23:45 etter midnatt i Oslo, venter den. Skal den gå også da, med børsdagen fra før midnatt?
  *Avgjort 2026-10-29 kl. 09:20 (gruppens svar, b):* den venter som nå. Hentingen gjør ingen nye kall fra 23:50, så det skjer sjelden, og i verste fall går noen kall tapt den kvelden.
- *Lagt til 2026-10-29 (gruppens svar kl. 09:20):* ingenting står igjen for gruppen før flettingen. Flettingen kommer i en egen instruksjon torsdag 29.10 kl. 23:50, etter jobbens siste kjøring (svaret 28.10 kl. 23:22).
