---
title: 'Story 8.26: «Vis meg rundt» spiller av siden, knappene øverst og funnene fra demoprøven'
type: 'feature'
created: '2026-11-11'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '7fd5320c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-9-vis-meg-rundt.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-25-spill-av-omvisningen.md'
---

Skrevet 11.11 i instruksjonen kl. 18:01, etter gruppens svar 11.11 kl. 16:58, 17:06, 17:12 og 17:21, med tilleggene 1–4 (ønskene kl. 17:44, svaret kl. 17:47 og ønskene kl. 17:48 og 17:53). Instruksjonen kl. 18:01 erstatter instruksjonen kl. 16:58 og tilleggene kl. 17:06 og 17:12, som aldri kom til vinduet, og tillegget kl. 17:38, som stoppet i steg 0. 8.25 er brukt, så dette er 8.26. Storyen flettes ikke før gruppens ja. Svarene står ikke i repoet ennå; det som står her om dem, er hentet fra instruksjonen og tilleggene.

## Storyen

Som **bruker i demoen og den ekte versjonen**, vil jeg at «Vis meg rundt» viser meg delene av siden der jeg står, uten at siden hopper, at knappene står sammen med sideknappene, og at funnene fra demoprøven er rettet, så sidene er roligere og sier det de viser.

**Oppfyller:** FR-109, svarene 11.11 kl. 16:58–17:53 · **Begrenses av:** NFR-06, `AD-3`, `AD-10`, regel 22

**Avhenger av:** 8.9, 8.25. **Én økt:** nei, delene bygges etter hverandre.

## Svarene

*Svar 2026-11-11 kl. 16:58 (gruppens svar):* «Vis meg rundt» starter den samme boksen som omvisningen, bare med stegene for siden man står på, og den nummererte lista fra 8.9 tas bort, fordi testpersonen 10.11 gikk seg vill når siden hoppet. Siste steg på en side har «Ferdig» og lenken «Spill av hele omvisningen». Tilbudet første gang står som før.

*Svar 2026-11-11 kl. 17:06 (gruppens svar):* «Vis meg rundt» og «Spill av omvisningen» står i raden øverst etter «Innstillinger», i samme stil som sideknappene og med hvert sitt ikon, og raden under demolinja blir borte. Rådet anbefalte én knapp, men gruppen valgte to. «?» ved Hovedindeksen sier: «OSEBX er hovedindeksen på Oslo Børs. I demoen heter den oppdiktede indeksen DEMIX.»

*Svar 2026-11-11 kl. 17:12 (gruppens svar):* «Dine egne aksjer» i Min liste får samme stil som oversikten og «Følg en aksje», og «Lista er full …» står ikke i rødt, fordi rødt betyr negativ.

*Svar 2026-11-11 kl. 17:21 (gruppens svar):* bryteren «Vis KI-tekst» ved «Børsdagen kort fortalt» og på aksjesiden blir oransje som i Innstillinger, og «Laget av KI» står grått, fordi det er en merkelapp og ikke en knapp. Punktet i `issues.md` (spørsmål 5 i 8.2b) lukkes.

*Ønsket 2026-11-11 kl. 17:44 (tillegg 1 og 2):* fotnoten under tabellen tas bort, og de andre løse tekstene mellom delene får et forslag hver. «uten data» får en forklaring, som «for kort historikk», og «Ukjent» som retning forklares bak «?».

*Svar 2026-11-11 kl. 17:47 (tillegg 3, rådet anbefalte alt):* en aksje som følges, får stjerne og står i Min liste med en gang; aksjene som venter på henting, står nederst i tabellen med «venter på henting»; og der «lista» betyr alle aksjene appen følger, sies det slik.

*Ønskene 2026-11-11 kl. 17:48 og 17:53 (tillegg 4, rådet var enig):* filteret «Alle», «3 av 3 positiv» og «3 av 3 negativ» tas bort, og lenken «Den ekte versjonen» åpnes i en ny fane.

*Ønsket 2026-11-11 kl. 19:36 (tillegg 6, rådet var enig):* siden står i ro når man trykker på en periode.

*Ønsket 2026-11-11 kl. 19:51 (tillegg 8, rådet var enig):* den samme forklaringen på hvorfor overalt der «uten data» sto. Det skjerper tillegg 2.

*Ønsket 2026-11-11 kl. 20:06 (tillegg 10, rådet var enig):* en lenke har samme farge før og etter at man har klikket på den.

*Svar 2026-11-11 kl. 20:28 (tillegg 12, rådet anbefalte begge, og siden i demoen var gruppens ønske):* «Din egen liste: kom i gang» i Min liste bygges som på designtavla, og knappen i steg 1 får en egen side i demoen.

Tilleggene 5, 7, 9, 11, 13 og 14 er ikke limt inn i vinduet. Tillegg 15 (kl. 20:46) stoppet i steg 0, fordi det bygger på forslaget fra tillegg 14.

Rådet anbefalte alle unntatt det med to knapper.

*Svar 2026-11-12 kl. 09:58 (tillegg 21, rådet anbefalte det):* etter målet «Brukerutfall» i §7 i PRD-en starter tilbudet første gang «Vis meg rundt» for oversikten, ikke hele omvisningen, og det siste steget der viser vei til navnene under «Skilte seg ut». Det retter tillegg 20, steg 3, om det appen tilbyr første gang. Se del 13.

*Svar 2026-11-12 kl. 10:16 (tillegg 22, rådet anbefalte alt):* spørsmål 1–9 og 12–22 godtas som bygget. Spørsmål 11: forslag 1, «Nøkkelen? Den ligger under matta, sammen med de 20 kallene.», som bygget. Spørsmål 15: tillegg 11 kommer ikke, fordi det var en pytest-pause for 10.10 som er over, så ingenting mer bygges for det. Spørsmål 10 rettes: forklaringen på en aksje uten kurser gir ikke lenger «nettopp er lagt til og venter på hentingen» som grunn, og sier hva neste henting gjør (del 14). PR-en flettes 12.11 kl. 23:50–23:58 når alt er grønt, med tillegg 21 og 22.

*Svar 2026-11-12 kl. 16:23 og 16:24 (tillegg 23):* gruppen antar at det ikke blir noen presentasjon, så README-en er inngangen for faglærer, og gruppen vil gjøre ferdig alt nå. To linjer under «Til faglærer», forskjellene mellom demoen og den ekte versjonen (ønsket kl. 16:24) og det som sa at appen er under utvikling, rettes i denne storyen. Rådet anbefalte README-en i en egen runde 13.11; gruppen valgte i dag. Fristen og flettingen fra tillegg 22 står. Se del 15.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Uten skriptet.** *Forslag:* begge knappene er skjult til skriptet er lastet, som «Spill av omvisningen» i 8.25, så de aldri står uten å virke. Uten skriptet er det ingen «Vis meg rundt»; lista fra 8.9 var reserven, og den er tatt bort etter svaret kl. 16:58.
2. **Ikonene.** *Forslag:* et kompass for «Vis meg rundt» og en avspillingsknapp i en sirkel for «Spill av omvisningen», 16 px med strek 2 som de andre ikonene i raden.
3. **«Spill av hele omvisningen».** *Forslag:* lenken står bare på siste steg med «Vis meg rundt». I hele omvisningen går «Neste» videre til neste side som før, og siste steg har «Ferdig».
4. **«Vis meg rundt» og en annen side.** *Forslag:* «Vis meg rundt» lagrer ingenting, så boksen lukkes når man går til en annen side, og en omvisning som er i gang, fortsetter ikke av den.
5. **Ved 390 px.** *Forslag:* knappene brytes over flere linjer som sideknappene i dag, uten rulling.
6. **Ordene for en aksje uten kurser (tillegg 2 og 8).** *Forslag:* rådets ord, «ingen kurser ennå», likt overalt, fra én konstant (`UTEN_DATA_TEKST`): raden på oversikten og i Min liste, ruta, `title` og begge kolonnene i tabellen på børsometeret (med stor forbokstav), aksjesiden og hjelpen bak «?» ved «Oppdatert». Båndet over radene sier «uten kurser». «?» og aksjesiden sier hvorfor, med den samme setningen (`UTEN_KURSER_HVORFOR`), og i demoen at Matfjord Merkevarer med vilje er uten kurser, med navnet fra `UTEN_KURSER` i `demo.py`. En aksje med kurser, men uten kurs på dagen, står med «Ingen kurs den dagen» (gjennomgangen, ECH4). Etter tillegg 2 sto ruta med «Ingen kurs», fordi den lange teksten ikke får plass i en stor rute; etter tillegg 8 står de samme ordene der, og ruta får den vanlige størrelsen. «venter på henting» står for aksjene som venter, i del 5.
7. **Stjernen og aksjene som venter (tillegg 3).** *Forslag:*
   - **Stjernen** skrives av nettsiden i `min_liste` i samme transaksjon som ønsket i `oenske`, og ingenting annet skrives (regel 22). En aksje som venter, står ikke i `aksje` ennå, og triggerne fra 0007 avviste den, så **migrasjon 0013** lar dem godta et symbol med et ønske om å følge som verken er tatt i bruk eller avvist. Med en migrasjon kan storyen bare flettes kl. 23:50–23:58. Alternativet uten migrasjon er at hentingen setter stjernen når den tar aksjen inn, men da skriver hentingen `min_liste`, mot AD-3 og føringen 30.09, eller at stjernen bare vises og ikke kan tas bort før hentingen.
   - **Tallene** («N av M aksjer», «Alle», «Min liste», «Øvrige aksjer» og «appen følger 16 av 18») teller en aksje som venter, som radene i tabellen, og båndet over radene sier «og N venter på henting». Først var forslaget at overskriften ikke talte den, men da sprikte tallene på samme side (gjennomgangen, ECH3). Med «Velg dag» står den ikke, fordi appen ikke fulgte den den dagen.
   - **«Angre»** tar også bort stjernen som «Følg» satte, også i et bytte, så Min liste ikke har en aksje appen ikke følger. En stjerne på en aksje som verken står i lista eller venter (ønsket ble avvist eller slettet), ryddes bort ved neste «Følg», «Angre» eller «Bruk denne lista». En aksje fra en ferdig liste får ikke stjerne, fordi svaret gjelder «Følg».
   - **Børsometeret** viser ikke en aksje som venter, fordi den ikke har kurs eller rute ennå. **Siden Min liste** viser den nederst med «venter på henting», som oversikten. Raden har stjernen, «Egen» og navnet uten lenke, fordi aksjen ikke har en aksjeside før hentingen.
