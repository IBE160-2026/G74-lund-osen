# Brukerreiser og heuristisk evaluering (9.16 og 9.17)

## 2026-11-17 kl. 14:03 — Marian Osen

### Oppgave
Instruksjonen etter gruppens svar 16.11 kl. 20:22 (limt inn 16.11 kl. 21:53, og på nytt kl. 22:16, ordrett lik): design og UX før brukertest 2. Steg 1 er flere brukerreiser i §1 i PRD-en, i én story. Steg 2 er en heuristisk evaluering av demoen mot de ti heuristikkene til Nielsen, i en annen story. Begge er skrevet 17.11, etter at appen ble bygget. Underveis kom beskjedene fra rådet kl. 12:32, 12:41 og 13:19, med gruppens svar på spørsmålene (13:19 ble limt inn to ganger, ordrett lik).

### Plan
- Instruksjonen kl. 21:50 ble gjort ferdig først, med flettingen av #162 og ryddingen (se [916](916-2026-11-16-17-16-49-story-9-15-meldingene-og-ryddingen.md)).
- 9.16 og 9.17 på hver sin gren fra `origin/main` (`ba866204`), med spesifikasjonen som første commit.
- To agenter med bare lesing, startet samtidig. Den ene sjekket stegene i reisene mot malene og testene. Den andre gikk gjennom demoen fra en midlertidig mappe på port 62957 og stoppet den etterpå. Vinduet slo opp påstandene igjen før de ble skrevet inn.
- Én gjennomgang per story, med tre linser i én leser, og så triage, `--dokumentene`, CI og fletting.

### Resultat
- **9.16, PR #163, flettet i `7d4a331c` kl. 13:14:**
  - UJ-2 (Min liste med notater) og UJ-3 (KI-teksten av og på) står i §1 i PRD-en. Etter svarene kl. 12:32 og 12:39 måles de med SM-10 og SM-11 i §7, og de to målene har oppgave G og et ekstra spørsmål i oppgave B under «Brukertest 2» i `docs/brukertest.md`. Linjene står i endringsloggen.
  - Gjennomgangen ga 24 funn, 6 på middels. BH1 ble besvart kl. 12:32, og 17 funn er rettet. To nye tester er lagt til: sjekkortene er like med KI av og på (feilet mot en mutant), og formen på UJ-1–UJ-3.
  - CI var grønn (run 44080174325, 5876 bestått og 99 hoppet over). Føringen står i `5f45ac45` og `70857ea4`.
- **9.17, PR #164, flettet i `fc70bdf3` kl. 14:01:**
  - `docs/heuristisk-evaluering.md` har 13 funn fra evalueringen, HE1–HE3 på middels, og HE14–HE17 fra gruppen som evaluerer nr. 2. De nye står som U114–U130 i UX-loggen, og idéen kl. 13:08 står som idé. README-en lenker til dokumentet, og avtrykket for «Dokumentene» er satt på nytt. Ingen kode er endret.
  - Gjennomgangen ga 19 funn, ECH1 og VG1 på middels, og 17 er rettet. CI var grønn (run 44087764478). Føringen står i `86932ed5` og `8d8c740a`.
- **Testene:** `--dokumentene` ble stoppet for lite minne to ganger, kl. 11:54 på 9.16 og kl. 13:15 på main, og startet igjen etter svaret 14.11 kl. 05:18. Fra kl. 12:42 hoppet 13 tester i `tests/test_dobbeltklikk.py` over, fordi gruppens app kjørte på port 8000. Det er sett med `-rs`, og appen er ikke rørt.
- Ingen API-kall er gjort utover kvotesjekken kl. 10:41. Den ekte versjonen er ikke startet av vinduet, og `data/` og `_privat/` er ikke lest. Ingenting er slettet: worktreene og grenene for 9.16 og 9.17 står.

### Åpne punkter
- Rettingene før brukertest 2 i en egen story med egen instruksjon: HE2, HE3, HE5, HE8, HE9 og HE10 fra evalueringen, og gruppens HE14, HE15, fast bredde i HE16, og HE17.
- HE15 og koden: gruppen så at notatene på en aksje uten stjerne ikke synes i Min liste, men på main viser «Mine notater» i Min liste alle notatene. Det er spørsmål 4 i 9.17.
- Brukertest 2: oppgave G (SM-10) og det ekstra spørsmålet i oppgave B (SM-11), og HE1 som et spørsmål. Gruppen skriver notatene i den ekte versjonen 17.11.
- Bildene av demoen og skriptene ligger i scratchpad, og ingenting er slettet.
