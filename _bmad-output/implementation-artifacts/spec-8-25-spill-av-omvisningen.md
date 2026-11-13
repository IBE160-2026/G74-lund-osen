---
title: 'Story 8.25: «Spill av omvisningen» ved «Vis meg rundt»'
type: 'feature'
created: '2026-11-11'
status: 'done'
route: 'dispatch'
baseline_commit: 'd6e3b4a3'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-9-vis-meg-rundt.md'
---

Skrevet 11.11 i instruksjonen kl. 23:02 10.11, etter gruppens svar 10.11 kl. 22:59. Rådet anbefalte onsdag, men gruppen valgte i natt. Storyen flettes ikke nå: PR-en stopper når CI er grønn, med bilder av stegene og spørsmålene samlet for gruppen, og flettingen og føringen i dagsfila og `epics.md` kommer i en egen instruksjon etter gruppens ja. Svaret kl. 22:59 står ikke i repoet ennå; det som står her om det, er hentet fra instruksjonen. 8.22, 8.23 og 8.24 er brukt, så dette er 8.25.

Svaret endrer svaret 10.11 kl. 11:52 om 8.9, at rundturen ikke flytter seg fra del til del. Det har fått en Rettet-linje i `spec-8-9-vis-meg-rundt.md` og under 8.9 i `epics.md`.

## Storyen

Som **ny bruker**, vil jeg kunne spille av en omvisning som går side for side gjennom appen og viser hva hver del er, så jeg finner fram uten å lese alt først.

**Oppfyller:** FR-109, svaret 10.11 kl. 22:59 · **Begrenses av:** NFR-06, `AD-10`

**Kontroll — hva testen ser etter:**
- Knappen «Spill av omvisningen» ved «Vis meg rundt» starter en omvisning gjennom oversikten, en aksjeside, børsometeret, Min liste og Innstillinger, i den rekkefølgen
- Hvert steg merker én del av siden og viser en kort tekst fra de samme tekstene som «Vis meg rundt», med «Tilbake», «Neste» og «Lukk»; Esc lukker, fokus flyttes til steget, og skjermleseren får rollen dialog
- Den nummererte lista fra 8.9 står
- Første gang appen åpnes, tilbys omvisningen én gang, og et nei huskes
- Ingen tekst gir råd, og omvisningen er lik i demoen og i den ekte versjonen
- **Ville feilet hvis:** omvisningen gikk i en annen rekkefølge, et steg pekte på en del som ikke finnes, Esc ikke lukket, eller et nei ikke ble husket

**Avhenger av:** 8.9. **Én økt:** ja.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

*Svar 2026-11-11 kl. 13:49 (gruppens svar):* tilbudet første gang og et nei huskes i nettleseren, som bygget (spørsmål 3). Rådet anbefalte det.

*Rettet 2026-11-12 (gruppens svar 12.11 kl. 09:58, story 8.26, tillegg 21):* tilbudet første gang starter ikke lenger hele omvisningen, men «Vis meg rundt» for oversikten, med teksten «Første gang her? «Vis meg rundt» viser deg denne siden, ett steg om gangen.» og knappene «Vis meg rundt» og «Nei takk». Hele omvisningen er 23 steg på seks sider, og målet «Brukerutfall» i §7 i PRD-en er at en person utenfor gruppen gjennomfører hovedflyten og forklarer hvorfor en aksje skiller seg ut, under 5 minutter, uten hjelp. Svaret huskes i nettleseren som før, og «Spill av omvisningen» står øverst som før. Rådet anbefalte det. Svaret føres etter instruksjonen kl. 18:01 11.11 og tillegg 21, som lagres i `docs/ai-prompts/2026-11-12.md` etter gruppens ja.

*Svar 2026-11-11 kl. 14:33 (gruppens svar):* ja til forslagene i spørsmål 1, 2, 4, 5, 6 og 8 og til starten fra oversikten med alle aksjene (spørsmål 9), som bygget. Omvisningen får stegene fra «Følg en aksje» etter Min liste når del B (8.22) er flettet (spørsmål 7). Omvisningen flettes når svarene er bygget, gjennomgått og CI er grønn, etter at del C og del B er flettet, uten at gruppen ser på den igjen. Rådet anbefalte alt.

