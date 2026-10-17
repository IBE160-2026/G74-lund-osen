---
title: 'Story 9.1, oppdatering 17.10: docs/kvalitetssikring.md følger repoet'
type: 'docs'
created: '2026-10-17'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3699a16'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/docs/vurderingsmatrise.md'
---

## Intent

**Problem:** `docs/kvalitetssikring.md` (story 9.1) har tallene fra 03.–05.10. §3 og §5 slutter ved 2.5, 8.0 og 9.0, og §6 sier at mye som er bygget, ikke er det: Docker, KI-laget, 2.3, 2.8, nettsperren og at webserveren leser basen. README-en viser til dokumentet under «Tester». Story 9.1 sier at dokumentet oppdateres ved hver epic (`epics.md`, «Tidspunkt»), og §8 i dokumentet sier hvordan.

**Grunnlaget:** instruksjonen 17.10 kl. 22:22, spesifikasjonene i `_bmad-output/implementation-artifacts/`, dagsfilene i `docs/ai-prompts/` og git-loggen. PR-en flettes i instruksjonen når vilkårene i steg 5 holder (svarene 17.10 kl. 22:06).

## Planen, én commit per punkt

**a) §1 og §2:** testene telles på nytt med `uv run pytest --collect-only -q` på `3699a16`, med CI-kjøringen for samme commit, i en ny tabell med dato over den fra 03.10, som står. Antallet som hoppes over lokalt, og testene for nettsperren, får en datert linje.

**b) §3 og §5:** en rad for hver spesifikasjon som mangler, 27 i alt: de 25 med status `done` fra 2.2 til 2.9 og 10.3, og 3.4 og 10.2a, som har en annen status. §3 har mutantene og hvilke som overlevde en stund, og vedlegget får én linje per spesifikasjon med mutantene og testene som fanget dem. §5 har radene i triagen (rettet, avvist, utsatt). Tallene er hentet fra spesifikasjonene. Der spesifikasjonen og dagsfila sier ulikt, føres det som et åpent punkt (regel 12). Tre agenter leste spesifikasjonene og dagsfilene, og et utvalg av påstandene deres er slått opp på nytt før de ble skrevet.

**c) §6:** hver linje som ikke stemmer lenger, får en Rettet-linje med commit. Nye hull føres inn: testene som bare bruker testklienten, ekte svar fra EODHD og Ollama, at CI kjører uten hemmeligheter uten egen test, og README-prøven.

**d) «Feil vi fant og rettet»:** 12 til 15 eksempler fra repoet. Minst ett for hver måte de ble funnet: en test, en mutant, en linse i gjennomgangen, utskriften fra en ekte henting, kontrollen av KI-teksten og vår egen gjennomgang av «Kom i gang» 16.10. For hvert: hva som var feil, hvordan det ble funnet, commiten som rettet det og testen som passer på nå. Det som rettes i README-PR-en søndag, står som ikke rettet ennå.

**e) Feilhåndtering, validering av input og hemmeligheter,** med testene som viser det.

**f) Manuelle tester og testplaner,** med dato og resultat der det finnes.

**Testfila** `tests/test_kvalitetssikring.py`:
- Hver spesifikasjon med status `done` har en rad i §3 og i §5. Deler flere spesifikasjoner samme story, kreves én rad for hver.
- Hver test som `kvalitetssikring.md` og `vurderingsmatrise.md` nevner med fil og navn, finnes.

**§5** får en linje om at hver PR fra nå får triagen som kommentar. PR #56–#60 og denne PR-en får en slik kommentar (steg 4).

## Boundaries & Constraints

- Bare det som står i repoet. Ingen karakter, intet anslag, og ingenting sitert fra sensorveiledningen.
- Ingen linje fjernes, utenom status og `updated`. En linje som ikke stemmer lenger, får en Rettet-linje.
- Ingen kall til EODHD utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- **Steg 4 i instruksjonen** ber om at kommentarene i PR #56–#60 merkes «satt sammen 18.10». De settes sammen 17.10, så de merkes med den datoen.

**Testtallet før:** 2366 bestått og 17 hoppet over lokalt, og 2383 bestått i CI (kjøring 39066471455 på `3699a16`).
