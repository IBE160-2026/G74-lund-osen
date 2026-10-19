---
title: 'Story 2.7 (2.7a): all stilen i én CSS-fil'
type: 'refactor'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a281bfd'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3f-bildene-av-appen-bak-en-knapp.md'
---

## Intent

**Problem:** stilen står i `<style>` i `_ramme.html`, i blokka `stil` i `index.html`, `aksje.html` og `basefeil.html`, og i tre makroer i delmalene (`hjelpestil`, `brikkestil` og `periodestil`). Seks regler står likt i `index.html` og `aksje.html`: `h1.overskrift mark`, `.opp`, `.ned`, `.blandet`, `.ingen, .ukjent` og `p.fotnote`. Tre har samme velger og ulik kropp: `h1.overskrift`, `p.meta` og `.mangler`. Kontrollpunktet i story 2.7 sier at malene deler én layout og én CSS-fil.

**Grunnlaget:** gruppens svar 19.10 kl. 12:06 og instruksjonen 19.10 kl. 13:24. Stilen flyttes nå, som første del av 2.7, før 8.3 og historikken (2.7b). Sidene skal se nøyaktig ut som før.

## Kontrollpunktene

- a) Før noe endres: skjermbilder med fremgangsmåten for bildene, fra en demobase i en midlertidig mappe, av oversikten og aksjesiden i 1280 og 390 px, oversikten sortert, siden for en valgt dag, en dag uten vurdering, et åpent hjelpevindu og feilsiden. De legges i scratchpaden, ikke i repoet.
- b) Fila: én CSS-fil under `src/static/`, lenket fra `_ramme.html` med et avtrykk av fila i adressen, så nettleseren aldri bruker en gammel utgave. All stilen fra rammen, sidene og delmalene flyttes dit, og makroene som bare gir stil, tas bort. De seks like reglene står én gang. Regler med samme velger og ulik kropp avgrenses til siden sin. Ingen mal har `<style>`. Testene som leser stilen fra siden, leser fila, med de samme kravene som før. Fila er med i avtrykkene bak bildene. `designregler.md` og spinen får en datert linje om hvor stilen står.
- c) Kontrollen: de samme skjermbildene fra grenen er like piksel for piksel som i a, og bildene i `docs/appen/` tas på nytt og er like byte for byte. Er noe ulikt, rettes stilen, ikke bildet. Tester med «Ville feilet hvis»: ingen `<style>` i malene, fila svarer 200 fra lenken på hver side, ingen velger står to ganger med samme kropp, og fargene står bare i `:root`. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: en `<style>` tilbake i en mal, en regel lagt inn to ganger, og lenken til fila tatt bort.

## Planen, én commit per punkt

1. a) Skjermbildene fra main, før noe endres, i scratchpaden. Ingen commit.
2. b) `src/static/stil.css` med rammen, delmalene, de seks felles reglene og hver side for seg. `_ramme.html` lenker til `/static/stil.css?v=<avtrykk>`, der avtrykket er de første 16 tegnene av sha256 av fila, regnet i `app.py`. `<body>` får klassen til siden. Blokka `stil` og makroene `hjelpestil`, `brikkestil` og `periodestil` tas bort. Hjelperen `_stil` i `tests/test_app.py` leser fila fra lenken og gir reglene som gjelder siden, så testene som leste `<style>`, stiller de samme kravene.
3. c) Skjermbildene fra grenen, bildene i `docs/appen/` på nytt, testene og mutantene.

## Avgjort i spesifikasjonen

- **Navnet på fila** er `src/static/stil.css`, ved siden av skriftene.
- **Avtrykket** er de første 16 tegnene av sha256 av fila, i parameteren `v`. Det regnes ved hver side fra fila som serveres, så en endret fil gir ny adresse uten omstart.
- **Avgrensningen:** hver side har en klasse på `<body>`: `side-oversikt`, `side-aksje` og `side-feil`. Alle reglene som bare sto i én side, avgrenses med `:where(.side-…)`, ikke bare de tre med ulik kropp. Grunnen: en regel fra én side som treffer noe på den andre, endrer den siden, som `figure` og `h2` fra aksjesiden, `table` og `.skjult` fra oversikten. `:where()` gir ingen ekstra spesifisitet, så rekkefølgen og vektene mellom reglene er de samme som før.
- **Rekkefølgen i fila:** skriftene, fargene, rammen, hjelpen, brikkene, periodevalget, de felles reglene, oversikten, aksjesiden og feilsiden. Det er rekkefølgen fra `<style>` i rammen, med blokka `stil` til slutt.
- **Skjermbildene på 390 px:** Edge uten vindu går ikke smalere enn 504 px (målt: `innerWidth` 504 med `--window-size=390,900`). Siden vises derfor i en iframe som er 390 px bred, og skriptet sjekker at `innerWidth` i den er 390.

