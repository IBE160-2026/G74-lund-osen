---
title: 'Story 8.2 (8.2b): fire ting som i designforslaget (svarene 04.11 kl. 22:23)'
type: 'feature'
created: '2026-11-05'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: '7d2a7321'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-2b-funnene-fra-ux-loggen.md'
---

## Intent

**Grunnlaget:** gruppens svar 04.11 kl. 22:23, ført under story 8.2 i `epics.md` («Avgjort 2026-11-04 kl. 22:23»), og instruksjonen 05.11 kl. 11:50 i `docs/ai-prompts/2026-11-05.md` (`0eab0e3a`). Bygges på grenen `8-2b-som-designforslaget` med PR, én commit per svar, og stopper før flettingen.

1. Store ruter i børsometeret, med en egen grense regnet som `NIVAA_3` og `STYRKE`.
2. Under søylene på oversikten, til høyre for «Stiplet linje: hovedindeksen»: lenken «Se perioden i Børsometer» med pil, til børsometeret med samme periode eller dag.
3. KI-delen på aksjesiden heter «<navnet> kort fortalt», i Newsreader, med «?».
4. Menyknappene øverst får ikoner: en tabell, en måler og en stjerne.

**Tallene fra designforslaget.** Designforslaget ligger i Claude, ikke i repoet (`designregler.md` §1, og linja under svaret i `epics.md`), så tallene er ikke slått opp mot det. De er tatt fra instruksjonen kl. 11:50 og svaret i `epics.md`:

| Hva | Tallet |
|---|---|
| Symbolet i en stor rute | 22 px, halvfett, øverst til venstre |
| Selskapsnavnet | 12,5 px, under symbolet, kuttet med «…» |
| Styrken | øverst til høyre, «3 av 3» og «2 av 3» i ringen som nå, ellers som tekst |
| Endringen | 28 px, halvfett, nederst |
| Luften i ruta | 10 px over og under, 12 px på sidene |
| Merket og grunnen | mellom navnet og endringen, der de får plass |
| Små ruter | som før, 14 px |
| Lenken under søylene | «Se perioden i Børsometer ›», halvfet; pila er «›» som i svaret i `epics.md` |
| KI-delen | «<navnet> kort fortalt», Newsreader, med «?» |
| Ikonene | 16 px, strek 2, i tekstfargen: tabell, måler (halvsirkel med viser), stjerne |

Instruksjonen sier «tabellikon», og svaret i `epics.md` sier «rutenett». Ikonet er et rektangel med en topplinje, en linje til og en loddrett strek, altså en tabell, som også er et rutenett.

## Slått opp 05.11 på `7d2a7321` (regel 3)

- `boersometer.py`: `NIVAA_3 = (126, 106)` og `STYRKE = (81, 75)`, regnet for 14 px, og `tekstnivaa` med nivå 0–3. Rutene har klassene `nivaa-N-K`, `styrke-N` og `grunn-N` for de fire klassene `bredest`, `bred`, `smal` og `smalest` (`Flate.tekst`), og stilen velger med `@container`.
- De lengste symbolene i `kursdata.py` og demoen: `AKRBP`, fem tegn.
- `_hovedindeks.html`: «Stiplet linje: hovedindeksen» står i `p.linjeforklaring`, som er `aria-hidden`.
- `aksje.html`: KI-delen hadde `<h2>Med KI-ens ord</h2>` og `aria-label="KI-tekst"`. Alle `h2` står i Newsreader (`h1, h2` i `stil.css`).
- `ki_grunnlag.py`: modellen får fortegnet for hver sjekk, styrken og retningen, og med dagen hvor mange aksjer i lista som steg og falt (`ANTALLENE`), og retningen på hovedindeksen og bransjen når de kan regnes (`VALGFRIE`). Ingen kurser, volumer, prosenter eller forholdstall. Kontrollen i `ki_kontroll.py` slipper bare antall fra grunnlaget og stopper ord som gir råd (punkt 2 og 3), og `prikkede_tall` i `ki_visning.py` merker tallene i en tekst som alt har bestått kontrollen.
- `_ramme.html`: de tre `a.sideknapp` hadde bare tekst.

