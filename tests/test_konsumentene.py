"""Konsumentene leser Kursrad gjennom Kursleser - story 1.4b, AD-3, AD-19.

signalberegning, markedsoversikt, aksjedetalj og graf er den funksjonelle
kjernen. De faar ikke vite hvor kursene kommer fra, og ikke hva kilden kaller
feltene sine. EODHDs feltnavn oversettes ett sted, kursrad_fra_eodhd, og
stopper der.

Foer 1.4b leste de tre konsumentene EODHDs dict-noekler og falt tilbake fra
adjusted_close til close. Testen under feiler hvis noekkelen eller fallbacken
kommer tilbake, eller hvis en av modulene begynner aa importere lageret selv.

Story 1.5: portmodulen kursdata.py gjoer ikke I/O og importerer ingen
adapter, og EODHDs feltnavn staar ikke der heller. app.py henter Kursleseren
fra filadapteren og velger ikke oeyeblikksbilde selv.
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

# Porten kjenner ingen adapter og gjoer ingen I/O (story 1.5).
PORTMODUL = "kursdata.py"
FORBUDT_I_PORTEN = {"json", "pathlib", "lagring_fil", "lagring_sqlite", "eodhd"}

# Modulene vakten mot EODHDs feltnavn gjelder: kjernen og porten.
UTEN_EODHD = KJERNEMODULER + (PORTMODUL,)


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


@pytest.mark.parametrize("navn", KJERNEMODULER)
def test_importerer_verken_sqlite3_eller_pathlib(navn):
    """Kjernen gjoer ikke I/O. Lagringen hoerer til skallet."""
    assert _importerte_moduler(_tre(navn)) & FORBUDTE_MODULER == set()


@pytest.mark.parametrize("navn", UTEN_EODHD)
def test_ingen_eodhd_noekler_i_kildeteksten(navn):
    """Ingen streng i modulen er en av EODHDs feltnavn. Staar den der, leser
    modulen kildens rader i stedet for Kursrad."""
    strenger = {
        node.value
        for node in ast.walk(_tre(navn))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert strenger & set(EODHD_NOEKLER) == set()


@pytest.mark.parametrize("navn", UTEN_EODHD)
def test_fallbacken_er_borte(navn):
    """Ingen adjusted_close, ingen rad.get( og ingen rad[ - heller ikke i en
    kommentar eller docstring, der den ellers kunne overlevd som laereplan."""
    tekst = (SRC / navn).read_text(encoding="utf-8")
    assert re.findall(r"adjusted_close|rad\.get\(|rad\[", tekst) == []


def test_porten_importerer_verken_io_eller_adapter():
    """kursdata.py er porten. Den leser ikke filer, og den importerer ingen
    adapter - da ville avhengigheten pekt feil vei (story 1.5)."""
    assert _importerte_moduler(_tre(PORTMODUL)) & FORBUDT_I_PORTEN == set()


def _navn_i(tre: ast.Module) -> set[str]:
    """Alle navn modulen bruker eller importerer, ogsaa som attributt."""
    navn = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Name):
            navn.add(node.id)
        elif isinstance(node, ast.Attribute):
            navn.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            navn |= {alias.name.split(".")[-1] for alias in node.names}
            navn |= {alias.asname for alias in node.names if alias.asname}
    return navn


def test_app_velger_ikke_oeyeblikksbilde_selv():
    """app.py verken importerer eller kaller nyeste_snapshot, og kjenner ikke
    SnapshotKilde. Kursleseren kommer fra filadapteren (story 1.5)."""
    assert _navn_i(_tre("app.py")) & {"nyeste_snapshot", "SnapshotKilde"} == set()
