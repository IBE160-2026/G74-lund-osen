---
title: 'Story 8.17a: periodevalget i oversikten, med søylene og indekslinja'
type: 'feature'
created: '2026-10-30'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'afd08c5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/src/perioder.py'
  - '{project-root}/src/templates/_perioder.html'
  - '{project-root}/src/markedsoversikt.py'
  - '{project-root}/src/hovedindeks.py'
  - '{project-root}/src/app.py'
---

## Intent

Oversikten får periodevalget fra 8.16 over tabellen, og søylene under hovedindeksen og indekslinja følger samme periode og dag (story 8.17, første del). Min liste og børsometeret er 8.17b (gruppens svar 23.10 kl. 12:35, c). Storyen er «Ekstra» og flettes bare ferdig og grønt (svaret 19.10 kl. 14:48). Bygget 30.10 etter svaret 29.10 kl. 09:20, og stopper før flettingen.

## Slik er det i dag (slått opp 30.10 på `afd08c5`)

- `perioder.py` har kodene, knappene, `startdag` og `les_valg`. `les_valg` gir 6 mnd uten periode i adressen og ved feil, med en beskjed som sier «grafen viser 6 mnd».
- `_perioder.html` har makroen `periodevalg(knapper, valgt, adresse, dag, minst, maks, etikett, anker)`, med lenker og et skjema med `periode=velg` og `dag`.
- Oversikten (`_tabellsiden` i `app.py`) bygger radene med `bygg_oversikt`, der endringen er de to siste kursene (`endring_i_prosent`). Sortering står i adressen som `sorter` og `orden` (`side_adresse`).
- Søylene (`bygg_soeyler` i `hovedindeks.py`) bruker endringen for indeksens dato (`aksjeendring`), og linja indeksens endring for samme dag (`indeksendring`). `tre_av_tre` er symbolene med 3 av 3 på siste børsdag.
- `Oversiktsleser.vurdering(symbol, dato)` leser raden i `vurdering` for en dag uten å regne (8.16).

## Kontrollpunktene

- Siste børsdag er valgt når oversikten åpnes, og perioden og dagen står i adressen, også i lenkene som sorterer og i «Standard rekkefølge».
- For en periode er endringen `adjusted_close` på siste børsdag mot `adjusted_close` på startdagen fra `perioder.startdag`, regnet fra radens siste børsdag. Har serien ikke startdagen, regnes den fra første dag serien har etter den, og raden sier «fra» og datoen.
- Ved en periode gjelder sluttkursen, signalet, «Skilte seg ut», 2 av 3 og gult siste børsdag (svar a kl. 12:35).
- «Velg dag» viser sluttkursen og endringen den dagen og raden i `vurdering` for den, eller «– ikke vurdert», grunnen eller «– ikke børsdag». Signalet regnes aldri (AD-7).
- Gult står ved 3 av 3 på siste børsdag også med en periode og «Velg dag». 2 av 3 merkes bare når siden viser siste børsdag eller en periode (signalet er da siste børsdag), aldri for en valgt dag (designregler §3).
- Søylene og linja følger samme periode og dag, regnet med de samme funksjonene. Bransjesymbolet er gult ved 3 av 3 på siste børsdag, som før.
- **Ville feilet hvis:** «Velg dag» før vurderingene i demoen viste et signal, eller søylene viste dagens endring mens tabellen viste en uke.

## Valg som er gjort her

- **Oversikten åpner med siste børsdag**, ikke 6 mnd som kursgrafen (§2). `les_valg` får derfor en standardperiode og en tekst for hva siden viser ved en feil i adressen: «så oversikten viser siste børsdag». Kursgrafen er uendret.
- **Grensene for «Velg dag»:** første dag og siste dag blant seriene i oversikten, så `les_valg` avviser en dag fram i tid, etter siste kurs eller på eller før første kurs, som på aksjesiden.
- **Endringen for en periode** er ett tall per rad i kolonnen «Endring», som får perioden i kolonneraden. FR-102 og sorteringen på endring bruker tallet som vises.
- **«Velg dag» er én liste uten delene**, fordi «Skilte seg ut» gjelder siste børsdag (svar a). Rekkefølgen er FR-102 på dagens tall, og sortering ved klikk virker som før.
- **Gult ved «Velg dag»:** raden har streken i sterk oransje og teksten «3 av 3 siste børsdag» når aksjen fikk 3 av 3 siste børsdag. Pillen for dagen har ingen ring og ingen 2 av 3-merking.
- **Overskriften og indekstallet** over tabellen gjelder fortsatt siste børsdag. Søylene får en overskrift med perioden eller dagen.
- **Merkingen i Min liste** (stjernen) sender tilbake til oversikten med perioden og dagen.
- Ingen ny tabell, ingen migrasjon og ingen nettkall.

## Planen

1. a) Periodevalget, radene og adressen.
2. b) Søylene og linja, hjelpen, `docs/hjelp.md` og README-en.
3. c) Testene og mutantene.
4. Hele settet, gjennomgangen, triagen her og i PR-en.

## Mutantene

Tre, én om gangen med `-x`, med kopi før og sha256 mot HEAD etter: endringen fra dagen før i stedet for startdagen, søylene for siste børsdag ved en periode, og gult fra dagen som vises.

*Utfallet 30.10 kl. 00:52:19–00:52:25 på `635205e`, mot `tests/test_periodevalget_oversikten.py`:*

| Mutant | Endringen | Fanget av |
|---|---|---|
| M1 | `periodeendring` i `src/markedsoversikt.py` tar raden før slutt, ikke raden på startdagen | `test_1_uke_og_1_mnd_mot_den_haandregnede_serien` |
| M2 | `soeylene_for` i `src/hovedindeks.py` gir søylene for siste børsdag også ved en periode (`if True:`) | `test_soeylene_og_linja_foelger_perioden` |
| M3 | `bygg_rad_for_dag` i `src/markedsoversikt.py` gir gult fra 3 av 3 den dagen som vises | `test_dagen_viser_det_som_er_lagret` |

Etter hver mutant var fila lik kopien (samme sha256) og lik `HEAD`.

## Gjennomgangen

## Åpent
