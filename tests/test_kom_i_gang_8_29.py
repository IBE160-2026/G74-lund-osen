"""Story 8.29: «Din egen liste: kom i gang» som tavla, og investorknappen 44 px.

Gruppens svar 13.11 kl. 10:32-10:54, med tavla «Min liste» 13.10, og tillegg 1
(svarene kl. 10:59-11:02): én overskrift, titlene og teksten i kortene med
linjehøyde, brikkene i steg 3, setningen i steg 2, delen uten ramme, egen
bakgrunn og luft på sidene, bransjekortene stablet i kolonner, og knappen til
investorsiden minst 44 px høy. Spesifikasjonen er
spec-8-29-din-egen-liste-kom-i-gang.md. Demoen og den ekte versjonen bygges
under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import json
import os
import re
from pathlib import Path

import pytest

from test_hjelpefeltet import NETTLESER, _kjoer
from test_vis_meg_rundt_8_26 import ekte, klient, mal  # noqa: F401  (fiksturene)

ROT = Path(__file__).resolve().parents[1]
STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
I_NETTLESER = pytest.mark.skipif(NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome")
SETNINGEN = (
    "Nøkkelen står på kontosiden hos EODHD. Startskriptet til den ekte versjonen spør etter den første gang,"
    " og den lagres bare på denne maskinen."
)


def _side(k, adresse: str) -> str:
    svar = k.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.get_data(as_text=True)


def _delen(side: str) -> str:
    return side.split('<section class="egne" id="din-egen-liste"', 1)[1].split("</ol>", 1)[0]


@pytest.fixture(params=("demo", "ekte"))
def versjon(request, klient, ekte):  # noqa: F811
    return klient if request.param == "demo" else ekte


class TestOverskriften:
    def test_en_h2_med_id_en_delen_viser_til(self, versjon):
        """Ville feilet hvis delen hadde mer enn én h2, overskriften ikke var
        «Din egen liste: kom i gang» med id-en i aria-labelledby, eller
        overskriften «Din egen liste» og setningen under sto igjen."""
        side = _side(versjon, "/min-liste")
        delen = _delen(side)
        assert 'aria-labelledby="egen-liste-tittel"' in side
        assert re.findall(r"<h2[^>]*>(.*?)</h2>", delen) == ["Din egen liste: kom i gang"]
        assert '<h2 id="egen-liste-tittel">Din egen liste: kom i gang</h2>' in delen
        assert not re.search(r">\s*Din egen liste\s*<", side)
        assert "<h3>Din egen liste: kom i gang</h3>" not in side
        assert "Vil du følge helt andre aksjer" not in side
        assert "Appen kjører på din egen maskin, så det finnes ingen innlogging hos oss." in delen

    def test_overskriften_i_stilen(self):
        """Ville feilet hvis overskriften ikke var 32 px med vekt 500 (Newsreader
        kommer fra h2 i hele appen)."""
        assert ":where(.side-oversikt) #din-egen-liste > h2 { margin: 0; font-size: 32px; font-weight: 500; }" in STIL
        assert 'h1, h2 { font-family: "Newsreader", Georgia, serif; font-weight: 500; }' in STIL


class TestKortene:
    def test_setningen_i_steg_2_og_ingen_felt(self, versjon):
        """Ville feilet hvis steg 2 ikke sa at startskriptet spør etter
        nøkkelen, sa den gamle setningen, eller fikk et felt (AD-10)."""
        delen = _delen(_side(versjon, "/min-liste"))
        assert SETNINGEN in delen
        assert "EODHD. Den lagres bare på denne maskinen." not in delen
        assert "<input" not in delen and "<form" not in delen

    def test_titlene_teksten_og_kortene_i_stilen(self):
        """Ville feilet hvis titlene ikke var 21 px med linjehøyde 1,2, teksten
        16 px med 1,5, eller stegkortene ikke hadde luften, hjørnene og
        avstanden fra tavla."""
        for regel in (
            "#din-egen-liste .kort-steg .steg-topp h4 { font-size: 21px; line-height: 1.2; }",
            "#din-egen-liste .kort-steg p { font-size: 16px; line-height: 1.5; }",
            "#din-egen-liste .stegkort { gap: 14px; }",
            "#din-egen-liste .kort-steg { padding: 18px 18px 20px; border-radius: 14px; }",
        ):
            assert f":where(.side-oversikt) {regel}" in STIL, regel

    def test_brikkene_i_stilen(self):
        """Ville feilet hvis brikkene i steg 3 ikke var 30 px høye, med 12 px
        luft, 13 px tekst med vekt 600, 6 px mellom og ikonet 13 px."""
        brikken = re.search(r":where\(\.side-oversikt\) #din-egen-liste \.ferdigknapp \{([^}]*)\}", STIL).group(1)
        for del_ in (
            "min-height: 30px",
            "height: 30px",
            "padding: 0 12px",
            "font-size: 13px",
            "font-weight: 600",
            "gap: 6px",
        ):
            assert del_ in brikken, del_
        assert ":where(.side-oversikt) #din-egen-liste .ferdige-knapper { gap: 6px; }" in STIL
        assert (
            ":where(.side-oversikt) #din-egen-liste .ferdigknapp .bransjesymbol { width: 13px; height: 13px; }" in STIL
        )

    def test_delen_uten_ramme_bakgrunn_og_luft_paa_sidene(self):
        """Tillegg 1. Ville feilet hvis delen hadde ramme, egen bakgrunn eller
        luft på sidene, eller «Dine egne aksjer» på oversikten mistet kortet."""
        assert (
            ":where(.side-oversikt) #din-egen-liste { padding: 21px 0; background: none; border: none; border-radius: 0; }"
            in STIL
        )
        assert ":where(.side-oversikt) .egne { margin: 40px 0 8px; padding: 20px 22px; background: var(--kort);" in STIL

    def test_bransjekortene_i_kolonner(self):
        """Tillegg 1. Ville feilet hvis kortene sto i rader med hull, kunne
        deles mellom to kolonner, eller kolonnene var smalere enn 260 px."""
        assert ":where(.side-oversikt) .bransjekort { columns: 3 260px; column-gap: 16px; }" in STIL
        kortet = re.search(r":where\(\.side-oversikt\) \.bransjekortet \{([^}]*)\}", STIL).group(1)
        assert "break-inside: avoid" in kortet and "margin: 0 0 16px" in kortet
        assert "grid-template-columns: repeat(3" not in STIL.split(".bransjekort {", 1)[1].split("}", 1)[0]


# Målt i nettleseren, med siden fra appen og stilen fra static/ (test_hjelpefeltet).
MAAL_DELEN = r"""
const s = document.querySelector('#din-egen-liste');
const r = (e) => e.getBoundingClientRect();
const cs = getComputedStyle(s);
const tabell = document.querySelector('main table');
const titler = [...s.querySelectorAll('.steg-topp h4')].map((h) => [parseFloat(getComputedStyle(h).lineHeight), r(h).height]);
const brikker = [...s.querySelectorAll('.ferdigknapp')].map((b) => r(b).height);
const kort = [...s.querySelectorAll('.bransjekortet')].map((k) => [Math.round(r(k).left), Math.round(r(k).top), Math.round(r(k).bottom)]);
ferdig({h2: s.querySelectorAll('h2').length, bakgrunn: cs.backgroundColor, kant: cs.borderTopWidth,
        venstre: [Math.round(r(s).left), tabell ? Math.round(r(tabell).left) : null],
        hoeyre: [Math.round(r(s).right), tabell ? Math.round(r(tabell).right) : null],
        titler, brikker, kort,
        rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth});
