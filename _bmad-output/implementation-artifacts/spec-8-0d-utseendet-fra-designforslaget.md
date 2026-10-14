---
title: 'Story 8.0d: Utseendet fra designforslaget'
type: 'feature'
created: '2026-10-14'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '9f8471341e466df1b34e9112882ec02bff710d3e'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-10-13.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0e-oversikten-fra-designforslaget.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sidene bruker systemets skrift, gult banner i demoen og farger som ikke er valgt, og ser ikke ut som designforslaget gruppen valgte (story 8.0d i `epics.md`, med tillegget 13.10).

**Approach:** Tre pull requests. PR 1 (grenen `8-0d-grunnlag`) tar grunnlaget: del 5 i `designregler.md`, skriftfilene, en felles ramme med stripa, fargene, fokus og bunnlinja, demomerket i stripa, feilsiden og hjelpevinduet. PR 2 tar oversikten, med kortet «Slik leser du tabellen». PR 3 tar aksjesiden.

## Planen

Planen ble vist i chatten 13.10 kl. 23:27 (del A–G) og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-13.md`. Kilden er `designutdrag-2026-10-13.md` (sha256 `b2883eb4…e4d6`). Svarene kl. 23:39 og rettelsen kl. 23:43 er beslutninger:

1. **Del A** skrives inn i `designregler.md` som del 5, med dato og grunn, i PR 1, med endringene under.
2. **Avvik 1, 2, 3, 5, 6, 7, 8 og 11** som planen foreslo: ringen og 3 av 3-streken i `#a67c00`, og `#F2B53A` bare på blekk; fokus 3 px i blekk på lys bakgrunn og lys gul i stripa; «2 av 3» med fet skrift og strek, uten fyll og uten gult; snittet i `#9A5A0E`; det grå feltet `#8A847A`; ingen vinkel etter navnet; tabellen ruller i en egen boks ved 390 px; ticker og bransje med symbol under navnet i oversikten.
3. **Gult ved en aksje betyr bare 3 av 3.** Båndet «Skilte seg ut» er en nøytral, varm grå med tekst i blekk, og radene under er hvite. Gult står bare ved 3 av 3: ringen og streken på 4 px til venstre.
4. **Det viktigste i en overskrift har fet skrift**, ikke gul understrek (rettelsen kl. 23:43, `designregler.md` §4 rettet 13.10).
5. **Skriftfilene** hentes én gang med curl fra de offisielle kildene på GitHub (IBM/plex og productiontype/Newsreader). Adressen, versjonen og sha256 står under. WOFF 1.0, og testen bruker bare standardbiblioteket. Ingen ny avhengighet.
6. **Demomerket:** hele «Demoversjon. Eksempeltall: …» står som egen rad i stripa i demoen, med samme ordlyd, i stedet for det gule banneret.
7. **Overskriften på aksjesiden** (PR 3): «<navn> skilte seg ut <ukedag>» når styrken er på terskelen eller over, ellers bare navnet, uten gul understrek. Innledningen fra tavla venter.
8. **Endringen** blir det fjerde nøkkeltallet på aksjesiden, i prosent (PR 3).
9. **Nøytralsonen** tegnes ikke (samlelista punkt 15).
10. **Tre pull requests:** grunnlaget, oversikten og aksjesiden.
11. **Kortet «Slik leser du tabellen»** (gruppen 14.10 kl. 12:15, instruksjonen kl. 14:41) står i PR 2 til høyre for overskriften, innledningen og «3 av 3»-linja, og under dem på smal skjerm, med ramme. Symbolene er `aria-hidden`: en grønn brikke med T +1, de tre retningssymbolene og en musepeker. Teksten fra 8.0e endres ikke. PR 2 får test og mutant for det.

## PR 1: grunnlaget

