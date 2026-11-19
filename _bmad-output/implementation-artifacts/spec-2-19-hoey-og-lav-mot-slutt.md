---
title: 'Story 2.19: høy og lav mot sluttkursen'
type: 'feature'
created: '2026-11-19'
status: 'done'
route: 'dispatch'
baseline_commit: '92862551'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-10-hoey-og-lav.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
---

Skrevet 19.11 etter gruppens svar kl. 18:47–18:51 på de tre spørsmålene fra
2.10, ført i `docs/ai-prompts/2026-11-19.md` under «Gruppens svar på de tre
spørsmålene fra 2.10». Storyen er ECH3 i gjennomgangen av 2.10, og får 2.19,
neste ledige nummer i Epic 2 (2.15 er gitt til «Utbytte fra EODHD», og 2.18 er
den siste). Worktreen `G74-lund-osen-2-19`, grenen
`2-19-hoey-og-lav-mot-slutt`, fra `origin/main` (`92862551`).

## Storyen

Som **bruker** vil jeg at høy og lav i basen bare står der de passer med
sluttkursen, så aksjesiden aldri kan vise en dag der sluttkursen ligger
utenfor dagens høyeste og laveste kurs.

**Oppfyller:** FR-203 (tillegget 2026-10-07) · **Begrenses av:** AD-5, AD-15,
AD-19, ECH3 i 2.10, regel 16 og 22

**Avhenger av:** 2.10. **Én økt:** ja.

## Svaret

*Svar 2026-11-19 kl. 18:47 (gruppens svar på spørsmål 2 i 2.10):* ECH3 bygges
nå, i en liten story med neste ledige nummer i Epic 2. Rådet anbefalte å vente
til aksjesiden viser tallene, men gruppen valgte nå. Fra svaret:

- En rad der lav er større enn sluttkursen, eller høy er mindre enn den,
  lagres uten høy og lav, på samme måte som en rad som mangler dem.
- Hentingen stopper ikke, og den sier hvor mange rader det gjaldt.
- Ingen ny migrasjon. Bare testbaser, og `data/db/ose.db` røres aldri.
- Gangen er som før: spesifikasjonen som første commit på en gren fra
  origin/main, en test som feiler før rettingen, testfilene og
  `--dokumentene` lokalt, hele settet i CI, «sjekk utfallet før hver push» og
  gjennomgangen. *Lagt til etter gjennomgangen (P1):* punktet manglet her.
- PR-en flettes uten nytt ja, låst til head-en, når CI er grønn i alle jobbene
  og ingen funn på middels eller høy grad står åpne (regel 25). Den flettes
  ikke kl. 22:10–23:58.
- Hovedkopien får storyen sammen med 2.10, etter sjekken kl. 23:51.

## Kontrollen

- En rad der lav er over sluttkursen, eller høy er under den, gir en `Kursrad`
  uten høy og lav, som en rad som mangler dem. Lik sluttkursen godtas.
- Hentingen stopper ikke, og linja for aksjen eller hovedindeksen sier hvor
  mange rader det gjaldt.
- Ingen ny migrasjon og ingen nye kall. Grenen bruker bare testbaser og rører
  aldri `data/db/ose.db`.
- **Ville feilet hvis:** en slik rad ble lagret med høy og lav, eller stoppet
  hentingen.

## Det som er nå

Slått opp på `92862551`:

- `kursrad_fra_eodhd` i `src/eodhd.py` gir `None` for høy og lav når en av dem
  ikke kan brukes (`_valgfri_kurs`), og begge `None` når høy er under lav. Den
  sammenligner dem ikke med `close`.
- `Kursrad` i `src/kursdata.py` og CHECK-en i `0015_hoey_lav.sql` avviser høy
  under lav, men ikke høy og lav mot sluttkursen.
- `hent_universet` og `hent_indeksen` i `src/fetch_prices.py` skriver én linje
  per symbol: «N dager, siste DATO», for aksjene med «← for kort for MA50» når
  serien er kort. Hentingen (`kjoer`) og forsøkene for aksjene og
  hovedindeksen bruker dem.
- `src/eodhd.py` står i `IKKE_BAK_AKSJESIDEN` i `tests/test_docker.py`, så den
  er ikke bak bildene. Demoen lager `Kursrad` uten høy og lav (`src/demo.py`).

## Delene

1. **Adapteren** sammenligner høy og lav med `close`, som gir `slutt` i
   `Kursrad`. Er lav over eller høy under, blir begge `None`, også når bare én
   av dem finnes. Lik sluttkursen godtas. Sjekken kommer før sjekken fra 2.10
   (høy under lav), og en rad der høy er under lav, har alltid en av dem på feil
   side av sluttkursen, så den telles også. Er `close` ikke et tall, gjør
   sjekken ingenting, og `Kursrad` avviser raden som før.
2. **Tellingen.** `hoey_og_lav_mot_slutt` i `src/eodhd.py` teller radene i en
   serie der adapteren tok bort høy og lav fordi de ikke passet med
   sluttkursen, med den samme regelen. Hentingen legger «, N rader uten høy og
   lav (passet ikke med sluttkursen)» til linja for symbolet når N er over 0.
   Ellers står linja som før. Antallet gjelder svaret, som «N dager» i samme
   linje, så en rad som ikke lagres, er med (ECH1). Antallet er regnet av oss, ikke en verdi fra
   kilden (regel 16).
