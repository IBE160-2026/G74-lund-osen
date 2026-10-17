---
title: 'Story 2.8, PR 2 (2.8b): kallet for hovedindeksen i hentingen, 16 kall, og sjekken av basen før kallene'
type: 'feature'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '0665703'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-8a-indeks-tabellen-og-porten.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
---

## Intent

**Problem:** PR 1 (2.8a, PR #56, `1d3a21d`) la tabellen `indeks` i migrering `0006`, porten og demoindeksen, men hentingen henter ikke indeksen ennå. Story 2.8 (FR-410) krever at `OSEBX.OL` hentes i samme kjøring som aksjene, med ett kall og 16 i alt. Samtidig avviser sjekken av basen før kallene en base som står en versjon bak, som 16.10 med `0005`: «Basen ose.db kunne ikke leses (RuntimeError). Henter likevel», og filvakten holdt (Utført-linja for hentingen 16.10). Den ekte basen står på versjon 5, og koden på main har 6.

**Grunnlaget:** kontrollpunktene under story 2.8 i `epics.md`, svarene 16.10 kl. 18:04 (PR 2 flettes lørdag 17.10, henteinstruksjonen fra mandag 19.10 har 16 kall, versjon 6 og 4 kall til nye forsøk, og README-henvisningen gjelder `docs/hjelp.md`), beslutningen 16.10 kl. 22:16 (sjekken av basen rettes i PR 2 som egen commit med en test) og BH1 og BH2, som ble utsatt fra PR 1 (spesifikasjonen 2.8a).

## Planen, én commit per punkt

**a) Sjekken av basen før kallene.** `manglende_i_basen`, `manglende_vurderinger` og `eldste_foerst` åpner basen gjennom én funksjon, `_aapne_for_sjekken`, skrivebeskyttet (`mode=ro`) og med `PRAGMA query_only`, og adapterne tar `godta_en_versjon_bak=True`. Da godtas en base på siste versjon eller én bak. To eller flere bak og en base som er nyere enn koden, avvises som før, og hentingen går videre slik den gjør i dag. Adapterne godtar flagget bare på en tilkobling med `query_only`, så en skriver aldri kan få en base med et skjema den ikke kjenner. Testen bruker en base på versjon 5 med kurser og vurderinger skrevet med SQL, og viser at sjekken svarer riktig, at hentingen sier «Basen har alt kursene» med 0 kall, og at sha256 for fila er den samme etter.

**b) Kallet.** Etter aksjene henter `kjoer` `HOVEDINDEKS.ticker` med ett kall, med samme `hent`, samme intervall og samme kontroll av formen (`serie_fra_eodhd`).
- Kvotesjekken før kallene regner med `len(lista) + 1`, altså 16. Bonuskvoten brukes som før bare til å fullføre hovedhentingen, nå 16 kall.
- Øyeblikksbildet får nøkkelen `indeks`, med `serier` og `feil` i samme form som for aksjene: `{"serier": {"OSEBX": [...]}, "feil": {}}`, eller `{"serier": {}, "feil": {"OSEBX": "..."}}`. Rådataene står uendret. `serier` og `feil` øverst har bare aksjene, så `SnapshotLeser` og `--les-inn` ser ikke indeksen.
- Indeksen lagres med `SqliteIndekslager` etter at aksjene er skrevet, aldri i `kurs` eller `vurdering`. En eldre fil skriver ikke over en nyere serie, som for aksjene.
- Feiler kallet, eller avvises serien, står indeksen i `feil`, aksjene lagres og vurderes som vanlig, og indeksen får ingen ny sjanse (AD-15). Utskriften sier det.
- Utskriften sier hvor mange dager som ble lagret, og hvor mange som ble tatt bort fordi de ikke er børsdager i årene `DEKKEDE_AAR` dekker (BH2). Antallet regnes med `bare_boersdager`, samme funksjon som porten bruker.
- En andre kjøring samme børsdag gjør 0 kall, også for indeksen (testen i 2.3 utvidet).
- Nye forsøk (2.3b) henter bare aksjene, med `kall_til_nye_forsoek(igjen, grense, len(lista) + 1)`, altså 4 med de 15. Forsøksfila har ingen `indeks`.

**c) Årsskiftet (BH1).** En test viser at hentingen stopper med 0 kall og kode 1 når dagen ligger utenfor `DEKKEDE_AAR`, før nøkkelen og kvoten leses, så `indeksserie` aldri får en fersk `hentet` uten rader.

