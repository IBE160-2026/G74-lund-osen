"""Story 2.3d: hentingen som jobb i Oppgaveplanlegging (gruppens svar 26.10
kl. 22:58 og 27.10 kl. 20:58, spesifikasjonen
spec-2-3d-hentingen-hver-kveld.md).

Testene leser skriptene i start/, og paa Windows kjoerer de
start/kveldshenting.ps1 i en midlertidig mappe: et lokalt repo som origin, en
hovedkopi og jobbens arbeidskopi med git worktree. Ingen nettkall, ingen
Docker og ingen ekte uv: PATH har en falsk docker og en falsk uv foerst, saa
git og System32.
legg-inn-kveldshentingen.ps1 og ta-bort-kveldshentingen.ps1 kjoeres aldri,
saa ingen jobb legges inn i Oppgaveplanlegging.
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from test_docker import README, ROT, _hjelp

JOBBEN = ROT / "start" / "kveldshenting.ps1"
LEGG_INN = ROT / "start" / "legg-inn-kveldshentingen.ps1"
TA_BORT = ROT / "start" / "ta-bort-kveldshentingen.ps1"
SKRIPTENE = [JOBBEN, LEGG_INN, TA_BORT]
NAVNET = "OSE Signal kveldshenting"
NOEKKELEN = "proevenoekkel-som-aldri-skal-skrives-ut-7f3a"
MILJOEET = "proevemiljoe-som-aldri-skal-skrives-ut-91c2"


def _kode(sti: Path) -> str:
    """Skriptet uten kommentarene og de tomme linjene."""
    linjer = []
    for linje in sti.read_text(encoding="utf-8-sig").splitlines():
        ren = linje.strip()
        if ren and not ren.startswith("#"):
            linjer.append(ren)
    return "\n".join(linjer)


@pytest.mark.parametrize("sti", SKRIPTENE, ids=lambda s: s.name)
def test_skriptene_har_bom_og_crlf_i_gitattributes(sti):
    """Ville feilet hvis Windows PowerShell 5.1 leste æ, ø og å feil, som i
    start.ps1 uten BOM."""
    assert sti.read_bytes().startswith(b"\xef\xbb\xbf")
    assert "*.ps1 text eol=crlf" in (ROT / ".gitattributes").read_text(encoding="utf-8")


@pytest.mark.parametrize("sti", SKRIPTENE, ids=lambda s: s.name)
def test_skriptene_skriver_ikke_ut_noekkelen_eller_miljoeet(sti):
    """Ville feilet hvis et skript skrev ut nøkkelen eller miljøet: ingen
    linje nevner EODHD_API_KEY, lister miljøet eller leser .env som tekst.
    .env leses bare som avtrykk (Get-FileHash) og som fil (Get-Item)."""
    kode = _kode(sti)
    assert "EODHD_API_KEY" not in kode
    for moenster in (
        r"(?i)\b(Get-ChildItem|gci|dir|ls|Get-Item|gi)\s+env:",
        r"(?i)GetEnvironmentVariables",
        r"(?i)\$env:\w*\s*$",
        r"(?i)Start-Transcript",
        r"(?i)\bSet\s*$",
    ):
        assert not re.search(moenster, kode, re.MULTILINE), moenster
    for linje in kode.splitlines():
        # Gjennomgangen (VG6): .env leses gjennom $envHoved og $envJobb.
        if ".env" in linje or "$envHoved" in linje or "$envJobb" in linje:
            assert not re.search(r"(?i)Get-Content|\bcat\b|\btype\b|ReadAllText|Select-String", linje), linje


def test_jobben_bruker_commiten_fra_midnatt_paa_origin_main():
    """Ville feilet hvis jobben brukte en nyere commit enn den main hadde ved
    midnatt (origin/main, HEAD eller en gren), eller sto paa en gren."""
    kode = _kode(JOBBEN)
    assert "$midnatt = ([DateTimeOffset]::new((Get-Date).Date)).ToString('yyyy-MM-ddTHH:mm:sszzz')" in kode
    assert "rev-list -1 --first-parent --before=$midnatt origin/main" in kode
    assert "checkout --quiet --detach $commit" in kode
    assert "symbolic-ref -q HEAD" in kode
    satt = [linje for linje in kode.splitlines() if linje.startswith("$commit =")]
    assert satt == [
        '$commit = "$(Kjoer-Git -C $Arbeidskopi rev-list -1 --first-parent --before=$midnatt origin/main)".Trim()'
    ]


def test_jobben_henter_uten_flagg_og_bare_med_ki_som_svarer():
    """Ville feilet hvis jobben hentet med andre innstillinger enn
    instruksjonene (steg 4), eller med KI-tekst uten at Ollama svarte
    (NFR-04)."""
    kode = _kode(JOBBEN)
    assert "& $uvSti run python src/fetch_prices.py 2>&1" in kode
    assert "--uten-tidskontroll" not in kode and "--les-inn" not in kode
    assert "$env:OSE_KI_TJENESTE = 'lokal'" in kode and "$env:OSE_KI_OLLAMA_URL = $OllamaUrl" in kode
    assert "$env:OSE_KI_TJENESTE = 'av'" in kode
    assert kode.index("if ($kiKlar) {") < kode.index("$env:OSE_KI_TJENESTE = 'lokal'")
    assert "$OllamaUrl = 'http://127.0.0.1:11434'" in kode
    assert "exit $kode" in kode.splitlines()[-1]


def test_jobben_maaler_omsetningen_etter_hentingen_i_hver_kjoering():
    """Ville feilet hvis jobben ikke kjoerte maalingen etter hentingen, bare
    kjoerte den naar hentingen ga kode 0, eller lot koden fra maalingen bli
    koden jobben avslutter med (story 2.13, avgjoerelsen 28.10 kl. 22:17)."""
    kode = _kode(JOBBEN)
    hentingen = kode.index("& $uvSti run python src/fetch_prices.py 2>&1")
    maalingen = kode.index("& $uvSti run python src/fetch_prices.py --maal-omsetning 2>&1")
    assert hentingen < kode.index("$kode = $LASTEXITCODE") < maalingen
    assert kode.count("$kode = $LASTEXITCODE") == 1
    mellom = kode[hentingen:maalingen]
    assert "if (" not in mellom and "exit" not in mellom
    # Gjennomgangen (VG10): $kode settes ikke igjen etter maalingen, utenom i
    # catch for en uventet feil.
    assert "$kode" not in kode[maalingen : kode.index("} catch {", maalingen)]
    assert re.search(r"\bif\s*\(", mellom) is None
    assert 'Logg "Målingen avsluttet med kode $LASTEXITCODE."' in kode


def test_modellen_er_den_samme_som_i_ki_lokal():
    """Ville feilet hvis jobben ventet paa en annen modell enn den hentingen
    bruker."""
    modell = re.search(r'^MODELL = "([^"]+)"', (ROT / "src" / "ki_lokal.py").read_text(encoding="utf-8"), re.M)
    assert f"$Modell = '{modell.group(1)}'" in _kode(JOBBEN)


def test_bare_det_skriptet_startet_stoppes():
    """Ville feilet hvis jobben stoppet Docker Desktop eller Ollama som
    kjoerte fra foer, eller fjernet containeren og volumet."""
    kode = _kode(JOBBEN)
    assert (
        "if ($startetOllama) {\nLogg 'Stopper Ollama.'\n$null = Kjoer-Med-Grense $docker.Source @('compose', '--profile', 'ki', 'stop', 'ollama') 120"
        in kode
    )
    assert "if ($startetDocker) {\nLogg 'Stopper Docker Desktop.'" in kode
    assert kode.count("$startetOllama = $true") == 1 and kode.count("$startetDocker = $true") == 1
    assert not re.search(
        r"(?i)Stop-Process|compose (--profile \w+ )?down|\brm\b|kill", kode.replace("taskkill.exe", "")
    )


def _tidene() -> list[str]:
    """Klokkeslettene jobben starter, regnet ut fra legg-inn-skriptet."""
    kode = _kode(LEGG_INN)
    start = re.findall(r"\$dato\.Date\.AddHours\((\d+)\)\.AddMinutes\((\d+)\)", kode)
    assert len(start) == 3 and len(set(start)) == 1, start
    intervall = re.search(r"-RepetitionInterval \(New-TimeSpan -Minutes (\d+)\)", kode)
    varighet = re.search(r"-RepetitionDuration \(New-TimeSpan -Hours (\d+) -Minutes (\d+)\)", kode)
    foerste = int(start[0][0]) * 60 + int(start[0][1])
    lengde = int(varighet.group(1)) * 60 + int(varighet.group(2))
    steg = int(intervall.group(1))
    return [f"{(foerste + n) // 60:02d}:{(foerste + n) % 60:02d}" for n in range(0, lengde, steg)]


def test_jobben_gaar_hver_dag_fra_22_15_hver_halvtime_til_23_45():
    """Ville feilet hvis jobben hadde andre tider enn i instruksjonen (punkt b):
    hver dag kl. 22:15, igjen hver halvtime til 23:45, ingen ny kjoering mens
    en gaar (ECH3), tapte kjoeringer tas ikke igjen, og foerste dato som valg."""
    assert _tidene() == ["22:15", "22:45", "23:15", "23:45"]
    kode = _kode(LEGG_INN)
    assert "New-ScheduledTaskTrigger -Daily -At $dato.Date.AddHours(22).AddMinutes(15)" in kode
    assert not re.search(r"(?i)-Weekly|-DaysOfWeek|-DaysInterval|-AtLogOn|-AtStartup", kode)
    assert "-MultipleInstances IgnoreNew" in kode
    assert "$innstillinger.StartWhenAvailable = $false" in kode and "-StartWhenAvailable" not in kode
    assert "-WakeToRun" not in kode
    # Gjennomgangen (ECH2, ECH3, VG5): lokal tid uten Z, ingen stopp ved
    # slutten av gjentakelsen, og jobben bare med brukeren logget inn.
    assert "$utloeser.StartBoundary = $dato.Date.AddHours(22).AddMinutes(15).ToString('yyyy-MM-ddTHH:mm:ss')" in kode
    assert "$utloeser.Repetition.StopAtDurationEnd = $false" in kode
    assert "-ExecutionTimeLimit (New-TimeSpan -Hours 1)" in kode
    assert "-LogonType Interactive -RunLevel Limited" in kode
    assert "[string]$FoersteDato = (Get-Date).ToString('yyyy-MM-dd')" in kode
    assert "TryParseExact($FoersteDato, 'yyyy-MM-dd'" in kode


def test_jobben_starter_skriptet_i_arbeidskopien_med_hovedkopien_som_argument():
    """Ville feilet hvis jobben startet skriptet i hovedkopien, eller
    innleggingen godtok hovedkopien som arbeidskopi."""
    kode = _kode(LEGG_INN)
    assert "$Skript = Join-Path $Arbeidskopi 'start\\kveldshenting.ps1'" in kode
    assert '-File `"$Skript`" -Hovedkopi `"$Hovedkopi`"' in kode
    assert "if ($Arbeidskopi -eq $Hovedkopi) {" in kode
    assert "-WorkingDirectory $Arbeidskopi" in kode


def test_jobbnavnet_er_det_samme_i_begge_skriptene():
    """Ville feilet hvis ta-bort-skriptet lette etter en annen jobb enn den
    som ble lagt inn."""
    for sti in (LEGG_INN, TA_BORT):
        assert f"$Navn = '{NAVNET}'" in _kode(sti)
    assert "Unregister-ScheduledTask -TaskName $Navn -Confirm:$false" in _kode(TA_BORT)


def test_readme_og_hjelpen_sier_hva_jobben_gjoer_loggen_og_hvordan_den_slaas_av():
    """Ville feilet hvis README-en eller docs/hjelp.md ikke sa hva jobben
    gjoer, hvor loggen er, og hvordan den slaas av (regel 19)."""
    readme = README.read_text(encoding="utf-8")
    hjelp = _hjelp()
    for tekst in (readme, hjelp):
        assert "data/logg/kveldshenting-" in tekst
        assert "ta-bort-kveldshentingen.ps1" in tekst
        assert "22:15" in tekst and "23:45" in tekst
    assert "legg-inn-kveldshentingen.ps1" in readme
    assert "commiten main hadde ved midnatt" in readme
    for tekst in (readme, hjelp):
        assert "--maal-omsetning" in tekst and "bonuskvoten" in tekst


# Kjoeringen paa Windows, i en midlertidig mappe.


def _git(mappe: Path, *argumenter: str, dato: str | None = None) -> str:
    miljoe = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t"}
    miljoe |= {"GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    if dato:
        miljoe |= {"GIT_AUTHOR_DATE": dato, "GIT_COMMITTER_DATE": dato}
    svar = subprocess.run(["git", "-C", str(mappe), *argumenter], capture_output=True, text=True, env=miljoe)
    assert svar.returncode == 0, svar
    return svar.stdout.strip()


def _oppsett(tmp_path: Path, start: str, etter: str = "") -> dict[str, Path | str]:
    """origin (bart repo), hovedkopien og jobbens arbeidskopi. Commiten fra
    i gaar kl. 12 er siste foer midnatt; commiten fra naa kom etter. start er
    "gren" (arbeidskopien paa en egen gren med en nyere commit) eller
    "nyeste" (løsrevet paa commiten fra naa). etter er "skriptet endret"
    (commiten fra naa har en annen kveldshenting.ps1) eller "jobben ny"
    (commiten fra i gaar har ingen kveldshenting.ps1)."""
    origin, hoved, jobb = tmp_path / "origin.git", tmp_path / "hoved", tmp_path / "jobb"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True, capture_output=True)
    _git(origin, "symbolic-ref", "HEAD", "refs/heads/main")
    subprocess.run(["git", "clone", "-q", str(origin), str(hoved)], check=True, capture_output=True)
    _git(hoved, "symbolic-ref", "HEAD", "refs/heads/main")
    (hoved / "start").mkdir()
    skriptet = hoved / "start" / "kveldshenting.ps1"
    if etter != "jobben ny":
        skriptet.write_bytes(JOBBEN.read_bytes())
    (hoved / ".gitignore").write_text("data/\n.env\n", encoding="utf-8")
    _git(hoved, "add", ".")
    i_gaar = (datetime.now().astimezone() - timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
    _git(hoved, "commit", "-q", "-m", "foer midnatt", dato=i_gaar.isoformat())
    foer = _git(hoved, "rev-parse", "HEAD")
    (hoved / "etter-midnatt.txt").write_text("flettet i dag\n", encoding="utf-8")
    if etter == "skriptet endret":
        skriptet.write_bytes(JOBBEN.read_bytes() + b"# flettet i dag\r\n")
    elif etter == "jobben ny":
        skriptet.write_bytes(JOBBEN.read_bytes())
    _git(hoved, "add", ".")
    _git(hoved, "commit", "-q", "-m", "etter midnatt")
    nyeste = _git(hoved, "rev-parse", "HEAD")
    _git(hoved, "push", "-q", "origin", "main")
    if start == "gren":
        _git(hoved, "worktree", "add", "-q", "-b", "gren", str(jobb), nyeste)
        (jobb / "paa-grenen.txt").write_text("gren\n", encoding="utf-8")
        _git(jobb, "add", ".")
        _git(jobb, "commit", "-q", "-m", "paa grenen")
    else:
        _git(hoved, "worktree", "add", "-q", "--detach", str(jobb), nyeste)
    (hoved / "data").mkdir()
    subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(jobb / "data"), str(hoved / "data")], check=True, capture_output=True
    )
    (hoved / ".env").write_text(f"EODHD_API_KEY={NOEKKELEN}\n", encoding="utf-8")
    os.link(hoved / ".env", jobb / ".env")
    return {"hoved": hoved, "jobb": jobb, "foer": foer, "etter": nyeste}


def _kjoer(tmp_path: Path, skript: Path, hoved: Path, *ekstra: str) -> tuple[int, str]:
    """Windows PowerShell 5.1 med den falske docker og den falske uv foerst
    paa PATH, saa git og System32. ProgramFiles peker paa en tom mappe, saa
    Docker Desktop aldri startes.

    CI-feilen 28.10 (40770982416 paa main og 40777327364 paa 2.13): runneren
    har en docker paa PATH som svarte innen fristen, saa skriptet startet og
    stoppet Ollama. Den falske docker svarer aldri, saa svaret er det samme
    med og uten Docker paa maskinen. Den skriver hvert kall til docker.txt.
    """
    systemrot = os.environ["SYSTEMROOT"]
    powershell = Path(systemrot) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    falsk = tmp_path / "falsk"
    falsk.mkdir(exist_ok=True)
    (falsk / "uv.cmd").write_text(
        "@echo off\r\necho falsk henting %*\r\necho tjeneste=%OSE_KI_TJENESTE%\r\necho mappe=%CD%\r\n"
        'if "%~4"=="--maal-omsetning" exit /b 5\r\nexit /b 3\r\n',
        encoding="ascii",
    )
    (falsk / "docker.cmd").write_text(
        '@echo off\r\necho falsk docker %*>>"%~dp0docker.txt"\r\nexit /b 1\r\n',
        encoding="ascii",
    )
    hjem = tmp_path / "hjem"
    miljoe = {
        "PATH": os.pathsep.join([str(falsk), str(Path(shutil.which("git")).parent), str(Path(systemrot) / "System32")]),
        "SYSTEMROOT": systemrot,
        "USERPROFILE": str(hjem),
        "LOCALAPPDATA": str(hjem / "AppData" / "Local"),
        "APPDATA": str(hjem / "AppData" / "Roaming"),
        "ProgramData": str(tmp_path / "ProgramData"),
        "ProgramFiles": str(tmp_path / "ProgramFiles"),
        "SystemDrive": os.environ.get("SystemDrive", "C:"),
        "PSModulePath": "",
        "PATHEXT": ".COM;.EXE;.BAT;.CMD",
        "OSE_PROEVE_HEMMELIG": MILJOEET,
    }
    argumenter = [str(powershell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File"]
    svar = subprocess.run(
        [*argumenter, str(skript), "-Hovedkopi", str(hoved), "-Tidsgrense", "1", *ekstra],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=miljoe,
        timeout=180,
    )
    return svar.returncode, svar.stdout + svar.stderr


def _loggen(hoved: Path) -> str:
    logg = hoved / "data" / "logg" / f"kveldshenting-{datetime.now():%Y-%m-%d}.log"
    return logg.read_text(encoding="utf-8-sig") if logg.is_file() else ""


paa_windows = pytest.mark.skipif(
    sys.platform != "win32" or shutil.which("git") is None, reason="krever Windows PowerShell og git"
)


@paa_windows
@pytest.mark.parametrize("start", ["gren", "nyeste"])
def test_arbeidskopien_flyttes_til_commiten_fra_midnatt(tmp_path, start):
    """Ville feilet hvis jobben kjoerte fra en gren eller brukte en nyere
    commit enn den origin/main hadde ved midnatt: arbeidskopien staar etterpaa
    løsrevet paa commiten fra i gaar, uten fila som ble flettet i dag."""
    oppsett = _oppsett(tmp_path, start)
    kode, utskrift = _kjoer(tmp_path, oppsett["jobb"] / "start" / "kveldshenting.ps1", oppsett["hoved"], "-BareUtsjekk")
    assert kode == 0, utskrift
    jobb = oppsett["jobb"]
    assert _git(jobb, "rev-parse", "HEAD") == oppsett["foer"]
    svar = subprocess.run(["git", "-C", str(jobb), "symbolic-ref", "-q", "HEAD"], capture_output=True)
    assert svar.returncode != 0
    assert not (jobb / "etter-midnatt.txt").exists() and not (jobb / "paa-grenen.txt").exists()
    assert f"Arbeidskopien står på {oppsett['foer']}" in _loggen(oppsett["hoved"])
    assert _git(oppsett["hoved"], "rev-parse", "HEAD") == oppsett["etter"]


@paa_windows
def test_jobben_stopper_i_hovedkopien(tmp_path):
    """Ville feilet hvis jobben kjoerte fra hovedkopien: den stopper med kode
    1 og flytter ikke hovedkopien."""
    oppsett = _oppsett(tmp_path, "nyeste")
    hoved = oppsett["hoved"]
    kode, utskrift = _kjoer(tmp_path, hoved / "start" / "kveldshenting.ps1", hoved, "-BareUtsjekk")
    assert kode == 1 and "kjører fra hovedkopien" in utskrift, utskrift
    assert _git(hoved, "rev-parse", "--abbrev-ref", "HEAD") == "main"
    assert _git(hoved, "rev-parse", "HEAD") == oppsett["etter"]


@paa_windows
@pytest.mark.parametrize("feil", ["env-kopi", "data-mappe"])
def test_jobben_stopper_uten_lenkene_til_hovedkopien(tmp_path, feil):
    """Ville feilet hvis jobben godtok en kopi av .env (nøkkelen kopiert) eller
    en egen data-mappe (en annen base enn hovedkopiens)."""
    oppsett = _oppsett(tmp_path, "nyeste")
    jobb = oppsett["jobb"]
    if feil == "env-kopi":
        (jobb / ".env").unlink()
        shutil.copyfile(oppsett["hoved"] / ".env", jobb / ".env")
    else:
        os.rmdir(jobb / "data")
        (jobb / "data").mkdir()
    kode, utskrift = _kjoer(tmp_path, jobb / "start" / "kveldshenting.ps1", oppsett["hoved"], "-BareUtsjekk")
    assert kode == 1 and "er ikke en lenke til" in utskrift, utskrift


@paa_windows
def test_hele_jobben_uten_docker_henter_uten_ki_og_gir_koden_fra_hentingen(tmp_path):
    """Ville feilet hvis jobben skrev ut nøkkelen eller miljøet, hentet med
    KI-tekst uten Docker (NFR-04), kjoerte hentingen et annet sted enn i
    arbeidskopien, ikke skrev loggen i data/, eller ga en annen kode enn
    hentingen (den falske uv gir 3). Story 2.13: maalingen kjoeres etter
    hentingen, og koden fra den (5) blir ikke koden jobben gir."""
    oppsett = _oppsett(tmp_path, "nyeste")
    jobb = oppsett["jobb"]
    kode, utskrift = _kjoer(tmp_path, jobb / "start" / "kveldshenting.ps1", oppsett["hoved"])
    loggen = _loggen(oppsett["hoved"])
    assert kode == 3, utskrift
    assert "falsk henting run python src/fetch_prices.py" in loggen
    assert "tjeneste=av" in loggen and f"mappe={jobb}" in loggen
    assert "Henter uten KI-tekst (NFR-04)" in loggen
    assert "Hentingen avsluttet med kode 3." in loggen
    assert "falsk henting run python src/fetch_prices.py --maal-omsetning" in loggen
    assert loggen.index("Hentingen avsluttet med kode 3.") < loggen.index("Målingen avsluttet med kode 5.")
    assert "Skriptet startet verken Docker Desktop eller Ollama." in loggen
    # Ville feilet hvis den ekte docker ble brukt: den falske er spurt, og
    # svarte ikke (CI-feilen 28.10).
    assert "falsk docker info" in (tmp_path / "falsk" / "docker.txt").read_text(encoding="ascii")
    assert "Docker svarte ikke innen 1 s." in loggen
    assert "Stopper Ollama." not in loggen and "Starter Ollama." not in loggen
    for tekst in (utskrift, loggen):
        assert NOEKKELEN not in tekst and MILJOEET not in tekst


@paa_windows
def test_den_nye_versjonen_kjoeres_en_gang_etter_utsjekken(tmp_path):
    """Gjennomgangen (VG2, ECH6). Ville feilet hvis jobben kjoerte skriptet
    fra en nyere commit enn den fra midnatt i kveld, mistet argumentene i den
    nye kjoeringen eller startet den mer enn én gang."""
    oppsett = _oppsett(tmp_path, "nyeste", "skriptet endret")
    jobb = oppsett["jobb"]
    kode, utskrift = _kjoer(tmp_path, jobb / "start" / "kveldshenting.ps1", oppsett["hoved"], "-BareUtsjekk")
    loggen = _loggen(oppsett["hoved"])
    assert kode == 0, utskrift
    assert loggen.count("Skriptet ble endret av utsjekken.") == 1, loggen
    assert loggen.count("Bare utsjekken: ingen henting.") == 1, loggen
    assert _git(jobb, "rev-parse", "HEAD") == oppsett["foer"]
    assert _uten_cr(jobb / "start" / "kveldshenting.ps1") == _uten_cr(JOBBEN)


@paa_windows
def test_jobben_stopper_naar_commiten_fra_midnatt_ikke_har_den(tmp_path):
    """Gjennomgangen (ECH1). Ville feilet hvis jobben sjekket ut en commit
    uten kveldshenting.ps1, dagen 2.3d flettes, og tok bort skriptet som
    kjoerer."""
    oppsett = _oppsett(tmp_path, "nyeste", "jobben ny")
    jobb = oppsett["jobb"]
    kode, utskrift = _kjoer(tmp_path, jobb / "start" / "kveldshenting.ps1", oppsett["hoved"], "-BareUtsjekk")
    assert kode == 1 and "har ikke start/kveldshenting.ps1 ennå" in utskrift, utskrift
    assert _git(jobb, "rev-parse", "HEAD") == oppsett["etter"]
    assert (jobb / "start" / "kveldshenting.ps1").is_file()


@paa_windows
def test_jobben_stopper_naar_arbeidskopien_har_endringer(tmp_path):
    """Gjennomgangen (VG3). Ville feilet hvis jobben tok med endringer i
    arbeidskopien til commiten fra midnatt."""
    oppsett = _oppsett(tmp_path, "nyeste")
    jobb = oppsett["jobb"]
    (jobb / "etter-midnatt.txt").write_text("endret for hånd\n", encoding="utf-8")
    kode, utskrift = _kjoer(tmp_path, jobb / "start" / "kveldshenting.ps1", oppsett["hoved"], "-BareUtsjekk")
    assert kode == 1 and "Arbeidskopien har endringer" in utskrift, utskrift
    assert _git(jobb, "rev-parse", "HEAD") == oppsett["etter"]


def _uten_cr(sti: Path) -> bytes:
    """Fila med LF, fordi git i den midlertidige mappa kan sjekke ut med CRLF."""
    return sti.read_bytes().replace(b"\r\n", b"\n")
