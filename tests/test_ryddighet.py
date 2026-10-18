"""Ryddigheten i repoet - regel 10 i CLAUDE.md, raden «Ryddighet i repoet» i
docs/vurderingsmatrise.md.

To ting: .gitignore holder ute noeklene (.env og .env.*, men ikke
.env.example), rådata og basen (data/), de lokale testskriptene (local-tests/)
og den private arbeidsmappa (_privat/). Og ingenting av det er sporet i git.

Den foerste delen leser .gitignore selv, saa den gaar ogsaa uten git, for
eksempel i ZIP-fila som leveres. Naar git finnes, sjekkes tolkningen mot
`git check-ignore`. Den andre delen trenger git, og hoppes over uten.
Testene leser bare: de endrer verken .gitignore eller git-indeksen.

Story 9.8: skillene til BMAD ligger bare i .claude/skills/. Det finnes ingen
.agents/ i rotmappa, ingen fil under den er sporet i git, og manifestet til
BMAD har bare claude-code under ides. At en ny installasjon leser ides fra
manifestet, er ikke slaatt opp, siden installasjonskoden ikke ligger i repoet.
Kommer kopien tilbake, feiler testene for .agents/.
"""

import re
import shutil
import subprocess
from fnmatch import fnmatchcase
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
MANIFEST = ROT / "_bmad" / "_config" / "manifest.yaml"

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


def _flytliste(tekst: str) -> list[str]:
    """Verdiene i [a, b], uten anfoerselstegn."""
    inni = tekst.strip().lstrip("[").split("]")[0]
    return [v.strip().strip("'\"") for v in inni.split(",") if v.strip()]


def ides(manifest: str) -> list[str]:
    """Lista under ides: i manifestet til BMAD, lest som tekst til neste
    noekkel paa toppnivaa. Delen av YAML en installasjon kan skrive: en liste
    med eller uten innrykk, [a, b] paa en eller flere linjer, en enkelt verdi
    paa samme linje, kommentarer etter mellomrom eller tabulator, en BOM og
    dokumentskilleren ---."""
    verdier = []
    inne = False
    flyt = None
    for linje in manifest.lstrip("﻿").splitlines():
        linje = re.sub(r"(^|\s)#.*$", "", linje).rstrip()
        innhold = linje.strip()
        if flyt is not None:
            flyt += " " + innhold
            if "]" in innhold:
                verdier += _flytliste(flyt)
                flyt = None
            continue
        if not innhold or innhold in ("---", "..."):
            continue
        if not linje[0].isspace() and not innhold.startswith("-"):
            noekkel, _, resten = innhold.partition(":")
            inne = noekkel.strip().strip("'\"") == "ides"
            resten = resten.strip()
            if inne and resten.startswith("["):
                if "]" in resten:
                    verdier += _flytliste(resten)
                else:
                    flyt = resten
            elif inne and resten:
                verdier.append(resten.strip("'\""))
            continue
        if inne and innhold.startswith("-"):
            verdier.append(innhold[1:].strip().strip("'\""))
    if flyt is not None:
        verdier += _flytliste(flyt)
    return verdier


def test_det_finnes_ingen_agents_i_rotmappa():
    """Story 9.8 (BH3 i gjennomgangen): gaar ogsaa uten git, for eksempel i
    ZIP-fila. Ville feilet hvis en ny BMAD-installasjon la kopien for Codex i
    .agents/ igjen, ogsaa foer noen kjoerte git add."""
    assert not (ROT / ".agents").exists(), ".agents/ finnes i rotmappa"


@pytest.mark.skipif(not har_git(ROT), reason=UTEN_GIT)
def test_ingen_fil_under_agents_er_sporet():
    """Story 9.8: kopien for Codex er tatt ut. Ville feilet hvis en fil fra
    .claude/skills/ ble kopiert til .agents/ og lagt inn med git add (mutant
    S1), eller .agents ble lagt inn som en fil, en lenke eller en submodul
    (ECH3). Indeksen leses, saa en fil som er lagt inn, men ikke committet,
    teller ogsaa."""
    svar = _git("ls-files", "-z")
    assert svar.returncode == 0, svar.stderr
    sporet = [s for s in svar.stdout.split("\0") if s.lower() == ".agents" or s.lower().startswith(".agents/")]
    assert sporet == [], f"sporet under .agents/: {sporet[:5]} ({len(sporet)} i alt)"


def test_manifestet_har_bare_claude_code():
    """Story 9.8: manifestet oppgir bare Claude Code. Ville feilet hvis
    «- codex» kom tilbake under ides (mutant S2), eller lista var tom."""
    assert ides(MANIFEST.read_text(encoding="utf-8")) == ["claude-code"]


