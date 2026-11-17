"""Story 9.18: rettingene før brukertest 2 (gruppens svar 17.11 kl. 13:03–13:33).

Funnene er fra den heuristiske evalueringen (docs/heuristisk-evaluering.md).
Testene i nettleseren bruker fremgangsmåten i test_hjelpefeltet.py: ingen
server og ingenting fra nettet (AD-8), og de hoppes over uten Edge eller
Chrome, unntatt i CI.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import app as app_modul
from test_hjelpefeltet import NETTLESER, _kjoer
from test_hjelpetekster import base, basemal, klient  # noqa: F401

# Uten Edge eller Chrome hoppes testene i nettleseren over, unntatt i CI.
I_NETTLESEREN = pytest.mark.skipif(NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome")


def _tekst(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


@pytest.fixture
def side(klient, base):  # noqa: F811
    def hent(adresse: str) -> str:
        svar = klient.get(adresse)
        assert svar.status_code == 200, adresse
        return svar.get_data(as_text=True)

    return hent


RAD = re.compile(
    r'<td class="selskap">(.*?)</td>.*?<td class="tall styrke">(.*?)</td>\s*<td class="retning">(.*?)</td>', re.S
)


class TestTabellenPaaSmalSkjerm:
    """HE3: på smal skjerm står styrken og retningen under selskapsnavnet, så
    kjernen synes uten å dra tabellen sidelengs. Tabellen ruller fortsatt i
    sin boks (avgjørelsen 17.10 om tabellen på smal skjerm)."""

    @pytest.mark.parametrize("adresse", ["/", "/min-liste?vis=alle"])
    def test_hver_rad_har_styrken_og_retningen_under_navnet(self, side, adresse):
        """Ville feilet uten linja under navnet, eller med en annen styrke
        eller retning enn kolonnene i samme rad."""
        rader = RAD.findall(side(adresse))
        assert len(rader) > 5, adresse
        for selskap, styrke, retning in rader:
            treff = re.search(r'<span class="smal-signal" aria-hidden="true">(.*)', selskap, re.S)
            assert treff, selskap[:200]
            linja = _tekst(treff.group(1).split('<span class="hentet"')[0].split('<span class="egen-dag"')[0])
            styrken = re.match(r"\d av \d\b", _tekst(styrke))
            if styrken:
                assert linja.startswith(styrken.group(0) + " · "), (linja, _tekst(styrke))
                symbol, ord_ = re.search(r'aria-hidden="true">([^<]+)</span>\s*([^<]+)</span>', retning).groups()
                assert linja.endswith(f"{symbol.strip()} {ord_.strip()}"), (linja, _tekst(retning))
            else:
                assert _tekst(styrke).startswith(linja), (linja, _tekst(styrke))
                assert linja.startswith("– ")

    def test_linja_vises_bare_paa_smal_skjerm(self):
        """Ville feilet hvis linja sto på bred skjerm også, eller ikke ble vist
        på smal skjerm."""
        from test_utseende import STILARKET, _reglene

        reglene = _reglene(STILARKET.read_text(encoding="utf-8"))
        kropper = {(ramme, velger): kropp for ramme, velger, kropp in reglene}
        velger = ":where(.side-oversikt) td.selskap .smal-signal"
        assert "display: none" in kropper[("", velger)]
        # Story 9.19: bruddet er der kolonnen for retningen slutter å få
        # plass, ikke 760 px (TestBareEnGangIAlleBredder).
        assert "display: block" in kropper[("@media (width < 743px)", velger)]

    @pytest.mark.parametrize("bredde, synlig", [(390, True), (1280, False)])
    @I_NETTLESEREN
    def test_i_nettleseren(self, side, tmp_path, bredde, synlig):
        """Ville feilet hvis styrken og retningen lå utenfor skjermen ved
        390 px, eller linja sto under navnet ved 1280 px."""
        skript = """
          const boks = document.querySelector(".tabellboks").getBoundingClientRect();
          const linjer = Array.from(document.querySelectorAll(".tabellboks .smal-signal"));
          const synlige = linjer.filter((l) => l.getBoundingClientRect().width > 0);
          const utenfor = synlige.filter((l) => l.getBoundingClientRect().right > boks.right + 0.5);
          const styrke = document.querySelector(".tabellboks td.styrke").getBoundingClientRect();
          ferdig({linjer: linjer.length, synlige: synlige.length, utenfor: utenfor.length,
                  styrke_utenfor: styrke.left >= boks.right,
                  side_ruller: document.documentElement.scrollWidth > document.documentElement.clientWidth});
        """
        svar = _kjoer(side("/"), tmp_path, bredde, skript)
        assert svar["linjer"] > 5
        assert svar["synlige"] == (svar["linjer"] if synlig else 0)
        assert svar["utenfor"] == 0
        assert svar["side_ruller"] is False
        if synlig:
            # Kolonnen for styrken ligger fortsatt utenfor, som før: tabellen
            # ruller i sin boks.
            assert svar["styrke_utenfor"] is True


class TestBareEnGangIAlleBredder:
    """Story 9.19 (spørsmål 4 i 9.18, gruppens svar 17.11 kl. 18:23): styrken
    og retningen står bare én gang i alle bredder. Linja under navnet vises
    bare når kolonnen for retningen ikke får plass i boksen. Målt i Edge
    17.11: tabellen er 709 px bred med demoens aksjer, og boksen er 34 px
    smalere enn vinduet, så kolonnene får plass fra 743 px. Før sto linja
    til og med 760 px, og i 743–760 px sto retningen to ganger."""

    @pytest.mark.parametrize("bredde", [390, 600, 639, 640, 700, 739, 746, 760, 761, 1280])
    @I_NETTLESEREN
    def test_linja_eller_kolonnen_aldri_begge(self, side, tmp_path, bredde):
        """Ville feilet hvis linja og hele kolonnen for retningen sto samtidig
        (som ved 746 og 760 px før 9.19), eller ingen av dem sto."""
        skript = """
          const boks = document.querySelector(".tabellboks");
          const ramme = boks.getBoundingClientRect();
          const innerst = ramme.left + boks.clientLeft;
          const retning = document.querySelector("#kolonne-retning").getBoundingClientRect();
          const linjer = Array.from(document.querySelectorAll(".tabellboks .smal-signal"));
          ferdig({linjer: linjer.length,
                  synlige: linjer.filter((l) => l.getBoundingClientRect().width > 0).length,
                  kolonnen: boks.scrollLeft === 0 && retning.left >= innerst
                            && retning.right <= innerst + boks.clientWidth + 0.5});
        """
        svar = _kjoer(side("/"), tmp_path, bredde, skript)
        assert svar["linjer"] > 5
        assert svar["synlige"] in (0, svar["linjer"]), svar
        linja = svar["synlige"] > 0
        assert linja != svar["kolonnen"], (bredde, svar)


class TestBoksenIOmvisningen:
    """HE16: boksen i omvisningen har fast bredde, så knappene står likt hver
    gang. At den bytter hjørne (8.26), endres ikke."""

    def test_stilarket_gir_fast_bredde(self):
        """Ville feilet med bare max-width, der bredden fulgte teksten."""
        from test_utseende import STILARKET, _reglene

        kropper = {
            velger: kropp for ramme, velger, kropp in _reglene(STILARKET.read_text(encoding="utf-8")) if not ramme
        }
        boksen = [d.strip() for d in kropper[".omvisning"].split(";")]
        assert "width: min(360px, calc(100vw - 32px))" in boksen
        assert "box-sizing: border-box" in boksen
        assert kropper[".omvisning.til-venstre"] == "right: auto; left: 16px"

    @pytest.mark.parametrize("bredde, venta", [(1280, 360), (390, 358)])
    @I_NETTLESEREN
    def test_i_nettleseren(self, side, tmp_path, bredde, venta):
        """Ville feilet hvis en kort og en lang tekst ga ulik bredde, eller
        boksen gikk utenfor skjermen ved 390 px."""
        skript = """
          const maal = (tekst) => {
            const b = document.createElement("div");
            b.className = "omvisning";
            b.innerHTML = "<h2>Steg</h2><p>" + tekst + "</p><div class='omvisning-knapper'><button>Tilbake</button><button>Neste</button></div>";
            document.body.append(b);
            const r = b.getBoundingClientRect();
            const knapp = b.querySelector("button:last-child").getBoundingClientRect();
            b.remove();
            return [r.width, r.left, r.right, knapp.left - r.left];
          };
          ferdig({kort: maal("Kort."), lang: maal("En lang tekst ".repeat(20)),
                  vindu: document.documentElement.clientWidth});
        """
        svar = _kjoer(side("/"), tmp_path, bredde, skript)
        assert round(svar["kort"][0]) == round(svar["lang"][0]) == venta
        assert svar["kort"][3] == svar["lang"][3]
        assert svar["kort"][1] >= 0 and svar["kort"][2] <= svar["vindu"]


SKRIPTET = Path(__file__).resolve().parent.parent / "src" / "static" / "hjelp.js"
NODE = shutil.which("node")


class TestOmvisningenBlarBareNaarDetTrengs:
    """HE18 (funnet av gruppen 17.11 kl. 13:32): omvisningen blar bare når det
    merkede ikke synes helt. Før blar den ved hvert steg, og ved linja
    «Oppdatert …» hoppet siden et hakk ned, så stripa forsvant."""

    def _node(self, uttrykk: str):
        if NODE is None:
            pytest.skip("node finnes ikke")
        kode = f"const o = require({json.dumps(str(SKRIPTET))}); console.log(JSON.stringify({uttrykk}));"
        svar = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, timeout=60)
        assert svar.returncode == 0, svar.stderr
        return json.loads(svar.stdout)

    @pytest.mark.parametrize(
        "rute, venta",
        [
            ("{top: 100, bottom: 300, left: 10, right: 500}", False),
            ("{top: -1, bottom: 300, left: 10, right: 500}", True),
            ("{top: 100, bottom: 901, left: 10, right: 500}", True),
            ("{top: 100, bottom: 300, left: 10, right: 1300}", True),
            ("{top: 100, bottom: 300, left: -5, right: 500}", True),
            # Rammen rundt det merkede står 7 px utenfor (stil.css), så den
            # skal også synes.
            ("{top: 4, bottom: 300, left: 10, right: 500}", True),
            ("{top: 8, bottom: 892, left: 8, right: 1272}", False),
            # Høyere enn vinduet: blar som før, så toppen står øverst.
            ("{top: 0, bottom: 2000, left: 10, right: 500}", True),
        ],
    )
    def test_blar_bare_naar_det_merkede_ikke_synes(self, rute, venta):
        """Ville feilet uten funksjonen, eller hvis den blar når alt synes."""
        assert self._node(f"o.maaBla({rute}, 900, 1280)") is venta

    def test_skriptet_spoer_foer_det_blar(self):
        """Ville feilet hvis scrollIntoView sto uten spørsmålet foran."""
        kilde = SKRIPTET.read_text(encoding="utf-8")
        foer = kilde.split('oeverst.scrollIntoView({ block: "start" })', 1)[0]
        assert foer.rstrip().endswith(
            "if (OMVISNING.maaBla(ruten, window.innerHeight, document.documentElement.clientWidth))"
        )

    # Ved 390 px står dagvalget under kanten av vinduet, så første steg må
    # bla der.
    @pytest.mark.parametrize("bredde, staar", [(1280, True), (390, False)])
    @I_NETTLESEREN
    def test_i_nettleseren(self, side, tmp_path, bredde, staar):
        """Ville feilet hvis første steg på oversikten, øverst på siden, blar
        siden så stripa forsvinner når alt det merkede alt synes, eller et
        steg lar det merkede stå utenfor vinduet."""
        skript = """
          window.scrollTo(0, 0);
          await vent(100);
          document.querySelector("button.vis-meg-rundt").click();
          await vent(200);
          const r = {foerste: window.scrollY, steg: []};
          for (let i = 0; i < 10; i++) {
            const merket = Array.from(document.querySelectorAll(".omvisning-merket, .omvisning-kolonne"));
            const rutene = merket.map((m) => m.getBoundingClientRect());
            const topp = Math.min(...rutene.map((b) => b.top));
            const bunn = Math.max(...rutene.map((b) => b.bottom));
            r.steg.push({tittel: document.getElementById("omvisning-tittel").textContent,
                         synes: topp >= 0 && (bunn <= window.innerHeight || topp < 40)});
            const neste = Array.from(document.querySelectorAll(".omvisning-knapper button")).find(
              (b) => b.textContent === "Neste" && !b.disabled);
            if (!neste) break;
            neste.click();
            await vent(200);
          }
          ferdig(r);
        """
        svar = _kjoer(side("/"), tmp_path, bredde, skript)
        assert (svar["foerste"] == 0) is staar
        assert len(svar["steg"]) >= 5
        assert all(s["synes"] for s in svar["steg"]), svar["steg"]


INNSTILLINGER = Path(__file__).resolve().parent.parent / "src" / "templates" / "innstillinger.html"


def _vis_meg_rundt(html: str) -> list[dict]:
    import html as html_modul

    treff = re.search(r'<button type="button" class="sideknapp vis-meg-rundt" data-steg="([^"]*)" hidden>', html)
    assert treff, "ingen «Vis meg rundt»"
    return json.loads(html_modul.unescape(treff.group(1)))


class TestStegetOmNotatene:
    """HE17: et steg om notatene ved notatfeltet på aksjesiden og et ved
    notatene i Min liste, i «Vis meg rundt» og i hele omvisningen, med de
    samme ordene som under «Notater» i Innstillinger."""

    def test_sist_paa_aksjesiden_og_foer_knappen_i_min_liste(self):
        """Ville feilet uten stegene, eller med «Mine notater» (knappen) som
        ikke sist i Min liste."""
        import hjelpetekster as ht

        for demo in (False, True):
            sider = ht.rundturer(demo=demo)
            for side in ("aksje", "aksje_uten_sjekker"):
                assert sider[side][-1] == ht.Steg("mine-notater", "Notatene", ht.NOTATENE_AKSJESIDEN), side
            assert [s.anker for s in sider["min_liste"]] == [
                "aksjene",
                "kolonne-signal",
                "kolonne-retning",
                "mine-notater",
                "notatknapp",
            ]
            assert sider["min_liste"][3] == ht.Steg("mine-notater", "Notatene", ht.NOTATENE_MIN_LISTE)
        assert ht.NOTATENE_ANKER == app_modul.NOTATANKER == "mine-notater"

    def test_de_samme_ordene_som_i_innstillinger(self):
        """Ville feilet hvis steget sa noe annet enn teksten under «Notater» i
        Innstillinger, eller hadde over 50 ord."""
        import hjelpetekster as ht

        innstillinger = " ".join(INNSTILLINGER.read_text(encoding="utf-8").split())
        for tekst in (ht.NOTATENE_AKSJESIDEN, ht.NOTATENE_MIN_LISTE):
            for setning in (
                "Under hvert notat står hva aksjen og hovedindeksen gjorde etterpå, på kurs justert for utbytte",
                "Appen sier aldri om noe var riktig.",
            ):
                assert setning in tekst and setning in innstillinger, setning
            assert "men sletter ingenting." in tekst
            assert len(re.findall(r"\w+", f"Notatene {tekst}")) <= 50
        assert ht.NOTATENE_AKSJESIDEN.startswith("Dine egne notater på aksjesiden, samlet nederst i Min liste.")
        assert "Dine egne notater på aksjesiden, samlet nederst i Min liste." in innstillinger

    def test_i_hele_omvisningen(self):
        """Ville feilet hvis stegene manglet i hele omvisningen, eller sto med
        «Notater» av."""
        import hjelpetekster as ht

        stegene = [(s["side"], s["anker"]) for s in ht.omvisningen()]
        assert ("aksje", "mine-notater") in stegene and ("min_liste", "mine-notater") in stegene
        i = stegene.index(("min_liste", "notatknapp"))
        assert stegene[i - 1] == ("min_liste", "mine-notater") and stegene[i + 1][0] == "folg"
        uten = ht.rundturer(notater=False)
        assert all(s.anker != "mine-notater" for steg in uten.values() for s in steg)
        assert all(s["anker"] != "mine-notater" for s in ht.omvisningen(notater=False))

    @pytest.mark.parametrize("adresse", ["/aksje/BRFE", "/min-liste?vis=alle"])
    def test_paa_sidene(self, side, adresse):
        """Ville feilet hvis steget ikke var i «Vis meg rundt» på siden, eller
        ankeret ikke sto der nøyaktig én gang."""
        html = side(adresse)
        stegene = [s["anker"] for s in _vis_meg_rundt(html)]
        assert "mine-notater" in stegene
        assert len(re.findall(r'(?<![\w-])id="mine-notater"', html)) == 1
