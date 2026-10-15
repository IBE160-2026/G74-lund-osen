"""Story 4.3: SQLite-adapteren for KILogg - FR-604, AD-4, AD-7, AD-16.

Porten proeves mot SqliteKILogg i tests/test_kilogg.py (fixturen
logg_lager). Her staar det som bare gjelder basen: migrasjonen 0005, at en
rad overlever en omstart, og at basen selv avviser endring og sletting.
"""

import ast
import inspect
import re
import sqlite3
import textwrap
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import lagring_sqlite
from kilogg import Emne, KIRad
from lagring_sqlite import MIGRASJONSKATALOG, SqliteKILogg, aapne_base
from migrering import migrer, versjon

OSLO = ZoneInfo("Europe/Oslo")
TORSDAG = date(2026, 10, 15)
SRC = Path(lagring_sqlite.__file__).resolve().parent


def klokke():
    return datetime(2026, 10, 15, 22, 0, tzinfo=OSLO)


def _rad(emne=None, **endret):
    felt = dict(
        emne=emne or Emne.aksje("EQNR", TORSDAG),
        grunnlag={"trend": 1, "bevegelse": 0, "interesse": -1, "styrke": 2, "retning": "Blandet"},
        regelen="Trenden og interessen ga utslag.",
        tekst="Trenden peker opp, mens interessen trekker ned.",
        besto=True, grunn=None, promptversjon="1", tjeneste="lokal", modell="gemma4:e4b",
        modell_id="dc35e8d9c606", seed=42, temperatur=0.0, maskinvare="gpu", ollama_versjon="0.35.1",
    )
    felt.update(endret)
    return KIRad(**felt)


@pytest.fixture
def base():
    tilkobling = sqlite3.connect(":memory:", isolation_level=None)
    migrer(tilkobling, MIGRASJONSKATALOG)
    yield tilkobling
    tilkobling.close()


def _rad_rett_i_basen(tilkobling, **endret):
    """En rad skrevet med SQL, utenom adapteren og KIRad."""
    verdier = dict(
        slag="aksje", dato="2026-10-15", symbol="EQNR", melding_id=None, grunnlag="{}",
        regelen="r", tekst="t", besto=1, grunn=None, promptversjon="1", tjeneste="lokal",
        modell="gemma4:e4b",
    )
    verdier.update(endret)
    kolonner = ", ".join(verdier)
    tilkobling.execute(
        f"INSERT INTO ki_logg ({kolonner}) VALUES ({', '.join('?' for _ in verdier)})",
        tuple(verdier.values()),
    )


class TestMigrasjonen:
    def test_0005_lager_ki_logg(self, base):
        """Tabellen lages av en nummerert migrasjon (AD-16)."""
        assert versjon(base) == 5
        assert base.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ki_logg'"
        ).fetchone()
        assert (MIGRASJONSKATALOG / "0005_ki_logg.sql").is_file()

    def test_tabellen_lages_bare_i_migrasjonen(self):
        """Ville feilet hvis tabellen ble opprettet utenfor
        migrasjonsloeperen. Da har to utviklere hvert sitt skjema (AD-16)."""
        for fil in SRC.glob("*.py"):
            tekst = fil.read_text(encoding="utf-8")
            assert not re.search(r"CREATE\s+TABLE[^;]*ki_logg", tekst, re.IGNORECASE), fil.name
        filer = [f.name for f in MIGRASJONSKATALOG.glob("*.sql")
                 if re.search(r"CREATE\s+TABLE\s+ki_logg", f.read_text(encoding="utf-8"))]
        assert filer == ["0005_ki_logg.sql"]

    def test_adapteren_avviser_en_base_paa_versjon_4(self, tmp_path):
        til_0004 = tmp_path / "til_0004"
        til_0004.mkdir()
        for fil in sorted(MIGRASJONSKATALOG.glob("000[1-4]_*.sql")):
            (til_0004 / fil.name).write_bytes(fil.read_bytes())
        tilkobling = sqlite3.connect(tmp_path / "v4.db", isolation_level=None)
        try:
            assert migrer(tilkobling, til_0004) == 4
            with pytest.raises(RuntimeError):
                SqliteKILogg(tilkobling, klokke)
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 5
            assert SqliteKILogg(tilkobling, klokke).les_alle() == []
        finally:
            tilkobling.close()


