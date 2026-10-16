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


# --- Porten (punkt b) ---------------------------------------------------------

from datetime import date, datetime, timedelta, timezone  # noqa: E402

from boersdag import er_boersdag  # noqa: E402
from indeksdata import (  # noqa: E402
    HOVEDINDEKS, Indekslager, Indeksleser, MinneIndekslager, bare_boersdager)
from kursdata import AKSJEUNIVERS, Kursrad  # noqa: E402
from lagring_sqlite import SqliteIndekslager, SqliteKurslager, aapne_base  # noqa: E402

HENTET = datetime(2026, 10, 16, 20, 10, tzinfo=timezone.utc)
FREDAG = date(2026, 10, 16)
LOERDAG = date(2026, 10, 17)
JULEDAG = date(2026, 12, 25)
I_FJOR = date(2025, 12, 30)
# malinger.md §14: datoene indeksen har og aksjene ikke har.
PARAGRAF_14 = [date(2025, 12, 24), date(2025, 12, 31), date(2026, 4, 2), date(2026, 5, 14), date(2026, 5, 25)]


def rad(dag: date, slutt: float = 1500.0) -> Kursrad:
    return Kursrad(dato=dag, slutt=slutt, justert_slutt=slutt, volum=1000)


def boersdager_fram_til(siste: date, antall: int) -> list[date]:
    dager, dag = [], siste
    while len(dager) < antall:
        if er_boersdag(dag):
            dager.append(dag)
        dag -= timedelta(days=1)
    return sorted(dager)


@pytest.fixture
def sqlite_base(tmp_path):
    tilkobling = aapne_base(tmp_path / "test.db")
    yield tilkobling
    tilkobling.close()


@pytest.fixture(params=["minne", "sqlite"])
def lager(request, tmp_path):
    if request.param == "minne":
        yield MinneIndekslager()
    else:
        tilkobling = aapne_base(tmp_path / "lager.db")
        yield SqliteIndekslager(tilkobling)
        tilkobling.close()


