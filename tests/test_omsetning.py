"""Tester for maalingen av omsetning - story 2.13, FR-413, NFR-01, AD-6, AD-16.

Avgjoerelsen 28.10 kl. 22:17: jobben kjoerer maalingen etter hentingen med
alle kallene som er igjen den dagen i GMT, ogsaa paa dager boersen er stengt,
hentingen og nye forsoek faar kallene foerst, bonuskvoten brukes aldri, og
naar hele lista er maalt, maales de eldste paa nytt foerst.

Kvoten og kallene er falske og teller som EODHD (regel 15): kall nummer 21 og
videre trekker fra extraLimit uten aa stoppe. Basen og data/raa/ ligger i
tmp_path (conftest.py), aldri i data/ (regel 22). Ingen test bruker nett.
"""

import ast
import json
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import fetch_prices
import lagring_fil
import lagring_sqlite
import omsetning
from kursdata import AKSJEUNIVERS, Kursrad
from lagring_sqlite import MIGRASJONSKATALOG, SqliteKurslager, aapne_base
from migrering import migrer, siste_versjon, versjon
from omsetning import MAALT_I_MALINGER, maal_omsetning, maalt_i_malingene, regn_ut, rekkefoelge, vindu
from test_indeks import katalog_til

ROT = Path(__file__).resolve().parent.parent
MALINGER = ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20" / "malinger.md"

# Onsdag 28.10 kl. 22:30 i Oslo (21:30 GMT), etter hentingen. Boersdagen er 28.10.
ONSDAG = datetime(2026, 10, 28, 21, 30, tzinfo=timezone.utc)
# Loerdag 31.10 kl. 13:00 i Oslo. Boersdagen er fredag 30.10.
LOERDAG = datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc)

# Kurs og volum som ikke finnes andre steder i utskriften.
KURS = 123.4567
VOLUM = 98765

NYE = ["NYA", "NYB", "NYC", "NYD", "NYE", "NYF"]


class Kvote:
    """/api/user og /api/eod som EODHD teller dem: kall over dailyRateLimit
    trekker fra extraLimit. dato er apiRequestsDate."""

    def __init__(self, brukt=16, dato=date(2026, 10, 28), grense=20, bonus=463):
        self.brukt, self.dato, self.grense, self.bonus = brukt, dato, grense, bonus
        self.kall: list[str] = []
        self.foer_kall = None

    def les(self, nokkel):
        return {
            "apiRequests": self.brukt,
            "apiRequestsDate": self.dato.isoformat(),
            "dailyRateLimit": self.grense,
            "extraLimit": self.bonus,
            "email": "ikke@les.dette",
        }

    def hent(self, ticker, nokkel, fra, til):
        if self.foer_kall:
            self.foer_kall(self)
        self.kall.append(ticker)
        if self.brukt >= self.grense:
            self.bonus -= 1
        self.brukt += 1
        start = date.fromisoformat(fra)
        return [
            {"date": (start + timedelta(days=i)).isoformat(), "close": KURS, "volume": VOLUM * (i % 3)}
            for i in range(10)
        ]


def _fyll(boersdag: date, uten: tuple[str, ...] = ()) -> None:
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = SqliteKurslager(tilkobling)
        for aksje in AKSJEUNIVERS:
            if aksje.symbol not in uten:
                rad = Kursrad(dato=boersdag, slutt=100.0, justert_slutt=100.0, volum=1000)
                lager.erstatt_serie(aksje.symbol, [rad], ONSDAG)
    finally:
        tilkobling.close()


def _lista(tmp_path: Path, koder: list[str]) -> Path:
    sti = tmp_path / "symbolliste.json"
    rader = [{"Code": kode, "Type": "Common Stock", "Name": kode} for kode in koder]
    rader.insert(1, {"Code": "ETFEN", "Type": "ETF", "Name": "ETFEN"})
    sti.write_text(json.dumps(rader), encoding="utf-8")
    return sti


def _kjoer(tmp_path, kvote, klokke=ONSDAG, koder=None, utskrift=None):
    tider = klokke if callable(klokke) else (lambda: klokke)
    linjer = utskrift if utskrift is not None else []
    kode = maal_omsetning(
        lagring_fil.RAA_KATALOG,
        lagring_sqlite.BASE_STI,
        _lista(tmp_path, NYE if koder is None else koder),
        lambda: "HEMMELIG",
        hent=kvote.hent,
        les_kvote=kvote.les,
        klokke=tider,
        skriv=linjer.append,
    )
    return kode, "\n".join(linjer)


def _radene() -> list[tuple]:
    c = sqlite3.connect(f"file:{lagring_sqlite.BASE_STI.as_posix()}?mode=ro", uri=True)
    try:
        return c.execute(
            "SELECT symbol, maalt, fra, til, handelsdager, dager_uten_volum, rader_uten_tall, "
            "median_omsetning, feil FROM omsetning ORDER BY maalt, rowid"
        ).fetchall()
    finally:
        c.close()