*Svar 2026-11-11 kl. 16:26 (gruppens svar):* lista «Ekstra, hvis tiden rekker» står borte fra README-en, og setningen under listene sier «Ekstra» igjen, som før 3.6. Bildegrenene beholdes, så bildene i PR-ene står, og så gruppen kan vise endringene i refleksjonsloggen og rapporten; ingen bildegren slettes. Rådet anbefalte det.

1. **Hvor står knappen?** *Forslag:* ved siden av «Vis meg rundt» øverst, på de samme sidene, og skjult til skriptet er lastet, så den aldri står uten å virke. Med «Vis hjelp» av står den ikke, som «Vis meg rundt».
2. **Hvilken aksjeside?** *Forslag:* den første aksjen i tabellen på oversikten, som omvisningen leser når den går fra oversikten. I demoen er det BRFE. Min liste vises med «Alle», så tabellen har aksjer også uten stjerner.
3. **Hvordan huskes tilbudet første gang og et nei?** *Forslag:* i nettleseren (`localStorage`), ikke i basen, så det trengs ingen migrasjon, og storyen kan flettes når som helst. Tilbudet står øverst på oversikten til det er besvart, med «Spill av omvisningen» og «Nei takk», og begge svarene huskes. Hvor omvisningen er mellom sidene, står i `sessionStorage`. Alternativet er en rad i `innstilling`, som krever en ny migrasjon og fletting kl. 23:50–23:58; da gjelder svaret maskinen, ikke nettleseren.
4. **Skriptet.** *Forslag:* omvisningen ligger i `src/static/hjelp.js`, fordi testene krever at sidene bare har det ene skriptet. Stegene står som data i rammen (`<div id="omvisning" hidden>`), og logikken for neste steg og adressen er rene funksjoner som testene kjører med Node.
5. **Steget og boksen.** *Forslag:* en boks fast nederst til høyre med «Steg N av M», tittelen, teksten og knappene, som `role="dialog"` med `aria-modal="false"`, så siden kan leses og brukes under. Delen steget gjelder, får en oransje ramme og rulles fram. Er ankeret et tomt merke rett foran delen, som `noekkeltallene` fra 8.9, merkes delen etter. Fokus går til boksen, og tilbake dit det var når omvisningen lukkes.
6. **Et steg uten delen.** *Forslag:* hoppes over i samme retning, som når en side ikke viser sjekkene.
7. **Stegene.** *Forslag:* de samme som «Vis meg rundt» på sidene (`rundturer()`), i rekkefølgen sidene står, 21 steg i demoen. «Følg en aksje» er ikke med, fordi den ikke er i rekkefølgen i svaret.
8. **Bildene.** *Forslag:* bildene av stegene fra demoen står i PR-en, fra en egen gren med bare bildene (som for 8.17b). Bildene i `docs/appen/` tas på nytt, med tilbudet besvart, fordi knappen står øverst på sidene.
9. **Startet fra oversikten med valg.** *Forslag:* lagt til ved flettingen av 8.23 11.11. Startes omvisningen på oversikten med «Min liste» (`?vis=min`), et filter eller en sortering, går den først til oversikten med alle aksjene (`/`), så stegene merker tabellen og aksjesiden er den første aksjen i den. Alternativet er å starte der brukeren er, men med tom Min liste står det ingen tabell der, og aksjesiden hoppes over.

## Delene

### A) Knappen og rekkefølgen

**Ville feilet hvis:** knappen manglet ved «Vis meg rundt», lista fra 8.9 forsvant, eller sidene kom i en annen rekkefølge.

### B) Stegene, tastaturet og skjermleseren

**Ville feilet hvis:** et steg hadde en annen tekst enn «Vis meg rundt», pekte på en del som ikke finnes, manglet en av knappene, eller Esc, fokuset eller rollen ikke virket.

### C) Første gang

**Ville feilet hvis:** tilbudet kom på en annen side enn oversikten, manglet «Nei takk», eller svaret ikke ble husket, eller storyen trengte en migrasjon.

### D) Ingen råd, og lik i begge versjonene

**Ville feilet hvis:** en tekst ga råd eller sa noe om hva kursen vil gjøre, eller omvisningen var en annen i den ekte versjonen.

