---
title: "Designregler"
status: aktiv
created: 2026-10-01
updated: 2026-10-15T15:27
---

# Designregler

Regler for hvordan alle skjermbildene ser ut. Kravene står i `prd.md` og `epics.md`, og her står hvordan de vises. En regel endres bare her, med dato og grunn, og ingen linje fjernes uten «Her sto» eller «Rettet» (regel 13).

## 1. Skrift

*Avgjort 2026-10-01, Marians beslutning, etter tre forslag i designtavla (i Claude, ikke i repoet).*

- IBM Plex Sans til all tekst og alle tall. Tall settes med tabelltall (`font-variant-numeric: tabular-nums`), så sifrene står rett under hverandre i kolonnene.
- Newsreader bare til overskrifter og titler, også når det står et tall i dem, som «4 av 15 aksjer skilte seg ut».
- Skriftfilene ligger i appen sammen med lisensen (SIL Open Font License 1.1), og siden henter ingen skrift fra nettet. Appen kjører lokalt (`prd.md` §2).
- Hele skriftfiler, ikke IBMs oppdelte webfiler i mappa `split`. I IBM/plex issue 162 på GitHub mangler stilvariantene `ss01` og `ss02` i Latin1-delen av de oppdelte filene. Tabelltall er også en OpenType-funksjon (`tnum`), så en test sjekker at filene vi bruker, har den.

**Hvorfor:** Tallene er det appen viser mest, og de skal kunne sammenlignes rad for rad. Newsreader er laget for lesing på skjerm (Production Type på GitHub) og gir overskriftene et rolig avispreg, som passer en app som forklarer og ikke gir råd (NFR-06). De to andre forslagene var Source Serif 4 med Source Sans 3, som gjør samme jobb, og Schibsted Grotesk, der beskrivelsen på GitHub ikke sier noe om tabelltall.

**I dag:** malene bruker systemets skrift, og noen tallceller har allerede tabelltall. Regelen tas inn i story 8.2.

**Testene når den tas inn:** ingen mal viser til en skrift på nettet, tallcellene i tabellene har tabelltall, og skriftfilene har OpenType-funksjonen `tnum`.

*Lagt til 2026-10-14 (story 8.0d, PR 1):* IBM Plex Sans har ikke `tnum`, men sifrene er like brede som standard, så tallene står rett under hverandre uten den. Testen krever like brede sifre i hver fil, og `tnum` i Newsreader, som har den. Se målingen i §5.

## 2. Periodevalg

*Avgjort 2026-10-01, Marians beslutning, etter designtavla.*

- Der man velger periode, er valget likt: samme knapper, samme rekkefølge, samme navn og samme utseende. Rekkefølgen er siste børsdag, 1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år og «Velg dag».
- Den første knappen heter «I går» når siste børsdag i dataene var i går, og «I dag» når den er fra i dag. Ellers står ukedagen, for eksempel «Fredag» på en mandag. Knappen er valgt når siden åpnes. Unntaket er kursgrafen, som åpner med 6 mnd (FR-201).
- «Velg dag» åpner en kalender, og dagen som er valgt, står på knappen. Signalet den dagen vises bare når vurderingen er lagret, ellers «– ikke lagret» (NFR-08).
  *Rettet 2026-10-03 (story 2.2b, Marians beslutning kl. 22:30):* en dag uten rad viser «– ikke vurdert», samme tekst som oversikten og aksjedetaljen. Har raden en grunn, står grunnen i stedet.
  *Presisert 2026-10-04 (gjennomgangen av 2.2b):* «ikke vurdert» gjelder en børsdag uten rad. En dag som ikke er børsdag, viser «– ikke børsdag», så de to tilstandene i FR-409 ikke slås sammen.
- Startdagen for periodene følger én skriftlig regel, lik for alle, som skrives og testes før et periodevalg bygges (NFR-08).

**Hvorfor:** Samme knapp betyr det samme overalt, så brukeren lærer valget én gang. Den første knappen sier hvilken dag tallene gjelder, med ord brukeren kjenner.