class TestKvoten:
    def test_bruker_alle_kallene_som_er_igjen_og_aldri_bonuskvoten(self, tmp_path):
        """Ville feilet hvis et kall gikk fra bonuskvoten: med 16 brukt er 4
        igjen, og seks aksjer venter. Kall nummer 21 ville trukket fra
        extraLimit, som den falske kvoten gjoer."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        kode, ut = _kjoer(tmp_path, kvote)
        assert kode == 0, ut
        assert kvote.kall == ["NYA.OL", "NYB.OL", "NYC.OL", "NYD.OL"]
        assert (kvote.brukt, kvote.bonus) == (20, 463)
        assert "API-kall brukt: 4." in ut

    def test_ingen_kall_naar_dagens_er_brukt(self, tmp_path):
        """Ville feilet hvis et kall gikk fra bonuskvoten naar alle 20 er brukt."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=20)
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall, kvote.bonus) == (0, [], 463), ut
        assert "0 kall brukt" in ut

    def test_stopper_naar_extraLimit_endres_etter_et_kall(self, tmp_path):
        """Ville feilet hvis stoppen ved endret extraLimit manglet: noe annet
        bruker et kall fra bonuskvoten under det siste av de 2 kallene, saa
        bare kontrollen etter kallet kan se det (mutanten)."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=18)

        def en_annen_bruker_bonusen(k):
            if len(k.kall) == 1:
                k.bonus -= 1

        kvote.foer_kall = en_annen_bruker_bonusen
        kode, ut = _kjoer(tmp_path, kvote)
        assert kode == 1
        assert kvote.kall == ["NYA.OL", "NYB.OL"]
        assert "STOPP: extraLimit er endret fra 463 til 462" in ut
        assert [rad[0] for rad in _radene()] == ["NYA", "NYB"]

    def test_stopper_foer_et_kall_naar_extraLimit_er_endret(self, tmp_path):
        """Ville feilet hvis extraLimit bare ble sjekket etter kallene: den
        er endret mellom foerste lesing og foerste kall."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        lest = []

        def les(nokkel):
            svar = Kvote.les(kvote, nokkel)
            lest.append(1)
            if len(lest) == 2:
                svar["extraLimit"] = 462
            return svar

        kvote.les = les
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall) == (1, []), ut


