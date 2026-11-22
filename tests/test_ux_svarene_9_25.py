"""Story 9.25: svarene på E1, E2, E4, E5 og E6 i UX-dokumentene.

Spesifikasjonen er spec-9-25-svarene-paa-ux-spoersmaalene.md, og svarene er
gruppens 22.11 kl. 18:23. Demobasen ligger i tmp_path (conftest.py, regel 22),
og ingen test gjør nettkall (AD-8).
"""

import re
from datetime import datetime, time, timezone
from pathlib import Path

import pytest

import app as app_modul
import boersdag
import demo
import lagring_sqlite

ROT = Path(__file__).resolve().parent.parent
MALENE = ROT / "src" / "templates"
PRD = ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20"


def _uten_kommentarer(mal: str) -> str:
    """Teksten i en mal uten Jinja-kommentarene, som aldri vises."""
    return re.sub(r"\{#.*?#\}", "", mal, flags=re.S)


def _synlig(side: str) -> str:
    """Teksten på siden uten tagger og skript, med mellomrom samlet."""
    side = re.sub(r"<(script|style)\b.*?</\1>", "", side, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", side))


@pytest.fixture
def demoen(monkeypatch):
    """Demoen slik den kjører, med demobasen ved siden av testbasen."""
    sti = lagring_sqlite.demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    demo.lag_demobase(sti, skriv=lambda _: None)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


class TestE1MinListe:
    """E1: der Min liste sa «lista» om aksjene med stjerne, står «Min liste»,
    som ordlista skiller (prd.md §1). «Lista» er aksjene appen henter."""

    def test_malen_sier_min_liste_om_stjernen(self):
        """Ville feilet hvis innledningen, teksten for en tom Min liste eller
        teksten for «Min liste» på oversikten sa «lista» om stjernen."""
        tekst = re.sub(r"\s+", " ", _uten_kommentarer((MALENE / "index.html").read_text(encoding="utf-8")))
        for gammel in ("legger aksjen i lista", "for å legge det i lista", "Lista lagres på denne maskinen"):
            assert gammel not in tekst, gammel
        assert tekst.count("legger aksjen i Min liste") == 2
        assert "for å legge det i Min liste." in tekst
        assert "Min liste lagres på denne maskinen" in tekst

    def test_min_liste_i_demoen(self, demoen):
        """Ville feilet hvis innledningen i Min liste i demoen sa «lista»."""
        side = _synlig(demoen.get("/min-liste").data.decode("utf-8"))
        assert "Stjernen foran et selskap legger aksjen i Min liste, og et nytt trykk tar den ut." in side
        assert "Min liste lagres på denne maskinen og koster ingen API-kall." in side


class TestE2Klokkeslettet:
    """E2: «kl. 22» i malene kommer fra TIDSGRENSE, som i stripa
    (grensen_som_tekst i markedsoversikt.py)."""

    def test_ingen_mal_har_klokkeslettet_skrevet_inn(self):
        """Ville feilet hvis en mal hadde «kl. 22» skrevet inn i teksten som
        vises. Kommentarene i malene teller ikke."""
        funnet = [
            mal.name
            for mal in sorted(MALENE.glob("*.html"))
            if "kl. 22" in _uten_kommentarer(mal.read_text(encoding="utf-8"))
        ]
        assert funnet == []

    @pytest.mark.parametrize("adresse", ["/", "/min-liste", "/folg?kode=HAVR", "/ferdig-liste?bransje=Kraft"])
    def test_sidene_bruker_tidsgrensen(self, demoen, monkeypatch, adresse):
        """Ville feilet hvis en side i demoen viste «etter kl. 22» når
        TIDSGRENSE er en annen, eller ikke viste grensen."""
        monkeypatch.setattr(boersdag, "TIDSGRENSE", time(21, 30))
        svar = demoen.get(adresse)
        assert svar.status_code == 200
        side = _synlig(svar.data.decode("utf-8"))
        assert "etter kl. 22" not in side
        assert "etter kl. 21.30" in side

    def test_grensen_i_hele_timer_som_foer(self, demoen):
        """Med kl. 22:00 står «kl. 22», som før (ingen endring på sidene)."""
        side = _synlig(demoen.get("/min-liste").data.decode("utf-8"))
        assert "etter kl. 22." in side and "kl. 22.00" not in side


class TestE4Modellnavnet:
    """E4: oversikten skriver modellnavnet i samme form som aksjesiden,
    «Modell: {modell}, {tjeneste}» (FR-602)."""

    def test_dagsvisningen_har_samme_form_som_aksjesiden(self):
        """Ville feilet hvis tjenesten sto i parentes på oversikten."""
        from types import SimpleNamespace

        import ki_visning

        rad = SimpleNamespace(modell="gemma4:e4b", tjeneste="lokal")
        assert ki_visning._modellnavnet(rad) == "gemma4:e4b, lokal"

    def test_oversikten_i_demoen(self, demoen):
        """Ville feilet hvis oversikten sa «Skrevet av … (lokal) da kursene
        ble hentet.» i stedet for «Modell: …, lokal»."""
        side = _synlig(demoen.get("/").data.decode("utf-8"))
        assert "Modell: gemma4:e4b, lokal" in side
        assert "Skrevet av gemma4" not in side
        assert "(lokal)" not in side


class TestE5Ticker:
    """E5: «ticker» gjelder, som i søkefeltet og FR-415."""

    def test_steget_ved_soekefeltet_sier_ticker(self):
        """Ville feilet hvis steget sa «symbolet»."""
        from hjelpetekster import rundturer

        (steget,) = [s for s in rundturer()["folg"] if s.anker == "q"]
        assert "ticker" in steget.tekst and "symbol" not in steget.tekst

    def test_ordlista_har_ordet(self):
        """Ville feilet hvis ordlista i PRD-en manglet «Ticker», eller
        endringsloggen ikke hadde en linje om det (regel 19)."""
        prd = (PRD / "prd.md").read_text(encoding="utf-8")
        ordlista = prd.split("| Ord | Betyr i appen |", 1)[1].split("\n\n", 1)[0]
        assert re.search(r"^\| \*\*Ticker\*\* \(symbol\) \|", ordlista, flags=re.M)
        logg = (PRD / "prd-endringslogg.md").read_text(encoding="utf-8")
        assert "«Ticker»" in logg.split("Endringer etter 12.11", 1)[1]
