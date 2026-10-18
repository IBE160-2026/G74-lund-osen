---
title: 'Story 3.3c: tre bilder i «Kom i gang», demoen først og fire rettelser'
type: 'docs'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '2e2bcca'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** gruppen gikk selv gjennom «Kom i gang» 16.10 kl. 20:40–21:11 og fant fire ting som ingen test fant: ZIP-fila ble dratt inn i stedet for mappa, mellomrommet etter `cd` manglet, «Cannot find path» hadde ikke noe svar, og det var uklart hvor kommandoen limes inn og hvor kopi-ikonet er. Faglærer prøver demoen, men den står etter den ekte versjonen. Beslutningen 16.10 kl. 21:16, med svarene kl. 21:25 og 21:57, står under story 3.3 i `epics.md`.

**Grunnlaget:** instruksjonen 18.10 kl. 12:23, og svarene kl. 14:48 på to spørsmål om grensene i testene. PR-en stopper før flettingen og venter på ja.

## Planen, én commit per punkt

1. Denne spesifikasjonen, og svarene kl. 14:48 under story 3.3.
2. Bildene: de tre skjermbildene fra gjennomgangen i `docs/bilder/readme/`, i steg 1, 2 og 4 med alt-tekst og en kort tekst under, og «Mappestruktur» nevner dem. Testene for bildene godtar disse tre og CI-merket, og ingen flere.
3. Rekkefølgen: «Demoen» før «Den ekte versjonen (anbefalt)» i README-en, `docs/hjelp.md` og tabellen for Prøve 1, som også får en kolonne for tiden. Testen krever demoen først.
4. a) Steg 4: mappa, ikke ZIP-fila, og hva man gjør når det står `.zip` til slutt.
5. b) «is not recognized as the name of a cmdlet»: mellomrommet etter `cd`.
6. c) «Cannot find path … because it does not exist»: dra mappa på nytt.
7. d) Hvordan en kommando kopieres og limes inn, og hva «Serving on http://0.0.0.0:5000» betyr.

## Avgjort i spesifikasjonen

- **Bildene** er valgt blant de 17 skjermbildene fra 16.10 kl. 20:41–21:03 i `Bilder\Skjermbilder`: `Skjermbilde 2026-10-16 204605.png` («Engine running»), `… 210020.png` (fanen «HTTPS» og «Download ZIP») og `… 205658.png` (`PS C:\prove\G74-lund-osen-main>`). Ingen av de tre viser brukernavn, nøkkel eller kurser, og ingen har tekstfelt i PNG-fila (bare `IHDR`, `gAMA`, `pHYs`, `sRGB`, `IDAT` og `IEND`). De andre bildene fra tidsrommet viser brukernavnet i stien, og brukes ikke. Kopiene ligger i `_privat/bilder/`, som er i `.gitignore`.
  *Rettet 2026-10-18 (gjennomgangen, VG4):* mappa er `OneDrive\Pictures\Skjermbilder` på maskinen, som Utforsker viser som «Bilder\Skjermbilder». Setningen om at de andre bildene viser brukernavnet, stemmer ikke for alle 14. Sju av dem viser brukernavnet i stien (`204536`, `204541`, `204830`, `204845`, `205044`, `205207` og `205426`). De andre er valgt bort fordi instruksjonen ber om akkurat de tre: «Engine starting» (`204120`), menyen med fanen «GitHub CLI» eller «SSH» (`204158`, `204410`), «Cannot find path» uten brukernavn (`205506`), `dir` (`205539`) og README-en (`205835`, `210335`).
  *Lagt til 2026-10-18 (gjennomgangen, VG12):* linja under story 3.3 fra 16.10 sa at PR-en med bildene skulle ha alt-tekst som sier at det er demoen. De tre bildene viser ikke appen, verken demoen eller den ekte versjonen, så alt-tekstene sier hva bildet viser, og regelen om at bilder i README-en aldri viser den ekte versjonen, holder.
  *Lagt til 2026-10-18 (gjennomgangen, VG14):* meldingen i testen for rettelse b, `'cdC:\…' is not recognized as the name of a cmdlet`, er fra skjermbildet `Skjermbilde 2026-10-16 205426.png`, som ikke er i repoet. Edge Case Hunter fikk den samme meldingen i PowerShell 5.1.
