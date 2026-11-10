-- 0012 - notat. Story 8.21, AD-3, AD-10, AD-16 (gruppens svar 10.11 kl. 14:32).
--
-- Egne notater paa aksjesiden: en rad per notat, med dagen siden viste da
-- notatet ble skrevet (dato), teksten og tidspunktet det ble lagret (laget).
-- Webserveren er eneste skriver, som for min_liste, oenske og innstilling
-- (spoersmaal 8 i spec-8-21-egne-notater-paa-aksjesiden.md). Et notat kan
-- slettes. Det er ikke et uerstattelig lager som vurdering (AD-7).
--
-- Triggeren avviser et symbol som ikke staar i aksje, som i 0007. NOT
-- EXISTS, ikke NOT IN, av samme grunn som der. Ingen tabell eller trigger
-- som finnes, endres.

CREATE TABLE notat (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL CHECK (symbol <> ''),
    -- Gjennomgangen (BH4): en dato som finnes, ikke bare formen.
    dato TEXT NOT NULL CHECK (
        length(dato) = 10 AND dato GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(dato) IS dato
    ),
    tekst TEXT NOT NULL CHECK (length(trim(tekst)) >= 1 AND length(tekst) <= 280),
    laget TEXT NOT NULL CHECK (julianday(laget) IS NOT NULL)
);

CREATE INDEX notat_symbol ON notat (symbol, dato);

CREATE TRIGGER notat_kjent_aksje_insert
BEFORE INSERT ON notat
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i notat');
END;

CREATE TRIGGER notat_kjent_aksje_update
BEFORE UPDATE OF symbol ON notat
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i notat');
END;
