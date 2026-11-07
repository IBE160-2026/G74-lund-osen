---
title: 'Story 3.4h: Investorsidene i demoen, og boblen nederst på aksjesiden'
type: 'feature'
created: '2026-11-07'
status: 'draft'
route: 'dispatch'
baseline_commit: 'a8a4e725'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/bilder/investorsider/LESMEG.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
  - '{project-root}/docs/skisser/2026-11-06/LESMEG.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-5-investorsiden.md'
---

*Svar 2026-11-07 kl. 10:33 (gruppens svar):* forslagene i spørsmål 1–10 under er godtatt, og teksten nederst på investorsiden blir «Oppdiktet selskap i demoen. I den ekte versjonen åpner lenken på aksjesiden selskapets egen investorside i en ny fane.», fordi kortet ble en boble 07.11 kl. 08:57. Rådet anbefalte begge. Svaret står også under story 3.4h i `epics.md`, ført etter instruksjonen kl. 10:38 i `docs/ai-prompts/2026-11-07.md`.

Utkast, skrevet 07.11 i instruksjonen kl. 09:45 (`docs/ai-prompts/2026-11-07.md`). Ingenting bygges før gruppen har svart på spørsmålene under (regel 9).

## Spørsmål til gruppen før noe bygges

Hvert spørsmål har et forslag. Forslaget er det utkastet under bygger på, til gruppen har svart.

1. **Hvilken adresse har investorsiden i demoen?** *Forslag:* `/investorside/‹symbol›`, for eksempel `/investorside/BRFE`. Ruta finnes bare i demoen. I den ekte versjonen svarer den 404, fordi selskapene der har egne sider.
2. **Hvor ligger tegningene appen viser?** Docker kopierer bare `src/` (`COPY src/ src/` i `Dockerfile`), så appen kan ikke lese `docs/bilder/investorsider/`. *Forslag:* de 15 SVG-ene og `bobler.json` kopieres urørt til en ny mappe, `src/static/investorsider/`, og en test krever at de er byte for byte lik filene i `docs/bilder/investorsider/`. Mappa i `docs/` står som den godkjente kilden.
3. **Hva står i boblen i den ekte versjonen når aksjen ikke har adresse?** I dag står setningen uten lenke (gjennomgangen av 10.5, ECH5). *Forslag:* ingen boble. En boble som ikke kan klikkes, ser ut som en feil.
4. **Hva står i boblen?** *Forslag:* som skissen `investorsiden-i-demoen.png`: «Investorsiden til ‹navn›» med pil ↗ i den ekte versjonen, som åpnes i en ny fane (svaret 24.10 kl. 11:48), og uten pil i demoen, i samme fane (svaret 06.11 kl. 23:51). NewsWeb nevnes ikke (svarene 06.11 kl. 22:16 og 22:23), og ingen logo (svaret 07.11 kl. 08:57).
5. **Har MTFJ, demoselskapet uten kurser, også boblen?** Aksjesiden for MTFJ svarer 200 med en beskjed om at det ikke finnes kurser ennå (U3). *Forslag:* ja, nederst på siden, fordi investorsiden finnes og slagordet «404: Varene ble ikke funnet.» er laget for den.
6. **Hvilken tekst er `alt` for tegningen?** `LESMEG.md` gir to valg. *Forslag:* teksten i `<desc>` i SVG-en, fordi tegningen viser mer enn slagordet. Slagordet står som vanlig tekst i boblen, og halen har `aria-hidden="true"`.
7. **Tegningen inline eller som `<img>`?** *Forslag:* `<img>` med `src="/static/investorsider/‹symbol›.svg"`, så SVG-en vises urørt, og boblen og halen i HTML og en liten SVG over, plassert etter `bobler.json`. Ingen skript.
8. **Skriftene: hele filer eller bare tegnene i navnene?** De nye er Inter Display, Lora og Liberation Mono, i ti snitt (del D). *Forslag:* hele `.woff`-filer, som IBM Plex Sans og Newsreader i dag, uten å kutte tegn. Å kutte er å lage en endret versjon, og det vil vi ikke måtte vurdere mot lisensen.
9. **Skal investorsiden ha stripa øverst?** *Forslag:* ja, siden bruker `_ramme.html`, så «Eksempeltall» og knappene står som på de andre sidene, og ingen knapp er fylt, som på aksjesiden.
10. **Rekkefølgen.** *Forslag:* etter 10.9 og 8.20a (spørsmål 21 i `spec-8-20-ux-rettingene-etter-gjennomgangen-06-11.md`), fordi boblen står under «Signalet dag for dag», som 8.20 flytter. Én PR.

