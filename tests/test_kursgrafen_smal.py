"""Story 8.2c: kursgrafen på smal skjerm.

Siden har den samme grafen to ganger: den brede, som før, og en med egne mål
på smal skjerm (graf.bygg_graf med smal=True). Stilarket viser den smale når
figuren er smalere enn 690 px, så teksten i grafen ved 390 px er minst like
stor som den minste teksten ellers på siden. Testene i nettleseren bruker
fremgangsmåten i test_hjelpefeltet.py: ingen server og ingenting fra nettet.
"""

import os
import re
from pathlib import Path

import pytest

from test_hjelpefeltet import NETTLESER, _kjoer
from test_hjelpetekster import base, basemal, klient  # noqa: F401

STIL = (Path(__file__).resolve().parent.parent / "src" / "static" / "stil.css").read_text(encoding="utf-8")


@pytest.fixture
def side(klient, base):  # noqa: F811
    def hent(adresse: str = "/aksje/BRFE") -> str:
        svar = klient.get(adresse)
        assert svar.status_code == 200, adresse
        return svar.get_data(as_text=True)

    return hent


@pytest.fixture
def aksjesiden(side):
    return side()


def _svg(html: str, klasse: str) -> str:
    deler = html.split(f'<svg class="{klasse}"')
    assert len(deler) == 2, f"ikke én <svg class={klasse!r}>"
    return deler[1].split("</svg>", 1)[0]


def test_den_smale_grafen_har_det_samme_som_den_brede(aksjesiden, side):
    """Ville feilet hvis den smale grafen manglet en linje, et merke på
    aksen, rutenettet, punktet ved enden eller et navn på en linje, eller
    hvis den hadde de brede målene, så den ble skalert ned som før."""
    from graf import SMAL_BREDDE, SMAL_HOYDE, VOLUMFELT

    bred, smal = _svg(aksjesiden, "graf"), _svg(aksjesiden, "graf smal")
    # Story 8.7: feltet for volumet står under grafen, i samme SVG. Her sto
    # SMAL_HOYDE alene.
    assert f'viewBox="0 0 {SMAL_BREDDE} {SMAL_HOYDE + VOLUMFELT}"' in smal
    for teller in (
        r'<polyline class="kurslinje"',
        r'<polyline class="ma50linje"',
        r'<polyline class="indekslinje"',
        r'class="rutetekst"',
        r'class="maanedsstrek"',
        r'class="sistepunkt"',
    ):
        assert len(re.findall(teller, bred)) == len(re.findall(teller, smal)) > 0, teller
    # Gjennomgangen (VG2): dagen som er merket, på en side med en valgt dag.
    # Story 8.20a (del C, U89): datoen i en lapp øverst på streken, og
    # punktet nederst er borte.
    dagen = side("/aksje/BRFE?dag=2026-10-01")
    for teller in (r'class="dagstrek"', r'class="daglapp"', r'class="daglapptekst"'):
        assert len(re.findall(teller, _svg(dagen, "graf"))) == len(re.findall(teller, _svg(dagen, "graf smal"))) == 1
    # Story 8.20a (del C, U92): lappen ved musepekeren for hver dag i begge.
    assert len(re.findall(r'<g class="musedag">', bred)) == len(re.findall(r'<g class="musedag">', smal)) > 0
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
    hvis grensen ikke var der teksten i den brede blir mindre enn 11,5 px.
    Gjennomgangen (BH9): grensene regnes av målene i graf.py."""
    from graf import BREDDE, SMAL_BREDDE

    figur = re.search(r":where\(\.side-aksje\) figure \{([^}]*)\}", STIL).group(1)
    assert "container-type: inline-size;" in figur
    smal = re.search(r":where\(\.side-aksje\) svg\.graf\.smal \{([^}]*)\}", STIL).group(1)
    assert "display: none;" in smal and f"max-width: calc({SMAL_BREDDE}px * 4 / 3);" in smal
    grense = round(BREDDE * 11.5 / 12)
    blokk = STIL.split(f"@container (width < {grense}px) {{", 1)[1].split("\n}", 1)[0]
    assert "svg.graf:not(.smal) { display: none; }" in blokk
    assert "svg.graf.smal { display: block; }" in blokk


MAAL = r"""
const svger = Array.from(document.querySelectorAll('svg.graf')).filter((s) => s.getBoundingClientRect().width > 0);
const r = {synlige: svger.map((s) => s.getAttribute('class'))};
const svg = svger[0];
const b = svg.getBoundingClientRect();
const skala = b.width / svg.viewBox.baseVal.width;
// Story 8.20a (del C): lappene ved musepekeren er skjult til musa er over
// dagen, så de telles ikke med den synlige teksten. De sjekkes for seg under.
const tekster = Array.from(svg.querySelectorAll('text')).filter((t) => t.textContent.trim() && !t.closest('.lapp'));
r.lappUtenfor = Array.from(svg.querySelectorAll('.lappramme')).filter((t) => { const tb = t.getBoundingClientRect();
  return tb.left < b.left - 0.5 || tb.right > b.right + 0.5 || tb.top < b.top - 0.5 || tb.bottom > b.bottom + 0.5; }).length;
