"""Story 8.31: stegkortene og styrken for én dag målt i nettleseren (VG8 og VG4 fra 8.29).

Tillegg 4 til 2.17, etter gruppens ønske 14.11 kl. 21:07. Målene kommer fra
spesifikasjonen for 8.29 (svaret 13.11 kl. 10:32-10:54 og ønsket kl. 20:35,
slik spesifikasjonen gjengir dem) og designreglene, ikke fra det appen viser
nå:

- VG8: stegkortene i «Din egen liste: kom i gang» har 18 px luft over og på
  sidene, 20 px nederst, 14 px hjørner og 14 px mellom, i demoen og den ekte
  versjonen.
- VG4: styrken for én dag i notatene (på siden og i panelet «Mine notater») og
  i «Signalet dag for dag»: 3 av 3 i pillen med fyll i blekk, hvit tekst og en
  ring på 2 px i sterk oransje, 2 av 3 i den hvite pillen med tekst og kant i
  blekk og uten ring, og 1 og 0 av 3 som tekst uten pille. Også en dag i
  ettertid.

Styrken finnes på teksten («2 av 3»), ikke på klassen, så en feil klasse
fanges også. Demoen og den ekte versjonen bygges under tmp_path (regel 22),
og ingen test gjør nettkall (AD-8). Spesifikasjonen er
spec-8-31-maalene-i-nettleseren.md.
"""

import os

import pytest

from test_ettertid_2_17 import demoen, ekte, stier  # noqa: F401  (fiksturene)
from test_historikken import base  # noqa: F401  (fiksturen ekte_med_notater bruker)
from test_hjelpefeltet import NETTLESER, _kjoer
from test_kom_i_gang_8_29 import ekte_med_notater  # noqa: F401  (fiksturen)

