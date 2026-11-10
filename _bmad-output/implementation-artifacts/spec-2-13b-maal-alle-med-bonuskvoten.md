---
title: 'Story 2.13b: målingen av aksjene uten måling, med bonuskvoten'
type: 'feature'
created: '2026-11-10'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '53ff012c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-13-maalingen-av-omsetning.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11b-de-15-i-bransjelistene.md'
---

Skrevet 10.11 i vindu 2. Instruksjonen «Målingen av alle aksjene i natt 10.11» ble limt inn kl. 16:20, med svarene om bransjeforslaget kl. 16:22 og 16:25, tilleggene kl. 16:26 og 16:28 og svaret om målingen kl. 16:35. Alt føres i `docs/ai-prompts/2026-11-10.md` i steg 4. Gruppens svar kl. 13:48: aksjene i børslista som mangler en måling av omsetningen, måles én gang i natt med bonuskvoten, med et tak så minst 200 kall blir igjen i den. Det endrer regelen om at målingen aldri bruker bonuskvoten, bare for denne kjøringen. Rådet anbefalte det. Endringen bygges fra `53ff012c` på grenen `2-13b-maal-alle`, i worktreen `G74-lund-osen-2-13b`.

## Svarene kl. 16:31

*Gruppens svar 2026-11-10 kl. 16:31, rådet anbefalte begge:*

1. «Mangler en måling» betyr ingen rad i tabellen `omsetning`. De 214 i malinger.md ble målt i planleggingen, men tallene ligger ikke i basen, og listene og filtrene kan bare bruke tallene der. Rekkefølgen er som før.
2. Aksjene i appens liste er ikke med, som i `rekkefoelge()` i dag, fordi appen regner omsetningen deres av kursene (8.11b). Det gir rundt 170 kall, innenfor taket.

Telt med `mode=ro` 10.11, før svaret kl. 16:31: 297 aksjer i `boersliste`, 112 med en rad i `omsetning`, 185 uten, og av dem 15 i appens liste. Valget måler derfor 170 i natt, hvis kvoten holder.

## Spørsmål til gruppen før flettingen

1. **Nummeret.** *Forslag:* story 2.13b, etter 2.13, fordi valget er et tillegg til målingen derfra. Den føres under 2.13 i `epics.md` i steg 2.
2. **Navnet på valget.** *Forslag:* `--med-bonuskvoten`, og det gjelder bare sammen med `--maal-omsetning`. Gis det alene eller med `--les-inn`, avviser kommandoen det med kode 2, så hentingen aldri bruker bonuskvoten gjennom det.
3. **Rekkefølgen.** *Forslag:* rekkefølgen fra `rekkefoelge()` som før, med aksjene som har en rad i `omsetning`, tatt ut. Først de som aldri er målt, i rekkefølgen i lista over Oslo Børs, og så de som bare er målt i malinger.md, med den eldste datoen der først og ved lik dato plassen i lista. Alle de 170 er målt i malinger.md, så i natt går de eldste fra malinger.md først.
4. **Bonuskvoten er alt under 200.** *Forslag:* kallene av dagens brukes likevel, fordi de ikke trekker fra bonuskvoten, og ingen kall tas fra bonuskvoten.
5. **Noe annet bruker bonuskvoten underveis.** *Forslag:* kvoten leses før og etter hvert kall, som før. Før et kall som går fra bonuskvoten, stopper valget hvis extraLimit da ville blitt under 200. Har extraLimit sunket under 200 i løpet av et kall, stopper valget også. Det som er målt, lagres.
6. **Et kall som feiler.** *Forslag:* som før. Et svar om at tickeren ikke finnes (HTTP 404) gir en rad med feil og regnes som målt, og en feil som går over, gir ingen rad.
7. **Datoen i GMT.** Kjøringen starter mellom kl. 23:50 og 00:40 i Oslo, altså 22:50–23:40 i GMT. *Forslag:* som før. Skifter datoen i GMT underveis, kl. 01:00 i Oslo, stopper valget, og det som er målt, lagres.
8. **Jobben.** *Forslag:* jobben fra 2.3d bruker ikke valget, og uten valget er alt som før. `docs/installasjon.md` sier det. `docs/hjelp.md` endres ikke, fordi valget ikke er noe brukeren kjører.
9. **Etter midnatt i Oslo (ECH1, høy).** Startes målingen etter midnatt, er børsdagen den nye dagen, og alle de 15 mangler kursen for den. Målingen venter da med 0 kall (svaret 29.10 kl. 09:20, b). Tillegg 2 kan gi start kl. 00:05, så kjøringen i natt ville ikke målt noe. *Forslag:* med valget gjelder børsdagen før når målingen startes før kl. 06:00 i Oslo, og den venter ikke på kursene, som etter kl. 23:45. Uten valget venter den etter midnatt som før. Bygget slik, og funnet står åpent til gruppen har svart (regel 25).
10. **Kall som feiler (ECH2, middels).** Uten valget kunne kall som feiler, bruke høyst de 20 kallene av dagens. Med valget kunne de bruke rundt 150 fra bonuskvoten uten en eneste måling. *Forslag:* med valget stopper målingen etter tre kall på rad som feiler uten svar om at tickeren ikke finnes (404). Det som er målt, lagres. Bygget slik.
11. **Samtidig med jobben (ECH3, middels).** Det finnes ingen lås mellom to kjøringer av `--maal-omsetning`. Går jobbens siste kjøring fortsatt, bruker begge kvoten og måler de samme aksjene. Jobben stopper da med kode 1, fordi extraLimit endrer seg. *Forslag:* ingen lås i koden. Steg 3 i instruksjonen starter bare når oppgaven ikke står som «Kjører», og `docs/installasjon.md` sier at valget ikke skal startes mens jobben kjører.

