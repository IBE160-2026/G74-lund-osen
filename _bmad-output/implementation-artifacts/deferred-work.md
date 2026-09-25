- source_spec: `_bmad-output/implementation-artifacts/spec-1-4a-lesegrensen-kursleser-og-oversetteren.md`
  summary: Tre konsumenter faller fortsatt tilbake fra adjusted_close til close (aksjedetalj.py:106, markedsoversikt.py:99, signalberegning.py:86).
  evidence: Bekreftet med grep 2026-09-24. Fantes foer 1.4a; AD-19 sier at oversettelsen skjer ett sted. Story 1.4b flytter konsumentene til Kursrad, og testene der boer kreve at fallbacken er borte.
  resolved: Loest i story 1.4b (c5efd05, 2026-09-25). De tre konsumentene leser justert_slutt fra Kursrad uten fallback, og tests/test_konsumentene.py feiler hvis fallbacken eller EODHD-noeklene kommer tilbake.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-4b-konsumentene-leser-kursrad.md`
  summary: Naar hentet i oeyeblikksbildet ikke kan leses, sier forsiden «Ingen kursdata funnet i data/» selv om dataene finnes. Meldingen er misvisende.
  evidence: Funnet i gjennomgangen av 1.4b (triageloggen, rad 1). SnapshotLeser gjoer da hele oeyeblikksbildet manglende (1.4a), og fotnoten ligger inne i {% if rader %} i index.html. Laast av test_uleselig_hentet_gjoer_hele_oeyeblikksbildet_manglende. Tas naar appen leser fra SQLite (1.5), eller foer hvis det blir aktuelt.
