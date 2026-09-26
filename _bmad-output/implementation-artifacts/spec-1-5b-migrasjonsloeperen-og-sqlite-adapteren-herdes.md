---
title: 'Story 1.5b: Migrasjonsløperen og SQLite-adapteren herdes'
type: 'bugfix'
created: '2026-09-26'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7c1ae48ff050ebd53d52269afdef90648858a1a4'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Løperen (`src/migrering.py`) og adapteren (`src/lagring_sqlite.py`) er riktige så lenge det finnes én migrasjon. Med `0002` kan en migrasjon kjøres feil, halvveis eller mot en katalog som er endret, uten at noe feiler. Forutsetningene a–h i story 1.5b (`epics.md`) er prøvd mot koden 23.–24.09.

**Approach:** Hver forutsetning får en test som feiler før rettingen og består etter. For d og h, der koden ikke skal endres, er det en mutant som viser at testen fanger feilen. Løperen kontrollerer katalogen og de anvendte migrasjonene inne i én `BEGIN IMMEDIATE`-transaksjon per migrasjon, og adapteren krever siste versjon. Kilde: story 1.5b i `epics.md` slik den står 26.09.

## Boundaries & Constraints

**Always:**
- AD-16: hver migrasjon kjøres i én transaksjon sammen med sin rad i `skjema_versjon`. Løperen eier transaksjonen.
- AD-7: ingen `DROP TABLE`-hjelper, ingen rebuild og ingen unntaksvei. `skjema_versjon` oppgraderes ikke stille.
- Samme oppførsel på Windows og Linux. CI kjører på Linux, og alle nye tester kjøres på begge.
- Regel 6: ingen nett i testene. Hver test lager egen katalog og base under `tmp_path`.

**Never:**
- Ingen `0002` i `src/migrasjoner/`. Den er story 1.6.
- Ingen endring i `Kurslager`-porten, i `Kursrad` eller i `0001_kurs.sql`.
- Ingen avgjørelse om hvem som kaller `migrer()`. Det er story 3.1.

## Beslutninger 26.09

- **b) En `COMMIT` stoppes før noe kjøres (valg B).** Avvisningen ser på første ord i hver hele setning fra `_setninger()`, etter mellomrom og kommentarer, både `--` og `/* */`. Setninger som begynner med `BEGIN`, `COMMIT`, `END`, `ROLLBACK`, `SAVEPOINT` eller `RELEASE`, avvises før transaksjonen starter. Sjekken skiller ikke mellom store og små bokstaver, så «commit;» og «Commit;» avvises på samme måte som «COMMIT;». Står et slikt ord midt i en setning, avvises den ikke, så `CREATE TRIGGER … BEGIN … END;` er fortsatt lov. Sjekken av `in_transaction` etter hver setning, som storyen beskriver, blir stående som ekstra sikring, med sin egen mutant.
- **Én story og én PR, i to deler (valg A).** Del 1 er løperen: a, b, e, f, g og h-testen i `test_migrering.py`. Del 2 er adapteren: c, d og h-testen i `test_lagring_sqlite.py`. Blir funnene etter del 1 mange, stopper vi der og tar del 2 i en ny økt på samme gren.
- **Lengden på spesifikasjonen er godtatt**, fordi hvert av de åtte kontrollpunktene trenger test og mutant.

## I/O & Edge-Case Matrix

| Punkt | Tilstand | Forventet |
|---|---|---|
| a | Basen har kjørt `0002_min.sql`, katalogen har `0002_din.sql` | `MigrasjonsFeil` som navngir begge filnavnene. Ingenting kjøres |
| b | Fila har `CREATE TABLE foer; COMMIT; CREATE TABLE etter; <ugyldig>` | Avvist før noe kjøres. Basen er uendret, uten `foer` eller `etter` |
| b | `-- kommentar` eller `/* kommentar */` rett før `COMMIT;` | Avvist før noe kjøres |
| b | «commit;» med små bokstaver midt i fila | Avvist før noe kjøres |
| b | Migrasjonen har `CREATE TRIGGER … BEGIN … END;` | Kjøres. Triggeren finnes etterpå |
| c | Basen står på 1, adapterens katalog har 2 | `RuntimeError` med begge versjonsnumrene |
| d | Trigger `RAISE(ABORT)` på `INSERT` og `UPDATE` i `kursserie` | Serie og tid står uendret, både for nytt og for kjent symbol |
| e | `0001_a.sql` er kjørt, og innholdet endres etterpå | `MigrasjonsFeil`: fila er endret etter at den ble kjørt |
| e | Samme innhold med CRLF i stedet for LF | Godtatt. Samme hash |
| e | `skjema_versjon` uten kolonnen `sha256` | `MigrasjonsFeil`: basen er laget før 1.5b. Ingen stille oppgradering |
| f | En annen tilkobling migrerer mellom lesingen og `BEGIN` | Returnerer 1 uten feil. En eventuell feilmelding leser versjonen fra basen |
| g | `0002_ny.SQL` | `MigrasjonsFeil` på begge plattformer |
| g | `0000_x.sql` | `MigrasjonsFeil`: «0000 er ikke et gyldig nummer, første migrasjon er 0001» |
| g | Tom katalog | `MigrasjonsFeil`: ingen migrasjoner |
| h | Første migrasjon feiler, eller adapteren avviser en umigrert base | `count(*)` i `sqlite_master` er 0 |

