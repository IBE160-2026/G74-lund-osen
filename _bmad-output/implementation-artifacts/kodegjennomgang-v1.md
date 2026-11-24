---
title: "Kodegjennomgang av v1"
status: aktiv
created: 2026-11-24
updated: 2026-11-24T21:58
---

# Kodegjennomgang av v1

Punkt 22 i `prd.md` §8, og instruksjonen kl. 13:02 i `docs/ai-prompts/2026-11-24.md`, steg 4, med beskjeden kl. 14:31: gjennomgangen går på main etter story 2.22. Den har samme form som `kodegjennomgang-epic-1.md`, men leser koden slik den står, ikke en diff: `src/` og `start/` på commiten `3f965546` (main 24.11 kl. 16:25, etter 2.22), 56 moduler og 22 511 linjer i `src/*.py`, 24 maler, 15 migrasjoner og 1 445 linjer i `start/`.

Denne runden finner og sorterer bare. **Ingen kode er endret.** Funnene på middels og høy grad er forslag til storyer etter brukertest 2. Story 3.4 står i review til gruppen har svart, så funnene i demoen og investorsidene er merket «3.4» og tas med der.

## Slik ble koden delt

- **Del A, lagringen og lista:** `migrering.py`, `migrasjoner/0001–0015`, `lagring_sqlite.py`, `lagring_fil.py`, `kursdata.py`, `vurderingsdata.py`, `indeksdata.py`, `kilogg.py`, `kilogg_minne.py`, `tilstand.py`, `minliste.py`, `notater.py`, `innstillinger.py`, `boersdag.py`, `valg.py` og `ferdige_lister.py`.
- **Del B, hentingen, signalet og skriptene:** `fetch_prices.py`, `eodhd.py`, `omsetning.py`, `omsetningsregning.py`, `dagen_ferdig.py`, `ettertid.py`, `signalberegning.py`, `justeringsdager.py`, `meldinger.py`, hele `start/`, startfilene i rotmappa, `Dockerfile` og `compose.yaml`.
- **Del C, sidene:** `app.py`, malene, `static/hjelp.js`, `markedsoversikt.py`, `aksjedetalj.py`, `boersometer.py`, `graf.py`, `historikk.py`, `perioder.py`, `dagene.py`, `hovedindeks.py`, `oversiktsdata.py`, `tallformat.py`, `hjelpetekster.py`, `etterpaa.py`, `moenstrene.py`, `dagsgrunnlag.py`, `ikon.py` og `investorsider.py`.
- **Del D, KI-teksten og demoen:** `ki_*.py`, `demo.py`, `demo_ki.py` og JSON-filene de leser.

Hver del fikk én leser med fire roller: Blind Hunter (BH), bare koden i delen, Edge Case Hunter (ECH) og Verification Gap (VG), med tilgang til repoet, og Acceptance Auditor (AA) mot `prd.md`, `ARCHITECTURE-SPINE.md` og `epics.md`. Radene har prefikset A-, B-, C- eller D- for delen. Ingen leser feilet. Hver leser fikk føre høyst seks funn per rolle og sa hvor mange mindre den lot ligge: til sammen 34.

Leserne leste bare. De kjørte verken pytest eller prosjektkode, så «overlever» under VG er lest ut av testene, ikke prøvd. Hvert funn er slått opp i koden av leseren, og sjekket mot `deferred-work.md`, spesifikasjonene og `.logs/marian-osen/issues.md`: «kjent» betyr at funnet står der fra før. De to funnene på høy grad er i tillegg prøvd etterpå mot `ki_kontroll.kontroller`, med den gode teksten fra `tests/test_ki_modell.py` og én setning lagt til: alle sju setningene i D-BH1 og D-BH2 besto kontrollen. Ingen andre funn er prøvd av andre enn leseren.

Hva leserne ikke rakk å lese helt, står nederst.

## Sammendrag

79 funn fra fire lesere: 2 på høy grad, 19 på middels og 58 lave. 21 er kjent eller delvis kjent fra før. De 21 på middels og høy er samlet i 14 grupper, sortert etter alvor:

