---
title: 'Story 2.8, PR 2 (2.8b): kallet for hovedindeksen i hentingen, 16 kall, og sjekken av basen før kallene'
type: 'feature'
created: '2026-10-17'
status: 'in-review'
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

- **Utgangskoden** er 0 når bare indeksen feiler. Kode 1 betyr i hentingen at samme kommando kjørt igjen samme kveld prøver det som mangler (2.3b), og et nytt forsøk tar ikke indeksen. Utskriften sier at indeksen feilet og ikke prøves igjen før neste kveld, da serien byttes ut for hele året (AD-5).
- **`--les-inn` leser ikke indeksen.** Innlesingen er for kursene når basen feilet. Indeksen hentes for hele året hver kveld og byttes ut, så neste henting gir den igjen. Utsatt, ikke avvist: kommer i en egen story hvis gruppen vil.
- **Sjekken av basen ser bare på aksjene.** Har basen alle aksjene for børsdagen, men ingen indeks, hentes ingenting. Det følger av at indeksen ikke får en ny sjanse (AD-15).
- **Én versjon bak, ikke vilkårlig mange:** beslutningen kl. 22:16 gjelder tilfellet der en ny migrasjon er flettet og basen ennå ikke er migrert. En base som står lenger bak, kan ha et skjema lesingen ikke kjenner, og da er det tryggere å hente og la skrivingen migrere den.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke mot EODHD, og `data/db/ose.db` røres ikke (regel 22). Testene bruker midlertidige baser og falske hentere.
- Den ekte basen migreres til versjon 6 første gang hentingen skriver, mandag 19.10 etter flettingen.
- Flettes ikke uten ja fra gruppen.

**Testtallet før:** 2274 bestått og 17 hoppet over (head-en til PR #56, `59020e2`, samme kode og tester som main etter `1d3a21d`).
