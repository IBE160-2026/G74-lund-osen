"""Story 10.1: grunnlaget som sendes - bare utledede verdier (betingelse 4,
prd.md §4.6, merknaden 04.10 i 4.1, svar 10 kl. 15:53)."""

from collections.abc import Mapping
from datetime import date, timedelta

import pytest

from ki_grunnlag import RETNINGER, SJEKKENE, UTENFOR_MAALINGEN, ki_grunnlag
from kursdata import Kursrad
from signalberegning import Signal, Sjekk, beregn_signal, vurder
from vurderingsdata import Vurdering

NOEKLENE = {*SJEKKENE, "styrke", "retning"}


def _serie(antall: int = 60) -> list[Kursrad]:
    """En serie der hver kurs og hvert volum er et eget tall med desimaler,
    saa ingen av dem kan forveksles med et fortegn eller en styrke."""
    rader = []
    kurs = 101.37
    for nummer in range(antall):
        kurs = round(kurs * (1.0123 if nummer % 3 else 0.9917), 4)
        rader.append(
            Kursrad(
                dato=date(2026, 7, 1) + timedelta(days=nummer),
                slutt=round(kurs * 1.0311, 4),
                justert_slutt=kurs,
                volum=1_000_003 + nummer * 7_919 + (900_000 if nummer == antall - 1 else 0),
            )
        )
    return rader


def _alle_tall(verdi):
    if isinstance(verdi, Mapping):
        for v in verdi.values():
            yield from _alle_tall(v)
    elif isinstance(verdi, (list, tuple)):
        for v in verdi:
            yield from _alle_tall(v)
    else:
        yield verdi


def _vurderingen(rader):
    vurdering = vurder(rader, rader[-1].dato)
    assert isinstance(vurdering, Vurdering), vurdering
    return vurdering


class TestBareUtledet:
    def test_signalet_gir_bare_fortegn_styrke_og_retning(self):
        signal = beregn_signal(_serie())
        grunnlag = ki_grunnlag(signal, utenfor_maalingen=False)
        assert set(grunnlag) == NOEKLENE
        assert grunnlag["styrke"] == signal.styrke
        assert grunnlag["retning"] == signal.retning
        assert [grunnlag[navn] for navn in SJEKKENE] == [sjekk.verdi for sjekk in signal.sjekker]

    def test_vurderingen_gir_det_samme(self):
        rader = _serie()
        assert ki_grunnlag(_vurderingen(rader), utenfor_maalingen=False) == ki_grunnlag(
            beregn_signal(rader), utenfor_maalingen=False
        )

    @pytest.mark.parametrize("hvor", ["signal", "vurdering"])
    def test_ingen_desimaltall(self, hvor):
        """Ville feilet hvis grunnlaget hadde en prosent eller et
        forholdstall (beslutningen 04.10)."""
        rader = _serie()
        kilde = beregn_signal(rader) if hvor == "signal" else _vurderingen(rader)
        for verdi in _alle_tall(ki_grunnlag(kilde, utenfor_maalingen=False)):
            assert not isinstance(verdi, float), verdi
            assert isinstance(verdi, (int, str)), verdi

    def test_ingen_kurs_volum_eller_maaling(self):
        """Ville feilet hvis grunnlaget inneholdt dagens volum eller en kurs.
        Da sendes et raatt datapunkt fra EODHD til en tredjepart."""
        rader = _serie()
        vurdering = _vurderingen(rader)
        signal = beregn_signal(rader)
        forbudt = {r.slutt for r in rader} | {r.justert_slutt for r in rader} | {r.volum for r in rader}
        forbudt |= {
            vurdering.trend_avvik,
            vurdering.dagens_endring,
            vurdering.standardavvik,
            vurdering.volumforhold,
            vurdering.slutt,
            vurdering.justert_slutt,
        }
        forbudt |= {s.maaling for s in signal.sjekker} | {s.grense for s in signal.sjekker}
        forbudt |= {round(v * 100, d) for v in (vurdering.dagens_endring, vurdering.trend_avvik) for d in (1, 2)}
        forbudt.discard(None)
        # Serien er laget slik at ingen av de forbudte verdiene er et fortegn
        # eller en styrke.
        assert not forbudt & {-1, 0, 1, 2, 3}
        for kilde in (signal, vurdering):
            for verdi in _alle_tall(ki_grunnlag(kilde, utenfor_maalingen=False)):
                assert verdi not in forbudt, verdi
                if isinstance(verdi, str):
                    assert not any(tegn.isdigit() for tegn in verdi), verdi
                else:
                    assert verdi in (-1, 0, 1, 2, 3), verdi

    def test_teksten_er_fra_den_lukkede_lista(self):
        grunnlag = ki_grunnlag(beregn_signal(_serie()), utenfor_maalingen=False)
        assert grunnlag["retning"] in RETNINGER

    def test_ingen_antall(self):
        """Svar 10 kl. 15:53: «antall» gjelder dagsteksten i 10.6."""
        grunnlag = ki_grunnlag(beregn_signal(_serie()), utenfor_maalingen=False)
        assert not any("antall" in noekkel for noekkel in grunnlag)