8. **Ordene om «lista» (tillegg 3, del 2).** *Forslag:* der «lista» betyr alle aksjene appen følger, sier sidene det: «appen følger 16 av 18» (to steder), «Appen følger allerede 18 aksjer, som er taket. Fjern en for å følge en annen.» (tre steder og i `valg.py`, også «… for å angre dette.»), «Appen følger alt …, eller den venter på hentingen.» og «Appen kan følge opptil 18 aksjer …». Ikke endret: «lista di» (stegene i «Din egen liste», som er brukerens egen liste), meldingen «N endringer i lista tas i bruk ved hentingen» og «13 av de 15 aksjene i lista» i «Signalet forklart» og KI-teksten, fordi tillegget sier at bare de setningene endres, og KI-teksten kontrolleres mot ordene.
9. **Testene av boksen i nettleseren (gjennomgangen, VG1, middels).** *Forslag:* skriptet testes som før: de rene funksjonene i `OMVISNING` kjøres med Node, og resten (`start`, `visSiden`, `avslutt`, lenken og `pageshow`) sjekkes i kildeteksten og er prøvd i Edge mot demoen for hver del og etter gjennomgangen. En test som kjører siden i en nettleser eller med jsdom, krever pakker fra npm i CI, som repoet ikke har. Alternativet er å legge til jsdom i CI før flettingen.
10. **Hvorfor en aksje er uten kurser (tillegg 8, gjennomgangen ECH2, BH3 og VG2, middels).** *Forslag:* ordlyden fra tillegg 8, som bygget: «appen har ingen kurser for aksjen ennå, fordi den nettopp er lagt til og venter på hentingen om kvelden, eller fordi kilden ikke har kurser for den.» Gjennomgangen påpekte at en aksje som venter på hentingen, står med «venter på henting», og at en aksje som står i lista uten kurser, alt er forsøkt hentet og tas ut kvelden etter hvis kilden fortsatt ikke gir kurser (`valg.uten_rader`). Alternativet er å legge til: «Gir kilden ingen kurser ved neste henting, tas den ut av lista.» Funnet står åpent til gruppen har svart (regel 25).
11. **Boblen på siden i demoen (tillegg 12).** *Forslag 1, som bygget:* «Nøkkelen? Den ligger under matta, sammen med de 20 kallene.» *Forslag 2:* «20 kall i døgnet: jeg bruker 18 og sparer 2 til en regnværsdag.» Begge handler om nøkler og kall, ikke om kurser eller kjøp og salg (NFR-06).
12. **Brikkene i «Følg en aksje» (tillegg 17).** *Forslag:* tallet på en brikke er alle aksjene i bransjen som kan følges, uavhengig av omsetningen og søket, så det står fast mens man velger. En bransje med 0 er grå med stiplet kant og `disabled`; er den alt valgt i adressen, kan den fortsatt velges bort. Med skriptet filtrerer og sorterer siden med en gang, «Alle» tar bort bransjene uten å laste siden, begge «Vis» er skjult, og adressen følger valget (`history.replaceState`), så en ny lasting og lenken viser det samme. Uten skriptet sender «Vis» skjemaet som før.
13. **Min liste med «Vis dagen» (tillegg 17).** *Forslag:* overskriften i Min liste står som før. Der er radene siste børsdag, og den valgte dagen står som linja under hver rad (8.17b, «Sammenlign med»), så overskriften sier alt dagen tabellen viser. På oversikten viser tabellen radene for den valgte dagen, og der følger overskriften og linja om 3 av 3 dagen. Alternativet er å legge til dagen det sammenlignes med, for eksempel «… skilte seg ut fredag, sammenlignet med tirsdag 06.10».
14. **«Oppdatert …» på alle sidene (tillegg 17).** *Forslag:* en side uten eget tidspunkt («Følg en aksje», «Er du sikker?», Innstillinger, investorsiden, aksjesiden uten kurser og siden for eodhd.com i demoen) viser det samme som oversikten: det eldste tidspunktet en aksje med kurser sist ble hentet (FR-101). Linja mangler bare når basen ikke kan leses eller ingen aksje har kurser ennå, fordi det da ikke finnes et tidspunkt. På aksjesiden uten kurser gjelder tidspunktet de andre aksjene; siden sier selv at aksjen ikke har kurser.
15. **Tilleggene som kom sent (tillegg 5, 7, 9, 13, 14 og 16).** Tilleggene 5, 7, 9, 13, 14 og 16 kom til vinduet 11.11 kl. 22:24–22:25, etter tillegg 20, og tillegg 15, som stoppet kl. 20:46 fordi det bygger på tillegg 14, er bygget med tillegg 14. Tillegg 11 er ikke limt inn i vinduet. *Forslag:* tillegg 11 bygges når det kommer, som et eget tillegg.
16. **«Signalet forklart» og «Børsdagen kort fortalt» i omvisningen (tillegg 20).** *Forslag:* stegene peker på delene (`ki-teksten` og `boersdagen-kort-fortalt`), som bare finnes når delen vises, så de hoppes over ellers. Tittelen på steget står i dataene for omvisningen på alle sidene, så testene som sier at «kort fortalt» ikke står på en side, ser bort fra `data-steg` (seks tester i fire filer).
17. **Kolonnen i omvisningen (tillegg 18, steg 3).** *Forslag:* steget merker overskriften og de tre første radene med kolonnens celler, med en oransje ramme og lys oransje bakgrunn i radene. Raden «Skilte seg ut» mellom overskriften og radene er ikke med, fordi den går over hele tabellen. Dekker boksen det merkede nederst til høyre, flyttes den til venstre. Uten tabell, som i en tom Min liste, hoppes stegene over.
18. **Bryteren «Vis KI-tekst» (tillegg 18, steg 2).** *Forslag:* bryteren på aksjesiden heter også «Vis KI-tekst», som i Innstillinger og ved «Børsdagen kort fortalt», og alle tre har samme skrift (16 px, ikke 14), høyde, kant, knott og farger. Navnet på aksjesiden var «KI-tekst» fra 8.2b; testen for 8.2b er rettet.
19. **«Følg flere aksjer» (tillegg 14 og 15).** *Forslag:* «Egen» står ved aksjene du følger selv, og «Utenfor målingen» bare ved dem, fordi omsetningen bare er regnet for dem. En aksje som venter etter «Følg», står ikke i kortene ennå, men telles i «Appen følger N av 18» og rutene, som overalt ellers. En bransje som ikke er en av de 13, står sist som «Uten bransje». Med «Vis hjelp» av står teksten om kallene ikke på siden; den står i steg 3.
20. **Hjelpetekstene (tillegg 18, steg 1).** *Forslag:* tekstene i tabellen under, alle på høyst 50 ord. «Hovedindeksen» har DEMIX i samme vindu fra del 2 (`hovedindeksnavnet`). Ordene som er tatt ut, som lenken under søylene, «fra»-datoen ved en periode og hvordan en aksje fjernes før hentingen, står i `docs/hjelp.md`. «kilden» er byttet med EODHD, også i forklaringen på hvorfor en aksje er uten kurser (spørsmål 10).
21. **Overskriften i Min liste med «Vis dagen» (tillegg 17).** Se spørsmål 13.
22. **Den første knappen og vinduet for kursgrafen (tillegg 5, gjennomgangen VG3, middels).** Vinduene på aksjesiden og børsometeret har høyst 60 ord (8.20a, svaret 06.11 kl. 23:07), og vinduet for kursgrafen har 60 ord fra før når en periode er valgt. *Forslag:* setningen om den første knappen står ved periodevalget på oversikten, i Min liste og på børsometeret, men ikke i vinduet for kursgrafen på aksjesiden. Den er kortet til «Den første knappen heter etter dagen kursene er fra.», og «I dag», «I går» og ukedagen står i `docs/hjelp.md`. Ringen sier bare «Uten ring: 0 eller 1 av 3.», med de samme ordene som rammen. Alternativet er å la vinduet for kursgrafen få flere enn 60 ord. Funnet står åpent til gruppen har svart (regel 25).

