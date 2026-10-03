---
title: "Designregler"
status: aktiv
created: 2026-10-01
updated: 2026-10-03T22:48
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
- Startdagen for periodene følger én skriftlig regel, lik for alle, som skrives og testes før et periodevalg bygges (NFR-08).

**Hvorfor:** Samme knapp betyr det samme overalt, så brukeren lærer valget én gang. Den første knappen sier hvilken dag tallene gjelder, med ord brukeren kjenner.

**I dag:** appen har ikke noe periodevalg. Kursgrafen har faste seks måneder (FR-201), og flere perioder står under «Hvis vi rekker».

## 3. Gult betyr 3 av 3

*Avgjort 2026-10-01, Marians beslutning.*

- Ved en aksje betyr gult at den fikk 3 av 3 på siste børsdag: gul ring rundt pillen «3 av 3» i tabellen, gul ramme med hvit kant og merket «3 av 3» i børsometeret, og gult bransjesymbol over søylen under hovedindeksen (FR-105).
- Gult står også når siden viser en periode eller en annen dag, så aksjen er lett å kjenne igjen. 2 av 3 merkes uten gult, og bare for siste børsdag.

**Hvorfor:** 3 av 3 er det sterkeste signalet, og samme farge overalt gjør det lett å finne.

**I dag:** appen bruker ikke gult. Rader som skiller seg ut, har lys grå bakgrunn og merket «skiller seg ut» (index.html).
