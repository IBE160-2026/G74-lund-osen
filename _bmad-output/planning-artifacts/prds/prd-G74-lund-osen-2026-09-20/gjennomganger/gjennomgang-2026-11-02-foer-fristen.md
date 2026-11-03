---
title: "Gjennomgang av PRD-en før fristen 5.11"
status: aktiv
created: 2026-11-02
updated: 2026-11-03T16:27
---

# Gjennomgang av PRD-en før fristen 5.11

**Dato:** 2026-11-02
**Formål:** finne det i `prd.md` som ikke lenger stemmer med repoet, før
rettingen onsdag 4.11. Fristen er beskjeden fra faglærer på emnesiden 2.11,
og gruppen svarte kl. 21:18: les først, rett onsdag (`docs/innlevering.md`,
under E). `prd.md` er ikke endret i denne gjennomgangen.

**Lest mot:** `prd.md` på `88827911` (2081 linjer, `updated` 2026-10-28T23:49),
`_bmad-output/planning-artifacts/epics.md`, `sprint-status.yaml`,
spesifikasjonene i `_bmad-output/implementation-artifacts/`, «Status» i
README-en, arkitekturspinen, `docs/innlevering.md`, `docs/brukertest.md`,
`docs/kilder-og-rettigheter.md` og koden i `src/` der det trengtes.
Linjenumrene under gjelder `prd.md` på `88827911`.

**Om kildene.** `sprint-status.yaml` er sist oppdatert 23.10 og henger etter
`epics.md` og git-loggen: 2.13 står som «review», men er flettet i `676fbc8b`
(29.10), 9.5 står som «backlog», men utgår (`9617a701`, 06.10), og 2.3c, 2.3d
og 3.5a–h mangler. Der de spriker, er `epics.md` og git-loggen lagt til grunn.
§4 og §5 er lest av en underagent mot `epics.md`, spesifikasjonene og `src/`,
og funnene som står under, er stikkprøvd mot `prd.md`, `src/` og commitene.

---

## §8: de 14 åpne punktene

