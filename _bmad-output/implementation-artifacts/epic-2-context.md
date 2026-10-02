# Epic 2 Context: Ferske data uten at kvoten sprenges

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren skal kunne hente nye kurser bevisst, og skal ikke ved uhell kunne
brenne dagskvoten på 20 kall. Hentingen er en egen kommando, aldri en bivirkning
av at webserveren startet, og den nekter å hente to ganger samme børsdag.
Epicen tar også databasen fra Epic 1 i bruk: hentekommandoen skriver kursene til
basen (2.1b), vurderingen lagrer målingene bak de tre sjekkene (2.1c), dagens
vurdering skrives i samme kjøring (2.5), og webserveren leser basen (2.2). Fra
2.5 kjøres hentingen hver børsdag mellom kl. 22:00 og midnatt, og hver dag blir
et svar eller en grunn i `vurdering`. Historikken vises i aksjedetaljen (2.7).
Utvidet 01.10 med hovedindeksen OSEBX: den hentes i samme kjøring (2.8), vises
over tabellen i markedsoversikten (2.9), med én søyle per aksje under (2.9b).
Status 02.10: 2.0 er `done`; 2.1, 2.1b og 2.1c er flettet (PR #13, #14, #16) og
står som `review` i sprint-status. Planen for 2.5 fikk ja 02.10. Resten står som
`backlog`.

## Stories

- Story 2.0: Hentingen lekker ikke nøkkelen og skriver ikke over et øyeblikksbilde
- Story 2.1: Børsdag i Oslo, tidsstempel i UTC
- Story 2.1b: Basen åpnes ett sted, og hentingen skriver kursene dit
- Story 2.1c: Vurderingen lagrer målingene bak de tre sjekkene
- Story 2.2: Hentekommandoen som egen inngang
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
  API-kall, også når basen er tom, og viser da en tom tilstand som sier hvordan
  man henter, ikke en feilside. En container startes på nytt hver gang, så en
  henting ved oppstart ville brent kvoten per `docker run`.
- **Kvoten:** 20 kall i døgnet, ett kall per symbol: 15 for aksjene, og 16 når
  indeksen hentes (2.8), så marginen går fra fem til fire. Kall nummer 21
  stopper ikke, men trekker stille fra bonuskvoten. Derfor skal kommandoen
  **nekte** å hente to ganger samme børsdag: en andre kjøring samme børsdag gjør
  null kall, også med indekskallet. Ett kall dekker hele intervallet, så et hull
  i serien koster ikke mer enn en vanlig henting.
- **Når kommandoen kjøres:** børsdager mellom kl. 22:00 og midnatt, norsk tid.
  Siste rad kan endres etter en henting mens børsen er åpen. *Avgjort for 2.3:*
  kommandoen **nekter** før kl. 22:00, med en uttrykkelig overstyring for kjøring
  for hånd, fordi en planlagt jobb ikke kan svare på en advarsel. Før kl. 22:00,
  på en dag som ikke er børsdag, eller når dataene for siste børsdag finnes,
  bruker den null kall og sier hvorfor. Til 2.3 er ferdig, kjøres hentingen for
  hånd. Når 2.3 er flettet, endres FR-401 (planlagt jobb i Oppgaveplanlegging,
  hverdager kl. 22:15), og oppsettet beskrives i README.
- **Kontroll mot forventet børsdag, ikke mot klokkeslett.** Er nyeste dato i
  svaret ikke forventet børsdag, vises siste kjente data med tidsstempel, og
  gårsdagens tall vises aldri som dagens. Kontrollen eies av hentekommandoen og
  regnes i norsk kalenderdato. Ligger den i webserveren, er den pynt.
- **Én kommando gjør hele hentingen:** kurser (og indeksen), så dagens vurdering
  for alle femten, i samme kjøring. Ingen egen migrasjonskommando.
- **Vurderinger etterfylles aldri; kurser gjør det.** Et symbol som feilet, får
  en rad med grunnen, også når nyeste kurs ikke er fra dagen og når signalet
  ikke kan regnes. Ingen rad ville blitt lest som «ikke kjørt».
- **Målingene lagres uavrundet, som brøk:** `trend_avvik`, `dagens_endring`,
  `standardavvik` og `volumforhold` (forholdstall mot medianen). `volumforhold`
  er `None` bare når medianvolumet er 0, og da er interesse 0.
- **Bare tall vi kan stå for:** et tall vises bare når det kommer fra dataene,
  er regnet etter en skrevet regel og har bestått kontrollen. Ellers «–» med
  grunnen, aldri 0, et anslag eller et reservetall.
- **Indeksen er ikke en aksje.** Feiler indekskallet, lagres og vurderes aksjene
  som vanlig; indeksen føres i `feil`, får ingen ny sjanse og gir aldri en rad i
  `vurdering`. Bare børsdager lagres, i årene `DEKKEDE_AAR` dekker, uten fast
  årstall i koden.
- **Universet telles, aldri et fast 15.** Ny kode tar aksjelista som parameter
  og testes også med en kortere liste. «x av N» og antall søyler bruker aksjene
  med kurs for indeksens dato; en aksje som mangler, navngis.
- **Utbyttedager merkes** av kursserien alene, fra avviket mellom endringen i
  `close` og i `adjusted_close`, uten avhengighet til NewsWeb. Kilden er ikke
  endelig valgt; storyen forutsetter den målte veien.
- **Manglende data stopper ikke hovedflyten.** Hver story har en test for den
  tomme eller manglende stien, test uten nett og en «ville feilet hvis»-kontroll
  prøvd med mutanter.
- **Nøkkelen** leses fra miljøet, vises eller lagres aldri, og øyeblikksbilder
  skrives aldri over.
- **Kontrollregning på ekte data** gjøres mot det nyeste øyeblikksbildet, uten
  API-kall og uten å kjøre `fetch_prices.py`, og utfallet føres uten verdiene.
- **Kan ikke kuttes:** 2.1, 2.1b, 2.5, 2.3 og 2.2. Kan kuttes, i denne
  rekkefølgen: 2.6, 2.4 (kontrollpunktet om fire dagers opphold ligger alt i
  2.1b) og 2.7. 2.8, 2.9 og 2.9b står ikke på «kan ikke kuttes»; blir det
  trangt, venter 2.9b først.

## Technical Decisions

- **Nøyaktig én funksjon per kilde rører nettet,** i `fetch_prices.py`, og den
  injiseres. Ingen test kaller den.
- **Tid:** hvilken dag en sluttkurs tilhører, er norsk kalenderdato
  (Europe/Oslo); tidsstempler for når noe ble hentet, er UTC med offset.
  Filnavn, `hentet` og datoen for vurderingen utledes av **samme øyeblikk**
  (`naa()` leses én gang, `kjoer` tar øyeblikket, dagen er
  `boersdag.norsk_dato`). En strengvakt avviser `date.today(`, `datetime.now()`
  og `astimezone()` uten argument i `src/`.
- **Basen åpnes ett sted:** `lagring_sqlite.aapne_base` lager mappa, kobler til
  og kjører `migrer()`; ingen annen kode kaller `sqlite3.connect`. Stiene er
  `RAA_KATALOG` (`data/raa/`) og `BASE_STI` (`data/db/ose.db`), og testene
  peker dem mot `tmp_path`.
- **Kursene skrives** med `erstatt_serie` per hentet symbol, med samme `hentet`
  som øyeblikksbildet; hele serien byttes, den skjøtes aldri. Et symbol som
  feilet, rører ikke serien. `--les-inn <fil>` leser et eksisterende
  øyeblikksbilde inn samme vei, uten kall, og skriver bare `kurs`.
- **Symbolvakten:** `Kurslager` avviser symboler utenfor `AKSJEUNIVERS` med
  `ValueError`; triggerne fra `0003` er vakten i basen. Hvilke feil kjøringen
  fanger fra `SqliteVurderingslager.skriv` (som slipper ut `sqlite3`-feil),
  avgjøres i 2.5.
- **Vurderingen skrives av hentekommandoen,** regnet av radene kjøringen selv
  lagret. Lat skriving ved sidevisning og en egen tredje kommando er forkastet.
  `skriv` er idempotent på `(symbol, dato)` og avviser enhver dato som ikke er
  inneværende børsdag. En kjøring som går over midnatt i Oslo, stopper og sier
  fra. `vurdering` kopierer kurs og målinger som verdier og peker på `aksje`,
  aldri på `kurs`. Vurderingen bygges av `Signal` med målingene fra 2.1c.
- **Målingene (bygget i 2.1c):** fire kolonner fra `0004`, lagt til med
  `ADD COLUMN` og CHECK, uten `DROP TABLE`. `Sjekk` har `maaling` og `grense`.
  Én funksjon avrunder, i `tallformat.py`: én desimal for prosent, to for
  forholdstallet. Kolonnene står i `VURDERINGSKOLONNER`.
- **Migrasjonsrekkefølgen:** `ki_logg` er `0005` (4.3), indeksen `0006` (2.8).
  Blir 4.3 utsatt, tas den før 2.8.
- **Indeksen** lagres i egen tabell `indeks`, aldri i `aksje`, `kurs`,
  `kursserie` eller `vurdering`, og står ikke i `AKSJEUNIVERS`. Rådata står i
  samme øyeblikksbilde som aksjene, under en egen nøkkel.
- **Webserveren mot basen (2.2):** `aapne_base` og `migrer()` én gang ved
  oppstart, fordi `migrer()` alltid tar skrivelås. Deretter én tilkobling per
  forespørsel, lukket etterpå, fordi Flask kjører forespørsler i egne tråder og
  en `sqlite3`-tilkobling ikke kan deles mellom tråder. Spørsmål til planen:
  kan oversikten hente de femten fra `aksje` med nyeste kurs i én join, og skal
  den lese dagens vurdering fra `vurdering` i stedet for å regne signalet ved
  hver visning?
- **Historikken (2.7)** leses gjennom en ny lesemetode for en periode på
  `Vurderingslager`, uten slette- eller endremetode, og hver dag går gjennom
  `tilstand`. Den regnes aldri ut på nytt av kursene.
- **Låste signalparametre** endres ikke uten ny måling.

## UX & Interaction Patterns

- Webserveren viser siste kjente data med tidsstempel, i norsk tid. Tom base gir
  en tom tilstand med beskjed om hvordan man henter; meldingen «Ingen kursdata
  funnet i `data/`» skal bort, og «Kom i gang» i README rettes i samme commit.
- Tall på sidene skrives norsk: desimalkomma, hardt mellomrom som tusenskille og
  foran %, vanlig bindestrek som minus. Avrunding skjer bare ved visning.
- **Hovedindeksen (2.9):** over tabellen «Hovedindeksen» med OSEBX, verdien,
  dagens endring og «x av N gikk bedre enn indeksen». Tabellen har fortsatt fem
  kolonner. Endringen regnes mot forrige børsdag, ikke forrige rad. «Bedre»
  avgjøres på endringen slik den vises, og lik er ikke bedre. Uten indeks vises
  det, og resten av siden virker.
- **Søylene (2.9b):** én per aksje, fra størst fall til størst stigning, med
  bransjesymbol over tickeren. Indeksens endring er en stiplet linje, grønn når
  den steg og rød når den falt. Skjermleserteksten har alle tallene.
  Bransjesymbolene ligger i malen, ikke på nettet. Gult bransjesymbol betyr 3 av
  3 på siste børsdag. Bare dagens søyler; perioder og «Velg dag» er v1.1.
  Fargegrensene avgjøres i spesifikasjonen og føres i `designregler.md`.
- **Historikken (2.7):** de siste fire ukene dag for dag: styrke og retning,
  eller grunnen, «ikke kjørt» eller «ikke børsdag», med målingene avrundet som i
  begrunnelsen. Styrke 0, en grunn og en manglende rad ser aldri like ut, og
  dagens rad som ikke er skrevet ennå, vises ikke som et hull. Malene deler én
  layout og én CSS-fil.
- En utbyttedag merkes i markedsoversikten, så avviket mellom vist kurs og vist
  prosent ikke ser ut som en feil.
- All brukervendt tekst er på norsk, og ingenting skal kunne leses som et
  investeringsråd.

## Cross-Story Dependencies

- **Rekkefølgen:** 2.1 → 2.1b → 2.1c → 2.5, så begynner de daglige kjøringene
  til basen. Deretter 2.3, 2.8 (etter 4.3), 2.2, 2.9, 2.9b, 2.7, 2.4 og 2.6. De
  daglige kjøringene venter ikke på 2.8.
- 2.7 avhenger av 2.2 og 2.5. 2.8 avhenger av 2.3 og 4.3. 2.9 avhenger av 2.2 og
  2.8, og 2.9b av 2.9. 2.8 utvider testen i 2.3 med indekskallet, og retter
  «15 kall» i README og spinen til 16 i samme commit.
- **Epic 1 er forutsetningen:** hentingen skriver gjennom `Kurslager` og
  `Vurderingslager`, bruker `tilstand`, og `aksje` (1.9) er på plass.
- **Epic 4.3** (SQLite-adapter for `KILogg`) bruker samme `aapne_base` og må
  komme før 2.8 for migrasjonsnumrene.
- **Epic 3** pakker bare: hentekommandoen må finnes før Dockerfilen kan pakke
  den, og migrasjonene kjøres av `aapne_base` uten eget kommandosteg.
- **Epic 8.1** (brukertesten) kommer rett etter Epic 2, med ekte data i
  historikken.
- **Epic 10.1–10.2** bruker målingene og avrundingen fra 2.1c, og 10.2 lager
  KI-teksten i hentekommandoen, daglig fra rundt 26.10.
