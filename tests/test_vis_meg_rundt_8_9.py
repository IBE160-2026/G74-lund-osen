"""Story 8.9: «Vis meg rundt» på hver side (FR-109).

Spesifikasjonen er spec-8-9-vis-meg-rundt.md. Hver test lager sin egen base
under tmp_path (regel 22), og ingen test gjør nettkall (AD-8). Kursene er
oppdiktet (regel 16).
"""

import re
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

import app as app_modul
import fetch_prices as fp
import hjelpetekster as ht
import lagring_sqlite
from signalberegning import STANDARD
from test_fetch_prices import NOEKKEL, nok_kvote, serie_til

SIDENE = {
    "oversikt": "/",
    "min_liste": "/min-liste",
    "boersometer": "/boersometer",
    "aksje": "/aksje/EQNR",
    "innstillinger": "/innstillinger",
    "folg": "/folg",
}


def _hent(ticker, *_):
    return serie_til(date(2026, 9, 22), dager=80)


@pytest.fixture
def klient(tmp_path, monkeypatch):
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    fp.kjoer(
        raa,
        base,
        datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc),
        NOEKKEL,
        _hent,
        lambda _: None,
        les_kvote=nok_kvote,
    )
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    k = app_modul.app.test_client()
    # Min liste med én aksje, så lista har noe å vise.
    svar = k.post("/min-liste/merk", data={"symbol": "EQNR", "til": "merk", "tilbake": "/"})
    assert svar.status_code in (302, 303)
    return k


def _rundturen(side: str) -> str:
    treff = re.search(r'<details class="rundtur">.*?</details>', side, re.S)
    assert treff, "ingen «Vis meg rundt»"
    return treff.group(0)


class TestHverSide:
    @pytest.mark.parametrize("side", sorted(SIDENE))
    def test_knappen_og_stegene_peker_paa_noe_som_finnes(self, klient, side):
        """Ville feilet hvis en side manglet «Vis meg rundt», eller et steg
        pekte på noe siden ikke har, som børsometeret før 8.6 var bygget."""
        html = klient.get(SIDENE[side]).data.decode("utf-8")
        rundtur = _rundturen(html)
        assert "<summary>Vis meg rundt</summary>" in rundtur
        ankrene = re.findall(r'<a href="#([^"]+)">', rundtur)
        assert ankrene == [s.anker for s in ht.rundturer()[side]]
        for anker in ankrene:
            # Gjennomgangen (BH3): en hel id, ikke data-id, og bare én.
            assert len(re.findall(rf'(?<![\w-])id="{re.escape(anker)}"', html)) == 1, (side, anker)

    def test_borte_naar_hjelpen_er_av(self, klient):
        """Ville feilet hvis «Vis meg rundt» sto når «Vis hjelp» er slått av
        i Innstillinger, som «?» ikke gjør."""
        svar = klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        assert svar.status_code in (302, 303)
        for adresse in SIDENE.values():
            assert 'class="rundtur"' not in klient.get(adresse).data.decode("utf-8"), adresse

    def test_ikke_der_stegene_ikke_passer(self, klient, monkeypatch):
        """Gjennomgangen (ECH1, ECH4, VG1): ville feilet hvis knappen sto på
        «Følg en aksje» når lista er full eller en aksje skal byttes, så
        «Søk» pekte på et søkefelt som ikke finnes, eller i Min liste uten
        merkede aksjer."""
        import valg

        assert 'class="rundtur"' not in klient.get("/folg?bytt=EQNR").data.decode("utf-8")
        monkeypatch.setattr(valg, "TAK", 0)
        full = klient.get("/folg").data.decode("utf-8")
        assert 'id="q"' not in full and 'class="rundtur"' not in full
        klient.post("/min-liste/merk", data={"symbol": "EQNR", "til": "fjern", "tilbake": "/"})
        assert 'class="rundtur"' not in klient.get("/min-liste").data.decode("utf-8")

    def test_alle_sidene_har_steg(self):
        """Ville feilet hvis en side i lista ikke hadde steg i hjelpetekster.py."""
        assert set(ht.rundturer()) == set(SIDENE) | {"aksje_uten_sjekker"}

    def test_aksjesiden_uten_sjekker(self, klient):
        """Ville feilet hvis «Vis meg rundt» forklarte sjekkene på en dag
        siden ikke har dem (en dag uten vurdering), eller et steg pekte på
        noe siden ikke har."""
        html = klient.get("/aksje/EQNR?dag=2026-09-21").data.decode("utf-8")
        assert "Hvorfor signalet ble ukjent" in html
        ankrene = re.findall(r'<a href="#([^"]+)">', _rundturen(html))
        assert ankrene == [s.anker for s in ht.rundturer()["aksje_uten_sjekker"]]
        assert "sjekkene" not in ankrene
        for anker in ankrene:
            assert len(re.findall(rf'(?<![\w-])id="{re.escape(anker)}"', html)) == 1, anker


