"""Story 9.26: siden med skjermene i OSE Signal, ordnet etter epic og story.

Spesifikasjonen er spec-9-26-skjermene.md. Bildene har ikke avtrykk som
bildene i docs/appen/, fordi de er et bilde av appen på én commit
(«Avtrykk og tester» i spesifikasjonen). Testene her sjekker siden og
bildene i stedet. Ingen nettkall (AD-8).
"""

import re
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
SIDEN = ROT / "docs" / "skjermene.md"
MAPPA = ROT / "docs" / "skjermene"
EPICS = ROT / "_bmad-output" / "planning-artifacts" / "epics.md"
GRENSE = 15 * 1024 * 1024
BILDE = re.compile(r"^!\[([^\]]+)\]\(skjermene/([a-z0-9-]+\.png)\)$", re.M)
LENKE = re.compile(r"\[(?:Spesifikasjonen|Storyen)\]\(\.\./([^)#]+)(?:#([^)]+))?\)$")


def _tekst() -> str:
    return SIDEN.read_text(encoding="utf-8")


def _anker(overskrift: str) -> str:
    """Ankeret GitHub lager av en overskrift, som _anker i test_docker.py."""
    return re.sub(r"[^\w\- ]", "", overskrift.strip().lower()).replace(" ", "-")


def _storyene() -> dict[str, str]:
    """Delen under hver «### N.M …» på siden."""
    deler = re.split(r"^### ", _tekst(), flags=re.M)[1:]
    return {d.split(" ", 1)[0]: d.split("\n## ", 1)[0] for d in deler}


def test_frontmatteren():
    """Regel 4: samme frontmatter som prd.md."""
    hode = _tekst().split("---\n", 2)[1]
    for felt in ("title:", "status: aktiv", "created: 2026-11-22", "updated: 2026-"):
        assert felt in hode, felt


def test_tallene_oeverst_stemmer_med_siden():
    """Ville feilet hvis tallene øverst ikke stemte med overskriftene og
    bildene på siden."""
    tekst = _tekst()
    m = re.search(r"Siden har (\d+) epics, (\d+) storyer og (\d+) bilder\. (\d+) av storyene", tekst)
    assert m, "tallene øverst mangler"
    epics, storyer, bilder, med_skjerm = map(int, m.groups())
    assert epics == len(re.findall(r"^## Epic \d+: ", tekst, flags=re.M))
    assert storyer == len(re.findall(r"^### \d+\.\w+ ", tekst, flags=re.M))
    assert bilder == len(BILDE.findall(tekst))
    assert med_skjerm == sum(1 for d in _storyene().values() if BILDE.search(d))
    assert "fra demoen, med oppdiktede selskaper" in tekst


def test_hver_story_i_epics_staar_en_gang():
    """Ville feilet hvis en story i epics.md manglet på siden, eller sto to
    ganger."""
    i_epics = re.findall(r"^### Story (\d+\.\w+): ", EPICS.read_text(encoding="utf-8"), flags=re.M)
    paa_siden = re.findall(r"^### (\d+\.\w+) ", _tekst(), flags=re.M)
    assert sorted(i_epics) == sorted(paa_siden)
    assert len(paa_siden) == len(set(paa_siden))


def test_ett_eller_to_bilder_eller_en_linje_per_story():
    """Ville feilet hvis en story hadde mer enn to bilder, eller verken
    bilde eller en linje om hvorfor."""
    for story, del_ in _storyene().items():
        n = len(BILDE.findall(del_))
        assert n <= 2, story
        if n == 0:
            linjene = [linje for linje in del_.splitlines()[1:] if linje.strip()]
            assert len(linjene) == 1, story


def test_hver_tekst_lenker_til_en_kilde_som_finnes():
    """Ville feilet hvis en tekst manglet lenken til spesifikasjonen eller
    storyen, eller lenken pekte på en fil eller et anker som ikke finnes."""
    ankrene = {_anker(h) for h in re.findall(r"^#+ (.+)$", EPICS.read_text(encoding="utf-8"), flags=re.M)}
    for story, del_ in _storyene().items():
        siste = [linje for linje in del_.splitlines() if linje.strip()][-1]
        m = LENKE.search(siste)
        assert m, story
        sti, anker = m.groups()
        assert (ROT / sti).is_file(), (story, sti)
        if anker:
            assert sti.endswith("epics.md") and anker in ankrene, (story, anker)
        else:
            assert "/spec-" in sti, story


def test_hvert_bilde_har_en_fil_og_hver_fil_et_bilde():
    """Ville feilet hvis en lenke pekte på et bilde som mangler, eller mappa
    hadde et bilde siden ikke viser."""
    lenket = [navn for _, navn in BILDE.findall(_tekst())]
    assert len(lenket) == len(set(lenket))
    assert sorted(lenket) == sorted(p.name for p in MAPPA.iterdir())


def test_bildene_er_png_1280_px_uten_tekstbiter():
    """Ville feilet hvis et bilde ikke var 1280 px bredt, ikke var en PNG,
    eller hadde tekstbiter (metadata) i fila."""
    for p in sorted(MAPPA.iterdir()):
        data = p.read_bytes()
        assert data[:8] == bytes.fromhex("89504e470d0a1a0a"), p.name
        assert int.from_bytes(data[16:20], "big") == 1280, p.name
        biter, i = [], 8
        while i < len(data):
            lengde = int.from_bytes(data[i : i + 4], "big")
            biter.append(data[i + 4 : i + 8].decode("ascii"))
            i += 12 + lengde
        assert biter[0] == "IHDR" and biter[-1] == "IEND", p.name
        assert not {"tEXt", "iTXt", "zTXt", "eXIf"} & set(biter), p.name


def test_mappa_er_under_15_mb():
    """Instruksjonen 22.11 kl. 19:06: hele mappa under 15 MB."""
    assert sum(p.stat().st_size for p in MAPPA.iterdir()) < GRENSE


def test_alt_teksten_sier_at_det_er_demoen():
    for alt, navn in BILDE.findall(_tekst()):
        assert "i demoen med oppdiktede selskaper" in alt, navn