def test_ides_leses_i_formene_en_installasjon_skriver():
    """Ville feilet hvis lesingen bare saa listen med innrykk, slik at
    «- codex» uten innrykk, [claude-code, codex] paa en eller flere linjer
    (ECH1) eller «ides: codex» slapp gjennom, eller hvis en BOM, en kommentar
    etter tabulator eller --- ga en falsk verdi (ECH2)."""
    assert ides("modules:\n  - name: core\nides:\n  - claude-code\n  - codex\n") == ["claude-code", "codex"]
    assert ides("ides:\n- claude-code\n- codex\nandre: 1\n") == ["claude-code", "codex"]
    assert ides("ides: [claude-code, 'codex']\n") == ["claude-code", "codex"]
    assert ides("ides:\n  # - codex\n  - claude-code # vi\n") == ["claude-code"]
    assert ides("ides:\n  - claude-code\nmodules:\n  - name: codex\n") == ["claude-code"]
    assert ides("modules:\n  - name: core\n") == []
    assert ides("ides: [claude-code,\n  codex]\n") == ["claude-code", "codex"]
    assert ides("ides: [\n  claude-code,\n  codex,\n]\nandre: 1\n") == ["claude-code", "codex"]
    assert ides("ides: codex\n") == ["codex"]
    assert ides("ides: []\n") == []
    assert ides("﻿ides:\n  - claude-code\n") == ["claude-code"]
    assert ides("ides:\n  - claude-code\t# x\n---\n") == ["claude-code"]
    assert ides("ides:\r\n  - claude-code\r\n  - codex\r\n") == ["claude-code", "codex"]


def _avsnitt(tekst: str, overskrift: str) -> str:
    """Teksten under «## overskrift» til neste overskrift paa samme nivaa."""
    start = tekst.index(f"\n## {overskrift}\n")
    slutt = tekst.find("\n## ", start + 1)
    return tekst[start : slutt if slutt != -1 else None]


def test_mappestrukturen_nevner_bmad_og_claude_skills_ikke_agents():
    """Story 9.8, punkt c (VG5 i gjennomgangen). Ville feilet hvis
    «Mappestruktur» i README-en nevnte .agents/ igjen, eller ikke lenger
    nevnte _bmad/ og .claude/skills/ (regel 19)."""
    del_ = _avsnitt((ROT / "README.md").read_text(encoding="utf-8"), "Mappestruktur")
    assert "`_bmad/` og `.claude/skills/` — BMAD-rammeverket" in del_
    assert ".agents" not in del_


def test_lekkasjesjekken_unntar_ikke_agents():
    """Story 9.8, punkt c (VG5). Ville feilet hvis .agents/ kom tilbake i
    unntaket for .csv, .json og .jsonl i morgensjekken."""
    kilde = (ROT / ".github" / "scripts" / "morgensjekk.py").read_text(encoding="utf-8")
    unntak = re.findall(r'"\.jsonl"\) and not f\.startswith\(\(([^)]*)\)\)', kilde)
    assert unntak == ['".claude/", "_bmad/"']
    assert ".agents" not in kilde


NEXTJS = [".next/", "out/", ".vercel/", ".turbo/", "*.tsbuildinfo", "next-env.d.ts"]
NODE_LOGGER = ["npm-debug.log*", "yarn-debug.log*", "yarn-error.log*", ".pnpm-debug.log*"]
ENGELSKE_OVERSKRIFTER = [
    "# Next.js / Node",
    "# Python environments, bytecode, packaging and caches",
    "# Tests / coverage",
    "# Secrets and local environment; keep example files",
    "# BMAD: keep shared framework, skills, plans and documentation",
    "# Operating system / editors",
]


def test_gitignore_uten_nextjs_men_med_node_og_byggemappene():
    """Story 9.8, punkt e (VG7 i gjennomgangen). Ville feilet hvis et
    moenster for Next.js eller loggene for npm, yarn og pnpm kom tilbake, hvis
    node_modules/, dist/, build/ eller *.log ble tatt bort, eller hvis en av
    de engelske overskriftene fra malen kom tilbake."""
    linjer = [linje.strip() for linje in _gitignore().splitlines()]
    for moenster in NEXTJS + NODE_LOGGER + ENGELSKE_OVERSKRIFTER:
        assert moenster not in linjer, moenster
    for moenster in ("node_modules/", "dist/", "build/", "*.log"):
        assert moenster in linjer, moenster
    for sti in ("node_modules/x/y.js", "dist/ose.whl", "build/lib/x.py", "npm-debug.log", "yarn-error.log"):
        assert ignorert(_gitignore(), sti), sti


def test_env_example_har_variablene_koden_leser_og_kallene_en_henting_bruker():
    """Story 9.8, punkt f (VG9 i gjennomgangen). Variablene er EODHD_API_KEY
    (fetch_prices.py) og de ki_tekst.py leser fra .env, og kallene er ett per
    aksje og ett for hovedindeksen (behov i fetch_prices.kjoer). Ville
    feilet hvis en variabel kom til i koden uten aa staa i .env.example, eller
    hvis tallet paa variablene eller kallene i teksten ikke stemte."""
    from ki_tekst import _NOEKLER
    from kursdata import AKSJEUNIVERS

    tekst = (ROT / ".env.example").read_text(encoding="utf-8")
    variabler = ("EODHD_API_KEY", *_NOEKLER)
    for navn in variabler:
        assert re.search(rf"^#? ?{navn}=", tekst, re.MULTILINE), navn
    tall = {3: "tre"}
    assert f"Det er {tall[len(variabler)]} variabler aa sette i .env" in tekst
    assert f"bruker {len(AKSJEUNIVERS) + 1} av de 20 kallene" in tekst
