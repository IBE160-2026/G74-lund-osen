-- 0014 - regnet. Story 2.17, FR-408, FR-409, AD-7, AD-16 (gruppens svar
-- 2026-11-14 kl. 05:41-05:49).
--
-- En rad i vurdering er enten skrevet av kveldens henting for inneveerende
-- boersdag (kveld) eller regnet i ettertid av kursene i basen for en
-- tidligere boersdag uten rad (ettertid). Kveldsradene er uerstattelige som
-- foer (AD-7). Radene i ettertid er avledet av kursene, saa de kan regnes paa
-- nytt eller slettes, men bare gjennom en egen vei som aldri roerer en
-- kveldsrad (SqliteEttertidslager).
--
-- Kolonnen legges til med ADD COLUMN, uten DROP TABLE, som i 0004. Alle
-- radene som finnes, er skrevet av hentingen eller demokommandoen gjennom
-- SqliteVurderingslager.skriv, saa de faar 'kveld'. En rad i ettertid har
-- alltid en vurdering, aldri en grunn: en dag uten nok kurser faar ingen rad.
-- CHECK-en i kolonnen kan vise til andre kolonner i raden, som i 0004.

ALTER TABLE vurdering ADD COLUMN regnet TEXT NOT NULL DEFAULT 'kveld'
    CHECK (regnet IN ('kveld', 'ettertid') AND (regnet = 'kveld' OR grunn IS NULL));

-- En kveldsrad blir aldri en rad i ettertid. Kveldens rad for samme dag kan
-- skrive over en rad i ettertid, aldri omvendt. Ingen trigger for DELETE:
-- testene sletter rader i testbaser, og vurdering hadde ingen slik trigger
-- foer. Veien som sletter, sletter bare radene i ettertid.
CREATE TRIGGER vurdering_kveld_blir_ikke_ettertid
BEFORE UPDATE OF regnet ON vurdering
WHEN OLD.regnet = 'kveld' AND NEW.regnet <> 'kveld'
BEGIN
    SELECT RAISE(ABORT, 'en kveldsrad blir aldri en rad i ettertid');
END;
