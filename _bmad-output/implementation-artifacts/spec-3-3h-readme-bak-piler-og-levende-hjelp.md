---
title: 'Story 3.3 (3.3h): README-en bak piler, og hjelpen som levende dokument'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: '013be41'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3g-readme-demoen-anbefales.md'
  - '{project-root}/docs/ux-logg.md'
---

Tillegg til story 3.3 (README — «Slik kjører du den»), etter gruppens svar 20.10 kl. 10:14, 10:15, 10:18 og 10:19 og kl. 16:19 (under story 3.3 i `epics.md`, `49e9041`). Det er U7 i [`docs/ux-logg.md`](../../docs/ux-logg.md).

## Intent

**Problem:** README-en er lang å lese: 419 linjer etter `wc -l` og om lag 3 800 ord 20.10 (U7). Alt står åpent, også stegene for den versjonen leseren ikke valgte, dokumentlista og mappestrukturen. `docs/hjelp.md` har åtte daterte linjer (*Rettet* og *Lagt til*) mellom svarene, og svaret «Når kan jeg hente?» begynner fortsatt med «Hent etter kl. 21», fordi kl. 22 bare står i en Rettet-linje under.

**Løsning:** README-en blir kortere å lese, med mer bak en pil som foldes ut (`<details>`), og alt står fortsatt i én fil, som virker fra ZIP-fila. Hjelpen blir et levende dokument som README-en: teksten rettes der den står, og historikken ligger i git.

## Planen, én commit per punkt

**a) Veiene.** De felles stegene 1–4 står åpent. Rett etter dem kommer en kort linje «Velg vei» og to piler:
- demoen, anbefalt for faglærer og sensor og uten nøkkel (svaret 19.10 kl. 14:46)
- den ekte versjonen, med kurser fra EODHD og egen nøkkel

Tabellen over viser forskjellen. Inne i hver pil står stegene fra 5, kommandoene, bildene og advarselen om `docker compose down -v` uendret. Lenkene og ankrene dit virker. Linja i demoen om å gå videre til den ekte versjonen peker til pila.

**b) Resten av README-en og hjelpen.**
- «Dokumentene» og «Mappestruktur» har overskriften synlig og innholdet bak en pil.
- Under «Tester» står kommandoene, punktene om nettkall, data, CI og ruff og lenken til kvalitetssikringen synlig. Installasjonen av uv og tipset når uv ikke blir funnet står bak en pil.
- «Status» står åpent, og «Ferdig» blir en kort liste over det appen kan, én linje per punkt, med alt som er flettet og ikke noe annet.
- I `docs/hjelp.md` arbeides hver linje som begynner med *Rettet eller *Lagt til, inn i svaret den hører til, eller tas bort når den bare sier hva som var før. Svaret om når man kan hente, sier kl. 22, og testene som krevde linjene, følger med.

**c) Testene**, med «Ville feilet hvis»:
- demoen, den ekte versjonen, dokumentlista og mappestrukturen står bak hver sin pil
- de felles stegene står ikke bak en pil
- pila til demoen sier at den er anbefalt for faglærer og sensor
- under «Tester» står `uv sync`, `uv run pytest` og lenken synlig
- hvert steg, hver kommando og hver lenke fra før finnes
- hjelpen sier klokkeslettet fra `TIDSGRENSE` i svaret og har ingen *Rettet- eller *Lagt til-linje
- markdown inne i pilene vises riktig på GitHub

## Det som ikke endres

- Ingen kode i `src/`.
- Rekkefølgen i README-en: beskrivelsen, bildene, «Innhold», «Til faglærer», «Kom i gang», «Status», «Tester», «Dokumentene», «Mappestruktur» og «Medlemmer».
- «Står du fast?» og «Mer for den som vil» står som før.
- Ingen linje fjernes fra andre dokumenter enn README-en og `docs/hjelp.md`, utenom `status` og `updated`.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Den ekte `.env` leses ikke.
- PR-en stopper før flettingen og venter på ja.

**Mutantene**, én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- de felles stegene bak en pil
- «anbefalt» tatt bort fra pila til demoen
- et steg tatt bort fra den ekte versjonen
- den tomme linja etter `</summary>` tatt bort
- en Rettet-linje lagt tilbake i hjelpen

