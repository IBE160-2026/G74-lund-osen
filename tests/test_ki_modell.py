"""Story 10.2a: porten Modell, prompten og kontrollen i FR-603 - AD-2, AD-8.

Alt med en falsk modell. Ingen test kaller en ekte tjeneste, og nettsperren
i conftest.py stopper en som proever (story 4.0).
"""

import hashlib
import inspect
import json
import re
from datetime import date
from pathlib import Path

import pytest

from ki_kontroll import AARSAKER, GJETNING, RAAD, kontroller
from ki_modell import Modell, ModellFeilet, Modellsvar, lag_ki_rad
from ki_prompt import ORDLYDEN, PROMPTVERSJON, REGLER, UTENFOR, lag_prompt, ordlyd_for_dagene
from kilogg import Emne

EMNE = Emne.aksje("EQNR", date(2026, 10, 15))
BLANDET = {"trend": 1, "bevegelse": 0, "interesse": -1, "styrke": 2, "retning": "Blandet"}
INGEN = {"trend": 0, "bevegelse": 0, "interesse": 0, "styrke": 0, "retning": "Ingen"}
EN_POSITIV = {"trend": 1, "bevegelse": 0, "interesse": 0, "styrke": 1, "retning": "Positiv"}
TRE_POSITIVE = {"trend": 1, "bevegelse": 1, "interesse": 1, "styrke": 3, "retning": "Positiv"}
REGELEN = "Trenden ga +1 og interessen -1."
GOD_TEKST = (
    "Kursen ligger over snittet for de siste 50 dagene, men det ble handlet mye på en dag "
    "kursen falt. To av de tre sjekkene ga utslag, i hver sin retning, så retningen er blandet."
)

# sha256 av promptteksten for hver versjon (FR-605). Endres teksten, maa
# PROMPTVERSJON opp og en ny linje inn her. Teksten til versjon 1 finnes bare
# i historikken, i src/ki_prompt.py paa 77ebf31 (gjennomgangen av 10.2c, ECH, BH9).
AVTRYKK = {
    "1": "8fa4608965a356110f97963f65ba85bb44c79e913d47b5b911dc06b51af7be72",
    "2": "4c697052292bf7069ed7ba0cb7600a8c67574c969fd4fcd184f4b854876df660",
    # Story 10.2e. Teksten til versjon 2 staar i src/ki_prompt.py paa 153aba8.
    # Versjon 3 ble rettet foer den ble flettet (gruppens svar 24.10 kl. 21:49),
    # og avtrykket ble satt paa nytt. Den foerste teksten staar paa c848ea6.
    # Gruppens svar 24.10 kl. 23:23: ferdig ordlyd for dagene, og avtrykket er
    # satt paa nytt med ORDLYDEN. Teksten fra kl. 21:49 staar paa 3252ecd.
    # Gjennomgangen 25.10 (VG2): avtrykket dekker ogsaa ordlyd_for_dagene og
    # lag_prompt (_promptteksten). Var c777d549....
    "3": "bc9abc8cf55198934eead877a130b958ae50b8ee831bb880ff1ffb86de740959",
}


def _promptteksten() -> str:
    """Det avtrykket for versjon 3 dekker: reglene, merket, ordlyden og koden
    i ordlyd_for_dagene og lag_prompt (inspect leser kildeteksten med LF)."""
    return REGLER + UTENFOR + "".join(ORDLYDEN) + inspect.getsource(ordlyd_for_dagene) + inspect.getsource(lag_prompt)


class FalskModell:
    """En modell som svarer det testen sier, og husker prompten (AD-8)."""

    tjeneste = "lokal"
    modell = "gemma4:e4b"

    def __init__(self, tekst: str | None = GOD_TEKST, feil: Exception | None = None, svar=None, **kjoering):
        self.tekst = tekst
        self.feil = feil
        self.svar = svar
        self.kjoering = dict(
            modell="gemma4:e4b",
            modell_id="dc35e8d9c606",
            seed=42,
            temperatur=0.0,
            maskinvare="gpu",
            ollama_versjon="0.35.1",
        )
        self.kjoering.update(kjoering)
        self.prompter: list[str] = []

    def lag_tekst(self, prompt: str) -> Modellsvar:
        self.prompter.append(prompt)
        if self.feil is not None:
            raise self.feil
        if self.svar is not None:
            return self.svar
        return Modellsvar(tekst=self.tekst, **self.kjoering)


class TestPorten:
    def test_den_falske_modellen_oppfyller_porten(self):
        assert isinstance(FalskModell(), Modell)

    def test_lag_tekst_tjeneste_og_modell(self):
        """Gjennomgangen (BH17): metoden og de to feltene."""
        assert {n for n in vars(Modell) if not n.startswith("_")} == {"lag_tekst"}
        assert Modell.__annotations__ == {"tjeneste": str, "modell": str}


class TestPrompten:
    def test_bare_grunnlaget_kommer_med(self):
        prompt = lag_prompt(BLANDET)
        opplysningene = json.loads(prompt.split("Opplysningene:\n", 1)[1])
        assert opplysningene == BLANDET

    def test_interessen_foelger_kursendringen(self):
        """Laerdommen fra C-med i malinger.md §19."""
        assert "Fortegnet for interessen følger dagens kursendring, ikke volumet" in lag_prompt(BLANDET)

    def test_regelen_forklares_med_fordi(self):
        """Versjon 2 (gruppen 16.10 kl. 22:33): i proevekjoeringen stoppet
        punkt 4 i kontrollen 9 av 15 tekster, paa «skyldes» og «indikerer»
        (malinger.md §32). Prompten ber om «fordi» i stedet. Ville feilet hvis
        linja ble tatt ut, eller kom utenfor reglene for teksten."""
        # Ikke et fast versjonsnummer: en versjon 3 kan beholde linja
        # (gjennomgangen av 10.2c, BH6, ECH, VG4).
        assert int(PROMPTVERSJON) >= 2
        linje = "- Når du forklarer regelen, bruk «fordi». Ikke bruk «skyldes» eller «indikerer»."
        assert "Regler for teksten:" in REGLER
        blokk = REGLER.split("Regler for teksten:", 1)[1].split("\n\n", 1)[0]
        assert linje in blokk.splitlines()
        assert linje in lag_prompt(BLANDET)
        assert linje in lag_prompt({**BLANDET, "merke": "Utenfor målingen"})

    def test_avtrykket_for_versjon_1_staar(self):
        """Radene med promptversjon 1 skal kunne spores til teksten (FR-605).
        Ville feilet hvis versjon 1 ble ryddet bort fra AVTRYKK (gjennomgangen
        av 10.2c, VG1)."""
        assert {"1", "2"} <= AVTRYKK.keys()
        assert AVTRYKK["1"] == "8fa4608965a356110f97963f65ba85bb44c79e913d47b5b911dc06b51af7be72"

    def test_avtrykket_for_versjon_2_staar(self):
        """Story 10.2e: radene fra uka med logget drift (19.-23.10) har
        versjon 2. Ville feilet hvis avtrykket ble ryddet bort eller endret."""
        assert AVTRYKK["2"] == "4c697052292bf7069ed7ba0cb7600a8c67574c969fd4fcd184f4b854876df660"

    def test_versjon_3(self):
        """Story 10.2e, gruppens svar 24.10 kl. 15:50."""
        assert PROMPTVERSJON == "3"

    def test_reglene_forklarer_hvert_felt_i_grunnlaget(self):
        """Story 10.2e: ville feilet hvis grunnlaget hadde et felt reglene
        ikke forklarer med ord, slik at modellen maatte gjette hva det er."""
        from ki_grunnlag import Dagsbilde, ki_grunnlag
        from vurderingsdata import Vurdering

        vurdering = Vurdering(
            styrke=2,
            retning="Blandet",
            trend=1,
            bevegelse=0,
            interesse=-1,
            slutt=101.37,
            justert_slutt=101.37,
            trend_avvik=0.0123,
            dagens_endring=-0.0217,
            standardavvik=0.0071,
            volumforhold=1.73,
        )
        dagen = Dagsbilde(
            dager=3, dager_minst=True, hovedindeksen="falt", aksjer_steg=4, aksjer_falt=11, bransjen="steg"
        )
        grunnlag = ki_grunnlag(vurdering, utenfor_maalingen=True, dagen=dagen)
        forklaringen = REGLER.split("Regler for teksten:")[0]
        for felt in grunnlag:
            if felt != "merke":
                assert felt in forklaringen, felt
        # Gruppens svar 24.10 kl. 23:23: «minst» staar bare i ordlyden.
        assert "Ordlyden for dagene: i minst 3 børsdager\n" in lag_prompt(grunnlag)
        assert UTENFOR in lag_prompt(grunnlag)

    def test_teksten_kan_vise_til_tallene_paa_siden(self):
        """Story 10.2e, svaret 21.10 kl. 23:51: teksten kan vise til tallene
        paa siden uten aa gjenta dem. Ville feilet hvis regelen ble tatt ut,
        eller kom utenfor reglene for teksten."""
        blokk = REGLER.split("Regler for teksten:", 1)[1].split("\n\n", 1)[0]
        assert any("vise til" in linje and "ikke gjenta tallene" in linje for linje in blokk.splitlines())
        assert any("antallene i opplysningene" in linje for linje in blokk.splitlines())

    def test_en_sjekk_med_navnet_og_ingen_sjekk_bare_ved_styrke_0(self):
        """Gruppens svar 24.10 kl. 21:49 (malinger.md §43): ville feilet hvis
        reglene ikke ba om navnet paa sjekken, eller lot «ingen sjekk» staa om
        én sjekk, eller ikke ba om aa beskrive hver sjekk slik fortegnet er."""
        blokk = REGLER.split("Regler for teksten:", 1)[1].split("\n\n", 1)[0].splitlines()
        assert any("én sjekk" in linje and "«interessen ga ikke utslag»" in linje for linje in blokk)
        assert any("«ingen sjekk» bare når styrken er 0" in linje for linje in blokk)
        assert any("Beskriv hver sjekk slik fortegnet står" in linje for linje in blokk)
        assert "for eksempel at ingen sjekk ga utslag" not in REGLER

    def test_dagene_bare_med_ordlyden(self):
        """Gruppens svar 24.10 kl. 23:23 (malinger.md §44): tre tekster sa
        «minst» uten merket og én «det tredje på rad». Erstatter testen fra
        kl. 21:49 om «minst» med merket. Ville feilet hvis reglene ikke ba om
        ordlyden, ordrett, eller hvis «minst» sto i reglene."""
        linje = next(linje for linje in REGLER.splitlines() if linje.startswith("- dager:"))
        assert "bare med ordlyden for dagene" in linje and "ordrett" in linje
        assert "aldri dagene med egne ord" in linje
        assert "minst" not in (REGLER + UTENFOR).lower()

    def test_ingen_raad_og_ingen_gjetning(self):
        prompt = lag_prompt(BLANDET)
        assert "Ikke gi råd" in prompt and "Ikke gjett" in prompt

    def test_merket_utenfor_maalingen(self):
        assert UTENFOR in lag_prompt({**BLANDET, "merke": "Utenfor målingen"})
        assert UTENFOR not in lag_prompt(BLANDET)

    def test_versjonen_foelger_teksten(self):
        """Gjennomgangen (BH13): en endret prompt maa faa ny versjon (FR-605).
        Gruppens svar 24.10 kl. 23:23: ordlyden for dagene er med, og
        gjennomgangen 25.10 (VG2, BH7): ogsaa koden som velger ordlyden og
        setter prompten sammen, saa en endret logikk ogsaa gir ny versjon."""
        avtrykk = hashlib.sha256(_promptteksten().encode("utf-8")).hexdigest()
        assert AVTRYKK.get(PROMPTVERSJON) == avtrykk, (
            "Promptteksten er endret. Sett ny PROMPTVERSJON og legg avtrykket i AVTRYKK."
        )

    def test_prompten_har_ingen_tall_kontrollen_stopper(self):
        """Gjennomgangen (BH1, BH2): gjentar modellen prompten, skal den ikke
        stoppes av punkt 2."""
        for styrke, retning in ((0, "Ingen"), (1, "Positiv"), (2, "Blandet"), (3, "Positiv")):
            grunnlag = {**BLANDET, "styrke": styrke, "retning": retning}
            del_av_prompten = REGLER.split("Regler for teksten:")[0].replace(
                "I opplysningene under står 1 for positivt utslag, -1 for negativt og 0 for ikke noe utslag.", ""
            )
            assert not [g for g in kontroller(del_av_prompten, grunnlag).grunner if g.startswith("2:")]
            assert kontroller(UTENFOR, grunnlag).besto


