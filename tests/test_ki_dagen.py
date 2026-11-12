"""Story 10.6: KI-teksten om dagen på forsiden - FR-601, FR-603, FR-604,
FR-605, FR-607, NFR-02, NFR-06, AD-8, AD-10.

Spesifikasjonen er spec-10-6-ki-teksten-om-dagen-paa-forsiden.md. Testene
bruker en falsk modell (AD-8), og ingen test kaller Ollama eller EODHD.
"""

import hashlib
import inspect
import json
from datetime import date, datetime, timedelta

import pytest

import app as app_modul
import ki_dagen
import lagring_sqlite
from dagsgrunnlag import dagsgrunnlag
from hjelpetekster import hjelpetekster
from ki_dagen import DAGSPROMPTVERSJON, REGLER_DAGEN, kontroller_dagen, lag_dagsprompt, lag_dagsrad
from ki_modell import ModellFeilet, Modellsvar
from ki_visning import DAGEN_AV, DAGEN_UTEN, KAPSEL, PERIODEN_UTEN, bygg_dagsvisning
from kilogg import Emne, KIRad
from kursdata import Aksje, Kursrad
from lagring_sqlite import SqliteKILogg, aapne_base
from test_app import HENTET, skriv_serie, skriv_vurdering
from test_ki_tekst import TIRSDAG, FalskModell, kjoer
from test_ki_visning import skriv_kirad
from vurderingsdata import Grunn, Vurdering

# Fredag 30.10.2026, en boersdag, og torsdagen foer.
FREDAG = date(2026, 10, 30)
TORSDAG = date(2026, 10, 29)


