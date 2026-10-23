"""Story 3.5a: start med dobbeltklikk med uv, uten Docker (gruppens svar
23.10 kl. 16:16 og 16:37, spesifikasjonen spec-3-5a-dobbeltklikk-med-uv.md).

Testene leser skriptene, README-en og CI, og kjoerer ingenting: uten nett,
uten uv sync og uten webserver. Selve starten proeves i jobben dobbeltklikk
i .github/workflows/tester.yml, paa Windows og Mac.
"""

import re
import subprocess

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
    "uv run waitress-serve --listen=127.0.0.1:8000 app:app",
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


@pytest.mark.parametrize("navn", list(SKRIPTENE))
def test_den_ekte_versjonen_startes_bare_fra_main(navn):
    """Regel 22 (gjennomgangen, VG1 og ECH9). Ville feilet hvis den ekte
    versjonen kunne hente fra en gren i en klon med .git, slik at
    data/db/ose.db ble skrevet fra grenen."""
    kode = "\n".join(_kode(SKRIPTENE[navn]))
    vern = kode.index("git rev-parse --abbrev-ref HEAD")
    assert "main" in kode[vern : vern + 200] and "regel 22" in kode[vern : vern + 400]
    assert vern < kode.index("uv run python src/fetch_prices.py")


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


def test_ci_proever_demoen_paa_windows_og_mac_men_ikke_den_ekte():
    """Ville feilet hvis jobben dobbeltklikk manglet et av systemene, ikke
    ventet paa «Eksempeltall», eller kjoerte den ekte versjonen."""
    ci = CI.read_text(encoding="utf-8")
    jobb = ci.split("\n  dobbeltklikk:\n", 1)[1]
    assert "os: [windows-latest, macos-latest]" in jobb
    assert 'OSE_START_SVAR_JA: "1"' in jobb and 'OSE_START_UTEN_NETTLESER: "1"' in jobb
    assert "Start demoen.cmd" in jobb and "Start demoen.command" in jobb
    assert jobb.count("Eksempeltall") >= 2
    assert "Start den ekte versjonen" not in jobb
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
