"""Story 10.10: rikere KI-tekster - FR-602, FR-603, FR-605, FR-607, NFR-06,
AD-8, AD-10.

Spesifikasjonen er spec-10-10-rikere-ki-tekster.md, etter gruppens svar
10.11 kl. 16:18. Testene bruker eksempelskriveren i ki_eksempel.py som falsk
modell (AD-8), og ingen test kaller Ollama eller EODHD.
"""

import json
from datetime import date
from pathlib import Path

import pytest

import demo_ki
from dagsgrunnlag import ANDRE, MEST_NED, MEST_OPP, NAVNENE, dagsgrunnlag, for_promptversjon, mest_opp_og_ned
from ki_dagen import DAGSPROMPTVERSJON, REGLER_DAGEN, dagsregel, kontroller_dagen, lag_dagsprompt, lag_dagsrad
from ki_eksempel import MODELLNAVN, EksempelModell, tekst_om_aksjen, tekst_om_dagen
from ki_kontroll import kontroller
from ki_modell import lag_ki_rad
from ki_prompt import PROMPTVERSJON, REGLER, lag_prompt
from ki_visning import bygg_dagsvisning
from kilogg import Emne, KIRad
from kursdata import Aksje, Kursrad
from test_ki_dagen import FREDAG, TORSDAG
from vurderingsdata import Vurdering

ROT = Path(__file__).resolve().parents[1]
HARDT = chr(0xA0)
MYK = chr(0xAD)
SPEC = ROT / "_bmad-output" / "implementation-artifacts" / "spec-10-10-rikere-ki-tekster.md"


def vurdering(styrke: int, retning: str) -> Vurdering:
    trend, bevegelse, interesse = {
        (1, "Positiv"): (1, 0, 0),
        (2, "Positiv"): (1, 1, 0),
        (2, "Negativ"): (-1, -1, 0),
        (3, "Positiv"): (1, 1, 1),
        (3, "Negativ"): (-1, -1, -1),
    }[(styrke, retning)]
    return Vurdering(
        styrke=styrke,
        retning=retning,
        trend=trend,
        bevegelse=bevegelse,
        interesse=interesse,
        slutt=100.0,
        justert_slutt=100.0,
        trend_avvik=0.0,
        dagens_endring=0.0,
        standardavvik=0.01,
        volumforhold=1.0,
    )


def to_dager(foer: float, etter: float) -> list[Kursrad]:
    return [
        Kursrad(dato=TORSDAG, slutt=foer, justert_slutt=foer, volum=1000),
        Kursrad(dato=FREDAG, slutt=etter, justert_slutt=etter, volum=1000),
    ]


# Sju aksjer som skilte seg ut, i tre bransjer. Navnene staar med vilje ikke
# i alfabetisk rekkefoelge i lista.
LISTA = (
    Aksje("GGG", "GGG.OL", "Gamma", "Energi"),
    Aksje("AAA", "AAA.OL", "Alfa", "Energi"),
    Aksje("FFF", "FFF.OL", "Foxtrot", "Finans"),
    Aksje("BBB", "BBB.OL", "Bravo", "Finans"),
    Aksje("EEE", "EEE.OL", "Echo", "Sjømat"),
    Aksje("CCC", "CCC.OL", "Charlie", "Sjømat"),
    Aksje("DDD", "DDD.OL", "Delta Hav" + HARDT + "ASA", "Sjømat"),
)
VURDERINGER = {
    "GGG": vurdering(2, "Positiv"),
    "AAA": vurdering(2, "Negativ"),
    "FFF": vurdering(3, "Positiv"),
    "BBB": vurdering(2, "Positiv"),
    "EEE": vurdering(3, "Negativ"),
    "CCC": vurdering(2, "Negativ"),
    "DDD": vurdering(2, "Positiv"),
}
# Snittene: Energi (3 - 1) / 2 = 1, Finans (-2 - 4) / 2 = -3, Sjømat (0,5 + 0,5 + 0,5) / 3 = 0,5.
SERIER = {
    "GGG": to_dager(100, 103),
    "AAA": to_dager(100, 99),
    "FFF": to_dager(100, 98),
    "BBB": to_dager(100, 96),
    "EEE": to_dager(100, 100.5),
    "CCC": to_dager(100, 100.5),
    "DDD": to_dager(100, 100.5),
}
INDEKS = to_dager(1000, 1005)


