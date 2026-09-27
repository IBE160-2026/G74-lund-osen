"""Aksjene i basen - story 1.9, AD-18, AD-21, G10 i kodegjennomgang-epic-1.md.

0003 lager tabellen aksje med de femten, og kurs, kursserie og vurdering
peker paa den med triggere. Testene som sier at basen avviser noe, bruker en
ny tilkobling som ikke har slaatt paa noe, og raa SQL. Det er det «avvises av
basen» betyr: porten er ikke eneste vakt.

Hver test lager sin egen base, i minnet eller under tmp_path. Ingen nett (AD-8).
"""

import dataclasses
import sqlite3

import pytest

from kursdata import AKSJEUNIVERS
from lagring_sqlite import MIGRASJONSKATALOG
from migrering import MigrasjonsFeil, migrer, siste_versjon, versjon


@pytest.fixture
def basefil(tmp_path):
    sti = tmp_path / "ose.db"
    tilkobling = sqlite3.connect(sti)
    migrer(tilkobling, MIGRASJONSKATALOG)
    tilkobling.close()
    return sti


@pytest.fixture
def ny(basefil):
    """En ny tilkobling til en migrert base, uten PRAGMA eller noe annet slaatt paa."""
    tilkobling = sqlite3.connect(basefil)
    yield tilkobling
    tilkobling.close()


class TestTabellen:
    def test_tom_base_migreres_til_versjon_3(self):
        tilkobling = sqlite3.connect(":memory:")
        try:
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 3
            assert siste_versjon(MIGRASJONSKATALOG) == 3
        finally:
            tilkobling.close()

    def test_aksje_er_lik_aksjeuniverset_felt_for_felt_og_i_samme_rekkefoelge(self, ny):
        """SQLite lover ingen rekkefoelge uten ORDER BY, saa rowid gir den."""
        felt = [f.name for f in dataclasses.fields(AKSJEUNIVERS[0])]
        assert felt == ["symbol", "ticker", "navn", "sektor"]
        i_basen = ny.execute(
            f"SELECT {', '.join(felt)} FROM aksje ORDER BY rowid"
        ).fetchall()
        assert i_basen == [dataclasses.astuple(aksje) for aksje in AKSJEUNIVERS]

    def test_kolonnene_er_feltene_i_aksje(self, ny):
        kolonner = [rad[1] for rad in ny.execute("PRAGMA table_info(aksje)")]
        assert kolonner == [f.name for f in dataclasses.fields(AKSJEUNIVERS[0])]


# En gyldig rad per tabell, med symbolet som parameter. Verdiene er oppdiktet.
RAD = {
    "kurs": (
        "INSERT INTO kurs (symbol, dato, slutt, justert_slutt, volum) "
        "VALUES (?, '2026-09-23', 1.0, 1.0, 1)"
    ),
    "kursserie": (
        "INSERT INTO kursserie (symbol, hentet) VALUES (?, '2026-09-23T16:00:00+00:00')"
    ),
    "vurdering": (
        "INSERT INTO vurdering (symbol, dato, grunn) VALUES (?, '2026-09-23', 'symbol_feilet')"
    ),
}
TABELLER = list(RAD)
UKJENTE = ["EQNR.OL", "eqnr", "XXX", "", " EQNR"]


def antall(tilkobling, tabell: str) -> int:
    return tilkobling.execute(f"SELECT count(*) FROM {tabell}").fetchone()[0]


