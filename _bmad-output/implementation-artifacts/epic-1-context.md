# Epic 1 Context: Dataene overlever en omstart, og historikken lagres slik at den kan leses tilbake

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Kursene skal ligge i en SQLite-base og overleve at maskinen slås av, og det
løsningen mente om hver aksje hver kjøredag skal lagres slik at det ikke kan
skrives om i ettertid. Epicen legger lagringsgrunnlaget de senere epicene står
på: migrasjonsløperen, `Kurslager`-porten med typede norske rader (`Kursrad`),
SQLite-adapteren, lesegrensen mot øyeblikksbildene, `Vurderingslager` og
skillet mellom de tre tilstandene i lageret. Samtidig lukkes to kjente brudd på
arkitekturen: `Kurskilde` ved siden av `Kurslager`, og I/O i portmodulen
`kursdata.py`. I v1 blir historikken lagret, men ikke besvarbar. Hvordan
spørsmålet om hva løsningen sa en tidligere dag skal kunne stilles, er et åpent
punkt med frist før demonstrasjonen.

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
  og en `None`. Kravet gjelder lageret, ikke en skjerm, og enhver senere
  visning, kommando eller spørring skal bevare skillet.
- **Markedsoversikten viser hvor gamle dataene er:** sidens tidsstempel er det
  eldste `sist_hentet` blant symbolene som vises. En rad som er eldre enn den
  nyeste viser sitt eget tidsstempel under selskapsnavnet, ikke i en sjette
  kolonne. Tidsstempler vises i norsk tid.
- **Manglende data stopper ikke hovedflyten.** Et symbol som ikke kan leses,
  behandles som manglende og navngis for brukeren. De andre vises som vanlig.
  Hver story trenger en test for den tomme eller manglende stien.
- **Hver story leveres med test som kjører uten nett.** Testsettet telles før og
  etter, og tallet føres i commit-meldingen. Det antas ikke. Hver story har en
  «ville feilet hvis»-kontroll, og det er den som avgjør om storyen er ferdig.
- **Kontrollregning på ekte data** (1.4b) gjøres mot et øyeblikksbilde som
  finnes, uten API-kall, og utfallet føres som antall like rader, aldri som
  verdiene.

**Uavklart i kildene:**
- Hva «inneværende børsdag» betyr en lørdag eller en helligdag, er ikke
  avgjort. Det må avgjøres før 1.6 (åpent punkt 3). Det finnes et forslag,
  «siste børsdag på eller før dagens dato i Europe/Oslo», men det er ikke
  vedtatt.
- Om «ingen rad på en børsdag» trenger en fjerde tilstand eller en lagret grunn
  på raden, er ikke avgjort. Det må avgjøres før 1.7 (åpent punkt 24). Årsaken
  er at en kjøring før kursen er publisert, eller et symbol som feilet, også gir
  ingen rad.
- Vurderingen skal etter kravet ha med relevante meldinger, men meldingsdelen er
  blokkert og kan bli strøket 28.09. Kildene sier ikke hvordan feltet skal
  håndteres i 1.6 uten meldinger.
- Hvordan en skjemaendring på `vurdering` skal gjøres uten å bryte forbudet mot
  sletting, er ikke avgjort. Det avgjøres ved første migrasjon som rører
  `vurdering`, tidligst etter 1.6.

## Technical Decisions

- **Funksjonell kjerne, imperativt skall, porter som `typing.Protocol`.**
  Kjernemodulene importerer ikke `requests`, `sqlite3`, `pathlib` eller `flask`.
  Portmodulen `kursdata.py` skal heller ikke gjøre I/O. Den gjør det i dag, og
  det lukkes i 1.5.
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
  `volum`. Kildens feltnavn stopper i adapteren. EODHD-oversettelsen skjer ett
  sted (`kursrad_fra_eodhd`), som Epic 2 også bruker, og faller aldri tilbake
  fra `adjusted_close` til `close`. Beregning bruker justert kurs.
- **Tid:** børsdato er norsk kalenderdato (Europe/Oslo). Tidsstempler er UTC med
  offset. Ved grensene lagres dato som `YYYY-MM-DD` og tid som ISO 8601.
  Tidssonen krever `tzdata` på Windows.
- **Uerstattelige lagre** (`vurdering`, `ki_logg`) har bare `skriv` og
  lesemetoder. `skriv` er idempotent på `(symbol, dato)` og avviser enhver dato
  som ikke er inneværende børsdag. Datogrensen regnes i norsk tid, ikke i UTC.
- **`vurdering` lagrer kursen som verdier.** Den har ingen fremmednøkkel til
  `kurs`, fordi `erstatt_serie` ellers ville feilet eller slettet historikk.
- **Skjemaendringer bare via nummererte migrasjoner** med `skjema_versjon`.
  Løperen styrer transaksjonen selv og bruker aldri `executescript()`, som gjør
  en implisitt `COMMIT`. `vurdering` opprettes av migrasjon `0002`.
- **Rådatafiler** heter `<prefiks>-raa-<dato>.json` og skrives aldri om.
  `nyeste_snapshot` velger på dato alene, og `KURSPREFIKS` vinner ved lik dato.
- **Låste signalparametre** endres ikke i denne epicen uten ny måling.

## UX & Interaction Patterns

- Bare 1.4c har synlig effekt: sidens tidsstempel og tidsstempel per rad, som
  beskrevet under kravene. All brukervendt tekst er på norsk, og ingen
  formulering skal kunne leses som et investeringsråd.

## Cross-Story Dependencies

- **Rekkefølgen inne i epicen:** 1.1 → 1.2 → 1.3 → 1.4a → 1.4b → 1.4c, med hele
  testsettet kjørt mellom hvert steg. `Kursrad` skulle etter planen inn i samme
  endring som SQLite-adapteren, men ble en egen endring først (1.2, så 1.3).
  Rettelsen fra 2026-09-24 gjelder.
- **Før 1.4b:** testhjelperne `serie()` i tre testfiler lager ugyldige
  tekstdatoer for serier lengre enn 30 rader. De byttes til `date` +
  `timedelta` i en egen commit før 1.4b. 1.4b kan ikke deles videre, fordi
  `beregn_signal` kalles av både `markedsoversikt` og `aksjedetalj`.
- **1.5b før 1.6:** alle åtte herdingspunktene (a–h) må være på plass før
  `0002` skrives. Åpent punkt 3 må være avgjort før 1.6, og åpent punkt 24
  før 1.7.
- **Epic 2 venter på Epic 1:** hentingen skriver gjennom `Kurslager`, bruker
  `kursrad_fra_eodhd` og skriver vurderingen gjennom `Vurderingslager` i samme
  kjøring (2.5). Svaret på åpent punkt 24 bestemmer hva 2.5 skriver for et
  symbol som feilet.
- **Epic 4.3** (SQLite-adapter for `KILogg`) venter på Epic 1. **Epic 5B**
  avhenger av 1.4a (`Kursleser`).
- **Utsatt til story 3.1:** hvem som kjører migrasjonene, og når. Løperen må
  kunne kalles både fra hentekommandoen og fra webserverens oppstart, uten
  endring. Den får ikke inneholde `DROP TABLE`-hjelpere eller unntaksveier for
  uerstattelige lagre. En egen migrasjonskommando ville brutt suksessmålet om at
  én kommando gjør hele hentingen.
- **Etter Epic 1:** kodegjennomgang med `bmad-code-review` (åpent punkt 22).
