---
title: 'Story 10.3: Visningen i aksjedetaljen'
type: 'feature'
created: '2026-10-15'
status: 'review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5586924'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KI-teksten lagres i `KILogg` (4.3, og PR F når den er flettet), men siden viser den ikke. Story 10.3 krever at regelforklaringen står først, og at KI-teksten står under den som et tillegg, merket som laget av KI, med en bryter brukeren ser (FR-601, FR-602, NFR-06).

**Approach:**
- `src/ki_visning.py` (ren logikk): `bygg_ki_visning` regner hva siden viser av raden og vurderingen. Teksten vises bare når grunnlaget stemmer med vurderingen (FR-602) og ingen av ordene «kjøp», «selg» eller «anbefal» står i den (NFR-06). Ellers viser siden hvorfor dagen er uten KI-tekst.
- `src/app.py`: aksjedetaljen leser raden i `KILogg` med forespørselens tilkobling og viser den bare når bryteren er på. `POST /ki` setter bryteren som en informasjonskapsel og går tilbake til siden (svar 4).
- `src/templates/aksje.html`: «Med KI-ens ord» under regelforklaringen og over grafen, og knappen «Skjul KI-teksten» eller «Vis KI-teksten». Uten vurdering vises ingen av delene.

PR G i planen for KI-laget. Flettes etter at gruppen har sett siden (instruksjonen kl. 22:36).

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 2037 bestått og 17 hoppet over på main (`5586924`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 3: er vurderingen skrevet på nytt samme dag, og grunnlaget i raden stemmer ikke lenger, vises dagen uten KI-tekst (FR-602).
- Svar 4: bryteren huskes i en informasjonskapsel nå. 8.10b flytter den til innstillingene og bruker samme kapsel (`ose_ki`).
- Svar 7: 3.4b, KI-tekstene i demoen, kommer rett etter 10.3. Til da viser demoen «Ingen KI-tekst for denne dagen.», og siden kaller aldri en modell (AD-10, FR-411).

**Mutantene** (planen kl. 15:43): V1 KI-teksten står før regelforklaringen; V2 teksten vises når grunnlaget ikke stemmer med vurderingen; V3 et tomt felt i stedet for «ingen KI-tekst»; V4 et ord fra vakten vises.

## Boundaries & Constraints

- Webserveren skriver aldri i `KILogg` og importerer ingen modell (AD-10). Ingen API-kall.
- Ingen JavaScript: bryteren er et skjema med `POST`. Fokus i blekk på lys bakgrunn (designreglene).
- Grenen bruker bare testbaser (regel 22). Bildene ligger bare i scratchpad.

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En rad som besto, med grunnlaget lik vurderingen | teksten under regelforklaringen, merket «Laget av KI · gemma4:e4b, lokal» |
| Ingen rad | «Ingen KI-tekst for denne dagen.» |
| Modellen feilet, eller teksten besto ikke kontrollen | grunnen, uten teksten |
| Grunnlaget stemmer ikke med vurderingen | «… vurderingen er skrevet på nytt …», uten teksten |
| «kjøp», «selg» eller «anbefal» i en tekst som besto | grunnen, uten teksten |
| Bryteren av | ingen KI-del, og siden er lik med og uten rad |
| Ingen vurdering (en grunn) | ingen KI-del og ingen bryter |
| `KILogg` kan ikke leses | «Ingen KI-tekst for denne dagen.» |
| `POST /ki` med en adresse utenfor siden | tilbake til / |

</frozen-after-approval>

## Code Map

- `src/ki_visning.py`: `bygg_ki_visning`, `KIVisning`, `ki_paa`, `KAPSEL`.
- `src/app.py`: `aksjedetalj`, `_ki_visning`, `ki_bryter`.
- `src/templates/aksje.html`: delen «Med KI-ens ord» og bryteren.
- `tests/test_ki_visning.py`.

## Spec Change Log

## Commitene

Grenen `10-3-ki-visningen`, PR #50: `921385e` spesifikasjonen og 10-3 til in-progress; `c0ff812` visningen, ruten, bryteren og testene; `4347eb2` rettingene fra gjennomgangen.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...c0ff812`, med Blind Hunter (BH, 19 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, 4). Rettingene står i `4347eb2`. Ingen funn må avgjøres av gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, BH12, ECH | `tilbake` med tabulator eller linjeskift ga en åpen omdirigering eller en 500 | high | patch: bare `/aksje/<symbol>` godtas, ellers /. Testene har tabulator, linjeskift og `%2F` |
| BH2, ECH | En annen side kunne slå bryteren med et skjema | medium | patch: `Origin` fra en annen side gir 403, og kapselen er `Secure` på https |
| BH3, ECH, VG4 | Vakten slapp «salgssignal», «salgsanbefaling», «aksjekjøp» og myk bindestrek | medium | patch: ordene også inni et ord, med salg, solg og tilrår, etter NFC og uten usynlige tegn. Vakten er grov og stopper også «mange kjøpere» |
| VG1 | Ingen test hadde andre fortegn med samme styrke og retning | medium | patch: tilfellet i `test_grunnlaget_stemmer_ikke_med_vurderingen` |
| VG2 | Skjemaet på siden ble aldri sjekket | medium | patch: `test_skjemaet_paa_siden_snur_bryteren`, `test_en_runde_med_bryteren` |
| VG3 | Ingen test så hva demoen viser | low | patch: `test_demoen_viser_ingen_ki_tekst` |
| BH5 | Uten vurdering sa grunnen «skrevet på nytt» | low | patch: «Ingen KI-tekst for denne dagen.» |
| BH6, BH19 | Feilen når KI-loggen ikke kan leses, ble ikke logget | low | patch: `app.logger.warning` |
| BH8 | Ruten brukte en egen klokke | low | patch: appens `naa` |
| BH9 | Knappen sa ikke om bryteren er på, og malen skrev verdiene selv | low | patch: `aria-pressed`, og verdien kommer fra ruten (`ki_til`) |
| BH10 | Siden avhenger av kapselen uten `Vary` | low | patch: `Vary: Cookie`, `test_siden_varierer_med_kapselen` |
| BH14 | AD-10-testen så bare importen, ikke en forespørsel | low | patch: en test som også viser siden, med testbasen i `tmp_path` |
| BH15 | En test delte siden på `</style>` | low | patch: testen som gjorde det, er skrevet om |
| BH4 | Dokumentasjonen sier «fortegn», koden sammenligner verdiene | avvist | verdiene for de tre er fortegnene (-1, 0 eller 1). Docstringen sier det nå |
| BH6 (del) | `besto=True` med `tekst=None` gir `TypeError` | avvist | `KIRad` avviser den raden (4.2) |
| BH7 | KI-raden og vurderingen kunne gjelde hver sin dag | avvist | vurderingen hentes på samme dag som den nyeste kursen (`v.dato = n.dato` i `_OVERSIKT`), og det er `detalj.dato` |
| BH11 | «lokal» vises som det er, og flere avsnitt slås sammen | avvist | FR-602 gir eksempelet «gemma4:e4b, lokal». Prompten ber om to eller tre setninger |
| BH13 | Vakten stopper også beskrivelser | avvist | grov med vilje (NFR-06): en tekst som stoppes, gir en dag uten KI-tekst |
| BH16 | Testhjelperen skriver med `_KI_SKRIV` | avvist | testseriene ligger ikke på inneværende børsdag, som i `skriv_vurdering` i `test_app.py` |
| BH17 | Spesifikasjonen har ikke `updated` | avvist | spesifikasjonene under `implementation-artifacts` har ikke det feltet. Verification er fylt ut under |
| BH18 | 10.3 bygger på PR F | avvist | `KILogg`, `KIRad` og `SqliteKILogg` er flettet (4.2, 4.3). G trenger ikke F, men viser bare rader når F lager dem |

Under rettingen laget den nye testen for AD-10 først en tom `data/db/ose.db` i arbeidstreet `G74-g`, ikke i repoet. Vakten for regel 22 fanget det. Fila er slettet, testen bruker `tmp_path`, og den ekte basen ble ikke rørt (sist endret kl. 22:10, av hentingen).


## Verification

**Commands:**
- `uv run pytest -q` -- før 2037 bestått og 17 hoppet over på main (`5586924`). 2068 og 17 på `c0ff812`. Etter rettingene 2091 og 17 på `4347eb2`.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_ki_visning.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. V1–V4 ble først kjørt på `c0ff812` og fanget alle, og så på nytt på `4347eb2` med VR1–VR4. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| V1 | KI-teksten står før regelforklaringen | `test_ki_teksten_under_regelforklaringen` |
| V2 | teksten vises når grunnlaget ikke stemmer | `test_grunnlaget_stemmer_ikke_med_vurderingen` |
| V3 | et tomt felt i stedet for «ingen KI-tekst» | `test_vises_ikke_naar_grunnlaget_ikke_stemmer` |
| V4 | et ord fra vakten vises | `test_vakten_stopper_raad` |
| VR1 | `tilbake` sjekkes bare for // og bakstrek | `test_bare_en_sti_paa_samme_side` |
| VR2 | `Origin` sjekkes ikke | `test_en_annen_side_kan_ikke_slaa_bryteren` |
| VR3 | vakten bare på ordstart | `test_vakten_stopper_raad[salgssignal]` |
| VR4 | siden varierer ikke med kapselen | `test_siden_varierer_med_kapselen` |

**Bildene** av aksjesiden i demoen ved 1280 og 390 px, med en KI-rad som besto, en som ikke besto, ingen rad og bryteren av, ligger bare i scratchpad. De er tatt på `c0ff812`. Rettingene endret ikke det som vises, bortsett fra `aria-pressed`. KI-radene i bildene er skrevet rett i en demobase i scratchpad.
