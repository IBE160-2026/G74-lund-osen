- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: «X av M aksjer ble vurdert.» står bare når en rad i tabellen mangler vurdering. Er alle radene vurdert, men én aksje i lista mangler kurser, står ingen slik setning, selv om bare 14 av 15 ble vurdert.
  evidence: BH1, ECH1 og VG3 i gjennomgangen av PR 2b av 8.0d (14.10). Beslutningen 14.10 kl. 21:04 og 21:06 gjelder M i setningen, ikke når den står. Aksjen uten kurser står under tabellen som «Uten data i denne kilden». Testen `test_alle_vurdert_gir_bare_setningen_fra_0510` låser at setningen ikke står når alle radene er vurdert. Avgjøres av gruppen.
  resolved: Løst i PR 3 av 8.0d (14.10, svar 8): setningen står under «Ingen aksjer skilte seg ut» når færre enn alle aksjene i lista ble vurdert, også når en aksje mangler kurser (`test_ble_vurdert_ogsaa_naar_en_aksje_mangler_kurser`).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4a-lesegrensen-kursleser-og-oversetteren.md`
  summary: Tre konsumenter faller fortsatt tilbake fra adjusted_close til close (aksjedetalj.py:106, markedsoversikt.py:99, signalberegning.py:86).
  evidence: Bekreftet med grep 2026-09-24. Fantes foer 1.4a; AD-19 sier at oversettelsen skjer ett sted. Story 1.4b flytter konsumentene til Kursrad, og testene der boer kreve at fallbacken er borte.
  resolved: Loest i story 1.4b (c5efd05, 2026-09-25). De tre konsumentene leser justert_slutt fra Kursrad uten fallback, og tests/test_konsumentene.py feiler hvis fallbacken eller EODHD-noeklene kommer tilbake.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4b-konsumentene-leser-kursrad.md`
  summary: Naar hentet i oeyeblikksbildet ikke kan leses, sier forsiden «Ingen kursdata funnet i data/» selv om dataene finnes. Meldingen er misvisende.
  evidence: Funnet i gjennomgangen av 1.4b (triageloggen, rad 1). SnapshotLeser gjoer da hele oeyeblikksbildet manglende (1.4a), og fotnoten ligger inne i {% if rader %} i index.html. Laast av test_uleselig_hentet_gjoer_hele_oeyeblikksbildet_manglende. Tas naar appen leser fra SQLite (story 2.2, se innledningen til Epic 2 i epics.md), eller foer hvis det blir aktuelt. Rettet 2026-09-25: her sto 1.5, som ikke bytter appen til SQLite.
  resolved: Loest i story 2.2 (2026-10-03). Sidene leser kursene fra basen, ikke oeyeblikksbildet, og den tomme siden sier «Ingen kurser i basen ennå» med kommandoen fra HENTEKOMMANDO i app.py. Meldingen om data/ finnes ikke lenger (test_tom_base_gir_tom_tilstand_med_kommandoen).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4c-rydding-kurskilde-ut-sist-hentet-inn.md`
  summary: Datoen i overskriften paa forsiden er rader[0].dato, altsaa datoen til den oeverste raden etter sorteringen, og den kan motsi sidens eldste tidsstempel naar symbolene har ulike siste datoer.
  evidence: Funnet i gjennomgangen av 1.4c (triageloggen, rad 12). Fantes foer 1.4c i index.html. I et oeyeblikksbilde har alle symbolene samme hentet, saa det synes foerst naar symbolene hentes hver for seg og ett kan feile (AD-15, Epic 2).
  resolved: Loest i story 8.0, merket 2026-10-03 i story 2.2b. Datoen over tabellen er sidens_dato, den eldste datoen blant radene som vises, og ikke rader[0].dato (src/markedsoversikt.py). Holdt av TestSidensDato i tests/test_markedsoversikt.py, som feiler hvis datoen avhenger av sorteringen.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4c-rydding-kurskilde-ut-sist-hentet-inn.md`
  summary: Spoersmaal til UX-gjennomgangen i story 8.2. Med en fersk rad og fjorten foreldede viser de fjorten samme tid som siden, og den ferske viser ingen tid. Er det den merkingen vi vil ha?
  evidence: Funnet i gjennomgangen av 1.4c (triageloggen, rad 4). Oppfoerselen er FR-101 ordrett («En rad med eldre tidsstempel enn det nyeste viser sitt eget»). Leseren ser hvilke rader som er gamle, men ikke naar den ferske ble hentet. FR-101 endres ikke naa.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-snapshotkilde-ut-av-kursdata-py.md`
  summary: Et nyeste oeyeblikksbilde med ugyldig JSON, eller en liste oeverst i stedet for et objekt, gir 500 paa alle sidene i stedet for en beskjed.
  evidence: Funnet i gjennomgangen av 1.5 (triageloggen, rad 1). Fantes foer 1.5: hent_kilde() kalte samme SnapshotKilde.fra_fil, og flyttingen til lagring_fil.py endret ikke oppfoerselen. Det rammer ikke webserveren naar den leser fra basen (2.2).
  resolved: Bortfalt i story 2.2 (2026-10-03). Sidene leser ikke lenger oeyeblikksbildet, saa en oedelagt fil i data/raa/ roerer dem ikke. Kan basen ikke aapnes, svarer sidene 503 med grunnen (test_basen_nyere_enn_koden_gir_503_med_grunnen).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5b-migrasjonsloeperen-og-sqlite-adapteren-herdes.md`
  summary: En test der to migratorer overlapper, som viser at BEGIN IMMEDIATE venter og at den andre ser den foerstes resultat, i stedet for at en av dem feiler.
  evidence: Gjennomgangen av 1.5b del 1 (triageloggen, VG3, BH6, ECH2 og ECH9). Mutanten som bytter BEGIN IMMEDIATE med BEGIN, overlever alle tester. Testene dekker bare luken mellom lesingen og BEGIN. Hoerer til story 3.1, som lager de samtidige kallerne.
  resolved: Loest i story 2.1b (2026-09-29; flyttet fra 3.1 til 2.1b i endringsforslaget 28.09). TestToMigratorerOverlapper i tests/test_migrering.py: to traader, hver med sin tilkobling til samme fil, der den foerste holder transaksjonen aapen inne i migrasjonen til den andre har startet. Begge lykkes, og 0001 kjoeres en gang. Mutanten BEGIN IMMEDIATE -> BEGIN feiler naa testen. Kjoert 50 ganger lokalt: 50 besto.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5b-migrasjonsloeperen-og-sqlite-adapteren-herdes.md`
  summary: migrer() krever skrivetilgang ogsaa naar basen er oppdatert, fordi den starter med BEGIN IMMEDIATE.
  evidence: Gjennomgangen av 1.5b del 1 (triageloggen, ECH1). Ubekreftet, medium hvis det er sant. Avgjoeres naar story 3.1 bestemmer hvem som kaller migrer(), og om webserveren faar en skrivebeskyttet base. Proeves med sqlite3.connect("file:...?mode=ro", uri=True) mot en oppdatert base.
  merknad: 2026-10-03, story 2.2: webserveren kaller naa migrer() en gang per prosess, gjennom aapne_base, og har derfor skrivetilgang til basen. Om imaget skal ha en skrivebeskyttet base, avgjoeres fortsatt i 3.1.
- source_spec: none
  summary: fetch_prices.py kan lekke EODHD-noekkelen naar et kall feiler, fordi feilteksten fra requests tar med hele adressen, med api_token, og den teksten skrives ut (FEIL-linjen) og lagres i feltet feil i oeyeblikksbildet i data/.
  evidence: Funnet ved kontrollen 26.09 (dagsfila, instruksjonen kl. 23:05). hent_ett_symbol sender noekkelen som api_token i params, raise_for_status() kalles, og hent_universet lagrer f"{type(feil).__name__}: {feil}" i resultat.feil og skriver den ut. Ingen lekkasje funnet: 0 treff paa noekkelen i data/ og i 409 commits, og ingen oeyeblikksbilder med ikke-tomt feil. Rettes i en egen liten story foer neste henting: story 2.0 i epics.md (lagt til 2026-09-26). Til da kjoeres ikke fetch_prices.py, og en FEIL-linje fra hentingen limes aldri inn noe sted.
  resolved: Loest i story 2.0 (4b65a3c, 2026-09-26). hent_ett_symbol gjoer enhver feil fra kallet om til en tekst uten adressen og uten response, og hent_universet bytter noekkelen, ogsaa URL-kodet, med *** foer utskrift og lagring. tests/test_fetch_prices.py feiler hvis noekkelen staar i feilteksten, i utskriften eller i det lagrede oeyeblikksbildet. fetch_prices.py kan kjoeres igjen.
- source_spec: none
  summary: test_absolutt_endring_avgjoer_ved_lik_styrke (tests/test_markedsoversikt.py) tester ikke regelen i FR-102 om lik styrke. assert staar inne i en if som aldri slaar til.
  evidence: Kjoert med testdataene 26.09 (kontrollen av repoet, instruksjonen kl. 23:44): styrkene blir DNB 2 og EQNR 1, saa if-en er usann og ingenting sjekkes. Rettes i en egen liten story for testene, sammen med de to under.
  resolved: Loest i story 9.0 (c2c26ba, 2026-09-27). EQNR faller 6 % og DNB stiger 3 %, begge faar styrke 2, og testen krever det med assert, ikke if. Rekkefoelgen skal vaere EQNR foer DNB, som verken fortegn eller navn gir. Testen feiler hvis abs fjernes i _sorteringsnokkel, eller hvis andresorteringen blir paa navn.
- source_spec: none
  summary: test_noeyaktig_paa_grensen_gir_null (tests/test_signalberegning.py) skiller ikke <= fra < i noeytralsonen.
  evidence: Regnet ut 26.09: kurser_med_avvik(0.02) gir et avvik paa 0.019999999999999928, altsaa under grensen, saa baade <= og < gir 0. Rettes i den samme lille storyen for testene.
  resolved: Loest i story 9.0 (c2c26ba, 2026-09-27). Seriene [100]*8 + [98, 102] og [100]*8 + [102, 98] gir snitt 100,0 og avvik noeyaktig +-0,02, og testen feiler hvis <= byttes med < i trend.
- source_spec: none
  summary: test_formatet_kan_leses_av_snapshotkilde (tests/test_fetch_prices.py) lover at visningen kan lese det hentingen skriver, men leser med SnapshotKilde. Visningen leser gjennom SnapshotLeser.
  evidence: Kjoert 26.09: SnapshotLeser paa det samme oeyeblikksbildet gir sist_hentet None og en tom serie, fordi den avviser «naa» som hentet og «dag-000» som dato. Rettes i den samme lille storyen for testene.
  resolved: Loest i story 9.0 (c2c26ba, 2026-09-27). Testen heter naa test_formatet_kan_leses_av_visningen (het test_formatet_kan_leses_av_snapshotkilde). Den skriver fila gjennom kjoer med ISO-datoer og leser den med nyeste_leser og SnapshotLeser, slik visningen gjoer. Den feiler hvis kjoer skriver hentet-tiden uten tidssone.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-6-vurderingslager-med-datoavvisning.md`
  summary: En kjoering som gaar over midnatt i Oslo, faar ValueError fra skriv for resten av symbolene, fordi klokka leses ved hvert kall og datoen er fast for kjoeringen. Symbolene som alt er skrevet, staar, mens resten faar verken vurdering eller grunn.
  evidence: Funnet i gjennomgangen av 1.6 (triageloggen, BH2). Oppfoerselen er AD-7 slik den er vedtatt: en dato som ikke er inneveerende boersdag, avvises. Story 2.5 er kalleren og maa si hva som skjer da, for eksempel at kjoeringen stopper og sier fra, eller at datoen regnes paa nytt og kursen kontrolleres mot den (FR-402).
  resolved: Loest i story 2.5 (2026-10-02). kjoer regner datoen en gang fra oeyeblikket og leser klokka en gang foer vurderingene: er det blitt en ny dag i Oslo, stopper kjoeringen, sier fra og avslutter med kode 1. En ValueError fra skriv midt i universet gir samme melding med antallet som alt er skrevet, uten traceback. Datoen regnes ikke paa nytt. Proevd med mutantene M7, M8a og M8b i spesifikasjonen for 2.5.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-9-aksjene-i-basen-og-tabellene-peker-paa-dem.md`
  summary: docs/innlevering.md (raden «Ligger i» for lagringen, linje 128) nevner bare 0001_kurs.sql, ikke 0002_vurdering.sql og 0003_aksje.sql, og status staar som «oppdatert 2026-09-23».
  evidence: Funnet i gjennomgangen av 1.9 (triageloggen, BH11). Raden manglet 0002 alt foer 1.9, saa den er ikke skapt av storyen. Fila foerer ogsaa tilbakemeldingen fra faglaererne (regel 17), og den oppdateres samlet naar lagringsdelen er koblet til appen.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0-de-rene-feilene-i-de-to-skjermbildene.md`
  summary: Tallene på aksen i kursgrafen har 0 desimaler, så en aksje med smalt kursspenn (for eksempel 1,2–1,5) får like tall på aksen.
  evidence: Funn 15 i gjennomgangen av 8.0. Oppførselen er fra før 8.0 (`"%.0f"` i `aksje.html`), og 8.0 flyttet den bare til slaget `akse` i `tallformat.py`. Kan tas i 8.2 eller når en aksje med lav kurs kommer inn.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: `tests/test_tidssone.py` består uten `tzdata`-pakken på Linux, fordi `zoneinfo` bruker systemets tidssonedatabase først. Spinen sier at `tzdata` er «holdt av» testen, men det gjelder bare der systemdatabasen mangler, som på Windows.
  evidence: K5 i kontrollen 26.09, slått opp på nytt 03.10: står (`tests/test_tidssone.py:20–36`, spinen linje 384). Venter på story 4.0, som tar testoppsettet.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: Nettsperren stopper ikke UDP (`sendto`) eller nettkall fra en underprosess.
  evidence: K11 i kontrollen 26.09, slått opp på nytt 03.10: står (fixturen `ingen_nettverk` i `tests/conftest.py`). Rapporten legger K11 til story 4.0 (linje 443). Venter på 4.0.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: Datoen i filnavnet til øyeblikksbildet er kjøredagen, mens `src/lagring_fil.py` og spinen sier at den er dagen dataene er fra.
  evidence: K8 i kontrollen 26.09, slått opp på nytt 03.10: står (`src/fetch_prices.py:485`, `src/lagring_fil.py:128–130`, spinen linje 364). Story 2.1 endret bare sonen (`27ae8e3`). Venter på 2.3 eller 2.4, som tar forventet børsdag og etterfylling.
  resolved: Løst i story 2.3 (2026-10-08, grenen 2-3). Fila heter etter børsdagen vurderingene skrives for, og filvakten sjekker samme dato. Spinen (raden «Datoer») og docstringen i `nyeste_snapshot` sier det samme. Ingen fil i `data/raa/` har fått nytt navn.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: AD-5 krever minst 175 handelsdager per henting, men ingen story har et kontrollpunkt for det, og hentingen har `MINST_HANDELSDAGER = 51`, med bare en merknad i utskriften.
  evidence: E9 i kontrollen 26.09, slått opp på nytt 03.10: står (`src/fetch_prices.py:73` og :205, spinen linje 184). Venter på 2.3 eller 2.4. *2026-10-08:* 2.3 tar ikke E9 (spesifikasjonen for 2.3, «Never»). Venter på 2.4.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: `Kursrad(volum=2**63)` godtas. `MinneKurslager` lagrer raden, mens `SqliteKurslager` reiser `OverflowError`, ikke `ValueError`, så lagrene oppfører seg ikke likt.
  evidence: K6 i kontrollen 26.09, slått opp på nytt 03.10: står (`src/kursdata.py:112–116`, `src/lagring_sqlite.py:129–136`), og ingen test dekker det. Venter på 3.1.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: `migrer()` og `SqliteKurslager` avviser en tilkobling som er åpnet med `autocommit=False` (Python 3.12 og nyere), med en beskjed som ikke kan følges.
  evidence: K9 i kontrollen 26.09, slått opp på nytt 03.10: står (`src/migrering.py:105–109`, `src/lagring_sqlite.py:106–110`). Venter på 3.1.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: `src/app.py` starter appen med `debug=True`. Et uhåndtert unntak viser Werkzeug-debuggeren med traceback. Det blir en risiko hvis Dockerfilen bruker samme inngang.
  evidence: K10 i kontrollen 26.09, slått opp på nytt 03.10: står (`src/app.py:98`). Venter på Epic 3, der Dockerfilen lages.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: CI kjører ved push til `main` og pull request mot `main`, mens AD-8 i spinen sier «på hver push og PR».
  evidence: K12 i kontrollen 26.09, slått opp på nytt 03.10: står (`.github/workflows/tester.yml:6–10`, spinen linje 210). Tas ved neste endring i CI.
