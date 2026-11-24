"""Story 2.22: en egen kode når det eneste som mangler, er aksjer tatt inn
etter kveldens henting.

Spesifikasjonen er spec-2-22-egen-kode-for-tatt-inn.md, og svaret er gruppens
24.11 kl. 14:29 på spørsmål 3 i 9.28. Tilstandene lages med hentingen selv,
som i 9.28: kveldens henting går, brukeren følger en aksje etterpå, og en
senere kjøring tar ønsket i bruk uten kall igjen. Alle øyeblikk er faste, og
hentingen får dem som argument, så ingen test følger den ekte klokka. Hver
test lager sin egen base under tmp_path (regel 22), og ingen test gjør
nettkall (AD-8).
"""

from datetime import date, timedelta
from pathlib import Path

import pytest

import ferdige_lister
import fetch_prices as fp
import valg
from boersdag import norsk_dato
from lagring_sqlite import aapne_base
from test_fetch_prices import (
    OEYEBLIKK_22_09,
    TIRSDAG_22_09,
    kjoer_23,
    kjoer_23_kode,
    kvote,
    kvoter,
    serie_til,
    svar,
)
from test_tatt_inn_9_28 import OSLO, _foelg
from test_valg import FASTE, med_boersen

ROT = Path(__file__).resolve().parents[1]
# Senere kjøringer samme kveld, etter kveldens henting kl. 22:00 norsk tid.
KL_22_45 = OEYEBLIKK_22_09 + timedelta(minutes=45)
KL_23_15 = OEYEBLIKK_22_09 + timedelta(minutes=75)
KL_23_45 = OEYEBLIKK_22_09 + timedelta(minutes=105)
UTEN_KALL = kvote(brukt=20)
I_ORDEN = "Det er i orden"


@pytest.fixture(autouse=True)
def faste_bransjer(monkeypatch):
    for kode, bransje in FASTE.items():
        monkeypatch.setitem(ferdige_lister.BRANSJE, kode, bransje)


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


def _hent(uten=(), feiler=(), dag: date = TIRSDAG_22_09):
    """EODHD: ingen kurser for symbolene i uten, en feil for dem i feiler, og
    kurser til og med dag for resten."""

    def hent(ticker, *a):
        symbol = ticker.removesuffix(".OL")
        if symbol in feiler:
            raise RuntimeError("nei")
        return [] if symbol in uten else serie_til(dag)

    return hent


def _uansett(raa, base, oeyeblikk, hent=None, **kw):
    """En kjøring som kan avslutte eller gå ferdig: (kode, kall, utskrift)."""
    linjer, kall = [], []

    def tell(ticker, *a):
        kall.append(ticker)
        return (hent or (lambda *_: serie_til(norsk_dato(oeyeblikk))))(ticker, *a)

    kw.setdefault("les_kvote", kvote())
    try:
        fp.kjoer(raa, base, oeyeblikk, "noekkel", tell, linjer.append, **kw)
        kode = 0
    except SystemExit as slutt:
        kode = slutt.code
    return kode, kall, "\n".join(linjer)


def _kurser(base, symbol: str) -> int:
    tilkobling = aapne_base(base)
    try:
        return tilkobling.execute("SELECT count(*) FROM kurs WHERE symbol = ?", (symbol,)).fetchone()[0]
    finally:
        tilkobling.close()


def test_klokka_i_testene_er_fast():
    """Ville feilet hvis en sen kjøring ble lagt etter midnatt norsk tid,
    eller etter kl. 23:50, der et nytt forsøk ikke starter."""
    for oeyeblikk in (KL_22_45, KL_23_15, KL_23_45):
        lokal = oeyeblikk.astimezone(OSLO)
        assert norsk_dato(oeyeblikk) == TIRSDAG_22_09
        assert (22, 0) < (lokal.hour, lokal.minute) < (23, 50)
    kilde = Path(__file__).read_text(encoding="utf-8")
    for ekte in ("datetime." + "now(", "date." + "today(", "time." + "time("):
        assert ekte not in kilde


