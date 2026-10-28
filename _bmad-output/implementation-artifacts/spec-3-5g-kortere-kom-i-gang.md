---
title: 'Story 3.5 (3.5g): «Kom i gang» med fem steg og resten bak piler'
type: 'docs'
created: '2026-10-27'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '54d4714'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5f-hovedveien.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** «Kom i gang» er for lang. Fra overskriften til den første pila står tabellen, «Velg vei», «Du trenger», hele dobbeltklikket med advarslene, nøkkelen og skriptene, og Docker-stegene 1–4 med bildene.

**Løsningen:** én setning, så «Enklest: dobbeltklikk (anbefalt)» med fem korte nummererte steg, én linje om advarselen første gang og én om den ekte versjonen. Alt annet står bak piler eller i `docs/hjelp.md`, og ingenting forsvinner.

**Grunnlaget:** avgjørelsen 26.10 kl. 23:00 under story 3.5 i `epics.md`. Den går foran innspillet 25.10 kl. 11:26 om at resten ryddes etter testene.

## Slik er det i dag (slått opp 27.10 på `54d4714`)

- **`README.md`, «Kom i gang» (linje 33–103 før den første pila):** ankeret `kom-i-gang`, avsnittet som begynner med «Vi anbefaler demoen for faglærer og sensor», tabellen, «Velg vei etter hva du har», «Du trenger», `### Enklest: dobbeltklikk, uten Docker` med fire punkter, «Når vinduet er åpent» med fire punkter, advarselen fra Windows, godkjenningen på Mac, `.git`-vernet, nøkkelen og skriptene med porten, så `### Med Docker Desktop` med steg 1–4, tre bilder, «Slik limer du inn en kommando» og «Velg versjon». Så pilene til demoen og den ekte versjonen, advarselen mot `down -v`, `### Står du fast?` med fem spørsmål bak piler, og `### Mer for den som vil` med fem piler, der «Uten Docker, med uv» er den andre.
- **Ankrene lenkene bruker:** `#kom-i-gang`, `#enklest-dobbeltklikk-uten-docker` («Til faglærer», «Velg vei» og «Windows advarer mot fila.» i `docs/hjelp.md`), `#med-docker-desktop` og `#demoen` («Til faglærer»), `#den-ekte-versjonen` («Til faglærer», demoen og `EKTE_VERSJONEN_URL` i `src/app.py`, som demolinja i appen lenker til), `#uten-docker-med-uv`, `#står-du-fast`, `#mer-for-den-som-vil` og `#tester`.
- **`docs/hjelp.md`:** «Windows advarer mot fila.» og «Mac sier at fila ikke kan åpnes.» under «Start med dobbeltklikk» har det samme som avsnittene i README-en. «Hvor finner jeg nøkkelen, og hvordan limer jeg den inn?» og «Nøkkelen var feil.» har det meste av avsnittet om nøkkelen, men ikke at den lagres bare i `.env`, eller at ingen kall brukes når alt er hentet. Svaret om porten sier at «Bytte mellom demoen og den ekte versjonen» står under «Mer for den som vil».
- **Testene for README-en:** de fleste i `tests/test_docker.py`, fra `TestReadme` (linje 512) til `TestHovedveien` (linje 3292), med hjelperne `_kom_i_gang`, `_seksjon`, `_pil`, `_steg`, `_detaljer`, `_utenfor_pilene` og `PIL`, og `tests/test_dobbeltklikk.py` (`_delen_i_readme`). Avtrykkene i `AVTRYKK_I_PILENE` er sha256 av innholdet i pilene til demoen, den ekte versjonen (med advarselen mot `down -v`), dokumentlista og mappestrukturen. `test_markdown_inne_i_pilene_vises_riktig_paa_github` godtar ingen pil inne i en annen. `test_demo.py::test_lenken_gaar_til_ankeret_i_readme` krever `<a name="den-ekte-versjonen"></a>` i README-en.

## Kontrollpunktene