- Del 5 «Utseendet» i `designregler.md`.
- Skriftfilene i `src/static/fonts/` med OFL-lisensene, og `@font-face` uten noe fra nettet.
- `_ramme.html`: stripa med logoen og «Oppdatert …», fargene som navn i stilen, fokus, bunnlinja, og demomerket som egen rad i stripa. Alle tre sidene bruker rammen.
- Feilsiden og hjelpevinduet i rammen: «?» som svart sirkel på 22 px i en klikkflate på minst 44 px, og vinduet med merket «Hjelp» og tittelen i Newsreader.
- Tabellen, kortet «Slik leser du tabellen» og kortene på aksjesiden endres ikke. README-en endres ikke, med mindre en test krever det.
- **Mutantene:** skrift fra Google Fonts; blekk byttet til en lys farge; `tabular-nums` fjernet fra tallcellene; merket borte fra stripa i demoen; gult fokus på lys bakgrunn; ringen i `#F2B53A`; en lenke til `/min-liste`.

## PR 2: oversikten

Planen ble vist i chatten 14.10 kl. 17:16 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-14.md`. Svarene står i instruksjonen kl. 17:31 og er beslutninger. Resten av planen gjelder som vist.

12. **Fargene som i originalen** (gruppen 14.10 kl. 17:17, og skissen gruppen valgte like etter). Ført med daterte linjer i `designregler.md` §3, §4 og del 5:
    - 3 av 3: strek på 4 px til venstre i raden og ring rundt pillen i sterk oransje `#F2B53A`.
    - 2 av 3: strek på 4 px i lys oransje `#F8DE9C`, og fet «2 av 3» som før.
    - 1 av 3 og 0 av 3: ingen strek og ingen farge.
    - Overskriften: lys oransje markering under «N av M aksjer» (`#F8DE9C` fra 60 % av høyden), uten fet skrift. Aksjesiden får det samme under «skilte seg ut <ukedag>» i PR 3.
    - Båndet «Skilte seg ut»: `#FFF6DC` med kant `#F0E3BD`, og tekst og pille i `#6B4E00`, med «signalstyrke 2 eller mer» etter pillen. «Øvrige aksjer» får «signalstyrke 0 eller 1». Tallene kommer fra Parametre. Radene er hvite.
    - Hvorfor: gruppen vil ha utseendet fra originalen. Teksten sier alltid det samme (FR-103), og pillen har svart fyll siden 8.0e, så ringen og strekene trenger ikke 3:1 mot hvitt. Testen fra 8.0c for ringen og parene for ringen mot hvitt og bakgrunn i PR 1 byttes ut med denne grunnen.
13. **Newsreader 72pt Medium** til de to store overskriftene. SemiBold i 72pt trengs ikke, fordi overskriftene ikke har fet skrift.
14. **Linja under kolonnenavnene:** bare «NOK» under Sluttkurs. «i går» er feil på mandager, og «hva sjekkene peker mot» kan leses som en spådom (NFR-06).
15. **h1:** overskriften med tallene. «Markedsoversikt» uten vurdering. Feilsiden får h1 «Siden kan ikke vises». «OSE Signal» står bare som logo i stripa.
16. **Merket «skiller seg ut»** tas bort fra synet, men står igjen som skjult tekst i cellen, så hver rad sier det med ord.
17. **Tidspunktet** står én gang, som «Oppdatert …» i stripa. «?» med vinduet flyttes dit, og vinduet heter «Oppdatert», som i ordlista (§4).

- Kortet «Slik leser du tabellen» etter beslutning 11, i et rutenett med overskriften og innledningen.
- De små overskriftene i IBM Plex Sans 12,5 px og 700.
- Tabellen i et kort med kolonneraden i blekk. «?» der er hvit med fokus i lys gul, som i stripa.
- Fokusringen rundt sirkelen i «?», ikke rundt klikkflaten på 44 px.
- Ved 390 px ruller tabellen i en egen boks, og siden ruller ikke sidelengs.
- Ticker og bransje med symbol under navnet (avvik 11).
- **Mutantene:** kortet flyttet under tabellen; `aria-hidden` fjernet fra symbolene; musepekeren byttet til en pil; «?» i kolonneraden i blekk; fokus i kolonneraden i blekk; ringen på klikkflaten; `overflow-x` fjernet; sterk oransje ved 2 av 3; strek ved 1 av 3; markeringen borte fra overskriften; «data hentet» tilbake i linja under tittelen; to h1; små overskrifter i Newsreader.

## Boundaries & Constraints

**Always:**
- Ingenting hentes fra nettet av sidene, også feilsiden og demoen.
- Fargene står som navn i stilen, og kontrasten regnes ut av dem i testene.
- Det nye vises også med demobasen (FR-411).
- Grenen bruker bare testbaser (regel 22). Ingen API-kall, ingen nettkall i tester (AD-8).

