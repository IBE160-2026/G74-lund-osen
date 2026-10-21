---
title: 'Story 2.7 (2.7b): historikken, «Signalet dag for dag», på aksjesiden'
type: 'feature'
created: '2026-10-21'
status: 'review'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: '7c55e44'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7a-stilen-i-en-css-fil.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-16b-dagen-paa-hele-siden.md'
---

## Intent

**Problem:** briefen v8 lover historikken i v1 (gruppens svar 19.10 kl. 15:43), og story 2.7 står igjen etter 2.7a. Aksjesiden viser i dag bare én dag om gangen, og FR-408s spørsmål, «hva sa løsningen om aksjen for to uker siden?», har ikke et svar i appen.

**Grunnlaget:** story 2.7 i `epics.md`, med avgjørelsen 2026-10-21 under «Prioritering» og under storyen, og instruksjonen 21.10 kl. 16:53. Svaret 19.10 kl. 11:24 som instruksjonen viser til, står ikke i repoet, så innholdet bygger på linja 21.10: historikken er månedsvisningen fra tavla, med piler så langt kursserien går tilbake, og målingene står på siden for dagen (8.16b), som hver dag lenker til. `designregler.md` §3 sier hvordan 3 av 3 merkes.

## Kontrollpunktene

- a) Lesingen: en lesemetode for en periode i `Vurderingslager`, uten slette- eller endremetode (`AD-7`), som siden leser gjennom (`AD-3`), én spørring per måned. Hver dag går gjennom `les_tilstand`, så styrke 0, en grunn, en manglende rad, en dag som ikke er børsdag og en dag utenfor børskalenderen aldri ser like ut.
- b) Siden: nederst på aksjesiden «Signalet dag for dag» med en kort tekst og en rad per uke med ukenummeret, man–fre og «x av y dager skilte seg ut» for uka. Hver dag har datoen, retningen, T, B, I og styrken, eller «–» og tilstanden, og 3 av 3 merkes som i `designregler.md` §3. Hver dag med kurs lenker til siden for dagen. Under står «<måned> samlet: <navn> skilte seg ut x av y børsdager» og hvor mange dager hver sjekk slo ut, der y er dagene med en vurdering, også for uka. Måneden er den for dagen siden viser. Pilene går fra måneden for første til siste kursrad, med en parameter som beholder perioden eller dagen; en ugyldig måned gir måneden for dagen og en kort beskjed, med 200. Dager etter siste kursrad står tomme. Stilen står i CSS-fila (2.7a). Avsnittet om investorsiden (10.5) står fortsatt rett under grafen. Alt virker på 390 px uten vannrett rulling. Hjelpen ved «?» på Sluttkurs sier dagen siden viser (U5). Hjelpen, `docs/hjelp.md` og README-en følger med (regel 19), og bildene tas på nytt.
- c) Testene, med «Ville feilet hvis»: hver tilstand ser ulik ut; tallene for uka og måneden; lenken til dagen; pilene i begge ender, en ugyldig måned og måneden for en valgt dag; dager etter siste kursrad er tomme; porten har lesemetoden og ingen slette- eller endremetode; `vurder` kalles ikke. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: historikken regnet med `vurder`, en manglende rad vist som styrke 0, og dager etter siste kursrad vist som «– ikke vurdert».

## Planen, én commit per punkt

