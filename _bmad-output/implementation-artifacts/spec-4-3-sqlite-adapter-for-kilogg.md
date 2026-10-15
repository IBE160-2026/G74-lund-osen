---
title: 'Story 4.3: SQLite-adapter for KILogg'
type: 'feature'
created: '2026-10-15'
status: 'done'
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

## Før flettingen

Fra gjennomgangen (BH14, ECH). PR-en flettes en annen dag før kl. 21:40, og:

- Første henting etter flettingen migrerer `ose.db` til versjon 5 gjennom `aapne_base`. Webserveren migrerer også når den starter (`_migrer_en_gang` i `src/app.py`). En prosess som åpner basen uten migrering, avviser den til en av dem har kjørt.
- En migrasjon går bare framover (AD-16). Ta en kopi av `data/db/ose.db` før første henting på versjon 5. Må PR-en tilbakestilles etterpå, må kopien legges tilbake, fordi koden på versjon 4 avviser en base på versjon 5.
- Henteinstruksjonen må sjekke versjon 5 i stedet for 4 (instruksjonen kl. 15:53, steg 4).

## Commitene

Grenen `4-3-sqlite-kilogg`, PR #46: `05f2ac3` spesifikasjonen og 4-3 til in-progress; `a87e9a2` migrasjonen, adapteren og testene; `b0628c8` rettingene fra gjennomgangen.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...a87e9a2`, med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 8) og Verification Gap (VG, 3). Rettingene står i `b0628c8`, og punktene i `deferred-work.md` i samme commit som denne triagen. Ingen funn må avgjøres av gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH, VG1 | Med `recursive_triggers` av, som er standard, slettet `INSERT OR REPLACE` en rad i `ki_logg` uten DELETE-triggeren. Testen slo på `recursive_triggers` og skjulte det | high | patch: triggeren `ki_logg_erstattes_ikke` (BEFORE INSERT, `RAISE(IGNORE)`) stopper en INSERT for et emne som finnes, som i 0003. `skriv` gir fortsatt `False`. `test_replace_erstatter_ikke_en_rad` prøver fire verb med og uten `recursive_triggers` |
| BH3, BH4, ECH | Basen sjekket ikke datoen eller at grunnlaget er JSON, og en rad den godtok, kunne gjøre `les_alle` ulesbar for alltid, fordi den ikke kan slettes | medium | patch: `dato IS date(dato)` og `json_valid(grunnlag) AND json_type(grunnlag) = 'object'` |
| BH5, BH6, ECH | Tom eller ukanonisk `symbol` og `melding_id`, tom `regelen`, ukjent `tjeneste`, og `seed` og `temperatur` av feil type ble godtatt av basen | medium | patch: CHECK for hver, de samme reglene som `KIRad` |
| VG2 | Ingen test så at `skriv` ruller tilbake etter en feil, eller avviser kallerens åpne transaksjon | medium | patch: `test_en_feil_rulles_tilbake`, `test_kallerens_aapne_transaksjon_avvises` |
| BH11, ECH | En ROLLBACK som feiler, skjulte den første feilen | low | patch: ROLLBACK i `try`, og den første feilen går videre |
| BH16 | Porttestene brukte `sqlite3.connect`, ikke `aapne_base` | low | patch: fixturen `logg_lager` åpner basen med `aapne_base` i `tmp_path` |
| VG3 | `test_klokka_maa_kunne_kalles` gjaldt bare `MinneKILogg` | low | patch: tar loggen fra `logg_lager` |
| BH12 | Regexene i `test_tabellen_lages_bare_i_migrasjonen` var ulike og så bare `src/*.py` | low | patch: én regex med `IF NOT EXISTS` og `rglob` |
| BH13 | Testen for «bare INSERT» så bare på kildeteksten | low | patch: `test_bare_begin_insert_og_commit` ser hva adapteren sender til basen |
| BH2 | Kommentaren i 0005 lovet mer enn triggerne gjør | low | patch: kommentaren sier at DROP og en senere migrasjon ikke stoppes av triggerne |
| BH7 | `besto = 0` med tekst var ikke forklart | low | patch: en tekst kontrollen stoppet, står med grunnen. Kommentar og `test_en_tekst_som_ikke_besto_staar_med_grunnen` |
| BH14, ECH | Ingen plan for tilbakestilling, og en prosess uten migrering avviser basen etter flettingen | low | patch: «Før flettingen» over |
| BH15 | Verification var tom | low | patch: fylt ut under |
| BH10 | En KI-rad kan ikke skrives i samme transaksjon som vurderingen | low | utsatt: `deferred-work.md`, tas i 10.2b |
| BH8 | Samme melding kan få én rad per dag | low | utsatt: `deferred-work.md`, plan A er utenfor v1 |
| BH9 | Adapteren sjekker ikke tilkoblingens `isolation_level` | avvist | som `SqliteVurderingslager`. `aapne_base` er den eneste veien inn, og porttestene bruker den |


## Verification

**Commands:**
- `uv run pytest -q` -- før 1721 bestått og 17 hoppet over på main (`a2f71ae`). 1760 og 17 på `a87e9a2`. Etter rettingene 1788 og 17 på `b0628c8`.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_kilogg_sqlite.py` og `tests/test_kilogg.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. C1–C3 ble først kjørt på `a87e9a2` og fanget alle, og så på nytt på `b0628c8` med CR1–CR4. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| C1 | tabellen lages utenfor migrasjonsløperen | `test_tabellen_lages_bare_i_migrasjonen` |
| C2 | skrivingen bruker `INSERT OR REPLACE` | `test_adapteren_skriver_bare_med_insert` |
| C3 | tabellen har ingen CHECK på emnet | `test_basen_sjekker_formen` |
| CR1 | ingen trigger mot REPLACE | `test_replace_erstatter_ikke_en_rad` |
| CR2 | datoen sjekkes ikke | `test_basen_sjekker_formen` |
| CR3 | grunnlaget sjekkes ikke som JSON | `test_basen_sjekker_formen` |
| CR4 | ingen ROLLBACK etter en feil | `test_en_feil_rulles_tilbake` |
