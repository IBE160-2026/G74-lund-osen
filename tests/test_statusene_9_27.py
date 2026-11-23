"""Story 9.27: statusene i «Dine egne aksjer» og «Følg en aksje» regner dagen.

Spesifikasjonen er spec-9-27-statusene-regner-dagen.md, og svarene er gruppens
23.11 kl. 14:49 på spørsmål 3 i 9.25 og kl. 22:25 på spørsmålene i 9.27: på en
børsdag står «i kveld» helt til midnatt, også etter første kjøring av
kveldsjobben (rådet anbefalte «i morgen», som stripa), og de andre stedene som
sier når en aksje tas ut, sier samme dag. Hver test lager sin egen base under
tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import re
from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import app as app_modul
import boersdag
import demo
import ferdige_lister
import lagring_sqlite
from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23
from test_notater import _kjoepsknapp, _uten_panelet
from test_valg import FASTE, med_boersen

ROT = Path(__file__).resolve().parent.parent
MALENE = ROT / "src" / "templates"
OSLO = ZoneInfo("Europe/Oslo")


def kl(maaned: int, dag: int, time_: int, minutt: int = 0) -> datetime:
    return datetime(2026, maaned, dag, time_, minutt, tzinfo=OSLO)


def d(maaned: int, dag: int) -> date:
    return date(2026, maaned, dag)


# Torsdag 12.11.2026 er børsdag, lørdag 14.11 ikke. 24.12 og 25.12 er stengt.
TORSDAG, FREDAG, MANDAG = d(11, 12), d(11, 13), d(11, 16)
I_KVELD = "i kveld etter kl. 22"


def _synlig(side: str) -> str:
    """Teksten på siden uten tagger og skript, med mellomrom samlet."""
    side = re.sub(r"<(script|style)\b.*?</\1>", "", side, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", side))


class TestDagen:
    """Dagen et ønske tidligst tas i bruk, og teksten for den."""

    @pytest.mark.parametrize(
        ("naa", "dag", "ventet"),
        [
            # En børsdag: «i kveld» helt til midnatt, også etter første
            # kjøring av kveldsjobben (svaret 23.11 kl. 22:25, spørsmål 1).
            (kl(11, 12, 15), TORSDAG, I_KVELD),
            (kl(11, 12, 21, 59), TORSDAG, I_KVELD),
            (kl(11, 12, 22, 0), TORSDAG, I_KVELD),
            (kl(11, 12, 23), TORSDAG, I_KVELD),
            (kl(11, 12, 23, 59), TORSDAG, I_KVELD),
            # Kl. 00:01 natt til neste børsdag: «i kveld», for den nye dagen.
            (kl(11, 13, 0, 1), FREDAG, I_KVELD),
            # En fredag kl. 23: fortsatt i kveld, ikke mandag.
            (kl(11, 13, 23), FREDAG, I_KVELD),
            # En lørdag, også kl. 00:01: ønskene tas bare i bruk på en
            # børsdag (ECH3 i 2.12), så det er mandag.
            (kl(11, 14, 0, 1), MANDAG, "mandag etter kl. 22"),
            (kl(11, 14, 10), MANDAG, "mandag etter kl. 22"),
            # Søndag kveld.
            (kl(11, 15, 23), MANDAG, "i morgen etter kl. 22"),
            # Fridag: 24.12 og 25.12 er stengt, og 23.12 er børsdag.
            (kl(12, 23, 23), d(12, 23), I_KVELD),
            (kl(12, 24, 12), d(12, 28), "mandag etter kl. 22"),
            # Klokka i UTC, som appen gir den: 22:30 UTC torsdag er 23:30 i
            # Oslo om vinteren, 23:30 UTC torsdag er fredag kl. 00:30, og
            # 23:30 UTC fredag er lørdag kl. 00:30.
            (datetime(2026, 11, 12, 22, 30, tzinfo=timezone.utc), TORSDAG, I_KVELD),
            (datetime(2026, 11, 12, 23, 30, tzinfo=timezone.utc), FREDAG, I_KVELD),
            (datetime(2026, 11, 13, 23, 30, tzinfo=timezone.utc), MANDAG, "mandag etter kl. 22"),
        ],
    )
    def test_dagen_og_teksten(self, naa, dag, ventet):
        """Ville feilet hvis statusen sa «i morgen» etter kl. 22 en børsdag,
        «mandag» en fredag kveld, eller «i kveld» en lørdag eller en fridag."""
        from markedsoversikt import oensket_hentes_tekst

        assert boersdag.neste_henting_av_oensket(naa) == dag
        assert oensket_hentes_tekst(naa) == ventet

    def test_ukedag_og_dato_naar_det_er_mer_enn_en_uke(self, monkeypatch):
        """Ville feilet hvis en dag mer enn en uke fram bare fikk ukedagen."""
        from markedsoversikt import oensket_hentes_tekst

        stengt = frozenset(boersdag.stengte_dager(2026)) | {d(11, n) for n in range(16, 25)}
        monkeypatch.setattr(boersdag, "stengte_dager", lambda aar: stengt)
        assert oensket_hentes_tekst(kl(11, 14, 10)) == "onsdag 25.11 etter kl. 22"

    def test_klokkeslettet_kommer_fra_tidsgrensen(self, monkeypatch):
        """Ville feilet hvis «kl. 22» sto fast. Grensen flytter ikke dagen:
        etter den står fortsatt «i kveld» (svaret 23.11 kl. 22:25)."""
        from markedsoversikt import oensket_hentes_tekst

        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        assert oensket_hentes_tekst(kl(11, 12, 15)) == "i kveld etter kl. 21.30"
        assert oensket_hentes_tekst(kl(11, 12, 21, 45)) == "i kveld etter kl. 21.30"
        assert oensket_hentes_tekst(kl(11, 14, 10)) == "mandag etter kl. 21.30"

    def test_ingen_dag_utenfor_kalenderen(self, monkeypatch):
        """NFR-08: ville feilet hvis statusen gjettet en dag kalenderen ikke
        dekker. Da står bare klokkeslettet. 31.12.2026 er stengt, så neste
        børsdag ligger i 2027."""
        from markedsoversikt import oensket_hentes_tekst

        monkeypatch.setattr(boersdag, "dekker", lambda aar: aar == 2026)
        assert oensket_hentes_tekst(kl(12, 31, 12)) == "etter kl. 22"
        # Gjennomgangen etter svarene (VG6): også når dagen selv ligger utenfor.
        monkeypatch.setattr(boersdag, "dekker", lambda aar: aar == 2027)
        assert oensket_hentes_tekst(kl(11, 12, 15)) == "etter kl. 22"

    def test_stripa_sier_det_samme_som_foer(self):
        """Stripa og statusene deler funksjonen som skriver dagen, men ikke
        dagen: stripa sier «i morgen» etter jobben, som før (svaret 23.11
        kl. 22:25: stripa endres ikke). Ville feilet hvis stripa fikk en
        annen ordlyd eller fulgte statusene."""
        from markedsoversikt import neste_henting_tekst

        assert neste_henting_tekst(d(11, 11), kl(11, 12, 15)) == "nye kurser fra kl. 22 i kveld"
        assert neste_henting_tekst(TORSDAG, kl(11, 12, 23)) == "nye kurser fra kl. 22 i morgen"
        assert neste_henting_tekst(FREDAG, kl(11, 14, 10)) == "nye kurser fra mandag kl. 22"
        assert neste_henting_tekst(TORSDAG, kl(11, 14, 10)) == "nye kurser kan hentes nå"


def test_ingen_mal_har_dagen_skrevet_inn():
    """Ville feilet hvis en mal hadde «i kveld» eller «før kvelden» skrevet
    inn i teksten som vises, i stedet for dagen som regnes (spørsmål 2 i
    9.27). Kommentarene i malene teller ikke."""
    for mal in sorted(MALENE.glob("*.html")):
        tekst = re.sub(r"\{#.*?#\}", "", mal.read_text(encoding="utf-8"), flags=re.S)
        assert "i kveld" not in tekst and "før kvelden" not in tekst, mal.name


@pytest.fixture(autouse=True)
def faste_bransjer(monkeypatch):
    for kode, bransje in FASTE.items():
        monkeypatch.setitem(ferdige_lister.BRANSJE, kode, bransje)


@pytest.fixture
def klient(tmp_path, monkeypatch):
    """Den ekte versjonen, med kursene til og med tirsdag 22.09.2026."""
    base = tmp_path / "db" / "ose.db"
    kjoer_23(tmp_path / "raa", base, OEYEBLIKK_22_09)
    med_boersen(base)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


# Kursene i basen går til og med tirsdag 22.09.2026. Etter jobben og en fredag
# kveld sto «i morgen» og «mandag» før svaret 23.11 kl. 22:25; nå «i kveld».
FOER_KL_22 = (kl(9, 23, 12), I_KVELD)
ETTER_JOBBEN = (kl(9, 22, 23), I_KVELD)
FREDAG_KVELD = (kl(9, 25, 23), I_KVELD)
LOERDAG = (kl(9, 26, 10), "mandag etter kl. 22")
TIDENE = pytest.mark.parametrize(
    ("naa", "naar"), [FOER_KL_22, ETTER_JOBBEN, FREDAG_KVELD, LOERDAG], ids=["foer", "etter", "fredag", "loerdag"]
)
# De andre stedene (spørsmål 2 i 9.27): en børsdag og en lørdag for hvert sted.
TO_TIDER = pytest.mark.parametrize(("naa", "naar"), [ETTER_JOBBEN, LOERDAG], ids=["etter", "loerdag"])


def _klokka(monkeypatch, naa: datetime) -> None:
    monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone(timezone.utc))


class TestSidene:
    """Statusene i den ekte versjonen, før kl. 22, etter jobben, en fredag
    kveld og en lørdag."""

    @TIDENE
    def test_venter_paa_henting(self, klient, monkeypatch, naa, naar):
        """Ville feilet hvis «Dine egne aksjer» sa «i kveld» en lørdag, eller
        «i morgen» etter første kjøring en børsdag."""
        _klokka(monkeypatch, naa)
        assert klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft"}).status_code == 303
        side = _synlig(klient.get("/").data.decode("utf-8"))
        assert f"Venter på henting {naar}." in side
        assert side.count("Venter på henting ") == 1

    @TIDENE
    def test_fjernes_ved_hentingen(self, klient, monkeypatch, naa, naar):
        """Ville feilet hvis en aksje som fjernes, sa en annen dag enn
        statusen, i «Dine egne aksjer» eller i Min liste."""
        _klokka(monkeypatch, naa)
        assert klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft", "bytt": "DNB"}).status_code == 303
        assert f"Fjernes ved hentingen {naar}." in _synlig(klient.get("/min-liste").data.decode("utf-8"))
        # En egen aksje som er hentet og så fjernes, står i «Dine egne aksjer».
        tilkobling = lagring_sqlite.aapne_base(lagring_sqlite.BASE_STI)
        try:
            with tilkobling:
                tilkobling.execute(
                    "INSERT INTO oenske (handling, symbol, navn, sektor, laget, tatt_i_bruk) VALUES "
                    "('folg', 'EQNR', 'Equinor', 'Energi', '2026-09-21T12:00:00+00:00', '2026-09-22')"
                )
        finally:
            tilkobling.close()
        assert klient.post("/fjern", data={"symbol": "EQNR"}).status_code == 303
        side = klient.get("/").data.decode("utf-8")
        egne = _synlig(side.split('id="dine-egne-aksjer"', 1)[1].split("</section>", 1)[0])
        assert f"Fjernes ved hentingen {naar}." in egne

    @TIDENE
    def test_foelg_en_aksje(self, klient, monkeypatch, naa, naar):
        """Ville feilet hvis «Følg en aksje» sa en annen dag enn statusen, i
        «tidligst …» eller i «Fjerner du aksjen før hentingen …» (AA5)."""
        _klokka(monkeypatch, naa)
        side = _synlig(klient.get("/folg?kode=NYA").data.decode("utf-8"))
        assert f"Aksjen hentes ved neste henting, tidligst {naar}." in side
        assert f"Fjerner du aksjen før hentingen {naar}, brukes ingen kall." in side
        assert "før kvelden" not in side

    def test_klokkeslettet_paa_sidene(self, klient, monkeypatch):
        """Ville feilet hvis sidene hadde «kl. 22» når TIDSGRENSE er en annen."""
        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        _klokka(monkeypatch, kl(9, 26, 10))
        side = _synlig(klient.get("/folg?kode=NYA").data.decode("utf-8"))
        assert "tidligst mandag etter kl. 21.30." in side


class TestDeAndreStedene:
    """Spørsmål 2 i 9.27 (AA1–AA3): aksjesiden, merknaden i Min liste og «Er
    du sikker?» sier samme dag som statusen."""

    @TO_TIDER
    def test_aksjesiden(self, klient, monkeypatch, naa, naar):
        """AA1: ville feilet hvis aksjesiden sa «ved hentingen i kveld» en
        lørdag om en aksje som fjernes."""
        _klokka(monkeypatch, naa)
        assert klient.post("/aksje/DNB/notat", data={"dag": "2026-09-22", "tekst": "x"}).status_code == 303
        assert klient.post("/fjern", data={"symbol": "DNB"}).status_code == 303
        # Gjennomgangen etter svarene (VG2): uten panelet «Mine notater», som
        # har den samme setningen fra merknaden i app.py.
        side = _synlig(_uten_panelet(klient.get("/aksje/DNB").data.decode("utf-8")))
        assert f"fjernes fra lista ved hentingen {naar} og får ingen nye kurser" in side

    @TO_TIDER
    def test_merknaden_i_min_liste(self, klient, monkeypatch, naa, naar):
        """AA2: ville feilet hvis merknaden ved notatene i Min liste sa «ved
        hentingen i kveld» en lørdag."""
        _klokka(monkeypatch, naa)
        assert klient.post("/aksje/DNB/notat", data={"dag": "2026-09-22", "tekst": "x"}).status_code == 303
        assert klient.post("/fjern", data={"symbol": "DNB"}).status_code == 303
        side = _synlig(klient.get("/min-liste").data.decode("utf-8"))
        assert f"fjernes fra lista ved hentingen {naar} og får ingen nye kurser" in side

    @TO_TIDER
    def test_er_du_sikker(self, klient, monkeypatch, naa, naar):
        """AA3: ville feilet hvis «Er du sikker?» sa «fra og med hentingen i
        kveld» en lørdag om en aksje med et åpent tenkt kjøp."""
        _klokka(monkeypatch, naa)
        assert klient.post("/aksje/DNB/notat", data={"dag": "2026-09-22", "tekst": "x"}).status_code == 303
        felt = _kjoepsknapp(klient.get("/aksje/DNB").data.decode("utf-8"))
        assert felt, "skjemaet for et tenkt kjøp mangler"
        assert klient.post("/aksje/DNB/notat/kjoep", data=felt).status_code == 303
        svar = klient.post("/fjern", data={"symbol": "DNB"})
        assert svar.status_code == 200
        side = _synlig(svar.data.decode("utf-8"))
        assert f"hentes ingen kurser for den fra og med hentingen {naar}. Endringen" in side


class TestDemoen:
    """Demoen henter aldri, og boksen under statusen sier det. Statusen står
    fast der, så bildene er like fra dag til dag (svaret på spørsmål 3 i 9.27)."""

    @pytest.mark.parametrize("naa", [kl(11, 12, 15), kl(11, 12, 23), kl(11, 14, 10)], ids=["foer", "etter", "loerdag"])
    def test_statusen_staar_fast_i_demoen(self, monkeypatch, naa):
        """Ville feilet hvis statusen i demoen fulgte dagen demoen kjøres.
        Lørdagen skiller: der sier den ekte versjonen «mandag»."""
        sti = lagring_sqlite.demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        demo.lag_demobase(sti, skriv=lambda _: None)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        _klokka(monkeypatch, naa)
        app_modul.app.config["TESTING"] = True
        klient = app_modul.app.test_client()
        folg = _synlig(klient.get("/folg?kode=HVLK").data.decode("utf-8"))
        assert "tidligst i kveld etter kl. 22." in folg
        assert "Fjerner du aksjen før hentingen i kveld etter kl. 22, brukes ingen kall." in folg
        assert klient.post("/folg", data={"kode": "SKRH", "sektor": "Helse"}).status_code == 303
        side = _synlig(klient.get("/").data.decode("utf-8"))
        assert "Venter på henting i kveld etter kl. 22." in side and "Demoen henter ingenting" in side
        # En aksje som fjernes, på aksjesiden (AA1). BRFE har bare et avsluttet
        # tenkt kjøp i demoen, så den fjernes uten spørsmål.
        assert klient.post("/fjern", data={"symbol": "BRFE", "tilbake": "oversikten"}).status_code == 303
        aksjen = _synlig(_uten_panelet(klient.get("/aksje/BRFE").data.decode("utf-8")))
        assert "fjernes fra lista ved hentingen i kveld etter kl. 22 og får ingen nye kurser" in aksjen
        # «Er du sikker?» (AA3). KVST har et åpent tenkt kjøp i demoen
        # (gjennomgangen etter svarene, VG4).
        svar = klient.post("/fjern", data={"symbol": "KVST", "tilbake": "oversikten"})
        assert svar.status_code == 200
        assert "fra og med hentingen i kveld etter kl. 22. Endringen" in _synlig(svar.data.decode("utf-8"))
