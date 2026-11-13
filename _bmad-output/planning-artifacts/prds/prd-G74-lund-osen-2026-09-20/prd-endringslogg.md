---
title: "Endringslogg for PRD-en"
status: aktiv
created: 2026-11-12
updated: 2026-11-13T19:36
---

# Endringslogg for PRD-en

[`prd.md`](prd.md) har den gjeldende teksten. Her står historikken: hver datert
linje fra PRD-en slik den var før omskrivingen 12.11, ordrett, ordnet etter krav
og dato, og kommentaren om status fra frontmatteren. PRD-en før omskrivingen står
i taggen `prd-vurdert-2026-11-12`, på commiten `10265324`, som faglærer vurderte i
[`tilbakemelding-prd.md`](tilbakemelding-prd.md). Omskrivingen er story 9.11 i
`epics.md`, etter gruppens svar 12.11 kl. 18:00: en ny versjon med gjeldende
tekst, slik briefen fikk versjon 8 i story 9.6.

Fra 12.11 er `prd.md` et levende dokument, som README-en: teksten endres der den
står, og historikken står her, i git og i taggene. En ny endring i et krav føres
nederst, under «Endringer etter 12.11», som en datert linje med kravets ID.

## Tilbakemeldingen 12.11 og hva som er gjort

| Punkt i tilbakemeldingen | Hva som er gjort |
|---|---|
| 4.1 Gjeldende krav må kunne leses uten historikken | Hvert FR og NFR har én gjeldende tekst som sier hva appen gjør nå, lest i koden 12.11. Alle de daterte linjene står under, ordrett. FR-201 sier periodevalget, FR-101 lista som er aktiv med opptil 18, FR-202 volumsøylene og båndet, og NFR-01 fordelingen av de 20 kallene |
| 4.2 Gi alle FR-er testbare konsekvenser | Hvert FR og NFR har «*Konsekvenser:*» med det en test kan sjekke, også FR-108 og NFR-06 slik tilbakemeldingen foreslo. Testen `tests/test_prd_9_11.py` sjekker at hvert krav har dem |
| 4.3 Én brukerreise og et glossar | UJ-1 med climax og edge, og en ordliste med ti ord, i §1. Ordlista skiller bransje og sektor, aksjesiden og aksjedetaljen, lista og Min liste, og signal og vurdering |
| 4.4 Implementasjonsdetaljer og byggestatus ut av kravene | Kodenavn, commits, migrasjoner, storynummer og «ikke bygget per» er ute av kravene. Det som manglet i arkitekturen eller `epics.md`, står under story 9.11 i `epics.md`. Feltnavn som er grensesnittet mot brukeren, som `close`, `adjusted_close` og variablene i `.env`, står |
| 4.5 Scope-status i én tabell | Tabellen «Kjerne, ekstra og senere» i §2: FR, krav, kjerne / ekstra / senere og bygget, lest i koden 12.11. Plan A står i vedlegg A til slutt |
| §5 Ingen glossar, UJ eller Assumptions Index | Glossar og UJ som i 4.3. Antakelsene som står igjen, `[ANTAKELSE]` og `[FORELØPIG]` i FR-302 og FR-606A, er i vedlegg A. Antakelsen i FR-501 var avkreftet 21.09 og er ute av kravteksten. En egen indeks er ikke laget (spørsmål i spesifikasjonen) |
| §5 FR-ID-ene er ikke sammenhengende | ID-ene er beholdt, så lenker og stories holder. Innledningen til §4 sier at FR-407 står i 4.1 |
| §5 Suksessmålene mangler ID og henvisning til FR | SM-1–SM-9 med kolonnen «Krav» i §7. «KI-bidrag i drift» og «Relevanseksperiment», som ikke gjelder lenger, står her |
| §5 Foreldet tekst: FR-401 «kravteksten over står uendret» | FR-401 er skrevet om: hentekommandoen i fem steg, kveldsjobben og «Start den ekte versjonen» |
| §5 Beslutninger tilskrevet enkeltpersoner | `prd.md` har ingen navn utenom gruppelinja. Avgjørelsene står som gruppens. Linjene under står ordrett, med navnene der de sto |
| §6 og §7 | «Under 5 minutter» står i SM-1, og spørsmålene og stikkordene til refleksjonsrapporten står i spesifikasjonen for 9.11 |

## Linjene, ordnet etter krav og dato

Hver linje står ordrett, med linjenummeret i taggen og, når den sto inne i en
setning, en liste eller en tabellrad, hvor. Innenfor hvert krav står linjene etter
den første datoen i linja, så en linje som begynner med en eldre dato, står
først. Overskriftene er de gamle.

### Innledningen

Linje 41 i taggen:

*Rettet 2026-11-09 (gruppens svar 08.11 kl. 22:14):* der en avgjørelse i dette dokumentet står som én persons, som «Marians beslutning», «godkjent av Marian» eller «Marian bestemte», var den gruppens, og svaret ble gitt i økta for gruppen. Det en person gjorde selv, som å sende en e-post eller regne for hånd, står som før.

### Kort fortalt

Linje 48 i taggen:

*Lagt til 2026-10-28 etter gruppens svar 27.10 kl. 00:08. Kravene under er ikke
endret. Det som er bygget nå, står i [«Status» i README-en](../../../../README.md#status)
(svaret 28.10 kl. 11:30).*

Linje 95 i taggen:

**Bygget per 28.10**, etter «Status» i README-en: sjekkene og styrken hver
børsdag, hentingen, oversikten med hjelp og sortering, hovedindeksen, periodene
i kursgrafen, Min liste, børsometeret, KI-teksten med bryter, Docker og demoen.
Fra 29.10 starter en jobb på en PC i gruppen hentingen hver kveld (tillegget
28.10 under FR-401). Neste i v1 er
prøven av README-en på en ren maskin.

Linje 104 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R35, svaret 03.11 kl. 16:25):* «Bygget per 28.10» i «Kort fortalt» gjelder til 28.10. Bygget per 3.11, etter «Status» i README-en: i tillegg måler jobben fra 29.10 omsetningen etter hentingen med kallene som er igjen (FR-413, story 2.13, `676fbc8b`), og fra 3.11 har oversikten periodevalget, med søylene og indekslinja (story 8.17a, `b2e8b2c`). Min liste, «Signalet dag for dag» og børsometeret som egen side har ikke eget FR (spørsmål 10 i gjennomgangen); de står i `epics.md` og i README-en. Linja står her og ikke i «Kort fortalt», fordi den delen har høyst 400 ord.

Linje 106 i taggen:

*Lagt til 2026-11-03:* PRD-en er gått gjennom før fristen 5.11 i [gjennomgangen 02.11](gjennomganger/gjennomgang-2026-11-02-foer-fristen.md), og rettet 03.11 etter gruppens svar 02.11 kl. 22:15. Hver retting står som en datert linje ved kravet, merket med raden i gjennomgangen (R1–R35), og §8 har fått tabellen «Utenfor v1».

Linje 118 i taggen:

**Om lengden.** Vi satte ambisjonsnivået til middels — 5–8 sider — og landet på
omtrent 11,7. Avviket er kjent og bevisst. Resonnementet er allerede flyttet ut
til `begrunnelser.md` og målingene til `malinger.md`; det som står igjen er
kravene selv, og 130 av linjene her er tabellrader som *er* krav: kolonnene i
markedsoversikten, de ti kategoriene med bøtte, feltene som skal lagres,
suksessmålene og de åpne punktene. Å komme under 11 sider krever at krav går ut,
ikke at teksten strammes. *Talt på nytt 2026-09-24: 130 datarader, uten
overskrift- og skillelinjer. Her sto 115; da det ble skrevet, hadde fila 114
tabellinjer medregnet overskrift- og skillelinjer.*
*Rettet 2026-10-28 kl. 20:57:* målt da hadde fila `2066` linjer og `25605` ord, telt med
`wc -l` og `wc -w`, frontmatteren og denne linja medregnet. Hvordan 11,7 sider
ble målt, står ikke i `.memlog.md`, så sidetallet er ikke målt på nytt.
«Kort fortalt» øverst er siden å lese først.

### 1. Bakgrunn og mål

Linje 148 i taggen:

*Rettet 2026-10-06, etter brief v8:* spørsmålet v1 svarer på, er hva som
beveget seg i går, og hvorfor. «Er det noe viktig på vei» er ute av v1 med
plan B (§2), og «om morgenen» gjelder ikke lenger, etter Marians beslutning
06.10 kl. 21:21: oversikten er ikke bundet til morgenen, og den kan leses når
kveldens henting er gjort.

### Inne i v1

Linje 166 i taggen, ved «Børsmeldinger sortert av regler og forklart av KI»:

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i §8).*

Linje 168 i taggen, ved «Kommende finansielle hendelser»:

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i §8).*

Linje 169 i taggen, ved «Lenke fra aksjedetaljen til selskapets side på NewsWeb»:

*(plan B, 28.09)*

Linje 202 i taggen:

*Plan B, 2026-09-28:* KI-laget forklarer signalet i stedet for børsmeldingene, ut fra tall regnet av kursene (Epic 10). Av/på-bryteren står. FR-601–606 er skrevet om for plan B 2026-09-28, og meldingsversjonen står i §4.6A. *Her sto:* «FR-601–606 skrives om for plan B i en egen runde.»

Linje 170 i taggen, ved «Lenke fra aksjedetaljen til selskapets egen nettside, på norsk der …»:

*(lagt til 2026-09-30)*

Linje 171 i taggen, ved «Tickeren fra Oslo Børs står ved selskapsnavnet i aksjedetaljen, for …»:

*(lagt til 2026-09-30)*

Linje 172 i taggen, ved «Hovedindeksen OSEBX i markedsoversikten, med søyler for dagens …»:

*(lagt til 2026-10-01, Marians beslutning)*

Linje 173 i taggen, ved ««Se nærmere» i aksjedetaljen: tre ting brukeren kan sjekke selv …»:

*(lagt til 2026-10-02, Marians beslutning)*

Linje 174 i taggen, ved «KI-tekst om dagen på forsiden, under tabellen (FR-607)»:

*(lagt til 2026-10-02, Marians beslutning)*

Linje 175 i taggen, ved «Demoversjonen: oppdiktede selskaper og kurser i en egen base, laget …»:

*(lagt til 2026-10-03, Marians beslutning)*

Linje 176 i taggen, ved «Valg av KI-tjeneste: en lokal modell er standard og trenger verken …»:

*(lagt til 2026-10-05, gruppens beslutning 04.10)*

Linje 169 i taggen, ved «Lenke fra aksjedetaljen til selskapets side på NewsWeb»:

*Rettet 2026-10-06:* Marians beslutning 2026-10-06 kl. 20:42: appen lenker ikke til `newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`, fordi Euronexts vilkår forbyr lenker uten tillatelse. Aksjedetaljen lenker til selskapets investorside og nevner NewsWeb uten lenke (`docs/kilder-og-rettigheter.md`, «Lenker til Euronexts nettsteder (lest 2026-10-06)»).

Linje 170 i taggen, ved «Lenke fra aksjedetaljen til selskapets egen nettside, på norsk der …»:

*Lagt til 2026-10-06:* lenken går til selskapets investorside (story 10.5).

Linje 177 i taggen, ved «Endringen i kroner, under prosenten i markedsoversikten og ved …»:

*(lagt til 2026-10-07, Marians beslutning)*

Linje 178 i taggen, ved «Høy og lav for siste børsdag ved sluttkursen i aksjedetaljen (FR-203)»:

*(lagt til 2026-10-07, Marians beslutning)*

Linje 164 i taggen, ved «Markedsoversikt og aksjedetalj for 15 likvide Oslo Børs-aksjer»:

*Lagt til 2026-10-08, Marians beslutning:* de 15 er lista appen starter med, og lista kan ha opptil 18 aksjer valgt fritt (FR-412).

Linje 182 i taggen:

*Lagt til 2026-10-08, Marians beslutning kl. 07:15–07:29, godkjent kl. 08:04 med endringene kl. 08:06* (`sprint-change-proposal-2026-10-08.md`). Femten idéer er «Fast i v1», ikke «Hvis vi rekker». Tretten er rader fra v1.1 i §8, og to er fra designforslaget:

Linje 184 i taggen, ved «Børsometeret: endringen per sektor for lista som er aktiv (FR-106, …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 185 i taggen, ved «Sjekk 2 og 3 synlige i kursgrafen: volumsøyler med median og grense, …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 186 i taggen, ved «Signaldager i kursgrafen, lest fra lagrede vurderinger (FR-206, story …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 187 i taggen, ved «Omvisning på alle sidene, «Vis meg rundt» (FR-109, story 8.9)»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 188 i taggen, ved «Innstillinger øverst, med «Vis hjelp» og «Vis KI-tekst» (FR-110, …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 189 i taggen, ved «Egne aksjelister: lista har opptil 18 aksjer valgt fritt, og de 15 …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 190 i taggen, ved «Flere ferdige lister og filter på signalet (FR-108, FR-412, story …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 191 i taggen, ved «Et merke under signalstyrken når den har endret seg siden forrige …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 192 i taggen, ved «Lær noe nytt (FR-109, story 8.13)»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 193 i taggen, ved «Egne aksjer, «Følg en aksje», som del av lista på opptil 18 (FR-412, …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 194 i taggen, ved «Justeringsdagene det siste året i kursgrafen, uten ordet «utbytte» …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 195 i taggen, ved «Kommende eks.dato i kursgrafen, ført for hånd fra selskapenes egne …»:

*(lagt til 2026-10-08, Marians beslutning kl. 08:06)*

Linje 196 i taggen, ved «Måling av omsetning med kall til overs, som egen kommando (FR-413, …»:

*(lagt til 2026-10-08, Marians beslutning)*

Linje 197 i taggen, ved «Sortering ved klikk på Sluttkurs, Endring og Signalstyrke i …»:

*(lagt til 2026-10-08, Marians beslutning, fra designforslaget)*

Linje 198 i taggen, ved «Periodevalg likt overalt, også i kursgrafen (FR-101, FR-201, story …»:

*(lagt til 2026-10-08, Marians beslutning, fra designforslaget)*

Linje 180 i taggen:

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* endelig v1 er det briefen v8 lover: kjernen, KI-teksten med bryter, historikken, hovedindeksen, Min liste, lenken til investorsiden og egne nøkler til Gemini, Anthropic og OpenAI (FR-608, svaret kl. 16:12), og det som alt er flettet. Resten av lista over, «Se nærmere» (FR-205), KI-teksten om dagen (FR-607), endringen i kroner og høy og lav (FR-101, FR-203), er «Ekstra, hvis tiden rekker». Det bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Det som ikke er flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står som plan for en senere versjon. Kravene står.

Linje 200 i taggen:

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* de femten over er «Ekstra, hvis tiden rekker», ikke v1. Sorteringen (8.15) og periodene i kursgrafen (8.16) er flettet og står. Resten, også periodevalget i oversikten (8.17), bygges etter regelen kl. 14:48, og det som ikke er flettet ved funksjonsstoppen, står som plan for en senere versjon.

### Hvis vi rekker

Linje 212 i taggen:

*Flyttet til v1 2026-09-30:* story 8.3, som eget skjermbilde (Marians beslutning).

Linje 217 i taggen, ved «tilgjengelig på EODHDs gratisnivå.»:

*Rettet 2026-09-30:* kontrollert med ett
  kall. Gratisnivået gir indeksdata for `OSEBX.OL`: HTTP 200 og ett års serie
  med de samme feltene som aksjene (`malinger.md` §14)

Linje 220 i taggen:

*Flyttet til v1 2026-10-01, Marians beslutning:* FR-104, FR-105 og FR-410.

Linje 214 i taggen:

*Flyttet til v1 2026-10-08, Marians beslutning:* FR-201 og FR-101, story 8.16 og 8.17.

### Utenfor v1

Linje 229 i taggen:

*Lagt til 2026-11-10 (gruppens svar kl. 14:44):* tenkte kjøp og salg ved et notat på aksjesiden (story 8.21) er flyttet inn i v1. Ekte portefølje, kontoer, varsler og statistikk over om signalene slår markedet står utenfor som før.

### Utsatte vurderinger

Linje 237 i taggen:

*Rettet 2026-09-24:* videreformidlingsretten er ikke lenger utsatt. Vilkårene
til EODHD og til Euronext, som dekker NewsWeb, ble kontrollert 2026-09-21. Se
`docs/kilder-og-rettigheter.md` og åpent punkt 1.

### Kriterium

Linje 261 i taggen:

*Lagt til 2026-10-13, endringsforslaget 13.10 (svar 24 og N3):* det brukeren ser, heter «bransje», og koden og kravene sier «sektor». Appen har 13 bransjer (`designregler.md` §4), og de 15 hører til 8 av dem.

### Universet

Linje 298 i taggen:

*Lagt til 2026-10-08, Marians beslutning kl. 07:29:* lista kan byttes (FR-412).
De 15 over er lista appen starter med, og lista kan ha opptil 18 aksjer valgt
fritt. Kriteriet over gjelder de 15. Grensene i signalet er målt på dem
(`AD-13`), og en aksje som omsettes mindre enn de 15 ble målt på, merkes
«Utenfor målingen» (Marians beslutning 02.10 i raden «Egne aksjelister» i §8).
18 aksjer og hovedindeksen gir 19 kall (NFR-01).

### FR-101 — Fem kolonner

Linje 324 i taggen, ved «Retning»:

*(rettet 2026-09-23 fra «Opp, Ned»)*

Linje 378 i taggen:

*Endret 2026-09-23.* Sidens tidsstempel er det **eldste** `sist_hentet` blant
symbolene som vises. En rad med eldre tidsstempel enn det nyeste viser sitt
eget, i selskapscellen under navnet — ikke som en sjette kolonne. Tidsstempler
vises i norsk tid (lagret i UTC, AD-20).

Linje 330 i taggen:

*Lagt til 2026-10-07, Marians beslutning kl. 23:11 (story 8.5):* endringscellen
viser også endringen i NOK, på en mindre linje under prosenten. Den regnes av
`adjusted_close` for de to siste børsdagene, som prosenten, så de to peker alltid
samme vei. Det er fortsatt fem kolonner, og sorteringen er fortsatt på prosent
(FR-102). En utbyttedag merkes etter FR-407.

Linje 338 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 2.11 og 8.17):* oversikten viser
aksjene i lista som er aktiv (FR-412), ikke et fast antall på 15. Periodevalget i
`designregler.md` §2 gjelder oversikten: siste børsdag («I går», «I dag» eller
ukedagen), 1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år og «Velg dag». Startdagen
følger én regel, lik for alle periodene og for kursgrafen (FR-201). Endringen
over en periode regnes av kursserien, på `adjusted_close`, som endringen for én
dag. Signalet for en dag vises bare der vurderingen er lagret, ellers «– ikke
vurdert», grunnen eller «– ikke børsdag». Det regnes aldri et signal for en
tidligere dag (`AD-7`). Det er fortsatt fem kolonner.

Linje 374 i taggen:

*Lagt til 2026-10-24 (story 8.2a, b, gruppens svar kl. 11:34 og 11:35, U23):* en aksje uten en eneste kursrad har en rad nederst i tabellen, med navnet som lenke, «–» i hver kolonne og «uten data». Fotnoten under tabellen er borte. Brukeren ser fortsatt at oversikten er ufullstendig, og tallet i overskriften stemmer med radene.

Linje 336 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R16):* ikke bygget per 3.11, story 8.5, ekstra fra 19.10.

Linje 348 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R14):* periodevalget i oversikten er bygget i story 8.17a (`b2e8b2c`, PR #106), med søylene og indekslinja (FR-105). I Min liste og børsometeret: ikke bygget per 3.11, story 8.17b, ekstra fra 19.10. At oversikten viser lista som er aktiv: ikke bygget per 3.11, story 2.11, ekstra fra 19.10.

Linje 350 i taggen:

*Lagt til 2026-11-03:* periodevalget i Min liste («Sammenlign med») og i børsometeret er flettet 3.11 i story 8.17b (`978bd1a`, PR #108).

### FR-102 — Standard sortering

Linje 411 i taggen:

*Endret 2026-09-23.* **Tidsstempelet påvirker ikke sorteringen.** En rad med
eldre data sorteres etter samme regel som de andre, ikke sist. Sorteringen er
signalets, ikke ferskhetens, og ferskheten vises på raden (FR-101).

Linje 423 i taggen:

*Flyttet til v1 2026-09-30:* story 8.3, som eget skjermbilde (Marians beslutning).

Linje 425 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.15):* standarden over står. Et
klikk på Sluttkurs, Endring eller Signalstyrke i kolonneraden sorterer på
kolonnen, og et nytt klikk snur rekkefølgen. Endring sorteres på prosent. Rader
uten verdi står sist i begge retninger. Kolonneraden sier hvilken kolonne og
retning som gjelder, også til skjermleseren. Det er fortsatt fem kolonner
(FR-101). Gjelder også Min liste.

Linje 432 i taggen:

*Lagt til 2026-10-15 (gruppens svar 1 og 2 på planen for story 8.15, instruksjonen kl. 14:01):*
første klikk sorterer synkende (høyest kurs, størst oppgang og sterkest signal
først), og neste klikk stigende. Endring sorteres med fortegn ved klikk.
Standarden over står som før. Retning kan også sorteres, som en gruppering i
alfabetisk rekkefølge, Blandet, Ingen, Negativ og Positiv, med standarden over
innenfor hver gruppe og Ukjent sist i begge retninger. Første klikk gir A til Å,
og teksten for skjermleseren sier «alfabetisk». Rekkefølgen er ikke en
rangering fra godt til dårlig (NFR-06).

Linje 441 i taggen:

*Lagt til 2026-10-15 (gruppens svar 8 på funnene i PR #43 for story 8.15, instruksjonen kl. 15:25):*
for Retning sier teksten for skjermleseren «stigende (A til Å)» eller «synkende
(Å til A)», ikke «alfabetisk», og linja over tabellen sier det samme.

Linje 445 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R6):* Selskap sorteres også ved klikk, A til Å først, i norsk rekkefølge (story 8.15b, gruppens svar 2026-10-18 kl. 22:06, `src/markedsoversikt.py`).

### FR-103 — Retning vises i tre redundante kanaler

Linje 461 i taggen:

*Endret 2026-09-21.* Kravet sa tidligere «Opp» og «Ned». De ordene sto rett ved
siden av kolonnen Endring og inviterte til å lese pilen som kursbevegelse,
mens retningen sier noe annet: hva de tre sjekkene peker mot. Briefen slår fast
at signalstyrke ikke er en anbefaling om kjøp eller salg, og «Opp/Ned» lener
seg mot nettopp den lesningen. Oversettelsen er fjernet, ikke dokumentert.

### FR-104 — Hovedindeksen i markedsoversikten

Linje 475 i taggen:

*Lagt til 2026-10-01, Marians beslutning.*

Linje 493 i taggen:

*Rettet 2026-10-30, gruppens svar kl. 12:21 (e og f):* alle sidene følger samme regel,
én dag per side, og alt på siden, også indeksen, gjelder den dagen (Rettet-linja
under FR-105). Verdien, endringen og «x av N» gjelder derfor tabellens dag, siste
børsdag i oversikten eller dagen fra «Velg dag», ikke indeksens siste børsdag, og N
er aksjene med kurs den dagen. Mangler indeksen kurs den dagen, står det der tallet
ellers står, i stedet for siste lagrede verdi. Gruppen ser over tolkningen før
flettingen av 8.17a (gjennomgangen 30.10, BH4).

Linje 501 i taggen:

*Lagt til 2026-11-03, gruppens svar 02.11 kl. 17:40:* tolkningen av f står, og avvikene fra
én dag per side beholdes som et felles unntak, slik koden er. Mangler en aksje kurs for
dagen siden viser, viser raden i oversikten og i Min liste aksjens egen siste dag:
sluttkursen, endringen og vurderingen for den dagen, og ved en periode endringen fra den
første kursen i perioden til den dagen (`med_perioden`). Raden sier ikke hvilken dag den
gjelder. Under navnet står «hentet» med tidspunktet bare når aksjens kurser ble hentet
tidligere enn de nyeste (`eldre_enn_nyeste`, story 1.4c). Ukedagen i overskriften og datoen i
linja under den er den eldste blant radene (`sidens_dato`), mens hovedindeksen, søylene og linja
over tabellen gjelder den nyeste (`sidens_siste`). Aksjesiden viser aksjens egen siste
dag, med datoen i linja under overskriften, og sier ikke at dagen er en annen enn
siste børsdag i oversikten: «Siden viser …, ikke siste børsdag» står bare for en tidligere
dag valgt med «Velg dag». Den stiplede indekslinja i kursgrafen slutter ved indeksens siste
kurs, og da står «Indeksen går bare til» med datoen ved grafen. «Velg dag» i oversikten har
ikke unntaket: der har en aksje uten kurs den dagen «–». Unntaket står også under FR-105.

Linje 516 i taggen:

*Rettet 2026-11-03, gruppens svar kl. 14:28 (story 8.17b):* «Raden sier ikke hvilken dag den
gjelder» gjelder ikke lenger. En rad med eldre dag enn sidens viser datoen sin, «siste kurs» med
ukedagen og datoen under navnet, i oversikten og i Min liste, også ved en periode (`egne_dager`).
Overskriften står som nå (FR-101). Bygget på grenen for 8.17b, ikke flettet per 3.11.

Linje 521 i taggen:

*Lagt til 2026-11-03:* flettet 3.11 i story 8.17b (`978bd1a`, PR #108).

Linje 523 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R5):* hovedindeksen står også som stiplet linje i kursgrafen på aksjesiden (FR-202, story 2.9c, `24849dd9`).

### FR-105 — Søylene under hovedindeksen

Linje 527 i taggen:

*Lagt til 2026-10-01, Marians beslutning.*

Linje 562 i taggen:

*Lagt til 2026-10-01:* bransjesymbolet er gult når aksjen har 3 av 3 på siste børsdag (designregler.md §3).

Linje 540 i taggen:

*Rettet 2026-10-08 kl. 21:48, Marians beslutning:* «Bare dagens søyler» gjelder
  ikke lenger. Søylene følger periodevalget i oversikten og «Velg dag», som
  tabellen (FR-101, tillegget 08.10), og indekslinja følger samme periode.
  Endringen regnes som i FR-101, av kursserien på `adjusted_close`.
  Bransjesymbolet er gult som før (`designregler.md` §3). Story 8.17.

Linje 545 i taggen:

*Rettet 2026-10-30, gruppens svar kl. 12:21 (f):* alle sidene følger samme
  regel, én dag per side, og alt på siden, også indeksen, gjelder den dagen.
  Søylene, den stiplede linja, tallet for indeksen og «x av N» gjelder derfor
  tabellens dag, siste børsdag i oversikten eller dagen fra «Velg dag», ikke
  indeksens dato. «En aksje uten kurs for indeksens dato får ingen søyle»
  gjelder tabellens dag. Mangler indeksen kurs den dagen, sier siden det der
  tallet ellers står og over søylene (svaret kl. 10:45 b og kl. 12:21 e).
  Gruppen ser over tolkningen før flettingen av 8.17a.

Linje 554 i taggen:

*Lagt til 2026-11-03, gruppens svar 02.11 kl. 17:40:* unntaket fra én dag per side under
  FR-104 gjelder også her. En aksje uten kurs for tabellens dag står i tabellen med sin egen
  siste dag, men får ingen søyle, fordi søylene bare har aksjene med kurs for tabellens dag
  (`bygg_soeyler` og `bygg_soeyler_perioden`). I kursgrafen på aksjesiden slutter den
  stiplede indekslinja ved indeksens siste kurs, med «Indeksen går bare til» og datoen.

Linje 560 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R14):* søylene og indekslinja følger periodevalget i oversikten, bygget i story 8.17a (`b2e8b2c`, PR #106).

### FR-106 — Børsometeret

Linje 566 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.6).*

Linje 576 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R4):* børsometeret er bygget som en egen side, `/boersometer`, ikke i markedsoversikten: et kart med én rute per aksje ordnet etter bransje, med farge for endringen, størrelse for volumet mot vanlig, ramme for signalet og snittet per bransje ved navnet (story 8.6, `7f1c1f09`, og 8.6b, `7f6d9e4c`, avgjørelsen 2026-10-22 kl. 23:19 i `epics.md`).

### FR-107 — Endret signalstyrke siden forrige børsdag

Linje 580 i taggen:

*Lagt til 2026-10-08, Marians beslutning 02.10 kl. 23:30, slik instruksjonen
2026-10-08 kl. 08:06 gjengir den (story 8.12).*

Linje 595 i taggen:

*Lagt til 2026-10-08 kl. 21:48, Marians beslutning:* «Sammenlign med» er
periodevalget i Min liste i designforslaget. Hver rad viser tallene for siste
børsdag øverst og dagen man sammenligner med under. Det beskrives og bygges i
8.17, som kommer før 8.12.

Linje 600 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R20):* ikke bygget per 3.11, story 8.12, ekstra fra 19.10.

### FR-108 — Filter på signalet

Linje 604 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.11).*

Linje 612 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R20):* ikke bygget per 3.11, story 8.11, ekstra fra 19.10.

### FR-109 — Hjelpen på sidene

Linje 616 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.0b, 8.9 og 8.13).*

Linje 632 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R21):* delvis bygget per 3.11. Hjelpen bak spørsmålstegnet er bygget (story 8.0b, og 8.0f, `238ef186`, PR #102). Omvisningen og «Lær noe nytt»: ikke bygget per 3.11, story 8.9 og 8.13, ekstra fra 19.10.

### FR-110 — Innstillinger

Linje 636 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.10).*

Linje 644 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R21):* ikke bygget per 3.11, story 8.10 og 8.10b, ekstra fra 19.10.

### FR-407 — Merking av utbyttedager

Linje 666 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.14):* kursgrafen markerer
justeringsdagene det siste året, og aksjedetaljen viser hvor mange det var og
datoen for den siste. Dagene er de samme som 2.6 finner, regnet av kursserien
alene. Metoden ser justeringer, ikke utbytter, og en splitt gir samme utslag
(`begrunnelser.md` §11), så grafen og teksten sier «justeringsdag», ikke
«utbytte». Vinduet er ett år, så et selskap som betaler én gang i året, kan i
perioder stå med null. Historikken sier ingenting om neste justering (NFR-06).
Navnet på kravet og på story 2.6 avgjøres i planen for 2.6.

Linje 664 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R15):* ikke bygget per 3.11, story 2.6 og 8.14, ekstra fra 19.10. «Kravet må være oppfylt før demonstrasjonen» gjelder derfor ikke lenger.

### FR-201 — Kursgraf med seks måneders historikk

Linje 690 i taggen:

*Rettet 2026-10-08, Marians beslutning (story 8.16):* perioden er ikke lenger fast,
og setningen over gjelder ikke lenger. Kursgrafen har periodevalget fra
`designregler.md` §2, med de samme knappene som oversikten (FR-101, tillegget
08.10): siste børsdag, 1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år og «Velg dag».
Grafen åpner med 6 mnd. Startdagen for hver periode kommer fra én funksjon, og
regelen skrives i `designregler.md` §2 før den bygges. Den testes med faste
datoer rundt helger, helligdager og nyttår (NFR-08). 1 år viser bare det
kursserien har, og grafen sier det når serien er kortere.

Linje 699 i taggen:

*Lagt til 2026-10-18 (gruppens svar kl. 21:46, 21:49 og 21:50, story 8.16):* grafen får alle åtte knappene. Den første knappen, siste børsdag («I går» når den var i går), og «Velg dag» viser 6 mnd fram til dagen, med dagen merket, endringen den dagen og signalet som er lagret for den. Signalet regnes aldri på nytt (AD-7).

Linje 701 i taggen:

*Lagt til 2026-10-19 (gruppens svar kl. 00:00, spesifikasjonen 8.16b under story 8.16):* når en dag er valgt med «Velg dag», viser hele aksjesiden den dagen: kortene øverst, «Hvorfor signalet ble», KI-teksten og grafen, lest fra det som er lagret for dagen, med et merke øverst og en lenke tilbake til siste børsdag. Signalet regnes aldri på nytt (AD-7). Det utvider linja over.

### FR-202 — MA50-linjen tegnes oppå kursen

Linje 746 i taggen:

*Rettet 2026-10-08, Marians beslutning (story 8.7):* «Volatilitetsbånd og
volumsøyler tegnes ikke i v1» gjelder ikke lenger. Volumsøylene står under
kursgrafen, i samme SVG, med en strek for medianvolumet og en for grensen sjekk 3
slår ut ved. Medianen regnes med samme funksjon og over samme vindu som i sjekk 3
(`VOLUM_VINDU`), og grensen er `VOLUMFAKTOR` ganger medianen. For sjekk 2 tegnes
et bånd rundt forrige dags `adjusted_close` med standardavviket fra sjekk 2
(`VOLATILITET_VINDU`). Tallene hentes fra `Parametre`, som i hjelpen. Mangler
volumet, eller er medianen 0, tegnes ikke streken, og grafen sier det (NFR-08).
Samme prinsipp som over: grafen skal forklare regelen som ble brukt.

Linje 710 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R5):* fra story 2.9c (`24849dd9`, PR #64) tegnes også hovedindeksen, som en tredje, stiplet linje, regnet om så den starter på aksjens kurs.

Linje 756 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R17):* ikke bygget per 3.11, story 8.7, ekstra fra 19.10.

### FR-203 — Øvrig innhold

Linje 783 i taggen:

*Lagt til 2026-09-25:* over meldingene står en teller for hvor mange som ble
funnet og hvor mange som vises, med grunnen til at resten er skjult: filtrert
bort etter kategori (FR-502) eller vurdert som «lite relevant» (FR-606A). En
bryter veksler mellom **Anbefalt**, som er filteret over, og **Alle**, som også
viser det som er skjult, merket med grunnen. Eks.dato er fortsatt merking, ikke
melding (FR-503). Bryteren endrer bare visningen, ikke hva KI-laget vurderer.
KI-forklaringen per melding ligger bak «Vis forklaring». Teksten er laget i
hentingen, og et klikk viser den, men lager den ikke (NFR-02).

Linje 765 i taggen, ved «Børsmeldinger som passerte filteret, med lenke til originalen på …»:

*Ute av v1 fra 2026-09-28 (plan B).*

Linje 767 i taggen, ved «av (FR-602A)»:

*Ute av v1 fra 2026-09-28 (plan B).*

Linje 768 i taggen, ved «Kommende finansielle hendelser fra Euronext»:

*Ute av v1 fra 2026-09-28 (plan B).*

Linje 769 i taggen, ved «KI-teksten under regelforklaringen når KI-laget er på (FR-602)»:

*(plan B, 2026-09-28)*

Linje 773 i taggen, ved «lenker, slås opp av en av oss før lenken bygges»:

*(plan B, 2026-09-28)*

Linje 783 i taggen:

*Ute av v1 fra 2026-09-28 (plan B).*

Linje 774 i taggen:

*Rettet 2026-10-06:* Marians beslutning 2026-10-06 kl. 20:42: appen lenker ikke til `newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`, fordi Euronexts vilkår forbyr lenker uten tillatelse. Aksjedetaljen lenker til selskapets investorside og nevner NewsWeb uten lenke (`docs/kilder-og-rettigheter.md`, «Lenker til Euronexts nettsteder (lest 2026-10-06)»).

Linje 776 i taggen:

*Lagt til 2026-10-07, Marians beslutning kl. 23:11 (story 2.10 og 8.5):*
aksjedetaljen viser høy og lav for siste børsdag ved sluttkursen, og endringen i
NOK ved prosenten. Høy og lav vises bare når begge finnes og lav ≤ sluttkurs ≤
høy, ellers «–» (regelen i NFR-08). De tegnes ikke i grafen.

Linje 781 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R16):* ikke bygget per 3.11, story 2.10 og 8.5, ekstra fra 19.10.

### FR-204 — Aksjedetaljen for en aksje uten gyldig signal

Linje 816 i taggen:

*Rettet 2026-10-23, gruppens svar kl. 11:44 (story 8.6):* 404 gjelder bare et
symbol utenfor lista, og en base uten en eneste kurs før første henting, når
ingen side lenker dit. En aksje i lista uten kurser svarer 200 med en beskjed
(svaret 23.10 kl. 09:24, b, under story 8.6 i `epics.md`).

### FR-205 — Se nærmere

Linje 823 i taggen:

*Lagt til 2026-10-02, Marians beslutning (story 8.4).*

Linje 829 i taggen:

*Rettet 2026-10-06:* Marians beslutning 2026-10-06 kl. 20:42: appen lenker ikke til `newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`, fordi Euronexts vilkår forbyr lenker uten tillatelse. Aksjedetaljen lenker til selskapets investorside og nevner NewsWeb uten lenke (`docs/kilder-og-rettigheter.md`, «Lenker til Euronexts nettsteder (lest 2026-10-06)»).

Linje 834 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R18):* ikke bygget per 3.11, story 8.4, ekstra fra 19.10.

### FR-206 — Signaldager i kursgrafen

Linje 838 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 8.8).*

Linje 847 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R18):* ikke bygget per 3.11, story 8.8, ekstra fra 19.10.

### FR-207 — Kommende eks.dato i kursgrafen

Linje 851 i taggen:

*Lagt til 2026-10-08, Marians beslutning kl. 08:06 (story 8.18).*

Linje 862 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R19):* ikke bygget per 3.11, story 8.18, ekstra fra 19.10.

### 4.3 Kommende finansielle hendelser

Linje 866 i taggen:

*Utenfor v1 (plan B, 28.09). Lagt til 2026-11-03 (gjennomgangen 02.11, R8):* kommende hendelser er ute av v1 (§2, punkt 1 i §8), og Epic 7 står i backlog. FR-301–FR-303 står som plan for en senere versjon.

### FR-401 — Henting utløses eksplisitt, aldri av en oppstart

