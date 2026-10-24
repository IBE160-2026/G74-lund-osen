---
title: 'Story 10.2, 10.2e: prompten versjon 3'
type: 'feature'
created: '2026-10-24'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '153aba8'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** KI-teksten i versjon 2 får bare fortegnet for de tre sjekkene, styrken og retningen. Den kan ikke si hvor lenge signalet har vært slik, eller hvordan dagen var på børsen.

**Beslutningene** (under story 10.1 og 10.2 i `epics.md`):
- *2026-10-21 kl. 22:57 og 23:51:* den nye promptversjonen får hvor lenge signalet har vært slik, retningen på hovedindeksen og børsometeret, og bare våre egne resultater. Ingen kurser, volumer, prosenter eller forholdstall, heller ikke tallene som står på siden. Teksten kan vise til tallene på siden uten å gjenta dem, og hvert tall i teksten kontrolleres mot grunnlaget.
- *2026-10-24 kl. 15:50:* versjon 3 bygges og flettes i kveld, etter uka med logget drift med versjon 2 (19.–23.10).
- *2026-10-24 kl. 16:15:* a) hvor lenge signalet har vært slik, er børsdager på rad med samme retning og styrke, til og med dagen; b) fra børsometeret: hvor mange aksjer i lista som steg og falt fra børsdagen før, og om bransjen til aksjen steg eller falt i snitt. Begge er fortegn og antall.
- *2026-10-16 kl. 23:51 (2):* en ny promptversjon flettes når den består minst like mange tekster som versjonen før, i en prøvekjøring på samme dags data, og ingen tekst gjetter på en årsak utenfor regelen.

## Approach

**a) Grunnlaget** (`src/ki_grunnlag.py`). `ki_grunnlag` får `dagen=`, et `Dagsbilde`, og grunnlaget får disse feltene i tillegg:
- `dager`: et heltall fra 1. Det er børsdager på rad bakover fra dagen, etter børskalenderen, der den lagrede vurderingen har samme retning og samme styrke. Rekka stopper ved en vurdering med annen retning eller styrke, eller ved en grunn. Den stopper også ved en børsdag uten rad, også før første lagrede vurdering, og der kalenderen slutter. Da får grunnlaget `dager_merke: "minst"`, fordi det ikke er kjent hvordan signalet var før.
- `hovedindeksen`: `steg`, `falt` eller `uendret`, etter fortegnet på endringen slik den vises (`avrundet(..., "endring")`). Endringen er den samme som `indeksendring` i `hovedindeks.py` gir den stiplede linja på forsiden. Feltet mangler når indeksen ikke har en rad for dagen, eller ingen rad for børsdagen før. Indeksen velges som i appen: OSEBX når basen har den, ellers den basen har (DEMIX i demoen). Valget flyttes fra `app.py` til `valgt_indeks` i `hovedindeks.py`, så begge bruker det samme.
- `aksjer_steg` og `aksjer_falt`: aksjene i lista med kurs for dagen og en rad før, som har endring over eller under null slik den vises. Endringen er den samme som i børsometeret (`endring_i_prosent` på de to siste radene). Uendret og uten data telles ikke.
- `bransjen`: `steg`, `falt` eller `uendret` for snittet av endringen til aksjene i lista i samme bransje, som i børsometeret. Fortegnet tas av snittet slik det vises. Feltet mangler når ingen aksje i bransjen har en endring.

Fortsatt ingen kurser, volumer, prosenter eller forholdstall. Grunnlaget har bare heltall og tekst fra lukkede lister, og `_kontroller` sjekker de nye feltene. `ki_tekst.lag_ki_tekster` leser seriene, indeksen og vurderingene fra basen og gir `dagen` for hver aksje. `dagen=None` gir grunnlaget fra versjon 2, slik testene fra 10.1 bruker det.

**b) Prompten** (`src/ki_prompt.py`): `PROMPTVERSJON = "3"`. Reglene forklarer de nye feltene med ord. Teksten kan vise til tallene på siden uten å gjenta dem. Avtrykket for versjon 3 står i `AVTRYKK` i testen, og avtrykkene for versjon 1 og 2 står.

