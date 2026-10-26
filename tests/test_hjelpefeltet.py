"""Story 8.0f: hjelpen ved «?» i ett fast felt, prøvd i nettleseren.

Siden lages av Flasks testklient og skrives til en midlertidig mappe sammen
med src/static/, og Edge eller Chrome uten hode åpner den med file:// og
--dump-dom. Et testskript nederst på siden trykker på knappene og skriver
målingene som JSON i siden. Ingen server, ingen port og ingenting fra nettet
(AD-8). Finnes ingen nettleser, hoppes testene over.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_hjelpetekster import base, basemal, klient  # noqa: F401

ROT = Path(__file__).resolve().parent.parent
STATIC = ROT / "src" / "static"

_KANDIDATER = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def _nettleser() -> str | None:
    for navn in ("msedge", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        sti = shutil.which(navn)
        if sti:
            return sti
    return next((k for k in _KANDIDATER if os.path.exists(k)), None)


NETTLESER = _nettleser()
pytestmark = pytest.mark.skipif(NETTLESER is None, reason="ingen Edge eller Chrome å prøve feltet i")

# Hjelperne testskriptene bygger på. tekst() er rutene rundt hver bit synlig
# tekst utenfor feltet, og dekket() de som overlapper feltet. På bred skjerm
# står feltet fast, så det dekker hele høyden av siden når man blar.
HJELPERE = r"""
const vent = (ms) => new Promise((r) => setTimeout(r, ms || 30));
const aapne = () => Array.from(document.querySelectorAll(".hjelpevindu:popover-open"));
function klippet(el) {
  for (let a = el; a && a !== document.body; a = a.parentElement) {
    const s = getComputedStyle(a);
    if (s.clip !== "auto" || s.visibility === "hidden") return true;
  }
  return false;
}
function tekst(felt) {
  const ut = [];
  const gaa = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = gaa.nextNode(); n; n = gaa.nextNode()) {
    // Tekst i <title> i en SVG og tekst som bare er for skjermlesere
    // (klippet til 1 × 1 px), vises ikke.
    if (!n.data.trim() || n.parentElement.closest(".hjelpevindu, script, pre#resultat, title")) continue;
    if (klippet(n.parentElement)) continue;
    const r = document.createRange();
    r.selectNodeContents(n);
    for (const b of r.getClientRects()) if (b.width > 1 && b.height > 1) ut.push([b, n.data.trim().slice(0, 30)]);
  }
  return ut;
}
function dekket(felt) {
  const f = felt.getBoundingClientRect();
  const fast = getComputedStyle(felt).position === "fixed";
  return tekst(felt)
    .filter(([b]) => b.left < f.right - 0.5 && b.right > f.left + 0.5 &&
                     (fast || (b.top < f.bottom - 0.5 && b.bottom > f.top + 0.5)))
    .map(([, t]) => t);
}
function ferdig(r) {
  const pre = document.createElement("pre");
  pre.id = "resultat";
  pre.textContent = JSON.stringify(r);
  document.body.append(pre);
}
"""


def _kjoer(html: str, mappe: Path, bredde: int, skript: str, foer: str = "") -> dict:
    """Skriver siden med testskriptet til mappe, åpner den i nettleseren og
    gir tilbake det testskriptet skrev. foer settes inn i <head> før
    hjelpeskriptet."""
    if not (mappe / "static").exists():
        shutil.copytree(STATIC, mappe / "static")
    side = html.replace('href="/static/', 'href="static/').replace('src="/static/', 'src="static/')
    side = side.replace("<head>", "<head>" + foer, 1)
    test = "<script>" + HJELPERE + "window.addEventListener('load', async () => {" + skript + "});</script>"
    side = side.replace("</body>", test + "</body>", 1)
    fil = mappe / f"side-{bredde}.html"
    fil.write_text(side, encoding="utf-8")
    profil = mappe / f"profil-{bredde}"
    kommando = [
        NETTLESER,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-sync",
        "--disable-extensions",
        f"--user-data-dir={profil}",
        f"--window-size={bredde},900",
        "--virtual-time-budget=10000",
        "--dump-dom",
        fil.as_uri(),
    ]
    if sys.platform.startswith("linux"):
        kommando.insert(1, "--no-sandbox")
    ut = subprocess.run(kommando, capture_output=True, text=True, encoding="utf-8", timeout=120)
    treff = re.search(r'<pre id="resultat">(.*?)</pre>', ut.stdout, re.DOTALL)
    assert treff, ut.stderr[-2000:]
    return json.loads(
        treff.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    )


@pytest.fixture
def sidene(klient, base):  # noqa: F811
    return {a: klient.get(a).data.decode("utf-8") for a in ("/aksje/BRFE", "/")}


class TestFeltetDekkerIkke:
    @pytest.mark.parametrize("bredde", [1280, 390])
    @pytest.mark.parametrize("adresse", ["/aksje/BRFE", "/"])
    def test_ingen_tekst_under_feltet(self, sidene, tmp_path, bredde, adresse):
        """Kontrollpunktet: feltet dekker ikke teksten ved 1280 og 390 px.
        Hvert «?» på siden åpnes etter tur, og ingen synlig tekst utenfor
        feltet ligger under det. Ville feilet hvis siden ikke ga plass på
        bred skjerm, eller feltet på smal skjerm lå over teksten under «?»
        i stedet for over en tom plass."""
        r = _kjoer(
            sidene[adresse],
            tmp_path,
            bredde,
            """
          const ut = {knapper: 0, dekket: {}, aapne: [], fast: []};
          for (const k of document.querySelectorAll("button.hjelpeknapp")) {
            if (!k.getClientRects().length) continue;
            k.click(); await vent();
            const felt = document.getElementById(k.getAttribute("popovertarget"));
            ut.knapper += 1;
            ut.aapne.push(aapne().length);
            ut.fast.push(getComputedStyle(felt).position);
            const d = dekket(felt);
            if (d.length) ut.dekket[k.getAttribute("popovertarget")] = d;
            felt.querySelector("button.lukk").click(); await vent();
          }
          ferdig(ut);
        """,
        )
        assert r["knapper"] >= 5, r
        assert r["dekket"] == {}, r["dekket"]
        assert set(r["aapne"]) == {1}, r
        assert set(r["fast"]) == ({"fixed"} if bredde == 1280 else {"absolute"}), r


class TestEttFelt:
    def test_et_nytt_spoersmaalstegn_bytter_innholdet(self, sidene, tmp_path):
        """Kontrollpunktet: et nytt «?» bytter innholdet. Ville feilet hvis
        to vinduer sto åpne samtidig, eller «?» for det åpne feltet lukket
        det."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            1280,
            """
          const [a, b] = document.querySelectorAll("main button.hjelpeknapp");
          a.click(); await vent();
          const foerst = aapne().map((f) => f.id);
          b.click(); await vent();
          const saa = aapne().map((f) => f.id);
          b.click(); await vent();
          const igjen = aapne().map((f) => f.id);
          document.body.click(); await vent();
          ferdig({a: a.getAttribute("popovertarget"), b: b.getAttribute("popovertarget"),
                  foerst, saa, igjen, etter_klikk_utenfor: aapne().map((f) => f.id)});
        """,
        )
        assert r["a"] != r["b"]
        assert r["foerst"] == [r["a"]]
        assert r["saa"] == [r["b"]]
        assert r["igjen"] == [r["b"]]
        assert r["etter_klikk_utenfor"] == [r["b"]]

    @pytest.mark.parametrize("maate", ["Esc", "Lukk"])
    def test_esc_og_lukk_lukker_og_fokus_gaar_tilbake(self, sidene, tmp_path, maate):
        """Kontrollpunktet: Esc og «Lukk» lukker, feltet får fokus når det
        åpnes, og fokus går tilbake til «?» når det lukkes. Ville feilet hvis
        Esc ikke lukket feltet (popover="manual" lukker ikke selv), eller
        fokus ble liggende i et lukket felt."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            1280,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          k.focus(); k.click(); await vent();
          const aapen = aapne().length, fokus_i_feltet = document.activeElement === felt;
          if (%s) {
            document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {key: "Escape", bubbles: true}));
          } else {
            felt.querySelector("button.lukk").click();
          }
          await vent();
          ferdig({aapen, fokus_i_feltet, etter: aapne().length, fokus_paa_knappen: document.activeElement === k});
        """
            % ("true" if maate == "Esc" else "false"),
        )
        assert r == {"aapen": 1, "fokus_i_feltet": True, "etter": 0, "fokus_paa_knappen": True}


