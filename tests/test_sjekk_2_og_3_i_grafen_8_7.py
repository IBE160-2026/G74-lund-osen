"""Story 8.7: sjekk 2 og 3 i kursgrafen (FR-202, tillegget).

Spesifikasjonen er spec-8-7-sjekk-2-og-3-i-grafen.md. Kursene er oppdiktet
(regel 16), og hver test som trenger en base, lager sin egen under tmp_path
(regel 22). Ingen nettkall (AD-8).
"""

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import pytest

import app as app_modul
import fetch_prices as fp
import lagring_sqlite
from aksjedetalj import bygg_punkter
from graf import VOLUMFELT, bygg_graf
from kursdata import Kursrad
from lagring_sqlite import SqliteVurderingslager, aapne_base
from signalberegning import STANDARD, bevegelse, interesse, medianvolum, standardavvik
from test_fetch_prices import NOEKKEL, nok_kvote, serie_til

START = date(2026, 3, 2)


def _serie(antall: int = 120, volum=lambda i: 1000 + (i * 37) % 900) -> list[Kursrad]:
    """En serie med kurs som svinger og volum som varierer, én rad per dag."""
    return [
        Kursrad(
            dato=START + timedelta(days=i),
            slutt=100.0 + (i % 7) - (i % 5) * 0.8,
            justert_slutt=100.0 + (i % 7) - (i % 5) * 0.8,
            volum=volum(i),
        )
        for i in range(antall)
    ]


class TestTalleneErSjekkenes:
    """Medianen, grensen og båndet regnes med de samme funksjonene og vinduene som sjekk 2 og 3."""

    def test_den_siste_dagen_er_sjekkenes(self):
        """Ville feilet hvis den siste dagen i grafen hadde et annet
        medianvolum eller standardavvik enn sjekk 2 og 3 regner."""
        serie = _serie()
        kurser = [r.justert_slutt for r in serie]
        volumer = [float(r.volum) for r in serie]
        siste = bygg_punkter(serie)[-1]
        assert siste.avvik == bevegelse(kurser).grense
        assert siste.volum / siste.median == interesse(kurser, volumer).maaling
        assert siste.forrige == serie[-2].justert_slutt

    def test_streken_foelger_vinduet_i_parametre(self):
        """Ville feilet hvis streken var en median over et annet vindu enn
        sjekk 3: da forklarer grafen en annen regel enn den som ble brukt."""
        serie = _serie()
        volumer = [float(r.volum) for r in serie]
        smalt = replace(STANDARD, volum_vindu=5, volatilitet_vindu=5)
        vanlig, kort = bygg_punkter(serie), bygg_punkter(serie, smalt)
        assert kort[-1].median == medianvolum(volumer, smalt) != vanlig[-1].median
        assert vanlig[-1].median == medianvolum(volumer, STANDARD)
        kurser = [r.justert_slutt for r in serie]
        assert kort[-1].avvik == standardavvik(kurser, smalt) != vanlig[-1].avvik
        g_vanlig = bygg_graf(vanlig, volumfaktor=STANDARD.volumfaktor)
        g_kort = bygg_graf(kort, volumfaktor=STANDARD.volumfaktor)
        assert g_vanlig.medianstreker != g_kort.medianstreker
        assert g_vanlig.baand != g_kort.baand

    def test_dagene_foer_vinduet_har_ingen_median(self):
        """Ville feilet hvis en dag uten nok dager før fikk en median eller et
        standardavvik regnet av færre dager enn vinduet."""
        punkter = bygg_punkter(_serie(), start=START)
        assert punkter[STANDARD.volum_vindu - 1].median is None
        assert punkter[STANDARD.volum_vindu].median is not None
        assert punkter[STANDARD.volatilitet_vindu].avvik is None
        assert punkter[STANDARD.volatilitet_vindu + 1].avvik is not None


