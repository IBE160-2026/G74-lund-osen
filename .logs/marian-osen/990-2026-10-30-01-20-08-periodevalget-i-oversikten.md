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

## 2026-10-30 kl. 13:55 — Marian Osen

### Oppgave
8.17a siste rettinger etter gruppens svar 30.10 kl. 12:21 (e: hele delen med hovedindeksen følger tabellens dag, f: én dag per side og en Rettet-linje under FR-105), på grenen, og stopp før flettingen mandag (instruksjonen kl. 12:21, kjørt etter svaret kl. 13:09).

### Plan
- Instruksjonen og svarene kl. 12:24 og 13:09 i dagsfila, og svaret kl. 12:21 under story 8.17 på main.
- Flett main inn (med 3.5h), e og f med tester, oppslaget for f, mutanten M5 og linjene i spesifikasjonen.
- Hele settet før hver commit som endrer src/ eller tests/, gjennomgang med Blind Hunter, Edge Case Hunter og Verification Gap, triagen og CI.

### Resultat
- Main: `1c603d29` og `7f1430b5` (instruksjonen og svarene), `e51b229f` (svaret kl. 12:21 under 8.17).
- Grenen: `4cc2b986` (main inn, uten konflikter), `a0868573` (e), `37b7ed66` (f), `e88d449c` (spesifikasjonen, M5 og oppslaget), `9537f188` (rettingene, Rettet-linje også under FR-104, og triagen).
- Hele settet: 13:16:10–13:25:19 (3903 bestått), 13:26:45–13:35:31 (3904) og 13:42:05–13:51:02 (3907), hver gang 24 hoppet over og bare de 7 porttestene feilet.
- M5 (tallet ved indeksens siste dag) fanget på `a0868573` og `9537f188`, og fila var lik HEAD etterpå.
- Gjennomgangen: BH 15, ECH 7 og VG 3 funn i 20 rader: 10 rettet, 5 avvist og 5 står. De tre med dom medium er rettet.
- CI 41058583275 grønn på `9537f188`. PR #106 er utkast og ikke flettet. Bildene er byte for byte de samme, og avtrykkene er oppdatert.

### Åpne punkter
- 8.17a: gruppen ser over tolkningen av f i Rettet-linjene under FR-104 og FR-105 før flettingen mandag.
- 8.17a f: avvik fra én dag per side, slått opp uten endring. Rader med eldre data viser sin egen dag, og ved en periode regnes endringen til radens egen siste børsdag (oversikten og Min liste). Aksjesiden følger aksjens egen siste dag, og indekslinja i grafen kan slutte før grafen.

## 2026-11-03 kl. 01:32 — Marian Osen

### Oppgave
Flette 8.17a 03.11 før kl. 21:20, etter gruppens svar 02.11 kl. 17:40: tolkningen av f står, og avvikene fra én dag per side beholdes som et felles unntak, bare som tekst (instruksjonen kl. 01:09 i dagsfila 03.11).

### Plan
- Instruksjonen i dagsfila, avgjørelsen under story 8.17 og de to spørsmålene i `issues.md` krysset av, på main.
- På grenen i en worktree utenfor repo-mappa: main flettet inn, unntaket under FR-104 og FR-105 og i spesifikasjonen, slått opp i koden, med en test. Hele settet, ruff, CI.
- Squash-fletting låst til head-en, og etterpå status, sprint-status og kvalitetssikringen på main.