## Svar 1: store ruter (`67f4c701`)

**Nivå 4.** En rute som er på nivå 3 og har plass etter `STOR`, får nivå 4 (`storplass` og `_nivaa_ved`). Der er ruta et rutenett i stilen: symbolet og styrken øverst, navnet under, merket og grunnen, og endringen nederst. Navnet er en egen `span.navn`, `aria-hidden`, fordi skjermleseren leser navnet i linja under. Små ruter, nivå 0–3, er som før.

**Grensen `STOR = (193, 107)`**, regnet med tallene i `stil.css` (`test_grensen_for_store_ruter_er_regnet_fra_stilen`):

- Høyden: rammen 2 × 4, luften 2 × 10, linjene 1,2 × (22 + 12,5 + 28) = 75, og 2 px over navnet: 8 + 20 + 75 + 2 = 105, rundet opp til 107.
- Bredden øverst: rammen 2 × 4, luften 2 × 12, `AKRBP` i 22 px halvfett med 0,62 em per tegn (68,2), 8 px mellomrom og «ikke vurdert» i 14 px med 0,5 em per tegn (84): 192,2.
- Bredden nederst: 32 + «Uten data» i 28 px halvfett, 0,62 × 28 × 9 = 156,24: 188,24.
- `STOR` er 193 × 107 og er bredere enn `NIVAA_3`.

**Merket og grunnen** står der de får plass (`_stor_linjer`): merket først, med `_linjer` på 14 px, og grunnen under det bare når merket står eller ikke trengs. En annen dag står styrken i en gul rute bare med merket, som på nivå 2 (svaret 04.11 kl. 20:53 og 20:56, 1). Rutene får klassen `merke-N` i tillegg.

*Rettet 05.11 etter gjennomgangen (ECH1, BH3, ECH3), i `36c53166`:* merket står i halvfet skrift og regnes nå alltid som to linjer, som i `grunnplass`, ikke med `_linjer` på 0,5 em. En rute er stor bare når også endringen slik den vises får plass i 28 px halvfett (`_stor_endring_plass`), fordi en endring over en periode kan ha flere tegn enn «Uten data».

**Hjelpen og `docs/hjelp.md`** sier at de største rutene har symbolet og styrken øverst, navnet under og endringen i stor skrift nederst.

**I demoen** er rutene store bare i klassen `bredest`, fra 1079 px: siste børsdag SLVP, KVST, LKSV og TRHF; ved en periode og 18.09 og 01.09 BLGT, LSTF, LKSV og TROY. I `bred`, `smal` og `smalest` er ingen rute 193 px bred.

**Testene** står i `tests/test_designforslaget.py`. To tester i `test_boersometer.py` regner nå med nivå 4 (`_nivaaet`). Den første kjøringen viste at de feilet fordi endringen ikke var ferdig (svaret 4.11 kl. 09:48), og de ble rettet. Navnet sto først mellom symbolet og endringen i HTML-en og ble flyttet ned til rett før den skjulte linja, så regexene i `test_boersometer.py` fortsatt fant symbolet og endringen.

## Svar 2: lenken under søylene (`0186234a`)

`div.soeylefot` rundt forklaringen og lenken, med `justify-content: space-between`, og lenken med `margin-left: auto` og `font-weight: 600`. Adressen er `/boersometer?periode=<perioden>`, og ved en valgt dag `/boersometer?periode=velg&dag=<dagen>`. Lenken står også når den stiplede linja mangler, til høyre. Hjelpen for søylene og `docs/hjelp.md` sier det. Bildet `docs/appen/oversikten-demo.png` er tatt på nytt med lenken; bunnen av siste rad under «Skilte seg ut» er fortsatt 1864 px, målt i Edge på main og på grenen.

## Svar 3: «<navnet> kort fortalt» (`26678ef6`)