| Gruppe | Del | Sak | Grad | Funn | Kjent | Forslag |
|---|---|---|---|---|---|---|
| G1 | KI-teksten | Oppdiktede tall og mengder består kontrollen for én aksje: de faste tallene 2, 3, 20 og 50 er lov hvor som helst, og «doblet», «øre» og «million» fanges ikke. Siden viser tallet med prikket strek, som om det var prøvd | høy | D-BH1 | nytt | egen story etter brukertest 2 |
| G2 | KI-teksten | Et råd uten ord fra listene består både kontrollen og vakta på siden, også på engelsk. Kontrollen for én aksje er en ordliste. Visningen bruker bare den korte vakta, så rader som besto før 11.11, vises fortsatt. Flere ord i listene har ingen test | høy | D-BH2, D-AA3, D-VG1 | kjent: `prd.md` («Kontrollen er grov», åpent punkt 27), `deferred-work.md` | egen story etter brukertest 2, sammen med G1 |
| G3 | sidene | «Børsdagen kort fortalt» på en valgt dag regnes av lista i dag, ikke lista den dagen. Etter et bytte i lista faller teksten bort for dagene før byttet (FR-607). Ingen test har en valgt dag med endret liste | middels | C-ECH1, C-AA1, C-VG3 | nytt (2.11 ECH5 rettet det samme på aksjesiden) | egen story |
| G4 | sidene | Stjernen på en aksje som er tatt ut, gir 400 med Werkzeugs engelske side, fra en vanlig knapp i «Vis dagen» | middels | C-ECH2 | nytt | egen story, sammen med G3 |
| G5 | hentingen | `--les-inn` avviser egne aksjer, fordi innlesingen bruker de 15 og ikke lista i basen. Rådet «Les den inn uten kall» virker ikke for dem, og ingen test leser inn en egen aksje | middels | B-BH1, B-VG2 | nytt | egen story |
| G6 | hentingen | Et delvis svar fra EODHD med dagens rad erstatter et helt år med kurser. Kravet om minst 175 børsdager (FR-406, AD-5) har ingen kontroll | middels | B-ECH1 | kjent: `deferred-work.md` | egen story |
| G7 | hentingen | Lista over Oslo Børs kommer bare inn med `--les-boerslista` fra en fil som ikke er i repoet. I en ZIP-kopi eller i Docker kan en bruker ikke følge en aksje (FR-412, FR-415) | middels | B-AA1 | delvis kjent: `spec-2-12` | spørsmål til gruppen |
| G8 | hentingen | Ingen test fanger det hvis et nytt forsøk slutter å stoppe når dagens kall er brukt underveis, så neste kall går fra bonuskvoten (NFR-01) | middels | B-VG1 | nytt | egen story, bare test |
| G9 | lista | FR-412 sier at en ticker som ikke gir rader, ikke tas inn. Koden tar den inn før hentingen og tar den ut kvelden etter, og den bruker en av de 18 plassene imens | middels | A-AA1 | kjent: `spec-2-12` (VG7); 9.28 og 2.21 bygger på det | rett ordlyden i `prd.md`, eller egen story |
| G10 | lista | Ingen test tar et bytte i bruk med full liste. Rekkefølgen «fjern før følg» i `ta_i_bruk` kan fjernes uten at en test feiler | middels | A-VG1 | nytt | egen story, bare test |
| G11 | KI-teksten | Ett tomt svar, ett avslag eller en feil nøkkel regnes som at modellen feilet. Da kalles den ikke for resten av aksjene eller for dagen, og radene står, så hele børsdagen blir uten KI-tekst | middels | D-ECH1, D-ECH2 | delvis kjent: `spec-10-2b`, `spec-10-7b` | spørsmål til gruppen |
| G12 | KI-teksten | Hentingen sender aldri merket «Utenfor målingen». Etter 2.12 kan lista ha egne aksjer, og KI-teksten for dem sier ikke at grensene ikke er målt på aksjen (story 10.1). Ingen test kjører hentingen med en slik aksje | middels | D-AA1, D-VG3 | delvis kjent: `spec-3-4b` (avvist før lista kunne byttes) | egen story |
| G13 | KI-teksten | `docs/kilder-og-rettigheter.md`, «Hva som sendes», nevner ikke at prompten for dagen sender selskapsnavn og bransjenavn, også til skytjenestene. Avgjørelsen står i `epics.md` og `prd.md` | middels | D-AA2 | nytt | gruppen fører det selv |
| G14 | KI-teksten | Tidsfristen på 10 s for sjekken av Ollama og oppslagene etter hver tekst er ikke låst av en test. En Ollama som henger, kunne stoppet hentingen (NFR-04) | middels | D-VG2 | nytt | egen story, bare test |
| — | | Lave funn (se tabellene) | lav | 58 funn | 13 kjent eller delvis kjent | vurderes etter brukertest 2 |

