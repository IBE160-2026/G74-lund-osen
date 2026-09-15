# Refleksjonslogg – IBE160 Programmering med KI

Denne loggen brukes underveis i prosjektet slik at vi har dokumentasjon til refleksjonsrapporten.
Før kort logg etter hver arbeidsøkt. Det viktigste er å dokumentere hvem som gjorde hva, hvordan KI ble brukt,
hvilke problemer som oppstod, hvilke valg vi tok, og hva vi lærte.

## Fast mal for hver arbeidsøkt

### Dato:
### Deltaker(e):
### Fase:
Planlegging / utvikling / testing / feilretting / dokumentasjon / annet

### Oppgave
Kort beskrivelse av hva vi jobbet med.

### Hva gjorde vi?
- 
- 
- 

### KI-verktøy brukt
Claude Code / ChatGPT / Codex / annet

### Viktige prompts
Skriv en kort oppsummering her og legg eventuelt hele prompten i `docs/ai-prompts/`.

### Hva foreslo KI?
- 

### Hva valgte vi å bruke eller endre selv?
- 

### Problemer eller feil
- 

### Hvordan ble problemet løst?
- 

### Hva lærte vi?
- 

### Git / dokumentasjon
Commit eller fil(er), hvis relevant:
- 

---

## 15.09.2026 – Marian

### Deltaker(e)
Marian

### Fase
Oppsett av utviklingsmiljø og prosjekt

### Oppgave
Gjøre PC og GitHub-repository klart for IBE160-prosjektet og installere BMAD.

### Hva gjorde vi?
- Installerte og kontrollerte Git.
- Installerte og kontrollerte VS Code og nødvendige utvidelser.
- Installerte Node.js LTS og npm.
- Installerte uv og Python 3.12.
- Installerte Docker Desktop og WSL2.
- Testet Docker med `docker run hello-world`.
- Installerte og logget inn i Claude Code.
- Installerte GitHub CLI og logget inn på kurskontoen.
- Klonet repositoryet `IBE160-2026/G74-lund-osen`.
- Konfigurerte Git med Marian sin egen Git-identitet.
- Installerte BMAD i prosjektet.
- Valgte BMad Method og BMad Creative Intelligence Suite.
- Valgte Claude Code og Codex som integrasjoner.
- Satte BMAD til norsk chat og norsk dokumentutdata.
- Satte BMAD-navn til `Lund og Osen`.
- Brukte `_bmad-output` som standard mappe for BMAD-dokumenter.

### KI-verktøy brukt
ChatGPT ble brukt som stegvis veiledning under installasjonen og oppsettet.
Claude Code ble installert og testet for senere bruk i prosjektet.

### Viktige prompts
Veiledningen bestod hovedsakelig av spørsmål om hvilke programmer som skulle installeres, hvilke valg som skulle tas,
og kontroll av feilmeldinger og installasjonsresultater.

### Hva foreslo KI?
- Rekkefølge for installasjon.
- Hvordan rette npm-problemet i PowerShell.
- Hvordan aktivere WSL2 slik at Docker kunne starte.
- Hvordan autentisere Claude Code og GitHub CLI.
- Hvordan installere og konfigurere BMAD i riktig repository.

### Hva valgte vi å bruke eller endre selv?
- Vi valgte norsk som samtale- og dokumentutdataspråk i BMAD.
- Vi valgte gruppenavnet `Lund og Osen`.
- Vi valgte både Claude Code og Codex som BMAD-integrasjoner.
- Vi valgte Creative Intelligence Suite som ekstra BMAD-modul.

### Problemer eller feil
- npm ble først blokkert av PowerShell sin policy for scripts.
- Docker kunne først ikke starte fordi virtualiseringsstøtte via WSL2 ikke var klar.
- Claude Code-innloggingen krevde korrekt autentiseringsflyt og kode.
- Første forsøk på å lime autentiseringskode ble tolket som en PowerShell-kommando.

### Hvordan ble problemet løst?
- Node.js LTS ble installert på nytt, og npm fungerte etterpå.
- WSL2 ble installert/aktivert, og Docker ble testet med `hello-world`.
- Claude Code ble autentisert på nytt gjennom nettleser og terminal.
- GitHub CLI ble autentisert med nettleser.

### Hva lærte vi?
- Forskjellen mellom lokal programvare, prosjektfiler og GitHub-repository.
- At BMAD installeres per repository og ikke som et vanlig globalt program.
- Hvordan Git brukes til å dokumentere og dele prosjektendringer.
- Hvordan Docker, WSL2, Claude Code, BMAD og GitHub henger sammen i utviklingsmiljøet.

### Git / dokumentasjon
BMAD-oppsettet legges inn i Git og pushes til kursrepositoryet slik at begge gruppemedlemmene bruker samme prosjektoppsett.

---
