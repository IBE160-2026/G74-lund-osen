---
title: "Kvalitetssikring"
status: aktiv
created: 2026-10-03
updated: 2026-10-26T18:54
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

*Oppdatert 2026-10-17:* tallene i §1 og §2, radene i §3 og §5 og linjene i §6 er talt og slått opp på nytt mot `3699a16`. §11–§13 er nye. Det som står uten en datert linje, gjelder fortsatt `3803b4d`. `tests/test_kvalitetssikring.py` passer på radene i §3 og §5 og testnavnene (§8).

## 1. Kort fortalt

- 1074 tester i 22 testfiler. Lokalt på Windows består 1058, og 16 hoppes over.
  I CI på Linux består alle 1074 (kjøring 37072797767 på `74fc69b`, den siste
  på main da dette ble skrevet, med samme tester som `3803b4d`; `D/2026-10-03.md`).
  *Oppdatert 2026-10-25, og det er tallene som gjelder nå:* 3656 tester i 49 testfiler, telt med `uv run pytest --collect-only -q` på `d183856`, med 40 moduler i `src/` og sju migrasjoner i `src/migrasjoner/`. I CI på Linux består 3649, og 7 hoppes over (kjøring 40242295656 på `d183856`). Lokalt på Windows besto 3636, og 20 ble hoppet over, i den siste hele kjøringen 25.10 (21:55:10–22:02:40, fil for fil, på `9b28e1e`; `git diff 9b28e1e d183856 -- src tests` er tom). Tabellen fra 25.10 står over den fra 17.10 i §2.
  *Oppdatert 2026-10-17:* 2383 tester i 38 testfiler, telt med `uv run pytest --collect-only -q` på `3699a16`. Lokalt på Windows består 2366, og 17 hoppes over (målt på `59976ee` etter gjennomgangene av PR #60, slik beskrivelsen av PR #60 sier; `git diff 59976ee 3699a16 -- src tests` er tom). I CI på Linux består alle 2383 (kjøring 39066471455 på `3699a16`). Tabellen fra 17.10 står over den fra 03.10 i §2.
  *Lagt til 2026-10-17:* story 9.1 legger til `tests/test_kvalitetssikring.py` med 10 tester, så etter flettingen har main 2393 tester i 39 testfiler. Tabellen i §2 er talt før den kom til.
  *Oppdatert 2026-10-05:* 1148 tester i 23 testfiler, telt med `uv run pytest --collect-only -q` på `3fac7cc`. Lokalt på Windows består 1132, og 16 hoppes over. I CI på Linux består alle 1148 (kjøring 37348017033 på `3fac7cc`). Siden 03.10 har story 2.2 (`1570ae9`, PR #19) og 2.2b (`ff58ecf`, PR #20) kommet til, med den nye testfila `test_oversiktsleser.py`. Tabellen under er fra 03.10.
- Testene kan ikke nå nettet. En sperre i `tests/conftest.py` stopper det
  (AD-8), men den dekker ikke hele testkjøringen ennå (§6).
- Hver story med kode er prøvd med mutanter: koden er ødelagt med vilje, og
  en test skal feile. Vedlegget har 197 linjer, én per mutant eller per gruppe
  som kilden bare teller. 18 tilfeller overlevde en stund, og hvert av dem fikk
  en test eller en forklaring (§3).
  *Oppdatert 2026-10-25:* vedlegget har nå 264 linjer: de 197 fra 03.10 og 67 i
  «Fra 2.2 til 10.3, én linje per spesifikasjon», talt på `d183856`.
- Fra story 1.4a fikk hver story med kode en gjennomgang med tre eller fire
  lenser før flettingen, og Epic 1 fikk en samlet gjennomgang etterpå (§5).
- Koden er også kontrollert mot ekte data, og ikke bare mot testdata (§4).
- §6 sier hva som ikke er testet.

## 2. Testene

### Antall

Talt med `uv run pytest --collect-only -q` 25.10.2026, på `d183856`, med CI-kjøringen 40242295656 for samme commit (3649 bestått og 7 hoppet over). Dette er tallene som gjelder nå:

| Fil | Tester |
|---|---:|
| `test_ki_modell.py` | 481 |
| `test_fetch_prices.py` | 332 |
| `test_app.py` | 306 |
| `test_ki_tjenestene.py` | 239 |
| `test_vurderingslager.py` | 170 |
| `test_snapshotleser.py` | 133 |
| `test_docker.py` | 131 |
| `test_ki_visning.py` | 127 |
| `test_kurslager.py` | 113 |
| `test_kilogg.py` | 106 |
| `test_boersometer.py` | 91 |
| `test_markedsoversikt.py` | 82 |
| `test_demo.py` | 74 |
| `test_dobbeltklikk.py` | 67 |
| `test_ki_grunnlag.py` | 66 |
| `test_min_liste.py` | 64 |
| `test_aksje.py` | 59 |
| `test_utseende.py` | 57 |
| `test_ki_tekst.py` | 54 |
| `test_signalberegning.py` | 52 |
| `test_hjelpetekster.py` | 51 |
| `test_boersdag.py` | 49 |
| `test_kilogg_sqlite.py` | 49 |
| `test_migrering.py` | 49 |
| `test_hovedindeks.py` | 48 |
| `test_historikken.py` | 46 |
| `test_perioder.py` | 43 |
| `test_konsumentene.py` | 40 |
| `test_ki_lokal.py` | 39 |
| `test_aksjedetalj.py` | 38 |
| `test_indeks.py` | 38 |
| `test_ryddighet.py` | 35 |
| `test_ingen_nettverk.py` | 32 |
| `test_graf.py` | 31 |
| `test_meldinger.py` | 31 |
| `test_tallformat.py` | 31 |
| `test_tilstand.py` | 29 |
| `test_demoproeven.py` | 27 |
| `test_lagring_sqlite.py` | 26 |
| `test_investorsiden.py` | 25 |
| `test_demo_ki.py` | 21 |
| `test_kursdata.py` | 19 |
| `test_oversiktsleser.py` | 16 |
| `test_lagring_fil.py` | 13 |
| `test_kvalitetssikring.py` | 11 |
| `test_ruff.py` | 6 |
| `test_tidssone.py` | 5 |
| `test_suksesskriterier.py` | 3 |
| `test_readme.py` | 1 |
| **Sum** | **3656** |

Tabellen fra 17.10 står under, som den var.

Talt med `uv run pytest --collect-only -q` 17.10.2026, på `3699a16`, med CI-kjøringen 39066471455 for samme commit (2383 bestått):

| Fil | Tester |
|---|---:|
| `test_fetch_prices.py` | 304 |
| `test_ki_modell.py` | 211 |
| `test_app.py` | 175 |
| `test_vurderingslager.py` | 170 |
| `test_snapshotleser.py` | 133 |
| `test_kurslager.py` | 113 |
| `test_kilogg.py` | 106 |
| `test_docker.py` | 81 |
| `test_markedsoversikt.py` | 78 |
| `test_ki_visning.py` | 67 |
| `test_aksje.py` | 59 |
| `test_signalberegning.py` | 52 |
| `test_ki_tekst.py` | 51 |
| `test_hjelpetekster.py` | 51 |
| `test_migrering.py` | 49 |
| `test_kilogg_sqlite.py` | 49 |
| `test_boersdag.py` | 49 |
| `test_demo.py` | 48 |
| `test_utseende.py` | 47 |
| `test_ki_grunnlag.py` | 42 |
| `test_konsumentene.py` | 40 |
| `test_ki_lokal.py` | 39 |
| `test_indeks.py` | 38 |
| `test_aksjedetalj.py` | 38 |
| `test_hovedindeks.py` | 37 |
| `test_ingen_nettverk.py` | 32 |
| `test_tallformat.py` | 31 |
| `test_meldinger.py` | 30 |
| `test_tilstand.py` | 29 |
| `test_ryddighet.py` | 27 |
| `test_lagring_sqlite.py` | 26 |
| `test_graf.py` | 25 |
| `test_kursdata.py` | 19 |
| `test_oversiktsleser.py` | 15 |
| `test_lagring_fil.py` | 13 |
| `test_tidssone.py` | 5 |
| `test_suksesskriterier.py` | 3 |
| `test_readme.py` | 1 |
| **Sum** | **2383** |

Tabellen fra 03.10 står under, som den var.

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

*Oppdatert 2026-10-17:* 17 hoppes over på Windows: de 16 over, og 1 i `tests/test_ingen_nettverk.py` med grunnen «AF_UNIX finnes ikke i Python paa Windows» (story 4.0, `dc43569`). Talt med `uv run pytest -rs` på grenen for story 9.1 17.10, med samme tester som `3699a16` (spesifikasjonen `S/spec-9-1-kvalitetssikringen-oppdateres.md`).

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

*Oppdatert 2026-10-17:* story 4.0 (`dc43569`, PR #44) la sperren over hele testkjøringen, også innsamlingen, og `tests/test_ingen_nettverk.py` har nå 32 tester, blant dem `tests/test_ingen_nettverk.py::test_innsamlingen_er_sperret`, `tests/test_ingen_nettverk.py::test_connect_ex_blokkeres`, `tests/test_ingen_nettverk.py::test_udp_blokkeres` og `tests/test_ingen_nettverk.py::test_navneoppslag_blokkeres`. Linja over om `connect_ex` gjelder 03.10.

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

*Lagt til 2026-10-24:* «testene for dokumentene», som instruksjonene og endringsforslagene viser til, er `tests/test_readme.py`, `tests/test_kvalitetssikring.py`, `tests/test_ryddighet.py`, `tests/test_suksesskriterier.py`, `tests/test_hjelpetekster.py` og `tests/test_docker.py`.

*Avgjort 2026-10-25 kl. 20:16 (gruppens svar):* ingen sperre før push. Regelen står i hver instruksjon, og CI fanger feil.

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
| 2.2 Hentekommandoen som egen inngang | `1570ae9` (#19) | 1 (18 mutanter, M1–M18) | M7 og M11 overlevde først, og testene ble rettet i `e4f1be8`. M15 ble ikke fanget av testen den var laget for, men av to andre | `S/spec-2-2-hentekommandoen-som-egen-inngang.md`, tabellen over mutantene |
| 2.2b Sidene leser dagens vurdering | `ff58ecf` (#20) | 1 (15, M1–M15) | M15 overlevde først, og en ny test tar bort tabellen `vurdering` | `S/spec-2-2b-sidene-leser-dagens-vurdering.md`, Implementation Notes |
| 2.3 Børsdagskontrollen | `249853e` (#22) | 1 (32 kjøringer, 28 navn) | To flyttinger overlevde før testene fra gjennomgangen (VG1). M4 hang én gang og ble delt i M4a og M4b | `S/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md` |
| 2.3, kl. 21 Hentingen fra kl. 21:00 | `336204f` (#60) | 1 (3, T1–T3) | – | `S/spec-2-3-hentingen-fra-kl-21.md`, «Mutantene» |
| 2.3, kl. 22 Hentingen tilbake til kl. 22:00 | `54a4c51` (#79) | 1 (2, G1–G2) | – | `S/spec-2-3-hentingen-fra-kl-22.md`, «Mutantene» |
| 2.3b Nye forsøk | `c3d6660` (#28) | 1 (28) | M10 og M20 overlevde første kjøring, og to tester kom til i `bf41134` | `S/spec-2-3b-kallene-som-er-igjen-brukes-paa-nye-forsoek.md` |
| 2.7a All stilen i én CSS-fil | `dc521ff` (#76) | 1 (6, M1–M3 og N1–N3) | – Skjermbildene, den beregnede stilen og bildene i `docs/appen/` ble sammenlignet med main | `S/spec-2-7a-stilen-i-en-css-fil.md` |
| 2.8a Tabellen indeks og porten | `1d3a21d` (#56) | 1 (4, I1–I4) | – | `S/spec-2-8a-indeks-tabellen-og-porten.md`, «Mutantene» |
| 2.8b Kallet for hovedindeksen | `bcac2b5` (#57) | 1 (11) | – Første kjøring i en klone med CRLF ble gjort om, fordi sha256 ble sammenlignet mot andre linjeskift | `S/spec-2-8b-indekskallet-i-hentingen.md`, «Mutantene» og «Kode 3» |
| 2.9 Hovedindeksen på forsiden | `b44284f` (#59) | 1 (4, H1–H4) | – | `S/spec-2-9-hovedindeksen-paa-forsiden.md`, «Mutantene» |
| 3.1 Dockerfile med to innganger | `a2ecee8` (#23) | 1 (24 statiske og 9 i imaget) | I5 overlevde først (uv lastet ned 3.13), og `UV_PYTHON_DOWNLOADS=never` kom til. D21 overlevde først | `S/spec-3-1-dockerfile-med-to-innganger.md` |
| 3.2 To volumer | `088c885` (#24) | 1 (10 statiske og 8 i CI) | C3, S8, S9 og S10 overlevde først. Første forsøk med C7 bygget ikke | `S/spec-3-2-to-volumer-og-ingenting-uerstattelig-i-imaget.md` |
| 3.2b Port 8000 | `3f1c789` (#68) | 1 (5, P1–P5) | – | `S/spec-3-2b-port-8000.md` |
| 3.3 README | `5816bc2` (#25) | 1 (15 statiske og 1 i CI) | – | `S/spec-3-3-readme-slik-kjoerer-du-den.md` |
| 3.3b README for sensor | `6b9dc2f` (#53), `1a95495` (#54) | 1 (21 i PR #53) | – | `S/spec-3-3b-readme-for-sensor.md` |
| 3.3c Bilder i «Kom i gang», demoen først og fire rettelser | `fdaf403` (#66) | 1 (9, M1–M9) | – M1–M4 er fra instruksjonen, M5–M9 fra funnene med dom medium | `S/spec-3-3c-kom-i-gang-bilder-og-demoen-foerst.md` |
| 3.3d README-ryddingen | `1be3a57` (#67) | 1 (11, N1–N11) | N6 overlevde først på `8dc1e8f` og ble fanget etter at testen ble rettet i `ff2f540` | `S/spec-3-3d-readme-ryddingen.md` |
| 3.3e Bildet av oversikten, uv i «Tester» og variablene i .env | `c5464e7` (#70) | 1 (8, E1–E8) | E5 traff ikke linja første gang og ble kjørt på nytt. E8 er bildet fra før gruppens svar kl. 21:42 | `S/spec-3-3e-bildet-uv-og-variablene.md` |
| 3.3f Bildene av appen bak en knapp | `208d086` (#75) | 1 (4, M1–M3 og N1) | Første forsøk på å kjøre M1–M3 på nytt la ikke inn noen mutant (feil i skriptet) og ble gjort om | `S/spec-3-3f-bildene-av-appen-bak-en-knapp.md` |
| 3.3g README-en anbefaler demoen, og regelen for omfanget | `855ba75` (#77) | 1 (7, M1, M2a, M2b, M3 og N1–N3) | Med `-x` fanget en eldre test M1 og M2a først. Alle sju ble også kjørt mot de nye testene alene | `S/spec-3-3g-readme-demoen-anbefales.md` |
| 3.3h README-en bak piler, og hjelpen som levende dokument | `fdbdf20` (#80) | 1 (7, M1–M7) | – M1–M5 ble kjørt på `3042a7f` og `8e551a1`, M6 og M7 på `94db900` etter svaret kl. 20:20 | `S/spec-3-3h-readme-bak-piler-og-levende-hjelp.md` |
| 3.4 Demoversjonen | `0ed87be` (#26), `59c0baf` (#27), `4464a10` (#30), `4c01a7e` (#31), `41a9df7` (#32), `1ead55a` (#33), `dfe6884` (#34) | 1 (#26: 24, #27: 28, #30: 17, 16, 16, 10 og 6, #31: 4, #32–#34: 2 hver) | M20 i #26 og H12 og H13 i #30 overlevde først. T9 ble forkastet, og B6 ble ikke kjørt ferdig. Spesifikasjonen står i review | `S/spec-3-4-demoversjonen.md` |
| 3.4, alle 10 Kombinasjonene på siste demodag | `f21f927` (#58) | 1 (4, R1–R4) | – | `S/spec-3-4-alle-ti-kombinasjonene-paa-siste-demodag.md`, «Mutantene» |
| 3.4b KI-tekstene i demoen | `ab81d3f` (#69) | 1 (6, K1–K6) | K2 og K3 traff ikke første gang og ble laget på nytt. K6 ble fanget av fiksturen | `S/spec-3-4b-ki-tekstene-i-demoen.md` |
| 4.0 Nettsperren dekker hele testkjøringen | `dc43569` (#44) | 1 (10) | – Under N1 og N4 ble det gjort ekte oppslag og tilkoblingsforsøk (BH10) | `S/spec-4-0-nettsperren-dekker-hele-testkjoeringen.md` |
| 4.2 KILogg-porten | `a1d22f1` (#45) | 1 (11) | – | `S/spec-4-2-kilogg-porten-med-minneimplementasjon.md` |
| 4.3 SQLite-adapter for KILogg | `3a089c8` (#46) | 1 (7) | – | `S/spec-4-3-sqlite-adapter-for-kilogg.md` |
| 8.0b Hjelp bak «?» | `8d70762` (#29) | 1 (19) | M12 overlevde først, og testen ble rettet i `ccdd7ee` | `S/spec-8-0b-hjelp-bak-et-spoersmaalstegn.md` |
| 8.0c Tydelig merking | `82271fb` (#35), `16e18d8` (#36) | 1 (25) | – | `S/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md` |
| 8.0d Utseendet | `e862743` (#39), `179b415` (#40), `8c9f8b7` (#41), `f7c5e64` (#42) | 1 (47) | – E9–E11 ble kjørt senere, fordi maskinen hadde for lite minne. M2 og M8 trengte en testfil til | `S/spec-8-0d-utseendet-fra-designforslaget.md` |
| 8.0e Oversikten | `85fe8a4` (#37), `cfc373e` (#38) | 1 (16) | – | `S/spec-8-0e-oversikten-fra-designforslaget.md` |
| 8.3 Min liste | `e02240a` (#78) | 1 (6, M1–M3 og N1–N3) | M1 og M2 ble først fanget av hele fila, men ikke av testen sin alene, på `203be21`. Testene ble gjort sterkere i `9b3f7fa`, og alle seks ble kjørt på `b01871f` | `S/spec-8-3-min-liste.md` |
| 8.15 Sortering | `a13d273` (#43) | 1 (16, og 5 tester fra gjennomgangen prøvd som mutanter) | – | `S/spec-8-15-sortering-ved-klikk-i-kolonneraden.md` |
| 8.15b Selskap og den sorterte kolonnen | `b6449ac` (#73) | 1 (5, M1–M3 og N1–N2) | M1–M3 ble kjørt på `b5f2400` og på nytt etter rettingene | `S/spec-8-15b-selskap-og-den-sorterte-kolonnen.md` |
| 8.16 Startdagen og periodene i kursgrafen | `be05337` (#72) | 1 (8, P1–P4 og Q1–Q4) | P1–P4 ble kjørt på `697f459` og på nytt etter rettingene. Testen for bildet feilet på commiten for b til bildet ble tatt på nytt i c | `S/spec-8-16-periodene-i-kursgrafen.md` |
| 8.16b Dagen på hele aksjesiden | `4e43ba5` (#74) | 1 (6, K1–K3 og N1–N3) | K1–K3 ble kjørt på `f1e2fae` og på nytt etter rettingene | `S/spec-8-16b-dagen-paa-hele-siden.md` |
| 10.1 Grunnlaget som sendes | `6855861` (#47) | 1 (8) | GR2 overlevde først, og testen ble endret i `2ae86b4` | `S/spec-10-1-grunnlaget-som-sendes-bare-utledede-verdier.md` |
| 10.2a Modellen, prompten og kontrollen | `77ebf31` (#48) | 1 (12) | – Spesifikasjonen står in-progress | `S/spec-10-2a-modellen-prompten-og-kontrollen.md` |
| 10.2b Teksten i hentekommandoen | `b13e50f` (#49) | 1 (18) | FR2 overlevde først, og testen ble skrevet om i `48838a7` | `S/spec-10-2b-teksten-i-hentekommandoen.md` |
| 10.2c Prompten versjon 2 | `cafe067` (#55) | 1 (4) | – | `S/spec-10-2c-prompten-versjon-2.md` |
| 10.2d Kontrollen leser formene Gemma skriver | `3c2bd51` (#71) | 1 (12, D1–D12) | Testen i punkt a var først xfail av feil grunn, fordi `\b` i mønsteret var skrevet som backspace. Rettet i `aae2eef` før D1–D4 ble kjørt | `S/spec-10-2d-kontrollen-leser-formene-gemma-skriver.md` |
| 10.2e Prompten versjon 3 | `0c25686` (#95) | 2 (9 i seks runder) | – M1 og M2 kjørt på `1795981` 24.10, rettingen M1 og M2 på `f42c9d7` og `4a1d088`, tredje forsøk på `d5a3476` og `c6d0c85`, fjerde forsøk M1 og M2 på `9aa4219`, lesingen på `dfa39fc` og ordlyden på `7d61aaf` 25.10 | `S/spec-10-2e-prompten-versjon-3.md` og Utført-linjene i dagsfila for 25.10 |
| 10.2f Grunnen i prompten | `a9c3bdd` (#96) | 1 | – kjørt på `6ea0aed` og `3751c95` 25.10 | `S/spec-10-2f-grunnen-i-prompten.md` |
| 10.2g Regelen for retningen Ingen og promptens avtrykk i demotekstene | `2aa7745` (#97) | 1 (2, M1 og M2) | – kjørt på `2ded327` og `2e7883d`, og igjen på `a71a9e7` 25.10 | `S/spec-10-2g-ingen-retning.md` |
| 10.2h Ordstillingen etter «fordi» og rekkefølgen på sjekkene i prompten | `998dadd` (#98) | 1 | – kjørt på `34b42d2` og `5261ebf` 25.10 | `S/spec-10-2h-ordstilling.md` |
| 10.3 Visningen i aksjedetaljen | `e728c37` (#50), `4a22199` (#51) | 1 (15) | – | `S/spec-10-3-visningen-i-aksjedetaljen.md` |
| 10.5 Lenken til selskapets investorside | `bd19380` (#81) | 1 (6, M1–M3 og N1–N3) | – N1–N3 er mutantene fra Edge Case Hunter som overlevde, kjørt etter rettingen i `18a377c` | `S/spec-10-5-investorsiden.md` |
| 2.7b Signalet dag for dag | `d4c2441` (#82) | 1 (13, M1–M3 og N1–N10) | – N1–N10 er mutantene fra Edge Case Hunter som overlevde, og to til, kjørt etter rettingen i `4289d93` | `S/spec-2-7b-signalet-dag-for-dag.md` |
| 10.7 Egen nøkkel til Gemini, Anthropic og OpenAI | `6b39b80` (#83) | 1 (11, M1–M3 og N1–N8) | – N1–N8 dekker mutantene fra Edge Case Hunter som overlevde på `c3be49c`, og rettingene, kjørt etter rettingen i `761c970` | `S/spec-10-7-egen-noekkel-til-gemini-anthropic-og-openai.md` |
| 10.7b En nøkkel som mangler, gir ingen rader | `286caa8` (#84) | 1 (2, M1 og M2) | – kjørt på `6d0981c` og igjen etter rettingen i `d7feed6` | `S/spec-10-7b-noekkel-som-mangler-gir-ingen-rader.md` |
| 3.3i README-rettingen etter gjennomgangen av demoen | `a98146b` (#85) | 1 (3, M1–M3) | – kjørt på `b4a9ae2` og igjen etter rettingen i `1edd479` | `S/spec-3-3i-readme-rettingen-etter-demoen.md` |
| 3.3j Fem spørsmål i «Står du fast?» igjen | `6d67db0` (#86) | 1 (2, M1 og M2) | – kjørt på `3252f5b` og igjen etter rettingen i `1c757b4` | `S/spec-3-3j-fem-spoersmaal-i-staar-du-fast.md` |
| 3.4c Historikken i demoen som den ekte | `9359a70` (#88) | 1 (3, M1–M3) | – kjørt på `c137b66` og igjen etter rettingen i `c60be34` | `S/spec-3-4c-historikken-i-demoen.md` |
| 2.3c Første henting på dagtid når basen er tom | `2a84142` (#87) | 1 (3, M1–M3) | – kjørt på `9ad2c60` og igjen etter rettingen i `1431a6a` | `S/spec-2-3c-foerste-henting-paa-dagtid.md` |
| 8.6 Børsometeret | `7f1c1f0` (#89) | 1 (5, M1–M3, N1 og N2) | – M1–M3 kjørt før og etter rettingen i `2d72dc2`, og igjen på `a1f869f`; N1 og N2 for svarene kl. 09:24 på `a1f869f` | `S/spec-8-6-boersometeret.md` |
| 8.6b Børsometeret som tavla | `7f6d9e4` (#99) | 2 | – begge kjørt på `4af6efa` og `6f5815b`, og igjen på `38cbb3e` 26.10 etter punktene a–d og gjennomgangen | `S/spec-8-6b-som-tavla.md` |
| 8.0f Hjelpen ved «?» i ett fast felt | `238ef18` (#102) | 2 | – begge kjørt på `2889c93`, og igjen på `8621103` 26.10 etter gjennomgangen | `S/spec-8-0f-hjelpefeltet.md` |
| 3.4d Fotnoten for «ikke vurdert» | `544648f` (#90) | 1 (5, M1–M3, c M1 og c M2) | – M1–M3 kjørt på `8dcde6d` 22.10, c M1 og c M2 for svarene kl. 23:19 og 11:44 på `abdb110` | `S/spec-3-4d-fotnoten-ikke-vurdert.md` |
| 3.4e Fotnoten etter startdagen i demoen, og for inneværende børsdag | `e772cc6` (#91) | 1 (3, M1–M3) | – M1 og M2 kjørt på `622e25f`, M3 for svaret kl. 19:10 på `2fd2635` | `S/spec-3-4e-fotnoten-etter-startdag.md` |
| 3.5a Start med dobbeltklikk med uv, uten Docker | `afbc0af` (#92) | 2 (4, M1–M3 og vernet) | – M1–M3 kjørt på `1d46532` og igjen på `6287033` 23.10, vernet «bare fra main» én gang med `-x` på `2a3dd7e` 24.10 | `S/spec-3-5a-dobbeltklikk-med-uv.md` |
| 3.5d Funnene fra forprøven av den ekte versjonen 24.10 | `5e01a4f` (#94) | 1 (1, sjekken av kommandolinja) | – kjørt én gang med `-x` på `50ab5a6` 24.10, før sjekken ble snevret inn etter gjennomgangen | `S/spec-3-5d-funn-fra-forproeven.md` |
| 3.5f Hovedveien i «Kom i gang» | `8cd20b3` (#101) | 1 (1, Docker-delen tatt ut av «Kom i gang») | – kjørt med `-x` på `b5e4faa` og igjen på `a052c74` 26.10 | `S/spec-3-5f-hovedveien.md` |
| 3.5e Den andre versjonen stoppes rett før webserveren | `dbfa0b9` (#100) | 1 (1, stoppen tilbake før uv) | – kjørt med `-x` på `df6b0a0` og igjen på `fd19b7f` 26.10 | `S/spec-3-5e-stopp-foer-webserveren.md` |
| 8.2a Seks funn fra prøven av demoen 24.10 | `e4d1ba4` (#93) | 1 (5, M1–M5) | – kjørt på `7ca19d9` 24.10 | `S/spec-8-2a-funn-fra-proeven-av-demoen.md` |
| 9.1 Kvalitetssikringen, oppdatering 17.10 | PR-en for 9.1; flettecommiten står under story 9.1 i `epics.md` | 1 (4, Q1–Q4) | Q3 og Q4 overlevde på grencommiten `af04741` og ble fanget etter rettingen i `70a22ef` | `S/spec-9-1-kvalitetssikringen-oppdateres.md` |
| 9.7 Linter og formatterer i CI | `faaa36c` (#62) | 1 (5, A1–A5) | – | `S/spec-9-7-linter-og-formatterer-i-ci.md` |
| 2.9b Søylene under hovedindeksen | `73098ed` (#63) | 1 (6, S1–S6) | – | `S/spec-2-9b-soeylene-under-hovedindeksen.md` |
| 2.9c Hovedindeksen i kursgrafen | `24849dd` (#64) | 1 (6, C1–C6) | – | `S/spec-2-9c-hovedindeksen-i-kursgrafen.md` |
| 9.8 Kopien `.agents/skills/` tas bort | `b5395e9` (#65) | 1 (8, S1–S8) | – S5 ble først ikke brukt, fordi erstatningen ikke traff, og ble fanget da den ble kjørt på nytt | `S/spec-9-8-agents-kopien-bort.md` |

**Ingen story mangler.** Lista er satt sammen fra storyene med status `done`
eller `review` i `sprint-status.yaml` (21 storyer) og squash-commitene med
`(#NN)` i git-loggen. 9.3 og 9.4 har ingen rad: de er dokumentasjon og et
eksperiment uten kode i `src/`, og ingen mutanter er kjørt.

*Rettet 2026-10-17:* setningen gjaldt 03.10. Lista sluttet ved 2.5, 8.0, 9.0 og nettsperren. 27 rader kom til 17.10, én for hver spesifikasjon fra 2.2 til 10.3, også 3.4 (review) og 10.2a (in-progress). Tallene er hentet fra spesifikasjonene, og vedlegget har én linje per spesifikasjon for dem. `tests/test_kvalitetssikring.py` krever en egen rad for hver spesifikasjon med status `done`, så en spesifikasjon som settes til done uten rad, gjør testen rød.

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

*Lagt til 2026-10-17, fra radene som kom til:*

- **2.2:** spesifikasjonen har 18 mutanter (M1–M18). Utført-linja kl. 18:05 i `D/2026-10-03.md` sier «**Mutantene:** 17». M18 kom til før flettingen og er nevnt kl. 19:30. Triagen har 15 rader med 10 rettet i spesifikasjonen, og Rettet-linja i dagsfila sier 14 rader med 9 rettet. Raden «Rådet 03.10» kom til kl. 19:30.
- **2.2b:** spesifikasjonen sier ulikt med seg selv: lista under Verification har 11 mutanter, og tabellen i Implementation Notes har 15.
- **2.3:** dagsfila teller funn («26 funn. 18 er rettet …»), og spesifikasjonen teller rader (20 rader, 15 rettet). Begge kan stemme.
- **2.8a:** lista over avviste i `D/2026-10-17.md` nevner BH6 to ganger og ikke de to ECH-radene spesifikasjonen avviser. BH10 står i to rader i spesifikasjonen.
- **2.8b:** `D/2026-10-17.md` kl. 11:37 sier «Defer: BH7». Spesifikasjonen har BH7 som patch, med en Rettet-linje om at ruten var defer (kode 3, beslutningen kl. 11:58).
- **3.2:** dagsfila sier at fire overlevde først (C3, S8, S9 og S10). Spesifikasjonen sier i tillegg at `sitecustomize` overlevde i C7, og den første tabellen sier «8 av 8 drept» med S8, mens avsnittet etter gjennomgangen sier at S8 overlevde først.
- **3.3b, PR #54:** mutantene U1 og U2 står bare i `D/2026-10-16.md`, ikke i spesifikasjonen.
- **3.4, PR #26 og #27:** dagsfila sier 15 og 12 rettet. Spesifikasjonen har 14 og 11 rader med patch, og én rad hver med en annen rute (status satt til in-review, og en Rettet-linje).
- **3.4, PR #33:** spesifikasjonen har to mutanter, og `D/2026-10-12.md` har tre.
- **8.0b:** `D/2026-10-12.md` har to mutanter til ved flettingen, som spesifikasjonen ikke nevner.
- **8.0c:** spesifikasjonen sier «Alle 19 ble fanget», men tabellen har 20 rader for PR 1 og 25 i alt. M24 kom til kl. 16:42. For PR #36 sier `D/2026-10-13.md` «11 er rettet», og spesifikasjonen har 10 rader med patch.
- **10.2b:** spesifikasjonen og dagsfila sier begge 16 funn fra BH og 5 fra VG i første runde, men BH5 og VG5 står ikke i tabellen.
- **10.2c:** dagsfila sier at to ting ble utsatt, og spesifikasjonen har tre rader med defer.
- **10.3, PR #51:** spesifikasjonen sier «BH, 15 funn», men BH8 står ikke i tabellen for PR 2.

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
| 2.2 | 15 | 10 | 3 | 2 |
| 2.2b | 18 | 9 | 8 | 1 |
| 2.3 | 20 | 15 | – | 5 |
| 2.3, kl. 21 | 13 | 8 | 5 | – |
| 2.3, kl. 22 | 19 | 12 | 6 | – |
| 2.3b | 21 | 16 | 4 | 1 |
| 2.7a | 19 | 10 | 9 | – |
| 2.8a | 19 | 8 | 8 | 2 |
| 2.8b, del 1 | 18 | 10 | 8 | – |
| 2.8b, kode 3 | 15 | 5 | 10 | – |
| 2.9 | 20 | 8 | 12 | – |
| 3.1 | 17 | 15 | 1 | 1 |
| 3.2 | 16 | 9 | 7 | – |
| 3.2b | 16 | 8 | 8 | – |
| 3.3 | 13 | 10 | 2 | 1 |
| 3.3b, PR #53 | 22 | 16 | 5 | 1 |
| 3.3b, PR #54 | 12 | 5 | 6 | 1 |
| 3.3c | 27 | 17 | 8 | 2 |
| 3.3d | 21 | 15 | 5 | 1 |
| 3.3e | 22 | 15 | 7 | 0 |
| 3.3f | 22 | 6 | 15 | 1 |
| 3.3g | 29 | 13 | 16 | – |
| 3.3h | 25 | 20 | 4 | – |
| 3.4, PR #26 | 21 | 14 | 5 | 1 |
| 3.4, PR #27 | 22 | 12 | 8 | 2 |
| 3.4, PR #30, første runde | 29 | 25 | 4 | – |
| 3.4, PR #30, kort form | 26 | 21 | 5 | – |
| 3.4, PR #30, helhetlig form | 24 | 19 | 5 | – |
| 3.4, PR #30, rekkefølgen | 11 | 10 | 1 | – |
| 3.4, alle 10 | 16 | 9 | 7 | – |
| 3.4b | 24 | 13 | 9 | 2 |
| 4.0 | 21 | 14 | 6 | 1 |
| 4.2 | 22 | 19 | 2 | 1 |
| 4.3 | 16 | 13 | 1 | 2 |
| 8.0b | 23 | 12 | 10 | 1 |
| 8.0c, PR #35 | 32 | 17 | 9 | 5 |
| 8.0c, PR #36 | 16 | 10 | 3 | 2 |
| 8.0d, PR 1 | 17 | 9 | 6 | 2 |
| 8.0d, PR 2 | 20 | 14 | 4 | 2 |
| 8.0d, PR 2b | 9 | 3 | 4 | 2 |
| 8.0d, PR 3 | 26 | 7 | 14 | 2 |
| 8.0d, svarene 15.10 | 14 | 5 | 7 | – |
| 8.0e, PR 1 | 13 | 7 | 6 | – |
| 8.0e, PR 2 | 11 | 4 | 7 | – |
| 8.3 | 33 | 20 | 13 | – |
| 8.15 | 19 | 11 | 7 | 1 |
| 8.15b | 26 | 11 | 15 | – |
| 8.16 | 29 | 15 | 13 | 1 |
| 8.16b | 20 | 5 | 14 | 1 |
| 10.1 | 15 | 13 | 2 | – |
| 10.2a | 25 | 20 | 4 | 1 |
| 10.2b, første runde | 24 | 20 | 2 | – |
| 10.2b, svar c | 19 | 13 | 6 | – |
| 10.2c | 17 | 8 | 4 | 3 |
| 10.2d | 23 | 17 | 6 | – |
| 10.2e, første gjennomgang 24.10 | 20 | 7 | 3 | 10 |
| 10.2e, rettingen 24.10 | 25 | 18 | 2 | 5 |
| 10.2e, natt til 25.10 | 25 | 15 | 6 | 4 |
| 10.2e, 25.10 kl. 11 | 30 | 13 | 4 | 13 |
| 10.2e, 25.10 kl. 13 | 11 | 6 | 2 | 3 |
| 10.2f, 25.10 kl. 19:30 | 17 | 10 | 5 | 2 |
| 10.2g, 25.10 kl. 20:37 | 15 | 9 | 3 | 3 |
| 10.2h, 25.10 kl. 21:54 | 15 | 10 | 0 | 5 |
| 10.3, PR #50 | 21 | 13 | 8 | – |
| 10.3, PR #51 | 13 | 9 | 2 | 2 |
| 10.5 | 25 | 16 | 4 | – |
| 2.7b | 38 | 30 | 3 | – |
| 10.7 | 26 | 22 | 2 | – |
| 10.7b | 13 | 8 | 3 | – |
| 3.3i | 20 | 15 | 1 | – |
| 3.3j | 13 | 7 | 1 | – |
| 3.4c | 11 | 6 | 1 | – |
| 2.3c | 18 | 13 | – | – |
| 8.6, to gjennomganger 23.10 | 36 | 24 | 12 | – |
| 3.4d, gjennomgangene 22.10 og 23.10 | 27 | 15 | 12 | – |
| 3.4e, to gjennomganger 23.10 | 36 | 22 | 13 | 1 |
| 3.5a, gjennomgangene 23.10 og 24.10 | 48 | 34 | 14 | – |
| 3.5d | 24 | 15 | 8 | 1 |
| 3.5f | 23 | 13 | 9 | 1 |
| 3.5e | 10 | 8 | – | 2 |
| 8.6b, gjennomgangene 26.10 | 37 | 21 | 13 | 3 |
| 8.0f, gjennomgangen 26.10 | 25 | 22 | 3 | – |
| 8.2a | 21 | 15 | 6 | – |
| 9.1, oppdatering 17.10 | 19 | 17 | 2 | – |
| 9.7 | 19 | 13 | 6 | – |
| 2.9b | 23 | 17 | 6 | – |
| 2.9c | 15 | 8 | 7 | – |
| 9.8 | 20 | 14 | 6 | – |

Noen rader slår sammen flere funn, så kolonnene summerer ikke alltid til
radtallet. 1.6 har i tillegg seks rader med «ingen endring», og BH2 ble avvist
for 1.6, men ført i `deferred-work.md` for 2.5. 1.9 har 18 funn i 15 rader:
13 funn ble rettet i 10 rettinger, og BH11 ble både rettet i spinen og utsatt
for `docs/innlevering.md`. 1.1–1.3 har ingen spesifikasjon, og en gjennomgang av dem
23.09 står i `S/kodegjennomgang-epic-1.md`. Tallene for 8.0 ble rettet etter
tabellen 03.10.

*Lagt til 2026-10-17:* radene fra 2.2 til 10.3 er talt rad for rad i spesifikasjonene. «Rettet» er rader med patch, også en Rettet-linje, en delvis patch og raden BH2 i 2.3b, som har ruten «Verification under». «Avvist» tar også med rader med «ikke endret», «false» og «ingen». Rader som går til gruppen, et spørsmål eller «info», står ikke i noen av de tre kolonnene, så summen kan bli mindre enn radtallet: 2.8a har 1 til gruppen, 3.4 PR #26 1 med status satt til in-review, 8.0c PR #35 1 spørsmål, 8.0c PR #36 1 info, 8.0d PR 3 3 til gruppen, 8.0d svarene 2 avgjort av gruppen, 10.2b første runde 2 til gruppen og 10.2c 2 til gruppen. Der spesifikasjonen og dagsfila sier ulikt, står det under «Åpne punkter i kildene» i §3.

*Lagt til 2026-10-17:* fra story 9.1 (17.10) får hver PR triagen fra spesifikasjonen som kommentar, med lenke til spesifikasjonen. PR #56–#60 fikk den i ettertid 17.10, satt sammen fra triagen i spesifikasjonene.

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

*Rettet 2026-10-03, etter svarene fra gruppa:* P9, P10, P12 og E8 er skrevet inn. Nå er 24 lukket, 4 delvis og 46 står.

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
  *Lagt til 2026-10-17:* det samme gjelder kallet for hovedindeksen,
  `hent_indeksen` (story 2.8, `bcac2b5`), som bruker `hent_ett_symbol`. Første
  ekte henting med indeksen er mandag 19.10.
- **Nettsperren dekker ikke hele testkjøringen.** Den er en autouse-fixture med
  funksjonsscope og gjelder bare inne i testfunksjonene. En fixture med
  `scope="module"` nådde nettet 23.09, og `gethostbyname`, `gethostbyname_ex`
  og `getfqdn` er ikke sperret. Story 4.0 skal rette det, og legge til tester
  for `connect_ex` og en fixture med module-scope (`epics.md`, story 4.0).
  Sperren stopper heller ikke UDP. Det er K11 i kontrollen 26.09, og rapporten
  legger det til story 4.0 (`docs/kontroll-2026-09-26.md`, linje 211 og 443).
  *Rettet 2026-10-17:* story 4.0 (`dc43569`, PR #44) la sperren over hele
  testkjøringen, også innsamlingen, navneoppslagene og UDP. Testene står i §2,
  blant dem `tests/test_ingen_nettverk.py::test_innsamlingen_er_sperret` og
  `tests/test_ingen_nettverk.py::test_udp_blokkeres`.
- **TZ-testene lokalt.** De 16 testene som hoppes over på Windows, kjøres bare
  i CI (§2).
  *Lagt til 2026-10-17:* nå hoppes 17 over, med testen for `AF_UNIX` fra story
  4.0 (§2).
- **Vurderingslageret mot to adaptere.** Det finnes bare `SqliteVurderingslager`,
  med vilje (§2).
- **Skriptene for morgensjekken.** `.github/scripts/morgensjekk.py` og
  `morgenrapport.py` har ingen tester.
- **Det appen viser fra basen.** Webserveren leser fortsatt øyeblikksbildene,
  ikke basen (README, «Kom i gang»). Vurderingene som lagres fra 02.10, vises
  ikke ennå (story 2.2 og 2.7).
  *Rettet 2026-10-17:* webserveren leser basen fra story 2.2 (`1570ae9`, PR #19),
  og sidene viser dagens vurdering fra 2.2b (`ff58ecf`, PR #20), med
  `tests/test_app.py::test_rutene_gjoer_ingen_nettverkskall`. Historikken, de
  lagrede vurderingene dag for dag, vises ennå ikke (story 2.7, backlog).
- **Det som ikke er bygget.** Docker finnes ikke (ingen `Dockerfile`).
  KI-laget er ikke bygget (Epic 10), og `src/` har ingen KI-kode.
  Børsdagskontrollen (2.3) og hovedindeksen (2.8) er ikke bygget.
  *Rettet 2026-10-17:* alt i punktet er bygget og flettet. Docker: story 3.1
  (`a2ecee8`, PR #23) og 3.2 (`088c885`, PR #24), og CI bygger og kjører imaget
  i jobben `docker` i `.github/workflows/tester.yml`. KI-laget: 4.2 (`a1d22f1`),
  4.3 (`3a089c8`), 10.1 (`6855861`), 10.2 (`77ebf31`, `b13e50f` og `cafe067`) og
  10.3 (`e728c37` og `4a22199`). Børsdagskontrollen: 2.3 (`249853e`, PR #22),
  med grensen kl. 21:00 fra `336204f`. Hovedindeksen: 2.8 (`1d3a21d` og
  `bcac2b5`) og visningen i 2.9 (`b44284f`). Søylene (2.9b), historikken (2.7),
  «Min liste» (8.3) og KI-tekstene i demoen (3.4b) står i backlog.
  *Lagt til 2026-10-20:* grensen er kl. 22:00 igjen fra 20.10 (gruppens svar 19.10 kl. 22:19 under story 2.3, `malinger.md` §37),
  i PR-en for `spec-2-3-hentingen-fra-kl-22.md`.
- **Brukere.** Ingen brukertest er gjort ennå (story 8.1). Sidene er bare
  prøvd med Flask sin testklient, ikke i en nettleser.
  *Lagt til 2026-10-17:* står fortsatt. 8.1 står i backlog, og ingen test i
  `tests/` starter en nettleser. Vi har gått gjennom «Kom i gang» selv 16.10 (§13).
- **To kontroller for hånd** står som gjenstående i `malinger.md` §6: de tre
  sjekkene i et regneark, og kursene mot Oslo Børs. Ingenting viser at de er
  gjort. Sluttverdien for OSEBX er kontrollert for hånd én gang (`malinger.md`
  §14).
  *Rettet 2026-10-06:* kontrollregningen av de tre sjekkene er gjort for EQNR
  05.10 (`malinger.md` §6). De fire målingene, de tre verdiene, styrken og
  retningen i regnearket er like det appen lagret 05.10. Kontrollen av kursene
  mot Oslo Børs gjenstår, utenom OSEBX 01.10 (§14).
  *Lagt til 2026-10-06:* kontrollregningen er også gjort for GJF 02.10, en dag
  der bevegelse slo ut (`malinger.md` §6). Også der er regnearket og det appen
  lagret, like. En dag med utslag på interesse gjenstår.
  *Lagt til 2026-10-13:* kontrollregningen er også gjort for TEL 08.10, en dag
  med utslag på interesse (`malinger.md` §6). De fire målingene, de tre
  verdiene, styrken og retningen i regnearket er like det appen lagret 08.10.
- **De 71 punktene fra kontrollen 26.09** er ikke kontrollert på nytt. Minst
  tre av dem er lukket (§5).
  *Rettet 2026-10-03:* de er kontrollert på nytt. Etter rettingene samme dag er
  14 av de 74 lukket, 6 delvis og 54 står (§5, og «Etterkontroll 03.10» i
  [`docs/kontroll-2026-09-26.md`](kontroll-2026-09-26.md#etterkontroll-0310)).
  *Rettet 2026-10-03, senere samme dag:* nå er 20 lukket, 4 delvis og 50 står.
  *Rettet 2026-10-03, etter svarene fra gruppa:* nå er 24 lukket, 4 delvis og 46 står.

*Lagt til 2026-10-17, nye hull:*

- **Ekte svar fra den lokale modellen.** Testene for `OllamaModell` bruker en
  falsk Ollama (`tests/test_ki_lokal.py`), og ingen test kaller modellen. Den
  er bare prøvd i prøvekjøringene mot en kopi av basen, ført i `malinger.md`
  §32 og §34.
- **At CI kjører uten hemmeligheter, har ingen test.** Arbeidsflyten har
  `permissions: contents: read` og ingen `secrets.`, sjekket for hånd 17.10 mot
  `.github/workflows/tester.yml`. Ingen test leser det.
- **README-prøven er ikke tatt.** Prøve 1, 2 og 3 i §9 står uten dato og
  resultat, og story 3.4 står i review til den er tatt (§9 og §13).
- **Hovedindeksen med ekte data.** Kallet, lagringen og visningen er prøvd
  med testserier. Første ekte henting med indeksen er mandag 19.10, og verdien
  for OSEBX er kontrollert for hånd én gang (`malinger.md` §14).
- **Grensen kl. 21:00 er prøvd for én aksje én dag** (`malinger.md` §31).
  Mandag 19.10 sammenlignes fire aksjer med kursfila etter kl. 22, med kallene
  som er igjen (beslutningen 17.10 kl. 22:00 under story 2.3 i `epics.md`).
  *Lagt til 2026-10-20:* målingen er tatt (`malinger.md` §37). DNO var ulik i
  `volume` etter kl. 22, så raden fra kl. 21 var ikke endelig, og grensen er
  kl. 22:00 igjen fra 20.10 (gruppens svar 19.10 kl. 22:19 under story 2.3).

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

*Lagt til 2026-10-17 (story 9.7):* ruff kjøres før en commit, `uv run ruff check --fix` og så `uv run ruff format`, med pyflakes, importene og bugbear (`pyproject.toml`). CI kjører `ruff check` og `ruff format --check` før testene, og `tests/test_ruff.py` gjør det samme, så pytest feiler lokalt også.

*Lagt til 2026-10-17:* `tests/test_kvalitetssikring.py` passer på to av punktene: hver spesifikasjon med status `done` har en rad i §3 og i §5, og hver test dette dokumentet og `vurderingsmatrise.md` nevner med fil og navn, finnes. Hver PR får triagen som kommentar (§5).

## 9. README-prøven

Kontrollpunktet i story 3.4 i [`epics.md`](../_bmad-output/planning-artifacts/epics.md):
README-oppskriften følges fra start til slutt på en maskin som ikke har hatt
repoet eller imaget før, uten nøkler. Prøven er planlagt 13.–16.10 (punkt 2 i
rekkefølgen i `epics.md`, fra endringsforslaget 08.10), og gjentas før
innleveringen. Avsnittet er laget i story 3.4, PR 2, og fylles ut av den som
prøver. Det som står over, gjelder fortsatt commit `3803b4d`.

Kommandoene står i den rekkefølgen «Kom i gang» i [`README.md`](../README.md)
har dem. Endres README-en før prøven, rettes lista her i samme commit.

*Lagt til 2026-10-10 (story 2.3b):* teksten under «Når du henter» i README-en er endret. Setningen om dager børsen er stengt nevner ikke lenger fila for dagen, og en ny setning sier at samme kommando kjørt igjen senere samme kveld prøver aksjene som mangler dagens kurs. Ingen kommando er ny eller endret, så tabellen under står. Prøven fører commiten den brukte.

*Lagt til 2026-10-12 (flettingen av 2.3b):* etter PR #30 står teksten ikke lenger i README-en, men under «Når kan jeg hente?» i `docs/hjelp.md`. Endringen fra 2.3b er ført der. Ingen kommando i «Kom i gang» er endret.

*Lagt til 2026-10-13 (story 8.0e, PR 2):* steg 2 i README-en slutter nå med setningen fra «Jeg har fått koden fra før» i `docs/hjelp.md`, og steg 4 med «Har mappa et annet navn, drar du den mappa der README og compose ligger.» Rad 2 og 4 i Prøve 1 er rettet etter det. Ingen kommando i «Kom i gang» er endret. Prøve 1 og 2 tas etter at 8.0d er flettet, så testeren ser det nye utseendet (beslutningen 13.10 kl. 23:40), og ikke 13.–16.10 som over. Prøven før innleveringen bruker ZIP-fila som faktisk leveres (beslutningen 13.10 kl. 23:22).

*Lagt til 2026-10-14 (gruppen kl. 22:19 og 22:25):* Rekkefølgen etter 8.0d er 8.15, så 2.8, 2.9 og 2.9b, 8.3, 8.10, 8.16 og 8.17, 2.7 og 8.8, 10.1–10.3, 8.10b, 10.6, og til slutt 2.11 og 2.12. README-prøven tas når mest mulig av dette er bygget, og senest én uke før innleveringen. Det erstatter setningen over om at Prøve 1 og 2 tas etter at 8.0d er flettet. Rekkefølgen står i `epics.md`.

*Lagt til 2026-10-18 (gruppens svar kl. 00:03):* Prøve 1 tas i uke 43 (19.–25.10), etter at de to README-PR-ene er flettet, og Prøve 2 samtidig hvis testeren har egen gratiskonto. Prøven tas på nytt senest én uke før innleveringen, med ZIP-fila som leveres. Det endrer setningen fra 14.10 over om at prøven tas når mest mulig er bygget. Beslutningen står under «Prioritering» og story 3.3 i `epics.md`.

*Rettet 2026-10-21 kl. 18:33:* Linja over om README-prøven i uke 43 (gruppens svar 18.10 kl. 00:03) gjelder ikke lenger. Prøven på en ren maskin er utsatt til v1 er ferdig bygget, etter avgjørelsen 2026-10-21 kl. 18:33 under «Prioritering» og story 3.3 i `epics.md`.

*Lagt til 2026-10-19 (story 3.3g, gruppens svar kl. 14:46 og 14:48):* «Kom i gang» anbefaler nå demoen for faglærer og sensor, og «(anbefalt)» står ikke lenger ved den ekte versjonen. Knappen for den lokale modellen under «Mer for den som vil» heter «Den lokale modellen for KI-teksten (valgfri)» og sier at den ikke trengs for demoen eller for å vurdere appen. Ingen kommando i «Kom i gang» er endret. README-prøven med ZIP-fila, senest én uke før innleveringen, er også funksjonsstoppen: det briefen ikke lover og som ikke er ferdig da, flettes ikke.

*Lagt til 2026-10-20 (story 3.3h, gjennomgangen ECH7):* i «Kom i gang» står demoen og den ekte versjonen nå bak hver sin pil etter linja «Velg vei», og testeren klikker på pila før steg 5 i hver av dem. Stegene og kommandoene er de samme, så ingen rad i tabellene endres.

*Avgjort 2026-10-21 kl. 18:33 (gruppens svar):* README-prøven på en ren maskin er utsatt til v1 er ferdig bygget, fordi flere deler skal inn (historikken 2.7b, som ble flettet i `d4c2441` kl. 17:58 samme dag, og egne nøkler 10.7), og prøven skal gjelde den appen som leveres. Gruppen har kjørt oppskriften på egen maskin, og den virker. Den siste daterte gjennomgangen på egen maskin som står i repoet, er 16.10 kl. 20:40–21:11, under story 3.3 i `epics.md` (avgjørelsen 16.10 kl. 21:16), i tabellen i §13 i `docs/kvalitetssikring.md` og i `docs/reflection-log.md` 16.10. Den fant fire ting, som ble rettet i `fdaf403`, PR #66, 18.10. Prøven på en ren maskin er fortsatt funksjonsstoppen, senest én uke før innleveringen (svaret 19.10 kl. 14:48), og 3.4 står i review til den er tatt.

### Prøve 1

- **Hvem som prøver:** åpent.
- **Dato og klokkeslett:**
- **Maskin og operativsystem:**
- **Docker Desktop, versjon** (`docker version`, linjen med «Docker Desktop»):
- **Logget inn i Docker Desktop:** ja / nei. Prøven gjøres uten innlogging, så vi vet at README-en virker uten Docker-konto.
- **Maskinen har aldri hatt repoet eller imaget:** ja / nei. Sjekket med
  `docker images` (ingen `ose-signal`) og at mappa `G74-lund-osen` ikke fantes.
- **Commit som ble prøvd** (`git log -1 --oneline`):
- **uv fra før** (`uv --version` før prøven, eller «ikke installert»), for hovedveien:

*Lagt til 2026-10-26 (story 3.5f, gruppens svar 25.10 kl. 11:32 under story 3.5 i `epics.md`):* dobbeltklikket er hovedveien i «Kom i gang», og prøven begynner med det, i tabellen «Hovedveien» under. Docker Desktop trengs ikke for radene D1–D6. Tabellen med Docker og uv, rad 1–23, er reserven og tas etterpå. Ingen rad i den er endret.

**Hovedveien: «Enklest: dobbeltklikk, uten Docker»**

| # | Steg i README-en | Det som skjedde | Tid (min) |
|---|---|---|---|
| D1 | Last ned med den direkte lenken, eller «Code» → «Download ZIP», og pakk ut med «Pakk ut alle» (Windows) eller dobbeltklikk (Mac). Kom det en mappe `G74-lund-osen-main`, og lå de fire filene i den innerste? | | |
| D2 | Finn de fire filene øverst i mappa. Viste Windows dem som «Start demoen» og «Start den ekte versjonen», uten filendelsen? | | |
| D3 | Dobbeltklikk «Start demoen». Kom advarselen fra Windows eller godkjenningen på Mac, og holdt teksten i README-en? Spurte vinduet om uv skulle installeres? | | |
| D4 | Åpnet nettleseren http://127.0.0.1:8000, og står «Eksempeltall» på siden? Hvor lang tid tok det fra dobbeltklikket? | | |
| D5 | En aksje i demoen åpnes fra oversikten. Så lukkes vinduet: svarer http://127.0.0.1:8000 etterpå? | | |
| D6 | Dobbeltklikk «Start den ekte versjonen» uten nøkkel. Åpnet registreringssiden hos EODHD seg, og spurte vinduet etter nøkkelen? Lukk vinduet uten å lime inn noe, og slett `.env` som vinduet laget, før reserven | | |

**Reserven: Docker Desktop, og uv i terminalen**

| # | Kommando eller steg i README-en | Det som skjedde | Tid (min) |
|---|---|---|---|
| 1 | Steg 1: installer og start Docker Desktop uten å logge inn, og vent til det står «Engine running». Ba installasjonen om administrator eller omstart? | | |
| 2 | Steg 2: «Code» → «Download ZIP» på GitHub, og pakk ut med «Pakk ut alle» (Windows) eller dobbeltklikk (Mac). Lå det en mappe med samme navn inni? Viste Windows filene som README og compose? Fikk prøveren koden som mappe eller ZIP-fil fra før, ble den pakket ut og prøven fortsatt fra steg 3? | | |
| 3 | Steg 3: åpne «Windows PowerShell», ikke «Windows PowerShell ISE» (Windows), eller Terminal (Mac) | | |
| 4 | Steg 4: `cd`, mellomrom, og den innerste mappa dratt inn i vinduet. Fikk en sti med mellomrom anførselstegn? Hadde mappa et annet navn, ble mappa der README og compose ligger, dratt inn? | | |
| 5 | Demoen, steg 5: `docker compose up --build demo`, kopiert med knappen i boksen, til linja med «Serving on» kommer. Hvor lang tid tok det, og kom det en linje med valg under? | | |
| 6 | Demoen, steg 6: åpne http://127.0.0.1:8000. Står «Eksempeltall» på siden? | | |
| 7 | En aksje i demoen åpnes fra oversikten | | |
| 8 | `docker compose run --rm demo-lag`, i et nytt vindu mens demoen kjører | | |
| 9 | Demoen, steg 7: `Ctrl+C` i vinduet med demoen, så `docker compose --profile demo down`. Stod det «Removed»? | | |
| 10 | Den ekte versjonen, steg 5: nøkkelen hos EODHD. Hoppes over i prøven, som gjøres uten nøkkel | | |
| 11 | Den ekte versjonen, steg 6: `cp .env.example .env`, så `notepad .env` (Windows) eller `open -e .env` (Mac), uten å fylle inn nøkkelen | | |
| 12 | Den ekte versjonen, steg 7: `docker compose up --build` og http://127.0.0.1:8000. Var oversikten tom, med kommandoen som henter? | | |
| 13 | Den ekte versjonen, steg 8: `docker compose run --rm hent`, uten nøkkel | | |
| 14 | Siden lastet på nytt | | |
| 15 | Den ekte versjonen, steg 9: `docker compose down`. Stod det «Removed»? | | |
| 16 | Byttet, fra den ekte versjonen til demoen og tilbake: `docker compose up --build`, så `docker compose down` og `docker compose up --build demo`, så `docker compose --profile demo down` og `docker compose up --build` igjen | | |
| 17 | uv: `uv sync` | | |
| 18 | `uv run python src/demo.py` | | |
| 19 | `uv run python src/app.py --demo` og http://127.0.0.1:8000 | | |
| 20 | `uv run python src/fetch_prices.py`, uten nøkkel | | |
| 21 | `uv run python src/app.py` | | |
| 22 | `docker ps -a` til slutt: står det containere igjen fra prøven? | | |
| 23 | Ble et spørsmål i «Står du fast?» eller i `docs/hjelp.md` brukt? Hvilket, og hjalp svaret? | | |

- **Prøvd på Mac:** ikke prøvd (svar 3 11.10). Står slik til noen har prøvd stegene på en Mac.
- **Den ekte versjonen med nøkkel:** prøves ikke her. Prøven gjøres uten nøkkel, så sjekken i steg 8 («utskriften sier hvilken børsdag vurderingene gjelder») og at oversikten fylles etter hentingen, er ikke prøvd etter README-en.
  *Lagt til 2026-10-13:* den ekte versjonen med nøkkel prøves i Prøve 2 under, med begge sjekkene.

*Rettet 2026-10-11 (story 3.4, PR 3):* tabellen følger «Kom i gang» slik den ble etter instruksjonen kl. 22:32: steg 1–4 felles, så den ekte versjonen (steg 5–9) og demoen (steg 5–7), i den rekkefølgen README-en har dem. Før PR 3 sto `git clone https://github.com/IBE160-2026/G74-lund-osen.git` og `cd G74-lund-osen` som rad 2 og 3, demoen før den ekte versjonen, og `Ctrl+C` og `docker compose --profile demo down` som to rader. Nytt i PR 3: rad 1 (installer og start, slått sammen av to rader), rad 2–4 (Download ZIP, PowerShell eller Terminal, og `cd`), rad 5 (nøkkelen), `notepad .env` og `open -e .env` i rad 6, og rad 23 (spørsmålene i «Står du fast?» og `docs/hjelp.md`). Slått sammen: rad 15 (Ctrl+C og `docker compose --profile demo down`). Flyttet: radene for den ekte versjonen står nå før demoen, som 6–10 (før rad 10–14). De andre radene er de samme som før, med nytt nummer. Koden hentes nå med «Download ZIP», så prøveren har ikke git: commiten som ble prøvd, er den GitHub viser øverst på siden når ZIP-fila lastes ned, og mappa som ikke skal finnes, er `G74-lund-osen-main`, ikke `G74-lund-osen` som i punktet om maskinen over. Radene 2 og 3 følger Marians svar kl. 21:14 samme dag: ZIP-fila må pakkes ut med «Pakk ut alle», Windows viser filene uten filendelse, og «Windows PowerShell ISE» står også i lista.

*Rettet 2026-10-18 (story 3.3c):* tabellen følger «Kom i gang» med demoen før den ekte versjonen (gruppen 16.10 kl. 21:16, svarene kl. 21:25). Radene for demoen, som var 11–15, er nå 5–9, og radene for den ekte versjonen, som var 5–10, er nå 10–15. Teksten i radene er den samme. Kolonnen «Tid» er ny: hvor lang tid hvert steg tok, i minutter.

*Rettet 2026-10-18 (gjennomgangen av 3.3c, BH7 og BH8):* rad 16 er skrevet om etter den nye rekkefølgen. Før sto det «Byttet: `docker compose --profile demo down`, så `docker compose up --build`, så det samme tilbake til `docker compose up --build demo`», som begynte med å stoppe demoen, men nå er den ekte versjonen den siste som kjørte (rad 15). Kolonnen heter «Tid (min)», så enheten står i tabellen.

*Rettet 2026-10-18 (story 3.2b):* appen bruker port 8000 fra 18.10, etter gruppens svar kl. 17:40, fordi AirPlay-mottakeren på Mac bruker 5000. Rad 6, 12 og 19 i Prøve 1 og rad 3 i Prøve 2 sa http://127.0.0.1:5000, og sier nå http://127.0.0.1:8000.

- **Det som ikke stemte:**
- **Rettet i** (commit eller story):

### Prøve 2: den ekte versjonen med egen nøkkel

*Lagt til 2026-10-13, etter faglærers tilbakemelding 06.10 og Marians ja kl. 13:44.*
Kriteriet «Kjørbar for andre» i briefen v8 krever også den ekte versjonen med
egen gratiskonto hos EODHD (`prd.md` §7), og Prøve 1 gjøres uten nøkkel. Testeren
lager sin egen gratiskonto, så kallene går fra testerens kvote og aldri fra
gruppens. EODHDs vilkår forbyr å dele kontoen (FR-411). Maskinen er den fra
Prøve 1 eller en annen ren maskin, aldri PC-en gruppen utvikler på. Prøven tas når
hentingen kan gi kurser, se «Når kan jeg hente?» i
[`docs/hjelp.md`](hjelp.md): etter kl. 22 og før midnatt på en børsdag.

*Lagt til 2026-10-17:* fra 19.10 er det etter kl. 21 og før midnatt, og `docs/hjelp.md` sier det (beslutningen 16.10 kl. 21:09 under story 2.3, `malinger.md` §31). Det gjelder også steg 4 i tabellen under.

*Lagt til 2026-10-20:* fra 20.10 er det etter kl. 22 og før midnatt igjen, og `docs/hjelp.md` sier det i en Rettet-linje under svaret (gruppens svar 19.10 kl. 22:19 under story 2.3, `malinger.md` §37). Det gjelder også steg 4 i tabellen under.

*Rettet 2026-10-20 (story 3.3h, gjennomgangen ECH1 og VG1):* linja over sier at `docs/hjelp.md` har kl. 22 i en Rettet-linje under svaret. Fra 3.3h er hjelpen et levende dokument (gruppens svar 20.10 kl. 16:19), og selve svaret «Når kan jeg hente?» sier kl. 22. Rettet-linja er tatt ut.

- **Hvem som prøver:** åpent.
- **Dato og klokkeslett:**
- **Maskin og operativsystem:**
- **Docker Desktop, versjon** (`docker version`, linjen med «Docker Desktop»):
- **Logget inn i Docker Desktop:** ja / nei.
- **Maskinen:** den fra Prøve 1 / en annen ren maskin. Ikke PC-en gruppen utvikler på.
- **Egen gratiskonto hos EODHD, laget av testeren:** ja / nei. Nøkkelen skrives ikke her.
- **Commit som ble prøvd** (den GitHub viser når ZIP-fila lastes ned):

| # | Kommando eller steg i README-en | Det som skjedde |
|---|---|---|
| 1 | Den ekte versjonen, steg 5: lag en gratis bruker hos EODHD og kopier API-nøkkelen. Ba registreringen om kort eller betaling? | |
| 2 | Den ekte versjonen, steg 6: `cp .env.example .env`, så `notepad .env` (Windows) eller `open -e .env` (Mac), og lim inn nøkkelen etter `EODHD_API_KEY=` | |
| 3 | Den ekte versjonen, steg 7: `docker compose up --build` og http://127.0.0.1:8000. Var oversikten tom, med kommandoen som henter? | |
| 4 | Den ekte versjonen, steg 8: `docker compose run --rm hent` i et nytt vindu, etter kl. 22 på en børsdag. Sa utskriften hvilken børsdag vurderingene gjelder? (Prøve 1 tar ikke denne sjekken) | |
| 5 | Siden lastet på nytt: ble oversikten fylt med aksjene, signalstyrken og retningen? (Prøve 1 tar ikke denne sjekken) | |
| 6 | En aksje åpnes fra oversikten | |
| 7 | Den ekte versjonen, steg 9: Ctrl+C i vinduet med appen, så `docker compose down`. Stod det «Removed»? | |
| 8 | `docker ps -a` til slutt: står det containere igjen fra prøven? | |
| 9 | Ble et spørsmål i «Står du fast?» eller i `docs/hjelp.md` brukt? Hvilket, og hjalp svaret? | |

- **Det som ikke stemte:**
- **Rettet i** (commit eller story):

### Prøve 3: den lokale modellen

*Lagt til 2026-10-15 (story 10.2, PR F, planen for KI-laget 15.10 kl. 15:43):* «Den lokale modellen (KI-teksten)» under «Mer for den som vil» i README-en. Prøven tas på en maskin med grafikkort fra NVIDIA, etter Prøve 2, med den ekte versjonen og egen EODHD-nøkkel. Ollama trenger ingen nøkkel.

*Lagt til 2026-10-19 (story 3.3g, gjennomgangen VG5):* knappen heter nå «Den lokale modellen for KI-teksten (valgfri)», og første setning sier at den ikke trengs for demoen eller for å vurdere appen. Prøven står som før.

- **Dato:**
- **Maskin og grafikkort:**
- **Commit som ble prøvd:**

| # | Kommando eller steg i README-en | Det som skjedde |
|---|---|---|
| 1 | `docker compose --profile ki up -d ollama`. Startet Ollama, og hvor lang tid tok det første gang? | |
| 2 | `docker compose exec ollama ollama pull gemma4:e4b`. Hvor lang tid tok det? | |
| 3 | `OSE_KI_TJENESTE=lokal` i `.env` | |
| 4 | Hentingen som i Prøve 2. Sa utskriften hvor mange KI-tekster som besto kontrollen? | |
| 5 | `docker compose --profile ki down`. Stod det «Removed»? | |
| 6 | En henting uten Ollama: sa utskriften at Ollama ikke svarer, at ingen rader er skrevet i KI-loggen, og gikk hentingen som før? | |
| 7 | En henting med Ollama i gang, men uten modellen hentet: sa utskriften at modellen ikke er hentet, og at ingen rader er skrevet? | |
| 8 | Ollama startet og hentingen kjørt igjen samme kveld etter steg 6: ble KI-tekstene laget? Les `/api/user` før og etter: `apiRequests` skal være uendret | |
| 9 | Modellen hentet og hentingen kjørt igjen etter steg 7: ble KI-tekstene laget? | |
| 10 | `OSE_KI_TJENESTE=av` i `.env` til slutt | |

- **Det som ikke stemte:**
- **Rettet i** (commit eller story):

## 10. Suksesskriteriene og testene

*Lagt til 2026-10-13, etter faglærers tilbakemelding 06.10
([`tilbakemelding-product-brief.md`](../_bmad-output/planning-artifacts/tilbakemelding-product-brief.md)):*
«Legg til suksesskriterier for at signalberegningen er riktig, slik at testene
kan spores tilbake til briefen.»

De fire kriteriene i briefen v8
([`product-brief.md`](../_bmad-output/planning-artifacts/product-brief.md),
«Success Criteria»), slik de står i `prd.md` §7, med testene og kontrollene som
viser dem. Tabellen viser bare tester og kontroller som finnes. En test i
`tests/test_suksesskriterier.py` krever at hver test tabellen viser til, finnes,
og at alle fire kriteriene står her.

| Kriterium | Testene og kontrollene som viser det | Det som står igjen |
|---|---|---|
| **Riktige beregninger**: håndlagde kursserier gir forhåndsberegnet styrke og retning, ved hver testkjøring | `tests/test_signalberegning.py::TestSignalstyrke::test_alle_tre_sjekkene_slaar_ut`, `tests/test_signalberegning.py::TestSignalstyrke::test_sjekkene_spriker_gir_blandet`, `tests/test_signalberegning.py::TestSignalstyrke::test_flat_serie_gir_styrke_0_og_ingen_retning`, `tests/test_signalberegning.py::TestStyrke::test_styrke_er_summen_av_absoluttverdiene`, `tests/test_signalberegning.py::TestRetning::test_alle_utslag_opp_er_positiv`, `tests/test_signalberegning.py::TestRetning::test_alle_utslag_ned_er_negativ`, `tests/test_signalberegning.py::TestRetning::test_sprikende_utslag_er_blandet`, `tests/test_signalberegning.py::TestRetning::test_ingen_utslag_er_ingen`, `tests/test_signalberegning.py::TestJustertKurs::test_signalet_foelger_justert_ikke_ujustert_kurs`, `tests/test_signalberegning.py::TestNoytralsone::test_noeyaktig_paa_grensen_gir_null`, `tests/test_signalberegning.py::TestTerskel::test_styrke_paa_terskelen_skiller_seg_ut` og `tests/test_signalberegning.py::TestMaalingen::test_regelen_paa_maalingene_gir_verdien_sjekken_ga`. Kontrollene: håndregningen for EQNR 05.10 og GJF 02.10 i `malinger.md` §6, håndkontrollen av første utslag på interesse i `malinger.md` §25, mutantpraksisen i §3 og kontrollregningen på ekte data i §4 her | Ingenting. Testene kjøres i CI ved hver push (§2) |
| **Brukerutfall**: minst én person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut, under 5 minutter, uten hjelp | Ingen ennå. Kriteriet måles med en person, ikke med en test | Brukertesten i story 8.1 |
| **KI-forklaringen**: hver KI-tekst som vises, har bestått kontrollen mot grunnlaget, og testene viser at feil stoppes. Én ukes drift er logget | Ingen ennå. KI-laget er ikke bygget | Kontrollen i FR-603 (story 10.2), loggen i FR-604 (story 4.2 og 4.3), visningen (story 10.3) og målingen av bidraget (story 10.4) |
| **Kjørbar for andre**: README-oppskriften fullføres gratis på en ren maskin, uten gruppens nøkler: demoen uten konto, og den ekte versjonen med egen gratiskonto hos EODHD | `tests/test_demo.py::TestDemokommandoen::test_lages_uten_nett_og_uten_noekkel`, `tests/test_demo.py::TestSidene::test_bryteren_med_demobase_viser_eksempeltall`, `tests/test_docker.py::TestImaget::test_ingen_noekkel_i_imaget`, `tests/test_docker.py::TestReadme::test_kommandoene_er_de_samme_som_i_koden_og_compose`, `tests/test_docker.py::TestReadme::test_readme_proeven_har_hver_kommando` og `tests/test_readme.py::test_hver_lenke_i_readme_peker_paa_noe_som_finnes`. Kontrollen: README-prøven i §9, Prøve 1 (demoen uten nøkkel) og Prøve 2 (den ekte versjonen med egen nøkkel) | Ingen av prøvene i §9 er gjort ennå |

*Lagt til 2026-10-13:* håndregningen for TEL 08.10, en dag med utslag på
interesse, står i `malinger.md` §6, ved siden av EQNR 05.10 og GJF 02.10.

*Lagt til 2026-10-16:* raden «KI-forklaringen» sier «KI-laget er ikke bygget». Det stemte 13.10, men nå finnes testene for kontrollen, loggen og visningen. Kontrollen i FR-603 (story 10.2a, PR #48, `77ebf31`): `tests/test_ki_modell.py`, med `TestKontrollen` og `TestRaden`. Loggen i FR-604 (story 4.2 og 4.3): `tests/test_kilogg.py`, der kontrakttestene kjøres mot både minnet og SQLite, og `tests/test_kilogg_sqlite.py`. Visningen (story 10.3, PR #50 og #51): `tests/test_ki_visning.py`, med `TestSiden::test_vakten_paa_siden` og `TestGrunnenPaaSiden`. Talt 16.10: 207 tester i `test_ki_modell.py`, 106 i `test_kilogg.py`, 49 i `test_kilogg_sqlite.py` og 67 i `test_ki_visning.py`. Teksten lages ennå ikke i hentingen (story 10.2b, PR #49, ikke flettet), så ingen KI-tekst er laget med ekte data. Én ukes logget drift begynner når PR #49 er flettet, og målingen av bidraget er story 10.4.

*Lagt til 2026-10-23 kl. 14:51:* raden «Brukerutfall»: opplegget for brukertesten står i `spec-8-1-brukertesten.md`, og skjemaet er `docs/brukertest.md`. Testen tas neste uke, med story 10.4 rett etter, med samme person og samme aksje (gruppens svar 23.10 kl. 12:29). Kriteriet er ikke målt ennå.

## 11. Feil vi fant og rettet

*Lagt til 2026-10-17.* Tolv eksempler fra repoet, med minst ett for hver måte en feil ble funnet. «Rettet i» er commiten på main. Ble PR-en squash-flettet, står grencommiten i parentes, og den finnes i PR-en på GitHub. En mutant som overlevde, viser et hull i testene, ikke nødvendigvis en feil i koden.

| # | Hva var feil | Funnet av | Rettet i | Testen som passer på nå |
|---|---|---|---|---|
| 1 | Nøkkelen kunne stå i feilteksten fra `requests`, fordi adressen med `api_token` står i teksten | **En test:** de nye testene ble kjørt mot koden før rettingen, og HTTP-testen feilet med adressen og den falske nøkkelen i teksten (`S/spec-2-0-…`, linje 75) | `4b65a3c` (#6) | `tests/test_fetch_prices.py::TestNoekkelenLekkerIkke::test_http_feil_gir_statuskode_uten_adresse` |
| 2 | Ingen test viste at to migreringer samtidig bare kjører `0001` én gang: `BEGIN` i stedet for `BEGIN IMMEDIATE` ga ingen feil | **En mutant** som overlevde i 1.5b (§3) | `9aa6131` (#14) | `tests/test_migrering.py::TestToMigratorerOverlapper::test_begge_lykkes_og_0001_kjoeres_en_gang` |
| 3 | Ingen test fanget at et nytt forsøk fredag kveld kunne skrive raden etter midnatt (M10), eller at et forsøk uten kall laget en tom fil (M20) | **Mutanter** som overlevde første kjøring i 2.3b | `c3d6660` (#28, `bf41134`) | `tests/test_fetch_prices.py::TestNyttForsoekEtterMutantene::test_fredag_over_midnatt_skriver_ingen_rad` og `tests/test_fetch_prices.py::TestNyttForsoekEtterMutantene::test_ingen_kall_gir_ingen_fil` |
| 4 | uv lastet ned sin egen Python i imaget (I5) | **En mutant** som overlevde i 3.1 | `a2ecee8` (#23), med `UV_PYTHON_DOWNLOADS=never` | `tests/test_docker.py::TestImaget::test_uv_laster_aldri_ned_en_egen_python` |
| 5 | Grunnlaget til KI sjekket ikke at retningen er en av de fire i lista (GR2) | **En mutant** som overlevde i 10.1 | `6855861` (#47, `2ae86b4`) | `tests/test_ki_grunnlag.py::TestKontrollen::test_retning_utenfor_den_lukkede_lista` |
| 6 | En henting som snudde rådataene på stedet, ville ikke blitt fanget | **En linse** i gjennomgangen av 1.8 (BH5 og ECH1, §3) | `5c316e8` (#10) | `tests/test_fetch_prices.py::TestHentUniverset::test_raadataene_lagres_uendret` |
| 7 | En `Indeks` med symbolet til en aksje ble godtatt av porten | **En linse** i gjennomgangen av 2.8a (ECH) | `1d3a21d` (#56) | `tests/test_indeks.py::TestPorten::test_en_aksje_avvises_ogsaa_naar_den_er_gitt_som_indeks` |
| 8 | Feilet en aksje og indeksen samme kveld, kunne et nytt forsøk som rettet aksjen, avslutte kvelden med kode 0 | **En linse** i gjennomgangen av kode 3 (BH4 og ECH2, `S/spec-2-8b-…`) | `bcac2b5` (#57, `a15f234`) | `tests/test_fetch_prices.py::TestKode3EtterGjennomgangen::test_et_nytt_forsoek_etter_en_aksje_og_indeksen_gir_kode_3` |
| 9 | En rad i indeksen som ikke kunne tolkes, ville gitt feilsiden (500) i stedet for tabellen | **En linse** i gjennomgangen av 2.9 (ECH1, ECH5 og BH4, `S/spec-2-9-…`) | `b44284f` (#59, `5539e4a`) | `tests/test_app.py::TestHovedindeksenPaaForsiden::test_en_rad_som_ikke_kan_tolkes_stopper_ikke_siden` |
| 10 | Sjekken av basen før kallene falt bort når basen sto en versjon bak, og bare filvakten holdt | **Utskriften fra den ekte hentingen** 16.10 kl. 22:10: «Basen ose.db kunne ikke leses (RuntimeError). Henter likevel» (`D/2026-10-16.md`) | `bcac2b5` (#57, `1610a24`) | `tests/test_fetch_prices.py::TestSjekkenLeserEnBaseEnVersjonBak::test_de_tre_sjekkene_virker_en_versjon_bak_og_fila_er_uendret` |
| 11 | Kontrollen stoppet 9 av 15 KI-tekster på regel 4 («skyldes» og «indikerer»), også der ordet bare forklarte regelen | **Kontrollen av KI-teksten** i prøvekjøringen 16.10 (`malinger.md` §32) | `cafe067` (#55), prompten versjon 2. I prøvekjøringen etter besto 15 av 15 (§34) | `tests/test_ki_modell.py::TestPrompten::test_regelen_forklares_med_fordi` og `tests/test_ki_modell.py::TestPrompten::test_versjonen_foelger_teksten` |
| 12 | I «Kom i gang» ble ZIP-fila dratt inn i stedet for mappa, mellomrommet etter `cd` manglet, «Cannot find path» hadde ikke noe svar, og det var uklart hvor kommandoen limes inn og hvor kopi-ikonet er | **Vår egen gjennomgang** av «Kom i gang» 16.10 kl. 20:40–21:11 (under story 3.3 i `epics.md`) | **Ikke rettet ennå.** Det bygges i README-PR-en søndag 18.10 | Ingen ennå |

## 12. Feilhåndtering, validering av input og hemmeligheter

*Lagt til 2026-10-17.* Hva appen gjør når noe mangler eller er feil, og hvordan nøkkelen holdes ute, med testene som viser det.

- **Nøkkelen står aldri i koden eller i repoet.** `.env` holdes ute av `.gitignore`, og ingenting av det er sporet i git: `tests/test_ryddighet.py::test_gitignore_holder_ute_noekler_data_og_private_mapper` og `tests/test_ryddighet.py::test_ingenting_av_det_er_sporet_i_git`.
- **Nøkkelen står aldri i imaget,** og bare tjenesten som henter, får den: `tests/test_docker.py::TestImaget::test_ingen_noekkel_i_imaget`, `tests/test_docker.py::TestCompose::test_bare_hent_har_noekkelen` og `tests/test_docker.py::TestOllama::test_ingen_noekkel_i_compose`.
- **Nøkkelen står aldri i utskriften eller i fila.** Feilene fra `requests` vaskes, også når nøkkelen er URL-kodet: `tests/test_fetch_prices.py::TestNoekkelenLekkerIkke::test_http_feil_gir_statuskode_uten_adresse`, `tests/test_fetch_prices.py::TestNoekkelenLekkerIkke::test_hent_universet_fjerner_noekkelen_fra_enhver_feil` og `tests/test_fetch_prices.py::TestNoekkelenLekkerIkke::test_url_kodet_noekkel_fjernes_ogsaa`.
- **CI kjører uten hemmeligheter.** Arbeidsflyten har `permissions: contents: read` og ingen `secrets.`. Det har ingen test, og står i §6.
- **Webserveren gjør ingen nettkall,** og importerer verken hentingen eller en modell: `tests/test_app.py::test_rutene_gjoer_ingen_nettverkskall`, `tests/test_konsumentene.py::test_webserveren_importerer_ikke_hentingen` og `tests/test_ki_visning.py::test_webserveren_importerer_ingen_modell`.
- **Sidene når basen mangler, er tom eller feiler.** En tom base gir en beskjed med kommandoen som henter, og en base som er nyere enn koden eller feiler under lesingen, gir 503 med grunnen og uten stier. En base som mangler, lages ikke av siden som leser: `tests/test_app.py::test_uten_kilde_viser_beskjed_i_stedet_for_aa_feile`, `tests/test_app.py::TestBasenIWebserveren::test_tom_base_gir_tom_tilstand_med_kommandoen`, `tests/test_app.py::TestBasenIWebserveren::test_basen_nyere_enn_koden_gir_503_med_grunnen`, `tests/test_app.py::TestBasenIWebserveren::test_feilsiden_viser_ingen_stier`, `tests/test_app.py::TestVurderingenIDetaljen::test_feil_i_spoerringen_gir_503_paa_begge_rutene` og `tests/test_lagring_sqlite.py::TestAapneBaseUtenMigrering::test_en_base_som_mangler_lages_ikke`.
- **Sidene når indeksen mangler eller ikke kan leses.** Delen sier det, og tabellen vises (NFR-03): `tests/test_app.py::TestHovedindeksenPaaForsiden::test_uten_indeks_sier_siden_det_og_tabellen_vises`, `tests/test_app.py::TestHovedindeksenPaaForsiden::test_en_indeks_som_ikke_kan_leses_stopper_ikke_siden` og `tests/test_app.py::TestHovedindeksenPaaForsiden::test_en_rad_som_ikke_kan_tolkes_stopper_ikke_siden`.
- **Validering av input.** En kursrad med et tall som ikke er endelig, avvises, og et svar med feil form gir en feil for den ene aksjen, mens de andre hentes (AD-15). En ukjent sortering i adressen gir standardrekkefølgen, og et ukjent eller uleselig symbol gir 404. Det gamle navnet på flagget avvises: `tests/test_kurslager.py::TestKursrad::test_ikke_endelige_tall_avvises`, `tests/test_fetch_prices.py::TestSvarMedFeilForm::test_feil_form_gir_feil_for_symbolet_og_de_andre_hentes`, `tests/test_fetch_prices.py::TestSvarMedFeilForm::test_ingen_aksje_forsvinner_uten_aa_staa_i_feil`, `tests/test_markedsoversikt.py::TestSorteringVedKlikk::test_ukjent_i_adressen_gir_ingen_sortering`, `tests/test_app.py::TestAksjedetalj::test_ukjent_symbol_gir_404`, `tests/test_app.py::TestAksjedetalj::test_uleselig_symbol_gir_404` og `tests/test_fetch_prices.py::TestTidskontrollen::test_det_gamle_flaggnavnet_godtas_ikke`.
  *Rettet 2026-10-23 (story 8.6, gruppens svar kl. 09:24, b; gjennomgangen VG2):* et uleselig symbol gir 404 bare når basen ikke har en eneste kurs, som før første henting. En aksje i lista uten kurser i en base med andre kurser svarer 200 med en beskjed: `tests/test_app.py::test_uleselig_symbol_navngis_i_fotnoten` og `tests/test_boersometer.py::TestSvaretKl0924::test_aksjesiden_uten_kurser_svarer_200_med_beskjed`.
- **Kvoten leses før kallene.** Nøkkelen og kvoten kommer før første kall, og en kvote som ikke holder, gir 0 kall: `tests/test_fetch_prices.py::TestRekkefoelgen::test_noekkelen_og_kvoten_kommer_foer_foerste_kall`, `tests/test_fetch_prices.py::TestKvoten::test_under_15_uten_nok_bonus_gir_0_kall_og_kode_1` og `tests/test_fetch_prices.py::TestKvoten::test_15_igjen_holder_ikke_for_16_uten_bonus`.
- **Vaktene mot demobasen.** Hentingen nekter en demobase før alt annet, og demokommandoen nekter en ekte base og en tom fil: `tests/test_demo.py::TestVaktene::test_hentingen_nekter_en_demobase_foer_alt_annet`, `tests/test_demo.py::TestVaktene::test_demokommandoen_nekter_en_ekte_base` og `tests/test_demo.py::TestVaktene::test_demokommandoen_nekter_en_tom_fil`.

## 13. Manuelle tester og testplaner

*Lagt til 2026-10-17.* Det som er prøvd for hånd eller er planlagt, med dato og resultat der det finnes.

| Hva | Dato | Resultat | Kilde |
|---|---|---|---|
| README-prøven, Prøve 1 (demoen uten nøkkel), Prøve 2 (den ekte versjonen med egen nøkkel) og Prøve 3 (den lokale modellen) | Ikke tatt. Tas senest én uke før innleveringen | Ingen ennå | §9 |
| Kontrollregningen av de tre sjekkene i et regneark | Dagene 05.10 (EQNR), 02.10 (GJF, utslag på bevegelse) og 08.10 (TEL, utslag på interesse), ført 06.10 og 13.10 | De fire målingene, de tre verdiene, styrken og retningen i regnearket er like det appen lagret | `malinger.md` §6; §6 og §10 her |
| Kursene mot Oslo Børs, for hånd | OSEBX 01.10 | Sluttverdien for OSEBX er kontrollert én gang. Kontrollen av aksjene gjenstår | `malinger.md` §6 og §14 |
| Navnene i demoen mot lista hos Euronext, for hånd | 10.10 kl. 12:25 | Kontrollert av en av oss, og av rådet med et søk på nettet samme dag. Resultatet per navn står ikke i kommentaren | kommentaren ved `DEMOUNIVERS` i `src/demo.py` |
| `DEMIX` og «Demoindeksen» mot lista hos Euronext, for hånd | 17.10 kl. 00:25 | Verken symbolet eller navnet finnes der, og PR #56 ble flettet | `S/spec-2-8a-indeks-tabellen-og-porten.md` |
| Vår egen gjennomgang av «Kom i gang», som en som aldri har gjort det | 16.10 kl. 20:40–21:11 | Fire ting som ingen test fant (§11, eksempel 12). De bygges i README-PR-en søndag 18.10 | under story 3.3 i `epics.md`; `docs/reflection-log.md`, 16.10 |
| Gruppens gjennomgang av «Kom i gang» for demoen på egen PC | 21.10, steg 1–5 kl. 22:19–22:34 og steg 6–7 til kl. 23:44 | Demoen startet, sidene ble gått gjennom, og demoen ble stoppet, så steg 1–7 er gått gjennom. Steg 2–4 var vanskeligst: PowerShell sto i den ytre mappa, som hadde fått et nummer etter flere nedlastinger, og ga «no configuration file provided: not found». Det ble løst med `cd` i samme vindu kl. 22:34. Første gang åpnet ikke siden seg i nettleseren, og grunnen er ikke kjent. 49 funn fra gjennomgangen og 13 forskjeller mot designtavla står som U8–U69, og seks avgjørelser kom samme kveld | `docs/ux-logg.md`, «Åpne funn før brukertesten», U8–U69; avgjørelsene 21.10 kl. 22:47–23:51 under «Prioritering» i `epics.md` |
| PowerShell fra adressefeltet i Filutforsker, i den innerste mappa (steg 3 etter 3.3i) | 22.10 kl. 17:42, på maskinen repoet ligger på: Windows 11 Home, versjon 25H2 (build 26200), slått opp med `Get-CimInstance Win32_OperatingSystem` | PowerShell åpnet i mappa, og `dir` viste `README.md` og `compose.yaml` | gruppens svar 22.10 kl. 17:42 under story 3.3 i `epics.md`; `S/spec-3-3i-readme-rettingen-etter-demoen.md` |
| Prøvekjøringene av KI-teksten mot en kopi av basen | 16.10 kl. 22:26–22:27 og kl. 23:43–23:44 | 6 av 15 besto med prompten versjon 1, og 15 av 15 med versjon 2 | `malinger.md` §32 og §34 |
| Grensen kl. 21:00: fire aksjer hentes på nytt og sammenlignes med kursfila | Planlagt mandag 19.10, etter kl. 22 | Ingen ennå | beslutningen 17.10 kl. 22:00 under story 2.3 i `epics.md` |
| Brukertesten (story 8.1) | Ikke tatt | Ingen ennå. Den måler også suksesskriteriet «Brukerutfall» (§10) | `sprint-status.yaml`, 8-1 i backlog |

*Lagt til 2026-10-20:* raden «Grensen kl. 21:00»: målingen ble tatt 19.10 etter kl. 22 (`malinger.md` §37). MOWI, GJF og AKRBP var like kursfila fra kl. 21 i alle sju feltene, og DNO var ulik i `volume`. Grensen er kl. 22:00 igjen fra 20.10 (gruppens svar 19.10 kl. 22:19 under story 2.3). Raden i tabellen er ikke endret.

*Lagt til 2026-10-18 (gruppens svar kl. 00:03):* README-prøven i første rad tas første gang i uke 43 (19.–25.10), etter at de to README-PR-ene er flettet: Prøve 1, og Prøve 2 samtidig hvis testeren har egen gratiskonto. Den tas på nytt senest én uke før innleveringen, med ZIP-fila som leveres (§9).

*Rettet 2026-10-21 kl. 18:33:* Linja over om README-prøven i uke 43 (gruppens svar 18.10 kl. 00:03) gjelder ikke lenger. Prøven på en ren maskin er utsatt til v1 er ferdig bygget, etter avgjørelsen 2026-10-21 kl. 18:33 under «Prioritering» og story 3.3 i `epics.md`.

*Avgjort 2026-10-21 kl. 18:33 (gruppens svar):* README-prøven på en ren maskin er utsatt til v1 er ferdig bygget, fordi flere deler skal inn (historikken 2.7b, som ble flettet i `d4c2441` kl. 17:58 samme dag, og egne nøkler 10.7), og prøven skal gjelde den appen som leveres. Gruppen har kjørt oppskriften på egen maskin, og den virker. Den siste daterte gjennomgangen på egen maskin som står i repoet, er 16.10 kl. 20:40–21:11, under story 3.3 i `epics.md` (avgjørelsen 16.10 kl. 21:16), i tabellen i §13 i `docs/kvalitetssikring.md` og i `docs/reflection-log.md` 16.10. Den fant fire ting, som ble rettet i `fdaf403`, PR #66, 18.10. Prøven på en ren maskin er fortsatt funksjonsstoppen, senest én uke før innleveringen (svaret 19.10 kl. 14:48), og 3.4 står i review til den er tatt.

*Lagt til 2026-10-18 kl. 15:41 (story 3.3c, ECH16 i triagen):* README-en har nå tre skjermbilder i «Kom i gang», fra gruppens gjennomgang 16.10 kl. 20:40–21:11 (raden i tabellen over): «Engine running» i steg 1, menyen under «Code» med «Download ZIP» i steg 2, og PowerShell med mappenavnet foran `>` i steg 4. De ligger i `docs/bilder/readme/` og viser ikke appen. Demoen står før den ekte versjonen, og de fire tingene gjennomgangen fant, er rettet. Flettet i `fdaf403`, PR #66.

*Lagt til 2026-10-23 kl. 14:51:* raden «Brukertesten (story 8.1)»: opplegget står i `spec-8-1-brukertesten.md`, med story 10.4 i samme økt (gruppens svar 23.10 kl. 12:29), og skjemaet er `docs/brukertest.md`. Testen er ikke tatt, og tas neste uke. 8-1 og 10-4 er ready-for-dev i `sprint-status.yaml`.

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

### Fra 2.2 til 10.3, én linje per spesifikasjon

*Lagt til 2026-10-17.* Mutantene står med testene som fanget dem, slik spesifikasjonen navngir dem. Der testene er mange, viser linja til tabellen i spesifikasjonen, der hver mutant står med sin test.

| Story | Mutantene | Fanget av | Kilde |
|---|---|---|---|
| 2.2 | M1–M18 | M1 `test_oppstart_med_tom_base_gjoer_ingen_nettkall`, M2 `test_migrer_kjoeres_en_gang_for_to_forespoersler`, M3 `test_tilkoblingen_lukkes_etter_forespoerselen`, M7 `test_en_base_som_mangler_lages_ikke`, M10 og M15 `test_basen_nyere_enn_koden_gir_503_med_grunnen`, M14 `test_slettet_base_lages_paa_nytt`, M16 `test_feilsiden_viser_ingen_stier`, M17 `test_andre_ruter_roerer_ikke_basen`, M18 `test_feil_mens_sidene_leser_gir_503`; resten i tabellen | `S/spec-2-2-…` |
| 2.2b | M1–M15 | M4, M8 og M10 blant andre `test_app_har_ingen_sql_og_regner_ikke_signalet`, M6 `test_styrke_0_vises_som_0`, M9 `test_utenfor_boerskalenderen_gir_tekst_ikke_feil`, M13 `test_dato_etter_i_dag_gir_tekst_ikke_feil`, M15 `test_feil_i_spoerringen_gir_503_paa_begge_rutene`; resten i tabellen | `S/spec-2-2b-…` |
| 2.3 | M1–M8, K1–K4 og V1–V4, så 15 mot hver sin test og B4 | M1 og M5 `TestTidskontrollen::test_boersdag_kl_20_59_59_gir_0_kall_og_nevner_flagget` (før 17.10: `test_boersdag_foer_kl_22_gir_0_kall_og_nevner_flagget`), K1 `test_dagen_regnes_i_gmt_ikke_i_oslo`, K4 `TestRekkefoelgen::test_noekkelen_og_kvoten_kommer_foer_foerste_kall`, V2 `TestVintertid::test_kl_20_59_i_oslo_i_november_nekter` (før 17.10: `test_kl_21_59_i_oslo_i_november_nekter`); resten i tabellen. De to tidstestene fikk nytt navn med grensen kl. 21:00 (`336204f`) | `S/spec-2-3-boersdagskontroll-…` |
| 2.3, kl. 21 | T1–T3 | T1 `test_grensen_er_kl_21`, T2 `test_kl_21_presis_henter`, T3 `test_det_gamle_flaggnavnet_godtas_ikke` | `S/spec-2-3-hentingen-fra-kl-21.md` |
| 2.3, kl. 22 | G1–G2 | G1 `test_boersdag_kl_21_59_59_gir_0_kall_og_nevner_flagget` (i hele fila først `test_grensen_er_kl_22`), G2 `test_kl_22_presis_henter` | `S/spec-2-3-hentingen-fra-kl-22.md` |
| 2.3b | 28 | M1, M2, M6 og M13 `TestNyttForsoek::test_bare_de_som_mangler_hentes_eldste_foerst`, M10 `test_fredag_over_midnatt_skriver_ingen_rad`, M20 `test_ingen_kall_gir_ingen_fil`, M22 `test_dagens_kall_brukt_opp_underveis_stopper`, M23 `test_fil_som_dukker_opp_gir_neste_n`; resten i tabellen | `S/spec-2-3b-…` |
| 2.7a | M1–M3 og N1–N3 | M1 `test_ingen_style_i_malene`, M2 `test_ingen_velger_staar_to_ganger_med_samme_kropp`, M3 `test_fila_svarer_200_fra_lenken_paa_hver_side`, N1 `test_siden_vises_ogsaa_naar_fila_ikke_kan_leses`, N2 `test_de_seks_felles_reglene_staar_en_gang_for_alle_sidene`, N3 `test_velgere_med_ulik_kropp_er_avgrenset_til_hver_sin_side` | `S/spec-2-7a-…` |
| 2.8a | I1–I4 | I1 og I3 `test_serien_byttes_ut_ikke_skjoetes_paa[sqlite]`, I2 `test_en_loerdag_og_en_helligdag_lagres_ikke[minne]`, I4 `test_indeksen_for_alle_demodagene` | `S/spec-2-8a-…` |
| 2.8b | A1, B2–B5, V1, V2, K1–K4 | A1 `test_de_tre_sjekkene_virker_en_versjon_bak_og_fila_er_uendret`, B2 `test_indeksen_lagres_i_indeks_aldri_i_kurs_eller_vurdering`, B3 `test_15_igjen_holder_ikke_for_16_uten_bonus`, B4, K1 og K2 `test_et_feilet_indekskall_stopper_ikke_aksjene[feil]`, B5 `test_bare_de_som_mangler_hentes_eldste_foerst`, V1 `test_en_serie_porten_avviser_stopper_ikke_aksjene`, V2 `test_en_eldre_fil_skriver_ikke_over_en_nyere_indeks`, K3 `TestOyeblikksbilde::test_formatet_kan_leses_av_visningen`, K4 `test_et_nytt_forsoek_etter_en_aksje_og_indeksen_gir_kode_3` | `S/spec-2-8b-…` |
| 2.9 | H1–H4 | H1 `test_n_er_aksjene_med_kurs_og_en_uten_navngis`, H2 `test_et_hull_foer_indeksens_dato_gir_ingen_endring`, H3 `test_lik_er_ikke_bedre`, H4 `test_like_foerst_etter_avrundingen_er_ikke_bedre` | `S/spec-2-9-…` |
| 3.1 | D1–D24 og I1–I9 | D1 `test_python_er_313_som_ci`, D4 `test_ingen_noekkel_i_imaget`, D5 og D23 `test_ikke_root`, D12 `test_bare_hent_har_noekkelen`, D18 `test_uv_laster_aldri_ned_en_egen_python`; I1–I9 fanges av stegene i CI, ikke av tester | `S/spec-3-1-…` |
| 3.2 | S1–S10 og C1–C8 | S1 og S2 `test_navngitte_volumer_aldri_data_paa_maskinen` og `test_volumene_overlapper_ikke`, S6 `test_skrivebeskyttet_rot_med_tmp_som_tmpfs`; C1–C8 fanges av stegene i CI. For S9 og S10 navngir tabellen ingen test | `S/spec-3-2-…` |
| 3.2b | P1–P5 | alle `test_porten_er_den_samme_overalt_og_ikke_5000` | `S/spec-3-2b-…` |
| 3.3 | R1–R15 og C1 | R1 `test_kommandoen_paa_den_tomme_siden_staar_i_readme`, R8 `test_tjenestene_i_readme_finnes_i_compose`, R9 `test_raadet_om_tidspunkt_uten_flagget`; for R13–R15 står bare «drept» | `S/spec-3-3-…` |
| 3.3b | S1–S20 og S5b (PR #53) | ikke navngitt per mutant i spesifikasjonen | `S/spec-3-3b-…` |
| 3.3c | M1–M9 | M1 `test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket`, M2, M8 og M9 `test_steg_4_mappa_ikke_zip_fila`, M3 `test_svaret_om_mellomrommet_etter_cd`, M4 `test_demoen_foerst_og_zip_foer_kommandoene`, M5 og M6 `test_kopieringen_forklares_en_gang_og_hvert_steg_sier_hvor`, M7 `test_henvisningene_og_proevetabellen` | `S/spec-3-3c-…` |
| 3.3d | N1–N11 | N1, N7 og N10 `test_status_uten_storynumre_og_uten_kommando`, N2 og N11 `test_staar_du_fast_har_hoeyst_5_spoersmaal` (N11 også `test_det_foerste_spoersmaalet_er_at_docker_ikke_kjoerer`), N3 `test_hvert_tema_staar_i_readme_eller_hjelp`, N4 `test_forklaringen_i_tester_staar_bak_en_knapp`, N5 og N9 `test_lenkene_virker`, N6, N8 og N9 `test_mappestrukturen_lenker_til_stier_i_repoet` | `S/spec-3-3d-…` |
| 3.3e | E1–E8 | E1 `test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket`, E2 og E5 `test_bildet_tas_paa_nytt_naar_oversikten_endres`, E3 `test_testene_uten_docker`, E4 `test_variablene_i_tabellen_er_de_i_env_example`, E6 `test_installasjonen_av_uv_staar_foer_uv_sync`, E7 `test_porten_er_den_samme_overalt_og_ikke_5000` og `test_standardene_i_tabellen_er_de_i_koden`, E8 `test_fila_finnes_og_er_1280_px_bred_og_1573_px_hoey` | `S/spec-3-3e-…` |
| 3.3f | M1–M3 og N1 | testene står per mutant i spesifikasjonen | `S/spec-3-3f-…` |
| 3.3g | M1, M2a, M2b, M3 og N1–N3 | M1 og N1 `test_kom_i_gang_anbefaler_demoen_for_faglaerer_og_sensor`, M2a og M2b `test_delen_om_den_lokale_modellen_sier_at_den_er_valgfri`, M3, N2 og N3 `test_ingen_av_de_ekstra_staar_under_neste_i_v1` | `S/spec-3-3g-…` |
| 3.3h | M1–M7 | M1 `test_de_felles_stegene_staar_ikke_bak_en_pil`, M2 `test_pila_til_demoen_sier_at_den_er_anbefalt_for_faglaerer_og_sensor`, M3 `test_hvert_steg_hver_kommando_og_hver_lenke_fra_foer_finnes`, M4 `test_markdown_inne_i_pilene_vises_riktig_paa_github`, M5 `test_hjelpen_sier_klokkeslettet_fra_tidsgrensen_og_har_ingen_daterte_linjer`, M6 `test_advarselen_mot_down_v_staar_synlig`, M7 `test_ferdig_begynner_med_signalet` | `S/spec-3-3h-…` |
| 3.4 | PR #26–#34 | testene står per mutant i tabellene i spesifikasjonen for PR #26, #27 og #30; for #31–#34 nevner avsnittene testen, som `test_hvorfor_bare_15_aksjer` og `test_til_faglaerer_lenker_til_briefen_med_gjeldende_tag` | `S/spec-3-4-demoversjonen.md` |
| 3.4, alle 10 | R1–R4 | med hele fila `test_kursene_har_samme_fingeravtrykk_paa_alle_plattformer`, med bare klassen `test_alle_ti_kombinasjonene_paa_sluttdato` | `S/spec-3-4-alle-ti-…` |
| 3.4b | K1–K6 | K1 `test_grunnlaget_stemmer_med_demodagen`, K2 `test_hver_tekst_demoen_viser_bestaar_kontrollen_slik_den_er_naa`, K3 `test_skriver_radene_uten_nett_og_uten_ollama`, K4 `test_en_kjoering_som_ikke_er_hel_skriver_ikke_fila`, K5 `test_en_oedelagt_fil_gir_en_demo_uten_ki_tekst`, K6 fiksturen `radene` i `tests/test_demo_ki.py` | `S/spec-3-4b-…` |
| 4.0 | N1–N5 og R1–R5 | N1, N3 og N5 `test_innsamlingen_er_sperret`, N2 `test_navneoppslag_blokkeres[gethostbyname]`, N4 `test_connect_ex_blokkeres`, R1 `test_asyncio_blokkeres`, R2 `test_udp_blokkeres` | `S/spec-4-0-…` |
| 4.2 | K1–K5 og KR1–KR6 | K3 `test_bare_skriv_og_lesemetoder`, K4 `test_bare_inneveerende_boersdag`, KR3 `test_dagen_regnes_i_oslo`; resten i tabellen | `S/spec-4-2-…` |
| 4.3 | C1–C3 og CR1–CR4 | C1 `test_tabellen_lages_bare_i_migrasjonen`, C2 `test_adapteren_skriver_bare_med_insert`, C3, CR2 og CR3 `test_basen_sjekker_formen`, CR1 `test_replace_erstatter_ikke_en_rad`, CR4 `test_en_feil_rulles_tilbake` | `S/spec-4-3-…` |
| 8.0b | M1–M19 | M12 `test_hjelpen_virker_ogsaa_i_demoen`; resten i tabellen | `S/spec-8-0b-…` |
| 8.0c | 25, i PR #35 og #36 | M7 og M8 `test_merket_staar_paa_samme_x_som_punktet_for_dagen`, M24 `test_noen_mangler_vurdering_gir_begge_setningene`, M25 `test_datoen_skrives_som_dd_mm`; resten i tabellen | `S/spec-8-0c-…` |
| 8.0d | 47, i PR 1, 2, 2b og 3 | testene står per mutant i tabellene i spesifikasjonen | `S/spec-8-0d-…` |
| 8.0e | M1–M8 og P1–P8 | testene står per mutant i tabellene i spesifikasjonen | `S/spec-8-0e-…` |
| 8.3 | M1–M3 og N1–N3 | M1 `test_merkingen_overlever_en_omstart`, M2 `test_filteret_endrer_ikke_rekkefoelgen`, M3 `test_en_post_fra_en_annen_side_gir_403`, N1 `test_alle_er_samme_tabell_ogsaa_naar_ingen_skilte_seg_ut`, N2 `test_oevrige_har_overskriften_naar_bare_de_er_merket`, N3 `test_antallet_teller_bare_merkede_med_en_rad` | `S/spec-8-3-…` |
| 8.15 | S1–S13 og T1–T3 | testene står per mutant i tabellen i spesifikasjonen | `S/spec-8-15-…` |
| 8.15b | M1–M3 og N1–N2 | testene står per mutant i spesifikasjonen | `S/spec-8-15b-…` |
| 8.16 | P1–P4 og Q1–Q4 | testene står per mutant i spesifikasjonen | `S/spec-8-16-…` |
| 8.16b | K1–K3 og N1–N3 | testene står per mutant i spesifikasjonen | `S/spec-8-16b-…` |
| 10.1 | G1–G4 og GR1–GR4 | G1–G4 `test_signalet_gir_bare_fortegn_styrke_og_retning`; resten i tabellen | `S/spec-10-1-…` |
| 10.2a | E1–E6 og ER1–ER6 | testene står per mutant i tabellen i spesifikasjonen | `S/spec-10-2a-…` |
| 10.2b | F1–F5, FR1–FR4, FC1–FC8 og F2b | testene står per mutant i tabellen i spesifikasjonen | `S/spec-10-2b-…` |
| 10.2c | H1–H4 | testene står per mutant i tabellen i spesifikasjonen | `S/spec-10-2c-…` |
| 10.2d | D1–D12 | testene står per mutant i spesifikasjonen | `S/spec-10-2d-…` |
| 10.2e | M1 og M2 24.10, og M1 og M2 i rettingen | M1 `test_dagene_naar_styrken_byttes`, M2 `test_2_tall_og_mengder_som_ikke_er_i_grunnlaget[Femdagssnittet ligger lavere.]`; i rettingen M1 `test_de_tre_tekstene_i_43_som_sa_feil_om_interessen`, M2 av testen for «minst» uten merket, som ble tatt bort i fjerde forsøk | `S/spec-10-2e-…` |
| 10.2e | tredje forsøk, fjerde forsøk M1 og M2, lesingen og ordlyden 25.10 | tredje forsøk `test_dagene_byttet_med_styrken`; M1 `test_en_dag_paa_siden`, M2 `test_dagene_byttet_med_styrken`; lesingen `test_siden_leser_en_gang_per_maaned`; ordlyden `test_setningen[4-False-True-…]` | `S/spec-10-2e-…` og dagsfila 25.10 |
| 10.2f | den gamle grunnen tilbake i prompten, på `6ea0aed` og `3751c95` | `test_grunnen_er_at_siden_sier_hvor_lenge_signalet_har_vart` begge gangene | `S/spec-10-2f-grunnen-i-prompten.md` |
| 10.2g | M1 regelen tatt ut av prompten, M2 sammenligningen med prompten tatt ut av `fra_json`, på `2ded327`/`2e7883d` og `a71a9e7` | M1 `test_retningen_ingen_skrives_som_ingen_retning`, M2 `test_en_rad_med_et_annet_promptavtrykk_avvises`, begge gangene | `S/spec-10-2g-ingen-retning.md` |
| 10.2h | Linja om rekkefølgen tatt ut av prompten, på `34b42d2` og `5261ebf` | `test_ordstillingen_og_rekkefoelgen_staar_i_reglene`, begge gangene | `S/spec-10-2h-ordstilling.md` |
| 10.3 | V1–V4, VR1–VR4 og B1–B7 | testene står per mutant i tabellene i spesifikasjonen | `S/spec-10-3-…` |
| 10.5 | M1–M3 og N1–N3 | M1 `test_hver_av_de_15_har_adressen_fra_svarene`, M2 `test_ingen_mal_lenker_til_euronext`, M3 `test_demoen_viser_teksten_og_ingen_lenke`, N1 og N2 `test_lenken_paa_siden_gaar_til_aksjen_siden_viser`, N3 `test_en_ekte_aksje_uten_adresse_faar_setningen_uten_lenke` | `S/spec-10-5-…` |
| 2.7b | M1–M3 og N1–N10 | M1 og M2 `test_hver_tilstand_ser_ulik_ut`, M3 `test_tallene_for_ukene`, N1–N10 i tabellen i spesifikasjonen | `S/spec-2-7b-…` |
| 10.7 | M1–M3 og N1–N8 | M1 `test_en_valgt_tjeneste_som_feiler_gir_ingen_tekst_fra_en_annen`, M2 `test_kallet_slik_dokumentasjonen_sier`, M3 `test_ikke_i_feilen_eller_grunnen_naar_feilen_har_den`, N1–N8 i tabellen i spesifikasjonen | `S/spec-10-7-…` |
| 10.7b | M1 og M2 | M1 `test_en_valgt_tjeneste_som_feiler_gir_ingen_tekst_fra_en_annen`, M2 `test_noekkelen_mangler`, begge også av `test_ingen_rader_og_ingen_kall` alene | `S/spec-10-7b-…` |
| 3.3i | M1–M3 | M1 `test_ingen_lenke_i_den_ekte_versjonen`, M2 `test_err_connection_refused_under_staar_du_fast`, M3 `test_tallene_20_og_16_stemmer_med_koden`, de nye testene alene (`-k`) | `S/spec-3-3i-…` |
| 3.3j | M1 og M2 | M1 `test_staar_du_fast_har_hoeyst_5_spoersmaal`, M2 `test_svaret_om_mellomrommet_etter_cd`, og `test_begge_meldingene_i_samme_spoersmaal` alene (`-k`) | `S/spec-3-3j-…` |
| 3.4c | M1–M3 | M1 `test_ingen_vurdering_foer_startdagen`, M2 `test_en_rad_per_aksje_hver_boersdag_fra_startdagen`, M3 `test_startdagen`, de nye testene alene (`-k`) | `S/spec-3-4c-…` |
| 2.3c | M1–M3 | M1 og M3 `test_tom_base_foer_22_henter_forrige_boersdag`, M2 `test_base_som_ikke_er_tom_gir_0_kall_foer_22`, `TestFoersteHenting` alene (`-k`) | `S/spec-2-3c-…` |
| 8.6 | M1–M3, N1 og N2 | M1 `test_snittet_er_av_endringen_for_alle_aksjene_i_bransjen`, M2 `test_gult_bare_ved_3_av_3`, M3 `test_rekkefoelgen_er_den_i_designreglene`, N1 `test_en_annen_dag_foelger_gult_siste_boersdag` og `test_uten_kurs_en_annen_dag_har_gult_fra_siste_boersdag` alene (`-k`), N2 `test_hver_rute_lenker_til_aksjesiden` og `test_aksjesiden_uten_kurser_svarer_200_med_beskjed` alene (`-k`) | `S/spec-8-6-…` |
| 8.6b | grensen 0,5 flyttet til 1 (`GRENSE_LYS`) | `test_hvert_trinn_ved_grensene[0.4951-lys-opp]` på `4af6efa`, `6f5815b` og `38cbb3e` | `S/spec-8-6b-…` |
| 8.6b | arealet uten vekten (`squarify([1.0 for r in bransje.ruter], …)` i `_legg_ut`) | `test_arealet_foelger_volumforholdet_i_tabellen` på `4af6efa`, `6f5815b` og `38cbb3e` | `S/spec-8-6b-…` |
| 8.0f | siden gir ikke plass (regelen `.hjelpefelt body:has(.hjelpevindu:popover-open)` tatt ut av `stil.css`) | `test_ingen_tekst_under_feltet[/aksje/BRFE-1280]` på `2889c93` og `8621103` | `S/spec-8-0f-…` |
| 8.0f | Esc lukker ikke (linjen med `Escape` tatt ut av `hjelp.js`) | `test_esc_og_lukk_lukker_og_fokus_gaar_tilbake[Esc]` på `2889c93` og `[Esc-1280]` på `8621103` | `S/spec-8-0f-…` |
| 3.4d | M1–M3, c M1 og c M2 | M1–M3 fanget på `8dcde6d` 22.10 (Utført-linja kl. 21:30), c M1 `test_datoen_i_fotnoten_kommer_fra_startdag` og `test_datoen_paa_sidene_kommer_fra_startdag` alene (`-k`), c M2 `test_demoen_foer_startdagen_har_fotnoten` og `test_den_ekte_versjonen_har_den_ekte_teksten` alene (`-k`) | `S/spec-3-4d-…` |
| 3.4e | M1–M3 | M1 `TestFotnotenIDemoen::test_oversikten_med_en_rad_som_mangler`, M2 `TestVurderingenPaaOversikten::test_ikke_vurdert_med_fotnoten`, M3 `TestFotnotenForInnevaerendeBoersdag::test_fredagen_i_helga[loerdag-/]`, og hver av de nye testene alene (`-k`) | `S/spec-3-4e-…` |
| 3.5a | M1–M3 | M1 `test_skriptene_bruker_kommandoene_i_readme[start.ps1]` og `test_webserveren_binder_bare_127_0_0_1`, M2 `test_noekkelen_og_miljoeet_skrives_aldri_ut[start.sh]`, M3 `test_aldri_debug_eller_down_v[start.ps1]` | `S/spec-3-5a-…` |
| 3.5a | vernet tilbake til «bare fra main» i begge skriptene | `test_den_ekte_versjonen_stopper_i_en_mappe_med_git[start.ps1]`, med `-x` | `S/spec-3-5a-…` |
| 3.5d | sjekken av kommandolinja borte i `start.ps1`, så alt på porten stoppes | `test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten[fremmed]`, med `-x` | `S/spec-3-5d-…` |
| 3.5f | Docker-delen, fra `### Med Docker Desktop` til `### Står du fast?`, tatt ut av `README.md` | `TestCompose::test_porten_er_den_samme_overalt_og_ikke_5000` med `-x` mot tre testfiler, og `TestHovedveien::test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil` med `-k TestHovedveien`, på `b5e4faa` og `a052c74` | `S/spec-3-5f-…` |
| 3.5e | stoppen tilbake før uv i `start.ps1` (`Frigjoer-Porten $true` der porten sjekkes) | `test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten[oss]`, med `-x` | `S/spec-3-5e-…` |
| 8.2a | M1–M5 | M1 `test_periodeknappene_og_velg_dag_gaar_til_kursgrafen`, M2 `test_aksjen_uten_kurser_har_en_rad_nederst_og_ingen_fotnote`, M3 `test_symbolene_over_soeylene_lenker_til_aksjesiden[/]`, M4 `test_raden_sier_hvorfor_med_samme_tall_som_aksjesiden[/]`, M5 `test_sortert_er_hele_lista_en_liste_uten_delene[synkende]` | `S/spec-8-2a-…` |
| 9.1 | Q1–Q4 | Q1, Q3 og Q4 `test_hver_ferdige_spesifikasjon_har_en_rad`, Q2 `test_hver_test_dokumentene_nevner_finnes` | `S/spec-9-1-…` |
| 9.7 | A1–A5 | A1 `test_ruff_check_finner_ingenting`, A2 og A3 `test_ruff_format_er_kjoert`, A4 `test_ci_kjoerer_ruff_foer_testene`, A5 `test_ingen_modul_i_src_bruker_meldinger` | `S/spec-9-7-…` |
| 2.9b | S1–S6 | S1 `test_en_soeyle_per_aksje_med_kurs_fra_stoerst_fall`, S2 `test_antallet_telles_med_en_kortere_liste`, S3 `test_den_stiplede_linja_er_groenn_naar_indeksen_steg_og_roed_naar_den_falt`, S4 og S5 `test_ingen_aksje_med_rad_foer_dagen_navngis_uten_soeyler`, S6 `test_hoeyden_er_paa_endringen_slik_den_vises` | `S/spec-2-9b-…` |
| 2.9c | C1–C6 | C1 `test_linja_starter_paa_aksjens_kurs_og_foelger_indeksen`, C2 `test_startdagen_er_grafens_foerste_dag_ikke_indeksens`, C3 `test_uten_indeks_ingen_linje_og_grafen_sier_det`, C4 `test_uten_grafens_foerste_dag_starter_linja_paa_den_neste`, C5 `test_teksten_sier_hva_linja_er_uten_raad`, C6 `test_hjelpen_for_linja_ogsaa_uten_snitt` | `S/spec-2-9c-…` |
| 9.8 | S1–S8 | S1 `test_ingen_fil_under_agents_er_sporet` og `test_det_finnes_ingen_agents_i_rotmappa`, S2 og S4 `test_manifestet_har_bare_claude_code`, S3 `test_det_finnes_ingen_agents_i_rotmappa`, S5 `test_mappestrukturen_nevner_bmad_og_claude_skills_ikke_agents`, S6 `test_lekkasjesjekken_unntar_ikke_agents`, S7 `test_gitignore_uten_nextjs_men_med_node_og_byggemappene`, S8 `test_env_example_har_variablene_koden_leser_og_kallene_en_henting_bruker` | `S/spec-9-8-…` |

*Lagt til 2026-10-20 (story 2.3, kl. 22):* testene for grensen fikk nye navn da grensen gikk tilbake til kl. 22:00 fra 20.10. I radene «2.3» og «2.3, kl. 21» over er `test_boersdag_kl_20_59_59_gir_0_kall_og_nevner_flagget` nå `test_boersdag_kl_21_59_59_gir_0_kall_og_nevner_flagget`, `test_kl_20_59_i_oslo_i_november_nekter` nå `test_kl_21_59_i_oslo_i_november_nekter`, `test_grensen_er_kl_21` nå `test_grensen_er_kl_22` og `test_kl_21_presis_henter` nå `test_kl_22_presis_henter`. De gamle navnene står i `OMDOEPT` i `tests/test_kvalitetssikring.py`.