## Del A: lagringen og lista

20 funn: 2 på middels og 18 lave. Leseren lot 15 mindre ligge. Alle 16 filene og de 15 migrasjonene er lest i sin helhet.

| Id | Grad | Funnet | Kjent |
|---|---|---|---|
| A-BH1 | lav | `Valglager._laas` committer stille en åpen transaksjon hos kalleren (`valg.py:243-244`), mens adapterne i `lagring_sqlite.py` reiser `RuntimeError` | nytt |
| A-BH2 | lav | `sqlite3.Error` svelges og gir «alt på» eller tomt svar i `innstillinger._rader`, fire funksjoner i `ferdige_lister.py` og `valg.har_tabellene`. En låst base gir hjelp og KI-tekst på selv om de er slått av | nytt |
| A-BH3 | lav | Docstringer som ikke stemmer: «Bare oenske skrives» i `valg.py`, «skriver bare denne tabellen» for to lagre, og «webserveren skal gjoere det samme» | nytt |
| A-BH4 | lav | Kode bare testene bruker: `nyeste_snapshot`, `nyeste_leser`, `SnapshotKilde.tidsstempel`, `Valglager.sok` og `SqliteEttertidslager.antall` | nytt |
| A-BH5 | lav | `ta_i_bruk` sjekker ikke `rowcount`. Et ønske om å følge en aksje som alt står i lista, gjør den til «Egen». Bare mulig utenom `Valglager.folg` | nytt |
| A-ECH1 | lav | `ta_i_bruk` og `uten_rader` leser ønskene før transaksjonen begynner. Et «Angre» i de millisekundene tar aksjen inn uten ønskerad. Ikke prøvd | nytt |
| A-ECH2 | lav | `_Transaksjon` bruker utsatt `BEGIN`. Committer hentingen samtidig, kan brukeren få 503 og miste notatteksten. Antatt etter SQLites dokumentasjon, ikke prøvd | nytt |
| A-ECH3 | lav | En stjerne overlever at aksjen tas ut, og er der igjen når aksjen kommer tilbake | delvis kjent: `spec-8-26` |
| A-ECH4 | lav | På en base én versjon bak gir `dagen_ferdig.py` alltid kode 2, fordi to adaptere krever siste versjon. Det feiler trygt | nytt |
| A-ECH5 | lav | En aksje med kurser som tas inn igjen, leses som i lista også de dagene den var ute | kjent: `spec-2-12`, `spec-2-21`, avgjort 08.11 |
| A-AA1 | middels | G9 | kjent |
| A-AA2 | lav | `min_liste` har to skriveveier, og `valg.py` og `ferdige_lister.py` leser fire tabeller med egen SQL, mot AD-3. Arkitekturen sier fortsatt bare `POST /min-liste/merk` | delvis kjent |
| A-AA3 | lav | «Egen» merker alle som kom inn via et ønske, også aksjene fra en ferdig liste og en av de 15 som er tatt ut og inn igjen | delvis kjent: `spec-2-12` |
| A-AA4 | lav | Arkitekturen sier at `Oversiktsleser` har to metoder. Adapteren har tre | nytt |
| A-VG1 | middels | G10 | nytt |
| A-VG2 | lav | `BEGIN IMMEDIATE` i `_laas` kan byttes mot `BEGIN` uten at en test feiler | nytt |
| A-VG3 | lav | 17. mai kan fjernes fra kalenderen uten at en test feiler: første år dagen teller alene, er 2028 | nytt |
| A-VG4 | lav | Ventetiden på en låst base har ingen test | nytt |
| A-VG5 | lav | To triggere i `0012_notat.sql` for oppdatering har ingen test | nytt |
| A-VG6 | lav | Usikker: ingen test fjerner en aksje samme børsdag som den kom inn uten rader | nytt |

