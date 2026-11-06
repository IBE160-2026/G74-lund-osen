"""Story 8.2c: kursgrafen på smal skjerm.

Siden har den samme grafen to ganger: den brede, som før, og en med egne mål
på smal skjerm (graf.bygg_graf med smal=True). Stilarket viser den smale når
figuren er smalere enn 690 px, så teksten i grafen ved 390 px er minst like
stor som den minste teksten ellers på siden. Testene i nettleseren bruker
fremgangsmåten i test_hjelpefeltet.py: ingen server og ingenting fra nettet.
"""

import re
from pathlib import Path

import pytest

from test_hjelpefeltet import NETTLESER, _kjoer
from test_hjelpetekster import base, basemal, klient  # noqa: F401

STIL = (Path(__file__).resolve().parent.parent / "src" / "static" / "stil.css").read_text(encoding="utf-8")


@pytest.fixture
def aksjesiden(klient, base):  # noqa: F811
    svar = klient.get("/aksje/BRFE")
    assert svar.status_code == 200
    return svar.get_data(as_text=True)


def _svg(html: str, klasse: str) -> str:
    deler = html.split(f'<svg class="{klasse}"')
    assert len(deler) == 2, f"ikke én <svg class={klasse!r}>"
    return deler[1].split("</svg>", 1)[0]


def test_den_smale_grafen_har_det_samme_som_den_brede(aksjesiden):
    """Ville feilet hvis den smale grafen manglet en linje, et merke på
    aksen, rutenettet, punktet ved enden eller et navn på en linje, eller
    hvis den hadde de brede målene, så den ble skalert ned som før."""
    from graf import SMAL_BREDDE, SMAL_HOYDE

    bred, smal = _svg(aksjesiden, "graf"), _svg(aksjesiden, "graf smal")
    assert f'viewBox="0 0 {SMAL_BREDDE} {SMAL_HOYDE}"' in smal
    for teller in (
        r'<polyline class="kurslinje"',
        r'<polyline class="ma50linje"',
        r'<polyline class="indekslinje"',
        r'class="rutetekst"',
        r'class="maanedsstrek"',
        r'class="sistepunkt"',
    ):
        assert len(re.findall(teller, bred)) == len(re.findall(teller, smal)) > 0, teller
    navn = lambda svg: sorted(re.findall(r'<text class="linjenavn (\w+)"[^>]*>([^<]*)</text>', svg))  # noqa: E731
    assert navn(bred) == navn(smal) and len(navn(smal)) == 3
    etikett = re.compile(r'aria-label="([^"]*)"')
    assert etikett.search(bred).group(1) == etikett.search(smal).group(1)


def test_navnene_staar_under_grafen_paa_smal_skjerm(aksjesiden):
    """Ville feilet hvis navnene på smal skjerm sto i feltet til høyre, eller
    hvis et navn manglet stykket av linja det hører til."""
    smal = _svg(aksjesiden, "graf smal")
    bunn = max(float(y) for y in re.findall(r'<line class="maanedsstrek"[^>]*y2="([\d.]+)"', smal))
    datoer = [float(y) for y in re.findall(r'<text class="maanedstekst"[^>]*y="([\d.]+)"', smal)]
    navn = re.findall(r'<text class="linjenavn (\w+)" x="([\d.]+)" y="([\d.]+)"', smal)
    assert all(float(y) > max(datoer) > bunn for _, _, y in navn)
    for klasse, linje in (("kurs", "kurslinje"), ("snitt", "ma50linje"), ("indeks", "indekslinje")):
        y = next(float(y) for k, _, y in navn if k == klasse)
        assert re.search(rf'<line class="{linje}" [^>]*y1="{y - 4:g}"', smal), klasse


