"""Tester for aksjedetaljen. Ingen nettverk, ingen filer."""

from datetime import date, datetime, timedelta, timezone

import pytest

from aksjedetalj import (
    GRAFVINDU_DAGER,
    Punkt,
    bygg_detalj,
    bygg_punkter,
    finn_aksje,
    glidende_snitt,
)
from kursdata import AKSJEUNIVERS, Aksje, Kursrad, MinneKurslager
from signalberegning import Parametre

EQNR = Aksje("EQNR", "EQNR.OL", "Equinor", "Energi")
KORT = Parametre(ma_vindu=5, volatilitet_vindu=3, volum_vindu=3)
HENTET = datetime(2026, 9, 21, 15, 40, tzinfo=timezone.utc)


def serie(kurser, volumer=None, start=date(2026, 1, 1), slutt=None):
    """Kursrader med ekte, sammenhengende datoer.

    kurser er den justerte serien. slutt er den ujusterte, og er lik den
    justerte naar testen ikke sier noe annet.
    """
    volumer = volumer or [1000] * len(kurser)
    slutt = slutt or kurser
    return [
        Kursrad(
            dato=start + timedelta(days=i),
            slutt=ujustert,
            justert_slutt=kurs,
            volum=volum,
        )
        for i, (kurs, ujustert, volum) in enumerate(zip(kurser, slutt, volumer))
    ]


def lager(serier: dict[str, list[Kursrad]]) -> MinneKurslager:
    """Et Kursleser med seriene lagt inn, slik hentingen ville gjort det."""
    ut = MinneKurslager()
    for symbol, rader in serier.items():
        ut.erstatt_serie(symbol, rader, HENTET)
    return ut


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
        rader = serie([100.0] * 365, start=date(2025, 9, 21))

        punkter = bygg_punkter(rader, KORT)

        assert len(punkter) < len(rader)
        assert (punkter[-1].dato - punkter[0].dato).days <= GRAFVINDU_DAGER

    def test_kort_serie_klippes_ikke(self):
        rader = serie([100.0] * 10)
        assert len(bygg_punkter(rader, KORT)) == 10

    def test_ma50_beholdes_for_foerste_punkt_i_vinduet(self):
        """Snittet regnes paa HELE serien og klippes etterpaa.

        Regnet vi bare paa vinduet, ville de foerste dagene mistet snittet
        sitt uten grunn - dataene finnes jo.
        """
        rader = serie([100.0] * 300, start=date(2025, 9, 21))

        punkter = bygg_punkter(rader, KORT)

        assert punkter[0].ma50 is not None

    def test_ma50_er_none_naar_historikken_er_for_kort(self):
        punkter = bygg_punkter(serie([100.0, 101.0, 102.0]), KORT)
        assert punkter[0].ma50 is None

    def test_kurs_og_snitt_tegnes_fra_samme_justerte_serie(self):
        """Tegnet vi slutt mot et snitt fra justert_slutt, ville de ligget
        paa hver sin skala - og avstanden ville vaert stoerst for aksjene som
        betaler mest utbytte."""
        rader = serie([100.0] * 10, slutt=[200.0] * 10)  # ujustert dobbelt saa hoey

        punkter = bygg_punkter(rader, KORT)

        assert punkter[-1].kurs == 100.0
        assert punkter[-1].ma50 == pytest.approx(100.0)

    def test_utbyttedag_gir_ikke_hakk_i_grafen(self):
        """Utbyttedagen: slutt faller 6 % siste dag, justert kurs gjoer det
        ikke. Hvert punkt skal ligge paa den justerte kursen."""
        justert = [100.0 + i for i in range(8)]
        slutt = [kurs * 1.06 for kurs in justert[:-1]] + [justert[-1]]

        punkter = bygg_punkter(serie(justert, slutt=slutt), KORT)

        assert [p.kurs for p in punkter] == justert

    def test_punktene_har_date(self):
        punkter = bygg_punkter(serie([100.0, 101.0]), KORT)
        assert [p.dato for p in punkter] == [date(2026, 1, 1), date(2026, 1, 2)]


class TestByggDetalj:
    def test_none_naar_kilden_ikke_har_aksjen(self):
        assert bygg_detalj(EQNR, lager({}), KORT) is None

    def test_sjekkene_kommer_med_navn_verdi_og_maaling(self):
        kilde = lager({"EQNR": serie([100.0] * 5 + [130.0])})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert len(detalj.sjekker) == 3
        assert [s.navn for s in detalj.sjekker] == ["Trend", "Bevegelse", "Interesse"]
        for sjekk in detalj.sjekker:
            assert sjekk.maaling, "maalingen bak fortegnet skal vaere med"

    def test_styrken_er_summen_av_bidragsyterne(self):
        """Det brukeren skal kunne etterproeve: hvorfor 2 og ikke 1."""
        kilde = lager(
            {"EQNR": serie([100.0, 90.0, 110.0, 95.0, 105.0, 160.0], [1, 1, 1, 1, 1, 9999])}
        )

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert detalj.styrke == len(detalj.bidragsytere)
        assert all(s.verdi != 0 for s in detalj.bidragsytere)

    def test_sjekker_uten_utslag_vises_likevel(self):
        """Alle tre skal staa der. En sjekk som ga 0 er ogsaa en forklaring."""
        kilde = lager({"EQNR": serie([100.0] * 6)})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert len(detalj.sjekker) == 3
        assert len(detalj.bidragsytere) <= 3

    def test_fortegn_vises_med_plusstegn(self):
        kilde = lager({"EQNR": serie([100.0] * 5 + [130.0])})
        detalj = bygg_detalj(EQNR, kilde, KORT)

        fortegn = {s.fortegn for s in detalj.sjekker}
        assert fortegn <= {"+1", "0", "-1"}

    def test_for_kort_serie_gir_detalj_uten_signal(self):
        kilde = lager({"EQNR": serie([100.0, 101.0])})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert detalj is not None
        assert detalj.styrke is None
        assert detalj.sjekker == ()
        assert detalj.retning.tekst == "Ukjent"
        assert "Trenger" in detalj.mangler

    def test_utbyttedag_viser_slutt_og_regner_paa_justert(self):
        """Sluttkursen er den aksjen omsettes til. Signal og graf foelger den
        justerte serien, ellers ser utbyttet ut som et kursfall."""
        justert = [100.0, 100.4, 99.8, 100.2, 99.9, 100.1]
        slutt = [kurs * 1.06 for kurs in justert[:-1]] + [justert[-1]]
        kilde = lager({"EQNR": serie(justert, slutt=slutt)})

        detalj = bygg_detalj(EQNR, kilde, KORT)

        assert detalj.sluttkurs == slutt[-1]
        assert detalj.dato == date(2026, 1, 6)
        assert detalj.styrke == 0
        assert [p.kurs for p in detalj.punkter] == justert

    def test_sluttkursen_er_slutt_ikke_justert(self):
        """Den ujusterte kursen er den aksjen faktisk omsettes til."""
        kilde = lager({"EQNR": serie([400.0, 400.0], slutt=[419.0, 419.0])})

        assert bygg_detalj(EQNR, kilde, KORT).sluttkurs == 419.0

    def test_grafen_finnes_selv_uten_signal(self):
        """Kursen kan tegnes selv om snittet ikke kan regnes."""
        detalj = bygg_detalj(EQNR, lager({"EQNR": serie([100.0, 101.0])}), KORT)

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
