"""Tester for portmodulen kursdata. Ingen nettverk, ingen API-kall.

Filtestene flyttet til test_lagring_fil.py i story 1.5, sammen med det de
tester.
"""

import pytest

from kursdata import AKSJEUNIVERS


def test_universet_har_femten_aksjer():
    assert len(AKSJEUNIVERS) == 15


def test_universet_dekker_minst_atte_sektorer():
    """Kriteriet fra PRD-en, kontrollert i kode i stedet for i en tabell."""
    sektorer = {aksje.sektor for aksje in AKSJEUNIVERS}
    assert len(sektorer) >= 8


def test_symbol_og_ticker_holdes_fra_hverandre():
    """issuerSign-formen og EODHD-formen er ikke den samme strengen."""
    for aksje in AKSJEUNIVERS:
        assert aksje.ticker == f"{aksje.symbol}.OL"
        assert not aksje.symbol.endswith(".OL")


def test_symbolene_er_unike():
    symboler = [aksje.symbol for aksje in AKSJEUNIVERS]
    assert len(set(symboler)) == len(symboler)


@pytest.mark.parametrize("aksje", AKSJEUNIVERS, ids=lambda a: a.symbol)
def test_hver_aksje_har_navn_og_sektor(aksje):
    assert aksje.navn.strip()
    assert aksje.sektor.strip()
