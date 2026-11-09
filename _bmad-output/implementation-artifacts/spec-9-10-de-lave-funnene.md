---
title: 'Story 9.10: de lave funnene fra 10.6, 8.8, 8.11b og 3.4h'
type: 'chore'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '78a45186'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/.logs/marian-osen/issues.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-6-ki-teksten-om-dagen-paa-forsiden.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-8-signaldager-i-kursgrafen.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11b-de-15-i-bransjelistene.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4h-investorsidene-i-demoen.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28 og 12:00, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:47 og 10:53: de fire små tingene fra `issues.md` tas nå. Dette er den tredje, de lave funnene. Tillegget kl. 11:28: de tre små PR-ene bygges først og flettes i natt av en egen instruksjon. Endringen bygges fra head-en til PR #129 (`78a45186`), på grenen `9-10-de-lave-funnene`, i worktreen `G74-lund-osen-lave-funn`, og stoppes før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Nummeret.** Funnene er fra fire storyer. *Forslag:* story 9.10 under Epic 9, etter 9.9, som en samlet opprydding. Den føres i `epics.md` i steg 4.
2. **ECH14 i 10.6.** Feiler hovedindeksen om kvelden og hentes ved et nytt forsøk, sto teksten om dagen med et grunnlag uten indeksen, og siden viste den aldri. *Forslag:* teksten om dagen venter til hovedindeksen har en rad for dagen, som den venter på aksjene. Et nytt forsøk samme kveld lager den. Hentes indeksen først neste kveld, er dagen uten tekst, som før, fordi teksten bare lages for inneværende børsdag (BH5 i 10.6). Har basen ingen rader for hovedindeksen, lages teksten som før, uten indeksen.
3. **BH7 og ECH11 i 10.6.** *Forslag:* bryteren ved «Børsdagen kort fortalt» tar med sorteringen tilbake, som perioden og dagen, og adressen bygges på nytt av det som er kjent, som etter merkingen (`tilbake_etter_merking`). En ukjent sortering faller bort. Filteret på signalet (8.11) tas ikke med, som etter merkingen.
4. **VG10 i 10.6.** *Forslag:* en test der lista har 14 aksjer: hentingen lager teksten, og siden viser den. Testen dekker også at lista leses fra basen (2.11).
5. **BH8 og ECH8 i 8.8.** *Forslag:* aksjesiden leser vurderingene én gang til siste dag i grafen (`_vurderingene` i `app.py`). Setningen om dagene bruker bare radene til og med dagen siden viser.
6. **BH4 og ECH4 i 8.11b.** *Forslag:* kursene i vinduet leses i én spørring for alle aksjene, og den siste dagen med primærnøkkelen for hver aksje, ikke med `max(dato)` over hele `kurs`. 8.11c endrer ikke `_aksjene_i_lista`, så de to PR-ene endrer ulike deler av `ferdige_lister.py`.
7. **ECH7 og BH16 i 3.4h.** *Forslag:* kommentaren om U66 i `aksje.html` og kommentaren ved `_RUTER_MED_BASE` i `app.py` rettes med en Rettet-linje i kommentaren. Begge filene står bak bildene i `docs/appen/`, så avtrykkene regnes ut på nytt og bildene tas på nytt.

## Delene

### A) Hovedindeksen for dagen (10.6 ECH14)
`_grunnlaget_for_dagen` i `src/ki_tekst.py`.
- **Ville feilet hvis:** teksten om dagen ble laget med et grunnlag uten hovedindeksen når indeksen manglet raden for dagen, eller et nytt forsøk med indeksen ikke laget den.

### B) Sorteringen i bryteren (10.6 BH7, ECH11)
`_boersdagen` og `ki_bryter` i `src/app.py`.
- **Ville feilet hvis:** sorteringen ble borte etter bryteren, eller en ukjent sortering eller en annen adresse ble sluppet gjennom.

### C) En liste som ikke har 15 (10.6 VG10)
- **Ville feilet hvis:** hentingen og siden regnet grunnlaget for dagen med hver sin liste når lista ikke har 15 aksjer.

### D) Vurderingene én gang (8.8 BH8, ECH8)
`_vurderingene`, `_signaldagene` og `_setningene_om_dagen` i `src/app.py`.
- **Ville feilet hvis:** aksjesiden leste hele vurderingshistorikken to ganger, eller setningen om dagene talte med dager etter dagen siden viser.

### E) Kursene i én spørring (8.11b BH4, ECH4)
`_aksjene_i_lista` i `src/ferdige_lister.py`.
- **Ville feilet hvis:** bransjelistene fikk andre medianer, kursene ble lest med én spørring per aksje, eller den siste dagen ble lest av hele `kurs`.

### F) Kommentarene (3.4h ECH7, BH16)
- Ingen test: kommentarene endrer ikke hva koden gjør. Avtrykkene bak bildene fanger at filene er endret.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke. Ollama startes ikke; testene bruker en falsk modell. Ingen migrasjon.
