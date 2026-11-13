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

Skrevet 13.11 i instruksjonen kl. 11:26, etter gruppens svar 13.11 kl. 10:32–10:54, med tavla «Min liste» 13.10, og tillegg 1 kl. 11:26 (gruppens ønske og svar kl. 10:59–11:02). Tillegget ble først limt inn kl. 11:04, før instruksjonen, og stoppet da i steg 0. Et første innlimingsforsøk av instruksjonen var avkortet og ble ikke utført. 8.27 og 8.28 er tatt av andre vinduer, så dette er 8.29. Tillegg 2 kl. 20:38 (gruppens ønske kl. 20:35) gjelder styrken for én dag. Svarene står ikke i repoet ennå; det som står her om dem, er hentet fra instruksjonen og tillegget.

## Storyen

Som **bruker i demoen og den ekte versjonen**, vil jeg at «Din egen liste: kom i gang» i Min liste ser ut som på tavla, med én overskrift, titler som ikke skrives oppå seg selv og kort som står tett, og at knappen til investorsiden er stor nok å trykke på, så siden er roligere og lettere å bruke på en mobil.

**Oppfyller:** svarene 13.11 kl. 10:32–10:54 og 10:59–11:02 · **Begrenses av:** NFR-06, `AD-10`, regel 22

**Avhenger av:** 8.22, 8.26. **Én økt:** ja.

## Svarene

*Svar 2026-11-13 kl. 10:32–10:54 (gruppens svar, tavla «Min liste» 13.10 foran seg, rådet anbefalte det):* «Din egen liste: kom i gang» bygges med tallene fra tavla, likt i demoen og den ekte versjonen: én overskrift (h2, Newsreader 32 px, vekt 500), titlene i kortene 21 px med linjehøyde 1,2, teksten 16 px med linjehøyde 1,5, stegkortene med 18 px luft (20 px nederst), 14 px hjørner og 14 px mellom, brikkene i steg 3 30 px høye, og steg 2 sier at startskriptet spør etter nøkkelen. Investorknappen på aksjesiden blir minst 44 px høy, som skissen 06.11 (`docs/skisser/2026-11-06/investorsiden-i-demoen.png`).

*Ønske og svar 2026-11-13 kl. 10:59–11:02 (tillegg 1, rådet anbefalte begge og har prøvd dem):* delen får ingen ramme, ingen egen bakgrunn og ingen luft på sidene (dette erstatter punkt d om bakgrunnen var(--bakgrunn) med kanten), og bransjekortene i «Følg flere aksjer» stables i kolonner uten hull.

*Ønske 2026-11-13 kl. 20:35 (tillegg 2, rådet anbefalte å ta det i 8.29):* styrken for én dag vises likt overalt, med regelen fra tabellen på oversikten: 3 av 3 som pille tre-av-tre, fra terskelen (2 av 3) som pille to-av-tre, og 1 og 0 av 3 som tekst uten pille. Det gjelder notatene (Min liste, aksjesiden og panelet) og «Signalet dag for dag», i begge versjonene. Summen under sjekkene og kortet «Signalstyrke» står som før. Punktet sto som lavt i `issues.md` fra 8.27.

## Spørsmål til gruppen

Et spørsmål stopper ikke arbeidet; alt er bygget etter forslaget.

1. **Luften over og under delen.** Tillegget sier at avstanden over og under er som nå. Før hadde delen 40 px margin over, 20 px luft og en kant på 1 px. *Forslag, som bygget:* margen står, og luften over og under er 21 px, så overskriften og kortene står like langt ned som før.
2. **«Dine egne aksjer» på oversikten** bruker den samme klassen (`egne`) og står som et hvitt kort med kant. Tillegget gjelder delen i Min liste. *Forslag, som bygget:* oversikten står som før, og reglene for 8.29 gjelder bare id-en `din-egen-liste`.
3. **Setningen under den gamle overskriften**, «Vil du følge helt andre aksjer, lager du din egen liste. Hver bruker har sin egen gratis nøkkel fra EODHD, som legges inn én gang.», tas bort med overskriften, som instruksjonen sier. At nøkkelen er ens egen, står fortsatt i steg 1 og 2. *Forslag, som bygget.*
4. **Tekstene som viser til overskriften.** README-en (bildeteksten og lista under «Ekstra, ferdig»), `docs/hjelp.md` og siden «eodhd.com» i demoen («Steg 1 i …») sier nå «Din egen liste: kom i gang». Omvisningen og «Vis meg rundt» på main nevner ikke delen. Kommentarene i koden og de daterte linjene i `docs/brukertest.md` og `docs/kvalitetssikring.md` er historikk og står. *Forslag, som bygget.*
5. **Rekkefølgen i «Følg flere aksjer»** leses nå nedover hver kolonne, ikke bortover hver rad, som tillegget sier. `docs/hjelp.md` sier det. *Forslag, som bygget.*
6. **Investorknappen** er 44 px innenfor kanten og 47 px med kanten på 1,5 px, med 11 px luft og 22 px linjehøyde, så teksten står midt i også når den brytes. *Forslag, som bygget.*

