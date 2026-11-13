"""Story 3.7: snarveien spør før nettleseren åpnes (svaret 11.11 kl. 22:07),
KI-teksten står på (tillegg 1), og Gemma eller egen nøkkel første gang
(tillegg 2 og 3). Spesifikasjonen er spec-3-7-snarveien-spoer-foer-nettleseren.md.

Startskriptene prøves med PowerShell på Windows, med et skrivebord og en rot
i tmp_path, en falsk nettleser, falske winget og ollama, og en falsk Ollama
på 127.0.0.1 i testen. Ingenting installeres, ingen modell hentes, og
nøklene er falske. Ingen kall går ut (AD-8).
"""

import json
import os
import re
import shutil
import socket
import subprocess
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import app as app_modul
import demo
from ki_tekst import velg_modell
from lagring_sqlite import demo_sti
from test_ki_tekst import SjekketModell, kjoer, radene, stier  # noqa: F401 (stier er en fixture)

ROT = Path(__file__).resolve().parent.parent
START = ROT / "start"
POWERSHELL = shutil.which("powershell")
WINDOWS = pytest.mark.skipif(os.name != "nt" or POWERSHELL is None, reason="startskriptet spør bare i Windows")
SPOERSMAAL_KI = "Skriv 1, 2 eller 3 og trykk Enter"
LINJA = "Nettleseren åpner appen når du har svart."
FALSK_NOEKKEL = "falsk-noekkel-3-7-ikke-ekte"


def _miljoe(miljoe: dict[str, str | None]) -> dict[str, str]:
    """os.environ med miljoe over. None tar variabelen bort, for eksempel
    OSE_KI_TJENESTE=av fra conftest.py, som ellers går foran .env."""
    ut = dict(os.environ)
    for navn, verdi in miljoe.items():
        if verdi is None:
            ut.pop(navn, None)
        else:
            ut[navn] = verdi
    return ut


def _ps(skript: str, miljoe: dict[str, str | None], inn: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", skript],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_miljoe(miljoe),
        input=inn,
        timeout=60,
    )


def _rot(tmp_path) -> tuple[Path, Path]:
    rot = tmp_path / "rot"
    (rot / "src" / "static").mkdir(parents=True, exist_ok=True)
    (rot / "src" / "static" / "ikon.ico").write_bytes(b"")
    for fil in ("Start den ekte versjonen.cmd", "Start demoen.cmd"):
        (rot / fil).write_text("@echo off\n", encoding="utf-8")
    skrivebord = tmp_path / "skrivebord"
    skrivebord.mkdir(exist_ok=True)
    return rot, skrivebord


@WINDOWS
class TestRekkefoelgen:
    """Del A: spørsmålet om snarveien først, så nettleseren."""

    @staticmethod
    def _start(tmp_path, svar="j", kjoerer="{ $true }", versjon="ekte", ja="", uten=""):
        rot, skrivebord = _rot(tmp_path)
        skript = (
            # Som i start.ps1 (gjennomgangen, VG8).
            "$ErrorActionPreference = 'Stop'; [Console]::OutputEncoding = [Text.Encoding]::UTF8; $script:n = 0; "
            f". '{START / 'snarvei.ps1'}'; "
            f"Snarvei-Og-Nettleser {versjon} '{rot}' {kjoerer} {{ Write-Host 'FALSK NETTLESER ÅPNET' }}; "
            "Write-Host 'videre'"
        )
        miljoe = {
            "OSE_SKRIVEBORD": str(skrivebord),
            "OSE_START_SVAR_SNARVEI": svar,
            "OSE_START_SVAR_JA": ja,
            "OSE_START_UTEN_NETTLESER": uten,
        }
        return _ps(skript, miljoe), rot, skrivebord

    @pytest.mark.parametrize("svar", ["j", "n"])
    def test_spoersmaalet_kommer_foer_nettleseren_ogsaa_etter_nei(self, tmp_path, svar):
        """Ville feilet hvis nettleseren ble åpnet før spørsmålet, som 11.11
        kl. 22:06, hvis linja om nettleseren ikke sto rett før spørsmålet,
        eller hvis et nei ga ingen nettleser."""
        ut, _, skrivebord = self._start(tmp_path, svar)
        tekst = ut.stdout
        assert ut.returncode == 0, tekst + ut.stderr
        sporsmaal = tekst.index("Lage snarveien «OSE Signal» på skrivebordet?")
        assert tekst.index(LINJA) < sporsmaal < tekst.index("FALSK NETTLESER ÅPNET") < tekst.index("videre")
        assert tekst[tekst.index(LINJA) + len(LINJA) :].lstrip().startswith("Lage snarveien")
        assert (skrivebord / "OSE Signal.lnk").exists() == (svar == "j")

    def test_nettleseren_aapnes_naar_vinduet_ikke_spoer(self, tmp_path):
        """Ville feilet hvis nettleseren ikke ble åpnet når snarveien finnes
        fra før, eller linja om nettleseren sto uten spørsmål."""
        self._start(tmp_path, "j")
        ut, _, _ = self._start(tmp_path, "j")
        assert "FALSK NETTLESER ÅPNET" in ut.stdout and LINJA not in ut.stdout and "Lage snarveien" not in ut.stdout

    def test_ci_aapner_ingen_nettleser_og_spoer_ikke(self, tmp_path):
        """Ville feilet hvis OSE_START_UTEN_NETTLESER=1 åpnet nettleseren, eller
        OSE_START_SVAR_JA=1 ga et spørsmål."""
        ut, _, skrivebord = self._start(tmp_path, "", ja="1", uten="1")
        assert ut.returncode == 0 and "videre" in ut.stdout
        assert "FALSK NETTLESER" not in ut.stdout and LINJA not in ut.stdout and not list(skrivebord.iterdir())

    def test_uten_nettleser_staar_ikke_linja(self, tmp_path):
        """Spørsmål 3. Ville feilet hvis linja lovet en nettleser som ikke åpnes."""
        ut, _, _ = self._start(tmp_path, "n", uten="1")
        assert "Lage snarveien" in ut.stdout and LINJA not in ut.stdout and "FALSK NETTLESER" not in ut.stdout

    def test_ingen_nettleser_naar_appen_stoppet_mens_vinduet_spurte(self, tmp_path):
        """Ville feilet hvis nettleseren ble åpnet etter at appen stoppet mens
        spørsmålet sto. Første gang kjører appen, andre gang har den stoppet."""
        ut, _, _ = self._start(tmp_path, "n", kjoerer="{ $script:n++; $script:n -le 1 }")
        assert "Lage snarveien" in ut.stdout and "FALSK NETTLESER" not in ut.stdout and "videre" in ut.stdout

    def test_ingen_spoersmaal_og_ingen_nettleser_naar_appen_alt_har_stoppet(self, tmp_path):
        """Ville feilet hvis vinduet spurte eller åpnet nettleseren når appen
        alt hadde stoppet (gjennomgangen av 3.6, ECH2)."""
        ut, rot, _ = self._start(tmp_path, "n", kjoerer="{ $false }")
        assert "Lage snarveien" not in ut.stdout and "FALSK NETTLESER" not in ut.stdout
        assert not (rot / "data").exists()

    def test_spoersmaalet_om_en_annen_kopi_ogsaa(self, tmp_path):
        """Svaret 11.11 kl. 13:47. Ville feilet hvis spørsmålet om en snarvei
        til en annen kopi kom etter nettleseren, eller uten linja."""
        annen = tmp_path / "annen"
        annen.mkdir()
        (annen / "Start den ekte versjonen.cmd").write_text("@echo off\n", encoding="utf-8")
        lnk = tmp_path / "skrivebord" / "OSE Signal.lnk"
        lnk.parent.mkdir()
        _ps(
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}'); "
            f"$s.TargetPath = '{annen / 'Start den ekte versjonen.cmd'}'; $s.Save()",
            {},
        )
        ut, _, _ = self._start(tmp_path, "n")
        tekst = ut.stdout
        assert tekst.index(LINJA) < tekst.index("Skal den starte denne kopien") < tekst.index("FALSK NETTLESER ÅPNET")


