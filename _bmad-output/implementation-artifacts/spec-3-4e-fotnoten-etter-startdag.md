---
title: 'Story 3.4 (3.4e): fotnoten etter startdagen i demoen, og for i dag'
type: 'bugfix'
created: '2026-10-23'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '651be64'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4d-fotnoten-ikke-vurdert.md'
---

## Intent

**Problem:** spesifikasjonen 3.4d har to åpne punkter. I demoen forklarer fotnoten en rad «ikke vurdert» med startdagen 21.09, også når raden er fra etter 21.09 (BH3, ECH1 22.10). I den ekte versjonen sier fotnoten at signalet aldri regnes ut bakover, også for dagens børsdag før kveldens henting har skrevet vurderingen (ECH3 23.10).

**Grunnlaget:** gruppens svar 23.10 kl. 15:53 under «Prioritering» og story 3.4: små funn fra en gjennomgang rettes med en gang, først de to åpne punktene i 3.4d. Teksten under er fra instruksjonen 23.10 kl. 16:06 i dagsfila.

## Slik er det i dag (slått opp 23.10 på `651be64`)

- **Fotnoten** står i delmalen `src/templates/_fotnote_ikke_vurdert.html`, og velger demoteksten med `{% if eksempeltall %}`. Aksjesiden (`detalj.ikke_vurdert`), oversikten og Min liste (`ikke_vurdert` fra radene) og børsometeret (`ikke_vurdert` fra rutene) tar den inn.
- **Datoen** for det som er «ikke vurdert»: `detalj.dato` på aksjesiden, `rad.dato` for hver rad på oversikten, og `dagen` på børsometeret. `STARTDAG` kommer fra `src/demo.py`, og `idag()` fra `src/app.py`.
- **Demoen** skriver en vurdering for hver aksje hver børsdag fra `STARTDAG`, så en rad «ikke vurdert» etter 21.09 finnes bare i en base som er endret for hånd, som i testen `test_oversikten_med_en_rad_som_mangler`.

## Kontrollpunktene

- a) Demoteksten står bare for en dag før `STARTDAG`. En dag fra `STARTDAG` og senere uten vurdering får den ekte teksten, også i demoen, slik en kveld uten henting gjør i den ekte versjonen. Testen som sletter en rad 09.10 i demoen, krever da den ekte teksten, med grunnen.
- b) Er dagen som vises, i dag, står det i tillegg i fotnoten: «For i dag kan signalet fortsatt lagres hvis hentingen kjøres ferdig i kveld.» Ellers står den ekte teksten fra kl. 23:19 uendret.
  *Rettet 2026-10-23 (gruppens svar 23.10 kl. 19:10, gjennomgangen 23.10 kveld, VG5):* setningen står når en av dagene er inneværende børsdag (`innevaerende_boersdag`), og lyder «Signalet for denne dagen kan fortsatt lagres hvis hentingen kjøres ferdig før neste børsdag.»
- c) Testene, med «Ville feilet hvis», uten nett: i demoen demoteksten før `STARTDAG` og den ekte teksten etter, på aksjesiden, oversikten og børsometeret; setningen om i dag bare når dagen er i dag, med `idag` satt i testen.
- Hjelpen og `docs/hjelp.md` følger med der de sier det samme (regel 19). Bildene tas på nytt bare hvis testene krever det.

## Planen, én commit per punkt

1. a) `_fotnoten(datoer)` i `app.py` gir malen `fotnote_demo`: sant i demoen når alle datoene som er «ikke vurdert», er før `STARTDAG`. Har oversikten rader både før og etter, står den ekte teksten, fordi den dekker begge. Delmalen bruker `fotnote_demo` i stedet for `eksempeltall`.
2. b) `_fotnoten` gir også `fotnote_i_dag`: sant når en av datoene er `idag()`. Setningen står etter den ekte teksten.
   *Rettet 2026-10-23 (gruppens svar 23.10 kl. 19:10, gjennomgangen 23.10 kveld, VG5):* `fotnote_kan_lagres`, sant når `innevaerende_boersdag(idag())` er en av datoene, i `2fd2635`.
3. c) Testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: demoteksten for alle dager i demoen, og setningen om i dag for en annen dag.

*Lagt til 2026-10-23:* kjørt på `622e25f` i en klon med `core.autocrlf=false`, slettet etterpå, med `tests/test_app.py`, `tests/test_demo.py` og `tests/test_boersometer.py`, og så med de nye testene alene (`-k`). Begge ble fanget, og sha256 for `src/app.py` var lik HEAD etter hver:

| # | Mutant | Først i filene | Alene |
|---|---|---|---|
| M1 | Demoteksten for alle dager i demoen | `TestFotnotenIDemoen::test_oversikten_med_en_rad_som_mangler` | `test_aksjesiden_etter_startdagen_har_den_ekte_teksten`, `TestFotnotenEtterStartdagen::test_demoen_etter_startdagen_har_den_ekte_teksten` |
| M2 | Setningen om i dag for en annen dag | `TestVurderingenPaaOversikten::test_ikke_vurdert_med_fotnoten` | `TestFotnotenForIDag::test_ingen_setning_en_annen_dag[/]`, `TestFotnotenEtterStartdagen::test_setningen_om_i_dag` |