## Intent

**Problem:** lenken til investorsiden er utydelig (U84 i `docs/ux-logg.md`). Den er en fotnote nederst som nevner NewsWeb, og i demoen en tekst om at selskapet er oppdiktet, så faglærer og sensor ser aldri hva lenken gjør.

**Avgjørelsene** (under story 3.4h i `epics.md`):
- *24.10 kl. 11:48:* alle lenker ut av appen åpnes i en ny fane.
- *24.10 kl. 11:58, 12:01, 12:37, 12:39, 12:51, 13:02 og 13:03:* en egen side i appen i demoen, med logo og tegning laget av KI, bransjesymbolet i logoen, ulike skrifter, tegneseriestrek, ikke vannmerke, «Illustrasjon laget av KI» under tegningen, boblen nær den som snakker, tegningen på samme sted på alle sidene, lenken tilbake øverst, og navnene aldri med små bokstaver.
- *24.10 kl. 13:43:* de 15 tegningene i `docs/bilder/investorsider/` er godkjent.
- *06.11 kl. 23:51:* sidene bygges i demoen, og lenken nederst på aksjesiden går dit, i samme fane og uten pil.
- *07.11 kl. 08:57:* lenken er boblen nederst på aksjesiden i begge versjonene, og logoen står bare på demosiden. Det erstatter kortet «Mer om ‹navn›» fra 24.10 kl. 15:21.

## Slått opp 07.11 på `a8a4e725` (regel 3)

- **De 15 i demoen** (`DEMOUNIVERS` i `src/demo.py`) er de samme symbolene, navnene og bransjene som tabellen i `docs/bilder/investorsider/LESMEG.md`. MTFJ har ingen kurser med vilje (U3).
- **`docs/bilder/investorsider/`:** `svg/` med 15 filer (`viewBox="0 0 420 300"`, med `<title>` og `<desc>`), `forhandsvisning/` med 15 PNG-er, og `bobler.json` med boblen, tuppen og halen per selskap, i piksler fra tegningens øvre venstre hjørne, for en tegning på 560 × 400 px i et felt på 896 px.
- **Lenken i dag** (`aksje.html`, story 10.5): en fotnote med klassen `investorside`. I demoen en tekst om at selskapet er oppdiktet. I den ekte versjonen en lenke med `rel="noreferrer"`, uten `target`, eller setningen uten lenke når adressen mangler. Adressene står i `INVESTORSIDER` i `src/kursdata.py`.
- **Skriftene i dag:** `src/static/fonts/ibm-plex-sans/` (Regular, Medium, SemiBold, Bold) og `src/static/fonts/newsreader/` (16pt Medium og SemiBold, 72pt Medium), hver med `OFL.txt`. Raden for tegningene i `docs/kilder-og-rettigheter.md` sier at Inter Display, Lora og Liberation Mono ikke ligger i repoet.
- **Bransjesymbolet:** makroen `bransjesymbol` i `src/templates/_bransjer.html`.
- **Lenken tilbake:** `a.tilbake` i `aksje.html` og `src/static/stil.css`.
- **Bildene:** `.woff` er i `SKRIFTFILER` i `tests/test_docker.py`, og alle filene i `src/static/` med de endelsene er med i avtrykket bak bildene i `docs/appen/`.