**d) Tekstene (regel 19).** `docs/hjelp.md` («en henting bruker 16», og 4 kall til nye forsøk), testen i `test_docker.py` som krever «en henting bruker N», nå med N lik antall aksjer pluss indeksen, diagrammet i spinen («16 kall, bevisst») og «Status» i README-en: at hovedindeksen hentes, står under «Flettet til main», mens visningen står under «Neste».

## Valgene i PR 2

- **Utgangskoden** er 3 (`KODE_BARE_INDEKSEN`) når aksjene er i orden, men indeksen feilet i kjøringen: kallet feilet, porten avviste serien, eller basen feilet. Da ser en feil med indeksen ikke ut som en vellykket kjøring (beslutningen 17.10 kl. 11:58 under story 2.8, BH7). Ikke 2, fordi argparse bruker 2 for feil i argumentene. Kode 1 går foran: mangler også en aksje dagens kurs, gir kjøringen 1, fordi aksjen kan prøves igjen samme kveld (2.3b), og et nytt forsøk tar ikke indeksen. En eldre fil som hoppes over for indeksen, er ingen feil. En ny kjøring etter kode 3 gir 0 kall og kode 0 (AD-15). Et nytt forsøk som fullfører aksjene, gir 3 når indeksen feilet i kveldens hovedhenting, fordi hovedhentingen da ga 1 (gjennomgangen av kode 3, BH4 og ECH2). *Rettet 2026-10-17:* her sto at utgangskoden er 0 når bare indeksen feiler, som rådet anbefalte.
- **`--les-inn` leser ikke indeksen.** Innlesingen er for kursene når basen feilet. Indeksen hentes for hele året hver kveld og byttes ut, så neste henting gir den igjen. Utsatt, ikke avvist: kommer i en egen story hvis gruppen vil.
- **Sjekken av basen ser bare på aksjene.** Har basen alle aksjene for børsdagen, men ingen indeks, hentes ingenting. Det følger av at indeksen ikke får en ny sjanse (AD-15).
- **Én versjon bak, ikke vilkårlig mange:** beslutningen kl. 22:16 gjelder tilfellet der en ny migrasjon er flettet og basen ennå ikke er migrert. En base som står lenger bak, kan ha et skjema lesingen ikke kjenner, og da er det tryggere å hente og la skrivingen migrere den.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke mot EODHD, og `data/db/ose.db` røres ikke (regel 22). Testene bruker midlertidige baser og falske hentere.
- Den ekte basen migreres til versjon 6 første gang hentingen skriver, mandag 19.10 etter flettingen.
- Flettes ikke uten ja fra gruppen.

*Lagt til 2026-10-17 kl. 12:30:* PR #57 er squash-flettet i `bcac2b5`, låst til head-en `b4a0721`, etter gruppens ja kl. 11:58 (gitt for når kode 3 var gjort). CI var grønn på head-en (kjøring 39025050482).

