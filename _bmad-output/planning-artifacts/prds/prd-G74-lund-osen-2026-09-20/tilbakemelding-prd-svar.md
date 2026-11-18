---
title: "Svar på tilbakemeldingen på PRD-en"
status: aktiv
created: 2026-11-17
updated: 2026-11-18T11:52
---

# Svar på tilbakemeldingen på PRD-en

Svar fra gruppen G74 på [tilbakemeldingen fra faglærer 12.11](tilbakemelding-prd.md),
i samme rekkefølge, punkt 1–7. Hver rad sier «Gjort», med lenke dit, eller
«Ikke gjort, fordi …». PRD-en er endret flere ganger etter 12.11. Den ble skrevet
om 12.–13.11 (story 9.11 i `epics.md`), etter gruppens svar 12.11 kl. 18:00.
Den ble endret 13.–17.11 i story 9.12–9.18, 2.17 og 2.18, etter hvert som appen
endret seg, blant annet med brukerreisene UJ-2 og UJ-3 og suksessmålene SM-10 og
SM-11 i 9.16. 17.–18.11 ble den gått gjennom mot rubrikken (story 9.20), etter
en validering og gruppens svar 17.11 kl. 12:29 («Rett alt, ID-ene står»), 13:03,
13:10 og 13:40. Hver endring står datert i [endringsloggen](prd-endringslogg.md),
i «Endringer etter 12.11». PRD-en slik den ble vurdert, står i taggen
`prd-vurdert-2026-11-12`.

<a name="id-ene"></a>**ID-ene står.** Ingen FR-, NFR-, UJ- eller SM-ID er endret. Rubrikken
begrunner ID-ene med stabile henvisninger, og ID-ene brukes i spesifikasjonene,
commitene og testene. Nye krav har fått nye ID-er i sine avsnitt.

## Tallene

