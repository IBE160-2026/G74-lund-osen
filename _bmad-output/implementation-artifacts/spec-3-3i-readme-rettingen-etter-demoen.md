---
title: 'Story 3.3 (3.3i): README-rettingen etter gruppens gjennomgang av demoen 21.10'
type: 'feature'
created: '2026-10-22'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '02a51bb'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3h-readme-bak-piler-og-levende-hjelp.md'
---

## Intent

**Problem:** gruppens gjennomgang av demoen 21.10 fant at steg 1–4 i «Felles for begge» ikke sier hva man gjør når Docker Desktop finnes fra før, eller står i «Resource Saver mode», hvor mappa skal pakkes ut, hva et tall i mappenavnet betyr, hvordan PowerShell åpnes i riktig mappe, og hvordan man ser at man står der. Meldingen fra nettleseren når appen ikke svarer, står ingen steder. Den ekte versjonen sier ikke hva gratiskontoen hos EODHD gir, og demoen lenker ikke til den.

**Grunnlaget:** radene U8–U15, U51, U52 og U55 i `docs/ux-logg.md`, avgjørelsene 21.10 kl. 22:51 og 22.10 kl. 00:09 under «Prioritering» i `epics.md` (rekkefølgen: 10.7, README-rettingen, 8.6, 2.12), og svaret 19.10 kl. 14:46 om at demoen anbefales. Første henting på dagtid (U53, U54, avgjørelsen 21.10 kl. 23:33) er ikke med; den kommer i 2.3c. Instruksjonen er den kl. 16:06 i dagsfila 22.10.

## Radene, slått opp i `docs/ux-logg.md` 22.10

- **U8:** «Steg 1 begynner med å installere Docker Desktop og sier ikke hva man gjør når det finnes på maskinen fra før.»
- **U9:** «Docker Desktop viste «Resource Saver mode» i stedet for «Engine running». Verken README-en eller `docs/hjelp.md` nevner den modusen.»
- **U10:** «PowerShell åpnet i systemmappa til Windows, trolig som administrator, og steg 3 og 4 sier ikke hvordan man kommer til riktig mappe.»
- **U11:** «README-en sier ikke om man skal lage en ny mappe, eller hvor den utpakkede mappa skal ligge.»
- **U12:** «Steg 4 har ingen kommando å kopiere, bare at mappa dras inn i vinduet.»
- **U13:** «Nettleseren sa at 127.0.0.1 nektet å koble til (ERR_CONNECTION_REFUSED).» Svaret, å vente på «Serving on», står i `docs/hjelp.md`, men ikke under «Står du fast?», og «Årsaken er ikke kjent».
- **U14:** «Etter flere nedlastinger legger Windows et nummer til den ytre mappa, som «G74-lund-osen-main (4)».» Tillegget kl. 22:30: «En kommando med fast sti (U12) treffer da en eldre kopi.»
- **U15:** «Sjekken i steg 4, at mappenavnet står foran `>`, ser ut til å stemme også i den ytre mappa når den har et nummer.»
- **U51:** «Demoen skal lenke til stegene for den ekte versjonen i README-en på GitHub, og si at det trengs en egen gratis nøkkel fra EODHD.»
- **U52:** «Teksten til faglærer skal invitere til å prøve den ekte versjonen, og si at demoen viser så mye som mulig. Svaret 19.10 kl. 14:46 om at demoen anbefales står, og dette legger til en invitasjon.»
- **U55:** «README-en skal si at appen er gratis, at gratiskontoen hos EODHD gir begrensningene (20 kall i døgnet, og derfor opptil 18 aksjer), og at et betalt abonnement gir flere kall.» «Vilkårene og prisene hos EODHD slås opp før noe skrives om betalte abonnementer.»

## Kildene, lest 22.10.2026

