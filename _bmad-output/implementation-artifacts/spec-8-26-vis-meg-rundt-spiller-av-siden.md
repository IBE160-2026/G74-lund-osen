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
- *VG1, åpent, spørsmål 9.* Testene av boksen søker i kildeteksten; ingen test kjører siden i en nettleser. Forslaget er å la det stå, med prøvingen i Edge.

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
- *ECH2, BH3 og VG2, åpent, spørsmål 10.* Forklaringen fra tillegg 8 sier «venter på hentingen» om en aksje som står i lista uten kurser.

*Lav*
- *Rettet:* BH4 (setningen om demoen bare på siden for MTFJ), BH6, ECH3 og VG4 (ankeret i Innstillinger slås opp før noe skrives, og en test knytter ankrene til valgene), BH12 (kommentaren i stilen), BH16 (hjelpen), ECH6 (kommentarene i `boersometer.py`), ECH7 («Alle» og «Min liste» i Min liste holder plassen).
- *Ført:* BH5, ECH4 og VG5 (teksten i ruta er ikke regnet for nivå 2 og 3; prøvd i Edge, der MTFJ står på nivå 1), ECH5 (en dag før første kurs sier «Ingen kurser ennå»), BH8 og VG6 (regexen for lenkene og testen av ankeret i omvisningen), BH9 (samletesten sammenligner uten stor forbokstav), BH10 (hjelpetekstene importerer demodataene), BH13 (stor forbokstav regnes to steder; samletesten sammenligner dem), BH14 (`test_notater` sletter også versjon 13), BH15 (testen for pila i demolinja), VG7 (`scroll-margin-top` er ikke testet).
- *Ikke en feil:* BH7 (de to radene med periodevalget utelukker hverandre, som ECH fant), BH11 (en tom tittel står ikke).

### 10) «Din egen liste» som på tavla, og siden i demoen (tillegg 12, svaret kl. 20:28)

- **Kortene:** tittelen i Newsreader ved tallet i den svarte boblen, kort tekst og én handling nederst, og like høye kort (`display: flex` og `margin-top: auto`). Steg 1 har knappen «Åpne eodhd.com ↗»: i den ekte versjonen `https://eodhd.com/register` (`EODHD_REGISTRERING`, samme adresse som startskriptet) i en ny fane, og i demoen `/eodhd-demo`. Svaret kl. 14:29 på spørsmål 9 i 8.22 har Rettet-linje i spesifikasjonen for 8.22 og i `epics.md`, og kontrollpunktet i `test_hjelpetekster.py` godtar akkurat den lenken. Steg 2 har statusen som én linje med ✓, og «Slik bytter du nøkkel» bak «?». Steg 3 har teksten fra tavla, de ferdige listene som brikker med ikonet og antallet, og «+ Følg en aksje»; kallene, regnet av lista som spørsmål 10 i 8.22 sa, og bransjelistene står bak «?» (hjelpevinduet har fått `linjer` for tall siden har regnet ut).
- **Siden i demoen:** `/eodhd-demo` (`eodhd_demo.html`), bare i demoen, i oppsettet fra investorsidene: «Tilbake til Min liste», tegningen `src/static/demo/eodhd.svg` laget av KI i samme stil som de 15, boblen etter forslag 1 i spørsmål 11, «Illustrasjon laget av KI» og teksten nederst. I den ekte versjonen svarer ruta 404. Prøvd i Edge ved 1280 og 390 px; der står boblen under tegningen, som på investorsidene.
- **Testene fra 8.22** som så etter adressen som tekst, kallene i steg 3, `<h5>Slik bytter du nøkkel</h5>` og avsnittet «Start fra en ferdig liste», er rettet til det nye oppsettet.

**Ville feilet hvis:** et kort manglet tallet ved tittelen eller handlingen nederst, demoen lenket til eodhd.com, den ekte versjonen ikke åpnet registreringen i en ny fane med adressen fra startskriptet, kallene eller byttet av nøkkel sto i kortene, eller siden i demoen manglet en av delene eller sa noe om kurser.