- a) «Kom i gang»: én setning først, så «Enklest: dobbeltklikk (anbefalt)» med de fem stegene, høyst 25 ord hver, linja om advarselen med lenker til svarene for Windows og Mac, og linja om den ekte versjonen. Ankrene som «Til faglærer» og andre lenker bruker, virker fortsatt.
- b) Bak piler, i denne rekkefølgen: «Demoen og den ekte versjonen» med tabellen, «Du trenger», «Med Docker Desktop» med stegene og bildene, «Uten Docker, med uv», «Slik virker dobbeltklikket» med skriptene, porten og `.git`-vernet, og «Står du fast?». Teksten flyttes og skrives ikke om, utenom det som trengs for at den henger sammen.
- c) Testene følger den nye formen, med «Ville feilet hvis» stegene ikke sto først, et steg manglet eller var for langt, en lenke eller et anker var dødt, en overskrift eller kommando fra før manglet, eller Docker-veien manglet. Avtrykkene settes på nytt. Mutant: steg 3 tatt ut.
- `docs/hjelp.md` følger med (regel 19).

## Valg som er gjort her

- **Ankeret til dobbeltklikket.** Overskriften «Enklest: dobbeltklikk (anbefalt)» gir ankeret `enklest-dobbeltklikk-anbefalt`. En linje `<a name="enklest-dobbeltklikk-uten-docker"></a>` rett over overskriften beholder det gamle, som `kom-i-gang` i 3.5f, så «Til faglærer» og `docs/hjelp.md` virker som før.
- **Pilene til demoen og den ekte versjonen står ikke inne i pila til Docker.** De står rett etter den, hver for seg, med advarselen mot `down -v` rett under pila til den ekte versjonen som før (svaret 20.10 kl. 20:20). Grunnen er ankrene: `#demoen` og `#den-ekte-versjonen` står i `<summary>`, og «Til faglærer» og demolinja i appen lenker dit. Inne i en lukket pil ville `<summary>` vært skjult, så lenken ikke viste noe. Innholdet i de to pilene er uendret, så avtrykkene deres er de samme.
- **«Står du fast?» er en pil med de fem spørsmålene inni,** fordi spørsmålene alt står bak hver sin pil. Det er den eneste pila inne i en annen. Testen for pilene godtar det der og ingen andre steder. Ankeret `står-du-fast` står i `<summary>`, som de andre.
- **Nummererte steg i dobbeltklikket.** 3.5f valgte punktliste fordi «steg 4» betyr Docker-stegene. Avgjørelsen 26.10 kl. 23:00 sier nummererte steg. Docker-stegene står nå bak pila «Med Docker Desktop», og overskriftene i `docs/hjelp.md` heter «Steg 1: Docker Desktop» og så videre, så de nevner Docker. «steg 4» i README-en står bare inne i Docker-pilene og i svarene under «Står du fast?», som gjelder Docker. Det står som åpent punkt om det likevel er uklart for leseren.
- **Avsnittene om advarselen, godkjenningen og nøkkelen står i pila «Slik virker dobbeltklikket»,** uendret, og linja om advarselen lenker til svarene i `docs/hjelp.md`. Svaret om nøkkelen i hjelpen mangler to setninger fra README-en (slått opp over), så avsnittet blir i README-en, og ingenting forsvinner.
- **Det som er skrevet om for at teksten henger sammen:** lenketeksten til dobbeltklikket i «Til faglærer» og «Velg vei» er «Enklest: dobbeltklikk», og «Velg vei» sier ikke lenger at uv står under «Mer for den som vil». I `docs/hjelp.md` viser svaret «Windows advarer mot fila.» til «Slik virker dobbeltklikket» i stedet for den gamle overskriften. Svaret om porten står, fordi «Bytte mellom demoen og den ekte versjonen» fortsatt står under «Mer for den som vil». Resten er flyttet uendret: fem av pilene har byte for byte samme innhold som delene på `54d4714`, og testene låser hver pil med sha256 (`AVTRYKK_I_KOM_I_GANG`).