**c) Kontrollen** (`src/ki_kontroll.py`, FR-603):
- Et tall er lov bare når det står i grunnlaget som et antall (`styrke`, `dager`, `aksjer_steg`, `aksjer_falt`), eller er et av regelens faste tall. Fortegnene er ikke antall, som før.
- Sier teksten at hovedindeksen eller bransjen steg, falt eller var uendret, skal det stemme med grunnlaget. Mangler feltet, stoppes et slikt utsagn.

**d) Demoen og prøvekjøringen:**
- KI-tekstene i demoen lages på nytt med versjon 3 (`uv run python src/demo_ki.py`). Bildene og avtrykkene følger med.
- Prøvekjøringen (§43 i `malinger.md`) går som i §34. Bare KI-steget (`lag_ki_tekster`) kjøres mot `data/db/ki-proeve-v3.db` for børsdagen 23.10, med den ekte klokka, fra et skript utenfor repoet.
- Kopien har radene med versjon 2 fra kveldshentingen 23.10. Utfallet av dem føres som sammenligning på samme dags data. Så slettes de i kopien, og bare i kopien, med utløseren `ki_logg_slettes_ikke` tatt bort og satt inn igjen, før KI-steget kjøres.
- sha256 for `data/db/ose.db` er den samme før og etter.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22).
- Kopien ble laget med skallet på main kl. 20:11, før grenen. sha256 var lik `ose.db`: `e3184c07…f4a4`.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis kontrollen stopper tre eller flere av tekstene i §43, eller hvis versjon 3 består færre enn versjon 2 på 23.10 (beslutningen 16.10 kl. 23:51, 2).

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- M1: dagene telt bare på retningen.
- M2: kontrollen slipper et tall utenfor grunnlaget.

**Utfallet** (på `1795981`, kl. 20:33, med sha256 lik HEAD etter hver):
- M1, `(rad.retning, rad.styrke) != …` byttet med `rad.retning != vurdering.retning`, ble fanget av `test_dagene_naar_styrken_byttes`.
- M2, alle heltallene i grunnlaget og tallene 4–12 lagt til de lovlige, ble fanget av `test_2_tall_og_mengder_som_ikke_er_i_grunnlaget[Femdagssnittet ligger lavere.]`.

## Prøvekjøringen

§43 i `malinger.md`, kl. 20:31:25–20:31:36: 12 av 15 besto, og 3 ble stoppet, mot 15 av 15 med versjon 2 på samme dag. Alle tre ble stoppet på «Ingen sjekk ga …» om én sjekk, som styrkeregelen fra 10.2a leser som styrke 0, og utsagnet var riktig. Etter instruksjonen kl. 20:00 (steg 4, tre eller flere stoppet) og beslutningen 16.10 kl. 23:51 (2) flettes ikke grenen før gruppen har avgjort det. Med kontrollen etter gjennomgangen (`6f34ebd`) er utfallet det samme: 12 besto.

KI-tekstene i demoen ble laget på nytt med versjon 3: 11 av 13 besto, mot 13 av 13 med versjon 2. NLYS ble stoppet på «skyldes» og TROY på «Ingen sjekk ga utslag på interesse».

## Gjennomgangen

