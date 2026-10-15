-- 0005 - ki_logg. Story 4.3, FR-604, FR-605, AD-3, AD-7, AD-16.
--
-- KI-loggen er det KI-laget la til, med det regelen sa og det modellen fikk
-- (grunnlag, som JSON). Den kan ikke lages paa nytt, saa tabellen er
-- uerstattelig, som vurdering (AD-7). Porten (src/kilogg.py) har bare skriv
-- og lesemetoder, og adapteren skriver med INSERT, aldri med UPDATE eller
-- REPLACE. To triggere avviser UPDATE og DELETE. En tredje stopper en INSERT
-- for et emne som finnes, foer konflikten loeses: REPLACE sletter ellers raden
-- som er i veien uten aa kjoere DELETE-triggeren (med mindre
-- recursive_triggers er paa), som i 0003. Den bruker RAISE(IGNORE), saa
-- adapterens INSERT ... ON CONFLICT DO NOTHING gir 0 rader og skriv gir
-- False (svar 2). Triggerne stopper ikke DROP TRIGGER, DROP TABLE eller en
-- senere migrasjon. Det er migrasjonsfilene og gjennomgangen som gjoer det.
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
-- tabellen. Basen sjekker de samme reglene som KIRad i porten der en CHECK
-- kan uttrykke dem, fordi en rad som ikke kan leses av adapteren, heller ikke
-- kan slettes (gjennomgangen av 4.3). En tekst som ikke besto kontrollen,
-- staar med grunnen (besto = 0, tekst satt). Feilet modellen, er tekst NULL.
--
-- dato er YYYY-MM-DD, som i vurdering. Adapteren oversetter ved grensen.

CREATE TABLE ki_logg (
    nr             INTEGER PRIMARY KEY,
    slag           TEXT    NOT NULL CHECK (slag IN ('aksje', 'melding', 'dag')),
    dato           TEXT    NOT NULL CHECK (dato IS date(dato)),
    symbol         TEXT    CHECK (symbol IS NULL OR (symbol <> '' AND symbol = trim(symbol) AND symbol = upper(symbol))),
    melding_id     TEXT    CHECK (melding_id IS NULL OR (melding_id <> '' AND melding_id = trim(melding_id))),
    grunnlag       TEXT    NOT NULL CHECK (json_valid(grunnlag) AND json_type(grunnlag) = 'object'),
    regelen        TEXT    NOT NULL CHECK (trim(regelen) <> ''),
    tekst          TEXT    CHECK (tekst IS NULL OR trim(tekst) <> ''),
    besto          INTEGER NOT NULL CHECK (besto IN (0, 1)),
    grunn          TEXT    CHECK (grunn IS NULL OR trim(grunn) <> ''),
    promptversjon  TEXT    NOT NULL CHECK (trim(promptversjon) <> ''),
    tjeneste       TEXT    NOT NULL CHECK (tjeneste IN ('lokal', 'gemini', 'anthropic', 'openai')),
    modell         TEXT    NOT NULL CHECK (trim(modell) <> ''),
    modell_id      TEXT,
    seed           INTEGER CHECK (seed IS NULL OR typeof(seed) = 'integer'),
    temperatur     REAL    CHECK (temperatur IS NULL OR (typeof(temperatur) = 'real' AND temperatur >= 0)),
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

CREATE TRIGGER ki_logg_erstattes_ikke
BEFORE INSERT ON ki_logg
WHEN EXISTS (
    SELECT 1 FROM ki_logg
    WHERE slag = NEW.slag AND dato = NEW.dato
      AND ifnull(symbol, '') = ifnull(NEW.symbol, '')
      AND ifnull(melding_id, '') = ifnull(NEW.melding_id, '')
)
BEGIN
    SELECT RAISE(IGNORE);
END;

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
