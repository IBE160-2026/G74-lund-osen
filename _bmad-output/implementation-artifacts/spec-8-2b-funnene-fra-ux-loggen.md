---
title: 'Story 8.2 (8.2b): 29 funn fra UX-loggen'
type: 'bugfix'
created: '2026-11-03'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
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
2. **U57, fargen:** tavla har lys og mørk farge etter størrelsen. `designregler.md` §5 (2.9b) sier at fortegnet er de eneste fargegrensene, og at lengden viser størrelsen. Skal regelen endres?
3. **U58:** vinkelen ved navnet strider mot 8.0d (avvik 7, pilene bare for retning), «i går» og «hva sjekkene peker mot» i kolonneraden mot `designregler.md` §5 (bare «NOK», 14.10), og «3 av 3» til høyre for T, B og I mot 8.0e (T, B og I under). Skal noe av det endres?
4. **U65:** notatet sier at tavla har navnene i en forklaring over grafen, med tallene ved enden utenfor feltet, mens utdraget §8 sier at navnene står ved enden av linjene. Bygget er det utdraget sier (U41 og U47). Skal grafen ha forklaringen over i stedet?
5. **U33 og U67, fargen:** tavla har en gul bryter. Gult ved en aksje betyr bare 3 av 3 (`designregler.md` §3). Bryteren er bygget i blekk. Skal den være gul likevel?
6. **U46, stripa:** tavla har bryteren også i stripa øverst. Valget gjelder hele appen, og stripa har ingen knapper før sidene finnes (`designregler.md` §5), som Innstillinger (8.10). Skal bryteren stå i stripa nå?
