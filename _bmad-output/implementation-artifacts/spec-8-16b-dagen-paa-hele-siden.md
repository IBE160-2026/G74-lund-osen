---
title: 'Story 8.16 (8.16b): når en dag er valgt, viser hele aksjesiden den dagen'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3adf22d'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-16-periodene-i-kursgrafen.md'
---

## Intent

**Problem:** etter 8.16 viser kortene øverst, «Hvorfor signalet ble» og KI-teksten alltid siste børsdag, mens linja over grafen viser dagen som er valgt med «Velg dag». Siden kan da ha to ulike signaler.

**Grunnlaget:** gruppens svar 19.10 kl. 00:00, som utvider svaret 18.10 kl. 21:50, og instruksjonen 19.10 kl. 10:32.

## Kontrollpunktene

- a) Siden for dagen: med en valgt dag bygges detaljen av kursraden og raden i vurdering for dagen, og KI-teksten av raden i KI-loggen for dagen, gjennom leserne som finnes. Overskriften, datoen, sluttkursen, endringen fra forrige børsdag, signalstyrken, retningen og sjekkene med målingene er dagens. Uten rad står «– ikke vurdert», grunnen eller «– ikke børsdag», og uten KI-rad teksten appen har for en dag uten KI-tekst. Øverst står et merke om at siden viser en tidligere dag, med en lenke tilbake til siste børsdag. Endringen og signalet for dagen står i kortene, ikke i en egen linje over grafen, og grafen har dagen merket. Knappen for KI-teksten tar deg tilbake til den samme dagen. Med en periode eller den første knappen viser toppen siste børsdag, som nå.
- b) Tekstene (regel 19): hjelpen til periodene og «Velg dag», og `docs/hjelp.md` hvis den nevner dem. Endres en fil bak bildet av oversikten, tas bildet på nytt slik feilmeldingen i testen sier.
- c) Testene, med «Ville feilet hvis»: med «Velg dag» viser kortene, sjekkene og KI-teksten den valgte dagen og ikke siste børsdag; en dag uten vurdering, en dag med en grunn og en lørdag; en dag uten KI-rad; merket og lenken tilbake; knappen for KI-teksten beholder dagen; med en periode viser toppen siste børsdag; for en valgt dag kalles `vurder` ikke (AD-7). Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: kortene fra siste børsdag med en valgt dag, KI-teksten fra siste børsdag, og en valgt dag som regner signalet.

## Planen, én commit per punkt

1. a) `bygg_detalj` i `src/aksjedetalj.py` får dagen og raden i vurdering for den. Uten dagen er alt som før. Med dagen er serien kursradene til og med dagen: sluttkursen og endringen er fra kursraden for dagen, og sjekkene fra raden i vurdering, lest med `Oversiktsleser.vurdering` fra 8.16. Ruta i `src/app.py` leser raden én gang og bruker den både til detaljen og til merket i grafen. KI-teksten leses for `detalj.dato` og prøves mot vurderingen som vises. Malen får merket øverst, linja over grafen står bare for den første knappen, og bryteren sender adressen med dagen, som `_TILBAKE` godtar. De testene fra 8.16 som leste linja over grafen for en valgt dag, leser kortene i stedet, i samme commit, så hver commit er grønn.
2. b) Hjelpeteksten «perioden» sier at «Velg dag» viser hele siden for dagen. `docs/hjelp.md` nevner ikke periodene (`git grep`), så den endres ikke. `src/hjelpetekster.py` står bak bildet, så bildet tas på nytt hvis avtrykket endres.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Siste børsdag** er siste rad i kursserien, som i resten av siden. Velges den med «Velg dag», er siden den samme som for siste børsdag, uten merket om en tidligere dag.
- **En dag uten kurs**, som en lørdag: datoen er dagen, sluttkursen og endringen er «–», og teksten fra `les_tilstand` står, som i oversikten. Grafen slutter dagen før, som i 8.16.
- **Lenken tilbake** går til `/aksje/<symbol>`, siden slik den åpnes, med siste børsdag øverst.
- **Bryteren** godtar `/aksje/<symbol>?dag=ÅÅÅÅ-MM-DD` og ellers bare stiene den godtok før. Datoen leses på nytt av `les_valg`, så en dag som ikke kan vises, gir 6 mnd og beskjeden fra 8.16.
- **Linja over grafen** står fortsatt for den første knappen, der dagen er siste børsdag og det samme som kortene. For en valgt dag står endringen og signalet bare i kortene.

## Avgjort underveis

- **Merket øverst** har fargene til merkene over h1 (`--hvit`, `--strek-2` og `--tekst`), ikke oransje, fordi `designregler.md` §5 gir oransje bare til faste ting.
- **Bildet** ble tatt på nytt i b kl. 10:41 (date), med samme fremgangsmåte og høyde (1280 × 1573), fordi `src/hjelpetekster.py` står bak det. Det var likt byte for byte, sha256 `57e53e54d4b0d264…`, så bare avtrykket er nytt.
- **Siste børsdag valgt med «Velg dag»** (gjennomgangen, VG4): siden har ikke merket om en tidligere dag, og kortene er de samme som for siste børsdag. Overskriften over grafen er den for «Velg dag», og linja over grafen står ikke, fordi perioden er «Velg dag». «Den samme» under «Avgjort i spesifikasjonen» gjelder toppen.
- **Overskriften for en tidligere dag** (VG3): markeringen «skilte seg ut» står bare ved 3 av 3, fordi `designregler.md` §3 merker 2 av 3 «bare for siste børsdag».