r.lappSkjult = Array.from(svg.querySelectorAll('.lapp')).every((g) => getComputedStyle(g).visibility === 'hidden');
// Gjennomgangen av 8.20a (ECH8): navnet og tallet på samme linje i lappen
// overlapper ikke, og står inne i rammen.
r.lappOverlapp = [];
for (const g of svg.querySelectorAll('.lapp')) {
  const ramme = g.querySelector('.lappramme').getBoundingClientRect();
  const navn = Array.from(g.querySelectorAll('.lappnavn')), tall = Array.from(g.querySelectorAll('.lapptall'));
  navn.forEach((n, i) => { const a = n.getBoundingClientRect(), c = tall[i].getBoundingClientRect();
    if (a.right > c.left - 2 || c.right > ramme.right + 0.5 || a.left < ramme.left - 0.5) r.lappOverlapp.push(n.textContent + '/' + tall[i].textContent); });
}
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


# Gjennomgangen (VG1): i CI feiler testen når nettleseren mangler, som i
# test_hjelpefeltet.py, i stedet for å hoppes over uten at noen ser det.
# Gjennomgangen (BH2, BH4, VG3): perioder med datoer og med annenhver måned,
# og en annen dag, ved 390 og 320 px.
@pytest.mark.skipif(NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome")
@pytest.mark.parametrize(
    "adresse, bredde",
    [("/aksje/BRFE", 1280)]
    + [
        (adresse, bredde)
        for adresse in (
            "/aksje/BRFE",
            # Siste børsdag, med dagen merket i grafen.
            "/aksje/BRFE?periode=siste",
            "/aksje/BRFE?periode=1-uke",
            "/aksje/BRFE?periode=1-mnd",
            "/aksje/BRFE?periode=1-aar",
            "/aksje/BRFE?dag=2026-10-01",
        )
        for bredde in (390, 320)
    ],
)
def test_teksten_i_grafen_i_nettleseren(side, tmp_path, adresse, bredde):
    """Kontrollpunktet: ved 390 px er teksten i grafen minst like stor som
    den minste teksten ellers på siden, uten vannrett rulling. Ville feilet
    hvis den brede grafen ble vist ved 390 px (om lag 5 px), hvis den smale
    ble vist ved 1280 px, eller hvis en tekst i grafen sto utenfor den eller
    oppå en annen. Ved 320 px er teksten mindre (10,4 px, i spesifikasjonen),
    så der sjekkes bare plassen."""
    r = _kjoer(side(adresse), tmp_path, bredde, MAAL)
    assert r["synlige"] == (["graf"] if bredde == 1280 else ["graf smal"]), r
    assert r["utenfor"] == [] and r["overlapp"] == [] and r["rulling"] is False, r
    # Story 8.20a (del C): lappen ved musepekeren står inne i grafen, og er
    # skjult til musa er over dagen.
    assert r["lappUtenfor"] == 0 and r["lappSkjult"] is True and r["lappOverlapp"] == [], r
    if bredde == 390:
        assert r["grafskrift"] >= r["ellers"] > 0, r
