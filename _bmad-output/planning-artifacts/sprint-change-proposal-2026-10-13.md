---
title: "Endringsforslag 13.10: samlelista, tekstene og rekkefølgen"
status: draft
created: 2026-10-13
updated: 2026-10-13T11:24
---

# Endringsforslag 13.10: samlelista, tekstene og rekkefølgen

Laget med `bmad-correct-course` i modusen Batch, etter instruksjonen kl. 11:17 i
`docs/ai-prompts/2026-10-13.md`. Bygd opp som
[`sprint-change-proposal-2026-10-08.md`](sprint-change-proposal-2026-10-08.md).

**Dette er et utkast.** Samlelista sier at den samlede endringen tas etter
README-prøven 13.–16.10, så forslaget godkjennes først da, og funnene fra prøven
kommer med i punkt 5. Ingenting i `prd.md`, `epics.md`, `designregler.md`,
`sprint-status.yaml`, spinen eller koden er endret. Ingenting endres før rådet
har lest forslaget og Marian har sagt ja (regel 2 og 9).

Grunnlaget er [`samleliste-endringsforslag.md`](../implementation-artifacts/samleliste-endringsforslag.md),
punkt 1–13 med de daterte linjene og utdraget fra designforslaget nederst, og
ordlista i [`designregler.md`](designregler.md) §4. Linjenumrene viser til filene
slik de sto på main 13.10 kl. 11:20.

## 1. Hva som utløste forslaget

**Samlelista.** Marian bestemte 12.10 kl. 12:21 at punkter som dukker opp, samles
og tas i ett endringsforslag, ikke ett og ett. Lista har 13 punkter fra 11.10 og
12.10. De fleste kom da Marian så hjelpen fra 8.0b på skjermen og sammenlignet
den med designforslaget, som ligger på en tavle i Claude og ikke i repoet.

| Punkt | Hva | Typen endring |
|---:|---|---|
| 1, 2 | Kortere hjelp, og tekstene i vanlige ord (NFR-05) | Tekst og test, 8.0c og 8.9 |
| 3, 4 | Hjelp og KI av og på øverst | Story 8.10 |
| 5 | Utseendet fra designforslaget | Story 8.0d, som finnes |
| 6, 12 | Knapperaden og hovedindeksen tidligere | Rekkefølgen i `epics.md` |
| 7, 10 | Tekstene på tavla, kontrollert mot koden | Tekst, 8.0c og 8.9 |
| 8 | Samme ord for signalstyrke, trend og retning | Krav (FR-701, FR-703, FR-704), mal og hjelp |
| 9 | Fire hull fra gjennomgangene 12.10 | Test og dokument |
| 11 | Seks ting fra tavla uten story | Story 8.0c, 8.0d og én ny |
| 13 | Kravlista og dekningstabellen etter 05.10 | `epics.md` |

Ordlista fra tavla ble ført i `designregler.md` §4 13.10, i `bab4adb` og `f33db34`.
Den er kontrollert i punkt 4.3.

**Typen endring.** Ingen nye idéer fra produkteier, og ingenting som er bygget, er
feil i det det gjør. Det som endres, er ord, rekkefølge og hva noen storyer tar
med. Ett unntak: punkt 11 gir oversikten mer innhold (T, B og I i hver rad, delt
tabell og en overskrift), som Marian bestemte 12.10 kl. 22:03.

**Rådets anbefaling.** Øverst i samlelista står det at rådet anbefalte kl. 22:03
og 22:40 at den samlede endringen tas før 8.0c planlegges, fordi 8.0c blir større
med de fire første tingene i punkt 11. Det er ikke avgjort (spørsmål 1 i punkt 7).

## 2. Virkninger

### Epics

Ingen ny epic. Tilbakemeldingen fra faglærer 06.10 ber om at antall epics ikke
vokser ([`tilbakemelding-product-brief.md`](tilbakemelding-product-brief.md)).

| Epic | Virkning |
|---|---|
| **Epic 8** | 8.0c får flere kontrollpunkter (punkt 1, 7, 8 og 11). 8.0d får rekkefølgen av delene på sidene (punkt 11). 8.9 får tekstene fra tavla (punkt 7). 8.10 kan deles, så hjelpebryteren kommer før KI-bryteren (punkt 3 og 4). Én ny liten story for stripa øverst, hvis Marian vil ha den for seg (punkt 11) |
| **Epic 2** | Rekkefølgen for 2.8, 2.9 og 2.9b (punkt 12). 2.12 får «Dine egne aksjer» hvis den delen skal stå for seg (punkt 11) |
| **Epic 10** | Får FR-601, FR-602, FR-603 og FR-605 i dekningstabellen og en FR-linje (punkt 13) |
| **Epic 5** | Beholder bare A-variantene av FR-6xx (punkt 13). Er fortsatt ute av v1 |
| Epic 4, 9 | Ingen virkning, utenom rekkefølgen |

### Andre dokumenter

`prd.md` får ny ordlyd i FR-701, FR-703 og FR-704 (punkt 8). `designregler.md`
får rettelser i §4 der ordlista strider mot krav eller regler (punkt 4.3), og
rekkefølgen av delene på sidene i planen for 8.0d. `sprint-status.yaml` mangler
8.0d i dag. Punkt 6 har hele lista.

## 3. Anbefalt vei

**Direkte justering:** nye kontrollpunkter i storyer som finnes, ny ordlyd i tre
krav, en rettet rekkefølge og opprydding i `epics.md`. Ingenting rulles tilbake,
og ingenting kuttes.

- **Innsats:** liten til middels. Det meste er tekst og kontrollpunkter. Det
  største er punkt 11, som gjør 8.0c større.
- **Risiko:** liten. Ingen endring i hentingen, basen eller signalet. Tekstene i
  hjelpen er låst av tester som henter tallene fra `Parametre`
  (`tests/test_hjelpetekster.py:26–33`), så en kortere tekst kan ikke få feil tall
  uten at en test feiler.
- **Tid:** avhenger av rekkefølgen i punkt 4.7. Bare ett av alternativene der får
  både KI-teksten fra rundt 26.10 og brukertesten 8.1 før uke 45 innenfor farten
  som står i repoet.