- **Docker Desktop, «Resource Saver mode»:** https://docs.docker.com/desktop/use-desktop/resource-saver/: «Resource Saver mode significantly reduces Docker Desktop's CPU and memory utilization on the host by 2 GBs or more», «by automatically stopping the Docker Desktop Linux VM when no containers are running for a period of time.» «A moon icon displays on the Docker Desktop status bar as well as on the Docker icon in the system tray.» «Docker Desktop exits the Resource Saver mode automatically when it needs to.» «Commands that cause an exit from Resource Saver take a little longer to execute». Siden har ingen dato.
- **Docker Desktop, start etter installasjonen:** https://docs.docker.com/desktop/setup/install/windows-install/, «Start Docker Desktop»: «Search for Docker, and select Docker Desktop in the search results.» Siden har ingen dato.
- **Windows, pakke ut:** https://support.microsoft.com/en-us/windows/zip-and-unzip-files-8d28fa72-f2f9-712f-67df-f80cf89fd4e5: «To unzip all the contents of the zipped folder, right-click (or press and hold) the folder,» og så «Extract All...». Siden har ingen dato.
- **Windows, PowerShell fra adressefeltet:** ingen side i dokumentasjonen til Windows eller PowerShell sier det. «Starting Windows PowerShell» på https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/starting-windows-powershell (ms.date 2025-03-27) nevner bare Start-menyen og kommandolinja. Det nærmeste er et arkivert blogginnlegg på Microsoft Learn fra 2013, skrevet for Windows 8, https://learn.microsoft.com/en-us/archive/blogs/simonmay/power-tip-launch-powershell-from-file-explorer-in-one-second: «hit **ALT + D** to jump to the address bar and simply type **PowerShell**», om å starte PowerShell «from the current location you're looking at in File Explorer». En kommentar der sier at adressefeltet kan åpne en mappe som heter «powershell» fra historikken i stedet. Gruppen bør prøve steget på Windows 11 før innleveringen.
- **Windows, tallet i mappenavnet (U14):** ingen kilde hos Microsoft er funnet. README-en sier derfor bare det gruppen så, at mappa kan få et tall som «(4)» etter flere nedlastinger, ikke hvem som legger det til.
- **EODHD, gratiskontoen og abonnementene:** https://eodhd.com/pricing: «Once you register you get 20 free API calls per day.», raden for historikk viser «1 yr» for gratisplanen, og de betalte planene har 100000 kall i døgnet, fra «$19.99/mo.». https://eodhd.com/financial-apis/api-limits/: «Free plan — 20 API calls per day.» og «Paid plans — from 100,000 API calls per day.» Sidene har ingen dato utenom «© Unicorn Data Services, 2017-2026».

## Kontrollpunktene

- a) «Felles for begge», steg 1–4: har man Docker Desktop, starter man det, ellers installerer man det (U8); «Resource Saver mode» er også klart, slik Docker beskriver det (U9); å pakke ut i Nedlastinger holder, uten ny mappe, og har mappa fått et tall som «(4)», brukes den nyeste (U11, U14); på Windows åpnes PowerShell i riktig mappe ved å skrive `powershell` i adressefeltet i Filutforsker i den innerste mappa, ikke som administrator, og å dra mappa inn er den andre veien (U10, U12); og kontrollen i steg 4 er at `dir` eller `ls` viser README.md og compose.yaml (U15). Under «Står du fast?» et svar på at 127.0.0.1 nektet å koble til, med ERR_CONNECTION_REFUSED ordrett (U13). `docs/hjelp.md` følger med.
- b) Den ekte versjonen: appen er gratis, gratiskontoen hos EODHD gir 20 kall i døgnet og kurser ett år tilbake, en henting bruker 16, og et betalt abonnement gir flere kall, med lenke og dato, men appen bruker ikke flere (U55). En kort invitasjon til å prøve den ekte versjonen, mens demoen fortsatt anbefales (U52). Demolinja øverst i demoen får en lenke til «Den ekte versjonen» i README-en på GitHub, og den ekte versjonen har ingen slik lenke (U51). Ingenting om første henting på dagtid.
- c) Testene, med «Ville feilet hvis», uten nett: lenken står i demoen og ikke i den ekte versjonen; ERR_CONNECTION_REFUSED står under «Står du fast?»; tallene 20 og 16 i README-en stemmer med koden.

## Planen, én commit per punkt

1. a) README-en, steg 1–4 og «Står du fast?», og `docs/hjelp.md`. Titlene i fet skrift i steg 1–4 står, så `STEGENE_FOER_3_3H` i `tests/test_docker.py` ikke endres. Det nye spørsmålet under «Står du fast?» legges til i `BEHOLDT_I_README` i samme commit, med grunnen her.
2. b) README-en, den ekte versjonen og «Til faglærer», og lenken i demolinja i `src/templates/_ramme.html`, med adressen som en konstant i `src/app.py`. `_ramme.html` er med i avtrykkene bak begge bildene i `docs/appen/`, så bildene tas på nytt og avtrykkene oppdateres i samme commit, etter fremgangsmåten i testene.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Tallet 20 er ikke en konstant i koden.** Hentingen leser `dailyRateLimit` fra `/api/user`. Testen binder 20 og 16 i README-en slik: 16 er antallet kall en henting gjør med en falsk EODHD (`len(AKSJEUNIVERS) + 1`), og 20 er tallet i docstringen øverst i `src/fetch_prices.py` og gir, med 16, de 4 kallene `kall_til_nye_forsoek` gir til nye forsøk, som `docs/hjelp.md` sier.
- **U55 sier «opptil 18 aksjer».** Det står alt i `docs/hjelp.md` («Planen er at du senere kan velge opptil 18 aksjer selv»), og instruksjonen sier 16 per henting, så README-en sier 16 og ikke 18.
- **Lenken i demolinja** går til https://github.com/IBE160-2026/G74-lund-osen#den-ekte-versjonen og står bare når basen har demomerket, i samme blokk som «Eksempeltall».

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter:

