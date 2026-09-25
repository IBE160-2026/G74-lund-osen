---
title: 'Story 1.5: SnapshotKilde ut av kursdata.py'
type: 'refactor'
created: '2026-09-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b0243b61533ac917a863ba19a19700f42d605bc7'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Portmodulen `kursdata.py` gjør I/O: den importerer `json`, `pathlib` og `re`, `SnapshotKilde.fra_fil` leser fil, og `nyeste_snapshot` globber katalogen. `app.py` kaller `nyeste_snapshot()` direkte, altså utenom enhver port. Spinen sier at `kursdata.py` ikke oppfyller portregelen, og `epics.md` fører det som «Gjenstående brudd».

**Approach:** Alt som leser filer, flyttes til en ny skallmodul `src/lagring_fil.py`, som spinen navngir, og oversettelsen fra EODHDs feltnavn flyttes til `src/eodhd.py`. `app.py` får en `Kursleser` derfra gjennom én funksjon og kjenner ikke lenger `nyeste_snapshot`. Oppførselen er uendret. Kilde: story 1.5 i `epics.md` slik den står 25.09.

## Boundaries & Constraints

**Always:**
- Ren flytting. Utvalgsregelen i `nyeste_snapshot` flyttes ordrett: datoen avgjør alene, og `KURSPREFIKS` vinner ved lik dato.
- `kursrad_fra_eodhd` er fortsatt den ene oversetteren (AD-19). Den flytter, men endres ikke.
- Hele testsettet kjøres før og etter, og tallene føres i commit-meldingen.
- Kontrollregningen kjøres før første kodeendring og etter, med samme skript uendret. Alt skal være likt, også tidsstemplene. I repoet står bare antall (regel 16).

**Never:**
- Appen bytter ikke til SQLite, og meldingen «Ingen kursdata funnet i data/» endres ikke (se beslutningene).
- Ingen endring i formatet på øyeblikksbildene, i filnavnene eller i hva `fetch_prices.py` skriver.
- Ingen API-kall.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Vanlig | `data/` med øyeblikksbilder | Samme sider som før, byte for byte | – |
| Ingen fil | tom eller manglende katalog | Porten gir `None`, og siden viser meldingen som i dag | – |
| Lik dato | `signaltest-` og `kurser-` samme dag | `kurser-` velges | – |
| Lik dato uten kursfil | to andre prefikser | Den alfabetisk første, som i dag | – |

**Beslutninger 2026-09-25 (Marian og Joakim):**
- **Arbeidsflyt som 1.4b og 1.4c.** Grenen `1-5` fra `main`, mellomcommits som pushes, aldri force-push (regel 7). Trenger grenen noe fra `main`, flettes det inn med merge. Dagsfila og sprint-statusen redigeres og committes bare på `main`. Pull request mot `main`, stopp før flettingen og vent på ja, og squash med testtallene, kontrollregningen og `Co-authored-by` for Joakim (regel 20). Grenen blir liggende.
- **Etter flettingen, på `main`:** spinens avsnitt om at `kursdata.py` ikke oppfyller portregelen, og «Gjenstående brudd» i `epics.md`, merkes lukket med squash-commiten, som AD-3-bruddet i 1.4c.
- **Meldingen «Ingen kursdata funnet i data/» rettes ikke i 1.5.** Storyen er en ren flytting, og kontrollregningen krever at alt er likt. Henvisningen i `deferred-work.md` er rettet til 2.2, og hullet i Epic 2 er ført i `epics.md` (`d9c4561`).
- **`kursrad_fra_eodhd` flytter ut av `kursdata.py`, til en egen modul `src/eodhd.py`,** sammen med `_dato_fra_tekst`, som bare den bruker. AD-19 sier «Adapteren oversetter fra kildens feltnavn», og spinens konvensjonstabell sier «Kildens feltnavn stopper i adapteren». Egen modul og ikke `lagring_fil.py`, fordi formatet er EODHDs og ikke filens: i dag kommer radene fra øyeblikksbildet, og i Epic 2 fra API-svaret i hentekommandoen. I `lagring_fil.py` måtte hentekommandoen importert filadapteren for å oversette et API-svar. `eodhd.py` gjør ingen I/O. `UgyldigKursrad` blir i `kursdata.py`, fordi `Kursrad` reiser den.
- **Vaktene:** vakten mot EODHD-feltnavn i `test_konsumentene.py` utvides til `kursdata.py`. AST-vakten sjekker at `kursdata.py` verken importerer `json`, `pathlib`, `lagring_fil`, `lagring_sqlite` eller `eodhd`: porten importerer ingen adapter. Det er grunnen til at `SnapshotLeser` flytter, og vakten holder den.
- **Spesifikasjonen beholdes hel.**

