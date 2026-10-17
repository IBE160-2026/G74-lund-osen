"""Tester for hentingen. Ingen nettverk.

hent_universet tar hentefunksjonen som argument, saa hele loekka kan kjoeres
mot en falsk henter. Den ekte hent_ett_symbol kjoeres bare med requests.get
byttet ut (story 2.0), saa ingen test naar nettet eller bruker kvote.
"""

import copy
import hashlib
import json
import os
import sqlite3
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote, quote_plus
from zoneinfo import ZoneInfo

import pytest
import requests

import fetch_prices as fp
import lagring_fil
import lagring_sqlite
from eodhd_serier import AVVISTE, AVVISTE_IDER
from boersdag import innevaerende_boersdag, norsk_dato
from kursdata import AKSJEUNIVERS, Aksje
from lagring_fil import SnapshotKilde, nyeste_leser, nyeste_snapshot
from lagring_sqlite import SqliteKurslager, SqliteVurderingslager, aapne_base
from signalberegning import beregn_signal, vurder
from vurderingsdata import Grunn, Vurdering


def falsk_serie(dager: int = 60):
    """En serie leseren godtar. Foer story 1.8 hadde den datoer som «dag-000»,
    som hentingen slapp gjennom og leseren avviste."""
    start = date(2026, 6, 1)
    return [
        {
            "date": (start + timedelta(days=i)).isoformat(),
            "close": 100.0 + i,
            "adjusted_close": 100.0 + i,
            "volume": 1000,
        }
        for i in range(dager)
    ]


NOEKKEL = "FALSK-NOEKKEL-123456"

# Story 2.8: en henting er aksjene og hovedindeksen, ett kall hver.
KALL = len(AKSJEUNIVERS) + 1


def nok_kvote(_noekkel):
    """Svar fra /api/user med hele dagskvoten igjen (story 2.3)."""
    return {"apiRequests": 0, "apiRequestsDate": "2026-01-01",
            "dailyRateLimit": 20, "extraLimit": 0}

# 22:00 i Oslo 22.09.2026. kjoer tar et oeyeblikk med sone (story 2.1).
OEYEBLIKK_22_09 = datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)


def falsk_respons(status: int, ticker: str, noekkel: str, innhold=None) -> requests.Response:
    """En ekte requests.Response, som om EODHD hadde svart. Adressen har
    noekkelen, slik den ekte har."""
    r = requests.Response()
    r.status_code = status
    r.reason = {200: "OK", 500: "Internal Server Error"}.get(status, "")
    r.url = f"{fp.BASE_URL}/{ticker}?api_token={noekkel}&fmt=json"
    r._content = json.dumps(innhold if innhold is not None else []).encode()
    return r


class TestNoekkelenLekkerIkke:
    """Story 2.0: noekkelen staar aldri i en feiltekst, verken i utskriften
    eller i feil i oeyeblikksbildet. Falsk noekkel, og requests.get byttet ut."""

    def test_http_feil_gir_statuskode_uten_adresse(self, monkeypatch):
        monkeypatch.setattr(
            fp.requests, "get",
            lambda url, params, timeout: falsk_respons(500, "DNB.OL", params["api_token"]),
        )

        with pytest.raises(requests.HTTPError) as feil:
            fp.hent_ett_symbol("DNB.OL", NOEKKEL, "a", "b")

        assert str(feil.value) == "HTTP 500 Internal Server Error"
        assert NOEKKEL not in str(feil.value)
        assert feil.value.__cause__ is None and feil.value.__suppress_context__
        # response.url har ogsaa noekkelen, saa den nye feilen har ingen response.
        assert feil.value.response is None

    @pytest.mark.parametrize("feiltype", [requests.ConnectionError, requests.Timeout])
    def test_tilkoblingsfeil_og_tidsavbrudd_gir_bare_typenavnet(self, monkeypatch, feiltype):
        """Ikke bare raise_for_status(): en tilkoblingsfeil eller et
        tidsavbrudd fra requests har ogsaa adressen, med noekkelen, i teksten."""

        def get(url, params, timeout):
            raise feiltype(
                "HTTPSConnectionPool(host='eodhd.com', port=443): Max retries "
                f"exceeded with url: /api/eod/DNB.OL?api_token={params['api_token']}"
            )

        monkeypatch.setattr(fp.requests, "get", get)

        with pytest.raises(feiltype) as feil:
            fp.hent_ett_symbol("DNB.OL", NOEKKEL, "a", "b")

        assert str(feil.value) == feiltype.__name__
        assert NOEKKEL not in str(feil.value)
        assert feil.value.__cause__ is None and feil.value.__suppress_context__

    def test_hent_universet_fjerner_noekkelen_fra_enhver_feil(self):
        """Andre lag: henteren er injisert, og en feil kan komme fra hvor som
        helst. Noekkelen fjernes baade fra utskriften og fra feil."""
        linjer = []

        def hent(ticker, noekkel, *_):
            if ticker == "DNB.OL":
                raise RuntimeError(f"noe gikk galt med {noekkel}")
            return falsk_serie()

        resultat = fp.hent_universet(NOEKKEL, "a", "b", hent, linjer.append)

        assert NOEKKEL not in resultat.feil["DNB"]
        assert "***" in resultat.feil["DNB"]
        assert not [l for l in linjer if NOEKKEL in l]
        assert any("DNB: FEIL" in l and "***" in l for l in linjer)

    @pytest.mark.parametrize(
        "kodet",
        ["ab%20c%2Bd%2Fe", "ab+c%2Bd%2Fe"],
        ids=["quote", "quote_plus"],
    )
    def test_url_kodet_noekkel_fjernes_ogsaa(self, kodet):
        """requests URL-koder params. En noekkel med tegn som kodes, maa
        fjernes ogsaa i den formen.

        Story 1.8 (G3): noekkelen har mellomrom, saa quote og quote_plus gir
        ulik tekst. Foer het den ab+c/d=e, der de to ga det samme, og
        _uten_noekkel kunne mistet en av formene uten at testen feilet."""
        noekkel = "ab c+d/e"
        assert kodet in {quote(noekkel, safe=""), quote_plus(noekkel)}

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError(f"feil med api_token={kodet} i adressen")
            return falsk_serie()

        resultat = fp.hent_universet(noekkel, "a", "b", hent, lambda _: None)

        assert kodet not in resultat.feil["DNB"]
        assert "***" in resultat.feil["DNB"]


