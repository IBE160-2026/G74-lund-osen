---
title: 'Story 3.5 (3.5g): «Kom i gang» med fem steg og resten bak piler'
type: 'docs'
created: '2026-10-27'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '54d4714'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5f-hovedveien.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** «Kom i gang» er for lang. Fra overskriften til den første pila står tabellen, «Velg vei», «Du trenger», hele dobbeltklikket med advarslene, nøkkelen og skriptene, og Docker-stegene 1–4 med bildene.

**Løsningen:** én setning, så «Enklest: dobbeltklikk (anbefalt)» med fem korte nummererte steg, én linje om advarselen første gang og én om den ekte versjonen. Alt annet står bak piler eller i `docs/hjelp.md`, og ingenting forsvinner.

**Grunnlaget:** avgjørelsen 26.10 kl. 23:00 under story 3.5 i `epics.md`. Den går foran innspillet 25.10 kl. 11:26 om at resten ryddes etter testene.

## Slik er det i dag (slått opp 27.10 på `54d4714`)

- **`README.md`, «Kom i gang» (linje 33–103 før den første pila):** ankeret `kom-i-gang`, avsnittet som begynner med «Vi anbefaler demoen for faglærer og sensor», tabellen, «Velg vei etter hva du har», «Du trenger», `### Enklest: dobbeltklikk, uten Docker` med fire punkter, «Når vinduet er åpent» med fire punkter, advarselen fra Windows, godkjenningen på Mac, `.git`-vernet, nøkkelen og skriptene med porten, så `### Med Docker Desktop` med steg 1–4, tre bilder, «Slik limer du inn en kommando» og «Velg versjon». Så pilene til demoen og den ekte versjonen, advarselen mot `down -v`, `### Står du fast?` med fem spørsmål bak piler, og `### Mer for den som vil` med fem piler, der «Uten Docker, med uv» er den andre.
- **Ankrene lenkene bruker:** `#kom-i-gang`, `#enklest-dobbeltklikk-uten-docker` («Til faglærer», «Velg vei» og «Windows advarer mot fila.» i `docs/hjelp.md`), `#med-docker-desktop` og `#demoen` («Til faglærer»), `#den-ekte-versjonen` («Til faglærer», demoen og `EKTE_VERSJONEN_URL` i `src/app.py`, som demolinja i appen lenker til), `#uten-docker-med-uv`, `#står-du-fast`, `#mer-for-den-som-vil` og `#tester`.
- **`docs/hjelp.md`:** «Windows advarer mot fila.» og «Mac sier at fila ikke kan åpnes.» under «Start med dobbeltklikk» har det samme som avsnittene i README-en. «Hvor finner jeg nøkkelen, og hvordan limer jeg den inn?» og «Nøkkelen var feil.» har det meste av avsnittet om nøkkelen, men ikke at den lagres bare i `.env`, eller at ingen kall brukes når alt er hentet. Svaret om porten sier at «Bytte mellom demoen og den ekte versjonen» står under «Mer for den som vil».
- **Testene for README-en:** de fleste i `tests/test_docker.py`, fra `TestReadme` (linje 512) til `TestHovedveien` (linje 3292), med hjelperne `_kom_i_gang`, `_seksjon`, `_pil`, `_steg`, `_detaljer`, `_utenfor_pilene` og `PIL`, og `tests/test_dobbeltklikk.py` (`_delen_i_readme`). Avtrykkene i `AVTRYKK_I_PILENE` er sha256 av innholdet i pilene til demoen, den ekte versjonen (med advarselen mot `down -v`), dokumentlista og mappestrukturen. `test_markdown_inne_i_pilene_vises_riktig_paa_github` godtar ingen pil inne i en annen. `test_demo.py::test_lenken_gaar_til_ankeret_i_readme` krever `<a name="den-ekte-versjonen"></a>` i README-en.

## Kontrollpunktene

