"""Story 9.7: ruff sjekker og formatterer src/ og tests/.

CI kjoerer `ruff check` og `ruff format --check` foer testene. Testene her
kjoerer det samme, saa `uv run pytest` feiler lokalt ogsaa, foer en commit.
ruff kjoeres som underprosess fra uv.lock (`python -m ruff`), uten cache og
uten nett, med reglene i pyproject.toml.
"""

import subprocess
import sys
import tomllib
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent


def _ruff(*argumenter: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ruff", *argumenter, "--no-cache"],
        cwd=ROT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


def test_ruff_check_finner_ingenting():
    """Ville feilet hvis en ubrukt import, en usortert importblokk eller en
    feil bugbear finner, sto i src/ eller tests/ (mutant A1)."""
    svar = _ruff("check")
    assert svar.returncode == 0, svar.stdout + svar.stderr


def test_ruff_format_er_kjoert():
    """Ville feilet hvis en linje i src/ eller tests/ ikke var formattert slik
    ruff format gjoer det (mutant A2)."""
    svar = _ruff("format", "--check")
    assert svar.returncode == 0, svar.stdout + svar.stderr


def test_ruff_sjekker_src_og_tests():
    """Ville feilet hvis include i pyproject.toml ikke lenger traff filene, saa
    sjekkene over gikk gjennom uten aa ha lest noe."""
    svar = _ruff("check", "--show-files")
    filer = {Path(linje.strip()).resolve() for linje in svar.stdout.splitlines() if linje.strip().endswith(".py")}
    assert ROT / "src" / "app.py" in filer
    assert Path(__file__).resolve() in filer
    assert len(filer) == len(list((ROT / "src").rglob("*.py"))) + len(list((ROT / "tests").rglob("*.py")))


def test_reglene_er_pyflakes_importene_og_bugbear():
    """Ville feilet hvis en regelgruppe ble tatt ut av pyproject.toml, eller en
    regel for smak kom inn uten at storyen ble endret."""
    oppsett = tomllib.loads((ROT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["ruff"]
    assert oppsett["lint"]["select"] == ["F", "I", "B"]
    assert oppsett["lint"]["ignore"] == ["B905"]
    utvikling = tomllib.loads((ROT / "pyproject.toml").read_text(encoding="utf-8"))["dependency-groups"]["dev"]
    assert any(krav.startswith("ruff") for krav in utvikling)


def test_ruff_er_laast_i_uv_lock():
    """Ville feilet hvis ruff ikke sto i uv.lock, saa CI og maskinene kunne
    formattert med ulike versjoner."""
    laas = tomllib.loads((ROT / "uv.lock").read_text(encoding="utf-8"))
    assert "ruff" in {pakke["name"] for pakke in laas["package"]}


def test_ci_kjoerer_ruff_foer_testene():
    """Ville feilet hvis CI sluttet aa kjoere ruff check eller ruff format
    --check, eller kjoerte dem etter testene."""
    arbeidsflyt = (ROT / ".github" / "workflows" / "tester.yml").read_text(encoding="utf-8")
    sjekk = arbeidsflyt.index("run: uv run ruff check")
    formatering = arbeidsflyt.index("run: uv run ruff format --check")
    tester = arbeidsflyt.index("run: uv run pytest -q")
    assert sjekk < tester and formatering < tester
