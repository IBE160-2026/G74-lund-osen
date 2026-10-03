# Epic 2 Context: Ferske data uten at kvoten sprenges

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren skal kunne hente nye kurser bevisst, og skal ikke ved uhell kunne
brenne dagskvoten på 20 kall. Hentingen er en egen kommando, aldri en bivirkning
av at webserveren startet, og den skal nekte å hente to ganger samme børsdag.
Epicen tar databasen fra Epic 1 i bruk: hentekommandoen skriver kursene (2.1b)
og dagens vurdering med målingene (2.1c, 2.5) i samme kjøring, webserveren leser
kursene fra basen (2.2), og sidene leser dagens vurdering i stedet for å regne
signalet (2.2b). Historikken vises i aksjedetaljen (2.7), og hovedindeksen OSEBX
hentes og vises over markedsoversikten (2.8, 2.9, 2.9b). Status 03.10: 2.0 er
`done`; 2.1, 2.1b, 2.1c, 2.5 og 2.2 er flettet (2.2 i `1570ae9`, PR #19) og står
som `review`. **Neste story er 2.2b**, «Sidene leser dagens vurdering». Resten
står som `backlog`.

## Stories

- Story 2.0: Hentingen lekker ikke nøkkelen og skriver ikke over et øyeblikksbilde
- Story 2.1: Børsdag i Oslo, tidsstempel i UTC
- Story 2.1b: Basen åpnes ett sted, og hentingen skriver kursene dit
- Story 2.1c: Vurderingen lagrer målingene bak de tre sjekkene
- Story 2.2: Hentekommandoen som egen inngang
- Story 2.2b: Sidene leser dagens vurdering
- Story 2.3: Børsdagskontroll før kvoten brukes
- Story 2.4: Etterfylling av hull i kursserien
- Story 2.5: Vurderingen skrives i samme kjøring
- Story 2.6: Utbyttedager merkes
- Story 2.7: Historikken i aksjedetaljen
- Story 2.8: Hovedindeksen hentes i samme kjøring
- Story 2.9: Hovedindeksen i markedsoversikten
- Story 2.9b: Søylene under hovedindeksen

## Requirements & Constraints

- **Henting utløses eksplisitt, aldri av en oppstart.** Webserveren bruker null
  API-kall, også med tom base, og viser da en tom tilstand med kommandoen for å
  hente. En container startes på nytt hver gang.
- **Kvoten:** 20 kall i døgnet, ett per symbol: 15 for aksjene, 16 med indeksen
  (2.8). Kall nummer 21 stopper ikke, men trekker stille fra bonuskvoten. En
  andre kjøring samme børsdag skal gjøre null kall, også med indekskallet. Ett
  kall dekker hele intervallet, så et hull koster ikke ekstra.
- **Når:** børsdager mellom kl. 22:00 og midnatt, norsk tid. Avgjort for 2.3:
  kommandoen nekter før kl. 22:00, med en uttrykkelig overstyring for hånd. Før
  kl. 22:00, på en dag som ikke er børsdag, eller når dataene finnes, bruker den
  null kall og sier hvorfor. Kontrollen eies av hentekommandoen og regnes i norsk
  kalenderdato. Til 2.3 er flettet, kjøres hentingen for hånd; deretter endres
  FR-401 og oppsettet i Oppgaveplanlegging beskrives i README. Er nyeste dato i
  svaret ikke forventet børsdag, vises siste kjente data med tidsstempel, aldri
  som dagens.
- **Én vei til tallet (2.2b):** oversikten og aksjedetaljen viser dagens
  vurdering fra `vurdering` for datoen til nyeste kurs. Mangler raden, vises «–»
  med tilstanden (grunnen, eller «ikke vurdert»), og signalet regnes aldri i
  stedet. En base lest inn med `--les-inn` har ingen vurderinger og sier det.
- **Vurderinger etterfylles aldri; kurser gjør det.** Hver kjøring som fullfører,
  gir hver aksje en rad: vurdering eller grunn.
- **Målingene lagres uavrundet, som brøk** (`trend_avvik`, `dagens_endring`,
  `standardavvik`, `volumforhold`); avrunding bare ved visning.
- **Bare tall vi kan stå for:** ellers «–» med grunnen, aldri 0 eller et anslag.
- **Indeksen er ikke en aksje.** Feiler indekskallet, går aksjene som vanlig;
  indeksen føres i `feil` og gir aldri en rad i `vurdering`. Bare børsdager i
  årene `DEKKEDE_AAR` dekker lagres, uten fast årstall i koden.
- **Utbyttedager (2.6)** merkes av kursserien alene, fra avviket mellom endringen
  i `close` og `adjusted_close`, uten avhengighet til NewsWeb.
- **Universet telles, aldri et fast 15.** Ny kode tar lista som parameter og
  testes med en kortere liste.
- **Demoversjonen (FR-411, 03.10):** en egen kommando lager `data/db/demo.db` med
  oppdiktede selskaper og kurser, uten nøkkel og nett. Hver side som viser den,
  sier «Eksempeltall», merket leses fra basen, ikke fra bryteren, og en side
  leser aldri begge basene. Legger en story i Epic 2 noe til på sidene, får den
  et kontrollpunkt om at demoen viser det også.
- **Manglende data stopper ikke hovedflyten.** Hver story har test for tom sti,
  kjører uten nett, og har «ville feilet hvis» prøvd med mutanter.
- **Nøkkelen** leses fra miljøet, vises eller lagres aldri; øyeblikksbilder
  skrives aldri over. Kontrollregning på ekte data gjøres mot nyeste
  øyeblikksbilde uten API-kall, og utfallet føres uten verdiene.
- **Kan ikke kuttes:** 2.1, 2.1b, 2.5, 2.3 og 2.2. Kuttes i rekkefølgen 2.6, 2.4,
  2.7. Blir det trangt, venter 2.9b først.

## Technical Decisions

- **Én funksjon per kilde rører nettet,** i `fetch_prices.py`, og den injiseres.
- **Tid:** dagen er norsk kalenderdato (Europe/Oslo), `hentet` er UTC med offset.
  Filnavn, `hentet` og vurderingsdatoen kommer fra samme øyeblikk (`naa()` én
  gang). En strengvakt avviser `date.today(`, `datetime.now()` og `astimezone()`
  uten argument i `src/`.
- **Basen åpnes ett sted:** `lagring_sqlite.aapne_base` (`RAA_KATALOG`,
  `BASE_STI`); ingen annen kode kaller `sqlite3.connect`.
- **Skrivingen (2.1b, 2.5):** `erstatt_serie` bytter hele serien per hentet
  symbol. Etter seriene leser `skriv_vurderinger` dem tilbake og skriver én rad
  per aksje med `signalberegning.vurder`: `Vurdering` med målingene, eller
  `KURS_IKKE_FRA_DAGEN`, `SIGNAL_IKKE_REGNET` eller `SYMBOL_FEILET`. Kjøringen
  fanger `sqlite3`-feil fra `skriv`, og stopper hvis det er blitt ny dag i Oslo.
  `skriv` avviser enhver dato som ikke er inneværende børsdag (AD-7).
- **Webserveren mot basen (bygget i 2.2):** bare `/` og `/aksje/<symbol>` rører
  basen. Første forespørsel kjører `migrer()` én gang gjennom `aapne_base`, under
  lås; deretter egen tilkobling per forespørsel (`kjoer_migrasjoner=False`,
  `mode=rw`), lukket i `teardown_appcontext`. Kan basen ikke leses, svarer sidene
  503 uten stier. Den tomme siden viser `HENTEKOMMANDO`. `app.py` importerer
  aldri `fetch_prices`, `requests`, `eodhd` eller `lagring_fil`.
- **2.2b:** oversikten henter de femten fra `aksje` med nyeste og forrige kurs,
  `hentet` fra `kursserie` og dagens rad i `vurdering` i **én spørring med
  join**. Aksjedetaljen tegner grafen av `kurs` og forklarer sjekkene med
  målingene i `vurdering` (FR-706). Tilstanden for en dag uten svar kommer fra
  `tilstand.py`.
- **Demobasen (03.10, AD-7/AD-21/AD-9):** sidene leser selskapene fra `aksje` i
  basen, ikke fra `AKSJEUNIVERS`; portene som skriver, tar lista som parameter
  med `AKSJEUNIVERS` som standard (demoen gir `DEMOUNIVERS`). Porten får ingen
  ny metode: demokommandoen skriver med `skriv` uendret og lagerets klokke stilt
  på hver dag. Demobasen merkes med `PRAGMA application_id`; demokommandoen
  nekter en base uten merket, og hentekommandoen og `--les-inn` nekter en
  demobase før første kall. Hentekommandoen er eneste skriver i den ekte basen.
  Ingen base, heller ikke demobasen, ligger i imaget eller repoet.
- **Indeksen** lagres i egen tabell `indeks` (migrering `0006`, etter `ki_logg`
  i `0005`), aldri i `aksje`, `kurs`, `kursserie` eller `vurdering`.
- **Historikken (2.7)** leses gjennom en ny periodemetode på `Vurderingslager`,
  uten slette- eller endremetode, og regnes aldri ut på nytt av kursene.
- **Låste signalparametre** endres ikke uten ny måling.

## UX & Interaction Patterns

- Tall på sidene skrives norsk via `tallformat.py`: desimalkomma, hardt
  mellomrom som tusenskille og foran %, vanlig bindestrek som minus.
- En dag uten vurdering viser «–» med tilstanden, aldri et regnet signal. Styrke
  0, en grunn og en manglende rad ser aldri like ut.
- **Hovedindeksen (2.9):** over tabellen, med verdien, dagens endring mot forrige
  børsdag og «x av N gikk bedre enn indeksen»; tabellen har fortsatt fem
  kolonner. Lik er ikke bedre. Uten indeks sier siden det, og resten virker.
- **Søylene (2.9b):** én per aksje, fra størst fall til størst stigning, med
  indeksen som stiplet linje (grønn/rød), bransjesymbol fra malen, gult ved 3 av
  3. Skjermleserteksten har alle tallene. Fargegrensene føres i
  `designregler.md`.
- **Historikken (2.7):** fire uker dag for dag; dagens uskrevne rad er ikke et
  hull. Malene deler én layout og én CSS-fil.
- Demobasen merkes «Eksempeltall» på hver side. All tekst er norsk, og ingenting
  skal kunne leses som et investeringsråd.

## Cross-Story Dependencies

- **Rekkefølgen:** 2.1 → 2.1b → 2.1c → 2.5 (daglige kjøringer begynner) → 2.3 →
  2.8 (etter 4.3) → 2.2 → 2.2b → 2.9 → 2.9b → 2.7 → 2.4 → 2.6.
- 2.2b avhenger av 2.2 og 2.5. 2.7 avhenger av 2.2 og 2.5. 2.8 av 2.3 og 4.3;
  2.9 av 2.2 og 2.8; 2.9b av 2.9. 2.8 utvider testen i 2.3 og retter «15 kall»
  til 16 i README og spinen i samme commit.
- **Story 3.4 (demoversjonen)** avhenger av 2.2b, fordi sidene må lese selskaper
  og vurderinger fra basen. Hovedindeksen kommer inn i demoen i den av 2.8 og 3.4
  som bygges sist.
- **Epic 1** er forutsetningen (`Kurslager`, `Vurderingslager`, `tilstand`,
  `aksje`). **Epic 4.3** må komme før 2.8 for migrasjonsnumrene. **Epic 3**
  pakker hentekommandoen. **Epic 8.1** kommer rett etter Epic 2. **Epic 10**
  bruker målingene fra 2.1c og lager KI-teksten i hentekommandoen fra rundt
  26.10.
