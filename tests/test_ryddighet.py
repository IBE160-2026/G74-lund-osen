"""Ryddigheten i repoet - regel 10 i CLAUDE.md, raden «Ryddighet i repoet» i
docs/vurderingsmatrise.md.

To ting: .gitignore holder ute noeklene (.env og .env.*, men ikke
.env.example), rådata og basen (data/), de lokale testskriptene (local-tests/)
og den private arbeidsmappa (_privat/). Og ingenting av det er sporet i git.

Den foerste delen leser .gitignore selv, saa den gaar ogsaa uten git, for
eksempel i ZIP-fila som leveres. Naar git finnes, sjekkes tolkningen mot
`git check-ignore`. Den andre delen trenger git, og hoppes over uten.
Testene leser bare: de endrer verken .gitignore eller git-indeksen.
"""

import shutil
import subprocess
from fnmatch import fnmatchcase
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent

# Stier som skal holdes ute. Filene trenger ikke finnes.
HOLDES_UTE = [
    ".env",
    ".env.local",
    ".env.production",
    "data/db/ose.db",
    "data/db/demo.db",
    "data/raa/kurser-raa-2026-10-15.json",
    "local-tests/proeve.py",
    "_privat/utkast.md",
]
# Stier som skal kunne spores. docs/data er en fil, ikke en mappe: data/
# gjelder bare mapper (mutant R14).
SPORES = [".env.example", "src/app.py", "docs/vurderingsmatrise.md", "docs/data"]

UTEN_GIT = "ingen git her (for eksempel ZIP-fila som leveres), saa det som er sporet, kan ikke sjekkes"
UTEN_GIT_TOLKNING = "ingen git her (for eksempel ZIP-fila som leveres), saa tolkningen sjekkes ikke mot git"


def _monstre(tekst: str) -> list[tuple[str, bool, bool, bool]]:
    """(moenster, negert, bare mapper, forankret) for hver linje i .gitignore.
    Delen av formatet .gitignore i repoet bruker: kommentarer, !, en / til
    slutt for mapper, en / foran eller inni for forankring, og * og ?."""
    monstre = []
    for linje in tekst.splitlines():
        linje = linje.rstrip()
        if not linje or linje.startswith("#"):
            continue
        negert = linje.startswith("!")
        if negert:
            linje = linje[1:]
        mappe = linje.endswith("/")
        linje = linje.rstrip("/")
        forankret = "/" in linje
        monstre.append((linje.lstrip("/"), negert, mappe, forankret))
    return monstre


def ignorert(gitignore: str, sti: str) -> bool:
    """Holder .gitignore stien ute? Det siste moensteret som treffer, vinner,
    og er en mappe over stien holdt ute, kan ingenting under den slippes inn
    igjen (som i git)."""
    monstre = _monstre(gitignore)
    deler = sti.split("/")
    for k in range(1, len(deler) + 1):
        del_sti = "/".join(deler[:k])
        er_mappe = k < len(deler)
        holdt_ute = False
        for moenster, negert, bare_mapper, forankret in monstre:
            if bare_mapper and not er_mappe:
                continue
            maal = del_sti if forankret else deler[k - 1]
            if fnmatchcase(maal, moenster):
                holdt_ute = not negert
        if holdt_ute and er_mappe:
            return True
        if k == len(deler):
            return holdt_ute
    return False


def har_git(rot: Path) -> bool:
    return shutil.which("git") is not None and (rot / ".git").exists()


def _git(*argumenter: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROT), *argumenter], capture_output=True, text=True)


def _gitignore() -> str:
    return (ROT / ".gitignore").read_text(encoding="utf-8")


@pytest.mark.parametrize("sti", HOLDES_UTE)
def test_gitignore_holder_ute_noekler_data_og_private_mapper(sti):
    assert ignorert(_gitignore(), sti), f"{sti} holdes ikke ute av .gitignore"


@pytest.mark.parametrize("sti", SPORES)
def test_gitignore_slipper_inn_env_example_og_koden(sti):
    assert not ignorert(_gitignore(), sti), f"{sti} holdes ute av .gitignore"


@pytest.mark.skipif(not har_git(ROT), reason=UTEN_GIT_TOLKNING)
@pytest.mark.parametrize("sti", HOLDES_UTE + SPORES)
def test_tolkningen_stemmer_med_git(sti):
    """Tolkningen over sjekkes mot git selv, saa testen ikke hviler paa en
    egen feil i tolkningen. --no-index: det som er sporet, sjekkes under."""
    svar = _git("check-ignore", "--no-index", "-q", sti)
    assert svar.returncode in (0, 1), svar.stderr
    assert (svar.returncode == 0) == ignorert(_gitignore(), sti)


def _skal_ikke_spores(sti: str) -> bool:
    deler = sti.split("/")
    navn = deler[-1]
    if deler[0] in ("data", "local-tests", "_privat"):
        return True
    return navn == ".env" or (navn.startswith(".env.") and not navn.endswith(".example"))


@pytest.mark.skipif(not har_git(ROT), reason=UTEN_GIT)
def test_ingenting_av_det_er_sporet_i_git():
    svar = _git("ls-files", "-z")
    assert svar.returncode == 0, svar.stderr
    sporet = [sti for sti in svar.stdout.split("\0") if sti and _skal_ikke_spores(sti)]
    assert sporet == [], f"sporet i git, men skal holdes ute: {sporet}"


def test_git_brukes_naar_det_finnes():
    """Hoppes delen over i et repo med git, sjekkes ingenting. Ville feilet
    hvis har_git alltid sa nei."""
    if (ROT / ".git").exists() and shutil.which("git"):
        assert har_git(ROT)
    assert not har_git(ROT / "finnes-ikke")


def test_hvilke_stier_som_ikke_skal_spores():
    """Filteret for det som er sporet, uten git."""
    for sti in ("data/db/ose.db", "local-tests/x.py", "_privat/x.md", ".env", ".env.local", "src/.env"):
        assert _skal_ikke_spores(sti), sti
    for sti in (".env.example", ".env.prod.example", "src/app.py", "docs/data.md", "src/lagring_fil.py"):
        assert not _skal_ikke_spores(sti), sti
