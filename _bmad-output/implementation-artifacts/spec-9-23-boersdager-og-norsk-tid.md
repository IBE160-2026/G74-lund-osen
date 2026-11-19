---
title: 'Story 9.23: «51 børsdager» i koden og norsk tid i morgensjekken'
type: 'code'
created: '2026-11-19'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'beb6aa15'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-22-morgensjekken-og-to-rettinger.md'
---

Skrevet 19.11 etter instruksjonen om de to spørsmålene fra 9.22 (limt inn
kl. 10:40 i `docs/ai-prompts/2026-11-19.md`) og gruppens svar 19.11 kl. 09:59.
Rådet anbefalte å vente med begge til kodegjennomgangen etter brukertest 2, men
gruppen valgte å ta dem nå. Neste ledige nummer i Epic 9 etter 9.22 er 9.23.
Worktreen er `G74-lund-osen-9-23`, på grenen `9-23-boersdager-og-norsk-tid`, fra
`origin/main` (`beb6aa15`). Svarene står på main, ved spørsmålene i
spesifikasjonen for 9.22 og ved punktene i `issues.md` (steg 1 i instruksjonen).

## Storyen

Som **gruppen som leser koden og morgensjekken** vil vi at kommentarene sier
«børsdager» der FR-101 gjør det, og at klokkeslettene i morgensjekken står i
norsk tid også når vi kjører den på Windows, så vi ikke må regne om en time.

**Oppfyller:** spørsmål 1 og 2 fra 9.22 (svaret 19.11 kl. 09:59) og de to
punktene i `issues.md` · **Begrenses av:** regel 3, 16, 20 og 22; ingen bilder
og ingen ny migrasjon, og den planlagte oppgaven «Morgensjekk OSE Signal»
endres ikke

**Avhenger av:** 9.22. **Én økt:** ja.

## Det som gjøres

1. **«51 handelsdager» blir «51 børsdager»** i kommentaren øverst i
   `src/fetch_prices.py` og i docstringen i `tests/test_fetch_prices.py`, og
   bare der. «Handelsdag» er brukt med vilje ellers og endres ikke: i navn som
   `MINST_HANDELSDAGER`, i kolonnen `handelsdager` i basen og i regelen om at
   halve handelsdager er børsdager. Historikken endres heller ikke.
2. **Klokkeslettene fra git i morgensjekken** står i norsk tid, også på
   Windows, der `TZ` i miljøet ikke virker for git. Det gjelder «HEAD paa
   GitHub» og de andre klokkeslettene fra git i utskriften. På GitHub er
   utskriften som før.
3. Hver retting får en test som feiler før rettingen.

## Bygget

Bygget 19.11 i vinduet, på grenen.

| Del | Commit | Testen som feiler før rettingen |
|---|---|---|
| «51 boersdager» i kommentaren øverst i `src/fetch_prices.py` og i docstringen i `tests/test_fetch_prices.py` | `41e18773` | `tests/test_boersdager_9_23.py`: 3 av 4 feilet før rettingen. Den siste passer på at «handelsdag» står der den er brukt med vilje |
| Klokkeslettene fra git i morgensjekken i norsk tid | `12ac90c4` | `tests/test_morgensjekken_9_23.py`: alle 9 feilet før rettingen |
| Rettingene etter gjennomgangen | `6c1744a4` | Med «\|» i forfatternavnet stoppet del 1 med `ValueError` før ECH1, så alle de 10 parametriserte testene feilet |

**Ordet.** Begge stedene er skrevet uten norske bokstaver («foer», «aar»), og
de første 60 linjene i `src/fetch_prices.py` har ingen æ, ø eller å. Derfor
står ordet som «boersdager», som i `src/boersdag.py` («Halve handelsdager er
boersdager»). «51 handelsdager» står ikke lenger noe sted i `src/` eller `tests/`,
utenom de to testene som sjekker at det er borte. `MINST_HANDELSDAGER`, kolonnen
`handelsdager` i `0008_omsetning.sql` og regelen om halve handelsdager står.

**Tiden.** git gir tiden som sekunder (`%at` og `%(taggerdate:unix)`), og
skriptet regner den om til norsk tid med `OSLO` i `norsk_tid()`. Det gjelder:
- «HEAD paa GitHub»;
- commitene siste døgn i del 1;
- endringene i briefen etter taggen i del 7;
- tiden for en ny tag i del 7.

