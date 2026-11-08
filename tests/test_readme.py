"""README-en foelger repoet - regel 19 i CLAUDE.md.

Dokumentlista i README-en sto uendret fra 21.09 til 24.09 mens repoet vokste.
Denne testen fanger den ene feilen som kan sjekkes uten skjoenn: en lenke som
peker paa noe som ikke finnes, fordi en fil er flyttet, har faatt nytt navn
eller er slettet. At lista er fullstendig, maa fortsatt ses paa.

Ingen nettverk: lenker til nettet hoppes over, ikke sjekket.
"""

import re
from pathlib import Path

from dokumentene import INSTALLASJONEN, README, installasjonen

ROT = Path(__file__).resolve().parent.parent

LENKE = re.compile(r"\]\(([^)\s]+)\)")
UTENFOR = ("http://", "https://", "mailto:", "#")


# Story 8.20c (U75, spørsmål 20 i 8.20): med ordene README-en allerede bruker.
KONTO_FRA_FOER = "Har du en konto hos EODHD fra før, logger du inn og kopierer «API token» under «Dashboard»."


def test_readme_sier_hva_man_gjoer_med_en_konto_fra_foer():
    """Ville feilet hvis steg 5 eller avsnittet om nøkkelen ved
    dobbeltklikket bare sa at man lager en gratis bruker (mutanten). Story
    3.5i: begge står i docs/installasjon.md."""
    tekst = installasjonen()
    steg_5 = next(linje for linje in tekst.splitlines() if linje.startswith("5. **Hent en nøkkel.**"))
    noekkelen = next(
        linje for linje in tekst.splitlines() if linje.startswith("Den ekte versjonen spør etter nøkkelen")
    )
    assert KONTO_FRA_FOER in steg_5
    assert KONTO_FRA_FOER in noekkelen


def test_hver_lenke_i_readme_peker_paa_noe_som_finnes():
    tekst = (ROT / "README.md").read_text(encoding="utf-8")

    mangler = [
        maal
        for maal in LENKE.findall(tekst)
        if not maal.startswith(UTENFOR) and not (ROT / maal.split("#", 1)[0]).exists()
    ]

    assert not mangler, f"Lenker i README.md som ikke finnes: {mangler}"


def test_hver_lenke_i_readme_og_installasjonen_gaar_til_en_fil_og_et_anker_som_finnes():
    """Story 3.5i, kontrollpunkt d: hver lenke i README-en og
    docs/installasjon.md går til en fil som finnes, regnet fra mappa lenken
    står i, og et anker i lenken finnes i den fila, eller i samme fil når
    lenken bare er et anker. Ville feilet hvis én lenke pekte på et anker som
    er flyttet, for eksempel #med-docker-desktop i README-en etter flyttingen,
    eller ../README.md#står-du-fast i installasjonen."""
    from test_docker import _ankrene

    sjekket = 0
    for fil in (README, INSTALLASJONEN):
        tekst = fil.read_text(encoding="utf-8")
        for maal in LENKE.findall(tekst):
            if maal.startswith(("http://", "https://", "mailto:")):
                continue
            sti, _, anker = maal.partition("#")
            maalfil = (fil.parent / sti) if sti else fil
            assert maalfil.exists(), (fil.name, maal)
            if anker:
                assert maalfil.suffix == ".md", (fil.name, maal)
                assert anker in _ankrene(maalfil.read_text(encoding="utf-8")), (fil.name, maal)
                sjekket += 1
    # Lenker til ankre i begge retninger, så testen ikke går tom (27 da den
    # ble skrevet).
    assert "](docs/installasjon.md#med-docker-desktop)" in README.read_text(encoding="utf-8")
    assert "](../README.md#tester)" in installasjonen()
    assert sjekket >= 20, sjekket
