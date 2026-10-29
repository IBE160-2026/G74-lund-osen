# Målingen av omsetning hver kveld (story 2.13)

## 2026-10-28 kl. 23:29 — Marian Osen

### Oppgave
Instruksjonen kl. 22:38: bygge story 2.13 i natt etter gruppens svar kl. 22:17. Valget `--maal-omsetning` i hentekommandoen skal måle de neste aksjene i lista over Oslo Børs med kallene som er igjen hver kveld, aldri med bonuskvoten. Jobben fra 2.3d skal kjøre det etter hentingen. Arbeidet stopper alltid før flettingen.

### Plan
- Steg 0–1: kvotesjekken, instruksjonen i dagsfila og avgjørelsen kl. 22:17 under 2.13 og 8.17 på main.
- Steg 2: grenen `2-13-maalingen-av-omsetning` i en egen worktree, spesifikasjonen (`_bmad-output/implementation-artifacts/spec-2-13-maalingen-av-omsetning.md`) og PR #105, så koden, testene og dokumentene.
- Steg 3: hele settet alene, mutanten, gjennomgangen med tre lesere, triagen, rettingene og CI.

### Resultat
- **Kvoten** kl. 22:38: 20 av 20 brukt 28.10 i GMT, `extraLimit` 463. Ingen andre kall.
- **Main:** instruksjonen i `a5014747`, avgjørelsen kl. 22:17 under 2.13 og 8.17 i `4e985641`.
- **Grenen**, PR #105 (utkast):
  - Spesifikasjonen i `41d39bc`.
  - Koden i `ab7b9678`: `src/omsetning.py`, `0008_omsetning.sql` (tabellen `omsetning`), valget i `fetch_prices.py`, `start/kveldshenting.ps1`, `tests/test_omsetning.py`, README-en, hjelpen, linja under FR-413 og avtrykket bak bildet av aksjesiden (bildet tatt på nytt, byte for byte likt).
  - Rettingene etter gjennomgangen i `fda73fd8`, og triagen i `e6287bf8`.
- **Minnet:** 4,3 GB ledig av 15,7 GB.
- **Hele settet:** 3849 bestått, 24 hoppet over og 0 feilet (22:57:49–23:05:44). Etter rettingene: 3861 bestått, 24 hoppet over og 0 feilet (23:16:23–23:24:49).
- **Mutanten** (stoppen ved endret `extraLimit` tatt ut) ble fanget begge gangene av `test_stopper_naar_extraLimit_endres_etter_et_kall`, og fila var lik HEAD etterpå.
- **Gjennomgangen:** BH 13, ECH 13 og VG 12 funn. Rettet: VG1 (high), BH3/ECH1, ECH3, BH4, VG3, VG4 og VG5, samt de fleste med dom low. BH2 er avvist etter oppslag.
- **CI** feilet på `ab7b967` (40777327364): Docker svarte på runneren, så testen for hele jobben fikk «Stopper Ollama». Den er grønn på head-en `e6287bf` (40779900164).
- `data/db/ose.db` og `.env` er ikke rørt, utenom lesingen av nøkkelen til kvotesjekken. Demobasen for bildet lå i en midlertidig mappe, som er slettet.

### Åpne punkter
- Gruppen avgjør før flettingen: datoen før første kall (en tidligere `apiRequestsDate` godtas som 0 brukt, så målingen går i helgene).
- Gruppen avgjør før flettingen: vinduet (tre måneder til og med børsdagen, ikke det faste fra §42–§52).
- Gruppen avgjør før flettingen: BH1/ECH2, om valget skal ta en lås mot to kjøringer samtidig.
- Gruppen avgjør før flettingen: ECH4, ingen måling når én av de 15 mangler kursen hele kvelden.
- Hvordan målingene fra tabellen føres i `malinger.md` (forslag: en ny § én gang i uka).
- Flett ikke mens jobben går, kl. 22:15–23:45 (ECH5).
- Testen for hele jobben på Windows kan feile i CI når Docker svarer innen ett sekund (40777327364).

## 2026-10-29 kl. 00:16 — Marian Osen

