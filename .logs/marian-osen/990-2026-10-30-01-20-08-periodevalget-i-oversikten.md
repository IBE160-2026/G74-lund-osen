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