**I dag:** appen har ikke noe periodevalg. Kursgrafen har faste seks måneder (FR-201), og flere perioder står under «Hvis vi rekker».

## 3. Gult betyr 3 av 3

*Avgjort 2026-10-01, Marians beslutning.*

- Ved en aksje betyr gult at den fikk 3 av 3 på siste børsdag: gul ring rundt pillen «3 av 3» i tabellen, gul ramme med hvit kant og merket «3 av 3» i børsometeret, og gult bransjesymbol over søylen under hovedindeksen (FR-105).
- Gult står også når siden viser en periode eller en annen dag, så aksjen er lett å kjenne igjen. 2 av 3 merkes uten gult, og bare for siste børsdag.

**Hvorfor:** 3 av 3 er det sterkeste signalet, og samme farge overalt gjør det lett å finne.

**I dag:** appen bruker ikke gult. Rader som skiller seg ut, har lys grå bakgrunn og merket «skiller seg ut» (index.html).

*Lagt til 2026-10-13 (story 8.0c, PR #35):* oversikten har gul ring rundt «3 av 3» i fargen `#a67c00`, for kontrast på minst 3:1 mot hvitt. 2 av 3 merkes med fet skrift og en strek til venstre i tekstfargen, uten gult.

*Lagt til 2026-10-13:* linja «I dag» over gjelder før 8.0c. Den lyse grå bakgrunnen er byttet ut med fet skrift og strek, og merket «skiller seg ut» står fortsatt (index.html).

*Lagt til 2026-10-05:* tabelldelen av regelen, gul ring rundt «3 av 3» og 2 av 3 merket uten gult, tas inn i story 8.0c.

*Lagt til 2026-10-13 (story 8.0e, svar 8 kl. 21:27):* pillen «3 av 3» i oversikten har svart fyll og hvit tekst inne i den gule ringen, som i designforslaget, med kontrast på minst 4,5:1. 2 av 3 merkes som før, med fet skrift og strek, uten fyll og uten gult.

*Lagt til 2026-10-14 (gruppen 14.10 kl. 17:17 og skissen gruppen valgte like etter, instruksjonen kl. 17:31):* fargene er som i originalen, med oransje som grunnfarge. 3 av 3 har strek på 4 px til venstre i raden og ring rundt pillen i sterk oransje `#F2B53A`. 2 av 3 har strek på 4 px i lys oransje `#F8DE9C`, og fet «2 av 3» som før. 1 av 3 og 0 av 3 har ingen strek og ingen farge. **Hvorfor:** gruppen vil ha utseendet fra originalen. Teksten sier alltid det samme (FR-103), og pillen har svart fyll siden 8.0e, så ringen og strekene trenger ikke 3:1 mot hvitt.

## 4. Ordliste – samme ord på alle sidene (01.10)

*Ført 2026-10-13 ordrett fra designtavla i Claude, versjon 1791623938-3408, med «-» for «•». Ordlista er ikke kontrollert mot koden og PRD-en etter 02.10. Det gjør den samlede endringen (samlelista punkt 8 og 10) før noe herfra brukes i appen.*

*Lagt til 2026-10-13:* kontrollert i endringsforslaget 13.10, punkt 4.3, og rettet under punktene. Punkt 21 venter til etter prøven i kveld (svar 6 og N1).

- Signalstyrke 0–3: hvor mange av de 3 sjekkene som slo ut.
- Sjekkene: trend (T), bevegelse (B) og interesse (I). Hver gir +1, 0 eller -1, skrevet «T +1» overalt, som kolonnen «Ga» i appen.
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* sjekkene skrives «T +1» i oversikten. På aksjesiden står navnet på sjekken og ordet, som i 8.0c (svar 8).
  *Rettet 2026-10-15 (gruppens svar kl. 12:15, svar 28 i 8.0d):* symbolet ved Signalstyrke i kortet «Slik leser du tabellen» er en grønn «+1» over en rød «-1», uten bokstav. Se tillegget 15.10 nederst i §5.
- Retning: Positiv, Negativ, Blandet eller Ingen, med pil (FR-103). Pilene brukes ikke til noe annet.
- Skilte seg ut: signalstyrke 2 eller mer. Signalstyrken skrives «3 av 3», og 3 av 3 er fylt med gul ring.
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* 3 av 3 merkes med gul ring rundt, som i §3.
  *Lagt til 2026-10-14 (gruppen 14.10 kl. 17:17 og skissen gruppen valgte like etter, instruksjonen kl. 17:31):* ringen og streken ved 3 av 3 er sterk oransje `#F2B53A`, og streken ved 2 av 3 lys oransje `#F8DE9C` (§3).
- Tall med sifre, også små: «3 av 3 sjekker», ikke «alle tre».
- Endring: fra forrige børsdag, utbyttejustert, med fortegn. Kolonnehodet sier «i går», som den første knappen i periodevalget.
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* endringen gjelder siste børsdag. Kolonnehodet følger den første knappen i periodevalget, som heter «I går», «I dag» eller ukedagen (§2).
- Retning forklares med tall: «1 sjekk ga +1, 2 ga -1», ikke «peker hver sin vei». På aksjesiden står sjekkene med navn: «Trend ga +1. Bevegelse og interesse ga -1.»
- Beløp skrives i NOK, ikke «kroner» eller «kr» (Marian 01.10). Øverst på hver side, i den svarte stripa, står når dataene ble oppdatert og når neste oppdatering tidligst kan komme, med klokke.
- Egen aksje: blått merke «Egen» og blå strek. Den står i tabellen sammen med de andre og sorteres likt. Under tabellen står bare valget: hentet eller venter, og Fjern. Stjerne betyr Min liste. Gul ring, gul ramme og gult symbol betyr 3 av 3 i går, også når en periode er valgt. I børsometeret har ruta gul ramme med hvit kant og merket «3 av 3».
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* egne aksjer står i en egen del, «Dine egne aksjer» (svar 11). Gul ring, gul ramme og gult symbol betyr 3 av 3 på siste børsdag (§3).
- Utenfor målingen: en egen aksje som omsettes for under 32 MNOK om dagen. Grensene i signalet er målt på aksjer som omsettes for over 32 MNOK, og så mye handel gjør dem lette å kjøpe og selge (begrunnelser.md §2). Teksten sier ikke «de 15» (Marian 02.10 kl. 21.56). Ikke «krav» og ikke «omsatt for lite». Grått merke, fordi gult betyr 3 av 3.
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* «en egen aksje» blir «en aksje», fordi hele lista kan byttes (08.10). Resten står.
- Børsen, bransjen eller selskapet: hvor dagens bevegelse ser ut til å komme fra, ikke hvorfor. Børsen er hovedindeksen, og tallet står med «for hovedindeksen». Regnes alltid av lista som er aktiv, også egne aksjer som er hentet. Svarene er «Børsen», «Bransjen», «Selskapet», «Selskapet eller bransjen» og «Liten bevegelse».
- Bransjer: 13, hver med navn og symbol (tavla «Bransjer»). De 11 hos Euronext (ICB), med sjømat og shipping for seg, som Euronexts indekser OBSFX og OBSHX. Nye: Forbruk, Teknologi, Helse, Eiendom og Kraft.
- Sortering: vinkler i den svarte kolonneraden. Pilene er bare for retning.
- Stiplet linje betyr bare hovedindeksen. 50-dagers snittet og grensen for interesse er heltrukne, og kursen er tykkere enn snittet.
- Datoer: 22.09, uten punktum til slutt, og med år bare når året er et annet: 29.09.2025.
- Knapper i en dialog: hovedvalget til høyre, det andre valget eller Avbryt til venstre for det. Samme handling har samme ord overalt, for eksempel «Følg aksjen».
- Merker ved et navn («Egen», «Utenfor målingen») har samme størrelse.
- Uten farger: retning, endring og sjekkene står alltid også som tekst, fortegn eller pil, og linjer og søyler kan leses av plassen over eller under null-linja.
- Periodevalg, likt overalt: «I går», 1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år og «Velg dag». Var siste børsdag ikke i går, står ukedagen, for eksempel «Fredag» på en mandag. Grafen åpner med 6 mnd (FR-201).
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* den første knappen heter «I går», «I dag» eller ukedagen, som i §2.
- Sammenligning: hver rad får en linje til for dagen du sammenligner med: sluttkursen, endringen siden da, og T, B og I den dagen, med T rett under T. Retningen står bare for i går. Kolonnehodet sier «i går», og datoen står i gult under.
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* retningen står bare for siste børsdag. Kolonnehodet følger den første knappen i periodevalget (§2), og datoen står under, uten gult (§3).
- U ved kursen: aksjen har betalt utbytte i perioden. Endringen er justert for utbytte, sluttkursen er ikke det, så de to stemmer ikke helt med hverandre (FR-101, FR-407).
- Ikke vurdert: en dag uten lagret vurdering. Signalet regnes aldri ut på nytt av kursene i ettertid (designregler §2, story 2.7).
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* «Ikke vurdert: en børsdag uten lagret vurdering. Har raden en grunn, står grunnen, og en dag som ikke er børsdag, står som «ikke børsdag» (§2, FR-409). Signalet regnes aldri ut på nytt i ettertid (FR-101, story 2.7).»
- KI-tekst: tekst fra språkmodellen, alltid merket «Laget av KI». Modellnavnet står i en liten linje under teksten (FR-602).
- Hjelp: faste tekster vi har skrevet og sjekket.
- Gul strek: det viktigste på siden. I KI-teksten har tall som er sjekket mot grunnlaget, prikket strek og farge etter retning.
  *Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* det viktigste på siden merkes med fet skrift. I KI-teksten har tall som er sjekket mot grunnlaget, prikket strek i tekstfargen (svar 7). Gult betyr bare 3 av 3 (§3).
  *Lagt til 2026-10-14 (gruppen 14.10 kl. 17:17 og skissen gruppen valgte like etter, instruksjonen kl. 17:31):* i overskriften har det viktigste en lys oransje markering, `#F8DE9C` fra 60 % av høyden, som i originalen, uten fet skrift. I oversikten er det «N av M aksjer», og på aksjesiden «skilte seg ut <ukedag>» (PR 3 av 8.0d).
- Antall: telles alltid og står aldri fast som 15, så tallene følger lista når egne aksjer kommer med.
- Hvor mange aksjer: én grense for hele lista, «opptil 18 aksjer», vist som «16 av 18 aksjer». Ikke «opptil 3 i tillegg».
- Hjelp bak «?»: forklaringer som ellers ville stått som løs tekst, samme utseende som «Vis meg rundt».
- Ikke «v1.1» eller «(idé)» i tekster brukeren leser. De stiplede merkene på tavla («Idé til v1.1», «Ønsket», «Planlagt») er for gruppa.
- Lenken går til selskapets investorside, den norske når den finnes, uten å skrive «på norsk» (Marian 02.10 kl. 21.56 og 06.10 kl. 20.42). NewsWeb og Oslo Børs nevnes uten lenke.
- Skrift (valgt 01.10): IBM Plex Sans til all tekst og alle tall, med tabelltall. Newsreader bare til overskrifter og titler, også når det står et tall i dem.

Ord kan endres rett i tavla. I appen samles hjelpetekstene i én fil (8.0b).

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3):* Ord endres her, med dato og grunn, og så i tavla.