def vurdering(styrke: int, retning: str) -> Vurdering:
    trend, bevegelse, interesse = {
        (0, "Ingen"): (0, 0, 0),
        (1, "Positiv"): (1, 0, 0),
        (2, "Positiv"): (1, 1, 0),
        (2, "Negativ"): (-1, -1, 0),
        (2, "Blandet"): (1, -1, 0),
        (3, "Positiv"): (1, 1, 1),
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


LISTA = (
    Aksje("AAA", "AAA.OL", "A", "Energi"),
    Aksje("BBB", "BBB.OL", "B", "Energi"),
    Aksje("CCC", "CCC.OL", "C", "Finans"),
    Aksje("DDD", "DDD.OL", "D", "Sjømat"),
)
SERIER = {
    "AAA": to_dager(100, 103),
    "BBB": to_dager(100, 98),
    "CCC": to_dager(100, 101),
    "DDD": to_dager(100, 100.4),
}
INDEKS = to_dager(1000, 1005)
VURDERINGER = {
    "AAA": vurdering(3, "Positiv"),
    "BBB": vurdering(2, "Negativ"),
    "CCC": vurdering(1, "Positiv"),
    "DDD": Grunn.SYMBOL_FEILET,
}


def grunnlaget(**endret):
    felt = dict(dag=FREDAG, lista=LISTA, vurderinger=VURDERINGER, serier=SERIER, indeksserie=INDEKS)
    felt.update(endret)
    return dagsgrunnlag(**felt)


class TestGrunnlaget:
    """Del A."""

    def test_feltene(self):
        """Ville feilet hvis grunnlaget talte feil: hovedindeksen steg 0,5,
        AAA og CCC gjorde det bedre, AAA og BBB skilte seg ut (styrke 2 og 3),
        og bare Energi har to aksjer med endring. Story 10.10: navnene, A
        med 3 av 3 foerst, og Energi med snittet 0,5 som bransjen som steg
        mest; ingen bransje falt."""
        assert dict(grunnlaget()) == {
            "aksjer": 4,
            "ukedag": "fredag",
            "hovedindeksen": "steg",
            "bedre_enn_indeksen": 2,
            "med_kurs": 4,
            "skilte_seg_ut": 2,
            "skilte_seg_ut_positiv": 1,
            "skilte_seg_ut_negativ": 1,
            "skilte_seg_ut_blandet": 0,
            "skilte_seg_ut_navn": [
                {"navn": "A", "styrke": 3, "retning": "positiv"},
                {"navn": "B", "styrke": 2, "retning": "negativ"},
            ],
            "bransjer": {"Energi": {"steg": 1, "med_endring": 2}},
            "bransje_mest_opp": "Energi",
        }

    def test_bare_heltall_og_tekst(self):
        """Ville feilet hvis grunnlaget fikk et desimaltall, en prosent eller
        en kurs (beslutningen 04.10, FR-607 rettet 05.10)."""

        def verdier(verdi):
            if isinstance(verdi, dict) or hasattr(verdi, "items"):
                for v in verdi.values():
                    yield from verdier(v)
            elif isinstance(verdi, (list, tuple)):
                # Story 10.10: navnene er en liste.
                for v in verdi:
                    yield from verdier(v)
            else:
                yield verdi

        for verdi in verdier(grunnlaget()):
            assert type(verdi) in (int, str)

    @pytest.mark.parametrize("antall", [3, 18])
    def test_antallet_er_lista_som_er_aktiv(self, antall):
        """Tillegget 08.10: ville feilet hvis grunnlaget sa 15 når lista hadde
        et annet antall. Prøver en liste med færre enn 15 og en med 18."""
        lista = tuple(Aksje(f"X{i}", f"X{i}.OL", f"X{i}", "Energi") for i in range(antall))
        vurderinger = {a.symbol: vurdering(1, "Positiv") for a in lista}
        serier = {a.symbol: to_dager(100, 101) for a in lista}
        g = dagsgrunnlag(FREDAG, lista, vurderinger, serier, INDEKS)
        assert g["aksjer"] == antall and g["med_kurs"] == antall

    def test_uten_indeks_er_hovedindeksen_ikke_med(self):
        """Ville feilet hvis grunnlaget sa noe om hovedindeksen uten den."""
        g = grunnlaget(indeksserie=None)
        assert "hovedindeksen" not in g and "bedre_enn_indeksen" not in g and "med_kurs" not in g

    def test_uten_vurdering_er_det_ikke_noe_grunnlag(self):
        """Ville feilet hvis det ble en tekst om en dag ingen aksje er vurdert."""
        assert grunnlaget(vurderinger={"DDD": Grunn.SYMBOL_FEILET}) is None


GRUNNLAG = {
    "aksjer": 15,
    "ukedag": "tirsdag",
    "hovedindeksen": "falt",
    "bedre_enn_indeksen": 9,
    "med_kurs": 15,
    "skilte_seg_ut": 4,
    "skilte_seg_ut_positiv": 2,
    "skilte_seg_ut_negativ": 1,
    "skilte_seg_ut_blandet": 1,
    "bransjer": {"Energi": {"steg": 1, "med_endring": 4}, "Sjømat": {"steg": 2, "med_endring": 2}},
}
GOD = (
    "Hovedindeksen falt tirsdag. 9 av 15 aksjer gjorde det bedre enn indeksen. 4 skilte seg ut: 2 med "
    "positiv retning, 1 negativ og 1 blandet. I energi steg 1 av 4 aksjer."
)


class TestKontrollen:
    """Del C, FR-603 med alle fire punktene."""

    def test_en_god_tekst_bestaar(self):
        """Eksempelteksten i utdraget §3. Ville feilet hvis kontrollen stoppet
        formene i prompten."""
        assert kontroller_dagen(GOD, GRUNNLAG).besto

    def test_tallene_staar_med_sifre(self):
        """Gjennomgangen (ECH10, VG7): tallene i formene står med sifre, så
        hvert tall som vises, har prikket strek. Ville feilet hvis «to av to»
        besto, som før gjennomgangen."""
        assert kontroller_dagen("I sjømat steg 2 av 2 aksjer.", GRUNNLAG).besto
        assert not kontroller_dagen("I sjømat steg to av to aksjer.", GRUNNLAG).besto

    @pytest.mark.parametrize(
        "tekst",
        [
            "Hovedindeksen falt ikke tirsdag.",
            "Hovedindeksen falt kraftig tirsdag.",
            "Aksjene gikk opp tirsdag.",
            "Oslo Børs gikk ned tirsdag.",
            "OSEBX gikk ned.",
            "Det var en negativ dag.",
            "Det var en urolig dag med store bevegelser.",
            "Equinor var vinneren.",
            "Finans gikk godt.",
            "Energiaksjene gikk opp.",
            "I energi steg 1 av 4 aksjer, så hele bransjen gikk ned.",
            "Hovedindeksen falt tirsdag for andre dag på rad.",
            "Flertallet av aksjene gjorde det godt.",
            "Tiden er inne for å handle.",
        ],
    )
    def test_bare_formene_og_bindeord(self, tekst):
        """Gjennomgangen (BH1-BH3, ECH2-ECH6, VG1, VG2): ville feilet hvis en
        nektelse, et synonym, et selskap, en bransje utenfor formen eller et
        ord om hvor kraftig noe var, besto. Resten av teksten kan bare være
        «og», «men» og tegnsetting."""
        svar = kontroller_dagen(tekst, GRUNNLAG)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner), svar.grunner

    def test_formene_med_bindeord_bestaar(self):
        assert kontroller_dagen(
            "Hovedindeksen falt tirsdag, men 9 av de 15 aksjene gikk bedre enn indeksen.", GRUNNLAG
        ).besto
        en = {**GRUNNLAG, "skilte_seg_ut": 1, "skilte_seg_ut_positiv": 1, "skilte_seg_ut_negativ": 0}
        assert kontroller_dagen(
            "1 aksje skilte seg ut: 1 med positiv retning.", {**en, "skilte_seg_ut_blandet": 0}
        ).besto

    @pytest.mark.parametrize(
        "tekst",
        [
            "10 av 15 aksjer gjorde det bedre enn indeksen.",
            "5 skilte seg ut.",
            "4 skilte seg ut: 3 med positiv retning.",
            "I energi steg 2 av 4 aksjer.",
            "I sjømat steg tre av to aksjer.",
        ],
    )
    def test_et_tall_som_ikke_stemmer_ved_feltet_stoppes(self, tekst):
        """Punkt 2. Ville feilet hvis teksten kunne nevne et tall som ikke
        står i grunnlaget (kontrollpunktet i storyen)."""
        svar = kontroller_dagen(tekst, GRUNNLAG)
        assert not svar.besto and any(g.startswith("2:") for g in svar.grunner)

    @pytest.mark.parametrize(
        "tekst",
        ["Det var 15 aksjer i lista.", "Fem aksjer falt.", "Indeksen falt 1,2 %.", "Omsetningen var 300 millioner."],
    )
    def test_et_tall_utenfor_formene_stoppes(self, tekst):
        """Punkt 2: ville feilet hvis et tall utenfor formene besto, også et
        som står i grunnlaget (15). Gjennomgangen (BH10): grunnen er tallet."""
        svar = kontroller_dagen(tekst, GRUNNLAG)
        assert not svar.besto and any(g.startswith("2:") for g in svar.grunner), svar.grunner

    @pytest.mark.parametrize(
        "tekst",
        ["Hovedindeksen steg tirsdag.", "Hovedindeksen var uendret tirsdag.", "Markedet var svakt.", "Børsen steg."],
    )
    def test_retningen_paa_hovedindeksen(self, tekst):
        """Punkt 1: ville feilet hvis teksten kunne si en annen retning enn
        grunnlaget, eller si noe om børsen utenfor formene."""
        svar = kontroller_dagen(tekst, GRUNNLAG)
        assert not svar.besto and any(g.startswith("1:") for g in svar.grunner)

    def test_hovedindeksen_uten_feltet_stoppes(self):
        uten = {k: v for k, v in GRUNNLAG.items() if k != "hovedindeksen"}
        assert not kontroller_dagen("Hovedindeksen falt tirsdag.", uten).besto

    @pytest.mark.parametrize(
        "tekst", ["Hovedindeksen falt onsdag.", "Hovedindeksen falt i dag.", "I går var det rolig."]
    )
    def test_ukedagen_og_i_dag(self, tekst):
        """Spørsmål 4: ville feilet hvis teksten fikk en annen ukedag, eller
        «i dag», som er feil når teksten leses senere."""
        assert not kontroller_dagen(tekst, GRUNNLAG).besto

    def test_en_bransje_som_ikke_er_i_grunnlaget_stoppes(self):
        """Spørsmål 3: ville feilet hvis teksten kunne nevne en bransje
        grunnlaget ikke har, eller bransjen utenfor formen."""
        assert not kontroller_dagen("I finans steg 1 av 2 aksjer.", GRUNNLAG).besto
        assert not kontroller_dagen("Energi hadde en god dag.", GRUNNLAG).besto

    @pytest.mark.parametrize("tekst", ["Det kan være lurt å kjøpe energiaksjer.", "Du bør holde aksjene."])
    def test_raad_stoppes(self, tekst):
        """Punkt 3, NFR-06: ville feilet hvis teksten kunne leses som et råd
        (kontrollpunktet i storyen)."""
        svar = kontroller_dagen(tekst, GRUNNLAG)
        assert not svar.besto and any(g.startswith("3:") for g in svar.grunner)

    @pytest.mark.parametrize(
        "tekst",
        ["Dette skyldes trolig oljeprisen.", "Det tyder på en sterk uke.", "Dette pleier å gjenta seg."],
    )
    def test_gjetning_stoppes(self, tekst):
        """Punkt 4: ville feilet hvis teksten kunne gjette på årsaker eller
        finne mønstre selv."""
        svar = kontroller_dagen(tekst, GRUNNLAG)
        assert not svar.besto and any(g.startswith("4:") for g in svar.grunner)

    def test_feltnavn_stoppes(self):
        assert not kontroller_dagen("skilte_seg_ut er ‹skilte_seg_ut›.", GRUNNLAG).besto

    def test_ingen_skilte_seg_ut(self):
        """Ville feilet hvis «Ingen aksjer skilte seg ut» besto når noen gjorde det."""
        assert not kontroller_dagen("Ingen aksjer skilte seg ut.", GRUNNLAG).besto
        null = {**GRUNNLAG, "skilte_seg_ut": 0, "skilte_seg_ut_positiv": 0, "skilte_seg_ut_negativ": 0}
        assert kontroller_dagen("Ingen aksjer skilte seg ut.", {**null, "skilte_seg_ut_blandet": 0}).besto


