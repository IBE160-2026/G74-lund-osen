"""Story 2.10: hoey og lav lagres med kursene.

Instruksjonen 19.11 kl. 14:24 i docs/ai-prompts/2026-11-19.md, etter gruppens
svar kl. 13:51. Kontrollen i storyen i epics.md gjelder: adapteren, Kursrad
og lageret tar med high og low, en ny migrasjon legger dem til, ingen nye
kall, og en rad uten dem lagres uten dem. Ville feilet hvis en rad uten high
eller low stoppet hentingen.

Alle basene er testbaser i tmp_path (regel 22). Ingen tall her er kursdata
fra en kilde.
"""

import math
import shutil
import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

import fetch_prices as fp
from eodhd import kursrad_fra_eodhd, serie_fra_eodhd
from indeksdata import HOVEDINDEKS
from kursdata import AKSJEUNIVERS, Kursrad, MinneKurslager, UgyldigKursrad
from lagring_sqlite import MIGRASJONSKATALOG, SqliteIndekslager, SqliteKurslager, aapne_base
from migrering import migrer, siste_versjon

DAG = date(2026, 9, 21)
HENTET = datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)
TIRSDAG = date(2026, 9, 22)


def _rad(**felt) -> dict:
    rad = {"date": "2026-09-21", "close": 100.0, "adjusted_close": 98.0, "volume": 1000, "high": 101.5, "low": 97.25}
    rad.update(felt)
    return {k: v for k, v in rad.items() if v is not _UTEN}


_UTEN = object()

# Verdier for high eller low som ikke kan brukes. Hver av dem blir None.
UBRUKELIGE = [None, "NA", "101.5", 0, 0.0, -1.0, math.nan, math.inf, -math.inf, True, False, [], {}, 10**400]


class TestKursrad:
    def test_hoey_og_lav_er_valgfrie(self):
        rad = Kursrad(dato=DAG, slutt=100.0, justert_slutt=98.0, volum=1000)
        assert rad.hoey is None and rad.lav is None

    def test_hoey_og_lav_kan_settes(self):
        rad = Kursrad(dato=DAG, slutt=100.0, justert_slutt=98.0, volum=1000, hoey=101.5, lav=97.25)
        assert (rad.hoey, rad.lav) == (101.5, 97.25)

    def test_bare_en_av_dem_kan_settes(self):
        assert Kursrad(dato=DAG, slutt=1.0, justert_slutt=1.0, volum=0, hoey=2.0).lav is None
        assert Kursrad(dato=DAG, slutt=1.0, justert_slutt=1.0, volum=0, lav=0.5).hoey is None

    @pytest.mark.parametrize("navn", ["hoey", "lav"])
    @pytest.mark.parametrize("verdi", [0, -1.0, math.nan, math.inf, "101.5", True])
    def test_en_verdi_som_ikke_er_en_kurs_avvises(self, navn, verdi):
        with pytest.raises(UgyldigKursrad):
            Kursrad(dato=DAG, slutt=100.0, justert_slutt=98.0, volum=1000, **{navn: verdi})

    def test_hoey_under_lav_avvises(self):
        with pytest.raises(UgyldigKursrad):
            Kursrad(dato=DAG, slutt=100.0, justert_slutt=98.0, volum=1000, hoey=97.0, lav=101.0)

    def test_hoey_lik_lav_godtas(self):
        assert Kursrad(dato=DAG, slutt=100.0, justert_slutt=98.0, volum=0, hoey=100.0, lav=100.0).lav == 100.0