Linje 916 i taggen:

*Endret 2026-09-22.* Kravet sa opprinnelig at henting utløses når applikasjonen
starter. Det var skrevet for en applikasjon som starter én gang. En container
startes på nytt hver gang, så «ved oppstart» ville betydd 15 kall per
`docker run` mot en dagskvote på 20 — to kjøringer ville brukt opp dagen.
Arkitekturspinen AD-10 og AD-17.

Linje 922 i taggen:

*Avgjort 2026-09-29, gjelder når story 2.3 er bygget.* Da endres kravet slik
at hentekommandoen kan startes av en planlagt jobb på Marians PC:
Oppgaveplanlegging i Windows, hverdager kl. 22:15. Tapte kjøringer tas ikke
igjen, og utskriften går til en loggfil i `data/`. Grunnene: punkt 23 har lagt
kjøringen til kl. 22:00–midnatt, 2.3 gjør kommandoen trygg å starte når som
helst, og etter 2.5 er en dag uten henting en vurdering som mangler for alltid
(AD-7). Til da kjøres hentingen for hånd, og kravteksten over står uendret.

Linje 930 i taggen:

*Lagt til 2026-10-05, gruppens svar kl. 19:17 på planen for story 2.3:* jobben kjører hver dag kl. 22:15, ikke bare på hverdager. På en dag som ikke er børsdag avgjør basen om det hentes: mangler siste børsdag for noen av aksjene, hentes den, fordi raden for den dagen fortsatt kan skrives (AD-7). Jobben kjører fra en egen arbeidskopi av main, som deler `data/` og `.env` med hovedkopien uten at nøkkelen kopieres.

Linje 932 i taggen:

*Lagt til 2026-10-17:* fra mandag 19.10 nekter tidskontrollen i hentingen bare før kl. 21:00 på en børsdag, ikke før kl. 22:00, så punkt 23 legger kjøringen til kl. 21:00–midnatt (beslutningen 16.10 kl. 21:09 under story 2.3, `malinger.md` §31). Når jobben i Oppgaveplanlegging skal kjøre, avgjøres i planen for den.

Linje 934 i taggen:

*Lagt til 2026-10-20 kl. 15:12:* fra tirsdag 20.10 nekter tidskontrollen igjen før kl. 22:00 på en børsdag, så punkt 23 legger kjøringen til kl. 22:00–midnatt, som før 19.10. Det snur beslutningen 16.10 kl. 21:09, etter gruppens svar 19.10 kl. 22:19 under story 2.3: raden fra kl. 21 var ikke endelig for DNO (`malinger.md` §37), og en vurdering kan ikke skrives om (AD-7).

Linje 936 i taggen:

*Lagt til 2026-10-24 (story 3.5a, gruppens svar 23.10 kl. 23:31):* regelen står. «Start den ekte versjonen» kjører hentekommandoen før webserveren, og dobbeltklikket er den bevisste handlingen. Webserveren henter aldri. Er det ingenting nytt å hente, gir dobbeltklikket 0 kall (FR-402): hentekommandoen stopper ved sjekken av basen, før første kall. I en mappe med `.git` starter ikke den ekte versjonen, så et dobbeltklikk i en klon aldri henter med gruppens nøkkel.

Linje 938 i taggen:

*Lagt til 2026-10-28 (story 2.3d, flettet i `817b331`, gruppens svar kl. 11:34):* beslutningen 29.09 gjelder fra torsdag 29.10. Hentekommandoen startes av jobben «OSE Signal kveldshenting» i Oppgaveplanlegging på Marians PC, hver dag kl. 22:15 og igjen hver halvtime til 23:45, fra en egen arbeidskopi av main på commiten main hadde ved midnatt. Tapte kjøringer tas ikke igjen, og loggen er `data/logg/kveldshenting-<dato>.log`. Instruksjonen for hentingen brukes bare når loggen viser at jobben feilet. Webserveren henter fortsatt aldri. README-en, «Hentingen hver kveld», sier hvordan jobben legges inn og tas bort.

Linje 912 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R7):* rekkefølgen som er bygget, er kursene for aksjene, hovedindeksen (FR-410), vurderingene og KI-teksten (`src/fetch_prices.py`). Målingen av omsetning (FR-413) er et eget valg som jobben kjører etter hentingen. Meldinger hentes ikke i v1 (plan B, 28.09).

Linje 940 i taggen:

*Lagt til 2026-11-05 (story 2.3d, gruppens svar 05.11 kl. 12:33 og 19:33, forslag a):* før Docker Desktop og Ollama startes, sjekker hver kjøring med `src/dagen_ferdig.py`, med basen bare for lesing og uten nøkkel eller kall, om børsdagen hentingen gjelder, er ferdig: kursene og vurderingene for de 15, hovedindeksen og KI-tekstene. Er den det, startes verken Docker Desktop eller Ollama, og `fetch_prices.py` (0 kall) og `--maal-omsetning` kjøres som før, med reglene for kvoten og kl. 23:45 der. Mangler noe, eller feiler sjekken eller går over tidsgrensen, går kjøringen som før.

### FR-402 — Kontroll mot forventet børsdag, ikke mot klokkeslett

Linje 955 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R1):* når basen er tom, henter første henting siste fullførte børsdag, også på dagtid en hverdag (story 2.3c, avgjørelsen 2026-10-21 kl. 23:33 i `epics.md`). Unntaket fra `AD-7` står ved FR-408.

### FR-403 — Etterfylling av kurser etter dager uten bruk

Linje 968 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R25):* FR-403 oppfylles gjennom FR-406: hver henting erstatter symbolets serie i sin helhet, så et hull fylles uansett. Kontrollen story 2.4 skal skrive: ikke bygget per 3.11, story 2.4, ekstra fra 19.10.

### FR-404 — Etterfylling av børsmeldinger

Linje 972 i taggen:

*Utenfor v1 (plan B, 28.09). Lagt til 2026-11-03 (gjennomgangen 02.11, R9):* det hentes ikke fra NewsWeb i v1 (punkt 1 i §8), og story 6.2 står i backlog.

### FR-405 — Avkorting ved lange meldingsintervaller

Linje 982 i taggen:

*Utenfor v1 (plan B, 28.09). Lagt til 2026-11-03 (gjennomgangen 02.11, R9):* som FR-404, og story 6.2 står i backlog.

### FR-406 — To lagre for kursdata, med hvert sitt ansvar

Linje 1051 i taggen:

*Skrevet inn 2026-09-21.* Kravet manglet. `fetch_prices.py` hentet 364 dager,
og det var tilstrekkelig — men det var en egenskap ved implementasjonen, ikke
noe noe krav ba om. En senere endring som kortet ned intervallet for å «spare»,
ville ødelagt grafen uten å bryte et eneste krav.

Linje 1059 i taggen:

*Merknad 2026-09-22.* Resonnementet over er bevart slik det ble skrevet.
> Utløseren det beskriver — henting ved oppstart — finnes ikke lenger etter
> omskrivingen av FR-401. Kvoteregnestykket står seg: 15 symboler mot en
> dagskvote på 20 er fortsatt grunnen til at minstehistorikk-kravet ser ut som
> det gjør. Det er ordet «oppstart» som er foreldet, ikke regnestykket.

### FR-408 — Dagens vurdering lagres per aksje

Linje 1124 i taggen:

*Presisert 2026-09-22.* Kravet sa «for hver aksje, hver dag» og «lagringen skjer
automatisk». Begge deler kunne leses som at systemet skriver av seg selv hver
dag, og det motsier FR-401 etter omskrivingen samme dag. Skillet mellom kurser
som etterfylles og vurderinger som ikke gjør det, var ikke skrevet ned før nå.

Linje 1084 i taggen:

*Utenfor v1 (plan B, 28.09). Lagt til 2026-11-03 (gjennomgangen 02.11, R11):* raden «Relevante meldinger» er ikke en kolonne i `vurdering`. `src/migrasjoner/0002_vurdering.sql` sier at den kommer senere, og meldingene er ute av v1.

Linje 1079 i taggen, ved «Målingene»:

*Lagt til 2026-09-29*

Linje 1086 i taggen:

*Lagt til 2026-09-29, avgjort av gruppen 28.09.* Målingene lagres fordi en
vurdering skal kunne etterprøves og sjekkes. Et fortegn uten måling kan ikke det
(FR-706): «trend +1» sier ikke hvor langt over snittet kursen lå. Med målingen
kan fortegnet regnes etter fra raden alene, med de låste parametrene (AD-13).
Endres en parameter, føres det i `malinger.md` (AD-13) med datoen den nye
grensen gjelder fra, så en eldre rad leses med grensene som gjaldt da.

Linje 1122 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R1):* det er ett unntak. Første henting på dagtid i en tom base skriver vurderingene og KI-radene for børsdagen rett før inneværende, bare når basen ikke har rader for en annen dato, og hver rad skrives én gang og regnes aldri på nytt (story 2.3c, `2a84142d`, PR #87, unntaket fra `AD-7` godkjent 2026-10-22 kl. 19:30 i `epics.md`).

### FR-409 — De tre tilstandene skal være skillbare i lageret

Linje 1164 i taggen:

*Skrevet inn 2026-09-22*, da `AD-17` ble tatt opp igjen og konsekvensen av
`AD-7` ble avgjort eksplisitt.

Linje 1144 i taggen:

*Avgjort 2026-09-27 (punkt 24 i §8):* kan kjøringen ikke vurdere en aksje,
skriver den en rad med grunnen i stedet. Det er fortsatt tre tilstander: raden
finnes, men bærer grunnen i stedet for vurderingen. En slik rad er verken styrke
0 eller et hull i driften, og ingen rad på en børsdag betyr bare at kommandoen
ikke ble kjørt.

Linje 1169 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 2.11):* en dag etter at aksjen ble
tatt ut av lista (FR-412), er verken «ikke kjørt» eller «ikke børsdag». Den vises
som «ikke i lista», så den ikke telles som et hull i driften. Skillet kommer i
`tilstand`, ikke i porten (`AD-7`). Fra samme dag finnes det visninger som leser
historikken: signaldagene (FR-206), merket for endret signalstyrke (FR-107) og
«Velg dag» (FR-101, tillegget 08.10). «Det finnes ingen visning av
vurderingshistorikk i v1» gjelder derfor ikke lenger, og bindingen over gjelder
dem alle.

Linje 1178 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R22):* «ikke i lista» er ikke bygget per 3.11 (`src/tilstand.py` har den ikke), story 2.11, ekstra fra 19.10.

Linje 1165 i taggen, ved «AD-7 ble avgjort eksplisitt.»:

*Rettet samme kveld:* kravet var først formulert
som et visningskrav og lovet at dagen ikke skulle se ut som «et hopp i
historikken» — i en historikkvisning som ikke er spesifisert noe sted.

### FR-410 — Hovedindeksen hentes i samme kjøring

Linje 1182 i taggen:

*Lagt til 2026-10-01, Marians beslutning.*

Linje 1195 i taggen:

*Lagt til 2026-11-07 (gruppens svar kl. 11:05, story 2.16):* appen skal regne ut de stengte
  hverdagene for hvert år etter reglene Oslo Børs følger, med påsken regnet ut, så kalenderen
  dekker alle år. Hvordan `DEKKEDE_AAR` endres, avgjøres i spesifikasjonen for 2.16.

Linje 1198 i taggen:

*Lagt til 2026-11-07 (story 2.16, flettet i `a1c67c1a`):* `DEKKEDE_AAR` er borte. Kalenderen
  dekker 2026 og hvert år etter (`FOERSTE_AAR = 2026` i `boersdag.py`, uten øvre grense), og 2025
  står utenfor (gruppens svar kl. 15:34).

### FR-411 — Demoversjonen har oppdiktede tall i en egen base

Linje 1207 i taggen:

*Lagt til 2026-10-03, Marians beslutning kl. 18:10.*

Linje 1239 i taggen:

*Avgjort 2026-10-05:* demoen får ferdige KI-tekster laget med Gemma, i story 3.4b (`epics.md`).

Linje 1241 i taggen:

*Lagt til 2026-10-05, gruppens beslutning:* demoversjonen er hovedveien for
vurderingen. Den ekte versjonen med egen EODHD-nøkkel står i README-en som et
valg. Grunnen er svaret fra hjelpelæreren 05.10 (`docs/innlevering.md`,
«Svaret, 2026-10-05»): vurderingen skal ikke avhenge av at noen oppretter konto
hos en ekstern tjeneste, og «en god demoversjon er mer enn tilstrekkelig for å
vise hvordan løsningen fungerer».

Linje 1248 i taggen:

*Lagt til 2026-10-08, Marians beslutning:* alt i v1 skal kunne vises i demoen.
Demobasen har i tillegg minst én aksje som er tatt ut av lista, én merket
«Utenfor målingen», noen målte omsetninger, oppdiktede eks.datoer og vurderinger
nok til at signaldagene, merket for endret signalstyrke og «Velg dag» har noe å
vise. Lista i demoen kan byttes, men det hentes aldri (story 3.4).

Linje 1256 i taggen:

*Lagt til 2026-10-13, Marians ja kl. 13:44, etter faglærers tilbakemelding 06.10 (`tilbakemelding-product-brief.md`):* alt brukeren ser i v1, vises også i demoen, også KI-laget av og på (story 3.4b). Faglærer skrev: «sørg for at alle funksjoner i v1, også KI-laget i av-modus, kan vises der.»

Linje 1258 i taggen:

*Lagt til 2026-10-16 (gruppens beslutning kl. 11:46, instruksjonen kl. 15:59):* demoen skal være mest mulig lik den ekte versjonen. Der demoen ikke kan gjøre det samme, fordi den ikke henter (FR-411), forklarer en boks hvordan det er i den ekte versjonen, gjerne med et bilde som blir stort ved klikk, trykk eller tastatur, ikke bare når musa holdes over. Bildet kan vise hele siden, for eksempel «Min liste» i den ekte versjonen, men lages fra testdata, aldri med ekte kurser (regelen 25.09 under story 3.3 i `epics.md`). For 2.12 betyr det noen ekstra oppdiktede selskaper i demobasen som kan velges, og at valget, «x av 18» og «Dine egne aksjer» virker likt i begge versjonene. Detaljene avgjøres i planen for 2.12.

Linje 1254 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R23):* tillegget 08.10 er ikke bygget per 3.11: demobasen har ingen aksje tatt ut av lista, ingen merket «Utenfor målingen», ingen målte omsetninger og ingen eks.datoer (`src/demo.py`). Det venter på story 2.11 og 2.14, ekstra fra 19.10. Målingen av omsetning (2.13) er bygget, men demoen har ingen målinger.

### FR-412 — Lista over aksjer

Linje 1262 i taggen:

*Lagt til 2026-10-08, Marians beslutning kl. 07:29 (story 2.11 og 2.12).*

Linje 1291 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R22):* ikke bygget per 3.11, story 2.11 og 2.12, ekstra fra 19.10. Oversikten viser de faste 15.

### FR-413 — Måling av omsetning

Linje 1295 i taggen:

*Lagt til 2026-10-08, Marians beslutning (story 2.13).*

Linje 1317 i taggen:

*Endret 2026-10-28 kl. 22:17 (gruppens svar, under story 2.13 og 8.17 i `epics.md`):*
jobben fra story 2.3d kjører målingen etter hentingen med alle kallene som er igjen
den dagen i GMT, også på dager børsen er stengt. Hentingen og nye forsøk får
kallene først, og bonuskvoten brukes aldri. Når hele lista er målt, måles de
eldste målingene på nytt først. Det går foran «etter 3 måneder» og «lar 2 stå
igjen» over.

Linje 1324 i taggen:

*Endret 2026-10-28 kl. 23:19 (gruppens svar, under story 2.13 i `epics.md`):*
før første kall godtas gårsdagens dato i `/api/user` og leses som 0 brukt i dag,
som i hentingen (regel 15), og etter hvert kall må datoen være dagens. Vinduet er
tre måneder bakover fra børsdagen og står ved hvert tall. Det er ingen lås, som
for hentingen: vi kjører ikke noe for hånd mens jobben går. Mangler én av de 15
kursen, går målingen kl. 23:45 med kallene som er igjen, og nye forsøk får
fortsatt kallene først.

Linje 1332 i taggen:

*Endret 2026-11-03 (gjennomgangen 02.11, R3):* rekkefølgen er bygget slik: først de som aldri er målt, i rekkefølgen i lista over Oslo Børs fra `malinger.md` §40, uten aksjene i appens liste, og når alle er målt, den eldste målingen først (`spec-2-13-maalingen-av-omsetning.md`). Det går foran «aksjene i OBX som ikke er i lista, først» over. Fra kl. 23:45 går målingen uansett hvor mange av de 15 som mangler kursen, også når alle mangler (gruppens svar 2026-10-29 kl. 09:20, a).

### FR-414 — Eks.datoer ført for hånd

Linje 1336 i taggen:

*Lagt til 2026-10-08, Marians beslutning kl. 08:06 (story 2.14).*

Linje 1354 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R19):* ikke bygget per 3.11, story 2.14, ekstra fra 19.10.

### 4.5 Meldingsfilter og deduplisering

Linje 1358 i taggen:

*Utenfor v1 (plan B, 28.09). Lagt til 2026-11-03 (gjennomgangen 02.11, R10):* hele delen gjelder meldingene, som er ute av v1 (punkt 1 i §8): FR-501, FR-502, FR-503 og «Resultat av filteret». Epic 6 står i backlog.

### FR-501 — Deduplisering av språkdubletter

Linje 1383 i taggen, ved «2026-09-21.»:

*Merknad 2026-09-26:* kontrollert 2026-09-21 og avkreftet.
   Meldingsobjektet har ikke noe språkfelt (`malinger.md` §7.3), så punkt 2 er
   hovedregelen.

Linje 1397 i taggen:

*Lagt til 2026-10-03 (P9 i kontrollen 26.09):* prinsippet fra `malinger.md` §7, «Hva dette betyr for FR-501»: «Kjennetegnet slår sammen bare når det finnes positivt grunnlag for at det er samme melding. Ved tvil beholdes begge.» Kravet hører til plan A, meldingene, som er utenfor v1.

### FR-503 — Eks.dato som datakilde for utbyttemerking

Linje 1442 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R10):* FR-407 bygger nå på kursserien, ikke på meldinger i `EKS.DATO` (FR-407, punkt 4 i §8).

### 4.6 KI-laget og grensen mot regelbasert kode

Linje 1461 i taggen:

*Skrevet om 2026-09-28 for plan B* (punkt 1 i §8). Kravene for KI-laget over
meldinger står ordrett i 4.6A. FR-601 og FR-605 gjelder begge planene.

Linje 1481 i taggen:

*Avgjort 2026-10-04:* vi spør ikke. Modellen får bare våre egne resultater: fortegn, styrke, retning og antall, og ingen prosenter, forholdstall, kurser eller volumer. Det gjelder også FR-607. `malinger.md` §19 viste at målingene ikke ga bedre tekst. Se punktet under «Å følge opp» i `docs/kilder-og-rettigheter.md`.