**Never:**
- Ingen knapp, lenke eller ikon til en side som ikke finnes. Knapperaden kommer med 8.3.
- Ingen nye funksjoner, og ingen endring i signalberegningen, hentingen eller basen.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ekte versjon | Basen med kurser | Stripa med logoen og «Oppdatert …», ingen demomerke | N/A |
| Demo | `OSE_DEMO` og demobasen | Stripa har en rad med hele merket, ingen gult banner | N/A |
| Tom base | Ingen kurser | Stripa uten «Oppdatert …», kommandoen som henter | N/A |
| Feilsiden | Basen kan ikke åpnes | Samme ramme, meldingen i et kort, 503 | N/A |
| Hjelpen | «?» trykkes | Vinduet med merket «Hjelp» og tittelen i Newsreader | N/A |

</frozen-after-approval>

## Code Map

- `src/templates/index.html`, `aksje.html`, `basefeil.html` -- hver med egen `<style>`, gult banner og `font-family: system-ui`. Får `{% extends "_ramme.html" %}`.
- `src/templates/_hjelp.html` -- `hjelpestil()`, `hjelpeknapp()`, `hjelpevindu()`.
- `src/app.py` -- kontekstprosessorene `_eksempeltall` og `_hjelp`, `hentet` i oversikten og aksjesiden, `EKSEMPELTALL_MERKE`, `UNDER_ARBEID_TEKST`.
- `tests/test_app.py` -- `_stil`, `_regel`, kontrasttestene fra 8.0c og 8.0e, `test_veien_tilbake_er_like_tydelig`.
- `tests/test_demo.py` -- merket i demoen, `demobase`.
- `_bmad-output/planning-artifacts/designregler.md` -- ny del 5 nederst.
- Flask serverer `src/static/` fra før (`Flask(__name__)`), og `Dockerfile` kopierer `src/`.

## Tasks & Acceptance

**Execution:**
- [x] `designregler.md` -- del 5 -- reglene før utseendet bygges
- [x] `src/static/fonts/` -- skriftfilene og lisensene -- §1
- [x] `src/templates/_ramme.html` og de tre malene -- rammen, stripa, fargene, fokus, bunnlinja og demomerket -- ett sted for utseendet
- [x] `src/templates/_hjelp.html`, `basefeil.html` -- hjelpevinduet og feilsiden i rammen
- [x] `tests/test_utseende.py` -- kontrasten, ingenting fra nettet, tabelltall, sifrene og `tnum` i filene, merket i stripa, lenkene

**Acceptance Criteria:**
- Given en side, when den vises, then hver farge i testlista har minst 4,5:1 for tekst og 3:1 for streker, ringen og fokus.
- Given demobasen, when en side vises, then hele merket står i stripa og det gule banneret er borte.

## Implementation Notes

**Skriftfilene** (hentet 14.10 kl. 14:42 med curl):

| Fil | Kilde | sha256 |
|---|---|---|
| `ibm-plex-sans/IBMPlexSans-Regular.woff` | `https://github.com/IBM/plex/releases/download/%40ibm/plex-sans%401.1.0/ibm-plex-sans.zip` (utgivelsen `@ibm/plex-sans@1.1.0`, zip-fila sha256 `fb365d910566e6d199cc2c15579a7dd9a267128e18431a394ed81f1970c69200`), `ibm-plex-sans/fonts/complete/woff/` | `b731cf56514a4bd711ab2f9acf641f9311707f4386772eb306d25c2b29b73b1a` |
| `ibm-plex-sans/IBMPlexSans-Medium.woff` | samme | `2b6a04d0f593ad57740e0f51c1bf0b1e3f05f27209c7ca1697a0a72973150f3f` |
| `ibm-plex-sans/IBMPlexSans-SemiBold.woff` | samme | `fff45f420f0d026b4a39f99b3bfc47dfc06561c598c8db825cfce5fd706bda7a` |
| `ibm-plex-sans/IBMPlexSans-Bold.woff` | samme | `5c8bcd6be12df67acd529819b92f36febeff4df059a9603c4ecd578f01cf4062` |
| `ibm-plex-sans/OFL.txt` | samme zip, `ibm-plex-sans/LICENSE.txt` | `7e6b2818edbd8f6a01ae80641cc8f16a51080d08fb4e532be3a0b6f74adb07da` |
| `newsreader/Newsreader16pt-Medium.woff` | `https://raw.githubusercontent.com/productiontype/Newsreader/cfcb4f7af0e52c25e8df2a2431814c8e5fe2e155/fonts/static/woff/Newsreader16pt-Medium.woff` | `96cf08a2b52f931d333e9b7fa979e7d014cedd58a5317a1e0261e43be4609583` |
| `newsreader/Newsreader16pt-SemiBold.woff` | samme commit, `fonts/static/woff/Newsreader16pt-SemiBold.woff` | `db9e22ee61e5dd45ac1e70ad565eedf218666f92991032889aae66a358c347dc` |
| `newsreader/OFL.txt` | samme commit, `OFL.txt` | `fdfad38143ec470553cae82a1e45320bdd1b9ec70415d37bd0171051d8a4ded8` |

