"""README-en foelger repoet - regel 19 i CLAUDE.md.

Dokumentlista i README-en sto uendret fra 21.09 til 24.09 mens repoet vokste.
Denne testen fanger den ene feilen som kan sjekkes uten skjoenn: en lenke som
peker paa noe som ikke finnes, fordi en fil er flyttet, har faatt nytt navn
eller er slettet. At lista er fullstendig, maa fortsatt ses paa.

Ingen nettverk: lenker til nettet hoppes over, ikke sjekket.
"""

import re
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent

LENKE = re.compile(r"\]\(([^)\s]+)\)")
UTENFOR = ("http://", "https://", "mailto:", "#")


def test_hver_lenke_i_readme_peker_paa_noe_som_finnes():
    tekst = (ROT / "README.md").read_text(encoding="utf-8")

    mangler = [
        maal
        for maal in LENKE.findall(tekst)
        if not maal.startswith(UTENFOR)
        and not (ROT / maal.split("#", 1)[0]).exists()
    ]

    assert not mangler, f"Lenker i README.md som ikke finnes: {mangler}"
