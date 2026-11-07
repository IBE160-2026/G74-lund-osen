---
title: 'Story 8.20: UX-rettingene etter gjennomgangen 06.11'
type: 'feature'
created: '2026-11-07'
status: 'done'
route: 'dispatch'
baseline_commit: '93140a71'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/docs/skisser/2026-11-06/LESMEG.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-9-ki-teksten-forklarer-det-siden-viser.md'
---

*Svar 2026-11-07 kl. 10:33 (gruppens svar):* forslagene i spørsmål 1–21 under er godtatt, med fire endringer. 7: pilene står bare når datofeltet viser en dag, og er borte i en periode. 12: verdiene ved musepekeren står i en lapp i appens stil, som i skissen `aksjesiden-ki-paa.png`, som vises straks og følger musa, med CSS og uten skript, ikke med `<title>`. 2: én kort setning om hvorfor retningen oftere er positiv blir i vinduet for retningen, under 60 ord, og målingen står i `docs/hjelp.md` med grensene. 21: rekkefølgen er 10.9, 8.20c, 8.20a, 3.4h og 8.20b, fordi README-prøven er et suksessmål i briefen («Kjørbar for andre» i `product-brief.md`). Svaret står også under story 8.20 i `epics.md`, ført etter instruksjonen kl. 10:38 i `docs/ai-prompts/2026-11-07.md`.

Utkast, skrevet 07.11 i instruksjonen kl. 09:45 (`docs/ai-prompts/2026-11-07.md`). Ingenting bygges før gruppen har svart på spørsmålene under (regel 9).

## Spørsmål til gruppen før noe bygges

Hvert spørsmål har et forslag. Forslaget er det utkastet under bygger på, til gruppen har svart. Spørsmål 11–17 gjelder ønskene i `docs/skisser/2026-11-06/LESMEG.md` som ikke er avgjort.

1. **Hvordan telles de 60 ordene i et hjelpevindu?** *Forslag:* med `\w+`, som i U95, over alt i vinduet: overskriften, de fete titlene og tekstene, men ikke linja «Siden viser ‹dag›» i vinduet for sluttkursen, som bare sier datoen. Tallene i denne spesifikasjonen er telt slik.
2. **Hvor havner teksten fra de seks «?» som går ut?** Svaret 06.11 kl. 23:07 sier at «Ga» og «Målt mot» forklares ved «Hvorfor signalet ble …». Med teksten om grensene (52 ord) blir det vinduet over 60. *Forslag:* «Ga» og «Målt mot» står i vinduet ved «Hvorfor signalet ble …» med én setning hver (del E). Teksten om grensene, og teksten om hvorfor retningen oftere er positiv (`skjevhet`, i vinduet for retningen i dag), flyttes til `docs/hjelp.md`, under et nytt spørsmål «Hvordan ble grensene valgt?».
3. **Hvor går fotnoten under summen?** Svaret kl. 22:25 sier at den flyttes. *Forslag:* «ingen vekting» står i vinduet ved «Hvorfor signalet ble …», og at retningen er blandet når noen ga +1 og noen -1, står allerede i vinduet for retningen. Fotnoten går ut, og ingen setning går tapt.
4. **Hva skjer med de to fotnotene etter grafen?** Skissen har én linje nederst i rammen «Signalet forklart»: «Signalet bygger bare på kurs og volum i sjekkene over, ikke på KI-teksten, og sier ikke om du bør kjøpe eller selge.» Fotnoten i dag sier også at børsmeldinger og kommende finansielle hendelser ikke er med. *Forslag:* skissens linje, med «Børsmeldinger og kommende finansielle hendelser er ikke med i denne versjonen.» etter, så kravet ikke forsvinner. Uten sjekker, når rammen ikke vises, står fotnotene som i dag.
5. **Hva står på knappen ved datoen?** *Forslag:* alltid «Vis dagen», fordi datoen står i feltet (svaret kl. 23:34 og 23:42). Knappen er merket som valgt ved en valgt dag. «Velg dag» skiftes ut overalt, også i `designregler.md` §2 og §4 med en Rettet-linje, og den skjulte etiketten til feltet blir «Dagen siden viser».
6. **Skal «Velg dag» i «Signalet dag for dag» bort?** Rådet foreslo at datovelgeren bare står ved grafen. *Forslag:* ja. En dag i kalenderen er fortsatt en lenke til siden for dagen, og datoen over grafen gjør det samme.
7. **Skal datoen ha piler for forrige og neste børsdag?** Rådets forslag, i `boersometeret-en-dag.png`. *Forslag:* ja, som to lenker uten skript, på alle sidene med datovelger. Ved første og siste dag med kurs er pila grå og ikke en lenke.
8. **U79: skal den første knappen fortsatt vise 6 mnd fram til dagen?** *Forslag:* ja, som `designregler.md` §2 sier. Datoen i feltet (svaret kl. 23:42) og datoen på streken (spørsmål 9) viser hvilken dag knappen gjelder.
9. **U89: hvordan merkes dagen i grafen?** *Forslag:* som i skissen, med datoen i en svart lapp øverst på streken, for eksempel «05.11», og uten punktet nederst.
10. **U90: hva heter kurslinja?** *Forslag:* «Kurs (justert for utbytte)» i grafen, som skissen, og «Kurs justert for utbytte:» som tittel i hjelpen. PRD-en er låst og står som den er.
11. **U81: hvordan står merket for KI-teksten?** Skissen har «Skrevet av KI med en språkmodell på denne maskinen (gemma4:e4b).» Det stemmer ikke med egen nøkkel hos Gemini, Anthropic eller OpenAI (story 10.7). *Forslag:* «Laget av KI» står, og modellnavnet i en liten linje under teksten, slik `designregler.md` §4 sier («KI-tekst»). FR-602 er oppfylt som før.
12. **U91 og U92, rådets forslag om U for utbytte og verdier ved musepekeren.** *Forslag:* U for utbytte står i story 2.6 og tas ikke her. Verdiene ved musepekeren tas, uten skript: hver dag i grafen får et usynlig felt med `<title>`, for eksempel «tirsdag 22.09: kurs 104,41, snitt 50 dager 96,97», som nettleseren viser selv. Tallene skrives med `tall()` (regel 21).
13. **«2 av 3» med svart ring også på aksjesiden?** Rådets forslag. *Forslag:* ja, i summen og i kortet «Signalstyrke», som i tabellen i oversikten og i skissen. «3 av 3» har gul ring som før (`designregler.md` §3).
14. **Børsometeret, ønskene fra 22:30–22:57:** a) «Slik leser du børsometeret» øverst til høyre, b) «Mål mot børsen» som kort med «N av 15 gikk bedre enn indeksen», c) tabellen i samme stil som på forsiden, d) bransjeoverskriftene med symbol, antall og snitt, e) «2 av 3» og «3 av 3» like store og aldri utenfor ruta. *Forslag:* alle fem, som skissene. a) erstatter «Hva fargene betyr» under rutene. d) endrer svaret 26.10 kl. 13:00 (b), der antallet bare står i tabellen: antallet og snittet står på egen linje under navnet, og linja skjules aldri.
15. **Ingen hull ved siden av kortet, og datoen samlet med periodeknappene (23:19–23:30).** *Forslag:* kortet «Mål mot børsen» og «Slik leser du» står side om side og er like høye fra 1056 px, og smalere står de under hverandre. Datoen står etter periodeknappene etter svaret kl. 22:24, 23:23 og 23:30.
16. **U88: hva mer gjør sidene mer visuelle?** *Forslag:* bare det skissene viser: den valgte periodeknappen fylt i blekk, retningen i farget pille i rammen, de fete navnene på sjekkene i KI-teksten (10.9) og børsometeret som skissene. Ingen ny farge: gult er 3 av 3 (`designregler.md` §3).
17. **U96: hjelpefeltet dytter siden.** Det er fra svaret 24.10 kl. 11:31, der siden gir plass så feltet ikke dekker det det forklarer. *Forslag:* feltet står som i dag. Med høyst 60 ord blir det kortere, men det dytter fortsatt. Vil gruppen at feltet skal ligge over siden, endrer det svaret 24.10, og da må det avgjøres her.
18. **U100: «ikke vurdert» og «utenfor børskalenderen».** *Forslag:* begge står, fordi FR-409 skiller dem. «utenfor børskalenderen» får årene børskalenderen dekker, fra `DEKKEDE_AAR` i `src/boersdag.py`: «utenfor børskalenderen, som bare har 2026».
19. **U101: hva heter periodevalget i Min liste?** *Forslag:* «Sammenlign siste børsdag med», fordi den øverste linja i hver rad alltid er siste børsdag. Navnet endrer beslutningen 08.10 kl. 21:48.
20. **U75 og U76, README-en og webserveren.** *Forslag:* steg 5 og avsnittet om nøkkelen får «Har du en konto hos EODHD fra før, logger du inn og kopierer «API token» under «Dashboard».», med ordene README-en allerede bruker. `uv run python src/app.py` starter uten debug: `app.run(port=8000)`.
21. **Hvor mange PR-er, og i hvilken rekkefølge?** *Forslag:* tre, etter 10.9 (svaret 06.11 kl. 22:05): 8.20a aksjesiden og periodevalget med datoen på alle sidene, 8.20b børsometeret, og 8.20c README-en, webserveren og ordene i U100 og U101. Boblen nederst bygges med 3.4h etter 8.20a.