`<h2><span id="ki-tittel">… kort fortalt</span> ?</h2>`, og seksjonen har `aria-labelledby="ki-tittel"` i stedet for `aria-label="KI-tekst"`. «?» åpner `hjelp-ki` med teksten `ki_kort_fortalt`, med kildene i `ki_grunnlag.py`, `ki_visning.py`, `ki_kontroll.py` og `aksje.html`. Hjelpen har høyst tre setninger og ingen ord fra lista over ord som er valgt bort, så den sier «om hver av sjekkene» og «gir ikke råd». `docs/hjelp.md` har et eget avsnitt, «Hva er «kort fortalt» på aksjesiden?». Ni linjer i tre testfiler så etter «Med KI-ens ord» og ser nå etter «kort fortalt». Bildet av aksjesiden i `docs/appen/` er tatt på nytt; bunnen av `p.dagene` er fortsatt 2198 px.

## Svar 4: ikonene (`7aae85db`)

`svg.ikon` foran navnet i hver `a.sideknapp`, `aria-hidden` og `focusable="false"`, 16 × 16 med `stroke: currentColor` og `stroke-width: 2`, og 8 px til navnet (`gap` i regelen for `a.sideknapp`). Ikonet følger fargen på knappen, så den fylte knappen har mørke ikoner. `docs/hjelp.md` sier hvilket ikon som står på hver knapp. README-linja under «Ferdig» fikk først «med ikoner», men linja ble da 22 ord, over grensen på 20 i `test_status_uten_storynumre_og_uten_kommando`, og den stemmer uten. Den ble derfor stående som før. Tre tester leste knappeteksten rett etter `>` og tar nå ikonet ut først. Bildene i `docs/appen/` er tatt på nytt med ikonene.

## Tester, mutanter og målinger

**Hele settet** alene før hver commit med kode, grense 15 minutter, med ledig minne 3,5–4,5 GB:

| Før | Bestått | Hoppet over | Feilet |
|---|---|---|---|
| `67f4c701` | 4037 | 24 | 4 porttester for `start.ps1` |
| `0186234a` | 4040 | 24 | 7 porttester |
| `26678ef6` | 4043 | 24 | 7 porttester |
| `7aae85db` | 4052 | 24 | 3 porttester |

Første kjøring før svar 1 og før svar 4 feilet også fordi endringene ikke var ferdige: avtrykkene i `test_docker.py`, regexene over og README-linja. De ble rettet, og settet ble kjørt på nytt (svaret 4.11 kl. 09:48).

**Mutantene**, én per svar, på den committede fila, med kopi før og git-bloben og sha256 av innholdet uten CR lik HEAD etter:

| | Mutanten | Fanget av |
|---|---|---|
| M1 | `if nivaa == 3 and storplass(b, h):` → `if False:` | 4 tester, 2 i `test_designforslaget.py` og 2 i `test_boersometer.py` |
| M2 | lenken uten perioden, alltid `/boersometer` | 3 tester |
| M3 | overskriften tilbake til «Med KI-ens ord» | `test_ki_delen_heter_navnet_kort_fortalt` |
| M4 | ikonet i «Børsometer» tatt ut | 4 tester |

**Edge i en iframe**, 05.11 kl. 13:16, med demobasen i en midlertidig mappe: 10 visninger × 10 bredder (1280, 1100, 1079, 900, 761, 760, 600, 390, 360 og 320 px): børsometeret siste børsdag, 1 uke, 18.09 og 01.09, oversikten siste børsdag, 1 mnd og 05.10, Min liste, og aksjesidene for BRFE og TRHF. Ingen synlig tekst utenfor ruta, ingen synlig tekst utenfor vinduet og ingen vannrett rulling i noen av de 100. Måleren venter til stilen og skriftene er lastet i hver ramme. En tidligere runde målte en 404-side for adressene uten `?`, fordi Git Bash gjorde `/boersometer` om til en sti på disken; den runden er forkastet, og alle 100 er målt på nytt med `MSYS_NO_PATHCONV=1`.

**Bildene** før (main `7d2a7321`) og etter (`7aae85db`) av oversikten, børsometeret og aksjesiden for BRFE ved 1280 og 390 px står på `pr-8-2b-bilder` i `55f97d82`, med navn som begynner på `designforslaget-`. Bare demoen, ingen ekte kurser.

## Åpent: spørsmål til gruppen