# Avtrykket av prompten for dagen (FR-605). Endres prompten, faar den ny
# versjon, og avtrykket settes paa nytt.
AVTRYKK = {
    "dag-1": "186958066d33e1588a31a6a6fa7dc5ca38bf6b8e31ad5242b008bf677c1472f7",
    # Story 10.10. Teksten til dag-1 staar i src/ki_dagen.py paa 059dc10c.
    # Tillegget kl. 17:21: tre nye former, og versjonen staar som dag-2, fordi den ikke er
    # flettet. Var f0377e8f....
    "dag-2": "cf1e7f7577f9f3afa07d1b7ca0db65845d9daecf9ef6cbf4ab472a6a33340c7a",
    # Story 10.11: formene med «mest» sier «av bransjene med minst to aksjer».
    "dag-3": "fd1f011d0d433374d1f28c16cbcbf0f225f07ea331d3165af6381ecad166bc7f",
}


def promptens_avtrykk() -> str:
    tekst = REGLER_DAGEN + inspect.getsource(lag_dagsprompt) + inspect.getsource(ki_dagen._vanlig)
    # Story 10.10: setningen om navnene.
    tekst += ki_dagen.SETNINGEN_NAVN + inspect.getsource(ki_dagen.setning_om_navnene)
    # Svaret 11.11 kl. 19:30: formen for én bransje og reglene() som velger den.
    tekst += ki_dagen.BRANSJEFORMEN + inspect.getsource(ki_dagen.reglene)
    return hashlib.sha256(tekst.replace("\r\n", "\n").encode("utf-8")).hexdigest()


