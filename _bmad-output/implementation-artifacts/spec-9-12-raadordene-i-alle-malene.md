---
title: 'Story 9.12: rådordene i alle malene, taggene i CI og technology.md'
type: 'chore'
created: '2026-11-12'
status: 'review'
route: 'dispatch'
baseline_commit: 'a93c668f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-11-prd-etter-tilbakemeldingen.md'
---

Skrevet 12.11 i vinduet som gjør PRD-en, etter tillegg 2 til 9.11 (limt inn kl.
20:10, føres i `docs/ai-prompts/2026-11-12.md`) og gruppens svar 12.11 kl. 20:04
og 20:06. Rådet anbefalte 9.12. Worktreen `G74-lund-osen-9-12`, grenen
`9-12-raadordene-i-alle-malene`, fra `origin/main` (`a93c668f`).

## Spørsmål til gruppen, med forslag

1. **Nummeret.** *Forslag:* 9.12, neste ledige i Epic 9 etter 9.11.
2. **Hva testen leser.** *Forslag:* alle malene i `src/templates/` uten
   kommentarer og kode (`{% %}`, navn i `{{ }}`), men med strengene i `{{ }}`.
   I tillegg alle hjelpetekstene (uten kildene), stegene i «Vis meg rundt»,
   omvisningen og strengene i `src/static/hjelp.js`. Lista er `RAAD` i
   `src/ki_kontroll.py`, den samme som kontrollen av KI-tekstene bruker.
3. **Unntakene**, som står i testen med grunn. *Forslag:*
   - En setning der «ikke» står foran treffet, som «ikke et råd» og «sier ikke om
     du bør kjøpe eller selge» (NFR-06, FR-108).
   - Ordene for notatene om tenkte kjøp og salg: «tenkt kjøp», «tenkte kjøpet»,
     «Tenkt kjøp og salg», «kjøpet», «Kjøpsdag», «kjøpsdagen», «Salgsdag» og «et
     kjøp eller salg». Grunnen er 8.21, 8.24 og svaret 12.11 kl. 10:16 under 8.27
     på grenen for 8.27, som er lest der.
   - En test feiler hvis et unntak ikke lenger brukes.
4. **Ekte råd.** Testen fant ingen. Alle de 52 treffene før unntakene var
   nektende setninger, eller notatene om tenkte handler. *Forslag:* ingen
   endring i malene.
5. **Taggene i CI.** *Forslag:* `fetch-depth: 0` i jobben `pytest` i
   `tester.yml`, så CI har hele historikken og taggene. Testen av endringsloggen
   mot taggen står i `tests/test_prd_9_11.py` på grenen for 9.11. Når 9.11 er
   flettet, og main er flettet inn her, kjører den i CI på denne grenen.
6. **technology.md.** Fila er lest. Den beskriver «Website V2» hos Pytagoras
   Forlag, ikke OSE Signal. *Forslag:* lenken står under «Dokumentene», rett
   under arkitekturen, og sier det. Avtrykket av «Dokumentene» i
   `test_docker.py` er nytt.
7. **Punkt 26 i §8.** *Forslag:* når 9.11 er flettet og main er flettet inn,
   lukkes punktet i `prd.md`. Linja om det føres under «Endringer etter 12.11» i
   endringsloggen, og NFR-06 sier at testen finnes.
8. **Flettingen.** *Forslag:* etter 9.11, når gruppen har sagt ja (tillegg 2).

## Delene

### A) Testen
`tests/test_raadordene_9_12.py`.
- **Ville feilet hvis:** en mal, en hjelpetekst, omvisningen eller `hjelp.js`
  hadde et ord fra rådlista utenfor de to unntakene; testen ikke leste alle
  malene; et ekte råd i eksemplene slapp gjennom; eller et unntak ikke ble brukt.

### B) Taggene i CI
`fetch-depth: 0` i jobben `pytest` i `.github/workflows/tester.yml`.

### C) technology.md i README-en
Én linje under «Dokumentene», og avtrykket i `tests/test_docker.py`.

## Grenser

Ingen API-kall. `src/` er ikke endret. `data/db/ose.db` røres ikke.

## Bygget 12.11
