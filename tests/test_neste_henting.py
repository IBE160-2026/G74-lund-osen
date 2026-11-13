"""Story 8.19: neste henting i stripa øverst (U60, tillegg 1 til 10.11,
gruppens svar 12.11 kl. 17:01).

Bare den ekte versjonen viser når nye kurser tidligst kan hentes, regnet med
børsdagskontrollen (2.3) og TIDSGRENSE. Den sier aldri at en henting kommer.
Fra spørsmål 10 (svaret 12.11 kl. 20:42) regnes linja av den siste kursdagen
i basen, den eldste blant aksjene i lista, ikke av tidspunktet i «Oppdatert».
Spørsmål 8 og 9 (tillegg 2 og 3) er omvisningen. Klokka står fast i hver
test. Spesifikasjonen:
_bmad-output/implementation-artifacts/spec-8-19-neste-henting-i-stripa.md.
"""

import dataclasses
import html as html_modul
import json
import re
import shutil
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import app as app_modul
import boersdag
import demo
import fetch_prices
import hjelpetekster as ht
from boersdag import TIDSGRENSE, neste_henting
from hjelpetekster import hjelpetekster
from kursdata import Kursrad
from lagring_sqlite import demo_sti
from markedsoversikt import neste_henting_tekst
from test_app import monter, serie, skriv_serie, snapshot

ROT = Path(__file__).resolve().parents[1]
OSLO = ZoneInfo("Europe/Oslo")


def kl(maaned: int, dag: int, time_: int, minutt: int = 0) -> datetime:
    return datetime(2026, maaned, dag, time_, minutt, tzinfo=OSLO)


def d(maaned: int, dag: int) -> date:
    return date(2026, maaned, dag)


# Torsdag 12.11.2026 er børsdag, lørdag 14.11 ikke. 24.12 og 25.12 er stengt.
ONSDAG, TORSDAG, FREDAG = d(11, 11), d(11, 12), d(11, 13)