class TestPrompten:
    """Del B, FR-605."""

    def test_versjonen_foelger_teksten(self):
        """Ville feilet hvis prompten fikk en annen tekst uten ny versjon. Da
        ser to prompter ut som én i loggen."""
        assert promptens_avtrykk() == AVTRYKK[DAGSPROMPTVERSJON]

    def test_versjonen_er_ikke_den_for_en_aksje(self):
        """Spørsmål 6: ville feilet hvis teksten om dagen og teksten om én
        aksje kunne få samme versjon i loggen."""
        from ki_prompt import PROMPTVERSJON

        assert DAGSPROMPTVERSJON != PROMPTVERSJON and DAGSPROMPTVERSJON.startswith("dag-")

    def test_prompten_har_grunnlaget_og_ingen_kurs(self):
        prompt = lag_dagsprompt(GRUNNLAG)
        assert json.dumps(GRUNNLAG, ensure_ascii=False, sort_keys=True) in prompt
        assert "Ikke gi råd" in prompt and "Ikke gjett på årsaker" in prompt


class EnModell(FalskModell):
    def __init__(self, tekst=GOD, feil=None):
        super().__init__(tekst, feil)
        self.prompter = []

    def lag_tekst(self, prompt):
        self.prompter.append(prompt)
        return super().lag_tekst(prompt)


class TestRaden:
    """Del D, FR-604 og FR-605."""

    def test_raden_har_versjonen_og_grunnlaget(self):
        rad = lag_dagsrad(Emne.dagen(date(2026, 11, 3)), GRUNNLAG, EnModell())
        assert rad.besto and rad.promptversjon == DAGSPROMPTVERSJON and rad.emne.slag == "dag"
        assert dict(rad.grunnlag)["skilte_seg_ut"] == 4

    def test_modellen_feilet_gir_en_rad_uten_tekst(self):
        """NFR-04: ville feilet hvis en feil hos modellen stoppet hentingen."""
        rad = lag_dagsrad(Emne.dagen(date(2026, 11, 3)), GRUNNLAG, EnModell(feil=ModellFeilet("tidsavbrudd")))
        assert rad.modellen_feilet and not rad.besto and "tidsavbrudd" in rad.grunn

    def test_en_tekst_som_ikke_bestaar_lagres_med_grunnen(self):
        rad = lag_dagsrad(Emne.dagen(date(2026, 11, 3)), GRUNNLAG, EnModell(tekst="Kjøp energi."))
        assert not rad.besto and rad.tekst == "Kjøp energi." and "3: «Kjøp»" in rad.grunn

    def test_bare_emnet_dag(self):
        with pytest.raises(ValueError):
            lag_dagsrad(Emne.aksje("EQNR", date(2026, 11, 3)), GRUNNLAG, EnModell())