def grunnlaget(lista=LISTA, vurderinger=VURDERINGER, serier=SERIER):
    return dagsgrunnlag(FREDAG, lista, vurderinger, serier, INDEKS)


class TestGrunnlagetForDagen:
    """Del A: appen regner ut navnene og bransjene."""

    def test_navnene_3_av_3_foerst_hoeyst_fem_og_resten_som_antall(self):
        """Ville feilet hvis navnene sto i lista sin rekkefoelge, hvis 2 av 3
        kom foer 3 av 3, hvis det var mer enn fem navn, eller resten ikke var
        et antall."""
        g = grunnlaget()
        assert [n["navn"] for n in g[NAVNENE]] == ["Echo", "Foxtrot", "Alfa", "Bravo", "Charlie"]
        assert [n["styrke"] for n in g[NAVNENE]] == [3, 3, 2, 2, 2]
        assert [n["retning"] for n in g[NAVNENE]] == ["negativ", "positiv", "negativ", "positiv", "negativ"]
        assert g[ANDRE] == 2

    def test_samme_grunnlag_uansett_rekkefoelgen_i_lista(self):
        """Spørsmål 3 (FR-607): forsiden regner grunnlaget på nytt med
        sorteringen den har. Ville feilet hvis navnene fulgte lista."""
        assert dict(grunnlaget()) == dict(grunnlaget(lista=tuple(reversed(LISTA))))

    def test_uten_resten_naar_fem_eller_faerre(self):
        """Ville feilet hvis feltet for resten sto med 0 (tall som er 0, tas
        ikke med)."""
        fem = {s: v for s, v in VURDERINGER.items() if s not in ("GGG", "DDD")}
        g = grunnlaget(vurderinger=fem)
        assert len(g[NAVNENE]) == 5 and ANDRE not in g

    def test_ingen_navn_naar_ingen_skilte_seg_ut(self):
        """Ville feilet hvis grunnlaget fikk en tom liste."""
        ingen = {s: vurdering(1, "Positiv") for s in VURDERINGER}
        g = grunnlaget(vurderinger=ingen)
        assert g["skilte_seg_ut"] == 0 and NAVNENE not in g and ANDRE not in g

    def test_bransjene_med_hoeyest_og_lavest_snitt(self):
        """Ville feilet hvis bransjen ble valgt etter antallet som steg, ikke
        snittet som paa Boersometeret: Energi har snittet 1, Sjømat 0,5 og
        Finans -3."""
        g = grunnlaget()
        assert g[MEST_OPP] == "Energi" and g[MEST_NED] == "Finans"

    def test_likt_snitt_gir_ingen_bransje(self):
        """Spørsmål 2: ville feilet hvis appen valgte én av to bransjer med
        samme snitt slik det vises."""
        assert mest_opp_og_ned({"Energi": 1.0, "Sjømat": 1.0, "Finans": -3.0}) == {MEST_NED: "Finans"}

    def test_snittet_sammenlignes_slik_det_vises(self):
        """Spørsmål 1 og 2, gjennomgangen (BH3, VG1): 1,001 og 1,004 vises
        begge som 1,00, og 0,004 og 0,003 som 0,00. Ville feilet hvis
        snittene ble sammenlignet uten avrunding: da ville Sjømat og Energi
        blitt «steg mest»."""
        opp = {s: to_dager(100, 101.001) for s in ("GGG", "AAA")} | {
            s: to_dager(100, 101.004) for s in ("EEE", "CCC", "DDD")
        }
        assert MEST_OPP not in grunnlaget(serier=dict(SERIER, **opp))
        naer_null = {s: to_dager(100, 100.004) for s in ("GGG", "AAA")} | {
            s: to_dager(100, 100.003) for s in ("EEE", "CCC", "DDD")
        }
        assert MEST_OPP not in grunnlaget(serier=dict(SERIER, **naer_null))

    def test_norsk_alfabetisk_rekkefoelge(self):
        """Gjennomgangen (BH5): ville feilet med rekkefølgen på kodepunkter,
        som gir Å foran Æ og Ø, og små bokstaver etter store."""
        lista = tuple(
            Aksje(f"S{i}", f"S{i}.OL", navn, "Energi") for i, navn in enumerate(("Ålesund", "Øst", "Ærlig", "berg"))
        )
        vurderinger = {a.symbol: vurdering(2, "Positiv") for a in lista}
        serier = {a.symbol: to_dager(100, 101) for a in lista}
        g = dagsgrunnlag(FREDAG, lista, vurderinger, serier, INDEKS)
        assert [n["navn"] for n in g[NAVNENE]] == ["berg", "Ærlig", "Øst", "Ålesund"]

    def test_ingen_bransje_steg_naar_alle_falt(self):
        """Ville feilet hvis bransjen med høyest snitt ble «steg mest» når
        snittet var under 0."""
        assert mest_opp_og_ned({"Energi": -1.0, "Finans": -3.0}) == {MEST_NED: "Finans"}

    def test_bare_navn_heltall_og_tekst(self):
        """Ville feilet hvis grunnlaget fikk en kurs, en prosent eller et
        snitt som tall (beslutningen 04.10, FR-607)."""
        tekst = json.dumps({n: v for n, v in grunnlaget().items()}, ensure_ascii=False)
        assert "." not in tekst and "%" not in tekst