class TestKnappenFlytter:
    def test_knappen_bytter_side_og_valget_huskes(self, sidene, tmp_path):
        """Kontrollpunktet: knappen bytter side, og valget huskes mens man
        blar. Ville feilet hvis feltet ble stående til høyre, siden ga plass
        på feil side, eller valget ikke ble lagret."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            1280,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          k.click(); await vent();
          const flytt = felt.querySelector("button.flytt");
          const foer = {x: felt.getBoundingClientRect().left, tekst: flytt.textContent};
          flytt.click(); await vent();
          const etter = {x: felt.getBoundingClientRect().right, tekst: flytt.textContent,
                         dekket: dekket(felt), lagret: sessionStorage.getItem("hjelpefelt-side")};
          flytt.click(); await vent();
          ferdig({foer, etter, tilbake: felt.getBoundingClientRect().left, lagret: sessionStorage.getItem("hjelpefelt-side")});
        """,
        )
        assert r["foer"]["x"] > 800 and r["foer"]["tekst"] == "Flytt til venstre", r
        assert r["etter"]["x"] < 480 and r["etter"]["tekst"] == "Flytt til høyre", r
        assert r["etter"]["dekket"] == [] and r["etter"]["lagret"] == "venstre", r
        assert r["tilbake"] > 800 and r["lagret"] == "hoeyre", r

    def test_neste_side_husker_venstre(self, sidene, tmp_path):
        """Valget huskes mens man blar: en ny side i samme fane leser det.
        Ville feilet hvis feltet startet til høyre på neste side."""
        r = _kjoer(
            sidene["/"],
            tmp_path,
            1280,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          k.click(); await vent();
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          ferdig({x: felt.getBoundingClientRect().right, tekst: felt.querySelector("button.flytt").textContent,
                  dekket: dekket(felt)});
        """,
            foer="<script>sessionStorage.setItem('hjelpefelt-side', 'venstre');</script>",
        )
        assert r["x"] < 480 and r["tekst"] == "Flytt til høyre" and r["dekket"] == [], r

    def test_uten_lagring_flyttes_feltet_likevel(self, sidene, tmp_path):
        """Lagringen i nettleseren tåler å være slått av. Ville feilet hvis
        skriptet stoppet på unntaket fra sessionStorage, så hjelpen ikke
        åpnet seg eller knappen ikke flyttet feltet."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            1280,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          k.click(); await vent();
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          const aapen = aapne().length;
          felt.querySelector("button.flytt").click(); await vent();
          ferdig({aapen, x: felt.getBoundingClientRect().right, klasse: document.documentElement.className});
        """,
            foer="""<script>Object.defineProperty(window, "sessionStorage",
                     {get() { throw new DOMException("slått av", "SecurityError"); }});</script>""",
        )
        assert r["aapen"] == 1 and r["x"] < 480 and "felt-venstre" in r["klasse"], r

    @pytest.mark.parametrize("bredde", [390])
    def test_knappen_staar_bare_paa_bred_skjerm(self, sidene, tmp_path, bredde):
        """Ville feilet hvis knappen sto på smal skjerm, der feltet står
        under «?» og ikke kan flyttes."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            bredde,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          k.click(); await vent();
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          ferdig({synlig: felt.querySelector("button.flytt").getClientRects().length});
        """,
        )
        assert r["synlig"] == 0, r
