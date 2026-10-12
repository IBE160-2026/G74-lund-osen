---
title: "Hjelp til «Kom i gang»"
status: aktiv
created: 2026-10-11
updated: 2026-10-12T10:26
---

# Hjelp til «Kom i gang»

Spørsmål og svar til «Kom i gang» i [README-en](../README.md), sortert etter steget de hører til. De vanligste står også i README-en, under «Står du fast?». Stegene 1–4 er felles for begge versjonene.

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

## Steg 2: koden

### ZIP-fila ser ut som en vanlig mappe.

Du må pakke ut. Står det «Komprimert størrelse» (Compressed size) som kolonne og «Pakk ut alle» (Extract All) øverst i vinduet, er du inne i ZIP-fila, og den er ikke pakket ut. Trykk «Pakk ut alle», og bruk mappa som lages. På Windows finner du Nedlastinger (Downloads) i Filutforsker (File Explorer), og etter «Pakk ut alle» trykker du «Pakk ut» (Extract).

### Det er to mapper med samme navn.

Bruk den innerste `G74-lund-osen-main`, den der filene README og compose ligger. Windows viser dem ofte uten filendelsen (.md og .yaml). På Windows har også ZIP-fila samme navn: den har en glidelås på ikonet, og den skal du ikke bruke.

### Jeg finner ikke ZIP-fila på Mac.

Ligger mappa `G74-lund-osen-main` allerede i Nedlastinger (Downloads), har Safari pakket den ut for deg. Bruk den.

### Jeg har fått koden fra før.

Har du fått koden som mappe eller ZIP-fil, pakker du den ut og går til steg 3.

### Mappa finnes fra før.

Vil du laste ned på nytt, og det ligger en `.env` med nøkkelen din i den gamle mappa, flytter du den ut først. Slett så den gamle mappa og pakk ut på nytt. Demodataene ligger i Docker, ikke i mappa, så de går ikke tapt. Har du hentet koden med `git clone`, går du heller inn i mappa og skriver `git pull`.

## Steg 3: terminalvinduet

### Hvilket vindu skal jeg åpne?

Et terminalvindu, der du skriver kommandoer i stedet for å klikke. Windows: trykk Start, skriv `PowerShell` og åpne «Windows PowerShell». Ikke velg «Windows PowerShell ISE», som også står i lista. Mac: trykk Cmd+mellomrom, skriv `Terminal` og trykk Enter. Når det har gått bra, ser du et vindu med en linje som venter på at du skriver. Kommandoene er de samme i PowerShell på Windows og i Terminal på Mac og Linux.

### Ingenting skjer når jeg limer inn.

Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal bare være åpent, og du skriver ingenting i det. Ledetekst (Command Prompt) på Windows virker også for demoen, men stegene er skrevet for PowerShell, og den ekte versjonen trenger PowerShell.

## Steg 4: mappa

### Hva betyr cd, og hvordan ser jeg at det gikk?

`cd` betyr «gå til mappe», og kommandoene etter steg 4 virker bare fra mappa med koden. Når det har gått bra, står `G74-lund-osen-main` rett før `>` (Windows) eller `%` (Mac) på linja som venter.

### Mappa lar seg ikke dra inn i vinduet.

PowerShell er trolig åpnet som administrator, og da sperrer Windows dra og slipp. Lukk vinduet og åpne PowerShell på vanlig måte (steg 3).

### Stien har mellomrom og fikk ikke anførselstegn.

