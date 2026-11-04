---
title: 'Story 8.2 (8.2b): 29 funn fra UX-loggen'
type: 'bugfix'
created: '2026-11-03'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: 'a6d59bb'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-10-13.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

## Intent

**Problem:** 38 av de 45 funnene til 8.2 i `docs/ux-logg.md` var ikke løst da statusen ble sjekket 03.11 («Status for funnene til 8.2, sjekket 03.11»). Gruppen valgte 29 av dem kl. 22:01.

**Grunnlaget:** gruppens svar 03.11 kl. 22:01, ført under story 8.2 i `epics.md` («Avgjort 2026-11-03 kl. 22:01») i `a90dded`, og instruksjonen kl. 22:44 i `docs/ai-prompts/2026-11-03.md` (`5910928`). Bygges i natt på egen gren og PR, én commit per gruppe a–d, og flettes etter bildene. Grunnen for de 9 som står, er ført i UX-loggen i `a90dded`.

- a) Oversikten: U20, U21, U22, U24, U25, U26, U29 og U57.
- b) Aksjesiden, småting: U2, U6, U16, U31, U37, U39, U41, U44, U47 og U65.
- c) Aksjesiden som på designtavla: U33, U46, U62, U63, U64, U66, U67 og U68.
- d) Forsiden og Min liste som på tavla: U58, U59 og U69.

Regelen i instruksjonen: strider et funn mot en avgjørelse som er ført, eller sier tavla og utdraget forskjellig, bygges det ikke, men står som spørsmål til gruppen under «Åpent», og resten bygges. Ingen ny KI-tekst, intet om kjøp eller salg, og retningen med tekst, symbol og farge (FR-103).

## Slått opp 03.11 på `a6d59bb` (regel 3)

Funnene og statusen i `docs/ux-logg.md`, designutdraget (`designutdrag-2026-10-13.md` §1–§14), `designregler.md` §2–§5, FR-101–FR-107 i `prd.md`, spesifikasjonene for 8.0d, 8.0e, 8.2a, 8.3, 8.6b, 8.16, 8.17a og 8.17b, malene, `stil.css`, `app.py`, `aksjedetalj.py`, `graf.py`, `ki_visning.py`, `hjelpetekster.py` og `docs/hjelp.md`. Det som avgjør hva som bygges:

- **FR-105:** «Over hver søyle står bransjesymbolet, over tickeren.» Tavla har dem under søylene (U57).
- **`designregler.md` §5, tillegget 17.10 (2.9b):** søylenes farge følger fortegnet, og «Det er de eneste fargegrensene: lengden på søylen viser hvor stor endringen er». Tavla har lys og mørk farge etter størrelsen (U57).
- **8.0d, beslutning 2 (avvik 7):** ingen vinkel etter selskapsnavnet. **`designregler.md` §5, tillegget 14.10:** «Under kolonnenavnene står bare «NOK» under Sluttkurs». **8.0e, PR 1:** T, B og I står under «N av 3». Alle tre delene av U58 strider mot dette.
- **Utdraget §8:** «Navnene på kurslinja og snittet står ved enden av linjene, i linjefargen.» U65 sier selv at notatet fra tavla har navnene i en forklaring over grafen. Tavla og utdraget sier forskjellig.
- **`designregler.md` §3 og §4:** gult ved en aksje betyr bare 3 av 3, og 8.0d byttet det gule demobanneret av samme grunn (utdraget §13 punkt 4, beslutning 6). Den gule bryteren på tavla (U33, U67) strider mot det.
- **`designregler.md` §5, «Stripa øverst»:** stripa har ingen knapper før sidene de viser til, finnes (8.3, 8.9 og 8.10). Bryteren i stripa på tavla (U46) er et valg for hele appen, som Innstillinger (8.10).
- **Utdraget §11 og `designregler.md` §5, «Rekkefølgen av delene»:** aksjesiden har nøkkeltallene, sjekkene, kursgrafen, «Se nærmere», KI-teksten og historikken, og delene fra senere stories settes inn på sin plass. U66 følger det. FR-602 (KI-teksten under regelforklaringen) holder også med KI-teksten etter grafen.
- **8.0d, beslutning 7:** «Innledningen fra tavla venter.» U62 er den.
- **`designregler.md` §4:** «Retning forklares med tall … På aksjesiden står sjekkene med navn: «Trend ga +1. Bevegelse og interesse ga -1.»» (U63), og «I KI-teksten har tall som er sjekket mot grunnlaget, prikket strek i tekstfargen» (rettet 13.10, svar 7) (U67).
- **8.3, «Avgjort i spesifikasjonen»:** «Min liste viser ikke overskriften med tall …». Det er et valg i spesifikasjonen, ikke et svar fra gruppen, og svaret kl. 22:01 tar U69, som endrer det.
- **Svar 21 og 29 i 8.0d (kommentaren i `aksje.html`):** kortet Endring har ukedagene, og datoene når det ligger en børsdag mellom. U31 legger datoene til også ellers. Ukedagene står, så det strider ikke.
- **Jobben** (`fetch_prices.py`) importerer, direkte og gjennom andre: `boersdag`, `dagene`, `eodhd`, `hovedindeks`, `indeksdata`, `ki_*` (utenom `ki_visning`), `kilogg`, `kursdata`, `lagring_fil`, `lagring_sqlite`, `markedsoversikt`, `migrering`, `minliste`, `omsetning`, `oversiktsdata`, `perioder`, `signalberegning`, `tallformat`, `tilstand` og `vurderingsdata` (lest med `ast` 03.11). Planen endrer ingen av dem.

