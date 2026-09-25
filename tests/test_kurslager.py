"""Tester for Kursrad og Kurslager-porten - story 1.2, 1.3 og 1.4a, AD-19 og AD-3.

Skrivetestene (fixturen lager) kjoeres mot baade MinneKurslager og
SqliteKurslager. Lesetestene (fixturen leser) kjoeres i tillegg mot
SnapshotLeser, som bare er en Kursleser. Lagrene skal oppfoere seg likt; der
de ikke gjoer det, tar en av dem feil. Det som bare gjelder SQLite, staar i
test_lagring_sqlite.py, og det som bare gjelder oeyeblikksbildet, i
test_snapshotleser.py.

Kursrad er raden porten gir ut: norske feltnavn, og ingen av dem kan mangle.
Poenget er at en feilstavet noekkel blir en feil der dataene kommer inn, i
stedet for en None som forplanter seg inn i signalberegningen som et tall som
mangler.
"""

import dataclasses
import inspect
import sqlite3
import typing
from datetime import date, datetime, timedelta, timezone

import pytest

from kursdata import (
    AKSJEUNIVERS,
    Kursleser,
    Kurslager,
    Kursrad,
    MinneKurslager,
    SnapshotKilde,
    SnapshotLeser,
    UgyldigKursrad,
)
from lagring_sqlite import MIGRASJONSKATALOG, SqliteKurslager
from migrering import migrer

HENTET = datetime(2026, 9, 22, 8, 33, tzinfo=timezone.utc)


def rad(dato: str = "2026-09-21", slutt: float = 100.0, justert: float = 98.0,
        volum: int = 1000) -> Kursrad:
    return Kursrad(dato=date.fromisoformat(dato), slutt=slutt,
                   justert_slutt=justert, volum=volum)


