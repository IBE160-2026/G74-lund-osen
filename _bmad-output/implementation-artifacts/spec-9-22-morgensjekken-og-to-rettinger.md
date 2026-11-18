---
title: 'Story 9.22: morgensjekken uten falske alarmer, «51 børsdager» og ett navn på sletteknappen'
type: 'code'
created: '2026-11-18'
status: 'done'
route: 'dispatch'
baseline_commit: '0c650e14'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-20-prd-mot-rubrikken.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-21-bildene-av-he2-og-he14.md'
---

Skrevet 18.11 etter instruksjonen om oppgavene for brukertest 2 og tre små
rettinger (limt inn kl. 21:41 i `docs/ai-prompts/2026-11-18.md`) og gruppens
svar 18.11 kl. 11:42, 11:49, 16:01 og 21:27. Rådet anbefalte rettingene, men for
knappen anbefalte det å vente til etter brukertest 2, og gruppen valgte i dag.
Neste ledige nummer i Epic 9 etter 9.21 er 9.22. Worktreen er
`G74-lund-osen-9-22`, på grenen `9-22-morgensjekken-og-to-rettinger`, fra
`origin/main` (`0c650e14`). Oppgavene for brukertest 2 i `docs/brukertest.md`
står på main, ikke på grenen (steg 1 i instruksjonen).

## Storyen

Som **gruppen som leser morgensjekken og bruker appen i brukertest 2** vil vi at
sjekken bare merker det som er feil, og at appen bruker de samme ordene overalt,
så et merke betyr noe og personen i testen ikke møter to navn på samme knapp.

**Oppfyller:** spørsmål 7 i 9.20 (svaret 18.11 kl. 11:49), spørsmål 1 i 9.21
(ECH3), og punktene om morgensjekken i `issues.md` · **Begrenses av:** regel
3, 16, 19, 20 og 22; ingen ny migrasjon, og den planlagte oppgaven «Morgensjekk
OSE Signal» endres ikke

**Avhenger av:** 9.20, 9.21. **Én økt:** ja.

## Det som gjøres

1. **Morgensjekken** (`.github/scripts/morgensjekk.py`):
   - Del 2, dagsfilene: hver «## »-overskrift er en instruksjon eller beskjed,
     med eller uten klokkeslett. Utført står som `**Utført:**`,
     `**Utført (…):**` og `**Utført, …:**`, og én linje kan dekke flere ved å
     nevne dem. En som er limt inn på nytt og ikke ført på nytt, trenger ingen.
     Kan sjekken ikke avgjøre det, står det «uklart», ikke «mangler».
   - Del 7: taggen `arbeidskrav-product-brief-v8` (06.10, story 9.6) står blant
     de kjente.
   - Del 9: de fire kjente `.json`-filene og de tolv treffene på plassholdere i
     fire testfiler står i en liste over unntak, med grunnen, etter verdien og
     ikke linjenummeret. En ny `.json`-fil eller en ekte nøkkel merkes
     fortsatt.
   - Del 10: regel 20 teller bare gruppens commits. Faglærers commits og
     merge-commits fra GitHub vises for seg.
2. **«51 handelsdager» blir «51 børsdager»** i FR-101 og i kilden i
   `src/hjelpetekster.py` som siterer den, med en linje i endringsloggen til
   PRD-en (regel 19). Teksten som vises, sier alt «børsdager».
3. **Knappen ved et notat med kjøp og salg** heter det samme på aksjesiden som i
   spørsmålet før sletting: «Slett notatet, kjøpet og salget». Bildene i
   `docs/appen/` som viser knappen, tas på nytt i demoen, og avtrykkene og
   bildegrenen følger med.
4. Hver retting får en test som feiler før rettingen.

## Bygget

Bygget 18.11 i vinduet, på grenen.

