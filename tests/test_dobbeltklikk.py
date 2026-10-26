"""Story 3.5a: start med dobbeltklikk med uv, uten Docker (gruppens svar
23.10 kl. 16:16 og 16:37, spesifikasjonen spec-3-5a-dobbeltklikk-med-uv.md).

Testene leser skriptene, README-en og CI, og kjoerer ingenting: uten nett,
uten uv sync og uten webserver. Selve starten proeves i jobben dobbeltklikk
i .github/workflows/tester.yml, paa Windows og Mac.
"""

import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from test_docker import CI, README, ROT, _hjelp
from test_ryddighet import UTEN_GIT, har_git

PS1 = ROT / "start" / "start.ps1"
SH = ROT / "start" / "start.sh"
SKRIPTENE = {"start.ps1": PS1, "start.sh": SH}
STARTFILENE = {
    "Start demoen.cmd": ("start\\start.ps1", "-Versjon demo"),
    "Start den ekte versjonen.cmd": ("start\\start.ps1", "-Versjon ekte"),
    "Start demoen.command": ("/start/start.sh", "demo"),
    "Start den ekte versjonen.command": ("/start/start.sh", "ekte"),
}
# Kommandoene skriptene kjoerer, slik README-en skriver dem.
KOMMANDOENE = [
    "uv sync",
    "uv run python src/demo.py",
    "uv run python src/fetch_prices.py",
    "uv run waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app",
]


def _kode(sti) -> list[str]:
    """Linjene i skriptet uten kommentarene og de tomme linjene."""
    linjer = []
    for linje in sti.read_text(encoding="utf-8-sig").splitlines():
        ren = linje.strip()
        if ren and not ren.startswith("#") and not ren.lower().startswith("rem "):
            linjer.append(ren)
    return linjer


def _delen_i_readme() -> str:
    tekst = README.read_text(encoding="utf-8")
    start = tekst.index("<summary>Start med dobbeltklikk, uten Docker</summary>")
    return tekst[start : tekst.index("</details>", start)]


