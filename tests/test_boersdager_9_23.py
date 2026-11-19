"""Story 9.23: «51 børsdager» i kommentaren øverst i src/fetch_prices.py og i
docstringen i tests/test_fetch_prices.py, og bare der.

Spørsmål 1 fra 9.22 (svaret 19.11 kl. 09:59) og instruksjonen 19.11 kl. 10:40 i
docs/ai-prompts/2026-11-19.md. Begge stedene er skrevet uten norske bokstaver
(«foer», «aar»), så ordet står som «boersdager», som i src/boersdag.py.
"""

import ast
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent


def _docstring_i_testen() -> str:
    tre = ast.parse((ROT / "tests" / "test_fetch_prices.py").read_text(encoding="utf-8"))
    for node in ast.walk(tre):
        if isinstance(node, ast.FunctionDef) and node.name == "test_intervallet_gir_rom_for_ma50":
            return ast.get_docstring(node)
    raise AssertionError("test_intervallet_gir_rom_for_ma50 finnes ikke")


class TestBoersdagerIKoden:
    def test_kommentaren_oeverst_i_fetch_prices(self):
        """Ville feilet med «51 handelsdager» i modul-docstringen."""
        kilde = (ROT / "src" / "fetch_prices.py").read_text(encoding="utf-8")
        doc = ast.get_docstring(ast.parse(kilde))
        assert "51 handelsdager" not in doc
        assert "MA50 trenger 51 boersdager foer signalet" in " ".join(doc.split())

    def test_docstringen_i_test_fetch_prices(self):
        """Ville feilet med «51 handelsdager er minimum.»."""
        doc = _docstring_i_testen()
        assert doc.startswith("51 boersdager er minimum."), doc

    def test_51_handelsdager_staar_ikke_lenger_i_koden(self):
        """Bare de to stedene hadde «51 handelsdager» i src/ og tests/. Testene
        som sjekker at det er borte, nevner det med vilje."""
        sjekkene = {"test_boersdager_9_22.py", "test_boersdager_9_23.py"}
        treff = [
            p.relative_to(ROT).as_posix()
            for mappe in ("src", "tests")
            for p in (ROT / mappe).rglob("*.py")
            if p.name not in sjekkene and "51 handelsdager" in p.read_text(encoding="utf-8")
        ]
        assert treff == []

    def test_handelsdag_som_er_brukt_med_vilje_staar(self):
        """Instruksjonen: navnene, kolonnen i basen og regelen om halve
        handelsdager endres ikke."""
        fp = (ROT / "src" / "fetch_prices.py").read_text(encoding="utf-8")
        assert "MINST_HANDELSDAGER = 51" in fp
        sql = (ROT / "src" / "migrasjoner" / "0008_omsetning.sql").read_text(encoding="utf-8")
        assert "handelsdager INTEGER NOT NULL" in sql
        boersdag = (ROT / "src" / "boersdag.py").read_text(encoding="utf-8")
        assert "Halve handelsdager er boersdager" in boersdag
