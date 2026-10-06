# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G74 – G74-lund-osen |
| **Product brief** | `_bmad-output/planning-artifacts/product-brief.md` (commit e62ea77, versjon 7) |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Godt utgangspunkt med justeringer.** Gruppen kan gå videre og innarbeide punktene under.

Vurderingen gjelder briefen i versjon 7. Vi har sett på PRD, arkitektur, epics og endringsforslaget fra 28.09 som kontekst, men det er briefen som vurderes.

**Det som er bra:**

1. Briefen bygger på egne målinger i stedet for antakelser: 121 børsmeldinger på fire uker, der nær 29 % er tilbakekjøpsrapporter og drøyt 26 % er dubletter på norsk og engelsk, og testene 17.09 og 21.09 som viste at nyhetstreff på et symbol ofte handler om andre selskaper. Det gir et svært konkret problem.
2. Prinsippet «regler sorterer, KI forklarer», med av/på-bryter for KI-laget, gjør KI-bidraget etterprøvbart og testbart. Avklaringen av bruksvilkår med EODHD og Euronext, og en ferdig plan B, viser at dere har tenkt på risiko før dere bygger. Historikken med 30 versjoner av briefen viser en tydelig, sporbar prosess.

**De viktigste endringene:**

1. Briefen beskriver fortsatt børsmeldinger og kommende hendelser som en del av v1, men README sier at Euronext ikke ga tillatelse, og at plan B gjelder. Lag en ny versjon av briefen (eller et kort tillegg) som beskriver v1 etter plan B, siden v7 er låst med tag. Ellers beskriver briefen en annen app enn den som leveres.
2. Suksesskriteriet «KI-bidrag i drift» handler om meldinger KI-laget forklarte eller omklassifiserte. Det faller bort med plan B. Formuler et nytt, sjekkbart kriterium for KI-laget slik det blir nå (forklaring av signalet ut fra utledede verdier).
3. Legg til minst ett funksjonelt kriterium for signalberegningen, for eksempel at signalstyrke og retning for en kjent kursserie gir et bestemt, forhåndsberegnet resultat. Kriteriene i dag handler om brukerutfall og eksperimenter, ikke om at beregningene er riktige.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Vanskelig**

**Sammenlignbart med:** Forslagene 3) og 4) på nivå: domenelogikk som må stemme (tekniske indikatorer og signalstyrke), flere moduler som henger sammen (henting, lagring av daglig historikk, regelbasert vurdering og KI-forklaring) og eksterne kilder med vilkår. Med plan B (uten børsmeldinger) blir omfanget noe mindre, men fortsatt i nedre del av vanskelig.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | Høy | Tekniske indikatorer, signalstyrke og retning, faktorer som bidro, og regler for grovsortering. Feil i beregningene gir feil signaler som brukeren ikke kan avsløre selv. |
| Datamodell – antall entiteter og relasjoner mellom dem | Middels | Aksje, daglige kurser, daglig vurdering, faktorer, KI-logg og målinger. Historikk som ikke kan etterfylles gjør datamodellen viktig. |
| Brukere, roller og innlogging | Lav | Brukerkontoer og innlogging er ute av v1. Et godt valg. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | Middels | Avgrenset KI-lag som forklarer, med merking av usikre vurderinger og av/på-bryter. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | Høy | EODHD med 20 kall i døgnet, og avklaring av NewsWeb og Euronext. Vilkår begrenser hva som kan deles. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | Lav | Daglig henting, ingen sanntid. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | Lav | Ingen opplasting. |
| Sikkerhet og personvern | Lav–middels | Ingen personopplysninger. API-nøkkelen holdes i `.env`. Briefen er tydelig på at signalstyrke ikke er en kjøps- eller salgsanbefaling. |

**Hva vanskelighetsgraden betyr for dere:**