class TestDatoenIGMT:
    def test_ingen_kall_etter_at_datoen_i_gmt_har_skiftet(self, tmp_path):
        """Ville feilet hvis et kall ble gjort med en annen dato i GMT: klokka
        passerer midnatt GMT etter foerste kall."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        tider = iter([ONSDAG, ONSDAG, ONSDAG.replace(hour=23, minute=59, second=59) + timedelta(seconds=2)])
        kode, ut = _kjoer(tmp_path, kvote, klokke=lambda: next(tider))
        assert kode == 1
        assert kvote.kall == ["NYA.OL"]
        assert "Datoen i GMT er ikke lenger 2026-10-28" in ut

    def test_stopper_naar_kvoten_staar_paa_en_annen_dato_etter_et_kall(self, tmp_path):
        """Ville feilet hvis et kall ble gjort med en annen dato i GMT: etter
        foerste kall staar apiRequestsDate paa neste dag."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        ekte_hent = kvote.hent

        def hent(*argumenter):
            svar = ekte_hent(*argumenter)
            kvote.dato = date(2026, 10, 29)
            return svar

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall) == (1, ["NYA.OL"]), ut

    def test_ingen_kall_naar_kvoten_staar_paa_en_senere_dato(self, tmp_path):
        """Ville feilet hvis et kall ble gjort med en annen dato i GMT: kvoten
        staar paa 29.10 og klokka paa 28.10."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=0, dato=date(2026, 10, 29))
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall) == (1, []), ut

    def test_en_dag_boersen_er_stengt_brukes_alle_20(self, tmp_path):
        """Avgjoerelsen kl. 22:17, b): ogsaa paa dager boersen er stengt. Paa
        en loerdag staar apiRequestsDate paa fredag til foerste kall, og det
        er 0 brukt i dag (regel 15). Etter foerste kall staar den paa loerdag."""
        _fyll(date(2026, 10, 30))
        koder = [f"N{i:02d}" for i in range(25)]
        kvote = Kvote(brukt=16, dato=date(2026, 10, 30))
        ekte_hent = kvote.hent

        def hent(*argumenter):
            if kvote.dato != date(2026, 10, 31):
                kvote.dato, kvote.brukt = date(2026, 10, 31), 0
            return ekte_hent(*argumenter)

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote, klokke=LOERDAG, koder=koder)
        assert kode == 0, ut
        assert kvote.kall == [f"{k}.OL" for k in koder[:20]]
        assert (kvote.brukt, kvote.bonus) == (20, 463)
        assert list(lagring_fil.RAA_KATALOG.glob("*-raa-*.json")) == [
            lagring_fil.RAA_KATALOG / "omsetning1-raa-2026-10-30.json"
        ]


class TestHentingenFoerst:
    def test_maaler_ikke_naar_en_aksje_mangler_kursen(self, tmp_path):
        """Ville feilet hvis det ble maalt mens en aksje manglet kursen: EQNR
        mangler 28.10, saa kallene staar til et nytt forsoek."""
        _fyll(date(2026, 10, 28), uten=("EQNR",))
        kvote = Kvote(brukt=16)
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall) == (1, []), ut
        assert "EQNR mangler kursen for 2026-10-28" in ut and "0 kall brukt" in ut

    def test_maaler_ikke_paa_en_boersdag_foer_hentingen(self, tmp_path):
        """Ville feilet hvis det ble maalt paa en boersdag foer hentingen hadde
        dagens kurser: basen har bare tirsdagen."""
        _fyll(date(2026, 10, 27))
        kvote = Kvote(brukt=0)
        kode, ut = _kjoer(tmp_path, kvote, klokke=ONSDAG.replace(hour=10))
        assert (kode, kvote.kall) == (1, []), ut
        assert "mangler kursen for 2026-10-28" in ut

    def test_maaler_ikke_uten_base(self, tmp_path):
        kvote = Kvote(brukt=0)
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall) == (1, []), ut
        assert not lagring_sqlite.BASE_STI.exists()


class TestSvarene2319:
    """Avgjoerelsen 28.10 kl. 23:19, a) og b)."""

    def test_gaarsdagens_dato_foer_foerste_kall_er_0_brukt_i_dag(self, tmp_path):
        """Ville feilet hvis gaarsdagens dato foer foerste kall stoppet
        maalingen, eller kallene fra i gaar ble trukket fra dagens: kvoten
        staar paa 27.10 med 20 brukt til foerste kall, og alle 6 maales."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=20, dato=date(2026, 10, 27))
        ekte_hent = kvote.hent

        def hent(*argumenter):
            if kvote.dato != date(2026, 10, 28):
                kvote.dato, kvote.brukt = date(2026, 10, 28), 0
            return ekte_hent(*argumenter)

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote)
        assert kode == 0, ut
        assert kvote.kall == [f"{kode}.OL" for kode in NYE]
        assert (kvote.brukt, kvote.bonus) == (6, 463)

    def test_vinduet_staar_ved_hvert_tall(self, tmp_path):
        """Ville feilet hvis vinduet ikke var tre maaneder bakover fra
        boersdagen, eller ikke sto ved hvert tall: maalingen tirsdag og
        onsdag gir hver sin fra og til i radene, og loerdag er vinduet fra
        fredagen, ikke fra loerdagen (gjennomgangen 29.10, VG1)."""
        _fyll(date(2026, 10, 27))
        assert _kjoer(tmp_path, Kvote(brukt=18, dato=date(2026, 10, 27)), klokke=ONSDAG - timedelta(days=1))[0] == 0
        _fyll(date(2026, 10, 28))
        assert _kjoer(tmp_path, Kvote(brukt=18), klokke=ONSDAG)[0] == 0
        _fyll(date(2026, 10, 30))
        assert _kjoer(tmp_path, Kvote(brukt=19, dato=date(2026, 10, 31)), klokke=LOERDAG)[0] == 0
        radene = [(rad[0], rad[2], rad[3]) for rad in _radene()]
        assert radene == [
            ("NYA", "2026-07-27", "2026-10-27"),
            ("NYB", "2026-07-27", "2026-10-27"),
            ("NYC", "2026-07-28", "2026-10-28"),
            ("NYD", "2026-07-28", "2026-10-28"),
            ("NYE", "2026-07-30", "2026-10-30"),
        ]


