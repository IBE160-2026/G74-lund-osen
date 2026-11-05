---
title: 'Story 2.3d (2.3e): kveldsjobben starter ikke Docker og Ollama for en ferdig dag, og CI-rettingen'
type: 'feature'
created: '2026-11-05'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '9706d1b8'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-3d-hentingen-hver-kveld.md'
  - '{project-root}/start/kveldshenting.ps1'
  - '{project-root}/src/fetch_prices.py'
---

## Intent

**Grunnlaget:** gruppens svar 03.11 kl. 20:48 (1), 05.11 kl. 12:33 og 05.11 kl. 19:33 (forslag a), ført under story 2.3d i `epics.md` (`113beb8e` og `9706d1b8`), og instruksjonen 05.11 kl. 19:41 i `docs/ai-prompts/2026-11-05.md` (`1d588198`). Én PR på grenen `2-3d-tidlig-stopp-og-ci`, én commit per endring.

a) «Start demoen på Windows» i `tester.yml` slutter med `exit 0` etter siste kontroll, som steget for den ekte versjonen.

b) I hver kjøring av `start/kveldshenting.ps1`, før steg 3, kjører `uv run python src/dagen_ferdig.py` med en tidsgrense (`-Sjekkgrense`, 120 s). Sjekken ser på børsdagen hentingen gjelder (`innevaerende_boersdag(norsk_dato(naa()))`, som `kjoer`), og om hver av de 15 har kurs (`manglende_i_basen`) og rad i vurdering (`manglende_vurderinger`), om hovedindeksen (`OSEBX`) har raden i `indeks`, og om hver aksje med en `Vurdering` har raden i KI-loggen, som `lag_ki_tekster` regner det. Basen åpnes med `_aapne_for_sjekken` (`mode=ro`, `query_only`), uten `.env`, nøkkel eller kall. Bare kode 0 og én linje som begynner med `FERDIG` og datoen, hopper over steg 3: én linje i loggen, `OSE_KI_TJENESTE=av`, og steg 4 går som før, med hentingen (0 kall når basen har dagen) og `--maal-omsetning`. Alt annet, også kode 1 (mangler), kode 2 (feil) og tidsgrensen, gir kjøringen som før.

## Utenfor

- Ingen endring i `fetch_prices.py`, `omsetning.py`, `ki_tekst.py` eller basen. Målingen har fortsatt sine egne regler for kvoten og kl. 23:45.
- Oppgaven i Oppgaveplanlegging og worktreen `G74-lund-osen-jobb` er ikke rørt. Endringen gjelder fra første kjøring etter at commiten fra midnatt har den, altså fredag 06.11.

## Commitene

- `2b26b542`: a), `exit 0` i «Start demoen på Windows».
- `f03bd70e`: b), `src/dagen_ferdig.py`, sjekken i `start/kveldshenting.ps1` (med `-Sjekkgrense`, også videre i kjøringen etter utsjekken), testene, README-en, `docs/hjelp.md` og en datert linje i PRD-en etter linja fra 28.10 om jobben.
- `3d53ca36`: testen for a), som mangelen på en test for a) gjorde nødvendig for mutanten.

## Tester og mutanter

- `tests/test_dagen_ferdig.py` (9 tester, basen laget av `kjoer` med falsk EODHD og falsk modell i `tmp_path`): en ferdig dag gir `FERDIG` og kode 0; basen har samme sha256 før og etter, uten `-journal` eller `-wal`; uten KI-tekster og uten hovedindeksen er dagen ikke ferdig; børsdagen er inneværende børsdag fra norsk dato (lørdag og etter midnatt); uten base mangler alt og ingen base lages; en feil og en base som ikke er SQLite gir kode 2; sjekken leser ikke `.env` og kaller ikke.
- `tests/test_kveldshenting.py`: den falske uv svarer også for sjekken. En ferdig dag spør ikke Docker (ingen `docker.txt`), henter med `tjeneste=av` og måler. «mangler», «feil», «ferdig-kode-1» og «henger» (med `-Sjekkgrense 2`) går som før, med Docker spurt.
- `tests/test_dobbeltklikk.py`: begge Windows-stegene slutter med `exit 0` etter siste `Write-Host`.
- Mutant A (`exit 0` tatt ut av «Start demoen på Windows») ble fanget av den nye testen. Mutant B (`$sjekk.Kode -eq 0 -and` tatt ut) ble fanget av `[ferdig-kode-1]`. Kopi før, og git-bloben og sha256 uten CR var lik HEAD etter begge.
- Hele settet alene: før `f03bd70e` 4082 bestått, 24 hoppet over og 6 porttester for `start.ps1` som feilet (ledig minne 5,2 GB); før `3d53ca36` 4082 bestått, 24 hoppet over og de 7 porttestene (3,7 GB).

