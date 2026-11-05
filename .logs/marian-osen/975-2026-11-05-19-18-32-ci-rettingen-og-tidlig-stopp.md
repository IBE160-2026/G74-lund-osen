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
