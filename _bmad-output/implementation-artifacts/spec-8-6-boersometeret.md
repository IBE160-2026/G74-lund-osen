---
title: 'Story 8.6: børsometeret'
type: 'feature'
created: '2026-10-23'
status: 'in-review'
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
  *Rettet 2026-10-23 (gjennomgangen, BH1):* høy er over `volumfaktor`, med «>» som interesse-sjekken, og vanlig er fra 1 til og med `volumfaktor`. Uten vurdering eller volumforhold er ruta i midtre størrelse.
- **Rammen** følger styrken i vurderingen for dagen som vises: 3 gul, 2 mørk, ellers ingen. Uten vurdering ingen ramme.
  *Rettet 2026-10-23 (gjennomgangen, VG1):* rammen følger siste børsdag. En annen dag har gult ved 3 av 3 på siste børsdag og ingen mørk ramme (designregler §3), og en dag uten vurdering har ingen ramme.
  *Rettet 2026-10-23 (gruppens svar kl. 09:24, a):* gult følger designregler §3 også en dag uten vurdering og en dag uten kurs: en aksje med 3 av 3 på siste børsdag har gul ramme på alle dagene, og mørk ramme for 2 av 3 står bare for siste børsdag. Det retter instruksjonen kl. 00:09.
- **Hovedindeksen** står for siste børsdag også når «Velg dag» viser en annen dag, med datoen ved verdien, som på oversikten.
- **Bransjer uten aksjer** i lista vises ikke. En aksje med en bransje utenfor de 13 står sist, under bransjens navn.

## Gjennomgangen 23.10

Blind Hunter (BH1–BH10), Edge Case Hunter (ECH1–ECH7) og Verification Gap (VG1–VG11), kjørt samtidig, før hele settet. Rettet i `2d72dc2` og `d427910`, og før det i `35f555e`, der testene for 8.6 b fant at ruta for en aksje uten kurser lenket til en aksjeside som gir 404 (FR-204).

| Funn | Dom | Utfall |
|---|---|---|
| VG1 rammen fulgte dagen som vises | høy | rettet: gult følger 3 av 3 på siste børsdag, 2 av 3 merkes bare siste børsdag (designregler §3) |
| VG2 README-en | medium | rettet i `d427910` |
| BH1 «høyt» ved `>=`, interesse ved `>` | medium | rettet |
| BH2, ECH4 volumtallet ved grensen | medium | rettet med `desimaler_mot_grense` |
| BH3, VG3, ECH1 dag før første kurs | medium | rettet, med egen melding |
| BH4, ECH2 lenkene mistet dagen | medium | rettet: `?dag=` til aksjesiden |
| VG4, VG5, VG6, VG8, VG9, VG11 tester | medium og lav | rettet: nye tester |
| VG7 gul ramme i `#F2B53A` på lys bakgrunn | lav-medium | rettet: `--gul-symbol` |
| VG10, BH6, BH7, BH8, BH10, ECH6 | lav | rettet |
| BH5, ECH3 hovedindeksen for siste børsdag på en annen dag | lav | avgjort i spesifikasjonen; siden sier det nå med en linje |
| BH9 fokus og mørk ramme i samme farge | lav | ikke rettet: fokus er blekk etter designregler §4 |
| ECH5 seriene leses to ganger | lav | ikke rettet: 15 ms med demobasen |
| ECH7 gjentatt `dag` i adressen | lav | ikke rettet: skjemaet sender én |

**Åpent punkt for gruppen (regel 12):** designregler §3 sier at gult står også når siden viser en annen dag. Instruksjonen kl. 00:09 sier at en dag uten vurdering har ingen ramme. Koden gjør det begge sier for en dag med vurdering, og det instruksjonen sier for en dag uten: ingen ramme.
*Lukket 2026-10-23 (gruppens svar kl. 09:24, a):* gult følger designregler §3 også en dag uten vurdering.

**Avvik fra instruksjonen:** ruta for en aksje uten kurser er ikke en lenke, fordi aksjesiden gir 404 for den (FR-204). Hjelpen sier det.
*Lukket 2026-10-23 (gruppens svar kl. 09:24, b):* alle ruter lenker til aksjesiden. Aksjesiden for en aksje i lista uten kurser svarer 200 med navnet, bransjen og en beskjed, uten graf og sjekker (`aksje_uten_kurser.html`), og navnet under tabellen på oversikten og i Min liste lenker dit. Siste avsnitt i FR-204 forbeholder fortsatt 404 for en aksje uten en eneste kursrad, og `prd.md` er ikke rettet (åpent punkt under story 8.6 i `epics.md`).

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: snittet av bare én aksje, gult ved 2 av 3, og et fast antall bransjer.

## Det som ikke endres

- Ingen nye kall og ingen ny tabell. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke, og demobaser lages bare i midlertidige mapper.
- Oversikten, Min liste og aksjesiden viser det samme som før.