**Testtallet før:** 2274 bestått og 17 hoppet over (head-en til PR #56, `59020e2`, samme kode og tester som main etter `1d3a21d`).

*Lagt til 2026-10-17:* arbeidet ble avbrutt kl. 10:10 med «API Error: The response stopped arriving» mens testene for punkt b ble skrevet, og fortsatt med instruksjonen kl. 10:25. Punkt b ble committet først etter det, i `f1aacb1`.

## Mutantene

Én om gangen med `-x` og bare `tests/test_fetch_prices.py`, i en fersk klone med `core.autocrlf=false`, med kopi før og sha256 mot HEAD etter hver. Første kjøring var i en klone med CRLF. Der ble alle fanget, men sha256 ble sammenlignet med en fil med andre linjeskift, så den ble gjort om på `51cf452`:
- A1, sjekken krever siste versjon igjen: `test_de_tre_sjekkene_virker_paa_versjon_5_og_fila_er_uendret`.
- B2, indeksen lagret i `kurs`: `test_indeksen_lagres_i_indeks_aldri_i_kurs_eller_vurdering`.
- B3, 15 kall i kvotesjekken: `test_15_igjen_holder_ikke_for_16_uten_bonus`.
- B4, et feilet indekskall stopper aksjene: `test_et_feilet_indekskall_stopper_ikke_aksjene[feil]`.
- B5, et nytt forsøk tar med indeksen: `test_bare_de_som_mangler_hentes_eldste_foerst`.

Igjen på `e6070a9`, etter rettingene fra gjennomgangen, med to til for de nye testene. Alle fanget, og sha256 lik HEAD etter hver. A1 ble fanget av testen med nytt navn, `test_de_tre_sjekkene_virker_en_versjon_bak_og_fila_er_uendret`, og B2–B5 av de samme testene som over:
- V1, `except ValueError` fjernet fra `skriv_indeksen_til_basen`: `test_en_serie_porten_avviser_stopper_ikke_aksjene`.
- V2, sammenligningen av tidene snudd: `test_en_eldre_fil_skriver_ikke_over_en_nyere_indeks`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `main...51cf452`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 6) og Verification Gap (VG, 3). Rettingene står i `16ebdf8` og `e6070a9`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | Ingen test feiler lagringen av indeksen, bare kallet | medium | patch: en serie porten avviser (bare helgedager) og en `OperationalError` fra basen, begge med kode 0 og 15 vurderinger |
| VG2 | Vakten mot en eldre fil for indeksen er ikke prøvd | medium | patch: `test_en_eldre_fil_skriver_ikke_over_en_nyere_indeks`, også lik tid |
| VG3 | Rekkefølgen i testen av `eldste_foerst` var den samme med og uten tidene | low | patch: tidene i `kursserie` går mot rekkefølgen i lista |
| BH4, ECH3 | En versjon bak er trygt bare så lenge siste migrasjon ikke endrer tabellene sjekken leser | medium | patch: `test_siste_migrasjon_roerer_ikke_tabellene_sjekken_leser` feiler når siste migrasjon endrer `kurs`, `kursserie`, `vurdering` eller `aksje`, så sjekken vurderes på nytt før den flettes |
| BH8, ECH1 | Feiler basen for aksjene, sier utskriften ikke at indeksen ikke er lagret | low | patch: meldingen sier det, og at `--les-inn` ikke leser den |
| BH9, ECH5 | Versjonene 4, 5 og 6 var skrevet inn i testene | low | patch: regnet fra `siste_versjon` |
| BH10 | «2026» var skrevet inn i testen av utskriften | low | patch: fra `DEKKEDE_AAR` |
| ECH6 | Docstringen til `kall_til_nye_forsoek` sa 5 | low | patch |
| BH13 | `boersdag` importeres både som modul og med navn | low | patch: kommentar. Modulen trengs, fordi en test i `test_indeks.py` bytter ut `boersdag.DEKKEDE_AAR` |
| BH1 | Med 15 kall igjen og ingen bonus hentes ingenting, selv om indeksen ellers ikke stopper aksjene | medium | avvist: kontrollpunktet og instruksjonen sier 16 kall også i kvotesjekken, og bonuskvoten fullfører hovedhentingen. 15 igjen og 0 i bonus har ikke skjedd, `extraLimit` er 463 |
| BH2, BH3 | Et unntak utenfor `ValueError`, `BASEFEIL` og `UgyldigSerie` fra indeksen stopper kjøringen | low | avvist: som for aksjene i `hent_universet`. Et bredere unntak ville skjult programmeringsfeil (gjennomgangen av 2.3, BH3) |
| BH5, ECH4 | `query_only` kan slås av etter at adapteren er laget | low | avvist: bare `_aapne_for_sjekken` gir flagget, og den slår aldri av `query_only` |
| BH6 | `mode=ro` kan feile med WAL | low | avvist: basen bruker ikke WAL, og `skrivebeskyttet` finnes i `aapne_base` fra før. En feil gir «Henter likevel», som før |
| BH7 | Kode 0 når bare indeksen feiler, så en varig feil kan gå lenge | low | patch: kode 3, beslutningen 17.10 kl. 11:58. *Rettet 2026-10-17:* ruten var defer, med at morgensjekken kunne se etter linja «Hovedindeksen OSEBX feilet» |
| BH11 | Antallet lagret regnes ved siden av porten | low | avvist: samme funksjon, `bare_boersdager`, som porten bruker |
| BH12 | Spesifikasjonen og testen sier ulikt om versjonen 16.10 | low | avvist: basen sto på 4 med `0005` flettet, altså en bak, og begge sier det |
| BH14 | Nye forsøk holder av et kall til indeksen også når hovedhentingen ikke tok den | low | avvist: svarene 16.10 kl. 18:04 sier 4 kall til nye forsøk |
| ECH2 | En indeks uten dagens rad lagres uten varsel | low | avvist: linja for kallet sier siste dato, og serien byttes ut neste kveld (AD-5). Visningen i 2.9 avgjør hva siden sier |

