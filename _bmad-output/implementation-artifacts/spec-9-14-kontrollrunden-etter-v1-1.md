---
title: 'Story 9.14: kontrollrunden etter v1.1'
type: 'docs'
created: '2026-11-16'
status: 'review'
route: 'dispatch'
baseline_commit: 'e90f0afa'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-17-signalet-regnet-i-ettertid.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-13-dokumentrunden-etter-v1-1.md'
---

Skrevet natt til 16.11 i vinduet som skrev refleksjonsloggen, etter
instruksjonen kl. 23:38 15.11 (ført i `docs/ai-prompts/2026-11-15.md`) og
gruppens svar 15.11 kl. 23:36: «Sjekk og rett klare feil». Rådet anbefalte det.
Worktreen `G74-lund-osen-9-14`, grenen `9-14-kontrollrunden-etter-v1-1`, fra
`origin/main` (`e90f0afa`), etter at refleksjonsloggen var pushet kl. 00:04.

9.14 er neste ledige nummer i Epic 9 etter 9.13.

## Storyen

Som **gruppe** vil vi at basen, dokumentene og koden er sjekket mot main etter
v1.1, og at klare feil i dokumentene er rettet, så det vi leverer, stemmer med
det appen gjør.

**Oppfyller:** regel 3, 12, 19 og 22 i `CLAUDE.md` · **Begrenses av:** ingen
endringer i `src/`; tester endres bare der en retting i et dokument krever det;
ingenting slettes; `data/db/ose.db` leses bare (regel 22), og `_privat/` røres
ikke

## Grensene

- Ingen API-kall utover kvotesjekken. `src/fetch_prices.py` kjøres ikke, og den
  ekte versjonen startes ikke.
- Fra den ekte basen skrives bare antall, symboler, datoer og navn på felt eller
  regler ut eller føres, aldri KI-tekst, kurser, volum eller målinger.
- Klare feil i dokumentene rettes: et tall som ikke stemmer med kilden, en død
  lenke eller en setning som motsier main. Alt annet blir et spørsmål med
  forslag: kode, sletting, valg og nye krav.
- Dagsfilene, sesjonsloggene og de gamle spesifikasjonene er historikk og
  rettes ikke.

## Steg 2: den ekte basen, bare med lesing

Kvotesjekken kl. 00:04 16.11: `apiRequestsDate` 2026-11-15, 20 av 20 kall brukt
den dagen (GMT) og 296 igjen i bonuskvoten. Kveldsjobben sto som Ready, med
siste kjøring 15.11 kl. 23:45 (resultat 0) og neste 16.11 kl. 22:15, så den
kjørte ikke mens kopien ble tatt.

Skriptene står i scratchpad til økta (`kontroll914.py` og `kontroll914b.py`).
Originalen ble åpnet bare med `mode=ro`, og kopien ble tatt med SQLites
`backup` til en mappe i scratchpad, utenfor repoet. Alt annet ble regnet på
kopien med appens egne funksjoner. sha256 av `data/db/ose.db` var
`9e5b0536…e61443` før og etter begge kjøringene (kl. 00:08 og 00:10), og
kopiene ble slettet med `Path.unlink` rett etterpå. Basen har ingen `-wal`
eller `-shm`.

### c) Radene

| Sjekk | Resultat |
|---|---|
| `regnet` | bare `kveld` (477) og `ettertid` (3105) |
| Rad i ettertid på (aksje, dato) med kveldsrad | 0. Primærnøkkelen er (`symbol`, `dato`), så det kan ikke skje |
| Rad i ettertid på en dato der andre aksjer har kveldsrad | 81, for aksjer som ikke ble vurdert den kvelden |
| Rad i ettertid med grunn | 0 |
| Rad fra før 2026 | 0. Eldste rad i ettertid er 2026-02-02, og eldste kveldsrad 2026-10-02 |
| Nyeste rad | kveld 2026-11-13, ettertid 2026-11-09 |
| `PRAGMA integrity_check` | `ok` |
| `skjema_versjon` | 14 |

### a) Kveldsradene regnet på nytt

Hver kveldsrad ble regnet på nytt med `vurder()` fra `signalberegning.py`, den
samme funksjonen som `regn_i_ettertid` bruker, og med kursene i basen til og med
dagen (`SqliteKurslager.serie`). Så ble feltene sammenlignet ett for ett.
Desimaltall regnes som like med relativ toleranse 1e-9.

