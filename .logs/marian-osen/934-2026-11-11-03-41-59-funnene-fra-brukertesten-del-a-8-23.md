# Funnene fra brukertesten, del A (8.23)

## 2026-11-11 kl. 03:51 — Marian Osen

### Oppgave
Del A, funnene fra brukertesten 10.11, etter gruppens svar kl. 13:54, med tilleggene 1–3 (kl. 14:15, 14:53, 14:59 og 15:54), tillegget om demoen (kl. 15:57), tillegget om main og testene i natt og tillegget om ventingen (kl. 23:05). Ny story i Epic 8 på egen gren, med spesifikasjon, tester, mutanter, gjennomgang og fletting etter kl. 00:45. Alt står ordrett i `docs/ai-prompts/2026-11-10.md`.

### Plan
- Spesifikasjon med 18 spørsmål og forslag, grenen `8-23-funnene-fra-brukertesten` fra `86d1fe4f`.
- Delene i grupper, tester i `tests/test_funnene_8_23.py`, hjelpen, designreglene og README-en.
- Ingen pytest kl. 22:15–23:50; gjennomgangen kl. 22:20 med bare lesing. Testene, mutantene, bildene og hele settet etter kl. 23:50, hver kjøring bare når ingen annen pytest kjører (`naar_ledig.sh` i scratchpad).

### Resultat
- **Kl. 17:23** kom del A avkortet (uten steg 2–3); ingenting ble gjort (regel 1). Kl. 21:31 kom den hel. Main var da ikke ren (ekstravinduet var midt i «2.13b done»), og ble ren kl. 21:33 med `86d1fe4f`.
- **Storyen** er 8.23, fordi 8.21 og 8.22 var tatt av åpne PR-er. Spesifikasjonen `a2543e2f`, første del `733ded29` (A2, A8, tillegg 1, B7), resten `4acfbd61`, bildene `e13485bb`, rettinger etter hele settet `b3d4bddb` og `7207d359`, main inn `5d7cae7d` og `3e9c84ae`.
- **Gjennomgangen** (kl. 22:20): Blind Hunter 18, Edge Case Hunter 11 og Verification Gap 11 funn. VG1 var høy (ingen test så ECH1, overskriften på oversikten med `?vis=min`); rettet med test. De middels er rettet eller ikke reelle; triagen står i spesifikasjonen.
- **Mutantene:** 17, én per del, alle fanget, med filene like før og etter (sha256).
- **Hele settet i deler** fant feil i tester som speilet det gamle (lenker uten anker, lukket tabell, hvit knapp, 0-brikken, setningen om samme dag). To ting ble endret etter det: hva 3 av 3 betyr, står bare i `docs/hjelp.md`, fordi et vindu i appen ville brutt 60 ord og ett «?» per del (8.20a); og KI-bryteren og bryteren ved «Børsdagen kort fortalt» er i blekk som før (spørsmål 5 i 8.2b), så bare bryterne i Innstillinger er oransje.
- **Siste kjøring** på `3e9c84ae`, kl. 03:25–03:40: 5137 bestått, 25 hoppet over, 0 feilet, til sammen 5162. CI grønn (run 42945863521). Flettet som `7fb9b1fd` kl. 03:41; treet på main er likt head-en. Done i `fa1ba00f` (`--dokumentene`: 2371 bestått, 7 hoppet over).
- **CI startet ikke** etter pushen kl. 03:04, fordi PR-en hadde konflikt med main (8.24). PR-en ble lukket og åpnet igjen kl. 03:17 uten virkning; main ble flettet inn på nytt, og CI gikk.
- **Brudd på regelen om pytest:** to ganger startet en kjøring mens en annen pytest kjørte, kl. 21:49 (testene for hjelpefeltet) og kl. 23:52 (mutantene: skriptet skrev ut antallet, 2, men ventet ikke). Etter det startet alle kjøringene gjennom `naar_ledig.sh`, som venter til antallet er 0.
- **Ventingen:** ventekommandoen til kl. 23:50 gikk i bakgrunnen og ble ikke stoppet. Etter kl. 23:50 ventet hver del på at andre vinduers pytest ble ferdige, ofte i flere omganger.
- **Grenser:** ingen API-kall, `src/fetch_prices.py` er ikke kjørt, `data/db/ose.db` er ikke rørt, demobasene lå i midlertidige mapper, og den ekte versjonen og Ollama er ikke startet.
- **Del C** er ikke startet; den venter til del A har Utført-linje.

### Åpne punkter
- Spørsmålene 1–18 i spesifikasjonen for 8.23 er bygget etter forslaget og flettet; gruppen har ikke svart på dem enkeltvis.
- Hva 3 av 3 betyr, står bare i `docs/hjelp.md`, ikke i et vindu i appen (8.20a, del E).
- KI-bryteren og bryteren ved «Børsdagen kort fortalt» er i blekk; bare bryterne i Innstillinger er oransje.