## Del B: hentingen, signalet og skriptene

18 funn: 5 på middels og 13 lave. Leseren lot 10 mindre ligge. Nøkkelen har ingen lekkasjevei leseren fant, og nye forsøk, indeksen alene og målingen uten `--med-bonuskvoten` bruker ikke bonuskvoten.

| Id | Grad | Funnet | Kjent |
|---|---|---|---|
| B-BH1 | middels | G5 | nytt |
| B-BH2 | lav | Forsøksfila skrives ikke atomisk. En `OSError` midt i gir en halv fil etter at kallene er brukt | kjent for kursfila: `spec-2-0` |
| B-BH3 | lav | Tre docstringer stemmer ikke, blant dem «bare naar den er paa siste versjon» i `ta_i_bruk_oenskene` og «de 15» i `dagen_ferdig.py` | nytt |
| B-BH4 | lav | Hovedhentingen har ingen sperre kl. 23:50. En start kl. 23:55 bruker kallene og stopper vurderingene ved midnatt | delvis kjent: `deferred-work.md` |
| B-ECH1 | middels | G6 | kjent |
| B-ECH2 | lav | `dagen_ferdig.py` sjekker ikke teksten om dagen. Feilet grunnlaget for den én gang, lages den aldri for den dagen | nytt |
| B-ECH3 | lav | Stopper Oppgaveplanlegging en kjøring etter 1 time, blir Docker Desktop og Ollama stående. Hva Windows gjør med barneprosessene, er antatt | delvis kjent: `spec-2-3d` |
| B-ECH4 | lav | To hentinger samtidig bruker 12 kall fra bonuskvoten uten at utskriften sier det | kjent: `issues.md`, gruppens svar 28.10 |
| B-ECH5 | lav | Uten Docker Desktop venter jobben hele tidsgrensen på 180 s. Kjøringen kl. 23:45 kommer da nær 23:50. Samme sak som spørsmål 1 i 2.22 | nytt |
| B-AA1 | middels | G7 | delvis kjent |
| B-AA2 | lav | Kan kvoten ikke leses ved første henting i en tom base, kan hentingen gå på bonuskvoten (NFR-01) | delvis kjent: `spec-2-3` |
| B-AA3 | lav | FR-406 og AD-5: ingen kontroll av 175 børsdager. Se G6 | kjent |
| B-VG1 | middels | G8 | nytt |
| B-VG2 | middels | G5 | nytt |
| B-VG3 | lav | `"x"` kan byttes mot `"w"` for forsøksfila og omsetningsfila uten at en test feiler | nytt |
| B-VG4 | lav | Ingen test har første henting med en kvote som ikke kan leses | nytt |
| B-VG5 | lav | Sjekken av datoen i GMT før første kall i målingen har ingen test | nytt |
| B-VG6 | lav | `umask 077` i `start/start.sh` har ingen test | nytt |

## Del C: sidene

20 funn: 4 på middels og 16 lave. Leseren lot 6 mindre ligge. `app.py` er lest i sin helhet.

| Id | Grad | Funnet | Kjent |
|---|---|---|---|
| C-BH1 | lav | `POST /angre` med en `id` på 20 sifre gir 500 (`OverflowError`). Prøvd av leseren utenfor repoet | nytt |
| C-BH2 | lav | KI-bryteren ved «Børsdagen kort fortalt» mister filteret «Min liste» | nytt |
| C-BH3 | lav | Linja over grafen farges etter det urundede tallet, så «0,00 %» kan stå i grønt | nytt |
| C-BH4 | lav | `/folg?feil=<tekst>` viser vilkårlig tekst i feilboksen. Teksten er escapet | nytt |
| C-BH5 | lav | Vernet på POST-rutene er bare Origin-sjekken | kjent: `spec-8-3`, avvist |
| C-ECH1 | middels | G3 | nytt |
| C-ECH2 | middels | G4 | nytt |
| C-ECH3 | lav | Børsometeret med en valgt dag viser lista i dag, oversikten lista den dagen | nytt, gruppen bør avgjøre |
| C-ECH4 | lav | Lappen på dagstreken er 44 px, men datoen får år når året er et annet | nytt |
| C-ECH5 | lav | Én serie som ikke kan tolkes, gir 500 på børsometeret og aksjesiden. At `serie()` kan gi `ValueError`, er antatt | nytt |
| C-AA1 | middels | G3 | nytt |
| C-AA2 | lav | Ved en periode viser linja for hovedindeksen siste børsdag, uten at det står. Koden følger avgjørelsen 30.10, men ordlyden i `prd.md` gjør ikke | delvis kjent |
| C-AA3 | lav | Beskjedene i `perioder.py` har alltid år, mot designreglene §4 | nytt |
| C-AA4 | lav | 404, 400 og 403 er Werkzeugs engelske sider (NFR-05) | kjent: `docs/ux-logg.md`, avvist |
| C-VG1 | lav | Feilhåndteringen i `angre` kan fjernes uten at en test feiler | nytt |
| C-VG2 | lav | Ingen test poster `/ki` med «Min liste» valgt | nytt |
| C-VG3 | middels | G3 | nytt |
| C-VG4 | lav | Origin-vernet testes bare for to av notatrutene | nytt |
| C-VG5 | lav | Ingen test ser på fargen i linja over grafen | nytt |
| C-VG6 | lav | Ingen test viser en dag i et annet år | nytt |

