"""Oversiktsleseren - story 2.2b, FR-101, FR-408, FR-409, AD-3, AD-21.

Porten og SQLite-adapteren proeves sammen mot en base i minnet, migrert som i
drift. Vurderingene skrives gjennom SqliteVurderingslager med klokka stilt paa
dagen, slik hentekommandoen gjoer, saa skriv brukes uendret (AD-7). Ingen
nett (AD-8).
"""

import inspect
import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

from kursdata import AKSJEUNIVERS, Kursrad
from lagring_sqlite import (
    MIGRASJONSKATALOG,
    SqliteKurslager,
    SqliteOversiktsleser,
    SqliteVurderingslager,
)
from migrering import migrer
from oversiktsdata import Oversiktsleser, Oversiktspost
from vurderingsdata import Grunn, Vurdering

HENTET = datetime(2026, 10, 2, 20, 30, tzinfo=timezone.utc)
FREDAG = date(2026, 10, 2)
TORSDAG = date(2026, 10, 1)


@pytest.fixture
def tilkobling():
    tilkobling = sqlite3.connect(":memory:")
    migrer(tilkobling, MIGRASJONSKATALOG)
    yield tilkobling
    tilkobling.close()


def kurser(siste: date, antall: int = 3, start: float = 100.0) -> list[Kursrad]:
    """antall kalenderdager fram til og med siste, med stigende kurs."""
    return [
        Kursrad(
            dato=siste - timedelta(days=antall - 1 - i),
            slutt=start + i,
            justert_slutt=start + i - 0.5,
            volum=1000 + i,
        )
        for i in range(antall)
    ]


def vurdering(styrke: int = 1, trend: int = 1) -> Vurdering:
    return Vurdering(
        styrke=styrke, retning="Positiv" if trend else "Ingen", trend=trend,
        bevegelse=0, interesse=0, slutt=102.0, justert_slutt=101.5,
        trend_avvik=0.03 if trend else 0.0, dagens_endring=0.001,
        standardavvik=0.01, volumforhold=1.0,
    )


def skriv(tilkobling, symbol: str, dato: date, innhold) -> None:
    """Skriv raden gjennom porten, med klokka stilt paa dagen (AD-7)."""
    oeyeblikk = datetime(dato.year, dato.month, dato.day, 20, 0, tzinfo=timezone.utc)
    SqliteVurderingslager(tilkobling, lambda: oeyeblikk).skriv(symbol, dato, innhold)


class TestPorten:
    def test_porten_har_bare_lesemetoder(self):
        metoder = {
            navn for navn, _ in inspect.getmembers(Oversiktsleser, inspect.isfunction)
            if not navn.startswith("_")
        }
        assert metoder == {"oversikt", "post"}

    def test_adapteren_har_ingen_skrivemetode(self):
        metoder = {
            navn for navn, _ in inspect.getmembers(SqliteOversiktsleser, inspect.isfunction)
            if not navn.startswith("_")
        }
        assert metoder == {"oversikt", "post"}

    def test_adapteren_oppfyller_porten(self, tilkobling):
        assert isinstance(SqliteOversiktsleser(tilkobling), Oversiktsleser)


