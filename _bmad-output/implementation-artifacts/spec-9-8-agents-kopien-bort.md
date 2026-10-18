---
title: 'Story 9.8: kopien .agents/skills/ tas bort'
type: 'chore'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f05e1d7'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** BMAD ble satt opp for Claude Code og Codex 15.09 (`59a90a2`), så de samme skillene ligger både i `.claude/skills/` og i `.agents/skills/`, 242 filer hver, med likt innhold (sjekket fil for fil med `cmp` 18.10). Gruppen bruker bare Claude Code. I tillegg har `.gitignore` en del for Next.js fra malen, og `.env.example` sier at `EODHD_API_KEY` er den eneste variabelen og at en full henting bruker 15 kall. Story 9.8 i `epics.md` (gruppens svar 18.10 kl. 00:03).

**Grunnlaget:** instruksjonen 18.10 kl. 11:40, steg 2 og 3. PR-en flettes når vilkårene i steg 4 holder.

## Planen, én commit per punkt

1. Storyen i `epics.md` og denne spesifikasjonen.
2. a) `git rm -r .agents/`. Lokalt fantes ingen `__pycache__` under `.agents/`, så mappa er borte etter commiten.
3. b) `- codex` tas ut under `ides` i `_bmad/_config/manifest.yaml`.
4. c) «Mappestruktur» i README-en nevner `_bmad/` og `.claude/skills/`, og `.agents/` tas ut av unntaket for `.csv`, `.json` og `.jsonl` i `.github/scripts/morgensjekk.py`.
5. d) To tester i `tests/test_ryddighet.py`: ingen fil under `.agents/` er sporet i git (hoppes over uten git), og manifestet har bare `claude-code` under `ides`.
6. e) `.gitignore`: delen for Next.js tas bort, utenom `node_modules/`, `dist/` og `build/`, og kommentarene skrives på norsk.
7. f) `.env.example`: tre variabler, og 16 av de 20 kallene.

*Rettet 2026-10-18 (gjennomgangen, BH12):* setningen i punkt 2 om at mappa er borte, ble skrevet før commiten. Den er sjekket etter commiten: `ls .agents` ga «No such file or directory».
*Rettet 2026-10-18 (gjennomgangen, BH6):* punkt 5 sier «To tester». Det ble tre i punkt d, og åtte etter gjennomgangen. Storyen sier «En test», ordrett fra instruksjonen.
*Rettet 2026-10-18 (gjennomgangen, BH1):* README-linja i punkt 4 står i commiten for punkt 2 (`151e309`), så slettingen og README-en endres i samme commit (regel 19). Grenen var ikke pushet og ble bygget på nytt fra `91bfe55`, med samme tre som før (`git diff` mellom gammel og ny head var tom). Punkt 4 er nå bare morgensjekken (`bb00787`).

## Avgjort i spesifikasjonen

- **Tre variabler:** koden leser `EODHD_API_KEY` (`src/fetch_prices.py`), `OSE_KI_TJENESTE` og `OSE_KI_OLLAMA_URL` (`src/ki_tekst.py`). `OSE_DEMO` og `OSE_I_DOCKER` (`I_DEMO` og `I_DOCKER` i `src/app.py`) settes av compose, Dockerfile og demoen, ikke i `.env`.
- **16 kall:** 15 aksjer og hovedindeksen, ett kall hver (docstringen i `src/fetch_prices.py`, story 2.8).
- **Manifestet leses som tekst,** ikke med PyYAML, som ikke er en avhengighet. Testen leser lista under `ides:` til neste nøkkel på toppnivå.
- *Lagt til 2026-10-18 (gjennomgangen, BH2 og VG4):* at en ny BMAD-installasjon leser `ides` fra manifestet, er ikke slått opp. Installasjonskoden ligger ikke i repoet, og den finnes ikke i den globale npm-mappa på maskinen. Testene sier derfor bare at manifestet oppgir Claude Code. Kommer kopien tilbake, feiler `test_det_finnes_ingen_agents_i_rotmappa`, også uten git.
- *Lagt til 2026-10-18 (gjennomgangen, BH3):* `.agents/` legges ikke i `.gitignore`. Det ville skjult en ny kopi i stedet for å si fra, og mutant S1 med `git add` ville trengt `-f`. Testen for mappa går uten git.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22).
- `.claude/skills/` endres ikke.

## Mutantene