Linje 1473 i taggen, ved «regelforklaringen, aldri i stedet for den (FR-602).»:

*Rettet 2026-10-05:* her
sto «KI får bare utledede verdier». Målingene er utledede verdier, men sendes
ikke lenger (avgjort 2026-10-04, under).

Linje 1483 i taggen:

*Lagt til 2026-10-15 (gruppens svar 10 på planen for KI-laget, instruksjonen kl. 15:53):* «antall» gjelder dagsteksten i FR-607 (story 10.6). Grunnlaget for én aksje (story 10.1) er fortegnet for de tre sjekkene, styrken og retningen, uten antall.

Linje 1485 i taggen:

*Lagt til 2026-10-21 (gruppens svar kl. 22:57, under «Prioritering» og story 10.1 i `epics.md`):* fra en ny promptversjon etter uka med logget drift får KI-teksten også hvor lenge signalet har vært slik, tallene som alt står på siden, og retningen på hovedindeksen. Det endrer avgjørelsen 04.10 over fra den nye versjonen, og versjon 2 gjelder til da. Fortsatt ingen råd (NFR-06), hvert tall i teksten kontrolleres mot grunnlaget, og børsometeret (8.6) kommer med når det er bygget. Åpent punkt: avgjørelsen 04.10 om ikke å spørre EODHD bygde på at modellen bare får våre egne resultater, og ingen prosenter, forholdstall, kurser eller volumer («Betingelse 4 og KI-tjenestene (2026-10-04)» i `docs/kilder-og-rettigheter.md`). Om tallene som står på siden, kan sendes til Gemini, Anthropic eller OpenAI med egen nøkkel uten å spørre, er ikke avgjort.

Linje 1487 i taggen:

*Lagt til 2026-10-21 (gruppens svar kl. 23:51, under «Prioritering» og story 10.1 i `epics.md`):* «Bare egne resultater». I den nye promptversjonen får modellen bare våre egne resultater. I tillegg til det den får i dag, fortegnet for de tre sjekkene, styrken og retningen (`ki_grunnlag` i `src/ki_grunnlag.py`), er det hvor lenge signalet har vært slik, retningen på hovedindeksen og børsometeret (8.6) når det er bygget. Modellen får ingen kurser, volumer, prosenter eller forholdstall, heller ikke tallene som står på siden. Teksten kan vise til tallene på siden uten å gjenta dem, og hvert tall i teksten kontrolleres fortsatt mot grunnlaget. Delen av linja 2026-10-21 kl. 22:57 om «tallene som alt står på siden» gjelder ikke lenger, og det åpne punktet i den er lukket. Grunnlaget holder seg innenfor avgjørelsen 04.10 (fortegn, styrke, retning og antall), som står, og EODHD spørres ikke. Fra den nye versjonen får grunnlaget for én aksje et antall (dagene), ulikt linja 15.10 (svar 10 kl. 15:53), der grunnlaget for én aksje er uten antall.

Linje 1489 i taggen:

*Lagt til 2026-10-24 (gruppens svar kl. 15:50 og 16:15, under story 10.2 i `epics.md`):* fra prompten versjon 3 får grunnlaget for én aksje tre antall i tillegg til fortegnene, styrken og retningen: dagene, som er børsdager på rad med samme retning og styrke, til og med dagen, og fra børsometeret hvor mange aksjer i lista som steg og som falt fra børsdagen før. Det får også retningen på hovedindeksen og på bransjen til aksjen i snitt, som steg, falt eller uendret. Det er fortegn og antall, innenfor avgjørelsen over, og fortsatt ingen prosenter, forholdstall, kurser eller volumer.

### FR-601 — Av/på-bryteren er brukersynlig

Linje 1497 i taggen, ved «I v1 slår bryteren av og på KI-teksten i aksjedetaljen (FR-602).»:

*Lagt til 2026-10-02:* Bryteren gjelder også KI-teksten om dagen på forsiden (FR-607). Én bryter styrer begge.

Linje 1501 i taggen:

*Lagt til 2026-10-05:* Bryteren slår av KI-teksten uansett hvilken tjeneste som er valgt (FR-608). Er tjenesten ikke tilgjengelig, også når Ollama ikke kjører, er KI av, og siden sier hvorfor.

Linje 1503 i taggen:

*Lagt til 2026-10-15 (gruppens svar kl. 23:57 på spørsmålet i Utført-linja kl. 23:51, instruksjonen kl. 23:58):* siden sier hvorfor med det loggen kan vise. Har dagen ingen rader i `ki_logg` i det hele tatt, står det «Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk.» Har andre aksjer rader for dagen, men ikke denne, sier siden at teksten for denne aksjen ikke ble laget i hentingen. Den nøyaktige grunnen står i utskriften fra hentingen og i Utført-linja for den kvelden. Med dette regnes kontrollpunktet fra 05.10 om at siden sier hvorfor (FR-601), som oppfylt.

Linje 1499 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R24):* KI-teksten om dagen på forsiden (FR-607) er ikke bygget per 3.11, story 10.6, ekstra fra 19.10.

### FR-602 — Visningen når KI-laget er av

Linje 1518 i taggen, ved «Ellers vises siden som en dag uten KI-tekst.»:

*Rettet 2026-09-29:* her sto
«samme styrke, samme retning og samme fortegn for de tre sjekkene» og
«Målingene lagres ikke i vurderingen (FR-408), så de kan ikke sammenlignes
der.» Målingene lagres fra story 2.1c (FR-408).

Linje 1513 i taggen:

*Lagt til 2026-10-05:* modellnavnet vises også for den lokale modellen, med
tjenesten, for eksempel «gemma4:e4b, lokal».

Linje 1521 i taggen, ved «der.» Målingene lagres fra story 2.1c (FR-408).»:

*Rettet 2026-10-05:* her sto
også «og samme målinger, avrundet som i FR-706». Grunnlaget har ikke målingene
lenger (§4.6, avgjort 2026-10-04), så de sammenlignes ikke. Målingene står
fortsatt i vurderingen (FR-408) og i regelforklaringen (FR-706).

### FR-603 — KI-teksten sier ikke mer enn grunnlaget

Linje 1557 i taggen, ved «teksten.»:

*Lagt til 2026-10-01, Marians beslutning.*

Linje 1570 i taggen:

*Lagt til 2026-10-01:* punkt 4 fanger ord, ikke mening.

Linje 1543 i taggen, ved «de femten».»:

*Rettet 2026-10-05:* her sto «Hvert tall i teksten står i
   grunnlaget, med samme avrunding som i FR-706, eller er et av regelens faste
   tall, som 50 i MA50.» Grunnlaget har ikke målingene lenger (§4.6), og
   `malinger.md` §19 viste feil tall skrevet med ord som kontrollen slapp
   gjennom.

Linje 1548 i taggen, ved «3. Råd. Teksten har ingen ord som gir råd (NFR-06).»:

*Lagt til 2026-10-05:*
   lista har også ord som «alternativ for investorer», «investerings-» og
   «rådgiver», fra tekstene i `malinger.md` §19.

Linje 1557 i taggen, ved «teksten.»:

*Rettet 2026-10-05:*
   her sto «Grunnlaget har bare fortegn og målinger for de tre sjekkene,
   styrken og retningen».

Linje 1559 i taggen, ved «styrken og retningen».»:

*Lagt til 2026-10-05:* lista har også «antyde». En
   forklaring av regelen selv er lov, som «fordi ingen sjekk ga utslag», men en
   årsak utenfor grunnlaget er det ikke. Ordet «resultat» står ikke i lista,
   fordi det i §19 viste til sjekkene og ikke til selskapenes regnskap.

### FR-604 — Logging av KI-bidraget, fra første kjøring

Linje 1583 i taggen, ved «Tjenesten, modell-ID, seed, temperatur og hvordan modellen kjørte, …»:

*(lagt til 2026-10-05)*

Linje 1594 i taggen:

*Lagt til 2026-10-15 (gruppens svar kl. 23:32 på spørsmålene i PR F og G, instruksjonen kl. 23:33):* a) G (story 10.3) flettes i kveld, fordi hentingen for 15.10 er ferdig. b) «lokal» gjelder fortsatt når `OSE_KI_TJENESTE` mangler (svar 5 kl. 15:53 står). c) Hentingen sjekker først at Ollama svarer og har modellen. Gjør den ikke det, skrives ingen rader i `ki_logg` for dagen, og utskriften sier hvorfor og at samme kommando kan kjøres igjen samme kveld, med 0 kall til EODHD. Svarer den, skrives rader som før, også når modellen feiler for en aksje (svar 2). Grunnen: formålet med FR-604, at en tekst ikke kan lages på nytt til man får en man liker, holder, fordi ingen tekst ble laget.

### FR-605 — Promptversjon og modell lagres med hver KI-tekst

Linje 1606 i taggen:

*Lagt til 2026-10-05:* med modellen føres også tjenesten (FR-608), modell-ID,
seed, temperatur og om modellen kjørte med eller uten grafikkort (FR-604). For
den lokale modellen føres også Ollama-versjonen. Prøven i `malinger.md` §19 ble
kjørt med Ollama 0.35.1.

### FR-606 — Relevansskalaen

Linje 1627 i taggen:

*Lagt til 2026-10-06:* Marians beslutning 2026-10-06 kl. 21:11: del 2 av relevanseksperimentet kjøres ikke, og story 9.5 utgår. Grunnen er rettighetene: nyhetene kan brukes privat, men ikke i en app som kan bli tilgjengelig for andre, og henvendelsene om dem er ikke besvart. Del 1 viste at mye av nyhetene kunne vært silt bort, og den brukes i refleksjonsrapporten. Skalaen brukes dermed ikke i v1.

### FR-607 — KI-teksten om dagen på forsiden

Linje 1631 i taggen:

*Lagt til 2026-10-02, Marians beslutning (story 10.6).*

Linje 1635 i taggen:

*Rettet 2026-10-05:* grunnlaget er bare antall og retninger: hvor mange som skilte seg ut, antall per retning, hvor mange som gikk bedre enn hovedindeksen (FR-104), retningen for hovedindeksen, og antall opp per bransje. Ingen prosenter. Her sto «Grunnlaget er bare utledede tall regnet av kursene: hvor mange som skilte seg ut, hvor mange som gikk bedre enn hovedindeksen (FR-104), indeksens endring, og snittendringen per bransje, for dagen og for uka.» Indeksens endring og snittendringen per bransje er prosenter, og sendes ikke (§4.6, avgjort 2026-10-04). Uka er ikke med i det nye grunnlaget; om den skal med som antall, avgjøres i story 10.6.

Linje 1637 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R24):* ikke bygget per 3.11, story 10.6, ekstra fra 19.10.

### FR-608 — Valg av tjeneste

Linje 1641 i taggen:

*Lagt til 2026-10-05, gruppens beslutning 04.10 (§4.6 og `docs/kilder-og-rettigheter.md`, «Betingelse 4 og KI-tjenestene (2026-10-04)»).*

Linje 1649 i taggen:

*Lagt til 2026-10-15 (gruppens svar 5 på planen for KI-laget, instruksjonen kl. 15:53):* `av` er et eget valg i `OSE_KI_TJENESTE`. Da lages ingen KI-tekst, og hentingen går som før. `.env.example` har `av`, og README-en sier hvordan KI slås på. Uten variabelen gjelder `lokal`.

Linje 1647 i taggen:

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* egen nøkkel til Gemini, Anthropic og OpenAI (story 10.7) er v1, fordi briefen v8 nevner den under «Data og kilder» (svaret kl. 16:12). ChatGPT med «Sign in with ChatGPT» (story 10.8) er «Ekstra, hvis tiden rekker».

### 4.6A Plan A: KI-laget over meldinger (utenfor v1)

Linje 1653 i taggen:

*Lagt til 2026-09-28.* Ute av v1 fra 2026-09-28 (plan B, punkt 1 i §8). Dette er
innledningen og kravene fra §4.6 slik de sto før plan B, ordrett. Kravene som
bare gjelder meldinger, har fått en A. FR-601 og FR-605 gjelder begge planene og
står i §4.6. Kommer et ja fra Euronext, bygges plan A oppå plan B.

### FR-606A — Relevansskalaen

Linje 1734 i taggen:

*Lagt til 2026-09-25:* visningsbryteren er bryteren Anbefalt/Alle i FR-203.

### 4.7 Signalstyrke og retning

Linje 1751 i taggen, ved «§9.»:

*Rettet 2026-09-24: her sto «de samme 2 985». §9 sier «Like mange
> aksjedager som §7.4, men ikke de samme».*

### FR-701 — Tre navngitte sjekker

Linje 1768 i taggen:

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.4), godkjent av Marian kl. 12:46:* her sto «Sluttkurs mot 50-dagers glidende snitt» i raden for trend. Trend bruker den utbyttejusterte kursen, som setningen under tabellen sier.

### FR-703 — Signalstyrke

Linje 1798 i taggen:

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.4), godkjent av Marian kl. 12:46:* her sto «Styrken sier hvor kraftig sjekkene slår ut — ikke hvor sannsynlig en kursbevegelse er, og ikke om aksjen bør kjøpes eller selges.» Definisjonen er den samme. Bare forklaringen er endret, så den sier det samme som hjelpen.

### FR-704 — Retning

Linje 1816 i taggen:

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.4), godkjent av Marian kl. 12:46:* her sto «Alle utslag peker opp», «Alle utslag peker ned» og «Utslagene spriker». Retningen forklares med +1 og -1, som ordlista i `designregler.md` §4.

### FR-705 — Terskel for at en aksje skiller seg ut

Linje 1839 i taggen:

*Endret 2026-09-22.* Setningen sa «hver dag» og «i døgnet». Det var en
frekvensgaranti fra modellen der applikasjonen hentet ved oppstart, og den
motsier FR-401 etter omskrivingen samme dag. Poenget setningen gjør, er
**omfanget per henting** — at terskelen ikke begrenser hva som hentes — og det
er uendret.

Linje 1835 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R12):* de to setningene over gjelder plan A. I v1 hentes ingen meldinger (plan B, 28.09), og KI-teksten lages for hver aksje med en vurdering (`src/fetch_prices.py`, story 10.2).

### FR-706 — Synlig begrunnelse i aksjedetaljen

Linje 1863 i taggen:

*Skjerpet 2026-09-21.* Kravet ba tidligere bare om navn og verdi. Det er ikke
nok til å oppfylle kravets eget formål: «Trend +1» kan ikke etterprøves uten å
vite hvor mye over snittet kursen lå. Brukeren ville sett et fortegn og måttet
tro på det — altså nøyaktig den skjulte formelen kravet finnes for å unngå.

### NFR-01 — Daglig drift skal holde seg innenfor API-kvoten

Linje 1888 i taggen:

*Endret 2026-10-01 (OSEBX i v1, Marians beslutning):* hovedindeksen hentes i
samme kjøring (FR-410), så daglig henting koster 16 kall og gir **fire kalls
margin**. Avsnittet over gjelder til story 2.8 er bygget.

Linje 1892 i taggen:

*Lagt til 2026-10-02:* idéen «Måling av omsetning med kall til overs» i §8 bruker marginen bare etter at kveldens henting har gått bra, og lar 2 kall stå igjen. Alle kallene brukes bare når brukeren selv kjører målingen etter at dagen er ferdig.

Linje 1896 i taggen:

*Lagt til 2026-10-02:* lista har opptil 18 aksjer (§8, «Egne aksjer»), så minst 1 kall er igjen hver dag.

Linje 1898 i taggen:

*Lagt til 2026-10-05, gruppens svar kl. 19:17 på planen for story 2.3:* bonuskvoten (`extraLimit`) brukes bare til å fullføre hovedhentingen. Hentekommandoen leser kvoten med `/api/user` før første kall. Er det færre enn 15 kall igjen av dagens 20, men bonuskvoten dekker resten, hentes det likevel, og utskriften sier hvor mange kall som tas fra bonusen. Dekker heller ikke bonusen det, blir det 0 kall. Nye forsøk etter hovedhentingen (story 2.3b) bruker aldri bonuskvoten.

Linje 1900 i taggen:

*Avgjort 2026-10-06, Marians beslutning:* v1 bygges på gratisnivået, og ingen del av v1 krever betaling. Demoen trenger verken konto eller nøkkel, ekte kurser trenger en gratis konto hos EODHD, og KI-teksten lages med den lokale modellen. Gruppen bruker selv gratisnivået, og studentrabatten er undersøkt (`docs/kilder-og-rettigheter.md`, «EODHD: studentrabatt»). En større plan på egen konto, betalte modeller med egen nøkkel og rettigheter til nyheter er valg for den enkelte, ikke krav, fordi sensor og andre skal kunne kjøre appen uten å betale (tilbakemeldingen 06.10, «Kjørbar for sensor» og «Avhengigheter og kostnader»). Kontrollen er README-prøven i 3.4.

Linje 1902 i taggen:

*Lagt til 2026-10-08, Marians beslutning (FR-412, story 2.3 og 2.11):* lista kan ha
opptil 18 aksjer, så kvotesjekken regner med antallet aksjer i lista pluss
indeksen, ikke med 15. 18 aksjer og indeksen gir 19 kall og 1 igjen. Med 15 aksjer
og indeksen er 4 kall igjen til nye forsøk (2.3b), med 18 er det 1. Kvotesjekken
i 2.3 tar antallet fra lista som parameter.

Linje 1908 i taggen:

*Avgjort 2026-10-08 kl. 08:06, Marians beslutning:* regelen fra 05.10 over står.
Bonuskvoten brukes bare til å fullføre kveldens henting, aldri til nye forsøk
(2.3b), målingen av omsetning (FR-413) eller noe annet. Utenom det gjelder
fortsatt aldri flere enn 20 kall i døgnet.

Linje 1913 i taggen:

*Lagt til 2026-10-21 kl. 18:38 (gruppens svar, under «Prioritering» og story 2.12 i `epics.md`):* de 20 kallene i døgnet hos EODHD er fordelt slik: 1 til hovedindeksen, 15 til de 15 aksjene, 3 holdt av til egne aksjer (story 2.12, taket på 18) og 1 i reserve, til et nytt forsøk hvis noe feiler eller til noe annet som trenger et kall. Brukes reserven til noe annet, er det ikke kall igjen til et nytt forsøk den kvelden. Til 2.12 er bygget, kan de 3 brukes til nye forsøk, som hentingen gjør i dag (`kall_til_nye_forsoek` i `src/fetch_prices.py`, som gir 4 med 15 aksjer og indeksen: de 3 og reserven).

Linje 1894 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R2):* fra story 2.13 (`676fbc8b`, 29.10) kjører jobben målingen hver kveld etter hentingen med alle kallene som er igjen den dagen i GMT, og aldri bonuskvoten. Det går foran «lar 2 kall stå igjen» og «bare når brukeren selv kjører målingen» over (FR-413, gruppens svar 2026-10-28 kl. 22:17).

### NFR-02 — Brukeren venter aldri på en henting

Linje 1928 i taggen:

