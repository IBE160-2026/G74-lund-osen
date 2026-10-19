-- 0007 - min_liste. Story 8.3, FR-101, FR-102, AD-3, AD-10, AD-16, AD-21.
--
-- Merkingen i Min liste er et eget datasett med webserveren som eneste
-- skriver (foeringen 2026-09-30 under AD-3). Tabellen har bare symbolet: en
-- rad betyr at aksjen er merket. Ingen kolonne for antall, beloep eller kurs,
-- for da er det en personlig portefoelje, som er utenfor v1 (story 8.3).
--
-- Merkingen gjelder maskinen, og en rad kan slettes igjen. Den er ikke et
-- uerstattelig lager som vurdering (AD-7), men en trigger mot aksje, som for
-- kurs, kursserie og vurdering i 0003 (AD-21), avviser et symbol som ikke
-- staar i lista. NOT EXISTS, ikke NOT IN, av samme grunn som der.
--
-- En aksje med en rad her kan fortsatt slettes fra aksje: triggeren i 0003
-- endres ikke, og porten leser bare symboler som staar i aksje.

CREATE TABLE min_liste (
    symbol TEXT PRIMARY KEY NOT NULL
);

CREATE TRIGGER min_liste_kjent_aksje_insert
BEFORE INSERT ON min_liste
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i min_liste');
END;

CREATE TRIGGER min_liste_kjent_aksje_update
BEFORE UPDATE OF symbol ON min_liste
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i min_liste');
END;
