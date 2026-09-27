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