- **M1:** lenken også i den ekte versjonen.
- **M2:** ERR_CONNECTION_REFUSED borte fra «Står du fast?».
- **M3:** 16 byttet med 15 i README-en.

## Avgjort underveis

- **«Står du fast?» har høyst 6 spørsmål, ikke 5** (VG1). Grensen på 5 er fra beslutningen 16.10 kl. 21:53–21:58 og svarene 18.10 kl. 15:37 (story 3.3d). Instruksjonen kl. 16:06 ber om et svar under «Står du fast?» på at 127.0.0.1 nektet å koble til (U13), og det passer ikke inn i noen av de fem: de gjelder Docker, ZIP-fila og mappa, ikke nettleseren. Testen heter fortsatt `test_staar_du_fast_har_hoeyst_5_spoersmaal`, fordi `docs/vurderingsmatrise.md` og vedlegget i `docs/kvalitetssikring.md` nevner den, og grunnen står i docstringen, og spørsmålet står i `BEHOLDT_I_README` foran «no configuration file provided» (`6fb1f32`). Gruppen kan velge å slå det sammen med et annet i stedet.
- **`ERR_CONNECTION_REFUSED` står i svaret, ikke i spørsmålet.** Testen av pilene godtar ikke `_` i en `<summary>`, og meldingen står i kodeformat i svaret, så den kan søkes opp. Spørsmålet er «Nettleseren sier at 127.0.0.1 nektet å koble til.», det samme i `docs/hjelp.md`. Svaret sier også at andre nettlesere sier det med andre ord (BH4). Hva Firefox og Safari skriver, er ikke slått opp, så det siteres ikke (regel 11).
- **«Resource Saver mode» står også i det første svaret under «Står du fast?»**, fordi testen av det svaret krever alt som står i svaret om «Engine running» i `docs/hjelp.md`.
- **Demolinja** er «Ekte kurser trenger en gratis nøkkel fra EODHD: se Den ekte versjonen.», med lenken på «Den ekte versjonen». Med «i README-en» til slutt brøt linja over to linjer i 1280 px og flyttet sidene 18 px ned (målt 1648 og 1890 px mot 1630 og 1872), så bildene ville fått ny høyde. Uten de ordene er den én linje, og høydene står.
- **Bildene** ble tatt på nytt, med samme høyde, fordi `_ramme.html` og `stil.css` er med i avtrykkene bak dem. `AVTRYKK_BAK_BILDET` og `AVTRYKK_BAK_AKSJESIDEN` er satt på nytt i `16d9d63`.
- **Avtrykkene av pilene** (`AVTRYKK_I_PILENE` i `tests/test_docker.py`, VG2):
  - «Den ekte versjonen»: avsnittet om at appen er gratis, og hva gratiskontoen og et betalt abonnement hos EODHD gir, står foran steg 5 (U55, `16d9d63`), og fra rettingen at de 4 kallene som er igjen, går til nye forsøk (BH5, `1edd479`). Stegene står uendret. Var `fd359e96…`, så `36cc2505…`, og er `542c8991…`.
  - «Demoen»: steg 6 sier at demolinja har en lenke til den ekte versjonen (VG8, `1edd479`). Var `b3f50242…`, og er `f124a92b…`.
- **Steg 3 har Start-menyen som den andre veien** på Windows, med «ikke ISE og ikke som administrator» der, fordi adressefeltet ikke er prøvd på Windows 11 av oss (BH2, VG5). Fra adressefeltet gjør man bare kontrollen i steg 4.
- **`tests/test_utseende.py` godtar lenken til README-en på GitHub** som en `<a href>` på sidene med demomerket, ved siden av investorsidene. Den laster ingenting. Testene der er ikke med i testene for dokumentene, og hele settet fant det etter triagen: fem feil i tre tester.
- **Tallet 20** kommer fra EODHD (`dailyRateLimit` i `/api/user`), ikke fra en konstant i koden. Testen binder det til docstringen i `fetch_prices.py` og til de 4 kallene i hjelpen, og «med de 15» i hjelpen til lista (ECH10).

*Rettet 2026-10-22 kl. 17:24:* den første kjøringen av hele settet hadde 5 feil: 3 tester i `tests/test_utseende.py` og 2 i `tests/test_kvalitetssikring.py`, fordi testen av «Står du fast?» hadde fått nytt navn. Punktet over om `tests/test_utseende.py` sier «fem feil i tre tester».

## Mutantene, kjørt