1. a) `Vurderingslager.les_periode(symbol, fra, til)` i `src/vurderingsdata.py`, og `SqliteVurderingslager.les_periode` i `src/lagring_sqlite.py`: én `SELECT` med `dato BETWEEN ? AND ?`, som gir en `dict` fra dato til `Vurdering` eller `Grunn`, med samme kontroll av nøkkelen som `les`. Den rene logikken i en ny fil, `src/historikk.py`: måneden fra adressen, ukene, dagene gjennom `les_tilstand` og tallene. Fila importerer ikke `signalberegning.vurder`.
2. b) Ruta i `src/app.py` leser måneden én gang gjennom `SqliteVurderingslager`, med aksjen siden viser som lista. Malen `src/templates/aksje.html` får avsnittet nederst, `src/static/stil.css` stilen, `src/hjelpetekster.py` hjelpen til historikken og Sluttkurs på aksjesiden, og `docs/hjelp.md` et spørsmål. Bildene tas på nytt, og avtrykkene i `tests/test_docker.py` rettes.
3. c) Testene i `tests/test_historikken.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Plasseringen:** avsnittet står nederst på siden, etter avsnittet om investorsiden og før hjelpevinduene. Avsnittet om investorsiden står fortsatt rett under grafen, etter de to fotnotene som sto der før.
- **Måneden** i adressen er `maaned=ÅÅÅÅ-MM`. Uten den er måneden den for dagen siden viser: dagen fra «Velg dag», ellers siste kursrad. En verdi som ikke kan leses, eller en måned utenfor kursserien, gir måneden for dagen og en beskjed under pilene, med 200.
- **Pilene** står over ukene: «‹ <forrige måned>» og «<neste måned> ›», bare når den måneden har en kursrad i serien. Lenkene beholder `dag` når en dag er valgt, ellers `periode` når adressen hadde en gyldig periode, og ender med `#signalet-dag-for-dag`, så siden blir stående ved avsnittet.
- **Ukene** er ukene etter ISO 8601, med ukenummeret, og bare mandag til fredag. En dag i uka som hører til en annen måned, står som en tom plass og telles ikke.
- **Dagen:** datoen, og med en vurdering retningen med symbolet og ordet, T, B og I som brikkene i oversikten, og styrken som «x av 3». Uten vurdering «–» og teksten fra `les_tilstand`. 3 av 3 får pillen med svart fyll og ring i sterk oransje og strek til venstre, som i oversikten (§3). 2 av 3 merkes ikke, fordi §3 merker 2 av 3 bare for siste børsdag.
- **«Skilte seg ut»** er styrken på terskelen eller over, som i oversikten (`Parametre.terskel`). Uka og måneden teller dagene med en vurdering. Har uka ingen, står «ingen dager med vurdering». Har måneden ingen, står «<måned> samlet: <navn> har ingen dager med vurdering.», uten tallene for sjekkene.
- **Sjekkene som slo ut:** antallet dager med +1 eller -1 for hver av de tre, med navnene fra aksjesiden.
- **Lenken:** hver dag med en kursrad lenker til `/aksje/<symbol>?dag=ÅÅÅÅ-MM-DD`, siden for dagen fra 8.16b, som viser målingene. Første dag i serien får ingen lenke, fordi `les_valg` ikke godtar den (8.16, BH3).
- **Dager etter siste kursrad** står med bare datoen. Har en slik dag likevel en rad i vurdering, som en grunn når hentingen feilet, vises raden, fordi den er skrevet og ikke er et hull.

## Avgjort underveis

- **`les_periode` står i porten og i `SqliteVurderingslager`**, og siden lager lageret med aksjen siden viser som lista. Da kan også demoselskapene leses, og kontrollen av nøkkelen er den samme som i `les` (`64ee382`). Med `fra` etter `til` reiser den `ValueError` (gjennomgangen, BH12).
- **De to eldre testene for porten** i `tests/test_vurderingslager.py` krevde akkurat `skriv` og `les`. Nå krever de også `les_periode`, og fortsatt ingen slett og ingen endre.
- **`tests/test_utseende.py`** godtar lenkene til siden for dagen og pilene med måneden. `tests/test_hjelpetekster.py` har de nye vinduene. `tests/test_docker.py` har historikken i «Ferdig», ett punkt under «Neste i v1» og `src/historikk.py` i avtrykket bak bildet av aksjesiden.
- **Hjelpen ved Sluttkurs (U5)** har en egen tekst på aksjesiden, `sluttkurs_aksje`, og vinduet sier dagen siden viser, som «Siden viser fredag 09.10.» (gjennomgangen, VG2). Oversikten har teksten fra før.
- **En uke uten en eneste dag i kursserien** har ingen tekst under seg, så den ikke ser ut som et hull.
- **Dagene utenfor kursserien:** også dagene før første kursrad står tomme, og når måneden har slike dager, sier en linje «Kursserien går fra <første> til <siste>, så dagene utenfor står tomme.» (gjennomgangen, BH2, ECH1, ECH2, VG10). Dagene etter siste kursrad står tomme, som instruksjonen sier, og linja sier hvor serien slutter, så de ikke leses som et hull.
- **Pilene** går til nærmeste måned med en kursrad, ikke bare til måneden før eller etter (gjennomgangen, VG9).
- **Brikkene i en dag** brytes over to linjer i en smal rute, og går ikke ut av den (gjennomgangen, BH3, `c780d6c`).
- **390 px**, målt i Edge uten vindu med siden i en iframe på 390 px: `scrollWidth` er 390 på `/aksje/KVST`, `?maaned=2026-09`, `?dag=2026-09-15`, `/aksje/BRFE?maaned=2026-08`, `/` og `/min-liste` i demoen. På 780 og 900 px er den lik bredden (gjennomgangen, VG1 og BH3).
- **Bildene** ble tatt på nytt tre ganger, etter fremgangsmåten i 3.3b og 3.3f, og var hver gang byte for byte de samme. Avsnittet om investorsiden begynner ved 1980 px, under bildet, som slutter ved bunnen av grafen (1872 px), og historikken står under det. Bare avtrykkene er nye.

