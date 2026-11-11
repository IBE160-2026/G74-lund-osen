"""Story 10.10, tillegget etter gruppens svar 11.11 kl. 17:21 - FR-603,
FR-607, NFR-06, AD-8.

Tre nye deler i teksten om børsdagen: Min liste (en linje appen skriver,
spørsmål 10), flere eller færre enn vanlig (spørsmål 11) og hovedindeksen
siste uke (spørsmål 12). Eksempelskriveren i ki_eksempel.py er den falske
modellen (AD-8), og ingen test kaller Ollama eller EODHD.
"""

from datetime import date

import pytest

from dagsgrunnlag import (
    FAERRE,
    FLERE,
    LIKE_MANGE,
    MOT_VANLIG,
    NYE_FELT,
    UKA,
    VANLIG,
    dagene_foer,
    dagsgrunnlag,
    for_promptversjon,
    min_liste_linje,
    uka_for_hovedindeksen,
    vanlig,
    vanlig_fra,
)
from ki_dagen import REGLER_DAGEN, dagsregel, kontroller_dagen, lag_dagsrad
from ki_eksempel import EksempelModell, tekst_om_dagen
from kilogg import Emne
from kursdata import Aksje, Kursrad
from test_rikere_ki_tekster import vurdering
from vurderingsdata import Grunn

FREDAG = date(2026, 10, 30)
# De fem boersdagene foer fredag 30.10: torsdag 29.10 tilbake til fredag 23.10.
DAGENE = [date(2026, 10, d) for d in (23, 26, 27, 28, 29, 30)]


def rad(dag: date, kurs: float) -> Kursrad:
    return Kursrad(dato=dag, slutt=kurs, justert_slutt=kurs, volum=1000)


LISTA = tuple(
    Aksje(f"S{i}", f"S{i}.OL", navn, "Energi")
    for i, navn in enumerate("Alfa Bravo Charlie Delta Echo Foxtrot Golf".split())
)


def historikk(antall_per_dag: list[int]) -> dict:
    """Tidligere vurderinger med antall_per_dag aksjer som skilte seg ut, én
    dag per tall, for de børsdagene som kommer rett før FREDAG."""
    dager = dagene_foer(FREDAG, len(antall_per_dag))
    tidligere: dict[str, dict] = {a.symbol: {} for a in LISTA}
    for d, n in zip(dager, antall_per_dag, strict=True):
        for i, a in enumerate(LISTA):
            tidligere[a.symbol][d] = vurdering(2, "Positiv") if i < n else vurdering(1, "Positiv")
    return tidligere


