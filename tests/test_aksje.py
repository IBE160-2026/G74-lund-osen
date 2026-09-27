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
from migrering import migrer, siste_versjon


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
