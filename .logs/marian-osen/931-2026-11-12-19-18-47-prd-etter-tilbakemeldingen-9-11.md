# PRD-en etter tilbakemeldingen (9.11)

## 2026-11-12 kl. 19:18 — Marian Osen

### Oppgave
Ny story i Epic 9: PRD-en skulle skrives om etter tilbakemeldingen fra faglærer 12.11 (`tilbakemelding-prd.md`, `29cf2874`), etter gruppens svar kl. 18:00. Målet var en ny versjon med gjeldende tekst, slik briefen fikk v8 i 9.6. Instruksjonen ble limt inn kl. 18:03 i et nytt vindu i hovedkopien, med stegene 0–5 og sluttmarkøren. Den er lagret ordrett med klokkeslett i scratchpad-fila `instruksjon-2026-11-12-1803.md`, og ført i dagsfila på main når den står der.

### Plan
- Kvotesjekken (regel 15): `apiRequestsDate` sto på 2026-11-11, altså 0 kall brukt i dag i GMT og 20 igjen. Ingen andre API-kall.
- Lese tilbakemeldingen hele, finne neste nummer (9.11) og lage grenen `9-11-prd-etter-tilbakemeldingen` og worktreen `G74-lund-osen-9-11` fra `origin/main`.
- Taggen `prd-vurdert-2026-11-12` på `10265324`, før noe ble endret.
- Slå opp i koden hva hvert krav gjør nå, med to agenter. Skrive `prd.md` på nytt.
- Flytte de daterte linjene ordrett med et skript, som sjekker hver bit mot taggen.
- Gjennomgang med fire lesere, triage, tester, mutant og hele settet.

### Resultat
- Commitene på grenen:
  - `409f81f0`: spesifikasjonen, story 9.11 og sprintstatusen
  - `1ecd7213`: omskrivingen
  - `d38e1101`: CLAUDE.md, regel 19
  - `51dde713`: rettingene etter gjennomgangen
  - `336abced`: triagen i spesifikasjonen
  - `8ec61554`: README-testene
- `prd.md`: hvert FR og NFR har én gjeldende tekst og «Konsekvenser», med de samme ID-ene. Nytt er UJ-1, ordlista, tabellen «Kjerne, ekstra og senere», SM-1–SM-9 med krav, og plan A i vedlegg A. Gamle ankre står. Tekstene `src/hjelpetekster.py` siterer, står ordrett, og `src/` er ikke endret.
- Lengden, målt med wc: `prd.md` gikk fra 2 264 linjer og 28 752 ord til 1 672 linjer og 13 777 ord.
- `prd-endringslogg.md` har alle 275 «Rettet» og «Lagt til» ordrett, og tabellen over tilbakemeldingen øverst. Nye linjer føres under «Endringer etter 12.11».
- `begrunnelser.md` har fått §13 med resonnementet.
- Gjennomgangen: Blind Hunter, Edge Case Hunter og Verification Gap i to deler, med 60 funn. Triagen står i spesifikasjonen, og ingen funn på middels eller over står åpne.
- Mutanten: FR-108 uten «Konsekvenser» ble fanget. sha256 var lik HEAD etterpå.
- Testene:
  - Dokumenttestene: 2 591 bestått og 7 hoppet over.
  - Hele settet i tre deler, ingen samtidig med en annen pytest: 1 964 + 23, 2 181 + 1 og 1 246. Summen 5 415 er lik `--collect-only`.
  - Ruff er grønn.
- Pushet grenen og taggen, og laget PR #150. CI er grønn: pytest, docker og dobbeltklikk.

### Åpne punkter
- PR #150 venter på gruppens svar på spørsmålene 1–20 i `spec-9-11-prd-etter-tilbakemeldingen.md`. Den flettes tidligst etter 8.26 i natt, med main flettet inn i grenen først.
- Instruksjonen kl. 18:03 og Utført-linja skal føres i `docs/ai-prompts/2026-11-12.md` på main. Denne instruksjonen hadde ingen commit på main.
- Disse er foreslått som egne storyer i spørsmål 6 og 14–18:
  - en test som går gjennom alle malene etter rådord (punkt 26)
  - FR-111 for Min liste
  - «De 15 mest omsatte»
  - 3.4 til `done`
  - pekerne i `src/` til tekst som er flyttet
  - `fetch-tags` i CI
- `technology.md` fra faglærer (`a93c668f`) er ikke lenket i «Dokumentene» (spørsmål 11).
