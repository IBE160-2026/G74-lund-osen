# Epic 2 Context: Ferske data uten at kvoten sprenges

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren skal kunne hente nye kurser bevisst, og skal ikke ved uhell kunne
brenne dagskvoten på 20 kall. Hentingen er en egen kommando, aldri en bivirkning
av at webserveren startet, og den nekter å hente to ganger samme børsdag.
*Utvidet 2026-09-28 (endringsforslaget):* epicen tar også databasen fra Epic 1 i
bruk. Hentekommandoen skriver kursene til basen (2.1b), vurderingen lagrer
målingene bak de tre sjekkene (2.1c, lagt til 29.09), dagens vurdering skrives i
samme kjøring (2.5), og webserveren leser basen i stedet for øyeblikksbildene
(2.2). Fra 2.5 kan hentingen kjøres hver børsdag mellom kl. 22:00 og midnatt, og
hver dag blir et svar eller en grunn i `vurdering`. Historikken vises i
aksjedetaljen (2.7). Epic 1 er ferdig (1.9 i `cfe2977`). 2.0 er flettet i
`4b65a3c` (PR #6), og 2.1 er ferdig og flettet i `27ae8e3` (PR #13); i
sprint-status står 2.1 i `review`. Resten står som `backlog`, og 2.1b er neste.

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
- **Kontroll mot forventet børsdag, ikke mot klokkeslett.** Er nyeste dato i
  svaret ikke forventet børsdag, vises siste kjente data med tidsstempel, og
  gårsdagens tall vises aldri som dagens. Kontrollen eies av hentekommandoen og
  regnes i norsk kalenderdato. Ligger den i webserveren, er den pynt.
- **Når kommandoen kjøres** (punkt 23, avgjort 28.09): på børsdager mellom
  kl. 22:00 og midnatt, norsk tid. En kjøring som kommer for tidlig, bruker
  dagens kall uten å få dagens rad, og vernet fra 2.0 stopper da kveldens
  kjøring, så dagen får en grunn og ikke en vurdering. Om 2.3 advarer eller
  nekter før kl. 22:00, avgjøres i planen for 2.3; endringsforslaget taler for å
  nekte, med en uttrykkelig overstyring. Til 2.3 er ferdig, kjøres hentingen for
  hånd, bare på børsdager og bare i vinduet.
- **Én kommando gjør hele hentingen:** kurser, så dagens vurdering for alle
  femten, i samme kjøring. Migrasjoner er uttrykkelig ikke et eget steg.
- **Vurderinger etterfylles aldri; kurser gjør det.** Et symbol som feilet, får
  en rad med grunnen, også når nyeste kurs ikke er fra dagen og når signalet
  ikke kan regnes. Ingen rad ville blitt lest som «ikke kjørt».
- **Målingene lagres uavrundet, som brøk** (2.1c): `trend_avvik`,
  `dagens_endring`, `standardavvik` og `volumforhold` (volum som forholdstall
  mot medianen). `volumforhold` mangler bare når medianvolumet er 0, og da er
  interesse 0. Én funksjon avrunder for visning: én desimal for prosent, to for
  forholdstallet. 2.1c må være ferdig før den første ekte raden skrives.
- **Utbyttedager merkes** (FR-407) av kursserien alene, fra avviket mellom
  endringen i `close` og i `adjusted_close`, uten avhengighet til NewsWeb.
  Kilden er ikke endelig valgt (åpent punkt 4); storyen forutsetter den målte
  veien.
- **Manglende data stopper ikke hovedflyten.** Hver story har en test for den
  tomme eller manglende stien, og hver story leveres med test uten nett og en
  «ville feilet hvis»-kontroll.
- **Nøkkelen** leses fra miljøet, vises eller lagres aldri, og øyeblikksbilder
  skrives aldri over (2.0, ferdig).
- **Kontrollregning på ekte data** gjøres mot et øyeblikksbilde som finnes,
  uten API-kall, og utfallet føres som antall like rader, ikke som verdiene.
- **Kan ikke kuttes:** 2.1, 2.1b, 2.5, 2.3 og 2.2. Kan kuttes, i denne
  rekkefølgen: 2.6, 2.4 (kontrollpunktet om fire dagers opphold ligger alt i
  2.1b), og til sist 2.7.

## Technical Decisions

- **Nøyaktig én funksjon per kilde rører nettet,** i skallet
  (`fetch_prices.py`), og den injiseres. Ingen test kaller den.
- **Tid (AD-20):** hvilken dag en sluttkurs tilhører, er norsk kalenderdato
  (Europe/Oslo); tidsstempler for når noe ble hentet, er UTC med offset.
  Filnavn, `hentet` og datoen for vurderingen utledes av **samme øyeblikk**. Å
  gjøre verdiene konsistente uten å si hvilken sone de er i, er forkastet.
  *Bygget i 2.1:* `fetch_prices.main` leser klokka én gang, i UTC (`naa()`), og
  `kjoer` tar øyeblikket. Dagen i filnavnet og intervallet er
  `boersdag.norsk_dato`, og `hentet` er øyeblikket i UTC med offset, altså
  starten på kjøringen. `meldinger._minutt` parser med `fromisoformat`, krever
  sone og regner om til UTC. En strengvakt i `tests/test_tidssone.py` avviser
  `date.today(`, `datetime.now()` og `astimezone()` uten argument i hele `src/`,
  så ny kode i 2.1b–2.5 må ta øyeblikket inn, ikke lese klokka selv.
- **Mappene:** øyeblikksbildene i `data/raa/`, basen i `data/db/ose.db`, faste
  stier under prosjektroten (ingen sti fra miljøet i v1). Testene peker stiene
  mot `tmp_path` med `monkeypatch`. `kurser-raa-*.json` flyttes for hånd fra
  `data/` til `data/raa/`, utenfor git.
- **Én funksjon åpner basen** (2.1b): lager mappa, kobler til og kjører
  `migrer()`. Både hentekommandoen og webserveren bruker den. Webserveren kjører
  den én gang ved oppstart, ikke per forespørsel, fordi `migrer()` alltid tar
  skrivelås. Deretter én tilkobling per forespørsel, lukket etterpå, fordi Flask
  kjører forespørsler i egne tråder og en `sqlite3`-tilkobling ikke kan deles
  mellom tråder. Testen der to migratorer overlapper, tas i 2.1b.
- **`erstatt_serie(symbol, rader, hentet)`** erstatter hele serien i én
  transaksjon, med samme `hentet` som øyeblikksbildet. Et symbol som feilet,
  rører ikke serien sin. Et eksisterende øyeblikksbilde kan skrives til basen
  uten API-kall, samme vei, men bare `kurs`, aldri `vurdering`. Om et
  øyeblikksbilde eldre enn serien i basen avvises, avgjøres i planen for 2.1b.
- **Symbolvakten:** `0003` avviser et ukjent symbol i basen, og
  `SqliteKurslager` gjør det om til `ValueError`, mens `MinneKurslager` godtar
  `EQNR.OL`. Om porten `Kurslager` selv skal sjekke symbolet, avgjøres i 2.1b.
  At `SqliteVurderingslager.skriv` slipper ut `sqlite3`-feil, og hvilke feil
  kjøringen fanger, avgjøres i 2.5.
- **Vurderingen skrives av hentekommandoen** (AD-17), regnet av radene
  kjøringen selv lagret. Lat skriving ved sidevisning og en egen tredje kommando
  er forkastet, fordi grunnlaget da kan være byttet ut. `skriv` er idempotent på
  `(symbol, dato)` og avviser enhver dato som ikke er inneværende børsdag.
  Datoen regnes én gang; en kjøring som går over midnatt i Oslo, stopper og
  sier fra i stedet for å få `ValueError` midt i universet.
- **Skjemaendringen i 2.1c:** `0004_maalinger.sql` legger fire kolonner til
  `vurdering` med `ADD COLUMN` og en `CHECK` i hver kolonne, uten `DROP TABLE`,
  med en kommentar om enheten. En hjelpetabell som `kontroll_0003` stopper
  migrasjonen hvis det finnes vurderingsrader uten grunn. `Sjekk` får `maaling`
  og `grense`; `Vurdering` kontrollerer verdiene, men ikke fortegnet mot
  målingen. Kolonnene står i `VURDERINGSKOLONNER`. `ki_logg` blir `0005`.
- **`vurdering` kopierer kurs og målinger som verdier** og peker på `aksje`,
  aldri på `kurs`.
- **Historikken (2.7)** leses gjennom en ny lesemetode for en periode på
  `Vurderingslager`, uten slette- eller endremetode, og hver dag går gjennom
  `tilstand`. Den regnes aldri ut på nytt av kursene.
- **Spørsmål til planen for 2.2:** kan oversikten hente de femten fra `aksje`
  sammen med nyeste kurs i én spørring (gruppen vil ha minst én join appen
  bruker, og en join mot `aksje` i 2.7 bare for navnet teller ikke)? Og skal
  oversikten lese dagens vurdering fra `vurdering` i stedet for å regne signalet
  ved hver visning?
- **Låste signalparametre** endres ikke uten ny måling.

## UX & Interaction Patterns

- Webserveren viser alltid siste kjente data med tidsstempel, i norsk tid.
  Tom base gir en tom tilstand med beskjed om hvordan man henter. Meldingen
  «Ingen kursdata funnet i `data/`» skal bort, og «Kom i gang» i README rettes i
  samme commit (2.2).
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

- **Rekkefølgen:** 2.1 (ferdig) → 2.1b → 2.1c → 2.5, så begynner de daglige
  kjøringene til basen. Deretter 2.3, 2.2, 2.7, 2.4 og 2.6. 2.1b avhenger av
  2.1, 2.1c av 2.1b, og 2.7 av 2.2 og 2.5. 2.5 regner datoen for vurderingen fra
  det samme øyeblikket som 2.1 innførte i `kjoer`.
- **Epic 1 er forutsetningen:** hentingen skriver gjennom `Kurslager` og
  `Vurderingslager`, bruker `kursrad_fra_eodhd` og `tilstand`, og `aksje`
  (1.9) er på plass før Epic 2 skriver til basen.
- **2.1c før første ekte rad:** en vurdering kan aldri endres eller fylles inn
  etterpå. Finnes det vurderingsrader uten grunn i basen, stopper `0004`, og
  gruppen avgjør hva som skjer med dem før 2.1c flettes.
- **Epic 4.3** (SQLite-adapter for `KILogg`) bruker samme åpning av basen og kan
  tas når 2.1b er ferdig, etter 4.2.
- **Epic 3** pakker bare: 3.1 får migrasjonene uten eget kommandosteg fra
  åpningen i 2.1b, og monterer `ose-raa` og `ose-db` på `data/raa/` og
  `data/db/`. Hentekommandoen må finnes før Dockerfilen kan pakke den.
- **Epic 8.1** (brukertesten) kommer rett etter Epic 2, med ekte data i
  historikken fra uke 40 og 41.
- **Epic 10.2** lager KI-teksten i hentekommandoen og lagrer den i `KILogg`,
  daglig fra rundt 26.10.
