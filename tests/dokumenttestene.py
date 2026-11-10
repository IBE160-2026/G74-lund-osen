"""Dokumenttestene: testene som leser README-en, docs/ eller _bmad-output/.

Story 9.9, ekstravinduet 09.11 (spec-9-9-dokumenttestene.md). Kjøres med

    uv run pytest --dokumentene

Modulene finnes uten å endre testfilene. En testmodul er med når en
strengkonstant i koden er en sti til README.md, docs/ eller _bmad-output/,
eller når den importerer en hjelpemodul i tests/ som gjør det (som
dokumentene.py). Docstrings, kommentarer, f-strenger og meldingene i assert
teller ikke, fordi de bare nevner dokumentene (gjennomgangen, BH1). En modul
som leser dokumentene på en måte koden ikke viser, som gjennom src/ eller en
fixture i conftest.py, føres i TILLEGG (BH2, BH3).

Under hver kjøring noterer conftest.py hvilke dokumenter hver testmodul
åpner. test_dokumenttestene.py kjøres sist og feiler hvis en modul som åpnet
et dokument, ikke er med i kommandoen. Grensen: en underprosess som en test
starter, noteres ikke, så der er det koden som avgjør.
"""

import ast
import os
from functools import cache
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
TESTMAPPA = ROT / "tests"
# Hvert dokument som åpnes under en kjøring: modulstien -> dokumentene.
AAPNET = pytest.StashKey[dict[str, set[str]]]()

_README = os.path.normcase(str(ROT / "README.md"))
_MAPPENE = tuple(os.path.normcase(str(ROT / navn)) + os.sep for navn in ("docs", "_bmad-output"))


def er_dokument(sti) -> bool:
    """Sant for README-en og alt under docs/ og _bmad-output/ i repoet."""
    if isinstance(sti, int):
        return False
    try:
        full = os.path.normcase(os.path.abspath(os.fsdecode(sti)))
    except (TypeError, ValueError):
        return False
    return full == _README or full.startswith(_MAPPENE)


# Moduler som leser dokumentene uten at det står i koden deres (BH2, BH3).
# Tom 09.11: hele settet fant ingen.
TILLEGG: frozenset[str] = frozenset()


def _peker_paa_dokumentene(tekst: str) -> bool:
    t = tekst.replace("\\", "/")
    return (
        "README.md" in t
        or t in ("docs", "_bmad-output")
        or t.startswith(("docs/", "_bmad-output/"))
        or "/docs/" in t
        or "/_bmad-output" in t
    )


def _docstringene(tre: ast.AST) -> set[int]:
    """id-ene til strengene som ikke er stier: de som står alene som en
    setning (docstrings), delene av en f-streng og meldingen i en assert
    (gjennomgangen, BH1)."""
    ut = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            ut.add(id(node.value))
        elif isinstance(node, ast.JoinedStr):
            ut.update(id(del_) for del_ in node.values)
        elif isinstance(node, ast.Assert) and node.msg is not None:
            ut.update(id(del_) for del_ in ast.walk(node.msg))
    return ut


def _importene(tre: ast.AST) -> set[str]:
    navn = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            navn.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            navn.add(node.module.split(".")[0])
    return navn


def _leser_selv(tre: ast.AST) -> bool:
    docstringene = _docstringene(tre)
    return any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstringene
        and _peker_paa_dokumentene(node.value)
        for node in ast.walk(tre)
    )


@cache
def modulene(mappe: Path = TESTMAPPA) -> frozenset[str]:
    """Filnavnene til testmodulene i mappa som leser dokumentene."""
    trær = {sti: ast.parse(sti.read_text(encoding="utf-8"), filename=str(sti)) for sti in sorted(mappe.glob("*.py"))}
    leser = {sti.stem for sti, tre in trær.items() if _leser_selv(tre)}
    # Lagt til 10.11 (hele settet i deler, steg 4 i ekstravinduet): også en
    # testmodul som importeres, teller. test_utseende.py importerer
    # test_investorsidene_demo, som leser docs/kilder-og-rettigheter.md når den
    # lastes; i en del uten den modulen ble lesingen notert på test_utseende.py.
    hjelperne = {sti.stem for sti in trær if sti.stem != "conftest"}
    endret = True
    while endret:
        endret = False
        for sti, tre in trær.items():
            if sti.stem not in leser and _importene(tre) & hjelperne & leser:
                leser.add(sti.stem)
                endret = True
    return frozenset(f"{stem}.py" for stem in leser if stem.startswith("test_")) | TILLEGG


def utenfor(aapnet: dict[str, set[str]], med: frozenset[str]) -> dict[str, list[str]]:
    """Modulene som åpnet et dokument uten å være med, med opptil tre av
    dokumentene. Vakten i test_dokumenttestene.py feiler når den ikke er tom."""
    return {modul: sorted(filer)[:3] for modul, filer in aapnet.items() if modul not in med}
