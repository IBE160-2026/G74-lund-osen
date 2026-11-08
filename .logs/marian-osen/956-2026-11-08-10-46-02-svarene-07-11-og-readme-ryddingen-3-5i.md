# Svarene 07.11, opplegget for brukertesten og README-ryddingen (3.5i)

## 2026-11-08 kl. 10:49 — Marian Osen

### Oppgave
Instruksjonen kl. 10:36 i `docs/ai-prompts/2026-11-08.md`: føre gruppens svar fra kvelden 07.11 i repoet, oppdatere opplegget for brukertesten etter sidene slik de er nå, og rydde README-en på en egen gren med PR, med stopp før flettingen, eller etter spesifikasjonen hvis noe sensor vil se, ikke er avklart.

### Plan
- Kvotesjekk, og så dagsfila med instruksjonen og kvoten 07.11.
- Svarene kl. 22:48, 22:49, 22:51 og 23:26 i `epics.md`, og testdagene og opplegget i spesifikasjonen 8.1 og `docs/brukertest.md`, slått opp i malene og koden.
- Worktree `G74-lund-osen-3-5i`, grenen `3-5i-installasjonen-i-egen-fil`, og spesifikasjonen `spec-3-5i-installasjonen-i-egen-fil.md`.

### Resultat
- Kvoten 08.11 kl. 10:36: 0 brukt og 20 igjen i GMT, `extraLimit` 463. De 20 kallene 07.11 gikk til målingen av omsetning (story 2.13), ett per aksje.
- `50103bcc`: dagsfila. `958c27a3`: svarene under «Prioritering», story 3.3, 8.1 og 10.4, og i spesifikasjonen 8.1 og `docs/brukertest.md`: rammen «Signalet forklart», bryteren «KI-tekst» øverst til høyre i rammen, datofeltet («I går» med dataene fra kvelden før), og at den ekte versjonen på denne maskinen startes med `uv run python src/app.py` fra repo-mappa på main. Docker bruker volumet `ose-db`, og «Start den ekte versjonen» stopper i en klon. Begge er pushet etter dokumenttestene (258 bestått). Kontrollen mot HEAD viste at bare `updated` er fjernet.
- Grenen: `8aca3062` (bare spesifikasjonen), PR #121, CI grønn på head-en (run 42468555515). Ingen kode eller tester er endret, så hele settet, mutantene og gjennomgangen er ikke kjørt.
- Stoppet etter spesifikasjonen med tre spørsmål. `src/app.py` endres ikke, fordi lenken i demoen er den samme, så bildene tas ikke på nytt, og ECH7 og BH16 står fortsatt åpne.

### Åpne punkter
- PR #121 (3.5i) venter på svar på de tre spørsmålene i spesifikasjonen: 1) overskriften «Enklest: dobbeltklikk (anbefalt)» med ankeret over de fem stegene, mens setningen om demoen flyttes; 2) «øverst i README-en» i setningen «Velg versjon»; 3) `docs/installasjon.md` som levende dokument, med en linje i regel 19.
