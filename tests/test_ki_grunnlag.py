"""Story 10.1: grunnlaget som sendes - bare utledede verdier (betingelse 4,
prd.md §4.6, merknaden 04.10 i 4.1, svar 10 kl. 15:53)."""

from collections.abc import Mapping
from datetime import date, timedelta

import pytest

from dagene import tell_dagene
from ki_grunnlag import (
    FALT,
    RETNINGER,
    SJEKKENE,
    STEG,
    UENDRET,
    UTENFOR_MAALINGEN,
    Dagsbilde,
    bevegelse,
    ki_grunnlag,
    lag_dagsbilde,
)
from kursdata import Aksje, Kursrad
from signalberegning import Signal, Sjekk, beregn_signal, vurder
from vurderingsdata import Grunn, Vurdering

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


# Story 10.2e: dagen i grunnlaget for prompten versjon 3 (gruppens svar 24.10
# kl. 16:15). Fredag 23.10, med helgen 17.-18.10 mellom fredag 16.10 og
# mandag 19.10.
FREDAG = date(2026, 10, 23)
UKA = [date(2026, 10, 16), date(2026, 10, 19), date(2026, 10, 20), date(2026, 10, 21), date(2026, 10, 22), FREDAG]
FORTEGN = {
    ("Positiv", 1): (1, 0, 0),
    ("Positiv", 2): (1, 1, 0),
    ("Positiv", 3): (1, 1, 1),
    ("Negativ", 2): (-1, -1, 0),
    ("Blandet", 2): (1, -1, 0),
    ("Ingen", 0): (0, 0, 0),
}


def _v(retning: str, styrke: int) -> Vurdering:
    trend, bevegelse_, interesse = FORTEGN[(retning, styrke)]
    return Vurdering(
        styrke=styrke,
        retning=retning,
        trend=trend,
        bevegelse=bevegelse_,
        interesse=interesse,
        slutt=101.37,
        justert_slutt=101.37,
        trend_avvik=0.0123,
        dagens_endring=0.0217,
        standardavvik=0.0071,
        volumforhold=1.73,
    )


def _aksje(symbol: str, sektor: str) -> Aksje:
    return Aksje(symbol=symbol, ticker=f"{symbol}.OL", navn=symbol.title(), sektor=sektor)


def _kurser(*justert: float, siste: date = FREDAG) -> list[Kursrad]:
    """Kursene til og med siste, én per boersdag bakover."""
    dager = [d for d in UKA if d <= siste][-len(justert) :]
    return [Kursrad(dato=d, slutt=k, justert_slutt=k, volum=1_000_003) for d, k in zip(dager, justert)]


class TestDagene:
    def test_samme_retning_og_styrke_hele_uka(self):
        """Ville feilet hvis dagene ikke telte bakover over helgen etter
        boersdagene: mandag 19.10 og fredag 16.10 er paa rad."""
        tidligere = {d: _v("Positiv", 2) for d in UKA[:-1]}
        tidligere[date(2026, 10, 15)] = _v("Negativ", 2)
        assert tell_dagene(FREDAG, _v("Positiv", 2), tidligere) == (6, False)

    def test_dagene_naar_styrken_byttes(self):
        """Ville feilet hvis dagene ble telt bare paa retningen: Positiv med
        styrke 1 til og med onsdag og Positiv med styrke 2 torsdag og fredag
        er to boersdager, ikke seks."""
        tidligere = {d: _v("Positiv", 1) for d in UKA[:-2]}
        tidligere[UKA[-2]] = _v("Positiv", 2)
        assert tell_dagene(FREDAG, _v("Positiv", 2), tidligere) == (2, False)

    def test_dagene_naar_retningen_byttes(self):
        """Ville feilet hvis dagene ble telt bare paa styrken."""
        tidligere = {UKA[-2]: _v("Negativ", 2), UKA[-3]: _v("Positiv", 2)}
        assert tell_dagene(FREDAG, _v("Positiv", 2), tidligere) == (1, False)

    def test_en_grunn_stopper_rekka(self):
        """Ville feilet hvis en dag med en grunn i stedet for vurdering ga
        «minst»: den dagen var det ikke noe signal, saa antallet er kjent."""
        tidligere = {UKA[-2]: _v("Ingen", 0), UKA[-3]: Grunn.KURS_IKKE_FRA_DAGEN}
        assert tell_dagene(FREDAG, _v("Ingen", 0), tidligere) == (2, False)

    def test_minst_ved_foerste_lagrede_vurdering(self):
        """Ville feilet hvis rekka som naar foerste lagrede vurdering, ikke ble
        merket «minst»: hvordan signalet var foer, er ukjent."""
        tidligere = {d: _v("Blandet", 2) for d in UKA[2:-1]}
        assert tell_dagene(FREDAG, _v("Blandet", 2), tidligere) == (4, True)

    def test_minst_naar_en_boersdag_mangler(self):
        tidligere = {UKA[-2]: _v("Positiv", 3), UKA[-4]: _v("Positiv", 3)}
        assert tell_dagene(FREDAG, _v("Positiv", 3), tidligere) == (2, True)

    def test_minst_ved_starten_av_kalenderen(self):
        """Ville feilet hvis rekka gikk forbi kalenderen (UtenforKalenderen)
        i stedet for aa si «minst»."""
        assert tell_dagene(date(2026, 1, 2), _v("Ingen", 0), {}) == (1, True)