## Bygget 11.11

Bygget på grenen `8-25-spill-av-omvisningen`, i worktreen `G74-lund-osen-8-25`, fra origin/main (`d6e3b4a3`), i `de666402`.

- **Filene:** `OMVISNING` og omvisningen i `src/static/hjelp.js`; `OMVISNINGEN_SIDER` og `omvisningen()` i `src/hjelpetekster.py`; `_omvisningen` i `src/app.py`; dataene i `src/templates/_ramme.html`; knappen i `src/templates/_rundtur.html`; stilen i `src/static/stil.css`; `docs/hjelp.md`, README-en og Rettet-linjene for 8.9.
- **Tester:** `tests/test_omvisningen_8_25.py`. Logikken i skriptet kjøres med Node (v24 på maskinen), og testene for den hoppes over der Node mangler.
- **Prøvd i Edge** uten vindu med DevTools-protokollen, mot en demobase i en midlertidig mappe og en server på en ledig port, ikke 8000: tilbudet første gang, «Nei takk» som huskes, alle 21 stegene på de fem sidene med fokus på boksen og delen merket, «Tilbake» over en side, Esc, og en lenke midt i omvisningen, som lukker den.
- **Bildene:** de åtte bildene i `docs/appen/` som viser toppen av en side med «Vis meg rundt», er tatt på nytt med knappen, med tilbudet besvart og de samme høydene. Bildene av stegene står i PR-en.

## Mutantene

På `de666402` fire, én per del: A (børsometeret før aksjesiden), B (et steg uten delen hoppes ikke over), C (et nei huskes ikke) og D (omvisningen bare i demoen). Alle ble fanget av `tests/test_omvisningen_8_25.py`, og hver fil var lik HEAD etterpå (kopi før, sha256 mot HEAD etter).

## Gjennomgangen 11.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, uten bildene og `tests/test_docker.py`, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 15 funn, Edge Case Hunter 9 og Verification Gap 7.

**Høy**
- *BH1, ECH1 og ECH2, rettet.* En lagret omvisning sendte brukeren videre fra hver side, også fra en lenke i stripa, nettleserens Tilbake, investorsiden og feilsiden, og kunne gi en løkke. Nå lagrer omvisningen adressen den selv gikk til, og fortsetter bare på den (`OMVISNING.fortsett`); ellers lukkes den stille. Prøvd i Edge og med Node.

**Middels**
- *BH2 og ECH3, rettet.* Retningen tas med til neste side, så «Tilbake» over en side virker.
- *BH3 og ECH4, rettet.* «Tilbake» virker bare når det finnes et steg før, og «Neste» heter «Ferdig» når det ikke finnes flere (`OMVISNING.knappene`).
- *BH4, rettet* med BH1: en side med en annen adresse fortsetter ikke omvisningen.
- *BH5, rettet.* En side fra hurtigbufferen ved Tilbake leser tilstanden på nytt (`pageshow`).
- *BH14 og VG1, rettet.* Tilstanden, knappene, Esc og tilbudet er rene funksjoner som testene kjører med Node, og en test viser at siden bruker dem.
- *VG6, ikke en feil.* Instruksjonen kl. 23:02 sier at føringen i dagsfila og `epics.md` kommer i en egen instruksjon etter gruppens ja. Den ligger ordrett i scratchpad til da, og Rettet-linjene sier det.

**Lav**
- *Rettet:* BH6 og ECH5 (en gammel tilstand starter ikke omvisningen), BH7 og ECH7 (delen rulles øverst, så boksen dekker mindre), BH8 (fokus går tilbake til knappen når det var på siden), BH9 (Esc lukker ikke omvisningen når et hjelpevindu er åpent), BH10 (bare et tomt `<span>` er et merke), BH15 (en åpen liste står på egen linje), VG4 (testen for migrasjonen ser ikke på nummeret), VG5 og VG7 (hjelpen og README-en).
- *Ført:* BH11 («Steg N av M» teller med steg som hoppes over), BH12 og ECH6 (uten lagring i nettleseren kommer tilbudet igjen, og omvisningen stopper ved første sidebytte; hjelpen sier det), ECH8 (fokus går til boksen ved hvert steg), ECH9 (tilbudet står også på en tom oversikt), VG2 (aksjesiden uten sjekker og uten kurser er ikke testet for seg) og VG3 (testen for demoen og den ekte versjonen sammenligner bare dataene).
- *Ikke en feil:* BH13 (både «Vis meg rundt» og omvisningen bruker `STANDARD`).

