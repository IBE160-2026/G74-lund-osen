"""Tester for markedsoversikten. Ingen nettverk, ingen filer.

Seriene bygges i minnet, saa hver test kan beskrive noeyaktig den situasjonen
den vil proeve.
"""

import pytest

from kursdata import Aksje, MinneKilde
from markedsoversikt import (
    RETNINGSVISNING,
    Rad,
    bygg_oversikt,
    bygg_rad,
    endring_i_prosent,
)
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Parametre

EQNR = Aksje("EQNR", "EQNR.OL", "Equinor", "Energi")
DNB = Aksje("DNB", "DNB.OL", "DNB Bank", "Finans")

# Korte vinduer, slik signalberegningstestene gjoer det. Da trengs 6 rader.
KORT = Parametre(ma_vindu=5, volatilitet_vindu=3, volum_vindu=3)


def serie(kurser, volumer=None, fra_dato=1):
    """Kursrader med stigende datoer. Volum er likt naar det ikke betyr noe."""
    volumer = volumer or [1000] * len(kurser)
    return [
        {
            "date": f"2026-09-{fra_dato + i:02d}",
            "close": kurs,
            "adjusted_close": kurs,
            "volume": volum,
        }
        for i, (kurs, volum) in enumerate(zip(kurser, volumer))
    ]


class TestEndringIProsent:
    def test_regner_fra_forrige_dag(self):
        assert endring_i_prosent(serie([100.0, 110.0])) == pytest.approx(10.0)

    def test_er_none_naar_det_bare_finnes_en_dag(self):
        assert endring_i_prosent(serie([100.0])) is None

    def test_bruker_justert_kurs_ikke_sluttkurs(self):
        """Utbyttedagen: close faller, justert kurs gjoer det ikke.

        Prosenten skal foelge den justerte serien, ellers ser et ordinaert
        utbytte ut som et kursfall.
        """
        rader = [
            {"date": "2026-09-17", "close": 106.0, "adjusted_close": 100.0, "volume": 1},
            {"date": "2026-09-18", "close": 100.0, "adjusted_close": 100.0, "volume": 1},
        ]
        assert endring_i_prosent(rader) == pytest.approx(0.0)

    def test_faller_tilbake_til_close_naar_justert_mangler(self):
        rader = [
            {"date": "2026-09-17", "close": 100.0, "volume": 1},
            {"date": "2026-09-18", "close": 110.0, "volume": 1},
        ]
        assert endring_i_prosent(rader) == pytest.approx(10.0)


class TestByggRad:
    def test_gir_none_uten_kursrader(self):
        assert bygg_rad(EQNR, []) is None

    def test_viser_ujustert_sluttkurs(self):
        rader = [
            {"date": "2026-09-18", "close": 419.0, "adjusted_close": 400.0, "volume": 1}
        ]
        rad = bygg_rad(EQNR, rader, KORT)
        assert rad.sluttkurs == 419.0

    def test_kort_serie_gir_rad_uten_signal(self):
        """NFR-03: manglende data for en aksje stopper ikke hovedflyten."""
        rad = bygg_rad(EQNR, serie([100.0, 101.0]), KORT)

        assert rad is not None
        assert rad.signal is None
        assert rad.styrke is None
        assert "Trenger" in rad.mangler
        assert rad.retning.tekst == "Ukjent"

    def test_lang_nok_serie_gir_signal(self):
        rad = bygg_rad(EQNR, serie([100.0] * 5 + [130.0]), KORT)

        assert rad.signal is not None
        assert rad.mangler is None
        assert rad.styrke in (0, 1, 2, 3)


class TestRetningsvisning:
    def test_alle_fire_retninger_har_visning(self):
        for retning in (POSITIV, NEGATIV, BLANDET, INGEN):
            assert retning in RETNINGSVISNING

    @pytest.mark.parametrize(
        "retning,symbol",
        [(POSITIV, "↑"), (NEGATIV, "↓"), (BLANDET, "↔"), (INGEN, "–")],
    )
    def test_symbolet_foelger_fr_103(self, retning, symbol):
        assert RETNINGSVISNING[retning].symbol == symbol

    @pytest.mark.parametrize("retning", [POSITIV, NEGATIV, BLANDET, INGEN])
    def test_teksten_er_fr_704s_ord_uendret(self, retning):
        """Visningen oversetter ikke. Staar det Positiv i modellen, staar det
        Positiv paa skjermen."""
        assert RETNINGSVISNING[retning].tekst == retning

    def test_ingen_retning_vises_som_opp_eller_ned(self):
        """Opp/Ned inviterer til aa lese pilen som kursbevegelse, og briefen
        slaar fast at signalet ikke er en anbefaling om kjoep eller salg."""
        tekster = {v.tekst for v in RETNINGSVISNING.values()}
        assert "Opp" not in tekster
        assert "Ned" not in tekster

    def test_de_tre_kanalene_er_forskjellige_per_retning(self):
        """Tekst, symbol og klasse skal skille retningene hver for seg.

        Faller to retninger sammen i en av kanalene, er den kanalen ikke
        lenger en av de tre uavhengige i FR-103.
        """
        for felt in ("tekst", "symbol", "klasse"):
            verdier = [getattr(v, felt) for v in RETNINGSVISNING.values()]
            assert len(set(verdier)) == len(verdier), felt


class TestSortering:
    def test_sterkest_signal_foerst(self):
        rolig = serie([100.0] * 6)
        urolig = serie([100.0, 90.0, 110.0, 95.0, 105.0, 140.0], [1, 1, 1, 1, 1, 9999])
        kilde = MinneKilde({"EQNR": rolig, "DNB": urolig})

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)

        assert rader[0].styrke >= rader[1].styrke

    def test_absolutt_endring_avgjoer_ved_lik_styrke(self):
        """Absolutt, ikke fortegn: et stort fall skal ikke havne bakerst."""
        lite = serie([100.0] * 5 + [100.5])
        stort_fall = serie([100.0] * 5 + [94.0])
        kilde = MinneKilde({"EQNR": lite, "DNB": stort_fall})

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)
        med_lik_styrke = {r.aksje.symbol: r for r in rader}
        if med_lik_styrke["EQNR"].styrke == med_lik_styrke["DNB"].styrke:
            assert rader[0].aksje.symbol == "DNB"

    def test_rader_uten_signal_sorteres_sist(self):
        kilde = MinneKilde(
            {"EQNR": serie([100.0, 101.0]), "DNB": serie([100.0] * 5 + [130.0])}
        )

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)

        assert rader[-1].aksje.symbol == "EQNR"
        assert rader[-1].styrke is None


class TestByggOversikt:
    def test_aksjer_uten_data_faller_ut_men_resten_staar(self):
        kilde = MinneKilde({"DNB": serie([100.0] * 6)})

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)

        assert [r.aksje.symbol for r in rader] == ["DNB"]

    def test_tom_kilde_gir_tom_oversikt_uten_aa_kaste(self):
        assert bygg_oversikt(MinneKilde({}), (EQNR, DNB), KORT) == []

    def test_hver_rad_har_de_fem_kolonnene_fr_101_krever(self):
        kilde = MinneKilde({"EQNR": serie([100.0] * 6)})
        rad = bygg_oversikt(kilde, (EQNR,), KORT)[0]

        assert rad.aksje.navn
        assert isinstance(rad.sluttkurs, float)
        assert rad.endring_prosent is not None
        assert rad.styrke is not None
        assert rad.retning.tekst