## Intent

**Problem:** gruppens gjennomgang 06.11 kl. 20:16–22:16 ga U75–U102 i `docs/ux-logg.md`. U77 er rettet, U82 bygges i 10.9 og U84 i 3.4h. Denne storyen tar de 25 andre.

**Avgjørelsene** (under story 8.20 i `epics.md`):
- *06.11 kl. 22:25:* toppen av aksjesiden står som i dag, med overskriften, de fire kortene, sjekkortene og summen, og fotnoten under summen flyttes.
- *06.11 kl. 22:24, 23:23 og 23:30:* periodeknappene og så datoen med «Vis dagen», samlet på én linje; er det for smalt, står datoen og knappen sammen på egen linje til venstre.
- *06.11 kl. 22:57:* for én dag følger størrelsen på rutene volumet, som avgjort 22.10 kl. 23:19, og for en periode er de like store. Gult har to nyanser som i appen.
- *06.11 kl. 23:34 og 23:42:* datofeltet viser dagen ved «I går» og ved en valgt dag, og er tomt i en periode, på alle sidene med datovelger.
- *06.11 kl. 23:07* (under story 8.0c): på aksjesiden ett «?» per kort og del, og høyst 60 ord i hvert hjelpevindu. Regelen fra 13.10 om høyst 3 setninger per tekst står (rettelsen 07.11 under 8.0c).
- *Fra 10.9* (svarene 06.11 kl. 22:16 og 22:23, og svaret 07.11 kl. 08:58): rammen «Signalet forklart» med appens setninger først og bryteren fast øverst til høyre.

**Skissene:** `docs/skisser/2026-11-06/`. `LESMEG.md` der skiller det som er avgjort fra ønskene, og ønskene avgjøres i spørsmålene over.

## Slått opp 07.11 på `93140a71` (regel 3)

- **«?» på aksjesiden** (`src/templates/aksje.html`): ved de fire kortene, ved «Hvorfor signalet ble …», ved «Ga», navnet og «Målt mot» i hvert av de tre sjekkortene, ved kursgrafen når den har hjelp, ved «‹navn› kort fortalt» når KI-teksten vises, og ved «Signalet dag for dag». Det er 17 med KI-teksten, og «?» i stripa kommer i tillegg. Vinduene står nederst i malen, med nøklene fra `src/hjelpetekster.py`.
- **Ordene i vinduene i dag**, telt som i spørsmål 1: Sluttkurs 58, Endring 55, Kursgrafen 159 med alle tre tekstene, Signalstyrke 71, Retning 143, Sjekkene 55, Signalet dag for dag 77, Kort fortalt 151, Trend 29, Bevegelse 37, Interesse 44, Ga 14, Målt mot 79. På børsometeret: Børsometer 266 og Periodene 49. Over 60: Kursgrafen, Signalstyrke, Retning, Signalet dag for dag, Kort fortalt, Målt mot og Børsometer.
- **Periodevalget** (`src/templates/_perioder.html`): én delmal for aksjesiden, oversikten, Min liste og børsometeret. Feltet har `value` bare når `dag` er gitt, det vil si ved en valgt dag, og knappen sier «Velg dag» eller datoen. Den første knappen heter «I dag», «I går» eller ukedagen (`foerste_knapp` i `src/perioder.py`).
- **Historikken** har et eget skjema med «Velg dag» øverst til høyre (story 8.2b, c, U68).
- **Fotnotene på aksjesiden:** under summen, to etter grafen, og fotnoten om investorsiden, som 3.4h tar.
- **Grafen:** kurslinja heter «Utbyttejustert kurs» i `linjenavn`, og dagen har `dagstrek` og `dagpunkt`. Grafen er en SVG laget på serveren, og det eneste skriptet er `hjelp.js`.
- **Børsometeret** (`src/templates/boersometer.html`): to tekster i innledningen, én for en dag og én for en periode, «Mål mot børsen» som en liste, «Hva fargene betyr» under rutene, tabellen bak «Se tallene som tabell», og fotnoten om en annen grunn (svaret 05.11 kl. 09:34, 1). Gult har to nyanser i `src/static/stil.css`: `--oransje` og `--gul-symbol`.
- **Webserveren:** `app.run(debug=True, port=8000)` under `__main__` i `src/app.py`. Skriptene og Docker starter waitress uten debug.

## Delene

### A) Toppen og summen (U83)

Toppen står som i dag (svaret kl. 22:25). Fotnoten under summen går ut, og setningene står i hjelpen (spørsmål 3). «2 av 3» får svart ring i summen og i kortet «Signalstyrke» (spørsmål 13).

**«?»:** ingen endring i kortene. De fire «?» står.

**Ville feilet hvis:** fotnoten sto igjen under summen, eller «ingen vekting» ikke sto i noe vindu på siden. Da er setningen borte, ikke flyttet.

### B) Periodevalget og datoen, på alle sidene (U79, U86)

Periodeknappene og så datoen med «Vis dagen» på én linje. Er det for smalt, står datoen og knappen sammen på egen linje til venstre (svaret kl. 22:24, 23:23 og 23:30). Feltet viser dagen ved den første knappen og ved en valgt dag, og er tomt i en periode (svaret kl. 23:34 og 23:42). Knappen heter «Vis dagen» (spørsmål 5), og pilene for forrige og neste børsdag står ved datoen (spørsmål 7). U86 er besvart av svaret kl. 22:24: valget er fortsatt et skjema uten skript, så knappen trengs. U79 står (spørsmål 8). «Velg dag» i historikken går ut (spørsmål 6).

**Ville feilet hvis:** feltet var tomt ved den første knappen, viste en dato i en periode, eller datoen sto på en egen linje ved 1280 px. Testen kjører alle fire sidene, ved 1280 og 390 px.

### C) Kursgrafen (U89, U90, U91, U92)