def test_stilarket_viser_den_smale_naar_figuren_er_smal():
    """Ville feilet hvis begge grafene ble vist, eller den smale aldri, eller
    hvis grensen ikke var der teksten i den brede blir mindre enn 11,5 px."""
    figur = re.search(r":where\(\.side-aksje\) figure \{([^}]*)\}", STIL).group(1)
    assert "container-type: inline-size;" in figur
    assert re.search(r":where\(\.side-aksje\) svg\.graf\.smal \{ display: none;", STIL)
    blokk = STIL.split("@container (width < 690px) {", 1)[1].split("\n}", 1)[0]
    assert "svg.graf:not(.smal) { display: none; }" in blokk
    assert "svg.graf.smal { display: block; }" in blokk
    assert 12 * 690 / 720 == pytest.approx(11.5)


MAAL = r"""
const svger = Array.from(document.querySelectorAll('svg.graf')).filter((s) => s.getBoundingClientRect().width > 0);
const r = {synlige: svger.map((s) => s.getAttribute('class'))};
const svg = svger[0];
const b = svg.getBoundingClientRect();
const skala = b.width / svg.viewBox.baseVal.width;
const tekster = Array.from(svg.querySelectorAll('text')).filter((t) => t.textContent.trim());
r.grafskrift = Math.min(...tekster.map((t) => parseFloat(getComputedStyle(t).fontSize) * skala));
r.utenfor = tekster.filter((t) => { const tb = t.getBoundingClientRect();
  return tb.left < b.left - 0.5 || tb.right > b.right + 0.5 || tb.top < b.top - 0.5 || tb.bottom > b.bottom + 0.5; })
  .map((t) => t.textContent.trim());
const bokser = tekster.map((t) => [t.getBoundingClientRect(), t.textContent.trim()]);
r.overlapp = [];
for (let i = 0; i < bokser.length; i++) for (let j = i + 1; j < bokser.length; j++) {
  const [a, x] = bokser[i], [c, y] = bokser[j];
  if (a.left < c.right - 0.5 && a.right > c.left + 0.5 && a.top < c.bottom - 0.5 && a.bottom > c.top + 0.5) r.overlapp.push(x + '/' + y);
}
// Den minste synlige teksten utenfor grafen, som tekst() i hjelperne.
r.ellers = 1e9;
const gaa = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
for (let n = gaa.nextNode(); n; n = gaa.nextNode()) {
  if (!n.data.trim() || n.parentElement.closest('svg.graf, script, pre#resultat, title, .hjelpevindu')) continue;
  if (klippet(n.parentElement)) continue;
  const rg = document.createRange(); rg.selectNodeContents(n);
  if (Array.from(rg.getClientRects()).some((q) => q.width > 1 && q.height > 1))
    r.ellers = Math.min(r.ellers, parseFloat(getComputedStyle(n.parentElement).fontSize));
}
r.rulling = document.documentElement.scrollWidth > document.documentElement.clientWidth;
ferdig(r);
"""


@pytest.mark.skipif(NETTLESER is None, reason="ingen Edge eller Chrome")
@pytest.mark.parametrize("bredde", [1280, 390, 320])
def test_teksten_i_grafen_i_nettleseren(aksjesiden, tmp_path, bredde):
    """Kontrollpunktet: ved 390 px er teksten i grafen minst like stor som
    den minste teksten ellers på siden, uten vannrett rulling. Ville feilet
    hvis den brede grafen ble vist ved 390 px (om lag 5 px), hvis den smale
    ble vist ved 1280 px, eller hvis en tekst i grafen sto utenfor den eller
    oppå en annen. Ved 320 px er teksten mindre (10,4 px, i spesifikasjonen),
    så der sjekkes bare plassen."""
    r = _kjoer(aksjesiden, tmp_path, bredde, MAAL)
    assert r["synlige"] == (["graf"] if bredde == 1280 else ["graf smal"]), r
    assert r["utenfor"] == [] and r["overlapp"] == [] and r["rulling"] is False, r
    if bredde == 390:
        assert r["grafskrift"] >= r["ellers"] > 0, r
