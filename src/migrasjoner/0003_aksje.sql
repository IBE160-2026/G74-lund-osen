-- 0003 - aksje. Story 1.9, AD-4, AD-7, AD-16, AD-18, AD-21, G10 i
-- kodegjennomgang-epic-1.md.
--
-- aksje er universet, de femten i AKSJEUNIVERS i kursdata.py, med de samme
-- fire feltene som Aksje. En test holder tabellen og AKSJEUNIVERS like, felt
-- for felt og i samme rekkefoelge (ORDER BY rowid). Endres universet, er det
-- en ny migrasjon og en endring i kursdata.py i samme commit.
--
-- symbol er formen NewsWeb bruker (EQNR), ticker formen EODHD bruker
-- (EQNR.OL). kurs, kursserie og vurdering bruker symbol.
--
-- De tre tabellene peker paa aksje med triggere, ikke fremmednoekler, av
-- tre grunner. SQLite haandhever fremmednoekler bare naar tilkoblingen har
-- slaatt dem paa, og en trigger virker alltid (samme grunn som i 0002).
-- PRAGMA foreign_keys = ON gjoer ingenting inne i en transaksjon, og
-- loeperen kjoerer hver migrasjon i BEGIN IMMEDIATE. Og ALTER TABLE kan ikke
-- legge en fremmednoekkel paa en kolonne som finnes: kurs, kursserie og
-- vurdering maatte blitt bygget om, og vurdering er uerstattelig (AD-7).
--
-- Triggerne bruker NOT EXISTS, ikke NOT IN. NULL NOT IN (...) er NULL, og
-- da slaar triggeren ikke til. kursserie.symbol er en TEXT PRIMARY KEY, som
-- i SQLite kan vaere NULL.
--
-- vurdering peker paa aksje, aldri paa kurs (AD-18).

CREATE TABLE aksje (
    symbol TEXT PRIMARY KEY NOT NULL,
    ticker TEXT NOT NULL UNIQUE,
    navn   TEXT NOT NULL,
    sektor TEXT NOT NULL
);

INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES
    ('EQNR', 'EQNR.OL', 'Equinor', 'Energi'),
    ('DNB', 'DNB.OL', 'DNB Bank', 'Finans'),
    ('KOG', 'KOG.OL', 'Kongsberg Gruppen', 'Industri'),
    ('AKRBP', 'AKRBP.OL', 'Aker BP', 'Energi'),
    ('NHY', 'NHY.OL', 'Norsk Hydro', 'Materialer'),
    ('FRO', 'FRO.OL', 'Frontline', 'Shipping'),
    ('VAR', 'VAR.OL', 'Vår Energi', 'Energi'),
    ('TEL', 'TEL.OL', 'Telenor', 'Telekom'),
    ('YAR', 'YAR.OL', 'Yara International', 'Materialer'),
    ('MOWI', 'MOWI.OL', 'Mowi', 'Sjømat'),
    ('ORK', 'ORK.OL', 'Orkla', 'Konsum'),
    ('SALM', 'SALM.OL', 'SalMar', 'Sjømat'),
    ('GJF', 'GJF.OL', 'Gjensidige Forsikring', 'Finans'),
    ('DNO', 'DNO.OL', 'DNO', 'Energi'),
    ('MPCC', 'MPCC.OL', 'MPC Container Ships', 'Shipping');

-- En base i versjon 2 kan ha rader for et symbol som ikke staar over.
-- Triggerne under ser bare nye rader, saa de gamle ville blitt staaende uten
-- aksje, og radene i vurdering kan verken slettes eller skrives paa nytt
-- (AD-7). Migrasjonen stopper derfor, loeperen ruller den tilbake, og basen
-- staar paa versjon 2 med feilen synlig. RAISE finnes bare i triggere, saa
-- kontrollen er en CHECK paa en hjelpetabell som fjernes igjen.

CREATE TABLE kontroll_0003 (
    rader_uten_aksje INTEGER NOT NULL CHECK (rader_uten_aksje = 0)
);

INSERT INTO kontroll_0003 (rader_uten_aksje)
SELECT (SELECT count(*) FROM kurs
        WHERE NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = kurs.symbol))
     + (SELECT count(*) FROM kursserie
        WHERE NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = kursserie.symbol))
     + (SELECT count(*) FROM vurdering
        WHERE NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = vurdering.symbol));

DROP TABLE kontroll_0003;

CREATE TRIGGER kurs_kjent_aksje_insert
BEFORE INSERT ON kurs
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i kurs');
END;

CREATE TRIGGER kurs_kjent_aksje_update
BEFORE UPDATE OF symbol ON kurs
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i kurs');
END;

CREATE TRIGGER kursserie_kjent_aksje_insert
BEFORE INSERT ON kursserie
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i kursserie');
END;

CREATE TRIGGER kursserie_kjent_aksje_update
BEFORE UPDATE OF symbol ON kursserie
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i kursserie');
END;

CREATE TRIGGER vurdering_kjent_aksje_insert
BEFORE INSERT ON vurdering
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i vurdering');
END;

CREATE TRIGGER vurdering_kjent_aksje_update
BEFORE UPDATE OF symbol ON vurdering
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i vurdering');
END;

-- En aksje med rader i kurs, kursserie eller vurdering kan ikke slettes.
-- Radene i vurdering kan verken slettes eller skrives paa nytt (AD-7), og de
-- ville blitt staaende uten aksje. En aksje uten rader kan slettes: aksje er
-- oppsett, ikke et uerstattelig lager. Symbolet kan aldri endres, fordi det
-- er det radene peker paa. navn og sektor kan endres, og ticker saa lenge
-- ingen annen aksje har den.

CREATE TRIGGER aksje_slettes_ikke_med_rader
BEFORE DELETE ON aksje
WHEN EXISTS (SELECT 1 FROM kurs WHERE symbol = OLD.symbol)
  OR EXISTS (SELECT 1 FROM kursserie WHERE symbol = OLD.symbol)
  OR EXISTS (SELECT 1 FROM vurdering WHERE symbol = OLD.symbol)
BEGIN
    SELECT RAISE(ABORT, 'en aksje med rader slettes ikke');
END;

CREATE TRIGGER aksje_symbol_endres_ikke
BEFORE UPDATE OF symbol ON aksje
WHEN NEW.symbol IS NOT OLD.symbol
BEGIN
    SELECT RAISE(ABORT, 'symbolet til en aksje endres ikke');
END;

-- REPLACE sletter raden som er i veien uten aa kjoere DELETE-triggere (med
-- mindre recursive_triggers er slaatt paa). INSERT OR REPLACE med en ticker
-- som finnes, eller UPDATE OR REPLACE av ticker, ville da fjernet en aksje
-- med rader. En INSERT eller en ny ticker som kolliderer, avvises derfor
-- foer konflikten loeses, ogsaa for en aksje uten rader og ogsaa med
-- OR IGNORE og ON CONFLICT DO NOTHING. En ny aksje er en ny migrasjon.

CREATE TRIGGER aksje_erstattes_ikke_insert
BEFORE INSERT ON aksje
WHEN EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol OR ticker = NEW.ticker)
BEGIN
    SELECT RAISE(ABORT, 'en aksje erstattes ikke');
END;

CREATE TRIGGER aksje_erstattes_ikke_update
BEFORE UPDATE OF ticker ON aksje
WHEN EXISTS (SELECT 1 FROM aksje WHERE ticker = NEW.ticker AND symbol IS NOT OLD.symbol)
BEGIN
    SELECT RAISE(ABORT, 'en aksje erstattes ikke');
END;
