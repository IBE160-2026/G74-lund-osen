"""Story 10.11: «mest av bransjene med minst to aksjer» i teksten om
boersdagen (gruppens svar 11.11 kl. 22:04, funn 4 fra demoproeven).

Spesifikasjonen: _bmad-output/implementation-artifacts/
spec-10-11-mest-av-bransjene-med-minst-to-aksjer.md. Eksempelskriveren er
den falske modellen, som i testene for 10.10.
"""

from pathlib import Path

import pytest

import demo_ki
from dagene import MINST_I_BRANSJEN
from dagsgrunnlag import MEST_NED, MEST_OPP
from hjelpetekster import hjelpetekster
from ki_dagen import AV_BRANSJENE, DAGSPROMPTVERSJON, REGLER_DAGEN, kontroller_dagen, lag_dagsprompt, lag_dagsrad
from ki_eksempel import EksempelModell, tekst_om_dagen
from ki_visning import bygg_dagsvisning
from kilogg import Emne, KIRad
from kursdata import Aksje
from test_ki_dagen import AVTRYKK, FREDAG
from test_rikere_ki_tekster import LISTA, SERIER, VURDERINGER, grunnlaget, to_dager, vurdering

ROT = Path(__file__).resolve().parents[1]
STEG = f"I snitt steg energi mest {AV_BRANSJENE}."
FALT = f"I snitt falt finans mest {AV_BRANSJENE}."


class TestFormene:
    def test_formen_sier_grensen_for_bransjene(self):
        """Ville feilet hvis formen sa et annet tall enn grensen appen regner
        snittet med, eller prompten ikke hadde formen for begge sidene."""
        assert MINST_I_BRANSJEN == 2 and AV_BRANSJENE == "av bransjene med minst to aksjer"
        assert f"mest {AV_BRANSJENE}.»" in REGLER_DAGEN
        assert REGLER_DAGEN.count(f"mest {AV_BRANSJENE}.»") == 2
        assert "«I snitt steg ‹bransje_mest_opp› mest.»" not in lag_dagsprompt(grunnlaget())

    def test_versjonen_er_dag_3(self):
        """FR-605: ville feilet hvis de nye formene fikk samme versjon som
        tekstene kveldshentingen alt kan ha skrevet med dag-2."""
        assert DAGSPROMPTVERSJON == "dag-3"
        assert AVTRYKK["dag-3"] != AVTRYKK["dag-2"]

    def test_de_nye_formene_bestaar(self):
        """Ville feilet hvis kontrollen stoppet formene prompten gir, alene,
        i hele eksempelteksten, eller med linjeskift og store bokstaver."""
        g = grunnlaget()
        assert g[MEST_OPP] == "Energi" and g[MEST_NED] == "Finans"
        for tekst in (STEG, FALT, f"{STEG} {FALT}", tekst_om_dagen(g), FALT.replace(" med ", "\nmed ").upper()):
            svar = kontroller_dagen(tekst, g)
            assert svar.besto, (tekst, svar.grunner)
        assert tekst_om_dagen(g).endswith(f"{STEG} {FALT}")

    @pytest.mark.parametrize(
        "tekst",
        [
            "I snitt steg energi mest.",
            "I snitt falt finans mest.",
            "I snitt falt finans mest, av bransjene med minst to aksjer.",
            "I snitt falt finans mest av bransjene.",
            "I snitt falt finans mest av bransjene med minst 2 aksjer.",
            "I snitt falt finans mest av bransjene med minst tre aksjer.",
            "I snitt falt finans mest av alle bransjene med minst to aksjer.",
            "I snitt falt finans mest av bransjene med minst to aksjer med en endring.",
        ],
    )
    def test_mest_uten_av_bransjene_stoppes(self, tekst):
        """Ville feilet hvis kontrollen godtok en form med «mest» som ikke
        sier «av bransjene med minst to aksjer» slik formen gir det, også med
        et siffer eller et annet tall."""
        svar = kontroller_dagen(tekst, grunnlaget())
        assert not svar.besto, tekst

    def test_den_gamle_formen_faar_en_egen_grunn(self):
        """Spørsmål 2: ville feilet hvis grunnen ikke sa hva som mangler."""
        svar = kontroller_dagen("I snitt falt finans mest.", grunnlaget())
        assert svar.grunner == (f"1: «I snitt falt finans mest» sier ikke «{AV_BRANSJENE}»",)

    def test_feil_bransje_i_den_nye_formen_stoppes(self):
        """Ville feilet hvis den nye formen godtok en annen bransje enn den
        appen regnet ut, eller formen uten feltet i grunnlaget."""
        assert not kontroller_dagen(FALT.replace("finans", "sjømat"), grunnlaget()).besto
        uten = {n: v for n, v in grunnlaget().items() if n != MEST_NED}
        assert not kontroller_dagen(FALT, uten).besto


