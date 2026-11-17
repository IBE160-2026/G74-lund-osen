---
title: 'Story 9.20: PRD-en mot faglærers rubrikk'
type: 'docs'
created: '2026-11-17'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'e5673cbb'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd-endringslogg.md'
  - '{project-root}/.claude/skills/bmad-prd/references/validate.md'
  - '{project-root}/.claude/skills/bmad-prd/assets/prd-validation-checklist.md'
---

Skrevet 17.11 i vinduet som bygde 9.19, etter instruksjonen om PRD-en mot
faglærers rubrikk (limt inn kl. 21:07 i `docs/ai-prompts/2026-11-17.md`) og
gruppens svar 17.11 kl. 12:29 («Rett alt, ID-ene står»), 13:03, 13:10 og 13:40.
Rådet anbefalte dem. 9.19 ble flettet først (kl. 21:28). Neste ledige nummer i
Epic 9 etter 9.19 er 9.20. Worktreen er `G74-lund-osen-9-20`, på grenen
`9-20-prd-mot-rubrikken`, fra `origin/main` (`e5673cbb`).

## Storyen

Som **den som skal lage UX, stories eller tester** vil jeg kunne lese i PRD-en
hva som gjelder nå, uten å lete i historikken, så kravene kan brukes direkte.

**Oppfyller:** tilbakemeldingen fra faglærer 12.11 (punkt 1–7) og svarene
17.11 · **Begrenses av:** regel 3, 11, 12, 13, 14, 19 og 20; ingen ID endres;
ingen kode i `src/` endres; faglærers filer røres ikke

**Avhenger av:** 9.11, 9.16–9.19. **Én økt:** nei.

## Valideringen

Gjort 17.11 med `references/validate.md` og
`assets/prd-validation-checklist.md` i `.claude/skills/bmad-prd`, av én leser
med bare lesing, på `prd.md` på main (1970 linjer). Rapportfilene som
`validate.md` beskriver, er ikke skrevet. Funnene står her. Samlet vurdering
etter formelen: *Fair*, fordi det er ett høyt funn. Decision-readiness,
Substance over theater og Strategic coherence er *strong*. Done-ness clarity,
Scope honesty, Downstream usability og Shape fit er *adequate*.

| # | Dimensjon | Sted | Grad | Funnet | Forslag |
|---|---|---|---|---|---|
| V1 | Done-ness clarity | UJ-2, SM-10, NFR-06, §2 | høy | UJ-2 og SM-10 hviler på notatene med «Etterpå» og tenkte kjøp og salg, som ikke har eget krav. Følg og «Din egen liste» har heller ikke eget krav | Egne FR med konsekvenser, nye ID-er i sine avsnitt |
| V2 | Done-ness clarity | FR-603 | middels | Kravet mangler regelen fra 10.9 (del F) om at ordene om målingen skal stemme med fortegnet, og «Kontrollen er grov» sier at den bare fanger tall, retning og ord | Et punkt om målingen, en konsekvens med eksemplet fra demotekstene 07.11, og en presis setning om hva som fanges og ikke |
| V3 | Scope honesty, Shape fit | §2, §7, §8 | middels | Status- og prosesslinjer (hvem svarte når, hva er flettet, hva blir done) står i kravregisteret, med storynumre i parentes | Flyttes til endringsloggen, og bare terskel og frist står |
| V4 | Scope honesty | §8 «v1.1» | lav | Lista dupliserer «senere»-radene i tabellen i §2 | Viser til tabellen i §2 og sier hva som er bygget |
| V5 | Downstream usability | toppen | lav | Ingen del sier at §1–§8 gjelder nå og at vedlegg A ikke er bygget | «Slik leser du PRD-en» øverst |
| V6 | Downstream usability | §4 | lav | §4 sier ikke hva første siffer i ID-en er, og FR-407 står i §4.1 | FR-407 til §4.4, og §4 sier at første siffer er avsnittet |
| V7 | Downstream usability | hele | lav | Ordlista glir: «aksjedetaljen», «handelsdag», «forsiden» og «markedsoversikten», «KI-laget» og «KI-bidraget», «universet», «hentekommandoen» og «kveldsjobben». Posisjonsord som «over» og «under» | Ordene brukes likt overalt, uten posisjonsord |
| V8 | Done-ness clarity | FR-602, FR-203, FR-111, FR-110 | lav | Noe i kravteksten mangler konsekvens: den korte lista over ord om kjøp og salg, «Signalet dag for dag», knappen og panelet «Mine notater» | En konsekvens for hver |
| V9 | Scope honesty | FR-606 | lav | Kravet er «senere» og hører til plan A, men står i §4.6 | Står, og §4 sier hvorfor, eller til vedlegg A (spørsmål) |
| V10 | Mekanisk | UJ-1/SM-1, UJ-2/SM-10 | lav | Reisene og målene lister ulike krav | Samme krav begge steder |
| V11 | Mekanisk | §8, vedlegg A | lav | «punkt 16» og «punkt 2» peker på tekst som bare står i endringsloggen | Skrives ut |
| V12 | Mekanisk | endringsloggen | lav | Svartabellen er foreldet (UJ-1 alene, SM-1–SM-9, fem steg) | Flyttes til svarbrevet og rettes |
| V13 | Mekanisk | vedlegg A | lav | Ingen liste over [ANTAKELSE] og [FORELØPIG] | En liste, begge veier |
| V14 | Substance | NFR-03, SM-4 | lav | «dager uten tydelige signaler» er et adjektiv | Bundet til styrke 0 |

## Det som gjøres

Etter steg 2–4 i instruksjonen. Ingen ID endres, og ingen kode i `src/` endres.

1. **`prd.md`:** «Slik leser du PRD-en» øverst. Status og prosess i §7 og §8 til
   endringsloggen, og «v1.1» viser til tabellen i §2. Nye krav for notatene med
   «Etterpå», tenkte kjøp og salg, Følg med stjernen og «Din egen liste», med
   nye ID-er i sine avsnitt, og et tenkt salg uten kjøp som senere. FR-407 til
   §4.4. FR-603 med regelen om målingen. Ordene i ordlista likt overalt, ingen
   «se over» eller «se under», og kodenavn med vanlige ord, unntatt feltnavnene
   hos kilden. En linje i endringsloggen (regel 19).
2. **Sporingsfila** ved siden av `prd.md`: hver FR-, NFR-, UJ- og SM-ID med
   avsnitt, status, storyene og testfilene, og hvorfor noen numre mangler, med
   en test som låser fila. Lista over [ANTAKELSE] og [FORELØPIG].
3. **Svarbrevet** `tilbakemelding-prd-svar.md`, i faglærers rekkefølge 1–7, med
   tallene for linjer, ord og daterte linjer 12.11, etter 9.11 og nå.
4. **«Teknologi og nøkler»** i arkitekturmappa, i samme form som
   `technology.md`, lenket fra README-en.

## Grenser

- Faglærers filer (`tilbakemelding-prd.md` og `technology.md`) røres ikke.
- Ingen API-kall. `data/` og `_privat/` røres ikke.
- Pausene om kvelden gjelder: ingen pytest kl. 22:15–23:50, ingen git i de
  korte pausene, og ingen fletting kl. 22:10–23:58.

## Kontroll

- [ ] Funnene fra valideringen er rettet eller står som spørsmål
- [ ] «Slik leser du PRD-en», sporingsfila med test og lista over markørene
- [ ] Svarbrevet og «Teknologi og nøkler», lenket fra README-en
- [ ] Diff mot HEAD etter omskrivingen, uten krav som er borte (regel 13)
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
