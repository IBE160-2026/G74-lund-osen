---
title: "Den heuristiske evalueringen"
status: aktiv
created: 2026-11-17
updated: 2026-11-17T16:22
---

# Den heuristiske evalueringen av demoen

Laget 17.11.2026, etter at appen ble bygget, før brukertest 2. Gruppen ba om den
i svaret 16.11 kl. 20:22, og rådet anbefalte den (instruksjonen i
[dagsfila](ai-prompts/2026-11-16.md)). Spesifikasjonen er
[`spec-9-17-heuristisk-evaluering.md`](../_bmad-output/implementation-artifacts/spec-9-17-heuristisk-evaluering.md).
Ingen kode er endret. Hvert funn har et forslag som gruppen svarer på, og de
nye funnene står også i [UX-loggen](ux-logg.md) som U114–U131.

## Metoden

- **Hva:** demoen på main (`ba866204`), med oppdiktede selskaper og tall. Den
  ekte versjonen er ikke startet, og basen er ikke lest.
- **Hvordan:** demoen ble startet fra en midlertidig mappe, med en ny demobase,
  på en ledig port som ikke er 8000, og stoppet etterpå. 33 skjermbilder ble tatt
  med Edge uten vindu, i 1280 og 390 px bredde, og HTML-en ble lest fra
  demoserveren. Malene eller koden ble slått opp for hvert funn som har en
  kilde der. HE4 bygger bare på bildene.
- **Sidene:** oversikten, aksjesiden, Min liste, Innstillinger, «Vis meg rundt»,
  hjelpen og visningen på 390 px.
- **Målestokken:** de ti heuristikkene til Jakob Nielsen, H1–H10 under.
  Heuristikkene og anbefalingen om flere evaluerere er fra Nielsen Norman
  Group. Kilden er ikke lest i økta, så den er ikke sitert (regel 11).
- **Hvem:** én evaluerer, KI-assistenten i økten. Metoden anbefaler tre til fem
  evaluerere, fordi hver finner bare en del av problemene. Én evaluerer er
  derfor en svakhet, og brukertest 2 er den andre kilden.
  *Svar 2026-11-17 kl. 13:03–13:13 (gruppens svar, rådet anbefalte det):* gruppen er evaluerer nr. 2. Den fant HE14–HE17 selv i den ekte
  versjonen 17.11, og kilden for dem er gruppen, ikke malene.
- **Sjekket mot UX-loggen:** et funn som alt står i [UX-loggen](ux-logg.md),
  får nummeret sitt der og er ikke ført som nytt.
- **Bildene** er av demoen og ligger ikke i repoet. Svaret ba ikke om dem, og
  `docs/bilder/` og `docs/appen/` er låst av testene.

| | Heuristikken |
|---|---|
| H1 | Synlig systemstatus |
| H2 | Samsvar mellom systemet og den virkelige verden |
| H3 | Brukerkontroll og frihet |
| H4 | Konsistens og standarder |
| H5 | Forebygging av feil |
| H6 | Gjenkjenning fremfor hukommelse |
| H7 | Fleksibilitet og effektivitet |
| H8 | Estetisk og minimalistisk design |
| H9 | Hjelp brukere å gjenkjenne, forstå og rette feil |
| H10 | Hjelp og dokumentasjon |

**Gradene.** *Høy:* hindrer en kjerneoppgave. *Middels:* gjør en vanlig oppgave
vanskeligere eller kan gi en feil som er vanskelig å rette. *Lav:* et hinder som
er lett å komme rundt, eller bare ser rotete ut. Ingen funn er høye. Gradene for
HE14–HE17 er satt etter den samme skalaen.

## Funnene

