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
