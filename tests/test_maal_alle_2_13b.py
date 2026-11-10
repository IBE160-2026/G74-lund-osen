"""Tester for story 2.13b: maalingen av aksjene uten maaling, med bonuskvoten.

Gruppens svar 10.11 kl. 13:48 og 16:31: med valget maales bare aksjene uten
en rad i tabellen omsetning, i samme rekkefoelge som foer, med kallene som er
igjen av dagens og saa bonuskvoten, og valget stopper foer extraLimit blir
under 200. Uten valget er alt som foer, og bonuskvoten brukes aldri.

Kvoten og kallene er falske og teller som EODHD (regel 15): kall nummer 21 og
videre trekker fra extraLimit. Basen ligger i tmp_path (conftest.py, regel
22). Ingen test bruker nett (AD-8).
"""

import sqlite3
from datetime import date

import pytest

import fetch_prices
import lagring_fil
import lagring_sqlite
import omsetning
from omsetning import BONUSGULV, Maaling, maal_omsetning, skriv_radene
from test_omsetning import NYE, ONSDAG, Kvote, _fyll, _lista

BOERSDAG = date(2026, 10, 28)


def _kjoer(tmp_path, kvote, koder, med_bonus=True):
    linjer: list[str] = []
    kode = maal_omsetning(
        lagring_fil.RAA_KATALOG,
        lagring_sqlite.BASE_STI,
        _lista(tmp_path, koder),
        lambda: "HEMMELIG",
        hent=kvote.hent,
        les_kvote=kvote.les,
        klokke=lambda: ONSDAG,
        skriv=linjer.append,
        med_bonus=med_bonus,
    )
    return kode, "\n".join(linjer)


def _med_rad(symbol: str) -> None:
    """En rad i omsetning for symbolet, som en tidligere maaling."""
    skriv_radene(
        lagring_sqlite.BASE_STI,
        "2026-10-27T21:00:00+00:00",
        date(2026, 7, 28),
        date(2026, 10, 27),
        [Maaling(symbol, 60, 0, 0, 1.0, None)],
    )


def _symbolene_i_basen() -> list[str]:
    c = sqlite3.connect(f"file:{lagring_sqlite.BASE_STI.as_posix()}?mode=ro", uri=True)
    try:
        return [s for (s,) in c.execute("SELECT symbol FROM omsetning ORDER BY rowid")]
    finally:
        c.close()


class TestUtvalget:
    def test_bare_aksjene_uten_rad_i_samme_rekkefoelge(self, tmp_path):
        """Ville feilet hvis en aksje med en rad i omsetning ble maalt paa
        nytt, hvis en aksje som bare er maalt i malinger.md ble hoppet over,
        eller hvis rekkefoelgen ikke var den fra rekkefoelge(): de aldri
        maalte foerst i lista sin rekkefoelge, saa de eldste i malinger.md."""
        _fyll(BOERSDAG)
        _med_rad("NYB")
        kvote = Kvote(brukt=0)
        # 2020 er maalt 23.10 (§41), AKER 02.10 (§15): AKER er eldst.
        kode, ut = _kjoer(tmp_path, kvote, ["2020", "NYA", "NYB", "AKER", "NYC"])
        assert kode == 0, ut
        assert kvote.kall == ["NYA.OL", "NYC.OL", "AKER.OL", "2020.OL"]
        assert _symbolene_i_basen() == ["NYB", "NYA", "NYC", "AKER", "2020"]

    def test_aksjene_i_appens_liste_er_ikke_med(self, tmp_path):
        """Ville feilet hvis valget maalte en aksje i appens liste, som ikke
        har en rad i omsetning (svaret kl. 16:31, punkt 2)."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=0)
        kode, ut = _kjoer(tmp_path, kvote, ["EQNR", "NYA", "MOWI"])
        assert kode == 0, ut
        assert kvote.kall == ["NYA.OL"]

    def test_ingen_kall_naar_alle_har_en_rad(self, tmp_path):
        """Ville feilet hvis valget maalte de eldste paa nytt, som maalingen
        uten valget gjoer naar alle er maalt."""
        _fyll(BOERSDAG)
        for symbol in ("NYA", "NYB"):
            _med_rad(symbol)
        kvote = Kvote(brukt=0)
        kode, ut = _kjoer(tmp_path, kvote, ["NYA", "NYB"])
        assert (kode, kvote.kall) == (0, [])
        assert "0 kall brukt" in ut


class TestTaket:
    def test_dagens_foerst_og_saa_bonusen_til_200_staar_igjen(self, tmp_path):
        """Ville feilet hvis valget brukte bonuskvoten foer dagens kall, eller
        tok kallet som ga 199: med 16 brukt og 203 i bonusen er det 4 av
        dagens og 3 fra bonusen, og tre aksjer venter."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=16, bonus=BONUSGULV + 3)
        koder = [*NYE, "NYG", "NYH", "NYI", "NYJ"]
        kode, ut = _kjoer(tmp_path, kvote, koder)
        assert kode == 0, ut
        assert kvote.kall == [f"{k}.OL" for k in koder[:7]]
        assert (kvote.brukt, kvote.bonus) == (23, BONUSGULV)
        assert "med 4 av de 4 kallene som er igjen av dagens og 3 fra bonuskvoten" in ut
        assert "API-kall brukt: 7." in ut and "Kall fra bonuskvoten: 3." in ut

    def test_ingen_kall_fra_bonusen_naar_den_er_200(self, tmp_path):
        """Ville feilet hvis valget tok et kall fra bonusen naar den alt
        staar paa 200 og dagens er brukt."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20, bonus=BONUSGULV)
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert (kode, kvote.kall, kvote.bonus) == (0, [], BONUSGULV)
        assert "0 kall brukt" in ut

    def test_dagens_brukes_selv_om_bonusen_er_under_200(self, tmp_path):
        """Ville feilet hvis bonusen under 200 stoppet kallene av dagens,
        som ikke trekker fra den."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=18, bonus=BONUSGULV - 50)
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert kode == 0, ut
        assert kvote.kall == ["NYA.OL", "NYB.OL"] and kvote.bonus == BONUSGULV - 50


