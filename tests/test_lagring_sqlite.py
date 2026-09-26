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

import lagring_sqlite
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


class TestFeilISisteSteg:
    """Story 1.5b, d: tilbakerullingen naar skrivingen til kursserie feiler.

    Koden var riktig foer 1.5b, men ingen test holdt den riktig. erstatt_serie
    gjoer INSERT for et nytt symbol og ON CONFLICT DO UPDATE for et kjent, saa
    det er to veier, og hver test stopper sin: INSERT for nytt symbol og
    UPDATE for kjent. En BEFORE INSERT-trigger slaar til ogsaa ved upsert, foer
    konflikten er sjekket, saa testen for kjent symbol har bare UPDATE-triggeren.

    Ville feilet hvis COMMIT laa foer skrivingen til kursserie: da faar et nytt
    symbol en serie uten tid, og et kjent symbol ny serie med gammel tid.
    """

    @staticmethod
    def stopp_kursserie(tilkobling, hendelser=("INSERT", "UPDATE")):
        for hendelse in hendelser:
            tilkobling.execute(
                f"CREATE TRIGGER stopp_{hendelse.lower()} BEFORE {hendelse} "
                "ON kursserie BEGIN SELECT RAISE(ABORT, 'stoppet av testen'); END"
            )
        tilkobling.commit()

    def test_nytt_symbol_faar_verken_serie_eller_tid(self, tilkobling):
        lager = SqliteKurslager(tilkobling)
        self.stopp_kursserie(tilkobling, ("INSERT",))

        with pytest.raises(ValueError, match="stoppet av testen"):
            lager.erstatt_serie("EQNR", [rad("2026-09-21")], HENTET)

        assert lager.serie("EQNR") == []
        assert lager.sist_hentet("EQNR") is None
        assert not tilkobling.in_transaction

    def test_kjent_symbol_beholder_gammel_serie_og_tid(self, tilkobling):
        lager = SqliteKurslager(tilkobling)
        lager.erstatt_serie("EQNR", [rad("2026-09-18")], HENTET)
        self.stopp_kursserie(tilkobling, ("UPDATE",))

        with pytest.raises(ValueError, match="stoppet av testen"):
            lager.erstatt_serie(
                "EQNR", [rad("2026-09-21"), rad("2026-09-22")],
                HENTET + timedelta(days=1),
            )

        assert [r.dato for r in lager.serie("EQNR")] == [date(2026, 9, 18)]
        assert lager.sist_hentet("EQNR") == HENTET
        assert not tilkobling.in_transaction


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
            # Story 1.5b, h: versjonen alene ville ikke sett en tabell som
            # adapteren laget uten aa migrere.
            assert versjon(tilkobling) == 0
            assert tilkobling.execute(
                "SELECT count(*) FROM sqlite_master"
            ).fetchone()[0] == 0
        finally:
            tilkobling.close()

    def test_base_paa_eldre_versjon_enn_katalogen_avvises(
        self, tilkobling, tmp_path, monkeypatch
    ):
        """Story 1.5b, c: med 0002 i katalogen er en base paa versjon 1 ikke
        klar. Adapteren sjekket foer bare at basen var migrert en gang."""
        katalog = tmp_path / "migrasjoner"
        katalog.mkdir()
        for fil in MIGRASJONSKATALOG.glob("*.sql"):
            (katalog / fil.name).write_bytes(fil.read_bytes())
        (katalog / "0002_ny.sql").write_text(
            "CREATE TABLE ny (x INTEGER);", encoding="utf-8"
        )
        monkeypatch.setattr(lagring_sqlite, "MIGRASJONSKATALOG", katalog)

        with pytest.raises(RuntimeError, match=r"versjon 1, og .* har 2 migrasjoner"):
            SqliteKurslager(tilkobling)

        # Adapteren migrerer ikke selv, og lager ingen tabeller.
        assert versjon(tilkobling) == 1
        assert tilkobling.execute(
            "SELECT count(*) FROM sqlite_master WHERE name = 'ny'"
        ).fetchone()[0] == 0

    def test_base_paa_nyere_versjon_enn_katalogen_avvises(self, tmp_path, monkeypatch):
        """Story 1.5b, c: en base migrert av en nyere utgave av koden har et
        skjema denne koden ikke kjenner."""
        ny = tmp_path / "ny"
        ny.mkdir()
        for fil in MIGRASJONSKATALOG.glob("*.sql"):
            (ny / fil.name).write_bytes(fil.read_bytes())
        (ny / "0002_ny.sql").write_text("CREATE TABLE ny (x INTEGER);", encoding="utf-8")
        tilkobling = sqlite3.connect(tmp_path / "nyere.db")
        try:
            assert migrer(tilkobling, ny) == 2

            with pytest.raises(RuntimeError, match=r"nyere enn koden.*versjon 2, og .* har bare 1"):
                SqliteKurslager(tilkobling)
        finally:
            tilkobling.close()

    def test_katalog_som_ikke_er_i_orden_gir_runtimeerror(
        self, tilkobling, tmp_path, monkeypatch
    ):
        """Adapteren sier fra paa samme maate som ellers naar basen ikke er
        klar, i stedet for aa slippe MigrasjonsFeil ut av konstruktoeren."""
        tom = tmp_path / "tom"
        tom.mkdir()
        monkeypatch.setattr(lagring_sqlite, "MIGRASJONSKATALOG", tom)

        with pytest.raises(RuntimeError, match="ikke i orden.*Ingen migrasjoner"):
            SqliteKurslager(tilkobling)

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
