"""Story 4.2: KILogg-porten med minneimplementasjon - FR-604, FR-605, AD-3, AD-7.

Hele porten proeves mot MinneKILogg, uten database.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from kilogg import AKSJE, DAG, MELDING, Emne, KILogg, KIRad, UgyldigKIRad
from kilogg_minne import MinneKILogg

OSLO = ZoneInfo("Europe/Oslo")
TORSDAG = date(2026, 10, 15)
FREDAG = date(2026, 10, 16)


def _klokka(dag: date, time: int = 22):
    return datetime(dag.year, dag.month, dag.day, time, 0, tzinfo=OSLO)


class Klokke:
    """En klokke testen kan flytte."""

    def __init__(self, dag: date = TORSDAG):
        self.naa = _klokka(dag)

    def __call__(self):
        return self.naa


def _rad(emne: Emne | None = None, **endret) -> KIRad:
    felt = dict(
        emne=emne or Emne.aksje("EQNR", TORSDAG),
        grunnlag={"trend": 1, "bevegelse": 0, "interesse": 1, "styrke": 2, "retning": "Positiv"},
        regelen="Trenden og interessen ga utslag.",
        tekst="Kursen ligger over snittet, og flere enn vanlig handlet.",
        besto=True,
        grunn=None,
        promptversjon="1",
        tjeneste="lokal",
        modell="gemma4:e4b",
        modell_id="dc35e8d9c606",
        seed=42,
        temperatur=0,
        maskinvare="gpu",
        ollama_versjon="0.35.1",
    )
    felt.update(endret)
    return KIRad(**felt)


class TestRaden:
    def test_de_felles_feltene(self):
        """Dato, modell, promptversjon, hva regelen sa og hva KI la til."""
        rad = _rad()
        assert rad.emne.dato == TORSDAG
        assert rad.modell == "gemma4:e4b"
        assert rad.promptversjon == "1"
        assert rad.regelen == "Trenden og interessen ga utslag."
        assert rad.tekst.startswith("Kursen ligger")

    @pytest.mark.parametrize("felt", ["promptversjon", "modell"])
    @pytest.mark.parametrize("verdi", ["", "   ", None, 1])
    def test_promptversjon_og_modell_kan_ikke_mangle(self, felt, verdi):
        """Ville feilet hvis promptversjon og modell var utelatt fra raden
        (story 4.2). Da blir eksempelsettet flere systemer som ser ut som ett."""
        with pytest.raises(UgyldigKIRad):
            _rad(**{felt: verdi})

    @pytest.mark.parametrize("felt", ["promptversjon", "modell", "tjeneste", "regelen", "grunnlag"])
    def test_feltene_er_paakrevd(self, felt):
        argumenter = dict(
            emne=Emne.aksje("EQNR", TORSDAG), grunnlag={}, regelen="", tekst=None, besto=False,
            grunn="modellen feilet", promptversjon="1", tjeneste="lokal", modell="gemma4:e4b",
        )
        del argumenter[felt]
        with pytest.raises(TypeError):
            KIRad(**argumenter)

    def test_tilleggene_fra_0510(self):
        """Tjenesten, modell-ID, seed, temperatur, maskinvaren og
        Ollama-versjonen (FR-604, FR-605)."""
        rad = _rad()
        assert (rad.tjeneste, rad.modell_id, rad.seed, rad.temperatur, rad.maskinvare, rad.ollama_versjon) == (
            "lokal", "dc35e8d9c606", 42, 0.0, "gpu", "0.35.1")
        tom = _rad(tjeneste="gemini", modell_id=None, seed=None, temperatur=None, maskinvare=None, ollama_versjon=None)
        assert tom.maskinvare is None

    @pytest.mark.parametrize("felt, verdi", [
        ("tjeneste", "av"), ("tjeneste", "chatgpt"), ("maskinvare", "tpu"), ("seed", True),
        ("seed", 1.5), ("temperatur", float("nan")), ("temperatur", -0.1), ("temperatur", "0"),
        ("modell_id", ""), ("ollama_versjon", ""), ("regelen", None),
    ])
    def test_ugyldige_verdier(self, felt, verdi):
        with pytest.raises(UgyldigKIRad):
            _rad(**{felt: verdi})

    def test_modellen_feilet_gir_en_rad_uten_tekst(self):
        """FR-604, NFR-04: raden finnes ogsaa naar modellen feilet."""
        rad = _rad(tekst=None, besto=False, grunn="modellen svarte ikke innen tidsfristen")
        assert rad.tekst is None and not rad.besto

    def test_tekst_som_ikke_besto_har_grunnen(self):
        rad = _rad(besto=False, grunn="feil retning: teksten sier negativ")
        assert rad.tekst and rad.grunn

    @pytest.mark.parametrize("endret", [
        dict(besto=False, grunn=None),
        dict(besto=True, grunn="feil tall"),
        dict(besto=True, tekst=None),
        dict(besto=1),
        dict(tekst=""),
    ])
    def test_besto_tekst_og_grunn_hoerer_sammen(self, endret):
        with pytest.raises(UgyldigKIRad):
            _rad(**endret)

    def test_grunnlaget_er_en_kopi_som_ikke_kan_endres(self):
        grunnlag = {"trend": 1, "retning": "Positiv"}
        rad = _rad(grunnlag=grunnlag)
        grunnlag["trend"] = -1
        assert rad.grunnlag["trend"] == 1
        with pytest.raises(TypeError):
            rad.grunnlag["trend"] = 0

    @pytest.mark.parametrize("grunnlag", [
        {"x": float("nan")}, {"x": object()}, {1: "tall som noekkel"}, ["ikke", "mapping"],
    ])
    def test_grunnlaget_maa_kunne_skrives_som_json(self, grunnlag):
        with pytest.raises(UgyldigKIRad):
            _rad(grunnlag=grunnlag)


class TestEmnet:
    def test_tre_slag(self):
        """Plan B, plan A og dagsteksten i 10.6 (svar 6 kl. 15:53)."""
        assert Emne.aksje("EQNR", TORSDAG) == Emne(AKSJE, TORSDAG, symbol="EQNR")
        assert Emne.melding("m-1", TORSDAG) == Emne(MELDING, TORSDAG, melding_id="m-1")
        assert Emne.dagen(TORSDAG) == Emne(DAG, TORSDAG)

    @pytest.mark.parametrize("slag, symbol, melding_id", [
        (AKSJE, "EQNR", "m-1"),
        (MELDING, "EQNR", "m-1"),
        (DAG, "EQNR", None),
        (DAG, None, "m-1"),
    ])
    def test_begge_emnene_avvises(self, slag, symbol, melding_id):
        """En rad med begge, eller med et emne slaget ikke har, avvises (4.2)."""
        with pytest.raises(UgyldigKIRad):
            Emne(slag, TORSDAG, symbol=symbol, melding_id=melding_id)

    @pytest.mark.parametrize("slag, symbol, melding_id", [
        (AKSJE, None, None), (AKSJE, "", None), (MELDING, None, None), (MELDING, None, " "),
    ])
    def test_ingen_av_dem_avvises_for_aksje_og_melding(self, slag, symbol, melding_id):
        with pytest.raises(UgyldigKIRad):
            Emne(slag, TORSDAG, symbol=symbol, melding_id=melding_id)

    @pytest.mark.parametrize("slag, dato", [
        ("aksjer", TORSDAG), ("", TORSDAG), (AKSJE, datetime(2026, 10, 15, 12)), (AKSJE, "2026-10-15"),
    ])
    def test_ukjent_slag_og_dato_som_ikke_er_date(self, slag, dato):
        with pytest.raises(UgyldigKIRad):
            Emne(slag, dato, symbol="EQNR")

    def test_emne_maa_vaere_emne(self):
        with pytest.raises(UgyldigKIRad):
            _rad(emne=("EQNR", TORSDAG))


class TestPorten:
    def test_bare_skriv_og_lesemetoder(self):
        """AD-7: ingen slett og ingen endre, i porten og i minnet."""
        offentlige = {navn for navn in vars(KILogg) if not navn.startswith("_")}
        assert offentlige == {"skriv", "les", "les_alle"}
        minnet = {navn for navn in dir(MinneKILogg) if not navn.startswith("_")}
        assert minnet == {"skriv", "les", "les_alle"}

    def test_minnet_oppfyller_porten(self):
        assert isinstance(MinneKILogg(Klokke()), KILogg)

    def test_skriv_og_les(self):
        logg = MinneKILogg(Klokke())
        rad = _rad()
        assert logg.skriv(rad) is True
        assert logg.les(Emne.aksje("EQNR", TORSDAG)) == rad
        assert logg.les(Emne.aksje("NHY", TORSDAG)) is None

    def test_raden_staar_naar_den_finnes(self):
        """FR-604 og svar 2 kl. 15:53: den foerste raden staar, og skriv gir
        False uten aa reise. Ville feilet hvis raden ble skrevet over."""
        logg = MinneKILogg(Klokke())
        foerste = _rad()
        assert logg.skriv(foerste)
        assert logg.skriv(_rad(tekst="En annen tekst.")) is False
        assert logg.les(foerste.emne) == foerste
        assert len(logg.les_alle()) == 1

    def test_raden_staar_ogsaa_naar_modellen_feilet(self):
        logg = MinneKILogg(Klokke())
        feilet = _rad(tekst=None, besto=False, grunn="modellen svarte ikke")
        assert logg.skriv(feilet)
        assert logg.skriv(_rad()) is False
        assert logg.les(feilet.emne) == feilet

    @pytest.mark.parametrize("dato", [date(2026, 10, 14), FREDAG])
    def test_bare_inneveerende_boersdag(self, dato):
        """AD-7: en eldre rad kan ikke skrives, og heller ikke en dag fram."""
        logg = MinneKILogg(Klokke(TORSDAG))
        with pytest.raises(ValueError):
            logg.skriv(_rad(Emne.aksje("EQNR", dato)))
        assert logg.les_alle() == []

    def test_helgen_hoerer_til_fredagen(self):
        klokke = Klokke(date(2026, 10, 17))
        logg = MinneKILogg(klokke)
        assert logg.skriv(_rad(Emne.aksje("EQNR", FREDAG)))

    def test_bare_kirad(self):
        with pytest.raises(TypeError):
            MinneKILogg(Klokke()).skriv({"emne": "EQNR"})

    def test_en_lesing_gir_alle_slag_ordnet_etter_dato(self):
        """Plan A og plan B i samme logg (story 4.2, AD-3)."""
        klokke = Klokke(TORSDAG)
        logg = MinneKILogg(klokke)
        torsdag = [_rad(Emne.aksje("EQNR", TORSDAG)), _rad(Emne.melding("m-1", TORSDAG)),
                   _rad(Emne.dagen(TORSDAG))]
        for rad in torsdag:
            assert logg.skriv(rad)
        klokke.naa = _klokka(FREDAG)
        fredag = [_rad(Emne.dagen(FREDAG)), _rad(Emne.aksje("EQNR", FREDAG))]
        for rad in fredag:
            assert logg.skriv(rad)
        assert logg.les_alle() == torsdag + fredag
        assert {rad.emne.slag for rad in logg.les_alle()} == {AKSJE, MELDING, DAG}