## Kontrollpunktene

**a) Oversikten**

- U20 og U57 (delvis): tickerne over søylene er større (13 px) og står vannrett når det er plass, i et vindu bredere enn 760 px. På smal skjerm står de på høykant som før, så 15 søyler får plass ved 390 px.
- U21: feltet med søylene er høyere, 200 px.
- U22: den stiplede linja er 3 px.
- U57 (delvis): under søylene står en forklaring av den stiplede linja: «Stiplet linje: hovedindeksen» med endringen.
- U24: i «Slik leser du tabellen» står hver setning på egen linje, uten større linjeavstand.
- U25: symbolene i kortet er større: +1 og -1 12 px, pilene 16 px og musepekeren 22 px, i det samme feltet på 36 × 36 px.
- U26: hjelpen for hovedindeksen og for søylene er to vinduer, med hvert sitt «?»: ved «Hovedindeksen» og ved overskriften over søylene. Hver tekst er kortere.
- U29: tas aksjen ut av Min liste (uten «Alle»), sender stjernen tilbake til tabellen (`#aksjene`), fordi raden er borte. Ellers til raden som før.
- *Rettet 04.11 kl. 00:15:* tickeren står vannrett fra 900 px, ikke fra 760 px. Ved 761 px er det 44 px per søyle til en ticker på fem tegn i 13 px, og det er for trangt. Ved 900 px er det 53 px. Når tickeren står vannrett i appen (U57), står den fortsatt over søylene (spørsmål 1).

**b) Aksjesiden, småting**

- U2: på aksjesiden er «Markedsoversikt» i stripa merket som delen siden hører til: kant, ikke fyll, og `aria-current="true"`, ikke `"page"`.
- U6: i demoen sier KI-delen for en tidligere dag «Ingen KI-tekst for denne dagen: demoen har KI-tekst bare for siste børsdag.» Den ekte versjonen har teksten som før.
- U16: ingressen i «Signalet dag for dag» er kortere og uten «lest fra basen og aldri regnet på nytt» og «signalstyrke 2 eller mer». Det som er tatt ut, står i hjelpen ved «?».
- U31: kortet Endring har alltid ukedagen og datoen: «fra fredag 09.10 til mandag 12.10».
- U37: periodeknappene og «Velg dag» er like høye, med teksten midtstilt.
- U39: når kursserien begynner etter startdagen, sier overskriften over grafen «Kursutvikling fra <første dag> til <siste dag>», ikke «6 måneder fram til».
- U41 og U47: grafen har et felt til høyre der navnene står, ved enden av linjene og i linjefargen (utdraget §8), og et felt til venstre og nederst for tallene og datoene, så linjene ikke krysser tekstene. Den stiplede linja har navnet «Hovedindeksen» ved enden, i Dempet.
- U44: pilene til forrige og neste måned er knapper med kant, minst 44 px høye, ikke understreket tekst.
- U65: ikke bygget (spørsmål 4). U41 og U47 dekker det utdraget sier.

