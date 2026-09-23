"""Tester som bare gjelder SQLite-adapteren - story 1.3.

Kontrakten porten lover, proeves i test_kurslager.py mot baade minnelageret og
denne adapteren. Her staar det kontrakten ikke kan se: at dataene overlever en
ny tilkobling, hvordan de ligger lagret, og hvordan adapteren oppfoerer seg mot
en base som ikke er klar.

Hver test bruker sin egen basefil under tmp_path. Ingen test roerer data/.
"""

import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

from kursdata import Kursrad
from lagring_sqlite import MIGRASJONSKATALOG, SqliteKurslager
from migrering import migrer, versjon

HENTET = datetime(2026, 9, 22, 8, 33, tzinfo=timezone.utc)


def rad(dato: str, slutt: float = 100.0) -> Kursrad:
    return Kursrad(dato=date.fromisoformat(dato), slutt=slutt,
                   justert_slutt=slutt - 1, volum=1000)


@pytest.fixture
def basefil(tmp_path):
    sti = tmp_path / "ose.db"
    tilkobling = sqlite3.connect(sti)
    migrer(tilkobling, MIGRASJONSKATALOG)
    tilkobling.close()
    return sti


@pytest.fixture
def tilkobling(basefil):
    tilkobling = sqlite3.connect(basefil)
    yield tilkobling
    tilkobling.close()


class TestMigrasjonen:
    def test_0001_finnes_i_src_migrasjoner(self):
        assert MIGRASJONSKATALOG.name == "migrasjoner"
        assert MIGRASJONSKATALOG.parent.name == "src"
        assert (MIGRASJONSKATALOG / "0001_kurs.sql").is_file()

    def test_tom_base_migreres_til_versjon_1_med_to_tabeller(self, tmp_path):
        tilkobling = sqlite3.connect(tmp_path / "ny.db")
        try:
            assert migrer(tilkobling, MIGRASJONSKATALOG) >= 1
            tabeller = {
                navn for (navn,) in tilkobling.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            assert {"kurs", "kursserie"} <= tabeller
        finally:
            tilkobling.close()


class TestOverleverOmstart:
    """Storyen: kursene finnes etter at maskinen har vaert av."""

    def test_serie_og_tid_finnes_etter_ny_tilkobling(self, basefil):
        foerste = sqlite3.connect(basefil)
        SqliteKurslager(foerste).erstatt_serie(
            "EQNR", [rad("2026-09-18"), rad("2026-09-21")], HENTET
        )
        foerste.close()

        andre = sqlite3.connect(basefil)
        try:
            lager = SqliteKurslager(andre)
            assert [r.dato for r in lager.serie("EQNR")] == [
                date(2026, 9, 18), date(2026, 9, 21),
            ]
            assert lager.sist_hentet("EQNR") == HENTET
        finally:
            andre.close()


class TestOversettelsenVedGrensen:
    """Inne i systemet er dato en date og hentet en datetime i UTC. I basen
    er begge tekst. Adapteren oversetter begge veier; ingen tekst slipper ut."""

    def test_dato_lagres_som_aaaa_mm_dd(self, tilkobling):
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", [rad("2026-09-21")], HENTET)

        (lagret,) = tilkobling.execute("SELECT dato FROM kurs").fetchone()

        assert lagret == "2026-09-21"

    def test_hentet_lagres_som_iso_8601_med_utc_offset(self, tilkobling):
        oslo = HENTET.astimezone(timezone(timedelta(hours=2)))
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", [rad("2026-09-21")], oslo)

        (lagret,) = tilkobling.execute(
            "SELECT hentet FROM kursserie WHERE symbol = 'EQNR'"
        ).fetchone()

        assert lagret == "2026-09-22T08:33:00+00:00"

    def test_en_rad_per_symbol_i_kursserie(self, tilkobling):
        lager = SqliteKurslager(tilkobling)
        lager.erstatt_serie("EQNR", [rad("2026-09-18")], HENTET)
        lager.erstatt_serie("EQNR", [rad("2026-09-21")], HENTET + timedelta(days=1))

        (antall,) = tilkobling.execute(
            "SELECT count(*) FROM kursserie WHERE symbol = 'EQNR'"
        ).fetchone()

        assert antall == 1


class TestBaseSomIkkeErKlar:
    def test_umigrert_base_avvises_og_faar_ingen_tabeller(self, tmp_path):
        """Adapteren kjoerer ikke migrasjoner selv - hvem som gjoer det,
        avgjoeres i story 3.1. Den sier fra i stedet for aa feile paa
        'no such table' ved foerste oppslag."""
        tilkobling = sqlite3.connect(tmp_path / "umigrert.db")
        try:
            with pytest.raises(RuntimeError, match="migrert"):
                SqliteKurslager(tilkobling)
            assert versjon(tilkobling) == 0
        finally:
            tilkobling.close()

    def test_aapen_transaksjon_hos_kalleren_avvises(self, tilkobling):
        """Samme regel som migrasjonsloeperen: adapteren eier transaksjonen, og
        en COMMIT herfra ville tatt med seg kallerens endringer."""
        lager = SqliteKurslager(tilkobling)
        tilkobling.execute("CREATE TABLE kallerens (x INTEGER)")
        tilkobling.execute("INSERT INTO kallerens VALUES (1)")

        with pytest.raises(RuntimeError, match="transaksjon"):
            lager.erstatt_serie("EQNR", [rad("2026-09-21")], HENTET)

        assert tilkobling.in_transaction
        tilkobling.rollback()
        assert lager.serie("EQNR") == []
