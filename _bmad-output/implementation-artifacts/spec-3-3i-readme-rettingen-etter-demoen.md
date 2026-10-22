---
title: 'Story 3.3 (3.3i): README-rettingen etter gruppens gjennomgang av demoen 21.10'
type: 'feature'
created: '2026-10-22'
status: 'ready-for-dev'
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

## Det som ikke endres

- Ingen test går på nett. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildene tas med demobasen i en midlertidig mappe.
- Første henting på dagtid (2.3c), og tidskontrollen i hentingen.
- Briefen står.
