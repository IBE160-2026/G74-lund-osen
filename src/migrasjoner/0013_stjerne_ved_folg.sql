-- 0013 - stjernen ved «Følg». Story 8.26, tillegg 3 (gruppens svar
-- 2026-11-11 kl. 17:47), AD-3, AD-10, AD-21.
--
-- En aksje som følges med «Følg», får stjerne og står i Min liste med en
-- gang. Nettsiden skriver stjernen i min_liste i samme transaksjon som
-- ønsket i oenske, og ingenting annet (AD-3, regel 22). En aksje som venter
-- på hentingen, står ikke i aksje ennå, så triggerne fra 0007 avviste den.
-- Nå godtas også et symbol med et ønske om å følge som ikke er avvist, og
-- som ikke er tatt i bruk; når hentingen tar det i bruk, står aksjen i aksje.
-- Ellers er triggerne som i 0007: et ukjent symbol avvises. NOT EXISTS, ikke
-- NOT IN, av samme grunn som der.

DROP TRIGGER min_liste_kjent_aksje_insert;
DROP TRIGGER min_liste_kjent_aksje_update;

CREATE TRIGGER min_liste_kjent_aksje_insert
BEFORE INSERT ON min_liste
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
 AND NOT EXISTS (
    SELECT 1 FROM oenske
    WHERE symbol = NEW.symbol AND handling = 'folg' AND tatt_i_bruk IS NULL AND avvist IS NULL
 )
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i min_liste');
END;

CREATE TRIGGER min_liste_kjent_aksje_update
BEFORE UPDATE OF symbol ON min_liste
WHEN NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)
 AND NOT EXISTS (
    SELECT 1 FROM oenske
    WHERE symbol = NEW.symbol AND handling = 'folg' AND tatt_i_bruk IS NULL AND avvist IS NULL
 )
BEGIN
    SELECT RAISE(ABORT, 'ukjent aksje i min_liste');
END;