### Resultat
- Kvoten kl. 01:09 (00:09 GMT): 0 brukt 03.11 i GMT og 20 igjen, med `extraLimit` 463. Ingen andre kall.
- `4868723b` (01:10) dagsfila, og `ee58786b` (01:11) avgjørelsen og flyttingen til 3.11 under story 8.17, med de to punktene i `issues.md` krysset av.
- Grenen: main flettet inn i `aaa3c284` (01:12). Unntaket står i `047f1f7b` (01:27): datert linje under FR-104 og FR-105 i `prd.md` og i «Åpent» ved f i spesifikasjonen, med `test_fr_104_og_fr_105_har_unntaket_fra_en_dag_per_side`, som feilet med `prd.md` fra HEAD og besto med linja. Slått opp i koden: raden viser aksjens egen siste dag (`bygg_rad`, `med_perioden`) og sier ikke hvilken dag den gjelder, utenom «hentet» under navnet (`eldre_enn_nyeste`). Ukedagen i overskriften og datoen under den er den eldste blant radene (`sidens_dato`), mens indeksen og søylene bruker den nyeste (`sidens_siste`). Aksjesiden har dagen i linja under overskriften. Indekslinja slutter med «Indeksen går bare til». Søylene har bare aksjer med kurs for tabellens dag. Hjelpen og `docs/hjelp.md` er ikke endret, fordi de ikke sier noe som går imot unntaket.
- Ledig minne 6 054 MB. Hele settet alene kl. 01:16:28–01:26:44 (614 s): 3908 bestått, 24 hoppet over og 7 feilet, de 7 porttestene for `start.ps1`. Ruff: ingen funn.
- CI 41552952105 grønn på `047f1f7b`. Worktreen er fjernet. PR #106 ble squash-flettet i `b2e8b2c3` (01:30), låst til head-en, og grenen er slettet på GitHub. `pr-8-17a-bilder` står. CI 41553322199 er grønn på `b2e8b2c3`.
- `de362fac` (01:32): spesifikasjonen done, linja under story 8.17, 8-17 in-progress i sprint-status, og radene i §3, §5 (66 rader: 39 rettet, 13 avvist, 10 utsatt) og vedlegget i kvalitetssikringen.

### Åpne punkter
- 8.17b: Min liste og børsometeret med periodevalget.
- Raden i oversikten sier ikke hvilken dag den gjelder når aksjen mangler kurs for siden sin dag, og overskriften tar da den eldste datoen. Det er unntaket gruppen valgte. Forslag, ikke avgjort: se på det igjen i 8.17b.

## 2026-11-03 kl. 18:44 — Marian Osen

### Oppgave
Bygge 8.17b: periodevalget i Min liste («Sammenlign med») og i børsometeret, etter story 8.17, designreglene §2–3, beslutningen 08.10 kl. 21:48 og svaret 23.10 kl. 12:35 b og c. Egen gren med PR, og stopp før flettingen (instruksjonen kl. 17:42 i dagsfila 03.11).

### Plan
- Instruksjonen i dagsfila og avgjørelsene 03.11 kl. 01:06 og 14:28 under story 8.17, på main.
- Gren i worktreen `../G74-lund-osen-8-17b`, spesifikasjonen `spec-8-17b-periodevalget-i-min-liste-og-boersometeret.md`, PR #108 og én commit per punkt a, b og c.
- Fire mutanter, hele settet alene, gjennomgang med tre linser, triage, CI og bilder av demoen.

