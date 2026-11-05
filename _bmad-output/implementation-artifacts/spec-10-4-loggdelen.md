---
title: 'Story 10.4: Loggdelen, uka 29.10–04.11'
type: 'docs'
created: '2026-11-05'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '2b3ea0f9'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

## Intent

Story 10.4 har to deler (`epics.md`, story 10.4, «Kontroll»): `KILogg` over minst én ukes drift, med hvor ofte KI-teksten sa noe regelforklaringen ikke sa med ord og hvor ofte den bare gjentok, og brukertesten med én person. Etter gruppens svar 5.11 kl. 12:23 og 12:24 telles loggdelen nå, for uka 29.10–04.11, de sju første dagene jobben gikk av seg selv. Delen med en person venter på brukertesten. Denne spesifikasjonen gjelder bare loggdelen.

Ingenting i `src/` eller `tests/` er endret. `data/db/ose.db` ble åpnet skrivebeskyttet (`mode=ro`), med sha256 `58b893ebfe2799a226e8fa8e0bb690522c33019ae8c27dff02bf6a2b56bfc1be` før og etter. Her står bare antall, datoer, symboler og klokkeslett (regel 16), og ingen KI-tekst ordrett.

## Hva som ble talt

Radene i `ki_logg` med `dato` fra 2026-10-29 til 2026-11-04. Alle 105 er av slaget `aksje`. Det finnes ingen rader av slagene `melding` eller `dag` i basen. Alle 105 besto kontrollen (FR-603), og 0 ble stoppet. Hver rad ville også blitt vist etter reglene i `bygg_ki_visning` i `src/ki_visning.py`: grunnlaget stemmer med vurderingen (FR-602), og vakta finner ingen av ordene (NFR-06). Modellen er `gemma4:e4b`, lokal, med `modell_id` `dc35e8d9c606`, og promptversjonen er `3` alle dagene. Hver av de fem børsdagene har 15 tekster, én for hver aksje. 31.10 og 01.11 er helg, uten kurser og uten rader. Tallene per dag står i en linje under R29 i §7 i `prd.md`.

*Rettet 2026-11-05 (instruksjonen kl. 16:09):* «Alle 105» i avsnittet over skal være «alle 75». `ki_logg` har 75 rader for 29.10–04.11, 15 for hver av de fem børsdagene, og ingen for helgen 31.10 og 01.11. 105 er 7 × 15, de sju dagene i uka ganget med 15. Tabellen under og klassifiseringen gjelder de 75 og er ikke endret. Rettelsen står også under R29 i §7 i `prd.md`.

## Regelen

Regelforklaringen på aksjesiden er det `regelen` i raden sier: hvilke sjekker som ga +1, 0 eller -1, styrken og retningen. Hver KI-tekst for en aksje i uka som besto kontrollen, får én klasse:

- **gjentar:** teksten sier bare det regelforklaringen sier. Den nevner retningen, styrken eller hva trenden, bevegelsen og interessen ga, eller en del av dette, og ingenting annet.
- **sier mer:** teksten sier noe med ord som regelforklaringen ikke sier, for eksempel om bransjen, hovedindeksen eller hvor mange aksjer som steg eller falt (feltene i grunnlaget som regelforklaringen ikke har), eller en sammenheng mellom sjekkene.
- **usikker:** ellers, for eksempel når en setning kan leses begge veier.

Klassifisert av Claude 05.11, ferdig før kl. 15:46 (`date`), ved å lese hver av de 75 tekstene ved siden av `regelen` og resten av grunnlaget. Som kontroll ble ordene i alle tekstene talt: de 75 tekstene er 18 ulike tekster, og de bruker til sammen 20 ulike ord. Ingen av dem er et ord for bransjen, hovedindeksen, antallet aksjer eller et tall. Klassifiseringen er ikke gjort av en person.

## Antallet i hver klasse

| Dag | Tekster som besto | gjentar | sier mer | usikker |
|---|---|---|---|---|
| 29.10 | 15 | 15 | 0 | 0 |
| 30.10 | 15 | 15 | 0 | 0 |
| 02.11 | 15 | 15 | 0 | 0 |
| 03.11 | 15 | 15 | 0 | 0 |
| 04.11 | 15 | 15 | 0 | 0 |
| **Totalt** | **75** | **75** | **0** | **0** |

Usikre: ingen, så ingen symboler eller datoer å føre.

## Funnet

Alle 75 tekstene gjentar regelforklaringen med andre ord. Ingen nevner bransjen, hovedindeksen eller hvor mange aksjer som steg eller falt, selv om grunnlaget har dem. Ingen sier heller styrken som tall. At KI-teksten bare gjentar, er et funn til refleksjonsrapporten, ikke en feil (`epics.md`, story 10.4: «Et funn om at KI ikke hjelper, føres som funn og ikke som feil»).

## Det som gjenstår i 10.4

- Delen med en person: samme person og samme aksje, først med KI av (8.1) og så på (10.4), med svarene ordrett. Den venter på brukertesten (`docs/brukertest.md`).
- Funnet skal inn i refleksjonsrapporten.

10-4 står som `in-progress` i `sprint-status.yaml`, fordi loggdelen er talt og delen med en person gjenstår.
