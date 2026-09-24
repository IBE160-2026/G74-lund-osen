- source_spec: `_bmad-output/implementation-artifacts/spec-1-4a-lesegrensen-kursleser-og-oversetteren.md`
  summary: Tre konsumenter faller fortsatt tilbake fra adjusted_close til close (aksjedetalj.py:106, markedsoversikt.py:99, signalberegning.py:86).
  evidence: Bekreftet med grep 2026-09-24. Fantes foer 1.4a; AD-19 sier at oversettelsen skjer ett sted. Story 1.4b flytter konsumentene til Kursrad, og testene der boer kreve at fallbacken er borte.
