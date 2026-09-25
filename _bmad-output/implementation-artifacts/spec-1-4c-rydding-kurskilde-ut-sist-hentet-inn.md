---
title: 'Story 1.4c: Rydding — Kurskilde ut, sist_hentet inn'
type: 'refactor'
created: '2026-09-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'fcc48f95b9f8e3a86abc6f0381da37b049e61df9'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kursdataene har fortsatt to porter, `Kurskilde` ved siden av `Kurslager` (AD-3-bruddet fra valg b i 1.2), og siden viser «data hentet» som de ti første tegnene av øyeblikksbildets `hentet`. Viste den det nyeste tidspunktet, ville en side med én fersk rad og fjorten foreldede sett fersk ut (FR-101, endret 2026-09-23).

**Approach:** `Kurskilde`, `MinneKilde` og `TestKurskildeErPaaVeiUt` fjernes. Oversikten leser `sist_hentet` per symbol gjennom `Kursleser`: sidens tidsstempel er det eldste blant symbolene som vises, og en rad som er eldre enn den nyeste, viser sitt eget under selskapsnavnet. Tidsstempler vises i norsk tid. Kilde: story 1.4c i `epics.md` slik den står 25.09.

## Boundaries & Constraints

**Always:**
- Fem kolonner (FR-101). Radens tidsstempel står i selskapscellen, ikke i en sjette kolonne.
- Tid er UTC i modellen og blir norsk tid (`Europe/Oslo`) først i visningen (AD-20).
- Hele testsettet kjøres før og etter, og tallene føres i commit-meldingen.
- Kontrollregningen gjøres før første kodeendring og etter. Kursene, endringene og signalene skal være like, og bare tidsstemplene skal endre seg. I repoet står bare antall (regel 16).
- `grep` etter `Kurskilde`, `MinneKilde` og `TestKurskildeErPaaVeiUt` i `src/` og `tests/` gir ingen treff.

**Never:**
- `SnapshotKilde` og I/O-en i `kursdata.py` blir stående (1.5). `SnapshotKilde.tidsstempel()` og `.serie()` beholdes, fordi `test_kursdata` og `test_fetch_prices` bruker dem.
- Den misvisende meldingen når `hentet` ikke kan leses (`deferred-work.md`), rettes ikke her. Den venter til 1.5.
- Ingen API-kall.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Alle like ferske | øyeblikksbildet, én `hentet` | Sidens tidsstempel er `hentet` i norsk tid. Ingen rad viser eget | – |
| Én foreldet rad | to symboler, ulik `sist_hentet` | Siden viser det eldste. Den eldste raden viser sitt eget under navnet. Den ferske viser ingenting | – |
| Over midnatt, sommertid | `hentet` 2026-09-24T22:30Z | `2026-09-25 kl. 00.30` | – |
| Vintertid (etter 25.10) | `hentet` 2026-11-16T22:30Z | `2026-11-16 kl. 23.30` | – |
| Uleselig `hentet` | `SnapshotLeser` gir ingen rader | Som i dag: ingen «data hentet» (låst av `test_uleselig_hentet_...`) | – |

**Beslutninger 2026-09-25 (Marian og Joakim):**
- **Arbeidsflyt som 1.4b.** Grenen `1-4c` fra `main`, mellomcommits som pushes, aldri force-push (regel 7). Trenger grenen noe fra `main`, flettes det inn med merge, ikke rebase. Dagsfila og sprint-statusen redigeres og committes bare på `main`. Pull request før flettingen, og grenen flettes inn som én commit (squash) med testtallene, kontrollregningen og `Co-authored-by` for Joakim (regel 20). Grenen blir liggende på GitHub.
- **Den misvisende meldingen venter til 1.5.** 1.4c endrer hvor sidens tidsstempel kommer fra, men ikke når siden er tom: meldingen står i `{% else %}` til `{% if rader %}`, og en uleselig `hentet` gir ingen rader både før og etter. I 1.5 flytter lesingen ut av `kursdata.py`, og det er der «ingen fil» og «fil uten lesbare data» kan skilles.
- **Formatet er dato og klokkeslett i norsk tid,** `ÅÅÅÅ-MM-DD kl. TT.MM`, for eksempel `2026-09-24 kl. 20.05`. Det gjelder sidens tidsstempel og radens.
- **Aksjedetaljen viser symbolets egen `sist_hentet`** i norsk tid, i samme format.
- **Spesifikasjonen beholdes hel** (omtrent 2 500 tokens).
- **Vintertid prøves.** Sommertiden slutter 25.10, og demonstrasjonen er anslått til uke 45 (PRD §7). En test krever at `2026-11-16T22:30Z` vises som `2026-11-16 kl. 23.30`, og en fjerde mutant med fast +2 timer i stedet for `Europe/Oslo` skal fanges.