Datoen i en svart lapp øverst på streken (spørsmål 9). Kurslinja heter «Kurs (justert for utbytte)» (spørsmål 10). Verdiene ved musepekeren med `<title>`, uten skript (spørsmål 12). U91 står i story 2.6.

**«?»:** ett ved «Kursutvikling …», som i dag.

**Ville feilet hvis:** streken ikke hadde datoen, «Utbyttejustert kurs» sto igjen i grafen, eller et tall i `<title>` hadde punktum. Da er tallet ikke norsk der det leses (regel 21).

### D) Bunnen av aksjesiden (U78, U80, U81, U85, U87)

Rekkefølgen etter grafen, som skissen `aksjesiden-ki-paa.png`: rammen «Signalet forklart», så «Signalet dag for dag», så boblen til investorsiden (3.4h). Rammen bygges i 10.9 (del C der), og tar U78, U80 og U85: bryteren står fast øverst til høyre med KI på og av, og «‹navn› kort fortalt» går ut. Denne storyen legger til linja nederst i rammen (spørsmål 4) og merket (spørsmål 11). De to fotnotene etter grafen går ut når rammen vises.

**«?»:** ett ved «Signalet forklart», også med KI av, fordi rammen står da også. Teksten skrives i 10.9 (del D der).

**Ville feilet hvis:** setningen om børsmeldinger og kommende hendelser forsvant, eller en fotnote sto både etter grafen og i rammen. Da har siden mistet et krav, eller sier det to ganger.

### E) «?» og hjelpetekstene på aksjesiden (U95 for aksjesiden)

Etter 8.20 har aksjesiden 11 «?» med KI-teksten, og stripa i tillegg: de fire kortene, «Hvorfor signalet ble …», navnet i hvert av de tre sjekkortene, «Kursutvikling …», «Signalet forklart» og «Signalet dag for dag». De seks som går ut er «Ga» og «Målt mot» i hvert sjekkort. Teksten deres havner i vinduet ved «Hvorfor signalet ble …» (spørsmål 2).

Utkast, med antall ord telt som i spørsmål 1:

| Vindu | Utkast | Ord |
|---|---|---|
| Sluttkurs | **Sluttkurs:** kursen ved børsens stengning den dagen siden viser, uten utbyttejustering. Dagen står under navnet øverst: siste børsdag i dataene, eller dagen du valgte. | 25 (30 med «Siden viser fredag 09.10.») |
| Endring | **Endring:** endringen i prosent fra forrige dag med kurs, regnet på kursen justert for utbytte. Ved endringen står de to dagene, med ukedag og dato. **Kurs justert for utbytte:** kilden regner kursen om bakover ved hvert nytt utbytte, så et ordinært utbytte ikke ser ut som et kursfall. | 49 |
| Signalstyrke | **Signalstyrke:** hvor mange av de 3 sjekkene som slo ut, fra 0 til 3. Både +1 og -1 teller, så en sjekk med +1 og en med -1 gir 2. Med 2 eller mer står aksjen under «Skilte seg ut» i oversikten. Signalet er ikke en spådom og ikke et råd. | 52 |
| Retning | **Retning:** om sjekkene som slo ut, ga +1 eller -1, ikke hvor kursen går videre. **↑ Positiv:** alle ga +1. **↓ Negativ:** alle ga -1. **↔ Blandet:** noen +1 og noen -1. **– Ingen:** ingen slo ut. **– Ukjent:** ingen vurdering for dagen, og grunnen står under kortene. | 44 |
| Sjekkene, ved «Hvorfor signalet ble …» | **Hvorfor signalet ble:** tre sjekker, hver på sin del av dataene: kursnivå, endring og volum. «Ga» er det sjekken ga: +1, 0 eller -1. «Målt mot» er tallet sjekken ble avgjort av, og prikken viser det mot feltet der sjekken gir 0. Summen teller sjekkene som slo ut, uten vekting. | 51 |
| Trend | **Trend:** ligger kursen justert for utbytte mer enn 2 % over eller under snittet av de siste 50 børsdagene? Over gir +1, under gir -1, og innenfor 2 % gir 0. | 30 |
| Bevegelse, Interesse | Som i dag. | 37 og 44 |
| Kursgrafen | **Kursutvikling:** den tykke linja er kursen justert for utbytte, og den tynne snittet av de siste 50 børsdagene, som trenden måler mot. Den stiplede er hovedindeksen, regnet om så den starter på aksjens kurs. Streken med datoen er dagen siden viser. Knappene velger hvor langt tilbake grafen går. | 49 |
| Signalet dag for dag | **Signalet dag for dag:** det appen skrev om aksjen hver børsdag, lest fra basen og aldri regnet på nytt. Uka og måneden teller dagene med signalstyrke 2 eller mer, og 3 av 3 har ring. Klikk på en dag med kurs for å se hele siden for den dagen. | 53 |
| Signalet forklart | Skrives i 10.9 (del D der). | høyst 60 |

Tallene som er parametre (3, 2, 50, 0 til 3), hentes fra `Parametre` som i dag. Kursgrafen er i dag tre tekster etter hva grafen viser (`grafhjelp` i malen). Utkastet er én tekst, og setningen om den stiplede linja står bare når grafen har indeksen. Regelen for startdagen og «I år» står i `docs/hjelp.md`, «Hva gjør knappene over hovedindeksen?».

**Ville feilet hvis:** et vindu på aksjesiden hadde mer enn 60 ord, en tekst hadde mer enn 3 setninger, eller «Ga» eller «Målt mot» hadde et «?». En ny test i `tests/test_hjelpetekster.py` teller ordene i hvert vindu med demobasen, og `TestStory80c::test_hoeyst_tre_setninger_per_tekst` og `TestSidene::test_hvert_spoersmaalstegn_staar_ved_det_det_forklarer` rettes etter det nye. `TestIkkeRaad::test_hjelpen_sier_at_signalet_ikke_er_et_raad` står.

### F) Børsometeret (U93, U94, U95, U97, U98, U99, U102)

Som skissene `boersometeret-en-dag.png` og `boersometeret-1-uke.png`, med svarene over og ønskene i spørsmål 14 og 15:
- **Størrelsen:** for én dag følger arealet volumet mot vanlig, og for en periode er rutene like store (svaret kl. 22:57). Det er som i dag (22.10 kl. 23:19 og 8.17b).
- **Gult:** to nyanser som i appen, `--oransje` og `--gul-symbol`, for ramme og ring ved 3 av 3.
- **Innledningen (U98):** én tekst for en dag og en periode, som skissen: «Hver rute er en aksje, samlet etter bransje. Fargen viser endringen i perioden du velger, og rammen viser signalet siste børsdag. Klikk på en rute for å se aksjen. Bildet viser hva som skjedde, ikke hva du bør kjøpe eller selge.» Det som er ulikt for en dag og en periode, står i kortet «Mål mot børsen».
- **«Slik leser du børsometeret» (U99):** fargen, rammen, størrelsen og ruta, som skissen. Kortet erstatter «Hva fargene betyr».
- **Bransjene (U97):** symbolet og navnet, og under dem antallet og snittet, alltid synlig.
- **Rutene (U94):** «2 av 3» og «3 av 3» i samme størrelse i alle rutene, og aldri utenfor ruta. Får pillen ikke plass, står styrken i tabellen.
- **Tabellen (U93):** som på forsiden: kolonneraden i blekk, en rad per bransje med symbol, antall og snitt, en kant i `--oransje` ved 3 av 3, og styrken i ring.
- **Fotnoten (U102):** fotnoten om en annen grunn står, og hjelpen sier det ikke lenger.

