# Rettingene før brukertest 2 (9.18)

## 2026-11-17 kl. 16:05 — Marian Osen

### Oppgave
Instruksjonen om rettingene før brukertest 2 (limt inn kl. 14:15), med beskjeden kl. 14:16. Gruppen svarte 17.11 kl. 13:03–13:33 på spørsmålene i 9.17 og fant fem ting selv (HE14–HE18). Dette rettes i én story før brukertest 2: HE2, HE3, HE5, HE8, HE9, HE10 og HE14–HE18, hver med en test. Testen er tidligst fredag 20.11. PR-en må være flettet før torsdag 19.11 kl. 20:00.

### Plan
- Gjøre ferdig føringen av 9.17 og pushe main (kl. 14:22), og så story 9.18 på en gren fra `origin/main` (`e29f3020`), med spesifikasjonen som første commit (`bb8488dc`).
- Én agent som bare leser, kartla koden. Én agent bygde rettingene i worktreen, med én commit per retting og en test som feilet før. Vinduet kontrollerte commitene, at ingen migrasjon og ingen bilder var med, og bildene fra demoen. Dokumentene, PRD-en og loggene skrev vinduet selv.
- Gjennomgangen tas med én leser og tre linser, og så triage, `--dokumentene`, CI og fletting.

### Resultat
- **Rettingene:** HE14 `773c78ab`, HE2 `3d2599cf`, HE3 `fde463cd` og `8ffd671f`, HE16 `46082e05`, HE18 `32a69e6f`, HE17 `73cb94c4`, HE5 `a1720f3a`, HE8 `a2a28bdc`, HE9 `a88aa68d` og HE10 `4f01c344`. Avtrykkene står i `261e1e2a` og `bc68e0d3`.
- **HE15:** ingen kodeendring. `Valglager.folg` setter stjernen fra 8.26 (11.11), og `test_foelg_gir_stjerne_og_rad_i_min_liste` låser det. Beskrivelsen er rettet i evalueringen og UX-loggen (`d08ed981`).
- **HE8:** målingen er ikke lagret i basen eller i KI-grunnlaget, så bare visningen er endret. FR-706 og FR-101 er rettet, med en linje i endringsloggen (`5586b394`).
- **Dokumentene:** evalueringen, UX-loggen (U131 for HE18) og spørsmålet om HE1 etter oppgave G i brukertest 2 (`ddeef476`). Spesifikasjonen er i `acc52a83` og `6ab838d8`.
- **Gjennomgangen:** 18 funn, 3 på middels. ECH1 og VG2 er rettet (`3e225584` og `d08ed981`), og BH1–BH5, ECH2 og VG3 også (`9b186fa8` og `5fa19b16`). **VG1 (middels) står åpent:** bildene i `docs/appen/` er ikke tatt på nytt, fordi instruksjonen sier at bildene blir i scratchpad.
- **Demoen:** sjekket på port 62971 i 1280 og 390 px og stoppet etterpå. Bildene ligger i scratchpad.
- **Testene:** testfilene storyen rører, kjørt én om gangen, og `--dokumentene` på grenen kl. 15:44–16:03, med 2996 bestått og 20 hoppet over. 13 av dem hoppet over fordi gruppens app er på port 8000. Kjøringen kl. 15:39 ble stoppet for lite minne og startet igjen. PR #165 er åpnet, og CI kjører.
- Ingen ny migrasjon og ingen API-kall. `data/` og `_privat/` er ikke rørt, og den ekte versjonen er ikke startet av vinduet. Worktreene for 9.16–9.18 står.

### Åpne punkter
- VG1, spørsmål 2 i 9.18 (middels, følger av instruksjonen): skal bildene i `docs/appen/` tas på nytt i 9.18 eller i en egen story etter brukertest 2? PR #165 flettes ikke før gruppen har svart, og må være flettet før torsdag 19.11 kl. 20:00.
- Spørsmål 1 i 9.18 (HE15): aksjer fulgt før 11.11 eller tatt inn med en ferdig liste har ingen stjerne. Forslaget er at gruppen setter stjernen selv før testen, og at ferdige lister og Fjern tas etter testen.
- Spørsmål 3 og 4 i 9.18 (lave): setningen om tenkte kjøp i stegene for notatene, og linja mellom 640 og 760 px.
- Føringen av 9.18 på main kommer etter flettingen.

## 2026-11-17 kl. 17:23 — Marian Osen

### Oppgave
Beskjeden kl. 16:21 med gruppens svar kl. 16:19 på spørsmål 1 og 2 i 9.18, og resten av instruksjonen: push, fletting, føring, Utført-linja og loggen.

### Plan
- Føre svarene i 9.18, kjøre `--dokumentene`, pushe, flette når CI er grønn, og føre på main.

### Resultat
- **HE15:** lukket som alt bygget. Gruppen setter stjernen selv på de tre egne aksjene i den ekte versjonen (`84187858`).
- **VG1:** besvart. Bildene i `docs/appen/` tas på nytt i en egen liten story rett etter 9.18, før rubrikk-passet, med egen instruksjon. Graden står (`358aa863`).
- **Testene:** `--dokumentene` på grenen ga 3009 bestått og 7 hoppet over kl. 16:53–17:14, etter én omstart for lite minne. CI var grønn (run 44123485449).
- **Flettingen:** PR #165 ble squash-flettet i `9bf8769e` kl. 17:20. Føringen står i `36464e3f` og `aeb7b958`, og tallet på funn i gjennomgangen er rettet fra 18 til 16. Utført-linja står i `3ba1c22a`, og ble skrevet før denne loggseksjonen, ikke etter.
- **Avvik:** kl. 16:23 ble main pushet etter en kjøring av `--dokumentene` med «1 error» (exit 1), fordi kommandoen ikke sjekket utfallet før push. Commitene var bare dagsfila, loggen og Utført-linja. Ny kjøring kl. 16:23–16:42 ga 2970 bestått og 7 hoppet over. Hvilken test som ga feilen, er ikke kjent, fordi utskriften bare viste antallet. Fra nå sjekkes utfallet i samme kommando som push.

### Åpne punkter
- Storyen som tar bildene i `docs/appen/` på nytt, med egen instruksjon (VG1).
- Spørsmål 3 og 4 i 9.18 (lave) står.
