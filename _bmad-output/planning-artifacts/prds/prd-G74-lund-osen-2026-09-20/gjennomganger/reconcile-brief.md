# Avstemming: Product Brief mot PRD

**Dato:** 2026-09-20
**Kilde:** `_bmad-output/planning-artifacts/product-brief.md`
**Avstemt mot:** `prd.md`, `malinger.md`
**Kjente avvik holdt utenfor:** `korreksjon-til-brief.md`

## Metode

Hver setning i briefen som bærer et **krav**, et **tall**, et **forbehold** eller
en **beslutning** er sjekket mot PRD-en og vedlegget. Setninger som bare bærer
innramming eller gjentakelse er ikke listet. Kontrollen leter primært etter
innhold som er *borte*, ikke etter formuleringer som halter — prosjektet har
mistet seks substansielle detaljer i tidligere omskrivinger (se
`korreksjon-til-brief.md`, «Mønsteret»), og dette er den sjuende kontrollen av
samme type.

De to korreksjonene som allerede er dokumentert — rentejusteringseksempelet i
*The Problem* og det gjenopprettede kravet om dager uten tydelige signaler — er
**ikke** rapportert som funn her. De står som kjente avvik i del D.

---

## A. Utelatelser — innhold i kilden som ikke gjenfinnes

### A1. Shippingselskapet i medietesten 17.09 — motprøven er borte

**Alvorlighet: høy.**

Briefen, *The Problem*, linje 18:

> I vår egen test 17.09 leste vi manuelt de ti siste nyhetstreffene for et
> utvalg selskaper. For et stort finansselskap handlet flertallet i realiteten
> om andre selskaper; det var bare ett av mange symboler i artikkelen.
> **For et shippingselskap var bildet motsatt.**

PRD-en gjengir testen i seksjon 4.3, punkt 1, men bare halvparten av den:
finansselskapet er med, shippingselskapet er strøket. Det samme gjelder
`malinger.md` — testen har ingen seksjon der i det hele tatt.

Dette er ikke en illustrasjon som kan strykes. Motprøven er selve funnet:
symbolstøy er **ikke en konstant egenskap ved symbolmatching, den varierer med
selskapet**. Med bare finansselskapet igjen leser PRD-en som om symbolmatching
er jevnt dårlig. Med begge halvdelene sier målingen noe skarpere — at et
uniformt tiltak ikke vil virke, og at relevans må avgjøres per sak.

Konsekvensen treffer relevanseksperimentet direkte: et testsett på 50
medieartikler som ikke er sammensatt slik at begge mønstrene er representert,
kan gi et resultat som er en artefakt av utvalget. Briefen bærer den
opplysningen som trengs for å unngå det. PRD-en gjør det ikke.

**Forslag:** før setningen tilbake i PRD seksjon 4.3 punkt 1, og legg testen
inn som egen seksjon i `malinger.md` med metode, selskapsutvalg og
rådatareferanse på linje med de øvrige målingene.

### A2. Medietesten 17.09 mangler helt i `malinger.md`

**Alvorlighet: høy.**

`malinger.md` åpner med at den inneholder «alle tall PRD-en bygger på, med
metode og dato, slik at de kan etterprøves eller kjøres på nytt». Medietesten
17.09 er den ene av tre målinger som bærer begrunnelsen for KI-laget (PRD
seksjon 4.3, punkt 1), og den eneste av de tre som ikke har noen oppføring i
vedlegget:

| Måling | Ført i `malinger.md` |
|---|---|
| Symbolkoblingen i medier, 17.09.2026 | **Nei — mangler helt** |
| Samlekategorien i NewsWeb, 20.09.2026 | Ja, seksjon 4 |
| Tilbakekjøpskategorien, 20.09.2026 | Ja, seksjon 4 |

Det som ikke finnes noe sted: hvilke selskaper som inngikk, hvilken kilde
nyhetstreffene kom fra, hvordan «handler om selskapet» ble avgjort manuelt, og
en rådatareferanse. Målingen styrer to ting nedstrøms — usikkerhetskriteriene i
FR-603 og utformingen av relevanseksperimentet — og kan i dag ikke etterprøves
eller kjøres på nytt.

