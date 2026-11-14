"""Story 9.12: ingen råd i det appen viser (NFR-06, punkt 26 i §8 i PRD-en).

Én test går gjennom alle malene, hjelpetekstene, omvisningen og tekstene i
hjelp.js etter ordene i rådlista i FR-603, den samme lista kontrollen av
KI-tekstene bruker (RAAD i src/ki_kontroll.py). Forslaget i 4.2 i
tilbakemeldingen fra faglærer 12.11, etter gruppens svar 12.11 kl. 20:04.

To slags treff er lov, og grunnen står ved hvert unntak:
- en setning som sier at noe ikke er et råd («ikke et råd», «sier ikke om du
  bør kjøpe eller selge»), fordi den sier det motsatte av et råd (NFR-06, FR-108)
- ordene for notatene om tenkte kjøp og salg, som «Noter et tenkt kjøp»
  (story 8.21, 8.24 og svaret 12.11 kl. 10:16 under 8.27): brukerens egne,
  tenkte handler, ikke noe appen anbefaler

Kode i malene ({% %}, navn i {{ }}) og kommentarer er ikke tekst brukeren ser,
og regnes ikke med. Strengene i {{ }} er det.
"""

import dataclasses
import re
from pathlib import Path

from hjelpetekster import hjelpetekster, omvisningen, rundturer
from ki_kontroll import _RAAD

ROT = Path(__file__).resolve().parent.parent
MALENE = ROT / "src" / "templates"
HJELP_JS = ROT / "src" / "static" / "hjelp.js"

# Unntak 1: setninger som sier at noe ikke er et råd. Ordet «ikke» står foran
# treffet i samme setning.
IKKE_FORAN = re.compile(r"\bikke\b", re.IGNORECASE)
# Unntak 2: notatene om tenkte kjøp og salg (8.21, 8.24, 8.27). Hvert uttrykk
# må dekke hele treffet.
TENKT_HANDEL = (
    r"tenkt kjøp",
    r"tenkte kjøpet",
    r"Tenkt kjøp og salg",
    r"kjøpet",
    r"Kjøpsdag",
    r"kjøpsdagen",
    r"Salgsdag",
    r"et kjøp eller salg",
)
_TENKT_HANDEL = re.compile("|".join(TENKT_HANDEL), re.IGNORECASE)
# En streng i «"…"» eller «'…'» i {{ }} i en mal.
STRENG = re.compile(r"\"([^\"]*)\"|'([^']*)'")
_SETNINGSSLUTT = re.compile(r"[.!?:]\s|<[^>]*>|\n\s*\n")


def _synlig_i_malen(tekst: str) -> str:
    """Teksten i en mal uten kommentarer og kode. Strengene i {{ }} står."""
    tekst = re.sub(r"\{#.*?#\}", " ", tekst, flags=re.S)
    tekst = re.sub(r"<!--.*?-->", " ", tekst, flags=re.S)
    tekst = re.sub(r"\{%.*?%\}", " ", tekst, flags=re.S)

    def strengene(m: re.Match) -> str:
        return " " + " ".join(a or b for a, b in STRENG.findall(m.group(0))) + " "

    return re.sub(r"\{\{.*?\}\}", strengene, tekst, flags=re.S)


def _strengene_i_js(tekst: str) -> str:
    """Bare strengene i hjelp.js, uten kommentarer og kode."""
    tekst = re.sub(r"/\*.*?\*/", " ", tekst, flags=re.S)
    tekst = re.sub(r"(?m)^\s*//.*$", " ", tekst)
    return "\n".join(a or b or c for a, b, c in re.findall(r'"([^"\n]*)"|\'([^\'\n]*)\'|`([^`]*)`', tekst))