def dagens_rad(base, dato=TIRSDAG):
    tilkobling = aapne_base(base)
    try:
        return SqliteKILogg(tilkobling, lambda: datetime(2026, 9, 22, 20, 0).astimezone()).les(Emne.dagen(dato))
    finally:
        tilkobling.close()


class _Teller(FalskModell):
    """Tekstene for aksjene, og eksempelteksten for dagen."""

    def __init__(self, feil_for_aksjene=None):
        super().__init__()
        self.dagkall = 0
        self.feil_for_aksjene = feil_for_aksjene

    def lag_tekst(self, prompt):
        # Svaret 11.11 kl. 19:30: reglene har formen for én bransje bare uten «mest».
        if prompt.startswith(REGLER_DAGEN.split("{bransjeformen}")[0]):
            self.dagkall += 1
            self.kall += 1
            return Modellsvar(tekst="Hovedindeksen steg tirsdag.", modell="gemma4:e4b")
        if self.feil_for_aksjene is not None:
            self.kall += 1
            raise self.feil_for_aksjene
        return super().lag_tekst(prompt)


@pytest.fixture
def stier(tmp_path):
    """Som i test_ki_tekst.py: raamappa og testbasen i tmp_path (regel 22)."""
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


class TestHentingen:
    """Del D, NFR-02: ett kall per børsdag, i hentingen."""

    def test_ett_kall_for_dagen_og_raden_staar(self, stier):
        """Ville feilet hvis modellen ble kalt to ganger for samme dag, eller
        raden ble laget på nytt samme kveld (FR-604)."""
        raa, base = stier
        modell = _Teller()
        kode, _, ut = kjoer(raa, base, modell)
        assert kode == 0 and modell.dagkall == 1
        rad = dagens_rad(base)
        assert rad is not None and rad.promptversjon == DAGSPROMPTVERSJON
        assert "Teksten om dagen: besto kontrollen." in ut
        andre = _Teller()
        kjoer(raa, base, andre)
        assert andre.dagkall == 0 and dagens_rad(base) == rad

    def test_feilet_modellen_for_en_aksje_kalles_den_ikke_for_dagen(self, stier):
        """Ville feilet hvis hentingen ventet på en modell som alt har feilet."""
        raa, base = stier
        modell = _Teller(feil_for_aksjene=ModellFeilet("tidsavbrudd"))
        kjoer(raa, base, modell)
        rad = dagens_rad(base)
        assert modell.dagkall == 0 and rad.modellen_feilet and "ikke kalt" in rad.grunn

    def test_ingen_rader_naar_modellen_ikke_er_klar(self, stier):
        """Svar c kl. 23:32: ville feilet hvis teksten om dagen ble skrevet når
        Ollama ikke svarer."""
        raa, base = stier

        class IkkeKlar(_Teller):
            def sjekk(self):
                return "Ollama svarer ikke"

        modell = IkkeKlar()
        kjoer(raa, base, modell)
        assert modell.kall == 0 and dagens_rad(base) is None

    def test_siden_kaller_aldri_modellen(self):
        """AD-10: ville feilet hvis webserveren importerte ki_dagen."""
        kilde = inspect.getsource(app_modul)
        assert "import ki_dagen" not in kilde and "from ki_dagen" not in kilde


# --- Forsiden (del E) -------------------------------------------------------


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 12, 31, 12, 0).astimezone())


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def forsiden_med(tekst: str | None, grunnlag=None, besto=True):
    """To aksjer med kurs og vurdering fredag 30.10, og raden for dagen."""
    rader = [
        Kursrad(dato=TORSDAG - timedelta(days=1), slutt=99.0, justert_slutt=99.0, volum=1000),
        *to_dager(100, 103),
    ]
    skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
    skriv_vurdering("EQNR", FREDAG, vurdering(3, "Positiv"))
    skriv_serie("DNB", [*rader[:1], *to_dager(100, 98)], datetime.fromisoformat(HENTET), vurdert=False)
    skriv_vurdering("DNB", FREDAG, vurdering(1, "Positiv"))
    if grunnlag is None:
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            from app import SqliteOversiktsleser

            poster = SqliteOversiktsleser(tilkobling).oversikt()
            lista = tuple(p.aksje for p in poster)
            serier = {a.symbol: lagring_sqlite.SqliteKurslager(tilkobling).serie(a.symbol) for a in lista}
            vurderinger = {a.symbol: SqliteOversiktsleser(tilkobling).vurdering(a.symbol, FREDAG) for a in lista}
            grunnlag = dagsgrunnlag(FREDAG, lista, vurderinger, serier, None)
        finally:
            tilkobling.close()
    if tekst is not None:
        skriv_kirad(
            KIRad(
                emne=Emne.dagen(FREDAG),
                grunnlag=grunnlag,
                regelen="r",
                tekst=tekst,
                besto=besto,
                grunn=None if besto else "2: tallet",
                promptversjon=DAGSPROMPTVERSJON,
                tjeneste="lokal",
                modell="gemma4:e4b",
            )
        )
    return grunnlag