</frozen-after-approval>

## Code Map

- `src/migrering.py` -- løperen. `migrer()` (linje 54–81) leser versjonen før transaksjonen (f) og sammenlikner bare antall (a). `_migrasjoner()` bruker `glob("*.sql")` (g, linje 94), og `range(1, …)` gir feil melding for 0000 og ingen feil for tom katalog. `_kjoer()` bruker `BEGIN` (utsatt), lager `skjema_versjon (versjon, fil, anvendt)` og regner ut versjonen i feilmeldingen (`nummer - 1`, linje 157). `_setninger()` gjenbrukes uendret.
- `src/lagring_sqlite.py` -- `SqliteKurslager.__init__` sjekker `versjon < 1` (c). `erstatt_serie` er riktig og endres ikke (d).
- `tests/test_migrering.py` -- 21 tester (`test_lagring_sqlite.py` har 8, begge telt 26.09). `TestIngenUnntaksvei` låser modulen til to offentlige funksjoner, og den testen må endres (se Design Notes). Linje 174 bruker `versjon()` og `tabeller()`, som filtrerer bort `skjema_versjon` (h).
- `tests/test_lagring_sqlite.py` -- linje 119 sjekker bare versjonen (h). d-testene hører hjemme her.
- `tests/test_kurslager.py` -- bruker `migrer` og `SqliteKurslager` i fixtures. Skal fortsatt være grønn uten endring.
- Ingen produksjonskode kaller `migrer()` eller `SqliteKurslager`, og ingen `.db`-fil finnes i repoet eller i `data/`. Det er slått opp 26.09.

## Tasks & Acceptance

**Execution:**
- [ ] `src/migrering.py` -- `_migrasjoner`: bytt `glob` ut med `iterdir()` og velg filer der `suffix.lower() == ".sql"`, så `FILNAVN` avviser `.SQL` med en egen melding. Avvis 0000 og tom katalog med egne meldinger -- g
- [ ] `src/migrering.py` -- `migrer`: katalogen kontrolleres først. Deretter gjøres dette per migrasjon: `BEGIN IMMEDIATE`, les `(versjon, fil, sha256)` inne i transaksjonen, avvis nytt filnavn (a) og endret innhold (e), og kjør neste eller avslutt -- a, e, f
- [ ] `src/migrering.py` -- `_kjoer`: `skjema_versjon` får `sha256 TEXT NOT NULL`, med hash av filteksten normalisert til LF. Mangler kolonnen, avvises basen. Forhåndssjekk av første ord i hver setning (se Beslutninger), `in_transaction` etter hver setning som ekstra sikring, og feilmeldingen leser versjonen etter `ROLLBACK` -- b, e, f
- [ ] `src/migrering.py` -- ny offentlig `siste_versjon(katalog) -> int`, som gjør samme katalogkontroll. Den er en ren lesing og ingen unntaksvei -- c
- [ ] `src/lagring_sqlite.py` -- krev `versjon(t) == siste_versjon(MIGRASJONSKATALOG)`, og nevn begge tallene i feilmeldingen -- c
- [ ] `tests/test_migrering.py` -- tester for a, b (fem: `COMMIT` midt i fila, `COMMIT` etter en kommentar, «commit;» med små bokstaver midt i fila, en trigger som kjøres, og den ekstra sikringen alene, med forhåndssjekken byttet ut med en som slipper alt gjennom via `monkeypatch`), e (tre), f (to), g (tre) og h (linje 174). `TestIngenUnntaksvei` endres til tre funksjoner, med begrunnelse i testen -- a, b, e, f, g, h
- [ ] `tests/test_lagring_sqlite.py` -- tester for c og d (to: nytt og kjent symbol) og h (linje 119) -- c, d, h

**Acceptance Criteria:**
- Gitt at hver test kjøres mot koden fra `baseline_commit`, når testene for a, b, c, e, f og g kjøres, så feiler hver av dem av grunnen som står i matrisen. Unntaket er to tester som vokter mot en for streng retting, triggeren i b og CRLF-testen i e. De skal bestå også mot koden fra `baseline_commit`, og for dem er det mutantene som viser at de virker.
- Gitt mutantene i Design Notes, når hver av dem legges inn én om gangen, så feiler akkurat testene for det punktet, med forventet melding og ikke bare et bredt utslag (lærdommen fra 23.09).
- Gitt hele testsettet på Windows lokalt og på Linux i CI, når det kjøres, så er det grønt begge steder med samme antall tester.