class TestSkriverIkkeOver:
    """Story 2.0: et oeyeblikksbilde skrives aldri om (AD-6)."""

    # En annen dato enn i dag, saa en retting som glemmer i_dag, feiler.
    DAG = date(2026, 9, 22)
    # Story 2.1: kjoer tar et oeyeblikk. 20:00 UTC er 22:00 i Oslo samme dag.
    OEYEBLIKK = datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)

    def test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel(self, tmp_path):
        katalog = tmp_path / "data"  # finnes ikke fra foer
        linjer = []

        def hent(ticker, noekkel, *_):
            if ticker == "DNB.OL":
                raise RuntimeError(f"feil med {noekkel}")
            return serie_til(TIRSDAG_22_09)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(katalog, tmp_path / "ose.db", self.OEYEBLIKK, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1
        fil = katalog / fp.filnavn(self.DAG)

        assert fil.exists()
        tekst = fil.read_text(encoding="utf-8")
        assert NOEKKEL not in tekst
        bilde = json.loads(tekst)
        assert (bilde["from"], bilde["to"]) == fp.bygg_intervall(self.DAG)
        assert len(bilde["serier"]) == len(AKSJEUNIVERS) - 1
        assert "***" in bilde["feil"]["DNB"]
        assert SnapshotKilde.fra_fil(fil) is not None
        assert any("Lagret" in l for l in linjer)
        assert any(f"API-kall brukt: {KALL}" in l for l in linjer)

    def test_dagens_fil_finnes_og_ingen_kall_brukes(self, tmp_path):
        fil = tmp_path / fp.filnavn(self.DAG)
        fil.write_text('{"gammel": true}', encoding="utf-8")
        linjer = []

        def hent(*_):
            pytest.fail("ingen kall skal brukes naar dagens fil finnes")

        # Beslutningen 08.10 (BH4): filvakten gir kode 1, fordi basen
        # da mangler dagen. Story 2.3b: basen mangler alle, saa det blir et
        # nytt forsoek; med dagens 20 brukt er det 0 kall til det.
        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(tmp_path, tmp_path / "ose.db", self.OEYEBLIKK, NOEKKEL, hent,
                     linjer.append, les_kvote=kvote(brukt=20))
        assert slutt.value.code == 1
        assert fil.read_text(encoding="utf-8") == '{"gammel": true}'
        assert any("finnes og skrives aldri om" in l for l in linjer)
        assert any("0 til nye forsoek" in l and "0 kall brukt" in l for l in linjer)

    def test_fil_som_dukker_opp_under_kjoeringen_skrives_ikke_over(self, tmp_path):
        """Da er kallene brukt og ingenting lagret, og kjoeringen avslutter
        med kode 1, saa det synes."""
        fil = tmp_path / fp.filnavn(self.DAG)
        linjer = []

        def hent(*_):
            if not fil.exists():
                fil.write_text('{"annen kjoering": true}', encoding="utf-8")
            return falsk_serie()

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(tmp_path, tmp_path / "ose.db", self.OEYEBLIKK, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert fil.read_text(encoding="utf-8") == '{"annen kjoering": true}'
        assert any(
            "ikke skrevet over" in l and f"{KALL} kall er brukt" in l
            for l in linjer
        )


class TestSvarMedFeilForm:
    """Story 2.0, valg A: et svar med feil form stopper ikke hentingen
    (AD-15, NFR-03).

    Story 1.8: «feil form» er alt SnapshotLeser avviser. Seriene kommer fra
    samme liste som testene for leseren bruker (tests/eodhd_serier.py)."""

    @pytest.mark.parametrize("svar", AVVISTE, ids=AVVISTE_IDER)
    def test_feil_form_gir_feil_for_symbolet_og_de_andre_hentes(self, svar):
        def hent(ticker, *_):
            if ticker == "DNB.OL":
                return svar
            return falsk_serie()

        resultat = fp.hent_universet(NOEKKEL, "a", "b", hent, lambda _: None)

        assert resultat.feil == {"DNB": "svar med feil form"}
        assert "DNB" not in resultat.serier
        assert len(resultat.serier) == len(AKSJEUNIVERS) - 1
        assert resultat.kall_brukt == len(AKSJEUNIVERS)

    @pytest.mark.parametrize("svar", AVVISTE, ids=AVVISTE_IDER)
    def test_ingen_aksje_forsvinner_uten_aa_staa_i_feil(self, tmp_path, svar):
        """Det storyen lover: hver aksje i fila hentingen skrev, kan enten
        leses av visningen eller staar i feil. Foer 1.8 ble DNB lagret, uten
        noe i feil, og visningen droppet den."""

        def hent(ticker, *_):
            return svar if ticker == "DNB.OL" else serie_til(TIRSDAG_22_09)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(tmp_path, tmp_path / "ose.db", OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1
        fil = tmp_path / fp.filnavn(TIRSDAG_22_09)
        feil = json.loads(fil.read_text(encoding="utf-8"))["feil"]
        leser = nyeste_leser(tmp_path)

        for aksje in AKSJEUNIVERS:
            kan_leses = leser.serie(aksje.symbol) != []
            assert kan_leses != (aksje.symbol in feil), aksje.symbol
        assert "DNB" in feil

    def test_tom_serie_forsvinner_heller_ikke_uten_aa_staa_i_feil(self, tmp_path):
        """Den tomme serien er ikke i den felles lista. Den gir «tomt svar»,
        og loftet over gjelder ogsaa den."""

        def hent(ticker, *_):
            return [] if ticker == "DNB.OL" else serie_til(TIRSDAG_22_09)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(tmp_path, tmp_path / "ose.db", OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1
        fil = tmp_path / fp.filnavn(TIRSDAG_22_09)
        feil = json.loads(fil.read_text(encoding="utf-8"))["feil"]
        leser = nyeste_leser(tmp_path)

        for aksje in AKSJEUNIVERS:
            kan_leses = leser.serie(aksje.symbol) != []
            assert kan_leses != (aksje.symbol in feil), aksje.symbol
        assert feil == {"DNB": "tomt svar"}


class TestIntervall:
    def test_henter_omtrent_et_aar(self):
        fra, til = fp.bygg_intervall(date(2026, 9, 21))

        assert til == "2026-09-21"
        assert fra == "2025-09-22"

    def test_holder_seg_innenfor_ett_aars_historikk(self):
        """Gratisnivaaet gir ett aar. Et intervall paa 365 dager eller mer
        ville lagt seg utenfor."""
        assert fp.DAGER_TILBAKE < 365

    def test_intervallet_gir_rom_for_ma50(self):
        """51 handelsdager er minimum. Et aar gir rundt 250."""
        handelsdager_anslag = fp.DAGER_TILBAKE * 5 / 7
        assert handelsdager_anslag > fp.MINST_HANDELSDAGER * 3


class TestHentUniverset:
    def test_ett_kall_per_aksje_i_universet(self):
        kall = []

        def hent(ticker, nokkel, fra, til):
            kall.append(ticker)
            return falsk_serie()

        resultat = fp.hent_universet("noekkel", "2025-09-22", "2026-09-21", hent, lambda _: None)

        assert resultat.kall_brukt == len(AKSJEUNIVERS)
        assert len(kall) == len(AKSJEUNIVERS)
        assert kall == [aksje.ticker for aksje in AKSJEUNIVERS]

    def test_henter_alle_femten_og_ikke_de_fem_gamle(self):
        """Lista hadde fem aksjer fra tidlige tester. Den skal foelge universet."""
        hentet = []
        fp.hent_universet(
            "noekkel", "a", "b",
            lambda t, n, f, ti: hentet.append(t) or falsk_serie(),
            lambda _: None,
        )

        assert len(hentet) == len(AKSJEUNIVERS)
        assert "MPCC.OL" in hentet
        assert "SALM.OL" in hentet

    def test_serier_lagres_paa_symbol_ikke_ticker(self):
        """Kursdata slaar opp paa EQNR, ikke EQNR.OL."""
        resultat = fp.hent_universet(
            "noekkel", "a", "b", lambda *_: falsk_serie(), lambda _: None
        )

        assert "EQNR" in resultat.serier
        assert "EQNR.OL" not in resultat.serier

    def test_en_feil_stopper_ikke_de_andre(self, monkeypatch):
        """NFR-03: manglende data for en aksje stopper ikke hovedflyten.

        Story 2.0: gaar gjennom den ekte hent_ett_symbol, med requests.get
        byttet ut. DNB faar en ekte HTTP 500 fra raise_for_status()."""

        def get(url, params, timeout):
            ticker = url.rsplit("/", 1)[1]
            if ticker == "DNB.OL":
                return falsk_respons(500, ticker, params["api_token"])
            return falsk_respons(200, ticker, params["api_token"], falsk_serie())

        monkeypatch.setattr(fp.requests, "get", get)

        resultat = fp.hent_universet(NOEKKEL, "a", "b", skriv=lambda _: None)

        assert "DNB" in resultat.feil
        assert "HTTP 500" in resultat.feil["DNB"]
        assert NOEKKEL not in resultat.feil["DNB"]
        assert len(resultat.serier) == len(AKSJEUNIVERS) - 1

    def test_feilet_symbol_teller_som_brukt_kall(self):
        """Kallet er brukt selv om svaret var ubrukelig. Kvoten maa stemme."""

        def hent(ticker, *_):
            raise RuntimeError("nei")

        resultat = fp.hent_universet("noekkel", "a", "b", hent, lambda _: None)

        assert resultat.kall_brukt == len(AKSJEUNIVERS)
        assert resultat.serier == {}

    def test_feilet_symbol_proeves_ikke_paa_nytt(self):
        """Et nytt forsoek ville kostet et kall til."""
        forsok = []

        def hent(ticker, *_):
            forsok.append(ticker)
            raise RuntimeError("nei")

        fp.hent_universet("noekkel", "a", "b", hent, lambda _: None)

        assert len(forsok) == len(set(forsok))

    def test_tomt_svar_foeres_som_feil_ikke_som_tom_serie(self):
        resultat = fp.hent_universet("noekkel", "a", "b", lambda *_: [], lambda _: None)

        assert resultat.serier == {}
        assert all(grunn == "tomt svar" for grunn in resultat.feil.values())

    def test_raadataene_lagres_uendret(self):
        """Story 1.8: oversettelsen er bare kontrollen. Oeyeblikksbildet har
        samme format som foer, med EODHDs rader slik de kom."""
        svar = {aksje.ticker: falsk_serie() for aksje in AKSJEUNIVERS}
        # Ekstra felt EODHD sender, og som ikke oversettes, skal ogsaa staa.
        svar["DNB.OL"][0]["open"] = 99.0
        # Usortert, saa en henting som sorterer raadataene, ogsaa feiler.
        svar["EQNR.OL"].reverse()
        # En kopi foer kallet: hentingen faar de samme objektene, saa en
        # endring paa stedet ville ellers ogsaa endret det testen sammenligner med.
        forventet = copy.deepcopy(svar)

        resultat = fp.hent_universet(
            "noekkel", "a", "b", lambda ticker, *_: svar[ticker], lambda _: None
        )

        assert resultat.serier == {
            aksje.symbol: forventet[aksje.ticker] for aksje in AKSJEUNIVERS
        }

    def test_utskriften_viser_siste_dato_fra_serien(self):
        """Serien er usortert, saa siste dato maa komme fra den oversatte
        serien, ikke fra siste raa rad."""
        linjer = []
        fp.hent_universet(
            "noekkel", "a", "b", lambda *_: falsk_serie(60)[::-1], linjer.append
        )

        assert any("60 dager, siste 2026-07-30" in linje for linje in linjer)

    def test_kort_serie_merkes_i_utskriften(self):
        """En serie under 51 dager kan ikke gi signal. Det skal vaere synlig."""
        linjer = []
        fp.hent_universet(
            "noekkel", "a", "b", lambda *_: falsk_serie(10), linjer.append
        )

        assert any("for kort for MA50" in linje for linje in linjer)


class TestOyeblikksbilde:
    def test_formatet_kan_leses_av_visningen(self, tmp_path):
        """Det hentingen skriver, skal visningen kunne lese - uten mellomledd.

        Het foer test_formatet_kan_leses_av_snapshotkilde, og leste med
        SnapshotKilde, som godtar alt. Visningen leser gjennom nyeste_leser og
        SnapshotLeser, som krever ISO-datoer i radene og en hentet-tid med
        tidssone. Derfor gaar testen gjennom kjoer, som setter tiden selv,
        og leser fila slik visningen gjoer.
        """
        start = TIRSDAG_22_09 - timedelta(days=59)

        def hent(*_):
            return [
                {
                    "date": (start + timedelta(days=i)).isoformat(),
                    "close": 100.0 + i,
                    "adjusted_close": 100.0 + i,
                    "volume": 1000,
                }
                for i in range(60)
            ]

        fil = fp.kjoer(tmp_path, tmp_path / "ose.db", OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        assert fil is not None and fil.parent == tmp_path

        leser = nyeste_leser(tmp_path)
        assert leser is not None
        for aksje in AKSJEUNIVERS:
            tid = leser.sist_hentet(aksje.symbol)
            assert tid is not None, (
                f"{aksje.symbol}: visningen kan ikke lese hentet-tiden i fila"
            )
            assert len(leser.serie(aksje.symbol)) == 60, (
                f"{aksje.symbol}: visningen leser ikke alle radene hentingen skrev"
            )

    def test_filnavnet_baerer_datoen(self):
        assert fp.filnavn(date(2026, 9, 22)) == "kurser-raa-2026-09-22.json"

    def test_nyeste_snapshot_finner_begge_navnemoenstrene(self, tmp_path):
        """Signaltestens fil og hentingens fil leses likt."""
        (tmp_path / "signaltest-raa-2026-09-21.json").write_text("{}", encoding="utf-8")
        (tmp_path / fp.filnavn(date(2026, 9, 22))).write_text("{}", encoding="utf-8")

        assert nyeste_snapshot(tmp_path).name == "kurser-raa-2026-09-22.json"

    def test_nyeste_velges_paa_dato_ikke_alfabetisk(self, tmp_path):
        """kurser- kommer foer signaltest- alfabetisk. Datoen skal avgjoere."""
        (tmp_path / "kurser-raa-2026-09-20.json").write_text("{}", encoding="utf-8")
        (tmp_path / "signaltest-raa-2026-09-21.json").write_text("{}", encoding="utf-8")

        assert nyeste_snapshot(tmp_path).name == "signaltest-raa-2026-09-21.json"

    def test_feil_foelger_med_i_bildet(self):
        resultat = fp.Resultat(serier={}, feil={"DNB": "HTTP 500"}, kall_brukt=15)
        bilde = fp.lag_oyeblikksbilde(resultat, "a", "b", "naa")

        assert bilde["feil"]["DNB"] == "HTTP 500"
        assert bilde["kilde"] == "EODHD /api/eod"


def test_ingen_test_her_roerer_nettet(monkeypatch):
    """Vakt: gaar en test forbi den injiserte henteren, skal den feile."""
    monkeypatch.setattr(
        fp.requests, "get", lambda *a, **k: pytest.fail("ingen test skal kalle nettet")
    )

    resultat = fp.hent_universet(
        "noekkel", "a", "b", lambda *_: falsk_serie(), lambda _: None
    )
    assert resultat.kall_brukt == len(AKSJEUNIVERS)


# Story 2.1 (AD-20): filnavn og hentet fra samme oeyeblikk. Dagen er norsk
# kalenderdato, hentet er oeyeblikket i UTC med offset. Hver rad er en liste av
# (oeyeblikk i UTC, dato i filnavnet, hentet), fordi to rader i matrisen i
# spesifikasjonen har to oeyeblikk.
def _utc(*deler) -> datetime:
    return datetime(*deler, tzinfo=timezone.utc)


TIDSMATRISE = {
    # Oeyeblikket gitt i Oslo-tid: hentet maa likevel skrives i UTC. Ville
    # feilet hvis kjoer skrev oeyeblikket uten aa regne det om til UTC.
    "00:30 norsk sommertid, gitt i Oslo-tid": [
        (
            datetime(2026, 9, 25, 0, 30, tzinfo=ZoneInfo("Europe/Oslo")),
            "2026-09-25",
            "2026-09-24T22:30:00+00:00",
        ),
    ],
    "00:30 norsk sommertid": [
        (_utc(2026, 9, 24, 22, 30), "2026-09-25", "2026-09-24T22:30:00+00:00"),
    ],
    "like foer midnatt": [
        (_utc(2026, 9, 24, 21, 59, 59), "2026-09-24", "2026-09-24T21:59:59+00:00"),
    ],
    "like etter midnatt": [
        (_utc(2026, 9, 24, 22, 0, 0), "2026-09-25", "2026-09-24T22:00:00+00:00"),
    ],
    "00:30 siste sommertidsdag": [
        (_utc(2026, 10, 24, 22, 30), "2026-10-25", "2026-10-24T22:30:00+00:00"),
    ],
    "02:30 to ganger 25.10": [
        (_utc(2026, 10, 25, 0, 30), "2026-10-25", "2026-10-25T00:30:00+00:00"),
        (_utc(2026, 10, 25, 1, 30), "2026-10-25", "2026-10-25T01:30:00+00:00"),
    ],
    "midnatt i vintertid": [
        (_utc(2026, 10, 25, 22, 59, 59), "2026-10-25", "2026-10-25T22:59:59+00:00"),
        (_utc(2026, 10, 25, 23, 0, 0), "2026-10-26", "2026-10-25T23:00:00+00:00"),
    ],
}


def _kjoer_matrisen(tmp_path, rad):
    """Hvert oeyeblikk i sin egen katalog og sin egen base, saa vakten mot en
    fil som finnes, og basesjekken i story 2.3 ikke stopper det andre
    oeyeblikket i en rad med to. Flagget slipper forbi tidskontrollen, som
    testes for seg. Story 2.3, K8: navnet er boersdagen for den norske
    datoen, mens til-datoen fortsatt er den norske datoen."""
    for nr, (oeyeblikk, dato, hentet) in enumerate(rad):
        katalog = tmp_path / str(nr)
        boersdag = innevaerende_boersdag(date.fromisoformat(dato))
        fil = fp.kjoer(katalog, tmp_path / f"ose-{nr}.db", oeyeblikk, NOEKKEL,
                       lambda *_: serie_til(boersdag), lambda _: None,
                       hent_foer_kl_22=True, les_kvote=nok_kvote)

        assert fil == katalog / f"kurser-raa-{boersdag.isoformat()}.json"
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        # K1: hentet er oeyeblikket, i UTC, som tekst. Teksten sammenlignes,
        # fordi to datetime i ulike soner er like naar oeyeblikket er det samme.
        assert bilde["hentet"] == hentet
        assert datetime.fromisoformat(bilde["hentet"]) == oeyeblikk
        assert norsk_dato(datetime.fromisoformat(bilde["hentet"])).isoformat() == dato
        assert bilde["to"] == dato


class TestBoersdagIOsloTidsstempelIUtc:
    """Story 2.1, K1 og K2: filnavn, til-dato og hentet fra samme oeyeblikk.

    Ville feilet hvis hentet ble lest fra klokka etter hentingen (M1), hvis
    dagen var UTC-dagen (M2), eller hvis hentet sto i Oslo-tid (M7)."""

    @pytest.mark.parametrize("rad", TIDSMATRISE.values(), ids=TIDSMATRISE.keys())
    def test_filnavn_og_hentet_fra_samme_oeyeblikk(self, tmp_path, rad):
        _kjoer_matrisen(tmp_path, rad)

    def test_oeyeblikk_uten_sone_gir_valueerror_foer_vakt_og_kall(self, tmp_path):
        def hent(*_):
            pytest.fail("ingen kall skal brukes naar oeyeblikket mangler sone")

        with pytest.raises(ValueError):
            fp.kjoer(tmp_path, tmp_path / "ose.db", datetime(2026, 9, 25, 0, 30), NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)

        assert list(tmp_path.iterdir()) == []


@pytest.fixture(params=["UTC", "Pacific/Auckland"])
def maskinsone(request):
    """Setter maskinens sone for testen og setter den tilbake etterpaa.

    time.tzset finnes ikke paa Windows, saa der hoppes testene over. I CI
    (Linux) kjoeres de. Ville feilet hvis kjoer leste maskinens sone, for
    eksempel med oeyeblikk.astimezone().date() (M6)."""
    if not hasattr(time, "tzset"):
        pytest.skip("time.tzset finnes ikke her (Windows); TZ-testene kjoeres i CI")
    foer = os.environ.get("TZ")
    os.environ["TZ"] = request.param
    time.tzset()
    try:
        # Uten tidssonedata faller TZ stille tilbake til UTC, og da beviser
        # testene ingenting. Sjekk at sonen faktisk ble satt.
        forskyvning = time.localtime(0).tm_gmtoff
        if request.param == "UTC":
            assert forskyvning == 0
        else:
            assert forskyvning != 0, f"TZ={request.param} ga UTC; mangler tidssonedata?"
        yield request.param
    finally:
        if foer is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = foer
        time.tzset()


class TestMaskinensSoneSpillerIngenRolle:
    """Story 2.1, K6: samme matrise med maskinen i UTC og i Pacific/Auckland."""

    @pytest.mark.parametrize("rad", TIDSMATRISE.values(), ids=TIDSMATRISE.keys())
    def test_filnavn_og_hentet_uavhengig_av_maskinens_sone(self, tmp_path, maskinsone, rad):
        _kjoer_matrisen(tmp_path, rad)

    def test_oeyeblikk_uten_sone_avvises_ogsaa_her(self, tmp_path, maskinsone):
        with pytest.raises(ValueError):
            fp.kjoer(tmp_path, tmp_path / "ose.db", datetime(2026, 9, 25, 0, 30), NOEKKEL,
                lambda *_: pytest.fail("ingen kall"), lambda _: None, les_kvote=nok_kvote,
            )
        assert list(tmp_path.iterdir()) == []


def test_noekkelen_leses_fra_miljoeet_uten_env_fil(tmp_path, monkeypatch):
    """Story 2.2 og AD-12: i en container finnes ingen .env, og nøkkelen
    kommer fra miljøet. Ville feilet hvis den bare ble lest fra fila (M9)."""
    monkeypatch.setattr(fp, "PROSJEKTROT", tmp_path)
    monkeypatch.setenv("EODHD_API_KEY", NOEKKEL)

    assert fp.hent_api_nokkel() == NOEKKEL


def test_uten_noekkel_i_miljoeet_og_uten_env_stopper_hentingen(tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "PROSJEKTROT", tmp_path)
    monkeypatch.delenv("EODHD_API_KEY", raising=False)

    with pytest.raises(SystemExit):
        fp.hent_api_nokkel()


def test_naa_gir_utc_med_offset_null():
    tid = fp.naa()

    assert tid.tzinfo is not None
    assert tid.utcoffset() == timedelta(0)


def test_main_skriver_fila_for_norsk_dato_uten_noekkel(tmp_path, monkeypatch):
    """G12 og K5: main hele veien, uten nett. Falsk noekkel i miljoeet,
    load_dotenv byttet ut, falsk requests.get og klokka satt til 00:30 norsk
    sommertid. Ville feilet hvis main ga kjoer date.today() (M5)."""
    monkeypatch.setenv("EODHD_API_KEY", NOEKKEL)
    monkeypatch.setattr(fp, "load_dotenv", lambda *a, **k: None)
    # Story 2.1b: RAA_KATALOG og BASE_STI i stedet for DATA_KATALOG. Fixturen
    # i conftest.py gjoer det samme; her staar det uttrykkelig.
    raa = tmp_path / "data" / "raa"
    base = tmp_path / "data" / "db" / "ose.db"
    monkeypatch.setattr(lagring_fil, "RAA_KATALOG", raa)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(fp, "naa", lambda: _utc(2026, 9, 24, 22, 30))

    def get(url, params, timeout):
        ticker = url.rsplit("/", 1)[1]
        return falsk_respons(200, ticker, params["api_token"], serie_til(date(2026, 9, 25)))

    monkeypatch.setattr(fp.requests, "get", get)

    # Story 2.3: 00:30 fredag er foer kl. 22:00 paa en boersdag.
    fp.main(["--hent-foer-kl-22"])

    fil = raa / "kurser-raa-2026-09-25.json"
    assert [f.name for f in raa.iterdir()] == [fil.name]
    tekst = fil.read_text(encoding="utf-8")
    assert NOEKKEL not in tekst
    bilde = json.loads(tekst)
    assert len(bilde["serier"]) == len(AKSJEUNIVERS) == 15
    assert bilde["hentet"] == "2026-09-24T22:30:00+00:00"
    # Basen i data/db/, med samme hentet som fila.
    tilkobling = sqlite3.connect(base)
    try:
        lager = SqliteKurslager(tilkobling)
        for aksje in AKSJEUNIVERS:
            assert lager.sist_hentet(aksje.symbol) == _utc(2026, 9, 24, 22, 30)
    finally:
        tilkobling.close()


# Story 2.1b: basen aapnes ett sted, og hentingen skriver kursene dit. Fila
# skrives foerst, saa basen, med samme hentet. Ingen test roerer data/: stiene
# pekes mot tmp_path her og i fixturen i conftest.py.


def serie_til(siste: date, dager: int = 60) -> list[dict]:
    """En serie leseren godtar, som slutter paa en gitt dato."""
    return [
        {
            "date": (siste - timedelta(days=dager - 1 - i)).isoformat(),
            "close": 100.0 + i,
            "adjusted_close": 100.0 + i,
            "volume": 1000,
        }
        for i in range(dager)
    ]


def lager_i(base):
    """Et blikk paa basen gjennom porten. Kalleren lukker tilkoblingen."""
    tilkobling = aapne_base(base)
    return tilkobling, SqliteKurslager(tilkobling)


def antall_rader(base, tabell: str) -> int:
    tilkobling = aapne_base(base)
    try:
        return tilkobling.execute(f"SELECT count(*) FROM {tabell}").fetchone()[0]
    finally:
        tilkobling.close()


def alle_kursrader(base) -> list[tuple]:
    tilkobling = aapne_base(base)
    try:
        return tilkobling.execute("SELECT * FROM kurs ORDER BY symbol, dato").fetchall()
    finally:
        tilkobling.close()


@pytest.fixture
def stier(tmp_path):
    """raa/ og db/ under tmp_path/data, som i prosjektet. Ingen av dem finnes."""
    return tmp_path / "data" / "raa", tmp_path / "data" / "db" / "ose.db"


class TestHentingenSkriverBasen:
    """Story 2.1b, K1, K3, K4 og K9: matrisen i spesifikasjonen."""

    def test_foerste_henting_lager_begge_mappene_og_skriver_15_serier(self, stier):
        """K1 og K3: fila i raa/, basen i db/ose.db, og hver serie i basen har
        samme hentet som fila. Ville feilet hvis hentet kom fra klokka (M5)."""
        raa, base = stier
        fil = fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: serie_til(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)

        assert fil == raa / "kurser-raa-2026-09-22.json"
        assert base.is_file()
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        tilkobling, lager = lager_i(base)
        try:
            for aksje in AKSJEUNIVERS:
                assert lager.sist_hentet(aksje.symbol) == OEYEBLIKK_22_09
                assert lager.sist_hentet(aksje.symbol) == datetime.fromisoformat(bilde["hentet"])
                assert lager.serie(aksje.symbol) == fp.serie_fra_eodhd(
                    bilde["serier"][aksje.symbol]
                )
        finally:
            tilkobling.close()
        assert antall_rader(base, "kursserie") == len(AKSJEUNIVERS) == 15
        # Story 2.5: kjoeringen skriver ogsaa en rad i vurdering per aksje.
        assert antall_rader(base, "vurdering") == 15

    def test_symbol_som_feilet_faar_ingen_rad_i_ny_base(self, stier):
        """K3 og AD-15. Ville feilet hvis symbolet som feilet, ble skrevet (M6)."""
        raa, base = stier

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("nei")
            return serie_til(TIRSDAG_22_09)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1

        tilkobling, lager = lager_i(base)
        try:
            assert lager.serie("DNB") == []
            assert lager.sist_hentet("DNB") is None
            assert lager.sist_hentet("EQNR") == OEYEBLIKK_22_09
        finally:
            tilkobling.close()
        assert antall_rader(base, "kursserie") == len(AKSJEUNIVERS) - 1

    def test_symbol_som_feilet_beholder_gammel_serie_og_tid(self, stier):
        raa, base = stier
        foer = OEYEBLIKK_22_09
        fp.kjoer(raa, base, foer, NOEKKEL, lambda *_: serie_til(date(2026, 9, 22)), lambda _: None, les_kvote=nok_kvote)
        tilkobling, lager = lager_i(base)
        gammel = lager.serie("DNB")
        tilkobling.close()

        etter = foer + timedelta(days=1)

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                return []
            return serie_til(date(2026, 9, 23))

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, etter, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1

        tilkobling, lager = lager_i(base)
        try:
            assert lager.serie("DNB") == gammel
            assert lager.sist_hentet("DNB") == foer
            assert lager.sist_hentet("EQNR") == etter
            assert lager.serie("EQNR")[-1].dato == date(2026, 9, 23)
        finally:
            tilkobling.close()

    def test_basen_kan_ikke_aapnes_fila_staar_og_kode_1(self, stier):
        """K4: base_sti er en mappe. Fila staar, meldingen sier hvordan den
        leses inn, og kjoeringen ender med kode 1. Ville feilet hvis basen
        ble skrevet foer fila (M7)."""
        raa, base = stier
        base.mkdir(parents=True)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: falsk_serie(), linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        fil = raa / "kurser-raa-2026-09-22.json"
        assert len(json.loads(fil.read_text(encoding="utf-8"))["serier"]) == 15
        assert any(f"--les-inn {fil}" in l for l in linjer)
        assert not [l for l in linjer if NOEKKEL in l]

    def _basen_feilet(self, raa, base, linjer, slutt):
        """Det K4 lover: kode 1, fila staar med 15 serier, og meldingen sier
        hvordan den leses inn."""
        assert slutt.value.code == 1
        fil = raa / "kurser-raa-2026-09-22.json"
        assert len(json.loads(fil.read_text(encoding="utf-8"))["serier"]) == 15
        assert any(f"--les-inn {fil}" in l for l in linjer)
        return fil

    def test_basen_feiler_midt_i_skrivingen_fila_staar_og_kode_1(self, stier, monkeypatch):
        """K4 inne i loekka: basen er laast for ett symbol etter at andre er
        skrevet. Meldingen sier hvor mange som alt var skrevet."""
        raa, base = stier

        class Laast(SqliteKurslager):
            def erstatt_serie(self, symbol, rader, hentet):
                if symbol == "KOG":
                    raise sqlite3.OperationalError("database is locked")
                super().erstatt_serie(symbol, rader, hentet)

        monkeypatch.setattr(fp, "SqliteKurslager", Laast)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: falsk_serie(), linjer.append, les_kvote=nok_kvote)

        self._basen_feilet(raa, base, linjer, slutt)
        # EQNR og DNB kommer foer KOG i universet.
        assert any("database is locked" in l and "2 serier var alt skrevet" in l for l in linjer)

    def test_basen_nyere_enn_koden_fila_staar_og_kode_1(self, stier):
        """K4 med MigrasjonsFeil: basen er migrert med en migrasjon koden ikke
        har, saa aapne_base avviser den."""
        raa, base = stier
        katalog = base.parent / "nyere"
        katalog.mkdir(parents=True)
        for migrasjon in lagring_sqlite.MIGRASJONSKATALOG.glob("*.sql"):
            (katalog / migrasjon.name).write_bytes(migrasjon.read_bytes())
        neste = lagring_sqlite.siste_versjon(lagring_sqlite.MIGRASJONSKATALOG) + 1
        (katalog / f"{neste:04d}_ny.sql").write_text("CREATE TABLE ny (x INTEGER);", encoding="utf-8")
        tilkobling = sqlite3.connect(base)
        lagring_sqlite.migrer(tilkobling, katalog)
        tilkobling.close()
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: falsk_serie(), linjer.append, les_kvote=nok_kvote)

        self._basen_feilet(raa, base, linjer, slutt)
        assert any("MigrasjonsFeil" in l for l in linjer)

    def test_ett_symbol_avvist_av_basen_de_andre_skrives(self, stier, monkeypatch):
        raa, base = stier

        class Avvisende(SqliteKurslager):
            def erstatt_serie(self, symbol, rader, hentet):
                if symbol == "DNB":
                    raise ValueError("avvist i testen")
                super().erstatt_serie(symbol, rader, hentet)

        monkeypatch.setattr(fp, "SqliteKurslager", Avvisende)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: falsk_serie(), linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert any("DNB" in l and "avvist i testen" in l for l in linjer)
        tilkobling, lager = lager_i(base)
        try:
            assert lager.sist_hentet("DNB") is None
            assert all(
                lager.sist_hentet(a.symbol) == OEYEBLIKK_22_09
                for a in AKSJEUNIVERS if a.symbol != "DNB"
            )
        finally:
            tilkobling.close()

    def test_fire_dagers_opphold_fylles_med_16_kall(self, stier):
        """K9: basen mangler fire boersdager. Etter neste henting er de der,
        og hentingen brukte 16 kall, 15 aksjer og indeksen (story 2.8). Ville feilet hvis kjoer bare skrev
        symboler som ikke finnes i basen (M12)."""
        raa, base = stier
        # Mandag 21.09, saa fredag 25.09, begge kl. 22 i Oslo: 22.-25. mangler.
        fp.kjoer(raa, base, _utc(2026, 9, 21, 20), NOEKKEL,
                 lambda *_: serie_til(date(2026, 9, 21)), lambda _: None, les_kvote=nok_kvote)
        kall = []

        def hent(ticker, *_):
            kall.append(ticker)
            return serie_til(date(2026, 9, 25), dager=64)

        fp.kjoer(raa, base, _utc(2026, 9, 25, 20), NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)

        assert len(kall) == 16
        tilkobling, lager = lager_i(base)
        try:
            for aksje in AKSJEUNIVERS:
                datoer = {r.dato for r in lager.serie(aksje.symbol)}
                assert {date(2026, 9, d) for d in (22, 23, 24, 25)} <= datoer
                assert lager.sist_hentet(aksje.symbol) == _utc(2026, 9, 25, 20)
        finally:
            tilkobling.close()

    def test_hentingen_og_innlesingen_gaar_samme_vei(self, stier, monkeypatch):
        """K5: begge skriver gjennom skriv_til_basen, med samme hentet."""
        raa, base = stier
        kall = []
        ekte = fp.skriv_til_basen

        # Story 2.3b: kjoer gir ogsaa lista til skriv_til_basen.
        def spion(base_sti, serier, hentet, fil, skriv, *resten):
            kall.append((set(serier), hentet))
            return ekte(base_sti, serier, hentet, fil, skriv, *resten)

        monkeypatch.setattr(fp, "skriv_til_basen", spion)
        fil = fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: serie_til(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)
        fp.les_inn(fil, base, lambda _: None)

        assert len(kall) == 2
        assert kall[0] == kall[1] == ({a.symbol for a in AKSJEUNIVERS}, OEYEBLIKK_22_09)


@pytest.fixture
def uten_noekkel_og_nett(monkeypatch):
    """Innlesingen leser ingen noekkel og gjoer ingen kall. Alt som ville
    gjort det, feiler testen."""
    monkeypatch.delenv("EODHD_API_KEY", raising=False)
    monkeypatch.setattr(fp, "hent_api_nokkel", lambda: pytest.fail("noekkelen ble lest"))
    monkeypatch.setattr(fp, "load_dotenv", lambda *a, **k: pytest.fail(".env ble lest"))
    monkeypatch.setattr(fp, "hent_ett_symbol", lambda *a: pytest.fail("et kall ble gjort"))
    monkeypatch.setattr(fp.requests, "get", lambda *a, **k: pytest.fail("et kall ble gjort"))


def lag_bilde(katalog, hentet: datetime, siste: date = date(2026, 9, 22)):
    """Et oeyeblikksbilde med 15 serier, i formatet kjoer skriver."""
    katalog.mkdir(parents=True, exist_ok=True)
    resultat = fp.Resultat(
        serier={a.symbol: serie_til(siste) for a in AKSJEUNIVERS}, kall_brukt=15
    )
    fil = katalog / fp.filnavn(norsk_dato(hentet))
    bilde = fp.lag_oyeblikksbilde(resultat, "a", siste.isoformat(), hentet.isoformat())
    fil.write_text(json.dumps(bilde), encoding="utf-8")
    return fil


class TestInnlesing:
    """Story 2.1b, K5 og K6: et oeyeblikksbilde som finnes, inn i basen uten kall."""

    def test_innlesing_gir_15_serier_uten_vurdering_noekkel_eller_kall(
        self, stier, uten_noekkel_og_nett
    ):
        """Ville feilet hvis innlesingen leste noekkelen (M8)."""
        raa, base = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)
        linjer = []

        fp.les_inn(fil, base, linjer.append)

        tilkobling, lager = lager_i(base)
        try:
            for aksje in AKSJEUNIVERS:
                assert lager.sist_hentet(aksje.symbol) == OEYEBLIKK_22_09
                assert len(lager.serie(aksje.symbol)) == 60
        finally:
            tilkobling.close()
        assert antall_rader(base, "vurdering") == 0
        # Regel 16: ingen kurser i utskriften, bare antall, symboler og datoer.
        # Hver close, adjusted_close og volume i fila, i tekstformen den ville
        # blitt skrevet ut i.
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        verdier = {
            str(rad[felt])
            for serie in bilde["serier"].values()
            for rad in serie
            for felt in ("close", "adjusted_close", "volume")
        }
        assert verdier
        assert not [(l, v) for l in linjer for v in verdier if v in l]
        assert any("15 serier" in l for l in linjer)

    def test_main_med_les_inn_skriver_til_base_sti(self, stier, uten_noekkel_og_nett):
        """Flagget gaar til les_inn, og BASE_STI slaas opp naar main kalles."""
        raa, _ = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)

        fp.main(["--les-inn", str(fil)])

        tilkobling, lager = lager_i(lagring_sqlite.BASE_STI)
        try:
            assert lager.sist_hentet("EQNR") == OEYEBLIKK_22_09
        finally:
            tilkobling.close()

    def test_innlesing_to_ganger_gir_samme_innhold(self, stier):
        raa, base = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)

        fp.les_inn(fil, base, lambda _: None)
        foer = alle_kursrader(base)
        fp.les_inn(fil, base, lambda _: None)

        assert alle_kursrader(base) == foer
        assert len(foer) == 15 * 60

    def test_eldre_oeyeblikksbilde_hopper_over_symbolet_og_gir_kode_1(self, stier):
        """K6, svar A: DNB i basen er nyere enn fila. DNB hoppes over med en
        melding som nevner fila, symbolet og begge tidene, de andre skrives,
        og kjoeringen ender med kode 1. Ville feilet uten sammenligningen (M9)."""
        raa, base = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)
        fp.les_inn(fil, base, lambda _: None)
        nyere = OEYEBLIKK_22_09 + timedelta(days=1)
        tilkobling, lager = lager_i(base)
        lager.erstatt_serie("DNB", fp.serie_fra_eodhd(serie_til(date(2026, 9, 23))), nyere)
        tilkobling.close()
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.les_inn(fil, base, linjer.append)

        assert slutt.value.code == 1
        melding = [l for l in linjer if "DNB" in l and "hoppet over" in l]
        assert len(melding) == 1
        assert fil.name in melding[0]
        assert OEYEBLIKK_22_09.isoformat() in melding[0]
        assert nyere.isoformat() in melding[0]
        tilkobling, lager = lager_i(base)
        try:
            assert lager.sist_hentet("DNB") == nyere
            assert lager.serie("DNB")[-1].dato == date(2026, 9, 23)
            assert lager.sist_hentet("EQNR") == OEYEBLIKK_22_09
        finally:
            tilkobling.close()

    @staticmethod
    def _endret_bilde(raa, endring):
        fil = lag_bilde(raa, OEYEBLIKK_22_09)
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        endring(bilde)
        fil.write_text(json.dumps(bilde), encoding="utf-8")
        return fil

    def _de_femten_skrevet(self, base, uten=()):
        tilkobling, lager = lager_i(base)
        try:
            for aksje in AKSJEUNIVERS:
                if aksje.symbol in uten:
                    assert lager.sist_hentet(aksje.symbol) is None
                else:
                    assert lager.sist_hentet(aksje.symbol) == OEYEBLIKK_22_09
        finally:
            tilkobling.close()

    def test_symbol_utenfor_universet_nevnes_og_gir_kode_1(self, stier):
        raa, base = stier
        fil = self._endret_bilde(
            raa, lambda b: b["serier"].__setitem__("EQNR.OL", serie_til(date(2026, 9, 22)))
        )
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.les_inn(fil, base, linjer.append)

        assert slutt.value.code == 1
        assert any("EQNR.OL" in l and "ikke skrevet" in l for l in linjer)
        self._de_femten_skrevet(base)

    def test_serie_som_ikke_kan_leses_nevnes_og_gir_kode_1(self, stier):
        raa, base = stier

        def oedelegg(bilde):
            bilde["serier"]["DNB"][3]["close"] = "ikke et tall"

        fil = self._endret_bilde(raa, oedelegg)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.les_inn(fil, base, linjer.append)

        assert slutt.value.code == 1
        assert any("DNB" in l and "kan ikke leses" in l for l in linjer)
        self._de_femten_skrevet(base, uten={"DNB"})

    def test_hentet_null_gir_kode_1_og_ingen_base(self, stier):
        raa, base = stier
        fil = self._endret_bilde(raa, lambda b: b.__setitem__("hentet", None))
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.les_inn(fil, base, linjer.append)

        assert slutt.value.code == 1
        assert any("hentet i fila" in l and "kan ikke leses" in l for l in linjer)
        assert not [l for l in linjer if "serien i fila" in l]
        assert not base.exists()

    def test_fil_som_ikke_kan_leses_gir_kode_1_og_ingen_base(self, stier):
        raa, base = stier
        raa.mkdir(parents=True)
        fil = raa / "kurser-raa-2026-09-22.json"
        fil.write_text("ikke json", encoding="utf-8")

        with pytest.raises(SystemExit) as slutt:
            fp.les_inn(fil, base, lambda _: None)

        assert slutt.value.code == 1
        assert not base.exists()