class TestOversikten:
    def test_en_post_per_aksje_i_rekkefoelgen_fra_aksje(self, tilkobling):
        poster = SqliteOversiktsleser(tilkobling).oversikt()
        rekkefoelge = [s for (s,) in tilkobling.execute("SELECT symbol FROM aksje ORDER BY rowid")]
        assert [p.aksje.symbol for p in poster] == rekkefoelge
        assert all(p.nyeste is None and p.innhold is None for p in poster)

    def test_selskapene_kommer_fra_basen(self, tilkobling):
        tilkobling.execute("UPDATE aksje SET navn = 'Annet navn' WHERE symbol = 'EQNR'")
        post = SqliteOversiktsleser(tilkobling).post("EQNR")
        assert post.aksje.navn == "Annet navn"

    def test_faerre_aksjer_gir_faerre_poster(self, tilkobling):
        tilkobling.execute("DELETE FROM aksje WHERE symbol IN ('DNO', 'MPCC')")
        poster = SqliteOversiktsleser(tilkobling).oversikt()
        assert len(poster) == len(AKSJEUNIVERS) - 2
        assert {"DNO", "MPCC"}.isdisjoint(p.aksje.symbol for p in poster)

    def test_nyeste_og_forrige_kurs_og_hentet(self, tilkobling):
        serie = kurser(FREDAG, antall=5)
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", serie, HENTET)
        post = SqliteOversiktsleser(tilkobling).post("EQNR")
        assert post.nyeste == serie[-1]
        assert post.forrige == serie[-2]
        assert post.hentet == HENTET

    def test_en_kurs_gir_ingen_forrige(self, tilkobling):
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(FREDAG, antall=1), HENTET)
        post = SqliteOversiktsleser(tilkobling).post("EQNR")
        assert post.nyeste is not None and post.forrige is None

    def test_aksje_uten_kurser_har_ingen_nyeste(self, tilkobling):
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(FREDAG), HENTET)
        poster = {p.aksje.symbol: p for p in SqliteOversiktsleser(tilkobling).oversikt()}
        assert poster["EQNR"].nyeste is not None
        assert poster["DNB"] == Oversiktspost(
            aksje=poster["DNB"].aksje, nyeste=None, forrige=None, hentet=None, innhold=None
        )


class TestVurderingen:
    def test_raden_for_datoen_til_nyeste_kurs(self, tilkobling):
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(FREDAG), HENTET)
        skriv(tilkobling, "EQNR", TORSDAG, vurdering(styrke=1))
        skriv(tilkobling, "EQNR", FREDAG, vurdering(styrke=0, trend=0))
        post = SqliteOversiktsleser(tilkobling).post("EQNR")
        assert post.innhold == vurdering(styrke=0, trend=0)

    def test_rad_med_grunn(self, tilkobling):
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(FREDAG), HENTET)
        skriv(tilkobling, "EQNR", FREDAG, Grunn.SIGNAL_IKKE_REGNET)
        assert SqliteOversiktsleser(tilkobling).post("EQNR").innhold is Grunn.SIGNAL_IKKE_REGNET

    def test_ingen_rad_gir_none(self, tilkobling):
        # Kurser uten vurdering, som etter --les-inn.
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(FREDAG), HENTET)
        skriv(tilkobling, "EQNR", TORSDAG, vurdering())
        assert SqliteOversiktsleser(tilkobling).post("EQNR").innhold is None

    def test_gaarsdagens_vurdering_naar_dagens_rad_har_grunn(self, tilkobling):
        # Hentingen feilet fredag: nyeste kurs er fra torsdag, og fredagens rad
        # har grunnen. Siden viser torsdagens vurdering med torsdagens dato.
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(TORSDAG), HENTET)
        skriv(tilkobling, "EQNR", TORSDAG, vurdering(styrke=1))
        skriv(tilkobling, "EQNR", FREDAG, Grunn.SYMBOL_FEILET)
        post = SqliteOversiktsleser(tilkobling).post("EQNR")
        assert post.nyeste.dato == TORSDAG
        assert post.innhold == vurdering(styrke=1)

    def test_post_er_lik_posten_i_oversikten(self, tilkobling):
        SqliteKurslager(tilkobling).erstatt_serie("EQNR", kurser(FREDAG), HENTET)
        skriv(tilkobling, "EQNR", FREDAG, vurdering())
        leser = SqliteOversiktsleser(tilkobling)
        fra_oversikten = {p.aksje.symbol: p for p in leser.oversikt()}
        assert leser.post("EQNR") == fra_oversikten["EQNR"]

    def test_ukjent_symbol_gir_none(self, tilkobling):
        leser = SqliteOversiktsleser(tilkobling)
        assert leser.post("EQNR.OL") is None
        assert leser.post("FINNESIKKE") is None