class TestUtenforMaalingen:
    def test_merket_og_de_samme_verdiene(self):
        """FR-412, endringsforslaget 08.10: samme utledede verdier, og merket."""
        signal = beregn_signal(_serie())
        vanlig = ki_grunnlag(signal, utenfor_maalingen=False)
        utenfor = ki_grunnlag(signal, utenfor_maalingen=True)
        assert utenfor == {**vanlig, "merke": UTENFOR_MAALINGEN}
        assert "merke" not in vanlig

    def test_bare_true_eller_false(self):
        with pytest.raises(TypeError):
            ki_grunnlag(beregn_signal(_serie()), utenfor_maalingen="ja")


def _signal(trend, bevegelse, interesse, styrke=None, retning=None, navn=("Trend", "Bevegelse", "Interesse")):
    sjekker = tuple(Sjekk(n, v, "") for n, v in zip(navn, (trend, bevegelse, interesse)))
    if styrke is None:
        styrke = sum(abs(v) for v in (trend, bevegelse, interesse))
    return Signal(styrke=styrke, retning=retning or "Blandet", sjekker=sjekker, skiller_seg_ut=False)


def _vurdering(trend, bevegelse, interesse, retning):
    return Vurdering(
        styrke=abs(trend) + abs(bevegelse) + abs(interesse),
        retning=retning,
        trend=trend,
        bevegelse=bevegelse,
        interesse=interesse,
        slutt=101.37,
        justert_slutt=99.11,
        trend_avvik=0.0123,
        dagens_endring=-0.0045,
        standardavvik=0.0167,
        volumforhold=1.53,
    )


class TestFortegnene:
    """Gjennomgangen (VG1): ulike fortegn paa de tre sjekkene."""

    def test_signal_med_ulike_fortegn(self):
        assert ki_grunnlag(_signal(-1, 0, 1), utenfor_maalingen=False) == {
            "trend": -1,
            "bevegelse": 0,
            "interesse": 1,
            "styrke": 2,
            "retning": "Blandet",
        }

    @pytest.mark.parametrize(
        "fortegn, retning",
        [
            ((-1, 0, 1), "Blandet"),
            ((0, -1, 0), "Negativ"),
            ((1, 0, 0), "Positiv"),
            ((0, 0, 0), "Ingen"),
        ],
    )
    def test_vurdering_med_ulike_fortegn(self, fortegn, retning):
        grunnlag = ki_grunnlag(_vurdering(*fortegn, retning), utenfor_maalingen=False)
        assert [grunnlag[s] for s in SJEKKENE] == list(fortegn)
        assert grunnlag["retning"] == retning
        assert grunnlag["styrke"] == sum(abs(v) for v in fortegn)

    def test_grunnlaget_kan_ikke_endres(self):
        """Gjennomgangen (BH7): ingen kan legge til et felt etter kontrollen."""
        grunnlag = ki_grunnlag(_signal(1, 0, 0, retning="Positiv"), utenfor_maalingen=False)
        with pytest.raises(TypeError):
            grunnlag["kurs"] = 101.37