class TestDagsbildet:
    LISTA = (
        _aksje("EQNR", "Energi"),
        _aksje("AKRBP", "Energi"),
        _aksje("DNB", "Finans"),
        _aksje("MOWI", "Sjømat"),
        _aksje("NY", "Teknologi"),
    )

    def _bildet(self, serier, indeks=None, aksje=0):
        return lag_dagsbilde(self.LISTA[aksje], FREDAG, _v("Positiv", 1), {}, self.LISTA, serier, indeks)

    def test_antallene_som_i_boersometeret(self):
        """Ville feilet hvis antallene og bransjen ikke var de samme som
        fargene og snittet i boersometeret (bygg_rute og snitt)."""
        from boersometer import bygg_rute, snitt

        serier = {
            "EQNR": _kurser(100.0, 101.37),
            "AKRBP": _kurser(200.0, 197.13),
            "DNB": _kurser(50.0, 50.001),
            "MOWI": _kurser(180.0, 177.55),
            "NY": _kurser(10.0),
        }
        bildet = self._bildet(serier)
        ruter = [bygg_rute(a, serier[a.symbol], _v("Positiv", 1), FREDAG, FREDAG) for a in self.LISTA]
        assert bildet.aksjer_steg == sum(1 for r in ruter if bevegelse(r.endring) == STEG) == 1
        assert bildet.aksjer_falt == sum(1 for r in ruter if bevegelse(r.endring) == FALT) == 2
        assert bildet.bransjen == bevegelse(snitt([r for r in ruter if r.aksje.sektor == "Energi"])) == FALT

    def test_uendret_slik_det_vises(self):
        """Ville feilet hvis en endring som vises som 0,00 % ble telt som
        steg: fargen i boersometeret er da noeytral."""
        assert bevegelse(0.004) == UENDRET
        assert bevegelse(-0.004) == UENDRET
        assert bevegelse(0.006) == STEG
        assert bevegelse(None) is None

    def test_en_aksje_uten_kurs_paa_dagen_telles_ikke(self):
        serier = {"EQNR": _kurser(100.0, 101.0), "DNB": _kurser(50.0, 49.0, siste=UKA[-2])}
        bildet = self._bildet(serier)
        assert (bildet.aksjer_steg, bildet.aksjer_falt) == (1, 0)

    def test_hovedindeksen_som_streken_paa_grafen(self):
        """Ville feilet hvis hovedindeksen fikk en annen retning enn den
        stiplede linja paa forsiden (bygg_soeyler), som ligger under null
        naar indeksen falt."""
        from hovedindeks import bygg_soeyler, indeksendring

        indeks = _kurser(1500.0, 1491.2)
        bildet = self._bildet({"EQNR": _kurser(100.0, 101.0)}, indeks)
        soeyler = bygg_soeyler(FREDAG, indeksendring(indeks), [(self.LISTA[0], _kurser(100.0, 101.0), False)])
        assert bildet.hovedindeksen == FALT
        assert soeyler.linje > 50

    def test_ingen_hovedindeks_uten_rad_for_dagen(self):
        """Ville feilet hvis en gammel indeksrad ga hovedindeksen for dagen."""
        bildet = self._bildet({"EQNR": _kurser(100.0, 101.0)}, _kurser(1500.0, 1510.0, siste=UKA[-2]))
        assert bildet.hovedindeksen is None
        assert "hovedindeksen" not in ki_grunnlag(_v("Positiv", 1), utenfor_maalingen=False, dagen=bildet)

    def test_ingen_hovedindeks_uten_forrige_boersdag(self):
        indeks = [Kursrad(dato=d, slutt=k, justert_slutt=k, volum=0) for d, k in ((UKA[-3], 1500.0), (FREDAG, 1510.0))]
        assert self._bildet({}, indeks).hovedindeksen is None

    def test_ingen_bransje_uten_endring(self):
        bildet = self._bildet({"NY": _kurser(10.0)}, aksje=4)
        assert bildet.bransjen is None
        assert "bransjen" not in ki_grunnlag(_v("Positiv", 1), utenfor_maalingen=False, dagen=bildet)


