---
title: 'Story 9.13: dokumentrunden etter v1.1'
type: 'docs'
created: '2026-11-14'
status: 'done'
route: 'dispatch'
baseline_commit: 'ff6e5209'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/.logs/marian-osen/issues.md'
  - '{project-root}/docs/vurderingsmatrise.md'
---

Skrevet 14.11 i vinduet som bygde 2.17, etter tillegg 3 (limt inn kl. 21:15,
ført i `docs/ai-prompts/2026-11-14.md`) og gruppens svar 14.11 kl. 17:45 og
21:07. Rådet anbefalte det. Worktreen `G74-lund-osen-9-13`, grenen
`9-13-dokumentrunden-etter-v1-1`, fra `origin/main` (`ff6e5209`), etter
Utført-linja for den siste gjennomgangen av bildene (tillegg 2, steg 3).
Bare dokumenter, README-en og testene for dem. Ingen kode i `src/`.

9.13 er neste ledige nummer i Epic 9 etter 9.12.

## Det storyen gjør

1. **Statusene.** 3.4 og 8.2 er `done` i `sprint-status.yaml`, i
   spesifikasjonen for 3.4 og i `epics.md`, med en datert linje om hvorfor.
   8.2 har ingen egen spesifikasjon (8.2a–8.2c har sine). 10.4 står til
   brukertest 2 er ført.
2. **`issues.md`.** De 67 åpne punktene i `.logs/marian-osen/issues.md` er
   sjekket mot `origin/main` (`ff6e5209`). 18 er løst og krysset av med
   «(løst 2026-11-14: …)», 35 står med en datert linje med grunnen, og 14
   trenger gruppen og er spørsmål 5–18 under. To nye punkter kommer fra
   statusene (spørsmål 1 og 2). Tabellen nederst viser hvert punkt.
3. **README-en.** Punktene om «Status», «Ekstra» og «Mappestruktur» er løst på
   main (`69fe677a`, `dcb0bc6f` og `078c7c28`), så README-en og
   `tests/test_docker.py` er ikke endret. 2.17 står ikke under «Ekstra, ferdig»
   (spørsmål 4).
4. **Vurderingsmatrisen.** `docs/vurderingsmatrise.md` har «Status 14.11.2026»
   med bevisene fra 12.–14.11: taggen `versjon-1-ferdig-2026-11-14`, 9.11,
   9.12, 8.27–8.30, 3.3k, 2.17 og den siste gjennomgangen av bildene. Hver
   lenke og hvert testnavn er sjekket på `ff6e5209`. README-prøven, brukertest
   2 og refleksjonsrapporten står som gjenstår.

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet. Det som er bygget, er bygget etter
forslaget. Spørsmål 1 og 2 er bygget etter instruksjonen (tillegg 3, steg 2),
så punktet om 8.2 er lukket og 3.4 er med i lukkingen av linje 247. Punktene
i `issues.md` som spørsmål 5–18 gjelder, står åpne med en datert linje til
gruppen har svart.

1. **3.4 til done.** Storyen ventet bare på README-prøven på en ren maskin (§9
   i `docs/kvalitetssikring.md`). Gruppen avgjorde 12.11 kl. 20:04 og 20:06 at
   3.4 settes til done etter prøven på ny PC. Tillegg 3 (kl. 21:15 i
   `docs/ai-prompts/2026-11-14.md`) setter den til done nå, og det står som en
   datert linje under avgjørelsen i `epics.md`. *Forslag:* 3.4 er done, og README-prøven
   står som et eget punkt i `issues.md` og som gjenstår i vurderingsmatrisen.
   Bygget slik.
2. **8.2 til done.** Kontrollpunktet «Funnene fra 8.1 er brukt som grunnlag» er
   oppfylt: brukertesten ble tatt 10.11, og funnene står som U103–U112 i
   `docs/ux-logg.md`. Det som gjenstår, er U33, U46, U57 og U67, som var delvis
   bygget, U58 og U65, som sto (linja 04.11 kl. 11:34 i `epics.md`), og svaret
   på papir om hvordan Nyheter og Kalender ville passet inn. *Forslag:* 8.2 er
   done, og resten står som ett punkt i `issues.md`. Bygget slik.