class TestStartskriptet:
    def test_start_ps1_aapner_nettleseren_bare_gjennom_snarveien(self):
        """Ville feilet hvis start.ps1 åpnet nettleseren før spørsmålet, som
        før 3.7, eller kalte rekkefølgen uten vakten for en app som har stoppet."""
        tekst = (START / "start.ps1").read_text(encoding="utf-8-sig")
        kall = (
            "Snarvei-Og-Nettleser $Versjon (Split-Path -Parent $PSScriptRoot) "
            "{ -not $server.HasExited } { Start-Process $Adresse }"
        )
        assert tekst.count(kall) == 1
        assert "Start-Process $Adresse" not in tekst.replace(kall, "")
        assert tekst.index(". (Join-Path $PSScriptRoot 'snarvei.ps1')") < tekst.index(kall)
        assert tekst.index('Write-Host "Appen kjører på $Adresse."') < tekst.index(kall)
        assert tekst.index(kall) < tekst.index("$server.WaitForExit()")

    def test_bare_den_ekte_versjonen_tilbyr_ki(self):
        """Tillegg 2 og 3. Ville feilet hvis demoen kunne spørre om Gemma eller
        en nøkkel, eller hvis spørsmålet kom etter hentingen eller før nøkkelen."""
        tekst = (START / "start.ps1").read_text(encoding="utf-8-sig")
        kall = "Tilby-KI (Split-Path -Parent $PSScriptRoot)"
        assert tekst.count(kall) == 1 and tekst.count("ki-modell.ps1") == 1
        demo_gren = tekst.index("Write-Host 'Lager demobasen.'")
        ekte_gren = tekst.index("Remove-Item Env:OSE_DEMO")
        assert demo_gren < ekte_gren < tekst.index("Write-Host 'Nøkkelen er lagret i .env.'") < tekst.index(kall)
        assert tekst.index(kall) < tekst.index("uv run python src/fetch_prices.py")
        for fil in START.iterdir():
            if fil.name not in ("start.ps1", "ki-modell.ps1"):
                assert "Tilby-KI" not in fil.read_text(encoding="utf-8-sig"), fil
        for fil in (f for f in ROT.glob("Start*") if f.is_file()):
            assert "ki-modell" not in fil.read_text(encoding="utf-8", errors="replace"), fil
        assert (START / "ki-modell.ps1").read_bytes().startswith(b"\xef\xbb\xbf")


class TestKITekstenStaarPaa:
    """Del B (tillegg 1): lokal i .env.example, og en tydelig linje uten modell."""

    def test_env_example_har_lokal(self):
        """Ville feilet hvis .env.example fortsatt hadde av, eller hadde
        variabelen to ganger."""
        eksempel = (ROT / ".env.example").read_text(encoding="utf-8")
        assert re.findall(r"^OSE_KI_TJENESTE=(.*)$", eksempel, re.MULTILINE) == ["lokal"]

    @pytest.mark.skipif(os.name != "nt" or POWERSHELL is None, reason="linja i start.ps1 kjøres med PowerShell")
    def test_ny_env_fra_startskriptet_har_lokal_og_en_gammel_endres_ikke(self, tmp_path):
        """Ville feilet hvis en ny .env fra start.ps1 ikke fikk lokal, eller en
        .env som fantes fra før, ble endret. Linja kjøres slik den står i skriptet."""
        tekst = (START / "start.ps1").read_text(encoding="utf-8-sig")
        linja = next(l.strip() for l in tekst.splitlines() if "Copy-Item -LiteralPath '.env.example'" in l)
        ny = tmp_path / "ny"
        gammel = tmp_path / "gammel"
        for mappe in (ny, gammel):
            mappe.mkdir()
            shutil.copy(ROT / ".env.example", mappe / ".env.example")
        innhold = b"EODHD_API_KEY=x\r\nOSE_KI_TJENESTE=av\r\n"
        (gammel / ".env").write_bytes(innhold)
        for mappe in (ny, gammel):
            ut = _ps(f"Set-Location -LiteralPath '{mappe}'; {linja}", {})
            assert ut.returncode == 0, ut.stderr
        assert re.search(r"^OSE_KI_TJENESTE=lokal\r?$", (ny / ".env").read_text(encoding="utf-8"), re.MULTILINE)
        assert (gammel / ".env").read_bytes() == innhold

    def test_start_sh_kopierer_den_samme_fila(self):
        """Ville feilet hvis Mac fikk en ny .env fra en annen fil enn .env.example."""
        assert "[ -f .env ] || cp .env.example .env" in (START / "start.sh").read_text(encoding="utf-8")

    def test_lokal_gir_ollama_uten_kall(self):
        """Ville feilet hvis lokal ikke ga den lokale modellen, eller sjekket den
        med et kall allerede da modellen ble valgt."""
        modell = velg_modell({"OSE_KI_TJENESTE": "lokal"}, skriv=lambda _: None)
        assert modell is not None and modell.tjeneste == "lokal"

    def test_hentingen_uten_ollama_fortsetter_med_linja(self, stier):  # noqa: F811
        """Ville feilet hvis hentingen stoppet uten Ollama, skrev KI-tekst, eller
        ikke sa i én linje at teksten ikke lages, hvorfor og hvor i
        docs/installasjon.md det står hvordan den slås på."""
        raa, base = stier
        modell = SjekketModell("Ollama svarer ikke (kjører den?)")
        kode, kall, ut = kjoer(raa, base, modell)
        assert kode == 0 and modell.kall == 0 and len(kall) == 16
        assert all(r is None for r in radene(base).values())
        linja = next(l for l in ut.splitlines() if l.startswith("Ingen KI-tekst for børsdagen"))
        assert "Ollama svarer ikke" in linja
        assert "Start Ollama, eller installer den, se «Den lokale modellen» i docs/installasjon.md" in linja