*Presisert 2026-10-14:* LICENSE.txt i zip-fila fra IBM har CRLF, og sha256 i tabellen gjelder den. Git lagrer OFL.txt med LF og samme tekst, sha256 `37784b44044a4ffd9256702b7c0982c37e5c8887ba90c6dca0479aea93dc898d`.

*Lagt til 2026-10-14 (PR 2):* `newsreader/Newsreader72pt-Medium.woff`, fra `https://raw.githubusercontent.com/productiontype/Newsreader/cfcb4f7af0e52c25e8df2a2431814c8e5fe2e155/fonts/static/woff/Newsreader72pt-Medium.woff`, sha256 `1b37a7e21e1c729b8fa16c5de7da360da256afa5e5268d2716ea5f7f1f91ce42`. Hentet med curl 14.10 kl. 17:21, til sammenligningen i planen.

- Newsreader har ingen utgivelser på GitHub. Filene er hentet fra repoet på siste commit, `cfcb4f7` fra 01.03.2021, og adressen er låst til den. Repoet har statiske WOFF-filer i tre optiske størrelser (6pt, 16pt og 72pt). 16pt er valgt, fordi overskriftene er fra 23 til 56 px.
- **IBM Plex Sans har ingen `tnum`** i GSUB-tabellen. Sifrene 0–9 er like brede som standard (600 enheter i alle fire vektene), så tallene står likevel rett under hverandre. Newsreader har `tnum` og `pnum`, og sifrene er like brede (1140 og 1185). Testen krever like brede sifre i hver fil, og `tnum` i filene som har GSUB med `pnum`. `designregler.md` §1 sier «en test sjekker at filene vi bruker, har den». Det stemmer ikke for Plex, og del 5 sier det med dato.

**PR 1, 14.10 (grenen `8-0d-grunnlag`):** `bec0a70` spesifikasjonen, `6c59659` del 5 i `designregler.md`, `88f9de3` skriftfilene og testene for dem, `82a18cb` rammen, `d6e3ad1` hjelpen, `a77a62a` testene for utseendet, `a82552c` rettingene fra gjennomgangen, `dc45df8` den daterte linja under §1 og `bc99062` punktet i `deferred-work.md`.

- Rammen er `_ramme.html`. De tre sidene begynner med `{% extends "_ramme.html" %}` og fyller blokkene `tittel`, `stil` og `innhold`. Fargene står bare i `:root` i rammen, og hvitt heter `--hvit`.
- «Oppdatert …» i stripa kommer fra `oppdatert()` i `markedsoversikt.py`, med ukedagen i norsk tid. Linja «data hentet …» under tittelen står fortsatt, og PR 2 avgjør den (`deferred-work.md`).
- Testen som forbød `url(` på sidene, tillater nå bare `/static/`. Testen for merket i malene ser nå i rammen. Fyllet i «3 av 3» er blekk (`#16181D`), ikke `#000000`, og testene fra 8.0e er rettet etter det.
- Feilsiden for en demo.db som ikke kan leses, har ikke merket, fordi ingen kan si at basen er en demobase. Feilsiden for en demobase har merket i stripa (`test_feilsiden_har_eksempeltall_for_en_demobase`).

