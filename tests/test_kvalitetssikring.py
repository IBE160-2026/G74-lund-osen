"""Story 9.1: docs/kvalitetssikring.md følger repoet.

Hver spesifikasjon med status done har en egen rad i tabellen per story i §3
og i tabellen over gjennomgangene i §5, og hver test som kvalitetssikring.md
og vurderingsmatrise.md nevner med fil og navn, finnes. Det samme gjelder
testene vedlegget fra 17.10 nevner uten fil. Testene leser filene og kjører
ingenting.
"""

import ast
import functools
import re
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
KVALITETSSIKRING = ROT / "docs" / "kvalitetssikring.md"
MATRISE = ROT / "docs" / "vurderingsmatrise.md"
SPESIFIKASJONER = ROT / "_bmad-output" / "implementation-artifacts"
TESTER = ROT / "tests"

# tests/test_x.py::Klasse::test_navn, tests/test_x.py::test_navn eller med
# nøstede klasser, og med en parameter i hakeparentes som skal bort.
TESTNAVN = re.compile(r"tests/((?:\w+/)*test_\w+\.py)::((?:\w+::)*\w+)(?:\[[^\]`]*\])?")

# Spesifikasjoner som deler story med en annen, og hva raden for dem begynner
# med i tabellene. Den andre har bare storynummeret. Gjennomgangen av 9.1
# (ECH3): uten dette kunne raden for en spesifikasjon dekke en annens.
EGEN_MERKELAPP = {
    "spec-2-3-hentingen-fra-kl-21": "2.3, kl. 21",
    "spec-3-4-alle-ti-kombinasjonene-paa-siste-demodag": "3.4, alle 10",
}

# Tester som har fått nytt navn etter at et dokument nevnte dem, med det nye
# navnet. En linje fjernes ikke (regel 13), så det gamle navnet godtas her.
OMDOEPT: dict[str, str] = {}

# Antall spesifikasjoner med status done da testen ble skrevet, 17.10: 41 før
# spesifikasjonen for 9.1 selv. Gulvet fanger en lesing av status som slutter
# å virke.
MINST_FERDIGE = 41


def _frontmatter(spesifikasjon: Path) -> dict[str, str]:
    """Nøkkel og verdi mellom de to første linjene med «---»."""
    linjer = spesifikasjon.read_text(encoding="utf-8").splitlines()
    if not linjer or linjer[0].strip() != "---":
        return {}
    felt = {}
    for linje in linjer[1:]:
        if linje.strip() == "---":
            break
        if ":" in linje:
            noekkel, verdi = linje.split(":", 1)
            felt[noekkel.strip()] = verdi.strip().strip("'\"")
    return felt


def _merkelapp(spesifikasjon: Path) -> str:
    """spec-2-3b-... gir 2.3b, spec-10-2a-... gir 10.2a."""
    treff = re.match(r"spec-(\d+)-(\d+[a-z0-9]*)(?:-|\.md$)", spesifikasjon.name)
    if not treff:
        pytest.fail(f"Navnet {spesifikasjon.name} gir ingen story. Ventet spec-<epic>-<story>-…")
    return f"{treff.group(1)}.{treff.group(2)}"


def alle() -> list[Path]:
    return sorted(SPESIFIKASJONER.glob("spec-*.md"))


def ferdige() -> list[Path]:
    return [s for s in alle() if _frontmatter(s).get("status") == "done"]


def _tabellen_under(tekst: str, overskrift: str, kolonne: str) -> list[str]:
    """Første celle i hver rad i den første tabellen etter overskriften,
    der første kolonne heter kolonne. Bare den tabellen, så en annen tabell
    med samme kolonne lenger ned ikke teller (gjennomgangen av 9.1, ECH2)."""
    if f"\n{overskrift}\n" not in tekst:
        pytest.fail(f"Overskriften «{overskrift}» finnes ikke i {KVALITETSSIKRING.name}")
    linjer = tekst.split(f"\n{overskrift}\n", 1)[1].splitlines()
    celler, i_tabell = [], False
    for linje in linjer:
        if not i_tabell:
            if linje.startswith(f"| {kolonne} |"):
                i_tabell = True
            elif linje.startswith("#"):
                break
            continue
        if not linje.startswith("|"):
            break
        if not linje.startswith("|---"):
            celler.append(linje.split("|")[1].strip())
    if not celler:
        pytest.fail(f"Ingen tabell med «{kolonne}» under «{overskrift}»")
    return celler


def _har_rad(celler: list[str], spesifikasjon: Path) -> bool:
    """Om en rad er spesifikasjonens egen. Raden for en med egen merkelapp
    begynner med den. Raden for den andre har storynummeret alene, fulgt av
    mellomrom eller komma, men ikke en av de egne merkelappene."""
    egen = EGEN_MERKELAPP.get(spesifikasjon.stem)
    if egen:
        return any(c.startswith(egen) for c in celler)
    merke = _merkelapp(spesifikasjon)
    andres = [m for m in EGEN_MERKELAPP.values() if m.split(",")[0] == merke]
    return any(
        (c == merke or c.startswith(merke + " ") or c.startswith(merke + ","))
        and not any(c.startswith(m) for m in andres)
        for c in celler
    )


def test_merkelappen_leses_av_filnavnet():
    assert _merkelapp(Path("spec-2-3b-kallene.md")) == "2.3b"
    assert _merkelapp(Path("spec-10-2a-modellen.md")) == "10.2a"
    assert _merkelapp(Path("spec-8-15-sortering.md")) == "8.15"