## Delene

Hver del har tester med «Ville feilet hvis» i `tests/test_vis_meg_rundt_8_26.py`, og én mutant.

### 1) «Vis meg rundt» spiller av siden, og knappene øverst (kl. 16:58 og 17:06)

**Ville feilet hvis:** «Vis meg rundt» hadde andre steg enn sidens egne, et steg sendte brukeren til en annen side, siste steg manglet «Ferdig» eller lenken til hele omvisningen, knappene ikke sto i raden etter «Innstillinger» med hvert sitt ikon, lista fra 8.9 eller raden under demolinja sto igjen, eller det var ulikt i demoen og den ekte versjonen.

### 2) Funnene fra demoprøven (kl. 17:06, 17:12 og 17:21)

- **Hjelpevinduet** har nederst «Lukk med «Lukk», Esc eller et nytt trykk på samme «?».». Et nytt trykk og Esc lukker et popover også uten skriptet, så linja stemmer i begge tilfeller.
- **«Slik leser du tabellen»:** feltet med de tre brikkene vokser med dem (`:has(> .utslagsfelt)`), med 6 px luft over og under, så brikkene står innenfor den grå ruta og ikke inntil overskriften. De andre feltene, pilene og pekeren, er lavere enn 36 px og står som før.
- **«?» ved Hovedindeksen** sier først «OSEBX er hovedindeksen på Oslo Børs. I demoen heter den oppdiktede indeksen DEMIX.», som en egen tekst (`hovedindeksnavnet`), fordi en tekst har høyst tre setninger (8.0c). Det står likt i begge versjonene.
- **«Dine egne aksjer»:** tabellen står på oversikten, også under «Min liste» der, og ikke på siden Min liste, som har «Din egen liste». Den har nå navnet med «Egen» og «Utenfor målingen» og ticker med bransjeikonet under, uten egen bransjekolonne, og «Angre» og «Fjern» som en liten knapp til høyre.
- **«Lista er full …»** står i en boks som meldingen om endringer som venter, ikke i rødt. Teksten endres i del 5 (tillegg 3).
- **Bryterne ved KI-teksten** er oransje med blekk-knott, som i Innstillinger, og «Laget av KI» står grått som før. Det endrer spørsmål 5 i 8.2b og testen fra 8.23 (`test_bryteren_ved_ki_teksten_er_oransje`).

**Ville feilet hvis:** et hjelpevindu manglet linja om lukkingen, brikkene sto utenfor ruta, «?» ved Hovedindeksen ikke sa hvilken indeks det er, «Dine egne aksjer» hadde bransjekolonnen eller en stor knapp, beskjeden om full liste var rød, eller en KI-bryter ikke var oransje.

### 6) Filteret og lenken «Den ekte versjonen» (tillegg 4, ønskene kl. 17:48 og 17:53)

- **Filteret** er tatt bort: raden «Alle», «3 av 3 positiv» og «3 av 3 negativ», linja «Filteret viser hva sjekkene ga …», lenken til dem som fikk 2 av 3, adressene `?signal=` (en gammel adresse med `?signal=` viser alle radene) og det som bare fantes for filteret i `app.py` og stilen. «Alle | Min liste» står, og at signalstyrken ikke er et råd, står i innledningen på oversikten (NFR-06). Filteret står i PRD-en som FR-108, med FR-412 i lista over det ekstra; Rettet-linja står under FR-108, og under 8.11 og 8.23 i `epics.md`. Testene for filteret i `test_ferdige_lister.py` og `test_funnene_8_23.py` er tatt bort, og hjelpen og installasjonen er rettet.
- **«Den ekte versjonen»** i demolinja åpnes i en ny fane, med `target="_blank"`, `rel="noreferrer"`, pila ↗ og «(åpnes i en ny fane)» for skjermlesere, som lenken til investorsiden. Adressen er den samme (`EKTE_VERSJONEN_URL`). Det er den eneste lenken ut av appen som åpnet i samme fane; en test sjekker alle malene.

**Ville feilet hvis:** filteret, linja om det eller adressene sto igjen, `?signal=` skjulte rader, setningen om råd ble borte fra oversikten, eller en lenke ut av appen åpnet i samme fane.

### 4) «uten data» sier hvorfor (tillegg 2, ønsket kl. 17:44)

- `UTEN_DATA_TEKST` i `markedsoversikt.py` er «ingen kurser ennå», og båndet over radene sier «N uten kurser». `UTEN_DATA` i `boersometer.py` er «Ingen kurs», og tabellen under kartet og `title` sier «Ingen kurser ennå»; styrken i tabellen er «–», så teksten ikke står to ganger.
- Hjelpen «Ingen kurser ennå» i vinduet «Oppdatert» og «Ukjent» bak «?» ved Retning er rettet, og `docs/hjelp.md` om demoen.
- Testene som så etter «uten data» som tekst på sidene, er rettet til de nye ordene; kommentarene og docstringene står.

**Ville feilet hvis:** en side fortsatt sa «uten data», raden for MTFJ i demoen ikke sa «ingen kurser ennå», ruta ikke sa «Ingen kurs», teksten ikke fikk plass i en stor rute, eller «Ukjent» ikke forklarte en aksje uten kurser.

### 3) Fotnoten og de løse tekstene (tillegg 1, ønsket kl. 17:44)

**Fotnoten** under tabellen på oversikten og i Min liste («Sluttkursen er den ujusterte kursen …») er tatt bort. Det den sa, står bak «?»: Sluttkurs sier «uten utbyttejustering», Endring sier «justert for utbytte» og at et ordinært utbytte ikke ser ut som et kursfall, og Signalstyrke sier hvor mange av de 3 sjekkene som slo ut, og at det ikke er et råd. Ingen tekst bak «?» måtte endres. At signalstyrken ikke er et råd, står synlig i innledningen på oversikten (som før) og i Min liste (setningen fra fotnoten er lagt til innledningen der), så NFR-06 står på begge (Rettet-linje i raden for NFR-06 i `epics.md`). Kilden for «sluttkurs» i `hjelpetekster.py` var fotnoten; nå er den PRD-en alene. Vurderingsmatrisen og kvalitetssikringen viser ikke til denne fotnoten, så de er ikke endret.

**De andre løse tekstene.** Forslaget for hver; beskjeder som bare står i demoen eller bare når noe gjelder, står til gruppen har svart (tillegg 1, steg 2).

| Side | Teksten | Forslag | Grunnen |
|---|---|---|---|
| Aksjesiden | Innledningen «Siden viser sjekkene for … med tallene bak, kursgrafen og det appen skrev om aksjen hver børsdag.» (U62) | Ta bort (bygget) | Overskriftene og «Vis meg rundt» sier det samme. |
| Aksjesiden | «Linjene er kursen og 50-dagers snittet …» under grafen | Behold | Tegnforklaringen for grafen, som ikke står andre steder. |
| Aksjesiden | «Signalet bygger bare på kurs og volum …» i «Signalet forklart», og «Signalstyrken sier ikke om du bør kjøpe eller selge.» uten sjekker | Behold | NFR-06. |
| Aksjesiden | «Laget av KI. Regelforklaringen over …» | Behold | Merket for KI-teksten. |
| Aksjesiden | Ingressen under «Mine notater» og «Signalet dag for dag» | Behold | Sier hvor notatene lagres og hvordan man velger en dag. |
| Børsometeret | Innledningen «Hver rute er en aksje …, ikke hva du bør kjøpe eller selge.» | Behold | Sier hvordan kartet leses, og NFR-06. |
| Børsometeret | «Datoen kunne ikke leses …», «… er før første kurs …», «Gul ramme betyr 3 av 3 …», «Ikke vurdert» kan også ha en annen grunn …» | Står til gruppen har svart | Bare når noe gjelder. |
| Min liste | «Stjernen foran et selskap legger aksjen i lista …» | Behold, med setningen om signalstyrken | NFR-06 etter fotnoten. |
| Min liste | «Øverst i hver rad står siste børsdag …» med «Velg dag» eller en periode | Står til gruppen har svart | Bare når en dag eller periode er valgt. |
| Min liste | «Ingen aksjer i Min liste ennå …», «Ingen notater ennå …» | Står til gruppen har svart | Bare når lista er tom. |
| Min liste | Ingressen under «Mine notater» | Behold | Sier hva man kan gjøre der. |
| Oversikten | Meldingen om endringer som venter, og eksempelet i demoen | Står til gruppen har svart | Bare når noe venter, eller bare i demoen. |
| Oversikten | «Tabellen viser …» og «Endringen gjelder …» med «Velg dag» eller en periode | Står til gruppen har svart | Bare når en dag eller periode er valgt. |
| Oversikten | Fotnoten om «ikke vurdert» | Står til gruppen har svart | Bare når en dag ikke er vurdert. |
| Innstillinger | «Valgene gjelder alle sidene og lagres på denne maskinen.» | Behold | Ordrett fra utdraget §4, og testet. |
| Innstillinger | Forklaringene under bryterne | Behold | De forklarer bryteren rett over. |

