"""Dokumenttestene: testene som leser README-en, docs/ eller _bmad-output/.

Ekstravinduet 09.11 (spec-dokumenttestene.md). Kjøres med

    uv run pytest --dokumentene

Modulene finnes uten å endre testfilene. En testmodul er med når en
strengkonstant i koden peker på README-en, docs/ eller _bmad-output/, eller
når den importerer en hjelpemodul i tests/ som gjør det (som dokumentene.py).
Docstrings og kommentarer teller ikke, fordi de bare nevner dokumentene.

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


def _peker_paa_dokumentene(tekst: str) -> bool:
    t = tekst.replace("\\", "/")
    return "README" in t or "_bmad-output" in t or t == "docs" or t.startswith("docs/") or "/docs/" in t


def _docstringene(tre: ast.AST) -> set[int]:
    """id-ene til strengene som står alene som en setning (docstrings)."""
    return {
        id(node.value)
        for node in ast.walk(tre)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
    }


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
    hjelperne = {sti.stem for sti in trær if not sti.stem.startswith("test_") and sti.stem != "conftest"}
    endret = True
    while endret:
        endret = False
        for sti, tre in trær.items():
            if sti.stem not in leser and _importene(tre) & hjelperne & leser:
                leser.add(sti.stem)
                endret = True
    return frozenset(f"{stem}.py" for stem in leser if stem.startswith("test_"))