## Gjennomgangen 05.11 kl. 20:11

Blind Hunter (10 funn), Edge Case Hunter (7) og Verification Gap (9) på `9706d1b8..3d53ca36`, etter hele settet. Ingen på høy. Rettingene står i `7ebc9aca`.

| Funn | Grad | Utfall |
|---|---|---|
| BH1, VG1, ECH2 | middels | Rettet: sjekken bruker av fristen for steg 3 (`-Tidsgrense`), med den minste av `-Sjekkgrense` og tiden som er igjen, så hentingen starter ikke senere enn før. Kommentaren om kl. 23:50 gjelder igjen. |
| BH2, ECH5 (lav), VG7 (lav) | middels | Rettet: `uv run --no-sync`, så sjekken aldri drepes midt i en synkronisering. Er miljøet ikke synket, feiler sjekken, og kjøringen går som før, med synkroniseringen i steg 4. README-en sier `--no-sync`. |
| BH9, VG9 (lav) | middels | Rettet: `test_utskriften_passer_regexen_i_skriptet` leser `-cmatch`-regexen fra skriptet og krever nøyaktig én linje fra den ekte sjekken for en ferdig dag, og ingen for en dag som mangler noe. |
| VG2 | middels | Rettet: `test_basen_er_lik_foer_og_etter_ogsaa_for_en_ferdig_dag`. |
| VG3 | middels | Avvist: kvoten leses først på `fetch_prices.py:1100`, etter at `kjoer` har returnert for en base som har dagen («Ingenting å hente (FR-402). 0 kall brukt.»). Hentingen bruker 0 kall. Målingen er ikke omtalt som 0 kall. |
| ECH1 | middels hos linsen, lav i triagen | Følger av svaret kl. 19:33 (indeksen er med i «ferdig»). Feiler OSEBX en dag der de 15 har kursene, henter `kjoer` ikke indeksen på nytt, så dagen blir ikke ferdig, og kjøringene går som før, med Docker og Ollama, til neste børsdag. Ingen kjøring blir verre enn før endringen, så graden er satt til lav. Spørsmål til gruppen: skal en manglende indeks hindre det tidlige stoppet når hentingen ikke kan hente den? |
| BH4 | lav | Rettet: `-cmatch`, så bare `FERDIG` med store bokstaver teller. |
| BH6 | lav | Rettet: første linje fra sjekken (det som mangler, bare symboler og dato) står i loggen ved kode 1 og 2. |
| VG6 | lav | Rettet: «Fant ikke uv. Sjekken av dagen er ikke kjørt.» |
| VG8 | lav | Rettet: hjelpen sier «uten KI-tekst» og at en feil i sjekken gir kjøringen som før. |
| BH3 | lav | Står: sier sjekken FERDIG rett før midnatt og hentingen starter etter, stopper tidskontrollen en børsdag med 0 kall, og en helgedag er børsdagen den samme (ECH, «Sjekket uten funn»). |
| BH5, ECH4 | lav | Står: `Kjoer-Med-Grense` gir -1 både ved tidsgrensen og når prosessen ikke starter. Utfallet er det samme, kjøringen som før. |
| BH7 | lav | Står: en KI-rad som feilet, teller som ferdig, som i `lag_ki_tekster` (en rad som finnes, står, FR-604). |
| BH8 | lav | Står: tre tilkoblinger kan i verste fall gi kode 1 eller 2, ikke en falsk FERDIG. |
| BH10, VG5 | lav | Står: en aksje med en grunn i stedet for vurdering, en base én versjon bak, kode 0 uten FERDIG og to FERDIG-linjer har ingen egen test. |
| ECH3 | lav | Står: en base én versjon bak gir kode 2 fra `SqliteIndekslager` og `SqliteKILogg`, og kjøringen går som før. |
| ECH6 | lav | Står: `-Sjekkgrense` sendes videre til versjonen etter utsjekken. En commit fra midnatt uten parameteren (en tilbakeføring av 2.3d) ville stoppet kvelden. Må med i en eventuell tilbakeføring. |
| ECH7 | lav | Står: en demobase kan gi FERDIG, men hentingen stopper ved `nekt_demobase` som før. |
| VG4 | lav | Står: nettsperren i `tests/conftest.py` (AD-8) er vernet mot kall. |

Hele settet alene før `7ebc9aca`: 4084 bestått, 24 hoppet over, de 6 porttestene og `test_hver_story_som_deles_har_egen_merkelapp`, fordi denne spesifikasjonen manglet merkelapp. Den ble lagt inn («2.3d, tidlig stopp»), og settet kjørt på nytt: 4088 bestått, 24 hoppet over og 3 porttester for `start.ps1` som feilet (ledig minne 4,1 og 4,2 GB). CI var grønn på `3d53ca36` (42091407924).