class TestKontrollen:
    def test_en_god_tekst_bestaar(self):
        svar = kontroller(GOD_TEKST, BLANDET)
        assert svar.besto, svar.grunner
        assert svar.grunn is None

    def test_en_forklaring_med_fordi_bestaar(self):
        """Versjon 2 ber om «fordi»: en forklaring av regelen med «fordi»
        bestaar når sjekkene ga utslag (gjennomgangen av 10.2c, VG3)."""
        assert kontroller(
            "Retningen er blandet fordi to av de tre sjekkene ga utslag, i hver sin retning.", BLANDET
        ).besto

    def test_regelen_selv_kan_forklares(self):
        """FR-603 punkt 4: «fordi ingen sjekk ga utslag» er lov naar ingen ga det."""
        assert kontroller("Retningen er ingen, fordi ingen sjekk ga utslag.", INGEN).besto

    def test_fordi_ingen_sjekk_naar_noen_ga_utslag(self):
        """Gjennomgangen (BH7): da er det et feil utsagn om styrken."""
        svar = kontroller("Retningen er blandet fordi ingen sjekk ga utslag.", BLANDET)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner)

    @pytest.mark.parametrize(
        "tekst",
        [
            "Retningen er positiv.",
            "Det er en negativ retning.",
            "Retningen er altså ingen.",
            "Det er ingen retning.",
            "Retningen er ikke blandet.",
        ],
    )
    def test_1_feil_retning(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and svar.grunner[0].startswith("1:")

    @pytest.mark.parametrize(
        "tekst",
        [
            "Trendens retning er positiv.",
            "Retningen er ikke positiv.",
            "Retningen er dermed blandet.",
        ],
    )
    def test_1_retning_som_er_riktig_eller_gjelder_en_sjekk(self, tekst):
        assert kontroller(tekst, BLANDET).besto, kontroller(tekst, BLANDET).grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Styrken er tre.",
            "Signalstyrken er 1.",
            "Ingen av de tre sjekkene ga utslag.",
            "Én av tre sjekker slo ut.",
            "En av de tre sjekkene ga utslag.",
            "Alle tre sjekkene ga utslag.",
            "Styrken på signalet er tre.",
            "Styrken er altså tre.",
            "3 av 3 sjekker ga utslag.",
        ],
    )
    def test_1_feil_styrke(self, tekst):
        """Ogsaa «ingen av de tre sjekk» naar styrken er 2 (§19, E-med)."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner)

    @pytest.mark.parametrize(
        "grunnlag, tekst",
        [
            (EN_POSITIV, "To sjekker ga utslag."),
            (EN_POSITIV, "To av de tre sjekkene ga utslag."),
            (TRE_POSITIVE, "To av de tre sjekkene ga utslag."),
            (INGEN, "Én sjekk ga utslag."),
        ],
    )
    def test_1_feil_styrke_ved_andre_styrker(self, grunnlag, tekst):
        """Gjennomgangen (BH18): ikke bare styrke 2."""
        assert not kontroller(tekst, grunnlag).besto

    @pytest.mark.parametrize(
        "grunnlag, tekst",
        [
            (EN_POSITIV, "Én av de tre sjekkene ga utslag, så retningen er positiv."),
            (TRE_POSITIVE, "Alle tre sjekkene ga utslag, og retningen er positiv."),
            (INGEN, "Ingen av de tre sjekkene ga utslag."),
        ],
    )
    def test_1_riktig_styrke_bestaar(self, grunnlag, tekst):
        assert kontroller(tekst, grunnlag).besto, kontroller(tekst, grunnlag).grunner

    def test_positiv_og_negativ_som_ord_i_blandet(self):
        """FR-603 punkt 1: ordene alene er ikke et utsagn om retningen."""
        tekst = "Trenden er positiv, mens interessen er negativ. Retningen er blandet."
        assert kontroller(tekst, BLANDET).besto

    @pytest.mark.parametrize(
        "tekst",
        [
            "Kursen steg 2,4 prosent.",
            "Kursen steg 3 %.",
            "Snittet for de siste 30 dagene.",
            "Femdagssnittet ligger lavere.",
            "Seks av de femti aksjene.",
            "Snittet over sytti dager.",
            "Volumet var 1.5 ganger normalt.",
            "Kursen steg to prosent.",
            "Kursen steg 3 prosent.",
            "Aksjen kostet 50 kroner.",
            "Handelen var dobbelt så stor.",
            "Femtifem dager.",
            "Det tiårige snittet.",
            "For tredje dag på rad.",
            "Over tiårsperioden.",
        ],
    )
    def test_2_tall_og_mengder_som_ikke_er_i_grunnlaget(self, tekst):
        """Ogsaa tall skrevet med ord (§19: «femdagssnittet», «seks av de femti»)."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("2:") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Snittet for de siste 50 dagene.",
            "MA50 ligger under kursen.",
            "Vinduet er 20 dager.",
            "To av de tre sjekkene ga utslag.",
            "Femti dager er grunnlaget for trenden.",
            "Dette gjelder én aksje.",
            "Grensene er ikke målt på denne aksjen.",
        ],
    )
    def test_2_regelens_faste_tall_og_styrken_er_lov(self, tekst):
        assert kontroller(tekst, BLANDET).besto, kontroller(tekst, BLANDET).grunner

    @pytest.mark.parametrize("ord_", ["trend", "tid", "nivået", "totalt", "trenden"])
    def test_2_ord_som_begynner_som_et_tallord(self, ord_):
        assert kontroller(f"Det gjelder {ord_}.", BLANDET).besto

    @pytest.mark.parametrize("tekst", ["Styrken er ².", "Kursen er " + "9" * 5000 + "."])
    def test_2_rare_tall_gir_en_grunn_ikke_en_feil(self, tekst):
        """Gjennomgangen (ECH): «²» og et svaert langt tall reiste ValueError."""
        assert not kontroller(tekst, BLANDET).besto or "²" in tekst

    @pytest.mark.parametrize(
        "tekst",
        [
            "Du kan kjøpe aksjen.",
            "Det kan være lurt å selge.",
            "Vi anbefaler å vente.",
            "Investorer bør følge med.",
            "Dette er ikke investeringsråd.",
            "Snakk med en rådgiver.",
            "Et alternativ for investorer.",
            "Et godt investeringsalternativ.",
            "Et kjøpssignal.",
            "Et salgssignal.",
            "Kursmålet er nådd.",
            "Behold aksjen.",
            "Hold på aksjen.",
            "Aksjen er undervurdert.",
            "Oppsiden er stor.",
        ],
    )
    def test_3_raad(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("3:") for g in svar.grunner)

    @pytest.mark.parametrize(
        "ord_, punkt",
        [
            # Ordene FR-603 og NFR-06 nevner, skrevet her og ikke hentet fra
            # listene, saa et ord som fjernes fra en liste, feiler testen (VG1).
            ("kjøp", "3"),
            ("selg", "3"),
            ("anbefaler", "3"),
            ("alternativ for investorer", "3"),
            ("investeringsråd", "3"),
            ("rådgiver", "3"),
            ("trolig", "4"),
            ("sannsynligvis", "4"),
            ("kan tyde på", "4"),
            ("forventes", "4"),
            ("antyder", "4"),
            ("skyldes", "4"),
            ("indikerer", "4"),
            ("kanskje", "4"),
            ("muligens", "4"),
            ("spår", "4"),
            ("nyheter", "4"),
            ("kontrakter", "4"),
            ("kvartalstall", "4"),
            ("oppkjøp", "4"),
            ("utbytte", "4"),
            ("børsmelding", "4"),
            ("renter", "4"),
            ("oljeprisen", "4"),
        ],
    )
    def test_ordene_fr_603_nevner(self, ord_, punkt):
        svar = kontroller(f"Her står {ord_} i teksten.", BLANDET)
        assert not svar.besto and any(g.startswith(punkt + ":") for g in svar.grunner), ord_

    @staticmethod
    def _eksempel(moenster: str) -> str:
        eksempel = re.sub(r"\(\?:([^|)]*)[^)]*\)\??", r"\1", moenster)
        return eksempel.replace("\\b", "").replace("\\w*", "")

    @pytest.mark.parametrize("moenster", RAAD)
    def test_3_hvert_ord_i_lista_stopper(self, moenster):
        assert not kontroller(f"Her står {self._eksempel(moenster)} i teksten.", BLANDET).besto

    @pytest.mark.parametrize("moenster", GJETNING + AARSAKER)
    def test_4_hvert_ord_i_lista_stopper(self, moenster):
        svar = kontroller(f"Her står {self._eksempel(moenster)} i teksten.", BLANDET)
        assert not svar.besto and any(g.startswith("4:") for g in svar.grunner), moenster

    @pytest.mark.parametrize(
        "tekst",
        [
            "Kursen steg trolig på grunn av nyheter.",
            "Det skyldes en ny kontrakt.",
            "Det kan tyde på mer oppgang.",
            "Kursen vil fortsette opp.",
            "Kursen vil stige.",
            "Kursen ventes å stige.",
            "Det skyldtes en kontrakt.",
        ],
    )
    def test_4_gjetning_og_aarsaker(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("4:") for g in svar.grunner)

    @pytest.mark.parametrize("ord_", ["børsdagen", "resultatet av sjekkene", "orientering", "rådata"])
    def test_4_ord_som_ikke_er_paa_lista(self, ord_):
        """«resultat» er ikke paa lista (FR-603), og «bør» stopper ikke «børs»."""
        assert kontroller(f"Det gjelder {ord_}.", BLANDET).besto

    @pytest.mark.parametrize("tekst", ["Snakk med en Rådgiver.", "Du bør kj­øpe."])
    def test_andre_tegn_slipper_ikke_gjennom(self, tekst):
        """Gjennomgangen (ECH): NFD og myk bindestrek."""
        assert not kontroller(tekst, BLANDET).besto

    def test_alle_grunnene_kommer_med(self):
        svar = kontroller("Retningen er positiv. Kjøp nå, kursen steg 3 %, trolig.", BLANDET)
        assert {g[0] for g in svar.grunner} == {"1", "2", "3", "4"}
        assert svar.grunn == "; ".join(svar.grunner)

    @pytest.mark.parametrize("styrke", ["2", 2.0, True, None])
    def test_styrken_i_grunnlaget_maa_vaere_et_heltall(self, styrke):
        with pytest.raises(TypeError):
            kontroller(GOD_TEKST, {**BLANDET, "styrke": styrke})


