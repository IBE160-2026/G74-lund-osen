---
title: 'Story 9.21: bildene av spørsmålet før sletting og lenken tilbake'
type: 'docs'
created: '2026-11-18'
status: 'done'
route: 'dispatch'
baseline_commit: '06523402'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-19-grensen-og-bildene.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3k-bildene-av-appen-i-readme.md'
---

Skrevet 18.11 i vinduet som bygde 9.20, etter instruksjonen om svarene i 9.20 og
bildene (limt inn kl. 11:51 i `docs/ai-prompts/2026-11-18.md`) og gruppens svar
17.11 kl. 22:18 på spørsmål 1 i 9.19. Rådet anbefalte svarene kl. 11:49 18.11.
Neste ledige nummer i Epic 9 etter 9.20 er 9.21. Worktreen er
`G74-lund-osen-9-21`, på grenen `9-21-bildene-av-he2-og-he14`, fra `origin/main`
(`06523402`). Brukertest 2 er tidligst fredag 20.11.

## Storyen

Som **den som leser README-en før brukertest 2** vil jeg se spørsmålet før et
notat slettes og lenken tilbake i «Signalet dag for dag», så rettingene fra 9.18
synes der appen vises fram.

**Oppfyller:** spørsmål 1 i 9.19 (svaret 17.11 kl. 22:18) · **Begrenses av:**
regel 3, 16, 19 og 22; ingen kode i `src/` og ingen ny migrasjon

**Avhenger av:** 9.18, 9.19. **Én økt:** ja.

## Det som gjøres

1. To nye bilder av demoen i full bredde, slik 3.3k og 9.19 gjorde: spørsmålet
   før et notat slettes (HE2), og lenken tilbake ved månedspilene i «Signalet dag
   for dag» når en eldre måned er valgt (HE14). Demobasen i en midlertidig mappe
   og serveren på en ledig port, aldri 8000.
2. Bildene legges i `docs/appen/` og vises i README-en der de hører hjemme: ved
   notatene og ved aksjesiden, med alt-tekst og en kort tekst under, som de
   andre bildene.
3. Rekkefølgen i «Mappestruktur», avtrykkene og testene som sjekker bildene i
   README-en, følger med. README-en viser fortsatt ingen bilder fra mobil
   (svaret 17.11 kl. 18:26).
4. Bildene legges også på en egen bildegren, som før.
5. Spørsmål 1 i spesifikasjonen for 9.19 og punktet i `issues.md` får en datert
   linje om at bildene er lagt inn.

## Bygget

Bygget 18.11 av én agent i worktreen, og kontrollert i vinduet: begge bildene er
sett på, og de viser bare demoen.

| Del | Commit |
|---|---|
| `docs/appen/signalet-dag-for-dag-demo.png` (1280 × 977, BRFE i september 2026 med «Til oktober 2026») og `docs/appen/slett-notatet-demo.png` (1280 × 640, spørsmålet før notatet om BRFE fra 22.09 slettes, med kjøpet og salget), README-en, «Mappestruktur» og testene i `tests/test_docker.py` | `ed20b85e` |
| Bildegrenen `pr-9-21-bilder`, pushet | `a8c66c70`, `c59effdd` |

- Begge bildene er tatt to ganger med ny demobase, på port 62991 og 62992, og var
  like byte for byte. Spørsmålet før sletting nås med en POST, så skriptet
  klikker «Slett» og venter på den nye siden.
- I README-en står lenken tilbake rett etter aksjesiden, og spørsmålet før
  sletting rett etter notatene. README-en viser ingen bilder fra mobil.
- Siden med spørsmålet har ingen steg i omvisningen, som investorsiden, så
  raden øverst har ikke «Vis meg rundt». Det er appen slik den er.
- Bildet av «Signalet dag for dag» er et utsnitt uten demolinja. Selskapet er
  oppdiktet, og alt-teksten og teksten under sier at det er demoen
  (gjennomgangen, ECH4).