3. **10.4 sier to ting.** `sprint-status.yaml` har `10-4: done` (`10265324`,
   PR #140), men `spec-10-4-loggdelen.md` har `status: 'in-progress'`, og
   kommentaren over 10-4 i sprintstatusen sier at delen med én person venter
   på brukertesten. Tillegg 3 sier at 10.4 står til brukertest 2 er ført.
   *Forslag:* begge rettes når brukertest 2 er ført, ikke nå. Ikke endret.
4. **2.17 i «Status» i README-en.** 2.17 (v1.1) er flettet, men står ikke under
   «Ekstra, ferdig». Lista har åtte punkter, som er grensen i
   `test_status_uten_storynumre_og_uten_kommando`, og bildeteksten øverst nevner
   alt prikkene som er regnet i ettertid. *Forslag:* ingen endring nå. Vil
   gruppen ha den med, slås to punkter sammen i en egen sak. Ikke endret.
5. **Prøven med 0 kall fra hentingen (2.3d, `issues.md` linje 7).** Rad 5 i
   Prøve 4 i `docs/kvalitetssikring.md` har bare kjøringen 28.10, og «0 kall»
   er ikke ført for 29.10. *Forslag:* loggen fra første kveld etter pausen
   (16.11) leses, og en datert linje føres i Prøve 4. Til da står punktet.
6. **«Kort fortalt» før timen 29.10 (linje 25).** Datoen er passert, og delen
   er skrevet om i 9.11 (`ef802733`). *Forslag:* punktet lukkes som utgått.
7. **Windows Update (linje 49).** PC-en startet på nytt 11.11 kl. 04:29
   (`docs/ai-prompts/2026-11-11.md`). *Forslag:* punktet lukkes som utgått, og
   morgenkontrollen etter 16.11 viser om jobben har kjørt etter omstarten.
8. **Neste § i `malinger.md` (linje 56).** Siste § er 57. Målingen av
   omsetning fra 02.11 og målingen i 2.13b (`178107d9`) står ikke der.
   *Forslag:* én samlet §58 i en egen sak.
9. **Bruksloggen (linje 59).** `docs/brukslogg.md` har bare 04.11, og SM-2 og
   SM-5 bygger på den. *Forslag:* loggen føres fra i dag, og hullet skrives
   inn i §7 i PRD-en etter regel 19 (en datert linje i endringsloggen).
10. **macOS uten maskin på `dc027575` (linje 72).** Kjøringen er ikke tatt på
    nytt, og commiten endret bare to filer under `.logs/`. *Forslag:* lukkes
    uten ny kjøring, fordi ingen fletting venter på den.
11. **Store ruter bare i `bredest` (linje 96).** `STORE_KLASSER = frozenset({"bredest"})`
    i `src/boersometer.py`. *Forslag:* tolkningen står, som bygget.
12. **Tellingen for 10.4 med versjon 5 (VG10, linje 133).** Versjon 6 ble
    flettet 11.11 (`e5268b30`), så versjon 5 gikk høyst tre kvelder.
    *Forslag:* børsdagene 09.–13.11 telles med klassene fra spørsmål 9 i 10.4,
    delt på versjon 5 og 6, i en egen sak, når jobben går igjen.
13. **«Vis hjelp» og «Vis KI-tekst» i «Ferdig» (linje 179).** *Forslag:* de
    navnes ikke. «Innstillinger» og «med bryter» står alt, og grensen er åtte
    punkter med høyst 20 ord.
14. **Dokumenttestene følger importer (`3641ce50`, linje 185).** *Forslag:*
    endringen godtas. Vakten er ikke svekket, og README-en oppgir ikke
    antallet moduler.
15. **Spørsmål 1–18 i 8.23 (linje 199).** Gruppen svarte samlet «ja» til del A
    og B 10.11 kl. 13:54, før spørsmålene fantes. *Forslag:* 1–18 godtas som bygget og flettet i
    `7fb9b1fd`.
16. **Hva 3 av 3 betyr (linje 200).** Det står bare i `docs/hjelp.md`, mot
    forslaget i spørsmål 15 i 8.23. *Forslag:* avviket godtas, fordi grensen på
    60 ord og ett «?» per del (8.20a) går foran.
17. **Dagsteksten når eldre data kommer inn senere (BH2, linje 218).**
    Spørsmål 13 i 10.10 er åpent i `epics.md`. *Forslag:* ja, som før.
    Hentingen fyller ikke inn eldre dager, og dagen sier «Dagen er uten
    KI-tekst.».
18. **Investorsiden og siden for eodhd.com i omvisningen (linje 254).**
    *Forslag:* ingen steg i v1. Sidene finnes bare i demoen.

## Punktene i `issues.md`

Sjekket mot `origin/main` på `ff6e5209` 14.11 kl. 22:00–22:10, i tre deler med
bare lesing. Bevisene for de løste er slått opp på nytt før føringen. Linje er
linjenummeret i `issues.md` på `ff6e5209`.

| Linje | Punkt | Utfall | Bevis eller grunn |
|---|---|---|---|
| 7 | 2.3d: prøven med 0 kall 29.10 | spørsmål 5 | Rad 5 i Prøve 4 har bare 28.10 |
| 12 | 2.3d VG4, BH7, BH9/ECH8, BH15/VG7, BH16 | står | BH7 løst i `0955f796`; VG4 sett i drift, ikke i en test; resten lave |
| 15 | 3.5f BH15: prøven av hovedveien (D1) | står | Venter på README-prøven; rad D1 i Prøve 1 er tom |
| 16 | 3.5f BH8: hjelpen når uv-installasjonen feiler | står | Lav, ikke bygget |
| 17 | 3.5f ECH2: vinduet lukkes inne i ZIP-fila | står | Ikke prøvd; hjelpen har svaret; tas i README-prøven |
| 18 | 3.5e BH3: hentingen mens den ekte versjonen kjører | står | Lav, ikke prøvd |
| 19 | 3.5e BH8: to vinduer nesten samtidig | står | Lav, ikke bygget; ingen lås |
| 20 | 8.6b BH5: høyden på smal flate | står | Lav, høyden er ikke målt |
| 21 | 8.6b ECH5: «Mål mot børsen» | står | Mer enn 6 dager rettet (`vis_dagen_foer`); spriket kurser og kalender står |
| 22 | 8.6b: bransje uten kurs i overskriften | løst | 8.20b, `8d89cf8c`: `Bransje.tillegg` i `src/boersometer.py`, og `test_linja_i_overskriften_er_bransje_tillegg` |
| 25 | «Kort fortalt» før timen 29.10 | spørsmål 6 | Datoen er passert; skrevet om i 9.11 |
| 26 | Sidetallet 11,7 i «Om lengden» | løst | 9.11, `ef802733`: delen er tatt ut av `prd.md` |
| 46 | CI Windows: opprydningen og timeouten | står | Opprydningen rettet med `exit 0` i `0955f796`; timeouten ikke slått opp igjen |
| 49 | Windows Update på pause | spørsmål 7 | Omstart 11.11 kl. 04:29 |
| 52 | Docker Desktop i jobben etter 29.10 | står | Drift, ikke prøvd |
| 55 | NEXT, HYN, OUTLT, færre handelsdager | står | Ikke slått opp; åpent i `malinger.md` |
| 56 | Neste § i `malinger.md` | spørsmål 8 | Siste § er 57 |
| 59 | Bruksloggen | spørsmål 9 | Bare 04.11 i `docs/brukslogg.md` |
| 67 | macOS avbrutt og Windows feilet 03.11 | løst | Svaret 03.11 kl. 20:48 og `exit 0` i `0955f796` |
| 72 | macOS uten maskin på `dc027575` | spørsmål 10 | Ikke kjørt på nytt |
| 76 | 8.2 in-progress til funnene fra 8.1 er brukt | løst | 9.13: 8.2 er done |
| 79 | Periodevalget ved zoom 200 % | står | Lav, zoom 200 % er ikke målt |
| 94 | Funnet fra 10.4 i refleksjonsrapporten | står | Refleksjonsrapporten er ikke skrevet |
| 95 | Delen av 10.4 med én person | løst | `10265324`, PR #140 (se spørsmål 3) |
| 96 | Store ruter bare i `bredest` | spørsmål 11 | `STORE_KLASSER` i `src/boersometer.py` |
| 97 | BH7: stilen for nivå 4 brukes ikke | står | Lav, står etter triagen i 8.2b |
| 98 | VG9: avtrykket mangler `app.py` | står | Lav, arvet fra 3.3e |
| 102 | PR #113 og tellingen med versjon 4 | løst | `374f1bdb`; kjøringen med versjon 4 07.11 laget ingen KI-tekster, og fra 08.11 gikk versjon 5 (refleksjonsloggen 07.11) |
| 106 | Linja i loggen 06.11 | løst | `b11f5435`, refleksjonsloggen |
| 133 | Tellingen med versjon 5 (VG10) | spørsmål 12 | Versjon 6 fra 11.11 (`e5268b30`) |
| 163 | Omsetningen for en ny aksje | løst | 8.11c `d12301a8`, medianen av kursene |
| 179 | «Vis hjelp» og «Vis KI-tekst» i «Ferdig» | spørsmål 13 | Grensen på åtte punkter |
| 180 | ECH14 i 10.6, alternativ c | står | Lav, ikke bygget |
| 181 | 9.9, 8.11c og 9.10 under «Ekstra» | løst | `69fe677a` |
| 184 | «Mappestruktur» og to bilder | løst | `69fe677a`; begge står i README-en |
| 185 | Dokumenttestene følger importer | spørsmål 14 | Ingen svar funnet |
| 186 | Vakten hopper over seg selv | står | Ikke rettet; bare CI prøver den |
| 187 | «Ekstra» med PR-ene #137–#139 | løst | 8.22, `dcb0bc6f` |
| 189 | 8.21: BH6, ECH4, ECH6 | står | Lav, ført i triagen |
| 190 | 8.21: ECH4, ECH5, ECH6, ECH3 | står | Lav, ført i triagen |
| 191 | Notatene og målingen under «Ekstra» | løst | 3.6, `078c7c28`, «Ekstra, ferdig» |
| 194 | U103–U112 og kravet om under 5 minutter | står | Storyene er flettet, også 8.9; kravet venter på brukertest 2 |
| 195 | 8.24: de lave funnene | står | Lav, ført og ikke rettet |
| 199 | Spørsmål 1–18 i 8.23 | spørsmål 15 | Samlet svar 10.11 kl. 13:54 |
| 200 | Hva 3 av 3 betyr | spørsmål 16 | Står bare i `docs/hjelp.md` |
| 207 | Bildegrenen `pr-8-22-bilder` | løst | Duplikat av punktet lukket 11.11; svaret 11.11 kl. 16:26, ført med 8.25 i `c53df5b1` |
| 211 | BH6: «følg nøye med» | står | Lavt funn, ikke rettet |
| 214 | 1 error i `--dokumentene` på `40a5637b` | står | Testen er ukjent, og feilen er ikke sett igjen |
| 215 | VG3/VG4 etter 8.23 | står | Lave funn, bare ført |
| 216 | De lave funnene fra «Følg en aksje» | står | Lave funn, bare ført |
| 218 | BH2: dagsteksten ved eldre data | spørsmål 17 | Spørsmål 13 i 10.10 er åpent |
| 219 | ECH1: «dem» og anførselstegnene | står | Lave funn, latt stå i triagen |
| 227 | Tabellen i «Følg en aksje» ved 390 px | står | Ikke rettet |
| 229 | `tilbakemelding-prd.md` i «Dokumentene» | løst | 9.11, `ef802733` |
| 241 | BH9: kommandoene uten Docker | står | Venter på README-prøven |
| 244 | ECH6: Gemma og bransjene | står | Drift; jobben står på pause til 16.11 |
| 247 | De seks foreslåtte storyene fra 9.11 | løst | 9.12 `e537345f` med `fetch-depth: 0`, 8.28 `c8ad6f4c`, FR-111 i 9.11, 3.4 i 9.13; pekerne etter spørsmål 17 i 9.11 |
| 249 | `pr-8-28-bilder` viser det gamle | løst | Svaret 11.11 kl. 16:26; bildet på main er fra 3.3k |
| 250 | En test feilet én gang på `7f2edbce` | står | Testen er ukjent, og feilen er ikke sett igjen |
| 252 | VG8: stegkortene ikke målt | står | Tillegg 4 tar det i natt |
| 253 | VG4: pillen uten nettlesertest | står | Tillegg 4 tar det i natt |
| 254 | Investorsiden og eodhd-siden i omvisningen | spørsmål 18 | Bare i demoen |
| 255 | ECH5: linja om neste henting | står | Lav, godtatt i triagen for 3.3k, ikke av gruppen |
| 256 | Bildegrenen `pr-3-3k-bilder` | løst | Svaret 11.11 kl. 16:26, ført med 8.25 i `c53df5b1` |
| 259 | Morgenkontrollen etter første kveld med 2.17 | står | Jobben står på pause til 16.11 |
| 261 | Bildegrenen `pr-2-17-bilder` | løst | Svaret 11.11 kl. 16:26, ført med 8.25 i `c53df5b1` |
| 262 | Bildeskriptet bruker `click()` | står | Bildet på main er det en bruker ser |

## Kontroll

- [x] `uv run pytest tests/test_kvalitetssikring.py tests/test_ryddighet.py tests/test_dokumenttestene.py tests/test_readme.py` består lokalt (`test_kvalitetssikring.py` sjekker testnavnene i matrisen og radene for spesifikasjonene som er done)
- [x] `--dokumentene` består lokalt (2957 bestått og 7 hoppet over på grenen)
- [x] CI er grønn i alle jobbene (run 43644459699)
- [x] `git diff --stat origin/main` viser bare dokumenter, `issues.md` og ingen fil i `src/`

## Flettet 14.11

CI var grønn i alle fire jobbene på head-en `ee756c36` (run 43644459699). Triagen
hadde ingen åpne funn på middels eller høy grad. PR #158 ble squash-flettet i
`5afabbc9` kl. 22:53, låst til `ee756c36`, uten nytt ja, slik tillegg 3 sier.
Kveldsjobben sto som Disabled.

## Mutantene

To mutanter 14.11 på `8fe6b3cd`, med `tests/test_kvalitetssikring.py`. Begge
filene var like HEAD etterpå, målt med sha256.

- **M1:** testnavnet `test_ledig_mot_bakgrunnen_og_brukt_mot_ledig` i matrisen
  byttet med et som ikke finnes. Fanget av
  `test_hver_test_dokumentene_nevner_finnes[vurderingsmatrise.md]`.
- **M2:** denne spesifikasjonen satt til `done` uten rad i kvalitetssikringen.
  Fanget av `test_hver_ferdige_spesifikasjon_har_en_rad`, i §3 og §5.

Ingen test sjekker lenkene i matrisen eller bevisene i `issues.md`. De er
sjekket for hånd og i gjennomgangen (lav, står).

## Gjennomgangen 14.11

Én leser gikk gjennom diffen med tre linser (Verification Gap, Edge Case Hunter
og Blind Hunter), bare med lesing. 20 funn: 6 middels og 14 lave.

- **Rettet:** V1 (middels, `c46f63ac` finnes ikke på main; nå vist til
  `c53df5b1` og dagsfila 11.11, og linje 207 er et duplikat), V2 (middels, ECH5
  ble godtatt i triagen, ikke av gruppen; punktet står), V7 (middels, 784
  Utført-linjer med tellingen fra 07.11, ikke 797), P1 (middels, avgjørelsen
  12.11 om 3.4 er endret av tillegg 3; en datert linje under den i
  `epics.md`), P2 (middels, 9.12 hadde ingen gjennomgang; nevnt i matrisen),
  P3 (middels, 08.–11.11 og 13.11 manglet i matrisen; én setning om dem),
  V3, V4, V5, V6, V8, V9, E1, P4, P5, P6, P7 og P8.
- **Står:** E2 (`'review'` er formen sprintstatusen bruker, og 2.17 brukte den),
  E3 (kommentaren over i sprintstatusen er historikk).

Ingen funn på middels eller høy står åpne.