## Avgjort underveis

- **Rekkefølgen i fila** (gjennomgangen, BH1, BH2 og BH11): setningen over om at rekkefølgen er den fra `<style>` i rammen, stemmer innenfor hver side, men ikke for periodevalget og de seks felles reglene. Periodevalget sto før midt i blokka `stil` i `aksje.html`, og de felles reglene sto midt i `index.html` og nær slutten av `aksje.html`. Nå står begge foran reglene for sidene. Én plass kan ikke gi begge sidene den gamle rekkefølgen. Derfor er den beregnede stilen (`getComputedStyle`) for hvert element sammenlignet med main, i 1280 og 504 px, i lukkede hjelpevinduer også. Sidene var oversikten, alle ti sorteringene, aksjesiden for hver av demoaksjene med kurs (MTFJ har ingen og svarer 404), de seks andre periodene, en valgt dag, en dag uten vurdering og feilsiden: 68 filer og 26 572 elementer, og ingen var ulike. Edge lister de egendefinerte egenskapene i ulik rekkefølge, så deklarasjonene ble sortert før sammenligningen. Kommentaren øverst i fila sier dette.
- **Reglene per side** ble også sammenlignet tekstlig: reglene fra `<style>` på `a281bfd`, med makroene satt inn, mot fila filtrert per side. Aksjesiden har de samme 137 reglene. Oversikten og feilsiden har i tillegg periodevalget og de felles reglene, som ikke treffer noe element der. Ingen regel er borte.
- **Kan fila ikke leses** (gjennomgangen, BH3 og ECH1), står lenken uten avtrykk, så sidene og feilsiden vises i stedet for 500.

## Kontrollen

**a)** Kl. 13:37 fra main (`a281bfd`), før noe var endret, med `skjermbilder_27a.py` i scratchpaden: demobasen i en midlertidig mappe, `OSE_DEMO=1`, waitress på en ledig port og Edge uten vindu, med høyden målt til hele siden. Tretten bilder:
- oversikten i 1280 og 390;
- aksjesiden for KVST i 1280 og 390;
- oversikten sortert på endring i 1280 og på selskap i 390;
- en valgt dag (01.10) i 1280 og 390;
- en dag uten vurdering (lørdag 03.10) i 1280;
- et åpent hjelpevindu på oversikten i 1280 og på aksjesiden i 390;
- feilsiden i 1280 og 390, med en base som ikke er en base.

Det første forsøket på 390 px ga 504 px, fordi Edge uten vindu ikke går smalere. Bildene ble tatt på nytt med en iframe på 390 px (se «Avgjort i spesifikasjonen»).

**c)** Kl. 13:58–14:01 ble de samme tretten bildene tatt to ganger fra en fersk klon av main og to ganger fra en fersk klon av grenen (`8e69e53`), begge med `core.autocrlf=false`. Tolv av tretten var like byte for byte i alle fem kjøringene, og dermed piksel for piksel. Hjelpevinduet på oversikten kom i to utgaver, `54e45acf…` og `191ebbbd…`, og begge kom også i de to kjøringene fra main. Ulikheten ligger bare i vinduet (x 357–922, y 972–1420) og kommer fra Edge, ikke fra stilen. Bildene i `docs/appen/` ble tatt tre ganger fra hver klon og to ganger etter rettingene (kl. 14:10), med skriptene fra 3.3e og 3.3f, og var like byte for byte med bildene i repoet i alle kjøringene (`57e53e54…` og `68c65a5f…`). Ett forsøk på arbeidskopien før committen i b tok bildet av aksjesiden før skriftene var lastet; de tre neste var like. Bare avtrykkene er nye, i `0742c11` og `9e74fc8`.

## Mutantene

