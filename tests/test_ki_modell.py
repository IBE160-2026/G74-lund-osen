"""Story 10.2a: porten Modell, prompten og kontrollen i FR-603 - AD-2, AD-8.

Alt med en falsk modell. Ingen test kaller en ekte tjeneste, og nettsperren
i conftest.py stopper en som proever (story 4.0).
"""

import json
from datetime import date

import pytest

from ki_kontroll import AARSAKER, GJETNING, RAAD, kontroller
from ki_modell import Modell, ModellFeilet, Modellsvar, lag_ki_rad
from ki_prompt import PROMPTVERSJON, lag_prompt
from kilogg import Emne

EMNE = Emne.aksje("EQNR", date(2026, 10, 15))
BLANDET = {"trend": 1, "bevegelse": 0, "interesse": -1, "styrke": 2, "retning": "Blandet"}
INGEN = {"trend": 0, "bevegelse": 0, "interesse": 0, "styrke": 0, "retning": "Ingen"}
REGELEN = "Trenden ga +1 og interessen -1."
GOD_TEKST = ("Kursen ligger over snittet for de siste 50 dagene, men det ble handlet mye på en dag "
             "kursen falt. To av de tre sjekkene ga utslag, i hver sin retning, så retningen er blandet.")


class FalskModell:
    """En modell som svarer det testen sier, og husker prompten (AD-8)."""

    tjeneste = "lokal"
    modell = "gemma4:e4b"

    def __init__(self, tekst: str | None = GOD_TEKST, feil: Exception | None = None):
        self.tekst = tekst
        self.feil = feil
        self.prompter: list[str] = []

    def lag_tekst(self, prompt: str) -> Modellsvar:
        self.prompter.append(prompt)
        if self.feil is not None:
            raise self.feil
        return Modellsvar(tekst=self.tekst, modell="gemma4:e4b", modell_id="dc35e8d9c606", seed=42,
                          temperatur=0.0, maskinvare="gpu", ollama_versjon="0.35.1")


class TestPorten:
    def test_den_falske_modellen_oppfyller_porten(self):
        assert isinstance(FalskModell(), Modell)

    def test_bare_lag_tekst(self):
        offentlige = {n for n in vars(Modell) if not n.startswith("_")}
        assert offentlige == {"lag_tekst"}


class TestPrompten:
    def test_bare_grunnlaget_kommer_med(self):
        prompt = lag_prompt(BLANDET)
        opplysningene = json.loads(prompt.split("Opplysningene:\n", 1)[1])
        assert opplysningene == BLANDET

    def test_interessen_foelger_kursendringen(self):
        """Laerdommen fra C-med i malinger.md §19."""
        assert "Fortegnet for interessen følger dagens kursendring, ikke volumet" in lag_prompt(BLANDET)

    def test_ingen_raad_og_ingen_gjetning(self):
        prompt = lag_prompt(BLANDET)
        assert "Ikke gi råd" in prompt and "Ikke gjett" in prompt

    def test_merket_utenfor_maalingen(self):
        assert "utenfor de 15" in lag_prompt({**BLANDET, "merke": "Utenfor målingen"})
        assert "utenfor de 15" not in lag_prompt(BLANDET)

    def test_promptversjonen_finnes(self):
        assert PROMPTVERSJON