## Delene

### A) Siden for hvert av de 15 selskapene

Etter oppsettet i `docs/bilder/investorsider/LESMEG.md`, ovenfra:
1. Lenken «Tilbake til ‹navn›» til aksjesiden, med `a.tilbake`.
2. Logoen: sirkel 116 px, 4 px kant i Blekk, gul ring innenfor (`--oransje`, `#F2B53A`), bransjesymbolet øverst og symbolet under, i selskapets skrift.
3. Navnet, 50 px i selskapets skrift, og under det bransjesymbolet og «‹Bransje› · Demo Børs».
4. Tegningen, 560 × 400 px, rett under overskriften og venstrejustert, på samme sted på alle sidene. Full bredde på smal skjerm.
5. Boblen med slagordet, plassert etter `bobler.json` (del C).
6. «Illustrasjon laget av KI» rett under tegningen.
7. Nederst: «Oppdiktet selskap i demoen. I den ekte versjonen åpner knappen selskapets egen investorside i en ny fane.»

Ikke vannmerke. Navnet har stor forbokstav, også der skriften viser det med store bokstaver. Siden har ingen kurs, ingen endring og ingen tekst om kjøp eller salg (NFR-06).

**Ville feilet hvis:** en av de 15 manglet en side, et navn sto med små bokstaver i HTML-en, eller tegningen sto et annet sted på én av sidene enn på de andre. Testen går gjennom alle 15 med demobasen.

### B) Ruta og malen

Ruta `/investorside/<symbol>` i `src/app.py` (spørsmål 1), og en ny mal, `src/templates/investorside.html`, som bruker `_ramme.html` (spørsmål 9). Et symbol som ikke er blant de 15, gir 404. I den ekte versjonen gir ruta 404 for alle. Slagordet, skriften og plassen til boblen leses fra `src/static/investorsider/bobler.json` og en tabell i koden med skriften per selskap, fra `LESMEG.md`. Ingenting hentes fra nettet (AD-2).

**Ville feilet hvis:** ruta svarte 200 i den ekte versjonen, eller en ukjent ticker ga en side.

### C) Boblen og halen på investorsiden

Hvit, 3,5 px kant i Blekk, runde hjørner 22 px, IBM Plex Sans 600, 22 px, linjehøyde 1,25 og innvendig avstand 14 × 18 px, som `bobler.json` sier. Boblen og halen er plassert i prosent av tegningen, så de følger den når den skaleres. Halen går ut fra kanten nærmest den som snakker, og den hvite flaten dekker kanten der. På smal skjerm står boblen under tegningen, uten hale. Slagordet er vanlig tekst.

**Ville feilet hvis:** boblen dekket overskriften, KI-merket eller teksten nederst ved 1280 px, eller slagordet bare fantes i en SVG. Testen i nettleseren måler rektanglene, som `tests/test_kursgrafen_smal.py` gjør.

### D) Skriftene og lisensene

De nye snittene, etter tabellen i `LESMEG.md`:
- **Inter Display:** 200, 700, 800 kursiv og 900.
- **Lora:** 400, 500, 600 kursiv og 700. Kapitélene for FJSB lages med `font-variant: small-caps`.
- **Liberation Mono:** 400 og 700.

IBM Plex Sans 400, 500 og 600, Newsreader 16pt 600 og Newsreader 72pt 500 finnes. Filene legges i tre nye mapper, `src/static/fonts/inter-display/`, `src/static/fonts/lora/` og `src/static/fonts/liberation-mono/`, hver med lisensfila fra kilden, lest før den committes (regel 11). `docs/kilder-og-rettigheter.md` får en rad per skrift med kilden, versjonen og lisensen, og raden for tegningene får en datert linje om at de tre nå ligger i repoet. `@font-face` står i `stil.css` som for de to andre, og skriftene lastes bare på investorsidene.

