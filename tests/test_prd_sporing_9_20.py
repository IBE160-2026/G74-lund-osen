"""Story 9.20: sporingen av PRD-en mot faglærers rubrikk.

Gruppens svar 17.11 kl. 12:29 («Rett alt, ID-ene står»): prd-sporing.md ved
siden av prd.md har en rad for hver ID i prd.md, med avsnittet, statusen,
storyene og testfilene, og lista over [ANTAKELSE] og [FORELØPIG], begge veier
(V13 i valideringen). Testene her holder fila sann når prd.md endres.

Gjennomgangen av 9.20 (VG1, VG3, VG4): avsnittet regnes av hvor overskriften
står i prd.md, statusen av radene i tabellen i §2, storyene slås opp i
epics.md, og numrene som mangler, regnes av prd.md. Hver markør lenker til
raden for kravet den står i. Lenkene i svaret på tilbakemeldingen, i
«Teknologi og nøkler» og i sporingen peker på filer og ankre som finnes.
"""

import re
from pathlib import Path

import pytest

from test_prd_9_11 import _anker, _ankrene

ROT = Path(__file__).resolve().parent.parent
MAPPA = ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20"
PRD = MAPPA / "prd.md"
SPORINGEN = MAPPA / "prd-sporing.md"
EPICS = ROT / "_bmad-output" / "planning-artifacts" / "epics.md"
SVARET = MAPPA / "tilbakemelding-prd-svar.md"
TEKNOLOGI = ROT / "_bmad-output" / "planning-artifacts" / "architecture" / "teknologi-og-noekler.md"
ID = re.compile(r"\b(?:FR-\d{3}A?|NFR-\d\d|UJ-\d+|SM-\d+)\b")
# Hver markør, med eller uten kodeformat.
MARKOER = re.compile(r"\[(?:ANTAKELSE|FORELØPIG)\]")
OVERSKRIFT = re.compile(r"^#{3,4} ((?:FR-\d{3}A?|NFR-\d\d)) — (.+)$")


def _prd() -> str:
    return PRD.read_text(encoding="utf-8")


def _sporingen() -> str:
    return SPORINGEN.read_text(encoding="utf-8")


def _del(tekst: str, overskrift: str) -> str:
    return tekst.split(f"\n## {overskrift}\n", 1)[1].split("\n## ", 1)[0]


def _radene() -> dict[str, list[str]]:
    """ID -> cellene i raden, fra tabellen under «## Tabellen»."""
    ut = {}
    for rad in _del(_sporingen(), "Tabellen").splitlines():
        celler = [c.strip() for c in rad.strip().strip("|").split("|")]
        if rad.startswith("| ") and ID.fullmatch(celler[0]):
            assert celler[0] not in ut, f"{celler[0]} står to ganger"
            ut[celler[0]] = celler
    return ut


def _avsnittene() -> dict[str, str]:
    """ID -> avsnittet, regnet av hvor overskriften står i prd.md."""
    ut, gjeldende = {}, ""
    for linje in _prd().splitlines():
        m = re.match(r"^#{2,3} (.+)$", linje)
        if m:
            tittel = m.group(1)
            if tittel.startswith("Vedlegg A"):
                gjeldende = "vedlegg A"
            elif gjeldende.startswith("vedlegg A") and re.match(r"4\.\d", tittel):
                gjeldende = "vedlegg A, " + tittel.split(" ", 1)[0]
            elif re.match(r"\d\. ", tittel):
                gjeldende = "§" + tittel.split(".", 1)[0]
            elif re.match(r"4\.\d ", tittel):
                gjeldende = "§" + tittel.split(" ", 1)[0]
        h = OVERSKRIFT.match(linje)
        if h:
            ut[h.group(1)] = gjeldende
    return ut