class TestKontrollen:
    def test_en_god_tekst_bestaar(self):
        svar = kontroller(GOD_TEKST, BLANDET)
        assert svar.besto, svar.grunner
        assert svar.grunn is None

    def test_regelen_selv_kan_forklares(self):
        """FR-603 punkt 4: «fordi ingen sjekk ga utslag» er lov."""
        assert kontroller("Retningen er ingen, fordi ingen sjekk ga utslag.", INGEN).besto

    @pytest.mark.parametrize("tekst", [
        "Retningen er positiv.", "Det er en negativ retning.", "Retningen er altså ingen.",
    ])
    def test_1_feil_retning(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and svar.grunner[0].startswith("1:")

    @pytest.mark.parametrize("tekst", [
        "Styrken er tre.", "Signalstyrken er 1.", "Ingen av de tre sjekkene ga utslag.",
        "Én av tre sjekker slo ut.",
    ])
    def test_1_feil_styrke(self, tekst):
        """Ogsaa «ingen av de tre sjekk» naar styrken er 2 (§19, E-med)."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner)

    def test_positiv_og_negativ_som_ord_i_blandet(self):
        """FR-603 punkt 1: ordene alene er ikke et utsagn om retningen."""
        tekst = "Trenden er positiv, mens interessen er negativ. Retningen er blandet."
        assert kontroller(tekst, BLANDET).besto

    @pytest.mark.parametrize("tekst", [
        "Kursen steg 2,4 prosent.", "Kursen steg 3 %.", "Snittet for de siste 30 dagene.",
        "Femdagssnittet ligger lavere.", "Seks av de femti aksjene.", "Snittet over sytti dager.",
        "Volumet var 1.5 ganger normalt.",
    ])
    def test_2_tall_som_ikke_er_i_grunnlaget(self, tekst):
        """Ogsaa tall skrevet med ord (§19: «femdagssnittet», «seks av de femti»)."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("2:") for g in svar.grunner)

    @pytest.mark.parametrize("tekst", [
        "Snittet for de siste 50 dagene.", "MA50 ligger under kursen.", "Vinduet er 20 dager.",
        "To av de tre sjekkene ga utslag.", "Femti dager er grunnlaget for trenden.",
    ])
    def test_2_regelens_faste_tall_og_styrken_er_lov(self, tekst):
        assert kontroller(tekst, BLANDET).besto, kontroller(tekst, BLANDET).grunner

    @pytest.mark.parametrize("ord_", ["trend", "tid", "nivået", "totalt", "trenden"])
    def test_2_ord_som_begynner_som_et_tallord(self, ord_):
        assert kontroller(f"Det gjelder {ord_}.", BLANDET).besto

    @pytest.mark.parametrize("tekst", [
        "Du kan kjøpe aksjen.", "Det kan være lurt å selge.", "Vi anbefaler å vente.",
        "Investorer bør følge med.", "Dette er ikke investeringsråd.", "Snakk med en rådgiver.",
        "Et alternativ for investorer.", "Et godt investeringsalternativ.", "Et kjøpssignal.",
        "Et salgssignal.", "Kursmålet er nådd.",
    ])
    def test_3_raad(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("3:") for g in svar.grunner)

    @pytest.mark.parametrize("moenster", RAAD)
    def test_3_hvert_ord_i_lista_stopper(self, moenster):
        ord_ = {"bør\\b": "bør", "råd\\b": "råd", "investerings\\w*": "investeringsråd"}.get(moenster, moenster)
        assert not kontroller(f"Her står {ord_} i teksten.", BLANDET).besto

    @pytest.mark.parametrize("moenster", GJETNING + AARSAKER)
    def test_4_hvert_ord_i_lista_stopper(self, moenster):
        ord_ = moenster.replace("(?:dag|uke|måned)", "uke")
        svar = kontroller(f"Her står {ord_} i teksten.", BLANDET)
        assert not svar.besto and any(g.startswith("4:") for g in svar.grunner)

    @pytest.mark.parametrize("tekst", [
        "Kursen steg trolig på grunn av nyheter.", "Det skyldes en ny kontrakt.",
        "Det kan tyde på mer oppgang.", "Kursen vil fortsette opp.",
    ])
    def test_4_gjetning_og_aarsaker(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("4:") for g in svar.grunner)

    @pytest.mark.parametrize("ord_", ["børsdagen", "resultatet av sjekkene", "orientering", "rådata"])
    def test_4_ord_som_ikke_er_paa_lista(self, ord_):
        """«resultat» er ikke paa lista (FR-603), og «bør» stopper ikke «børs»."""
        assert kontroller(f"Det gjelder {ord_}.", BLANDET).besto

    def test_alle_grunnene_kommer_med(self):
        svar = kontroller("Retningen er positiv. Kjøp nå, kursen steg 3 %, trolig.", BLANDET)
        assert {g[0] for g in svar.grunner} == {"1", "2", "3", "4"}
        assert svar.grunn == "; ".join(svar.grunner)


class TestRaden:
    def test_en_tekst_som_bestaar(self):
        modell = FalskModell()
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, modell)
        assert rad.besto and rad.tekst == GOD_TEKST and rad.grunn is None
        assert rad.promptversjon == PROMPTVERSJON
        assert (rad.tjeneste, rad.modell, rad.modell_id, rad.seed, rad.temperatur, rad.maskinvare,
                rad.ollama_versjon) == ("lokal", "gemma4:e4b", "dc35e8d9c606", 42, 0.0, "gpu", "0.35.1")
        assert rad.grunnlag == BLANDET and rad.regelen == REGELEN
        assert modell.prompter == [lag_prompt(BLANDET)]

    @pytest.mark.parametrize("tekst, punkt", [
        ("Retningen er positiv.", "1"), ("Kursen steg 2,4 prosent.", "2"),
        ("Du bør kjøpe aksjen.", "3"), ("Det skyldes trolig nyheter.", "4"),
    ])
    def test_hvert_punkt_stopper_en_tekst(self, tekst, punkt):
        """Story 10.2: en test med falsk modell viser at hvert av de fire
        punktene stopper en tekst. Teksten logges med grunnen og vises ikke."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(tekst))
        assert not rad.besto and rad.tekst == tekst
        assert rad.grunn.startswith(punkt + ":")
        assert not rad.modellen_feilet

    @pytest.mark.parametrize("feil", [ModellFeilet("tidsavbrudd etter 60 s"), ModellFeilet()])
    def test_modellen_feilet_gir_en_rad_uten_tekst(self, feil):
        """NFR-04, FR-604: ingenting reises videre, og raden sier hvorfor."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(feil=feil))
        assert rad.modellen_feilet and not rad.besto
        assert rad.grunn.startswith("modellen feilet")
        assert (rad.tjeneste, rad.modell, rad.promptversjon) == ("lokal", "gemma4:e4b", PROMPTVERSJON)

    @pytest.mark.parametrize("tekst", ["", "   "])
    def test_en_tom_tekst_er_at_modellen_feilet(self, tekst):
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(tekst))
        assert rad.modellen_feilet and rad.grunn == "modellen feilet: tom tekst"

    def test_en_annen_feil_reises(self):
        """Bare ModellFeilet blir en rad. En feil i koden vaar skal synes."""
        with pytest.raises(ZeroDivisionError):
            lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(feil=ZeroDivisionError()))