- source_spec: `docs/kontroll-2026-09-26.md`
  summary: `Punkt` og `Rad` importeres uten å brukes i to testfiler, og `SnapshotKilde.tidsstempel`, `SnapshotKilde.serie` og `Detalj.har_ma50` brukes bare av tester.
  evidence: K13 i kontrollen 26.09, delvis rettet før 27.09 (`Path` i `4b65a3c`), slått opp på nytt 03.10: resten står (`tests/test_aksjedetalj.py:9`, `tests/test_markedsoversikt.py:14`, `src/lagring_fil.py:53–57`, `src/aksjedetalj.py`). Tas av neste story som rører de filene.
  merknad: 2026-10-03, story 2.2b: Punkt i tests/test_aksjedetalj.py, Rad i tests/test_markedsoversikt.py og Detalj.har_ma50 er fjernet, og finn_aksje med den. SnapshotKilde.tidsstempel og SnapshotKilde.serie i src/lagring_fil.py staar: 2.2b roerer ikke den fila.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-hentekommandoen-som-egen-inngang.md`
  summary: Den tomme siden viser HENTEKOMMANDO, som er den lokale kommandoen (uv run python src/fetch_prices.py). I en container er kommandoen en annen.
  evidence: Funnet i gjennomgangen av 2.2 (Blind Hunter). Konstanten i app.py og README endres i 3.1, og testen test_kommandoen_paa_den_tomme_siden_staar_i_readme krever at de to er like.
  resolved: Loest i story 3.3 (2026-10-09). Den tomme siden viser HENTEKOMMANDO_DOCKER naar OSE_I_DOCKER=1, som Dockerfile setter, og HENTEKOMMANDO ellers. README har begge, og testen krever det.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-hentekommandoen-som-egen-inngang.md`
  summary: Migreringen i webserveren holder en laas mens den venter paa basen. Feiler migreringen hver gang, for eksempel paa en skrivebeskyttet base, venter hver forespoersel paa tur, opptil 5 sekunder hver.
  evidence: Funnet i gjennomgangen av 2.2 (Blind Hunter og Edge Case Hunter). Det betyr noe for avgjoerelsen i 3.1 om imaget skal ha en skrivebeskyttet base.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-2b-sidene-leser-dagens-vurdering.md`
  summary: Spoersmaal til UX-gjennomgangen i story 8.2. Feiler hentingen for en aksje, eller er det ingen kurs fra dagen, faar dagens rad grunnen, mens siden viser gaarsdagens vurdering med gaarsdagens dato. Skal grunnen ogsaa vises ved siden av den eldre raden?
  evidence: Tillegget i instruksjonen kl. 22:30 03.10. Sidene leser raden for datoen til nyeste kurs (FR-101), og SYMBOL_FEILET og KURS_IKKE_FRA_DAGEN skrives for en dag uten ny kurs. Holdt av test_gaarsdagens_vurdering_naar_dagens_rad_har_grunn i tests/test_app.py og tests/test_oversiktsleser.py.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-2b-sidene-leser-dagens-vurdering.md`
  summary: Sidene bygger forklaringene av maalingene i raden (sjekker_fra) og merket «skiller seg ut» med dagens parametre: noeytralsonen, volumfaktoren og terskelen. Parametrene lagres ikke med raden. For dagens rad er det det samme, men for eldre rader i historikken kan forklaringen motsi fortegnet hvis en parameter endres.
  evidence: Gjennomgangen av 2.2b (Blind Hunter) og raadet 03.10, punkt c. sjekker_fra(vurdering, p) i src/signalberegning.py og skiller_seg_ut i markedsoversikt.bygg_rad bruker p. AD-13 sier at en endret parameter foeres i malinger.md med datoen den gjelder fra, saa en eldre rad kan leses med grensene som gjaldt da. Parametrene er laast i dag, saa ingen side viser det ennaa. Venter paa story 2.7, som viser eldre rader.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md`
  summary: Et symbol som feiler i hentingen, gir kode 0, mens et svar uten kursen for børsdagen (FR-402) gir kode 1. Oppgaveplanlegging ser da en vellykket kjøring for en dag der en aksje mangler.
  evidence: ECH1 i gjennomgangen av 2.3 (08.10). Kode 0 er oppførselen fra main (AD-15, NFR-03). Tas i 2.3b, som gjør nye forsøk for symbolene som feilet.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md`
  summary: En base på nyere skjemaversjon enn koden gir «henter likevel» i basesjekken, og 15 kall som så feiler i basen. Tilstanden er kjent før første kall.
  evidence: ECH3 i gjennomgangen av 2.3 (08.10). `_krev_siste_versjon` reiser `RuntimeError` både for nyere og eldre versjon, så skillet må gjøres i porten. Venter på en egen retting.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md`
  summary: En `dato` i `kurs` som ikke kan leses, gir `ValueError` i `manglende_i_basen` og traceback før første kall.
  evidence: ECH4 i gjennomgangen av 2.3 (08.10). Bare en endring for hånd i basen gir det.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md`
  summary: Stopper vurderingene ved midnatt eller fordi basen feiler, nevner ikke utskriften aksjene uten kursen for børsdagen (FR-402).
  evidence: ECH7 i gjennomgangen av 2.3 (08.10). Fila står og viser det.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md`
  summary: Har basen kursene for børsdagen, men vurderingene for dagen mangler, sier kommandoen «Ingenting aa hente» med kode 0.
  evidence: ECH8 i gjennomgangen av 2.3 (08.10). Ingen regresjon: filvakten ville stoppet kjøringen uansett. Tas i 2.3b.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-dockerfile-med-to-innganger.md`
  summary: `docker compose run --rm hent --hent-foer-kl-22` erstatter `command` i stedet for å legge flagget til, så flagget må gis med hele kommandoen (`docker compose run --rm hent python src/fetch_prices.py --hent-foer-kl-22`).
  evidence: ECH7 i gjennomgangen av 3.1 (08.10). Tas i 3.3, der README viser kommandoene. Et `entrypoint` for `hent` er det andre valget.
  resolved: Loest i story 3.3 (2026-10-09). `hent` har `entrypoint` og ingen `command`, så flagget legges til.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-2-to-volumer-og-ingenting-uerstattelig-i-imaget.md`
  summary: README-en sier at `docker compose down -v` fjerner begge volumene, også øyeblikksbildene i `ose-raa` og vurderingene i `ose-db`, og at man stopper med `docker compose down` uten `-v`. Den sier også at basen ikke kan slettes og bygges opp igjen, fordi `vurdering` ikke kan lages på nytt (`AD-7`, `AD-11`).
  evidence: Svar 3 fra gruppen 09.10 kl. 20:46. Advarselen står i `compose.yaml`, og README-teksten tas i 3.3, som ECH7 fra 3.1.
  resolved: Loest i story 3.3 (2026-10-09). «Kom i gang» sier at volumene står når containerne stoppes, at man aldri bruker `docker compose down -v`, og at basen ikke kan slettes og bygges opp igjen.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-3-readme-slik-kjoerer-du-den.md`
  summary: Når basen ikke kan skrives, sier hentingen at fila kan leses inn med `uv run python src/fetch_prices.py --les-inn <fil>`, også i containeren. I Docker er kommandoen `docker compose run --rm hent --les-inn <fil>`, med stien i containeren.
  evidence: VG1 i gjennomgangen av 3.3 (09.10). `_basen_feilet` i `src/fetch_prices.py` har kommandoen fast, og `src/fetch_prices.py` endres ikke i 3.3. Rettes med `OSE_I_DOCKER` som på den tomme siden, og en test i `tests/test_fetch_prices.py`.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md`
  summary: Med ekte data gjør en aksje uten kurs siste dag datoen over tabellen til dagen før for hele siden, og ingen rad viser hvilken aksje som henger etter.
  evidence: Funnet med Tareøy Havbruk i 3.4 (Spec Change Log, 10.10). Oversikten viser vurderingen for dagen til nyeste kurs for hver aksje, og datoen over tabellen er den eldste av dem (story 8.0). Demoen viser derfor ikke «ingen kurs fra dagen», etter gruppens beslutning i instruksjonen kl. 14:46 10.10. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md`
  summary: To kjøringer av demokommandoen samtidig, for eksempel `docker compose run --rm demo-lag` mens en `docker compose up demo` kjører `demo-lag`, bruker samme midlertidige fil `demo.db.ny`. Den ene kan bytte inn en halvferdig base med merket.
  evidence: ECH2 i gjennomgangen av 3.4 PR 2 (10.10). `lag_demobase` i `src/demo.py` sletter `demo.db.ny` før den bygger, og bytter den inn med `os.replace`. Én kjøring av gangen er prøvd i CI. Rettes med et eget navn per prosess eller en låsefil. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md`
  summary: Ligger det en fil som ikke kan leses, som `demo.db` i volumet `ose-demo`, nekter `demo-lag`, og `docker compose up --build demo` stopper. Siden viser `docker compose run --rm demo-lag`, som nekter igjen, og README-en sier ikke hva man da gjør.
  evidence: ECH3 i gjennomgangen av 3.4 PR 2 (10.10). Demokommandoen nekter en fil uten merket, og en fil som ikke kan leses, regnes ikke som demobase (gruppens beslutning 10.10, PR 1). Om `demo-lag` skal få skrive over en slik fil i `ose-demo`, der det bare ligger demodata, eller README-en skal vise hvordan volumet fjernes, er gruppens valg. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md`
  summary: I demoen står «Oslo Børs · 2026-10-09 · 14 aksjer» over tabellen, rett under «Eksempeltall: oppdiktede selskaper og kurser, ikke data fra Oslo Børs.» Spørsmål til gruppen: skal linjen si «Eksempeltall» i stedet for «Oslo Børs» når basen har demomerket?
  evidence: Gruppens instruksjon kl. 17:35 10.10, etter PR #27. Linjen kommer fra `src/templates/index.html:67`, og merknaden fra linje 61 i samme mal. `test_bryteren_med_demobase_viser_eksempeltall` i `tests/test_demo.py` krever teksten «Oslo Børs · 2026-10-09 · 14 aksjer» i dag. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3b-kallene-som-er-igjen-brukes-paa-nye-forsoek.md`
  summary: To nye forsøk som starter samtidig, leser samme tall fra `/api/user` og kan til sammen bruke flere kall enn marginen. Leser begge 19 brukt før sitt siste kall, kan det ene kallet tas fra bonuskvoten før stoppen slår inn.
  evidence: ECH3 i gjennomgangen av 2.3b (10.10). Forsøket leser `/api/user` etter hvert kall og stopper når `apiRequests` når grensen eller `extraLimit` synker (`e245619`), men det er ingen lås mellom to kjøringer. Oppgaveplanlegging kjører én gang hver halvtime, så det krever en kjøring for hånd samtidig. Rettes med en låsefil i `data/raa/` rundt forsøket. Ikke rettet nå; hører naturlig til steget med Oppgaveplanlegging.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0b-hjelp-bak-et-spoersmaalstegn.md`
  summary: Fotnotene under tabellene bruker ordene svar 3 11.10 tok ut av hjelpen. `index.html` sier at signalstyrken «sier hvor kraftig de tre sjekkene slår ut — ikke om aksjen bør kjøpes eller selges», og `aksje.html` at den «er summen av tallene uten fortegn». Hjelpen ved siden av sier at styrken teller sjekkene som ga +1 eller -1.
  evidence: Funn 23 i gjennomgangen av 8.0b (VG, 11.10). Linjene fantes før 8.0b, og instruksjonen ba ikke om å endre dem. Om fotnotene skal si det samme som hjelpen, eller tas ut fordi hjelpen nå forklarer styrken, er gruppens valg, for eksempel i 8.0c. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md`
  summary: Når hovedindeksen hentes i samme kjøring (story 2.8), bruker en henting 16 kall. Da må «Hvorfor bare 15 aksjer?» og «en henting bruker 15» i «Hva med nøkkelen?» i docs/hjelp.md ses på igjen, og test_hvorfor_bare_15_aksjer følge.
  evidence: VG2 i gjennomgangen av PR #31 (12.10). NFR-01 i PRD-en: daglig henting koster 16 kall når indeksen hentes, og avsnittet med 15 gjelder til story 2.8 er bygget. Testen henter bare antallet aksjer fra AKSJEUNIVERS, ikke kallet for indeksen.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3b-kallene-som-er-igjen-brukes-paa-nye-forsoek.md`
  summary: Har kveldens henting skrevet kursfila, men skrivingen til basen feilet, og basen kan leses ved neste kjøring, går samme kommando til et nytt forsøk. Det bruker inntil 5 kall på aksjer som allerede står i kveldens fil, og resten mangler fortsatt. `--les-inn <fil>` hadde lest alle inn med 0 kall.
  evidence: Rådet leste `kjoer` og `nytt_forsoek` 10.10: filvakten sender til `nytt_forsoek` når fila finnes og basen mangler dagens kurs, uten å se i fila. Funnet skulle føres ved flettingen av PR #28 12.10, men kom ikke med i blokka. Meldingen ved basefeil viser `--les-inn`, men hjelpen under «Når kan jeg hente?» sier at samme kommando kan kjøres igjen. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md`
  summary: «?» står inne i `<th>` og `<h2>`, så skjermleseren leser overskriften som for eksempel «Sluttkurs Hjelp: sluttkurs» ved hver celle i kolonnen.
  evidence: BH4 i gjennomgangen av PR #35 (13.10). Mulige løsninger: `aria-labelledby` på overskriften, eller knappen utenfor `<h2>` i en flex-rad. Hører til 8.0d (fokus og utseende). Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md`
  summary: Teksten om «Uten data i denne kilden» står bare i vinduet ved «data hentet», og det vinduet finnes bare når `hentet` har en verdi. Fotnoten kan stå uten at teksten finnes på siden.
  evidence: BH5 og ECH8 i gjennomgangen av PR #35 (13.10). Delen 2 av hjelpen ble godkjent med teksten i det vinduet. Et eget «?» ved fotnoten er et valg for gruppen. Ikke rettet nå.
  resolved: Bortfalt 2026-10-24 i story 8.2a (b, gruppens svar kl. 11:34 og 11:35): fotnoten «Uten data i denne kilden» er borte, og en aksje uten kurser har en rad nederst i tabellen med «uten data». Teksten i vinduet ved «Oppdatert» heter nå «Uten data:» (`spec-8-2a-funn-fra-proeven-av-demoen.md`, BH14 i gjennomgangen 24.10).
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md`
  summary: Ga sier «0 ingen utslag» en dag volumet var over 1,5 ganger medianen og kursen var uendret, mens hjelpen for interesse sier «Slår ut over 1,5 ganger medianen».
  evidence: ECH1 i gjennomgangen av PR #35 (13.10). Sjekken gir 0 og teller ikke i styrken (`signalberegning.py`, `interesse`), så «ingen utslag» stemmer med styrken. Hjelpen kan presiseres. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md`
  summary: 404-siden er Flasks standardside på engelsk, uten merket i demoen og uten linja «Appen er under utvikling og ikke ferdig.»
  evidence: ECH9 i gjennomgangen av PR #35 (13.10). Svar 4 sier linja nederst på alle sidene. En `errorhandler(404)` med en egen mal er ny funksjonalitet. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md`
  summary: Kursgrafen får ikke månedsmerker for måneder utenfor børskalenderen. Den dekker bare 2026 (`boersdag.DEKKEDE_AAR`), så fra januar 2027 mangler merket for inneværende måned.
  evidence: BH3, BH4 og ECH4 i gjennomgangen av PR #36 (13.10). Beslutning 13 sier «etter `er_boersdag`». Rettes når stengte dager for 2027 føres inn (kommentaren i `boersdag.py`), eller med første punkt i måneden som merke. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md`
  summary: Månedsmerkene kan overlappe når et langt hull gjør to måneder til naboer i serien, og navnene står uten år når serien går over et årsskifte.
  evidence: ECH3 og BH6 i gjennomgangen av PR #36 (13.10). Kan tas i 8.0d sammen med utseendet. Ikke rettet nå.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: Oversikten og aksjesiden viser tidspunktet to ganger, som «Oppdatert …» i stripa og som «data hentet …» i linja under tittelen.
  evidence: BH2 i gjennomgangen av PR 1 av 8.0d (14.10). Stripa kom i PR 1, og linja under tittelen hører til oversikten og aksjesiden, som er PR 2 og PR 3. Hjelpen bak «?» ved «data hentet» står i den linja, så den må flyttes med hvis linja tas bort. Avgjøres i planen for PR 2.
  resolved: Oversikten er løst i PR 2 av 8.0d (14.10): tidspunktet står bare som «Oppdatert …» i stripa, med «?» ved siden av (svar 5). Aksjesiden er løst i PR 3 av 8.0d (14.10): «data hentet» er borte fra linja under h1, og hjelpen `data_hentet_aksje` står bak «?» ved «Oppdatert» i stripa.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: Båndet «Øvrige aksjer» sier «signalstyrke 0 eller 1», men rader uten vurdering («Ikke vurdert» eller en grunn) står også der og telles i pillen. Strekene og båndteksten forutsetter terskel 2: med en annen terskel følger strekene «Skilte seg ut» og ikke nivået, og ingenting holder terskelen mellom 1 og 3.
  evidence: BH2, ECH1, ECH2 og ECH3 i gjennomgangen av PR 2 av 8.0d (14.10). Ordlyden i båndet er gruppens beslutning (instruksjonen kl. 17:31), så en endring avgjøres av gruppen. Terskelen er 2 i Parametre i dag. Grensene i båndene følger terskelen (testen med terskel 3).
  resolved: Ordlyden er løst i PR 3 av 8.0d (14.10, svar 7): båndet sier «og N uten signal» etter grensen når rader uten signal står der, og pillen teller alle radene. Strekene og terskelen står som før.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: Endringskortet på aksjesiden sier bare ukedagene («fra fredag til fredag») når de to siste kursradene ligger 7 dager eller mer fra hverandre, så det ser ut som én børsdag. Det skjer når kilden mangler kurser for en uke, for eksempel når aksjen er suspendert.
  evidence: BH6 og ECH2 i gjennomgangen 15.10 av PR 3 av 8.0d. Svar 21 (14.10 kl. 22:50) sier ukedagene, med datoen under h1. Hentingen leser 364 dager hver gang (`DAGER_TILBAKE` i `src/fetch_prices.py`), så et hull kommer fra kilden. En retting endrer teksten på siden og avgjøres av gruppen.
  resolved: Løst i PR 3 av 8.0d (15.10, gruppens svar kl. 12:15, svar 29, `07b4ff6`): ligger det en børsdag mellom de to kursradene (`boersdag_mellom` i `src/aksjedetalj.py`), står datoene ved ukedagene, som «fra fredag 02.10 til fredag 09.10». Ellers ukedagene som før, og med `UtenforKalenderen` står datoene (`test_endringen_med_datoene_naar_en_boersdag_ligger_mellom` og `test_endringen_med_datoene_naar_kalenderen_ikke_dekker_dagene`).
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: Aksjesiden leser aksjen og vurderingen (`post`) og serien (`leser.serie`) i to lesinger. Skriver kveldshentingen mellom dem, kan endringen og «fra … til …» gjelde en annen dag enn sluttkursen og datoen på siden.
  evidence: ECH1 i gjennomgangen 15.10 av PR 3 av 8.0d. Grafen leser serien slik også på main (`punkter=bygg_punkter(rader, p)`), og PR 3 regner også endringen av den (`bygg_detalj` i `src/aksjedetalj.py`, ruten i `src/app.py`). Luken er mellom to lesinger i samme forespørsel, og neste visning er riktig. Rettingen er i koden, ikke i tester eller dokumenter, og hører ikke til denne instruksjonen.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: Stilen for brikkene står i rammen siden PR 3 av 8.0d og gjelder `.brikke` på alle sidene. Symbolet «T +1» i kortet «Slik leser du tabellen» har samme klasse og arver nå `min-width: 34px`, `height: 24px`, `inline-flex` og en gjennomsiktig kant.
  evidence: BH20 i gjennomgangen 15.10 av PR 3 av 8.0d. Regelen `.symbolfelt .brikke` i `src/templates/index.html` er fra PR 2, og planen for PR 3 nevner ikke kortet. En retting endrer det som vises, og avgjøres av gruppen.
  resolved: Løst i PR 3 av 8.0d (15.10, gruppens svar kl. 12:15, svar 28, `138ef80`): feltet ved Signalstyrke viser en grønn +1 over en rød -1 i klassen `utslagsfelt`, uten klassen `brikke`, og teksten har de to setningene om +1 og -1 (`test_symbolene_i_kortet_er_skjult_og_ingen_pil_ved_navnet` og `test_slik_leser_du_tabellen_har_3_punkter`).