class TestGamleRader:
    """Spørsmål 5: rader med dag-1 vises fortsatt etter flettingen."""

    def test_dag_1_sammenlignes_uten_de_nye_feltene(self):
        """Ville feilet hvis en tekst fra før flettingen forsvant fra
        forsiden, fordi grunnlaget nå har flere felt."""
        naa = grunnlaget()
        gammelt = {n: v for n, v in naa.items() if n not in (NAVNENE, ANDRE, MEST_OPP, MEST_NED)}
        rad = KIRad(
            emne=Emne.dagen(FREDAG),
            grunnlag=gammelt,
            regelen="r",
            tekst="Hovedindeksen steg fredag.",
            besto=True,
            grunn=None,
            promptversjon="dag-1",
            tjeneste="lokal",
            modell="gemma4:e4b",
        )
        assert bygg_dagsvisning(rad, naa).vist

    def test_dag_2_maa_ha_de_nye_feltene(self):
        """Ville feilet hvis en rad med dag-2 uten navnene ble vist."""
        naa = grunnlaget()
        gammelt = {n: v for n, v in naa.items() if n != NAVNENE}
        rad = lag_dagsrad(Emne.dagen(FREDAG), naa, EksempelModell())
        assert bygg_dagsvisning(rad, naa).vist
        endret = KIRad(**{**{f: getattr(rad, f) for f in rad.__dataclass_fields__}, "grunnlag": gammelt})
        assert not bygg_dagsvisning(endret, naa).vist

    def test_for_promptversjon_endrer_bare_dag_1(self):
        naa = grunnlaget()
        assert for_promptversjon(naa, DAGSPROMPTVERSJON) is naa
        assert NAVNENE not in for_promptversjon(naa, "dag-1")


class TestPromptenForDagen:
    def test_versjon_dag_2_med_formene(self):
        """Ville feilet hvis prompten manglet formene for navnene og
        bransjene, eller versjonen ikke var ny (FR-605)."""
        assert DAGSPROMPTVERSJON == "dag-2"
        assert "«Blant dem var ‹navn› (‹styrke› av 3, ‹retning›)" in REGLER_DAGEN
        assert "«I snitt steg ‹bransje_mest_opp› mest.»" in REGLER_DAGEN
        assert "«I snitt falt ‹bransje_mest_ned› mest.»" in REGLER_DAGEN
        assert "«bør», «verdt å følge» eller «følg med»" in REGLER_DAGEN

    def test_navnene_kommer_med_i_prompten(self):
        opplysningene = json.loads(lag_dagsprompt(grunnlaget()).split("Opplysningene:\n", 1)[1].splitlines()[0])
        assert opplysningene[NAVNENE][0] == {"navn": "Echo", "retning": "negativ", "styrke": 3}


