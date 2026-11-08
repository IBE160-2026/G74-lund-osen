"""Felles leser for installasjonen, som testene leser (story 3.5i).

Gruppens svar 07.11 kl. 23:26 og 08.11 kl. 11:24: README-en beholder de fem
stegene for dobbeltklikket, linja om første gang og linja om den ekte
versjonen. Resten av «Kom i gang» står ordrett i docs/installasjon.md, bare
med stiene rettet for mappa docs/. Testene som leste delene i README-en,
leser dem her.
"""

from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
README = ROT / "README.md"
INSTALLASJONEN = ROT / "docs" / "installasjon.md"
# Tittelen under frontmatteren. Alt under den er det som er flyttet.
TITTELEN = "# Installasjonen"


def installasjonen() -> str:
    """Det som er flyttet fra «Kom i gang»: alt under tittelen i
    docs/installasjon.md. Mangler tittelen, feiler testen med en melding,
    ikke med IndexError."""
    tekst = INSTALLASJONEN.read_text(encoding="utf-8")
    deler = tekst.split(f"\n{TITTELEN}\n\n", 1)
    assert len(deler) == 2, f"«{TITTELEN}» mangler i docs/installasjon.md"
    return deler[1]


def readme_og_installasjonen() -> str:
    """README-en og installasjonen etter hverandre, for testene som leste
    hele README-en etter noe som kan stå i begge."""
    return README.read_text(encoding="utf-8") + "\n" + installasjonen()
