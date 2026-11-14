"""Story 8.30: de ledige rutene i plassstreken med nok kontrast.

Gruppens svar 14.11 kl. 05:10–05:13 på spørsmål 7 i 8.29 (tillegg 9 til 9.11):
de ledige rutene i streken under «Appen følger N av 18» skal ha nok kontrast
mot den beige bakgrunnen. Designregler §3 og WCAG 1.4.11 krever minst 3:1 for
streker og felt som må ses for å forstå siden, og brukt og ledig skal også ha
3:1 mot hverandre. Spesifikasjonen er spec-8-30-plassstreken-kontrast.md.
Demoen og den ekte versjonen bygges under tmp_path (regel 22), og ingen test
gjør nettkall (AD-8).
"""

import re

import pytest

from test_hjelpefeltet import _kjoer
from test_kom_i_gang_8_29 import I_NETTLESER, STIL, VERSJONENE, _versjonen
from test_utseende import _kontrast
from test_vis_meg_rundt_8_26 import ekte, klient, mal  # noqa: F401  (fiksturene)

MINST = 3.0


def _farger(stil: str) -> dict[str, str]:
    """Fargene i :root, uten #, med små bokstaver."""
    rot = re.search(r":root\s*\{([^}]*)\}", stil).group(1)
    return {n: h.lower() for n, h in re.findall(r"--([a-z0-9-]+):\s*#([0-9a-fA-F]{6})\s*;", rot)}


def _bakgrunn(stil: str, velger: str) -> str:
    """Navnet på fargen i background for regelen med akkurat denne velgeren."""
    regel = re.search(re.escape(velger) + r"\s*\{([^}]*)\}", stil)
    assert regel, velger
    farge = re.search(r"background:\s*var\(--([a-z0-9-]+)\)", regel.group(1))
    assert farge, (velger, regel.group(1))  # gjennomgangen (ECH1): tydelig feil, ikke None
    return farge.group(1)


def _fargene_i_stilen(stil: str) -> tuple[str, str, str]:
    """(ledig, brukt, bakgrunnen) som hex, lest fra reglene i stilen."""
    farger = _farger(stil)
    ledig = farger[_bakgrunn(stil, ":where(.side-oversikt) .plassstrek span")]
    brukt = farger[_bakgrunn(stil, ":where(.side-oversikt) .plassstrek span.brukt")]
    bak = farger[_bakgrunn(stil, "\nbody")]
    return ledig, brukt, bak


def _stilen_til(k, side: str) -> str:
    """Stilarket siden lenker til, slik appen gir det ut."""
    href = re.search(r'<link rel="stylesheet" href="([^"]+)">', side).group(1)
    svar = k.get(href)
    assert svar.status_code == 200, href
    return svar.get_data(as_text=True)


@VERSJONENE
def test_ledig_mot_bakgrunnen_og_brukt_mot_ledig(request, hvilken):
    """Ville feilet hvis de ledige rutene hadde under 3:1 mot bakgrunnen, som
    --strek-2 med 1,34:1, eller brukt og ledig hadde under 3:1 mot hverandre,
    regnet ut fra fargene i stilarket siden lenker til, i begge versjonene.
    Ville også feilet hvis streken manglet en brukt eller en ledig rute."""
    k, side = _versjonen(request, hvilken)
    strek = side.split('<span class="plassstrek" aria-hidden="true">', 1)[1].split("</span></span>", 1)[0]
    assert '<span class="brukt">' in strek and '<span class="ledig">' in strek, strek
    ledig, brukt, bak = _fargene_i_stilen(_stilen_til(k, side))
    assert _kontrast(ledig, bak) >= MINST, (ledig, bak, round(_kontrast(ledig, bak), 2))
    assert _kontrast(brukt, ledig) >= MINST, (brukt, ledig, round(_kontrast(brukt, ledig), 2))


def test_fargene_i_stilen():
    """Ville feilet hvis de ledige rutene ikke hadde --dempet-2 (svaret og
    designregler §3, 14.11), de brukte ikke lenger hadde --blekk, sidens
    bakgrunn ikke var --bakgrunn, eller regelen for forced-colors manglet."""
    assert _bakgrunn(STIL, ":where(.side-oversikt) .plassstrek span") == "dempet-2"
    assert _bakgrunn(STIL, ":where(.side-oversikt) .plassstrek span.brukt") == "blekk"
    assert _bakgrunn(STIL, "\nbody") == "bakgrunn"
    assert (
        "@media (forced-colors: active) { :where(.side-oversikt) .plassstrek span { border: 1px solid CanvasText; }"
        " :where(.side-oversikt) .plassstrek span.brukt { background: CanvasText; } }"
    ) in STIL
    ledig, brukt, bak = _fargene_i_stilen(STIL)
    assert round(_kontrast(ledig, bak), 2) == 4.14 and round(_kontrast(brukt, ledig), 2) == 3.83