| # | Linje | Hva det gjelder | Avgjort eller bygget, og hvor | Fristen | Forslag |
|---|---|---|---|---|---|
| 2 | 1954 | KI-terskelen i samlekategorien (FR-606, meldinger) | Ute av v1 med plan B 28.09 (punkt 1 under «Lukket», l. 1991). Eierfeltet er fortsatt `‹fylles inn›` | Ingen frist (plan B) | Utenfor v1, som nå. Eier Gruppen i stedet for plassholderen |
| 4 | 1955 | Hvordan eks.dato utledes, for FR-407 og FR-503 | Den målte veien er funnet 21.09 (`begrunnelser.md` §11). Story 2.6 er «Ekstra, hvis tiden rekker» fra 19.10 (`epics.md` l. 1716, `ac12ca8c`) og står i backlog, og det gjør 2.14 (FR-414) også. Ingenting er bygget | «Før story 2.6», ikke utløst | Utenfor v1 (ekstra, 19.10), med frist «før 2.6, hvis den bygges». FR-503 er plan B |
| 16 | 1956 | Språkgjenkjenningen for Vår Energi (FR-501) | Ute av v1 med plan B 28.09. Epic 6 er backlog | Ingen frist (plan B) | Utenfor v1, som nå |
| 5b | 1962 | Relevanseksperimentet, del 2 | Kjøres ikke: beslutningen 06.10 kl. 21:11, story 9.5 utgår (`epics.md` l. 4245, `9617a701`). Betingelse 4 er ført 04.10 (`dcbce6d9`, story 4.1 done) | «Når KI-laget finnes»: KI-laget finnes (10.1–10.3 done) | Lukk, lukket av beslutningen 06.10 kl. 21:11, som alt står i raden |
| 6 | 1963 | Usikkerhetskriteriene er skrevet for medieartikler | Gjelder KI-laget over meldinger, plan A (§4.6A, FR-603A l. 1558). KI-laget i v1 (Epic 10) forklarer signalet og har ingen usikkerhetskriterier | «Før KI-laget implementeres»: passert, men laget som ble bygget, er ikke det punktet gjelder | Utenfor v1 (plan B) |
| 8 | 1964 | Oppstart av tilbakekjøpsprogram filtreres bort (FR-502) | Meldingsfilteret, Epic 6 backlog, plan B | «Før innlevering», dato ukjent (punkt 13) | Utenfor v1 (plan B) |
| 9 | 1965 | Alpha Vantages vilkår | Alpha Vantage er forkastet som kilde (`docs/kilder-og-rettigheter.md` l. 38) og finnes ikke i `src/`, `tests/` eller README-en (`git grep` 02.11). Avkrysningen i `docs/kilder-og-rettigheter.md` l. 1336 står åpen | «Før innlevering», dato ukjent | Lukk: kilden brukes ikke i v1. Avkrysningen i `docs/kilder-og-rettigheter.md` rettes i samme runde |
| 11 | 1966 | Meldepliktig handel for primærinnsidere (FR-502) | Meldingsfilteret, plan B | «Etter én ukes drift» med meldinger, som aldri startet | Utenfor v1 (plan B) |
| 12 | 1967 | Horisont og hendelsestyper i FR-302 | Kommende hendelser er ute av v1 med plan B (§2 l. 162). Epic 7 er backlog | «Før implementasjon», ikke implementert | Utenfor v1 (plan B) |
| 13 | 1968 | Datoene for demonstrasjonen og prosjektinnleveringen | Ingen dato i repoet etter svaret 23.09 (`docs/innlevering.md`, C og D). Beskjeden 2.11 gjelder bare PRD-fila, med frist 5.11 | «Avventer Bård Inge», ingen dato | Åpent, eier Marian. Ny frist: spørsmålet stilles på nytt før rettingen onsdag 4.11, så rettingen kan føre svaret eller at det mangler |
| 15 | 1969 | Kategoriene i «ukjent» (FR-502) | Meldingsfilteret, plan B | «Etter én ukes drift» med meldinger, som aldri startet | Utenfor v1 (plan B) |
| 21 | 1970 | Emnesidens tredje del | Ikke besvart (`docs/innlevering.md`, «Hva emnesiden ikke sier») | «Sammen med punkt 13» | Åpent, eier Marian, sammen med 13 |
| 22 | 1971 | Kodegjennomgang som BMAD-steg, én per epic | Bare Epic 1 har sin egen gjennomgang (`kodegjennomgang-epic-1.md`, 27.09). Etter det har hver PR fått en gjennomgang med triage (`docs/kvalitetssikring.md` §5). Epic 2 er in-progress: v1-delen er flettet, og det som står igjen, er «Ekstra» | «Etter Epic 2», ikke utløst | Åpent, eier Gruppen. Ny frist: én samlet gjennomgang av v1-koden før README-prøven (funksjonsstoppen). Se spørsmål 4 |
| 25 | 1972 | Dagene Oslo Børs er stengt i 2027 | Ikke gjort: `DEKKEDE_AAR = frozenset({2026})` (`src/boersdag.py:22`), og `docs/kilder-og-rettigheter.md` l. 1114 har bare 2026. Om Euronext har publisert kalenderen for 2027, er ikke slått opp (ingen nettkall) | 2026-12-01, ikke passert | Åpent, eier Marian, frist 2026-12-01 som nå |

Med forslagene blir 5b og 9 lukket, 2, 4, 6, 8, 11, 12, 15 og 16 står utenfor
v1, og 13, 21, 22 og 25 står åpne med eier og frist.

---

## Resten: §4, §5, §7, «Kort fortalt» og formen

**B** er bygget annerledes enn kravet uten Rettet-linje, **C** gjelder
meldingsdelen uten merket for plan B, og **A** er ikke bygget. Alle A-ene er
«Ekstra, hvis tiden rekker» fra 19.10, og det står bare samlet i §2 (l. 174 og
194), ikke ved kravene.