Gjennomgang 24.10 på diffen `df137b3..1795981` (commitene `ed68979` og `153aba8` på main og grenen), med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 12) og Verification Gap (VG, 3). Rettingene står i `6f34ebd`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH7 | Grenen gjør versjon 3 til standard og bytter demotekstene, men §43 sier at den ikke skal flettes | medium | **må avgjøres av gruppen:** grenen flettes ikke. Gruppen avgjør om versjon 3 rettes, eller legges bort |
| BH6 | «Ingen sjekk ga utslag på interesse» om én sjekk leses som styrke 0. Det stoppet alle tre i §43 og TROY i demoen, og utsagnet var riktig | medium | **må avgjøres av gruppen:** det er styrkeregelen fra 10.2a, og en retting endrer kontrollen etter prøvekjøringen |
| BH8 | Kontrollen sjekker ikke utsagn om én sjekk: tre tekster i §43 sier at interessen ga utslag der bare trenden ga det, og de besto | medium | **må avgjøres av gruppen**, og ført under «Åpent» |
| BH1, ECH6 | «Minst» om dagene sjekkes ikke: fem tekster i §43 og seks i demoen sier «minst» uten merket, og en tekst med merket kan si et eksakt antall | medium | **må avgjøres av gruppen:** en sjekk ville stoppe flere tekster i §43 og i demoen |
| BH9, VG2 | En feil ved lesingen av indeksen stoppet KI-teksten for alle aksjene | medium | patch: grunnlaget uten hovedindeksen, som forsiden, og `test_en_indeks_som_ikke_kan_leses_stopper_ikke_tekstene` |
| VG1 | Ingen test for valget av OSEBX når basen har en annen indeks | medium | patch: `test_hovedindeksen_er_osebx_ogsaa_med_en_annen_indeks` |
| BH3, ECH1 | «Alle aksjene» og «begge» ble lest som styrkens 3 og 2 | low | patch: egen ordliste for antallene, og «alle» og «begge» om aksjene stoppes |
| BH4, ECH3 | Perfektum, «har steget», «har sunket», «har gått opp», ble ikke lest | low | patch |
| BH5, VG3 | «Aksjen på børsen steg» ble lest som hovedindeksen | low | patch |
| BH2, ECH8, ECH12 | Tallene er lov som én mengde, og bare «N aksjer steg/falt» og «N (børs)dager på rad» knyttes til feltet sitt. «I sju dager» eller «og fem falt» sjekkes bare mot mengden | low | defer: punkt c) sier at et tall er lov når det står i grunnlaget. Ført under «Åpent» |
| ECH2 | Et antall uendrede aksjer stoppes alltid | low | defer: grunnlaget har ikke antallet |
| ECH7 | Sammensatte tallord over 20, som «tjueen», leses ikke | low | defer |
| ECH4, BH12 | Ord mellom feltet og verbet kan binde feltet til en annen setningsdel, som «Sammenlignet med bransjen falt aksjen» | low | defer: gir et stopp, ikke en feil som slipper gjennom |
| ECH5 | To mellomrom foran «Oslo Børs» | low | defer |
| ECH9 | Bransjen med bare aksjen selv | low | defer: står under «Åpent» fra før |
| BH10, ECH10 | Aksjene bruker forrige rad og indeksen forrige børsdag | avvist | som børsometeret (`bygg_rute`) og forsiden (`indeksendring`), slik spesifikasjonen sier |
| BH11 | Blandet med styrke 2 telles på rad selv om fortegnene bytter | avvist | gruppens svar kl. 16:15: samme retning og styrke |
| BH13, ECH11 | Uten OSEBX velges en annen indeks og kalles hovedindeksen | avvist | som forsiden og kursgrafen (`valgt_indeks`). Basen har bare OSEBX, og demoen DEMIX |
| BH14 | NLYS i demoen brukte «skyldes» igjen | low | ført i «Prøvekjøringen» over |
| BH15 | Tester for hullene over | low | testene er lagt til for funnene som er rettet |

## Åpent

- `bransjen` for en bransje med bare aksjen selv sier det samme som aksjens egen endring. Børsometeret merker den «1 aksje». Grunnlaget har ikke det merket.
- *Lagt til 2026-10-24:* om versjon 3 skal rettes og prøvekjøres på nytt, eller legges bort: styrkeregelen og «Ingen sjekk ga» (BH6), utsagn om én sjekk (BH8) og «minst» (BH1, ECH6).
- *Lagt til 2026-10-24:* tall som står i grunnlaget, men om et annet felt, sjekkes bare der teksten har formene «N aksjer steg/falt» og «N (børs)dager på rad» (BH2, ECH8, ECH12).