## Intent

**Problem:** De ferdige listene og filtrene (8.11) kan bare bruke en median som står i tabellen `omsetning`. 185 av de 297 aksjene i børslista har ingen rad der. Målingen fra 2.13 tar 20 om dagen og bruker aldri bonuskvoten, så det ville tatt over en uke.

**Approach:** Et valg, `--med-bonuskvoten`, til `--maal-omsetning`. Med det måler `maal_omsetning()` bare aksjene uten en rad i `omsetning`, med kallene som er igjen av dagens og så bonuskvoten, og stopper før extraLimit blir under `BONUSGULV` (200).

## Delene

### A) Utvalget
`maal_omsetning(med_bonus=True)` i `src/omsetning.py`: planen fra `rekkefoelge()` uten aksjene med en rad i `omsetning`.
- **Ville feilet hvis:** en aksje med en rad ble målt på nytt, en aksje som bare er målt i malinger.md ble hoppet over, rekkefølgen ikke var den fra `rekkefoelge()`, eller en aksje i appens liste ble målt.

### B) Taket
Planen kortes til kallene av dagens pluss extraLimit over `BONUSGULV`.
- **Ville feilet hvis:** valget brukte bonuskvoten før dagens kall, tok kallet som ga 199, eller lot en bonuskvote under 200 stoppe kallene av dagens.

### C) Kontrollen før og etter hvert kall
- **Ville feilet hvis:** valget bare regnet taket før det første kallet, slik at noe annet som brukte bonuskvoten underveis, ga under 200.

### D) Valget i hentekommandoen
`--med-bonuskvoten` i `main()` i `src/fetch_prices.py`.
- **Ville feilet hvis:** valget ikke nådde `maal_omsetning()`, kunne gis uten `--maal-omsetning`, eller målingen uten valget brukte bonuskvoten.

## Grenser

Ingen API-kall i testene, som bruker en falsk henter og en falsk kvote (AD-8). `data/db/ose.db` leses bare med `mode=ro` på grenen (regel 22). Ingen migrasjon. Utskriften har bare antall, datoer og extraLimit, ingen kurser, volumer eller medianer (regel 16).

## Mutantene

