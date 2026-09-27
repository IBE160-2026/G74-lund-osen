"""Tester for hentingen. Ingen nettverk.

hent_universet tar hentefunksjonen som argument, saa hele loekka kan kjoeres
mot en falsk henter. Den ekte hent_ett_symbol kjoeres bare med requests.get
byttet ut (story 2.0), saa ingen test naar nettet eller bruker kvote.
"""

import json
from datetime import date, timedelta

import pytest
import requests

import fetch_prices as fp
from kursdata import AKSJEUNIVERS
from lagring_fil import SnapshotKilde, nyeste_leser, nyeste_snapshot


def falsk_serie(dager: int = 60):
    return [
        {
            "date": f"dag-{i:03d}",
            "close": 100.0 + i,
            "adjusted_close": 100.0 + i,
            "volume": 1000,
        }
        for i in range(dager)
    ]


NOEKKEL = "FALSK-NOEKKEL-123456"


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

    def test_url_kodet_noekkel_fjernes_ogsaa(self):
        """requests URL-koder params. En noekkel med tegn som kodes, maa
        fjernes ogsaa i den formen."""
        noekkel = "ab+c/d=e"

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("feil med api_token=ab%2Bc%2Fd%3De i adressen")
            return falsk_serie()

        resultat = fp.hent_universet(noekkel, "a", "b", hent, lambda _: None)

        assert "ab%2Bc%2Fd%3De" not in resultat.feil["DNB"]
        assert "***" in resultat.feil["DNB"]


class TestSkriverIkkeOver:
    """Story 2.0: et oeyeblikksbilde skrives aldri om (AD-6)."""

    # En annen dato enn i dag, saa en retting som glemmer i_dag, feiler.
    DAG = date(2026, 9, 22)

    def test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel(self, tmp_path):
        katalog = tmp_path / "data"  # finnes ikke fra foer
        linjer = []

        def hent(ticker, noekkel, *_):
            if ticker == "DNB.OL":
                raise RuntimeError(f"feil med {noekkel}")
            return falsk_serie()

        fil = fp.kjoer(katalog, self.DAG, NOEKKEL, hent, linjer.append)

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

        assert fp.kjoer(tmp_path, self.DAG, NOEKKEL, hent, linjer.append) is None
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
            fp.kjoer(tmp_path, self.DAG, NOEKKEL, hent, linjer.append)

        assert slutt.value.code == 1
        assert fil.read_text(encoding="utf-8") == '{"annen kjoering": true}'
        assert any(
            "ikke skrevet over" in l and f"{len(AKSJEUNIVERS)} kall er brukt" in l
            for l in linjer
        )


class TestSvarMedFeilForm:
    """Story 2.0, valg A: et svar med feil form stopper ikke hentingen
    (AD-15, NFR-03)."""

    @pytest.mark.parametrize(
        "svar",
        [
            [{"close": 1.0, "adjusted_close": 1.0, "volume": 1}],  # rad uten date
            [{"date": "2026-09-22"}],  # rad uten prisfeltene eodhd.py leser
            {"code": 403, "message": "Forbidden"},  # feilobjekt i stedet for liste
            ["2026-09-22"],  # liste uten rader
            None,
        ],
        ids=["rad-uten-date", "rad-uten-close", "feilobjekt", "liste-uten-rader", "None"],
    )
    def test_feil_form_gir_feil_for_symbolet_og_de_andre_hentes(self, svar):
        def hent(ticker, *_):
            if ticker == "DNB.OL":
                return svar
            return falsk_serie()

        resultat = fp.hent_universet(NOEKKEL, "a", "b", hent, lambda _: None)

        assert resultat.feil == {"DNB": "svar med feil form"}
        assert len(resultat.serier) == 14
        assert resultat.kall_brukt == 15


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

        assert resultat.kall_brukt == 15
        assert len(kall) == 15
        assert kall == [aksje.ticker for aksje in AKSJEUNIVERS]

    def test_henter_alle_femten_og_ikke_de_fem_gamle(self):
        """Lista hadde fem aksjer fra tidlige tester. Den skal foelge universet."""
        hentet = []
        fp.hent_universet(
            "noekkel", "a", "b",
            lambda t, n, f, ti: hentet.append(t) or falsk_serie(),
            lambda _: None,
        )

        assert len(hentet) == 15
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
        assert len(resultat.serier) == 14

    def test_feilet_symbol_teller_som_brukt_kall(self):
        """Kallet er brukt selv om svaret var ubrukelig. Kvoten maa stemme."""

        def hent(ticker, *_):
            raise RuntimeError("nei")

        resultat = fp.hent_universet("noekkel", "a", "b", hent, lambda _: None)

        assert resultat.kall_brukt == 15
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
        dag = date(2026, 9, 22)
        start = date(2026, 6, 1)

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

        fil = fp.kjoer(tmp_path, dag, NOEKKEL, hent, lambda _: None)
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
    assert resultat.kall_brukt == 15