**c) Aksjesiden som på designtavla**

- U33 og U46 (delvis) og U67 (delvis): bryteren står inne i KI-rammen øverst til høyre, som en bryter (`role="switch"`) med «KI-tekst» og «På» eller «Av», i blekk, ikke gul (spørsmål 5). Rammen er større (kort som de andre, radius 16, luft 20/22 px) og teksten 17 px. Med KI av står rammen med tittelen og bryteren, og en linje om at KI-teksten er skjult.
- U67 (delvis): tallene i en KI-tekst som vises, har prikket strek i tekstfargen (`designregler.md` §4). Teksten er alt kontrollert (FR-603), så bare sifrene markeres, og ingen tekst endres.
- U62: en innledning under tittelen sier hva siden viser.
- U63: kortet Retning har en kort forklaring nederst, med sjekkene med navn, som «Trend ga +1. Bevegelse og interesse ga 0.»
- U64: en rad for summen under de tre sjekkene, med styrken, T, B og I og retningen.
- U66: KI-teksten står etter kursgrafen, før historikken.
- U68: historikken er en kompakt tabell med en rad per uke: uka, mandag til fredag og summen. Månedsvelgeren er én knapp med piler på hver side, «Velg dag» står øverst til høyre i delen, ingressen er kort, og sumlinja har antallet per sjekk (finnes alt).
- *Rettet 04.11 kl. 00:48:* med KI av står bare bryteren, ikke rammen, tittelen og en linje om at teksten er skjult. Kommentaren i `aksje.html` fører svaret 25.10 kl. 00:51 og gjennomgangen 25.10 kl. 11 (VG11): med KI av er siden lik den var før 10.3, bortsett fra bryteren og setningen om dagene. Punktet over strider mot det, og regelen i instruksjonen sier at det da ikke bygges.
- *Rettet 04.11 kl. 00:48:* bildet av aksjesiden i `docs/appen/` slutter nå ved setningen om dagene under KI-teksten, ikke ved grafen, så det fortsatt har både grafen og KI-teksten (README-en). Månedsvelgeren har kanten rundt hele valget, og pilene inne i den er 44 px høye (U44).

**d) Forsiden og Min liste som på tavla**

- U58: ikke bygget (spørsmål 3).
- U59: oversikten har overskriften «Aksjene» med antallet over tabellen, og valget mellom «Alle» og «Min liste» (lenke til Min liste, med perioden).
- U69: Min liste har tittelen «N av M i Min liste skilte seg ut <ukedag>» når noe er merket og vurdert, med markeringen fra §4, og valget «Alle / Min liste» til høyre for tittelen på bred skjerm.

**Alle sidene:** demoen og den ekte versjonen likt, 390 px uten vannrett rulling, tastatur og skjermleser, og «?», `docs/hjelp.md` og README-en oppdatert (regel 19).

**Ville feilet hvis:** et funn som er bygget, var som i UX-loggen; et spørsmål under «Åpent» var bygget; eller siden rullet sidelengs ved 390 px.

## Planen, én commit per gruppe

1. Spesifikasjonen.
2. a) Oversikten.
3. b) Aksjesiden, småting.
4. c) Aksjesiden som på tavla.
5. d) Forsiden og Min liste.
6. Mutantene, gjennomgangen og triagen.

Hver commit med tester («Ville feilet hvis», uten nett), hjelpen, `docs/hjelp.md` og README-en, og bildene i `docs/appen/` med avtrykkene i `tests/test_docker.py` når malene bak dem endres. Hele settet alene før hver commit som endrer kode eller tester, og ruff (regel 23).

## Åpent: spørsmål til gruppen

1. **U57, plasseringen:** tavla har symbolet og tickeren under søylene, og FR-105 sier «Over hver søyle står bransjesymbolet, over tickeren». Skal FR-105 endres, så de står under?
   *Svar 04.11 kl. 09:58:* står som bygget, over søylene (FR-105).
2. **U57, fargen:** tavla har lys og mørk farge etter størrelsen. `designregler.md` §5 (2.9b) sier at fortegnet er de eneste fargegrensene, og at lengden viser størrelsen. Skal regelen endres?
   *Svar 04.11 kl. 09:58:* lys og mørk, mørk fra 2 % opp eller ned som i børsometeret. `designregler.md` §5 har fått en Rettet-linje. Bygget i `1fb126ec`.
