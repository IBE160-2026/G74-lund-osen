-- 0006 - indeks og indeksserie. Story 2.8, FR-410, AD-5, AD-16, AD-21.
--
-- Hovedindeksen er ikke en aksje (foeringen 2026-10-01 under AD-21). Den
-- lagres her, aldri i aksje, kurs, kursserie eller vurdering, og triggerne
-- fra 0003 gjelder ikke tabellen. Porten (src/indeksdata.py) avviser et
-- symbol som ikke er en kjent indeks.
--
-- indeks har feltene kurs har for en dag. Hver henting erstatter indeksens
-- rader i sin helhet (AD-5), saa tabellen kan bygges opp igjen fra kilden,
-- som kurs (AD-7). indeksserie har tidspunktet serien sist ble hentet, og
-- skrives i samme transaksjon som radene, som kursserie.
--
-- dato er YYYY-MM-DD og hentet er ISO 8601 med UTC-offset. Adapteren
-- oversetter til date og datetime ved grensen.

CREATE TABLE indeks (
    symbol        TEXT    NOT NULL,
    dato          TEXT    NOT NULL,
    slutt         REAL    NOT NULL,
    justert_slutt REAL    NOT NULL,
    volum         INTEGER NOT NULL,
    PRIMARY KEY (symbol, dato)
);

CREATE TABLE indeksserie (
    symbol TEXT PRIMARY KEY,
    hentet TEXT NOT NULL
);