| # | Linje | Krav | Funn og kilde | Forslag |
|---|---|---|---|---|
| R1 | 1014–1015 | FR-408 (B) | Teksten sier at `Vurderingslager.skriv` avviser enhver dato som ikke er inneværende børsdag. Første henting på dagtid i en tom base skriver forrige børsdag (2.3c, `2a84142d`, PR #87, unntaket fra AD-7 godkjent 22.10 kl. 19:30) | Rettet-linje ved FR-408 og FR-402 om unntaket |
| R2 | 1760 | NFR-01 (B) | Sier at målingen lar 2 kall stå igjen, og at alle bare brukes når brukeren selv kjører den. Fra `676fbc8b` kjører jobben målingen hver kveld med alle kallene som er igjen. Det står bare under FR-413 (l. 1199) | Linje ved NFR-01 som viser til FR-413 og svaret 28.10 kl. 22:17 |
| R3 | 1190, 1210–1212 | FR-413 (B) | Sier «aksjene i OBX som ikke er i lista, først», og at målingen går kl. 23:45 når én av de 15 mangler kursen. Bygget: de som aldri er målt, i rekkefølgen i lista fra `malinger.md` §40 (`spec-2-13-maalingen-av-omsetning.md`), og målingen går uansett hvor mange som mangler (svaret 29.10 kl. 09:20 a) | Endret-linje om rekkefølgen og svaret 29.10 kl. 09:20 |
| R4 | 504 | FR-106 (B) | Sier at markedsoversikten viser endringen per sektor. Bygget som egen side, `/boersometer` (`src/app.py:548`), et kart med én rute per aksje ordnet etter bransje (8.6 `7f1c1f09`, 8.6b `7f6d9e4c`) | Rettet-linje om egen side og kartet, med avgjørelsene fra `epics.md` under 8.6 |
| R5 | 632 | FR-202 (B) | Sier «begge linjene». Fra 2.9c (`24849dd9`, PR #64) tegnes hovedindeksen som en tredje, stiplet linje | Lagt til-linje ved FR-202 og FR-104 |
| R6 | 411–429 | FR-102 (B) | Selskap sorteres også A til Å ved klikk (8.15b, svaret 18.10 kl. 22:06, `src/markedsoversikt.py:357`), og det står ikke | Lagt til-linje |
| R7 | 819–820 | FR-401 (B, C) | Rekkefølgen «kurser, deretter meldinger, og til slutt dagens vurdering». Bygget: kurser, indeksen, vurderingen, KI-teksten og så målingen (`src/fetch_prices.py:54–72`), ingen meldinger | Rettet-linje med rekkefølgen som er bygget, og «meldinger» merket for plan B |
| R8 | 776–802 | §4.3, FR-301–303 (C) | Ingen merking for plan B i §4.3, bare i §2 (l. 162). Epic 7 er backlog | Merk overskriften «Utenfor v1 (plan B, 28.09)» |
| R9 | 872–905 | FR-404, FR-405 (C) | Etterfyllingen og avkortingen av meldinger fra NewsWeb er ikke merket. Story 6.2 er backlog | Merk begge «Utenfor v1 (plan B)» |
| R10 | 1234, 1275, 1309, 1318 | §4.5, FR-502, FR-503, «Resultat av filteret» (C) | Bare FR-501 er merket (l. 1273). Epic 6 er backlog | Merk overskriften i §4.5. Ved FR-503: FR-407 bygger nå på kursserien (l. 576) |
| R11 | 978 | FR-408, raden «Relevante meldinger» (C, A) | Feltet finnes ikke i `vurdering` (`src/migrasjoner/0002_vurdering.sql:22` sier at det kommer senere) | Merk raden «Utenfor v1 (plan B)» |
| R12 | 1700–1703 | FR-705 (C) | «Meldinger hentes for alle 15 selskapene ved hver henting» og KI-kostnaden per melding gjelder plan A | Merk de to setningene som plan A |
| R13 | 1813–1814 | NFR-05 (C) | Begrunnelsen viser til dedupliseringen i FR-501, som er plan A | Merknad om at henvisningen gjelder plan A |
| R14 | 328–336, 492–496 | FR-101, FR-105: periodevalget i oversikten (A) | Ikke på main. Story 8.17 er backlog, og 8.17a står på grenen i PR #106, stoppet før flettingen (`95673e07`, 30.10) | «Ikke bygget per 04.11, story 8.17 (ekstra)» ved kravet |
| R15 | 572–597 | FR-407 (A) | Ingen merking av utbytte- eller justeringsdager. Story 2.6 og 8.14 er backlog. L. 588 sier at kravet må være oppfylt før demonstrasjonen | «Ikke bygget, ekstra», og l. 588 får en Rettet-linje etter 19.10 |
| R16 | 322–326, 696–699 | FR-101 i kroner, FR-203 høy og lav (A) | Story 8.5 og 2.10 er backlog | «Ikke bygget, ekstra» |
| R17 | 668–676 | FR-202, volumsøyler og bånd (A) | Story 8.7 er backlog | «Ikke bygget, ekstra» |
| R18 | 739–761 | FR-205, FR-206 (A) | «Se nærmere» (8.4) og signaldagene (8.8) er backlog | «Ikke bygget, ekstra» |
| R19 | 763–772, 1214–1232 | FR-207, FR-414 (A) | Story 8.18 og 2.14 er backlog | «Ikke bygget, ekstra» |
| R20 | 512–542 | FR-107, FR-108 (A) | Story 8.12 og 8.11 er backlog | «Ikke bygget, ekstra» |
| R21 | 544–570 | FR-109, FR-110 (A) | Hjelpen bak «?» er bygget (8.0b, 8.0f). «Vis meg rundt» (8.9), «Lær noe nytt» (8.13) og Innstillinger (8.10, 8.10b) er backlog | «Delvis bygget» ved FR-109, «ikke bygget, ekstra» ved FR-110 |
| R22 | 1063–1070, 1144–1173 | FR-412, og «ikke i lista» i FR-409 (A) | Story 2.11 og 2.12 er backlog, og `tilstand` har ingen «ikke i lista». Oversikten viser de faste 15 | «Ikke bygget, ekstra» |
| R23 | 1134–1138 | FR-411, tillegget 08.10 (A) | Venter på 2.11, 2.13 og 2.14, og finnes ikke i `src/demo.py` | Merk at tillegget venter på de storyene |
| R24 | 1371, 1501–1507 | FR-607, og delen av FR-601 om den (A) | Story 10.6 er backlog | «Ikke bygget, ekstra» |
| R25 | 863–870 | FR-403 (A, delvis) | Story 2.4 er backlog, men hver henting tar hele serien (`src/fetch_prices.py:149`, FR-406), så et hull fylles uansett | Linje om at FR-403 oppfylles gjennom FR-406, og at kontrollen i 2.4 ikke er skrevet |
| R26 | 1879 | §7, «KI-bidrag i drift», «est. uke 45» | Uke 45 er denne uka, 2.–8.11. Datoen for demonstrasjonen er fortsatt ukjent (punkt 13), og raden er erstattet av «KI-forklaringen» | Rettet-linje: «est. uke 45» gjelder ikke lenger, datoen er ukjent (punkt 13) |
| R27 | 1875 | §7, «Brukerutfall» | Brukertesten (8.1) er ikke tatt. `docs/brukertest.md` sier at den tas «neste uke» (svaret 23.10 kl. 12:29), og den uka er passert | Ny dato fra gruppen, se spørsmål 7 |
| R28 | 1876, 1881 | §7, «Adopsjon» og «Fortsatt bruk» | Begge krever bruk som er «loggført». Repoet har ingen logg over hvilke dager vi brukte appen. `docs/ux-logg.md` fører det vi har sett om brukeropplevelsen, og jobbens logger ligger i `data/` | Avgjør hva som teller som loggført, se spørsmål 8 |
| R29 | 1884 | §7, «KI-forklaringen», «Én ukes drift er logget» | `ki_logg` får rader hver børsdag fra jobben, og 10.4 (måle bidraget) er ready-for-dev. Hvilke dager som utgjør uka, er ikke ført | Linje som sier hvilken uke som teller, med antallet rader, når den er regnet ut |
| R30 | 1885 | §7, «Kjørbar for andre» | «README-prøven fra en ren maskin i story 3.4». Prøven er utsatt til v1 er bygget og er funksjonsstoppen, senest én uke før innleveringen (svaret 21.10 kl. 18:33, `epics.md` l. 568). Ingen Rettet-linje i §7 | Rettet-linje om svaret 21.10 kl. 18:33 |
| R31 | 1890–1892 | §7, «Bundet til datoer som ikke er fastsatt» | Nevner FR-407, som er ekstra fra 19.10 | Rettet-linje om at FR-407 ikke er v1 |
| R32 | 1923 | §7, «Det skal leses når Dockerfilen skrives» | Dockerfilen er skrevet (3.1), og migrasjonene kjøres når basen åpnes (`kjoer_migrasjoner=True` som standard, `src/lagring_sqlite.py:92`), ikke som eget steg | Lagt til-linje om at det er lest, og at «Drift» holder |
| R33 | 1985 | §8, punkt 18 under «Lukket» | «Merk at selve filen ikke er skrevet». `Dockerfile` og `compose.yaml` finnes (story 3.1, 3.2) | Rettet-linje om at filen er skrevet i 3.1 |
| R34 | 2013, 2026 | §8, oppsummeringen og «Om eierfeltet» | Setningene teller punktene etter status og eier, og må stemme med det gruppen avgjør for punktene over | Skrives om onsdag, med en Rettet-linje, etter svarene på spørsmål 1–4 |
| R35 | 93–98 | «Kort fortalt», «Bygget per 28.10» | Nevner jobben fra 29.10, men ikke målingen av omsetning (2.13, `676fbc8b`, 29.10). «Status» i README-en nevner verken jobben eller målingen under «Ferdig», bare i avsnittet om Oppgaveplanlegging (README l. 413–417) | Begge oppdateres til samme dag onsdag, README-en i egen commit (regel 8) |
| R36 | 1–37 | Front matter | `title`, `status: final`, `created` og `updated` finnes. `updated` 2026-10-28T23:49 er fra siste endring, som kom på main med `676fbc8b` 29.10 | Ingen retting. `updated` settes fra klokka onsdag |
| R37 | hele fila | Lenker og ankre | De 14 lenkene og ankrene fører fram, og hver sti i kodeformat finnes (sjekket 02.11) | Ingen retting |

Min liste (8.3), «Signalet dag for dag» (2.7b) og børsometeret som egen side er
flettet, men har ikke eget FR i §4. Det er ikke ført som funn, fordi et nytt
krav ikke er en retting (spørsmål 10).

Ikke slått opp: at tallene i hjelpen hentes fra `Parametre` (FR-109), detaljene
i det bygde kartet mot FR-106, målingene slik aksjesiden viser dem (FR-706), at
modellversjonen føres for Ollama (FR-604, FR-605), og NFR-03, NFR-06 og NFR-08
i alle visningene.

---

## Spørsmål før rettingen onsdag

1. **Skal 6, 8, 11, 12 og 15 stå som utenfor v1 (plan B), som 2 og 16, og skal
   de sju flyttes til en egen tabell i §8?** Forslag: ja, i en ny tabell
   «Utenfor v1 (plan B)» under «Må følges opp», med numrene som før og eier
   Gruppen.
2. **Skal punkt 4 stå som utenfor v1, med frist «før 2.6, hvis den bygges»?**
   Forslag: ja, og i samme tabell som spørsmål 1, merket «ekstra, 19.10»
   i stedet for plan B.
3. **Skal 5b og 9 lukkes?** Forslag: ja. 5b med beslutningen 06.10 kl. 21:11,
   og 9 fordi Alpha Vantage ikke brukes i v1. Avkrysningen i
   `docs/kilder-og-rettigheter.md` rettes i en egen commit.
4. **Hva gjør vi med punkt 22?** Forslag: åpent, med én samlet
   `bmad-code-review` av v1-koden før README-prøven, eier Gruppen, i stedet
   for én per epic. Gjennomgangene per PR står som det de er.
5. **Skal faglærer spørres på nytt om datoene og den tredje delen (punkt 13 og
   21)?** Forslag: ja, av Marian før onsdag 4.11, og svaret eller at det
   mangler føres i `docs/innlevering.md` og i punkt 13.
6. **Hvordan skal kravene som ikke er bygget (R14–R25), merkes?** Forslag: en
   kort linje ved hvert krav, «Ikke bygget per 04.11, story N, ekstra fra
   19.10», så den som leser kravet, ser det der.
7. **Når tas brukertesten (8.1 og 10.4), og står «Brukerutfall» som mål for v1?**
   Forslag: før funksjonsstoppen, med datoen ført i `docs/brukertest.md` og i
   §7 med en Rettet-linje.
8. **Hva teller som «loggført» for «Adopsjon» og «Fortsatt bruk»?** Forslag:
   står det ingen logg over bruksdager, skriver §7 at målene ikke er målt, i
   stedet for å regne jobbens logger som bruk.
9. **Skal R1–R7 og R26–R33 rettes med Rettet- eller Lagt til-linjer slik
   tabellen foreslår?** Forslag: ja, én linje per krav, og ingen linje fjernes.
10. **Skal Min liste, historikken og børsometeret som egen side få en linje i
    §4?** Forslag: nei, ikke før 5.11. En henvisning i «Kort fortalt» til
    stories og README-en holder, fordi rettingen ikke skal lage nye krav.
11. **Skal `sprint-status.yaml` rettes samme dag (2.13, 9.5, 2.3c, 2.3d og
    3.5a–h)?** Forslag: ja, i en egen commit, fordi «Kort fortalt» og README-en
    viser til den.

*Avgjort 2026-11-02 kl. 22:15 (gruppens svar):* A) forslagene til spørsmål 1–4, 6
og 9–11 er godtatt. B) Punkt 13 og 21 står åpne som nå (spørsmål 5). C) Brukertesten
8.1 og 10.4 tas senere, uten dato ennå, og «Brukerutfall» står som mål for v1
(spørsmål 7). D) En brukslogg starter 4.11, med én linje for hver dag gruppen bruker
appen, og §7 sier at bruken ikke ble logget før (spørsmål 8). Ført 03.11 i
instruksjonen kl. 14:41.

*Lagt til 2026-11-03:* PRD-en er rettet før fristen 5.11, 03.11, etter gruppens svar 02.11 kl. 22:15. I `prd.md`: §8 i `c075b54e` (5b og 9 lukket, tabellen «Utenfor v1», R34), R1–R7 i `a79bd455`, R8–R13 i `b0cfa6b2`, R14–R25 i `3c74eff1`, R28 med brukslogga i `7d36abef`, R26, R27 og R29–R33 i `b33c1ae5`, og R35 like under «Kort fortalt» i `d8524821` (svaret 03.11 kl. 16:25, fordi «Kort fortalt» har høyst 400 ord). 126 linjer er lagt til i `prd.md`, og de 11 som er fjernet, er de ti flyttede radene i §8 og `updated`. Utenfor `prd.md`: Alpha Vantage i `docs/kilder-og-rettigheter.md` i `8a006032`, «Status» i README-en i `7f67d336`, `sprint-status.yaml` i `fb6d1051` og `docs/brukertest.md` i `ef5f627a`. `status` i `prd.md` står som final.
