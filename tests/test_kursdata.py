"""Tester for datalaget. Ingen nettverk, ingen API-kall.

Filtestene skriver til tmp_path, ikke til data/.
"""

import json

import pytest

from kursdata import (
    AKSJEUNIVERS,
    MinneKilde,
    SnapshotKilde,
    nyeste_snapshot,
)


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


def test_minnekilde_gir_serien_den_fikk():
    rader = [{"date": "2026-09-18", "close": 10.0}]
    kilde = MinneKilde(serier={"EQNR": rader}, hentet="2026-09-21")

    assert kilde.serie("EQNR") == rader
    assert kilde.tidsstempel() == "2026-09-21"


def test_minnekilde_gir_tom_liste_for_ukjent_symbol():
    """Et symbol vi mangler skal ikke kaste - visningen maa kunne vise resten."""
    kilde = MinneKilde(serier={})
    assert kilde.serie("FINNESIKKE") == []


def test_snapshotkilde_leser_formatet_signaltesten_skrev(tmp_path):
    fil = tmp_path / "signaltest-raa-2026-09-21.json"
    fil.write_text(
        json.dumps(
            {
                "hentet": "2026-09-21T15:40:00+00:00",
                "serier": {"DNB": [{"date": "2026-09-18", "close": 250.0}]},
            }
        ),
        encoding="utf-8",
    )

    kilde = SnapshotKilde.fra_fil(fil)

    assert kilde.tidsstempel() == "2026-09-21T15:40:00+00:00"
    assert kilde.serie("DNB")[0]["close"] == 250.0
    assert kilde.serie("MANGLER") == []


def test_snapshotkilde_taaler_fil_uten_serier(tmp_path):
    fil = tmp_path / "tom.json"
    fil.write_text(json.dumps({"hentet": "2026-09-21"}), encoding="utf-8")

    kilde = SnapshotKilde.fra_fil(fil)
    assert kilde.serie("EQNR") == []


def test_nyeste_snapshot_velger_siste_dato(tmp_path):
    for navn in ("signaltest-raa-2026-09-19.json", "signaltest-raa-2026-09-21.json"):
        (tmp_path / navn).write_text("{}", encoding="utf-8")
    (tmp_path / "noe-annet.json").write_text("{}", encoding="utf-8")

    assert nyeste_snapshot(tmp_path).name == "signaltest-raa-2026-09-21.json"


def test_nyeste_snapshot_er_none_naar_katalogen_er_tom(tmp_path):
    assert nyeste_snapshot(tmp_path) is None


@pytest.mark.parametrize("aksje", AKSJEUNIVERS, ids=lambda a: a.symbol)
def test_hver_aksje_har_navn_og_sektor(aksje):
    assert aksje.navn.strip()
    assert aksje.sektor.strip()
