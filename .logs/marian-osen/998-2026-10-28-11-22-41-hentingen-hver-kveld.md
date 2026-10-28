# Hentingen hver kveld

## 2026-10-28 kl. 11:22 — Marian Osen

### Oppgave
Instruksjonen kl. 10:34 28.10: bygg story 2.3d, hentingen som jobb i Oppgaveplanlegging, etter gruppens svar 26.10 kl. 22:58 og 27.10 kl. 20:58. Bygges og stopper før flettingen. Ingen jobb legges inn, og ingen arbeidskopi lages nå.

### Plan
- Instruksjonen i dagsfila 28.10, og story 2.3d i `epics.md` etter 2.3b, på main.
- Grenen `2-3d-hentingen-hver-kveld`: spesifikasjonen `_bmad-output/implementation-artifacts/spec-2-3d-hentingen-hver-kveld.md`, skriptene i `start/`, testene, README-en, `docs/hjelp.md` og Prøve 4 i §9.
- Hele settet, mutanten, gjennomgangen med tre linser, rettelsene, triagen i spesifikasjonen og i PR-en, og CI.

### Resultat
- Kvotesjekken kl. 10:35: 0 brukt 28.10 i GMT, 20 igjen. Ingen andre kall, `src/fetch_prices.py` ikke kjørt, `data/db/ose.db` og `.env` ikke rørt.
- Main: instruksjonen i `730f64f5`, story 2.3d i `85998f65`.
- PR #104, åpen: spesifikasjonen `c4fb9409`, skriptene og dokumentene `5b5b7379`, rettelsene fra gjennomgangen `c852bbd1`, triagen `045e59d2`.
- `start/kveldshenting.ps1` kjører fra jobbens egen arbeidskopi, løsrevet på commiten `origin/main` hadde ved midnatt. Den krever at `data/` og `.env` er lenker til hovedkopien, starter Docker Desktop og Ollama med én frist på 180 s og henter uten KI-tekst hvis de ikke svarer. Loggen er `data/logg/`, og skriptet avslutter med koden fra hentingen.
- `start/legg-inn-kveldshentingen.ps1` legger inn jobben hver dag kl. 22:15 og så hver halvtime til 23:45. `start/ta-bort-kveldshentingen.ps1` tar den bort. Ingen av dem er kjørt.
- Hele settet: 3803 bestått og 24 hoppet over på `5b5b737`, og 3806 bestått og 24 hoppet over på `c852bbd`. Det nye steget i CI kjørte 23 tester på `windows-latest`, og alle besto. CI var grønn på head-en `045e59d` (40671201799).
- Mutanten, `origin/main` i stedet for commiten fra midnatt, ble fanget på begge head-ene, og fila var lik HEAD etterpå.
- Gjennomgangen: BH 18, ECH 13 og VG 8 funn. Rettet: ECH1 og ECH2 (high), ECH3, ECH4, BH2, BH3, VG1 og VG2 (medium), og flere med dom low. Avvist etter oppslag: BH1 og BH4.

### Åpne punkter
- 2.3d BH6: en henting for hånd samtidig med jobben er ikke sperret. Spørsmål til gruppen før flettingen.
- 2.3d ECH5: jobben setter `OSE_KI_TJENESTE`, som overstyrer `av` eller en tjeneste i skyen i `.env`. Spørsmål til gruppen før flettingen.
- 2.3d: FR-401 i `prd.md` er ikke endret, men beslutningen 29.09 sier at kravet endres når 2.3 er bygget. Gruppen avgjør.
- 2.3d: arbeidskopien, lenkene og jobben settes opp på PC-en etter flettingen, i Prøve 4 før kl. 22, og prøven skal gi 0 kall. Første kjøring er 29.10.
- 2.3d VG4, BH7, BH9/ECH8, BH15/VG7 og BH16 (low) står under «Åpent» i spesifikasjonen.
