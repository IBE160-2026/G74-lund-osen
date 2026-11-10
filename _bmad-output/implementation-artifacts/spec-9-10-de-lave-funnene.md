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

*Svar 2026-11-09 kl. 17:37 (gruppens svar):* forslagene i spørsmål 1 og 3–7 er godtatt. På spørsmål 2 anbefalte rådet a, men gruppen valgte c: neste kveld lages teksten for forrige børsdag når den mangler og hovedindeksen nå er der. Det bygges senere, og ECH14 i 10.6 står åpent som lav, med et punkt i `issues.md`. Rådet anbefalte resten. Svaret er ført etter instruksjonen kl. 21:41 i `docs/ai-prompts/2026-11-09.md`, og storyen står i `epics.md` i Epic 9.

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

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `9-10-de-lave-funnene`, i worktreen `G74-lund-osen-lave-funn`, fra `78a45186`.

- **Filene.** `src/app.py` (B, D og BH16), `src/ferdige_lister.py` (E), `src/templates/aksje.html` (ECH7), «Hva er «Børsdagen kort fortalt» på forsiden?» i `docs/hjelp.md` (regel 19), og testene i `tests/test_de_lave_funnene_9_10.py`. `test_siden_leser_en_gang_per_maaned` i `tests/test_historikken.py` venter nå én lesing fra starten, ikke to (D).
- **Bildene.** `app.py`, `ferdige_lister.py`, `ki_tekst.py` og `aksje.html` står bak bildene i `docs/appen/`. Avtrykkene er regnet ut på nytt, og alle ni bildene er tatt på nytt med DevTools-protokollen og er byte for byte de samme.
- **Flettingen med 8.11c.** Begge PR-ene endrer avtrykkene i `tests/test_docker.py`. Den som flettes sist, får en konflikt der, og avtrykkene må regnes ut på nytt etter at den andre er flettet inn.

## Mutantene

Én per del på `05e3e864`, med kopi før og fila lik HEAD etterpå: A (ventingen tatt bort) fanget av `TestHovedindeksenForDagen`, B (skjemaet uten sorteringen) overlevde, fordi testen fant sorteringen i skjemaet for merkingen. Testen ser nå bare i bryterens skjema, og mutanten ble fanget. D (setningen om dagene med alle dagene) ble fanget bare av `test_setningen_om_dagene_bare_til_dagen_siden_viser`, som leser kildeteksten (se BH7 og VG3), og E (én kursrad per aksje) av `TestKurseneIEnSpoerring` og `test_ferdige_lister_8_11b.py`. Del A er tatt ut igjen etter gjennomgangen (ECH1 under).

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `78a45186..05e3e864`, uten `tests/test_docker.py`: Blind Hunter med bare diffen (9 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (3 og 5 funn, med mutanter i en kopi utenfor worktreen).

**Høy**
- *VG1, rettet.* D gjorde `test_siden_leser_en_gang_per_maaned` i `tests/test_historikken.py` rød, fordi den ventet to lesinger fra starten. Testen venter nå én, med en Rettet-linje i kommentaren. Funnet viser at testene som rører endringen, ikke ble kjørt før gjennomgangen; hele settet kjøres før push.

**Middels**
- *ECH1, rettet ved å ta del A ut, og ECH14 står åpent.* Premisset i spørsmål 2 var feil: hentingen prøver ikke hovedindeksen på nytt samme kveld (AD-15, kommentarene i `fetch_prices.py`), så teksten om dagen ville aldri blitt laget den kvelden indeksen feilet, og det er verre enn før. Koden i `ki_tekst.py` er som på `78a45186`. BH5 (ventingen har ingen grense) og VG2 (testen prøvde en vei som ikke finnes) følger med.
- *ECH1, besvart 2026-11-09 med spørsmål 2* (gruppens svar kl. 17:37), middels som før (regel 25): del A er tatt ut, og gruppen valgte c for ECH14, som bygges senere. ECH14 står åpent som lav.
- *ECH2, rettet.* Kursene i vinduet ble lest ved å gå gjennom hele `kurs`. Nå med `CROSS JOIN`, så primærnøkkelen brukes for hver aksje (`test_kurs_leses_aldri_i_sin_helhet`, som krever `symbol=` i hver linje i spørringsplanen som gjelder `kurs`).
- *BH1, ikke reelt.* `kode` er primærnøkkel i `boersliste`, så en kursrad kommer ikke med to ganger.
- *BH2, ikke reelt.* `aksjedetalj` returnerer før `rader[-1]` når aksjen ikke har kurser.

**Lav**
- *Rettet:* BH6 (`&` er påkrevd mellom perioden og sorteringen i `_TILBAKE_OVERSIKTEN`), BH8 (testen krever nøyaktig to spørringer mot `kurs`), ECH3 (hjelpen sier at filteret på signalet ikke tas med etter bryteren), VG4 (spørringsplanen i stedet for et søk i kildeteksten), VG5 (valgt dag og sortering sammen).
- *Ført:* BH7 og VG3 (setningen om dagene bare til dagen siden viser er sjekket i kildeteksten; to mutanter overlevde der, og en sidetest med en valgt dag gjenstår), BH9 (den siste dagen fra `aksje`; triggerne på `kurs` stopper rader for andre symboler, så verdien er den samme).
- *Ikke reelt:* BH3 (`BASEFEIL` har `RuntimeError`), BH4 (dagen siden viser er aldri etter siste dag i grafen).

*Lagt til 2026-11-09 under spørsmål 2 (gjennomgangen, ECH1):* forslaget i spørsmål 2 er tatt ut igjen og ikke bygget. ECH14 står åpent, og spørsmålet til gruppen er nå: a) som før, teksten lages uten hovedindeksen når den mangler, og dagen står uten tekst når indeksen kommer neste kveld; b) teksten venter bare når hovedindeksen ble lagret i kveldens henting, ellers lages den uten; eller c) neste kveld lages teksten for forrige børsdag når den mangler og indeksen nå er der (ett kall til). *Forslag:* a, til gruppen har svart, fordi b og c endrer når modellen kalles. Hjelpen er som før om dette.
- **Mutantene for rettingene**, med kopi før og fila lik indeksen etterpå: B for `&` (valgfri igjen) fanget av `TestSorteringenIBryteren`, ECH2 (`JOIN` uten `CROSS`) og den gamle `max(dato)` over hele `kurs` av `test_kurs_leses_aldri_i_sin_helhet`. Den gamle `max(dato)` overlevde først, fordi SQLite skriver «SEARCH … COVERING INDEX» også når hele indeksen leses, og ble fanget da testen krevde `symbol=`. Første runde med kopien feilet fordi en gjennomgangsagent hadde laget en mappe med samme navn som kopifila; filene ble hentet tilbake fra indeksen og kontrollert, og mutantene ble kjørt på nytt.