TEKSTEN = "1 skilte seg ut: 1 med positiv retning."


def html(klient, adresse="/", kapsel=None) -> str:
    if kapsel is not None:
        klient.set_cookie(KAPSEL, kapsel)
    svar = klient.get(adresse)
    assert svar.status_code == 200
    return svar.data.decode("utf-8")


class TestForsiden:
    def test_teksten_vises_med_merket_modellen_og_prikkede_tall(self, klient):
        """Utdraget §3. Ville feilet hvis teksten ikke sto under tabellen,
        eller tallene ikke hadde prikket strek (spørsmål 8)."""
        forsiden_med(TEKSTEN)
        side = html(klient)
        assert "Børsdagen kort fortalt" in side and "Laget av KI" in side
        assert '<span class="tall">1</span> skilte seg ut' in side
        assert "Skrevet av gemma4:e4b (lokal) da kursene ble hentet." in side
        assert side.index('class="tabell') < side.index("boersdagen-kort-fortalt")

    def test_grunnlaget_maa_stemme_med_siden(self, klient):
        """FR-607: ville feilet hvis teksten ble vist når grunnlaget ikke
        stemmer med det siden viser."""
        grunnlag = forsiden_med(None)
        forsiden_med(TEKSTEN, grunnlag={**grunnlag, "skilte_seg_ut": 2, "skilte_seg_ut_positiv": 2})
        side = html(klient)
        assert TEKSTEN not in side and DAGEN_UTEN in side

    def test_en_tekst_som_ikke_besto_vises_ikke(self, klient):
        forsiden_med(TEKSTEN, besto=False)
        side = html(klient)
        assert TEKSTEN not in side and DAGEN_UTEN in side

    def test_uten_rad(self, klient):
        forsiden_med(None)
        assert DAGEN_UTEN in html(klient)

    def test_bryteren_slaar_av_begge_ki_tekstene(self, klient):
        """FR-601: ville feilet hvis bryteren ikke slo av teksten om dagen,
        eller ikke var den samme kapselen som på aksjesiden."""
        forsiden_med(TEKSTEN)
        side = html(klient, kapsel="av")
        assert TEKSTEN not in side and DAGEN_AV in side
        assert 'name="til" value="paa"' in side and 'aria-checked="false"' in side

    def test_bryteren_sender_tilbake_til_delen(self, klient):
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/"})
        assert svar.status_code == 303 and svar.headers["Location"].endswith("/#boersdagen-kort-fortalt")
        assert "ose_ki=av" in svar.headers["Set-Cookie"]

    def test_en_periode_har_ingen_tekst(self, klient):
        """Spørsmål 1: ville feilet hvis en periode viste teksten for én dag."""
        forsiden_med(TEKSTEN)
        side = html(klient, "/?periode=1-uke")
        assert PERIODEN_UTEN in side and TEKSTEN not in side

    def test_min_liste_har_ikke_delen(self, klient):
        """Spørsmål 9: FR-607 gjelder markedsoversikten."""
        forsiden_med(TEKSTEN)
        assert "Børsdagen kort fortalt" not in html(klient, "/min-liste?vis=alle")

    def test_linja_om_min_liste_under_teksten(self, klient):
        """Story 10.10, spørsmål 10 (gjennomgangen, VG1): ville feilet hvis
        forsiden ikke viste linja appen skriver om Min liste under teksten,
        viste den uten merkede aksjer, eller viste den med KI av."""
        import re

        forsiden_med(TEKSTEN)
        assert "min-liste-linje" not in html(klient)
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            lagring_sqlite.SqliteMinlistelager(tilkobling).merk("EQNR")
        finally:
            tilkobling.close()
        side = html(klient)
        linja = re.search(
            r'<p class="min-liste-linje">I Min liste skilte [^<]+ \(3 av 3, positiv\) seg ut\. '
            r'<span class="merke-app">Skrevet av appen\.</span></p>',
            side,
        )
        assert linja and side.index('class="ki-tekst"') < linja.start(), side[side.index("boersdagen-kort-fortalt") :][
            :1500
        ]
        assert "min-liste-linje" not in html(klient, kapsel="av")

    def test_hentingen_og_forsiden_regner_det_samme_grunnlaget(self, klient):
        """Story 10.10, tillegget (gjennomgangen, VG2, FR-607): med 12 vurderte
        dager før har grunnlaget fra hentingen antallet mot vanlig, og
        forsiden viser teksten. Ville feilet hvis hentingen eller forsiden
        leste de tidligere vurderingene ulikt, så teksten forsvant."""
        from dagsgrunnlag import VANLIG, dagene_foer
        from ki_tekst import _grunnlaget_for_dagen
        from lagring_sqlite import SqliteVurderingslager

        forsiden_med(None)
        for d in dagene_foer(FREDAG, 12):
            skriv_vurdering("EQNR", d, vurdering(2, "Positiv"))
            skriv_vurdering("DNB", d, vurdering(1, "Positiv"))
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            from app import SqliteOversiktsleser

            lista = tuple(p.aksje for p in SqliteOversiktsleser(tilkobling).oversikt())
        finally:
            tilkobling.close()
        # Hentingen venter til hver aksje i lista har en rad for dagen.
        for a in lista:
            if a.symbol not in ("EQNR", "DNB"):
                skriv_vurdering(a.symbol, FREDAG, Grunn.SYMBOL_FEILET)
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            klokke = app_modul.naa
            grunnlag, grunn = _grunnlaget_for_dagen(
                tilkobling,
                SqliteKILogg(tilkobling, klokke),
                SqliteVurderingslager(tilkobling, klokke, lista),
                FREDAG,
                lista,
                lambda: FREDAG,
                lambda _: None,
            )
        finally:
            tilkobling.close()
        assert grunnlag is not None, grunn
        assert grunnlag[VANLIG] == 1
        forsiden_med(TEKSTEN, grunnlag=dict(grunnlag))
        side = html(klient)
        assert '<p class="ki-tekst">' in side and DAGEN_UTEN not in side

    def test_vakta_stopper_et_raad(self):
        """NFR-06: ville feilet hvis en tekst som besto kontrollen, men sier
        «kjøp», ble vist."""
        rad = KIRad(
            emne=Emne.dagen(FREDAG),
            grunnlag=GRUNNLAG,
            regelen="r",
            tekst="Kjøp nå.",
            besto=True,
            grunn=None,
            promptversjon=DAGSPROMPTVERSJON,
            tjeneste="lokal",
            modell="m",
        )
        assert not bygg_dagsvisning(rad, GRUNNLAG).vist