3. **U58:** vinkelen ved navnet strider mot 8.0d (avvik 7, pilene bare for retning), «i går» og «hva sjekkene peker mot» i kolonneraden mot `designregler.md` §5 (bare «NOK», 14.10), og «3 av 3» til høyre for T, B og I mot 8.0e (T, B og I under). Skal noe av det endres?
   *Svar 04.11 kl. 09:58:* står som bygget, U58 er ikke bygget.
4. **U65:** notatet sier at tavla har navnene i en forklaring over grafen, med tallene ved enden utenfor feltet, mens utdraget §8 sier at navnene står ved enden av linjene. Bygget er det utdraget sier (U41 og U47). Skal grafen ha forklaringen over i stedet?
   *Svar 04.11 kl. 09:58:* står som bygget, navnene ved enden av linjene.
5. **U33 og U67, fargen:** tavla har en gul bryter. Gult ved en aksje betyr bare 3 av 3 (`designregler.md` §3). Bryteren er bygget i blekk. Skal den være gul likevel?
   *Svar 04.11 kl. 09:58:* står som bygget, i blekk.
6. **U46, stripa:** tavla har bryteren også i stripa øverst. Valget gjelder hele appen, og stripa har ingen knapper før sidene finnes (`designregler.md` §5), som Innstillinger (8.10). Skal bryteren stå i stripa nå?
   *Svar 04.11 kl. 09:58:* står som bygget, bryteren står ikke i stripa.
7. **U64, rekkefølgen i summen** (fra gjennomgangen 04.11, VG): raden for summen under sjekkene på aksjesiden har T, B og I og så «3 av 3» til høyre, som tavla. Det er samme rekkefølge som spørsmål 3 holder igjen for tabellen, der 8.0e har T, B og I under «N av 3». Skal summen ha styrken først?
   *Svar 04.11 kl. 09:48:* styrken først, som tabellen. Bygget i `26f488e4`.
8. **Grafen ved 390 px** (fra gjennomgangen 04.11, ECH6): feltet til høyre for navnene er 170 av 720 i grafen, og hele grafen skaleres ned på smal skjerm, så teksten i den blir om lag 5 px. Teksten var like liten før 8.2b, men tegneflaten er nå smalere. Skal grafen ha egne mål på smal skjerm (en egen story)?
   *Svar 04.11 kl. 09:48:* egen story, 8.2c, ekstra, ført i `epics.md` og sprint-status som backlog.

## Gjennomgangen 04.11 kl. 01:16

Etter hele settet på `f116c30`, med tre gjennomganger etter hverandre uten pytest eller demo samtidig: Blind Hunter (bare diffen), Edge Case Hunter og Verification Gap (med spesifikasjonen). Ingen funn på høy. Ingen funn sier at et spørsmål under «Åpent» er bygget.

**Rettet:**
- BH1, ECH2 (middels): «Velg dag» i historikken godtok seriens første dag, som `les_valg` avviser. Feltet begynner nå på andre dag, som periodevalget, og skjemaet sender tilbake til delen.
- BH2, ECH8, VG6 (middels): tittelen i Min liste talte vurderingene for hele markedet. Nå står tallet bare når minst én merket aksje er vurdert.
- ECH1 (middels): datoene på aksen for 1 mnd kom borti hverandre på den smalere tegneflaten. Et merke nærmere det forrige enn 36 får streken, ikke datoen.
- VG1 (middels): testen for «ikke gul» så bare etter ordet «gul». Den ser nå etter alle de gule fargene i stilen.
- VG2 (middels, regel 13): hjelpen mistet «med kurs samme dag» og «grå ved 0,00 %». Begge står igjen, og testen sjekker bare lengden.
- BH3, ECH3 (lav): demogrunnen sto også for siste dag i en demobase uten KI-tekstene. Nå bare for en dag før siste dag.
- BH4, ECH4, VG5 (lav): tallene i KI-teksten deles nå som kontrollen deler dem (`_SIFFER` i `ki_kontroll.py`), så tallet som er markert, er det som er prøvd.
- BH7, ECH7 (lav): valget «Alle / Min liste» på oversikten beholder sorteringen.
- ECH9 (lav): bryteren har kant og systemfarger med høy kontrast.
- BH9 (lav): «3 av 3» i hjelpen for historikken kommer fra antallet sjekker.
- VG3 (middels): en test for at hver ny rad brytes på smal skjerm. 390 px er også sjekket i Edge med en ramme på 390 px for oversikten, Min liste, børsometeret og aksjesidene.
- VG7, VG8 (lav): `docs/hjelp.md` sier at bryteren står alene med KI av, og ingressen sier «en dag med kurs».