### Oppgave
Instruksjonen 28.10 kl. 23:41: 2.13 videre etter gruppens svar 28.10 kl. 23:19, 23:22 og 23:36 om PR #105, og CI-feilen på Windows. Arbeidet stopper alltid før flettingen, og PR #105 står som utkast.

### Plan
- Steg 0–1: kvotesjekken, instruksjonen i dagsfila og de tre svarene under story 2.13 på main.
- Steg 2: main flettet inn i grenen i en ny worktree, så én commit per punkt a–d, og mutanten for grensen kl. 23:45.
- Steg 3: hele settet alene, gjennomgangen med tre lesere av endringene etter `e6287bf`, triagen, rettingene og CI.

### Resultat
- **Kvoten** kl. 23:41: 20 av 20 brukt 28.10 i GMT, `extraLimit` 463. Ingen andre kall.
- **Main:** instruksjonen i `16c5d3ca`, og svarene kl. 23:19, 23:22 og 23:36 under 2.13 i `c2035716`.
- **Grenen**, PR #105 (utkast), head `08abdaba`:
  - Main flettet inn i `cd1e64d2`.
  - a) `f58cf7b3`: fra kl. 23:45 i Oslo stopper ikke en manglende kurs målingen, og utskriften sier hvor mange av de 15 som mangler (`TestKl2345`).
  - b) `441b922c`: en falsk docker først i PATH i testene for jobben. CI-feilen i 40777327364 og på main i 40770982416 (`1721d9f`, bare dokumenter) hadde samme årsak: runneren hadde en docker på PATH som svarte innen fristen på 1 s, så skriptet startet og stoppet Ollama.
  - c) `8c336afe`: `TestSvarene2319` og daterte linjer i triagen og «Åpent».
  - d) `e744f875`: README-en, hjelpen og en datert linje under FR-413.
  - Rettingene etter gjennomgangen i `06403784`, og triagen og mutanten i spesifikasjonen i `08abdaba`.
- **Minnet:** 4,2 GB ledig av 15,7 GB.
- **Hele settet:** 3867 bestått, 24 hoppet over og 0 feilet (23:50:30–23:59:07). Etter rettingene: 3867 bestått, 24 hoppet over og 0 feilet (00:04:10–00:12:08).
- **Mutanten** (grensen kl. 23:45 tatt ut) ble fanget begge gangene av `test_gaar_fra_23_45_naar_en_kurs_mangler`, og fila var lik HEAD etterpå.
- **Gjennomgangen:** BH 10, ECH 9 og VG 6 funn, ingen med dom high. Rettet: VG1 (medium) og 7 med dom low. To med dom medium er ikke rettet og går til gruppen.
- **CI:** grønn på `e744f87` (40784071691) og på head-en `08abdab` (40785774200).
- Worktreen er fjernet. `data/db/ose.db` og `.env` er ikke rørt, utenom lesingen av nøkkelen til kvotesjekken.
- Lukket i `issues.md`: de 4 punktene fra 28.10 om PR #105.

### Åpne punkter
- PR #105, spørsmål til gruppen: fra 23:45 går målingen også når alle 15 mangler kursen (BH2, VG2, ECH3, ECH2, dom medium).
- PR #105, spørsmål til gruppen: starter målingen i kjøringen kl. 23:45 etter midnatt i Oslo, venter den (ECH1, BH3, dom medium).
- 2.13 flettes torsdag 29.10 kl. 23:50, og ikke etter 23:59 (svaret kl. 23:22). Kallene som er igjen, brukes av målingen for hånd rett etter, før midnatt (svaret kl. 23:36).
- Målingene fra tabellen føres i `malinger.md` som en ny § hver søndag, første gang søndag 01.11 (svaret kl. 23:36, g).

## 2026-10-29 kl. 10:32 — Marian Osen

### Oppgave
Instruksjonen 29.10 kl. 10:25: 2.13 klar til flettingen i kveld, med gruppens svar 29.10 kl. 09:20 på de to spørsmålene fra gjennomgangen 29.10 i PR #105. Ingen kodeendring, og stopp før flettingen.

