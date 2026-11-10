# Målingen av alle aksjene i natt (2.13b)

## 2026-11-11 kl. 00:32 — Marian Osen

### Oppgave
Instruksjonen kl. 16:20 10.11 i vindu 2, etter gruppens svar kl. 13:48. Aksjene i børslista uten måling av omsetningen skulle måles én gang i natt med bonuskvoten, og minst 200 kall skulle stå igjen i den. Det ble bygget som story 2.13b, flettet før kl. 22:00 og kjørt én gang etter notatene. Spørsmålene ble besvart kl. 16:31 og 17:42. Tilleggene kom kl. 16:26 (bransjeforslaget), kl. 16:28 (rekkefølgen og testene i natt) og kl. 23:14 (ventingen).

### Plan
- 2.13b fra `53ff012c` på grenen `2-13b-maal-alle` i worktreen `G74-lund-osen-2-13b`. Spesifikasjonen er [spec-2-13b-maal-alle-med-bonuskvoten.md](../../_bmad-output/implementation-artifacts/spec-2-13b-maal-alle-med-bonuskvoten.md).
- Valget `--med-bonuskvoten` til `--maal-omsetning`. Det tester med en falsk henter og en falsk kvote, har én mutant per del, går gjennom Blind Hunter, Edge Case Hunter og Verification Gap, og så triage, ruff, hele settet, PR og CI.
- Flettingen etter Utført-linja for de fem storyene (kl. 20:48) og før kl. 22:00. Kjøringen etter notatenes Utført-linje eller kl. 00:05, og ikke etter kl. 00:40.
- Ventingen leser dagsfila med `gh api`, ikke git, så den ikke bruker git i stilletidene. Den startes på nytt hvis den blir stoppet (tillegget kl. 23:14).

### Resultat
- **Kvotesjekken kl. 16:26:** 0 brukt 10.11 i GMT, 20 igjen og 463 i `extraLimit`.
- **Grenen:** `b50eeda9`, `97f0fdc4`, `36bca8cf`, `1f7084b0`, `39c89ebf`, `07decefd` og `2d01504f`. Main ble flettet inn i `7964277e` og `7d61de0e`. PR #137 ble squash-flettet i `178107d9` kl. 21:10:39, låst til `7d61de0e`, med CI grønn (42891875216). Grenen og worktreen er borte, og treet på main er likt head-en. Done-commiten er `86d1fe4f`, med CI grønn.
- **Gjennomgangen:** 18 funn, 12 rettet og 6 ført. ECH1 (høy, etter midnatt) og ECH2 og ECH3 (middels) ble lukket med gruppens svar kl. 17:42, med graden urørt (regel 25).
- **Mutantene:** A–D ble fanget. Av mutantene for rettingene ble ECH1, ECH2 og BH1 fanget med en gang. BH3 overlevde først og ble fanget etter en ny test.
- **Hele settet:** på `39c89ebf` 4872 bestått og 24 hoppet over (4896). På `7d61de0e` 4946 bestått og 24 hoppet over (4970). 0 feilet begge gangene.
- **Dokumenttestene før `86d1fe4f`:** den første kjøringen ble stoppet av tidsgrensen på 10 minutter ved 96 %. Delt i to besto de: 925 bestått, og 1306 bestått og 7 hoppet over (2238).
- **Kjøringen 11.11 kl. 00:05:57–00:11:49**, fra repo-mappa på main (`63fe5fca`). Kopien før er `data/db/ose-foer-maalingen-2026-11-10.db`. 167 aksjer ble målt, med 0 kall av dagens og 167 fra bonuskvoten. 296 står igjen i bonuskvoten. Koden ble 0, og ingen kall feilet. 280 av de 297 aksjene i børslista har nå en måling. De 17 uten måling er i appens liste, som nå har 18 aksjer.
- **Dagsfila:** instruksjonene, svarene og tilleggene står ordrett i `docs/ai-prompts/2026-11-10.md` (`9553c7b8`).

### Åpne punkter
- `apiRequests` sto på 20 av 20 også etter 167 kall fra bonuskvoten. Bare `extraLimit` sank, fra 463 til 296. Kontrollen etter hvert kall bruker `extraLimit` med valget, så den holdt. §7.1 og §11 i `malinger.md` sier ikke om `apiRequests` stopper på grensen.