## Del D: KI-teksten og demoen

21 funn: 2 på høy, 8 på middels og 11 lave. Leseren lot 3 mindre ligge. Nøkkelen står bare i headeren, og prompten for én aksje har verken navn eller symbol.

| Id | Grad | Funnet | Kjent |
|---|---|---|---|
| D-BH1 | høy | G1 | nytt |
| D-BH2 | høy | G2 | kjent |
| D-BH3 | lav | `ki_lokal.py` følger videresendinger, mens skyadapterne ikke gjør det | nytt |
| D-BH4 | lav | Docstringer som ikke stemmer om hvem som laget demotekstene. **3.4:** `demo.py` sier at DEMIX ikke er sjekket mot Euronext ennå | nytt |
| D-BH5 | lav | En modell sjekken godtar, kan gi rader uten modell-ID og maskinvare (FR-604) | nytt |
| D-ECH1 | middels | G11 | delvis kjent |
| D-ECH2 | middels | G11 | kjent |
| D-ECH3 | lav | `ki_lokal.py` leser ikke om svaret ble kortet av. At Ollama melder det i et eget felt, er antatt | nytt |
| D-ECH4 | lav | Teksten om dagen forsvinner for eldre dager når lista endres, uten at siden sier hvorfor. Se G3 | nytt |
| D-ECH5 | lav | Markdown og HTML i teksten for én aksje vises som rå tegn. De er escapet | nytt |
| D-ECH6 | lav | **3.4:** en eldre demobase kjennes igjen på to tegn, uten versjonsmerke | nytt |
| D-AA1 | middels | G12 | delvis kjent |
| D-AA2 | middels | G13 | nytt |
| D-AA3 | middels | G2 | delvis kjent: `spec-10-10` |
| D-AA4 | lav | AD-2 sier én hentefunksjon i hver skyadapter. Koden har én felles i `ki_sky.py` | nytt |
| D-AA5 | lav | **3.4:** alle demoradene besto, så meldingene for en tekst som ikke besto, kan ikke vises i demoen (FR-411) | nytt |
| D-VG1 | middels | G2 | nytt |
| D-VG2 | middels | G14 | nytt |
| D-VG3 | middels | G12 | nytt |
| D-VG4 | lav | **3.4:** feilhåndteringen for `demo_ki_dagen.json` har ingen test | nytt |
| D-VG5 | lav | «tilrad» i vakta på siden har ingen test | nytt |

## Tellingen

| | Del A | Del B | Del C | Del D | Sum |
|---|---|---|---|---|---|
| Blind Hunter | 5 | 4 | 5 | 5 | 19 |
| Edge Case Hunter | 5 | 5 | 5 | 6 | 21 |
| Acceptance Auditor | 4 | 3 | 4 | 5 | 16 |
| Verification Gap | 6 | 6 | 6 | 5 | 23 |
| **Sum** | 20 | 18 | 20 | 21 | 79 |
| Høy | 0 | 0 | 0 | 2 | 2 |
| Middels | 2 | 5 | 4 | 8 | 19 |
| Lav | 18 | 13 | 16 | 11 | 58 |
| Mindre, ikke ført | 15 | 10 | 6 | 3 | 34 |

