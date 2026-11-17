---
title: 'Story 9.16: flere brukerreiser i PRD-en'
type: 'docs'
created: '2026-11-17'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'ba866204'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd-endringslogg.md'
---

Skrevet 17.11, etter at appen ble bygget, i vinduet som bygde 9.15, etter steg 1
i instruksjonen etter gruppens svar 16.11 kl. 20:22 (design og UX før brukertest
2), ført i `docs/ai-prompts/2026-11-16.md`. Rådet anbefalte det. Instruksjonen
kl. 21:50 om ikonene ble gjort ferdig først, med flettingen av #162 og
ryddingen. Neste ledige nummer i Epic 9 etter 9.15 er 9.16. Worktreen er
`G74-lund-osen-9-16`, på grenen `9-16-flere-brukerreiser`, fra `origin/main`
(`ba866204`).

## Storyen

Som **gruppe** vil vi at §1 i PRD-en har flere brukerreiser enn UJ-1, slik at
brukertest 2 og vurderingen kan se hvem appen er for også utenfor hovedflyten.

**Oppfyller:** steg 1 i instruksjonen etter svaret 16.11 kl. 20:22 ·
**Begrenses av:** regel 3, 11, 19 og 20

**Avhenger av:** 2.18, 8.21, 8.27, 9.11. **Én økt:** ja.

## Svaret

*Svar 2026-11-16 kl. 20:22 (gruppens svar, rådet anbefalte det):* §1 i PRD-en
får én eller to brukerreiser til, i samme form som UJ-1: en person, stegene,
Climax, Edge, kravene reisen hviler på og suksessmålet som måler den. Forslaget
er Min liste med notater for en som kommer tilbake, og KI av og på. Bare det
appen gjør på main tas med, og hvert steg sjekkes mot malene og testene. Det
samlede UX-dokumentet tas senere, med `/goal`, som gruppen starter selv.

## Det som skrives

- **§1 i `prd.md`:** to nye avsnitt etter «Brukerreisen UJ-1», med hver sin
  overskrift, «Brukerreisen UJ-2» (Min liste med notater) og «Brukerreisen
  UJ-3» (KI-teksten av og på), i samme form som UJ-1. Overskriften for UJ-1 står
  urørt, fordi `test_brukerreisen_og_ordlista` i `tests/test_prd_9_11.py` deler
  teksten ved den. `prd.md` har ingen «Lagt til»-linjer eller storynumre
  (`test_prd_9_11.py`), så at reisene er skrevet 17.11, etter at appen ble
  bygget, står i endringsloggen og her.
- **`prd-endringslogg.md`:** én datert linje under «Endringer etter 12.11»
  (regel 19).
- `updated` i begge filene settes fra `date` (regel 4).
- Ingen kode og ingen maler endres. Ingen nye krav: reisene hviler på krav
  som finnes.
- Etter gjennomgangen to tester: `test_sjekkortene_er_like_med_ki_av_og_paa`
  i `tests/test_ki_visning.py::TestSiden` låser climax i UJ-3 (VG1), og
  `test_brukerreisene_har_samme_form` i `tests/test_prd_9_11.py` låser formen
  på UJ-1–UJ-3 (VG9). Den første feilet mot en mutant der sjekkortene fikk
  et ekstra element med KI på, og malen ble satt tilbake etterpå.

## Sjekken mot main

Slått opp på `ba866204`, først av én leser med bare lesing og så kontrollert i
vinduet: hvert testnavn under finnes, og malstedene er lest. Personene Sindre og
Ingrid er oppdiktet og står ikke andre steder i `docs/`, `_bmad-output/` eller
README-en.

**UJ-2, Min liste med notater**

