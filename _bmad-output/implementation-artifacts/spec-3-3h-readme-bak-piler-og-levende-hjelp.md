---
title: 'Story 3.3 (3.3h): README-en bak piler, og hjelpen som levende dokument'
type: 'feature'
created: '2026-10-20'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '013be41'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3g-readme-demoen-anbefales.md'
  - '{project-root}/docs/ux-logg.md'
---

Tillegg til story 3.3 (README — «Slik kjører du den»), etter gruppens svar 20.10 kl. 10:14, 10:15, 10:18 og 10:19 og kl. 16:19 (under story 3.3 i `epics.md`, `49e9041`). Det er U7 i [`docs/ux-logg.md`](../../docs/ux-logg.md).

## Intent

**Problem:** README-en er lang å lese: 419 linjer og om lag 3 800 ord 20.10 (U7). Alt står åpent, også stegene for den versjonen leseren ikke valgte, dokumentlista og mappestrukturen. `docs/hjelp.md` har åtte daterte linjer (*Rettet* og *Lagt til*) mellom svarene, og svaret «Når kan jeg hente?» begynner fortsatt med «Hent etter kl. 21», fordi kl. 22 bare står i en Rettet-linje under.

**Løsning:** README-en blir kortere å lese, med mer bak en pil som foldes ut (`<details>`), og alt står fortsatt i én fil, som virker fra ZIP-fila. Hjelpen blir et levende dokument som README-en: teksten rettes der den står, og historikken ligger i git.

## Planen, én commit per punkt

**a) Veiene.** De felles stegene 1–4 står åpent. Rett etter dem kommer en kort linje «Velg vei» og to piler:
- demoen, anbefalt for faglærer og sensor og uten nøkkel (svaret 19.10 kl. 14:46)
- den ekte versjonen, med kurser fra EODHD og egen nøkkel

Tabellen over viser forskjellen. Inne i hver pil står stegene fra 5, kommandoene, bildene og advarselen om `docker compose down -v` uendret. Lenkene og ankrene dit virker. Linja i demoen om å gå videre til den ekte versjonen peker til pila.

**b) Resten av README-en og hjelpen.**
- «Dokumentene» og «Mappestruktur» har overskriften synlig og innholdet bak en pil.
- Under «Tester» står kommandoene, punktene om nettkall, data, CI og ruff og lenken til kvalitetssikringen synlig. Installasjonen av uv og tipset når uv ikke blir funnet står bak en pil.
- «Status» står åpent, og «Ferdig» blir en kort liste over det appen kan, én linje per punkt, med alt som er flettet og ikke noe annet.
- I `docs/hjelp.md` arbeides hver linje som begynner med *Rettet eller *Lagt til, inn i svaret den hører til, eller tas bort når den bare sier hva som var før. Svaret om når man kan hente, sier kl. 22, og testene som krevde linjene, følger med.

**c) Testene**, med «Ville feilet hvis»:
- demoen, den ekte versjonen, dokumentlista og mappestrukturen står bak hver sin pil
- de felles stegene står ikke bak en pil
- pila til demoen sier at den er anbefalt for faglærer og sensor
- under «Tester» står `uv sync`, `uv run pytest` og lenken synlig
- hvert steg, hver kommando og hver lenke fra før finnes
- hjelpen sier klokkeslettet fra `TIDSGRENSE` i svaret og har ingen *Rettet- eller *Lagt til-linje
- markdown inne i pilene vises riktig på GitHub

## Det som ikke endres

- Ingen kode i `src/`.
- Rekkefølgen i README-en: beskrivelsen, bildene, «Innhold», «Til faglærer», «Kom i gang», «Status», «Tester», «Dokumentene», «Mappestruktur» og «Medlemmer».
- «Står du fast?» og «Mer for den som vil» står som før.
- Ingen linje fjernes fra andre dokumenter enn README-en og `docs/hjelp.md`, utenom `status` og `updated`.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Den ekte `.env` leses ikke.
- PR-en stopper før flettingen og venter på ja.

**Mutantene**, én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- de felles stegene bak en pil
- «anbefalt» tatt bort fra pila til demoen
- et steg tatt bort fra den ekte versjonen
- den tomme linja etter `</summary>` tatt bort
- en Rettet-linje lagt tilbake i hjelpen