class TestBasenAvviserUkjentAksje:
    """G10: basen selv avviser et symbol som ikke staar i aksje, paa en ny
    tilkobling uten noe slaatt paa. Ville feilet hvis porten var eneste vakt."""

    def test_tilkoblingen_har_ikke_slaatt_paa_fremmednoekler(self, ny):
        assert ny.execute("PRAGMA foreign_keys").fetchone()[0] == 0

    @pytest.mark.parametrize("tabell", TABELLER)
    def test_kjent_aksje_godtas(self, ny, tabell):
        ny.execute(RAD[tabell], ("EQNR",))
        ny.commit()
        assert antall(ny, tabell) == 1

    @pytest.mark.parametrize("symbol", UKJENTE)
    @pytest.mark.parametrize("tabell", TABELLER)
    def test_ukjent_aksje_avvises_ved_insert(self, ny, tabell, symbol):
        with pytest.raises(sqlite3.IntegrityError, match=f"ukjent aksje i {tabell}"):
            ny.execute(RAD[tabell], (symbol,))
        assert antall(ny, tabell) == 0

    def test_null_avvises_i_kursserie(self, ny):
        """kursserie.symbol er TEXT PRIMARY KEY uten NOT NULL. Med NOT IN i
        triggeren ville NULL sluppet gjennom."""
        with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i kursserie"):
            ny.execute(RAD["kursserie"], (None,))
        assert antall(ny, "kursserie") == 0

    @pytest.mark.parametrize("tabell", TABELLER)
    def test_symbol_kan_ikke_endres_til_ukjent_aksje(self, ny, tabell):
        ny.execute(RAD[tabell], ("EQNR",))
        ny.commit()
        with pytest.raises(sqlite3.IntegrityError, match=f"ukjent aksje i {tabell}"):
            ny.execute(f"UPDATE {tabell} SET symbol = 'EQNR.OL'")
        assert ny.execute(f"SELECT symbol FROM {tabell}").fetchall() == [("EQNR",)]

    @pytest.mark.parametrize("tabell", TABELLER)
    def test_symbol_kan_endres_til_en_annen_kjent_aksje(self, ny, tabell):
        """Triggeren sjekker det nye symbolet, ikke at det staar stille."""
        ny.execute(RAD[tabell], ("EQNR",))
        ny.execute(f"UPDATE {tabell} SET symbol = 'DNB'")
        assert ny.execute(f"SELECT symbol FROM {tabell}").fetchall() == [("DNB",)]


class TestAksjenStaarFast:
    """En aksje med rader kan ikke slettes, og symbolet kan aldri endres."""

    @pytest.mark.parametrize("tabell", TABELLER)
    def test_aksje_med_rad_i_bare_en_tabell_kan_ikke_slettes(self, ny, tabell):
        ny.execute(RAD[tabell], ("EQNR",))
        ny.commit()
        with pytest.raises(sqlite3.IntegrityError, match="en aksje med rader slettes ikke"):
            ny.execute("DELETE FROM aksje WHERE symbol = 'EQNR'")
        assert antall(ny, "aksje") == 15

    def test_aksje_uten_rader_kan_slettes(self, ny):
        """aksje er oppsett, ikke et uerstattelig lager (godkjent 27.09)."""
        ny.execute(RAD["kurs"], ("EQNR",))
        ny.execute("DELETE FROM aksje WHERE symbol = 'DNB'")
        assert antall(ny, "aksje") == 14
        with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i kurs"):
            ny.execute(RAD["kurs"], ("DNB",))

    def test_symbol_kan_ikke_endres_uten_rader(self, ny):
        with pytest.raises(sqlite3.IntegrityError, match="symbolet til en aksje endres ikke"):
            ny.execute("UPDATE aksje SET symbol = 'EQNR.OL' WHERE symbol = 'EQNR'")
        assert ny.execute(
            "SELECT count(*) FROM aksje WHERE symbol = 'EQNR'"
        ).fetchone()[0] == 1

    def test_symbol_kan_ikke_endres_med_rader(self, ny):
        ny.execute(RAD["vurdering"], ("EQNR",))
        ny.commit()
        with pytest.raises(sqlite3.IntegrityError, match="symbolet til en aksje endres ikke"):
            ny.execute("UPDATE aksje SET symbol = 'EQUINOR' WHERE symbol = 'EQNR'")
        assert ny.execute(
            "SELECT a.navn FROM vurdering v JOIN aksje a USING (symbol)"
        ).fetchall() == [("Equinor",)]

    def test_navn_og_sektor_kan_endres(self, ny):
        ny.execute(RAD["kurs"], ("EQNR",))
        ny.execute("UPDATE aksje SET navn = 'Nytt navn', sektor = 'Ny' WHERE symbol = 'EQNR'")
        assert ny.execute(
            "SELECT navn, sektor FROM aksje WHERE symbol = 'EQNR'"
        ).fetchone() == ("Nytt navn", "Ny")

    @pytest.mark.parametrize("sql", [
        "INSERT OR REPLACE INTO aksje VALUES ('NY', 'EQNR.OL', 'Ny', 'Energi')",
        "INSERT OR REPLACE INTO aksje VALUES ('EQNR', 'NY.OL', 'Ny', 'Energi')",
        "REPLACE INTO aksje VALUES ('NY', 'EQNR.OL', 'Ny', 'Energi')",
        "INSERT INTO aksje VALUES ('NY', 'EQNR.OL', 'Ny', 'Energi') "
        "ON CONFLICT DO NOTHING",
        "UPDATE OR REPLACE aksje SET ticker = 'EQNR.OL' WHERE symbol = 'DNB'",
    ])
    def test_aksje_med_rader_erstattes_ikke(self, ny, sql):
        """REPLACE sletter raden som er i veien uten DELETE-triggeren."""
        ny.execute(RAD["kurs"], ("EQNR",))
        ny.commit()
        with pytest.raises(sqlite3.IntegrityError, match="en aksje erstattes ikke"):
            ny.execute(sql)
        assert ny.execute(
            "SELECT symbol, ticker FROM aksje WHERE symbol = 'EQNR'"
        ).fetchall() == [("EQNR", "EQNR.OL")]
        assert antall(ny, "aksje") == 15

    def test_ny_aksje_kan_legges_til(self, ny):
        ny.execute("INSERT INTO aksje VALUES ('NY', 'NY.OL', 'Ny', 'Energi')")
        ny.execute(RAD["kurs"], ("NY",))
        assert antall(ny, "aksje") == 16