## Flettingen av main 11.11 (8.23, del A av funnene fra brukertesten)

Instruksjonen kl. 11:59 11.11. Main ble flettet inn i grenen i `07033d0c`. Konfliktene var i README-en, `src/app.py`, `tests/test_docker.py` og åtte bilder i `docs/appen/`, ikke ni. Begge sidene er beholdt. I `583f291c` er de åtte bildene med knappen tatt på nytt fra demoen, med høydene fra 8.23 og tilbudet besvart. De fem andre bildene i `docs/appen/` ble like byte for byte, og avtrykkene er regnet ut på nytt. Omvisningen ble prøvd side for side i Edge etterpå: alle 21 stegene var merket, og «Tilbake» over en side, Esc og en lenke midt i omvisningen virket som før. Bildene av stegene i PR-en er tatt på nytt.

**Gjennomgangen av det som ble endret ved konfliktene** (Edge Case Hunter og Verification Gap i samme agent, med repoet). 8.23 fikk «Min liste» på oversikten til å filtrere tabellen (`?vis=min`), med en tekst i stedet for tabellen når lista er tom.

*Middels*
- *ECH1, ECH2, VG1 og VG2, rettet.* Startet omvisningen på `/?vis=min` med tom Min liste, merket stegene om tabellen teksten «Ingen aksjer i Min liste ennå». Aksjesiden ble i tillegg hoppet over stille, fordi ingen aksjelenke fantes. Nå går omvisningen først til `/` når den startes på oversikten med en annen adresse (`OMVISNING.startAdresse`), og en aksje fra en tidligere omvisning glemmes. Tester: ankeret `aksjene` på `/` er tabellen med BRFE først, tilfellet med tom Min liste, og `startAdresse` kjørt med Node. Prøvd i Edge med tom Min liste i demoen: omvisningen gikk fra `/?vis=min` til `/`, merket tabellen og gikk videre til BRFE. Fra `/?signal=positiv` gikk den også til `/`.

*Lav*
- *Rettet med ECH1:* ECH3 (fra `/?vis=min` ble aksjesiden den første merkede aksjen) og ECH4 (adressen med valg på oversikten gikk tapt ved «Tilbake»; nå starter omvisningen alltid på `/`).
- *Ført:* VG3 (ingen test kjører hele løpet når en side uten adresse hoppes over) og VG4 (omvisningen med tom Min liste er bare prøvd i demoen, ikke i den ekte versjonen, som ikke ble startet).

## Stegene fra «Følg en aksje» 11.11 (spørsmål 7)

Instruksjonen kl. 16:07 11.11. Del B (8.22) ble flettet med PR #138, og Utført-linja kom i dagsfila 11.11 kl. 16:19. Main ble flettet inn i grenen i `c6c01170`, med konflikter i README-en, `docs/hjelp.md`, `src/static/hjelp.js`, `tests/test_docker.py` og `issues.md`; begge sidene er beholdt.

- **Stegene** (`5862d1f2`): `OMVISNINGEN_SIDER` og `OMVISNING.SIDENE` har `folg` etter `min_liste`, med adressen `/folg`, og stegene er de to fra «Vis meg rundt» på siden (`folg-tittel` og `q`), 23 steg i demoen. Er lista full, står bare tittelen, og søket hoppes over.
- **Navnet på siden.** «Følg en aksje» merker oversikten (eller Min liste ved et bytte) i stripa, og rammen ga skriptet det navnet. Da ville omvisningen blitt tilbudt der, og et steg på siden sendt brukeren til samme side igjen. Nå gir siden `omvisning_side="folg"`, og rammen bruker det før `aktiv`.
- **Feil fra flettingen:** søket fra 8.22 i `hjelp.js` kjørte når testene laster skriptet i Node, uten `document`. Det hopper nå over da, som omvisningen.
- **README-en** har omvisningen under «Ekstra, ferdig» (svaret kl. 13:49), og setningen under listene sier «Ekstra» igjen (svaret kl. 16:26, `a96e5f12`).
- **Prøvd i Edge** mot demoen, side for side: alle 23 stegene på de seks sidene er merket, med fokus på boksen; «Tilbake» over en side, Esc og en lenke midt i omvisningen virker, og tilbudet står ikke på `/folg`.
- **Bildene** i `docs/appen/` er tatt på nytt (`97f3dbe5`): bare de to av «Følg en aksje» ble ulike, med knappen, og med de samme høydene. Bildene av stegene på `pr-8-25-bilder` er tatt på nytt, med et nytt av «Følg en aksje» (`d35e705f`).
- **Mutanten:** `omvisning_side=None` i `folg_side` ble fanget av to tester i `tests/test_omvisningen_8_25.py`, og `src/app.py` var lik HEAD etterpå (kopi før, sha256 mot HEAD etter).

