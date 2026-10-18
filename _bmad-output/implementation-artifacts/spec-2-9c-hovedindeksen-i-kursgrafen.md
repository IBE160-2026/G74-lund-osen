---
title: 'Story 2.9c: hovedindeksen som stiplet linje i kursgrafen'
type: 'feature'
created: '2026-10-18'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'bf289a4'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/src/graf.py'
  - '{project-root}/src/templates/aksje.html'
---

## Intent

**Problem:** kursgrafen på aksjesiden viser aksjens kurs og snittet, men ikke børsen. Story 2.9c i `epics.md` (gruppens svar 17.10 kl. 22:38–22:42) ber om hovedindeksen som stiplet linje, regnet om så den starter på aksjens kurs.

**Grunnlaget:** instruksjonen 17.10 kl. 23:13, steg 5, og kontrollpunktene under story 2.9c, skrevet inn i `db5624b` før storyen ble bygget.

## Planen, én commit per punkt

1. Denne spesifikasjonen.
2. `src/graf.py`: `indeksverdier` regner indeksen om til aksjens kurs, og `bygg_graf` tegner den som `indekslinje` på samme skala som kursen og snittet.
3. `src/app.py`: aksjesiden leser serien for indeksen gjennom `SqliteIndekslager`, med samme valg av indeks som forsiden (OSEBX, ellers den basen har, som DEMIX i demoen).
4. `src/templates/aksje.html`: den stiplede linja, navnet på den i teksten for skjermleser og under grafen, teksten når indeksen mangler, og teksten bak «?».
5. `designregler.md`: stiplet linje brukes bare for indeksen.
6. Testene for demoen.

## Avgjort i spesifikasjonen

- **Omregningen.** Startdagen er den første dagen i grafen som indeksen også har. Hver dag d indeksen har, får verdien `kurs(start) × indeks(d) / indeks(start)`. Den første dagen i grafen er startdagen når indeksen har den, og det har den nesten alltid, fordi indeksen hentes sammen med aksjene. Indeksen leses på `justert_slutt`, som endringen på forsiden (story 2.9).
- **Bare dager indeksen har.** En dag i grafen som indeksen ikke har, får ikke noe punkt på den stiplede linja. Linja går rett fra dagen før til dagen etter. Dager indeksen har utenfor grafen, brukes ikke.
- **Skalaen.** Kursen, snittet og indeksen deler skala, så alle tre får plass.
- **Mangler indeksen.** Har indeksen færre enn to dager i grafen, tegnes ingen linje. Teksten under grafen sier at hovedindeksen mangler for perioden. Kan indeksen ikke leses, sier teksten det, og grafen vises uten linja (NFR-03).
- **Farge og strek.** Linja er stiplet, 1,5 px, i Dempet `#5F646C` (5,96:1 mot hvitt). Stiplet brukes bare for indeksen (`designregler.md`).
- **Teksten.** Den sier hva linja er, og at aksjens linje over den stiplede betyr at aksjen gikk bedre enn indeksen i perioden. Den sier ikke noe om hva aksjen vil gjøre (NFR-06).

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Ingen ny tabell og ingen nye kall: indeksen er den 2.8 henter.

## Kjøringen som ble stoppet 18.10

Testkjøringen etter rettingene fra gjennomgangen startet 18.10 kl. 00:40:21. Den hadde fem testfiler med til sammen 384 tester, og skulle ta rundt to minutter. Claude Code stoppet den om morgenen fordi det var lite minne, og fila med utskriften ble sist skrevet kl. 09:59:28.

**Grunnen:** maskinen gikk i hvilemodus kl. 00:40:21, samme sekund som kjøringen startet (Kernel-Power 42 i systemloggen). Den våknet kl. 09:58:23 (Power-Troubleshooter 1). Rett etter stoppet Claude Code kjøringen. Kjøringen hang altså ikke i koden. Prosessen sto stille mens maskinen sov, og ingen stakk fra faulthandler kom, fordi ingen test brukte tid.

**Slik det ble sjekket 18.10 kl. 10:42:**
- 4418 MB av 16 124 MB var ledig.
- `tests/test_graf.py` (31), `tests/test_demo.py` (52) og `tests/test_app.py` (203) ble kjørt hver for seg med `-x`, `-o faulthandler_timeout=60` og `timeout 300` i Git Bash. Utskriften gikk til en fil, og `test_app.py` ble kjørt sist.
- Alle besto, på 1,3 s, 11,6 s og 37,5 s.

Det var ingen feil i koden, og derfor er det ingen ny test for det.

Utskriften fra den stoppede kjøringen gikk gjennom `tail -1`, og der sto bare 40 punkter. Det er den uferdige linja med fremdrift når kjøringen ble stoppet, ikke antallet tester. Fra nå går utskriften til en fil, ikke gjennom `tail`.

