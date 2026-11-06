---
title: 'Story 8.2c: kursgrafen på smal skjerm'
type: 'feature'
created: '2026-11-06'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: 'abf65895'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-2b-funnene-fra-ux-loggen.md'
---

## Intent

**Problem:** spørsmål 8 i `spec-8-2b-funnene-fra-ux-loggen.md` (fra gjennomgangen 04.11, ECH6): feltet til høyre for navnene er 170 av 720 i grafen, og hele grafen skaleres ned på smal skjerm, så teksten i den blir om lag 5 px. Grafen er én SVG med `viewBox="0 0 720 260"` og `width: 100%` (`src/graf.py`, `aksje.html`, `stil.css`).

**Beslutningen:** svaret 4.11 kl. 09:48 gjorde dette til story 8.2c, ekstra. Svaret 6.11 kl. 15:08 (under story 8.2c i `epics.md`): bygges nå på egen gren og flettes før kl. 21:20 hvis alt er grønt og ingen funn på middels eller over står åpne.

**Kravet** (instruksjonen kl. 15:10 i dagsfila 06.11): kursgrafen får egne mål på smal skjerm, så teksten i den ved 390 px er minst like stor som den minste teksten ellers på siden, uten vannrett rulling. Den viser de samme dataene, linjene og merkene som den brede grafen; må noe utelates fordi det ikke får plass, står det og grunnen her. Brede vinduer er som før, og bildene ved 1280 px er byte for byte de samme.

## Målt før endringen

I Edge, på main (`abf65895`), aksjesiden for BRFE i demoen, i en iframe med nøyaktig bredde, demobasen i en midlertidig mappe. Tekststørrelsen i grafen er skriftstørrelsen ganger bredden på SVG-en delt på 720. Den minste teksten ellers på siden er 11,5 px (`.skala .grense` og `.gir-null` i sjekkortene).

| Vindu | 1280 | 1100 | 1079 | 900 | 761 | 760 | 600 | 390 | 360 | 320 |
|---|---|---|---|---|---|---|---|---|---|---|
| SVG-en, px | 962 | 962 | 962 | 822 | 683 | 682 | 522 | 312 | 282 | 242 |
| Teksten i grafen, px | 16,03 | 16,03 | 16,03 | 13,7 | 11,38 | 11,37 | 8,7 | 5,2 | 4,7 | 4,03 |

Det samme for siste børsdag, en annen dag (01.10) og 1 uke. Ingen tekst utenfor grafen og ingen vannrett rulling i noen av de 30.

## Approach

**1) Grafen regnes med egne mål på smal skjerm (`src/graf.py`).** `bygg_graf(..., smal=True)` gir en graf på 280 × 250 (`SMAL_BREDDE`, `SMAL_HOYDE`) av de samme punktene, med den samme skalaen, det samme rutenettet, de samme strekene på aksen, punktet ved enden og dagen som er merket. Feltet til venstre for tallene (44) er som før. Feltet til høyre er 8 (`SMAL_HOEYRE`), bare plass til punktet ved enden.

- **Navnene på linjene** står i en forklaring under datoene (`FORKLARING`, 52), én linje per navn med et stykke av linja det hører til, i samme farge og strek. *Grunnen:* i feltet til høyre ville det lengste navnet, «50-dagers snitt (sjekk 1)», tatt over halve flaten. Navnene er de samme, og bare linjer som er tegnet, får navn.
- **Navn på aksen** som ville kommet borti hverandre, mister navnet, men ikke streken (`_uten_overlapp`). Plassen regnes med 7 per tegn (`TEGNBREDDE`) og 4 mellom navnene, fra høyre, så det siste navnet, nærmest dagen grafen slutter på, alltid står. *Grunnen:* på 228 i bredden får ikke alle månedsnavnene eller datoene plass. Ved 6 mnd for BRFE står mai, juni, juli og oktober, og august og september har bare streken. Dette er det eneste som utelates.
- Den brede grafen regnes som før. Alle 135 aksjesidene i demoen (15 aksjer, siste børsdag, to andre dager og seks perioder) ga byte for byte samme HTML før og etter.

*Utfallet:* `8bfc9885`. `TestSmalSkjerm` i `tests/test_graf.py` har fem tester med «Ville feilet hvis» (de samme punktene, linjene, skalaen, rutenettet og strekene som den brede; ingen linje i feltene; dagen som er merket; navnene i forklaringen; navnene på aksen uten overlapp for 1 uke, 1 mnd, 3 mnd, 6 mnd, I år og 1 år, med det siste navnet beholdt). Bildene i `docs/appen/` ble tatt på nytt og er byte for byte de samme, så bare avtrykkene i `test_docker.py` er satt.

