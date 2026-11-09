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

## Mutantene

På `5f98fe88` fire: A (bryteren ved teksten skriver ikke raden) 1, B (siden leser bare kapselen) 2, C (Innstillinger kan ikke lagre KI-teksten) 2 og D (uten rad gjelder ikke kapselen) 1 test. Alle ble fanget, og hver fil var lik HEAD etterpå.

## Gjennomgangen 08.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 8 funn, Edge Case Hunter 5 og Verification Gap 6. Ingen høye.

**Middels**
- *BH1, ECH1 og ECH2, rettet.* Kunne raden ikke skrives (låst base eller basefeil), satte `/ki` kapselen likevel, og raden, som går foran, viste den gamle verdien. Nå setter ikke bryteren kapselen da, og siden sier at basen ikke kan brukes (503), så de to aldri viser hver sin verdi. Før 8.10b virket bryteren også mens basen var låst; det er prisen for ett valg i basen (`test_kan_valget_ikke_skrives_endres_ingenting`).
- *BH3 og ECH3, åpent til flettingen.* 10.6 (PR #122) leser kapselen direkte i `_boersdagen`. Når begge er flettet, må `_boersdagen` bruke `_ki_er_paa()`, ellers kan forsiden og aksjesiden vise hver sin verdi. Det gjøres i flettingen av den som kommer sist, og står i issues.md.
- *VG1, rettet.* `test_uten_tabellen_virker_bryteren_med_kapselen`.
- *VG3, rettet med teksten over.* Hjelpen sier at et trykk endrer begge; når basen ikke kan skrives, endres ingen av dem.

**Lav**
- *Rettet:* BH8 og VG5 (raden sjekkes også ved «på»), VG2 (kapselen fra Innstillinger).
- *Ført:* BH2 og ECH4 (`/ki` åpner, og en ny installasjon lager, basen), BH4 (en forbigående lesefeil gir kapselen), BH5 (kapselen deles av demoen og den ekte versjonen på samme port), BH6 (med en base fra før 0011 gjelder bare kapselen), BH7 (Origin som for de andre skjemaene), VG4 og VG6.
- **Etter gjennomgangen:** hele settet alene kl. 19:25:46–19:36:23: 4673 bestått, 24 hoppet over og 0 feilet. Bildene ble tatt på nytt og er byte for byte de samme.
- **Mutantene på nytt** på `b870f693`, med E «kapselen settes når raden ikke kan skrives»: A 2, B 2, C 3, D 1 og E 1 test. Alle fem ble fanget, og hver fil var lik HEAD etterpå.

## Bygget og ikke flettet

Grenen `8-10b-vis-ki-tekst` er ikke flettet. Den bygger på 8.10 (PR #125), og flettes etter 2.11, 2.12 og 8.10. Flettes 10.6 (PR #122) også, må `_boersdagen` bruke `_ki_er_paa()` (BH3, ECH3).

*Svar 2026-11-08 kl. 22:53 (gruppens svar):* forslagene i spørsmål 1–3 er godtatt, og rådet anbefalte det. BH3 og ECH3 (middels) rettes nå som 10.6 er flettet: `_boersdagen` bruker `_ki_er_paa()`, med en test. Svaret er ført etter instruksjonen kl. 00:30 i `docs/ai-prompts/2026-11-09.md`.

*Lagt til 2026-11-09 (instruksjonen kl. 00:30 i `docs/ai-prompts/2026-11-09.md`, steg 4):* 8.10 (med 2.12 og main, også 10.6) er flettet inn. BH3 og ECH3 er rettet: `_boersdagen` i `src/app.py` leser på eller av med `_ki_er_paa()`, som aksjesiden. `TestBoersdagen` i `tests/test_innstillinger_ki.py` viser at bryteren på oversikten, ved teksten og i Innstillinger sier det samme som raden i basen når kapselen sier noe annet. Mutanten «`_boersdagen` leser kapselen direkte» fikk begge tilfellene til å feile, og `src/app.py` var lik som før etterpå. Med det står ingen funn på middels eller over åpne.