class TestAdapteren:
    def test_high_og_low_blir_hoey_og_lav(self):
        rad = kursrad_fra_eodhd(_rad())
        assert (rad.hoey, rad.lav) == (101.5, 97.25)
        assert (rad.slutt, rad.justert_slutt, rad.volum) == (100.0, 98.0, 1000)

    @pytest.mark.parametrize("felt", ["high", "low"])
    def test_en_rad_uten_feltet_leses_uten_det(self, felt):
        """Ville feilet hvis adapteren leste rad["high"] eller rad["low"]."""
        rad = kursrad_fra_eodhd(_rad(**{felt: _UTEN}))
        assert getattr(rad, "hoey" if felt == "high" else "lav") is None
        assert (rad.slutt, rad.justert_slutt, rad.volum) == (100.0, 98.0, 1000)

    def test_en_rad_uten_begge_leses_uten_dem(self):
        rad = kursrad_fra_eodhd(_rad(high=_UTEN, low=_UTEN))
        assert (rad.hoey, rad.lav) == (None, None)

    @pytest.mark.parametrize("felt", ["high", "low"])
    @pytest.mark.parametrize("verdi", UBRUKELIGE, ids=repr)
    def test_en_verdi_som_ikke_kan_brukes_blir_none(self, felt, verdi):
        rad = kursrad_fra_eodhd(_rad(**{felt: verdi}))
        assert getattr(rad, "hoey" if felt == "high" else "lav") is None
        assert getattr(rad, "lav" if felt == "high" else "hoey") is not None

    def test_high_under_low_gir_ingen_av_dem(self):
        rad = kursrad_fra_eodhd(_rad(high=97.0, low=101.0))
        assert (rad.hoey, rad.lav) == (None, None)

    def test_heltall_blir_tall(self):
        rad = kursrad_fra_eodhd(_rad(high=102, low=97))
        assert (rad.hoey, rad.lav) == (102.0, 97.0)

    def test_serien_stopper_ikke_paa_en_rad_uten_dem(self):
        serie = serie_fra_eodhd(
            [
                _rad(date="2026-09-18"),
                _rad(date="2026-09-21", high=_UTEN, low=None),
                _rad(date="2026-09-22", high="NA", low=0),
            ]
        )
        assert [(r.hoey, r.lav) for r in serie] == [(101.5, 97.25), (None, None), (None, None)]


def _base(sti):
    return aapne_base(sti)


def _rader() -> list[Kursrad]:
    return [
        Kursrad(dato=date(2026, 9, 18), slutt=100.0, justert_slutt=98.0, volum=1000, hoey=101.5, lav=97.25),
        Kursrad(dato=date(2026, 9, 21), slutt=100.0, justert_slutt=98.0, volum=1000),
        Kursrad(dato=date(2026, 9, 22), slutt=100.0, justert_slutt=98.0, volum=1000, hoey=103.0),
    ]


class TestLageret:
    def test_sqlite_kurslager_gir_tilbake_det_som_ble_skrevet(self, tmp_path):
        t = _base(tmp_path / "ose.db")
        try:
            SqliteKurslager(t).erstatt_serie("EQNR", _rader(), HENTET)
            assert SqliteKurslager(t).serie("EQNR") == _rader()
            assert t.execute("SELECT dato, hoey, lav FROM kurs ORDER BY dato").fetchall() == [
                ("2026-09-18", 101.5, 97.25),
                ("2026-09-21", None, None),
                ("2026-09-22", 103.0, None),
            ]
        finally:
            t.close()

    def test_minnelageret_gir_det_samme(self, tmp_path):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", _rader(), HENTET)
        assert lager.serie("EQNR") == _rader()

    def test_sqlite_indekslager_gir_tilbake_det_som_ble_skrevet(self, tmp_path):
        t = _base(tmp_path / "ose.db")
        try:
            SqliteIndekslager(t).erstatt_serie(HOVEDINDEKS.symbol, _rader(), HENTET)
            assert SqliteIndekslager(t).serie(HOVEDINDEKS.symbol) == _rader()
        finally:
            t.close()

    @pytest.mark.parametrize("tabell", ["kurs", "indeks"])
    @pytest.mark.parametrize(("hoey", "lav"), [(0.0, None), (None, -1.0), (97.0, 101.0)])
    def test_basen_avviser_det_kursrad_avviser(self, tmp_path, tabell, hoey, lav):
        symbol = "EQNR" if tabell == "kurs" else HOVEDINDEKS.symbol
        sql = (
            f"INSERT INTO {tabell} (symbol, dato, slutt, justert_slutt, volum, hoey, lav) "
            "VALUES (?, ?, 100.0, 98.0, 1000, ?, ?)"
        )
        t = _base(tmp_path / "ose.db")
        try:
            # Samme rad med en hoey og lav som kan brukes, godtas, saa det er
            # CHECK-en og ikke noe annet som avviser.
            t.execute(sql, (symbol, "2026-09-18", 101.5, 97.25))
            with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
                t.execute(sql, (symbol, "2026-09-21", hoey, lav))
        finally:
            t.close()


