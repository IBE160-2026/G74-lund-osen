# Epic 1 Context: Dataene overlever en omstart, og historikken lagres slik at den kan leses tilbake

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Kursene skal ligge i en SQLite-base og overleve at maskinen slås av, og det
løsningen mente om hver aksje hver kjøredag skal lagres slik at det ikke kan
skrives om i ettertid. Epicen legger lagringsgrunnlaget de senere epicene står
på: migrasjonsløperen, `Kurslager`-porten med typede norske rader (`Kursrad`),
SQLite-adapteren, lesegrensen mot øyeblikksbildene, `Vurderingslager` og
skillet mellom tilstandene i lageret. Bruddet med `Kurskilde` ved siden av
`Kurslager` er lukket i 1.4c, og I/O i portmodulen `kursdata.py` er lukket i
1.5 (`23af8db`). `Vurderingslager` er bygget i 1.6 (`7dc8a48`, PR #8), og de tre
tilstandene skilles i 1.7 (`5e9e6ad`, PR #9). *Oppdatert 2026-09-27:* det som
står igjen i epicen, er to stories fra kodegjennomgangen og prioriteringen
27.09: 1.8 (hentingen og leseren får én regel for en gyldig serie) og 1.9
(`aksje`-tabellen, som de andre tabellene peker på). I v1 blir historikken
lagret, men ikke besvarbar i denne epicen. *Avgjort 2026-09-27:* historikken
vises i aksjedetaljen, story 2.7 i Epic 2, fordi den trenger at webserveren
leser basen (2.2) og at vurderingen skrives (2.5).

## Stories

- Story 1.1: Migrasjonsløperen og `skjema_versjon`
- Story 1.2: `Kursrad` og `Kurslager`-porten
- Story 1.3: SQLite-adapteren og `kurs`-tabellen
- Story 1.4a: Lesegrensen — `Kursleser` og oversetteren fra øyeblikksbildet
- Story 1.4b: Konsumentene leser `Kursrad`
- Story 1.4c: Rydding — `Kurskilde` ut, `sist_hentet` inn
- Story 1.5: `SnapshotKilde` ut av `kursdata.py`
- Story 1.5b: Migrasjonsløperen og SQLite-adapteren herdes
- Story 1.6: `Vurderingslager` med datoavvisning
- Story 1.7: De tre tilstandene skilles
- Story 1.8: Hentingen godtar bare det leseren kan lese
- Story 1.9: Aksjene i basen, og tabellene peker på dem

## Requirements & Constraints

- **To lagre for kursdata som aldri blandes.** Beregningsgrunnlaget (`kurs` i
  basen) erstattes i sin helhet per symbol ved hver henting, i én transaksjon,
  og skjøtes aldri på. Rådata er tidsstemplede øyeblikksbilder som aldri skrives
  om, og som bevares fra første kjøring. Hver henting dekker minst 175
  handelsdager (125 for grafen pluss 50 for MA50).
- **Dagens vurdering lagres per aksje** hver dag kommandoen kjøres: dato,
  signalstyrke, retning, verdien fra hver av de tre sjekkene, relevante
  meldinger og kursen (`close` og `adjusted_close`). Vurderinger etterfylles
  aldri. En vurdering skrevet i ettertid ville vært dagens parametres svar, ikke
  datidens.
- **Tre tilstander skal være entydig skillbare i lageret:** rad med styrke 0 (et
  gyldig svar), ingen rad på en børsdag (kommandoen ble ikke kjørt) og ingen rad
  på en ikke-børsdag (dagen finnes ikke). De tre gir tre ulike verdier, ikke to
  og en `None`. En rad med grunn er en fjerde lesning: kommandoen kjørte, men
  kunne ikke vurdere aksjen. Kravet gjelder lageret, ikke en skjerm, og enhver
  senere visning, kommando eller spørring skal bevare skillet.
- **En aksje hentingen melder som hentet, skal også kunne leses** (1.8). Én
  regel avgjør om en serie fra EODHD kan leses, og både hentingen og leseren
  bruker den. En serie leseren ville avvist, gir «svar med feil form» for
  symbolet, og de andre lagres likevel. Øyeblikksbildet beholder formatet.
- **Basen skal selv kjenne de femten aksjene** (1.9). En rad i `kurs`,
  `kursserie` eller `vurdering` for et symbol som ikke står i `aksje`, avvises
  av basen, også formen `EQNR.OL`. En aksje med rader kan ikke slettes. Porten
  skal ikke være eneste vakt. SQLite ble godtatt av faglærerstaben ut fra
  relasjoner mellom data, joins, migrasjoner og logging av KI-vurderinger, og i
  dag har ingen tabell fremmednøkler.
- **Manglende data stopper ikke hovedflyten.** Et symbol som ikke kan leses,
  behandles som manglende og navngis for brukeren. De andre vises som vanlig.
  Hver story trenger en test for den tomme eller manglende stien.
- **Hver story leveres med test som kjører uten nett.** Testsettet telles før og
  etter, og tallet føres i commit-meldingen. Det antas ikke. Hver story har en
  «ville feilet hvis»-kontroll, og det er den som avgjør om storyen er ferdig.
- **Kontrollregning på ekte data** gjøres mot et øyeblikksbilde som finnes,
  uten API-kall, og utfallet føres som antall like rader, aldri som verdiene.

**Avgjort i kildene (2026-09-27):**
- **Inneværende børsdag** er siste børsdag på eller før dagens dato i
  Europe/Oslo (punkt 3 i `prd.md` §8, lukket). En børsdag er mandag–fredag som
  ikke står på lista over dager Oslo Børs er stengt, ført for hånd fra
  Euronexts kalender for 2026. Halve handelsdager er børsdager, og for en dato
  utenfor lista reiser funksjonen en feil. Funksjonen er ren, ligger i kjernen
  og ble bygget i 1.6.
- **Ingen rad på en børsdag** løses med en lagret grunn på raden, ikke en egen
  tilstand (punkt 24, lukket). Kan kjøringen ikke vurdere en aksje, skriver den
  en rad med grunnen i stedet: symbolet feilet, nyeste kurs var ikke fra dagen,
  eller signalet kunne ikke regnes. En rad med grunn skriver aldri over en rad
  med vurdering samme dag. Svaret bestemte formen på `vurdering` i 1.6.
- **Relevante meldinger** er ikke med i `0002`, fordi meldingsdelen er blokkert
  og kan bli strøket 28.09. De kommer senere som en kolonne som kan være tom
  (`ALTER TABLE vurdering ADD COLUMN`), der `NULL` betyr «ikke registrert».

**Uavklart i kildene:**
- Hvordan en skjemaendring på `vurdering` skal gjøres uten å bryte forbudet mot
  sletting, er ikke avgjort. Det avgjøres ved første migrasjon som rører
  `vurdering`. *Utsatt videre 2026-09-27 (1.6):* `0002` er formet
  så de to endringene vi vet om, ikke krever ombygging: en ny grunn er en
  `INSERT INTO grunn` i en ny migrasjon, og meldingene er en ny kolonne.
  Verdiene kontrolleres derfor i porten, ikke i en `CHECK`, fordi en ny regel i
  en `CHECK` krever ombygging. Spørsmålet står åpent for alle andre
  formendringer. 1.9 rører `vurdering`, og planen for den må velge
  fremmednøkkel eller trigger med grunnen fra `0002`. Fremmednøkler på en
  kolonne som finnes, krever at tabellen bygges om, og det er billigst før den
  har data.
- **Dagene Oslo Børs er stengt i 2027** er ikke ført inn (åpent punkt 25, eier
  Marian, frist 2026-12-01). Lista dekker bare 2026, så fra 2027-01-01 reiser
  `innevaerende_boersdag`, og dermed `skriv`. Dagene føres inn i `STENGT` i
  `src/boersdag.py` og i `docs/kilder-og-rettigheter.md` (Handelskalenderen)
  når Euronext publiserer dem, og 2027 legges til i `DEKKEDE_AAR` samtidig.

## Technical Decisions

- **Funksjonell kjerne, imperativt skall, porter som `typing.Protocol`.**
  Kjernemodulene importerer ikke `requests`, `sqlite3`, `pathlib` eller `flask`.
  Portmodulen `kursdata.py` gjør ikke I/O og importerer ikke `json` eller
  `pathlib` (oppfylt fra 1.5, `23af8db`). `kursdata.py`, `vurderingsdata.py` og
  `boersdag.py` importerer ingen annen prosjektmodul. `tilstand.py` importerer
  bare `boersdag` og porten `vurderingsdata`, aldri skallet.
- **Én port og én skriver per datasett:** `Kurslager` (med lesesiden
  `Kursleser`: `serie`, `sist_hentet`), `Vurderingslager` og `KILogg`. Ingen
  felles lagerklasse. Navneregel: `<Datasett>lager` har skrivesiden,
  `<Datasett>leser` er lesesiden av samme port, `<Datasett>logg` legges bare
  til, og `<Noe>kilde` leser bare rådata fra fil.
- **SQLite fra standardbiblioteket,** ingen hostet database. Adapteren tar en
  `sqlite3.Connection`, ikke en filsti. Skallet bestemmer hvor basen ligger.
- **`erstatt_serie(symbol, rader, hentet)`** gjør DELETE+INSERT og skriver
  `hentet` i samme transaksjon. Tiden er et argument og leses ikke av lagerets
  egen klokke. En tom serie avvises med `ValueError`. Det finnes ingen
  `legg_til_rad`.
- **`Kursrad`** har `dato` (`datetime.date`), `slutt`, `justert_slutt` og
  `volum`. Kildens feltnavn stopper i adapteren: EODHDs feltnavn skal bare stå
  i `eodhd.py`, og 1.8 legger `fetch_prices.py` under strengvakten i
  `test_konsumentene.py`. EODHD-oversettelsen skjer ett sted
  (`kursrad_fra_eodhd`), som Epic 2 også bruker, og faller aldri tilbake fra
  `adjusted_close` til `close`. Beregning bruker justert kurs, mens
  markedsoversikten viser `close`.
- **Tid:** børsdato er norsk kalenderdato (Europe/Oslo). Tidsstempler er UTC med
  offset. Ved grensene lagres dato som `YYYY-MM-DD` og tid som ISO 8601.
  Tidssonen krever `tzdata` på Windows.
- **Uerstattelige lagre** (`vurdering`, `ki_logg`) har bare `skriv` og
  lesemetoder, ingen `slett` og ingen `endre`. `skriv` er idempotent på
  `(symbol, dato)` og avviser enhver dato som ikke er inneværende børsdag.
  Datogrensen regnes i norsk tid, ikke i UTC. Samme `(symbol, dato)` igjen
  skriver over, og den siste vinner, med ett unntak: en `Grunn` over en
  `Vurdering` ignoreres, og `skriv` gir `False` uten å reise, så ett symbol som
  feiler, ikke stopper kjøringen. En dato som avvises, reiser, og da skrives
  ingenting.
- **`vurdering` lagrer kursen som verdier.** Den har ingen fremmednøkkel til
  `kurs`, fordi `erstatt_serie` ellers ville feilet eller slettet historikk.
  Det gjelder også etter 1.9.
- **Slik 1.6 ble bygget (`7dc8a48`):**
  - `src/boersdag.py` er ren kjerne: `innevaerende_boersdag(dag)` gir siste
    børsdag på eller før `dag`, og `norsk_dato(oeyeblikk)` gir kalenderdatoen
    i Oslo for et tidspunkt med sone (uten sone reiser den). `STENGT` er de
    stengte hverdagene i 2026, og `DEKKEDE_AAR` er årene lista dekker. Må
    funksjonen slå opp en dag utenfor dem, reiser den `UtenforKalenderen`
    (en `ValueError`) i stedet for å gjette. Den leser aldri klokka selv.
  - `src/vurderingsdata.py` er porten, uten I/O og uten import av kjernen:
    `Vurdering` (styrke, retning, de tre sjekkene og `slutt`/`justert_slutt`,
    kontrollert ved opprettelse), `Grunn` (`symbol_feilet`,
    `kurs_ikke_fra_dagen`, `signal_ikke_regnet`) og `Vurderingslager` med
    bare `skriv` og `les`. `les` gir `Vurdering`, `Grunn` eller `None`.
  - `0002_vurdering.sql` lager `vurdering` og `grunn`. En `CHECK` krever enten
    alle sju vurderingsfeltene eller en grunn, aldri begge. Grunnene er rader i
    `grunn`, håndhevet med triggere, og en grunn kan ikke slettes eller endres.
  - `SqliteVurderingslager` i `src/lagring_sqlite.py` tar en tilkobling og en
    klokke, og klokka leses ved hvert `skriv`. Den godtar bare symboler i
    `AKSJEUNIVERS` (formen `EQNR`, ikke `EQNR.OL`), både i `skriv` og `les`.
    Datokontrollen ligger i adapteren, fordi porten ikke importerer kjernen.
    Det finnes med vilje ikke noe minnelager. Testene bruker SQLite i minnet.
- **Slik 1.7 ble bygget (`5e9e6ad`):** `tilstand.tilstand(innhold, dato, idag)`
  tar imot det `les` gir og skiller svar, rad med grunn, ikke kjørt og ikke
  børsdag, med `boersdag.er_boersdag` og samme liste som `skriv`. Lageret
  svarer fortsatt `None` for både «ikke kjørt» og «ikke børsdag», og skillet
  kan gjenskapes så lenge kalenderen dekker året. Porten fikk ingen ny metode.
  «Ikke kjørt» er ikke et endelig hull så lenge dagen er inneværende børsdag.
  En dato etter dagens dato reiser `ValueError`, også når raden finnes, og en
  dag uten rad utenfor `DEKKEDE_AAR` reiser `UtenforKalenderen`.
- **Skjemaendringer bare via nummererte migrasjoner** med `skjema_versjon`.
  Løperen styrer transaksjonen selv og bruker aldri `executescript()`, som gjør
  en implisitt `COMMIT`. `vurdering` opprettes av `0002`, som ble skrevet etter
  herdingen i 1.5b. `aksje` opprettes av `0003` i 1.9, og en test holder
  tabellen og `AKSJEUNIVERS` like.
- **Rådatafiler** heter `<prefiks>-raa-<dato>.json` og skrives aldri om.
  `nyeste_snapshot` velger på dato alene, og `KURSPREFIKS` vinner ved lik dato.
- **Låste signalparametre** endres ikke i denne epicen uten ny måling.

## UX & Interaction Patterns

- Markedsoversikten viser hvor gamle dataene er: sidens tidsstempel er det
  eldste `sist_hentet` blant symbolene som vises. En rad som er eldre enn den
  nyeste, viser sitt eget tidsstempel på raden, uten en sjette kolonne.
  Tidsstempler vises i norsk tid.
- All brukervendt tekst er på norsk, og ingen formulering skal kunne leses som
  et investeringsråd.

## Cross-Story Dependencies

- **Rekkefølgen inne i epicen:** 1.1 → 1.2 → 1.3 → 1.4a → 1.4b → 1.4c, med hele
  testsettet kjørt mellom hvert steg. `Kursrad` kom i en egen endring før
  SQLite-adapteren (1.2, så 1.3), ikke i samme endring som planen først sa.
- **1.5b før 1.6, 1.6 før 1.7:** herdingen (a–h) var på plass før `0002` ble
  skrevet (1.5b flettet i `ef1cca7`, PR #5). Punkt 3 og 24 ble avgjort før 1.6.
  1.7 leser de tre tilstandene fra `vurdering` gjennom `Vurderingslager`, og
  børsdagene fra `src/boersdag.py`. En rad med grunn leses som en rad
  (kommandoen kjørte, men kunne ikke vurdere aksjen), ikke som styrke 0 og ikke
  som fravær. Alle tre er ferdige.
- **1.8 har ingen forutsetning.** Den kommer fra G1 i kodegjennomgangen av
  Epic 1 (27.09): hentingen i `fetch_prices.py` sjekker bare at feltene finnes
  og at `date` er tekst, mens `SnapshotLeser` oversetter hver rad og avviser
  like datoer. En serie kan da lagres uten noe i `feil` og droppes av leseren.
  Testene for leseren og hentingen tar radene fra samme liste. Storyen tar også
  G2–G5 og G8: `len(AKSJEUNIVERS)` i stedet for 14 og 15, en nøkkel med
  mellomrom i testen for URL-koding, `SnapshotLeser` i docstringene, en test
  som binder `styrke` i `Vurdering` til `beregn_signal`, og testnavnet uten
  `versjon_1`.
- **1.9 før Epic 2 skriver til basen.** Fremmednøkkel eller trigger velges i
  planen, og det er billigst mens tabellene er tomme. 1.9 løser i basen at
  `Kurslager` godtar ethvert symbol mens `Vurderingslager` bare godtar formen i
  `AKSJEUNIVERS` (G10).
- **Epic 2 venter på Epic 1:** hentingen skriver gjennom `Kurslager`, bruker
  `kursrad_fra_eodhd` og skriver vurderingen gjennom `Vurderingslager` i samme
  kjøring (2.5). For et symbol som feilet, skriver 2.5 en rad med grunnen, også
  når nyeste kurs ikke er fra dagen og når signalet ikke kan regnes. *Utsatt
  til 2.5:* en kjøring som går over midnatt i Oslo, får `ValueError` fra
  `skriv` for resten av symbolene, fordi klokka leses ved hvert kall. Symbolene
  som alt er skrevet, står, mens resten får verken vurdering eller grunn. 2.5
  må si hva som skjer da. 2.5 avgjør også om `Kurslager` skal sjekke symbolet,
  og hvilke feil kjøringen fanger: `SqliteVurderingslager.skriv` slipper ut
  `sqlite3`-feil, mens `erstatt_serie` gjør `IntegrityError` om til
  `ValueError` (G11). At `main()` i hentingen ikke har noen test (G12), tas i
  2.1.
- **Historikken (punkt 20) vises i 2.7,** som avhenger av 2.2 og 2.5. Den gir
  `Vurderingslager` en lesemetode for en periode, uten slette- eller
  endremetode, og hver dag går gjennom `tilstand`.
- **Epic 4.3** (SQLite-adapter for `KILogg`) venter på Epic 1. **Epic 5B**
  avhenger av 1.4a (`Kursleser`).
- **Utsatt til story 3.1:** hvem som kjører migrasjonene, og når. Løperen må
  kunne kalles både fra hentekommandoen og fra webserverens oppstart, uten
  endring. Den får ikke inneholde `DROP TABLE`-hjelpere eller unntaksveier for
  uerstattelige lagre. En egen migrasjonskommando ville brutt suksessmålet om at
  én kommando gjør hele hentingen.
- **Kodegjennomgang etter Epic 1** med `bmad-code-review` (åpent punkt 22). En
  første gjennomgang ble gjort etter 1.1–1.3, og funnene står som
  forutsetninger i 1.5b og 2.2. Gjennomgangen av hele epicen ble gjort 27.09
  (`kodegjennomgang-epic-1.md`), og funnene er fordelt på 1.8, 2.1 og 2.5.
- **Prioritering 2026-09-27:** databasen skal i bruk i Epic 2, med skrivingen
  først, fordi en vurdering ikke kan etterfylles og løsningen må brukes
  jevnlig. 1.9 står blant det vi prøver å få til, før Epic 2 skriver til
  basen. Den utvider ikke omfanget: den er en skjemaendring før basen har data.
