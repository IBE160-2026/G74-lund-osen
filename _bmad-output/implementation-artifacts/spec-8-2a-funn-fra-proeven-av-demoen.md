---
title: 'Story 8.2 (8.2a): seks funn fra prøven av demoen 24.10'
type: 'bugfix'
created: '2026-10-24'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3a4fb86'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

## Intent

**Problem:** gruppens prøve av demoen 24.10 fant seks ting på oversikten, Min liste, børsometeret og aksjesiden. Knapper på aksjesiden sender til toppen av siden, en aksje uten kurser står bare i en fotnote, symbolene over søylene lenker ikke, raden sier ikke hvorfor signalet ikke kunne regnes, sorteringen holder delene, og linja om 3 av 3 begynner med «Bare».

**Grunnlaget:** gruppens svar 24.10 kl. 11:21–11:49, ført under story 8.2 («Avgjort 2026-10-24 kl. 11:49») og story 8.15 («Avgjort 2026-10-24 kl. 11:39») i `epics.md` i `3a4fb86`, og U20, U23, U35, U36 og U71–U74 i `docs/ux-logg.md`. Teksten under er fra instruksjonen 24.10 kl. 13:42 i dagsfila.

## Slik er det i dag (slått opp 24.10 på `3a4fb86`)

- **Aksjesiden:** periodeknappene og «Velg dag» i `_perioder.html` lenker til `/aksje/<symbol>?periode=…` uten anker, og `ki_bryter` i `src/app.py` sender 303 til `tilbake` uten anker. Pilene i historikken har alt ankeret `#signalet-dag-for-dag` (`ANKER` i `src/historikk.py`).
- **En aksje uten kurser** faller ut av `bygg_oversikt` og står i fotnoten «Uten data i denne kilden» under tabellen (`uten_kurser`, `mangler` i `index.html`). I demoen er det Matfjord Merkevarer (`UTEN_KURSER = "MTFJ"` i `src/demo.py`). Overskriften sier «7 av 15 aksjer», og tabellen har 14 rader.
- **Søylene** under hovedindeksen står i `_hovedindeks.html`, som oversikten og børsometeret bruker. Symbolene står i `<div aria-hidden="true">`, uten lenke.
- **Grunnen:** en rad uten vurdering viser «–» og teksten fra `GRUNNTEKST` i `src/markedsoversikt.py`, for Varde Systemer «signalet kunne ikke regnes». Ruta i børsometeret viser samme tekst. Aksjesiden sier «Trenger 51 dager for å regne signal, fikk 30» (`for_kort_serie`, `noedvendige_dager` og `antall_dager` i `src/aksjedetalj.py`).
- **Sorteringen:** `_tabellsiden` sorterer hver del for seg etter `del_i_to` (tillegget 13.10), og linja over tabellen slutter med «innenfor hver del».
- **Linja om 3 av 3** i `index.html` sier «Bare … fikk utslag på alle 3 sjekkene.»

## Kontrollpunktene

- a) Periodeknappene og «Velg dag» på aksjesiden går til ankeret `#kursgrafen` ved overskriften over kursgrafen, og KI-bryteren til `#ki-teksten` ved KI-teksten (U35, U36, kl. 11:21).
- b) En aksje uten kurser har en rad nederst, som Varde Systemer: navnet som lenke, «–» i hver kolonne og «uten data». Fotnoten «Uten data i denne kilden» er borte. Tallet i overskriften og linja under er antallet rader, så «7 av 15» stemmer og følger lista (U23, kl. 11:34 og 11:35).
- c) Symbolene over søylene lenker til aksjesiden, på oversikten og i børsometeret (U20, kl. 11:23).
- d) Der signalet ikke kunne regnes fordi kursserien er for kort, sier raden og ruta i børsometeret «for kort historikk: N av M dager», med samme N og M som aksjesiden (kl. 11:29).
- e) Velges en kolonne, sorteres hele lista som én liste, uten delene. Rader uten tall i kolonnen står sist, og de som skilte seg ut, beholder kanten. Uten sortering er delene som før. Linja over tabellen og designreglene §5 følger med. Gjelder oversikten og Min liste (kl. 11:39).
- f) Setningen om dem med 3 av 3 begynner ikke med «Bare» (kl. 11:49, NFR-06).

Hvert punkt har tester med «Ville feilet hvis», uten nett. Hjelpetekstene og `docs/hjelp.md` følger med (regel 19), og bildene i `docs/appen/` og avtrykkene i `tests/test_docker.py` tas på nytt når malene bak dem endres.

## Valg som er gjort her

- **«Som Varde Systemer»** leses som at raden har samme form som raden til Varde Systemer: stjernen og navnet som lenke, symbolet og bransjen under, og «– Ukjent» i Retning. Sluttkurs og Endring har «–», og Signalstyrke «–» med «uten data» under.
- **Raden uten data** er en egen type, `RadUtenData` i `src/markedsoversikt.py`, med de samme feltene som malen og sorteringen leser. Den har ingen dato og ingen tid, så den er ikke med i `rader`, som datoen og tidspunktet på siden regnes av.
- **Grunnen med tall** står bare når grunnen er «signalet kunne ikke regnes» og serien er kortere enn signalet trenger, som `for_kort_serie` på aksjesiden. Andre grunner står som før.

## Planen, én commit per punkt

1. Spesifikasjonen.
2. a) Ankerne.
3. b) Raden uten data.
4. c) Lenkene fra søylene.
5. d) Grunnen med tall.
6. e) Én liste når man sorterer.
7. f) «Bare» tas bort.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: ankeret borte (a), raden uten data borte (b), lenken borte (c), grunnen borte (d) og sorteringen tilbake innenfor hver del (e).

## Det som ikke endres

- Linja om hovedindeksen, «7 av 14 gikk bedre enn indeksen», og «Ikke med, uten kurs».
- Standardrekkefølgen etter FR-102, med delene «Skilte seg ut» og «Øvrige aksjer».
- `src/fetch_prices.py`, basen og migrasjonene. Ingen API-kall utover kvotesjekken i regel 15, `data/db/ose.db` røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
