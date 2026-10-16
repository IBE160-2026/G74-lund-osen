---
title: 'Story 2.8, PR 1 (2.8a): tabellen indeks, porten og demoindeksen'
type: 'feature'
created: '2026-10-17'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e978511'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
---

## Intent

**Problem:** Story 2.8 (FR-410) krever at hovedindeksen `OSEBX.OL` hentes i samme kjøring som aksjene og lagres i en egen tabell, `indeks`, fra migrering `0006`, aldri i `aksje`, `kurs`, `kursserie` eller `vurdering` (føringen 2026-10-01 under AD-21). Story 2.9 skal vise den over tabellen, også i demoen (FR-411, beslutningen 16.10 kl. 11:46).

**Planen** (instruksjonen 16.10 kl. 17:45, vist i chatten og ført kort i Utført-linja i `619720c`) deler arbeidet i fire PR-er. Svarene kl. 18:04 (under story 2.8 i `epics.md`, `8cb8c77`): PR 1 flettes etter #49, demobasen får en oppdiktet hovedindeks i PR 1, PR 2 flettes lørdag 17.10, og henteinstruksjonen fra mandag 19.10 har 16 kall, versjon 6 og 4 kall til nye forsøk. Gruppen sa «klar» til PR 1 16.10 kl. 23:57.

**PR 1, denne:** tabellen, porten og demoindeksen, uten endring i hentingen.
- `src/migrasjoner/0006_indeks.sql`: tabellen `indeks` med feltene `kurs` har for en dag (`symbol`, `dato`, `slutt`, `justert_slutt`, `volum`), og `indeksserie` med `hentet`, som `kursserie`. Ingen trigger mot `aksje`, fordi indeksen ikke er en aksje (AD-21).
- `src/indeksdata.py`: `Indeks`, `HOVEDINDEKS` (`OSEBX`, `OSEBX.OL`), `Indeksleser` og `Indekslager` i samme form som `Kursleser` og `Kurslager`, `bare_boersdager`, `kontroller_indeksskriving` og `MinneIndekslager`.
- `src/lagring_sqlite.py`: `SqliteIndekslager`, som bytter ut serien i én transaksjon (AD-5).
- `src/demo.py`: `DEMOINDEKS` og en oppdiktet serie over alle demodagene.
- Spinen: en merknad under AD-21 om tabellen og porten.

**PR 2, ikke denne:** kallet for `OSEBX.OL` i `src/fetch_prices.py`, 16 kall per kveld og 4 til nye forsøk, rådata under en egen nøkkel i øyeblikksbildet, `docs/hjelp.md` og diagrammet i spinen («15 kall, bevisst»), og sjekken av basen før kallene, som skal virke også når basen står en versjon bak (beslutningen 16.10 kl. 22:16 under story 2.8). README-en og `docs/hjelp.md` endres ikke i PR 1.

## Valgene i PR 1