class TestKode4:
    def test_konstanten_er_4_og_ingen_av_de_andre(self):
        """Ville feilet hvis koden falt sammen med 0, 1, argparse sin 2 eller
        KODE_BARE_INDEKSEN."""
        assert fp.KODE_BARE_TATT_INN == 4
        assert fp.KODE_BARE_TATT_INN not in (0, 1, 2, fp.KODE_BARE_INDEKSEN)

    def test_bare_en_aksje_tatt_inn_etter_hentingen_gir_kode_4(self, stier):
        """Ville feilet hvis kjøringen som tar inn en aksje uten kall, endte
        med kode 1, som om noe som skulle vært hentet, manglet."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=UTEN_KALL)
        assert kode == 4 and kall == [], ut
        assert "NYA er tatt inn i lista fra 2026-09-22." in ut
        assert "Kode 4" in ut and I_ORDEN in ut and "NYA" in ut.split("Kode 4", 1)[1]
        assert _kurser(base, "NYA") == 0

    def test_hver_senere_kjoering_samme_kveld_gir_kode_4(self, stier):
        """Ville feilet hvis bare kjøringen som tok ønsket i bruk, ga 4, og
        kveldens siste kjøring, som Oppgaveplanleggeren viser, ga 1."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        for oeyeblikk in (KL_22_45, KL_23_15, KL_23_45):
            kode, kall, ut = kjoer_23_kode(raa, base, oeyeblikk, les_kvote=UTEN_KALL)
            assert kode == 4 and kall == [], ut

    def test_to_tatt_inn_og_kall_til_bare_den_ene_gir_kode_4(self, stier):
        """To aksjer er tatt inn, og det er ett kall igjen til nye forsøk.
        Den ene hentes, og den andre er ikke forsøkt. Ville feilet hvis den
        som ikke ble forsøkt, ga kode 1."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        _foelg(base, "NYB")
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=kvote(brukt=19))
        assert kode == 4 and len(kall) == 1, ut
        hentet = kall[0].removesuffix(".OL")
        venter = ({"NYA", "NYB"} - {hentet}).pop()
        assert _kurser(base, hentet) > 0 and _kurser(base, venter) == 0
        assert venter in ut.split("Kode 4", 1)[1]


class TestKode1Staar:
    def test_mangler_ogsaa_en_annen_aksje_er_koden_1(self, stier):
        """Ville feilet hvis en aksje fra kveldens henting som mangler dagens
        kurs, ble skjult bak kode 4."""
        raa, base = stier
        kode, _, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, _hent(feiler=("DNB",)))
        assert kode == 1
        med_boersen(base)
        _foelg(base)
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=UTEN_KALL)
        assert kode == 1 and kall == [] and "Kode 4" not in ut

    def test_feilet_indeksen_er_koden_som_foer(self, stier):
        """Ville feilet hvis en kveld der hovedindeksen feilet, endte med
        kode 4. Før rettingen ga det nye forsøket uten kall kode 1."""
        raa, base = stier
        kode, _, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, _hent(feiler=("OSEBX",)))
        assert kode == fp.KODE_BARE_INDEKSEN
        med_boersen(base)
        _foelg(base)
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=UTEN_KALL)
        assert kode == 1 and kall == [] and "Kode 4" not in ut

    def test_eodhd_ga_ingen_kurser_er_koden_1(self, stier):
        """NYA sto i lista da kveldens henting gikk, og EODHD ga ingen kurser.
        Ville feilet hvis en aksje som er forsøkt hentet, ga kode 4."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
        med_boersen(base)
        _foelg(base)
        kode, kall, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, _hent(uten=("NYA",)))
        assert kode == 1 and "NYA.OL" in kall
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=UTEN_KALL)
        assert kode == 1 and kall == [] and "Kode 4" not in ut

    def test_et_kall_som_ikke_ga_kursen_er_koden_1(self, stier):
        """Det var kall igjen, forsøket spurte EODHD om aksjen som er tatt
        inn, og fikk ingen kurser. Ville feilet hvis det ga kode 4: da er
        aksjen forsøkt, og noe som skulle vært hentet, mangler."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, _hent(uten=("NYA",)), les_kvote=kvote(brukt=16))
        assert kode == 1 and kall == ["NYA.OL"] and "Kode 4" not in ut
        # Gjennomgangen (ECH1, VG1): forsøket skrev ingen rad i vurdering, så
        # aksjen leses fortsatt som ikke forsøkt (9.28). Kjøringene etterpå
        # uten kall skal likevel gi 1: forsøksfila for dagen viser at EODHD
        # er spurt. Ville feilet hvis kvelden endte med kode 4.
        for oeyeblikk in (KL_23_15, KL_23_45):
            kode, kall, ut = kjoer_23_kode(raa, base, oeyeblikk, les_kvote=UTEN_KALL)
            assert kode == 1 and kall == [] and "Kode 4" not in ut

    def test_et_kall_som_feilet_er_koden_1_ogsaa_etterpaa(self, stier):
        """Som over, når kallet feilet i stedet for å gi et tomt svar."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        kode, kall, _ = kjoer_23_kode(raa, base, KL_22_45, _hent(feiler=("NYA",)), les_kvote=kvote(brukt=16))
        assert kode == 1 and kall == ["NYA.OL"]
        kode, kall, ut = kjoer_23_kode(raa, base, KL_23_15, les_kvote=UTEN_KALL)
        assert kode == 1 and kall == [] and "Kode 4" not in ut

    def test_indeksen_uten_dagen_er_koden_1(self, stier):
        """Gjennomgangen (ECH2, VG2): kallet for hovedindeksen gikk, men
        svaret manglet børsdagen. Ville feilet hvis kvelden endte med kode 4
        og «det eneste som mangler», når indeksen også mangler dagen."""
        raa, base = stier

        def hent(ticker, *a):
            return serie_til(TIRSDAG_22_09 - timedelta(days=1) if ticker == "OSEBX.OL" else TIRSDAG_22_09)

        _uansett(raa, base, OEYEBLIKK_22_09, hent)
        assert fp.indeksen_mangler(base, TIRSDAG_22_09)
        med_boersen(base)
        _foelg(base)
        kode, kall, ut = _uansett(raa, base, KL_22_45, hent, les_kvote=UTEN_KALL)
        assert kode == 1 and kall == [] and "Kode 4" not in ut, ut

    def test_et_forsoek_som_ble_avbrutt_er_koden_1(self, stier):
        """Gjennomgangen (ECH3): to aksjer er tatt inn, det er kall til
        begge, og forsøket stopper etter det første fordi bonuskvoten sank.
        Ville feilet hvis den som ikke ble spurt, ga kode 4 med «hadde ikke
        kall»: grunnen var en annen."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        _foelg(base, "NYB")
        les, _ = kvoter(svar(brukt=17, bonus=463), svar(brukt=18, bonus=462))
        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=les)
        assert len(kall) == 1 and "Bonuskvoten sank" in ut, ut
        assert kode == 1 and "Kode 4" not in ut

    def test_kvoten_kan_ikke_leses_er_koden_1(self, stier):
        """Ville feilet hvis en kjøring som ikke vet om den har kall, sa at
        alt er i orden."""
        import requests

        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)

        def les(_noekkel):
            raise requests.ConnectionError("nei")

        kode, kall, ut = kjoer_23_kode(raa, base, KL_22_45, les_kvote=les)
        assert kode == 1 and kall == [] and "Kode 4" not in ut

    def test_en_dag_boersen_er_stengt_er_koden_1(self, stier):
        """Aksjen ble tatt inn fredag kveld. Lørdag har jobben dagens kall, så
        er det ikke kall da, mangler noe som skulle vært hentet."""
        raa, base = stier
        fredag = OEYEBLIKK_22_09 + timedelta(days=3)
        kjoer_23(raa, base, fredag)
        med_boersen(base)
        _foelg(base)
        kode, _, _ = kjoer_23_kode(
            raa, base, fredag + timedelta(minutes=45), les_kvote=kvote(brukt=20, dato="2026-09-25")
        )
        assert kode == 4
        loerdag = fredag + timedelta(days=1, minutes=15)
        kode, kall, ut = kjoer_23_kode(raa, base, loerdag, les_kvote=kvote(brukt=20, dato="2026-09-26"))
        assert kode == 1 and kall == [] and "Kode 4" not in ut


class TestSomFoer:
    def test_med_kall_igjen_hentes_aksjen_og_koden_er_0(self, stier):
        """Det som hentes, er ikke endret: ville feilet hvis en aksje som er
        tatt inn, ikke lenger ble hentet når det er kall igjen."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        fil, kall, ut = kjoer_23(raa, base, KL_22_45, les_kvote=kvote(brukt=16))
        assert fil is not None and kall == ["NYA.OL"] and "Kode 4" not in ut
        assert _kurser(base, "NYA") > 0

    def test_ingenting_er_skrevet_av_en_kjoering_med_kode_4(self, stier):
        """Ville feilet hvis kjøringen med kode 4 skrev en rad i vurdering for
        aksjen, så 9.28 og 2.21 leste den som forsøkt hentet."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        _foelg(base)
        for oeyeblikk in (KL_22_45, KL_23_15):
            assert kjoer_23_kode(raa, base, oeyeblikk, les_kvote=UTEN_KALL)[0] == 4
        tilkobling = aapne_base(base)
        try:
            assert valg.ikke_forsoekt(tilkobling) == {"NYA": TIRSDAG_22_09}
            assert tilkobling.execute("SELECT count(*) FROM vurdering WHERE symbol = 'NYA'").fetchone()[0] == 0
        finally:
            tilkobling.close()


class TestTekstene:
    def test_skriptet_gir_koden_videre_og_sier_hva_den_betyr(self):
        """Ville feilet hvis kveldsjobben gjorde 4 om til en annen kode, eller
        loggen ikke sa hva 4 betyr."""
        kode = (ROT / "start" / "kveldshenting.ps1").read_text(encoding="utf-8-sig")
        assert "exit $kode" in kode.splitlines()[-1]
        assert "if ($kode -eq 4)" in kode and "Det er i orden" in kode

    def test_hjelpen_og_installasjonen_sier_hva_koden_betyr(self):
        """Ville feilet hvis hjelpen fortsatt sa at hentingen slutter med
        kode 1 i tilfellet, eller installasjonen ikke nevnte koden."""
        hjelp = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "hentingen slutter med kode 1 fordi det nye forsøket ikke har kall" not in hjelp
        assert "kode 4" in hjelp
        installasjon = (ROT / "docs" / "installasjon.md").read_text(encoding="utf-8")
        assert "Kode 4" in installasjon and "`LastTaskResult`" in installasjon
