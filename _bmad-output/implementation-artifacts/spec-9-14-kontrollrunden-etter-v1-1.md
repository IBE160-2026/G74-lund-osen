---
title: 'Story 9.14: kontrollrunden etter v1.1'
type: 'docs'
created: '2026-11-16'
status: 'in-progress'
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
  - 66 rader der bare `volumforhold` er ulikt, for DNB (16), ORK (9), GJF,
    NHY og SALM (8 hver), YAR (7), TEL (5), VAR (3) og ATEA, BAKKA, DNO og
    KOG (1 hver). `slutt` og `justert_slutt` er like, så det kommer ikke av
    justerte kurser. Volumforholdet regnes av volumene i vinduet. Grunnen er
    trolig at serien er hentet på nytt med andre volum, men det er ikke sjekket,
    fordi volum ikke skrives ut (regel 16).
  - 2 rader der også signalet er ulikt: ORK 2026-10-16 (`styrke` og
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