- **`indeksserie`:** `Kursleser` har `sist_hentet`, og AD-5 setter den i samme transaksjon som radene. Indeksen får derfor sin egen tabell for tidspunktet, som `kursserie`, i samme migrering.
- **Symbolet** er `OSEBX`, uten `.OL`, slik aksjene har `EQNR` og tickeren `EQNR.OL`. Porten tar lista over indekser som parameter, med `(HOVEDINDEKS,)` som standard, slik `Kurslager` tar `univers`. Et annet symbol avvises i porten. Basen har ingen trigger for symbolet i `indeks`, fordi AD-21 sier at triggerne ikke gjelder tabellen.
- **Bare børsdager:** porten tar bort dager i år utenfor `DEKKEDE_AAR` og dager som ikke er børsdager, før noe lagres, og gir ingen feil for dem. Serien fra EODHD går ett år bakover, og §14 i `malinger.md` viser fem datoer i indeksen som aksjene ikke har: 2025-12-24, 2025-12-31, 2026-04-02, 2026-05-14 og 2026-05-25. De to første ligger i 2025, utenfor `DEKKEDE_AAR`, og de tre siste er stengte dager i kalenderen. Blir det ingen rader igjen, avvises serien som tom (AD-5). Koden har ikke noe fast årstall: året leses fra `DEKKEDE_AAR` i `boersdag.py` når serien skrives.
- **Demoindeksen** heter «Demoindeksen» med symbolet `DEMIX` (ticker `DEMIX.OL`). Den er regnet fra demoaksjene: dagens endring er snittet av endringen for aksjene som har kurs begge dagene, så indeksen følger demoaksjene, og 2.9 kan vise «x av N». Ingen side viser den i PR 1.
- **Navnet og symbolet** er sjekket mot symbolene i repoet (`AKSJEUNIVERS`, `DEMOUNIVERS` og de 122 i `malinger.md` §33), men ikke mot lista hos Euronext, fordi instruksjonen ikke tillater nettkall. **Må sjekkes av gruppen**, slik selskapene i demoen ble sjekket for hånd 10.10 (spesifikasjonen til 3.4).

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` endres ikke og kjøres ikke.
- `data/db/ose.db` røres ikke (regel 22). Testene bruker midlertidige baser.
- Etter flettingen migreres den ekte basen til 6 neste gang webserveren eller hentingen skriver. Sjekken av basen før kallene (`manglende_i_basen`) avviser en base som står en versjon bak, og hentingen går da videre uten den, med filvakten som vakt (Utført-linja for hentingen 16.10). Det rettes i PR 2 (beslutningen kl. 22:16).
- Flettes ikke uten ja fra gruppen.
- **Navnet og symbolet til demoindeksen sjekkes av gruppen mot lista hos Euronext før flettingen** (gjennomgangen, BH13).

**Testtallet før:** 2236 bestått og 17 hoppet over (grenen til PR #55 på `1efe816`, samme kode som main etter `cafe067`).

*Lagt til 2026-10-17 (gjennomgangen, BH12):* `baseline_commit` er main på `e978511`. Testtallet før er målt på `1efe816`, og koden og testene er de samme som på main etter flettingen av PR #55 i `cafe067`, så tallet gjelder for `e978511`.

## Mutantene

Én om gangen med `-x` og bare `tests/test_indeks.py`, i en fersk klone, med sha256 mot HEAD etter hver, på `5054f76` og igjen på `ebf8235` etter rettingene. Alle fanget begge gangene:
- I1, indeksen skrevet i `kurs`: `test_serien_byttes_ut_ikke_skjoetes_paa[sqlite]` (triggeren fra `0003` avviser `OSEBX` i `kurs`).
- I2, en lørdag lagret: `test_en_loerdag_og_en_helligdag_lagres_ikke[minne]`.
- I3, serien skjøtt på i stedet for byttet ut: `test_serien_byttes_ut_ikke_skjoetes_paa[sqlite]`.
- I4, demobasen uten indeks: `test_indeksen_for_alle_demodagene`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `main...5054f76`, med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, 3). Rettingene står i `9efcef4` og `ebf8235`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH | En `Indeks` med symbolet til en aksje ble godtatt, og basen har ingen trigger for `indeks` | medium | patch: porten avviser et symbol i `AKSJEUNIVERS`, `test_en_aksje_avvises_ogsaa_naar_den_er_gitt_som_indeks` |
| VG3, BH10 | Bare `IntegrityError` var prøvd for tilbakerullingen | medium | patch: `test_en_annen_feil_midt_i_transaksjonen_ruller_tilbake` |
| VG1 | Øyeblikksbildet av demobasen i `test_demo.py` tok ikke med `indeks` | medium | patch: `indeks` og `indeksserie` i `_tabeller` |
| VG2, ECH, BH8 | Testen av demoindeksen så bare siste dag, med en toleranse som kunne glippe på avrundingen, og ikke volumet | low | patch: hver dag med relativ toleranse, volumet, og en egenskap (alle opp 1 % gir indeksen opp 1 %) |
| BH10 | Tid i norsk sone og rader i omvendt rekkefølge var ikke prøvd | low | patch: `test_tid_i_norsk_sone_leses_som_utc`, `test_radene_leses_i_rekkefoelge` |
| BH14 | Merknaden i spinen sa ikke at symbolet bare håndheves i porten | low | patch |
| BH15 | Importer midt i fila, og to sjekker i én test | low | patch: importene øverst, testen delt i to |
| BH12 | To grunnlag for testtallet før | low | patch: linja over |
| BH13 | Navnet og symbolet til demoindeksen er ikke sjekket mot lista hos Euronext | medium | **må gjøres av gruppen** før flettingen (Boundaries) |
| BH1 | Ved et årsskifte uten ny kalender faller alle nye dager bort, mens `hentet` blir fersk | medium | defer til PR 2: hentekommandoen stopper alt i dag med `UtenforKalenderen` når dagen ligger utenfor `DEKKEDE_AAR`, så den henter ikke. Kallet og utskriften kommer i PR 2 |
| BH2 | Dagene som tas bort, telles ikke | low | defer til PR 2, der hentingen skriver ut det den lagret |
| BH6 | Sjekken av basen før kallene avviser en base som står en versjon bak, til PR 2 | medium | avvist: beslutningen 16.10 kl. 22:16 legger rettingen i PR 2, og filvakten holdt 16.10. Står i PR-en |
| BH3 | Ingen CHECK i `indeks` | low | avvist: samme form som `kurs`, og `Kursrad` avviser tall som ikke er endelige, null eller under null, og negativt volum, før noe lagres |
| BH4 | NaN, uendelig og negative tall | low | avvist: `Kursrad.__post_init__` avviser dem (`UgyldigKursrad`) |
| BH5 | `volum` kan mangle for en indeks | low | avvist: §14 i `malinger.md` sier at `volume` finnes på alle radene for `OSEBX.OL` og er 0 på én. 0 er lovlig i `Kursrad` |
| BH7 | Demoindeksen avrundes til to desimaler når den lagres (regel 21) | low | avvist: som demoaksjene, etter regelen i `demo.py`, fordi kilden gir to desimaler. Nivået regnes videre uavrundet |
| BH9, ECH | Et hull i en aksjeserie, og deling på null | low | avvist: demoseriene har ingen hull (Varde Systemer begynner sent, og Matfjord Merkevarer har ingen kurser), og `Kursrad` avviser en kurs på null |
| BH11 | Lesesiden sjekker ikke symbolet | low | avvist: som `Kursleser`, der et ukjent symbol gir en tom serie |
| ECH | En tom liste over indekser gir en feilmelding om ukjent indeks | low | avvist: meldingen er riktig |
