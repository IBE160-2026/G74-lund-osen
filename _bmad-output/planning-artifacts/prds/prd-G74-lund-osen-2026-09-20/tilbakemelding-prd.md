# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G74 – G74-lund-osen |
| **PRD vurdert** | `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md` (status `final`, sist endret 2026-11-11, commit 10265324) |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

PRD-en har en tydelig tese («regler regner, KI formulerer», forklarbarhet i stedet for treffsikkerhet), målte tall bak terskelene og ærlig omtale av plan B, kvote og rettigheter. Risikoen er formen: med ca. 2 260 linjer, 28 700 ord og ca. 55 FR er dokumentet blitt en endringslogg der «Lagt til/Rettet»-linjer ligger oppå krav som ikke lenger gjelder. Den som skal lage UX, stories eller tester, må selv finne ut hva som er gjeldende. Innholdet er sterkt, men PRD-en trenger konsolidering.

## 2. Dette fungerer godt

1. **Testbar kjerne.** FR-701: trend slår ut «når kursen ligger mer enn 2 % over eller under snittet», bevegelse ved «ett standardavvik av siste 20 dagers endringer». FR-702/703 har målte andeler (styrke 0 hos 12,7 %). Dette kan bli testtilfeller direkte, og §7 «Riktige beregninger» knytter dem til håndregnede eksempler.
2. **KI-bruken er styrt.** FR-601 (bryter), FR-603 («En tekst som ikke består, vises ikke, men logges»), FR-604/605 (logg med promptversjon og modell), NFR-04, FR-411 (demo uten nøkkel) og NFR-01 (kvote). Det dekker usikre svar, kostnad og testmodus. FR-603 er ærlig: «Kontrollen er grov.»
3. **Ærlige avveininger.** §7: «Ingenting utløses av et menneske» er «Gitt opp. Det var et valg.» Motmålene: «Vi setter ikke mål for hvor godt signalene treffer markedet.» At «Brukerutfall» ikke er nådd (10.11), står åpent.

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | sterk | Valg og det som ble gitt opp er skrevet ut og datert. |
| Substans | sterk | Egne målinger bærer kravene; ingen pynt. |
| Strategisk sammenheng | sterk | Funksjonene tjener «forklar hvorfor en aksje skiller seg ut». |
| Testbarhet | god | Signal og KI-kontroll er testbare; mange andre FR-er er fortelling. |
| Scope og avgrensning | god | Plan B og «Ekstra» er eksplisitt, men status står på fem steder. |
| Brukbarhet for neste fase | svak | Lagdelt tekst, ingen glossar eller brukerreiser, kode i kravene. |
| Formtilpasning | svak | Brukerrettet app uten UJ, og en endringslogg i stedet for kravregister. |

## 4. Viktigste forbedringer

### 4.1 Gjeldende krav må kunne leses uten å følge historikken
- **Alvorlighet:** høy
- **Hvor:** §4.2 FR-201: «Kursgrafen viser seks måneders historikk, fast i v1», fulgt av «Rettet 2026-10-08 … perioden er ikke lenger fast». Samme mønster i FR-101 («de 15 aksjene» mot FR-412, opptil 18), FR-202 («tegnes ikke i v1») og NFR-01 (fem, så fire, så én kalls margin).
- **Problem og hvorfor det betyr noe:** Den som leser første setning, bygger eller tester feil. Git og `begrunnelser.md` kan bære historikken.
- **Forslag:** Skriv hvert krav om til én gjeldende tekst, og flytt «Rettet/Lagt til» til en endringslogg. Eksempel FR-201: «Brukeren kan velge periode i kursgrafen: siste børsdag, 1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år eller «Velg dag». Grafen åpner med 6 mnd. *Konsekvenser:* har serien færre dager enn perioden, tegnes det som finnes, og grafen sier det. Startdagen for hver periode er den samme i oversikten og grafen.»

### 4.2 Gi alle FR-er testbare konsekvenser
- **Alvorlighet:** høy
- **Hvor:** FR-407 «Utbyttedager skal derfor merkes i grensesnittet»; FR-109 «Et tips skal ikke kunne leses som et råd»; NFR-06 «Ingen del av grensesnittet skal formuleres som en anbefaling»; §7 «ryddig, gjennomarbeidet grensesnitt».
- **Problem og hvorfor det betyr noe:** Stories får akseptkriterier fra FR-ene, men bare FR-6xx og FR-7xx har dem.
- **Forslag:** FR-108: «*Konsekvenser:* med filteret på vises bare aksjer med styrke 3 og retning Positiv eller Negativ; styrke 3 med Blandet vises ikke; uten filter vises hele lista; ingen API-kall.» NFR-06: «Ingen tekst i maler, hjelp eller KI-tekst inneholder ord fra rådlista i FR-603; en test går gjennom malene.»

