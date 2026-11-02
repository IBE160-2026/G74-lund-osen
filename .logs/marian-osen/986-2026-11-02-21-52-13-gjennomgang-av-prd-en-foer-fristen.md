# Gjennomgang av PRD-en før fristen

## 2026-11-02 kl. 21:52 — Marian Osen

### Oppgave
Instruksjonen kl. 21:42 i `docs/ai-prompts/2026-11-02.md`: lese `prd.md` mot repoet før fristen torsdag 5.11, etter beskjeden fra faglærer på emnesiden 2.11 og gruppens svar kl. 21:18: les først, rett onsdag. `prd.md` endres ikke i kveld.

### Plan
- Steg 0 og kvoten (regel 15), og instruksjonen i dagsfila.
- Beskjeden under E i `docs/innlevering.md` og to Rettet-linjer i oppføringen 30.10 i refleksjonsloggen, slått opp i dagsfila 30.10 og `git log` først.
- §8 lest selv mot `epics.md`, `docs/innlevering.md`, `src/boersdag.py` og `docs/kilder-og-rettigheter.md`. §4 og §5 lest av en underagent, og funnene stikkprøvd mot `prd.md`, `src/` og commitene.
- Funnene i en ny fil i `gjennomganger/`, med lenke fra `docs/innlevering.md`.

### Resultat
- Kvoten kl. 21:42 (20:42 GMT): 0 brukt og 20 igjen 02.11 i GMT, `extraLimit` 463. Ingen andre kall.
- `6748dc18`: instruksjonen i dagsfila.
- `88827911`: beskjeden og svaret kl. 21:18 under E i `docs/innlevering.md`, og to Rettet-linjer i 30.10 (kl. 12:00 var planen; instruksjonen kl. 12:21 heter «8.17a siste rettinger»).
- `95edc9e9`: `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/gjennomganger/gjennomgang-2026-11-02-foer-fristen.md` med de 14 punktene i §8, 37 rader for resten (2 uten retting: front matter og lenkene) og 11 spørsmål, og lenken under beskjeden.
- Forslag for §8: lukk 5b og 9; utenfor v1 for 2, 4, 6, 8, 11, 12, 15 og 16; åpne med eier og frist: 13, 21, 22 og 25.
- Testene for dokumentene, de seks i `docs/kvalitetssikring.md`, ga 255 bestått før hver push. `prd.md` og koden er ikke endret.

### Åpne punkter
- Rettingen av `prd.md` onsdag 4.11, etter gruppens svar på de 11 spørsmålene i gjennomgangen.
- `sprint-status.yaml` henger etter `epics.md`: 2.13 står som review (flettet i `676fbc8b`), 9.5 som backlog (utgår 06.10), og 2.3c, 2.3d og 3.5a–h mangler.