### Plan
- Steg 0–1: kvotesjekken, instruksjonen i dagsfila og svaret under story 2.13 på main.
- Steg 2: main flettet inn i grenen i en ny worktree, svaret i triagen og under «Åpent» i spesifikasjonen, testene for dokumentene og CI.

### Resultat
- **Kvoten** kl. 10:25 (09:25 GMT): `apiRequests` 20 med `apiRequestsDate` 2026-10-28, så 0 brukt og 20 igjen 29.10 i GMT, `extraLimit` 463. Ingen andre kall.
- **Main:** instruksjonen i `bc08a18a`, og svaret kl. 09:20 under story 2.13 i `epics.md` i `5b05db38`. CI grønn på begge (40849867055 og 40849927390).
- **Grenen**, PR #105 (fortsatt utkast): main flettet inn i `97ab8287`, og svaret i `2d0ea174`, med en «Svart»-rad ved BH2/VG2/ECH3/ECH2 og ECH1/BH3 i triagen, en «Avgjort»-linje under hvert spørsmål i «Åpent», og en linje om at ingenting står igjen for gruppen før flettingen. CI grønn på head-en `2d0ea174` (40850130502): pytest, docker og dobbeltklikk på Windows og macOS.
- **Slått opp:** fra 23:45 har `src/omsetning.py` ingen grense på hvor mange som mangler, så svaret a) er slik koden var. Bare en base som ikke finnes, venter fortsatt. `TestKl2345` prøver 2 av 15 som mangler, ingen test prøver alle 15, og det står i triagen. `KL_23_50` i `src/fetch_prices.py` bekrefter b).
- Testene for dokumentene (de seks i `docs/kvalitetssikring.md`) ga 253 bestått før hver push. Worktreen er fjernet. `data/db/ose.db` og `.env` er ikke rørt, utenom lesingen av nøkkelen til kvotesjekken.
- Lukket i `issues.md`: de 2 spørsmålene til gruppen om PR #105.

### Åpne punkter
- 2.13 flettes torsdag 29.10 kl. 23:50, og ikke etter 23:59, i en egen instruksjon. Kallene som er igjen, brukes av målingen for hånd rett etter, før midnatt (står fra før i `issues.md`).
- Ingen test prøver at målingen går fra 23:45 når alle 15 mangler kursen (svaret 29.10 kl. 09:20, a). Instruksjonen hadde ingen kodeendring.

## 2026-10-29 kl. 19:42 — Marian Osen

### Oppgave
Fortsette testblokka fra kl. 11:35 for 2.13, som stoppet kl. 11:48 med 7 feil i `tests/test_dobbeltklikk.py` i hele settet. Først finne ut om feilen kommer fra 2.13, og så committe testen og triageraden hvis settet er grønt.

### Plan
- Instruksjonen i dagsfila 29.10 (`4f85a46b`).
- `tests/test_dobbeltklikk.py` alene i worktreen og så på main, og se hva som lytter på port 8000.
- Hele settet, commit og CI bare hvis fila består. Ellers stoppe før commit.

### Resultat
- Kvoten kl. 19:36 (18:36 GMT): `apiRequestsDate` 2026-10-28, så 0 brukt og 20 igjen 29.10, og `extraLimit` 463. Ingen andre kall.
- `tests/test_dobbeltklikk.py` alene i worktreen, to ganger: 4 feil (19:37–19:38) og 5 feil, hver gang i `test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten` og `test_start_ps1_frigjoer_porten_rett_foer_webserveren`, men med ulike parametre. Første linje av feilen: utskriften sier «et annet program svarer allerede på http://127.0.0.1:8000 … Programmet er et program skriptet ikke fant navnet på», så `assert 'Den andre versjonen av OSE Signal kjører allerede …' in …` ([oss]), `assert 'python' in …` ([annen_mappe], [fremmed]) og `ValueError: substring not found` (frigjør-testene) feiler.
- På main, alene (19:40–19:41): 7 feil, de samme to testene med alle 7 parametrene. Feilen kommer altså ikke fra 2.13.
- Port 8000: ingenting lytter utenom testene.
- Årsaken, slik den ser ut: `Lyttere` i `start/start.ps1` spør `Get-NetTCPConnection -LocalPort 8000 -State Listen`. Med en Python-lytter på 127.0.0.1:8000 fant den ingenting, både i testmiljøet og i vanlig PowerShell, i og utenfor sandkassen. `netstat -ano` viste lytteren med tilstanden `FIN_WAIT_1` i stedet for `LISTENING`, og bare 4 porter totalt som `LISTENING`. Windows-oppdateringen KB5127936 ble installert 29.10, og maskinen startet på nytt kl. 02:31. Hele settet var sist grønt lokalt 28.10 kl. 23:50–00:12. At oppdateringen er årsaken, er ikke bevist, men det er det eneste som er endret.
- `tests/test_omsetning.py` alene i worktreen: 51 bestått. Den nye testen og triageraden er fortsatt ikke committet i `..\G74-lund-osen-2-13`. Raden sier at mutanten der målingen venter når alle mangler, feilet i testen. Kjøringen av mutanten kl. 11:35 er ikke sett i denne økten.
- Hele settet er ikke kjørt, og ingen commit, push eller CI er gjort på grenen. Ledig minne: 5 241 MB av 16 124 MB. Worktreen er ikke fjernet, fordi testen og raden bare finnes der.

