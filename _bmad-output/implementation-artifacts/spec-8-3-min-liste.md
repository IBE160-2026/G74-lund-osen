---
title: 'Story 8.3: Min liste, med stjerne i oversikten og en egen side'
type: 'feature'
created: '2026-10-19'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7f2c11c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7a-stilen-i-en-css-fil.md'
---

## Intent

**Problem:** briefen v8 lover «Min liste» i v1, og story 8.3 står igjen. I dag har appen bare oversikten og aksjesiden, og ingen måte å følge et utvalg av aksjene på.

**Grunnlaget:** story 8.3 i `epics.md`, gruppens svar 19.10 kl. 10:29 under «Prioritering» og under story 8.3, og instruksjonen 19.10 kl. 20:20. Føringen 2026-09-30 under AD-3 sier at merkingen blir et eget datasett med egen port og webserveren som eneste skriver, og at navnet på porten settes når 8.3 bygges. Regel 22 i `CLAUDE.md` har fått en datert linje om at webserveren fra main skriver merkingen, og grenen bygges derfor i en egen worktree utenfor repo-mappa.

## Kontrollpunktene

- a) Lagringen: migrasjonen `0007` med en egen tabell for merkingen, med bare symbolet og en trigger mot `aksje` som for de andre tabellene (AD-21). En egen port etter navneregelen, i minnet og i `lagring_sqlite.py` (AD-3). Demoen merker fem av selskapene, fra begge delene av tabellen.
- b) Merkingen: en POST som bryteren for KI-teksten (`/ki` i `app.py`), med 403 fra en annen side, bare egne stier tilbake, og 303 til samme side med sorteringen. Webserveren skriver bare den nye tabellen og henter aldri (AD-10).
- c) Sidene: i stripa på alle sidene en knapperad med «Markedsoversikt» og «Min liste», der knappen for siden man står på, er fylt (`aria-current`). Aksjesiden beholder veien tilbake. På hver rad i oversikten og i Min liste står en stjerne i cellen for Selskap, foran navnet, så tabellen har fem kolonner (FR-101): fylt når aksjen er merket, en knapp med `aria-pressed` og selskapets navn, og «★ = Min liste» under «Selskap». `/min-liste` har overskriften «Min liste», en kort tekst om at stjernen legger aksjen i lista uten kall, knappen «Alle / Min liste» med antallet, og samme tabell i samme rekkefølge (FR-102), også med sorteringen fra 8.15. En tom liste sier hvordan man merker. Alt virker på 390 px uten vannrett rulling. Hjelpen, `docs/hjelp.md` og README-en følger med (regel 19). Stilen står i CSS-fila. Bildene tas på nytt slik feilmeldingen i testen sier.
- d) Testene, med «Ville feilet hvis»: merkingen overlever en omstart; filteret endrer ikke rekkefølgen, heller ikke sortert; tabellen for merkingen har ingen kolonne for antall, beløp eller kurs; et ukjent symbol avvises i porten og i basen; en POST fra en annen side og en fremmed adresse tilbake; under en merking skrives bare den nye tabellen; lista som parameter, også med færre enn 15 aksjer; den tomme lista; den fylte knappen på hver side; kontrasten til stjernen. Spinen får daterte linjer under AD-3, AD-10 og AD-16.

## Planen, én commit per punkt

1. a) `src/migrasjoner/0007_min_liste.sql`, porten og de to lagerne, og merkingen i demoen.
2. b) POST-ruten for merkingen i `app.py`.
3. c) Knapperaden, stjernen, `/min-liste`, stilen i `src/static/stil.css`, hjelpen, `docs/hjelp.md`, README-en og bildene.
4. d) De nye testene, de daterte linjene i spinen, og mutantene.

## Avgjort i spesifikasjonen

- **Navnet på porten** (føringen 30.09 under AD-3) er `Minlistelager`, etter navneregelen i spinen: `<Datasett>lager` er porten med skrivesiden. Den har `MinneMinlistelager` i minnet og `SqliteMinlistelager` i `lagring_sqlite.py`.
- **Rekkefølgen:** Min liste filtrerer radene fra oversikten og sorterer dem ikke på nytt, så rekkefølgen er den samme som i oversikten (FR-102), også når en kolonne er sortert (8.15).
- **Den ekte basen** får en tom tabell fra `0007`. Demoen merker fem (svaret kl. 10:29).

## Avgjort underveis

