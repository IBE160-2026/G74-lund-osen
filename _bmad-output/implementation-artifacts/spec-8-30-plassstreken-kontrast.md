---
title: 'Story 8.30: de ledige rutene i plassstreken med nok kontrast'
type: 'fix'
created: '2026-11-14'
status: 'review'
route: 'dispatch'
baseline_commit: '8944bf67'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-29-din-egen-liste-kom-i-gang.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

Skrevet 14.11 i vinduet som gjør PRD-en, etter tillegg 9 til 9.11 (limt inn kl.
05:17, ført i `docs/ai-prompts/2026-11-14.md`) og gruppens svar 14.11 kl.
05:10–05:13 på spørsmål 7 og 8 i 8.29. Vinduet som bygde 8.29, er lukket. 9.12 er
flettet, og dette er neste ledige nummer i Epic 8. Worktreen `G74-lund-osen-8-30`,
grenen `8-30-plassstreken-kontrast`, fra `origin/main` (`8944bf67`).

## Storyen

Som **bruker i demoen og den ekte versjonen** vil jeg se de ledige plassene i
streken under «Appen følger N av 18» på den beige bakgrunnen. Da ser jeg hvor
mange aksjer jeg kan følge til.

**Oppfyller:** svaret på spørsmål 7 i 8.29 · **Begrenses av:** NFR-06,
designregler §3 (kontrast), WCAG 1.4.11, regel 22

**Avhenger av:** 8.29. **Én økt:** ja.

## Svarene

*Svar 2026-11-14 kl. 05:10–05:13 (gruppens svar på spørsmål 8 i 8.29, rådet
anbefalte det):* «Som nå, med ring». Det er godtatt som bygget: 2 av 3 har den
hvite pillen også en tidligere dag, i notatene og i «Signalet dag for dag», slik
skissen 06.11 viser, og linja i designregler §3 står. Ingenting bygges for
svaret.

*Svar 2026-11-14 kl. 05:10–05:13 (gruppens svar på spørsmål 7 i 8.29, rådet
anbefalte det):* «endre så det blir riktig nå». De ledige rutene i streken under
«Appen følger N av 18» skal ha nok kontrast mot den beige bakgrunnen.

## Det som var

`.plassstrek span` har `var(--strek-2)` (`#D6D3CA`), og `span.brukt` har
`var(--blekk)` (`#16181D`). Bakgrunnen er `var(--bakgrunn)` (`#F3F2EE`). Regnet
etter WCAG ga det 1,34:1 for de ledige rutene mot bakgrunnen (ECH3 i 8.29), men
designregler §3 krever minst 3:1 for streker og felt som må ses for å forstå
siden. Regelen for forced-colors gir hver rute en kant i `CanvasText`.
`designregler.md` har ingen egen farge for streken.

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet, og alt er bygget etter forslaget.

1. **Fargen på de ledige rutene.** Fargene i `:root` i `stil.css` som gir minst
   3:1 både mot bakgrunnen og mot de brukte rutene, er `--dempet-2` (`#70757D`,
   4,14:1 og 3,83:1), `--felt` (`#8A847A`, 3,31:1 og 4,79:1), `--gul-symbol`,
   `--soeyle-lys-opp`, `--soeyle-lys-ned` og `--snitt`. De fire siste betyr noe
   annet i appen, som retning eller gult. En kant rundt en lys rute ville gitt
   to farger per rute uten å gjøre mer. *Forslag, som bygget:* `--dempet-2`, den
   grå teksten som alt brukes i appen. Den har størst margin på begge kravene
   og er nøytral, så streken ikke ser ut som et signal.
2. **Designreglene.** `designregler.md` §3 har regelen om 3:1, men ingen farge
   for streken. *Forslag, som bygget:* en datert linje under «Kontrast» sier at
   de ledige rutene har `--dempet-2`, og at testen regner det ut.