### A3. Personvern og finansregelverk som åpne forpliktelser

**Alvorlighet: middels.**

Briefen, *Vision*, linje 85:

> En kommersiell versjon vil kreve egne vurderinger av videreformidlingsrett,
> **personvern og regelverket som gjelder når en tjeneste presenterer
> finansielle signaler**.

PRD-en seksjon 2 fører bare den første av de tre videre:

> Vurderingen av videreformidlingsrett er utsatt til en eventuell kommersiell
> versjon, fordi v1 kjøres lokalt i undervisningssammenheng og ikke publiseres.

Personvern og verdipapirregelverket er falt ut. Begrunnelsen PRD-en gir —
lokal kjøring, ingen publisering — dekker faktisk alle tre, så utelatelsen
endrer ingen beslutning i v1. Men den fjerner to av tre punkter fra listen over
hva en kommersiell versjon må avklare, og det er nettopp den typen tap som er
dokumentert seks ganger før i dette prosjektet. Finansregelverket henger dessuten
sammen med NFR-06: grunnen til at løsningen ikke skal formuleres som en
anbefaling, er ikke bare redelighet, det er også regelverket.

**Forslag:** utvid setningen i seksjon 2 til å nevne alle tre.

### A4. «Ingen teknisk fordel» som eksplisitt forbehold

**Alvorlighet: middels-lav.**

Briefen, *What Makes This Different*, linje 44:

> Vi har ingen teknisk fordel andre ikke kan kopiere, og skal ikke påstå at vi
> har det. Datakildene er åpne eller kommersielt tilgjengelige for alle.

Formuleringen er et **«skal ikke»** — den hører til samme familie som motmålene
i PRD seksjon 7 og som NFR-06. PRD-en har beholdt «Vi lover ikke bedre signaler
enn andre» (seksjon 1 og 4.4), som er den beslektede påstanden, men ikke denne.
I en refleksjonsrapport der gruppen skal gjøre rede for hva løsningen faktisk
er, er dette en av de mer verdifulle setningene i briefen.

**Forslag:** ta den inn som et motmål i seksjon 7, eller i seksjon 1 sammen med
«Vi lover ikke bedre signaler enn andre».

### A5. Form faktor: «webapplikasjon for PC»

**Alvorlighet: middels-lav.**

Briefen, *Executive Summary*, linje 8: «OSE Signal er en norsk **webapplikasjon
for PC**». PRD-en fastslår at v1 er på norsk, kjører lokalt og ikke publiseres
(seksjon 2), og at mobiltilpasning er utenfor v1 — men sier ingen steder at
løsningen er en webapplikasjon, eller at målflaten er PC.

«Utenfor v1: mobiltilpasning» dekker PC-delen indirekte. At det er *web* og ikke
et skrivebordsprogram eller et notebook-grensesnitt, står ikke noe sted, og
PRD-en skal etter sin egen innledning inneholde «beslutningene som må være låst
før arkitekturarbeidet starter». Dette er en slik beslutning.

**Forslag:** én setning i seksjon 2: v1 er en webapplikasjon som kjøres lokalt
på PC.

### A6. «Uten å kreve opplæring»

**Alvorlighet: lav — regnes som dekket.**

Briefen, sammenligningstabellen linje 49: profesjonelle verktøy dekker alt, mens
vår løsning «dekker det en sparer faktisk bruker, **uten å kreve opplæring**».

Dette er det eneste stedet briefen stiller et brukbarhetskrav uavhengig av
femminuttersmålet. PRD-en har femminuttersmålet (suksessmålet «Brukerutfall»:
under 5 minutter, **uten hjelp**), som dekker det samme i praksis. Noteres for
fullstendighet.

### A7. «Vi har ikke gjennomført en brukerundersøkelse»

**Alvorlighet: lav.**

Briefen, linje 58, er eksplisitt på at grunnlaget ikke er en brukerundersøkelse,
og at dokumentet derfor ikke bygger på antakelser om et bredere marked. PRD-en
har ingen tilsvarende avgrensning. Forbeholdet er formulert om briefen som
dokument, så det overføres ikke direkte — men det forklarer hvorfor målet
«Brukerutfall» stopper på **én** person utenfor gruppen, som ellers kan se ut
som en vilkårlig lav terskel.

