"""Story 3.6: ikonet og snarveien (del C, gruppens svar 10.11 kl. 14:07, og
tillegget om demoen kl. 15:57). Spesifikasjonen er
spec-3-6-ikonet-og-snarveien.md.

Ikonet prøves mot logoen i _ramme.html og mot filene i src/static, og
snarveien med PowerShell på Windows, med et skrivebord i tmp_path. Ingen
nettkall, og ingen snarvei lages på det ekte skrivebordet.
"""

import os
import re
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import ikon
from lagring_sqlite import demo_sti

ROT = Path(__file__).resolve().parent.parent
STATIC = ROT / "src" / "static"
POWERSHELL = shutil.which("powershell")


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def klient(mal, monkeypatch):
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    return app_modul.app.test_client()


class TestIkonet:
    """Del 1: ikonet av logoen, som SVG, PNG og ICO, uten nye avhengigheter."""

    def test_filene_i_repoet_er_det_modulen_lager(self):
        """Ville feilet hvis en fil i src/static var laget av en annen tegning
        enn src/ikon.py, eller manglet."""
        for navn, data in ikon.filene().items():
            assert (STATIC / navn).read_bytes() == data, navn

    def test_stoerrelsene(self):
        """Ville feilet hvis en PNG hadde en annen størrelse enn navnet sier,
        eller ICO-fila manglet en størrelse til snarveien."""
        for n in ikon.IKON_STOERRELSER:
            data = (STATIC / f"ikon-{n}.png").read_bytes()
            assert data[:8] == b"\x89PNG\r\n\x1a\n"
            assert struct.unpack(">II", data[16:24]) == (n, n)
        ico = (STATIC / "ikon.ico").read_bytes()
        _, art, antall = struct.unpack("<HHH", ico[:6])
        assert (art, antall) == (1, len(ikon.ICO_STOERRELSER))
        stoerrelser = [ico[6 + 16 * i] or 256 for i in range(antall)]
        assert stoerrelser == list(ikon.ICO_STOERRELSER)

    def test_soeylene_er_logoen_i_toppen(self):
        """Ville feilet hvis ikonet hadde andre søyler enn logoen i toppen,
        eller den høye ikke var oransje."""
        ramme = (ROT / "src" / "templates" / "_ramme.html").read_text(encoding="utf-8")
        logo = ramme.split('<p class="logo">', 1)[1].split("</svg>", 1)[0]
        rektangler = re.findall(
            r'<rect class="soeyle( hoey)?" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)"/>',
            logo,
        )
        assert [
            (float(x), float(y), float(b), float(h), float(r), bool(hoey)) for hoey, x, y, b, h, r in rektangler
        ] == list(ikon.SOEYLENE)
        stil = (STATIC / "stil.css").read_text(encoding="utf-8")
        assert f"--oransje: #{''.join(f'{c:02X}' for c in ikon.ORANSJE)}" in stil
        assert f"--blekk: #{''.join(f'{c:02X}' for c in ikon.BLEKK)}" in stil
        assert ikon.svg().count("<rect") == 4

    @pytest.mark.parametrize("sti", ["/", "/min-liste", "/boersometer", "/aksje/BRFE", "/innstillinger", "/folg"])
    def test_hver_side_viser_ikonet_i_fanen(self, klient, sti):
        """Ville feilet hvis en side manglet ikonet i fanen, eller filen ikke
        kunne hentes. Demoen og den ekte versjonen bruker samme ramme."""
        html = klient.get(sti).get_data(as_text=True)
        for href in ("/static/ikon.svg", "/static/ikon-32.png", "/static/ikon-180.png"):
            assert f'href="{href}"' in html, (sti, href)
        assert klient.get("/static/ikon.svg").status_code == 200

    def test_ingen_nye_avhengigheter(self):
        """Ville feilet hvis ikonet trengte et bibliotek utenfor standardbiblioteket."""
        kilde = (ROT / "src" / "ikon.py").read_text(encoding="utf-8")
        importer = set(re.findall(r"^(?:import|from) (\w+)", kilde, re.M))
        assert importer <= {"struct", "zlib", "pathlib"}, importer


def _ps(skript: str, miljoe: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", skript],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, **miljoe},
        timeout=60,
    )


