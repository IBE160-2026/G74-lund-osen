"""Story 8.0f: hjelpen ved «?» i ett fast felt, prøvd i nettleseren.

Siden lages av Flasks testklient og skrives til en midlertidig mappe sammen
med src/static/, og Edge eller Chrome uten hode åpner den med file:// og
--dump-dom. Siden står i en iframe så bred som bredden testen gjelder, fordi
vinduet uten hode er minst 504 px og ikke akkurat så bredt som bedt om. Et
testskript nederst på siden trykker på knappene og sender målingene som JSON
til rammen, som skriver dem i sin side. Ingen server, ingen port og ingenting fra nettet
(AD-8). Finnes ingen nettleser, hoppes testene over.
"""

import html as html_modul
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
# Gjennomgangen (BH6, VG6): i CI (GitHub setter CI) feiler testene når
# nettleseren mangler, i stedet for å hoppes over uten at noen ser det.
pytestmark = pytest.mark.skipif(
    NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome å prøve feltet i"
)

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
  r.bredde = document.documentElement.clientWidth;
  r.skrift = document.fonts.check('16px "IBM Plex Sans"');
  parent.postMessage(JSON.stringify(r), "*");
}
"""


def _side(html: str, skript: str, foer: str = "") -> str:
    """Siden med adressene til static/ ved siden av, foer i <head> før
    hjelpeskriptet og testskriptet nederst. Testskriptet venter på skriftene
    (gjennomgangen, BH2)."""
    assert html.count("<head>") == 1 and html.count("</body>") == 1
    side = html.replace('href="/static/', 'href="static/').replace('src="/static/', 'src="static/')
    side = side.replace("<head>", "<head>" + foer, 1)
    test = (
        "<script>"
        + HJELPERE
        + "window.addEventListener('load', async () => { await document.fonts.ready;"
        + skript
        + "});</script>"
    )
    return side.replace("</body>", test + "</body>", 1)


def _kjoer(html: str, mappe: Path, bredde: int, skript: str, foer: str = "", neste: tuple | None = None) -> dict:
    """Skriver siden med testskriptet til mappe, åpner den i nettleseren og
    gir tilbake det testskriptet skrev. foer settes inn i <head> før
    hjelpeskriptet. neste er (html, skript) for en side til, som skriptet på
    den første kan gå til med location.href = "neste.html"."""
    assert NETTLESER, "ingen Edge eller Chrome å prøve feltet i, og CI krever det"
    if not (mappe / "static").exists():
        shutil.copytree(STATIC, mappe / "static")
        # Gjennomgangen (BH2): skriftene ligger i static/fonts/ ved siden av,
        # så testene måler med de samme skriftene som appen.
        stil = mappe / "static" / "stil.css"
        stil.write_text(stil.read_text(encoding="utf-8").replace('url("/static/', 'url("'), encoding="utf-8")
    fil = mappe / f"side-{bredde}.html"
    fil.write_text(_side(html, skript, foer), encoding="utf-8")
    if neste:
        (mappe / "neste.html").write_text(_side(*neste), encoding="utf-8")
    ramme = mappe / f"ramme-{bredde}.html"
    ramme.write_text(
        "<!doctype html><body style='margin:0'>"
        f"<iframe src='{fil.name}' style='border:0;width:{bredde}px;height:900px'></iframe>"
        "<script>addEventListener('message', (e) => { const pre = document.createElement('pre');"
        " pre.id = 'resultat'; pre.textContent = e.data; document.body.append(pre); });</script></body>",
        encoding="utf-8",
    )
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
        # Gjennomgangen (BH6): ingenting fra nettet, heller ikke fra
        # nettleseren selv (AD-8).
        "--proxy-server=127.0.0.1:9",
        "--host-resolver-rules=MAP * ~NOTFOUND",
        f"--user-data-dir={profil}",
        f"--window-size={bredde + 100},1000",
        "--virtual-time-budget=10000",
        "--dump-dom",
        ramme.as_uri(),
    ]
    if sys.platform.startswith("linux"):
        kommando.insert(1, "--no-sandbox")
    ut = subprocess.run(kommando, capture_output=True, text=True, encoding="utf-8", timeout=120)
    treff = re.search(r'<pre id="resultat">(.*?)</pre>', ut.stdout, re.DOTALL)
    assert treff, ut.stderr[-2000:]
    svar = json.loads(html_modul.unescape(treff.group(1)))
    assert svar.pop("bredde") == bredde, "siden ble ikke så bred som testen gjelder"
    assert svar.pop("skrift") is True, "skriftene fra appen ble ikke lastet"
    return svar


@pytest.fixture
def sidene(klient, base):  # noqa: F811
    return {a: klient.get(a).data.decode("utf-8") for a in ("/aksje/BRFE", "/", "/boersometer")}


class TestFeltetDekkerIkke:
    @pytest.mark.parametrize("bredde", [1280, 390])
    @pytest.mark.parametrize("adresse", ["/aksje/BRFE", "/", "/boersometer"])
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
          const ut = {knapper: 0, hoppet: [], dekket: {}, aapne: [], fast: []};
          for (const k of document.querySelectorAll("button.hjelpeknapp")) {
            if (!k.getClientRects().length) { ut.hoppet.push(k.getAttribute("popovertarget")); continue; }
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
        # Gjennomgangen (BH9): hvert «?» på siden er prøvd.
        assert r["knapper"] + len(r["hoppet"]) == sidene[adresse].count('class="hjelpeknapp"'), r
        assert r["knapper"] >= 1 and r["hoppet"] == [], r
        assert r["dekket"] == {}, r["dekket"]
        assert set(r["aapne"]) == {1}, r
        assert set(r["fast"]) == ({"fixed"} if bredde == 1280 else {"absolute"}), r


class TestEttFelt:
    @pytest.mark.parametrize("bredde", [1280, 390])
    def test_et_nytt_spoersmaalstegn_bytter_innholdet(self, sidene, tmp_path, bredde):
        """Kontrollpunktet: et nytt «?» bytter innholdet. Ville feilet hvis
        to vinduer sto åpne samtidig, «?» for det åpne feltet lukket det, et
        klikk utenfor lukket det (vinduene er manual med skriptet,
        gjennomgangen BH5), eller den tomme plassen ble stående etter byttet
        på smal skjerm (VG4)."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            bredde,
            """
          const [a, b] = document.querySelectorAll("main button.hjelpeknapp");
          a.click(); await vent();
          const foerst = aapne().map((f) => f.id);
          b.click(); await vent();
          const saa = aapne().map((f) => f.id);
          b.click(); await vent();
          const igjen = aapne().map((f) => f.id);
          const plasser = document.querySelectorAll(".hjelpeplass").length;
          const d = dekket(document.getElementById(b.getAttribute("popovertarget")));
          const manual = Array.from(document.querySelectorAll(".hjelpevindu")).every((f) => f.popover === "manual");
          for (const type of ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]) {
            document.body.dispatchEvent(new PointerEvent(type, {bubbles: true, clientX: 5, clientY: 5}));
          }
          await vent();
          ferdig({a: a.getAttribute("popovertarget"), b: b.getAttribute("popovertarget"),
                  foerst, saa, igjen, plasser, dekket: d, manual, etter_klikk_utenfor: aapne().map((f) => f.id)});
        """,
        )
        assert r["a"] != r["b"]
        assert r["foerst"] == [r["a"]]
        assert r["saa"] == [r["b"]]
        assert r["igjen"] == [r["b"]]
        assert r["etter_klikk_utenfor"] == [r["b"]] and r["manual"] is True
        assert r["plasser"] == (0 if bredde == 1280 else 1) and r["dekket"] == [], r

    @pytest.mark.parametrize("bredde", [1280, 390])
    @pytest.mark.parametrize("maate", ["Esc", "Lukk"])
    def test_esc_og_lukk_lukker_og_fokus_gaar_tilbake(self, sidene, tmp_path, maate, bredde):
        """Kontrollpunktet: Esc og «Lukk» lukker, feltet får fokus når det
        åpnes, og fokus går tilbake til «?» når det lukkes. Ville feilet hvis
        Esc ikke lukket feltet (popover="manual" lukker ikke selv), fokus ble
        liggende i et lukket felt, den tomme plassen ble stående (VG5), eller
        siden bladde tilbake til «?» da feltet ble lukket på bred skjerm
        etter at man hadde bladd (gjennomgangen, BH1)."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            bredde,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          k.focus(); k.click(); await vent();
          const aapen = aapne().length, fokus_i_feltet = document.activeElement === felt;
          const bred = getComputedStyle(felt).position === "fixed";
          if (bred) { scrollTo(0, 600); await vent(); }
          const y = scrollY;
          if (%s) {
            document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {key: "Escape", bubbles: true}));
          } else {
            felt.querySelector("button.lukk").click();
          }
          await vent();
          ferdig({aapen, fokus_i_feltet, etter: aapne().length, fokus_paa_knappen: document.activeElement === k,
                  plasser: document.querySelectorAll(".hjelpeplass").length,
                  blar_ikke: !bred || (y > 0 && scrollY === y)});
        """
            % ("true" if maate == "Esc" else "false"),
        )
        assert r == {
            "aapen": 1,
            "fokus_i_feltet": True,
            "etter": 0,
            "fokus_paa_knappen": True,
            "plasser": 0,
            "blar_ikke": True,
        }


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
        """Valget huskes mens man blar: knappen trykkes på aksjesiden, og
        oversikten i samme fane åpner feltet til venstre (gjennomgangen,
        BH10). Ville feilet hvis feltet startet til høyre på neste side."""
        r = _kjoer(
            sidene["/aksje/BRFE"],
            tmp_path,
            1280,
            """
          const k = document.querySelector("main button.hjelpeknapp");
          k.click(); await vent();
          document.getElementById(k.getAttribute("popovertarget")).querySelector("button.flytt").click();
          await vent();
          location.href = "neste.html";
        """,
            neste=(
                sidene["/"],
                """
          const k = document.querySelector("main button.hjelpeknapp");
          k.click(); await vent();
          const felt = document.getElementById(k.getAttribute("popovertarget"));
          ferdig({x: felt.getBoundingClientRect().right, tekst: felt.querySelector("button.flytt").textContent,
                  dekket: dekket(felt), side: document.body.className});
        """,
            ),
        )
        assert r.pop("side") != "side-aksje", r
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
          let kastet = false;
          try { sessionStorage.getItem("x"); } catch { kastet = true; }
          ferdig({aapen, kastet, x: felt.getBoundingClientRect().right, klasse: document.documentElement.className});
        """,
            foer="""<script>Object.defineProperty(window, "sessionStorage",
                     {get() { throw new DOMException("slått av", "SecurityError"); }});</script>""",
        )
        assert r["kastet"] is True, "lagringen ble ikke slått av i testen (gjennomgangen, BH12)"
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