Får du en feil etter `cd` når mappa ligger i en mappe med mellomrom i navnet, skriver du anførselstegn rundt stien, for eksempel `cd "C:\Users\Ola Nordmann\Downloads\G74-lund-osen-main"`. På Mac setter Terminal `\` foran hvert mellomrom, og det virker også.

### Terminal spør om tilgang til Nedlastinger (Mac).

Svar OK. Ellers får ikke Terminal åpne mappa.

## Den ekte versjonen

### Hva med nøkkelen?

Du trenger en egen gratis API-nøkkel fra [EODHD](https://eodhd.com/register), fordi vilkårene ikke lar oss dele vår. Den gir 20 kall i døgnet, og en henting bruker 15. Åpne `.env` i en teksteditor (`notepad .env` på Windows, `open -e .env` på macOS, `nano .env` på Linux) og lim den inn etter `EODHD_API_KEY=`. `cp` skriver over en `.env` som finnes, så kopier bare første gang. Webserveren starter uten `.env` og bruker aldri kvote: den leser bare fra basen. Bare hentingen trenger nøkkelen, og `docker compose run --rm hent` starter ikke uten `.env`.

### Hvorfor bare 15 aksjer?

Kursene kommer fra EODHD, og den gratis nøkkelen gir 20 kall i døgnet. Hver aksje koster ett kall, så med 15 aksjer er det kall til overs hvis noe må hentes på nytt. Planen er at du senere kan velge opptil 18 aksjer selv.

### Når kan jeg hente?

Hent etter kl. 22 og før midnatt på en børsdag. Første gang kan du også hente i helgen: da henter den siste børsdag, fordi basen mangler den. På dagtid en børsdag stopper hentingen med 0 kall og sier hvorfor: dagens sluttkurs er ikke klar ennå, og en vurdering kan ikke fylles inn senere. Har basen alt kursene for børsdagen, bruker den også 0 kall. På en dag børsen er stengt henter den bare hvis basen mangler forrige børsdag og fila for den dagen ikke finnes. Før kallene leser den kvoten med `/api/user`, som er gratis.

### Oversikten er tom.

Uten henting starter appen med tom oversikt og viser kommandoen som henter. Hent kursene med steg 8 i den ekte versjonen, og last siden på nytt. Utskriften fra hentingen sier hvilken børsdag vurderingene gjelder, og hvilke aksjer som fikk en grunn i stedet for en vurdering.

### Hvor ligger dataene?

Dataene ligger i to Docker-volumer: `ose-db` med basen og `ose-raa` med øyeblikksbildene fra EODHD. De står når containerne stoppes. **Bruk aldri `docker compose down -v`.** `-v` fjerner begge volumene, og verken øyeblikksbildene eller vurderingene kan hentes på nytt. Basen kan heller ikke slettes og bygges opp igjen: kursene kan hentes på nytt, men vurderingene for dagene som har gått, kan ikke lages på nytt.

### Kan appen nås fra nettet?

Nei. Porten er bare åpen på maskinen selv (127.0.0.1). Appen kan ikke nås fra nettet.

## Demoen

### Hva skal jeg se etter i vinduet?

Første gang bygger Docker appen, og det kommer mange linjer. Demoen er klar når denne linja kommer. Den skal du ikke kopiere, bare se etter:

```text
demo-1  | INFO:waitress:Serving on http://0.0.0.0:5000
```

Under den kan det komme en linje med valg fra Docker. La terminalvinduet stå åpent mens du bruker demoen. `0.0.0.0` er adressen inne i Docker, og du åpner http://127.0.0.1:5000 i steg 6 i demoen.

### Hva er demoen?

Sidene sier «Eksempeltall»: 15 oppdiktede selskaper med kurser til fredag 9. oktober 2026, ikke data fra Oslo Børs. Under merket står en tabell med aksjer, og du klikker på et selskapsnavn for å se aksjen. Demoen trenger verken `.env` eller nøkkel, og gjør ingen kall. Demobasen lages på nytt hver gang demoen starter, i sitt eget volum, `ose-demo`. Den ekte basen røres ikke. Mens demoen kjører, kan demobasen også lages på nytt med `docker compose run --rm demo-lag` i et nytt terminalvindu, fra samme mappe.

## Når appen kjører, eller ikke

### Siden åpnes ikke.

Vent til linja med «Serving on» har kommet, og sjekk at terminalvinduet fortsatt er åpent. Adressen er http://127.0.0.1:5000, ikke 0.0.0.0.

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

Noe annet bruker port 5000. Kjører den andre versjonen, stopper du den først (se «Bytte mellom demoen og den ekte versjonen» under «Mer for den som vil»). På Mac bruker AirPlay-mottakeren (AirPlay Receiver) port 5000. Slå den av under Systeminnstillinger (System Settings) → Generelt (General) → AirDrop og Handoff (AirDrop & Handoff), og prøv igjen. «Mer for den som vil» står i [README-en](../README.md).

## Stopp

### Jeg lukket vinduet før jeg stoppet.

Åpne et nytt terminalvindu, gjør steg 4 og lim inn stoppkommandoen for versjonen du kjørte: `docker compose down` for den ekte versjonen, eller `docker compose --profile demo down` for demoen.

## Neste gang

### Hvordan starter jeg neste gang?

Start Docker Desktop fra Start-menyen (Windows) eller Programmer (Mac), og vent til det står «Engine running». Gjør så steg 3 og 4, og hopp over steg 2. Start så appen med steg 7 i den ekte versjonen, og hent kursene med steg 8 om kvelden, eller start demoen med steg 5 i demoen. Det går raskere enn første gang. Etter «Stopp» kan du lukke terminalvinduet og Docker Desktop.