# Story 2.5: vurderingen skrives i samme kjoering. Hver test leser radene
# tilbake med Vurderingslager.les fra en base paa disk.

TIRSDAG_22_09 = date(2026, 9, 22)


def serie_med_utslag(siste: date, dager: int = 60) -> list[dict]:
    """Som serie_til, men siste dag stiger mer og har tre ganger volumet, saa
    verdiene skiller seg fra serie_til og sjekkene gir utslag."""
    serie = serie_til(siste, dager)
    serie[-1] = {**serie[-1], "close": 180.0, "adjusted_close": 180.0, "volume": 3000}
    return serie


def vurderingene(base, dato: date, klokke: datetime = OEYEBLIKK_22_09) -> dict:
    """Radene for dato gjennom porten, og seriene i basen, per symbol."""
    tilkobling = aapne_base(base)
    try:
        lager = SqliteVurderingslager(tilkobling, lambda: klokke)
        kurslager = SqliteKurslager(tilkobling)
        return {
            a.symbol: (lager.les(a.symbol, dato), kurslager.serie(a.symbol))
            for a in AKSJEUNIVERS
        }
    finally:
        tilkobling.close()


def datoene_i_vurdering(base) -> list[str]:
    tilkobling = aapne_base(base)
    try:
        return [r[0] for r in tilkobling.execute("SELECT DISTINCT dato FROM vurdering")]
    finally:
        tilkobling.close()