- **Like:** 293 av 477. Ingen kveldsrad har en grunn, og alle dagene har en kurs.
- **Ulike:** 184.
  - 116 rader for AKRBP (22), DNO (25), EQNR (30), MOWI (30) og TEL (9),
    fra 2026-10-02 til 2026-11-12. Den justerte sluttkursen for dagen er
    endret siden kvelden, så ulikheten **kommer av justerte kurser**. Feltene
    er `justert_slutt`, `trend_avvik`, `standardavvik`, `dagens_endring` og i
    18 av dem `volumforhold`. Styrken, retningen og de tre sjekkene er like.
  - 68 rader der `slutt` og `justert_slutt` er like, så ulikheten ikke kommer
    av justerte kurser: DNB (16), ORK (9), GJF, NHY og SALM (8 hver), YAR (7),
    TEL (5), VAR (3) og ATEA, BAKKA, DNO og KOG (1 hver). I 66 av dem er bare
    `volumforhold` ulikt. Volumforholdet regnes av volumene i vinduet. Grunnen er
    trolig at serien er hentet på nytt med andre volum, men det er ikke sjekket,
    fordi volum ikke skrives ut (regel 16).
  - De 2 andre av de 68 har også et annet signal: ORK 2026-10-16 (`styrke` og
    `interesse`) og YAR 2026-10-26 (`styrke`, `retning` og `interesse`). Begge
    har samme kurser, og `volumforhold` er ulikt, så volumsjekken slår ut
    annerledes i dag.

Kveldsradene står som de ble skrevet (AD-7), og en rad i ettertid regnes bare
for en dag uten kveldsrad. Avvikene påvirker derfor ikke radene i ettertid.
Funnet er K1 under.

### b) KI-tekstene

317 rader i `ki_logg`: 312 om aksjer og 5 om dagen. Visningen er regnet slik
appen gjør det: `bygg_ki_visning` med raden siden viser for aksjen og dagen
(`SqliteOversiktsleser.vurdering`), og `bygg_dagsvisning` med `dagsgrunnlag`
av lista den dagen (`les_lista`), kveldsradene og radene før dagen. Kontrollen
i dag er `kontroller` for aksjene og `kontroller_dagen` for dagen, mot
grunnlaget i raden.

| | Aksjer | Dagen |
|---|---:|---:|
| Besto da | 306 | 5 |
| Besto ikke da | 6 | 0 |
| Vises nå | 306 av 306 | 5 av 5 |
| Raden siden viser, er i ettertid | 0 | – |
| Ville vist noe annet med radene i ettertid tatt med | – | 0 |
| Består kontrollen i dag | 285 | 4 |
| Besto da, men ikke i dag | 21 | 1 |

Alle tekstene som besto, vises fortsatt nå som radene i ettertid er kommet.
Grunnlaget stemmer, og ingen dag med KI-tekst har en rad i ettertid.

De 21 tekstene om aksjer er fra promptversjon 5. Kontrollen i dag stopper dem på
regel 1: «mønsteret …, tall som er 0, tas ikke med».
- **2026-11-09:** AKRBP, NHY, FRO, YAR, MOWI, ORK og DNO.
- **2026-11-10:** de samme sju.
- **2026-11-11:** AKRBP, NHY, FRO, TEL, YAR, MOWI og DNO.

Teksten om dagen 2026-11-12 er fra `dag-2` og stoppes på regel 1, der et
utsagn ikke sier det grunnlaget sier. Begge regelendringene kom etter at
tekstene var laget, og tekstene besto reglene som gjaldt da. Funnet er K2
under.

## Steg 3 og 4: dokumentene, koden og ryddingen

Fire lesere, bare med lesing, på `e90f0afa`: README-en og `docs/` (A), den
gjeldende teksten i PRD-en (B), statusene og `issues.md` (C), og koden, malene,
testene og ryddekandidatene (D). Ingen kjørte pytest, startet appen eller leste
`data/`, `_privat/` eller `.env`. Hvert funn som er rettet, er slått opp på nytt
i kilden før rettingen. Lenkene i README-en og `docs/` (233) og alle ankrene i
PRD-en virker.

### Funnene

Ingen funn i kontrollrunden er på høy grad (gjennomgangen av rettingene fant ett, se under). «Rettet» betyr rettet på grenen, med Rettet-linje der
regelen krever det. README-en, `docs/hjelp.md`, `docs/installasjon.md` og
`prd.md` er levende, så der står rettingen i teksten, og for `prd.md` med en
linje i endringsloggen.