### Bransjene

*Lagt til 2026-10-13, fra tavla «Bransjer», versjon 1791623938-3408, uten eksempelet BAKKA (en egen aksje). Tavla kaller de 5 nye «idé til v1.1», men Marian tok alle 13 inn nå (kl. 11:50). Brukeren ser «bransje», og koden sier `sektor` (svar 24).*

| Bransje | Hva som hører til | Hos Euronext (ICB) | I lista i dag |
|---|---|---|---|
| Energi | Olje og gass, oljeservice og utstyr til fornybar energi | Energy | EQNR, VAR, AKRBP, DNO |
| Finans | Banker, forsikring og andre finansselskaper | Financials | DNB, GJF |
| Industri | Forsvar, maskiner, bygg, elektronikk og transport utenom skip | Industrials, utenom shipping | KOG |
| Materialer | Metaller, gruver, kjemikalier, gjødsel og skog | Basic Materials | NHY, YAR |
| Shipping | Rederier og skipsfart | Marine Transportation, som indeksen OBSHX | FRO, MPCC |
| Telekom | Mobil, bredbånd og utstyr til nett | Telecommunications | TEL |
| Sjømat | Oppdrett og fiske | Farming, Fishing, Ranching and Plantations, som indeksen OBSFX | MOWI, SALM |
| Konsum | Mat, drikke, dagligvarer og pleieprodukter, utenom sjømat | Consumer Staples, utenom sjømat | ORK |
| Forbruk | Butikker, media, reiser, fritid og biler | Consumer Discretionary | Ny |
| Teknologi | Programvare, IT-tjenester og maskinvare | Technology | Ny |
| Helse | Legemidler, bioteknologi, medisinsk utstyr og helsetjenester | Health Care | Ny |
| Eiendom | Selskaper som eier, leier ut eller utvikler eiendom | Real Estate | Ny |
| Kraft | Strøm og fornybar kraft, vann og avfall | Utilities | Ny |

