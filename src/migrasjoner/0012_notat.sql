-- 0012 - notat. Story 8.21, AD-3, AD-10, AD-16 (gruppens svar 10.11 kl. 14:32).
--
-- Egne notater paa aksjesiden: en rad per notat, med dagen siden viste da
-- notatet ble skrevet (dato), teksten og tidspunktet det ble lagret (laget).
-- Webserveren er eneste skriver, som for Min liste, oenske og innstilling
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

-- Tillegget 10.11 kl. 14:44: tenkte kjøp og salg ved et notat. Et kjøp
-- hører til ett notat, og en aksje har høyst ett åpent kjøp om gangen.
-- Ved trykket lagres tidspunktet, de tre sjekkene slik de sto på siden
-- (NULL når dagen ikke var vurdert), og dagen sluttkursen må være etter
-- (kjoep_etter): den siste dagen med kurs da brukeren trykket, eller
-- børsdagen før, om den er senere. Kursen lagres ikke. Sidene leser den
-- første kursen etter den dagen fra kursserien, så prosenten følger serien
-- når den hentes på nytt eller justeres (spoersmaal 15 i
-- spec-8-21-egne-notater-paa-aksjesiden.md). Webserveren er eneste skriver.

CREATE TABLE tenkt_kjoep (
    id INTEGER PRIMARY KEY,
    notat INTEGER NOT NULL UNIQUE,
    symbol TEXT NOT NULL CHECK (symbol <> ''),
    kjoept TEXT NOT NULL CHECK (julianday(kjoept) IS NOT NULL),
    kjoep_etter TEXT NOT NULL CHECK (length(kjoep_etter) = 10 AND date(kjoep_etter) IS kjoep_etter),
    kjoep_trend INTEGER CHECK (kjoep_trend IN (-1, 0, 1)),
    kjoep_bevegelse INTEGER CHECK (kjoep_bevegelse IN (-1, 0, 1)),
    kjoep_interesse INTEGER CHECK (kjoep_interesse IN (-1, 0, 1)),
    solgt TEXT CHECK (solgt IS NULL OR julianday(solgt) IS NOT NULL),
    salg_etter TEXT CHECK (salg_etter IS NULL OR (length(salg_etter) = 10 AND date(salg_etter) IS salg_etter)),
    salg_trend INTEGER CHECK (salg_trend IN (-1, 0, 1)),
    salg_bevegelse INTEGER CHECK (salg_bevegelse IN (-1, 0, 1)),
    salg_interesse INTEGER CHECK (salg_interesse IN (-1, 0, 1)),
    CHECK ((solgt IS NULL) = (salg_etter IS NULL)),
    CHECK (salg_etter IS NULL OR salg_etter >= kjoep_etter),
    CHECK ((kjoep_trend IS NULL) = (kjoep_bevegelse IS NULL) AND (kjoep_trend IS NULL) = (kjoep_interesse IS NULL)),
    CHECK ((salg_trend IS NULL) = (salg_bevegelse IS NULL) AND (salg_trend IS NULL) = (salg_interesse IS NULL)),
    CHECK (solgt IS NOT NULL OR salg_trend IS NULL)
);

CREATE UNIQUE INDEX tenkt_kjoep_ett_aapent ON tenkt_kjoep (symbol) WHERE solgt IS NULL;

-- Kjøpet hører til et notat for samme aksje.
CREATE TRIGGER tenkt_kjoep_notat_insert
BEFORE INSERT ON tenkt_kjoep
WHEN NOT EXISTS (SELECT 1 FROM notat WHERE id = NEW.notat AND symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'tenkt kjøp uten notat for aksjen');
END;

CREATE TRIGGER tenkt_kjoep_notat_update
BEFORE UPDATE OF notat, symbol ON tenkt_kjoep
WHEN NOT EXISTS (SELECT 1 FROM notat WHERE id = NEW.notat AND symbol = NEW.symbol)
BEGIN
    SELECT RAISE(ABORT, 'tenkt kjøp uten notat for aksjen');
END;

-- Spørsmål 17: slettes notatet, slettes det tenkte kjøpet med det.
CREATE TRIGGER notat_slett_tenkt_kjoep
BEFORE DELETE ON notat
BEGIN
    DELETE FROM tenkt_kjoep WHERE notat = OLD.id;
END;

-- Tillegget kl. 14:44, punkt 1: bryteren «Notater» i Innstillinger. Egen
-- tabell, fordi CHECK i innstilling (0011) bare godtar de to valgene der, og
-- en tabell som finnes, endres ikke. Ingen rad betyr på.

CREATE TABLE notatvalg (
    navn TEXT PRIMARY KEY NOT NULL CHECK (navn = 'vis_notater'),
    verdi INTEGER NOT NULL CHECK (verdi IN (0, 1))
);