- source_spec: `_bmad-output/implementation-artifacts/spec-8-0d-utseendet-fra-designforslaget.md`
  summary: Grensene over skalaen for bevegelse vises med én desimal (`bygg_skala` i `src/aksjedetalj.py`), så et standardavvik under 0,05 % står som «-0,0 %» og «+0,0 %», mens tallet i kortet har så mange desimaler som trengs (`desimaler_mot_grense`).
  evidence: ECH3 i gjennomgangen 15.10 av PR 3 av 8.0d. En retting endrer teksten på siden og avgjøres av gruppen.
  resolved: Løst i PR 3 av 8.0d (15.10, gruppens svar kl. 12:15, svar 30, `70d47f6`): grensene over skalaen og standardavviket i teksten får desimalene fra `bevegelsesdesimaler` i `src/signalberegning.py`, så de viser samme tall, og en grense over 0 vises aldri som 0,0 (`desimaler_uten_null` i `src/tallformat.py`, høyst `MEST_DESIMALER`). Testene: `test_grensene_for_bevegelse_er_tallet_i_teksten` i `tests/test_aksjedetalj.py` og `tests/test_app.py`, og `TestDesimalerUtenNull`.
- source_spec: `_bmad-output/implementation-artifacts/spec-8-15-sortering-ved-klikk-i-kolonneraden.md`
  summary: Lenkene i kolonneraden bygger adressen som `/?sorter=…&orden=…` og tar ikke med andre parametre. Når perioden eller «Velg dag» kommer i adressen (8.17), nullstiller et klikk på en kolonne dem, og «Standard rekkefølge» går til /.
  evidence: BH4 i gjennomgangen 15.10 av 8.15. I dag har oversikten ingen andre parametre, og `test_hver_lenke_gaar_til_en_side_som_finnes` godtar bare `/?sorter=…&orden=…`. Tas når 8.17 bygges: lenkene må ta med de andre parametrene.
