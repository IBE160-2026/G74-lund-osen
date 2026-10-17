"""Story 4.2: KILogg-porten med minneimplementasjon - FR-604, FR-605, AD-3, AD-7.

Hele porten proeves mot MinneKILogg, uten database. Testene for porten tar
loggen fra fixturen logg_lager, saa SQLite-adapteren i 4.3 kan proeves mot de
samme testene (gjennomgangen av 4.2, BH7). Story 4.3: SqliteKILogg proeves
mot de samme testene, med en base i minnet.
"""

import json
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from kilogg import (
    AKSJE,
    DAG,
    MELDING,
    Emne,
    IkkeInnevaerendeBoersdag,
    KILogg,
    KIRad,
    UgyldigKIRad,
)
from kilogg_minne import MinneKILogg
from lagring_sqlite import SqliteKILogg, aapne_base

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
            emne=Emne.aksje("EQNR", TORSDAG),
            grunnlag={},
            regelen="Ingen sjekk ga utslag.",
            tekst=None,
            besto=False,
            grunn="modellen feilet",
            promptversjon="1",
            tjeneste="lokal",
            modell="gemma4:e4b",
        )
        del argumenter[felt]
        with pytest.raises(TypeError):
            KIRad(**argumenter)

    def test_tilleggene_fra_0510(self):
        """Tjenesten, modell-ID, seed, temperatur, maskinvaren og
        Ollama-versjonen (FR-604, FR-605)."""
        rad = _rad()
        assert (rad.tjeneste, rad.modell_id, rad.seed, rad.temperatur, rad.maskinvare, rad.ollama_versjon) == (
            "lokal",
            "dc35e8d9c606",
            42,
            0.0,
            "gpu",
            "0.35.1",
        )
        assert type(rad.temperatur) is float
        tom = _rad(tjeneste="gemini", modell_id=None, seed=None, temperatur=None, maskinvare=None, ollama_versjon=None)
        assert tom.maskinvare is None

    @pytest.mark.parametrize(
        "felt, verdi",
        [
            ("tjeneste", "av"),
            ("tjeneste", "chatgpt"),
            ("maskinvare", "tpu"),
            ("seed", True),
            ("seed", 1.5),
            ("seed", 2**63),
            ("seed", -(2**63) - 1),
            ("temperatur", float("nan")),
            ("temperatur", -0.1),
            ("temperatur", "0"),
            ("temperatur", 10**400),
            ("modell_id", ""),
            ("ollama_versjon", ""),
            ("regelen", None),
            ("regelen", ""),
            ("regelen", "  "),
        ],
    )
    def test_ugyldige_verdier(self, felt, verdi):
        with pytest.raises(UgyldigKIRad):
            _rad(**{felt: verdi})

    @pytest.mark.parametrize(
        "endret",
        [
            dict(maskinvare="gpu", ollama_versjon=None),
            dict(maskinvare=None, ollama_versjon="0.35.1"),
        ],
    )
    def test_maskinvaren_og_ollama_bare_for_den_lokale(self, endret):
        """Gjennomgangen (BH8): en tjeneste paa nettet har ikke dem (FR-605)."""
        with pytest.raises(UgyldigKIRad):
            _rad(tjeneste="gemini", **endret)

    def test_modellen_feilet_gir_en_rad_uten_tekst(self):
        """FR-604, NFR-04: raden finnes ogsaa naar modellen feilet."""
        rad = _rad(tekst=None, besto=False, grunn="modellen svarte ikke innen tidsfristen")
        assert rad.tekst is None and not rad.besto
        assert rad.modellen_feilet

    def test_tekst_som_ikke_besto_har_grunnen(self):
        rad = _rad(besto=False, grunn="feil retning: teksten sier negativ")
        assert rad.tekst and rad.grunn
        assert not rad.modellen_feilet

    @pytest.mark.parametrize(
        "endret",
        [
            dict(besto=False, grunn=None),
            dict(besto=True, grunn="feil tall"),
            dict(besto=True, tekst=None),
            dict(besto=1),
            dict(tekst=""),
        ],
    )
    def test_besto_tekst_og_grunn_hoerer_sammen(self, endret):
        with pytest.raises(UgyldigKIRad):
            _rad(**endret)

    def test_grunnlaget_er_en_kopi_som_ikke_kan_endres(self):
        grunnlag = {"trend": 1, "retning": "Positiv", "under": {"a": [1, 2]}}
        rad = _rad(grunnlag=grunnlag)
        grunnlag["trend"] = -1
        grunnlag["under"]["a"].append(3)
        assert rad.grunnlag["trend"] == 1
        assert rad.grunnlag["under"]["a"] == (1, 2)
        with pytest.raises(TypeError):
            rad.grunnlag["trend"] = 0
        with pytest.raises(TypeError):
            rad.grunnlag["under"]["b"] = 0

    def test_grunnlaget_som_json(self):
        rad = _rad(grunnlag={"b": [1, {"c": None}], "a": "Ø"})
        assert json.loads(rad.grunnlag_som_json()) == {"a": "Ø", "b": [1, {"c": None}]}

    @pytest.mark.parametrize(
        "grunnlag",
        [
            {"x": float("nan")},
            {"x": object()},
            {1: "tall som noekkel"},
            ["ikke", "mapping"],
            {"x": {1: "tall som noekkel inni"}},
            {"x": (1, 2)},
            {"x": {"y": float("inf")}},
        ],
    )
    def test_grunnlaget_maa_kunne_skrives_som_json(self, grunnlag):
        with pytest.raises(UgyldigKIRad):
            _rad(grunnlag=grunnlag)

    def test_grunnlaget_kan_ikke_vaere_uendelig_dypt(self):
        dypt = {}
        for _ in range(100):
            dypt = {"x": dypt}
        with pytest.raises(UgyldigKIRad):
            _rad(grunnlag=dypt)

    def test_raden_kan_hashes(self):
        """Gjennomgangen (BH9): uten grunnlaget, som ikke kan hashes."""
        assert hash(_rad()) == hash(_rad())
        assert _rad() == _rad()
        assert _rad() != _rad(grunnlag={"trend": 0})