**PR 2, 14.10 (grenen `8-0d-oversikten`, PR #40):** `5d8a728` svarene og fargene i spesifikasjonen, `27e9043` de daterte linjene i `designregler.md`, `1d18817` skriftfila Newsreader 72pt Medium, `d3411af` h1 på feilsiden, `c55e340` oversikten, `d8936c4` testene for oversikten, `61b6cb9` den skjulte teksten inne i tabellboksen, `9f0a010` rettingene fra gjennomgangen og `f6202a7` punktene i `deferred-work.md`.

- Fargenavnene i rammen: `--gul` og `--lys-gul` er byttet med `--oransje` (`#F2B53A`) og `--lys-oransje` (`#F8DE9C`), `--hjelp` heter `--brun` fordi båndet bruker samme farge, og `--baand-ut` er `#FFF6DC` med `--baand-ut-kant`. Under kolonnenavnene står `--kolonne-tekst-2`.
- Symbolene for bransjene ligger i `_bransjer.html`, ordrett fra utdraget §12.
- Vinduet ved «Oppdatert» bruker hjelpeteksten `data_hentet`, med tittelen «Oppdatert:» (svar 5). `data_hentet_aksje` venter til PR 3.
- Testparseren `_Tabell` i `test_app.py` legger linja under navnet, antallet og grensen i båndene og «NOK» i `ekstra`, så cellene er som før.
- Målt i Edge 14.10: Edge uten vindu går ikke under 504 px, så 390 px ble målt i en iframe. Der var siden 409 px bred, fordi den skjulte teksten «skiller seg ut» er `position: absolute`. Rettet i `61b6cb9` med `position: relative` på boksen.

## Spec Change Log

## Review Triage Log

Gjennomgang av PR 1 (diffen `main...8-0d-grunnlag` på `a77a62a`, 14.10), med Blind Hunter (BH, 12 funn), Edge Case Hunter (ECH, 10) og Verification Gap (VG, 1). Rettingene står i `a82552c`, `dc45df8` og `bc99062`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1, BH3 | «Oppdatert …» var en lambda uten test, og bare begynnelsen av teksten var prøvd | medium | patch: `oppdatert()` med test over midnatt, og hele teksten i stripa på begge sidene |
| BH4, ECH5 | Hvitt sto fast, og testen fant ikke farger med tre sifre, `rgb()` eller attributter | low | patch: `--hvit`, og testen ser etter alle tre |
| BH5, ECH6 | Fargepar på bakgrunnen og `blandet` mot kort var ikke prøvd | low | patch: parene i `KONTRAST` |
| BH6 | §1 sier fortsatt at filene har `tnum`, og Newsreader var ikke krevd å ha den | low | patch: datert linje under §1, og `tnum` krevd i Newsreader |
| BH10 | Kortet på feilsiden var ikke prøvd | low | patch |
| BH11 | Raden med demomerket brukte en strek §5 ikke nevner | low | patch: `--stripe-strek` |
| ECH2, ECH3 | Klikkflaten til «?» gikk 11 px inn i teksten etter, og kommentaren stemte ikke | low | patch: 5 px luft på hver side, og ny kommentar |
| ECH7, ECH8 | Testene for skriftfilene feilet uten en klar melding hvis et siffer eller GSUB manglet | low | patch |
| BH8, ECH9 | Sidene importerte `hjelpestil`, som bare rammen bruker | low | patch |
| BH2 | Tidspunktet står to ganger, i stripa og i linja under tittelen | low | utsatt: `deferred-work.md`, avgjøres i planen for PR 2 |
| ECH4 | 404-siden er Flasks standardside, uten rammen | low | utsatt fra før: ECH9 i 8.0c står i `deferred-work.md` |
| BH1 | README-en sier «Øverst står «Eksempeltall: …»» | false | merket står i stripa, øverst på siden, med samme ordlyd. `test_merket_i_demoen_er_det_samme_som_i_malene` holder sitatet lik konstanten |
| BH7 | Feilsiden har `<h1>OSE Signal</h1>` under logoen | avvist | overskriften er sidens struktur for skjermlesere. Overskriftene på oversikten avgjøres i PR 2 |
| BH9 | Klikkflaten kan overlappe en lenke ved siden av | maybe-false, avvist | marginene gir 5 px luft. Det som avgjør det, er en prøve i nettleseren i PR 2, der tabellen får nytt utseende |
| BH12 | Spesifikasjonen manglet avkryssing, triage og testtall | avvist | rettingen er å skrive i spesifikasjonen, som gjøres her |
| ECH1 | «Oppdatert» på aksjesiden er aksjens egen tid, ikke sidens eldste | avvist | aksjesiden viser én aksje, og tiden er dens egen, som linja «data hentet» der i dag |
| ECH10 | Fokus på hjelpeknappen kommer bare fra rammen | avvist | alle sidene bruker rammen, og testen krever regelen på hver side |

Gjennomgang av PR 2 (diffen `main...61b6cb9`, 14.10), med Blind Hunter (BH, 12 funn), Edge Case Hunter (ECH, 8) og Verification Gap (VG, 8 og to andre). Rettingene står i `9f0a010` og `f6202a7`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | Den hvite sirkelen og det oransje fokuset gjaldt hver `thead`, også den lyse på aksjesiden | high | patch: bare `.tabellboks thead`, og testen krever det |
| BH3, BH11, ECH4 | Ord, antall og grense i båndene, og tidspunktet under navnet, sto uten mellomrom | medium | patch |
| ECH6 | En tom bransje ga « · » under navnet | low | patch, uten egen test: kolonnen er `NOT NULL`, og alle aksjene har bransje |
| BH12 | Overskriften hadde ikke blekk selv, så paret i kontrasttesten gjaldt en arvet farge | low | patch |
| VG1, BH7 | Testene sjekket ikke at kortet står i rutenettet og tabellen i boksen | medium | patch: `_innhold()` |
| VG2 | Hvilket som helst brudd for smal skjerm ble godtatt | medium | patch: minst 816 px |
| VG3, BH6 | Ingen test for kolonneraden i blekk | medium | patch |
| VG4 | Bare `--oransje` var festet | medium | patch: `test_fargene_fra_beslutningen` |
| VG5 | Ingen test for at overskriften ikke er fet | medium | patch |
| VG6 | Den skjulte teksten kunne skjules for skjermlesere | medium | patch |
| VG7 | Ringen i regelen for blekk var ikke prøvd | medium | patch |
| VG8 | h1 når demobasen er tom, var ikke prøvd | low | patch |
| BH8, BH9, BH10 | Svakere sjekker etter omskrivingen: tidspunktet, «NOK» og grensene med en annen terskel | low | patch |
| VG, andre | Docstringen om `#F2B53A`, og raden `<tr >` som regexen ikke traff | low | patch |
| BH2, ECH1, ECH2, ECH3 | «Øvrige aksjer» sier «signalstyrke 0 eller 1» også når rader uten vurdering står der, og strekene forutsetter terskel 2 | medium | utsatt: `deferred-work.md`. Ordlyden er gruppens, og terskelen er 2 |
| ECH8 | Aksjesiden viser tidspunktet to ganger | low | utsatt fra før: BH2 fra PR 1, PR 3 |
| BH4 | Lys oransje mot hvitt er 1,3:1 | avvist | beslutning 12: teksten sier det samme (FR-103), og strekene trenger ikke 3:1 |
| BH5 | Testen for 3:1 mot hvitt ble byttet med en fast fargeverdi | avvist | instruksjonen kl. 17:31 bytter den ut med grunnen. Ringen mot fyllet står i `KONTRAST` |
| ECH5 | Boksen er et ekstra stopp for tastaturet når ingenting ruller | avvist | `tabindex="0"` på et område som ruller, er det som lar det rulles med tastaturet (WCAG 2.1.1) |
| ECH7 | Markeringen står også ved «0 av 15 aksjer» | avvist | beslutning 12 sier markering under «N av M aksjer», og M teller alle radene (8.0e, svar 3) |

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn. Før: 1491 bestått og 16 hoppet over på main (`7bb4c3e`, 14.10). Etter: 1517 bestått og 16 hoppet over på `a82552c`.

**Mutantene** (14.10, på `a77a62a`) ble kjørt én om gangen mot hele testsettet med `-x`, og fila ble satt tilbake og kontrollert med sha256. Alle 7 ble fanget:

| # | Mutant | Fanget av |
|---|---|---|
| D1 | skrift fra Google Fonts | `tests/test_hjelpetekster.py::TestSidene::test_ingen_skript_og_ingenting_fra_nettet` |
| D2 | blekk byttet til en lys farge | `tests/test_utseende.py::TestRammen::test_kontrasten_regnet_fra_fargene_i_stilen` |
| D3 | `tabular-nums` fjernet fra tallcellene | `tests/test_utseende.py::TestRammen::test_tabelltall_i_tallcellene` |
| D4 | merket borte fra stripa i demoen | `tests/test_demo.py::TestSidene::test_bryteren_med_demobase_viser_eksempeltall` |
| D5 | gult fokus på lys bakgrunn | `tests/test_utseende.py::TestRammen::test_fokus_i_blekk_paa_lys_bakgrunn_og_lys_gul_i_stripa` |
| D6 | ringen i `#F2B53A` | `tests/test_app.py::TestStory80c::test_den_gule_ringen_har_minst_3_til_1_mot_hvit` |
| D7 | en lenke til `/min-liste` | `tests/test_utseende.py::TestRammen::test_hver_lenke_gaar_til_en_side_som_finnes` |

**PR 2:** `uv run pytest -q`: før 1517 bestått og 16 hoppet over på main (`2e274d0`), etter 1532 og 16 på `9f0a010`.

**Mutantene for PR 2** (14.10, på `9f0a010`), kjørt på samme måte. Mutant 8 i planen er byttet med E8a–E8c (instruksjonen kl. 17:31). Kjøringen ble stoppet av Claude Code etter E8c fordi maskinen hadde for lite minne. E9–E11 er ikke kjørt, og fila ble satt tilbake fra kopien. *Lagt til 2026-10-14:* E9–E11 ble kjørt kl. 20:49 på `df2e77d`, én om gangen med `-x` og bare `tests/test_utseende.py`. Fila ble satt tilbake etter hver og var lik HEAD (sha256 og blob). Alle 13 er fanget.

| # | Mutant | Fanget av |
|---|---|---|
| E1 | kortet flyttet under tabellen | `tests/test_utseende.py::TestOversikten::test_kortet_slik_leser_staar_ved_siden_av_overskriften` |
| E2 | `aria-hidden` fjernet fra symbolene | `tests/test_app.py::TestStory80eTekst::test_slik_leser_du_tabellen_har_3_punkter` |
| E3 | musepekeren byttet til en pil | `tests/test_utseende.py::TestOversikten::test_symbolene_i_kortet_er_skjult_og_ingen_pil_ved_navnet` |
| E4 | «?» i kolonneraden i blekk | `tests/test_utseende.py::TestOversikten::test_hjelpeknappen_er_hvit_paa_blekk_med_oransje_fokus` |
| E5 | fokus i kolonneraden i blekk | `tests/test_utseende.py::TestOversikten::test_hjelpeknappen_er_hvit_paa_blekk_med_oransje_fokus` |
| E6 | ringen på klikkflaten | `tests/test_utseende.py::TestOversikten::test_fokusringen_staar_rundt_sirkelen` |
| E7 | `overflow-x` fjernet | `tests/test_utseende.py::TestOversikten::test_tabellen_ruller_i_sin_egen_boks` |
| E8a | sterk oransje ved 2 av 3 | `tests/test_app.py::TestStory80c::test_to_av_tre_merkes_med_mer_enn_lys_bakgrunn` |
| E8b | strek ved 1 av 3 | `tests/test_app.py::TestStory80c::test_bare_radene_over_terskelen_er_merket` |
| E8c | markeringen borte fra overskriften | `tests/test_app.py::TestStory80eTekst::test_overskriften_teller_fra_radene` |
| E9 | «data hentet» tilbake under tittelen | `tests/test_utseende.py::TestOversikten::test_tidspunktet_staar_en_gang` |
| E10 | to h1 | `tests/test_utseende.py::TestOversikten::test_kortet_slik_leser_staar_ved_siden_av_overskriften` |
| E11 | små overskrifter i Newsreader | `tests/test_utseende.py::TestOversikten::test_de_smaa_overskriftene_er_i_plex` |
