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
    "boersdag.py",
    "tilstand.py",
    "tallformat.py",
)

# Kjernen gjoer ikke I/O og importerer ikke skallet (spinen, lagtabellen).
# Skallet ble lagt til i story 1.7, der spinen sier det for tilstand.py.
FORBUDTE_MODULER = {
    "sqlite3", "pathlib", "requests", "flask",
    "app", "fetch_prices", "lagring_sqlite", "lagring_fil", "eodhd",
}

EODHD_NOEKLER = ("adjusted_close", "close", "volume", "date")

# Portene kjenner ingen adapter og gjoer ingen I/O (story 1.5). De importerer
# heller ikke kjernen: de er loevnoder (spinen, grafen). Story 1.6 la til
# vurderingsdata.py, som derfor ikke kan regne boersdagen selv.
PORTMODULER = ("kursdata.py", "vurderingsdata.py")
FORBUDT_I_PORTEN = {
    "json", "pathlib", "sqlite3", "lagring_fil", "lagring_sqlite", "eodhd",
    *(navn.removesuffix(".py") for navn in KJERNEMODULER),
}

# Modulene vakten mot EODHDs feltnavn gjelder: kjernen og portene.
UTEN_EODHD = KJERNEMODULER + PORTMODULER

# Strengvakten gjelder i tillegg skallet utenom oversetteren (eodhd.py). Ikke
# fallbackvakten: lagring_sqlite.py leser rad[0] fra basen, og det er lovlig.
# Story 1.8: fetch_prices.py oversetter gjennom eodhd.py og er med her.
UTEN_EODHD_STRENGER = UTEN_EODHD + (
    "lagring_fil.py", "lagring_sqlite.py", "app.py", "fetch_prices.py",
)

# De to som leser en serie fra EODHD. Begge skal bruke samme regel (story 1.8).
SERIELESERE = ("lagring_fil.py", "fetch_prices.py")


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
def test_importerer_verken_io_eller_skallet(navn):
    """Kjernen gjoer ikke I/O og importerer ikke skallet. Lagringen hoerer
    til skallet."""
    assert _importerte_moduler(_tre(navn)) & FORBUDTE_MODULER == set()


def test_signalberegning_importerer_bare_porten_og_loevnodene():
    """Story 2.5: vurder bygger Vurdering og Grunn, saa kjernen importerer
    porten vurderingsdata, slik tilstand.py gjoer. Av prosjektets moduler er
    det bare kursdata, tallformat og vurderingsdata, aldri et lager."""
    prosjektet = {sti.stem for sti in SRC.glob("*.py")}
    assert _importerte_moduler(_tre("signalberegning.py")) & prosjektet == {
        "kursdata", "tallformat", "vurderingsdata",
    }


@pytest.mark.parametrize("navn", UTEN_EODHD_STRENGER)
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


@pytest.mark.parametrize("navn", PORTMODULER)
def test_porten_importerer_verken_io_eller_adapter(navn):
    """En port leser ikke filer, og den importerer verken en adapter eller
    kjernen - da ville avhengigheten pekt feil vei (story 1.5 og 1.6)."""
    assert _importerte_moduler(_tre(navn)) & FORBUDT_I_PORTEN == set()


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


@pytest.mark.parametrize("navn", SERIELESERE)
def test_hentingen_og_leseren_bruker_samme_regel_for_en_serie(navn):
    """Story 1.8: serie_fra_eodhd avgjoer om en serie kan leses. Kaller en
    av dem kursrad_fra_eodhd selv, har den sin egen regel ved siden av."""
    brukt = _navn_i(_tre(navn))
    assert "serie_fra_eodhd" in brukt
    assert "kursrad_fra_eodhd" not in brukt


def test_app_velger_ikke_oeyeblikksbilde_selv():
    """app.py verken importerer eller kaller nyeste_snapshot, og kjenner ikke
    SnapshotKilde, SnapshotLeser, DATA_KATALOG eller RAA_KATALOG.
    Kursleseren kommer fra filadapteren (story 1.5 og 2.1b)."""
    forbudt = {
        "nyeste_snapshot", "SnapshotKilde", "SnapshotLeser", "DATA_KATALOG", "RAA_KATALOG",
    }
    assert _navn_i(_tre("app.py")) & forbudt == set()


def test_webserveren_importerer_ikke_hentingen():
    """Story 2.2, AD-2 og AD-10: app.py er sin egen inngang og kjenner verken
    hentekommandoen, nettet eller filadapteren. Sidene leser basen."""
    forbudt = {"fetch_prices", "requests", "eodhd", "lagring_fil"}
    assert _importerte_moduler(_tre("app.py")) & forbudt == set()


def _connect_kall(tre: ast.Module) -> list[str]:
    """Funksjonene som kaller connect paa sqlite3, eller importerer connect
    fra sqlite3. "<modul>" for kall utenfor en funksjon."""
    funnet = []

    def besoek(node, funksjon):
        for barn in ast.iter_child_nodes(node):
            navn = funksjon
            if isinstance(barn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                navn = barn.name
            if (
                isinstance(barn, ast.Call)
                and isinstance(barn.func, ast.Attribute)
                and barn.func.attr == "connect"
                and isinstance(barn.func.value, ast.Name)
                and barn.func.value.id == "sqlite3"
            ):
                funnet.append(navn)
            if isinstance(barn, ast.ImportFrom) and barn.module == "sqlite3":
                if any(alias.name == "connect" for alias in barn.names):
                    funnet.append(navn)
            besoek(barn, navn)

    besoek(tre, "<modul>")
    return funnet


def test_bare_aapne_base_kobler_til_basen():
    """Story 2.1b, K2: basen aapnes ett sted. Ingen annen kode i src/
    kaller sqlite3.connect. Ville feilet hvis fetch_prices koblet til selv
    (M4)."""
    kall = {
        (sti.name, funksjon)
        for sti in sorted(SRC.glob("*.py"))
        for funksjon in _connect_kall(_tre(sti.name))
    }
    assert kall == {("lagring_sqlite.py", "aapne_base")}
