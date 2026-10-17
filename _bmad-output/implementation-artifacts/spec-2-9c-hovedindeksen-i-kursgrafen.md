---
title: 'Story 2.9c: hovedindeksen som stiplet linje i kursgrafen'
type: 'feature'
created: '2026-10-18'
status: 'in-progress'
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