I en fersk klon med `core.autocrlf=false`, slettet etterpå, én om gangen med `-x`, med kopi før og sha256 lik HEAD etter hver. Kjørt på `b4a9ae2` og igjen på `1edd479`, med `tests/test_docker.py` og `tests/test_demo.py`, og en gang til med bare de nye testene (`-k`) (VG7).

| # | Mutant | Først i fila (`1edd479`) | De nye testene alene |
|---|---|---|---|
| M1 | Lenken også i den ekte versjonen, utenfor blokken for demoen i `_ramme.html` | `test_bildet_tas_paa_nytt_naar_oversikten_endres` | `test_ingen_lenke_i_den_ekte_versjonen` |
| M2 | `ERR_CONNECTION_REFUSED` borte fra svaret under «Står du fast?» | `test_like_spoersmaal_har_samme_svar` | `test_err_connection_refused_under_staar_du_fast` |
| M3 | 16 byttet med 15 i pila til den ekte versjonen | `test_innholdet_i_pilene_er_det_samme_som_foer` | `test_tallene_20_og_16_stemmer_med_koden` |

## Gjennomgangen

Gjennomgang 22.10 på diffen `02a51bb..b4a9ae2`. Linsene var Blind Hunter (BH, 8 funn, bare diffen), Edge Case Hunter (ECH, 11 funn) og Verification Gap (VG, 9 funn), hver for seg og uten å endre noe i repoet. 28 funn ble 20 rader. Fem hadde dom medium, og alle er rettet, i `1edd479` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1, VG4 | Hjelpen sa at man slipper steg 4 fra adressefeltet, og hoppet over kontrollen med `dir` | medium | rettet: man slipper `cd`, men gjør kontrollen |
| BH2, VG5 | Steg 3 hadde bare adressefeltet, og advarslene om ISE og administrator sto ved feil vei | medium | rettet: Start-menyen som den andre veien, med advarslene |
| VG3, ECH3 | Bildeteksten i steg 4 hadde bare det gamle tegnet, navnet foran `>` | medium | rettet: «Sjekk med `dir` eller `ls`.» (høyst 25 ord, og setningen om `>` er bundet av en test) |
| VG1 | Grensen 5 ble 6 uten at spesifikasjonen sa det | medium | rettet under «Avgjort underveis» |
| VG2 | Avtrykket av pila ble endret uten grunnen i spesifikasjonen | medium | rettet under «Avgjort underveis» |
| BH3, ECH4 | «Da står vinduet i en annen mappe» kom etter setningen om ISE | low | rettet |
| BH4 | Spørsmålet passer bare meldingen fra Chrome og Edge | low | rettet: «Andre nettlesere sier det med andre ord.» uten å sitere dem |
| BH5, ECH11 | «ikke flere enn 16» sa ikke at resten går til nye forsøk | low | rettet |
| ECH2 | Ingenting sa hva man gjør når `dir` ikke viser filene | low | rettet i hjelpen: `cd G74-lund-osen-main` fra den ytre |
| ECH5 | Tallet står på den ytre mappa, og «slett de gamle» kunne slette `.env` | low | rettet i hjelpen |
| ECH10 | 20 er bundet til en docstring, og «med de 15» ikke til lista | low | rettet: lista er bundet; 20 kommer fra EODHD, under «Avgjort underveis» |
| VG7 | Det sto ikke hvilken test som fanget mutantene | low | rettet: tabellen over |
| VG6 | Steg 2 og 4 mistet de engelske navnene og «den innerste hvis det er to» | low | avvist: stegene er på grensen på 65 ord; de engelske navnene står i hjelpen, og «den innerste» i steg 3 |
| BH6, VG9, ECH8 | Testen av den ekte versjonen ser bare på `/` og `/min-liste` | low | uten endring: lenken står i én felles ramme for alle sidene |
| ECH6 | PowerShell fra adressefeltet arver rettighetene til Filutforsker | low | uten endring: fra adressefeltet trengs ikke dra og slipp |
| BH7 | Invitasjonen var tung å lese | nit | rettet |
| BH8 | Spesifikasjonen sto i `ready-for-dev` | nit | rettet: `review` |
| VG8 | Steg 6 i demoen nevnte ikke lenken i demolinja | nit | rettet |
| ECH7 | Demolinja har lite å gå på i 1280 px, og fokus på lenken | nit | uten endring: linja kan bryte uten fast høyde, og fokusrammen finnes alt |
| ECH9 | Ankeret åpner ikke pila på GitHub | nit | uten endring: README-en sier at man klikker på pila |

## Det som ikke endres

- Ingen test går på nett. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildene tas med demobasen i en midlertidig mappe.
- Første henting på dagtid (2.3c), og tidskontrollen i hentingen.
- Briefen står.
