---
title: "Svar på tilbakemeldingen på PRD-en"
status: draft
created: 2026-11-17
updated: 2026-11-18T09:48
---

# Svar på tilbakemeldingen på PRD-en

Svar fra gruppen G74 på [tilbakemeldingen fra faglærer 12.11](tilbakemelding-prd.md),
i samme rekkefølge, punkt 1–7. For hvert punkt står det hva som er gjort, med
lenke dit, eller hvorfor det ikke er gjort. PRD-en ble skrevet om i to runder:
først 12.–13.11 (story 9.11 i `epics.md`), etter gruppens svar 12.11 kl. 18:00,
og så 17.11 (story 9.20), etter en validering mot rubrikken og gruppens svar
17.11 kl. 12:29 («Rett alt, ID-ene står»), 13:03, 13:10 og 13:40. Hver endring
står datert i [endringsloggen](prd-endringslogg.md), under «Endringer etter
12.11». PRD-en slik den ble vurdert, står i taggen `prd-vurdert-2026-11-12`.

**ID-ene står.** Ingen FR-, NFR-, UJ- eller SM-ID er endret. Rubrikken
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
| Etter omskrivingen 12.11 (`ef802733`) | 1 870 | 14 773 | 0 |
| Nå, etter 17.11 | 2 125 | 17 848 | 0 |

Tilbakemeldingen sier «ca. 2 260 linjer, 28 700 ord». Linjene stemmer. Ordene
spriker: vi teller 30 660 med metoden over, og vi vet ikke hvordan 28 700 er
telt. Spriket står åpent (regel 12 i `CLAUDE.md`). PRD-en er lengre nå enn
etter 12.11, fordi den har fått to brukerreiser, fire nye krav med
konsekvenser, en ordliste med tolv ord og regelen om målingen i FR-603.

## Punkt for punkt

