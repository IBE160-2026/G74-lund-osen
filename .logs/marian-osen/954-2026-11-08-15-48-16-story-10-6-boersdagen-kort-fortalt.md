# Story 10.6: KI-teksten om dagen på forsiden, «Børsdagen kort fortalt»

## 2026-11-08 kl. 15:48 — Marian Osen

### Oppgave
Instruksjonen kl. 14:05 08.11, første story av sju: spesifikasjon og bygging av 10.6 på egen gren med PR, stopp før flettingen. Gruppen er borte fra kl. 15, og Claude Code bygger etter forslagene i spesifikasjonen (svaret kl. 12:32). Ollama og Docker Desktop kunne startes til 10.6 (svaret kl. 11:57).

### Plan
- Spesifikasjon etter storyen, FR-601–FR-607, svarene 08.11 og designutdraget §3.
- Grunnlaget, prompten `dag-1`, kontrollen, hentingen, visningen, hjelpen og demoen.
- Demoteksten med Gemma og prøvekjøringen på `ose.db` med `mode=ro`.
- Hele settet alene, mutantene, gjennomgangen med tre linser, triage, push, PR og CI.

### Resultat
- Kvoten kl. 14:05: `apiRequestsDate` 2026-11-07, altså 0 brukt og 20 igjen 08.11 i GMT, `extraLimit` 463. Ingen andre API-kall.
- På main: `408b7494` (instruksjonen i dagsfila og Lagt til-linja i `docs/skisser/2026-11-06/LESMEG.md`) og `907393d6` (Lagt til-linja under regel 22 om prøvekjøringer med `mode=ro`).
- Grenen `10-6-ki-teksten-om-dagen` i worktreen `G74-lund-osen-10-6`: `1c27113e` (byggingen), `d78f2e4b` (rettingene etter gjennomgangen) og `46f883e0` (mutantene på nytt). PR #122, ikke flettet. CI grønn på `46f883e0` (run 42490597204): pytest, docker og dobbeltklikk på Windows og macOS.
- Demoteksten ble laget med Gemma kl. 14:28 og på nytt kl. 14:46 etter `ruff format`, og besto begge gangene. Prøvekjøringen (§57 i `malinger.md`): 10 av 10 besto for 26.10–06.11, og sha256 for `ose.db` var den samme før og etter. Etter gjennomgangen besto alle 10 også den nye kontrollen.
- Hele settet alene: 4631 bestått, 24 hoppet over og 0 feilet (15:00:33–15:10:32), og etter rettingene 4650 bestått, 24 hoppet over og 0 feilet (15:22:02–15:31:42). To kjøringer før det ga 16 og 3 feil, som ble rettet.
- Mutantene: sju på `1c27113e` og ti på `d78f2e4b`, alle fanget, og hver fil var lik HEAD etterpå.
- Gjennomgangen: Blind Hunter 11, Edge Case Hunter 14 og Verification Gap 11 funn. Høy og middels er rettet, utenom BH9, som er avvist. Kontrollen godtar nå bare formene, «og», «men» og tegnsetting, og teksten om dagen lages først når alle aksjene har en rad.
- Ollama og Docker Desktop ble startet kl. 14:20 og 14:46 og stoppet etter demoteksten og prøvekjøringen, aldri samtidig med hele settet.
- `data/db/ose.db` er bare lest med `mode=ro`. Oppgaven, worktreen `G74-lund-osen-jobb` og `_privat/` er ikke rørt.

### Åpne punkter
- PR #122 (10.6) er ikke flettet; gruppen går gjennom de 12 spørsmålene i spesifikasjonen før flettingen.
- ECH14: feiler hovedindeksen om kvelden og hentes neste kveld, er dagen uten tekst under «Velg dag».
- BH7 og ECH11: bryteren på forsiden beholder perioden og dagen, men ikke sorteringen.
- VG10: at hentingen og siden bruker samme liste når den ikke har 15 aksjer, er bare testet i `dagsgrunnlag`.
