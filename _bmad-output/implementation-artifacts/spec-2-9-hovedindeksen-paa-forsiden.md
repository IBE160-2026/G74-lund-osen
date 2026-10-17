---
title: 'Story 2.9, PR 3 for hovedindeksen: «Hovedindeksen» over tabellen på forsiden'
type: 'feature'
created: '2026-10-17'
status: 'done'
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

**Symbolet fra basen:** porten får `symboler()`, som gir indeksene basen har en serie for. Siden viser den som sist ble hentet, så den ekte basen viser OSEBX og demobasen DEMIX. *Rettet 2026-10-17 (gjennomgangen, BH13):* har basen `HOVEDINDEKS` (OSEBX), viser siden den, også når en annen indeks er hentet senere. Ellers viser den den som sist ble hentet, som DEMIX i demobasen. SQL-en ligger i `SqliteIndekslager`, ikke i `app.py`, som ikke har SQL (testen fra 2.2b).

**b) Visningen,** mellom innledningen (med «Slik leser du tabellen») og tabellen, etter §11:
- Overskriften «Hovedindeksen» med symbolet ved siden av, så verdien og dagens endring i prosent. Under dem står «x av N gikk bedre enn indeksen», og navnene på aksjene som ikke er med.
- Står indeksen på en annen dag enn tabellen, står datoen ved verdien.
- **Uten indeks i basen** sier delen «Hovedindeksen er ikke hentet ennå.», og resten av siden virker (NFR-03). Kan indeksen ikke leses, også når en rad ikke kan tolkes (`ValueError`), sier den det, og tabellen vises likevel (gjennomgangen, ECH1 og ECH5).
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

*Lagt til 2026-10-17 kl. 19:55:* PR #59 er squash-flettet i `b44284f`, låst til head-en `bdfd412`. CI var grønn på head-en (39055685375) og på main (39055792414).

## Mutantene

Én om gangen med `-x`, mot `tests/test_hovedindeks.py` og `TestHovedindeksenPaaForsiden` i `tests/test_app.py`, i den ferske klonen med `core.autocrlf=false`, med kopi før og sha256 mot HEAD etter hver. Alle ble fanget på `7f8cd02`, og igjen på `5539e4a`, etter rettingene:
- H1, N som et fast 15: `test_n_er_aksjene_med_kurs_og_en_uten_navngis`.
- H2, endringen mot forrige rad: `test_et_hull_foer_indeksens_dato_gir_ingen_endring`.
- H3, lik regnet som bedre: `test_lik_er_ikke_bedre`.
- H4, «bedre» avgjort før avrundingen: `test_like_foerst_etter_avrundingen_er_ikke_bedre`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `main...7f8cd02`, med Blind Hunter (BH, 20 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 1). Rettingene står i `5539e4a`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1, ECH5, BH4 | En rad i indeksen som ikke kan tolkes (`ValueError`), er ikke med i `BASEFEIL`, og forsiden ville gitt 500 | medium | patch: `_hovedindeks` fanger også `ValueError`, og `test_en_rad_som_ikke_kan_tolkes_stopper_ikke_siden` |
| VG1 | Fargen ved en endring som ikke er null, er ikke prøvd | low | patch: `opp` ved +0,50 % og `ned` ved -1,00 % |
| BH9, BH10 | `avrundet` og `tall` kan gi ulike tall på halvveien og rundt null | low | patch: `TestAvrundingenErDenSomVises`, med halvveis-tall og 4001 tall |
| BH13 | Siden bytter indeks hvis en annen blir hentet senere | low | patch: OSEBX først, og `test_hovedindeksen_vises_foran_en_annen_indeks` |
| BH12 | Navnet på delen for skjermleseren tok med symbolet og knappen | low | patch: `id` på et `span` med bare «Hovedindeksen» |
| BH16 | Testen for 390 px så på én regel | low | patch: alle reglene for delen, uten fast bredde og uten `nowrap` |
| BH17 | `OSEBX` ble sjekket på hele demosiden | low | patch: bare i delen |
| BH3 | Docstringen lovet tider i ulik sone | low | patch: porten lagrer i UTC, og docstringen sier det |
| BH1 | `symboler()` gir et symbol per rad | low | avvist: `indeksserie` har én rad per symbol (`ON CONFLICT (symbol)` i `0006`) |
| BH11, BH19 | «?» uten vindu, og dato ved verdien når siden ikke har rader | low | avvist: delen og vinduet står begge inne i `{% if rader %}` |
| BH2 | Tider uten sone sorteres feil | low | avvist: porten avviser en tid uten sone og lagrer i UTC (`kontroller_indeksskriving`) |
| BH5 | Endringen på justert kurs og verdien på `slutt` | low | avvist: `close` og `adjusted_close` er like for indeksen (§14 i `malinger.md`, FR-104) |
| BH6 | En aksje med kurs, men uten rad før, telles i N | low | avvist: FR-104 sier at N er aksjene med kurs for indeksens dato. Den kan ikke være bedre (`test_en_aksje_uten_rad_foer_dagen_er_med_men_ikke_bedre`) |
| BH7 | En aksjes endring etter et hull gjelder flere dager | low | avvist: FR-104 sammenligner med aksjenes endring fra FR-101, som i tabellen |
| BH8 | Serien er ikke sortert | low | avvist: porten gir radene `ORDER BY dato`, og datoen er primærnøkkel |
| BH14, BH15 | En spørring per aksje og flere gjennomløp | low | avvist: 15 aksjer i en lokal base |
| BH18 | Grensen på 14 dager i `forrige_boersdag` | low | avvist: den lengste stengte perioden er påsken, og testen for påsken går gjennom |
| BH20 | Frontmatter uten `updated` | low | avvist: samme form som spesifikasjonene 2.8a og 2.8b. Regel 4 gjelder `docs/` og `planning-artifacts/` |
| ECH2, ECH3 | Står indeksen foran alle aksjene, eller mangler endringen, navngis ingen | low | avvist: FR-104 sier at sammenligningen ikke vises da, og navnene hører til sammenligningen |
| ECH4 | Et symbol i `indeksserie` uten rader i `indeks` | low | avvist: porten skriver begge i én transaksjon og avviser en tom serie (AD-5) |
