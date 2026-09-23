-- 0001 - kurs og kursserie. Story 1.3, FR-406, AD-5.
--
-- kurs er beregningsgrunnlaget. Hver henting erstatter symbolets rader i sin
-- helhet (AD-5), saa tabellen er gjenoppbyggbar fra raadatafilene (AD-6).
--
-- kursserie har en rad per symbol med tidspunktet serien sist ble hentet.
-- Tidsstempelet hoerer til serien, ikke til radene, og skrives i samme
-- transaksjon som radene byttes ut.
--
-- dato er YYYY-MM-DD og hentet er ISO 8601 med UTC-offset. Adapteren
-- oversetter til date og datetime ved grensen.

CREATE TABLE kurs (
    symbol        TEXT    NOT NULL,
    dato          TEXT    NOT NULL,
    slutt         REAL    NOT NULL,
    justert_slutt REAL    NOT NULL,
    volum         INTEGER NOT NULL,
    PRIMARY KEY (symbol, dato)
);

CREATE TABLE kursserie (
    symbol TEXT PRIMARY KEY,
    hentet TEXT NOT NULL
);