**Ville feilet hvis:** fotnoten sto igjen, forbeholdet ikke sto synlig på oversikten og i Min liste, «?» ved kolonnene ikke sa det fotnoten sa, eller innledningen på aksjesiden sto igjen.

### 5) Stjernen ved «Følg», aksjene som venter, og «lista» (tillegg 3, svaret kl. 17:47)

- **Filene:** `src/migrasjoner/0013_stjerne_ved_folg.sql`; `folg()` og `angre()` i `src/valg.py` skriver og sletter stjernen i samme transaksjon som ønsket; `SqliteMinlistelager` godtar og leser stjernen på en aksje som venter (`merkede_som_venter`); `rader_som_venter` og `VENTER_TEKST` i `src/markedsoversikt.py`; radene, tallet og båndet i `src/app.py` og `index.html`; ordene i `_egne.html`, `folg.html` og `valg.py` (`FULL`, `FULL_ANGRE`).
- **Testene som teller migrasjonene**, sier versjon 13, og testene for hvem som skriver `min_liste`, har `valg.py` med en kommentar: `folg()` og `angre()` kalles bare av webserveren.
- **Likt i begge versjonene:** demoen henter aldri, så en aksje man følger der, står alltid nederst med «venter på henting». En test viser det samme i den ekte versjonen med en testbase.

**Ville feilet hvis:** «Følg» ikke ga stjerne og rad med en gang, skrev noe annet enn ønsket og stjernen, stjernen ikke kunne tas bort og settes igjen, «Angre» lot stjernen stå, tallet i overskriften talte en aksje som venter, triggeren godtok et ukjent symbol, eller sidene sa «aksjer i lista» og «Lista er full».

## Bildene

Bildene i `docs/appen/` er tatt på nytt fra demoen etter delene (`947b1d79`), med de nye høydene for bildene av hele siden, og avtrykkene er regnet ut på nytt. Bildene før og etter, også ved 390 px, og bilder av «Vis meg rundt» og en aksje som venter, står i PR-en fra bildegrenen `pr-8-26-bilder`. I bildet av investorsiden sto «(åpnes i en ny fane)» synlig i demolinja; det er rettet i `16aded4d`, med en test.

## Mutantene

Én per del, med kopi før og sha256 mot HEAD etter; alle ble fanget av `tests/test_vis_meg_rundt_8_26.py`, og hver fil var lik HEAD etterpå:

- Del 1 (`e06fa3e6`): uten lenken «Spill av hele omvisningen» i `hjelp.js`.
- Del 2 (`d24de09a`): bryteren ved «Børsdagen kort fortalt» i blekk igjen.
- Del 3 (`1b180fcf`): fotnoten satt inn igjen i `index.html`.
- Del 4 (`4d2ee9ec`): `UTEN_DATA_TEKST` «uten data» igjen. Fanget i demoen; testbasen for den ekte versjonen har ingen aksje uten kurser, så den varianten besto.
- Del 5 (`c922edcc`): uten stjernen i `valg.folg()`.
- Del 6 (`8846fbc1`): lenken «Den ekte versjonen» uten `target="_blank"`.

## Gjennomgangen 11.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen fra `7fd5320c`, uten bildene; Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 17 funn, Edge Case Hunter 9 og Verification Gap 9. Ingen høye.

*Middels*
- *ECH1 og BH4, rettet.* «Spill av omvisningen» mens boksen fra «Vis meg rundt» var åpen, spilte bare siden. Nå lukker `start()` boksen først. Prøvd i Edge: fra steg 2 av 4 på børsometeret til steg 1 av 23 på `/`.
- *ECH2, rettet.* En side fra hurtigbufferen beholdt stegene for siden; `oppstart()` setter hele omvisningen tilbake.
- *ECH3, BH10, BH11 og VG4, rettet.* Tallene sprikte når en aksje venter: overskriften talte den ikke, men radene, «Min liste» og «appen følger» gjorde. Nå teller alle den (spørsmål 7).
- *ECH4 og VG5, rettet.* «Ingen kurser ennå» sto også for en aksje med kurser, men uten kurs på dagen. Nå sier tabellen og `title` «Ingen kurs den dagen» da (`aldri_kurs`).
- *BH1, rettet.* En påstand i `test_tallene_foelger_konstantene` hadde havnet i en kommentar.
- *BH2 og ECH5, rettet.* En stjerne fra «Følg» ble liggende når ønsket ble avvist eller slettet, og kunne følge med aksjen fra en ferdig liste. Nå ryddes den (`_rydd_stjernene`). At en aksje fra en ferdig liste ikke får stjerne, følger av svaret, som gjelder «Følg», og hjelpen sier «med «Følg»».
- *BH8 og VG2, rettet.* Testen av triggeren prøvde ikke et ønske som er avvist eller tatt i bruk, et ønske om å fjerne eller UPDATE.
- *VG3, rettet.* «Angre» i et bytte har en test.
- *VG1, åpent, spørsmål 9.* Testene av boksen søker i kildeteksten; ingen test kjører siden i en nettleser. Forslaget er å la det stå, med prøvingen i Edge. *Lukket 12.11 med svaret kl. 10:16:* godtatt som bygget.

*Lav*
- *Rettet:* ECH7 (en aksje som venter, står ikke med «Velg dag»), BH15 (kommentarene om høydene i `test_docker.py`), BH16 («Ukjent» og hjelpen om raden sier «venter på hentingen» og at raden ikke har lenke), BH17 (docstringen sier 13), VG7 (kommentarene ved `SqliteMinlistelager` og `_SKRIVERE`).
- *Ført:* BH3 og ECH6 («Angre» tar også en stjerne som fantes før, for en aksje som var tatt ut og følges igjen; den står da også uten lenke mens den venter), BH5 (knappen «Vis meg rundt» står bare når dataene for omvisningen kan leses, som på alle sidene med knappen), BH6 (lenken «Spill av hele omvisningen» er en lenke med `href="#"`), BH7 (ingen egen fokusring for sideknappene, verken lenkene eller knappene), BH9 (som VG1), BH12 (`FULL` sier 18 også når testene endrer `TAK`), ECH8 (en base på versjon 12 gir feil ved «Følg»; webserveren migrerer når den starter), ECH9 (telleren og tre steg med samme anker, som BH11 i 8.25), VG6 (testen for lenker ut av appen søker etter `http` og to variabler), VG8 (stegene på knappen er bare sammenlignet på børsometeret og i 8.9-testene), VG9 (testene for brikkene og fargen søker i stilen).
- *Ikke en feil:* BH13 (oversikten sier «ikke hva», Min liste «ikke om»; begge er NFR-06), BH14 (sitatet «Sluttkursen vises som `close`» står i PRD-en, og kildetesten slår det opp).

### 7) Siden står i ro (tillegg 6, ønsket kl. 19:36)

- Periodevalget på oversikten, i Min liste og på børsometeret har ankeret `#perioden` på raden over (`PERIODEANKER`), som aksjesiden har `#kursgrafen` (8.2a, U36): knappene, pilene og skjemaet for «Vis dagen» går dit. Filteret i «Følg en aksje» har `#filteret`, «Alle» og «Min liste» i Min liste `#visvalget`, og bryterne i Innstillinger sender tilbake til bryteren (`INNSTILLINGSANKER`). `scroll-margin-top: 16px` gir luft over. Omvisningen sammenligner adressen uten ankeret (`her()`), og steget `velg-dag` finnes som før.
- Prøvd i Edge mot demoen, ved 1280 og 390 px: etter et trykk på «1 uke» står periodevalget 16 px fra toppen på oversikten, i Min liste og på børsometeret, og filteret i «Følg en aksje» etter et klikk på en bransje (58 px ved 1280 px, der siden ikke kan rulles lenger). Før sto alle sidene på toppen. Bildene før og etter står på bildegrenen.

**Ville feilet hvis:** en lenke eller skjemaet i periodevalget manglet ankeret, ankeret ikke fantes eller sto to ganger, aksjesiden mistet ankeret, filteret i «Følg en aksje» eller bryterne i Innstillinger sendte til toppen, eller omvisningen så på ankeret.

### 8) De samme ordene overalt (tillegg 8, ønsket kl. 19:51)

