"""Story 3.5a: start med dobbeltklikk med uv, uten Docker (gruppens svar
23.10 kl. 16:16 og 16:37, spesifikasjonen spec-3-5a-dobbeltklikk-med-uv.md).

Testene leser skriptene, README-en og CI, og kjoerer ingenting: uten nett,
uten uv sync og uten webserver. Selve starten proeves i jobben dobbeltklikk
i .github/workflows/tester.yml, paa Windows og Mac.
"""

import os
import re
import shutil
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
    server = kode.index("waitress-serve")
    assert sync < demo < ellers < henting < server
    assert kode.count("src/demo.py") == 1 and kode.count("src/fetch_prices.py") == 1


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_webserveren_binder_bare_127_0_0_1(navn):
    """Ville feilet hvis serveren lyttet paa 0.0.0.0, paa en annen adresse
    eller med --host, som binder til alle adresser (M1)."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    adressene = re.findall(r"--listen=([^\s'\"]+)", kode)
    assert adressene == ["127.0.0.1:8000"], adressene
    assert "0.0.0.0" not in kode and "--host" not in kode and "--port" not in kode


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
    assert "Se «Står du fast?» i README-en, eller docs/hjelp.md." in tekst
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


def _kjoer(argumenter, miljoe):
    """Kjoerer skriptet med «n» paa stdin, saa et spoersmaal om uv faar nei
    og ingenting installeres. Ingen uv paa PATH og en tom brukermappe, saa
    heller ikke en mutant kommer til uv sync eller hentingen."""
    svar = subprocess.run(
        argumenter,
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
        assert "System.Net.Sockets.TcpClient" in kode and "if (Opptatt) {" in kode
        assert "taskkill.exe /T /F /PID $script:server.Id" in kode
        assert kode.index("function Stopp([string]$Melding) {\nStopp-Serveren") >= 0
        assert "$null = $server.Handle" in kode and "if ($server.ExitCode -ne 0)" in kode
    else:
        assert "-w '%{http_code}'" in kode and "if opptatt; then" in kode
        assert "trap 'kill \"$server\" 2>/dev/null' EXIT" in kode
        assert "trap 'exit 130' INT TERM HUP" in kode
        assert '[ "$kode" = 0 ] || stopp "appen stoppet med kode $kode.' in kode


# Forproeven 24.10 (funn 4): ordene som sto med oe, aa og ae i det
# fetch_prices.py og demo.py skrev ut, foer 3.5d.
SKREVET_UTEN_AEOEAA = {
    "aa", "aapen", "aapnes", "aaret", "boers", "boersdag", "boersdagen", "boersdager", "boersen", "ennaa",
    "faa", "faar", "foer", "foerst", "foerste", "forsoek", "forsoeket", "inneveerende", "kjoer", "kjoeres",
    "kjoeringen", "laaser", "laast", "naa", "noekkelen", "oeyeblikksbilde", "oeyeblikksbildet", "paa",
    "paagikk", "proever", "proeves", "saa", "staar",
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


@pytest.mark.parametrize("fil", ["fetch_prices.py", "demo.py"])
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