## 5. Utseendet

*Avgjort 2026-10-13 kl. 23:39, gruppen, etter planen for story 8.0d (kl. 23:27) og [utdraget fra designtavla 13.10](designutdrag-2026-10-13.md). Rettet kl. 23:43: det viktigste i en overskrift merkes med fet skrift. Ført 2026-10-14 i PR 1 av 8.0d.*

**Hvorfor:** sidene skal se ut som forslaget gruppen valgte. Der tavla ikke holder WCAG, eller strider mot §3 og §4, går reglene her foran tavla.

**Fargene.** Hver farge har ett navn i stilen, og ingen farge skrives fast i en mal.

- Blekk `#16181D`: hovedtekst, stripa, kolonneraden, fyllet i «3 av 3» og fokus.
- Tekst `#3C4048`: brødtekst og innledning.
- Dempet `#5F646C`: etiketter, linja under navnet, fotnoter og aksetekst.
- Dempet 2 `#70757D`: en sjekk som ga 0.
- Bakgrunn `#F3F2EE`, Kort `#FFFFFF`, Strek `#E4E2DB`, Strek 2 `#D6D3CA` og Rutenett `#ECEAE4`.
- Positiv `#13703C` på `#E4F4EA`, Negativ `#B42318` på `#FBE9E6`, Blandet `#6A46A0` på `#F0EBF8` og Ingen `#5F646C` på `#EEEDEA`.
- Gul ring `#a67c00`: ringen rundt «3 av 3» og streken på 4 px til venstre i en rad med 3 av 3, på lys bakgrunn. Kontrasten er 3,82 mot hvitt, 3,41 mot Bakgrunn og 4,65 mot blekk.
- Lys gul `#F2B53A`: bare på blekk, det vil si logoens høyeste søyle, klokka og fokus i stripa (9,68:1).
- Båndet «Skilte seg ut» `#ECE9E1`, en nøytral, varm grå, med kant i Strek og tekst i blekk (14,64:1). Radene under er hvite. Båndet «Øvrige aksjer» `#F7F6F2`, med kant i Strek og tekst i Tekst (9,62:1). Gult står ved en aksje bare ved 3 av 3 (§3), og «Skilte seg ut» har også 2 av 3.
- Hjelp `#6B4E00` på `#FFF1CC`: merket «Hjelp» i hjelpevinduet (6,89:1).
- Kurs `#1F4E8C`. Snitt `#9A5A0E`, både streken og navnet (5,46:1 mot hvitt).
- Det grå feltet: sporet `#F1EFEA` og feltet `#8A847A` (3,23:1).
- I stripa: tekst `#DADDE2`, `#C9CCD2` og `#A9AEB8`, og kantene `#3A3E47` og `#2A2E36`. Under kolonnenavnene: `#B9BDC5`.

