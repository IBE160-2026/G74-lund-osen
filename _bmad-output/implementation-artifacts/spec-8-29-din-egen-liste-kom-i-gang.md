---
title: 'Story 8.29: «Din egen liste: kom i gang» som tavla, og investorknappen 44 px'
type: 'feature'
created: '2026-11-13'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '46692396'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-22-foelg-en-aksje-og-min-liste.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-26-vis-meg-rundt-spiller-av-siden.md'
---

Skrevet 13.11 i instruksjonen kl. 11:26, etter gruppens svar 13.11 kl. 10:32–10:54, med tavla «Min liste» 13.10, og tillegg 1 kl. 11:26 (gruppens ønske og svar kl. 10:59–11:02). Tillegget ble først limt inn kl. 11:04, før instruksjonen, og stoppet da i steg 0. Et første innlimingsforsøk av instruksjonen var avkortet og ble ikke utført. 8.27 og 8.28 er tatt av andre vinduer, så dette er 8.29. Svarene står ikke i repoet ennå; det som står her om dem, er hentet fra instruksjonen og tillegget.

## Storyen

Som **bruker i demoen og den ekte versjonen**, vil jeg at «Din egen liste: kom i gang» i Min liste ser ut som på tavla, med én overskrift, titler som ikke skrives oppå seg selv og kort som står tett, og at knappen til investorsiden er stor nok å trykke på, så siden er roligere og lettere å bruke på en mobil.

**Oppfyller:** svarene 13.11 kl. 10:32–10:54 og 10:59–11:02 · **Begrenses av:** NFR-06, `AD-10`, regel 22

**Avhenger av:** 8.22, 8.26. **Én økt:** ja.

## Svarene

*Svar 2026-11-13 kl. 10:32–10:54 (gruppens svar, tavla «Min liste» 13.10 foran seg, rådet anbefalte det):* «Din egen liste: kom i gang» bygges med tallene fra tavla, likt i demoen og den ekte versjonen: én overskrift (h2, Newsreader 32 px, vekt 500), titlene i kortene 21 px med linjehøyde 1,2, teksten 16 px med linjehøyde 1,5, stegkortene med 18 px luft (20 px nederst), 14 px hjørner og 14 px mellom, brikkene i steg 3 30 px høye, og steg 2 sier at startskriptet spør etter nøkkelen. Investorknappen på aksjesiden blir minst 44 px høy, som skissen 06.11 (`docs/skisser/2026-11-06/investorsiden-i-demoen.png`).

*Ønske og svar 2026-11-13 kl. 10:59–11:02 (tillegg 1, rådet anbefalte begge og har prøvd dem):* delen får ingen ramme, ingen egen bakgrunn og ingen luft på sidene (dette erstatter punkt d om bakgrunnen var(--bakgrunn) med kanten), og bransjekortene i «Følg flere aksjer» stables i kolonner uten hull.

## Spørsmål til gruppen

Et spørsmål stopper ikke arbeidet; alt er bygget etter forslaget.

1. **Luften over og under delen.** Tillegget sier at avstanden over og under er som nå. Før hadde delen 40 px margin over, 20 px luft og en kant på 1 px. *Forslag, som bygget:* margen står, og luften over og under er 21 px, så overskriften og kortene står like langt ned som før.
2. **«Dine egne aksjer» på oversikten** bruker den samme klassen (`egne`) og står som et hvitt kort med kant. Tillegget gjelder delen i Min liste. *Forslag, som bygget:* oversikten står som før, og reglene for 8.29 gjelder bare id-en `din-egen-liste`.
3. **Setningen under den gamle overskriften**, «Vil du følge helt andre aksjer, lager du din egen liste. Hver bruker har sin egen gratis nøkkel fra EODHD, som legges inn én gang.», tas bort med overskriften, som instruksjonen sier. At nøkkelen er ens egen, står fortsatt i steg 1 og 2. *Forslag, som bygget.*
4. **Tekstene som viser til overskriften.** README-en (bildeteksten og lista under «Ekstra, ferdig»), `docs/hjelp.md` og siden «eodhd.com» i demoen («Steg 1 i …») sier nå «Din egen liste: kom i gang». Omvisningen og «Vis meg rundt» på main nevner ikke delen. Kommentarene i koden og de daterte linjene i `docs/brukertest.md` og `docs/kvalitetssikring.md` er historikk og står. *Forslag, som bygget.*
5. **Rekkefølgen i «Følg flere aksjer»** leses nå nedover hver kolonne, ikke bortover hver rad, som tillegget sier. `docs/hjelp.md` sier det. *Forslag, som bygget.*
6. **Investorknappen** er 44 px innenfor kanten og 47 px med kanten på 1,5 px, med 11 px luft og 22 px linjehøyde, så teksten står midt i også når den brytes. *Forslag, som bygget.*

