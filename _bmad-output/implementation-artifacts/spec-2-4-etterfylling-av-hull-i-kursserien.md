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

*Svar 2026-11-10 kl. 11:52 (gruppens svar):* forslagene i spørsmål 1–5 er godtatt. Rådet anbefalte det. Spørsmål 6 står under funnene og kom ikke med i spørsmålet til gruppen kl. 11:52; svaret på det står under spørsmål 6. Svarene er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`, med svaret kl. 15:30 under den.

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

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `2-4-etterfylling`, i worktreen `G74-lund-osen-2-4`, fra `1a72810a`. Ingen endring i `src/`. Testene er i `tests/test_etterfyllingen_2_4.py`, og svaret står i «Jeg har ikke hentet på noen dager.» i `docs/hjelp.md`. Ingen side endres, så bildene og avtrykkene i `tests/test_docker.py` står.

## Mutantene

Én per del på `653d8d0c`, med kopi før og fila lik HEAD etterpå: A (`kurs` skjøtes med `INSERT OR REPLACE` uten `DELETE`) fanget av `test_eldre_rader_er_kildens_nye`, B (indeksen lagres ikke) av `test_hullet_i_hovedindeksen_fylles_ogsaa`, C (intervallet fire dager) av `test_samme_kall_etter_et_hull_som_dagen_etter`, etter at testen regner intervallet av `DAGER_TILBAKE` og ikke av `bygg_intervall` (`fbf4c7ce`), og D (lageret godtar enhver dato) av `test_ad7_stopper_et_forsoek_paa_aa_etterfylle`.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `1a72810a..fbf4c7ce`: Blind Hunter med bare diffen (11 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (5 og 5 funn, med mutanter i en kopi utenfor worktreen). Ingen høye.

**Middels**
- *BH1, BH2, BH3, ECH1, ECH2 og ECH3, rettet.* Hjelpen sa «Neste henting fyller hullet» uten forbehold, og at kurslinja går rett over dagene som mangler. Et hull fra dager uten henting står i enden av serien, så grafen slutter på siste dag som er hentet, og har ingen linje over hullet. Hjelpen sier nå at hentingen må være etter kl. 22 eller i helgen når basen mangler forrige børsdag, at en aksje som feiler, står med hullet til et nytt forsøk eller neste henting, og at hovedindeksen som feiler, står med hullet til neste kveld som henter, fordi den ikke prøves på nytt og en henting som finner aksjenes kurser i basen, ikke henter den (`manglende_i_basen` ser bare på aksjene).
- *BH5 og VG1, rettet.* Testen for indeksen så bare at hullet var fylt. Nå med kildens endrede kurser, og mutanten B2 (`indeks` skjøtes uten `DELETE`), som overlevde i gjennomgangen, ble fanget.
- *VG2, rettet.* `TestNaarHentingenFeiler`: en aksje og hovedindeksen som feiler etter hullet.
- *BH4, rettet.* `test_en_uke_med_helgen`: en uke borte, over helgen.
- *BH11, ikke reelt.* K9 og sitatet fra endringsforslaget 28.09, §4.6, er slått opp (Edge Case Hunter gjorde det samme).
- *ECH1, lagt til 2026-11-10:* det som sto igjen etter rettingen i hjelpen, at hovedindeksen ikke hentes før neste kveld når bare den mangler, ble spørsmål 6. Gruppen avgjorde det kl. 15:30: hovedindeksen hentes også når bare den mangler. Graden er middels som før (regel 25).

**Lav**
- *Rettet:* ECH4 (signalet lagres bare for børsdagen hentingen gjelder, også i helgen), ECH5 (en aksje som er tatt ut av lista, hentes ikke).
- *Ført:* BH6 (den eldste dagen i `endret` er ikke en egen prøve, fordi serien fra mandag alt begynner tidligere), BH7 og VG4 (testen for AD-7 prøver regelen i lageret, som kontrollen i epics.md ber om, ikke noe 2.4 endrer), BH8 (testene bruker `AKSJEUNIVERS`, som er lista i en ny testbase), BH9 (kl. 22:00 sommertid er grensen og godtas), BH10 og VG5 (ett år er prøvd i `test_fetch_prices.py`, `TestIntervall`), VG3 (sidene endres ikke).

*Lagt til 2026-11-09 under spørsmål 4 (gjennomgangen, BH3):* et hull fra dager uten henting står i enden av serien, så grafen slutter på den siste dagen som er hentet, og går ikke over hullet. Forslaget er det samme: ingen merking.

6. **Hovedindeksen etter en feil.** *Lagt til 2026-11-09 (gjennomgangen, ECH1):* feiler hovedindeksen i hentingen etter hullet, henter ingen kjøring den før neste kveld der en aksje mangler kursene, fordi `manglende_i_basen` bare ser på aksjene. *Forslag:* som før, og hjelpen sier det. Å hente indeksen i helgen når bare den mangler, ville bruke et kall som i dag ikke brukes.

*Svar 2026-11-10 kl. 15:30 (gruppens svar):* hovedindeksen hentes også når bare den mangler. Rådet anbefalte forslaget om å la det være som før, men gruppen valgte dette. Det bygges på grenen før flettingen. Svarene er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`, med svaret kl. 15:30 under den.
