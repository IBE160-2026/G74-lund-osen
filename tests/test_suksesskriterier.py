"""§10 i docs/kvalitetssikring.md: suksesskriteriene i briefen og testene.

Faglaerers tilbakemelding 06.10: testene skal kunne spores tilbake til
briefen. Tabellen i §10 viser til tester med fil, klasse og navn. Disse
testene holder tabellen sann: hver test den viser til, finnes, og alle fire
kriteriene i briefen v8 staar der.
"""

import ast
import re
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
KVALITET = ROT / "docs" / "kvalitetssikring.md"
BRIEF = ROT / "_bmad-output" / "planning-artifacts" / "product-brief.md"


def _seksjon_10() -> str:
    tekst = KVALITET.read_text(encoding="utf-8")
    return tekst.split("## 10. Suksesskriteriene og testene", 1)[1].split("\n## ", 1)[0]


def _testene_i_tabellen() -> list[str]:
    return re.findall(r"`(tests/[\w/]+\.py::[\w:]+)`", _seksjon_10())


def _navnene_i_fila(fil: Path) -> set[str]:
    """«Klasse::test» og «test» for hver testfunksjon i fila."""
    tre = ast.parse(fil.read_text(encoding="utf-8"))
    navn = set()
    for node in tre.body:
        if isinstance(node, ast.FunctionDef):
            navn.add(node.name)
        elif isinstance(node, ast.ClassDef):
            for del_ in node.body:
                if isinstance(del_, ast.FunctionDef):
                    navn.add(f"{node.name}::{del_.name}")
    return navn


def test_tabellen_viser_til_tester():
    """Ville feilet hvis tabellen ikke viste til noen test, for eksempel
    fordi formen paa henvisningene ble endret og regexen ikke fant dem."""
    assert len(_testene_i_tabellen()) >= 10


def test_hver_test_tabellen_viser_til_finnes():
    """Ville feilet hvis en test i tabellen fikk nytt navn eller ble
    slettet uten at tabellen ble rettet."""
    for henvisning in _testene_i_tabellen():
        fil, navn = henvisning.split("::", 1)
        sti = ROT / fil
        assert sti.exists(), henvisning
        assert navn in _navnene_i_fila(sti), henvisning


def test_alle_kriteriene_i_briefen_staar_i_tabellen():
    """Kriteriene leses fra tabellen under «Success Criteria» i briefen.
    Ville feilet hvis et kriterium manglet i §10."""
    brief = BRIEF.read_text(encoding="utf-8")
    del_ = brief.split("## Success Criteria", 1)[1].split("\n## ", 1)[0]
    kriterier = re.findall(r"^\| ([^|*]+?) \| \*", del_, flags=re.MULTILINE)
    assert len(kriterier) == 4, kriterier
    seksjon = _seksjon_10()
    for kriterium in kriterier:
        assert f"| **{kriterium}**" in seksjon, kriterium