</frozen-after-approval>

## Code Map

- `src/kursdata.py:1–14, 150, 219–253` -- modul-docstringen (to porter, bruddet), `Kurslager`-docstringen («Erstatter Kurskilde i 1.4»), `Kurskilde` og `MinneKilde` fjernes. `Kursleser.sist_hentet` og `SnapshotLeser` gjenbrukes uendret
- `src/markedsoversikt.py:68–83, 152–167` -- `Rad` får `sist_hentet: datetime` fra `kilde.sist_hentet(symbol)` i `bygg_oversikt`. Ny ren funksjon for sidens tidsstempel (eldste) og for om en rad er eldre enn den nyeste. Formatet i norsk tid som ren funksjon (`zoneinfo`, ingen I/O)
- `src/app.py` -- ny `hent_leser()` som pakker `hent_kilde()` i `SnapshotLeser`, så testene kan montere et `MinneKurslager` med ulike tider. `hent_kilde()` beholdes (kontrollregningen monterer den). `kilde.tidsstempel()` brukes ikke lenger. Filter for norsk tid til malene. Docstringen rettes
- `src/templates/index.html` -- sidens tidsstempel fra modellen, radens tidsstempel under navnet i `td.selskap`
- `src/templates/aksje.html:68` -- `hentet[:10]` byttes med symbolets `sist_hentet` i norsk tid
- `tests/test_kursdata.py:14, 43–54` -- de to `MinneKilde`-testene fjernes
- `tests/test_kurslager.py:15–17, 492–517` -- avsnittet i modul-docstringen og `TestKurskildeErPaaVeiUt` fjernes
- `tests/test_konsumentene.py:62–65` -- `test_importerer_ikke_kurskilde` (4 parametre) fjernes; klassen finnes ikke lenger
- `tests/test_app.py:169–175` -- `test_data_hentet_leses_fra_oeyeblikksbildet` skrives om til norsk tid
- `ARCHITECTURE-SPINE.md:115–116, 290` -- AD-3: bruddet lukket med commit. Konvensjonsraden nevner `MinneKilde` som port-dobbel; blir `MinneKurslager`
- `epics.md:520` (1.2-merknaden) -- bruddet lukket med commit
- Testtall 25.09 før endringen: 408. Åtte tester fjernes med `Kurskilde` og `MinneKilde`
- Øyeblikksbildet for kontrollregningen: `data/kurser-raa-2026-09-24.json`, samme som i 1.4b

## Tasks & Acceptance