I_NETTLESER = pytest.mark.skipif(NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome")

# Designreglene §5: Blekk #16181D, hvit og «Sterk oransje #F2B53A: ringen rundt
# «3 av 3»» (fargene ved en aksje fra 14.10).
BLEKK = "rgb(22, 24, 29)"
HVIT = "rgb(255, 255, 255)"
ORANSJE = "rgb(242, 181, 58)"
GJENNOMSIKTIG = "rgba(0, 0, 0, 0)"

# Svaret 13.11 kl. 10:32-10:54, slik spesifikasjonen for 8.29 gjengir det:
# «stegkortene med 18 px luft (20 px nederst), 14 px hjørner og 14 px mellom».
LUFT = [18.0, 18.0, 20.0, 18.0]  # over, høyre, under, venstre
HJOERNER = 14.0
MELLOM = 14.0


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.get_data(as_text=True)


MAAL_KORTENE = r"""
const s = document.querySelector('#din-egen-liste');
const kort = s ? [...s.querySelectorAll('.stegkort > li')] : [];
ferdig({kort: kort.map((k) => {
  const c = getComputedStyle(k), b = k.getBoundingClientRect();
  return {luft: [c.paddingTop, c.paddingRight, c.paddingBottom, c.paddingLeft].map(parseFloat),
          hjoerner: [c.borderTopLeftRadius, c.borderTopRightRadius, c.borderBottomRightRadius,
                     c.borderBottomLeftRadius].map(parseFloat),
          boks: [b.left, b.top, b.right, b.bottom]};
})});
"""


@I_NETTLESER
@pytest.mark.parametrize("hvilken", ("demoen", "ekte_med_notater"))
@pytest.mark.parametrize("bredde, i_rad", ((1280, True), (390, False)))
def test_stegkortene(request, tmp_path, hvilken, bredde, i_rad):
    """VG8. Ville feilet hvis et stegkort i «Din egen liste: kom i gang» hadde
    annen luft enn 18 px over og på sidene og 20 px nederst, andre hjørner enn
    14 px, eller ikke sto 14 px fra kortet ved siden av (1280 px, de tre i én
    rad) eller over (390 px, under hverandre), i demoen eller den ekte
    versjonen (gjennomgangen, ECH7)."""
    side = _side(request.getfixturevalue(hvilken), "/min-liste")
    assert ("Eksempeltall" in side) == (hvilken == "demoen"), "feil versjon"
    kort = _kjoer(side, tmp_path, bredde, MAAL_KORTENE)["kort"]
    assert len(kort) == 3, kort
    for k in kort:
        assert k["luft"] == pytest.approx(LUFT, abs=0.01), k
        assert k["hjoerner"] == pytest.approx([HJOERNER] * 4, abs=0.01), k
    for forrige, neste in zip(kort, kort[1:]):
        if i_rad:
            assert abs(neste["boks"][1] - forrige["boks"][1]) <= 1, (forrige, neste)
            mellom = neste["boks"][0] - forrige["boks"][2]
        else:
            assert neste["boks"][1] > forrige["boks"][3], (forrige, neste)
            mellom = neste["boks"][1] - forrige["boks"][3]
        assert mellom == pytest.approx(MELLOM, abs=0.5), (forrige, neste)


# Gjennomgangen: bare dagene i «Signalet dag for dag», ikke årssummen i samme
# del (ECH1); panelet åpnes med knappen, fordi notatene står i en <template>
# til da (ECH3); og «synlig» er det nettleseren sier, ikke størrelsen (ECH6).
MAAL_STYRKEN = r"""
const knapp = document.querySelector('a.notatknapp');
if (knapp && document.getElementById('notatpanel')) { knapp.click(); await vent(100); }
const ut = [];
const steder = [['dag for dag', '.historikk li.dag'], ['notat', 'main .etterpaa'],
                ['panel', '.notatpanel-innhold .etterpaa']];
for (const [hvor, velger] of steder) {
  for (const rot of document.querySelectorAll(velger)) {
    if (hvor === 'notat' && rot.closest('.notatpanel')) continue;
    for (const el of rot.querySelectorAll('span')) {
      const m = /^\s*([0-3])\s+av\s+3\s*$/.exec(el.textContent);
      if (!m || el.children.length) continue;
      const c = getComputedStyle(el), b = el.getBoundingClientRect();
      const sider = ['Top', 'Right', 'Bottom', 'Left'];
      const ettertid = !!el.closest('li.ettertid') || !!el.parentElement.querySelector(':scope > .ettertid-merke');
      ut.push({hvor, verdi: Number(m[1]), ettertid,
               bakgrunn: c.backgroundColor, bilde: c.backgroundImage, farge: c.color,
               kant: sider.map((s) => [parseFloat(c['border' + s + 'Width']), c['border' + s + 'Style'],
                                       c['border' + s + 'Color']]),
               radius: parseFloat(c.borderTopLeftRadius), skygge: c.boxShadow, omriss: c.outlineStyle,
               hoeyde: b.height, synlig: el.checkVisibility()});
    }
  }
}
ferdig({styrker: ut, panel: !!document.querySelector('.notatpanel-innhold .etterpaa')});
"""


def _terskel() -> int:
    from signalberegning import STANDARD

    return STANDARD.terskel


def _ring(s: dict) -> bool:
    """En ring på 2 px i sterk oransje: kanten rundt, eller en skygge uten
    uskarphet (begge er en ring i designreglene)."""
    kant = all(b == pytest.approx(2, abs=0.01) and stil == "solid" and farge == ORANSJE for b, stil, farge in s["kant"])
    return kant or f"{ORANSJE} 0px 0px 0px 2px" in s["skygge"]


def _sjekk(s: dict) -> None:
    """Regelen fra tabellen på oversikten, etter designreglene §3 og §5."""
    assert s["synlig"], s
    assert s["bilde"] == "none" and s["omriss"] == "none", s
    if s["verdi"] == 3:
        assert s["bakgrunn"] == BLEKK and s["farge"] == HVIT, s
        assert _ring(s), s
        assert s["radius"] >= s["hoeyde"] / 2 - 0.5, s  # pille
    elif s["verdi"] >= _terskel():
        assert s["bakgrunn"] == HVIT and s["farge"] == BLEKK, s
        # Gjennomgangen (ECH5): kant i blekk, ikke tykkere enn ringen, og
        # ingen ring i noen farge.
        assert all(1 <= b <= 2 and stil == "solid" and farge == BLEKK for b, stil, farge in s["kant"]), s
        assert s["skygge"] == "none", s
        # Samme form som 3 av 3: en pille (spørsmål 7 om høyden).
        assert s["radius"] >= s["hoeyde"] / 2 - 0.5, s
    else:
        assert s["bakgrunn"] == GJENNOMSIKTIG, s
        assert all(b == 0 or stil == "none" for b, stil, _ in s["kant"]), s
        assert s["skygge"] == "none", s


ALLE = {0, 1, 2, 3}
# Siden, og styrkene som må finnes i «Signalet dag for dag», i notatene på
# siden, i panelet og på en dag i ettertid.
SIDENE = (
    # Demoen: september for LKSV har alle fire på dagene i «Signalet dag for
    # dag», også på dager i ettertid før STARTDAG (årssummen teller ikke,
    # ECH1). Notatene med 0-3 står i Min liste og i panelet.
    ("demoen", "/aksje/LKSV?maaned=2026-09", ALLE, set(), ALLE, ALLE),
    ("demoen", "/min-liste", set(), ALLE, set(), set()),
    # Den ekte versjonen: EQNR med 0-3 og et notat hver dag (8.29, VG1 og
    # VG2), med alle notatene åpne (?alle=1, ECH6).
    ("ekte_med_notater", "/aksje/EQNR?alle=1", ALLE, ALLE, ALLE, set()),
    ("ekte_med_notater", "/min-liste", set(), ALLE, set(), set()),
    # Den ekte versjonen etter én henting 22.09, med dagene før i ettertid (2.17).
    ("ekte", "/aksje/EQNR?maaned=2026-09", set(), set(), set(), {2}),
)


@I_NETTLESER
@pytest.mark.parametrize("hvilken, adresse, dag_for_dag, notatene, panelet, i_ettertid", SIDENE)
def test_styrken_for_en_dag(request, tmp_path, hvilken, adresse, dag_for_dag, notatene, panelet, i_ettertid):
    """VG4. Ville feilet hvis 3 av 3 i et notat, i panelet eller i «Signalet
    dag for dag» ikke hadde fyll i blekk, hvit tekst og ringen på 2 px i sterk
    oransje, 2 av 3 ikke var den hvite pillen med kant i blekk uten ring, eller
    1 og 0 av 3 sto i en pille, også en dag i ettertid, i
    demoen eller den ekte versjonen. Ville også feilet hvis en side ikke hadde
    styrkene testen skal måle der."""
    side = _side(request.getfixturevalue(hvilken), adresse)
    assert ("Eksempeltall" in side) == (hvilken == "demoen"), "feil versjon"
    r = _kjoer(side, tmp_path, 1280, MAAL_STYRKEN)
    styrker = r["styrker"]
    assert styrker, "ingen styrke ble målt"
    for s in styrker:
        _sjekk(s)

    def verdiene(hvor: str) -> set[int]:
        return {s["verdi"] for s in styrker if s["hvor"] == hvor}

    assert dag_for_dag <= verdiene("dag for dag"), styrker
    assert notatene <= verdiene("notat"), styrker
    assert panelet <= verdiene("panel"), (r["panel"], styrker)
    assert i_ettertid <= {s["verdi"] for s in styrker if s["ettertid"]}, styrker
    if i_ettertid:
        assert any(s["ettertid"] and s["hvor"] == "dag for dag" for s in styrker), styrker
