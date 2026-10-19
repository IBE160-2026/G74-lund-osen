---
title: "Endringsforslag 19.10: endelig v1 er det briefen v8 lover"
status: final
created: 2026-10-19
updated: 2026-10-19T17:04
---

# Endringsforslag 19.10: endelig v1 er det briefen v8 lover

Laget med `bmad-correct-course` i modusen Batch, etter instruksjonen kl. 17:00 i
`docs/ai-prompts/2026-10-19.md`. Bygd opp som
[`sprint-change-proposal-2026-10-13.md`](sprint-change-proposal-2026-10-13.md).

**Godkjent av gruppen 19.10 kl. 15:43** (gruppens svar under «Prioritering» i
[`epics.md`](epics.md)). Egne nøkler (10.7) er v1 etter gruppens svar kl. 16:12,
og regelen for det ekstra er svaret kl. 14:48.

Grunnlaget er [briefen v8](product-brief.md) (taggen
`arbeidskrav-product-brief-v8`), [tilbakemeldingen 06.10](tilbakemelding-product-brief.md),
«Inne i v1» i [`prd.md`](prds/prd-G74-lund-osen-2026-09-20/prd.md) og
[`sprint-status.yaml`](../implementation-artifacts/sprint-status.yaml). Linjenumrene viser
til filene slik de sto på main 19.10 kl. 17:00.

## 1. Hva som utløste forslaget

**Omfanget vokste etter briefen.** Briefen v8, «Inne i v1», lover kjernen
(markedsoversikt og aksjedetalj med signalstyrke, retning og synlig begrunnelse),
KI-forklaringen med av/på-bryter, historikk, hovedindeks og «Min liste». Under
«The Solution» lenker aksjedetaljen «til selskapets investorside», og under «Data
og kilder» kan Gemini, Anthropic eller OpenAI velges med egen nøkkel. PRD-en har
mer under «Inne i v1»: «Se nærmere», KI-teksten om dagen, endringen i kroner, høy
og lav, og de femten «Fast i v1» fra endringsforslaget 08.10.

**Tilbakemeldingen 06.10** sier om omfanget: «Pass på at antall epics (til og med
Epic 10) ikke vokser videre», og om briefen: «Ellers beskriver briefen en annen app
enn den som leveres» (linje 58 og 23). Del 1 vurderes blant annet på «om appen
gjør det dere har beskrevet» (linje 79).

**Typen endring.** Ingen ny idé, og ingenting som er bygget, endres. Det som
endres, er hva som er lovet i v1. Det som ikke er lovet, kan fortsatt bygges, men
bare etter regelen kl. 14:48: på egen gren, og flettet bare ferdig og grønt. Det som
ikke er flettet ved funksjonsstoppen, README-prøven med ZIP-fila senest én uke før
innleveringen, står som plan for en senere versjon.

## 2. Virkninger

### Sjekklista i `bmad-correct-course`

| Del | Status | Funn |
|---|---|---|
| 1. Utløseren | [x] | Tilbakemeldingen 06.10 og svaret kl. 15:43. Ingen feil i det som er bygget |
| 2. Epics | [x] | Ingen ny epic og ingen epic som faller bort. Epic 2, 8 og 10 får ekstra storyer. Epic 5, 6 og 7 er ute av v1 fra 28.09 og røres ikke |
| 3. Dokumentene | [x] | `prd.md`, `epics.md`, `sprint-status.yaml` og vurderingsmatrisen. Spinen og `designregler.md` har ingen løfte om omfang som endres. Briefen røres ikke (regel 17) |
| 4. Veien videre | [x] | Direkte justering, uten tilbakerulling (punkt 3) |
| 5. Forslaget | [x] | Punkt 4 og 6 |
| 6. Overlevering | [x] | Punkt 8 |

### Epics

| Epic | Virkning |
|---|---|
| **Epic 2** | 2.7 er v1. 2.4, 2.6, 2.10, 2.11, 2.12, 2.13 og 2.14 blir ekstra |
| **Epic 3** | 3.4 er v1, som suksessmålet «Kjørbar for andre». Ingen ekstra |
| **Epic 8** | 8.1, 8.2 og 8.3 er v1. 8.4–8.14, 8.10b, 8.17, 8.18 og 8.19 blir ekstra |
| **Epic 9** | 9.2 er v1. 9.5 utgår, som avgjort 06.10 |
| **Epic 10** | 10.4, 10.5 og 10.7 er v1. 10.6 og 10.8 blir ekstra |
| Epic 1 og 4 | Ingen virkning: alle storyene er done |
| Epic 5, 6 og 7 | Ingen virkning: ute av v1 fra 28.09 (plan B) |

### Andre dokumenter

