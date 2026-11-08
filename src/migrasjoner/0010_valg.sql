-- 0010 - valg. Story 2.12, FR-412, AD-3, AD-10, AD-16.
--
-- boersliste er lista over aksjene paa Oslo Boers (typen «Common Stock»),
-- lest fra fila fra malinger.md §40 med fetch_prices.py --les-boerslista,
-- uten kall (spoersmaal 2 i spec-2-12-velge-og-bytte-aksjer.md). Siden viser
-- bare koder som staar her, saa en ticker som ikke finnes, aldri koster et
-- kall (avgjoerelsen 22.10 kl. 23:14).
--
-- oenske er det eneste webserveren skriver i 2.12 (AD-3): aa foelge eller
-- fjerne en aksje. Et bytte er to oensker, laget samtidig. Kveldens henting
-- tar oenskene i bruk foer den leser lista (tatt_i_bruk), og er fortsatt
-- eneste skriver av aksje, kurser og vurderinger. Et oenske som ikke er tatt
-- i bruk, kan angres, og da slettes raden. Et oenske hentingen ikke kunne
-- bruke, faar avvist med grunnen. Ingen tabell eller trigger som finnes,
-- endres.

CREATE TABLE boersliste (
    kode TEXT PRIMARY KEY NOT NULL CHECK (kode <> '' AND kode NOT GLOB '*[^A-Z0-9-]*'),
    navn TEXT NOT NULL CHECK (navn <> '')
);

CREATE TABLE oenske (
    id INTEGER PRIMARY KEY,
    handling TEXT NOT NULL CHECK (handling IN ('folg', 'fjern')),
    symbol TEXT NOT NULL CHECK (symbol <> ''),
    navn TEXT,
    sektor TEXT CHECK (sektor IS NULL OR sektor IN (
        'Energi', 'Finans', 'Industri', 'Materialer', 'Shipping', 'Telekom', 'Sjømat',
        'Konsum', 'Forbruk', 'Teknologi', 'Helse', 'Eiendom', 'Kraft'
    )),
    laget TEXT NOT NULL,
    tatt_i_bruk TEXT,
    avvist TEXT,
    CHECK ((handling = 'folg') = (navn IS NOT NULL AND sektor IS NOT NULL)),
    CHECK (tatt_i_bruk IS NULL OR avvist IS NULL)
);