**2) Siden viser den smale grafen på smal skjerm (`app.py`, `aksje.html`, `stil.css`).** `app.py` gir malen også `graf_smal`, og malen tegner den samme SVG-en for begge i en løkke, med `class="graf smal"` på den smale og forklaringen nederst. Stilarket gjør figuren til en container og viser den smale i stedet for den brede når figuren er smalere enn 690 px. *Grensen:* der blir teksten på 12 i den brede 12 × 690 / 720 = 11,5 px, den minste teksten ellers. Den smale er høyst 4/3 av 280 bred, midtstilt, så teksten i den ikke blir større enn 16 px, som i den brede ved 1280 px. Den skjulte grafen har `display: none`, så skjermleseren leser bare den som vises. Etiketten er den samme.

*Valget gruppen kan se på:* mellom 690 og 373 px i figuren, altså et vindu på om lag 451–767 px, er den smale grafen 373 px bred og midtstilt, med luft på sidene. Alternativet var å la den brede stå der, med tekst under 11,5 px.

*Utfallet:* `ccbbe0df`. `tests/test_kursgrafen_smal.py` sjekker at den smale grafen har de samme linjene, merkene, tallene, punktet og navnene som den brede, at navnene står under datoene med et stykke av linja, at stilarket viser den smale under 690 px, og i Edge ved 1280, 390 og 320 px hvilken graf som vises, at ingen tekst står utenfor grafen eller oppå en annen, at siden ikke ruller vannrett, og ved 390 px at teksten i grafen er minst like stor som den minste teksten ellers. To tester i `test_app.py` (`test_maanedsmerkene_staar_i_grafen` og `test_merkene_paa_aksen_passer_perioden`) leser nå bare den brede grafen, fordi de gjelder den. Den første kjøringen av hele settet feilet i dem og i `test_velgere_med_ulik_kropp_er_avgrenset_til_hver_sin_side`, som krever én regel for `figure` på aksjesiden, fordi endringene ikke var ferdige. *Lagt til etter gjennomgangen (BH13):* de sju var `TestStory80c::test_maanedsmerkene_staar_i_grafen`, `TestPeriodeneIKursgrafen::test_merkene_paa_aksen_passer_perioden` for 1 uke, 1 mnd, 6 mnd, 1 år og I år, og `TestStilarket::test_velgere_med_ulik_kropp_er_avgrenset_til_hver_sin_side`. De fire andre var porttester for `start.ps1`. `container-type` står nå i regelen for `figure`, og settet ble kjørt på nytt (svaret 4.11 kl. 09:48). Alle sju bildene i `docs/appen/` ble tatt på nytt og er byte for byte de samme.

**3) Hjelpen.** «?» ved «Kursutvikling» sier nå at navnene står til høyre, ved enden av linjene, og på smal skjerm under grafen (`hjelpetekster.py`). `docs/hjelp.md` nevner ikke hvor navnene står, og README-en sier ingenting om grafen på smal skjerm, så de er ikke endret.

## Målt etter endringen

Som før, på `ccbbe0df`, for siste børsdag, en annen dag (01.10) og 1 uke:

| Vindu | 1280 | 1100 | 1079 | 900 | 761 | 760 | 600 | 390 | 360 | 320 |
|---|---|---|---|---|---|---|---|---|---|---|
| Grafen | bred | bred | bred | bred | smal | smal | smal | smal | smal | smal |
| SVG-en, px | 962 | 962 | 962 | 822 | 373,3 | 373,3 | 373,3 | 312 | 282 | 242 |
| Teksten i grafen, px | 16,03 | 16,03 | 16,03 | 13,7 | 16 | 16 | 16 | 13,37 | 12,09 | 10,37 |

Ingen tekst utenfor grafen, ingen tekst i grafen oppå en annen og ingen vannrett rulling i noen av de 30. Den minste teksten ellers er 11,5 px. Ved 320 px er teksten i grafen 10,37 px, under 11,5, men kravet gjelder 390 px. 1 mnd, 3 mnd, 6 mnd, I år og 1 år for BRFE, siste børsdag for VRDS og 1 år for KVST ved 390 og 320 px ga det samme: ingen tekst utenfor, ingen overlapp og ingen rulling.

## Testene

Hele settet alene før hver commit med kode eller tester, i en egen worktree:

- `8bfc9885`: 4231 bestått, 24 hoppet over og 7 porttester for `start.ps1` som feilet (svaret 29.10 kl. 21:02), 8 min 30 s.
- `ccbbe0df`: først 4233 bestått og 11 som feilet, 4 av dem porttester, fordi endringene ikke var ferdige (over). Etter rettingen: 4237 bestått, 24 hoppet over og 7 porttester som feilet, 7 min 39 s.

**Mutantene**, én per commit med kode, med kopi før og sha256 mot HEAD etter (lik HEAD etter alle). Hjelpeteksten og forklaringen er i samme commit som M2 (BH13):

