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
4. **`updated`-felter** settes fra `date +%Y-%m-%dT%H:%M`, aldri for hånd.
5. **Memloggene er append-only.** En feil rettes med en ny linje.
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