## Delene

### 1) Én overskrift (a)

`_egne.html`: «Din egen liste: kom i gang» er h2 med id-en `egen-liste-tittel`, som `aria-labelledby` på delen viser til. Overskriften «Din egen liste», setningen under og h3-en er borte. Setningen «Appen kjører på din egen maskin …» står.

### 2) Kortene og brikkene (b, c, e, f)

`stil.css`, under `#din-egen-liste`: titlene 21 px med linjehøyde 1,2, teksten 16 px med 1,5, stegkortene med 18 px luft (20 px nederst), 14 px hjørner og 14 px mellom, og brikkene 30 px høye, 12 px luft, 13 px tekst med vekt 600, 6 px mellom og ikonet 13 px. «Åpne eodhd.com» og «+ Følg en aksje» står som før. Steg 2 har ikke felt eller knapp (AD-10), og setningen er «Nøkkelen står på kontosiden hos EODHD. Startskriptet til den ekte versjonen spør etter den første gang, og den lagres bare på denne maskinen.»

### 3) Delen uten ramme (tillegg 1, steg 1)

Delen har ingen ramme, bakgrunn eller luft på sidene, og står 136–1144 px ved 1280 px, i linje med tabellen over og «Mine notater» under. Stegkortene og bransjekortene står hvite.

### 4) Bransjekortene i kolonner (tillegg 1, steg 2)

`.bransjekort { columns: 3 260px; column-gap: 16px; }`, og hvert kort har `break-inside: avoid` og 16 px under. Rekkefølgen i HTML-en er som før. Målt i demoen ved 1280 px: tre kolonner, og delen med kortene er 519 px høy, som tillegget regnet med (678 med radene). Ved 390 px én kolonne.

### 5) Investorknappen (steg 3)

`p.investorboble a` har `min-height: 44px`, 11 px luft og 22 px linjehøyde, i begge versjonene. ↗ og ny fane står bare i den ekte versjonen.

## Målt i nettleseren 13.11 kl. 11:31

Edge uten vindu, mot en demobase og en testbase i midlertidige mapper, på en ledig port (ikke 8000).

| | Demo 1280 | Demo 390 | Ekte 1280 | Ekte 390 |
|---|---|---|---|---|
| Delen, venstre–høyre | 136–1144 | 16–374 | 136–1144 | 16–374 |
| Ramme og bakgrunn | ingen | ingen | ingen | ingen |
| h2 i delen | 1, 32 px, 500 | 1 | 1 | 1 |
| Titlene, linjehøyde | 25,2 px | 25,2 px | 25,2 px | 25,2 px |
| Brikkene | 30 px | 30 px | (ingen ferdige lister) | (ingen) |
| Kolonner med bransjekort | 3, 519 px | 1 | 3, 519 px | 1 |
| Investorknappen | 46 px | 46 px | 46 px | 46 px |

Fokusringen er den samme som for de andre knappene (`*:focus-visible`, 3 px i blekk).

## Bildene

`min-liste-demo.png`, `din-egen-liste-demo.png` (1709 → 1339 px) og `notatene-min-liste-demo.png` er tatt på nytt; de andre bildene er byte for byte de samme. Ingen av bildene viser investorknappen. Avtrykkene i `test_docker.py` er regnet ut på nytt.