class TestRaden:
    def test_en_tekst_som_bestaar(self):
        modell = FalskModell()
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, modell)
        assert rad.besto and rad.tekst == GOD_TEKST and rad.grunn is None
        assert rad.promptversjon == PROMPTVERSJON
        assert (
            rad.tjeneste,
            rad.modell,
            rad.modell_id,
            rad.seed,
            rad.temperatur,
            rad.maskinvare,
            rad.ollama_versjon,
        ) == ("lokal", "gemma4:e4b", "dc35e8d9c606", 42, 0.0, "gpu", "0.35.1")
        assert rad.grunnlag == BLANDET and rad.regelen == REGELEN
        assert modell.prompter == [lag_prompt(BLANDET)]

    @pytest.mark.parametrize(
        "tekst, punkt",
        [
            ("Retningen er positiv.", "1"),
            ("Kursen steg 2,4 prosent.", "2"),
            ("Du bør kjøpe aksjen.", "3"),
            ("Det skyldes trolig nyheter.", "4"),
        ],
    )
    def test_hvert_punkt_stopper_en_tekst(self, tekst, punkt):
        """Story 10.2: en test med falsk modell viser at hvert av de fire
        punktene stopper en tekst. Teksten logges med grunnen og vises ikke."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(tekst))
        assert not rad.besto and rad.tekst == tekst
        assert rad.grunn.startswith(punkt + ":")
        assert not rad.modellen_feilet

    def test_merket_og_en_tekst_som_sier_det(self):
        grunnlag = {**BLANDET, "merke": "Utenfor målingen"}
        tekst = GOD_TEKST + " Grensene er ikke målt på denne aksjen."
        assert lag_ki_rad(EMNE, grunnlag, REGELEN, FalskModell(tekst)).besto

    @pytest.mark.parametrize(
        "feil, grunn",
        [
            (ModellFeilet("tidsavbrudd etter 60 s"), "modellen feilet: tidsavbrudd etter 60 s"),
            (ModellFeilet(), "modellen feilet"),
            (ModellFeilet("401 for key=abc123"), "modellen feilet: 401 for key=***"),
        ],
    )
    def test_modellen_feilet_gir_en_rad_uten_tekst(self, feil, grunn):
        """NFR-04, FR-604: ingenting reises videre, og raden sier hvorfor,
        uten noekler (gjennomgangen, BH14)."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(feil=feil))
        assert rad.modellen_feilet and not rad.besto
        assert rad.grunn == grunn
        assert (rad.tjeneste, rad.modell, rad.promptversjon) == ("lokal", "gemma4:e4b", PROMPTVERSJON)

    def test_en_lang_feilmelding_kortes_av(self):
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(feil=ModellFeilet("x" * 1000)))
        assert len(rad.grunn) <= len("modellen feilet: ") + 200

    @pytest.mark.parametrize("tekst", ["", "   ", None])
    def test_en_tom_tekst_er_at_modellen_feilet(self, tekst):
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(tekst))
        assert rad.modellen_feilet and rad.grunn == "modellen feilet: tom tekst"

    @pytest.mark.parametrize("svar", [None, "en tekst", {"tekst": "x"}])
    def test_et_svar_som_ikke_er_et_modellsvar(self, svar):
        """Gjennomgangen (BH15, ECH): en rad, ikke en feil som stopper hentingen."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(svar=svar or 0))
        assert rad.modellen_feilet and "ikke et Modellsvar" in rad.grunn

    @pytest.mark.parametrize(
        "kjoering",
        [
            dict(modell=""),
            dict(modell_id=""),
            dict(ollama_versjon=""),
            dict(seed=2**70),
            dict(temperatur="varm"),
            dict(maskinvare="GPU"),
        ],
    )
    def test_ugyldige_verdier_i_svaret(self, kjoering):
        """Gjennomgangen (VG5, ECH): en rad uten verdiene, ikke UgyldigKIRad."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(**kjoering))
        assert rad.modellen_feilet and rad.grunn == "modellen feilet: ugyldige verdier i svaret"
        assert rad.modell == "gemma4:e4b" and rad.seed is None

    def test_en_annen_feil_reises(self):
        """Bare feil hos modellen blir en rad. En feil i koden vaar skal synes."""
        with pytest.raises(ZeroDivisionError):
            lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(feil=ZeroDivisionError()))

    @pytest.mark.parametrize(
        "emne, grunnlag",
        [
            (Emne.dagen(date(2026, 10, 15)), BLANDET),
            (EMNE, {"trend": 1}),
            (EMNE, {**BLANDET, "styrke": "2"}),
        ],
    )
    def test_feil_emne_eller_grunnlag_reises_foer_modellen_kalles(self, emne, grunnlag):
        """Gjennomgangen (ECH, BH11): ingen kall gaar tapt."""
        modell = FalskModell()
        with pytest.raises(ValueError):
            lag_ki_rad(emne, grunnlag, REGELEN, modell)
        assert modell.prompter == []


