"""Story 8.19: neste henting i stripa øverst (U60, tillegg 1 til 10.11,
gruppens svar 12.11 kl. 17:01).

Bare den ekte versjonen viser når nye kurser tidligst kan hentes, regnet med
børsdagskontrollen (2.3) og TIDSGRENSE. Den sier aldri at en henting kommer.
Klokka står fast i hver test. Spesifikasjonen:
_bmad-output/implementation-artifacts/spec-8-19-neste-henting-i-stripa.md.
"""

import shutil
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import app as app_modul
import boersdag
import demo
import fetch_prices
from boersdag import TIDSGRENSE, neste_henting
from hjelpetekster import hjelpetekster
from lagring_sqlite import demo_sti
from markedsoversikt import neste_henting_tekst
from test_app import monter, serie, snapshot

ROT = Path(__file__).resolve().parents[1]
OSLO = ZoneInfo("Europe/Oslo")


def kl(maaned: int, dag: int, time_: int, minutt: int = 0) -> datetime:
    return datetime(2026, maaned, dag, time_, minutt, tzinfo=OSLO)


# Torsdag 12.11.2026 er børsdag, lørdag 14.11 ikke. 24.12 og 25.12 er stengt.
ONSDAG_HENTET = kl(11, 11, 22, 15)
TORSDAG_HENTET = kl(11, 12, 22, 15)
FREDAG_HENTET = kl(11, 13, 22, 15)


class TestTilfellene:
    @pytest.mark.parametrize(
        ("hentet", "naa", "ventet"),
        [
            # Før kl. 22 en børsdag: hentingen henter ingenting før kl. 22.
            (ONSDAG_HENTET, kl(11, 12, 15), "nye kurser fra kl. 22 i kveld"),
            # Etter kl. 22, og dagen er ikke hentet.
            (ONSDAG_HENTET, kl(11, 12, 22, 30), "nye kurser kan hentes nå"),
            # Etter kl. 22, og dagen er alt hentet.
            (TORSDAG_HENTET, kl(11, 12, 23), "nye kurser fra kl. 22 i morgen"),
            # Fredag kveld, alt hentet: helgen hoppes over.
            (FREDAG_HENTET, kl(11, 13, 23), "nye kurser fra mandag kl. 22"),
            # Helg, fredag hentet.
            (FREDAG_HENTET, kl(11, 14, 10), "nye kurser fra mandag kl. 22"),
            # Helg, fredag ikke hentet: hentingen henter fredag i helgen.
            (TORSDAG_HENTET, kl(11, 14, 10), "nye kurser kan hentes nå"),
            # Etter midnatt en børsdag: før kl. 22 igjen.
            (kl(11, 9, 22, 15), kl(11, 10, 0, 30), "nye kurser fra kl. 22 i kveld"),
            # Fridag: 24.12 og 25.12 er stengt.
            (kl(12, 23, 22, 15), kl(12, 23, 23), "nye kurser fra mandag kl. 22"),
            (kl(12, 23, 22, 15), kl(12, 24, 12), "nye kurser fra mandag kl. 22"),
            # Første henting på dagtid hentet forrige børsdag (story 2.3c).
            (kl(11, 12, 14), kl(11, 12, 15), "nye kurser fra kl. 22 i kveld"),
            (kl(11, 12, 14), kl(11, 12, 22, 5), "nye kurser kan hentes nå"),
        ],
    )
    def test_teksten(self, hentet, naa, ventet):
        """Ville feilet hvis stripa sa i morgen en fredag, i kveld en dag
        hentingen alt har, glemte en fridag, eller sa «kan hentes nå» før
        kl. 22 en børsdag."""
        assert neste_henting_tekst(hentet, naa) == ventet

    def test_ukedag_og_dato_naar_det_er_mer_enn_en_uke(self, monkeypatch):
        """Ville feilet hvis en dag mer enn en uke fram bare fikk ukedagen,
        som da kunne vært to dager."""
        stengt = frozenset(boersdag.stengte_dager(2026)) | {kl(11, d, 0).date() for d in range(16, 25)}
        monkeypatch.setattr(boersdag, "stengte_dager", lambda aar: stengt)
        assert neste_henting_tekst(FREDAG_HENTET, kl(11, 13, 23)) == "nye kurser fra onsdag 25.11 kl. 22"

    def test_klokkeslettet_kommer_fra_tidsgrensen(self, monkeypatch):
        """Ville feilet hvis «kl. 22» sto fast i koden eller malen."""
        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        assert neste_henting_tekst(ONSDAG_HENTET, kl(11, 12, 15)) == "nye kurser fra kl. 21.30 i kveld"
        assert neste_henting_tekst(ONSDAG_HENTET, kl(11, 12, 21, 45)) == "nye kurser kan hentes nå"

    def test_hentingen_og_stripa_har_samme_grense(self):
        """Ville feilet hvis fetch_prices og stripa hadde hver sin grense."""
        assert fetch_prices.TIDSGRENSE is TIDSGRENSE == time(22, 0)

    def test_ingen_tekst_utenfor_kalenderen(self, monkeypatch):
        """NFR-08: ville feilet hvis stripa gjettet en dag kalenderen ikke
        dekker."""
        monkeypatch.setattr(boersdag, "dekker", lambda aar: aar == 2026)
        assert neste_henting_tekst(kl(12, 30, 22, 15), kl(12, 30, 23)) is None

    def test_dagen_er_en_dato_eller_none(self):
        assert neste_henting(ONSDAG_HENTET, kl(11, 12, 22, 30)) is None
        assert neste_henting(TORSDAG_HENTET, kl(11, 12, 23)) == kl(11, 13, 0).date()


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