3. **Hjelpen.** `docs/hjelp.md` sier «mørk for hver aksje appen følger og lys for
   hver ledige». *Forslag, som bygget:* «grå for hver ledige», fordi rutene ikke
   lenger er lyse.

## Delene

### A) Fargen
`:where(.side-oversikt) .plassstrek span` får `background: var(--dempet-2)`.
`span.brukt` og regelen for forced-colors står. Streken ligger i `_egne.html`,
som demoen og den ekte versjonen deler, og har den samme stilen i begge.

### B) Testene
`tests/test_plassstreken_8_30.py`.
- **Ville feilet hvis:** de ledige rutene hadde under 3:1 mot bakgrunnen, eller
  brukt og ledig under 3:1 mot hverandre, regnet ut fra fargene i `stil.css`,
  med streken lest fra Min liste i begge versjonene. Den ville også feilet hvis
  de brukte rutene ikke lenger var `--blekk`, regelen for forced-colors manglet,
  eller fargene i nettleseren ved 1280 og 390 px var andre enn i stilen.

### C) Bildene
Bildene i `docs/appen/` og `docs/appen/mobil/` som viser streken, tas på nytt
fra en demobase i en midlertidig mappe, aldri på port 8000. Avtrykkene følger.

## Grenser

Ingen API-kall. `data/db/ose.db` røres ikke. Bare stilen, hjelpen,
designreglene, testene og bildene endres.

## Bygget 14.11

Commitene `fd28a2fe` (spesifikasjonen, storyen og svarene), `6de80813` (fargen,
testen, designreglene og hjelpen) og `80483315` (bildet og avtrykkene).

**Målt.** Testen regner 4,14:1 for de ledige rutene mot bakgrunnen og 3,83:1 for
brukt mot ledig, fra stilarket appen gir ut i begge versjonene. I Edge ved 1280
og 390 px har rutene fargene fra stilen, er 10 × 10 px og står på sidens beige,
i demoen og den ekte versjonen.

**Mutanten M1.** `--strek-2` ble satt tilbake for de ledige rutene i en kopi av
`stil.css` på HEAD `6de80813`. Alle åtte testene i `tests/test_plassstreken_8_30.py`
feilet. Kopien ble lagt tilbake, og sha256 og git-hashen var lik HEAD.

**Bildene.** Alle bildene ble tatt på nytt fra en demobase i en midlertidig
mappe, ikke på port 8000. Bare `docs/appen/din-egen-liste-demo.png` viser streken,
og det er byttet. Ingen av bildene i `docs/appen/mobil/` viser Min liste.
Notatpanelet, «Vis meg rundt» og notatene ved 390 px ble også ulike, fordi
skriptet ikke åpner panelet og omvisningen. De viser ikke streken, så bildene fra
main står. Avtrykkene i `tests/test_docker.py` er regnet ut på nytt, fordi de tar
med `stil.css`.

## Gjennomgangen 14.11 (Edge Case Hunter)

Diffen `8944bf67..80483315`. Ingen funn på middels eller høy grad. Tallene i
spesifikasjonen, hjelpen og designreglene ble regnet på nytt og stemmer. Rettingene
står i `af986b9b`.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | lav | `_bakgrunn` leser første regel, så en senere `@media` med en annen bakgrunn sees bare av nettlesertesten | Rettet: `test_ingen_annen_regel_gir_rutene_en_bakgrunn`, og en tydelig feil i stedet for `None`. En `@media` for 390 px med `--strek-2` ble fanget av den og nettlesertesten |
| ECH2 | lav | En full eller tom liste gir `null` i skriptet i nettleseren og en uklar feil | Rettet: skriptet melder hva som mangler, og testen sier det |
| ECH3 | lav | `_hex` tar bare `rgb()`, og `bak()` godtar en halvgjennomsiktig farge og ser bort fra bakgrunnsbilder | Rettet: `rgba` bare helt dekkende, og en forelder med bilde gir en feil |
