"""Story 10.1: grunnlaget som sendes - bare utledede verdier (betingelse 4,
prd.md §4.6, merknaden 04.10 i 4.1, svar 10 kl. 15:53)."""

from datetime import date, timedelta

import pytest

from kursdata import Kursrad
from ki_grunnlag import RETNINGER, SJEKKENE, UTENFOR_MAALINGEN, ki_grunnlag
from signalberegning import Sjekk, Signal, beregn_signal, vurder
from vurderingsdata import Vurdering

NOEKLENE = {*SJEKKENE, "styrke", "retning"}


def _serie(antall: int = 60) -> list[Kursrad]:
    """En serie der hver kurs og hvert volum er et eget tall med desimaler,
    saa ingen av dem kan forveksles med et fortegn eller en styrke."""
    rader = []
    kurs = 101.37
    for nummer in range(antall):
        kurs = round(kurs * (1.0123 if nummer % 3 else 0.9917), 4)
        rader.append(Kursrad(
            dato=date(2026, 7, 1) + timedelta(days=nummer),
            slutt=round(kurs * 1.0311, 4),
            justert_slutt=kurs,
            volum=1_000_003 + nummer * 7_919 + (900_000 if nummer == antall - 1 else 0),
        ))
    return rader


def _alle_tall(verdi):
    if isinstance(verdi, dict):
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
        grunnlag = ki_grunnlag(signal)
        assert set(grunnlag) == NOEKLENE
        assert grunnlag["styrke"] == signal.styrke
        assert grunnlag["retning"] == signal.retning
        assert [grunnlag[navn] for navn in SJEKKENE] == [sjekk.verdi for sjekk in signal.sjekker]

    def test_vurderingen_gir_det_samme(self):
        rader = _serie()
        assert ki_grunnlag(_vurderingen(rader)) == ki_grunnlag(beregn_signal(rader))

    @pytest.mark.parametrize("hvor", ["signal", "vurdering"])
    def test_ingen_desimaltall(self, hvor):
        """Ville feilet hvis grunnlaget hadde en prosent eller et
        forholdstall (beslutningen 04.10)."""
        rader = _serie()
        kilde = beregn_signal(rader) if hvor == "signal" else _vurderingen(rader)
        for verdi in _alle_tall(ki_grunnlag(kilde)):
            assert not isinstance(verdi, float), verdi
            assert isinstance(verdi, (int, str)), verdi

    def test_ingen_kurs_volum_eller_maaling(self):
        """Ville feilet hvis grunnlaget inneholdt dagens volum eller en kurs.
        Da sendes et raatt datapunkt fra EODHD til en tredjepart."""
        rader = _serie()
        vurdering = _vurderingen(rader)
        signal = beregn_signal(rader)
        forbudt = {r.slutt for r in rader} | {r.justert_slutt for r in rader} | {r.volum for r in rader}
        forbudt |= {vurdering.trend_avvik, vurdering.dagens_endring, vurdering.standardavvik,
                    vurdering.volumforhold, vurdering.slutt, vurdering.justert_slutt}
        forbudt |= {s.maaling for s in signal.sjekker} | {s.grense for s in signal.sjekker}
        forbudt |= {round(v * 100, d) for v in (vurdering.dagens_endring, vurdering.trend_avvik)
                    for d in (1, 2)}
        forbudt.discard(None)
        # Serien er laget slik at ingen av de forbudte verdiene er et fortegn
        # eller en styrke.
        assert not forbudt & {-1, 0, 1, 2, 3}
        for kilde in (signal, vurdering):
            for verdi in _alle_tall(ki_grunnlag(kilde)):
                assert verdi not in forbudt, verdi
                if isinstance(verdi, str):
                    assert not any(tegn.isdigit() for tegn in verdi), verdi
                else:
                    assert verdi in (-1, 0, 1, 2, 3), verdi

    def test_teksten_er_fra_den_lukkede_lista(self):
        grunnlag = ki_grunnlag(beregn_signal(_serie()))
        assert grunnlag["retning"] in RETNINGER

    def test_ingen_antall(self):
        """Svar 10 kl. 15:53: «antall» gjelder dagsteksten i 10.6."""
        grunnlag = ki_grunnlag(beregn_signal(_serie()))
        assert not any("antall" in noekkel for noekkel in grunnlag)


class TestUtenforMaalingen:
    def test_merket_og_de_samme_verdiene(self):
        """FR-412, endringsforslaget 08.10: samme utledede verdier, og merket."""
        signal = beregn_signal(_serie())
        vanlig = ki_grunnlag(signal)
        utenfor = ki_grunnlag(signal, utenfor_maalingen=True)
        assert utenfor == {**vanlig, "merke": UTENFOR_MAALINGEN}
        assert "merke" not in vanlig

    def test_bare_true_eller_false(self):
        with pytest.raises(TypeError):
            ki_grunnlag(beregn_signal(_serie()), utenfor_maalingen="ja")


class TestKontrollen:
    def test_bare_signal_eller_vurdering(self):
        with pytest.raises(TypeError):
            ki_grunnlag({"trend": 1})

    def test_ukjent_sjekk_avvises(self):
        sjekker = (Sjekk("Trend", 1, ""), Sjekk("Bevegelse", 0, ""), Sjekk("Volum", 1, ""))
        with pytest.raises(ValueError):
            ki_grunnlag(Signal(styrke=2, retning="Positiv", sjekker=sjekker, skiller_seg_ut=False))

    def test_styrke_utenfor_omraadet_avvises(self):
        sjekker = (Sjekk("Trend", 1, ""), Sjekk("Bevegelse", 1, ""), Sjekk("Interesse", 1, ""))
        with pytest.raises(ValueError):
            ki_grunnlag(Signal(styrke=4, retning="Positiv", sjekker=sjekker, skiller_seg_ut=True))

    def test_grunnlaget_kan_logges(self):
        """Grunnlaget er det KIRad.grunnlag lagrer (story 4.2)."""
        from kilogg import Emne, KIRad

        rad = KIRad(
            emne=Emne.aksje("EQNR", date(2026, 10, 15)), grunnlag=ki_grunnlag(beregn_signal(_serie())),
            regelen="r", tekst=None, besto=False, grunn="modellen feilet", promptversjon="1",
            tjeneste="lokal", modell="gemma4:e4b",
        )
        assert set(rad.grunnlag) == NOEKLENE