**Ville feilet hvis:** en skrift manglet lisensfil eller rad i kildene, eller siden lastet en skrift fra nettet. `TestBildeneAvAppen::test_avtrykket_dekker_modulene_appen_og_demoen_importerer` i `tests/test_docker.py` står.

### E) Boblen nederst på aksjesiden, i begge versjonene

Som skissen `investorsiden-i-demoen.png`, etter svaret 07.11 kl. 08:57 og spørsmål 3–5:
- **Demoen:** «Investorsiden til ‹navn›», uten pil, til `/investorside/‹symbol›` i samme fane.
- **Den ekte versjonen:** «Investorsiden til ‹navn› ↗», til adressen i `INVESTORSIDER`, med `target="_blank"` og `rel="noreferrer"`. Pila har `aria-hidden="true"`, og den skjulte teksten sier «åpnes i en ny fane».
- **Uten adresse:** ingen boble.
- Ingen logo, og NewsWeb nevnes ikke. Fotnoten med klassen `investorside` går ut.
- Boblen står nederst, under «Signalet dag for dag» (skissen `aksjesiden-ki-paa.png`).

Det endrer beslutningen 06.10 under story 10.5, der aksjedetaljen nevner NewsWeb uten lenke. 10.9 slo fast det samme (svarene 06.11 kl. 22:16 og 22:23), og `spec-10-5-investorsiden.md` får en datert linje.

**Ville feilet hvis:** boblen i den ekte versjonen åpnet i samme fane, boblen i demoen hadde pil eller ny fane, eller «NewsWeb» sto på aksjesiden. `test_demoen_viser_teksten_og_ingen_lenke`, `test_lenken_paa_siden_gaar_til_aksjen_siden_viser` og `test_en_ekte_aksje_uten_adresse_faar_setningen_uten_lenke` i `tests/test_investorsiden.py` skrives om etter dette. `test_ingen_side_som_vises_lenker_til_euronext`, `test_ingen_demoside_lenker_til_euronext` og `test_ingen_kode_i_src_kaller_adressene` står.

### F) 390 px uten vannrett rulling

Investorsiden og aksjesiden med boblen ved 390 og 320 px: tegningen i full bredde, boblen under tegningen, logoen og navnet under hverandre når de ikke får plass, og boblen på aksjesiden bryter teksten i stedet for å gå ut av siden.

**Ville feilet hvis:** `scrollWidth` var større enn `clientWidth` på en av de 15 sidene ved 390 px, som testen i `tests/test_kursgrafen_smal.py` måler, eller boblen sto over tegningen på smal skjerm. Testen kjører i Edge eller Chrome og feiler i CI når nettleseren mangler, som `tests/test_hjelpefeltet.py`.

### G) Testene, og det som rettes i samme PR

- **Nye tester** i en ny fil for 3.4h: alle 15 sidene svarer 200 i demoen og 404 i den ekte versjonen; kopiene i `src/static/investorsider/` er byte for byte lik `docs/bilder/investorsider/`; «Illustrasjon laget av KI» og teksten nederst står på hver side; ingen side har kurs, prosent eller ord om kjøp eller salg; boblen i begge versjonene (del E); 390 px (del F).
- **Bildene i `docs/appen/`:** de nye skriftene i `src/static/` endrer avtrykket bak alle sju, og aksjesiden endres av boblen. Alle tas på nytt, og avtrykkene settes med en kommentar som før. `TestAksjesidebildet::test_bildet_tas_paa_nytt_naar_aksjesiden_endres` og `TestBildeneAvAppen::test_de_nye_bildene_tas_paa_nytt_naar_siden_endres` feiler til det er gjort.
- **Hjelpen og README-en:** `docs/hjelp.md` får et svar om investorsiden i demoen, og README-en sier i «Demoen» at lenken går til en side i appen (regel 19). «Mappestruktur» endres ikke, fordi den ikke nevner `src/static/`.
- **U84** i `docs/ux-logg.md` får en datert linje når PR-en er flettet.