7. **Plassstreken på beige.** Uten den hvite bakgrunnen har de ledige rutene i streken under «Appen følger N av 18» (`--strek-2`) omtrent 1,3:1 i kontrast mot sidens bakgrunn, mot omtrent 1,5:1 mot hvitt før (ECH3). Streken er skjult for skjermlesere, og tallet står som tekst. *Forslag, som bygget:* streken står som før; en mørkere farge for de ledige rutene kan tas i en egen runde.

8. **2 av 3 en tidligere dag** (tillegg 2). `designregler.md` §3 (01.10) sier «2 av 3 merkes uten gult, og bare for siste børsdag», og to tester holdt det: `test_to_av_tre_har_ingen_ring_en_tidligere_dag` (8.20a, BH11 og ECH1) og `test_3_av_3_merkes_som_i_oversikten_og_2_av_3_ikke` i `test_historikken.py`. Tillegget og skissen 06.11 (`docs/skisser/2026-11-06/aksjesiden-ki-paa.png`, onsdag 04.11 med «2 av 3» i pille) har den hvite pillen også en tidligere dag. *Forslag, som bygget:* som tillegget og skissen. §3 har en linje om det, testen i 8.20a sjekker nå bare summen og kortet en tidligere dag, og testen i `test_historikken.py` heter `test_styrken_merkes_som_i_tabellen_paa_oversikten`.
9. **Andre steder med styrken for én dag.** Setningen «Signal: 2 av 3, …» for en valgt dag på aksjesiden er tekst, som tabellen for en valgt dag («Velg dag»). Børsometeret har pille ved mørk og gul ramme og ellers tekst, som tabellen. Lista for skjermlesere under hovedindeksen nevner bare «3 av 3» i teksten. *Forslag, som tabellen:* de står som før.

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

### 6) Styrken for én dag (tillegg 2)

Makroen `styrke` i `_brikker.html` har regelen, og `_notat.html` og «Signalet dag for dag» i `aksje.html` bruker den med `parametre.terskel`. Tabellen har samme regel med `skiller_seg_ut`. `stil.css` har den hvite pillen og teksten uten pille under `.etterpaa` (også i panelet) og `.historikk`.

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

## Gjennomgangen 13.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `46692396..94234186`, med tre lesere som ikke så hverandres funn. 21 funn: 19 rettet (VG8 delvis), 1 avvist og 1 utsatt. Rettingene står i commiten etter `94234186`.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | høy | Testene ba om både `klient` og `ekte`; `ekte` tok bort `OSE_DEMO`, så demoen ble aldri prøvd | Rettet: én fikstur per test med `request.getfixturevalue`, og testen sjekker at det er riktig versjon |
| BH1 | middels | Overskriftene hoppet fra h2 til h4 | Rettet: titlene i stegkortene er h3 |
| BH2, ECH2, VG9 | middels | Fast høyde på brikkene, så teksten kunne gå ut av dem | Rettet: bare `min-height: 30px`, og testen ser at teksten er inne |
| VG2 | middels | Linja mot tabellen ble ikke sjekket uten tabell, og ikke mot «Mine notater» eller 136–1144 | Rettet |
| VG3 | middels | Fokusringen var ikke prøvd | Rettet: en brikke (eller knappen i steg 1) og investorknappen får fokus, og ringen er 3 px |
| BH3, ECH4, VG1 | lav | Luft under det siste kortet | Rettet: målt, ved 1280 px kuttes margen i kolonnebruddet, men ved 390 px ga den 16 px; `:last-child` har ingen marg, og testen måler 0 |
| ECH5 | lav | Linjehøyden 1,5 traff også avsnittet med knappen | Rettet: `p:not(.handling)` |
| BH4 | lav | Kommentaren ga 44 px uten kanten | Rettet: 44 px innenfor kanten, 47 px med |
| BH5, VG5 | lav | Tre kolonner hviler på testdataene, og to kolonner var ikke prøvd | Rettet: 700 px gir to, og docstringen sier testdataene |
| VG4 | lav | At kortene er hvite, var ikke prøvd | Rettet |
| VG6 | lav | Nettlesertesten bare i demoen | Rettet: begge versjonene |
| VG7 | lav | Ny fane bare sjekket med ↗ | Rettet: også `target` og «(åpnes i en ny fane)» |
| VG8 | lav | Overskriften bare sjekket som tekst i stilen | Rettet for h2 (32 px, 500, Newsreader i nettleseren); luften og hjørnene i stegkortene er fortsatt bare sjekket i stilen, utsatt |
| ECH6 | lav | Avrunding kunne gi 15 eller 17 px mellom kortene | Rettet: ±1 px |
| BH6 | lav | En tittel kunne strekkes av «?»-knappen | Avvist: `.steg-topp` har `align-items: center` (stil.css), og titlene måles som hele linjer |
| ECH3 | lav | Kontrasten i plassstreken på beige | Utsatt: spørsmål 7 |

