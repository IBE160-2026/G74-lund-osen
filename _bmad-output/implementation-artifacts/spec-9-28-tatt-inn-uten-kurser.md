---
title: 'Story 9.28: en egen aksje som er tatt inn uten kurser, står ikke som «Hentet»'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'bbf861f6'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-27-statusene-regner-dagen.md'
---

Skrevet 24.11 etter instruksjonen kl. 23:29 i `docs/ai-prompts/2026-11-23.md`
og gruppens svar 23.11 kl. 23:27 på spørsmål 4 i 9.27 (AA1 i gjennomgangen
etter svarene). Rådet anbefalte å vente med storyen til etter brukertest 2,
men gruppen valgte nå. Neste ledige nummer i Epic 9 etter 9.27 er 9.28.
Worktreen er `G74-lund-osen-9-28`, på grenen `9-28-tatt-inn-uten-kurser`, fra
`origin/main` (`bbf861f6`), etter at 9.27 er flettet i `93b26f50` og ført.

## Storyen

Som **bruker som følger en aksje sent en børsdag** vil jeg at appen sier at
aksjen er tatt inn og når kursene kommer, så jeg ikke leser «Hentet» om en
aksje uten kurser, eller at EODHD ikke ga kurser når ingen har spurt.

**Oppfyller:** AA1 i gjennomgangen etter svarene i 9.27 (svaret 23.11 kl.
23:27), FR-412, FR-415 · **Begrenses av:** regel 3, 16, 19, 20, 21 og 22,
NFR-06, NFR-08, AD-3 og AD-10 (siden leser bare); ingen ny migrasjon, og
hentingen endres ikke

**Avhenger av:** 9.27. **Én økt:** ja.

## Det som er slått opp

- Tilfellet: en kjøring av kveldsjobben etter den første tar et ønske i bruk
  (`ta_i_bruk_oenskene` i `src/fetch_prices.py`), så aksjen står i lista med
  `inn` lik dagen. Det nye forsøket som skulle hentet den, bruker bare
  kallene som er igjen av dagens, og målingen etter første kjøring har brukt
  dem. Aksjen har da ingen kurser, og ingen har spurt EODHD om den.
- Det appen viser i dag: «Hentet. Står i tabellen over.» under «Dine egne
  aksjer» (`_egne_regnet` i `src/app.py` og `_egne.html`), og «EODHD har ikke
  gitt kurser for aksjen. Gir EODHD ingen kurser ved neste henting heller,
  slutter appen å følge en aksje du har valgt selv.» bak «?» ved «Oppdatert»
  og på siden for aksjen (`UTEN_KURSER_HVORFOR` i `src/hjelpetekster.py`,
  `aksje_uten_kurser.html`).
- **Appen kan se forskjellen med det som alt er lagret, så ingen migrering
  trengs.** En vanlig henting skriver en rad i `vurdering` for hver aksje i
  lista, også når EODHD ikke ga kurser, da med grunnen `symbol_feilet`
  (`skriv_vurderinger`). En aksje som bare er tatt inn, har ingen rad. Det er
  regelen `valg.uten_rader` alt bruker for å ta ut en aksje som «ble forsøkt
  hentet»: en rad i `vurdering` med `dato >= aksje.inn`.
- «Ikke forsøkt» er derfor: en egen aksje i lista (`ut` ikke satt, og et ønske
  om å følge som er tatt i bruk), med `inn` satt, uten en eneste rad i `kurs`
  og uten en rad i `vurdering` fra og med `inn`.

## Det som gjøres

1. **Regelen.** `valg.ikke_forsoekt(tilkobling)` gir de egne aksjene som er
   tatt inn uten kurser og ikke er forsøkt hentet, med dagen de kom inn. Bare
   lesing.
2. **Dagen.** Kursene kommer ved hentingen neste børsdag etter dagen aksjen
   kom inn, og aldri før dagen 9.27 regner: den seneste av
   `neste_boersdag(inn)` og `neste_henting_av_oensket(naa)`, skrevet som i
   9.27, «i morgen etter kl. 22», «mandag etter kl. 22» eller «i kveld etter
   kl. 22» dagen etter. Dekker kalenderen ikke dagen, står bare klokkeslettet
   (NFR-08).
3. **Statusen.** Under «Dine egne aksjer» står «Tatt inn. Kursene kommer ved
   hentingen …» i stedet for «Hentet. Står i tabellen over.» for en slik
   aksje. Knappen «Fjern» står som før.
4. **Teksten bak «?» og på siden for aksjen.** For en slik aksje sier «?» ved
   «Oppdatert» og siden for aksjen at den er tatt inn og at ingen kall er
   brukt på den ennå, ikke at EODHD ikke ga kurser eller at appen slutter å
   følge den.
5. **Som før:** en aksje EODHD faktisk ikke ga kurser for, beholder «Hentet.
   Står i tabellen over.» og teksten om EODHD. Raden i tabellen sier «ingen
   kurser ennå» i begge tilfellene.
6. **Hjelpen.** `docs/hjelp.md` sier det appen nå viser.
7. **Testen** feiler før rettingen. Bildene og avtrykkene håndteres som i
   9.27, og `docs/skjermene.md` får en linje for 9.28.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/`, `.env` og `_privat/` røres
  ikke, og den ekte versjonen startes ikke. Kveldsjobben og databasekopien
  røres ikke.
- Ingen migrering, ingen ny tabell og ingen ny fil for å se forskjellen.
  Hentingen endres ikke.
- Bilder bare av demoen, på en ledig port, aldri 8000, og uten ekte kurser.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.

## Kontroll

- [ ] En egen aksje som er tatt inn uten kurser og ikke er forsøkt hentet, står som «Tatt inn. Kursene kommer ved hentingen …», med dagen regnet som i 9.27
- [ ] «?» ved «Oppdatert» og siden for aksjen sier ikke at EODHD ikke ga kurser, eller at appen slutter å følge den
- [ ] En aksje EODHD ikke ga kurser for, har teksten som før
- [ ] Ingen migrering, og hentingen er ikke endret
- [ ] Testen feilet før rettingen
- [ ] Hjelpen følger med
- [ ] Bildene og avtrykkene er håndtert som i 9.27
- [ ] Gjennomgangen med fire roller er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