| # | Heuristikken | Siden | Grad | Det som ble sett | Kilden | Forslaget |
|---|---|---|---|---|---|---|
| HE1 | H4, H2 | Min liste og oversikten | middels | «Min liste» er aksjene med stjernen, som bare velger hva du ser. «Dine egne aksjer» og «Din egen liste: kom i gang» handler om hvilke aksjer appen henter, og koster kall. Navnene ligner, og begge står på samme side. | `_egne.html` (overskriftene) | Gi delen om egne aksjer et navn som ikke ligner «Min liste», og én linje om at stjernen velger hva du ser, mens Følg velger hva appen henter |
| HE2 | H3, H5 | Notatene på aksjesiden, i Min liste og i panelet | middels | «Slett» sletter et notat med en gang, uten å spørre og uten angre. Med et tenkt kjøp heter knappen «Slett notatet og det tenkte kjøpet», og kjøpet forsvinner også. Å slutte å følge en aksje kan angres, og spør først når aksjen har et åpent tenkt kjøp. | `_notat.html` (`slett-notat`), ruten `/aksje/<symbol>/notat/slett` i `app.py`, mot `bekreft_fjern.html` og `_egne.html` | Etter slettingen sier siden at notatet er slettet, med «Angre», som ved Følg. Det andre valget er å spørre først |
| HE3 | H6, H1 | Tabellen på 390 px, på oversikten og i Min liste | middels | Bare selskapet, sluttkursen og en del av endringen synes. Signalstyrken og retningen, som er kjernen, ligger utenfor skjermen, og ingenting viser at tabellen kan dras sidelengs. | `index.html` (`tabellboks`), `stil.css` (`overflow-x: auto`) | Vis styrken og retningen under selskapsnavnet på smal skjerm, eller en skygge i høyre kant og en linje om å dra sidelengs. Gruppen tok inn «tabellen på smal skjerm» 17.10 (UX-loggen), og det punktet ser ut til å stå åpent. «Bredden ved 390 px» ble avvist 19.10 fordi tabellboksen ruller sidelengs |
| HE4 | H8, H7 | Stripa på 390 px, alle sidene | lav | Knappene i stripa går over fire rader, og innholdet begynner omtrent midt på skjermen. | Bildene av Min liste og aksjesiden på 390 px | En «Meny»-knapp på smal skjerm, eller færre knapper (se HE6) |
| HE5 | H1, H6 | Innstillinger | lav | Når «Vis hjelp» er av, forsvinner også «Vis meg rundt» og omvisningen fra stripa, men teksten under bryteren sier bare «Faste forklaringer som vi har skrevet og sjekket …», og steget i omvisningen sier «Slår spørsmålstegnene ved overskriftene av og på.» | `_rundtur.html`, `innstillinger.html`, `hjelpetekster.py` | Én setning til under bryteren: av skjuler også «Vis meg rundt» og omvisningen |
| HE6 | H4, H8 | Stripa: «Vis meg rundt» og «Spill av omvisningen» | lav | To knapper side om side, og forskjellen synes først etter et trykk: den ene går gjennom siden, den andre gjennom hele appen. | `_rundtur.html` | Et navn som sier forskjellen, for eksempel «Hele omvisningen», eller bare lenken på siste steg |
| HE7 | H1 | «Vis meg rundt» | lav | Steget «Dagen og perioden» sier «Knappene og datoen velger …», men merker bare datofeltet. På aksjesiden merker to steg det samme stedet, og på 390 px merkes bare overskriften over sjekkene. | `hjelpetekster.py` (stegene), `_perioder.html` (`velg-dag`) | Merk hele periodevalget i steget, og la det andre steget merke det første sjekkortet |
| HE8 | H2 | Aksjesiden, sjekk 1 | lav | Målingen står som «… mot MA50», en fagforkortelse, mens resten av siden sier 50-dagers snitt. | `signalberegning.py` («mot MA{…}») | «mot 50-dagers snitt» |
| HE9 | H2, H8 | Oversikten, raden «Øvrige aksjer» | lav | Tallet ved «Øvrige aksjer» teller tre grupper sammen, og teksten etter har tre ledd bundet med «og». Ordlyden «og N uten signal» er gruppens valg fra 14.10 (svar 7 i 8.0d), og «uten kurser» kom i 8.2a. | `index.html` (`del oevrige`) | Ett tall per gruppe, skilt med punkt |
| HE10 | H4 | Min liste, «Din egen liste: kom i gang», steg 2 | lav | Steget heter «Lim inn nøkkelen din», men siden har ikke noe felt for nøkkelen. Teksten i steget sier at startskriptet spør etter den, så det er tittelen som villeder. | `_egne.html` | Et navn som sier hvor nøkkelen limes inn |
| HE11 | H10 | Hjelpevinduene | lav | Svarene som ikke får plass i et hjelpevindu, står i `docs/hjelp.md`, men ingen side eller hjelpevindu lenker dit. Bare kommentarer i malen og i `hjelpetekster.py` nevner fila. | `aksje.html` og `hjelpetekster.py` (kommentarene) | En lenke til hjelpen nederst i hjelpevinduet |
| HE12 | H6 | Aksjesiden, periodevalget | lav | Aksjesiden åpner på en periode, så datofeltet er tomt og uten piler fra start. Oversikten åpner på siste børsdag, med dagen og pilene. Med en periode valgt er feltet tomt på alle sidene, valgt med vilje i 8.20a, og et lignende punkt ble avvist 18.10 i 8.16. | `_perioder.html`, `perioder.py` | Vis dagen siden viser i feltet, eller en kort tekst foran feltet |
| HE13 | H8 | Aksjesiden, «Signalet dag for dag» | lav | Ukene etter siste demodag står som tomme rader, med linja «… så dagene utenfor står tomme.» | `aksje.html` (`kursserien`) | Skjul uker der alle dagene er etter siste kursdag |
| HE14 | H3, H7 | Aksjesiden, «Signalet dag for dag» | middels | Pilene går én måned om gangen, og ingenting tar deg tilbake til måneden for dagen siden viser. Oppgaven om «i ettertid» i brukertest 2 sender testpersonen måneder bakover der. | Funnet av gruppen 17.11 kl. 12:48, i den ekte versjonen | En lenke tilbake ved pilene, som bare vises når du har bladd bort. Før testen |
| HE15 | H2, H7 | «Dine egne aksjer» og Min liste | middels | Gruppen så en aksje den følger, uten stjerne, så den sto ikke i tabellen i Min liste. *Rettet 17.11 (svaret kl. 14:16, spørsmål 4):* Følg setter stjernen fra 11.11 (8.26), og notatene synes under «Mine notater» uten stjerne. En aksje uten stjerne kan være fulgt før 11.11, eller tatt inn med en ferdig liste. | Funnet av gruppen 17.11 kl. 13:03, i den ekte versjonen, og sjekket mot main: `folg` i `valg.py` og `_alle_notatene` i `app.py` | Ingen kodeendring før testen. Spørsmål 1 i spesifikasjonen for 9.18 |
| HE16 | H4, H5 | Omvisningen | lav | Boksen bytter hjørne (8.26), og bredden følger teksten. Da flytter «Neste» seg, og man trykker «Tilbake». | Funnet av gruppen 17.11 kl. 13:11, i den ekte versjonen | Fast bredde på boksen før testen. Plasseringen tas etter testen |
| HE17 | H10 | Omvisningen | lav | Notatene er ikke forklart i omvisningen. | Funnet av gruppen 17.11 kl. 13:11, i den ekte versjonen | Ett steg ved notatfeltet på aksjesiden og ett ved notatene i Min liste. Før testen |
| HE18 | H1, H3 | Omvisningen | lav | Omvisningen blar alltid så det merkede havner øverst, også når det synes fra før. Ved linja «Oppdatert …» hopper siden et hakk ned, og stripa forsvinner. | Funnet av gruppen 17.11 kl. 13:32, i den ekte versjonen | Bla bare når det merkede ikke synes. Før testen |