| Punkt i tilbakemeldingen | Hva som er gjort |
|---|---|
| 1 Samlet inntrykk: «dokumentet er blitt en endringslogg» | Gjort. `prd.md` har én gjeldende tekst per krav, og historikken står i [endringsloggen](prd-endringslogg.md). [«Slik leser du PRD-en»](prd.md#slik-leser-du-prd-en) øverst sier at §1–§8 gjelder nå, at vedlegg A ikke er bygget, og hvor historikken, sporingen og dette svaret står |
| 2 Dette fungerer godt | Gjort, det står. FR-701–FR-703, kontrollen i FR-603, FR-411, NFR-01, «Drift: hva målet ga opp» og motmålene i [§7](prd.md#7-suksessmål) er beholdt. At SM-1 ikke er nådd, er åpent punkt 28 i [§8](prd.md#8-åpne-punkter), og statusen fra 12.11 står i endringsloggen. [FR-603](prd.md#fr-603--ki-teksten-sier-ikke-mer-enn-grunnlaget) har fått punkt 5, at ordene om målingen skal stemme med fortegnet, og «Kontrollen er grov» sier nå nøyaktig hva den fanger og ikke |
| 3 Oversikt per dimensjon | Gjort for de tre som var «god» eller «svak». Testbarhet: hvert krav har «*Konsekvenser:*» (4.2). Scope: én tabell i [§2](prd.md#kjerne-ekstra-og-senere) (4.5). Brukbarhet: ordliste, tre brukerreiser og [sporingen](prd-sporing.md) (4.3). Formtilpasning: kravregister med UJ og SM (4.3, §5) |
| 4.1 Gjeldende krav må kunne leses uten historikken | Gjort. Hvert FR og NFR har én gjeldende tekst som sier hva appen gjør, lest i koden. De daterte linjene står ordrett i endringsloggen. FR-201 sier periodevalget, FR-101 lista som er aktiv med opptil 18, FR-202 volumsøylene og båndet, og NFR-01 fordelingen av de 20 kallene. 17.11 er også status og prosess i §2, §7 og §8 flyttet til endringsloggen |
| 4.2 Gi alle FR-er testbare konsekvenser | Gjort. Hvert FR og NFR har «*Konsekvenser:*» med det en test kan sjekke, også FR-108 og NFR-06 slik tilbakemeldingen foreslo, og de fire nye kravene. `tests/test_prd_9_11.py` sjekker at hvert krav har dem |
| 4.3 Én brukerreise og et glossar | Gjort. [UJ-1](prd.md#brukerreisen-uj-1), UJ-2 og UJ-3 med climax og edge, og en [ordliste](prd.md#ordliste) med tolv ord, i §1. Ordene i ordlista brukes likt i hele teksten, og ordet i parentes står bare i overskriftene, så lenkene holder |
| 4.4 Implementasjonsdetaljer og byggestatus ut av kravene | Gjort. Kodenavn, commits, migrasjoner, storynummer og «ikke bygget per» er ute av kravene, og kodenavn er skrevet med vanlige ord. Navnene på nøklene og variablene står i [«Teknologi og nøkler»](../../architecture/teknologi-og-noekler.md). Feltnavnene hos kilden, som `close` og `adjusted_close`, står |
| 4.5 Scope-status i én tabell | Gjort. Tabellen «Kjerne, ekstra og senere» i [§2](prd.md#kjerne-ekstra-og-senere): FR, krav, kjerne / ekstra / senere og bygget. «v1.1» i §8 viser til tabellen i stedet for å gjenta den. Plan A står i vedlegg A |
| §5 Ingen glossar, UJ eller Assumptions Index | Gjort. Ordliste og brukerreiser som i 4.3. Lista over `[ANTAKELSE]` og `[FORELØPIG]` står i [sporingen](prd-sporing.md#antakelser-og-foreløpige-tall), og hver markør i FR-302 og FR-606A lenker dit. Antakelsen i FR-501 var avkreftet 21.09 og er ute av kravteksten |
| §5 FR-ID-ene er ikke sammenhengende | ID-ene står (se avsnittet om ID-ene). FR-407 står nå i §4.4 med de andre FR-4xx. Innledningen til [§4](prd.md#4-funksjonelle-krav) sier at første siffer er avsnittet, og [sporingen](prd-sporing.md#hvorfor-noen-numre-mangler) hvorfor noen numre mangler |
| §5 Suksessmålene mangler ID og henvisning til FR | Gjort. [SM-1–SM-11](prd.md#7-suksessmål) med kolonnen «Krav», og hver brukerreise viser til de samme kravene som målet som måler den. «KI-bidrag i drift» og «Relevanseksperiment», som ikke gjelder lenger, står i endringsloggen |
| §5 Foreldet tekst: FR-401 «kravteksten over står uendret» | Gjort. [FR-401](prd.md#fr-401--henting-utløses-eksplisitt-aldri-av-en-oppstart) er skrevet om: hentingen i seks steg, kveldsjobben og «Start den ekte versjonen» |
| §5 Beslutninger tilskrevet enkeltpersoner | Gjort. `prd.md` har ingen navn utenom gruppelinja, og avgjørelsene står som gruppens. Linjene i endringsloggen står ordrett, med navnene der de sto |
| §6 Før dere går videre | Gjeldende tekst og kjerne mot ekstra er gjort (4.1, 4.5), og hovedflyten er UJ-1. «Under 5 minutter» i SM-1 står og avgjøres etter brukertest 2, som åpent punkt 28 i [§8](prd.md#8-åpne-punkter). Punkt 13 og 21 i §8 venter fortsatt på faglærer |
| §7 Refleksjonsspørsmål | Ikke besvart her, fordi spørsmålene besvares i refleksjonsrapporten. Spørsmål 2 står også som åpent punkt 27 i [§8](prd.md#8-åpne-punkter) |

## Det som ikke er endret

- **ID-ene**, av grunnen over.
- **FR-606**, relevansskalaen, står i §4.6, selv om den er plan A og «senere».
  Om den skal til vedlegg A, er et spørsmål til gruppen.
