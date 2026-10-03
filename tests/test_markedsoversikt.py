"""Tester for markedsoversikten. Ingen nettverk, ingen filer.

Seriene bygges i minnet, saa hver test kan beskrive noeyaktig den situasjonen
den vil proeve. Story 2.2b: oversikten faar en Oversiktspost per aksje og
viser raden i vurdering. post() lager posten med det vurder() gir for
serien, slik hentekommandoen skriver det, saa testene proever det sidene
viser, ikke en omregning.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from kursdata import Aksje, Kursrad
from markedsoversikt import (
    ETTER_I_DAG,
    GRUNNTEKST,
    IKKE_BOERSDAG,
    IKKE_VURDERT,
    RETNINGSVISNING,
    UTENFOR_KALENDEREN,
    bygg_oversikt,
    bygg_rad,
    eldre_enn_nyeste,
    endring_i_prosent,
    norsk_tid,
    sidens_dato,
    sidens_tidsstempel,
    uten_kurser,
)
from oversiktsdata import Oversiktspost
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Parametre, vurder
from tilstand import Art
from vurderingsdata import Grunn, Vurdering

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


# Etter alle testseriene, saa ingen dato er etter i dag.
IDAG = date(2026, 12, 31)

_VURDER = object()


def post(aksje, rader, p=KORT, hentet=HENTET, innhold=_VURDER) -> Oversiktspost:
    """Posten Oversiktsleser ville gitt. innhold er som standard det vurder()
    gir for serien paa nyeste dag, slik hentekommandoen skrev det."""
    if innhold is _VURDER:
        innhold = vurder(rader, rader[-1].dato, p) if rader else None
    return Oversiktspost(
        aksje=aksje,
        nyeste=rader[-1] if rader else None,
        forrige=rader[-2] if len(rader) > 1 else None,
        hentet=hentet if rader else None,
        innhold=innhold,
    )


def lager(serier: dict[str, list[Kursrad]], p=KORT) -> list[Oversiktspost]:
    """Postene for seriene, i rekkefoelgen de er gitt, slik aksje gir dem."""
    return [post(AKSJER[symbol], rader, p) for symbol, rader in serier.items()]


AKSJER = {"EQNR": EQNR, "DNB": DNB}


def boersdager(kurser) -> list[Kursrad]:
    """Kursrader paa boersdager som slutter fredag 02.10.2026, mandag til
    fredag uten helg i mellom naar de er fem eller faerre."""
    start = date(2026, 10, 2) - timedelta(days=len(kurser) - 1)
    return [
        Kursrad(dato=start + timedelta(days=i), slutt=k, justert_slutt=k, volum=1000)
        for i, k in enumerate(kurser)
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
        assert bygg_rad(post(EQNR, []), IDAG) is None

    def test_viser_ujustert_sluttkurs(self):
        rad = bygg_rad(post(EQNR, serie([400.0], slutt=[419.0])), IDAG, KORT)
        assert rad.sluttkurs == 419.0

    def test_dato_er_en_date(self):
        """AD-20: datoen er en kalenderdato hele veien. Malen skriver den."""
        rad = bygg_rad(post(EQNR, serie([100.0, 101.0], fra_dato=17)), IDAG, KORT)
        assert rad.dato == date(2026, 9, 18)

    def test_utbyttedag_foelger_justert_kurs_og_viser_slutt(self):
        """Utbyttedagen gjennom hele raden: slutt faller 6 %, justert kurs
        staar stille. Endring og signal foelger den justerte, sluttkursen er
        slutt."""
        justert = [100.0, 100.4, 99.8, 100.2, 99.9, 100.1]
        slutt = [kurs * 1.06 for kurs in justert[:-1]] + [justert[-1]]

        rad = bygg_rad(post(EQNR, serie(justert, slutt=slutt)), IDAG, KORT)

        assert rad.sluttkurs == slutt[-1]
        assert rad.endring_prosent == pytest.approx((100.1 - 99.9) / 99.9 * 100)
        assert rad.styrke == 0

    def test_kort_serie_gir_rad_uten_signal(self):
        """NFR-03: manglende data for en aksje stopper ikke hovedflyten."""
        rad = bygg_rad(post(EQNR, serie([100.0, 101.0])), IDAG, KORT)

        assert rad is not None
        assert rad.vurdering is None
        assert rad.styrke is None
        assert rad.tekst == "signalet kunne ikke regnes"
        assert rad.retning.tekst == "Ukjent"

    def test_lang_nok_serie_gir_signal(self):
        rad = bygg_rad(post(EQNR, serie([100.0] * 5 + [130.0])), IDAG, KORT)

        assert rad.vurdering is not None
        assert rad.tekst is None
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

        rader = bygg_oversikt(kilde, IDAG, KORT)

        assert rader[0].styrke >= rader[1].styrke

    def test_absolutt_endring_avgjoer_ved_lik_styrke(self):
        """Absolutt, ikke fortegn: et stort fall skal ikke havne bakerst (FR-102).

        EQNR faller 6 %, DNB stiger 3 %. Begge faar styrke 2, saa det er
        endringen som avgjoer. Uten abs ville stigningen (+3) komme foran
        fallet (-6). Fallet er heller ikke foerst alfabetisk, saa en
        andresortering paa navn ville ogsaa feilet.
        """
        stort_fall = serie([100.0] * 5 + [94.0])
        opp = serie([100.0] * 5 + [103.0])
        kilde = lager({"EQNR": stort_fall, "DNB": opp})

        rader = bygg_oversikt(kilde, IDAG, KORT)
        styrker = {r.aksje.symbol: r.styrke for r in rader}

        assert styrker["EQNR"] == styrker["DNB"] == 2, styrker
        assert [r.aksje.symbol for r in rader] == ["EQNR", "DNB"], (
            "ved lik styrke skal stoerst absolutt endring staa foerst"
        )

    def test_rader_uten_signal_sorteres_sist(self):
        kilde = lager(
            {"EQNR": serie([100.0, 101.0]), "DNB": serie([100.0] * 5 + [130.0])}
        )

        rader = bygg_oversikt(kilde, IDAG, KORT)

        assert rader[-1].aksje.symbol == "EQNR"
        assert rader[-1].styrke is None

    def test_rad_uten_vurdering_staar_bak_styrke_0(self):
        """Story 2.2b, FR-102: en rad uten vurdering sorteres sist, ogsaa bak
        styrke 0 med mindre endring. Ville feilet hvis raden uten vurdering
        ble sortert som styrke 0 (M11): da avgjoer endringen, og den er
        stoerst for EQNR."""
        uten = post(EQNR, serie([100.0] * 5 + [130.0]), innhold=None)
        null = post(DNB, serie([100.0] * 6))
        assert null.innhold.styrke == 0

        rader = bygg_oversikt([uten, null], IDAG, KORT)

        assert [r.aksje.symbol for r in rader] == ["DNB", "EQNR"]


class TestByggOversikt:
    def test_aksjer_uten_data_faller_ut_men_resten_staar(self):
        kilde = [post(EQNR, []), post(DNB, serie([100.0] * 6))]

        rader = bygg_oversikt(kilde, IDAG, KORT)

        assert [r.aksje.symbol for r in rader] == ["DNB"]
        assert uten_kurser(kilde) == ["Equinor"]

    def test_tom_kilde_gir_tom_oversikt_uten_aa_kaste(self):
        assert bygg_oversikt([], IDAG, KORT) == []

    def test_hver_rad_har_de_fem_kolonnene_fr_101_krever(self):
        kilde = lager({"EQNR": serie([100.0] * 6)})
        rad = bygg_oversikt(kilde, IDAG, KORT)[0]

        assert rad.aksje.navn
        assert isinstance(rad.sluttkurs, float)
        assert rad.endring_prosent is not None
        assert rad.styrke is not None
        assert rad.retning.tekst


def lager_med_tider(tider: dict[str, datetime]) -> list[Oversiktspost]:
    """Poster der hvert symbol er hentet paa sin egen tid, slik AD-15 gir
    det naar ett symbol feiler og beholder sin gamle serie."""
    return [post(AKSJER[symbol], serie([100.0] * 6), hentet=tid) for symbol, tid in tider.items()]


ELDRE = datetime(2026, 9, 20, 15, 40, tzinfo=timezone.utc)


class TestSistHentet:
    """Story 1.4c, FR-101: hvor gamle dataene er, per symbol."""

    def test_raden_faar_symbolets_egen_tid(self):
        kilde = lager_med_tider({"EQNR": ELDRE, "DNB": HENTET})

        rader = {r.aksje.symbol: r for r in bygg_oversikt(kilde, IDAG, KORT)}

        assert rader["EQNR"].sist_hentet == ELDRE
        assert rader["DNB"].sist_hentet == HENTET

    def test_sidens_tidsstempel_er_det_eldste(self):
        """Det nyeste ville faatt en side med en fersk rad og fjorten
        foreldede til aa se fersk ut."""
        kilde = lager_med_tider({"EQNR": HENTET, "DNB": ELDRE})

        assert sidens_tidsstempel(bygg_oversikt(kilde, IDAG, KORT)) == ELDRE

    def test_alle_like_ferske_gir_den_felles_tiden_og_ingen_egne(self):
        rader = bygg_oversikt(lager_med_tider({"EQNR": HENTET, "DNB": HENTET}), IDAG, KORT)

        assert sidens_tidsstempel(rader) == HENTET
        assert eldre_enn_nyeste(rader) == set()

    def test_bare_den_eldste_raden_viser_sin_egen_tid(self):
        rader = bygg_oversikt(lager_med_tider({"EQNR": ELDRE, "DNB": HENTET}), IDAG, KORT)

        assert eldre_enn_nyeste(rader) == {"EQNR"}

    def test_uten_rader_er_det_ingen_tid(self):
        assert sidens_tidsstempel([]) is None
        assert eldre_enn_nyeste([]) == set()


class TestNorskTid:
    """AD-20: UTC i modellen, Europe/Oslo foerst i visningen."""

    def test_formatet(self):
        tid = datetime(2026, 9, 24, 18, 5, tzinfo=timezone.utc)
        assert norsk_tid(tid) == "2026-09-24 kl. 20.05"

    def test_sommertid_over_midnatt(self):
        """22.30 UTC er 00.30 neste dag i Oslo om sommeren. Datoen skifter."""
        tid = datetime(2026, 9, 24, 22, 30, tzinfo=timezone.utc)
        assert norsk_tid(tid) == "2026-09-25 kl. 00.30"

    def test_vintertid(self):
        """Etter 25.10 er Oslo en time foran UTC, ikke to. En fast +2 timer
        ville gitt 2026-11-17 kl. 00.30 her."""
        tid = datetime(2026, 11, 16, 22, 30, tzinfo=timezone.utc)
        assert norsk_tid(tid) == "2026-11-16 kl. 23.30"


class TestSidensDato:
    """Story 8.0: datoen over tabellen er den eldste blant radene som vises,
    samme prinsipp som sidens tidsstempel (FR-101), og avhenger ikke av
    sorteringen."""

    def _rader(self):
        # EQNR har sterkere signal og sorteres foerst, men DNB har eldre dato.
        kilde = lager({
            "EQNR": serie([100.0] * 5 + [104.0], fra_dato=3),
            "DNB": serie([100.0] * 6, fra_dato=1),
        })
        return bygg_oversikt(kilde, IDAG, KORT)

    def test_radene_i_to_rekkefoelger_gir_samme_dato(self):
        rader = self._rader()
        assert sidens_dato(rader) == sidens_dato(list(reversed(rader)))

    def test_eldre_rad_gir_den_eldre_datoen(self):
        rader = self._rader()
        assert [rad.aksje.symbol for rad in rader] == ["EQNR", "DNB"]
        assert sidens_dato(rader) == date(2026, 9, 6)

    def test_uten_rader_er_none(self):
        assert sidens_dato([]) is None


class TestTilstandene:
    """Story 2.2b, FR-409: siden viser raden i vurdering gjennom tilstand(),
    og regner aldri signalet."""

    def test_styrke_0_er_et_svar_ikke_en_mangel(self):
        """Ville feilet hvis styrke 0 ble vist som «–» (M6)."""
        rad = bygg_rad(post(EQNR, serie([100.0] * 6)), IDAG, KORT)
        assert rad.styrke == 0
        assert rad.tekst is None
        assert rad.retning.tekst == INGEN

    @pytest.mark.parametrize("grunn", list(Grunn))
    def test_rad_med_grunn_viser_grunnen_ikke_styrke_0(self, grunn):
        """Ville feilet hvis en rad med grunn ble vist som styrke 0 (M5)."""
        rad = bygg_rad(post(EQNR, serie([100.0] * 6), innhold=grunn), IDAG, KORT)
        assert rad.tilstand.art is Art.GRUNN
        assert rad.styrke is None
        assert rad.tekst == GRUNNTEKST[grunn]
        assert rad.retning.tekst == "Ukjent"

    def test_tekstene_for_grunnene(self):
        assert GRUNNTEKST == {
            Grunn.SYMBOL_FEILET: "hentingen feilet",
            Grunn.KURS_IKKE_FRA_DAGEN: "ingen kurs fra dagen",
            Grunn.SIGNAL_IKKE_REGNET: "signalet kunne ikke regnes",
        }

    def test_ingen_rad_paa_en_boersdag_er_ikke_vurdert(self):
        """Kurser uten rad, som etter --les-inn. Ville feilet hvis siden
        regnet signalet naar raden mangler (M1): serien er lang nok til aa
        gi et signal med de korte vinduene."""
        rader = boersdager([100.0, 100.0, 100.0, 100.0, 130.0])  # 28.09 til 02.10
        rad = bygg_rad(post(EQNR, rader, innhold=None), IDAG, KORT)
        assert rad.tilstand.art is Art.IKKE_KJOERT
        assert rad.tekst == IKKE_VURDERT
        assert rad.ikke_vurdert
        assert rad.styrke is None

    def test_ingen_rad_paa_en_dag_som_ikke_er_boersdag(self):
        rader = serie([100.0, 101.0], fra_dato=5)  # 05.09 og 06.09, helg
        rad = bygg_rad(post(EQNR, rader, innhold=None), IDAG, KORT)
        assert rad.tilstand.art is Art.IKKE_BOERSDAG
        assert rad.tekst == IKKE_BOERSDAG

    def test_utenfor_boerskalenderen_gir_tekst_ikke_feil(self):
        """Ville feilet hvis UtenforKalenderen ikke ble fanget (M9)."""
        rader = [Kursrad(dato=date(2027, 3, 1), slutt=100.0, justert_slutt=100.0, volum=1)]
        rad = bygg_rad(post(EQNR, rader, innhold=None), date(2027, 3, 2), KORT)
        assert rad.tilstand is None
        assert rad.tekst == UTENFOR_KALENDEREN

    def test_dato_etter_i_dag_gir_tekst_ikke_feil(self):
        rader = serie([100.0, 101.0], fra_dato=17)
        rad = bygg_rad(post(EQNR, rader), date(2026, 9, 1), KORT)
        assert rad.tilstand is None
        assert rad.tekst == ETTER_I_DAG
        assert rad.styrke is None

    def test_vurderingen_fra_raden_ikke_fra_serien(self):
        """Raden avgjoer, ogsaa naar serien ville gitt noe annet. Her en rad
        med styrke 3 paa en flat serie, som ville gitt styrke 0."""
        lagret = Vurdering(
            styrke=3, retning=NEGATIV, trend=-1, bevegelse=-1, interesse=-1,
            slutt=100.0, justert_slutt=100.0, trend_avvik=-0.05,
            dagens_endring=-0.04, standardavvik=0.01, volumforhold=0.2,
        )
        rad = bygg_rad(post(EQNR, serie([100.0] * 6), innhold=lagret), IDAG, KORT)
        assert rad.styrke == 3
        assert rad.retning.tekst == NEGATIV
        assert rad.skiller_seg_ut

    def test_markedsoversikten_regner_ikke_signalet(self):
        """Story 2.2b: en vei til tallet. Ville feilet hvis beregn_signal
        eller vurder ble tatt inn igjen (M1)."""
        import markedsoversikt

        assert not hasattr(markedsoversikt, "beregn_signal")
        assert not hasattr(markedsoversikt, "vurder")