- **Demobasen åpnes for skriving bare av merkingen.** Sidene åpner den som før, bare for lesing og uten migrering. Ruta `POST /min-liste/merk` åpner den for skriving, så stjernen virker i demoen, som er den sensor bruker. Det samme gjelder en demobase som ligger der den ekte skal ligge. Docker monterer `ose-demo` og `ose-db` uten `:ro`, og brukeren `ose` eier `data/` (`compose.yaml`, `Dockerfile`).
- **Min liste viser ikke overskriften med tall, kortet «Slik leser du tabellen» eller hovedindeksen.** Siden har sin egen overskrift og tekst, og tabellen er den samme som i oversikten (FR-102).
- **«Alle / Min liste»** er to lenker, `/min-liste?vis=alle` og `/min-liste`, som beholder sorteringen. Valget har `aria-current="true"`, fordi knappen i stripa alt sier hvilken side man står på.
- **Antallet:** «Alle» er alle aksjene i lista, også de uten kurser, som «N av M» i oversikten (beslutningen 14.10). «Min liste» teller de merkede som har en rad i tabellen.
- **En POST uten Origin godtas**, som bryteren for KI-teksten. Nettlesere sender Origin på en POST fra en annen side.
- **Ankeret:** merkingen sender tilbake til `#rad-<symbol>`, id-en på skjemaet i raden, så siden ikke hopper til toppen. Bare symboler porten har godtatt, kommer i ankeret.
- **En merket aksje som er tatt ut av `aksje`,** vises ikke, men raden kan fjernes gjennom porten.
- **390 px** er målt i Edge uten vindu, med hver side i en iframe på 390 px: `scrollWidth` er 390 på `/`, `/min-liste`, `/min-liste?vis=alle` og `/aksje/KVST`. Tabellen ruller i sin egen boks, som før (avvik 8). Edge uten vindu går ikke under 504 px, så målingen kan ikke tas med vinduet alene.
- **Bildene** ble tatt på nytt, med høydene målt: oversikten 1630 px (var 1573) og aksjesiden 1872 px (var 1816), fordi knapperaden ligger i stripa. Navnet `test_fila_finnes_og_er_1280_px_bred_og_1573_px_hoey` står, fordi `docs/kvalitetssikring.md` viser til det.

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter hver:

- Merkingen bare i minnet.
- Min liste i annen rekkefølge enn oversikten.
- POST uten Origin-sjekken.

Kjørt én om gangen med `-x` på `tests/test_min_liste.py`, i en fersk klon av `b01871f` med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etterpå. Hver ble fanget av hele fila og av testen den er laget for, alene:

- M1, merkingen bare i minnet (et sett i prosessen i `SqliteMinlistelager`): `test_merkingen_overlever_en_omstart`.
- M2, Min liste i annen rekkefølge enn oversikten (sortert på navnet): `test_filteret_endrer_ikke_rekkefoelgen`.
- M3, POST uten Origin-sjekken: `test_en_post_fra_en_annen_side_gir_403`.
- N1, «Alle» uten setningen om at ingen skilte seg ut: `test_alle_er_samme_tabell_ogsaa_naar_ingen_skilte_seg_ut`.
- N2, «Øvrige aksjer» uten overskrift i Min liste: `test_oevrige_har_overskriften_naar_bare_de_er_merket`.
- N3, antallet teller også merkede uten rad: `test_antallet_teller_bare_merkede_med_en_rad`.

Første runde, på `203be21`, fanget alle tre i hele fila, men M1 og M2 ikke alene. Testen for omstarten leste gjennom porten, og de fem i demoen står i alfabetisk rekkefølge i hver del. Testene ble gjort sterkere i `9b3f7fa`, og runden ble tatt på nytt.

## Gjennomgangen