**Execution:**
- [x] `data/kontrollregning_1_4c.py` (ikke i repoet) -- kopi av `kontrollregning_1_4b.py` som bruker `SnapshotLeser` både før og etter, og skriver `-1-4c-foer.json` og `-1-4c-etter.json`. Sammenligningen skriver antall like to ganger: med alt, og med tidsstemplene tatt ut (feltet `sist_hentet` og «data hentet …» og radtidsstempelet i HTML-en). Kjøres før første kodeendring
- [x] `src/kursdata.py` -- `Kurskilde` og `MinneKilde` ut, docstringene rettet -- AD-3
- [x] `src/markedsoversikt.py`, `src/app.py`, `src/templates/index.html` og `aksje.html` -- `sist_hentet` inn, norsk tid -- FR-101, AD-15, AD-20
- [x] `tests/test_kursdata.py`, `tests/test_kurslager.py`, `tests/test_konsumentene.py` -- testene for `Kurskilde` og `MinneKilde` ut
- [x] `tests/test_markedsoversikt.py`, `tests/test_app.py` -- nye tester for matrisen over: eldste vinner, eget tidsstempel på den eldste raden og ikke på den ferske, fem kolonner, norsk tid over midnatt og i vintertid, og detaljens tidsstempel
- [x] Etter flettingen, på `main`: spinen, `epics.md` og arkitekturmemloggen merker AD-3-bruddet lukket med squash-commiten. Egen commit (`cd97164`)

**Acceptance Criteria:**
- Given hele testsettet, when det kjøres før og etter, then er begge grønne, og tallene står i commit-meldingen
- Given fire mutanter (sidens tidsstempel er det nyeste, UTC vises i stedet for norsk tid, radens tidsstempel vises aldri, fast +2 timer i stedet for `Europe/Oslo`), when testene kjøres, then feiler minst én test for hver
- Given kontrollregningen før og etter, when de sammenlignes med tidsstemplene tatt ut, then er 15 av 15 rader, 15 av 15 detaljer og 16 av 16 sider like. Med tidsstemplene med er forskjellen bare i dem
- Given `grep -rn "Kurskilde\|MinneKilde\|TestKurskildeErPaaVeiUt" src tests`, when det kjøres, then er det ingen treff

## Implementation Notes

- `Rad.sist_hentet` er `datetime | None = None`, ikke `datetime`, så `bygg_rad` kan kalles uten tid i de eldre testene. `bygg_oversikt` setter den alltid.
- Nye rene funksjoner i `markedsoversikt.py`: `sidens_tidsstempel` (eldste), `eldre_enn_nyeste` (symbolene som viser egen tid) og `norsk_tid` (`ZoneInfo("Europe/Oslo")`), som `app.py` registrerer som Jinja-filter.
- Radens tid står som `<span class="hentet"><br><small>hentet …</small></span>` i `td.selskap`, uten ny CSS.
- Testtall: 408 før, 416 etter (8 fjernet, 16 nye).
- Kontrollregningen mot `kurser-raa-2026-09-24.json`: med alt er 0 av 15 rader, 15 av 15 detaljer og 0 av 16 sider like. Uten tidsstemplene er 15 av 15, 15 av 15 og 16 av 16 like, og rekkefølgen er lik. Ingen rad viser egen tid på ekte data.
- Mutanter, én om gangen: sidens tid er den nyeste (2 feiler), UTC i stedet for norsk tid (11), radens tid vises aldri (1), fast +2 timer (3). Alle fanget.
- Etter gjennomgangen (rad 5 og 6 i triageloggen): radens tid har egen CSS-regel (`td.selskap .hentet`, dempet, normal vekt) i stedet for `<br><small>`, og docstringen til `Rad.sist_hentet` navngir lesekontrakten. 416 grønne, alle fire mutanter fanget.
- Kontrollregningen etter rettelsene, uten tidsstemplene: 15 av 15 rader, 15 av 15 detaljer og 15 av 16 sider like. Den ene forskjellen er CSS-regelen for radens tidsstempel i `<style>` på `/`; ingenting annet skiller. Sammenligningen ble ikke endret etter kjøringen før.

## Spec Change Log

## Review Triage Log

