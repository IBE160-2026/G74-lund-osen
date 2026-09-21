"""Tester for aksjedetaljen. Ingen nettverk, ingen filer."""

import pytest

from aksjedetalj import (
    GRAFVINDU_DAGER,
    Punkt,
    bygg_detalj,
    bygg_punkter,
    finn_aksje,
    glidende_snitt,
)
from kursdata import AKSJEUNIVERS, Aksje, MinneKilde
from signalberegning import Parametre

EQNR = Aksje("EQNR", "EQNR.OL", "Equinor", "Energi")
KORT = Parametre(ma_vindu=5, volatilitet_vindu=3, volum_vindu=3)


def serie(kurser, volumer=None, start="2026-01-01"):
    """Kursrader med ekte, sammenhengende datoer."""
    from datetime import date, timedelta

    d0 = date.fromisoformat(start)
    volumer = volumer or [1000] * len(kurser)
    return [
        {
            "date": (d0 + timedelta(days=i)).isoformat(),
            "close": kurs,
            "adjusted_close": kurs,
            "volume": volum,
        }
        for i, (kurs, volum) in enumerate(zip(kurser, volumer))
    ]


class TestGlidendeSnitt:
    def test_none_til_vinduet_er_fullt(self):
        assert glidende_snitt([1.0, 2.0, 3.0], 3) == [None, None, 2.0]

    def test_ruller_videre(self):
        assert glidende_snitt([1.0, 2.0, 3.0, 4.0], 2) == [None, 1.5, 2.5, 3.5]

    def test_tom_serie_gir_tom_liste(self):
        assert glidende_snitt([], 5) == []


class TestBjyggPunkter:
    def test_klipper_til_seks_maaneder(self):
        """Ett aar inn, seks maaneder ut."""
        rader = serie([100.0] * 365, start="2025-09-21")

        punkter = bygg_punkter(rader, KORT)

        assert len(punkter) < len(rader)
        from datetime import date

        forste = date.fromisoformat(punkter[0].dato)
        siste = date.fromisoformat(punkter[-1].dato)
        assert (siste - forste).days <= GRAFVINDU_DAGER

    def test_kort_serie_klippes_ikke(self):
        rader = serie([100.0] * 10)
        assert len(bygg_punkter(rader, KORT)) == 10

    def test_ma50_beholdes_for_foerste_punkt_i_vinduet(self):
        """Snittet regnes paa HELE serien og klippes etterpaa.

        Regnet vi bare paa vinduet, ville de foerste dagene mistet snittet
        sitt uten grunn - dataene finnes jo.
        """
        rader = serie([100.0] * 300, start="2025-09-21")

        punkter = bygg_punkter(rader, KORT)

        assert punkter[0].ma50 is not None

    def test_ma50_er_none_naar_historikken_er_for_kort(self):
        punkter = bygg_punkter(serie([100.0, 101.0, 102.0]), KORT)
        assert punkter[0].ma50 is None

    def test_kurs_og_snitt_tegnes_fra_samme_justerte_serie(self):
        """Tegnet vi close mot et snitt fra adjusted_close, ville de ligget
        paa hver sin skala - og avstanden ville vaert stoerst for aksjene som
        betaler mest utbytte."""
        rader = serie([100.0] * 10)
        for rad in rader:
            rad["close"] = 200.0  # ujustert er dobbelt saa hoey

        punkter = bygg_punkter(rader, KORT)

        assert punkter[-1].kurs == 100.0
        assert punkter[-1].ma50 == pytest.approx(100.0)

    def test_taaler_rader_uten_kurs(self):
        rader = serie([100.0] * 6)
        rader[2]["close"] = None
        rader[2]["adjusted_close"] = None

        punkter = bygg_punkter(rader, KORT)

        assert all(p.kurs is not None for p in punkter)


class TestByggDetalj:
    def test_none_naar_kilden_ikke_har_aksjen(self):
        assert bygg_detalj(EQNR, MinneKilde({}), KORT) is None

    def test_sjekkene_kommer_med_navn_verdi_og_maaling(self):
        kilde = MinneKilde({"EQNR": serie([100.0] * 5 + [130.0])})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert len(detalj.sjekker) == 3
        assert [s.navn for s in detalj.sjekker] == ["Trend", "Bevegelse", "Interesse"]
        for sjekk in detalj.sjekker:
            assert sjekk.maaling, "maalingen bak fortegnet skal vaere med"

    def test_styrken_er_summen_av_bidragsyterne(self):
        """Det brukeren skal kunne etterproeve: hvorfor 2 og ikke 1."""
        kilde = MinneKilde(
            {"EQNR": serie([100.0, 90.0, 110.0, 95.0, 105.0, 160.0], [1, 1, 1, 1, 1, 9999])}
        )

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert detalj.styrke == len(detalj.bidragsytere)
        assert all(s.verdi != 0 for s in detalj.bidragsytere)

    def test_sjekker_uten_utslag_vises_likevel(self):
        """Alle tre skal staa der. En sjekk som ga 0 er ogsaa en forklaring."""
        kilde = MinneKilde({"EQNR": serie([100.0] * 6)})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert len(detalj.sjekker) == 3
        assert len(detalj.bidragsytere) <= 3

    def test_fortegn_vises_med_plusstegn(self):
        kilde = MinneKilde({"EQNR": serie([100.0] * 5 + [130.0])})
        detalj = bygg_detalj(EQNR, kilde, KORT)

        fortegn = {s.fortegn for s in detalj.sjekker}
        assert fortegn <= {"+1", "0", "-1"}

    def test_for_kort_serie_gir_detalj_uten_signal(self):
        kilde = MinneKilde({"EQNR": serie([100.0, 101.0])})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert detalj is not None
        assert detalj.styrke is None
        assert detalj.sjekker == ()
        assert detalj.retning.tekst == "Ukjent"
        assert "Trenger" in detalj.mangler

    def test_grafen_finnes_selv_uten_signal(self):
        """Kursen kan tegnes selv om snittet ikke kan regnes."""
        detalj = bygg_detalj(EQNR, MinneKilde({"EQNR": serie([100.0, 101.0])}), KORT)

        assert len(detalj.punkter) == 2
        assert detalj.har_ma50 is False


class TestFinnAksje:
    def test_finner_paa_symbol(self):
        assert finn_aksje("EQNR", AKSJEUNIVERS).navn == "Equinor"

    def test_taaler_smaa_bokstaver_og_mellomrom(self):
        assert finn_aksje("  dnb ", AKSJEUNIVERS).symbol == "DNB"

    def test_none_for_ukjent_symbol(self):
        assert finn_aksje("FINNESIKKE", AKSJEUNIVERS) is None

    def test_ticker_er_ikke_symbol(self):
        """EQNR.OL er EODHDs form. Ruta skal bruke vaar."""
        assert finn_aksje("EQNR.OL", AKSJEUNIVERS) is None