**«?»:** to, som i dag: ved overskriften og først i periodehodet. Kortet «Slik leser du» får ingen.

**Hjelpetekstene:**

| Vindu | Utkast | Ord |
|---|---|---|
| Børsometer | **Børsometer:** én rute per aksje, samlet etter bransje. Fargen er endringen, i fem trinn. For én dag følger størrelsen volumet mot vanlig, og for en periode er rutene like store. Gul ramme er 3 av 3 og mørk 2 av 3, begge siste børsdag. Klikk på en rute for å se aksjen. | 53 |
| Periodene | **Periodene:** den første knappen viser siste børsdag, de andre endringen fra den første kursen i perioden, og datoen med «Vis dagen» en dag du velger. Ved en periode er rutene like store, fordi volumet mot vanlig gjelder én dag. Rammen er signalet siste børsdag. | 45 |

Resten av teksten om børsometeret i dag (265 ord) står i `docs/hjelp.md`, «Hva viser børsometeret?», som allerede har det meste.

**Ville feilet hvis:** innledningen byttet tekst ved en periode, snittet for en bransje var skjult, en pille sto utenfor ruta ved 1280 eller 390 px, eller hjelpen for børsometeret hadde mer enn 60 ord.

### G) Hjelpefeltet (U96)

Står som i dag, etter forslaget i spørsmål 17.

**Ville feilet hvis:** feltet dekket siden fra 1056 px uten at gruppen har svart på spørsmål 17. `tests/test_hjelpefeltet.py` står.

### H) Ordene i U88, U100 og U101

U88 etter spørsmål 16, U100 etter spørsmål 18 og U101 etter spørsmål 19.

**Ville feilet hvis:** «utenfor børskalenderen» sto uten årene, eller årene var skrevet fast i stedet for lest fra `DEKKEDE_AAR`.

### I) README-en og webserveren (U75, U76)

Etter spørsmål 20. README-en rettes i samme commit som koden (regel 19).

**Ville feilet hvis:** `src/app.py` hadde `debug=True`, eller README-en ikke sa hva man gjør med en konto fra før.

### J) Hjelpen som rettes når ordene på siden endres

`docs/hjelp.md` rettes der teksten står, uten Rettet-linje (regel 19, svaret 20.10 kl. 16:19). `designregler.md` får Rettet-linjer.

| Ordet på siden | Blir | Rettes i |
|---|---|---|
| «Velg dag» | «Vis dagen» | `sluttkurs_aksje` og `perioden` i `src/hjelpetekster.py`; `docs/hjelp.md`, «Hva viser børsometeret?», «Hva gjør knappene over hovedindeksen?» (to steder) og «Hva sa appen om en aksje tidligere?», der «bruk «Velg dag» øverst til høyre» går ut med spørsmål 6; `README.md`, lista over det som er bygget («På aksjesiden: …»); `designregler.md` §2 og §4 |
| «Laget av KI» | står (spørsmål 11) | ingen endring, utenom teksten for rammen i 10.9 |
| «‹navn› kort fortalt» | «Signalet forklart» (10.9) | `docs/hjelp.md`, spørsmålet «Hva er «kort fortalt» på aksjesiden?» og svaret; tittelen «Kort fortalt:» i `ki_kort_fortalt` og vinduet «Kort fortalt» i `aksje.html` |
| «Hva fargene betyr» | «Slik leser du børsometeret» (spørsmål 14 a) | `boersometeret` i `src/hjelpetekster.py`; `docs/hjelp.md`, «Hva viser børsometeret?» |
| «Utbyttejustert kurs» | «Kurs (justert for utbytte)» (spørsmål 10) | tittelen i `utbyttejustert`, teksten i `grafen` og `trend` i `src/hjelpetekster.py`; `linjenavn`, `aria-label` og bildeteksten under grafen i `aksje.html` |
| sitatet «skiller seg ut» | «Skilte seg ut», som oversikten sier | `signalstyrke` i `src/hjelpetekster.py`; det skjulte merket «skiller seg ut» i `src/templates/index.html` |

`hjelpetekster.py` har kildene til hver tekst ordrett. Når ordet i malen endres, rettes kilden i samme commit, og `TestKildene::test_hver_tekst_har_en_kilde_som_finnes` i `tests/test_hjelpetekster.py`, som slår opp kildene, viser om noe er glemt.

**Ville feilet hvis:** «Velg dag», «kort fortalt» eller «Hva fargene betyr» sto igjen i hjelpen, README-en eller malene etter at ordet på siden var endret, eller hjelpen siterte «skiller seg ut». En test leter etter de gamle ordene i `docs/hjelp.md`, `README.md`, `src/hjelpetekster.py` og malene.

### K) Bildene i `docs/appen/`

`_perioder.html` og `hjelpetekster.py` er med i avtrykket bak alle sju bildene, så alle tas på nytt:
- `aksjesiden-brfe-demo.png`: endres av A–E.
- `boersometeret-demo.png` og `boersometeret-390-demo.png`: endres av B og F, og høydene i `DE_NYE_BILDENE` i `tests/test_docker.py` måles på nytt.
- `oversikten-demo.png`, `oversikten-390-demo.png` og `min-liste-demo.png`: endres av B.
- `oversikten-topp-demo.png`: slutter over periodeknappene, så den skal være byte for byte den samme. Er den ikke det, sies det.

Avtrykkene settes på nytt med en kommentar, som før.

**Ville feilet hvis:** et bilde viste «Velg dag» eller et tomt datofelt ved den første knappen. `TestAksjesidebildet::test_bildet_tas_paa_nytt_naar_aksjesiden_endres`, `TestSkjermbildet::test_bildet_tas_paa_nytt_naar_oversikten_endres` og `TestBildeneAvAppen::test_de_nye_bildene_tas_paa_nytt_naar_siden_endres` i `tests/test_docker.py` feiler til bildene og avtrykkene er nye.

## Grenser

- Ingen kall til EODHD utover kvotesjekken i regel 15. `data/db/ose.db` røres ikke (regel 22). Demobaser bare i midlertidige mapper.
- Ingen skript utover `hjelp.js`, og ingenting fra nettet.
- Ingen tall fra den ekte versjonen i sporede filer (regel 16). Tallene i skissene er oppdiktet.
- Bygges på egen gren etter 10.9, og flettes bare ferdig og grønn.
- En mutant per del, med kopi før og sha256 mot HEAD etter.

## 8.20c, bygget 07.11

*Lagt til 2026-11-07, etter instruksjonen kl. 13:35 i `docs/ai-prompts/2026-11-07.md`:* 8.20c er bygget i samme PR som story 2.16 og porttestene, på grenen `2-16-boerskalenderen-for-alle-aar`, i rekkefølgen fra svar 21 (10.9, 8.20c, 8.20a, 3.4h og 8.20b). Den har del I og ordene i U100 og U101 fra del H. U88 i del H hører til 8.20a og 8.20b (spørsmål 16), og står.

*Lagt til 2026-11-07:* 8.20c er flettet med PR #117 i `a1c67c1a`, låst til head-en `20571270`, etter gruppens svar kl. 15:34 (U100: «utenfor børskalenderen, som begynner i 2026»). CI var grønn på head-en (run 42382704962) og på flettecommiten (run 42382919357).

