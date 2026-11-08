---
title: 'Story 8.8: Signaldager i kursgrafen'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '6ec218c9'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Utdraget 08.11 §5 sier at signaldagene ikke er tegnet på tavla, og at storyen bygges etter story 8.8 i `epics.md` og `designregler.md`.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hvilke dager markeres?** *Forslag:* dagene aksjen skilte seg ut, med signalstyrke på terskelen eller over (2), som i oversikten. En prikk på kurslinja den dagen, i fargen for retningen (positiv, negativ eller blandet, `designregler.md` §3), og med en gul ring ved 3 av 3. Andre dager markeres ikke.
2. **Dager uten signal.** *Forslag:* en dag med grunn, en dag uten rad og en dag som ikke er børsdag markeres ikke, så ingen av dem kan se ut som styrke 0, og heller ikke styrke 0 eller 1.
3. **Hvor starter markeringene?** *Forslag:* ved den første raden i `vurdering` for aksjen, med vurdering eller grunn: dagen signalet begynte å bli lagret. Teksten under grafen sier datoen: «Prikkene på kurslinja viser dagene med signalstyrke 2 eller mer, fra ‹dato›.» Ordene «skilte seg ut» står ikke der, fordi siden bare bruker dem om dagen den viser (story 8.0d). Er den første raden etter grafens første dag, står det at det ikke er signal før den datoen.
4. **Begge grafene.** *Forslag:* den brede og den smale grafen har prikkene, med en tekst for skjermleser i figuren.

## Intent

**Problem:** kursgrafen viser ikke hvilke dager aksjen skilte seg ut, så man ser ikke hvordan signalet har oppført seg over tid (FR-206).

**Avgjørelsene:** story 8.8 i `epics.md` (08.10), FR-206, og §5 i `designutdrag-2026-11-08.md`.

## Delene

### A) Dagene leses, aldri regnes

`bygg_graf` får dagene som skilte seg ut, lest med `les_periode` fra 2.7 (`SqliteVurderingslager`), med retningen og styrken som er lagret. Signalet regnes aldri av kursene (AD-7).

**Ville feilet hvis:** markeringene ble regnet av kursene. Da viser grafen dagens parametre, ikke hva løsningen sa.

### B) Prikkene i grafen

En prikk per dag som skilte seg ut og står i grafen, i retningens farge, og en gul ring ved 3 av 3.

**Ville feilet hvis:** en dag med grunn, uten rad eller med styrke under terskelen ble markert.

### C) Datoen markeringene starter

Teksten under grafen sier datoen for den første raden i `vurdering`.

**Ville feilet hvis:** grafen hadde markeringer før den datoen, eller ikke sa den.

### D) Hjelpen, `docs/hjelp.md` og README-en

Hjelpen ved grafen og `docs/hjelp.md` sier hva prikkene er (regel 19).

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `8-8-signaldager-i-kursgrafen`, i worktreen `G74-lund-osen-8-8`, fra main (`6ec218c9`). Ingen migrasjon.

- **Filene:** `Signaldag` og `signal` i `bygg_graf` (`src/graf.py`), `_signaldagene` i `src/app.py`, som leser med `les_periode`, prikkene og teksten under grafen i `src/templates/aksje.html`, fargene i `src/static/stil.css`, og «Hva er prikkene på kurslinja?» i `docs/hjelp.md`.
- **Avvik:** del D sier «hjelpen ved grafen». Hjelpen bak «?» ved grafen er ikke endret, fordi teksten under grafen sier hva prikkene er og datoen; `docs/hjelp.md` har forklaringen. README-en sier ingenting om grafen som blir feil.
- **Tester («Ville feilet hvis» i hver):** `tests/test_signaldager.py`. `test_siden_leser_en_gang_per_maaned` i `tests/test_historikken.py` teller nå én lesing til, for hele perioden, aldri dag for dag.
- **Hele settet alene** kl. 20:01:39–20:10:55: 4581 bestått, 24 hoppet over og 0 feilet. Bildet av aksjesiden er nytt og 2294 px høyt (teksten under grafen har en linje til); de andre er byte for byte de samme.
