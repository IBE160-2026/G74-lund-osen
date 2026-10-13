---
title: 'Story 8.0e: Oversikten fra designforslaget'
type: 'feature'
created: '2026-10-13'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '4c4b420f3ef2bd6ef07d1ae24d301632d721544c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oversikten viser bare «N av 3» og ikke hvilke sjekker som slo ut, og aksjene som skilte seg ut, står i samme liste som resten (story 8.0e i `epics.md`, endringsforslaget 13.10, punkt 4.6).

**Approach:** To pull requests. PR 1 (grenen `8-0e`) tar tabellen: T, B og I under «N av 3», de to delene «Skilte seg ut» og «Øvrige aksjer», og pillen «3 av 3» med svart fyll. PR 2 tar teksten over tabellen: overskriften med ukedagen, innledningen, linja om «3 av 3», «Slik leser du tabellen», «Demo Børs» og README-statusen.

## Planen

Planen ble vist i chatten 13.10 og er ført kort i `docs/ai-prompts/2026-10-13.md` (Utført-linja for instruksjonen kl. 20:34). Svarene kl. 21:10 (1–7) og kl. 21:27 (8) er beslutninger:

1. **Demoen sier «Demo Børs»** der den ekte versjonen sier «Oslo Børs»: i innledningen og i linja over tabellen («Demo Børs · 09.10 · 14 aksjer»). Det endrer beslutning 3 i 8.0c. Merket «Demoversjon. Eksempeltall: …» står som før, og grensene i hjelpen sier fortsatt «15 aksjer på Oslo Børs» (beslutning 5 i 8.0c). PR 2.
2. **Første punkt i «Slik leser du tabellen»:** «T, B og I er trend, bevegelse og interesse, og hver gir +1, 0 eller -1. Øverst i cellen står hvor mange som slo ut, fra 0 av 3 til 3 av 3.» PR 2.
3. **Når ingen skiller seg ut:** overskriften er «0 av M aksjer skilte seg ut <ukedag>», setningen «Hos …» står ikke, og setningen fra 8.0c står der «Skilte seg ut» ellers står. Uten en eneste vurdering står ingen overskrift. Setningene i PR 1, overskriften i PR 2.
4. **Når N er 1:** «Hos 1 aksje slo minst 2 av 3 ut.» Ellers tavlas ordlyd. PR 2.
5. **Ukedagen** gjelder samme dato som linja over tabellen, altså den eldste (story 8.0). PR 2.
6. **To pull requests:** først tabellen, så teksten over tabellen.
7. **Demoen har samme logo og utseende** som den ekte versjonen, nå og når 8.0d kommer. Bare merket øverst og «Demo Børs» skiller dem (FR-411).
8. **Pillen «3 av 3»** får svart fyll og hvit tekst inne i den gule ringen (`#a67c00`), som i designforslaget. 2 av 3 merkes som i dag, med fet skrift og strek, uten fyll og uten gult. PR 1, med en test for kontrasten, og `designregler.md` §3 får en datert linje.

## Boundaries & Constraints

**Always:**
- Tabellen har fortsatt fem kolonner (FR-101).
- T, B og I leses fra den lagrede vurderingen, aldri regnet på nytt (FR-101, AD-7).
- Delingen bruker terskelen fra `Parametre` (FR-705), og hver del er sortert etter FR-102.
- Det nye vises også med demobasen, og en test krever det (FR-411).
- Grenen bruker bare testbaser (regel 22). Ingen API-kall, ingen nettkall i tester (AD-8).
- Tall vises med vanlig bindestrek som minus (regel 21), og formen bestemmes ett sted.

**Never:**
- Ingen sjette kolonne og ingen endring i signalberegningen, hentingen eller basen.
- README-en endres ikke i PR 1.
- Ingen tekst bak «?» endres i PR 1.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Noen over terskelen | Rader med 3, 2, 1 og 0 | «Skilte seg ut» med 3 og 2, så «Øvrige aksjer» med 1, 0 og radene uten vurdering, hver del i FR-102-rekkefølge | N/A |
| Ingen over terskelen | Alle vurderte har 0 eller 1 | Setningene fra 8.0c i stedet for «Skilte seg ut», så «Øvrige aksjer» | N/A |
| Ingen vurdering | Ingen rad har vurdering | Én del uten overskrift, ingen setning | N/A |
| Alle over terskelen | Alle har 2 eller 3 | Bare «Skilte seg ut» | N/A |
| Rad uten vurdering | Grunn eller ingen rad | «–» og grunnen, uten T, B og I | N/A |
| Lagret mot kursene | Vurderingen sier T +1, kursene ville gitt 0 | «T +1» | N/A |

