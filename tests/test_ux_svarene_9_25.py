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
