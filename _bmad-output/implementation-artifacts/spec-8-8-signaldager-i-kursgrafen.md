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
- **Hele settet alene** kl. 20:01:39–20:10:55: 4581 bestått, 24 hoppet over og 0 feilet. Bildet av aksjesiden er nytt; de andre er byte for byte de samme.

## Mutantene

På `9a7f7fa9` fire: A (en dag under terskelen markeres) 2, B (3 av 3 får ikke ringen) 1, C (grafen sier ikke datoen) 1 og D (den smale grafen mangler prikkene) 1 test. Alle ble fanget, og hver fil var lik HEAD etterpå.

## Gjennomgangen 08.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 15 funn, Edge Case Hunter 9 og Verification Gap 10. Ingen høye.

**Middels, alle rettet**
- *BH3, ECH1, VG1:* lista over dagene sto synlig under grafen, fordi `.skjult` ikke gjaldt på aksjesiden. Nå er den skjult, og antallet står synlig (`test_lista_er_skjult_og_antallet_staar`).
- *ECH2, VG3:* siste-punktet dekket prikken for siste dag. Prikkene tegnes nå etter siste-punktet og streken (`test_prikkene_tegnes_over_siste_punktet`).
- *BH2, ECH7, VG2:* retningen ble bare vist med farge. Nå har den også en form, rund for positiv, firkant for negativ og rute for blandet, og teksten under grafen sier det (`test_retningen_har_en_form`).
- *BH4:* lista for skjermleseren hadde ingen grense. Nå står antallet, og lista bare opptil 31 dager.
- *BH5, ECH3:* prikkene ble et bånd i lange perioder. Radien følger nå avstanden mellom dagene, mellom 2 og 4 px.
- *BH6, ECH4, VG4:* med «Velg dag» før signalet sto en startdato etter grafen som om den var i den. Nå står «Signalet er lagret fra …, etter den siste dagen i grafen» (`test_velg_dag_foer_signalet`).

**Lav**
- *Rettet:* BH10 (negativ testes), BH12 og VG6 («Ingen av dagene i grafen hadde …»), VG5 (setningen «før den dagen» testes også når den ikke skal stå), BH7 (hjelpen sier nå at startdatoen er den første raden, med signal eller grunn), BH14 (`dato` viser året når det er et annet).
- *Ført:* BH1 og ECH6 (terskelen er `STANDARD`, som `parametre` på siden, så de er like; endres terskelen, tolkes historikken med den nye), BH8 og ECH8 (hele historikken leses to ganger per side), BH9 (testen av `bygg_graf` alene; appnivåtestene fanger en mutant som regner signalet, VG), BH11, VG9 og VG10 (hjelpeteksten er ikke bundet til tallene), BH13 (status), BH15 (navnet `alle`), ECH5 og VG8 (en ugyldig rad gir ingen prikker uten beskjed), VG7.
- **Etter gjennomgangen:** hele settet alene kl. 20:28:03–20:37:44: 4586 bestått, 24 hoppet over og 0 feilet. Bildet av aksjesiden er tatt på nytt, 2258 px som før.
