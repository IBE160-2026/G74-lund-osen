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
