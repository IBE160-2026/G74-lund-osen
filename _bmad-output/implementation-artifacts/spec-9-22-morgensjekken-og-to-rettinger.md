---
title: 'Story 9.22: morgensjekken uten falske alarmer, «51 børsdager» og ett navn på sletteknappen'
type: 'code'
created: '2026-11-18'
status: 'in-progress'
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

- [ ] Morgensjekken: dagsfilene, taggen, unntakene og regel 20, hver med en test som feiler før rettingen
- [ ] Morgensjekken kjørt mot main før og etter, med utskriften her
- [ ] «51 børsdager» i FR-101 og i kilden, med en linje i endringsloggen
- [ ] Knappen har samme navn på aksjesiden og i spørsmålet, og bildene, avtrykkene og bildegrenen følger
- [ ] Spørsmål 7 i 9.20, spørsmål 1 i 9.21 og punktene i `issues.md` har en datert linje
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