1. **En gul rute en annen dag uten plass til merket** (følger av svar 1 og svaret 04.11 kl. 20:53 og 20:56, 1). LKSV 18.09 er stor ved 1280 px, men merket «3 av 3 siste børsdag» får ikke plass mellom navnet og endringen. Da står verken merket eller styrken («ikke vurdert»), bare symbolet, navnet og endringen. Skal det være slik, eller skal merket gå foran navnet, eller ruta bli liten (nivå 3) når merket ikke får plass?
2. **Store ruter bare fra 1079 px.** Med grensen 193 × 107 er ingen rute stor under 1079 px i demoen, og på 390 px er alle små. Er det som gruppen så for seg?
3. **Teksten på lenken** er «Se perioden i Børsometer ›» også når oversikten viser siste børsdag eller en valgt dag, som svaret sier. Skal den si «dagen» da?

*Besvart 05.11 kl. 14:29 (gruppens svar, under story 8.2 i `epics.md`):* 1) merket og styrken står i stedet for navnet; 2) store ruter bare fra 1079 px, som bygget; 3) «Se dagen i Børsometer» ved én dag og «Se perioden i Børsometer» ved en periode; 4) grensen regnes for hver rute, så høye, smale ruter som HVDO og BRFE blir store når alt deres får plass. Bygget etter instruksjonen 05.11 kl. 16:09, se «Svarene 05.11 kl. 14:29» nederst.

## Gjennomgangen 05.11 kl. 13:30

På diffen `7d2a7321..3cc34200`, etter hele settet, med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, 5), hver for seg. Rettingene står i `36c53166`. Hele settet før den: 4054 bestått, 24 hoppet over og 6 porttester for `start.ps1` som feilet. De 100 målingene i Edge ble gjort på nytt kl. 13:35, uten tekst utenfor ruta og uten vannrett rulling, og bildene i `docs/appen/` er byte for byte de samme.

| Funn | Alvorlighet | Hva | Avgjort |
|---|---|---|---|
| BH1 | høy | «?» kunne peke på et vindu som ikke finnes | Avvist: `ki_vises` settes inne i `{% if detalj.sjekker %}`, så vilkåret for knappen og vinduet er det samme. Ingen funn står på høy. |
| BH2 | middels | Hjelpen nevnte ikke merket for en aksje utenfor de 15, og sa «ga utslag» om fortegnet | Rettet: «ga +1, 0 eller -1» og merket, med kilden `UTENFOR_MAALINGEN` |
| BH3, ECH3 | middels, lav | En lang endring over en periode får ikke plass i 28 px | Rettet: `_stor_endring_plass`, test med «+1 234,56 %» |
| BH4 | middels | En gul rute en annen dag uten plass til merket viser verken merket eller styrken | Åpent, spørsmål 1 til gruppen. Følger av svar 1 og svaret 04.11 kl. 20:53 og 20:56, 1. |
| BH5 | middels | `velg` uten dag ga `/boersometer?periode=velg` uten dag | Rettet: da får lenken ingen periode, og børsometeret viser siste børsdag |
| BH6, VG5 | lav | Ingen test av lenken uten stiplet linje | Rettet: test i `test_app.py` |
| BH7 | middels | `_nivaaet` i testene bruker `storplass` | Avvist: grensen selv er testet med faste tall i `test_storplass` (193 og 192, 107 og 106), og M1 ble fanget |
| BH8 | lav | Ringen i den øverste raden | Avvist: ringen er 22,4 px høy og lavere enn symbolet, 26,4 px, og «3 av 3» i ring (60,4 px) er smalere enn «ikke vurdert» (84 px), som grensen er regnet for |
| BH9, VG4 | lav, middels | Ingen test av at hver klasse står i riktig `@container` for nivå 4 | Rettet: `test_nivaa_4_staar_i_grensen_klassen_er_regnet_for` |
| BH10 | lav | De skjulte spennene i rutenettet | Avvist: `.skjult` og de skjulte elementene har `position: absolute`, og ruta har `position: absolute`, så de står ikke i rutenettet |
| BH11 | lav | Etiketten «Hjelp: KI-teksten» | Rettet: «Hjelp: kort fortalt». Knappen står i overskriften som ved «Hvorfor signalet ble» og «Kursutvikling». |
| BH12 | lav | Navnet i alle ruter | Rettet: bare i ruter som er store i minst én klasse |
| BH13, ECH4, VG1 | lav, lav, middels | Faste tall i testen, ingen test av grunnen på nivå 4 | Rettet: høydene regnes fra konstantene, med grunnen med og uten merket |
| BH14 | lav | Samme regex for ikonene i tre testfiler | Står: tre linjer, ingen felles hjelper i conftest.py for dette |
| BH15 | lav | Hjelpen sier ikke at store ruter bare finnes i et bredt vindu | Avvist: om ruta er stor, avgjøres av størrelsen, ikke av vinduet. At det i demoen bare skjer fra 1079 px, er spørsmål 2. |
| ECH1 | middels | Merket regnet med 0,5 em, men står i halvfet skrift | Rettet, se Rettet-linja under svar 1 |
| ECH2 | lav | Ingen lenke når ingen aksje har søyle | Står: da står ingen søyler og ingen forklaring, og lenken hører til søylene |
| VG2 | middels | `annen_grunn_i_kartet` med nivå 4 uten test | Rettet: `test_fotnoten_for_en_annen_grunn_paa_nivaa_4` |
| VG3 | middels | Ingen test av at `kart()` fyller `merke` | Rettet: `test_kartet_og_siden_har_merket_i_en_stor_rute` |

