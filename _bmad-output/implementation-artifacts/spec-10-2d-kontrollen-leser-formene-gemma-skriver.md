---
title: 'Story 10.2 (10.2d): kontrollen i FR-603 leser formene Gemma skriver'
type: 'feature'
created: '2026-10-18'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '52d5107'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4b-ki-tekstene-i-demoen.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Kontrollen i FR-603 (`src/ki_kontroll.py`) leser retningen bare der teksten sier «retningen er X» eller «X retning». Gemma skriver retningen som «Dette signalet er Negativt» eller «av typen Ingen», og styrken som «av styrke tre». En feil retning eller styrke i de formene slipper gjennom. Hullet ble funnet med mutant K2 i 3.4b og står som åpent punkt i `spec-3-4b-ki-tekstene-i-demoen.md`.

**Grunnlaget:** gruppens svar 18.10 kl. 21:03: hullet rettes før byggestoppen mandag 19.10 kl. 20:40, så uka med logget drift går med den rettede kontrollen. Instruksjonen 18.10 kl. 22:18. Prompten står, versjon 2.

## Kontrollpunktene

- a) Hullet, uten å endre koden: en test med de 13 tekstene i `src/demo_ki_tekster.json`, der retningen i første setning er byttet til en feil retning. Den skal stoppe hver av dem. På main slipper 12 gjennom, så testen er merket `xfail` med `strict=True` og grunnen, til punkt b.
- b) Kontrollen: retningen leses også der teksten sier den om hele signalet: «signalet er X», også med «av typen», med fyllordene og bøyd (positivt, negativt), «retningen på signalet er X», og «et X signal» når det gjelder hele signalet. Styrken leses også i «av styrke N». Det som gjelder én sjekk, som «Trendens retning er positiv» og «Trenden ga et positivt utslag» eller «signal», sjekkes fortsatt ikke. Docstringen i `src/ki_kontroll.py` sier det. `xfail` fra a tas bort i samme commit.
- c) Testene, med «Ville feilet hvis»: hver form i b stoppes med feil retning eller styrke og slipper gjennom med riktig; formene om én sjekk stoppes ikke; de 13 tekstene i demoen består som de er, så de lages ikke på nytt. Den nye kontrollen kjøres også på KI-tekstene som står i sporede filer, som `malinger.md` ved PRD-en, og hver tekst som får et annet svar enn før, står her med grunnen. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: mønsteret for «signalet er» tatt bort, «av typen» tatt bort, «av styrke N» tatt bort, og et mønster som også leser «Trenden ga et positivt utslag».

## Planen, én commit per punkt

1. a) Testen for hullet, merket `xfail(strict=True)`.
2. b) Mønstrene i `ki_kontroll.py`, docstringen, og `xfail` tatt bort.
3. c) Testene for hver form og for formene om én sjekk, og kjøringen på tekstene i sporede filer.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22), og ingen test kaller Ollama.
- Prompten står, versjon 2. Tekstene i demoen lages ikke på nytt.

## Avgjort underveis

- **Testen i a** bytter den første retningen teksten sier, med stor forbokstav som Gemma skriver den. For LKSV sier første setning styrken («av styrke tre»), og retningen står først i andre setning («Retningen er Blandet»). Den byttes der, og det er den ene av de 13 som ble stoppet på main (gjennomgangen, VG5). Første versjon av testen (`6eab5f1`) hadde backspace i stedet for `\b` i mønsteret, så hjelpefunksjonen feilet på hver tekst og `xfail` godtok det. Rettet i `aae2eef`: hjelpefunksjonen kaster `ValueError`, og `xfail` krever `AssertionError`.
- **«Signalet er ingen»** leses bare som retningen Ingen med «av typen» foran eller et skilletegn eller «fordi» etter, så «Signalet er ingen garanti» ikke er en retning.
- **«et X signal»** leses bare med signalet som subjekt, eller med «Dette er» eller «Det er» først i teksten. Andre steder viser «det er et positivt signal» ofte til én sjekk (gjennomgangen, BH1 og ECH1).
- **Én sjekk** kjennes på ordene trend, bevegelse, interesse, sjekk, kurs, volum og utslag i de tre ordene foran, på bindestrek foran «signalet», og på «for» eller «på» en sjekk rett etter retningen. Da leses ikke utsagnet. Det samme gjelder «av styrke N».

