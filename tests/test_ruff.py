"""Story 9.7: ruff sjekker og formatterer src/ og tests/.

CI kjoerer `ruff check` og `ruff format --check` foer testene. Testene her
kjoerer det samme, saa `uv run pytest` feiler lokalt ogsaa, foer en commit.
ruff kjoeres som underprosess fra uv.lock (`python -m ruff`), uten cache og
uten nett, med reglene i pyproject.toml.
"""

import importlib.util
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
OPPSETT = tomllib.loads((ROT / "pyproject.toml").read_text(encoding="utf-8"))


def _ruff(*argumenter: str) -> subprocess.CompletedProcess:
    # Gjennomgangen (BH3, ECH4): uten utviklingsgruppen sier testen det, i
    # stedet for «No module named ruff», som ligner en feil ruff fant.
    if importlib.util.find_spec("ruff") is None:
        pytest.fail("ruff mangler i miljoeet: kjoer uv sync (ruff er i utviklingsgruppen i uv.lock)")
    return subprocess.run(
        [sys.executable, "-m", "ruff", *argumenter, "--no-cache"],
        cwd=ROT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        # Under faulthandler_timeout paa 120 s, saa en ruff som henger, gir
        # TimeoutExpired og ikke en stakk fra faulthandler (BH15).
        timeout=60,
    )


def _filene_ruff_sjekker() -> set[Path]:
    svar = _ruff("check", "--show-files")
    assert svar.returncode == 0, svar.stdout + svar.stderr
    return {Path(linje.strip()).resolve() for linje in svar.stdout.splitlines() if linje.strip().endswith(".py")}


def _filene_i_src_og_tests() -> set[Path]:
    """Python-filene i src/ og tests/: de som er sporet i git, eller alle
    utenom __pycache__ uten git, som i ZIP-fila (BH4, ECH2). En fil git
    holder ute, sjekker ruff heller ikke."""
    if shutil.which("git") and (ROT / ".git").exists():
        svar = subprocess.run(
            ["git", "ls-files", "--", "src/*.py", "tests/*.py"], cwd=ROT, capture_output=True, text=True
        )
        if svar.returncode == 0:
            return {(ROT / linje).resolve() for linje in svar.stdout.splitlines() if linje}
    return {
        sti.resolve()
        for mappe in ("src", "tests")
        for sti in (ROT / mappe).rglob("*.py")
        if "__pycache__" not in sti.parts
    }


def test_ruff_check_finner_ingenting():
    """Ville feilet hvis en ubrukt import, en usortert importblokk eller en
    feil bugbear finner, sto i src/ eller tests/ (mutant A1)."""
    svar = _ruff("check")
    assert svar.returncode == 0, svar.stdout + svar.stderr


def test_ruff_format_er_kjoert():
    """Ville feilet hvis en linje i src/ eller tests/ ikke var formattert slik
    ruff format gjoer det (mutant A2), eller hvis formatteringen leste andre
    filer enn sjekken, for eksempel med en exclude bare for format (VG2)."""
    svar = _ruff("format", "--check")
    assert svar.returncode == 0, svar.stdout + svar.stderr
    antall = len(_filene_ruff_sjekker())
    assert re.search(rf"^{antall} files already formatted$", svar.stdout, re.M), svar.stdout


def test_ruff_sjekker_src_og_tests():
    """Ville feilet hvis include i pyproject.toml ikke lenger traff filene, saa
    sjekkene over gikk gjennom uten aa ha lest noe."""
    filer = _filene_ruff_sjekker()
    assert ROT / "src" / "app.py" in filer
    assert Path(__file__).resolve() in filer
    assert _filene_i_src_og_tests() <= filer


def test_reglene_er_pyflakes_importene_og_bugbear():
    """Ville feilet hvis en regelgruppe ble tatt ut av pyproject.toml, eller en
    regel for smak kom inn uten at storyen ble endret, ogsaa gjennom
    extend-select, extend-ignore eller per-file-ignores (BH5, VG3)."""
    ruff = OPPSETT["tool"]["ruff"]
    assert set(ruff) == {"required-version", "include", "src", "line-length", "target-version", "lint"}
    assert ruff["lint"] == {"select": ["F", "I", "B"], "ignore": ["B905"]}
    utvikling = OPPSETT["dependency-groups"]["dev"]
    assert any(isinstance(krav, str) and krav.startswith("ruff") for krav in utvikling)


def test_ruff_er_laast_i_uv_lock():
    """Ville feilet hvis ruff ikke sto i uv.lock, eller hvis versjonen der
    ikke var den required-version krever, saa en uv lock --upgrade ga en ny
    formattering uten at noen bestemte det (BH2, ECH3)."""
    laas = tomllib.loads((ROT / "uv.lock").read_text(encoding="utf-8"))
    versjoner = [pakke["version"] for pakke in laas["package"] if pakke["name"] == "ruff"]
    assert versjoner == [OPPSETT["tool"]["ruff"]["required-version"].removeprefix("==")]


def _steget(arbeidsflyt: list[str], navn: str) -> list[str]:
    """Linjene i steget med navnet, til neste steg eller jobb."""
    start = arbeidsflyt.index(f"      - name: {navn}")
    slutt = start + 1
    while slutt < len(arbeidsflyt) and not re.match(r"^      - name: |^  \S", arbeidsflyt[slutt]):
        slutt += 1
    return arbeidsflyt[start:slutt]


def test_ci_kjoerer_ruff_foer_testene():
    """Ville feilet hvis CI sluttet aa kjoere ruff check eller ruff format
    --check, kjoerte dem med et flagg som slipper feil gjennom, uten aa stoppe
    (continue-on-error) eller med et vilkaar, eller kjoerte dem etter
    testene i jobben pytest (BH6, ECH5, VG4)."""
    linjer = (ROT / ".github" / "workflows" / "tester.yml").read_text(encoding="utf-8").splitlines()
    jobb = linjer[linjer.index("  pytest:") : linjer.index("  docker:")]
    sjekk = _steget(jobb, "ruff check")
    formatering = _steget(jobb, "ruff format --check")
    tester = _steget(jobb, "Kjoer testene")
    for steg, kommando in ((sjekk, "uv run ruff check"), (formatering, "uv run ruff format --check")):
        innhold = [linje.strip() for linje in steg[1:] if linje.strip() and not linje.strip().startswith("#")]
        assert innhold == [f"run: {kommando}"], steg
    assert jobb.index(sjekk[0]) < jobb.index(tester[0])
    assert jobb.index(formatering[0]) < jobb.index(tester[0])
    # Gjennomgangen (BH14, ECH1): testene kjoeres ogsaa naar ruff har feilet,
    # saa en glemt formattering ikke skjuler resultatet av testene.
    assert "        if: success() || failure()" in tester
