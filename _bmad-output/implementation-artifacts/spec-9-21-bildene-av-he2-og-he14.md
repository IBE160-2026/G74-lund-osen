---
title: 'Story 9.21: bildene av spørsmålet før sletting og lenken tilbake'
type: 'docs'
created: '2026-11-18'
status: 'in-progress'
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
| Bildegrenen `pr-9-21-bilder` | `a8c66c70` |

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
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