@pytest.fixture(scope="module")
def demomal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


class TestDemoen:
    """Linja om modellen står bare i den ekte versjonen. Den ekte versjonen
    prøves i test_ki_visning.py og test_ki_dagen.py."""

    def test_demoen_viser_ikke_linja(self, demomal, monkeypatch):
        """Ville feilet hvis demoen sa at maskinen trenger en modell, eller lenket
        til installasjonen fra KI-teksten."""
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(demomal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        klient = app_modul.app.test_client()
        sider = ["/", "/aksje/BRFE"]
        html = klient.get("/aksje/BRFE").get_data(as_text=True)
        sider += sorted(set(re.findall(r'href="(/aksje/BRFE\?dag=[\d-]+)"', html)))[:2]
        for adresse in sider:
            side = klient.get(adresse).get_data(as_text=True)
            assert "på en maskin med en språkmodell" not in side, adresse
            assert app_modul.KI_TEKSTEN_URL not in side, adresse


class _FalskOllama(BaseHTTPRequestHandler):
    modeller: list = []

    def do_GET(self):  # noqa: N802
        data = json.dumps({"models": [{"name": m, "model": m} for m in self.modeller]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass


@pytest.fixture
def ollama():
    """En falsk Ollama på 127.0.0.1 i testen. modeller settes per test."""
    klasse = type("Falsk", (_FalskOllama,), {"modeller": []})
    tjener = ThreadingHTTPServer(("127.0.0.1", 0), klasse)
    traad = threading.Thread(target=tjener.serve_forever, daemon=True)
    traad.start()
    yield klasse, f"http://127.0.0.1:{tjener.server_address[1]}"
    tjener.shutdown()
    tjener.server_close()


def _lukket_port() -> str:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return f"http://127.0.0.1:{port}"


WINGET = """@echo off
echo winget %*>>"%OSE_TEST_LOGG%"
mkdir "%LOCALAPPDATA%\\Programs\\Ollama" 2>nul
if "%OSE_TEST_WINGET_KOPI%"=="1" copy /y "%OSE_TEST_FALSK_OLLAMA%" "%LOCALAPPDATA%\\Programs\\Ollama\\ollama.cmd" >nul
exit /b %OSE_TEST_WINGET_KODE%
"""
# Som den ekte skriver den framdriften til stderr (gjennomgangen, VG14).
OLLAMA = """@echo off
echo ollama %*>>"%OSE_TEST_LOGG%"
echo pulling 50%% 1>&2
exit /b %OSE_TEST_OLLAMA_KODE%
"""


@WINDOWS
class TestKIValget:
    """Del C (tillegg 2 og 3): Gemma, egen nøkkel eller ikke nå, første gang."""

    @staticmethod
    def _tilby(
        tmp_path, url, svar="", tjeneste="", noekkel="", winget=False, ollama_finnes=False, foer="", inn=None, **koder
    ):
        rot = tmp_path / "rot"
        rot.mkdir(exist_ok=True)
        bin_ = tmp_path / "bin"
        bin_.mkdir(exist_ok=True)
        lad = tmp_path / "lad"
        lad.mkdir(exist_ok=True)
        falsk = tmp_path / "falsk-ollama.cmd"
        falsk.write_text(OLLAMA, encoding="ascii")
        if winget:
            (bin_ / "winget.cmd").write_text(WINGET, encoding="ascii")
        if ollama_finnes:
            shutil.copy(falsk, bin_ / "ollama.cmd")
        system = os.environ.get("SystemRoot", r"C:\Windows")
        miljoe = {
            "PATH": f"{bin_};{system}\\System32;{system}\\System32\\WindowsPowerShell\\v1.0",
            "LOCALAPPDATA": str(lad),
            # Ingen ekte Ollama under Program Files på denne PC-en finnes eller startes.
            "ProgramFiles": str(tmp_path / "pf"),
            "OSE_KI_TJENESTE": koder.get("tjeneste_i_miljoeet"),
            "OSE_KI_OLLAMA_URL": None,
            "OSE_START_SVAR_FRIST": "2",
            "OSE_START_OLLAMA_URL": url,
            "OSE_START_OLLAMA_VENT": "1",
            "OSE_START_SVAR_KI": svar,
            "OSE_START_SVAR_KI_TJENESTE": tjeneste,
            "OSE_START_SVAR_KI_NOEKKEL": noekkel,
            "OSE_START_SVAR_JA": koder.get("ja", ""),
            "OSE_START_UTEN_NETTLESER": koder.get("uten", "1"),
            "OSE_TEST_LOGG": str(tmp_path / "logg.txt"),
            "OSE_TEST_FALSK_OLLAMA": str(falsk),
            "OSE_TEST_WINGET_KODE": koder.get("winget_kode", "0"),
            "OSE_TEST_WINGET_KOPI": koder.get("winget_kopi", "1"),
            "OSE_TEST_OLLAMA_KODE": koder.get("ollama_kode", "0"),
        }
        skript = (
            "$ErrorActionPreference = 'Stop'; [Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{START / 'ki-modell.ps1'}'; {foer} Tilby-KI '{rot}'; Write-Host 'appen starter'"
        )
        ut = _ps(skript, miljoe, inn)
        logg = tmp_path / "logg.txt"
        kall = logg.read_text(encoding="utf-8", errors="replace").splitlines() if logg.exists() else []
        return ut, rot, [k.strip() for k in kall]

    def test_ingen_spoersmaal_naar_ollama_har_modellen(self, tmp_path, ollama):
        """Ville feilet hvis vinduet spurte når Ollama svarer med gemma4:e4b."""
        klasse, url = ollama
        klasse.modeller = ["gemma4:e4b"]
        ut, rot, kall = self._tilby(tmp_path, url, "1", winget=True)
        assert SPOERSMAAL_KI not in ut.stdout and kall == [] and not (rot / "data").exists()
        assert "appen starter" in ut.stdout

    def test_ja_installerer_ollama_og_henter_saa_modellen(self, tmp_path, ollama):
        """Ville feilet hvis ja ikke installerte Ollama med winget og pakken
        Ollama.Ollama, eller hentet modellen før installasjonen."""
        klasse, url = ollama
        klasse.modeller = []
        ut, rot, kall = self._tilby(tmp_path, url, "1", winget=True)
        assert SPOERSMAAL_KI in ut.stdout, ut.stdout + ut.stderr
        assert len(kall) == 2, kall
        assert kall[0].startswith("winget install --id Ollama.Ollama --exact --source winget")
        assert kall[1] == "ollama pull gemma4:e4b"
        assert "Gemma er hentet." in ut.stdout and "appen starter" in ut.stdout
        assert not (rot / ".env").exists() and not (rot / "data").exists()

    def test_bare_modellen_naar_ollama_finnes(self, tmp_path, ollama):
        """Ville feilet hvis Ollama ble installert på nytt når den finnes."""
        klasse, url = ollama
        klasse.modeller = ["llama3:latest"]
        ut, _, kall = self._tilby(tmp_path, url, "1", winget=True, ollama_finnes=True)
        assert kall == ["ollama pull gemma4:e4b"], kall

    @pytest.mark.parametrize(
        ("koder", "beskjed", "antall"),
        [
            ({"winget_kode": "1", "winget_kopi": "0"}, "Ollama kunne ikke installeres med winget (kode 1).", 1),
            ({"ollama_kode": "1"}, "Gemma ble ikke hentet (kode 1).", 2),
        ],
    )
    def test_en_feil_gir_beskjeden_og_appen_starter(self, tmp_path, ollama, koder, beskjed, antall):
        """Ville feilet hvis en feil i winget eller ollama pull stoppet vinduet,
        ble husket som nei, eller ikke sa hva som skjedde og hvordan det gjøres senere."""
        klasse, url = ollama
        klasse.modeller = []
        ut, rot, kall = self._tilby(tmp_path, url, "1", winget=True, **koder)
        assert ut.returncode == 0 and "appen starter" in ut.stdout, ut.stdout + ut.stderr
        assert beskjed in ut.stdout and "Appen starter som før, uten KI-tekst." in ut.stdout
        assert "«Den lokale modellen for KI-teksten» i docs/installasjon.md" in ut.stdout
        assert len(kall) == antall and not (rot / "data").exists()

    def test_uten_winget_aapnes_nedlastingssiden(self, tmp_path, ollama):
        """Ville feilet hvis vinduet uten winget ikke viste siden der Ollama
        lastes ned, eller ikke ga beskjeden når Ollama fortsatt mangler."""
        klasse, url = ollama
        klasse.modeller = []
        ut, _, kall = self._tilby(tmp_path, url, "1")
        assert "https://ollama.com/download" in ut.stdout and "Ollama ble ikke funnet" in ut.stdout
        assert kall == [] and "appen starter" in ut.stdout

    def test_ollama_som_ikke_svarer_gir_spoersmaalet(self, tmp_path):
        """Ville feilet hvis vinduet ikke spurte når ingenting svarer på adressen."""
        ut, rot, _ = self._tilby(tmp_path, _lukket_port(), "3")
        assert SPOERSMAAL_KI in ut.stdout and (rot / "data" / "ki-nei-ekte").exists()

    @pytest.mark.parametrize("svar", ["3", " "])
    def test_ikke_naa_huskes(self, tmp_path, ollama, svar):
        """Ville feilet hvis ikke nå, et tomt svar eller noe annet ikke ble
        husket, så vinduet spurte hver gang, eller installerte noe."""
        klasse, url = ollama
        ut, rot, kall = self._tilby(tmp_path, url, svar, winget=True)
        assert (rot / "data" / "ki-nei-ekte").exists() and kall == []
        assert "Vinduet spør ikke igjen." in ut.stdout
        ut, _, kall = self._tilby(tmp_path, url, "1", winget=True)
        assert SPOERSMAAL_KI not in ut.stdout and kall == []

    @pytest.mark.parametrize(
        ("bokstav", "verdi", "variabel"),
        [
            ("g", "gemini", "OSE_KI_GEMINI_NOKKEL"),
            ("a", "anthropic", "OSE_KI_ANTHROPIC_NOKKEL"),
            ("o", "openai", "OSE_KI_OPENAI_NOKKEL"),
        ],
    )
    def test_egen_noekkel_skrives_i_env(self, tmp_path, ollama, bokstav, verdi, variabel):
        """Ville feilet hvis en annen tjeneste eller nøkkel ble skrevet, en gammel
        linje ble doblet i stedet for byttet ut, noe annet i .env ble endret,
        eller nøkkelen sto i det vinduet skriver."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        foer = [
            "# kommentar",
            "EODHD_API_KEY=falsk-eodhd",
            "OSE_KI_TJENESTE=lokal",
            "# OSE_KI_OLLAMA_URL=http://127.0.0.1:11434",
            "OSE_KI_GEMINI_NOKKEL=",
            "OSE_KI_ANTHROPIC_NOKKEL=",
            "OSE_KI_OPENAI_NOKKEL=",
            f"{variabel}=gammel",
        ]
        (rot / ".env").write_bytes(("\r\n".join(foer) + "\r\n").encode("utf-8"))
        ut, _, kall = self._tilby(tmp_path, url, "2", tjeneste=bokstav, noekkel=f" {FALSK_NOEKKEL} ")
        etter = (rot / ".env").read_text(encoding="utf-8").splitlines()
        forventet = [l for l in foer if not l.startswith(f"{variabel}=gammel")]
        forventet = [
            "OSE_KI_TJENESTE=" + verdi
            if l == "OSE_KI_TJENESTE=lokal"
            else (f"{variabel}={FALSK_NOEKKEL}" if l == f"{variabel}=" else l)
            for l in forventet
        ]
        assert etter == forventet, etter
        assert FALSK_NOEKKEL not in ut.stdout and FALSK_NOEKKEL not in ut.stderr
        assert "Valget er lagret i .env" in ut.stdout and kall == [] and not (rot / "data").exists()

    def test_egen_noekkel_uten_linjene_fra_foer(self, tmp_path, ollama):
        """Ville feilet hvis linjene ikke ble lagt til når .env mangler dem."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        (rot / ".env").write_bytes(b"EODHD_API_KEY=falsk-eodhd\r\n")
        self._tilby(tmp_path, url, "2", tjeneste="g", noekkel=FALSK_NOEKKEL)
        assert (rot / ".env").read_text(encoding="utf-8").splitlines() == [
            "EODHD_API_KEY=falsk-eodhd",
            "OSE_KI_TJENESTE=gemini",
            f"OSE_KI_GEMINI_NOKKEL={FALSK_NOEKKEL}",
        ]

    @pytest.mark.parametrize(("tjeneste", "noekkel"), [("g", " "), ("x", FALSK_NOEKKEL)])
    def test_tom_noekkel_eller_ukjent_tjeneste_endrer_ingenting(self, tmp_path, ollama, tjeneste, noekkel):
        """Spørsmål 16. Ville feilet hvis en tom nøkkel eller en ukjent bokstav
        endret .env eller ble husket som nei."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        innhold = b"EODHD_API_KEY=falsk-eodhd\r\nOSE_KI_TJENESTE=lokal\r\n"
        (rot / ".env").write_bytes(innhold)
        ut, _, _ = self._tilby(tmp_path, url, "2", tjeneste=tjeneste, noekkel=noekkel)
        assert (rot / ".env").read_bytes() == innhold and not (rot / "data").exists()
        assert "Vinduet spør igjen neste gang." in ut.stdout and FALSK_NOEKKEL not in ut.stdout

    @pytest.mark.parametrize("verdi", ["av", "gemini"])
    def test_et_valg_i_env_gir_ikke_spoersmaalet(self, tmp_path, ollama, verdi):
        """Spørsmål 11. Ville feilet hvis vinduet spurte når .env alt har et annet valg enn lokal."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        (rot / ".env").write_bytes(f"OSE_KI_TJENESTE={verdi}\r\n".encode())
        ut, _, kall = self._tilby(tmp_path, url, "1", winget=True)
        assert SPOERSMAAL_KI not in ut.stdout and kall == []

    def test_ci_gir_verken_spoersmaal_installasjon_eller_endring(self, tmp_path, ollama):
        """Ville feilet hvis OSE_START_SVAR_JA=1 (CI) spurte, installerte noe
        eller endret .env."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        (rot / ".env").write_bytes(b"OSE_KI_TJENESTE=lokal\r\n")
        miljoe_ja = {"ja": "1"}
        ut, _, kall = self._tilby(tmp_path, url, "", winget=True, **miljoe_ja)
        assert SPOERSMAAL_KI not in ut.stdout and kall == []
        assert (rot / ".env").read_bytes() == b"OSE_KI_TJENESTE=lokal\r\n" and not (rot / "data").exists()


def _ps_uten_svar(skript: str, miljoe: dict[str, str]) -> tuple[str, str, int]:
    """Som _ps, men standard inn står åpen uten at noe skrives, som et vindu
    ingen svarer i (tillegg 4). Fristen settes med OSE_START_SVAR_FRIST."""
    prosess = subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", skript],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_miljoe(miljoe),
    )
    try:
        kode = prosess.wait(timeout=60)
        return prosess.stdout.read().decode("utf-8"), prosess.stderr.read().decode("utf-8", "replace"), kode
    finally:
        prosess.stdin.close()
        prosess.stdout.close()
        prosess.stderr.close()


@WINDOWS
class TestFristen:
    """Tillegg 4: et spørsmål uten svar på 30 sekunder (her 2) gir ingen
    endring, ingenting huskes, og appen og nettleseren starter."""

    @staticmethod
    def _snarvei(tmp_path):
        rot, skrivebord = _rot(tmp_path)
        skript = (
            "[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{START / 'snarvei.ps1'}'; "
            f"Snarvei-Og-Nettleser ekte '{rot}' {{ $true }} {{ Write-Host 'FALSK NETTLESER ÅPNET' }}"
        )
        miljoe = {
            "OSE_SKRIVEBORD": str(skrivebord),
            "OSE_START_SVAR_SNARVEI": "",
            "OSE_START_SVAR_JA": "",
            "OSE_START_UTEN_NETTLESER": "",
            "OSE_START_SVAR_FRIST": "2",
        }
        return _ps_uten_svar(skript, miljoe), rot, skrivebord

    def test_uten_svar_aapnes_nettleseren_og_det_spoerres_igjen(self, tmp_path):
        """Ville feilet hvis vinduet ventet på svaret uten frist, laget
        snarveien, husket det som nei, eller ikke åpnet nettleseren."""
        (ut, feil, kode), rot, skrivebord = self._snarvei(tmp_path)
        assert kode == 0, ut + feil
        assert "Ingen svar på 2 sekunder" in ut and "Spørsmålet kommer igjen neste gang." in ut
        assert ut.index("Lage snarveien") < ut.index("Ingen svar") < ut.index("FALSK NETTLESER ÅPNET")
        assert not list(skrivebord.iterdir()) and not (rot / "data").exists()
        (ut, _, _), _, _ = self._snarvei(tmp_path)
        assert "Lage snarveien" in ut

    def test_uten_svar_om_en_annen_kopi_blir_snarveien_staaende(self, tmp_path):
        """Ville feilet hvis en snarvei til en annen kopi ble flyttet, eller
        neiet ble husket, når ingen svarte."""
        annen = tmp_path / "annen"
        annen.mkdir()
        maal = annen / "Start den ekte versjonen.cmd"
        maal.write_text("@echo off\n", encoding="utf-8")
        lnk = tmp_path / "skrivebord" / "OSE Signal.lnk"
        lnk.parent.mkdir()
        _ps(
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}'); $s.TargetPath = '{maal}'; $s.Save()",
            {},
        )
        (ut, feil, _), rot, _ = self._snarvei(tmp_path)
        assert "Skal den starte denne kopien" in ut and "Ingen svar på 2 sekunder" in ut, ut + feil
        mål = _ps(f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}').TargetPath", {}).stdout.strip()
        assert Path(mål) == maal and not (rot / "data").exists() and "FALSK NETTLESER ÅPNET" in ut

    def test_ki_uten_svar_er_ikke_naa_bare_denne_gangen(self, tmp_path, ollama):
        """Spørsmål 22. Ville feilet hvis KI-spørsmålet ventet uten frist,
        installerte noe, eller ble husket som nei, så appen ikke startet."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        skript = (
            "$ErrorActionPreference = 'Stop'; [Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{START / 'ki-modell.ps1'}'; Tilby-KI '{rot}'; Write-Host 'appen starter'"
        )
        miljoe = {
            "OSE_START_OLLAMA_URL": url,
            "OSE_START_SVAR_KI": "",
            "OSE_START_SVAR_JA": "",
            "OSE_START_SVAR_FRIST": "2",
            "OSE_KI_TJENESTE": None,
            "OSE_KI_OLLAMA_URL": None,
            "LOCALAPPDATA": str(tmp_path / "lad"),
            "ProgramFiles": str(tmp_path / "pf"),
            "PATH": os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32"),
        }
        ut, feil, kode = _ps_uten_svar(skript, miljoe)
        assert kode == 0 and SPOERSMAAL_KI in ut, ut + feil
        assert "Ingen svar på 2 sekunder, så ingen KI-tekst nå." in ut and "appen starter" in ut
        assert not (rot / "data").exists() and not (rot / ".env").exists()


@WINDOWS
class TestGjennomgangen:
    """Funnene fra gjennomgangen 12.11 (Blind Hunter, Edge Case Hunter og
    Verification Gap), som står i spesifikasjonen."""

    @staticmethod
    def _snarvei(tmp_path, inn, ja="", uten=""):
        rot, skrivebord = _rot(tmp_path)
        skript = (
            "$ErrorActionPreference = 'Stop'; [Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{START / 'snarvei.ps1'}'; "
            f"Snarvei-Og-Nettleser ekte '{rot}' {{ $true }} {{ Write-Host 'FALSK NETTLESER ÅPNET' }}"
        )
        miljoe = {
            "OSE_SKRIVEBORD": str(skrivebord),
            "OSE_START_SVAR_SNARVEI": "",
            "OSE_START_SVAR_JA": ja,
            "OSE_START_UTEN_NETTLESER": uten,
            "OSE_START_SVAR_FRIST": "2",
        }
        return _ps(skript, miljoe, inn), rot, skrivebord

    def test_et_svar_gjennom_lesingen_lager_snarveien(self, tmp_path):
        """VG1 (høy). Ville feilet hvis svaret som leses, ikke ble svaret,
        for eksempel hvis Les-Med-Frist ga en tom tekst, så et ja ble et nei
        som huskes."""
        ut, rot, skrivebord = self._snarvei(tmp_path, "j\n")
        assert (skrivebord / "OSE Signal.lnk").exists(), ut.stdout + ut.stderr
        assert ut.stdout.index("Lage snarveien") < ut.stdout.index("FALSK NETTLESER ÅPNET")
        assert not (rot / "data").exists()

    def test_lukket_standard_inn_er_uten_svar(self, tmp_path):
        """VG3. Ville feilet hvis en lukket standard inn (EOF) ble et nei som
        huskes, eller nettleseren ikke ble åpnet."""
        ut, rot, skrivebord = self._snarvei(tmp_path, "")
        assert "Ingen svar på 2 sekunder" in ut.stdout and "FALSK NETTLESER ÅPNET" in ut.stdout
        assert not list(skrivebord.iterdir()) and not (rot / "data").exists()

    def test_bare_svar_ja_aapner_nettleseren_uten_spoersmaal(self, tmp_path):
        """VG12. Ville feilet hvis OSE_START_SVAR_JA=1 alene stoppet nettleseren
        eller ga spørsmålet og linja."""
        ut, _, _ = self._snarvei(tmp_path, None, ja="1")
        assert "FALSK NETTLESER ÅPNET" in ut.stdout and "Lage snarveien" not in ut.stdout and LINJA not in ut.stdout

    def test_en_feil_i_spoersmaalet_aapner_nettleseren_likevel(self, tmp_path):
        """ECH6, VG8. Ville feilet hvis en feil i Tilby-Snarvei, med Stop som i
        start.ps1, stoppet vinduet før nettleseren."""
        rot, _ = _rot(tmp_path)
        skript = (
            "$ErrorActionPreference = 'Stop'; [Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{START / 'snarvei.ps1'}'; function Tilby-Snarvei {{ throw 'falsk feil' }}; "
            f"Snarvei-Og-Nettleser ekte '{rot}' {{ $true }} {{ Write-Host 'FALSK NETTLESER ÅPNET' }}; Write-Host 'videre'"
        )
        ut = _ps(skript, {"OSE_START_UTEN_NETTLESER": ""})
        assert ut.returncode == 0 and "Snarveien kunne ikke tilbys: falsk feil" in ut.stdout
        assert "FALSK NETTLESER ÅPNET" in ut.stdout and "videre" in ut.stdout

    @staticmethod
    def _taster(taster: str, sekunder=1, skjult=False):
        """Les-Taster med falske taster. j, a og 1 er tegn, < er Backspace og
        | er Enter."""
        lag = []
        for t in taster:
            if t == "|":
                lag.append("[ConsoleKeyInfo]::new([char]13, [ConsoleKey]::Enter, $false, $false, $false)")
            elif t == "<":
                lag.append("[ConsoleKeyInfo]::new([char]8, [ConsoleKey]::Backspace, $false, $false, $false)")
            else:
                lag.append(f"[ConsoleKeyInfo]::new([char]'{t}', [ConsoleKey]::A, $false, $false, $false)")
        skript = (
            "[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{START / 'frist.ps1'}'; $koe = New-Object System.Collections.Queue; "
            + "".join(f"$koe.Enqueue({x}); " for x in lag)
            + f"$svar = Les-Taster {sekunder} {{ $koe.Count -gt 0 }} {{ $koe.Dequeue() }}"
            + (" -Skjult" if skjult else "")
            + "; if ($null -eq $svar) { Write-Host 'SVAR=NULL' } else { Write-Host \"SVAR=[$svar]\" }"
        )
        return _ps(skript, {})

    def test_tastene_gir_svaret(self, tmp_path):
        """VG2 (høy). Ville feilet hvis lesingen i et ekte vindu ga et annet
        svar enn tastene, eller Backspace ikke tok bort et tegn."""
        assert "SVAR=[j]" in self._taster("j|").stdout
        assert "SVAR=[1]" in self._taster("a<1|").stdout
        assert "SVAR=[]" in self._taster("|").stdout

    def test_uten_taster_gaar_fristen_ut(self, tmp_path):
        """VG2. Ville feilet hvis lesingen ventet uten frist, eller ga en tom
        tekst, et nei, når fristen gikk ut."""
        ut = self._taster("", sekunder=1)
        assert "SVAR=NULL" in ut.stdout, ut.stdout + ut.stderr

    def test_skjult_viser_stjerner(self, tmp_path):
        """Ville feilet hvis en nøkkel som tastes, ble vist i vinduet."""
        ut = self._taster("ja|", skjult=True)
        linjer = ut.stdout.splitlines()
        assert "SVAR=[ja]" in ut.stdout and "**" in ut.stdout
        assert not any(("j" in l or "a" in l) and "SVAR" not in l for l in linjer), ut.stdout

    def test_fristen_er_30_sekunder(self):
        """VG9. Ville feilet hvis standarden ikke var 30 sekunder, eller en
        verdi som ikke er et tall, ga en feil."""
        for verdi in (None, "x"):
            ut = _ps(f". '{START / 'frist.ps1'}'; Write-Host (Svar-Frist)", {"OSE_START_SVAR_FRIST": verdi})
            assert ut.stdout.strip() == "30", ut.stdout + ut.stderr

    def test_modellen_og_adressen_er_de_i_koden(self):
        """VG10. Ville feilet hvis vinduet spurte etter en annen modell eller
        adresse enn hentingen og kveldsjobben bruker."""
        from ki_lokal import MODELL, STANDARD_URL

        tekst = (START / "ki-modell.ps1").read_text(encoding="utf-8-sig")
        assert f"$KiModell = '{MODELL}'" in tekst and f"$KiStandardUrl = '{STANDARD_URL}'" in tekst
        assert f"$Modell = '{MODELL}'" in (START / "kveldshenting.ps1").read_text(encoding="utf-8-sig")

    def test_stedene_vinduet_og_siden_viser_til_finnes(self):
        """VG11, ECH10. Ville feilet hvis ankeret ki-teksten eller delene som
        vinduet og siden viser til, ikke fantes i docs/installasjon.md."""
        inst = (ROT / "docs" / "installasjon.md").read_text(encoding="utf-8")
        assert '<a name="ki-teksten"></a>' in inst
        assert "<summary>Den lokale modellen for KI-teksten (valgfri)</summary>" in inst
        assert "<summary>Egen nøkkel til Gemini, Anthropic eller OpenAI (valgfri)</summary>" in inst
        assert "**Den lokale modellen uten Docker.**" in inst
        tekst = (START / "ki-modell.ps1").read_text(encoding="utf-8-sig")
        assert "$KiLokal = '«Den lokale modellen for KI-teksten»'" in tekst
        assert "$KiEgen = '«Egen nøkkel til Gemini, Anthropic eller OpenAI»'" in tekst

    def test_hentingen_skriver_linja_en_gang(self, stier):  # noqa: F811
        """VG15. Ville feilet hvis linja om Ollama sto to ganger."""
        raa, base = stier
        _, _, ut = kjoer(raa, base, SjekketModell("Ollama svarer ikke (kjører den?)"))
        linjer = [l for l in ut.splitlines() if "Ollama svarer ikke" in l]
        assert len(linjer) == 1 and "docs/installasjon.md" in linjer[0]


@WINDOWS
class TestKIValgetEtterGjennomgangen:
    """Funnene i KI-valget (tillegg 2 og 3)."""

    _tilby = staticmethod(TestKIValget._tilby)

    def test_et_svar_gjennom_lesingen_installerer(self, tmp_path, ollama):
        """VG1 (høy). Ville feilet hvis 1 lest fra vinduet ikke ga installasjonen."""
        klasse, url = ollama
        ut, _, kall = self._tilby(tmp_path, url, "", winget=True, inn="1\n")
        assert [k.split(" --")[0] for k in kall] == ["winget install", "ollama pull gemma4:e4b"], ut.stdout + ut.stderr

    def test_ollama_som_ikke_svarer_startes_og_ellers_beskjeden(self, tmp_path):
        """VG5, ECH7. Ville feilet hvis en Ollama som finnes, ikke ble startet
        med serve, eller hvis modellen ble hentet når Ollama ikke svarte."""
        ut, _, kall = self._tilby(tmp_path, _lukket_port(), "1", ollama_finnes=True)
        assert "ollama serve" in kall and "ollama pull gemma4:e4b" not in kall, kall
        assert "Ollama svarte ikke etter 1 sekunder." in ut.stdout and "appen starter" in ut.stdout

    def test_uten_winget_aapnes_siden_i_nettleseren(self, tmp_path, ollama):
        """VG6. Ville feilet hvis siden der Ollama lastes ned, ikke ble åpnet."""
        klasse, url = ollama
        foer = 'function Start-Process { Write-Host "FALSK START $args" };'
        ut, _, _ = self._tilby(tmp_path, url, "1", foer=foer, uten="")
        assert "FALSK START https://ollama.com/download" in ut.stdout, ut.stdout + ut.stderr

    def test_ingenting_annet_i_en_ny_env_endres(self, tmp_path, ollama):
        """VG7. Ville feilet hvis en .env fra .env.example, med «» og æøå i
        kommentarene, fikk andre linjer endret enn de to."""
        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        foer = (ROT / ".env.example").read_bytes()
        (rot / ".env").write_bytes(foer)
        self._tilby(tmp_path, url, "2", tjeneste="a", noekkel=FALSK_NOEKKEL)
        gamle = foer.decode("utf-8").splitlines()
        nye = (rot / ".env").read_bytes().decode("utf-8").splitlines()
        assert len(nye) == len(gamle)
        ulike = [(g, n) for g, n in zip(gamle, nye, strict=True) if g != n]
        assert ulike == [
            ("OSE_KI_TJENESTE=lokal", "OSE_KI_TJENESTE=anthropic"),
            ("OSE_KI_ANTHROPIC_NOKKEL=", f"OSE_KI_ANTHROPIC_NOKKEL={FALSK_NOEKKEL}"),
        ]

    @pytest.mark.parametrize(
        "linjer",
        [
            "OSE_KI_TJENESTE=lokal\r\nOSE_KI_TJENESTE=av\r\n",
            "OSE_KI_TJENESTE=gemini # egen nøkkel\r\n",
            "export OSE_KI_TJENESTE=openai\r\n",
        ],
    )
    def test_env_leses_som_hentingen_leser_den(self, tmp_path, ollama, linjer):
        """ECH2. Ville feilet hvis vinduet leste den første linja, en kommentar
        eller export annerledes enn python-dotenv, og spurte når hentingen har
        et annet valg."""
        from dotenv import dotenv_values

        klasse, url = ollama
        rot = tmp_path / "rot"
        rot.mkdir()
        (rot / ".env").write_bytes(linjer.encode("utf-8"))
        assert dotenv_values(rot / ".env")["OSE_KI_TJENESTE"] != "lokal"
        ut, _, kall = self._tilby(tmp_path, url, "1", winget=True)
        assert SPOERSMAAL_KI not in ut.stdout and kall == []

    def test_miljoeet_gaar_foran_env(self, tmp_path, ollama):
        """ECH3. Ville feilet hvis vinduet spurte når miljøet har en annen tjeneste."""
        klasse, url = ollama
        ut, _, kall = self._tilby(tmp_path, url, "1", winget=True, tjeneste_i_miljoeet="gemini")
        assert SPOERSMAAL_KI not in ut.stdout and kall == []

    def test_et_annet_svar_huskes_ikke(self, tmp_path, ollama):
        """ECH13. Ville feilet hvis et j, som i de andre spørsmålene, slo av
        spørsmålet for godt."""
        klasse, url = ollama
        ut, rot, kall = self._tilby(tmp_path, url, "j", winget=True)
        assert "Spørsmålet kommer igjen neste gang." in ut.stdout
        assert not (rot / "data").exists() and kall == []

    def test_winget_som_feiler_naar_ollama_finnes_etterpaa(self, tmp_path, ollama):
        """ECH8, BH7. Ville feilet hvis en kode fra winget når Ollama finnes
        etterpå (pakken var installert), stoppet hentingen av modellen."""
        klasse, url = ollama
        ut, _, kall = self._tilby(tmp_path, url, "1", winget=True, winget_kode="1")
        assert kall[-1] == "ollama pull gemma4:e4b" and "Gemma er hentet." in ut.stdout, ut.stdout


def _reglene(css: str) -> list[tuple[str, str]]:
    """(velgerne, innholdet) for hver regel i stilarket, uten kommentarene og
    uten @-blokkene rundt."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(v.strip(), i) for v, i in re.findall(r"([^{}@]+)\{([^{}]*)\}", css)]


class TestLenkefargen:
    """Spørsmål 26 (gruppens svar 12.11 kl. 19:06, tillegg 5 og 6): lenken
    «Slik slår du den på» har fargen til teksten rundt, med understrek, som de
    andre lenkene i appen. Regelen `a { color: inherit; … }` fra 8.26 gjør det
    etter flettingen av main 13.11, så stil.css trenger ingen egen regel."""

    def test_lenken_arver_fargen_og_er_understreket(self):
        """Ville feilet hvis den felles regelen for a ikke lenger arvet fargen,
        eller hvis en regel for lenken i .uten ga den en egen farge eller tok
        bort understreken, så den ble blå eller skilte seg fra de andre."""
        reglene = _reglene((ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8"))
        felles = [i for v, i in reglene if v == "a"]
        assert len(felles) == 1 and re.search(r"(^|;)\s*color:\s*inherit\s*(;|$)", felles[0]), felles
        assert "text-decoration:" not in felles[0].replace("text-decoration-", ""), felles
        for velgerne, innholdet in reglene:
            for velger in velgerne.split(","):
                if re.search(r"\.(uten|ki|boersdagen)\b[^,]*\ba\b", velger):
                    assert "color" not in innholdet and "text-decoration: none" not in innholdet, velger

    def test_malene_gir_lenken_ingen_egen_klasse(self):
        """Ville feilet hvis lenken fikk en klasse eller stil i malene, som en
        regel kunne farge annerledes enn teksten rundt."""
        for mal in ("aksje.html", "index.html"):
            tekst = (ROT / "src" / "templates" / mal).read_text(encoding="utf-8")
            assert tekst.count('<a href="{{ ki_teksten_url }}">Slik slår du den på</a>') == 1, mal