# Story 10.2d: de 13 tekstene Gemma skrev til demoen (3.4b), og en feil
# retning for hver retning. Story 10.2e: tekstene i demoen er laget paa nytt
# med versjon 3, og de 13 med versjon 2 ligger ved testene, uendret fra
# src/demo_ki_tekster.json paa 153aba8, saa testene fra 10.2d staar.
DEMOTEKSTENE = Path(__file__).resolve().parent / "demo_ki_tekster_versjon_2.json"
FEIL_RETNING = {"Positiv": "Negativ", "Negativ": "Positiv", "Blandet": "Positiv", "Ingen": "Positiv"}


def _demotekstene() -> list[tuple[str, str, dict]]:
    """(symbol, tekst, grunnlag) for hver rad i demo_ki_tekster.json."""
    radene = json.loads(DEMOTEKSTENE.read_text(encoding="utf-8"))["radene"]
    return [(r["symbol"], r["tekst"], r["grunnlag"]) for r in radene]


def _med_feil_retning(tekst: str, retning: str) -> str:
    """Bytter den foerste retningen teksten sier, med stor forbokstav som Gemma
    skriver den («Negativt», «Blandet», «av typen Ingen»), til en feil retning,
    og beholder boeyningen."""
    treff = re.search(rf"\b{retning}(t?)\b", tekst)
    if not treff:
        raise ValueError(f"teksten sier ikke retningen {retning}: {tekst[:80]}")
    return tekst[: treff.start()] + FEIL_RETNING[retning] + treff.group(1) + tekst[treff.end() :]


class TestFormeneGemmaSkriver:
    """Story 10.2d (gruppens svar 18.10 kl. 21:03): kontrollen leser retningen
    og styrken i formene Gemma skriver. Hullet ble funnet med mutant K2 i 3.4b."""

    def test_feil_retning_i_demotekstene_stoppes(self):
        """Ville feilet hvis en av de 13 tekstene i demoen, med retningen den
        foerst sier byttet til en feil, besto kontrollen."""
        tekstene = _demotekstene()
        assert len(tekstene) == 13
        # Gjennomgangen (BH10): stoppet av retningen, ikke av noe annet.
        slapp = [
            symbol
            for symbol, tekst, grunnlag in tekstene
            if not any(
                g.startswith("1: retningen")
                for g in kontroller(_med_feil_retning(tekst, grunnlag["retning"]), grunnlag).grunner
            )
        ]
        assert slapp == [], f"{len(slapp)} av 13 slapp gjennom: {slapp}"

    def test_demotekstene_bestaar_som_de_er(self):
        """Ville feilet hvis den nye kontrollen stoppet en av de 13 tekstene i
        demoen slik de staar, saa de maatte lages paa nytt."""
        for symbol, tekst, grunnlag in _demotekstene():
            svar = kontroller(tekst, grunnlag)
            assert svar.besto, (symbol, svar.grunner)

    @pytest.mark.parametrize(
        "tekst",
        [
            "Dette signalet er Positivt, fordi to av de tre sjekkene ga utslag.",
            "Dette signalet er Negativt.",
            "Signalet er positiv.",
            "Signalet er altså positivt.",
            "Signalet er derfor negativt.",
            "Dette signalet er av typen Ingen.",
            "Dette signalet er av typen Positiv, fordi to av de tre sjekkene ga utslag.",
            "Signalet er ingen, fordi to av de tre sjekkene ga utslag.",
            "Signalet er ikke blandet.",
            "Retningen på signalet er positiv.",
            "Retningen til signalet er negativ.",
            "Dette er et positivt signal.",
            "Det er altså et negativt signal.",
            "Signalet er ikke et blandet signal.",
            # Gjennomgangen: omvendt ordstilling (BH2), ord mellom signalet og
            # verbet (BH3), fyll- og gradsord (BH4, ECH5), og anfoerselstegn og
            # fet skrift (BH5, ECH5).
            "Samlet er signalet positivt.",
            "Derfor er retningen positiv.",
            "Signalet for MOWI er Positivt.",
            "Signalet i dag er negativt.",
            "Dagens signal er Positivt.",
            "Signalet er samlet sett Negativt.",
            "Signalet er klart negativt.",
            "Dette er et sterkt positivt signal.",
            "Signalet er **Positivt**.",
            "Signalet er av typen «Ingen».",
            'Signalet er "Negativt".',
            "Signalet er: Negativt.",
        ],
    )
    def test_feil_retning_i_formene_stoppes(self, tekst):
        """Grunnlaget sier Blandet. Ville feilet hvis en av formene i punkt b
        slapp gjennom med feil retning."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("1: retningen") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "grunnlag, tekst",
        [
            (TRE_POSITIVE, "Dette signalet er Positivt, fordi alle tre sjekkene ga et positivt utslag."),
            (BLANDET, "Dette signalet er Blandet, fordi to av de tre sjekkene ga utslag."),
            (BLANDET, "Signalet er altså blandet."),
            (INGEN, "Dette signalet er av typen Ingen, fordi ingen av de tre sjekkene ga et utslag."),
            (INGEN, "Signalet er ingen, fordi ingen av de tre sjekkene ga utslag."),
            (BLANDET, "Signalet er ikke positivt."),
            (BLANDET, "Retningen på signalet er blandet."),
            (EN_POSITIV, "Dette er et positivt signal."),
            (BLANDET, "Dette signalet er av styrke to."),
            (TRE_POSITIVE, "Dette signalet er av styrke tre."),
            (INGEN, "Dette signalet er av styrke null."),
            (BLANDET, "Samlet er signalet blandet."),
            (
                {**BLANDET, "retning": "Negativ"},
                "Signalet for MOWI er **Negativt**, fordi to av de tre sjekkene ga utslag.",
            ),
        ],
    )
    def test_riktig_retning_og_styrke_i_formene_bestaar(self, grunnlag, tekst):
        """Ville feilet hvis en av formene i punkt b stoppet en tekst med
        riktig retning eller styrke."""
        svar = kontroller(tekst, grunnlag)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        ["Dette signalet er av styrke tre.", "Signalet er av styrke 1.", "Det er et signal av signalstyrke null."],
    )
    def test_feil_styrke_i_av_styrke_stoppes(self, tekst):
        """Grunnlaget sier styrke 2. Ville feilet hvis «av styrke N» med feil
        N slapp gjennom."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("1: styrken") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Trendens retning er positiv.",
            "Trenden ga et positivt utslag.",
            "Trenden ga et positivt signal.",
            # Gruppens svar 24.10 kl. 21:49: «bevegelsen ga et positivt utslag»
            # er et utsagn om én sjekk og stoppes naa, fordi bevegelsen er 0.
            # Formen staar med trenden, som er 1.
            "Interessen ga et negativt signal, og trenden ga et positivt utslag.",
            "Trendsignalet er positivt.",
            "Signalet er ingen garanti.",
            # Gjennomgangen: «det er et positivt signal» om en sjekk (BH1,
            # ECH1), en sjekk foran «signalet» (ECH2), bindestrek (BH7) og
            # retningen for hver sjekk etter «for» eller «på» (BH6, ECH3).
            "Kursen ligger over MA50, og det er et positivt signal.",
            "Dette signalet er Blandet. Trenden ga et positivt utslag, og det er et positivt signal.",
            "Volumet er høyt, og dette er et negativt signal for interessen.",
            "Trendens bidrag til signalet er positivt.",
            "Trendens retning på signalet er positiv.",
            "Trend-signalet er negativt.",
            "Signalet er positivt for trenden, men negativt for interessen.",
            # Gjennomgangen av rettingen (VG2): «negativt på bevegelse» er et
            # feil utsagn om én sjekk naar bevegelsen er 0, og stoppes i
            # TestEnSjekk. Formen staar med interessen, som er -1.
            "Signalet er positivt på trend, men negativt på interesse.",
        ],
    )
    def test_formene_om_en_sjekk_stoppes_ikke(self, tekst):
        """Grunnlaget sier Blandet. Ville feilet hvis kontrollen leste en form
        som gjelder én sjekk som retningen paa hele signalet, eller «Signalet
        er ingen garanti» som retningen Ingen."""
        svar = kontroller(tekst, BLANDET)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "tekst", ["Hver sjekk er av styrke én.", "Utslaget er av styrke tre.", "Trenden var av styrke én."]
    )
    def test_av_styrke_om_en_sjekk_stoppes_ikke(self, tekst):
        """Gjennomgangen (ECH8): grunnlaget sier styrke 2. Ville feilet hvis «av
        styrke N» om én sjekk eller et utslag ble lest som styrken paa hele
        signalet."""
        svar = kontroller(tekst, BLANDET)
        assert not any(g.startswith("1: styrken") for g in svar.grunner), svar.grunner

    def test_retningen_paa_signalet_gir_en_grunn(self):
        """Gjennomgangen (ECH4, VG6): ville feilet hvis «Retningen på signalet
        er positiv» ga samme grunn to ganger."""
        assert len(kontroller("Retningen på signalet er positiv.", BLANDET).grunner) == 1