- «ingen kurser ennå» kommer fra én konstant (`UTEN_DATA_TEKST`) i raden på oversikten og i Min liste, ruta, `title` og begge kolonnene i tabellen på børsometeret, aksjesiden og hjelpen bak «?» ved «Oppdatert». Forklaringen (`UTEN_KURSER_HVORFOR`) står bak «?» og på aksjesiden, og i demoen setningen om Matfjord Merkevarer (`DEMO_UTEN_KURSER`, navnet fra `UTEN_KURSER` i `demo.py`), på aksjesiden bare for den aksjen. En test finner alle stedene for MTFJ og feiler hvis ett sier noe annet.
- Ruta har ikke plass til teksten i den store utformingen (`STOR`), så den får den vanlige; den er prøvd i Edge ved 1280 og 390 px uten at teksten kuttes. En aksje med eldre kurser, men uten kurs på dagen, står med «Ingen kurs» i ruta og «Ingen kurs den dagen» i `title` og tabellen.

**Ville feilet hvis:** ett av stedene sa noe annet enn «ingen kurser ennå», forklaringen manglet bak «?» eller på aksjesiden, demoen ikke sa hvilken aksje som med vilje er uten kurser, eller den ekte versjonen sa det.

### 9) Lenkene (tillegg 10, ønsket kl. 20:06)

- En felles regel `a { color: inherit; … }` i `stil.css`, med understreken fra navnene i tabellene. Stilarket går foran nettleserens, også for en besøkt lenke, og `a` er svakest, så lenker med egen farge, som i demolinja og `.knapp`, står som før. `:where(a)` ble prøvd først, men testen for stilarket krever at `:where` bare avgrenser til en side.
- Prøvd i Edge etter et besøk på aksjesiden for NLYS: navnet i notatet i Min liste er `rgb(22, 24, 29)`, som navnene i tabellen; før var det nettleserens blå (`rgb(0, 0, 238)`). Bildene før og etter står på bildegrenen.

**Ville feilet hvis:** lenkene ikke hadde en felles regel med `color: inherit`, eller en regel ga en lenke nettleserens blå eller lilla.

### Mutantene for tilleggene

- Tillegg 6 (`2f71e9d1`): periodevalget på børsometeret uten ankeret.
- Tillegg 8 (`2f71e9d1`): «Uten data» i kolonnen for styrken på børsometeret.
- Tillegg 10 (`c6083134`): regelen for `a` uten `color: inherit`.

Alle ble fanget av `tests/test_vis_meg_rundt_8_26.py`, og hver fil var lik HEAD etterpå.

### Gjennomgangen av tilleggene 6 og 8

Blind Hunter med bare diffen fra `059a4228`, og Edge Case Hunter og Verification Gap med repoet. Blind Hunter hadde 16 funn, Edge Case Hunter 7 og Verification Gap 7.

*Høy*
- *VG1, rettet.* Testen for «Ingen kurs den dagen» så bare i malteksten, og ruta sa «Ingen kurser ennå» også for en aksje med eldre kurser (ECH1, BH1, BH2, VG3). Nå skiller ruta på `aldri_kurs`, og en test tegner ruta med en aksje som har eldre kurser.

*Middels*
- *ECH1, BH1, BH2 og VG3, rettet* med VG1.
- *ECH2, BH3 og VG2, åpent, spørsmål 10.* Forklaringen fra tillegg 8 sier «venter på hentingen» om en aksje som står i lista uten kurser. *Lukket 12.11 med svaret kl. 10:16:* rettet i del 14 (tillegg 22).

*Lav*
- *Rettet:* BH4 (setningen om demoen bare på siden for MTFJ), BH6, ECH3 og VG4 (ankeret i Innstillinger slås opp før noe skrives, og en test knytter ankrene til valgene), BH12 (kommentaren i stilen), BH16 (hjelpen), ECH6 (kommentarene i `boersometer.py`), ECH7 («Alle» og «Min liste» i Min liste holder plassen).
- *Ført:* BH5, ECH4 og VG5 (teksten i ruta er ikke regnet for nivå 2 og 3; prøvd i Edge, der MTFJ står på nivå 1), ECH5 (en dag før første kurs sier «Ingen kurser ennå»), BH8 og VG6 (regexen for lenkene og testen av ankeret i omvisningen), BH9 (samletesten sammenligner uten stor forbokstav), BH10 (hjelpetekstene importerer demodataene), BH13 (stor forbokstav regnes to steder; samletesten sammenligner dem), BH14 (`test_notater` sletter også versjon 13), BH15 (testen for pila i demolinja), VG7 (`scroll-margin-top` er ikke testet).
- *Ikke en feil:* BH7 (de to radene med periodevalget utelukker hverandre, som ECH fant), BH11 (en tom tittel står ikke).

### 10) «Din egen liste» som på tavla, og siden i demoen (tillegg 12, svaret kl. 20:28)

- **Kortene:** tittelen i Newsreader ved tallet i den svarte boblen, kort tekst og én handling nederst, og like høye kort (`display: flex` og `margin-top: auto`). Steg 1 har knappen «Åpne eodhd.com ↗»: i den ekte versjonen `https://eodhd.com/register` (`EODHD_REGISTRERING`, samme adresse som startskriptet) i en ny fane, og i demoen `/eodhd-demo`. Svaret kl. 14:29 på spørsmål 9 i 8.22 har Rettet-linje i spesifikasjonen for 8.22 og i `epics.md`, og kontrollpunktet i `test_hjelpetekster.py` godtar akkurat den lenken. Steg 2 har statusen som én linje med ✓, og «Slik bytter du nøkkel» bak «?». Steg 3 har teksten fra tavla, de ferdige listene som brikker med ikonet og antallet, og «+ Følg en aksje»; kallene, regnet av lista som spørsmål 10 i 8.22 sa, og bransjelistene står bak «?» (hjelpevinduet har fått `linjer` for tall siden har regnet ut).
- **Siden i demoen:** `/eodhd-demo` (`eodhd_demo.html`), bare i demoen, i oppsettet fra investorsidene: «Tilbake til Min liste», tegningen `src/static/demo/eodhd.svg` laget av KI i samme stil som de 15, boblen etter forslag 1 i spørsmål 11, «Illustrasjon laget av KI» og teksten nederst. I den ekte versjonen svarer ruta 404. Prøvd i Edge ved 1280 og 390 px; der står boblen under tegningen, som på investorsidene.
- **Testene fra 8.22** som så etter adressen som tekst, kallene i steg 3, `<h5>Slik bytter du nøkkel</h5>` og avsnittet «Start fra en ferdig liste», er rettet til det nye oppsettet.

**Ville feilet hvis:** et kort manglet tallet ved tittelen eller handlingen nederst, demoen lenket til eodhd.com, den ekte versjonen ikke åpnet registreringen i en ny fane med adressen fra startskriptet, kallene eller byttet av nøkkel sto i kortene, eller siden i demoen manglet en av delene eller sa noe om kurser.

### Gjennomgangen av tilleggene 10 og 12

Blind Hunter med bare diffen fra `99d0d24a`, og Edge Case Hunter og Verification Gap med repoet. Blind Hunter hadde 14 funn, Edge Case Hunter 9 og Verification Gap 7. Ingen høye. Mutanten for tillegg 12 (demoen lenket til eodhd.com) ble fanget av `test_demoen_lenker_aldri_til_eodhd`, og fila var lik HEAD etterpå.

*Middels*
- *ECH1, BH2 og VG1, rettet.* Med «Vis hjelp» av forsvant byttet av nøkkel og kallene fra siden, og statusen viste til en «?» som ikke fantes. Nå står de i kortene da, med en test.
- *BH3, rettet.* Steg 3 sa «dagens 15» fast; nå antallet appen følger, og den ferdige lista nevnes bare når det finnes en (ECH2).
- *BH1, ikke en feil.* Diffen Blind Hunter fikk, begynte etter tillegg 10. Edge Case Hunter gikk gjennom regelen for `a` i repoet og fant ingen lenke med egen farge som ble overstyrt.

*Lav*
- *Rettet:* BH6 og ECH5 (tittelen sto to ganger), ECH4 (stilen på kallene i vinduet), ECH8 (hjelpen sa «under»).
- *Ført:* BH4 og ECH3 (teksten om kallene bruker konstantene fra `valg.py`, linjene regnes av lista), BH5 (linjene står etter tekstene i vinduet), BH7 (setningen om «Følg en aksje» og overskriften «Start fra en ferdig liste» er tatt bort med tavla), BH8 («Åpne eodhd.com» går i demoen til siden som sier at det er demoen), BH10 og ECH9 (plassen til boblen er i rammen på 560 × 400, som på investorsidene), BH11, BH12, BH13, VG2–VG7 (svakere testvakter), BH14 (tonen i boblen; spørsmål 11 har et annet forslag), ECH6 (siden i demoen har data-side for Min liste og leser lista), ECH7 (✓ i grønt).
- *Ikke en feil:* BH9 (`.skjult` i kortene er avgrenset til oversikten, som Min liste er).

### 11) Brikkene, overskriften med «Vis dagen», «3 av 3» og «Oppdatert» (tillegg 17, svaret kl. 22:04)

