---
title: 'Story 8.31: stegkortene og styrken for én dag målt i nettleseren'
type: 'test'
created: '2026-11-14'
status: 'done'
route: 'dispatch'
baseline_commit: '04c26cdb'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-29-din-egen-liste-kom-i-gang.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

Skrevet 14.11 i vinduet som bygde 2.17, etter tillegg 4 (limt inn kl. 21:16,
ført i `docs/ai-prompts/2026-11-14.md`) og gruppens ønske 14.11 kl. 21:07 om at
natta brukes. Rådet anbefalte det. Worktreen `G74-lund-osen-8-31`, grenen
`8-31-maalene-i-nettleseren`, fra `origin/main` (`04c26cdb`), etter at
dokumentrunden (9.13) var flettet. Bare tester og spesifikasjonen. Ingen
endring i `src/`, malene eller stilarket.

8.31 er neste ledige nummer i Epic 8 etter 8.30.

## Storyen

Som **gruppe** vil vi at målene fra tavla og designreglene for stegkortene og
for styrken for én dag prøves i nettleseren, ikke bare som tekst i stilarket.
Da fanger testene en regel som et annet omfang eller en senere regel
overstyrer.

**Oppfyller:** VG8 og VG4 fra 8.29 · **Begrenses av:** regel 22, AD-8

## Målene og kildene

- **VG8, stegkortene** i «Din egen liste: kom i gang» ved 1280 px (i én rad) og
  390 px (under hverandre), i demoen og den ekte versjonen. Svaret 13.11 kl. 10:32–10:54 i spesifikasjonen for 8.29:
  «stegkortene med 18 px luft (20 px nederst), 14 px hjørner og 14 px mellom».
- **VG4, styrken for én dag** i notatene, i panelet «Mine notater» og i
  «Signalet dag for dag», også en dag i ettertid. Ønsket 13.11 kl. 20:35 i spesifikasjonen for 8.29 og
  designreglene: 3 av 3 er «en pille med fyll i blekk, hvit tekst og en ring
  på 2 px» (§5), og «Sterk oransje `#F2B53A`: ringen rundt «3 av 3»» (§5,
  fargene ved en aksje fra 14.10). 2 av 3 er «den hvite pillen fra originalen (utdraget §6): samme form
  som «3 av 3», hvit, med tekst og kant i blekk og uten ring» (§5, 14.10).
  1 og 0 av 3 er «tekst uten pille».

Testene står i `tests/test_maalene_8_31.py`. Styrken finnes på teksten
(«2 av 3»), ikke på klassen, så en feil klasse fanges også.

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet. Alt er bygget etter forslaget.

1. **Nummeret.** *Forslag:* 8.31, neste ledige i Epic 8 etter 8.30.
2. **Fargen på ringen rundt 3 av 3.** Fargelista i §5 (13.10) har «Gul ring
   `#a67c00`», men linja 14.10 under den i §5 erstatter den: «Sterk oransje
   `#F2B53A`: ringen rundt «3 av 3»». §3 (14.10) og ønsket 13.11 sier det
   samme. *Forslag:* testen bruker `#F2B53A`. Ingen endring i designreglene.
   (Rettet etter gjennomgangen, ECH8: spørsmålet sa først at reglene sprikte.)
3. **Kanten rundt 2 av 3.** Designreglene sier «kant i blekk», uten bredde.
   *Forslag:* testen krever en heltrukken kant i blekk på minst 1 px på alle
   sider, ikke en bestemt bredde.
4. **Ringen som kant eller skygge.** *Forslag:* begge godtas, en kant på 2 px
   eller en skygge uten uskarphet på 2 px, så lenge fargen er `#F2B53A`.
5. **«14 px mellom».** *Forslag:* avstanden måles mellom nabokortene, bortover
   når de står i rad og nedover når de står under hverandre. Ved 1280 px skal
   de tre stå i rad, og ved 390 px under hverandre.
