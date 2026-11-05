---
title: 'Story 8.2 (8.2b): fire ting som i designforslaget (svarene 04.11 kl. 22:23)'
type: 'feature'
created: '2026-11-05'
status: 'in-review'
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