- **Brikkene i «Følg en aksje»:** hver bransje viser antallet aksjer som kan følges, og en bransje med 0 er grå og kan ikke velges (spørsmål 12). Alle radene står i siden med bransjen, omsetningen, medianen og rangen som `data-`, og `FOLGLISTA` i `hjelp.js` filtrerer og sorterer som `ferdige_lister.filtrer` og `.sorter`. Med skriptet oppdateres lista med en gang ved klikk på en brikke, en omsetning eller en sortering, og «Vis» står bare uten skriptet. Søket står som før.
- **Overskriften med «Vis dagen»:** på oversikten sier overskriften dagen tabellen viser, og «N av 15» og linja om 3 av 3 regnes av radene den dagen, med styrken mot terskelen (radene for en annen dag merker ikke 2 av 3, 8.17a). Med en periode og ved siste børsdag står det som før. Min liste i spørsmål 13.
- **«3 av 3» uten en eneste vurdering:** `AlleSjekkene.vurdert` er usann når aksjen bare har grunner, og «Signalet dag for dag» sier da «Signalet er ikke regnet ennå:» med grunnen øverst på siden, for Varde Systemer «Trenger 51 dager for å regne signal, fikk 30.».
- **«Oppdatert …»:** `_oppdatert_overalt` gir `hentet_felles` til rammen for sidene med basen, og rammen bruker det når siden ikke har sitt eget tidspunkt (spørsmål 14).

**Ville feilet hvis:** en brikke manglet antallet eller en bransje med 0 kunne velges, serveren bare sendte radene i filteret, skriptet ga en annen rekkefølge eller andre rader enn serveren, «Vis» sto med skriptet eller et klikk lastet siden, overskriften sa fredag over tabellen for tirsdag, antallet eller linja om 3 av 3 var fra siste børsdag, en periode fikk en annen overskrift, Varde Systemer fikk «3 av 3 aldri», eller en av sidene manglet «Oppdatert» eller viste et annet tidspunkt enn oversikten.

### 12) Tilleggene 5, 7, 9, 13, 14, 15, 18, 19 og 20 (11.11 kl. 22:15–22:25)

- **Tillegg 5, den første knappen:** «?» ved periodevalget på oversikten, i Min liste og på børsometeret sier «Den første knappen heter etter dagen kursene er fra.» (`foerste_knapp`; kortet og uten kursgrafen etter gjennomgangen, spørsmål 22), og demoen i tillegg «I demoen er det fredag 09.10, den siste dagen med oppdiktede kurser.», regnet av `SLUTTDATO` i `demo.py` (`foerste_knapp_demo`).
- **Tillegg 7, uten ramme:** forklaringen på børsometeret har en prøve uten ramme og «Uten ramme: 0 eller 1 av 3.», og «?» ved signalstyrken på oversikten, i Min liste og på aksjesiden sier «Uten ring: 0 eller 1 av 3.». «0 eller 1» regnes av terskelen (`UNDER_TERSKELEN`).
- **Tillegg 9:** filteret var tatt bort i del 6; testen dekker nå også «Alle» i Min liste og «3 av 3 negativ», i begge versjonene.
- **Tillegg 13:** «Start fra en ferdig liste» sto bare i steg 3 etter tillegg 12, med `#ferdige-lister`; en test sier det, og at «Avbryt» går dit.
- **Tillegg 14 og 15, «Følg flere aksjer»:** overskriften med «?» (kallene og gratiskontoen, regnet av kvoten, taket og lista), «Appen følger N av 18» med «, som er taket.» eller «, N plasser ledige.», og en strek med 18 ruter, skjult for skjermlesere. Under står «Bytt ut en aksje for å følge en annen. Byttet skjer ved neste henting.» når lista er full, og ellers «Følg en aksje til, eller bytt ut en. Endringen skjer ved neste henting.» med «+ Følg en aksje». Aksjene står i hvite kort per bransje, i rekkefølgen på børsometeret, med navnet som lenke, tickeren, merkene og en liten «Bytt ut»; tre kolonner på bred skjerm, to under 900 px og én under 600 px.
- **Tillegg 18:** se spørsmål 17, 18 og 20, og tabellen under.
- **Tillegg 19:** eksempelboksen i demoen er tatt bort (Rettet-linje under spørsmål 14 i spesifikasjonen for 8.23). En endring som venter, står som før.
- **Tillegg 20:** stegene «Børsdagen kort fortalt» og «Signalet forklart» (spørsmål 16), og hele omvisningen hopper over «Dagen og perioden» på børsometeret og «Signalstyrken» og «Retningen» i Min liste (`GJENTATT_I_OMVISNINGEN`); «Vis meg rundt» har dem. README-en har setningen etter dobbeltklikket, og linja under «Ekstra, ferdig» er rettet.

**Ville feilet hvis:** setningen om den første knappen manglet ved et av periodevalgene, demoen ikke sa fredag 09.10 eller datoen var skrevet for hånd; prøven eller setningen om rammen manglet, eller en side sa det med andre ord; filteret sto på en av sidene; de ferdige listene sto under «Følg flere aksjer»; tallet, rutene, setningen eller kortene i rekkefølgen på børsometeret manglet; en hjelpetekst hadde over 50 ord eller ordene «basen», «kilden» eller «kontrollsjekken»; bryterne var ulike; et kolonnesteg merket hele tabellen; eksempelboksen sto i demoen; et KI-steg manglet, eller omvisningen hadde stegene som gjentas.

### Hjelpetekstene før og etter (tillegg 18, steg 1)

Alle tekstene i `hjelpetekster()` som er endret i storyen, regnet av main (`db89c5ba`) og grenen, med ordene telt med `\w+` som i kontrollene av briefen. Tekstene som ikke står her, er uendret og på høyst 50 ord.