class TestGrunnlagetMedDagen:
    BILDET = Dagsbilde(dager=4, dager_minst=True, hovedindeksen=STEG, aksjer_steg=9, aksjer_falt=5, bransjen=FALT)

    def test_feltene(self):
        grunnlag = ki_grunnlag(_v("Positiv", 2), utenfor_maalingen=False, dagen=self.BILDET)
        assert dict(grunnlag) == {
            "trend": 1,
            "bevegelse": 1,
            "interesse": 0,
            "styrke": 2,
            "retning": "Positiv",
            "hovedindeksen": STEG,
            "aksjer_steg": 9,
            "aksjer_falt": 5,
            "bransjen": FALT,
        }

    def test_ingen_desimaltall_med_dagen(self):
        """Ville feilet hvis dagen sendte en prosent, et snitt eller en kurs
        (beslutningen 04.10 og svaret 21.10 kl. 23:51)."""
        grunnlag = ki_grunnlag(_v("Positiv", 2), utenfor_maalingen=True, dagen=self.BILDET)
        for verdi in _alle_tall(grunnlag):
            assert type(verdi) in (int, str), verdi

    def test_dagene_sendes_ikke(self):
        """Gruppens svar 25.10 kl. 00:51: modellen faar ikke dagene, med eller
        uten merket. Ville feilet hvis dager eller dager_merke kom med."""
        for minst in (False, True):
            bildet = Dagsbilde(
                dager=1, dager_minst=minst, hovedindeksen=None, aksjer_steg=0, aksjer_falt=0, bransjen=None
            )
            grunnlag = ki_grunnlag(_v("Ingen", 0), utenfor_maalingen=False, dagen=bildet)
            assert set(grunnlag) == NOEKLENE | {"aksjer_steg", "aksjer_falt"}

    @pytest.mark.parametrize(
        "felt, verdi",
        [
            ("aksjer_steg", -1),
            ("aksjer_falt", True),
            ("hovedindeksen", "opp"),
            ("bransjen", "Positiv"),
        ],
    )
    def test_ugyldige_verdier_avvises(self, felt, verdi):
        """Ville feilet hvis et felt fra dagen kunne ha en verdi utenfor
        omraadet eller den lukkede lista, som et flyttall eller True."""
        import dataclasses

        bildet = dataclasses.replace(self.BILDET, **{felt: verdi})
        with pytest.raises(ValueError):
            ki_grunnlag(_v("Positiv", 2), utenfor_maalingen=False, dagen=bildet)

    def test_dagen_maa_vaere_et_dagsbilde(self):
        with pytest.raises(TypeError):
            ki_grunnlag(_v("Positiv", 2), utenfor_maalingen=False, dagen={"dager": 1})