</frozen-after-approval>

## Code Map

- `src/kursdata.py:15–24, 219–243, 285–420` (også `_dato_fra_tekst` og `kursrad_fra_eodhd` på 245–282) -- ut: `json`, `re`, `pathlib`, `PROSJEKTROT`, `DATA_KATALOG`, `SnapshotKilde`, `_hentet_fra_tekst`, `SnapshotLeser`, `KURSPREFIKS`, `_SNAPSHOT_MONSTER` og `nyeste_snapshot`. Blir: `Aksje`, `AKSJEUNIVERS`, `Kursrad`, `UgyldigKursrad`, `Kursleser`, `Kurslager`, `kontroller_skriving` og `MinneKurslager`. `_dato_fra_tekst` og `kursrad_fra_eodhd` går til `src/eodhd.py`. Modul-docstringen rettes
- `src/lagring_fil.py` (ny) -- det som flyttes, uendret, pluss én funksjon som gir en `Kursleser` for det nyeste øyeblikksbildet i en katalog, eller `None`. `SnapshotLeser` følger `SnapshotKilde`, fordi porten ellers ville importert adapteren
- `src/eodhd.py` (ny) -- `kursrad_fra_eodhd` og `_dato_fra_tekst`, uendret. Importerer `Kursrad` og `UgyldigKursrad` fra `kursdata`. `lagring_fil.SnapshotLeser` bruker den
- `src/app.py:19–40` -- `hent_kilde()` fjernes. `hent_leser()` beholdes som monteringspunkt og kaller funksjonen i `lagring_fil`. `app.py` importerer verken `SnapshotKilde` eller `nyeste_snapshot`
- `src/fetch_prices.py:15, 29, 124, 138` -- importerer `DATA_KATALOG`, `KURSPREFIKS` og `PROSJEKTROT` fra `lagring_fil`. Docstringene nevner `kursdata.SnapshotKilde`
- Tester som importerer det som flyttes: `test_kursdata.py` (`SnapshotKilde`, `nyeste_snapshot`, `KURSPREFIKS`, filtestene), `test_fetch_prices.py:14`, `test_app.py:16, 50–62` (`monter` monterer `hent_kilde`; blir `hent_leser`), `test_kurslager.py:30–31`, `test_snapshotleser.py:21–22` (også `kursrad_fra_eodhd` og `UgyldigKursrad`). Filtestene i `test_kursdata.py` flyttes til en ny `tests/test_lagring_fil.py`
- `tests/test_konsumentene.py` -- AST-hjelperne gjenbrukes, og vakten mot EODHD-feltnavn får `kursdata.py` med
- `ARCHITECTURE-SPINE.md:46–54` og `epics.md:168–170` -- merkes lukket etter flettingen
- Testtall 25.09 før endringen: 416
- Kontrollregningen: `data/kontrollregning_1_5.py` mot `data/kurser-raa-2026-09-24.json`, samme fil som i 1.4b og 1.4c

## Tasks & Acceptance

**Execution:**
- [x] `data/kontrollregning_1_5.py` (ikke i repoet) -- bygger på `kontrollregning_1_4c.py`, men monterer `app.hent_leser`, som finnes både før og etter, og importerer `SnapshotKilde` og `SnapshotLeser` fra `lagring_fil` med `kursdata` som reserve. Da kjører samme skript uendret før og etter. Sammenligningen krever at alt er likt, uten å ta ut noe. Kjøres før første kodeendring
- [x] `src/lagring_fil.py`, `src/eodhd.py`, `src/kursdata.py` -- flyttingen -- AD-1, AD-6, AD-19
- [x] `src/app.py`, `src/fetch_prices.py` -- importene og `hent_leser` -- AD-2, AD-3
- [x] Testene over -- importene rettes, og filtestene flyttes til `tests/test_lagring_fil.py`
- [x] Nye vakter: `kursdata.py` importerer verken `json`, `pathlib`, `lagring_fil`, `lagring_sqlite` eller `eodhd` (AST), og vakten mot EODHD-feltnavn dekker `kursdata.py`. `app.py` kaller ikke `nyeste_snapshot` og importerer den ikke. `app.hent_leser()` gir en `Kursleser` fra en katalog med en fil, og `None` fra en tom katalog
- [ ] Etter flettingen, på `main`: spinen og `epics.md` merker bruddet lukket med squash-commiten, og spinens lagtabell får `lagring_fil.py` i skallet. Egen commit