| Steget | Malen eller koden | Testen |
|---|---|---|
| «Min liste» med overskriften om de merkede som skilte seg ut | `index.html` (`h1` med «i Min liste»), ruten `/min-liste` i `app.py` | `test_min_liste.py::TestSidene::test_min_liste_har_overskriften_teksten_og_knappen_med_antallet` |
| «Mine notater» nederst, alle notatene, den nyeste først, navnet som lenke | `index.html` («Alle notatene dine, den nyeste først. …»), `_notat.html` | `test_notater.py::TestMinListe::test_alle_notatene_samlet_nyeste_foerst_med_lenke` |
| «Etterpå»: aksjen og hovedindeksen fra notatdagen til siste børsdag, og signalet begge dagene | `_notat.html` (`etterpaa`) | `test_notater.py::TestSiden::test_etterpaa_paa_siden` og `::TestSiden::test_samme_tall_som_basen` |
| Et tenkt kjøp som er solgt, når sluttkursen etter salget er hentet: salgsdagen, sjekkene da salget ble notert, aksjen og hovedindeksen fra kjøpet til salget | `_notat.html` («Tenkt kjøp og salg», «Salgsdag …», «Aksjen fra kjøpet til salget:») | `test_notater.py::TestDemoen::test_eksemplene_har_tall_og_ett_aapent_og_ett_avsluttet_kjoep` |
| Nytt notat på aksjesiden | `aksje.html` («Notatet får datoen …», «Lagre notatet») | `test_notater.py::TestSkjemaet::test_notatet_faar_dagen_siden_viser` |
| Knappen og panelet «Mine notater» på en bred skjerm | `_ramme.html`, `_notatpanel.html` | `test_notatpanel_8_27.py::TestKnappen::test_etter_min_liste_med_ikon_paa_hver_side` og `::TestPanelet::test_alle_notatene_nyeste_foerst_som_i_min_liste`; bredden i `::TestPanelet::test_skriptet_og_stilen` og `::TestPanelskriptetMedNode::test_bare_fra_1056_px_og_bare_aapent` |
| Climax: ingen dom over notatet | `innstillinger.html` («Appen sier aldri om noe var riktig.») | `test_notater.py::TestSiden::test_ingen_ord_om_riktig_eller_galt_og_ingen_raad`, `::TestBryteren::test_bryteren_staar_i_innstillinger_med_hjelpen` og `::TestEtterGjennomgangen::test_ingen_raad_i_tekstene_for_grunnene` |
| Edge: notat fra siste børsdag | `_notat.html` («Ingen børsdager med kurs etter notatdagen ennå.») | `test_notater.py::TestEtterGjennomgangen::test_siste_dag_sier_at_det_ikke_er_dager_etter` |
| Edge: «Vis notater» av | `innstillinger.html`, `_ramme.html`, `index.html` og `aksje.html` | `test_notater.py::TestBryteren::test_av_skjuler_notatene_og_sletter_ingenting` og `test_notatpanel_8_27.py::TestKnappen::test_borte_naar_bryteren_er_av` |

Linja for et tenkt kjøp som ikke er solgt, har ingen test mot siden, så den er
ikke med i reisen.

**UJ-3, KI-teksten av og på**

| Steget | Malen eller koden | Testen |
|---|---|---|
| De tre sjekkene under «Hvorfor signalet ble 3», uten betingelse på KI | `aksje.html` | `test_ki_visning.py::TestSiden::test_regelforklaringen_staar_alltid` (overskriften) |
| KI på: «Signalet forklart», appens setninger, «Laget av KI» og modellen | `aksje.html` (`ki-del`, `merke-ki` og `modell`) | `test_ki_visning.py::TestSiden::test_ki_teksten_under_regelforklaringen` |
| Bryteren «Vis KI-tekst» ved teksten | `aksje.html` (`ki-bryter`), ruten `/ki` i `app.py` | `test_ki_visning.py::TestSiden::test_med_ki_av_ingen_ki_tekst_og_bryteren_sier_vis`, `test_demo_ki.py::TestAksjesiden::test_knappen_skjuler_og_viser_teksten` og `test_innstillinger_ki.py::TestSammeValg::test_bryteren_ved_teksten_slaar_av_innstillinger` |
| KI av: bryteren, appens setninger og linja om grunnlaget står | `aksje.html` (`dagene`, `samme-dag` og `grunnlaget`) | `test_aksjesiden_8_20a.py::TestBunnen::test_linja_nederst_i_rammen_og_ingen_fotnote_to_ganger`, `test_ki_visning.py::TestSetningenOmSammeDag::test_ogsaa_med_ki_av` og `test_ki_visning.py::TestSiden::test_med_ki_av_er_siden_lik_med_og_uten_rad` |
| Innstillinger viser samme verdi | `innstillinger.html` | `test_innstillinger_ki.py::TestSammeValg::test_bryteren_ved_teksten_slaar_av_innstillinger` og `::test_innstillinger_slaar_av_bryteren_ved_teksten` |
| Forsiden med KI av: bryteren og én linje under «Børsdagen kort fortalt» | `index.html`, `DAGEN_AV` i `ki_visning.py` | `test_ki_dagen.py::TestForsiden::test_bryteren_slaar_av_begge_ki_tekstene` |
| KI på igjen ved teksten på aksjesiden | `aksje.html`, ruten `/ki` | `test_demo_ki.py::TestAksjesiden::test_knappen_skjuler_og_viser_teksten` |
| Climax: sjekkortene er de samme med KI av og på | `aksje.html` (`sjekkort-rad`) | `test_ki_visning.py::TestSiden::test_sjekkortene_er_like_med_ki_av_og_paa`, lagt til etter gjennomgangen (VG1) |
| Edge: i den ekte versjonen, for siste børsdag uten KI-tekst for noen aksje, ingen språkmodell, med lenken «Slik slår du den på» | `index.html`, `DAGEN_UTEN_MODELL` i `ki_visning.py` | `test_ki_dagen.py::TestForsiden::test_uten_rad`, og for aksjesiden `test_ki_visning.py::TestSiden::test_en_dag_uten_rad_sier_det` |

