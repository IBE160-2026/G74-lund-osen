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
*Rettet 2026-10-18 (gjennomgangen, BH10):* «steg 4» er steg 4 i instruksjonen kl. 18:05: ingen test feiler, ingen mutant overlever, CI er grønn, og hvert funn med dom medium eller høyere er rettet.

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

## Avgjort etter gjennomgangen

- **Setningen om AirPlay** er tatt ut av svaret om porten i `docs/hjelp.md` (gruppens svar kl. 18:58, BH1 og ECH1). Den står ordrett i Rettet-linja under svaret. Instruksjonen sa at setningen skulle få en Rettet-linje. Svaret kl. 18:58 går lenger, fordi svaret ellers ba en Mac-bruker slå av AirPlay rett over linja som sa at det ikke trengs.

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. P1–P3 er fra instruksjonen, fanget på `75b73f8` og på nytt på `1521c05`. P4 og P5 er for funnene med dom medium eller høyere, fanget på `1521c05`. Alle ble fanget av `test_porten_er_den_samme_overalt_og_ikke_5000`:
- P1, `"127.0.0.1:5000:5000"` i `compose.yaml`.
- P2, `http://127.0.0.1:5000` i steg 6 i README-en.
- P3, `EXPOSE 5000` i `Dockerfile`.
- P4, setningen om AirPlay og port 5000 tilbake i svaret om porten i `docs/hjelp.md` (BH1).
- P5, `http://127.0.0.1:5000` i «Siden åpnes ikke.» i `docs/hjelp.md` (BH3).

## Gjennomgangen

Gjennomgang 18.10 på diffen `3dc5ba0..75b73f8`. Linsene var Blind Hunter (BH, 10 funn, bare diffen), Edge Case Hunter (ECH, 8, der ECH5, ECH6 og ECH8 ikke fant noen feil) og Verification Gap (VG, 12, der VG6, VG7, VG9, VG10 og VG12 fant kravene oppfylt). Ingen av dem kjørte pytest eller Docker. Ett funn har dom high og tre har medium, og alle er rettet i `1521c05` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | Svaret om porten sa «Noe annet bruker port 8000» og så at man skulle slå av AirPlay, rett over Rettet-linja som sa at det ikke trengs | high | patch etter gruppens svar kl. 18:58: setningen er tatt ut og står ordrett i Rettet-linja. P4 |
| BH2 | `UTE_AV_README` låste den selvmotsigende teksten | medium | patch: svaret uten AirPlay, med en kommentar |
| BH3, ECH2, VG2 | Testen for porten leste ikke `docs/hjelp.md` | medium | patch: adressene og «Serving on» i `docs/hjelp.md`, og 5000 bare i Rettet-linjer. P5 |
| VG1 | Mutantene var ikke ført | medium | patch: over, og i Utført-linja |
| BH4, VG11 | Testen er rød mellom punkt a og b | low | avvist: `test_linja_som_viser_at_appen_er_klar` binder README-en til `Dockerfile`, så ingen av punktene kan stå grønne alene. Commitmeldingen sier det, og squash-flettingen gir én commit på main. Dommen er senket fra medium (BH) til low (VG) |
| BH5 | Bare den siste port-linja per tjeneste i compose ble telt | low | patch |
| BH6 | Porten til Ollama ble lest med `rsplit` | low | patch: `urlsplit` |
| BH7, ECH3 | Adresser med `localhost` ble ikke lest | low | patch. `EXPOSE 8000/tcp`, `port=PORT` og lang form i compose gir en falsk rød test, aldri en falsk grønn |
| ECH4 | «5000» som delstreng kan felle testen for et tall som ikke er en port | low | avvist: ingen slike tall i filene testen leser, og det gir en falsk rød test, ikke en falsk grønn |
| BH8, VG5 | Merknaden i arkitekturdokumentet står ikke i datorekkefølge | low | avvist: instruksjonen sier «der det nevner 5000», rett under merknaden den retter |
| BH9 | Samme `updated` i to commits | low | avvist: `47523dc` kl. 18:08:27 og `cd6d859` kl. 18:08:56, begge fra `date` |
| BH10 | «steg 4» i spesifikasjonen | low | patch: Rettet-linje over |
| VG3 | Ingen test for Rettet-linja i `docs/hjelp.md` | low | avvist: P4 viser at setningen ikke kan komme tilbake i svaret |
| VG4 | Rettet-linja for Prøve 2 står under Prøve 1 | low | avvist: linja nevner begge |
| ECH7 | 8000 er standardport for flere utviklerverktøy | low | avvist: ikke slått opp i repoet (regel 3), og svaret sier «Noe annet bruker port 8000» |
| VG8 | «Hentingen og basene røres ikke» er sjekket med diffen | low | avvist: `src/fetch_prices.py`, migrasjonene og volumene er ikke i diffen |
