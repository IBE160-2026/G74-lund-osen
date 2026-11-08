---
title: 'Story 8.10: Innstillinger øverst, med «Vis hjelp»'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'f09e0c6f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). 8.10b bygger på grenen for denne.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hvilken gren?** Storyen krever en ny migrasjon (AD-16), og 2.11 og 2.12 bruker alt `0009` og `0010`, som ikke er flettet. *Forslag:* 8.10 bygges på grenen for 2.12, med `0011_innstillinger.sql`, så migrasjonene kommer i rekkefølge når de flettes: 2.11, 2.12, 8.10 og 8.10b.
2. **Tabellen.** *Forslag:* `innstilling` med én rad per valg (`vis_hjelp`, og `vis_ki_tekst` fra 8.10b), verdien 0 eller 1. Ingen rad betyr på. Webserveren er eneste skriver, som for Min liste (føringen 30.09 under AD-3).
3. **Hva gjør «Vis hjelp» av?** *Forslag:* alle «?»-knappene og hjelpevinduene på sidene tas bort. «Slik leser du tabellen» og fotnotene står, fordi de ikke er hjelp bak «?».
4. **Hvor står Innstillinger?** *Forslag:* knappen «Innstillinger» i stripa etter «Min liste», som i utdraget §4, og en egen side `/innstillinger` med skjema, som virker uten skript. «Vis meg rundt» (8.9) er ikke med.
5. **Demoen.** *Forslag:* valget virker i demoen og lagres i demobasen, som merkingen i Min liste.

## Intent

**Problem:** hjelpen bak «?» kan ikke slås av, og FR-110 sier at «Vis hjelp» og «Vis KI-tekst» står i «Innstillinger» øverst, lagret i basen, så valget gjelder alle sidene og huskes.

**Avgjørelsene:** story 8.10 i `epics.md` (08.10, delt 13.10: «Vis KI-tekst» kommer i 8.10b), FR-110 i `prd.md`, svaret 08.11 kl. 12:39 («Innstillinger bare med hjelp og KI-tekst») og §4 i `designutdrag-2026-11-08.md`.

## Delene

### A) Tabellen `innstilling` (`0011_innstillinger.sql`)

Én rad per valg, `navn` og `verdi` (0 eller 1). Ingen rad betyr på. `navn` kan være `vis_hjelp` og `vis_ki_tekst`, så 8.10b bruker samme tabell (spørsmål 2).

**Ville feilet hvis:** valget ikke overlevde en omstart, eller tabellen godtok et annet navn eller en annen verdi.

### B) Siden «Innstillinger»

Knappen i stripa etter «Min liste», og siden `/innstillinger` med «Hjelp» og «Vis hjelp», teksten fra utdraget §4, og nederst «Valgene gjelder alle sidene og lagres på denne maskinen.» Skjemaet skriver bare `innstilling` (AD-3), og ingen kall (AD-10).

### C) «Vis hjelp» av

Ingen «?»-knapp og ingen hjelpevinduer på noen side (spørsmål 3).

**Ville feilet hvis:** en side viste «?» med hjelpen av, eller valget gjaldt bare én side.

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `8-10-innstillinger-oeverst`, i worktreen `G74-lund-osen-8-10`, fra grenen for 2.12 (`f09e0c6f`).

- **Filene:** `src/migrasjoner/0011_innstillinger.sql`, `src/innstillinger.py` (lesing og skriving), rutene `/innstillinger` i `src/app.py`, `src/templates/innstillinger.html`, knappen i `_ramme.html`, og `_hjelp.html`, der «?» og vinduet bare står med hjelpen på. `docs/hjelp.md` har «Hva er «Innstillinger»?».
- **Avvik:** ingen fra delene. «Vis KI-tekst» kommer i 8.10b, i samme tabell.
- **Tester («Ville feilet hvis» i hver):** `tests/test_innstillinger.py`. Testene som talte tre knapper i stripa, teller fire, og versjonen er 11.
- **Bildene:** alle sju i `docs/appen/` og bildet av «Din egen liste» viser knappen og er tatt på nytt med DevTools-protokollen, med de samme høydene.
- **Hele settet,** alene: kl. 17:59:50–18:10:23 ga 8 feil (tre knapper i stripa i fire tester, og «min_liste» i en kommentar i 0011), rettet. Kl. 18:11:20–18:21:28 ga 3 feil i avtrykkene for bildene, rettet. Kl. 18:21:49–18:32:30: 4657 bestått, 24 hoppet over og 0 feilet.

## Mutantene

På `d9f2aaf5` seks: A (tabellen godtar en annen verdi), B («?» står med hjelpen av), B2 (hjelpevinduet står), C (knappen mangler i stripa), D (valget lagres ikke) og E (en annen side kan endre), med 1 test hver. Alle ble fanget, og hver fil var lik HEAD etterpå.

## Gjennomgangen 08.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 10 funn, Edge Case Hunter 5 og Verification Gap 8.

**Høy**
- *BH1 og VG1, rettet.* Da tre knapper ble til fire i `tests/test_min_liste.py`, havnet sjekken av `aria-current` på aksjesiden og aksjen uten kurser i en kommentar, så den var borte (regel 13). Den er satt tilbake.

**Middels**
- *ECH1, rettet.* En base eller demobase fra før 0011 fikk «før basen finnes». Nå sier siden at den må hentes eller lages på nytt.
- *BH5 og ECH2, rettet.* En POST med basefeil gir feilsiden, som GET.
- *VG2, rettet.* En test leser valget i fila med en egen tilkobling og en ny klient, og svaret har ingen informasjonskapsel.
- *VG3, rettet.* En test viser at bare `innstillinger.py` skriver tabellen, og at en POST bare endrer `innstilling` og en GET ingenting.
- *VG4, rettet.* Testen leser rutene i `app.py`, ikke bare modulen.
- *BH2, BH3 og BH4, delvis rettet.* Testen dekker nå også «Følg en aksje» og «Alle» i Min liste, og Edge Case Hunter fant ingen «?» utenfor makroen. At makroen viser hjelpen når valget mangler (uten «with context»), er ført.

**Lav**
- *Rettet:* BH6 og ECH5 (én lesing per side), BH7 og ECH3 (8.10 lagrer bare «Vis hjelp»), BH8 og VG8 (et avvist valg endrer ingenting), BH10 (docstringen med versjonen), ECH4 (README-en har knappen), VG5 (testen i demoen), VG6 og VG7 (flere sider og hele teksten).
- *Ført:* BH9 (fokuset etter trykket står øverst på siden).
- **Etter gjennomgangen:** hele settet alene kl. 18:41:38–18:52:01 ga 1 feil (en test leser «og børsometeret som et kart, med knappene» i README-en), rettet. Kl. 18:53:04–19:04:10: 4664 bestått, 24 hoppet over og 0 feilet.
