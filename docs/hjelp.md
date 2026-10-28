---
title: "Hjelp til «Kom i gang»"
status: aktiv
created: 2026-10-11
updated: 2026-10-28T19:24
---

# Hjelp til «Kom i gang»

Spørsmål og svar til «Kom i gang» i [README-en](../README.md), sortert etter steget de hører til. De vanligste står også i README-en, under «Står du fast?». Dobbeltklikket står først, som i README-en. Stegene 1–4 hører til «Med Docker Desktop» og er felles for begge versjonene der, og demoen står før den ekte versjonen.

## Start med dobbeltklikk

### Jeg finner ikke de fire filene.

Etter «Pakk ut alle» på Windows ligger en `G74-lund-osen-main` inne i en annen med samme navn. Åpne den innerste, der README ligger. De fire filene står øverst der: `Start demoen` og `Start den ekte versjonen`, som `.cmd` for Windows og `.command` for Mac. Står du inne i ZIP-fila, se «ZIP-fila ser ut som en vanlig mappe.» under steg 2.

### Vinduet lukkes med en gang.

Har du dobbeltklikket inne i ZIP-fila uten å pakke ut, finner ikke startfila skriptene i `start/`. Pakk ut først, og dobbeltklikk i den innerste `G74-lund-osen-main`.

### Det er to filer som heter «Start demoen».

Windows viser ofte `Start demoen.cmd` uten filendelsen og `Start demoen.command` med den. På Windows tar du den som bare heter «Start demoen». `.command` er for Mac, og på Windows spør den bare hvilket program som skal åpne den.

### Windows advarer mot fila.