def _tabellen_i_2() -> dict[str, list[tuple[str, str]]]:
    """FR -> [(kjerne/ekstra/senere, ja/nei)] fra tabellen i §2."""
    del2 = _prd().split("### Kjerne, ekstra og senere\n", 1)[1].split("\n### ", 1)[0]
    ut: dict[str, list[tuple[str, str]]] = {}
    for rad in del2.splitlines():
        if not rad.startswith("| FR-"):
            continue
        fr, _, status, bygget = [c.strip() for c in rad.strip().strip("|").split("|")]
        for bit in fr.split(", "):
            ender = re.findall(r"FR-\d{3}A?", bit)
            if "–" in bit and len(ender) == 2:
                fra, til = (int(e[3:6]) for e in ender)
                suffiks = "A" if ender[0].endswith("A") else ""
                dekket = [f"FR-{n}{suffiks}" for n in range(fra, til + 1)]
            else:
                dekket = ender
            for d in dekket:
                ut.setdefault(d, []).append((status, bygget))
    return ut


def _ventet_status(i: str, avsnitt: str, tabellen: dict) -> str:
    """Regelen i «Slik leses kolonnene»."""
    if i.startswith("NFR"):
        return "gjelder hele appen"
    if i.startswith("UJ"):
        return "bygget"
    if i.startswith("SM"):
        return "måles"
    if avsnitt.startswith("vedlegg A"):
        return "utenfor v1 (plan A)"
    rader = tabellen[i]
    if any(b == "ja" for _, b in rader):
        return "bygget, en del senere" if any(s == "senere" for s, _ in rader) else "bygget"
    if all(s == "senere" for s, _ in rader):
        return "senere"
    return "tatt bort"


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


def test_avsnittet_er_der_overskriften_staar():
    """VG1. Ville feilet hvis et krav var flyttet i prd.md, som FR-407 til
    §4.4, uten at avsnittet i sporingen ble endret. UJ står i §1 og SM i §7.
    FR-404 og FR-405 står i vedlegg A, under 4.3, men hører til 4.4, så
    sporingen sier bare «vedlegg A»."""
    avsnittene = _avsnittene()
    feil = {}
    for i, celler in _radene().items():
        ventet = "§1" if i.startswith("UJ") else "§7" if i.startswith("SM") else avsnittene[i]
        if i in ("FR-404", "FR-405"):
            ventet = "vedlegg A"
        if celler[1] != ventet:
            feil[i] = (celler[1], ventet)
    assert feil == {}


def test_statusen_er_regnet_av_tabellen_i_2():
    """VG1. Ville feilet hvis statusen i en rad ikke fulgte radene i tabellen
    i §2 etter regelen i «Slik leses kolonnene», for eksempel et krav som var
    bygget, men sto som senere. FR-606 er senere og plan A, og FR-108 er
    tatt bort."""
    avsnittene, tabellen = _avsnittene(), _tabellen_i_2()
    feil = {}
    for i, celler in _radene().items():
        ventet = _ventet_status(i, avsnittene.get(i, ""), tabellen)
        if i == "FR-606":
            ventet = "senere (plan A)"
        if celler[2] != ventet:
            feil[i] = (celler[2], ventet)
    assert feil == {}


def test_storyene_finnes_i_epics():
    """VG1. Ville feilet hvis en story i sporingen ikke har en overskrift
    «### Story X.Y» i epics.md, for eksempel et nummer med en skrivefeil."""
    finnes = set(re.findall(r"^### Story ([0-9]+\.[0-9]+[a-z]?):", EPICS.read_text(encoding="utf-8"), re.MULTILINE))
    feil = {}
    for i, celler in _radene().items():
        ukjente = [nr for nr in re.findall(r"\b\d+\.\d+[a-z]?\b", celler[3]) if nr not in finnes]
        if ukjente:
            feil[i] = ukjente
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