**Står, med grunnen:**
- BH5 (lav): `til_venstre` slår ikke lenger til, fordi tegneflaten slutter 170 før kanten. Den står som vern hvis feltet til høyre blir mindre.
- BH6, ECH5 (lav): navnene kan stå et stykke fra enden når tre linjer ender likt, eller når indeksen slutter før siste dag. Fargen viser hvilken linje navnet hører til, og navnene ligger aldri oppå hverandre.
- BH8 (lav): «?» i overskriften over søylene leses med i figurteksten. Det er gyldig HTML, og knappen har sitt eget navn.
- ECH6 (lav): grafen på 390 px, spørsmål 8.
- VG4 (lav): commit b sier «knapper med kant» om pilene. Fra c har hele månedsvelgeren kanten (rettet 04.11 over), og meldingen skrives ikke om (regel 7).
- VG8 (lav): `endring_med_datoer` og `boersdag_mellom` i `aksjedetalj.py` brukes ikke lenger av malen, bare av testene. De står, så det er lett å gå tilbake hvis gruppen vil.
- VG, U58: summen på aksjesiden har «3 av 3» til høyre for T, B og I, spørsmål 7.

## Svarene 04.11 kl. 09:48–10:04, bygget samme dag

Svarene står under story 8.2 i `epics.md` (`29d310fc` på main). Main er flettet inn i `49b66d5e`. Én commit per endring:
- `26f488e4`: summen på aksjesiden har styrken først, «Sum 3 av 3 T -1 B -1 I -1 ↓Negativ».
- `1fb126ec`: søylene under hovedindeksen er lyse under 2 % opp eller ned og mørke fra 2 %, med `GRENSE_STERK` fra `boersometer.py` og endringen slik den vises. 0,00 % er grå som før. De lyse fargene fra børsometeret har om lag 1,4:1 mot hvitt, og søylene har ingen tekst, så søylene har egne lyse farger, `--soeyle-lys-opp` `#4E946D` og `--soeyle-lys-ned` `#CE7069`, med minst 3:1 mot kortet og bakgrunnen (designregler §5, kontrast). Forklaringen står under søylene, i hjelpen ved «?» og i `docs/hjelp.md`. FR-105 sier ingenting om fargen på søylene, bare om den stiplede linja, og er ikke endret.
- `d0f03d35`: «?» ved «Ga» og «Målt mot» i alle tre sjekkortene. Testen som krevde én knapp per vindu, har en datert kommentar.
- `75980cca`: børsometeret. Teksten i rutene og ved bransjenavnene er 14 px, og «Mål mot børsen» og «Hva fargene betyr» 16 px. Hver bransje har en tynn ramme i Strek 2, som er pynt: navnet over feltet sier hvilken bransje det er, så rammen trenger ikke 3:1. Styrken står i rutene som har plass: «3 av 3» og «2 av 3» i ringen fra tabellen for siste børsdag, ellers som tekst, som tabellen en annen dag. En gul ramme en annen dag har fortsatt merket «3 av 3 siste børsdag».
- `f212cfd3`: «?» for periodene står først i raden på oversikten, i Min liste og i børsometeret. Aksjesiden har ingen «?» for periodene. Hjelpen for grafen, også periodene, står ved overskriften over knappene, og den er ikke flyttet. Gruppen kan be om en egen «?» der.

**Tekstnivået i børsometeret.** Grensene i `tekstnivaa` var regnet for 13 og 12 px. Med 14 px er de 10 px per tegn pluss 10, 80 × 65 og, etter gjennomgangen, 126 × 106 (`NIVAA_3`). Målt i Edge med en ramme så bred som vinduet, ved 1280, 1100, 1079, 900, 761, 760, 600, 390, 360 og 320 px, for siste børsdag, 01.10, 18.09 og 1 uke: ingen synlig tekst utenfor ruta, og ingen vannrett rulling. 390 px er også sjekket for oversikten, Min liste, børsometeret og aksjesiden BRFE.