@pytest.mark.skipif(os.name != "nt" or POWERSHELL is None, reason="snarveien lages bare i Windows")
class TestSnarveien:
    """Del 2: snarveien på skrivebordet i Windows, første gang."""

    @staticmethod
    def _tilby(tmp_path, versjon, svar=None, ja=None):
        rot = tmp_path / "rot"
        rot.mkdir(exist_ok=True)
        skrivebord = tmp_path / "skrivebord"
        skrivebord.mkdir(exist_ok=True)
        miljoe = {
            "OSE_SKRIVEBORD": str(skrivebord),
            "OSE_START_SVAR_SNARVEI": svar or "",
            "OSE_START_SVAR_JA": ja or "",
        }
        skript = (
            "[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
            f". '{ROT / 'start' / 'snarvei.ps1'}'; Tilby-Snarvei {versjon} '{rot}'"
        )
        return _ps(skript, miljoe), rot, skrivebord

    @staticmethod
    def _maalet(lnk: Path) -> tuple[str, str]:
        ut = _ps(
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}'); "
            "[Console]::OutputEncoding = [Text.Encoding]::UTF8; Write-Output $s.TargetPath; Write-Output $s.IconLocation",
            {},
        ).stdout.splitlines()
        return ut[0], ut[1]

    @pytest.mark.parametrize(
        ("versjon", "navn", "fil"),
        [("ekte", "OSE Signal", "Start den ekte versjonen.cmd"), ("demo", "OSE Signal (demo)", "Start demoen.cmd")],
    )
    def test_ja_lager_snarveien_med_ikonet(self, tmp_path, versjon, navn, fil):
        """Ville feilet hvis snarveien ikke ble laget, startet en annen fil
        enn dobbeltklikket, manglet ikonet, eller demoen fikk samme navn."""
        svar, rot, skrivebord = self._tilby(tmp_path, versjon, "j")
        lnk = skrivebord / f"{navn}.lnk"
        assert lnk.exists(), svar.stdout + svar.stderr
        maal, ikonet = self._maalet(lnk)
        assert Path(maal) == rot / fil
        assert ikonet.lower().endswith("ikon.ico,0")

    def test_nei_huskes_og_spoersmaalet_kommer_ikke_igjen(self, tmp_path):
        """Ville feilet hvis et nei ikke ble husket, så vinduet spurte hver gang."""
        svar, rot, skrivebord = self._tilby(tmp_path, "ekte", "n")
        assert not list(skrivebord.iterdir())
        assert (rot / "data" / "snarvei-nei-ekte").exists()
        assert "spør ikke igjen" in svar.stdout
        # Nå svares ja, men nei er husket, så det spørres ikke og lages ingen snarvei.
        svar, _, skrivebord = self._tilby(tmp_path, "ekte", "j")
        assert not list(skrivebord.iterdir()) and svar.stdout.strip() == ""

    def test_finnes_snarveien_spoerres_det_ikke(self, tmp_path):
        """Ville feilet hvis vinduet spurte igjen når snarveien finnes."""
        self._tilby(tmp_path, "ekte", "j")
        svar, rot, _ = self._tilby(tmp_path, "ekte", "n")
        assert svar.stdout.strip() == "" and not (rot / "data" / "snarvei-nei-ekte").exists()

    def test_ci_gir_ingen_snarvei(self, tmp_path):
        """Ville feilet hvis CI (OSE_START_SVAR_JA=1) laget en snarvei eller ventet på et svar."""
        svar, rot, skrivebord = self._tilby(tmp_path, "ekte", None, "1")
        assert svar.returncode == 0 and not list(skrivebord.iterdir()) and not (rot / "data").exists()


class TestStartskriptet:
    def test_startskriptet_tilbyr_snarveien_naar_appen_svarer(self):
        """Ville feilet hvis start.ps1 ikke tilbød snarveien, eller gjorde det
        før appen svarte."""
        tekst = (ROT / "start" / "start.ps1").read_text(encoding="utf-8-sig")
        assert ". (Join-Path $PSScriptRoot 'snarvei.ps1')" in tekst
        assert tekst.index("Tilby-Snarvei $Versjon") > tekst.index("if (-not $klar) { Stopp")
        assert (ROT / "start" / "snarvei.ps1").read_bytes().startswith(b"\xef\xbb\xbf")


class TestDokumentene:
    """Del 3: README-en og installasjonen sier det, og at mobil kommer senere."""

    def test_readme_og_installasjonen(self):
        """Ville feilet hvis README-en eller installasjonen ikke nevnte
        snarveien, ikonet eller at mobil kommer senere."""
        readme = (ROT / "README.md").read_text(encoding="utf-8")
        assert "snarveien «OSE Signal» med ikonet på skrivebordet" in readme
        assert "Mobil kommer i en senere versjon" in readme
        inst = (ROT / "docs" / "installasjon.md").read_text(encoding="utf-8")
        assert "snarveien «OSE Signal» på skrivebordet, eller «OSE Signal (demo)» for demoen" in inst
        assert "](../src/static/ikon-48.png)" in inst and "Mobil kommer i en senere versjon." in inst
