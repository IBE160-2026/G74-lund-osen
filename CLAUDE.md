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
   oppføringer», ikke nederst i fila. `_bmad/scripts/memlog.py` skriver hele
   frontmatteren på nytt og tåler bare linjer på formen `nøkkel: verdi`.
   PRD-memloggen har kommentarlinjer i frontmatteren som skriptet fjerner eller
   endrer, så der legges nye linjer til direkte, nederst i fila.
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
    …); en tag flyttes aldri. Versjon 7 er om lag 750 ord og fyller to sider, så
    en ny versjon skal ikke bli lengre. Tilbakemeldingen fra faglærerne føres i
    `innlevering.md`, ikke i briefen.
18. **Hver innlimte instruksjon lagres ordrett.** Den lagres i
    `docs/ai-prompts/<ÅÅÅÅ-MM-DD>.md` før den utføres, med klokkeslett. Når den
    er utført, legges en linje under med commitene og utfallet. Linjen begynner
    med **Utført:**, også når bare noe ble gjort eller svaret var en plan eller
    spørsmål uten commit, og da sier linjen det. Morgensjekken teller disse
    linjene. Ingen rådata eller nøkler (regel 16). Grunnen: emnesiden krever
    dokumentasjon av hvordan KI ble brukt, og instruksjonene er promptene.
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
