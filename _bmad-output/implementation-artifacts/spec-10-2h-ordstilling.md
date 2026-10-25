---
title: 'Story 10.2, 10.2h: ordstillingen etter «fordi» og rekkefølgen på sjekkene i prompten'
type: 'feature'
created: '2026-10-25'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd4b6d12'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2g-ingen-retning.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Fire punkter under «Åpent» i spesifikasjonen 10.2g. Modellen skriver «fordi trenden ga ikke utslag», med feil ordstilling i leddsetningen (BH10), og nevner ikke alltid sjekkene i fast rekkefølge (BH11 i 10.2f, BH13). Kontrollen håndhever ikke regelen for retningen Ingen (BH4, ECH4), og KI-loggen i basen har ikke promptens avtrykk (BH5).

**Beslutningen** (under story 10.2 i `epics.md`, *Avgjort 2026-10-25 kl. 20:54*):
- a) Kontrollen stopper ikke «Signalet er Ingen», fordi teksten er riktig, og regelen ga 0 i §48 (BH4).
- b) KI-loggen i basen får ikke promptens avtrykk (BH5). Fra hentingen mandag 26.10, når basen får tekster med versjon 3, gir enhver endring i prompten en ny versjon.
- c) Prompten får to linjer blant reglene, ordrett: «- Etter «fordi» står «ikke» foran verbet, for eksempel «fordi trenden ikke ga utslag».» og «- Når du nevner flere sjekker, ta dem i rekkefølgen trend, bevegelse og interesse.» (rådets ordlyd).
- d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b): ingen tekst i `ose.db` er laget med versjon 3 ennå.

## Approach

**a) Prompten** (`src/ki_prompt.py`): de to linjene fra svaret c) under «Regler for teksten», linja om rekkefølgen etter linja om å bruke navnet på sjekken, og linja om ordstillingen etter linja om «fordi». Avtrykket for versjon 3 i `AVTRYKK` i `tests/test_ki_modell.py` settes på nytt, og docstringen får svarene b) og d).

*Utfallet:* `34b42d2` (21:37). Avtrykket for versjon 3 er `ec166426…22d5` (var `0d427725…`). `test_ordstillingen_og_rekkefoelgen_staar_i_reglene` sjekker at begge linjene står én gang i reglene og kommer med i prompten, med og uten merket. Etter gjennomgangen, i `5261ebf` (21:53): `test_ordstillingen_og_rekkefoelgen_staar_der_spesifikasjonen_sier` sjekker plassen, og `test_avtrykket_for_versjon_3_staar` låser avtrykket (svaret b).

**b) Demoen:** KI-tekstene i demoen lages på nytt (`uv run python src/demo_ki.py`), med promptens avtrykk i hver rad, og bildet av aksjesiden i README-en tas på nytt med avtrykkene, av en demoaksje der teksten besto.

*Utfallet:* `756eb75` (21:41). KI-tekstene i demoen ble laget på nytt 21:38:14–21:38:42: 13 av 13 besto, 0 ble stoppet, og modellen feilet for 0. Alle har `promptversjon` 3 og `promptavtrykk` `ec166426…22d5`. HVDO, NLYS, SLVP, FJSB, TRHF, LSTF, SGNT, LKSV og TROY fikk en annen tekst, og BRFE, KVST, JGRD og BLGT er like. TRHF og LKSV sier ikke lenger «Styrken er tre, fordi tre av sjekkene ga et utslag.» (gjennomgangen, BH9). SLVP sier nå «fordi trenden ikke ga utslag, …». Hver tekst er lest mot grunnlaget: alle beskriver hver sjekk slik fortegnet er, og ingen nevner dagene. FJSB, LSTF og SGNT nevner bevegelsen, som ga utslag, før trenden og interessen (før: de tre og HVDO). Bildet av BRFE ble tatt på nytt med fremgangsmåten i 3.3b og ble byte for byte det samme, 1280 × 1894, fordi teksten for BRFE er den samme. Bare `AVTRYKK_BAK_AKSJESIDEN` er satt på nytt.