- **U76 (del I, spørsmål 20):** `app.run(port=8000)` under `__main__` i `src/app.py`, uten debug. **Ville feilet hvis** `src/app.py` hadde `debug=True` (`TestDemoflagget::test_webserveren_fra_kommandoen_har_ikke_debug` i `tests/test_demo.py`).
- **U75 (del I, spørsmål 20):** steg 5 i «Den ekte versjonen» og avsnittet om nøkkelen i «Slik virker dobbeltklikket» har «Har du en konto hos EODHD fra før, logger du inn og kopierer «API token» under «Dashboard».» **Ville feilet hvis** en av dem bare sa at man lager en gratis bruker (`test_readme_sier_hva_man_gjoer_med_en_konto_fra_foer` i `tests/test_readme.py`). Avtrykkene av de to pilene i `tests/test_docker.py` er satt på nytt.
- **U100 (del H, spørsmål 18):** avgjøres i spesifikasjonen for 2.16, spørsmål 2, fordi forslaget her («som bare har 2026») ikke stemmer når kalenderen ikke har noe siste år. Byggingen følger forslaget der: «utenfor børskalenderen, som begynner i 2026», med året fra `FOERSTE_AAR`. **Ville feilet hvis** året var borte eller skrevet fast (`test_utenfor_boerskalenderen_gir_tekst_ikke_feil` i `tests/test_markedsoversikt.py`, og testen for tilstandene i `tests/test_historikken.py`).
- **U101 (del H, spørsmål 19):** periodevalget i Min liste heter «Sammenlign siste børsdag med», i overskriften, i navnet på valget, i «?» og vinduet, i hjelpeteksten `sammenlign_med` med kilden, og i `docs/hjelp.md`. **Ville feilet hvis** det gamle navnet sto igjen på siden eller i hjelpen (`TestTilgjengelig::test_skjermleseren_hoerer_hva_linja_under_gjelder` i `tests/test_periodevalget_min_liste_boersometer.py`). Kommentarene som viser til beslutningen 08.10 med det gamle navnet, står som historikk.
- **Bildene (del K):** `min-liste-demo.png` er tatt på nytt, med samme høyde. De seks andre er tatt på nytt og er byte for byte de samme.

## 8.20a, bygget 07.11

*Lagt til 2026-11-07, etter instruksjonen kl. 15:59 i `docs/ai-prompts/2026-11-07.md`:* 8.20a er bygget på grenen `8-20a-aksjesiden-og-periodevalget`, i rekkefølgen fra svar 21. Den har delene A–E og G, U88 for aksjesiden og periodevalget, det som hører til dem i J og K, og BH10 fra 2.16. Oppsettet av børsometeret i del F er 8.20b, men datofeltet og pilene der er med, fordi de hører til del B. Testene står i `tests/test_aksjesiden_8_20a.py`, utenom de som er rettet i `tests/test_hjelpetekster.py`.

- **A (U83, spørsmål 3 og 13):** fotnoten under summen er borte. «uten vekting» står i vinduet ved «Hvorfor signalet ble …», og blandet retning i vinduet for retningen. 2 av 3 har svart ring i summen og i kortet «Signalstyrke», og 3 av 3 har gul ring som før. **Ville feilet hvis** fotnoten sto igjen, «uten vekting» ikke sto i noe vindu, eller 2 av 3 sto uten ring (`TestToppenOgSummen`).
- **B (U79, U86, spørsmål 5–8, svarene 06.11 kl. 22:24–23:42 og 07.11 kl. 10:33, 7):** datoen står etter periodeknappene i samme liste, med pilene og «Vis dagen». Feltet viser siste børsdag ved den første knappen og dagen som er valgt, og er tomt i en periode (`dagen_i_feltet` i `src/perioder.py`). Pilene er lenker til forrige og neste børsdag etter børskalenderen, og en hverdag før 2026 (`pilene`), bare når feltet viser en dag, og grå ved første og siste dag feltet godtar. Den skjulte etiketten er «Dagen siden viser». Datovelgeren i «Signalet dag for dag» er borte (spørsmål 6). Det gjelder aksjesiden, oversikten, Min liste og børsometeret. **Ville feilet hvis** feltet var tomt ved den første knappen, viste en dato i en periode, pilene sto i en periode, eller «Velg dag» sto igjen (`TestDatoen`, `TestPilene`). At datoen står på samme linje ved 1280 px og ikke gir vannrett rulling ved 390 px, er sett i bildene og målt med `scrollWidth`, se K.
- **C (U89, U90, U92, spørsmål 9, 10 og 12 med svaret kl. 10:33):** datoen i en svart lapp øverst på streken, uten punktet nederst. Kurslinja heter «Kurs (justert for utbytte)». Hver dag i grafen har et usynlig felt, og lappen med datoen, kursen og snittet vises straks musa er over feltet, med `:hover` i stilarket og uten skript eller `<title>`. Tallene skrives med `tall()` (regel 21). **Ville feilet hvis** streken ikke hadde datoen, «Utbyttejustert kurs» sto igjen, et tall i lappen hadde punktum, eller lappen var en `<title>` (`TestGrafen`).
- **D (U81, spørsmål 4 og 11):** med rammen «Signalet forklart» står linja «Signalet bygger bare på kurs og volum i sjekkene over, ikke på KI-teksten, og sier ikke om du bør kjøpe eller selge. Børsmeldinger og kommende finansielle hendelser er ikke med i denne versjonen.» nederst i rammen, og de to fotnotene etter grafen er borte. Uten sjekker står fotnotene som før. «Laget av KI.» står over teksten, og «Modell:» med navnet i en liten linje under. **Ville feilet hvis** setningen om børsmeldinger forsvant eller sto to ganger (`TestBunnen`).
- **E (U95 for aksjesiden, spørsmål 1 og 2, svaret kl. 10:33, 2):** ett «?» per kort og del, og ingen ved «Ga» og «Målt mot». Vinduene har tekstene fra utkastet over, med tre avvik: «Ga» og «Målt mot» står i én setning, så teksten har høyst 3 setninger; vinduet ved «Hvorfor signalet ble …» har en egen tekst når siden ikke har sjekker (`sjekkene_uten`, med de 51 børsdagene); og vinduet for signalstyrken har «Signalet er ikke en spådom og ikke et råd.» som egen tekst (`ikke_raad_kort`), fordi oversikten bruker `signalstyrke` med `ikke_raad`. Vinduet for retningen har én setning om hvorfor retningen oftere er positiv (`oftere_positiv`), og målingen og grensene står i `docs/hjelp.md`, «Hvordan ble grensene valgt?». `grensene`, `skjevhet`, `hvorfor_tre`, `antall_dager`, `ga` og `maalt_mot` er tatt ut av `src/hjelpetekster.py`, og teksten deres står i det spørsmålet. **Ville feilet hvis** et vindu på aksjesiden hadde mer enn 60 ord, med KI på og av, med og uten sjekker (`TestHjelpevinduene::test_hoeyst_60_ord_i_hvert_vindu`, utvidet fra vinduet ved rammen i 10.9), eller «Ga» eller «Målt mot» hadde et «?».
- **G (U96):** hjelpefeltet står som før. `tests/test_hjelpefeltet.py` står.
- **U88 (spørsmål 16, svaret kl. 12:32, 4):** navnet på hver sjekk står med fet skrift første gang det står i KI-teksten (`ki_tekst` i `src/ki_visning.py`), i ubestemt eller bestemt form. Tallene har prikket strek som før. Den valgte periodeknappen var alt fylt i blekk, og retningen står i pille i summen. **Ville feilet hvis** et navn ikke var fett, var fett to ganger, eller et tall mistet prikket strek (`TestFeteNavn`).
- **BH10 fra 2.16:** vinduet ved dobbeltklikket i `start/start.ps1` og `start/start.sh` sier «Har du en konto hos EODHD fra før, logger du inn.», og `docs/hjelp.md` det samme. **Ville feilet hvis** vinduet bare ba om en gratis konto (`test_dobbeltklikket_nevner_en_konto_fra_foer`).
- **J:** «Velg dag» er «Vis dagen» i hjelpetekstene, `docs/hjelp.md` og README-en, «Utbyttejustert kurs» er «Kurs justert for utbytte», og hjelpen sier «Skilte seg ut» som oversikten. `designregler.md` §2 og §4 har Rettet-linjer. «kort fortalt» var alt borte etter 10.9. **Ville feilet hvis** et av de gamle ordene sto igjen (`test_de_gamle_ordene_staar_ikke_igjen`).
- **K:** alle sju bildene i `docs/appen/` er tatt på nytt med DevTools-protokollen i Edge uten vindu, som i 10.9 og 2.16. `oversikten-topp-demo.png` er byte for byte den samme, som delen sa. De seks andre er nye. Aksjesiden er 2300 px høy til bunnen av rammen (var 2345), og oversikten ved 390 px 3509 px (var 3524). Ved 390 px er bildene tatt med bredden 390 i protokollen, ikke med en iframe. Ved 1280, 390 og 320 px er `scrollWidth` lik bredden på aksjesiden, oversikten, Min liste og børsometeret, med siste børsdag, en periode og en valgt dag, og datoen står på samme linje som knappene ved 1280 px og på egen linje ved 390 og 320 px. Avtrykkene i `tests/test_docker.py` er satt på nytt med en kommentar.

