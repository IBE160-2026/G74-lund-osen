# Periodevalget i oversikten

## 2026-10-30 kl. 01:20 — Marian Osen

### Oppgave
Bygge 8.17a, periodevalget i oversikten med søylene og indekslinja, på egen gren med spesifikasjon, PR og én commit per punkt, og stoppe før flettingen (instruksjonen 30.10 kl. 00:10, med gruppens svar 29.10 kl. 09:20).

### Plan
- Instruksjonen og svaret i dagsfila 30.10, og svaret kl. 09:20 under story 8.17 i `epics.md`.
- Spesifikasjonen `_bmad-output/implementation-artifacts/spec-8-17a-periodevalget-i-oversikten.md` på grenen `8-17a-periodevalget-i-oversikten`, PR #106 som utkast.
- a) periodevalget og radene, b) søylene, linja, hjelpen og README-en, c) testene og mutantene.
- Hele settet alene, gjennomgang med Blind Hunter, Edge Case Hunter og Verification Gap, triagen, CI og bildene i PR-en.

### Resultat
- Main: `61b31641` (instruksjonen) og `afd08c5f` (svaret kl. 09:20 og at byggingen startet 30.10 etter midnatt). Kvoten kl. 00:10: 20 brukt 29.10 i GMT, `extraLimit` 463. Ingen andre kall.
- Grenen: `a46f0187` (spesifikasjonen), `8bd801fe` (a), `635205ec` (b), `4e40a33e` (c), `d355ceec` (rettingene fra gjennomgangen og triagen). README-bildet av oversikten er tatt på nytt med høyden 1690, og bildet av aksjesiden er byte for byte det samme.
- Hele settet før gjennomgangen (00:52:47–00:59:57): 3885 bestått, 24 hoppet over, 3 feilet. Etter rettingene (01:10:19–01:17:19): 3888 bestått, 24 hoppet over, 6 feilet. Alle feilene er i porttestene for `start.ps1`, som CI avgjør. Ledig minne 7188 og 7052 MB av 16124 MB.
- Mutantene M1–M3 ble fanget før og etter rettingene (00:52, 01:10), og filene var like etterpå.
- Gjennomgangen: 33 funn i 25 rader. Rettet blant annet én startdag for alle radene, ingen linje når indeksen er kortere, «Velg dag» på siste børsdag og «fra» bare for en kortere serie. BH1 ble avvist etter oppslag. 390 px er prøvd for hånd i Edge (iframe på 390 px, `scrollWidth` 390).
- CI grønn: 40976917255 på `4e40a33e` og 40978782787 på `d355ceec`. Triagen og bildene (grenen `pr-8-17a-bilder`, `c9336999`) står som kommentarer i PR #106, som fortsatt er utkast.

### Åpne punkter
- 8.17a ECH1: utenfor børskalenderen (før 2026) kan startdagen være en stengt dag, og linja over tabellen nevner den. Skal kalenderen dekke 2025?
- 8.17a VG5: søylene bruker indeksens siste dato, tabellen sidens. Skal søylene følge tabellens dag ved en periode?
- 8.17a VG1: 390 px er prøvd for hånd, ikke i en test.
- PR #106 flettes tidligst fredag, etter svarene over. Spesifikasjonen står som `in-progress` og settes til `done` ved flettingen.

## 2026-10-30 kl. 12:03 — Marian Osen

### Oppgave
Kontroll av jobben og CI, og så 8.17a videre etter gruppens svar 30.10 kl. 10:45 (ECH1, VG5, VG1, og tellingen i §5 for 2.13), før gruppen er borte fra kl. 12:00 til mandag kveld. Stopp før flettingen (instruksjonen 30.10 kl. 10:55).

### Plan
- Instruksjonen i dagsfila og svaret under story 8.17 og 2.13 i `epics.md` på main.
- Lesing av oppgaven, loggen 29.10, kvoten, powercfg, Windows Update og CI-feilen på `2eb10f1`.
- På grenen i worktreen `..\G74-lund-osen-8-17a`: flett main inn, a, b og c med tester, mutanten M4, linjene i spesifikasjonen.
- Hele settet alene, gjennomgang med Blind Hunter, Edge Case Hunter og Verification Gap, triagen, CI.

### Resultat
- Kvoten kl. 10:54 (09:54 GMT): `apiRequestsDate` 29.10, så 0 brukt og 20 igjen, `extraLimit` 463. Ingen andre kall.
- Main: `16861d2b` (instruksjonen), `0d7f3ec9` (svaret kl. 10:45 under 8.17 og 2.13). CI grønn på begge (41037014034, 41037153786).
- Steg 2: jobben Ready, siste kjøring 29.10 kl. 23:45:00 med resultat 0, neste 30.10 kl. 22:15. Loggen 29.10 har fire kjøringer (22:15–22:16, 22:45, 23:15, 23:45), Docker Desktop og Ollama startet og stoppet hver gang, KI-tekstene fra den lokale modellen, ingen feillinjer. Hvilemodus i strøm: aldri. Windows Update: ikke på pause. CI-feilen på `2eb10f1` (#1563): testen uten Docker på windows-latest fant runnerens docker, fordi den falske docker (`441b922c`) bare lå på grenen for 2.13 til `676fbc8`.
- Grenen: `524adcf1` (main inn), `16c68b1d` (a), `3aa2d80d` (b), `9c8bda28` (c), `07378532` (spesifikasjonen og M4), `c4cc3cd6` (avtrykkene bak bildene), `f583503a` (rettingene fra gjennomgangen og triagen).
- Commitene a og b ble laget mens tre tester i `tests/test_docker.py` feilet (avtrykkene bak README-bildene), fordi den fila ikke ble kjørt før de commitene. Funnet i hele settet etter c, rettet i `c4cc3cd6`. Bildene er byte for byte de samme.
- Hele settet: 11:19:41–11:29:11 (10 feilet: de 7 porttestene og de 3 for avtrykkene), 11:31:26–11:40:22 (3897 bestått, 24 hoppet over, 7 feilet) og 11:49:31–11:58:43 (3898 bestått, 24 hoppet over, 7 feilet). Bare porttestene for `start.ps1`.
- M4 (søylene ved indeksens dag) fanget av `test_indeksen_en_dag_foran_tabellen` 11:17:35–11:17:42 og 11:59:05–11:59:14, fila lik kopien og HEAD.
- Gjennomgangen: BH 14, ECH 6, VG 1. Rettet BH3/ECH1, BH7, BH11, BH12, BH14/VG1 og ECH3. Triagen i spesifikasjonen og i PR #106.
- CI: 41042643003 feilet på `c4cc3cd6` i «Start demoen på Windows» etter at demoen svarte 200 (prosessen kunne ikke avsluttes). 41044941912 grønn på `f583503a`.

### Åpne punkter
- 8.17a BH1/ECH2: indekstallet over søylene gjelder indeksens siste dato, linja tabellens dag. Spørsmål til gruppen.
- 8.17a VG5: FR-105 i `prd.md` sier indeksens dato. Skal den få en Rettet-linje?
- CI på windows-latest: «Start demoen på Windows» feilet i opprydningen på `c4cc3cd6` (41042643003), og to porttester fikk timeout på `61b3164` (40971615322). Begge gikk igjen uten endring.
- PR #106 flettes mandag kveld. Spesifikasjonen settes til `done` da.
