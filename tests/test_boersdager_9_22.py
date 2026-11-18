"""Story 9.22: «51 børsdager» i FR-101 og i kilden i hjelpetekstene.

Spørsmål 7 i 9.20 og instruksjonen 18.11 kl. 21:41 i docs/ai-prompts/2026-11-18.md.
"""

from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
PRD = ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20"


class TestBoersdager:
    def test_fr_101_og_kilden_sier_boersdager(self):
        """Spørsmål 7 i 9.20 (svaret 18.11 kl. 11:49). Ville feilet hvis FR-101
        sa «51 handelsdager», hvis kilden i hjelpetekstene ikke viste til
        setningen i FR-101, eller hvis endringsloggen ikke sa det."""
        prd = (PRD / "prd.md").read_text(encoding="utf-8")
        assert "51 handelsdager" not in prd
        kilde = "Signalet krever 51 børsdager"
        assert "**Aksjer uten gyldig signal vises likevel.** Signalet krever 51 børsdager\nfordi MA50" in prd
        hjelp = (ROT / "src" / "hjelpetekster.py").read_text(encoding="utf-8")
        assert f'(PRD, "{kilde}"),' in hjelp and "51 handelsdager" not in hjelp
        assert kilde in prd.replace("\n", " ")
        logg = (PRD / "prd-endringslogg.md").read_text(encoding="utf-8")
        assert "*Endret 2026-11-18 (story 9.22" in logg and "«Signalet krever 51 børsdager»" in logg
