# Nattblokka: 8.8, navnet i avgjørelsene og brukertesten

## 2026-11-09 kl. 00:22 — Marian Osen

### Oppgave
Nattblokka i [dagsfila 09.11](../../docs/ai-prompts/2026-11-09.md), instruksjonen kl. 00:01. PR #124 (2.12) ble ikke flettet 08.11, så etter steg 0 gjøres bare steg 1, 3 og 4 og 8.8 av steg 2.

### Plan
- Steg 1: instruksjonen og svarene 08.11 kl. 22:01–23:12 i `epics.md`.
- 8.8: svaret i spesifikasjonen, main inn, hele settet, CI, squash-fletting og føringene.
- Steg 3: Rettet-linjer der avgjørelser står som én persons.
- Steg 4: brukertesten, med de nye delene og 0011.

### Resultat
- **Kvote:** kl. 23:57 08.11 (22:57 GMT) var alle 20 kallene for 08.11 i GMT brukt av kveldshentingen, og 0 var igjen. Ingen andre kall. `src/fetch_prices.py`, `data/db/ose.db`, oppgaven, `G74-lund-osen-jobb` og `_privat/` er ikke rørt, og Ollama er ikke startet.
- **Steg 1:** `673230d9`. Svarene kl. 22:14 og 23:12 står under «Prioritering», kl. 22:01, 22:03 og 22:06 under 8.11, og kl. 22:53 under 8.8, 8.10 og 8.10b. De sju tickerne i svaret kl. 22:03 er slått opp i `BRANSJE` på grenen for 8.11, og Energi, Industri, Shipping og Finans i `designregler.md` §4. Dokumenttestene: 263 bestått.
- **8.8:** svaret står i spesifikasjonen (`f488e1cc` på grenen, med i squashen). Main er flettet inn i `32bf3918`, med konfliktene i `sprint-status.yaml`, `stil.css` (begge stilene står) og avtrykkene. Bildene er byte for byte de samme. 3,9 GB ledig minne. Hele settet alene 00:03:16–00:18:08: 4695 bestått, 24 hoppet over og 0 feilet. CI grønn (run 42534544829). PR #127 er squash-flettet i `ab5fb6a7` kl. 00:21, låst til `32bf3918`, og treet på main er likt treet på head-en. Føringene står i `67f93cf2`. 8.11 ble ikke flettet først, fordi den venter på 2.12.
- **Steg 3:** `2ed9cb3b`. Rettet-linje øverst i 19 dokumenter (prd.md, epics.md, tre endringsforslag, spinen, tre spesifikasjoner, malinger, designregler, begrunnelser, relevanseksperimentet, kilder og rettigheter, kvalitetssikringen, refleksjonsloggen, to epic-kontekster og samlelista), en linje nederst i de to memloggene (regel 5), en linje i `docs/ai-prompts/README.md`, en kommentar i `sprint-status.yaml`, og en Lagt til-linje under regel 20 i `CLAUDE.md`. Det en person gjorde selv (e-post, innboks, regnet for hånd, gjengitt) står urørt.
- **Steg 4:** `cf4f655c`. Lagt til-linjer i `docs/brukertest.md` og spesifikasjonen 8.1: «Børsdagen kort fortalt» med KI av, «Dine egne aksjer» med valgene i demoen, Innstillinger på grenene for 8.10 og 8.10b, prikkene i kursgrafen, og 0011. Basen får 0009 i jobben mandag kveld (main fra midnatt). Den får 0010 og 0011 tirsdag når den ekte versjonen startes på main etter pull, fordi `aapne_base` kjører `migrer()`, eller ellers i jobben tirsdag kl. 22:15.
- Steg 3 og 4 ble først committet før flettingen av 8.8, så lagt til side og plukket inn igjen etterpå, slik at treet på main ble likt head-en til 8.8 ved flettingen.

### Åpne punkter
- Regel 22 sier at webserveren bare skriver merkingen i Min liste, men den ekte versjonen startet på main migrerer også basen (0010 og 0011 før testen tirsdag). Gruppen avgjør om det er greit, eller om basen skal få dem i jobben tirsdag kl. 22:15.
- 8.11 (PR #128) er ikke flettet, og 8.8 ble flettet før den, fordi #124 ikke ble flettet 08.11 (steg 0).
- Nattblokk 2 (limt inn kl. 00:01) venter til nattblokka har Utført-linje.