*Lagt til 2026-11-17 (story 9.18, gruppens svar kl. 13:03–13:33):* rettet før brukertest 2, hver med en test som feilet mot koden før rettingen:

- HE2: «Slett» ved et notat spør først, nevner aksjen, datoen og notatet, og sier om et tenkt kjøp slettes også. «Avbryt» lar alt stå.
- HE3: på smal skjerm står styrken og retningen under selskapsnavnet, for eksempel «2 av 3 · ↑ Positiv».
- HE5: teksten ved «Vis hjelp» og steget i omvisningen sier at av også skjuler «Vis meg rundt» og «Spill av omvisningen».
- HE8: målingen sier «mot 50-dagers snitt». Den er ikke lagret i basen eller i KI-grunnlaget, så bare visningen er endret.
- HE9: «Øvrige aksjer» har ett tall per gruppe, skilt med «·».
- HE10: steg 2 heter «Lim inn nøkkelen i startskriptet».
- HE14: ved månedspilene står en lenke tilbake til måneden for dagen siden viser, for eksempel «Til oktober 2026», bare når en annen måned er valgt.
- HE15: ingen kodeendring. Følg setter alt stjernen (8.26, 11.11). Beskrivelsen er rettet: notatene synes under «Mine notater» uten stjerne (svaret på spørsmål 4, beskjeden kl. 14:16). Se spørsmålet i spesifikasjonen for 9.18.
  *Svar 2026-11-17 kl. 16:19 (gruppens svar, rådet anbefalte det):* HE15 lukkes som alt bygget. Følg har satt stjernen siden 8.26 (11.11), og en test låser det. De tre egne aksjene ble fulgt før det, og gruppen setter stjernen på dem selv i den ekte versjonen.
- HE16: boksen i omvisningen har fast bredde. At den bytter hjørne, er ikke endret.
- HE17: et steg om notatene sist på aksjesiden og et i Min liste, rett før «Mine notater», med ordene fra Innstillinger.
- HE18: omvisningen blar bare når det merkede ikke synes.

HE1 er et spørsmål i brukertest 2, og HE4, HE6, HE7, HE11, HE12 og HE13 venter til etter testen.

**Ført fra før og fortsatt synlig, ikke nye funn:**

- En ukjent adresse, også en ukjent aksje, gir Flasks engelske «Not Found» uten
  rammen og uten vei tilbake (H9). Står i UX-loggen fra 2026-10-13 som åpent,
  ble utsatt 14.10 og avvist 19.10.
- To nevnere på oversikten, aksjene som skilte seg ut og aksjene som gikk
  bedre enn indeksen (U23). Den er delvis løst i 8.2a, og linja om indeksen har
  fortsatt sin egen nevner.

## Det som virker