class TestOmstart:
    def test_en_skrevet_rad_finnes_etter_omstart(self, tmp_path):
        sti = tmp_path / "db" / "ose.db"
        tilkobling = aapne_base(sti)
        try:
            rad = _rad()
            assert SqliteKILogg(tilkobling, klokke).skriv(rad)
        finally:
            tilkobling.close()
        tilkobling = aapne_base(sti)
        try:
            assert SqliteKILogg(tilkobling, klokke).les(rad.emne) == rad
        finally:
            tilkobling.close()

    def test_alle_feltene_kommer_tilbake_like(self, base):
        logg = SqliteKILogg(base, klokke)
        rader = [
            _rad(),
            _rad(Emne.melding("m-1", TORSDAG), grunnlag={"a": [1, {"b": None}], "c": "Ø"}),
            _rad(Emne.dagen(TORSDAG), tekst=None, besto=False, grunn="modellen svarte ikke",
                 tjeneste="gemini", modell_id=None, seed=None, temperatur=None, maskinvare=None,
                 ollama_versjon=None),
        ]
        for rad in rader:
            assert logg.skriv(rad)
        assert logg.les_alle() == rader
        assert type(logg.les(rader[0].emne).temperatur) is float
        assert logg.les(rader[0].emne).besto is True


class TestIngenEndring:
    def test_adapteren_skriver_bare_med_insert(self):
        """Ingen vei gjennom adapteren kan slette eller endre en eldre rad."""
        tre = ast.parse(textwrap.dedent(inspect.getsource(SqliteKILogg)))
        tre.body[0].body = tre.body[0].body[1:]  # uten docstringen
        kode = ast.unparse(tre)
        kilde = kode + lagring_sqlite._KI_SKRIV + lagring_sqlite._KI_LES
        for ord_ in ("UPDATE", "REPLACE", "DELETE", "OR IGNORE"):
            assert ord_ not in kilde.upper(), ord_

    @pytest.mark.parametrize("sql", [
        "UPDATE ki_logg SET tekst = 'endret'",
        "DELETE FROM ki_logg",
        "INSERT OR REPLACE INTO ki_logg (slag, dato, symbol, grunnlag, regelen, tekst, besto, "
        "promptversjon, tjeneste, modell) VALUES ('aksje', '2026-10-15', 'EQNR', '{}', 'r', "
        "'ny', 1, '1', 'lokal', 'm')",
    ])
    def test_basen_avviser_endring_og_sletting(self, base, sql):
        """Triggerne i 0005: ogsaa en annen vei inn i basen kan ikke endre en
        rad (AD-7). REPLACE sletter foerst, og stoppes av triggeren for DELETE
        naar recursive_triggers er paa, ellers av den unike indeksen."""
        SqliteKILogg(base, klokke).skriv(_rad())
        foer = base.execute("SELECT * FROM ki_logg").fetchall()
        base.execute("PRAGMA recursive_triggers = ON")
        with pytest.raises(sqlite3.DatabaseError):
            base.execute(sql)
        assert base.execute("SELECT * FROM ki_logg").fetchall() == foer

    def test_en_rad_per_emne_ogsaa_uten_symbol(self, base):
        """SQLite regner to NULL som ulike i UNIQUE, saa indeksen bruker ifnull."""
        _rad_rett_i_basen(base, slag="dag", symbol=None)
        with pytest.raises(sqlite3.IntegrityError):
            _rad_rett_i_basen(base, slag="dag", symbol=None)

    @pytest.mark.parametrize("endret", [
        dict(slag="aksje", symbol="EQNR", melding_id="m-1"),
        dict(slag="aksje", symbol=None),
        dict(slag="melding", symbol="EQNR", melding_id="m-1"),
        dict(slag="dag", symbol="EQNR"),
        dict(slag="aksjer"),
        dict(besto=1, tekst=None),
        dict(besto=0, grunn=None),
        dict(besto=2),
        dict(promptversjon=""),
        dict(modell=""),
        dict(maskinvare="tpu"),
    ])
    def test_basen_sjekker_formen(self, base, endret):
        with pytest.raises(sqlite3.IntegrityError):
            _rad_rett_i_basen(base, **endret)

    def test_en_check_som_feiler_svelges_ikke(self, base):
        """ON CONFLICT DO NOTHING gjelder bare den unike indeksen. INSERT OR
        IGNORE ville ogsaa svelget en CHECK som feiler."""
        verdier = ("aksje", "2026-10-15", "EQNR", "m-1", "{}", "r", "t", 1, None, "1", "lokal",
                   "gemma4:e4b", None, None, None, None, None)
        with pytest.raises(sqlite3.IntegrityError):
            base.execute(lagring_sqlite._KI_SKRIV, verdier)
