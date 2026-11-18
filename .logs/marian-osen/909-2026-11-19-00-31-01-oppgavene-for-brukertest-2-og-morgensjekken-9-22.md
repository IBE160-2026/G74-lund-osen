# Oppgavene for brukertest 2 og morgensjekken uten falske alarmer (9.22)

## 2026-11-19 kl. 00:31 — Marian Osen

### Oppgave
Instruksjonen limt inn 18.11 kl. 21:41, etter gruppens svar 18.11 kl. 11:42, 11:49, 16:01 og 21:27. Først oppgavene A–G for brukertest 2 i `docs/brukertest.md` på main. Så story 9.22 med tre små rettinger: morgensjekken uten falske alarmer, «51 børsdager» i stedet for «handelsdager», og samme navn på sletteknappen som i spørsmålet før sletting. For knappen anbefalte rådet å vente til etter brukertest 2, men gruppen valgte å ta den nå.

### Plan
- `docs/brukertest.md` på main først, med `--dokumentene` før push (`e65692b3`).
- Story 9.22 på en gren fra `origin/main` (`0c650e14`), i worktreen `G74-lund-osen-9-22`, med spesifikasjonen som første commit (`d1c14744`).
- Hver retting fikk en test som feiler før rettingen. Morgensjekken ble kjørt mot main før og etter. Gjennomgangen ble tatt med én leser.
- Bildene ble tatt etter kveldsjobben, og flettingen skjedde etter pausene om kvelden.
- Spesifikasjonen: [spec-9-22-morgensjekken-og-to-rettinger.md](../../_bmad-output/implementation-artifacts/spec-9-22-morgensjekken-og-to-rettinger.md).

### Resultat
- **Brukertest 2** (`e65692b3`): oppgavene A–G og spørsmålet etter G står i en tabell med egen «Før testen». Svarene kl. 21:27 er tatt med: F tas i den ekte versjonen, og én egen aksje uten notat fjernes før testen.
- **Morgensjekken** (`812f462a`, `02eb116c`):
  - Del 2 teller hver «## »-overskrift og godtar `**Utført (…):**` og `**Utført, …:**`. Telt for hånd gir den 11/11 for 10.11, 7/7 for 16.11 og 12/12 for 17.11.
  - Del 7 kjenner taggen v8.
  - Del 9 har en liste over kjente `.json`-filer og plassholdere, med grunnen.
  - Del 10 teller regel 20 bare for gruppens commits.
  - Mot main gikk saken fra «17 ting å se på» til «alt i orden».
- **«51 børsdager»** står i FR-101 og i kilden i `src/hjelpetekster.py`, med en linje i `prd-endringslogg.md` (`46c7dde5`).
- **Knappen** heter «Slett notatet, kjøpet og salget» (`1185c652`). Alle de 20 bildene ble tatt to ganger i demoen på port 8922 og 8923 og var like byte for byte. Tre er nye, og avtrykkene er regnet ut på nytt (`f0f5abec`). Bildegrenen `pr-9-22-bilder` er pushet (`dd395dc3`).
- **Spørsmål 7 i 9.20 og spørsmål 1 i 9.21** har en datert linje (`b99bd3f3`).
- **Gjennomgangen:** 11 funn. ECH1 og ECH2 (middels) og åtte lave er rettet. ECH5 står med grunn.
- **Testene:**
  - Testfilene storyen rører, er grønne lokalt.
  - `--dokumentene` på grenen ga 3085 bestått og 7 hoppet over.
  - CI var grønn i alle fire jobbene (run 44418120615), med 6002 bestått og 99 hoppet over i `pytest`.
  - `--dokumentene` på main etter føringen ga 3085 bestått og 7 hoppet over.
- **Flettingen:** PR #169 ble squash-flettet i `7480e72c` 19.11 kl. 00:16, låst til `1557ff5e`, uten nytt ja. Føringen står i `f6c46741` og `2cda2a21`.
- Lukket i `issues.md`: spørsmål 7 i 9.20, spørsmål 1 i 9.21 og punktet om `morgensjekk.py` fra refleksjonsloggen.

### Åpne punkter
- «51 handelsdager» står fortsatt i en kommentar i `src/fetch_prices.py` og i en docstring i `tests/test_fetch_prices.py`. Instruksjonen gjaldt bare FR-101 og kilden. Spørsmål til gruppen: skal de også rettes?
- Klokkeslettet i «HEAD paa GitHub» viser UTC når morgensjekken kjøres lokalt på Windows. På GitHub kjører den på Linux. Det er ikke endret.