class TestStripa:
    def test_den_ekte_versjonen_viser_linja(self, klient, monkeypatch):
        """Ville feilet hvis linja ikke sto bak «Oppdatert …», eller brukte
        en annen klokke enn sidene."""
        monkeypatch.setattr(app_modul, "naa", lambda: kl(11, 2, 15).astimezone(timezone.utc))
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        for adresse in ("/", "/aksje/EQNR"):
            html = klient.get(adresse).get_data(as_text=True)
            # HENTET i test_app er mandag 21.09 kl. 17.40, og klokka er mandag 02.11 kl. 15.
            assert (
                'Oppdatert mandag 21.09 kl. 17.40<span class="neste-henting"> · nye kurser fra kl. 22 i kveld</span>'
                in html
            ), adresse

    def test_demoen_viser_ikke_linja(self, tmp_path, monkeypatch):
        """Ville feilet hvis demoen, som ikke henter, sa når nye kurser kan
        hentes."""
        monkeypatch.setattr(app_modul, "naa", lambda: kl(10, 13, 12).astimezone(timezone.utc))
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        mal = tmp_path / "demo.db"
        demo.lag_demobase(mal, skriv=lambda _: None)
        shutil.copy(mal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        klient = app_modul.app.test_client()
        for adresse in ("/", "/aksje/BRFE", "/boersometer", "/min-liste"):
            html = klient.get(adresse).get_data(as_text=True)
            assert "Oppdatert " in html, adresse
            assert 'class="neste-henting"' not in html and "· nye kurser" not in html, adresse


class TestHjelpen:
    def test_hjelpen_og_docs_sier_det(self):
        """Regel 19: ville feilet hvis hjelpen ved «Oppdatert» eller
        docs/hjelp.md ikke sa at linja ikke lover en henting, og at demoen
        ikke viser den."""
        tekst = hjelpetekster()["neste_henting"].tekst
        assert f"fra kl. {TIDSGRENSE.hour} en børsdag" in tekst
        assert (
            "men ikke om de blir hentet: det avhenger av at appen eller kveldsjobben kjører" in tekst
            and "Demoen henter ikke" in tekst
        )
        hjelp = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "Det sier ikke at en henting kommer" in hjelp and "Demoen henter ikke og viser det ikke." in hjelp