class TestTilfellene:
    @pytest.mark.parametrize(
        ("kursdag", "naa", "ventet"),
        [
            # Før kl. 22 en børsdag: hentingen henter ingenting før kl. 22.
            (ONSDAG, kl(11, 12, 15), "nye kurser fra kl. 22 i kveld"),
            # Etter kl. 22, og dagen er ikke i basen.
            (ONSDAG, kl(11, 12, 22, 30), "nye kurser kan hentes nå"),
            # Etter kl. 22, og dagen er i basen.
            (TORSDAG, kl(11, 12, 23), "nye kurser fra kl. 22 i morgen"),
            # Fredag kveld, fredag i basen: helgen hoppes over.
            (FREDAG, kl(11, 13, 23), "nye kurser fra mandag kl. 22"),
            # Helg, fredag i basen.
            (FREDAG, kl(11, 14, 10), "nye kurser fra mandag kl. 22"),
            # Helg, fredag mangler: hentingen henter fredag i helgen.
            (TORSDAG, kl(11, 14, 10), "nye kurser kan hentes nå"),
            # Etter midnatt en børsdag: før kl. 22 igjen.
            (d(11, 9), kl(11, 10, 0, 30), "nye kurser fra kl. 22 i kveld"),
            # Fridag: 24.12 og 25.12 er stengt.
            (d(12, 23), kl(12, 23, 23), "nye kurser fra mandag kl. 22"),
            (d(12, 23), kl(12, 24, 12), "nye kurser fra mandag kl. 22"),
            # ECH1: en henting med --uten-tidskontroll før kl. 22 fikk dagens
            # kurs. Etter kl. 22 er dagen alt i basen.
            (TORSDAG, kl(11, 12, 22, 5), "nye kurser fra kl. 22 i morgen"),
            # ECH2: dagen mangler i basen selv om hentingen gikk etter kl. 22.
            (ONSDAG, kl(11, 12, 23, 30), "nye kurser kan hentes nå"),
        ],
    )
    def test_teksten(self, kursdag, naa, ventet):
        """Ville feilet hvis stripa sa i morgen en fredag, i kveld en dag
        basen alt har, glemte en fridag, sa «kan hentes nå» før kl. 22 en
        børsdag, eller regnet av tidspunktet for hentingen i stedet for
        kursdagen (ECH1, ECH2)."""
        assert neste_henting_tekst(kursdag, naa) == ventet

    def test_ukedag_og_dato_naar_det_er_mer_enn_en_uke(self, monkeypatch):
        """Ville feilet hvis en dag mer enn en uke fram bare fikk ukedagen,
        som da kunne vært to dager."""
        stengt = frozenset(boersdag.stengte_dager(2026)) | {d(11, n) for n in range(16, 25)}
        monkeypatch.setattr(boersdag, "stengte_dager", lambda aar: stengt)
        assert neste_henting_tekst(FREDAG, kl(11, 13, 23)) == "nye kurser fra onsdag 25.11 kl. 22"

    def test_klokkeslettet_kommer_fra_tidsgrensen(self, monkeypatch):
        """Ville feilet hvis «kl. 22» sto fast i koden eller malen."""
        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        assert neste_henting_tekst(ONSDAG, kl(11, 12, 15)) == "nye kurser fra kl. 21.30 i kveld"
        # Gjennomgangen (ECH7): hjelpen viser grensen på samme måte.
        assert "fra kl. 21.30 en børsdag" in hjelpetekster()["neste_henting"].tekst
        assert neste_henting_tekst(ONSDAG, kl(11, 12, 21, 45)) == "nye kurser kan hentes nå"

    def test_hentingen_og_stripa_har_samme_grense(self):
        """Ville feilet hvis fetch_prices og stripa hadde hver sin grense."""
        assert fetch_prices.TIDSGRENSE is TIDSGRENSE == time(22, 0)

    def test_ingen_tekst_utenfor_kalenderen(self, monkeypatch):
        """NFR-08: ville feilet hvis stripa gjettet en dag kalenderen ikke
        dekker."""
        monkeypatch.setattr(boersdag, "dekker", lambda aar: aar == 2026)
        assert neste_henting_tekst(d(12, 30), kl(12, 30, 23)) is None

    @pytest.mark.parametrize("kursdag", [kl(11, 11, 22, 15), datetime(2026, 11, 11), "2026-11-11", None])
    def test_noe_annet_enn_en_dato_gir_ingen_tekst(self, kursdag):
        """Gjennomgangen (ECH4): ville feilet hvis et tidspunkt eller en
        tekst ga en linje, før eller etter kl. 22."""
        for naa in (kl(11, 12, 15), kl(11, 12, 23)):
            assert neste_henting_tekst(kursdag, naa) is None

    def test_dagen_er_en_dato_eller_none(self):
        assert neste_henting(ONSDAG, kl(11, 12, 22, 30)) is None
        assert neste_henting(TORSDAG, kl(11, 12, 23)) == FREDAG


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _serie_til(siste: date) -> list[Kursrad]:
    """61 dager med kurser, den siste på siste."""
    rader = serie([100.0] * 61)
    return [dataclasses.replace(r, dato=siste - timedelta(days=60 - i)) for i, r in enumerate(rader)]


def _linja(html: str) -> str | None:
    m = re.search(r'<span class="neste-henting" id="neste-henting"> · ([^<]*)</span>', html)
    return m.group(1) if m else None


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
                'Oppdatert mandag 21.09 kl. 17.40<span class="neste-henting" id="neste-henting"> · '
                "nye kurser fra kl. 22 i kveld</span>" in html
            ), adresse

    def test_ech1_dagens_kurs_hentet_foer_kl_22(self, klient, monkeypatch):
        """ECH1, spørsmål 10: ville feilet hvis stripa regnet av tidspunktet.
        En henting kl. 14 med --uten-tidskontroll fikk torsdagens kurs, så
        etter kl. 22 har basen dagen, og neste er i morgen, ikke «nå»."""
        monkeypatch.setattr(app_modul, "naa", lambda: kl(11, 12, 23).astimezone(timezone.utc))
        for symbol in ("EQNR", "DNB"):
            skriv_serie(symbol, _serie_til(TORSDAG), kl(11, 12, 14))
        for adresse in ("/", "/aksje/EQNR"):
            assert _linja(klient.get(adresse).get_data(as_text=True)) == "nye kurser fra kl. 22 i morgen", adresse

    def test_ech2_en_aksje_mangler_dagen(self, klient, monkeypatch):
        """ECH2, ECH6 og spørsmål 10: ville feilet hvis stripa sa «i morgen»
        når én aksje i lista ble hentet etter kl. 22 uten raden for dagen,
        eller hvis aksjesiden for en aksje som har dagen, brukte sin egen dag
        og ikke den samme som oversikten."""
        monkeypatch.setattr(app_modul, "naa", lambda: kl(11, 12, 23, 30).astimezone(timezone.utc))
        skriv_serie("EQNR", _serie_til(TORSDAG), kl(11, 12, 22, 15))
        skriv_serie("DNB", _serie_til(ONSDAG), kl(11, 12, 22, 15))
        for adresse in ("/", "/aksje/EQNR", "/aksje/DNB", "/boersometer", "/min-liste"):
            assert _linja(klient.get(adresse).get_data(as_text=True)) == "nye kurser kan hentes nå", adresse

    def test_demoen_viser_ikke_linja(self, tmp_path, monkeypatch):
        """Ville feilet hvis demoen, som ikke henter, sa når nye kurser kan
        hentes."""
        klient = _demoklient(tmp_path, monkeypatch)
        for adresse in ("/", "/aksje/BRFE", "/boersometer", "/min-liste"):
            html = klient.get(adresse).get_data(as_text=True)
            assert "Oppdatert " in html, adresse
            assert 'class="neste-henting"' not in html and "· nye kurser" not in html, adresse


