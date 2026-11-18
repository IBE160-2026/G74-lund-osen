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

## Bygget

Skrevet 17.11–18.11 av én agent i worktreen, og kontrollert i vinduet: at `src/`
og faglærers filer ikke er rørt, at ingen ID er endret, og testene.

| Del | Commit |
|---|---|
| «Teknologi og nøkler» i `architecture/`, lenket fra README-en | `66db04a8`, `e9707ece` |
| Status og prosess ut av §2, §7, §8 og FR-108, og «v1.1» viser til tabellen i §2 | `bf418d0f`, `50134d36` |
| Nye krav: FR-112 «Din egen liste» (§4.1), FR-208 notatene med «Etterpå» og FR-209 tenkte kjøp og salg (§4.2), FR-415 «Følg en aksje» med stjernen (§4.4); et tenkt salg uten kjøp er senere | `b26522dc` |
| FR-407 i §4.4, og §4 sier at første siffer er avsnittet | `e7b52b22` |
| FR-603 med punkt 5, «Målingen», og en presis «Kontrollen er grov» | `da440801` |
| Ordene i ordlista likt overalt, uten posisjonsord og kodenavn (12 ord) | `e262ea67` |
| Konsekvensene som manglet, samme krav i reisene og målene, punktene for plan A skrevet ut | `6558560c` |
| `prd-sporing.md` med testen `tests/test_prd_sporing_9_20.py`, og lista over antakelsene begge veier | `7f6f9d74`, `79295858` |
| «Slik leser du PRD-en» øverst | `b8ab8192` |
| Svarbrevet `tilbakemelding-prd-svar.md`, med svartabellen fra endringsloggen | `6ee4ec58`, `4356fe5d` |
| Rettingene etter gjennomgangen | `b8ee7433`, `394fd64d`, `50134d36`, `b201014d`, `301d8e13` |

Hver endring i `prd.md` har en datert linje i endringsloggen med teksten som
sto, ordrett (regel 13). Diffen mot HEAD ga ingen krav som er borte: det som er
tatt ut, står i endringsloggen, i svarbrevet eller i «Teknologi og nøkler».

**Tallene** (ord telt med `\w+`):

| | Linjer | Ord | Daterte linjer |
|---|---:|---:|---:|
| Taggen `prd-vurdert-2026-11-12` | 2 264 | 30 660 | 174 |
| Etter 9.11 (`ef802733`, 13.11) | 1 870 | 14 773 | 0 |
| Nå | 2 132 | 18 026 | 0 |

Faglærer skrev om lag 28 700 ord. Med `str.split()` gir taggen 29 030. Hvordan
han telte, er ikke kjent, så spriket står åpent (regel 12).

## Gjennomgangen 17.11–18.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `d3c40031`. 27 funn: 6 på middels og 21 lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| BH1 | middels | FR-604 fikk snevrere mening | Rettet: en rad også når modellen feiler (`b8ee7433`) |
| BH2 | middels | Kriterium 2 i §3 gjaldt lista, ikke de 15 | Rettet (`b8ee7433`) |
| BH3 | middels | At SM-1 ikke er nådd, og terskelen «under 5 minutter», sto ikke i PRD-en | Rettet: åpent punkt 28 i §8, lenket fra svarbrevet (`394fd64d`) |
| BH4 | middels | Lista over hva som er bygget fra v1.1, var feil | Rettet: viser til lista i endringsloggen og tabellen i §2 (`50134d36`) |
| BH5 | middels | NFR-03 og SM-4 ble bundet til at alle aksjene har styrke 0 | Rettet: dager der ingen aksje skiller seg ut (FR-705) (`b201014d`) |
| VG1 | middels | Testen låste mindre enn brevet og endringsloggen sa | Rettet: avsnittet, statusen, storyene og numrene som mangler, sjekkes (`79295858`) |
| BH6 | lav | Raden for FR-108 har dato | Står: teksten er låst av en test |
| BH7–BH13 | lav | «Slik leser du» uten unntak, FR-606 i «v1.1», punkt 27, FR-415 i §4.4, «Med av», svarbrevet, teknologidokumentet | Rettet (`301d8e13`, `50134d36`, `4356fe5d`, `e9707ece`) |
| ECH1–ECH6 | lav | Hele lista i `_VAKT`, plassene i FR-112, Min liste og de som venter, testfilene for FR-109 og FR-415, waitress i Docker, datoen for `ef802733` | Rettet |
| VG2 | lav | Ingen test for at ordene i ordlista brukes likt | Står: lesingen er gjort, og en test ville måtte kjenne hvert synonym |
| VG3, VG4 | lav | Markørene uten kodeformat, og lenkene i de nye dokumentene | Rettet (`79295858`) |

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet.

1. **FR-606 i §4.6 (V9).** Relevansskalaen er senere og plan A, men står i
   KI-avsnittet. *Forslag:* den står, og «v1.1» i §8 sier hvorfor.
2. **FR-112 i §4.1.** «Din egen liste» står som en del av Min liste-siden.
   *Forslag:* behold.
3. **Ordlista har 12 ord**, med «Oversikten» og «KI-teksten», og testen tillater
   8–12. Faglærer foreslo 8–10. *Forslag:* behold, fordi de to ordene ble brukt
   ulikt.
4. **Filnavn i PRD-en.** Variabelnavnene er skrevet med vanlige ord, men
   `.env`, `.git`, `data/` og `src/` står som filnavn. *Forslag:* behold.
5. **Svarbrevet** har `status: draft`, fordi gruppen ikke har lest det.
   *Forslag:* `sendt` når det er sendt.
6. **Startskriptene** har variabler som bare brukes av testene (`OSE_START_*` og
   `OSE_SKRIVEBORD`), og «Teknologi og nøkler» beskriver dem som testkroker.
   *Forslag:* behold.

## Grenser

- Faglærers filer (`tilbakemelding-prd.md` og `technology.md`) røres ikke.
- Ingen API-kall. `data/` og `_privat/` røres ikke.
- Pausene om kvelden gjelder: ingen pytest kl. 22:15–23:50, ingen git i de
  korte pausene, og ingen fletting kl. 22:10–23:58.

## Kontroll

- [x] Funnene fra valideringen er rettet eller står som spørsmål
- [x] «Slik leser du PRD-en», sporingsfila med test og lista over markørene
- [x] Svarbrevet og «Teknologi og nøkler», lenket fra README-en
- [x] Diff mot HEAD etter omskrivingen, uten krav som er borte (regel 13)
- [x] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