**c) Prøvekjøringen** (§49 i `malinger.md`), som i §48, mot `data/db/ki-proeve-v3i.db` for børsdagen 23.10, med hver tekst lest mot grunnlaget. Tekstene i §48 og §49 telles for «fordi» med «ikke» etter verbet og for sjekker i en annen rekkefølge. Tabellen sammenligner §34 og §43–§49.

*Utfallet:* `98d88a5` (21:42), rettet i `bed17e7` (21:54). Kjørt 21:41:47–21:41:54 mot `ki-proeve-v3i.db`: 15 av 15 besto, 0 ble stoppet, og modellen feilet for 0, med median 0,44 s og lengste kall 0,69 s (kall nr. 1). Hver tekst er lest mot grunnlaget: ingen sier feil om en sjekk, og ingen nevner dagene. «Fordi» med «ikke» etter verbet: 2 i §48 (DNB og TEL), 0 i §49. Sjekker i en annen rekkefølge: 1 i §48 og 1 i §49 (DNO, samme tekst). Leddsetninger med «ikke» etter verbet, alle konjunksjoner: 2 og 0. 10 av de 15 er ordrett de samme som i §48. sha256 for `ose.db` var den samme før og etter.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Kontrollen (`ki_kontroll.py`) og KI-loggen (`kilogg.py`) endres ikke (svarene a og b).
- Kopien ble laget med skallet på main kl. 21:36:36, før grenen, med samme sha256 som `ose.db` (`e3184c07…f4a4`). Ingen KI-rad i kopien har `promptversjon` 3: alle 75 har 2.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis færre enn 15 tekster i §49 besto, en tekst i §49 sier feil om en sjekk eller nevner dagene, eller sha256 for `ose.db` rett før flettingen ikke er den samme som for kopien.
- *Lagt til kl. 21:54 (gjennomgangen, BH13):* virkningen av de to linjene måles i §49, men den er ikke et krav for flettingen. Stoppkriteriene er instruksjonens.

## Mutanten

Én med `-x`, med kopi før og sha256 mot HEAD etter: linja om rekkefølgen tatt ut av prompten.

*Utfallet:* kjørt kl. 21:38:06 på `34b42d2` og kl. 21:53:30 på `5261ebf`. Begge gangene ble den fanget av `test_ordstillingen_og_rekkefoelgen_staar_i_reglene` (linja om rekkefølgen). `src/ki_prompt.py` var lik HEAD etterpå (samme blob, `bde07d2b`, og samme sha256 som kopien).

## Gjennomgangen

