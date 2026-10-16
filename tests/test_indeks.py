"""Story 2.8, PR 1: tabellen indeks, porten og demoindeksen - FR-410, AD-5,
AD-16, AD-21 med foeringen 2026-10-01.

Hovedindeksen er ikke en aksje. Den lagres i indeks, aldri i aksje, kurs,
kursserie eller vurdering, og staar ikke i AKSJEUNIVERS. Kallet i hentingen
kommer i PR 2.
"""

import re
import shutil
import sqlite3
from pathlib import Path

import pytest

import lagring_sqlite
from lagring_sqlite import MIGRASJONSKATALOG
from migrering import migrer, siste_versjon, versjon

SRC = Path(lagring_sqlite.__file__).resolve().parent
TABELLENE_FOER_0006 = {"aksje", "grunn", "ki_logg", "kurs", "kursserie", "skjema_versjon", "vurdering"}


def tabeller(tilkobling) -> set[str]:
    return {r[0] for r in tilkobling.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def triggere_paa(tilkobling, tabell: str) -> list[str]:
    return [r[0] for r in tilkobling.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = ?", (tabell,))]


def katalog_til(tmp_path: Path, siste: int) -> Path:
    katalog = tmp_path / f"til_{siste:04d}"
    katalog.mkdir()
    for fil in sorted(MIGRASJONSKATALOG.glob("*.sql")):
        if int(fil.name[:4]) <= siste:
            shutil.copyfile(fil, katalog / fil.name)
    return katalog


class TestMigrasjonen:
    def test_0006_fra_tom_base(self):
        """Ville feilet hvis 0006 manglet, eller ikke la til begge tabellene."""
        tilkobling = sqlite3.connect(":memory:")
        try:
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 6 == siste_versjon(MIGRASJONSKATALOG)
            assert tabeller(tilkobling) == TABELLENE_FOER_0006 | {"indeks", "indeksserie"}
            assert [k[1] for k in tilkobling.execute("PRAGMA table_info(indeks)")] == [
                "symbol", "dato", "slutt", "justert_slutt", "volum"]
            assert [k[1] for k in tilkobling.execute("PRAGMA table_info(indeksserie)")] == ["symbol", "hentet"]
        finally:
            tilkobling.close()

    def test_0006_fra_versjon_5_rorer_ikke_det_som_finnes(self, tmp_path):
        """En base paa versjon 5 med rader i kurs faar indeks, og ingenting
        annet endres. Ville feilet hvis 0006 bygde om en tabell, eller la en
        trigger paa aksje, kurs, kursserie eller vurdering."""
        tilkobling = sqlite3.connect(tmp_path / "v5.db", isolation_level=None)
        try:
            assert migrer(tilkobling, katalog_til(tmp_path, 5)) == 5
            tilkobling.execute("INSERT INTO kurs VALUES ('EQNR', '2026-10-16', 1.0, 1.0, 10)")
            foer_skjema = {r for r in tilkobling.execute("SELECT type, name, sql FROM sqlite_master")}
            foer_kurs = tilkobling.execute("SELECT * FROM kurs").fetchall()
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 6
            assert versjon(tilkobling) == 6
            etter_skjema = {r for r in tilkobling.execute("SELECT type, name, sql FROM sqlite_master")}
            assert {r[1] for r in etter_skjema - foer_skjema} == {"indeks", "indeksserie", "sqlite_autoindex_indeks_1",
                                                                  "sqlite_autoindex_indeksserie_1"}
            assert foer_skjema <= etter_skjema
            assert tilkobling.execute("SELECT * FROM kurs").fetchall() == foer_kurs
        finally:
            tilkobling.close()

    def test_ingen_trigger_paa_indeks(self):
        """AD-21: triggerne mot aksje gjelder ikke indeksen. Ville feilet hvis
        indeks fikk en kobling til aksje."""
        tilkobling = sqlite3.connect(":memory:")
        try:
            migrer(tilkobling, MIGRASJONSKATALOG)
            assert triggere_paa(tilkobling, "indeks") == []
            assert triggere_paa(tilkobling, "indeksserie") == []
        finally:
            tilkobling.close()

    def test_tabellene_lages_bare_i_0006(self):
        """AD-16: ingen CREATE TABLE for indeks utenfor migrasjonen."""
        lager = re.compile(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?[\"`]?indeks(serie)?\b", re.IGNORECASE)
        for fil in SRC.rglob("*.py"):
            assert not lager.search(fil.read_text(encoding="utf-8")), fil.name
        filer = [f.name for f in MIGRASJONSKATALOG.glob("*.sql") if lager.search(f.read_text(encoding="utf-8"))]
        assert filer == ["0006_indeks.sql"]
