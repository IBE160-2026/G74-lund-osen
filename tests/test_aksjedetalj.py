"""Tester for aksjedetaljen. Ingen nettverk, ingen filer.

Story 2.2b: detaljen faar posten fra Oversiktsleser og serien fra kurs.
detalj() lager posten med det vurder() gir for serien, slik hentekommandoen
skriver det, saa testene proever det siden viser, ikke en omregning.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from aksjedetalj import (
    GRAFVINDU_DAGER,
    bygg_detalj,
    bygg_punkter,
    glidende_snitt,
    normaliser_symbol,
)
from kursdata import Aksje, Kursrad
from oversiktsdata import Oversiktspost
from signalberegning import Parametre, vurder
from tilstand import Art
from vurderingsdata import Grunn, Vurdering

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


IDAG = date(2026, 12, 31)
_VURDER = object()


def detalj(rader, p=KORT, innhold=_VURDER, idag=IDAG):
    """Detaljen for EQNR med serien rader. innhold er som standard det
    vurder() gir paa nyeste dag, slik hentekommandoen skrev det."""
    if innhold is _VURDER:
        innhold = vurder(rader, rader[-1].dato, p) if rader else None
    post = Oversiktspost(
        aksje=EQNR,
        nyeste=rader[-1] if rader else None,
        forrige=rader[-2] if len(rader) > 1 else None,
        hentet=HENTET if rader else None,
        innhold=innhold,
    )
    return bygg_detalj(post, rader, idag, p)


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
        assert detalj([]) is None

    def test_sjekkene_kommer_med_navn_verdi_og_maaling(self):
        d = detalj(serie([100.0] * 5 + [130.0]))

        assert len(d.sjekker) == 3
        assert [s.navn for s in d.sjekker] == ["Trend", "Bevegelse", "Interesse"]
        for sjekk in d.sjekker:
            assert sjekk.maaling, "maalingen bak fortegnet skal vaere med"

    def test_interesse_uten_medianvolum_viser_strek_og_grunnen(self):
        """Story 2.1c, NFR-08: medianvolumet 0 gir «–» med grunnen, aldri 0.
        Vinduet er KORT.volum_vindu, 3, ikke 20 skrevet inn for haand."""
        d = detalj(serie([100.0] * 5 + [130.0], [0] * 5 + [1000]))

        interesse = next(s for s in d.sjekker if s.navn == "Interesse")
        assert interesse.maaling == "–, medianvolumet de 3 dagene før er 0"
        assert interesse.verdi == 0

    def test_styrken_er_summen_av_bidragsyterne(self):
        """Det brukeren skal kunne etterproeve: hvorfor 2 og ikke 1."""
        d = detalj(serie([100.0, 90.0, 110.0, 95.0, 105.0, 160.0], [1, 1, 1, 1, 1, 9999]))

        assert d.styrke == len(d.bidragsytere)
        assert all(s.verdi != 0 for s in d.bidragsytere)

    def test_sjekker_uten_utslag_vises_likevel(self):
        """Alle tre skal staa der. En sjekk som ga 0 er ogsaa en forklaring."""
        d = detalj(serie([100.0] * 6))

        assert len(d.sjekker) == 3
        assert len(d.bidragsytere) <= 3

    def test_fortegn_vises_med_plusstegn(self):
        d = detalj(serie([100.0] * 5 + [130.0]))

        fortegn = {s.fortegn for s in d.sjekker}
        assert fortegn <= {"+1", "0", "-1"}

    def test_for_kort_serie_gir_detalj_uten_signal(self):
        d = detalj(serie([100.0, 101.0]))

        assert d is not None
        assert d.styrke is None
        assert d.sjekker == ()
        assert d.retning.tekst == "Ukjent"
        assert d.for_kort_serie
        assert (d.noedvendige_dager, d.antall_dager) == (6, 2)

    def test_lang_serie_med_signal_ikke_regnet_er_ikke_for_kort(self):
        """Raadet 03.10: vurder() gir signal_ikke_regnet ogsaa naar porten
        ikke godtar tallene paa en serie som er lang nok. Da skal siden ikke
        si antallet dager. Ville feilet hvis lengden ikke ble sjekket (M12)."""
        d = detalj(serie([100.0] * 10), innhold=Grunn.SIGNAL_IKKE_REGNET)

        assert d.tekst == "signalet kunne ikke regnes"
        assert not d.for_kort_serie
        assert d.sjekker == ()

    def test_utbyttedag_viser_slutt_og_regner_paa_justert(self):
        """Sluttkursen er den aksjen omsettes til. Signal og graf foelger den
        justerte serien, ellers ser utbyttet ut som et kursfall."""
        justert = [100.0, 100.4, 99.8, 100.2, 99.9, 100.1]
        slutt = [kurs * 1.06 for kurs in justert[:-1]] + [justert[-1]]
        d = detalj(serie(justert, slutt=slutt))

        assert d.sluttkurs == slutt[-1]
        assert d.dato == date(2026, 1, 6)
        assert d.styrke == 0
        assert [p.kurs for p in d.punkter] == justert

    def test_sluttkursen_er_slutt_ikke_justert(self):
        """Den ujusterte kursen er den aksjen faktisk omsettes til."""
        assert detalj(serie([400.0, 400.0], slutt=[419.0, 419.0])).sluttkurs == 419.0

    def test_grafen_finnes_selv_uten_signal(self):
        """Kursen kan tegnes selv om snittet ikke kan regnes."""
        d = detalj(serie([100.0, 101.0]))

        assert len(d.punkter) == 2
        assert all(p.ma50 is None for p in d.punkter)


class TestNormaliserSymbol:
    """Story 2.2b: aksjen slaas opp i aksje i basen. Ruta godtar smaa
    bokstaver og mellomrom, som foer."""

    def test_taaler_smaa_bokstaver_og_mellomrom(self):
        assert normaliser_symbol("  dnb ") == "DNB"

    def test_ticker_forblir_ticker(self):
        """EQNR.OL er EODHDs form. Den blir ikke et symbol, saa oppslaget i
        aksje gir ingenting."""
        assert normaliser_symbol("eqnr.ol") == "EQNR.OL"


class TestVurderingenIDetaljen:
    """Story 2.2b, FR-706, FR-204: sjekkene og maalingene kommer fra raden."""

    LAGRET = Vurdering(
        styrke=3, retning="Blandet", trend=1, bevegelse=-1, interesse=-1,
        slutt=101.0, justert_slutt=101.0, trend_avvik=0.031,
        dagens_endring=-0.035, standardavvik=0.011, volumforhold=4.95,
    )

    def test_sjekkene_og_maalingene_fra_raden_ikke_fra_serien(self):
        """Eksempelet i FR-706. En flat serie ville gitt tre nuller. Ville
        feilet hvis detaljen forklarte med et signal regnet av serien (M7)."""
        NB = "\u00a0"
        d = detalj(serie([100.0] * 6), innhold=self.LAGRET)

        assert [(s.navn, s.verdi) for s in d.sjekker] == [
            ("Trend", 1), ("Bevegelse", -1), ("Interesse", -1),
        ]
        maalinger = [s.maaling for s in d.sjekker]
        assert maalinger[0] == f"+3,1{NB}% mot MA5"
        assert maalinger[1].startswith(f"-3,5{NB}% mot 1,1{NB}%")
        assert maalinger[2] == "volum 4,95 × medianen"
        assert d.styrke == 3
        assert d.retning.tekst == "Blandet"

    @pytest.mark.parametrize("grunn", [Grunn.SYMBOL_FEILET, Grunn.KURS_IKKE_FRA_DAGEN])
    def test_rad_med_grunn_gir_graf_og_tekst_uten_sjekker(self, grunn):
        d = detalj(serie([100.0] * 6), innhold=grunn)

        assert d.tilstand.art is Art.GRUNN
        assert d.sjekker == ()
        assert d.styrke is None
        assert d.tekst in ("hentingen feilet", "ingen kurs fra dagen")
        assert len(d.punkter) == 6

    def test_ingen_rad_gir_ikke_vurdert(self):
        # 2026-01-05 til 2026-01-09, mandag til fredag.
        d = detalj(serie([100.0] * 5, start=date(2026, 1, 5)), innhold=None)

        assert d.tilstand.art is Art.IKKE_KJOERT
        assert d.tekst == "ikke vurdert"
        assert d.sjekker == ()

    def test_aksjedetaljen_regner_ikke_signalet(self):
        """En vei til tallet. Ville feilet hvis beregn_signal eller vurder
        ble tatt inn igjen (M7)."""
        import aksjedetalj

        assert not hasattr(aksjedetalj, "beregn_signal")
        assert not hasattr(aksjedetalj, "vurder")
