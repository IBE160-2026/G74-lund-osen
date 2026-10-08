"""Tester for hentingen. Ingen nettverk.

hent_universet tar hentefunksjonen som argument, saa hele loekka kan kjoeres
mot en falsk henter. Den ekte hent_ett_symbol kjoeres bare med requests.get
byttet ut (story 2.0), saa ingen test naar nettet eller bruker kvote.
"""

import copy
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
from kursdata import AKSJEUNIVERS
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

        fil = fp.kjoer(katalog, tmp_path / "ose.db", self.OEYEBLIKK, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)

        assert fil == katalog / fp.filnavn(self.DAG)
        tekst = fil.read_text(encoding="utf-8")
        assert NOEKKEL not in tekst
        bilde = json.loads(tekst)
        assert (bilde["from"], bilde["to"]) == fp.bygg_intervall(self.DAG)
        assert len(bilde["serier"]) == len(AKSJEUNIVERS) - 1
        assert "***" in bilde["feil"]["DNB"]
        assert SnapshotKilde.fra_fil(fil) is not None
        assert any("Lagret" in l for l in linjer)
        assert any(f"API-kall brukt: {len(AKSJEUNIVERS)}" in l for l in linjer)

    def test_dagens_fil_finnes_og_ingen_kall_brukes(self, tmp_path):
        fil = tmp_path / fp.filnavn(self.DAG)
        fil.write_text('{"gammel": true}', encoding="utf-8")
        linjer = []

        def hent(*_):
            pytest.fail("ingen kall skal brukes naar dagens fil finnes")

        assert fp.kjoer(tmp_path, tmp_path / "ose.db", self.OEYEBLIKK, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote) is None
        assert fil.read_text(encoding="utf-8") == '{"gammel": true}'
        assert any("finnes allerede" in l and "0 kall brukt" in l for l in linjer)

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
            "ikke skrevet over" in l and f"{len(AKSJEUNIVERS)} kall er brukt" in l
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

        fil = fp.kjoer(tmp_path, tmp_path / "ose.db", OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
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

        fil = fp.kjoer(tmp_path, tmp_path / "ose.db", OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)
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

        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)

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

        fp.kjoer(raa, base, etter, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)

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

    def test_fire_dagers_opphold_fylles_med_15_kall(self, stier):
        """K9: basen mangler fire boersdager. Etter neste henting er de der,
        og hentingen brukte 15 kall. Ville feilet hvis kjoer bare skrev
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

        assert len(kall) == 15
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

        def spion(base_sti, serier, hentet, fil, skriv):
            kall.append((set(serier), hentet))
            return ekte(base_sti, serier, hentet, fil, skriv)

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

        fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)

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
        fp.kjoer(raa, base, senere, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)

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
        fil = fp.kjoer(raa, base, OEYEBLIKK_22_09, NOEKKEL, hent, linjer.append, les_kvote=nok_kvote)

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
        assert len(kall) == len(AKSJEUNIVERS)

    def test_flagget_henter_foer_kl_22_med_dagens_navn(self, stier):
        """Ville feilet hvis flagget ble ignorert (M6)."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, _utc(2026, 9, 22, 10, 0),
                                 hent_foer_kl_22=True)
        assert fil == raa / "kurser-raa-2026-09-22.json"
        assert len(kall) == len(AKSJEUNIVERS)
        assert "--hent-foer-kl-22" in ut

    def test_dag_som_ikke_er_boersdag_har_ingen_tidskontroll(self, stier):
        """Loerdag kl. 12: basen avgjoer. Ville feilet hvis tidskontrollen
        gjaldt alle dager (M7)."""
        raa, base = stier
        fil, kall, _ = kjoer_23(raa, base, LOERDAG_26_09_KL_12,
                                lambda *_: serie_til(FREDAG_25_09))
        assert fil == raa / "kurser-raa-2026-09-25.json"
        assert len(kall) == len(AKSJEUNIVERS)

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

        kjoer_23(raa, base, OEYEBLIKK_22_09, uten_dnb)
        (raa / "kurser-raa-2026-09-22.json").unlink()

        fil, kall, _ = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30))
        assert fil is not None and len(kall) == len(AKSJEUNIVERS)

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
        assert len(kall) == len(AKSJEUNIVERS)
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
        assert len(kall) == len(AKSJEUNIVERS)
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

        fil, kall, ut = kjoer_23(raa, base, LOERDAG_26_09_KL_12,
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
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
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09, les_kvote=kvote(brukt=5))
        assert fil is not None and len(kall) == 15
        assert "15 kall igjen" in ut and "bonus" not in ut

    def test_under_15_med_bonus_henter_og_sier_hvor_mange(self, stier):
        """Ville feilet hvis bonusen ikke ble talt med (K2)."""
        raa, base = stier
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09,
                                 les_kvote=kvote(brukt=10, bonus=463))
        assert fil is not None and len(kall) == 15
        assert "5 kall tas fra bonuskvoten" in ut

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
        assert fil is not None and len(kall) == 15
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
        assert "0 kall igjen av dagens" in ut and "trenger 15" in ut and "0 kall brukt" in ut

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
        assert fil is not None and len(kall) == 15
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
        assert len(kall) == len(AKSJEUNIVERS)

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

        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=30),
                                 ingen_kall, ingen_noekkel, ingen_kall)
        assert fil is None and kall == []
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
        """kjoer gir len(AKSJEUNIVERS), ikke et tall skrevet inn."""
        raa, base = stier
        sett = []
        ekte = fp.vurder_kvote

        def spion(igjen, bonus, antall):
            sett.append(antall)
            return ekte(igjen, bonus, antall)

        monkeypatch.setattr(fp, "vurder_kvote", spion)
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert sett == [len(AKSJEUNIVERS)]


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
        assert fil is not None and len(kall) == len(AKSJEUNIVERS)
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
        assert fil is not None and len(kall) == len(AKSJEUNIVERS)
        assert "Kvoten: 0 kall igjen av dagens. 15 kall tas fra bonuskvoten" in ut

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