6. **Sidene som måles.** *Forslag:* i demoen september for LKSV (alle fire
   styrkene på dagene i «Signalet dag for dag», også på dager i ettertid, og
   notatene med 0–3 i panelet) og Min liste (notatene med 0–3). I den ekte
   versjonen EQNR med `?alle=1`, så alle notatene er åpne, og Min liste, med
   et notat hver dag (fiksturen fra 8.29), og september for EQNR etter én
   henting 22.09 (dager i ettertid med 2 av 3, fiksturen fra 2.17).
7. **«Samme form» for 2 av 3.** Designreglene sier «samme form som «3 av 3»».
   Målt er 2 av 3 1–2 px lavere enn 3 av 3 på samme sted (20,6 mot 22,6 px i
   «Signalet dag for dag» og 22,6 mot 24,6 px i notatene), fordi kanten er
   1,5 px og ringen 2 px. *Forslag:* «samme form» betyr pilleformen, og testen
   sjekker den, ikke høyden. Ingen endring i appen.

## Resultatet

Alle ni testene består på `04c26cdb`, så appen gjør det spesifikasjonen sier,
og ingenting i appen er endret. Første versjon av testene målte årssummen i
«Signalet dag for dag» som en dag, og tok ikke med panelet, som står i en
`<template>` til knappen trykkes. Det er rettet etter gjennomgangen.

## Flettet 14.11

CI var grønn i alle fire jobbene på head-en `c45cbb7c` (run 43649592034). Triagen
hadde ingen åpne funn på middels eller høy grad. PR #159 ble squash-flettet i
`167640bd` kl. 23:51, låst til `c45cbb7c`, uten nytt ja, slik tillegg 4 sier.
Kveldsjobben sto som Disabled.

## Mutantene

Én mutant per test i `src/static/stil.css`, med kopi før. Fila var lik HEAD
etterpå (`git hash-object` lik `422ea603`, og sha256 lik kopien).

- **M1:** luften nederst i stegkortene 18 px i stedet for 20 px. Fanget av
  `test_stegkortene` i begge versjonene ved 1280 og 390 px.
- **M2:** ringen rundt 3 av 3 i «Signalet dag for dag» i blekk i stedet for
  oransje. Fanget av `test_styrken_for_en_dag` for LKSV i demoen og EQNR i den
  ekte versjonen. Siden etter én henting 22.09 har ingen dag med 3 av 3.

Mutantene ble tatt på nytt etter rettingene i gjennomgangen.

## Gjennomgangen 14.11 (Edge Case Hunter)

Én leser, bare med lesing. 8 funn: 3 middels og 5 lave, alle rettet.

| Funn | Grad | Rettet |
|---|---|---|
| ECH1: årssummen i `.historikk` ble målt som en dag | middels | Bare `.historikk li.dag`. Demoen måles på LKSV, der dagene har alle fire |
| ECH2: ingen styrke krevd på en dag i ettertid, og notatene ble aldri merket | middels | Demoen krever 0–3 på dager i ettertid, den ekte versjonen 2 av 3, og et notat merkes etter `.ettertid-merke` |
| ECH3: panelet «Mine notater» ble aldri målt | middels | Skriptet trykker på knappen og måler i `.notatpanel-innhold`, med 0–3 der |
| ECH4: 1 og 0 av 3 sjekket ikke bilde eller omriss | lav | `background-image` og `outline` er `none` for alle |
| ECH5: 2 av 3 godtok en ring i en annen farge og en tykk kant | lav | Ingen skygge, ikke noe omriss og kanten 1–2 px |
| ECH6: notatene i en lukket `<details>` ble regnet som synlige | lav | `?alle=1` og `checkVisibility()` |
| ECH7: avstanden nedover ble aldri målt | lav | Også 390 px, og kortene i rad ved 1280 px |
| ECH8: spørsmål 2 sa at designreglene sprikte | lav | Spørsmål 2 og kommentarene er rettet |

Ingen funn på middels eller høy står åpne.

## Kontroll

- [x] `uv run pytest tests/test_maalene_8_31.py tests/test_kom_i_gang_8_29.py tests/test_ettertid_2_17.py tests/test_kvalitetssikring.py` består lokalt
- [x] `--dokumentene` består lokalt
- [x] CI er grønn i alle jobbene (run 43649592034)
- [x] `git diff --stat origin/main` viser ingen fil i `src/`
