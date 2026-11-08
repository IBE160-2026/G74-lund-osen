-- 0009 - lista. Story 2.11, FR-412, FR-409, AD-3, AD-7, AD-16, AD-21.
--
-- aksje er lista appen foelger, og faar naar hver aksje kom inn (inn) og
-- naar den gikk ut (ut). ut er den foerste dagen aksjen ikke er i lista,
-- saa hentingen dagen foer er den siste for den. NULL i inn betyr at aksjen
-- er med fra foerste henting, og NULL i ut at den er i lista. Datoene er
-- tekst paa formen AAAA-MM-DD, som dato i kurs og vurdering.
--
-- De femten som staar, faar den foerste raden sin i vurdering som inn: den
-- dagen appen begynte aa foelge dem. Kursene gaar et aar lenger tilbake,
-- fordi foerste henting henter historikken (spoersmaal 1 i
-- spec-2-11-lista-leses-fra-basen.md). En aksje uten rad i vurdering faar NULL.
--
-- En aksje som er tatt ut, slettes ikke: kursene og vurderingene staar
-- (AD-7, AD-21), og triggeren i 0003 hindrer at den slettes med rader.
--
-- Bransjen (sektor) maa vaere en av de 13 i designregler.md §4, for en ny
-- aksje og ved en endring (tillegget 13.10, N3, svar 24). Triggerne ser bare
-- nye rader og endringer; de femten har alle en av de 13. Ingen tabell eller
-- trigger som finnes, endres.

ALTER TABLE aksje ADD COLUMN inn TEXT CHECK (inn IS NULL OR inn GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]');
ALTER TABLE aksje ADD COLUMN ut TEXT CHECK (
    ut IS NULL OR (ut GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND (inn IS NULL OR inn < ut))
);

UPDATE aksje SET inn = (SELECT MIN(dato) FROM vurdering WHERE vurdering.symbol = aksje.symbol);

CREATE TRIGGER aksje_bransje_insert
BEFORE INSERT ON aksje
WHEN NEW.sektor IS NULL OR NEW.sektor NOT IN (
    'Energi', 'Finans', 'Industri', 'Materialer', 'Shipping', 'Telekom', 'Sjømat',
    'Konsum', 'Forbruk', 'Teknologi', 'Helse', 'Eiendom', 'Kraft'
)
BEGIN
    SELECT RAISE(ABORT, 'bransjen er ikke en av de 13');
END;

CREATE TRIGGER aksje_bransje_update
BEFORE UPDATE OF sektor ON aksje
WHEN NEW.sektor IS NULL OR NEW.sektor NOT IN (
    'Energi', 'Finans', 'Industri', 'Materialer', 'Shipping', 'Telekom', 'Sjømat',
    'Konsum', 'Forbruk', 'Teknologi', 'Helse', 'Eiendom', 'Kraft'
)
BEGIN
    SELECT RAISE(ABORT, 'bransjen er ikke en av de 13');
END;
