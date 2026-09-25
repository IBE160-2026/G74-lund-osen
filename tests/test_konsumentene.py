"""Konsumentene leser Kursrad gjennom Kursleser - story 1.4b, AD-3, AD-19.

signalberegning, markedsoversikt, aksjedetalj og graf er den funksjonelle
kjernen. De faar ikke vite hvor kursene kommer fra, og ikke hva kilden kaller
feltene sine. EODHDs feltnavn oversettes ett sted, kursrad_fra_eodhd, og
stopper der.

Foer 1.4b leste de tre konsumentene EODHDs dict-noekler og falt tilbake fra
adjusted_close til close. Testen under feiler hvis noekkelen eller fallbacken
kommer tilbake, eller hvis en av modulene begynner aa importere lageret selv.
"""

import ast
import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"

KJERNEMODULER = (
    "signalberegning.py",
    "markedsoversikt.py",
    "aksjedetalj.py",
    "graf.py",
)

FORBUDTE_MODULER = {"sqlite3", "pathlib"}

EODHD_NOEKLER = ("adjusted_close", "close", "volume", "date")


def _tre(navn: str) -> ast.Module:
    return ast.parse((SRC / navn).read_text(encoding="utf-8"), filename=navn)


def _importerte_moduler(tre: ast.Module) -> set[str]:
    moduler = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            moduler.add(node.module.split(".")[0])
    return moduler


def _importerte_navn(tre: ast.Module) -> set[str]:
    return {
        alias.name
        for node in ast.walk(tre)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }


@pytest.mark.parametrize("navn", KJERNEMODULER)
def test_importerer_verken_sqlite3_eller_pathlib(navn):
    """Kjernen gjoer ikke I/O. Lagringen hoerer til skallet."""
    assert _importerte_moduler(_tre(navn)) & FORBUDTE_MODULER == set()


@pytest.mark.parametrize("navn", KJERNEMODULER)
def test_importerer_ikke_kurskilde(navn):
    """Kurskilde gir dict. Kjernen leser Kursrad gjennom Kursleser."""
    assert "Kurskilde" not in _importerte_navn(_tre(navn))


@pytest.mark.parametrize("navn", KJERNEMODULER)
def test_ingen_eodhd_noekler_i_kildeteksten(navn):
    """Ingen streng i modulen er en av EODHDs feltnavn. Staar den der, leser
    modulen kildens rader i stedet for Kursrad."""
    strenger = {
        node.value
        for node in ast.walk(_tre(navn))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert strenger & set(EODHD_NOEKLER) == set()


@pytest.mark.parametrize("navn", KJERNEMODULER)
def test_fallbacken_er_borte(navn):
    """Ingen adjusted_close, ingen rad.get( og ingen rad[ - heller ikke i en
    kommentar eller docstring, der den ellers kunne overlevd som laereplan."""
    tekst = (SRC / navn).read_text(encoding="utf-8")
    assert re.findall(r"adjusted_close|rad\.get\(|rad\[", tekst) == []