## Design Notes

**f) Kappløpet uten sleep og uten tråder.** Tilkobling A lages med `sqlite3.connect(..., factory=Krok)`, der `Krok.execute` lar tilkobling B migrere første gang den ser en setning som begynner med `BEGIN`. Før rettingen leser A versjon 0, B migrerer, og A kjører `0001` og feiler med «Basen staar paa versjon 0». Etter rettingen leser A versjonen inne i `BEGIN IMMEDIATE`, ser 1 og returnerer 1.

**g) Lik oppførsel på Linux og Windows.** Årsaken til forskjellen er at `glob`s mønster skiller store og små bokstaver bare på Linux. `iterdir()` med `suffix.lower()` gjør valget i Python, likt på begge plattformer. Deretter avviser `FILNAVN`, som bare godtar `.sql`, fila med en melding som sier hva som er feil. Testen oppretter `0002_ny.SQL` og forventer samme `MigrasjonsFeil` på begge.

**e) sha256 og baser som alt finnes.** Hashen regnes av `read_text(encoding="utf-8").replace("\r\n", "\n")`. Uten det ville samme fil gitt ulik hash etter en Windows-utsjekking med `core.autocrlf=true`, som er satt på Marians maskin, og i Linux-imaget. Ingen base finnes ennå. Løperen avviser derfor en `skjema_versjon` uten `sha256` i stedet for å oppgradere den stille, fordi en stille oppgradering måtte stolt på filen slik den er nå, og det er nettopp det e skal hindre. En gammel testbase bygges på nytt fra rådatafilene (AD-6). Etter at `vurdering` finnes (1.6), kan vi ikke gjøre det slik lenger.

**c) krever en ny offentlig funksjon.** `TestIngenUnntaksvei` låser `migrering` til `migrer` og `versjon`. Adapteren må vite siste versjon uten å gjenta katalogkontrollen. Alternativet er at den kaller den private `_migrasjoner`. `siste_versjon` leser bare, og testen endres synlig til tre funksjoner.

**d og h har ingen retting i koden.** Beviset er mutanter:
- d: `COMMIT` flyttes før skrivingen til `kursserie`.
- h, første test: `CREATE TABLE skjema_versjon` flyttes før `BEGIN`.
- h, andre test: adapteren lager `kurs` i `__init__`.
- De gamle testene består alle tre mutantene. De nye feiler.

**Mutanter for de andre punktene**, én per punkt: fjern filnavnsjekken (a), fjern forhåndssjekken (b, testene for `COMMIT` feiler), la forhåndssjekken se på hele setningen i stedet for første ord (b, triggertesten feiler), la sjekken skille mellom store og små bokstaver (b, testen med «commit;» feiler), fjern `in_transaction`-sjekken med forhåndssjekken slått av i testen (b, ekstra sikring), bytt `==` tilbake til `< 1` (c), fjern hashsjekken (e), fjern LF-normaliseringen (e, CRLF-testen), bytt `BEGIN IMMEDIATE` tilbake til `BEGIN` og les utenfor (f), og bytt tilbake til `glob("*.sql")` (g, bare utslag på Linux, så denne må kjøres i CI eller i WSL).

**Størrelse.** Om lag 20 nye tester og 3 endrede, alle i to testfiler, og to kildefiler. Punktene a, e og f omskriver samme løkke i `migrer()` og kan ikke deles. c avhenger av `siste_versjon`. Én økt er realistisk for del 1. Del 2 er liten, men gjennomgangen etter del 1 kan ta resten av økta.

**Arbeidsflyt, som 1.4b, 1.4c og 1.5:** grenen `1-5b` fra `main`. Mellomcommits pushes per punkt eller per par av punkter. PR mot `main`. Kodegjennomgang tas per epic, ikke per story (åpent punkt 22). Vi stopper før flettingen og venter på ja. Så squash med `Co-authored-by: Joakim Lund`. Antall tester før (427) og etter telles og føres i squash-meldingen.

**Etter flettingen:**
- Spinen: AD-16, «Opphav», med at løperen er herdet, sha256 i `skjema_versjon` og `BEGIN IMMEDIATE`.
- `epic-1-context.md`: punktet «1.5b før 1.6» får status ferdig.
- `epics.md`: 1.5b krysses av.
- `sprint-status.yaml`.
- `deferred-work.md`: bare hvis gjennomgangen utsetter noe. Den har ingen 1.5b-oppføringer i dag.
- `docs/innlevering.md`, linje 98 (tallet på tester er fra 24.09): meldes, men rettes ikke uten at vi ber om det.

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: grønt, 427 + nye tester, telt
- `uv run pytest -q tests/test_migrering.py tests/test_lagring_sqlite.py` -- forventet: grønt, med nye tester for hvert punkt a–h
- Mutantene i Design Notes, én om gangen -- forventet: akkurat testene for punktet feiler, og koden settes tilbake mellom hver