## Kode 3 (beslutningen 17.10 kl. 11:58)

Instruksjonen kl. 12:07: feiler bare hovedindeksen, gir hentingen kode 3, `KODE_BARE_INDEKSEN`. Koden står i `8b93d83`, spesifikasjonen i `3b0e092` og Rettet-linja i spinen i `5d946f3`. Main ble flettet inn i grenen i `8c118e1`.

**Mutantene,** én om gangen med `-x` og bare `tests/test_fetch_prices.py`, i den ferske klonen med `core.autocrlf=false`, med kopi før og sha256 mot HEAD etter hver. Alle ble fanget på `5d946f3`, og igjen på `a15f234` med K4:
- K1, kode 0 når bare indeksen feiler: `test_et_feilet_indekskall_stopper_ikke_aksjene[feil]`.
- K2, kode 3 foran kode 1: `test_et_feilet_indekskall_stopper_ikke_aksjene[feil]`. Med `-x` stopper kjøringen på første test som feiler, og `test_en_aksje_og_indeksen_feiler_gir_kode_1` kommer senere i fila.
- K3, kode 3 også når indeksen ble lagret: `TestOyeblikksbilde::test_formatet_kan_leses_av_visningen`.
- K4, et nytt forsøk gir 0 etter at indeksen feilet: `test_et_nytt_forsoek_etter_en_aksje_og_indeksen_gir_kode_3`.

**Gjennomgangen** på diffen `8c118e1...5d946f3`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, 2). Rettingene står i `a15f234`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH4, ECH2 | Feiler en aksje og indeksen, gir kjøringen 1, og et nytt forsøk som retter aksjen, gir 0. Feilen med indeksen ser da ut som en vellykket kveld, som BH7 skulle hindre | medium | patch: forsøket gir 3 når kursfila har `indeks` og basen ikke har en serie fra kvelden (`_indeksen_feilet_i_kveld`). Tre tester, og K4 |
| VG1 | Ingen test for at basen ikke kan åpnes for indeksen | low | patch: `test_basen_kan_ikke_aapnes_for_indeksen_gir_kode_3` |
| VG2, ECH3 | Testene viser til K1–K3 i spesifikasjonen, men de sto ikke der | low | patch: avsnittet over |
| BH6, ECH4 | Utskriften lovet 0 kall ved neste kjøring, og det holder ikke når basen ikke kan leses | low | patch: «Indeksen prøves ikke igjen i kveld (AD-15)» |
| BH1 | `kjoer` avslutter med `sys.exit` i stedet for å gi koden tilbake | low | avvist: som kode 1 i `kjoer` fra før, og `main` kaller bare `kjoer` |
| BH2 | `indeksen_feilet` kan være ubundet | low | avvist: variabelen settes i både if og else, og den blokken går alltid foran slutten |
| BH3, BH14 | Et nytt forsøk gir falsk kode 3 eller KeyError, fordi indeksen ikke er hentet | low | avvist: `nytt_forsoek` avslutter kjøringen før slutten av `kjoer`. Hovedhentingen prøver alltid indeksen |
| BH5 | `True` betyr nå «ingen feil», ikke «lagret» | low | avvist: står i docstringen, og `kjoer` er den eneste som kaller |
| BH7 | `navn.lower()` | low | avvist: samme form som «Henter 15 aksjer og hovedindeksen» |
| BH8 | Ingenting som leser utgangskoden, kjenner 3 | low | avvist: ingen skript eller arbeidsflyt i repoet leser koden (VG). Henteinstruksjonen får den fra PR-en |
| BH9 | Diagrammet sier fortsatt 15 | low | avvist: diagrammet sier 16 fra `51cf452`, og linja under forteller hva det sto |
| BH10, BH11 | Den andre kjøringen sjekker ikke koden, og fila slås opp med navn | low | avvist: `kjoer_23` slipper `SystemExit` gjennom, så en annen kode enn 0 feiler testen. Navnet er det `filnavn` gir |
| BH12 | Tilfeller som mangler i testene | low | delvis patch med BH4 og VG1. Resten avvist: `--les-inn` leser ikke indeksen og har ingen kode 3 |
| BH13 | `fp.main(["--ukjent"])` skriver til stderr | low | avvist: pytest fanger utskriften |
| ECH1 | En indeks uten dagens rad gir kode 0 | low | avvist: beslutningen lister kallet, porten og basen. Linja for kallet viser siste dato, som ECH2 i den første gjennomgangen |