"""


@I_NETTLESER
@pytest.mark.parametrize("bredde,kolonner", ((1280, 3), (390, 1)))
def test_delen_i_nettleseren(klient, tmp_path, bredde, kolonner):  # noqa: F811
    """Ville feilet hvis delen hadde mer enn én h2, en ramme eller egen
    bakgrunn, ikke sto i linje med tabellen, en tittel som brytes ble skrevet
    oppå seg selv (linjehøyde 1,2), en brikke var lavere enn 24 px (WCAG
    2.5.8), bransjekortene ikke sto i tre kolonner ved 1280 px og én ved 390,
    eller et kort ikke startet 16 px under kortet over i samme kolonne."""
    r = _kjoer(_side(klient, "/min-liste"), tmp_path, bredde, MAAL_DELEN)
    assert r["h2"] == 1 and r["kant"] == "0px" and r["bakgrunn"] == "rgba(0, 0, 0, 0)", r
    assert not r["rulling"]
    if r["venstre"][1] is not None:
        assert abs(r["venstre"][0] - r["venstre"][1]) <= 1 and abs(r["hoeyre"][0] - r["hoeyre"][1]) <= 1, r
    for linje, hoeyde in r["titler"]:
        assert linje == pytest.approx(25.2, abs=0.1)
        assert hoeyde >= linje - 0.5 and round(hoeyde / linje, 1) == round(hoeyde / linje)  # hele linjer
    assert r["brikker"] and all(h == pytest.approx(30, abs=0.5) for h in r["brikker"]), r["brikker"]
    venstre = sorted({k[0] for k in r["kort"]})
    assert len(venstre) == kolonner, r["kort"]
    for kol in venstre:
        i_kol = sorted(k for k in r["kort"] if k[0] == kol)
        i_kol.sort(key=lambda k: k[1])
        for over, under in zip(i_kol, i_kol[1:]):
            assert under[1] - over[2] == 16, (over, under)


MAAL_KNAPPEN = r"""
const a = document.querySelector('p.investorboble a');
const b = a.getBoundingClientRect();
ferdig({hoeyde: b.height, linjer: Math.round((b.height - 25) / 22),
        rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth});
