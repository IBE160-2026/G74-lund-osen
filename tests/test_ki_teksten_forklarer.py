"""Story 10.9: KI-teksten forklarer det siden viser (spesifikasjonen
spec-10-9-ki-teksten-forklarer-det-siden-viser.md, med gruppens svar 07.11
kl. 08:58 på spørsmål 1-10).

Del A (datoen i setningen om dagene) testes i test_ki_visning.py, i
TestSetningenOmDagene. Her står delene B-H: de tre mønstrene, rammen
«Signalet forklart», hjelpen ved rammen, promptversjon 5, kontrollen,
demoen og grunnlaget. Ingen nett og ingen modell: demobasen lages i
tmp_path, som i test_designforslaget.py.
"""

import json
import re
import shutil
from datetime import date, datetime, timezone

import pytest

import app as app_modul
import demo
import demo_ki
from ki_grunnlag import ki_grunnlag
from ki_kontroll import kontroller
from ki_prompt import PROMPTVERSJON, REGLER, lag_prompt
from ki_visning import KAPSEL
from kursdata import Kursrad
from lagring_sqlite import demo_sti
from moenstrene import Moenstrene, boersdagene, lag_moenstrene, retningene, samme_vei, skiftene
from vurderingsdata import Grunn, Vurdering

# Torsdag 05.11.2026, og de 25 boersdagene til og med den, den eldste foerst.
DAGEN = date(2026, 11, 5)
DAGENE = boersdagene(DAGEN, 25)[::-1]
FORTEGN = {"Positiv": (1, 0, 0), "Negativ": (-1, 0, 0), "Blandet": (1, -1, 0), "Ingen": (0, 0, 0)}


def _v(retning: str) -> Vurdering:
    trend, bevegelse, interesse = FORTEGN[retning]
    return Vurdering(
        styrke=abs(trend) + abs(bevegelse) + abs(interesse),
        retning=retning,
        trend=trend,
        bevegelse=bevegelse,
        interesse=interesse,
        slutt=101.37,
        justert_slutt=101.37,
        trend_avvik=0.0123,
        dagens_endring=0.0217,
        standardavvik=0.0071,
        volumforhold=1.73,
    )


def _serie(kurser: dict[date, float]) -> list[Kursrad]:
    return [Kursrad(dato=d, slutt=k, justert_slutt=k, volum=1_000_003) for d, k in sorted(kurser.items())]


def _stigende(dager: list[date], start: float = 100.0) -> dict[date, float]:
    return {d: start + i for i, d in enumerate(dager)}


# --- Del B: de tre mønstrene -------------------------------------------------


class TestRetningene:
    def test_dager_som_ikke_er_vurdert_telles_ikke(self):
        """Mønster 1 (spørsmål 3): 14 vurderte av de siste 20, med fire
        grunner og to dager uten rad. En vurdert dag før vinduet telles ikke.
        Ville feilet hvis en dag som er «ikke vurdert», ble talt som en
        retning, eller vinduet var lengre enn 20 børsdager."""
        vinduet = DAGENE[-20:]
        retninger = ["Positiv"] * 6 + ["Negativ"] * 5 + ["Blandet"] * 2 + ["Ingen"]
        radene: dict[date, Vurdering | Grunn] = {d: _v(r) for d, r in zip(vinduet, retninger)}
        for d in vinduet[14:18]:
            radene[d] = Grunn.KURS_IKKE_FRA_DAGEN
        radene[DAGENE[-21]] = _v("Positiv")
        assert retningene(vinduet[-1], radene) == (14, 6, 5, 2, 1)

    def test_faerre_enn_ti_vurderte_gir_ikke_moensteret(self):
        """Ville feilet hvis mønsteret ble gitt med 9 vurderte dager."""
        radene = {d: _v("Positiv") for d in DAGENE[-9:]}
        assert retningene(DAGEN, radene) is None
        radene[DAGENE[-10]] = _v("Negativ")
        assert retningene(DAGEN, radene) == (10, 9, 1, 0, 0)