Én per del på `97f0fdc4`, med kopi før og fila lik HEAD etterpå. Lik betyr `git hash-object` mot `git rev-parse HEAD:<fil>`; sha256 av arbeidskopien skiller seg fra blobben bare med CRLF, fordi `core.autocrlf` er på. Alle ble fanget:
- A: filteret tatt bort, fanget av `TestUtvalget`.
- B: taket ett for høyt, fanget av `TestTaket`.
- C: kontrollen før kallet tatt bort, fanget av `TestKontrollenFoerHvertKall`.
- D: `med_bonus=False` i `main()`, fanget av `TestUtenValget`.

## Gjennomgangen 10.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `53ff012c..97f0fdc4`. Blind Hunter så bare diffen og fant 7 funn. Edge Case Hunter og Verification Gap gikk i én agent med repoet og fant 7 og 4 funn. Mutantene deres ble kjørt i en kopi utenfor worktreen.

**Høy**
- *ECH1, rettet med forslaget i spørsmål 9, står åpent til gruppen har svart (regel 25).* Startes målingen etter midnatt i Oslo, venter den på kursene for den nye dagen. Nå gjelder børsdagen før når valget startes før kl. 06:00. Testene er `test_etter_midnatt_gjelder_kvelden_foer` (kl. 00:05, 00:40 og 05:59), `test_kl_6_gjelder_dagen_selv` og `test_uten_valget_venter_maalingen_etter_midnatt_som_foer`.

**Middels**
- *ECH2, rettet (spørsmål 10).* Med valget stopper målingen etter tre kall på rad som feiler uten 404. Testene er `test_stopper_etter_tre_feil_paa_rad`, `test_en_feil_innimellom_stopper_ikke` og `test_404_teller_ikke_som_feil_paa_rad`.
- *ECH3, ført (spørsmål 11).* Det er ingen lås. Steg 3 og `docs/installasjon.md` dekker det.
- *BH1 og ECH7, rettet.* Den tomme planen sier hver grunn for seg. Startlinja sier hvor mange av aksjene uten måling som måles, og hvor mange som venter.
- *BH5, rettet.* Testen uten valget har nå en aksje med rad og sjekker de eksakte kallene.

**Lav**
- *Rettet:*
  - BH3, ECH6 og VG3: «Kall fra bonuskvoten» summerer det extraLimit sank under hvert kall, ikke forskjellen fra starten.
  - BH4: «inntil N fra bonuskvoten».
  - BH6 og VG1: nye tester for gårsdagens dato før første kall og for skifte av dato i GMT.
  - VG2: utskriften med valget er testet uten kurser, volumer og medianer.
  - ECH4 delvis: `docs/installasjon.md` sier nå at kallene av dagens brukes også når bonuskvoten er under 200.
- *Ført:*
  - BH2 og ECH4: bruker noe annet et kall mellom lesingen og kallet, kan extraLimit bli 199. Kontrollen etter kallet stopper da. Det kan ikke unngås uten en lås hos EODHD.
  - ECH5: tellingene, 170 aksjer og kall, er over 100 i utskriften. De er antall, ikke rådata (regel 16).
  - BH7: en 404 gir en rad med feil og regnes som målt (spørsmål 6).
  - VG4: to samtidige kjøringer er ikke testet (ECH3).
- **Mutantene for rettingene** på `36bca8cf` og `39c89ebf`, med kopi før og fila lik HEAD etterpå (`git hash-object`):
  - ECH1 (`natt` alltid usann), fanget av `TestGjennomgangen`.
  - ECH2 (stoppen etter tre feil tatt bort), fanget av `TestGjennomgangen`.
  - BH1 (grunnen «ingen aksje mangler» tatt bort), fanget av `TestUtvalget`.
  - BH3 (forskjellen fra starten): overlevde først på `36bca8cf`. Etter `test_kallene_fra_bonusen_telles_uten_det_andre_bruker_mellom_kallene` i `39c89ebf` ble den fanget.

## Testene

Hele settet på `39c89ebf`, alene i fire deler, 16:53:07–17:11:01: 4872 bestått, 24 hoppet over og 0 feilet. Det er til sammen de 4896 som `pytest --collect-only` finner. ruff er kjørt før hver commit.
