---
title: 'Story 8.15 (8.15b): Selskap kan sorteres, og den sorterte kolonnen synes'
type: 'feature'
created: '2026-10-18'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd6e2d1c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-15-sortering-ved-klikk-i-kolonneraden.md'
---

## Intent

**Problem:** I oversikten kan Sluttkurs, Endring, Signalstyrke og Retning sorteres ved klikk (story 8.15), men ikke Selskap. Den sorterte kolonnen skilles fra de andre bare av fargen på vinkelen. Designtavla har sorteringsmerket på Selskap, og et lysere felt med en oransje strek under den sorterte kolonnen.

**Grunnlaget:** gruppens svar 18.10 kl. 22:06 og instruksjonen 18.10 kl. 23:58.

## Kontrollpunktene

- a) Selskap: navnet i kolonneraden blir en sorteringslenke som de andre, med vinkel, og «?» ved siden av. Første klikk gir A til Å i den norske rekkefølgen som alt brukes ved lik verdi (Æ, Ø og Å etter Z, uten forskjell på store og små bokstaver), og et nytt klikk snur. Sorteringen gjelder innenfor hver del, som før (tillegget 13.10). Linja over tabellen og teksten for skjermleseren sier «stigende (A til Å)» eller «synkende (Å til A)», som for Retning. Hjelpen og `docs/hjelp.md` følger med der sorteringen nevnes (regel 19).
- b) Markeringen: kolonnen tabellen er sortert på, får et lysere felt og en oransje strek under i kolonneraden, med fargene i `designregler.md`, og kontrasten regnes i testene for utseendet. `designregler.md` får en datert linje om det under linja fra 15.10 om vinkelen. Endres en fil bak bildet av oversikten, tas bildet på nytt slik feilmeldingen i testen sier.
- c) Testene, med «Ville feilet hvis»: Selskap sorteres i norsk rekkefølge og innenfor hver del; et nytt klikk snur; bare den sorterte kolonnen har markeringen, og uten sortering har ingen den; `aria-sort` som før. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: navnet sortert på kodepunkt, markeringen på alle kolonnene, og Selskap sortert på tvers av delene.

## Planen, én commit per punkt

1. a) `selskap` i `SORTERBARE` med stigende først, verdien er navnet med `_navn` (norsk rekkefølge), lenken og «?» i kolonneraden, ordene «(A til Å)» og «(Å til A)», og bildet av oversikten tatt på nytt, fordi Selskap får en vinkel.
2. b) Markeringen i stilen, med velgeren `th[aria-sort]`, så den følger `aria-sort`, som bare står på den sorterte kolonnen. Linja i `designregler.md`, og bildet på nytt hvis avtrykket endres.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Fargene:** feltet er `#3A3E47`, kanten i stripa i `designregler.md` §5, og streken er sterk oransje `#F2B53A` (`--oransje`, §3), 3 px nederst i cellen. Begge står i `designregler.md`. Det lysere feltet står ikke med egen farge der, så kanten fra stripa brukes, fordi den er den lyseste av de mørke fargene og hører til samme flate.
- **Markeringen følger `aria-sort`**, så det ikke er to ting som kan si hvilken kolonne som er sortert.
- **Bildet** tas på nytt i a, fordi Selskap får en vinkel i kolonneraden, så hver commit har et bilde som stemmer.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe.

## Avgjort underveis

- **Hjelpen og `docs/hjelp.md`:** ingen av dem nevnte sorteringen da a ble bygget (`git grep`), så de ble ikke endret i a. Etter gjennomgangen (ECH2, VG3) sier hjelpen ved «?» på Selskap hva hvert klikk gjør, fordi «?» nå står ved en lenke som sorterer.
- **Bildet** ble tatt på nytt tre ganger med samme fremgangsmåte og høyde (1280 × 1573): i a kl. 00:03, fordi Selskap fikk en vinkel (sha256 `777eee6eab84dfed…` ble `57e53e54d4b0d264…`); i b kl. 00:04 og etter rettingene kl. 00:12 (tidspunktene filene ble skrevet), begge like `57e53e54d4b0d264…`, fordi siden uten sortering ikke har markeringen og boksen «Slik leser du tabellen» ikke bruker hjelpeteksten. Bare avtrykket er nytt i b og i rettingene (VG5).
- **Tvungne farger:** den sorterte kolonnen har en gjennomsiktig kant på 3 px, som nettleseren tegner i systemfargen når den tar bort bakgrunnen og skyggen (BH6, ECH3).
- **Innenfor hver del:** å sortere hele lista før `del_i_to` gir samme svar som å sortere hver del, fordi `del_i_to` beholder rekkefølgen. Det er derfor ikke en mutant som kan fanges. Mutanten M3 flytter rader mellom delene, og testdataene har Aker BP under «Øvrige aksjer», først i alfabetet (VG1).

## Mutantene

