---
title: "Kvalitetssikring"
status: aktiv
created: 2026-10-03
updated: 2026-10-03T14:51
---

# Kvalitetssikring

Hva som er testet i OSE Signal, hvordan, og hva som ikke er det. Dokumentet er
story 9.1 i [`epics.md`](../_bmad-output/planning-artifacts/epics.md). Det skulle
vært skrevet da Epic 1 ble ferdig 28.09, så det dekker alt som er flettet til nå.

**Gjelder for commit `3803b4d`, 03.10.2026.** Tall og status er talt mot den
commiten. Hver påstand har en kilde: en commit, en spesifikasjon i
[`_bmad-output/implementation-artifacts/`](../_bmad-output/implementation-artifacts/),
en dagsfil i [`docs/ai-prompts/`](ai-prompts/) eller en memlogg.

Forkortelser i kildene: `S/` er `_bmad-output/implementation-artifacts/`, og
`D/` er `docs/ai-prompts/`.

## 1. Kort fortalt

- 1074 tester i 22 testfiler. Lokalt på Windows består 1058, og 16 hoppes over.
  I CI på Linux består alle 1074 (kjøring 37072797767 på `74fc69b`, den siste
  på main da dette ble skrevet, med samme tester som `3803b4d`; `D/2026-10-03.md`).
- Testene kan ikke nå nettet. En sperre i `tests/conftest.py` stopper det
  (AD-8), men den dekker ikke hele testkjøringen ennå (§6).
- Hver story med kode er prøvd med mutanter: koden er ødelagt med vilje, og
  en test skal feile. Vedlegget har 197 linjer, én per mutant eller per gruppe
  som kilden bare teller. 18 tilfeller overlevde en stund, og hvert av dem fikk
  en test eller en forklaring (§3).
- Fra story 1.4a fikk hver story med kode en gjennomgang med tre eller fire
  lenser før flettingen, og Epic 1 fikk en samlet gjennomgang etterpå (§5).
- Koden er også kontrollert mot ekte data, og ikke bare mot testdata (§4).
- §6 sier hva som ikke er testet.

## 2. Testene

### Antall

Talt med `uv run pytest --collect-only -q` 03.10.2026, på `3803b4d`:

| Fil | Tester |
|---|---:|
| `test_vurderingslager.py` | 170 |
| `test_fetch_prices.py` | 145 |
| `test_snapshotleser.py` | 133 |
| `test_kurslager.py` | 113 |
| `test_aksje.py` | 59 |
| `test_signalberegning.py` | 52 |
| `test_boersdag.py` | 49 |
| `test_migrering.py` | 49 |
| `test_app.py` | 47 |
| `test_markedsoversikt.py` | 38 |
| `test_konsumentene.py` | 36 |
| `test_meldinger.py` | 30 |
| `test_tilstand.py` | 29 |
| `test_aksjedetalj.py` | 24 |
| `test_tallformat.py` | 23 |
| `test_lagring_sqlite.py` | 20 |
| `test_kursdata.py` | 19 |
| `test_graf.py` | 13 |
| `test_lagring_fil.py` | 13 |
| `test_ingen_nettverk.py` | 6 |
| `test_tidssone.py` | 5 |
| `test_readme.py` | 1 |
| **Sum** | **1074** |

`tests/` har også `conftest.py` og `eodhd_serier.py`, som ikke er testfiler.

Testdataene er kursserier vi har skrevet selv. Testdata som hentes, endrer
seg, og da tester vi børsen i stedet for koden (README, «Tester»).

### CI