*Lagt til 2026-10-23, etter gruppens svar 23.10 kl. 19:10 under story 3.4 i `epics.md`:* M3, vilkåret tilbake til i dag (`"fotnote_kan_lagres": not demo and i_dag in datoer`), kjørt én gang med `-x` på `2fd2635` med de nye testene i arbeidskopien, med kopi før og `tests/test_app.py`, `tests/test_boersometer.py` og `tests/test_demo.py`. Fanget av `TestFotnotenForInnevaerendeBoersdag::test_fredagen_i_helga[loerdag-/]`, etter 283 bestått. De nye testene alene (`-k Innevaerende`): 6 feilet og 8 bestått, alle for lørdag, søndag og julaften. Etter kopien tilbake var `git hash-object src/app.py` lik `HEAD:src/app.py`, og sha256 uten CR var lik HEAD; arbeidskopien har CRLF (`core.autocrlf=true`), så sha256 på selve fila er ikke den samme.

## Gjennomgangen 23.10

Gjennomgang 23.10 etter hele settet, på diffen `651be64..622e25f` og `31feb13` og `651be64` på main. Linsene var Blind Hunter (BH, 8 funn), Edge Case Hunter (ECH, 6 funn) og Verification Gap (VG, 9 funn), hver for seg og uten å endre noe i repoet. 23 funn ble 18 rader. Ett hadde dom medium, ECH1, og det er ikke rettet, så flettingen venter på gruppen (steg 4).

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1 | På en lørdag, søndag eller helligdag kan fredagens signal fortsatt lagres, men setningen om i dag står bare når dagen er i dag | medium | **ikke rettet**: instruksjonen gir vilkåret («er dagen som vises, i dag») og setningen ordrett, og «For i dag» passer ikke for fredagen lest på lørdag. Gruppen avgjør; flettingen venter |
| BH2 | Setningen om i dag står også etter at kveldens henting har gått, hvis raden fortsatt mangler | low | uten endring: siden vet ikke om hentingen har gått; føres under «Åpent» sammen med ECH1 |
| BH1, ECH3 | I demoen kunne setningen om i dag stå, selv om ingen henting skriver til en demobase | low | rettet i `5ff7e1c` |
| ECH2 | `_fotnoten` leste klokka en gang til | low | rettet i `5ff7e1c`: samme `i_dag` som siden |
| BH3, ECH6 | Samme sjekk regnet to ganger på børsometeret og oversikten | nit | rettet i `5ff7e1c` |
| ECH5 | Aksjesiden ga datoen også når dagen ikke er «ikke vurdert» | nit | rettet i `5ff7e1c` |
| VG1 | STARTDAG selv var ikke testet | low | rettet i `1aac9f3` |
| VG2, ECH4 | Datoer både før og etter STARTDAG på oversikten var ikke testet | low | rettet i `1aac9f3` |
| VG3 | De nye testene sa «Ville feilet uten/med», ikke «hvis» | low | rettet i `1aac9f3` |
| VG4 | Mutantene var ikke ført | low | rettet: tabellen over |
| VG5 | Spesifikasjonen 8.1 viste fortsatt til «Åpent» for de to lukkede punktene | low | rettet her: Rettet-linjer |
| VG6 | Innledningen i `docs/brukertest.md` sa ikke at 10.4 kan tas med neste person | nit | rettet her: en Rettet-linje |
| VG8 | Spesifikasjonen sto på `ready-for-dev` | nit | rettet: `in-review` |
| BH4, BH5 | Tekstene og oppsettet for den ekte versjonen står i flere testfiler | nit | uten endring: hver testfil sier hva siden skal vise |
| BH6 | `"ikke vurdert" in html` i testen av oversikten før STARTDAG er svak alene | nit | uten endring: sammenligningen av hele fotnoten etter dekker det |
| BH7, VG7 | To kommentarer per avtrykk sier at bildet ble tatt på nytt | nit | uten endring: bildene ble tatt på nytt etter hvert punkt og var like, som Utført-linja sier |
| BH8 | `docs/hjelp.md` skriver 21.09 for hånd | nit | uten endring: som VG6 22.10 i 3.4d |
| VG9 | Setningen om i dag er ikke testet på Min liste | nit | uten endring: samme `_fotnoten` og samme mal som oversikten |

## Åpent

- **Helg og helligdag** (ECH1, medium): lørdag, søndag og en helligdag er `innevaerende_boersdag` forrige børsdag, så hentingen kan fortsatt skrive den dagens vurdering (`skriv` i `src/lagring_sqlite.py`, og tidskontrollen i `src/fetch_prices.py` gjelder bare på en børsdag). Fotnoten sier da ikke at signalet kan lagres. Vilkåret og setningen står ordrett i instruksjonen, så gruppen avgjør om vilkåret blir «dagen er inneværende børsdag», og hvilken tekst som da står.
  *Lukket 2026-10-23 (gruppens svar 23.10 kl. 19:10 under story 3.4 i `epics.md`):* setningen står når dagen som vises, er siste børsdag fram til i dag, med samme regel som lagringen (`innevaerende_boersdag`), og lyder «Signalet for denne dagen kan fortsatt lagres hvis hentingen kjøres ferdig før neste børsdag.» Rettet i `2fd2635` (a), testet i `TestFotnotenForInnevaerendeBoersdag` (b).