class TestKontrollenForDagen:
    """Del C: hvert navn og hvert tall mot grunnlaget (FR-603)."""

    def tekst(self) -> str:
        return tekst_om_dagen(grunnlaget())

    def test_eksempelteksten_bestaar(self):
        """Ville feilet hvis kontrollen stoppet formene prompten gir, også et
        navn med hardt mellomrom skrevet med vanlig mellomrom."""
        tekst = self.tekst()
        assert "Blant dem var Echo (3 av 3, negativ), Foxtrot (3 av 3, positiv)" in tekst
        assert tekst.endswith("og 2 andre. I snitt steg energi mest. I snitt falt finans mest.")
        assert kontroller_dagen(tekst, grunnlaget()).besto, kontroller_dagen(tekst, grunnlaget()).grunner
        g = {n: v for n, v in grunnlaget().items() if n != ANDRE}
        g[NAVNENE] = [{"navn": "Delta Hav" + HARDT + "ASA", "styrke": 2, "retning": "positiv"}]
        tekst = "Blant dem var Delta Hav ASA (2 av 3, positiv)."
        assert HARDT not in tekst
        assert kontroller_dagen(tekst, g).besto, kontroller_dagen(tekst, g).grunner

    @pytest.mark.parametrize(
        ("navnene", "tekst"),
        [
            # ECH2: et navn som er slutten av et annet.
            (
                [("BP", 3, "positiv"), ("Aker BP", 2, "negativ")],
                "Blant dem var BP (3 av 3, positiv) og Aker BP (2 av 3, negativ).",
            ),
            # ECH3: to aksjer med samme navn.
            (
                [("Foo", 3, "positiv"), ("Foo", 2, "negativ")],
                "Blant dem var Foo (3 av 3, positiv) og Foo (2 av 3, negativ).",
            ),
            # ECH5: myk bindestrek i navnet i grunnlaget.
            ([("Kon" + MYK + "sberg", 3, "positiv")], "Blant dem var Konsberg (3 av 3, positiv)."),
        ],
    )
    def test_vanskelige_navn_bestaar(self, navnene, tekst):
        """Gjennomgangen (ECH2, ECH3, ECH5): ville feilet hvis en riktig tekst
        ble stoppet fordi et navn var slutten av et annet, to aksjer hadde
        samme navn, eller navnet i grunnlaget hadde en myk bindestrek."""
        g = {n: v for n, v in grunnlaget().items() if n != ANDRE}
        g[NAVNENE] = [{"navn": n, "styrke": s, "retning": r} for n, s, r in navnene]
        svar = kontroller_dagen(tekst, g)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        ("fra", "til", "grunn"),
        [
            # BH1, ECH1: et navn utelatt, men «og 2 andre» som i feltet.
            ("Echo (3 av 3, negativ), ", "", "4 av 5 navn"),
            # BH1: rekkefølgen i grunnlaget.
            (
                "Echo (3 av 3, negativ), Foxtrot (3 av 3, positiv)",
                "Foxtrot (3 av 3, positiv), Echo (3 av 3, negativ)",
                "rekkefølgen",
            ),
            # BH7: et navn utenfor setningen etter «Blant dem var».
            ("Blant dem var Echo (3 av 3, negativ), ", "Echo (3 av 3, negativ). Blant dem var ", "setningen etter"),
            # ECH4: «Blant dem var» og bransjen to ganger.
            ("I snitt falt finans mest.", "I snitt falt finans mest. Blant dem var.", "én gang foran navnene"),
            ("I snitt falt finans mest.", "I snitt falt finans mest. I snitt steg energi mest.", "mer enn én gang"),
            # «og N andre» mangler når feltet er der.
            (" og 2 andre", "", "andre» skal stå én gang"),
            # VG6: navnet med andre store og små bokstaver.
            ("Echo (", "ECHO (", "4 av 5 navn"),
        ],
    )
    def test_setningen_med_navnene_stoppes(self, fra, til, grunn):
        """Gjennomgangen: ville feilet hvis kontrollen godtok en setning der
        et navn manglet (så «og 2 andre» ble feil), navnene sto i en annen
        rekkefølge, et navn sto utenfor setningen, en form sto to ganger,
        «og N andre» manglet, eller navnet var skrevet med andre bokstaver."""
        tekst = self.tekst()
        assert fra in tekst
        svar = kontroller_dagen(tekst.replace(fra, til, 1), grunnlaget())
        assert not svar.besto and any(grunn in g for g in svar.grunner), svar.grunner

    def test_blant_dem_var_uten_navnene_i_grunnlaget(self):
        """Gjennomgangen (VG5): ville feilet hvis «Blant dem var» besto uten
        navnene i grunnlaget, også når resten av setningen er en lovlig form."""
        g = {n: v for n, v in grunnlaget().items() if n != NAVNENE}
        svar = kontroller_dagen("Blant dem var 2 andre.", g)
        assert not svar.besto and any(f"{NAVNENE} mangler" in x for x in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        ("setning", "grunn"),
        [
            ("Den bør følges.", "3: «bør"),
            ("Den er verdt å følge.", "3: «verdt"),
            ("Følg med på den.", "3: «Følg med"),
            ("Den følges med interesse.", "3: «følges med"),
            ("Det vil vise seg.", "4: «vil"),
        ],
    )
    def test_raad_stoppes_under_punkt_3_og_4(self, setning, grunn):
        """Gjennomgangen (VG3, VG4, BH6): ville feilet hvis ordene bare ble
        stoppet som rest, ikke under punkt 3 og 4, eller hvis «vil» bare ble
        stoppet med de gamle verbene. Gjelder begge kontrollene."""
        svar = kontroller_dagen(self.tekst() + " " + setning, grunnlaget())
        assert not svar.besto and any(g.startswith(grunn) for g in svar.grunner), svar.grunner
        svar = kontroller(tekst_om_aksjen(TestVersjon6.GRUNNLAG) + " " + setning, TestVersjon6.GRUNNLAG)
        assert not svar.besto and any(g.startswith(grunn) for g in svar.grunner), svar.grunner

    def test_regelen_har_navnene_og_bransjene(self):
        """Gjennomgangen (VG2), FR-604: ville feilet hvis regelen i loggen
        manglet navnene, resten eller bransjene."""
        regelen = dagsregel(grunnlaget())
        assert "Navnene: Echo (3 av 3, negativ), Foxtrot (3 av 3, positiv)," in regelen
        assert ", og 2 andre." in regelen
        assert "Høyest snitt: Energi." in regelen and "Lavest snitt: Finans." in regelen

    @pytest.mark.parametrize(
        ("fra", "til"),
        [
            ("Echo (3 av 3, negativ)", "Echo (3 av 3, positiv)"),
            ("Echo (3 av 3, negativ)", "Echo (2 av 3, negativ)"),
            ("Echo (3 av 3, negativ)", "Equinor (3 av 3, negativ)"),
            ("Echo (3 av 3, negativ)", "Echo (3 av 3, negativ), Echo (3 av 3, negativ)"),
            ("og 2 andre", "og 3 andre"),
            ("I snitt steg energi mest", "I snitt steg sjømat mest"),
            ("I snitt falt finans mest", "I snitt falt energi mest"),
            ("I snitt steg energi mest.", "I snitt steg energi mest, og den bør følges."),
            ("I snitt steg energi mest.", "I snitt steg energi mest, og den er verdt å følge."),
            ("I snitt steg energi mest.", "I snitt steg energi mest. Følg med på den."),
            ("I snitt steg energi mest.", "I snitt steg energi mest, og den vil stige."),
            ("I snitt steg energi mest.", "I snitt steg energi mest, fordi oljeprisen steg."),
        ],
    )
    def test_feil_stoppes(self, fra, til):
        """Ville feilet hvis kontrollen slapp gjennom feil retning eller
        styrke ved et navn, et navn som ikke er i grunnlaget, et navn to
        ganger, feil antall for resten, feil bransje, råd («bør», «verdt å
        følge», «følg med»), noe om hva som vil skje, eller en årsak."""
        tekst = self.tekst()
        assert fra in tekst
        assert not kontroller_dagen(tekst.replace(fra, til, 1), grunnlaget()).besto

    def test_formene_stoppes_naar_feltet_mangler(self):
        """Ville feilet hvis «Blant dem var», «andre» eller «I snitt»
        besto uten feltet i grunnlaget."""
        g = {n: v for n, v in grunnlaget().items() if n not in (NAVNENE, ANDRE, MEST_OPP, MEST_NED)}
        for tekst in ("Blant dem var Echo (3 av 3, negativ).", "I snitt steg energi mest.", "Og 2 andre."):
            assert not kontroller_dagen(tekst, g).besto, tekst


