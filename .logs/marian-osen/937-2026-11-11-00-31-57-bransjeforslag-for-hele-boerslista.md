# Bransjeforslag for hele børslista

## 2026-11-11 kl. 00:31 — Marian Osen

### Oppgave
Instruksjonen kl. 13:41 10.11 i vindu 2, etter gruppens svar kl. 13:38: lag et forslag til bransje for hver aksje i børslista, så den som følger en aksje, ikke velger bransjen selv. Det skulle bare leses, og lages én fil i scratchpad. Ingen API-kall, og ingen endring i repo-mappa.

### Plan
- Les `boersliste` i `data/db/ose.db` med `mode=ro`, de 13 bransjene i `valg.BRANSJENE` og `BRANSJE` i `src/ferdige_lister.py` på origin/main.
- Bransjen fra `BRANSJE` uendret for aksjene der, og et forslag ut fra navnet for de andre, merket usikker der lite er kjent. Definisjonene er de i tabellen «Bransjene» i `designregler.md` §4.
- CSV-fila `bransjeforslag-2026-11-10.csv` i scratchpad, og bare antallene i svaret.

### Resultat
- 297 rader: 87 «sjekket 08.11», 157 «forslag» og 53 «forslag, usikker». BAKKA er satt til Sjømat og ATEA til Teknologi.
- `BRANSJE` har 89 nøkler. To av dem er demoaksjer (HVLK og NRDE) som ikke står i børslista.
- Gruppen sjekket lista på en delt side kl. 14:43: alle 195 er avgjort, 194 som foreslått, og MULTI er tatt ut. De 195 er de 210 forslagene og de usikre, minus de 15 i lista, som har samme bransje som i §4 (svar 2 kl. 16:25). Kl. 15:22 avgjorde gruppen at SCOIN er ute, som 08.11.
- Instruksjonen og de to svarene er ført ordrett i `docs/ai-prompts/2026-11-10.md` i `9553c7b8`, i steg 4 i målingen, som tillegget kl. 16:26 sier.
- Del B i vindu 4 fører lista inn i koden og leser CSV-fila i scratchpad. Fila committes aldri.

### Åpne punkter
- Avklart: 87 sjekket i `BRANSJE` mot 88 i svaret 08.11. Forskjellen er SCOIN, som ble tatt ut kl. 22:03 08.11 fordi selskapet er under avvikling (docstringen i `src/ferdige_lister.py`).