def base_paa_versjon_2(tmp_path) -> sqlite3.Connection:
    """En base migrert med bare 0001 og 0002, slik en base fra foer 1.9 ser ut."""
    katalog = tmp_path / "til_0002"
    katalog.mkdir()
    for navn in ("0001_kurs.sql", "0002_vurdering.sql"):
        (katalog / navn).write_bytes((MIGRASJONSKATALOG / navn).read_bytes())
    tilkobling = sqlite3.connect(tmp_path / "v2.db")
    assert migrer(tilkobling, katalog) == 2
    return tilkobling


def alle_rader(tilkobling) -> dict[str, list[tuple]]:
    return {
        tabell: tilkobling.execute(f"SELECT * FROM {tabell} ORDER BY 1, 2").fetchall()
        for tabell in TABELLER
    }


class TestBaseIVersjon2:
    """0003 paa en base som alt har rader."""

    def test_rader_for_kjente_aksjer_blir_staaende(self, tmp_path):
        tilkobling = base_paa_versjon_2(tmp_path)
        try:
            for tabell in TABELLER:
                for symbol in ("EQNR", "MPCC"):
                    tilkobling.execute(RAD[tabell], (symbol,))
            tilkobling.commit()
            foer = alle_rader(tilkobling)

            assert migrer(tilkobling, MIGRASJONSKATALOG) == 3
            assert alle_rader(tilkobling) == foer
            assert antall(tilkobling, "aksje") == 15
            assert tilkobling.execute(
                "SELECT count(*) FROM sqlite_master WHERE name = 'kontroll_0003'"
            ).fetchone()[0] == 0
        finally:
            tilkobling.close()

    @pytest.mark.parametrize("tabell", TABELLER)
    def test_rad_for_ukjent_aksje_stopper_migrasjonen(self, tmp_path, tabell):
        """Godkjent 27.09: 0003 stopper og rulles tilbake, og basen staar paa
        versjon 2. Radene er uroert, og aksje finnes ikke."""
        tilkobling = base_paa_versjon_2(tmp_path)
        try:
            for t in TABELLER:
                tilkobling.execute(RAD[t], ("EQNR",))
            tilkobling.execute(RAD[tabell].replace("2026-09-23", "2026-09-24"), ("EQNR.OL",))
            tilkobling.commit()
            foer = alle_rader(tilkobling)

            with pytest.raises(MigrasjonsFeil, match="0003_aksje.sql.*rader_uten_aksje"):
                migrer(tilkobling, MIGRASJONSKATALOG)

            assert versjon(tilkobling) == 2
            assert alle_rader(tilkobling) == foer
            assert tilkobling.execute(
                "SELECT count(*) FROM sqlite_master WHERE name IN ('aksje', 'kontroll_0003')"
            ).fetchone()[0] == 0
        finally:
            tilkobling.close()