Før 9.23 skrev git tiden selv med `--date=format-local` og `TZ=Europe/Oslo`,
som ikke virker for git på Windows. På GitHub er utskriften som før for
commitene. Taggene sto før i taggerens egen tidssone og står nå i norsk tid.
Taggene vi har, er laget i Oslo (`+0200`), så de står som før.

Testen kjører starten, del 1 og del 7 mot et lite repo i en midlertidig mappe.
`TZ` er satt både til Europe/Oslo, som på GitHub, og til UTC, som gir det samme
som Windows. Commiten er fra vintertid (21:44 i Oslo) og taggen fra sommertid
(23:01 i Oslo). Testene for taggene i 9.22 har en falsk git som nå gir sekunder.

## Morgensjekken mot main, før og etter

Kjørt lokalt mot main på `beb6aa15`, som er committet 19.11 kl. 10:41 (`+0100`):
før med skriptet på `origin/main` kl. 11:03, og etter med skriptet på grenen
kl. 11:15 (`6c1744a4`).

| Kjøring | Linja |
|---|---|
| Før | `HEAD paa GitHub: beb6aa15 19.11 09:41 Svarene 19.11 kl. 09:59 på de to spørsmålene fra 9.22` |
| Etter | `HEAD paa GitHub: beb6aa15 19.11 10:41 Svarene 19.11 kl. 09:59 på de to spørsmålene fra 9.22` |

Også klokkeslettene for commitene i del 1 var én time for tidlige før, for
eksempel `7480e72c 18.11 23:16` for flettingen av 9.22, som var kl. 00:16 19.11.

## Gjennomgangen 19.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, uten git og pytest, på diffen kl. 11:11. 6 funn, alle lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | lav | Del 1 delte feltene på «\|», så en «\|» i forfatternavnet ga nå `ValueError` og stoppet sjekken | Rettet: `%x1f`, som i del 10. Testen har «Test \| Person» |
| ECH2 | lav | En tag uten `-a` (uten tid) var ikke testet, og hjelperen i 9.22 tålte den ikke | Rettet: testen har en slik tag, og hjelperen tåler den |
| ECH3 | lav | Testrepoet arvet den globale git-oppsettet, med signering og hooks | Rettet: `GIT_CONFIG_GLOBAL` til en tom fil og `GIT_CONFIG_NOSYSTEM` |
| VG1 | lav | Instruksjonen sier «51 børsdager», koden «51 boersdager» | Står: stedene er skrevet uten norske bokstaver, og valget står over. Spørsmål 1 |
| VG2 | lav | «Som før på GitHub» stemte ikke for en tag i en annen tidssone | Rettet: docstringen og spesifikasjonen sier det |
| VG3 | lav | Vakten forbød bare tre skrivemåter | Rettet: ingen datoformat fra git utenom `%at` og `%ct`, ingen `--date`, og hver `%(…date)` er `:unix` |

Leseren fant at alle klokkeslettene fra git i utskriften er dekket, at
formatene er de samme som før, og at tomme svar fra git gir det samme som før.

## Spørsmål

1. «51 boersdager» står uten ø, som resten av teksten på de to stedene
   (VG1). Skal det heller stå «51 børsdager», som i instruksjonen?

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Ingen bilder og ingen ny migrasjon. Den planlagte oppgaven «Morgensjekk OSE
  Signal» endres ikke.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.
- Pausene om kvelden gjelder.

## Kontroll

- [x] «51 boersdager» bare i kommentaren og docstringen, med en test som feiler før rettingen
- [x] Klokkeslettene fra git i norsk tid, også på Windows, med en test som feiler før rettingen
- [x] Morgensjekken kjørt mot main før og etter, med linja «HEAD paa GitHub» her
- [x] Gjennomgangen er tatt
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: `test_boersdager_9_23.py` 4, `test_fetch_prices.py` 317 og 16 hoppet over, `test_morgensjekken_9_23.py` 11, `test_morgensjekken_9_22.py` 13, `test_boersdager_9_22.py` 1, `test_ryddighet.py` 36 og `test_ruff.py` 6, én om gangen, og `--dokumentene` på `ecd3e6b9` kl. 11:16–11:35 med 3096 bestått og 7 hoppet over
- [ ] CI er grønn i alle jobbene
- [ ] Spørsmålene og punktene i `issues.md` har en datert linje når de er løst