Én om gangen med `-x` på `tests/test_ryddighet.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver. `git status` var tom etter hver. S1 og S2 er fra instruksjonen, og ble fanget på `9a5dfe6`, før gjennomgangen, og på nytt på `a0b44a1`. S3–S8 er ett for hvert funn med dom medium som kan prøves med en mutant, fanget på `a0b44a1`:
- S1, `.claude/skills/bmad-help/SKILL.md` kopiert til `.agents/skills/bmad-help/` og lagt inn med `git add`, så tatt ut med `git rm --cached` og slettet: `test_ingen_fil_under_agents_er_sporet` (på `a0b44a1` først `test_det_finnes_ingen_agents_i_rotmappa`, og sporingstesten alene med `-k sporet`). Indeksen var lik HEAD etter (sha256 av `git ls-files -s`).
- S2, `  - codex` tilbake under `ides` i manifestet: `test_manifestet_har_bare_claude_code`.
- S3, samme kopi i `.agents/` uten `git add` (BH3): `test_det_finnes_ingen_agents_i_rotmappa`.
- S4, `ides: [claude-code,\n  codex]` i manifestet (ECH1): `test_manifestet_har_bare_claude_code`.
- S5, `.agents/skills/` tilbake i «Mappestruktur» (VG5): `test_mappestrukturen_nevner_bmad_og_claude_skills_ikke_agents`.
- S6, `.agents/` tilbake i unntaket i morgensjekken (VG5): `test_lekkasjesjekken_unntar_ikke_agents`.
- S7, `.next/` tilbake i `.gitignore` (VG7): `test_gitignore_uten_nextjs_men_med_node_og_byggemappene`.
- S8, «bruker 15 av de 20» i `.env.example` (VG9): `test_env_example_har_variablene_koden_leser_og_kallene_en_henting_bruker`.

S5 ble først ikke brukt, fordi erstatningen i skallet ikke traff, og testene besto. Mutanten ble kjørt på nytt fra en skriptfil og ble fanget. Den overlevde ikke.

## Gjennomgangen

Gjennomgang 18.10 på diffen `f05e1d7..9a5dfe6`, med de 242 slettede filene som en liste. Linsene var Blind Hunter (BH, 13 funn, bare diffen), Edge Case Hunter (ECH, 8, der ECH5–ECH8 ikke fant noen feil) og Verification Gap (VG, 11, der VG1, VG10 og VG11 fant påstandene riktige). Sju funn har dom medium, og alle er rettet. Rettingene står i `151e309` (BH1, grenen bygget på nytt), `b87cd6c`, `9efab07`, `bac16b9`, `3665db2` og `a0b44a1`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | `.agents/` ble slettet i a, men README-linja ble rettet først i c (regel 19) | medium | patch: grenen bygget på nytt før push, README-linja i `151e309` |
| BH2, VG4 | «så en ny BMAD-installasjon ikke legger kopien inn igjen» sto uten oppslag i commit b og i docstringen | medium | patch: meldingen i b, docstringene og «Avgjort i spesifikasjonen» sier at det ikke er slått opp |
| BH3 | Ingen sjekk uten git, så en lokal kopi ble ikke funnet før `git add` | medium | patch: `test_det_finnes_ingen_agents_i_rotmappa`. S3 |
| ECH1, BH4 | `ides()` slapp `codex` gjennom i en flytliste over flere linjer | medium | patch: flytlister over flere linjer. S4 |
| VG5 | Punkt c var bare sjekket for hånd | medium | patch: to tester. S5 og S6 |
| VG7 | Punkt e var bare sjekket for hånd | medium | patch: testen for mønstrene og de engelske overskriftene. S7 |
| VG9 | Punkt f var bare sjekket for hånd | medium | patch: testen tar variablene og kallene fra koden. S8 |
| ECH2, BH5 | BOM, kommentar etter tabulator, `---` og `ides: codex` ga feil verdier | low | patch. `#` inne i anførselstegn, et mapping-element og en tom strek gir fortsatt en falsk feil, aldri en falsk bestått |
| ECH3 | `.agents` uten skråstrek (fil, lenke eller submodul) slapp gjennom | low | patch |
| BH9, VG8 | «`*.log` dekker loggene for npm, yarn og pnpm» stemte ikke for rullerte logger | low | patch: kommentaren sier det |
| BH10 | «Node og byggemapper fra malen» skjulte at `dist/` og `build/` også er Python-pakkingens | low | patch: kommentaren sier det |
| BH11 | «tre variabler å sette», men bare én må ha verdi | low | patch: `.env.example` sier hvilken hentingen trenger |
| BH6 | «En test», «To tester», og tre i diffen | low | patch: Rettet-linje over. Storyen er ordrett fra instruksjonen |
| BH12 | Setningen om at mappa er borte, ble skrevet før commiten | low | patch: Rettet-linje over |
| BH7, VG3 | At diffen under `.claude/skills/` er tom, er ikke sjekket av en test | low | avvist: en test mot main gir ikke mening etter flettingen. Sjekket med `git diff main -- .claude/skills` (0 linjer), og står i Utført-linja |
| VG2 | `cmp`-kjøringen står ikke i dagsfila | low | avvist: VG fant innholdet likt med blob-hashene, og kjøringen står i Utført-linja |
| BH8 | Commit e blander mønstrene og kommentarene | low | avvist: punkt e i instruksjonen er én sak med begge deler |
| BH13 | Testen for manifestet har ingen skipif | low | avvist: manifestet er sporet og følger med ZIP-fila fra GitHub. Mangler det, er en feil riktig |
| ECH4 | `safe.directory` gir en feil i stedet for skip | low | avvist: samme mønster som `test_ingenting_av_det_er_sporet_i_git` fra før, og ikke en del av storyen |
| VG6 | At mutantene er kjørt, måtte stå et sted | low | avvist: de står under «Mutantene» |
