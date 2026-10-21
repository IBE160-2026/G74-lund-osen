---
title: 'Story 2.7 (2.7b): historikken, «Signalet dag for dag», på aksjesiden'
type: 'feature'
created: '2026-10-21'
status: 'review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7c55e44'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7a-stilen-i-en-css-fil.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-16b-dagen-paa-hele-siden.md'
---

## Intent

**Problem:** briefen v8 lover historikken i v1 (gruppens svar 19.10 kl. 15:43), og story 2.7 står igjen etter 2.7a. Aksjesiden viser i dag bare én dag om gangen, og FR-408s spørsmål, «hva sa løsningen om aksjen for to uker siden?», har ikke et svar i appen.

**Grunnlaget:** story 2.7 i `epics.md`, med avgjørelsen 2026-10-21 under «Prioritering» og under storyen, og instruksjonen 21.10 kl. 16:53. Svaret 19.10 kl. 11:24 som instruksjonen viser til, står ikke i repoet, så innholdet bygger på linja 21.10: historikken er månedsvisningen fra tavla, med piler så langt kursserien går tilbake, og målingene står på siden for dagen (8.16b), som hver dag lenker til. `designregler.md` §3 sier hvordan 3 av 3 merkes.

## Kontrollpunktene

- a) Lesingen: en lesemetode for en periode i `Vurderingslager`, uten slette- eller endremetode (`AD-7`), som siden leser gjennom (`AD-3`), én spørring per måned. Hver dag går gjennom `les_tilstand`, så styrke 0, en grunn, en manglende rad, en dag som ikke er børsdag og en dag utenfor børskalenderen aldri ser like ut.
- b) Siden: nederst på aksjesiden «Signalet dag for dag» med en kort tekst og en rad per uke med ukenummeret, man–fre og «x av y dager skilte seg ut» for uka. Hver dag har datoen, retningen, T, B, I og styrken, eller «–» og tilstanden, og 3 av 3 merkes som i `designregler.md` §3. Hver dag med kurs lenker til siden for dagen. Under står «<måned> samlet: <navn> skilte seg ut x av y børsdager» og hvor mange dager hver sjekk slo ut, der y er dagene med en vurdering, også for uka. Måneden er den for dagen siden viser. Pilene går fra måneden for første til siste kursrad, med en parameter som beholder perioden eller dagen; en ugyldig måned gir måneden for dagen og en kort beskjed, med 200. Dager etter siste kursrad står tomme. Stilen står i CSS-fila (2.7a). Avsnittet om investorsiden (10.5) står fortsatt rett under grafen. Alt virker på 390 px uten vannrett rulling. Hjelpen ved «?» på Sluttkurs sier dagen siden viser (U5). Hjelpen, `docs/hjelp.md` og README-en følger med (regel 19), og bildene tas på nytt.
- c) Testene, med «Ville feilet hvis»: hver tilstand ser ulik ut; tallene for uka og måneden; lenken til dagen; pilene i begge ender, en ugyldig måned og måneden for en valgt dag; dager etter siste kursrad er tomme; porten har lesemetoden og ingen slette- eller endremetode; `vurder` kalles ikke. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: historikken regnet med `vurder`, en manglende rad vist som styrke 0, og dager etter siste kursrad vist som «– ikke vurdert».

## Planen, én commit per punkt

1. a) `Vurderingslager.les_periode(symbol, fra, til)` i `src/vurderingsdata.py`, og `SqliteVurderingslager.les_periode` i `src/lagring_sqlite.py`: én `SELECT` med `dato BETWEEN ? AND ?`, som gir en `dict` fra dato til `Vurdering` eller `Grunn`, med samme kontroll av nøkkelen som `les`. Den rene logikken i en ny fil, `src/historikk.py`: måneden fra adressen, ukene, dagene gjennom `les_tilstand` og tallene. Fila importerer ikke `signalberegning.vurder`.
2. b) Ruta i `src/app.py` leser måneden én gang gjennom `SqliteVurderingslager`, med aksjen siden viser som lista. Malen `src/templates/aksje.html` får avsnittet nederst, `src/static/stil.css` stilen, `src/hjelpetekster.py` hjelpen til historikken og Sluttkurs på aksjesiden, og `docs/hjelp.md` et spørsmål. Bildene tas på nytt, og avtrykkene i `tests/test_docker.py` rettes.
3. c) Testene i `tests/test_historikken.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Plasseringen:** avsnittet står nederst på siden, etter avsnittet om investorsiden og før hjelpevinduene. Avsnittet om investorsiden står fortsatt rett under grafen, etter de to fotnotene som sto der før.
- **Måneden** i adressen er `maaned=ÅÅÅÅ-MM`. Uten den er måneden den for dagen siden viser: dagen fra «Velg dag», ellers siste kursrad. En verdi som ikke kan leses, eller en måned utenfor kursserien, gir måneden for dagen og en beskjed under pilene, med 200.
- **Pilene** står over ukene: «‹ <forrige måned>» og «<neste måned> ›», bare når den måneden har en kursrad i serien. Lenkene beholder `dag` når en dag er valgt, ellers `periode` når adressen hadde en gyldig periode, og ender med `#signalet-dag-for-dag`, så siden blir stående ved avsnittet.
- **Ukene** er ukene etter ISO 8601, med ukenummeret, og bare mandag til fredag. En dag i uka som hører til en annen måned, står som en tom plass og telles ikke.
- **Dagen:** datoen, og med en vurdering retningen med symbolet og ordet, T, B og I som brikkene i oversikten, og styrken som «x av 3». Uten vurdering «–» og teksten fra `les_tilstand`. 3 av 3 får pillen med svart fyll og ring i sterk oransje og strek til venstre, som i oversikten (§3). 2 av 3 merkes ikke, fordi §3 merker 2 av 3 bare for siste børsdag.
- **«Skilte seg ut»** er styrken på terskelen eller over, som i oversikten (`Parametre.terskel`). Uka og måneden teller dagene med en vurdering. Har uka ingen, står «ingen dager med vurdering». Har måneden ingen, står «<måned> samlet: <navn> har ingen dager med vurdering.», uten tallene for sjekkene.
- **Sjekkene som slo ut:** antallet dager med +1 eller -1 for hver av de tre, med navnene fra aksjesiden.
- **Lenken:** hver dag med en kursrad lenker til `/aksje/<symbol>?dag=ÅÅÅÅ-MM-DD`, siden for dagen fra 8.16b, som viser målingene. Første dag i serien får ingen lenke, fordi `les_valg` ikke godtar den (8.16, BH3).
- **Dager etter siste kursrad** står med bare datoen. Har en slik dag likevel en rad i vurdering, som en grunn når hentingen feilet, vises raden, fordi den er skrevet og ikke er et hull.

## Avgjort underveis

## Gjennomgangen

## Mutantene