| Del | Commit | Testen som feiler før rettingen |
|---|---|---|
| Morgensjekken: dagsfilene, taggen v8, unntakene og regel 20 | `812f462a` | `tests/test_morgensjekken_9_22.py`: 10 av 11 feilet mot skriptet på `origin/main`; den siste passer på at en ny tag fortsatt merkes |
| «51 børsdager» i FR-101 og i kilden, med en linje i endringsloggen | `46c7dde5` | `tests/test_boersdager_9_22.py` |
| Sletteknappen ved et notat med kjøp og salg | `1185c652` | `test_knappen_ved_notatet_heter_som_i_spoersmaalet_med_salg` i `tests/test_notater.py`, på aksjesiden og i Min liste |
| Spørsmål 7 i 9.20 og spørsmål 1 i 9.21, og 9.22 i `epics.md` og sprintstatusen | `b99bd3f3`, `b2f46f69` | – |
| Bildene som viser knappen, og avtrykkene | `f0f5abec` | Avtrykkene i `tests/test_docker.py` |

**Dagsfilene.** Hver «## »-overskrift utenfor kodeblokkene er en instruksjon
eller beskjed. En Utført-linje nevner en seksjon med:
- et klokkeslett i etiketten («(beskjedene kl. 12:32, 12:41 og 13:19)») eller i
  første setning («Instruksjonen kl. 11:17, med svaret kl. 11:19»);
- første ord i overskriften først i etiketten eller etter «om» («instruksjonen
  om rettingene»), der de vanlige ordene som «svarene» og «oppføringen» hoppes
  over;
- eller et storynummer alene («**Utført, 8.19:**») når overskriften sier
  «story 8.19».

Klokkeslettet til en seksjon er dens eget: først i overskriften, ellers det
første «kl.» i overskriften, ellers «Limt inn kl.» først i teksten. Har flere
seksjoner samme klokkeslett, gjelder det den ene som linja ikke alt nevner med
første ord. Ellers er det «uklart».

En linje uten etikett gjelder seksjonen den står under. En linje med etikett
gjelder den bare når den ikke nevner en annen seksjon klart.

En seksjon som er limt inn på nytt, og der teksten sier «ikke ført på nytt»,
trenger ingen. Står det bare «limt inn på nytt», er det «uklart».

«Uklart» er også en seksjon uten et klart treff der en senere etikett har et av
de lengre ordene i overskriften, eller der neste seksjon har sin egen linje.
Neste seksjon kan da dekke begge, som «## 21:54» og «## 21:56» 18.10. Ellers står
det «mangler».

Telt for hånd 18.11 kl. 22:00, og testen sier det samme:

| Dagsfil | Instruksjoner og beskjeder | Med Utført | Limt inn på nytt |
|---|---:|---:|---:|
| 10.11 | 11 | 11 | 0 |
| 16.11 | 7 | 7 | 0 |
| 17.11 | 12 | 12 | 0 |
| 18.11, før instruksjonen kl. 21:41 | 6 | 5 | 1 |

Testen har også en konstruert dagsfil med alle de fire utfallene, tilfellene fra
gjennomgangen og en overskrift i en kodeblokk, som ikke teller. Dagsfila for
17.11 uten linja «(beskjedene kl. 22:18 og 22:50)» gir «mangler» for kl. 22:18 og
22:50 (ECH1). Dagsfila for 13.10 (38 overskrifter, med overskrifter fra innlimt
tekst) gir 38 med Utført.

Dagsfilene fra 21.09 til 07.11 gir noen «mangler» og «uklart», blant annet fordi
filene fra september er fra før regel 18 hadde Utført-linjer. Sjekken leser bare i
går og i dag.

**Unntakene i lekkasjesjekken** står i `KJENTE_FILER` og `KJENTE_PLASSHOLDERE`,
med grunnen. En fil gjelder bare akkurat den stien, og en nøkkel bare akkurat den
verdien i akkurat den fila, ikke linjenummeret. Verdiene som ligner nøkler, er
skrevet i to deler, så sjekken ikke finner dem i skriptet selv. Testen sjekker at
hvert unntak fortsatt finnes i repoet, og at en ny `.json`-fil, en ekte verdi i en
kjent fil og en kjent verdi i en annen fil merkes, også i diffen det siste døgnet.