### A8. «Prioriterer stabilitet fremfor mange funksjoner»

**Alvorlighet: lav — regnes som dekket.**

Briefen linje 12. PRD-en uttrykker samme prioritering strukturelt gjennom «Hvis
vi rekker» (seksjon 2), NFR-03 og NFR-04, men ikke som uttalt prinsipp. Ingen
beslutning går tapt.

### A9. «Fastsettes endelig i PRD **og sprintplan**»

**Alvorlighet: lav.**

Briefen linje 71 sier at ukenumrene fastsettes endelig i PRD *og sprintplan*.
PRD seksjon 7 gjengir bare «i PRD» og omregner selv alle ukenumre til datoer.
Det er en tilstramming som er riktig i praksis, men den lukker en dør briefen
holdt åpen — og siden prosjektinnleveringsdatoen fortsatt er uavklart (åpent
punkt 8), er det sprintplanen som må ta den.

---

## B. Motsetninger og avvik som ikke er forklart

### B1. FR-705 innfører en driftsbeslutning som strider mot PRD-ens egne tall

**Alvorlighet: høy. Dette er det viktigste funnet i avstemmingen.**

FR-705, siste avsnitt:

> Terskelen har en driftskonsekvens utover visningen: nyheter hentes og
> KI-vurderes bare for selskapene som skiller seg ut (se 4.1). Terskelen styrer
> derfor hvor mye arbeid KI-laget får.

Dette står i strid med fire andre steder i PRD-en og med briefen:

1. **Kryssreferansen peker på noe som ikke finnes.** Seksjon 4.1 (FR-401 til
   FR-407) sier ingen steder at meldingshenting begrenses til utvalgte
   selskaper. FR-401 sier «kurser først, deretter meldinger», uten forbehold.
2. **FR-404 sier det motsatte.** Etterfylling skal dekke *alle* kalenderdager i
   hullet, og måleoppsettet i seksjon 4.2 henter for alle 15 selskapene.
3. **Volumtallene i seksjon 4.2 er regnet på alle 15.** «~35 til KI-forklaring»
   og «~13 til KI-relevansvurdering» er avledet av 121 meldinger for hele
   universet. Hentes nyheter bare for de i snitt 5,4 selskapene som passerer
   terskel 2, er begge tallene for høye — og da er heller ikke dimensjoneringen
   av KI-laget riktig.
4. **FR-203 forutsetter at meldinger finnes for enhver aksje brukeren åpner.**
   Aksjedetaljen skal vise «børsmeldinger som passerte filteret». Med FR-705
   slik den står, vil aksjedetaljen for en aksje med signalstyrke 0 eller 1 være
   tom for meldinger — også når selskapet faktisk har publisert noe. Briefen
   lover det motsatte (linje 30): aksjedetaljen svarer på hvorfor, med
   «relevante børsmeldinger med lenke til originalen».

Avviket er ikke forklart noe sted. Det kan ikke begrunnes med kvote heller —
PRD-en slår selv fast at NewsWeb ikke koster EODHD-kall (seksjon 3, FR-404,
seksjon 6), så det er ingen kvotegrunn til å begrense *hentingen*. Den eneste
reelle begrensningen er antall KI-kall, og det er en annen beslutning enn
henting.

**Må avklares.** Enten strykes koblingen fra FR-705, eller så skrives den inn
som et eget krav i 4.1, med konsekvensene for FR-203 uttrykt og volumtallene i
4.2 regnet om.

### B2. «Før demonstrasjon» er blitt «uke 45 (fra 2026-11-02)»

**Alvorlighet: middels.**

| | Brief | PRD |
|---|---|---|
| KI-bidrag i drift, frist | Før demonstrasjon (est. uke 45) | Uke 45 (fra 2026-11-02) |

PRD seksjon 7 sier at ukenumrene er «omregnet til datoer», og det er riktig for
relevanseksperimentet (est. uke 41 → uke 41, fra 2026-10-05). Men for
KI-bidraget var briefens frist ikke uke 45 — den var **før demonstrasjonen**,
med uke 45 som estimat på når demonstrasjonen faller. PRD-en gjør estimatet til
fristen, og «fra 2026-11-02» peker på *starten* av uka. Ligger demonstrasjonen
tidlig i uke 45, er fristen nå etter det den skulle sikre.

