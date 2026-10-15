"""Story 10.2, PR F: KI-teksten i hentekommandoen - FR-603, FR-604, FR-608,
NFR-04, AD-17.

kjoer med en falsk EODHD (hent) og en falsk modell (AD-8). Ingen test kaller
Ollama eller EODHD.
"""

from datetime import date, datetime, timezone

import pytest

import sqlite3

import fetch_prices as fp
import ki_tekst
from ki_lokal import OllamaModell
from ki_modell import ModellFeilet, Modellsvar
from ki_tekst import ki_innstillinger, lag_ki_tekster, modell_fra_miljoeet, regeltekst, velg_modell
from kilogg import Emne
from kursdata import AKSJEUNIVERS
from lagring_sqlite import SqliteKILogg, aapne_base
from test_fetch_prices import NOEKKEL, nok_kvote, serie_med_utslag, serie_til, vurderingene

TIRSDAG = date(2026, 9, 22)
OEYEBLIKK = datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)
ONSDAG_KL_22 = datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc)
GOD_TEKST = "Trenden peker opp, og retningen er positiv."


class FalskModell:
    tjeneste = "lokal"
    modell = "gemma4:e4b"

    def __init__(self, tekst=GOD_TEKST, feil=None):
        self.tekst, self.feil, self.kall = tekst, feil, 0

    def lag_tekst(self, prompt):
        self.kall += 1
        if self.feil is not None:
            raise self.feil
        return Modellsvar(tekst=self.tekst, modell="gemma4:e4b", modell_id="dc35e8d9c606",
                          seed=42, temperatur=0.0, maskinvare="gpu", ollama_versjon="0.35.1")


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


def kjoer(raa, base, modell, hent=None, oeyeblikk=OEYEBLIKK, les_kvote=nok_kvote):
    """kjoer med utskriften samlet og kallene til EODHD talt."""
    linjer, kall = [], []

    def tell(ticker, *a):
        kall.append(ticker)
        return (hent or (lambda *_: serie_med_utslag(TIRSDAG)))(ticker, *a)

    kode = 0
    try:
        fp.kjoer(raa, base, oeyeblikk, NOEKKEL, tell, linjer.append, les_kvote=les_kvote, modell=modell)
    except SystemExit as slutt:
        kode = slutt.code
    return kode, kall, "\n".join(linjer)


def radene(base, dato=TIRSDAG):
    tilkobling = aapne_base(base)
    try:
        logg = SqliteKILogg(tilkobling, lambda: OEYEBLIKK)
        return {a.symbol: logg.les(Emne.aksje(a.symbol, dato)) for a in AKSJEUNIVERS}
    finally:
        tilkobling.close()


class TestSteget:
    def test_en_rad_per_aksje_etter_vurderingene(self, stier):
        """FR-604, AD-17. Ville feilet hvis steget kom foer vurderingene (F3)."""
        raa, base = stier
        modell = FalskModell()
        kode, _, ut = kjoer(raa, base, modell)
        assert kode == 0
        rader = radene(base)
        assert all(r is not None and r.besto for r in rader.values())
        assert modell.kall == 15
        assert ut.index("Skrev 15 rader i vurdering") < ut.index("KI-tekst for boersdagen 2026-09-22")
        assert "15 besto kontrollen, 0 ble stoppet av kontrollen, og modellen feilet for 0." in ut

    def test_grunnlaget_og_regelen_er_vurderingens(self, stier):
        raa, base = stier
        kjoer(raa, base, FalskModell())
        vurdering = vurderingene(base, TIRSDAG)["EQNR"][0]
        rad = radene(base)["EQNR"]
        assert dict(rad.grunnlag) == {"trend": vurdering.trend, "bevegelse": vurdering.bevegelse,
                                      "interesse": vurdering.interesse, "styrke": vurdering.styrke,
                                      "retning": vurdering.retning}
        assert rad.regelen == regeltekst(vurdering)

    def test_ingen_kall_til_eodhd_fra_steget(self, stier, tmp_path):
        """Ville feilet hvis KI-steget gjorde et kall til EODHD (F5)."""
        raa, base = stier
        _, med, _ = kjoer(raa, base, FalskModell())
        _, uten, _ = kjoer(tmp_path / "raa2", tmp_path / "db2" / "ose.db", None)
        assert med == uten and len(med) == 15

    def test_uten_modell_ingen_rader(self, stier):
        """OSE_KI_TJENESTE=av (svar 5): hentingen gaar som foer."""
        raa, base = stier
        kode, _, ut = kjoer(raa, base, None)
        assert kode == 0 and "KI-tekst" not in ut
        assert all(r is None for r in radene(base).values())

    def test_teksten_skrives_ikke_ut(self, stier):
        """Regel 16: bare antall i utskriften."""
        raa, base = stier
        _, _, ut = kjoer(raa, base, FalskModell())
        assert GOD_TEKST not in ut


