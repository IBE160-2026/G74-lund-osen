# Dobbeltklikk-jobbene i CI

## 2026-11-03 kl. 20:43 — Marian Osen

### Oppgave
Bare lesing: hvorfor dobbeltklikk-jobben på macOS ble avbrutt etter 15 minutter tre ganger 3.11, og hvorfor jobben på Windows feilet i «Start demoen på Windows» på `8b0988b` (instruksjonen kl. 20:32 i dagsfila 03.11).

### Plan
- Slått opp i `.github/workflows/tester.yml` hva stegene i jobben `dobbeltklikk` gjør.
- Med `gh api`: alle kjøringene av `tester.yml` fra 20.10, med hvert forsøk, og varigheten til jobben og hvert steg på macOS og Windows.
- Loggene for de feilede Windows-kjøringene, og dokumentasjonen fra GitHub for `pwsh`.

### Resultat
- Kvoten kl. 20:32 (19:32 GMT): 0 brukt 03.11 i GMT, 20 igjen og `extraLimit` 463. Ingen andre kall. Ingenting i `.github/`, `src/`, `tests/` eller `start/` er endret, ingen ny kjøring i CI, og ingen demo eller server er startet.
- 483 kjøringer og 616 dobbeltklikk-jobber fra 20.10. macOS: 300 grønne, 10–41 s og én gang 99 s, og 8 avbrutt (26.10, 28.10, tre 2.11 og tre 3.11), alle uten maskin og uten steg. Windows: 9 feil, 3 i «Start demoen på Windows»; 30.10 og 3.11 med samme mønster (`taskkill` fikk ikke stoppet en underprosess, og `pwsh` avsluttet med den koden), 23.10 en annen feil.
- Funnene, det som ikke er funnet, og to spørsmål til gruppen står som datert linje under punktet om CI i `issues.md`.

### Åpne punkter
- Gruppen svarer på de to spørsmålene under punktet om CI i `issues.md` (`exit 0` i steget på Windows, og hva som gjøres når macOS-jobben ikke får maskin).
