# Kontroll av kveldskjøringene

## 2026-11-02 kl. 17:43 — Marian Osen

### Oppgave
Kontrollere jobbens kjøringer fredag 30.10 til søndag 01.11, som gikk uten oppsyn, og PC-en og CI. Bare lesing: ingen API-kall utover kvotesjekken, `src/fetch_prices.py` kjøres ikke, basen åpnes bare for lesing, og oppgaven og worktreen `G74-lund-osen-jobb` røres ikke.

### Plan
- Steg 0 og instruksjonen i dagsfila `docs/ai-prompts/2026-11-02.md`, pushet.
- Lese oppgaven, PC-en (oppstart, Windows Update, pause, hvilemodus, disk), de tre loggene, basen med `mode=ro`, kvoten og CI.

### Resultat
- Dagsfila: `84792a30` (17:41).
- **Avvik fra det ventede:**
  - Windows Update står på pause, fra 30.10 kl. 12:23 til 06.11 kl. 12:22 norsk tid (`PauseUpdatesStartTime` og `PauseUpdatesExpiryTime`). Ved kontrollen 30.10 kl. 10:54 sto den ikke på pause. Det er ikke slått opp hvem som satte pausen.
  - Docker Desktop har kjørt hele tiden siden 30.10 kl. 13:59:50 (prosessenes starttid). Jobben fant derfor Docker svarende og verken startet eller stoppet Docker Desktop i noen av de 12 kjøringene. Den startet og stoppet bare Ollama. Skriptet starter Docker Desktop bare når `docker info` ikke svarer (`start/kveldshenting.ps1`, steg 3). Docker Desktop er ikke stoppet, fordi denne økten ikke startet den.
- a) Oppgaven er Ready, LastRunTime 01.11 kl. 23:45:01, LastTaskResult 0 og NextRunTime 02.11 kl. 22:15:00.
- b) PC-en:
  - LastBootUpTime 29.10 kl. 19:59:48, og ingen hendelser om omstart eller avslåing (1074, 6005, 6006, 6008, 41) etter 30.10 kl. 13:56.
  - Windows Update har etter det bare installert Defender-definisjoner (KB2267602, 9 ganger, sist 02.11 kl. 12:55) og Store-apper 30.10 kl. 21:04, 31.10 kl. 22:06, 01.11 kl. 06:50 og 01.11 kl. 23:04. CrossDevice feilet to ganger (0x80073D02) og gikk inn 01.11 kl. 23:04. Siste KB i Get-HotFix er fortsatt KB5127936 fra 29.10.
  - Hvilemodus i strøm er Aldri (STANDBYIDLE AC 0), og det er 396,4 GB ledig av 951,6 GB på C:.
- c) Loggene for 30.10, 31.10 og 01.11 har fire kjøringer hver, kl. 22:15, 22:45, 23:15 og 23:45, og hver kjøring brukte 19 til 24 sekunder, utenom den første hver dag, som brukte 82 til 92 sekunder. Det finnes ingen logg for 02.11.
  - Arbeidskopien sto på `cf39c77` fredag og på `95673e0` lørdag og søndag. Den første kjøringen fredag ble startet på nytt fordi utsjekken endret skriptet.
  - Fredag kl. 22:16 kom kursene for 30.10, 15 vurderinger og 15 KI-tekster fra den lokale modellen (`gemma4:e4b`), og alle 15 besto kontrollen.
  - Koden fra hentingen og fra målingen var 0 i alle 12 kjøringene. Loggene har 0 linjer med FEIL eller STOPP.
  - «Kvoten etter»: 20 av 20 brukt 30.10, 31.10 og 01.11 i GMT, alle med `extraLimit` 463.
- d) Basen: siste dag i `kurs` er 30.10 for alle 15, og i `indeks` 30.10. I `vurdering` er det 15 rader for 30.10, og i `ki_logg` 15 (slag aksje, modell `gemma4:e4b`, 15 besto). Ingen rader etter 30.10.
- e) `omsetning` har 48 rader og 0 med feil, regnet per dag i norsk tid: 4 for 29.10 (HGSB, HKY, HPUR, HSPG), 4 for 30.10 (HUDL, HYN, HYPRO, IDEX), 20 for 31.10 (INDCT–NCOD) og 20 for 01.11 (NEXT–POLAR).
- f) Kvoten kl. 17:40 (16:40 GMT): `apiRequests` 20 med `apiRequestsDate` 2026-11-01, så 0 brukt og 20 igjen 02.11 i GMT, og `extraLimit` 463.
  - CI på `95673e0` er grønn: 41059150318 (tester) og morgensjekken 41193502505, 41302158764 og 41448320817 (31.10, 01.11 og 02.11, de eneste kjøringene etter fredag kl. 14 utenom dagsfila).
  - CI på `9537f18` er grønn (41058583275), og PR #106 er fortsatt et åpent utkast, uten noen kjøring på grenen etter den.
- Testene for dokumentene ga 255 bestått før pushen av dagsfila.

### Åpne punkter
- Pausen i Windows Update går ut 06.11 kl. 12:22. Etter det kan oppdateringer starte PC-en på nytt.
- Docker Desktop har kjørt siden 30.10 kl. 13:59, så jobbens start og stopp av Docker Desktop er ikke prøvd etter 29.10.
- Paragrafen i `malinger.md` for søndag 01.11 er ikke skrevet. Punktet i `issues.md` fra 29.10 står fortsatt åpent.
