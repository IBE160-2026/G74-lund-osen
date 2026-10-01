# Epic 2 Context: Ferske data uten at kvoten sprenges

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren skal kunne hente nye kurser bevisst, og skal ikke ved uhell kunne
brenne dagskvoten på 20 kall. Hentingen er en egen kommando, aldri en bivirkning
av at webserveren startet, og den nekter å hente to ganger samme børsdag.
Epicen tar også databasen fra Epic 1 i bruk: hentekommandoen skriver kursene til
basen (2.1b), vurderingen lagrer målingene bak de tre sjekkene (2.1c), dagens
vurdering skrives i samme kjøring (2.5), og webserveren leser basen i stedet for
øyeblikksbildene (2.2). Fra 2.5 kan hentingen kjøres hver børsdag mellom
kl. 22:00 og midnatt, og hver dag blir et svar eller en grunn i `vurdering`.
Historikken vises i aksjedetaljen (2.7). Status 01.10: 2.0 er flettet i
`4b65a3c` (PR #6), 2.1 i `27ae8e3` (PR #13) og 2.1b i `9aa6131` (PR #14); 2.1 og
2.1b står som `review` i sprint-status. Planen for 2.1c fikk ja 01.10 og bygges
nå. Resten står som `backlog`.

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

## Requirements & Constraints

- **Henting utløses eksplisitt, aldri av en oppstart.** Webserveren bruker null
  API-kall, også når basen er tom, og viser da en tom tilstand som sier hvordan
  man henter, ikke en feilside. En container startes på nytt hver gang, så en
  henting ved oppstart ville brukt 15 kall per `docker run`.
- **Kvoten:** 20 kall i døgnet, 15 til kursene, fem i margin. Kall nummer 21
  stopper ikke, men trekker stille fra bonuskvoten. Derfor skal kommandoen
  **nekte** å hente to ganger samme børsdag, ikke bare unngå det: en andre
  kjøring samme børsdag gjør null kall. Ett kall per symbol dekker hele
  intervallet, så et hull i serien koster 15 kall uansett lengde.
- **Når kommandoen kjøres:** på børsdager mellom kl. 22:00 og midnatt, norsk
  tid. Siste rad kan endres etter en henting mens børsen er åpen, og en kjøring
  som kommer for tidlig, bruker dagens kall uten å få dagens rad; vernet fra 2.0
  stopper da kveldens kjøring, og dagen får en grunn, ikke en vurdering.
  *Avgjort for 2.3:* kommandoen **nekter** før kl. 22:00, med en uttrykkelig
  overstyring for kjøring for hånd, fordi en planlagt jobb ikke kan svare på en
  advarsel. Før kl. 22:00, på en dag som ikke er børsdag, eller når dataene for
  siste børsdag finnes, bruker den null kall og sier hvorfor. Til 2.3 er ferdig,
  kjøres hentingen for hånd, bare på børsdager og bare i vinduet. Når 2.3 er
  flettet, endres FR-401, og oppsettet i Oppgaveplanlegging beskrives i README.
- **Kontroll mot forventet børsdag, ikke mot klokkeslett.** Er nyeste dato i
  svaret ikke forventet børsdag, vises siste kjente data med tidsstempel, og
  gårsdagens tall vises aldri som dagens. Kontrollen eies av hentekommandoen og
  regnes i norsk kalenderdato. Ligger den i webserveren, er den pynt.
- **Én kommando gjør hele hentingen:** kurser, så dagens vurdering for alle
  femten, i samme kjøring. Migrasjoner er uttrykkelig ikke et eget steg.
- **Vurderinger etterfylles aldri; kurser gjør det.** Et symbol som feilet, får
  en rad med grunnen, også når nyeste kurs ikke er fra dagen og når signalet
  ikke kan regnes. Ingen rad ville blitt lest som «ikke kjørt».
- **Målingene lagres uavrundet, som brøk** (2.1c): `trend_avvik`,
  `dagens_endring`, `standardavvik` og `volumforhold` (volum som forholdstall
  mot medianen, ikke to volumtall). Regelen for interesse avgjør med
  forholdstallet, så det lagrede tallet er det som avgjorde. `volumforhold` er
  `None` bare når medianvolumet er 0, og da er interesse 0. 2.1c må være ferdig
  før den første ekte raden skrives.
- **Bare tall vi kan stå for** (NFR-08): et tall vises bare når det kommer fra
  dataene, er regnet etter en skrevet regel og har bestått kontrollen. Mangler
  det, vises «–» med grunnen, aldri 0, et anslag eller et reservetall. For
  manglende `volumforhold` er teksten «–, medianvolumet de 20 dagene før er 0»,
  der tallet hentes fra `volum_vindu` i parametrene, ikke skrives inn for hånd.
- **Utbyttedager merkes** (FR-407) av kursserien alene, fra avviket mellom
  endringen i `close` og i `adjusted_close`, uten avhengighet til NewsWeb.
  Kilden er ikke endelig valgt (åpent punkt 4); storyen forutsetter den målte
  veien.
- **Manglende data stopper ikke hovedflyten.** Hver story har en test for den
  tomme eller manglende stien, og hver story leveres med test uten nett og en
  «ville feilet hvis»-kontroll, med mutanter lagt inn én om gangen.
- **Nøkkelen** leses fra miljøet, vises eller lagres aldri, og øyeblikksbilder
  skrives aldri over (2.0).
- **Kontrollregning på ekte data** gjøres mot det nyeste øyeblikksbildet i
  `data/raa/`, uten API-kall og uten å kjøre `fetch_prices.py`, og utfallet
  føres som symboler og om de er like, ikke som verdiene.
- **Kan ikke kuttes:** 2.1, 2.1b, 2.5, 2.3 og 2.2. Kan kuttes, i denne
  rekkefølgen: 2.6, 2.4 (kontrollpunktet om fire dagers opphold ligger alt i
  2.1b), og til sist 2.7.

## Technical Decisions

- **Nøyaktig én funksjon per kilde rører nettet,** i skallet
  (`fetch_prices.py`), og den injiseres. Ingen test kaller den.
- **Tid (AD-20):** hvilken dag en sluttkurs tilhører, er norsk kalenderdato
  (Europe/Oslo); tidsstempler for når noe ble hentet, er UTC med offset.
  Filnavn, `hentet` og datoen for vurderingen utledes av **samme øyeblikk**.
  `fetch_prices.main` leser klokka én gang (`naa()`), og `kjoer` tar øyeblikket;
  dagen er `boersdag.norsk_dato`. En strengvakt i `tests/test_tidssone.py`
  avviser `date.today(`, `datetime.now()` og `astimezone()` uten argument i hele
  `src/`, så ny kode må ta øyeblikket inn, ikke lese klokka selv.
- **Basen og mappene (bygget i 2.1b):** øyeblikksbildene i `RAA_KATALOG`
  (`data/raa/`), basen i `BASE_STI` (`data/db/ose.db`), faste stier, slått opp
  når funksjonen kalles. `aapne_base` i `lagring_sqlite.py` er eneste sted som
  kobler til: lager mappa, kobler til og kjører `migrer()`. En vakt sikrer at
  `sqlite3.connect` bare står der. `kjoer` tar `base_sti` som påkrevd argument,
  og en autouse-fixture i `tests/conftest.py` peker stiene mot `tmp_path`, så
  ingen test rører `data/`.
- **Skrivingen av kurser (2.1b):** `erstatt_serie` for hvert hentet symbol, med
  samme `hentet` som øyeblikksbildet, etter at fila er skrevet. Et symbol som
  feilet, rører ikke serien. Et øyeblikksbilde eldre enn `sist_hentet(symbol)`
  hoppes over for det symbolet med melding, og kjøringen ender med kode 1.
  `fetch_prices.py --les-inn <fil>` leser et eksisterende øyeblikksbilde inn
  samme vei, uten kall og uten nøkkel, og skriver bare `kurs`, aldri
  `vurdering`.
- **Symbolvakten:** porten `Kurslager` avviser symboler utenfor `AKSJEUNIVERS`
  med `ValueError` før noe lagres, så minne- og SQLite-lageret oppfører seg likt;
  triggerne fra `0003` står som vakt i basen. At `SqliteVurderingslager.skriv`
  slipper ut `sqlite3`-feil, og hvilke feil kjøringen fanger, avgjøres i 2.5.
- **Webserveren mot basen (2.2):** samme `aapne_base`, `migrer()` én gang ved
  oppstart, ikke per forespørsel, fordi den alltid tar skrivelås. Deretter én
  tilkobling per forespørsel, lukket etterpå, fordi Flask kjører forespørsler i
  egne tråder og en `sqlite3`-tilkobling ikke kan deles mellom tråder.
  Ventetiden ved samtidige kallere avgjøres her. Spørsmål til planen: kan
  oversikten hente de femten fra `aksje` sammen med nyeste kurs i én spørring
  (gruppen vil ha minst én join appen bruker), og skal oversikten lese dagens
  vurdering fra `vurdering` i stedet for å regne signalet ved hver visning?
- **Skjemaendringen i 2.1c:** `0004_maalinger.sql` legger fire kolonner til
  `vurdering` med `ADD COLUMN`, uten `DROP TABLE`, med en kommentar om enheten
  (brøk) for hver. CHECK-ene: en vurdering har alle fire, bortsett fra at
  `volumforhold` kan mangle når interesse er 0; en rad med grunn har ingen;
  `standardavvik >= 0` og `volumforhold >= 0`. En hjelpetabell som
  `kontroll_0003` stopper migrasjonen hvis det finnes vurderingsrader uten grunn.
  `ki_logg` blir `0005`.
- **Kjernen og porten i 2.1c:** `Sjekk` får `maaling` og `grense`, og
  `forklaring` lages av dem; teksten for interesse blir forholdstallet. Én
  funksjon avrunder: tallfunksjonen i `tallformat.py` (regel 21), brukt av
  visningen, grunnlaget i 10.1 og kontrollen i FR-603, med én desimal for
  prosent og to for forholdstallet. `Vurdering` kontrollerer verdiene (endelige
  tall, ikke-negative, `None` bare ved interesse 0), men ikke fortegnet mot
  målingen. Kolonnene står i `VURDERINGSKOLONNER`. 2.5 lager en `Vurdering` av
  et `Signal`; 2.1c har bare rundturtesten.
- **Vurderingen skrives av hentekommandoen** (AD-17), regnet av radene
  kjøringen selv lagret. Lat skriving ved sidevisning og en egen tredje kommando
  er forkastet, fordi grunnlaget da kan være byttet ut. `skriv` er idempotent på
  `(symbol, dato)` og avviser enhver dato som ikke er inneværende børsdag.
  Datoen regnes én gang; en kjøring som går over midnatt i Oslo, stopper og
  sier fra. `vurdering` kopierer kurs og målinger som verdier og peker på
  `aksje`, aldri på `kurs`.
- **Historikken (2.7)** leses gjennom en ny lesemetode for en periode på
  `Vurderingslager`, uten slette- eller endremetode, og hver dag går gjennom
  `tilstand`. Den regnes aldri ut på nytt av kursene.
- **Låste signalparametre** endres ikke uten ny måling.

## UX & Interaction Patterns

- Webserveren viser alltid siste kjente data med tidsstempel, i norsk tid.
  Tom base gir en tom tilstand med beskjed om hvordan man henter. Meldingen
  «Ingen kursdata funnet i `data/`» skal bort, og «Kom i gang» i README rettes i
  samme commit (2.2).
- Tall på sidene skrives norsk: desimalkomma, hardt mellomrom som tusenskille og
  foran %, og vanlig bindestrek som minus. Avrunding skjer bare ved visning.
- Historikken i aksjedetaljen viser de siste fire ukene dag for dag: styrke og
  retning, eller grunnen, «ikke kjørt» eller «ikke børsdag», med målingene
  avrundet som i FR-706. Styrke 0, en grunn og en manglende rad ser aldri like
  ut, og dagens rad som ikke er skrevet ennå, vises ikke som et hull. Malene
  deler én layout og én CSS-fil.
- En utbyttedag merkes i markedsoversikten, så avviket mellom vist kurs og vist
  prosent ikke ser ut som en feil.
- All brukervendt tekst er på norsk, og ingen formulering skal kunne leses som
  et investeringsråd.

## Cross-Story Dependencies

- **Rekkefølgen:** 2.1 → 2.1b → 2.1c → 2.5, så begynner de daglige kjøringene
  til basen. Deretter 2.3, 2.2, 2.7, 2.4 og 2.6. 2.7 avhenger av 2.2 og 2.5.
  2.5 regner datoen for vurderingen fra det samme øyeblikket som 2.1 innførte i
  `kjoer`, og bygger vurderingen med målingene fra 2.1c.
- **Epic 1 er forutsetningen:** hentingen skriver gjennom `Kurslager` og
  `Vurderingslager`, bruker `kursrad_fra_eodhd` og `tilstand`, og `aksje` (1.9)
  er på plass.
- **2.1c før første ekte rad:** en vurdering kan aldri endres eller fylles inn
  etterpå. Basen på PC-en hadde 0 vurderingsrader uten grunn 01.10, så `0004`
  stopper ikke der.
- **Story 8.0** eier tallfunksjonen i `tallformat.py`; 2.1c bruker den, og tre
  tester fra 8.0 for den gamle interesseteksten byttes ut i 2.1c.
- **Epic 4.3** (SQLite-adapter for `KILogg`) bruker samme `aapne_base` og kan
  tas nå som 2.1b er ferdig, etter 4.2.
- **Epic 3** pakker bare: 3.1 får migrasjonene fra `aapne_base` uten eget
  kommandosteg, og monterer `ose-raa` og `ose-db` på `data/raa/` og `data/db/`.
  Hentekommandoen må finnes før Dockerfilen kan pakke den.
- **Epic 8.1** (brukertesten) kommer rett etter Epic 2, med ekte data i
  historikken.
- **Epic 10.1–10.2** bruker målingene og avrundingen fra 2.1c i grunnlaget, og
  10.2 lager KI-teksten i hentekommandoen og lagrer den i `KILogg`, daglig fra
  rundt 26.10.
