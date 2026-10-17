---
title: 'Story 2.9b: søylene under hovedindeksen'
type: 'feature'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e0519b5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/src/hovedindeks.py'
  - '{project-root}/src/templates/index.html'
---

## Intent

**Problem:** delen om hovedindeksen på forsiden (story 2.9) viser verdien, endringen og «x av N gikk bedre», men ikke hvilke aksjer som trakk opp og ned. FR-105 og story 2.9b i `epics.md` ber om én søyle per aksje med dagens endring under indeksen.

**Grunnlaget:** instruksjonen 17.10 kl. 23:13, steg 4, kontrollpunktene under story 2.9b og svaret 16.10 kl. 18:04: søylene viser bare dagens tall. Periodene og «Velg dag» kommer med 8.17.

## Planen, én commit per punkt

1. Denne spesifikasjonen.
2. `src/hovedindeks.py`: `Soeyle` og `bygg_soeyler`. Én søyle per aksje i lista med kurs for indeksens dato og en rad før, sortert fra størst fall til størst stigning. Høyden og plassen til indekslinja regnes her, ikke i malen. `Hovedindeksvisning` får søylene, og `app.py` gir hvilke aksjer som har 3 av 3.
3. `src/templates/index.html`: søylene under «x av N», med bransjesymbolet over tickeren, den stiplede linja for indeksen, en tekst for skjermleser med alle tallene, og teksten bak «?» i vinduet for hovedindeksen.
4. `designregler.md`: fargegrensene og gult ved 3 av 3 for søylene.
5. Testene for demoen: søylene mot DEMIX.

## Avgjort i spesifikasjonen

- **Hvilke aksjer.** En aksje får søyle når den har kurs for indeksens dato og en rad før den, så endringen fra FR-101 kan regnes (`aksjeendring`, som «x av N» bruker). En aksje uten kurs for dagen står allerede under «Ikke med». En aksje med kurs, men uten rad før, får ingen søyle og navngis under søylene. Antallet telles, aldri et fast 15 (føringen 30.09 under AD-21).
- **Rekkefølgen.** Fra størst fall til venstre til størst stigning til høyre, på endringen uavrundet. Er to like, står de i rekkefølgen fra lista.
- **Fargegrensene.** De følger endringen slik den vises, med to desimaler (`tallformat.avrundet`), som tabellen og endringen ved indeksen (story 2.9):
  - over 0,00 % gir Positiv `#13703C` (6,16:1 mot hvitt);
  - under 0,00 % gir Negativ `#B42318` (6,57:1);
  - 0,00 % gir Ingen `#5F646C` (5,96:1).

  Det samme gjelder søylene og den stiplede linja. Ingen andre grenser: lengden på søylen viser hvor stor endringen er.
- **Skalaen.** Null står midt i feltet. Den største endringen, av søylene og indeksen, fyller halve høyden. Er alle 0, er skalaen 1 %.
  *Lagt til 2026-10-17 (gjennomgangen, BH7 og ECH6):* høyden, retningen og linja regnes på endringen slik den vises, med to desimaler. En søyle som viser 0,00 %, har da ingen lengde, og tallet, fargen og søylen sier det samme.
- **Gult ved 3 av 3.** Bransjesymbolet tegnes i `#a67c00` (3,82:1 mot hvitt), som var «Gul ring» i designregler §5. Sterk oransje `#F2B53A` har 1,83:1 mot det hvite kortet, under 3:1 for grafikk som bærer mening (WCAG 1.4.11). «3 av 3» står også i teksten for skjermleser.
- **390 px.** Søylene deler bredden likt (`flex: 1 1 0`, `min-width: 0`), og tickeren står loddrett. Da får 15 søyler plass uten fast bredde, og siden ruller ikke sideveis.
- **Linja.** Den stiplede linja tegnes bare når indeksen har en endring. Uten den står søylene alene, og teksten sier at linja mangler.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Ingen ny tabell og ingen nye kall: endringen er den i FR-101, og bransjen står i `AKSJEUNIVERS`.

*Lagt til 2026-10-18 kl. 00:16:* PR #63 er squash-flettet i `73098ed`, låst til head-en `dbb6fe6`. CI var grønn på head-en (39074089927) og på main (39074214167). Triagen står som kommentar i PR #63.

## Mutantene