class TestKontrollen:
    @pytest.mark.parametrize("verdi", [2, -2, 0.9, True, "1", None])
    def test_fortegn_som_ikke_er_heltallet_minus_1_0_eller_1(self, verdi):
        """Gjennomgangen (BH1, BH2, ECH): ingenting rundes av til noe gyldig."""
        with pytest.raises(ValueError):
            ki_grunnlag(_signal(verdi, 0, 0, styrke=1, retning="Positiv"), utenfor_maalingen=False)

    @pytest.mark.parametrize("styrke", [4, -1, 2.5, 2.0, True, "2"])
    def test_styrke_som_ikke_er_et_heltall_fra_0_til_3(self, styrke):
        with pytest.raises(ValueError):
            ki_grunnlag(_signal(1, 1, 0, styrke=styrke, retning="Positiv"), utenfor_maalingen=False)

    @pytest.mark.parametrize("retning", ["Kurs 123,45", "positiv", "", None])
    def test_retning_utenfor_den_lukkede_lista(self, retning):
        """Gjennomgangen (VG2): retning er den eneste teksten som sendes."""
        signal = Signal(styrke=1, retning=retning, sjekker=_signal(1, 0, 0).sjekker, skiller_seg_ut=False)
        # Kontrollen av den lukkede lista stopper den, foer samsvaret med
        # sjekkene sjekkes (mutant GR2).
        with pytest.raises(ValueError, match="retning maa vaere en av"):
            ki_grunnlag(signal, utenfor_maalingen=False)

    @pytest.mark.parametrize(
        "navn",
        [
            ("Trend", "Trend", "Interesse"),
            ("TREND", "Bevegelse", "Interesse"),
            ("Interesse", "Bevegelse", "Trend"),
        ],
    )
    def test_sjekkene_maa_vaere_de_tre_en_av_hver(self, navn):
        """Gjennomgangen (BH5, ECH): et dobbelt navn ga stille én av verdiene."""
        with pytest.raises(ValueError):
            ki_grunnlag(_signal(1, 0, -1, navn=navn), utenfor_maalingen=False)

    def test_fire_sjekker_avvises(self):
        sjekker = _signal(1, 0, 0).sjekker + (Sjekk("Volum", 1, ""),)
        with pytest.raises(ValueError):
            ki_grunnlag(
                Signal(styrke=2, retning="Positiv", sjekker=sjekker, skiller_seg_ut=False), utenfor_maalingen=False
            )

    @pytest.mark.parametrize("styrke, retning", [(3, "Blandet"), (2, "Positiv")])
    def test_et_signal_som_ikke_stemmer_med_sjekkene(self, styrke, retning):
        """Gjennomgangen (ECH): et Signal kontrolleres ikke naar det lages."""
        with pytest.raises(ValueError):
            ki_grunnlag(_signal(1, 0, -1, styrke=styrke, retning=retning), utenfor_maalingen=False)

    def test_feilen_nevner_ikke_verdien(self):
        """Gjennomgangen (BH9): en raa verdi skal ikke havne i en logg."""
        with pytest.raises(ValueError) as feil:
            ki_grunnlag(_signal(101.37, 0, 0, styrke=1, retning="Positiv"), utenfor_maalingen=False)
        assert "101" not in str(feil.value)

    def test_merket_maa_oppgis(self):
        """Gjennomgangen (BH6): kalleren kan ikke glemme merket."""
        with pytest.raises(TypeError):
            ki_grunnlag(_signal(1, 0, 0, retning="Positiv"))

    def test_bare_signal_eller_vurdering(self):
        with pytest.raises(TypeError):
            ki_grunnlag({"trend": 1}, utenfor_maalingen=False)

    def test_ukjent_sjekk_avvises(self):
        sjekker = (Sjekk("Trend", 1, ""), Sjekk("Bevegelse", 0, ""), Sjekk("Volum", 1, ""))
        with pytest.raises(ValueError):
            ki_grunnlag(
                Signal(styrke=2, retning="Positiv", sjekker=sjekker, skiller_seg_ut=False), utenfor_maalingen=False
            )

    def test_grunnlaget_kan_logges(self):
        """Grunnlaget er det KIRad.grunnlag lagrer (story 4.2)."""
        from kilogg import Emne, KIRad

        rad = KIRad(
            emne=Emne.aksje("EQNR", date(2026, 10, 15)),
            grunnlag=ki_grunnlag(beregn_signal(_serie()), utenfor_maalingen=False),
            regelen="r",
            tekst=None,
            besto=False,
            grunn="modellen feilet",
            promptversjon="1",
            tjeneste="lokal",
            modell="gemma4:e4b",
        )
        assert set(rad.grunnlag) == NOEKLENE