## Tekstene i sporede filer

Kontrollen fra main og den nye ble kjørt på alle KI-tekstene som står ordrett i sporede filer, med et skript utenfor repoet som lastet `ki_kontroll.py` fra main ved siden av den nye. Tekstene er:
- de 66 i §19 i `malinger.md`, «Tekstene, ordrett». Det er seks kjøringer med A–E med og uten målinger, og grunnlaget er tatt fra «Eksemplene» (A Positiv 3, B Negativ 2, C Blandet 3, D Ingen 0, E Negativ 1). De seks «Dag»-tekstene handler om dagen, ikke en aksje, og ble kjørt med Ingen 0;
- de 13 i `src/demo_ki_tekster.json`.

§32 og §34 sier at tekstene står bare i kopien av basen. `git grep` etter «signalet er», «retningen er» og «ga et positivt/negativt utslag» fant ellers bare beskrivelser av kontrollen og testtekster (gjennomgangen, VG4).

**Ingen av de 79 tekstene fikk et annet svar eller andre grunner** med den nye kontrollen etter rettingene på `94fcdd8`. På `6dcd18f` ble de 73 uten «Dag»-tekstene kjørt, også med samme svar for alle. Tekstene i demoen lages ikke på nytt.

## Mutantene

Én om gangen med `-x` på `tests/test_ki_modell.py`, i en fersk klon med `core.autocrlf=false`, med kopi av `src/ki_kontroll.py` før og sha256 mot HEAD etter hver, og `git status` tom etter hver. D1–D4 er fra instruksjonen og ble fanget på `6dcd18f`, og på nytt på `94fcdd8`. D5–D12 er for funnene med dom high og medium, fanget på `94fcdd8`:
- D1, mønsteret for «signalet er» tatt bort: `test_feil_retning_i_demotekstene_stoppes`.
- D2, «av typen» tatt bort: `test_feil_retning_i_demotekstene_stoppes` (SLVP).
- D3, «av styrke N» tatt bort: `test_feil_styrke_i_av_styrke_stoppes`.
- D4, et mønster som også leser «Trenden ga et positivt utslag»: `test_demotekstene_bestaar_som_de_er`.
- D5, «det er et X signal» hvor som helst (BH1): `test_formene_om_en_sjekk_stoppes_ikke`.
- D6, en sjekk foran «signalet» stopper ikke lesingen (ECH2): `test_formene_om_en_sjekk_stoppes_ikke`.
- D7, «positivt for trenden» leses (BH6): `test_formene_om_en_sjekk_stoppes_ikke`.
- D8, anførselstegn og fet skrift leses ikke (BH5): `test_feil_retning_i_formene_stoppes`.
- D9, omvendt ordstilling tatt bort (BH2): `test_feil_retning_i_formene_stoppes`.
- D10, «Signalet for MOWI» og «Dagens signal» tatt bort (BH3): `test_feil_retning_i_formene_stoppes`.
- D11, bare de fire fyllordene fra før (BH4): `test_feil_retning_i_formene_stoppes`.
- D12, «av styrke N» om én sjekk leses (ECH8): `test_av_styrke_om_en_sjekk_stoppes_ikke`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `d031e4e..6dcd18f`. Linsene var Blind Hunter (BH, 13 funn, bare diffen), Edge Case Hunter (ECH, 11, prøvde rundt 160 tekster) og Verification Gap (VG, 8). Ingen av dem kjørte hele testsettet eller kalte Ollama. Ett funn har dom high, og ni rader har dom medium. Alle er rettet i `94fcdd8`, unntatt VG1, som er rettet her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | «…, og det er et positivt signal» etter en sjekk ble lest som hele signalet | high | patch: «Dette er» / «Det er» bare først i teksten. D5 |
| BH6, ECH3 | «Signalet er positivt for trenden, men negativt for …» ble stoppet ved Blandet | medium | patch: «for» eller «på» en sjekk etter retningen. D7 |
| ECH2, BH7, VG7 | «Trendens bidrag til signalet er positivt», «Trend-signalet» og «MA50-signalet» ble stoppet | medium | patch: en sjekk i de tre ordene foran, og bindestrek. D6 |
| BH2 | «Samlet er signalet Positivt» og «Derfor er retningen positiv» slapp gjennom | medium | patch: omvendt ordstilling. D9 |
| BH3 | «Signalet for MOWI er», «Signalet i dag er» og «Dagens signal er» slapp gjennom | medium | patch. D10 |
| BH4, ECH5, VG8 | «samlet sett», «klart», «i dag», «et sterkt positivt signal» slapp gjennom | medium | patch: opptil to fyll- og gradsord. D11. «av type», «har retningen» og «et signal av typen» er avvist: ingen av de 79 tekstene bruker dem, og uka med logget drift viser om Gemma gjør det |
| BH5, ECH5 | «**Positivt**», «Ingen» i anførselstegn og «Signalet er: Negativt» slapp gjennom | medium | patch. D8 |
| ECH8 | «Hver sjekk er av styrke én» ble lest som styrken | low–medium | patch: en sjekk eller et utslag foran. D12 |
| BH10 | Testen med demotekstene sjekket ikke grunnen | medium | patch: krever «1: retningen» |
| VG1 | Mutantene var ikke dokumentert | medium | patch: over |
| ECH4, VG6 | «Retningen på signalet er X» ga to like grunner, og utvidelsen i mønster 1 ble ikke prøvd | low | patch: utvidelsen er tatt bort, «signalet er» leser formen, og en test krever én grunn |
| BH8, ECH7 | «ingen» foran tankestrek, parentes eller linjeskift leses ikke | low | avvist: regelen er streng med vilje, så «ingen» som vanlig ord ikke stopper en riktig tekst. «Retningen på signalet er ingen garanti» stoppes ikke lenger |
| BH9, ECH9 | Ordet etter «styrke» som ikke er et tall, og «av styrken tre» | low | avvist: et ord som ikke er et tall, gir ingen grunn, og «styrke på to» leses av mønsteret fra før |
| BH11 | Ingen tester for de falske stoppene og hullene | low | patch: testene over |
| BH12 | Docstringen var upresis | low | patch: den sier formene, «Det er» først i teksten og hvordan én sjekk kjennes |
| BH13 | «nøytral» leses ikke | low | avvist: det er ikke en av de fire retningene i regelen, og prompten bruker dem |
| ECH6 | «blandede» og «blanda» leses ikke | low | avvist: Gemma skriver retningen slik regelen gjør, med stor forbokstav |
| ECH10 | «Signalet var negativt i går» stoppes | low | avvist: prompten har ingen historikk |
| ECH11 | Andre kallere | low | ingen endring: de 13 i demoen gir samme svar, og `sjekk_radene` kaller ikke kontrollen |
| VG2 | Resultatet for tekstene sto ikke i spesifikasjonen | low | patch: «Tekstene i sporede filer» |
| VG3 | §19 har 66 tekster, ikke 60 | low | patch: alle 66 er kjørt, også «Dag» |
| VG4 | Søket etter sporede filer var ikke nevnt | low | patch: over |
| VG5 | LKSV byttes i andre setning | low | patch: forklart under «Avgjort underveis» |

*Lagt til 2026-10-18 kl. 22:49:* PR #71 er squash-flettet i `3c2bd51`, låst til head-en `0bdd259`. Main hadde ikke gått videre. CI var grønn på head-en (39164796411) og på main (39164925044). Triagen står over og som kommentar på PR-en. Kontrollen er flettet før byggestoppen mandag 19.10 kl. 20:40.