Gjennomgang 25.10 etter hele settet (49 filer, 3634 bestått, 20 hoppet over, 0 feilet, 21:43:17–21:50:23), av diffen `d4b6d12..98d88a5`, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 1). Rettet i `5261ebf`, `bed17e7` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH7, ECH2 | Linja om rekkefølgen ble ikke fulgt der én sjekk som ikke er trenden, ga utslag: DNO i §48 og §49, og FJSB, LSTF og SGNT i demoen | medium | **under «Åpent»:** linja er gruppens ordrette ordlyd (svaret c), så en ny ordlyd må avgjøres av gruppen. Ikke rettet, så PR-en flettes ikke (steg 4) |
| BH7, ECH2 | *Lagt til 2026-10-25 kl. 23:23:* som raden over | medium | **avgjort av gruppen kl. 22:11:** 10.2h flettes i kveld. Linja står, avviket står under «Åpent», og en ny ordlyd gir versjon 4 |
| BH4, ECH1 | Avtrykket for versjon 3 var ikke låst, så det kunne skrives over etter 26.10 | medium | **rettet** i `5261ebf`: `test_avtrykket_for_versjon_3_staar` |
| BH1 | §49 sier ikke hvilken prompt som ble brukt | medium | **rettet** i `bed17e7`: avtrykket og commiten i §49 |
| BH3 | Tellingen i §49 dekker bare leddsetninger med «fordi» | medium | **rettet** i `bed17e7`: en rad for alle konjunksjoner, 2 i §48 og 0 i §49 |
| BH5 | Spesifikasjonen hadde ingen Utfallet-linjer og ikke utfallet av mutanten | medium | **rettet:** Utfallet under a), b), c) og «Mutanten» |
| BH2 | Linja om ordstillingen nevner bare «fordi», ikke «mens» og andre leddsetninger | low | **under «Åpent»:** linja er gruppens ordrette ordlyd. Ingen tekst i §48 eller §49 har «mens … ga ikke», og i demoen er LSTF rettet. Blind Hunter satte den til medium |
| BH6, ECH3 | Eksempelet «interessen ga ikke utslag» i linja over har motsatt ordstilling av den nye linja | low | **under «Åpent»:** eksempelet er riktig i en hovedsetning, og prompten avgjøres av gruppen |
| BH8, VG1 | Ingen test sjekket hvor de to linjene står | low | **rettet** i `5261ebf` |
| BH9 | Demotekstene for TRHF og LKSV mistet setningen om styrken | low | **rettet:** ført i Utfallet under b). Teksten er fortsatt riktig |
| BH10 | Demotekstene skriver retningen på flere måter («er negativt», «har en negativ retning», «er Blandet») | low | **under «Åpent»** |
| BH11 | §49 sier ikke om modellen var lastet ved kall nr. 1 | low | **rettet** i `bed17e7`: det ble ikke sjekket |
| BH12 | §49 sier ikke at klokkeslettene er vintertid | low | **rettet** i `bed17e7` |
| BH13 | Ingen stoppkriterium for virkningen av linjene | low | **rettet:** linja under «Boundaries & Constraints» |
| ECH4 | Kontrollen håndhever ingen av de to linjene | low | **under «Åpent»:** `ki_kontroll.py` er ikke endret i denne instruksjonen |
| ECH5 | §49 talte for få tekster der linja om ordstillingen gjaldt | low | **rettet** i `bed17e7`: 5 av 15 og 5 av 13 demotekster |

## Åpent

- *Lagt til 2026-10-25 kl. 21:54 (BH7, ECH2):* linja om rekkefølgen ble ikke fulgt i DNO (§48 og §49) og i FJSB, LSTF og SGNT i demoen. Der ga en annen sjekk enn trenden utslag, og modellen nevner den først. Om linja skal få en ny ordlyd, for eksempel at rekkefølgen også gjelder når bare én sjekk ga utslag, avgjør gruppen. Dom medium, så PR #98 er ikke flettet.
  - *Avgjort 2026-10-25 kl. 22:11 (gruppens svar):* 10.2h flettes i kveld. Linja om ordstillingen virket: «fordi» med «ikke» etter verbet i 2 tekster i §48 og 0 i §49. Linja om rekkefølgen står, men modellen følger den ikke når bare én sjekk utenom trenden ga utslag. Tekstene er riktige, og avviket står her. En ny ordlyd gir versjon 4.
- *Lagt til 2026-10-25 kl. 21:54 (BH2):* linja om ordstillingen nevner bare «fordi». Om den skal gjelde alle leddsetninger, avgjør gruppen.
- *Lagt til 2026-10-25 kl. 21:54 (BH6, ECH3):* eksempelet «interessen ga ikke utslag» i linja om navnet på sjekken har ordstillingen fra en hovedsetning, rett over linja om «fordi».
- *Lagt til 2026-10-25 kl. 21:54 (BH10):* demotekstene skriver retningen på flere måter, og «Blandet» med stor forbokstav midt i setningen.
- *Lagt til 2026-10-25 kl. 21:54 (ECH4):* kontrollen i `ki_kontroll.py` håndhever verken ordstillingen eller rekkefølgen.