class TestEnAksjeBlirAldriMest:
    """Funnet: Industri hadde én aksje og falt mer enn Finans."""

    # Industri har én aksje som falt 10 %, Telekom én som steg 10 %, og
    # Konsum to, men bare én med kurs paa dagen.
    LISTA = LISTA + (
        Aksje("III", "III.OL", "India", "Industri"),
        Aksje("TTT", "TTT.OL", "Tango", "Telekom"),
        Aksje("KKK", "KKK.OL", "Kilo", "Konsum"),
        Aksje("LLL", "LLL.OL", "Lima", "Konsum"),
    )
    VURDERINGER = {
        **VURDERINGER,
        "III": vurdering(1, "Positiv"),
        "TTT": vurdering(1, "Positiv"),
        "KKK": vurdering(1, "Positiv"),
        "LLL": vurdering(1, "Positiv"),
    }
    SERIER = {
        **SERIER,
        "III": to_dager(100, 90),
        "TTT": to_dager(100, 110),
        "KKK": to_dager(100, 80),
        "LLL": to_dager(100, 100)[:1],
    }

    def grunnlaget(self):
        return grunnlaget(lista=self.LISTA, vurderinger=self.VURDERINGER, serier=self.SERIER)

    def test_en_bransje_med_en_aksje_er_aldri_mest(self):
        """Ville feilet hvis en bransje med én aksje, eller med to aksjer der
        bare én har en endring den dagen, ble bransjen som steg eller falt
        mest, selv om den steg eller falt mer enn alle de andre."""
        g = self.grunnlaget()
        assert g[MEST_OPP] == "Energi" and g[MEST_NED] == "Finans"
        assert not {"Industri", "Telekom", "Konsum"} & set(g["bransjer"])

    @pytest.mark.parametrize(("verb", "bransje"), [("falt", "industri"), ("steg", "telekom"), ("falt", "konsum")])
    def test_kontrollen_stopper_en_bransje_med_en_aksje(self, verb, bransje):
        """Ville feilet hvis teksten kunne si at en bransje med én aksje med
        en endring steg eller falt mest."""
        svar = kontroller_dagen(f"I snitt {verb} {bransje} mest {AV_BRANSJENE}.", self.grunnlaget())
        assert not svar.besto


class TestTekstene:
    def test_en_tekst_med_dag_2_vises_fortsatt(self):
        """Spørsmål 3: ville feilet hvis en tekst med dag-2 og den gamle
        formen forsvant fra forsiden, selv om grunnlaget er det samme."""
        naa = grunnlaget()
        rad = lag_dagsrad(Emne.dagen(FREDAG), naa, EksempelModell())
        felt = {f: getattr(rad, f) for f in rad.__dataclass_fields__}
        gammel = KIRad(**{**felt, "grunnlag": naa, "promptversjon": "dag-2", "tekst": "I snitt falt finans mest."})
        assert bygg_dagsvisning(gammel, naa).vist

    def test_demoteksten_har_de_nye_formene(self):
        """Ville feilet hvis demoteksten om dagen var laget med en gammel
        prompt, eller sa «mest» uten «av bransjene med minst to aksjer»."""
        dagen = demo_ki.les_dagsraden(prompt=demo_ki.dagens_promptavtrykk())
        assert dagen.promptversjon == "dag-3" and dagen.besto
        assert f"finans mest {AV_BRANSJENE}" in dagen.tekst.lower()
        assert kontroller_dagen(dagen.tekst, dagen.grunnlag).besto

    def test_hjelpen_sier_grensen(self):
        """Regel 19: ville feilet hvis hjelpen på siden eller docs/hjelp.md
        ikke sa at «mest» bare gjelder bransjene med minst to aksjer."""
        assert "minst to aksjer" in hjelpetekster()["boersdagen_kort_fortalt"].tekst
        hjelp = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "Bransjen som steg eller falt mest regnes bare av bransjene med minst to aksjer med en endring" in hjelp
