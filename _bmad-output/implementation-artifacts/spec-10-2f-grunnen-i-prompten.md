---
title: 'Story 10.2, 10.2f: grunnen i prompten'
type: 'feature'
created: '2026-10-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '448bc60'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2e-prompten-versjon-3.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Prompten i versjon 3 sier: «Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier det under teksten.» Etter gruppens svar 25.10 kl. 12:12 a) sier ikke siden lenger «for første gang», så grunnen stemmer ikke (punktet fra gjennomgangen 25.10 kl. 13 under «Åpent» i spesifikasjonen 10.2e).

**Beslutningen** (under story 10.2 i `epics.md`, *Avgjort 2026-10-25 kl. 18:34 og 18:35*):
- a) Grunnen i prompten endres i kveld. Linja blir: «Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier under teksten hvor lenge signalet har vart.» Regelen for modellen står.
- b) `PROMPTVERSJON` står som «3», fordi ingen tekst i `ose.db` er laget med versjon 3 ennå. Avtrykket settes på nytt, og demotekstene og prøvekjøringen lages på nytt, så alle tekster med versjon 3 er laget med samme prompt. Det er et unntak fra regelen om ny versjon i docstringen i `ki_prompt.py`, og docstringen sier det.

## Approach

**a) Prompten** (`src/ki_prompt.py`): linja med ordlyden fra svaret a), avtrykket for versjon 3 i `AVTRYKK` i `tests/test_ki_modell.py` satt på nytt, og docstringen med svaret b).

**b) Demoen:** KI-tekstene i demoen lages på nytt (`uv run python src/demo_ki.py`), og bildet av aksjesiden i README-en tas på nytt med avtrykkene. Bildet viser en demoaksje der teksten besto (svaret 24.10 kl. 23:23 b).

*Utfallet:* KI-tekstene i demoen ble laget på nytt 19:15:59–19:16:21: 13 av 13 besto, 0 ble stoppet, og modellen feilet for 0. Alle har `promptversjon` 3. BRFE, SLVP, TRHF og LKSV fikk en annen tekst enn før, og de ni andre er like. Hver er lest mot grunnlaget: alle beskriver hver sjekk slik fortegnet er, og ingen nevner dagene, hovedindeksen, bransjen eller antallet aksjer. Bildet viser fortsatt BRFE, der teksten besto, 1280 × 1934. Bunnen av grafen ble målt i Edge uten vindu og står fortsatt ved 1934. `AVTRYKK_BAK_AKSJESIDEN` er satt på nytt. README-teksten under bildet siterer ikke KI-teksten og er ikke endret.

**c) Prøvekjøringen** (§47 i `malinger.md`), som i §46, mot `data/db/ki-proeve-v3g.db` for børsdagen 23.10, med hver tekst lest mot grunnlaget. Tabellen sammenligner §34 og §43–§47.

*Utfallet:* kjørt 19:19:04–19:19:12 mot `ki-proeve-v3g.db`: 15 av 15 besto, 0 ble stoppet, og modellen feilet for 0, med median 0,46 s og lengste kall 1,02 s. Hver tekst er lest mot grunnlaget: ingen sier feil om en sjekk, og ingen nevner dagene. 9 er ordrett de samme som i den siste kjøringen i §46. sha256 for `ose.db` var den samme før og etter.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Kopien ble laget med skallet på main kl. 19:13:44, før grenen, med samme sha256 som `ose.db` (`e3184c07…f4a4`). Ingen KI-rad i kopien har `promptversjon` 3: alle 75 har 2.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis færre enn 15 tekster i §47 besto, eller en tekst i §47 sier feil om en sjekk eller nevner dagene.

## Mutanten

Én med `-x`, med kopi før og sha256 mot HEAD etter: den gamle grunnen, «Siden sier det under teksten.», tilbake i prompten.

*Utfallet:* på `6ea0aed` kl. 19:15:45 (den gamle grunnen også i sitatet i docstringen) og på `3751c95` kl. 19:31:28 (bare i regellinja). Begge gangene ble den fanget av `test_grunnen_er_at_siden_sier_hvor_lenge_signalet_har_vart`, og `src/ki_prompt.py` var lik HEAD etterpå (samme blob, og samme sha256 uten CRLF).

## Gjennomgangen

