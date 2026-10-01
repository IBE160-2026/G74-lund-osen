---
title: "Designregler"
status: aktiv
created: 2026-10-01
updated: 2026-10-01T15:31
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
