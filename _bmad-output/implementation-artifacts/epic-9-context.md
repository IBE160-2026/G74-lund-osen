# Epic 9 Context: Dokumentasjon av prosessen

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Sensor skal kunne se hvordan KI ble brukt og hvordan koden er kvalitetssikret,
uten å lese git-loggen. Emnesiden legger dette under prosjektkoden (70 %), så
epicen er en del av det som vurderes, ikke pynt. Epicen har ingen FR-er: den
leverer tester som faktisk kan feile (9.0), et samlet dokument om
kvalitetssikringen (9.1), instruksjonene som styrte byggingen, ordrett (9.2),
en beskrivelse av arbeidsmønsteret mellom rådgivningsøkt, byggeøkt og menneske
(9.3), og del 1 av relevanseksperimentet (9.4). Per 27.09 er 9.3 og 9.4 ferdige;
9.0, 9.1 og 9.2 står igjen.

## Stories

- Story 9.0: Fem tester sjekker det de lover
- Story 9.1: `docs/kvalitetssikring.md`
- Story 9.2: `docs/ai-prompts/bygging/`
- Story 9.3: Arbeidsmønsteret (ferdig)
- Story 9.4: Relevanseksperimentet, del 1 — utvalg, innsamling og merking (ferdig)

## Requirements & Constraints

- **En grønn testkjøring skal bety det vi sier den betyr.** Fem tester er funnet
  å bestå uten å sjekke det navnet og docstringen lover (tre ført i
  `deferred-work.md`, to som K3 og K4 i kontrollrapporten 26.09). Hver skal
  feile mot en mutant som bryter løftet, og bestå mot koden slik den er.
  Koden i `src/` endres ikke; viser en test at koden er feil, stopper arbeidet og
  saken avgjøres for seg.
- **Kvalitetssikringsdokumentet skal vise hullene, ikke bare dekningen.** Det
  må ha en egen seksjon for det som ikke testes (for eksempel den ekte
  hentefunksjonen mot EODHD, som bruker kvote og aldri kjøres i tester). Antall
  tester telles når dokumentet skrives, aldri kopiert fra planene. Mutantpraksisen
  dokumenteres med story, commit, mutant og hvilke tester som fanget den,
  inkludert forkastede mutanter. Kodegjennomgangene (én per epic) og kontrollene
  (22.09 og 26.09) er en del av bildet. Dokumentet oppdateres ved hver epic.
- **Instruksjonene lagres ordrett, aldri renskrevet eller oppsummert.** Omskriving
  er der krav har forsvunnet før. Fra 24.09 kl. 22:05 føres instruksjonene løpende
  i dagsfiler; det som gjenstår i 9.2, er å hente inn 21.–24.09 fra
  økthistorikken i samme format. De innhentede filene leses av Marian eller
  Joakim før commit, fordi repoet er offentlig (navn og formuleringer, ikke bare
  nøkler).
- **Ingen rådata i sporede filer:** ingen kurser, volumer, meldingstitler,
  artikkelutdrag eller nøkler, heller ikke i dokumentasjon og eksempler. Tall vi
  har regnet ut selv, kan stå.
- **Siter bare det som er lest i samme økt.** Tilfeller og påstander i
  dokumentasjonen skal ha kilde (commit, memlogg eller refleksjonsloggen); finnes
  ikke kilden, sies det.
- Nye hoveddokumenter under `docs/` får frontmatter (`title`, `status`,
  `created`, `updated`) og føres som lenke i README-ens «Dokumentene» i samme
  commit.

## Technical Decisions

- **Nettverk er sperret i testkjøringen.** `tests/conftest.py` sperrer socket,
  DNS og proxy med en autouse-fixture; bare loopback slipper gjennom. CI kjører
  `pytest` på hver push og PR uten hemmeligheter. Mutanter i 9.0 må kjøres innenfor
  denne sperren.
- **Testoppsett:** kjernen testes direkte; skallet testes med port-dobler (for
  eksempel `MinneKurslager`). Kontrakttestene kjøres mot begge lagrene, og det er
  dette 9.1 skal beskrive.
- **Ingen API-kall uten avtale.** Kostnad måles med `/api/user` før og etter.
  Relevanseksperimentet del 1 er gjennomført (48 par, merket hver for oss før
  diskusjon); del 2, KI-klassifiseringen, venter på KI-laget og på at EODHDs
  betingelse om at modelltjenesten ikke trener på innholdet er dokumentert.
  Kriteriene fra del 1 endres ikke i ettertid.
  *Lagt til 2026-10-06:* del 2 av relevanseksperimentet utgår etter Marians beslutning 06.10 kl. 21:11
  (story 9.5).

## Cross-Story Dependencies

- 9.0 går foran 9.1, så kvalitetssikringsdokumentet kan vise til tester som
  faktisk kan feile. 9.0 rører bare `tests/`.
- 9.1 skrives etter at Epic 1 er ferdig og oppdateres ved hver ferdige epic,
  sammen med kodegjennomgangen for epicen.
- 9.2 bygger på formatet i `docs/ai-prompts/README.md`; 9.3 har lagt
  arbeidsmønsteret inn i samme README.
- Del 2 av relevanseksperimentet avhenger av KI-laget og kalibrerer terskelen for
  samlekategorien i relevansvurderingen.
  *Lagt til 2026-10-06:* del 2 av relevanseksperimentet utgår etter Marians beslutning 06.10 kl. 21:11
  (story 9.5).
