# Ikonet og snarveien, del C (3.6)

## 2026-11-11 kl. 12:49 — Marian Osen

### Oppgave
Del C (limt inn 10.11 kl. 17:23): ikonet til appen laget av logoen i toppen, og snarveien «OSE Signal» på skrivebordet i Windows, som startskriptet tilbyr første gang. Demoen får sin egen, «OSE Signal (demo)», etter tillegget om demoen kl. 15:57. Arbeidet ble avbrutt kl. 04:29, da Windows Update startet maskinen på nytt, og gjort ferdig etter fortsettelsen kl. 11:52. Etter kl. 06:30 flettes ingenting før gruppen har sagt ja.

### Plan
- Story 3.6 i Epic 3, på grenen `3-6-ikonet-og-snarveien` i worktreen `G74-lund-osen-3-6` fra `059dc10c`. Spesifikasjonen er [spec-3-6-ikonet-og-snarveien.md](../../_bmad-output/implementation-artifacts/spec-3-6-ikonet-og-snarveien.md).
- Arbeidet i tre deler, ikonet, snarveien og dokumentene, hver med tester og en mutant. Så gjennomgangen, triagen, hele settet, PR-en og CI.

### Resultat
- **Natten, kl. 04:01–04:20:** commitene `7cd5d9fb` (storyen), `6b249318` (SVG på én linje, README-en og installasjonen etter testene) og `ec558aec` (funnene fra gjennomgangen). PR-en er #144.
  - `src/ikon.py` tegner ikonet med bare standardbiblioteket. Det ligger i `src/static` som SVG, PNG og ICO, og står i fanen på alle sidene.
  - `start/snarvei.ps1` blir kalt fra `start.ps1` når appen svarer. Et nei huskes i `data\snarvei-nei-<versjon>`.
- **Gjennomgangen:** Blind Hunter hadde 15 funn, Edge Case Hunter 12 og Verification Gap 9. Ingen var høye. De middels er rettet, bortsett fra spørsmål 8, som står åpent (regel 25). Triagen står i spesifikasjonen.
- **Mutantene:** én per del, alle fanget. Etter gjennomgangen ble seks kjørt, og fem fanget. Den som overlevde, `New-Item` utenfor `try`, er forklart i spesifikasjonen. Filene var like før og etter (sha256).
- **CI kl. 04:23:** pytest feilet i lenketesten i `tests/test_utseende.py`, fordi ikonlenkene ikke sto på lista over lovlige adresser. Kl. 04:29 startet Windows Update maskinen på nytt midt i rettingen (hendelse 1074).
- **Statusinstruksjonen** ble kjørt med samme tekst og samme resultat i to vinduer, kl. 10:29 (økt a0c93c71) og kl. 10:33 (økt 7227a2b2).
  - Begge var bare lesing og ga ingen commit.
  - Kveldsjobben 10.11 ble ferdig uten FEIL-linjer, og tillegg 3 og 5 til del B kom aldri fram.
  - Tillegget kl. 11:41 kom i feil vindu og stoppet ved steg 0.
  - Alt er ført i ettertid i `docs/ai-prompts/2026-11-11.md` (`ce33771c`), sammen med fortsettelsen kl. 11:52.
- **Fortsettelsen kl. 11:52:** steg 0 stemte. Kvotesjekken viste 0 kall brukt i dag (GMT), 20 igjen og `extraLimit` 296.
  - Rettingen er `0e354030`: lista i lenketesten har nå nøyaktig de tre ikonadressene, og bare når fila finnes, slik stilarket står der (2.7a).
  - Begrunnelsen og «Ville feilet hvis» står i spesifikasjonen. Mutanten med `/static/ikon-64.png` ble fanget.
- **Hele settet i deler, kl. 12:02–12:45:** 5159 bestått, 25 hoppet over og 0 feilet, til sammen 5184, likt `--collect-only`. Flere av delene ventet på pytest fra andre vinduer.
- **CI:** run 43014596449 er grønn på alle fire jobbene. Steget «Snarveien på Windows» kjørte 22 tester, og ingen ble hoppet over. PR #144 kan flettes (CLEAN), men er ikke flettet.
- **Grenser:** ingen API-kall utover kvotesjekken, og `data/db/ose.db` er ikke rørt. Ingen snarvei er laget på det ekte skrivebordet, fordi testene bruker en midlertidig mappe. Den ekte versjonen og Ollama er ikke startet.

