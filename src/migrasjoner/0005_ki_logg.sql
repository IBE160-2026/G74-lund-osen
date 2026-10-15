-- 0005 - ki_logg. Story 4.3, FR-604, FR-605, AD-3, AD-7, AD-16.
--
-- KI-loggen er det KI-laget la til, med det regelen sa og det modellen fikk
-- (grunnlag, som JSON). Den kan ikke lages paa nytt, saa tabellen er
-- uerstattelig, som vurdering (AD-7). Porten (src/kilogg.py) har bare skriv
-- og lesemetoder, og adapteren skriver med INSERT, aldri med UPDATE eller
-- REPLACE. To triggere avviser UPDATE og DELETE, saa heller ikke en annen vei
-- inn i basen kan endre en rad.
--
-- Emnet har tre slag (story 4.2, svar 6 kl. 15:53): en aksje og en dato
-- (symbol satt), en melding (melding_id satt) eller dagen alene (ingen av
-- dem). CHECK-en sier hvilke felt hvert slag har. En rad per emne: den
-- unike indeksen bruker ifnull, fordi SQLite regner to NULL som ulike i en
-- UNIQUE-regel. Finnes raden, staar den, ogsaa naar modellen feilet
-- (FR-604, svar 2).
--
-- Ingen fremmednoekkel til vurdering eller aksje: raden er et oeyeblikksbilde
-- av hva modellen saa (AD-18), og en melding (plan A) har ingen aksje i
-- tabellen. Verdiene ellers (tjenestene, maskinvaren, tekst som ikke er tom)
-- kontrolleres av KIRad i porten. Basen sjekker formen.
--
-- dato er YYYY-MM-DD, som i vurdering. Adapteren oversetter ved grensen.

CREATE TABLE ki_logg (
    nr             INTEGER PRIMARY KEY,
    slag           TEXT    NOT NULL CHECK (slag IN ('aksje', 'melding', 'dag')),
    dato           TEXT    NOT NULL,
    symbol         TEXT,
    melding_id     TEXT,
    grunnlag       TEXT    NOT NULL,
    regelen        TEXT    NOT NULL,
    tekst          TEXT,
    besto          INTEGER NOT NULL CHECK (besto IN (0, 1)),
    grunn          TEXT,
    promptversjon  TEXT    NOT NULL CHECK (promptversjon <> ''),
    tjeneste       TEXT    NOT NULL,
    modell         TEXT    NOT NULL CHECK (modell <> ''),
    modell_id      TEXT,
    seed           INTEGER,
    temperatur     REAL,
    maskinvare     TEXT    CHECK (maskinvare IS NULL OR maskinvare IN ('gpu', 'cpu')),
    ollama_versjon TEXT,
    CHECK (
        (slag = 'aksje'   AND symbol IS NOT NULL AND melding_id IS NULL)
        OR (slag = 'melding' AND symbol IS NULL AND melding_id IS NOT NULL)
        OR (slag = 'dag'     AND symbol IS NULL AND melding_id IS NULL)
    ),
    CHECK (
        (besto = 1 AND tekst IS NOT NULL AND grunn IS NULL)
        OR (besto = 0 AND grunn IS NOT NULL)
    )
);

CREATE UNIQUE INDEX ki_logg_ett_emne
    ON ki_logg (slag, dato, ifnull(symbol, ''), ifnull(melding_id, ''));

CREATE TRIGGER ki_logg_endres_ikke
BEFORE UPDATE ON ki_logg
BEGIN
    SELECT RAISE(ABORT, 'en rad i ki_logg endres ikke (AD-7)');
END;

CREATE TRIGGER ki_logg_slettes_ikke
BEFORE DELETE ON ki_logg
BEGIN
    SELECT RAISE(ABORT, 'en rad i ki_logg slettes ikke (AD-7)');
END;
