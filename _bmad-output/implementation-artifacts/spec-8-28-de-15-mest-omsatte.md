---
title: 'Story 8.28: «De 15 mest omsatte» som ferdig liste'
type: 'feature'
created: '2026-11-12'
status: 'review'
route: 'dispatch'
baseline_commit: 'a93c668f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11-ferdige-lister.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-11-prd-etter-tilbakemeldingen.md'
---

Skrevet 12.11 i vinduet som gjør PRD-en, etter tillegg 2 til 9.11 (limt inn kl.
20:10, føres i `docs/ai-prompts/2026-11-12.md`) og gruppens svar 12.11 kl. 20:04
og 20:06 (spørsmål 15 i 9.11). Rådet anbefalte 9.12, og gruppen valgte å bygge
lista. Worktreen `G74-lund-osen-8-28`, grenen `8-28-de-15-mest-omsatte`, fra
`origin/main` (`a93c668f`).

## Spørsmål til gruppen, med forslag

1. **Nummeret.** 8.26 og 8.27 er tatt av åpne grener. *Forslag:* 8.28.
2. **Antallet.** *Forslag:* 15, som i FR-412. Lista får da tre ledige plasser
   under taket på 18. Antallet står ett sted (`MEST_OMSATTE_ANTALL` i
   `src/ferdige_lister.py`).
3. **Navnet.** *Forslag:* «De 15 mest omsatte», som i FR-412. Knappen viser
   antallet ved siden av, som bransjeknappene. Er færre enn 15 målt, viser den
   færre.
4. **Hvor lista står.** *Forslag:* først under «Start fra en ferdig liste» i Min
   liste, foran bransjene, med den samme siden «Er du sikker?»
   (`/ferdig-liste?liste=mest-omsatte`). Den siden sier «på hele børsen» og
   viser bransjen ved hver aksje.
5. **Hvilke aksjer.** *Forslag:* de samme radene som bransjelistene. Det er de
   målte aksjene, og aksjene appen følger eller har fulgt, med medianen regnet av
   kursene (8.11b). Bare aksjer med en bransje er med, så hver kan følges med
   sin egen bransje. Kravet om åtte bransjer gjelder ikke.
6. **Bildene.** Lista står ikke på «Følg en aksje» (`/folg`), men under «Start
   fra en ferdig liste» i Min liste, der «+ Følg en aksje» også står. *Forslag:*
   bildene før og etter tas av den delen og av siden «Er du sikker?», og ligger på
   bildegrenen `pr-8-28-bilder`. `/folg` er uendret.
7. **Hjelpen.** Hjelpetekstene i appen nevner ikke de ferdige listene.
   *Forslag:* `docs/hjelp.md` følger («Hva er de ferdige listene og filteret?»),
   og omvisningen endres ikke, fordi den ikke nevner listene.

## Delene

### A) Lista
`mest_omsatte()` og `_radene()` i `src/ferdige_lister.py`. `lister()` bruker de
samme radene og gir de samme listene som før.
- **Ville feilet hvis:** lista hadde flere enn 15, ikke sto med høyest omsetning
  først, hadde en aksje uten måling eller bransje, eller regnet omsetningen ulikt
  bransjelistene.

### B) Sidene
`_egne()`, `ferdig_liste_side()` og `bruk_ferdig_liste()` i `src/app.py`,
`_egne.html` og `ferdig_liste.html`.
- **Ville feilet hvis:** knappen ikke sto først med antallet, siden ikke sa hele
  børsen, eller «Bruk denne lista» fulgte en aksje med en annen bransje enn sin
  egen.

### C) Demoen
Lista kommer av de samme radene i demobasen, så den er lik i demoen og i den
ekte versjonen.

## Grenser

Ingen API-kall. Ingen migrasjon. `data/db/ose.db` røres ikke. Demobaser lages
bare i midlertidige mapper, og demoserveren går aldri på port 8000.

## Bygget 12.11

Commitene `89edb931` (spesifikasjonen og storyen) og `4e7e61b4` (lista, testene,
hjelpen og bildene), og rettingen etter gjennomgangen i commiten etter dem.

**Bildene.** Alle bildene i `docs/appen/` ble tatt på nytt med
DevTools-protokollen, mot en demobase i en midlertidig mappe og waitress på en
ledig port, aldri 8000.
- «Din egen liste» er ny: knappen «De 15 mest omsatte» står først. Bildet er
  1474 px høyt, mot 1454 før, fordi setningen over knappene går over to linjer.
- «Mine notater» i Min liste er tatt på nytt fordi delen står lenger ned.
  Innholdet er det samme.
- Notatene på aksjesiden ved 390 px ble også nye med koden fra main. Det kommer
  ikke av 8.28, så fila fra HEAD er lagt tilbake.
- Resten er byte for byte de samme.
- Bildene før og etter for PR-en ligger på bildegrenen `pr-8-28-bilder`.

**Mutanten.** Lista fikk 16 aksjer i stedet for 15 (`MEST_OMSATTE_ANTALL + 1`)
i en kopi av `ferdige_lister.py` på HEAD `4e7e61b4`. To tester feilet. Kopien
ble lagt tilbake, og git-hashen og sha256 etter samme linjeskift var like HEAD.

**Gjennomgangen med Edge Case Hunter, og triagen:**
- ECH1 (lav), rettet: MULTI og SCOIN, som aldri kan følges, kunne komme med i
  lista hvis de hadde en bransje i basen. Da ville «Er du sikker?» lovet 15
  aksjer og gitt 14. `_radene()` tar dem nå ut for alle de ferdige listene, og en
  test viser det.
- ECH2 (lav), står: navnet «De 15 mest omsatte» står også når færre er målt.
  Antallet ved knappen og teksten på siden sier det riktige tallet, og det skjer
  bare i en tom eller ny base.
- ECH3 (lav), står: lista kan endre seg mellom «Er du sikker?» og «Bruk denne
  lista» hvis hentingen går imellom. Bransjelistene gjør det samme fra før, og
  det er ikke nytt i 8.28.

Ingen funn på middels eller over.
