---
title: 'Story 8.0d: Utseendet fra designforslaget'
type: 'feature'
created: '2026-10-14'
status: 'in-progress'
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

## PR 2b: antallet i overskriften

*Lagt til 2026-10-14 (gruppen 14.10 kl. 21:04 og 21:06, instruksjonen kl. 21:08):* M i «N av M aksjer» er alle aksjene i lista, også de uten kurser, ikke bare radene i tabellen. Det gjelder overskriften, linja under den og «… av M aksjer ble vurdert». I demoen blir det «5 av 15 aksjer skilte seg ut fredag» og «Demo Børs · 09.10 · 15 aksjer». Aksjer uten kurser står fortsatt under tabellen som «Uten data i denne kilden», og båndene teller radene sine som før. Dette erstatter beslutningen i 8.0e (svar 3) om at M telles fra radene.

Mutanten: M fra radene igjen.

**PR 2b, 14.10 (grenen `8-0d-antall`, PR #41):** `fe730b4` beslutningen, `77e6f51` endringen (`antall_aksjer=len(poster)` i `app.py`, brukt i overskriften, linja under og setningen om vurdert), `4fc313e` testene og `ebfebef` rettingene fra gjennomgangen. Lista er tabellen `aksje` i basen (AD-21), som også gir «Uten data i denne kilden». Setningen «… av M aksjer ble vurdert.» står fortsatt bare når en rad mangler vurdering.

`uv run pytest -q`: før 1532 bestått og 16 hoppet over på main (`4637004`), etter 1533 og 16 på `4fc313e`. Mutanten «M fra radene igjen» (`antall_aksjer=len(rader)`) ble kjørt med `-x` og bare `tests/test_app.py`, og fanget av `tests/test_app.py::TestStory80c::test_noen_mangler_vurdering_gir_begge_setningene`. Fila var lik HEAD etterpå (sha256 og blob).

Gjennomgang av PR 2b (diffen `main...4fc313e`), med Blind Hunter (BH, 6 funn), Edge Case Hunter (ECH, 3) og Verification Gap (VG, 3). Rettingene står i `ebfebef`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | M kunne vært fast 15 eller `len(AKSJEUNIVERS)` uten at en test feilet | medium | patch: testen der DNO og MPCC er fjernet fra `aksje`, krever «0 av 13» og «13 aksjer» |
| VG2 | Antallet i båndet «Øvrige aksjer» var ikke festet | medium | patch: den nye testen krever antallene i begge båndene |
| BH3 | Testnavnet sa at M telles fra radene | low | patch: `test_overskriften_teller_n_fra_radene_og_m_fra_lista` |
| BH1, ECH1, VG3 | Setningen om vurdert står ikke når alle radene er vurdert og en aksje mangler kurser | medium | utsatt: `deferred-work.md`. Beslutningen gjelder M, ikke når setningen står |
| BH2 | Ingen test for tilfellet over | low | utsatt sammen med BH1 |
| BH4 | Demotesten krever «5 av 15 aksjer skilte seg ut fredag» ordrett | avvist | instruksjonen kl. 21:08 sier at demoen skal vise nettopp det |
| BH5 | Den nye testen antar rekkefølgen i `AKSJEUNIVERS` og datoen 31.10 | avvist | testbasen og de andre testene i klassen bruker samme dato, og hvilken aksje som mangler, spiller ingen rolle |
| BH6, ECH2 | M teller tabellen `aksje`, ikke `AKSJEUNIVERS` | avvist | lista er `aksje` (AD-21), som fotnoten, og VG1-testen krever det |
| ECH3 | Linja under overskriften har datoen fra radene og antallet fra lista | avvist | fotnoten «Uten data i denne kilden» står på samme side, og beslutningen sier «15 aksjer» i linja |

## PR 3: aksjesiden, og brikkene og pillene i oversikten

*Lagt til 2026-10-14 (planen kl. 22:28, svarene kl. 22:50, beslutningen kl. 19:59):* grenen `8-0d-aksjesiden`. Planen er vist i chatten og ført kort i Utført-linja for kl. 22:28 i `docs/ai-prompts/2026-10-14.md`. Svarene er beslutninger:

18. Under h1 på aksjesiden står «Oslo Børs · 14.10», og «Demo Børs» i demoen. Ticker og bransje står i merkene over h1.
19. Tegnforklaringen under grafen fjernes når navnene står ved enden av linjene. Teksten for skjermleseren sier fortsatt hvilken linje som er hva.
20. Bevegelse får tre ganger grensen på hver side, som trend, og prikken står ved enden når målingen er utenfor skalaen.
21. Endringskortet sier ukedagene, som på tavla, for eksempel «fra tirsdag til onsdag». Datoen står i linja under h1.
22. I sjekkortene står «?» ved navnet på sjekken, ved «Ga»-pillen og ved «Målt mot».
23. «Ukjent» retning står som tekst uten pille, i Dempet.
24. «Øvrige aksjer» får «og N uten signal» etter grensen når rader uten signal står der, også «og 1 uten signal». Pillen teller alle radene i båndet.
25. Setningen «… av M aksjer ble vurdert.» står bare når ingen skilte seg ut, nå når færre enn alle aksjene i lista ble vurdert. «Uten data i denne kilden» dekker resten.
26. README-statusen: «utseendet fra designforslaget» flyttes til «Flettet til main», og «Neste:» blir «sortering ved klikk i kolonneraden, hovedindeksen, Min liste, periodene i kursgrafen, og så KI-laget». Endres i PR 3.
27. «2 av 3» i oversikten er den hvite pillen med tekst og kant i blekk, uten ring, med den lys oransje streken som før (gruppen kl. 19:59).

Resten av planen gjelder som vist: merkene over h1, overskriften «<navn> skilte seg ut <ukedag>» med lys oransje markering i 72pt når styrken er på terskelen eller over (beslutning 7), tidspunktet bare i stripa, fire nøkkeltallkort med endringen som det fjerde og T, B og I som brikker, de 3 sjekkene som kort med det grå feltet foran grafen, grafen med heltrukket snitt og navnene ved enden av linjene, og «Markedsoversikt» uten pil. I oversikten: T, B og I som brikker og retningen i en pille.

**Mutantene for PR 3** (planen kl. 22:28; b, c, d, g og k er nr. 2, 3, 4, 7 og 11 i del G fra 13.10): M1 `stroke-dasharray` tilbake på snittet; M2 hjelpeteksten sier «stiplede»; M3 «← » tilbake i lenken; M4 grafen før sjekkene; M5 det grå feltet tilbake til `#D9D5CB`; M6 «data hentet» tilbake på aksjesiden; M7 markeringen borte fra overskriften på aksjesiden; M8 «skilte seg ut» også under terskelen; M9 endringskortet borte; M10 skalaen uten `aria-hidden`; M11 brikken for 0 med grønt fyll; M12 «2 av 3» uten pille; M13 setningen om vurdert regnet fra radene igjen; M14 «uten signal» teller alle radene i «Øvrige».

**PR 3, 14.–15.10 (grenen `8-0d-aksjesiden`, PR #42):** `4e68153` svarene og planen, `30e6d97` oversikten, `cec8c53` aksjesiden, `c503654` testene, `c8ed4aa` README-statusen (svar 26), `fcfbdc2` navnene i grafen med hvit kant og brikkene høyrestilt, `8323d3c` tre punkter i `deferred-work.md`, `f889bcd` og `ee27d53` rettingene og testene fra gjennomgangen i natt. *Lagt til 2026-10-15:* `fae3e24` testene, og `1deed86` og `58f385c` punktene i `deferred-work.md` fra gjennomgangen 15.10. `0962974` triagen, mutantene og testtallene.

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

Gjennomgang av PR 3. Gjennomgangen natt til 15.10 er ikke ført med funnene. Rettingene står i `f889bcd` og `ee27d53`, med merkene i kommentarene: BH2 og ECH1 (navnene over månedsnavnene), ECH3 og ECH4 (ingen prikk og ingen skala for en måling eller volumfaktor som ikke er et tall), BH5 og VG4 (etiketten sier tykkelsen, ikke fargen), VG1 («Demo Børs»), VG3 (3 av 3 over terskelen), VG5 (feltet mellom grensene), VG6 (ukedagene i endringen), VG7 (rekkefølgen i README-en) og VG8 (feltet mot sporet). «?» ved «Oppdatert» står bare når siden har et tidspunkt (`f889bcd`).

*Lagt til 2026-10-15:* gjennomgangen ble kjørt på nytt på diffen `main...ee27d53`, med Blind Hunter (BH, 20 funn), Edge Case Hunter (ECH, 8) og Verification Gap (VG, 4). Rettingene står i `fae3e24`, `1deed86` og `58f385c`. Bare tester og dokumenter er rettet (instruksjonen 15.10 kl. 11:09).

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH6, ECH2 | Endringskortet sier «fra fredag til fredag» når de to siste kursradene ligger 7 dager eller mer fra hverandre | medium | **avgjøres av gruppen**: en retting endrer teksten på siden. Ført i `deferred-work.md`. PR-en flettes ikke før det er avgjort |
| ECH1 | Aksjen og serien leses i to lesinger, så endringen kan gjelde en annen dag enn sluttkursen hvis hentingen skriver mellom dem | low | utsatt: `deferred-work.md`. Rettingen er i koden. Grafen leser serien slik også på main |
| VG1 | Terskelen i overskriften på aksjesiden var ikke prøvd med en annen terskel | medium | patch: `test_terskelen_i_overskriften_kommer_fra_parametre` |
| VG2 | Ingen test leste «hva den måler» og regelen i sjekkortene | medium | patch: `test_hva_sjekken_maaler_og_regelen_kommer_fra_parametre` |
| VG3 | Endringskortet ved 0,00 % og med én kursdag var ikke prøvd | medium | patch: `test_endringen_uten_farge_naar_den_vises_som_null_og_strek_uten_dagen_foer` |
| VG4 | Prikken ved enden av kurslinja var ikke prøvd | low | patch: `test_prikken_staar_paa_det_siste_kurspunktet`, og sirkelen i `test_grafen_har_heltrukket_snitt_og_navnene_ved_enden` |
| BH12, ECH7 | Klassen `bidro` på sjekkortene har ingen regel i stilen | low | patch i testen: det som skiller kortene for synet, er pillen med farge etter fortegnet (utdraget §8), og `test_bare_sjekkene_som_slo_ut_er_merket` krever det. Klassen står som før |
| BH15 | To `resolved:`-linjer i samme punkt i `deferred-work.md` | low | patch: én linje |
| BH18 | Testen for «under arbeid» ga ValueError, ikke en melding, uten graf | low | patch |
| BH1, ECH4 | En grense som er NaN eller uendelig, slipper gjennom `<= 0` | avvist | `Vurdering` krever endelige tall for `standardavvik` (`src/vurderingsdata.py`), og volumfaktoren er en parameter |
| BH2, BH3 | Grensen for trend, volumfaktoren, terskelen og vinduene kommer fra Parametre i dag, ikke fra vurderingen | avvist | `sjekker_fra` tar grensene som er parametre, fra `p` (docstringen), og oversikten bruker samme terskel |
| BH4, ECH5 | `hva_den_maaler` og `regelen` gir KeyError for et nytt navn | avvist | `sjekker_fra` gir alltid de tre navnene |
| BH5 | Fargen i endringskortet rundes i malen | avvist | samme regel som i oversikten (`test_endring_som_vises_som_null_har_ingen_farge`). `Kursrad` krever endelige kurser over 0 (`src/kursdata.py`), så endringen er et tall |
| BH7 | Navnet på snittet står ved x for kurslinja | avvist | snittet regnes for hvert punkt etter de første dagene i vinduet, så linjene ender på samme punkt |
| BH8, ECH6 | Navnene kan gå utenfor eller over hverandre ved liten høyde, og kursnavnet alene klemmes ikke nederst | avvist | `HOYDE` er fast. Kursnavnet står 8 px over punktet, som er minst `MARG_Y` (12) fra bunnen, så det står over månedsnavnene |
| BH9 | `_siste` leser punktstrengen på nytt | avvist | strengen lages av `_koordinater` i samme modul |
| BH10 | Alt annet enn +1 og -1 får klassen `null` | avvist | verdiene er `SJEKKVERDIER` (-1, 0, 1) i `Vurdering` |
| BH11 | Tittelen på bokstaven er feltnavnet | avvist | «trend», «bevegelse» og «interesse» er ordene, som i oversikten siden 8.0e |
| BH13 | Hjelpen ved «Målt mot» nevner feltet også når skalaen mangler | avvist | skalaen mangler bare når grensen ikke er over 0, og hjelpen står i det første kortet, Trend, der grensen er nøytralsonen |
| BH14 | Klassen `to-av-tre` følger terskelen, ikke 2 | utsatt fra før | strekene og terskelen står i `deferred-work.md` (PR 2) |
| BH16 | README-prøven er borte fra «Neste:» | avvist | svar 26 sier hva «Neste:» skal være, og README-prøven tas når mest mulig er bygget (gruppen 14.10 kl. 22:19 og 22:25) |
| BH17 | Status gikk fra `in-review` til `in-progress` | avvist | satt i `4e68153` da PR 3 begynte |
| BH19 | Testene sier «lørdag», og 31.10 er ikke en børsdag | avvist | testbasen bruker 31.10, som i PR 2b (BH5 der) |
| BH20 | Stilen for brikkene står i rammen og gjelder alle sidene | medium | **avgjøres av gruppen**: symbolet «T +1» i kortet «Slik leser du tabellen» har klassen `brikke` og arver nå `min-width: 34px`, `height: 24px`, `inline-flex` og en gjennomsiktig kant fra den felles regelen. Det er en endring på siden fra PR 2 som planen for PR 3 ikke nevner. Ført i `deferred-work.md`. `.retningspille.opp` er mer spesifikk enn `.opp`, så den delen er avvist |
| ECH3 | Grensen over skalaen for bevegelse vises med én desimal, «0,0 %» under 0,05 %, mens tallet i kortet har så mange desimaler som trengs (`desimaler_mot_grense`) | low | **avgjøres av gruppen**: en retting endrer teksten på siden. Ført i `deferred-work.md` |
| ECH8 | Merket viser symbolet, ikke tickeren fra EODHD | avvist | oversikten viser også symbolet (avvik 11) |

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

**PR 3:** `uv run pytest -q`: før 1533 bestått og 16 hoppet over på main (`b9bcffd`), etter 1558 og 16 på `fae3e24` (15.10).

**Mutantene for PR 3** (15.10, på `ee27d53`), kjørt én om gangen med `-x` og bare testfilene som skulle fange dem, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver (sha256 uten CRLF, og ingen endring i `git status`). Alle 14 er fanget.

| # | Mutant | Fanget av |
|---|---|---|
| M1 | `stroke-dasharray` tilbake på snittet | `tests/test_app.py::TestStory80dAksjesiden::test_grafen_har_heltrukket_snitt_og_navnene_ved_enden` |
| M2 | hjelpeteksten sier «stiplede» | `tests/test_app.py::TestStory80dAksjesiden::test_grafen_har_heltrukket_snitt_og_navnene_ved_enden` |
| M3 | «← » tilbake i lenken | `tests/test_app.py::TestStory80dAksjesiden::test_tilbakelenken_er_markedsoversikt_uten_pil` |
| M4 | grafen før sjekkene | `tests/test_app.py::TestStory80dAksjesiden::test_sjekkene_staar_som_kort_foer_grafen` |
| M5 | det grå feltet tilbake til `#D9D5CB` | `tests/test_app.py::TestStory80dAksjesiden::test_det_graa_feltet_har_fargen_fra_designreglene` |
| M6 | «data hentet» tilbake på aksjesiden | `tests/test_app.py::TestTidsstempler::test_detaljen_viser_symbolets_egen_tid` |
| M7 | markeringen borte fra overskriften på aksjesiden | `tests/test_app.py::TestStory80dAksjesiden::test_overskriften_med_markering_naar_aksjen_skilte_seg_ut` |
| M8 | «skilte seg ut» også under terskelen | `tests/test_app.py::TestStory80dAksjesiden::test_overskriften_med_markering_naar_aksjen_skilte_seg_ut` |
| M9 | endringskortet borte | `tests/test_app.py::TestStory80dAksjesiden::test_endringen_er_det_fjerde_kortet_med_ukedagene` |
| M10 | skalaen uten `aria-hidden` | `tests/test_app.py::TestStory80dAksjesiden::test_sjekkene_staar_som_kort_foer_grafen` |
| M11 | brikken for 0 med grønt fyll | `tests/test_utseende.py::TestBrikkene::test_brikkene_har_klassen_etter_verdien` |
| M12 | «2 av 3» uten pille | `tests/test_utseende.py::TestBrikkene::test_to_av_tre_er_en_hvit_pille_og_en_av_tre_er_tekst` |
| M13 | setningen om vurdert regnet fra radene igjen | `tests/test_app.py::TestStory80e::test_ble_vurdert_ogsaa_naar_en_aksje_mangler_kurser` |
| M14 | «uten signal» teller alle radene i «Øvrige» | `tests/test_app.py::TestStory80e::test_delingen_bruker_terskelen_fra_parametre` |

M2 ble kjørt med `tests/test_hjelpetekster.py` og `tests/test_app.py`, M8 med `tests/test_aksjedetalj.py` og `tests/test_app.py`, og M5, M6, M10 og M12 med to filer. Den første fila fanget ikke M2 og M8. To av testene fra gjennomgangen 15.10 ble prøvd på samme måte: uten `terskel=p.terskel` i `bygg_detalj` feilet `test_terskelen_i_overskriften_kommer_fra_parametre`, og med 50 fast i teksten for trend feilet `test_hva_sjekken_maaler_og_regelen_kommer_fra_parametre`.
