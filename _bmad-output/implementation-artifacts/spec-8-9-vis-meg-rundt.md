---
title: 'Story 8.9: «Vis meg rundt»'
type: 'feature'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '1a72810a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28, 12:00 og 15:43, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:30 og 10:43: 2.4, 2.6 med 8.14, 8.7 og 8.9 bygges i dag og flettes onsdag etter brukertesten, 8.9 så den ikke påvirker det testen måler. Instruksjonen sier for 8.9: «‹Vis meg rundt› på hver side, også Innstillinger og Min liste, med tekstene i samme fil som hjelpen.» Bygget fra head-en til PR #126 (`1a72810a`), på grenen `8-9-vis-meg-rundt`, i worktreen `G74-lund-osen-8-9`, og stoppet før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Hvordan rundturen vises.** *Forslag:* en knapp «Vis meg rundt» øverst, under linjene i toppen, som åpner en nummerert liste med stegene. Hvert steg er en lenke til delen av siden det forklarer. Det er ingen skript og ingen omvisning som flytter seg fra del til del, så den virker med tastatur og skjermleser som resten av siden.
2. **Hvilke sider.** *Forslag:* oversikten, Min liste, børsometeret, aksjesiden, Innstillinger og «Følg en aksje» (søket). Oversikten, Min liste og børsometeret har knappen bare når de har aksjer å vise. Investorsiden i demoen og sidene for en feil har den ikke.
3. **Stegene.** *Forslag:* høyst 7 per side (endringsforslaget 13.10, punkt 4.1). Stegene om signalstyrken, retningen og sjekkene bruker tekstene bak «?» i `hjelpetekster.py`. Punkt 4.1 sier «tekstene fra tavla i punkt 4.2»; tekstene bak «?» er de som er bygget fra den, og her brukes de som de står.
4. **Aksjesiden uten sjekker.** På en dag uten vurdering viser siden ikke sjekkene, og «?» for dem står ikke. *Forslag:* stegene om sjekkene står heller ikke da (`aksje_uten_sjekker`).
5. **«Vis hjelp».** *Forslag:* knappen følger «Vis hjelp» i Innstillinger, som «?»: med hjelpen av står den ikke.
6. **Brukertesten.** *Forslag:* flettes onsdag etter brukertesten, som svaret sier, så den ikke er på sidene testen måler.
7. **Testene som er endret.** Tre eksisterende tester er endret, fordi siden har en ny lenke og en ny `<details>`. `test_hver_lenke_gaar_til_en_side_som_finnes` i `tests/test_utseende.py` godtar nå en lenke til en id på samme side, når id-en finnes på siden. `test_tabellen_er_lukket_bak_se_tallene_som_tabell` i `tests/test_boersometer.py` holder `<details class="rundtur">` utenfor tellingen. *Forslag:* godta. Det testene vakter, at hver lenke går til noe som finnes, og at tabellen står lukket, står som før.

## Intent

**Problem:** En ny bruker ser alle delene av siden på en gang og vet ikke hva de er før tallene leses (FR-109).

**Approach:** Stegene står i `hjelpetekster.py`, som hjelpen, og en makro i `src/templates/_rundtur.html` viser dem i toppen av hver side, i blokken `rundtur` i `_ramme.html`.

## Delene

### A) Stegene
`Steg`, `rundturer()` og `MAKS_STEG` i `src/hjelpetekster.py`.
- **Ville feilet hvis:** en side hadde flere enn 7 steg, et tall i stegene var skrevet for hånd og ikke hentet fra `Parametre`, eller stegene om signalstyrken, retningen og sjekkene hadde egne tekster.

### B) Sidene
`_rundtur.html`, blokken `rundtur` i `_ramme.html`, og sidene.
- **Ville feilet hvis:** en side manglet knappen, et steg pekte på noe siden ikke har, aksjesiden uten sjekker forklarte sjekkene, eller knappen sto med «Vis hjelp» av.

### C) Hjelpen og bildene
«Hva er «Vis meg rundt»?» i `docs/hjelp.md`. Bildene i `docs/appen/` er tatt på nytt.

## Grenser

Ingen KI og ingen nettkall. `data/db/ose.db` røres ikke. Ingen migrasjon.

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `8-9-vis-meg-rundt`, i worktreen `G74-lund-osen-8-9`, fra `1a72810a`. Filene: `src/hjelpetekster.py`, `src/app.py` (stegene til malene), `src/templates/_rundtur.html` (ny), `_ramme.html`, `index.html`, `boersometer.html`, `aksje.html` (to tomme ankre, `noekkeltallene` og `sjekkene`, så malen ellers er som før), `innstillinger.html` (id-ene `hjelp-valget` og `ki-valget`), `folg.html`, `src/static/stil.css`, «Hva er «Vis meg rundt»?» i `docs/hjelp.md`, og testene i `tests/test_vis_meg_rundt_8_9.py`. Bildene er tatt på nytt med DevTools-protokollen: åtte er endret med knappen i toppen, og investorsiden er byte for byte den samme. Avtrykkene er regnet ut på nytt.

Under byggingen: knappen sto først i innholdet, og sju eksisterende tester som leser teksten på aksjesiden, feilet. Den står nå i toppen. Den lukkede lista ble regnet som synlig tekst under hjelpefeltet i `test_hjelpefeltet.py`, så den har `display: none` når den er lukket.