def _demoklient(tmp_path, monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: kl(10, 13, 12).astimezone(timezone.utc))
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    mal = tmp_path / "demo.db"
    demo.lag_demobase(mal, skriv=lambda _: None)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    return app_modul.app.test_client()


class TestHjelpen:
    def test_hjelpen_og_docs_sier_det(self):
        """Regel 19: ville feilet hvis hjelpen ved «Oppdatert» eller
        docs/hjelp.md ikke sa at linja ikke lover en henting, og at demoen
        ikke viser den."""
        tekst = hjelpetekster()["neste_henting"].tekst
        assert f"fra kl. {TIDSGRENSE.hour} en børsdag" in tekst  # kl. 22, uten minutter
        assert (
            "men ikke om de blir hentet: det avhenger av at appen eller kveldsjobben kjører" in tekst
            and "Demoen henter ikke" in tekst
        )
        hjelp = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "Det sier ikke at en henting kommer" in hjelp and "Demoen henter ikke og viser det ikke." in hjelp


# --- Spørsmål 8 (tillegg 2): omvisningen forklarer linja ---------------------


def _rundturen(side: str) -> list[dict]:
    treff = re.search(r'<button type="button" class="sideknapp vis-meg-rundt" data-steg="([^"]*)" hidden>', side)
    assert treff, "ingen «Vis meg rundt»"
    return json.loads(html_modul.unescape(treff.group(1)))


def _omvisningen(side: str) -> list[dict]:
    treff = re.search(r'<div id="omvisning" hidden data-side="[^"]*" data-steg="([^"]*)"></div>', side)
    assert treff, "ingen omvisning"
    return json.loads(html_modul.unescape(treff.group(1)))


def _dagen(steg: list[dict]) -> dict:
    return next(s for s in steg if s["tittel"] == "Dagen og perioden" and s.get("side", "oversikt") == "oversikt")