**Mutantene,** én om gangen med `-x`, kopi før og sha256 mot HEAD etter (lik hver gang): Me1 T, B og I foran styrken, Me2 `>` i stedet for `>=` ved 2 %, Me3 «?» ved «Ga» bare i det første kortet, Me4 «2 av 3» uten ring, Me5 «?» etter knappene i børsometeret og Mg1 hjelpefeltet flyttes ikke til et annet kort. Alle ble fanget.

## Gjennomgangen 04.11 kl. 11:15

Etter hele settet på `f212cfd3`, med Blind Hunter, Edge Case Hunter og Verification Gap på `49b66d5e..f212cfd3`, uten pytest eller demo fra hovedøkta samtidig. Ingen funn på høy.

**Rettet i `8ea018f9`:**
- BH1, ECH1 (middels): med tre «?» for samme vindu ble hjelpefeltet stående under det første kortet når «?» i et annet kort ble trykket mens vinduet var åpent, og fokus gikk tilbake til et annet «?». Klikket flytter nå feltet (`hjelp.js`), med en test i nettleseren ved 1280 og 390 px.
- BH2, ECH2, VG1 (middels): det lengste på nivå 3, en gul ramme en annen dag, kunne kuttes ved 112 × 103. Nivå 3 er nå 126 × 106, og en test regner høyden og bredden av tallene i `stil.css`.
- ECH3 (lav): skilletegn for skjermleseren før styrken og merket i ruta.
- ECH5 (lav): med høy kontrast står prøvene under søylene og rammen rundt bransjen.
- ECH6 (lav): «Lys søyle: under 2 %, opp eller ned».
- BH3 (lav): testen for en annen dag krever også styrken.
- BH6 (lav): kommentaren om én knapp per vindu i `test_hjelpetekster.py` har fått en datert linje.
- VG5 (lav): en test for at `docs/hjelp.md` sier samme grense som `GRENSE_STERK`.

**Står, med grunnen:**
- BH4 (lav): skjermleseren hører «1 av 3» og «3 av 3 siste børsdag» uten ordet «styrke». Merket sier dagen, og tabellen har kolonnenavnene.
- BH5, ECH4, VG2 (lav): lys og mørk søyle har om lag 1,7:1 og 1,9:1 mellom seg. Lengden viser størrelsen, tallene står i lista for skjermleseren, og forklaringen under søylene har ordene. Svaret kl. 09:58 bestemmer bare at de er lyse og mørke.
- VG3 (lav): rammen rundt bransjen er pynt, over.
- VG4 (lav): aksjesiden har ingen «?» for periodene, over.

## Rettet 04.11 kl. 19:21

Gruppens svar 04.11 kl. 19:21, ført under story 8.2 i `epics.md` (`e4d050d9`), bygget på grenen `8-2b-retting-styrken-og-sporsmaal`.

**1) Styrken i flere ruter (`3f02b59c`).** `STYRKE = (81, 75)` i `boersometer.py`: plass til én linje til under symbolet og endringen. På nivå 2 får ruta klassen `styrke-N` når den har plass, og `stil.css` skjuler styrken på nivå 2 bare uten den klassen. Merket for en annen dag og teksten står fortsatt bare på nivå 3. Grensen er regnet for 14 px med ringen og den gule rammen: høyden 2 × 4 + 2 × 4 + 2 × 16,8 + 22,4 (ringen) + 2 × 1 = 74,0, og bredden 2 × 4 + 2 × 6 + 2 × 2 + 2 × 7,2 + teksten. I Edge er «3 av 3» 38,78 px (0,46 em per tegn) og ringen 57,16 × 22,39 px; testen regner teksten med 0,5 em per tegn, og det gir 80,4. TROY i demoen er 86 × 191 px ved 1280 px og viser nå «2 av 3».

**2) «?» midt på periodeknappene (`3918f77d`).** `margin-top: -4px` på «?» i `.periodehode`, så midten av sirkelen er 18 px ned, midt på en knapp på 36 px. Periodevalget har `flex: 1 1 0; min-width: 0`, så det krymper og bryter knappene inne i seg og står ved siden av «?» også ved 390 px. Før sto «?» 7 px for høyt, og ved 390 px brøt hele periodevalget til linja under «?».