Telt i `prd.md` på tre tidspunkter. Ordene er telt med Python,
`re.findall(r"\w+", tekst)`. Daterte linjer er linjer som begynner med en
stjerne, et ord med stor forbokstav og en dato, som «*Rettet 2026-10-08» eller
«*(Lagt til 2026-09-25», med `re.match(r"\*\(?[A-ZÆØÅ][\w ]* \d{4}-\d\d-\d\d", linje)`.

| | Linjer | Ord | Daterte linjer |
|---|---:|---:|---:|
| Vurdert 12.11 (taggen `prd-vurdert-2026-11-12`) | 2 264 | 30 660 | 174 |
| Etter omskrivingen i story 9.11 (`ef802733`, 13.11 kl. 22:47) | 1 870 | 14 773 | 0 |
| Nå, etter story 9.20 | 2 132 | 18 026 | 0 |

Tilbakemeldingen sier «ca. 2 260 linjer, 28 700 ord». Linjene stemmer, og
ordene også, telt som `wc -w` med `LC_ALL=C`: det gir 28 752 ord på taggen.
Tabellen teller med `re.findall(r"\w+", tekst)`, som gir 30 660, og
`str.split()`, ord skilt av mellomrom, gir 29 030. Forskjellen mot `wc` er de
278 ordene uten et eneste ASCII-tegn, som `wc` ikke teller i C-locale: blant
annet 160 frittstående «—» og 77 «å». Spriket er dermed forklart av metoden. PRD-en er lengre nå enn etter
9.11, fordi den har fått to brukerreiser, fire nye krav med konsekvenser, en
ordliste med tolv ord og regelen om målingen i FR-603.

## Punkt for punkt

| Punkt i tilbakemeldingen | Hva som er gjort |
|---|---|
| 1 Samlet inntrykk: «dokumentet er blitt en endringslogg» | Gjort. `prd.md` har én gjeldende tekst per krav, og historikken står i [endringsloggen](prd-endringslogg.md). [«Slik leser du PRD-en»](prd.md#slik-leser-du-prd-en) øverst sier at §1–§8 gjelder nå, utenom det som er senere, at vedlegg A ikke er bygget, og hvor historikken, sporingen og dette svaret står |
| 2 Dette fungerer godt | Gjort: det står. FR-701–FR-703, kontrollen i FR-603, FR-411, NFR-01, «Drift: hva målet ga opp» og motmålene i [§7](prd.md#7-suksessmål) er beholdt. At SM-1 ikke er nådd, er åpent punkt 28 i [§8](prd.md#8-åpne-punkter), og statusen fra 12.11 står i endringsloggen. [FR-603](prd.md#fr-603--ki-teksten-sier-ikke-mer-enn-grunnlaget) har fått punkt 5, at ordene om målingen skal stemme med fortegnet, og «Kontrollen er grov» sier nå nøyaktig hva den fanger og ikke |
| 3 Oversikt per dimensjon | Gjort for de fire som var «god» eller «svak». Testbarhet: hvert krav har «*Konsekvenser:*» (4.2). Scope: én tabell i [§2](prd.md#kjerne-ekstra-og-senere) (4.5). Brukbarhet: ordliste, tre brukerreiser og [sporingen](prd-sporing.md) (4.3). Formtilpasning: kravregister med UJ og SM (4.3, §5) |
| 4.1 Gjeldende krav må kunne leses uten historikken | Gjort. Hvert FR og NFR i [§4](prd.md#4-funksjonelle-krav) og [§5](prd.md#5-tverrgående-krav) har én gjeldende tekst som sier hva appen gjør, lest i koden. De daterte linjene står ordrett i [endringsloggen](prd-endringslogg.md). FR-201 sier periodevalget, FR-101 lista som er aktiv med opptil 18, FR-202 volumsøylene og båndet, og NFR-01 fordelingen av de 20 kallene. 17.11 er også status og prosess i §2, §7 og §8 flyttet til endringsloggen |
| 4.2 Gi alle FR-er testbare konsekvenser | Gjort. Hvert FR og NFR i [§4](prd.md#4-funksjonelle-krav), [§5](prd.md#5-tverrgående-krav) og vedlegg A har «*Konsekvenser:*» med det en test kan sjekke, også [FR-108](prd.md#fr-108--filter-på-signalet) og [NFR-06](prd.md#nfr-06--løsningen-gir-ikke-investeringsråd) slik tilbakemeldingen foreslo, og de fire nye kravene. `tests/test_prd_9_11.py` sjekker at hvert krav har dem |
| 4.3 Én brukerreise og et glossar | Gjort. [UJ-1](prd.md#brukerreisen-uj-1), UJ-2 og UJ-3 med climax og edge, og en [ordliste](prd.md#ordliste) med tolv ord, i §1. Ordene i ordlista brukes likt i teksten, og ordet i parentes står bare i koden og i overskriftene, så lenkene holder |
| 4.4 Implementasjonsdetaljer og byggestatus ut av kravene | Gjort. Kodenavn, commits, migrasjoner, storynummer og «ikke bygget per» er ute av kravene, og kodenavn er skrevet med vanlige ord. Navnene på nøklene og variablene står i [«Teknologi og nøkler»](../../architecture/teknologi-og-noekler.md). Feltnavnene hos kilden, som `close` og `adjusted_close`, står |
| 4.5 Scope-status i én tabell | Gjort. Tabellen «Kjerne, ekstra og senere» i [§2](prd.md#kjerne-ekstra-og-senere): FR, krav, kjerne / ekstra / senere og bygget. «v1.1» i [§8](prd.md#8-åpne-punkter) viser til tabellen i stedet for å gjenta den. Plan A står i vedlegg A |
| §5 Ingen glossar, UJ eller Assumptions Index | Gjort. Ordliste og brukerreiser som i 4.3. Lista over `[ANTAKELSE]` og `[FORELØPIG]` står i [sporingen](prd-sporing.md#antakelser-og-foreløpige-tall), og hver markør i FR-302 og FR-606A lenker dit. Antakelsen i FR-501 var avkreftet 21.09 og er ute av kravteksten |
| §5 FR-ID-ene er ikke sammenhengende | Ikke gjort for numrene, fordi [ID-ene står](#id-ene). Gjort for resten: FR-407 står nå i §4.4 med de andre FR-4xx. Innledningen til [§4](prd.md#4-funksjonelle-krav) sier at første siffer er avsnittet, og [sporingen](prd-sporing.md#hvorfor-noen-numre-mangler) hvorfor noen numre mangler |
| §5 Suksessmålene mangler ID og henvisning til FR | Gjort. [SM-1–SM-11](prd.md#7-suksessmål) med kolonnen «Krav», og hver brukerreise viser til de samme kravene som målet som måler den. «KI-bidrag i drift» og «Relevanseksperiment», som ikke gjelder lenger, står i endringsloggen |
| §5 Foreldet tekst: FR-401 «kravteksten over står uendret» | Gjort. [FR-401](prd.md#fr-401--henting-utløses-eksplisitt-aldri-av-en-oppstart) er skrevet om: hentingen i seks steg, kveldsjobben og «Start den ekte versjonen» |
| §5 Beslutninger tilskrevet enkeltpersoner | Gjort. [`prd.md`](prd.md) har ingen navn utenom gruppelinja, og avgjørelsene står som gruppens. `tests/test_prd_9_11.py` sjekker det. Linjene i [endringsloggen](prd-endringslogg.md) står ordrett, med navnene der de sto |
| §6 Før dere går videre | Gjort for det som måtte avklares: gjeldende tekst og kjerne mot ekstra (4.1, 4.5), og hovedflyten som [UJ-1](prd.md#brukerreisen-uj-1). «Under 5 minutter» i SM-1 står og avgjøres etter brukertest 2, som åpent punkt 28 i [§8](prd.md#8-åpne-punkter). Punkt 13 og 21 i §8 venter fortsatt på faglærer |
| §7 Refleksjonsspørsmål | Ikke gjort, fordi spørsmålene besvares i refleksjonsrapporten. Spørsmål 2 står også som åpent punkt 27 i [§8](prd.md#8-åpne-punkter) |

## Det som ikke er endret

- **ID-ene**, av grunnen i [«ID-ene står»](#id-ene).
- **FR-606**, relevansskalaen, står i §4.6, selv om den er plan A og «senere».
  Om den skal til vedlegg A, er et spørsmål til gruppen.