### 4.3 Legg til én brukerreise og et glossar
- **Alvorlighet:** medium
- **Hvor:** §1 («en vanlig sparer»), §7 («Hovedflyten» i én setning). Ordbruken glir: sektor/bransje, aksjedetaljen/aksjesiden, lista/aktiv liste/Min liste, vurdering/signal.
- **Problem og hvorfor det betyr noe:** UX trenger en scene å tegne skjermer rundt, og stories trenger faste begreper.
- **Forslag:** «UJ-1. Kari, som følger 12 aksjer ved siden av studiene, åpner appen om kvelden, ser at to aksjer har styrke 3, åpner den ene og leser de tre sjekkene med målingene. *Climax:* hun kan forklare hvorfor aksjen skiller seg ut. *Edge:* henting mangler i dag, og siden viser siste kjente dag.» Legg til 8–10 termer i et glossar.

### 4.4 Ta implementasjonsdetaljer og byggestatus ut av kravene
- **Alvorlighet:** medium
- **Hvor:** FR-105 «`bygg_soeyler` og `bygg_soeyler_perioden`»; FR-104 «`eldre_enn_nyeste`, story 1.4c»; FR-410 «Migreringen er `0006`»; «ikke bygget per 3.11».
- **Problem og hvorfor det betyr noe:** Kravene blir utdatert ved hver commit, og arkitekturen skal eie dette.
- **Forslag:** Behold den observerbare konsekvensen («En aksje uten kurs for tabellens dag står i tabellen med sin egen siste dag, men får ingen søyle») og flytt navn og hasher til epics eller arkitektur.

### 4.5 Samle scope-status i én tabell
- **Alvorlighet:** medium
- **Hvor:** §2 «Inne i v1», «Fast i v1», «Ekstra, hvis tiden rekker», «Hvis vi rekker», §8 «v1.1»; ca. 15 plan A-krav (FR-301–303, 404–405, 501–503, 602A–606A) ligger i hoveddelen.
- **Problem og hvorfor det betyr noe:** Statusen finnes, men må settes sammen av leseren.
- **Forslag:** Én tabell «FR | kjerne / ekstra / senere | bygget?», og plan A i vedlegg.

## 5. Mekaniske funn

- Ingen glossar, UJ eller Assumptions Index. Bare to `[ANTAKELSE]` (FR-302, FR-501) og tre `[FORELØPIG]`, alle i plan A.
- FR-ID-ene er unike, men ikke sammenhengende (FR-407 ligger i §4.1; dokumentert). Ingen brutte krysshenvisninger funnet.
- Suksessmålene mangler ID (SM-1 …) og henvisning til FR.
- Foreldet tekst: FR-401 «kravteksten over står uendret».
- Beslutninger er tilskrevet enkeltpersoner ca. 95 steder, selv om en felles rettelse står øverst.

## 6. Før dere går videre

**Må avklares før UX, arkitektur og epics:**
- Hva som er gjeldende tekst per krav (4.1), og hva som er kjerne mot ekstra (4.5). UX trenger én liste.
- Hovedflyten som brukerreise (4.3).

**Kan vente:** punkt 13 og 21 (venter på faglærer), plan A-punktene, og om «under 5 minutter» skal stå eller UX endres etter testen 10.11.

**Oppfølging av briefen:** ja. Plan B er gjennomført, «KI-forklaringen» erstatter det gamle KI-kriteriet, «Riktige beregninger» gir et funksjonelt kriterium, og demo uten nøkkel (FR-411) og KI-kostnad (FR-608, NFR-01) er beskrevet.

## 7. Refleksjonsspørsmål

1. Når en beslutning endret et krav, la dere til en datert linje i stedet for å skrive om kravet. Hva ga det dere, og hva koster det den som skal lese kravet?
2. FR-603 sier «Kontrollen er grov». Hvordan ville dere oppdage en KI-tekst med riktige tall, men misvisende mening, og kan dere skrive det som en testbar konsekvens?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
