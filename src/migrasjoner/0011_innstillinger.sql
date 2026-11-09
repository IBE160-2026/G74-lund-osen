-- 0011 - innstillinger. Story 8.10, FR-110, AD-3, AD-10, AD-16.
--
-- Valgene i «Innstillinger» øverst: én rad per valg, verdien 0 (av) eller 1
-- (på). Ingen rad betyr på. vis_hjelp er story 8.10, og vis_ki_tekst story
-- 8.10b, i samme tabell (spoersmaal 2 i spec-8-10-innstillinger-oeverst.md).
-- Webserveren er eneste skriver, som for Min liste (foeringen 30.09 under
-- AD-3). Valgene gjelder maskinen; det er ingen innlogging. Ingen tabell
-- eller trigger som finnes, endres.

CREATE TABLE innstilling (
    navn TEXT PRIMARY KEY NOT NULL CHECK (navn IN ('vis_hjelp', 'vis_ki_tekst')),
    verdi INTEGER NOT NULL CHECK (verdi IN (0, 1))
);
