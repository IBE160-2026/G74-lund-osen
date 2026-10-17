"""Story 9.1: docs/kvalitetssikring.md følger repoet.

Hver spesifikasjon med status done har en rad i tabellen per story i §3 og i
tabellen over gjennomgangene i §5, og hver test som kvalitetssikring.md og
vurderingsmatrise.md nevner med fil og navn, finnes. Testene leser filene og
kjører ingenting.
"""

import ast
import re
from collections import Counter
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
KVALITETSSIKRING = ROT / "docs" / "kvalitetssikring.md"
MATRISE = ROT / "docs" / "vurderingsmatrise.md"
SPESIFIKASJONER = ROT / "_bmad-output" / "implementation-artifacts"

# tests/test_x.py::Klasse::test_navn eller tests/test_x.py::test_navn, med en
# parameter i hakeparentes som skal bort.
TESTNAVN = re.compile(r"tests/(test_\w+\.py)::((?:\w+::)?\w+)(?:\[[^\]`]*\])?")


def _status(spesifikasjon: Path) -> str | None:
    for linje in spesifikasjon.read_text(encoding="utf-8").splitlines():
        if linje.startswith("status:"):
            return linje.split(":", 1)[1].strip().strip("'\"")
    return None


def _merkelapp(spesifikasjon: Path) -> str:
    """spec-2-3b-... gir 2.3b, spec-10-2a-... gir 10.2a."""
    treff = re.match(r"spec-(\d+)-(\d+[a-z]?)-", spesifikasjon.name)
    assert treff, spesifikasjon.name
    return f"{treff.group(1)}.{treff.group(2)}"


def ferdige() -> list[Path]:
    return sorted(s for s in SPESIFIKASJONER.glob("spec-*.md") if _status(s) == "done")


def _del(tekst: str, overskrift: str) -> str:
    """Teksten fra overskriften (## N. ...) til neste overskrift på samme nivå."""
    start = tekst.index(f"\n## {overskrift}")
    slutt = tekst.find("\n## ", start + 1)
    return tekst[start: slutt if slutt != -1 else None]


def _forste_celler(del_: str, kolonnenavn: str) -> list[str]:
    """Første ord i første celle i hver rad i tabellene som har kolonnenavn
    som første kolonne."""
    celler, i_tabell = [], False
    for linje in del_.splitlines():
        if linje.startswith(f"| {kolonnenavn} |"):
            i_tabell = True
            continue
        if not linje.startswith("|"):
            i_tabell = False
            continue
        if i_tabell and not linje.startswith("|---"):
            forste = linje.split("|")[1].strip()
            celler.append(re.split(r"[\s,]", forste, maxsplit=1)[0])
    return celler


def test_merkelappen_leses_av_filnavnet():
    assert _merkelapp(Path("spec-2-3b-kallene.md")) == "2.3b"
    assert _merkelapp(Path("spec-10-2a-modellen.md")) == "10.2a"
    assert _merkelapp(Path("spec-8-15-sortering.md")) == "8.15"


def test_det_finnes_ferdige_spesifikasjoner():
    """Ville feilet hvis lesingen av status sluttet å virke, så testene
    under ikke prøvde noe."""
    assert len(ferdige()) >= 40


@pytest.mark.parametrize("overskrift, kolonne", [
    ("3. Mutantpraksisen", "Story"),
    ("5. Kodegjennomganger og kontroller", "Story"),
])
def test_hver_ferdige_spesifikasjon_har_en_rad(overskrift, kolonne):
    """Ville feilet hvis en rad ble tatt bort fra §3 eller §5, eller en ny
    spesifikasjon ble satt til done uten rad. Deler flere spesifikasjoner
    samme story, som 2.3 og tillegget om kl. 21:00, kreves én rad for hver."""
    del_ = _del(KVALITETSSIKRING.read_text(encoding="utf-8"), overskrift)
    rader = Counter(_forste_celler(del_, kolonne))
    trengs = Counter(_merkelapp(s) for s in ferdige())
    mangler = {merke: antall for merke, antall in trengs.items() if rader[merke] < antall}
    assert not mangler, (overskrift, mangler)


def _testene_i_fila(fil: Path) -> set[str]:
    """«Klasse::test» og «test» for hver test i fila."""
    navn = set()
    for node in ast.parse(fil.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            navn.add(node.name)
        elif isinstance(node, ast.ClassDef):
            for metode in node.body:
                if isinstance(metode, ast.FunctionDef) and metode.name.startswith("test"):
                    navn.add(f"{node.name}::{metode.name}")
    return navn


@pytest.mark.parametrize("dokument", [KVALITETSSIKRING, MATRISE], ids=lambda d: d.name)
def test_hver_test_dokumentene_nevner_finnes(dokument):
    """Ville feilet hvis et testnavn i dokumentet var skrevet feil, eller testen
    var flyttet eller fikk nytt navn uten at dokumentet fulgte med."""
    nevnt = TESTNAVN.findall(dokument.read_text(encoding="utf-8"))
    assert nevnt, dokument.name
    borte = sorted({f"tests/{fil}::{navn}" for fil, navn in nevnt
                    if navn not in _testene_i_fila(ROT / "tests" / fil)})
    assert not borte, borte
