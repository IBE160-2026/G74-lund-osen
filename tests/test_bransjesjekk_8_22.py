"""Story 8.22, del B: kontrollsjekken av bransjene 10.11.

Spesifikasjonen er spec-8-22-foelg-en-aksje-og-min-liste.md. Dokumentet er
_bmad-output/planning-artifacts/bransjesjekk-2026-11-10.md.
"""

import re
from collections import Counter
from pathlib import Path

import ferdige_lister

ROT = Path(__file__).resolve().parent.parent
SJEKKEN = ROT / "_bmad-output" / "planning-artifacts" / "bransjesjekk-2026-11-10.md"
DEMOEN = {"HVLK", "NRDE"}


def _tabellen() -> list[tuple[str, str, str]]:
    tekst = SJEKKEN.read_text(encoding="utf-8")
    del_ = tekst.split("## Aksjene", 1)[1]
    return [
        tuple(c.strip() for c in linje.strip().strip("|").split("|"))
        for linje in del_.splitlines()
        if linje.startswith("| ") and not linje.startswith("| Ticker")
    ]


def test_tabellen_er_lik_bransje():
    """Ville feilet hvis dokumentet og BRANSJE i koden sa noe ulikt om en
    eneste aksje, eller en aksje manglet i det ene."""
    rader = _tabellen()
    med = {t: b for t, b, _ in rader if b != "–"}
    assert med == {k: v for k, v in ferdige_lister.BRANSJE.items() if k not in DEMOEN}
    assert len(rader) == 297 and len({t for t, _, _ in rader}) == 297


def test_multi_og_scoin_er_ute_med_grunnen():
    """Ville feilet hvis grunnene til at MULTI og SCOIN er ute, manglet."""
    ute = {t: k for t, b, k in _tabellen() if b == "–"}
    assert set(ute) == {"MULTI", "SCOIN"}
    assert "fusjon" in ute["MULTI"] and "avvikling" in ute["SCOIN"]


def test_kildene_og_tallene():
    """Ville feilet hvis antallet per kilde ikke stemte med forslagsfila
    (87 sjekket 08.11, 157 forslag og 53 usikre, der 15 er de 15 i lista),
    eller tabellen hadde en kolonne til, som selskapsnavnet."""
    rader = _tabellen()
    assert all(len(r) == 3 for r in rader)
    kilder = Counter(k.split(":")[0] if k.startswith("tatt ut") else k for _, _, k in rader)
    assert kilder["sjekket 08.11 kl. 22:01 og 22:03"] == 87
    assert kilder["de 15 i lista, bransjen fra designregler.md §4"] == 15
    assert kilder["forslag, sjekket 10.11 kl. 14:43"] == 141
    assert kilder["forslag merket usikker, sjekket 10.11 kl. 14:43"] == 52
    tekst = SJEKKEN.read_text(encoding="utf-8")
    assert "`302e28433bf582ec9abad65ffde06c2dbcd533cd6130713990e2fa3ed0c6dec9`" in tekst
    assert re.search(r"^status: final$", tekst, re.M)