class TestNaarNoeGaarGalt:
    def test_modellen_feilet_gir_rader_og_hentingen_gaar_som_foer(self, stier):
        """NFR-04, FR-604: en rad om at modellen feilet, og kode 0."""
        raa, base = stier
        kode, _, ut = kjoer(raa, base, FalskModell(feil=ModellFeilet("Ollama svarer ikke")))
        assert kode == 0
        assert all(r.modellen_feilet for r in radene(base).values())
        assert "modellen feilet for 15." in ut
        assert len([v for v, _ in vurderingene(base, TIRSDAG).values() if v is not None]) == 15

    def test_en_annen_feil_stopper_steget_ikke_hentingen(self, stier):
        """Ville feilet hvis en feil hos modellen stoppet hentingen (F1)."""
        raa, base = stier
        kode, _, ut = kjoer(raa, base, FalskModell(feil=ZeroDivisionError()))
        assert kode == 0
        assert "KI-teksten stoppet etter 0 rader: ZeroDivisionError." in ut
        assert len([v for v, _ in vurderingene(base, TIRSDAG).values() if v is not None]) == 15

    def test_en_tekst_som_ikke_bestaar_logges_med_grunnen(self, stier):
        """FR-603: vises ikke, men logges. Ville feilet hvis den ble logget
        som bestaatt (F4)."""
        raa, base = stier
        _, _, ut = kjoer(raa, base, FalskModell("Du bør kjøpe aksjen."))
        rader = radene(base).values()
        assert all(not r.besto and r.tekst and r.grunn.startswith("3:") for r in rader)
        assert "0 besto kontrollen, 15 ble stoppet av kontrollen" in ut

    def test_en_aksje_med_grunn_faar_ingen_ki_tekst(self, stier):
        """En grunn i stedet for vurdering gir ingenting aa forklare."""
        raa, base = stier

        def hent(ticker, *a):
            return serie_til(date(2026, 9, 21)) if ticker == "EQNR.OL" else serie_med_utslag(TIRSDAG)

        modell = FalskModell()
        kjoer(raa, base, modell, hent)
        rader = radene(base)
        assert rader["EQNR"] is None
        assert sum(r is not None for r in rader.values()) == 14 == modell.kall


class TestSammeKveld:
    def test_raden_staar_og_modellen_kalles_ikke_igjen(self, stier):
        """FR-604, svar 2. Ville feilet hvis modellen ble kalt paa nytt (F2)."""
        raa, base = stier
        kjoer(raa, base, FalskModell(feil=ModellFeilet("nede")))
        foer = radene(base)
        modell = FalskModell()
        kode, kall, ut = kjoer(raa, base, modell)
        assert (kode, kall, modell.kall) == (0, [], 0)
        assert radene(base) == foer
        assert "15 rader sto fra foer og er ikke laget paa nytt." in ut

    def test_radene_som_mangler_lages_med_null_kall_til_eodhd(self, stier):
        """Punktet fra 4.3: stoppet kjoeringen mellom vurderingen og KI-raden,
        lager samme kommando radene som mangler, uten kall til EODHD."""
        raa, base = stier
        kjoer(raa, base, None)
        modell = FalskModell()
        kode, kall, _ = kjoer(raa, base, modell)
        assert (kode, kall, modell.kall) == (0, [], 15)
        assert all(r is not None for r in radene(base).values())

    def test_midnatt_stopper_steget_med_beskjed(self, stier):
        """Punktet fra 4.2: KILogg avviser datoen etter midnatt, og steget
        stopper uten aa stoppe hentingen."""
        raa, base = stier
        kjoer(raa, base, None)
        linjer = []
        lag_ki_tekster(base, TIRSDAG, lambda: ONSDAG_KL_22, FalskModell(), linjer.append)
        assert linjer and linjer[0].startswith("KI-teksten stoppet: det er blitt en ny boersdag")
        assert all(r is None for r in radene(base).values())