3. **`Kursrad` og basen endres ikke.** Uten en migrasjon kan CHECK-en ikke
   endres. Og en `Kursrad` som avviste det, ville gjort rader lagret av 2.10
   alene uleselige. Går jobben 20.11 med 2.10 uten 2.19, bytter neste henting ut
   serien (AD-5), og radene får da `None`.
4. **`--les-inn` og leseren** (`SnapshotLeser`) bruker den samme adapteren, så
   de lagrer det samme, men uten linja om antallet. Det er hentingen svaret
   gjelder.

## Kveldsjobben og flettingen

2.19 har ingen migrasjon, så faren fra 2.10 (en base nyere enn koden) gjelder
ikke. Kommer flettecommiten etter midnatt, går jobben 20.11 med 2.10 alene, og
2.19 går fra jobben 21.11. PR-en flettes ikke kl. 22:10–23:58, og hovedkopien
får 2.19 sammen med 2.10, etter sjekken av jobben kl. 23:51.

## Bygget 19.11

| Del | Commit |
|---|---|
| Adapteren: høy og lav mot sluttkursen, og `hoey_og_lav_mot_slutt` | `d021d6de` |
| Hentingen sier hvor mange rader det gjaldt | `848a10f4` |
| Testene i `tests/test_hoey_lav_mot_slutt_2_19.py` | `838e34ca` |

## Testene før

Testene ble skrevet før rettingen, men committet etter den, så git viser
ikke den røde kjøringen (P1). De ble kjørt mot koden på `92862551` i en egen
utsjekk i scratchpad: 19 av 33 feilet, blant dem alle testene for at en rad
utenfor sluttkursen lagres uten høy og lav, tellingen og hentingen. De 14
som besto, gjelder det som skal stå som før: lik sluttkursen, innenfor, bare
én av dem på riktig side, at sluttkursen er `close`, og en `close` som ikke
kan brukes. På grenen besto alle 33, før testen fra gjennomgangen (VG1)
kom til. Ingen tester i andre filer måtte endres.

## Mutantene

Kjørt mot `tests/test_hoey_lav_mot_slutt_2_19.py`. Alle ble fanget, og `src`
var lik HEAD etterpå:

| Mutant | Feilet |
|---|---|
| M1: adapteren sjekker ikke mot `close` | 14 |
| M2: sjekken bruker `adjusted_close` | 12 |
| M3: lik sluttkursen avvises | 6 |
| M4: sjekken bare når begge finnes | 6 |
| M5: hentingen sier det ikke | 1, `test_hentingen_stopper_ikke_og_sier_hvor_mange` |
| M6: linja for hovedindeksen sier det ikke | 1, den samme |

## Gjennomgangen 19.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `838e34ca`. 5 funn, alle lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | lav | Antallet regnes på svaret, før `bare_boersdager` og basen, men docstringen sa «lagret» | Rettet: docstringen og del 2 sier at antallet gjelder svaret, som «N dager» |
| ECH2 | lav | Rader som 2.10 alene har lagret med høy og lav utenfor sluttkursen, rettes først når symbolet hentes uten feil | Står: ufarlig så lenge aksjesiden ikke viser høy og lav, og serien byttes ut ved neste henting som lykkes (AD-5) |
| VG1 | lav | Ingen test med antallet og «← for kort for MA50» i samme linje | Rettet: `test_antallet_staar_foer_merknaden_om_ma50` |
| VG2 | lav | Forsøkene og `--les-inn` er ikke testet for 2.19 | Står: de bruker `hent_universet`, `hent_indeksen` og `serie_fra_eodhd`, som er testet |
| P1 | lav | Punktet om gangen manglet i «Svaret», og testene ble committet etter rettingen | Rettet: punktet står, og «Testene før» sier det |

Leseren fant at alle veiene som skriver `kurs` og `indeks`, går gjennom
adapteren, at tellingen og adapteren bruker den samme regelen, og at ingen
type i `close` gir noe annet enn `UgyldigKursrad`.

## Flettet 19.11

CI var grønn i alle fire jobbene på head-en `2532598b` (run 44593291667): 6124 bestått og
99 hoppet over i jobben `pytest`. Ingen funn på middels eller høy grad sto åpne
(regel 25). PR #172 ble squash-flettet i `690fea4c` 19.11 kl. 20:04, låst til `2532598b`,
uten nytt ja, utenfor kl. 22:10–23:58. Hovedkopien fikk 2.19 sammen med 2.10, etter
sjekken av kveldsjobben kl. 23:51.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Grenen bruker bare testbaser og rører aldri `data/db/ose.db` (regel 22). Den
  bygges i en egen worktree.
- Aksjesiden viser ikke høy og lav, og signalberegningen bruker dem ikke.
- Den planlagte oppgaven «Morgensjekk OSE Signal» endres ikke. Aldri to
  pytest samtidig. Pausene om kvelden gjelder.
