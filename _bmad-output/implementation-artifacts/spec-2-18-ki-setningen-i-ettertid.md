---
title: 'Story 2.18: setningen om KI-teksten for en dag i ettertid bare med KI på'
type: 'bugfix'
created: '2026-11-16'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'b68ea82a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-17-signalet-regnet-i-ettertid.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-14-kontrollrunden-etter-v1-1.md'
---

Skrevet 16.11 i vinduet som kjørte kontrollrunden (9.14), etter steg 3 i
instruksjonen kl. 09:52 og svaret kl. 11:20, begge ført i
`docs/ai-prompts/2026-11-16.md`. Neste ledige nummer i Epic 2 etter 2.17 er
2.18. Worktreen `G74-lund-osen-2-18`, grenen `2-18-ki-setningen-i-ettertid`, fra
`origin/main` (`b68ea82a`), etter at PR #160 er flettet.

## Storyen

Som **bruker** vil jeg at aksjesiden ikke sier noe om KI når KI-teksten er slått
av, heller ikke for en dag med signalet regnet i ettertid, så bryteren gjør det
den sier.

**Oppfyller:** FR-601 · **Begrenses av:** FR-602, FR-607, spørsmål 7 i 2.17,
regel 19 og 22

**Avhenger av:** 2.17, 9.14. **Én økt:** ja.

## Svarene

*Svar 2026-11-16 kl. 09:51 (gruppens svar, rådet anbefalte det), spørsmål 1 i
`spec-9-14-kontrollrunden-etter-v1-1.md`:* rettes i dag i en egen liten story.
Setningen om KI-teksten for en dag i ettertid vises bare når KI er på, og kravet
i FR-601 står. Se etter samme mønster i de andre malene. Testene: med KI av har
aksjesiden for en dag i ettertid ingen melding om KI, og med KI på står
setningen som før.

*Svar 2026-11-16 kl. 11:20 (gruppens svar, rådet anbefalte det), spørsmålet om
forsiden:* vinduet spurte kl. 09:57 om storyen også skulle ta bort linja «KI-teksten
er slått av. Tabellen over viser bare det reglene har regnet ut.» under
«Børsdagen kort fortalt». Linja står, som valgt i 10.6, fordi boksen ellers ville
stå tom, med bare overskriften og bryteren. FR-601 får unntaket nå i 2.18: under
«Konsekvenser» har aksjesiden med KI av ingen melding om KI, og forsiden har
bryteren og den ene linja om at KI-teksten er slått av, med en linje i
endringsloggen (regel 19). 2.18 retter ellers bare setningen på aksjesiden, og
ingen nye bilder trengs.

## Det som var

I `src/templates/aksje.html` sjekkes `detalj.ettertid` før `ki_vises` i rammen
«Signalet forklart». For en dag i ettertid sto derfor setningen «Signalet for
denne dagen er regnet i ettertid. KI-teksten lages bare samme kveld som kursene
hentes, så dagen har ingen KI-tekst.» også med KI av. Funnet er B2 i 9.14.
Testen i 2.17 (`test_aksjesiden_for_dagen_sier_det_under_datoen_og_om_ki_teksten`)
så bare på siden med KI på, som er standard i testene.

## Endringen

- `src/templates/aksje.html`: setningen står bare når `ki_er_paa`. Med KI av
  står rammen med bryteren og linja om hva signalet bygger på, og ingen av
  appens setninger om dagene, som før (spørsmål 7 i 2.17). Linja under datoen om at signalet er regnet i
  ettertid står, fordi den ikke handler om KI.
- `prd.md`, FR-601, «Konsekvenser»: unntaket for forsiden, og en linje i
  `prd-endringslogg.md` (svaret kl. 11:20).
- Ingen endring i `src/app.py`, `src/ki_visning.py` eller de andre malene.

## De andre malene

Sett gjennom etter samme mønster: en melding om KI som står uten at
`ki_er_paa` eller `er_paa` er sjekket.

- `index.html`, «Børsdagen kort fortalt»: med KI av står `DAGEN_AV` fra
  `src/ki_visning.py`. Den står, etter svaret kl. 11:20.
- `aksje.html`: `dagene` og `samme_dag` er appens setninger og står med KI av,
  som valgt 25.10 og 05.11. «Laget av KI» og modellen står bare inne i
  `ki_vises`. Linja «Signalet bygger bare på kurs og volum i sjekkene over, ikke
  på KI-teksten …» står alltid.
- `boersometer.html`, `_notat.html`, `_brikker.html`, `innstillinger.html` og
  de andre: ingen melding om KI som avhenger av en dag i ettertid. Innstillinger
  har bryteren og forklaringen av den.
- Hjelpetekstene i `src/hjelpetekster.py` står med KI av og på, fordi de
  forklarer bryteren.

## Testene

I `tests/test_ettertid_2_17.py`, i `TestVisningen`, i begge versjonene:

- Med KI av har rammen «Signalet forklart» for en dag i ettertid ingen setning
  om KI-teksten, ingen `uten`-linje og ingen KI-tekst. Bryteren står, og linja
  under datoen står.
- Med KI på igjen står setningen som før.

Testen ble kjørt mot malen før rettingen og feilet der den skulle.

## Bildene

Bildene av aksjesiden i README-en er tatt av `/aksje/BRFE` i demoen, altså
siste børsdag, som har en kveldsrad, med KI på. Ingen av bildene viser en dag i
ettertid med KI av, så ingen bilder endres, og ingen nye lages.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke (regel 22).
- Lokalt bare testfilene storyen rører og `--dokumentene`. Hele settet kjøres
  i CI.
- Flettes uten nytt ja, låst til head-en, når CI er grønn og ingen funn på
  middels eller høy grad står åpne (regel 25), og bare før kl. 22:10.

## Kontroll

- [ ] Testen feiler mot malen før rettingen
- [ ] Testfilene storyen rører, består lokalt
- [ ] `--dokumentene` består lokalt
- [ ] CI er grønn i alle jobbene
- [ ] Gjennomgangen er tatt, og funnene er rettet eller står som spørsmål