**Regel 20** teller commits der forfatteren (med `.mailmap`) er Marian Osen eller
Joakim Lund og den andre står som medforfatter. Merge-commits fra GitHub (to
foreldre og committer «GitHub») og commits fra andre enn gruppen vises for seg.

**Bildene.** Etter kveldsjobben 18.11 kl. 23:51–23:53 ble alle de 20 bildene i
`docs/appen/` tatt på nytt av demoen på grenen, etter flettingen av main
(`2516de61`), med skriptet og jobblista fra 9.19 og 9.21, på port 8922 og 8923,
med en ny demobase hver gang. De to rundene var like byte for byte. Tre er nye,
og de viser knappen ved notatet om BRFE fra 22.09: `notatene-brfe-demo.png`,
`notatene-min-liste-demo.png` og `mobil/notatene-brfe-390-demo.png`. Bare
teksten på knappen er endret. De andre 17 er byte for byte de samme, også
`slett-notatet-demo.png`, fordi spørsmålet alt het «Slett notatet, kjøpet og
salget». Avtrykkene er regnet ut på nytt, fordi `_notat.html` er med bak alle
bildene. Før og etter står på bildegrenen `pr-9-22-bilder` med en LESMEG.

**Testene lokalt** 18.11 og 19.11, én om gangen, på `f0f5abec`: `test_docker.py` 158,
`test_notater.py` 152, `test_morgensjekken_9_22.py` 13, `test_boersdager_9_22.py` 1,
`test_hjelpetekster.py` 54, `test_ryddighet.py` 36 og `test_ruff.py` 6, alle grønne.
`--dokumentene` ga 3085 grønne og 7 hoppet over (13 minutter). Hele settet kjøres i CI.

## Morgensjekken mot main, før og etter

Kjørt lokalt mot main på `e65692b3` med `2026-11-18T21:47` som tid: før med
skriptet på `origin/main` (`0c650e14`) kl. 21:45, og etter med skriptet på
grenen kl. 21:56. Resten av utskriften er lik.

| Del | Før | Etter |
|---|---|---|
| 2, dagsfilene | 17.11: 0 instruksjoner, 0 med Utført; 18.11: 0, 0 | 17.11: 12 instruksjoner og beskjeder, 12 med Utført; 18.11: 7, 5 med Utført, 1 limt inn på nytt, og «mangler Utført» for denne instruksjonen, som ikke var ferdig |
| 7, taggene | «ny tag: arbeidskrav-product-brief-v8» og «MERK: endring etter innleveringsfristen 27.09» | Bare «briefen er uendret siden arbeidskrav-product-brief-v8 (52023c9)» |
| 9, lekkasjesjekken | 4 filer som ikke skal være der og 12 mulige nøkler | 0 og 0 |
| 10, regel 20 | 219 med Joakim som medforfatter og 0 med Marian, av 222 | 219 av 219 av gruppens commits med den andre som medforfatter; 2 commits fra faglærer og 1 merge-commit fra GitHub for seg |
| Tittelen i saken | «17 ting å se på» | «alt i orden» |

Klokkeslettet i «HEAD paa GitHub» viste 20:44, ikke 21:44, lokalt i begge
kjøringene. `TZ` virker ikke for `git log` på Windows, og på GitHub kjører
skriptet på Linux. Det er ikke endret her.

