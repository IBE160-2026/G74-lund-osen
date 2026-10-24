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

*Lagt til 2026-10-24 (gjennomgangen, VG3 og BH6):* sortert er tabellen én liste uten delene, og da står heller ikke setningene fra 8.0c, «Ingen aksjer skilte seg ut» og «N av M aksjer ble vurdert», som står i stedet for «Skilte seg ut». Uten sortering står de som før. `test_sortert_uten_noen_som_skilte_seg_ut_er_en_liste_uten_setningene` holder det slik.

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

*Lagt til 2026-10-24:* kjørt 14:32:22–14:32:31 på `7ca19d9`, i arbeidskopien, mot `tests/test_demoproeven.py`. Hver fil ble kopiert før, og etter mutanten var sha256 lik kopien og `git hash-object` lik `HEAD:<sti>`. Alle ble fanget:

| # | Mutant | Fanget av |
|---|---|---|
| M1 | Ankeret borte fra periodeknappene i `_perioder.html` | `test_periodeknappene_og_velg_dag_gaar_til_kursgrafen` |
| M2 | Radene uten data borte fra `index.html` | `test_aksjen_uten_kurser_har_en_rad_nederst_og_ingen_fotnote` |
| M3 | `href` borte fra symbolet over søyla i `_hovedindeks.html` | `test_symbolene_over_soeylene_lenker_til_aksjesiden[/]` |
| M4 | `grunn_med_tall` gir teksten uten tall | `test_raden_sier_hvorfor_med_samme_tall_som_aksjesiden[/]` |
| M5 | Sorteringen tilbake innenfor hver del i `app.py` | `test_sortert_er_hele_lista_en_liste_uten_delene[synkende]` |

## Gjennomgangen 24.10

Gjennomgang 24.10 etter hele settet (3316 bestått og 17 hoppet over), av endringene i dag for 8.2a: `0b98f42..3a4fb86` på main og `3a4fb86..7ca19d9` på grenen, uten bildene. Linsene var Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 6 funn) og Verification Gap (VG, 5 funn), hver for seg og uten å endre noe i repoet. 26 funn ble 21 rader. Funnene er rettet med en gang (svaret 23.10 kl. 15:53), i `4be99ed` (dokumentene) og `c44e165` (koden og testene).

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | PRD-en sa at en aksje uten kurser navngis under tabellen, og hjelpeteksten viste til den setningen | high | rettet i `4be99ed` og `c44e165`: en datert linje under avsnittet i `prd.md`, og hjelpen viser til den |
| BH2 | `serie()` uten vern kunne gi en feilside for hele oversikten (NFR-03) | medium | rettet i `c44e165`: `_dager_i_serien` med vern, og `test_en_serie_som_ikke_kan_leses_gir_grunnen_uten_tall` |
| BH3, VG1 | Testhjelperne i `test_app.py` legger radene uten data for seg, og klassen docstringen viste til, fantes ikke | medium | rettet i `c44e165`: `TestStory82aRadUtenData` prøver hvor radene står, også sortert |
| BH4 | Båndet talte aksjene uten kurser som «uten signal» | medium | rettet i `c44e165`: «og N uten signal og M uten data» |
| VG2 | Min liste med bare en aksje uten kurser var ikke prøvd | medium | rettet i `c44e165`: `test_min_liste_med_bare_aksjen_uten_kurser_har_tabellen` |
| VG3, BH6 | Sortert uten noen som skilte seg ut var ikke prøvd, og setningene fra 8.0c står da ikke | low | rettet i `c44e165`: testen, og linja under «Valg» |
| ECH1 | N talte hele serien, ikke radene til og med dagen grunnen gjelder | low | rettet i `c44e165` |
| ECH2, BH10 | Ruta i børsometeret brukte standard Parametre, ikke dem oversikten får | nit og low | rettet i `c44e165`: `p` gjennom `bygg_rute` |
| ECH3, BH7 | Raden uten data kunne komme foran en rad med kurs ved lik nøkkel, og hjelpen sa nederst også sortert | low | rettet i `c44e165`: sist blant radene uten verdi, og hjelpen sier «uten sortering». Sortert på Selskap står raden etter navnet |
| ECH4, BH9 | Lenkene over søylene og lista for skjermleseren gir aksjene to ganger, og kommentaren sa at alt er skjult | low | rettet i `c44e165`: kommentaren. Lista står, fordi den har tallene. Fokus: `*:focus-visible` i `stil.css` gjelder også lenkene |
| BH5 | `len(rader) + len(alle_uten_data)` er lik `len(poster)` | low | rettet i `c44e165`: kommentaren sier det, og definisjonen fra 14.10 står |
| BH13 | To konstanter heter `UTEN_DATA`, med ulik stor bokstav | nit | rettet i `c44e165`: `UTEN_DATA_TEKST` i `markedsoversikt.py` |
| BH14 | `deferred-work.md` og `epic-8-context.md` beskrev fotnoten og sorteringen innenfor hver del | nit | rettet i `4be99ed` med daterte linjer |
| VG4 | Andre steg i testen av båndet kunne ikke feile alene | nit | rettet i `c44e165`: MOWI går fra uten data til uten signal |
| VG5 | Navnet i `aria-label` var bare sjekket på slutten | nit | rettet i `c44e165`: lik navnet i tabellen |
| BH8 | KI-bryteren beholder ikke en periode som 1 år | low | uten endring: som før 8.2a, bare `?dag=` er med (8.16b). Ikke i svaret |
| ECH6 | Aksjene uten kurser navngis ikke når ingen aksje har kurser | low | uten endring: da gir `hent_leser` ingen leser, og siden sier at basen er tom |
| BH11 | Eksemplet «32 av 50 dager» under story 8.2 stemmer ikke med demoen | nit | uten endring: eksemplet er gruppens. Demoen sier «30 av 51 dager» |
| BH12 | Kommentaren ved bildet etter d) | nit | avvist: bildet slutter etter «Skilte seg ut», før raden til Varde Systemer |
| BH15 | Raden uten data har «– Ukjent» i Retning | nit | uten endring: valgt som Varde Systemer under «Valg». Gruppen avgjør om det skal være bare «–» |
| ECH5 | Ankeret for KI-teksten finnes ikke når siden ikke har sjekker | nit | uten endring: krever at dataene endres mellom visningen og klikket |

## Det som ikke endres

- Linja om hovedindeksen, «7 av 14 gikk bedre enn indeksen», og «Ikke med, uten kurs».
- Standardrekkefølgen etter FR-102, med delene «Skilte seg ut» og «Øvrige aksjer».
- `src/fetch_prices.py`, basen og migrasjonene. Ingen API-kall utover kvotesjekken i regel 15, `data/db/ose.db` røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