Én om gangen med `-x` på `tests/test_markedsoversikt.py` og `tests/test_app.py` (med `-k` for sorteringen), i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. M1–M3 er fra instruksjonen og ble fanget på `b5f2400` og på nytt på `764d966`. N1 og N2 er for funnene med dom medium, fanget på `764d966`:
- M1, navnet sortert på kodepunkt: `test_a_til_aa_i_norsk_rekkefoelge`.
- M2, markeringen på alle kolonnene: `test_markeringen_staar_bare_paa_den_sorterte_kolonnen`.
- M3, Selskap sortert på tvers av delene: `test_hver_del_sorteres_for_seg[selskap stigende]`.
- N1, Selskap sortert på tickeren (BH2): `test_a_til_aa_i_norsk_rekkefoelge`, og `test_navnet_ikke_tickeren` for seg.
- N2, uten kanten for tvungne farger (BH6): `test_markeringen_staar_bare_paa_den_sorterte_kolonnen`.

## Gjennomgangen

Gjennomgang 19.10 på diffen `fb218a7..b5f2400`, uten bildet. Linsene var Blind Hunter (BH, 13 funn, bare diffen), Edge Case Hunter (ECH, 11, prøvd med `sorter` og test_client mot en demobase i en midlertidig mappe) og Verification Gap (VG, 8). Ingen av dem kjørte hele testsettet, en server eller et nettkall. Seks rader har dom medium. Fem er rettet i `764d966` og her, og BH1 er avvist med beviset under.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH2 | Testen i appen kunne ikke skille navn fra ticker | medium | patch: `test_navnet_ikke_tickeren`. N1 |
| BH6, ECH3 | Markeringen forsvant med tvungne farger | medium | patch: en gjennomsiktig kant. N2 |
| ECH2, VG3 | Hjelpen ved «?» på Selskap sa bare at et klikk åpner aksjen | medium | patch: hjelpen sier begge klikkene |
| VG1 | Testdataene kunne ikke vise «innenfor hver del» for Selskap | medium | patch: Aker BP under «Øvrige aksjer», og forklart over |
| VG2 | Mutantene var ikke dokumentert | medium | patch: over |
| BH1 | Bildet skulle ikke være tatt på nytt | medium | avvist: diffen holdt `docs/bilder` utenfor. Bildet ble byttet i `a0343fe`, med vinkelen på Selskap |
| BH3, ECH10 | `stil.count(...) == 1` låste fargebruken | low | patch: hver regel i kolonneraden med feltet må gjelde `th[aria-sort]` |
| BH5 | aria-sort var bare testet stigende | low | patch: begge retninger |
| VG7 | Linja var bare testet stigende | low | patch |
| VG4 | §5 sier at `#F2B53A` står bare på blekk | low | patch: linja fra 18.10 sier unntaket, og at feltet har 1,66:1 mot blekk |
| VG5 | At bildet var likt, var ikke vist | low | patch: tider og sha256 over |
| BH4 | Testen uten sortering gjentok en sjekk fra 8.15 | low | avvist: den står i klassen for 8.15b med sin egen «Ville feilet hvis» |
| BH7, ECH8 | Fokusringen og streken er begge oransje | low | avvist: omtrent 2 px luft mellom dem, regnet fra stilen, og fokus i kolonneraden var oransje fra før |
| BH8 | `box-shadow` kunne overskrive en skygge | low | avvist: `thead th` har ingen skygge |
| BH9 | «?» mot feltet var ikke i kontrasttestene | low–medium | avvist: «?» er en hvit sirkel og fokusringen oransje, og begge parene mot feltet er med (10,71:1 og 5,84:1) |
| BH10 | `_navn` og returtypen | low | avvist: `_navn` er nøkkelen, en tekst, og navn og tall blandes aldri i samme sortering (ECH7) |
| BH11, ECH1 | Andre bokstaver med aksent havner etter Å | low | avvist: ingen navn i universet eller demoen har dem (ECH1 sjekket alle) |
| BH12 | Datoen i linjene i designreglene | low | avvist: linjene har datoen for svaret, og `updated` kommer fra klokka |
| BH13 | Kontrasttallene i designreglene testes ikke | low | avvist: testen sjekker grensene, og tallene er regnet på nytt av VG |
| ECH4 | Like navn med ulik stor og liten bokstav snus ikke | low | avvist: stabil sortering, som for de andre kolonnene (BH8 i 8.15) |
| ECH5, ECH6 | Tomme navn, sifre, «Aa» og NFD | low | avvist: navnene er konstanter i koden, i NFC |
| ECH7 | Navn mot tall, adressen og demoen | low | ingen endring: ingen feil funnet |
| ECH9 | Bredden ved 390 px | low | avvist: tabellboksen ruller sidelengs, ikke siden |
| ECH11 | Det runde hjørnet når Selskap er sortert | low | avvist: kosmetisk, og båndene treffes ikke |
| VG6 | Testene for aria-sort | low | patch: begge retninger, se BH5 |
| VG8 | `prd.md` nevner ikke Retning og Selskap under sorteringen | low | avvist: utenfor kontrollpunktene. Retning manglet alt fra 8.15 |

*Lagt til 2026-10-19 kl. 00:22:* PR #73 er squash-flettet i `b6449ac`, låst til head-en `a698f71`. Main hadde ikke gått videre. CI var grønn på head-en (39171682987) og på main (39171808452). Triagen står over og som kommentar på PR-en.
