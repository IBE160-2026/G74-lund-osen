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

*Svar 2026-11-10 kl. 11:52 (gruppens svar):* alle åtte forslagene er godtatt, også spørsmål 8, som står nederst. BH1 og BH4 lukkes som avgjort av gruppen, med graden urørt (regel 25). Rådet anbefalte det. Svaret er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`.

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

## Mutantene

Én per del og regel på `d20090b6`, med kopi før og fila lik HEAD etterpå: A1 (et tall skrevet for hånd i «Tallene bak») overlevde først, fordi det samme tallet sto i steget om kursgrafen, og ble fanget da testen så på hvert steg for seg (`a4111592`). A2 (en egen tekst for signalstyrken) fanget av `test_samme_tekster_som_hjelpen`, B1 (børsometeret uten knappen) av `test_knappen_og_stegene_peker_paa_noe_som_finnes`, B2 (aksjesiden alltid med sjekkene) av `test_aksjesiden_uten_sjekker`, og B3 (knappen uten «Vis hjelp») av `test_borte_naar_hjelpen_er_av`.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `1a72810a..a4111592`, uten `tests/test_docker.py` og bildene: Blind Hunter med bare diffen (12 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (5 og 4 funn; om lag 40 tilstander av sidene, også demoen, og 6 mutanter i en kopi utenfor worktreen). Ingen høye.

**Middels**
- *ECH1, rettet.* Når lista er full, viser «Følg en aksje» ikke søket, men knappen sto, og «Søk» pekte på `#q`, som ikke finnes. Knappen står nå bare når søket står.
- *VG1 og BH2, rettet.* Testene så bare standardtilstandene. Nå `test_ikke_der_stegene_ikke_passer`: «Bytt ut», en full liste og Min liste uten merkede aksjer. Edge Case Hunter fant alle ankrene i de andre tilstandene (periode, valgt dag, sortering, KI av, kort serie, uten hovedindeks, søk, demoen).
- *ECH5, rettet.* Stegene om retningen, styrken og sjekkene brukte tekstene bak «?», ikke tekstene fra tavla som tillegget 13.10 i epics.md krever. Nå er de ordrett fra «Kan tas som de står» i punkt 4.2 i endringsforslaget 13.10 (`TAVLA_RETNING`, `TAVLA_STYRKEN`, `TAVLA_SJEKKENE`), og `test_tekstene_fra_tavla` leser dem i forslaget. Retningen står uten «Ikke et råd om å kjøpe eller selge.», som etter merknaden der ikke kan bli en vanlig hjelpetekst. Mutanten med den gamle teksten ble fanget.
- *BH3, rettet.* Testen av ankrene godtok `data-id="q"` og to like id-er. Nå en hel id, og nøyaktig én. Det samme i `test_utseende.py`.
- *BH1, ført.* På en dag uten sjekker står fortsatt overskriften og «?» for sjekkene, med teksten for en side uten sjekker. Spørsmål 4 og hjelpen sier at sjekkene ikke vises, og det gjelder kortene; stegene om dem står ikke.
- *BH4, ført.* Signalstyrken og retningen peker på tabellen, og «Tallene bak» på sjekkene, som «Sjekkene». Det er delen de forklarer.
- *BH1 og BH4, lukket 2026-11-10 som avgjort av gruppen* (svaret kl. 11:52), middels som før (regel 25).
- *BH5, ikke reelt.* Tekstene er vanlige strenger uten HTML.

**Lav**
- *Rettet:* ECH2 («Tabellen» sier at «Skilte seg ut» gjelder siste børsdag uten sortering), ECH3 («Kursgrafen» sier snittet og hovedindeksen når serien og indeksen har dem), ECH4 (Min liste har knappen når du har merket en aksje, og «Aksjene dine» nevner «Alle»), VG2 og BH8 (volumfaktoren er med i testen av tallene), BH11 (hjelpen sier når «Følg en aksje» har knappen).
- *Ført:* BH6 (ankrene er tomme `span`, så malen ellers er som før), BH7 (pila i `summary` er borte med `inline-block`; knappen har ramme og står alene), BH9 (`assert` for antallet steg; testen `test_hoeyst_sju_steg` er vakten), BH10 (en ny side uten `vis_hjelp` i konteksten; alle sidene får den fra innstillingene), BH12 (filteret i `test_boersometer.py` er den eksakte strengen), VG3 (demoen er prøvd av Edge Case Hunter, ikke i testene), VG4 (tekstene fra tavla er nå like, ikke `in`).
- *Spesifikasjonen:* spørsmål 7 sier tre tester er endret, men nevner to; den tredje er avtrykkene i `tests/test_docker.py`.

*Lagt til 2026-11-09 under spørsmål 3 (gjennomgangen, ECH5):* stegene bruker nå tekstene fra tavla, ikke tekstene bak «?». Forslaget er det samme: godta.

*Lagt til 2026-11-09 (hele settet i deler):* to tester feilet etter gjennomgangen, og begge hadde rett. `test_fotnoten_under_summen_er_flyttet_til_hjelpen` (8.20a) krever at «Ingen vekting og ingen skjult formel» ikke står på aksjesiden, og den setningen er den siste i teksten fra tavla om sjekkene. Steget har nå teksten uten den, som retningen uten rådsetningen. `test_ki_teksten_under_regelforklaringen` leser rekkefølgen av overskriftene, og «Signalet dag for dag» i toppen sto før «Signalet forklart»; steget heter nå «Dag for dag». Ingen test er svekket.

8. **Tavla og 8.20a.** Tillegget 13.10 sier at stegene bruker tekstene fra tavla, og 8.20a tok «Ingen vekting og ingen skjult formel.» bort fra aksjesiden. *Forslag:* stegene har tavlas tekster uten de setningene som er tatt bort fra sidene eller ikke kan stå i en hjelpetekst (rådsetningen i retningen). Dette er et svar gruppen må gi før flettingen (regel 25).

*Svar 2026-11-10 kl. 11:52 (gruppens svar):* forslaget i spørsmål 8 er godtatt: stegene har tavlas tekster uten setningene som er tatt bort fra sidene eller ikke kan stå i en hjelpetekst. Rådet anbefalte det. Svaret er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`.