**Testene og mutantene.** Hele settet ble kjørt alene før hver commit med kode eller tester, med ledig minne 4,4–4,6 GB av 15,7 GB. Første kjøring (16:14:57–16:27:24) ga 57 feilet, fordi testene ventet de gamle ordene og malene, og fordi klassen `dagene` på feltene i grafen kolliderte med setningen om dagene (den heter nå `musefelt`). Etter rettingene ga den andre (16:37:53–16:45:51) 2 feilet i `test_hjelpefeltet.py`, som brukte vinduet for «Ga» med tre knapper; testen legger nå en kopi av knappen ved «Trend» i de to andre kortene. Før `5bc2689c` (16:46:41–16:54:29) og `1c11844a` (16:56:01–17:04:05): 4434 bestått, 24 hoppet over og 0 feilet. Én mutant per del, med kopi før og sha256 mot HEAD etter, på `5bc2689c`: B, C, D, E, U88, BH10 og J ble fanget. A (2 av 3 uten ring) overlevde, fordi testen brukte symbolene fra skissen, og i demoen fantes bare BRFE med 3 av 3. Testen leser nå symbolene fra oversikten og krever både 2 av 3 og 3 av 3 (`1c11844a`), og A ble fanget. Hver fil var lik HEAD etterpå.

### Gjennomgangen av 8.20a

*Lagt til 2026-11-07:* gjennomgangen gikk på diffen `main...32648845` uten bildene, etter at hele settet var kjørt. Blind Hunter ga 14 funn (BH1–BH14), Edge Case Hunter 8 (ECH1–ECH8) og Verification Gap 1 hull og 2 andre funn (VG1–VG3). Hvert funn er sjekket i koden. Ingen er satt til høy.

| Funn | Grad | Utfall |
|---|---|---|
| BH11, ECH1: 2 av 3 fikk svart ring også en tidligere dag, mot `designregler.md` §3 og overskriften | middels | rettet: `and not tidligere_dag`, med testen `test_to_av_tre_har_ingen_ring_en_tidligere_dag` |
| ECH2: i børsometeret, som viser nærmeste dag med kurs, gikk neste-pila til et hull og ga samme dag tilbake | middels | rettet: børsometeret gir `kursdager`, og pilene går til forrige og neste dag med kurs (`test_med_kursdagene_hoppes_et_hull_over`) |
| ECH3: i den smale grafen ble lappen skjøvet inn over punktet den gjelder | middels | rettet: lappen står over eller under punktet når den ikke får plass ved siden av (`test_lappen_dekker_aldri_punktet`) |
| BH1: fire setninger falt ut av vinduene (indekslinja om framtida, «ikke en femte retning», signalet som er lagret for en valgt dag, og «eller hvorfor det mangler») | middels | rettet: de tre første står i `docs/hjelp.md`, fordi vinduene ellers går over 60 ord. Den fjerde står i ingressen på siden |
| ECH4, VG2: en dag uten vurdering har snittlinja, men hjelpen nevnte den ikke | lav | rettet: teksten følger `graf.har_ma50` |
| ECH5: vinduet nevnte streken med datoen også i en periode, der den ikke vises | lav | rettet: egen tekst `streken`, bare når grafen har en dag merket |
| ECH8: navn og tall i lappen kunne overlappe | lav | rettet: `LAPPBREDDE` 176, og nettlesertesten sjekker navn og tall i hver lapp |
| VG1: regelen før 2026 i `pilene` ble ikke prøvd | lav | rettet: `test_foer_2026_er_en_hverdag_en_boersdag` |
| BH5: testen for feltet sammenlignet med `max` i samme felt | lav | rettet: sammenlignes med siste børsdag i kortene på aksjesiden |
| BH3: `updated` i `docs/hjelp.md` var ikke satt | lav | rettet (regel 4) |
| ECH6: «trendsjekken» og «trend-sjekken» ble ikke fete | lav | rettet: mønsteret tar dem som hele ord (`test_sjekken_i_navnet`) |
| BH12: kommentarene sa «ingen vekting», teksten «uten vekting» | lav | rettet |
| BH7: siden vokser med lappene | lav | målt: aksjesiden er 401,6 kB ved «1 år» og 295,1 kB ved 6 mnd i demoen. Ikke endret |
| BH9: den svarte lappen øverst på streken kan dekke toppen av kurslinja den siste dagen | lav | avvist: lappen er 18 px, og punktet ved enden tegnes over den. Å flytte den over tegneflaten endrer målene på grafen og alle bildene |
| BH6: tallene i lappen er bare for mus | lav | avvist: lappen er et tillegg, uten skript etter svaret kl. 10:33, og tallene for dagen står i kortene og tabellen |
| BH8: målene på lappen står både i `graf.py` og malen | lav | avvist: ingen feil i dag, og nettlesertesten fanger en lapp utenfor grafen |
| BH10, ECH7: et vanlig «interessen for aksjen» før sjekknavnet ville blitt fett | lav | avvist: versjon 5 skriver «Interessen ga …» (svaret kl. 12:32, 3), og en vakt ville lagt til regler |
| BH13: forklaringen av kursgrafen står under spørsmålet om knappene | lav | avvist: der står regelen for perioden allerede, og spørsmålet sier at kursgrafen har de samme knappene |
| BH14: `test_velg_dag_i_historikken_godtar_bare_dager_siden_viser` gjelder nå feltet ved grafen | lav | avvist: navnet står fordi `docs/kvalitetssikring.md` viser til det, og docstringen sier hva testen gjør nå |
| VG3: fra 02.01.2026 går forrige-pila til 31.12.2025, som er stengt | lav | avvist: regelen for dager før 2026 er hverdager, som `foerste_boersdag_fra`, og siden sier at dagen ikke har kurs |
| BH2: målingen står bare i `docs/hjelp.md` | – | ikke en feil: svaret kl. 10:33, 2 |
| BH4: datoen kan vise aksjens siste dag, ikke børsens | – | ikke en feil: den første knappen på aksjesiden heter også etter aksjens siste dag (`knappene(rader[-1].dato, …)`) |