- source_spec: `_bmad-output/implementation-artifacts/spec-4-0-nettsperren-dekker-hele-testkjoeringen.md`
  summary: Nettsperren gjelder prosessen pytest kjører i. En underprosess som en test starter (`subprocess`, eller `multiprocessing`, som starter nye prosesser på Windows), får den ikke.
  evidence: BH7 og ECH i gjennomgangen 15.10 av 4.0. Den eneste testen som starter en underprosess i dag, `test_stiene_er_data_raa_og_data_db_ose_db` i `tests/test_lagring_sqlite.py`, leser to konstanter og bruker ikke nett. Grensen står i docstringen i `tests/conftest.py`. Tas når en test skal starte en underprosess som kan bruke nett, for eksempel med en `sitecustomize` som setter sperren i barneprosessen.
- source_spec: `_bmad-output/implementation-artifacts/spec-4-2-kilogg-porten-med-minneimplementasjon.md`
  summary: Passerer hentingen midnatt i Oslo mellom modellkallet og `skriv`, gir `skriv` `IkkeInnevaerendeBoersdag` for resten av radene den kvelden.
  evidence: ECH i gjennomgangen 15.10 av 4.2. Porten reiser en egen type for feil dag, så kalleren kan skille den fra en feil i klokka eller kalenderen. Tas i 10.2b (PR F): hentekommandoen må fange den per rad og la hentingen gå videre (NFR-04).
  resolved: Løst i 10.2b (PR F, `5dd8a00`): `lag_ki_tekster` sjekker børsdagen før hvert kall og fanger `IkkeInnevaerendeBoersdag`, og steget stopper med beskjed uten å endre utgangskoden (`test_midnatt_stopper_steget_med_beskjed`, `test_modellen_kalles_ikke_etter_midnatt`).