Én om gangen med `-x` på `tests/test_utseende.py`, i en fersk klon av `9e74fc8` med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. Hver ble også kjørt mot testen den er laget for, og den feilet. M1–M3 er fra instruksjonen, N1–N3 for rettingene:
- M1, en `<style>` tilbake i `_ramme.html`: `test_ingen_style_i_malene`.
- M2, `.blandet` lagt inn to ganger: `test_ingen_velger_staar_to_ganger_med_samme_kropp`.
- M3, lenken til fila tatt bort: først `TestRammen::test_kontrasten_regnet_fra_fargene_i_stilen` (`_stil` finner ingen lenke), og for seg `test_fila_svarer_200_fra_lenken_paa_hver_side`.
- N1 (BH3, ECH1), uten reserven når fila ikke kan leses: `test_siden_vises_ogsaa_naar_fila_ikke_kan_leses`.
- N2 (VG1), `.opp` også avgrenset til aksjesiden: først `test_ingen_velger_staar_to_ganger_med_samme_kropp`, og for seg `test_de_seks_felles_reglene_staar_en_gang_for_alle_sidene`.
- N3 (VG2), `h1.overskrift` på aksjesiden uten avgrensningen: `test_velgere_med_ulik_kropp_er_avgrenset_til_hver_sin_side`.

## Gjennomgangen

Gjennomgang 19.10 på diffen `a281bfd..8e69e53`. Linsene var Blind Hunter (BH, 11 funn, bare diffen), Edge Case Hunter (ECH, 8, prøvd i en klon) og Verification Gap (VG, 9). Ingen av dem kjørte hele testsettet, en server eller et nettkall. Rettingene står i `9e74fc8` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | De felles reglene står foran sidenes regler, så like vekter kan avgjøres annerledes | medium–høy | patch: kommentaren i fila sier det, og den beregnede stilen for 26 572 elementer er lik main (over) |
| BH2 | Periodevalget er felles og står tidligere enn før | medium | patch: som BH1. Delmalen gjelder alle sidene og skal brukes i oversikten i 8.17 |
| BH3, ECH1 | Mangler fila, gir hver side 500, også feilsiden | medium | patch: lenken uten avtrykk, og en test. N1 |
| VG1, BH8 | De seks felles kunne stå avgrenset i hver side, og en kopi med annet semikolon slapp gjennom | medium | patch: duplikattesten ser bort fra avgrensningen og det siste semikolonet, og en egen test for de seks. N2 |
| VG2, BH6, ECH5 | Ingen test for at velgere med ulik kropp er avgrenset, og en blandet velgerliste ville forsvunnet i `_stil` | medium | patch: test for at de er avgrenset til hver sin side, og at hele velgerlista er avgrenset. N3 |
| BH5 | En ny side uten blokka `side` mister sine regler | low–medium | patch: test for hver mal som bygger på rammen |
| VG3, BH7, ECH4 | Fargetesten slapp fire og åtte tegn og fargenavn | low–medium | patch |
| VG4 | Spesifikasjonen hadde ikke plass for kontrollen, mutantene og triagen | low | patch: her |
| VG5 | Kommentaren i `test_docker.py` sier byte for byte uten at det står noe sted | low | patch: «Kontrollen» over |
| VG6, BH11 | Gammel ordlyd om `<style>`, en lang linje og setningen om rekkefølgen | low | patch: kommentarene, og «Avgjort underveis». `re.sub` for `<style>` i testene står som en sikring |
| BH4, ECH2 | `?v=` styrer ikke bufringen, fordi Flask sender `no-cache`, og adressen er skrevet uten `url_for` | low | avvist: avtrykket er det instruksjonen ber om, og gir ny adresse når fila endres, også bak en mellomlagring. Appen kjører ikke under et prefiks |
| ECH3 | CRLF og LF gir ulikt avtrykk | low | ingen endring: avtrykket regnes av fila som serveres, og avtrykkene bak bildene bruker LF |
| BH9 | Parserne i testene er skjøre | low | avvist: de feiler med en melding, og fila har ingen klammer i strenger |
| BH10 | `test_hjelpetekster.py` importerer fra `test_app.py` | low | avvist: samme mønster som `test_utseende.py` |
| ECH6 | `style`-attributter med tall fra dataene | low | avvist: instruksjonen lar dem stå |
| ECH7 | Kommentaren om tabellen på aksjesiden i hjelpestilen | low | avvist: fra 8.0d, flyttet uendret |
| ECH8 | Werkzeugs 404 og 405 har ingen stil | low | avvist: som før 2.7a |
| VG7, VG8 | Regel 19 og 21 | – | ingen endring: README-en nevner ikke malene eller `src/static/` |
| VG9 | Sjekken for `stil()` er bred | low | avvist: `<style` er sjekken som teller |

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildene tas fra en demobase i en midlertidig mappe.
- Sidene skal se nøyaktig ut som før.

*Lagt til 2026-10-19 kl. 14:28:* PR #76 er squash-flettet i `dc521ff`, låst til head-en `625d044`. Main hadde ikke gått videre. CI var grønn på head-en (39251984445), med pytest og docker, også demoen i compose. Triagen står over og som kommentar på PR-en.