*Endret 2026-09-22.* Kravet lovet opprinnelig en bakgrunnsoppgave med samtidig
visning. Utfallet er uendret — brukeren venter fortsatt aldri — men mekanismen
finnes ikke lenger etter omskrivingen av FR-401, og et krav som beskriver en
bakgrunnsjobb i webserveren, ville ført en utvikler til å bryte AD-10.

### NFR-05 — Norsk i grensesnitt og forklaringer

Linje 1950 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R13):* dedupliseringen i FR-501 er plan A og ute av v1, så den delen av begrunnelsen gjelder ikke v1. Kravet om norsk står.

### NFR-07 — Rådata bevares fra første kjøring

Linje 1964 i taggen:

*Rettet 2026-10-03 (P10 i kontrollen 26.09):* FR-406 gjelder bare kursdata. NewsWeb-delen hører til plan A, som er utenfor v1. Hvilket krav henvisningen skal vise til, avgjøres hvis plan A tas opp igjen.

### NFR-08 — Bare tall vi kan stå for

Linje 1968 i taggen:

*Lagt til 2026-10-01, Marians regel.*

Linje 1979 i taggen:

*Lagt til 2026-10-03, Marians beslutning (FR-411):* oppdiktede tall merkes
«Eksempeltall» på hver side der de vises, og vises aldri sammen med ekte tall.
En side leser enten demobasen eller den ekte basen, aldri begge.

### 6. Datakilder

Linje 1995 i taggen, ved «EODHD /api/news»:

*Rettet 2026-09-24: her sto 10 per ticker og ~80*

Linje 1999 i taggen, ved «nettside.»:

*Rettet 2026-09-24:* vilkårene ble kontrollert 2026-09-21. Euronexts
vilkår dekker NewsWeb ved navn og forbyr automatisert henting uten skriftlig
tillatelse på forhånd; se åpent punkt 1. Faller NewsWeb bort, finnes ingen åpenbar erstatning — E24 er forkastet
på vilkår, og andre norske finansmedier publiserer ikke lenger åpen RSS. Se
åpent punkt 1.

Linje 1995 i taggen, ved «EODHD /api/news»:

*Rettet 2026-09-25: her sto «For flere tickere er tallet ikke målt: ~40 kall for åtte selskaper hvis det er 5 per ticker, ~80 hvis det er 10. Avgjøres av den første forespørselen med to tickere (story 9.4).»*

### 7. Suksessmål

Linje 2060 i taggen:

*Endret 2026-09-22.* Terskelen sa «Ingen manuelle steg». Den målte **to**
egenskaper, og FR-401 har skilt dem fra hverandre:

Linje 2048 i taggen, ved ««Grensesnitt og stabilitet». Se åpent punkt 13.»:

*Rettet 2026-09-24: her sto
bare «KI-bidrag i drift» og «Grensesnitt og stabilitet». «Brukerutfall» og
«Fortsatt bruk» har frist ved prosjektinnlevering.*

Linje 2016 i taggen, ved «Relevanseksperiment»:

*Gjennomført 26.09* (`relevanseksperiment.md` §8). **Del 2** KI-kjøringen, når KI-laget finnes

Linje 2015 i taggen, ved «KI-bidrag i drift»:

*Rettet 2026-10-06, brief v8:* erstattet av «KI-forklaringen» etter plan B. KI-laget forklarer signalet og omklassifiserer ingen meldinger

Linje 2016 i taggen, ved «Relevanseksperiment»:

*Lagt til 2026-10-06:* Marians beslutning 2026-10-06 kl. 21:11: del 2 av relevanseksperimentet kjøres ikke, og story 9.5 utgår. Grunnen er rettighetene: nyhetene kan brukes privat, men ikke i en app som kan bli tilgjengelig for andre, og henvendelsene om dem er ikke besvart. Del 1 viste at mye av nyhetene kunne vært silt bort, og den brukes i refleksjonsrapporten.

Linje 2019 i taggen, ved «Riktige beregninger»:

*(lagt til 2026-10-06, brief v8)*

Linje 2020 i taggen, ved «KI-forklaringen»:

*(lagt til 2026-10-06, brief v8)*

Linje 2021 i taggen, ved «Kjørbar for andre»:

*(lagt til 2026-10-06, brief v8)*

Linje 2043 i taggen:

*Rettet 2026-10-06, brief v8:* «og meldingene som gjelder» er ute med plan B
(§2). Flyten slutter med de tre sjekkene, og KI-teksten når laget er på.

Linje 2051 i taggen:

*Lagt til 2026-10-06, brief v8:* med de tre nye radene har tabellen elleve
mål. «KI-bidrag i drift» er erstattet av «KI-forklaringen», og del 2 av
«Relevanseksperiment» utgår, mens del 1 er gjennomført. Ni mål gjelder, og fem
av dem er bundet til datoer som ikke er fastsatt: «Brukerutfall», «Fortsatt
bruk», «Grensesnitt og stabilitet», «KI-forklaringen» og «Kjørbar for andre».
«Riktige beregninger» gjelder ved hver testkjøring.

Linje 2023 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R26, gruppens svar 02.11 kl. 22:15, B):* «est. uke 45» i raden «KI-bidrag i drift» gjelder ikke lenger. Uke 45 er 2.–8.11, og datoen for demonstrasjonen er fortsatt ukjent (punkt 13 i §8, som står åpent).

Linje 2025 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R27, gruppens svar 02.11 kl. 22:15, C):* «Brukerutfall» står som mål for v1. Brukertesten (story 8.1 og 10.4) er ikke tatt, og den tas senere, uten dato ennå (`docs/brukertest.md`). «Neste uke» i svaret 23.10 kl. 12:29 gjelder ikke lenger.

Linje 2029 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R28, gruppens svar 02.11 kl. 22:15, D):* «Adopsjon» og «Fortsatt bruk» krever bruk som er loggført. Bruken ble ikke logget før 4.11. Fra 4.11 føres én linje for hver dag gruppen bruker appen, i [brukslogga](../../../../docs/brukslogg.md), med dato, hvem, hva vi gjorde i appen og feil vi så. Jobbens logger regnes ikke som bruk.

Linje 2031 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R29):* hvilken uke som teller for «Én ukes drift er logget» i «KI-forklaringen», og antallet rader i `ki_logg` for den, er ikke regnet ut per 3.11, og basen er ikke åpnet i rettingen. Linja føres når det er regnet ut.

Linje 2037 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R30):* README-prøven fra en ren maskin i «Kjørbar for andre» er utsatt til v1 er ferdig bygget (gruppens svar 2026-10-21 kl. 18:33 i `epics.md`), og den tas senest én uke før innleveringen (gruppens svar 2026-10-14 kl. 22:19 og 22:25 i `epics.md`).

Linje 2058 i taggen:

*Rettet 2026-11-03 (gjennomgangen 02.11, R31):* FR-407 er ekstra fra 19.10 og ikke v1 (story 2.6), så den er ikke lenger bundet til en dato i v1.

Linje 2079 i taggen:

*Lagt til 2026-11-03 (gjennomgangen 02.11, R32):* det er lest. Dockerfilen er skrevet (story 3.1, `a2ecee8a`), og migrasjonene kjøres når basen åpnes (`kjoer_migrasjoner=True` som standard i `aapne_base`, `src/lagring_sqlite.py`), ikke som et eget steg. Terskelen for «Drift» holder.

Linje 2033 i taggen:

*Lagt til 2026-11-05 (R29, gruppens svar 5.11 kl. 12:23 og 12:24):* uka som teller for «Én ukes drift er logget», er 29.10–04.11. `data/db/ose.db` er lest skrivebeskyttet. `ki_logg` har 15 rader av slaget `aksje` for hver av børsdagene 29.10, 30.10, 02.11, 03.11 og 04.11, og ingen av slagene `melding` eller `dag`. Hver dag besto alle 15 kontrollen (FR-603) og ville blitt vist, og 0 ble stoppet. Modellen er `gemma4:e4b` (lokal) og promptversjonen `3` alle dagene. 31.10 og 01.11 er helg, uten kurser og uten rader. Uka er logget: 105 rader, alle børsdager har tekster. Loggdelen av story 10.4 står i `spec-10-4-loggdelen.md`.

Linje 2035 i taggen:

*Rettet 2026-11-05 (R29, instruksjonen kl. 16:09):* linja over sier at uka er logget med 105 rader. Det riktige tallet er 75. `data/db/ose.db` er lest skrivebeskyttet på nytt: `ki_logg` har 15 rader for hver av de fem børsdagene 29.10, 30.10, 02.11, 03.11 og 04.11, og ingen for 31.10 og 01.11, som er helg. 5 × 15 er 75. 105 er 7 × 15, altså alle sju dagene i uka ganget med 15, også de to helgedagene uten rader. Regnestykket bak 105 står ikke i sesjonsloggen eller commitene. Alle 75 besto kontrollen (FR-603), og 0 ble stoppet. Resten av linja over stemmer, og uka er logget.

Linje 2027 i taggen:

*Lagt til 2026-11-11 (gruppens svar 10.11 kl. 22:26 og 22:30):* brukertesten er tatt 10.11 med én person, med den ekte versjonen. Personen forklarte uoppfordret hvorfor en aksje skilte seg ut, men brukte over 5 minutter, så «Brukerutfall» er ikke nådd. Målet står som før. Notatene står i `docs/brukertest.md`.

### Motmål

Linje 2090 i taggen:

*Lagt til 2026-10-06:* eksperimentet utgår etter del 1. Marians beslutning kl. 21:11: del 2 av relevanseksperimentet kjøres ikke, og story 9.5 utgår. Grunnen er rettighetene: nyhetene kan brukes privat, men ikke i en app som kan bli tilgjengelig for andre, og henvendelsene om dem er ikke besvart. Del 1 viste at mye av nyhetene kunne vært silt bort, og den brukes i refleksjonsrapporten.

Linje 2093 i taggen:

*Rettet 2026-10-06, brief v8:* KI-laget måles i at tekstene består kontrollen
  i FR-603, ikke i hvor mange det lager.

## Kommentaren om status i frontmatteren

Kommentaren sto i frontmatteren til `prd.md` fra september til 12.11, ordrett:

```yaml
# updated settes fra klokka, aldri for hånd:
#   date +%Y-%m-%dT%H:%M   (lokal tid, samme som memloggen)
# Feltet sto på 2026-09-20 mens fem commits den 21.09 hadde endret dokumentet.
#
# Hvorfor status var draft, og hva som avsluttet den.
#
# «draft» er IKKE en påstand om at dokumentet er uferdig. Det har vært gjennom
# fem gjennomganger og en sjekkliste, og kravene er nummererte og begrunnet.
# Det står som draft fordi ARKITEKTURFASEN KOMMER TIL Å ENDRE KRAV DET
# INNEHOLDER — først og fremst FR-406.
#
# Statusen endres når alle fire er innfridd. Dette er en betingelse, ikke en
# dato; ingen frist løser den ut:
#   1. Åpent punkt 17 (database) er besluttet
#   2. Åpent punkt 18 (Dockerfile) er besluttet
#   3. FR-406 er oppdatert i tråd med 1 og 2
#   4. De to gjenstående [FORELØPIG]-vinduene i §4.7 er målt: de 20 dagene i
#      bevegelsessjekken og de 20 i interessesjekken. De var ikke med i testen
#      i malinger.md §7.4, som låste tre parametre og ikke fem
#
# INNFRIDD 2026-09-22T16:07 — alle fire. Betingelsen står igjen slik den ble
# formulert, ikke slettet: den viser hva som skulle til, og refleksjonsrapporten
# skal kunne lese det. 1 og 2 ble besluttet i arkitekturfasen (spinen AD-3..AD-5,
# AD-9..AD-11). 3 ble skrevet inn samme dag. 4 ble målt mot de 2 985
# aksjedagene, malinger.md §9 — og målingen måtte bytte metrikk underveis, fordi
# den første målte avstand fra 20 og var 0 ved 20 per konstruksjon.
#
# Betingelsen står her fordi en status uten utgangsbetingelse blir stående til
# noen tilfeldigvis tar den opp — samme mekanisme som datoen på
# relevanseksperimentet, som ble stående i uke 41 etter at det som blokkerte
# det var avklart.
```

## Åpne punkter og idéene til v1.1, slik de sto

Hele §8 fra taggen, ordrett. De åpne punktene som gjelder, står i §8 i `prd.md`.

## 8. Åpne punkter

### Må avgjøres før arbeidet går videre

| # | Punkt | Eier | Frist | Blokkerer |
|---|---|---|---|---|

*Lagt til 2026-11-03 (gruppens svar 02.11 kl. 22:15, spørsmål 1 og 2):* punkt 2, 4 og 16 er flyttet til «Utenfor v1» under «Må følges opp», med teksten ordrett. Ingen punkter står igjen i tabellen over.

### Må følges opp

| # | Punkt | Eier | Frist |
|---|---|---|---|
| 13 | **Datoer for demonstrasjon og prosjektinnlevering.** Spørsmål sendt faglærer i Teams 2026-09-22, sammen med spørsmål om leveranselista er fullstendig og om noen BMAD-dokumenter skal leveres inn. **Besvart av hjelpelærer 2026-09-23: ingen dato finnes ennå** — «Bård Inge vil presisere dette». Fire av de åtte suksessmålene i §7 er bundet til disse datoene (*rettet 2026-09-24: her sto «Åtte suksessmål»*), og «est. uke 45» er vår egen estimering — ikke en oppgitt dato. Se `docs/innlevering.md` | Marian | **Avventer Bård Inge** (spurt 22.09, besvart 23.09) |
| 21 | **Hva er emnesidens tredje del?** Emnesiden sier «tre deler», men lister to, og nevner at «delvurdering 3 gir anledning til å demonstrere unike bidrag». Hva den tredje delen er, er ikke oppgitt. Spørres Bård Inge sammen med datoene i punkt 13. Se `docs/innlevering.md`, «Eksamen» | Marian | Sammen med punkt 13 |
| 22 | **Kodegjennomgang som BMAD-steg, én per epic.** `bmad-code-review` kjøres etter hver ferdige epic, første gang etter Epic 1. Emnesiden: «Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har kvalitetssikret koden» — en gjennomgang med flere uavhengige lesere er en del av det, i tillegg til testene og mutantene. Lagt til 2026-09-23. *2026-09-24:* den første gjennomgangen ble gjort 23.09 etter story 1.1–1.3, midt i Epic 1, ikke etter den. Funnene står som forutsetninger i `epics.md` under 1.5b og 2.2. *Rettet 2026-09-26:* her sto «under 1.6 og 2.2». De ble flyttet fra 1.6 til 1.5b 24.09 (`f7e4544`). *2026-09-28:* gjennomgangen etter Epic 1 ble gjort 27.09 (`kodegjennomgang-epic-1.md`). Funnene er rettet i 1.8 og 1.9 eller lagt til 2.1, 2.5 og 4.0. Fristen var «Etter Epic 1». Punktet står åpent, fordi det gjelder hver epic. | Gruppen | Etter Epic 2 |
| 25 | **Dagene Oslo Børs er stengt i 2027.** Fra 2027-01-01 reiser `innevaerende_boersdag`, og dermed `skriv`, til dagene for 2027 er ført inn (punkt 3, og BH2 i gjennomgangen av story 1.6). Når Euronext publiserer kalenderen for 2027, føres dagene inn i `STENGT` i `src/boersdag.py` og i seksjonen Handelskalenderen i `docs/kilder-og-rettigheter.md`, og 2027 legges til i `DEKKEDE_AAR`. Kalenderen for 2026 er merket «© 2025», så kalenderen for 2027 kommer trolig i høst | Marian | 2026-12-01 |

*Lagt til 2026-11-03 (gruppens svar 02.11 kl. 22:15, spørsmål 1, 3 og 5):* 5b og 9 er flyttet til «Lukket» (spørsmål 3), og 6, 8, 11, 12 og 15 til «Utenfor v1» under (spørsmål 1), med teksten ordrett. 13, 21 og 25 står som før (svar B).

*Lagt til 2026-11-03 (gruppens svar 02.11 kl. 22:15, spørsmål 4):* punkt 22: i stedet for én gjennomgang per epic tas én samlet `bmad-code-review` av v1-koden før README-prøven, eier Gruppen. Gjennomgangene per PR står som det de er (`docs/kvalitetssikring.md` §5).

*Lagt til 2026-11-07 (gruppens svar kl. 11:05 og 11:10, story 2.16):* punkt 25: Euronexts kalender for 2027 (IF261106CADE, 06.11.2026) er lastet ned for hånd, lest ut av rådet og sjekket av gruppen: stengt 2027-01-01, 03-25, 03-26, 03-29, 05-06, 05-17, 12-24 og 12-31, og 2027-03-24 er halv handelsdag og regnes som børsdag. Dagene står i seksjonen Handelskalenderen i `docs/kilder-og-rettigheter.md`, med SHA-256. I stedet for å føre inn dagene for hvert år regner appen ut de stengte hverdagene etter reglene Oslo Børs følger, og listene for 2026 og 2027 blir tester regelen må stemme med (story 2.16). Punktet lukkes når 2.16 er flettet.

