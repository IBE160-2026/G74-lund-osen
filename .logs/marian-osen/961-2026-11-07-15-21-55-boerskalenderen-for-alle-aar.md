# Børskalenderen for alle år

## 2026-11-07 kl. 15:21 — Marian Osen

### Oppgave
Instruksjonen kl. 13:35 07.11: story 2.16 «Børskalenderen for alle år», 8.20c og porttestene i én PR på egen gren, etter gruppens svar kl. 10:33, 11:05, 11:10 og 11:47. PR-en stopper før flettingen.

### Plan
- Steg 0 og kvotesjekken (regel 15), og instruksjonen i dagsfila.
- Storyen og svarene på main, i `epics.md`, `sprint-status.yaml`, kildene, PRD-en og kvalitetssikringen.
- Oppslag, så bygging i worktreen `G74-lund-osen-2-16`: én commit per sak med hele settet alene før hver commit, så mutanter, gjennomgang med tre linser, triage og CI.
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-2-16-boerskalenderen-for-alle-aar.md`, og avsnittet «8.20c, bygget 07.11» i spesifikasjonen for 8.20.

### Resultat
- Kvoten kl. 13:35 (12:36 GMT): `apiRequestsDate` 2026-11-06, så 0 brukt og 20 igjen 07.11 i GMT, `extraLimit` 463. Ingen andre kall. `src/fetch_prices.py` er ikke kjørt, og `data/db/ose.db` er ikke rørt. PDF-en er bare sjekket med sha256.
- Main: `fa8c112e` (instruksjonen) og `5b1e2778` (story 2.16 som backlog med svarene). 2.15 var gitt til utbytte 13.10, så storyen fikk 2.16.
- Grenen `2-16-boerskalenderen-for-alle-aar`, PR #117:
  - `2b8db0d7`: porten.
  - `df946918`: kalenderen, med `FOERSTE_AAR = 2026` og ingen øvre grense.
  - `fea11d48`: 8.20c (U75, U76, U101).
  - `6eeaf5b2`: spesifikasjonene.
  - `c140e607`: rettingene etter gjennomgangen.
  - `cc6255af`: triagen.
- Hele settet alene før hver kodecommit, med ledig minne 4,6–4,7 GB av 15,7 GB:
  - 4338, 4378, 4380 og 4387 bestått, 24 hoppet over og 0 feilet.
  - De sju porttestene går gjennom igjen lokalt.
- Porten: `netstat` så lytteren 0 og 4 av 30 ganger, og `Get-NetTCPConnection` uten tilstand 30 av 30. Derfor spørres den før `netstat` (spørsmål 3).
- Mutantene:
  - Alle 14 fanget, utenom C. C er demotesten for januar 2027, som ventet: demoen var lik også før 2.16.
  - Hver fil var lik HEAD etterpå.
- Bildene:
  - Tatt med DevTools-protokollen i Edge uten vindu. Seks er byte for byte like.
  - `min-liste-demo.png` er ny, med samme høyde.
- Gjennomgangen ga 29 funn: Blind Hunter 10, Edge Case Hunter 8 og Verification Gap 11. Ingen var på høy.
  - Middels rettet: VG1, VG2, VG3 og BH2.
  - Middels åpent: BH1 og ECH1, som spørsmål 4.
- CI er grønn på `6eeaf5b2` (run 42379091292) og `cc6255af` (run 42380989445).
- Punktene om porttestene i `issues.md` (29.10 og 07.11) står åpne til PR #117 er flettet.

### Åpne punkter
- PR #117 venter på gruppens svar på spørsmål 1–4 i spesifikasjonen for 2.16: 2025 i kalenderen, teksten i U100, rekkefølgen i porten, og klokka langt fram i tid. BH1 og ECH1 (middels) står åpne til gruppen har svart (regel 25).
- Ved flettingen (VG6): datert linje ved `DEKKEDE_AAR` i `epics.md`, `designregler.md` og PRD-en, punkt 25 lukket, 2-16 til `done` i `sprint-status.yaml`, og radene for 2.16 i `docs/kvalitetssikring.md`.
- BH10, utsatt: vinduet ved dobbeltklikket nevner ikke en konto hos EODHD fra før. Kan tas med 3.4h eller 8.20a.
