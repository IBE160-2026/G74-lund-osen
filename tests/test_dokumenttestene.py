"""Story 9.9: dokumenttestene (spec-9-9-dokumenttestene.md).

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


def test_en_test_uten_dokumentene_er_ikke_med():
    """Gjennomgangen (VG3): ville feilet hvis modulene() tok med alle
    testfilene, så kommandoen ble hele settet. test_ruff.py og
    test_tallformat.py leser ingen dokumenter."""
    assert not {"test_ruff.py", "test_tallformat.py"} & dokumenttestene.modulene()


def test_bare_koden_teller(tmp_path):
    """Ville feilet hvis en docstring eller en kommentar som nevner README-en
    gjorde en modul til en dokumenttest, eller en sti i koden ikke gjorde det."""
    _skriv(tmp_path, "test_nevner.py", '"""Se README-en og docs/hjelp.md."""\n# _bmad-output\nX = 1\n')
    _skriv(tmp_path, "test_leser.py", 'from pathlib import Path\nT = (Path("..") / "docs" / "hjelp.md")\n')
    _skriv(tmp_path, "test_readme_sti.py", 'T = open("README.md").read()\n')
    _skriv(tmp_path, "test_bmad.py", 'S = "_bmad-output/implementation-artifacts"\n')
    _skriv(tmp_path, "test_url.py", 'U = "https://docs.astral.sh/uv/"\n')
    # Gjennomgangen (BH1): en melding som nevner README-en, er ingen sti.
    _skriv(
        tmp_path,
        "test_melding.py",
        'def test_x(n):\n    assert n, "står ikke i README.md"\n    print(f"se {n} i docs/")\n',
    )
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


def test_utenfor_finner_en_modul_som_ikke_er_med():
    """Gjennomgangen (VG1): ville feilet hvis sammenligningen vakten gjør,
    ikke fant en modul som åpnet et dokument uten å være med, så vakten
    aldri kunne feile."""
    aapnet = {"test_med.py": {"README.md"}, "test_ute.py": {"d", "c", "b", "a"}}
    assert dokumenttestene.utenfor(aapnet, frozenset({"test_med.py"})) == {"test_ute.py": ["a", "b", "c"]}
    assert dokumenttestene.utenfor(aapnet, frozenset({"test_med.py", "test_ute.py"})) == {}


def _samlet(*argumenter):
    svar = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--dokumentene",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            *argumenter,
        ],
        cwd=dokumenttestene.ROT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert svar.returncode == 0, svar.stdout[-2000:] + svar.stderr[-2000:]
    return {
        linje.split("::")[0].replace(chr(92), "/").rsplit("/", 1)[-1]
        for linje in svar.stdout.splitlines()
        if "::" in linje
    }


def test_kommandoen_tar_ut_en_fil_paa_kommandolinja():
    """Gjennomgangen (ECH3): ville feilet hvis en fil gitt på kommandolinja
    ble kjørt med --dokumentene selv om den ikke leser dokumentene."""
    assert _samlet("tests/test_tallformat.py", "tests/test_readme.py") == {"test_readme.py"}


def test_kommandoen_kjoerer_bare_dokumenttestene():
    """Ville feilet hvis --dokumentene ikke fantes, eller samlet inn moduler
    som ikke leser dokumentene. Bare innsamlingen kjøres. Gjennomgangen
    (BH8): en modul som hoppes over på en maskintype, gir ingen linjer, så
    testen krever bare at ingen andre er med, og at de seks er det."""
    assert DE_SEKS <= _samlet() <= set(dokumenttestene.modulene())


def test_vakten_kjoeres_sist(request):
    """Ville feilet hvis vakten under ikke ble flyttet sist, så den ikke så
    modulene som kjører etter den."""
    navnene = [item.name for item in request.session.items]
    vakten = "test_ingen_test_som_leser_dokumentene_faller_utenfor"
    if vakten not in navnene:
        # Gjennomgangen (ECH2): valgt bort med -k eller kjørt alene.
        pytest.skip("vakten er ikke med i denne kjøringen")
    assert navnene[-1] == vakten


def test_ingen_test_som_leser_dokumentene_faller_utenfor(request):
    """Ville feilet hvis en testmodul åpnet README-en, docs/ eller
    _bmad-output/ i denne kjøringen uten å være med i --dokumentene, som
    test_aksjesiden_8_20a.py 08.11. Kjøres sist (conftest.py)."""
    andre = {item.path.name for item in request.session.items} - {"test_dokumenttestene.py"}
    if not andre:
        # Gjennomgangen (ECH1): med --lf eller alene har vakten ingenting å se.
        pytest.skip("ingen andre testmoduler i denne kjøringen")
    utenfor = dokumenttestene.utenfor(request.config.stash[dokumenttestene.AAPNET], dokumenttestene.modulene())
    assert not utenfor, (
        f"Leser dokumentene, men er ikke med i --dokumentene: {utenfor}. Står det ikke i koden til modulen, "
        "kan det komme fra src/, en fixture i conftest.py eller en import; før modulen i TILLEGG i "
        "tests/dokumenttestene.py (gjennomgangen, BH2, BH3, ECH5)."
    )


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