## Planen

1. Spesifikasjonen.
2. README-en, `docs/hjelp.md` og testene i samme commit (regel 19 og instruksjonen).

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: steg 3 tatt ut av dobbeltklikket.

*Utfallet 27.10 kl. 00:13:48–00:13:50 på `e450ff9`:* linja `3. **Åpne `G74-lund-osen-main` og dobbeltklikk «Start demoen».** …` tatt ut av `README.md`, kjørt med `-x` mot `tests/test_docker.py`, `tests/test_dobbeltklikk.py` og `tests/test_readme.py`. Fanget av `TestReadmeBakPiler::test_hvert_steg_hver_kommando_og_hver_lenke_fra_foer_finnes`. Kjørt igjen kl. 00:13:57 med `-k TestHovedveien`: fanget av `test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil`. Fila var lik HEAD etter begge: samme sha256 som kopien, og samme git-objekt som `HEAD:README.md` (`e152934`).

## Avtrykkene

Avtrykkene i `AVTRYKK_I_KOM_I_GANG` er sha256 av innholdet i hver pil på grenen. Med et skript utenfor repoet ble de sammenlignet med sha256 av de samme delene i `git show 54d4714:README.md` (linje 51, 55–77, 81–102, 172–213 og 247–289). «Du trenger», «Med Docker Desktop», «Uten Docker, med uv», «Slik virker dobbeltklikket» og «Står du fast?» var like på `e450ff9`. Etter gjennomgangen er «Med Docker Desktop» skrevet om i én setning (BH2), og de fire andre er fortsatt like.

## Gjennomgangen

Kommer etter hele settet.