| Funn | Grad | Hvor | Kilde på main | Utfall |
|---|---|---|---|---|
| A1 | middels | README, «Dokumentene»: brukertesten «ikke tatt ennå» | `docs/brukertest.md`, 8-1 done | Rettet (`38625e72`) |
| A2 | lav | README: «Spill av omvisningen» viser «alle sidene» i hovedflyten, «seks av sidene» i «Status» | `OMVISNINGEN_SIDER` i `src/hjelpetekster.py` har seks | Spørsmål 3 |
| A3, B9 | lav | 2.17 står ikke i «Status» i README-en | Spørsmål 4 i 9.13, svart 15.11 | Står, som svaret |
| A4 | middels | `hjelp.md`: prikkene er bare det appen lagret den kvelden, og demoen begynner 21.09 | `_signaldagene` og `les_periode(med_ettertid=True)` i `src/app.py`; `tests/test_funnene_8_23.py` | Rettet (`38625e72`) |
| A5 | middels | `hjelp.md`: webserveren skriver bare merkingen i Min liste | Regel 22, tilleggene 09.11 og 10.11 | Rettet (`38625e72`) |
| A6 | middels | `hjelp.md`: «Planen er at du senere kan velge opptil 18» | `TAK = 18` i `src/valg.py`, 2.12 done | Rettet (`38625e72`) |
| A7, A11 | lav | `hjelp.md` og `installasjon.md`: en henting bruker 16, opptil 15 KI-kall | `TAK` og `KVOTE` i `src/valg.py`, teksten om dagen i `src/ki_tekst.py` | Rettet (`38625e72`) |
| A8 | lav | `hjelp.md`: setningene i «Signalet forklart» står alltid | `detalj.ettertid` i `src/app.py` (spørsmål 7 i 2.17) | Rettet (`38625e72`) |
| A9 | lav | `hjelp.md`: dagene før første henting er regnet i ettertid | `dekker()` i `src/boersdag.py`, brukt i `regn_i_ettertid`: fra 2026 | Rettet (`38625e72`) |
| A10 | middels | `installasjon.md`: grunnlaget har ingen navn eller bransjer | `lag_dagsrad` i `src/ki_tekst.py`, `src/dagsgrunnlag.py` | Rettet (`38625e72`) |
| A12, A14 | middels | `innlevering.md` og `kvalitetssikring.md`: tallene fra 25.10 «gjelder nå» | 56 moduler, 14 migrasjoner og 100 testfiler (`ls`); CI-kjøring 43649592034 | Rettet (`d60eb0d7`) |
| A13 | middels | `innlevering.md`: «Dockerfile finnes ikke», og demoen finnes ikke | `Dockerfile` og `compose.yaml`; 3.1 og 3.2 done | Rettet (`d60eb0d7`) |
| A15 | lav | `kvalitetssikring.md` §1: sperren dekker ikke hele kjøringen | 4.0 (`dc43569`) | Rettet (`d60eb0d7`) |
| A16, A17, C4 | middels | `kvalitetssikring.md` §6, §10 og §13: brukertesten er ikke tatt | `docs/brukertest.md`, 8-1 done (#140) | Rettet (`d60eb0d7`) |
| A18 | lav | `kvalitetssikring.md` §11 rad 12: «Ikke rettet ennå» | `fdaf403` (#66) | Rettet (`d60eb0d7`) |
| A19 | lav | `kilder-og-rettigheter.md`: lenken til selskapenes sider står åpen | 10.5 done | Rettet (`d9d0d367`) |
| A20 | lav | Vurderingsmatrisen: «Status 14.11.2026» er talt før 9.13 og 8.31 | `5afabbc9` og `167640bd` | Spørsmål 4 |
| A21 | lav | `brukertest.md`: «Ikke tatt ennå» øverst | Den daterte linja under sier at testen er tatt | Står, som historikk med datert linje |
| C5 | lav | `kvalitetssikring.md` §1: vedlegget har 264 linjer | 197 + 129 = 326 på `e90f0afa` | Rettet (`d60eb0d7`) |
| B1 | lav | PRD §2: «Bygget» lest i koden 12.11 | 2.17 og 8.28 flettet 13.–14.11 | Rettet (`37404d55`) |
| B2 | middels | PRD FR-601: med KI av ingen melding om KI | `aksje.html` viser setningen om KI-teksten for en dag i ettertid også med KI av | Spørsmål 1 |
| B3 | lav | PRD FR-408: en grunn skriver aldri over en vurdering | `_UPSERT` i `src/lagring_sqlite.py` | Rettet (`37404d55`) |
| B4 | lav | PRD FR-409: «ikke kjørt» | Visningen sier «ikke vurdert», og tilstanden heter `IKKE_KJOERT` | Spørsmål 5 |
| B5 | lav | PRD FR-401: steg 1 «nekter», men steg 6 kjøres likevel | `finally` i `kjoer` i `src/fetch_prices.py` | Rettet (`37404d55`) |
| B6 | lav | PRD §8 «v1.1»: KI-tekst for små hull mangler | §2, svaret 14.11 kl. 05:49 | Rettet (`37404d55`) |
| B7 | lav | PRD §8: «Ingen av dem tas før v1 er kontrollert» | 2.17 flettet 14.11, før README-prøven | Spørsmål 6 |
| B8 | lav | PRD §7: «Status 12.11.» over en linje fra 15.11, og SM-9 | `56adfe5d`; 3.4 i review | Overskriften rettet (`37404d55`); SM-9 er spørsmål 6 |
| C1, C2 | middels | `spec-8-1-brukertesten.md` står `ready-for-dev`, mens 8-1 er done, og kravet om under 5 minutter er ikke nådd | `10265324` (#140) | Spørsmål 2 |
| C3 | lav | `spec-10-2a-…` står `in-progress` | PR #48 flettet i `77ebf31`, 10-2 done | Rettet (`d9d0d367`) |
| C6, D11 | lav | 10.4: linja om 10.2i under 10.4 i `epics.md`, «Det som gjenstår» i spesifikasjonen og kommentaren i sprintstatusen | Spørsmål 3 i 9.13, svart 15.11 | Står til brukertest 2 er ført, som svaret |
| C7 | lav | Underpunktene har egen nøkkel i sprintstatusen for noen stories, ikke for andre | `sprint-status.yaml` | Spørsmål 7 |
| C8 | lav | `issues.md`: `- [x ]` med mellomrom | `.logs/marian-osen/issues.md` | Rettes i føringen på main |
| K1 | lav | 184 av 477 kveldsrader er ulike når de regnes på nytt, og 2 har et annet signal | Steg 2a | Spørsmål 8 |
| K2 | lav | 22 KI-tekster vises, men består ikke kontrollen i dag | Steg 2b | Spørsmål 9 |
| D1–D4 | lav | Meldinger og en docstring i koden sier at en dag ikke regnes på nytt: `_stoppet_ved_midnatt` og `_kan_skrives_til` i `src/fetch_prices.py`, `src/tilstand.py` og utskriften fra `--les-inn` | `regn_signalet_i_ettertid` i `finally` | Spørsmål 10 |
| D5–D10 | lav | Kode og filer som ikke brukes, eller som bare testene bruker | Se spørsmål 11 | Spørsmål 11 |

Ingen TODO, FIXME eller HACK i `src/` eller `tests/`. «XXX» er bare et
testsymbol.

### Ryddekandidatene

Ingenting er slettet. Bildegrenene beholdes (svaret 11.11 kl. 16:26). Lokalt
gjelder det `8-19-bilder`, `pr-2-17-bilder`, `pr-3-3k-bilder`, `pr-8-17b-bilder`,
`pr-8-26-bilder`, `pr-8-27-bilder` og `pr-8-28-bilder`. Eksternt gjelder det i
tillegg `pr-8-0f-bilder`, `pr-8-17a-bilder`, `pr-8-22-bilder`, `pr-8-25-bilder`,
`pr-8-2b-bilder` og `pr-8-2c-bilder`.
Kandidatene står i spørsmål 12.

### Tallene til refleksjonsrapporten

Talt 16.11 på `origin/main` (`e90f0afa`).

| Tall | Verdi | Kommando |
|---|---|---|
| Commits på main | 2 562 | `git rev-list --count origin/main` |
| Flettede pull requests | 153 | `gh pr list --state merged --limit 500 --json number --jq length` |
| Dagsfiler i `docs/ai-prompts/` | 54 | `ls docs/ai-prompts/`, bare filene med navnet `ÅÅÅÅ-MM-DD.md` |
| Linjer som begynner med `**Utført` | 802 | `grep -c` etter `^\*\*Utført` i dagsfilene |
| Spesifikasjoner | 140, og 136 med `done` før 9.14 | `git ls-tree` over `_bmad-output/implementation-artifacts/`, og `status:` i hver |
| Stories i `sprint-status.yaml` | 143: 119 done, 1 review og 23 backlog | `git show e90f0afa:_bmad-output/implementation-artifacts/sprint-status.yaml \| grep -E '^  [0-9][0-9a-z]*-[^:]+: ' \| awk '{print $2}' \| sort \| uniq -c` |
| Testfiler | 100 `test_*.py`, og 104 `.py` i alt | `ls tests/test_*.py \| wc -l` |
| Testfunksjoner | 3 486 | `grep -rE` etter `^\s*def test_` i `tests/*.py`, og `wc -l` |
| Tester i CI | 5 863 bestått og 99 hoppet over | Kjøring 43649592034 på `c45cbb7c` (8.31) |
| Linjer Python | 22 043 i `src/` og 61 287 i `tests/` | `cat src/*.py \| wc -l` og `cat tests/*.py \| wc -l` |
| Maler | 23 | `ls src/templates/*.html \| wc -l` |
| Første commit | 2026-09-07 kl. 12:59, `300b6cea` | `git log --reverse --format=%ad --date=iso origin/main`, første linje |

Vurderingsmatrisen har 784 Utført-linjer. De er talt 14.11 og bare med
**Utført:**. Tallene over er talt 16.11 med alle linjene som begynner med
`**Utført`. Tallene gjelder ulike tidspunkter og telles ulikt (regel 12).

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet. Ingenting i koden er endret, og ingenting
er slettet.

1. **B2: setningen om en dag i ettertid når KI-teksten er av (middels).**
   FR-601 sier at aksjesiden med KI av ikke har noen melding om KI. For en dag i
   ettertid står likevel en setning om at KI-teksten bare lages samme kveld som
   kursene hentes. Det skjer fordi `detalj.ettertid` sjekkes før `ki_vises` i
   `aksje.html`. *Forslag:* en liten story som viser setningen bare med KI på,
   med en test med KI av. Kravet står.
2. **C1 og C2: 8.1 (middels).** 8-1 er done i sprintstatusen fra PR #140, men
   spesifikasjonen står `ready-for-dev`, og kravet om under 5 minutter er ikke
   nådd. *Forslag:* som for 10.4 (spørsmål 3 i 9.13). Spesifikasjonen og
   kvalitetssikringen rettes når brukertest 2 er ført, og 8-1 står som done
   til da, med en datert linje i `epics.md` om kravet.
3. **A2: «alle sidene» eller «seks av sidene».** Ordene i hovedflyten er låst
   av en test, etter svaret 12.11 kl. 09:58. *Forslag:* ingen endring. Linja i
   «Status» sier hvor mange sider det er.
4. **A20: «Status 14.11.2026» i vurderingsmatrisen er talt før 9.13 og 8.31.**
   *Forslag:* en ny status når refleksjonsrapporten skrives, med tallene over.
5. **B4: «ikke kjørt» i FR-409.** *Forslag:* teksten står. Det er navnet på
   tilstanden. Visningen sier «ikke vurdert», og det sier FR-101 også.
6. **B7 og B8: §8 og SM-9 etter v1.1.** §8 sier at ingen av idéene tas før v1
   er kontrollert, men 2.17 ble flettet 14.11, før README-prøven. SM-9 sier at
   prøven tas når v1 er ferdig bygget. *Forslag:* begge får en setning om
   svarene 14.11 og 15.11. 2.17 ble tatt inn etter svaret kl. 05:41–05:49, og
   3.4 blir done når README-prøven er tatt.
7. **C7: underpunktene i sprintstatusen.** *Forslag:* som de er. Ingen test
   eller leser trenger dem.
8. **K1: kveldsradene som er ulike når de regnes på nytt.** De står som de ble
   skrevet (AD-7). 116 av dem kommer av justerte kurser, og 68 av volumet. Bare
   2 har et annet signal (ORK 2026-10-16 og YAR 2026-10-26). *Forslag:* de står.
   Kveldsraden er det appen visste den kvelden.
9. **K2: KI-tekster som besto kontrollen da, men ikke i dag.** Det gjelder 21
   tekster fra promptversjon 5 (09.–11.11) og teksten om dagen 12.11 (`dag-2`).
   De vises, og de besto reglene som gjaldt da. *Forslag:* de står. Loggen
   endres ikke (AD-7), og raden har promptversjonen.
10. **D1–D4: meldinger i koden fra før 2.17.** *Forslag:* en liten story med
    testene for meldingene, etter innleveringen, eller før hvis gruppen vil.
11. **D5–D10: kode og filer som ikke brukes.**
    - `MinneNotatlagerMedKjoep` i `src/notater.py` og `RETNINGENE` i
      `src/dagsgrunnlag.py` brukes ikke.
    - `nyeste_leser` i `src/lagring_fil.py` og noen konstanter i
      `src/hjelpetekster.py` brukes bare av testene.
    - `src/meldinger.py` er ubrukt med vilje, for Epic 6.
    - Ingen mal viser til `ikon-16.png`, `ikon-48.png`, `ikon-192.png` eller
      `ikon-512.png` i `src/static/`.

    *Forslag:* de står til etter innleveringen, og ryddes da i én story.
12. **Ryddingen.** *Forslag:*
    - **Behold:** `G74-lund-osen-jobb`, som er kveldsjobben, og bildegrenene.
    - **Fjern:** gruppen gjør det selv eller sier ja. Det gjelder:
      - worktreene med flettet PR: 10-11, 2-17, 3-7, 8-19, 8-27, 8-28, 8-30,
        8-31, 9-11, 9-12 og 9-13;
      - `3-3k-foering` og `8-29-foering`, som ikke har noe som ikke står på
        main;
      - de lokale grenene med flettet PR: 74 med upstream `gone`, og
        `3-3k-bildene-av-appen-i-readme` og `8-29-din-egen-liste-kom-i-gang`;
      - de 13 eksterne grenene med flettet PR som ikke er bildegrener.
    - **Ikke lest:** `local-tests/` har fem `.ps1` fra 16.–17.09. Mappa er
      ignorert og kan ha nøkler. Gruppen ser selv om filene flyttes til
      `_privat/` eller slettes.

Spørsmål 1 og 2 er på middels. De står åpne til gruppen har svart (regel 25),
så PR-en stopper ved grønn CI og flettes ikke i natt.

## Gjennomgangen 16.11

Én leser gikk gjennom diffen med tre linser (Verification Gap, Edge Case Hunter
og Blind Hunter), bare med lesing. Leseren hadde ikke skrevet rettingene.
Gjennomgangen ga 14 funn: 1 høy, 2 middels og 11 lave. Alle er rettet.

- **VG1 (høy):** rettingen av kallene i `docs/hjelp.md` og
  `docs/installasjon.md` og av «Dokumentene» i README-en brøt tre tester i
  `tests/test_docker.py`. Testene låser 16 kall for de 15 aksjene appen
  begynner med, og avtrykkene i pilene. `--dokumentene` fant de samme tre
  (2963 bestått og 3 feilet, kl. 00:18–00:30). Setningene om 16 kall står nå
  som før, og 19 kall med 18 aksjer kommer i tillegg. Avtrykkene for «Den ekte
  versjonen» og «Dokumentene» er satt på nytt i testen med en kommentar, slik
  testen sier. Det er den eneste endringen i `tests/`.
- **ECH3 (middels):** medforfatterlinja i commiten med funnene manglet `>`.
  Grenen var ikke pushet, så meldingen ble rettet (`e3bfab0b`).
- **VG2 (middels):** tallet på stories i sprintstatusen kunne ikke gjenskapes.
  Det er talt på nytt med kommandoen i tabellen: 143, med 119 done, 1 review
  og 23 backlog.
- **De lave:**
  - VG3: 68, ikke 66, rader uten endret kurs.
  - VG4: navnene på bildegrenene.
  - VG5: webserveren migrerer basen.
  - VG6: `dekker()` står i `src/boersdag.py`.
  - VG7: steg 6 kjøres ikke for en demobase.
  - ECH1: en Rettet-linje for raden 10.2a i §3.
  - ECH2: `updated` i hjelpen og installasjonen.
  - BH1: setningen om KI-tekst for små hull står under lista i §8.
  - BH2: Rettet-linja om brukerne står under linja fra 17.10.
  - BH3: bransjen sendes ikke med grunnlaget for hver aksje.
  - BH4: punktum foran Rettet-linjene i innleveringen.

Ingen funn fra gjennomgangen står åpne. I kontrollrunden står spørsmål 1 og 2
på middels.

## Kontroll

- [x] `--dokumentene` består lokalt (2966 bestått og 7 hoppet over, kl. 00:32–00:44 på `aec37c87`)
- [ ] CI er grønn i alle jobbene
- [x] `git diff --stat origin/main` viser ingen fil i `src/`, og i `tests/` bare avtrykkene i `tests/test_docker.py`
- [x] sha256 av `data/db/ose.db` var lik før og etter steg 2
