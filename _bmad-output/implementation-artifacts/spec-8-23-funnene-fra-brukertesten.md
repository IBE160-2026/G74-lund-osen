---
title: 'Story 8.23: funnene fra brukertesten 10.11 (del A)'
type: 'feature'
created: '2026-11-10'
status: 'done'
route: 'dispatch'
baseline_commit: '86d1fe4f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

Skrevet 10.11 etter instruksjonen «Del A, funnene fra brukertesten 10.11» (lest kl. 21:31), med tillegget om overskriften i Min liste (gruppens funn kl. 14:15), tillegg 2 (gruppens svar kl. 14:53 og 14:59), tillegg 3 (gruppens svar kl. 15:54) og tillegget om demoen (gruppens svar kl. 15:57). Alt føres ordrett i `docs/ai-prompts/2026-11-10.md` når instruksjonen har Utført-linje. Bygget fra main (`86d1fe4f`), på grenen `8-23-funnene-fra-brukertesten`, i worktreen `G74-lund-osen-8-23`. 8.21 og 8.22 er tatt av de åpne PR-ene #139 og #138, så 8.23 er neste ledige nummer i Epic 8.

*Svar 2026-11-10 kl. 13:54 (gruppens svar):* «ja» til del A og B. Rådet anbefalte det.

*Svar 2026-11-10 kl. 14:15 (gruppens funn), 14:53 og 14:59 (gruppens svar), 15:54 og 15:57 (gruppens svar):* tilleggene 1, 2 og 3 og tillegget om demoen er en del av del A. Rådet anbefalte alle.

Grensene i appen som styrer delene: `src/static/hjelp.js` er det eneste skriptet, og testene krever det (`test_app.py`, `test_hjelpetekster.py`, `test_aksjesiden_8_20a.py`), så alt annet er lenker og skjemaer. Hver endring i `stil.css` eller `hjelp.js` gir nye avtrykk for alle bildene i `docs/appen/`. Demoen har vurderinger fra 21.09 til 09.10 og ingen ventende endringer i lista.

## Spørsmål til gruppen

Forslaget er det som bygges. Spørsmålene står åpne til gruppen har svart.

1. **«Dine egne aksjer» (A1).** Radene er en liste med navn, symbol og bransje i teksten. *Forslag:* en tabell i samme `tabellboks` som tabellen over, med samme rad, skrift og skillelinje, bransjeikonet i en egen liten celle foran navnet, og status og knappen i hver sin kolonne. Kursene står fortsatt i tabellen over; denne lista er for å følge og fjerne.
2. **Sorteringen (A2).** Lenkene i kolonneraden har ikke noe anker, så siden hopper til toppen. *Forslag:* `#aksjene` på sorteringslenkene, «Standard rekkefølge» og filterknappene, uten skript.
3. **«?» (A3).** *Forslag:* et nytt trykk på samme «?» lukker hjelpen, både i sidefeltet og under knappen på smal skjerm, i `hjelp.js`. Uten skript gjør nettleseren det selv (`popovertarget` veksler).
4. **Små ruter i børsometeret (A4).** I dag viser de minste rutene bare fargen, og de nest minste bare symbolet. *Forslag:* ruter som har plass til symbolet, viser også endringen og styrken i liten skrift («-1,7 %», «2/3»), og alle rutene har en `title` med symbolet, endringen og styrken, så musa viser det også på de minste. Forklaringen «Rammen» sier at ringen rundt styrken gjelder siste børsdag, og at den tykke rammen rundt ruta er gul ved 3 av 3 og mørk ved 2 av 3.
   *Rettet 2026-11-10 (gjennomgangen, BH3 og ECH3):* de minste rutene som har symbolet, viser endringen i liten skrift, og styrken står i lappen ved musa der den ikke får plass. Styrken på nivå 2 skjules igjen uten `styrke-N`, som svaret 04.11 kl. 19:21 sa, så en gul ramme en annen dag aldri står med en annen styrke uten merket.
5. **«Volum mot vanlig» med to desimaler (A4).** I dag står flere desimaler når to ville rundet over en grense (1,4996 vises ikke som 1,50). *Forslag:* alltid to desimaler, og et tall like under en grense rundes ned mot den siden det står på (1,4996 blir 1,49), så tallet og ordet (vanlig, høyt, lavt) aldri sier ulikt.
   *Rettet 2026-11-10 (gjennomgangen, BH11 og ECH5):* tallet flyttes bare når ordet for det viste tallet ellers ville blitt et annet enn ordet for målingen: 1,5004 blir 1,51 og 0,998 blir 0,99, mens 1,4996 står som 1,50 (vanlig) og 1,0004 som 1,00 (vanlig).