# Story 10.2e: grunnlaget med dagen, som ki_grunnlag gir det for versjon 3.
DAGEN = {
    **BLANDET,
    "dager": 4,
    "dager_merke": "minst",
    "hovedindeksen": "falt",
    "aksjer_steg": 9,
    "aksjer_falt": 5,
    "bransjen": "steg",
}


class TestKontrollenVersjon3:
    """Story 10.2e, punkt c: tallene i grunnlaget, og retningen paa
    hovedindeksen og bransjen."""

    @pytest.mark.parametrize(
        "tekst",
        [
            "Signalet har vært slik i minst 4 børsdager.",
            "Ni aksjer i lista steg, og fem falt.",
            "9 av aksjene steg.",
            "Hovedindeksen falt i dag, mens bransjen steg i snitt.",
            "I dag falt hovedindeksen.",
            "Hovedindeksen på Oslo Børs falt.",
            "Aksjene i samme bransje steg i snitt.",
            "Bransjen falt ikke.",
            "Se endringen i tabellen.",
            "Aksjen på Oslo Børs steg.",
            "Hovedindeksen er ikke en del av regelen.",
        ],
    )
    def test_det_grunnlaget_sier_bestaar(self, tekst):
        """Ville feilet hvis kontrollen stoppet et antall fra grunnlaget, eller
        en riktig retning paa hovedindeksen eller bransjen."""
        svar = kontroller(tekst, DAGEN)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "tekst", ["Signalet har vært slik i 7 børsdager.", "Elleve aksjer.", "Det gjelder 6 aksjer."]
    )
    def test_et_tall_som_ikke_staar_i_grunnlaget(self, tekst):
        """Ville feilet hvis kontrollen slapp et tall som ikke er et av
        antallene i grunnlaget eller regelens faste tall."""
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any(g.startswith("2:") for g in svar.grunner), svar.grunner

    def test_tallene_fra_dagen_er_ikke_lov_uten_dagen(self):
        """Ville feilet hvis antallene var lov ogsaa naar grunnlaget ikke har
        dem: 9 er ikke et tall i grunnlaget fra versjon 2."""
        assert kontroller("Ni aksjer.", DAGEN).besto
        assert not kontroller("Ni aksjer.", BLANDET).besto

    @pytest.mark.parametrize(
        "tekst",
        [
            "Hovedindeksen steg i dag.",
            "I dag steg hovedindeksen.",
            "Hovedindeksen på Oslo Børs gikk opp.",
            "Oslo Børs steg.",
            "Hovedindeksen var uendret.",
            "Hovedindeksen falt ikke.",
            "OSEBX steg.",
        ],
    )
    def test_feil_retning_paa_hovedindeksen(self, tekst):
        """Grunnlaget sier at hovedindeksen falt. Ville feilet hvis en tekst
        som sier noe annet, besto."""
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any(g.startswith("1: hovedindeksen") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        ["Bransjen falt i snitt.", "Aksjene i samme bransje falt.", "Sektoren var uendret.", "Bransjen steg ikke."],
    )
    def test_feil_retning_paa_bransjen(self, tekst):
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any(g.startswith("1: bransjen") for g in svar.grunner), svar.grunner

    def test_hovedindeksen_naar_feltet_mangler(self):
        """Ville feilet hvis teksten kunne si noe om hovedindeksen eller
        bransjen naar grunnlaget ikke har feltet."""
        uten = {k: v for k, v in DAGEN.items() if k not in ("hovedindeksen", "bransjen")}
        for tekst in ("Hovedindeksen falt.", "Bransjen steg."):
            assert not kontroller(tekst, uten).besto, tekst

    @pytest.mark.parametrize("tekst", ["Fem aksjer steg.", "9 aksjer falt.", "Ni av aksjene i lista falt."])
    def test_antallene_byttet(self, tekst):
        """Ville feilet hvis et antall fra grunnlaget kunne staa om det andre
        antallet, som bare punkt 2 ikke fanger."""
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any(g.startswith("1: antallet") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst, grunn",
        [
            ("Hovedindeksen har steget.", "1: hovedindeksen"),
            ("Børsen har gått opp i dag.", "1: hovedindeksen"),
            ("Bransjen har sunket.", "1: bransjen"),
            ("Alle aksjene i lista steg.", "1: antallet"),
            ("Begge aksjene falt.", "1: antallet"),
        ],
    )
    def test_formene_fra_gjennomgangen_stoppes(self, tekst, grunn):
        """Gjennomgangen av 10.2e (BH3, BH4, ECH1, ECH3): ville feilet hvis
        perfektum slapp gjennom med feil retning, eller «alle» og «begge» ble
        lest som styrkens 3 og 2. Grunnlaget har ikke antallet i lista, saa
        «alle aksjene» kan ikke sjekkes og stoppes."""
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any(g.startswith(grunn) for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize("tekst", ["Aksjen på børsen steg.", "Hovedindeksen har sunket.", "Bransjen har økt."])
    def test_formene_fra_gjennomgangen_bestaar(self, tekst):
        """Gjennomgangen av 10.2e (BH5, VG3): «Aksjen på børsen steg» gjelder
        aksjen, ikke hovedindeksen."""
        svar = kontroller(tekst, DAGEN)
        assert svar.besto, svar.grunner

    def test_dagene_byttet_med_styrken(self):
        """Grunnlaget sier styrke 2 og 4 dager. Ville feilet hvis «to børsdager
        på rad» besto."""
        svar = kontroller("Signalet har vært slik i to børsdager på rad.", DAGEN)
        assert not svar.besto and any(g.startswith("1: dagene") for g in svar.grunner), svar.grunner


# Gruppens svar 24.10 kl. 21:49 (malinger.md §43): grunnlaget for MOWI, ORK og
# SALM 23.10, der bare trenden ga utslag, og for EQNR og AKRBP, der trenden og
# bevegelsen ga det. Antallene er vaare egne (regel 16).
BARE_TRENDEN = {
    **EN_POSITIV,
    "dager": 2,
    "hovedindeksen": "steg",
    "aksjer_steg": 8,
    "aksjer_falt": 7,
    "bransjen": "steg",
}
TREND_OG_BEVEGELSE = {**BARE_TRENDEN, "bevegelse": 1, "styrke": 2, "dager": 1}


class TestEnSjekk:
    """Gruppens svar 24.10 kl. 21:49, punkt b: et utsagn om én sjekk, med
    navnet og utslaget, skal stemme med fortegnet i grunnlaget."""

    @pytest.mark.parametrize(
        "tekst, dager",
        [
            # De tre tekstene i §43 som sa feil om interessen (MOWI, ORK, SALM).
            (
                "Dette signalet er Positivt med styrke én, fordi trenden ga et positivt utslag og interessen ga et "
                "positivt utslag. Signalet har hatt samme retning og styrke i to børsdager.",
                2,
            ),
            (
                "Dette signalet er Positivt med styrke én, fordi trenden ga et positivt utslag og interessen ga et "
                "positivt utslag. Signalet har hatt samme retning og styrke i to børsdager på rad.",
                2,
            ),
            (
                "Dette signalet er Positivt med styrke én, fordi trenden ga et positivt utslag og interessen ga et "
                "positivt utslag. Signalet har hatt samme retning og styrke i tre børsdager.",
                3,
            ),
        ],
    )
    def test_de_tre_tekstene_i_43_som_sa_feil_om_interessen(self, tekst, dager):
        """Ville feilet hvis kontrollen slapp en tekst som sier at interessen
        ga utslag der grunnlaget sier 0, slik de tre gjorde i §43. Stoppet av
        sjekken av interessen, og etter svaret 24.10 kl. 23:23 ogsaa av dagene
        med egne ord, og ingenting annet."""
        svar = kontroller(tekst, {**BARE_TRENDEN, "dager": dager})
        assert not svar.besto and any(g.startswith("1: sjekken interesse") for g in svar.grunner), svar.grunner
        assert all(g.startswith(("1: sjekken interesse", "1: dagene")) for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Interessen ga et utslag.",
            "Bevegelsen ga et negativt utslag.",
            "Trenden ga et negativt utslag.",
            "Trenden ga ikke noe utslag.",
            "Trenden og interessen ga positive utslag.",
            "Trend, bevegelse og interesse ga et positivt utslag.",
            "Interessen slo ut.",
            "Trenden slo ikke ut.",
            "Interessen er positiv.",
            "Trenden ga ikke et positivt utslag.",
            "Ingen sjekk ga utslag på trenden.",
            "Det var et positivt utslag på interessen.",
            "Trendsjekken ga et negativt utslag.",
        ],
    )
    def test_feil_om_en_sjekk_stoppes(self, tekst):
        """Grunnlaget sier at bare trenden ga et positivt utslag. Ville feilet
        hvis en av formene sa noe annet om én sjekk og slapp gjennom."""
        svar = kontroller(tekst, EN_POSITIV)
        assert not svar.besto and any(g.startswith("1: sjekken") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Trenden ga et positivt utslag.",
            "Trenden ga utslag, mens bevegelse og interesse ikke ga noe utslag.",
            "Interessen ga ikke utslag.",
            "Interessen ga ikke et positivt utslag.",
            "Bevegelsen og interessen slo ikke ut.",
            "Trenden er positiv.",
            "Det var ikke noe utslag på interessen.",
            "Ingen sjekk ga utslag på interesse.",
        ],
    )
    def test_riktig_om_en_sjekk_bestaar(self, tekst):
        """Ville feilet hvis kontrollen stoppet et riktig utsagn om én sjekk."""
        svar = kontroller(tekst, EN_POSITIV)
        assert svar.besto, svar.grunner

    def test_ingen_sjekk_ga_utslag_paa_en_sjekk_er_ikke_styrken(self):
        """Teksten for EQNR og AKRBP i §43 ble stoppet fordi «Ingen sjekk ga»
        ble lest som styrke 0. Ville feilet hvis «ingen sjekk ga utslag på»
        en sjekk fortsatt ble lest som styrken, eller ikke ble sjekket mot
        den sjekken."""
        tekst = (
            "Dette signalet er Positivt med styrke to, fordi trenden ga et positivt utslag og bevegelsen ga et "
            "positivt utslag. Ingen sjekk ga utslag på interesse."
        )
        assert kontroller(tekst, TREND_OG_BEVEGELSE).besto, kontroller(tekst, TREND_OG_BEVEGELSE).grunner
        svar = kontroller(tekst, {**TREND_OG_BEVEGELSE, "interesse": 1, "styrke": 3})
        assert not svar.besto and any(g.startswith("1: sjekken interesse") for g in svar.grunner), svar.grunner
        assert not any(g.startswith("1: styrken «Ingen") for g in svar.grunner), svar.grunner

    def test_ingen_sjekk_uten_en_sjekk_er_fortsatt_styrken(self):
        """MPCC i §43: «Ingen sjekk ga et positivt utslag» med styrke 2. Ville
        feilet hvis det ikke lenger ble lest som styrken."""
        svar = kontroller("Ingen sjekk ga et positivt utslag.", {**BLANDET, "retning": "Negativ"})
        assert not svar.besto and any(g.startswith("1: styrken") for g in svar.grunner), svar.grunner

    def test_listen_over_tankestrek_er_styrken(self):
        """DNB i §43: ville feilet hvis «ingen av de tre sjekkene – trend,
        bevegelse og interesse – ga et utslag» ble lest som at hver sjekk ga
        utslag."""
        tekst = (
            "Dette signalet er av typen Ingen, fordi ingen av de tre sjekkene – trend, bevegelse og interesse – "
            "ga et utslag."
        )
        assert kontroller(tekst, INGEN).besto, kontroller(tekst, INGEN).grunner


