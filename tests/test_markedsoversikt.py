"""Tester for markedsoversikten. Ingen nettverk, ingen filer.

Seriene bygges i minnet, saa hver test kan beskrive noeyaktig den situasjonen
den vil proeve.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from kursdata import Aksje, Kursrad, MinneKurslager
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


HENTET = datetime(2026, 9, 21, 15, 40, tzinfo=timezone.utc)


def serie(kurser, volumer=None, fra_dato=1, slutt=None):
    """Kursrader med stigende datoer. Volum er likt naar det ikke betyr noe.

    kurser er den justerte serien. slutt er den ujusterte, og er lik den
    justerte naar testen ikke sier noe annet.
    """
    volumer = volumer or [1000] * len(kurser)
    slutt = slutt or kurser
    return [
        Kursrad(
            dato=date(2026, 9, fra_dato) + timedelta(days=i),
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
        rader = serie([100.0, 100.0], slutt=[106.0, 100.0])
        assert endring_i_prosent(rader) == pytest.approx(0.0)

    def test_justert_stigning_vises_selv_om_slutt_staar_stille(self):
        """Motsatt vei: slutt er lik begge dager, justert kurs stiger 10 %.
        Prosenten skal vaere 10, ikke 0. Slutt ligger over begge de justerte
        kursene, saa baade fra- og til-kursen maa vaere den justerte."""
        rader = serie([100.0, 110.0], slutt=[120.0, 120.0])
        assert endring_i_prosent(rader) == pytest.approx(10.0)


class TestByggRad:
    def test_gir_none_uten_kursrader(self):
        assert bygg_rad(EQNR, []) is None

    def test_viser_ujustert_sluttkurs(self):
        rad = bygg_rad(EQNR, serie([400.0], slutt=[419.0]), KORT)
        assert rad.sluttkurs == 419.0

    def test_dato_er_en_date(self):
        """AD-20: datoen er en kalenderdato hele veien. Malen skriver den."""
        rad = bygg_rad(EQNR, serie([100.0, 101.0], fra_dato=17), KORT)
        assert rad.dato == date(2026, 9, 18)

    def test_utbyttedag_foelger_justert_kurs_og_viser_slutt(self):
        """Utbyttedagen gjennom hele raden: slutt faller 6 %, justert kurs
        staar stille. Endring og signal foelger den justerte, sluttkursen er
        slutt."""
        justert = [100.0, 100.4, 99.8, 100.2, 99.9, 100.1]
        slutt = [kurs * 1.06 for kurs in justert[:-1]] + [justert[-1]]

        rad = bygg_rad(EQNR, serie(justert, slutt=slutt), KORT)

        assert rad.sluttkurs == slutt[-1]
        assert rad.endring_prosent == pytest.approx((100.1 - 99.9) / 99.9 * 100)
        assert rad.styrke == 0

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
        kilde = lager({"EQNR": rolig, "DNB": urolig})

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)

        assert rader[0].styrke >= rader[1].styrke

    def test_absolutt_endring_avgjoer_ved_lik_styrke(self):
        """Absolutt, ikke fortegn: et stort fall skal ikke havne bakerst."""
        lite = serie([100.0] * 5 + [100.5])
        stort_fall = serie([100.0] * 5 + [94.0])
        kilde = lager({"EQNR": lite, "DNB": stort_fall})

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)
        med_lik_styrke = {r.aksje.symbol: r for r in rader}
        if med_lik_styrke["EQNR"].styrke == med_lik_styrke["DNB"].styrke:
            assert rader[0].aksje.symbol == "DNB"

    def test_rader_uten_signal_sorteres_sist(self):
        kilde = lager(
            {"EQNR": serie([100.0, 101.0]), "DNB": serie([100.0] * 5 + [130.0])}
        )

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)

        assert rader[-1].aksje.symbol == "EQNR"
        assert rader[-1].styrke is None


class TestByggOversikt:
    def test_aksjer_uten_data_faller_ut_men_resten_staar(self):
        kilde = lager({"DNB": serie([100.0] * 6)})

        rader = bygg_oversikt(kilde, (EQNR, DNB), KORT)

        assert [r.aksje.symbol for r in rader] == ["DNB"]

    def test_tom_kilde_gir_tom_oversikt_uten_aa_kaste(self):
        assert bygg_oversikt(lager({}), (EQNR, DNB), KORT) == []

    def test_hver_rad_har_de_fem_kolonnene_fr_101_krever(self):
        kilde = lager({"EQNR": serie([100.0] * 6)})
        rad = bygg_oversikt(kilde, (EQNR,), KORT)[0]

        assert rad.aksje.navn
        assert isinstance(rad.sluttkurs, float)
        assert rad.endring_prosent is not None
        assert rad.styrke is not None
        assert rad.retning.tekst