6. **«Se tallene som tabell» (A5 og tillegg 3).** *Forslag:* tabellen står åpen fra start, og knappen, som ser ut som de andre knappene, lukker den. Tabellen har stilen til tabellen på oversikten og beholder bransjeradene. «?» ved «Endring» og «Volum mot vanlig». Hjelpen ved volumet sier lavt under 1, vanlig fra 1 til 1,5 og høyt over 1,5 (`VOLUMFAKTOR`), og hjelpen ved bransjeraden sier at snittet er gjennomsnittet av endringen for aksjene i bransjen som har kurs, uten vekt. Svaret 26.10 kl. 15:21 (f) får Rettet-linje i epics.md.
7. **Oransje i Innstillinger (A6).** Designreglene sier at sterk oransje står på blekk. *Forslag:* bryteren er oransje når den er på, med svart knott, også KI-bryteren på aksjesiden og bryteren for dagens tekst, og siden man er på har oransje kant og strek i toppen, som er blekk. designregler.md får regelen som Lagt til-linje.
8. **Kallene på «Følg en aksje» (A7).** *Forslag:* 20, 1 kall per aksje, taket og «Med N aksjer er M kall igjen» regnes av `KVOTE`, `TAK`, `INDEKSKALL` og lista, ikke skrevet for hånd.
9. **Filteret «3 av 3» (A8).** *Forslag:* knappene har antallet i parentes, for eksempel «3 av 3 positiv (2)». Gir filteret 0, står «Ingen fikk 3 av 3 positiv. 3 fikk 2 av 3 positiv: se dem.», og lenken viser dem som fikk 2 av 3 i samme retning, med samme periode og sortering.
10. **Overskriften i Min liste (tillegg 1).** *Forslag:* med «Alle» står «10 av 15 skilte seg ut mandag, 6 av dem i Min liste», og med «Min liste» som før, «6 av 9 i Min liste skilte seg ut mandag».
11. **0-brikken (tillegg 2).** *Forslag:* «Slik leser du tabellen» viser +1, 0 og -1, med 0 hvit med kant som i tabellen.
12. **Teksten under kursgrafen (tillegg 2).** *Forslag:* først én kort setning i vanlig størrelse om linjene og tegnene, og resten bak «Mer om grafen» (`details`), med de samme setningene som nå. Bygges etter at #134 og #135 er flettet; de er flettet.
13. **«Signalet forklart» (tillegg 2).** *Forslag:* «13 av de 15 aksjene i lista steg og 2 falt», med antallet i lista den dagen.
14. **Endringer som venter (tillegg 2).** *Forslag:* når en endring i lista venter på hentingen etter kl. 22, står en kort linje øverst på oversikten og i Min liste: «N endringer i lista tas i bruk ved hentingen etter kl. 22.» I demoen står den med «Eksempeltall» og sier at demoen ikke henter, så endringene ikke tas i bruk der.
   *Rettet 2026-11-11 (story 8.26, tillegg 19, gruppens svar kl. 22:17):* eksempelboksen som sto i demoen når ingen endring ventet, er tatt bort, fordi den forklarte noe som ikke skjer. En endring som venter, står som før, også i demoen.
15. **3 av 3 det siste året (tillegg 2).** *Forslag:* hjelpen ved signalstyrken forklarer 3 av 3, og aksjesiden sier under «Signalet dag for dag» for eksempel «3 av 3 fire ganger det siste året, sist 14.10», regnet av vurderingene som er lagret. Er serien kortere enn et år, står «siden» og den første dagen. Ingen avkastning (NFR-06). I demoen er det vurderingene fra 21.09.
   *Rettet 2026-11-10 (gjennomgangen, BH6, BH13, ECH10 og ECH11):* tallet står med sifre («4 ganger»), 0 er «aldri», «siden» er den første dagen som er lagret, også en dag med grunn, og hjelpen om 3 av 3 står både ved signalstyrken og ved «Signalet dag for dag».
16. **Sjekkortene (tillegg 2).** *Forslag:* tykk venstrekant, 4 px, i `--opp`, `--ned` eller `--dempet-2` etter resultatet; merket står som før.
   *Rettet 2026-11-10 (gjennomgangen, BH9):* kanten er på alle sidene av kortet, som instruksjonen sier («en tykk kant»), ikke bare til venstre.