class TestVanlig:
    """Spørsmål 11: antallet mot snittet for de siste 20 børsdagene."""

    @pytest.mark.parametrize(("antall", "mot"), [(3, FLERE), (1, FAERRE), (2, LIKE_MANGE)])
    def test_flere_faerre_eller_like_mange(self, antall, mot):
        """Ville feilet hvis flere, færre og like mange ble byttet om."""
        assert vanlig(FREDAG, LISTA, historikk([2] * 12), antall) == {VANLIG: 2, MOT_VANLIG: mot}

    def test_sammenlignes_med_det_rundede_snittet(self):
        """Gjennomgangen (VG3): snittet 2,5 står som 3, og 3 er da like mange.
        Ville feilet med sammenligning mot det uavrundede snittet (flere)."""
        assert vanlig(FREDAG, LISTA, historikk([2, 3] * 6), 3) == {VANLIG: 3, MOT_VANLIG: LIKE_MANGE}

    def test_halve_opp_og_ikke_alltid_opp(self):
        """Gjennomgangen (VG3): 2,25 rundes til 2. Ville feilet med math.ceil."""
        assert vanlig(FREDAG, LISTA, historikk([2, 2, 2, 3] * 3), 2)[VANLIG] == 2

    def test_vinduet_er_noeyaktig_20_boersdager(self):
        """Gjennomgangen (BH4, VG5): ville feilet med et vindu på 19 eller 21
        dager. 21 dager med 7, 7 og så 0: 20 dager gir 7/20 = 0,35, altså 0,
        mens 21 ville gitt 14/21 = 0,67, altså 1. 20 dager med 6, 6 og så 0:
        20 dager gir 12/20 = 0,6, altså 1, mens 19 ville gitt 6/19, altså 0."""
        assert vanlig(FREDAG, LISTA, historikk([7, 7] + [0] * 19), 0)[VANLIG] == 0
        assert vanlig(FREDAG, LISTA, historikk([6, 6] + [0] * 18), 0)[VANLIG] == 1

    def test_minst_10_vurderte_dager(self):
        """Gjennomgangen (VG5): ville feilet med en annen grense enn 10."""
        assert vanlig(FREDAG, LISTA, historikk([2] * 9), 3) == {}
        assert vanlig(FREDAG, LISTA, historikk([2] * 10), 3) == {VANLIG: 2, MOT_VANLIG: FLERE}

    def test_en_dag_uten_vurdering_telles_ikke(self):
        """Gjennomgangen (BH3, VG4): 14 dager med 3, der 4 er uten vurdering,
        gir 3. Ville feilet hvis de 4 dagene telte som 0 (30/14 = 2,1, altså 2)."""
        tidligere = historikk([3] * 14)
        for d in sorted(tidligere["S0"])[:4]:
            for a in LISTA:
                tidligere[a.symbol][d] = Grunn.SYMBOL_FEILET
        assert vanlig(FREDAG, LISTA, tidligere, 3) == {VANLIG: 3, MOT_VANLIG: LIKE_MANGE}

    def test_lesingen_begynner_ved_vinduet(self):
        """Gjennomgangen (BH6): ville feilet hvis hentingen og forsiden leste
        fra en annen dag enn den første i vinduet."""
        assert vanlig_fra(FREDAG) == dagene_foer(FREDAG, 20)[0] == date(2026, 10, 2)


class TestUka:
    """Spørsmål 12: hovedindeksen de siste fem børsdagene, bare retningen."""

    @pytest.mark.parametrize(("slutt", "ventet"), [(1010, "steg"), (990, "falt"), (1000.00001, "uendret")])
    def test_retningen(self, slutt, ventet):
        """Ville feilet hvis endringen ble regnet fra en annen dag enn fem
        børsdager før, eller ikke slik den vises."""
        serie = [rad(DAGENE[0], 1000)] + [rad(d, 5000) for d in DAGENE[1:5]] + [rad(FREDAG, slutt)]
        assert uka_for_hovedindeksen(serie, FREDAG) == ventet

    def test_uten_rad_paa_dagen_eller_fem_boersdager_foer(self):
        """Gjennomgangen (VG6): ville feilet hvis appen brukte en annen dag, eller
        reiste KeyError, når en av de to dagene mangler."""
        assert uka_for_hovedindeksen([rad(d, 1000) for d in DAGENE[1:]], FREDAG) is None
        assert uka_for_hovedindeksen([rad(d, 1000) for d in DAGENE[:-1]], FREDAG) is None

    def test_over_en_helligdag(self):
        """Gjennomgangen (VG6): fredag 8.5.2026, og 1.5 er stengt, så fem
        børsdager før er torsdag 30.4. Ville feilet med ukedager i stedet for
        børsdager (da ville det vært fredag 1.5)."""
        fredag = date(2026, 5, 8)
        assert dagene_foer(fredag, 5)[0] == date(2026, 4, 30)
        serie = [rad(date(2026, 4, 30), 1000), rad(fredag, 1010)]
        assert uka_for_hovedindeksen(serie, fredag) == "steg"

    def test_grunnlaget_har_feltet(self):
        serie = [rad(d, 1000) for d in DAGENE[:-1]] + [rad(FREDAG, 1010)]
        vurderinger = {a.symbol: vurdering(2, "Positiv") for a in LISTA}
        serier = {a.symbol: [rad(DAGENE[-2], 100), rad(FREDAG, 101)] for a in LISTA}
        assert dagsgrunnlag(FREDAG, LISTA, vurderinger, serier, serie)[UKA] == "steg"