- a) «Kom i gang»: én setning først, så «Enklest: dobbeltklikk (anbefalt)» med de fem stegene, høyst 25 ord hver, linja om advarselen med lenker til svarene for Windows og Mac, og linja om den ekte versjonen. Ankrene som «Til faglærer» og andre lenker bruker, virker fortsatt.
- b) Bak piler, i denne rekkefølgen: «Demoen og den ekte versjonen» med tabellen, «Du trenger», «Med Docker Desktop» med stegene og bildene, «Uten Docker, med uv», «Slik virker dobbeltklikket» med skriptene, porten og `.git`-vernet, og «Står du fast?». Teksten flyttes og skrives ikke om, utenom det som trengs for at den henger sammen.
- c) Testene følger den nye formen, med «Ville feilet hvis» stegene ikke sto først, et steg manglet eller var for langt, en lenke eller et anker var dødt, en overskrift eller kommando fra før manglet, eller Docker-veien manglet. Avtrykkene settes på nytt. Mutant: steg 3 tatt ut.
- `docs/hjelp.md` følger med (regel 19).

## Valg som er gjort her

- **Ankeret til dobbeltklikket.** Overskriften «Enklest: dobbeltklikk (anbefalt)» gir ankeret `enklest-dobbeltklikk-anbefalt`. En linje `<a name="enklest-dobbeltklikk-uten-docker"></a>` rett over overskriften beholder det gamle, som `kom-i-gang` i 3.5f, så «Til faglærer» og `docs/hjelp.md` virker som før.
- **Pilene til demoen og den ekte versjonen står ikke inne i pila til Docker.** De står rett etter den, hver for seg, med advarselen mot `down -v` rett under pila til den ekte versjonen som før (svaret 20.10 kl. 20:20). Grunnen er ankrene: `#demoen` og `#den-ekte-versjonen` står i `<summary>`, og «Til faglærer» og demolinja i appen lenker dit. Inne i en lukket pil ville `<summary>` vært skjult, så lenken ikke viste noe. Innholdet i de to pilene er uendret, så avtrykkene deres er de samme.
- **«Står du fast?» er en pil med de fem spørsmålene inni,** fordi spørsmålene alt står bak hver sin pil. Det er den eneste pila inne i en annen. Testen for pilene godtar det der og ingen andre steder. Ankeret `står-du-fast` står i `<summary>`, som de andre.
- **Nummererte steg i dobbeltklikket.** 3.5f valgte punktliste fordi «steg 4» betyr Docker-stegene. Avgjørelsen 26.10 kl. 23:00 sier nummererte steg. Docker-stegene står nå bak pila «Med Docker Desktop», og overskriftene i `docs/hjelp.md` heter «Steg 1: Docker Desktop» og så videre, så de nevner Docker. «steg 4» i README-en står bare inne i Docker-pilene og i svarene under «Står du fast?», som gjelder Docker. Det står som åpent punkt om det likevel er uklart for leseren.
- **Avsnittene om advarselen, godkjenningen og nøkkelen står i pila «Slik virker dobbeltklikket»,** uendret, og linja om advarselen lenker til svarene i `docs/hjelp.md`. Svaret om nøkkelen i hjelpen mangler to setninger fra README-en (slått opp over), så avsnittet blir i README-en, og ingenting forsvinner.
- **Det som er skrevet om for at teksten henger sammen:** lenketeksten til dobbeltklikket i «Til faglærer» og «Velg vei» er «Enklest: dobbeltklikk», og «Velg vei» sier ikke lenger at uv står under «Mer for den som vil». I `docs/hjelp.md` viser svaret «Windows advarer mot fila.» til «Slik virker dobbeltklikket» i stedet for den gamle overskriften. Svaret om porten står, fordi «Bytte mellom demoen og den ekte versjonen» fortsatt står under «Mer for den som vil». Resten er flyttet uendret: fem av pilene har byte for byte samme innhold som delene på `54d4714`, og testene låser hver pil med sha256 (`AVTRYKK_I_KOM_I_GANG`).

## Planen

1. Spesifikasjonen.
2. README-en, `docs/hjelp.md` og testene i samme commit (regel 19 og instruksjonen).

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: steg 3 tatt ut av dobbeltklikket.

## Gjennomgangen

Kommer etter hele settet.

## Åpent

- Om «steg 4» er uklart nå som dobbeltklikket også har nummererte steg (se «Valg som er gjort her»).
