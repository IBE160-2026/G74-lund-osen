---
title: 'Story 8.16 (8.16b): når en dag er valgt, viser hele aksjesiden den dagen'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3adf22d'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-16-periodene-i-kursgrafen.md'
---

## Intent

**Problem:** etter 8.16 viser kortene øverst, «Hvorfor signalet ble» og KI-teksten alltid siste børsdag, mens linja over grafen viser dagen som er valgt med «Velg dag». Siden kan da ha to ulike signaler.

**Grunnlaget:** gruppens svar 19.10 kl. 00:00, som utvider svaret 18.10 kl. 21:50, og instruksjonen 19.10 kl. 10:32.

## Kontrollpunktene

- a) Siden for dagen: med en valgt dag bygges detaljen av kursraden og raden i vurdering for dagen, og KI-teksten av raden i KI-loggen for dagen, gjennom leserne som finnes. Overskriften, datoen, sluttkursen, endringen fra forrige børsdag, signalstyrken, retningen og sjekkene med målingene er dagens. Uten rad står «– ikke vurdert», grunnen eller «– ikke børsdag», og uten KI-rad teksten appen har for en dag uten KI-tekst. Øverst står et merke om at siden viser en tidligere dag, med en lenke tilbake til siste børsdag. Endringen og signalet for dagen står i kortene, ikke i en egen linje over grafen, og grafen har dagen merket. Knappen for KI-teksten tar deg tilbake til den samme dagen. Med en periode eller den første knappen viser toppen siste børsdag, som nå.
- b) Tekstene (regel 19): hjelpen til periodene og «Velg dag», og `docs/hjelp.md` hvis den nevner dem. Endres en fil bak bildet av oversikten, tas bildet på nytt slik feilmeldingen i testen sier.
- c) Testene, med «Ville feilet hvis»: med «Velg dag» viser kortene, sjekkene og KI-teksten den valgte dagen og ikke siste børsdag; en dag uten vurdering, en dag med en grunn og en lørdag; en dag uten KI-rad; merket og lenken tilbake; knappen for KI-teksten beholder dagen; med en periode viser toppen siste børsdag; for en valgt dag kalles `vurder` ikke (AD-7). Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: kortene fra siste børsdag med en valgt dag, KI-teksten fra siste børsdag, og en valgt dag som regner signalet.

## Planen, én commit per punkt

1. a) `bygg_detalj` i `src/aksjedetalj.py` får dagen og raden i vurdering for den. Uten dagen er alt som før. Med dagen er serien kursradene til og med dagen: sluttkursen og endringen er fra kursraden for dagen, og sjekkene fra raden i vurdering, lest med `Oversiktsleser.vurdering` fra 8.16. Ruta i `src/app.py` leser raden én gang og bruker den både til detaljen og til merket i grafen. KI-teksten leses for `detalj.dato` og prøves mot vurderingen som vises. Malen får merket øverst, linja over grafen står bare for den første knappen, og bryteren sender adressen med dagen, som `_TILBAKE` godtar. De testene fra 8.16 som leste linja over grafen for en valgt dag, leser kortene i stedet, i samme commit, så hver commit er grønn.
2. b) Hjelpeteksten «perioden» sier at «Velg dag» viser hele siden for dagen. `docs/hjelp.md` nevner ikke periodene (`git grep`), så den endres ikke. `src/hjelpetekster.py` står bak bildet, så bildet tas på nytt hvis avtrykket endres.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Siste børsdag** er siste rad i kursserien, som i resten av siden. Velges den med «Velg dag», er siden den samme som for siste børsdag, uten merket om en tidligere dag.
- **En dag uten kurs**, som en lørdag: datoen er dagen, sluttkursen og endringen er «–», og teksten fra `les_tilstand` står, som i oversikten. Grafen slutter dagen før, som i 8.16.
- **Lenken tilbake** går til `/aksje/<symbol>`, siden slik den åpnes, med siste børsdag øverst.
- **Bryteren** godtar `/aksje/<symbol>?dag=ÅÅÅÅ-MM-DD` og ellers bare stiene den godtok før. Datoen leses på nytt av `les_valg`, så en dag som ikke kan vises, gir 6 mnd og beskjeden fra 8.16.
- **Linja over grafen** står fortsatt for den første knappen, der dagen er siste børsdag og det samme som kortene. For en valgt dag står endringen og signalet bare i kortene.

## Boundaries

- Alt leses fra det som er lagret, og signalet regnes aldri på nytt (AD-7).
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe.