class TestTekstene:
    def test_hoeyst_sju_steg(self):
        """Ville feilet hvis en side fikk flere enn 7 steg (endringsforslaget
        13.10, punkt 4.1)."""
        assert all(1 <= len(steg) <= ht.MAKS_STEG == 7 for steg in ht.rundturer().values())

    def test_tallene_kommer_fra_parametre(self):
        """Ville feilet hvis et tall i stegene var skrevet inn for hånd og ikke
        hentet fra Parametre."""
        endret = replace(STANDARD, ma_vindu=37, volatilitet_vindu=23, volum_vindu=17, terskel=3, volumfaktor=2.5)
        tekst = " ".join(s.tekst for steg in ht.rundturer(endret).values() for s in steg)
        for tall in ("37-dagers", "23 dager", "17 dager", "signalstyrke 3 eller mer"):
            assert tall in tekst, tall
        vanlig = " ".join(s.tekst for steg in ht.rundturer().values() for s in steg)
        assert "37-dagers" not in vanlig
        # Hvert steg med tall for seg, så ett steg med tallet ikke dekker et annet.
        aksje = {s.tittel: s.tekst for s in ht.rundturer(endret)["aksje"]}
        assert "37-dagers" in aksje["Tallene bak"] and "37-dagers" in aksje["Kursgrafen"]
        assert "23 dager" in aksje["Tallene bak"] and "17 dager" in aksje["Tallene bak"]
        # Gjennomgangen (VG2, BH8): også volumfaktoren.
        assert "2,5 ×" in aksje["Tallene bak"] and "1,5 ×" not in aksje["Tallene bak"]

    def test_tekstene_fra_tavla(self):
        """Gjennomgangen (ECH5): ville feilet hvis stegene om signalstyrken,
        retningen og sjekkene ikke var tekstene fra tavla, ordrett fra punkt
        4.2 i endringsforslaget 13.10 (tillegget i epics.md 13.10)."""
        from pathlib import Path

        forslaget = (Path(__file__).resolve().parent.parent / ht.ENDRINGSFORSLAGET_13_10).read_text(encoding="utf-8")
        alle = {s.tittel: s.tekst for steg in ht.rundturer().values() for s in steg}
        assert alle["Signalstyrken"] == ht.TAVLA_STYRKEN and f"«{ht.TAVLA_STYRKEN}»" in forslaget
        assert alle["Retningen"] == ht.TAVLA_RETNING and f"Retning: «{ht.TAVLA_RETNING} " in forslaget
        assert alle["Sjekkene"] == ht.TAVLA_SJEKKENE and f"«{ht.TAVLA_SJEKKENE}»" in forslaget

    def test_ingen_ki_og_ingen_nett(self):
        """Ville feilet hvis hjelpetekster.py, der stegene står, importerte
        KI-modulene eller noe som gjør nettkall."""
        kilde = open(ht.__file__, encoding="utf-8").read()
        for modul in ("ki_", "requests", "ollama", "fetch_prices"):
            assert f"import {modul}" not in kilde and f"from {modul}" not in kilde, modul