class TestMigrasjonen:
    def test_paa_en_kopi_av_en_testbase_paa_dagens_siste_versjon(self, tmp_path):
        """Ville feilet hvis 0015 endret en rad som finnes, ikke ga dem NULL,
        eller lageret ikke kunne skrive og lese etterpå."""
        assert siste_versjon(MIGRASJONSKATALOG) == 15
        katalog = tmp_path / "migrasjoner"
        katalog.mkdir()
        for fil in sorted(MIGRASJONSKATALOG.glob("*.sql")):
            if fil.name < "0015":
                shutil.copy(fil, katalog / fil.name)
        gammel = tmp_path / "gammel.db"
        t = sqlite3.connect(gammel)
        assert migrer(t, katalog) == 14
        t.execute(
            "INSERT INTO kurs (symbol, dato, slutt, justert_slutt, volum) VALUES "
            "('EQNR', '2026-09-21', 100.0, 98.0, 1000), ('EQNR', '2026-09-22', 101.0, 99.0, 1200)"
        )
        t.execute(
            "INSERT INTO indeks (symbol, dato, slutt, justert_slutt, volum) VALUES "
            f"('{HOVEDINDEKS.symbol}', '2026-09-21', 1500.0, 1500.0, 0)"
        )
        t.execute("INSERT INTO kursserie (symbol, hentet) VALUES ('EQNR', ?)", (HENTET.isoformat(),))
        t.commit()
        kurs_foer = t.execute("SELECT * FROM kurs ORDER BY symbol, dato").fetchall()
        indeks_foer = t.execute("SELECT * FROM indeks ORDER BY symbol, dato").fetchall()
        t.close()

        kopi = tmp_path / "kopi.db"
        shutil.copy(gammel, kopi)
        t = sqlite3.connect(kopi)
        try:
            assert migrer(t, MIGRASJONSKATALOG) == 15
            assert t.execute("SELECT * FROM kurs ORDER BY symbol, dato").fetchall() == [
                (*r, None, None) for r in kurs_foer
            ]
            assert t.execute("SELECT * FROM indeks ORDER BY symbol, dato").fetchall() == [
                (*r, None, None) for r in indeks_foer
            ]
            lager = SqliteKurslager(t)
            assert [(r.hoey, r.lav) for r in lager.serie("EQNR")] == [(None, None), (None, None)]
            ny = [Kursrad(dato=date(2026, 9, 22), slutt=101.0, justert_slutt=99.0, volum=1200, hoey=102.0, lav=98.5)]
            lager.erstatt_serie("EQNR", ny, HENTET + timedelta(days=1))
            assert lager.serie("EQNR") == ny
        finally:
            t.close()
        # Den gamle basen er ikke rørt.
        t = sqlite3.connect(gammel)
        try:
            assert t.execute("SELECT * FROM kurs ORDER BY symbol, dato").fetchall() == kurs_foer
        finally:
            t.close()

    def test_en_base_en_versjon_bak_leses_av_sjekken(self, tmp_path):
        """Sjekken foer kallene leser basen med godta_en_versjon_bak, ogsaa
        den kvelden 0015 er flettet og basen staar paa 14 (story 2.8). Ville
        feilet med «no such column: hoey» hvis lageret alltid leste kolonnene."""
        katalog = tmp_path / "migrasjoner"
        katalog.mkdir()
        for fil in sorted(MIGRASJONSKATALOG.glob("*.sql")):
            if fil.name < "0015":
                shutil.copy(fil, katalog / fil.name)
        sti = tmp_path / "gammel.db"
        t = sqlite3.connect(sti)
        assert migrer(t, katalog) == 14
        t.execute(
            "INSERT INTO kurs (symbol, dato, slutt, justert_slutt, volum) VALUES ('EQNR', '2026-09-22', 100.0, 98.0, 1000)"
        )
        t.execute("INSERT INTO kursserie (symbol, hentet) VALUES ('EQNR', ?)", (HENTET.isoformat(),))
        t.commit()
        t.close()
        foer = sti.read_bytes()
        assert fp.manglende_i_basen(sti, TIRSDAG, AKSJEUNIVERS[:1]) == []
        assert AKSJEUNIVERS[0].symbol == "EQNR"
        t = sqlite3.connect(f"file:{sti}?mode=ro", uri=True)
        try:
            t.execute("PRAGMA query_only = ON")
            rader = SqliteKurslager(t, AKSJEUNIVERS, godta_en_versjon_bak=True).serie("EQNR")
        finally:
            t.close()
        assert [(r.hoey, r.lav) for r in rader] == [(None, None)]
        assert sti.read_bytes() == foer

    def test_paa_en_ny_base(self, tmp_path):
        t = _base(tmp_path / "ose.db")
        try:
            for tabell in ("kurs", "indeks"):
                assert [r[1] for r in t.execute(f"PRAGMA table_info({tabell})")][-2:] == ["hoey", "lav"]
        finally:
            t.close()