class TestPorten:
    def test_lagrene_oppfyller_porten(self, lager):
        assert isinstance(lager, Indekslager) and isinstance(lager, Indeksleser)

    def test_serien_byttes_ut_ikke_skjoetes_paa(self, lager):
        """AD-5. Ville feilet hvis serien ble skjøtt på: da sto de tre gamle
        dagene igjen ved siden av de to nye."""
        gamle = boersdager_fram_til(date(2026, 10, 9), 3)
        nye = boersdager_fram_til(FREDAG, 2)
        lager.erstatt_serie("OSEBX", [rad(d) for d in gamle], HENTET)
        senere = HENTET + timedelta(days=1)
        lager.erstatt_serie("OSEBX", [rad(d, 1600.0) for d in nye], senere)
        assert [r.dato for r in lager.serie("OSEBX")] == nye
        assert {r.slutt for r in lager.serie("OSEBX")} == {1600.0}
        assert lager.sist_hentet("OSEBX") == senere

    def test_en_loerdag_og_en_helligdag_lagres_ikke(self, lager):
        """Bare børsdager i DEKKEDE_AAR. Ville feilet hvis lørdagen eller
        juledagen ble lagret."""
        assert not er_boersdag(LOERDAG) and not er_boersdag(JULEDAG)
        lager.erstatt_serie("OSEBX", [rad(FREDAG), rad(LOERDAG), rad(JULEDAG)], HENTET)
        assert [r.dato for r in lager.serie("OSEBX")] == [FREDAG]

    def test_en_dag_i_et_aar_utenfor_kalenderen_hoppes_over_uten_feil(self, lager):
        """Serien fra EODHD går ett år bakover. Ville feilet hvis dagen i 2025
        ga UtenforKalenderen, eller ble lagret."""
        lager.erstatt_serie("OSEBX", [rad(I_FJOR), rad(FREDAG)], HENTET)
        assert [r.dato for r in lager.serie("OSEBX")] == [FREDAG]

    def test_dagene_i_paragraf_14_faller_bort(self, lager):
        """De fem datoene i §14 som aksjene ikke har."""
        lager.erstatt_serie("OSEBX", [rad(d) for d in PARAGRAF_14] + [rad(FREDAG)], HENTET)
        assert [r.dato for r in lager.serie("OSEBX")] == [FREDAG]

    def test_en_serie_uten_boersdager_avvises_og_endrer_ingenting(self, lager):
        lager.erstatt_serie("OSEBX", [rad(FREDAG)], HENTET)
        with pytest.raises(ValueError):
            lager.erstatt_serie("OSEBX", [rad(LOERDAG), rad(I_FJOR)], HENTET + timedelta(days=1))
        assert [r.dato for r in lager.serie("OSEBX")] == [FREDAG]
        assert lager.sist_hentet("OSEBX") == HENTET

    def test_en_aksje_avvises(self, lager):
        """Ville feilet hvis porten tok imot en aksje som indeks."""
        with pytest.raises(ValueError):
            lager.erstatt_serie("EQNR", [rad(FREDAG)], HENTET)
        assert lager.serie("EQNR") == [] and lager.sist_hentet("EQNR") is None

    def test_to_rader_samme_dag_avvises_og_endrer_ingenting(self, lager):
        lager.erstatt_serie("OSEBX", [rad(FREDAG)], HENTET)
        with pytest.raises(ValueError):
            lager.erstatt_serie("OSEBX", [rad(date(2026, 10, 15)), rad(date(2026, 10, 15))], HENTET + timedelta(days=1))
        assert [r.dato for r in lager.serie("OSEBX")] == [FREDAG]
        assert lager.sist_hentet("OSEBX") == HENTET

    def test_tid_uten_sone_avvises(self, lager):
        with pytest.raises(ValueError):
            lager.erstatt_serie("OSEBX", [rad(FREDAG)], datetime(2026, 10, 16, 22, 0))

    def test_bare_boersdager_har_ikke_noe_fast_aar(self, monkeypatch):
        """Året leses fra DEKKEDE_AAR når serien skrives. Ville feilet hvis
        koden hadde 2026 fast: med 2025 tatt bort fra kalenderens år er
        fredagen 16.10.2026 heller ikke med."""
        import boersdag
        monkeypatch.setattr(boersdag, "DEKKEDE_AAR", frozenset({2025}))
        assert bare_boersdager([rad(FREDAG)]) == []
        # Ingen årstall som tall i koden (datoer i docstringene teller ikke).
        import ast
        tre = ast.parse((SRC / "indeksdata.py").read_text(encoding="utf-8"))
        assert not [n.value for n in ast.walk(tre)
                    if isinstance(n, ast.Constant) and isinstance(n.value, int) and 1900 <= n.value <= 2100]