def _kommandoene_i(navn: str) -> list[str]:
    """Kommandoene med uv i skriptet, i samme form som README-en. I start.ps1
    startes webserveren med Start-Process, med argumentene i en liste."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    funnet = re.findall(
        r"^(?:PYTHONPATH=src )?(uv (?:sync|run python \S+|run waitress-serve [^&\n]+?))\s*(?:\|\||&|$)", kode, re.M
    )
    for liste in re.findall(r"-FilePath 'uv' -ArgumentList ([^\n]+?) -NoNewWindow", kode):
        funnet.append("uv " + " ".join(re.findall(r"'([^']+)'", liste)))
    return [k.strip() for k in funnet]


@pytest.mark.parametrize("navn", list(STARTFILENE))
def test_startfilene_finnes_og_starter_riktig_skript(navn):
    """Ville feilet hvis en av de fire filene i rota manglet, eller startet
    feil skript eller feil versjon."""
    skript, versjon = STARTFILENE[navn]
    tekst = (ROT / navn).read_text(encoding="utf-8")
    assert skript in tekst and versjon in tekst, navn


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_skriptene_bruker_kommandoene_i_readme(navn):
    """Ville feilet hvis et skript kjoerte en kommando README-en ikke viser,
    manglet en av dem, eller README-en viste en annen."""
    del_ = _delen_i_readme()
    kommandoene = _kommandoene_i(navn)
    assert sorted(set(kommandoene)) == sorted(KOMMANDOENE), kommandoene
    for kommando in KOMMANDOENE:
        assert f"`{kommando}`" in del_, kommando


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_rekkefoelgen_demo_eller_henting_foer_serveren(navn):
    """Gjennomgangen (VG3). Ville feilet hvis hentingen kom etter at
    serveren startet, kjoerte i demoen, eller demo.py kjoerte i den ekte
    versjonen: demo.py, saa grenen for den ekte, saa hentingen, saa serveren."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    sync = kode.index("uv sync")
    demo = kode.index("uv run python src/demo.py")
    ellers = kode.index("else", demo)
    henting = kode.index("uv run python src/fetch_prices.py")
    server = kode.index("uv run waitress-serve" if "uv run waitress-serve" in kode else "'run', 'waitress-serve'")
    assert sync < demo < ellers < henting < server
    assert kode.count("src/demo.py") == 1 and kode.count("src/fetch_prices.py") == 1


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_webserveren_binder_bare_127_0_0_1(navn):
    """Ville feilet hvis serveren lyttet paa 0.0.0.0, paa en annen adresse
    eller med --host, som binder til alle adresser (M1)."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    # Spesifikasjonen 3.5d: bare linja som starter serveren, ikke sjekken av
    # kommandolinja paa porten.
    start = [l for l in kode.splitlines() if "uv run waitress-serve" in l or "-ArgumentList" in l]
    adressene = re.findall(r"--listen=([^\s'\"]+)", "\n".join(start))
    assert adressene == ["127.0.0.1:8000"], adressene
    assert len(start) == 1 and "0.0.0.0" not in kode and "--host" not in kode and "--port" not in kode


def test_webserveren_har_8_traader_i_skriptene_readme_og_dockerfile():
    """Forproeven 24.10 (funn 6, spesifikasjonen 3.5d). Ville feilet hvis
    webserveren startet med standarden paa 4 traader et sted, saa waitress
    skrev «Task queue depth» i vinduet."""
    for navn in SKRIPTENE:
        kode = "\n".join(_kode(SKRIPTENE[navn]))
        assert kode.count("--threads=8") == 1 and "--threads=" not in kode.replace("--threads=8", ""), navn
    assert "`uv run waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app`" in _delen_i_readme()
    dockerfile = (ROT / "Dockerfile").read_text(encoding="utf-8")
    assert 'CMD ["waitress-serve", "--listen=0.0.0.0:8000", "--threads=8", "app:app"]' in dockerfile


@pytest.mark.parametrize("navn", [*SKRIPTENE, *STARTFILENE])
def test_aldri_debug_eller_down_v(navn):
    """Ville feilet hvis et skript slo paa debug, for eksempel med
    FLASK_DEBUG eller src/app.py som skript, som har debug=True (M3), eller
    kjoerte docker compose down -v, som sletter basen."""
    sti = SKRIPTENE.get(navn, ROT / navn)
    kode = "\n".join(_kode(sti)).lower()
    assert "debug" not in kode, navn
    assert "src/app.py" not in kode and "app.run" not in kode, navn
    assert "down -v" not in kode and "--volumes" not in kode, navn


def test_noekkelen_leses_uten_aa_vises():
    """Ville feilet hvis noekkelen ble lest med ekko paa skjermen."""
    assert any("Read-Host" in l and "-AsSecureString" in l for l in _kode(PS1))
    assert any(re.match(r"read -r -s ", l) and "noekkel" in l for l in _kode(SH))


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_noekkelen_og_miljoeet_skrives_aldri_ut(navn):
    """Ville feilet hvis noekkelen ble skrevet ut (M2), eller hele miljoeet:
    noekkelen staar i det etter load_dotenv eller i CI. Noekkelen skrives bare
    til .env."""
    kode = _kode(SKRIPTENE[navn])
    ut = re.compile(
        r"\b(echo|printf|Write-Host|Write-Output|Write-Information|Out-Host|Out-File|Set-Content|Add-Content|tee|cat)\b"
        r"|>",
        re.I,
    )
    # Gjennomgangen (BH12, VG4): noekkelen faar ikke et nytt navn som kan
    # skrives ut i stedet.
    tekst = "\n".join(kode)
    assert not re.search(r"\$\w+\s*=\s*\$noekkel\b|\b(?!EODHD_API_KEY=)\w+=\"?\$noekkel\b", tekst), "noekkelen kopieres"
    assert not re.search(r"Write-\w+[^\n]*\$sikker|\$sikker[^\n]*\|", tekst)
    for linje in kode:
        if re.search(r"noekkel\b", linje, re.I) and ut.search(linje):
            assert ">> .env.ny" in linje or "WriteAllText" in linje, linje
        assert not re.search(r"(^|[;|&]\s*)(env|printenv|set)\s*($|[|>])", linje), linje
        assert not re.search(r"(Get-ChildItem|dir|ls|gci)\s+env:", linje, re.I), linje
        assert "GetEnvironmentVariables" not in linje and "export -p" not in linje, linje
        assert "declare -x" not in linje and "declare -p" not in linje, linje
        assert "set -x" not in linje and "Set-PSDebug" not in linje, linje
        # Variabelen leses aldri i skriptet, bare av fetch_prices.py fra .env.
        assert not re.search(r"\$(env:)?\{?EODHD_API_KEY", linje, re.I), linje
    assert "https://eodhd.com/register" in tekst


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_vinduet_sier_hvor_noekkelen_staar_og_hvordan_den_limes_inn(navn):
    """Forproeven 24.10 (funn 1–3, spesifikasjonen 3.5d). Ville feilet hvis
    vinduet ikke sa at noekkelen staar som «API token» under «Dashboard» med
    kopiknappen, ikke sa hvordan den limes inn paa systemet, eller sa at den
    ikke vises paa Windows, der Read-Host viser stjerner. Det samme staar i
    README-en og hjelpen."""
    meldinger = "\n".join(l for l in _kode(SKRIPTENE[navn]) if re.search(r"\b(Write-Host|Read-Host|echo|read -r)\b", l))
    assert "Nøkkelen står som «API token» under «Dashboard» hos EODHD, med kopiknappen til høyre." in meldinger
    if navn == "start.ps1":
        assert "Ctrl+V eller et høyreklikk" in meldinger and "Den vises som stjerner." in meldinger
        assert "vises ikke" not in meldinger and "Cmd+V" not in meldinger
    else:
        assert "Cmd+V" in meldinger and "Den vises ikke mens du limer inn" in meldinger
        assert "Ctrl+V" not in meldinger and "stjerner" not in meldinger
    for tekst in (_delen_i_readme(), _hjelp()):
        assert "«API token» under «Dashboard»" in tekst and "kopiknappen til høyre" in tekst
        assert "Ctrl+V eller et høyreklikk på Windows, og med Cmd+V på Mac" in tekst
        assert "På Windows vises den som stjerner" in tekst


def test_noekkelen_skrives_bare_til_env():
    """Ville feilet hvis noekkelen ble skrevet til en annen fil enn .env."""
    ps1 = "\n".join(_kode(PS1))
    assert re.search(r"WriteAllText\(\(Join-Path \(Get-Location\) '\.env'\)", ps1)
    sh = "\n".join(_kode(SH))
    assert "printf 'EODHD_API_KEY=%s\\n' \"$noekkel\" >> .env.ny" in sh
    assert "mv .env.ny .env" in sh


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_spoer_foer_uv_installeres(navn):
    """Ville feilet hvis skriptet installerte uv uten aa spoerre, eller med en
    annen installasjon enn den offisielle i README-en (svaret kl. 16:16)."""
    tekst = "\n".join(_kode(SKRIPTENE[navn]))
    readme = README.read_text(encoding="utf-8")
    installasjon = {
        "start.ps1": 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
        "start.sh": "curl -LsSf https://astral.sh/uv/install.sh | sh",
    }[navn]
    assert installasjon in readme
    assert tekst.index("Installere uv nå?") < tekst.index(installasjon)
    assert "OSE_START_SVAR_JA" in tekst
    # Gjennomgangen (VG5): bare j, ja, y og yes er ja, og et nei stopper
    # foer installasjonen.
    ja = {
        "start.ps1": "$svar -notmatch '^\\s*(j|ja|y|yes)\\s*$'",
        "start.sh": "j|J|ja|Ja|JA|y|Y|yes) ;;",
    }[navn]
    assert ja in tekst
    nei = tekst.index("stopp" if navn == "start.sh" else "Stopp", tekst.index(ja))
    assert nei < tekst.index(installasjon)


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_vinduet_sier_hvordan_man_stopper_paa_norsk(navn):
    """Ville feilet hvis vinduet ikke sa hvordan appen stoppes og hva man gjoer
    hvis noe feiler, eller æ, ø og å var borte."""
    tekst = SKRIPTENE[navn].read_text(encoding="utf-8-sig")
    assert "Lukk dette vinduet, eller trykk Ctrl+C, for å stoppe den." in tekst
    assert "Står det fortsatt fast, er det mer hjelp under «Start med dobbeltklikk» i docs/hjelp.md i mappa." in tekst
    # Gjennomgangen (BH11): i det vinduet sier, ikke i kommentarene.
    meldinger = [
        linje
        for linje in _kode(SKRIPTENE[navn])
        if re.search(r"\b(Write-Host|Read-Host|Stopp|echo|stopp|read -r)\b", linje)
    ]
    for bokstav in "æøå":
        assert any(bokstav in linje for linje in meldinger), bokstav
    assert any("Vinduet må være åpent mens appen kjører." in linje for linje in meldinger)


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_nettleseren_aapnes_etter_at_siden_svarer(navn):
    """Gjennomgangen (VG6). Ville feilet hvis nettleseren ble aapnet foer
    siden svarte, eller registreringssiden ble aapnet uten at noekkelen
    manglet."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    klar = kode.index("Appen kjører på")
    aapne = {"start.ps1": "Start-Process $Adresse", "start.sh": 'aapne "$ADRESSE"'}[navn]
    assert kode.count(aapne) == 1 and kode.index(aapne) > klar
    mangler = {
        "start.ps1": "if (-not $harNoekkel) {",
        "start.sh": "if ! grep -q '^EODHD_API_KEY=[^[:space:]]' .env; then",
    }[navn]
    lagret = kode.index("Nøkkelen er lagret i .env.")
    assert kode.index(mangler) < kode.index("https://eodhd.com/register") < lagret