class TestMinst:
    """Gruppens svar 24.10 kl. 21:49, punkt b: «minst» om dagene er lov bare
    med merket, og et eksakt antall dager med merket stoppes."""

    @pytest.mark.parametrize(
        "tekst",
        [
            # Formene fra §43, der grunnlaget ikke hadde merket.
            "Signalet har hatt samme retning og styrke i minst to børsdager.",
            "Det har vært minst to børsdager med samme retning og styrke.",
            "Signalet har hatt samme retning og styrke i minst to børsdager på rad.",
            "Det har vært to bølger av samme retning og styrke, fordi feltet dager er minst.",
        ],
    )
    def test_minst_uten_merket_stoppes(self, tekst):
        """Ville feilet hvis «minst» om dagene slapp gjennom uten merket, slik
        seks tekster i §43 gjorde."""
        svar = kontroller(tekst, BARE_TRENDEN)
        assert not svar.besto and any(g.startswith("1: «minst»") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            # Gruppens svar 24.10 kl. 23:23: ordlyden er «i 2 børsdager på rad».
            "Signalet har hatt samme retning og styrke i 2 børsdager på rad.",
            "Minst én sjekk ga utslag. Signalet har vært slik i 2 børsdager på rad.",
            "Det ble handlet mye på en dag kursen steg, og i dag er signalet det samme.",
        ],
    )
    def test_eksakt_uten_merket_bestaar(self, tekst):
        """Ville feilet hvis kontrollen stoppet ordlyden uten merket, «minst»
        i en annen setning, eller «en dag» som vanlig ord."""
        svar = kontroller(tekst, BARE_TRENDEN)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            # Bestod foer svaret 24.10 kl. 23:23: riktig antall, med egne ord.
            "Signalet har hatt samme retning og styrke i to børsdager.",
            "Signalet har hatt samme retning og styrke i to børsdager på rad.",
            "Minst én sjekk ga utslag. Signalet har vært slik i to børsdager.",
        ],
    )
    def test_riktig_antall_med_egne_ord_stoppes(self, tekst):
        """Gruppens svar 24.10 kl. 23:23: dagene aldri med egne ord. Ville
        feilet hvis et riktig antall dager i annen form enn ordlyden besto."""
        svar = kontroller(tekst, BARE_TRENDEN)
        assert not svar.besto and any("i annen form" in g for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Signalet har hatt samme retning og styrke i fire børsdager.",
            "Signalet har vært slik i 4 børsdager på rad.",
            "Det har vært fire børsdager med samme retning og styrke.",
        ],
    )
    def test_eksakt_med_merket_stoppes(self, tekst):
        """Grunnlaget sier minst 4. Ville feilet hvis et eksakt antall dager
        slapp gjennom med merket."""
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any("i annen form" in g for g in svar.grunner), svar.grunner

    def test_minst_med_merket_bestaar(self):
        """Ville feilet hvis ordlyden med «minst» ble stoppet med merket.
        Gruppens svar 24.10 kl. 23:23: ordlyden er «i minst 4 børsdager»."""
        svar = kontroller("Signalet har hatt samme retning og styrke i minst 4 børsdager.", DAGEN)
        assert svar.besto, svar.grunner

    def test_minst_med_merket_og_egne_ord_stoppes(self):
        """Bestod foer svaret 24.10 kl. 23:23. Ville feilet hvis «minst fire»
        med ord, ikke ordlyden, besto med merket."""
        svar = kontroller("Signalet har hatt samme retning og styrke i minst fire børsdager.", DAGEN)
        assert not svar.besto and any("i annen form" in g for g in svar.grunner), svar.grunner