Gjennomgang 19.10 på diffen `main...9b3f7fa`. Linsene var Blind Hunter (BH, 20 funn, bare diffen), Edge Case Hunter (ECH, 13 funn, om lag 140 prøver i en klon, som var ren etterpå) og Verification Gap (VG, 14 hull, mot instruksjonen, story 8.3, spesifikasjonen og spinen). Rettingene står i `b01871f`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH7, ECH1 | «Alle» i Min liste mistet setningen om at ingen skilte seg ut | medium | rettet, testen `test_alle_er_samme_tabell_ogsaa_naar_ingen_skilte_seg_ut` |
| BH8, ECH2 | Antallet talte en merket aksje uten rad, og en tom side uten forklaring | medium | rettet: antallet er de merkede med en rad, og den tomme teksten står når ingen rad vises |
| BH4, VG1, VG4, ECH6 | Min liste var ikke med i sidene rammetestene går over, og lenkene og skjemaet der var ikke testet | medium | rettet: to sider til i `sidene`, og `test_lenkene_og_skjemaet_i_min_liste_beholder_valgene` |
| BH5 | Siden hoppet til toppen etter en merking | medium | rettet: ankeret `#rad-<symbol>` |
| VG2 | 390 px uten vannrett rulling var ikke prøvd | medium | rettet: målt i iframe (se «Avgjort underveis»), og en test for at knapperaden brytes |
| VG3 | Triggeren skjulte en manglende sjekk i porten, og ingen side var prøvd med færre enn 15 | medium | rettet: `test_porten_avviser_selv_uten_triggeren` og `test_sidene_med_faerre_enn_15_aksjer` |
| BH1 | En demobase på versjon 6 gir 500 | medium–høy | avvist: `RuntimeError` er i `BASEFEIL`, og sidene gir 503 med feiltypen, som før 8.3 (prøvd av ECH8). En linje i `docs/hjelp.md` sier hvordan demobasen lages på nytt |
| BH2, ECH9 | En låst base gir 503 etter 5 s | medium | avvist: samme som for sidene før 8.3. Hentingen skriver en serie per transaksjon (`erstatt_serie`), så låsen er kort |
| BH3 | Volumene kunne vært skrivebeskyttet i Docker | medium | avvist: `compose.yaml` monterer dem uten `:ro`, og brukeren `ose` eier `data/` |
| ECH3, BH16 | En rad for en aksje som er tatt ut av `aksje`, kunne ikke fjernes | low | rettet, `test_en_rad_for_en_aksje_som_er_tatt_ut_kan_fjernes` |
| ECH4 | Ingen test for merkingen når demobasen mangler | low | rettet, `test_merkingen_naar_demobasen_mangler_gir_404` |
| ECH5 | Overskriften «Øvrige aksjer» når bare de er merket, var ikke testet | low | rettet, mutanten N2 |
| ECH7, BH9, BH20 | Fotnotene og teksten om stjernen sto også uten tabell | low | rettet, `test_fotnotene_i_min_liste_gjelder_bare_lista` |
| BH10 | To lenker med `aria-current="page"` | low | rettet: valget har `aria-current="true"` |
| BH12, VG10 | Testen for omstarten av webserveren så ikke på siden | low | rettet: den fylte stjernen etter omstarten |
| VG5 | «Fylt» var bare prøvd som attributt | low | rettet: regelen i `stil.css` er testet |
| VG6 | `docs/hjelp.md` sa at webserveren bare leser fra basen | low | rettet: en datert linje |
| VG7 | Fire tester manglet «Ville feilet hvis» | low | rettet |
| VG8 | Ingen vakt mot en ny skriver av `min_liste` | low | rettet, `test_bare_webserveren_og_demoen_skriver_min_liste` |
| VG9 | Den ekte basen var ikke prøvd for at bare `min_liste` skrives | low | rettet, `test_i_den_ekte_basen_skriver_merkingen_bare_min_liste` |
| VG11 | Spesifikasjonen manglet valgene, mutantene og triagen | low | rettet: denne delen og «Avgjort underveis» |
| ECH8 | En demobase fra før 8.3 gir feilsiden med `RuntimeError` | low | rettet med linja i `docs/hjelp.md`. I Docker lages demobasen på nytt ved hver start |
| BH6, ECH10 | Vernet mot en annen side hviler på Origin, og DNS-rebinding er ikke stoppet | low | avvist: samme vern som bryteren for KI-teksten, appen lytter på 127.0.0.1, og det verste er en byttet stjerne |
| BH11 | Ingen fokusregel for knappene i stripa | low | avvist: `header.stripe *:focus-visible` gir den oransje ringen, som testen for fokus ser |
| BH13 | Testen for at sidene ikke skriver, ser ikke en WAL-fil | low | avvist: basen bruker ikke WAL, og testen for den ekte basen sammenligner tabellene |
| BH14, VG12 | Testen for at ruta ikke henter, er et tekstsøk | low | avvist: nettet er sperret i hele testkjøringen (AD-8) |
| BH15 | Kontrasten bare mot kortet og bakgrunnen | low | avvist: alle radene i tabellen har kortet som bakgrunn |
| BH17 | Docstringen sa at lista «aldri har 15» | nit | rettet |
| BH18 | Testnavnet sier 1573 | nit | avvist: navnet står, se «Avgjort underveis» |
| BH19 | «★ = Min liste» leses i hver celle av skjermleseren | nit | avvist: kort tekst, og den forklarer stjernen |
| ECH11, ECH12 | Over 100 tegn eller `#` i `tilbake` gir `/`, og `rstrip` godtar `//` i Origin | nit | avvist: malen lager høyst 49 tegn, og det er ufarlig |
| ECH13 | 404-sidene har ingen knapperad | nit | avvist: Flasks egen side, som før 8.3 |
| VG13, VG14 | Ingen hjelpetekst for knapperaden, og «Alle 15» teller aksjen uten kurser | nit | avvist: knappene sier det selv, og antallet følger «N av M» (se «Avgjort underveis») |

Ingen funn med dom medium eller høyere står urettet. BH1, BH2 og BH3 er avvist etter oppslag, med grunnen i tabellen.