**Acceptance Criteria:**
- Given hele testsettet, when det kjøres før og etter, then er begge grønne, og tallene står i commit-meldingen
- Given en mutant der `nyeste_snapshot` velger med `max` over tuplene `(dato, sti)`, when testene kjøres, then feiler minst én test (`signaltest-` ville vunnet over `kurser-` ved lik dato)
- Given en mutant der `app.py` kaller `nyeste_snapshot()` direkte, when testene kjøres, then feiler vakten
- Given kontrollregningen før og etter, when de sammenlignes, then er 15 av 15 rader, 15 av 15 detaljer og 16 av 16 sider like, også tidsstemplene
- Given en mutant som legger `"adjusted_close"` tilbake i `kursdata.py`, eller `from lagring_fil import ...` der, when testene kjøres, then feiler vakten
- Given `grep -nE "^import (json|re)|pathlib|adjusted_close" src/kursdata.py`, when det kjøres, then er det ingen treff

## Implementation Notes

- Kontrollregningen før er kjørt på grenen før første kodeendring (`data/kontrollregning-1-5-foer.json`, 15 rader, 15 detaljer, 16 sider med 200). Skriptet `data/kontrollregning_1_5.py` har sha256 som begynner på `4eb4a0a6966d15bc`. Verken skriptet eller før-fila skal endres eller kjøres på nytt med `--foer`; etter flyttingen kjøres bare `--etter` og `--sammenlign`.
- `lagring_fil.nyeste_leser(katalog=None)` er den ene nye funksjonen. Uten argument leses `DATA_KATALOG` ved kallet, så en test kan peke den mot en annen katalog. `app.hent_leser()` returnerer den.
- Alt som flyttet, er likt definisjon for definisjon (sammenlignet med `ast.get_source_segment` mot `b0243b6`). Eneste endring i det som ble igjen: `Kurslager`-docstringen sier «den justerte kursen» i stedet for `adjusted_close`, så vakten mot EODHD-feltnavn kan dekke `kursdata.py`.
- Testtall: 416 før, 424 etter. Filtestene er flyttet til `tests/test_lagring_fil.py`.
- Kontrollregningen etter, med samme skript (sha256 `4eb4a0a6966d15bc…`, uendret): 15 av 15 rader, 15 av 15 detaljer og 16 av 16 sider like, rekkefølgen lik. Ingenting tatt ut av sammenligningen.
- Mutanter: `max` over `(dato, sti)` (2 feiler), `app.py` kaller `nyeste_snapshot()` (3), `"adjusted_close"` i `kursdata.py` (2), `kursdata.py` importerer en adapter (vakten `test_porten_importerer_verken_io_eller_adapter` feiler; en import på modulnivå gir i tillegg sirkulær import). Alle fanget.
- Etter gjennomgangen (triageloggen, rad 4, 6 og 11): vakten for `app.py` forbyr også `SnapshotLeser` og `DATA_KATALOG`, vakten mot EODHD-strenger dekker også `lagring_fil.py`, `lagring_sqlite.py` og `app.py`, og to modul-docstringer i testene er rettet. Testtall etter rettelsene: 427 (3 nye parametre). En femte mutant, der `app.py` gir `DATA_KATALOG` til `nyeste_leser` selv, fanges av vakten. Kontrollregningen etter rettelsene: 15 av 15, 15 av 15 og 16 av 16 like, skriptet uendret.

## Spec Change Log

## Review Triage Log