class TestSammeVei:
    def test_fem_dager_samme_vei(self):
        """Ville feilet hvis en dag der begge steg, ikke ble talt."""
        dager = DAGENE[-6:]
        assert samme_vei(DAGEN, _serie(_stigende(dager)), _serie(_stigende(dager, 1000.0))) == (5, 5)

    def test_en_dag_med_hull_telles_ikke(self):
        """Spørsmål 4: aksjen mangler kurs mandag 02.11, så mandag har ingen
        rad, og tirsdag er regnet mot fredag. Ingen av dem telles. Ville
        feilet hvis en dag med hull ble talt som samme vei."""
        dager = DAGENE[-6:]
        aksjen = _stigende(dager)
        del aksjen[date(2026, 11, 2)]
        assert samme_vei(DAGEN, _serie(aksjen), _serie(_stigende(dager, 1000.0))) == (3, 3)

    def test_en_uendret_dag_telles_ikke(self):
        """Spørsmål 4: en dag der aksjen var uendret, telles ikke, og en dag
        der indeksen falt og aksjen steg, telles uten å være samme vei. Ville
        feilet hvis uendret ble talt, eller motsatt vei ble talt som samme."""
        dager = DAGENE[-6:]
        aksjen = {d: 100.0 + i for i, d in enumerate(dager)}
        aksjen[dager[2]] = aksjen[dager[1]]
        indeksen = _stigende(dager, 1000.0)
        indeksen[dager[-1]] = indeksen[dager[-2]] - 5
        assert samme_vei(DAGEN, _serie(aksjen), _serie(indeksen)) == (4, 3)

    def test_en_dag_der_hovedindeksen_var_uendret_eller_mangler_telles_ikke(self):
        """Spørsmål 4 (gjennomgangen, VG8): ville feilet hvis en dag med
        uendret hovedindeks, eller uten rad i indeksen, ble talt."""
        dager = DAGENE[-6:]
        aksjen = _serie(_stigende(dager))
        uendret = _stigende(dager, 1000.0)
        uendret[dager[2]] = uendret[dager[1]]
        assert samme_vei(DAGEN, aksjen, _serie(uendret)) == (4, 4)
        # Uten rad i indeksen 04.11 kan verken 04.11 eller 05.11 regnes.
        mangler = _stigende(dager, 1000.0)
        del mangler[dager[4]]
        assert samme_vei(DAGEN, aksjen, _serie(mangler)) == (3, 3)

    def test_faerre_enn_tre_gir_ikke_moensteret(self):
        """Ville feilet hvis mønsteret ble gitt med to dager som kunne
        telles, eller uten hovedindeksen."""
        dager = DAGENE[-3:]
        assert samme_vei(DAGEN, _serie(_stigende(dager)), _serie(_stigende(dager, 1000.0))) is None
        assert samme_vei(DAGEN, _serie(_stigende(DAGENE[-6:])), None) is None


class TestSkiftene:
    def test_skift_mellom_vurderte_dager_paa_rad(self):
        """Mønster 3 (spørsmål 5): fra 05.10 til 05.11, som perioden «1 mnd».
        Retningen skifter to ganger. Ville feilet hvis en dag før måneden
        ble talt med, eller et skift ikke ble talt."""
        radene = {d: _v("Positiv") for d in DAGENE}
        radene[date(2026, 10, 2)] = _v("Negativ")
        radene[date(2026, 10, 20)] = _v("Negativ")
        assert skiftene(DAGEN, radene) == (2, False)

    def test_en_dag_som_ikke_er_vurdert_gir_minst(self):
        """Spørsmål 5: en grunn bryter rekka, og skiftet over den telles
        ikke. Ville feilet hvis antallet sto som kjent, eller skiftet over
        grunnen ble talt."""
        radene = {d: _v("Positiv") for d in DAGENE}
        radene[date(2026, 10, 20)] = Grunn.KURS_IKKE_FRA_DAGEN
        radene[date(2026, 10, 21)] = _v("Negativ")
        assert skiftene(DAGEN, radene) == (1, True)

    def test_bare_retningen_telles_ikke_styrken(self):
        """Spørsmål 1 og 5 (gjennomgangen, VG5): mønster 3 teller skift i
        retningen. Positiv med styrke 1 og så styrke 2 er ikke et skift. Ville
        feilet hvis en endring i styrken ble talt."""
        sterkere = Vurdering(**{**_v("Positiv").__dict__, "bevegelse": 1, "styrke": 2})
        radene = {d: _v("Positiv") for d in DAGENE}
        radene[date(2026, 10, 20)] = sterkere
        assert skiftene(DAGEN, radene) == (0, False)

    def test_uten_to_vurderte_dager_paa_rad_gis_ikke_moensteret(self):
        """Ville feilet hvis mønsteret ble gitt uten et eneste par."""
        assert skiftene(DAGEN, {DAGEN: _v("Positiv")}) is None