## Svarene 05.11 kl. 14:29 og README-en (svarene kl. 12:14 og 12:20)

Instruksjonen 05.11 kl. 16:09 i `docs/ai-prompts/2026-11-05.md`. Main er flettet inn i `665b3642`. Én commit per endring:

- **Svar 1, `92d87579`:** en stor gul rute en annen dag uten plass til merket under navnet viser merket og styrken i stedet for navnet. Navnet står bare med klassen `navn-N` (`Kartrute.navn`). Får merket ikke plass der heller, er ruta ikke stor (`_stor_linjer` gir `None`). Merket regnes i linjer med `HALVFET_EM`, ikke alltid som to linjer, så LKSV 18.09 (231 × 123 px ved 1280 px) har merket på én linje i stedet for navnet. Hjelpen og `docs/hjelp.md` sier det.
- **Svar 3, `931b1ccc`:** lenken sier «Se dagen i Børsometer ›» når oversikten viser siste børsdag eller en valgt dag, og «Se perioden i Børsometer ›» ved 1 uke til 1 år, etter det samme som adressen i lenken. Hjelpen for søylene måtte kortes inn til «og «Se dagen» eller «Se perioden» under søylene …», fordi den ellers ble 79 ord, over grensen på 77 i `test_hovedindeksen_og_soeylene_har_hvert_sitt_vindu`.
- **Svar 4, `469b02b2`:** `storplass(rute, b, h)` regner bredden ruta selv trenger (`stor_bredde`): øverst symbolet i 22 px halvfett, 8 px og styrken, med ringen der den står (2 × 2 + 2 × 7,2 px), og nederst endringen i 28 px halvfett. Høyden er som før, `STOR[1]` = 107. HVDO og BRFE (175 og 173 px brede ved 1280 px, siste børsdag) trenger 154,96 px og er store. `STOR[0]` = 193 er nå den største bredden en rute med en endring på høyst ni tegn kan trenge. `_stor_endring_plass` er med i `stor_bredde`. **Tolkning av svar 2 sammen med svar 4:** med grensen per rute ville KVST og LKSV (160 px) blitt store også i klassen `bred`, 761–1078 px. Svar 2 sier «store ruter bare fra 1079 px: som bygget», så nivå 4 står bare i klassen `bredest` (`STORE_KLASSER`). Stilen for nivå 4 i de andre klassene står som før og brukes ikke.
- **README-en, `42088949`:** toppen av oversikten (1280 × 615 px, over periodeknappene) står synlig under beskrivelsen, og bak knappen står oversikten og aksjesiden som før, og børsometeret og Min liste ved 1280 px og oversikten og børsometeret ved 390 px, med alt-tekst og en kort tekst under hvert. Bare demoen. Bildene ved 390 px er tatt i en iframe som er 390 px bred, fordi Edge uten vindu ikke ble 390 px bredt (det første bildet ble kuttet til høyre). Hvert nytt bilde har adresse, størrelse, filene bak og avtrykk i `DE_NYE_BILDENE` og `AVTRYKK_BAK_DE_NYE_BILDENE` i `test_docker.py`, med to nye tester. «Dokumentene» under «Til faglærer» er delt i fem korte punkter, raden «Klar» er kortere (bonuskvoten står fortsatt, og mer i `docs/hjelp.md`), og «Brukertesten med én person, først med KI av» står under «Neste i v1», uten storynummer, fordi «Status» ikke har storynumre (`test_status_uten_storynumre_og_uten_kommando`). «Mappestruktur» har de nye bildene (regel 19).

