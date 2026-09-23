# Regler for KI-økter i dette repoet

Gjelder alle økter, uansett hvem som kjører dem. Alle reglene har vært i bruk,
og grunnene står i `docs/reflection-log.md` og memloggene under `_bmad-output/`.
Regel 11 kommer for eksempel fra 21.09, da en klausul fra Euronexts vilkår ble
gjengitt i anførselstegn uten å være lest. Se refleksjonsloggen, «Tilfelle 4:
et sitat som ikke fantes».

1. **Sluttmarkør.** Innlimte instruksjoner slutter med «SLUTT PÅ INSTRUKSJONEN».
   Mangler linjen, er teksten avkortet: gjør ingenting, si fra.
2. **Vis, vent, skriv.** Ber brukeren om å se noe før det skrives, ender turen
   med visningen. Aldri vis og skriv i samme tur.
3. **Ingen påstand uten oppslag.** Ingenting om koden, filene eller historikken
   uten at det er slått opp. Usikker: vis kilden i stedet for å konkludere.
   Det gjelder også påstander i en innlimt instruksjon: slå dem opp før de
   skrives inn.
4. **`updated`-felter** settes fra `date +%Y-%m-%dT%H:%M`, aldri for hånd.
5. **Memloggene er append-only.** En feil rettes med en ny linje.
   Nye oppføringer i `docs/reflection-log.md` skrives over «# Joakims
   oppføringer», ikke nederst i fila.
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
    (gratis) og si hvor mange kall som er brukt i dag og hvor mange som er igjen.
    Kvoten nullstilles ved midnatt GMT, men `/api/user` viser gårsdagens tall til
    første kall etter det. Står `apiRequestsDate` på en tidligere dato, er det
    brukt 0 i dag (`malinger.md` §7.1). Ubrukte kall forsvinner. Kall nummer 21
    og videre trekker fra bonuskvoten `extraLimit` uten å stoppe (§11). Er det
    kall igjen sent på dagen, foreslå en bruk som svarer på noe åpent: en måling,
    en test mot ekte data, et øyeblikksbilde Epic 2 trenger. Foreslå, ikke bruk:
    regel 6 gjelder fortsatt, ingen kall uten avtale.