class TestEmnet:
    def test_tre_slag(self):
        """Plan B, plan A og dagsteksten i 10.6 (svar 6 kl. 15:53)."""
        assert Emne.aksje("EQNR", TORSDAG) == Emne(AKSJE, TORSDAG, symbol="EQNR")
        assert Emne.melding("m-1", TORSDAG) == Emne(MELDING, TORSDAG, melding_id="m-1")
        assert Emne.dagen(TORSDAG) == Emne(DAG, TORSDAG)

    @pytest.mark.parametrize(
        "slag, symbol, melding_id",
        [
            (AKSJE, "EQNR", "m-1"),
            (MELDING, "EQNR", "m-1"),
            (DAG, "EQNR", None),
            (DAG, None, "m-1"),
        ],
    )
    def test_begge_emnene_avvises(self, slag, symbol, melding_id):
        """En rad med begge, eller med et emne slaget ikke har, avvises (4.2)."""
        with pytest.raises(UgyldigKIRad):
            Emne(slag, TORSDAG, symbol=symbol, melding_id=melding_id)

    @pytest.mark.parametrize(
        "slag, symbol, melding_id",
        [
            (AKSJE, None, None),
            (AKSJE, "", None),
            (MELDING, None, None),
            (MELDING, None, " "),
        ],
    )
    def test_ingen_av_dem_avvises_for_aksje_og_melding(self, slag, symbol, melding_id):
        with pytest.raises(UgyldigKIRad):
            Emne(slag, TORSDAG, symbol=symbol, melding_id=melding_id)

    @pytest.mark.parametrize(
        "emne",
        [
            lambda: Emne.aksje("eqnr", TORSDAG),
            lambda: Emne.aksje("EQNR ", TORSDAG),
            lambda: Emne.aksje(" EQNR", TORSDAG),
            lambda: Emne.melding("m-1 ", TORSDAG),
        ],
    )
    def test_samme_noekkel_kan_ikke_skrives_paa_to_maater(self, emne):
        """Gjennomgangen (BH1): ellers kunne samme aksje faatt to rader."""
        with pytest.raises(UgyldigKIRad):
            emne()

    @pytest.mark.parametrize(
        "slag, dato",
        [
            ("aksjer", TORSDAG),
            ("", TORSDAG),
            (AKSJE, datetime(2026, 10, 15, 12)),
            (AKSJE, "2026-10-15"),
        ],
    )
    def test_ukjent_slag_og_dato_som_ikke_er_date(self, slag, dato):
        with pytest.raises(UgyldigKIRad):
            Emne(slag, dato, symbol="EQNR")

    def test_emne_maa_vaere_emne(self):
        with pytest.raises(UgyldigKIRad):
            _rad(emne=("EQNR", TORSDAG))