class TestKursrad:
    def test_har_de_fire_norske_feltene(self):
        felter = [f.name for f in dataclasses.fields(Kursrad)]

        assert felter == ["dato", "slutt", "justert_slutt", "volum"]

    @pytest.mark.parametrize("mangler", ["dato", "slutt", "justert_slutt", "volum"])
    def test_avviser_aa_bli_konstruert_uten_et_felt(self, mangler):
        felt = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        del felt[mangler]

        with pytest.raises(TypeError):
            Kursrad(**felt)

    def test_feilstavet_noekkel_er_en_feil(self):
        """Det storyen finnes for. Med dict ville dette gitt None et sted senere."""
        with pytest.raises(TypeError):
            Kursrad(dato=date(2026, 9, 21), slutt=100.0, justert_slut=98.0, volum=1000)

    def test_eodhds_engelske_noekler_avvises(self):
        with pytest.raises(TypeError):
            Kursrad(date="2026-09-21", close=100.0, adjusted_close=98.0, volume=1000)

    @pytest.mark.parametrize("felt", ["slutt", "justert_slutt", "volum"])
    def test_none_avvises(self, felt):
        """Et felt som er der men tomt, er samme feil som et som mangler."""
        verdier = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        verdier[felt] = None

        with pytest.raises(UgyldigKursrad):
            Kursrad(**verdier)

    @pytest.mark.parametrize(
        "dato",
        ["2026-09-21", datetime(2026, 9, 21, 17, 30), None],
        ids=["tekst", "datetime", "None"],
    )
    def test_dato_maa_vaere_en_kalenderdato(self, dato):
        """AD-20: boersdagen er en kalenderdato. Tekst betyr at adapteren glemte
        aa oversette. datetime er en underklasse av date, men baerer et
        klokkeslett og kan gi feil dag - derfor avvises den eksplisitt."""
        with pytest.raises(UgyldigKursrad):
            Kursrad(dato=dato, slutt=100.0, justert_slutt=98.0, volum=1000)

    @pytest.mark.parametrize("felt", ["slutt", "justert_slutt"])
    @pytest.mark.parametrize("verdi", [float("nan"), float("inf"), float("-inf")],
                             ids=["nan", "inf", "-inf"])
    def test_ikke_endelige_tall_avvises(self, felt, verdi):
        """NaN og uendelig er gyldige float, men ikke kurser. Minnelageret ville
        lagret NaN mens SQLite avviste den (NOT NULL); uendelig ville begge
        lagret. Avvises her, der dataene kommer inn."""
        verdier = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        verdier[felt] = verdi

        with pytest.raises(UgyldigKursrad):
            Kursrad(**verdier)

    @pytest.mark.parametrize(
        ("felt", "verdi"),
        [
            ("slutt", "100.0"),
            ("justert_slutt", "98.0"),
            ("slutt", True),
            ("volum", 1000.0),
            ("volum", "1000"),
            ("volum", True),
        ],
        ids=["slutt-tekst", "justert-tekst", "slutt-bool", "volum-float",
             "volum-tekst", "volum-bool"],
    )
    def test_feil_type_avvises(self, felt, verdi):
        verdier = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        verdier[felt] = verdi

        with pytest.raises(UgyldigKursrad):
            Kursrad(**verdier)

    @pytest.mark.parametrize("felt", ["slutt", "justert_slutt"])
    def test_heltall_for_stort_for_float_avvises(self, felt):
        """math.isfinite(10**400) reiser OverflowError. Den skal ikke slippe ut."""
        verdier = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        verdier[felt] = 10**400

        with pytest.raises(UgyldigKursrad):
            Kursrad(**verdier)

    @pytest.mark.parametrize("felt", ["slutt", "justert_slutt"])
    @pytest.mark.parametrize("verdi", [0, 0.0, -0.01, -100])
    def test_kurs_paa_null_eller_under_avvises(self, felt, verdi):
        verdier = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        verdier[felt] = verdi

        with pytest.raises(UgyldigKursrad):
            Kursrad(**verdier)

    def test_negativt_volum_avvises(self):
        with pytest.raises(UgyldigKursrad):
            Kursrad(dato=date(2026, 9, 21), slutt=100.0, justert_slutt=98.0, volum=-1)

    def test_volum_null_godtas(self):
        """En dag uten handel er en lovlig dag."""
        assert Kursrad(dato=date(2026, 9, 21), slutt=100.0, justert_slutt=98.0, volum=0).volum == 0

    def test_ugyldig_kursrad_er_en_valueerror(self):
        """Kode som fanger ValueError, fanger den fortsatt."""
        assert issubclass(UgyldigKursrad, ValueError)

    def test_heltall_godtas_som_kurs(self):
        """EODHD sender hele kurser som heltall, for eksempel "open":250."""
        r = Kursrad(dato=date(2026, 9, 21), slutt=250, justert_slutt=250, volum=1000)

        assert r.slutt == 250 and r.justert_slutt == 250

    def test_dato_er_date(self):
        assert rad("2026-09-21").dato == date(2026, 9, 21)

    def test_kan_ikke_endres_etter_konstruksjon(self):
        r = rad()

        with pytest.raises(dataclasses.FrozenInstanceError):
            r.slutt = 1.0


class TestKurslagerProtokollen:
    def test_har_erstatt_serie_serie_og_sist_hentet_og_ingenting_annet(self):
        metoder = {
            navn for navn, _ in inspect.getmembers(Kurslager, inspect.isfunction)
            if not navn.startswith("_")
        }

        assert metoder == {"erstatt_serie", "serie", "sist_hentet"}

    def test_har_ingen_legg_til_rad(self):
        """AD-5: serien skjoetes aldri paa."""
        assert not hasattr(Kurslager, "legg_til_rad")

    def test_serie_lover_kursrader_ikke_dict(self):
        """Ville feilet hvis porten returnerte list[dict] med EODHDs noekler."""
        retur = typing.get_type_hints(Kurslager.serie)["return"]

        assert retur == list[Kursrad]

    def test_erstatt_serie_tar_kursrader_og_hentetidspunkt(self):
        hint = typing.get_type_hints(Kurslager.erstatt_serie)

        assert hint["rader"] == list[Kursrad]
        assert hint["hentet"] is datetime
        assert list(inspect.signature(Kurslager.erstatt_serie).parameters) == [
            "self", "symbol", "rader", "hentet",
        ]

    def test_sist_hentet_lover_datetime_eller_none(self):
        assert typing.get_type_hints(Kurslager.sist_hentet)["return"] == datetime | None

    def test_er_kursleser_pluss_bare_erstatt_serie(self):
        """Story 1.4a: Kurslager arver lesesiden og legger bare til skrivingen."""
        assert Kursleser in Kurslager.__mro__
        egne = {
            navn for navn, verdi in vars(Kurslager).items()
            if inspect.isfunction(verdi) and not navn.startswith("_")
        }

        assert egne == {"erstatt_serie"}


