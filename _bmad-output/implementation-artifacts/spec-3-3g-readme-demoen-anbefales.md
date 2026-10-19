---
title: 'Story 3.3 (3.3g): README-en anbefaler demoen, og regelen for omfanget'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '9c3d8a1'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/product-brief.md'
  - '{project-root}/_bmad-output/planning-artifacts/tilbakemelding-product-brief.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3d-readme-ryddingen.md'
---

## Intent

**Problem:** README-en anbefaler den ekte versjonen, mens briefen v8 sier at demoen «viser sensor alt i v1», og tilbakemeldingen 06.10 (punkt 2) ber om at demoen er «den versjonen sensor bruker». Den lokale modellen står uten at det står at den er valgfri. «Neste» under «Status» blander det briefen lover med det den ikke lover, og punktet om lenkene nevner NewsWeb, som appen ikke lenker til (06.10, story 10.5).

**Grunnlaget:** gruppens svar 19.10 kl. 14:46, 14:48 og 16:12 under «Prioritering» i `epics.md`, og instruksjonen 19.10 kl. 16:00 med svaret kl. 16:12. Svaret 14:46 snur anbefalingen i svaret 11.10 kl. 22:32 (`spec-3-4-demoversjonen.md`), og med det «den ekte versjonen er fortsatt anbefalt» i svaret 16.10 kl. 21:16. Rekkefølgen i «Kom i gang» står.

## Kontrollpunktene

- a) Anbefalingen: «Kom i gang» begynner med at demoen anbefales for faglærer og sensor, fordi den ikke trenger nøkkel og viser hovedfunksjonene med faste eksempeldata, også KI-teksten, og at den ekte versjonen er for å prøve løsningen med kurser fra EODHD. «(anbefalt)» tas bort ved den ekte versjonen, og lenkene til ankeret følger med
- b) Den lokale modellen: overskriften og første setning sier at den er valgfri og ikke trengs for demoen eller for å vurdere appen, fordi demoen har ferdig KI-tekst og bare trenger Docker. Innholdet står
- c) Beskrivelsen øverst sier «interesse (handelsvolum)». «Status» begynner med «Prosjektet er under utvikling. Listene under viser hva som er ferdig på main, og hva som gjenstår.» «Neste» deles i «Neste i v1», det briefen lover og som ikke er ferdig, og «Ekstra, hvis tiden rekker», med én setning om regelen kl. 14:48. NewsWeb tas ut av punktet om lenkene. `docs/hjelp.md`, kvalitetssikringen og vurderingsmatrisen følger med, med daterte linjer (regel 19)
- d) Testene, med «Ville feilet hvis»: «Kom i gang» anbefaler demoen for faglærer og sensor; ingen «(anbefalt)» ved den ekte versjonen; delen om den lokale modellen sier at den er valgfri; «interesse (handelsvolum)» øverst; ingen av de ekstra står under «Neste i v1»

## Planen, én commit per punkt

1. a) Første avsnitt i «Kom i gang» begynner med anbefalingen. Overskriften blir «Den ekte versjonen», tabellhodet «| | Demoen | Den ekte versjonen |», og lenken under «Til faglærer» går til `#den-ekte-versjonen`. Testene som bruker overskriften som nøkkel, følger med.
2. b) `<summary>` og første setning i knappen for den lokale modellen. Testene som slår opp knappen på navnet, følger med.
3. c) Beskrivelsen, «Status» og de to listene, og de daterte linjene i `docs/hjelp.md`, `docs/kvalitetssikring.md` og `docs/vurderingsmatrise.md`. Testen for «Status» følger med.
4. d) De nye testene, og mutantene.

## Avgjort i spesifikasjonen

- **Hvilke punkter som er v1.** Briefen v8, «Inne i v1»: kjernen, KI-forklaringen med av/på-bryter, historikk, hovedindeks og «Min liste». Under «The Solution» lenker aksjedetaljen «til selskapets investorside», og under «Data og kilder» kan Gemini, Anthropic eller OpenAI velges med egen nøkkel (svaret kl. 16:12). «Neste i v1» er derfor Min liste (8.3), historikken i aksjedetaljen (2.7), lenken til selskapets egen nettside (10.5) og egen nøkkel (10.7), i den rekkefølgen «Neste» hadde dem.
- **Signaldagene i grafen** (8.8) sto i samme punkt som historikken. Briefen nevner historikk, ikke signaldagene, så punktet deles: historikken under «Neste i v1» og signaldagene under «Ekstra».
- **«Ekstra, hvis tiden rekker»** er signaldagene (8.8), innstillingene med «Vis KI-tekst» (8.10 og 8.10b, svaret 18.10 kl. 11:20), periodevalget, børsometeret og KI-teksten om dagen på forsiden (8.17 og 10.6) og å velge og bytte aksjer (2.11 og 2.12).
- **«(anbefalt)»** settes ikke ved demoen. Overskriften «Demoen» og ankeret `#demoen` står, så lenkene til den ikke endres.

## Boundaries

- Ingen kode i `src/` endres. Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db`, `data/db/demo.db` og den ekte `.env` røres ikke.
- Ingen linje fjernes fra andre dokumenter enn README-en, utenom status og updated.
- PR-en stopper før flettingen og venter på ja.