class TestHjelpen:
    """Del F, regel 19."""

    def test_hjelpen_har_ordene_fra_utdraget_i_tre_setninger(self):
        tekst = hjelpetekster()["boersdagen_kort_fortalt"].tekst
        assert tekst.startswith("Et kort sammendrag av børsdagen, skrevet av en språkmodell (KI).")
        assert "tall med prikket strek står i det modellen fikk, og den gir ikke råd." in tekst

    def test_docs_hjelp_og_readme_sier_det_samme(self):
        """Regel 19: ville feilet hvis hjelpen på siden og docs/hjelp.md eller
        README-en sa ulikt om hva modellen fikk."""
        from pathlib import Path

        rot = Path(__file__).resolve().parent.parent
        hjelp = (rot / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "### Hva er «Børsdagen kort fortalt» på forsiden?" in hjelp
        assert "Dagen er uten KI-tekst." in hjelp
        # Gjennomgangen (BH6, VG6): setningen om hva modellen fikk, ordrett i begge.
        tekst = hjelpetekster()["boersdagen_kort_fortalt"].tekst
        # Story 10.10: «bare det appen regnet ut», fordi modellen ogsaa faar navnene.
        setningen = tekst[
            tekst.index("Modellen fikk bare det appen regnet ut:") : tekst.index("nyheter.") + len("nyheter.")
        ]
        assert setningen in hjelp
        assert "Børsdagen kort fortalt" in (rot / "README.md").read_text(encoding="utf-8")


class TestDemoen:
    """Del G: teksten om dagen i demoen, laget med Gemma."""

    def test_demoteksten_er_laget_med_prompten_som_staar(self):
        """Ville feilet hvis prompten ble endret uten at demoteksten ble laget
        på nytt (uv run python src/demo_ki.py --dagen)."""
        import demo
        from demo_ki import dagens_promptavtrykk, les_dagsraden

        rad = les_dagsraden(prompt=dagens_promptavtrykk())
        assert rad.emne.dato == demo.SLUTTDATO and rad.promptversjon == DAGSPROMPTVERSJON
        assert rad.besto and kontroller_dagen(rad.tekst, rad.grunnlag).besto

    def test_forsiden_i_demoen_viser_teksten(self, monkeypatch):
        """Ville feilet hvis grunnlaget i demoteksten ikke stemte med det
        forsiden i demoen viser, eller demoen ikke skrev raden inn."""
        import shutil
        import tempfile
        from pathlib import Path

        import demo
        from demo_ki import les_dagsraden
        from lagring_sqlite import demo_sti

        with tempfile.TemporaryDirectory() as mappe:
            mal = Path(mappe) / "demo.db"
            demo.lag_demobase(mal, skriv=lambda _: None)
            sti = demo_sti()
            sti.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(mal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0).astimezone())
        side = app_modul.app.test_client().get("/").data.decode("utf-8")
        tekst = les_dagsraden().tekst
        # Story 10.10 (svaret 11.11 kl. 16:05): Gemma i demoen.
        assert "Skrevet av gemma4:e4b (lokal) da kursene ble hentet." in side
        from ki_visning import prikkede_tall

        assert str(prikkede_tall(tekst)) in side and DAGEN_UTEN not in side