`prd.md`: en datert linje under «Inne i v1», under de femten «Fast i v1» og ved
FR-608. `epics.md`: en datert linje ved hver story som blir ekstra, og i
innledningen til Epic 2, 8 og 10. `sprint-status.yaml`: kommentarer, ingen ny
status. Vurderingsmatrisen: en datert linje under «Funksjonalitet og omfang».

## 3. Anbefalt vei

**Direkte justering, med et mindre løfte.** Ingenting rulles tilbake og ingenting
slettes. Storyene som blir ekstra, står med kontrollpunktene sine og kan bygges
etter regelen kl. 14:48.

- **Innsats:** liten. Bare daterte linjer og kommentarer.
- **Risiko:** liten. Ingen kode endres. Testene for dokumentene kjøres før push.
- **Tid:** v1 har fire storyer for appen igjen (2.7, 8.3, 10.5 og 10.7), og fem
  for suksessmålene og prosessen (3.4, 8.1, 8.2, 9.2 og 10.4).

## 4. Forslagene i detalj

### 4.1 Hver story som ikke er done og ikke er ute av v1

34 storyer i `sprint-status.yaml` er verken `done` eller under «Ute av v1» (Epic
5, 6 og 7): 9 er v1, 24 er ekstra, og 1 utgår.

#### I v1, fra briefen

| Story | Status | Grunnen |
|---|---|---|
| 2.7 Historikken i aksjedetaljen | in-progress | Briefen, «Inne i v1»: «historikk». 2.7a er flettet |
| 8.3 Min liste | backlog | Briefen, «Inne i v1»: «Min liste» |
| 10.5 Lenken til investorsiden | backlog | Briefen, «The Solution»: aksjedetaljen lenker «til selskapets investorside». Tittelen sier NewsWeb, men lenken går til investorsiden fra 06.10. Adressene er godkjent kl. 16:03 |
| 10.7 Egen nøkkel til Gemini, Anthropic og OpenAI | backlog | Briefen, «Data og kilder», og gruppens svar kl. 16:12 |

#### I v1, fra briefens suksessmål og prosessen

| Story | Status | Grunnen |
|---|---|---|
| 3.4 Demoversjonen | review | Suksessmålet «Kjørbar for andre» og README-prøven. Briefen: demoen «viser sensor alt i v1» |
| 8.1 Brukertest rett etter Epic 2 | backlog | Suksessmålet «Brukerutfall» |
| 10.4 Måle bidraget, egen brukertest etter 8.1 | backlog | Suksessmålet for KI-forklaringen, «KI-bidrag i drift» i storyen |
| 8.2 UX-gjennomgang av de to skjermbildene | backlog | Svaret kl. 15:43. Storyen følger opp beslutningen 22.09 om `bmad-ux`, og del 1 vurderes på om appen «er godt designet» (tilbakemeldingen, linje 79) |
| 9.2 `docs/ai-prompts/bygging/` | backlog | Svaret kl. 15:43. Emnesiden krever at det vises hvordan KI ble brukt |

#### Utgår

| Story | Grunnen |
|---|---|
| 9.5 Relevanseksperimentet, del 2 | Utgår fra 06.10 (beslutningen kl. 21:11, `prd.md` §7). Står i `epics.md` og som kommentar i `sprint-status.yaml` fra før, men med status `backlog` |

#### Ekstra, hvis tiden rekker

Grunnen er den samme for alle: briefen v8 lover dem ikke. Kolonnen «Hvor fra»
viser hvor de kom inn i v1.

| Story | Hvor fra |
|---|---|
| 2.4 Etterfylling av hull i kursserien | Epic 2 fra starten |
| 2.6 Utbyttedager merkes | Epic 2 fra starten (FR-407) |
| 2.10 Høy og lav lagres med kursene | «Inne i v1» 07.10, for 8.5 |
| 2.11 Lista leses fra basen | «Fast i v1» 08.10, egne aksjelister |
| 2.12 Velge og bytte aksjer | «Fast i v1» 08.10, egne aksjelister og «Følg en aksje» |
| 2.13 Kommandoen som måler omsetning | «Fast i v1» 08.10 |
| 2.14 Eks.datoer føres inn for hånd | «Fast i v1» 08.10 |
| 8.4 Se nærmere i aksjedetaljen | «Inne i v1» 02.10 (FR-205) |
| 8.5 Endring i kroner, og høy og lav | «Inne i v1» 07.10 (FR-101, FR-203) |
| 8.6 Børsometeret | «Fast i v1» 08.10 |
| 8.7 Sjekk 2 og 3 i kursgrafen | «Fast i v1» 08.10 |
| 8.8 Signaldager i kursgrafen | «Fast i v1» 08.10 |
| 8.9 «Vis meg rundt» | «Fast i v1» 08.10 |
| 8.10 Innstillinger øverst | «Fast i v1» 08.10 |
| 8.10b «Vis KI-tekst» i Innstillinger | Endringsforslaget 13.10. Bryteren finnes alt på aksjesiden (svaret 18.10 kl. 11:20) |
| 8.11 Ferdige lister og filter på signalet | «Fast i v1» 08.10 |
| 8.12 Endret signalstyrke siden forrige børsdag | «Fast i v1» 08.10 |
| 8.13 Lær noe nytt | «Fast i v1» 08.10 |
| 8.14 Justeringsdager i kursgrafen | «Fast i v1» 08.10 |
| 8.17 Periodevalget i oversikten, Min liste og børsometeret | «Fast i v1» 08.10 (periodevalg likt overalt) |
| 8.18 Kommende eks.dato i kursgrafen | «Fast i v1» 08.10 |
| 8.19 Neste henting i stripa øverst | Endringsforslaget 13.10 (svar 13) |
| 10.6 KI-teksten om dagen på forsiden | «Inne i v1» 02.10 (FR-607) |
| 10.8 ChatGPT med «Sign in with ChatGPT» | FR-608: «kommer senere» |

