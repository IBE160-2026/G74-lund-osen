---
title: 'Story 1.4b: Konsumentene leser Kursrad'
type: 'refactor'
created: '2026-09-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f4bf940e32e5a9470c26d44c9c6aa9bd251fb249'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `signalberegning`, `markedsoversikt` og `aksjedetalj` leser EODHDs `dict`-nøkler og faller tilbake fra `adjusted_close` til `close` (`deferred-work.md`, fra 1.4a). AD-19 gjelder derfor bare ved porten.

**Approach:** De tre konsumentene og `graf.py` tar `Kursrad` og leser gjennom `Kursleser`. `app.py` gir dem `SnapshotLeser(kilde)`. Alt skjer i én kodeendring, fordi `beregn_signal` kalles av både `markedsoversikt` og `aksjedetalj`. Kilde: story 1.4b i `epics.md` slik den står 25.09.

## Boundaries & Constraints

**Always:**
- Konsumentene regner på `justert_slutt`, viser `slutt` som sluttkurs og leser `volum`. Ingen `.get()` og ingen fallback.
- `dato` er `date` hele veien. Malene skriver den som `YYYY-MM-DD`, slik de gjør i dag.
- Hele testsettet kjøres før og etter, og tallene føres i commit-meldingen.
- Kontrollregningen på ekte data gjøres før første kodeendring. Resultatene ligger i `data/`, og i repoet står bare antall like rader (regel 16).

**Never:**
- Ingen midlertidig oversettelse fra `dict` til `Kursrad` mellom konsumentene.
- `Kurskilde`, `MinneKilde` og `SnapshotKilde` blir stående (1.4c og 1.5).
- Sidens «data hentet» leses fortsatt fra `SnapshotKilde.tidsstempel()`. `sist_hentet` i visningen hører til 1.4c.
- Ingen API-kall.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Utbyttedag | `slutt` ≠ `justert_slutt` | Endring, signal og graf følger `justert_slutt`, og sluttkursen er `slutt` | – |
| Kort serie | færre rader enn `_nodvendige_dager` | Rad eller detalj uten signal, med grunnen i `mangler` | `ValueError` som i dag |
| Tomt symbol | `serie()` gir `[]` | Ingen rad. Appen navngir aksjen under «Uten data» | – |
| Uleselig symbol i øyeblikksbildet | én rad kan ikke oversettes | Symbolet er tomt (1.4a) og navngis under «Uten data» | – |

**Beslutninger 2026-09-25 (Marian og Joakim):**
- **Arbeidsflyt, alternativ B.** Arbeidet gjøres på grenen `1-4b`. Grenen pushes til GitHub etter hver mellomcommit, så arbeidet ikke bare ligger på én maskin. Aldri force-push (regel 7). Testkjøringen på GitHub går ved push til `main`, så en uferdig gren gir ikke rødt der.
- Trenger grenen noe fra `main` underveis, flettes `main` inn i grenen med merge, ikke rebase, så force-push aldri blir nødvendig.
- Dagsfila redigeres og committes bare på `main`. Grenen har bare endringene for storyen.
- Til slutt flettes grenen inn i `main` som én commit (squash), med `Co-authored-by` for Joakim (regel 20). Grenen blir liggende på GitHub etterpå, som historikk.
- Spesifikasjonen beholdes hel (omtrent 2 100 tokens). Kontrollregningen er et kontrollpunkt i selve storyen.

</frozen-after-approval>

## Code Map

