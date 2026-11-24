"""Story 2.21: en aksje som tas ut og inn igjen, får dagen den kom inn igjen.

Spesifikasjonen er spec-2-21-ut-og-inn-igjen.md, og svaret er gruppens 24.11
kl. 12:57 på spørsmål 2 i 9.28 (ECH5). Tilstandene lages med hentingen selv,
som i 9.28: EODHD gir ingen kurser for en egen aksje, hentingen kvelden etter
tar den ut, brukeren følger den igjen, og en sen kjøring uten kall tar ønsket
i bruk. Hver test lager sin egen base under tmp_path (regel 22), og ingen
test gjør nettkall (AD-8).
"""

import sqlite3
from datetime import date, timedelta

import pytest

import ferdige_lister
import valg
from lagring_sqlite import aapne_base, les_lista
from test_fetch_prices import OEYEBLIKK_22_09, TIRSDAG_22_09, kjoer_23, kjoer_23_kode, kvote, serie_til
from test_tatt_inn_9_28 import HENTET, _egne, _foelg, _klient, kl
from test_valg import FASTE, med_boersen
from valg import Valglager

ONSDAG_23_09 = date(2026, 9, 23)
TORSDAG_24_09 = date(2026, 9, 24)
ONSDAG = OEYEBLIKK_22_09 + timedelta(days=1)
TORSDAG = OEYEBLIKK_22_09 + timedelta(days=2)
FREDAG = OEYEBLIKK_22_09 + timedelta(days=3)
SENT = timedelta(minutes=45)


@pytest.fixture(autouse=True)
def faste_bransjer(monkeypatch):
    for kode, bransje in FASTE.items():
        monkeypatch.setitem(ferdige_lister.BRANSJE, kode, bransje)


def _uten_nya(dag: date):
    """EODHD gir ingen kurser for NYA, og kurser til og med dag for resten."""

    def hent(ticker, *a):
        return [] if ticker == "NYA.OL" else serie_til(dag)

    return hent


def _fjern(base, kode: str = "NYA") -> None:
    lager = Valglager(aapne_base(base), lambda: OEYEBLIKK_22_09)
    try:
        lager.fjern(kode)
    finally:
        lager._t.close()


def _rad(base, kode: str = "NYA") -> tuple:
    """(inn, ut, rader i kurs, rader i vurdering) for aksjen."""
    tilkobling = aapne_base(base)
    try:
        return tilkobling.execute(
            "SELECT inn, ut, (SELECT count(*) FROM kurs WHERE symbol = a.symbol), "
            "(SELECT count(*) FROM vurdering WHERE symbol = a.symbol) FROM aksje a WHERE symbol = ?",
            (kode,),
        ).fetchone()
    finally:
        tilkobling.close()


def _ikke_forsoekt(base) -> dict:
    tilkobling = aapne_base(base)
    try:
        return valg.ikke_forsoekt(tilkobling)
    finally:
        tilkobling.close()


@pytest.fixture
def tatt_ut(tmp_path):
    """NYA kom inn tirsdag 22.09 med kveldens henting, EODHD ga ingen kurser,
    og hentingen onsdag 23.09 tok den ut igjen."""
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
    med_boersen(base)
    _foelg(base)
    kode, kall, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, _uten_nya(TIRSDAG_22_09))
    assert kode == 1 and "NYA.OL" in kall
    _, kall, ut = kjoer_23(raa, base, ONSDAG)
    assert "NYA.OL" not in kall and "NYA ga ingen kurser" in ut
    assert _rad(base) == ("2026-09-22", "2026-09-23", 0, 1)
    return raa, base


@pytest.fixture
def inn_igjen(tatt_ut):
    """Brukeren følger NYA igjen onsdag kveld, etter kveldens henting, og
    kjøringen kl. 22:45 tar ønsket i bruk uten kall igjen."""
    raa, base = tatt_ut
    _foelg(base)
    kode, kall, ut = kjoer_23_kode(raa, base, ONSDAG + SENT, les_kvote=kvote(brukt=20, dato="2026-09-23"))
    assert kode == 1 and kall == [], ut
    assert "NYA er tatt inn i lista fra 2026-09-23." in ut
    return raa, base


