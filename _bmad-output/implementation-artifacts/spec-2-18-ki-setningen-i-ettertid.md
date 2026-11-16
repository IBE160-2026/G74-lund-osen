---
title: 'Story 2.18: setningen om KI-teksten for en dag i ettertid bare med KI på'
type: 'bugfix'
created: '2026-11-16'
status: 'done'
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
i FR-601 står. Steg 3 i instruksjonen kl. 09:52 legger til: se etter samme
mønster i de andre malene, og testene ser at aksjesiden for en dag i ettertid
med KI av ikke har noen melding om KI, og at setningen står som før med KI på.

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
- `tests/test_docker.py`: avtrykkene bak bildene, se «Bildene».

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
  forklarer rammen og bryteren. Det gjelder også steget «Signalet forklart» i
  «Vis meg rundt» (`STEGET_SIGNALET_FORKLART`), som sier at en dag i ettertid
  ikke har KI-tekst. Brukeren starter omvisningen selv, som «?», så den står.
- «Illustrasjon laget av KI» i `investorside.html` og `eodhd_demo.html` står
  uten bryteren. Den merker en tegning, ikke KI-teksten, og FR-601 gjelder
  aksjesiden og forsiden.

## Testene

I `tests/test_ettertid_2_17.py`, i `TestVisningen`, i begge versjonene:

- Med KI av har rammen «Signalet forklart» for en dag i ettertid ingen setning
  om KI-teksten, ingen `uten`-linje og ingen KI-tekst. Bryteren står, og linja
  under datoen står.
- Med KI på igjen står setningen som før.

Testen ble kjørt mot malen før rettingen kl. 11:48–11:50 (mellom `5bf104fd`
og `684bdd19`, etter `git log`), og feilet i begge versjonene på
`assert "ettertid-ki" not in ki`, med setningen i rammen. Etter rettingen besto
alle 39 testene i fila.

## Bildene

Bildet av aksjesiden i README-en viser, etter alt-teksten i `README.md`,
setningene om dagene og om samme dag og KI-teksten. De står bare med KI på og
for en dag som ikke er regnet i ettertid (`_setningene_om_dagen` i
`src/app.py`). Ingen av bildene viser en dag i ettertid med KI av, så ingen
bilder endres, og ingen nye lages. Svaret kl. 11:20 sier det samme.

Avtrykkene bak bildene i `tests/test_docker.py` regnes av malene, så
kommentaren og vilkåret i `aksje.html` ga nye avtrykk for aksjesidebildet og 16
av bildene. `--dokumentene` fant det (2963 bestått, 3 feilet og 7 hoppet over,
kl. 11:50–12:09). Alle de 18 bildene ble tatt på nytt kl. 12:10–12:11 fra
demobasen i en midlertidig mappe, med demoserveren på en ledig port (ikke 8000)
og skriptet og jobblista fra 2.17. Alle er byte for byte like bildene i
repoet, så bare avtrykkene er satt på nytt, med en kommentar (`856432ac`).

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke (regel 22).
- Lokalt bare testfilene storyen rører og `--dokumentene`. Hele settet kjøres
  i CI.
- Flettes uten nytt ja, låst til head-en, når CI er grønn og ingen funn på
  middels eller høy grad står åpne (regel 25), og bare før kl. 22:10.

## Gjennomgangen 16.11

Én leser gikk gjennom diffen `b68ea82a..0dd12b08` med tre linser (Blind Hunter,
Edge Case Hunter og Verification Gap), bare med lesing, mens `--dokumentene`
kjørte. Leseren hadde ikke skrevet rettingen. Gjennomgangen ga 9 funn, alle
lave, og ingen på middels eller høy grad. 8 er rettet, og 1 står.

- **BH1:** testen så etter linja under datoen bare med KI av. Den ser nå også
  etter linja med KI på igjen.
- **BH2:** en tom linje for mye foran 2.18 i `epics.md`.
- **BH3 (står):** FR-601 og kommentaren i malen sier at aksjesiden med KI av
  ikke har noen melding om KI, men bryteren heter «Vis KI-tekst», og linja
  «Signalet bygger bare på kurs og volum i sjekkene over, ikke på KI-teksten
  …» står alltid. Ordlyden i FR-601 er den fra svaret kl. 11:20 og sto før
  2.18. Bryteren og linja om grunnlaget er ikke meldinger om KI-teksten for
  dagen, så teksten står.
  *Svar 2026-11-16 kl. 15:37 (gruppens svar, rådet anbefalte det):* FR-601
  presiseres. Med KI av står bryteren «Vis KI-tekst» og linja om hva signalet
  bygger på, som før, og ellers har aksjesiden ingen KI-tekst og ingen melding
  om KI. Presiseringen og linja i endringsloggen for PRD-en er ført på main.
  Kommentaren i malen står, fordi ingen kode endres.
- **ECH1:** steget «Signalet forklart» i «Vis meg rundt» er nevnt under «De
  andre malene».
- **ECH2:** «Illustrasjon laget av KI» er nevnt under «De andre malene».
- **VG1:** «Bildene» bygger nå på alt-teksten i README-en og på
  `_setningene_om_dagen`, ikke på en adresse uten kilde i repoet.
- **VG2:** kjøringen før rettingen er ført under «Testene», med tid og hvilken
  assert som feilet, og avkrysset.
- **VG3:** punktet om FR-601 i storyen i `epics.md` sier at det er PRD-en som
  sjekkes, ikke en test.
- **VG4:** «Svarene» skiller nå svaret kl. 09:51 fra det steg 3 i instruksjonen
  legger til.

Leseren fant logikken i malen i orden. Med KI av og en dag i ettertid står
ingen av grenene, og ingenting faller ned til `ki.grunn`. Testen kan ikke bestå
av feil grunn, fordi den krever 303 fra `/ki`, `aria-checked="false"`, linja
under datoen og rammen, og setningen igjen med KI på.

## Kontroll

- [x] Testen feiler mot malen før rettingen (kl. 11:48–11:50, begge versjonene)
- [x] Testfilene storyen rører, består lokalt (`tests/test_ettertid_2_17.py`, 39 bestått, og `tests/test_docker.py`, 158 bestått)
- [x] `--dokumentene` består lokalt (2966 bestått og 7 hoppet over, kl. 12:13–12:30 på `cb21c7d2`)
- [x] CI er grønn i alle jobbene (run 43858445935 på `b1fa8c50`, med 5865 bestått og 99 hoppet over i `pytest`)
- [x] Gjennomgangen er tatt, og funnene er rettet eller står med grunn (9 lave, 8 rettet og 1 står)
- [x] Bildene er tatt på nytt og er byte for byte de samme (kl. 12:10–12:11)

## Flettet 16.11

CI var grønn i alle fire jobbene på head-en `b1fa8c50` (run 43858445935). Ingen
funn på middels eller høy grad sto åpne (regel 25). PR #161 ble squash-flettet
i `05bc46e7` kl. 12:36, låst til `b1fa8c50`, uten nytt ja, slik steg 3 i
instruksjonen kl. 09:52 sier, før kl. 22:10.