class TestGjennomgangenAvRettingen:
    """Gjennomgangen 24.10 av rettingen etter svaret kl. 21:49 (BH, ECH, VG)."""

    @pytest.mark.parametrize(
        "tekst",
        [
            # BH1: ord mellom «ga» og «utslag» etter «ingen sjekk».
            "Ingen sjekk ga dessverre noe utslag på interessen.",
            # BH2: «ikke» inne i perfektum.
            "Trenden har ikke gitt utslag.",
            # BH3, ECH6: genitiv og fortegnet etter «ut».
            "Trendens utslag var negativt.",
            "Trenden slo ut negativt.",
            # BH5, ECH7: verbet underforstaatt etter «og».
            "Trenden ga et positivt utslag, og interessen et negativt.",
            # ECH5: et gradsord foran fortegnet.
            "Interessen ga et sterkt positivt utslag.",
            # BH10, ECH4: «eller» i lista etter «ingen sjekk ga utslag på».
            "Ingen sjekk ga utslag på bevegelsen eller trenden.",
            # VG2: «signal» og «negativt på» om én sjekk.
            "Interessen ga et positivt signal.",
            "Signalet er positivt på trend, men negativt på bevegelse.",
            # «eller» uten «verken» sier ikke hvilken sjekk.
            "Trenden eller interessen ga utslag.",
        ],
    )
    def test_feil_om_en_sjekk_i_formene_fra_gjennomgangen_stoppes(self, tekst):
        """Grunnlaget sier at bare trenden ga et positivt utslag. Ville feilet
        hvis en av formene slapp gjennom."""
        svar = kontroller(tekst, EN_POSITIV)
        assert not svar.besto and any(g.startswith(("1: sjekk", "1: styrken")) for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Verken bevegelsen eller interessen ga utslag.",
            "Hverken bevegelsen eller interessen slo ut.",
            "Interessen har ikke gitt utslag.",
            "Trendens utslag var positivt.",
            "Trenden slo ut positivt.",
            "Trenden ga et klart positivt utslag, og interessen ikke noe utslag.",
            "Ingen sjekk ga utslag på bevegelse eller interesse.",
            "Signalet er positivt for trenden.",
        ],
    )
    def test_riktig_om_en_sjekk_i_formene_fra_gjennomgangen_bestaar(self, tekst):
        """Ville feilet hvis en riktig form fra gjennomgangen ble stoppet."""
        svar = kontroller(tekst, EN_POSITIV)
        assert svar.besto, svar.grunner

    def test_en_sjekk_som_mangler_i_grunnlaget_stoppes(self):
        """ECH: ville feilet hvis et utsagn om en sjekk som mangler i
        grunnlaget, slapp gjennom uten aa bli sjekket."""
        grunnlag = {k: v for k, v in EN_POSITIV.items() if k != "interesse"}
        svar = kontroller("Interessen ga ikke utslag.", grunnlag)
        assert not svar.besto and any("grunnlaget sier ingenting" in g for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            # Gruppens svar 24.10 kl. 23:23: med ordlyden, ikke «i to børsdager».
            "Minst én sjekk ga utslag, og signalet har vært slik i 2 børsdager på rad.",
            "Minst én sjekk ga utslag sammenlignet med de siste 20 dagene.",
            "Minst én sjekk ga utslag i  dag.",
            "Snittet for de siste 50 børsdager.",
            "Vinduet er 20 dager.",
        ],
    )
    def test_minst_om_sjekkene_og_regelens_vinduer_bestaar(self, tekst):
        """BH6, ECH8, ECH9: ville feilet hvis «minst» om sjekkene i en setning
        om dagene, eller regelens vinduer, ble lest som dagene."""
        svar = kontroller(tekst, BARE_TRENDEN)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Signalet har holdt seg åtte børsdager.",
            "Signalet har vært slik i hele tre børsdager.",
            "Signalet har hatt samme retning og styrke i tre børsdager.",
            "Det har vært tre børsdager.",
            "Signalet har vært slik tre børsdager etter hverandre.",
        ],
    )
    def test_feil_antall_dager_uten_paa_rad_stoppes(self, tekst):
        """BH7, ECH1, ECH2, VG1: grunnlaget sier 2 dager. Ville feilet hvis et
        feil antall dager slapp gjennom fordi teksten ikke har «i» eller «på
        rad» (8 er ogsaa aksjer_steg, saa punkt 2 fanger det ikke)."""
        svar = kontroller(tekst, BARE_TRENDEN)
        assert not svar.besto and any(g.startswith("1: dagene") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Signalet har holdt seg fire børsdager.",
            "Det har vært fire børsdager.",
            "Signalet har vært slik fire børsdager etter hverandre.",
        ],
    )
    def test_eksakt_med_merket_uten_i_stoppes(self, tekst):
        """BH7, VG1: grunnlaget sier minst 4. Ville feilet hvis et eksakt
        antall dager uten «i» slapp gjennom med merket."""
        svar = kontroller(tekst, DAGEN)
        assert not svar.besto and any("i annen form" in g for g in svar.grunner), svar.grunner

    def test_minst_foer_i_med_merket_stoppes(self):
        """BH8: bestod etter rettingen kl. 21:49. Gruppens svar 24.10 kl.
        23:23: «minst i fire børsdager» er ikke ordlyden «i minst 4
        børsdager». Ville feilet hvis den besto."""
        svar = kontroller("Signalet har vært slik minst i fire børsdager.", DAGEN)
        assert not svar.besto and any("i annen form" in g for g in svar.grunner), svar.grunner


# Gruppens svar 24.10 kl. 23:23 (malinger.md §44): grunnlaget for EQNR, AKRBP
# og FRO 23.10, der trenden og bevegelsen ga utslag, og for VAR, der alle tre
# ga det. Alle fire hadde 1 dag uten merket. Antallene er vaare egne (regel 16).
TO_POSITIVE_EN_DAG = {**TREND_OG_BEVEGELSE, "retning": "Positiv"}
TRE_POSITIVE_EN_DAG = {**TRE_POSITIVE, "dager": 1}


