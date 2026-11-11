"""Story 8.26: «Vis meg rundt» spiller av siden, knappene øverst og funnene
fra demoprøven (gruppens svar 11.11 kl. 16:58, 17:06, 17:12, 17:21, 17:44,
17:47, 17:48 og 17:53).

Spesifikasjonen er spec-8-26-vis-meg-rundt-spiller-av-siden.md, med delene.
Demoen lages i en midlertidig mappe, og den ekte versjonen fra en testbase
under tmp_path (regel 22). Ingen nettkall (AD-8).
"""

import html
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import hjelpetekster as ht
from lagring_sqlite import demo_sti

ROT = Path(__file__).resolve().parents[1]
SKRIPTET = ROT / "src" / "static" / "hjelp.js"
NODE = shutil.which("node")


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
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def ekte(tmp_path, monkeypatch):
    """Den ekte versjonen, fra en testbase under tmp_path."""
    import lagring_sqlite
    from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23

    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


def _raden(side: str) -> str:
    return side[side.index('<nav class="rad sider"') : side.index("</nav>")]


class _Node:
    def _kjoer(self, uttrykk: str):
        kode = f"const o = require({json.dumps(str(SKRIPTET))}); console.log(JSON.stringify({uttrykk}));"
        svar = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, timeout=60)
        assert svar.returncode == 0, svar.stderr
        return json.loads(svar.stdout)


# --- 1) «Vis meg rundt» spiller av siden, og knappene øverst ------------------


class TestKnappeneOeverst:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_begge_knappene_i_raden_med_ikon(self, versjon, request):
        """Svaret kl. 17:06: ville feilet hvis «Vis meg rundt» og «Spill av
        omvisningen» ikke sto i raden øverst etter «Innstillinger», som
        sideknapper med hvert sitt ikon, eller raden under demolinja sto
        igjen. Likt i demoen og i den ekte versjonen."""
        k = request.getfixturevalue(versjon)
        side = _side(k, "/")
        etter = _raden(side).split("Innstillinger</a>", 1)[1]
        knappene = re.findall(
            r'<button type="button" class="sideknapp ([\w-]+)"[^>]*hidden>(<svg class="ikon".*?</svg>)', etter
        )
        assert [k for k, _ in knappene] == ["vis-meg-rundt", "spill-av"]
        assert knappene[0][1] != knappene[1][1], "samme ikon på begge"
        assert "rundtur-rad" not in side and "<details" not in side.split("</header>")[0]

    def test_stegene_paa_knappen_er_sidens(self, klient):
        """Svaret kl. 16:58: ville feilet hvis «Vis meg rundt» hadde andre steg
        enn sidens egne i hjelpetekster.py."""
        side = _side(klient, "/boersometer")
        m = re.search(r'class="sideknapp vis-meg-rundt" data-steg="([^"]*)"', side)
        stegene = json.loads(html.unescape(m.group(1)))
        assert [s["anker"] for s in stegene] == [s.anker for s in ht.rundturer()["boersometer"]]


@pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")
class TestBoksenForSiden(_Node):
    def test_sidens_steg_blir_paa_siden(self):
        """Svaret kl. 16:58: ville feilet hvis et steg fra «Vis meg rundt»
        sendte brukeren til en annen side, eller ikke ble hoppet over når
        delen mangler, som i omvisningen."""
        liste = '[{"anker":"a","tittel":"A","tekst":"x"},{"anker":"b","tittel":"B","tekst":"y"}]'
        steg = self._kjoer(f"o.sidensSteg({liste})")
        assert {s["side"] for s in steg} == {"siden"}
        assert self._kjoer(f"o.nesteSteg(o.sidensSteg({liste}), 0, 1, o.SIDEN, (a) => a !== 'a')") == 1
        assert self._kjoer(f"o.knappene(o.sidensSteg({liste}), 1, o.SIDEN, () => true)") == {
            "tilbake": True,
            "ferdig": True,
        }
        assert self._kjoer("o.sidensSteg('feil')") == []

    def test_siste_steg_har_lenken_til_hele_omvisningen(self):
        """Svaret kl. 16:58: ville feilet hvis siste steg med «Vis meg rundt»
        manglet «Ferdig» og lenken «Spill av hele omvisningen», eller den
        sto i hele omvisningen også."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        vis = skriptet[skriptet.index("  function vis(j) {") :]
        vis = vis[: vis.index("\n  }\n")]
        assert 'knapp(siste ? "Ferdig" : "Neste"' in vis
        assert "if (siste && aktive !== steg) {" in vis
        assert '"Spill av hele omvisningen"' in vis

    def test_vis_meg_rundt_lagrer_ingen_omvisning(self):
        """Ville feilet hvis «Vis meg rundt» lagret steget som omvisningen
        fortsetter fra på neste side, så en annen side åpnet boksen."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        assert (
            "if (aktive === steg) skriv(sessionStorage, OMVISNING.STEGET, OMVISNING.tilstand(j, 1, her()));" in skriptet
        )
        assert 'document.querySelectorAll("button.vis-meg-rundt[hidden]")' in skriptet
