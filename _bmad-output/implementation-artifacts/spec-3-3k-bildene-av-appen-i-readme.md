---
title: 'Story 3.3 (3.3k): bildene av appen i README-en i rekkefølgen fra knapperaden, med mobilbildene i egen mappe'
type: 'feature'
created: '2026-11-14'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '21876255'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3f-bildene-av-appen-bak-en-knapp.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-26-vis-meg-rundt-spiller-av-siden.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-27-mine-notater-i-panel.md'
---

Skrevet 14.11 etter instruksjonen 12.11 kl. 17:11 (gruppens svar 12.11 kl. 17:09) og tilleggene 1–6 (12.11 kl. 17:59, 20:10, 20:51, 21:03 og 21:25, og 13.11 kl. 11:26), med det felles tillegget for køen 13.11 kl. 18:25. Grenen er laget fra origin/main (`21876255`) da Utført-linjene og done for de sju storyene sto der: 8.26, 8.27, 3.7, 10.11 («av bransjene med minst to aksjer»), 8.19, 8.28 («De 15 mest omsatte») og 8.29, og 9.11 var flettet. 3.3b–3.3j er brukt, så dette er 3.3k, etter 3.3f (bildene av appen bak en knapp). Instruksjonen og tilleggene står ikke i repoet ennå; de føres i dagsfilene med flettingen (regel 18).

## Storyen

Som **faglærer eller sensor som leser README-en**, vil jeg se bildene av appen i samme rekkefølge som knappene øverst i appen, med sidene man kommer til rett etter, og bildene fra smal skjerm for seg, så jeg finner fram og ser at mobil kommer senere.

**Oppfyller:** svaret 12.11 kl. 17:09 og tilleggene 1–6 · **Begrenses av:** regel 16 (bare demoen), regel 19, regel 22 (demobasen i en midlertidig mappe)

**Avhenger av:** 3.3f, 8.26, 8.27, 3.7, 10.11, 8.19, 8.28, 8.29. **Én økt:** ja.

## Svarene

*Svar 2026-11-12 kl. 17:09 (gruppens svar, instruksjonen kl. 17:11):* bildene i README-en står i rekkefølgen fra knapperaden, med sidene man kommer til rett etter. Rådet anbefalte rekkefølgen og to nye bilder; gruppen valgte en egen mappe for mobil, fordi den viser at sidene alt virker i smal bredde, og at mobil kan komme senere.

*Svar 2026-11-12 kl. 16:23 (tillegg 1):* linja nederst på sidene, «Appen er under utvikling og ikke ferdig.», rettes slik README-en ble rettet i 8.26, før bildene tas. Det gjelder demoen og den ekte versjonen likt.

*Svar 2026-11-12 kl. 20:06 (tillegg 2):* bildene tas når «De 15 mest omsatte» (8.28) også er flettet, og bildet av «Følg en aksje» viser lista.

*Svar 2026-11-12 kl. 20:44 (tillegg 3):* PR-en flettes uten nytt stopp, etter PRD-en (9.11). Forslagene i spesifikasjonen godtas som bygget, også ordene for linja nederst på sidene. Stopp bare ved avvik eller en ny avgjørelse.

*Rådets gjennomgang 2026-11-12 kl. 21:00 (tillegg 4):* ventingen ser også etter done i `sprint-status.yaml` på origin/main.

*Ønske 2026-11-12 kl. 21:15 (tillegg 5):* tabellen «Demoen og den ekte versjonen» får alle forskjellene etter natten, og det som er likt, får ingen rad.

*Svar 2026-11-13 kl. 10:32–10:54 (tillegg 6):* bildene venter også på 8.29 og viser den. Tabellen får ingen rad for 8.29, fordi endringen er lik i begge versjonene.

*Svar 2026-11-13 kl. 18:24 og 18:26 (felles tillegg):* kveldshentingen hoppes over i kveld, hele settet kjøres i CI, og rekkefølgen er 8.27, 8.19, 8.28, 9.11, 8.29, bildene 3.3k og 9.12.

## Spørsmål til gruppen

