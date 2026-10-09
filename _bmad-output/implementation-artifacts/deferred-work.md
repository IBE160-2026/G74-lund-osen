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
