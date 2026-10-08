# Regler for KI-økter i dette repoet

Gjelder alle økter, uansett hvem som kjører dem. Alle reglene har vært i bruk,
og grunnene står i `docs/reflection-log.md` og memloggene under `_bmad-output/`.
Regel 11 kommer for eksempel fra 21.09, da en klausul fra Euronexts vilkår ble
gjengitt i anførselstegn uten å være lest. Se refleksjonsloggen, «Tilfelle 4:
et sitat som ikke fantes».

1. **Sluttmarkør.** Innlimte instruksjoner slutter med «SLUTT PÅ INSTRUKSJONEN».
   Markøren godtas også skrevet uten norske bokstaver: «SLUTT PAA
   INSTRUKSJONEN». Mangler linjen, er teksten avkortet: gjør ingenting, si fra.
2. **Vis, vent, skriv.** Ber brukeren om å se noe før det skrives, ender turen
   med visningen. Aldri vis og skriv i samme tur.
3. **Ingen påstand uten oppslag.** Ingenting om koden, filene eller historikken
   uten at det er slått opp. Usikker: vis kilden i stedet for å konkludere.
   Det gjelder også påstander i en innlimt instruksjon: slå dem opp før de
   skrives inn.
4. **`updated`-felter** settes fra `date +%Y-%m-%dT%H:%M`, aldri for hånd.
   Nye dokumenter under `docs/` og `_bmad-output/planning-artifacts/` får samme
   frontmatter som `prd.md`: `title`, `status` (`draft`, `final`, `aktiv` eller
   `sendt`), `created` (datoen fila først ble committet) og `updated`.
5. **Memloggene er append-only.** En feil rettes med en ny linje.
   Unntak: rå kildedata (regel 16) fjernes fra linjen der de står, linjen merkes
   `[raadata fjernet <dato>]`, og en ny linje nederst sier hvorfor. Brukt i
   `0ccb415`. Nye oppføringer i `docs/reflection-log.md` skrives over «# Joakims
   oppføringer», ikke nederst i fila. Joakims egne oppføringer står under
   «# Joakims oppføringer» (rettet 2026-10-03, D4 i kontrollen 26.09). `_bmad/scripts/memlog.py` skriver hele
   frontmatteren på nytt og tåler bare linjer på formen `nøkkel: verdi`.
   PRD-memloggen har kommentarlinjer i frontmatteren som skriptet fjerner eller
   endrer, så der legges nye linjer til direkte, nederst i fila.
   Da settes `updated` fra klokka i samme commit (regel 4), og bare den linjen
   i frontmatteren endres.
6. **Ingen nettverkskall i tester** (AD-8, håndhevet i `tests/conftest.py`).
   **Ingen API-kall uten avtale.** Kostnad måles med `/api/user` før og etter
   (`malinger.md` §7.1).
7. **Aldri force-push.** Hent før push.
8. **Én sak per commit.**
9. **Ingenting bygges før det er sagt fra.**
10. **`_privat/`, `data/` og `.env` committes aldri.**
11. **Siter bare det du har lest.** Ordrette sitater kommer bare fra dokumenter
    som er lest i samme økt. Ellers: si at kilden mangler. Aldri rekonstruer et
    sitat.
12. **Tall som spriker.** Når to dokumenter oppgir samme tall ulikt, skriv bare
    det de er enige om, og før spriket som åpent punkt.
13. **Diff etter omskriving.** Etter hver omskriving av et dokument: diff mot
    forrige versjon og let etter krav som er borte, ikke bare formuleringer som
    er endret.
14. **PRD-en revideres i samme mappe.** Aldri en ny datostemplet mappe ved
    siden av.
15. **Kvoten sjekkes ved øktstart.** Første ting i hver økt: les `/api/user`
    (gratis) med `EODHD_API_KEY` fra `.env`, aldri en annen nøkkel, og si hvor
    mange kall som er brukt i dag og hvor mange som er igjen.
    Kvoten nullstilles ved midnatt GMT, men `/api/user` viser gårsdagens tall til
    første kall etter det. Står `apiRequestsDate` på en tidligere dato, er det
    brukt 0 i dag (`malinger.md` §7.1). Ubrukte kall forsvinner. Kall nummer 21
    og videre trekker fra bonuskvoten `extraLimit` uten å stoppe (§11). Er det
    kall igjen sent på dagen, foreslå en bruk som svarer på noe åpent: en måling,
    en test mot ekte data, et øyeblikksbilde Epic 2 trenger. Foreslå, ikke bruk:
    regel 6 gjelder fortsatt, ingen kall uten avtale.
    *Presisert 2026-10-04:* «i dag» og «en tidligere dato» regnes i GMT. Fra
    midnatt norsk tid til midnatt GMT, kl. 02:00 om sommeren og kl. 01:00 om
    vinteren, står apiRequestsDate fortsatt på dagens dato i GMT, og kallene fra
    dagen før teller. Tilfellet er kvotesjekken 04.10 kl. 01:00.
16. **Ingen rå enkeltverdier fra kildene i sporede filer.** Rå enkeltverdier fra
    kildene (kurs, volum eller meldingsinnhold for en bestemt dag) skrives ikke
    i sporede filer. Tall vi har regnet ut selv, kan stå. Regel 10 dekker bare
    filer, og MOWI-tallene kom inn 23.09 etter at denne fila fantes.