## Gjennomgangen 18.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `db6bc792`. 10 funn: 1 på middels og 9 lave. Avtrykkene og
«Mappestruktur» er regnet ut på nytt av leseren og stemmer.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | middels | Feilmeldingen for å ta slettebildet på nytt viste til toppen av `/aksje/BRFE`, men spørsmålet nås bare med en POST | Rettet: `SLIK_NAAS_BILDET` sier hvordan begge bildene tas (`d5b3cafe`) |
| BH1, ECH2 | lav | «etter «Slett»» stemte ikke med knappen ved notatet, «Slett notatet og det tenkte kjøpet» | Rettet i README-en, testen og LESMEG (`1229e3c7`, `c59effdd`) |
| BH2 | lav | «som sier» i alt-teksten pekte på notatet, ikke spørsmålet | Rettet (`1229e3c7`) |
| BH3 | lav | Kommentaren om rekkefølgen nevnte ikke de nye bildene | Rettet (`d5b3cafe`) |
| BH4 | lav | En sti var brutt over to linjer i spesifikasjonen for 9.19 | Rettet (`7db19167`) |
| BH5 | lav | LESMEG brukte navnene uten `etter-`, og bildegrenen var ikke pushet | Rettet, og pushet (`c59effdd`) |
| ECH3 | lav | Knappen heter «Slett notatet og det tenkte kjøpet» på aksjesiden og «Slett notatet, kjøpet og salget» på spørsmålet | Står: det er appen fra 9.18, og koden endres ikke her. Spørsmål 1 |
| ECH4 | lav | Bildet av «Signalet dag for dag» har ingen demolinje | Står: selskapet er oppdiktet, og teksten sier det (`7db19167`) |
| VG1 | lav | Tekstfeltene i PNG-filene testes bare for to bilder, og faktaene i alt-tekstene ikke | Står: fantes før 9.21, og de nye bildene er sjekket for hånd |

## Spørsmål til gruppen, med forslag

1. **To navn på knappen ved et notat med kjøp og salg (ECH3).** På aksjesiden
   heter den «Slett notatet og det tenkte kjøpet», og på spørsmålet «Slett
   notatet, kjøpet og salget». *Forslag:* knappen på aksjesiden sier det
   samme som spørsmålet når salget er notert, i en senere story der koden kan
   endres. Det endrer ikke brukertest 2.
   *Svar 2026-11-18 (gruppens svar, instruksjonen kl. 21:41):* knappen rettes i dag,
   før brukertest 2. Rådet anbefalte å vente til etter testen, og gruppen valgte i dag.
   *Lagt til 2026-11-18 (story 9.22):* knappen ved et notat med kjøp og salg heter
   «Slett notatet, kjøpet og salget» på aksjesiden og i Min liste, som i spørsmålet
   (`1185c652`).

## Grenser

- Ingen API-kall, `data/` og `_privat/` røres ikke, og den ekte versjonen
  startes ikke. Ingen ekte kurser i bildene.
- Lokalt kjøres bare testfilene storyen rører, og `--dokumentene`, og utfallet
  sjekkes før hver push.

## Kontroll

- [x] To nye bilder fra demoen, tatt to ganger og like byte for byte
- [x] Vist i README-en ved notatene og ved aksjesiden, med alt-tekst og tekst under
- [x] Rekkefølgen, avtrykkene og testene følger med, og bildegrenen er laget
- [x] Spørsmål 1 i 9.19 har linja om bildene, og `issues.md` får den i føringen på main
- [x] Gjennomgangen er tatt
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: `--dokumentene` på `a858fe63` kl. 12:44–13:05, med 3070 bestått og 7 hoppet over, etter én kjøring som ble stoppet for lite minne
- [x] CI er grønn i alle jobbene (run 44300672153 på `a858fe63`, med 5987 bestått og 99 hoppet over i `pytest`)

## Flettet 18.11

CI var grønn i alle fire jobbene på head-en `a858fe63` (run 44300672153). Ingen
funn på middels eller høy grad sto åpne (regel 25). PR #168 ble squash-flettet i
`0c2ab7d2` kl. 13:11, låst til `a858fe63`, uten nytt ja. Bildegrenen
`pr-9-21-bilder` er pushet (`c59effdd`).