def test_numrene_som_mangler():
    """VG1. Ville feilet hvis «Hvorfor noen numre mangler» ikke stemte med
    prd.md: et krav lista sier står i vedlegg A, sto i hoveddelen, en
    A-variant lista sier ikke finnes, fantes, eller intervallene lista sier er
    uten hull, ikke var nøyaktig ID-ene i prd.md utenom plan A."""
    del_ = _del(_sporingen(), "Hvorfor noen numre mangler")
    avsnittene = _avsnittene()
    prd_id = set(ID.findall(_prd()))
    hoveddel, vedlegg = _prd().split("\n## Vedlegg A", 1)
    for nr in ("4.3", "4.5"):
        assert f"\n### {nr} " not in hoveddel and f"\n### {nr} " in vedlegg, nr
    for i in ("FR-404", "FR-405", "FR-602A", "FR-603A", "FR-604A", "FR-606A"):
        assert i in del_, i
        assert avsnittene[i].startswith("vedlegg A"), i
    for i in ("FR-601A", "FR-605A", "FR-607A", "FR-608A"):
        assert i in del_ and i not in prd_id, i
    assert avsnittene["FR-407"] == "§4.4"
    linja = " ".join(next(bit for bit in del_.split("\n- ") if "uten hull" in bit).split())
    sagt = set()
    for fra, til in re.findall(r"((?:FR|NFR|UJ|SM)-\d+)–((?:FR|NFR|UJ|SM)-\d+)", linja):
        prefiks, a = fra.rsplit("-", 1)
        b = til.rsplit("-", 1)[1]
        sagt |= {f"{prefiks}-{n:0{len(a)}d}" for n in range(int(a), int(b) + 1)}
    uten_plan_a = {i for i in prd_id if not i.endswith("A") and not i.startswith(("FR-3", "FR-5"))}
    assert sagt == uten_plan_a, (sorted(uten_plan_a - sagt), sorted(sagt - uten_plan_a))


def _markoerene() -> list[tuple[str, int]]:
    """(overskriften til kravet markøren står i, nummeret på raden den
    lenker til), i rekkefølgen i prd.md. Nummeret er 0 uten lenke."""
    ut, kravet = [], ""
    for linje in _prd().splitlines():
        if OVERSKRIFT.match(linje):
            kravet = linje.split(" ", 1)[1]
        for m in MARKOER.finditer(linje):
            lenke = re.match(r"[^`\[]*`? \(\[A(\d+)\]\(prd-sporing\.md#a\1\)\)", linje[m.end() :])
            ut.append((kravet, int(lenke.group(1)) if lenke else 0))
    return ut


def _antakelsene() -> list[list[str]]:
    return [
        [c.strip() for c in rad.strip().strip("|").split("|")]
        for rad in _del(_sporingen(), "Antakelser og foreløpige tall").splitlines()
        if rad.startswith('| <a name="a')
    ]


def test_antakelsene_begge_veier():
    """V13 og VG3. Ville feilet hvis antallet markører i prd.md, med eller
    uten kodeformat, ikke var antallet rader i lista, en markør ikke lenket til
    sin rad, eller en rad lenket til et annet krav enn det markøren står i."""
    tekst = _prd()
    markoerene, radene = _markoerene(), _antakelsene()
    assert len(markoerene) == len(radene), (len(markoerene), len(radene))
    assert [nr for _, nr in markoerene] == list(range(1, len(radene) + 1))
    for (kravet, nr), celler in zip(markoerene, radene):
        assert celler[0] == f'<a name="a{nr}"></a>A{nr}', celler[0]
        anker = re.search(r"\(prd\.md#([^)]+)\)", celler[2]).group(1)
        # Ankeret til kravets overskrift, eller et gammelt anker rett foran den.
        foer = tekst[: tekst.index("#### " + kravet)].rstrip().rsplit("\n", 1)[-1]
        assert anker in (_anker(kravet), *re.findall(r'<a name="([^"]+)"></a>', foer)), (kravet, anker)


def _lenkene(fil: Path) -> list[tuple[str, str]]:
    tekst = re.sub(r"`[^`\n]*`", "", fil.read_text(encoding="utf-8"))
    return re.findall(r"\]\(([^)\s#]*)(?:#([^)\s]+))?\)", tekst)


@pytest.mark.parametrize("fil", [SVARET, TEKNOLOGI, SPORINGEN], ids=lambda f: f.name)
def test_lenkene_peker_paa_noe_som_finnes(fil):
    """VG4. Ville feilet hvis en relativ lenke i svaret på tilbakemeldingen,
    i «Teknologi og nøkler» eller i sporingen pekte på en fil som ikke finnes,
    eller på et anker som ikke finnes i en .md-fil."""
    brutt = []
    for sti, anker in _lenkene(fil):
        if sti.startswith(("http://", "https://", "mailto:")):
            continue
        maal = (fil.parent / sti).resolve() if sti else fil
        if not maal.exists():
            brutt.append(sti)
        elif anker and maal.suffix == ".md" and anker not in _ankrene(maal.read_text(encoding="utf-8")):
            brutt.append(f"{sti}#{anker}")
    assert brutt == []