- source_spec: `_bmad-output/implementation-artifacts/spec-4-3-sqlite-adapter-for-kilogg.md`
  summary: `SqliteKILogg.skriv` styrer sin egen transaksjon og avviser kallerens, så en rad i `ki_logg` kan ikke skrives i samme transaksjon som vurderingen den forklarer.
  evidence: BH10 i gjennomgangen 15.10 av 4.3. Vurderingen skrives før modellen kalles (10.2), og FR-602 viser bare en KI-tekst når grunnlaget stemmer med vurderingen. Tas i 10.2b (PR F): om rekkefølgen skal være vurdering, så KI-rad, hver for seg, og hva som skjer når kjøringen stopper mellom dem.
  resolved: Løst i 10.2b (PR F, `9bc8b3b` og `5dd8a00`): rekkefølgen er vurdering, så KI-rad, hver i sin transaksjon. Stopper kjøringen mellom dem, lager samme kommando radene som mangler, med 0 kall til EODHD når basen har kursene, og før et nytt forsøk ellers (`test_radene_som_mangler_lages_med_null_kall_til_eodhd`, `test_ki_radene_som_mangler_lages_foer_et_nytt_forsoek`).
- source_spec: `_bmad-output/implementation-artifacts/spec-4-3-sqlite-adapter-for-kilogg.md`
  summary: Emnet for en melding (plan A) har datoen i nøkkelen, så samme melding kan få én rad per dag.
  evidence: BH8 i gjennomgangen 15.10 av 4.3. Story 4.2 sier at hva plan A lagrer, avgjøres når plan A bygges. Plan A er utenfor v1.