### 4.2 `prd.md`

Ingen krav slettes, og ingen ordlyd endres. Tre daterte linjer:

- **Under «Inne i v1»** (linje 94–110): endelig v1 er det briefen v8 lover, og
  resten av lista er ekstra, med regelen kl. 14:48.
- **Under de femten «Fast i v1»** (linje 112–128): alle femten er ekstra. 8.15 og
  8.16 er flettet og står, og periodevalget i oversikten (8.17) er ekstra.
- **Ved FR-608** (linje 1409): egen nøkkel til Gemini, Anthropic og OpenAI (10.7)
  er v1. ChatGPT med «Sign in with ChatGPT» (10.8) er ekstra.

### 4.3 `epics.md`

En datert linje ved hver av de 24 storyene i «Ekstra» i punkt 4.1, og i
innledningen til Epic 2, 8 og 10 om hvilke storyer i epicen som er v1 og hvilke
som er ekstra.

### 4.4 `sprint-status.yaml`

Statusene endres ikke, så `backlog` blir stående for de ekstra. En kommentar over
de ekstra i hver epic, et merke på 9.5 om at den utgår (kommentaren fra 06.10 står),
og en kommentar ved 10.5 om at den er lenken til investorsiden (06.10). Nøklene
endres ikke, så testene for fila holder.

### 4.5 README-en

«Neste i v1» har Min liste, historikken, lenken til investorsiden og egen nøkkel,
de fire storyene for appen i v1. «Ekstra, hvis tiden rekker» har signaldagene,
innstillingene, forsiden og å velge og bytte aksjer, som alle er ekstra her. Lista
er ikke fullstendig, men ingenting står i feil liste, så «Status» endres ikke.
README-en får bare lenken til dette forslaget under «Dokumentene» (regel 19). Storyene for suksessmålene og prosessen er ikke punkter for appen og
står ikke i «Status».

## 5. Fra README-prøven

Ingen endring. README-prøven er funksjonsstoppen, og den er ikke tatt ennå.

## 6. Hva som må endres

| Dokument | Endring |
|---|---|
| `prd.md` | Tre daterte linjer (punkt 4.2), og `updated` |
| `epics.md` | 24 daterte linjer ved storyene og tre i innledningene (punkt 4.3) |
| `sprint-status.yaml` | Kommentarer (punkt 4.4), og `last_updated` |
| `docs/vurderingsmatrise.md` | En datert linje under «Funksjonalitet og omfang» |
| `README.md` | Bare lenken til dette forslaget under «Dokumentene», i samme commit som forslaget (regel 19, punkt 4.5) |
| Briefen | Ingen (regel 17) |
| Spinen og `designregler.md` | Ingen |
| Kode og tester | Ingen |

## 7. Åpne punkter

1. **Statusen på 9.5** er fortsatt `backlog` i `sprint-status.yaml`. Forslaget
   gir den et merke, ikke en ny status, fordi statusene i fila er BMAD sine.
2. **Tittelen på 10.5** sier fortsatt NewsWeb. Den står, som avgjort 06.10.

## 8. Overlevering

**Omfang: lite.** Ingen ny epic, ingen ny story og ingen endring i koden. Bare
hva som er lovet i v1.

**Rekkefølgen for føringene**, én commit per dokument:

1. `prd.md`
2. `epics.md`
3. `sprint-status.yaml`
4. Vurderingsmatrisen

**Suksesskriterier:**

- Hver av de 34 storyene i punkt 4.1 er merket som v1, ekstra eller utgått, likt i
  `epics.md` og `sprint-status.yaml`
- PRD-en sier hva i «Inne i v1» og «Fast i v1» som er ekstra, uten at noe krav er
  borte
- README-en, «Neste i v1» og «Ekstra», stemmer med lista
- Testene for dokumentene består