**Ville feilet hvis:** en kopi i `src/static/investorsider/` var endret i forhold til den godkjente fila, eller en av de 15 manglet. Da viser appen noe gruppen ikke har godkjent.

## Grenser

- Ingen kall til EODHD utover kvotesjekken i regel 15, og ingen kall til adressene i `INVESTORSIDER` (AD-2). `data/db/ose.db` røres ikke (regel 22). Demobaser bare i midlertidige mapper.
- Tegningene og `bobler.json` i `docs/bilder/investorsider/` endres ikke. De er godkjent 24.10 kl. 13:43.
- Skriftene lastes ned fra kildene de er utgitt fra, med lisensen lest før commit. Ingen skrift fra nettet når appen kjører.
- Bygges på egen gren og flettes bare ferdig og grønn.
- En mutant per del, med kopi før og sha256 mot HEAD etter.

## 3.4h, bygget 07.11

*Lagt til 2026-11-07, etter instruksjonene kl. 20:17 og 20:57 i `docs/ai-prompts/2026-11-07.md`:* 3.4h er bygget på grenen `3-4h-investorsidene-i-demoen`, med svaret kl. 10:33 (forslagene i spørsmål 1–10). De nye testene står i `tests/test_investorsidene_demo.py`. Testene for fotnoten fra 10.5 er skrevet om i `tests/test_investorsiden.py`, `tests/test_historikken.py` og `tests/test_funnene_8_2b.py`, og `tests/test_utseende.py` og `tests/test_docker.py` kjenner den nye siden, skriftene og avtrykkene.

- **A, siden for hvert av de 15:** lenken tilbake, logoen, navnet i selskapets skrift, bransjen med «Demo Børs», tegningen 560 × 400 px, boblen, «Illustrasjon laget av KI» og teksten nederst fra svaret kl. 10:33. **Ville feilet hvis** en av de 15 manglet en side, lenken tilbake, KI-merket eller teksten nederst (`test_hvert_av_de_15_har_sin_side_i_demoen`, `test_ingen_kurs_prosent_eller_kjoep_og_salg`).
- **B, ruta og malen:** `/investorside/<symbol>` i `src/app.py`, `src/templates/investorside.html` og `src/investorsider.py`, med skriften per selskap i `SKRIFTER` etter tabellen i `LESMEG.md`. **Ville feilet hvis** ruta svarte 200 i den ekte versjonen eller for en ukjent ticker, eller skriften var en annen enn i `LESMEG.md` (`test_ruta_svarer_404_i_den_ekte_versjonen`, `test_en_ukjent_ticker_gir_ingen_side`, `test_skriften_er_den_i_lesmeg`).
- **C, boblen og halen:** plassen fra `bobler.json` i prosent av tegningen, og halen som en SVG med `aria-hidden="true"`. **Ville feilet hvis** slagordet bare fantes i en SVG, plassen ikke kom fra `bobler.json`, eller boblen dekket overskriften, KI-merket eller teksten nederst ved 1280 px, målt i Edge (`test_slagordet_er_vanlig_tekst_og_halen_pynt`, `test_boblen_ved_1280_px`).
- **D, skriftene:** se under. **Ville feilet hvis** en skrift manglet lisensfil, rad i kildene eller `@font-face`, en WOFF-fil hadde metadata, en privat blokk eller en tabell som ikke stemte med sjekksummen, eller et snitt i `LESMEG.md` manglet (`test_hver_skrift_har_lisensen_raden_og_font_face`, `test_skriften_er_bare_komprimert`, `test_hvert_snitt_i_lesmeg_finnes_i_appen`).
- **E, boblen nederst på aksjesiden:** makroen i `src/templates/_investorboble.html`, under «Signalet dag for dag» i `aksje.html` og nederst i `aksje_uten_kurser.html` (spørsmål 5). Fotnoten med klassen `investorside` er borte, og NewsWeb nevnes ikke på aksjesiden. **Ville feilet hvis** boblen i demoen hadde pil eller ny fane, boblen i den ekte versjonen åpnet i samme fane, en aksje uten adresse fikk en boble, eller «NewsWeb» sto på aksjesiden (`test_boblen_i_demoen`, `test_boblen_i_den_ekte_versjonen`, `test_uten_adresse_ingen_boble`).
- **F, 390 og 320 px:** tegningen i full bredde og boblen under KI-merket, uten hale. **Ville feilet hvis** en av de 15 sidene eller boblen på aksjesiden med det lengste navnet rullet vannrett, målt i Edge (`test_smal_skjerm_uten_vannrett_rulling`, `test_boblen_paa_aksjesiden_ved_smal_skjerm`).
- **G:** kopiene i `src/static/investorsider/` (`test_kopiene_er_byte_for_byte_de_godkjente`), `docs/hjelp.md` og steg 6 i «Demoen» i README-en (`test_hjelpen_sier_det_samme_som_sidene`). Bare `aksjesiden-brfe-demo.png` i `docs/appen/` er endret, 2258 px høyt (var 2300), fordi fotnoten mellom grafen og rammen er borte. De seks andre er byte for byte de samme, og avtrykkene i `tests/test_docker.py` er satt på nytt med en kommentar. U84 i `docs/ux-logg.md` får en datert linje når PR-en er flettet.