class TestVersjon6:
    """Del B: teksten om én aksje, med kortere setninger og uten tall som er 0."""

    GRUNNLAG = {
        "trend": 1,
        "bevegelse": 0,
        "interesse": -1,
        "styrke": 2,
        "retning": "Blandet",
        "siste_20_vurdert": 14,
        "siste_20_positiv": 6,
        "siste_20_negativ": 0,
        "siste_20_blandet": 8,
        "siste_20_ingen": 0,
        "siste_5_kunne_telles": 4,
        "siste_5_samme_vei": 0,
        "siste_måned_skift": 2,
    }

    def test_prompten_sier_det(self):
        """Ville feilet hvis prompten manglet regelen om 0, de korte formene,
        eller ordene om råd (NFR-06)."""
        assert PROMPTVERSJON == "6"
        assert "- Tall som er 0, tar du ikke med" in REGLER
        assert "«Bevegelsen ga ikke utslag fordi dagens endring ikke var stor.»" in REGLER
        assert "«bør», «verdt å følge» eller «følg med»" in REGLER

    def test_eksempelteksten_har_ingen_0_og_bestaar(self):
        """Ville feilet hvis teksten tok med «negativt 0», setningen om samme
        vei med 0, eller ikke besto kontrollen."""
        rad = lag_ki_rad(Emne.aksje("EQNR", date(2026, 10, 30)), self.GRUNNLAG, "r", EksempelModell())
        assert rad.besto, rad.grunn
        assert " 0" not in rad.tekst and "samme vei som hovedindeksen" not in rad.tekst
        assert "Av de 14 vurderte børsdagene av de siste 20 var signalet positivt 6 og blandet 8." in rad.tekst
        assert rad.tekst.count(".") == 5

    @pytest.mark.parametrize(
        "setning",
        [
            "Av de 14 vurderte børsdagene av de siste 20 var signalet positivt 6, negativt 0 og blandet 8.",
            "Den siste måneden skiftet retningen 0 ganger.",
        ],
    )
    def test_kontrollen_stopper_0(self, setning):
        """Ville feilet hvis en form med 0 besto (versjon 6)."""
        grunnlag = {**self.GRUNNLAG, "siste_måned_skift": 0}
        svar = kontroller(setning, grunnlag)
        assert not svar.besto and any("0, tas ikke med" in g for g in svar.grunner)

    @pytest.mark.parametrize(("bevegelse", "ord_"), [(1, "steg"), (-1, "falt")])
    def test_den_korte_formen_for_bevegelsen_leses(self, bevegelse, ord_):
        """Ville feilet hvis kontrollen ikke leste den kortere formen, så feil
        fortegn slapp gjennom."""
        tekst = f"Bevegelsen ga et positivt utslag fordi kursen {ord_} mer enn den vanligvis svinger."
        riktig = {**self.GRUNNLAG, "bevegelse": bevegelse}
        galt = {**self.GRUNNLAG, "bevegelse": -bevegelse}
        assert not kontroller(tekst, galt).besto
        if bevegelse == 1:
            assert kontroller(tekst, riktig).besto, kontroller(tekst, riktig).grunner

    @pytest.mark.parametrize("bevegelse", [1, -1, 0])
    def test_eksempelskriverens_form_bestaar_for_hvert_fortegn(self, bevegelse):
        """Gjennomgangen (BH9): ville feilet hvis kontrollen stoppet den
        riktige korte formen for bevegelsen, også den negative og den uten
        utslag."""
        grunnlag = {**self.GRUNNLAG, "bevegelse": bevegelse, "styrke": 2 + abs(bevegelse)}
        grunnlag["retning"] = "Blandet"
        svar = kontroller(tekst_om_aksjen(grunnlag), grunnlag)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize("ord_", ["Den bør følges.", "Den er verdt å følge.", "Følg med på den.", "Den vil stige."])
    def test_raad_og_det_som_vil_skje_stoppes(self, ord_):
        """NFR-06: ville feilet hvis ordene slapp gjennom i teksten om én aksje."""
        tekst = tekst_om_aksjen(self.GRUNNLAG) + " " + ord_
        assert not kontroller(tekst, self.GRUNNLAG).besto


