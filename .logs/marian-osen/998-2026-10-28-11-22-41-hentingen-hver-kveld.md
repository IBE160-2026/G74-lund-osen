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

## 2026-10-28 kl. 11:43 — Marian Osen

### Oppgave
Instruksjonen kl. 11:36 28.10: flett 2.3d etter gruppens svar kl. 11:34, legg inn jobben på PC-en med første kjøring torsdag 29.10, og ta Prøve 4, rad 5, i dag.

### Plan
- Føre instruksjonen og avgjørelsen kl. 11:34 på main, flette main inn i grenen og føre BH6 og ECH5 i triagen.
- Squash-flette PR #104 låst til head-en, og føre spesifikasjonen, `epics.md`, kvalitetssikringen, FR-401 og memloggen.
- Kjøre de fire kommandoene fra README-en, vise jobben og ta Prøve 4.

### Resultat
- Kvotesjekken kl. 11:36: 0 brukt 28.10 i GMT, 20 igjen.
- Main: instruksjonen i `683b145b`, og avgjørelsen kl. 11:34 i `ee82976e`, der BH6 ga ingen lås og ECH5 alltid den lokale modellen.
- Grenen: main flettet inn i `35028366`, og BH6 og ECH5 ført i `ad8ec4a4`. CI var grønn på head-en (40673689106).
- PR #104 er squash-flettet i `817b331a`, låst til `ad8ec4a`, og grenen er slettet på GitHub.
- Etter flettingen, i `a6b4e413`: spesifikasjonen done, en linje under 2.3d, radene i §3, §5 og vedlegget, en datert linje under FR-401 og beslutningen i `.memlog.md`.
- PC-en: arbeidskopien `..\G74-lund-osen-jobb`, `data` som Junction og `.env` som HardLink.
- Jobben «OSE Signal kveldshenting» går daglig fra 29.10 kl. 22:15 lokal tid og hver halvtime til 23:45. Den er satt opp med IgnoreNew og Interactive, og uten StartWhenAvailable. Neste kjøring er 29.10 kl. 22:15.
- Prøve 4, rad 5, kl. 11:42:31: jobben stoppet fordi commiten fra midnatt (`b17bda6`) ikke har skriptet. Siste resultat var 1, med 0 kall, og `apiRequests` var 16 før og etter. Nøkkelen står ikke i loggen. Utfallet er ført i §9 i `b9c06097`.

### Åpne punkter
- 2.3d: prøven med 0 kall fra selve hentingen tas 29.10 før kl. 22:00, eller leses i loggen etter første kjøring 29.10 kl. 22:15.
- 2.3d VG4, BH7, BH9/ECH8, BH15/VG7 og BH16 (low) står fortsatt under «Åpent» i spesifikasjonen.
