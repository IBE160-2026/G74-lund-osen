---
title: 'Story 10.2, 10.2g: regelen for retningen Ingen og promptens avtrykk i demotekstene'
type: 'feature'
created: '2026-10-25'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '78e1c8f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2f-grunnen-i-prompten.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** To punkter under «Åpent» i spesifikasjonen 10.2f. Modellen skriver retningen Ingen som et ord i setningen, «Signalet er Ingen, fordi …» (SLVP i demoen, BH10). Og en rad i `src/demo_ki_tekster.json` har bare promptversjonen, ikke avtrykket av prompten, så ingen test skiller tekster fra to prompter med samme versjon (VG1, ECH2, BH13).

**Beslutningen** (under story 10.2 i `epics.md`, *Avgjort 2026-10-25 kl. 19:54 og 19:56*):
- a) Begge punktene rettes i kveld.
- b) Prompten får regelen «- Når retningen er Ingen, skriv at signalet ikke har noen retning.», fordi modellen skrev «Signalet er Ingen, fordi …» (BH10). Rekkefølgen på sjekkene (BH11) står åpen.
- c) Hver rad i `src/demo_ki_tekster.json` får promptens avtrykk ved `promptversjon`, og en test feiler hvis en rad har et annet avtrykk enn prompten (VG1, ECH2, BH13, rådets forslag).
- d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b): ingen tekst i `ose.db` er laget med versjon 3 ennå.

## Approach

**a) Prompten** (`src/ki_prompt.py`): regelen fra svaret b) under «Regler for teksten», avtrykket for versjon 3 i `AVTRYKK` i `tests/test_ki_modell.py` satt på nytt, og docstringen med svaret d).

**b) Demoen:** hver rad i `src/demo_ki_tekster.json` får feltet `promptavtrykk` rett etter `promptversjon`, i `src/demo_ki.py`. Fila leses i `demo_ki.les_radene`, som `demo.py` bruker, og en rad med et annet avtrykk enn prompten avvises der, så demoen lages uten KI-tekst og sier hvorfor, som for en fil som ikke stemmer med demoen (NFR-04). KI-tekstene i demoen lages på nytt (`uv run python src/demo_ki.py`), og bildet av aksjesiden i README-en tas på nytt med avtrykkene, av en demoaksje der teksten besto.

*Utfallet:* KI-tekstene i demoen ble laget på nytt 20:17:51–20:18:20: 13 av 13 besto, 0 ble stoppet, og modellen feilet for 0. Alle har `promptversjon` 3 og `promptavtrykk` `0d427725…0a27`, det samme som `AVTRYKK["3"]`. BRFE, NLYS, SLVP, TRHF og LKSV fikk en annen tekst enn før, og de åtte andre er like. SLVP, den eneste med retningen Ingen, sier nå «Signalet har ingen retning fordi …». Hver er lest mot grunnlaget: alle beskriver hver sjekk slik fortegnet er, og ingen nevner dagene, hovedindeksen, bransjen eller antallet aksjer. Bildet viser fortsatt BRFE, der teksten besto. Teksten er kortere, og bunnen av grafen ble målt i Edge uten vindu til 1894, så bildet er 1280 × 1894 (var 1934). `HOEYDE_PAA_AKSJESIDEN` og `AVTRYKK_BAK_AKSJESIDEN` er satt på nytt. README-teksten under bildet siterer ikke KI-teksten og er ikke endret.

*Valg underveis:* webserveren importerer ikke `ki_prompt` (AD-10, `test_webserveren_importerer_ingen_modell`), og demoen leser fila når den lages. Derfor krever `les_radene` feltet `promptavtrykk` som en sha256, mens sammenligningen med prompten bare gjøres når kalleren gir avtrykket (`prompt=promptavtrykk()`). Testene leser fila slik, så en endret prompt gjør testene røde til tekstene lages på nytt. `promptavtrykk()` importerer `ki_prompt` inne i funksjonen.

**c) Prøvekjøringen** (§48 i `malinger.md`), som i §47, mot `data/db/ki-proeve-v3h.db` for børsdagen 23.10, med hver tekst lest mot grunnlaget og telt for «Ingen» skrevet som et ord. Tabellen sammenligner §34 og §43–§48.

*Utfallet:* kjørt 20:23:20–20:23:38 mot `ki-proeve-v3h.db`: 15 av 15 besto, 0 ble stoppet, og modellen feilet for 0, med median 0,46 s og lengste kall 11,44 s (kall nr. 1). Hver tekst er lest mot grunnlaget: ingen sier feil om en sjekk, og ingen nevner dagene. «Ingen» står som et ord i 0 av de 15, mot 2 i §47 (DNB og TEL, de to med retningen Ingen). Begge sier nå «Signalet har ingen retning fordi …». 7 er ordrett de samme som i §47. sha256 for `ose.db` var den samme før og etter.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Kopien ble laget med skallet på main kl. 20:13:43, før grenen, med samme sha256 som `ose.db` (`e3184c07…f4a4`). Ingen KI-rad i kopien har `promptversjon` 3: alle 75 har 2.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis færre enn 15 tekster i §48 besto, en tekst i §48 sier feil om en sjekk eller nevner dagene, eller sha256 for `ose.db` rett før flettingen ikke er den samme som for kopien.

## Mutantene

To med `-x`, hver med kopi før og sha256 mot HEAD etter: regelen tatt ut av prompten, og sjekken av avtrykket tatt ut av lesingen.
