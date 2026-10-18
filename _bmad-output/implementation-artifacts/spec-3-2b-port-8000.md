---
title: 'Story 3.2b: port 8000 i stedet for 5000'
type: 'chore'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3dc5ba0'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** på Mac bruker AirPlay-mottakeren port 5000, så appen starter ikke der uten at man slår den av. Story 3.2b i `epics.md` (gruppens svar 18.10 kl. 17:40).

**Grunnlaget:** instruksjonen 18.10 kl. 18:05. PR-en flettes når vilkårene i steg 4 holder.

## Planen, én commit per punkt

1. Storyen i `epics.md` og denne spesifikasjonen.
2. a) Koden: `compose.yaml`, `Dockerfile`, `src/app.py` og CI bruker 8000, også inne i containeren.
3. b) README-en og `docs/hjelp.md` sier 8000, og setningen om AirPlay får en Rettet-linje.
4. c) `docs/kvalitetssikring.md` (Prøve 1 og 2) sier 8000, med en Rettet-linje, og arkitekturdokumentet får en datert linje.
5. d) Testen for at porten er den samme overalt, og at 5000 ikke står igjen.

## Avgjort i spesifikasjonen

- **Testene som har 5000 i seg i dag**, rettes i commiten som endrer det de leser: `tests/test_docker.py` for waitress og portene i punkt a, og adressene, «Serving on» og svaret om porten i punkt b. Svaret README-en hadde om porten (`UTE_AV_README`, story 3.3d), sier 8000, som svaret i `docs/hjelp.md`.
- **Tallet 5000 i `tests/test_app.py`, `tests/test_utseende.py` og `tests/test_ki_modell.py`** er volum og tekstlengde, ikke porten, og står.

## Boundaries

- Hentingen og basene røres ikke. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- Spesifikasjonene og dagsfilene står som de er.