VERNET = {
    "start.ps1": "if ($Versjon -eq 'ekte' -and (Test-Path -LiteralPath '.git')) {",
    "start.sh": 'if [ "$VERSJON" = "ekte" ] && [ -e .git ]; then',
}
# Beskjeden fra vernet, i begge skriptene (gjennomgangen 24.10, BH6).
BESKJEDEN = "mappa har .git (en klon av repoet eller et eget git-repo)"


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_den_ekte_versjonen_stopper_i_en_mappe_med_git(navn):
    """Gruppens svar 23.10 kl. 23:31 (b), som erstatter vernet «bare fra
    main» (VG1 og ECH9). Ville feilet hvis vernet sjekket grenen, saa den
    ekte versjonen kunne hente fra main i en klon med gruppens noekkel, ikke
    stoppet (gjennomgangen 24.10, BH8), eller kom etter uv, .env eller
    hentingen."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    vern = kode.index(VERNET[navn])
    blokken = kode[vern : kode.index("\n", kode.index("Download ZIP", vern))]
    assert "git rev-parse" not in kode and "main" not in blokken
    assert "Download ZIP" in blokken and "egen nøkkel" in blokken and BESKJEDEN in blokken
    assert blokken.splitlines()[1].startswith("Stopp '" if navn == "start.ps1" else 'stopp "')
    for senere in ("uv sync", ".env.example", "uv run python src/fetch_prices.py"):
        assert vern < kode.index(senere), senere
    # Foer uv-sjekken, ogsaa.
    assert vern < kode.index("Appen trenger uv")


def _mappe_med_skriptet(tmp_path, navn, git):
    """En mappe med bare skriptet, uten pyproject.toml og .env.example.
    git er "klon" (git init og en tom commit, saa HEAD er main, ikke en
    ufoedt gren; gjennomgangen 24.10, VG2), "fil" (.git som fil, som i en
    worktree; VG3) eller "ingen" (som en ZIP-fil). git er lokalt og gjoer
    ingen nettkall."""
    (tmp_path / "start").mkdir()
    (tmp_path / "start" / navn).write_bytes(SKRIPTENE[navn].read_bytes())
    if git == "klon":
        # Uten init -b, som krever git 2.28 (BH10, ECH2).
        subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
        git_c = ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run([*git_c, "symbolic-ref", "HEAD", "refs/heads/main"], check=True, capture_output=True)
        subprocess.run([*git_c, "commit", "-q", "--allow-empty", "-m", "t"], check=True, capture_output=True)
        gren = subprocess.run([*git_c, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        assert gren.stdout.strip() == "main", gren
    elif git == "fil":
        (tmp_path / ".git").write_text("gitdir: ../annen/.git/worktrees/kopi\n", encoding="utf-8")
    return tmp_path


def _porten_er_ledig() -> bool:
    """Om ingenting er bundet til port 8000 paa maskinen. Bind er ikke sperret
    av conftest, og ingenting kobles til. Paa Windows med SO_EXCLUSIVEADDRUSE,
    saa ogsaa en lytter paa 127.0.0.1 alene gjoer porten opptatt."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if sys.platform == "win32":
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        s.bind(("0.0.0.0", 8000))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _kjoer(argumenter, miljoe, sjekk_porten=True):
    """Kjoerer skriptet med «n» paa stdin, saa et spoersmaal om uv faar nei
    og ingenting installeres. Ingen uv paa PATH og en tom brukermappe, saa
    heller ikke en mutant kommer til uv sync eller hentingen.

    Spesifikasjonen 3.5d: skriptet stopper den andre versjonen av OSE Signal
    paa port 8000. Er porten opptatt paa maskinen, for eksempel av appen fra
    main, hoppes testen over, saa ingen test stopper den. Testene for 3.5e
    legger en falsk uv foerst paa PATH; den gjoer ingen nettkall."""
    if sjekk_porten and not _porten_er_ledig():
        pytest.skip("port 8000 er i bruk paa maskinen")
    # Gjennomgangen av 3.5d (BH1, ECH1): uten LOCALAPPDATA, ProgramData og
    # SystemDrive skrev Windows PowerShell cachen sin i mappa den sto i, og
    # det var repoet. Mappene ligger i tmp_path, og skriptet kjoeres derfra.
    hjem = Path(miljoe.get("USERPROFILE") or miljoe["HOME"])
    if sys.platform == "win32":
        miljoe = {
            **miljoe,
            "LOCALAPPDATA": str(hjem / "AppData" / "Local"),
            "APPDATA": str(hjem / "AppData" / "Roaming"),
            "ProgramData": str(hjem.parent / "ProgramData"),
            "SystemDrive": os.environ.get("SystemDrive", "C:"),
        }
    svar = subprocess.run(
        argumenter,
        cwd=hjem.parent,
        input="n\nn\nn\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=miljoe,
        timeout=120,
    )
    return svar.returncode, svar.stdout + svar.stderr


def _sjekk(git, mappe, kode, utskrift):
    """Med .git: stoppet av vernet, foer uv. Uten .git (kontrollen,
    gjennomgangen 24.10, BH5 og BH6): forbi vernet til spoersmaalet om uv,
    som faar nei, saa PATH og mappa ikke stopper skriptet foer vernet."""
    assert kode == 1, utskrift
    assert not (mappe / ".env").exists()
    if git == "ingen":
        assert "Appen trenger uv" in utskrift and BESKJEDEN not in utskrift, utskrift
    else:
        assert BESKJEDEN in utskrift and "Download ZIP" in utskrift and "egen nøkkel" in utskrift, utskrift
        assert "Appen trenger uv" not in utskrift, utskrift


def _bash():
    """bash, men ikke WSL-starteren i System32 eller WindowsApps paa Windows
    (gjennomgangen 24.10, ECH4)."""
    sti = shutil.which("bash")
    if sti and sys.platform == "win32" and ("system32" in sti.lower() or "windowsapps" in sti.lower()):
        return None
    return sti


def _uten_uv(stier):
    # Gjennomgangen 24.10 (ECH1): uv ved siden av bash eller git, for
    # eksempel i Homebrew, er en grunn til aa hoppe over, ikke en feil.
    if any((Path(s) / "uv").exists() or (Path(s) / "uv.exe").exists() for s in stier):
        pytest.skip("uv ligger i samme mappe som bash eller git")


@pytest.mark.skipif(_bash() is None or shutil.which("git") is None, reason="krever bash og git")
@pytest.mark.parametrize("git", ["klon", "fil", "ingen"])
def test_start_sh_stopper_den_ekte_versjonen_i_en_mappe_med_git(tmp_path, git):
    """Svaret 23.10 kl. 23:31 (b). Ville feilet hvis start.sh gikk videre
    fra en klon paa main, slik vernet «bare fra main» gjorde, eller fra en
    mappe med .git som fil: da spoer den om uv i stedet for aa vise til
    «Download ZIP», eller lager .env. Uten .git maa den komme forbi vernet."""
    mappe = _mappe_med_skriptet(tmp_path, "start.sh", git)
    stier = {str(Path(_bash()).parent), str(Path(shutil.which("git")).parent)}
    if shutil.which("dirname"):
        stier.add(str(Path(shutil.which("dirname")).parent))
    _uten_uv(stier)
    miljoe = {
        "PATH": os.pathsep.join(sorted(stier)),
        "HOME": str(tmp_path / "hjem"),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
    }
    kode, utskrift = _kjoer([_bash(), str(mappe / "start" / "start.sh"), "ekte"], miljoe)
    _sjekk(git, mappe, kode, utskrift)