Første gang kan Windows advare mot `Start demoen.cmd` eller `Start den ekte versjonen.cmd`, fordi fila er lastet ned fra nettet. Advarselen heter «Windows beskyttet PC-en». Klikk «Mer informasjon», og så «Kjør likevel». Spør Windows om du vil kjøre fila, svarer du ja. Mer står under «Slik virker dobbeltklikket» i [README-en](../README.md#slik-virker-dobbeltklikket).

### Mac sier at fila ikke kan åpnes.

Første gang kan macOS stoppe `Start demoen.command` eller `Start den ekte versjonen.command`, fordi fila er lastet ned fra nettet. Fra macOS 15 holder det ikke å høyreklikke og velge Åpne. Velg Apple-menyen > Systeminnstillinger, og Personvern og sikkerhet i sidepanelet. Under Sikkerhet klikker du «Åpne likevel» og skriver inn passordet ditt. Knappen står der i omtrent en time etter at du prøvde å åpne fila. Dobbeltklikk så fila på nytt. På macOS 14 og eldre kan du også høyreklikke fila, velge Åpne og bekrefte.

### Vinduet sier at mappa har .git.

`Start den ekte versjonen` starter ikke i en mappe med `.git`, en klon av repoet, heller ikke på main. Da stopper vinduet før noe installeres eller hentes, så et dobbeltklikk i en klon aldri henter med nøkkelen som ligger i den. Last ned en egen kopi med «Download ZIP» på GitHub, pakk den ut, og bruk din egen nøkkel fra EODHD. `Start demoen` starter også i en klon.

### Vinduet sier at den andre versjonen av OSE Signal stoppes.

Demoen eller den ekte versjonen kjørte allerede fra denne mappa, på samme port, fra et annet dobbeltklikk eller startet med `uv run waitress-serve`. Skriptet sier fra med en gang, men stopper den først rett før appen starter, så den kjører videre hvis skriptet stopper før det, for eksempel fordi `uv sync` feiler. Feiler hentingen, starter appen likevel med det som er hentet før, og da stoppes den andre versjonen. Så venter skriptet til porten er ledig, og starter den du dobbeltklikket. Det andre vinduet sier da at appen stoppet, og at det kan lukkes fordi den andre versjonen kjører.

### Vinduet sier at et annet program svarer på 127.0.0.1:8000.

Skriptet stopper aldri andre programmer, heller ikke OSE Signal fra en annen mappe, og vinduet sier hvilket program det er. Det sjekkes før uv, og igjen rett før appen starter, i tilfelle et annet program har tatt porten i mellomtiden. Er det demoen eller appen i Docker, stopper du den med `docker compose --profile demo down` i et terminalvindu i mappa med koden. Den stopper både demoen og den ekte versjonen. Er det et annet program, lukker du det. Dobbeltklikk så på nytt.

### Hvor finner jeg nøkkelen, og hvordan limer jeg den inn?

`Start den ekte versjonen` åpner registreringssiden hos EODHD første gang. Når du har laget kontoen, står nøkkelen som «API token» under «Dashboard», med kopiknappen til høyre. Lim den inn i vinduet med Ctrl+V eller et høyreklikk på Windows, og med Cmd+V på Mac, og trykk Enter. På Windows vises den som stjerner. På Mac vises ingenting mens du limer inn, men nøkkelen kommer med.

### Nøkkelen var feil.

Vinduet spør bare etter nøkkelen når den mangler i `.env`. Åpne `.env` i mappa, slett det som står etter `EODHD_API_KEY=`, og lagre. Neste dobbeltklikk på «Start den ekte versjonen» spør da på nytt.

## Steg 1: Docker Desktop

### Må jeg logge inn eller lage konto?

Nei. Hopp over innloggingen i Docker Desktop. Demoen trenger verken Docker-konto, GitHub-konto eller nøkkel. Den ekte versjonen trenger en gratis bruker hos EODHD (steg 5 i den ekte versjonen).

### Hvilken Docker Desktop skal jeg velge?

Windows: den vanlige (AMD64), med mindre maskinen har en ARM-prosessor. Mac: «Apple Silicon» hvis Apple-menyen → Om denne maskinen (About This Mac) viser en M-brikke på linja Brikke (Chip), ellers «Intel».

### Hva skjer under installasjonen?

Windows: åpne fila du lastet ned, og behold valgene som er krysset av. Spør Windows om programmet får gjøre endringer, svarer du ja. Ber Windows om omstart, gjør det. Mac: åpne fila og dra Docker til Programmer (Applications). Første gang Docker Desktop starter, godtar du vilkårene, og på Mac kan det be om passordet ditt. Docker Desktop ligger så i Start-menyen (Windows) eller i Programmer (Mac).

### Installasjonen ber om administrator.

Docker Desktop må installeres av en som er administrator på maskinen. Spør den som har ansvar for maskinen, eller bruk en annen maskin.

### Docker Desktop sier at virtualisering mangler.

Virtualisering må være slått på i maskinens oppstartsinnstillinger (BIOS eller UEFI). Hvordan, er forskjellig fra maskin til maskin. Spør den som har ansvar for maskinen, eller søk på maskinmodellen og «enable virtualization».

### Docker Desktop ber om å oppdatere WSL (Windows).

Følg beskjeden, eller lim inn `wsl --update` i PowerShell og start Docker Desktop på nytt.

### Det står ikke «Engine running» etter noen minutter.

Avslutt Docker Desktop helt: høyreklikk hvalen ved klokka (Windows) eller klikk den i menylinja øverst (Mac), og velg «Quit Docker Desktop». Åpne det igjen og vent. Hjelper ikke det, starter du maskinen på nytt.

Står det «Resource Saver mode», med en måne, er alt i orden: Docker har stoppet motoren fordi ingen containere kjører, og starter den selv når den trengs, bare litt tregere. Da trenger du ikke vente på «Engine running».

## Steg 2: koden

### ZIP-fila ser ut som en vanlig mappe.

Du må pakke ut. Står det «Komprimert størrelse» (Compressed size) som kolonne og «Pakk ut alle» (Extract All) øverst i vinduet, er du inne i ZIP-fila, og den er ikke pakket ut. Trykk «Pakk ut alle», og bruk mappa som lages. På Windows finner du Nedlastinger (Downloads) i Filutforsker (File Explorer), og etter «Pakk ut alle» trykker du «Pakk ut» (Extract).

### Det er to mapper med samme navn.

Bruk den innerste `G74-lund-osen-main`, den der filene README og compose ligger. Windows viser dem ofte uten filendelsen (.md og .yaml). På Windows har også ZIP-fila samme navn: den har en glidelås på ikonet, og den skal du ikke bruke. Har du lastet ned flere ganger, kan ZIP-fila og den ytre mappa ha fått et tall i navnet, som `G74-lund-osen-main (4)`. Bruk den nyeste ytre mappa, og den innerste i den. Vil du slette de gamle, flytter du først ut en `.env` med nøkkelen din (se «Mappa finnes fra før.»).

### Jeg finner ikke ZIP-fila på Mac.

Ligger mappa `G74-lund-osen-main` allerede i Nedlastinger (Downloads), har Safari pakket den ut for deg. Bruk den.

### Jeg har fått koden fra før.

Har du fått koden som mappe eller ZIP-fil, pakker du den ut og går til steg 3.

### Mappa finnes fra før.

Vil du laste ned på nytt, og det ligger en `.env` med nøkkelen din i den gamle mappa, flytter du den ut først. Slett så den gamle mappa og pakk ut på nytt. Demodataene ligger i Docker, ikke i mappa, så de går ikke tapt. Har du hentet koden med `git clone`, går du heller inn i mappa og skriver `git pull`.

## Steg 3: terminalvinduet

### Hvilket vindu skal jeg åpne?

Et terminalvindu, der du skriver kommandoer i stedet for å klikke. Windows: gå i Filutforsker inn i den innerste mappa `G74-lund-osen-main`, klikk i adressefeltet øverst, skriv `powershell` og trykk Enter. Da åpnes PowerShell i mappa, og du slipper `cd`, men gjør kontrollen i steg 4: `dir` skal vise `README.md` og `compose.yaml`. Du kan også trykke Start, skrive `PowerShell` og åpne «Windows PowerShell», men ikke «Kjør som administrator» (Run as administrator). Fra Start-menyen står vinduet i en annen mappe, og du går til mappa med steg 4. Ikke velg «Windows PowerShell ISE», som også står i lista. Mac: trykk Cmd+mellomrom, skriv `Terminal` og trykk Enter. Når det har gått bra, ser du et vindu med en linje som venter på at du skriver. Kommandoene er de samme i PowerShell på Windows og i Terminal på Mac og Linux.

### Ingenting skjer når jeg limer inn.

Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal bare være åpent, og du skriver ingenting i det. Ledetekst (Command Prompt) på Windows virker også for demoen, men stegene er skrevet for PowerShell, og den ekte versjonen trenger PowerShell.

Kopier kommandoen med ikonet til høyre i den grå boksen i README-en. Ikonet synes først når musa er over boksen. Du kan også markere kommandoen og trykke Ctrl+C (Cmd+C på Mac), eller skrive den inn. Lim den inn i PowerShell-vinduet fra steg 4 med Ctrl+V (Cmd+V på Mac), og trykk Enter.

## Steg 4: mappa

### Hva betyr cd, og hvordan ser jeg at det gikk?

`cd` betyr «gå til mappe», og kommandoene etter steg 4 virker bare fra mappa med koden. Når det har gått bra, står `G74-lund-osen-main` rett før `>` (Windows) eller `%` (Mac) på linja som venter. Det gjør det også i den ytre mappa, så sjekk med `dir` (Windows) eller `ls` (Mac): lista skal vise `README.md` og `compose.yaml`. Viser den bare en mappe som heter `G74-lund-osen-main`, står du i den ytre: skriv `cd G74-lund-osen-main`, trykk Enter og sjekk igjen.

### Står det .zip til slutt i linja.

Du har dratt inn ZIP-fila, ikke mappa. Dra mappa du pakket ut i steg 2, ikke ZIP-fila. Står det `.zip` til slutt i linja før du har trykket Enter, trykker du Esc (Windows) eller Ctrl+U (Mac), så linja blir tom, og skriver `cd` og et mellomrom på nytt. Dra så mappa inn i vinduet. På Windows har ZIP-fila en glidelås på ikonet.

### Mappa lar seg ikke dra inn i vinduet.

PowerShell er trolig åpnet som administrator, og da sperrer Windows dra og slipp. Lukk vinduet og åpne PowerShell på vanlig måte (steg 3). Åpner du den fra adressefeltet i Filutforsker, står du alt i mappa og trenger ikke dra.

### «is not recognized as the name of a cmdlet» eller «Cannot find path … because it does not exist» etter cd.

Kommer «is not recognized as the name of a cmdlet»: Det mangler mellomrom etter `cd`. Står `cd` klistret til stien i meldingen, for eksempel `'cdC:\...'`, skriver du `cd`, et mellomrom, og drar mappa inn i vinduet på nytt (steg 4). Står det `'docker'` i meldingen, er Docker Desktop ikke installert, eller vinduet ble åpnet før installasjonen: lukk det og åpne et nytt (steg 3). Står det `'uv'` i meldingen, er uv ikke installert, eller vinduet ble åpnet før installasjonen: se «Tester» i README-en.

Kommer «Cannot find path … because it does not exist»: Mappa ligger ikke der stien sier, for eksempel fordi den er flyttet, eller fordi ZIP-fila ble dratt inn i stedet for mappa. Skriv `cd` og et mellomrom, og dra mappa inn i vinduet på nytt (steg 4). Står det `.zip` til slutt i stien i meldingen, var det ZIP-fila: se «Står det .zip til slutt i linja.» over.

### Stien har mellomrom og fikk ikke anførselstegn.

Får du en feil etter `cd` når mappa ligger i en mappe med mellomrom i navnet, skriver du anførselstegn rundt stien, for eksempel `cd "C:\Users\Ola Nordmann\Downloads\G74-lund-osen-main"`. På Mac setter Terminal `\` foran hvert mellomrom, og det virker også.

### Terminal spør om tilgang til Nedlastinger (Mac).

Svar OK. Ellers får ikke Terminal åpne mappa.

## Demoen

### Hva skal jeg se etter i vinduet?

Første gang bygger Docker appen, og det kommer mange linjer. Demoen er klar når denne linja kommer. Den skal du ikke kopiere, bare se etter:

```text
demo-1  | INFO:waitress:Serving on http://0.0.0.0:8000
```

Under den kan det komme en linje med valg fra Docker. La terminalvinduet stå åpent mens du bruker demoen. `0.0.0.0` er adressen inne i Docker, og du åpner http://127.0.0.1:8000 i steg 6 i demoen. «Serving on http://0.0.0.0:8000» betyr bare at appen kjører.

### Hva er demoen?

Sidene sier «Eksempeltall»: 15 oppdiktede selskaper med kurser til fredag 9. oktober 2026, ikke data fra Oslo Børs. Under merket står en tabell med aksjer, og du klikker på et selskapsnavn for å se aksjen. Hver aksje har en rad. Matfjord Merkevarer har ingen kurser i demoen, med vilje, og står nederst med «–» og «uten data» når tabellen ikke er sortert. Varde Systemer er nylig notert, så raden sier hvor mange dager kursserien har og hvor mange signalet trenger. Klikker du på et kolonnenavn, sorteres alle aksjene i én liste på den kolonnen, og «Standard rekkefølge» gir delene «Skilte seg ut» og «Øvrige aksjer» tilbake. Demoen trenger verken `.env` eller nøkkel, og gjør ingen kall. Aksjesiden viser KI-teksten for siste dag, laget én gang med Gemma og lagret i repoet, så demoen trenger ikke Ollama. Demobasen lages på nytt hver gang demoen starter, i sitt eget volum, `ose-demo`. Den ekte basen røres ikke. Mens demoen kjører, kan demobasen også lages på nytt med `docker compose run --rm demo-lag` i et nytt terminalvindu, fra samme mappe.

Øverst på sidene står knappene «Markedsoversikt», «Børsometer» og «Min liste», og knappen for siden du står på, er fylt. Stjernen foran et selskap legger aksjen i Min liste, og et nytt trykk tar den ut. Demoen starter med fem merket, og siden demobasen lages på nytt hver gang demoen starter, er det de samme fem neste gang. I den ekte versjonen starter lista tom, og merkingen blir liggende til du tar den bort.

Har du laget demobasen utenfor Docker før 22.10, sier sidene «Demobasen er laget av en eldre versjon av demoen». Lag den på nytt med `uv run python src/demo.py`. I Docker lages den på nytt hver gang demoen starter.

### Hva viser børsometeret?

Én rute per aksje, ordnet etter bransje. Fargen har fem trinn etter endringen fra børsdagen før, slik tallet står i ruta: grå under ±0,5 %, lys grønn eller lys rød fra 0,5 % til under 2 %, og sterk grønn eller rød med hvit tekst fra 2 %. En rute uten endring er hvit med grå kant. «Hva fargene betyr» under rutene viser trinnene og rammene. Rutene er et fylt kart: hver bransje er et felt, og arealet av ruta følger volumet mot medianen for de 20 børsdagene før, men ruta blir ikke større over tre ganger vanlig volum eller mindre under halvparten, og tabellen under har det faktiske tallet. Med Tab går du gjennom kartet fra det største feltet og den største ruta, slik kartet legger dem, mens tabellen har bransjene i fast rekkefølge. Symbolet og endringen står på ruter som er store nok, og i et bredt vindu får flere ruter plass til teksten. Rammen er tykk med en hvit linje innenfor, gul ved 3 av 3 på siste børsdag og mørk ved 2 av 3 samme dag. Ved hver bransje står navnet og snittet av endringen for aksjene i den som har kurs, eller «1 aksje» der det er én; antallet står i tabellen. Er feltet for smalt, står bare navnet, og blir det for smalt for hele navnet, kuttes det med «…». Med «Velg dag» ser du en tidligere dag. Gult står da fortsatt ved 3 av 3 på siste børsdag, også en dag uten vurdering, og mørk ramme står bare for siste børsdag. En dag uten vurdering står som «ikke vurdert», og da står fotnoten om «ikke vurdert» under tabellen. Klikk på en rute for å se aksjen den dagen. For en aksje uten kurser sier aksjesiden at det ikke finnes kurser ennå. Under rutene står de samme tallene i en tabell, bak «Se tallene som tabell». Den er lukket til du åpner den, og har bransjene i fast rekkefølge. Linja «Mål mot børsen» over rutene sier hva fargen og størrelsen måler, og endringen i hovedindeksen den dagen, eller «–» når indeksen ikke har den. Søylene står bare på oversikten. Det gjelder både demoen og den ekte versjonen.

### Hva sa appen om en aksje tidligere?

Nederst på aksjesiden står «Signalet dag for dag»: det appen skrev om aksjen hver børsdag, en måned om gangen, med retningen, T, B, I og styrken. Pilene viser måneden før og etter, så langt kursserien går. Klikk på en dag med kurs for å se hele siden for den dagen, med målingene. En dag uten vurdering står med «–» og grunnen, og dagene før første og etter siste kurs står tomme. Det gjelder både demoen og den ekte versjonen. Den ekte versjonen har signal fra første henting, og dagene før står som «ikke vurdert». Demoen viser det samme: vurderingene starter mandag 21. september 2026, tre uker før siste demodag, og dagene før står som «ikke vurdert».

### Hvorfor står det «ikke vurdert»?

Står «ikke vurdert» på oversikten, aksjesiden eller børsometeret, sier en fotnote hvorfor. I den ekte versjonen lagres signalet bare den kvelden kursene hentes, og regnes aldri ut bakover. Det gjelder dagene før første henting, kvelder uten henting, og dager der kursene er lest inn med `--les-inn`. Er dagen siste børsdag, også når siden leses i helga eller på en helligdag, sier fotnoten i tillegg at signalet for den dagen fortsatt kan lagres hvis hentingen kjøres ferdig før neste børsdag. I demoen sier fotnoten for en dag før 21.09 at vurderingene starter mandag 21.09, slik den ekte versjonen har signal fra første henting. En dag fra 21.09 uten vurdering får den ekte teksten, også i demoen.

## Den ekte versjonen

### Hva med nøkkelen?

Du trenger en egen gratis API-nøkkel fra [EODHD](https://eodhd.com/register), fordi vilkårene ikke lar oss dele vår. Den gir 20 kall i døgnet, og en henting bruker 16: ett per aksje og ett for hovedindeksen. Åpne `.env` i en teksteditor (`notepad .env` på Windows, `open -e .env` på macOS, `nano .env` på Linux) og lim den inn etter `EODHD_API_KEY=`. `cp` skriver over en `.env` som finnes, så kopier bare første gang. Webserveren starter uten `.env`, henter aldri og bruker aldri kvote. Den skriver bare én ting i basen, merkingen i Min liste, når du trykker på stjernen. Bare hentingen trenger nøkkelen, og `docker compose run --rm hent` starter ikke uten `.env`.

### Hvorfor bare 15 aksjer?

Kursene kommer fra EODHD, og den gratis nøkkelen gir 20 kall i døgnet. Hver aksje koster ett kall, og hovedindeksen ett til, så med 15 aksjer er det kall til overs hvis noe må hentes på nytt. Planen er at du senere kan velge opptil 18 aksjer selv.

### Når kan jeg hente?

Hent etter kl. 22 og før midnatt på en børsdag. Første gang, når basen er tom, kan du også hente på dagtid og i helgen: da henter den siste fullførte børsdag, før kl. 22 en børsdag altså forrige børsdag, og aldri dagens kurs. Signalet lagres fra første henting og regnes aldri bakover, så «Signalet dag for dag» fylles én børsdag om gangen. Første henting på dagtid bruker normalt 16 av dagens 20 kall, så det er ingen kall igjen til nye forsøk samme kveld, og den bruker aldri bonuskvoten. Kveldens henting samme dag trenger 16 til: har kontoen minst 12 i bonuskvoten, tas de derfra, og dagen får signal. Ellers bruker den 0 kall, og den dagen får aldri signal, fordi en vurdering bare kan skrives for inneværende børsdag. Neste kveld hentes neste børsdag. Før kl. 22 en børsdag stopper hentingen med 0 kall og sier hvorfor når basen ikke er tom: dagens sluttkurs er ikke klar ennå, og en vurdering kan ikke fylles inn senere. Har basen alt kursene for børsdagen, bruker den også 0 kall. På en dag børsen er stengt henter den bare hvis basen mangler forrige børsdag. Mangler noen aksjer dagens kurs etter hentingen, sier den hvilke. Kjør samme kommando igjen senere samme kveld, så prøver den bare dem, med kallene som er til overs etter hentingen (20 minus ett per aksje og ett for hovedindeksen, altså 4 med de 15), aldri bonuskvoten og ikke etter kl. 23:50. Hovedindeksen prøves ikke på nytt samme kveld. Før kallene leser den kvoten med `/api/user`, som er gratis.

### Kan hentingen gå av seg selv hver kveld?

Ja, på Windows, med en jobb i Oppgaveplanlegging. Den går hver dag kl. 22:15, og igjen kl. 22:45, 23:15 og 23:45, fra en egen arbeidskopi på commiten main hadde ved midnatt, og henter uten KI-tekst hvis Docker Desktop eller Ollama ikke svarer. Loggen står i `data/logg/kveldshenting-<dato>.log`. Slik slås den på og av, med `start\legg-inn-kveldshentingen.ps1` og `start\ta-bort-kveldshentingen.ps1`: [Hentingen hver kveld](../README.md#hentingen-hver-kveld) i README-en. Slå den av før du henter for hånd samme kveld, eller vent til den er ferdig, så to hentinger ikke går samtidig.

### Oversikten er tom.

Uten henting starter appen med tom oversikt og viser kommandoen som henter. Hent kursene med steg 8 i den ekte versjonen, og last siden på nytt. Utskriften fra hentingen sier hvilken børsdag vurderingene gjelder, og hvilke aksjer som fikk en grunn i stedet for en vurdering.

### Hvor ligger dataene?

Dataene ligger i to Docker-volumer: `ose-db` med basen og `ose-raa` med øyeblikksbildene fra EODHD. De står når containerne stoppes. **Bruk aldri `docker compose down -v`.** `-v` fjerner begge volumene, og verken øyeblikksbildene eller vurderingene kan hentes på nytt. Basen kan heller ikke slettes og bygges opp igjen: kursene kan hentes på nytt, men vurderingene for dagene som har gått, kan ikke lages på nytt.

### Kan appen nås fra nettet?

Nei. Porten er bare åpen på maskinen selv (127.0.0.1). Appen kan ikke nås fra nettet.

### Hvor finner jeg børsmeldingene?

Appen viser ikke børsmeldingene. De står på NewsWeb og ofte også på selskapets investorside. Under kursgrafen på aksjesiden står en lenke til investorsiden for aksjen siden viser. Appen henter ingenting derfra. I demoen er selskapene oppdiktet og har ingen investorside, så der står det i stedet at lenken står der i den ekte versjonen.

### Kan KI-teksten lages uten grafikkort?

Ja, med din egen nøkkel til Gemini, Anthropic eller OpenAI. Sett `OSE_KI_TJENESTE=gemini`, `anthropic` eller `openai` i `.env`, og lim inn nøkkelen etter `OSE_KI_GEMINI_NOKKEL=`, `OSE_KI_ANTHROPIC_NOKKEL=` eller `OSE_KI_OPENAI_NOKKEL=`. Da sendes grunnlaget for hver aksje til tjenesten du har valgt, og det kan koste hos dem. Del aldri nøkkelen, og bruk ikke en konto der du har sagt ja til at tjenesten trener på innholdet. Mangler nøkkelen, eller har den tegn som ikke kan sendes, skrives ingen rader, og utskriften sier hvilken variabel det gjelder: legg den inn og hent igjen samme kveld, før midnatt. Feiler tjenesten, for eksempel fordi nøkkelen er feil, blir det ingen KI-tekst for noen av aksjene den dagen, heller ikke om du retter det og henter igjen samme kveld. Hentingen går ikke over til en annen tjeneste. Mer står under «Egen nøkkel til Gemini, Anthropic eller OpenAI» i [README-en](../README.md).

## Når appen kjører, eller ikke

### Siden åpnes ikke.

Vent til linja med «Serving on» har kommet, og sjekk at terminalvinduet fortsatt er åpent. Adressen er http://127.0.0.1:8000, ikke 0.0.0.0.

### Nettleseren sier at 127.0.0.1 nektet å koble til.

Nettleseren viser da `ERR_CONNECTION_REFUSED`. Andre nettlesere sier det med andre ord. Ingenting svarer på adressen ennå. Appen er ikke klar, eller den er stoppet. Se i terminalvinduet: vent til linja med «Serving on» har kommet, og sjekk at vinduet fortsatt er åpent og at Docker Desktop kjører. Last så siden på nytt. Adressen er http://127.0.0.1:8000, ikke 0.0.0.0.

### «The term 'uv' is not recognized» eller «command not found: uv».

Blir `uv` ikke funnet etter installasjonen, lukker du vinduet, åpner et nytt og går til mappa, som i steg 4. Er uv ikke installert, står installasjonen for Windows og Mac under «Tester» i [README-en](../README.md#tester).

### «docker» er ikke gjenkjent, eller «command not found: docker».

Docker Desktop er ikke installert, eller terminalvinduet ble åpnet før installasjonen. Lukk terminalvinduet og åpne et nytt (steg 3).

### «Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».

Docker Desktop er ikke startet, eller motoren er ikke klar. Start Docker Desktop, vent til det står «Engine running» (steg 1), og prøv kommandoen igjen.

### To kommandoer havnet på samme linje.

For eksempel med feilen «no such service». Lim inn én kommando om gangen, og trykk Enter etter hver. Står det noe på linja fra før, sletter du det først.

### «no configuration file provided: not found».

Terminalvinduet står i feil mappe. Gjør steg 4 på nytt, og dra den mappa der fila compose ligger. Windows viser den uten filendelsen, som compose og ikke compose.yaml.

### «toomanyrequests» fra Docker Hub.

Docker Hub begrenser hvor ofte samme IP-adresse kan laste ned uten innlogging. Prøv igjen senere, eller fra et annet nett. Innlogging i Docker Desktop hever grensen, men trengs ellers ikke.

### «port is already allocated», «address already in use» eller «ports are not available».

Noe annet bruker port 8000. Kjører den andre versjonen, stopper du den først (se «Bytte mellom demoen og den ekte versjonen» under «Mer for den som vil»). «Mer for den som vil» står i [README-en](../README.md).

## Stopp

### Jeg lukket vinduet før jeg stoppet.

Åpne et nytt terminalvindu, gjør steg 4 og lim inn stoppkommandoen for versjonen du kjørte: `docker compose down` for den ekte versjonen, eller `docker compose --profile demo down` for demoen.

## Neste gang

### Hvordan starter jeg neste gang?

Med dobbeltklikket: dobbeltklikk «Start demoen» eller «Start den ekte versjonen» i mappa igjen. Den ekte versjonen henter det som mangler før appen starter.

Med Docker: start Docker Desktop fra Start-menyen (Windows) eller Programmer (Mac), og vent til det står «Engine running». Gjør så steg 3 og 4, og hopp over steg 2. Start så appen med steg 7 i den ekte versjonen, og hent kursene med steg 8 om kvelden, eller start demoen med steg 5 i demoen. Det går raskere enn første gang. Etter «Stopp» kan du lukke terminalvinduet og Docker Desktop.