**Kontrast.** Tekst har minst 4,5:1 mot bakgrunnen den står på. Streker, felt og fokus som må ses for å forstå siden, har minst 3:1 (WCAG 1.4.11). En test regner det ut fra fargene i stilen. Retningsfargene er nesten like lyse, så retningen står alltid med ord og symbol (§4).

**Skriften** følger §1. Newsreader brukes til logoen (27 px, 600), overskriftene (oversikten 52 px og aksjesiden 56 px, 500), delene på aksjesiden (36 px), navnet på en sjekk (30 px, 600) og tittelen i hjelpen (23 px, 600). Resten er IBM Plex Sans, med størrelsene i utdraget §3. Alle tall har tabelltall. Det viktigste i en overskrift har fet skrift, ikke gul understrek (§4, rettet 13.10).

*Målt 2026-10-14, da filene ble hentet:* IBM Plex Sans har ikke OpenType-funksjonen `tnum`, i motsetning til det §1 sier. Sifrene 0–9 er like brede som standard (600 enheter i alle fire vektene), så tallene står rett under hverandre uten den. Newsreader har `tnum`. Testen krever like brede sifre i hver fil, og `tnum` der filen har proporsjonale sifre som valg (`pnum`).

**Stripa øverst.** Den har blekk over hele bredden og to rader. Den første raden er 72 px med logoen: tre søyler, den høyeste i lys gul, og «OSE Signal» i hvitt. Den andre er 38 px med klokka og «Oppdatert …». Mellom radene står en strek i `#2A2E36`. I demoen står hele merket «Demoversjon. Eksempeltall: …» som egen rad i stripa, med samme ordlyd (13,04:1). Stripa har ingen knapper før sidene de viser til, finnes (8.3, 8.9 og 8.10).