Én om gangen med `-x`, i den ferske klonen med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver. S1–S3 er de instruksjonen ber om, og ble fanget både på `c591570`, før gjennomgangen, og på `800c717`. S4–S6 er for rettingene, og ble fanget på `800c717`:
- S1, et fast antall 15 i teksten for skjermleser (`{{ sy.soeyler|length }}` byttet med `15`): `test_en_soeyle_per_aksje_med_kurs_fra_stoerst_fall`.
- S2, feil rekkefølge (`reverse=True` i sorteringen): `test_antallet_telles_med_en_kortere_liste`, og `test_fra_stoerst_fall_til_stoerst_stigning` etter den.
- S3, feil farge på linja (alltid `opp`): `test_den_stiplede_linja_er_groenn_naar_indeksen_steg_og_roed_naar_den_falt[990.0-ned--1,00 %]`.
- S4, figuren bare med søyler (BH3): `test_ingen_aksje_med_rad_foer_dagen_navngis_uten_soeyler`.
- S5, teksten om søylene alltid bak «?» (VG5): `test_ingen_aksje_med_rad_foer_dagen_navngis_uten_soeyler`.
- S6, høyden på endringen uavrundet (BH7): `test_hoeyden_er_paa_endringen_slik_den_vises`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `e0519b5..c591570`, med Blind Hunter (BH, 17 funn), Edge Case Hunter (ECH, 10) og Verification Gap (VG, 8). Verification Gap regnet kontrastene og regnestykket for 390 px på nytt, og fant dem riktige. Den sjekket også at demoen viser 14 søyler mot DEMIX og at kildene for teksten bak «?» står ordrett. Rettingene står i `54b0a52` og `800c717`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH3, VG6 | Manglet alle med kurs raden før dagen, falt hele figuren bort, og de ble ikke navngitt | medium | patch: figuren står uten søyler, med linja om dem. S4 |
| BH4 | Med flere enn 19 aksjer får ikke symbolene på 14 px plass ved 390 px | medium | patch: `max-width: 100%` på symbolet, og testen krever det |
| BH7, ECH6 | En søyle som viste 0,00 %, hadde lengde og retning fra tallet uavrundet | low | patch: høyden, retningen og linja på endringen slik den vises. S6 |
| BH13, VG5 | Vilkåret for søylene sto to steder i malen, og grenen uten søyler bak «?» var ikke prøvd | low | patch: `har_soeyler`, og en test uten søyler. S5 |
| BH9 | Overskriften og indeksen sto i lista for skjermleser | low | patch: lista har én linje per aksje |
| BH2 | «3 av 3» i teksten for skjermleser var ikke prøvd | low | patch: testen i demoen |
| BH5, ECH9, VG4 | Regnestykket for 390 px brukte faste tall | low | patch: tallene leses fra stilen |
| BH6 | En påstand i testen for demoen var alltid sann | low | patch: tatt ut |
| BH8, ECH7 | Teksten bak «?» sa ikke noe om grått ved 0,00 % eller om at linja kan mangle | low | patch, innenfor tre setninger |
| BH11, ECH4 | Linja ved kanten av feltet sto 2 px utenfor | low | patch: `margin-top: -1px` |
| BH14 | `tre_av_tre` hadde en standardverdi | low | patch: uten |
| BH17 | Testene fra 2.9 ble avgrenset til delen over søylene | low | patch: en påstand om at ingenting står etter figuren |
| ECH5 | En aksje uten bransje ga «(SYM, )» for skjermleser | low | patch: bransjen bare når den finnes. Alle i `AKSJEUNIVERS` og demoen har bransje, så ingen egen test |
| ECH8 | Overskriften sa «Dagens» når indeksen sto på en annen dag | low | patch: datoen i overskriften |
| VG1 | Testene viste til mutantene i spesifikasjonen, som ikke var skrevet ennå | low | patch: denne delen |
| VG2, VG3 | Fargen på det gule symbolet og på søylene var ikke prøvd | low | patch |
| VG7 | Designreglene viste til §3 for fargen, som står i §5 | low | patch |
| BH1, ECH1, ECH10 | Gult kommer fra aksjens siste børsdag, også når søylene er for en annen dag | low | avvist: designregler §3 sier at gult står ved 3 av 3 på siste børsdag, også når siden viser en annen dag. Teksten bak «?» sier det samme |
| ECH2, ECH3, BH16 | En kurs på 0, NaN eller uendelig ville gitt deling på null eller `nan%` | low | avvist: `Kursrad` avviser kurser som ikke er endelige eller over null (`src/kursdata.py`), så slike rader kommer ikke fram |
| BH10 | Høyden står i `style`, som en CSP kunne stoppet | low | avvist: appen har ingen CSP, og aksjesiden bruker `style` på samme måte |
| BH12 | `--gul-symbol` er ikke definert for et mørkt tema | low | avvist: sidene har ikke noe mørkt tema |
| BH15 | `ANTALL_SJEKKER` kunne mangle i `app.py` | low | avvist: importert fra før (`from hjelpetekster import ANTALL_SJEKKER`) |
| VG8 | «Ingen ny tabell» har ingen egen test | low | avvist: diffen rører ingen migrasjon og ingen adapter, og nettsperren stopper nye kall (AD-8) |