**Hele settet** alene før hver commit med kode eller tester, grense 15 minutter, ledig minne 4,2–4,5 GB:

| Før | Bestått | Hoppet over | Feilet |
|---|---|---|---|
| `92d87579` | 4057 | 24 | 6 porttester for `start.ps1` |
| `931b1ccc` | 4058 | 24 | 7 porttester |
| `469b02b2` | 4062 | 24 | 5 porttester |
| `42088949` | 4066 | 24 | 3 porttester |

Første kjøring før svar 1 feilet også i tre avtrykkstester i `test_docker.py`, og første kjøring før svar 3 i lengden på hjelpen for søylene, fordi endringene ikke var ferdige. De ble rettet, og settet ble kjørt på nytt (svaret 4.11 kl. 09:48). En kjøring før svar 1 ble stoppet etter første feil med `-x` ved en feil, og ble kjørt på nytt uten.

**Mutantene**, på den committede fila, med kopi før og git-bloben og sha256 av innholdet uten CR lik HEAD etter:

| | Mutanten | Fanget av |
|---|---|---|
| P1 | `navn = False` tatt ut i `_stor_linjer` | 3 tester i `test_designforslaget.py` |
| P2 | lenken sier alltid «Se perioden» | 3 tester |
| P3 | `storplass` med den faste bredden `STOR[0]` | 5 tester |
| P4 | store ruter i alle klassene, ikke bare `bredest` | 3 tester |
| P5 | toppbildet i README-en uten «Toppen av oversikten» i alt-teksten | 1 test |

**Edge i en iframe**, 05.11 kl. 16:58, med demobasen i en midlertidig mappe, på svar 1, 3 og 4: 10 visninger × 10 bredder (1280, 1100, 1079, 900, 761, 760, 600, 390, 360 og 320 px), de samme som før. Ingen synlig tekst utenfor ruta, ingen synlig tekst utenfor vinduet og ingen vannrett rulling i noen av de 100. Måleren regner ikke tekst i en boks som ruller selv (tabellene på smal skjerm), og regner tekst som en boks med `overflow: hidden` kutter, som kuttet («Industri» og «Konsum» ved 320 px). Bunnen av siste rad under «Skilte seg ut» er fortsatt 1864 px, og bunnen av `p.dagene` 2198 px.

**Bildene** før (`2e48eb0f`) og etter (`42088949`) står på `pr-8-2b-bilder` i `77a0c0fa`, med navn som begynner på `svar-1429-`: børsometeret ved 1280 px siste børsdag og 18.09, børsometeret ved 390 px (likt før og etter, svar 2), og oversikten ved 1280 og 390 px. Bare demoen, ingen ekte kurser.

## Gjennomgangen av svarene 05.11 kl. 14:29

På diffen `665b3642..952e44dc`, etter hele settet, med Blind Hunter (BH, 12 funn), Edge Case Hunter (ECH, 2) og Verification Gap (VG, 9), hver for seg. Ingen funn står på høy. Rettingene står i `1be0676a`. Hele settet før den: 4072 bestått, 24 hoppet over og 2 porttester for `start.ps1` som feilet. Mutanten P6 (symbolet med `HALVFET_EM` i `stor_bredde`) ble fanget av 4 tester, og fila var lik HEAD etter. De 100 målingene i Edge ble gjort på nytt kl. 17:31 uten avvik, og de sju bildene i `docs/appen/` er byte for byte de samme.

