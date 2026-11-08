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

## 2026-11-08 kl. 12:50 — Marian Osen

### Oppgave
Instruksjonen kl. 11:27: gruppens svar kl. 11:24 føres (forslagene i spørsmål 1–3 er godtatt), og README-ryddingen i PR #121 (3.5i) bygges etter spesifikasjonen i worktreen `G74-lund-osen-3-5i`. Det stoppes før flettingen.

### Plan
- Dagsfila, så main flettet inn i grenen, og svaret i spesifikasjonen og `epics.md`.
- `docs/installasjon.md` lages med et skript, så flyttingen blir ordrett. README-en, hjelpen, `src/ki_tekst.py`, `.env.example`, regel 19 og `sprint-status.yaml` rettes.
- Testene leser delene der de står, og a), c), d), e), f) og g) får tester. b) sjekkes én gang.
- Hele settet alene før hver commit som endrer tester. Så mutantene, gjennomgangen, triagen, pushen og CI.
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-3-5i-installasjonen-i-egen-fil.md`.

### Resultat
- Main: `e4048ce6` (dagsfila, med kvoten 0 brukt og 20 igjen 08.11 i GMT, og `extraLimit` 463).
- Grenen `3-5i-installasjonen-i-egen-fil`:
  - `643d32cd`: main flettet inn.
  - `af05e738`: svaret kl. 11:24.
  - `7be9aac8`: byggingen.
  - `059a0ea9`: testen for f) teller testene etter 3.5i.
  - `4d1656f7`: rettingene etter gjennomgangen.
  - `8d858b59`: triagen i spesifikasjonen.
- b) er sjekket én gang mot `958c27a3`: 396 linjer, 0 avvik og 12 linjer med rettet sti. De seks pilene gir avtrykkene fra før når stiene rettes tilbake.
- Hele settet ga 4573 bestått, 24 hoppet over og 0 feilet tre ganger (11:57:43–12:11:01, 12:12:35–12:25:45 og 12:31:44–12:44:17), med 3,5–3,8 GB ledig. Dokumenttestene ga 262 bestått før pushen.
- Mutantene: sju, alle drept til slutt. Mutanten for f) overlevde først. sha256 var lik HEAD etter hver av dem.
- Gjennomgangen fant 16 funn fra Blind Hunter, 5 fra Edge Case Hunter og 3 fra Verification Gap. BH4, BH6, ECH1 og ECH5 (medium) er rettet. BH1 (medium) står åpen som spørsmål til gruppen.
- CI er grønn på `8d858b59` (run 42477209734): docker, dobbeltklikk på Windows og macOS, og pytest.
- `src/app.py` er ikke endret, så bildene i `docs/appen/` er de samme.

### Åpne punkter
- BH1 i 3.5i (medium, regel 25): lenken «Den ekte versjonen» i demoen lander på linja om dobbeltklikket i README-en, ikke på Docker-stegene. Forslag: i en egen PR lenke til `docs/installasjon.md#den-ekte-versjonen`, med nye bilder i `docs/appen/` og ECH7 og BH16 samtidig.
- VG2 i 3.5i: raden D7 og innledningen til §9 i `docs/kvalitetssikring.md` viser til README-en, og rettes før README-prøven.
- VG3 i 3.5i: morgensjekken (`.github/scripts/morgensjekk.py`) sjekker bare lenkene i README-en, ikke i `docs/installasjon.md`.
- PR #121 er ikke flettet.
