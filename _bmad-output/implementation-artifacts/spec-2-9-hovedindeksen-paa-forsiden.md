---
title: 'Story 2.9, PR 3 for hovedindeksen: «Hovedindeksen» over tabellen på forsiden'
type: 'feature'
created: '2026-10-17'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5d38173'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-10-13.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-8a-indeks-tabellen-og-porten.md'
---

## Intent

**Problem:** hentingen lagrer hovedindeksen fra PR #57 (`bcac2b5`), og demobasen har demoindeksen fra PR #56 (`1d3a21d`), men ingen side viser den. Story 2.9 (FR-104) krever «Hovedindeksen» over tabellen på forsiden, med symbolet, verdien, dagens endring og «x av N gikk bedre enn indeksen». Søylene (2.9b, FR-105) kommer i PR 4, og story 2.9b endres ikke.

**Grunnlaget:** kontrollen under story 2.9 i `epics.md`, FR-104 i `prd.md`, AD-10 (webserveren gjør ingen nettkall), AD-21 med føringene 30.09 (N telles, aldri fast) og 01.10 (indeksen er ikke en aksje), `designregler.md` §3–§5, §11 i `designutdrag-2026-10-13.md` (indeksen står mellom innledningen og tabellen) og porten fra spesifikasjonen 2.8a.

## Planen, én commit per punkt

**a) Tallene.** En ny ren modul, `src/hovedindeks.py`, uten I/O og uten nettkall (AD-10). Den får serien for indeksen og seriene for aksjene gjennom portene, og gir det siden viser:
- **Verdien** er `slutt` for indeksens siste rad.
- **Endringen** regnes mot forrige børsdag etter kalenderen (`boersdag.er_boersdag`), ikke mot forrige rad, fordi indeksen kan ha datoer aksjene ikke har (`malinger.md` §14). Mangler raden for forrige børsdag, eller ligger den utenfor `DEKKEDE_AAR`, er endringen `None`, og ingen endring vises.
- **N** er aksjene med kurs for indeksens dato, telt fra lista i basen, aldri et fast antall (føringen 30.09). En aksje uten kurs for den datoen navngis.
- **En aksjes endring** for indeksens dato er endringen fra FR-101: kursen den dagen mot raden før, som i tabellen (`endring_i_prosent`).
- **«Bedre»** avgjøres på endringene slik de vises: begge rundes til desimalene for `endring` i `tallformat.py` (to), og aksjen er bedre bare når dens tall er større. Lik er ikke bedre. Avrundingen står i én funksjon i `tallformat.py`, `avrundet`, som også brukes til fargen (regel 21).
- **Ingen sammenligning** når ingen aksje har kurs for indeksens dato, eller når indeksen ikke har en endring.

**Symbolet fra basen:** porten får `symboler()`, som gir indeksene basen har en serie for. Siden viser den som sist ble hentet, så den ekte basen viser OSEBX og demobasen DEMIX. SQL-en ligger i `SqliteIndekslager`, ikke i `app.py`, som ikke har SQL (testen fra 2.2b).

**b) Visningen,** mellom innledningen (med «Slik leser du tabellen») og tabellen, etter §11:
- Overskriften «Hovedindeksen» med symbolet ved siden av, så verdien og dagens endring i prosent. Under dem står «x av N gikk bedre enn indeksen», og navnene på aksjene som ikke er med.
- Står indeksen på en annen dag enn tabellen, står datoen ved verdien.
- **Uten indeks i basen** sier delen «Hovedindeksen er ikke hentet ennå.», og resten av siden virker (NFR-03). Kan indeksen ikke leses, sier den det, og tabellen vises likevel.
- Tabellen har fortsatt fem kolonner (FR-101).
- **Designreglene:** teksten bærer og fargen forsterker, så endringen har fortegn og farge etter tallet slik det vises, som i tabellen. Ingen piler (FR-103, pilene er bare for retning). Tallene skrives med `tall` som i tabellen. Delen er et kort som de andre (§5) og bryter linjene ved 390 px.
- «?» med hjelp ved overskriften, som de andre delene (8.0b), med en tekst i `hjelpetekster.py` som har kildene sine.

**c) Tekstene (regel 19):** i «Status» i README-en flyttes «hovedindeksen på forsiden» fra «Neste» til «Flettet til main». `docs/hjelp.md` beskriver ikke forsiden (søkt etter «forsiden», «oversikten» og «tabellen»), så den endres ikke.

## Testene

Etter kontrollen i story 2.9, hver med «Ville feilet hvis»:
- N med en kortere liste enn 15, og en aksje uten kurs som navngis.
- Et hull før indeksens dato.
- Lik er ikke bedre.
- To endringer som er like først etter avrundingen.
- En indeks som står en dag bak tabellen.
- En base uten indeks.
- Demoen med DEMIX, der Matfjord Merkevarer navngis fordi den ikke har kurser.

**Mutantene,** én om gangen med `-x`, kopi før og sha256 mot HEAD etter:
- N som et fast 15
- endringen mot forrige rad
- lik regnet som bedre
- «bedre» avgjort før avrundingen

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobasene lages bare i midlertidige mapper.
- Story 2.9b endres ikke, og søylene kommer i PR 4.
- Flettes i instruksjonen kl. 19:31 når ingen test feiler, ingen mutant overlever, CI er grønn på head-en, og hvert funn med dom medium eller høyere er rettet.

**Testtallet før:** 2309 bestått og 17 hoppet over (head-en til PR #58, `33ca133`, samme kode og tester som main på `5d38173`).
