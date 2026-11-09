"""Story 2.6 og 8.14: justeringsdagene, regnet av kursserien alene.

Spesifikasjonen er spec-2-6-justeringsdager.md. Hver test lager sin egen base
under tmp_path (regel 22), og ingen test gjør nettkall (AD-8). Kursene er
oppdiktet (regel 16).
"""

import ast
import inspect
import re
from datetime import date, datetime, timedelta, timezone

import pytest

import app as app_modul
import fetch_prices as fp
import justeringsdager as jd
import lagring_sqlite
from kursdata import Kursrad
from test_fetch_prices import NOEKKEL, nok_kvote, serie_til

TIRSDAG = date(2026, 9, 22)
JUSTERT = "EQNR"


def _rad(dag: int, slutt: float, justert: float) -> Kursrad:
    return Kursrad(dato=date(2026, 9, dag), slutt=slutt, justert_slutt=justert, volum=1000)


class TestRegelen:
    """2.6: dagen merkes når endringen i sluttkursen og i den justerte kursen spriker."""

    def test_en_vanlig_dag_merkes_ikke(self):
        """Ville feilet hvis en dag der de to kursene endret seg likt, ble
        merket."""
        assert not jd.er_justeringsdag(_rad(14, 100.0, 90.0), _rad(15, 102.0, 91.8))

    def test_en_dag_der_de_spriker_merkes(self):
        """Ville feilet hvis en dag der kilden regnet de eldre kursene om, ikke
        ble merket."""
        assert jd.er_justeringsdag(_rad(14, 100.0, 98.0), _rad(15, 99.0, 99.0))

    def test_terskelen(self):
        """Ville feilet hvis terskelen var en annen enn 0,1 prosentpoeng, eller
        en forskjell på akkurat terskelen ble merket."""
        assert jd.TERSKEL_PP == 0.1
        # 1,00 % i sluttkursen og 1,10 % i den justerte: akkurat terskelen.
        assert not jd.er_justeringsdag(_rad(14, 100.0, 100.0), _rad(15, 101.0, 101.1 - 1e-9))
        assert jd.er_justeringsdag(_rad(14, 100.0, 100.0), _rad(15, 101.0, 101.11))

    def test_foerste_rad_merkes_ikke(self):
        """Ville feilet hvis den første raden, som ikke har en dag før seg, ga
        en justeringsdag. En kurs på null avvises alt av Kursrad."""
        assert jd.justeringsdager([_rad(15, 99.0, 99.0)]) == ()

    def test_det_siste_aaret(self):
        """8.14: ville feilet hvis en dag eldre enn et år, eller etter dagen
        siden viser, kom med."""
        serie = [
            Kursrad(dato=date(2025, 9, 21), slutt=100.0, justert_slutt=98.0, volum=1),
            Kursrad(dato=date(2025, 9, 22), slutt=99.0, justert_slutt=99.0, volum=1),
            Kursrad(dato=date(2025, 9, 23), slutt=100.0, justert_slutt=98.0, volum=1),
            Kursrad(dato=date(2025, 9, 24), slutt=99.0, justert_slutt=99.0, volum=1),
        ]
        assert jd.justeringsdager(serie) == (date(2025, 9, 22), date(2025, 9, 23), date(2025, 9, 24))
        assert jd.justeringsdager(serie, til=date(2026, 9, 23)) == (date(2025, 9, 24),)
        assert jd.justeringsdager(serie, til=date(2025, 9, 23)) == (date(2025, 9, 22), date(2025, 9, 23))

    def test_bare_kursserien(self):
        """Ville feilet hvis dagene ble lest fra en annen kilde enn
        kursserien, som meldingene: modulen importerer bare kursraden."""
        moduler = set()
        for node in ast.walk(ast.parse(inspect.getsource(jd))):
            if isinstance(node, ast.ImportFrom):
                moduler.add(node.module)
            elif isinstance(node, ast.Import):
                moduler.update(a.name for a in node.names)
        assert moduler == {"datetime", "kursdata"}


def _hent(ticker, *_):
    """EQNR har en justeringsdag siste børsdag: kilden har regnet kursene
    før den ned med 2 %. De andre har ingen."""
    serie = serie_til(TIRSDAG, dager=64)
    if ticker.startswith(JUSTERT + "."):
        serie = [
            {**r, "adjusted_close": r["adjusted_close"] * (0.98 if r["date"] < TIRSDAG.isoformat() else 1)}
            for r in serie
        ]
    return serie