**Demoen.** Begge reisene kan vises i demoen. Den merker fem aksjer, har fire
oppdiktede notater med ett solgt og ett åpent tenkt kjøp, og har KI-tekster for
siste demodag (`src/demo.py`,
`test_notater.py::TestDemoen::test_notatene_samlet_i_min_liste_i_demoen` og
`test_demo_ki.py::TestAksjesiden::test_viser_teksten_med_merket_og_modellinja`).
Edgen i UJ-3 kan ikke vises i demoen, som sier «Dagen er uten KI-tekst.» uten
lenken.

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet, og alt er skrevet etter forslaget. Spørsmål
1 og 3 er BH1 i gjennomgangen, på middels og fra svaret, så PR-en flettes ikke
før gruppen har svart (regel 25).

1. **Suksessmålet for UJ-2 (BH1, middels).** Ingen SM måler reisen. Som
   skrevet sier PRD-en at SM-2 er det nærmeste, men at den måler at gruppen
   bruker appen, ikke reisen. *Forslag:* et nytt SM-10 for brukertest 2: en
   person utenfor gruppen finner et notat i Min liste og sier hva aksjen og
   hovedindeksen gjorde etterpå, minst 1 person, uten hjelp, før innleveringen,
   med FR-110, FR-111 og FR-203. Det andre valget er at teksten står som nå.
2. **«Sjekkene er de samme» hadde ingen direkte test.** *Rettet etter
   gjennomgangen (VG1):* `test_sjekkortene_er_like_med_ki_av_og_paa` låser
   det nå, i denne storyen. Spørsmålet er besvart av rettingen.
3. **Suksessmålet for UJ-3 (BH1, middels).** Som skrevet sier PRD-en at SM-8
   er det nærmeste, men at den måler kontrollen og loggen av KI-teksten, ikke
   vekslingen. *Forslag:* et nytt SM-11 for brukertest 2: en person utenfor
   gruppen slår KI-teksten av og på og sier at signalet og sjekkene er de samme,
   med FR-601, FR-602 og FR-706. Det andre valget er at teksten står som nå.
4. **UJ-1 nevnes alene i «Kort fortalt» og under §7.** *Forslag:* de står,
   fordi UJ-1 er hovedflyten som SM-1 og SM-6 måler.
5. **Lavt, utenfor PRD-en:** docstringen i
   `test_demo_ki.py::TestAksjesiden::test_knappen_skjuler_og_viser_teksten`
   nevner «Skjul KI-teksten» og «Vis KI-teksten», mens bryteren heter «Vis
   KI-tekst». *Forslag:* rettes neste gang fila endres.