17. **«Alle | Min liste» på oversikten (tillegg 2).** *Forslag:* «Min liste» over «Aksjene» filtrerer tabellen på oversikten (`/?vis=min`) og beholder perioden og sorteringen, og knappen «Min liste» i menyen går til siden. Det som står om valget i designregler.md og designutdragene, får Rettet-linje.
18. **Demoen (tillegget om demoen).** *Forslag:* hver del kan ses i demoen uten nøkkel. Endringene som venter og «3 av 3 … det siste året» står med «Eksempeltall», aldri ekte navn eller kurser. Snarveien for demoen hører til del C.

## Delene og «Ville feilet hvis»

Hver del får tester med «Ville feilet hvis» og én mutant med kopi før og sha256 mot HEAD etter. Delene, testene og mutantene føres under, del for del, når de er bygget.

## Gjennomgangen 10.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `86d1fe4f` mot arbeidskopien kl. 22:20: Blind Hunter med bare diffen (18 funn), og Edge Case Hunter og Verification Gap i samme agent med worktreen, bare lesing, uten pytest, fordi maskinen var gitt til notatene kl. 22:15–23:50 (11 og 11 funn). Ingen høye i koden; VG1 var høy, fordi ingen test så feilen i ECH1.

**Høy**
- *VG1, rettet med test.* `test_overskriften_paa_oversikten_gjelder_alle_ogsaa_med_min_liste`.

**Middels**
- *ECH1 og BH2, rettet.* Med «Min liste» på oversikten talte overskriften og linja over tabellen bare de merkede. Nå regnes de av alle aksjene, og valget filtrerer bare tabellen (spørsmål 17).
- *BH1, rettet.* Den gamle regelen med `display: flex` for `.egen-rad` gjaldt også de nye tabellradene. Den gjelder nå bare `li.egen-rad` i bytte-lista.
- *BH3 og ECH3, rettet.* Se Rettet-linja under spørsmål 4.
- *ECH2 og VG4, rettet med test.* «Min liste» på oversikten uten merkede aksjer sto uten tabell og uten forklaring. Nå står «Ingen aksjer i Min liste ennå.» med ankeret `#aksjene`, så stjernen og lenkene sender dit (`test_min_liste_paa_oversikten_uten_merkede`).
- *BH5, ikke reelt.* Antallet i lista er lista den dagen (`oversiktsleser.oversikt(detalj.dato)`), og «12 av de 15 steg og 2 falt» er sant når én aksje sto stille eller manglet kurs.
- *BH6, delvis.* `rader[-1]` er alt brukt for vurderingene over, så en side uten kurser kommer aldri hit (ikke reelt). «Siden» er rettet i hjelpen, se spørsmål 15.
- *BH7, VG2, VG3 og VG5, rettet med tester.* Året og grensen (`test_aaret_og_grensen`), testen for 2 av 3 uten tidlig retur og med sorteringen, antallet med «Min liste» på oversikten, to endringer som venter, og testen for volumtallet uten unntaket ved 1 og 1,5.
- *BH4, ikke reelt.* `periodevalg` tar alt `ekstra` (8.17b).

**Lav**
- *Rettet:* BH8 (pila ▾/▴ viser om tabellen og «Mer om grafen» er åpne), BH11 og ECH5 (spørsmål 5), BH13 (eksemplet i hjelpen og «Eksempeltall» også ved en ekte endring i demoen), BH15 og VG9 (`KALL_PER_AKSJE` i `valg.py`), BH16 (navnet og symbolet skilles for skjermleser), ECH6 (bryteren for KI-teksten beholder «Min liste»), ECH8 (den korte teksten sier bare det som er tegnet), ECH9 (teksten om kallene gjelder lista etter neste henting), ECH10 og ECH11 (spørsmål 15, og «1 aksje i lista»).
- *Ført:* BH10 og ECH8 om HTML (innholdet i `p` er bare `span`, så det er gyldig), BH12 og ECH7 (med `?signal=positiv-2` er ingen av de tre knappene valgt; teksten under sier hva som vises), BH14 (sporet er oransje på hvitt, og «På» og «Av» står ved bryteren, så fargen er ikke alene), BH17 (vinduene og knappene står begge innenfor `{% if bransjer %}`, og «?» i kolonneraden er som i oversikten), BH18 (kommentarene om den lukkede tabellen har en linje om 8.23 under seg), ECH4 (et bytte er to endringer, og «Bruk denne lista» kan gi mange; tallet er ønskene som venter), VG6–VG8, VG10 og VG11 (dekket av testene over eller ført).
- *Ikke reelt:* BH13 om `popovertarget` uten skript (uten `hjelp.js` er handlingen «toggle», så et nytt trykk lukker).