class TestDemoen:
    """Del D: demotekstene fra Gemma i de nye formene, merket som før (FR-602).
    Svaret 11.11 kl. 16:05 (spørsmål 6): Gemma, ikke eksempeltekster, og
    eksempelskriveren er den falske modellen i testene."""

    def test_demotekstene_er_fra_gemma_i_de_nye_formene(self):
        """Ville feilet hvis demoen hadde tekster med en gammel versjon, uten
        de nye formene, med tall som er 0, en tekst som ikke besto, eller en
        annen modell enn Gemma."""
        from ki_lokal import MODELL

        radene = demo_ki.les_radene(prompt=demo_ki.promptavtrykk())
        assert radene and all(r.modell == MODELL and r.besto for r in radene)
        assert all(" 0 " not in r.tekst and " 0." not in r.tekst and " 0," not in r.tekst for r in radene)
        dagen = demo_ki.les_dagsraden(prompt=demo_ki.dagens_promptavtrykk())
        assert dagen.promptversjon == "dag-2" and dagen.modell == MODELL and dagen.besto
        assert "Blant dem var " in dagen.tekst and "I snitt steg " in dagen.tekst

    def test_grunnlaget_er_det_samme_som_den_falske_modellen_faar(self, tmp_path):
        """Ville feilet hvis grunnlaget eller regelen i fila for dagen var
        endret, så demoteksten ikke er laget av demodagen slik den er nå."""
        fil = tmp_path / "dagen.json"
        rad = demo_ki.lag_dagsteksten(EksempelModell(), fil=fil, skriv=lambda _: None)
        lagret = demo_ki.les_dagsraden()
        assert demo_ki.avtrykk(rad) == demo_ki.avtrykk(lagret) and rad.regelen == lagret.regelen
        assert rad.besto and rad.modell == MODELLNAVN

    def test_grunnlagene_for_aksjene_er_de_samme(self, tmp_path):
        """Gjennomgangen (VG8): ville feilet hvis grunnlaget for en av de 13
        tekstene i fila ikke var det demodagen gir nå."""
        radene = demo_ki.lag_tekstene(EksempelModell(), fil=tmp_path / "tekstene.json", skriv=lambda _: None)
        lagret = {r.emne.symbol: demo_ki.avtrykk(r) for r in demo_ki.les_radene()}
        assert {r.emne.symbol: demo_ki.avtrykk(r) for r in radene} == lagret
        assert all(r.besto for r in radene)

    def test_kommandoen_med_eksempel_starter_ikke_ollama(self, tmp_path, monkeypatch):
        """Gjennomgangen (VG8): ville feilet hvis --eksempel likevel brukte
        Ollama, eller ikke skrev teksten om dagen."""
        import ki_lokal

        class IkkeOllama:
            def __init__(self, *args, **kwargs):
                raise AssertionError("--eksempel skal ikke bruke Ollama")

        monkeypatch.setattr(ki_lokal, "OllamaModell", IkkeOllama)
        monkeypatch.setattr(demo_ki, "DAGFIL", tmp_path / "dagen.json")
        lag = demo_ki.lag_dagsteksten
        monkeypatch.setattr(demo_ki, "lag_dagsteksten", lambda modell: lag(modell, fil=tmp_path / "dagen.json"))
        demo_ki.main(["--eksempel", "--dagen"])
        assert demo_ki.les_dagsraden(tmp_path / "dagen.json").modell == MODELLNAVN


def test_spesifikasjonen_sier_hvilke_versjoner_brukertesten_brukte():
    """Del E: ville feilet hvis spesifikasjonen ikke sa at brukertesten 10.4
    ble tatt 10.11 med versjon 5 og dag-1."""
    tekst = SPEC.read_text(encoding="utf-8")
    assert "Brukertesten 10.4 ble tatt 10.11 med promptversjon 5 for teksten om én aksje og dag-1" in tekst


def test_eksempelskriveren_er_ikke_i_webserveren():
    """AD-10: ville feilet hvis webserveren importerte eksempelskriveren."""
    assert "ki_eksempel" not in (ROT / "src" / "app.py").read_text(encoding="utf-8")


def test_prompten_for_en_aksje_kan_leses_av_skriveren():
    """Ville feilet hvis skriveren ikke fant opplysningene og ordlyden i
    prompten, så demoen fikk tekster uten ordlyden om hovedindeksen."""
    grunnlag = {**TestVersjon6.GRUNNLAG, "aksjen": "steg", "hovedindeksen": "steg"}
    tekst = EksempelModell().lag_tekst(lag_prompt(grunnlag)).tekst
    assert "Aksjen gikk samme vei som hovedindeksen." in tekst
