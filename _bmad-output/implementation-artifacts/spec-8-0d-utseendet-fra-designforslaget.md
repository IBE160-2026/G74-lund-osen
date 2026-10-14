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
- [ ] `designregler.md` -- del 5 -- reglene før utseendet bygges
- [ ] `src/static/fonts/` -- skriftfilene og lisensene -- §1
- [ ] `src/templates/_ramme.html` og de tre malene -- rammen, stripa, fargene, fokus, bunnlinja og demomerket -- ett sted for utseendet
- [ ] `src/templates/_hjelp.html`, `basefeil.html` -- hjelpevinduet og feilsiden i rammen
- [ ] `tests/test_utseende.py` -- kontrasten, ingenting fra nettet, tabelltall, sifrene og `tnum` i filene, merket i stripa, lenkene

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

- Newsreader har ingen utgivelser på GitHub. Filene er hentet fra repoet på siste commit, `cfcb4f7` fra 01.03.2021, og adressen er låst til den. Repoet har statiske WOFF-filer i tre optiske størrelser (6pt, 16pt og 72pt). 16pt er valgt, fordi overskriftene er fra 23 til 56 px.
- **IBM Plex Sans har ingen `tnum`** i GSUB-tabellen. Sifrene 0–9 er like brede som standard (600 enheter i alle fire vektene), så tallene står likevel rett under hverandre. Newsreader har `tnum` og `pnum`, og sifrene er like brede (1140 og 1185). Testen krever like brede sifre i hver fil, og `tnum` i filene som har GSUB med `pnum`. `designregler.md` §1 sier «en test sjekker at filene vi bruker, har den». Det stemmer ikke for Plex, og del 5 sier det med dato.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn. Før: 1491 bestått og 16 hoppet over på main (`7bb4c3e`, 14.10).
