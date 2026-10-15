---
title: 'Story 4.3: SQLite-adapter for KILogg'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a2f71ae'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KI-loggen fra 4.2 finnes bare i minnet. Eksempelsettet fra én ukes drift krever at loggen overlever en omstart (story 4.3 i `epics.md`, FR-604).

**Approach:** Migrasjonen `0005_ki_logg.sql` lager tabellen `ki_logg` med en CHECK for emnet og for besto, tekst og grunn, en unik indeks per emne med `ifnull` for feltene som kan være tomme, og to triggere som avviser UPDATE og DELETE. `SqliteKILogg` i `src/lagring_sqlite.py` oppfyller porten fra 4.2, skriver bare med `INSERT … ON CONFLICT DO NOTHING`, og prøves mot de samme testene som `MinneKILogg` (fixturen `logg_lager`). Hovedindeksen (2.8) får `0006`. PR C i planen for KI-laget.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1721 bestått og 17 hoppet over på main (`a2f71ae`).

**Flettes ikke i dag.** Migrasjonen endrer `ose.db` ved neste henting, fordi hentingen migrerer gjennom `aapne_base`. PR-en flettes en annen dag før kl. 21:40, når henteinstruksjonen er rettet for versjon 5 (instruksjonen kl. 15:53, steg 4).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 2: raden står når den finnes, også når modellen feilet (FR-604). Adapteren skriver med `ON CONFLICT DO NOTHING`, og `skriv` gir da `False`.
- Svar 6: `0005` gir plass til dagsteksten i 10.6, med en dato som eneste emne (slaget `dag`).

**Mutantene** (planen kl. 15:43): C1 tabellen lages utenfor migrasjonsløperen; C2 skrivingen bruker `INSERT OR REPLACE`; C3 tabellen har ingen CHECK på emnet.

## Boundaries & Constraints

- Ingen endring i `src/fetch_prices.py`. Hentingen migrerer likevel basen til versjon 5 ved neste kjøring etter flettingen.
- Grenen bruker bare testbaser (regel 22). Ingen API-kall.

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En tom base | `migrer` gir versjon 5 med `ki_logg` |
| En base på versjon 4 | `SqliteKILogg` avviser den til den er migrert |
| `skriv` og så omstart | raden leses tilbake lik |
| `UPDATE` eller `DELETE` på `ki_logg` med SQL | avvist av triggerne |
| To rader for dagen samme dato, også med SQL | den andre avvises av den unike indeksen |
| En rad med feil form med SQL (begge emner, besto uten tekst) | avvist av CHECK |

</frozen-after-approval>

## Code Map

- `src/migrasjoner/0005_ki_logg.sql`: tabellen, indeksen og triggerne.
- `src/lagring_sqlite.py`: `SqliteKILogg` og `_kirad`.
- `tests/test_kilogg.py`: porttestene, nå også mot `SqliteKILogg`.
- `tests/test_kilogg_sqlite.py`: migrasjonen, omstarten og basens egne kontroller.
- `tests/test_aksje.py`, `tests/test_migrering.py`: siste versjon er 5.

## Spec Change Log

## Review Triage Log

## Verification