def _tekster(obj, sti: str):
    if isinstance(obj, str):
        yield sti, obj
    elif dataclasses.is_dataclass(obj):
        for felt in dataclasses.fields(obj):
            if felt.name != "kilder":
                yield from _tekster(getattr(obj, felt.name), f"{sti}.{felt.name}")
    elif isinstance(obj, dict):
        for noekkel, verdi in obj.items():
            yield from _tekster(verdi, f"{sti}[{noekkel}]")
    elif isinstance(obj, (list, tuple)):
        for i, verdi in enumerate(obj):
            yield from _tekster(verdi, f"{sti}[{i}]")


def alle_tekstene() -> list[tuple[str, str]]:
    """Hver tekst brukeren kan se, med hvor den står."""
    ut = list(_tekster(hjelpetekster(), "hjelpetekster"))
    ut += _tekster(rundturer(), "rundturer")
    ut += _tekster(omvisningen(), "omvisningen")
    for mal in sorted(MALENE.glob("*.html")):
        ut.append((f"templates/{mal.name}", _synlig_i_malen(mal.read_text(encoding="utf-8"))))
    ut.append(("static/hjelp.js", _strengene_i_js(HJELP_JS.read_text(encoding="utf-8"))))
    return ut


def _setningen_foer(tekst: str, start: int) -> str:
    """Setningen fram til treffet."""
    slutter = [m.end() for m in _SETNINGSSLUTT.finditer(tekst, 0, start)]
    return tekst[(slutter[-1] if slutter else 0) : start]


def raadene(tekst: str) -> list[str]:
    """Treffene fra rådlista som ikke er et av de to unntakene."""
    tenkt = [m.span() for m in _TENKT_HANDEL.finditer(tekst)]
    ut = []
    for treff in _RAAD.finditer(tekst):
        if any(a <= treff.start() and treff.end() <= b for a, b in tenkt):
            continue
        if IKKE_FORAN.search(_setningen_foer(tekst, treff.start())):
            continue
        ut.append(" ".join(tekst[max(0, treff.start() - 50) : treff.end() + 30].split()))
    return ut


def test_ingen_raad_i_det_appen_viser():
    """NFR-06. Ville feilet hvis en mal, en hjelpetekst, omvisningen eller
    hjelp.js hadde et ord fra rådlista i FR-603 som verken står i en setning
    som sier at noe ikke er et råd, eller i notatene om tenkte kjøp og salg."""
    funn = [(sti, r) for sti, tekst in alle_tekstene() for r in raadene(tekst)]
    assert funn == []


def test_alle_malene_og_omvisningen_er_med():
    """Ville feilet hvis testen over ikke leste alle malene, eller
    omvisningen og hjelpetekstene var tomme, så den besto uten å se noe."""
    stiene = {sti for sti, _ in alle_tekstene()}
    assert {f"templates/{m.name}" for m in MALENE.glob("*.html")} <= stiene
    assert any(s.startswith("omvisningen") for s in stiene)
    assert any(s.startswith("rundturer") for s in stiene)
    assert sum(s.startswith("hjelpetekster") for s in stiene) > 20


def test_et_raad_stoppes_og_unntakene_er_smale():
    """Ville feilet hvis et ekte råd slapp gjennom, eller unntakene var så
    vide at «bør» eller «anbefal» utenfor en nektende setning ble godtatt."""
    assert raadene("<p>Du bør kjøpe aksjen nå.</p>")
    assert raadene("<p>Vi anbefaler EQNR.</p>")
    assert raadene("<p>Aksjen er ikke dyr. Behold den.</p>")
    assert raadene("<p>Selg før kjøpet.</p>")
    assert raadene("<p>Signalet er ikke et råd.</p>") == []
    assert raadene("<p>Noter et tenkt kjøp</p>") == []
    assert raadene("<p>Sier ikke om du bør kjøpe eller selge.</p>") == []


def test_unntakene_brukes():
    """Ville feilet hvis et uttrykk i TENKT_HANDEL ikke lenger fantes i noe
    appen viser, så lista bare ble lengre over tid."""
    alt = "\n".join(tekst for _, tekst in alle_tekstene())
    ubrukte = [u for u in TENKT_HANDEL if not re.search(u, alt, re.IGNORECASE)]
    assert ubrukte == []
