"""Story 10.2a: porten Modell, prompten og kontrollen i FR-603 - AD-2, AD-8.

Alt med en falsk modell. Ingen test kaller en ekte tjeneste, og nettsperren
i conftest.py stopper en som proever (story 4.0).
"""

import hashlib
import json
import re
from datetime import date

import pytest

from ki_kontroll import AARSAKER, GJETNING, RAAD, kontroller
from ki_modell import Modell, ModellFeilet, Modellsvar, lag_ki_rad
from ki_prompt import PROMPTVERSJON, REGLER, UTENFOR, lag_prompt
from kilogg import Emne

EMNE = Emne.aksje("EQNR", date(2026, 10, 15))
BLANDET = {"trend": 1, "bevegelse": 0, "interesse": -1, "styrke": 2, "retning": "Blandet"}
INGEN = {"trend": 0, "bevegelse": 0, "interesse": 0, "styrke": 0, "retning": "Ingen"}
EN_POSITIV = {"trend": 1, "bevegelse": 0, "interesse": 0, "styrke": 1, "retning": "Positiv"}
TRE_POSITIVE = {"trend": 1, "bevegelse": 1, "interesse": 1, "styrke": 3, "retning": "Positiv"}
REGELEN = "Trenden ga +1 og interessen -1."
GOD_TEKST = ("Kursen ligger over snittet for de siste 50 dagene, men det ble handlet mye på en dag "
             "kursen falt. To av de tre sjekkene ga utslag, i hver sin retning, så retningen er blandet.")

# sha256 av promptteksten for hver versjon (FR-605). Endres teksten, maa
# PROMPTVERSJON opp og en ny linje inn her.
AVTRYKK = {"1": "8fa4608965a356110f97963f65ba85bb44c79e913d47b5b911dc06b51af7be72",
           "2": "4c697052292bf7069ed7ba0cb7600a8c67574c969fd4fcd184f4b854876df660"}


class FalskModell:
    """En modell som svarer det testen sier, og husker prompten (AD-8)."""

    tjeneste = "lokal"
    modell = "gemma4:e4b"

    def __init__(self, tekst: str | None = GOD_TEKST, feil: Exception | None = None, svar=None, **kjoering):
        self.tekst = tekst
        self.feil = feil
        self.svar = svar
        self.kjoering = dict(modell="gemma4:e4b", modell_id="dc35e8d9c606", seed=42, temperatur=0.0,
                             maskinvare="gpu", ollama_versjon="0.35.1")
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
        assert PROMPTVERSJON == "2"
        linje = "- Når du forklarer regelen, bruk «fordi». Ikke bruk «skyldes» eller «indikerer»."
        assert linje in REGLER.split("Regler for teksten:", 1)[1].splitlines()
        assert linje in lag_prompt(BLANDET)

    def test_ingen_raad_og_ingen_gjetning(self):
        prompt = lag_prompt(BLANDET)
        assert "Ikke gi råd" in prompt and "Ikke gjett" in prompt

    def test_merket_utenfor_maalingen(self):
        assert UTENFOR in lag_prompt({**BLANDET, "merke": "Utenfor målingen"})
        assert UTENFOR not in lag_prompt(BLANDET)

    def test_versjonen_foelger_teksten(self):
        """Gjennomgangen (BH13): en endret prompt maa faa ny versjon (FR-605)."""
        avtrykk = hashlib.sha256((REGLER + UTENFOR).encode("utf-8")).hexdigest()
        assert AVTRYKK.get(PROMPTVERSJON) == avtrykk, (
            "Promptteksten er endret. Sett ny PROMPTVERSJON og legg avtrykket i AVTRYKK.")

    def test_prompten_har_ingen_tall_kontrollen_stopper(self):
        """Gjennomgangen (BH1, BH2): gjentar modellen prompten, skal den ikke
        stoppes av punkt 2."""
        for styrke, retning in ((0, "Ingen"), (1, "Positiv"), (2, "Blandet"), (3, "Positiv")):
            grunnlag = {**BLANDET, "styrke": styrke, "retning": retning}
            del_av_prompten = REGLER.split("Regler for teksten:")[0].replace(
                "I opplysningene under står 1 for positivt utslag, -1 for negativt og 0 for ikke noe utslag.", "")
            assert not [g for g in kontroller(del_av_prompten, grunnlag).grunner if g.startswith("2:")]
            assert kontroller(UTENFOR, grunnlag).besto


