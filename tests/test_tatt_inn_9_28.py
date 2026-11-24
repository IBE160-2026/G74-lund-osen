"""Story 9.28: en egen aksje som er tatt inn uten kurser, står ikke som «Hentet».

Spesifikasjonen er spec-9-28-tatt-inn-uten-kurser.md, og svaret er gruppens
23.11 kl. 23:27 på spørsmål 4 i 9.27 (AA1). Tilstandene lages med hentingen
selv, slik kveldsjobben gjør det: en senere kjøring uten kall igjen tar ønsket
i bruk uten å spørre EODHD, og en vanlig henting der EODHD ikke gir kurser,
skriver en rad i vurdering med en grunn. Hver test lager sin egen base under
tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

import app as app_modul
import boersdag
import ferdige_lister
import lagring_sqlite
import valg
from lagring_sqlite import aapne_base
from test_fetch_prices import OEYEBLIKK_22_09, TIRSDAG_22_09, kjoer_23, kjoer_23_kode, kvote, serie_til
from test_valg import FASTE, med_boersen
from valg import Valglager

OSLO = ZoneInfo("Europe/Oslo")
EODHD = "EODHD har ikke gitt kurser for aksjen."
SLUTTER = "slutter appen å følge en aksje du har valgt selv"
HENTET = "Hentet. Står i tabellen over."


def kl(maaned: int, dag: int, time_: int, minutt: int = 0) -> datetime:
    return datetime(2026, maaned, dag, time_, minutt, tzinfo=OSLO)


def _synlig(side: str) -> str:
    """Teksten på siden uten tagger og skript, med mellomrom samlet."""
    side = re.sub(r"<(script|style)\b.*?</\1>", "", side, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", side))


def _egne(side: str) -> str:
    """Delen «Dine egne aksjer» på oversikten, som synlig tekst."""
    return _synlig(side.split('id="dine-egne-aksjer"', 1)[1].split("</section>", 1)[0])


@pytest.fixture(autouse=True)
def faste_bransjer(monkeypatch):
    for kode, bransje in FASTE.items():
        monkeypatch.setitem(ferdige_lister.BRANSJE, kode, bransje)


def _foelg(base, kode: str = "NYA") -> None:
    lager = Valglager(aapne_base(base), lambda: OEYEBLIKK_22_09)
    try:
        lager.folg(kode, "Kraft")
    finally:
        lager._t.close()


@pytest.fixture
def tatt_inn(tmp_path):
    """NYA er tatt inn tirsdag 22.09 av en senere kjøring uten kall igjen:
    kveldens henting er ferdig, ønsket kom etterpå, og kjøringen kl. 22:45
    tar det i bruk, men det nye forsøket har ingen kall."""
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    med_boersen(base)
    _foelg(base)
    kode, kall, ut = kjoer_23_kode(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=45), les_kvote=kvote(brukt=20))
    assert kode == 1 and kall == [], ut
    assert "NYA er tatt inn i lista fra 2026-09-22." in ut
    return base


@pytest.fixture
def ga_ingen(tmp_path):
    """NYA er tatt inn tirsdag 22.09 av kveldens henting, og EODHD ga ingen
    kurser for den, som i test_valg.py."""
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
    med_boersen(base)
    _foelg(base)

    def hent(ticker, *a):
        return [] if ticker == "NYA.OL" else serie_til(TIRSDAG_22_09)

    kode, kall, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, hent)
    assert kode == 1 and "NYA.OL" in kall
    return base


def _klient(monkeypatch, base, naa: datetime):
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone(timezone.utc))
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


class TestRegelen:
    """Forskjellen ses av det som alt er lagret: en rad i vurdering fra dagen
    aksjen kom inn. Ingen migrering."""

    def test_tatt_inn_uten_kall_er_ikke_forsoekt(self, tatt_inn):
        """Ville feilet hvis en aksje som bare er tatt inn, ikke ble funnet."""
        tilkobling = aapne_base(tatt_inn)
        try:
            assert valg.ikke_forsoekt(tilkobling) == {"NYA": TIRSDAG_22_09}
            assert tilkobling.execute("SELECT count(*) FROM kurs WHERE symbol = 'NYA'").fetchone()[0] == 0
            assert tilkobling.execute("SELECT count(*) FROM vurdering WHERE symbol = 'NYA'").fetchone()[0] == 0
        finally:
            tilkobling.close()

    def test_eodhd_ga_ingen_kurser_er_forsoekt(self, ga_ingen):
        """Ville feilet hvis en aksje EODHD ikke ga kurser for, ble lest som
        ikke forsøkt: hentingen skrev en rad i vurdering med en grunn."""
        tilkobling = aapne_base(ga_ingen)
        try:
            assert valg.ikke_forsoekt(tilkobling) == {}
            assert tilkobling.execute("SELECT count(*) FROM kurs WHERE symbol = 'NYA'").fetchone()[0] == 0
            assert tilkobling.execute("SELECT count(*) FROM vurdering WHERE symbol = 'NYA'").fetchone()[0] == 1
        finally:
            tilkobling.close()

    def test_bare_egne_aksjer_uten_kurser(self, tmp_path):
        """Ville feilet hvis en aksje med kurser, eller en aksje som ikke er
        valgt på siden, ble regnet med."""
        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
        med_boersen(base)
        _foelg(base)
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        tilkobling = aapne_base(base)
        try:
            assert valg.egne_i_lista(tilkobling) == {"NYA"}
            assert valg.ikke_forsoekt(tilkobling) == {}
            # En aksje fra den første lista er ikke en egen aksje.
            # Gjennomgangen (VG2): den har en dag den kom inn, så bare det at
            # den ikke er valgt på siden, holder den utenfor. (VG4): en egen
            # aksje med kurser er aldri med, heller ikke uten rad i vurdering.
            with tilkobling:
                tilkobling.execute("UPDATE aksje SET inn = '2026-09-22' WHERE symbol = 'DNB'")
            rader = tilkobling.execute(
                "SELECT (SELECT count(*) FROM kurs WHERE symbol = 'DNB'), (SELECT inn FROM aksje WHERE symbol = 'DNB')"
            ).fetchone()
            assert rader[0] > 0 and rader[1] == "2026-09-22"
            assert valg.ikke_forsoekt(tilkobling) == {}
        finally:
            tilkobling.close()

    def test_regelen_skriver_ingenting(self, tatt_inn):
        """AD-3 og AD-10: ville feilet hvis regelen skrev i basen."""
        tilkobling = aapne_base(tatt_inn)
        try:
            foer = tilkobling.total_changes
            valg.ikke_forsoekt(tilkobling)
            assert tilkobling.total_changes == foer
        finally:
            tilkobling.close()


class TestDagen:
    """Kursene kommer ved hentingen dagen etter at aksjen kom inn, også i
    helgen, med dagen skrevet som i 9.27 (gjennomgangen, ECH1)."""

    @pytest.mark.parametrize(
        ("inn", "naa", "ventet"),
        [
            # Samme kveld som aksjen kom inn: kveldens kall er brukt, så
            # kursene kommer dagen etter.
            (date(2026, 9, 22), kl(9, 22, 23), "i morgen etter kl. 22"),
            (date(2026, 9, 22), kl(9, 22, 23, 59), "i morgen etter kl. 22"),
            # Dagen etter: i kveld.
            (date(2026, 9, 22), kl(9, 23, 0, 1), "i kveld etter kl. 22"),
            (date(2026, 9, 22), kl(9, 23, 12), "i kveld etter kl. 22"),
            # Hentingen dagen etter gikk ikke: i kveld, hver dag til den går.
            (date(2026, 9, 22), kl(9, 24, 12), "i kveld etter kl. 22"),
            # Tatt inn en fredag: jobben går også lørdag, og et nytt forsøk
            # henter fredagens kurs da. Ikke «mandag».
            (date(2026, 9, 25), kl(9, 25, 23), "i morgen etter kl. 22"),
            (date(2026, 9, 25), kl(9, 26, 10), "i kveld etter kl. 22"),
            (date(2026, 9, 25), kl(9, 27, 23), "i kveld etter kl. 22"),
            (date(2026, 9, 25), kl(9, 28, 10), "i kveld etter kl. 22"),
            # Klokka i UTC, som appen gir den: 22:30 UTC er 00:30 dagen etter
            # i Oslo om sommeren.
            (date(2026, 9, 22), datetime(2026, 9, 22, 21, 30, tzinfo=timezone.utc), "i morgen etter kl. 22"),
            (date(2026, 9, 22), datetime(2026, 9, 22, 22, 30, tzinfo=timezone.utc), "i kveld etter kl. 22"),
        ],
    )
    def test_teksten(self, inn, naa, ventet):
        """Ville feilet hvis statusen lovet kurser samme kveld som aksjen kom
        inn, eller sa «mandag» en fredag, når hentingen henter lørdag."""
        from markedsoversikt import kursene_kommer_tekst

        assert kursene_kommer_tekst(inn, naa) == ventet

    def test_klokkeslettet_kommer_fra_tidsgrensen(self, monkeypatch):
        """Ville feilet hvis «kl. 22» sto fast."""
        from datetime import time

        from markedsoversikt import kursene_kommer_tekst

        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        assert kursene_kommer_tekst(date(2026, 9, 22), kl(9, 22, 23)) == "i morgen etter kl. 21.30"

    def test_ingen_dag_slaas_opp_i_kalenderen(self, monkeypatch):
        """NFR-08: teksten gjetter ingen børsdag. Den regner bare dagen etter,
        så den står også når kalenderen ikke dekker året."""
        from markedsoversikt import kursene_kommer_tekst

        monkeypatch.setattr(boersdag, "dekker", lambda aar: False)
        assert kursene_kommer_tekst(date(2026, 9, 22), kl(9, 22, 23)) == "i morgen etter kl. 22"

    def test_hentingen_henter_aksjen_en_loerdag(self, tmp_path):
        """Grunnen til «i morgen» en fredag (gjennomgangen, ECH1): ville
        feilet hvis hentingen lørdag ikke hentet en aksje som ble tatt inn
        fredag kveld uten kall."""
        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        fredag_kl_22 = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)
        kjoer_23(raa, base, fredag_kl_22)
        med_boersen(base)
        _foelg(base)
        kode, kall, _ = kjoer_23_kode(
            raa, base, fredag_kl_22 + timedelta(minutes=45), les_kvote=kvote(brukt=20, dato="2026-09-25")
        )
        assert kode == 1 and kall == []
        tilkobling = aapne_base(base)
        try:
            assert valg.ikke_forsoekt(tilkobling) == {"NYA": date(2026, 9, 25)}
        finally:
            tilkobling.close()
        loerdag = datetime(2026, 9, 26, 20, 15, tzinfo=timezone.utc)
        _, kall, _ = kjoer_23(
            raa,
            base,
            loerdag,
            lambda *_: serie_til(date(2026, 9, 25)),
            les_kvote=kvote(brukt=0, dato="2026-09-26"),
        )
        assert kall == ["NYA.OL"]
        tilkobling = aapne_base(base)
        try:
            assert valg.ikke_forsoekt(tilkobling) == {}
            assert tilkobling.execute("SELECT count(*) FROM kurs WHERE symbol = 'NYA'").fetchone()[0] > 0
        finally:
            tilkobling.close()


class TestSidene:
    def test_statusen_sier_tatt_inn_og_naar_kursene_kommer(self, tatt_inn, monkeypatch):
        """Ville feilet hvis en aksje som bare er tatt inn, sto som «Hentet»,
        eller mistet knappen «Fjern»."""
        klient = _klient(monkeypatch, tatt_inn, kl(9, 22, 23))
        side = klient.get("/").data.decode("utf-8")
        egne = _egne(side)
        assert "Tatt inn. Kursene kommer ved hentingen i morgen etter kl. 22." in egne
        assert HENTET not in egne
        rad = side.split('id="dine-egne-aksjer"', 1)[1].split('<tr class="egen-rad">', 1)[1].split("</tr>", 1)[0]
        assert 'action="/fjern"' in rad and 'value="NYA"' in rad
        # Dagen etter, før kveldens henting.
        klient = _klient(monkeypatch, tatt_inn, kl(9, 23, 12))
        assert "Tatt inn. Kursene kommer ved hentingen i kveld etter kl. 22." in _egne(
            klient.get("/").data.decode("utf-8")
        )

    @pytest.mark.parametrize("adresse", ["/", "/min-liste", "/aksje/NYA"])
    def test_ingen_tekst_om_eodhd_for_en_aksje_som_bare_er_tatt_inn(self, tatt_inn, monkeypatch, adresse):
        """Ville feilet hvis «?» ved «Oppdatert» eller siden for aksjen sa at
        EODHD ikke ga kurser, eller at appen slutter å følge aksjen, når ingen
        har spurt EODHD."""
        klient = _klient(monkeypatch, tatt_inn, kl(9, 22, 23))
        svar = klient.get(adresse)
        assert svar.status_code == 200
        side = _synlig(svar.data.decode("utf-8"))
        assert EODHD not in side and SLUTTER not in side
        assert "kursene er ikke hentet ennå" in side

    def test_siden_for_aksjen_sier_naar_kursene_kommer(self, tatt_inn, monkeypatch):
        """Ville feilet hvis siden for aksjen ikke sa at den er tatt inn, og
        når kursene kommer."""
        klient = _klient(monkeypatch, tatt_inn, kl(9, 22, 23))
        side = _synlig(klient.get("/aksje/NYA").data.decode("utf-8"))
        assert "Ny Aksje ASA er tatt inn i lista, men kursene er ikke hentet ennå." in side
        assert "De kommer ved hentingen i morgen etter kl. 22." in side
        assert "ingen kursgraf og ingen sjekker for Ny Aksje ASA" in side

    def test_raden_i_tabellen_er_som_foer(self, tatt_inn, monkeypatch):
        """Raden nederst i tabellen sier «ingen kurser ennå» i begge
        tilfellene."""
        klient = _klient(monkeypatch, tatt_inn, kl(9, 22, 23))
        assert "ingen kurser ennå" in _synlig(klient.get("/").data.decode("utf-8"))

    @pytest.mark.parametrize("adresse", ["/", "/aksje/NYA"])
    def test_eodhd_ga_ingen_kurser_har_teksten_som_foer(self, ga_ingen, monkeypatch, adresse):
        """Ville feilet hvis tilfellet der EODHD faktisk ikke ga kurser, fikk
        den nye teksten."""
        klient = _klient(monkeypatch, ga_ingen, kl(9, 22, 23))
        side = klient.get(adresse).data.decode("utf-8")
        tekst = _synlig(side)
        assert EODHD in tekst and SLUTTER in tekst
        assert "kursene er ikke hentet ennå" not in tekst and "Tatt inn." not in tekst
        if adresse == "/":
            assert HENTET in _egne(side)

    def test_oversikten_uten_en_slik_aksje_er_som_foer(self, tmp_path, monkeypatch):
        """Ville feilet hvis «?» ved «Oppdatert» mistet teksten om aksjer uten
        kurser når ingen aksje bare er tatt inn."""
        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        klient = _klient(monkeypatch, base, kl(9, 22, 23))
        tekst = _synlig(klient.get("/").data.decode("utf-8"))
        assert EODHD in tekst and "kursene er ikke hentet ennå" not in tekst


@pytest.fixture
def blandet(tmp_path):
    """To egne aksjer uten kurser: NYB kom inn med kveldens henting, og EODHD
    ga ingen kurser for den. NYA kom inn av en senere kjøring uten kall."""
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
    med_boersen(base)
    _foelg(base, "NYB")

    def hent(ticker, *a):
        return [] if ticker == "NYB.OL" else serie_til(TIRSDAG_22_09)

    kode, kall, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, hent)
    assert kode == 1 and "NYB.OL" in kall
    _foelg(base)
    kode, kall, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09 + timedelta(minutes=45), les_kvote=kvote(brukt=20))
    assert kode == 1 and kall == []
    return base


def test_blandet_viser_begge_tekstene(blandet, monkeypatch):
    """Gjennomgangen (VG1): ville feilet hvis «?» ved «Oppdatert» mistet
    teksten om EODHD når én aksje er forsøkt hentet og en annen bare er tatt
    inn, eller hvis begge fikk samme status."""
    tilkobling = aapne_base(blandet)
    try:
        assert valg.ikke_forsoekt(tilkobling) == {"NYA": TIRSDAG_22_09}
    finally:
        tilkobling.close()
    klient = _klient(monkeypatch, blandet, kl(9, 22, 23))
    side = klient.get("/").data.decode("utf-8")
    tekst = _synlig(side)
    assert EODHD in tekst and "kursene er ikke hentet ennå" in tekst
    egne = _egne(side)
    assert egne.count("Tatt inn. Kursene kommer ved hentingen i morgen etter kl. 22.") == 1
    assert egne.count(HENTET) == 1
    assert EODHD in _synlig(klient.get("/aksje/NYB").data.decode("utf-8"))
    assert EODHD not in _synlig(klient.get("/aksje/NYA").data.decode("utf-8"))


def test_en_aksje_som_skal_fjernes_lover_ikke_kurser(tatt_inn, monkeypatch):
    """Gjennomgangen (BH2): ville feilet hvis en aksje som bare er tatt inn,
    og som så fjernes, fortsatt sa at kursene kommer. Den hentes aldri."""
    klient = _klient(monkeypatch, tatt_inn, kl(9, 22, 23))
    assert klient.post("/fjern", data={"symbol": "NYA"}).status_code == 303
    side = klient.get("/").data.decode("utf-8")
    egne = _egne(side)
    assert "Fjernes ved hentingen i kveld etter kl. 22." in egne and "Tatt inn." not in egne
    assert "De kommer ved hentingen" not in _synlig(klient.get("/aksje/NYA").data.decode("utf-8"))


def test_hentingen_er_ikke_endret_av_regelen(tatt_inn):
    """Neste børsdag henter hentingen aksjen som før, og tar den ikke ut:
    ville feilet hvis en aksje som bare er tatt inn, ble avvist kvelden
    etter."""
    raa = tatt_inn.parent.parent / "raa"
    _, kall, ut = kjoer_23(raa, tatt_inn, OEYEBLIKK_22_09 + timedelta(days=1))
    assert "NYA.OL" in kall and "ga ingen kurser" not in ut
    tilkobling = aapne_base(tatt_inn)
    try:
        assert valg.ikke_forsoekt(tilkobling) == {}
        assert tilkobling.execute("SELECT count(*) FROM kurs WHERE symbol = 'NYA'").fetchone()[0] > 0
    finally:
        tilkobling.close()