### Resultat
- Kvoten kl. 17:42 (16:42 GMT): 0 brukt 03.11 i GMT, 20 igjen og `extraLimit` 463. Ingen andre kall. `data/db/ose.db` er ikke rørt.
- Main: `0e36796e` dagsfila og `dc8a5b08` avgjørelsene under story 8.17.
- Grenen `8-17b-periodevalget-min-liste-boersometer`: `322dd46b` spesifikasjonen, `5d2a9a82` a (Min liste, datoen i en rad med eldre dag, Rettet-linja under FR-104), `7caab471` b (børsometeret, hjelpen, `docs/hjelp.md`, README-en), `7844af63` c (25 tester etter rettingene; testen for adressen fant `&amp;` skrevet to ganger, rettet der), `3c8fd278` rettingene etter gjennomgangen, `496e619c` mutantene og triagen.
- Ledig minne 5 843 MB. Hele settet alene på `7844af6` kl. 18:12:56–18:19:59: 3929 bestått, 24 hoppet over, 6 feilet (porttestene for `start.ps1`). På `496e619` kl. 18:27:07–18:33:50: 3934 bestått, 24 hoppet over, 6 feilet (de samme).
- Mutantene M1–M4 fanget på `7844af6` og på `3c8fd27`, og hver fil var lik kopien og HEAD etterpå.
- Gjennomgangen: BH 17, ECH 7 og VG 4. Rettet: ECH1, BH11/VG1, ECH2/VG2 (børsometeret), VG3, VG4, BH10, BH13, BH16, og kolonneraden i Min liste (funnet i bildene). Avvist: BH1, BH2, BH4, BH5, BH7. Resten står, med BH15 og BH8 som spørsmål til gruppen.
- CI 41684364131 grønn på `496e619c`: macOS-jobben ble avbrutt etter 15 min uten et steg som feilet, og besto ved ny kjøring. Bildene av demoen ligger på `pr-8-17b-bilder` (`8a0ed85d`) og i en kommentar i PR #108. Bildene til README-en er byte for byte de samme, og avtrykkene er oppdatert. Worktreen `../G74-lund-osen-8-17b` står til flettingen.

### Åpne punkter
- 8.17b, spørsmål til gruppen før flettingen: er tolkningen av f riktig (siste børsdag er sidens dag, og linja under er sammenligningen)?
- 8.17b, spørsmål til gruppen: skal endringen i linja under ved «Velg dag» i Min liste være fra dagen til siste børsdag (bygget), eller endringen den dagen?
- 8.17b BH8, spørsmål til gruppen: skal fargetrinnene i børsometeret (±0,5 % og 2 %) være de samme for en periode?
- PR #108 flettes etter svarene; worktreen `../G74-lund-osen-8-17b` fjernes da.

## 2026-11-03 kl. 19:53 — Marian Osen

### Oppgave
Flette 8.17b 03.11 før kl. 21:20, etter gruppens svar kl. 19:25 på de tre spørsmålene i PR #108 (instruksjonen kl. 19:29 i dagsfila 03.11).

### Plan
- Instruksjonen og svaret under story 8.17 på main, med spørsmålene i `issues.md` merket som besvart.
- På grenen: main flettet inn, svarene i spesifikasjonen og PR-en, CI grønn på head-en.
- Squash-fletting låst til head-en, og etterpå status, sprint-status, kvalitetssikringen og `prd.md` på main.

### Resultat
- Kvoten kl. 19:29 (18:29 GMT): 0 brukt 03.11 i GMT, 20 igjen og `extraLimit` 463. Ingen andre kall.
- Main: `c58b0ce7` (19:29) dagsfila, `a6df8f16` (19:30) svaret kl. 19:25 under story 8.17 og spørsmålene besvart.
- Grenen: main flettet inn i `f01a07da` (19:30), svarene i spesifikasjonen i `b6978b2f` (19:30), PR-en oppdatert. CI 41694504920 grønn på `b6978b2f`.
- PR #108 squash-flettet i `978bd1ab` kl. 19:36, låst til head-en. Grenen er slettet på GitHub, worktreen er fjernet, og `pr-8-17b-bilder` står.
- `23c16ad9` (19:37): spesifikasjonen done, linja under story 8.17, 8-17 done i sprint-status, og radene i §3, §5 (26 rader: 9 rettet, 5 avvist, 10 utsatt) og vedlegget i kvalitetssikringen. `045ddeb1` (19:37): datert linje om flettingen ved R14 og under Rettet-linja i FR-104 i `prd.md`.
- CI 41695429612 på `978bd1ab`: macOS-jobben ble avbrutt etter 15 min uten et steg som feilet, og besto ved ny kjøring (grønn 19:52). CI 41695568637 og 41695671845 grønne på `23c16ad9` og `045ddeb1`.

### Åpne punkter
Ingen.
