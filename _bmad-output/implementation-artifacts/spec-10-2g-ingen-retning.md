---
title: 'Story 10.2, 10.2g: regelen for retningen Ingen og promptens avtrykk i demotekstene'
type: 'feature'
created: '2026-10-25'
status: 'done'
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

*Rettet 2026-10-25 kl. 20:37 (gjennomgangen, BH2, ECH1 og VG2):* første setning over stemmer ikke med det som ble bygget. Demoen avviser en rad som mangler `promptavtrykk` eller har et felt som ikke er en sha256, men sammenligner ikke med prompten, fordi webserveren ikke importerer `ki_prompt` (AD-10, se «Valg underveis»). Det er testene som avviser en rad med et annet avtrykk enn prompten, så en endret prompt gjør dem røde til tekstene lages på nytt.

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

*Utfallet:* M1, regelen tatt ut av prompten, kl. 20:16:42 på `2ded327`, fanget av `test_retningen_ingen_skrives_som_ingen_retning`. M2, sammenligningen med prompten tatt ut av `fra_json` (`if False:`), kl. 20:23:10 på `2e7883d`, fanget av `test_en_rad_med_et_annet_promptavtrykk_avvises`. Begge ble kjørt på nytt på `a71a9e7` etter rettingene, kl. 20:37:30 og 20:37:31, og ble fanget av de samme testene. Fila var lik HEAD etter hver (samme blob).

## Gjennomgangen

Gjennomgang 25.10 etter hele settet (49 filer, 3631 bestått, 20 hoppet over, 0 feilet, 20:25:09–20:32:15), av diffen `f669904..c098d47`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 2). Rettet i `a71a9e7` og i dokumentene.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, BH14, ECH2 | `til_json` satte avtrykket av prompten slik den var da fila ble skrevet, ikke da tekstene ble laget, og satte feltet bare hvis `promptversjon` sto i `FELTENE` | medium | **rettet** i `a71a9e7`: `lag_tekstene` regner ut avtrykket før det første kallet og sjekker det etter det siste, `til_json` får det som argument, og `FELTENE.index("promptversjon")` feiler hvis feltet mangler |
| BH2, ECH1, VG2 | Approach b) sier at demoen avviser en rad med et annet avtrykk, men det gjør bare testene | medium | **rettet:** rettelinjen under Approach b). Koden er som «Valg underveis» (AD-10) |
| BH3 | Avtrykket dekker bare `REGLER`, `UTENFOR` og kildeteksten til `lag_prompt` | low | avvist: det er samme definisjon som avtrykket for versjonen i `test_ki_modell.py` (10.2e, VG2), og `lag_prompt` bruker ingen andre konstanter eller hjelpefunksjoner, bare `json.dumps` |
| BH4, ECH4 | Kontrollen håndhever ikke regelen for retningen Ingen | medium (BH), low (ECH) | **under «Åpent»:** `ki_kontroll.py` er ikke endret i denne instruksjonen. «Signalet er Ingen» er riktig retning (10.2f, BH10). Ført i §48 |
| BH5 | Versjon 3 står for flere prompter, og KI-loggen i basen har ikke promptens avtrykk | medium | **under «Åpent»:** `kilogg.py` og basen er ikke endret i denne instruksjonen. `ose.db` har ingen tekst med versjon 3 (kopien kl. 20:13:43), så fra 26.10 er det én prompt med versjon 3 der |
| BH6 | Formelen for avtrykket står både i `demo_ki.py` og i testen | low | avvist: testen regner ut avtrykket selv med vilje og sjekker at `demo_ki.promptavtrykk()` gir det samme |
| BH7 | `ruff format` i `lag_prompt` endrer avtrykket | low | avvist: det gjelder avtrykket for versjonen fra før (10.2e, VG2), og feilmeldingene sier hva som må gjøres |
| BH8, ECH3 | De nye testene leste fila med `utf-8`, ikke `utf-8-sig` | low | **rettet** i `a71a9e7` |
| BH9 | Testen av en endret prompt endret bare `REGLER` | low | **rettet** i `a71a9e7`: også `UTENFOR` |
| BH10 | «fordi trenden ga ikke utslag» har feil ordstilling i leddsetningen | low | **under «Åpent»:** prompten avgjøres av gruppen. Formen står også i tekster fra før |
| BH11 | 11,44 s for kall nr. 1 i §48 står uten forklaring | low | **rettet** i §48: om modellen ble lastet inn, ble ikke ført |
| BH12 | Regelen er prøvd på få tekster | low | **rettet** i §48: 2 av 15 i én kjøring og 1 demotekst |
| BH13 | Rekkefølgen på sjekkene (BH11 i 10.2f) føres ikke videre | low | **rettet:** under «Åpent» |
| ECH5 | Testen viste ikke at regelen står for alle retninger | low | **rettet** i `a71a9e7` |
| VG1 | Ingen test sjekket feltet i fila kommandoen skriver | low | **rettet** i `a71a9e7`: `test_lager_en_rad_per_aksje_og_ingen_ny_runde` |

