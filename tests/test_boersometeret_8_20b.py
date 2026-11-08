"""Story 8.20b: børsometeret (spesifikasjonen
spec-8-20-ux-rettingene-etter-gjennomgangen-06-11.md, del F, og det som hører
til børsometeret i E, H (U88), J og K, og BH9 fra 8.20a).

Testene som fantes for børsometeret, er rettet i test_boersometer.py,
test_funnene_8_2b.py og test_periodevalget_min_liste_boersometer.py. Her står
det som er nytt. Ingen nett: demobasen lages i tmp_path, som i
test_aksjesiden_8_20a.py, og nettlesertestene bruker _kjoer fra
test_hjelpefeltet.py, med siden skrevet til en midlertidig mappe.
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
from graf import MARG_Y
from hjelpetekster import hjelpetekster
from hovedindeks import er_bedre
from lagring_sqlite import demo_sti
from test_hjelpefeltet import NETTLESER, _kjoer

ROT = Path(__file__).resolve().parent.parent
STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
ADRESSENE = ("/boersometer", "/boersometer?periode=1-uke", "/boersometer?periode=velg&dag=2026-10-01")
# Gjennomgangen (VG1): i CI feiler testene når nettleseren mangler, som i test_hjelpefeltet.py.
nettleser = pytest.mark.skipif(
    NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome å måle siden i"
)


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


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.get_data(as_text=True)


def _synlig(html: str) -> str:
    return re.sub(r"[ \t\r\n]+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _regel(velger: str) -> str:
    return re.search(rf"side-oversikt\) {re.escape(velger)} \{{([^}}]*)\}}", STIL).group(1)


# --- Del F: innledningen (U98) -------------------------------------------------


class TestInnledningen:
    def test_samme_tekst_for_en_dag_og_en_periode(self, klient):
        """U98: ville feilet hvis innledningen byttet tekst, og antall linjer,
        ved en periode eller en valgt dag."""
        tekster = {re.search(r'<p class="innledning">(.*?)</p>', _side(klient, a), re.S).group(1) for a in ADRESSENE}
        assert len(tekster) == 1
        assert "Fargen viser endringen i perioden du velger, og rammen viser signalet siste børsdag." in tekster.pop()


# --- Del F: kortet «Mål mot børsen» (spørsmål 14 b) ------------------------------


class TestMaalMotBoersen:
    @pytest.mark.parametrize("adresse", ADRESSENE)
    def test_n_av_m_gikk_bedre_enn_indeksen(self, klient, adresse):
        """Spørsmål 14 b: «N av M gikk bedre enn indeksen», regnet med
        er_bedre som oversikten, av rutene med en endring. Ville feilet med et
        fast tall, med alle 15 som M når noen mangler endring, eller med lik
        som bedre."""
        html = _side(klient, adresse)
        kortet = html.split('<section class="maal"', 1)[1].split("</section>", 1)[0]
        n, m = map(int, re.search(r"<strong>(\d+) av (\d+)</strong> gikk bedre enn indeksen\.", kortet).groups())
        indeks = _tall(re.search(r'<span class="indeksendring[^"]*">([^<]+)</span>', kortet).group(1))
        endringer = [
            _tall(t)
            for t in re.findall(r'<span class="endring">([+-]?\d+,\d+ %)</span>', html.split('<div class="kart"', 1)[1])
        ]
        assert m == len(endringer)
        assert n == sum(er_bedre(e, indeks) for e in endringer)

    def test_uten_indeks_staar_ikke_tallet(self, klient, monkeypatch):
        """Ville feilet med «0 av 15» når indeksen ikke har en endring."""
        monkeypatch.setattr(app_modul, "_indeksen_for_dagen", lambda dag: None)
        kortet = _side(klient, "/boersometer").split('<section class="maal"', 1)[1].split("</section>", 1)[0]
        assert "gikk bedre" not in kortet and '<span class="indeksendring">–</span>' in kortet


def _tall(tekst: str) -> float:
    return float(tekst.replace(" %", "").replace(",", "."))


# --- Del F: størrelsen og gult (svaret 06.11 kl. 22:57) ------------------------------


class TestStoerrelsenOgGult:
    def test_like_store_ruter_i_en_periode_og_etter_volumet_en_dag(self, klient):
        """Svaret 06.11 kl. 22:57: for én dag følger størrelsen volumet, og for
        en periode er rutene like store. Ville feilet hvis rutene var like
        store en dag, eller fulgte volumet i en periode."""

        def arealer(html: str) -> set[float]:
            ut = set()
            for felt in re.findall(r'<section class="bransje"(.*?)</section>', html, re.S):
                b, h = (float(x) for x in re.search(r"--b-bred: ([\d.]+)%; --h-bred: ([\d.]+)%", felt).groups())
                for rb, rh in re.findall(r'<li style="[^"]*--b-bred: ([\d.]+)%; --h-bred: ([\d.]+)%', felt):
                    ut.add(round(float(rb) * b * float(rh) * h / 1e4, 1))
            return ut

        en_dag, perioden = arealer(_side(klient, "/boersometer")), arealer(_side(klient, "/boersometer?periode=1-uke"))
        assert len(en_dag) > 5
        # Feltene er ulike store, men rutene i kartet har samme areal.
        assert len(perioden) <= 2, perioden

    def test_to_nyanser_av_gult(self):
        """Svaret 06.11 kl. 22:57: rammen ved 3 av 3 i --gul-symbol og ringen
        i --oransje, som i appen. Ville feilet med én nyanse for begge."""
        assert re.search(r"\.rute\.ramme-gul, [^{]*\.proeve\.ramme-gul \{ border-color: var\(--gul-symbol\); \}", STIL)
        assert "border: 2px solid var(--oransje)" in _regel(".pille.tre-av-tre")
        farger = dict(re.findall(r"--(oransje|gul-symbol): (#[0-9A-Fa-f]{6});", STIL))
        assert farger["oransje"].lower() != farger["gul-symbol"].lower()


# --- Del F: tabellen (U93) --------------------------------------------------------


class TestTabellen:
    def test_som_paa_forsiden(self, klient):
        """U93: kolonneraden i blekk, et bånd per bransje med symbolet, antallet
        og snittet, oransje strek ved 3 av 3 siste børsdag og styrken i ring.
        Ville feilet med bransjen som egen kolonne, uten båndet, uten streken
        eller ringen."""
        html = _side(klient, "/boersometer")
        tabell = html.split('<table class="boersometertabell">', 1)[1].split("</table>", 1)[0]
        assert re.findall(r'<th scope="col"[^>]*>([^<,]+)', tabell) == [
            "Selskap",
            "Endring",
            "Volum mot vanlig",
            "Signalstyrke",
        ]
        baand = re.findall(
            r'<tbody>\s*<tr class="del oevrige"><th colspan="4" scope="rowgroup"><span class="bransjebaand">(<svg .*?</svg>)',
            tabell,
            re.S,
        )
        # Gjennomgangen (BH11, ECH5): én tbody per bransje, og ECH4: båndet har bakgrunnen fra forsiden.
        assert len(baand) == 8 and tabell.count("<tbody>") == 8
        gule = re.findall(r'<tr class="gul">\s*<td class="selskap"><a href="/aksje/([A-Z]+)"', tabell)
        assert sorted(gule) == ["BRFE", "KVST", "LKSV", "TRHF"]
        for symbol in gule:
            rad = tabell.split(f'href="/aksje/{symbol}"', 1)[1].split("</tr>", 1)[0]
            assert '<span class="pille tre-av-tre">3 av 3</span>' in rad
        assert '<span class="pille to-av-tre">2 av 3</span>' in tabell
        assert "inset 4px 0 0 var(--oransje)" in _regel("tr.gul td:first-child")
        assert "background: var(--baand-oevrige)" in _regel("tr.del.oevrige th")

    def test_ingen_ring_ved_3_av_3_en_annen_dag(self, klient):
        """Gjennomgangen (VG4): en annen dag har radene med gul ramme styrken
        fra den dagen, uten ringen for 3 av 3. Ville feilet hvis «and dagen ==
        siste» falt bort, så «1 av 3» fikk den oransje ringen."""
        html = _side(klient, "/boersometer?periode=velg&dag=2026-10-01")
        tabell = html.split('<table class="boersometertabell">', 1)[1].split("</table>", 1)[0]
        rader = re.findall(r'<tr class="gul">(.*?)</tr>', tabell, re.S)
        assert rader
        for rad in rader:
            assert "pille tre-av-tre" not in rad, rad


# --- Del F: bransjeoverskriften (U97) ---------------------------------------------------


def test_linja_i_overskriften_er_bransje_tillegg(klient, monkeypatch):
    """Gjennomgangen (VG3, BH5): bredden på feltet regnes av Bransje.tillegg,
    så teksten malen viser, må være den samme. Ville feilet med et annet
    format på snittet, eller en annen tekst, i malen enn i Bransje.tillegg."""
    bygde = []
    ekte = app_modul.bygg_boersometer
    monkeypatch.setattr(app_modul, "bygg_boersometer", lambda ruter: bygde.extend(ekte(ruter)) or bygde)
    for adresse in ADRESSENE:
        bygde.clear()
        html = _side(klient, adresse)
        vist = {
            _synlig(navn): _synlig(linje)
            for navn, linje in re.findall(
                r'<span class="bransjenavn">([^<]+)</span></span></span>\s*<span class="tillegg">(.*?)</span></h2>',
                html,
                re.S,
            )
        }
        assert len(vist) == 8 and vist == {b.navn: b.tillegg for b in bygde}, adresse


def test_det_verste_kartet_faar_plass():
    """Gjennomgangen (BH8, ECH8): mange aksjer i én bransje med lang linje, og
    én aksje med MINSTE_VEKT mot resten med STOERSTE_VEKT. Ville feilet hvis
    kartet ikke fant plass, så tabellen sto alene, eller et felt var smalere
    enn linja med antallet og snittet."""
    import boersometer as b
    from kursdata import Aksje

    ruter = [
        b.Rute(
            Aksje(f"A{i}", f"A{i}.OL", f"Aksje {i}", "Energi" if i < 10 else b.BRANSJER[i % 8]),
            -12.34,
            b.STOERSTE_VEKT if i else b.MINSTE_VEKT,
            2,
            None,
        )
        for i in range(15)
    ]
    kartet = b.kart(b.bygg_boersometer(ruter))
    for flate in b.FLATENE:
        for felt in kartet.felt:
            assert felt.plass[flate.navn].b / 100 * flate.minste >= b.tilleggsbredde(felt.bransje) - 1e-9


# --- Del E for børsometeret: høyst 60 ord (U95) og fotnoten (U102) -------------------


def _vinduene(html: str) -> dict[str, str]:
    deler = re.findall(r'<div id="(hjelp-[a-z-]+)" class="hjelpevindu" popover>(.*?)\n</div>', html, flags=re.S)
    return {id_: _synlig(innhold.split("</div>", 1)[1]) for id_, innhold in deler}


class TestHjelpevinduene:
    @pytest.mark.parametrize("adresse", ADRESSENE)
    def test_hoeyst_60_ord_i_hvert_vindu(self, klient, adresse):
        """Svaret 06.11 kl. 23:07, utvidet til børsometeret: hvert vindu har
        høyst 60 ord, telt med \\w+ som på aksjesiden. Ville feilet med vinduet
        for børsometeret før 8.20b, som hadde 266 ord."""
        vinduene = _vinduene(_side(klient, adresse))
        assert set(vinduene) >= {"hjelp-boersometer", "hjelp-perioden"}
        for id_, tekst in vinduene.items():
            assert len(re.findall(r"\w+", tekst)) <= 60, (id_, len(re.findall(r"\w+", tekst)), tekst)

    def test_fotnoten_staar_og_vinduet_gjentar_den_ikke(self, klient):
        """U102: fotnoten om en annen grunn står under kartet, og hjelpen ved
        «?» sier det ikke lenger. Ville feilet hvis vinduet gjentok fotnoten,
        eller fotnoten var borte."""
        html = _side(klient, "/boersometer")
        assert "«Ikke vurdert» kan også ha en annen grunn" in html
        assert "kort kurshistorikk" not in _vinduene(html)["hjelp-boersometer"]


# --- Del J: ordene som er endret ---------------------------------------------------


def test_hva_fargene_betyr_staar_ikke_igjen():
    """J: «Hva fargene betyr» er kortet «Slik leser du børsometeret». Ville
    feilet hvis det gamle navnet sto igjen i hjelpen, README-en, hjelpetekstene
    eller malene."""
    # Story 3.5i: og docs/installasjon.md, med det som er flyttet fra README-en.
    filer = [ROT / "docs" / "hjelp.md", ROT / "README.md", ROT / "docs" / "installasjon.md"]
    filer += [ROT / "src" / "hjelpetekster.py"]
    filer += sorted((ROT / "src" / "templates").glob("*.html"))
    for fil in filer:
        assert "Hva fargene betyr" not in fil.read_text(encoding="utf-8"), fil.name
    assert "«Slik leser du børsometeret»" in (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
    assert all("Hva fargene betyr" not in t.tekst for t in hjelpetekster().values())


# --- BH9 fra 8.20a: lappen over tegneflaten -------------------------------------------


def test_lappen_med_datoen_staar_over_tegneflaten(klient):
    """BH9: lappen med datoen øverst på streken står over tegneflaten, så den
    aldri dekker toppen av kurslinja. Ville feilet med lappen inne i
    tegneflaten, som i 8.20a, eller med kurslinja over MARG_Y."""
    # Streken står ved den første knappen og en valgt dag, ikke ved 6 mnd,
    # som siden åpner med (mutanten for BH9 overlevde med den adressen).
    html = _side(klient, "/aksje/BRFE?periode=siste")
    figuren = html.split("<figure>", 1)[1].split("</figure>", 1)[0]
    assert figuren.count('<rect class="daglapp"') == 2  # den brede og den smale grafen
    for y in re.findall(r'<rect class="daglapp" x="[\d.]+" y="([\d.-]+)" width="44" height="18"', figuren):
        assert 0 <= float(y) and float(y) + 18 < MARG_Y
    for linje in re.findall(r'<polyline class="kurslinje" points="([^"]+)"', figuren):
        assert min(float(p.split(",")[1]) for p in linje.split()) >= MARG_Y - 0.05


# --- Nettleseren: kortene, rutene og 390 px ------------------------------------------------

MAAL_SKRIPT = r"""
const r = {};
const kort = ["section.maal", "section.slik-leser"].map((v) => document.querySelector(v).getBoundingClientRect());
r.kort = kort.map((k) => [Math.round(k.top), Math.round(k.left), Math.round(k.height), Math.round(k.width)]);
r.rulling = document.documentElement.scrollWidth - document.documentElement.clientWidth;
r.piller = [];
for (const p of document.querySelectorAll(".kart .rute .styrke.pille")) {
  const s = getComputedStyle(p);
  if (klippet(p) || s.display === "none") continue;
  const b = p.getBoundingClientRect(), a = p.closest(".rute").getBoundingClientRect();
  r.piller.push([s.fontSize, b.left >= a.left - 0.5 && b.right <= a.right + 0.5 && b.top >= a.top - 0.5 && b.bottom <= a.bottom + 0.5,
                 p.closest(".rute").querySelector(".ticker").textContent]);
}
r.tillegg = Array.from(document.querySelectorAll(".kart section.bransje h2 .tillegg")).map((t) => {
  const b = t.getBoundingClientRect(), h = t.closest("h2").getBoundingClientRect();
  // Gjennomgangen (BH6): h2 klipper, så linja må stå innenfor h2 sidelengs også.
  return [b.left >= h.left - 0.5 && b.right <= h.right + 0.5, b.bottom <= h.bottom + 0.5, b.height > 0];
});
ferdig(r);
"""


@nettleser
class TestINettleseren:
    @pytest.mark.parametrize("bredde", [1056, 1280])
    @pytest.mark.parametrize("adresse", ["/boersometer", "/boersometer?periode=1-uke"])
    def test_kortene_side_om_side_og_like_hoeye(self, klient, tmp_path, bredde, adresse):
        """Spørsmål 15: fra 1056 px står kortene side om side og er like høye.
        Ville feilet med kortene under hverandre, eller ulik høyde."""
        r = _kjoer(_side(klient, adresse), tmp_path, bredde, MAAL_SKRIPT)
        (t1, v1, h1, _), (t2, v2, h2, _) = r["kort"]
        assert t1 == t2 and v1 < v2 and h1 == h2, r["kort"]
        assert r["rulling"] == 0

    @pytest.mark.parametrize("bredde", [390, 1055])
    def test_kortene_under_hverandre_smalere(self, klient, tmp_path, bredde):
        """Spørsmål 15: smalere enn 1056 px står kortene under hverandre, og
        ved 390 px ruller ikke siden vannrett. Ville feilet med kortene side om
        side ved 390 px, eller vannrett rulling."""
        r = _kjoer(_side(klient, "/boersometer"), tmp_path, bredde, MAAL_SKRIPT)
        (t1, _, h1, _), (t2, _, _, _) = r["kort"]
        assert t2 >= t1 + h1, r["kort"]
        assert r["rulling"] == 0

    # Gjennomgangen (VG2): også ved 320 px, der kartet er smalest mot skriften.
    @pytest.mark.parametrize("bredde", [320, 390, 1280])
    @pytest.mark.parametrize("adresse", ["/boersometer", "/boersometer?periode=1-uke"])
    def test_pillene_like_store_og_inne_i_ruta(self, klient, tmp_path, bredde, adresse):
        """U94: «2 av 3» og «3 av 3» i samme størrelse i alle rutene, og aldri
        utenfor ruta. U97: linja med antallet og snittet står hel i
        overskriften. Ville feilet med en pille utenfor ruta, ulik skrift, eller
        en linje som er kuttet."""
        r = _kjoer(_side(klient, adresse), tmp_path, bredde, MAAL_SKRIPT)
        assert r["piller"], "ingen piller i kartet"
        assert {s for s, _, _ in r["piller"]} == {"14px"}, r["piller"]
        assert all(inne for _, inne, _ in r["piller"]), r["piller"]
        assert len(r["tillegg"]) == 8 and all(all(t) for t in r["tillegg"]), json.dumps(r["tillegg"])
        assert r["rulling"] == 0