| # | Kilde | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|---|
| 1 | blind | Spinen og `epics.md` er ikke oppdatert, og spinens «Porter»-rad (linje 46) nevner fortsatt `MinneKilde` | low | Spinen og `epics.md` er en planlagt oppgave etter flettingen, fordi de skal ha squash-commiten. Linje 46 manglet i Code Map; den tas i samme commit | patch (etter flettingen) |
| 2 | blind | `norsk_tid` er visningskode i kjernen | false | AD-1 forbyr I/O, og `zoneinfo` er ikke I/O. `markedsoversikt` kjenner fortsatt ingen HTML, og Code Map plasserte funksjonen der. Ingen kaller eller regel brytes | avvist |
| 3 | blind, edge | `norsk_tid` tar imot en tid uten sone og viser den som lokal tid | low | Nås ikke: `kontroller_skriving` gir UTC, `_hentet_fra_tekst` avviser tid uten sone, og SQLite lagrer tiden med offset. Rettingen er en ny vakt | avvist |
| 4 | blind | Med én fersk og fjorten foreldede gjentar fjorten rader sidens tid, og den ferske raden har ingen tid | low | Riktig, men det er FR-101 ordrett («En rad med eldre tidsstempel enn det nyeste viser sitt eget»). En endring er en PRD-endring | avvist, nevnt for gruppa |
| 5 | blind | Radens tid har ingen CSS og arver `font-weight: 500` fra `td.selskap` | low | Riktig. Synes først når tidene er ulike (Epic 2). Rettingen er én CSS-regel | patch |
| 6 | blind, edge | Docstringen til `Rad.sist_hentet` sier «alltid», og en rad uten tid ville falt ut av minimumet | low | Nås ikke: lesekontrakten sier at `sist_hentet` er None hvis og bare hvis serien er tom, og en tom serie gir ingen rad (`bygg_rad`). Docstringen bør navngi kontrakten | patch (tekst) |
| 7 | blind | Tester mangler for dagen sommertiden slutter, for tre ulike tider og for at detaljen ikke har radtid | low | Ingen feil er vist. Sommer- og vintertestene skiller allerede `Europe/Oslo` fra en fast forskyvning (mutant 4) | avvist |
| 8 | blind | Tidssonetestene står både i `test_markedsoversikt` og `test_app` | low | Apptestene viser at filteret er koblet til hver mal, også detaljen i vintertid. Ingen skade | avvist |
| 9 | blind | Importvakten for `Kurskilde` er fjernet uten erstatning, så kjernen kan importere `SnapshotKilde` | false | `SnapshotKilde` gir EODHD-`dict`, og `test_ingen_eodhd_noekler_i_kildeteksten` feiler hvis kjernen leser de nøklene | avvist |
| 10 | blind | Testtallet etter står ikke i spesifikasjonen (anslått 413) | false | Implementation Notes har 416, målt. Anslaget regnet 13 nye tester, ikke 16 | avvist |
| 11 | edge | To tider som bare skiller seg i sekunder, gir radtid med samme minutt som siden | low | En henting gir samme `hentet` til alle symbolene (AD-5, argumentet til `erstatt_serie`). Rettingen er ny avrundingslogikk | avvist |
| 12 | edge | Datoen i overskriften er `rader[0].dato`, og den kan motsi sidens eldste tidsstempel når symbolene har ulike siste datoer | low | Fantes før 1.4c (`index.html`). Blir synlig når symbolene hentes hver for seg (Epic 2) | defer |
## Design Notes

**Trinn:** (1) Etter ja: spesifikasjonen `ready-for-dev` på `main`, 1-4c `in-progress`, grenen `1-4c`, kontrollregningen før. (2) Kode og tester på grenen, mellomcommits som pushes. (3) Kontrollregningen etter, mutantene og gjennomgangen (bmad-build steg 4), så pull request. Stopp før flettingen med testtallene, kontrollregningen og utfallet av gjennomgangen, og vent på ja. (4) Squash, så spinen og `epics.md`, så 1-4c til `review` sammen med dagsfila.

På ekte data har alle symbolene samme `hentet`, så ingen rad viser eget tidsstempel der. Det nye synes bare i testene med ulike tider.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: alt grønt; 408 før
- `uv run python data/kontrollregning_1_4c.py --sammenlign` -- expected: bare antall, alle like uten tidsstemplene
- `grep -rn "Kurskilde\|MinneKilde\|TestKurskildeErPaaVeiUt" src tests` -- expected: ingen treff