class TestEtterGjennomgangen:
    """Funnene fra gjennomgangen av 10.6 som gjelder hentingen og bryteren."""

    def test_ikke_teksten_om_dagen_foer_alle_aksjene_har_en_rad(self, stier):
        """BH4, ECH1, VG3: ville feilet hvis teksten om dagen ble laget når en
        aksje ennå mangler raden for dagen, for da står raden med et grunnlag
        siden aldri regner, og dagen blir for godt uten tekst."""
        from ki_tekst import lag_ki_tekster
        from test_ki_tekst import OEYEBLIKK

        raa, base = stier
        kjoer(raa, base, None)
        tilkobling = aapne_base(base)
        try:
            tilkobling.execute("DELETE FROM vurdering WHERE symbol = 'EQNR' AND dato = ?", (TIRSDAG.isoformat(),))
            tilkobling.commit()
        except Exception:
            pytest.skip("vurdering kan ikke slettes i denne basen")
        finally:
            tilkobling.close()
        modell = _Teller()
        linjer = []
        lag_ki_tekster(base, TIRSDAG, lambda: OEYEBLIKK, modell, linjer.append, med_dagen=True)
        assert modell.dagkall == 0 and dagens_rad(base) is None
        assert "Teksten om dagen: venter til alle aksjene har en rad for dagen." in linjer[-1]

    def test_velg_dag_viser_teksten_for_den_dagen(self, klient):
        """VG4: ville feilet hvis en valgt dag viste teksten for siste dag,
        eller ingen tekst, eller bryteren ikke sendte tilbake til dagen."""
        forsiden_med(TEKSTEN)
        skriv_vurdering("EQNR", TORSDAG, vurdering(2, "Negativ"))
        skriv_vurdering("DNB", TORSDAG, vurdering(1, "Positiv"))
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            from app import SqliteOversiktsleser

            leser = SqliteOversiktsleser(tilkobling)
            lista = tuple(p.aksje for p in leser.oversikt())
            serier = {a.symbol: lagring_sqlite.SqliteKurslager(tilkobling).serie(a.symbol) for a in lista}
            grunnlag = dagsgrunnlag(
                TORSDAG, lista, {a.symbol: leser.vurdering(a.symbol, TORSDAG) for a in lista}, serier, None
            )
        finally:
            tilkobling.close()
        torsdag = "1 skilte seg ut: 1 med negativ retning."
        skriv_kirad(
            KIRad(
                emne=Emne.dagen(TORSDAG),
                grunnlag=grunnlag,
                regelen="r",
                tekst=torsdag,
                besto=True,
                grunn=None,
                promptversjon=DAGSPROMPTVERSJON,
                tjeneste="lokal",
                modell="gemma4:e4b",
            )
        )
        side = html(klient, f"/?periode=velg&dag={TORSDAG.isoformat()}")
        assert '<span class="tall">1</span> med negativ retning' in side and TEKSTEN not in side
        assert f'name="tilbake" value="/?periode=velg&amp;dag={TORSDAG.isoformat()}"' in side

    def test_bryteren_tilbake_til_valgt_dag(self, klient):
        svar = klient.post("/ki", data={"til": "av", "tilbake": f"/?periode=velg&dag={FREDAG.isoformat()}"})
        assert svar.headers["Location"].endswith(f"/?periode=velg&dag={FREDAG.isoformat()}#boersdagen-kort-fortalt")

    def test_bryteren_uten_tilbake_gaar_til_forsiden_som_foer(self, klient):
        """ECH12: ville feilet hvis en forespørsel uten tilbake fikk ankeret."""
        svar = klient.post("/ki", data={"til": "av"})
        assert svar.headers["Location"] in ("/", "http://localhost/")