def _minne(klokke):
    return MinneKILogg(klokke)


@pytest.fixture(params=["minne", "sqlite"])
def logg_lager(request):
    """Lager en KILogg med en klokke: i minnet, eller i SQLite med en base
    aapnet med aapne_base i tmp_path, migrert til siste versjon (story 4.3)."""
    if request.param == "minne":
        yield _minne
        return
    tilkoblinger = []
    katalog = request.getfixturevalue("tmp_path")

    def _sqlite(klokke):
        # Gjennomgangen av 4.3 (BH16): samme tilkobling som hentingen bruker.
        tilkobling = aapne_base(katalog / f"ki{len(tilkoblinger)}.db")
        tilkoblinger.append(tilkobling)
        return SqliteKILogg(tilkobling, klokke)

    yield _sqlite
    for tilkobling in tilkoblinger:
        tilkobling.close()


class TestPorten:
    def test_bare_skriv_og_lesemetoder(self):
        """AD-7: ingen slett og ingen endre, i porten og i minnet."""
        offentlige = {navn for navn in vars(KILogg) if not navn.startswith("_")}
        assert offentlige == {"skriv", "les", "les_alle"}
        for klasse in (MinneKILogg, SqliteKILogg):
            assert {navn for navn in dir(klasse) if not navn.startswith("_")} == {"skriv", "les", "les_alle"}
        for navn in ("__setitem__", "__delitem__"):
            for klasse in (KILogg, MinneKILogg, SqliteKILogg):
                assert not hasattr(klasse, navn)

    def test_oppfyller_porten(self, logg_lager):
        assert isinstance(logg_lager(Klokke()), KILogg)

    def test_klokka_maa_kunne_kalles(self, logg_lager):
        with pytest.raises(TypeError):
            logg_lager(_klokka(TORSDAG))

    def test_skriv_og_les(self, logg_lager):
        logg = logg_lager(Klokke())
        rad = _rad()
        assert logg.skriv(rad) is True
        assert logg.les(Emne.aksje("EQNR", TORSDAG)) == rad
        assert logg.les(Emne.aksje("NHY", TORSDAG)) is None

    def test_les_tar_bare_emne(self, logg_lager):
        with pytest.raises(TypeError):
            logg_lager(Klokke()).les(("EQNR", TORSDAG))

    def test_raden_staar_naar_den_finnes(self, logg_lager):
        """FR-604 og svar 2 kl. 15:53: den foerste raden staar, og skriv gir
        False uten aa reise. Ville feilet hvis raden ble skrevet over."""
        logg = logg_lager(Klokke())
        foerste = _rad()
        assert logg.skriv(foerste)
        assert logg.skriv(_rad(tekst="En annen tekst.")) is False
        assert logg.les(foerste.emne) == foerste
        assert len(logg.les_alle()) == 1

    def test_raden_staar_ogsaa_naar_modellen_feilet(self, logg_lager):
        logg = logg_lager(Klokke())
        feilet = _rad(tekst=None, besto=False, grunn="modellen svarte ikke")
        assert logg.skriv(feilet)
        assert logg.skriv(_rad()) is False
        assert logg.les(feilet.emne) == feilet

    @pytest.mark.parametrize("emne", [Emne.dagen(TORSDAG), Emne.melding("m-1", TORSDAG)])
    def test_dagen_og_meldingen_har_ogsaa_bare_en_rad(self, logg_lager, emne):
        """Gjennomgangen (BH6): ogsaa emnene uten symbol."""
        logg = logg_lager(Klokke())
        assert logg.skriv(_rad(emne))
        assert logg.skriv(_rad(emne, tekst="En annen tekst.")) is False

    @pytest.mark.parametrize("dato", [date(2026, 10, 14), FREDAG])
    def test_bare_inneveerende_boersdag(self, logg_lager, dato):
        """AD-7: en eldre rad kan ikke skrives, og heller ikke en dag fram."""
        logg = logg_lager(Klokke(TORSDAG))
        with pytest.raises(IkkeInnevaerendeBoersdag):
            logg.skriv(_rad(Emne.aksje("EQNR", dato)))
        assert logg.les_alle() == []

    def test_helgen_hoerer_til_fredagen(self, logg_lager):
        logg = logg_lager(Klokke(date(2026, 10, 17)))
        assert logg.skriv(_rad(Emne.aksje("EQNR", FREDAG)))

    def test_en_helligdag_hoerer_til_dagen_foer(self, logg_lager):
        """Kristi himmelfartsdag 2026 er stengt."""
        logg = logg_lager(Klokke(date(2026, 5, 14)))
        assert logg.skriv(_rad(Emne.aksje("EQNR", date(2026, 5, 13))))

    def test_dagen_regnes_i_oslo(self, logg_lager):
        """Gjennomgangen (VG2): 22:30 UTC torsdag er 00:30 fredag i Oslo."""
        klokke = Klokke()
        klokke.naa = datetime(2026, 10, 15, 22, 30, tzinfo=timezone.utc)
        logg = logg_lager(klokke)
        with pytest.raises(IkkeInnevaerendeBoersdag):
            logg.skriv(_rad(Emne.aksje("EQNR", TORSDAG)))
        assert logg.skriv(_rad(Emne.aksje("EQNR", FREDAG)))

    def test_klokke_uten_sone_avvises(self, logg_lager):
        klokke = Klokke()
        klokke.naa = datetime(2026, 10, 15, 22, 0)
        with pytest.raises(TypeError):
            logg_lager(klokke).skriv(_rad())

    def test_bare_kirad(self, logg_lager):
        with pytest.raises(TypeError):
            logg_lager(Klokke()).skriv({"emne": "EQNR"})

    def test_en_lesing_gir_alle_slag_ordnet_etter_dato(self, logg_lager):
        """Plan A og plan B i samme logg (story 4.2, AD-3)."""
        klokke = Klokke(TORSDAG)
        logg = logg_lager(klokke)
        torsdag = [_rad(Emne.aksje("EQNR", TORSDAG)), _rad(Emne.melding("m-1", TORSDAG)), _rad(Emne.dagen(TORSDAG))]
        for rad in torsdag:
            assert logg.skriv(rad)
        klokke.naa = _klokka(FREDAG)
        fredag = [_rad(Emne.dagen(FREDAG)), _rad(Emne.aksje("EQNR", FREDAG))]
        for rad in fredag:
            assert logg.skriv(rad)
        assert logg.les_alle() == torsdag + fredag
        assert {rad.emne.slag for rad in logg.les_alle()} == {AKSJE, MELDING, DAG}

    def test_ordnet_etter_dato_ikke_etter_skrivingen(self, logg_lager):
        """Gjennomgangen (VG1): en klokke som er stilt tilbake, gir en senere
        dato skrevet foer en tidligere."""
        klokke = Klokke(FREDAG)
        logg = logg_lager(klokke)
        fredag = _rad(Emne.aksje("EQNR", FREDAG))
        assert logg.skriv(fredag)
        klokke.naa = _klokka(TORSDAG)
        torsdag = _rad(Emne.aksje("EQNR", TORSDAG))
        assert logg.skriv(torsdag)
        assert logg.les_alle() == [torsdag, fredag]

    def test_lista_fra_les_alle_endrer_ikke_loggen(self, logg_lager):
        logg = logg_lager(Klokke())
        logg.skriv(_rad())
        logg.les_alle().clear()
        assert len(logg.les_alle()) == 1
