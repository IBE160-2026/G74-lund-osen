"""Story 8.0b: hjelpetekstene bak «?».

Hvert kontrollpunkt i storyen har sin test, og hver test er proevd med en
mutant (spesifikasjonen, Verification).
"""

import re
from pathlib import Path

import pytest

from hjelpetekster import Hjelp, hjelpetekster
from markedsoversikt import RETNINGSVISNING
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, STANDARD, Parametre
from tallformat import HARDT_MELLOMROM as NB
from tallformat import tall

ROT = Path(__file__).resolve().parent.parent

# Tallene med dagens parametre, slik de staar i tekstene.
STANDARDTALL = (
    f"mer enn 2{NB}%",
    "de siste 50 børsdagene",
    "de 20 børsdagene før",
    "1,5 ganger",
    "trenger 51 børsdager",
    "styrke 2 eller mer",
)

ANDRE = Parametre(
    ma_vindu=40, noytralsone=0.03, volatilitet_vindu=15, volum_vindu=25,
    volumfaktor=2.5, terskel=3,
)


def _alt(tekster) -> str:
    return "\n".join(f"{t.tittel} {t.tekst}" for t in tekster.values())


class TestTalleneFraParametre:
    def test_dagens_tall_staar_i_tekstene(self):
        alt = _alt(hjelpetekster())
        for tekst in STANDARDTALL:
            assert tekst in alt, tekst

    def test_andre_parametre_gir_andre_tall(self):
        """Kontrollpunktet: tallene hentes fra Parametre. Ville feilet hvis
        50 dager eller 1,5 ganger var skrevet fast i en tekst."""
        alt = _alt(hjelpetekster(ANDRE))
        for tekst in STANDARDTALL:
            assert tekst not in alt, tekst
        for tekst in (
            f"mer enn 3{NB}%",
            f"innenfor 3{NB}%",
            "de siste 40 børsdagene",
            "de 15 børsdagene før",
            "de 25 børsdagene før",
            "2,5 ganger",
            "trenger 41 børsdager",
            "styrke 3 eller mer",
            "vinduene på 15 og 25 børsdager",
            "terskelen 3",
        ):
            assert tekst in alt, tekst

    @pytest.mark.parametrize(
        "verdi, slag",
        [
            (STANDARD.noytralsone * 100, "grense"),
            (STANDARD.volumfaktor, "faktor"),
            (STANDARD.ma_vindu, "heltall"),
            (STANDARD.volatilitet_vindu, "heltall"),
            (STANDARD.volum_vindu, "heltall"),
            (STANDARD.terskel, "heltall"),
        ],
    )
    def test_tallet_som_vises_er_parameteren(self, verdi, slag):
        """Ville feilet hvis en parameter ble rundet av der den vises,
        for eksempel en volumfaktor paa 1,25 vist som «1,3»."""
        vist = tall(verdi, slag).replace(NB, "").removesuffix("%").replace(",", ".")
        assert float(vist) == pytest.approx(verdi, abs=1e-12)


class TestRetningen:
    @pytest.mark.parametrize(
        "noekkel, retning",
        [("positiv", POSITIV), ("negativ", NEGATIV), ("blandet", BLANDET), ("ingen", INGEN)],
    )
    def test_ordet_og_symbolet_er_fr_704_sine(self, noekkel, retning):
        """Kontrollpunktet: retningen forklares med ordene i FR-704, bygget
        av de samme konstantene som tabellen viser."""
        visning = RETNINGSVISNING[retning]
        assert hjelpetekster()[noekkel].tittel == f"{visning.symbol} {visning.tekst}:"

    def test_ikke_opp_og_ned_som_navn(self):
        """FR-103, endret 21.09: «Opp» og «Ned» er fjernet som ord for
        retningen. Som verb i bevegelse («Opp gir +1») er de ikke navn paa
        en retning, saa testen ser paa titlene og ordene i anfoerselstegn."""
        for tekst in hjelpetekster().values():
            assert not re.search(r"\b(Opp|Ned)\b", tekst.tittel, re.IGNORECASE), tekst.tittel
            assert not re.search(r"«(Opp|Ned)»", tekst.tekst, re.IGNORECASE), tekst.tekst

    def test_ingen_og_ukjent_forklares_hver_for_seg(self):
        """Kontrollpunktet: «Ingen» og «Ukjent» forklares hver for seg.
        Ville feilet hvis de to sto som én tekst."""
        tekster = hjelpetekster()
        ingen, ukjent = tekster["ingen"], tekster["ukjent"]
        assert ingen.tittel == "– Ingen:" and ukjent.tittel == "– Ukjent:"
        assert "styrken er 0" in ingen.tekst
        assert "ingen vurdering" in ukjent.tekst
        assert "styrken er 0" not in ukjent.tekst
        assert "ingen vurdering" not in ingen.tekst


# Ord som kan leses som et raad (NFR-06). Bare ikke_raad kan si kjoepe og
# selge, fordi den sier at signalet ikke er et raad.
RAADSORD = (
    r"\bbør\b", r"\banbefal", r"\bkjøp", r"\bselg", r"\blønn", r"\bmulighet",
    r"\btips", r"\bvil stige", r"\bvil falle", r"\bkurspotensial", r"\bgevinst",
)


class TestIkkeRaad:
    def test_ingen_tekst_kan_leses_som_et_raad(self):
        """Ville feilet hvis en tekst sa noe som kan leses som et raad."""
        for noekkel, tekst in hjelpetekster().items():
            if noekkel == "ikke_raad":
                continue
            for ord_ in RAADSORD:
                assert not re.search(ord_, f"{tekst.tittel} {tekst.tekst}", re.IGNORECASE), (noekkel, ord_)

    def test_hjelpen_sier_at_signalet_ikke_er_et_raad(self):
        tekst = hjelpetekster()["ikke_raad"].tekst
        assert "ikke en spådom" in tekst
        assert "ikke et råd om å kjøpe eller selge" in tekst


class TestKildene:
    def test_hver_tekst_har_en_kilde_som_finnes(self):
        """Kontrollpunktet: teksten sier ikke noe som ikke staar i en kilde.
        Hver tekst viser til en fil, og stedet staar ordrett i den. Ville
        feilet hvis en tekst manglet kilde, eller kilden var flyttet."""
        for noekkel, tekst in hjelpetekster().items():
            assert tekst.kilder, noekkel
            for fil, sted in tekst.kilder:
                sti = ROT / fil
                assert sti.is_file(), (noekkel, fil)
                assert sted in sti.read_text(encoding="utf-8"), (noekkel, fil, sted)


class TestHjelp:
    def test_en_ukjent_noekkel_feiler_med_navnet(self):
        with pytest.raises(KeyError, match="'finnes_ikke'"):
            Hjelp(hjelpetekster()).tekst("finnes_ikke")

    def test_en_kjent_noekkel_gir_teksten(self):
        assert Hjelp(hjelpetekster()).tekst("trend") == hjelpetekster()["trend"]