def test_ingen_annen_regel_gir_rutene_en_bakgrunn():
    """Gjennomgangen (ECH1): _bakgrunn leser den første regelen med velgeren.
    Ville feilet hvis en senere regel, for eksempel i en @media for smal
    skjerm, ga rutene en annen bakgrunn, så testene over ikke så den. Bare
    grunnregelen, regelen for de brukte og regelen for forced-colors setter
    bakgrunnen."""
    med_bakgrunn = [
        (velger.strip().rsplit("{", 1)[-1].strip(), kropp.strip())
        for velger, kropp in re.findall(
            r"([^{}]*\.plassstrek span[^{}]*)\{([^}]*)\}", re.sub(r"/\*.*?\*/", "", STIL, flags=re.S)
        )
        if "background" in kropp
    ]
    assert med_bakgrunn == [
        (
            ":where(.side-oversikt) .plassstrek span",
            "width: 10px; height: 10px; border-radius: 2px; background: var(--dempet-2);",
        ),
        (":where(.side-oversikt) .plassstrek span.brukt", "background: var(--blekk);"),
        (":where(.side-oversikt) .plassstrek span.brukt", "background: CanvasText;"),
    ], med_bakgrunn


def test_regningen_fanger_den_gamle_fargen():
    """Ville feilet hvis regningen ikke fanget --strek-2 fra før 8.30, så
    testene over ikke prøvde noe."""
    gammel = STIL.replace(
        ":where(.side-oversikt) .plassstrek span { width: 10px; height: 10px; border-radius: 2px; background: var(--dempet-2); }",
        ":where(.side-oversikt) .plassstrek span { width: 10px; height: 10px; border-radius: 2px; background: var(--strek-2); }",
    )
    assert gammel != STIL
    ledig, _, bak = _fargene_i_stilen(gammel)
    assert _kontrast(ledig, bak) < MINST


MAAL_STREKEN = r"""
const ledig = document.querySelector('.plassstrek span.ledig');
const brukt = document.querySelector('.plassstrek span.brukt');
// Gjennomgangen (ECH3): bare en helt gjennomsiktig forelder uten bilde hoppes over.
function bak(el) {
  for (let a = el.parentElement; a; a = a.parentElement) {
    const s = getComputedStyle(a);
    if (s.backgroundImage !== 'none') return 'bilde: ' + s.backgroundImage;
    if (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent') return s.backgroundColor;
  }
  return getComputedStyle(document.documentElement).backgroundColor;
}
// Gjennomgangen (ECH2): en full eller tom liste gir en tydelig feil.
if (!ledig || !brukt) { ferdig({mangler: {ledig: !ledig, brukt: !brukt}}); } else {
const b = ledig.getBoundingClientRect();
ferdig({ledig: getComputedStyle(ledig).backgroundColor, brukt: getComputedStyle(brukt).backgroundColor,
        bak: bak(ledig), stoerrelse: [b.width, b.height],
        rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth});
}
"""


def _hex(rgb: str) -> str:
    """Gjennomgangen (ECH3): også rgba, men bare helt dekkende."""
    m = re.fullmatch(r"rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)", rgb)
    assert m and (m.group(4) is None or float(m.group(4)) == 1), rgb
    r, g, b = (int(t) for t in m.groups()[:3])
    return f"{r:02x}{g:02x}{b:02x}"


@I_NETTLESER
@VERSJONENE
@pytest.mark.parametrize("bredde", (1280, 390))
def test_streken_i_nettleseren(request, tmp_path, hvilken, bredde):
    """Ville feilet hvis fargene i nettleseren var andre enn i stilen, for
    eksempel fordi en annen regel vant, hvis bakgrunnen bak streken ikke var
    sidens beige, kontrasten var under 3:1, rutene ikke var 10 × 10 px, eller
    siden rullet sidelengs, ved 1280 og 390 px i begge versjonene."""
    _, side = _versjonen(request, hvilken)
    r = _kjoer(side, tmp_path, bredde, MAAL_STREKEN)
    assert "mangler" not in r, r
    ledig, brukt, bak = _fargene_i_stilen(STIL)
    assert (_hex(r["ledig"]), _hex(r["brukt"]), _hex(r["bak"])) == (ledig, brukt, bak), r
    assert _kontrast(ledig, bak) >= MINST and _kontrast(brukt, ledig) >= MINST
    assert r["stoerrelse"] == [10, 10] and not r["rulling"], r
