---
title: 'Story 2.19: høy og lav mot sluttkursen'
type: 'feature'
created: '2026-11-19'
status: 'in-progress'
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
   Ellers står linja som før. Antallet er regnet av oss, ikke en verdi fra
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

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Grenen bruker bare testbaser og rører aldri `data/db/ose.db` (regel 22). Den
  bygges i en egen worktree.
- Aksjesiden viser ikke høy og lav, og signalberegningen bruker dem ikke.
- Den planlagte oppgaven «Morgensjekk OSE Signal» endres ikke. Aldri to
  pytest samtidig. Pausene om kvelden gjelder.