Samme uklarhet treffer FR-407 («Kravet må være oppfylt før demonstrasjonen») og
FR-601 (bryteren skal kunne vises fram «mens noen ser på»). Tre krav er bundet
til en demonstrasjonsdato som ikke er fastsatt noe sted, mens åpent punkt 8 bare
nevner prosjektinnleveringsdatoen.

**Forslag:** utvid åpent punkt 8 til å omfatte demonstrasjonsdatoen, og sett
fristen for KI-bidraget til «før demonstrasjonen» slik briefen har den.

### B3. «Fortsatt bruk» har mistet vinduet sitt i terskelkolonnen

**Alvorlighet: lav.**

Brief: «Brukt minst tre dager i uka de to siste ukene **før prosjektinnlevering**,
loggført». PRD: «Minst tre dager i uka de to siste ukene, loggført», med
«Ved prosjektinnlevering» i fristkolonnen.

Fristkolonnen redder innholdet, men terskelen alene er nå tvetydig — de to siste
ukene før hva? Målet skiller seg fra «Adopsjon» nettopp ved at vinduet ligger
etter at utviklingen er ferdig. Sett «før prosjektinnlevering» tilbake i
terskelen.

### B4. Radnavn endret fra «Kvalitet» til «Drift»

**Alvorlighet: ingen — notert for sporbarhet.** Suksessmålet er ellers ordrett
likt, og ingen substans er endret.

---

## C. Kontrollerte setninger som er gjenfunnet

Setning for setning gjennom briefen. Alt under er verifisert til stede i PRD-en
eller vedlegget.

### Executive Summary

| Kilde | Gjenfunnet |
|---|---|
| Sorteringsspørsmålet besvares på omtrent fem minutter om morgenen | PRD 1 |
| Fast utvalg likvide Oslo Børs-aksjer, kursutvikling, signalstyrke, retning | PRD 2, 3, FR-101 |
| Mulighet for å se hva som ligger bak | FR-706 |
| Beregninger og grovsortering gjøres med vanlig programkode | FR-502, PRD 4.3 |
| KI forklarer hva en melding betyr, og vurderer relevans der kategorifeltet ikke strekker til | PRD 4.3, FR-502, FR-602 |
| Første versjon er på norsk | NFR-05 |
| Kjører lokalt | PRD 2 |
| Webapplikasjon for PC | **Nei — se A5** |
| «Mulig nå fordi KI-assistert utvikling…» | Ikke i PRD — begrunnelse, ikke krav. Ingen innvending |
| Prioriterer stabilitet fremfor mange funksjoner | Se A8 |

### The Problem

| Kilde | Gjenfunnet |
|---|---|
| 10–30 norske aksjer, sorteringsproblem ikke informasjonsproblem | PRD 1, ordrett |
| Medietest 17.09, ti siste nyhetstreff, finansselskapet | PRD 4.3 punkt 1 |
| Medietest 17.09, shippingselskapet | **Nei — se A1** |
| Metode og rådata for medietesten | **Nei — se A2** |
| «En nyhet knyttet til et symbol handler ikke nødvendigvis om selskapet» | PRD 4.3 punkt 1, kursivert |
| 102 meldinger / 73 utstedere / 31 rentejusteringer | Kjent avvik, se del D. Tallene er kontrollert i `malinger.md` seksjon 4 |
| «Mengden er ikke problemet. Sorteringen er» | PRD 4.2, ordrett |
| Forklaringsproblemet: opp 4 %, men ikke hvorfor | PRD 1, FR-706, FR-203 |

### The Solution