class TestVurderingenISammeKjoering:
    """Story 2.5, K1-K13 i spesifikasjonen."""

    def test_en_kjoering_skriver_kurser_og_vurderinger_for_alle_femten(self, stier):
        """K1: 15 serier og 15 vurderinger, lest tilbake fra en base paa disk,
        med maalingene fra Signal av serien i basen. Ville feilet hvis
        standardavvik og dagens_endring var byttet om (M1)."""
        raa, base = stier
        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                 lambda *_: serie_med_utslag(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)

        rader = vurderingene(base, TIRSDAG_22_09)
        assert antall_rader(base, "vurdering") == 15
        for symbol, (innhold, serie) in rader.items():
            assert isinstance(innhold, Vurdering), symbol
            assert innhold.styrke > 0, symbol
            assert serie[-1].dato == TIRSDAG_22_09
            signal = beregn_signal(serie)
            trend_sjekk, bevegelse_sjekk, interesse_sjekk = signal.sjekker
            assert (innhold.styrke, innhold.retning) == (signal.styrke, signal.retning)
            assert (innhold.trend, innhold.bevegelse, innhold.interesse) == (
                trend_sjekk.verdi, bevegelse_sjekk.verdi, interesse_sjekk.verdi
            )
            assert innhold.trend_avvik == trend_sjekk.maaling
            assert innhold.dagens_endring == bevegelse_sjekk.maaling
            assert innhold.standardavvik == bevegelse_sjekk.grense
            assert innhold.volumforhold == interesse_sjekk.maaling
            assert innhold.slutt == serie[-1].slutt
            assert innhold.justert_slutt == serie[-1].justert_slutt

    def test_vurderingen_er_regnet_av_serien_kjoeringen_selv_lagret(self, stier, monkeypatch):
        """K2: basen har en serie fra en tidligere kjoering samme dag. Den nye
        kjoeringen vurderer den nye serien. Ville feilet hvis vurderingen ble
        regnet foer kursene var skrevet (M2)."""
        raa, base = stier
        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                 lambda *_: serie_til(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)
        (raa / "kurser-raa-2026-09-22.json").unlink()
        senere = OEYEBLIKK_22_09 + timedelta(minutes=30)
        # Story 2.3: basesjekken ville stoppet kjoering nummer to, fordi basen
        # har dagen. Den slaas av her, som et nytt forsoek i 2.3b.
        monkeypatch.setattr(fp, "manglende_i_basen", lambda *_: ["alle"])

        fp.kjoer(raa, base, senere, NOEKKEL,
                 lambda *_: serie_med_utslag(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)

        for symbol, (innhold, serie) in vurderingene(base, TIRSDAG_22_09, senere).items():
            assert serie == fp.serie_fra_eodhd(serie_med_utslag(TIRSDAG_22_09))
            assert innhold == vurder(serie, TIRSDAG_22_09), symbol
            assert innhold != vurder(fp.serie_fra_eodhd(serie_til(TIRSDAG_22_09)), TIRSDAG_22_09)

    def test_symbol_som_feilet_i_hentingen_faar_en_rad_med_grunn(self, stier):
        """K3 og AD-15. Ville feilet hvis et feilet symbol ikke fikk rad (M3)."""
        raa, base = stier

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("nei")
            return serie_til(TIRSDAG_22_09)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1

        rader = vurderingene(base, TIRSDAG_22_09)
        assert rader["DNB"] == (Grunn.SYMBOL_FEILET, [])
        assert all(isinstance(v, Vurdering) for s, (v, _) in rader.items() if s != "DNB")

    def test_symbol_avvist_av_basen_faar_en_rad_med_grunn(self, stier, monkeypatch):
        """K3: serien ble ikke lagret, saa symbolet regnes som feilet. De
        andre faar vurdering, og kjoeringen ender med kode 1."""
        raa, base = stier

        class Avvisende(SqliteKurslager):
            def erstatt_serie(self, symbol, rader, hentet):
                if symbol == "DNB":
                    raise ValueError("avvist i testen")
                super().erstatt_serie(symbol, rader, hentet)

        monkeypatch.setattr(fp, "SqliteKurslager", Avvisende)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                     lambda *_: serie_til(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        rader = vurderingene(base, TIRSDAG_22_09)
        assert rader["DNB"][0] == Grunn.SYMBOL_FEILET
        assert sum(isinstance(v, Vurdering) for v, _ in rader.values()) == 14

    def test_nyeste_kurs_ikke_fra_dagen_gir_en_rad_med_grunn(self, stier):
        """K4: EQNR har ingen kurs for 22.09. Ville feilet hvis vurderingen
        ble regnet av gaarsdagens kurs (M4)."""
        raa, base = stier

        def hent(ticker, *_):
            siste = date(2026, 9, 21) if ticker == "EQNR.OL" else TIRSDAG_22_09
            return serie_til(siste)

        # Story 2.3, FR-402: svaret mangler dagens kurs for EQNR. Raden med
        # grunn skrives, utskriften nevner EQNR, og kjoeringen gir kode 1.
        linjer = []
        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, linjer.append,
                     les_kvote=nok_kvote)
        assert slutt.value.code == 1

        rader = vurderingene(base, TIRSDAG_22_09)
        assert rader["EQNR"][0] == Grunn.KURS_IKKE_FRA_DAGEN
        assert isinstance(rader["DNB"][0], Vurdering)

    def test_signal_som_ikke_kan_regnes_gir_en_rad_med_grunn(self, stier):
        """K5: 30 dager er for kort for MA50. Ville feilet hvis ValueError fra
        beregn_signal ikke ble fanget (M5)."""
        raa, base = stier

        def hent(ticker, *_):
            return serie_til(TIRSDAG_22_09, dager=30 if ticker == "KOG.OL" else 60)

        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)

        rader = vurderingene(base, TIRSDAG_22_09)
        assert rader["KOG"][0] == Grunn.SIGNAL_IKKE_REGNET
        assert len(rader["KOG"][1]) == 30
        assert isinstance(rader["EQNR"][0], Vurdering)

    def test_to_kjoeringer_samme_dag_gir_en_vurdering_per_aksje(self, stier):
        """K6: den andre kjoeringen stopper ved filvakten foer noe kall, og
        radene er de samme."""
        raa, base = stier
        hent = lambda *_: serie_med_utslag(TIRSDAG_22_09)  # noqa: E731
        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
        foer = vurderingene(base, TIRSDAG_22_09)
        kall = []

        assert fp.kjoer(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=5), NOEKKEL,
                        lambda *a: kall.append(a), lambda _: None, les_kvote=nok_kvote) is None

        assert kall == []
        assert antall_rader(base, "vurdering") == 15
        assert vurderingene(base, TIRSDAG_22_09) == foer

    def test_grunn_skriver_ikke_over_vurderingen_fra_tidligere_i_dag(self, stier, monkeypatch):
        """K6 og punkt 24: fila er borte, og DNB feiler i kjoering nummer to.
        Vurderingen fra den foerste staar, og utskriften sier det. Ville
        feilet hvis upserten skrev en grunn over en vurdering (M6)."""
        raa, base = stier
        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                 lambda *_: serie_med_utslag(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)
        dnb_foer = vurderingene(base, TIRSDAG_22_09)["DNB"][0]
        (raa / "kurser-raa-2026-09-22.json").unlink()
        # Story 2.3: basesjekken ville stoppet kjoering nummer to, fordi basen
        # har dagen. Den slaas av her, som et nytt forsoek i 2.3b.
        monkeypatch.setattr(fp, "manglende_i_basen", lambda *_: ["alle"])

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("nei")
            return serie_til(TIRSDAG_22_09)

        linjer = []
        senere = OEYEBLIKK_22_09 + timedelta(minutes=30)
        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, senere, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1

        assert antall_rader(base, "vurdering") == 15
        assert isinstance(dnb_foer, Vurdering)
        assert vurderingene(base, TIRSDAG_22_09, senere)["DNB"][0] == dnb_foer
        assert any("sto fra foer" in l and "DNB" in l for l in linjer)

    @staticmethod
    def _klokke(*tider):
        """En klokke som gir tidene etter tur, og den siste resten av tiden."""
        tider = list(tider)

        def klokke():
            return tider.pop(0) if len(tider) > 1 else tider[0]

        return klokke

    def test_midnatt_midt_i_universet_stopper_og_sier_fra(self, stier):
        """K7: klokka gaar over midnatt i Oslo etter to rader. Kjoeringen
        stopper med kode 1, sier fra, og ingen rad faar neste dag. Ville
        feilet hvis datoen ble lest paa nytt for hvert symbol (M7), eller
        hvis ValueError fra skriv ikke ble fanget (M8b).

        Klokka leses en gang i kjoer foer vurderingene og en gang per skriv i
        SqliteVurderingslager. Tre lesinger foer midnatt gir derfor to rader.
        Leser koden klokka oftere, flytter punktet seg, og testen maa telles
        paa nytt."""
        raa, base = stier
        start = _utc(2026, 9, 22, 21, 59, 50)   # 23:59:50 i Oslo
        klokke = self._klokke(start, start, start, _utc(2026, 9, 22, 22, 0, 10))
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, start, NOEKKEL, lambda *_: serie_til(TIRSDAG_22_09),
                     linjer.append, klokke=klokke, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert datoene_i_vurdering(base) == ["2026-09-22"]
        assert antall_rader(base, "vurdering") == 2
        assert any("midnatt" in l and "etter 2 rader" in l for l in linjer)
        assert antall_rader(base, "kursserie") == 15

    def test_midnatt_foer_vurderingene_stopper_ogsaa_fredag(self, stier):
        """K7: fredag 25.09 kl. 23:59 til loerdag. Lageret ville godtatt
        fredagen, som fortsatt er inneveerende boersdag, men kjoeringen
        stopper fordi dagen er en annen enn oeyeblikkets. Ville feilet hvis
        sjekken foer vurderingene var fjernet (M8a)."""
        raa, base = stier
        start = _utc(2026, 9, 25, 21, 59, 50)
        klokke = self._klokke(_utc(2026, 9, 25, 22, 0, 10))
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, start, NOEKKEL, lambda *_: serie_til(date(2026, 9, 25)),
                     linjer.append, klokke=klokke, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert antall_rader(base, "vurdering") == 0
        assert any("midnatt" in l and "etter 0 rader" in l for l in linjer)

    def test_main_gir_kjoeringen_den_ekte_klokka(self, tmp_path, monkeypatch):
        """K7 gjennom main: naa leses for oeyeblikket og igjen foer
        vurderingene. Ville feilet hvis main ikke ga kjoer klokka."""
        monkeypatch.setenv("EODHD_API_KEY", NOEKKEL)
        monkeypatch.setattr(fp, "load_dotenv", lambda *a, **k: None)
        raa = tmp_path / "data" / "raa"
        base = tmp_path / "data" / "db" / "ose.db"
        monkeypatch.setattr(lagring_fil, "RAA_KATALOG", raa)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(fp, "naa", self._klokke(
            _utc(2026, 9, 22, 21, 59, 50), _utc(2026, 9, 22, 22, 0, 10)
        ))

        def get(url, params, timeout):
            ticker = url.rsplit("/", 1)[1]
            return falsk_respons(200, ticker, params["api_token"], serie_til(TIRSDAG_22_09))

        monkeypatch.setattr(fp.requests, "get", get)

        with pytest.raises(SystemExit) as slutt:
            fp.main([])

        assert slutt.value.code == 1
        assert antall_rader(base, "vurdering") == 0
        assert antall_rader(base, "kursserie") == 15

    def test_innlesing_skriver_aldri_vurdering(self, stier, monkeypatch):
        """K8 og AD-7: basen har dagens vurderinger. --les-inn av samme fil
        gjennom main endrer ingen rad og skriver ingen ny. Ville feilet hvis
        innlesingen skrev vurderinger (M9)."""
        raa, base = stier
        fil = fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                       lambda *_: serie_med_utslag(TIRSDAG_22_09), lambda _: None, les_kvote=nok_kvote)
        foer = vurderingene(base, TIRSDAG_22_09)
        tilkobling = aapne_base(base)
        try:
            tilkobling.execute("DELETE FROM vurdering WHERE symbol = 'DNB'")
            tilkobling.commit()
        finally:
            tilkobling.close()
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(fp, "hent_api_nokkel", lambda: pytest.fail("noekkelen ble lest"))
        monkeypatch.setattr(fp.requests, "get", lambda *a, **k: pytest.fail("et kall ble gjort"))

        fp.main(["--les-inn", str(fil)])
        fp.les_inn(fil, base, lambda _: None)

        etter = vurderingene(base, TIRSDAG_22_09)
        assert etter["DNB"][0] is None
        assert {s: v for s, (v, _) in etter.items() if s != "DNB"} == {
            s: v for s, (v, _) in foer.items() if s != "DNB"
        }
        assert antall_rader(base, "vurdering") == 14

    def test_utskriften_har_antall_dag_og_grunner_men_ingen_kurser(self, stier):
        """K9 og regel 16: antall rader, boersdagen, antall med grunn og
        symbolene med grunnen. Ingen kurs, intet volum og ingen maaling i
        utskriften. Ville feilet hvis slutt sto i linjen (M10)."""
        raa, base = stier

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("nei")
            return serie_med_utslag(TIRSDAG_22_09)

        linjer = []
        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)
        # Story 2.3b, svar 5 (ECH1): en aksje som feilet, gir kode 1.
        assert slutt.value.code == 1
        fil = raa / fp.filnavn(TIRSDAG_22_09)

        assert any(
            "Skrev 15 rader i vurdering for boersdagen 2026-09-22" in l
            and "14 vurderinger og 1 med grunn" in l
            for l in linjer
        )
        assert any("Med grunn: DNB (symbol_feilet)" in l for l in linjer)
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        verdier = {
            str(rad[felt])
            for serie in bilde["serier"].values()
            for rad in serie
            for felt in ("close", "adjusted_close", "volume")
        }
        for innhold, _ in vurderingene(base, TIRSDAG_22_09).values():
            if isinstance(innhold, Vurdering):
                verdier |= {
                    str(getattr(innhold, felt)) for felt in (
                        "slutt", "justert_slutt", "trend_avvik", "dagens_endring",
                        "standardavvik", "volumforhold",
                    )
                }
        assert verdier
        assert not [(l, v) for l in linjer for v in verdier if v in l]

    def test_basen_feiler_ingen_vurdering_og_kode_1(self, stier, monkeypatch):
        """K10: basen feiler midt i kursene. Ingen vurdering skrives, og
        meldingen sier at dagen ikke kan fylles inn. Ville feilet hvis
        vurderingene ble skrevet likevel (M11)."""
        raa, base = stier

        class Laast(SqliteKurslager):
            def erstatt_serie(self, symbol, rader, hentet):
                if symbol == "KOG":
                    raise sqlite3.OperationalError("database is locked")
                super().erstatt_serie(symbol, rader, hentet)

        monkeypatch.setattr(fp, "SqliteKurslager", Laast)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                     lambda *_: serie_til(TIRSDAG_22_09), linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert antall_rader(base, "vurdering") == 0
        assert any("Ingen vurdering er skrevet for 2026-09-22" in l for l in linjer)

    def test_basen_feiler_midt_i_vurderingene_kode_1_og_melding(self, stier, monkeypatch):
        """K10 og G11: basen er laast for den tredje vurderingen. To rader
        staar, kjoeringen sier fra uten traceback og ender med kode 1. Ville
        feilet hvis sqlite3-feilen slapp ut (M14), eller hvis kjoeringen
        endte med kode 0 (M15)."""
        raa, base = stier

        class Laast(SqliteVurderingslager):
            def skriv(self, symbol, dato, innhold):
                if symbol == "KOG":
                    raise sqlite3.OperationalError("database is locked")
                return super().skriv(symbol, dato, innhold)

        monkeypatch.setattr(fp, "SqliteVurderingslager", Laast)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                     lambda *_: serie_til(TIRSDAG_22_09), linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert antall_rader(base, "vurdering") == 2
        assert antall_rader(base, "kursserie") == 15
        assert any(
            "feilet etter 2 vurderinger" in l and "database is locked" in l for l in linjer
        )

    def test_basen_kan_ikke_aapnes_for_vurderingene_kode_1(self, stier, monkeypatch):
        """K10 og G11: basen aapnes for kursene, men ikke for vurderingene.
        Ingen rad, en melding og kode 1."""
        raa, base = stier
        aapne = fp.aapne_base
        kall = []

        def aapne_en_gang(sti):
            kall.append(sti)
            if len(kall) > 1:
                raise sqlite3.OperationalError("unable to open database file")
            return aapne(sti)

        monkeypatch.setattr(fp, "aapne_base", aapne_en_gang)
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL,
                     lambda *_: serie_til(TIRSDAG_22_09), linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert antall_rader(base, "vurdering") == 0
        assert antall_rader(base, "kursserie") == 15
        assert any("kunne ikke aapnes for vurderingene" in l for l in linjer)

    def test_stengt_dag_skriver_raden_for_inneveerende_boersdag(self, stier):
        """K11, svar 1: en kjoering loerdag 26.09 uten rad fra foer skriver
        fredagens rad, og utskriften sier hvilken dag den gjelder."""
        raa, base = stier
        loerdag = _utc(2026, 9, 26, 20, 0)
        fredag = date(2026, 9, 25)
        linjer = []

        fp.kjoer(raa, base, loerdag, NOEKKEL, lambda *_: serie_til(fredag), linjer.append, les_kvote=nok_kvote)

        assert datoene_i_vurdering(base) == ["2026-09-25"]
        rader = vurderingene(base, fredag, loerdag)
        assert all(isinstance(v, Vurdering) for v, _ in rader.values())
        assert any(
            "boersdagen 2026-09-25 (boersen er stengt 2026-09-26)" in l for l in linjer
        )

    def test_stengt_dag_lar_raden_fra_foer_staa(self, stier, monkeypatch):
        """K12, svar 1: fredagens rad finnes fra fredag kveld. Loerdagens
        kjoering skriver den ikke om, og utskriften sier det. Ville feilet
        hvis raden ble skrevet over (M12)."""
        raa, base = stier
        fredag = date(2026, 9, 25)
        fp.kjoer(raa, base, _utc(2026, 9, 25, 20, 0), NOEKKEL,
                 lambda *_: serie_til(fredag), lambda _: None, les_kvote=nok_kvote)
        loerdag = _utc(2026, 9, 26, 20, 0)
        foer = vurderingene(base, fredag, loerdag)
        linjer = []
        # Story 2.3: loerdagens fil heter som fredagens (K8), og basen har
        # fredagen. Begge vaktene slaas av her, som et nytt forsoek i 2.3b.
        (raa / "kurser-raa-2026-09-25.json").unlink()
        monkeypatch.setattr(fp, "manglende_i_basen", lambda *_: ["alle"])

        fp.kjoer(raa, base, loerdag, NOEKKEL,
                 lambda *_: serie_med_utslag(fredag), linjer.append, les_kvote=nok_kvote)

        etter = vurderingene(base, fredag, loerdag)
        assert {s: v for s, (v, _) in etter.items()} == {s: v for s, (v, _) in foer.items()}
        assert etter["EQNR"][1] == fp.serie_fra_eodhd(serie_med_utslag(fredag))
        assert any("Skrev 0 rader" in l for l in linjer)
        assert any("sto fra foer" in l and "EQNR" in l for l in linjer)

    def test_utenfor_kalenderen_stopper_foer_foerste_kall(self, stier):
        """K13, svar 2: 2027 er ikke foert inn. Kjoeringen stopper med 0 kall,
        uten fil og uten base, og sier at dagene maa foeres inn. Ville feilet
        hvis datoen ble regnet etter kallene (M13)."""
        raa, base = stier
        kall = []
        linjer = []

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, _utc(2027, 1, 4, 21, 0), NOEKKEL,
                     lambda *a: kall.append(a), linjer.append, les_kvote=nok_kvote)

        assert slutt.value.code == 1
        assert kall == []
        assert not base.exists()
        assert not raa.exists() or list(raa.iterdir()) == []
        assert any("2027" in l and "stengt" in l and "0 kall" in l for l in linjer)


# Story 2.3: boersdagskontrollen foer kvoten brukes. Rekkefoelgen foer foerste
# kall er klokka, tidskontrollen, basen, filvakten, noekkelen og kvoten.

FREDAG_25_09 = date(2026, 9, 25)
LOERDAG_26_09_KL_12 = _utc(2026, 9, 26, 10, 0)


def ingen_noekkel():
    pytest.fail("noekkelen skal ikke leses naar kjoeringen stopper foer den")


def ingen_kall(*_):
    pytest.fail("ingen kall skal brukes")


def kvote(brukt=0, dato="2026-09-22", grense=20, bonus=0, **mer):
    def les(_noekkel):
        return {"apiRequests": brukt, "apiRequestsDate": dato,
                "dailyRateLimit": grense, "extraLimit": bonus, **mer}
    return les


def kjoer_23(raa, base, oeyeblikk, hent=None, nokkel=NOEKKEL, les_kvote=nok_kvote, **kw):
    """kjoer med utskriften samlet og kallene talt."""
    linjer, kall = [], []

    def tell(ticker, *a):
        kall.append(ticker)
        return (hent or (lambda *_: serie_til(norsk_dato(oeyeblikk))))(ticker, *a)

    fil = fp.kjoer(raa, base, oeyeblikk, nokkel, tell, linjer.append,
                   les_kvote=les_kvote, **kw)
    return fil, kall, "\n".join(linjer)


def kjoer_23_kode(raa, base, oeyeblikk, hent=None, nokkel=NOEKKEL, les_kvote=nok_kvote, **kw):
    """Som kjoer_23, for en kjoering som skal avslutte: (kode, kall, utskrift)."""
    linjer, kall = [], []

    def tell(ticker, *a):
        kall.append(ticker)
        return (hent or (lambda *_: serie_til(norsk_dato(oeyeblikk))))(ticker, *a)

    with pytest.raises(SystemExit) as slutt:
        fp.kjoer(raa, base, oeyeblikk, nokkel, tell, linjer.append,
                 les_kvote=les_kvote, **kw)
    return slutt.value.code, kall, "\n".join(linjer)


