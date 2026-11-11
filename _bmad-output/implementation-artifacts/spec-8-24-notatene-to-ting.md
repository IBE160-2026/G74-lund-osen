---
title: 'Story 8.24: Notatene, to ting etter flettingen'
type: 'feature'
created: '2026-11-11'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'f68c6f89'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-21-egne-notater-paa-aksjesiden.md'
---

Skrevet 11.11 i instruksjonen kl. 23:01 10.11, etter gruppens gjennomgang av bildene og svaret 10.11 kl. 22:59. Rådet anbefalte det. Instruksjonen lagres i `docs/ai-prompts/2026-11-10.md` etter flettingen. Svaret kl. 22:59 står ikke i repoet ennå; det som står her om det, er hentet fra instruksjonen. 8.22 og 8.23 er tatt av andre vinduer (PR #138 og grenen `8-23-funnene-fra-brukertesten`), så dette er 8.24.

## Storyen

Som **bruker**, vil jeg ha forklaringen av notatene der de andre valgene har sin, og kunne notere et tenkt kjøp eller salg og slette fra notatene i Min liste, så jeg ikke må gå til aksjesiden for hvert notat.

**Oppfyller:** svaret 10.11 kl. 22:59 · **Begrenses av:** NFR-06, `AD-3`, `AD-10`

**Kontroll — hva testen ser etter:**
- Bryteren «Notater» i Innstillinger står uten «?», og forklaringen står under den, som ved Hjelp og KI-tekst
- Notatene i Min liste har knappene «Noter et tenkt kjøp», «Noter et tenkt salg» og «Slett», med de samme reglene og varslene som på aksjesiden, og innledningen sier det
- **Ville feilet hvis:** «?» sto igjen ved Notater, eller Min liste manglet en knapp, tillot et kjøp aksjesiden ikke tillater, eller sendte svaret til en annen side

**Avhenger av:** 8.21. **Én økt:** ja.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hjelpeteksten bak «?».** *Forslag:* teksten `notatene` i `src/hjelpetekster.py` tas bort sammen med «?», fordi ingen side viser den lenger, og testen krever at hver tekst brukes av en side. Teksten under bryteren og avsnittet i `docs/hjelp.md` står.
2. **Hvilken dag gjelder knappene i Min liste?** *Forslag:* siste dag med kurser for aksjen, som knappene på aksjesiden for siste dag. Sjekkene som lagres, er de som er lagret for den dagen.
3. **«Er du sikker?»** *Forslag:* aksjesiden spør ikke før et notat slettes eller et kjøp noteres (spørsmål 7 i 8.21), så Min liste spør heller ikke. Det eneste stedet appen spør, er «Fjern» for en aksje med et åpent kjøp, og den siden er den samme.
4. **Hvor går svaret?** *Forslag:* tilbake til «Mine notater» i Min liste, med «Alle» hvis siden viste alle. Perioden i Min liste tas ikke med, fordi notatene ikke avhenger av den.
5. **En aksje som fjernes i kveld.** *Forslag:* som på aksjesiden: ingen knapp for kjøp eller salg, og en linje ved notatet som sier hvorfor. «Slett» står.
6. **Nye notater.** *Forslag:* skrives fortsatt bare på aksjesiden, fordi notatet får dagen siden viser.

## Delene

### A) Uten «?» ved Notater

`src/templates/innstillinger.html` uten `hjelpeknapp` og `hjelpevindu`, og uten teksten `notatene` i `src/hjelpetekster.py`.

**Ville feilet hvis:** «?» eller vinduet sto igjen på Innstillinger, eller teksten sto uten en side som viste den.

### B) Knappene i Min liste

`_Notatet` i `src/app.py` har siste dag, om det kan noteres, og om aksjen fjernes i kveld, regnet med de samme reglene som på aksjesiden. `_notat.html` viser knappene med navnet på aksjen, og skjemaene sender `vis=min-liste` eller `vis=min-liste-alle`, så svaret går tilbake til Min liste.

**Ville feilet hvis:** en knapp manglet, et kjøp kunne noteres for en aksje med et åpent kjøp eller en som fjernes i kveld, kjøpet fikk sjekkene for en annen dag, eller svaret gikk til aksjesiden.