Rettingene er i `4cfdff78`. Hele settet alene før den, 17:16:51–17:25:03, med ledig minne 4,3 GB av 15,7 GB: 4440 bestått, 24 hoppet over og 0 feilet. Tre mutanter for rettingene, BH11, ECH2 og ECH3, ble fanget, og hver fil var lik HEAD etterpå. Bildene ble tatt på nytt og er byte for byte de samme, og avtrykkene er satt på nytt. CI var grønn på `32648845` (run 42389466402).

Ingen funn på middels eller over står åpne, og det er ingen spørsmål til gruppen før flettingen utover avvisningene over.

*Lagt til 2026-11-07:* 8.20a er flettet med PR #118 i `427a1de2` kl. 18:09, låst til head-en `8f740b7e` (main flettet inn), etter instruksjonen kl. 18:04 i `docs/ai-prompts/2026-11-07.md`. CI var grønn på head-en (run 42394650968) og på flettecommiten (run 42394909599), med 4433 bestått og 31 hoppet over i jobben `pytest` begge gangene. Hele settet lokalt før `4cfdff78`: 4440 bestått, 24 hoppet over og 0 feilet. BH9 tas med 8.20b (instruksjonen kl. 18:04).

## 8.20b, bygget 07.11

*Lagt til 2026-11-07, etter instruksjonen kl. 18:04 i `docs/ai-prompts/2026-11-07.md`:* 8.20b er bygget på grenen `8-20b-boersometeret`, PR #119, etter svaret kl. 17:36 (8.20b før 3.4h). Den har del F, det som hører til børsometeret i E, H (U88), J og K, og BH9 fra 8.20a. Testene som er nye, står i `tests/test_boersometeret_8_20b.py`. Testene for det gamle børsometeret er rettet i `tests/test_boersometer.py`, `tests/test_funnene_8_2b.py`, `tests/test_periodevalget_min_liste_boersometer.py` og `tests/test_designforslaget.py`.

- **F, innledningen (U98):** én tekst for en dag og en periode, som skissen. **Ville feilet hvis** innledningen byttet tekst ved en periode eller en valgt dag (`TestInnledningen`).
- **F, «Mål mot børsen» (spørsmål 14 b):** et kort med hovedindeksen, dagen eller perioden og «N av M gikk bedre enn indeksen», regnet med `er_bedre` som oversikten, av rutene med en endring og uten kortere serie (BH1). Setningen under sier hva fargen og størrelsen måler, ulikt for en dag og en periode. **Ville feilet hvis** M var alle 15 når noen mangler endring, eller lik telte som bedre (`TestMaalMotBoersen`).
- **F, «Slik leser du børsometeret» (U99, spørsmål 14 a):** fargen med skalaen og grensene, rammen, størrelsen og ruta, i stilen fra kortet på oversikten. Kortet erstatter «Hva fargene betyr». **Ville feilet hvis** kortet manglet, sto under rutene, eller et tall var et annet enn grensene (`TestFargetrinnene::test_slik_leser_du_boersometeret`).
- **F, kortene (spørsmål 15):** side om side og like høye fra 1056 px, og under hverandre smalere, over periodeknappene som i skissene. Skissen har «Slik leser du» ved siden av overskriften; her står begge kortene under innledningen, fordi kravet er at de er like høye. **Ville feilet hvis** kortene sto under hverandre ved 1056 px eller hadde ulik høyde (`TestINettleseren::test_kortene_side_om_side_og_like_hoeye`, målt i Edge).
- **F, bransjene (U97, spørsmål 14 d):** symbolet og navnet, og under dem antallet og snittet, for eksempel «4 aksjer · snitt -2,48 %», eller «1 aksje». Linja skjules aldri: `OVERSKRIFT` er 40 px, og hvert felt er minst så bredt som linja (`tilleggsbredde`, `TILLEGG_EM` 0,55). Det endrer svaret 26.10 kl. 13:00 (b). **Ville feilet hvis** linja manglet, var en annen tekst enn `Bransje.tillegg`, eller et felt var smalere enn den (`test_overskriften_er_navnet_og_under_antallet_og_snittet`, `test_linja_med_antallet_skjules_aldri`, `test_linja_i_overskriften_er_bransje_tillegg`, og linja målt i Edge ved 320, 390 og 1280 px).
- **F, rutene (U94):** «2 av 3» og «3 av 3» er 14 px i alle rutene og står inne i ruta. **Ville feilet hvis** en pille hadde en annen størrelse eller sto utenfor ruta ved 320, 390 eller 1280 px (`TestINettleseren::test_pillene_like_store_og_inne_i_ruta`).
- **F, tabellen (U93, spørsmål 14 c):** som på forsiden: kolonneraden i blekk, et bånd per bransje i sin egen `tbody` med symbolet, antallet og snittet, oransje strek ved 3 av 3 siste børsdag og styrken i ring. **Ville feilet hvis** bransjen var en egen kolonne, båndet eller streken manglet, eller ringen sto ved 3 av 3 en annen dag (`TestTabellen`).
- **F, størrelsen og gult (svaret 06.11 kl. 22:57):** for én dag følger arealet volumet, og for en periode er rutene like store, som før (8.17b). Rammen ved 3 av 3 er `--gul-symbol` og ringen `--oransje`. **Ville feilet hvis** rutene var like store en dag eller fulgte volumet i en periode, eller begge hadde samme nyanse (`TestStoerrelsenOgGult`).
- **E (U95 for børsometeret, U102):** vinduet «Børsometer» har `boersometeret` og `boersometeret_ruta`, og «Periodene» `perioden_boersometeret`, høyst 60 ord hver. Resten av teksten om børsometeret står i `docs/hjelp.md`, «Hva viser børsometeret?». Fotnoten om en annen grunn står, og vinduet sier det ikke lenger. **Ville feilet hvis** et vindu hadde mer enn 60 ord ved en dag, en periode eller en valgt dag, eller vinduet gjentok fotnoten (`TestHjelpevinduene`).
- **H (U88 for børsometeret):** det skissene viser: kortene, bransjeoverskriftene og tabellen. Ingen ny farge.
- **J:** «Hva fargene betyr» er borte fra hjelpen, README-en, hjelpetekstene og malene. **Ville feilet hvis** det gamle navnet sto igjen (`test_hva_fargene_betyr_staar_ikke_igjen`).
- **BH9 fra 8.20a:** lappen med datoen står over tegneflaten i kursgrafen. `MARG_Y` er 26 (var 12), og lappen står 4 px over tegneflaten. **Ville feilet hvis** lappen sto inne i tegneflaten eller kurslinja over `MARG_Y` (`test_lappen_med_datoen_staar_over_tegneflaten`).
- **K:** bildene er tatt med DevTools-protokollen i Edge uten vindu, som i 8.20a. `boersometeret-demo.png` er 1682 px (var 1329), `boersometeret-390-demo.png` 3327 px (var 1687) og `aksjesiden-brfe-demo.png` er ny med samme høyde (2300 px). De fire andre er byte for byte de samme. Ved 1280, 1056, 390 og 320 px ruller ikke børsometeret vannrett. README-en har ny bildetekst. Avtrykkene i `tests/test_docker.py` er satt på nytt med en kommentar.
- **Følger av U97 i demoen:** feltene er lavere med to linjer i overskriften. VRDS viser «ikke vurdert» i den smale flaten, ikke lenger ved 1280 px, og fotnoten for en annen grunn følger det (`vis-smal`). LKSV 18.09 er ikke lenger stor, så testen for merket i stedet for navnet bruker BRFE 06.10 og har beholdt navnet sitt, fordi `docs/kvalitetssikring.md` viser til det.

