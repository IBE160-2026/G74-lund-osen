"""Story 9.20: sporingen av PRD-en mot faglærers rubrikk.

Gruppens svar 17.11 kl. 12:29 («Rett alt, ID-ene står»): prd-sporing.md ved
siden av prd.md har en rad for hver ID i prd.md, med avsnittet, statusen,
storyene og testfilene, og lista over [ANTAKELSE] og [FORELØPIG], begge veier
(V13 i valideringen). Testene her holder fila sann når prd.md endres.
"""

import re
from pathlib import Path

from test_prd_9_11 import _ankrene

ROT = Path(__file__).resolve().parent.parent
MAPPA = ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20"
PRD = MAPPA / "prd.md"
SPORINGEN = MAPPA / "prd-sporing.md"
ID = re.compile(r"\b(?:FR-\d{3}A?|NFR-\d\d|UJ-\d+|SM-\d+)\b")
MARKOER = re.compile(r"`\[(?:ANTAKELSE|FORELØPIG)\][^`]*`")
STATUS = (
    "bygget",
    "bygget, en del senere",
    "senere",
    "senere (plan A)",
    "utenfor v1 (plan A)",
    "tatt bort",
    "gjelder hele appen",
    "måles",
)


def _prd() -> str:
    return PRD.read_text(encoding="utf-8")


def _sporingen() -> str:
    return SPORINGEN.read_text(encoding="utf-8")


def _radene() -> dict[str, list[str]]:
    """ID -> cellene i raden, fra tabellen under «## Tabellen»."""
    tabellen = _sporingen().split("\n## Tabellen\n", 1)[1].split("\n## ", 1)[0]
    ut = {}
    for rad in tabellen.splitlines():
        celler = [c.strip() for c in rad.strip().strip("|").split("|")]
        if rad.startswith("| ") and ID.fullmatch(celler[0]):
            assert celler[0] not in ut, f"{celler[0]} står to ganger"
            ut[celler[0]] = celler
    return ut


def _antakelsene() -> list[list[str]]:
    del_ = _sporingen().split("\n## Antakelser og foreløpige tall\n", 1)[1].split("\n## ", 1)[0]
    return [
        [c.strip() for c in rad.strip().strip("|").split("|")]
        for rad in del_.splitlines()
        if rad.startswith('| <a name="a')
    ]


def test_hver_id_i_prd_har_en_rad():
    """Ville feilet hvis en FR, NFR, UJ eller SM i prd.md manglet i
    sporingen, for eksempel et nytt krav uten rad."""
    mangler = sorted(set(ID.findall(_prd())) - set(_radene()))
    assert mangler == []


def test_hver_rad_er_en_id_i_prd():
    """Ville feilet hvis sporingen hadde en ID som ikke står i prd.md, for
    eksempel et krav som er tatt ut eller fått feil nummer."""
    ukjente = sorted(set(_radene()) - set(ID.findall(_prd())))
    assert ukjente == []


def test_statusen_er_en_av_de_kjente():
    """Ville feilet hvis en rad hadde en status som ikke er forklart i
    «Slik leses kolonnene»."""
    feil = {i: celler[2] for i, celler in _radene().items() if celler[2] not in STATUS}
    assert feil == {}


def test_hver_testfil_finnes():
    """Ville feilet hvis sporingen viste til en testfil som ikke finnes, for
    eksempel etter at en fil fikk nytt navn."""
    filene = set(re.findall(r"`(tests/[\w/]+\.py)`", _sporingen()))
    assert filene, "ingen testfiler i sporingen"
    assert sorted(f for f in filene if not (ROT / f).is_file()) == []


def test_hver_rad_har_storyer_og_tester_eller_ingen():
    """Ville feilet hvis en celle for storyene eller testene var tom, i stedet
    for å si «ingen»."""
    tomme = [i for i, celler in _radene().items() if not celler[3] or not celler[4]]
    assert tomme == []


def test_antakelsene_begge_veier():
    """V13. Ville feilet hvis antallet markører i prd.md ikke var antallet
    rader i lista, en markør ikke lenket til sin rad, eller en rad lenket til
    et anker i prd.md som ikke finnes."""
    prd = _prd()
    markoerene = MARKOER.findall(prd)
    radene = _antakelsene()
    assert len(markoerene) == len(radene), (len(markoerene), len(radene))
    ankrene = _ankrene(prd)
    for nr, celler in enumerate(radene, start=1):
        assert celler[0] == f'<a name="a{nr}"></a>A{nr}', celler[0]
        # Markøren i prd.md lenker til raden.
        assert re.search(r"`\[(?:ANTAKELSE|FORELØPIG)\][^`]*` \(\[A" + str(nr) + rf"\]\(prd-sporing\.md#a{nr}\)\)", prd)
        # Raden lenker til kravet der markøren står.
        anker = re.search(r"\(prd\.md#([^)]+)\)", celler[2]).group(1)
        assert anker in ankrene, anker