- `src/signalberegning.py:79–90` -- `_justerte_kurser` (fallback), `_volumer` (`or 0`). `beregn_signal(rader: list[Kursrad])`
- `src/markedsoversikt.py:98–143, 158–173` -- `_justert` (fallback), `endring_i_prosent`, `bygg_rad` (`siste["date"]`, `siste["close"]`), `bygg_oversikt(kilde: Kursleser)`. `Rad.dato: date`
- `src/aksjedetalj.py:105–186` -- `_justert` (fallback), `_innenfor_vindu` (fanger `ValueError` fra datotekst; blir enkel datosammenligning), `bygg_punkter` (filteret for `None`-kurs forsvinner), `bygg_detalj(kilde: Kursleser)`. `Punkt.dato` og `Detalj.dato: date`
- `src/graf.py:39–40` -- `forste_dato`, `siste_dato: date`
- `src/app.py:23–71` -- `hent_kilde()` beholdes. Rutene lager `SnapshotLeser(kilde)` og gir den til konsumentene. `hentet=kilde.tidsstempel()` uendret. `mangler` (linje 37) virker uendret på tomme serier
- `src/kursdata.py` -- `Kursrad`, `Kursleser`, `SnapshotLeser` gjenbrukes uendret
- `tests/test_kurslager.py:492–516` -- `TestKurskildeErPaaVeiUt.TILLATT` strammes til `set()`
- Tester som testet fallbacken og fjernes: `test_markedsoversikt::test_faller_tilbake_til_close_naar_justert_mangler`, `test_aksjedetalj::test_taaler_rader_uten_kurs`
- Testtall 25.09, før endringen: 378 (aksjedetalj 20, app 18, graf 13, markedsoversikt 25, signalberegning 15)
- Øyeblikksbildet for kontrollregningen: `data/kurser-raa-2026-09-24.json`, det nyeste i dag. Det låses ved navn, så kveldens henting ikke bytter det ut

## Tasks & Acceptance

**Execution:**
- [x] `data/kontrollregning_1_4b.py` (ikke i repoet) -- bygg oversikten og de 15 detaljene med graf fra den låste fila, og lagre alle felt med datoer som ISO-tekst, pluss HTML for `/` og de 15 `/aksje/<symbol>`. Kjøres før endringen (`-foer.json`) og etter (`-etter.json`), og sammenligningen skriver bare antall -- kontrollpunktet fra 25.09
- [x] `src/signalberegning.py`, `src/markedsoversikt.py`, `src/aksjedetalj.py`, `src/graf.py` -- `Kursrad` og `Kursleser`, fallbacken fjernet, docstringer rettet (de nevner `Kurskilde`/`adjusted_close`) -- AD-19
- [x] `src/app.py` -- `SnapshotLeser` til konsumentene -- AD-3
- [x] `tests/test_signalberegning.py`, `test_markedsoversikt.py`, `test_aksjedetalj.py`, `test_app.py`, `test_graf.py` -- `serie()` gir `Kursrad`. `MinneKilde` byttes med `MinneKurslager`; i `test_app` monteres en `SnapshotKilde` med `hentet`, så appen prøves gjennom den ekte oversettelsen. De to fallback-testene erstattes av tester der `slutt` ≠ `justert_slutt` for endring, signal og grafpunkter
- [x] `tests/test_konsumentene.py` (ny) -- de fire kjernemodulene importerer verken `sqlite3`, `pathlib` eller `Kurskilde`, og kildeteksten har ingen EODHD-nøkler (`"adjusted_close"`, `"close"`, `"volume"`, `"date"`). Testen krever at fallbacken er borte

**Acceptance Criteria:**
- Given hele testsettet, when det kjøres før og etter, then er begge grønne, og tallene står i commit-meldingen
- Given tre mutanter som bruker `slutt` i stedet for `justert_slutt` (i `signalberegning`, `endring_i_prosent` og `bygg_punkter`), when testene kjøres, then feiler minst én test for hver
- Given kontrollregningen før og etter, when de sammenlignes, then er 15 av 15 rader i oversikten, 15 av 15 detaljer og 16 av 16 sider like
- Given `grep` etter `adjusted_close`, `rad.get(` og `rad[` i de fire kjernemodulene, when det kjøres, then er det ingen treff

## Design Notes

**Trinn:**
1. Planen er godkjent 25.09. Når byggingen starter: sett 1-4b til `in-progress`, lag grenen `1-4b` fra `main`, og kjør kontrollregningen før første kodeendring.
2. Gjør kode- og testendringen på grenen, med mellomcommits som pushes.
3. Kjør kontrollregningen etter endringen, og mutantene. Deretter gjennomgangen (bmad-build steg 4). Når alt er grønt, flettes grenen inn i `main` som én commit (squash), med testtallene og `Co-authored-by` for Joakim. Til slutt settes 1-4b til `review` i sprint-statusen.