def test_status_leses_bare_fra_frontmatter(tmp_path):
    """Ville feilet hvis en linje «status: done» i teksten ble lest."""
    fil = tmp_path / "spec-1-1-x.md"
    fil.write_text("---\ntitle: x\nstatus: 'in-review'\n---\n\nstatus: done\n", encoding="utf-8")
    assert _frontmatter(fil)["status"] == "in-review"
    fil.write_text("status: done\n", encoding="utf-8")
    assert _frontmatter(fil) == {}


def test_det_finnes_ferdige_spesifikasjoner():
    """Ville feilet hvis lesingen av status sluttet å virke, så testene
    under ikke prøvde noe."""
    assert len(ferdige()) >= MINST_FERDIGE


def test_hver_story_som_deles_har_egen_merkelapp():
    """Deler to spesifikasjoner story, må alle utenom én ha en egen
    merkelapp. Ville feilet med en ny spesifikasjon for samme story uten."""
    per_merke: dict[str, list[str]] = {}
    for s in alle():
        per_merke.setdefault(_merkelapp(s), []).append(s.stem)
    for merke, stammer in per_merke.items():
        uten = [s for s in stammer if s not in EGEN_MERKELAPP]
        assert len(uten) <= 1, (merke, uten)


@pytest.mark.parametrize(
    "overskrift, kolonne",
    [
        ("### Per story", "Story"),
        ("### Gjennomgangen av hver story", "Story"),
    ],
)
def test_hver_ferdige_spesifikasjon_har_en_rad(overskrift, kolonne):
    """Ville feilet hvis raden for en spesifikasjon med status done ble tatt
    bort fra tabellen i §3 eller §5, eller en spesifikasjon ble satt til done
    uten rad. Raden må være dens egen, ikke en for en annen spesifikasjon med
    samme story (ECH3)."""
    celler = _tabellen_under(KVALITETSSIKRING.read_text(encoding="utf-8"), overskrift, kolonne)
    mangler = [s.stem for s in ferdige() if not _har_rad(celler, s)]
    assert not mangler, (overskrift, mangler)


@functools.lru_cache(maxsize=None)
def _testene_i_fila(fil: Path) -> frozenset[str]:
    """Hver test og klasse i fila, med klassene foran: «test», «Klasse»,
    «Klasse::test» og «Ytre::Indre::test». Også async def."""
    if not fil.is_file():
        return frozenset()
    navn = set()

    def gaa(noder, foran: str) -> None:
        for node in noder:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                navn.add(foran + node.name)
            elif isinstance(node, ast.ClassDef):
                navn.add(foran + node.name)
                gaa(node.body, f"{foran}{node.name}::")

    gaa(ast.parse(fil.read_text(encoding="utf-8")).body, "")
    return frozenset(navn)


def _alle_testnavn() -> set[str]:
    """Navnet på hver test i tests/, uten fil og klasse."""
    navn = set()
    for fil in TESTER.rglob("test_*.py"):
        navn.update(n.rsplit("::", 1)[-1] for n in _testene_i_fila(fil))
    return navn


def test_lesingen_tar_med_async_noestede_klasser_og_en_fil_som_mangler(tmp_path):
    fil = tmp_path / "test_x.py"
    fil.write_text("class TestA:\n    class TestB:\n        async def test_c(self): pass\n", encoding="utf-8")
    assert {"TestA", "TestA::TestB", "TestA::TestB::test_c"} <= _testene_i_fila(fil)
    assert _testene_i_fila(tmp_path / "finnes_ikke.py") == frozenset()


@pytest.mark.parametrize("dokument", [KVALITETSSIKRING, MATRISE], ids=lambda d: d.name)
def test_hver_test_dokumentene_nevner_finnes(dokument):
    """Ville feilet hvis et testnavn i dokumentet var skrevet feil, eller testen
    var flyttet eller fikk nytt navn uten at dokumentet fulgte med. En fil
    som ikke finnes, står i lista, ikke som en feil midt i sjekken."""
    nevnt = TESTNAVN.findall(dokument.read_text(encoding="utf-8"))
    assert nevnt, dokument.name
    borte = sorted(
        {
            f"tests/{fil}::{navn}"
            for fil, navn in nevnt
            if navn not in _testene_i_fila(TESTER / fil) and f"tests/{fil}::{navn}" not in OMDOEPT
        }
    )
    assert not borte, borte


def test_testene_i_vedlegget_fra_17_10_finnes():
    """Gjennomgangen av 9.1 (BH3, BH4): vedlegget fra 17.10 nevner testene uten
    fil. Hvert navn finnes i tests/, utenom gamle navn merket «før 17.10:».
    Ville feilet med et navn som er skrevet feil i vedlegget."""
    tekst = KVALITETSSIKRING.read_text(encoding="utf-8")
    del_ = tekst.split("\n### Fra 2.2 til 10.3, én linje per spesifikasjon\n", 1)[1]
    gamle = set(re.findall(r"før 17\.10: `(?:\w+::)?(test_\w+)`", del_))
    nevnt = set(re.findall(r"`(?:\w+::)*(test_\w+)", del_)) - gamle
    assert nevnt
    borte = sorted(nevnt - _alle_testnavn())
    assert not borte, borte