class TestKursleserProtokollen:
    def test_har_noeyaktig_serie_og_sist_hentet(self):
        metoder = {
            navn for navn, _ in inspect.getmembers(Kursleser, inspect.isfunction)
            if not navn.startswith("_")
        }

        assert metoder == {"serie", "sist_hentet"}

    def test_serie_lover_kursrader(self):
        assert typing.get_type_hints(Kursleser.serie)["return"] == list[Kursrad]

    def test_sist_hentet_lover_datetime_eller_none(self):
        assert typing.get_type_hints(Kursleser.sist_hentet)["return"] == datetime | None


@pytest.fixture(params=["minne", "sqlite"])
def lager(request, tmp_path):
    """Hver kontrakttest kjoeres mot begge lagrene. De skal oppfoere seg likt;
    der de ikke gjoer det, er det en av dem som tar feil."""
    if request.param == "minne":
        yield MinneKurslager()
        return
    tilkobling = sqlite3.connect(tmp_path / "ose.db")
    migrer(tilkobling, MIGRASJONSKATALOG)
    yield SqliteKurslager(tilkobling)
    tilkobling.close()


def datoer(lager, symbol: str = "EQNR") -> list[date]:
    return [r.dato for r in lager.serie(symbol)]


class TestKurslagerKontrakt:
    def test_oppfyller_protokollen(self, lager):
        assert isinstance(lager, Kurslager)
        for navn in ("erstatt_serie", "serie", "sist_hentet"):
            assert (
                inspect.signature(getattr(type(lager), navn))
                == inspect.signature(getattr(Kurslager, navn))
            )

    def test_erstatt_serie_erstatter_ikke_skjoeter(self, lager):
        """Ville feilet hvis adapteren skjoetet paa (AD-5)."""
        lager.erstatt_serie("EQNR", [rad("2026-09-17"), rad("2026-09-18")], HENTET)

        lager.erstatt_serie("EQNR", [rad("2026-09-21")], HENTET)

        assert datoer(lager) == [date(2026, 9, 21)]

    def test_erstatt_serie_roerer_ikke_de_andre_fjorten(self, lager):
        for aksje in AKSJEUNIVERS:
            lager.erstatt_serie(aksje.symbol, [rad("2026-09-18")], HENTET)
        senere = HENTET + timedelta(days=1)

        lager.erstatt_serie("EQNR", [rad("2026-09-21")], senere)

        andre = [a.symbol for a in AKSJEUNIVERS if a.symbol != "EQNR"]
        assert len(andre) == 14
        for symbol in andre:
            assert datoer(lager, symbol) == [date(2026, 9, 18)]
            assert lager.sist_hentet(symbol) == HENTET

    def test_dict_med_eodhds_noekler_avvises(self, lager):
        """Porten slipper ikke inn det gamle formatet bakveien."""
        with pytest.raises(TypeError):
            lager.erstatt_serie("EQNR", [{"date": "2026-09-21", "close": 100.0,
                                          "adjusted_close": 98.0, "volume": 1000}], HENTET)

        assert lager.serie("EQNR") == []

    def test_lagret_serie_foelger_ikke_endringer_i_kallerens_liste(self, lager):
        rader = [rad("2026-09-18")]
        lager.erstatt_serie("EQNR", rader, HENTET)

        rader.append(rad("2026-09-21"))

        assert len(lager.serie("EQNR")) == 1