**Testene og mutantene.** Hele settet ble kjørt alene før hver commit med kode eller tester, med ledig minne 4,0–4,3 GB av 15,7 GB. Første kjøring (18:37:51–18:46:12) ga 1 feilet, `test_lksv_18_09_viser_merket_i_stedet_for_navnet`, fordi LKSV 18.09 var mindre (se over). Etter rettingen: 4464 bestått før `d95dcc43` (18:55:26–19:04:08) og `54a7cc50` (19:06:58–19:15:15), og 4470 før `2aba7d25` (19:24:20–19:32:39), med 24 hoppet over og 0 feilet hver gang. Én mutant per del på `d95dcc43`, med kopi før og sha256 mot HEAD etter: U98, spørsmål 14 b, U99, U97, U94, U93, størrelsen, spørsmål 15, E, J, U102 og BH9. Alle ble fanget, BH9 først etter `54a7cc50`, fordi testen åpnet aksjesiden med 6 mnd, der streken ikke står. Seks mutanter for rettingene på `2aba7d25` (BH1, BH11, ECH4, BH15, VG3 og VG4) ble fanget. Hver fil var lik HEAD etterpå.

### Gjennomgangen av 8.20b

*Lagt til 2026-11-07:* gjennomgangen gikk på diffen `main...54a7cc50` uten bildene, etter at hele settet var kjørt. Blind Hunter ga 20 funn (BH1–BH20), Edge Case Hunter 8 (ECH1–ECH8) og Verification Gap 6 (VG1–VG6). Hvert funn er sjekket i koden. Ingen er satt til høy.

| Funn | Grad | Utfall |
|---|---|---|
| BH1, ECH2: en aksje med kortere serie i en periode ble sammenlignet med indeksen over hele perioden | middels | rettet: telles ikke i M (`test_en_kortere_serie_telles_ikke_mot_indeksen`) |
| BH11, ECH5: alle bransjene i én `tbody`, så `scope="rowgroup"` gjaldt hele tabellen | middels | rettet: én `tbody` per bransje, som delene på forsiden |
| ECH4: båndet i tabellen hadde ingen bakgrunn, og antallet var hvitt på lys bunn | middels | rettet: klassen `oevrige` fra forsiden |
| BH15: «Gul ramme: 3 av 3.» sa ikke siste børsdag | middels | rettet: «på siste børsdag, også en annen dag» |
| BH5, VG3: malen bygde linja selv, og ingen test sammenlignet den med `Bransje.tillegg` | middels | rettet med testen `test_linja_i_overskriften_er_bransje_tillegg`; malen står, fordi snittet skal ha fargen |
| BH6: nettlesertesten sjekket ikke om linja ble kuttet sidelengs | middels | rettet: linja må stå innenfor h2 |
| VG4: ringen for 3 av 3 i tabellen en annen dag var ikke prøvd | middels | rettet: `test_ingen_ring_ved_3_av_3_en_annen_dag` |
| BH3, ECH6, VG6: grensene under skalaen sto ikke ved overgangene | middels | rettet: ved 20, 40, 60 og 80 % |
| BH8, ECH8: det verste kartet var ikke prøvd | middels | rettet med `test_det_verste_kartet_faar_plass` (10 aksjer i én bransje, MINSTE_VEKT mot STOERSTE_VEKT). Får kartet likevel ikke plass, står tabellen alene, som før (NFR-03) |
| BH9: børsometeret ved 390 px er 3327 px høyt, mot 1687, fordi linja med antallet aldri skjules | middels | lukket 2026-11-07 etter gruppens svar kl. 20:01 på spørsmål 1 (regel 25): slik det er |
| BH12: regelen for cellene i tabellen ble slettet | middels | avvist: `:where(.side-oversikt) th, td` i `stil.css` gir venstrestilling, luft og strek, som på forsiden |
| BH2, ECH1: «0 av 0» uten aksjer med endring | lav | rettet |
| BH16: vinduet for periodene sa ikke at perioden slutter siste børsdag | lav | rettet, innenfor 60 ord |
| BH14: navnet og symbolet sto inntil hverandre for skjermleseren | lav | rettet: skjult komma, og mellomrom etter titlene i kortet |
| BH18: en påstand i testen var alltid sann | lav | rettet |
| BH20: hjelpen sa ikke at ringen og endringen fra børsdagen før gjelder en dag | lav | rettet i `docs/hjelp.md` |
| VG1: nettlesertestene ble hoppet over i CI uten nettleser | lav | rettet: vernet fra `test_hjelpefeltet.py` |
| VG2: linja ble ikke målt ved 320 px | lav | rettet |
| VG5: vinduet for volumet i kortet var ikke prøvd | lav | rettet |
| BH4: grensene i skalaen var ikke formatert som i `trinnforklaringer` | lav | avvist: `trinnforklaringer` formaterer den sterke grensen på samme måte, uten `_noeyaktig` |
| BH7, ECH7: `TILLEGG_EM` er et anslag, og en annen skrift kan gi en bredere linje | lav | avvist: skriftene ligger i appen, og linja er målt i Edge ved 320, 390 og 1280 px |
| BH10: testene for VRDS og LKSV følger utlegningen i demoen | lav | avvist: kravet er prøvd med konstruerte ruter i testene for nivåene, og demoen viser det; endringen står over |
| BH13: båndet har antallet uten «aksjer», og snittet også ved én aksje | lav | avvist: som båndene på forsiden |
| BH17: `MARG_Y` er større også uten lapp | lav | avvist: samme tegneflate med og uten dag, så grafen ikke hopper mellom knappene |
| BH19: kildene `def ramme(` og `class="periodevalg"` | lav | ikke en feil: begge finnes, og `TestKildene` slår dem opp |
| ECH3: M i børsometeret er ikke M i oversikten | lav | ikke en feil: børsometeret teller aksjene med en endring for dagen eller perioden, og sier det i `docs/hjelp.md` |

Rettingene er i `2aba7d25`. CI var grønn på `54a7cc50` (run 42400409007).

*Lagt til 2026-11-07:* 8.20b er flettet med PR #119 i `8d89cf8c` kl. 20:08, låst til head-en `3266e7b2` (main flettet inn i `73de46d1`, og svaret kl. 20:01 med BH9 lukket), etter instruksjonen kl. 20:03 i `docs/ai-prompts/2026-11-07.md`. CI var grønn på head-en (run 42404496878) og på flettecommiten (run 42404752485), med 4463 bestått og 31 hoppet over i jobben `pytest` begge gangene. Med 8.20c (#117), 8.20a (#118) og 8.20b (#119) er 8.20 done; U84 står til 3.4h.

## Spørsmål til gruppen før flettingen av 8.20b

1. **BH9: børsometeret ved 390 px er 3327 px høyt (var 1687).** Linja med antallet og snittet skjules aldri (spørsmål 14 d), så hvert felt må være bredt nok til den, og på smal skjerm står bransjene mest under hverandre. *Forslag:* slik det er, fordi svaret var at linja aldri skjules. Alternativet er at snittet står på smal skjerm og antallet bare i tabellen.

*Svar 2026-11-07 kl. 20:01 (gruppens svar):* forslaget i spørsmål 1 er godtatt. Børsometeret står som bygget, også 3327 px høyt ved 390 px, fordi linja med antallet og snittet under hver bransje aldri skjules (spørsmål 14 d). BH9 er dermed besvart og lukket (regel 25). Rådet anbefalte det. Koden er ikke endret. Svaret er ført etter instruksjonen kl. 20:03 i `docs/ai-prompts/2026-11-07.md`.

## Det som står igjen i 8.20 etter 8.20b

*Lagt til 2026-11-07:* boblen til investorsiden nederst på aksjesiden (del D og U84) bygges i 3.4h i natt, etter svaret kl. 17:36. Ellers står ingenting i 8.20 igjen.
