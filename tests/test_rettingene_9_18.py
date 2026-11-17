"""Story 9.18: rettingene før brukertest 2 (gruppens svar 17.11 kl. 13:03–13:33).

Funnene er fra den heuristiske evalueringen (docs/heuristisk-evaluering.md).
Testene i nettleseren bruker fremgangsmåten i test_hjelpefeltet.py: ingen
server og ingenting fra nettet (AD-8), og de hoppes over uten Edge eller
Chrome, unntatt i CI.
"""

import re

import pytest

from test_hjelpefeltet import _kjoer
from test_hjelpetekster import base, basemal, klient  # noqa: F401


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
        assert "display: block" in kropper[("@media (max-width: 760px)", velger)]

    @pytest.mark.parametrize("bredde, synlig", [(390, True), (1280, False)])
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