**Kolonneraden og båndene.** Kolonneraden er 64 px i blekk, med navnene i hvitt og en linje under i `#B9BDC5`. Båndet «Skilte seg ut» og båndet «Øvrige aksjer» har antallet i en pille. Radene under «Skilte seg ut» er hvite og 66 px, og en rad med 3 av 3 har en strek på 4 px i Gul ring til venstre. Radene under «Øvrige aksjer» er hvite og 54 px.

**Pillene og brikkene.**

- «3 av 3» er en pille med fyll i blekk, hvit tekst og en ring på 2 px i Gul ring.
- «2 av 3» har fet skrift og strek, uten fyll og uten gult (§3, beslutningen 13.10 kl. 21:27).
- «1 av 3» og «0 av 3» er tekst uten pille.
- T, B og I står i brikker på 34 × 24 px med radius 6. +1 har grønt fyll og -1 rødt, begge med hvit tekst. 0 er hvit med tekst i Dempet 2 og kant i Strek 2.
- Retningen står i en pille på 28 px med symbolet først.

**Avstander.** Sidemargen er 120 px ved 1280 px og 16 px ved 390 px. Det er 40–44 px mellom delene i oversikten og 60 px på aksjesiden. Kort har radius 16, kant i Strek og luft 18–22 px. Brikker har radius 6, merker 8 og piller 999. Klikkflater er minst 44 px.

**Fokus.** På lys bakgrunn er fokus `outline: 3px solid` i blekk med `outline-offset: 2px` (15,85:1). I stripa er fokus lys gul (9,68:1).

**Rekkefølgen av delene.**

- Oversikten: stripa, så overskriften og innledningen med kortet «Slik leser du tabellen» til høyre for dem, så tabellen, og til slutt bunnlinja. På smal skjerm står kortet under innledningen.
- Aksjesiden: stripa, så merkene med overskriften og innledningen, nøkkeltallene, de 3 sjekkene, kursgrafen, fotnotene og bunnlinja.
- Feilsiden: stripa, så meldingen og bunnlinja.
- Delene som hører til senere stories, settes inn på sin plass når de bygges (utdraget §11).

