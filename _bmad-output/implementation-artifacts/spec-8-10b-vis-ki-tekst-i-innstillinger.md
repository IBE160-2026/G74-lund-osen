---
title: 'Story 8.10b: «Vis KI-tekst» i Innstillinger'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'f2b0453d'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-10-innstillinger-oeverst.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Bygger på grenen for 8.10.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hvor står valget?** I dag er bryteren ved KI-teksten en informasjonskapsel (`ose_ki`, FR-601). *Forslag:* valget står i tabellen `innstilling` fra 8.10, som `vis_ki_tekst`. Bryteren ved KI-teksten og valget i Innstillinger skriver begge raden, så de viser alltid det samme. Kapselen skrives fortsatt, og leses bare når basen ikke har raden ennå (en base fra før 8.10b, eller en side uten base), så valget ikke går tapt ved overgangen.
2. **Teksten.** *Forslag:* «KI-tekst» med «Vis KI-tekst» og utdragets tekst: «Noen setninger om dagen og om hver aksje, skrevet av en språkmodell når kursene hentes. Merket «Laget av KI». Hver KI-tekst har også sin egen bryter.» Før 10.6 er flettet finnes bare teksten om hver aksje, men teksten står ordrett.
3. **Demoen.** *Forslag:* valget lagres i demobasen, som «Vis hjelp».

## Intent

**Problem:** KI-teksten kan bare slås av ved teksten, og valget står i en kapsel, ikke i basen med «Vis hjelp».

**Avgjørelsene:** story 8.10b i `epics.md` (13.10), FR-110 og FR-601 i `prd.md`, svaret 08.11 kl. 12:39 og §4 i `designutdrag-2026-11-08.md`.

## Delene

### A) «Vis KI-tekst» i Innstillinger

I samme tabell som «Vis hjelp». Skjemaet skriver bare `innstilling` (AD-3), og ingen kall (AD-10).

### B) Bryteren ved KI-teksten og Innstillinger viser det samme

`/ki` skriver raden `vis_ki_tekst`, og siden leser den. Kapselen er bare reserve, se spørsmål 1.

**Ville feilet hvis:** bryteren ved KI-teksten og Innstillinger kunne vise hver sin verdi.

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `8-10b-vis-ki-tekst`, i worktreen `G74-lund-osen-8-10b`, fra grenen for 8.10 (`f2b0453d`).

- **Filene:** `les_rader` i `src/innstillinger.py`, `_ki_er_paa` og `_lagre_ki` i `src/app.py` (aksjesiden, Innstillinger og `/ki` leser og skriver samme rad), og «KI-tekst» i `src/templates/innstillinger.html`. `docs/hjelp.md` sier at de to viser det samme.
- **Avvik:** ingen fra delene. Testen fra 8.10 som avviste «vis_ki_tekst», avviser nå et ukjent navn.
- **Tester («Ville feilet hvis» i hver):** `tests/test_innstillinger_ki.py`.
- **Hele settet,** alene: kl. 19:07:33–19:18:30, 4670 bestått, 24 hoppet over og 0 feilet. Alle bildene ble tatt på nytt og er byte for byte de samme.
