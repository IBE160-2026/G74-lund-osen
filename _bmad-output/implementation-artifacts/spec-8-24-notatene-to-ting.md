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

## Bygget 11.11

Bygget på grenen `8-24-notatene-to-ting`, i worktreen `G74-lund-osen-8-24`, fra origin/main (`f68c6f89`), i `efb3f25a`.

- **Filene:** `src/templates/innstillinger.html` og `src/hjelpetekster.py` (del A); `_Notatet`, `_kan_kjoepe` og `_alle_notatene` i `src/app.py`, `MIN_LISTE_TILBAKE`, `src/templates/_notat.html` og `src/templates/index.html` (del B); `docs/hjelp.md` og README-en (teksten under bildene av Min liste og Innstillinger).
- **Tester:** `tests/test_notater.py` (`TestKnappeneIMinListe`, `TestUtenSpoersmaalstegn` og `TestMinListeEtterGjennomgangen`). To eldre tester er endret etter svaret: den som krevde «?» ved bryteren, og den som krevde at Min liste ikke hadde skjemaer. `/innstillinger` er tatt ut av `SIDENE` i `tests/test_hjelpetekster.py`, fordi siden ikke har «?» lenger.
- **Bildene:** `notatene-min-liste-demo.png` (1346 px, var 1182) og `innstillinger-demo.png` (1060 px, var 1062) er tatt på nytt. De elleve andre var byte for byte de samme.

## Mutantene

På `efb3f25a` to, én per del: A («?» satt tilbake ved Notater) og B (Min liste uten knappene). Begge ble fanget av `tests/test_notater.py`, og hver fil var lik HEAD etterpå (kopi før, sha256 mot HEAD etter).

## Gjennomgangen 11.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, uten bildene og `tests/test_docker.py`, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 10 funn, Edge Case Hunter 6 og Verification Gap 6.

**Middels**
- *ECH1 og VG5, rettet.* Min liste godtar en valgt dag, men knappene lagret sjekkene for siste dag, og hjelpen sa «slik de sto på siden». Nå står knappene for kjøp og salg bare når Min liste viser siste børsdag, som på aksjesiden, og en linje sier hvorfor. Hjelpen sier «sjekkene for siste dag med kurser, slik de står på aksjesiden for den dagen».
- *BH2, rettet.* Regelen for et nytt kjøp står i én funksjon, `_kan_kjoepe`, for begge sidene.
- *VG1, VG2 og VG3, rettet.* Testene har nå en aksje med en annen siste dag, en aksje som fjernes i kveld med et åpent kjøp, en aksje som er tatt ut, og en valgt dag.
- *BH1, ikke en feil.* Bildene og `tests/test_docker.py` var holdt utenfor diffen Blind Hunter fikk; begge er med i `efb3f25a`.
- *BH3, ikke en feil.* Et avvist trykk gir 400, som på aksjesiden, ikke aksjesiden.

**Lav**
- *Rettet:* BH4 og ECH3 (grunnen står én gang per aksje, ved det nyeste notatet), BH5 og ECH5 (Min liste sier hvorfor knappene mangler for en aksje som er tatt ut eller ikke har kurser), BH7 (salget før kjøpet har kursen) og ECH4 (navnet på aksjen i etiketten på «Slett» i Min liste).
- *Ført:* ECH2 og BH6 (svaret fra Min liste beholder «Alle», men ikke perioden, sorteringen eller filteret), ECH6 (en side åpnet før kveldshentingen gir 400 etter den, som på aksjesiden), VG4 (testen for ett åpent kjøp sjekker ikke knappen ved notatet med kjøpet), VG6 og BH8 (ingen test sjekker hjelpereglene på Innstillinger, nå uten «?») og BH10 (skjemaene har ingen CSRF-token; Origin sjekkes, som før).
- *Ikke en feil:* BH9 (teksten under bryteren sier fortsatt at et tenkt kjøp eller salg får neste sluttkurs).
