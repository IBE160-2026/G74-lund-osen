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
README = ROT / "README.md"
MATRISEN = ROT / "docs" / "vurderingsmatrise.md"
GRENSE = 15 * 1024 * 1024
BILDE = re.compile(r"^!\[([^\]]+)\]\(skjermene/([a-z0-9-]+\.png)\)$", re.M)
LENKE = re.compile(r"\[(?:Spesifikasjonen|Storyen)\]\(\.\./([^)#]+)(?:#([^)]+))?\)")
# 8.14 og 2.6 har én felles spesifikasjon (spec-2-6-justeringsdager.md).
FELLES_SPESIFIKASJON = {"8.14": "2-6"}


def _tekst() -> str:
    return SIDEN.read_text(encoding="utf-8")


def _anker(overskrift: str) -> str:
    """Ankeret GitHub lager av en overskrift, som _anker i test_docker.py."""
    return re.sub(r"[^\w\- ]", "", overskrift.strip().lower()).replace(" ", "-")


def _storyene() -> dict[str, str]:
    """Delen under hver «### N.M …» på siden, uten overskriften."""
    deler = re.split(r"^### ", _tekst(), flags=re.M)[1:]
    return {d.split(" ", 1)[0]: d.split("\n", 1)[1].split("\n## ", 1)[0] for d in deler}


def _avsnitt(del_: str) -> list[str]:
    return [a.strip() for a in re.split(r"\n\s*\n", del_) if a.strip()]


def _epicene_i_epics() -> list[tuple[str, list[str]]]:
    """Epicene og storyene i rekkefølgen i epics.md, med 8.28 i Epic 8 før 8.29."""
    rekke: list[tuple[str, list[str]]] = []
    for linje in EPICS.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^## (Epic \d+: .*)", linje):
            rekke.append((m.group(1), []))
        elif (m := re.match(r"^### Story (\d+\.\w+): ", linje)) and rekke:
            rekke[-1][1].append(m.group(1))
    for navn, st in rekke:
        if "8.28" in st and not navn.startswith("Epic 8"):
            st.remove("8.28")
    for navn, st in rekke:
        if navn.startswith("Epic 8"):
            st.insert(st.index("8.29"), "8.28")
    return rekke


def _epicene_paa_siden() -> list[tuple[str, list[str]]]:
    rekke: list[tuple[str, list[str]]] = []
    for linje in _tekst().splitlines():
        if m := re.match(r"^## (Epic \d+: .*)", linje):
            rekke.append((m.group(1), []))
        elif (m := re.match(r"^### (\d+\.\w+) ", linje)) and rekke:
            rekke[-1][1].append(m.group(1))
    return rekke


def test_frontmatteren():
    """Regel 4: samme frontmatter som prd.md, med updated fra klokka."""
    hode = _tekst().split("---\n", 2)[1]
    for felt in ("title:", "status: aktiv", "created: 2026-11-22"):
        assert felt in hode, felt
    assert re.search(r"^updated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", hode, flags=re.M), hode


def test_epicene_og_storyene_i_rekkefoelgen_i_epics():
    """Ville feilet hvis en epic eller story manglet, sto to ganger, sto
    under feil epic eller i en annen rekkefølge enn i epics.md
    (gjennomgangen, BH1). 8.28 står i Epic 8, foran 8.29."""
    assert _epicene_paa_siden() == _epicene_i_epics()


def test_tallene_oeverst_stemmer_med_siden_og_epics():
    """Ville feilet hvis tallene øverst ikke stemte med epics.md og bildene
    på siden."""
    tekst = _tekst()
    m = re.search(r"Siden har (\d+) epics, (\d+) storyer og (\d+) bilder\. (\d+) av storyene har ett eller to", tekst)
    assert m, "tallene øverst mangler"
    epics, storyer, bilder, med_bilde = map(int, m.groups())
    i_epics = _epicene_i_epics()
    assert epics == len(i_epics)
    assert storyer == sum(len(st) for _, st in i_epics)
    assert bilder == len(BILDE.findall(tekst))
    assert med_bilde == sum(1 for d in _storyene().values() if BILDE.search(d))
    assert "fra demoen, med oppdiktede selskaper" in tekst