class TestMinListe:
    """Spørsmål 10: en linje appen skriver av lista slik den er nå."""

    VURDERINGER = {"S0": vurdering(2, "Positiv"), "S1": vurdering(3, "Negativ"), "S2": vurdering(1, "Positiv")}

    def test_navnene_med_3_av_3_foerst(self):
        """Ville feilet hvis linja tok med en aksje utenfor Min liste, eller
        brukte andre regler for navnene enn teksten."""
        linja = min_liste_linje(LISTA, self.VURDERINGER, {"S0", "S1", "S2"})
        assert linja == "I Min liste skilte Bravo (3 av 3, negativ) og Alfa (2 av 3, positiv) seg ut."
        assert min_liste_linje(LISTA, self.VURDERINGER, {"S0"}) == "I Min liste skilte Alfa (2 av 3, positiv) seg ut."

    def test_hoeyst_fem_navn_og_resten_som_antall(self):
        """Gjennomgangen (VG8): ville feilet uten kuttet ved fem og «og N andre»."""
        alle = {a.symbol: vurdering(2, "Positiv") for a in LISTA}
        linja = min_liste_linje(LISTA, alle, {a.symbol for a in LISTA})
        assert linja.count("(2 av 3, positiv)") == 5
        assert linja.endswith("Echo (2 av 3, positiv) og 2 andre seg ut.")

    def test_ingen_skilte_seg_ut(self):
        """Ville feilet hvis linja manglet når ingen i Min liste skilte seg ut."""
        assert min_liste_linje(LISTA, self.VURDERINGER, {"S2"}) == "Ingen av aksjene i Min liste skilte seg ut."

    def test_ingen_linje_uten_vurderte_i_min_liste(self):
        """Ville feilet hvis linja sto når Min liste er tom, ingen av dem er
        vurdert, eller de merkede ikke er i lista."""
        assert min_liste_linje(LISTA, self.VURDERINGER, set()) is None
        assert min_liste_linje(LISTA, {"S0": Grunn.SYMBOL_FEILET}, {"S0"}) is None
        assert min_liste_linje(LISTA, self.VURDERINGER, {"ANNEN"}) is None

    def test_min_liste_er_ikke_i_grunnlaget(self):
        """FR-607: ville feilet hvis Min liste var med i grunnlaget, så teksten
        forsvant når lista endres."""
        serier = {a.symbol: [rad(DAGENE[-2], 100), rad(FREDAG, 101)] for a in LISTA}
        g = dagsgrunnlag(FREDAG, LISTA, self.VURDERINGER, serier, None)
        assert not any("min" in n.lower() for n in g)


