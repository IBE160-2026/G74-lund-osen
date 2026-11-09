---
title: 'Story 8.11c: «Utenfor målingen» med medianen av kursene'
type: 'feature'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '78a45186'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11b-de-15-i-bransjelistene.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-12-velge-og-bytte-aksjer.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28 og 12:00, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:23: spørsmål 9 i 8.11b blir et punkt i `issues.md` til senere. Kl. 10:47 og 10:53: de fire små tingene fra `issues.md` tas nå. Tillegget kl. 11:28: de tre små PR-ene bygges først og flettes i natt av en egen instruksjon. Endringen bygges fra head-en til PR #129 (`78a45186`), på grenen `8-11c-utenfor-maalingen`, i worktreen `G74-lund-osen-8-11c`, og stoppes før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Nummeret.** *Forslag:* story 8.11c, etter 8.11 og 8.11b, fordi endringen er spørsmål 9 i 8.11b. Den føres i `epics.md` i steg 4.
2. **Hvilke aksjer?** *Forslag:* de samme som regnes av kursene i de ferdige listene: alle aksjene i `aksje` som står i `boersliste`, i lista eller tatt ut (spørsmål 1 i 8.11b, utvidet etter ECH1). For dem gjelder medianen av kursene. De andre har den siste målingen i `omsetning` (2.13), som før. Det gjelder også en aksje som venter på henting, fordi den ikke er i `aksje` ennå.
3. **Hvor?** *Forslag:* merket ved navnet i oversikten, på aksjesiden og i børsometeret, «Dine egne aksjer» og «Din egen liste», og omsetningen på «Følg en aksje», både for en valgt aksje og i søket. Da sier alle sidene det samme tallet som de ferdige listene.
4. **Teksten.** For en median av kursene sier teksten bak merket «regnet av kursene til 22.09.2026» i stedet for «målt 22.09.2026». Dagen er den siste dagen med kurser i basen. *Forslag:* som bygget, og samme ord på «Følg en aksje».
5. **En aksje i lista uten kurser i vinduet.** Den har ingen median av kursene og bruker ikke en eldre måling (BH3 i 8.11b). *Forslag:* merket står da som «Omsetningen er ikke målt ennå», som i de ferdige listene, der den ikke står.
6. **«+0,1 % MNOK» på «Følg en aksje».** Siden fra 2.12 viste omsetningen med slaget for målingene, med fortegn og %. Funnet under byggingen. *Forslag:* rettet i en egen commit i samme PR (`e5d456a2`), med et nytt slag `mnok` i `tallformat.py` (regel 21) og en test. Rettingen følger med i natt, ellers står feilen i 2.12 etter flettingen kl. 23:50.
7. **Samspillet med de lave funnene.** BH4/ECH4 i 8.11b (`max(dato)` over hele `kurs` og én spørring per aksje) rettes i PR-en for de lave funnene, i `_aksjene_i_lista`. *Forslag:* 8.11c endrer ikke `_aksjene_i_lista`, men kaller den fra en ny funksjon, `medianene()`, nederst i `ferdige_lister.py`, så de to PR-ene endrer ulike deler av fila og kan flettes etter hverandre i natt.

## Intent

**Problem:** Merket «Utenfor målingen» fra 2.12 leser den siste målingen i `omsetning`, mens de ferdige listene i 8.11b regner medianen av kursene for aksjene appen henter. En egen aksje kunne stå som ikke målt i tabellen og med en median i den ferdige lista (ECH2 i 8.11b).

**Approach:** `medianene()` i `src/ferdige_lister.py` gir medianen `lister()` bruker for hver aksje som regnes av kursene, og `_omsetningen()` i `src/app.py` bruker den for merket og «Følg en aksje», med målingen fra 2.13 for de andre.

## Delene

### A) Medianene
`medianene()` i `src/ferdige_lister.py`.
- **Ville feilet hvis:** merket og de ferdige listene fikk hver sin median for en aksje som regnes av kursene, eller en aksje som bare er målt i 2.13, fikk en median herfra.

### B) Merket
`_omsetningen()` og `_egne()` i `src/app.py`.
- **Ville feilet hvis:** merket fulgte målingen i 2.13 og ikke medianen av kursene for en egen aksje som er hentet, eller merket og den ferdige lista var uenige.

### C) «Følg en aksje»
`folg_side()` i `src/app.py` og `src/templates/folg.html`.
- **Ville feilet hvis:** siden viste målingen i 2.13 for en aksje som regnes av kursene, eller mistet målingen for en aksje appen aldri har hentet.

### D) Teksten
`utenfor_tekst()` i `src/valg.py`.
- **Ville feilet hvis:** teksten sa «målt» om en median regnet av kursene, eller omvendt.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke. Ingen migrasjon. Medianene regnes når siden vises og lagres ikke, og ingen tall fra kildene står i koden, testene eller spesifikasjonen (regel 16).
