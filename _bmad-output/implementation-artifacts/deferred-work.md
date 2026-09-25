- source_spec: `_bmad-output/implementation-artifacts/spec-1-4a-lesegrensen-kursleser-og-oversetteren.md`
  summary: Tre konsumenter faller fortsatt tilbake fra adjusted_close til close (aksjedetalj.py:106, markedsoversikt.py:99, signalberegning.py:86).
  evidence: Bekreftet med grep 2026-09-24. Fantes foer 1.4a; AD-19 sier at oversettelsen skjer ett sted. Story 1.4b flytter konsumentene til Kursrad, og testene der boer kreve at fallbacken er borte.
  resolved: Loest i story 1.4b (c5efd05, 2026-09-25). De tre konsumentene leser justert_slutt fra Kursrad uten fallback, og tests/test_konsumentene.py feiler hvis fallbacken eller EODHD-noeklene kommer tilbake.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4b-konsumentene-leser-kursrad.md`
  summary: Naar hentet i oeyeblikksbildet ikke kan leses, sier forsiden «Ingen kursdata funnet i data/» selv om dataene finnes. Meldingen er misvisende.
  evidence: Funnet i gjennomgangen av 1.4b (triageloggen, rad 1). SnapshotLeser gjoer da hele oeyeblikksbildet manglende (1.4a), og fotnoten ligger inne i {% if rader %} i index.html. Laast av test_uleselig_hentet_gjoer_hele_oeyeblikksbildet_manglende. Tas naar appen leser fra SQLite (story 2.2, se innledningen til Epic 2 i epics.md), eller foer hvis det blir aktuelt. Rettet 2026-09-25: her sto 1.5, som ikke bytter appen til SQLite.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4c-rydding-kurskilde-ut-sist-hentet-inn.md`
  summary: Datoen i overskriften paa forsiden er rader[0].dato, altsaa datoen til den oeverste raden etter sorteringen, og den kan motsi sidens eldste tidsstempel naar symbolene har ulike siste datoer.
  evidence: Funnet i gjennomgangen av 1.4c (triageloggen, rad 12). Fantes foer 1.4c i index.html. I et oeyeblikksbilde har alle symbolene samme hentet, saa det synes foerst naar symbolene hentes hver for seg og ett kan feile (AD-15, Epic 2).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4c-rydding-kurskilde-ut-sist-hentet-inn.md`
  summary: Spoersmaal til UX-gjennomgangen i story 8.2. Med en fersk rad og fjorten foreldede viser de fjorten samme tid som siden, og den ferske viser ingen tid. Er det den merkingen vi vil ha?
  evidence: Funnet i gjennomgangen av 1.4c (triageloggen, rad 4). Oppfoerselen er FR-101 ordrett («En rad med eldre tidsstempel enn det nyeste viser sitt eget»). Leseren ser hvilke rader som er gamle, men ikke naar den ferske ble hentet. FR-101 endres ikke naa.