**Skriftene.** Hele filer, pakket til WOFF 1.0 med bare zlib per tabell, uten WOFF-metadata og uten privat blokk (OFL-FAQ 2.2.1, lest 07.11). Kontrollert 07.11 i instruksjonen kl. 20:57, før settet ble kjørt: hver tabell i hver av de ti filene er byte for byte lik tabellen i TTF-fila i arkivet, og sha256 for arkivene er den i `docs/kilder-og-rettigheter.md`.
- Inter Display 200, 700, 800 kursiv og 900: Inter 4.1, `Inter-4.1.zip` fra utgivelsen v4.1 hos rsms/inter, `extras/ttf/`. Lisensen er OFL 1.1, `LICENSE.txt` i zip-fila, uten reserverte navn.
- Lora 400, 500, 600 kursiv og 700: Lora 3.021, `Lora.zip` fra utgivelsen v3.021 hos cyrealtype/Lora-Cyrillic, `ttf/`. Lisensen er OFL 1.1, `OFL.txt` lagt ved samme utgivelse, med det reserverte navnet «Lora».
- Liberation Mono 400 og 700: Liberation 2.1.5, `liberation-fonts-ttf-2.1.5.tar.gz`, lenket fra utgivelsen 2.1.5 hos liberationfonts. Lisensen er OFL 1.1, `LICENSE` i arkivet, med de reserverte navnene «Liberation», «Arimo», «Tinos» og «Cousine».

**Testene og mutantene.** Kjøringen kl. 20:43 ga 19 feilet: 17 fordi ruff og git ikke startet da minnet var nesten brukt opp (0xC0000142), og 2 som ventet fotnoten og ble rettet (stoppen kl. 20:53 i dagsfila). Hele settet ble kjørt alene på nytt før `ac0944f9`, 21:03:09–21:15:01 med 3,9 GB ledig av 15,7 GB: 4568 bestått, 24 hoppet over og 0 feilet. Én mutant per del på `ac0944f9`, med kopi før og sha256 mot HEAD etter: A (KI-merket), B (ruta i den ekte versjonen), C (toppen av boblen regnet mot bredden), D (vekten til Lora 700 i `@font-face`), E (ny fane i demoen), F (tegningen 560 px på smal skjerm) og G (en endret kopi av `brfe.svg`). Alle ble fanget, og hver fil var lik HEAD etterpå (med LF, som git lagrer den).