def test_lag_moenstrene_bruker_vurderingen_for_dagen():
    """Ville feilet hvis vurderingen for dagen ikke var med i mønster 1. De
    20 dagene dekker ikke hele måneden fra 05.10, så skiftene er «minst»."""
    tidligere = {d: _v("Negativ") for d in DAGENE[-20:-1]}
    moenstrene = lag_moenstrene(DAGEN, _v("Positiv"), tidligere, [], None)
    assert moenstrene.retningene == (20, 1, 19, 0, 0)
    assert moenstrene.skiftene == (1, True)
    assert moenstrene.samme_vei is None


# --- Del H: grunnlaget og rettighetene ----------------------------------------

MOENSTRENE = Moenstrene(retningene=(14, 6, 5, 2, 1), samme_vei=(4, 3), skiftene=(2, True))


class TestGrunnlaget:
    def test_bare_heltall_og_tekst_fra_lukkede_lister(self):
        """Del H (beslutningen 04.10): mønstrene er antall dager. Ville
        feilet hvis grunnlaget fikk et desimaltall, en prosent eller en kurs."""
        grunnlag = ki_grunnlag(_v("Positiv"), utenfor_maalingen=False, moenstrene=MOENSTRENE)
        assert dict(grunnlag) == {
            "trend": 1,
            "bevegelse": 0,
            "interesse": 0,
            "styrke": 1,
            "retning": "Positiv",
            "siste_20_vurdert": 14,
            "siste_20_positiv": 6,
            "siste_20_negativ": 5,
            "siste_20_blandet": 2,
            "siste_20_ingen": 1,
            "siste_5_kunne_telles": 4,
            "siste_5_samme_vei": 3,
            "siste_måned_skift": 2,
            "siste_måned_merke": "minst",
        }
        for verdi in grunnlag.values():
            assert type(verdi) is int or verdi in ("Positiv", "minst")

    @pytest.mark.parametrize(
        "moenstrene",
        [
            Moenstrene(retningene=(14, 6, 5, 2, 0), samme_vei=None, skiftene=None),
            Moenstrene(retningene=(9, 9, 0, 0, 0), samme_vei=None, skiftene=None),
            Moenstrene(retningene=None, samme_vei=(2, 2), skiftene=None),
            Moenstrene(retningene=None, samme_vei=(4, 5), skiftene=None),
            Moenstrene(retningene=None, samme_vei=None, skiftene=(1.5, False)),
            Moenstrene(retningene=None, samme_vei=None, skiftene=(-1, False)),
        ],
    )
    def test_et_moenster_som_ikke_kan_stemme_avvises(self, moenstrene):
        """Ville feilet hvis en sum som ikke går opp, et mønster under
        grensen, flere samme vei enn talt, et desimaltall eller et negativt
        tall kom med i grunnlaget."""
        with pytest.raises(ValueError):
            ki_grunnlag(_v("Positiv"), utenfor_maalingen=False, moenstrene=moenstrene)


# --- Del E: promptversjon 5 ----------------------------------------------------


class TestPrompten:
    def test_en_setning_per_sjekk_og_en_om_moenstrene(self):
        """Del E: ville feilet hvis prompten manglet linja om én setning per
        sjekk i fast rekkefølge, eller linja om mønstrene, eller versjonen
        ikke var 5. Da kan to prompter se ut som én i loggen (FR-605).
        Story 10.10: versjon 6 har én kort setning for hvert mønster."""
        assert PROMPTVERSJON == "6"
        reglene = REGLER.split("Regler for teksten:\n", 1)[1].splitlines()
        assert reglene[0].startswith(
            "- Skriv én setning for hver sjekk, i rekkefølgen trend, bevegelse og interesse. "
            "Si med vanlige ord hva sjekken måler og hva den ga"
        )
        assert any(linje.startswith("- Etter sjekkene kommer én kort setning for hvert mønster") for linje in reglene)
        assert any("ikke finn mønstre selv" in linje for linje in reglene)

    def test_moenstrene_kommer_med_i_prompten(self):
        """Ville feilet hvis antallene ikke kom med i opplysningene."""
        grunnlag = ki_grunnlag(_v("Positiv"), utenfor_maalingen=False, moenstrene=MOENSTRENE)
        opplysningene = lag_prompt(grunnlag).split("Opplysningene:\n", 1)[1].splitlines()[0]
        assert json.loads(opplysningene)["siste_20_positiv"] == 6


