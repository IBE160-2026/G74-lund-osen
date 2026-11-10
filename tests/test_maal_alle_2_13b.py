"""Tester for story 2.13b: maalingen av aksjene uten maaling, med bonuskvoten.

Gruppens svar 10.11 kl. 13:48 og 16:31: med valget maales bare aksjene uten
en rad i tabellen omsetning, i samme rekkefoelge som foer, med kallene som er
igjen av dagens og saa bonuskvoten, og valget stopper foer extraLimit blir
under 200. Uten valget er alt som foer, og bonuskvoten brukes aldri.

Kvoten og kallene er falske og teller som EODHD (regel 15): kall nummer 21 og
videre trekker fra extraLimit. Basen ligger i tmp_path (conftest.py, regel
22). Ingen test bruker nett (AD-8).
"""

import re
import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

import fetch_prices
import lagring_fil
import lagring_sqlite
import omsetning
from omsetning import BONUSGULV, Maaling, maal_omsetning, skriv_radene
from test_omsetning import KURS, NYE, ONSDAG, VOLUM, Kvote, _fyll, _lista

BOERSDAG = date(2026, 10, 28)


def _kjoer(tmp_path, kvote, koder, med_bonus=True, klokke=ONSDAG):
    linjer: list[str] = []
    tider = klokke if callable(klokke) else (lambda: klokke)
    kode = maal_omsetning(
        lagring_fil.RAA_KATALOG,
        lagring_sqlite.BASE_STI,
        _lista(tmp_path, koder),
        lambda: "HEMMELIG",
        hent=kvote.hent,
        les_kvote=kvote.les,
        klokke=tider,
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
        # Gjennomgangen (BH1): grunnen er at alle er maalt, ikke kvoten.
        assert "Ingen aksje i lista over Oslo Børs mangler en måling i basen. 0 kall brukt." in ut


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
        assert "med 4 av de 4 kallene som er igjen av dagens og inntil 3 fra bonuskvoten" in ut
        assert "Måler omsetningen for 7 av de 10 aksjene uten måling" in ut
        assert "3 aksjer uten måling venter til en senere kjøring." in ut
        assert "API-kall brukt: 7." in ut and "Kall fra bonuskvoten: 3." in ut

    def test_ingen_kall_fra_bonusen_naar_den_er_200(self, tmp_path):
        """Ville feilet hvis valget tok et kall fra bonusen naar den alt
        staar paa 200 og dagens er brukt."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20, bonus=BONUSGULV)
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert (kode, kvote.kall, kvote.bonus) == (0, [], BONUSGULV)
        assert "bonuskvoten har 200, ikke over 200. 6 aksjer uten måling venter. 0 kall brukt." in ut

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
        assert "Kall fra bonuskvoten: 3." in ut

    def test_kallene_fra_bonusen_telles_uten_det_andre_bruker_mellom_kallene(self, tmp_path):
        """BH3, ECH6 og VG3. Ville feilet hvis linja talte forskjellen fra
        starten: noe annet bruker 5 fra bonusen mellom det foerste og det andre
        kallet, og valget tok selv 3."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20, bonus=BONUSGULV + 10)
        ekte_les = kvote.les
        lest = []

        def les(nokkel):
            lest.append(1)
            if len(lest) == 4:
                kvote.bonus -= 5
            return ekte_les(nokkel)

        kvote.les = les
        kode, ut = _kjoer(tmp_path, kvote, ["NYA", "NYB", "NYC"])
        assert kode == 0, ut
        assert len(kvote.kall) == 3 and kvote.bonus == BONUSGULV + 2
        assert "Kall fra bonuskvoten: 3." in ut

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
        _med_rad("NYA")
        kvote = Kvote(brukt=16, bonus=463)
        kode, ut = _kjoer(tmp_path, kvote, [*NYE, "NYG"], med_bonus=False)
        assert kode == 0, ut
        # Gjennomgangen (BH5): NYA har en rad og maales sist, som foer.
        assert kvote.kall == ["NYB.OL", "NYC.OL", "NYD.OL", "NYE.OL"]
        assert kvote.bonus == 463
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


class TestGjennomgangen:
    """Funnene fra gjennomgangen 10.11 (BH, ECH og VG i spesifikasjonen)."""

    @pytest.mark.parametrize("oslo", ["00:05", "00:40", "05:59"])
    def test_etter_midnatt_gjelder_kvelden_foer(self, tmp_path, oslo):
        """ECH1. Ville feilet hvis valget etter midnatt i Oslo regnet den nye
        dagen som boersdag og ventet paa kursene for den: torsdag 29.10 etter
        midnatt i Oslo er kursene for onsdag 28.10 hentet."""
        _fyll(BOERSDAG)
        timer, minutter = map(int, oslo.split(":"))
        klokke = datetime(2026, 10, 28, 23, 0, tzinfo=timezone.utc) + timedelta(hours=timer, minutes=minutter)
        kvote = Kvote(brukt=0, dato=klokke.date())
        kode, ut = _kjoer(tmp_path, kvote, ["NYA"], klokke=klokke)
        assert (kode, kvote.kall) == (0, ["NYA.OL"]), ut
        assert "til 2026-10-28" in ut

    def test_kl_6_gjelder_dagen_selv(self, tmp_path):
        """ECH1. Ville feilet hvis kvelden foer gjaldt hele dagen: torsdag kl.
        06:00 i Oslo er boersdagen torsdag, og kursene for den mangler."""
        _fyll(BOERSDAG)
        klokke = datetime(2026, 10, 29, 5, 0, tzinfo=timezone.utc)
        kvote = Kvote(brukt=0, dato=klokke.date())
        kode, ut = _kjoer(tmp_path, kvote, ["NYA"], klokke=klokke)
        assert (kode, kvote.kall) == (1, []), ut

    def test_uten_valget_venter_maalingen_etter_midnatt_som_foer(self, tmp_path):
        """ECH1. Ville feilet hvis rettingen endret maalingen uten valget, som
        venter etter midnatt (svaret 29.10 kl. 09:20, b)."""
        _fyll(BOERSDAG)
        klokke = datetime(2026, 10, 28, 23, 5, tzinfo=timezone.utc)
        kvote = Kvote(brukt=0, dato=klokke.date())
        kode, ut = _kjoer(tmp_path, kvote, ["NYA"], med_bonus=False, klokke=klokke)
        assert (kode, kvote.kall) == (1, []), ut

    def test_stopper_etter_tre_feil_paa_rad(self, tmp_path):
        """ECH2. Ville feilet hvis valget brukte bonuskvoten paa kall som
        feiler: tre feil paa rad som ikke er 404, og valget stopper."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20)
        ekte_hent = kvote.hent

        def hent(ticker, *argumenter):
            ekte_hent(ticker, *argumenter)
            raise TimeoutError("tidsavbrudd")

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert kode == 1, ut
        assert kvote.kall == ["NYA.OL", "NYB.OL", "NYC.OL"]
        assert "3 kall på rad feilet" in ut

    def test_en_feil_innimellom_stopper_ikke(self, tmp_path):
        """ECH2. Ville feilet hvis feilene ble talt uten at en maaling
        nullstilte tellingen."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20)
        ekte_hent = kvote.hent

        def hent(ticker, *argumenter):
            svar = ekte_hent(ticker, *argumenter)
            if ticker in {"NYA.OL", "NYB.OL", "NYD.OL", "NYE.OL"}:
                raise TimeoutError("tidsavbrudd")
            return svar

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert kode == 0, ut
        assert len(kvote.kall) == 6

    def test_404_teller_ikke_som_feil_paa_rad(self, tmp_path):
        """ECH2. Ville feilet hvis et svar om at tickeren ikke finnes, stoppet
        valget: det gir en rad, som foer."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20)
        ekte_hent = kvote.hent

        def hent(ticker, *argumenter):
            ekte_hent(ticker, *argumenter)
            raise RuntimeError("HTTP 404")

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert kode == 0, ut
        assert len(kvote.kall) == 6 and len(_symbolene_i_basen()) == 6

    def test_stopper_naar_datoen_i_gmt_skifter(self, tmp_path):
        """VG1. Ville feilet hvis valget gikk videre inn i en ny dag i GMT:
        klokka passerer midnatt i GMT etter det foerste kallet."""
        _fyll(BOERSDAG)
        tider = iter([ONSDAG, ONSDAG])
        kvote = Kvote(brukt=0)
        kode, ut = _kjoer(tmp_path, kvote, NYE, klokke=lambda: next(tider, ONSDAG + timedelta(hours=3)))
        assert kode == 1, ut
        assert kvote.kall == ["NYA.OL"] and _symbolene_i_basen() == ["NYA"]
        assert "Datoen i GMT er ikke lenger 2026-10-28." in ut

    def test_gaarsdagens_dato_foer_foerste_kall_er_0_brukt(self, tmp_path):
        """BH6. Ville feilet hvis apiRequestsDate paa gaarsdagen ga kall fra
        bonusen: alle 20 av dagens er igjen."""
        _fyll(BOERSDAG)
        kvote = Kvote(brukt=20, dato=date(2026, 10, 27), bonus=BONUSGULV)

        def ny_dag(k):
            if k.dato != BOERSDAG:
                k.dato, k.brukt = BOERSDAG, 0

        kvote.foer_kall = ny_dag
        kode, ut = _kjoer(tmp_path, kvote, NYE)
        assert kode == 0, ut
        assert len(kvote.kall) == 6 and kvote.bonus == BONUSGULV

    def test_ingen_tall_fra_kildene_i_utskriften(self, tmp_path):
        """VG2. Ville feilet hvis utskriften med valget hadde en kurs, et
        volum eller en median fra de falske svarene."""
        _fyll(BOERSDAG)
        kode, ut = _kjoer(tmp_path, Kvote(brukt=16), NYE)
        assert kode == 0, ut
        for tall in (str(KURS), str(VOLUM), "123", "98765"):
            assert tall not in ut
        uten_datoer = re.sub(r"\d{4}-\d{2}-\d{2}", "", ut)
        assert [int(t) for t in re.findall(r"\d+", uten_datoer) if int(t) >= 100] == [463, 200, 461]