Trinn 1 og 3 rekker én økt hver. Trinn 2 er det store: storyen anslår at testendringen er større enn kodeendringen.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: alt grønt; 378 før
- `uv run python data/kontrollregning_1_4b.py --sammenlign` -- expected: bare antall, alle like
- `grep -nE 'adjusted_close|rad\.get\(|rad\[' src/signalberegning.py src/markedsoversikt.py src/aksjedetalj.py src/graf.py` -- expected: ingen treff

## Review Triage Log

| # | Kilde | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|---|
| 1 | blind, edge, verif. | Et øyeblikksbilde med `hentet` som ikke kan leses, viser nå «Ingen kursdata funnet i data/» uten rader og uten «data hentet», og detaljen gir 404. Ingen apptest låser det | low | Følger av 1.4a: `SnapshotLeser` gjør da hele bildet manglende, og 1.4b gir den til konsumentene. Nås ikke i dag: `nyeste_snapshot` foretrekker `kurser-`, og de fila har `hentet` med tidssone (kontrollregningen ga 15 rader). Rettingen er en test, ikke ny kode | patch |
| 2 | blind, edge | Utbyttetestene i `test_markedsoversikt` og `test_aksjedetalj` sammenligner sluttkursen med `justert[-1]`, som er lik `slutt[-1]` | low | Riktig: testene kan ikke skille de to. `test_sluttkursen_er_slutt_ikke_justert` og `test_viser_ujustert_sluttkurs` fanger en slik mutant. Siste dag er lik i ekte data, så fixturen står | patch |
| 3 | blind | `signalberegning` importerer `kursdata`, som importerer `pathlib`, og testen ser bare direkte importer | false | Testen lover bare direkte importer («importere lageret selv»). `markedsoversikt` og `aksjedetalj` importerte `kursdata` før 1.4b også. Ingen av de fire modulene gjør I/O | avvist |
| 4 | blind | Docstringene om `Kurskilde` (`kursdata.py`, `test_kurslager.py`) sier «fjernes i 1.4» | false | «1.4» er hele 1.4-rekken. Fjerningen er 1.4c (`epics.md:697`), og den tar `Kurskilde`, `MinneKilde` og `TestKurskildeErPaaVeiUt` | avvist |
| 5 | blind | Spesifikasjonen nevner ikke `test_kurslager.py` og har ikke resultatene | false | Code Map nevner `tests/test_kurslager.py:492–516`. Resultatene står i commit-meldingen, som AC-en krever, og en rettelse ville endret spesifikasjonen | avvist |
| 6 | blind | `"2026-11-19" in html` i detaljtesten følger av grafteksten, så datoen i overskriften prøves ikke for seg | low | Riktig: grafteksten «2026-09-01 til 2026-11-19» inneholder datoen. Rettingen er én påstand | patch |
| 7 | blind, edge | Importvaktene er ulike: regex i `test_kurslager`, AST i `test_konsumentene`, og `import kursdata` med `kursdata.Kurskilde` slipper gjennom | low | Ingen modul i `src/` gjør `import kursdata`. Regex-vakten fjernes i 1.4c. En samlet vakt er mer kode | avvist |
| 8 | blind | `SnapshotLeser` bygges ved hver forespørsel | low | `hent_kilde()` leser allerede fila ved hver forespørsel. 15 serier, ingen målt kostnad | avvist |
| 9 | blind | Docstringen i `test_aksjedetalj.py:92` sier fortsatt `close`/`adjusted_close` | low | Riktig, og rettingen er tekst | patch |
| 10 | edge, verif. | `test_uleselig_symbol_navngis_i_fotnoten` passerer også om DNB vises som rad | low | Riktig: «DNB Bank» står i lenken i raden. Lesertestene i `test_snapshotleser.py` dekker at raden faller ut. Rettingen er én påstand | patch |
| 11 | edge | Testhjelperne `zip`-er lister som kan ha ulik lengde | low | Ingen test gir ulike lengder i dag. Rettingen er en ny vakt i hjelperne | avvist |