- **Spørsmålene under «Står du fast?»:** høyst 10, ikke 8 (svar 1 kl. 14:48). Det endrer grensen fra 11.10 kl. 22:32.
- **Ordgrensen** (svar 2 kl. 14:48): 65 ord per steg står for teksten i steget. Bildet og teksten under det telles for seg, og teksten under har høyst 25 ord. Forklaringen av hvordan en kommando kopieres, står én gang, i et kort avsnitt rett før det første steget med en kommando, og hvert steg med en kommando sier bare at den limes inn i PowerShell-vinduet fra steg 4. Blir et steg fortsatt over 65 ord, flyttes detaljene til `docs/hjelp.md` med en lenke fra steget.
- **Rettelse b** gjelder bare meldingen der `cd` står klistret til stien (`'cdC:\…' is not recognized`). «`docker` er ikke gjenkjent» har sitt eget svar i `docs/hjelp.md`, og står.

## Boundaries

- Bare dokumentene, testene og de tre bildene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- Ingen linje fjernes fra «Kom i gang» eller `docs/hjelp.md`, bare utvides. Flyttingen endrer verken stegnumrene eller teksten i stegene.
- Bildet av oversikten kommer ikke tilbake her. Det kommer etter 3.4b, i en egen README-PR (gruppens svar 18.10 kl. 00:20).

## Åpne punkter