## Gjennomgangen av tillegg 2 (13.11, Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `d905cb62..99d454b3`, med tre lesere som ikke så hverandres funn. 15 funn: 12 rettet (VG4 delvis), 2 avvist og 1 utsatt. Rettingene står i `6d3d46ea`.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| BH1 | middels | `signalet` leser `parametre.terskel` fra konteksten, og ingen test hentet sidene med notater | Rettet: Edge Case Hunter slo opp at `parametre` kommer fra context-prosessoren på alle sidene, og en test henter Min liste, aksjesiden og oversikten (panelet) med notater i den ekte versjonen |
| VG1 | middels | Den ekte versjonen var ikke prøvd med 0–3 på en side | Rettet: basen fra `test_historikken.py` (EQNR med 3, 0, 2 og 1 av 3), og testen krever alle fire |
| VG2, ECH3, BH3 | middels | Notatene på sidene kunne bestå uten et eneste notat | Rettet: ett notat hver av de fire dagene, og testen krever 0–3 på hver side |
| BH2 | middels | Testen og malen kunne få terskelen fra to steder | Rettet: testen sjekker at malen får samme terskel |
| BH4 | lav | Kortet kunne kuttes for tidlig i testen fra 8.20a | Rettet: testen krever styrken i kortet |
| BH5, ECH1 | lav | Hjelpen sa «som i tabellen» og 2 av 3 uten terskelen, mens tabellen viser tekst for en valgt dag | Rettet: hjelpen og kommentaren sier regelen tabellen har for siste børsdag, og terskelen |
| VG3 | lav | Testen av cellen feilet uforståelig hvis cellen ble flyttet | Rettet |
| VG4 | lav | Stilen bare sjekket som tekst | Rettet for selektorene med omfang; en nettlesertest av stilen er utsatt |
| VG5 | lav | Summen og kortet bare sjekket i demoen | Rettet: en tidligere dag med 2 av 3 i den ekte versjonen |
| BH6 | lav | §3 i designreglene var ikke rettet i diffen | Avvist: linja står i `17bd178d`, utenfor diffen |
| BH7 | lav | Stilen for notatene gjelder bare under `.etterpaa` | Avvist: begge kallene står inne i `.etterpaa` (Edge Case Hunter slo det opp) |
| ECH2 | lav | Setningen for en valgt dag viser styrken som ren tekst | Utsatt: spørsmål 9 |

## Mutantene

| Mutant | Commit | Endringen | Utfall |
|---|---|---|---|
| M1 | `be35000a` | `min-height: 30px` til `20px` for brikkene i steg 3 i `stil.css` | Fanget av `test_brikkene_i_stilen` og `test_delen_i_nettleseren` ved 1280, 700 og 390 px i demoen; den ekte versjonen har ingen ferdige lister. `stil.css` var lik HEAD etterpå (`git hash-object`). |
| M2 | arbeidskopien før `99d454b3` | `verdi >= terskel` til `verdi > terskel` i makroen `styrke` i `_brikker.html` (tillegg 2) | Fanget av 7 tester: `test_i_notatet` og `test_i_signalet_dag_for_dag` med 2 av 3 i begge versjonene, `test_paa_sidene` i begge og `test_styrken_merkes_som_i_tabellen_paa_oversikten`. `_brikker.html` var lik før etterpå (`git hash-object`). |
