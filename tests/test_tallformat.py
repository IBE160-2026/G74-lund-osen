"""Tall slik sidene viser dem - story 8.0, regel 21.

Desimalkomma, hardt mellomrom som tusenskille og foran %, bindestrek som
minus, og aldri «-0,00». Desimalene per slag bestemmes i tallformat.py, ikke i
malene.
"""

import ast
from pathlib import Path

import pytest

from tallformat import HARDT_MELLOMROM as NB
from tallformat import desimaler_mot_grense, tall


class TestTall:
    def test_negativt(self):
        assert tall(-1.5, "kurs") == "-1,50"

    def test_null(self):
        assert tall(0, "kurs") == "0,00"

    def test_rundes_til_null_faar_ikke_minus(self):
        assert tall(-0.004, "kurs") == "0,00"

    def test_endring_som_rundes_til_null_faar_ikke_pluss(self):
        assert tall(0.004, "endring") == f"0,00{NB}%"
        assert tall(-0.004, "endring") == f"0,00{NB}%"

    def test_over_tusen_har_hardt_mellomrom(self):
        assert tall(1234.5, "kurs") == f"1{NB}234,50"

    def test_volum_har_ingen_desimaler(self):
        assert tall(1234567, "volum") == f"1{NB}234{NB}567"

    def test_endring_har_fortegn_to_desimaler_og_prosent(self):
        assert tall(1.234, "endring") == f"+1,23{NB}%"
        assert tall(-1.236, "endring") == f"-1,24{NB}%"

    def test_minus_er_vanlig_bindestrek(self):
        assert tall(-2.0, "endring")[0] == "-"

    def test_maaling_har_minst_en_desimal(self):
        assert tall(2.04, "maaling") == f"+2,0{NB}%"

    def test_fortegn_kan_slaas_av(self):
        """Et standardavvik har ingen retning og vises uten +."""
        assert tall(1.2, "maaling", fortegn=False) == f"1,2{NB}%"

    def test_desimaler_kan_overstyres(self):
        assert tall(1.2346, "maaling", desimaler=3) == f"+1,235{NB}%"

    def test_akse_har_ingen_desimaler(self):
        assert tall(1234.4, "akse") == f"1{NB}234"

    def test_forhold_har_to_desimaler_uten_fortegn_og_uten_prosent(self):
        """Story 2.1c: volumet som forholdstall mot medianen."""
        assert tall(4.954, "forhold") == "4,95"
        assert tall(1.5, "forhold") == "1,50"
        assert tall(0, "forhold") == "0,00"

    def test_forhold_med_flere_desimaler_og_tusenskille(self):
        assert tall(1.5004, "forhold", desimaler_mot_grense(1.5004, 1.5, minst=2)) == "1,5004"
        assert tall(1234.5, "forhold") == f"1{NB}234,50"

    def test_ukjent_slag_avvises(self):
        with pytest.raises(ValueError, match="Ukjent slag"):
            tall(1.0, "pris")

    def test_ingen_vanlig_mellomrom_og_intet_punktum(self):
        for tekst in (tall(1234567.891, "kurs"), tall(-1234.5, "endring")):
            assert " " not in tekst
            assert "." not in tekst


class TestDesimalerMotGrense:
    """Story 8.0: en maaling som blir lik grensen etter avrunding uten aa vaere
    det, vises med saa mange desimaler at forskjellen synes."""

    def test_vanlig_avstand_gir_en_desimal(self):
        assert desimaler_mot_grense(-3.4, 1.2) == 1

    def test_maaling_som_rundes_til_grensen_faar_flere(self):
        """Ville feilet hvis «-1,2 % mot 1,2 % standardavvik» sto ved en
        sjekk som ga -1."""
        antall = desimaler_mot_grense(-1.214, 1.212)
        assert antall == 3
        assert tall(-1.214, "maaling", antall) == f"-1,214{NB}%"
        assert tall(1.212, "maaling", antall, fortegn=False) == f"1,212{NB}%"

    def test_trend_like_over_noytralsonen(self):
        assert desimaler_mot_grense(2.004, 2.0) == 3

    def test_noeyaktig_lik_grensen_gir_minst(self):
        assert desimaler_mot_grense(2.0, 2.0) == 1
        assert desimaler_mot_grense(-2.0, 2.0) == 1

    def test_flyttallsstoey_gir_minst(self):
        """Like med seks desimaler: forskjellen er stoey, ikke en maaling."""
        assert desimaler_mot_grense(2.0 + 1e-12, 2.0) == 1

    def test_minst_kan_hoeynes(self):
        assert desimaler_mot_grense(-3.4, 1.2, minst=2) == 2


def test_tallformat_er_en_loevnode():
    """Spinen: tallformat.py importerer ingenting, saa kjernen og app.py kan
    bruke den uten aa trekke med seg noe annet."""
    kilde = Path(__file__).resolve().parent.parent / "src" / "tallformat.py"
    tre = ast.parse(kilde.read_text(encoding="utf-8"))
    assert not [
        node for node in ast.walk(tre) if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