- _Vanskelig:_ Et vanskelig prosjekt gir større mulighet for toppkarakter, men også større risiko. Definer en minimal versjon som sikkert kan bli ferdig, og legg resten i tydelige trinn etterpå. Dere har allerede gjort mye av dette med epics og plan B. Sørg for at markedsoversikt og aksjedetalj med regelbasert signal er ferdig og stabil i demoversjonen før KI-laget bygges ut.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | OK | Omfanget i v1 er tydelig avgrenset (ingen innlogging, portefølje eller sanntid), og git-loggen viser at dere er godt i gang med implementeringen. Pass på at antall epics (til og med Epic 10) ikke vokser videre. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | OK | Briefen er svært konkret, og PRD og arkitektur bygger tydelig på den. Det eneste hullet er at briefen ikke er oppdatert etter plan B. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | Python-webapp med SQLite, tester og CI er godt dokumentert. Docker for demoversjonen øker oppsettet litt, men er vanlig. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | Risiko | Tekniske indikatorer er lette å få subtilt feil. Kontroller dem mot håndregnede eksempler eller en uavhengig kilde, og dokumenter det. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | OK | Regelbasert analyse og av/på-bryter for KI gjør det mulig å teste kjernen uten KI. Faste kursserier i demoversjonen egner seg godt som testdata. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | Risiko | Den ekte versjonen krever egen EODHD-nøkkel. Demoversjonen uten nøkkel er riktig løsning, men den er ennå ikke bygget. Prioriter den. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | Risiko | EODHD-gratisnivå er avklart. Briefen sier ikke hvilken språkmodell KI-laget bruker, eller hva den koster. Av/på-bryteren gjør at appen virker uten, og det er bra. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart som beskrevet.**

Forutsetningen er at briefen oppdateres til plan B, og at demoversjonen blir ferdig.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Oppdater scope i briefen: flytt børsmeldinger og kalender over kommende hendelser til «Utenfor v1» med henvisning til svaret fra Euronext, og beskriv hva KI-laget forklarer i stedet.
2. La demoversjonen med oppdiktede selskaper være den versjonen sensor bruker, og sørg for at alle funksjoner i v1, også KI-laget i av-modus, kan vises der.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | OK | Svært tydelig: én oversikt som svarer på hva som beveget seg, hvorfor, og hva som kommer, på omtrent fem minutter. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Sorteringsproblemet og forklaringsproblemet er underbygget med egne målinger. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | Juster | God beskrivelse av markedsoversikt og aksjedetalj. Oppdater delen om børsmeldinger etter plan B. |
| What Makes This Different – er vurderingen ærlig og realistisk? | OK | Ærlig: ingen teknisk fordel, men synlig skille mellom kode og KI. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | OK | Sparer med 10–30 norske aksjer og begrenset tid. Ærlig om at det ikke er gjort brukerundersøkelse. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Juster | Brukerutfallet (under 5 minutter, uten hjelp) er sjekkbart. «KI-bidrag i drift» må skrives om etter plan B, og det mangler kriterier for at beregningene er riktige. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Endre | Inn/ut er tydelig, men «Inne i v1» stemmer ikke lenger med plan B. Oppdater i en ny versjon. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | Personlig oppfølging og portefølje er naturlig neste steg og holdt utenfor v1. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | OK | Svært sporbar prosess: mange versjoner av briefen, lenker til PRD og målinger, lagrede prompts og endringsforslag. Hold briefen i takt med plan B. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | OK | Tydelig kjerneflyt og godt avgrenset v1. Endringen i omfang etter plan B er begrunnet, og det bør også stå i briefen. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Juster | Regelbasert kjerne og CI er et godt grunnlag. Legg til suksesskriterier for at signalberegningen er riktig, slik at testene kan spores tilbake til briefen. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | OK | Morgenoversikten på fem minutter og synlig skille mellom regler og KI i grensesnittet er tydelige designmål. Det finnes også egne designregler. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | OK | Briefen holder seg til problem og løsning. Arkitekturen ligger i eget dokument med gjennomganger. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Risiko | Krever egen EODHD-nøkkel inntil demoversjonen er ferdig. Prioriter demoversjonen, og test README fra en ren maskin. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | OK | Tydelig plan i README for hva som ikke ligger i repoet (`.env`, `data/`, `local-tests/`, `_privat/`). |

## 3. Neste steg for gruppen

1. Lag en ny versjon av briefen (v8) som beskriver v1 etter plan B, med oppdatert Solution, Scope og suksesskriteriet for KI-laget.
2. Legg til ett eller to suksesskriterier for at signalstyrke og indikatorer beregnes riktig, med kjente kursserier og forventede resultater.
3. Fullfør demoversjonen uten nøkkel, og test hele README-oppskriften fra en ren maskin.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