class TestOrdlyden:
    """Gruppens svar 24.10 kl. 23:23: modellen faar ferdig ordlyd for dagene
    og skriver dem aldri med egne ord. Kontrollen stopper dagene i annen form."""

    @pytest.mark.parametrize(
        "dager, merke, ordlyd",
        [
            (1, None, "i dag for første gang"),
            (4, None, "i 4 børsdager på rad"),
            (12, "minst", "i minst 12 børsdager"),
            (1, "minst", "i minst 1 børsdag"),
        ],
    )
    def test_ordlyden_lages_av_dagene_og_merket(self, dager, merke, ordlyd):
        """Ville feilet hvis ordlyden ikke fulgte dagene og merket, eller ikke
        sto i prompten etter opplysningene."""
        grunnlag = {**BLANDET, "dager": dager, **({"dager_merke": merke} if merke else {})}
        assert ordlyd_for_dagene(grunnlag) == ordlyd
        prompt = lag_prompt(grunnlag)
        opplysningene, linja = prompt.split("Opplysningene:\n", 1)[1].split("\n", 1)
        assert json.loads(opplysningene) == grunnlag
        assert linja == f"Ordlyden for dagene: {ordlyd}\n"

    def test_ingen_ordlyd_uten_dagene(self):
        """Grunnlaget fra versjon 2 har ikke dagene. Ville feilet hvis
        prompten fikk en ordlyd for dager grunnlaget ikke har."""
        assert ordlyd_for_dagene(BLANDET) is None
        assert "Ordlyden for dagene:" not in lag_prompt(BLANDET)

    def test_minst_staar_ikke_i_prompten_uten_merket(self):
        """BH13 i gjennomgangen av rettingen: prompten nevnte «minst» ogsaa
        uten merket, og 3 av 4 stopp i §44 var «minst». Ville feilet hvis
        «minst» sto i prompten for et grunnlag uten merket."""
        for dager in (1, 2, 12):
            assert "minst" not in lag_prompt({**BARE_TRENDEN, "dager": dager}).lower()

    @pytest.mark.parametrize(
        "tekst, grunnlag",
        [
            ("Signalet har i dag for første gang denne retningen og styrken.", TO_POSITIVE_EN_DAG),
            ("I dag for første gang har signalet denne retningen og styrken.", TO_POSITIVE_EN_DAG),
            ("Signalet har hatt samme retning og styrke i 2 børsdager på rad.", BARE_TRENDEN),
            ("Signalet har hatt samme retning og styrke i minst 4 børsdager.", DAGEN),
            ("Hovedindeksen falt i dag, og den andre sjekken ga ikke utslag.", DAGEN),
        ],
    )
    def test_ordlyden_bestaar(self, tekst, grunnlag):
        """Ville feilet hvis ordlyden ordrett, ogsaa med stor forbokstav
        foerst i setningen, eller «i dag» og «andre» som vanlige ord, ble
        stoppet."""
        svar = kontroller(tekst, grunnlag)
        assert svar.besto, svar.grunner

    def test_minst_en_boersdag_fra_44_stoppes(self):
        """EQNR, AKRBP og FRO i §44 hadde samme setning og samme grunnlag:
        «i minst én børsdag» uten merket. Én test, ikke tre (gjennomgangen
        25.10, BH8, VG5). Ville feilet hvis formen slapp gjennom."""
        tekst = "Dette signalet har hatt samme retning og styrke i minst én børsdag."
        svar = kontroller(tekst, TO_POSITIVE_EN_DAG)
        assert not svar.besto and any(g.startswith("1: «minst» om dagene") for g in svar.grunner), svar.grunner

    def test_det_tredje_paa_rad_fra_44_stoppes_som_dagene(self):
        """VAR i §44: «det tredje på rad» med 1 dag. Foer ble den bare
        stoppet av punkt 2 («tredje»). Ville feilet hvis ordenstallet ikke
        ogsaa ble stoppet som dagene i annen form."""
        tekst = "Dette er det tredje på rad at signalet har hatt samme retning og styrke."
        svar = kontroller(tekst, TRE_POSITIVE_EN_DAG)
        assert not svar.besto and any(g.startswith("1: dagene «tredje på rad»") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst, grunnlag",
        [
            ("Signalet har denne retningen for første gang.", TO_POSITIVE_EN_DAG),
            ("Signalet har denne retningen for andre gang.", TO_POSITIVE_EN_DAG),
            ("Dette er det andre på rad.", TO_POSITIVE_EN_DAG),
            ("Signalet har vært slik i 1 børsdag.", TO_POSITIVE_EN_DAG),
            ("Signalet har vært slik i fire børsdager på rad.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik i 4 børsdager.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik 4 børsdager på rad.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik i 4 dager på rad.", {**DAGEN, "dager_merke": None}),
            ("Det er den fjerde børsdagen på rad.", {**DAGEN, "dager_merke": None}),
            ("Signalet er i dag for første gang slik.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært det samme flere dager på rad.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært det samme dager i trekk.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik i 4 børsdager på rad.", DAGEN),
            ("Signalet har vært slik i 2 børsdager på rad.", BLANDET),
            # Gjennomgangen 25.10 (BH12, VG3, ECH5, BH2, ECH6, BH1, ECH7).
            ("Signalet har vært slik i minst fire børsdager på rad.", DAGEN),
            ("Signalet har vært slik dager etter hverandre.", {**DAGEN, "dager_merke": None}),
            ("Det er den femte børsdagen.", {**DAGEN, "dager_merke": None}),
            ("Det er den 4. dagen.", {**DAGEN, "dager_merke": None}),
            ("Signalet har holdt seg 20 børsdager.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vart 50 dager.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik flere ganger.", {**DAGEN, "dager_merke": None}),
            ("Nok en gang er signalet slik.", {**DAGEN, "dager_merke": None}),
            ("Signalet er det samme som i går.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik siden mandag.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik i flere dager.", {**DAGEN, "dager_merke": None}),
            ("Signalet har vært slik i 4 handelsdager.", {**DAGEN, "dager_merke": None}),
            ("Signalet er det første med denne retningen.", TO_POSITIVE_EN_DAG),
            ("Signalet har ikke vært slik i dag for første gang.", TO_POSITIVE_EN_DAG),
            ("Det har ikke holdt i 4 børsdager på rad.", {**DAGEN, "dager_merke": None}),
        ],
    )
    def test_dagene_i_annen_form_stoppes(self, tekst, grunnlag):
        """Ville feilet hvis dagene slapp gjennom i annen form enn ordlyden:
        ordenstall, tall med ord, uten «i» eller «på rad», «dager» for
        «børsdager», ordlyden for et annet antall, eller dager grunnlaget
        ikke har."""
        svar = kontroller(tekst, grunnlag)
        assert not svar.besto and any(g.startswith(("1: dagene", "1: «minst»")) for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            # Formene fra demotekstene 25.10 for NLYS, SLVP og KVST, med 1 dag.
            "Dette er det første signalet i dag for første gang.",
            "Dette er det første signalet med denne retningen og styrken i dag for første gang.",
            "Dette er det første signalet med denne retningen og styrken, som vist i «i dag for første gang».",
            "Det er det tredje positive signalet.",
        ],
    )
    def test_ordenstall_ved_signalet_stoppes(self, tekst):
        """Ville feilet hvis «det første signalet med denne retningen», dagene
        med egne ord, slapp gjennom ved siden av ordlyden."""
        svar = kontroller(tekst, TRE_POSITIVE_EN_DAG)
        assert not svar.besto and any(g.startswith("1: dagene") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Signalet har hatt samme retning og styrke i «i dag for første gang».",
            "Den andre sjekken ga ikke utslag.",
            "Bevegelsen og de andre sjekkene ga et positivt utslag.",
        ],
    )
    def test_ordlyden_i_anfoerselstegn_og_andre_som_vanlig_ord_bestaar(self, tekst):
        """Demotekstene 25.10 hadde ordlyden i anfoerselstegn. Ville feilet
        hvis den, eller «andre» som vanlig ord, ble stoppet."""
        svar = kontroller(tekst, TRE_POSITIVE_EN_DAG)
        assert svar.besto, svar.grunner


class TestGjennomgangen25_10:
    """Gjennomgangen 25.10 av ordlyden for dagene (BH, ECH, VG)."""

    @pytest.mark.parametrize(
        "tekst, grunnlag",
        [
            # ECH1, BH3: «andre … i dag» er ikke dagene.
            ("Trenden og de andre sjekkene i dag ga dette.", DAGEN),
            ("De andre aksjene i dag steg.", DAGEN),
            ("Snittet for de andre dagene.", DAGEN),
            # ECH2, VG4: «andre» og «annen» som «other».
            ("Andre dager kan bli annerledes.", DAGEN),
            ("Det ble handlet mye på en annen dag enn i dag.", DAGEN),
            ("Ingen andre signaler er med.", DAGEN),
            # ECH3: et tall som slutter en setning, foran «Dagen».
            ("Signalet har styrke 2. Dagen var rolig for hovedindeksen, som falt.", DAGEN),
            # ECH5: regelens vinduer med ordet foran.
            ("Vinduet er 20 dager.", DAGEN),
            ("Snittet for 50 dager.", DAGEN),
            # BH1: «ikke» om noe annet foer ordlyden.
            ("Bevegelsen ga ikke utslag, og signalet er slik i minst 4 børsdager.", DAGEN),
            # VG6: ordlyden i rette anfoerselstegn, som i demotekstene.
            ('Signalet har hatt samme retning og styrke i "i minst 4 børsdager".', DAGEN),
            # Grunnlaget fra versjon 2 uten dagene.
            ("Trenden og de andre sjekkene i dag ga dette.", BLANDET),
        ],
    )
    def test_riktige_tekster_bestaar(self, tekst, grunnlag):
        """Ville feilet hvis en riktig tekst ble stoppet som dagene i annen
        form."""
        svar = kontroller(tekst, grunnlag)
        assert svar.besto, svar.grunner

    def test_prompten_og_kontrollen_bruker_samme_ordlyd(self, monkeypatch):
        """VG1: ville feilet hvis kontrollen hadde sin egen kopi av ordlyden i
        stedet for ordlyd_for_dagene fra ki_prompt."""
        import ki_prompt

        monkeypatch.setattr(ki_prompt, "DAGENE_FOERSTE", "for aller første gang i dag")
        grunnlag = {**TO_POSITIVE_EN_DAG}
        assert "Ordlyden for dagene: for aller første gang i dag\n" in lag_prompt(grunnlag)
        assert kontroller("Signalet er slik for aller første gang i dag.", grunnlag).besto
        assert not kontroller("Signalet er slik i dag for første gang.", grunnlag).besto

    def test_avtrykket_dekker_valget_av_ordlyd(self):
        """VG2, BH7: ville feilet hvis avtrykket bare dekket malene, slik at en
        endret logikk i ordlyd_for_dagene ga samme versjon."""
        assert inspect.getsource(ordlyd_for_dagene) in _promptteksten()
        assert inspect.getsource(lag_prompt) in _promptteksten()

    def test_bildet_viser_en_aksje_der_teksten_besto(self):
        """VG7, gruppens svar 24.10 kl. 23:23 (b): ville feilet hvis bildet av
        aksjesiden viste en demoaksje der KI-teksten ble stoppet."""
        radene = json.loads((Path(__file__).parents[1] / "src" / "demo_ki_tekster.json").read_text("utf-8"))["radene"]
        assert next(r for r in radene if r["symbol"] == "BRFE")["besto"] is True
