---
title: 'Story 9.23: «51 børsdager» i koden og norsk tid i morgensjekken'
type: 'code'
created: '2026-11-19'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'beb6aa15'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-22-morgensjekken-og-to-rettinger.md'
---

Skrevet 19.11 etter instruksjonen om de to spørsmålene fra 9.22 (limt inn
kl. 10:40 i `docs/ai-prompts/2026-11-19.md`) og gruppens svar 19.11 kl. 09:59.
Rådet anbefalte å vente med begge til kodegjennomgangen etter brukertest 2, men
gruppen valgte å ta dem nå. Neste ledige nummer i Epic 9 etter 9.22 er 9.23.
Worktreen er `G74-lund-osen-9-23`, på grenen `9-23-boersdager-og-norsk-tid`, fra
`origin/main` (`beb6aa15`). Svarene står på main, ved spørsmålene i
spesifikasjonen for 9.22 og ved punktene i `issues.md` (steg 1 i instruksjonen).

## Storyen

Som **gruppen som leser koden og morgensjekken** vil vi at kommentarene sier
«børsdager» der FR-101 gjør det, og at klokkeslettene i morgensjekken står i
norsk tid også når vi kjører den på Windows, så vi ikke må regne om en time.

**Oppfyller:** spørsmål 1 og 2 fra 9.22 (svaret 19.11 kl. 09:59) og de to
punktene i `issues.md` · **Begrenses av:** regel 3, 16, 20 og 22; ingen bilder
og ingen ny migrasjon, og den planlagte oppgaven «Morgensjekk OSE Signal»
endres ikke

**Avhenger av:** 9.22. **Én økt:** ja.

## Det som gjøres

1. **«51 handelsdager» blir «51 børsdager»** i kommentaren øverst i
   `src/fetch_prices.py` og i docstringen i `tests/test_fetch_prices.py`, og
   bare der. «Handelsdag» er brukt med vilje ellers og endres ikke: i navn som
   `MINST_HANDELSDAGER`, i kolonnen `handelsdager` i basen og i regelen om at
   halve handelsdager er børsdager. Historikken endres heller ikke.
2. **Klokkeslettene fra git i morgensjekken** står i norsk tid, også på
   Windows, der `TZ` i miljøet ikke virker for git. Det gjelder «HEAD paa
   GitHub» og de andre klokkeslettene fra git i utskriften. På GitHub er
   utskriften som før.
3. Hver retting får en test som feiler før rettingen.