Gjennomgang 25.10 etter hele settet (49 filer, 3627 bestått, 20 hoppet over, 0 feilet, 19:20:17–19:28:32), av diffen `448bc60..eaff794`, med Blind Hunter (BH, 17 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 2). Rettet i `6c75a7c` og `3751c95`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH2, ECH1, ECH5, VG2 | Unntaket i svaret b) hviler på at `ose.db` ikke har tekster med versjon 3. Kveldshentingen fra main har versjon 3 med den gamle grunnen og kunne skrive dem før flettingen (AD-7) | medium | **rettet:** sha256 for `ose.db` var kl. 19:30:50 fortsatt `e3184c07…f4a4`, den samme som kopien fra kl. 19:13:44, der ingen rad har versjon 3. Det sjekkes igjen rett før flettingen, og flettes ikke hvis den er endret. 25.10 er søndag, så kveldshentingen har ikke kjørt |
| BH1 | Docstringen sier at alle tekster med versjon 3 er laget med samme prompt, men §43–§46 og historikken til demofila har den gamle grunnen | low | **rettet** i `6c75a7c`: «i ose.db og i demoen», og hvilke som har den gamle |
| BH14, ECH3, ECH4 | Testen så bare på `REGLER` og bare på den ordrette gamle frasen | low | **rettet** i `6c75a7c`: «Siden sier» står bare én gang, og grunnen kommer med i `lag_prompt` |
| BH3 | Utfallet av mutanten var ikke ført | low | **rettet:** under «Mutanten» |
| BH4 | «Åpent» sto tom | low | **rettet:** under |
| BH6 | §47 sammenligner ordlyden med den siste kjøringen i §46, mens tabellen viser den første | low | **rettet** i `3751c95` |
| BH7 | «Versjon 2 på samme dag» og «(2)» er uklare | low | **rettet** i `3751c95`: de 15 radene fra kveldshentingen 23.10, punkt 2 i beslutningen |
| BH17 | 9,27 s i §46-kolonnen står uten forklaring | low | **rettet** i `3751c95`: hvilket kall, ble ikke ført (som i §46) |
| BH9 | Det står ikke at utløseren ble satt inn igjen med samme definisjon | low | **rettet** i `3751c95`: skriptet setter inn definisjonen fra `sqlite_master` og sjekker at den finnes |
| VG1, ECH2, BH13 | Ingen test skiller en demotekst laget med den gamle grunnen fra en med den nye, fordi begge har versjon 3 og raden ikke har avtrykket av prompten | low | **under «Åpent»:** `src/demo_ki.py` er ikke endret i denne instruksjonen. Demotekstene er laget på nytt og lest |
| BH10, BH11 | «Signalet er Ingen, fordi …» (SLVP) og rekkefølgen i LKSV leses klønete, men er riktige | low | **under «Åpent»:** prompten avgjøres av gruppen |
| BH5 | Statusen står som `in-progress` | low | avvist: den settes til done etter flettingen (steg 4) |
| BH8 | §47 er én kjøring, mens §46 ble kjørt tre ganger | low | avvist: §46 ble kjørt på nytt fordi kontrollen ble endret. Instruksjonen ber om én kjøring, og modellen kjører med `seed` 42 og `temperatur` 0 |
| BH12 | `avtrykk` i demofila er uendret | low | avvist: det er avtrykket av grunnlaget, som docstringen i `demo_ki.py` sier, og grunnlaget er ikke endret |
| BH15 | Den nye grunnen begrunner bare varigheten, ikke «nytt» og «første gang» | low | avvist: ordlyden er gruppens, fra svaret a) |
| BH16 | Docstringen blander ASCII-omskriving og «første» | low | avvist: sitatet er ordrett, og docstringen har alt «én» og «» |
| ECH-claim | Påstanden i docstringen om `ose.db` ble sjekket bare på kopien | medium | **rettet:** samme som BH2 over |

## Åpent

- *Lagt til 2026-10-25 kl. 19:31 (VG1, ECH2, BH13):* en rad i `demo_ki_tekster.json` har ikke avtrykket av prompten, bare versjonen, så ingen test skiller tekster fra to prompter med samme versjon. `src/demo_ki.py` er ikke endret i 10.2f.
- *Lagt til 2026-10-25 kl. 19:31 (BH10, BH11):* modellen skriver retningen Ingen som et ord i setningen («Signalet er Ingen, fordi …»), og nevner ikke alltid sjekkene i fast rekkefølge. Tekstene er riktige. Om prompten skal si noe om det, avgjør gruppen.
