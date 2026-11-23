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

## Resultatet

| Del | Commit | Testen |
|---|---|---|
| Dagen: `boersdag.neste_henting_av_oensket` | `e4265972` | `TestDagen` |
| Teksten: `oensket_hentes_tekst` og `_dagen_som_tekst`, som stripa også bruker | `e4265972` | `TestDagen`, og `tests/test_neste_henting.py` for stripa |
| Malene: `{{ oensket_hentes(kursdag_felles) }}` fire steder, med `_oensket_hentes` i `app.py` | `e4265972` | `TestSidene` og `test_ingen_mal_sier_i_kveld_om_hentingen_etter_grensen` |
| Demoen: «i kveld» står fast | `e4265972` | `TestDemoen` |
| Hjelpen: «Dagen i statusen regnes …» | `e4265972` | Ingen, hjelpen er levende |
| Skjermsiden: en linje for 9.27, 143 storyer, og 101 uten bilde i vurderingsmatrisen | `0cf90bde` | `tests/test_skjermene_9_26.py` |

Testfila ble kjørt mot koden på `85300ee5`, før rettingen: 28 av de 35 testene
feilet. De 7 som besto, var de tre tilfellene før kl. 22 på sidene, de tre i
demoen og testen for stripa, som alle skal si det samme før og etter. Etter
rettingen besto alle 35. De tre tilfellene som kom etter gjennomgangen (VG2 og
VG4), er ikke kjørt mot koden før rettingen.

**Bildene.** Ingen bilder i `docs/appen/` endrer seg, så ingen er tatt på
nytt, og storyen har ingen bildegren. Sidene i demoen ble hentet med appens
testklient mot en midlertidig demobase, på main (`042d922a`) og på grenen
(`e4265972`): `/`, `/min-liste`, `/boersometer`, `/folg`, `/folg?kode=HVLK`,
`/aksje/BRFE` og `/innstillinger`, med klokka på en tirsdag og en lørdag, og
`/` og `/min-liste` etter et valg. Alle var like byte for byte. Demoen ble
ikke startet på en port.

## Gjennomgangen 23.11

Én leser, bare med lesing, på `042d922a..0cf90bde`, i fire roller: Blind
Hunter, Edge Case Hunter, Acceptance Auditor og Verification Gap. Den kjørte
ikke pytest. ECH1 og AA1–AA5 er slått opp i koden etterpå. 19 funn: 5 middels
og 14 lave.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| ECH1 | middels | Etter første kjøring av kveldsjobben sier statusen «i morgen», men kjøringene kl. 22:45, 23:15 og 23:45 tar et nytt ønske i bruk samme kveld: `fetch_prices.py` tar ønskene i bruk i hver kjøring på børsdagen, og `start/kveldshenting.ps1` kjører hentingen også når dagen er ferdig | Åpent: spørsmål 1. Følger av svaret, så det står til gruppen har svart (regel 25) |
| VG1 | middels | Testen låser «i morgen» kl. 23 uten å si noe om kjøringene etterpå | Åpent: følger ECH1 og spørsmål 1 |
| AA1 | middels | Aksjesiden sier «fjernes fra lista ved hentingen i kveld» (`aksje.html`), som nå kan motsi statusen | Åpent: spørsmål 2 |
| AA2 | middels | Samme setning i Min liste, bygget i `app.py` | Åpent: spørsmål 2 |
| AA3 | middels | «Er du sikker?» sier «fra og med hentingen i kveld» (`bekreft_fjern.html`) | Åpent: spørsmål 2 |
| AA4 | lav | `docs/hjelp.md` siterer setningene i AA1–AA3 med «i kveld» | Står: følger spørsmål 2 |
| AA5 | lav | «Fjerner du aksjen før kvelden, brukes ingen kall.» står under «tidligst mandag …» en lørdag (`folg.html`) | Står: følger spørsmål 2. Setningen vises også i demoen |
| AA6 | lav | Spesifikasjonen viste til et spørsmål som ikke fantes | Rettet: «Spørsmål til gruppen» under |
| AA7 | lav | `updated` i `docs/skjermene.md` var ikke satt | Rettet, fra `date` |
| AA8 | lav | Tallet 100 var endret til 101 i en eldre datert linje i vurderingsmatrisen | Rettet: linja sier 100 som før, og Rettet-linja sier «De 101 andre» |
| AA9 | lav | `EXPERIENCE.md` siterer statusen med «i kveld» | Står: en datert linje ved føringen på main |
| ECH2 | lav | Kan `kursdag_felles` ikke leses, er den `None`, og statusen sier «i kveld» som ved en tom base | Står: linja i stripa faller bort på samme måte |
| ECH3 | lav | En henting før kl. 22 med `--uten-tidskontroll` tar ønskene i bruk med en gang | Står: statusen sier «tidligst» om den vanlige hentingen |
| ECH4 | lav | Mangler én aksje i lista dagens kurs, sier statusen «i kveld» til midnatt | Står: en ny kjøring samme kveld tar ønsket, som stripa sier «kan hentes nå» |
| VG2 | lav | Grensen på minuttet var ikke prøvd | Rettet: kl. 22:00 gir «i morgen» |
| VG4 | lav | Klokka i UTC var ikke prøvd i `TestDagen` | Rettet: to tilfeller i UTC |
| VG3 | lav | Bare lørdagen skiller demoen som står fast, fra en demo som regner | Står: lørdagen fanger det |
| VG5 | lav | Grensen ved 7 dager er bare prøvd med 12 | Står: fantes fra før, i stripa |
| VG6 | lav | Ingen sidetest med en tom base | Står: `TestDagen` har tilfellene uten kursdag |

## Spørsmål til gruppen

1. **Et ønske etter første kjøring samme kveld (ECH1, middels).** Jobben går
   kl. 22:15, og igjen kl. 22:45, 23:15 og 23:45. Et ønske om å følge en aksje
   kl. 22:30 tas inn kl. 22:45 samme kveld, mens statusen nå sier «Venter på
   henting i morgen etter kl. 22.» Siden vet ikke om jobben går igjen.
   *Forslag:* behold «i morgen», som stripa, og la hjelpen si at en senere
   kjøring samme kveld kan ta ønsket. Alternativet er «i kveld» til midnatt på
   en børsdag, som er feil når jobben er ferdig for kvelden. PR-en flettes
   ikke før gruppen har svart (regel 25).
2. **De andre stedene som sier «i kveld» (AA1–AA5, middels og lav).**
   Aksjesiden, merknaden i Min liste og «Er du sikker?» sier «ved hentingen i
   kveld» om en aksje som fjernes, og «Følg en aksje» sier «før kvelden».
   Svaret gjaldt statusene i «Dine egne aksjer» og «Følg en aksje», så de er
   ikke rørt. *Forslag:* rett dem på samme måte i denne storyen, med hjelpen,
   før PR-en flettes.
3. **Demoen.** Der står «i kveld etter kl. 22» fast, fordi demoen ikke henter,
   og bildene ellers ville fulgt dagen de ble tatt. *Forslag:* behold.

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
