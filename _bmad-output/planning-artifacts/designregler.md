---
title: "Designregler"
status: aktiv
created: 2026-10-01
updated: 2026-10-13T11:06
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

*Lagt til 2026-10-05:* tabelldelen av regelen, gul ring rundt «3 av 3» og 2 av 3 merket uten gult, tas inn i story 8.0c.

## 4. Ordliste – samme ord på alle sidene (01.10)

*Ført 2026-10-13 ordrett fra designtavla i Claude, versjon 1791623938-3408, med «-» for «•». Ordlista er ikke kontrollert mot koden og PRD-en etter 02.10. Det gjør den samlede endringen (samlelista punkt 8 og 10) før noe herfra brukes i appen.*

- Signalstyrke 0–3: hvor mange av de 3 sjekkene som slo ut.
- Sjekkene: trend (T), bevegelse (B) og interesse (I). Hver gir +1, 0 eller -1, skrevet «T +1» overalt, som kolonnen «Ga» i appen.
- Retning: Positiv, Negativ, Blandet eller Ingen, med pil (FR-103). Pilene brukes ikke til noe annet.
- Skilte seg ut: signalstyrke 2 eller mer. Signalstyrken skrives «3 av 3», og 3 av 3 er fylt med gul ring.
- Tall med sifre, også små: «3 av 3 sjekker», ikke «alle tre».
- Endring: fra forrige børsdag, utbyttejustert, med fortegn. Kolonnehodet sier «i går», som den første knappen i periodevalget.
- Retning forklares med tall: «1 sjekk ga +1, 2 ga -1», ikke «peker hver sin vei». På aksjesiden står sjekkene med navn: «Trend ga +1. Bevegelse og interesse ga -1.»
- Beløp skrives i NOK, ikke «kroner» eller «kr» (Marian 01.10). Øverst på hver side, i den svarte stripa, står når dataene ble oppdatert og når neste oppdatering tidligst kan komme, med klokke.
- Egen aksje: blått merke «Egen» og blå strek. Den står i tabellen sammen med de andre og sorteres likt. Under tabellen står bare valget: hentet eller venter, og Fjern. Stjerne betyr Min liste. Gul ring, gul ramme og gult symbol betyr 3 av 3 i går, også når en periode er valgt. I børsometeret har ruta gul ramme med hvit kant og merket «3 av 3».
- Utenfor målingen: en egen aksje som omsettes for under 32 MNOK om dagen. Grensene i signalet er målt på aksjer som omsettes for over 32 MNOK, og så mye handel gjør dem lette å kjøpe og selge (begrunnelser.md §2). Teksten sier ikke «de 15» (Marian 02.10 kl. 21.56). Ikke «krav» og ikke «omsatt for lite». Grått merke, fordi gult betyr 3 av 3.
- Børsen, bransjen eller selskapet: hvor dagens bevegelse ser ut til å komme fra, ikke hvorfor. Børsen er hovedindeksen, og tallet står med «for hovedindeksen». Regnes alltid av lista som er aktiv, også egne aksjer som er hentet. Svarene er «Børsen», «Bransjen», «Selskapet», «Selskapet eller bransjen» og «Liten bevegelse».
- Bransjer: 13, hver med navn og symbol (tavla «Bransjer»). De 11 hos Euronext (ICB), med sjømat og shipping for seg, som Euronexts indekser OBSFX og OBSHX. Nye: Forbruk, Teknologi, Helse, Eiendom og Kraft.
- Sortering: vinkler i den svarte kolonneraden. Pilene er bare for retning.
- Stiplet linje betyr bare hovedindeksen. 50-dagers snittet og grensen for interesse er heltrukne, og kursen er tykkere enn snittet.
- Datoer: 22.09, uten punktum til slutt, og med år bare når året er et annet: 29.09.2025.
- Knapper i en dialog: hovedvalget til høyre, det andre valget eller Avbryt til venstre for det. Samme handling har samme ord overalt, for eksempel «Følg aksjen».
- Merker ved et navn («Egen», «Utenfor målingen») har samme størrelse.
- Uten farger: retning, endring og sjekkene står alltid også som tekst, fortegn eller pil, og linjer og søyler kan leses av plassen over eller under null-linja.
- Periodevalg, likt overalt: «I går», 1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år og «Velg dag». Var siste børsdag ikke i går, står ukedagen, for eksempel «Fredag» på en mandag. Grafen åpner med 6 mnd (FR-201).
- Sammenligning: hver rad får en linje til for dagen du sammenligner med: sluttkursen, endringen siden da, og T, B og I den dagen, med T rett under T. Retningen står bare for i går. Kolonnehodet sier «i går», og datoen står i gult under.
- U ved kursen: aksjen har betalt utbytte i perioden. Endringen er justert for utbytte, sluttkursen er ikke det, så de to stemmer ikke helt med hverandre (FR-101, FR-407).
- Ikke vurdert: en dag uten lagret vurdering. Signalet regnes aldri ut på nytt av kursene i ettertid (designregler §2, story 2.7).
- KI-tekst: tekst fra språkmodellen, alltid merket «Laget av KI». Modellnavnet står i en liten linje under teksten (FR-602).
- Hjelp: faste tekster vi har skrevet og sjekket.
- Gul strek: det viktigste på siden. I KI-teksten har tall som er sjekket mot grunnlaget, prikket strek og farge etter retning.
- Antall: telles alltid og står aldri fast som 15, så tallene følger lista når egne aksjer kommer med.
- Hvor mange aksjer: én grense for hele lista, «opptil 18 aksjer», vist som «16 av 18 aksjer». Ikke «opptil 3 i tillegg».
- Hjelp bak «?»: forklaringer som ellers ville stått som løs tekst, samme utseende som «Vis meg rundt».
- Ikke «v1.1» eller «(idé)» i tekster brukeren leser. De stiplede merkene på tavla («Idé til v1.1», «Ønsket», «Planlagt») er for gruppa.
- Lenken går til selskapets investorside, den norske når den finnes, uten å skrive «på norsk» (Marian 02.10 kl. 21.56 og 06.10 kl. 20.42). NewsWeb og Oslo Børs nevnes uten lenke.
- Skrift (valgt 01.10): IBM Plex Sans til all tekst og alle tall, med tabelltall. Newsreader bare til overskrifter og titler, også når det står et tall i dem.

Ord kan endres rett i tavla. I appen samles hjelpetekstene i én fil (8.0b).