| Tekst | Før | Ord før | Etter | Ord etter |
|---|---|---|---|---|
| `boersdagen_kort_fortalt` | Et kort sammendrag av børsdagen, skrevet av en språkmodell (KI). Modellen fikk bare det appen regnet ut: om hovedindeksen steg eller falt, hvor mange aksjer som gjorde det bedre enn indeksen, hvor mange som skilte seg ut og med hvilken retning, med navnet, styrken og retningen for høyst fem, hvor mange som steg i hver bransje med minst to aksjer med en endring, bransjen som steg mest og den som falt mest i snitt, om flere eller færre enn vanlig skilte seg ut, og om hovedindeksen steg eller falt de siste fem børsdagene, med ukedagen og antallet aksjer i lista, og ingen prosenter, kurser eller nyheter. Teksten sjekkes før den vises: tall med prikket strek står i det modellen fikk, og den gir ikke råd. | 125 | Et kort sammendrag av børsdagen, skrevet av en språkmodell (KI). Modellen fikk bare det appen regnet ut: hovedindeksen, aksjene som skilte seg ut og bransjene, ingen kurser eller nyheter. Teksten sjekkes før den vises: tall med prikket strek står i det modellen fikk, og den gir ikke råd. | 48 |
| `boersometeret_ruta` | For én dag følger størrelsen volumet mot vanlig, og for en periode er rutene like store. Gul ramme er 3 av 3 og mørk 2 av 3, begge siste børsdag. | 30 | For én dag følger størrelsen volumet mot vanlig, og for en periode er rutene like store. Gul ramme er 3 av 3 og mørk 2 av 3, begge siste børsdag. Uten ramme: 0 eller 1 av 3. | 37 |
| `bytt_noekkel` | – | – | Slett det som står etter EODHD_API_KEY= i fila .env i mappa til appen. Neste gang den ekte versjonen startes med startskriptet, spør det etter nøkkelen og lagrer den nye. | 29 |
| `bytt_noekkel_docker` | – | – | Med Docker, eller uten startskriptet, skriver du den nye nøkkelen etter EODHD_API_KEY= selv og starter appen på nytt. Siden har ikke noe felt for nøkkelen, fordi den aldri rører den. | 30 |
| `dine_egne_aksjer` | Lista kan ha opptil 18 aksjer, og aksjer du følger selv, står i tabellen sammen med de andre, merket «Egen». En ny aksje hentes ved neste henting om kvelden og bruker da 1 kall om dagen, og fjerner du den før det, brukes ingen kall; valget lagres på denne maskinen. Signalet er målt på aksjer som omsettes for over 32 MNOK om dagen, og omsettes aksjen mindre, eller er omsetningen ikke målt, merkes den «Utenfor målingen». | 76 | Appen følger opptil 18 aksjer. «Følg» gir stjerne og merket «Egen», og aksjen hentes ved neste henting om kvelden og bruker da 1 kall om dagen. Signalet er målt på aksjer som omsettes for over 32 MNOK om dagen, og andre merkes «Utenfor målingen». | 44 |
| `ferdige_lister_kort` | – | – | De ferdige listene: velger du en bransje, ser du lista før noe byttes, og ved neste henting byttes lista di ut med de mest omsatte aksjene i bransjen. | 28 |
| `foelg_en_aksje` | Lista har alle aksjene på Oslo Børs som har en bransje og ikke er i lista di, og bransjen er fast for hver aksje, fra kontrollsjekken 10.11, så du velger den ikke selv. «Mest omsatt først» ordner etter median omsetning de 3 siste månedene og er ingen rangering etter kursen eller signalet. En aksje som ikke er målt, står med «ikke målt ennå», og en som omsettes for under 32 MNOK om dagen, eller ikke er målt, merkes «Utenfor målingen» når du velger den. | 85 | Lista har aksjene på Oslo Børs med en bransje som appen ikke følger, og tallet på en bransje er hvor mange som kan følges. «Mest omsatt først» ordner etter median omsetning de 3 siste månedene, ikke etter signalet. Under 32 MNOK om dagen, eller ikke målt, merkes «Utenfor målingen». | 49 |
| `foerste_knapp` | – | – | Den første knappen heter etter dagen kursene er fra. | 9 |
| `foerste_knapp_demo` | – | – | I demoen er det fredag 09.10, den siste dagen med oppdiktede kurser. | 13 |
| `historikken` | Signalet dag for dag: det appen skrev om aksjen hver børsdag, lest fra basen og aldri regnet på nytt. Uka og måneden teller dagene med signalstyrke 2 eller mer, og 3 av 3 har ring. Klikk på en dag med kurs for å se hele siden for den dagen. | 49 | Signalet dag for dag: det appen skrev om aksjen hver børsdag, aldri regnet på nytt. Uka og måneden teller dagene med signalstyrke 2 eller mer, og 3 av 3 har ring. Klikk på en dag med kurs for å se hele siden for den dagen. | 45 |
| `hovedindeksnavnet` | – | – | OSEBX er hovedindeksen på Oslo Børs. I demoen heter den oppdiktede indeksen DEMIX. | 13 |
| `kallene_lista` | – | – | Kallene: hver aksje bruker 1 av de 20 kallene i døgnet hos EODHD, og hovedindeksen 1. Det som er igjen, er margin til et nytt forsøk hvis noe feiler. | 29 |
| `perioden_boersometeret` | Periodene: den første knappen viser siste børsdag, de andre endringen fra den første kursen i perioden til siste børsdag, i fargen og snittet, og datoen med «Vis dagen» en dag du velger. Ved en periode er rutene like store, fordi volumet mot vanlig gjelder én dag. Rammen er signalet siste børsdag. | 51 | Periodene: den første knappen viser siste børsdag, de andre endringen i perioden, i fargen og snittet, og «Vis dagen» en dag du velger. Ved en periode er rutene like store. Rammen er signalet siste børsdag. | 35 |
| `perioden_oversikten` | Periodene: knappene viser siste børsdag, endringen fra den første kursen i perioden til siste børsdag, eller en dag du velger, med signalet som er lagret for den. Ved en periode gjelder sluttkursen og signalet siste børsdag, og «fra» med en dato står under endringen når kursserien begynner senere. Søylene og den stiplede linja følger samme periode eller dag, og oransje strek viser 3 av 3 siste børsdag. | 67 | Periodene: den første knappen viser siste børsdag, og de andre endringen fra den første kursen i perioden til siste børsdag. «Vis dagen» viser en dag du velger, med signalet som er lagret for den. Søylene følger samme periode eller dag. | 40 |
| `ringen` | – | – | Uten ring: 0 eller 1 av 3. | 7 |
| `sammenlign_med` | Sammenlign siste børsdag med: knappene er de samme som i oversikten, og øverst i hver rad står alltid siste børsdag. Med en periode eller en dag du velger, står en linje under hver rad med sluttkursen den første dagen i perioden eller dagen du valgte, endringen derfra til siste børsdag og signalet som er lagret for dagen, som aldri regnes på nytt. Oransje strek og «3 av 3» gjelder siste børsdag. | 71 | Sammenlign siste børsdag med: øverst i hver rad står alltid siste børsdag. Med en periode eller en dag du velger, står en linje under hver rad: sluttkursen den dagen, endringen derfra til siste børsdag og signalet som er lagret for dagen. «3 av 3» gjelder siste børsdag. | 47 |
| `signalet_forklart` | Først skriver appen hvor lenge signalet har vært slik og hva hovedindeksen, bransjen og lista gjorde samme dag. Med KI på kommer en tekst fra en språkmodell, merket «Laget av KI», som bare fikk det appen har regnet ut, som sjekkene og antall dager, aldri kurser, prosenter eller volumer. Tallene med prikket strek er sjekket før teksten vises. | 58 | Først skriver appen hvor lenge signalet har vært slik, og hva hovedindeksen, bransjen og lista gjorde samme dag. Med KI på kommer en tekst fra en språkmodell, merket «Laget av KI», som bare fikk det appen har regnet ut, aldri kurser, prosenter eller volumer. Tall med prikket strek er sjekket. | 50 |
| `soeylene` | Søylene: endringen for hver aksje, fra størst fall til venstre til størst stigning til høyre, mørk fra 2 % opp eller ned, som i børsometeret, og lys under. Den stiplede linja er indeksen, grønn når den steg, rød når den falt og grå ved 0,00 %. Et gult bransjesymbol betyr 3 av 3 siste børsdag, et klikk på symbolet viser aksjen, og «Se dagen» eller «Se perioden» under søylene åpner børsometeret med samme dag eller periode. | 75 | Søylene: endringen for hver aksje, fra størst fall til størst stigning, mørk fra 2 % opp eller ned. Den stiplede linja er indeksen: grønn når den steg, rød når den falt, grå ved 0,00 %. Et gult bransjesymbol er 3 av 3 siste børsdag. | 43 |
| `ukjent` | – Ukjent: det finnes ingen vurdering for dagen, og grunnen står under signalstyrken. Det er ikke en femte retning: «Ingen» betyr at sjekkene ble regnet uten at noen slo ut. | 29 | – Ukjent: det finnes ingen vurdering for dagen, eller aksjen har ingen kurser ennå eller venter på hentingen, og grunnen står under signalstyrken. Det er ikke en femte retning: «Ingen» betyr at sjekkene ble regnet uten at noen slo ut. | 39 |
| `utbyttejustert` | Kurs justert for utbytte: kilden regner kursen om bakover ved hvert nytt utbytte, så et ordinært utbytte ikke ser ut som et kursfall. Endringen, de 3 sjekkene og kursgrafen bruker den. | 31 | Kurs justert for utbytte: EODHD regner kursen om bakover ved hvert nytt utbytte, så et ordinært utbytte ikke ser ut som et kursfall. Endringen, de 3 sjekkene og kursgrafen bruker den. | 31 |
| `uten_data` | Uten data: en aksje uten en eneste kurs står nederst i tabellen uten sortering, med «–» i hver kolonne og «uten data» og med lenke til aksjesiden. | 26 | Uten data: appen har ingen kurser for aksjen ennå, fordi den nettopp er lagt til og venter på hentingen om kvelden, eller fordi EODHD ikke har kurser for den. Raden står nederst i tabellen, med «–». En aksje som venter, står under med «venter på henting». | 45 |
| `uten_data_demo` | – | – | I demoen er Matfjord Merkevarer med vilje uten kurser, så du ser hvordan det ser ut. | 16 |
| `uten_ramme` | – | – | Uten ramme: 0 eller 1 av 3. | 7 |

### Gjennomgangen av tilleggene 5–20 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen `0e7fd7c5..d1fe78c5`, og Edge Case Hunter og Verification Gap med repoet. Blind Hunter hadde 15 funn, Edge Case Hunter 9 og Verification Gap 12. Ingen agent kjørte pytest, som var stengt kl. 22:15–23:50. Da pytest åpnet kl. 23:50, viste testene at tekstene også må ha høyst tre setninger (8.0c), at «Kom i gang» i README-en har fem avsnitt (3.5i) og at linjene under «Ekstra» har høyst 20 ord, og at utdraget 08.11 §3 og designforslaget krever noen ord ordrett. Tekstene er skrevet om etter det, og setningen om omvisningen står i avsnittet «Første gang» i README-en.

*Høy*
- *VG1 og VG2, rettet.* Eldre tester sto med gamle tekster og gammel markup («kilden», «Appen følger N av 18</p>», «lest fra basen», `<h3>Følg flere aksjer</h3>`, omvisningen med alle stegene, og søket i «Følg en aksje» med `form.submit()`). De er rettet til det som er bygget, med en kommentar ved hver.
- *VG3, rettet og spørsmål 22.* Tre vinduer gikk over 60 ord på aksjesiden og børsometeret. Teksten om ringen og den første knappen er kortet, og vinduet for kursgrafen er uten setningen om den første knappen. Funnet følger av et svar og står åpent (regel 25). *Lukket 12.11 med svaret kl. 10:16:* godtatt som bygget.