# --- Del F: kontrollen ------------------------------------------------------------

SJEKKENE = (
    "Kursen ligger over snittet for de siste 50 børsdagene, så trenden ga et positivt utslag. "
    "Dagens endring var ikke stor sammenlignet med de siste 20 dagene, så bevegelsen ga ikke utslag. "
    "Det ble ikke handlet mer enn vanlig, så interessen ga ikke utslag. "
)
MOENSTERSETNINGEN = (
    "Av de 14 vurderte børsdagene av de siste 20 var signalet positivt 6, negativt 5, blandet 2 og "
    "uten retning 1, aksjen gikk samme vei som hovedindeksen 3 av de 4 dagene som kunne telles av de "
    "siste 5 børsdagene, og den siste måneden skiftet retningen minst 2 ganger."
)


class TestKontrollen:
    @pytest.fixture
    def grunnlag(self):
        return ki_grunnlag(_v("Positiv"), utenfor_maalingen=False, moenstrene=MOENSTRENE)

    def test_setningen_om_moenstrene_bestaar_med_tallene_fra_grunnlaget(self, grunnlag):
        """Ville feilet hvis formene i prompten ble stoppet når tallene
        stemmer."""
        svar = kontroller(SJEKKENE + MOENSTERSETNINGEN, grunnlag)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "feil",
        [
            ("positivt 6, negativt 5", "positivt 5, negativt 6"),
            ("3 av de 4 dagene", "4 av de 3 dagene"),
            ("minst 2 ganger", "2 ganger"),
            ("Av de 14 vurderte børsdagene av de siste 20", "Av de siste 20 børsdagene"),
        ],
    )
    def test_et_tall_ved_feil_felt_stoppes(self, grunnlag, feil):
        """Ville feilet hvis en tekst med byttede antall, uten «minst» når
        antallet er det minste, eller uten antallet vurderte dager besto."""
        assert not kontroller(SJEKKENE + MOENSTERSETNINGEN.replace(*feil), grunnlag).besto

    @pytest.mark.parametrize(
        "tekst",
        [
            "Aksjen pleier å stige etter slike dager.",
            "Det er en tendens til positive signaler.",
            "Signalet er oftere positivt enn negativt.",
            "Mønsteret gjentar seg.",
            "Av de 14 vurderte børsdagene av de siste 20 var signalet positivt 7.",
            "Av de ‹siste_20_vurdert› vurderte børsdagene var signalet positivt siste_20_positiv.",
        ],
    )
    def test_et_moenster_modellen_finner_selv_stoppes(self, grunnlag, tekst):
        """Del F: ville feilet hvis en tekst som sa at aksjen «pleier» å gå
        opp, et tall som ikke er i grunnlaget, eller et feltnavn fra
        formene i prompten besto."""
        assert not kontroller(SJEKKENE + tekst, grunnlag).besto

    def test_uten_moenstrene_i_grunnlaget_stoppes_setningen(self):
        """Ville feilet hvis setningen besto når grunnlaget ikke har
        mønstrene: da finner modellen dem selv."""
        grunnlag = ki_grunnlag(_v("Positiv"), utenfor_maalingen=False)
        assert not kontroller(SJEKKENE + MOENSTERSETNINGEN, grunnlag).besto

    def test_et_moenstertall_i_en_annen_form_stoppes(self, grunnlag):
        """Ville feilet hvis «ganger» og «måneden» besto utenfor formen."""
        assert not kontroller(SJEKKENE + "Retningen har vært den samme i 2 ganger denne måneden.", grunnlag).besto

    @pytest.mark.parametrize(
        "tekst",
        [
            # ECH1: en retning for hele signalet ved et tall som er en telling.
            "Signalet er positivt i to av tre sjekker.",
            # ECH2, ECH3, BH3: vinduet og måneden utenfor setningen om mønstrene.
            "Signalet har vært negativt de siste 20 børsdagene.",
            "Retningen har ikke skiftet den siste måneden.",
            "Den siste måneden har kursen ligget over snittet.",
            # ECH4, ECH6, ECH12: mer enn formene i setningen om mønstrene.
            "Av de 14 vurderte børsdagene var 5 positive og 6 negative.",
            "Av de 14 vurderte børsdagene var signalet oftest positivt.",
            "Av de 14 vurderte børsdagene var signalet positivt 6, flere enn negativt 5.",
            "Det stemmer ikke at aksjen gikk samme vei som hovedindeksen 3 av de 4 dagene som kunne telles.",
            # ECH5, BH2: en telling er ikke et lovlig tall utenfor formene.
            "Kursen ligger 14 over snittet.",
            # ECH7: skiftene uten «den siste måneden».
            "Retningen skiftet minst 2 ganger i dag.",
            # VG2: tallet i mønster 3.
            "Den siste måneden skiftet retningen minst 7 ganger.",
            # BH4, VG3: bøyningene og ord om hvor ofte.
            "Aksjen pleide å stige etter slike dager.",
            "Mønstrene viser at signalet er positivt.",
            "Signalet er vanligvis positivt.",
            "Signalet har stort sett vært positivt.",
            "Retningen skifter hyppig.",
        ],
    )
    def test_funnene_fra_gjennomgangen_stoppes(self, grunnlag, tekst):
        """Gjennomgangen av 10.9 (ECH1-ECH7, ECH12, BH2-BH4, VG2, VG3): ville
        feilet hvis formene ble tatt ut utenfor setningen om mønstrene, eller
        noe mer enn formene sto i den setningen."""
        assert not kontroller(SJEKKENE + tekst, grunnlag).besto, tekst

    def test_formene_med_minst_foer_verbet_og_markdown_bestaar(self, grunnlag):
        """ECH10, ECH11: ville feilet hvis «minst» foran verbet eller fet skrift
        med __ ble stoppet."""
        tekst = MOENSTERSETNINGEN.replace("skiftet retningen minst 2 ganger", "har retningen minst skiftet 2 ganger")
        assert kontroller(SJEKKENE.replace("så trenden", "så __trenden__") + tekst, grunnlag).besto

    def test_mønster_3_uten_moensteret_i_grunnlaget_stoppes(self):
        """BH10, VG7: med bare faste tall i setningen. Ville feilet hvis formen
        besto når grunnlaget ikke har mønster 3."""
        grunnlag = ki_grunnlag(_v("Positiv"), utenfor_maalingen=False)
        assert not kontroller(SJEKKENE + "Den siste måneden skiftet retningen 3 ganger.", grunnlag).besto
        assert not kontroller(SJEKKENE + "Aksjen gikk samme vei som hovedindeksen 3 av de 3 dagene.", grunnlag).besto