@pytest.fixture
def klient(tmp_path, monkeypatch):
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    fp.kjoer(
        raa,
        base,
        datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc),
        NOEKKEL,
        _hent,
        lambda _: None,
        les_kvote=nok_kvote,
    )
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


def _spennet(side: str, klasse: str) -> str:
    treff = re.search(rf'<span class="[^"]*\b{klasse}\b[^"]*"[^>]*>(.*?)</span>', side, re.S)
    assert treff, klasse
    return treff.group(0)


class TestOversikten:
    """2.6: merket under endringen i oversikten."""

    def test_bare_aksjen_med_justeringsdag_merkes(self, klient):
        """Ville feilet hvis en aksje uten justeringsdag ble merket, eller
        aksjen med en ikke ble det."""
        side = _side(klient, "/")
        assert side.count('<span class="justeringsdag"') == 1
        raden = side.split(f'id="rad-{JUSTERT}"', 1)[1].split("</tr>", 1)[0]
        assert '<span class="justeringsdag"' in raden

    def test_ikke_for_en_periode(self, klient):
        """Ville feilet hvis merket sto ved endringen for en periode, der
        sluttkursen og endringen ikke gjelder samme dag."""
        assert 'class="justeringsdag"' not in _side(klient, "/?periode=1-mnd")

    def test_valgt_dag(self, klient):
        """Ville feilet hvis en dag valgt med datoen fikk merket fra siste
        børsdag, eller ikke sitt eget."""
        assert 'class="justeringsdag"' in _side(klient, "/?periode=velg&dag=2026-09-22")
        assert 'class="justeringsdag"' not in _side(klient, "/?periode=velg&dag=2026-09-21")

    def test_ordet_er_justeringsdag(self, klient):
        """8.14: ville feilet hvis merket kalte justeringen et utbytte."""
        merket = _spennet(_side(klient, "/"), "justeringsdag")
        assert "justeringsdag" in merket and "utbytte" not in merket.lower()


class TestAksjesiden:
    """2.6 og 8.14: kortet, grafen og teksten under."""

    def test_kortet_sier_justeringsdag(self, klient):
        """2.6: ville feilet hvis endringen på aksjesiden ikke sa at dagen er
        en justeringsdag, eller sa det for en aksje uten."""
        kort = _spennet(_side(klient, f"/aksje/{JUSTERT}"), "justeringsdag")
        assert "Justeringsdag" in kort and "utbytte" not in kort.lower()
        assert 'forklaring justeringsdag"' not in _side(klient, "/aksje/DNB")

    def test_grafen_og_antallet(self, klient):
        """8.14: ville feilet hvis grafen ikke merket dagen, eller antallet og
        den siste datoen manglet i aksjedetaljen."""
        side = _side(klient, f"/aksje/{JUSTERT}")
        assert side.count('<line class="justeringsdag"') == 2  # den brede og den smale grafen
        tekst = _spennet(side, "justeringstekst")
        assert "Det siste året var det 1 justeringsdag, den siste 22.09." in tekst

    def test_ingen_justeringsdager(self, klient):
        """8.14: ville feilet hvis en aksje uten justeringsdager fikk streker
        eller et antall."""
        side = _side(klient, "/aksje/DNB")
        assert '<line class="justeringsdag"' not in side
        assert "Ingen justeringsdager det siste året." in _spennet(side, "justeringstekst")

    def test_teksten_sier_ikke_utbytte_eller_neste(self, klient):
        """8.14: ville feilet hvis teksten ved dagene kalte dem utbytte, eller
        sa noe om neste justering (NFR-06)."""
        for symbol in (JUSTERT, "DNB"):
            tekst = _spennet(_side(klient, f"/aksje/{symbol}"), "justeringstekst").lower()
            assert "utbytte" not in tekst and "neste" not in tekst

    def test_dagene_er_de_samme_som_2_6_finner(self, klient):
        """8.14: ville feilet hvis grafen merket andre dager enn regelen i 2.6
        finner i kursserien til samme dag."""
        side = _side(klient, f"/aksje/{JUSTERT}?periode=velg&dag=2026-09-21")
        assert '<line class="justeringsdag"' not in side
        assert "Ingen justeringsdager det siste året." in _spennet(side, "justeringstekst")
        # Dagen før er ikke en justeringsdag i oversikten heller.
        assert 'class="justeringsdag"' not in _side(klient, "/?periode=velg&dag=2026-09-21")


def test_aaret_er_365_dager():
    """Ville feilet hvis «det siste året» var noe annet enn dagene etter
    samme dato året før."""
    assert jd.AARET == timedelta(days=365)