class TestIndeksenErIkkeEnAksje:
    def test_ikke_i_aksjeuniverset(self):
        """Ville feilet hvis indeksen ble lagt i AKSJEUNIVERS for å slippe en
        ny tabell. Da teller den som en aksje i signalet og i «x av N»."""
        assert HOVEDINDEKS.symbol not in {a.symbol for a in AKSJEUNIVERS}
        assert HOVEDINDEKS.ticker not in {a.ticker for a in AKSJEUNIVERS}

    def test_aldri_i_kurs_kursserie_aksje_eller_vurdering(self, sqlite_base):
        """Ville feilet hvis SqliteIndekslager skrev til kurs."""
        SqliteIndekslager(sqlite_base).erstatt_serie("OSEBX", [rad(FREDAG)], HENTET)
        for tabell in ("kurs", "kursserie", "vurdering"):
            assert sqlite_base.execute(f"SELECT count(*) FROM {tabell}").fetchone()[0] == 0, tabell
        assert sqlite_base.execute("SELECT count(*) FROM aksje WHERE symbol = 'OSEBX'").fetchone()[0] == 0
        assert sqlite_base.execute("SELECT symbol, dato FROM indeks").fetchall() == [("OSEBX", "2026-10-16")]

    def test_kurslageret_avviser_indeksen(self, sqlite_base):
        """Porten til kursene og triggerne fra 0003 stopper OSEBX i kurs."""
        with pytest.raises(ValueError):
            SqliteKurslager(sqlite_base).erstatt_serie("OSEBX", [rad(FREDAG)], HENTET)
        with pytest.raises(sqlite3.IntegrityError):
            sqlite_base.execute("INSERT INTO kurs VALUES ('OSEBX', '2026-10-16', 1.0, 1.0, 1)")

    def test_adapteren_avviser_en_base_paa_versjon_5(self, tmp_path):
        tilkobling = sqlite3.connect(tmp_path / "v5.db", isolation_level=None)
        try:
            migrer(tilkobling, katalog_til(tmp_path, 5))
            with pytest.raises(RuntimeError):
                SqliteIndekslager(tilkobling)
        finally:
            tilkobling.close()


# --- Demoindeksen (punkt c) ---------------------------------------------------

import demo  # noqa: E402


@pytest.fixture(scope="module")
def demobasen(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demoindeks") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    tilkobling = sqlite3.connect(f"file:{sti.as_posix()}?mode=ro", uri=True)
    yield tilkobling
    tilkobling.close()


class TestDemoindeksen:
    def test_indeksen_for_alle_demodagene(self, demobasen):
        """FR-411 og beslutningen 16.10 kl. 11:46. Ville feilet hvis demobasen
        ble laget uten indeks, eller manglet en dag."""
        dager = [r[0] for r in demobasen.execute(
            "SELECT dato FROM indeks WHERE symbol = ? ORDER BY dato", (demo.DEMOINDEKS.symbol,))]
        assert dager == [d.isoformat() for d in demo.handelsdager()]
        assert demobasen.execute("SELECT DISTINCT symbol FROM indeks").fetchall() == [(demo.DEMOINDEKS.symbol,)]
        assert demobasen.execute("SELECT count(*) FROM indeksserie").fetchone()[0] == 1

    def test_indeksen_er_ikke_en_demoaksje(self, demobasen):
        """«x av N» teller den ikke: den står ikke i aksje eller kurs."""
        symbol = demo.DEMOINDEKS.symbol
        assert symbol not in {a.symbol for a in demo.DEMOUNIVERS}
        assert symbol not in {a.symbol for a in AKSJEUNIVERS} and symbol != HOVEDINDEKS.symbol
        for tabell in ("aksje", "kurs", "kursserie", "vurdering"):
            assert demobasen.execute(f"SELECT count(*) FROM {tabell} WHERE symbol = ?", (symbol,)).fetchone()[0] == 0
        assert demobasen.execute("SELECT count(*) FROM aksje").fetchone()[0] == len(demo.DEMOUNIVERS)

    def test_indeksen_foelger_demoaksjene(self):
        """Dagens endring er snittet av endringen for aksjene som har kurs
        begge dagene."""
        dager = demo.handelsdager()
        serier = {a.symbol: demo.serie(n, a, dager) for n, a in enumerate(demo.DEMOUNIVERS)}
        indeks = demo.indeksserie(serier, dager)
        siste, forrige = dager[-1], dager[-2]
        endringer = [
            {r.dato: r for r in rader}[siste].justert_slutt / {r.dato: r for r in rader}[forrige].justert_slutt - 1
            for rader in serier.values() if {siste, forrige} <= {r.dato for r in rader}
        ]
        ventet = indeks[-2].slutt * (1 + sum(endringer) / len(endringer))
        assert indeks[-1].slutt == pytest.approx(ventet, abs=0.01)
        assert indeks[0].slutt == demo.INDEKS_START
