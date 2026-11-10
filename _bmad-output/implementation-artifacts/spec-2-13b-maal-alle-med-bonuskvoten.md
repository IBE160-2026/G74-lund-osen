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