**Testtallet før:** 2763 bestått og 17 hoppet over (head-en til PR #79, samme tester som main på `013be41`).

## Avgjort underveis

- **Ankeret står i `<summary>`:** `<a name="demoen"></a>` og `<a name="den-ekte-versjonen"></a>`, fordi en `<details>` ikke har noe anker på GitHub. Prøvd på grenen 20.10 med README-en GitHub viser (`gh api …/readme?ref=3-3h-readme-bak-piler`): GitHub beholder dem som `user-content-demoen` og `user-content-den-ekte-versjonen`, som ankrene til overskriftene. En lenke dit går til pila, men åpner den ikke, så linja i demoen sier «og klikker på pila».
- **Advarselen om `docker compose down -v` står uendret i pila til den ekte versjonen**, som steg 2a sier, og synes når pila er åpnet. Testen `test_advarselen_mot_down_v_staar_synlig` krever den sist i pila og ikke i en pil til inni den. Fra 22:32 11.10 sto den synlig uten å åpne noe.
- **«Ferdig» har det appen kan, i 8 punkter på høyst 16 ord.** Det rundt appen, README-en, ruff, kvalitetssikringen og repoet uten kopien av BMAD-skillene, står i én setning under listene. Hvert punkt fra før står, kortere sagt, og loggen der KI-tekstene lagres er ikke et eget punkt.
- **I `docs/hjelp.md`** ble de åtte daterte linjene arbeidet inn i svarene eller tatt bort:
  - de tre øverst ble én setning om at demoen står før den ekte versjonen
  - de to under «Hva er demoen?» ble avsnitt i svaret
  - den under «Hva med nøkkelen?» ble en del av setningen om webserveren
  - kl. 22 står i selve svaret «Når kan jeg hente?», og «På dagtid» ble «Før kl. 22»
  - linja om AirPlay sa bare hva som sto før, og ble tatt bort, med «AirPlay» ute av `test_svarene_beholdt_innholdet`
- **Innholdet i de fire pilene er låst med sha256** mot delen under overskriften på main før grenen (`AVTRYKK_I_PILENE`). Demoen er uten linja om den ekte versjonen, som fikk lenken.
- **README-en blir ikke kortere i linjer** (447 mot 419 etter `wc -l`), men kortere å lese, fordi stegene for den andre versjonen, dokumentlista, mappestrukturen og installasjonen av uv er lukket.
- **De andre dokumentene** fikk en datert linje der de sa noe om Rettet-linjene i hjelpen: `docs/kvalitetssikring.md` (også om pilene i README-prøven), `docs/ux-logg.md` (U7) og story 3.2b i `epics.md`.
- *Rettet 2026-10-20 (gruppens svar kl. 20:20):* advarselen om `docker compose down -v` står ikke lenger i pila, men uendret rett under pila til den ekte versjonen, utenfor alle piler. Den kommer rett etter steg 9 når pila er åpen, og synes for alle når den er lukket (`48d6d7a`). `test_advarselen_mot_down_v_staar_synlig` krever det, og avtrykket for den ekte versjonen i `test_innholdet_i_pilene_er_det_samme_som_foer` regnes av pila og advarselen etter den, så det er det samme som fra `013be41`.
- *Rettet 2026-10-20 (rådets funn):* «Ferdig» manglet selve signalet. Det første punktet er nå de tre sjekkene, trend, bevegelse og interesse, og styrken for hver aksje hver børsdag, med regelforklaringen på aksjesiden, med ordene fra `src/aksjedetalj.py` og `src/templates/aksje.html`. Demolinja har igjen «av de tre sjekkene» (`94db900`). Lista har fortsatt høyst 8 punkter (3.3d), så hentingen og de nye forsøkene står i ett punkt, og grensen per punkt er 20 ord, ikke 16, fordi signalet og demolinja ikke fikk plass innenfor 16. Testen er `test_ferdig_begynner_med_signalet`.

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py` og `tests/test_readme.py`, i en fersk klon med `core.autocrlf=false`. Det ble tatt kopi av fila før hver mutant, sha256 var lik HEAD etter hver, og `git status` var tom. Kjørt på `3042a7f` og igjen på `8e551a1`, med samme utfall:

| # | Mutant | Først i fila | Den nye testen alene |
|---|---|---|---|
| M1 | De felles stegene bak en pil | `test_kopieringen_forklares_en_gang_og_hvert_steg_sier_hvor` | `test_de_felles_stegene_staar_ikke_bak_en_pil` feiler |
| M2 | «anbefalt» tatt bort fra pila til demoen | `test_kom_i_gang_anbefaler_demoen_for_faglaerer_og_sensor` | `test_pila_til_demoen_sier_at_den_er_anbefalt_for_faglaerer_og_sensor` feiler |
| M3 | Steg 8 tatt bort fra den ekte versjonen, og 9 blir 8 | `test_docker_foerst_og_uv_som_alternativ` | `test_hvert_steg_hver_kommando_og_hver_lenke_fra_foer_finnes` feiler |
| M4 | Den tomme linja etter `</summary>` i pila til demoen tatt bort | `test_demoen_foerst_og_zip_foer_kommandoene` | `test_markdown_inne_i_pilene_vises_riktig_paa_github` feiler |
| M5 | En Rettet-linje lagt tilbake i hjelpen | `test_raadet_om_tidspunkt_uten_flagget` | `test_hjelpen_sier_klokkeslettet_fra_tidsgrensen_og_har_ingen_daterte_linjer` feiler |
| M6 | Advarselen om `down -v` tilbake i pila, kjørt på `94db900` | `test_advarselen_mot_down_v_staar_synlig` | den samme feiler |
| M7 | Signalet tatt bort fra «Ferdig», kjørt på `94db900` | `test_ferdig_begynner_med_signalet` | den samme feiler |

## Gjennomgangen

Gjennomgang 20.10 på diffen `013be41..3042a7f`. Linsene var:
- Blind Hunter (BH, 15 funn, bare diffen)
- Edge Case Hunter (ECH, 10 funn, med mutanter i en fersk klon som ble slettet etterpå, og 126 bestått i `test_docker.py` og `test_readme.py`)
- Verification Gap (VG, 8 funn)

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH3, VG3 | «Ferdig» mistet kontrollen av børsdagen og at bare tekster som besto kontrollen vises | medium | rettet: begge står i punktene, og testen krever dem |
| ECH2, BH5, VG5 | En setning inne i en pil kunne tas bort uten at noen test feilet | medium | rettet: `test_innholdet_i_pilene_er_det_samme_som_foer` med sha256 av innholdet |
| ECH1, VG1 | `docs/kvalitetssikring.md` sier at hjelpen har kl. 22 i en Rettet-linje | medium | rettet: en Rettet-linje under |
| BH3 | Testen for «Tester» sammenlignet indekser fra to tekster | medium | rettet: alle tre i samme tekst |
| VG2 | Spesifikasjonen manglet «Avgjort underveis», mutantene og triagen | medium | rettet: denne delen |
| BH4, ECH8 | Advarselen om `down -v` synes først når pila er åpnet | medium | avvist: steg 2a sier at advarselen står uendret inne i pila. Ført under «Avgjort underveis» |
| BH2 | «signalstyrken for hver aksje» var nytt i «Ferdig» | low | rettet: tatt ut igjen, fordi beskrivelsen øverst sier det |
| BH6, VG4 | Det var ikke prøvd at GitHub beholder ankrene i pilene | low | rettet: prøvd på grenen, se «Avgjort underveis» |
| BH7 | En lenke til pila åpner den ikke | low | rettet: linja i demoen sier «og klikker på pila» |
| BH10 | «før Min liste kom» sier ikke når | low | rettet: «før 20.10, da Min liste kom» |
| ECH4 | Story 3.2b i `epics.md` sier at setningen om AirPlay står i en Rettet-linje | low | rettet: en datert linje |
| ECH5 | Testen for daterte linjer kjente bare to former | low | rettet: også Avgjort, Presisert, Skrevet og Ferdig |
| ECH6 | Ankrene ble også lest i kode, og ikke i rekkefølge | low | rettet |
| ECH7 | README-prøven i kvalitetssikringen nevner ikke pilene | low | rettet: en datert linje i §9 |
| VG6, ECH10 | U7 i UX-loggen sier at 3.3h ikke står i `epics.md` | low | rettet: en datert linje under tabellen |
| BH8 | Kravet om Python 3.13 står inne i pila for uv | low | avvist: uv henter Python selv, og «Du trenger» sier det åpent |
| BH9, VG8 | «Før kl. 22 en børsdag» er bredere enn «på dagtid» | low | avvist: det er det koden gjør (`TIDSGRENSE`) |
| BH11 | Setningen «Rundt appen …» leste tungt | nit | rettet |
| BH12, VG8 | Kommentaren om de daterte linjene i hjelpen var gammel | nit | rettet |
| BH13, ECH9 | Kursiv i `<summary>` ble ikke fanget | nit | rettet |
| BH14 | «Tabellen over» er langt over | nit | avvist: tabellen står i innledningen til «Kom i gang», og VG fant det riktig |
| BH15 | Mutantene sto under «Boundaries», og 419 linjer hadde ingen kilde | nit | rettet: egen del, og `wc -l` står ved tallet |
| VG7 | Utført-linja, PR-en og CI gjenstår | nit | gjøres i steg 3–5 |
| BH4, ECH8 | Advarselen om `down -v` synes først når pila er åpnet | medium | rettet etter gruppens svar 20.10 kl. 20:20, som snur avvisningen i raden lenger opp: advarselen står rett under pila (`48d6d7a`) |
| Rådet, 20.10 | «Ferdig» manglet selve signalet: de tre sjekkene, styrken og regelforklaringen | medium | rettet: først i lista, og demolinja har igjen «av de tre sjekkene» (`94db900`) |