## Åpent

- *Lagt til 2026-10-25 kl. 20:37 (BH11 i 10.2f, BH13):* modellen nevner ikke alltid sjekkene i fast rekkefølge. Gruppens svar kl. 19:54 og 19:56 b) lot det stå åpent.
  - *Avgjort 2026-10-25 kl. 20:54 (gruppens svar):* a) kontrollen stopper ikke «Signalet er Ingen», fordi teksten er riktig, og regelen ga 0 i §48 (BH4). b) KI-loggen i basen får ikke promptens avtrykk (BH5). Fra hentingen mandag 26.10, når basen får tekster med versjon 3, gir enhver endring i prompten en ny versjon. c) Prompten får to linjer blant reglene, ordrett: «- Etter «fordi» står «ikke» foran verbet, for eksempel «fordi trenden ikke ga utslag».» og «- Når du nevner flere sjekker, ta dem i rekkefølgen trend, bevegelse og interesse.» (rådets ordlyd). d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b).
- *Lagt til 2026-10-25 kl. 20:37 (BH4, ECH4):* kontrollen i `ki_kontroll.py` håndhever ikke regelen for retningen Ingen. «Signalet er Ingen» består, fordi det er riktig retning. Om kontrollen skal stoppe det, avgjør gruppen.
  - *Avgjort 2026-10-25 kl. 20:54 (gruppens svar):* a) kontrollen stopper ikke «Signalet er Ingen», fordi teksten er riktig, og regelen ga 0 i §48 (BH4). b) KI-loggen i basen får ikke promptens avtrykk (BH5). Fra hentingen mandag 26.10, når basen får tekster med versjon 3, gir enhver endring i prompten en ny versjon. c) Prompten får to linjer blant reglene, ordrett: «- Etter «fordi» står «ikke» foran verbet, for eksempel «fordi trenden ikke ga utslag».» og «- Når du nevner flere sjekker, ta dem i rekkefølgen trend, bevegelse og interesse.» (rådets ordlyd). d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b).
- *Lagt til 2026-10-25 kl. 20:37 (BH5):* KI-loggen i basen har promptversjonen, men ikke promptens avtrykk, så tekster fra to prompter med samme versjon kan ikke skilles i basen. Det gjelder prøvekopiene for §43–§48. `ose.db` får tekster med versjon 3 først fra hentingen 26.10.
  - *Avgjort 2026-10-25 kl. 20:54 (gruppens svar):* a) kontrollen stopper ikke «Signalet er Ingen», fordi teksten er riktig, og regelen ga 0 i §48 (BH4). b) KI-loggen i basen får ikke promptens avtrykk (BH5). Fra hentingen mandag 26.10, når basen får tekster med versjon 3, gir enhver endring i prompten en ny versjon. c) Prompten får to linjer blant reglene, ordrett: «- Etter «fordi» står «ikke» foran verbet, for eksempel «fordi trenden ikke ga utslag».» og «- Når du nevner flere sjekker, ta dem i rekkefølgen trend, bevegelse og interesse.» (rådets ordlyd). d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b).
- *Lagt til 2026-10-25 kl. 20:37 (BH10):* modellen skriver «fordi trenden ga ikke utslag» med feil ordstilling i leddsetningen. Om prompten skal si noe om det, avgjør gruppen.
  - *Avgjort 2026-10-25 kl. 20:54 (gruppens svar):* a) kontrollen stopper ikke «Signalet er Ingen», fordi teksten er riktig, og regelen ga 0 i §48 (BH4). b) KI-loggen i basen får ikke promptens avtrykk (BH5). Fra hentingen mandag 26.10, når basen får tekster med versjon 3, gir enhver endring i prompten en ny versjon. c) Prompten får to linjer blant reglene, ordrett: «- Etter «fordi» står «ikke» foran verbet, for eksempel «fordi trenden ikke ga utslag».» og «- Når du nevner flere sjekker, ta dem i rekkefølgen trend, bevegelse og interesse.» (rådets ordlyd). d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b).