class TestGrafen:
    """Volumsøylene, strekene og båndet i samme SVG."""

    def test_baand_soeyler_og_streker(self):
        """Ville feilet hvis grafen manglet båndet, søylene eller strekene,
        eller grensen ikke var volumfaktoren ganger medianen."""
        punkter = bygg_punkter(_serie())
        g = bygg_graf(punkter, volumfaktor=STANDARD.volumfaktor)
        assert g.baand and g.volumsoeyler and g.medianstreker and g.grensestreker
        assert len(g.volumsoeyler) == len(punkter)
        assert g.totalhoyde == g.hoyde + VOLUMFELT
        # Grensen ligger over medianen (lavere y), med samme x.
        m = [tuple(map(float, p.split(","))) for p in g.medianstreker[0].split()]
        gr = [tuple(map(float, p.split(","))) for p in g.grensestreker[0].split()]
        bunn = g.volumbunn
        for (xm, ym), (xg, yg) in zip(m, gr, strict=True):
            assert xm == xg
            assert (bunn - yg) == pytest.approx(STANDARD.volumfaktor * (bunn - ym), abs=0.15)

    def test_uten_volumfaktor_som_foer(self):
        """Ville feilet hvis en graf uten volumfaktoren fikk feltet for
        volumet, som de andre kallene av bygg_graf ikke ber om."""
        g = bygg_graf(bygg_punkter(_serie()))
        assert not g.baand and not g.volumsoeyler and g.totalhoyde == g.hoyde

    def test_median_null_gir_ingen_strek(self):
        """NFR-08: ville feilet hvis streken ble tegnet der medianvolumet er 0,
        eller grafen ikke talte dagene uten strek."""
        serie = _serie(volum=lambda i: 0 if 60 <= i < 90 else 500)
        punkter = bygg_punkter(serie)
        g = bygg_graf(punkter, volumfaktor=STANDARD.volumfaktor)
        uten = sum(1 for p in punkter if not p.median)
        assert uten > 0 and g.uten_median == uten
        assert len(g.medianstreker) == 2  # brutt der medianen er 0


def _hent(ticker, *_):
    return serie_til(date(2026, 9, 22), dager=80)


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
    return app_modul.app.test_client(), base


class TestAksjesiden:
    def test_i_samme_svg_og_teksten(self, klient):
        """Ville feilet hvis volumsøylene sto i en annen SVG enn kursgrafen,
        eller teksten under grafen ikke forklarte båndet og strekene med
        tallene fra Parametre."""
        k, _ = klient
        side = k.get("/aksje/EQNR").data.decode("utf-8")
        for klasse in ('<svg class="graf"', '<svg class="graf smal"'):
            svg = side.split(klasse, 1)[1].split("</svg>", 1)[0]
            assert 'class="volumsoeyle"' in svg and 'class="baand"' in svg and 'class="medianstrek"' in svg
        tekst = side.split('class="sjekkene-i-grafen">', 1)[1].split("</span>", 1)[0]
        assert f"de {STANDARD.volatilitet_vindu} børsdagene før" in tekst
        assert f"medianvolumet de {STANDARD.volum_vindu} børsdagene før" in tekst
        assert "1,5 × medianen" in tekst

    def test_siste_dag_som_vurderingen(self, klient):
        """Ville feilet hvis den siste dagen i grafen ga et annet utslag enn
        sjekkene i aksjedetaljen, som leser den lagrede vurderingen."""
        _, base = klient
        t = aapne_base(base)
        try:
            vurdering = SqliteVurderingslager(t, lambda: datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)).les(
                "EQNR", date(2026, 9, 22)
            )
            serie = lagring_sqlite.SqliteKurslager(t).serie("EQNR")
        finally:
            t.close()
        siste = bygg_punkter(serie)[-1]
        assert siste.avvik == vurdering.standardavvik
        assert (siste.volum / siste.median if siste.median else None) == vurdering.volumforhold
