"""Dokumenttestene (ekstravinduet 09.11, spec-dokumenttestene.md).

`uv run pytest --dokumentene` kjører testmodulene som leser README-en, docs/
eller _bmad-output/. Modulene finnes i koden (tests/dokumenttestene.py), uten
å endre testfilene. Testen nederst kjøres sist og feiler hvis en modul som
åpnet et dokument i samme kjøring, ikke er med.
"""

import ast
import subprocess
import sys

import pytest

import dokumenttestene

# De seks i docs/kvalitetssikring.md (lagt til 2026-10-24), og testen som ga
# rød CI på 00b56821 fordi den leste README-en uten å være blant dem.
DE_SEKS = {
    "test_readme.py",
    "test_kvalitetssikring.py",
    "test_ryddighet.py",
    "test_suksesskriterier.py",
    "test_hjelpetekster.py",
    "test_docker.py",
}


def _skriv(mappe, navn, kode):
    (mappe / navn).write_text(kode, encoding="utf-8")


def test_de_seks_og_8_20a_er_med():
    """Ville feilet hvis en av de seks fra 24.10 eller test_aksjesiden_8_20a.py,
    som leser README-en og ga rød CI 08.11, falt utenfor kommandoen."""
    modulene = dokumenttestene.modulene()
    assert DE_SEKS | {"test_aksjesiden_8_20a.py", "test_dokumenttestene.py"} <= modulene


def test_bare_koden_teller(tmp_path):
    """Ville feilet hvis en docstring eller en kommentar som nevner README-en
    gjorde en modul til en dokumenttest, eller en sti i koden ikke gjorde det."""
    _skriv(tmp_path, "test_nevner.py", '"""Se README-en og docs/hjelp.md."""\n# _bmad-output\nX = 1\n')
    _skriv(tmp_path, "test_leser.py", 'from pathlib import Path\nT = (Path("..") / "docs" / "hjelp.md")\n')
    _skriv(tmp_path, "test_readme_sti.py", 'T = open("README.md").read()\n')
    _skriv(tmp_path, "test_bmad.py", 'S = "_bmad-output/implementation-artifacts"\n')
    _skriv(tmp_path, "test_url.py", 'U = "https://docs.astral.sh/uv/"\n')
    funnet = dokumenttestene.modulene.__wrapped__(tmp_path)
    assert funnet == {"test_leser.py", "test_readme_sti.py", "test_bmad.py"}


def test_en_hjelpemodul_som_leser_tar_med_dem_som_importerer_den(tmp_path):
    """Ville feilet hvis en test som leser dokumentene gjennom en hjelpemodul
    (som dokumentene.py, story 3.5i), ble borte fra kommandoen, også i to ledd."""
    _skriv(tmp_path, "hjelper.py", 'STI = "docs/installasjon.md"\n')
    _skriv(tmp_path, "hjelper2.py", "from hjelper import STI\n")
    _skriv(tmp_path, "test_direkte.py", "import hjelper\n")
    _skriv(tmp_path, "test_to_ledd.py", "from hjelper2 import STI\n")
    _skriv(tmp_path, "test_annen.py", "import json\n")
    funnet = dokumenttestene.modulene.__wrapped__(tmp_path)
    assert funnet == {"test_direkte.py", "test_to_ledd.py"}


@pytest.mark.parametrize(
    ("sti", "forventet"),
    [
        (dokumenttestene.ROT / "README.md", True),
        (dokumenttestene.ROT / "docs" / "hjelp.md", True),
        (dokumenttestene.ROT / "_bmad-output" / "planning-artifacts" / "epics.md", True),
        (str(dokumenttestene.ROT / "docs" / "appen" / "forsiden.png").encode(), True),
        (dokumenttestene.ROT / "src" / "app.py", False),
        (dokumenttestene.ROT / "docsen" / "x.md", False),
        (dokumenttestene.ROT / "tests" / "README.md", False),
        (3, False),
    ],
)
def test_er_dokument(sti, forventet):
    """Ville feilet hvis lytteren noterte en fil utenfor dokumentene, som en
    mappe som bare begynner med «docs», eller overså en under dem."""
    assert dokumenttestene.er_dokument(sti) is forventet


def test_kommandoen_kjoerer_bare_dokumenttestene(tmp_path):
    """Ville feilet hvis --dokumentene ikke fantes, eller samlet inn moduler
    som ikke leser dokumentene. Bare innsamlingen kjøres."""
    svar = subprocess.run(
        [sys.executable, "-m", "pytest", "--dokumentene", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=dokumenttestene.ROT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert svar.returncode == 0, svar.stdout[-2000:] + svar.stderr[-2000:]
    filene = {
        linje.split("::")[0].replace("\\", "/").rsplit("/", 1)[-1]
        for linje in svar.stdout.splitlines()
        if "::" in linje
    }
    assert filene == set(dokumenttestene.modulene())


def test_vakten_kjoeres_sist(request):
    """Ville feilet hvis vakten under ikke ble flyttet sist, så den ikke så
    modulene som kjører etter den."""
    navnene = [item.name for item in request.session.items]
    assert navnene[-1] == "test_ingen_test_som_leser_dokumentene_faller_utenfor"


def test_ingen_test_som_leser_dokumentene_faller_utenfor(request):
    """Ville feilet hvis en testmodul åpnet README-en, docs/ eller
    _bmad-output/ i denne kjøringen uten å være med i --dokumentene, som
    test_aksjesiden_8_20a.py 08.11. Kjøres sist (conftest.py)."""
    aapnet = request.config.stash[dokumenttestene.AAPNET]
    utenfor = {modul: sorted(filer)[:3] for modul, filer in aapnet.items() if modul not in dokumenttestene.modulene()}
    assert not utenfor, f"Leser dokumentene, men er ikke med i --dokumentene: {utenfor}"


def test_lytteren_noterer_en_aapning(request, tmp_path):
    """Ville feilet hvis lytteren i conftest.py ikke noterte et dokument som
    denne modulen åpner, så vakten over aldri kunne feile."""
    (dokumenttestene.ROT / "README.md").read_text(encoding="utf-8")
    aapnet = request.config.stash[dokumenttestene.AAPNET]
    assert "test_dokumenttestene.py" in aapnet
    assert any(fil.endswith("README.md") for fil in aapnet["test_dokumenttestene.py"])


def test_modulene_kan_leses():
    """Ville feilet hvis en testfil ikke kunne leses av ast, så modulene() ga
    en feil i stedet for en liste."""
    for sti in dokumenttestene.TESTMAPPA.glob("test_*.py"):
        ast.parse(sti.read_text(encoding="utf-8"))