class TestKontrollen:
    def test_en_god_tekst_bestaar(self):
        svar = kontroller(GOD_TEKST, BLANDET)
        assert svar.besto, svar.grunner
        assert svar.grunn is None

    def test_regelen_selv_kan_forklares(self):
        """FR-603 punkt 4: «fordi ingen sjekk ga utslag» er lov naar ingen ga det."""
        assert kontroller("Retningen er ingen, fordi ingen sjekk ga utslag.", INGEN).besto

    def test_fordi_ingen_sjekk_naar_noen_ga_utslag(self):
        """Gjennomgangen (BH7): da er det et feil utsagn om styrken."""
        svar = kontroller("Retningen er blandet fordi ingen sjekk ga utslag.", BLANDET)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner)

    @pytest.mark.parametrize("tekst", [
        "Retningen er positiv.", "Det er en negativ retning.", "Retningen er altså ingen.",
        "Det er ingen retning.", "Retningen er ikke blandet.",
    ])
    def test_1_feil_retning(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and svar.grunner[0].startswith("1:")

    @pytest.mark.parametrize("tekst", [
        "Trendens retning er positiv.", "Retningen er ikke positiv.", "Retningen er dermed blandet.",
    ])
    def test_1_retning_som_er_riktig_eller_gjelder_en_sjekk(self, tekst):
        assert kontroller(tekst, BLANDET).besto, kontroller(tekst, BLANDET).grunner

    @pytest.mark.parametrize("tekst", [
        "Styrken er tre.", "Signalstyrken er 1.", "Ingen av de tre sjekkene ga utslag.",
        "Én av tre sjekker slo ut.", "En av de tre sjekkene ga utslag.", "Alle tre sjekkene ga utslag.",
        "Styrken på signalet er tre.", "Styrken er altså tre.", "3 av 3 sjekker ga utslag.",
    ])
    def test_1_feil_styrke(self, tekst):
        """Ogsaa «ingen av de tre sjekk» naar styrken er 2 (§19, E-med)."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner)

    @pytest.mark.parametrize("grunnlag, tekst", [
        (EN_POSITIV, "To sjekker ga utslag."), (EN_POSITIV, "To av de tre sjekkene ga utslag."),
        (TRE_POSITIVE, "To av de tre sjekkene ga utslag."), (INGEN, "Én sjekk ga utslag."),
    ])
    def test_1_feil_styrke_ved_andre_styrker(self, grunnlag, tekst):
        """Gjennomgangen (BH18): ikke bare styrke 2."""
        assert not kontroller(tekst, grunnlag).besto

    @pytest.mark.parametrize("grunnlag, tekst", [
        (EN_POSITIV, "Én av de tre sjekkene ga utslag, så retningen er positiv."),
        (TRE_POSITIVE, "Alle tre sjekkene ga utslag, og retningen er positiv."),
        (INGEN, "Ingen av de tre sjekkene ga utslag."),
    ])
    def test_1_riktig_styrke_bestaar(self, grunnlag, tekst):
        assert kontroller(tekst, grunnlag).besto, kontroller(tekst, grunnlag).grunner

    def test_positiv_og_negativ_som_ord_i_blandet(self):
        """FR-603 punkt 1: ordene alene er ikke et utsagn om retningen."""
        tekst = "Trenden er positiv, mens interessen er negativ. Retningen er blandet."
        assert kontroller(tekst, BLANDET).besto

    @pytest.mark.parametrize("tekst", [
        "Kursen steg 2,4 prosent.", "Kursen steg 3 %.", "Snittet for de siste 30 dagene.",
        "Femdagssnittet ligger lavere.", "Seks av de femti aksjene.", "Snittet over sytti dager.",
        "Volumet var 1.5 ganger normalt.", "Kursen steg to prosent.", "Kursen steg 3 prosent.",
        "Aksjen kostet 50 kroner.", "Handelen var dobbelt så stor.", "Femtifem dager.",
        "Det tiårige snittet.", "For tredje dag på rad.", "Over tiårsperioden.",
    ])
    def test_2_tall_og_mengder_som_ikke_er_i_grunnlaget(self, tekst):
        """Ogsaa tall skrevet med ord (§19: «femdagssnittet», «seks av de femti»)."""
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("2:") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize("tekst", [
        "Snittet for de siste 50 dagene.", "MA50 ligger under kursen.", "Vinduet er 20 dager.",
        "To av de tre sjekkene ga utslag.", "Femti dager er grunnlaget for trenden.",
        "Dette gjelder én aksje.", "Grensene er ikke målt på denne aksjen.",
    ])
    def test_2_regelens_faste_tall_og_styrken_er_lov(self, tekst):
        assert kontroller(tekst, BLANDET).besto, kontroller(tekst, BLANDET).grunner

    @pytest.mark.parametrize("ord_", ["trend", "tid", "nivået", "totalt", "trenden"])
    def test_2_ord_som_begynner_som_et_tallord(self, ord_):
        assert kontroller(f"Det gjelder {ord_}.", BLANDET).besto

    @pytest.mark.parametrize("tekst", ["Styrken er ².", "Kursen er " + "9" * 5000 + "."])
    def test_2_rare_tall_gir_en_grunn_ikke_en_feil(self, tekst):
        """Gjennomgangen (ECH): «²» og et svaert langt tall reiste ValueError."""
        assert not kontroller(tekst, BLANDET).besto or "²" in tekst

    @pytest.mark.parametrize("tekst", [
        "Du kan kjøpe aksjen.", "Det kan være lurt å selge.", "Vi anbefaler å vente.",
        "Investorer bør følge med.", "Dette er ikke investeringsråd.", "Snakk med en rådgiver.",
        "Et alternativ for investorer.", "Et godt investeringsalternativ.", "Et kjøpssignal.",
        "Et salgssignal.", "Kursmålet er nådd.", "Behold aksjen.", "Hold på aksjen.",
        "Aksjen er undervurdert.", "Oppsiden er stor.",
    ])
    def test_3_raad(self, tekst):
        svar = kontroller(tekst, BLANDET)
        assert not svar.besto and any(g.startswith("3:") for g in svar.grunner)

    @pytest.mark.parametrize("ord_, punkt", [
        # Ordene FR-603 og NFR-06 nevner, skrevet her og ikke hentet fra
        # listene, saa et ord som fjernes fra en liste, feiler testen (VG1).
        ("kjøp", "3"), ("selg", "3"), ("anbefaler", "3"), ("alternativ for investorer", "3"),
        ("investeringsråd", "3"), ("rådgiver", "3"),
        ("trolig", "4"), ("sannsynligvis", "4"), ("kan tyde på", "4"), ("forventes", "4"),
        ("antyder", "4"), ("skyldes", "4"), ("kanskje", "4"), ("muligens", "4"), ("spår", "4"),
        ("nyheter", "4"), ("kontrakter", "4"), ("kvartalstall", "4"), ("oppkjøp", "4"),
        ("utbytte", "4"), ("børsmelding", "4"), ("renter", "4"), ("oljeprisen", "4"),
    ])
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

    @pytest.mark.parametrize("tekst", [
        "Kursen steg trolig på grunn av nyheter.", "Det skyldes en ny kontrakt.",
        "Det kan tyde på mer oppgang.", "Kursen vil fortsette opp.", "Kursen vil stige.",
        "Kursen ventes å stige.", "Det skyldtes en kontrakt.",
    ])
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

    def test_merket_og_en_tekst_som_sier_det(self):
        grunnlag = {**BLANDET, "merke": "Utenfor målingen"}
        tekst = GOD_TEKST + " Grensene er ikke målt på denne aksjen."
        assert lag_ki_rad(EMNE, grunnlag, REGELEN, FalskModell(tekst)).besto

    @pytest.mark.parametrize("feil, grunn", [
        (ModellFeilet("tidsavbrudd etter 60 s"), "modellen feilet: tidsavbrudd etter 60 s"),
        (ModellFeilet(), "modellen feilet"),
        (ModellFeilet("401 for key=abc123"), "modellen feilet: 401 for key=***"),
    ])
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

    @pytest.mark.parametrize("kjoering", [
        dict(modell=""), dict(modell_id=""), dict(ollama_versjon=""), dict(seed=2**70),
        dict(temperatur="varm"), dict(maskinvare="GPU"),
    ])
    def test_ugyldige_verdier_i_svaret(self, kjoering):
        """Gjennomgangen (VG5, ECH): en rad uten verdiene, ikke UgyldigKIRad."""
        rad = lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(**kjoering))
        assert rad.modellen_feilet and rad.grunn == "modellen feilet: ugyldige verdier i svaret"
        assert rad.modell == "gemma4:e4b" and rad.seed is None

    def test_en_annen_feil_reises(self):
        """Bare feil hos modellen blir en rad. En feil i koden vaar skal synes."""
        with pytest.raises(ZeroDivisionError):
            lag_ki_rad(EMNE, BLANDET, REGELEN, FalskModell(feil=ZeroDivisionError()))

    @pytest.mark.parametrize("emne, grunnlag", [
        (Emne.dagen(date(2026, 10, 15)), BLANDET),
        (EMNE, {"trend": 1}),
        (EMNE, {**BLANDET, "styrke": "2"}),
    ])
    def test_feil_emne_eller_grunnlag_reises_foer_modellen_kalles(self, emne, grunnlag):
        """Gjennomgangen (ECH, BH11): ingen kall gaar tapt."""
        modell = FalskModell()
        with pytest.raises(ValueError):
            lag_ki_rad(emne, grunnlag, REGELEN, modell)
        assert modell.prompter == []