class TestKontrollenFoerHvertKall:
    def test_stopper_naar_noe_annet_bruker_bonusen_underveis(self, tmp_path):
        """Ville feilet hvis valget bare regnet taket foer det foerste kallet:
        noe annet bruker to kall fra bonusen etter det foerste, og neste kall
        ville gitt 199. Det som er maalt, lagres."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20, bonus=BONUSGULV + 3)
        ekte_hent = kvote.hent

        def hent(*argumenter):
            svar = ekte_hent(*argumenter)
            kvote.bonus -= 2
            return svar

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert kode == 1, ut
        assert kvote.kall == ["NYA.OL"] and kvote.bonus == BONUSGULV
        assert "neste kall ville gitt under 200" in ut
        assert _symbolene_i_basen() == ["NYA"]

    def test_stopper_naar_bonusen_er_under_200_etter_et_kall(self, tmp_path):
        """Ville feilet hvis valget gikk videre naar extraLimit sto under 200
        etter et kall av dagens."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=0, bonus=BONUSGULV + 5)
        ekte_hent = kvote.hent

        def hent(*argumenter):
            svar = ekte_hent(*argumenter)
            kvote.bonus = BONUSGULV - 1
            return svar

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert (kode, kvote.kall) == (1, ["NYA.OL"]), ut
        assert "under 200" in ut


class TestUtenValget:
    def test_uten_valget_brukes_bonusen_aldri(self, tmp_path):
        """Ville feilet hvis maalingen uten valget brukte bonuskvoten eller
        hoppet over en aksje med en rad: som foer, 4 kall med 16 brukt."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=16, bonus=463)
        kode, ut = _kjoer(tmp_path, kvote, [*NYE, "NYG"], med_bonus=False)
        assert kode == 0, ut
        assert (len(kvote.kall), kvote.bonus) == (4, 463)
        assert "Bonuskvoten brukes aldri." in ut and "Kall fra bonuskvoten" not in ut

    def test_valget_i_hentekommandoen(self, tmp_path, monkeypatch):
        """Ville feilet hvis --med-bonuskvoten ikke naadde maal_omsetning: med
        19 brukt tar valget 1 av dagens og 1 fra bonusen."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=19)
        monkeypatch.setattr(fetch_prices, "hent_ett_symbol", kvote.hent)
        monkeypatch.setattr(fetch_prices, "hent_kvote", kvote.les)
        monkeypatch.setattr(fetch_prices, "hent_api_nokkel", lambda: "HEMMELIG")
        monkeypatch.setattr(fetch_prices, "naa", lambda: ONSDAG)
        monkeypatch.setattr(omsetning, "LISTEFIL", _lista(tmp_path, ["NYA", "NYB"]))
        with pytest.raises(SystemExit) as utgang:
            fetch_prices.main(["--maal-omsetning", "--med-bonuskvoten"])
        assert utgang.value.code == 0
        assert kvote.kall == ["NYA.OL", "NYB.OL"] and kvote.bonus == 462

    @pytest.mark.parametrize("argumenter", [["--med-bonuskvoten"], ["--les-inn", "x.json", "--med-bonuskvoten"]])
    def test_valget_gjelder_bare_med_maal_omsetning(self, argumenter):
        """Ville feilet hvis --med-bonuskvoten kunne gis uten --maal-omsetning,
        for eksempel til hentingen."""
        with pytest.raises(SystemExit) as utgang:
            fetch_prices.main(argumenter)
        assert utgang.value.code == 2