## Mutantene

Én om gangen med `-x` på `tests/test_app.py` og `tests/test_ki_visning.py` (med `-k 816b`), i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. K1–K3 er fra instruksjonen og ble fanget på `f1e2fae` og på nytt på `315dcbb`. N1–N3 er for funnene, fanget på `315dcbb`:
- K1, kortene fra siste børsdag med en valgt dag: `test_kortene_og_sjekkene_viser_den_valgte_dagen`.
- K2, KI-teksten fra siste børsdag: `test_ki_teksten_for_den_valgte_dagen`.
- K3, en valgt dag som regner signalet med `vurder`: `test_kortene_og_sjekkene_viser_den_valgte_dagen`, og for seg `test_vurder_kalles_ikke_for_en_valgt_dag` og `test_en_dag_uten_vurdering_med_en_grunn_og_en_loerdag`.
- N1, endringen fra siste børsdag med datoene for dagen (VG1): `test_endringen_er_dagens`.
- N2, «Kursen vises likevel» også uten kurs (ECH1): `test_en_boersdag_uten_kurs_i_serien`.
- N3, en tidligere dag merket ved 2 av 3 (VG3): `test_en_tidligere_dag_merkes_bare_ved_3_av_3[2-False]`.

## Gjennomgangen

Gjennomgang 19.10 på diffen `6caf967..f1e2fae`. Linsene var Blind Hunter (BH, 11 funn, bare diffen), Edge Case Hunter (ECH, 7, prøvd med test_client mot en base i en midlertidig mappe) og Verification Gap (VG, 6). Ingen av dem kjørte hele testsettet, en server eller et nettkall. Fire rader har dom medium: tre er rettet i `315dcbb` og her, og BH1 er avvist med beviset under.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | Endringen for dagen var ikke testet på verdien | medium | patch: `test_endringen_er_dagens`. N1 |
| ECH1, ECH2 | En børsdag uten kurs sa «ikke vurdert», «Kursen vises likevel» og --les-inn | medium | patch: «Kursserien har ingen kurs for dagen.», uten fotnoten. N2 |
| VG2 | Mutantene var ikke ført | medium | patch: over |
| BH1 | `detalj.vurdering` var ikke vist i diffen | medium | avvist: propertyen `vurdering` på `Detalj` finnes fra før i `src/aksjedetalj.py`, og testene for KI-teksten går gjennom den |
| VG3 | En tidligere dag med 2 av 3 fikk markeringen i overskriften, mot `designregler.md` §3 | low | patch: bare ved 3 av 3. N3 |
| VG4 | Siste børsdag med «Velg dag» er ikke helt den samme siden | low | patch: forklart over |
| BH2 | Merket for en dag etter siste børsdag | low | avvist: `les_valg` avviser en dag etter siste rad med en beskjed (testet i 8.16) |
| BH3, ECH7 | `innhold` uten `dag`, eller `dag` uten `innhold` | low | avvist: ruta er eneste kaller og gir begge, og docstringen sier hva de betyr |
| BH4 | `sluttkurs` kan være None andre steder | low | avvist: ECH7 fant bare `aksje.html`, som tar høyde for det |
| BH5, VG6 | Testen for AD-7 fanger bare `vurder` | low | avvist: målingene i testene kan ikke regnes fra kursene, så en ny utregning ville vist andre tall (K3) |
| BH6, ECH5 | Bryteren godtar en umulig dato | low | avvist: `les_valg` gir 6 mnd og beskjeden (ECH5 prøvde 2026-02-30), og det er ingen omdirigering ut av siden |
| BH7 | Bryteren beholder ikke en periode | low | avvist: utenfor punkt a, som gjelder dagen, og slik før 8.16b |
| BH8 | Ingen test følger omdirigeringen | low | avvist: adressen er den samme som testene med `?dag=` henter |
| BH9 | Avtrykket for bildet endret uten endring i oversikten | low | avvist: `src/hjelpetekster.py` står bak bildet, og bildet er likt byte for byte (over) |
| BH10 | `bygg_dagen` for «Velg dag» brukes bare til merket i grafen | low | avvist: raden i vurdering leses én gang og deles med detaljen |
| BH11 | `antall_dager` for en valgt dag var ikke testet | low | avvist: ECH prøvde en grunn tidlig i serien og fikk «Trenger 51 dager …, fikk 11» |
| ECH3 | En lagret vurdering på en dag uten kurs viser signalet uten kurs | low | avvist: siden viser det som er lagret (AD-7), og sluttkursen sier «–» |
| ECH4 | Hjelpen til sluttkursen sier «siste børsdag i dataene» | low | utsatt: hjelpeteksten deles med oversikten. Føres som åpent punkt |
| ECH6 | Bryteren på siste børsdag valgt med «Velg dag» beholder `?dag=` | low | avvist: det er dagen brukeren valgte, og merket sier det etter neste henting |
| VG5 | Hjelpen sier ikke lenger 6 måneder for «Velg dag» | low | avvist: overskriften over grafen sier «6 måneder fram til» dagen |

## Boundaries

- Alt leses fra det som er lagret, og signalet regnes aldri på nytt (AD-7).
- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe.
