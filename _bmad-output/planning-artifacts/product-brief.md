---
title: "Product Brief: OSE Signal"
status: final
created: 2026-09-20
updated: 2026-10-06T23:00
---

# Product Brief: OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde  
**Gruppe:** G74 – Joakim Lund, Marian Osen  
**Status:** Versjon 8, etter plan B og faglærers tilbakemelding 06.10: v1 uten børsmeldinger, KI som forklarer signalet, og nye suksesskriterier. Versjon 7 står i taggen `arbeidskrav-product-brief-v7`.

## Executive Summary

En vanlig sparer som følger norske aksjer, bruker flere tjenester for å finne ut hva som beveget seg i går, og hvorfor. OSE Signal er en norsk webapplikasjon som kjører lokalt og samler dette i én oversikt, så spørsmålet kan besvares på omtrent fem minutter. Vanlig programkode regner ut signalene, og KI forklarer dem med ord.

## The Problem

Den som følger 10–30 norske aksjer ved siden av jobb eller studier har ikke et informasjonsproblem, men et sorteringsproblem: kurser, meldinger og rapportdatoer finnes, men ligger spredt, og det meste er irrelevant akkurat i dag. I tillegg kommer forklaringsproblemet: gratis markedsoversikter viser at en aksje er opp 4 %, men ikke hvorfor.

I vår test 17.09 handlet flere av de ti siste nyhetstreffene for et stort finansselskap om andre selskaper, og i en kjøring 21.09 med tidsstempel og rådata gjaldt det flertallet. En nyhet knyttet til et symbol handler altså ikke nødvendigvis om selskapet bak symbolet. I børsmeldingene for selskapene løsningen skal dekke, målte vi 121 meldinger på fire uker. Nær 29 % er ukentlige statusrapporter om tilbakekjøp av egne aksjer, med samme ordlyd hver gang. Drøyt 26 % er samme melding publisert to ganger, på norsk og på engelsk.

## The Solution

**Markedsoversikten** viser 15 likvide Oslo Børs-aksjer med kursutvikling, signalstyrke og retning, så brukeren ser hvilke få det er verdt å lese børsmeldinger om på NewsWeb. **Aksjedetaljen** svarer på hvorfor: kursgraf og de tre sjekkene med tallene bak. Den lenker til selskapets investorside. **KI-laget** forklarer signalet ut fra fortegn, styrke, retning og antall. Teksten merkes «Laget av KI» og kontrolleres mot grunnlaget før den vises. **Prinsippet** er at KI-laget kan slås av, og appen fungerer med reglene alene. Det gjør KI-bidraget etterprøvbart. Signalstyrke er ikke en anbefaling om kjøp eller salg. **Demoversjonen**, med oppdiktede selskaper og uten nøkkel, viser sensor alt i v1, også med KI av.

## Data og kilder

Kursdata hentes fra EODHD, som har gitt skriftlig godkjenning med betingelser. Gratisnivået gir 20 API-kall i døgnet, ett per aksje, og derfor 15 aksjer. NewsWeb og Euronext krever skriftlig tillatelse til automatisert henting og lenker. Euronext svarte ikke innen 28.09, så børsmeldinger og hendelser er ute av v1. KI-laget bruker den lokale modellen Gemma 4 E4B, gratis og uten nøkkel. Gemini, Anthropic eller OpenAI kan velges med egen nøkkel. Ingen del av v1 krever betaling.

## What Makes This Different

Vi har ingen teknisk fordel andre ikke kan kopiere. Den viktigste forskjellen er at kode og KI holdes fra hverandre: regler sorterer, KI forklarer, og grensen er synlig i grensesnittet — ikke bare i koden. Vi lover ikke bedre signaler enn andre, men at brukeren alltid kan se hva som ga utslaget.

## Who This Serves

Primærbrukeren er en vanlig sparer med begrenset tid som vil ha oversikt uten å bli finansanalytiker. Vi er selv i målgruppen, men har ikke gjennomført en brukerundersøkelse.

## Success Criteria

| Signal | Mål |
|---|---|
| Brukerutfall | *Før prosjektinnlevering:* minst én person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut, under 5 minutter, uten hjelp |
| Riktige beregninger | *Ved hver testkjøring:* håndlagde kursserier gir forhåndsberegnet styrke og retning. *Kontrollert 06.10:* to ekte aksjer og dager, regnet for hånd, stemmer med appen |
| KI-forklaringen | *Før demonstrasjon:* hver KI-tekst som vises, har bestått kontrollen mot grunnlaget (retning, styrke, tall, råd, gjetning), og testene viser at feil stoppes. Én ukes drift er logget |
| Kjørbar for andre | *Før prosjektinnlevering:* README-oppskriften fullføres gratis på en ren maskin, uten gruppens nøkler: demoen uten konto, og den ekte versjonen med egen gratiskonto hos EODHD |

Ved kildefeil vises siste kjente data med tidsstempel, og «ingen tydelige signaler» er et gyldig svar. Vi setter ikke mål for hvor godt signalene treffer markedet.

## Scope

**Inne i v1:** først kjernen, stabil i demoen: markedsoversikt og aksjedetalj med signalstyrke, retning og synlig begrunnelse. Deretter KI-forklaringen med av/på-bryter, historikk, hovedindeks og «Min liste».

**Utenfor v1:** børsmeldinger og kommende hendelser; brukerkontoer, innlogging og personlig portefølje; varsler, betaling, mobiltilpasning og meglerintegrasjon; flere børser og flere språk; fundamental- og verdimodell, intradag og sanntidsdata; statistisk studie av om signalene slår markedet.

## Vision

Neste steg er personlig oppfølging: egne aksjelister og til slutt brukerens egen portefølje. Med en større EODHD-plan kan brukeren følge flere aksjer.

**Videre lesning:** [PRD-en](prds/prd-G74-lund-osen-2026-09-20/prd.md), [målingene](prds/prd-G74-lund-osen-2026-09-20/malinger.md) og [datakildenes vilkår](../../docs/kilder-og-rettigheter.md).