**Gjennomgangen av «Følg en aksje»** (Blind Hunter med bare diffen fra `c6c01170`, Edge Case Hunter og Verification Gap i samme agent, med repoet). Blind Hunter hadde 10 funn, Edge Case Hunter 5 og Verification Gap 6. Ingen høye. Rettet i `29601f75`.

*Middels*
- *ECH1 og VG1, rettet.* Når basen ikke kan åpnes, svarer `/folg` med feilsiden på samme adresse, uten navnet `folg`. Omvisningen fortsatte der fordi adressen stemte, og lastet `/folg` igjen og igjen. Nå fortsetter den bare når steget hører til siden (`OMVISNING.paaSiden`); ellers lukkes den. Tester med Node og for feilsiden på `/folg`. Prøvd i Edge igjen: alle 23 stegene.
- *VG2, BH3 og ECH4 (delvis), rettet.* At «Følg en aksje» med full liste viser tittelen og ikke søket, hadde ingen test. Nå følger testen aksjer i demoen til lista er full.

*Lav*
- *Rettet:* ECH5 og BH5 (`default(..., true)` i rammen, så `None` gir navnet fra stripa), BH4 (en test for at `/folg?kode=` lukker omvisningen), BH7 (testen sammenligner også tekstene) og VG5 (antallet sider i README-en følger `OMVISNINGEN_SIDER`).
- *Ført:* ECH2 (en base uten tabellene fra 0010 gir en 404 uten rammen på `/folg`, så omvisningen stopper der), ECH3 (`/ferdig-liste` og investorsiden har navnet fra stripa; `fortsett` og `paaSiden` holder dem utenfor), ECH4 (telleren hopper over steget om søket med full liste, som BH11), VG3 (`OMVISNING.SIDENE` brukes ikke av skriptet; rekkefølgen kommer fra dataene, som testene sjekker), VG4 (stripa ved `?bytt=` er ikke testet her, men i testene for 8.22), VG6 (testene med Node hoppes over uten Node; CI har Node) og BH10 (vakten i søket fra 8.22 dekkes av testene med Node, som laster hele skriptet).
- *Ikke en feil:* BH1 («fem av sidene» står ikke lenger i README-en), BH2 (setningen er gruppens svar kl. 16:26), BH6 (`folg_side` rendrer `folg.html` ett sted), BH8 (bildene er i `97f3dbe5`, utenfor diffen gjennomgangen fikk) og BH9 (instruksjonen kl. 16:07 sier «Ekstra, ferdig» etter svaret kl. 13:49, og README-en flettes med omvisningen).

## Flettingen

*Lagt til 2026-11-11:* 8.25 er flettet med PR #143 i `c53df5b1` kl. 17:10, låst til head-en `97003ae8`, etter instruksjonen kl. 16:07 i `docs/ai-prompts/2026-11-11.md` og gruppens svar 11.11 kl. 13:49, 14:33 og 16:26. Main hadde ikke endret seg siden main ble flettet inn i grenen (`c6c01170`). Hele settet lokalt i seks deler før pushen: 5252 bestått og 37 hoppet over (5289, likt `--collect-only`). CI var grønn på head-en (run 43054754599). Grenen er slettet og worktreen fjernet; bildegrenen `pr-8-25-bilder` står, etter svaret kl. 16:26.