### Åpne punkter
- `tests/test_dobbeltklikk.py` feiler lokalt i 4–7 av de 7 tilfellene for start.ps1 og porten, fordi `Get-NetTCPConnection -State Listen` ikke ser lytteren etter Windows-oppdateringen 29.10. Gruppen avgjør om maskinen skal startes på nytt og testen kjøres igjen, eller om testene for start.ps1 skal hoppes over lokalt og bare kjøres i CI.
- Testen og triageraden for 2.13 (og Rettet-linja ved ECH5) ligger ukommittert i `..\G74-lund-osen-2-13` til settet er grønt.

## 2026-10-29 kl. 20:06 — Marian Osen

### Oppgave
Kjøre testblokkene fra kl. 11:35 og 19:36 for 2.13 videre etter at maskinen ble startet på nytt (gruppens svar 29.10 kl. 19:49), fordi `tests/test_dobbeltklikk.py` feilet lokalt, også på main.

### Plan
- Instruksjonen i dagsfila 29.10 (`62fc181e`).
- `tests/test_dobbeltklikk.py` alene i worktreen, og se om `Get-NetTCPConnection` nå ser en lytter på 127.0.0.1:8000 som `Listen`.
- Hele settet, commit og CI bare hvis fila består. Ellers stoppe før commit.

### Resultat
- Omstarten: `LastBootUpTime` er 29.10 kl. 19:59:48.
- Kvoten kl. 20:02 (19:02 GMT): `apiRequestsDate` 2026-10-28, så 0 brukt og 20 igjen 29.10 i GMT, og `extraLimit` 463. Ingen andre kall.
- `tests/test_dobbeltklikk.py` alene i worktreen: 5 feil, 59 bestått og 11 hoppet over (20:03:59–20:04:42), og så 7 feil i en ny kjøring, i de samme to testene som kl. 19:36.
- En lytter jeg startet selv (Python, `socket.listen()` på 127.0.0.1:8000) får fortsatt tilstanden `FinWait1` i `Get-NetTCPConnection` og `FIN_WAIT_1` i `netstat -ano`, ikke `Listen`/`LISTENING`. Omstarten rettet altså ikke feilen. Lytteren er stoppet, og ingenting lytter på port 8000.
- Ledig minne: 6 186 MB av 16 124 MB.
- Steg 3 er ikke gjort: hele settet, ruff, commiten, Rettet-linja ved ECH5, pushen, CI, punktene i `issues.md` og Avklart-linja i refleksjonsloggen står igjen. Worktreen står med `9fc20a2c` ikke pushet og testen og raden ukommittert.

### Åpne punkter
- `tests/test_dobbeltklikk.py` feiler lokalt også etter omstarten (punktet står fra før i `issues.md`). Gruppen avgjør neste steg, for eksempel å hoppe over testene for start.ps1 lokalt og bare kjøre dem i CI, eller å la CI avgjøre for denne grenen.
- Testen og triageraden for 2.13 ligger fortsatt ukommittert i `..\G74-lund-osen-2-13` (står fra før).