- **«Til faglærer» (VG9, ECH3):** beslutningen 16.10 kl. 21:16 under story 3.3 sier også at «Til faglærer» får lenker til demoen, den ekte versjonen og testene, og at det bygges i README-PR-en søndag 18.10. Instruksjonen kl. 12:23 nevner det ikke, så det er ikke bygget her (regel 9). Spørsmål til gruppen: i denne PR-en, eller i PR-en som rydder README-en?
- **Antallet spørsmål under «Står du fast?» (ECH4, regel 12):** beslutningen 16.10 kl. 21:53–21:58 sier «fem spørsmål under «Står du fast?»» i PR-en som rydder README-en, og svar 1 kl. 14:48 sier høyst 10. Her står 10. Hvilken som gjelder for oppryddingen, er åpent.

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. M1–M4 er fra instruksjonen, fanget på `c258565` og på nytt på `9a5f526`. M5–M9 er ett for hvert funn med dom medium som kan prøves med en mutant, fanget på `9a5f526`:
- M1, et bilde til i steg 1 (`docs/bilder/readme/ekstra.png`, en kopi av et av bildene): `test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket`.
- M2, lenken om `.zip` borte fra steg 4: `test_steg_4_mappa_ikke_zip_fila`.
- M3, svaret om mellomrommet etter `cd` borte fra «Står du fast?»: `test_svaret_om_mellomrommet_etter_cd`.
- M4, den ekte versjonen før demoen igjen: `test_demoen_foerst_og_zip_foer_kommandoene`.
- M5, «det nye PowerShell-vinduet fra steg 4» i steg 8 (BH1): `test_kopieringen_forklares_en_gang_og_hvert_steg_sier_hvor`.
- M6, kopieringsavsnittet over 65 ord (VG6, ECH2): samme test.
- M7, den gamle rad 16 i Prøve 1 (BH7): `test_henvisningene_og_proevetabellen`.
- M8, Esc uten Ctrl+U for Mac (VG8, ECH1): `test_steg_4_mappa_ikke_zip_fila`.
- M9, «fra steg 2, ikke ZIP-fila, der» i steg 4 (BH2): `test_steg_4_mappa_ikke_zip_fila`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `2e2bcca..c258565`, med bildene som stat. Linsene var Blind Hunter (BH, 14 funn, bare diffen), Edge Case Hunter (ECH, 17, der ECH8, ECH9 og ECH17 ikke fant noen feil) og Verification Gap (VG, 15, der VG1, VG2, VG3, VG5 og VG13 fant kravene oppfylt). Ingen av dem kjørte pytest. Åtte funn har dom medium. Sju er rettet i `483b013` og `9a5f526`, og ett er et åpent spørsmål til gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | Steg 8 sa «det nye PowerShell-vinduet fra steg 4», men vinduet fra steg 4 kjører appen | medium | patch: «i det nye PowerShell-vinduet». M5 |
| BH2, ECH13 | I steg 4 kunne «der README og compose ligger» leses om ZIP-fila | medium | patch: «fra steg 2 (ikke ZIP-fila), der». M9 |
| BH3, BH4, VG6, ECH2, ECH12 | Kopieringen ble forklart flere steder med to ord for samme knapp, og avsnittet var 94 ord | medium | patch: avsnittet har høyst 65 ord, sier at ikonet er knappen stegene nevner, og «Serving on» står bare i stegene der linja står. Setningene om «knappen til høyre i boksen» i demoen steg 5 og den ekte versjonen steg 6 står, fordi ingen linje fjernes (instruksjonen, steg 4). M6 |
| BH7, VG3, ECH15 | Rad 16 i Prøve 1 begynte med å stoppe demoen, som ikke lenger kjører sist | medium | patch: raden er skrevet om, og den gamle teksten står i en Rettet-linje. M7 |
| VG7 | Rettelse a og d sto ikke under «Står du fast?» | medium | patch for d: svaret «Ingenting skjer når jeg limer inn.» har kopieringen, likt med `docs/hjelp.md`. a står i steg 4 og i svaret om «Cannot find path», og «Står du fast?» har nådd grensen på 10 |
| VG8, ECH1 | Esc tømmer ikke linja i Terminal på Mac | medium | patch: «Esc (Windows) eller Ctrl+U (Mac)». M8 |
| VG9, ECH3 | «Til faglærer» har ikke lenkene fra beslutningen 16.10 | medium | åpent: ikke i instruksjonen, spørsmål til gruppen (over) |
| BH5, ECH11 | Mac mangler i teksten under bildet i steg 4 og i stegene | low | patch for bildeteksten: «(`%` på Mac)». Stegene står med PowerShell: avsnittet sier «Terminal på Mac», og fire steg har nådd 65 ord |
| BH6 | Svaret om `cd` i README-en sa ikke hva `'docker'` i meldingen betyr | low | patch: samme setning i README-en og `docs/hjelp.md` |
| BH8 | Kolonnen «Tid» hadde ingen enhet | low | patch: «Tid (min)» |
| BH10, VG10, ECH10 | Rettet-linja i `docs/hjelp.md` sa at svarene var de samme | low | patch: en ny Rettet-linje |
| BH11 | Begge seksjonene begynner på steg 5, uten overgang | low | patch: «Vil du også prøve den ekte versjonen, går du videre til steg 5 under.» |
| BH12, ECH6 | Kursiv rett under bildet uten tom linje ble godtatt som tekst under | low | patch: minst én tom linje. `_kursiv_`, fet og kursiv over to linjer gir en falsk feil, aldri en falsk bestått |
| BH13 | Bildetesten viste ikke lista når den feilet | low | patch |
| VG4 | Mappa og påstanden om de andre bildene | low | patch: Rettet-linje over |
| VG12 | Alt-teksten skulle si demoen | low | patch: forklart over |
| VG14 | Kilden til meldingen i testen | low | patch: forklart over |
| ECH4 | Fem spørsmål (16.10 kl. 21:53) mot høyst 10 (i dag) | low | åpent punkt (regel 12), over |
| BH9 | Kolonnen «Tid» i samme commit som rekkefølgen | low | avvist: instruksjonen har den i punkt 3 |
| BH14, ECH7 | Bildene står utenfor listepunktene | low | avvist: som boksene fra før. GitHub beholder startnummeret, så stegene får riktige tall |
| VG1, VG2 | At ingen linje er fjernet og stegene er uendret, er bare sjekket for hånd | low | avvist: VG sjekket det ord for ord, og en test mot `2e2bcca` gir ikke mening etter flettingen |
| VG11 | `updated` i `docs/hjelp.md` ble ikke satt i hver commit | low | avvist: står riktig ved HEAD |
| VG15 | Rekkefølgen i `docs/hjelp.md` sjekkes i `test_hvorfor_bare_15_aksjer` | low | avvist: testen leser seksjonen der, og M4 viser at rekkefølgen i README-en har sin egen |
| ECH5 | Fire steg står på 65 ord | low | avvist: ingen feil. Neste tillegg må gå til `docs/hjelp.md` (svar 2) |
| ECH14 | Tekst mellom avsnittet og «### Demoen» ble ikke sjekket | low | patch: testen krever at «### Demoen» kommer rett etter avsnittet |
| ECH15 | Rad 5 spør om tiden, og Prøve 2 har ingen kolonne for tid | low | avvist: instruksjonen gjelder tabellen for Prøve 1 |
| ECH16 | Eldre linjer sier at README-en ikke har bilder | low | avvist: daterte historikklinjer. Vurderingsmatrisen og §13 får en linje når PR-en flettes |