| Kilde | Gjenfunnet |
|---|---|
| To skjermbilder og ett prinsipp | PRD 4.5 og 4.6 |
| Omtrent 15 aksjer fra flere sektorer, endelig liste i PRD | PRD 3 — 15 symboler, minst åtte sektorer. Oppdraget er utført |
| Signalstyrke = hvor kraftig kriteriene slår ut | FR-703 |
| Retning = positiv, negativ eller blandet | FR-704 |
| Aksjedetalj: kursgraf | FR-201 |
| Aksjedetalj: noen få tekniske indikatorer | FR-202 — innsnevret til MA50 i grafen, sjekk 2 og 3 som tall. Avgrensningen er begrunnet i FR-202 |
| Aksjedetalj: hvilke faktorer som bidro | FR-706, FR-203 |
| Aksjedetalj: relevante meldinger med lenke til originalen | FR-203 — men se B1 |
| Aksjedetalj: kommende hendelser | FR-203, PRD 6 |
| Meldinger kommer ferdig merket med utsteder og kategori | FR-502, PRD 4.3 (`issuerSign`) |
| Tvilsom vurdering merkes som usikker | FR-603 |
| KI-laget kan slås av; appen fungerer med regelbasert analyse alene | FR-601, NFR-04 |
| Gjør KI-bidraget etterprøvbart | FR-601, FR-604 |
| Hindrer at en treg modell tar ned hovedflyten | NFR-04 |
| Signalstyrke er ikke en anbefaling om kjøp eller salg | PRD 1 og NFR-06 |

### Data og kilder

| Kilde | Gjenfunnet |
|---|---|
| EODHD for kurs, NewsWeb for meldinger, Euronext for hendelser | PRD 6, tabell |
| Hver NewsWeb-melding knyttet til utsteder og kategori | PRD 4.3, FR-502 |
| 20 API-kall i døgnet, ett kall per symbol | PRD 3, NFR-01, `malinger.md` 2 |
| NewsWeb og Euronext koster ingen kall | PRD 3, FR-404, PRD 6 |
| «Tallet er utledet av kvoten, ikke valgt etter skjønn» | PRD 3, nær ordrett |
| Henvisning til `docs/kilder-og-rettigheter.md` | PRD 6 |
| Oppdateringsmekanikk og lagring hører til PRD | FR-401 til FR-406 — utført |

### What Makes This Different

| Kilde | Gjenfunnet |
|---|---|
| Ingen teknisk fordel andre ikke kan kopiere | **Nei — se A4** |
| Koblingen mellom kurs, melding og hendelse er allerede gjort | FR-203 |
| Dekker det en sparer bruker, uten å kreve opplæring | Delvis — se A6 |
| Overskrifter sier ikke hva som gjelder egne aksjer | PRD 4.3 punkt 1 |
| Kode og KI holdes fra hverandre; grensen er synlig i grensesnittet | PRD 1, ordrett |
| «Vi lover ikke bedre signaler enn andre» | PRD 1 og 4.4, ordrett |

### Who This Serves

| Kilde | Gjenfunnet |
|---|---|
| Primærbruker: sparer ved siden av jobb eller studier, begrenset tid | PRD 1 |
| Suksess = åpne om morgenen, se hva som har endret seg, forstå hvorfor, finne det viktigste | PRD 1, ordrett |
| Gruppen er selv i målgruppen og bruker løsningen gjennom perioden | Suksessmålene «Adopsjon» og «Fortsatt bruk» |
| Ingen brukerundersøkelse gjennomført | **Nei — se A7** |

### Success Criteria

| Kilde | Gjenfunnet |
|---|---|
| Brukerutfall: 1 person, under 5 min, uten hjelp, før innlevering | PRD 7, ordrett |
| Adopsjon: 4 av 5 børsdager fra første fungerende versjon | PRD 7, ordrett |
| Kvalitet: henting innenfor kvoten, siste kjente data med tidsstempel | PRD 7 («Drift»), NFR-01, NFR-02, NFR-03 |
| KI-bidrag: dokumentert eksempelsett fra minst én ukes drift | PRD 7, FR-604 — frist endret, se B2 |
| Relevanseksperiment: 50 medieartikler, symbolmatching mot KI | PRD 7, `malinger.md` 6 |
| «Eksperimentet skal avgjøre påstanden, ikke bekrefte den» | PRD 7, motmål |
| Fortsatt bruk: tre dager i uka de to siste ukene, loggført | PRD 7 — se B3 |
| «Relevanseksperimentet er et avgrenset delprosjekt, ikke del av driften» | NFR-01, siste linje |
| «Vi setter ikke mål for hvor godt signalene treffer markedet» | PRD 7, motmål, og PRD 4.4 |
| Ukenumre er planestimater som fastsettes i PRD og sprintplan | PRD 7 — se A9 |