## Mutantene

Én om gangen med `-x`, i den ferske klonen med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver. C1–C3 er de instruksjonen kl. 23:13 ber om, og ble fanget både på `4c8c10b`, før gjennomgangen, og på `b190ed5`. C4–C6 er én for hvert funn med dom medium, og ble fanget på `b190ed5`:
- C1, uten omregning (indeksen i sine egne poeng): `test_linja_starter_paa_aksjens_kurs_og_foelger_indeksen`.
- C2, feil startdag (indeksens første dag i stedet for grafens): `test_startdagen_er_grafens_foerste_dag_ikke_indeksens`.
- C3, en linje tegnet uten indeks: `test_uten_indeks_ingen_linje_og_grafen_sier_det`.
- C4, startdatoen alltid grafens første dag (BH4, VG1): `test_uten_grafens_foerste_dag_starter_linja_paa_den_neste`.
- C5, «Begge linjene» også med indeksen (BH3): `test_teksten_sier_hva_linja_er_uten_raad`.
- C6, «?» bare med sjekkene (BH11): `test_hjelpen_for_linja_ogsaa_uten_snitt`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `bf289a4..4c8c10b`, med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 9) og Verification Gap (VG, 9). Verification Gap regnet kontrasten på nytt (5,956:1) og fant den riktig. Den sjekket også at kildene for teksten bak «?» står ordrett, at teksten ikke har ord for råd, og at demoen viser DEMIX. Rettingene står i commitene fra `d1f9f72` til `b190ed5`, én per funn eller gruppe.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH4, ECH1, ECH9, VG1 | Mangler indeksen grafens første dag, starter linja senere, men teksten bak «?» og designreglene sa «første dag i grafen». Det var ikke prøvd | medium | patch: «den første dagen i grafen som indeksen har», og tester der indeksen mangler grafens første dag (`d1f9f72`). C4 |
| BH3, ECH3, ECH2, VG7 | Under grafen sto «Begge linjene» med tre linjer, og hjelpen sa at navnet står ved hver linje | medium | patch: egen tekst med indeksen, og navnet ved kurslinja og snittet (`cc62fd2`). C5 |
| BH11, ECH4, VG8 | «?» for linja krevde sjekkene, og ble ikke prøvd uten snittet | medium | patch: hjelpen for linja står når linja står (`a7aa180`). C6 |
| BH5 | Teksten under grafen og bak «?» sa det ulikt | low | patch: samme ordlyd (`d1f9f72`) |
| BH9, ECH5 | Sluttet indeksen før aksjen, sto det ikke noe om det | low | patch: «Indeksen går bare til …» (`aeadcc4`) |
| ECH8, VG9 | Etiketten for skjermleser sa ikke at linja manglet, og en feil i `serie` var ikke prøvd | low | patch (`9da97f9`) |
| VG6 | En kilde for teksten bak «?» var docstringen | low | patch: regnestykket (`ecfb8c4`) |
| VG2, VG3, BH13, VG4, VG5, BH15, BH12 | Testene manglet `justert_slutt`, samme indeks som forsiden, stiplet per velger på begge sidene, hva testen for 390 px viser, og linja i demoen innenfor tegneflaten | low | patch (`b190ed5`, og BH12 i `d1f9f72`) |
| BH1, BH2 | En indeks på 0, NaN eller None ville gitt deling på null eller TypeError | low | avvist: `Kursrad` avviser kurser som ikke er tall, ikke er endelige eller ikke er over null (`src/kursdata.py`), og `UgyldigKursrad` er en ValueError som `_indeksen_for_grafen` fanger |
| BH6 | Den stiplede linja har ikke navn ved enden | low | avvist: den har navnet under grafen og i etiketten for skjermleser, og hjelpen sier nå at navnet står ved kurslinja og snittet |
| BH7 | `symboler()[0]` var ikke vist å være den sist hentede | low | avvist: rekkefølgen er prøvd i `test_sist_hentet_foerst` (story 2.9), og VG3 prøver at grafen viser OSEBX |
| BH8 | Hele serien for indeksen leses på hver side | low | avvist: det er samme mengde som serien for aksjen, som også leses hel |
| BH10, ECH6 | En indeks som beveger seg mye, presser aksjens linje sammen | low | avvist: felles skala er det storyen ber om, for at «over den stiplede» skal bety noe |
| BH14 | Forventningen i testen for vinduene er fast | low | avvist: fiksturen er demobasen med DEMIX, og den fantes før 2.9c |
| ECH7 | Én dag i grafen og ingen dager gir samme tekst | low | avvist: med færre enn to dager kan ingen linje tegnes, og «mangler for perioden» stemmer for perioden |