Besvart 12.11 kl. 20:44 (tillegg 3): forslagene godtas som bygget. Et spørsmål stoppet ikke arbeidet.

1. **Ordene i linja nederst på sidene** (tillegg 1). README-en sier etter 8.26 «Versjon 1 er ferdig» i beskrivelsen og under «Status», og tar ikke linja bort. *Forslag, som bygget:* linja sier «Versjon 1 er ferdig.», i begge versjonene. Bryteren `UNDER_ARBEID` og navnene `UNDER_ARBEID_TEKST` og klassen `under-arbeid` står, så endringen er bare teksten; `docs/innlevering.md` §5 får en datert linje om det.
2. **Hvor bildene ved 390 px står.** Instruksjonen sier en egen sammenleggbar del til slutt. *Forslag, som bygget:* en egen pil, «Bilder av appen på mobil (demoen)», rett etter pila «Bilder av appen (demoen)» og før «Innhold», med setningen først og så bildene i samme rekkefølge som over.
3. **Setningen om mobil.** *Forslag, som bygget:* «Sidene virker alt i smal bredde, men i v1 svarer appen bare på denne maskinen (127.0.0.1), så mobil kommer senere.» Det er det samme som `docs/installasjon.md` sier under «Mer for den som vil».
4. **De to nye bildene.** *Forslag, som bygget:* `notatpanelet-demo.png`, oversikten ved 1280 px med panelet «Mine notater» åpent til høyre, de første 1000 px, og `vis-meg-rundt-demo.png`, første steg i «Vis meg rundt» på oversikten ved 1280 px, slik siden står når steget vises. Panelet står etter notatene i Min liste, under «Mine notater», og omvisningen sist, som knappen «Vis meg rundt».
5. **Rekkefølgen innenfor Markedsoversikt og Min liste.** *Forslag, som bygget:* siden selv først (oversikten, Min liste), så sidene man kommer til i den rekkefølgen instruksjonen sier. Aksjesiden har ikke noe bilde ved 390 px, så mobildelen har oversikten, notatene på aksjesiden, investorsiden, børsometeret og «Følg en aksje».
6. **«Mappestruktur».** Punktet for `docs/appen/` nevnte ikke `folg-en-aksje-demo.png`. *Forslag, som bygget:* punktet nevner alle bildene i rekkefølgen fra README-en, med de to nye, og bildene ved 390 px under `docs/appen/mobil/`, i samme punkt.
7. **`docs/hjelp.md`** nevner ingen av bildene eller `docs/appen/`, så den endres ikke. Andre dokumenter som lenker til et flyttet bilde, finnes ikke utenom README-en og testene. Eldre spesifikasjoner (8.20, 8.22, 8.27 og 10.11), dagsfilene og sesjonsloggene i `.logs/` nevner den gamle plassen, `docs/appen/<navn>-390-demo.png`, og endres ikke. *Forslag, som bygget.*
8. **Nye rader i tabellen** (tillegg 5), sjekket i koden: «Neste henting» (8.19: `_ramme.html` viser linja bare når `eksempeltall` er av, og `NESTE_HENTING_STEGET_DEMO` i `hjelpetekster.py` sier i omvisningen at den ekte versjonen viser den), «Investorsiden» (`_investorboble.html`: i demoen `/investorside/<symbol>` i samme fane, ellers selskapets adresse i en ny fane, og ruta svarer 404 i den ekte versjonen) og «Åpne eodhd.com» (`_egne.html`: i demoen `/eodhd-demo`, en side i appen med en tegning laget av KI, ellers `https://eodhd.com/register` i en ny fane). Raden «KI-tekst» stemmer med 3.7 og testen `test_ki_teksten`. *Forslag, som bygget:* de tre radene etter «Notatene».
9. **Forskjeller uten rad.** «Demo Børs» i stedet for «Oslo Børs» i overskriftene følger av raden «Kurser». Merket «Eksempeltall», boksene som sier at demoen ikke henter, «Demoen trenger ingen nøkkel» i steg 2 og setningen i panelet om at notatene står til demoen startes på nytt, er forklart av radene «Kurser», «Trenger», «Endringer i lista» og «Notatene». *Forslag, som bygget:* ingen rad for dem.
10. **«De 15 mest omsatte» og bildet av «Følg en aksje»** (tillegg 2). Tillegget sier at lista endrer siden «Følg en aksje», og at bildet av den viser lista. I 8.28 står lista ikke på `/folg`, men først i steg 3 i «Din egen liste: kom i gang» i Min liste (spørsmål 6 i `spec-8-28-de-15-mest-omsatte.md`, godtatt som bygget). *Forslag, som bygget:* bildet `din-egen-liste-demo.png` viser lista, og alt-teksten og teksten under nevner den; bildet av `/folg` står som siden er. Teksten under bildet sa «Start fra en ferdig liste» nederst, som 8.29 tok bort, og er rettet.
11. **Investorsiden har verken «Vis meg rundt» eller «Spill av omvisningen».** Siden har ingen steg i omvisningen (`investorside.html` fyller ikke `rundtur`), slik den har vært siden 8.26, og det samme gjelder siden for eodhd.com i demoen. Bildene viser det som appen er. *Forslag, som bygget:* 3.3k endrer ikke det; om de to sidene skal ha egne steg, er en egen sak.
12. **Avtrykket bak bildene.** Linja nederst kommer fra `app.py`, som avtrykket for oversikten ikke har med, så oversikten ved 390 px endret seg uten at avtrykket gjorde det. *Forslag, som bygget:* avtrykket har `UNDER_ARBEID_TEKST` med, som merket «Eksempeltall», og alle avtrykkene er regnet ut på nytt.