## Gjennomgangen 17.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `32885761`. 24 funn: 6 på middels og 18 lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| BH1 | middels | SM-2 og SM-8 måler ikke reisene, og kravene deres mangler noen av kravene reisene hviler på | **Står åpent, følger av svaret (regel 25).** Svaret ba om suksessmålet som måler reisen, og ingen SM gjør det. Teksten sier nå at SM-2 og SM-8 er de nærmeste. Spørsmål 1 og 3 |
| ECH1 | middels | «Hvorfor signalet ble 3» gjelder ikke enhver aksje som skiller seg ut, fordi grensen er 2 | Rettet: «en aksje med 3 av 3», som UJ-1 |
| ECH2 | middels | Edgen i UJ-3 gjelder bare den ekte versjonen, siste børsdag og når ingen aksje har KI-tekst | Rettet: forbeholdene står i Edgen |
| ECH3 | middels | Kravene for UJ-2 dekker ikke «Etterpå» og de tenkte kjøpene | Rettet: «Notatene med «Etterpå» og de tenkte kjøpene har ikke eget FR (§2).» |
| VG1 | middels | Ingen test låste climax i UJ-3 | Rettet: `test_sjekkortene_er_like_med_ki_av_og_paa`, prøvd mot en mutant |
| VG2 | middels | «Begge tekstene er tilbake» hadde ingen test for oversikten | Rettet: steget gjelder aksjesiden, med testen i tabellen |
| BH2 | lav | Tre navn på forsiden | Rettet: «oversikten», som UJ-1 |
| BH3 | lav | «Sjekkene står som før» uten sted i Edgen | Rettet: «På aksjesiden» |
| BH4 | lav | «begge tekstene» var uklart | Rettet sammen med VG2 |
| BH5 | lav | «tenkt kjøp» uten innføring, og bare sjekkene ved salget | Står: «tenkt kjøp» står i §2 og på siden, og reisen viser det som er låst av testene |
| BH6 | lav | Edgen i UJ-2 har to tilfeller | Står: begge er kanttilfeller for samme reise |
| BH7 | lav | «Kort fortalt» nevner bare UJ-1 | Står: spørsmål 4 |
| BH8 | lav | «i et panel ved siden av siden» | Står: ordlyden er fra FR-111 |
| ECH4 | lav | «Etterpå» regnes til siste dag med kurs | Rettet |
| ECH5 | lav | Salgsdagen står først når sluttkursen er hentet | Rettet |
| ECH6 | lav | Panelet åpnes bare med skript og fra 1056 px | Står: «på en bred skjerm», og testene for bredden står i tabellen |
| ECH7 | lav | Overskriften i Min liste avhenger av at en merket aksje er vurdert | Står: reisen gjelder en dag med vurdering |
| VG3 | lav | Testen for bryteren går ikke via `/ki` | Rettet: to tester til i tabellen |
| VG4 | lav | Testen for en dag i ettertid låser ikke steget | Rettet: tatt ut av raden |
| VG5 | lav | Climax i UJ-2 manglet testen for teksten i Innstillinger | Rettet: to tester til i tabellen |
| VG6 | lav | Testene for «Etterpå» leser aksjesiden | Står: samme makro i Min liste |
| VG7 | lav | Bredden for panelet sto ikke i tabellen | Rettet |
| VG8 | lav | Knappen og panelet med «Vis notater» av | Rettet: testen står i tabellen |
| VG9 | lav | Ingen test holdt UJ-2 og UJ-3 i samme form | Rettet: `test_brukerreisene_har_samme_form` |

## Grenser

- Bare det appen gjør på main nå. Står noe i PRD-en som malene ikke gjør, eller
  omvendt, blir det et spørsmål med forslag, ikke en endring.
- Ingen kurser, volum eller navn på testpersoner (regel 16). Personene i reisene
  er oppdiktet.
- Reisene skrives ikke som om de var laget før koden.

## Kontroll

- [x] UJ-2 og UJ-3 i §1, i samme form som UJ-1
- [x] Hvert steg sjekket mot malene og testene, med kilde i tabellen
- [x] Linja i endringsloggen
- [x] Diff mot HEAD etter omskrivingen, uten krav som er borte (regel 13): bare `updated` er endret i det som sto
- [x] Gjennomgangen er tatt
- [x] `--dokumentene` er grønn lokalt: på `248d71ce` kl. 12:04–12:23, med 2970 bestått og 7 hoppet over. Første kjøring kl. 11:54 ble stoppet for lite minne og startet igjen
- [ ] CI er grønn i alle jobbene
