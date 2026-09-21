"""Tester for hentingen. Ingen nettverk.

hent_universet tar hentefunksjonen som argument, saa hele loekka kan kjoeres
mot en falsk henter. Den ekte hent_ett_symbol roeres ikke av noen test her -
den koster kvote, og kvoten testes ikke.
"""

import json
from datetime import date

import pytest

import fetch_prices as fp
from kursdata import AKSJEUNIVERS, SnapshotKilde, nyeste_snapshot


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

    def test_en_feil_stopper_ikke_de_andre(self):
        """NFR-03: manglende data for en aksje stopper ikke hovedflyten."""

        def hent(ticker, *_):
            if ticker == "DNB.OL":
                raise RuntimeError("HTTP 500")
            return falsk_serie()

        resultat = fp.hent_universet("noekkel", "a", "b", hent, lambda _: None)

        assert "DNB" in resultat.feil
        assert "HTTP 500" in resultat.feil["DNB"]
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
    def test_formatet_kan_leses_av_snapshotkilde(self, tmp_path):
        """Det hentingen skriver, skal visningen kunne lese - uten mellomledd."""
        resultat = fp.hent_universet(
            "noekkel", "2025-09-22", "2026-09-21", lambda *_: falsk_serie(), lambda _: None
        )
        bilde = fp.lag_oyeblikksbilde(resultat, "2025-09-22", "2026-09-21", "naa")

        fil = tmp_path / fp.filnavn(date(2026, 9, 22))
        fil.write_text(json.dumps(bilde), encoding="utf-8")

        kilde = SnapshotKilde.fra_fil(fil)
        assert kilde.tidsstempel() == "naa"
        assert len(kilde.serie("EQNR")) == 60

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