class TestTidskontrollen:
    """Foer kl. 22:00 paa en boersdag: 0 kall, med mindre flagget er gitt."""

    def test_boersdag_foer_kl_22_gir_0_kall_og_nevner_flagget(self, stier):
        """Ville feilet uten tidskontrollen (M1) eller med noekkelen lest
        foerst (M5)."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, _utc(2026, 9, 22, 19, 59, 59),
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
        assert "--hent-foer-kl-22" in ut and "0 kall brukt" in ut
        assert not raa.exists() and not base.exists()

    def test_kl_22_presis_henter(self, stier):
        """Grensen er 22:00, ikke 22:01. Ville feilet med <= (M2)."""
        raa, base = stier
        fil, kall, _ = kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert fil == raa / "kurser-raa-2026-09-22.json"
        assert len(kall) == KALL

    def test_flagget_henter_foer_kl_22_med_dagens_navn(self, stier):
        """Ville feilet hvis flagget ble ignorert (M6)."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, _utc(2026, 9, 22, 10, 0),
                                 hent_foer_kl_22=True)
        assert fil == raa / "kurser-raa-2026-09-22.json"
        assert len(kall) == KALL
        assert "--hent-foer-kl-22" in ut

    def test_dag_som_ikke_er_boersdag_har_ingen_tidskontroll(self, stier):
        """Loerdag kl. 12: basen avgjoer. Ville feilet hvis tidskontrollen
        gjaldt alle dager (M7)."""
        raa, base = stier
        fil, kall, _ = kjoer_23(raa, base, LOERDAG_26_09_KL_12,
                                lambda *_: serie_til(FREDAG_25_09))
        assert fil == raa / "kurser-raa-2026-09-25.json"
        assert len(kall) == KALL

    def test_main_gir_flagget_videre_og_godtar_ikke_forkortelse(self, monkeypatch):
        sett = {}
        monkeypatch.setattr(fp, "kjoer", lambda *a, **kw: sett.update(kw))
        monkeypatch.setattr(fp, "naa", lambda: OEYEBLIKK_22_09)

        fp.main(["--hent-foer-kl-22"])
        assert sett["hent_foer_kl_22"] is True
        fp.main([])
        assert sett["hent_foer_kl_22"] is False
        with pytest.raises(SystemExit) as stopp:
            fp.main(["--hent"])
        assert stopp.value.code == 2

    def test_main_gir_noekkelen_som_funksjon(self, monkeypatch):
        """Noekkelen leses i kjoer, etter filvakten, ikke i main."""
        sett = []
        monkeypatch.setattr(fp, "kjoer", lambda *a, **kw: sett.append(a))
        monkeypatch.setattr(fp, "hent_api_nokkel", ingen_noekkel)
        fp.main([])
        assert sett[0][3] is ingen_noekkel


class TestBasenAvgjoer:
    """FR-402: har basen boersdagen for alle aksjene, hentes ingenting."""

    def test_basen_har_dagen_gir_0_kall(self, stier):
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        (raa / "kurser-raa-2026-09-22.json").unlink()

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30),
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
        assert "2026-09-22" in ut and "FR-402" in ut and "0 kall brukt" in ut

    def test_basen_mangler_en_aksje_og_da_hentes_det(self, stier):
        """Ville feilet hvis det holdt at en aksje hadde dagen (M3)."""
        raa, base = stier

        def uten_dnb(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("nei")
            return serie_til(TIRSDAG_22_09)

        # Story 2.3b, svar 5 (ECH1): DNB feilet, saa kode 1.
        assert kjoer_23_kode(raa, base, OEYEBLIKK_22_09, uten_dnb)[0] == 1
        (raa / "kurser-raa-2026-09-22.json").unlink()

        fil, kall, _ = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30))
        assert fil is not None and len(kall) == KALL

    def test_base_som_ikke_kan_leses_gir_henting(self, stier):
        """Fila skrives foerst (AD-6). Ville feilet hvis en ulesbar base
        stoppet hentingen (M8)."""
        raa, base = stier
        base.parent.mkdir(parents=True)
        base.write_bytes(b"ikke en sqlite-base" * 10)
        linjer, kall = [], []

        def hent(ticker, *_):
            kall.append(ticker)
            return serie_til(TIRSDAG_22_09)

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, linjer.append,
                     les_kvote=nok_kvote)
        assert slutt.value.code == 1
        assert len(kall) == KALL
        # Gjennomgangen, VG8: meldingen om basen, ikke om kvoten.
        assert any(l.startswith(f"Basen {base.name} kunne ikke leses") for l in linjer)
        assert (raa / "kurser-raa-2026-09-22.json").exists()


class TestHelgen:
    """K8: fila heter etter boersdagen vurderingene skrives for."""

    def test_loerdag_med_fredagens_kurser_gir_0_kall(self, stier):
        raa, base = stier
        kjoer_23(raa, base, _utc(2026, 9, 25, 20, 0))
        (raa / "kurser-raa-2026-09-25.json").unlink()

        fil, kall, ut = kjoer_23(raa, base, LOERDAG_26_09_KL_12,
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
        assert "2026-09-25" in ut

    def test_loerdag_uten_fredagens_kurser_henter_med_fredagens_navn(self, stier):
        """Ville feilet hvis fila fikk kjoeredagens navn (M4)."""
        raa, base = stier
        fil, kall, _ = kjoer_23(raa, base, LOERDAG_26_09_KL_12,
                                lambda *_: serie_til(FREDAG_25_09))
        assert fil == raa / "kurser-raa-2026-09-25.json"
        assert len(kall) == KALL
        assert datoene_i_vurdering(base) == ["2026-09-25"]
        # Til-datoen i intervallet er fortsatt kjoeredagen.
        assert json.loads(fil.read_text(encoding="utf-8"))["to"] == "2026-09-26"

    def test_loerdag_naar_fredagens_fil_finnes_gir_0_kall_og_sier_hvorfor(self, stier):
        """Basen mangler fredagen, men fila finnes. Filvakten stopper ogsaa paa
        en dag som ikke er boersdag (AD-6). Ville feilet hvis vakten sjekket
        kjoeredagen (M4)."""
        raa, base = stier
        raa.mkdir(parents=True)
        (raa / "kurser-raa-2026-09-25.json").write_text("{}", encoding="utf-8")

        # Story 2.3b: basen mangler fredagen, saa det blir et nytt forsoek. Med
        # dagens 20 brukt er det 0 kall til det.
        kode, kall, ut = kjoer_23_kode(raa, base, LOERDAG_26_09_KL_12,
                                       ingen_kall, NOEKKEL,
                                       kvote(brukt=20, dato="2026-09-26"))
        # Beslutningen 08.10 (BH4): fredagen er ikke komplett, saa kode 1.
        # Ville feilet hvis filvakten ga kode 0 igjen (B4).
        assert kode == 1 and kall == []
        assert "kurser-raa-2026-09-25.json" in ut and "AD-6" in ut and "2.3b" in ut
        assert sorted(f.name for f in raa.iterdir()) == ["kurser-raa-2026-09-25.json"]


class TestRekkefoelgen:
    def test_noekkelen_og_kvoten_kommer_foer_foerste_kall(self, stier):
        raa, base = stier
        hendelser = []

        def nokkel():
            hendelser.append("noekkel")
            return NOEKKEL

        def les(n):
            assert n == NOEKKEL
            hendelser.append("kvote")
            return nok_kvote(n)

        def hent(*_):
            hendelser.append("kall")
            return serie_til(TIRSDAG_22_09)

        fp.kjoer(raa, base, OEYEBLIKK_22_09, nokkel, hent, lambda _: None, les_kvote=les)
        assert hendelser[:3] == ["noekkel", "kvote", "kall"]
        assert hendelser.count("noekkel") == hendelser.count("kvote") == 1


class TestKvoten:
    """Regel 15: kvoten leses med /api/user, i GMT, foer foerste kall."""

    def test_nok_igjen_henter_uten_bonus(self, stier):
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=kvote(brukt=4))
        assert fil is not None and len(kall) == 16
        assert "16 kall igjen" in ut and "bonus" not in ut

    def test_15_igjen_holder_ikke_for_16_uten_bonus(self, stier):
        """Story 2.8: hentingen er 16 kall, ogsaa i kvotesjekken. Ville
        feilet med 15 i kvotesjekken (mutant B3): da hentes det med 15 igjen,
        og kall nummer 16 tas fra bonuskvoten uten at sjekken sa ja."""
        raa, base = stier
        kode, kall, ut = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, ingen_kall,
                                       les_kvote=kvote(brukt=5, bonus=0))
        assert kode == 1 and kall == []
        assert "15 kall igjen av dagens og 0 i bonuskvoten. Hentingen trenger 16. 0 kall brukt." in ut

    def test_15_igjen_tar_ett_kall_fra_bonusen(self, stier):
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=kvote(brukt=5, bonus=463))
        assert fil is not None and len(kall) == 16
        assert "Kvoten: 15 kall igjen av dagens. 1 kall tas fra bonuskvoten" in ut

    def test_under_15_med_bonus_henter_og_sier_hvor_mange(self, stier):
        """Ville feilet hvis bonusen ikke ble talt med (K2)."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09,
                                 les_kvote=kvote(brukt=10, bonus=463))
        assert fil is not None and len(kall) == 16
        assert "6 kall tas fra bonuskvoten" in ut

    def test_under_15_uten_nok_bonus_gir_0_kall_og_kode_1(self, stier):
        raa, base = stier
        linjer = []
        with pytest.raises(SystemExit) as stopp:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, ingen_kall, linjer.append,
                     les_kvote=kvote(brukt=10, bonus=4))
        assert stopp.value.code == 1
        assert any("0 kall brukt" in l for l in linjer)
        assert list(raa.iterdir()) == []

    def test_tidligere_dato_i_gmt_betyr_0_brukt(self, stier):
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09,
                                 les_kvote=kvote(brukt=20, dato="2026-09-21"))
        assert fil is not None and len(kall) == 16
        assert "20 kall igjen" in ut

    def test_dagen_regnes_i_gmt_ikke_i_oslo(self, stier):
        """00:30 i Oslo 23.09 er 22.09 i GMT, og gaarsdagens kall teller
        fortsatt (presisert 04.10). Ville feilet med datoen i Oslo (K1)."""
        raa, base = stier
        linjer = []
        with pytest.raises(SystemExit) as stopp:
            fp.kjoer(raa, base, _utc(2026, 9, 22, 22, 30), NOEKKEL, ingen_kall,
                     linjer.append, hent_foer_kl_22=True,
                     les_kvote=kvote(brukt=20, dato="2026-09-22"))
        assert stopp.value.code == 1
        ut = "\n".join(linjer)
        # Gjennomgangen, BH9: stoppet av kvoten, ikke av noe annet.
        assert "0 kall igjen av dagens" in ut and "trenger 16" in ut and "0 kall brukt" in ut

    @pytest.mark.parametrize("svar", [
        requests.ConnectionError("nett"), "tekst", [], {}, {"apiRequests": 1},
        {"apiRequests": True, "apiRequestsDate": "2026-09-22", "dailyRateLimit": 20, "extraLimit": 0},
        {"apiRequests": 1, "apiRequestsDate": "igaar", "dailyRateLimit": 20, "extraLimit": 0},
        {"apiRequests": 1, "apiRequestsDate": None, "dailyRateLimit": 20, "extraLimit": 0},
    ], ids=["unntak", "tekst", "liste", "tomt", "felt-mangler", "bool", "dato", "dato-none"])
    def test_svar_som_ikke_kan_leses_gir_henting(self, stier, svar):
        """Ville feilet hvis et ulesbart svar stoppet hentingen (K3)."""
        raa, base = stier

        def les(_):
            if isinstance(svar, Exception):
                raise svar
            return svar

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=les)
        assert fil is not None and len(kall) == 16
        assert "Kvoten kunne ikke leses" in ut

    @pytest.mark.parametrize("brukt, bonus", [(0, 0), (10, 463), (10, 0)])
    def test_navn_og_epost_staar_aldri_i_utskriften(self, stier, brukt, bonus):
        """Ville feilet hvis svaret ble skrevet ut (K4)."""
        raa, base = stier
        les = kvote(brukt=brukt, bonus=bonus, name="Kari Testesen",
                    email="kari@eksempel.no", subscriptionType="free")
        linjer = []
        try:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, lambda *_: serie_til(TIRSDAG_22_09),
                     linjer.append, les_kvote=les)
        except SystemExit:
            pass
        ut = "\n".join(linjer)
        assert "Kvoten" in ut
        for hemmelig in ("Kari", "Testesen", "kari@eksempel.no", "free", NOEKKEL):
            assert hemmelig not in ut

    def test_unntak_fra_kvoten_viser_bare_typenavnet(self, stier):
        raa, base = stier

        def les(_):
            raise requests.ConnectionError(f"https://eodhd.com/api/user?api_token={NOEKKEL}")

        _, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=les)
        assert "ConnectionError" in ut and NOEKKEL not in ut


class TestHentKvote:
    """/api/user er den andre nettfunksjonen mot EODHD (AD-2). Uten nett."""

    def test_gir_svaret_tilbake_og_sender_noekkelen_som_parameter(self, monkeypatch):
        sett = {}

        def get(url, params, timeout):
            sett.update(url=url, params=params)
            svar = requests.Response()
            svar.status_code = 200
            svar._content = json.dumps({"apiRequests": 3}).encode()
            return svar

        monkeypatch.setattr(fp.requests, "get", get)
        assert fp.hent_kvote(NOEKKEL) == {"apiRequests": 3}
        assert sett["url"] == "https://eodhd.com/api/user"
        assert sett["params"]["api_token"] == NOEKKEL

    def test_http_feil_uten_adresse(self, monkeypatch):
        def get(url, params, timeout):
            return falsk_respons(401, "user", params["api_token"])

        monkeypatch.setattr(fp.requests, "get", get)
        with pytest.raises(requests.HTTPError) as feil:
            fp.hent_kvote(NOEKKEL)
        assert NOEKKEL not in str(feil.value)
        assert "401" in str(feil.value)


class TestVintertid:
    """Story 2.3, fra planen 05.10: tidskontrollen regner klokka i Oslo, ogsaa
    etter at sommertiden slutter 25.10. Ville feilet med klokka regnet i UTC
    (V1) eller med fast UTC+2 (V2)."""

    def test_kl_22_30_i_oslo_etter_25_10_er_21_30_utc_og_henter(self, stier):
        """Tirsdag 27.10 kl. 22:30 i Oslo er 21:30 UTC. Ville feilet med
        klokka regnet i UTC (V1), som gir 21:30 og nekter."""
        raa, base = stier
        fil, kall, _ = kjoer_23(raa, base, _utc(2026, 10, 27, 21, 30))
        assert fil == raa / "kurser-raa-2026-10-27.json"
        assert len(kall) == KALL

    def test_kl_21_59_i_oslo_i_november_nekter(self, stier):
        """Tirsdag 10.11 kl. 21:59 i Oslo er 20:59 UTC. Ville feilet med fast
        UTC+2 (V2), som gir 22:59 og henter."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, _utc(2026, 11, 10, 20, 59),
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
        assert "--hent-foer-kl-22" in ut and "0 kall brukt" in ut


class TestSvaretIkkeFraBoersdagen:
    """Story 2.3, FR-402, fra planen 05.10: mangler svaret dagens kurs for
    noen av aksjene, nevner utskriften dem, og kjoeringen gir kode 1. Ville
    feilet med varselet fjernet (V3)."""

    @staticmethod
    def _uten_dagen(ticker, *_):
        siste = date(2026, 9, 21) if ticker in ("EQNR.OL", "DNB.OL") else TIRSDAG_22_09
        return serie_til(siste)

    def test_utskriften_nevner_aksjene_og_kode_1(self, stier):
        raa, base = stier
        linjer = []
        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, self._uten_dagen,
                     linjer.append, les_kvote=nok_kvote)
        assert slutt.value.code == 1
        varsel = [l for l in linjer if "FR-402" in l and "2026-09-22" in l]
        assert len(varsel) == 1
        assert "DNB, EQNR" in varsel[0] and "2 aksjer" in varsel[0]
        # Fila og kursene staar, og hver aksje har en rad i vurdering.
        assert (raa / "kurser-raa-2026-09-22.json").exists()
        assert antall_rader(base, "vurdering") == len(AKSJEUNIVERS)

    def test_ny_kjoering_samme_kveld_gir_0_kall(self, stier):
        raa, base = stier
        with pytest.raises(SystemExit):
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, self._uten_dagen,
                     lambda _: None, les_kvote=nok_kvote)

        # Story 2.3b: et nytt forsoek, med dagens 20 brukt, gir 0 kall.
        kode, kall, ut = kjoer_23_kode(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30),
                                       ingen_kall, NOEKKEL, kvote(brukt=20))
        assert kode == 1 and kall == []
        assert "0 kall brukt" in ut and "2.3b" in ut

    def test_alle_har_dagen_gir_ingen_varsel(self, stier):
        raa, base = stier
        fil, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert fil is not None
        assert "FR-402" not in ut.replace("Ingenting aa hente (FR-402)", "")


class TestKvotenTarAntallet:
    """Endringsforslaget 08.10: kvotesjekken tar antallet aksjer i lista som
    parameter, ikke et fast 15, og testes med en kortere liste. Ville feilet
    med 15 skrevet inn i vurder_kvote (V4)."""

    @pytest.mark.parametrize(
        "igjen, bonus, antall, ventet",
        [
            (12, 0, 10, 0),      # kortere liste: 12 igjen holder for 10
            (12, 0, 15, None),   # de 15: 12 holder ikke, og ingen bonus
            (12, 3, 15, 3),      # bonusen fullfoerer kveldens henting
            (9, 1, 10, 1),
            (8, 1, 18, None),
            (18, 0, 18, 0),      # 18 aksjer, uten indeksen
            (0, 463, 15, 15),
        ],
    )
    def test_vurder_kvote(self, igjen, bonus, antall, ventet):
        assert fp.vurder_kvote(igjen, bonus, antall) == ventet

    def test_kjoer_gir_antallet_i_universet(self, stier, monkeypatch):
        """kjoer gir len(AKSJEUNIVERS) pluss indeksen (story 2.8), ikke et
        tall skrevet inn."""
        raa, base = stier
        sett = []
        ekte = fp.vurder_kvote

        def spion(igjen, bonus, antall):
            sett.append(antall)
            return ekte(igjen, bonus, antall)

        monkeypatch.setattr(fp, "vurder_kvote", spion)
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert sett == [len(AKSJEUNIVERS) + 1]


class TestKvotenErInjisert:
    """Instruksjonen kl. 19:00 08.10: kjoer() har ingen standardverdi for
    les_kvote, saa en test som glemmer kvoten, feiler i stedet for aa gaa mot
    nettet og bli stoppet av sperren uten at noen ser det (AD-8)."""

    def test_kjoer_uten_les_kvote_feiler(self, stier):
        raa, base = stier
        with pytest.raises(TypeError, match="les_kvote"):
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, ingen_kall, lambda _: None)

    def test_main_gir_hent_kvote(self, monkeypatch):
        sett = {}
        monkeypatch.setattr(fp, "kjoer", lambda *a, **kw: sett.update(kw))
        monkeypatch.setattr(fp, "naa", lambda: OEYEBLIKK_22_09)
        fp.main([])
        assert sett["les_kvote"] is fp.hent_kvote