class TestKl2345:
    """Avgjoerelsen 28.10 kl. 23:19, d): mangler en av de 15 kursen, gaar
    maalingen kl. 23:45 med kallene som er igjen etter nye forsoek."""

    def test_venter_til_23_45_naar_en_kurs_mangler(self, tmp_path):
        """Ville feilet hvis maalingen gikk foer 23:45 med en kurs som mangler:
        kl. 23:44:59 i Oslo venter den som foer."""
        _fyll(date(2026, 10, 28), uten=("EQNR",))
        kvote = Kvote(brukt=16)
        kode, ut = _kjoer(tmp_path, kvote, klokke=datetime(2026, 10, 28, 22, 44, 59, tzinfo=timezone.utc))
        assert (kode, kvote.kall) == (1, []), ut
        assert "EQNR mangler kursen for 2026-10-28" in ut and "0 kall brukt" in ut

    def test_gaar_fra_23_45_naar_en_kurs_mangler(self, tmp_path):
        """Ville feilet hvis maalingen ikke gikk fra 23:45: EQNR og MOWI
        mangler, og kl. 23:45:00 i Oslo brukes de 4 kallene som er igjen.
        Utskriften sier hvor mange av de 15 som mangler, og hvilke."""
        _fyll(date(2026, 10, 28), uten=("EQNR", "MOWI"))
        kvote = Kvote(brukt=16)
        kode, ut = _kjoer(tmp_path, kvote, klokke=datetime(2026, 10, 28, 22, 45, tzinfo=timezone.utc))
        assert kode == 0, ut
        assert kvote.kall == ["NYA.OL", "NYB.OL", "NYC.OL", "NYD.OL"]
        assert (kvote.brukt, kvote.bonus) == (20, 463)
        assert "2 av de 15 i lista mangler kursen for 2026-10-28 (EQNR, MOWI)" in ut
        assert "målingen venter" not in ut
        assert [rad[0] for rad in _radene()] == ["NYA", "NYB", "NYC", "NYD"]

    def test_gaar_fra_23_45_ogsaa_naar_alle_15_mangler(self, tmp_path):
        """Svaret 29.10 kl. 09:20, a): fra 23:45 er det ingen grense paa hvor
        mange som mangler. Basen har bare kursene for 27.10, saa alle 15
        mangler 28.10. Ville feilet hvis maalingen ventet fra 23:45 naar alle
        mangler, eller gikk foer 23:45."""
        _fyll(date(2026, 10, 27))
        kvote = Kvote(brukt=16)
        kode, ut = _kjoer(tmp_path, kvote, klokke=datetime(2026, 10, 28, 22, 44, 59, tzinfo=timezone.utc))
        assert (kode, kvote.kall) == (1, []), ut
        assert "0 kall brukt" in ut
        kode, ut = _kjoer(tmp_path, kvote, klokke=datetime(2026, 10, 28, 22, 45, tzinfo=timezone.utc))
        assert kode == 0, ut
        assert kvote.kall == ["NYA.OL", "NYB.OL", "NYC.OL", "NYD.OL"]
        assert (kvote.brukt, kvote.bonus) == (20, 463)
        assert "15 av de 15 i lista mangler kursen for 2026-10-28" in ut
        assert "målingen venter" not in ut
        assert [rad[0] for rad in _radene()] == ["NYA", "NYB", "NYC", "NYD"]

    def test_23_45_gjelder_ogsaa_i_sommertid(self, tmp_path):
        """Grensen er klokka i Oslo, ikke i GMT: 23:45 i september er 21:45 GMT."""
        _fyll(date(2026, 9, 30), uten=("EQNR",))
        kvote = Kvote(brukt=19, dato=date(2026, 9, 30))
        foer = datetime(2026, 9, 30, 21, 44, tzinfo=timezone.utc)
        assert _kjoer(tmp_path, kvote, klokke=foer)[0] == 1 and kvote.kall == []
        kode, ut = _kjoer(tmp_path, kvote, klokke=foer + timedelta(minutes=1))
        assert (kode, kvote.kall) == (0, ["NYA.OL"]), ut

    def test_uten_base_venter_ogsaa_etter_23_45(self, tmp_path):
        """En base som ikke finnes, er ingen henting: ingen kall, og ingen base
        lages."""
        kvote = Kvote(brukt=0)
        kode, ut = _kjoer(tmp_path, kvote, klokke=datetime(2026, 10, 28, 22, 50, tzinfo=timezone.utc))
        assert (kode, kvote.kall) == (1, []), ut
        assert not lagring_sqlite.BASE_STI.exists()
        assert "Basen finnes ikke" in ut and "Målingen venter. 0 kall brukt." in ut


class TestRekkefoelgen:
    def test_ingen_maales_to_ganger_foer_alle_er_maalt(self, tmp_path):
        """Ville feilet hvis en aksje ble maalt to ganger foer alle var maalt:
        tre kjoeringer med 4 kall hver over seks nye og tre rangerte."""
        _fyll(date(2026, 10, 28))
        koder = ["NYA", "HAVI", "NYB", "AKER", "NYC", "EQNR", "NYD", "HERMA", "NYE", "NYF"]
        alle = []
        for minutt in range(3):
            kvote = Kvote(brukt=16)
            kode, ut = _kjoer(tmp_path, kvote, klokke=ONSDAG + timedelta(minutes=minutt), koder=koder)
            assert kode == 0, ut
            alle += [ticker.removesuffix(".OL") for ticker in kvote.kall]
        # De seks nye i rekkefoelgen i lista, saa de rangerte, eldste foerst:
        # AKER (§15, 02.10), HAVI og HERMA (§52, 28.10), saa de nye igjen.
        assert alle[:9] == ["NYA", "NYB", "NYC", "NYD", "NYE", "NYF", "AKER", "HAVI", "HERMA"]
        assert len(set(alle[:9])) == 9
        assert "EQNR" not in alle
        # Tredje kjoering: HERMA var den siste av de 9, og saa de eldste
        # maalingene fra basen, NYA, NYB og NYC fra foerste kjoering.
        assert alle[8:] == ["HERMA", "NYA", "NYB", "NYC"]

    def test_de_eldste_kommer_foerst_naar_alle_er_maalt(self):
        """Ville feilet hvis de eldste ikke kom foerst naar alle var maalt:
        datoen er siste rad i basen, ellers datoen til paragrafen, og ved lik
        dato plassen i lista."""
        i_basen = {
            "NYA": datetime(2026, 10, 1, tzinfo=timezone.utc),
            "NYB": datetime(2026, 11, 2, 21, tzinfo=timezone.utc),
            "HAVI": datetime(2026, 9, 30, tzinfo=timezone.utc),
            "AKER": datetime(2026, 11, 3, tzinfo=timezone.utc),
        }
        lista = ["NYB", "HERMA", "AKER", "HDLY", "NYA", "HAVI", "GOLDR", "AASB"]
        assert rekkefoelge(lista, i_basen) == ["NYA", "AASB", "GOLDR", "HERMA", "HDLY", "HAVI", "NYB", "AKER"]

    def test_de_som_aldri_er_maalt_kommer_foer_alle_andre(self):
        lista = ["AKER", "NYB", "HAVI", "NYA"]
        i_basen = {"AKER": datetime(2020, 1, 1, tzinfo=timezone.utc)}
        assert rekkefoelge(lista, i_basen) == ["NYB", "NYA", "AKER", "HAVI"]

    def test_aksjene_i_appens_liste_maales_aldri(self):
        lista = [aksje.symbol for aksje in AKSJEUNIVERS] + ["NYA"]
        assert rekkefoelge(lista, {}) == ["NYA"]


