---
title: "Product Brief: OSE Signal"
status: final
created: 2026-09-20
updated: 2026-09-24T22:54
---

# Product Brief: OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde  
**Gruppe:** G74 – Joakim Lund, Marian Osen  
**Status:** Arbeidskrav på 1–2 sider, innleveringsfrist søndag 27.09.2026. Låst med git-taggen `arbeidskrav-product-brief-v3`. Versjon 2 i full lengde: [product-brief-tillegg.md](product-brief-tillegg.md).

## Executive Summary

En vanlig sparer som følger norske aksjer bruker flere tjenester for å finne ut det samme: hva beveget seg i går, hvorfor, og er det noe viktig på vei. OSE Signal er en norsk webapplikasjon for PC som samler dette i én oversikt, slik at spørsmålet kan besvares på omtrent fem minutter om morgenen. Beregninger og grovsortering av meldinger gjøres med vanlig programkode. KI brukes der språkforståelse gir en reell fordel: å forklare hva en børsmelding betyr, og å vurdere relevans der kategorifeltet ikke strekker til.

## The Problem

Den som følger 10–30 norske aksjer ved siden av jobb eller studier har ikke et informasjonsproblem, men et sorteringsproblem: kurser, meldinger og rapportdatoer finnes, men ligger spredt, og det meste er irrelevant akkurat i dag. I tillegg kommer forklaringsproblemet: gratis markedsoversikter viser at en aksje er opp 4 %, men ikke hvorfor.

I vår test 17.09 handlet flertallet av de ti siste nyhetstreffene for et stort finansselskap om andre selskaper, så en nyhet knyttet til et symbol handler ikke nødvendigvis om selskapet bak symbolet. I børsmeldingene for selskapene løsningen skal dekke, målte vi 121 meldinger på fire uker. Nær 29 % er ukentlige statusrapporter om tilbakekjøp av egne aksjer, med samme ordlyd hver gang. Drøyt 26 % er samme melding publisert to ganger, på norsk og på engelsk.

## The Solution

**Markedsoversikten** viser omtrent 15 likvide Oslo Børs-aksjer med kursutvikling, signalstyrke og retning. **Aksjedetaljen** svarer på hvorfor: kursgraf, noen få tekniske indikatorer, hvilke faktorer som bidro, relevante børsmeldinger med lenke til originalen, og kommende hendelser. Meldingene kommer ferdig merket med utsteder og kategori, så grovsorteringen gjøres med regler i kode. KI brukes på det som passerer, og tvilsomme vurderinger merkes som usikre. **Prinsippet** er at KI-laget kan slås av. Applikasjonen skal fungere med den regelbaserte analysen alene. Det gjør KI-bidraget etterprøvbart. Signalstyrke er ikke en anbefaling om kjøp eller salg.

## Data og kilder

Kursdata hentes fra EODHD, børsmeldinger fra Oslo Børs' NewsWeb og finansielle hendelser fra Euronext. EODHD har gitt skriftlig godkjenning med betingelser. Universet er satt til omtrent 15 aksjer fordi gratisnivået gir 20 API-kall i døgnet, ett per symbol. NewsWeb og Euronext krever skriftlig tillatelse på forhånd til automatisert henting. Forespørselen er sendt 21.09, og det hentes ikke fra NewsWeb før Euronext har svart. Får vi nei, eller ikke svar innen 28.09, bygges løsningen uten meldingsdelen og kalenderen over kommende hendelser: KI-laget forklarer da signalet i stedet for børsmeldingene, ut fra tall vi har regnet ut av kursene og ikke ut fra kursene selv.

## What Makes This Different

Vi har ingen teknisk fordel andre ikke kan kopiere. Den viktigste forskjellen er at kode og KI holdes fra hverandre: regler sorterer, KI forklarer, og grensen er synlig i grensesnittet — ikke bare i koden. Vi lover ikke bedre signaler enn andre, men at brukeren alltid kan se hva som ga utslaget.

## Who This Serves

Primærbrukeren er en vanlig sparer med begrenset tid som vil ha oversikt uten å bli finansanalytiker. Vi er selv i målgruppen, men har ikke gjennomført en brukerundersøkelse.

## Success Criteria

| Signal | Mål |
|---|---|
| Brukerutfall | *Før prosjektinnlevering:* minst én person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut, under 5 minutter, uten hjelp |
| KI-bidrag i drift | *Før demonstrasjon:* dokumenterte eksempler fra minst én ukes drift på meldinger som KI-laget forklarte eller omklassifiserte, og som regelfilteret alene ikke skilte |
| Relevanseksperiment | *Innsamling og merking uke 39–40 (plan), KI-kjøringen når KI-laget finnes:* 50 manuelt merkede medieartikler kjørt mot symbolmatching og KI-klassifisering; tallene dokumenteres uansett utfall |

Ved kildefeil vises siste kjente data med tidsstempel, og «ingen tydelige signaler» er et gyldig svar. Vi setter ikke mål for hvor godt signalene treffer markedet.

## Scope

**Inne i v1:** markedsoversikt og aksjedetalj; signalstyrke og retning med synlig begrunnelse; børsmeldinger sortert av regler og forklart av KI; av/på-bryter for KI-laget; kommende finansielle hendelser.

**Utenfor v1:** brukerkontoer, innlogging og personlig portefølje; varsler, betaling, mobiltilpasning og meglerintegrasjon; flere børser og flere språk; fundamental- og verdimodell, intradag og sanntidsdata; statistisk studie av om signalene slår markedet.

## Vision

Hvis første versjon fungerer, er neste steg personlig oppfølging: favorittaksjer, egne lister og til slutt brukerens egen portefølje. Da blir OSE Signal en personlig markedsassistent.