## Det leserne ikke leste helt

- **Del A:** `epics.md` er ikke lest; AA bygger på `prd.md` og arkitekturen. Testene er søkt i, ikke lest som hele filer.
- **Del B:** `epics.md` er ikke lest; storyene er sjekket mot sprintstatusen og spesifikasjonene. `start.sh` er lest, men ikke vurdert på en Mac eller Linux-maskin. `test_kveldshenting.py`, `test_dobbeltklikk.py` og `test_docker.py` er bare søkt i.
- **Del C:** `moenstrene.py`, `ikon.py`, `hjelpetekster.py` og `oversiktsdata.py` er ikke lest. `hjelp.js`, `stil.css`, `dagene.py` og `dagsgrunnlag.py` er bare søkt i. Storyene i Epic 8 er lest bare for 8.17.
- **Del D:** `SqliteKILogg` og `kilogg_minne.py` er ikke lest. JSON-filene, Epic 10 og story 3.4 i `epics.md` er bare søkt i. `docs/kilder-og-rettigheter.md` er lest til OpenAI-delen.

Det som ikke er lest, er ikke gjennomgått. Et tomt felt i tabellene betyr ikke at det er uten feil.

## Spørsmål til gruppen

1. **Hvilke grupper blir storyer etter brukertest 2?** *Forslag:* G1 og G2 sammen først, fordi de gjelder NFR-06 og det brukeren leser. Så G3 og G4 sammen, G5, G6 og G12. G8, G10 og G14 er bare tester og kan tas i én story.
   *Svar 24.11 kl. 21:47:* som foreslått. Rådet anbefalte det. Etter brukertest 2 kommer G1 og G2 først (story 10.12), så G3 og G4 (10.13), G5 (2.23), G6 (2.24) og G12 (10.14), og én story med bare tester for G8, G10 og G14 (2.25). De står i `epics.md` og sprintstatusen som backlog, merket «etter brukertest 2», i epicen som eier koden. Ingen av dem bygges nå. Før testen leser gruppen KI-teksten for aksjen i oppgave B (`docs/brukertest.md`, «Før testen (brukertest 2)»).
2. **G7, lista over Oslo Børs i en ZIP-kopi eller i Docker.** *Forslag:* avgjør om fila kan ligge i repoet etter vilkårene, eller om hjelpen skal si at «Følg en aksje» trenger den.
   *Svar 24.11 kl. 21:47:* gruppen avgjør det når den har lest vilkårene for lista over Oslo Børs. Rådet anbefalte det. Det står som åpent punkt i `.logs/marian-osen/issues.md`.
3. **G9, ordlyden i FR-412.** *Forslag:* rett ordlyden i `prd.md` til det koden gjør, med en linje i endringsloggen: aksjen tas inn, og tas ut kvelden etter hvis EODHD ikke gir kurser.
   *Svar 24.11 kl. 21:47:* som foreslått. Rådet anbefalte det. Ordlyden i FR-412 i `prd.md` er rettet til det koden gjør, med en linje i endringsloggen, og raden i `prd-sporing.md` følger med. Ingen kode er endret.
4. **G11, én feil stopper KI-teksten for hele kvelden.** Valget ble gjort for en modell som henger. *Forslag:* behold det for tidsfrist og nettfeil, og la et tomt svar eller et avslag gjelde bare den ene aksjen.
   *Svar 24.11 kl. 21:47:* som foreslått. Rådet anbefalte det. Det er story 10.15, i backlog til etter brukertest 2.
5. **G13, navn i prompten for dagen.** *Forslag:* gruppen fører det i `docs/kilder-og-rettigheter.md`, under «Hva som sendes».
   *Svar 24.11 kl. 21:47:* gruppen skriver det selv i `docs/kilder-og-rettigheter.md`. Rådet anbefalte det. Det står som åpent punkt i `.logs/marian-osen/issues.md`, og vinduet skriver det ikke.
6. **Funnene merket 3.4** (D-BH4, D-ECH6, D-AA5 og D-VG4) står til gruppen har svart på 3.4.
   *Svar 24.11 kl. 21:47:* funnene står til gruppen har svart på 3.4. Rådet anbefalte det.