class TestOmvisningenOmLinja:
    def test_den_ekte_versjonen_peker_paa_linja(self, klient, monkeypatch):
        """Ville feilet hvis steget om dagen ikke sa hva linja bak
        «Oppdatert» betyr, eller ikke merket linja, i «Vis meg rundt» og i
        omvisningen."""
        monkeypatch.setattr(app_modul, "naa", lambda: kl(11, 2, 15).astimezone(timezone.utc))
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        html = klient.get("/").get_data(as_text=True)
        for steg in (_dagen(_rundturen(html)), _dagen(_omvisningen(html))):
            assert steg["tekst"].endswith(ht.NESTE_HENTING_STEGET), steg
            assert steg["anker"] == "velg-dag" and steg["ogsaa"] == ht.NESTE_HENTING_ANKER
        # Linja steget merker, finnes én gang.
        assert len(re.findall(rf'(?<![\w-])id="{ht.NESTE_HENTING_ANKER}"', html)) == 1

    def test_demoen_sier_at_den_ikke_henter(self, tmp_path, monkeypatch):
        """Ville feilet hvis demoen sa at linja står øverst, pekte på en linje
        den ikke har, eller ikke sa at den ikke henter."""
        html = _demoklient(tmp_path, monkeypatch).get("/").get_data(as_text=True)
        for steg in (_dagen(_rundturen(html)), _dagen(_omvisningen(html))):
            assert steg["tekst"].endswith(ht.NESTE_HENTING_STEGET_DEMO), steg
            assert "demoen henter ikke" in steg["tekst"] and "Den ekte versjonen viser" in steg["tekst"]
            assert steg["ogsaa"] == ""

    def test_hjelpen_sier_det_samme_i_begge_versjonene(self, klient, tmp_path, monkeypatch):
        """Ville feilet hvis vinduet ved «Oppdatert» hadde en annen tekst om
        linja i demoen enn i den ekte versjonen."""
        tekst = html_modul.escape(hjelpetekster()["neste_henting"].tekst, quote=False)
        monkeypatch.setattr(app_modul, "naa", lambda: kl(11, 2, 15).astimezone(timezone.utc))
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        assert tekst in klient.get("/").get_data(as_text=True)
        assert tekst in _demoklient(tmp_path, monkeypatch).get("/").get_data(as_text=True)

    @pytest.mark.parametrize("demo_", [False, True])
    def test_ingen_side_har_mer_enn_sju_steg(self, demo_):
        """Ville feilet hvis setningen om linja ble et eget steg, så
        oversikten fikk åtte, eller et steg fikk over 50 ord."""
        assert ht.MAKS_STEG == 7
        for side, steg in ht.rundturer(demo=demo_).items():
            assert len(steg) <= 7, side
            for s in steg:
                assert len(re.findall(r"\w+", f"{s.tittel} {s.tekst}")) <= 50, (side, s.tittel)

    def test_bare_steget_om_dagen_er_ulikt(self):
        """Ville feilet hvis demoen og den ekte versjonen hadde ulik omvisning
        i noe annet enn steget om dagen på oversikten og steget for «Mine
        notater», som har linja om demoen fra 8.27."""
        ekte, demoen = ht.omvisningen(), ht.omvisningen(demo=True)
        ulike = [(e["side"], e["tittel"]) for e, m in zip(ekte, demoen, strict=True) if e != m]
        assert ulike == [("oversikt", "Dagen og perioden"), ("min_liste", "Mine notater")]

    def test_skriptet_merker_linja_og_fjerner_merket(self):
        """Ville feilet hvis hjelp.js ikke merket den andre delen, eller lot
        merket stå etter steget."""
        skriptet = (ROT / "src" / "static" / "hjelp.js").read_text(encoding="utf-8")
        assert "document.getElementById(s.ogsaa)" in skriptet
        assert 'ogsaaMerket.classList.remove("omvisning-merket")' in skriptet
        assert "ogsaa: s.ogsaa" in skriptet
        # Linja står over dagvalget, så det rulles til den, og begge vises.
        assert 'oeverst.scrollIntoView({ block: "start" })' in skriptet


# --- Spørsmål 9 (tillegg 3): fire ting i omvisningen -------------------------


class TestOmvisningenTillegg3:
    def _alle(self) -> dict[str, list[str]]:
        alle: dict[str, list[str]] = {}
        for steg in ht.rundturer().values():
            for s in steg:
                alle.setdefault(s.tittel, []).append(s.tekst)
        return alle

    def test_signalstyrken_nevner_de_tre_sjekkene(self):
        """Ville feilet hvis «Signalstyrken» ikke nevnte trend, bevegelse og
        interesse (T, B og I)."""
        for tekst in self._alle()["Signalstyrken"]:
            for ord_ in ("trend", "bevegelse", "interesse", "(T, B og I)", "+1, 0 eller -1"):
                assert ord_ in tekst, ord_

    def test_retningen_har_blandet_og_ikke_et_raad(self):
        """Ville feilet hvis «Blandet» sto under «Signalstyrken» og ikke
        under «Retningen», eller «Retningen» ikke sa at den ikke er et råd
        (NFR-06)."""
        alle = self._alle()
        for tekst in alle["Retningen"]:
            assert "Blandet" in tekst and "ikke et råd" in tekst
        for tekst in alle["Signalstyrken"]:
            assert "Blandet" not in tekst

    def test_de_to_ki_stegene_har_ulik_tekst(self):
        """Ville feilet hvis «Signalet forklart» hadde den samme teksten som
        «Børsdagen kort fortalt»."""
        alle = self._alle()
        forklart, kort = alle["Signalet forklart"][0], alle["Børsdagen kort fortalt"][0]
        assert forklart != kort
        assert forklart.startswith("Først appens egne setninger")
        assert "«Laget av KI»" in forklart and "prikket strek" in forklart

    def test_smaatingene(self):
        """Ville feilet hvis «Hovedindeksen» eller «Dag for dag» manglet
        ordene fra tillegget."""
        alle = self._alle()
        assert "den stiplede linja er hovedindeksen" in alle["Hovedindeksen"][0]
        assert "lagret hver børsdag og aldri regnet på nytt" in alle["Dag for dag"][0]
