# CI-rettingen og kveldsjobbens tidlige stopp

## 2026-11-05 kl. 19:18 — Marian Osen

### Oppgave
Instruksjonen kl. 19:15 05.11: én PR med `exit 0` i «Start demoen på Windows» (svaret 03.11 kl. 20:48, 1) og et tidlig stopp i `start/kveldshenting.ps1` når dagen alt er ferdig (svaret 05.11 kl. 12:33). Den skulle flettes før kl. 21:20. Var det uklart hva «ferdig» er, skulle jeg stoppe og si fra.

### Plan
- Steg 0 og kvoten, så instruksjonen i dagsfila og de to Avgjort-linjene i `epics.md`.
- Slå opp `tester.yml`, `start/kveldshenting.ps1`, `src/omsetning.py` og FR-401 og FR-413 i PRD-en før grenen.

### Resultat
- Kvoten kl. 19:15 (18:15 GMT): `apiRequests` 20 med `apiRequestsDate` 2026-11-04, altså 0 brukt og 20 igjen 05.11 i GMT, og `extraLimit` 463. Ingen andre kall.
- `909e161f`: instruksjonen i dagsfila. `113beb8e`: «Avgjort 2026-11-05 kl. 12:33» under story 2.3d og «Avgjort 2026-11-05 kl. 19:13» under story 10.4. Begge er pushet etter dokumenttestene (257 bestått).
- Ingen gren, ingen kode og ingen PR. Stoppet etter steg 1, fordi det ikke er klart når målingen er «ferdig» (se åpne punkter).
- `data/db/ose.db`, oppgaven og worktreen `G74-lund-osen-jobb` er ikke rørt, og jobben er ikke kjørt.

### Åpne punkter
- Gruppen må avgjøre hva «målingen er ferdig» betyr for det tidlige stoppet i kveldsjobben. Målingen (FR-413, `src/omsetning.py`) bruker alle kallene som er igjen av dagens i GMT, og det vet bare `/api/user`, ikke basen. Forslag: a) etter hentingen og KI-tekstene stopper kjøringen uten Docker og Ollama, men kjører fortsatt `--maal-omsetning`, som har sine egne regler for kvoten og kl. 23:45; b) målingen regnes som ferdig når `omsetning` har en rad målt i dag; c) sjekken leser `/api/user`.
- CI-rettingen (`exit 0` i «Start demoen på Windows») er fortsatt ikke bygget.

## 2026-11-05 kl. 20:43 — Marian Osen

### Oppgave
Instruksjonen kl. 19:41 05.11: den samme PR-en etter gruppens svar 05.11 kl. 19:33 (forslag a), med `exit 0` i «Start demoen på Windows» og sjekken av dagen før steg 3 i kveldsjobben, flettet før kl. 21:20.

### Plan
- Kvoten, instruksjonen i dagsfila og svaret kl. 19:33 under story 2.3d.
- Grenen `2-3d-tidlig-stopp-og-ci`, én commit per endring, hele settet alene før hver commit med kode eller tester, mutanter, gjennomgang med tre linser, triage, CI, fletting og dokumentene etterpå.
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-2-3d-tidlig-stopp-og-ci.md`.

### Resultat
- Kvoten kl. 19:41 (18:41 GMT): `apiRequests` 20 med `apiRequestsDate` 2026-11-04, altså 0 brukt og 20 igjen 05.11 i GMT, og `extraLimit` 463. Ingen andre kall.
- Main: `1d588198` (instruksjonen) og `9706d1b8` (svaret kl. 19:33 under story 2.3d).
- Grenen: `2b26b542` (a), `f03bd70e` (b: `src/dagen_ferdig.py`, sjekken i `start/kveldshenting.ps1`, testene, README-en, `docs/hjelp.md` og PRD-linja), `3d53ca36` (testen for a), `7ebc9aca` (rettingene etter gjennomgangen) og `fcc676e5` (spesifikasjonen og merkelappen). PR #114, squash-flettet i `0955f796`, låst til head-en. Etterpå på main: `0f99c4e5`.
- Hele settet alene: 4082 (6 porttester), 4082 (7 porttester), 4084 (6 porttester og merkelappen for spesifikasjonen, rettet) og 4088 bestått (3 porttester), 24 hoppet over hver gang. Mutant A og B fanget, filene lik HEAD etter begge.
- Gjennomgangen: 26 funn, 19 rader, ingen på høy. 8 rettet, 1 avvist (VG3) og 10 står med grunnen. CI grønn på head-en (42091407924 og 42095609243) og på flettecommiten (42096163757).
- `data/db/ose.db`, oppgaven og worktreen `G74-lund-osen-jobb` er ikke rørt, og jobben er ikke kjørt. `src/fetch_prices.py` er ikke kjørt.
- Punktet om CI (`exit 0`) og spørsmålet fra kl. 19:18 er krysset av i issues.md.

### Åpne punkter
- ECH1: en indeks som feilet en dag der de 15 har kursene, hentes ikke på nytt, så den dagen blir aldri «ferdig». Graden er satt til lav i triagen, og gruppen må si om det godtas.
- Første ekte kjøring med sjekken er fredag 06.11 kl. 22:15. Se i loggen for den dagen.
- *Rettet 2026-11-05 (gruppens svar kl. 21:01):* ECH1 i PR #114 er middels, ikke lav, for graden skal ikke settes ned. Funnet godtas: hovedindeksen blir i «ferdig», og en kveld der den feiler, går kjøringene som i dag. PR #114 ble flettet med ECH1 åpent, mot steg 4 i instruksjonen kl. 19:41, og flettingen står.