## Gjennomgangen

Blind Hunter fant 14 funn, Edge Case Hunter 12 og Verification Gap 12, til sammen 38: 29 rettet, 4 avvist og 5 uten endring. Rettingene står i `4289d93` og `c780d6c`.

| # | Funn | Dom | Utfall |
|---|---|---|---|
| BH1 | Testen for basefeil godtok 500 | medium | rettet: krever 503 og feiltypen |
| BH2 | Dagene før første kursrad viste «– ikke vurdert» | medium | rettet: de står tomme |
| BH3 | Innholdet i en dag kunne gå ut av ruta mellom 760 og 900 px | medium | rettet: brikkene brytes; målt på 780 og 900 px |
| BH4 | Uka teller 2 av 3, men bare 3 av 3 merkes | lav–medium | avvist: «x av y dager skilte seg ut» er instruksjonens ord, og §3 merker 2 av 3 bare for siste børsdag |
| BH5 | Ingressen sa «hver børsdag», og hjelpen «klikk på en dag» | lav | rettet: «hver dag, eller hvorfor det mangler» og «en dag med kurs» |
| BH6 | Docstringen i fixturen sa 06.10 for DNB | lav | rettet: 07.10 |
| BH7 | Importtesten ser bare på `historikk.py` | lav | uten endring: `test_siden_regner_aldri_signalet` stopper `vurder` i alle modulene i `src/` |
| BH8 | Bare `vurder` stoppes | lav | uten endring: signalet regnes bare gjennom `vurder`, og testen for tilstandene viser de lagrede radene |
| BH9 | Lenken på en dag beholder ikke perioden | lav | avvist: siden for dagen er «Velg dag», der perioden ikke gjelder, og den skal begynne øverst med målingene |
| BH10 | `display: contents` på lista | lav | uten endring |
| BH11 | Navnet på avsnittet tok med hjelpeknappen | lav | rettet: `aria-labelledby` peker på teksten alene |
| BH12 | `les_periode` godtok `fra` etter `til` | lav | rettet: `ValueError` |
| BH13 | Testen for porten står to steder | lav | uten endring: instruksjonen c ber om den her |
| BH14 | «Under kursgrafen» i `docs/hjelp.md` | lav | avvist: avsnittet står etter grafen og to fotnoter, og en test holder rekkefølgen (VG5) |
| ECH1 | Dagene etter siste kursrad skjuler et hull som er endelig | medium | rettet: linja sier hvor kursserien slutter; dagene står tomme, som instruksjonen sier |
| ECH2 | Dagene før første kursrad | medium | rettet, som BH2 |
| ECH3 | Formen på måneden var ikke testet | medium | rettet: `2026-1` og `2026x10` i testen |
| ECH4 | Siste måned i adressen var ikke testet | medium | rettet |
| ECH5 | Pilene i nest første og nest siste måned var ikke testet | medium | rettet |
| ECH6 | En måned som begynner i helgen | lav–medium | rettet: august 2026 i testen |
| ECH7 | Siste kursrad uten rad | lav | rettet: DNB 09.10 i testen |
| ECH8 | Escapingen av beskjeden | lav | rettet |
| ECH9 | Avkortingen av beskjeden | lav | rettet |
| ECH10 | Terskelen var ikke testet med en annen verdi | lav | rettet: terskel 3 i testen |
| ECH11 | 500 eller 503, som BH1 | lav | rettet |
| ECH12 | Sjekket uten funn | info | uten endring |
| VG1 | 390 px var ikke ført | medium | rettet: målt og ført over |
| VG2 | Hjelpen ved Sluttkurs sa ikke datoen | medium | rettet: «Siden viser <dag>» i vinduet |
| VG3 | Stilen for 3 av 3 var ikke testet | medium | rettet |
| VG4 | Dager i en annen måned ble ikke prøvd | medium | rettet: en rad 30.09, i uke 40 |
| VG5 | Rekkefølgen grafen, investorsiden og historikken var ikke testet | medium | rettet |
| VG6 | Mutantene og triagen var ikke ført | medium | rettet: ført under |
| VG7 | Seks tester manglet «Ville feilet hvis» | lav | rettet |
| VG8 | Hjelpen var bredere enn koden | lav | rettet, som BH5 |
| VG9 | En pil kunne gå til en måned uten kursrad | lav | rettet |
| VG10 | Dagene før første kursrad | lav | rettet, som BH2 |
| VG11 | Kontrollpunktet om fire uker står uten datert linje | lav | rettet etter flettingen: en datert linje under story 2.7 |
| VG12 | Bildene viser ikke historikken | lav | avvist: bildet slutter ved grafen etter `HOEYDE_PAA_AKSJESIDEN`, og et nytt bilde er ikke bedt om |