17. **Product Brief er låst.** Briefen er arbeidskravet: den skal være på 1–2
    sider, med innleveringsfrist søndag 27.09.2026. `product-brief.md` er låst.
    Gjeldende tag er `arbeidskrav-product-brief-v7`; de eldre taggene står
    urørt, og versjon 2 i full lengde ligger i `arbeidskrav-product-brief-v2`.
    Fila endres ikke uten at Marian eller Joakim ber om det uttrykkelig. Må den
    endres før fristen, lages en ny tag med neste ledige nummer (`-v8`, `-v9`
    …); en tag flyttes aldri. Versjon 7 er om lag 790 ord (785, telt med `\w+`
    som i kontrollene av briefen) og fyller to sider, så en ny versjon skal ikke
    bli lengre. Tilbakemeldingen fra faglærerne føres i `innlevering.md`, ikke i
    briefen.
    *Presisert 2026-10-06, Marians beslutning kl. 12:42:* det faglærere legger
    inn i repoet selv, blir liggende urørt i sin egen fil og lenkes i
    «Dokumentene» (regel 19). Svar på e-post vi har sendt, føres i
    `innlevering.md`.
    *Lagt til 2026-10-06 (story 9.6):* gjeldende tag er nå
    `arbeidskrav-product-brief-v8`. Versjon 8 er 785 ord, telt på samme måte, og
    en ny versjon skal fortsatt ikke bli lengre.
18. **Hver instruksjon lagres ordrett, også når den skrives rett inn.** Den
    lagres i `docs/ai-prompts/<ÅÅÅÅ-MM-DD>.md` før den utføres, med klokkeslett.
    Når den er utført, legges en linje under med commitene og utfallet. Linjen
    begynner med **Utført:**, også når bare noe ble gjort eller svaret var en
    plan eller spørsmål uten commit, og da sier linjen det. Morgensjekken teller
    disse linjene. Ingen rådata eller nøkler (regel 16). Grunnen: emnesiden
    krever dokumentasjon av hvordan KI ble brukt, og instruksjonene er
    promptene. Det gjelder også korte svar som «ja». Sluttmarkøren i regel 1
    gjelder bare innlimt tekst. Tilfellet bak: et «ja» 26.09 ga `a23b3e5` uten å
    bli ført, og ble ført i ettertid i `3d9dca0`.
19. **README-en følger repoet.** Når et dokument eller en mappe som README-en
    nevner, legges til, flyttes, får nytt navn eller slettes, rettes
    «Dokumentene» og «Mappestruktur» i samme commit. Nye hoveddokumenter under
    `docs/` og `_bmad-output/planning-artifacts/`, for eksempel en ny
    kontrollrapport, `docs/kvalitetssikring.md` eller refleksjonsrapporten,
    føres i «Dokumentene» som lenke. Nye filer i en mappe som allerede er
    lenket, som `docs/ai-prompts/` og `_bmad-output/implementation-artifacts/`,
    trenger ikke egen linje. Endres koden slik at noe README-en sier om den,
    ikke lenger stemmer, rettes README-en i samme commit. `tests/test_readme.py`
    sjekker at hver lenke i README-en peker på noe som finnes.
20. **Felles arbeid står på begge.** Vi diskuterer og avgjør arbeidet sammen, og
    det meste skrives inn på én maskin. Hver commit får derfor den av oss som
    ikke committer, som medforfatter. Linjen står nederst i meldingen, i samme
    blokk som Claude-linjen. Er `git config user.name` Marian Osen:
    `Co-authored-by: Joakim Lund <joakim.lund@himolde.no>`. Er den Joakim Lund:
    `Co-authored-by: Marian Osen <marian.osen@himolde.no>`. Skriver Joakim selv
    på Marians maskin, og det står i instruksjonen, committes det med
    `--author="Joakim Lund <joakim.lund@himolde.no>"` og
    `Co-authored-by: Marian Osen <marian.osen@himolde.no>`. Da står den som
    skrev, som forfatter. Tilfellet bak: `b4cb9f2` ble ført av Joakim 25.09, men
    står med Marian som forfatter, fordi git-brukeren på maskinen er hennes. Den
    skrives ikke om (regel 7). Instruksjonen kl. 22:27 i dagsfila viser at
    Joakim førte den. Linjen betyr at begge har vært med på det som committes.
    Sier brukeren at noe er gjort alene, får de commitene ikke linjen. Commitene
    før 2026-09-25 har den ikke, og historikken skrives ikke om (regel 7).
21. **Tall skrives norsk der de leses, og som tall der de regnes.** Det sidene
    viser: desimalkomma, hardt mellomrom som tusenskille og foran %, og vanlig
    bindestrek (-) som minus, så tallet kan limes inn i et regneark. Hvor mange
    desimaler hver type tall har, bestemmes i én funksjon med tester, ikke i
    hver mal. Norsk tekst i dokumentene bruker også desimalkomma. I kode,
    basen, JSON og CSV: punktum og ingen tusenskille, og tall lagres som tall
    med full presisjon. Avrunding skjer bare der tallet vises. Siteres en
    kodeverdi med punktum i norsk tekst, står den i kodeformat. Tilfellet bak:
    29.09 viste sidene punktum (`"%.2f"` i malene og forklaringene i
    `signalberegning.py`), mens dokumentene hadde komma.
22. **En gren bruker bare testbaser.** Kode, tester og kjøringer på en gren
    rører aldri `data/db/ose.db`. Basen skrives bare av kveldshentingen, som
    kjører fra main. Grunnen: en vurdering som er skrevet, kan verken slettes
    eller skrives på nytt (AD-7), så en feil fra en gren kan ikke rettes.
    Besluttet av gruppen 05.10 kl. 19:17 (svar 3 under story 2.3 i
    `epics.md`), og ført her da 2.3 ble bygget.