*Lagt til 2026-11-11 (hele settet, del 1):* vinduet ved signalstyrken på aksjesiden ble over 60 ord med teksten om 3 av 3 (8.20a, del E, `test_hoeyst_60_ord_i_hvert_vindu`), så teksten står bare ved «Signalet dag for dag», der linja om året står, og er kortere. ECH10 er derfor rettet bare der. Den korte teksten under grafen sier «50-dagers snittet», fordi «børsdagene» har «bør» i seg (`test_teksten_sier_hva_linja_er_uten_raad`), som i 8.7.

*Lagt til 2026-11-11 (hele settet, del 1):* heller ikke vinduet ved «Signalet dag for dag» har plass til teksten om 3 av 3 innenfor 60 ord, og et eget «?» ved linja om året bryter regelen om ett «?» per kort og del (8.20a, del E, `test_ett_spoersmaalstegn_per_kort_og_del`). Hva 3 av 3 betyr, står derfor i `docs/hjelp.md` under «Hva sa appen om en aksje tidligere?», med linja om året, og ikke i et vindu i appen. Linja over gjelder også ECH10.

*Lagt til 2026-11-11 (hele settet, del 3):* forslaget i spørsmål 7 tok med KI-bryteren og bryteren ved «Børsdagen kort fortalt». `test_bryteren_staar_i_rammen_som_en_bryter` håndhever at KI-bryteren er i blekk, etter spørsmål 5 i 8.2b, så bare bryterne i Innstillinger er oransje, som instruksjonen sa. Designregelen og hjelpen sier det samme. `test_et_nytt_spoersmaalstegn_bytter_innholdet` krevde at «?» for det åpne feltet ikke lukket det; den følger nå A3, og `test_ikke_vurdert_staar_en_gang_og_uten_data_er_som_foer` teller teksten i ruta uten lappen (A4).

## Mutantene

Én per del, på arbeidskopien 10.11 kl. 23:51–23:52, med kopi før og fila lik før og etter (sha256), alle fanget: A1 (uten bransjeikon) `test_radene_er_en_tabell_som_tabellen_over`, A2 (sortering uten anker) `test_lenkene_i_kolonneraden_gaar_til_tabellen`, A3 (nytt trykk lukker ikke) `test_et_nytt_trykk_paa_samme_knapp_lukker`, A4 (uten lappen) `test_alle_rutene_har_symbolet_endringen_og_styrken_i_lappen`, A4 (volumet rundes over grensen) `test_volum_mot_vanlig_med_to_desimaler`, A5 (tabellen lukket) `test_tabellen_er_aapen_og_har_hjelp_ved_kolonnene`, A6 (bryteren svart) `test_bryterne`, A7 (kvoten skrevet for hånd) `test_tallene_foelger_konstantene`, A8 (ingen lenke til 2 av 3) `test_ved_0_staar_2_av_3_med_lenke`, tillegg 1 (overskriften som før) `test_med_alle_staar_begge_tallene`, B1 (uten 0-brikken) `test_tre_brikker`, B2 (uten den korte forklaringen) `test_kort_og_resten_bak_mer_om_grafen`, B3 (uten antallet i lista) `test_paa_aksjesiden`, B4 (meldingen teller ikke) `test_med_en_endring_som_venter`, B5 (alltid det siste året) `test_regnet_av_radene_som_er_lagret`, B6 (kortet uten farge) `test_kortene_har_klassen_og_kanten` og B7 (valget går til siden) `test_bare_de_merkede_paa_oversikten`.

*Lagt til 2026-11-11:* 8.23 er flettet med PR #142 i `7fb9b1fd` kl. 03:41, låst til head-en `3e9c84ae`, etter instruksjonen om del A (lest 10.11 kl. 21:31) i `docs/ai-prompts/2026-11-10.md` og gruppens svar 10.11 kl. 13:54, 14:15, 14:53, 14:59, 15:54 og 15:57. Main ble flettet inn to ganger, i `5d7cae7d` (8.21, #140 og 2.13b) og `3e9c84ae` (8.24), med avtrykkene regnet ut på nytt og alle de 13 bildene tatt på nytt fra demoen. Hele settet alene i ni deler 11.11 kl. 03:25–03:40, hver del bare når ingen annen pytest kjørte: 5137 bestått, 25 hoppet over og 0 feilet, til sammen de 5162 som `pytest --collect-only` finner. CI var grønn på head-en (run 42945863521). Treet på main etter `git pull --ff-only` er likt treet på `3e9c84ae`. Ingen funn på middels eller over sto åpne. Spørsmålene 1–18 er bygget etter forslaget og står i `issues.md` til gruppen har sett på dem.