### Åpne punkter
- PR #144 (3.6) er grønn og flettes først etter gruppens ja, i en egen instruksjon. Spørsmålene 1–7 i spesifikasjonen er bygget etter forslaget.
  1. Ikonet er søylene fra logoen på blekk.
  2. Ikonet står i fanen.
  3. Spørsmålet kommer etter at nettleseren er åpnet.
  4. Et nei huskes i `data\`.
  5. Demoen får «OSE Signal (demo)».
  6. Mac får ingen snarvei.
  7. Ikonet beskrives med ord i installasjonen.
- Spørsmål 8 (BH2 og ECH4, middels) står åpent til gruppen har svart. En snarvei til en annen kopi som finnes, blir stående. Forslaget er at snarveien bare rettes når mappa den peker på, er slettet.
- Del C, steg 2 og 3 gjenstår etter ja: flettingen, done-commiten (epics.md, sprint-status, kvalitetssikringen og mobil som plan for en senere versjon) og føringen av del C med Utført-linje i dagsfila 10.11.

## 2026-11-11 kl. 15:36 — Marian Osen

### Oppgave
Del C gjøres ferdig og flettes, etter gruppens svar kl. 13:47 og 13:49 (instruksjonen kl. 14:26). Spørsmål 8: startskriptet spør om snarveien skal starte denne kopien når den starter en annen. README-en får lista «Ekstra, ferdig», og brukertesten flyttes til setningen om det som er ferdig rundt appen. Så flettingen, done og føringen av del C i dagsfila 10.11.

### Plan
- Steg 0 og kvotesjekken, dagsfila 11.11 og svarene i spesifikasjonen.
- Spørsmål 8 og README-en på grenen i worktreen `G74-lund-osen-3-6`, med tester, mutant, gjennomgang og triage.
- Main inn, hele settet i deler, push og CI. Så squash-flett låst til head-en, og føringen på main.

### Resultat
- **Fortsettelsen av 10.10 kl. 14:18** ble limt inn i dette vinduet ved en feil. Den stoppet ved steg 0, og ingenting ble gjort. Etterpå ble slutten av svaret limt inn igjen uten instruksjon. Begge er ført i dagsfila 11.11 (`c6ec09ea`), sammen med instruksjonen kl. 14:26.
- **Kvotesjekken:** 0 kall brukt i dag (GMT), 20 igjen, `extraLimit` 296.
- **Svarene i spesifikasjonen:** `2a28a86f`.
- **Spørsmål 8 (`d4dd5382`):**
  - Starter snarveien samme startfil i en annen kopi som finnes, sier vinduet mappa og spør én gang. Det gjelder begge snarveiene.
  - Ja retter snarveien hit, og nei huskes.
  - Installasjonen har én setning om det.
  - Mutanten ble fanget av fire tester.
- **README-en (`7153b37a`):** «Ekstra, ferdig» har målingen av omsetningen, notatene og ikonet med snarveien. Brukertesten står i setningen rundt appen.
- **Gjennomgangen kl. 14:36–14:55:** Blind Hunter hadde 7 funn, Edge Case Hunter 5 og Verification Gap 4. Ingen var høye.
  - Rettet i `f8eaec8f`:
    - ECH1/BH1 (middels): neiet til å flytte har sin egen fil, `snarvei-nei-flytt-<versjon>`.
    - VG1 (middels): spørsmålet prøves.
    - ECH3/BH2: bare samme startfil er en annen kopi, og argumentene nullstilles.
    - VG2 og BH5.
    - ECH5/BH7: regelsetningen gjelder «Ekstra, hvis tiden rekker».
  - Mutantene for ECH1 og VG1 ble fanget.
  - Triagen står i spesifikasjonen (`b489c4d5`).
- **Main inn og testene:** main ble flettet inn (`11998215`). Hele settet i åtte deler, én om gangen bare når ingen annen pytest kjørte: 5166 bestått, 25 hoppet over og 0 feilet, til sammen 5191, likt `--collect-only`.
- **CI:** grønn på head-en (run 43036831538). Jobben `pytest` hadde 5143 bestått og 48 hoppet over, og «Snarveien på Windows» kjørte 29 tester uten at noen ble hoppet over.
- **Flettingen:** flettet med PR #144 som `078c7c28` kl. 15:21, låst til head-en. Grenen er slettet, worktreen fjernet, og treet på main er likt head-en. CI er grønn på flettecommiten (run 43037656742).
- **Done (`be287801`):** spesifikasjonen, storyen med svarene og mobil som plan i epics.md, sprint-status og radene i kvalitetssikringen. Dokumenttestene ga 2400 bestått og 7 hoppet over.
- **Dagsfila 10.11:** del C er ført med Utført-linja (`c3e34f1d`).
- **Grenser:** ingen API-kall utover kvotesjekken. `data/db/ose.db` er ikke rørt, ingen snarvei er laget på det ekte skrivebordet, og andre grener er ikke rørt.

### Åpne punkter
Ingen. De tre punktene for 3.6 i `issues.md` er lukket.
