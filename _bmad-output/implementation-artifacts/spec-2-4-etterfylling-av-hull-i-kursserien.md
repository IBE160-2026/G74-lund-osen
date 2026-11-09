---
title: 'Story 2.4: etterfylling av hull i kursserien'
type: 'feature'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '1a72810a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28, 12:00 og 15:43, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:30 og 10:43: 2.4, 2.6 med 8.14, 8.7 og 8.9 bygges i dag og flettes onsdag etter brukertesten. Instruksjonen sier for 2.4: «hullet fylles ved neste henting med de samme kallene som ellers, prøvd bare på testbaser.» Bygget fra head-en til PR #126 (`1a72810a`), på grenen `2-4-etterfylling`, i worktreen `G74-lund-osen-2-4`, og stoppet før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Hva bygges?** Hver henting tar et år bakover for hver aksje og hovedindeksen (`DAGER_TILBAKE` i `fetch_prices.py`) og erstatter hele serien i basen (`erstatt_serie`, AD-5). Et hull fylles derfor alt ved neste henting, og K9 i 2.1b (`test_fire_dagers_opphold_fylles_med_16_kall`) prøver fire dager. Det står også i endringsforslaget 28.09, §4.6: «2.4 står, men kan lukkes med en henvisning dit». *Forslag:* ingen endring i koden. 2.4 får testene for resten av kontrollen i epics.md og et svar i hjelpen.
2. **«15 kall».** Med 2.8 ble det 16, og med lista fra basen (2.11) er det én per aksje i lista og én for hovedindeksen. *Forslag:* kontrollen leses som «de samme kallene som en vanlig kveld», slik instruksjonen sier, og testen sammenligner en kveld etter et hull med kvelden etter.
3. **Hjelpen.** *Forslag:* et nytt spørsmål i `docs/hjelp.md`, «Jeg har ikke hentet på noen dager.», etter «Når kan jeg hente?»: neste henting fyller hullet, og dagene uten henting har ikke signal.
4. **Før neste henting.** Åpnes appen før hullet er fylt, går kurslinja rett over dagene som mangler, og endringen regnes mot forrige rad (gruppens svar 06.11 kl. 09:55 og 12:16). *Forslag:* som før, uten merking av hullet. Det er utenfor kontrollen i 2.4.
5. **Over et år.** Serien er alltid ett år bakover fra dagen, så etter et opphold på over et år er hele serien ny, og kurser eldre enn et år står ikke i basen, som før. *Forslag:* ingen endring.

## Intent

**Problem:** En bruker som ikke har hentet på en uke, skal se en hel graf etter neste henting, uten at hullet ser ut som en kursbevegelse, og uten at noen vurdering etterfylles (AD-7).

**Approach:** Oppførselen finnes fra 2.1b. Testene i `tests/test_etterfyllingen_2_4.py` prøver resten av kontrollen på testbaser, og hjelpen sier det.

## Delene

### A) Serien byttes i sin helhet
- **Ville feilet hvis:** hentingen bare la til dagene som manglet, så eldre kurser som kilden har justert, og en dag kilden ikke lenger har, sto igjen.

### B) Hovedindeksen
- **Ville feilet hvis:** bare aksjene ble fylt, og hovedindeksen sto med hullet.

### C) De samme kallene
- **Ville feilet hvis:** hullet ble hentet med ett kall per dag som manglet, eller med et annet intervall enn en vanlig kveld.

### D) Ingen vurderinger etterfylles
- **Ville feilet hvis:** hentingen etter hullet skrev vurderinger for dagene i hullet, eller lageret godtok en vurdering for en av dem (AD-7).

### E) Hjelpen
«Jeg har ikke hentet på noen dager.» i `docs/hjelp.md` (regel 19). Ingen side endres, så bildene i `docs/appen/` tas ikke på nytt.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres bare i testene med en falsk henter, og `data/db/ose.db` røres ikke. Ingen migrasjon.