- **H1:** når dataene ble hentet, og demolinja, står på hver side. Omvisningen
  viser hvilket steg du er på. Notatpanelet i demoen sier at notatene forsvinner
  når demoen startes på nytt, og en tidligere dag sier at den ikke er siste
  børsdag og lenker tilbake.
- **H2:** sjekkene heter Trend, Bevegelse og Interesse, tallene er norske, og
  overskriften sier dagen i én setning. Sidene sier at signalet ikke er et råd
  der det trengs.
- **H3:** omvisningen har Tilbake, Lukk og Esc, hjelpen lukkes på samme måter,
  og tilbudet første gang har «Nei takk». Å slutte å følge en aksje kan angres,
  og spør først når aksjen har et åpent tenkt kjøp. «Vis notater» av skjuler
  notatene uten å slette dem.
- **H4:** samme periodevalg, samme tabell og samme brytere på sidene som har
  dem.
- **H5:** datofeltet har første og siste dag, notatfeltet sier hvor mange tegn
  det tar, og en ferdig liste spør først.
- **H6:** kortet om hvordan tabellen leses, forklarer tegnene, og hver rad har
  sjekkene med verdien. Sjekkortene viser hvor grensene ligger.
- **H7:** Alle og Min liste, sortering med et klikk, en dag fram og tilbake med
  pilene, og KI-teksten kan slås av både ved teksten og i Innstillinger.
- **H8:** på bred skjerm er overskriften sammendraget, og ved en aksje betyr
  gult 3 av 3.
- **H9:** en rad uten signal sier hvorfor, for eksempel for kort historikk,
  ikke børsdag eller ingen kurser ennå.
- **H10:** spørsmålstegn ved hver overskrift, hjelpefeltet ved siden av siden på
  bred skjerm, en omvisning for siden og en for hele appen, og et tilbud første
  gang.

## Spørsmål til gruppen

Hvert funn over er et forslag. Ingenting er endret, og ingenting endres før
gruppen har svart.

1. **HE1–HE3 (middels).** Skal de rettes før brukertest 2? *Forslag:* HE2 og
   HE3 før testen, fordi HE2 kan slette et notat ved et feiltrykk, og HE3
   skjuler signalet på en telefon. HE1 tas som et spørsmål i brukertest 2
   først, fordi brukertest 1 fant flest merknader på Min liste (U105).
   *Svar 2026-11-17 kl. 13:03–13:13 (gruppens svar, rådet anbefalte det):* HE2 og HE3 rettes før brukertest 2. HE1 blir først et
   spørsmål i brukertest 2.
2. **HE4–HE13 (lave).** *Forslag:* HE5, HE8, HE9 og HE10 er tekst og kan tas i én
   liten story. HE4, HE6, HE7, HE11, HE12 og HE13 venter til etter brukertest 2.
   *Svar 2026-11-17 kl. 13:03–13:13 (gruppens svar, rådet anbefalte det):* HE5, HE8, HE9 og HE10 tas i samme story som HE2 og HE3, før
   testen. HE4, HE6, HE7, HE11, HE12 og HE13 venter til etter testen.
3. **Én evaluerer.** *Forslag:* gruppen går selv gjennom tabellen før
   brukertest 2 og fører funn den er uenig i, som en datert linje under
   tabellen.
   *Svar 2026-11-17 kl. 13:03–13:13 (gruppens svar, rådet anbefalte det):* gruppen er evaluerer nr. 2 og fant HE14–HE17 selv. De står i
   tabellen. Før testen rettes HE14, HE15, fast bredde i HE16 og HE17, og
   plasseringen i HE16 tas etter testen. Rettingene kommer i en egen story
   etter at 9.17 er flettet.
4. **HE15 og koden.** Gruppen så at notatene på en aksje uten stjerne ikke
   synes i Min liste, men på main viser «Mine notater» i Min liste alle
   notatene. *Forslag:* storyen med rettingene ser på det i den ekte
   versjonen først, for eksempel om en valgt dag eller «Vis notater» spilte
   inn. At Følg setter stjernen, gjelder uansett.
   *Svar 2026-11-17 kl. 14:16 (gruppens svar, rådet anbefalte det):* «Mine
   notater» i Min liste viser alle notatene, også uten stjerne. Følg setter
   også stjernen, og beskrivelsen av HE15 er rettet. Slått opp i 9.18: Følg
   setter alt stjernen fra 11.11 (8.26), så det er ingen kodeendring.

## En idé fra gruppen

*Idé 2026-11-17 kl. 13:08 (gruppen), ikke et funn:* et tenkt salg uten et
tenkt kjøp først, for aksjer man har fra før. Appen sier aldri om et kjøp
eller salg er godt (NFR-06), bare hva aksjen og indeksen gjorde etterpå. Den
tas etter brukertest 2, og hører sammen med U112 fra brukertest 1.
