-- 0016 - eksdato. Story 2.14, FR-414, AD-3, AD-10, AD-16 (gruppens svar
-- 2026-11-24 kl. 13:05).
--
-- Kommende eks.datoer, foert inn for haand fra selskapenes egne sider med
-- kommandoen src/eksdato.py. En rad per symbol: den kommende eks.datoen,
-- datoen den ble sjekket, og hvor den ble lest. En ny sjekk av samme dato
-- oppdaterer sjekket, og en flyttet dato erstatter den gamle, saa tabellen
-- er ikke et uerstattelig lager som vurdering (AD-7).
--
-- Kommandoen er eneste skriver. Webserveren skriver aldri tabellen, og
-- ingen eks.dato staar i en sporet fil (regel 16), saa migrasjonen legger
-- ikke inn noen rad.
--
-- Datoene er ISO-datoer som finnes, som i 0012. En eks.dato foer dagen den
-- ble sjekket, er ikke en kommende dato. Triggerne avviser et symbol som
-- ikke staar i aksje, som i 0007 og 0012. Ingen tabell eller trigger som
-- finnes, endres.

CREATE TABLE eksdato (
    symbol TEXT PRIMARY KEY NOT NULL CHECK (symbol <> ''),
    eks_dato TEXT NOT NULL CHECK (
        length(eks_dato) = 10
        AND eks_dato GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        AND date(eks_dato) IS eks_dato
    ),
    sjekket TEXT NOT NULL CHECK (
        length(sjekket) = 10
        AND sjekket GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        AND date(sjekket) IS sjekket
        AND sjekket <= eks_dato
    ),
    kilde TEXT NOT NULL CHECK (length(trim(kilde)) >= 1 AND length(kilde) <= 500)
);

CREATE TRIGGER eksdato_kjent_aksje_insert
BEFORE INSERT ON eksdato
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i eksdato');
END;

CREATE TRIGGER eksdato_kjent_aksje_update
BEFORE UPDATE OF symbol ON eksdato
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i eksdato');
END;