- M1, kl. 15:30:19 på `8bfc9885`: `_uten_overlapp` gir merkene tilbake uendret. Fanget av `test_navnene_paa_aksen_kommer_ikke_borti_hverandre` for 1 uke, 1 mnd, 6 mnd, I år og 1 år.
- M2, kl. 15:55:53 på `ccbbe0df`: grensen i `@container` satt til 1 px, så den smale grafen aldri vises. Fanget av `test_stilarket_viser_den_smale_naar_figuren_er_smal` og `test_teksten_i_grafen_i_nettleseren` ved 390 og 320 px.

## Gjennomgangen

På diffen `abf65895..b4cc5c44`, etter hele settet, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 3), hver for seg. Ingen funn på høy. Rettingene står i `67596cb8`.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | middels | Ved 1 mnd tok `DATOBREDDE` i `_dagmerker` bort datoen nærmest sluttdagen før `_uten_overlapp`, mot påstanden over | Rettet: på smal skjerm tynnes datoene bare i `_uten_overlapp`, fra høyre (`tynn=False`). Testene for 1 mnd til 09.04 og 30.12 |
| BH1, ECH2 | middels, lav | Et siste navn som «september» kunne gå forbi høyre kant, fordi grensen `NAVNEBREDDE` er for den brede grafen | Rettet: et navn som ville gått forbi kanten, står til venstre for streken. Testene for 3 mnd til 23.09 og 6 mnd til 30.11 |
| BH2, VG3 | middels, lav | Nettlesertesten tok bare standardperioden | Rettet: 1 uke, 1 mnd, 1 år og en annen dag (01.10) ved 390 og 320 px |
| BH4 | middels | Testen av navnene på aksen bruker samme anslag som koden, og sjekket ikke feltet med tallene | Rettet: `VENSTRE <= fra`, og den virkelige plassen sjekkes i nettleseren for fire perioder og en annen dag |
| VG1 | middels | Nettlesertesten ble hoppet over i CI uten nettleser | Rettet: samme vakt som `test_hjelpefeltet.py`, så den feiler i CI |
| VG2 | middels | Dagen som er merket, var ikke sjekket i høyden eller på siden | Rettet: punktet ligger på kurslinja innenfor tegneflaten, og dagstreken og dagpunktet står én gang i hver graf ved en valgt dag |
| BH3 | middels | `container-type` på `figure` kunne klippe posisjonerte elementer | Avvist med oppslag: figuren har bare SVG-ene, `figcaption` og tre `span`, ingen posisjonert og ingen hjelpevindu, og alle sju bildene er byte for byte de samme |
| BH5 | lav | Malen krevde `graf_smal` | Rettet: `{% for g in (graf, graf_smal) if g %}` |
| BH6 | lav | Valgene ble skrevet to ganger i `app.py` | Rettet: én ordbok, `grafvalg` |
| BH7, ECH4 | lav | `smal` var utledet av feltet til høyre | Rettet: eget felt i `Graf` |
| BH8, ECH3 | lav | `bredde` og `hoyde` overstyres med `smal` | Rettet: docstringen sier det |
| BH9 | lav | Testen av grensene regnet bare konstanter | Rettet: 690 og 280 regnes av `BREDDE` og `SMAL_BREDDE` |
| BH11 | lav | Plassen til forklaringen var ikke sjekket | Rettet: det lengste navnet, også med tre sifre, og den nederste linja |
| BH13 | lav | Mutantene og den første kjøringen var ikke helt forklart | Rettet over |
| BH10 | lav | Ved 320 px er teksten 10,37 px | Står: kravet gjelder 390 px, og tallet står over |
| BH12 | lav | Forklaringen bruker klassene til linjene | Står: med vilje, så stykket har samme farge og strek. Testene teller `<polyline class=…>` |
| ECH5 | lav | Uten stilark vises begge grafene | Står: stilarket lastes alltid, og uten det vises ingen andre regler på siden heller |

Hele settet før `67596cb8`: 4254 bestått, 24 hoppet over og 3 porttester for `start.ps1` som feilet. Alle sju bildene i `docs/appen/` ble tatt på nytt og er byte for byte de samme, og de 30 målingene og de 14 for de andre periodene ble gjort på nytt, med de samme tallene og ingen avvik.

- M3, kl. 16:13:47 på `67596cb8`: `tynn=True` igjen i `bygg_graf`, som før ECH1. Fanget av `test_navnene_paa_aksen_kommer_ikke_borti_hverandre` for 1 mnd til 09.04 og 30.12.

## Kontroll

- [x] Teksten i grafen ved 390 px er minst like stor som den minste teksten ellers på siden
- [x] Ingen vannrett rulling, og ingen tekst utenfor grafen, ved de ti breddene
- [x] Den smale grafen har de samme dataene, linjene og merkene, og det som utelates, står over med grunnen
- [x] Bildene ved 1280 px er byte for byte de samme
- [x] Tester med «Ville feilet hvis», og én mutant per endring

**Ville feilet hvis:** teksten i grafen var mindre ved 390 px enn i resten av siden.
