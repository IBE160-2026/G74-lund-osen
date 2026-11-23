"""Story 9.27: statusene i «Dine egne aksjer» og «Følg en aksje» regner dagen.

Spesifikasjonen er spec-9-27-statusene-regner-dagen.md, og svaret er gruppens
23.11 kl. 14:49 på spørsmål 3 i 9.25. Hver test lager sin egen base under
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
from test_valg import FASTE, med_boersen

ROT = Path(__file__).resolve().parent.parent
MALENE = ROT / "src" / "templates"
OSLO = ZoneInfo("Europe/Oslo")


def kl(maaned: int, dag: int, time_: int, minutt: int = 0) -> datetime:
    return datetime(2026, maaned, dag, time_, minutt, tzinfo=OSLO)


def d(maaned: int, dag: int) -> date:
    return date(2026, maaned, dag)


# Torsdag 12.11.2026 er børsdag, lørdag 14.11 ikke. 24.12 og 25.12 er stengt.
ONSDAG, TORSDAG, FREDAG = d(11, 11), d(11, 12), d(11, 13)


def _synlig(side: str) -> str:
    """Teksten på siden uten tagger og skript, med mellomrom samlet."""
    side = re.sub(r"<(script|style)\b.*?</\1>", "", side, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", side))


class TestDagen:
    """Dagen et ønske tidligst tas i bruk, og teksten for den."""

    @pytest.mark.parametrize(
        ("kursdag", "naa", "dag", "ventet"),
        [
            # Før kl. 22 en børsdag.
            (ONSDAG, kl(11, 12, 15), TORSDAG, "i kveld etter kl. 22"),
            # Etter kl. 22, og jobben har ikke hentet dagen ennå.
            (ONSDAG, kl(11, 12, 22, 5), TORSDAG, "i kveld etter kl. 22"),
            # Etter jobben: dagen er i basen.
            (TORSDAG, kl(11, 12, 23), FREDAG, "i morgen etter kl. 22"),
            # Paa minuttet: kl. 22:00 er ikke foer grensen (gjennomgangen, VG2).
            (TORSDAG, kl(11, 12, 22, 0), FREDAG, "i morgen etter kl. 22"),
            # Klokka i UTC, som appen gir den: 21:30 UTC er 22:30 i Oslo om
            # vinteren (gjennomgangen, VG4).
            (TORSDAG, datetime(2026, 11, 12, 21, 30, tzinfo=timezone.utc), FREDAG, "i morgen etter kl. 22"),
            (ONSDAG, datetime(2026, 11, 12, 20, 30, tzinfo=timezone.utc), TORSDAG, "i kveld etter kl. 22"),
            # Fredag etter jobben: helgen hoppes over.
            (FREDAG, kl(11, 13, 23), d(11, 16), "mandag etter kl. 22"),
            # En lørdag, med fredagen i basen.
            (FREDAG, kl(11, 14, 10), d(11, 16), "mandag etter kl. 22"),
            # En lørdag der basen mangler fredagen: stripa sier «kan hentes
            # nå», men ønskene tas bare i bruk på en børsdag (ECH3 i 2.12).
            (TORSDAG, kl(11, 14, 10), d(11, 16), "mandag etter kl. 22"),
            # Søndag kveld.
            (FREDAG, kl(11, 15, 23), d(11, 16), "i morgen etter kl. 22"),
            # Etter midnatt en børsdag: før kl. 22 igjen.
            (d(11, 9), kl(11, 10, 0, 30), d(11, 10), "i kveld etter kl. 22"),
            # Fridag: 24.12 og 25.12 er stengt.
            (d(12, 23), kl(12, 23, 23), d(12, 28), "mandag etter kl. 22"),
            (d(12, 23), kl(12, 24, 12), d(12, 28), "mandag etter kl. 22"),
            # En henting med --uten-tidskontroll før kl. 22 fikk dagens kurs.
            # Hentingen etter kl. 22 samme dag tar ønsket i bruk.
            (TORSDAG, kl(11, 12, 15), TORSDAG, "i kveld etter kl. 22"),
            # En tom base har ingen kursdag.
            (None, kl(11, 12, 15), TORSDAG, "i kveld etter kl. 22"),
            (None, kl(11, 12, 23), TORSDAG, "i kveld etter kl. 22"),
            (None, kl(11, 14, 10), d(11, 16), "mandag etter kl. 22"),
        ],
    )
    def test_dagen_og_teksten(self, kursdag, naa, dag, ventet):
        """Ville feilet hvis statusen sa «i kveld» etter jobben, en lørdag
        eller en fridag, eller «i morgen» en fredag."""
        from markedsoversikt import oensket_hentes_tekst

        assert boersdag.neste_henting_av_oensket(kursdag, naa) == dag
        assert oensket_hentes_tekst(kursdag, naa) == ventet

    def test_ukedag_og_dato_naar_det_er_mer_enn_en_uke(self, monkeypatch):
        """Ville feilet hvis en dag mer enn en uke fram bare fikk ukedagen."""
        from markedsoversikt import oensket_hentes_tekst

        stengt = frozenset(boersdag.stengte_dager(2026)) | {d(11, n) for n in range(16, 25)}
        monkeypatch.setattr(boersdag, "stengte_dager", lambda aar: stengt)
        assert oensket_hentes_tekst(FREDAG, kl(11, 13, 23)) == "onsdag 25.11 etter kl. 22"

    def test_klokkeslettet_kommer_fra_tidsgrensen(self, monkeypatch):
        """Ville feilet hvis «kl. 22» sto fast, eller grensen for «i kveld»
        ikke var TIDSGRENSE."""
        from markedsoversikt import oensket_hentes_tekst

        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        assert oensket_hentes_tekst(ONSDAG, kl(11, 12, 15)) == "i kveld etter kl. 21.30"
        assert oensket_hentes_tekst(TORSDAG, kl(11, 12, 21, 45)) == "i morgen etter kl. 21.30"

    def test_ingen_dag_utenfor_kalenderen(self, monkeypatch):
        """NFR-08: ville feilet hvis statusen gjettet en dag kalenderen ikke
        dekker. Da står bare klokkeslettet."""
        from markedsoversikt import oensket_hentes_tekst

        monkeypatch.setattr(boersdag, "dekker", lambda aar: aar == 2026)
        assert oensket_hentes_tekst(d(12, 30), kl(12, 30, 23)) == "etter kl. 22"

    @pytest.mark.parametrize("kursdag", [kl(11, 12, 22, 15), datetime(2026, 11, 12), "2026-11-12"])
    def test_noe_annet_enn_en_dato_er_som_ingen_kursdag(self, kursdag):
        """Ville feilet hvis et tidspunkt eller en tekst ble lest som at
        dagen er hentet, eller ga en feil på siden."""
        from markedsoversikt import oensket_hentes_tekst

        assert oensket_hentes_tekst(kursdag, kl(11, 12, 23)) == "i kveld etter kl. 22"

    def test_stripa_sier_det_samme_som_foer(self):
        """Stripa og statusene deler funksjonen som skriver dagen. Ville
        feilet hvis stripa fikk en annen ordlyd."""
        from markedsoversikt import neste_henting_tekst

        assert neste_henting_tekst(ONSDAG, kl(11, 12, 15)) == "nye kurser fra kl. 22 i kveld"
        assert neste_henting_tekst(TORSDAG, kl(11, 12, 23)) == "nye kurser fra kl. 22 i morgen"
        assert neste_henting_tekst(FREDAG, kl(11, 14, 10)) == "nye kurser fra mandag kl. 22"
        assert neste_henting_tekst(TORSDAG, kl(11, 14, 10)) == "nye kurser kan hentes nå"


def test_ingen_mal_sier_i_kveld_om_hentingen_etter_grensen():
    """Ville feilet hvis en mal hadde «i kveld etter» skrevet inn foran
    klokkeslettet, i stedet for dagen som regnes."""
    for mal in sorted(MALENE.glob("*.html")):
        tekst = re.sub(r"\{#.*?#\}", "", mal.read_text(encoding="utf-8"), flags=re.S)
        assert "i kveld etter" not in tekst, mal.name


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


# Kursene i basen går til og med tirsdag 22.09.2026.
FOER_KL_22 = (kl(9, 23, 12), "i kveld etter kl. 22")
ETTER_JOBBEN = (kl(9, 22, 23), "i morgen etter kl. 22")
LOERDAG = (kl(9, 26, 10), "mandag etter kl. 22")
TIDENE = pytest.mark.parametrize(("naa", "naar"), [FOER_KL_22, ETTER_JOBBEN, LOERDAG], ids=["foer", "etter", "loerdag"])


class TestSidene:
    """De fire stedene i den ekte versjonen, før kl. 22, etter jobben og en
    lørdag."""

    @TIDENE
    def test_venter_paa_henting(self, klient, monkeypatch, naa, naar):
        """Ville feilet hvis «Dine egne aksjer» sa «i kveld» etter jobben
        eller en lørdag."""
        monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone(timezone.utc))
        assert klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft"}).status_code == 303
        side = _synlig(klient.get("/").data.decode("utf-8"))
        assert f"Venter på henting {naar}." in side
        assert side.count("Venter på henting ") == 1

    @TIDENE
    def test_fjernes_ved_hentingen(self, klient, monkeypatch, naa, naar):
        """Ville feilet hvis en aksje som fjernes, sa «i kveld» etter jobben
        eller en lørdag, i «Dine egne aksjer» eller i Min liste."""
        monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone(timezone.utc))
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
        """Ville feilet hvis «Følg en aksje» sa «tidligst i kveld» etter
        jobben eller en lørdag."""
        monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone(timezone.utc))
        side = _synlig(klient.get("/folg?kode=NYA").data.decode("utf-8"))
        assert f"Aksjen hentes ved neste henting, tidligst {naar}." in side

    def test_klokkeslettet_paa_sidene(self, klient, monkeypatch):
        """Ville feilet hvis sidene hadde «kl. 22» når TIDSGRENSE er en annen."""
        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        monkeypatch.setattr(app_modul, "naa", lambda: kl(9, 22, 23).astimezone(timezone.utc))
        side = _synlig(klient.get("/folg?kode=NYA").data.decode("utf-8"))
        assert "tidligst i morgen etter kl. 21.30." in side


class TestDemoen:
    """Demoen henter aldri, og boksen under statusen sier det. Statusen står
    fast der, så bildene er like fra dag til dag."""

    @pytest.mark.parametrize("naa", [kl(11, 12, 15), kl(11, 12, 23), kl(11, 14, 10)], ids=["foer", "etter", "loerdag"])
    def test_statusen_staar_fast_i_demoen(self, monkeypatch, naa):
        """Ville feilet hvis statusen i demoen fulgte dagen demoen kjøres."""
        sti = lagring_sqlite.demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        demo.lag_demobase(sti, skriv=lambda _: None)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone(timezone.utc))
        app_modul.app.config["TESTING"] = True
        klient = app_modul.app.test_client()
        assert klient.post("/folg", data={"kode": "SKRH", "sektor": "Helse"}).status_code == 303
        side = _synlig(klient.get("/").data.decode("utf-8"))
        assert "Venter på henting i kveld etter kl. 22." in side and "Demoen henter ingenting" in side
        folg = _synlig(klient.get("/folg?kode=HVLK").data.decode("utf-8"))
        assert "tidligst i kveld etter kl. 22." in folg