## Delene

### 1) Linja nederst på sidene (tillegg 1)

`src/app.py`: `UNDER_ARBEID_TEKST = "Versjon 1 er ferdig."`. Testen i `tests/test_app.py` sjekker de nye ordene, og at de gamle ikke står. `docs/innlevering.md` §5 får en linje om det.

### 2) Bildene tatt på nytt

Alle bildene tas på nytt fra grenen i demoen, med en demobase i en midlertidig mappe og demoserveren på en ledig port, aldri 8000. Et bilde som er likt byte for byte, byttes ikke. Hvert bilde sjekkes mot det gruppen har avgjort: «Vis meg rundt», «Spill av omvisningen» og «Mine notater» i raden øverst, ingen «3 av 3 positiv/negativ», ingen eksempelboks, «ingen kurser ennå» for Matfjord Merkevarer, og dagsteksten med «av bransjene med minst to aksjer». To nye: panelet og første steg i «Vis meg rundt».

### 3) README-en

Toppen av oversikten først som før. I pila «Bilder av appen (demoen)»: Markedsoversikt (oversikten, aksjesiden, notatene på aksjesiden, investorsiden), Børsometer, Min liste (Min liste, «Din egen liste: kom i gang», «Følg en aksje», notatene i Min liste), Mine notater (panelet), Innstillinger og «Vis meg rundt». Bildene ved 390 px flyttes med `git mv` til `docs/appen/mobil/` og står i pila «Bilder av appen på mobil (demoen)», med setningen om mobil. «Mappestruktur» følger (regel 19).

### 4) Tabellen «Demoen og den ekte versjonen»

Tre rader etter «Notatene»: «Neste henting», «Investorsiden» og «Åpne eodhd.com», med testene i `tests/test_vis_meg_rundt_8_26.py` og rekkefølgen i `tests/test_docker.py`.

### 5) Testene

`tests/test_docker.py`: bildene og rekkefølgen i README-en, mappa `docs/appen/mobil/`, at hver bildelenke peker på en fil som finnes, og avtrykkene. Hver ny test sier «Ville feilet hvis».

## Kontroll

- Testfilene storyen endrer, og de som leser filene den endrer, lokalt; `uv run pytest --dokumentene` før push; hele settet i CI (felles tillegg, gruppens svar 13.11 kl. 18:24).
- Én mutant, med en kopi før og sha256 mot HEAD etter.
- Gjennomgang med Edge Case Hunter, og triage.
- Bilder før og etter på en egen bildegren.
