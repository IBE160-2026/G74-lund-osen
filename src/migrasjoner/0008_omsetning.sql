-- 0008 - omsetning. Story 2.13, FR-413, NFR-01, AD-6, AD-16.
--
-- Median omsetning for aksjene i lista over Oslo Boers, maalt med kallene som
-- er igjen etter kveldshentingen (avgjoerelsen 28.10 kl. 22:17). Tallet og
-- datoen staar her; raadataene staar i data/raa/ (AD-6).
--
-- En rad per maaling. En ny maaling av samme aksje legges til med et nytt
-- maalt og skriver aldri over en gammel, saa primaernoekkelen er (symbol,
-- maalt). maalt er starten paa kjoeringen i UTC med offset, som hentet.
-- median_omsetning er NOK, volume x close per handelsdag og medianen over
-- vinduet fra-til, uavrundet (regel 21). Feilet kallet, eller ga ingen rad
-- tall, staar feil i stedet for medianen, og aksjen regnes som maalt.
--
-- Ingen trigger mot aksje: aksjene som maales, staar ikke i lista. Ingen
-- tabell eller trigger som finnes, endres.

CREATE TABLE omsetning (
    symbol TEXT NOT NULL CHECK (symbol <> ''),
    maalt TEXT NOT NULL,
    fra TEXT NOT NULL,
    til TEXT NOT NULL CHECK (fra <= til),
    handelsdager INTEGER NOT NULL CHECK (handelsdager >= 0),
    dager_uten_volum INTEGER NOT NULL CHECK (dager_uten_volum >= 0 AND dager_uten_volum <= handelsdager),
    rader_uten_tall INTEGER NOT NULL CHECK (rader_uten_tall >= 0),
    median_omsetning REAL CHECK (median_omsetning >= 0),
    feil TEXT,
    CHECK ((median_omsetning IS NULL) = (feil IS NOT NULL)),
    PRIMARY KEY (symbol, maalt)
);