class TestAvvisningEndrerIngenting:
    """En avvist skriving etterlater lageret slik det var: gammel serie og
    gammel tid. For SQLite er det transaksjonen som sikrer det."""

    SENERE = HENTET + timedelta(days=1)

    def _foer(self, lager):
        lager.erstatt_serie("EQNR", [rad("2026-09-18")], HENTET)

    def _uendret(self, lager):
        assert datoer(lager) == [date(2026, 9, 18)]
        assert lager.sist_hentet("EQNR") == HENTET

    def test_tom_serie_avvises(self, lager):
        """AD-5: hver henting dekker minst 175 dager, saa ingen lovlig kaller
        sender tom liste. Slapp den gjennom, ville historikken blitt slettet og
        faatt et ferskt tidsstempel paa ingenting - en feil som ser ut som
        suksess, samme feilklasse som AD-15."""
        self._foer(lager)

        with pytest.raises(ValueError):
            lager.erstatt_serie("EQNR", [], self.SENERE)

        self._uendret(lager)

    def test_tom_serie_avvises_ogsaa_for_nytt_symbol(self, lager):
        with pytest.raises(ValueError):
            lager.erstatt_serie("EQNR", [], HENTET)

        assert lager.serie("EQNR") == []
        assert lager.sist_hentet("EQNR") is None

    def test_to_rader_med_samme_dato_avvises(self, lager):
        """For SQLite er dette feilen midtveis: DELETE er kjoert og to rader
        satt inn foer primaernoekkelen stopper den tredje. Ville feilet hvis
        slettingen og innsettingen ikke laa i samme transaksjon."""
        self._foer(lager)

        with pytest.raises(ValueError):
            lager.erstatt_serie(
                "EQNR",
                [rad("2026-09-17"), rad("2026-09-21"), rad("2026-09-21")],
                self.SENERE,
            )

        self._uendret(lager)

    def test_tid_uten_sone_avvises(self, lager):
        """Et naivt tidspunkt kan ikke plasseres i UTC (AD-20)."""
        self._foer(lager)

        with pytest.raises(ValueError):
            lager.erstatt_serie("EQNR", [rad("2026-09-21")], datetime(2026, 9, 23, 8, 0))

        self._uendret(lager)

    def test_feil_radtype_avvises(self, lager):
        self._foer(lager)

        with pytest.raises(TypeError):
            lager.erstatt_serie("EQNR", [{"date": "2026-09-21"}], self.SENERE)

        self._uendret(lager)


class TestSistHentet:
    """sist_hentet settes av erstatt_serie i samme kall, per symbol, i UTC."""

    def test_er_per_symbol(self, lager):
        """AD-15: ett symbol kan feile og beholde sin gamle serie - og da ogsaa
        sin gamle tid. Et globalt tidsstempel ville sagt at DNB er fersk."""
        lager.erstatt_serie("DNB", [rad()], HENTET)
        senere = HENTET + timedelta(days=1)

        lager.erstatt_serie("EQNR", [rad()], senere)

        assert lager.sist_hentet("EQNR") == senere
        assert lager.sist_hentet("DNB") == HENTET


def eodhd(r: Kursrad) -> dict:
    """Kursrad tilbake til EODHDs form, slik et oeyeblikksbilde lagrer den."""
    return {"date": r.dato.isoformat(), "close": r.slutt,
            "adjusted_close": r.justert_slutt, "volume": r.volum}