| Funn | Alvorlighet | Hva | Avgjort |
|---|---|---|---|
| ECH1 | middels | Symbolet ble regnet med 0,62 em, men store bokstaver i 22 px halvfett er bredere | Rettet: målt i Edge med en Range til opptil 0,721 em (MOWI) for de 15 aksjene og demoen, og regnet med `STORSYMBOL_EM` = 0,75. `STOR` er (207, 107). HVDO og BRFE trenger 166,4 px og er fortsatt store. Styrken målt til 0,462 em, under de 0,5 som regnes. |
| BH1, VG7 | middels, lav | Testen for nivået regnet fasiten med `_stor_bredde` | Rettet: `_bredden` i `test_boersometer.py` med tallene skrevet ut |
| BH2 | middels | Raden «Klar» mistet at dagen aldri får signal uten bonuskvote | Rettet: «ellers får dagen aldri signal». `docs/hjelp.md` sier det samme. |
| VG1 | middels | Ingen test krevde `navn-bredest` på en stor rute | Rettet: HVDO, BRFE og KVST |
| VG2 | middels | Ringen og skriften i `stor_bredde` var ikke testet mot stilen | Rettet: `PILLELUFT`, `PILLEKANT`, `HALVFET_EM` og skriften for styrken mot `stil.css` |
| BH3 | lav | `stor=True` som standard i `_nivaa_ved` | Avvist: bare `kart()` regner klassene, og testene kaller `_nivaa_ved` for én rute uten klasse |
| BH4 | lav | «None av 3» | Avvist: `uten_styrke` er «ikke vurdert» når styrken mangler og ruta har data |
| BH5 | lav | Testen for den bredeste brukte «Uten data» med «ikke vurdert» | Rettet |
| BH6 | lav | Kommentaren i `stil.css` sa `STOR` | Rettet |
| BH7, ECH2 (stilen) | lav | Stilen for nivå 4 i `bred`, `smal` og `smalest` brukes ikke | Står: den er lik for alle klassene og testet, så den virker hvis `STORE_KLASSER` utvides |
| ECH2 (hjelpen) | lav | Hjelpen sa ikke at store ruter bare finnes fra 1079 px | Rettet i hjelpen og `docs/hjelp.md` |
| BH8 | lav | Kommentaren sto over feil linje | Rettet |
| BH9 | lav | `velg` uten dag | Avvist: `les_valg` gir `siste` da (ECH), og lenken sier «dagen» |
| BH10 | lav | Min liste kunne bruke en annen mal | Avvist: `/min-liste` bruker `index.html` (malene i `app.py` er `index.html`, `boersometer.html` og `basefeil.html`) |
| BH11 | lav | Feilmeldingen for bildene ved 390 px ga fremgangsmåten som kuttet bildet | Rettet: iframen og `--virtual-time-budget` |
| BH12 | lav | `Kartrute.navn` er tom som standard | Står: bare `kart()` lager ruter til siden, og uten klassen står ruta uten navn, ikke med tekst oppå hverandre |
| VG3 | lav | `MERKET` ikke bundet til malen | Rettet: `test_merket_er_det_malen_skriver` |
| VG4 | lav | Ikke alle periodene i testen for lenken | Rettet |
| VG5 | lav | Hjelpen testes ikke mot oppførselen | Står, som for de andre svarene: hjelpen har kildene sine i `hjelpetekster.py` |
| VG6 | lav | `STOR[0]` brukes ikke i koden | Står: den er testet som øvre grense i `test_stor_den_bredeste_er_stor_bredde` |
| VG8 | lav | Antallet underpunkter og lengden på «Klar» testes ikke | Står: strukturen og lenkene er testet, og innholdet er gruppens |
| VG9 | lav | Avtrykket for oversikten har ikke `app.py` | Står: arvet fra `SKJERMBILDET` (3.3e), ikke en del av svarene |

Ingen funn på middels eller over står åpne, og ingen følger av et svar.