### Scope

| Kilde | Gjenfunnet |
|---|---|
| Inne: markedsoversikt og aksjedetalj for ~15 aksjer | PRD 2 |
| Inne: signalstyrke og retning med synlig begrunnelse | PRD 2, FR-706 |
| Inne: meldinger sortert av regler, forklart av KI | PRD 2, FR-502 |
| Inne: av/på-bryter for KI-laget | PRD 2, FR-601 (skjerpet til brukersynlig) |
| Inne: kommende finansielle hendelser | PRD 2, FR-203 |
| Utenfor: brukerkontoer, innlogging, personlig portefølje | PRD 2 |
| Utenfor: varsler, betaling, mobiltilpasning, meglerintegrasjon | PRD 2 |
| Utenfor: flere børser, flere språk | PRD 2 |
| Utenfor: fundamental- og verdimodell, intradag, sanntid | PRD 2 |
| Utenfor: statistisk studie av om signalene slår markedet | PRD 2, og motmål i PRD 7 |
| Kjører lokalt, publiseres ikke; videreformidlingsrett utsatt | PRD 2 |

Alle tretten punktene i Scope er gjenfunnet. Ingen utelatelser i denne
seksjonen.

### Vision

| Kilde | Gjenfunnet |
|---|---|
| Favorittaksjer | PRD 2, «hvis vi rekker» — favorittmerking |
| Egne lister, mer historikk | Ikke i PRD. Framtidig retning, ikke v1-krav. Ingen innvending |
| Brukerens egen portefølje | PRD 2, utenfor v1 |
| Flere børser og flere språk på sikt | PRD 2, utenfor v1 |
| Kommersiell versjon krever vurdering av videreformidlingsrett | PRD 2 |
| …og av personvern og finansregelverket | **Nei — se A3** |

---

## D. Kjente avvik — ikke rapportert som funn

Disse står i `korreksjon-til-brief.md` og er bevisste:

1. **Rentejusteringseksempelet i *The Problem*.** Tallene (102/73/31) er
   kontrollert og stemmer, men de 31 gjaldt hele Oslo Børs, ikke universet.
   Skal erstattes av tilbakekjøp (28,9 %) og språkdubletter (26,4 %). PRD-en
   bygger allerede på de riktige tallene i seksjon 4.2.
2. **Raden «Dager uten signal» i PRD seksjon 7 finnes ikke i briefen.** Kravet
   sto i tre utkast, falt ut i språkvasken, og er gjenopprettet i PRD-en fordi
   det styrer FR-702. Dette er detalj 6 i mønsteret.

---

## E. Oppsummering

**Utelatelser som bør rettes:** A1 (shippingselskapet — høy), A2 (medietesten
mangler i vedlegget — høy), A3 (personvern og finansregelverk — middels),
A4 (ingen teknisk fordel — middels-lav), A5 (webapplikasjon for PC —
middels-lav). A6 til A9 er notert, ikke påkrevd.

**Motsetninger:** B1 (FR-705 mot FR-203, FR-404 og volumtallene i 4.2 — høy,
må avklares), B2 (frist for KI-bidrag — middels), B3 (vinduet i «Fortsatt
bruk» — lav).

**Dekning ellers:** Scope er fullstendig overført, alle tretten punkter. Success
Criteria er overført med de to avvikene i B2 og B3. Data og kilder er overført i
sin helhet, og alle tall er sporet til `malinger.md` med unntak av medietesten
17.09 (A2).

**Om mønsteret.** A1 og A3 har samme form som de seks tidligere tapene: en
setning der hovedpoenget står først og den kvalifiserende halvdelen sist, og der
bare hovedpoenget overlever omskrivingen. «For et shippingselskap var bildet
motsatt» og «…personvern og regelverket som gjelder når en tjeneste presenterer
finansielle signaler» er begge slike halehalvdeler. Tiltaket i
`korreksjon-til-brief.md` — diff mot forrige versjon, se etter krav som er borte
— bør suppleres: **se særlig etter setninger som er kortet ned bakfra.**