[`.github/workflows/tester.yml`](../.github/workflows/tester.yml) kjører
`uv sync --locked` og `uv run pytest -q` på hver push til `main` og hver pull
request mot `main`, på `ubuntu-latest` med Python 3.13. Workflowen har
`permissions: contents: read` og ingen hemmeligheter, så en test kan ikke
bruke API-nøkkelen. CI har kjørt siden 21.09 (`266e6d9`), og fra story 1.4b
(PR #1) også på pull requesten før flettingen. Kjørings-ID-en står i dagsfila,
for eksempel PR #18 og kjøring 36987808151 i `D/2026-10-02.md`.

`morgensjekk.yml` er ingen testkjøring. Den lager morgenrapporten i saken
«Morgensjekk».

### Hoppes over lokalt

16 tester hoppes over på Windows: 14 og 2 i `TestMaskinensSoneSpillerIngenRolle`
i `tests/test_fetch_prices.py`. De kjører hele hentingen med maskinen satt til
`UTC` og `Pacific/Auckland`, og krever `time.tzset`, som ikke finnes på
Windows. Grunnen står i skip-meldingen: «time.tzset finnes ikke her (Windows);
TZ-testene kjoeres i CI». I CI på Linux kjører de (story 2.1, spinen AD-20).

### Nettsperren

`tests/conftest.py` har fixturen `ingen_nettverk`, som gjelder hver test
(`autouse=True`). Den fjerner proxyvariablene og byttet `getproxies` i
`requests` og `urllib`. Den sperrer `socket.getaddrinfo` for alt utenom
loopback, og `socket.socket.connect` og `connect_ex` for alt utenom
127.0.0.1, ::1 og localhost. En test som prøver, feiler med `NettverkISTest`.
Sperren prøves av 6 tester i `tests/test_ingen_nettverk.py`. Proxy-sperren og
DNS-sperren ble tatt bort hver for seg, og testen for den delen feilet
(`982b216`, vedlegget). `connect_ex` og `getproxies` i `urllib` har ingen egen
test (§6).

Grunnen er kvoten: 20 kall i døgnet hos EODHD. En test som kaller et ekte
endepunkt, ville brukt av den på hver push (AD-8, README, «Tester»). Hullene
i sperren står i §6.

En annen autouse-fixture, `stiene_i_tmp_path`, peker `DATA_KATALOG`,
`RAA_KATALOG` og `BASE_STI` mot en midlertidig mappe, så ingen test rører
`data/` (story 2.1b).

### Kontrakttestene

Samme test kjøres mot hver adapter som oppfyller en port:

- `tests/test_kurslager.py`: fixturen med `params=["minne", "sqlite"]` gir
  `MinneKurslager` og `SqliteKurslager` til `TestKurslagerKontrakt`,
  `TestAvvisningEndrerIngenting` og `TestSistHentet`.
- Fixturen med `params=["minne", "sqlite", "snapshot"]` gir i tillegg
  `SnapshotLeser` til `TestKursleserKontrakt` og `TestKursleserSistHentet`
  (story 1.4a).
- `TestKurslagerProtokollen` og `TestKursleserProtokollen` sjekker formen på
  portene: metodenavn og typeangivelser. At hver adapter oppfyller porten,
  sjekkes av `test_oppfyller_protokollen` i de to kontraktklassene, med
  `isinstance` mot protokollen. Den ser bare at metodene finnes.

`Vurderingslager` har bare én adapter, med vilje: reglene for overskriving
skal stå ett sted, i adapterens upsert (`src/vurderingsdata.py`, docstringen).
Den har derfor ingen kontrakttest mot to lagre (§6).

### Vakter i kildeteksten

Noen tester leser koden i stedet for å kjøre den. `tests/test_konsumentene.py`
sjekker at kjernen ikke importerer I/O eller skallet, at portene ikke
importerer adaptere, at `signalberegning.py` bare importerer `kursdata`,
`tallformat` og `vurderingsdata` (story 2.5), og at bare `aapne_base` kobler
til basen (story 2.1b). `tests/test_tidssone.py` avviser `date.today(`,
`datetime.now()` og `astimezone()` uten argument i hele `src/` (story 2.1).
`tests/test_readme.py` sjekker at hver lenke i README peker på noe som finnes.

## 3. Mutantpraksisen

### Hva den er

En test som aldri har feilet, er ikke prøvd. For hvert kontrollpunkt i en
story endres koden med vilje, slik at kontrollpunktet ikke lenger holder. Det
kalles en mutant. Så kjøres hele testsettet, og minst én test skal feile. Én
mutant legges inn om gangen. Koden settes tilbake fra en kopi, ikke med
`git checkout`, fordi det i 1.8 tok med seg kode som ikke var committet
(`S/spec-1-8-hentingen-godtar-bare-det-leseren-kan-lese.md`, Implementation
Notes).

En mutant som overlever, viser et hull. Da kommer en ny test til, eller koden
viser seg å være overflødig. En mutant som feiler av feil grunn, forkastes og
lages på nytt (1.3, under).

Praksisen har strammet seg til underveis. I 1.6 og 1.7 ble koden satt tilbake
med `git checkout` mellom mutantene (`S/spec-1-6-…`, Implementation Notes). Fra
1.8 settes den tilbake fra en kopi, og fra 2.1b sjekkes sha256 av kopien.

### Per story

Én rad per story. Hver mutant står med testene som fanget den, i vedlegget
sist i dokumentet.

| Story | Commit | Linjer i vedlegget | Overlevde eller forkastet | Kilde |
|---|---|---:|---|---|
| 1.1 Migrasjonsløperen | `57a83c5` | 1 | – (versjonsradtesten alene fanget den ikke, skjemakontrollen gjorde) | commitmeldingen; arkitekturens memlogg, linje 74 |
| 1.2 Kursrad, med to senere rettinger av `Kursrad` | `a796214`, `60f2f2b`, `54696d9` | 5 (11 mutanter) | – | commitmeldingene. Sju av dem er bare talt («Sju mutanter proevd») |
| 1.3 SQLite-adapteren | `f4fada0` | 4 (3 og den forkastede) | 1 forkastet | commitmeldingen; memloggen, linje 77 |
| 1.4a Lesegrensen | `04933f6` | 4 | – | `S/spec-1-4a-…`, Implementation Notes |
| 1.4b Konsumentene leser Kursrad | `c5efd05` (#1) | 4 (3 i spesifikasjonen, 6 i refleksjonsloggen) | – | `S/spec-1-4b-…`, linje 78; `docs/reflection-log.md`, 25.09 |
| 1.4c Rydding | `a91ef79` (#2) | 4 | – | `S/spec-1-4c-…`, Implementation Notes |
| 1.5 SnapshotKilde | `23af8db` (#3) | 5 | – | `S/spec-1-5-…`, Implementation Notes |
| 1.5b Løperen herdes | `ef1cca7` (#5) | 19 | 7 overlevde en stund | `S/spec-1-5b-…`, Implementation Notes, Design Notes og triage |
| 1.6 Vurderingslageret | `7dc8a48` (#8) | 27 | 5 overlevde en stund, 1 forkastet som ekvivalent | `S/spec-1-6-…`, Implementation Notes og triage |
| 1.7 De tre tilstandene | `5e9e6ad` (#9) | 10 | – | `S/spec-1-7-…`, Implementation Notes |
| 1.8 Hentingen godtar bare det leseren kan lese | `5c316e8` (#10) | 12 | 1 overlevde en stund | `S/spec-1-8-…`, tabellen i Implementation Notes |
| 1.9 Aksjene i basen | `cfe2977` (#11) | 18 | 1 overlevde en stund | `S/spec-1-9-…`, tabellen i Implementation Notes |
| 2.0 Hentingen lekker ikke nøkkelen | `4b65a3c` (#6) | 17 | 4 overlevde, funnet senere i kodegjennomgangen av Epic 1 | `S/spec-2-0-…`; `S/kodegjennomgang-epic-1.md`, linje 118–120 |
| 2.1 Børsdag i Oslo | `27ae8e3` (#13) | 8 | 1 overlevde en stund | `S/spec-2-1-…`, Implementation Notes og triage |
| 2.1b Basen åpnes ett sted | `9aa6131` (#14) | 15 | – | `S/spec-2-1b-…`, Implementation Notes og triage |
| 2.1c Målingene i vurderingen | `4b7e074` (#16) | 13 | – | `S/spec-2-1c-…`, Verification |
| 2.5 Vurderingen i samme kjøring | `c65f587` (#18) | 17 | 3 lagt til etter gjennomgangen | `S/spec-2-5-…`, Verification og triage |
| 8.0 De rene feilene | `33317df` (#15) | 6 (17 mutanter, 1–12 på én linje) | 2 lagt til etter gjennomgangen | `S/spec-8-0-…`, Implementation Notes og triage |
| 9.0 Fem tester sjekker det de lover | `c2c26ba` (#7) | 6 | – | `S/spec-9-0-…`, Implementation Notes |
| AD-8, nettsperren | `982b216` | 2 | – | commitmeldingen |

**Ingen story mangler.** Lista er satt sammen fra storyene med status `done`
eller `review` i `sprint-status.yaml` (21 storyer) og squash-commitene med
`(#NN)` i git-loggen. 9.3 og 9.4 har ingen rad: de er dokumentasjon og et
eksperiment uten kode i `src/`, og ingen mutanter er kjørt.

**Åpne punkter i kildene** (regel 12):

- **1.4b:** spesifikasjonen fører tre mutanter, én per funksjon som leste
  `slutt` i stedet for `justert_slutt`. Refleksjonsloggen 25.09 sier «Seks
  mutanter». De tre andre er ikke navngitt noe sted.
- **8.0:** mutant 1–12 sto i planen som ble vist i chatten 30.09. Dagsfila
  sier ikke hva de var, så bare antallet står: 17 i alt (`33317df`).
  Spesifikasjonen sier «de tolv fra planen», mens `D/2026-09-30.md` sier «14
  fra planen».
- **2.5:** vedlegget teller 17 kjøringer, M1–M16 der M8 er delt i a og b.
  Utført-linjen i `D/2026-10-02.md` sier 16.
- **1.2, 1.4a, 1.4c, 1.5, 1.7, 1.9, 2.0, 2.1 og 2.1c:** kildene oppgir for
  mange av mutantene hvor mange tester som feilet, men ikke navnene. Det står i
  vedlegget.
- **2.0:** testene i vedlegget er de som var planlagt for hver mutant (Design
  Notes). Implementation Notes sier bare at alle ble fanget av testene for sitt
  kontrollpunkt.
- **2.5, triagen:** spesifikasjonen gir 10 rettet og 8 avvist, mens
  `D/2026-10-02.md` sier 11 rettet og 7 avvist.

### Mutanter som overlevde

Hver mutant som overlevde en stund, med hvordan den ble funnet, testen som
kom til, og commiten. «Funnet av gjennomgangen» betyr at en av lensene i
kodegjennomgangen viste at ingen test ville feilet.

| Story | Hva overlevde | Funnet av | Det som kom til | Commit |
|---|---|---|---|---|
| 1.5b | `BEGIN IMMEDIATE` → `BEGIN`: alle tester besto | mutantkjøringen og gjennomgangen | `TestToMigratorerOverlapper` i 2.1b, to tråder mot samme fil. Kjørt 50 ganger, besto alle, og mutanten feiler nå | `9aa6131` |
| 1.5b | `glob("*.sql")` i katalogvalget: besto på Windows | mutantkjøringen, prøvd på Linux i Docker samme kveld | Koden bruker `iterdir()` med `suffix.lower()`, og CI kjører på Linux | `ef1cca7` |
| 1.5b | LF-normaliseringen fjernet | mutantkjøringen | Ingen test: linjen var overflødig, fordi `read_text()` alt gjør CRLF om til LF, og ble fjernet | `ef1cca7` |
| 1.5b | `ROLLBACK` fjernet etter avvisning | gjennomgangen (VG1) | `assert not base.in_transaction` etter avvisningene, og tre tester fanger den | `ef1cca7` |
| 1.5b | `!=` → `<` i versjonskontrollen | gjennomgangen (2-BH2) | Test for en base som er nyere enn katalogen | `ef1cca7` |
| 1.5b | `TRANSAKSJONSORD = {"COMMIT"}` | gjennomgangen (BH5) | `test_alle_seks_transaksjonsordene_avvises`. Utfallet etterpå er ikke ført | `ef1cca7` |
| 1.5b | `siste_versjon` teller `.sql`-filer med `glob` | gjennomgangen (2-VG2) | `TestSisteVersjon` og testen for en katalog som ikke er i orden | `ef1cca7` |
| 1.6 | B8: sonevakten så bare på `tzinfo` | gjennomgangen (VG1) | Test for en sone uten forskyvning | `7dc8a48` |
| 1.6 | R5: ingen `ROLLBACK` i `skriv` | gjennomgangen (VG2) | Test der en midlertidig trigger stopper `INSERT` | `7dc8a48` |
| 1.6 | R3: `les` godtok et tidspunkt som dato | gjennomgangen (VG3) | Egen test for `les` | `7dc8a48` |
| 1.6 | R6: `styrke=True` ble avvist av summen, ikke av `bool`-kontrollen | gjennomgangen (VG4) | Testtilfellet fikk riktig sum | `7dc8a48` |
| 1.6 | `OverflowError` var ikke testet | gjennomgangen (VG4) | `10**400` testet. Utfallet etterpå er ikke ført | `7dc8a48` |
| 1.8 | En henting som snur rådataene på stedet | gjennomgangen (BH5, ECH1) | `copy.deepcopy` og en usortert serie i `test_raadataene_lagres_uendret` | `5c316e8` |
| 1.9 | `NOT IN` i kontrollen i versjon 2 | gjennomgangen (BH7) | `test_null_i_kursserie_stopper_migrasjonen` | `cfe2977` |
| 2.0 | `adjusted_close` fjernet fra `FELT`, og tekstkontrollen av `date` (to mutanter) | kodegjennomgangen av Epic 1 (B-VG1) | Ingen egen test: koden ble erstattet av `serie_fra_eodhd` i 1.8 (G1), der mutanten «egen regel» gir 30 feil | `5c316e8` |
| 2.0 | En `main` som skriver til en annen katalog | kodegjennomgangen av Epic 1 (B-VG2) | `test_main_skriver_fila_for_norsk_dato_uten_noekkel` i 2.1 (G12) | `27ae8e3` |
| 2.0 | `quote` eller `quote_plus` fjernet fra `_uten_noekkel` | kodegjennomgangen av Epic 1 (B-VG-a) | En nøkkel med mellomrom i 1.8 (G3), 1 feil per mutant | `5c316e8` |
| 2.1 | `hentet = oeyeblikk.isoformat()` | gjennomgangen (BH1) | Ny rad i matrisen med øyeblikket i Europe/Oslo | `27ae8e3` |

Fire tilfeller er ikke talt som overlevende, fordi kilden ikke viser at
mutanten ble kjørt før rettingen:

- **8.0, f-strengen i `_interesseforklaring` og aksen i grafen.**
  Gjennomgangen viste at ingen test ville fanget en tilbakeføring. Mutant 16
  og 17 ble laget etterpå og fanget (`S/spec-8-0-…`, triagerad 1 og 2).
- **2.5, `except BASEFEIL` i `skriv_vurderinger` (G11).** Gjennomgangen viste at
  ingen test lot basen feile etter kursene. To tester kom til, og M14–M16 ble
  laget etterpå og fanget (`S/spec-2-5-…`, triagerad BH3 og VG1).
- **2.1b, den andre `except BASEFEIL`.** Gjennomgangen (VG1) viste hullet, og
  to tester kom til. Mutantene ble fanget etter det (`S/spec-2-1b-…`, triage
  VG1).

### Forkastet

- **1.3, transaksjonsmutanten.** Første forsøk fjernet `BEGIN`, men beholdt
  `COMMIT`. 17 tester feilet på «no transaction is active», altså av feil
  grunn. Mutanten ble forkastet og laget på nytt som autocommit per setning,
  og den nye ble fanget av `test_to_rader_med_samme_dato_avvises[sqlite]`
  (`f4fada0`; arkitekturens memlogg, linje 77).
- **1.6, kontrollen av området 0–3.** Mutanten var ekvivalent: summen av tre
  sjekker er alltid 0–3. Kontrollen ble fjernet (`S/spec-1-6-…`, triage VG4).

## 4. Kontrollregning på ekte data

Testene bruker serier vi har skrevet selv. Noen ganger er koden i tillegg
kjørt på ekte øyeblikksbilder, og bare antall og utfall er ført. Skriptene og
resultatene ligger i `data/`, som aldri committes (regel 10 og 16).

| Dato | Story | Hva | Utfall | Kilde |
|---|---|---|---|---|
| 25.09 | 1.4b | Oversikten, de 15 detaljene og HTML for 16 sider, på et låst øyeblikksbilde, før og etter endringen | 15 av 15 rader, 15 av 15 detaljer og 16 av 16 sider like | commitmeldingen til `c5efd05`; `docs/reflection-log.md`, 25.09 |
| 25.09 | 1.4c | Samme øyeblikksbilde og samme kontroll | Etter rettingene og uten tidsstemplene: 15 av 15 rader og detaljer, og 15 av 16 sider like. Den ene forskjellen var CSS-regelen for radens tidsstempel | `S/spec-1-4c-…`, linje 94–97 |
| 25.09 | 1.5 | Samme kontroll, med skriptet uendret (sha256 ført før og etter) | 15 av 15, 15 av 15 og 16 av 16 like, også tidsstemplene | `S/spec-1-5-…`, linje 87–91 |
| 29.09 | 2.1b | Et ekte øyeblikksbilde lest inn i en midlertidig base | 15 serier, 250 rader per symbol, 0 vurderinger | `S/spec-2-1b-…`, linje 146 |
| 29.09 | – | Tre rådatafiler flyttet til `data/raa/` | sha256 lik før og etter for alle tre, seriene like for 15 av 15 | `D/2026-09-29.md` |
| 29.09 | – | Den første ekte hentingen, etterkontroll | 15 kall, 250 rader per symbol, `hentet` lik fila for 15 av 15 | `D/2026-09-29.md`, kl. 22:26 |
| 29.09 | – | Basen sammenlignet med øyeblikksbildet den kom fra | Først 0 av 15 like: fila har noen hele kurser som heltall. Som `Kursrad` 15 av 15 like, og ingen verdi avvek | `D/2026-09-29.md`, kl. 22:32; `docs/reflection-log.md` |
| 30.09 | – | Daglig henting, etterkontroll | Serien byttet ut, ikke skjøtt på (AD-5): samme radtall, første dato flyttet én dag. Ingen kopi av basen er nevnt | `D/2026-09-30.md` |
| 01.10 | – | Daglig henting, etterkontroll | Kopi av basen tatt, uten ført sha256. Byttet ut, ikke skjøtt på, kontrollert mot kopien | `D/2026-10-01.md` |
| 01.10 | 2.1c | Signalet før og etter, på et ekte øyeblikksbilde | Styrke, retning og de tre verdiene like for alle 15. Bare teksten for interesse ulik, som ventet | `S/spec-2-1c-…`, linje 107 |
| 02.10 | 2.5 | `vurder()` på et ekte øyeblikksbilde, uten nett og uten basen | 15 av 15 gir en `Vurdering`, ingen gir en grunn | `S/spec-2-5-…`, Implementation Notes |
| 02.10 | – | Den første hentingen med vurderinger, etterkontroll | Kopi med samme sha256 som basen. Byttet ut, ikke skjøtt på. 15 vurderinger lest tilbake med `SqliteVurderingslager.les`, ingen med grunn | `D/2026-10-02.md`, kl. 22:37 |

Kontrollregningen fanger ikke alt. I 1.4b ble tilfellet med en `hentet` som
ikke kan leses, funnet av gjennomgangen og ikke av kontrollregningen
(`docs/reflection-log.md`, 25.09).

## 5. Kodegjennomganger og kontroller

### Gjennomgangen av hver story

Hver story med spesifikasjon ble gjennomgått før flettingen med Blind Hunter,
Edge Case Hunter og Verification Gap, og noen også med Acceptance Auditor.
Det gjelder fra 1.4a. Funnene står i «Review Triage Log» i spesifikasjonen, med dom og rute for hvert
funn. Antall rader i loggen:

| Story | Rader | Rettet | Avvist | Utsatt |
|---|---:|---:|---:|---:|
| 1.4a | 13 | 3 | 9 | 1 |
| 1.4b | 11 | 5 | 6 | – |
| 1.4c | 12 | 3 | 8 | 1 |
| 1.5 | 13 | 3 | 9 | 1 |
| 1.5b, del 1 | 25 | 14 | 6 | 5 |
| 1.5b, del 2 | 22 | 21 | 1 | – |
| 1.6 | 41 | 24 | 10 | – |
| 1.7 | 16 | 10 | 6 | – |
| 1.8 | 13 | 8 | 5 | – |
| 1.9 | 15 | 10 | 5 | 1 |
| 2.0 | 26 | 24 | 2 | – |
| 2.1 | 13 | 5 | 8 | – |
| 2.1b | 20 | 9 | 11 | – |
| 2.1c | 15 | 8 | 7 | – |
| 2.5 | 18 | 10 | 8 | – |
| 8.0 | 17 | 9 | 7 | 1 |
| 9.0 | 11 | 4 | 7 | – |

Noen rader slår sammen flere funn, så kolonnene summerer ikke alltid til
radtallet. 1.6 har i tillegg seks rader med «ingen endring», og BH2 ble avvist
for 1.6, men ført i `deferred-work.md` for 2.5. 1.9 har 18 funn i 15 rader:
13 funn ble rettet i 10 rettinger, og BH11 ble både rettet i spinen og utsatt
for `docs/innlevering.md`. 1.1–1.3 har ingen spesifikasjon, og en gjennomgang av dem
23.09 står i `S/kodegjennomgang-epic-1.md`. Tallene for 8.0 ble rettet etter
tabellen 03.10.

### Kodegjennomgangen av Epic 1

[`S/kodegjennomgang-epic-1.md`](../_bmad-output/implementation-artifacts/kodegjennomgang-epic-1.md),
27.09. Hele diffen fra `57a83c5^` til `8fa254f` ble delt i to, og hver del
fikk fire lenser: Blind Hunter, Edge Case Hunter, Verification Gap og
Acceptance Auditor. Lensene fant 61 funn. Etter sortering sto 14 igjen,
samlet i G1–G12:

- G1–G5 og G8 ble rettet i 1.8 (`5c316e8`).
- G10 ble løst i 1.9 (`cfe2977`) og 2.1b.
- G11 ble tatt i 2.5, og G12 i 2.1.
- G6 ble avvist, og G7 var ikke et funn.
- G9 venter på story 4.0.

Tellingen nederst i dokumentet ble rettet 03.10, fordi den regnet G11 og G12
som ventende.

### Kontrollen 22.09

[`docs/kontroll-2026-09-22.md`](kontroll-2026-09-22.md) kontrollerte alt som
ble endret 22.09: 22 commits i 15 filer. Fire lenser gikk i hvert sitt
kontekstvindu: påstander om koden, kryssreferanser, omskrevne krav, og tall og
tidsstempler. Lensene oppga 35 feil. Talt på nytt 23.09 ble det 31 distinkte.
Rapporten samler dem under A1–A14, uten å si hvilken lens hvert funn kom fra,
så de 31 kan ikke kobles én og én til A-punktene. Rettingene ble foreslått i
[`docs/kontroll-2026-09-22-plan.md`](kontroll-2026-09-22-plan.md):

| Funn | Rettet i | Dato |
|---|---|---|
| A1, A2, A3, A5, A6, A7 og A12 | `a2a9c0c` | 22.09 |
| A4 | `a2a9c0c`, `61df5b9` og `a08d8e1` | 22.09 |
| A9 | `a2a9c0c`, `cfbee46`, `6c3e095`, `d408e9e` og `e0980e7` | 22.–24.09 |
| A11 | `a2a9c0c` og `4d4321e` | 22.–23.09 |
| A8 | `571dcc2` | 23.09 |
| A10 | `f7acedf` | 23.09 |
| A13 | `6ffa556` | 23.09 |
| U1–U4, de fire uenighetene | `94fd482`, `3c78c8a`, `5a056fd` og `027866a` | 23.09 |
| A14, to `updated`-felter | ikke funnet i noen commit | – |

Del B hadde 16 uklare punkter. Bare B5 er sporet med nummer: det ble U3
(`5a056fd`). Noen av de andre ser ut til å være tatt i senere rettinger av
PRD-en, som `e0980e7` (punkt 10 lukket, «reservealternativet» for punkt 19) og
`4d4321e` (eieroppsummeringen), men commitene viser ikke til B-numrene. Tabellen er satt sammen
03.10 fra commitmeldingene og `git log -S`.

### Kontrollen 26.09

[`docs/kontroll-2026-09-26.md`](kontroll-2026-09-26.md) kontrollerte hele
repoet 26.09 mot `7af4992`, og det som sto igjen, ble slått opp på nytt mot
`802ab16` natt til 27.09. Fem lenser oppga 122 funn, og 105 var distinkte.
**Tallene gjelder 26.–27.09:**

| Utfall | Antall |
|---|---:|
| Rettet 26.09 | 22 |
| Delvis rettet | 3 |
| Utsatt til en egen story for testene | 3 |
| Spørsmål til gruppa | 2 |
| Ikke funn likevel | 3 |
| Usikker | 1 |
| Står igjen | 71 |
| **Sum** | **105** |

**De 71 som sto igjen, er ikke kontrollert på nytt siden 27.09.** Ingen commit
etter 27.09 viser til rapporten eller til numrene i den, og dagsfilene fra
28.09 til 02.10 nevner den ikke. De tre som ble utsatt, og K3 og K4 ble tatt i
story 9.0 (`c2c26ba`, 27.09), og D11 ble rettet i `1f7336d` samme dag. Minst
tre av de 71 er altså lukket. Noen funn hører til storyer som er bygget siden,
som K8 til 2.1, men ingen har ført om de er lukket.

*Rettet 2026-10-03:* alle 74 punktene under «Står igjen» er slått opp på nytt mot `9214a95`. 5 var lukket, 6 delvis og 63 sto. Ni av dem ble rettet samme dag, og etter det er 14 lukket, 6 delvis og 54 står. Ni av dem som står, venter på en story og har punkt i `deferred-work.md`. Tolv gjelder meldinger og plan A, som er utenfor v1. Tabellen står i [«Etterkontroll 03.10»](kontroll-2026-09-26.md#etterkontroll-0310).

*Rettet 2026-10-03, senere samme dag:* seks til ble rettet (P3, P5, P6, P11, P13 og E6). Nå er 20 lukket, 4 delvis og 50 står. P9, P10, P12 og E8 er spørsmål til gruppa.

### Det som står igjen i `deferred-work.md`

[`S/deferred-work.md`](../_bmad-output/implementation-artifacts/deferred-work.md)
har sju punkter uten `resolved:` 03.10:

| Fra | Hva | Venter på |
|---|---|---|
| 1.4b | Forsiden sier «Ingen kursdata funnet» når `hentet` ikke kan leses | 2.2 |
| 1.4c | Datoen over tabellen kan motsi sidens eldste tidsstempel | ingen story navngitt |
| 1.4c | Hvordan tiden merkes på ferske og foreldede rader (UX-spørsmål) | 8.2 |
| 1.5 | Et ødelagt øyeblikksbilde gir 500 på alle sidene | 2.2 |
| 1.5b | `migrer()` krever skrivetilgang også når basen er oppdatert (ubekreftet) | 3.1 |
| 1.9 | `docs/innlevering.md` nevner bare `0001_kurs.sql` | ingen story navngitt |
| 8.0 | Aksen i kursgrafen har 0 desimaler | 8.2 |

*Rettet 2026-10-03:* ni punkter fra kontrollen 26.09 ble lagt til samme dag (`1635bab`), så 16 står nå uten `resolved:`. De ni venter på story 4.0, 2.3 eller 2.4, 3.1, Epic 3, neste endring i CI og neste story som rører filene (§5, «Kontrollen 26.09»).

## 6. Hva som ikke testes

- **Den ekte `hent_ett_symbol`.** Det er den eneste funksjonen som når nettet,
  og hvert kall bruker kvote (docstringen i `src/fetch_prices.py`). Testene
  kjører den bare med `requests.get` byttet ut (`tests/test_fetch_prices.py`).
  Om EODHD svarer som vi venter, prøves bare av den daglige hentingen (§4).
- **Nettsperren dekker ikke hele testkjøringen.** Den er en autouse-fixture med
  funksjonsscope og gjelder bare inne i testfunksjonene. En fixture med
  `scope="module"` nådde nettet 23.09, og `gethostbyname`, `gethostbyname_ex`
  og `getfqdn` er ikke sperret. Story 4.0 skal rette det, og legge til tester
  for `connect_ex` og en fixture med module-scope (`epics.md`, story 4.0).
  Sperren stopper heller ikke UDP. Det er K11 i kontrollen 26.09, og rapporten
  legger det til story 4.0 (`docs/kontroll-2026-09-26.md`, linje 211 og 443).
- **TZ-testene lokalt.** De 16 testene som hoppes over på Windows, kjøres bare
  i CI (§2).
- **Vurderingslageret mot to adaptere.** Det finnes bare `SqliteVurderingslager`,
  med vilje (§2).
- **Skriptene for morgensjekken.** `.github/scripts/morgensjekk.py` og
  `morgenrapport.py` har ingen tester.
- **Det appen viser fra basen.** Webserveren leser fortsatt øyeblikksbildene,
  ikke basen (README, «Kom i gang»). Vurderingene som lagres fra 02.10, vises
  ikke ennå (story 2.2 og 2.7).
- **Det som ikke er bygget.** Docker finnes ikke (ingen `Dockerfile`).
  KI-laget er ikke bygget (Epic 10), og `src/` har ingen KI-kode.
  Børsdagskontrollen (2.3) og hovedindeksen (2.8) er ikke bygget.
- **Brukere.** Ingen brukertest er gjort ennå (story 8.1). Sidene er bare
  prøvd med Flask sin testklient, ikke i en nettleser.
- **To kontroller for hånd** står som gjenstående i `malinger.md` §6: de tre
  sjekkene i et regneark, og kursene mot Oslo Børs. Ingenting viser at de er
  gjort. Sluttverdien for OSEBX er kontrollert for hånd én gang (`malinger.md`
  §14).
- **De 71 punktene fra kontrollen 26.09** er ikke kontrollert på nytt. Minst
  tre av dem er lukket (§5).
  *Rettet 2026-10-03:* de er kontrollert på nytt. Etter rettingene samme dag er
  14 av de 74 lukket, 6 delvis og 54 står (§5, og «Etterkontroll 03.10» i
  [`docs/kontroll-2026-09-26.md`](kontroll-2026-09-26.md#etterkontroll-0310)).
  *Rettet 2026-10-03, senere samme dag:* nå er 20 lukket, 4 delvis og 50 står.

## 7. Hvordan KI-arbeidet kontrolleres

Rollene og hvem som avgjør hva, står i «Arbeidsmønsteret» i
[`docs/ai-prompts/README.md`](ai-prompts/README.md), og skrives ikke om her.
Hver innlimte instruksjon går gjennom en forhåndskontroll: byggeøkta slår opp
påstandene i repoet før noe skrives, og stopper og sier fra når noe ikke
stemmer (regel 3 i `CLAUDE.md`). To eksempler står i
[`docs/reflection-log.md`](reflection-log.md): «Oppslaget fant feilene
instruksjonene hadde» (24.09) og «Seks stopp på to dager» (30.09–01.10).

## 8. Slik holdes dokumentet oppdatert

Dokumentet oppdateres ved hver epic, sammen med kodegjennomgangen av den
(story 9.1, «Tidspunkt»):

1. Testene telles på nytt med `uv run pytest --collect-only -q`, og tallet og
   CI-kjøringen i §1 og §2 settes på nytt.
2. Hver ny story får en rad i tabellen i §3 og én linje per mutant i
   vedlegget. Mutanter som overlevde, føres i lista i §3.
3. Kontrollregninger og etterkontroller fra dagsfilene føres i §4.
4. Triageloggen i hver ny spesifikasjon telles inn i §5, og lista fra
   `deferred-work.md` tas på nytt.
5. §6 gås gjennom: det som er bygget, tas ut, og nye hull føres inn.
6. Commiten og `updated` øverst settes på nytt.

**Fra 03.10 navngir hver spesifikasjon hver mutant og testen som fanget den**,
så dokumentet kan oppdateres uten hull. Det var ikke gjort for alle storyene
før 03.10 (§3, «Åpne punkter i kildene»).

## Vedlegg: hver mutant

Én linje per mutant: storyen, mutanten slik kilden beskriver den, testene som
fanget den, og kilden. Der kilden ikke navngir mutanten eller testen, står
det. Linjene er hentet fra spesifikasjonene og commitmeldingene 03.10.

| Story | Mutanten | Fanget av | Kilde |
|---|---|---|---|
| 1.1 | `_kjoer` byttet midlertidig til `executescript()` | 3 av 6 i `TestFeilMidtveis`, av riktig grunn; versjonsradtesten alene fanget den ikke | `57a83c5`; architecture-memlog `.memlog.md:74` |
| 1.2 | `dict` sluppet inn i lageret | fanget, ikke navngitt i kilden | `a796214`; architecture-memlog `.memlog.md:75` |
| 1.2 | tekst som dato | fanget, ikke navngitt i kilden | `a796214`; architecture-memlog `.memlog.md:75` |
| 1.2 | `hentet` uten tidssone | fanget, ikke navngitt i kilden | `a796214`; architecture-memlog `.memlog.md:75` |
| 1.2 | `Kursrad` uten `isfinite` | de seks nye avvisningstestene (NaN, inf, -inf i begge feltene), ingen andre | `60f2f2b` |
| 1.2 | sju mutanter for `UgyldigKursrad`, ikke navngitt i kilden | alle fanget; testene ikke navngitt i kilden | `54696d9` |
| 1.3 | autocommit per setning (ingen `BEGIN`/`COMMIT`) | `test_to_rader_med_samme_dato_avvises[sqlite]` alene | `f4fada0`; architecture-memlog `.memlog.md:77` |
| 1.3 | skjøter (ingen `DELETE`) | `test_erstatt_serie_erstatter_ikke_skjoeter[sqlite]` alene | `f4fada0`; architecture-memlog `.memlog.md:77` |
| 1.3 | tom serie sluppet gjennom | 4 tester: begge tom-serie-testene i begge lagre | `f4fada0`; `36cb171` |
| 1.3 | første transaksjonsmutant: fjernet `BEGIN`, beholdt `COMMIT` | forkastet: 17 tester feilet av feil grunn («no transaction is active»); laget på nytt | `f4fada0`; architecture-memlog `.memlog.md:77` |
| 1.4a | `rad.get("adjusted_close", rad["close"])` i `kursrad_fra_eodhd` («Ville feilet hvis») | 3 tester, ikke navngitt i kilden | `spec-1-4a-*.md:73` (Implementation Notes) |
| 1.4a | like datoer slipper gjennom | 1 test, ikke navngitt i kilden | `spec-1-4a-*.md:73` |
| 1.4a | tid uten serie | 22 tester, blant dem «hvis og bare hvis»-testen (ukjent symbol gir tid) | `spec-1-4a-*.md:73`; triage rad 6, `:88` |
| 1.4a | `hentet` uten sone gir likevel serier | 6 tester, ikke navngitt i kilden | `spec-1-4a-*.md:73` |
| 1.4b | `slutt` i stedet for `justert_slutt` i `signalberegning` | fanget («alle fanget»), testene ikke navngitt i kilden | `spec-1-4b-*.md:78` (AC); `c5efd05` |
| 1.4b | `slutt` i stedet for `justert_slutt` i `endring_i_prosent` | fanget («alle fanget»), testene ikke navngitt i kilden | `spec-1-4b-*.md:78` (AC); `c5efd05` |
| 1.4b | `slutt` i stedet for `justert_slutt` i `bygg_punkter` | fanget («alle fanget»), testene ikke navngitt i kilden | `spec-1-4b-*.md:78` (AC); `c5efd05` |
| 1.4b | tre til, ifølge refleksjonsloggen 25.09 («Seks mutanter») | ikke navngitt i kilden | docs/reflection-log.md:2260 |
| 1.4c | sidens tidsstempel er det nyeste | 2 tester, ikke navngitt; fanget også etter rettelsene | `spec-1-4c-*.md:95–96` |
| 1.4c | UTC vises i stedet for norsk tid | 11 tester, ikke navngitt; fanget også etter rettelsene | `spec-1-4c-*.md:95–96` |
| 1.4c | radens tidsstempel vises aldri | 1 test, ikke navngitt; fanget også etter rettelsene | `spec-1-4c-*.md:95–96` |
| 1.4c | fast +2 timer i stedet for `Europe/Oslo` | 3 tester, ikke navngitt; fanget også etter rettelsene | `spec-1-4c-*.md:95–96`; reflection-log.md:2302 |
| 1.5 | `nyeste_snapshot` velger med `max` over `(dato, sti)` | 2 tester, ikke navngitt i kilden | `spec-1-5-*.md:92` |
| 1.5 | `app.py` kaller `nyeste_snapshot()` direkte | 3 tester (vakten), ikke navngitt i kilden | `spec-1-5-*.md:92` |
| 1.5 | `"adjusted_close"` lagt tilbake i `kursdata.py` | 2 tester, ikke navngitt i kilden | `spec-1-5-*.md:92` |
| 1.5 | `kursdata.py` importerer en adapter | `test_porten_importerer_verken_io_eller_adapter`; import på modulnivå gir i tillegg sirkulær import | `spec-1-5-*.md:92` |
| 1.5 | `app.py` gir `DATA_KATALOG` til `nyeste_leser` selv (femte, etter gjennomgangen) | vakten for `app.py` | `spec-1-5-*.md:93` |
| 1.5b | filnavnsjekken fjernet (a) | testene for punktet, ikke navngitt i kilden | `spec-1-5b-*.md:196` (Design Notes), `:97` |
| 1.5b | forhåndssjekken fjernet (b) | testene for `COMMIT` | `spec-1-5b-*.md:196`, `:97` |
| 1.5b | forhåndssjekken ser på hele setningen, ikke første ord (b) | triggertesten | `spec-1-5b-*.md:196`, `:97` |
| 1.5b | sjekken skiller store og små bokstaver (b) | testen med «commit;» | `spec-1-5b-*.md:196`, `:97` |
| 1.5b | `in_transaction`-sjekken fjernet, forhåndssjekken slått av (b) | testen for ekstra sikring | `spec-1-5b-*.md:196`, `:97` |
| 1.5b | `TRANSAKSJONSORD = {"COMMIT"}` (b) | overlevde først; rettet med `test_alle_seks_transaksjonsordene_avvises` (utfallet etterpå ikke ført) | `spec-1-5b-*.md:130` (BH5), `:92` |
| 1.5b | `ROLLBACK` fjernet etter avvisning | overlevde først, fanget av tre tester etter `assert not base.in_transaction` | `spec-1-5b-*.md:146` (VG1) |
| 1.5b | kravet tilbake til `versjon < 1` (c) | testen for eldre versjon | `spec-1-5b-*.md:106`, `:196` |
| 1.5b | kontrollen av nyere base fjernet, `!=` → `<` (c) | overlevde først, fanget etter ny test for nyere versjon | `spec-1-5b-*.md:107`, `:158` (2-BH2) |
| 1.5b | `MigrasjonsFeil` pakkes ikke inn | testen for katalog som ikke er i orden | `spec-1-5b-*.md:108` |
| 1.5b | `siste_versjon` teller `.sql`-filer med `glob` | `TestSisteVersjon` og testen for katalog som ikke er i orden; fanget etter rettelsen 2-VG2 | `spec-1-5b-*.md:109`, `:176` |
| 1.5b | `COMMIT` før skrivingen til `kursserie` (d) | begge d-testene; de gamle testene besto | `spec-1-5b-*.md:110`, `:191–194` |
| 1.5b | `CREATE TABLE skjema_versjon` før `BEGIN` (h, første test) | den nye h-testen; de gamle testene besto | `spec-1-5b-*.md:192–194` |
| 1.5b | adapteren lager en tabell før kontrollen (h, andre test) | h-testen; den gamle h-testen fra `f5516d5` besto | `spec-1-5b-*.md:111`, `:193` |
| 1.5b | hashsjekken fjernet (e) | testene for punktet, ikke navngitt i kilden | `spec-1-5b-*.md:196`, `:97` |
| 1.5b | LF-normaliseringen fjernet (e) | overlevde: linjen var overflødig og er fjernet | `spec-1-5b-*.md:94` |
| 1.5b | `_tekst` leser rå bytes (e) | CRLF-testen | `spec-1-5b-*.md:94` |
| 1.5b | `BEGIN IMMEDIATE` byttet med `BEGIN`, lest utenfor (f) | overlevde; utsatt (`deferred-work.md`), fanget i 2.1b av `TestToMigratorerOverlapper` (`9aa6131`) | `spec-1-5b-*.md:97`, `:148` (VG3) |
| 1.5b | tilbake til `glob("*.sql")` (g) | overlevde på Windows; på Linux (Docker) `TestKatalogkontrollen::test_stor_filendelse_avvises_likt_paa_alle_plattformer` | `spec-1-5b-*.md:97` |
| 1.6 | B1: 2026-04-06 fjernet fra `STENGT` | påsketesten for 04-06 og testen mot dokumentet | `spec-1-6-*.md:115` |
| 1.6 | B2: 2026-04-01 lagt til i `STENGT` | halvdagstesten, påsketestene og testen mot dokumentet | `spec-1-6-*.md:116` |
| 1.6 | B3: årsvakten fjernet | 2026-01-01-testen og begge testene for dager utenfor 2026 | `spec-1-6-*.md:117` |
| 1.6 | B4: årsvakten sjekker uka rundt nyttår | 2026-01-02-testen; 2026-01-01-testen feiler på meldingen | `spec-1-6-*.md:118` |
| 1.6 | B5: lørdag regnes som hverdag | helgetestene, påsketestene 04-04 til 04-06, testen for 12-26; senere også 2. pinsedag | `spec-1-6-*.md:119`, `:128` |
| 1.6 | B6: datoen regnes i UTC | begge 00:30-testene og testen med tidspunkt i Oslo | `spec-1-6-*.md:120` |
| 1.6 | B7: et tidspunkt godtas som dag | testen for `datetime` | `spec-1-6-*.md:121` |
| 1.6 | B8: sonevakten ser bare på `tzinfo` | overlevde først, fanget etter ny test for en sone uten forskyvning | `spec-1-6-*.md:125`, `:180` (VG1) |
| 1.6 | B9: 2027 i `DEKKEDE_AAR` uten dagene for 2027 | testen for 2027-01-04 og testen for at lista og årene stemmer | `spec-1-6-*.md:126` |
| 1.6 | K1: datokontrollen fjernet | 6 tester (i går, i morgen, lørdag, 00:30 i begge tider, gårsdagens rad neste dag) | `spec-1-6-*.md:139` |
| 1.6 | K1: UTC i stedet for Oslo | begge 00:30-testene og testen for en klokke uten sone | `spec-1-6-*.md:140` |
| 1.6 | K2: `INSERT` uten `ON CONFLICT` | de fire testene for overskriving | `spec-1-6-*.md:141` |
| 1.6 | K3: `endre` i protokollen | testen for protokollen og testen for at adapteren oppfyller den | `spec-1-6-*.md:142` |
| 1.6 | K4: `erstatt_serie` sletter fra `vurdering` | testen for at vurderingen overlever | `spec-1-6-*.md:143` |
| 1.6 | K5: tabellen lages av adapteren | 25 tester (24 i `TestSkjemaet`, åpen transaksjon); senere 28 | `spec-1-6-*.md:144`, `:159` |
| 1.6 | K6: `WHERE` fjernet | testen for grunn over vurdering | `spec-1-6-*.md:145` |
| 1.6 | K6: `WHERE` som stopper vurdering over grunn | testene for vurdering over grunn og grunn over grunn | `spec-1-6-*.md:146` |
| 1.6 | K6: triggerne fjernet | de tre testene for ukjent grunn; senere 4 | `spec-1-6-*.md:147`, `:159` |
| 1.6 | K6: `CHECK` fjernet | 16 tester for enten/eller; senere 17 | `spec-1-6-*.md:148`, `:159` |
| 1.6 | R1: triggerne på `grunn` fjernet | de to testene for sletting og endring | `spec-1-6-*.md:152` |
| 1.6 | R2: retningen kontrolleres ikke mot sjekkene | alle 27 retningstestene | `spec-1-6-*.md:153` |
| 1.6 | R3: `les` kontrollerer ikke symbol og dato | de to testene for `les`; datodelen overlevde først (VG3) | `spec-1-6-*.md:154`, `:209` |
| 1.6 | R4: kursen gjøres ikke om til float | de to testene for store heltall | `spec-1-6-*.md:155` |
| 1.6 | R5: ingen tilbakerulling i `skriv` | overlevde først (VG2), fanget av testen for tilbakerullingen | `spec-1-6-*.md:156`, `:208` |
| 1.6 | R6: `bool` godtas som styrke | overlevde først (VG4), fanget av testen for `styrke=True` | `spec-1-6-*.md:157`, `:210` |
| 1.6 | kontrollen av området 0–3 | forkastet: ekvivalent mutant; kontrollen fjernet, summen dekker den | `spec-1-6-*.md:210` (VG4) |
| 1.6 | `OverflowError` utestet | overlevde først; `10**400` testet etter rettelsen (utfallet etterpå ikke ført) | `spec-1-6-*.md:210` (VG4) |
| 1.7 | T1: styrke 0 som fravær | 3 tester, blant dem testen for styrke 0 og for fire forskjellige verdier | `spec-1-7-*.md:93` |
| 1.7 | T2: `None` for begge fravær | 14 tester, ikke navngitt i kilden | `spec-1-7-*.md:94` |
| 1.7 | T3: fraværene byttet | 11 tester, ikke navngitt i kilden | `spec-1-7-*.md:95` |
| 1.7 | T4: grunn som fravær | 5 tester, blant dem de tre grunnene | `spec-1-7-*.md:96` |
| 1.7 | T5: egen kalender som bare ser på ukedagen | 4 tester (langfredag, julaften, de to årene utenfor lista) | `spec-1-7-*.md:97` |
| 1.7 | T6: fremtiden godtas | de 3 testene for fremtid | `spec-1-7-*.md:98` |
| 1.7 | T7: `er_boersdag` gjetter utenfor lista | 4 tester, i `test_boersdag.py` og `test_tilstand.py` | `spec-1-7-*.md:99` |
| 1.7 | T8: kalenderen før raden | testen for at raden går foran | `spec-1-7-*.md:100` |
| 1.7 | T9: datoen kontrolleres før typen | testen for feil innhold med en dato etter i dag | `spec-1-7-*.md:104`, `:120` (BH7) |
| 1.7 | T10: `tilstand.py` importerer `lagring_sqlite` | vakten mot skallet i `test_konsumentene.py` | `spec-1-7-*.md:105`, `:115` (BH2) |
| 1.8 | M1: hentingen med sin egen regel (`fetch_prices.py` fra baseline) | 30 feil: testene over lista, strukturtesten og strengvakten | `spec-1-8-*.md:94` |
| 1.8 | M2: hentingen hopper over kontrollen og lagrer rådataene | 54 feil: alle 27 i begge testene over lista | `spec-1-8-*.md:95` |
| 1.8 | M3: seriefunksjonen sjekker ikke like datoer | 6 feil, for leseren og hentingen | `spec-1-8-*.md:96` |
| 1.8 | M4: `rader[-1]['date']` tilbake i utskriften | 1 feil: strengvakten for `fetch_prices.py`. Etter ECH2 fanger også utskriftstesten den | `spec-1-8-*.md:97` |
| 1.8 | M5: den oversatte serien lagres | 29 feil: rådatatesten, `test_formatet_kan_leses_av_visningen` og alle 27 gjennom `kjoer` | `spec-1-8-*.md:98` |
| 1.8 | M6: `UgyldigSerie` for `[]` | 2 feil: «tomt svar» i hentingen og testen for funksjonen | `spec-1-8-*.md:99` |
| 1.8 | G2: en 16. aksje i `AKSJEUNIVERS` | de nye testene består (81 av 81); testene fra før G2 gir 5 feil | `spec-1-8-*.md:100`, `:124` (BH8) |
| 1.8 | G3: `quote` fjernet fra `_uten_noekkel` | 1 feil, i sin parametrisering | `spec-1-8-*.md:101` |
| 1.8 | G3: `quote_plus` fjernet fra `_uten_noekkel` | 1 feil, i sin parametrisering | `spec-1-8-*.md:101` |
| 1.8 | G5: `finn_styrke` uten `abs` | 22 feil, 19 i testen over de 27 kombinasjonene | `spec-1-8-*.md:102` |
| 1.8 | G5: `beregn_signal` summerer selv uten `abs` | 4 feil, blant dem de to seriene med negative sjekker i `TestStyrke` | `spec-1-8-*.md:103` |
| 1.8 | en henting som snur rådataene på stedet | overlevde først, fanget etter `copy.deepcopy` og usortert serie i `test_raadataene_lagres_uendret` | `spec-1-8-*.md:121` (BH5/ECH1) |
| 1.9 | M1: MPCC mangler i 0003 | 1 feil: testen mot `AKSJEUNIVERS` | `spec-1-9-*.md:98` |
| 1.9 | M2: `Var Energi` i stedet for `Vår Energi` | 1 feil: testen mot `AKSJEUNIVERS` | `spec-1-9-*.md:99` |
| 1.9 | M2b: EQNR og DNB byttet om | 1 feil: testen mot `AKSJEUNIVERS` | `spec-1-9-*.md:100` |
| 1.9 | M3: INSERT-triggeren på `kurs` mangler (`WHEN 0`) | 5 feil: alle fem ukjente symboler i `kurs`; etter ECH1 også adaptertesten | `spec-1-9-*.md:101`, `:125` |
| 1.9 | M4: triggeren på `kursserie` med `NOT IN` | 1 feil: NULL-testen | `spec-1-9-*.md:102` |
| 1.9 | M5: INSERT-triggeren på `vurdering` mangler | 5 feil, ikke navngitt i kilden | `spec-1-9-*.md:103` |
| 1.9 | M6: UPDATE-triggeren mangler, på `kurs`, `kursserie` og `vurdering` hver for seg | 1 feil hver, ikke navngitt i kilden | `spec-1-9-*.md:104` |
| 1.9 | M7: slettetriggeren sjekker bare `kurs` | 2 feil: rad bare i `kursserie`, og bare i `vurdering` | `spec-1-9-*.md:105` |
| 1.9 | M7b: slettetriggeren mangler | 1 feil: rad bare i `kurs` | `spec-1-9-*.md:106` |
| 1.9 | M8: triggeren for endret symbol mangler | 2 feil: med og uten rader | `spec-1-9-*.md:107` |
| 1.9 | M8b: REPLACE-triggeren for INSERT mangler | 4 feil, ikke navngitt i kilden | `spec-1-9-*.md:108` |
| 1.9 | M8c: REPLACE-triggeren for UPDATE mangler | 1 feil, ikke navngitt i kilden | `spec-1-9-*.md:109` |
| 1.9 | M9: en trigger fra `vurdering` til `kurs` | 55 feil, blant dem AD-18-testene og testene i `test_vurderingslager.py` | `spec-1-9-*.md:110` |
| 1.9 | M10: `except IntegrityError` fjernet i `SqliteKurslager` | 4 feil: adaptertesten og tre eksisterende | `spec-1-9-*.md:111` |
| 1.9 | M11: kontrollen i versjon 2 mangler (`CHECK (1)`) | 3 feil: én per tabell | `spec-1-9-*.md:112` |
| 1.9 | M11b: kontrollen teller ikke `kursserie` | 1 feil, ikke navngitt i kilden | `spec-1-9-*.md:113` |
| 1.9 | uten `AND symbol IS NOT OLD.symbol` (ticker-oppdatering) | ikke prøvd før; 1 feil etter `test_ticker_kan_endres_uten_kollisjon` | `spec-1-9-*.md:123` (VG1/BH6) |
| 1.9 | `NOT IN` i kontrollen i versjon 2 | overlevde først, fanget etter `test_null_i_kursserie_stopper_migrasjonen` (1 feil) | `spec-1-9-*.md:133` (BH7) |
| AD-8 (982b216) | proxy-sperren tatt bort | proxy-testen (`test_proxy_paa_loopback_slipper_ikke_forbi`), ingen andre | `982b216`, commit-meldingen |
| AD-8 (982b216) | DNS-sperren (`socket.getaddrinfo`) tatt bort | DNS-testen (`test_dns_oppslag_blokkeres`), ingen andre | `982b216`, commit-meldingen |
| 2.0 | lag 1 fjernet | HTTP-testen og tilkoblingstesten på `hent_ett_symbol` (navn ikke i kilden) | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:77`, Design Notes `:147` |
| 2.0 | lag 1 bare for `HTTPError` | tilkoblingstesten (navn ikke i kilden) | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:78`, Design Notes `:148` |
| 2.0 | `HTTPError` beholder `response` | testene for kontrollpunktet, ikke navngitt i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:79,90`; triage ECH5 |
| 2.0 | `from None` fjernet for `RequestException` | tilkoblingstesten (triage VG3), navn ikke i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:80,90`; triage VG3 |
| 2.0 | lag 2 fjernet | testen gjennom `hent_universet`, både utskrift og `feil` (navn ikke i kilden) | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:81`, Design Notes `:149` |
| 2.0 | lag 2 uten URL-kodet form | testene for kontrollpunktet, ikke navngitt i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:82,90` |
| 2.0 | sjekken før første kall fjernet | testen «dagens fil finnes» (henteren kalles), navn ikke i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:83`, Design Notes `:150` |
| 2.0 | `"x"` byttet med `"w"` | testen «fil dukker opp under kjøringen», navn ikke i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:84`, Design Notes `:151` |
| 2.0 | kode 1 byttet med `return None` | testene for kontrollpunktet, ikke navngitt i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:85,90` |
| 2.0 | `mkdir` i `kjoer` fjernet | testene for kontrollpunktet, ikke navngitt i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:86,90` |
| 2.0 | kontrollen av formen fjernet | testen med feil form (navn ikke i kilden) | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:87`, Design Notes `:152` |
| 2.0 | bare `date` kontrolleres | testene for kontrollpunktet, ikke navngitt i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:88,90` |
| 2.0 | tomt svar sjekkes før formen | testene for kontrollpunktet, ikke navngitt i kilden | `spec-2-0-hentingen-lekker-ikke-noekkelen.md:89,90` |
| 2.0 | `adjusted_close` fjernet fra `FELT` | overlevde, funnet i kodegjennomgangen av Epic 1 (B-VG1). Koden (`FELT`, `_riktig_form`) ble fjernet i 1.8 (`ba7e019`, G1); ingen egen mutant for den | `kodegjennomgang-epic-1.md:118`; `spec-1-8-hentingen-godtar-bare-det-leseren-kan-lese.md:21` |
| 2.0 | tekstkontrollen av `date` fjernet | overlevde, funnet i kodegjennomgangen av Epic 1 (B-VG1). Koden ble fjernet i 1.8 (`ba7e019`, G1); ingen egen mutant for den | `kodegjennomgang-epic-1.md:118`; `spec-1-8-hentingen-godtar-bare-det-leseren-kan-lese.md:21` |
| 2.0 | en `main` som skriver til en annen katalog | overlevde, funnet i kodegjennomgangen av Epic 1 (B-VG2). Test lagt til i 2.1 (G12): `test_main_skriver_fila_for_norsk_dato_uten_noekkel` | `kodegjennomgang-epic-1.md:119`; `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:91` |
| 2.0 | én av formene (`quote`/`quote_plus`) fjernet fra `_uten_noekkel` | overlevde, funnet i kodegjennomgangen av Epic 1 (B-VG-a). Test lagt til i 1.8 (G3): nøkkel med mellomrom, 1 feil hver | `kodegjennomgang-epic-1.md:120`; `spec-1-8-hentingen-godtar-bare-det-leseren-kan-lese.md:71,101` |
| 2.1 | M1: `hentet` leses fra klokka etter hentingen | 7 feilet; docstringen i `TestBoersdagIOsloTidsstempelIUtc` (`test_filnavn_og_hentet_fra_samme_oeyeblikk`) | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:88,114`; `tests/test_fetch_prices.py:545` |
| 2.1 | M2: `dag = oeyeblikk.date()` (UTC-dagen) | 6 feilet; docstringen i `TestBoersdagIOsloTidsstempelIUtc` | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:89,115`; `tests/test_fetch_prices.py:546` |
| 2.1 | M3: `[:16]` tilbake i `_minutt` | 3 feilet, ikke navngitt i kilden | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:90,116` |
| 2.1 | M4: `_minutt` godtar tidsstempel uten sone | 1 feilet, ikke navngitt i kilden | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:90,117` |
| 2.1 | M5: `date.today()` tilbake i `main` | 2 feilet: G12 (`test_main_skriver_fila_for_norsk_dato_uten_noekkel`) og strengvakten | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:91,118`; `tests/test_fetch_prices.py:616` |
| 2.1 | M6: `dag = oeyeblikk.astimezone().date()` (maskinens sone) | 2 feilet lokalt: strengvakten (`test_ingen_kode_i_src_leser_maskinens_sone`) og øyeblikket uten sone; TZ-testene i CI | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:92,119`; `tests/test_tidssone.py:44` |
| 2.1 | M7: `hentet` i Oslo-tid (`+02:00`) | 7 feilet; fanget av K1 (`TestBoersdagIOsloTidsstempelIUtc`) | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:92,120`; `tests/test_fetch_prices.py:546` |
| 2.1 | `hentet = oeyeblikk.isoformat()` (BH1) | overlevde først (890 passed); etter retting 1 failed: ny rad i matrisen med øyeblikket i Europe/Oslo | `spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md:124`, triage BH1 `:131` |
| 2.1b | M1: `kjoer` skriver fila i `DATA_KATALOG` (`main` gir `DATA_KATALOG`) | 1 feilet (G12-testen) | `spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md:100,132` |
| 2.1b | M2: uten `mkdir` | 14 feilet, blant dem `test_sti_uten_mappe_gir_mappe_og_base_paa_siste_versjon` | `spec-2-1b-….md:101,133`; `tests/test_lagring_sqlite.py:274` |
| 2.1b | M3: uten `migrer` | 52 feilet, blant dem `test_sti_uten_mappe_gir_mappe_og_base_paa_siste_versjon` | `spec-2-1b-….md:101,134`; `tests/test_lagring_sqlite.py:274` |
| 2.1b | M4: `fetch_prices` kaller `sqlite3.connect` selv | 1 feilet (vakten, `test_bare_aapne_base_kobler_til_basen`) | `spec-2-1b-….md:101,135`; `tests/test_konsumentene.py:184` |
| 2.1b | M5: `hentet` fra klokka i stedet for øyeblikket | 6 feilet, blant dem `test_foerste_henting_lager_begge_mappene_og_skriver_15_serier` | `spec-2-1b-….md:102,136`; `tests/test_fetch_prices.py:703` |
| 2.1b | M6: symbolet som feilet, skrives likevel | 2 feilet, blant dem `test_symbol_som_feilet_faar_ingen_rad_i_ny_base` | `spec-2-1b-….md:102,137`; `tests/test_fetch_prices.py:725` |
| 2.1b | M7: basen skrives før fila | 1 feilet (`test_basen_kan_ikke_aapnes_fila_staar_og_kode_1`) | `spec-2-1b-….md:103,138`; `tests/test_fetch_prices.py:773` |
| 2.1b | M8: innlesingen leser nøkkelen | 2 feilet, blant dem `test_innlesing_gir_15_serier_uten_vurdering_noekkel_eller_kall` | `spec-2-1b-….md:104,139`; `tests/test_fetch_prices.py:938` |
| 2.1b | M9: sammenligningen fjernes | 1 feilet (`test_eldre_oeyeblikksbilde_hopper_over_symbolet_og_gir_kode_1`) | `spec-2-1b-….md:105,140`; `tests/test_fetch_prices.py:994` |
| 2.1b | M10: symbolsjekken fjernes fra `kontroller_skriving` | 9 feilet, blant dem `test_symbol_utenfor_universet_avvises` | `spec-2-1b-….md:106,141`; `tests/test_kurslager.py:359` |
| 2.1b | M11: `BEGIN IMMEDIATE` blir `BEGIN` | 1 feilet (overlapptesten, `TestToMigratorerOverlapper`) | `spec-2-1b-….md:107,142`; `tests/test_migrering.py:505` |
| 2.1b | M12: `kjoer` skriver bare symboler som ikke finnes i basen | 3 feilet, blant dem `test_fire_dagers_opphold_fylles_med_15_kall` | `spec-2-1b-….md:108,143`; `tests/test_fetch_prices.py:868` |
| 2.1b | M13: `nyeste_leser` leser `DATA_KATALOG` | 4 feilet, blant dem `test_standardstien_er_raa_katalog_slik_den_er_ved_kallet` | `spec-2-1b-….md:109,144`; `tests/test_lagring_fil.py:153` |
| 2.1b | andre `except BASEFEIL` fjernet (VG1) | feiler nå etter to nye tester (låst base midt i løkka, base nyere enn koden); hvilken som fanget, står ikke | `spec-2-1b-….md:156`, triage VG1; `tests/test_fetch_prices.py:796,817` |
| 2.1b | `BASEFEIL` innsnevret (VG1) | feiler nå etter de samme to nye testene; hvilken som fanget, står ikke | `spec-2-1b-….md:156`, triage VG1 |
| 2.1c | 1. Målingen i prosent | 3 feilet, ikke navngitt i kilden | `spec-2-1c-vurderingen-lagrer-maalingene-bak-de-tre-sjekkene.md:108,143` |
| 2.1c | 2. Målingen avrundet | 1 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 3. CHECK på `trend_avvik` fjernet | 2 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 4. CHECK på `volumforhold` godtar NULL uansett interesse | 2 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 5. Hjelpetabellen fjernet | 2 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 6. `>` → `>=` i interesse | 2 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 7. Porten godtar `None` med interesse 1 | 2 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 8. Porten godtar negativt standardavvik | 1 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 9. En kolonne mangler i `VURDERINGSKOLONNER` | 17 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 10. Fast to desimaler i stedet for `desimaler_mot_grense` | 1 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 11. Medianvolum 0 gir `0.0` | 2 feilet, ikke navngitt i kilden | `spec-2-1c-….md:108,143` |
| 2.1c | 12. CHECK `standardavvik >= 0` fjernet | 1 feilet, ikke navngitt i kilden | `spec-2-1c-….md:48,108,143` |
| 2.1c | 13. CHECK `volumforhold >= 0` fjernet | 1 feilet, ikke navngitt i kilden | `spec-2-1c-….md:48,108,143` |
| 2.5 | M1: `standardavvik` og `dagens_endring` byttet om | 2 feilet, blant dem `test_en_kjoering_skriver_kurser_og_vurderinger_for_alle_femten` | `spec-2-5-vurderingen-skrives-i-samme-kjoering.md:101,136`; `tests/test_fetch_prices.py:1138` |
| 2.5 | M2: Vurderingen regnes før kursene er skrevet | 12 feilet, blant dem `test_vurderingen_er_regnet_av_serien_kjoeringen_selv_lagret` | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1165` |
| 2.5 | M3: Et feilet symbol gir ingen rad | 4 feilet, blant dem `test_symbol_som_feilet_i_hentingen_faar_en_rad_med_grunn` | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1181` |
| 2.5 | M4: Datokontrollen i `vurder` fjernet | 2 feilet, blant dem `test_nyeste_kurs_ikke_fra_dagen_gir_en_rad_med_grunn` | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1219` |
| 2.5 | M5: `ValueError` fanges ikke i `vurder` | 4 feilet, blant dem `test_signal_som_ikke_kan_regnes_gir_en_rad_med_grunn` | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1234` |
| 2.5 | M6: `WHERE`-leddet i `_UPSERT` fjernet | 2 feilet, blant dem `test_grunn_skriver_ikke_over_vurderingen_fra_tidligere_i_dag` | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1266` |
| 2.5 | M7: Datoen leses på nytt for hvert symbol | 1 feilet (`test_midnatt_midt_i_universet_stopper_og_sier_fra`) | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1300` |
| 2.5 | M8a: sjekken før vurderingene fjernet | 2 feilet, blant dem `test_midnatt_foer_vurderingene_stopper_ogsaa_fredag` | `spec-2-5-….md:101`, triage BH8; `tests/test_fetch_prices.py:1326` |
| 2.5 | M8b: `ValueError` fra `skriv` fanges ikke | 1 feilet (`test_midnatt_midt_i_universet_stopper_og_sier_fra`) | `spec-2-5-….md:101`, triage BH8; `tests/test_fetch_prices.py:1301` |
| 2.5 | M9: `les_inn` skriver vurderinger | 2 feilet, blant dem `test_innlesing_skriver_aldri_vurdering` | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1369` |
| 2.5 | M10: `slutt` i utskriften | 1 feilet (`test_utskriften_har_antall_dag_og_grunner_men_ingen_kurser`) | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1397` |
| 2.5 | M11: Vurderingene skrives når basen har feilet | 1 feilet (`test_basen_feiler_ingen_vurdering_og_kode_1`) | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1435` |
| 2.5 | M12: Raden for en stengt dag skrives over | 1 feilet (`test_stengt_dag_lar_raden_fra_foer_staa`) | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1527` |
| 2.5 | M13: Datoen regnes etter kallene | 1 feilet (`test_utenfor_kalenderen_stopper_foer_foerste_kall`) | `spec-2-5-….md:101,136`; `tests/test_fetch_prices.py:1548` |
| 2.5 | M14: `sqlite3`-feilen i vurderingene slipper ut | 1 feilet (`test_basen_feiler_midt_i_vurderingene_kode_1_og_melding`); lagt til etter gjennomgangen | `spec-2-5-….md:101,113,136`; `tests/test_fetch_prices.py:1458` |
| 2.5 | M15: Feil i basen midt i vurderingene gir kode 0 | 1 feilet (`test_basen_feiler_midt_i_vurderingene_kode_1_og_melding`); lagt til etter gjennomgangen | `spec-2-5-….md:101,113,136`; `tests/test_fetch_prices.py:1459` |
| 2.5 | M16: Basen som ikke åpnes for vurderingene, gir kode 0 | 1 feilet, ikke navngitt i kilden; lagt til etter gjennomgangen | `spec-2-5-….md:101,113,136` |
| 8.0 | mutant 1–12, ikke navngitt i kilden (planen ble vist i chatten 30.09, og dagsfila sier ikke hva de var) | 12, alle fanget; mutant 2 først ikke lagt inn (literalt hardt mellomrom), fanget etter `7e7aa54` | `spec-8-0-de-rene-feilene-i-de-to-skjermbildene.md:88`; `33317df` |
| 8.0 | 13: nyeste dato i stedet for eldste over tabellen | fanget av datotestene (to rekkefølger, én eldre rad), ikke navngitt i kilden | `spec-8-0-….md:35,88` |
| 8.0 | 14: tilbakelenken uten understrek | fanget, ikke navngitt i kilden | `spec-8-0-….md:88` |
| 8.0 | 15: endringen farges opp/ned når teksten viser «0,00 %» | `test_endring_som_vises_som_null_har_ingen_farge` | `spec-8-0-….md:104` (triage 6), `:117` |
| 8.0 | 16: tilbakeført aksen i grafen (`"%.0f"`) | aksen i `test_tallene_i_detaljen_er_norske` | `spec-8-0-….md:100` (triage 2), `:117` |
| 8.0 | 17: tilbakeført f-streng i `_interesseforklaring` | `test_interesse_gjennom_beregn_signal` (byttet ut i 2.1c, beslutning 1) | `spec-8-0-….md:99` (triage 1), `:117`; `spec-2-1c-….md:44` |
| 9.0 | `abs` fjernet i `_sorteringsnokkel` | bare `test_absolutt_endring_avgjoer_ved_lik_styrke` | `spec-9-0-fem-tester-sjekker-det-de-lover.md:77` |
| 9.0 | `<=` byttet med `<` i `trend` | bare `test_noeyaktig_paa_grensen_gir_null` | `spec-9-0-….md:78` |
| 9.0 | `naa` i `kjoer` uten tidssone | bare `test_formatet_kan_leses_av_visningen` | `spec-9-0-….md:79` |
| 9.0 | Sluttkursen fjernet fra `aksje.html` | K3-testen (`test_kort_serie_viser_kurs_men_sier_at_signalet_mangler`) og `test_rutene_gjoer_ingen_nettverkskall` | `spec-9-0-….md:43,80` |
| 9.0 | `hent_leser` kaller `requests.get` | `test_rutene_gjoer_ingen_nettverkskall` og de to testene i `TestHentLeser` | `spec-9-0-….md:81` |
| 9.0 | andresortering på navn i stedet for `abs` (BH1) | bare `test_absolutt_endring_avgjoer_ved_lik_styrke`; lagt til etter gjennomgangen | `spec-9-0-….md:82`, triage BH1 `:92` |