class TestDagenDenKomInnIgjen:
    def test_aksjen_faar_dagen_den_kom_inn_igjen(self, inn_igjen):
        """Ville feilet hvis aksjen beholdt dagen den først kom inn. Ingen rad
        er slettet (AD-7): raden i vurdering fra tirsdag står."""
        _, base = inn_igjen
        assert _rad(base) == ("2026-09-23", None, 0, 1)

    def test_statusen_fra_9_28_regner_fra_den_nye_dagen(self, inn_igjen, monkeypatch):
        """Ville feilet hvis den gamle raden i vurdering gjorde at aksjen ble
        lest som forsøkt hentet, og sto som «Hentet» uten kurser."""
        _, base = inn_igjen
        assert _ikke_forsoekt(base) == {"NYA": ONSDAG_23_09}
        egne = _egne(_klient(monkeypatch, base, kl(9, 23, 23)).get("/").data.decode("utf-8"))
        assert "Tatt inn. Kursene kommer ved hentingen i morgen etter kl. 22." in egne
        assert HENTET not in egne
        egne = _egne(_klient(monkeypatch, base, kl(9, 24, 12)).get("/").data.decode("utf-8"))
        assert "Tatt inn. Kursene kommer ved hentingen i kveld etter kl. 22." in egne

    def test_den_tas_ikke_ut_foer_kursene_er_hentet(self, inn_igjen):
        """Ville feilet hvis hentingen torsdag tok aksjen ut på grunn av
        raden fra tirsdag, før den hadde spurt EODHD på nytt."""
        raa, base = inn_igjen
        _, kall, ut = kjoer_23(raa, base, TORSDAG)
        assert "NYA.OL" in kall and "NYA ga ingen kurser" not in ut
        inn, ut_dag, kurser, _ = _rad(base)
        assert (inn, ut_dag) == ("2026-09-23", None) and kurser > 0
        assert _ikke_forsoekt(base) == {}

    def test_gir_eodhd_ingen_kurser_igjen_tas_den_ut_kvelden_etter(self, inn_igjen):
        """Som før (spørsmål 6 i 2.12): ville feilet hvis en aksje som er
        forsøkt på nytt uten å få kurser, ble stående i lista, eller ble tatt
        ut samme kveld som forsøket."""
        raa, base = inn_igjen
        kode, kall, ut = kjoer_23_kode(raa, base, TORSDAG, _uten_nya(TORSDAG_24_09))
        assert kode == 1 and "NYA.OL" in kall and "NYA ga ingen kurser" not in ut
        assert _rad(base) == ("2026-09-23", None, 0, 2)
        assert _ikke_forsoekt(base) == {}
        _, kall, ut = kjoer_23(raa, base, FREDAG)
        assert "NYA.OL" not in kall and "NYA ga ingen kurser" in ut
        assert _rad(base) == ("2026-09-23", "2026-09-25", 0, 2)

    def test_inn_igjen_foer_kveldens_henting(self, tatt_ut):
        """Ville feilet hvis en aksje som tas inn igjen av kveldens vanlige
        henting, ikke ble forsøkt, eller ble tatt ut dagen etter uten forsøk."""
        raa, base = tatt_ut
        _foelg(base)
        _, kall, ut = kjoer_23(raa, base, TORSDAG)
        assert "NYA er tatt inn i lista fra 2026-09-24." in ut and "NYA.OL" in kall
        inn, ut_dag, kurser, _ = _rad(base)
        assert (inn, ut_dag) == ("2026-09-24", None) and kurser > 0


class TestFjernetOgFulgtIgjen:
    def test_fjernet_uten_kurser_og_fulgt_igjen_samme_kveld(self, tmp_path):
        """Ville feilet hvis den nye dagen brøt regelen i basen om at inn er
        før ut (0009), når aksjen fjernes og følges igjen flere ganger."""
        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        uten_kall = kvote(brukt=20)
        kjoer_23_kode(raa, base, OEYEBLIKK_22_09 + SENT, les_kvote=uten_kall)
        assert _rad(base) == ("2026-09-22", None, 0, 0)
        # Onsdag: fjernet før kveldens henting, og fulgt igjen etter den.
        _fjern(base)
        kjoer_23(raa, base, ONSDAG)
        assert _rad(base) == ("2026-09-22", "2026-09-23", 0, 0)
        _foelg(base)
        uten_kall = kvote(brukt=20, dato="2026-09-23")
        kjoer_23_kode(raa, base, ONSDAG + SENT, les_kvote=uten_kall)
        assert _rad(base) == ("2026-09-23", None, 0, 0)
        assert _ikke_forsoekt(base) == {"NYA": ONSDAG_23_09}
        # Fjernet igjen samme kveld: ut blir dagen etter, fordi den kom inn i dag.
        _fjern(base)
        kjoer_23_kode(raa, base, ONSDAG + timedelta(minutes=75), les_kvote=uten_kall)
        assert _rad(base) == ("2026-09-23", "2026-09-24", 0, 0)
        # Og fulgt igjen: inn står på dagen, og ut er borte.
        _foelg(base)
        kjoer_23_kode(raa, base, ONSDAG + timedelta(minutes=105), les_kvote=uten_kall)
        assert _rad(base) == ("2026-09-23", None, 0, 0)

    def test_en_aksje_med_kurser_beholder_dagen(self, tmp_path):
        """Ville feilet hvis en aksje med kurser fikk ny dag: lista for dagene
        den har kurser og vurderinger for, leses av inn og ut, og skal være
        som før."""
        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
        med_boersen(base)
        _foelg(base)
        _, kall, _ = kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert "NYA.OL" in kall
        _fjern(base)
        kjoer_23(raa, base, ONSDAG)
        inn, ut_dag, kurser, _ = _rad(base)
        assert (inn, ut_dag) == ("2026-09-22", "2026-09-23") and kurser > 0
        _foelg(base)
        _, kall, ut = kjoer_23(raa, base, TORSDAG)
        assert "NYA er tatt inn i lista fra 2026-09-24." in ut and "NYA.OL" in kall
        assert _rad(base)[:2] == ("2026-09-22", None)
        tilkobling = aapne_base(base)
        try:
            assert "NYA" in {a.symbol for a in les_lista(tilkobling, TIRSDAG_22_09)}
            assert "NYA" in {a.symbol for a in les_lista(tilkobling, TORSDAG_24_09)}
        finally:
            tilkobling.close()

    def test_regelen_i_basen_staar(self, inn_igjen):
        """Vakten rettingen lener seg på: basen nekter en inn som ikke er før
        ut, så en feil dag ville stoppet hentingen i stedet for å lagres."""
        _, base = inn_igjen
        tilkobling = aapne_base(base)
        try:
            with pytest.raises(sqlite3.IntegrityError), tilkobling:
                tilkobling.execute("UPDATE aksje SET ut = inn WHERE symbol = 'NYA'")
        finally:
            tilkobling.close()
