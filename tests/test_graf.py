"""Tester for koordinatregningen. En linje som ligger galt, ser riktig ut."""

import pytest

from aksjedetalj import Punkt
from graf import BREDDE, HOYDE, MARG_X, MARG_Y, bygg_graf


def punkter(kurser, ma50=None):
    ma50 = ma50 or [None] * len(kurser)
    return tuple(
        Punkt(dato=f"2026-01-{i + 1:02d}", kurs=k, ma50=m)
        for i, (k, m) in enumerate(zip(kurser, ma50))
    )


def koordinater(linje):
    return [tuple(float(d) for d in par.split(",")) for par in linje.split()]


class TestTomtGrunnlag:
    def test_none_uten_punkter(self):
        assert bygg_graf(()) is None

    def test_none_med_bare_ett_punkt(self):
        """En linje trenger to punkter."""
        assert bygg_graf(punkter([100.0])) is None


class TestSkalering:
    def test_hoyeste_kurs_havner_oeverst(self):
        graf = bygg_graf(punkter([100.0, 200.0]))
        forste, siste = koordinater(graf.kurslinje)

        assert siste[1] < forste[1], "hoeyere kurs skal ha lavere y i SVG"

    def test_linja_holder_seg_innenfor_tegneflaten(self):
        graf = bygg_graf(punkter([50.0, 300.0, 120.0, 90.0]))

        for x, y in koordinater(graf.kurslinje):
            assert MARG_X <= x <= BREDDE - MARG_X
            assert MARG_Y <= y <= HOYDE - MARG_Y

    def test_foerste_og_siste_punkt_ligger_i_hver_sin_ende(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0]))
        punkt = koordinater(graf.kurslinje)

        assert punkt[0][0] == pytest.approx(MARG_X)
        assert punkt[-1][0] == pytest.approx(BREDDE - MARG_X)

    def test_flat_serie_deler_ikke_paa_null(self):
        graf = bygg_graf(punkter([100.0, 100.0, 100.0]))

        assert graf is not None
        assert graf.lav < graf.hoy
        for _, y in koordinater(graf.kurslinje):
            assert MARG_Y <= y <= HOYDE - MARG_Y


class TestMa50:
    def test_snittet_faar_egen_linje(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0], [99.0, 100.0, 101.0]))

        assert graf.har_ma50
        assert len(koordinater(graf.ma50linje)) == 3

    def test_uten_snitt_er_linja_tom(self):
        graf = bygg_graf(punkter([100.0, 110.0]))

        assert graf.ma50linje == ""
        assert graf.har_ma50 is False

    def test_snittet_er_med_i_skalaen(self):
        """Var snittet utenfor regnestykket, kunne MA50-linja havnet utenfor
        flaten uten at noe feilet - og sjekk 1 ville blitt usynlig."""
        graf = bygg_graf(punkter([100.0, 101.0], [40.0, 41.0]))

        for _, y in koordinater(graf.ma50linje):
            assert MARG_Y <= y <= HOYDE - MARG_Y
        assert graf.lav < 40.0

    def test_hull_i_snittet_hoppes_over(self):
        """MA50 mangler i starten av en kort serie. Linja skal begynne der
        snittet begynner, ikke klaske ned i null."""
        graf = bygg_graf(punkter([100.0, 110.0, 120.0], [None, 100.0, 105.0]))

        assert len(koordinater(graf.ma50linje)) == 2

    def test_ett_enkelt_snittpunkt_gir_ingen_linje(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0], [None, None, 105.0]))
        assert graf.ma50linje == ""


class TestRutenett:
    def test_tre_linjer_fra_lav_til_hoy(self):
        graf = bygg_graf(punkter([100.0, 200.0]))

        assert len(graf.rutenett) == 3
        assert graf.rutenett[0].verdi == pytest.approx(graf.lav)
        assert graf.rutenett[-1].verdi == pytest.approx(graf.hoy)

    def test_datoene_kommer_fra_ytterpunktene(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0]))

        assert graf.forste_dato == "2026-01-01"
        assert graf.siste_dato == "2026-01-03"