*Lukket 2026-11-07 (story 2.16, PR #117, flettet i `a1c67c1a`):* punkt 25: appen regner ut de stengte hverdagene for hvert år fra 2026 etter reglene, og listene for 2026 og 2027 fra Euronext er tester. `STENGT` og `DEKKEDE_AAR` er borte, så ingenting må føres inn for 2027, og kveldshentingen stopper ikke 01.01.2027. Etter gruppens svar kl. 15:34 er det ingen øvre grense og ingen ny kontroll av klokka.

### Utenfor v1

| # | Punkt | Eier | Frist | Blokkerer |
|---|---|---|---|---|
| 2 | **KI-terskelen i samlekategorien** — hvor grensen mellom «kan påvirke» og «lite relevant» skal gå. Kan ikke avgjøres på papir; relevanseksperimentet er input. Foreløpig regel står i FR-606. *Plan B 2026-09-28:* gjelder meldingsdelen, som ikke er med i v1. | Gruppen | Utenfor v1 (plan B, 28.09) | Kalibrering av FR-606 |
| 4 | **Hvordan utledes eks.dato?** FR-407 og FR-503 forutsetter at utbyttedager kan identifiseres. **En målt vei finnes, funnet 2026-09-21:** avviket mellom close-endringen og `adjusted_close`-endringen peker ut dagen justeringen skjedde. 38 hendelser over 3 720 dagovergangner, og antallet står stille fra 0,05 til 0,5 prosentpoeng — et rent skille, så terskelen kan begrunnes i stedet for velges. **Konsekvensen er større enn kravet:** FR-407 blir da uavhengig av EKS.DATO-meldinger, og dermed av NewsWeb og punkt 1. Se `begrunnelser.md` §11. *Frist endret 2026-09-24:* sto «Før demonstrasjonen»; story 2.6 bygger merkingen | Gruppen | Ekstra fra 19.10, før 2.6 hvis den bygges. Sto **Før story 2.6** | FR-407, FR-503 |
| 6 | **Usikkerhetskriteriene er skrevet for medieartikler.** Kjennetegn 1 bærer svakt når utstederen selv er avsender | Gruppen | Utenfor v1 (plan B, 28.09). Sto «Før KI-laget implementeres» | – |
| 8 | **Oppstart av tilbakekjøpsprogram** er ekte nyhet, men filtreres bort sammen med de ukentlige statusrapportene | Gruppen | Utenfor v1 (plan B, 28.09). Sto «Før innlevering» | – |
| 11 | **Meldepliktig handel for primærinnsidere** justeres hvis den viser seg å være i hovedsak opsjonsutøvelse | Gruppen | Utenfor v1 (plan B, 28.09). Sto «Etter én ukes drift» | – |
| 12 | **Bekrefte horisont og hendelsestyper** i FR-302, som i dag er antatt | Gruppen | Utenfor v1 (plan B, 28.09). Sto «Før implementasjon» | – |
| 15 | **Plassér kategoriene som havnet i «ukjent»** i riktig bøtte. Krever en ukes drift for å vite hvilke som faktisk dukker opp | Gruppen | Utenfor v1 (plan B, 28.09). Sto «Etter én ukes drift» | – |
| 16 | **Språkgjenkjenningen slår systematisk feil for Vår Energi.** `gjett_spraak` lar ett norsk tegn avgjøre alene, og `VAR` heter *Vår Energi ASA*. Hver engelsk melding derfra bærer «å» i sitt eget firmanavn og leses som norsk, så FR-501 vil beholde den engelske versjonen hver gang selskapet sender et meldingspar. Dette er ikke en kantsituasjon — det er hver gang, for én av de femten, og det vises i en norsk applikasjon. **To forsvarlige veier:** bygge om språkregelen, eller la den stå og forklare avviket i demonstrasjonen. Det som ikke er forsvarlig er at valget tas ved at ingen tar det opp. *Frist endret 2026-09-24:* sto «Før UI-arbeidet starter»; story 6.3 bygger dedupliseringen. *Plan B 2026-09-28:* gjelder meldingsdelen, som ikke er med i v1. | Gruppen | Utenfor v1 (plan B, 28.09) | FR-501, demonstrasjonen |

*Lagt til 2026-11-03 (gruppens svar 02.11 kl. 22:15, spørsmål 1 og 2):* tabellen er ny. Punkt 2, 4 og 16 er flyttet hit fra «Må avgjøres før arbeidet går videre», og 6, 8, 11, 12 og 15 fra «Må følges opp». Teksten i punktene står ordrett. Eier er Gruppen der feltet var tomt eller en plassholder, og fristen som sto før, står i fristfeltet. Punkt 4 er ekstra fra 19.10 (story 2.6), ikke plan B. «–» under Blokkerer er for punktene fra «Må følges opp», som ikke hadde feltet.

### Lukket

Punkter som er avgjort. De står igjen med hva som lukket dem, ikke slettet —
uten det kan ingen se at de var åpne, eller hva som måtte til.

| # | Punkt | Lukket av | Dato |
|---|---|---|---|
| 10 | **Skjevfordeling mot positiv retning**, 68 % i testen. Vurderes mot året, ikke mot femten dager | `malinger.md` §7.4 målte over 199 handelsdager: 60,0 % av aksjedagene med utslag er positive, mot 29,5 % negative. Det korte vinduet lå i en oppgangsperiode og overdrev skjevheten. Flyttet hit 2026-09-24 | 21.09 |
| 7 | **Låsing av signalparametre** mot ~200 handelsdager | `malinger.md` §7.4 låste terskel, volumfaktor og nøytralsone mot 199 handelsdager; §9 låste de to vinduene mot like mange aksjedager, 2 985, forskjøvet én handelsdag. **Punktet anslo 15 kall.** §7.4 kostet 15 kall, og §9 kostet 0, fordi den ble regnet mot lagrede øyeblikksbilder (`malinger.md`). *Rettet 2026-09-26:* her sto «Punktet anslo 15 kall. Det kostet 0 — begge målingene ble gjort mot lagrede øyeblikksbilder» | 21.09 og 22.09 |
| 14 | **Hver story leveres med test**, kjørbar uten API-kall | Skrevet inn som `AD-8` i arkitekturspinen. Praksisen var allerede innført: `tests/conftest.py` sperrer `socket.connect`, og CI kjører uten hemmeligheter | 22.09 |
| 17 | **Database** | SQLite besluttet i arkitekturfasen — spinen `AD-3` til `AD-7`, `AD-16`, `AD-18`, `AD-19`. Rådata forblir filer. **Kontrollert med faglærerstaben 22.09** og bekreftet av assisterende hjelpelærer: «Slik dere beskriver bruken […] bruker dere SQLite som en ordentlig database, ikke bare som enkel fillagring. […] Så ut fra det vi vet nå mener jeg dette er helt innenfor.» Svaret kom ikke fra emneansvarlig og bærer sitt eget forbehold | 22.09 |
| 18 | **Dockerfile** | Arkitekturen besluttet: `AD-9` (ingen data i imaget), `AD-10` (webserveren henter aldri), `AD-11` (to volumer), `AD-12` (hemmeligheter fra miljøet). **Merk at selve filen ikke er skrevet** — punktet gjaldt beslutningen, og bygget står i `docs/innlevering.md` | 22.09 |
| 5 | **Relevanseksperimentet, del 1: utvalgskriterier, innsamling og manuell merking.** Flyttet fram fra uke 41 den 2026-09-21. Uke 41 ble satt mens eksperimentet var blokkert av to ting — om vilkårene tillot språkmodellbruk, og om `/api/news` svarte for `.OL`. **Begge ble avklart 21.09**, men datoen ble aldri flyttet etterpå. Rekkefølge: (a) utvalgskriteriene skriftlig — hvilke åtte selskaper, hvor mange artikler per selskap, og hva som teller som at en artikkel handler om selskapet; (b) innsamlingen, med kalltall-kontrollen som **første** forespørsel: to tickere, og se om `apiRequests` flytter seg 10 eller 15, så kostnaden for resten er kjent før den brukes. Tas fra bonuskvoten `extraLimit`. *Prøvd 2026-09-23, `malinger.md` §11:* kall nummer 21 lyktes og trakk fra bonuskvoten (485 → 484), så den brukes automatisk når dagskvoten er tom. Kalltallet per ticker er fortsatt utledet, ikke målt. *Rettet 2026-09-24:* fristen sto «Etter punkt 17 og 18», som begge ble lukket 22.09. Ny frist fra briefen og §7. Bygges som story 9.4. *Endret 2026-09-25:* kontrollen med to tickere er byttet ut. Den måler hva en forespørsel med flere tickere koster, og det trenger vi ikke når hvert selskap hentes for seg. Prisen for én ticker er målt: 5 kall (`malinger.md` §7.2). I stedet leses `/api/user` før og etter hver forespørsel, og koster en forespørsel noe annet enn 5 kall, stopper vi før neste. Budsjettet er åtte forespørsler, ~40 kall. Kriteriene står i `relevanseksperiment.md` | Del 1 er gjennomført 25.–26.09. Kriteriene ble låst før innsamlingen, og de 48 parene ble merket hver for oss. Vi var enige om 40 av 48 før vi snakket sammen (kappa 0,749), og 35 av 48 par (72,9 %) er ikke «Lite relevant». Se `relevanseksperiment.md` §6–§8. Del 2 venter på KI-laget | 26.09 |
| 3 | **Hvilken kilde gir handelskalenderen?** FR-402 hviler på «forventet børsdag», men ingen kilde er utpekt for hvilke dager Oslo Børs er åpen. **Utvidet 2026-09-24: «inneværende børsdag» er heller ikke definert for helg og helligdager.** FR-408 og spinens skjerping av AD-7 lar `skriv` avvise enhver dato som ikke er inneværende børsdag, men sier ikke hva den er en lørdag eller en helligdag. Definisjonen må være avgjort før story 1.6. Forslag, ikke avgjort: «siste børsdag på eller før dagens dato i Europe/Oslo». *Rettet 2026-09-24:* fristen sto «Før implementasjon», som er passert, og punktet hadde ingen eier | **Avgjort av gruppen 27.09: forslaget er vedtatt.** Inneværende børsdag er siste børsdag på eller før dagens dato i Europe/Oslo. En børsdag er mandag–fredag som ikke står på lista over dager Oslo Børs er stengt, ført for hånd fra Euronexts egen kalender (`docs/kilder-og-rettigheter.md`, seksjonen Handelskalenderen). Halve handelsdager er børsdager. Lista dekker 2026; for en dato utenfor reiser funksjonen en feil i stedet for å gjette, og Marian fører inn dagene for 2027 når Euronext publiserer dem. Funksjonen er ren, ligger i kjernen, får datoen inn og brukes av story 1.6 (FR-408, AD-7), 1.7 (FR-409) og 2.3 (FR-402). Lista kommer inn i koden i 1.6. Når på døgnet dagens rad kan ventes, er fortsatt punkt 23 | 27.09 |
| 24 | **«Ingen rad på en børsdag» betyr ikke alltid at kommandoen ikke ble kjørt.** FR-409 leser det slik, men to tilfeller gir ingen rad uten et hull i driften: kommandoen kjørte før dagens kurs var publisert (punkt 23), eller ett symbol feilet mens de andre ble hentet (`AD-15`). To veier: en fjerde tilstand i FR-409, eller en lagret grunn på raden. Story 2.5 må si hva som skrives for et symbol som feilet. Lagt til 2026-09-24 | **Avgjort av gruppen 27.09: lagret grunn på raden.** Kan kjøringen ikke vurdere en aksje, skriver den likevel en rad for dagen, med grunnen i stedet for vurderingen: symbolet feilet (AD-15), nyeste kurs var ikke fra dagen (FR-402, punkt 23), eller signalet kunne ikke regnes (FR-204). Da betyr ingen rad på en børsdag bare at kommandoen ikke ble kjørt, slik FR-409 leser det. En rad med grunn skriver aldri over en rad med vurdering samme dag. Grunnen er valgt fremfor en egen tilstand fordi hentekommandoen alt vet den, og fordi FR-408s spørsmål da får et svar. Avgjort før story 1.6, ikke 1.7, fordi svaret bestemmer formen på `vurdering`, som 1.6 lager i `0002`. Da slipper tabellen å bygges om senere (spinen, Deferred) | 27.09 |
| 20 | **Hvordan skal FR-408s eget spørsmål kunne stilles?** Kravet begrunner seg med «hva sa løsningen om EQNR for to uker siden?», men ingen visning, kommando eller spørring i v1 svarer på det. Historikken er da **lagret, men ikke besvarbar**. Tre veier: en visning i aksjedetaljen, en egen kommando, eller en direkte spørring mot basen under demonstrasjonen. FR-409 binder alle tre til å bevare skillet mellom «ingen rad» og «styrke 0» | **Avgjort av gruppen 27.09: en visning i aksjedetaljen.** De siste ukenes vurderinger vises dag for dag, lest gjennom `Vurderingslager` og `tilstand`, så skillet i FR-409 står. Valgt fremfor en kommando eller en spørring under demonstrasjonen, fordi svaret da finnes i appen, der brukeren og sensor ser det. Story 2.7 | 27.09 |
| 23 | **Når på døgnet skal hentekommandoen kjøres?** Kl. 19:04 lokal tid 2026-09-23 var dagens sluttkurs ikke publisert: alle 15 serier sluttet 22.09 (`malinger.md` §11). Og en rad hentet mens børsen er åpen, kan bli korrigert i etterkant — MOWI 21.09 fikk volumet justert ned 0,8 % ved neste henting, med sluttkursen uendret. EODHD dokumenterer bare «2–3 timer etter at børsen stenger» (§2). Kjøres kommandoen for tidlig, får brukeren gårsdagens data eller en foreløpig rad; kjøres den to ganger, trekkes det stille fra bonuskvoten. Lagt til 2026-09-23. *Målt 2026-09-24 (`malinger.md` §12):* kl. 21:31 norsk tid hadde alle 15 serier en rad for 24.09, og ingen av de 3 720 felles aksjedagene med øyeblikksbildet fra 23.09 var endret. Når raden kommer mellom 19:04 og 21:31, og om den er endelig, er ikke målt. *Målt 2026-10-07 (`malinger.md` §22):* `close` og `adjusted_close` er endelige når vi henter etter kl. 22, og 6 av 90 rader fikk et litt høyere volum dagen etter (0,08–6,9 %). Når raden kommer, er fortsatt ikke målt. *Målt 2026-10-16 (`malinger.md` §31):* kl. 20:30 og 21:00 hadde EQNR.OL en rad for 16.10, så raden kom før 20:30 den dagen, for ett symbol. Kallene kl. 19:30 og 20:00 ble ikke gjort, så når mellom 19:04 og 20:30, er ikke målt | **Avgjort av gruppen 28.09: på børsdager mellom kl. 22:00 og midnatt, norsk tid.** Kl. 19:04 den 23.09 fantes ikke dagens rad, og kl. 21:31 den 24.09 fantes den for alle 15 (`malinger.md` §11 og §12). En rad hentet etter stengetid var uendret dagen etter, mens MOWI-raden som ble rettet, var hentet mens børsen var åpen. Før midnatt havner hele kjøringen på samme børsdag, slik vurderingen krever (AD-7). Om morgenen har en ny børsdag begynt uten kurs, og en kjøring som kommer for tidlig, bruker 15 kall uten å få dagens rad. Nøyaktig når raden kommer mellom 19:04 og 21:31, er ikke målt. Planen for story 2.3 avgjør om kommandoen advarer eller nekter før kl. 22:00. *Avgjort 2026-10-16, gruppens beslutning kl. 21:09:* hentingen på børsdager flyttes fra kl. 22:00 til kl. 21:00, på betingelse av at radene fra prøvene kl. 20:30 og 21:00 er like raden i kursfila etter kveldens henting (`malinger.md` §31). Er de ulike, tas spørsmålet opp igjen. Endringen bygges som en egen PR søndag 18.10 og gjelder fra mandag 19.10. Mangler noen aksjer raden kl. 21, henter et nytt forsøk dem senere samme kveld med kallene som er igjen (2.3b) (story 2.3 i `epics.md`). | 28.09 |
| 1 | **Vilkårskontroll — to av tre deler lukket 2026-09-21.** *Lukket:* EODHD har svart skriftlig ja til språkmodellbruk, med fire betingelser, og kontrollen av NewsWeb og Euronext er gjennomført. *Åpent:* kontrollen ga et **uttrykkelig forbud** mot automatisert henting uten tillatelse på forhånd. Forespørsel sendt 21.09, **purret 22.09 i samme tråd** — purringen dekker både de fire opprinnelige delene og overføring til en modelltjeneste (punkt 19), og tilbyr et smalere alternativ. Svar avventes. Holder ikke unntaket, må meldingsdelen omdisponeres. **Kontrollert 22.09: EODHDs `/api/news` er ikke en reservekilde** — den koster 75 kall i døgnet for universet mot en kvote på 20, innholdet er syndikert fra tredjepart via Yahoo, og taksonomien er **tematisk og ikke regulatorisk**, så FR-502s tre bøtter måtte bygges om fra grunnen. Vurderingen med tall i `malinger.md` §10. Et nei tar derfor hele KI-laget med seg. *Tillegg 2026-09-24:* et nei tar KI-laget **over meldinger** med seg, ikke hele KI-laget. Plan B (Epic 5B) utløses, og det hentes ikke fra NewsWeb før Euronext har svart (beslutningen 23.09) | **Avgjort av gruppen 28.09: plan B.** Euronext har ikke gitt tillatelse innen 28.09, vår egen frist for å ta stilling uten svar, og taushet regnes som nei for v1. Det hentes ikke fra NewsWeb eller Euronext i v1. Børsmeldingene og de kommende hendelsene er ute av v1, og storyene i Epic 5, 6 og 7 står som plan for en senere versjon. KI-laget forklarer signalet ut fra tall regnet av kursene (Epic 5B, som heter Epic 10 fra 28.09). Svarer Euronext senere, er det en ny beslutning, og plan A bygges da oppå plan B. | 28.09 |
| 19 | **Forespørselen til Euronext ba aldri om å sende innhold til en modelltjeneste.** Vilkårene forbyr å «otherwise transfer any of the Content to any third person», og parentesen strekker det til «others in your company or organisation» — altså svært bredt. Å sende meldingstekst inn i en språkmodell er en slik overføring. Brevet 21.09 beskriver fire ting — Retrieval, Storage, Display, Source code — og **ingen av dem nevner en modelltjeneste**; kontrollert 22.09, null treff på «language model», «LLM», «third person» og «third party» i hele brevet. Manuell innsamling løser klausul 1 om automatisert henting, men **ikke** overføringsklausulen. **Konsekvens: selv et fullt ja på alle fire delene lukker ikke dette.** Det må stilles som eget spørsmål. Kalenderspørsmålet i samme brev hjelper ikke: det ber om «the same answer» og arver dermed de fire overskriftenes rekkevidde, inkludert utelatelsen. **Purret 22.09, og purringen dekker begge deler** — de fire opprinnelige og overføringen — så et kort svar kan ikke lenger se fullstendig ut mens det bare dekker det ene. Purringen tilbyr også et smalere alternativ: et lite, manuelt innsamlet utvalg brukt én gang. Ordrett i `docs/epost-til-euronext.md` | **Bortfalt 28.09 med plan B.** Ikke noe innhold fra Euronext sendes til en modelltjeneste i v1. Reservealternativet for relevanseksperimentet trengs ikke: del 1 er gjort på EODHDs medieartikler (punkt 5). | 28.09 |
| 5b | **Relevanseksperimentet, del 2: KI-klassifiseringen.** Kan ikke gjøres ennå, og det er tre grunner, ikke én: KI-laget finnes ikke som kode, ingen modelltjeneste er valgt, og **betingelse 4 i EODHDs godkjenning — at modelltjenesten ikke trener på innholdet — er udokumentert.** Den må være ført før artikkeltekst sendes inn i en modell, se `docs/kilder-og-rettigheter.md`. *Rettet 2026-10-03 (kontrollen 26.09, P13):* `docs/kilder-og-rettigheter.md` har en fjerde avklaring før del 2: om EODHDs klarering holder når innholdet eies av andre, fordi EODHD er et mellomledd. Eier Marian, frist før del 2 *2026-10-04:* tjenesten er valgt, og betingelse 4 er ført i `docs/kilder-og-rettigheter.md` («Betingelse 4 og KI-tjenestene (2026-10-04)»). Standard er en lokal modell, Gemma 4 E4B. Igjen står at KI-laget ikke finnes som kode, og avklaringen om EODHDs klarering holder når EODHD er et mellomledd. *Lagt til 2026-10-06:* Marians beslutning 2026-10-06 kl. 21:11: del 2 av relevanseksperimentet kjøres ikke, og story 9.5 utgår. Grunnen er rettighetene: nyhetene kan brukes privat, men ikke i en app som kan bli tilgjengelig for andre, og henvendelsene om dem er ikke besvart. Del 1 viste at mye av nyhetene kunne vært silt bort, og den brukes i refleksjonsrapporten. | Gruppens beslutning 2026-10-06 kl. 21:11: del 2 kjøres ikke, og story 9.5 utgår (`9617a701`), som raden alt sa. Flyttet hit etter gruppens svar 02.11 kl. 22:15 (spørsmål 3) | 06.10 |
| 9 | **Kontrollere Alpha Vantages vilkår** for ikke-kommersiell bruk | Alpha Vantage brukes ikke i v1: den er forkastet som hovedkilde (`docs/kilder-og-rettigheter.md`, «Kilder»), og den finnes ikke i `src/`, `tests/` eller README-en (`git grep` 03.11). Avkrysningen i `docs/kilder-og-rettigheter.md` står åpen, med en linje om dette. Gruppens svar 02.11 kl. 22:15 (spørsmål 3) | 02.11 |

*Lagt til 2026-11-03 (gruppens svar 02.11 kl. 22:15, spørsmål 3):* 5b og 9 er flyttet hit fra «Må følges opp», med teksten ordrett.

*Rettet 2026-11-03 (gjennomgangen 02.11, R33):* punkt 18: «Merk at selve filen ikke er skrevet» gjelder ikke lenger. `Dockerfile` og `compose.yaml` er skrevet i story 3.1 (`a2ecee8a`).

*Lagt til 2026-10-20 kl. 15:54:* punkt 23: beslutningen 16.10 kl. 21:09 i raden er snudd. Fra tirsdag 20.10 går hentingen på børsdager fra kl. 22:00 igjen, etter gruppens svar 19.10 kl. 22:19 under story 2.3: raden fra kl. 21 var ikke endelig for DNO (`malinger.md` §37), og en vurdering kan ikke skrives om (AD-7). Byggestoppen er kl. 21:40.

**Punkt 1 og 19 er de to som kan velte datagrunnlaget.** Punkt 1 velter nå bare
én ting, ikke to. Punkt 19 kom til 22.09 og treffer meldingsdelen og KI-laget
sammen. *Tillegg 2026-09-24:* KI-laget betyr her KI-laget over meldinger. Et nei
utløser plan B (Epic 5B), og det hentes ikke fra NewsWeb før Euronext har svart.

*Avgjort 2026-09-28:* plan B. Se punkt 1 og 19 i «Lukket».

*Oppdatert 2026-09-21.* EODHD-halvdelen er lukket: språkmodellbruken er
skriftlig godkjent, og `/api/news` er målt til å svare for `.OL`-tickere.
Relevanseksperimentet kjøres derfor på medieartiklene (her sto «plan A»; *rettet 2026-09-24*, fordi plan B nå betyr Epic 5B) og deler ikke lenger kilde med
meldingsdelen. Det som står igjen, er Euronext: vilkårene som dekker NewsWeb
forbyr uttrykkelig automatisert henting uten tillatelse på forhånd, og
forespørselen om tillatelse ble sendt 21.09 og er ubesvart. Fristen 28.09 er vår
egen frist for å ta stilling uten svar, ikke en dato Euronext har lovet.
Fullstendig
gjennomgang med sitater i `docs/kilder-og-rettigheter.md`.

Av de åpne punktene har 4, 5b, 13, 16, 21, 22 og 25 eier. Punkt 2, 6, 8, 9, 11, 12 og 15 mangler det. Punkt 1, 3, 5, 7, 10, 14, 17, 18, 19, 20, 23 og 24 er lukket. *Rettet 2026-09-28, kveld: punkt 1 og 19 ble lukket med plan B, og punkt 2 har ikke lenger en frist.* *Rettet 2026-09-28: punkt 23 ble lukket.* *Rettet 2026-09-27: punkt 3, 20 og 24 ble lukket, og punkt 25 kom til, med Marian som eier.* *Rettet 2026-09-26: punkt 5 ble lukket.* *Rettet 2026-09-24: punkt 3 fikk eier, punkt 10 ble lukket, og punkt 24 kom til, med Gruppen som eier.* *Rettet 2026-09-23: setningen talte lukkede punkter blant de åpne, og manglet 13, 20 og 21.*

*Rettet 2026-11-03 (R34, gruppens svar 02.11 kl. 22:15):* setningen over gjelder før svaret. Nå står 13, 21, 22 og 25 åpne under «Må følges opp», og alle har eier. 2, 4, 6, 8, 11, 12, 15 og 16 står under «Utenfor v1», med Gruppen som eier. 1, 3, 5, 5b, 7, 9, 10, 14, 17, 18, 19, 20, 23 og 24 er lukket.

**Om nummereringen.** Numrene følger rekkefølgen punktene ble opprettet i, ikke
rekkefølgen i tabellene. Punkt 16 står derfor over sammen med de andre som må
avgjøres, selv om numrene 5–15 ligger i tabellen under. Det er gjort for at
kryssreferanser fra `malinger.md` og gjennomgangene skal forbli gyldige — et
punkt som renummereres, mister sporet tilbake til målingen som begrunnet det.

*Lagt til 2026-11-03:* punkt 16 står nå i «Utenfor v1», sammen med 2 og 4, og tabellen «Må avgjøres før arbeidet går videre» er tom.

*Rettet 2026-10-03 (kontrollen 26.09, P11):* det gjelder ikke gjennomgangene i `gjennomganger/`. De bruker numrene fra før renummereringen 20.09: «punkt 5» i `review-sjekkliste.md` er i dag punkt 10, «åpent punkt 8» i `reconcile-brief.md` er 13, og «åpent punkt 2» i `reconcile-utkast.md` er 6.

**Om eierfeltet.** «Gruppen» er et bevisst valg, ikke en tom rubrikk: vi er to,
og fordelingen gjøres internt etter hva som passer når punktet skal tas. Det
eierfeltet skal sikre, er at punktet har en frist og noen som svarer for den —
ikke at navnet er låst på forhånd. Punkt 6, 8, 9, 11, 12 og 15 har frist, men mangler eier. Punkt 2 mangler eier, men har ikke lenger en frist (plan B). *Rettet 2026-09-28:* her sto «Punkt 2, 6, 8, 9, 11, 12 og 15 har frist». *Rettet 2026-09-26:* her sto «Punkt 2, 3, 6, 8–12 og 15». Punkt 3 har eier, og punkt 10 er lukket, slik oppsummeringen over sier.

*Rettet 2026-11-03 (R34):* alle punktene har nå eier. Punkt 2, 6, 8, 11, 12 og 15 fikk Gruppen da de ble flyttet til «Utenfor v1», og punkt 9 er lukket.

### v1.1 — vurderes etter at v1 er kontrollert

*Lagt til 2026-09-23.* Dette er ideer, ikke krav og ikke stories. Ingen av dem
tas før v1 er kontrollert og virker, jf. prioriteringen 23.09. Hver står med det
den avhenger av.

*Lagt til 2026-10-08, Marians beslutning kl. 07:15–07:29, godkjent kl. 08:04:*
tretten av radene under er flyttet til v1 som «Fast i v1», og merket slik
(`sprint-change-proposal-2026-10-08.md`). Setningen over gjelder resten.

| Idé | Avhenger av | Forbehold |
|---|---|---|
| **Sektorvisning:** endring per sektor for dag, uke og måned | Ingenting nytt. Sektor finnes i `AKSJEUNIVERS`, og tallene regnes fra kursserien | 15 aksjer gir få per sektor: 8 sektorer, der Energi har 4, fire har 2 og **tre har bare én** (Industri, Telekom, Konsum). En «sektor» med én aksje er aksjen selv. Vurderes etter brukertesten (story 8.1). *Lagt til 2026-10-01, Marians beslutning:* søylene per aksje for dagens endring, med bransjesymbol og indeksen som stiplet linje, er tatt inn i v1 (FR-105). Endring per sektor står igjen her *Flyttet til v1 2026-10-08, Marians beslutning:* FR-106, story 8.6 (børsometeret), og periodene i 8.17. |
| **Større aksjeunivers enn 15** | Målingen av `extraLimit` 23.09 (`malinger.md` §11): bonuskvoten trer inn ved kall 21, men den er på 485 og tar slutt. *Rettet 2026-10-03 (kontrollen 26.09, P2):* 485 gjaldt 23.09. Bonuskvoten synker når den brukes. Den var 485 fram til kall 21 den 23.09, 484 etter det (`malinger.md` §11), 464 etter innsamlingen til relevanseksperimentet 25.09 (`relevanseksperiment.md` §6) og 463 etter OSEBX-kallet 30.09 (`malinger.md` §14) | Se regnestykket under. Det skal stå før idéen vurderes |
| **Navigasjon mellom flere skjermbilder** *(utvidet 2026-09-26)*: en knapperad øverst, der knappen for skjermbildet man står på, er fylt. Kandidatene er Markedsoversikt, Min liste, Nyheter og Kalender. En knapp vises bare når skjermbildet finnes | Story 8.2, som skal si hvordan et tredje skjermbilde ville passet inn, uten å bygge det. Min liste er «Favorittmerking av aksjer» fra «Hvis vi rekker». Nyheter krever Epic 6 eller raden «Mediesaker for ett selskap». Kalender er Epic 7, der utbyttedatoer er blant de typiske hendelsestypene (FR-302) | Med to skjermbilder i v1 gir en knapperad lite: aksjedetaljen nås ved å klikke på en aksje. Epic 6 og 7 er blokkert av åpent punkt 1, så uten et ja fra Euronext blir det verken børsmeldinger under Nyheter eller noen Kalender. Min liste er favorittmerking, ikke en personlig portefølje, som står under «Utenfor v1», og med 15 aksjer kan den like gjerne være et filter i oversikten. Utbyttehistorikken fra kursserien er historikk, ikke en kalender, og hører til aksjedetaljen. *Delvis flyttet til v1 2026-09-30:* knapperaden med Markedsoversikt og Min liste bygges i 8.3. Nyheter og Kalender står igjen her |
| **Mediesaker for ett selskap** *(lagt til 2026-09-25)*: de nyeste artiklene fra EODHDs nyhets-API for én aksje, hentet bare når brukeren ber om det. Også for selskaper utenfor de 15, med ticker skrevet inn | Relevanseksperimentet del 1 (story 9.4): hvor mange artikler som finnes per selskap, og hvor mange av dem som faktisk handler om selskapet. For selskaper utenfor universet: et eget skjermbilde uten kurs og signal, jf. idéen om flere skjermbilder | 5 kall per selskap (`malinger.md` §7.2). Kurshentingen bruker 15 av 20, så ett selskap per dag holder seg innenfor dagskvoten, og mer tar av bonuskvoten (§11). Hentes av hentekommandoen, ikke av en knapp i nettsiden: webserveren henter aldri (NFR-02, AD-10). Artiklene vises bare lokalt og publiseres ikke (`docs/kilder-og-rettigheter.md`). Skal KI vurdere relevansen, gjelder EODHDs betingelser fra 21.09, også betingelse 4 |
| **Egendefinert meldingsfilter** *(lagt til 2026-09-25)*: brukeren velger selv hvilke kategorier som vises, i tillegg til Anbefalt og Alle (FR-203) | Story 6.5, og en brukertest som viser at noen savner det | Rundt ti kategorier, og valgene må lagres. Hvert valg koster tid i hovedflyten, som skal gå på under fem minutter (§7, «Brukerutfall»). Tas ikke inn uten at en test viser behovet |
| **Merk det som er nytt siden forrige henting** *(lagt til 2026-09-25)*: meldinger som har kommet siden forrige henting, merkes som nye | At meldingslageret (story 6.1) lagrer når hver melding ble hentet første gang | Svarer rett på spørsmålet i briefen: «hva beveget seg i går, hvorfor». Ingen kall og ingen KI *Flyttet til v1 2026-10-08, Marians beslutning:* som Marian bestemte 02.10 kl. 23:30: et merke under signalstyrken når den har endret seg siden forrige lagrede børsdag, regnet av lagrede vurderinger, ikke meldinger (FR-107, story 8.12). |
| **Lenke til selskapets side på NewsWeb** *(lagt til 2026-09-25)*: én lenke fra aksjedetaljen, så alle børsmeldingene er ett klikk unna, også de som er filtrert bort | Ingenting nytt. Lenken henter ingenting | Vurderes allerede 28.09 hvis Euronext sier nei eller ikke svarer. Da har aksjedetaljen ingen meldinger, og lenken er det eneste som viser dem (åpent punkt 1). Adressen må slås opp før den bygges. *Tatt inn i v1 28.09 (plan B).* Adressen og det Euronexts vilkår sier om lenker, slås opp av en av oss før lenken bygges *Lagt til 2026-10-06:* bygges ikke. Euronexts vilkår forbyr lenker uten tillatelse, og vi ber ikke om tillatelse fordi brevet 21.09 og purringen 22.09 ikke er besvart. Aksjedetaljen lenker til selskapets investorside og nevner NewsWeb uten lenke (Marians beslutning 06.10 kl. 20:42) |
| **Sjekk 2 og 3 synlige i grafen** *(lagt til 2026-09-25)*: volumsøyler under kursgrafen, med en strek for medianvolumet, så sjekk 3 (interesse) synes slik MA50-linjen viser sjekk 1. Eventuelt også et bånd for sjekk 2 (bevegelse) | Ingenting nytt. Volumet finnes i `Kursrad`, og tegningen er samme SVG som i dag (`graf.py`). Tas stilling til i UX-gjennomgangen (8.2), etter brukertesten (8.1) | FR-202 sier at volatilitetsbånd og volumsøyler ikke tegnes i v1, så å ta dem inn er en endring av FR-202. Streken må være samme median, over samme vindu, som sjekk 3 regner med, etter samme prinsipp som i FR-202. Story 8.2 skal ikke ende i ny funksjonalitet, så søylene må begrunnes som en forbedring av forklaringen i FR-706, ellers hører de til v1.1 *Flyttet til v1 2026-10-08, Marians beslutning:* FR-202 med Rettet-linje, story 8.7. |
| **Signaldager i grafen** *(lagt til 2026-09-25)*: kursgrafen markerer dagene med sterkt signal, så man ser hvordan signalet har oppført seg over tid | Vurderingslageret (1.6) og at hentekommandoen skriver vurderingen hver dag (2.5). Historikken bygges opp fra første daglige kjøring | Bare visning. En studie av om signalene slår markedet er utenfor v1. Med få ukers historikk ved demonstrasjonen blir det få markeringer *Flyttet til v1 2026-10-08, Marians beslutning:* FR-206, story 8.8. Vurderingene finnes fra 02.10. |
| **Hjelp bak et spørsmålstegn** *(lagt til 2026-09-25)*: et «?» på begge skjermbildene åpner et lite vindu som forklarer begrepene og symbolene appen viser: sluttkurs og endring, utbyttejustert kurs, signalstyrke 0–3, retningen (↑ Positiv, ↓ Negativ, ↔ Blandet, – Ingen eller Ukjent), de tre sjekkene (trend med 50-dagers snitt, bevegelse og interesse), «data hentet» og «Uten data». Vinduet sier også at signalene ikke er investeringsråd (NFR-06) | Ingenting nytt. Fast tekst, uten nettkall og uten KI, og det kan lages med HTML alene, uten et nytt bibliotek. Bør bygges før brukertesten (8.1), så testen viser om hjelpen blir brukt | Forklarer bare det appen faktisk viser. P/E og andre nøkkeltall fra regnskapet ligger utenfor v1 («fundamental- og verdimodell»). Retningen forklares med ordene fra FR-704, ikke med «opp» og «ned», som ble fjernet fordi de inviterer til å lese pilen som kursbevegelse (`markedsoversikt.py`). Hjelpen skiller «Ingen» fra «Ukjent», slik FR-101 gjør. Tall i teksten, som 50 dager, hentes fra de samme parametrene som beregningen (`Parametre` i `signalberegning.py`), og en test krever det. Ellers kan hjelpeteksten si én ting mens koden gjør en annen, den samme feilen som story 3.3 skal hindre mellom README og den tomme siden. *Flyttet til v1 2026-10-01:* story 8.0b (Marians beslutning). |
| **Utbyttehistorikk i aksjedetaljen** *(lagt til 2026-09-26)*: hvor mange utbyttedager aksjen har hatt det siste året, og datoen for den siste, så man ser om selskapet betaler hvert kvartal, hvert halvår eller én gang i året | Story 2.6 (FR-407), som finner dagene i kursserien. Ingen nye kall og ingen ny kilde | Et ja/nei-merke («utbytteaksje») ville ikke skilt aksjene fra hverandre: alle 15 hadde minst én hendelse i målingen (`begrunnelser.md` §11). Metoden ser justeringer, ikke utbytter, og en splitt gir samme utslag, så grensesnittet kan bare bruke ordet *utbytte* hvis en kilde sier det (samme sted, forbehold 1). Vinduet er ett år, så et selskap som betaler én gang i året, kan i perioder stå med null. Historikken sier ingenting om neste utbytte, og den skal ikke formuleres som et råd (NFR-06) *Flyttet til v1 2026-10-08, Marians beslutning:* vist i kursgrafen som justeringsdager, uten ordet «utbytte» (FR-407, story 8.14). |
| **Kommende eks.dato i oversikten** *(lagt til 2026-09-26)*: aksjer med eks.dato de nærmeste dagene får et merke i markedsoversikten, så det synes før man handler, ikke bare i aksjedetaljen | Epic 7 (FR-301–FR-303). Utbyttedatoer er blant hendelsestypene FR-302 regner med, men horisonten og typene er antatt (åpent punkt 12) | Kursserien kan ikke gi dette: metoden bak FR-407 finner dagen først når den har skjedd (`begrunnelser.md` §11, forbehold 2). EODHDs kalender svarer 403 på gratisnivået (`docs/kilder-og-rettigheter.md`). Epic 7 er blokkert av åpent punkt 1 (Euronext). Et nei stryker epicen, og idéen med den. Merket vises når appen åpnes. Et varsel på e-post eller telefon ville krevd kontaktopplysninger og noe som kjører uten at brukeren ber om det, og er ikke med her *Flyttet til v1 2026-10-08, Marians beslutning:* kl. 08:06, vist i kursgrafen, ført for hånd fra selskapenes egne investorsider og ikke fra Epic 7 (FR-414, FR-207, story 2.14 og 8.18). Vilkårene for hvert selskap føres i `docs/kilder-og-rettigheter.md` før datoen tas inn. |
| **Høy, lav og omsetning i aksjedetaljen** *(lagt til 2026-09-26)*: høyeste og laveste kurs siste børsdag, og omsetningen i kroner, øverst i aksjedetaljen | Ingen nye kall: EODHDs svar har allerede open, high og low (`begrunnelser.md` §11), men adapteren (`eodhd.py`) tar bare med close, adjusted_close og volume. `Kursrad`, adapteren og lageret må utvides | FR-101 låser markedsoversikten til fem kolonner, så dette hører til aksjedetaljen. Høy og lav vises ved siden av sluttkursen, ikke i grafen, som tegnes på adjusted_close (FR-201). Omsetning regnet som volum ganger sluttkurs er et anslag, ikke børsens eget tall, og må merkes slik. *Rettet 2026-10-01 (NFR-08):* omsetningen tas ikke med, fordi volum ganger sluttkurs bare er et anslag. Før høy og lav vises, sammenlignes noen dager for hånd med Oslo Børs' egen side. Siden leses av en av oss og hentes aldri av programmet. *Flyttet til v1 2026-10-07, Marians beslutning kl. 23:11:* story 2.10 og 8.5. Omsetningen er fortsatt ute. |
| **Lær noe nytt** *(lagt til 2026-09-26)*: en liten boks i markedsoversikten med ett kort tips om aksjer per dag, for eksempel hva utbyttejustert kurs, medianvolum eller eks.dato betyr. Tipsene står i en fast liste. Dagens tips velges ut fra datoen, eller ut fra dagens tall når et tips passer, for eksempel tipset om medianvolum når en aksje har uvanlig høyt volum | KI skriver utkast til lista, og vi kontrollerer og retter hvert tips før det tas inn. Ingen nettkall og ingen KI når siden vises. Kan dele tekst med «Hjelp bak et spørsmålstegn» | Hvert tips må være riktig og kontrollert, og det skal ikke kunne leses som et råd (NFR-06). Tall i teksten hentes fra de samme parametrene som beregningen, slik som i hjelpen. Et nytt KI-tips hver dag er valgt bort: da når teksten skjermen uten at noen har lest den, og det krever modelltjenesten fra Epic 4. Bør bygges sammen med hjelpen, før brukertesten (8.1), så testen viser om noen leser den *Rettet 2026-10-03 (P12 i kontrollen 26.09):* «før brukertesten (8.1)» gjelder ikke lenger. Innledningen til tabellen sier at ingenting tas før v1 er kontrollert, og bare hjelpen er flyttet til v1, som story 8.0b. «Lær noe nytt» blir stående her. *Flyttet til v1 2026-10-08, Marians beslutning:* FR-109, story 8.13. |
| **Retning og type for nyheter** *(lagt til 2026-09-26, fra merkingen i 9.4)*: i tillegg til relevansen (FR-606) viser nyheten mulig retning (positiv, negativ, blandet eller uklar) og type (for eksempel resultat, kontrakt, oppkjøp, analytikervurdering eller sektor) | Relevanseksperimentet (story 9.4). Børsmeldingene har allerede kategori fra NewsWeb (Epic 6), og EODHDs nyheter har feltene `sentiment` og `tags`, som ble skjult under merkingen (`relevanseksperiment.md` §4) | EODHDs godkjenning gjelder å sende tekst til en språkmodell «solely to classify company relevance» (`docs/kilder-og-rettigheter.md`). Retning og type fra vår egen KI krever derfor et nytt spørsmål til EODHD. Retning må ikke kunne leses som et råd (NFR-06). Kriteriene i del 1 endres ikke: der merkes bare relevans, slik det ble bestemt før innsamlingen |
| **Egne aksjelister** *(lagt til 2026-09-30)*: hver bruker velger sine egne aksjer, opptil 18, og kan bytte underveis. *Rettet 2026-10-02:* samme grense som i «Egne aksjer». Her sto «opptil 15». Appen kjører lokalt, og hver bruker har sin egen gratiskonto hos EODHD med 20 kall i døgnet. Vilkårene forbyr å dele en konto med andre, også innen grupper (`docs/kilder-og-rettigheter.md`), så gruppens nøkkel kan ikke deles. Færre aksjer bruker færre kall. Ferdige lister å starte fra: dagens 15 og én liste per bransje, som gruppen lager og måler én gang. Innenfor lista kan appen vise for eksempel dagens og ukens mest omsatte, regnet av kursene som allerede er hentet | At `aksje` får aktiv fra og til, så en aksje som byttes ut, blir stående med historikken sin (AD-21 lar ikke en aksje med rader slettes). At regelen i AD-21 om at `aksje` og `AKSJEUNIVERS` er like, erstattes av at lista leses fra basen. En måte å velge og bytte på, med kontroll av tickeren. Og at kriteriet i §3 sjekkes for hver aksje. Gratisnivået gir ett års kurser i ett kall (`malinger.md` §2), så en ny aksje får signal med en gang | Parametrene er testet på dagens 15 (AD-13), så en ny liste bør måles før grensene brukes på den. Trolig har få bransjer 15 aksjer over kriteriet i §3. Det er ikke målt, og målingen koster kall. Lister for hele børsen, som mest omsatt, flest nyheter eller små selskaper på vei opp, krever data for langt flere aksjer enn 20 kall rekker til: bulk-endepunktet koster 100 kall (`begrunnelser.md` §7), og nyheter koster 5 kall per aksje (`malinger.md` §7.2). Små selskaper faller dessuten ofte under kriteriet i §3. Forslag fra KI om hvilke aksjer man bør følge, er ikke med, fordi det ligger for nær et råd (NFR-06). Vilkårene gjelder personlig bruk. *Lagt til 2026-09-30, Marians beslutning:* en aksje under kriteriet i §3 stoppes med en forklaring som viser median omsetning og kravet. Vil brukeren likevel ha den, legges den til og merkes «Under kravet» overalt der den vises. Første målerunde, for sjømat, står i malinger.md §13. *Rettet 2026-10-02, Marians beslutning:* stoppet ved kriteriet i §3 fra 30.09 gjelder ikke lenger. Appen sier hva signalet er målt på: de 15, som omsettes for 32 til 920 MNOK om dagen (§3). En aksje som omsettes mindre, kan velges og merkes «Utenfor målingen» overalt, i grått, fordi gult betyr 3 av 3 (designregler.md §3). Omsetningen står før brukeren velger når den er målt fra før, ellers etter hentingen, som måler den med samme kall. Utledede tall er ikke EODHDs data (svaret 21.09). *Flyttet til v1 2026-10-08, Marians beslutning:* kl. 07:29: de 15 kan byttes helt ut, og lista kan ha opptil 18 aksjer valgt fritt (FR-412, story 2.11 og 2.12). |
| **KI-tekst om dagen på forsiden** *(lagt til 2026-10-01)*: noen setninger under tabellen om hele børsdagen: hvor mange som skilte seg ut, hvilke bransjer som trakk opp eller ned, og hvordan dagen var mot uka. Samme bryter som KI-teksten i aksjedetaljen | Epic 10, altså grunnlaget, loggen (FR-604), kontrollen (FR-603) og bryteren (FR-601), og at story 10.4 har vist om KI-teksten hjelper. Grunnlaget er bare utledede tall regnet av kursene: hvor mange som skilte seg ut, og snittendringen per bransje for dagen og for uka. Kommer OSEBX med, kan indeksens endring også stå i grunnlaget. Teksten lages én gang i hentekommandoen, med ett kall til modellen per børsdag | FR-601 sier at bryteren i v1 gjelder KI-teksten i aksjedetaljen, så den må da gjelde begge steder. Kontrollen i FR-603 gjelder også her, med alle 4 punktene, og grunnlaget vises ved teksten. Et spørsmål til EODHD om plan B bør også dekke dette grunnlaget. Teksten gir ikke råd og spår ikke (NFR-06) *Flyttet til v1 2026-10-02, Marians beslutning:* FR-607 og story 10.6. Den venter ikke på at 10.4 har vist om KI-teksten hjelper. |
| **Endring i kroner** *(lagt til 2026-10-01)*: endringen fra forrige børsdag vises også i kroner. I markedsoversikten står kronene på en mindre linje under prosenten, i samme celle. I aksjedetaljen står de ved prosenten, sammen med høy og lav fra raden «Høy, lav og omsetning i aksjedetaljen» | Ingenting nytt. Kronene regnes av `adjusted_close` for de to siste børsdagene, de samme tallene som prosenten (`endring_i_prosent`). Ingen nye kall og ingen endring i basen | FR-101 sier nøyaktig fem kolonner, så kronene står i samme celle som prosenten, slik tidsstempelet står under selskapsnavnet, og FR-101 må endres før idéen bygges. Kronene regnes på samme justerte kurs som prosenten, så de to peker alltid samme vei. På en utbyttedag blir kronene derfor ikke lik forskjellen mellom de to sluttkursene og kan avvike fra børsens egne sider. Dagen merkes etter FR-407. Sorteringen i FR-102 er fortsatt på prosent: 5 kr er 2 % av 250 kr, men 10 % av 50 kr. *Flyttet til v1 2026-10-07, Marians beslutning kl. 23:11:* story 2.10 og 8.5. Omsetningen er fortsatt ute. |
| **Innstillinger øverst** *(lagt til 2026-10-01)*: en knapp «Innstillinger» i knapperaden på alle sider, med «Vis hjelp» og «Vis KI-tekst». Valgene gjelder alle sidene og lagres i basen på samme måte som merkingen i Min liste (8.3), så de huskes | Hjelpen (8.0b), KI-teksten (Epic 10) og en tabell for innstillinger i basen | FR-601 sier at bryteren skal kunne brukes under demonstrasjonen mens noen ser på, så hver KI-tekst beholder sin egen bryter ved teksten. Begge styrer samme valg. Ingen innlogging: valgene gjelder maskinen *Flyttet til v1 2026-10-08, Marians beslutning:* FR-110, story 8.10. |
| **Omvisning på alle sidene** («Vis meg rundt») *(lagt til 2026-10-01)*: en knapp som viser siden steg for steg, med fast tekst vi har skrevet og sjekket | Hjelpen (8.0b), som omvisningen deler tekstfil med, og at sidene finnes: først markedsoversikten og aksjedetaljen, så Min liste (8.3), og børsometeret hvis det blir bygget | Uten KI. Tall i teksten hentes fra `Parametre`, som i hjelpen. En test sjekker at hvert steg peker på noe som finnes på siden *Flyttet til v1 2026-10-08, Marians beslutning:* FR-109, story 8.9. |
| **Egne aksjer** («Følg en aksje») *(lagt til 2026-10-01)*: opptil 3 aksjer i tillegg til de 15, valgt av brukeren og merket «Egen». Hver hentes med samme nøkkel og ett av de fem ekstra kallene, så de er gratis og krever ingen konto; appen har ingen innlogging. Stjernen i Min liste virker også på dem, og hjelpen forklarer dette. Er en aksje under kriteriet i §3, gjelder Marians beslutning i raden «Egne aksjelister»: først en forklaring, og merket «Under kravet» hvis brukeren velger den likevel | At `aksje` kan ha opptil 3 aksjer utenom AKSJEUNIVERS, samme endring av AD-21 som «Egne aksjelister» trenger. Kriteriet sjekkes med ett kall per aksje, som i malinger.md §13, der Bakkafrost var over kravet | Hver aksje tar ett av de fem kallene i NFR-01, så 3 gir 2 kall i margin, og 1 med OSEBX i tillegg. Marians beslutning 01.10: flest mulig, og taket settes ned hvis marginen blir for liten i drift. Grensene i signalet er målt på de 15 (AD-13), og det må stå ved aksjen. *Rettet 2026-10-01:* OSEBX er nå i v1 (FR-410), så det er fire ekstra kall, og 3 egne aksjer gir 1 kall i margin. *Rettet 2026-10-02:* «Under kravet» er erstattet av «Utenfor målingen», se «Egne aksjelister». *Lagt til 2026-10-02 kl. 19:01, Marians beslutning:* én grense for hele lista: opptil 18 aksjer, de 15 og opptil 3 egne. Appen viser plassene som er brukt, for eksempel «16 av 18 aksjer», så det spiller ingen rolle om brukeren legger til én eller flere. 18 aksjer og hovedindeksen gir 19 kall, og 1 er igjen til en ny kjøring (NFR-01). 20 aksjer ville trengt 21 kall. *Flyttet til v1 2026-10-08, Marians beslutning:* som del av lista på opptil 18, der alle 18 er frie (FR-412, story 2.11 og 2.12). «Egen» avgjøres i planen for 2.12. |
| **Måling av omsetning med kall til overs** *(lagt til 2026-10-02, Marians beslutning)*: når kveldens henting har gått bra, måler den median omsetning for nye aksjer med kallene som er til overs, og lar 2 stå igjen til omkjøring. Vil man bruke alle kallene, kjører man målingen selv når man er ferdig for dagen. Den nekter hvis kveldens henting ikke har gått bra, og sier først hvor mange kall den bruker. Aksjene i OBX som ikke er blant de 15, måles først, så resten. Hver aksje måles på nytt etter 3 måneder, og datoen står ved tallet | En tabell for median omsetning og dato per symbol, i en ny migrasjon. Kvotesjekken før målingen. OBX-lista ført inn for hånd | 1 kall per aksje (malinger.md §13): med 1 egen aksje blir det 1 måling per kveld, uten egne 2. *Lagt til 2026-10-02:* med 2 eller 3 egne aksjer blir det ingen måling om kvelden, fordi bare 2 eller 1 kall er igjen etter hentingen, og 2 skal stå igjen (raden «Egne aksjer»). Kjører brukeren målingen selv med alle kallene, måles 2 eller 1, og den sier først at ingen blir igjen til en ny kjøring. Euronext beskriver OBX som de 25 mest omsatte på Oslo Børs, regnet over seks måneder og revidert i mars og september (https://www.euronext.com/en/news/obx-index-0). Det er en ny kilde, lest av et menneske, ikke hentet av programmet. Webserveren henter aldri (AD-10), og rådata committes aldri (regel 10) *Lagt til 2026-10-03, Marians beslutning 02.10 kl. 23:26:* på dager uten henting, som lørdag og søndag, kan alle 20 kallene brukes til måling. *Flyttet til v1 2026-10-08, Marians beslutning:* FR-413, story 2.13. Bonuskvoten brukes aldri til målingen (NFR-01). |
| **Flere ferdige lister og filter på signalet** *(lagt til 2026-10-02, idé fra Marian)*: «De 15 mest omsatte» som ferdig liste når OBX er målt, og et filter på forsiden for 3 av 3 med positiv eller negativ retning | Målingen i raden over, og «Egne aksjelister» for å bytte liste | En liste på 18 aksjer går innenfor kvoten, men gir 1 kall i margin og ingen egne aksjer. *Rettet 2026-10-02:* klarere ordlyd. Her sto «18 aksjer går i kall». «De 15 mest omsatte» har ikke kravet om minst åtte sektorer i §3. *Rettet 2026-10-02:* §3 sier «sektorer». Her sto «bransjer». Filteret virker bare innenfor lista som er aktiv: hele børsen krever kurser for alle aksjene hver dag, og bulk koster 100 kall (NFR-01). Filteret heter ikke «topp», fordi styrken verken er et råd eller en sannsynlighet (NFR-06, FR-703) *Flyttet til v1 2026-10-08, Marians beslutning:* FR-108 og FR-412, story 8.11. |

**Regnestykket for et større univers.** Det er regnet 23.09 fra målte tall: én
henting per døgn, ett kall per symbol (§2), dagskvote 20, og bonus 484 etter
kall 21. **Det forutsettes at bonusen ikke fylles på. Det er ikke kjent.**

*Rettet 2026-10-03 (kontrollen 26.09, P2):* regnestykket bruker 484, tallet 23.09. Bonuskvoten synker når den brukes. Den var 485 fram til kall 21 den 23.09, 484 etter det (`malinger.md` §11), 464 etter innsamlingen til relevanseksperimentet 25.09 (`relevanseksperiment.md` §6) og 463 etter OSEBX-kallet 30.09 (`malinger.md` §14).

| Symboler | Kall per henting | Fra bonus per døgn | Bonusen varer |
|---:|---:|---:|---|
| 15 | 15 | 0 | Urørt. Margin 5 kall per døgn |
| 20 | 20 | 0 | Urørt, men **margin 0**: hver ekstra kjøring tar fra bonus |
| 25 | 25 | 5 | 96 døgn (484 / 5) |
| 30 | 30 | 10 | 48 døgn (484 / 10) |

*Rettet 2026-10-01:* med hovedindeksen i v1 (FR-410) koster hentingen ett kall
mer enn antall aksjer. 15 aksjer gir 16 kall og margin 4.

**Antall rader per skjermbilde avgjøres ikke her.** 15 er valgt av kvoten, ikke
av skjermen. Om oversikten er for tett, er et spørsmål til brukertesten (story 8.1).

## Endringer etter 12.11

Linjene fra 8.26 (FR-108) og 3.7 (§4.6, FR-608) kom inn med main 13.11 og står her ordrett. Kravteksten i `prd.md` sier det samme.

*Rettet 2026-11-11 (gruppens ønske 11.11 kl. 17:48, story 8.26):* filteret er tatt bort. Raden «Alle», «3 av 3 positiv» og «3 av 3 negativ» under «Alle | Min liste» viste ikke noe tabellen ikke alt viser under «Skilte seg ut», og med den gikk linja om filteret, lenken til dem som fikk 2 av 3 og adressene `?signal=`. At signalstyrken ikke er et råd om å kjøpe eller selge, står fortsatt synlig i innledningen på oversikten (NFR-06). Rådet var enig.

*Lagt til 2026-11-12 (gruppens svar 12.11 kl. 16:32, story 3.7):* `.env.example` har nå `lokal`, så KI-teksten står på i en ny installasjon, som standarden over sier. Svarer ikke Ollama, lages ingen KI-tekst, hentingen sier hvorfor, og kursene hentes som før (NFR-04). Første gang den ekte versjonen startes med dobbeltklikk på Windows, tilbyr startskriptet å hente Gemma eller å bruke egen nøkkel (svarene kl. 16:41 og 16:46). En `.env` som finnes fra før, endres ikke.

*Avgjort 2026-11-12 kl. 20:04 og 20:06 (gruppens svar på spørsmål 14 og 15 i spesifikasjonen for 9.11):* FR-111, Min liste, er et nytt krav med konsekvenser, i kjernen og bygget. «De 15 mest omsatte» står i FR-412 som ferdig liste, ekstra, og bygges i natt som egen story. Rådet anbefalte alt utenom at lista bygges, som gruppen valgte.

*Avgjort 2026-11-12 kl. 20:09 og 20:10 (gruppens svar):* «Lær noe nytt» kommer ikke i v1, og de åtte kravene som sto som ekstra og ikke bygget, står som «senere»: endringen i kroner under prosenten (FR-101), merket for endret signalstyrke (FR-107), «Lær noe nytt» (FR-109), høy og lav og endringen i kroner (FR-203), «Se nærmere» (FR-205), kommende eks.dato i kursgrafen (FR-207), eks.datoer ført for hånd (FR-414) og «Sign in with ChatGPT» (FR-608). «Ekstra» er det som er bygget utover briefen. Rådet anbefalte det.

*Avgjort 2026-11-12 kl. 20:21 og 20:40 (gruppens ønske og svar):* en språkrunde gjennom hele `prd.md` på bokmål, uten at meningen, ID-ene, tallene eller ankrene endres. Konsekvensene er punktlister. Sluttkursen og den justerte sluttkursen er skrevet med vanlige ord, og kodeordene står bare i ordlista, FR-406 og FR-408. Overskriften i FR-302 har «fram», og det gamle ankeret står. Punkt 22 i §8 har fristen «Før innleveringen». Rådet anbefalte det.