*Rettet 2026-10-21 kl. 17:46:* BH4, med dom lav–medium, er rettet i `979041e` og ikke avvist, fordi steg 4 i instruksjonen krever at funn med dom medium er rettet. Ingressen sier nå at en dag skilte seg ut når signalstyrken var 2 eller mer, som i oversikten, og at 3 av 3 er merket med strek og ring. En test krever setningen. Det gir 30 rettet, 3 avvist og 5 uten endring. Bildene ble tatt på nytt og var byte for byte de samme.

*Rettet 2026-10-21 kl. 17:49:* setningen i linja over brøt to eldre tester i `tests/test_app.py`, som krever at «skilte seg ut» ikke står på siden når aksjen ikke skilte seg ut (CI 39628737448). I `4b97c37` sier ingressen i stedet «Tallene for uka og måneden teller dagene med signalstyrke 2 eller mer, som i oversikten, og 3 av 3 er merket med strek og ring.»

## Mutantene

Én om gangen med `-x` på `tests/test_historikken.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 lik HEAD etter hver, og `git status` tom. M1–M3 er fra instruksjonen, kjørt på `41f7594` og igjen på `4289d93`. N1–N10 er mutantene fra Edge Case Hunter som overlevde, og to til, kjørt på `4289d93`. Alle ble fanget.

| # | Mutant | Fanget av |
|---|---|---|
| M1 | Historikken regnet med `vurder` | `test_hver_tilstand_ser_ulik_ut` |
| M2 | En manglende rad vist som styrke 0 | `test_hver_tilstand_ser_ulik_ut` |
| M3 | Dager etter siste kursrad vist som «– ikke vurdert» | `test_tallene_for_ukene` |
| N1 | Formen på måneden ikke sjekket | `test_en_ugyldig_maaned_gir_maaneden_for_dagen_og_en_beskjed` |
| N2 | Siste måned regnet som utenfor serien | `test_siste_maaned_i_adressen_gir_ingen_beskjed` |
| N3 | Pila framover borte en måned for tidlig | `test_nest_siste_og_nest_foerste_maaned_har_begge_pilene` |
| N4 | Pila bakover borte en måned for tidlig | `test_nest_siste_og_nest_foerste_maaned_har_begge_pilene` |
| N5 | En uke uten dager i måneden tatt med | `test_en_maaned_som_begynner_i_helgen_har_ingen_tom_uke_foerst` |
| N6 | Siste kursrad tom | `test_siste_kursrad_uten_rad_er_ikke_vurdert` |
| N7 | Beskjeden uten escaping | `test_en_lang_eller_farlig_verdi_kortes_av_og_escapes` |
| N8 | Beskjeden uten avkorting | `test_en_lang_eller_farlig_verdi_kortes_av_og_escapes` |
| N9 | Terskelen 2 i koden | `test_terskelen_bestemmer_hva_som_skilte_seg_ut` |
| N10 | Dagene før første kursrad ikke tomme | `test_dagene_foer_foerste_kursrad_er_tomme` |