- **Etter kveldens henting** (BH2): setningen om i dag står også etter at hentingen har gått, hvis raden fortsatt mangler. Siden vet ikke om hentingen har gått.
  *Lukket 2026-10-23 (gruppens svar 23.10 kl. 19:10 under story 3.4 i `epics.md`):* svaret erstatter vilkåret og setningen fra kl. 16:06, så punktet er avgjort. Setningen sier nå at signalet kan lagres hvis hentingen kjøres ferdig før neste børsdag.

## Gjennomgangen 23.10 kveld

Gjennomgang 23.10 etter hele settet, etter gruppens svar 23.10 kl. 19:10, på `21a7bfe` og `578d875` på main og diffen `cbdf7c6..5cacd5e` på grenen. Linsene var Blind Hunter (BH, 10 funn), Edge Case Hunter (ECH, 6 funn) og Verification Gap (VG, 7 funn), hver for seg og uten å endre noe i repoet. Numrene gjelder denne gjennomgangen, ikke den over. 23 funn ble 18 rader. Blind Hunter ga BH1 og BH2 dom medium; begge ble slått opp og holder ikke, så ingen funn med dom medium eller høyere står igjen. De små funnene er rettet med en gang (svaret kl. 15:53).

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | Står `fotnote_i_dag` igjen et sted, forsvinner setningen der uten feil | medium etter linsen, avvist | uten endring: slått opp, `fotnote_i_dag` finnes ikke i `src/`, `tests/` eller `docs/hjelp.md` |
| BH2 | «Samme regel som lagringen» holder bare hvis lagringen bruker samme dato | medium etter linsen, avvist | uten endring: slått opp, lagringen bruker `innevaerende_boersdag(norsk_dato(...))` (`src/lagring_sqlite.py`), og siden `idag()`, som er `norsk_dato(naa())` |
| BH3, VG1 | Grenen for `UtenforKalenderen` i `_innevaerende` var ikke testet | low | rettet i `0fd807f` |
| BH4, ECH1 | Med flere datoer på oversikten sier ikke «denne dagen» hvilken | low | uten endring: teksten er gruppens ordrett; føres under «Åpent» |
| BH5 | Lukket-linja for BH2 er en avgjørelse, ikke en retting | low | uten endring: linja sier at svaret avgjør punktet |
| BH6, VG2 | Helga var ikke testet på børsometeret | low | rettet i `0fd807f` |
| BH7, VG4 | Konstanten `I_DAG` og `i_dag` holdt den nye setningen | nit | rettet i `0fd807f`: `SETNINGEN`; testnavnene står, fordi mutanttabellen over viser til dem |
| BH8, ECH5 | `bool(datoer)` i vilkåret er overflødig | nit | uten endring: en tom liste gir da ikke noe oppslag i kalenderen |
| BH9 | Ordlyden i `docs/hjelp.md` var tung | nit | rettet i `53223ca` |
| BH10 | Testene forutsetter at `serie` bruker kalenderdager | low | uten endring: slått opp, `serie` i `tests/test_app.py` legger til én kalenderdag per rad fra 01.09, så 60 rader slutter 30.10 og 114 rader 23.12 |
| ECH2 | Hentingen kan likevel ikke bli ferdig, når kvoten er brukt opp eller datoen skifter under kjøringen | low | uten endring: setningen er betinget («hvis hentingen kjøres ferdig») |
| ECH3 | Midnatt i Oslo mot UTC var ikke testet | nit | rettet i `0fd807f` |
| ECH4 | Lagringen godtar også forrige børsdag ved første henting i en tom base | nit | rettet i `0fd807f`: docstringen sier det, og at ingen rad da er «ikke vurdert» |
| ECH6 | En side som står åpen over midnatt, viser setningen til den lastes på nytt | nit | uten endring: siden bygges på serveren |
| VG3 | Ingen test av helga i demoen | low | rettet i `0fd807f` |
| VG5 | Kontrollpunktene og planen beskrev fortsatt vilkåret fra kl. 16:06 | nit | rettet her: Rettet-linjer |
| VG6 | Raden ECH1 i triagen over sier fortsatt «ikke rettet» | nit | rettet her: Lukket-linja under «Åpent» og denne tabellen; raden står som historikk |
| VG7 | Spesifikasjonen står på `in-review`, og bildene kan ikke sjekkes fra diffen | nit | uten endring: `done` etter flettingen (steg 4); bildene ble tatt på nytt, og git viste ingen endring |

Under «Åpent», etter gjennomgangen 23.10 kveld:

- **Flere datoer på oversikten** (BH4, ECH1, low): er en aksje «ikke vurdert» torsdag og en annen fredag, står setningen, men «denne dagen» gjelder bare fredagen. Teksten er gruppens ordrett.

## Det som ikke endres

- Hentingen, lagrene og demodataene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