class TestKontrollen:
    """FR-603: de nye formene, tall for tall."""

    GRUNNLAG = {
        "aksjer": 3,
        "ukedag": "fredag",
        "skilte_seg_ut": 3,
        "skilte_seg_ut_positiv": 3,
        "skilte_seg_ut_negativ": 0,
        "skilte_seg_ut_blandet": 0,
        VANLIG: 2,
        MOT_VANLIG: FLERE,
        UKA: "falt",
    }

    @pytest.mark.parametrize(("mot", "uka"), [(FLERE, "falt"), (FAERRE, "steg"), (LIKE_MANGE, "uendret")])
    def test_eksempelteksten_bestaar(self, mot, uka):
        """Gjennomgangen (VG7): ville feilet hvis en av formene for «flere»,
        «færre», «like mange» og uka ikke ble lest av kontrollen."""
        g = {**self.GRUNNLAG, MOT_VANLIG: mot, UKA: uka}
        tekst = tekst_om_dagen(g)
        svar = kontroller_dagen(tekst, g)
        assert svar.besto, (tekst, svar.grunner)
        annen = {"falt": "steg", "steg": "falt", "uendret": "steg"}[uka]
        assert not kontroller_dagen(tekst, {**g, UKA: annen}).besto

    def test_formene(self):
        tekst = tekst_om_dagen(self.GRUNNLAG)
        assert "Det var flere enn vanlig: snittet de siste 20 børsdagene er 2." in tekst
        assert "De siste fem børsdagene falt hovedindeksen." in tekst

    @pytest.mark.parametrize(
        ("fra", "til"),
        [
            ("flere enn vanlig", "færre enn vanlig"),
            ("er 2.", "er 3."),
            ("falt hovedindeksen", "steg hovedindeksen"),
            ("De siste fem børsdagene falt hovedindeksen.", "De siste fem børsdagene falt hovedindeksen 2,1 %."),
            ("De siste fem børsdagene falt hovedindeksen.", "Neste uke vil den stige."),
        ],
    )
    def test_feil_stoppes(self, fra, til):
        """Ville feilet hvis kontrollen slapp gjennom feil sammenligning, feil
        snitt, feil retning for uka, en prosent eller noe om hva som vil skje."""
        tekst = tekst_om_dagen(self.GRUNNLAG)
        assert fra in tekst
        assert not kontroller_dagen(tekst.replace(fra, til), self.GRUNNLAG).besto

    @pytest.mark.parametrize("felt", [VANLIG, UKA])
    def test_formen_stoppes_naar_feltet_mangler(self, felt):
        """Ville feilet hvis formen besto uten feltet i grunnlaget."""
        tekst = tekst_om_dagen(self.GRUNNLAG)
        uten = {n: v for n, v in self.GRUNNLAG.items() if n != felt and not (felt == VANLIG and n == MOT_VANLIG)}
        svar = kontroller_dagen(tekst, uten)
        assert not svar.besto and any(f"{felt} mangler" in g for g in svar.grunner), svar.grunner

    def test_prompten_og_regelen(self):
        """Ville feilet hvis prompten manglet formene, eller regelen i loggen
        (FR-604) manglet de nye feltene."""
        assert "«Det var flere enn vanlig: snittet de siste 20 børsdagene er ‹skilte_seg_ut_vanlig›.»" in REGLER_DAGEN
        assert "«De siste fem børsdagene steg hovedindeksen.»" in REGLER_DAGEN
        regelen = dagsregel(self.GRUNNLAG)
        assert "Mot vanlig: flere, snittet 2." in regelen and "Hovedindeksen siste fem børsdager: falt." in regelen

    def test_raden_med_falsk_modell(self):
        """Ville feilet hvis raden fra hentingen ikke besto med de nye formene."""
        rad_ = lag_dagsrad(Emne.dagen(FREDAG), self.GRUNNLAG, EksempelModell())
        assert rad_.besto, rad_.grunn


def test_dag_1_uten_de_nye_feltene():
    """Spørsmål 5: ville feilet hvis en rad med dag-1 ble sammenlignet med de
    nye feltene, så tekstene fra før flettingen forsvant."""
    assert {VANLIG, MOT_VANLIG, UKA} <= set(NYE_FELT)
    assert not ({VANLIG, MOT_VANLIG, UKA} & set(for_promptversjon(dict(TestKontrollen.GRUNNLAG), "dag-1")))


@pytest.mark.parametrize(
    "setning",
    ["Det var flere enn vanlig: snittet de siste 20 børsdagene er 2.", "De siste fem børsdagene falt hovedindeksen."],
)
def test_hver_ny_form_bare_en_gang(setning):
    """Gjennomgangen av tillegget (ECH1): ville feilet hvis en av de nye
    setningene kunne stå to ganger."""
    tekst = tekst_om_dagen(TestKontrollen.GRUNNLAG) + " " + setning
    svar = kontroller_dagen(tekst, TestKontrollen.GRUNNLAG)
    assert not svar.besto and any("mer enn én gang" in g for g in svar.grunner), svar.grunner