def _serie(siste: date, variant: str, dager: int = 60) -> list[dict]:
    """En serie hentingen godtar, med high og low etter varianten."""
    rader = []
    for i in range(dager):
        rad = {
            "date": (siste - timedelta(days=dager - 1 - i)).isoformat(),
            "close": 100.0 + i,
            "adjusted_close": 100.0 + i,
            "volume": 1000,
        }
        if variant == "med":
            rad.update(high=101.0 + i, low=99.0 + i)
        elif variant == "ubrukelige":
            rad.update(high=None, low="NA") if i % 2 else rad.update(high=0, low=-1)
        elif variant == "snudd":
            rad.update(high=99.0 + i, low=101.0 + i)
        rader.append(rad)
    return rader


VARIANTER = ("med", "uten", "ubrukelige", "snudd")


class TestHentingen:
    def test_hentingen_stopper_ikke_naar_hoey_eller_lav_mangler(self, tmp_path):
        """Kontrollen i storyen: ville feilet hvis en rad uten high eller low
        stoppet hentingen. Hver aksje har en av fire varianter, og alle 15
        lagres, med høy og lav bare der de kan brukes. Like mange kall som før:
        ett per aksje og ett for hovedindeksen."""
        raa, base = tmp_path / "data" / "raa", tmp_path / "data" / "db" / "ose.db"
        variant = {a.ticker: VARIANTER[i % len(VARIANTER)] for i, a in enumerate(AKSJEUNIVERS)}
        kall = []

        def hent(ticker, *_):
            kall.append(ticker)
            return _serie(TIRSDAG, variant.get(ticker, "uten"))

        utskrift = []
        fp.kjoer(
            raa,
            base,
            HENTET,
            "FALSK-NOEKKEL-123456",
            hent,
            utskrift.append,
            les_kvote=lambda _: {
                "apiRequests": 0,
                "apiRequestsDate": "2026-01-01",
                "dailyRateLimit": 20,
                "extraLimit": 0,
            },
        )
        assert len(kall) == len(AKSJEUNIVERS) + 1
        t = aapne_base(base)
        try:
            tall = {
                s: (n, h, lv)
                for s, n, h, lv in t.execute(
                    "SELECT symbol, count(*), count(hoey), count(lav) FROM kurs GROUP BY symbol"
                )
            }
            vurderinger = t.execute("SELECT count(*) FROM vurdering WHERE regnet = 'kveld'").fetchone()[0]
        finally:
            t.close()
        assert set(tall) == {a.symbol for a in AKSJEUNIVERS}, utskrift
        for aksje in AKSJEUNIVERS:
            n, med_hoey, med_lav = tall[aksje.symbol]
            assert n == 60
            if variant[aksje.ticker] == "med":
                assert (med_hoey, med_lav) == (60, 60), aksje.symbol
            else:
                assert (med_hoey, med_lav) == (0, 0), aksje.symbol
        assert vurderinger == len(AKSJEUNIVERS)