class TestMaalingen:
    """Del F, gjennomgangen (VG1, BH1, BH5, BH6, ECH8, ECH9): ordene om
    målingen mot fortegnet for sjekken."""

    GRUNNLAG = {"trend": 1, "bevegelse": -1, "interesse": 0, "styrke": 2, "retning": "Blandet"}

    @pytest.mark.parametrize(
        "tekst",
        [
            "Det ble ikke handlet mye mer enn vanlig.",
            "Kursen ligger over snittet for de siste 50 børsdagene.",
            "Kursen falt mer i dag enn den vanligvis svinger de siste 20 dagene.",
            "Kursen ligger ikke under snittet.",
            "Kursen ligger ikke nær snittet.",
            "Trenden måler om kursen ligger over eller under snittet for de siste 50 børsdagene.",
            "Kursen steg ikke mer enn vanlig.",
        ],
    )
    def test_det_som_stemmer_bestaar(self, tekst):
        """Ville feilet hvis en sann setning om målingen ble stoppet."""
        svar = kontroller(tekst, self.GRUNNLAG)
        assert svar.besto, svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        [
            "Det ble handlet mer enn vanlig på en dag kursen falt.",
            "Kursen ligger under snittet for de siste 50 børsdagene.",
            "Kursen ligger nær snittet.",
            "Kursen steg mer i dag enn den vanligvis svinger.",
            "Kursen falt ikke mer enn vanlig.",
            "Dagens endring var ikke stor.",
            "Dagens endring var liten.",
        ],
    )
    def test_det_som_strider_mot_fortegnet_stoppes(self, tekst):
        """Ville feilet hvis kontrollen ikke leste målingen, som i den første
        kjøringen av demotekstene (§56), eller ikke leste «ikke»."""
        assert not kontroller(tekst, self.GRUNNLAG).besto, tekst