def test_linja_om_min_liste_har_egen_stil():
    """Gjennomgangen av tillegget (ECH3): ville feilet hvis linja appen skriver
    sto uten stil, så den ikke skilte seg fra KI-teksten."""
    from pathlib import Path

    stil = (Path(__file__).resolve().parents[1] / "src" / "static" / "stil.css").read_text(encoding="utf-8")
    assert ".boersdagen p.min-liste-linje {" in stil and ".boersdagen .merke-app {" in stil


class TestSvaret1930:
    """Svaret 11.11 kl. 19:30: formen for én bransje bare uten «mest», og
    rekkefølgen i reglene."""

    MED_MEST = {
        **TestKontrollen.GRUNNLAG,
        "bransjer": {"Energi": {"steg": 1, "med_endring": 2}},
        "bransje_mest_opp": "Energi",
    }
    UTEN_MEST = {**TestKontrollen.GRUNNLAG, "bransjer": {"Energi": {"steg": 1, "med_endring": 2}}}

    def test_formen_for_en_bransje_er_ikke_i_reglene_med_mest(self):
        """Ville feilet hvis reglene hadde formen «I ‹bransje› steg …» når
        bransjen som steg eller falt mest kan stå, eller manglet den uten."""
        from ki_dagen import BRANSJEFORMEN, lag_dagsprompt

        assert BRANSJEFORMEN not in lag_dagsprompt(self.MED_MEST)
        assert BRANSJEFORMEN not in lag_dagsprompt({**self.UTEN_MEST, "bransje_mest_ned": "Energi"})
        assert BRANSJEFORMEN in lag_dagsprompt(self.UTEN_MEST)
        assert "{bransjeformen}" not in lag_dagsprompt(self.MED_MEST) + lag_dagsprompt(self.UTEN_MEST)

    def test_kontrollen_stopper_formen_med_mest(self):
        """Ville feilet hvis «I energi steg 1 av 2 aksjer.» besto når bransjen
        som steg mest står i grunnlaget."""
        svar = kontroller_dagen("I energi steg 1 av 2 aksjer.", self.MED_MEST)
        assert not svar.besto and any("falt mest kan stå" in g for g in svar.grunner), svar.grunner
        assert kontroller_dagen("I energi steg 1 av 2 aksjer.", self.UTEN_MEST).besto

    def test_rekkefoelgen_i_reglene(self):
        """Ville feilet hvis formene sto i en annen rekkefølge enn i svaret:
        hovedindeksen, fem børsdager, bedre enn indeksen, skilte seg ut, vanlig,
        navnene og bransjene."""
        from ki_dagen import lag_dagsprompt

        regler = lag_dagsprompt(self.UTEN_MEST)
        merker = [
            "«Hovedindeksen steg ‹ukedag›.»",
            "«De siste fem børsdagene steg hovedindeksen.»",
            "«‹bedre_enn_indeksen› av ‹med_kurs›",
            "«‹skilte_seg_ut› skilte seg ut:",
            "«Det var flere enn vanlig:",
            "«Blant dem var ‹navn›",
            "«I snitt steg ‹bransje_mest_opp› mest.»",
            "«I ‹bransje› steg ‹steg›",
        ]
        plasser = [regler.index(m) for m in merker]
        assert plasser == sorted(plasser)

    def test_eksempelskriveren_foelger_rekkefoelgen(self):
        """Ville feilet hvis den falske modellen skrev formene i en annen
        rekkefølge enn reglene."""
        tekst = tekst_om_dagen({**self.MED_MEST, "hovedindeksen": "steg"})
        deler = ["Hovedindeksen steg", "De siste fem", "skilte seg ut:", "Det var flere", "I snitt steg"]
        plasser = [tekst.index(d) for d in deler]
        assert plasser == sorted(plasser)
