---
title: 'Story 8.6: børsometeret'
type: 'feature'
created: '2026-10-23'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c497677'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-10-13.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

## Intent

**Problem:** børsometeret står i designforslaget, med en knapp i stripa, men mangler i appen (U70 i `docs/ux-logg.md`).

**Grunnlaget:** story 8.6 i `epics.md`, FR-106 i `prd.md`, avgjørelsen 22.10 kl. 00:09 (rekkefølgen) og 22.10 kl. 23:19 under «Prioritering» og story 8.6: «børsometeret blir som tavla, én rute per aksje ordnet etter bransje, med farge for endringen, størrelse for volumet mot vanlig og ramme for signalet, og snittet per bransje i overskriften, som storyen krever. Først for siste børsdag og «Velg dag»; periodene kommer med 8.17.» Storyen er «Ekstra», så den bygges på egen gren og flettes bare ferdig og grønt (svaret 19.10 kl. 14:48). Instruksjonen er den kl. 00:09 i dagsfila 23.10.

## Slik er det i dag (slått opp 23.10 på `c497677`)

- **Story 8.6:** «Én verdi per sektor i lista som er aktiv, regnet som snittet av endringen i FR-101 for aksjene i sektoren», «En sektor med én aksje merkes «1 aksje»», antallet sektorer og aksjer telles fra lista og prøves med en kortere liste, «Gult bare ved 3 av 3 på siste børsdag», «Ingen nye kall og ingen ny tabell». Linja 13.10: de 13 bransjene i `designregler.md` §4, med symbolene fra 8.0d, og brukeren ser «bransje». Avhenger av 8.17 for periodene.
- **FR-106:** snittet av endringen i FR-101 for aksjene i sektoren; en sektor med én aksje «vises som aksjen og merkes «1 aksje»»; «En aksje med 3 av 3 på siste børsdag har gul ramme med hvit kant og merket «3 av 3»»; sektoren står i `aksje`.
- **`designregler.md` §3:** gult betyr 3 av 3, «gul ramme med hvit kant og merket «3 av 3» i børsometeret», og «2 av 3 merkes uten gult». Fra 14.10 er 3 av 3 sterk oransje `#F2B53A` og 2 av 3 lys oransje `#F8DE9C` i tabellen. §4 har de 13 bransjene, i den rekkefølgen tabellen står.
- **Utdraget fra tavla** (`designutdrag-2026-10-13.md`) sier bare at knapperaden har «Markedsoversikt, Børsometer, Min liste». Tavla selv ligger ikke i repoet. Det tavla viser, står i avgjørelsen kl. 23:19.
- **Endringen (FR-101)** er `endring_i_prosent` i `src/markedsoversikt.py`, fra de to siste kursene, på justert kurs.
- **Volumforholdet** er `volumforhold` i den lagrede vurderingen, dagens volum mot medianvolumet (sjekk 3). Grensen for interesse er `volumfaktor` i `Parametre`, 1,5.
- **«Velg dag»** (8.16) finnes på aksjesiden: `?dag=ÅÅÅÅ-MM-DD`, lest med `les_valg` i `src/perioder.py`. Oversikten har det ikke.
- **Bransjesymbolene** er makroen `bransjesymbol` i `src/templates/_bransjer.html`. **Hovedindeksen** står i `index.html` og bygges av `_hovedindeks` i `src/app.py`.

## Kontrollpunktene

- a) Siden `/boersometer`, med knappen «Børsometer» i stripa mellom «Markedsoversikt» og «Min liste»: én rute per aksje i lista, ordnet etter bransje i rekkefølgen i `designregler.md` §4, med symbolet; farge for endringen (FR-101); størrelse i tre trinn for volumforholdet; mørk ramme ved 2 av 3 og gul ved 3 av 3; og snittet per bransje i overskriften, med «1 aksje» der det er én. Hovedindeksen står over, som på oversikten. «Velg dag» viser en tidligere dag, og en dag uten vurdering har ingen ramme og sier «ikke vurdert». En aksje uten kurs står med «Uten data». Hver rute lenker til aksjesiden. De samme tallene står i en tabell for skjermleser og tastatur. Ingen KI og ingen råd, og webserveren henter aldri. Demoen viser det samme. Hjelpen ved «?», `docs/hjelp.md` og README-en følger med.
- b) Testene, med «Ville feilet hvis», uten nett.

## Planen, én commit per punkt

1. a) `src/boersometer.py` (ren logikk), ruta i `app.py`, malen `boersometer.html`, hovedindeksen flyttet til delmalen `_hovedindeks.html`, som oversikten også bruker, knappen i `_ramme.html`, stilen, hjelpeteksten, `docs/hjelp.md` og README-en. Testene som bryter, og avtrykkene bak bildene, følger med i samme commit, med grunnen.
2. b) De nye testene.

## Avgjort i spesifikasjonen

- **Størrelsen** har tre trinn: under 1 (mindre enn vanlig), fra 1 til under `volumfaktor` (vanlig), og fra `volumfaktor` (høy, som gir utslag på interesse). Uten vurdering eller volumforhold er ruta i midtre størrelse.
- **Rammen** følger styrken i vurderingen for dagen som vises: 3 gul, 2 mørk, ellers ingen. Uten vurdering ingen ramme.
- **Hovedindeksen** står for siste børsdag også når «Velg dag» viser en annen dag, med datoen ved verdien, som på oversikten.
- **Bransjer uten aksjer** i lista vises ikke. En aksje med en bransje utenfor de 13 står sist, under bransjens navn.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: snittet av bare én aksje, gult ved 2 av 3, og et fast antall bransjer.

## Det som ikke endres

- Ingen nye kall og ingen ny tabell. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke, og demobaser lages bare i midlertidige mapper.
- Oversikten, Min liste og aksjesiden viser det samme som før.