@pytest.fixture(params=["minne", "sqlite", "snapshot"])
def leser(request, tmp_path):
    """Lesekontrakten kjoeres mot alle tre lagrene - story 1.4a.

    SnapshotLeser har ingen erstatt_serie, saa fixturen gir en fyllefunksjon
    per lager: fyll(serier, hentet) -> Kursleser. For de skrivbare lagrene
    kaller den erstatt_serie, for SnapshotLeser bygger den et
    oeyeblikksbilde. Et oeyeblikksbilde har en tid per fil, saa tester som
    krever ulike tider per symbol, bruker fixturen lager.
    """
    tilkobling = None

    def fyll(serier: dict[str, list[Kursrad]], hentet: datetime = HENTET):
        nonlocal tilkobling
        if request.param == "snapshot":
            return SnapshotLeser(SnapshotKilde(
                hentet=hentet.isoformat(),
                serier={s: [eodhd(r) for r in rader] for s, rader in serier.items()},
            ))
        if request.param == "minne":
            lager = MinneKurslager()
        else:
            tilkobling = sqlite3.connect(tmp_path / "ose.db")
            migrer(tilkobling, MIGRASJONSKATALOG)
            lager = SqliteKurslager(tilkobling)
        for symbol, rader in serier.items():
            lager.erstatt_serie(symbol, rader, hentet)
        return lager

    yield fyll
    if tilkobling is not None:
        tilkobling.close()


class TestKursleserKontrakt:
    """Det alle tre lagrene skal oppfylle naar de leses."""

    def test_oppfyller_protokollen(self, leser):
        lest = leser({"EQNR": [rad()]})

        assert isinstance(lest, Kursleser)
        for navn in ("serie", "sist_hentet"):
            assert (
                inspect.signature(getattr(type(lest), navn))
                == inspect.signature(getattr(Kursleser, navn))
            )

    def test_serie_gir_kursrader_med_samme_verdier(self, leser):
        inn = [rad("2026-09-18", 101.5, 99.25, 1234), rad("2026-09-21", 102.0, 100.0, 5678)]
        lest = leser({"EQNR": inn})

        serie = lest.serie("EQNR")

        assert serie == inn
        assert all(isinstance(r, Kursrad) for r in serie)
        assert all(type(r.dato) is date for r in serie)

    def test_serie_er_kronologisk_uansett_rekkefoelge_inn(self, leser):
        lest = leser({"EQNR": [rad("2026-09-21"), rad("2026-09-18")]})

        assert datoer(lest) == [date(2026, 9, 18), date(2026, 9, 21)]

    def test_serie_gir_sorterte_unike_datoer(self, leser):
        inn = [rad("2026-09-21"), rad("2026-09-16"), rad("2026-09-18"), rad("2026-09-17")]
        lest = leser({"EQNR": inn})

        ut = datoer(lest)

        assert ut == sorted(set(ut))
        assert len(ut) == len(inn)

    def test_ukjent_symbol_gir_tom_liste(self, leser):
        assert leser({}).serie("EQNR") == []

    def test_utlevert_serie_kan_ikke_endre_lageret(self, leser):
        lest = leser({"EQNR": [rad("2026-09-18")]})

        lest.serie("EQNR").append(rad("2026-09-21"))

        assert len(lest.serie("EQNR")) == 1


class TestKursleserSistHentet:
    def test_ukjent_symbol_har_ingen_tid(self, leser):
        assert leser({}).sist_hentet("EQNR") is None

    def test_fylt_symbol_har_tiden_det_ble_hentet(self, leser):
        assert leser({"EQNR": [rad()]}).sist_hentet("EQNR") == HENTET

    def test_leveres_i_utc(self, leser):
        """AD-20: tidsstempler i UTC. Et tidspunkt med annen sone regnes om,
        ikke kastes - oeyeblikket er det samme."""
        oslo = HENTET.astimezone(timezone(timedelta(hours=2)))

        tid = leser({"EQNR": [rad()]}, oslo).sist_hentet("EQNR")

        assert tid == HENTET
        assert tid.utcoffset() == timedelta(0)

    @pytest.mark.parametrize("symbol", ["EQNR", "DNB"], ids=["fylt", "ukjent"])
    def test_ingen_tid_hvis_og_bare_hvis_tom_serie(self, leser, symbol):
        """Lesekontrakten, begge retninger: tom serie gir None, og None gir
        tom serie. Ingen serie uten tid, og ingen tid uten serie."""
        lest = leser({"EQNR": [rad()]})

        assert (lest.sist_hentet(symbol) is None) == (lest.serie(symbol) == [])