# --- Del C og D: rammen «Signalet forklart» og hjelpen ved den ---------------------


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def klient(mal, monkeypatch):
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    return app_modul.app.test_client()


def _rammen(klient, kapsel: str | None) -> str:
    if kapsel is not None:
        klient.set_cookie(KAPSEL, kapsel)
    html = klient.get("/aksje/BRFE").get_data(as_text=True)
    return html.split('<section class="ki"', 1)[1].split("</section>", 1)[0]


class TestRammen:
    @pytest.mark.parametrize("kapsel", [None, "av"])
    def test_bryteren_staar_fast_oeverst_til_hoeyre(self, klient, kapsel):
        """Del C (svarene 06.11 kl. 22:16 og 22:23, U78): bryteren står i
        toppen av rammen, rett etter tittelen, både med KI på og av. Ville
        feilet hvis bryteren byttet plass når KI slås av."""
        rammen = _rammen(klient, kapsel)
        topp = rammen.split('<div class="ki-topp">', 1)[1].split("</div>", 1)[0]
        assert topp.index("</h2>") < topp.index('<form class="ki-bryter"')
        assert rammen.count('class="ki-bryter"') == 1

    def test_med_ki_av_staar_appens_setninger_i_rammen(self, klient):
        """Del C: med KI av står rammen med appens setninger og bryteren,
        uten KI-tekst. Ville feilet hvis bare bryteren sto, som før."""
        rammen = _rammen(klient, "av")
        assert '<p class="dagene">' in rammen and 'class="ki-tekst"' not in rammen
        # Gjennomgangen (VG11): også setningen om samme dag.
        assert '<p class="samme-dag">' in rammen

    def test_appens_setninger_foer_ki_teksten(self, klient):
        """Del C: ville feilet hvis KI-teksten sto før appens setninger."""
        rammen = _rammen(klient, None)
        assert rammen.index('<p class="dagene">') < rammen.index('<p class="ki-tekst">')


def test_hjelpen_ved_rammen_har_hoeyst_60_ord(klient):
    """Del D (svaret 06.11 kl. 23:07, spørsmål 10): vinduet ved rammen har
    høyst 60 ord, telt med \\w+ over tittelen og teksten, også med KI av.
    Ville feilet med hjelpen fra «kort fortalt», som hadde 149 ord. De andre
    vinduene rettes i 8.20a."""
    for kapsel in (None, "av"):
        if kapsel:
            klient.set_cookie(KAPSEL, kapsel)
        html = klient.get("/aksje/BRFE").get_data(as_text=True)
        vinduet = html.split('<div id="hjelp-ki" class="hjelpevindu" popover>', 1)[1].split("</div>\n", 2)[1]
        tekst = re.sub(r"<[^>]+>", " ", vinduet.split('<p class="vist">')[0])
        assert len(re.findall(r"\w+", tekst)) <= 60, tekst


# --- Del G: demoen ------------------------------------------------------------------


def test_demotekstene_har_versjon_5_og_moenstrene():
    """Del G: demotekstene er laget på nytt med versjon 5, og grunnlaget har
    mønster 1 med færre enn 20 vurderte dager, fordi vurderingene i demoen
    starter 21.09. Ville feilet hvis en demotekst med versjon 4 sto igjen.
    Story 10.10: demotekstene har versjon 6, som eksempeltekster."""
    radene = demo_ki.les_radene(prompt=demo_ki.promptavtrykk())
    assert radene and all(rad.promptversjon == "6" for rad in radene)
    assert all(10 <= rad.grunnlag["siste_20_vurdert"] < 20 for rad in radene)