*Middels*
- *Rettet:* BH8 (steget om KI-teksten sier «Med KI på»), BH9 (ringen, se VG3), ECH1 (skriptet sorterer med samme nøkkel som `ferdige_lister._norsk`, så «Aasen» står under A), ECH2 (M i overskriften er radene den valgte dagen), ECH3 (med «Vis hjelp» av står teksten om kallene i siden), VG4 (en test av 50 ord og de interne ordene), VG5 (tester av at tallet står fast og at en valgt tom bransje kan velges bort), VG12 (testen ser på alle kortene, og overskriften i Min liste med «Vis dagen» er testet).
- *Ført:* BH3 og ECH4 (aksjesiden uten kurser viser tidspunktet for de andre aksjene, som tillegg 17 ber om; spørsmål 14), BH11 og ECH9 (kortene er lista i dag, med aksjene som fjernes merket, mens tallet og rutene er etter neste henting; spørsmål 19), VG6 og VG7 (delene av skriptet som trenger en side, er sjekket i kildeteksten og i Edge, som spørsmål 9), VG8 (`min` mot `max` fanges ikke i demoen, der alle har samme tidspunkt; «Er du sikker?» er lagt til).
- *Ikke en feil:* BH1 (med «Vis dagen» er tabellen én liste, så delene brukes ikke), BH2 (`ingen_skilte_seg_ut` regner også med styrken), BH5 og BH6 (`#foelgbare` har bare radene, og «Ingen aksjer passer» styres av treffene), BH14 (en aksje som venter, har også «Egen»).

*Lav*
- *Rettet:* BH13 (hjelpen sier «Vis KI-tekst»), ECH5 (en feil i oppslaget gir ingen linje, ikke 500), ECH6 (kolonnen merkes over alle tbody-ene), ECH7 (boksen prøver øverst og beholder det bare hvis det hjelper).
- *Ført:* BH4 og ECH5 (oversikten leses to ganger på sidene med eget tidspunkt), BH7, BH10 og ECH8 (ordene om rammen følger `STANDARD`, som appen bruker), BH12, BH15, VG9, VG10, VG11.

### Mutantene for tilleggene 5–20 og hele settet (12.11 kl. 00:06–00:46)

Én mutant per tillegg, med en kopi av fila før og sha256 mot HEAD etter (`mutanter-t5-20.py` i scratchpad). Alle 14 ble fanget, og hver fil var lik HEAD etterpå: M13 (tillegg 17, den grå brikken kunne velges), M14 (overskriften sa siste børsdag med «Vis dagen»), M15 (uten «Oppdatert» på sidene uten eget tidspunkt), M16 (bryteren på aksjesiden i 14 px), M17 (steget om signalstyrken pekte på hele tabellen), M18 (en tekst med «kontrollsjekken»), M19 (eksempelboksen tilbake), M20 (omvisningen med stegene som gjentas), M21 (uten steget «Signalet forklart»), M22 (uten setningen om den første knappen), M23 (uten prøven uten ramme), M24 (ankeret `#ferdige-lister` borte), M25 (kortene i alfabetisk rekkefølge), M26 (uten setningen når lista ikke er full).

Hele settet i seks deler etter tilleggene: 5524 bestått og 24 hoppet over, til sammen 5548, likt `--collect-only`. Den første runden viste tester som sjekket det som sto før (bildet av investorsiden står 38 px lenger ned med «Oppdatert …», brikkene i steg 3 og kortene, «lenke til aksjesiden», «uten ramme» i `docs/hjelp.md` og «Signalet forklart» uten sjekker); de er rettet. Bildene i `docs/appen/` er tatt på nytt med høydene i `test_docker.py`.

### 13) Tilbudet første gang og veien videre (tillegg 21, svaret 12.11 kl. 09:58)

- **Tilbudet:** `tilby()` i `hjelp.js` sier `OMVISNING.TILBUDET`, «Første gang her? «Vis meg rundt» viser deg denne siden, ett steg om gangen.», med «Vis meg rundt» og «Nei takk». Ja huskes som før og starter `visSiden` med stegene fra knappen «Vis meg rundt» på oversikten, ikke `start()`. Uten den knappen, som når oversikten ikke har aksjer å vise, kommer ikke tilbudet, fordi ja ikke ville gjort noe. «Spill av omvisningen» står øverst som før.
- **Det siste steget:** `OMVISNING.videre(side, bareSiden, harNavn)` gir linja og målet for «Ferdig», bare på oversikten og bare i «Vis meg rundt». Med et navn under «Skilte seg ut» (`#aksjene tr.del.ut`) står «Klikk så et navn under «Skilte seg ut» for å se hvorfor aksjen skilte seg ut.», og «Ferdig» lukker boksen og gir fokus til det første navnet. Uten, for eksempel med en sortering eller når ingen fikk 2 av 3, står «Klikk så et navn i tabellen for å se sjekkene for aksjen.», og «Ferdig» går til tabellen. Linja står over knappene og er ikke et eget steg, så `MAKS_STEG = 7` gjelder. Hele omvisningen har ikke linja.
- **README-en og hjelpen:** «Første gang tilbyr appen «Vis meg rundt» på oversikten. «Spill av omvisningen» øverst viser alle sidene, og «Vis meg rundt» viser siden du står på.» Linja under «Ekstra, ferdig» og avsnittet i `docs/hjelp.md` følger. Rettet-linjer under svaret 11.11 kl. 13:49 i spesifikasjonen for 8.25 og i `epics.md`.

**Ville feilet hvis:** tilbudet startet hele omvisningen eller fortsatt sa at omvisningen viser sidene, linja sto i hele omvisningen, på en annen side eller som et eget steg, «Ferdig» bare lukket boksen, eller linja og «Ferdig» pekte på «Skilte seg ut» når ingen aksje står der.

### 14) Hvorfor en aksje er uten kurser (tillegg 22, svaret 12.11 kl. 10:16, spørsmål 10)

- **`UTEN_KURSER_HVORFOR`:** «EODHD har ikke gitt kurser for aksjen. Gir EODHD ingen kurser ved neste henting heller, slutter appen å følge en aksje du har valgt selv.» Det er det `valg.uten_rader` gjør: en egen aksje som er forsøkt hentet uten en eneste kurs, tas ut kvelden etter, og ønsket merkes avvist. De 15 faste aksjene tas ikke ut, og setningen sier derfor «en aksje du har valgt selv». Grunnen «nettopp er lagt til og venter på hentingen» er tatt bort, fordi en aksje som venter, står med «venter på henting».
- **Hjelpeteksten `uten_data`** bak «?» ved «Oppdatert» begynner med «Ingen kurser ennå:», ordene fra raden, og har tre setninger (8.0c): hvorfor, hva neste henting gjør, og raden med aksjen som venter i én setning. Aksjesiden uten kurser bruker den samme setningen. Linja om Matfjord Merkevarer i demoen står som før.
- **`docs/hjelp.md`** følger (regel 19), med at ønsket står som avvist og at en aksje som nettopp er valgt, står med «venter på henting».

**Ville feilet hvis:** forklaringen fortsatt ga «nettopp er lagt til» som grunn, ikke sa hva neste henting gjør eller sa noe annet enn koden, hjelpeteksten begynte med andre ord enn raden eller hadde over tre setninger, eller linja om Matfjord Merkevarer var endret.

### 15) README-en for faglærer (tillegg 23, svaret 12.11 kl. 16:23)

- **«Til faglærer»:** rett etter «Prøv appen» står to underpunkter, så de fire punktene fra svaret 29.10 kl. 19:36 står. Hovedflyten i demoen: aksjene som skilte seg ut, står øverst i tabellen under «Skilte seg ut»; klikk en av dem og les «Hvorfor signalet ble …» og «Signalet forklart»; «Vis meg rundt» viser siden du står på, og «Spill av omvisningen» alle sidene. Ordene er slått opp i `index.html`, `aksje.html` og `_rundtur.html`. Brukertesten, med lenke til `docs/brukertest.md`: målet om under 5 minutter i PRD-en, at det tok over 5 minutter 10.11 og at personen gikk seg vill på noen sider, og hva som er flettet etter det (rikere KI-tekster 11.11, «Spill av omvisningen» 11.11 og tilbudet om «Vis meg rundt»). «Vis meg rundt» fra 8.9 ble flettet 10.11 kl. 19:52, og brukertesten har ikke klokkeslettet, så linja nevner bare tilbudet.
- **Versjon 1 er ferdig:** ingressen og «Status» sier at versjon 1 er ferdig, og at «Ekstra» er det som er ferdig utover briefen. «Neste i v1» står med README-prøven til den er tatt. Ingressen sier at lista kan ha opptil 18 med «Følg en aksje» (`valg.TAK`). Linja i «Status» om endringer i lista følger tillegg 19: demoen sier at en endring ikke tas i bruk der, og viser ikke lenger et eksempel. Appen selv viser fortsatt «Appen er under utvikling og ikke ferdig.» nederst (`UNDER_ARBEID` i `app.py`); tillegget gjelder README-en, så den er ikke endret.
- **Tabellen «Demoen og den ekte versjonen»:** fire rader til, KI-tekst, dagen, endringer i lista og notatene, sjekket mot `demo.py`, `.env.example`, `start/start.ps1`, `start/start.sh`, `compose.yaml` og `docs/installasjon.md`.
- **`docs/innlevering.md`:** Lagt til-linja under «D. Dato for demonstrasjonen». Demomanuset står ikke i filene git sporer.

**Ville feilet hvis:** en av de to linjene manglet, sto et annet sted eller brukte andre ord enn malene; README-en sa at appen er under utvikling; ingressen ikke fulgte `valg.TAK`; «Status» fortsatt sa at demoen viser et eksempel på meldingen; en rad i tabellen manglet eller ikke stemte med koden.
