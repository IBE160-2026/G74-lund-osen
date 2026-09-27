-- 0002 - grunn og vurdering. Story 1.6, FR-408, AD-7, AD-18, punkt 24 i prd.md §8.
--
-- vurdering er det loesningen mente om hver aksje, en rad per symbol og
-- boersdag. Den kan ikke regnes ut paa nytt, saa tabellen er uerstattelig
-- (AD-7) og har ingen fremmednoekkel til kurs (AD-18). Kursen kopieres inn.
--
-- En rad har enten vurderingen eller en grunn, aldri begge og aldri ingen av
-- delene (punkt 24). Er grunn tom, er alle de sju vurderingsfeltene satt. Er
-- grunn satt, er alle sju NULL, ogsaa kursfeltene. CHECK-en sjekker bare
-- dette. Verdiene selv kontrolleres av Vurdering i porten, fordi en ny regel i
-- en CHECK krever at tabellen bygges om.
--
-- Grunnene er rader i tabellen grunn, ikke en CHECK. En ny grunn er da en
-- INSERT INTO grunn i en ny migrasjon, uten DROP og uten ombygging. To
-- triggere avviser en grunn som ikke staar der. Det er triggere og ikke en
-- fremmednoekkel fordi SQLite bare haandhever fremmednoekler naar
-- tilkoblingen har slaatt dem paa, og en trigger virker alltid.
--
-- Relevante meldinger (FR-408) kommer senere, som en kolonne som kan vaere
-- tom (ALTER TABLE vurdering ADD COLUMN). NULL betyr da ikke registrert.
--
-- dato er YYYY-MM-DD, som i kurs. Adapteren oversetter til date ved grensen.

CREATE TABLE grunn (
    navn TEXT PRIMARY KEY
);

INSERT INTO grunn (navn) VALUES
    ('symbol_feilet'),
    ('kurs_ikke_fra_dagen'),
    ('signal_ikke_regnet');

CREATE TABLE vurdering (
    symbol        TEXT    NOT NULL,
    dato          TEXT    NOT NULL,
    styrke        INTEGER,
    retning       TEXT,
    trend         INTEGER,
    bevegelse     INTEGER,
    interesse     INTEGER,
    slutt         REAL,
    justert_slutt REAL,
    grunn         TEXT,
    PRIMARY KEY (symbol, dato),
    CHECK (
        (grunn IS NULL
            AND styrke IS NOT NULL AND retning IS NOT NULL
            AND trend IS NOT NULL AND bevegelse IS NOT NULL
            AND interesse IS NOT NULL
            AND slutt IS NOT NULL AND justert_slutt IS NOT NULL)
        OR
        (grunn IS NOT NULL
            AND styrke IS NULL AND retning IS NULL
            AND trend IS NULL AND bevegelse IS NULL
            AND interesse IS NULL
            AND slutt IS NULL AND justert_slutt IS NULL)
    )
);

CREATE TRIGGER vurdering_kjent_grunn_insert
BEFORE INSERT ON vurdering
WHEN NEW.grunn IS NOT NULL AND NEW.grunn NOT IN (SELECT navn FROM grunn)
BEGIN
    SELECT RAISE(ABORT, 'ukjent grunn i vurdering');
END;

CREATE TRIGGER vurdering_kjent_grunn_update
BEFORE UPDATE OF grunn ON vurdering
WHEN NEW.grunn IS NOT NULL AND NEW.grunn NOT IN (SELECT navn FROM grunn)
BEGIN
    SELECT RAISE(ABORT, 'ukjent grunn i vurdering');
END;