| # | Kilde | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|---|
| 1 | edge, blind | Et nyeste øyeblikksbilde med ugyldig JSON, eller en liste øverst, gir 500 på alle sidene | low | Fantes før 1.5: `hent_kilde()` kalte samme `SnapshotKilde.fra_fil` (`b0243b6`, `kursdata.py:231–236`). Flyttingen endrer ikke oppførselen. `fetch_prices` skriver fila selv, og rettingen er en ny vakt. *Rettet 2026-09-25 etter flettingen: ført som utsatt i `deferred-work.md`, som overskriftsdatoen i 1.4c* | defer |
| 2 | edge | En katalog som heter `*-raa-*.json`, eller en fil som slettes mellom glob og lesing, gir unntak | low | Fantes før 1.5 (`nyeste_snapshot` er flyttet ordrett). Ingen lovlig vei lager en slik katalog. Rettingen er en ny vakt | avvist |
| 3 | blind | Skillet mellom «ingen fil» og «fil uten lesbare data» som 1.4c-spesifikasjonen la til 1.5, mangler | false | Avgjort 25.09 kl. 19:42: meldingen rettes ikke i 1.5, og henvisningen i `deferred-work.md` er rettet til 2.2 (`d9c4561`). Det står i beslutningene i denne spesifikasjonen | avvist |
| 4 | blind | «Kildens feltnavn stopper her» i `eodhd.py` håndheves ikke utenfor kjernen og porten | low | Riktig. `lagring_fil.py`, `lagring_sqlite.py` og `app.py` har ingen av nøklene i dag, så vakten kan dekke dem uten ny kode. `fetch_prices.py` er EODHD-adapteren for nettet og bruker `'date'` | patch |
| 5 | blind | Porten kan gjøre I/O med `open(...)` uten import, og vakten ser bare importer | low | Ingen `open` i `kursdata.py`. Vakten holder det storyen krever («importerer verken `json` eller `pathlib`») | avvist |
| 6 | blind | Vakten for `app.py` forbyr ikke `SnapshotLeser` eller `DATA_KATALOG` | low | Riktig: `app.py` kunne valgt øyeblikksbilde selv og bestått. Rettingen er to navn i en mengde | patch |
| 7 | blind | `nyeste_snapshot` binder `DATA_KATALOG` ved definisjon, `nyeste_leser` ved kall | low | Standardargumentet fantes før 1.5. Testene gir `nyeste_snapshot` katalogen eksplisitt | avvist |
| 8 | blind | `PROSJEKTROT` ligger i filadapteren | low | Plassert der av spesifikasjonen (Code Map). `fetch_prices` importerer `lagring_fil` uansett for `DATA_KATALOG` og `KURSPREFIKS` | avvist |
| 9 | blind | Formatet leses i `lagring_fil.py` og skrives i `fetch_prices.py`, og docstringen sier «slik signaltesten skrev det» | low | Skillet og docstringen fantes før 1.5. `lagring_fil.py` sier bare at lesingen ligger der, og det stemmer | avvist |
| 10 | blind | `eodhd.py` har ingen egen testfil | low | Testene for oversetteren finnes og kjører (`test_snapshotleser.py`). Plasseringen er kosmetisk | avvist |
| 11 | blind | Modul-docstringene i `test_app.py` og `test_snapshotleser.py` er ikke oppdatert | low | Riktig: `TestHentLeser` leser en katalog, og oversetteren ligger nå i `eodhd.py`. Rettingen er tekst | patch |
| 12 | blind | Hjelperen `eodhd` i `test_app.py` har samme navn som den nye modulen | low | Ingen import av modulen i den fila. Kollisjonen er hypotetisk | avvist |
| 13 | blind | `test_gir_kursleser_fra_en_katalog_med_en_fil` sjekker bare antall rader | low | Valget av nyeste fil og `sist_hentet` prøves i `test_lagring_fil.py` og `test_snapshotleser.py` | avvist |
## Design Notes

**Trinn:** (1) Etter ja: spesifikasjonen `ready-for-dev` på `main`, 1-5 `in-progress`, grenen `1-5`, kontrollregningen før. (2) Flyttingen og testene på grenen, mellomcommits som pushes. (3) Kontrollregningen etter, mutantene og gjennomgangen (bmad-build steg 4), så pull request. Stopp før flettingen med testtallene, kontrollregningen og utfallet av gjennomgangen, og vent på ja. (4) Squash, så spinen og `epics.md`, så 1-5 til `review` sammen med dagsfila.

**Hvorfor `SnapshotLeser` også flytter:** den tar en `SnapshotKilde`. Blir den i `kursdata.py`, må porten importere adapteren, og da peker avhengigheten feil vei. Den gjør selv ingen I/O.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: alt grønt; 416 før
- `uv run python data/kontrollregning_1_5.py --sammenlign` -- expected: bare antall, alle like
- `grep -rn "nyeste_snapshot\|SnapshotKilde" src/app.py` -- expected: ingen treff