def test_tallene_i_readme_og_matrisen_stemmer():
    """Gjennomgangen (ECH1): README-en og vurderingsmatrisen sier hvor mange
    bilder siden har, og tallet skal følge siden."""
    bilder = len(BILDE.findall(_tekst()))
    med_bilde = sum(1 for d in _storyene().values() if BILDE.search(d))
    uten = len(_storyene()) - med_bilde
    readme = [linje for linje in README.read_text(encoding="utf-8").splitlines() if "(docs/skjermene.md)" in linje]
    assert any(f": {bilder} bilder av demoen" in linje for linje in readme), readme
    matrisen = [linje for linje in MATRISEN.read_text(encoding="utf-8").splitlines() if "(skjermene.md)" in linje]
    assert len(matrisen) == 1
    assert f"Den har {bilder} bilder" in matrisen[0] and f"de {med_bilde} storyene" in matrisen[0]
    assert f"De {uten} andre" in matrisen[0]


def test_en_tekst_under_hvert_bilde_eller_en_linje():
    """Gjennomgangen (BH3): under hvert bilde står en tekst, og den siste
    har lenken. En story uten bilde har én linje med tekst før lenken.
    Ingen story har mer enn to bilder."""
    for story, del_ in _storyene().items():
        avsnitt = _avsnitt(del_)
        bilder = [a for a in avsnitt if BILDE.fullmatch(a)]
        assert len(bilder) <= 2, story
        if not bilder:
            assert len(avsnitt) == 1, story
        else:
            assert len(avsnitt) == 2 * len(bilder), story
            for i in range(0, len(avsnitt), 2):
                assert BILDE.fullmatch(avsnitt[i]), (story, i)
                assert not BILDE.search(avsnitt[i + 1]), (story, i)
        siste = avsnitt[-1]
        m = LENKE.search(siste)
        assert m and siste.endswith(")"), story
        assert len(siste[: m.start()].strip()) > 20, story


def test_hver_lenke_gaar_til_storyen_sin():
    """Ville feilet hvis en lenke pekte på en fil eller et anker som ikke
    finnes, eller på en annen story (gjennomgangen, BH2)."""
    ankrene = {_anker(h) for h in re.findall(r"^#+ (.+)$", EPICS.read_text(encoding="utf-8"), flags=re.M)}
    for story, del_ in _storyene().items():
        for m in LENKE.finditer(del_):
            sti, anker = m.groups()
            assert (ROT / sti).is_file(), (story, sti)
            if anker:
                assert sti.endswith("epics.md") and anker in ankrene, (story, anker)
                assert anker.startswith(f"story-{story.replace('.', '')}-"), (story, anker)
            else:
                nummer = FELLES_SPESIFIKASJON.get(story, story.replace(".", "-"))
                assert Path(sti).name.startswith(f"spec-{nummer}"), (story, sti)


def test_hvert_bilde_hoerer_til_storyen_sin():
    """Gjennomgangen (BH2): filnavnet og alt-teksten begynner med storyen."""
    for story, del_ in _storyene().items():
        for alt, navn in BILDE.findall(del_):
            assert navn.startswith(story.replace(".", "-") + "-"), (story, navn)
            assert alt.startswith(f"Story {story}, "), (story, alt)
            assert "i demoen med oppdiktede selskaper" in alt, navn


def test_hvert_bilde_har_en_fil_og_hver_fil_et_bilde():
    """Ville feilet hvis en lenke pekte på et bilde som mangler, mappa hadde
    et bilde siden ikke viser, eller et bilde ikke var sporet i git
    (gjennomgangen, ECH2)."""
    import shutil
    import subprocess

    lenket = [navn for _, navn in BILDE.findall(_tekst())]
    assert len(lenket) == len(set(lenket))
    assert sorted(lenket) == sorted(p.name for p in MAPPA.glob("*.png"))
    if shutil.which("git") and (ROT / ".git").exists():
        svar = subprocess.run(
            ["git", "-C", str(ROT), "ls-files", "docs/skjermene"], capture_output=True, text=True, check=True
        )
        sporet = {Path(f).name for f in svar.stdout.split()}
        assert sporet == set(lenket), set(lenket) ^ sporet


def test_bildene_er_png_1280_px_uten_tekstbiter():
    """Ville feilet hvis et bilde ikke var 1280 px bredt, ikke var en PNG,
    eller hadde tekstbiter (metadata) i fila."""
    for p in sorted(MAPPA.glob("*.png")):
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