class TestEtterGjennomgangen:
    """Funnene fra gjennomgangen av 2.3 (Review Triage Log i spesifikasjonen)."""

    def test_avvist_noekkel_gir_0_kall_og_kode_1(self, stier):
        """BH2: en 401 fra /api/user stopper foer fila skrives."""
        raa, base = stier
        linjer = []

        def les(_):
            raise requests.HTTPError("HTTP 401 Unauthorized")

        with pytest.raises(SystemExit) as slutt:
            fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, ingen_kall, linjer.append,
                     les_kvote=les)
        assert slutt.value.code == 1
        ut = "\n".join(linjer)
        assert "HTTP 401" in ut and "EODHD_API_KEY" in ut and "0 kall brukt" in ut
        assert list(raa.iterdir()) == []

    def test_serverfeil_fra_kvoten_gir_henting(self, stier):
        """BH2: andre HTTP-feil er et ulesbart svar, og da hentes det."""
        raa, base = stier

        def les(_):
            raise requests.HTTPError("HTTP 500 Internal Server Error")

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=les)
        assert fil is not None and len(kall) == KALL
        assert "HTTP 500" in ut and "Henter likevel" in ut

    def test_programmeringsfeil_i_kvoten_synes(self, stier):
        """BH3: en AttributeError gir ikke henting uten kvotesjekk."""
        raa, base = stier

        def les(_):
            raise AttributeError("feil i koden")

        with pytest.raises(AttributeError):
            kjoer_23(raa, base, OEYEBLIKK_22_09, ingen_kall, les_kvote=les)

    @pytest.mark.parametrize("felt", ["apiRequests", "dailyRateLimit", "extraLimit"])
    def test_negativt_tall_er_ulesbart(self, felt):
        """ECH5: -5 brukt ga 25 igjen."""
        svar = {"apiRequests": 1, "apiRequestsDate": "2026-09-22",
                "dailyRateLimit": 20, "extraLimit": 0, felt: -5}
        with pytest.raises(fp.UlesbarKvote, match=felt):
            fp.tolk_kvote(svar, date(2026, 9, 22))

    def test_brukt_over_grensen_gir_0_igjen_og_bonusen_fullfoerer(self, stier):
        """VG2: etter kall 21 er apiRequests over 20. Ville feilet uten max(…, 0)."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09,
                                 les_kvote=kvote(brukt=25, bonus=463))
        assert fil is not None and len(kall) == KALL
        assert "Kvoten: 0 kall igjen av dagens. 16 kall tas fra bonuskvoten" in ut

    def test_ulesbart_svar_med_navn_og_epost_viser_ingen_verdier(self, stier):
        """VG6 og VG7: feilteksten nevner feltnavn, aldri en verdi fra svaret."""
        raa, base = stier
        les = kvote(brukt="x", dato="igaar", name="Kari Testesen",
                    email="kari@eksempel.no")
        _, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=les)
        assert "Kvoten kunne ikke leses" in ut and "apiRequests" in ut
        for verdi in ("Kari", "kari@eksempel.no", "igaar", "'x'"):
            assert verdi not in ut

    def test_tidskontrollen_kommer_foer_basen(self, stier):
        """VG1: foer kl. 22 paa en boersdag, og basen har alt dagen. Tidskontrollen
        svarer, ikke basen. Ville feilet med basen foer tidskontrollen."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        # Samme boersdag kl. 21 i Oslo: basen har dagen, og klokka er foer 22.
        _, _, ut = kjoer_23(raa, base, _utc(2026, 9, 22, 19, 0),
                            ingen_kall, ingen_noekkel, ingen_kall)
        assert "--hent-foer-kl-22" in ut and "FR-402" not in ut

    def test_basen_kommer_foer_filvakten(self, stier):
        """VG1: basen har dagen, og fila finnes. Basen svarer, ikke filvakten.
        Ville feilet med filvakten foer basen."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert (raa / "kurser-raa-2026-09-22.json").exists()
        _, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30),
                            ingen_kall, ingen_noekkel, ingen_kall)
        assert "FR-402" in ut and "AD-6" not in ut

    def test_basesjekken_migrerer_ikke(self, stier, tmp_path):
        """VG3: manglende_i_basen aapner uten migrering. En base paa eldre
        skjemaversjon gir «kunne ikke leses» i basesjekken, og fila skrives
        foer basen migreres i skriv_til_basen. Ville feilet hvis basesjekken
        migrerte. (En base paa siste versjon endres ikke av en migrering, saa
        den kan ikke vise dette.)"""
        import migrering

        raa, base = stier
        eldre = tmp_path / "eldre"
        eldre.mkdir()
        for sql in sorted(lagring_sqlite.MIGRASJONSKATALOG.glob("*.sql"))[:3]:
            (eldre / sql.name).write_bytes(sql.read_bytes())
        base.parent.mkdir(parents=True)
        tilkobling = sqlite3.connect(base)
        try:
            migrering.migrer(tilkobling, eldre)
        finally:
            tilkobling.close()

        fil, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert f"Basen {base.name} kunne ikke leses (RuntimeError)" in ut
        assert fil is not None

    def test_flagget_advarer_om_filvakten(self, stier):
        """BH1 og ECH2: utskriften sier at fila kan laase dagen."""
        raa, base = stier
        _, _, ut = kjoer_23(raa, base, _utc(2026, 9, 22, 10, 0), hent_foer_kl_22=True)
        assert "filvakten" in ut and "dagens dato" in ut


# Story 2.3b: kallene som er igjen, brukes paa nye forsoek.

TRE_TIL = (
    Aksje("TSTA", "TSTA.OL", "Test A", "Test"),
    Aksje("TSTB", "TSTB.OL", "Test B", "Test"),
    Aksje("TSTC", "TSTC.OL", "Test C", "Test"),
)
ATTEN = AKSJEUNIVERS + TRE_TIL


def base_med_atten(base):
    """En testbase der aksje har de 15 og tre til, som demokommandoen gjoer
    med sin liste (AD-21). Bare i tmp_path (regel 22)."""
    base.parent.mkdir(parents=True, exist_ok=True)
    tilkobling = aapne_base(base)
    try:
        with tilkobling:
            tilkobling.executemany(
                "INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES (?, ?, ?, ?)",
                [(a.symbol, a.ticker, a.navn, a.sektor) for a in TRE_TIL],
            )
    finally:
        tilkobling.close()


class TestKvotetallene:
    """les_kvotetall gir grensen ogsaa, og tolk_kvote gir det samme som foer."""

    def test_les_kvotetall_gir_brukt_grense_og_bonus(self):
        svar = {"apiRequests": 7, "apiRequestsDate": "2026-09-22",
                "dailyRateLimit": 20, "extraLimit": 463}
        assert fp.les_kvotetall(svar, date(2026, 9, 22)) == (7, 20, 463)
        assert fp.tolk_kvote(svar, date(2026, 9, 22)) == (13, 463)

    def test_tidligere_dato_i_gmt_gir_0_brukt(self):
        svar = {"apiRequests": 20, "apiRequestsDate": "2026-09-21",
                "dailyRateLimit": 20, "extraLimit": 463}
        assert fp.les_kvotetall(svar, date(2026, 9, 22)) == (0, 20, 463)


class TestKallTilNyeForsoek:
    """NFR-01, tillegget 08.10: 20 minus aksjene i lista og indeksen, og aldri
    bonuskvoten. Ville feilet med et fast tall (M8) eller med bonusen (M3)."""

    @pytest.mark.parametrize(
        "igjen, grense, antall, ventet",
        [
            (5, 20, 15, 5),     # etter kveldens henting med de 15
            (20, 20, 15, 5),    # en dag uten henting: fortsatt bare marginen
            (2, 20, 15, 2),     # noen kall er brukt til noe annet
            (0, 20, 15, 0),
            (4, 20, 16, 4),     # de 15 og indeksen (2.8)
            (20, 20, 18, 2),    # 18 aksjer, uten indeksen
            (20, 20, 19, 1),    # 18 aksjer og indeksen
            (1, 20, 19, 1),
            (0, 20, 19, 0),
            (5, 20, 21, 0),     # aldri negativt
        ],
    )
    def test_kall_til_nye_forsoek(self, igjen, grense, antall, ventet):
        assert fp.kall_til_nye_forsoek(igjen, grense, antall) == ventet


class TestForsoeksfila:
    """Svar 1 (10.10): forsoek<n>-raa-<dato>.json med n fra 2 (AD-6)."""

    def test_foerste_er_forsoek2(self, tmp_path):
        assert fp.forsoeksfil(tmp_path, TIRSDAG_22_09) == tmp_path / "forsoek2-raa-2026-09-22.json"

    def test_neste_ledige(self, tmp_path):
        (tmp_path / "forsoek2-raa-2026-09-22.json").write_text("{}", encoding="utf-8")
        (tmp_path / "forsoek3-raa-2026-09-22.json").write_text("{}", encoding="utf-8")
        (tmp_path / "forsoek2-raa-2026-09-21.json").write_text("{}", encoding="utf-8")
        assert fp.forsoeksfil(tmp_path, TIRSDAG_22_09) == tmp_path / "forsoek4-raa-2026-09-22.json"

    def test_kursfila_vinner_ved_lik_dato(self, tmp_path):
        (tmp_path / "forsoek2-raa-2026-09-22.json").write_text("{}", encoding="utf-8")
        (tmp_path / "kurser-raa-2026-09-22.json").write_text("{}", encoding="utf-8")
        assert nyeste_snapshot(tmp_path).name == "kurser-raa-2026-09-22.json"


class TestEtSymbolSomFeilerGirKode1:
    """Svar 5 (ECH1): en aksje som feilet i hentingen, mangler dagens kurs,
    og kjoeringen gir kode 1. Ville feilet med kode 0 igjen (M12)."""

    def test_feilet_symbol_gir_kode_1_og_utskriften_sier_hva_som_gjoeres(self, stier):
        raa, base = stier

        def hent(ticker, *_):
            if ticker in ("DNB.OL", "EQNR.OL"):
                raise RuntimeError("nei")
            return serie_til(TIRSDAG_22_09)

        kode, kall, ut = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, hent)
        assert kode == 1 and len(kall) == KALL
        linje = [l for l in ut.splitlines() if "feilet i hentingen" in l]
        assert len(linje) == 1
        assert "2 aksjer" in linje[0] and "DNB, EQNR" in linje[0]
        assert "samme kommando igjen senere i kveld" in linje[0]
        # Fila, kursene og radene staar som foer.
        assert (raa / "kurser-raa-2026-09-22.json").exists()
        assert antall_rader(base, "vurdering") == len(AKSJEUNIVERS)

    def test_tomt_svar_gir_ogsaa_kode_1(self, stier):
        raa, base = stier
        kode, _, ut = kjoer_23_kode(
            raa, base, OEYEBLIKK_22_09,
            lambda t, *_: [] if t == "DNB.OL" else serie_til(TIRSDAG_22_09))
        assert kode == 1 and "1 aksjer feilet i hentingen" in ut

    def test_svar_uten_dagen_sier_ikke_lenger_at_det_kommer_senere(self, stier):
        raa, base = stier
        kode, _, ut = kjoer_23_kode(
            raa, base, OEYEBLIKK_22_09,
            lambda t, *_: serie_til(date(2026, 9, 21) if t == "DNB.OL" else TIRSDAG_22_09))
        assert kode == 1
        assert "kommer med story 2.3b" not in ut
        assert "samme kommando igjen senere i kveld" in ut


class TestListaMedAtten:
    """Endringsforslaget 08.10: hentingen tar lista som parameter og antar
    aldri 15 (AD-21). Ville feilet med AKSJEUNIVERS skrevet inn (M8)."""

    def test_hovedhentingen_med_atten(self, stier):
        raa, base = stier
        base_med_atten(base)
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, lista=ATTEN)
        assert fil is not None
        assert len(kall) == 19 and {"TSTA.OL", "TSTB.OL", "TSTC.OL", "OSEBX.OL"} <= set(kall)
        assert "Dette koster 19 kall" in ut
        assert antall_rader(base, "vurdering") == 18


# Story 2.3b, del 2: et nytt forsoek naar kveldens fil finnes.

ETTER_30_MIN = OEYEBLIKK_22_09 + timedelta(minutes=30)


def hovedhenting(stier, feiler=("DNB",), uten_dagen=(), oeyeblikk=OEYEBLIKK_22_09,
                 dato=TIRSDAG_22_09, lista=AKSJEUNIVERS):
    """Kveldens henting der noen aksjer feiler eller mangler dagen. Kode 1."""
    raa, base = stier

    def hent(ticker, *_):
        symbol = ticker.removesuffix(".OL")
        if symbol in feiler:
            raise RuntimeError("nei")
        return serie_til(dato - timedelta(days=1) if symbol in uten_dagen else dato)

    kode, _, _ = kjoer_23_kode(raa, base, oeyeblikk, hent, lista=lista)
    assert kode == 1


def sha(fil) -> str:
    return hashlib.sha256(fil.read_bytes()).hexdigest()


def kvoter(*svarene):
    """/api/user som gir svarene etter tur, og det siste resten av tiden.
    Lista som gis tilbake, teller lesingene."""
    lest = []

    def les(_noekkel):
        lest.append(1)
        neste = svarene[min(len(lest), len(svarene)) - 1]
        if isinstance(neste, Exception):
            raise neste
        return neste

    return les, lest


def svar(brukt=0, bonus=463, dato="2026-09-22", grense=20):
    return {"apiRequests": brukt, "apiRequestsDate": dato,
            "dailyRateLimit": grense, "extraLimit": bonus}


def raa_filer(raa) -> list[str]:
    return sorted(f.name for f in raa.iterdir())


class TestNyttForsoek:
    """Kontrollpunktene i 2.3b. Mutantene staar i spesifikasjonen."""

    def test_bare_de_som_mangler_hentes_eldste_foerst(self, stier):
        """EQNR fikk et svar uten dagen og har en serie fra 22:00. DNB feilet
        og har ingen. DNB foerst, saa EQNR, og ingen andre. Ville feilet hvis
        alle ble hentet (M1), en med dagens kurs ble hentet (M2), eller
        rekkefoelgen var lista (M13)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",), uten_dagen=("EQNR",))
        kursfil = raa / "kurser-raa-2026-09-22.json"
        foer = sha(kursfil)

        fil, kall, ut = kjoer_23(raa, base, ETTER_30_MIN)

        assert kall == ["DNB.OL", "EQNR.OL"]
        assert fil == raa / "forsoek2-raa-2026-09-22.json"
        assert sha(kursfil) == foer
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        assert set(bilde["serier"]) == {"DNB", "EQNR"} and bilde["feil"] == {}
        assert bilde["hentet"] == ETTER_30_MIN.isoformat()
        rader = vurderingene(base, TIRSDAG_22_09, ETTER_30_MIN)
        assert all(isinstance(v, Vurdering) for v, _ in rader.values())
        assert "eldste foerst: DNB, EQNR" in ut
        assert "Bonuskvoten brukes ikke" in ut
        assert "Alle 15 aksjene har kursen" in ut

    def test_vurderingen_skriver_over_grunnen_og_bare_den(self, stier, monkeypatch):
        """AD-7: vurderingen over grunnen samme boersdag, og radene som fantes,
        skrives ikke paa nytt. Ville feilet hvis forsoeket skrev alle radene
        (M14)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        assert vurderingene(base, TIRSDAG_22_09)["DNB"][0] == Grunn.SYMBOL_FEILET
        skrevet = []
        ekte = SqliteVurderingslager.skriv

        def spion(self, symbol, *a):
            skrevet.append(symbol)
            return ekte(self, symbol, *a)

        monkeypatch.setattr(SqliteVurderingslager, "skriv", spion)
        kjoer_23(raa, base, ETTER_30_MIN)
        assert skrevet == ["DNB"]
        assert isinstance(vurderingene(base, TIRSDAG_22_09, ETTER_30_MIN)["DNB"][0], Vurdering)

    def test_et_forsoek_som_feiler_igjen_roerer_ikke_raden(self, stier):
        """Grunnen kurs_ikke_fra_dagen staar naar EQNR feiler i forsoeket, og
        DNB faar vurderingen. Kode 1. Ville feilet hvis en ny grunn ble
        skrevet (M5)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",), uten_dagen=("EQNR",))

        def hent(ticker, *_):
            if ticker == "EQNR.OL":
                raise RuntimeError("igjen")
            return serie_til(TIRSDAG_22_09)

        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, hent)
        assert kode == 1 and kall == ["DNB.OL", "EQNR.OL"]
        rader = vurderingene(base, TIRSDAG_22_09, ETTER_30_MIN)
        assert rader["EQNR"][0] == Grunn.KURS_IKKE_FRA_DAGEN
        assert isinstance(rader["DNB"][0], Vurdering)
        assert "Mangler fortsatt kursen" in ut and "1 aksjer: EQNR" in ut
        assert "samme kommando igjen senere i kveld" in ut
        bilde = json.loads((raa / "forsoek2-raa-2026-09-22.json").read_text(encoding="utf-8"))
        assert "EQNR" in bilde["feil"]

    def test_neste_forsoek_faar_neste_fil(self, stier):
        """Svar 1: forsoek2, saa forsoek3. Ingen fil skrives om (AD-6)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        nei = lambda *_: (_ for _ in ()).throw(RuntimeError("nei"))  # noqa: E731
        assert kjoer_23_kode(raa, base, ETTER_30_MIN, nei)[0] == 1
        foer = sha(raa / "forsoek2-raa-2026-09-22.json")
        fil, kall, _ = kjoer_23(raa, base, ETTER_30_MIN + timedelta(minutes=30))
        assert fil == raa / "forsoek3-raa-2026-09-22.json" and kall == ["DNB.OL"]
        assert sha(raa / "forsoek2-raa-2026-09-22.json") == foer
        assert raa_filer(raa) == ["forsoek2-raa-2026-09-22.json",
                                  "forsoek3-raa-2026-09-22.json",
                                  "kurser-raa-2026-09-22.json"]


class TestNyttForsoekKvoten:
    """NFR-01, tillegget 08.10: kallene som er igjen av dagens, aldri
    bonuskvoten. Ville feilet med bonusen regnet med (M3) eller uten
    stoppen naar extraLimit synker (M4)."""

    def test_flere_mangler_enn_kallene_de_eldste_hentes(self, stier):
        raa, base = stier
        seks = ("EQNR", "DNB", "KOG", "AKRBP", "NHY", "FRO")
        hovedhenting(stier, feiler=seks)
        les, _ = kvoter(svar(brukt=15))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1
        # Story 2.8: 20 - 16 = 4, selv med 5 igjen av dagens.
        assert kall == [f"{s}.OL" for s in seks[:4]]
        assert "5 kall igjen av dagens, 4 til nye forsoek" in ut
        assert "2 aksjer: FRO, NHY" in [l for l in ut.splitlines() if "Mangler fortsatt" in l][0]

    def test_ingen_kall_igjen_gir_0_kall_selv_med_bonus(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        les, _ = kvoter(svar(brukt=20, bonus=463))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == []
        assert "0 til nye forsoek" in ut and "Bonuskvoten brukes aldri" in ut
        assert raa_filer(raa) == ["kurser-raa-2026-09-22.json"]

    def test_bare_marginen_selv_naar_hele_dagen_er_igjen(self, stier):
        """20 igjen gir likevel bare 20 - 16 = 4 (tillegget 08.10, story 2.8),
        og forsoeket henter aldri indeksen. Ville feilet med indeksen i
        forsoeket (mutant B5) eller med 15 i stedet for 16."""
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB", "KOG", "AKRBP", "NHY", "FRO", "VAR"))
        les, _ = kvoter(svar(brukt=0))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and len(kall) == 4
        assert "OSEBX.OL" not in kall and "20 kall igjen av dagens, 4 til nye forsoek" in ut

    def test_stopper_naar_extralimit_synker(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB", "KOG"))
        les, lest = kvoter(svar(brukt=15, bonus=463), svar(brukt=15, bonus=462))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == ["EQNR.OL"] and len(lest) == 2
        assert "Bonuskvoten sank fra 463 til 462" in ut
        bilde = json.loads((raa / "forsoek2-raa-2026-09-22.json").read_text(encoding="utf-8"))
        assert set(bilde["serier"]) == {"EQNR"}

    def test_leser_kvoten_etter_hvert_kall(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB", "KOG"))
        les, lest = kvoter(svar(brukt=15))
        fil, kall, _ = kjoer_23(raa, base, ETTER_30_MIN, les_kvote=les)
        assert fil is not None and len(kall) == 3
        assert len(lest) == 1 + 3

    def test_kvoten_som_ikke_kan_leses_etter_et_kall_stopper(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB"))
        les, _ = kvoter(svar(brukt=15), requests.ConnectionError("ConnectionError"))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == ["EQNR.OL"]
        assert "kunne ikke leses etter kallet" in ut

    @pytest.mark.parametrize("feil", [
        {},
        svar(brukt="tjue"),
        requests.ConnectionError("ConnectionError"),
        requests.HTTPError("HTTP 500 Internal Server Error"),
    ], ids=["tomt", "tekst", "nett", "http-500"])
    def test_kvote_som_ikke_kan_leses_gir_0_kall(self, stier, feil):
        """Strengere enn hovedhentingen: et nytt forsoek tar ingen sjanse paa
        bonusen. Ville feilet hvis det ble hentet likevel (M7)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        les, _ = kvoter(feil)
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == []
        assert "0 kall brukt" in ut
        assert raa_filer(raa) == ["kurser-raa-2026-09-22.json"]

    def test_noekkelen_avvist_gir_0_kall(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        les, _ = kvoter(requests.HTTPError("HTTP 401 Unauthorized"))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == [] and "avviste noekkelen" in ut

    def test_liste_med_18_gir_1_kall_med_indeksen(self, stier):
        """18 aksjer og indeksen (2.8): 20 - 19 = 1. Ville feilet med 15
        skrevet inn (M8)."""
        raa, base = stier
        base_med_atten(base)
        hovedhenting(stier, feiler=("TSTA", "TSTB", "TSTC"), lista=ATTEN)
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, lista=ATTEN)
        assert kode == 1 and kall == ["TSTA.OL"]
        assert "1 til nye forsoek" in ut
        assert fp.kall_til_nye_forsoek(20, 20, 18 + 1) == 1