Gjennomgang 27.10 etter hele settet (3773 bestått, 37 hoppet over, 0 feilet, 00:14:12–00:21:50 på `e450ff9`), av diffen `54d4714..e450ff9`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 15) og Verification Gap (VG, 5, ingen hull i dekningen av kravene i c). Dommen i tabellen er vår. Små funn er rettet med en gang.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH7, ECH1, ECH15, VG2 | Lenken i «Windows advarer mot fila.» i hjelpen nevner «Slik virker dobbeltklikket», men går til de fem stegene | medium | **rettet:** pila har ankeret `slik-virker-dobbeltklikket`, og hjelpen lenker dit |
| BH2, ECH6, VG4 | «Tabellen over viser forskjellen» i pila til Docker, men tabellen står i en annen pil | medium | **rettet:** «Tabellen i pila «Demoen og den ekte versjonen» viser forskjellen.», og avtrykket er satt på nytt |
| BH1, ECH5, VG4 | «Demoen står først i stegene under» står over tabellen, ikke over stegene | low | **rettet:** «i stegene for Docker og uv», og avtrykket er satt på nytt |
| ECH2, VG3 | Steg 3 sier ikke at Windows-brukere skal ta fila uten `.command` | medium | **rettet:** «På Windows: den uten `.command`.» (21 ord), med test |
| BH14, ECH3 | Steg 2 sier ikke at man ikke skal starte inne i ZIP-fila | medium | **rettet:** «Ikke start fra inne i ZIP-fila.» (22 ord), med test |
| BH5, ECH4 | Linja om den ekte versjonen sier ikke at den bare starter i en kopi fra ZIP-fila | medium | **rettet:** «og starter bare i en kopi fra ZIP-fila, ikke i en klon», med test |
| BH8, ECH8, VG1 | En assert i `test_readme_og_hjelpen_har_advarselen_og_godkjenningen` kan ikke feile | low | **rettet:** den krever at pila til Docker finnes og står etter stegene |
| BH9, ECH9 | `_utenfor_pilene` godtar en `</details>` uten par | low | **rettet:** `dybde` sjekkes i løkka og til slutt |
| ECH10, ECH11, ECH12 | `_pilene` gir IndexError, to piler med samme navn leses stille, og `_delen_i_readme` gir IndexError | low | **rettet:** påstander med melding |
| BH13, ECH14 | Avtrykkene er regnet på grenen, ikke vist mot `54d4714` | low | **rettet:** «Avtrykkene» over sier hvordan de ble sammenlignet |
| ECH13 | Commit-meldingen sier «uendret» om pilene, men «Velg vei» er skrevet om | low | står: spesifikasjonen og kommentaren over avtrykkene sier hva som er skrevet om, og historikken skrives ikke om (regel 7) |
| BH3 | Ingenting synlig viser til Docker eller uv, for eksempel for Linux | medium | **til gruppen:** avgjørelsen 26.10 kl. 23:00 sier én linje om advarselen og én om den ekte versjonen under stegene, og alt annet bak piler. «Du trenger» (Linux) og «Velg vei» står i pilene rett under. **Avgjort av gruppen 27.10 kl. 06:09 (a):** en tredje kort linje under stegene, «Linux: bruk Docker eller uv, under.», med lenker til pilene for Docker og uv og test (`test_linja_om_linux_lenker_til_docker_og_uv`) |
| ECH7 | «steg 4» i svarene under «Står du fast?» kan leses som steg 4 i dobbeltklikket | medium | **til gruppen:** står under «Åpent». Svarene er flyttet uendret. **Avgjort av gruppen 27.10 kl. 06:09 (b):** hver henvisning til et steg under «Står du fast?» sier hvilken vei den gjelder, alle fem «med Docker», og de samme svarene i `docs/hjelp.md` følger, med test (`test_hvert_steg_under_staar_du_fast_sier_hvilken_vei`) |
| BH4 | Den som har uv fra før, kan hoppe over steg 4 og ikke lese at første gang tar minutter | low | står: avgjørelsen gir fem steg i den rekkefølgen. Under «Åpent» |
| BH6 | «steg 1–4» i «Til faglærer» lander på pila til Docker, ikke på stegene | low | står: pila heter «Med Docker Desktop» og er synlig der lenken lander |
| BH11 | Bare én mutant, så grensen på 25 ord og ankeret er ikke mutert | low | står: instruksjonen sier én mutant. Grensen og ankeret sjekkes i `test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil` og `test_overskriftene_fra_foer_finnes` |
| BH12 | To ankre på samme sted, og ingen test hindrer lenker til `enklest-dobbeltklikk-anbefalt` | low | står: «Valg som er gjort her» sier at `enklest-dobbeltklikk-uten-docker` er ankeret lenkene bruker, og testen krever at det finnes én gang |
| BH10 | `<details open>` eller CRLF gjør at hjelperne ikke ser pila | low | avvist: `test_markdown_inne_i_pilene_vises_riktig_paa_github` krever `<details>` alene på linja og like mange `<details`, `</details>` og `<summary>`, og `read_text` leser CRLF som LF |
| VG5 | Prøveprotokollen i §9 i `docs/kvalitetssikring.md` har overskriften og stegene fra før 3.5g | low | **til gruppen:** §9 er ikke med i instruksjonen. Rettes før README-prøven, med en Rettet-linje |

## Åpent

- Om «steg 4» er uklart nå som dobbeltklikket også har nummererte steg (se «Valg som er gjort her», ECH7). Avgjort av gruppen 27.10 kl. 06:09: henvisningene sier hvilken vei, som «steg 4 med Docker».
- Om det skal stå en synlig linje til Docker og uv under stegene, for eksempel for Linux (BH3). Det ville vært en tredje linje under stegene, og avgjørelsen 26.10 kl. 23:00 sier to. Avgjort av gruppen 27.10 kl. 06:09: en tredje kort linje, «Linux: bruk Docker eller uv, under.»
- Om ventingen første gang skal stå i et eget steg (BH4).
- §9 i `docs/kvalitetssikring.md` følger ikke de fem stegene ennå (VG5).
