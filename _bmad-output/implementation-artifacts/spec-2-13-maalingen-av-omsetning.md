---
title: 'Story 2.13: målingen av omsetning som jobben kjører hver kveld'
type: 'feature'
created: '2026-10-28'
status: 'in-progress'
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
- **AD-6:** hvert uttrekk skrives som `<prefiks>-raa-<ÅÅÅÅ-MM-DD>.json` og skrives aldri om. `nyeste_snapshot` lar datoen avgjøre alene, og ved lik dato vinner `KURSPREFIKS`. **AD-16:** nummererte migrasjoner, `0001`–`0007` i dag. Den ekte basen står på versjon 7.
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
- **Kallene:** alle som er igjen av `dailyRateLimit` i dag i GMT, regnet fra `/api/user` før første kall. Før hvert kall må `apiRequests` være under `dailyRateLimit`, så kall nummer 21 aldri gjøres. Etter hvert kall må `apiRequests` ikke være over `dailyRateLimit`. Ingen kall holdes igjen (avgjørelsen kl. 22:17).
- **Stoppene:** før første kall stopper valget med 0 kall og kode 1 når basen er en demobase, når børsdagen ikke kan regnes (`UtenforKalenderen`), når en aksje i lista mangler kursen for børsdagen eller basen ikke kan leses, når lista over Oslo Børs mangler, og når kvoten ikke kan leses. Underveis stopper det, med kode 1, hvis `extraLimit` er en annen enn ved første lesing, hvis `apiRequestsDate` er en annen enn dagens dato i GMT etter et kall, hvis datoen i GMT på klokka har skiftet siden starten, eller hvis kvoten ikke kan leses. Det som alt er målt, lagres også da.
- **Børsdagen** er `innevaerende_boersdag` av datoen i Oslo: i dag på en børsdag, ellers siste børsdag før. På en børsdag før hentingen har dagens kurser, stopper valget derfor ved kursvakten med 0 kall, så kallene står til hentingen og nye forsøk (avgjørelsen kl. 22:17, b).
- **Vinduet** er tre måneder til og med børsdagen: fra samme dag tre måneder før (siste dag i måneden når den dagen ikke finnes) til børsdagen, som i §40 (`2026-07-22`–`2026-10-22`). Vinduet står i raden. §42–§52 brukte det faste vinduet `2026-07-02`–`2026-10-02`. Se «Åpent».
- **Medianen:** `volume × close` per rad i vinduet. En rad med volum 0 tas med med omsetning 0, som i §42. En rad uten tall for `close` eller `volume` tas ikke med, men telles i `rader_uten_tall`. Gir ingen rad tall, eller feiler kallet, lagres raden med `feil` i stedet for medianen. Aksjen regnes da som målt den dagen, så en ticker som ikke gir rader, ikke tar kallene hver kveld.
- **Tabellen** er `omsetning` i `0008_omsetning.sql`: `symbol`, `maalt` (starten av kjøringen i UTC med offset, som `hentet`), `fra`, `til`, `handelsdager`, `dager_uten_volum`, `rader_uten_tall`, `median_omsetning` i NOK, uavrundet (regel 21), og `feil`. Primærnøkkelen er `(symbol, maalt)`, så en ny måling legges til og skriver aldri over en gammel. Det er ingen trigger mot `aksje`, fordi aksjene ikke står i lista. Ingen tabell som finnes, endres.
- **Rådataene** står i `omsetning<n>-raa-<børsdag>.json` i `data/raa/`, med første `n` fra 1 som ikke finnes, skrevet med modus `x` (AD-6). Datoen er børsdagen, ikke kjøredagen, så fila aldri har nyere dato enn kursfila, og ved lik dato vinner kursfila (`nyeste_snapshot`). Fila skrives først, og så radene i basen. Feiler fila, skrives ingen rader.
- **Utskriften** sier hvor mange kall valget bruker, hvilke aksjer, antall handelsdager og dager uten volum per aksje, og kvoten etter. Kurser, volumer og medianene skrives ikke ut. Medianene står i tabellen.
- **Jobben** kjører `uv run python src/fetch_prices.py --maal-omsetning` etter hentingen i hver kjøring, også når hentingen ga kode 1 eller 3. Valget sjekker selv om kursene finnes. Loggen får linja «Målingen avsluttet med kode <n>.», og jobben avslutter fortsatt med koden fra hentingen.

## Planen

1. Spesifikasjonen.
2. `src/omsetning.py`, `0008_omsetning.sql`, valget i `fetch_prices.py`, `start/kveldshenting.ps1`, testene, README-en, `docs/hjelp.md`, linja under FR-413 og 2.13 i `sprint-status.yaml` i én commit (regel 19).
3. Hele settet, mutanten, gjennomgangen og triagen her og i PR-en.

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: stoppen ved endret `extraLimit` tatt ut.

## Gjennomgangen

## Åpent

- **Datoen før første kall:** instruksjonen sier at valget stopper hvis `apiRequestsDate` ikke er dagens dato i GMT. På en dag uten henting, som en lørdag, står `apiRequestsDate` på gårsdagen til første kall (regel 15), så en streng stopp før første kall ville gitt 0 målinger på dager børsen er stengt, mot avgjørelsen kl. 22:17, b). Valget godtar derfor en tidligere dato før første kall og leser den som 0 brukt i dag, som `les_kvotetall` og regel 15. Etter hvert kall må datoen være dagens. En dato etter dagens i GMT stopper alltid. Gruppen avgjør før flettingen.
- **Vinduet:** tre måneder til og med børsdagen, som FR-413 og §40, ikke det faste vinduet `2026-07-02`–`2026-10-02` fra §42–§52. Med et fast vindu blir en ny måling av samme aksje lik den gamle, og c) i avgjørelsen kl. 22:17 gir ingen ny kunnskap. Tallene fra valget kan derfor ikke settes rett inn i rangeringen i §50–§52 uten at vinduet står ved dem. Gruppen avgjør før flettingen.
- **De 15 i lista** måles ikke av valget. Omsetningen deres kan regnes av kursene i basen uten kall, men det er ikke en del av 2.13.
- **Lista over Oslo Børs** er fila fra 22.10. Nye noteringer kommer ikke med før lista hentes på nytt (avgjørelsen 22.10 kl. 23:14 under 2.12).