class TestLagringen:
    def test_migrasjonen_endrer_ingen_tabell_som_finnes(self, tmp_path):
        """Ville feilet hvis migrasjonen endret en tabell som finnes: skjemaet
        og radene fra versjon 7 er like etter 0008, og bare omsetning er ny."""
        sti = tmp_path / "base.db"
        tilkobling = sqlite3.connect(sti)
        try:
            assert migrer(tilkobling, katalog_til(tmp_path, 7)) == 7
            tilkobling.execute("INSERT INTO min_liste (symbol) VALUES ('EQNR')")
            tilkobling.commit()
            foer = _skjema_og_rader(tilkobling)
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 8 == siste_versjon(MIGRASJONSKATALOG)
            etter = _skjema_og_rader(tilkobling)
        finally:
            tilkobling.close()
        nye = {navn for navn in etter if navn not in foer}
        assert nye == {"omsetning", "sqlite_autoindex_omsetning_1"}
        for navn, innhold in foer.items():
            if navn != "skjema_versjon":
                assert etter[navn] == innhold, navn

    def test_raadata_tallet_og_datoen(self, tmp_path):
        """Raadataene i data/raa/ (AD-6) og en rad per maaling med vinduet,
        tallet uavrundet og datoen. Ingen kurser eller volumer i utskriften."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=18)
        ekte_hent = kvote.hent

        def hent(ticker, *resten):
            svar = ekte_hent(ticker, *resten)
            if ticker == "NYB.OL":
                raise RuntimeError("HTTP 404 Not Found med HEMMELIG")
            return svar

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote)
        assert kode == 0, ut
        fil = lagring_fil.RAA_KATALOG / "omsetning1-raa-2026-10-28.json"
        bilde = json.loads(fil.read_text(encoding="utf-8"))
        assert bilde["fra"] == "2026-07-28" and bilde["til"] == "2026-10-28"
        assert bilde["hentet"] == ONSDAG.isoformat()
        assert list(bilde["serier"]) == ["NYA"] and bilde["serier"]["NYA"][0]["close"] == KURS
        assert bilde["feil"] == {"NYB": "HTTP 404 Not Found med ***"}
        nya, nyb = _radene()
        assert nya == ("NYA", ONSDAG.isoformat(), "2026-07-28", "2026-10-28", 10, 4, 0, VOLUM * KURS, None)
        assert nyb[0] == "NYB" and nyb[7] is None and nyb[8] == "HTTP 404 Not Found med ***"
        for tall in (str(KURS), "123,45", str(VOLUM), "98 765", f"{VOLUM * KURS:.0f}", "HEMMELIG"):
            assert tall not in ut
        # En kjoering til samme dag skriver en ny fil, aldri over den gamle.
        _kjoer(tmp_path, Kvote(brukt=19), klokke=ONSDAG + timedelta(minutes=1))
        assert (lagring_fil.RAA_KATALOG / "omsetning2-raa-2026-10-28.json").is_file()
        assert json.loads(fil.read_text(encoding="utf-8")) == bilde

    def test_kursfila_vinner_over_raadataene(self, tmp_path):
        """AD-6: datoen i navnet er boersdagen, saa nyeste_snapshot velger
        kursfila ogsaa en loerdag."""
        katalog = tmp_path / "raa"
        katalog.mkdir()
        (katalog / "kurser-raa-2026-10-30.json").write_text("{}", encoding="utf-8")
        (katalog / omsetning.raafil(katalog, date(2026, 10, 30)).name).write_text("{}", encoding="utf-8")
        assert lagring_fil.nyeste_snapshot(katalog).name == "kurser-raa-2026-10-30.json"


class TestMedianen:
    def test_volum_null_er_med_og_rader_uten_tall_telles(self):
        rader = [
            {"date": "2026-10-01", "close": 10.0, "volume": 0},
            {"date": "2026-10-02", "close": 10.0, "volume": 3},
            {"date": "2026-10-05", "close": 10.0, "volume": 5},
            {"date": "2026-10-06", "close": None, "volume": 5},
            {"date": "2026-06-01", "close": 10.0, "volume": 900},
        ]
        maaling = regn_ut("X", rader, date(2026, 7, 6), date(2026, 10, 6))
        assert (maaling.handelsdager, maaling.dager_uten_volum, maaling.rader_uten_tall) == (3, 1, 1)
        assert maaling.median == 30.0 and maaling.feil is None

    def test_ingen_rader_gir_feil_og_ingen_median(self):
        assert regn_ut("X", [], date(2026, 7, 6), date(2026, 10, 6)).feil
        assert regn_ut("X", {"feil": 1}, date(2026, 7, 6), date(2026, 10, 6)).median is None

    @pytest.mark.parametrize(
        "boersdag, fra",
        [
            (date(2026, 10, 22), date(2026, 7, 22)),
            (date(2026, 5, 29), date(2026, 2, 28)),
            (date(2026, 1, 15), date(2025, 10, 15)),
            (date(2026, 3, 31), date(2025, 12, 31)),
        ],
    )
    def test_vinduet_er_tre_maaneder_til_og_med_boersdagen(self, boersdag, fra):
        assert vindu(boersdag) == (fra, boersdag)


class TestValget:
    def test_valget_i_hentekommandoen_med_de_ekte_stiene(self, tmp_path, monkeypatch):
        """main med --maal-omsetning bruker nettfunksjonene i fetch_prices.py,
        stiene fra lagring_fil og lagring_sqlite, og gir koden derfra."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=19)
        monkeypatch.setattr(fetch_prices, "hent_ett_symbol", kvote.hent)
        monkeypatch.setattr(fetch_prices, "hent_kvote", kvote.les)
        monkeypatch.setattr(fetch_prices, "hent_api_nokkel", lambda: "HEMMELIG")
        monkeypatch.setattr(fetch_prices, "naa", lambda: ONSDAG)
        monkeypatch.setattr(omsetning, "LISTEFIL", _lista(tmp_path, NYE))
        with pytest.raises(SystemExit) as utgang:
            fetch_prices.main(["--maal-omsetning"])
        assert utgang.value.code == 0
        assert kvote.kall == ["NYA.OL"]
        assert (lagring_fil.RAA_KATALOG / "omsetning1-raa-2026-10-28.json").is_file()

    @pytest.mark.parametrize("ekstra", [["--les-inn", "x.json"], ["--uten-tidskontroll"]])
    def test_valget_kombineres_ikke(self, ekstra):
        with pytest.raises(SystemExit) as utgang:
            fetch_prices.main(["--maal-omsetning", *ekstra])
        assert utgang.value.code == 2

    def test_valget_forkortes_ikke(self):
        with pytest.raises(SystemExit) as utgang:
            fetch_prices.main(["--maal"])
        assert utgang.value.code == 2

    def test_maalingen_kan_ikke_startes_fra_nettsiden(self):
        """Ville feilet hvis maalingen kunne startes fra nettsiden: app.py
        importerer verken omsetning eller hentekommandoen (AD-10)."""
        tre = ast.parse((ROT / "src" / "app.py").read_text(encoding="utf-8"))
        importert = set()
        for node in ast.walk(tre):
            if isinstance(node, ast.Import):
                importert |= {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                importert.add(node.module)
        assert importert & {"omsetning", "fetch_prices"} == set()

    def test_demobasen_nektes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(lagring_sqlite, "er_demobase", lambda sti: True)
        kvote = Kvote(brukt=0)
        with pytest.raises(SystemExit) as utgang:
            _kjoer(tmp_path, kvote)
        assert (utgang.value.code, kvote.kall) == (1, [])


def _skjema_og_rader(tilkobling: sqlite3.Connection) -> dict[str, object]:
    ut = {}
    for type_, navn, sql in tilkobling.execute("SELECT type, name, sql FROM sqlite_master ORDER BY name"):
        rader = tilkobling.execute(f'SELECT * FROM "{navn}" ORDER BY rowid').fetchall() if type_ == "table" else None
        ut[navn] = (type_, sql, rader)
    return ut


def test_de_214_er_de_samme_som_i_malinger():
    """MAALT_I_MALINGER er «Maalt i» i «Alle 206, rangert» i §50 og tabellene i
    §51 og §52, med datoen i overskriften til paragrafen."""
    tekst = MALINGER.read_text(encoding="utf-8")
    datoer = {
        int(m.group(1)): date.fromisoformat(m.group(2))
        for m in re.finditer(r"^## (\d+)\. .*\((\d{4}-\d{2}-\d{2})\)\s*$", tekst, re.M)
    }
    rangert = tekst[tekst.index("### Alle 206, rangert") : tekst.index("\n## 51.")]
    fra_tekst = {
        m.group(1): int(m.group(2))
        for m in re.finditer(r"^\| \d+ \| ([A-Z0-9]+) \| [^|]+\| [^|]+\| [^|]+\| [^|]+\| §(\d+) \|", rangert, re.M)
    }
    for paragraf, slutt in ((51, "\n## 52."), (52, None)):
        del_ = tekst[tekst.index(f"\n## {paragraf}.") : tekst.index(slutt) if slutt else None]
        fra_tekst |= {m.group(1): paragraf for m in re.finditer(r"^\| ([A-Z0-9]+) \| [^|]+\| \d+ \|", del_, re.M)}
    assert len(fra_tekst) == 214
    assert {s: (p, datoer[p]) for s, p in fra_tekst.items()} == {
        s: (p, dato) for p, (dato, symboler) in MAALT_I_MALINGER.items() for s in symboler
    }
    assert len(maalt_i_malingene()) == 214
    assert {aksje.symbol for aksje in AKSJEUNIVERS} <= set(maalt_i_malingene())


def test_basen_staar_paa_versjon_8(tmp_path):
    sti = tmp_path / "ny.db"
    aapne_base(sti).close()
    tilkobling = sqlite3.connect(sti)
    try:
        assert versjon(tilkobling) == 8
    finally:
        tilkobling.close()


class TestGjennomgangen:
    """Funnene fra gjennomgangen 28.10 (BH, ECH, VG i spesifikasjonen)."""

    def test_ingen_kall_naar_kvoten_naar_20_underveis(self, tmp_path):
        """Ville feilet hvis et kall gikk fra bonuskvoten fordi noe annet
        brukte kallene mens maalingen gikk (VG1): kontrollen foer hvert kall."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        ekte_hent = kvote.hent

        def hent(*argumenter):
            svar = ekte_hent(*argumenter)
            kvote.brukt = 20
            return svar

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote)
        assert kode == 1
        assert kvote.kall == ["NYA.OL"] and kvote.bonus == 463
        assert "går fra bonuskvoten" in ut

    def test_utskriften_sier_kallene_foer_foerste_kall_og_kvoten_etter(self, tmp_path):
        """VG4, VG5, BH7: hvor mange kall, foer det foerste, og kvoten etter."""
        _fyll(date(2026, 10, 28))
        kode, ut = _kjoer(tmp_path, Kvote(brukt=16))
        assert kode == 0
        start = "Måler omsetningen for 4 aksjer med 4 av de 4 kallene som er igjen av dagens"
        assert start in ut and ut.index(start) < ut.index("NYA:")
        assert "Ingen kall blir igjen i dag." in ut
        assert "Kvoten etter: 20 av 20 brukt 2026-10-28 i GMT, extraLimit 463." in ut
        _, ut = _kjoer(tmp_path, Kvote(brukt=0), klokke=ONSDAG + timedelta(minutes=1), koder=["NYX", "NYY"])
        assert "med 2 av de 20 kallene" in ut and "18 kall blir igjen i dag." in ut

    def test_ingen_tall_fra_kildene_eller_medianen_i_utskriften(self, tmp_path):
        """VG3: ingen tall i utskriften utenom datoer, tellinger under 100 og
        extraLimit."""
        _fyll(date(2026, 10, 28))
        _, ut = _kjoer(tmp_path, Kvote(brukt=16))
        uten_datoer = re.sub(r"\d{4}-\d{2}-\d{2}", "", ut)
        assert [int(t) for t in re.findall(r"\d+", uten_datoer) if int(t) >= 100] == [463]

    def test_stopper_naar_kvoten_staar_paa_gaarsdagen_etter_et_kall(self, tmp_path):
        """Ville feilet hvis et kall ble gjort med en annen dato i GMT (VG7):
        en loerdag staar apiRequestsDate fortsatt paa fredag etter kallet."""
        _fyll(date(2026, 10, 30))
        kvote = Kvote(brukt=16, dato=date(2026, 10, 30))
        kode, ut = _kjoer(tmp_path, kvote, klokke=LOERDAG, koder=["N01", "N02"])
        assert (kode, kvote.kall) == (1, ["N01.OL"]), ut
        assert "etter kallet" in ut

    def test_ingen_rader_naar_raadataene_ikke_kan_skrives(self, tmp_path, monkeypatch):
        """VG8, AD-6: raadataene foerst. Kan fila ikke skrives, skrives ingen rader."""
        _fyll(date(2026, 10, 28))
        (tmp_path / "en-fil").write_text("", encoding="utf-8")
        monkeypatch.setattr(lagring_fil, "RAA_KATALOG", tmp_path / "en-fil")
        kode, ut = _kjoer(tmp_path, Kvote(brukt=18))
        assert kode == 1 and "Ingen rader i basen" in ut and "API-kall brukt: 2." in ut
        assert _radene() == []

    def test_det_som_er_maalt_lagres_naar_kvoten_ikke_kan_leses(self, tmp_path):
        """VG9: kvoten kan ikke leses etter foerste kall."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        lest = []

        def les(nokkel):
            lest.append(1)
            return {} if len(lest) == 3 else Kvote.les(kvote, nokkel)

        kvote.les = les
        kode, ut = _kjoer(tmp_path, kvote)
        assert (kode, kvote.kall) == (1, ["NYA.OL"]), ut
        assert [rad[0] for rad in _radene()] == ["NYA"]

    def test_det_som_er_maalt_lagres_naar_kjoeringen_avbrytes(self, tmp_path):
        """ECH3: en feil som ikke er en stopp, etter foerste kall."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=16)
        ekte_hent = kvote.hent

        def hent(ticker, *resten):
            if ticker == "NYB.OL":
                raise KeyboardInterrupt
            return ekte_hent(ticker, *resten)

        kvote.hent = hent
        with pytest.raises(KeyboardInterrupt):
            _kjoer(tmp_path, kvote)
        assert [rad[0] for rad in _radene()] == ["NYA"]
        assert (lagring_fil.RAA_KATALOG / "omsetning1-raa-2026-10-28.json").is_file()

    def test_en_feil_som_gaar_over_gir_ingen_rad(self, tmp_path):
        """BH3, ECH1: et tidsavbrudd gir ingen rad, saa aksjen maales foerst
        neste gang. En ticker som ikke finnes (404), lagres som maalt."""
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=18)
        ekte_hent = kvote.hent

        def hent(ticker, *resten):
            ekte_hent(ticker, *resten)
            raise RuntimeError("Timeout" if ticker == "NYA.OL" else "HTTP 404 Not Found")

        kvote.hent = hent
        kode, ut = _kjoer(tmp_path, kvote)
        assert kode == 0, ut
        assert [(rad[0], rad[8]) for rad in _radene()] == [("NYB", "HTTP 404 Not Found")]
        fil = lagring_fil.RAA_KATALOG / "omsetning1-raa-2026-10-28.json"
        assert json.loads(fil.read_text(encoding="utf-8"))["feil"] == {"NYA": "Timeout", "NYB": "HTTP 404 Not Found"}
        kvote = Kvote(brukt=19)
        _kjoer(tmp_path, kvote, klokke=ONSDAG + timedelta(minutes=1))
        assert kvote.kall == ["NYA.OL"]

    def test_et_navn_som_dukker_opp_skrives_ikke_over(self, tmp_path, monkeypatch):
        """ECH8: fila med navnet raafil ga, finnes naar den aapnes."""
        _fyll(date(2026, 10, 28))
        ekte = omsetning.raafil
        katalog = lagring_fil.RAA_KATALOG
        katalog.mkdir(parents=True, exist_ok=True)

        def raafil(k, dag):
            sti = ekte(k, dag)
            if sti.name == "omsetning1-raa-2026-10-28.json":
                sti.write_text("en annen", encoding="utf-8")
            return sti

        monkeypatch.setattr(omsetning, "raafil", raafil)
        kode, _ = _kjoer(tmp_path, Kvote(brukt=19))
        assert kode == 0
        assert (katalog / "omsetning1-raa-2026-10-28.json").read_text(encoding="utf-8") == "en annen"
        assert (katalog / "omsetning2-raa-2026-10-28.json").is_file()

    def test_medianen_av_et_partall_rader_og_en_kode_to_ganger_i_lista(self, tmp_path):
        """VG12: medianen av 10, 20, 30 og 40 er 25, og en kode som staar to
        ganger i lista, maales en gang."""
        rader = [{"date": f"2026-10-0{i}", "close": 1.0, "volume": v} for i, v in enumerate((10, 20, 30, 40), 1)]
        assert regn_ut("X", rader, date(2026, 7, 1), date(2026, 10, 6)).median == 25.0
        _fyll(date(2026, 10, 28))
        kvote = Kvote(brukt=17)
        _kjoer(tmp_path, kvote, koder=["NYA", "NYA", "NYB"])
        assert kvote.kall == ["NYA.OL", "NYB.OL"]

    def test_kurs_null_er_ikke_en_dag_uten_volum_og_store_tall_stopper_ikke(self):
        """BH9, ECH3: kurs 0 med volum er ikke en dag uten volum, og et
        heltall for stort for float er en rad uten tall."""
        rader = [
            {"date": "2026-10-01", "close": 0.0, "volume": 5},
            {"date": "2026-10-02", "close": 1.0, "volume": 10**400},
        ]
        maaling = regn_ut("X", rader, date(2026, 7, 1), date(2026, 10, 6))
        assert (maaling.handelsdager, maaling.dager_uten_volum, maaling.rader_uten_tall) == (1, 0, 1)

    def test_valget_virker_naar_fetch_prices_kjoeres_som_skript(self, monkeypatch):
        """BH4: jobben kjoerer src/fetch_prices.py som __main__, og omsetning
        importerer fetch_prices en gang til. Uten base stopper den med 0 kall
        foer noekkelen og kvoten leses."""
        import runpy
        import sys

        monkeypatch.setattr(sys, "argv", ["fetch_prices.py", "--maal-omsetning"])
        monkeypatch.delitem(sys.modules, "omsetning")
        monkeypatch.delitem(sys.modules, "fetch_prices")
        with pytest.raises(SystemExit) as utgang:
            runpy.run_path(str(ROT / "src" / "fetch_prices.py"), run_name="__main__")
        assert utgang.value.code == 1
        assert not lagring_sqlite.BASE_STI.exists()