## Gjennomgangen 18.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, uten git og pytest, på diffen kl. 22:07. 11 funn: 2 på middels og 9 lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | middels | En linje med etikett ga seksjonen den står under Utført, også når den bare nevner en annen (17.11: linja om PRD-en under kl. 22:50) | Rettet: linja gjelder der den står bare når den ikke nevner en annen klart. Testen med 17.11 og den konstruerte fila |
| ECH2 | middels | Samme «Limt inn kl.» i to seksjoner, og én linje dekket begge | Rettet: et delt klokkeslett gjelder den ene som ikke alt er nevnt, ellers «uklart». Klokkeslettet er seksjonens eget, ikke et senere «kl.» i overskriften |
| ECH3 | lav | Første ord var ofte vanlig («svarene»), og en dato ble tatt for et storynummer | Rettet: de vanlige ordene hoppes over, og storynummeret må stå som «story X.Y» |
| ECH4 | lav | «limt inn på nytt» alene var nok | Rettet: teksten må også si «ikke ført på nytt», ellers «uklart» |
| ECH5 | lav | En «## » i innlimt tekst utenfor en kodeblokk deler seksjonen | Står: slik er dagsfilene, og instruksjonen sier at hver «## » teller. Fra 11.11 står de innlimte tekstene i ```text-blokker |
| BH1 | lav | Docstringen sa fire .json-filer, men det er fem i lista | Rettet: fire nye og den fra 3.4b |
| BH2 | lav | «(faglaerer)» om alle utenfor gruppen | Rettet: «(faglaerer og andre)» |
| BH3 | lav | Kommentaren sa at alle overskriftene 10.11 har tekst etter klokkeslettet | Rettet: én er «## 11:20» alene |
| VG1 | lav | Den falske git så bort fra formatstrengen | Rettet: testen krever `%aN`, `%cn`, `%p` og medforfatterne |
| VG2 | lav | Unntakene ble ikke kjørt mot de ekte testfilene, og diffen bare med én fil | Rettet: del 9 på de fire ekte testfilene og de fem .json-filene gir 0, og en kjent verdi i en annen fil i diffen merkes |
| VG3 | lav | Ingen test viste at for mye ikke dekkes | Rettet: den konstruerte fila har et delt klokkeslett, en dato og et vanlig første ord |

Leseren fant ingen ekte nøkkel som slipper gjennom, ingen krasj, og at CRLF ikke gir
feil. «51 handelsdager» står fortsatt i en kommentar i `src/fetch_prices.py` og i
en docstring i `tests/test_fetch_prices.py`, men instruksjonen gjelder bare FR-101
og kilden.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Bilder bare av demoen, på en ledig port, aldri 8000, og uten ekte kurser.
- Ingen ny migrasjon. Den planlagte oppgaven «Morgensjekk OSE Signal» endres
  ikke.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.
- Pausene om kvelden gjelder: ingen pytest kl. 22:15–23:50, ingen git kl.
  22:10–22:20, 22:43–22:48, 23:13–23:18 og 23:43–23:48, og ingen fletting kl.
  22:10–23:58.

## Kontroll

- [x] Morgensjekken: dagsfilene, taggen, unntakene og regel 20, hver med en test som feiler før rettingen
- [x] Morgensjekken kjørt mot main før og etter, med utskriften her
- [x] «51 børsdager» i FR-101 og i kilden, med en linje i endringsloggen
- [x] Knappen har samme navn på aksjesiden og i spørsmålet, og bildene, avtrykkene og bildegrenen følger
- [x] Spørsmål 7 i 9.20, spørsmål 1 i 9.21 og punktene i `issues.md` har en datert linje: spørsmålene i `b99bd3f3`, og punktene i `issues.md` lukkes i loggen etter føringen på main
- [x] Gjennomgangen er tatt
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [x] CI er grønn i alle jobbene (run 44418120615 på `1557ff5e`, med 6002 bestått og 99 hoppet over i `pytest`)

## Flettet 19.11

CI var grønn i alle fire jobbene på head-en `1557ff5e` (run 44418120615). Ingen
funn på middels eller høy grad sto åpne (regel 25). PR #169 ble squash-flettet i
`7480e72c` 19.11 kl. 00:16, etter pausene om kvelden, låst til `1557ff5e`, uten
nytt ja. Bildegrenen `pr-9-22-bilder` er pushet (`dd395dc3`).