**Det grå feltet.** Hvert sjekkort har et spor på 10 px med runde ender, og feltet der sjekken gir 0. Grensene står over feltet og «gir 0» under. Målingen er en prikk på 20 px i resultatfargen. Skalaen er `aria-hidden`, fordi teksten i kortet sier det samme.

*Lagt til 2026-10-14 (gruppen 14.10 kl. 17:17 og skissen gruppen valgte like etter, instruksjonen kl. 17:31, PR 2 av 8.0d):* fargene ved en aksje er som i originalen, og linjene over om gul ring `#a67c00`, båndet `#ECE9E1` og fet skrift i overskriften gjelder ikke lenger for oversikten.

- Sterk oransje `#F2B53A`: ringen rundt «3 av 3» og streken på 4 px til venstre i en rad med 3 av 3.
- Lys oransje `#F8DE9C`: streken på 4 px i en rad med 2 av 3, og markeringen under det viktigste i overskriften (fra 60 % av høyden). Overskriften har ikke fet skrift.
- 1 av 3 og 0 av 3: ingen strek og ingen farge.
- Båndet «Skilte seg ut» `#FFF6DC` med kant `#F0E3BD`, og tekst og pille i `#6B4E00`, med «signalstyrke 2 eller mer» etter pillen. «Øvrige aksjer» har «signalstyrke 0 eller 1». Tallene kommer fra Parametre. Radene er hvite.
- Kontrasten for teksten i båndet, pillen og markeringen regnes i testen. Ringen og strekene trenger ikke 3:1 mot hvitt, fordi teksten sier det samme (FR-103) og pillen har svart fyll.
- Overskriften på 52 og 56 px er Newsreader i optisk størrelse 72pt, Medium. Resten av Newsreader er 16pt.
- Under kolonnenavnene står bare «NOK» under Sluttkurs, i `#B9BDC5`.
- Tidspunktet står én gang, som «Oppdatert …» i stripa, med «?» ved siden av.

*Lagt til 2026-10-14 (gruppen 14.10 kl. 19:59, «ja til begge»):* «2 av 3» er den hvite pillen fra originalen (utdraget §6): samme form som «3 av 3», hvit, med tekst og kant i blekk og uten ring. Den lys oransje streken på 4 px til venstre i raden står som før. Linja over om at «2 av 3» har fet skrift og strek, uten fyll, gjelder ikke lenger.

*Lagt til 2026-10-15 (gruppens svar kl. 12:15, BH20 i gjennomgangen av PR 3 av 8.0d):* i kortet «Slik leser du tabellen» viser feltet ved Signalstyrke en grønn «+1» over en rød «-1», med en egen klasse i kortet, så regelen for brikkene i tabellen ikke virker inn. Teksten ved Signalstyrke sier «Både +1 og -1 teller som utslag.», og teksten ved Retning sier «Ga noen +1 og noen -1, står det Blandet.».

*Lagt til 2026-10-15 (gruppens svar 4 og 5 på planen for story 8.15, instruksjonen kl. 14:01):* kolonnene som kan sorteres, har en vinkel ved navnet i kolonneraden: dempet i `#B9BDC5` når kolonnen ikke er valgt, og hvit når den er valgt. Når en kolonne er valgt, står en linje rett over tabellen, «Sortert på <kolonne>, synkende» eller «stigende», og lenken «Standard rekkefølge» til /. Uten valg står ingen linje.

*Lagt til 2026-10-15 (gruppens svar 8 og 9 på funnene i PR #43 for story 8.15, instruksjonen kl. 15:25):* linja over tabellen og teksten for skjermleseren i kolonneraden sier det samme. For Retning står «stigende (A til Å)» eller «synkende (Å til A)». Linja slutter med «innenfor hver del», for eksempel «Sortert på endring, synkende, innenfor hver del.»
