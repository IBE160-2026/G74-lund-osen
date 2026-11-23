---
title: 'Story 9.27: statusene i «Dine egne aksjer» og «Følg en aksje» regner dagen'
type: 'code'
created: '2026-11-23'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '042d922a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-25-svarene-paa-ux-spoersmaalene.md'
---

Skrevet 23.11 etter instruksjonen om svarene på spørsmålene i 9.25 og 9.26
(limt inn kl. 14:50 i `docs/ai-prompts/2026-11-23.md`) og gruppens svar 23.11
kl. 14:49. Spørsmål 3 i 9.25 ville rådet vente med til etter brukertest 2, men
gruppen valgte å ta det nå. Neste ledige nummer i Epic 9 etter 9.26 er 9.27.
Worktreen er `G74-lund-osen-9-27`, på grenen `9-27-statusene-regner-dagen`, fra
`origin/main` (`042d922a`). Svarene på spørsmål 1 og 2 i 9.25 og på begge i
9.26 står på main, ikke på grenen (steg 1 i instruksjonen, `cd479f50` og
`042d922a`).

## Storyen

Som **bruker i brukertest 2** vil jeg at statusen ved en aksje jeg har valgt
eller fjernet, sier hvilken dag hentingen tar den, så den ikke sier «i kveld»
etter at kveldens henting er ferdig, eller en lørdag.

**Oppfyller:** spørsmål 3 i 9.25 (ECH3 i gjennomgangen der, svaret 23.11 kl.
14:49), FR-412, FR-415 · **Begrenses av:** regel 3, 16, 19, 20, 21 og 22,
NFR-06, NFR-08; ingen ny migrasjon

**Avhenger av:** 9.25. **Én økt:** ja.

## Det som er slått opp

- Statusene står fire steder: «Venter på henting i kveld etter …» og «Fjernes
  ved hentingen i kveld etter …» i «Dine egne aksjer» (`_egne.html`), «Fjernes
  ved hentingen i kveld etter …» under «Følg flere aksjer» i Min liste (samme
  mal), og «Aksjen hentes ved neste henting, tidligst i kveld etter …» i
  «Følg en aksje» (`folg.html`).
- Stripa regner dagen med `boersdag.neste_henting` og skriver den med
  `neste_henting_tekst` i `src/markedsoversikt.py`, av den siste kursdagen i
  basen, den eldste blant aksjene i lista (`kursdag_felles`).
- Hentingen tar bare ønskene i bruk på selve børsdagen, ikke i helgen eller
  om natta etter (`fetch_prices.py`, ECH3 i 2.12, som svaret 22.11 kl. 11:29
  lot stå). Stripa sier «nye kurser kan hentes nå» en lørdag når basen mangler
  fredagen, men et ønske venter da til mandag.
- Demoen bruker den ekte klokka, og kursene der slutter fredag 09.10.

## Det som gjøres

1. **Dagen.** `boersdag.neste_henting_av_oensket(kursdag, naa)` gir dagen et
   ønske tidligst tas i bruk: i dag på en børsdag, før `TIDSGRENSE` eller så
   lenge basen ikke har dagens kurser for alle aksjene i lista, og ellers neste
   børsdag. Den bruker de samme byggesteinene som `neste_henting` for stripa
   (`norsk_dato`, `er_boersdag`, `neste_boersdag` og `TIDSGRENSE`). Den skiller
   seg fra stripa på ett punkt: en dag børsen er stengt, er det alltid neste
   børsdag, fordi ønskene ikke tas i bruk da.
2. **Teksten.** `oensket_hentes_tekst` i `src/markedsoversikt.py` skriver dagen
   som stripa: «i kveld», «i morgen», ukedagen innen en uke, og ellers ukedagen
   og datoen, med klokkeslettet fra `TIDSGRENSE` (`grensen_som_tekst`, som i
   9.25). Stripa og statusene deler funksjonen som skriver dagen.
3. **Malene.** De fire stedene bruker teksten. Dekker kalenderen ikke dagen,
   står statusen uten dag: «etter kl. 22» (NFR-08, ingen gjetning).
4. **Demoen.** Demoen henter aldri, og boksen under statusen sier det. Der
   står «i kveld etter kl. 22» som før, så bildene er like fra dag til dag. Se
   spørsmål 1.
5. **Hjelpen.** `docs/hjelp.md` siterer statusen og sier at dagen regnes.
6. **Testen** feiler før rettingen, og prøver tiden før kl. 22, etter jobben
   og en lørdag. Endrer et bilde i `docs/appen/` seg, tas det på nytt i demoen,
   og avtrykket og bildegrenen følger med.
7. **Skjermsiden.** `docs/skjermene.md` får en linje for 9.27, fordi
   `tests/test_skjermene_9_26.py` låser siden mot `epics.md`, og tallene i
   vurderingsmatrisen følger.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Bilder bare av demoen, på en ledig port, aldri 8000, og uten ekte kurser.
- Ingen ny migrasjon.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.
- Pausene om kvelden gjelder når kveldsjobben er Ready: ingen pytest kl.
  22:15–23:50, ingen git kl. 22:10–22:20, 22:43–22:48, 23:13–23:18 og
  23:43–23:48, og ingen fletting kl. 22:10–23:58.

## Kontroll

- [ ] Statusene sier «i kveld» på en børsdag før kl. 22
- [ ] Etter kveldsjobben sier de neste børsdag: «i morgen», eller ukedagen
- [ ] En lørdag sier de «mandag», også når basen mangler fredagen
- [ ] Klokkeslettet kommer fra `TIDSGRENSE`
- [ ] Testen feilet før rettingen
- [ ] Bildene som endrer seg, avtrykkene og bildegrenen følger med
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