- source_spec: `_bmad-output/implementation-artifacts/spec-10-2a-modellen-prompten-og-kontrollen.md`
  summary: Kontrollen i FR-603 ser ikke på lengden, språket eller om en tekst for en aksje utenfor målingen sier at grensene ikke er målt på den, selv om prompten ber om to eller tre setninger på norsk og den setningen.
  evidence: BH16 i gjennomgangen 15.10 av PR E. FR-603 har fire punkter, og ingen av dem gjelder dette. Tas når 10.2b (PR F) gir de første ekte tekstene, eller i 10.4: om det trengs et femte punkt, avgjøres av gruppen.
- source_spec: `_bmad-output/implementation-artifacts/spec-10-2c-prompten-versjon-2.md`
  summary: Kontrollen i FR-603 fanger ikke en gjettet årsak etter «fordi». «Kursen steg fordi markedet var urolig.» består (prøvd 16.10). Kontrollen strammes inn: et «fordi»-ledd må nevne en av sjekkene, ellers stoppes teksten.
  evidence: ECH og BH1 i gjennomgangen 16.10 av PR H (10.2c). Ingen av de 15 tekstene i `malinger.md` §34 gjør det. Gruppens beslutning 16.10 kl. 23:51 (under story 10.2 i `epics.md`): en liten PR neste uke.