**3)** Aksjesiden er ikke endret. En test sjekker at den ikke har noen egen «?» for periodene, og at «?» står ved «Kursutvikling».

**Målt i Edge.** Headless Edge låser vinduet til minst 504 px innvendig og trekker 30 px for rammen. Den første målerunden var derfor ved feil bredder og telles ikke. Målingene som gjelder, er gjort i en iframe med nøyaktig bredde, mot demobasen i en midlertidig mappe:
- Børsometeret ved 1280, 1100, 1079, 900, 761, 760, 600, 390, 360 og 320 px, for siste børsdag, en annen dag (01.10) og 1 uke: ingen synlig tekst utenfor ruta og ingen vannrett rulling i noen av de 30.
- «?» på oversikten, i Min liste og i børsometeret ved de samme ti breddene: midten av «?» og midten av den første knappen er like (avvik 0,0 px), og det er ingen vannrett rulling.

**Bildene.** `docs/appen/oversikten-demo.png` er tatt på nytt, fordi «?» synes i det. «Øvrige aksjer» begynner på 1863,9 px før og etter, så høyden 1864 står. Bildet av aksjesiden er byte for byte det samme, og bare avtrykkene er endret. Hjelpen (`docs/hjelp.md` og `hjelpetekster.py`) sier allerede «styrken står i rutene som har plass», så den er ikke endret.

**Mutantene**, én om gangen med `-x`, med kopi før og sha256 mot HEAD etter (med LF, som i blobben):
- S1: `styrkeplass` gir alltid False. Fanget av `test_styrkeplass`.
- S2: `margin-top: 0px` på «?». Fanget av `test_spoersmaalstegnet_staar_midt_paa_den_foerste_knappen`.

### Gjennomgangen av rettingen 04.11

Blind Hunter, Edge Case Hunter og Verification Gap på `main..3918f77d`. Ingen funn på høy.

**Rettet i commiten etter gjennomgangen:**
- VG1 (middels): testen for nivåene på siden sjekker også `styrke-N` for alle fire klassene.
- VG2 (middels): ingen annen regel for `.periodehode`, heller ikke i en `@media`-blokk.
- VG3 (middels): en test for svar 3, aksjesiden.
- VG4 (middels): testen for grensen krever at styrken har samme skrift som ruta.
- ECH5 (lav): `styrke-N` settes bare på ruter med styrke, med en test.

**Står, med grunnen:**
- ECH1 (middels): en annen dag kan en rute på nivå 2 vise gul ramme og styrken for dagen, uten merket «3 av 3 siste børsdag». Det er svaret kl. 19:21: merket står som før, på nivå 3. «Hva fargene betyr» forklarer den gule rammen. Står som åpent punkt for gruppen.
- BH1, VG7 (middels og lav): testen for `styrke-N` i kartet bruker `styrkeplass`. Grensen selv er låst av `test_styrkeplass` (S1 ble fanget der) og av TROY.
- BH2 (middels): bredden for symbolet og endringen er dekket av nivå 2 (minst 80 px), som er et vilkår for `styrke-N`.
- BH3, ECH2, ECH3, VG8 (lav): grensen har 1 px og 0,6 px å gå på mot utregningen, og om lag 4 px i bredden mot målingen i Edge. Målt uten noe utenfor ruta ved alle ti breddene.
- BH4, ECH6, VG5 (lav): «?» forutsetter at den første knappen er 36 px. Målt i Edge på de tre sidene.
- BH5 (lav): klikkflaten på 44 px går 4 px opp. Den lå allerede 11 px utenfor (8.0d).
- BH6, ECH7 (lav): periodevalget fyller resten av raden. Målt ved 320 px uten vannrett rulling; zoom 200 % er ikke målt.
- BH7, BH9, VG6, VG9 (lav): testene leser velgerne slik de står; to av dem er strammet inn over (VG1, VG2).
- BH8 (lav): TROY-testen bygger på demoen, som instruksjonen ber om.
- ECH4 (lav): en overskrift på to linjer gjaldt før også; overskriften har én linje (`test_overskriften_har_plass_til_linja`).