class TestNyttForsoekKlokka:
    """Svar 4: ingen nye kall fra kl. 23:50 i Oslo, og AD-20 etter midnatt."""

    def test_kl_23_50_gir_0_kall(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        kl_23_50 = _utc(2026, 9, 22, 21, 50)
        kode, kall, ut = kjoer_23_kode(raa, base, kl_23_50, ingen_kall, ingen_noekkel, ingen_kall)
        assert kode == 1 and kall == [] and "23:50" in ut
        assert raa_filer(raa) == ["kurser-raa-2026-09-22.json"]

    def test_kl_23_49_henter(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        fil, kall, _ = kjoer_23(raa, base, _utc(2026, 9, 22, 21, 49))
        assert fil is not None and kall == ["DNB.OL"]

    def test_klokka_passerer_23_50_under_forsoeket(self, stier):
        """Klokka leses foer hvert kall. Ville feilet hvis den bare ble lest
        ved starten (M15)."""
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB"))
        tider = [_utc(2026, 9, 22, 21, 49), _utc(2026, 9, 22, 21, 49), _utc(2026, 9, 22, 21, 50)]

        def klokke():
            return tider.pop(0) if len(tider) > 1 else tider[0]

        kode, kall, ut = kjoer_23_kode(raa, base, _utc(2026, 9, 22, 21, 49), klokke=klokke)
        assert kode == 1 and kall == ["EQNR.OL"]
        assert "Ingen flere kall" in ut

    def test_over_midnatt_foer_vurderingene_skriver_ingen_rad(self, stier):
        """AD-20 og AD-7: kursen skrives, men ikke raden, naar det er blitt en
        ny dag i Oslo. Ville feilet uten sjekken (M10)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        tider = [_utc(2026, 9, 22, 21, 45), _utc(2026, 9, 22, 21, 45), _utc(2026, 9, 22, 22, 1)]

        def klokke():
            return tider.pop(0) if len(tider) > 1 else tider[0]

        kode, kall, ut = kjoer_23_kode(raa, base, _utc(2026, 9, 22, 21, 45), klokke=klokke)
        assert kode == 1 and kall == ["DNB.OL"]
        assert "over midnatt" in ut
        assert vurderingene(base, TIRSDAG_22_09)["DNB"][0] == Grunn.SYMBOL_FEILET


class TestNyttForsoekStengtDag:
    """Svar 3: en dag boersen er stengt, staar raden (beslutning 1 i 2.5)."""

    def test_loerdag_skriver_kursen_men_raden_staar(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",), oeyeblikk=_utc(2026, 9, 25, 20, 0),
                     dato=FREDAG_25_09)
        les, _ = kvoter(svar(brukt=0, dato="2026-09-26"))
        fil, kall, ut = kjoer_23(raa, base, LOERDAG_26_09_KL_12,
                                 lambda *_: serie_til(FREDAG_25_09), les_kvote=les)
        assert kall == ["DNB.OL"]
        assert fil == raa / "forsoek2-raa-2026-09-25.json"
        rader = vurderingene(base, FREDAG_25_09, LOERDAG_26_09_KL_12)
        assert rader["DNB"][0] == Grunn.SYMBOL_FEILET
        assert rader["DNB"][1][-1].dato == FREDAG_25_09
        assert "sto fra foer" in ut and "DNB" in ut


class TestNyttForsoekVaktene:
    def test_demobasen_nektes_foer_alt_annet(self, stier):
        """3.4: demovakten foerst, ogsaa naar kveldens fil finnes. Ville
        feilet hvis vakten kom etter filvakten (M9)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        tilkobling = sqlite3.connect(base)
        tilkobling.execute(f"PRAGMA application_id = {lagring_sqlite.DEMOMERKE}")
        tilkobling.commit()
        tilkobling.close()
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        assert kode == 1 and kall == [] and "demobase" in ut
        assert raa_filer(raa) == ["kurser-raa-2026-09-22.json"]

    def test_basen_som_ikke_kan_leses_gir_ingen_forsoek(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        base.write_bytes(b"ikke en base")
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        assert kode == 1 and kall == []
        assert "ikke noe nytt forsoek" in ut and "0 kall brukt" in ut

    def test_utskriften_har_ingen_kurser_og_ingen_noekkel(self, stier):
        """Regel 16."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        _, _, ut = kjoer_23(raa, base, ETTER_30_MIN, lambda *_: serie_med_utslag(TIRSDAG_22_09))
        assert NOEKKEL not in ut
        verdier = {str(r[f]) for r in serie_med_utslag(TIRSDAG_22_09)
                   for f in ("close", "adjusted_close", "volume")}
        assert not [v for v in verdier if v in ut]


class TestVurderingeneSomMangler:
    """Svar 6 (ECH8 i 2.3): har basen kursene for boersdagen, men radene i
    vurdering mangler, skrives de med 0 kall. Ville feilet uten (M11)."""

    @staticmethod
    def _bare_kursene(stier):
        """Kursene for 22.09 lest inn uten vurdering (2.1b), og fila borte."""
        raa, base = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)
        fp.les_inn(fil, base, lambda _: None)
        fil.unlink()
        assert antall_rader(base, "vurdering") == 0

    def test_radene_skrives_med_0_kall(self, stier):
        raa, base = stier
        self._bare_kursene(stier)
        fil, kall, ut = kjoer_23(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
        assert antall_rader(base, "vurdering") == len(AKSJEUNIVERS)
        assert "15 aksjer mangler raden i vurdering" in ut and "uten kall" in ut
        assert raa_filer(raa) == []

    def test_rader_som_finnes_roeres_ikke(self, stier, monkeypatch):
        raa, base = stier
        self._bare_kursene(stier)
        tilkobling = aapne_base(base)
        try:
            lager = SqliteVurderingslager(tilkobling, lambda: ETTER_30_MIN)
            for symbol in ("EQNR", "DNB"):
                lager.skriv(symbol, TIRSDAG_22_09, Grunn.SIGNAL_IKKE_REGNET)
        finally:
            tilkobling.close()
        skrevet = []
        ekte = SqliteVurderingslager.skriv

        def spion(self, symbol, *a):
            skrevet.append(symbol)
            return ekte(self, symbol, *a)

        monkeypatch.setattr(SqliteVurderingslager, "skriv", spion)
        kjoer_23(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        assert len(skrevet) == 13 and not {"EQNR", "DNB"} & set(skrevet)
        rader = vurderingene(base, TIRSDAG_22_09, ETTER_30_MIN)
        assert rader["EQNR"][0] == Grunn.SIGNAL_IKKE_REGNET

    def test_alle_radene_finnes_gir_ingen_skriving(self, stier, monkeypatch):
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        monkeypatch.setattr(SqliteVurderingslager, "skriv",
                            lambda *a: pytest.fail("ingen rad skal skrives"))
        fil, kall, ut = kjoer_23(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == [] and "mangler raden" not in ut

    def test_over_midnatt_skrives_ingen_rad(self, stier):
        """AD-7: radene kan bare skrives saa lenge dagen er inneveerende
        boersdag."""
        raa, base = stier
        self._bare_kursene(stier)
        kode, kall, ut = kjoer_23_kode(
            raa, base, _utc(2026, 9, 22, 21, 59), ingen_kall, ingen_noekkel, ingen_kall,
            klokke=lambda: _utc(2026, 9, 22, 22, 1))
        assert kode == 1 and kall == []
        assert antall_rader(base, "vurdering") == 0


class TestNyttForsoekEtterGjennomgangen:
    """Funnene i gjennomgangen av 2.3b (triageloggen i spesifikasjonen)."""

    def test_svar_som_fortsatt_mangler_dagen_gir_kode_1(self, stier):
        """VG1: forsoeket faar et svar uten dagen. Kode 1, aksjen nevnes, og
        raden faar grunnen kurs_ikke_fra_dagen i stedet for symbol_feilet,
        fordi serien ble skrevet. Ville feilet hvis bare feilene telte (M21)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN,
                                       lambda *_: serie_til(date(2026, 9, 21)))
        assert kode == 1 and kall == ["DNB.OL"]
        assert "Mangler fortsatt kursen" in ut and "1 aksjer: DNB" in ut
        assert "Alle 15 aksjene har kursen" not in ut
        assert vurderingene(base, TIRSDAG_22_09, ETTER_30_MIN)["DNB"][0] == Grunn.KURS_IKKE_FRA_DAGEN

    def test_neste_forsoek_tar_de_som_ikke_ble_proevd(self, stier):
        """VG2 og svar 2: alle sju har en serie fra 22:00 uten dagen. Det
        foerste forsoeket tar fire i lista-rekkefoelge (story 2.8), og de fire
        faar ny tid. Det andre tar de tre som ikke ble proevd, fordi de er
        eldst. Ville feilet med rekkefoelgen etter lista (M13)."""
        raa, base = stier
        sju = ("EQNR", "DNB", "KOG", "AKRBP", "NHY", "FRO", "VAR")
        hovedhenting(stier, feiler=(), uten_dagen=sju)
        uten = lambda *_: serie_til(date(2026, 9, 21))  # noqa: E731
        kode, kall, _ = kjoer_23_kode(raa, base, ETTER_30_MIN, uten)
        assert kode == 1 and kall == [f"{s}.OL" for s in sju[:4]]
        kode, kall, _ = kjoer_23_kode(raa, base, ETTER_30_MIN + timedelta(minutes=30), uten)
        assert kode == 1 and kall[:3] == ["NHY.OL", "FRO.OL", "VAR.OL"]

    def test_dagens_kall_brukt_opp_underveis_stopper(self, stier):
        """BH5 og ECH4: en annen kjoering bruker kall samtidig. Naar
        apiRequests naar grensen, stopper forsoeket foer neste kall, saa det
        aldri tas fra bonuskvoten. Ville feilet uten sjekken (M22)."""
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB", "KOG"))
        les, _ = kvoter(svar(brukt=15), svar(brukt=20))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == ["EQNR.OL"]
        assert "Dagens 20 kall er brukt" in ut

    def test_fil_som_dukker_opp_gir_neste_n(self, stier, monkeypatch):
        """BH6 og ECH2: navnet er fritt, saa forsoeket tar neste n i stedet
        for aa kaste kallene. Ville feilet uten (M23)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        ekte = fp.forsoeksfil

        def foerst_opptatt(katalog, dato):
            fil = ekte(katalog, dato)
            if fil.name == "forsoek2-raa-2026-09-22.json":
                fil.write_text('{"annen": true}', encoding="utf-8")
            return fil

        monkeypatch.setattr(fp, "forsoeksfil", foerst_opptatt)
        fil, kall, _ = kjoer_23(raa, base, ETTER_30_MIN)
        assert fil == raa / "forsoek3-raa-2026-09-22.json" and kall == ["DNB.OL"]
        assert (raa / "forsoek2-raa-2026-09-22.json").read_text(encoding="utf-8") == '{"annen": true}'

    def test_alle_kallene_feiler_og_fila_har_feilene(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("EQNR", "DNB"))
        nei = lambda *_: (_ for _ in ()).throw(RuntimeError("nei"))  # noqa: E731
        kode, kall, _ = kjoer_23_kode(raa, base, ETTER_30_MIN, nei)
        assert kode == 1 and kall == ["EQNR.OL", "DNB.OL"]
        bilde = json.loads((raa / "forsoek2-raa-2026-09-22.json").read_text(encoding="utf-8"))
        assert bilde["serier"] == {} and set(bilde["feil"]) == {"EQNR", "DNB"}

    def test_basen_feiler_i_forsoeket_sier_fra(self, stier, monkeypatch):
        """BH7: samme melding som hovedhentingen, og fila staar."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        monkeypatch.setattr(fp, "skriv_til_basen", lambda *a: None)
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN)
        assert kode == 1 and kall == ["DNB.OL"]
        assert "Ingen vurdering er skrevet for 2026-09-22 i forsoeket" in ut
        assert (raa / "forsoek2-raa-2026-09-22.json").exists()

    def test_basen_som_ikke_kan_leses_i_rekkefoelgen_gir_0_kall(self, stier, monkeypatch):
        """ECH1: en ren stopp med kode 1, ikke en traceback."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))

        def feiler(*_):
            raise sqlite3.OperationalError("database is locked")

        monkeypatch.setattr(fp, "eldste_foerst", feiler)
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN)
        assert kode == 1 and kall == [] and "OperationalError" in ut

    def test_ny_dag_sier_det_og_ikke_23_50(self, stier):
        """ECH6: grunnen i utskriften er den riktige."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        kode, kall, ut = kjoer_23_kode(raa, base, _utc(2026, 9, 22, 21, 45), ingen_kall,
                                       ingen_noekkel, ingen_kall,
                                       klokke=lambda: _utc(2026, 9, 22, 22, 1))
        assert kode == 1 and kall == []
        assert "ny dag i Oslo" in ut and "23:50" not in ut

    def test_noekkelen_avvist_med_403(self, stier):
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        les, _ = kvoter(requests.HTTPError("HTTP 403 Forbidden"))
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert kode == 1 and kall == [] and "avviste noekkelen" in ut

    def test_0_kall_linjen_kommer_fra_forsoeket(self, stier):
        """ECH8 i gjennomgangen: linjen med 0 kall er kvotelinjen i forsoeket."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        les, _ = kvoter(svar(brukt=20))
        _, _, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, les_kvote=les)
        assert any("0 til nye forsoek" in l and "0 kall brukt" in l for l in ut.splitlines())


class TestVurderingeneSomManglerEtterGjennomgangen:
    """Svar 6 (ECH8 i 2.3), funnene i gjennomgangen av 2.3b."""

    def test_radene_er_vurderinger(self, stier):
        """VG3: radene er regnet av kursene i basen, ikke grunner. Ville
        feilet hvis aksjene gikk som feilet (M24)."""
        raa, base = stier
        TestVurderingeneSomMangler._bare_kursene(stier)
        kjoer_23(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        rader = vurderingene(base, TIRSDAG_22_09, ETTER_30_MIN)
        assert all(isinstance(v, Vurdering) for v, _ in rader.values())

    def test_radene_som_ikke_kan_leses_gir_kode_1(self, stier, monkeypatch):
        """VG4: kode 1 og meldingen, 0 kall."""
        raa, base = stier
        TestVurderingeneSomMangler._bare_kursene(stier)

        def feiler(*_):
            raise sqlite3.OperationalError("no such table")

        monkeypatch.setattr(fp, "manglende_vurderinger", feiler)
        kode, kall, ut = kjoer_23_kode(raa, base, ETTER_30_MIN, ingen_kall, ingen_noekkel, ingen_kall)
        assert kode == 1 and kall == []
        assert "Radene i vurdering kunne ikke leses (OperationalError)" in ut

    def test_loerdag_skrives_fredagens_rader(self, stier):
        """En dag boersen er stengt, finnes ingen rad fra foer, saa radene
        for fredag skrives (AD-7, inneveerende boersdag)."""
        raa, base = stier
        fil = lag_bilde(raa, _utc(2026, 9, 25, 20, 0), FREDAG_25_09)
        fp.les_inn(fil, base, lambda _: None)
        fil.unlink()
        fil_, kall, ut = kjoer_23(raa, base, LOERDAG_26_09_KL_12, ingen_kall, ingen_noekkel, ingen_kall)
        assert fil_ is None and kall == []
        assert datoene_i_vurdering(base) == ["2026-09-25"]
        assert antall_rader(base, "vurdering") == len(AKSJEUNIVERS)

    def test_ny_dag_foer_radene_stopper(self, stier):
        """ECH5: ECH8 stopper ved midnatt i Oslo, som hovedhentingen. Fredag
        23:59, og klokka er loerdag naar radene skulle skrives."""
        raa, base = stier
        fil = lag_bilde(raa, _utc(2026, 9, 25, 20, 0), FREDAG_25_09)
        fp.les_inn(fil, base, lambda _: None)
        fil.unlink()
        kode, kall, ut = kjoer_23_kode(raa, base, _utc(2026, 9, 25, 21, 59), ingen_kall,
                                       ingen_noekkel, ingen_kall,
                                       klokke=lambda: _utc(2026, 9, 25, 22, 1))
        assert kode == 1 and kall == [] and "over midnatt" in ut
        assert antall_rader(base, "vurdering") == 0


class TestNyttForsoekEtterMutantene:
    """De to mutantene som overlevde foerste kjoering (M10 og M20)."""

    def test_fredag_over_midnatt_skriver_ingen_rad(self, stier):
        """M10: fredag til loerdag godtar lageret fortsatt fredag, saa bare
        sjekken i forsoeket hindrer at raden skrives etter midnatt (AD-20)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",), oeyeblikk=_utc(2026, 9, 25, 20, 0),
                     dato=FREDAG_25_09)
        tider = [_utc(2026, 9, 25, 21, 45), _utc(2026, 9, 25, 21, 45), _utc(2026, 9, 25, 22, 1)]

        def klokke():
            return tider.pop(0) if len(tider) > 1 else tider[0]

        kode, kall, ut = kjoer_23_kode(raa, base, _utc(2026, 9, 25, 21, 45),
                                       lambda *_: serie_til(FREDAG_25_09), klokke=klokke)
        assert kode == 1 and kall == ["DNB.OL"] and "over midnatt" in ut
        assert vurderingene(base, FREDAG_25_09, LOERDAG_26_09_KL_12)["DNB"][0] == Grunn.SYMBOL_FEILET

    def test_ingen_kall_gir_ingen_fil(self, stier):
        """M20: klokka passerer 23:50 foer foerste kall. Ingen tom forsoeksfil."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        tider = [_utc(2026, 9, 22, 21, 49), _utc(2026, 9, 22, 21, 50)]

        def klokke():
            return tider.pop(0) if len(tider) > 1 else tider[0]

        kode, kall, ut = kjoer_23_kode(raa, base, _utc(2026, 9, 22, 21, 49), klokke=klokke)
        assert kode == 1 and kall == []
        assert "ingen fil er skrevet" in ut
        assert raa_filer(raa) == ["kurser-raa-2026-09-22.json"]


# Story 2.8, PR 2, punkt a (beslutningen 16.10 kl. 22:16): sjekken av basen
# foer kallene leser ogsaa en base en versjon bak, uten aa skrive. 16.10 sto
# basen paa versjon 4 med 0005 flettet, og sjekken ga «Basen ose.db kunne ikke
# leses (RuntimeError)». Den ekte basen staar paa 5 naar 0006 er flettet.


def base_paa_versjon(tmp_path, base, versjon: int, uten_kurs=(), uten_vurdering=(),
                     dato: date = TIRSDAG_22_09):
    """En base migrert til versjon med en katalog som bare har de foerste
    migrasjonene, med kurs, kursserie og vurdering skrevet med SQL, fordi
    adapterne krever siste versjon for aa skrive."""
    from migrering import migrer, versjon as versjon_av

    katalog = tmp_path / f"migrasjoner_til_{versjon}"
    katalog.mkdir()
    for fil in sorted(lagring_sqlite.MIGRASJONSKATALOG.glob("*.sql")):
        if int(fil.name[:4]) <= versjon:
            katalog.joinpath(fil.name).write_bytes(fil.read_bytes())
    base.parent.mkdir(parents=True, exist_ok=True)
    tilkobling = sqlite3.connect(base, isolation_level=None)
    try:
        assert migrer(tilkobling, katalog) == versjon == versjon_av(tilkobling)
        for nr, aksje in enumerate(AKSJEUNIVERS):
            if aksje.symbol in uten_kurs:
                continue
            tilkobling.execute("INSERT INTO kurs VALUES (?, ?, 1.0, 1.0, 10)",
                               (aksje.symbol, dato.isoformat()))
            tilkobling.execute("INSERT INTO kursserie VALUES (?, ?)",
                               (aksje.symbol, _utc(2026, 9, 22, 20, nr).isoformat()))
            if aksje.symbol not in uten_vurdering:
                tilkobling.execute(
                    "INSERT INTO vurdering (symbol, dato, grunn) VALUES (?, ?, 'signal_ikke_regnet')",
                    (aksje.symbol, dato.isoformat()))
    finally:
        tilkobling.close()


class TestSjekkenLeserEnBaseEnVersjonBak:
    """Story 2.8, punkt a. Ville feilet hvis sjekken krevde siste versjon
    igjen (mutant A1): da gir den RuntimeError paa en base paa versjon 5."""

    def test_de_tre_sjekkene_virker_paa_versjon_5_og_fila_er_uendret(self, tmp_path, stier):
        _, base = stier
        siste = len(list(lagring_sqlite.MIGRASJONSKATALOG.glob("*.sql")))
        base_paa_versjon(tmp_path, base, siste - 1, uten_kurs=("DNB",), uten_vurdering=("EQNR",))
        foer = sha(base)

        assert fp.manglende_i_basen(base, TIRSDAG_22_09) == ["DNB"]
        assert fp.manglende_vurderinger(base, TIRSDAG_22_09) == ["EQNR", "DNB"]
        # DNB har ingen serie og kommer foerst, saa kursserie.hentet avgjoer.
        assert fp.eldste_foerst(base, ["NHY", "DNB", "EQNR"]) == ["DNB", "EQNR", "NHY"]
        assert sha(base) == foer

    def test_hentingen_ser_at_basen_har_dagen_og_gjoer_0_kall(self, tmp_path, stier):
        """Som 16.10, men med basen paa versjon 5 og 0006 flettet. Ville feilet
        hvis sjekken ga RuntimeError og hentingen gikk videre til filvakten."""
        raa, base = stier
        base_paa_versjon(tmp_path, base, 5)
        foer = sha(base)

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30),
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
        assert "Basen har alt kursene for boersdagen 2026-09-22" in ut
        assert "kunne ikke leses" not in ut
        assert sha(base) == foer

    def test_to_versjoner_bak_avvises_som_foer(self, tmp_path, stier):
        """En base som staar lenger bak, kan ha et skjema lesingen ikke
        kjenner. Den avvises, og hentingen henter og migrerer den."""
        _, base = stier
        base_paa_versjon(tmp_path, base, 4)
        with pytest.raises(RuntimeError, match="versjon 4"):
            fp.manglende_i_basen(base, TIRSDAG_22_09)

    def test_en_skriver_faar_aldri_en_base_en_versjon_bak(self, tmp_path, stier):
        """Flagget godtas bare paa en tilkobling med query_only. Ville feilet
        hvis et lager kunne skrive til en base med et skjema det ikke kjenner."""
        _, base = stier
        base_paa_versjon(tmp_path, base, 5)
        tilkobling = aapne_base(base, kjoer_migrasjoner=False)
        try:
            with pytest.raises(ValueError, match="query_only"):
                SqliteKurslager(tilkobling, godta_en_versjon_bak=True)
            with pytest.raises(ValueError, match="query_only"):
                SqliteVurderingslager(tilkobling, fp.naa, godta_en_versjon_bak=True)
            with pytest.raises(RuntimeError):
                SqliteKurslager(tilkobling)
        finally:
            tilkobling.close()


# Story 2.8, PR 2, punkt b: kallet for hovedindeksen i hentingen (FR-410).


def indeksen_i(base):
    """(serien, sist_hentet) for OSEBX gjennom porten."""
    from lagring_sqlite import SqliteIndekslager

    tilkobling = aapne_base(base)
    try:
        lager = SqliteIndekslager(tilkobling)
        return lager.serie("OSEBX"), lager.sist_hentet("OSEBX")
    finally:
        tilkobling.close()


def symbolene_i(base, tabell: str) -> set[str]:
    tilkobling = aapne_base(base)
    try:
        return {r[0] for r in tilkobling.execute(f"SELECT DISTINCT symbol FROM {tabell}")}
    finally:
        tilkobling.close()


class TestHovedindeksen:
    """Kontrollpunktene under story 2.8. Mutantene staar i spesifikasjonen 2.8b."""

    def test_ett_kall_for_indeksen_med_samme_intervall_og_16_i_alt(self, stier):
        """Ville feilet uten kallet, med to kall for indeksen, eller med et
        annet intervall enn aksjene."""
        raa, base = stier
        intervall = []

        def hent(ticker, _noekkel, fra, til):
            intervall.append((ticker, fra, til))
            return serie_til(TIRSDAG_22_09)

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, hent)
        assert fil is not None
        assert len(kall) == 16 and kall.count("OSEBX.OL") == 1 and kall[-1] == "OSEBX.OL"
        assert {(fra, til) for _, fra, til in intervall} == {fp.bygg_intervall(TIRSDAG_22_09)}
        assert "Henter 15 aksjer og hovedindeksen" in ut
        assert "Dette koster 16 kall" in ut and "API-kall brukt: 16" in ut

    def test_raadataene_staar_i_samme_bilde_under_egen_noekkel(self, stier):
        """Ville feilet hvis indeksen sto blant aksjeseriene, eller ble
        oversatt foer den ble skrevet."""
        raa, base = stier
        raadata = serie_til(TIRSDAG_22_09)
        fil, _, _ = kjoer_23(raa, base, OEYEBLIKK_22_09, lambda *_: copy.deepcopy(raadata))
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        assert bilde["indeks"] == {"serier": {"OSEBX": raadata}, "feil": {}}
        assert "OSEBX" not in bilde["serier"] and "OSEBX" not in bilde["feil"]
        assert set(bilde["serier"]) == {aksje.symbol for aksje in AKSJEUNIVERS}
        # Leseren for aksjene ser bare aksjene.
        assert SnapshotKilde.fra_fil(fil).serie("OSEBX") == []

    def test_indeksen_lagres_i_indeks_aldri_i_kurs_eller_vurdering(self, stier):
        """Ville feilet hvis indeksen ble lagret i kurs (mutant B2), eller
        talte som en aksje i vurdering."""
        raa, base = stier
        _, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09)
        serie, hentet = indeksen_i(base)
        ventet = [rad for rad in fp.serie_fra_eodhd(serie_til(TIRSDAG_22_09))
                  if rad.dato.weekday() < 5]
        assert serie == ventet and hentet == OEYEBLIKK_22_09
        for tabell in ("aksje", "kurs", "kursserie", "vurdering"):
            assert "OSEBX" not in symbolene_i(base, tabell), tabell
        assert antall_rader(base, "vurdering") == len(AKSJEUNIVERS)
        assert f"Hovedindeksen OSEBX: lagret {len(ventet)} dager, tok bort {60 - len(ventet)} " in ut

    def test_utskriften_teller_dagene_som_tas_bort(self, stier):
        """BH2 i 2.8a: 300 dager bakover fra 22.09.2026 gir dager i 2025, helger
        og stengte dager, og alle telles. Antallet regnes her med kalenderen,
        ikke med funksjonen hentingen bruker."""
        from boersdag import DEKKEDE_AAR, er_boersdag

        raa, base = stier
        raadata = serie_til(TIRSDAG_22_09, dager=300)
        _, _, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, lambda *_: copy.deepcopy(raadata))
        datoer = [date.fromisoformat(r["date"]) for r in raadata]
        lagret = sum(1 for d in datoer if d.year in DEKKEDE_AAR and er_boersdag(d))
        assert any(d.year not in DEKKEDE_AAR for d in datoer)
        assert len(indeksen_i(base)[0]) == lagret
        assert f"lagret {lagret} dager, tok bort {300 - lagret} som ikke er boersdager i 2026." in ut

    @pytest.mark.parametrize("svaret", ["feil", "tomt", "form"])
    def test_et_feilet_indekskall_stopper_ikke_aksjene(self, stier, svaret):
        """AD-15: aksjene lagres og vurderes, indeksen staar i feil, og
        kjoeringen gir kode 0, fordi et nytt forsoek ikke tar indeksen. Ville
        feilet hvis et feilet indekskall stoppet aksjene (mutant B4)."""
        raa, base = stier

        def hent(ticker, noekkel, *_):
            if ticker == "OSEBX.OL":
                if svaret == "feil":
                    raise requests.HTTPError(f"HTTP 500 med {noekkel}")
                return [] if svaret == "tomt" else {"ikke": "en liste"}
            return serie_til(TIRSDAG_22_09)

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, hent)
        assert fil is not None and len(kall) == 16
        tekst = fil.read_text(encoding="utf-8")
        bilde = json.loads(tekst)
        assert set(bilde["indeks"]) == {"serier", "feil"} and bilde["indeks"]["serier"] == {}
        assert set(bilde["indeks"]["feil"]) == {"OSEBX"}
        assert NOEKKEL not in tekst and NOEKKEL not in ut
        assert set(bilde["serier"]) == {aksje.symbol for aksje in AKSJEUNIVERS}
        assert antall_rader(base, "vurdering") == len(AKSJEUNIVERS)
        assert indeksen_i(base) == ([], None)
        linje = [l for l in ut.splitlines() if l.startswith("Hovedindeksen OSEBX feilet i hentingen")]
        assert len(linje) == 1 and "ingen ny sjanse" in linje[0] and "AD-15" in linje[0]
        assert "Symboler uten data" not in ut and "feilet i hentingen og mangler" not in ut

    def test_en_andre_kjoering_samme_boersdag_gjoer_0_kall(self, stier):
        """Testen i 2.3 med indekskallet, ogsaa naar indeksen feilet: den
        faar ingen ny sjanse (AD-15). Ville feilet hvis sjekken av basen
        krevde indeksen."""
        raa, base = stier

        def uten_indeks(ticker, *_):
            if ticker == "OSEBX.OL":
                raise RuntimeError("nei")
            return serie_til(TIRSDAG_22_09)

        kjoer_23(raa, base, OEYEBLIKK_22_09, uten_indeks)
        (raa / "kurser-raa-2026-09-22.json").unlink()
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30),
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == [] and "0 kall brukt" in ut

    def test_et_nytt_forsoek_tar_ikke_indeksen(self, stier):
        """2.3b: bare aksjene, og forsoeksfila har ingen indeks. Indeksen fra
        hovedhentingen staar. Ville feilet med indeksen i forsoeket (mutant B5)."""
        raa, base = stier
        hovedhenting(stier, feiler=("DNB",))
        foer = indeksen_i(base)
        assert foer[1] == OEYEBLIKK_22_09
        les, _ = kvoter(svar(brukt=16))
        fil, kall, ut = kjoer_23(raa, base, ETTER_30_MIN, les_kvote=les)
        assert fil == raa / "forsoek2-raa-2026-09-22.json" and kall == ["DNB.OL"]
        assert "4 kall igjen av dagens, 4 til nye forsoek" in ut
        assert "indeks" not in json.loads(fil.read_text(encoding="utf-8"))
        assert indeksen_i(base) == foer

    def test_en_base_paa_versjon_5_migreres_og_faar_indeksen(self, tmp_path, stier):
        """Mandag 19.10: den ekte basen staar paa 5. Sjekken leser den (punkt
        a), hentingen henter det som mangler, og basen migreres til 6 naar
        hentingen skriver."""
        from migrering import versjon

        raa, base = stier
        base_paa_versjon(tmp_path, base, 5, uten_kurs=("DNB",))
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30))
        assert fil is not None and len(kall) == 16 and "kunne ikke leses" not in ut
        tilkobling = sqlite3.connect(base)
        try:
            assert versjon(tilkobling) == 6
        finally:
            tilkobling.close()
        assert indeksen_i(base)[1] == OEYEBLIKK_22_09 + timedelta(minutes=30)


class TestAarsskiftet:
    """Story 2.8, punkt c (BH1 i 2.8a): ligger dagen utenfor DEKKEDE_AAR,
    stopper hentingen med 0 kall foer noekkelen og kvoten, saa indeksen aldri
    faar en fersk hentet uten rader. Porten ville ellers tatt bort alle de
    nye dagene og satt en ny tid paa serien."""

    def test_en_dag_utenfor_kalenderen_gir_0_kall_og_indeksen_staar(self, stier):
        from boersdag import DEKKEDE_AAR

        raa, base = stier
        siste_aar = max(DEKKEDE_AAR)
        siste_dag = innevaerende_boersdag(date(siste_aar, 12, 31))
        foerste_kjoering = datetime(siste_dag.year, siste_dag.month, siste_dag.day, 21, 0,
                                    tzinfo=timezone.utc)
        kjoer_23(raa, base, foerste_kjoering, lambda *_: serie_til(siste_dag))
        foer = indeksen_i(base)
        assert foer[1] == foerste_kjoering
        filene = raa_filer(raa)

        neste_aar = datetime(siste_aar + 1, 1, 5, 21, 0, tzinfo=timezone.utc)
        kode, kall, ut = kjoer_23_kode(raa, base, neste_aar, ingen_kall, ingen_noekkel, ingen_kall)
        assert kode == 1 and kall == []
        assert "0 kall brukt" in ut and "NFR-08" in ut
        assert indeksen_i(base) == foer
        assert raa_filer(raa) == filene