</frozen-after-approval>

## Code Map

- `src/markedsoversikt.py` -- `Rad` (vurdering, styrke, skiller_seg_ut med `>= p.terskel` i `bygg_rad`), `bygg_oversikt` (FR-102), `ingen_skilte_seg_ut`, `antall_vurdert`. Ny: `Rad.sjekker` og `del_i_to`.
- `src/tallformat.py` -- formen på tall (regel 21). Ny: `fortegn(verdi)` gir «+1», «0», «-1».
- `src/aksjedetalj.py:66` -- `SjekkVisning.fortegn`, samme form. Bruker `fortegn()`.
- `src/vurderingsdata.py` -- `Vurdering.trend`, `bevegelse`, `interesse`. Endres ikke.
- `src/app.py` -- ruta for `/`: gir `rader`, `ingen_skilte_seg_ut`, `antall_vurdert`, `parametre`, `antall_sjekker` til malen. Får de to delene.
- `src/templates/index.html` -- tabellen, `.pille.tre-av-tre`, setningene fra 8.0c.
- `tests/test_app.py` -- `_Tabell` (leser `tbody`), `test_fortsatt_fem_kolonner`, `TestStory80c`, kontrasttesten for ringen.
- `tests/test_demo.py` -- `TestStory80cIDemoen`, fixturen `demobase` (kopi i tmp).
- `_bmad-output/planning-artifacts/designregler.md` §3 -- datert linje om fyllet.

## Tasks & Acceptance

**Execution:**
- [ ] `src/tallformat.py`, `src/aksjedetalj.py` -- `fortegn()` og bruk den i `SjekkVisning` -- én form for fortegnet
- [ ] `src/markedsoversikt.py` -- `Rad.sjekker` (T, B, I fra vurderingen, tom uten vurdering) og `del_i_to(rader)` (skiller seg ut / øvrige, rekkefølgen beholdt) -- logikken uten HTML
- [ ] `src/app.py`, `src/templates/index.html` -- to `tbody` med en overskriftsrad hver, setningene fra 8.0c i første del når ingen skilte seg ut, T, B og I under pillen, svart fyll på «3 av 3» -- tabellen
- [ ] `tests/test_app.py`, `tests/test_markedsoversikt.py`, `tests/test_tallformat.py`, `tests/test_demo.py` -- testene for matrisen og mutantene
- [ ] `designregler.md` §3 -- datert linje

**Acceptance Criteria:**
- Given en rad med vurdering, when oversikten vises, then cellen har «N av 3» og under den «T +1», «B 0» og «I -1» fra vurderingen.
- Given demobasen, when oversikten vises, then T, B og I, de to delene og pillen med fyll står der.
- Given «3 av 3», when oversikten vises, then pillen har svart fyll, hvit tekst og gul ring, og kontrasten er minst 4,5:1.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Overskriften for hver del er en rad `<tr class="del"><th colspan="5" scope="rowgroup">` først i sin `tbody`, så tabellen har fortsatt fem kolonner. Setningene fra 8.0c står i en rad `<tr class="del">` med én celle over fem kolonner. Er det ingen første del (ingen vurdering), står radene i én `tbody` uten overskrift.

```html
<td class="tall styrke">
  <span class="pille tre-av-tre">3 av 3</span>
  <span class="sjekker"><span>T +1</span> <span>B +1</span> <span>I +1</span></span>
  <span class="merke">skiller seg ut</span>
</td>
```

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn. Før: 1461 bestått og 16 hoppet over på main (`3ad2922`, 13.10 kl. 22:32).

**Mutantene** kjøres én om gangen mot hele testsettet med `-x`, og fila settes tilbake og kontrolleres med sha256: T, B og I regnet av kursene; en sjette kolonne; T, B og I på en rad uten vurdering; `>=` blir `>` i delingen; terskelen skrevet fast; «Skilte seg ut» sammen med setningen fra 8.0c; sorteringen snudd i én del; «3 av 3» uten svart fyll.