class TestTjenesten:
    def test_av(self):
        assert velg_modell({"OSE_KI_TJENESTE": "av"}) is None
        assert velg_modell({"OSE_KI_TJENESTE": " AV "}) is None

    def test_uten_variabelen_gjelder_lokal(self):
        """Svar 5 og FR-608."""
        modell = velg_modell({})
        assert isinstance(modell, OllamaModell) and modell.url == "http://127.0.0.1:11434"

    def test_lokal_med_adressen(self):
        """Svar 8."""
        modell = velg_modell({"OSE_KI_TJENESTE": "lokal", "OSE_KI_OLLAMA_URL": "http://ollama:11434"})
        assert modell.url == "http://ollama:11434"

    @pytest.mark.parametrize("tjeneste, tekst", [
        ("gemini", "ikke bygget ennaa"), ("chatgpt", "ukjent eller tom verdi"),
        ("", "ukjent eller tom verdi"), ("   ", "ukjent eller tom verdi"),
    ])
    def test_ingen_stille_overgang(self, tjeneste, tekst):
        """FR-608: én tjeneste per kjoering, aldri en annen i stedet."""
        linjer = []
        assert velg_modell({"OSE_KI_TJENESTE": tjeneste}, linjer.append) is None
        assert tekst in linjer[0]

    def test_miljoeet_foer_env_og_bare_ki_noeklene(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("EODHD_API_KEY=hemmelig\nOSE_KI_TJENESTE=lokal\nOSE_KI_OLLAMA_URL=http://x:1\n",
                       encoding="utf-8")
        assert ki_innstillinger(env, {}) == {"OSE_KI_TJENESTE": "lokal", "OSE_KI_OLLAMA_URL": "http://x:1"}
        assert ki_innstillinger(env, {"OSE_KI_TJENESTE": "av"}) == {"OSE_KI_TJENESTE": "av"}
        assert ki_innstillinger(tmp_path / "finnes-ikke", {}) == {}

    def test_main_gir_kjoer_modellen(self, monkeypatch, tmp_path):
        fanget = {}
        monkeypatch.setattr(fp, "kjoer", lambda *a, **k: fanget.update(k))
        monkeypatch.setattr(fp, "PROSJEKTROT", tmp_path)
        fp.main([])
        assert fanget["modell"] is None  # conftest setter OSE_KI_TJENESTE=av
        monkeypatch.delenv("OSE_KI_TJENESTE")
        fp.main([])
        assert isinstance(fanget["modell"], OllamaModell)

    def test_regeltekst(self):
        class V:
            trend, bevegelse, interesse, styrke, retning = 1, 0, -1, 2, "Blandet"

        assert regeltekst(V()) == "Trend +1, bevegelse 0, interesse -1. Styrke 2, retning Blandet."


class TestEtterGjennomgangen:
    """Gjennomgangen av PR F."""

    def test_modellen_kalles_ikke_igjen_etter_en_feil(self, stier):
        """BH3: én tidsfrist, ikke femten. Resten faar en rad om at modellen
        feilet (FR-604), uten kall."""
        raa, base = stier
        modell = FalskModell(feil=ModellFeilet("tidsavbrudd etter 180 s"))
        kode, _, ut = kjoer(raa, base, modell)
        assert kode == 0 and modell.kall == 1
        rader = radene(base)
        assert all(r.modellen_feilet for r in rader.values())
        andre = [r for s, r in rader.items() if "ikke kalt" in r.grunn]
        assert len(andre) == 14
        assert "modellen feilet for 15." in ut

    def test_et_nytt_forsoek_faar_ki_tekst(self, stier):
        """VG1: en aksje som faar kursen i et nytt forsoek samme kveld, faar
        KI-teksten der."""
        raa, base = stier

        def hent(ticker, *a):
            return serie_til(date(2026, 9, 21)) if ticker == "EQNR.OL" else serie_med_utslag(TIRSDAG)

        kjoer(raa, base, FalskModell(), hent)
        assert radene(base)["EQNR"] is None
        modell = FalskModell()
        kode, kall, _ = kjoer(raa, base, modell)
        assert kall == ["EQNR.OL"]
        assert radene(base)["EQNR"] is not None and modell.kall == 1

    def test_ki_radene_som_mangler_lages_foer_et_nytt_forsoek(self, stier):
        """ECH: vurderte aksjer faar KI-raden selv om forsoeket stopper foer
        foerste kall, her fordi dagens kvote er brukt opp. Ville feilet hvis
        radene bare ble laget etter forsoeket (FR2)."""
        raa, base = stier

        def hent(ticker, *a):
            return serie_til(date(2026, 9, 21)) if ticker == "EQNR.OL" else serie_med_utslag(TIRSDAG)

        kjoer(raa, base, None, hent)

        def brukt_opp(_noekkel):
            return {"apiRequests": 20, "apiRequestsDate": "2026-09-22", "dailyRateLimit": 20, "extraLimit": 0}

        modell = FalskModell()
        kode, kall, _ = kjoer(raa, base, modell, hent, les_kvote=brukt_opp)
        assert kode == 1 and kall == []
        rader = radene(base)
        assert sum(r is not None for r in rader.values()) == 14 and rader["EQNR"] is None
        assert modell.kall == 14

    def test_main_leser_av_fra_env(self, monkeypatch, tmp_path):
        """VG2: .env.example sier av, og main maa lese det fra .env."""
        fanget = {}
        monkeypatch.setattr(fp, "kjoer", lambda *a, **k: fanget.update(k))
        monkeypatch.setattr(fp, "PROSJEKTROT", tmp_path)
        monkeypatch.delenv("OSE_KI_TJENESTE")
        (tmp_path / ".env").write_text("OSE_KI_TJENESTE=av\n", encoding="utf-8")
        fp.main([])
        assert fanget["modell"] is None

    def test_miljoeet_vinner_per_noekkel(self, tmp_path):
        """VG3 og ECH: adressen i miljoeet foer den i .env, og adressen i .env
        naar miljoeet bare har tjenesten."""
        env = tmp_path / ".env"
        env.write_text("OSE_KI_TJENESTE=lokal\nOSE_KI_OLLAMA_URL=http://x:1\n", encoding="utf-8")
        assert ki_innstillinger(env, {"OSE_KI_OLLAMA_URL": "http://y:2"})["OSE_KI_OLLAMA_URL"] == "http://y:2"
        assert ki_innstillinger(env, {"OSE_KI_TJENESTE": "lokal"})["OSE_KI_OLLAMA_URL"] == "http://x:1"

    @pytest.mark.parametrize("url", ["127.0.0.1:11434", "   ", "ftp://x", "http://"])
    def test_en_adresse_som_ikke_er_en_adresse(self, url):
        linjer = []
        assert velg_modell({"OSE_KI_TJENESTE": "lokal", "OSE_KI_OLLAMA_URL": url}, linjer.append) is None \
            or url.strip() == ""
        if url.strip():
            assert "ikke en adresse" in linjer[0]

    def test_en_adresse_utenfor_maskinen_gir_beskjed(self):
        """BH13: prompten sendes dit, og hentingen sier fra."""
        linjer = []
        modell = velg_modell({"OSE_KI_TJENESTE": "lokal", "OSE_KI_OLLAMA_URL": "http://ki.example.com:11434"},
                             linjer.append)
        assert modell is not None and "ki.example.com" in linjer[0]

    def test_innstillinger_som_ikke_kan_leses(self, tmp_path, monkeypatch):
        """ECH: en feil i innstillingene stopper ikke hentingen (NFR-04)."""
        monkeypatch.setattr(ki_tekst, "dotenv_values", lambda *_: 1 / 0)
        (tmp_path / ".env").write_text("x", encoding="utf-8")
        linjer = []
        assert modell_fra_miljoeet(tmp_path / ".env", {}, linjer.append) is None
        assert "innstillingene kunne ikke leses (ZeroDivisionError)" in linjer[0]

    def test_basen_som_ikke_kan_aapnes(self, stier, monkeypatch):
        """VG4: NFR-04 ogsaa naar basen ikke kan aapnes for steget."""
        raa, base = stier

        def feil(*_a, **_k):
            raise sqlite3.OperationalError("laast")

        monkeypatch.setattr(ki_tekst, "aapne_base", feil)
        linjer = []
        lag_ki_tekster(base, TIRSDAG, lambda: OEYEBLIKK, FalskModell(), linjer.append)
        assert linjer == ["KI-teksten: basen kunne ikke aapnes (OperationalError). Ingen KI-tekst i kveld."]

    def test_modellen_kalles_ikke_etter_midnatt(self, stier):
        """ECH: ny boersdag sjekkes foer kallet, ikke foerst ved skriv."""
        raa, base = stier
        kjoer(raa, base, None)
        modell = FalskModell()
        linjer = []
        lag_ki_tekster(base, TIRSDAG, lambda: ONSDAG_KL_22, modell, linjer.append)
        assert modell.kall == 0 and linjer[0].startswith("KI-teksten stoppet: det er blitt en ny boersdag")

    def test_nettsperren_svelges_ikke(self, stier):
        """ECH: NettverkISTest fra en ekte modell i en test skal synes."""
        from conftest import NettverkISTest

        raa, base = stier
        kjoer(raa, base, None)
        with pytest.raises(NettverkISTest):
            lag_ki_tekster(base, TIRSDAG, lambda: OEYEBLIKK, OllamaModell(), lambda _: None)
