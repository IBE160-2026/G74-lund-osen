---
title: 'Story 10.2, PR H (10.2c): prompten versjon 2'
type: 'feature'
created: '2026-10-16'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e25beb6'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** I prøvekjøringen 16.10 kl. 22:26–22:27 (`malinger.md` §32) stoppet punkt 4 i kontrollen i FR-603 9 av 15 tekster, 8 på «skyldes» og 1 på «indikerer», også der ordet bare forklarte regelen.

**Beslutningen:** *Avgjort 2026-10-16, gruppens beslutning kl. 22:33* (under story 10.2 i `epics.md`, `f124fa7`): prompten får versjon 2, som ber modellen forklare regelen med «fordi» og ikke bruke «skyldes» eller «indikerer». Kontrollen endres ikke. Det bygges med en ny prøvekjøring på en fersk kopi av basen, og flettes før hentingen mandag 19.10. Er det ikke flettet da, går mandagens henting med `OSE_KI_TJENESTE=av`, så ingen dag får tekster med versjon 1.

*Lagt til 2026-10-16:* gruppen sa kl. 23:27 at det bygges og prøvekjøres i kveld, ikke lørdag (instruksjonen kl. 23:35).

**Approach:**
- `src/ki_prompt.py`: `PROMPTVERSJON = "2"`, og én ny linje under «Regler for teksten»: «- Når du forklarer regelen, bruk «fordi». Ikke bruk «skyldes» eller «indikerer».»
- `src/ki_kontroll.py` er uendret.
- `tests/test_ki_modell.py`: avtrykket for versjon 2 i `AVTRYKK`, og versjon 1 står. `test_regelen_forklares_med_fordi` krever linja under «Regler for teksten» og i prompten.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22).
- Prøvekjøringen går mot `data/db/ki-proeve-v2.db`, kopiert med skallet på main før grenen ble laget.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil.
- Flettes ikke uten ja fra gruppen.

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- H1: linja tatt ut av prompten.
- H2: teksten endret uten ny versjon.
- H3: «skyld(?:es|tes)» tatt ut av kontrollen.

**Utfallet** (på `f8a22d4`, i en fersk klone, med sha256 mot HEAD etter hver): H1 fanget av `test_regelen_forklares_med_fordi`, H2 av `test_versjonen_foelger_teksten`, H3 av `test_ordene_fr_603_nevner[skyldes-4]`, og H4, lagt til etter gjennomgangen (`indikerer` tatt ut av kontrollen), av `test_ordene_fr_603_nevner[indikerer-4]`.

## Gjennomgangen

Gjennomgang 16.10 på diffen `main...382c214`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 7) og Verification Gap (VG, 4). Rettingene står i `f8a22d4`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1, ECH, BH9 | Avtrykket for versjon 1 er ikke beskyttet, og teksten finnes bare i historikken | medium | patch: `test_avtrykket_for_versjon_1_staar`, og kommentaren sier at teksten står i `src/ki_prompt.py` på `77ebf31` |
| VG2 | «indikerer» står ikke i den håndskrevne lista, så den kunne tas ut av kontrollen uten at en test feilet | medium | patch: `("indikerer", "4")`, og mutant H4 |
| VG4, BH6, ECH | Testen låste versjon 2 | low | patch: `int(PROMPTVERSJON) >= 2` |
| BH7, ECH | Linja ble godtatt hvor som helst etter overskriften, og en manglende overskrift ga `IndexError` | low | patch: overskriften kreves, og linja kreves i blokka til første tomme linje |
| BH8 | Prompten med merket utenfor målingen var ikke prøvd | low | patch |
| VG3 | Ingen test viste at en forklaring med «fordi» består når sjekkene ga utslag | low | patch: `test_en_forklaring_med_fordi_bestaar` |
| BH12 | «Kontrollen er uendret» i koden | low | patch: «ble ikke endret i versjon 2» |
| ECH, BH1 | «fordi» kan brukes om en gjettet årsak som ingen liste fanger. «Kursen steg fordi markedet var urolig.» består kontrollen, prøvd 16.10 | medium | **må avgjøres av gruppen:** kontrollen endres ikke etter beslutningen kl. 22:33. Prøvekjøringen (§34) viser om modellen skriver slik |
| ECH, BH2 | Andre ord på lista, som «skyldtes» og «på grunn av», er ikke nevnt i prompten | low | defer: linja er ordrett beslutningen. Prøvekjøringen viser om det trengs |
| ECH, BH3 | Prompten nevner selv ordene den forbyr, og en modell kan gjenta dem | low | defer: samme grunn |
| BH13 | «bruk «fordi»» kan leses som et krav i hver tekst | low | defer: samme grunn |
| BH4 | Ingen grense for når versjon 2 er god nok | low | **må avgjøres av gruppen** med §34 |
| BH5 | Reserven med `OSE_KI_TJENESTE=av` mandag håndheves ikke av koden | avvist | beslutningen kl. 22:33 legger den i henteinstruksjonen, ikke i koden |
| ECH | En dag som har rader med versjon 1, får ikke rader med versjon 2 | avvist | `ose.db` har ingen rader i `ki_logg` (etterkontrollen 16.10), og kopien er laget av den |
| BH10 | Utfallet av mutantene var ikke ført | patch | «Utfallet» over |
| BH11 | Frontmatter uten `updated` | avvist | spesifikasjonene i `implementation-artifacts` har samme form som `spec-10-2b-teksten-i-hentekommandoen.md` |
| BH14 | Ingenting hindrer at prøvekjøringen skriver til `ose.db` | avvist | skriptet krever at fila heter `ki-proeve-v2.db`, og sha256 for `ose.db` sjekkes før og etter |