@pytest.mark.skipif(sys.platform != "win32" or shutil.which("git") is None, reason="krever Windows PowerShell og git")
@pytest.mark.parametrize("git", ["klon", "fil", "ingen"])
def test_start_ps1_stopper_den_ekte_versjonen_i_en_mappe_med_git(tmp_path, git):
    """Svaret 23.10 kl. 23:31 (b). Ville feilet hvis start.ps1 gikk videre
    fra en klon paa main, slik vernet «bare fra main» gjorde, eller fra en
    mappe med .git som fil: da spoer den om uv i stedet for aa vise til
    «Download ZIP», eller lager .env. Uten .git maa den komme forbi vernet.
    PATH har ikke Windows PowerShell, saa installasjonen av uv ikke kan
    startes."""
    mappe = _mappe_med_skriptet(tmp_path, "start.ps1", git)
    systemrot = os.environ["SYSTEMROOT"]
    powershell = Path(systemrot) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    stier = [str(Path(shutil.which("git")).parent), str(Path(systemrot) / "System32")]
    _uten_uv(stier)
    miljoe = {
        "PATH": os.pathsep.join(stier),
        "USERPROFILE": str(tmp_path / "hjem"),
        "SYSTEMROOT": systemrot,
        "PSModulePath": "",
    }
    argumenter = [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
    kode, utskrift = _kjoer([*argumenter, str(mappe / "start" / "start.ps1"), "-Versjon", "ekte"], miljoe)
    _sjekk(git, mappe, kode, utskrift)


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_porten_sjekkes_for_alt_som_svarer_og_serveren_stoppes(navn):
    """Gjennomgangen (BH16, ECH7, BH3, ECH2, BH2). Ville feilet hvis bare
    200 talte som opptatt, serveren ble staaende etter en stopp, eller en
    server som stoppet av seg selv, lukket vinduet uten beskjed."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    if navn == "start.ps1":
        assert "System.Net.Sockets.TcpClient" in kode and "if (-not (Opptatt)) { return }" in kode
        assert "taskkill.exe /T /F /PID $script:server.Id" in kode
        assert kode.index("function Stopp([string]$Melding) {\nStopp-Serveren") >= 0
        assert "$null = $server.Handle" in kode and "if ($server.ExitCode -ne 0)" in kode
    else:
        # Spesifikasjonen 3.5d: /dev/tcp i bash, ikke curl.
        assert "(exec 3<>/dev/tcp/127.0.0.1/8000) 2>/dev/null" in kode and "opptatt || return 0" in kode
        assert "trap 'kill \"$server\" 2>/dev/null' EXIT" in kode
        assert "trap 'exit 130' INT TERM HUP" in kode
        assert '[ "$kode" = 0 ] || stopp "appen stoppet med kode $kode.' in kode


# Forproeven 24.10 (funn 4): ordene som sto med oe, aa og ae i det
# fetch_prices.py og demo.py skrev ut, foer 3.5d.
SKREVET_UTEN_AEOEAA = {
    "aa", "aapen", "aapnes", "aaret", "boers", "boersdag", "boersdagen", "boersdager", "boersen", "ennaa",
    "faa", "faar", "foer", "foerst", "foerste", "forsoek", "forsoeket", "inneveerende", "kjoer", "kjoeres",
    "kjoeringen", "laaser", "laast", "naa", "noekkelen", "oeyeblikksbilde", "oeyeblikksbildet", "paa",
    "paagikk", "proever", "proeves", "saa", "staar", "miljoeet", "gaar", "kjoering", "kjoerer",
}  # fmt: skip


def _tekstene_brukeren_ser(sti) -> list[tuple[int, str]]:
    """Strengene i fila, uten docstringene og filnavnene (-raa-, forsoek)."""
    import ast

    tre = ast.parse(sti.read_text(encoding="utf-8"))
    docstringer = {
        id(n.body[0].value)
        for n in ast.walk(tre)
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
        and n.body
        and isinstance(n.body[0], ast.Expr)
        and isinstance(n.body[0].value, ast.Constant)
    }
    return [
        (n.lineno, n.value)
        for n in ast.walk(tre)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and id(n) not in docstringer
        and n.value != "forsoek"
        and "-raa-" not in n.value
    ]


# Gjennomgangen av 3.5d (VG6): KI-tekstene hentingen skriver ut, med grunnen
# fra den lokale modellen og tjenestene.
@pytest.mark.parametrize("fil", ["fetch_prices.py", "demo.py", "ki_tekst.py", "ki_lokal.py", "ki_sky.py"])
def test_det_brukeren_ser_har_ae_oe_og_aa(fil):
    """Forproeven 24.10 (funn 4, spesifikasjonen 3.5d). Ville feilet hvis en
    melding eller hjelpetekst fra hentingen eller demoen skrev «paa»,
    «boersdagen» eller et annet ord med oe, aa eller ae i stedet for ø, å og
    æ. Filnavn som boersdag.py og -raa- teller ikke."""
    feil = []
    for linje, tekst in _tekstene_brukeren_ser(ROT / "src" / fil):
        for ord_ in re.findall(r"(?<![A-Za-z0-9_\-/.])[A-Za-z]+(?![A-Za-z0-9_\-/(]|\.py\b|\.json\b|\.db\b)", tekst):
            if ord_.lower() in SKREVET_UTEN_AEOEAA:
                feil.append((linje, ord_))
    assert not feil, feil


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_python_skriver_utf_8_ogsaa_til_en_fil(navn):
    """Forproeven 24.10 (funn 4). Ville feilet hvis skriptet ikke ba Python
    skrive UTF-8, saa æ, ø og å fra hentingen og demoen ble feil naar
    utskriften gaar til en fil, som i CI, foer uv sync."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    linja = {"start.ps1": "$env:PYTHONIOENCODING = 'utf-8'", "start.sh": "export PYTHONIOENCODING=utf-8"}[navn]
    assert kode.index(linja) < kode.index("uv sync")


def test_ci_krever_ae_oe_og_aa_i_utskriften_fra_start_demoen():
    """Forproeven 24.10 (funn 4). Ville feilet hvis jobben dobbeltklikk ikke
    krevde æ, ø og å i utskriften fra «Start demoen» paa Windows og Mac: ø fra
    demo.py, å fra demo.py og æ fra skriptet."""
    jobb = CI.read_text(encoding="utf-8").split("\n  dobbeltklikk:\n", 1)[1]
    for tekst in ("ikke data fra Oslo Børs", "aksjer på siste dag", "Vinduet må være åpent"):
        assert jobb.count(tekst) == 2, tekst
    assert "Get-Content -Raw -Encoding utf8 $logg" in jobb
    assert 'grep -qF "$t" "$RUNNER_TEMP/start-demoen.log"' in jobb
    demo = (ROT / "src" / "demo.py").read_text(encoding="utf-8")
    assert "ikke data fra Oslo Børs" in demo and "aksjer på siste dag" in demo


def test_start_ps1_har_bom():
    """Windows PowerShell 5.1 leser en fil uten BOM med tegnsettet til
    maskinen. Ville feilet hvis BOM-en ble borte, saa æ, ø og å ble feil."""
    assert PS1.read_bytes().startswith(b"\xef\xbb\xbf")


def test_gitattributes_gir_riktige_linjeskift():
    """Ville feilet hvis .cmd og .ps1 mistet CRLF eller .command og .sh LF i
    «Download ZIP»."""
    linjer = (ROT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    for linje in ("*.cmd text eol=crlf", "*.ps1 text eol=crlf", "*.command text eol=lf", "*.sh text eol=lf"):
        assert linje in linjer, linje


@pytest.mark.skipif(not har_git(ROT), reason=UTEN_GIT)
def test_command_filene_er_kjoerbare_i_git():
    """Ville feilet hvis .command-filene eller start.sh ikke var kjoerbare i
    git, saa Mac ikke kan starte dem med dobbeltklikk."""
    for navn in ("Start demoen.command", "Start den ekte versjonen.command", "start/start.sh"):
        svar = subprocess.run(["git", "-C", str(ROT), "ls-files", "-s", "--", navn], capture_output=True, text=True)
        assert svar.stdout.startswith("100755 "), (navn, svar.stdout)


def test_ci_proever_demoen_og_vernet_i_klonen_paa_windows_og_mac():
    """Ville feilet hvis jobben dobbeltklikk manglet et av systemene, ikke
    ventet paa «Eksempeltall», eller ikke krevde kode 1 og ingen .env av «Start
    den ekte versjonen» i klonen (svaret 23.10 kl. 23:31, b), foer demoen,
    eller ikke krevde beskjeden fra vernet, saa vernet «bare fra main» ogsaa
    gikk gjennom med loesrevet HEAD i en PR (gjennomgangen 24.10, VG1)."""
    ci = CI.read_text(encoding="utf-8")
    jobb = ci.split("\n  dobbeltklikk:\n", 1)[1]
    # Bare jobben, til neste jobb (gjennomgangen 24.10, BH9).
    jobb = re.split(r"\n  [a-z0-9_-]+:\n", jobb, maxsplit=1)[0]
    assert jobb.count("mappa har \\.git") == 2 and jobb.count("Download ZIP") == 2
    assert jobb.count("Appen trenger uv") == 2 and jobb.count("timeout-minutes: 5") == 2
    assert "os: [windows-latest, macos-latest]" in jobb
    assert 'OSE_START_SVAR_JA: "1"' in jobb and 'OSE_START_UTEN_NETTLESER: "1"' in jobb
    assert "Start demoen.cmd" in jobb and "Start demoen.command" in jobb
    assert jobb.count("Eksempeltall") >= 2
    windows = jobb.index("Start den ekte versjonen.cmd")
    mac = jobb.index("Start den ekte versjonen.command")
    assert windows < jobb.index("Start demoen.cmd") and mac < jobb.index("Start demoen.command")
    assert "if ($kode -ne 1)" in jobb and "Test-Path -LiteralPath '.env'" in jobb
    assert '[ "$kode" = 1 ]' in jobb and "[ ! -e .env ]" in jobb
    assert "EODHD_API_KEY" not in jobb and "secrets." not in jobb
    assert "setup-uv" not in jobb


def test_readme_og_hjelpen_har_advarselen_og_godkjenningen():
    """Ville feilet hvis advarselen fra Windows eller godkjenningen paa Mac
    manglet i README-en eller i docs/hjelp.md, eller «Kom i gang» nevnte
    skriptene foer gruppen har valgt hovedvei (svaret kl. 16:37)."""
    del_ = _delen_i_readme()
    assert "**Advarselen fra Windows.**" in del_ and "**Godkjenningen på Mac.**" in del_
    assert "nøkkelen fra EODHD første gang" in del_
    hjelp = _hjelp()
    assert "### Windows advarer mot fila." in hjelp and "### Mac sier at fila ikke kan åpnes." in hjelp
    tekst = README.read_text(encoding="utf-8")
    kom_i_gang = tekst.split("\n## Kom i gang\n", 1)[1].split("\n### Mer for den som vil\n", 1)[0]
    assert ".cmd" not in kom_i_gang and ".command" not in kom_i_gang
    assert "Start med dobbeltklikk" not in kom_i_gang


# Spesifikasjonen 3.5d (forproeven 24.10, funn 7, gruppens svar kl. 12:04):
# en lytter paa 127.0.0.1:8000. «oss» har kommandolinja fra skriptene og skal
# stoppes, «fremmed» har den ikke og skal kjoere videre. Lytteren er Python
# uten venv-omdirigeringen paa Windows, saa prosessen som lytter, er den testen
# startet.
LYTTEREN = (
    "import socket, sys, time\n"
    "s = socket.socket()\n"
    "s.bind(('127.0.0.1', 8000))\n"
    "s.listen()\n"
    "print('klar', flush=True)\n"
    "time.sleep(300)\n"
)
ARGUMENTENE = ["--listen=127.0.0.1:8000", "--threads=8", "app:app"]


def _waitress_serve(mappe, windows):
    """Stien til waitress-serve i .venv i mappa, slik uv starter den."""
    if windows:
        return str(mappe / ".venv" / "Scripts" / "waitress-serve.exe")
    return str(mappe / ".venv" / "bin" / "waitress-serve")


def _start_lytteren(hvem, mappe, windows):
    """«oss»: kommandolinja fra skriptene, med waitress-serve fra .venv i
    mappa. «annen_mappe»: den samme kommandolinja fra en annen mappe
    (gjennomgangen av 3.5d, BH3 og ECH2). «fremmed»: ingen av delene."""
    if not _porten_er_ledig():
        pytest.skip("port 8000 er i bruk paa maskinen")
    python = getattr(sys, "_base_executable", None) or sys.executable
    tillegg = {
        "oss": [_waitress_serve(mappe, windows), *ARGUMENTENE],
        "annen_mappe": [_waitress_serve(mappe.parent / "annen", windows), *ARGUMENTENE],
        "fremmed": [],
    }[hvem]
    lytter = subprocess.Popen(
        [python, "-c", LYTTEREN, *tillegg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    linja = lytter.stdout.readline().strip()
    if linja != "klar":
        # Gjennomgangen av 3.5d (ECH8): porten ble tatt etter sjekken.
        _stopp_lytteren(lytter)
        pytest.skip(f"lytteren startet ikke: {linja}")
    return lytter


def _stopp_lytteren(lytter):
    if lytter.poll() is None:
        lytter.kill()
    lytter.wait(timeout=30)


def _sjekk_porten(hvem, lytter, kode, utskrift):
    assert kode == 1, utskrift
    if hvem == "oss":
        # 3.5e (svaret 24.10 kl. 20:00): skriptet sier fra foer uv, som faar
        # nei, og den andre versjonen kjoerer videre, fordi den foerst stoppes
        # rett foer webserveren.
        assert "Den andre versjonen av OSE Signal kjører allerede på http://127.0.0.1:8000" in utskrift, utskrift
        assert f"(prosess {lytter.pid})" in utskrift, utskrift
        assert "Den stoppes rett før denne starter appen" in utskrift, utskrift
        assert "Appen trenger uv" in utskrift, utskrift
        assert "Den andre versjonen er stoppet" not in utskrift, utskrift
        assert lytter.poll() is None, "den andre versjonen ble stoppet foer uv"
    else:
        assert lytter.poll() is None, "den fremmede lytteren ble stoppet"
        assert "et annet program svarer allerede på http://127.0.0.1:8000" in utskrift, utskrift
        assert "python" in utskrift.lower() and f"(prosess {lytter.pid})" in utskrift, utskrift
        assert "Skriptet stopper aldri andre programmer." in utskrift, utskrift
        assert "docker compose --profile demo down" in utskrift and "Dobbeltklikk så på nytt." in utskrift
        assert "Den andre versjonen av OSE Signal" not in utskrift and "Appen trenger uv" not in utskrift
        assert "og det er ikke OSE Signal fra denne mappa." in utskrift, utskrift


@pytest.mark.skipif(sys.platform != "win32", reason="krever Windows PowerShell")
@pytest.mark.parametrize("hvem", ["oss", "annen_mappe", "fremmed"])
def test_start_ps1_stopper_bare_den_andre_versjonen_paa_porten(tmp_path, hvem):
    """Gruppens svar 24.10 kl. 12:04 og 20:00 (3.5e). Ville feilet hvis
    start.ps1 stoppet et annet program paa porten (mutanten: sjekken av
    kommandolinja borte), ikke sa hvilket program og hva man gjoer, eller
    stoppet den andre versjonen av OSE Signal foer uv i stedet for aa si fra
    og gaa videre (mutanten i 3.5e)."""
    mappe = _mappe_med_skriptet(tmp_path, "start.ps1", "ingen")
    systemrot = os.environ["SYSTEMROOT"]
    powershell = Path(systemrot) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    stier = [str(Path(systemrot) / "System32"), str(Path(systemrot) / "System32" / "Wbem")]
    _uten_uv(stier)
    miljoe = {"PATH": os.pathsep.join(stier), "USERPROFILE": str(tmp_path / "hjem"), "SYSTEMROOT": systemrot}
    miljoe["PSModulePath"] = ""
    lytter = _start_lytteren(hvem, mappe, windows=True)
    try:
        argumenter = [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
        argumenter += [str(mappe / "start" / "start.ps1"), "-Versjon", "demo"]
        kode, utskrift = _kjoer(argumenter, miljoe, sjekk_porten=False)
        _sjekk_porten(hvem, lytter, kode, utskrift)
    finally:
        _stopp_lytteren(lytter)


def _lsof():
    return shutil.which("lsof") or ("/usr/sbin/lsof" if Path("/usr/sbin/lsof").exists() else None)


@pytest.mark.skipif(sys.platform == "win32" or _bash() is None or _lsof() is None, reason="krever bash, lsof og ps")
@pytest.mark.parametrize("hvem", ["oss", "annen_mappe", "fremmed"])
def test_start_sh_stopper_bare_den_andre_versjonen_paa_porten(tmp_path, hvem):
    """Gruppens svar 24.10 kl. 12:04 og 20:00 (3.5e). Ville feilet hvis
    start.sh stoppet et annet program paa porten, ikke sa hvilket program og
    hva man gjoer, eller stoppet den andre versjonen av OSE Signal foer uv i
    stedet for aa si fra og gaa videre."""
    mappe = _mappe_med_skriptet(tmp_path, "start.sh", "ingen")
    stier = {str(Path(_bash()).parent)}
    for program in ("dirname", "ps", "grep", "sort", "sleep", "lsof"):
        if shutil.which(program):
            stier.add(str(Path(shutil.which(program)).parent))
    _uten_uv(stier)
    miljoe = {"PATH": os.pathsep.join(sorted(stier)), "HOME": str(tmp_path / "hjem")}
    lytter = _start_lytteren(hvem, mappe, windows=False)
    try:
        kode, utskrift = _kjoer([_bash(), str(mappe / "start" / "start.sh"), "demo"], miljoe, sjekk_porten=False)
        _sjekk_porten(hvem, lytter, kode, utskrift)
    finally:
        _stopp_lytteren(lytter)


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_porten_sjekkes_foer_uv_og_bare_oss_stoppes(navn):
    """Gruppens svar 24.10 kl. 12:04 og 20:00 (3.5e). Ville feilet hvis
    porten ble sjekket etter uv eller hentingen, den andre versjonen ble
    stoppet foer demobasen og hentingen i stedet for rett foer webserveren,
    eller skriptet stoppet lytterne uten aa sjekke kommandolinja foerst."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    kall, stoppen, sjekk, stopp_ = {
        "start.ps1": (
            "\nFrigjoer-Porten $false\n",
            "\nFrigjoer-Porten $true\n",
            "Er-OseSignal $_.Kommandolinje",
            "Stop-Process -Id $lytter.Id -Force",
        ),
        "start.sh": (
            "\nfrigjoer_porten sjekk\n",
            "\nfrigjoer_porten stopp\n",
            'er_ose_signal "$(ps -p "$id" -o command=',
            'kill "$id"',
        ),
    }[navn]
    assert kode.count(kall) == kode.count(stoppen) == 1
    assert kode.index(kall) < kode.index("Appen trenger uv") < kode.index("uv sync")
    assert kode.index(kall) < kode.index("uv run python src/fetch_prices.py") < kode.index(stoppen)
    serveren = {
        "start.ps1": "Start-Process -FilePath 'uv' -ArgumentList 'run', 'waitress-serve'",
        "start.sh": "uv run waitress-serve --listen",
    }[navn]
    assert kode.index("uv run python src/demo.py") < kode.index(stoppen) < kode.index(serveren)
    assert kode.index(sjekk) < kode.index("Skriptet stopper aldri andre programmer.") < kode.index(stopp_)
    # Gjennomgangen av 3.5d (VG1): delene staar i selve sjekken, ikke bare i
    # linja som starter serveren lenger ned.
    for del_ in ("waitress-serve", "--listen=127", "app:app", ".venv"):
        assert del_ in _sjekken(navn), del_


def _sjekken(navn) -> str:
    """Funksjonen som kjenner igjen kommandolinja, til foerste } paa egen linje."""
    tekst = SKRIPTENE[navn].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    start = tekst.index({"start.ps1": "function Er-OseSignal(", "start.sh": "er_ose_signal() {"}[navn])
    return tekst[start : tekst.index("\n}\n", start) + 3]


# Gjennomgangen av 3.5d (VG1, VG2): kommandolinjer og om de er OSE Signal fra
# mappa. MAPPE byttes med mappa skriptet staar i. Den foerste paa Windows har
# formen som ble slaatt opp 24.10 (spesifikasjonen 3.5d).
KOMMANDOLINJENE = {
    "start.ps1": [
        (
            r'"MAPPE\.venv\Scripts\python.exe" "MAPPE\.venv\Scripts\waitress-serve.exe" '
            "--listen=127.0.0.1:8000 --threads=8 app:app",
            True,
        ),
        (
            r'"MAPPE\.venv\Scripts\python.exe" "MAPPE\.venv\Scripts\waitress-serve.exe" --listen=127.0.0.1:8000 app:app',
            True,
        ),
        (r"MAPPE\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8000 --threads=8 app:app", True),
        (r"C:\annen\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8000 app:app", False),
        ("waitress-serve --listen=127.0.0.1:8000 app:app", False),
        (r"MAPPE\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8000 annen:app", False),
        (r"MAPPE\.venv\Scripts\waitress-serve.exe --listen=0.0.0.0:8000 app:app", False),
        (r"MAPPE\.venv\Scripts\waitress-serve.exe app:app", False),
        (r"python MAPPE\src\app.py", False),
        (r'"C:\Program Files\Docker\Docker\resources\com.docker.backend.exe"', False),
        ("", False),
    ],
    "start.sh": [
        ("MAPPE/.venv/bin/python3 MAPPE/.venv/bin/waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app", True),
        ("MAPPE/.venv/bin/python3 MAPPE/.venv/bin/waitress-serve --listen=127.0.0.1:8000 app:app", True),
        ("/annen/.venv/bin/python3 /annen/.venv/bin/waitress-serve --listen=127.0.0.1:8000 app:app", False),
        ("waitress-serve --listen=127.0.0.1:8000 app:app", False),
        ("MAPPE/.venv/bin/waitress-serve --listen=127.0.0.1:8000 annen:app", False),
        ("MAPPE/.venv/bin/waitress-serve --listen=0.0.0.0:8000 app:app", False),
        ("MAPPE/.venv/bin/waitress-serve app:app", False),
        ("python MAPPE/src/app.py", False),
        ("/Applications/Docker.app/Contents/MacOS/com.docker.backend", False),
        ("", False),
    ],
}

SJEKK_PS1 = """
$m = (Get-Location).ProviderPath
foreach ($l in [IO.File]::ReadAllLines((Join-Path $m 'linjer.txt'))) {
    if (Er-OseSignal ($l.Replace('MAPPE', $m))) { 'ja' } else { 'nei' }
}
"""

SJEKK_SH = """
m="$(pwd -P)"
while IFS= read -r l; do
    if er_ose_signal "${l//MAPPE/$m}"; then echo ja; else echo nei; fi
done < linjer.txt
"""


def _svar_fra_sjekken(navn, tmp_path):
    """Kjoerer sjekken alene, i en tom mappe, for hver kommandolinje."""
    linjene = "\n".join(linje for linje, _ in KOMMANDOLINJENE[navn]) + "\n"
    (tmp_path / "linjer.txt").write_bytes(linjene.encode("utf-8"))
    if navn == "start.ps1":
        (tmp_path / "sjekk.ps1").write_bytes(("\ufeff" + _sjekken(navn) + SJEKK_PS1).encode("utf-8"))
        systemrot = os.environ["SYSTEMROOT"]
        powershell = Path(systemrot) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        argumenter = [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(tmp_path / "sjekk.ps1")]
    else:
        (tmp_path / "sjekk.sh").write_bytes((_sjekken(navn) + SJEKK_SH).encode("utf-8"))
        argumenter = [_bash(), str(tmp_path / "sjekk.sh")]
    svar = subprocess.run(argumenter, cwd=tmp_path, capture_output=True, text=True, timeout=120)
    return svar.stdout.split(), svar.stderr


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_sjekken_kjenner_bare_igjen_waitress_fra_mappa(navn, tmp_path):
    """Gjennomgangen av 3.5d (VG1, VG2, BH3, ECH2). Ville feilet hvis sjekken
    ikke kjente igjen den ekte kommandolinja paa Windows, med sti i
    anfoerselstegn og .exe, eller kjente igjen en kommandolinje uten en av
    delene, med waitress-serve fra en annen mappe, med en annen app eller
    en annen adresse, slik at et annet program kunne blitt stoppet."""
    if navn == "start.ps1" and sys.platform != "win32":
        pytest.skip("krever Windows PowerShell")
    if navn == "start.sh" and _bash() is None:
        pytest.skip("krever bash")
    ut, feil = _svar_fra_sjekken(navn, tmp_path)
    forventet = ["ja" if ja else "nei" for _, ja in KOMMANDOLINJENE[navn]]
    assert ut == forventet, (ut, feil)


def _beskjedene(navn) -> list[str]:
    """Teksten i hvert kall til Stopp eller stopp, og i trap."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    return re.findall(r"\b[Ss]topp ('[^'\n]*'|\"[^\"\n]*\")", kode)


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_ingen_beskjed_viser_bare_til_readme(navn):
    """Forproeven 24.10 (funn 8, spesifikasjonen 3.5d). Ville feilet hvis en
    beskjed i vinduet bare viste til README-en, for eksempel «Installer uv
    slik «Tester» i README-en sier», i stedet for aa si hva man gjoer: hver
    beskjed sier at man dobbeltklikker paa nytt, eller laster ned en egen
    kopi."""
    beskjedene = _beskjedene(navn)
    assert len(beskjedene) >= 10, beskjedene
    for beskjed in beskjedene:
        assert "README" not in beskjed, beskjed
        assert "obbeltklikk" in beskjed or "Last ned en egen kopi" in beskjed, beskjed
    tekst = SKRIPTENE[navn].read_text(encoding="utf-8-sig")
    meldinger = [l for l in _kode(SKRIPTENE[navn]) if re.search(r"\b(Write-Host|echo)\b", l)]
    assert not any("README" in l for l in meldinger), [l for l in meldinger if "README" in l]
    assert "skriv j og trykk Enter når vinduet spør om uv" in tekst


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_vinduet_som_ble_stoppet_ber_ikke_om_et_nytt_dobbeltklikk_foerst(navn):
    """Gjennomgangen av 3.5d (BH2). Ville feilet hvis vinduet der appen ble
    stoppet av den andre versjonen, bare sa «dobbeltklikk på nytt», saa
    brukeren stoppet den nye versjonen igjen. Og hvis et program uten navn
    eller kommandolinje ga en tom plass i beskjeden (BH7, BH14)."""
    tekst = SKRIPTENE[navn].read_text(encoding="utf-8-sig")
    assert tekst.count("er det den som kjører nå, og dette vinduet kan lukkes.") == 1
    assert "appen stoppet med kode" in tekst.split("er det den som kjører nå", 1)[0].rsplit("\n", 1)[-1]
    if navn == "start.ps1":
        assert "kanskje startet som administrator" in tekst
        assert "if ($lyttere.Count -eq 0 -and -not (Opptatt)) { return }" in tekst
    else:
        assert '[ -n "$navn" ] || navn="et program skriptet ikke fant navnet på"' in tekst
        assert 'if [ -z "$ider" ] && ! opptatt; then return 0; fi' in tekst


def test_ci_proever_porten_paa_windows_og_mac():
    """Gjennomgangen av 3.5d (VG3). Ville feilet hvis porttestene og sjekken av
    kommandolinja bare kjoerte paa Linux i jobben pytest, saa Get-NetTCPConnection,
    Get-CimInstance, Stop-Process, lsof og ps aldri ble proevd paa Windows og
    Mac i CI."""
    jobb = CI.read_text(encoding="utf-8").split("\n  dobbeltklikk:\n", 1)[1]
    steget = jobb.split("- name: Porten på Windows og Mac", 1)[1]
    assert "os: [windows-latest, macos-latest]" in jobb
    assert "if: runner.os" not in steget.split("\n      - name:", 1)[0]
    assert 'uv run pytest -q -p no:cacheprovider -rs tests/test_dobbeltklikk.py -k "porten or sjekken"' in steget
    assert jobb.index("Start demoen på Mac") < jobb.index("Porten på Windows og Mac")


# Story 3.5e (svaret 24.10 kl. 20:00): en falsk uv, uten nett. Den skriver
# hvert steg og om porten var opptatt da, til loggen, og gaar ut med koden
# testen ber om. uv sync feiler med OSE_FALSK_UV_SYNC=1, hentingen feiler
# alltid, og webserveren gaar ut med 3 med en gang, saa skriptet stopper
# etter at porten er frigjort. Med OSE_FALSK_UV_FREMMED=1 starter uv sync et
# fremmed program paa porten og skriver prosessen til fremmed.pid.
FALSK_UV = (
    "import os, socket, subprocess, sys\n"
    "argumentene = sys.argv[1:]\n"
    "def opptatt():\n"
    "    s = socket.socket()\n"
    "    s.settimeout(2)\n"
    "    try:\n"
    "        s.connect(('127.0.0.1', 8000))\n"
    "        return 1\n"
    "    except OSError:\n"
    "        return 0\n"
    "    finally:\n"
    "        s.close()\n"
    "if argumentene[:1] == ['sync']:\n"
    "    steg = 'sync'\n"
    "elif 'src/demo.py' in argumentene:\n"
    "    steg = 'demo'\n"
    "elif 'src/fetch_prices.py' in argumentene:\n"
    "    steg = 'henting'\n"
    "elif 'waitress-serve' in argumentene:\n"
    "    steg = 'server'\n"
    "else:\n"
    "    steg = 'annet'\n"
    "with open(os.environ['OSE_FALSK_UV_LOGG'], 'a', encoding='utf-8') as logg:\n"
    "    logg.write(f'{steg} {opptatt()}\\n')\n"
    "if steg == 'sync' and os.environ.get('OSE_FALSK_UV_FREMMED') == '1':\n"
    "    ekstra = {'start_new_session': True} if os.name != 'nt' else {'creationflags': 0x00000200}\n"
    "    lytter = subprocess.Popen([sys.executable, '-c', os.environ['OSE_FALSK_UV_LYTTER']],\n"
    "        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, **ekstra)\n"
    "    lytter.stdout.readline()\n"
    "    with open(os.environ['OSE_FALSK_UV_PID'], 'w', encoding='utf-8') as fil:\n"
    "        fil.write(str(lytter.pid))\n"
    "koder = {'sync': int(os.environ.get('OSE_FALSK_UV_SYNC', '0')), 'henting': 1, 'server': 3}\n"
    "sys.exit(koder.get(steg, 0))\n"
)


def _falsk_uv(tmp_path, windows) -> Path:
    """Mappa med den falske uv, som uv.cmd paa Windows og uv ellers."""
    mappe = tmp_path / "falsk_uv"
    mappe.mkdir()
    (mappe / "falsk_uv.py").write_text(FALSK_UV, encoding="utf-8")
    python = getattr(sys, "_base_executable", None) or sys.executable
    if windows:
        (mappe / "uv.cmd").write_text(
            f'@"{python}" "{mappe / "falsk_uv.py"}" %*\r\n@exit /b %errorlevel%\r\n', encoding="utf-8"
        )
    else:
        uv = mappe / "uv"
        uv.write_text(f'#!/bin/sh\nexec "{python}" "{mappe / "falsk_uv.py"}" "$@"\n', encoding="utf-8")
        uv.chmod(0o755)
    return mappe


# Tilfellene: versjonen, om den andre versjonen kjoerer paa porten foerst,
# og miljoeet til den falske uv.
TILFELLENE_35E = {
    "uv_sync_feiler": ("demo", "oss", {"OSE_FALSK_UV_SYNC": "1"}),
    "hentingen_feiler": ("ekte", "oss", {}),
    "demoen": ("demo", "oss", {}),
    "fremmed_underveis": ("demo", None, {"OSE_FALSK_UV_FREMMED": "1"}),
}


def _drep(pid):
    try:
        os.kill(pid, 9 if os.name != "nt" else 15)
    except OSError:
        pass


def _kjoer_35e(tmp_path, navn, tilfelle):
    """Kjoerer skriptet med den falske uv og gir koden, utskriften, loggen,
    den andre versjonen og den fremmede prosessen, hvis noen."""
    windows = navn == "start.ps1"
    versjon, foerst, ekstra = TILFELLENE_35E[tilfelle]
    if not _porten_er_ledig():
        pytest.skip("port 8000 er i bruk paa maskinen")
    mappe = _mappe_med_skriptet(tmp_path, navn, "ingen")
    if versjon == "ekte":
        # Bare i tmp_path, og den falske uv henter ingenting.
        (mappe / ".env").write_text("EODHD_API_KEY=proeve\n", encoding="utf-8")
    falsk = _falsk_uv(tmp_path, windows)
    logg, pidfil = tmp_path / "uv.logg", tmp_path / "fremmed.pid"
    miljoe_uv = {
        "OSE_FALSK_UV_LOGG": str(logg),
        "OSE_FALSK_UV_PID": str(pidfil),
        "OSE_FALSK_UV_LYTTER": LYTTEREN,
        # Uten OSE_START_SVAR_JA, saa spoersmaalet om uv faar nei fra _kjoer
        # hvis den falske uv ikke blir funnet, og ingenting installeres.
        "OSE_START_UTEN_NETTLESER": "1",
        **ekstra,
    }
    if windows:
        systemrot = os.environ["SYSTEMROOT"]
        powershell = Path(systemrot) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        stier = [str(falsk), str(Path(systemrot) / "System32"), str(Path(systemrot) / "System32" / "Wbem")]
        miljoe = {"PATH": os.pathsep.join(stier), "USERPROFILE": str(tmp_path / "hjem"), "SYSTEMROOT": systemrot}
        # PATHEXT, saa Get-Command finner uv.cmd.
        miljoe["PSModulePath"], miljoe["PATHEXT"] = "", ".COM;.EXE;.BAT;.CMD"
        argumenter = [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
        argumenter += [str(mappe / "start" / "start.ps1"), "-Versjon", versjon]
    else:
        stier = {str(Path(_bash()).parent)}
        for program in ("dirname", "ps", "grep", "sort", "sleep", "lsof", "cp", "mv"):
            if shutil.which(program):
                stier.add(str(Path(shutil.which(program)).parent))
        miljoe = {"PATH": os.pathsep.join([str(falsk), *sorted(stier)]), "HOME": str(tmp_path / "hjem")}
        argumenter = [_bash(), str(mappe / "start" / "start.sh"), versjon]
    (tmp_path / "hjem").mkdir(exist_ok=True)
    lytter = _start_lytteren(foerst, mappe, windows) if foerst else None
    fremmed = None
    try:
        kode, utskrift = _kjoer(argumenter, {**miljoe, **miljoe_uv}, sjekk_porten=False)
        if pidfil.exists():
            fremmed = int(pidfil.read_text(encoding="utf-8"))
        linjene = logg.read_text(encoding="utf-8").split("\n")[:-1] if logg.exists() else []
        levde = lytter is not None and lytter.poll() is None
        return kode, utskrift, linjene, levde, fremmed
    finally:
        if lytter is not None:
            _stopp_lytteren(lytter)
        if pidfil.exists():
            _drep(int(pidfil.read_text(encoding="utf-8")))


def _sjekk_35e(tilfelle, kode, utskrift, linjene, levde, fremmed):
    assert kode == 1, utskrift
    stoppet = "Den andre versjonen er stoppet, og porten er ledig."
    beskjeden = "Den stoppes rett før denne starter appen"
    if tilfelle != "fremmed_underveis":
        # Gjennomgangen av 3.5e (BH, ECH): beskjeden kommer foer uv sync.
        assert utskrift.index(beskjeden) < utskrift.index("Installerer pakkene"), utskrift
    if tilfelle == "uv_sync_feiler":
        # Den andre versjonen kjoerte mens uv sync feilet, og kjoerer videre.
        # Vinduet sier at den kan holde .venv, ikke bare at nettet er grunnen.
        assert linjene == ["sync 1"], (linjene, utskrift)
        assert "kan holde filene i .venv åpne. Lukk vinduet der den kjører" in utskrift, utskrift
        assert "Sjekk at maskinen er koblet til nettet" not in utskrift, utskrift
        assert levde and stoppet not in utskrift, utskrift
    elif tilfelle == "fremmed_underveis":
        # Porten var ledig foer uv, og et fremmed program tok den under uv
        # sync. Det stoppes ikke, og vinduet sier hva man gjoer.
        assert fremmed is not None, utskrift
        assert linjene == ["sync 0", "demo 1"], (linjene, utskrift)
        assert "et annet program svarer allerede på http://127.0.0.1:8000" in utskrift, utskrift
        assert f"(prosess {fremmed})" in utskrift and "Dobbeltklikk så på nytt." in utskrift, utskrift
        assert "Starter appen" not in utskrift and stoppet not in utskrift, utskrift
    else:
        # Opptatt ved demobasen eller hentingen, ledig naar webserveren starter.
        midten = "demo" if tilfelle == "demoen" else "henting"
        assert linjene == ["sync 1", f"{midten} 1", "server 0"], (linjene, utskrift)
        assert not levde, utskrift
        assert "Den andre versjonen av OSE Signal (prosess " in utskrift and ") stoppes nå" in utskrift, utskrift
        assert utskrift.count("kjører allerede på http://127.0.0.1:8000") == 1, utskrift
        foer = "Lager demobasen." if tilfelle == "demoen" else "Hentingen gikk ut med kode 1"
        assert utskrift.index(foer) < utskrift.index(stoppet) < utskrift.index("Starter appen"), utskrift


@pytest.mark.skipif(sys.platform != "win32", reason="krever Windows PowerShell")
@pytest.mark.parametrize("tilfelle", list(TILFELLENE_35E))
def test_start_ps1_frigjoer_porten_rett_foer_webserveren(tmp_path, tilfelle):
    """Svaret 24.10 kl. 20:00 (3.5e). Ville feilet hvis start.ps1 stoppet den
    andre versjonen foer uv sync, demobasen eller hentingen, slik at den var
    borte naar uv sync feilet, ikke stoppet den rett foer webserveren, eller
    stoppet et program som tok porten underveis."""
    _sjekk_35e(tilfelle, *_kjoer_35e(tmp_path, "start.ps1", tilfelle))


@pytest.mark.skipif(sys.platform == "win32" or _bash() is None or _lsof() is None, reason="krever bash, lsof og ps")
@pytest.mark.parametrize("tilfelle", list(TILFELLENE_35E))
def test_start_sh_frigjoer_porten_rett_foer_webserveren(tmp_path, tilfelle):
    """Svaret 24.10 kl. 20:00 (3.5e). Ville feilet hvis start.sh stoppet den
    andre versjonen foer uv sync, demobasen eller hentingen, slik at den var
    borte naar uv sync feilet, ikke stoppet den rett foer webserveren, eller
    stoppet et program som tok porten underveis."""
    _sjekk_35e(tilfelle, *_kjoer_35e(tmp_path, "start.sh", tilfelle))