"""


def test_knappen_i_stilen():
    """Ville feilet hvis knappen til investorsiden ikke hadde minst 44 px."""
    regel = re.search(r"p\.investorboble a \{([^}]*)\}", STIL).group(1)
    assert "min-height: 44px" in regel and "padding: 11px 20px" in regel and "line-height: 22px" in regel


@I_NETTLESER
@pytest.mark.parametrize("hvilken", ("demo", "ekte"))
@pytest.mark.parametrize("bredde,brytes", ((1280, False), (320, True)))
def test_knappen_44_px_ogsaa_naar_teksten_brytes(klient, ekte, tmp_path, hvilken, bredde, brytes):  # noqa: F811
    """Ville feilet hvis knappen til investorsiden var lavere enn 44 px, på én
    linje eller når et langt navn brytes på smal skjerm, i en av versjonene,
    eller pila og den nye fanen sto i demoen."""
    k = klient if hvilken == "demo" else ekte
    side = _side(k, "/min-liste")
    symbol = re.search(r'href="/aksje/([A-Z0-9.]+)"', side).group(1)
    html = _side(k, f"/aksje/{symbol}")
    navn = re.search(r'<p class="investorboble"><a [^>]*>Investorsiden til ([^<]+)<', html).group(1)
    assert ("↗" in html.split('class="investorboble"', 1)[1].split("</p>", 1)[0]) == (hvilken == "ekte")
    if brytes:
        html = html.replace(f"Investorsiden til {navn}<", f"Investorsiden til {navn} Holding og Kraftselskap ASA<", 1)
    r = _kjoer(html, tmp_path, bredde, MAAL_KNAPPEN)
    assert r["hoeyde"] >= 44 and not r["rulling"], r
    assert (r["linjer"] > 1) == brytes, json.dumps(r)
