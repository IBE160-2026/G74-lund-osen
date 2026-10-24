"""KI-tekstene i demoen - story 3.4b, FR-411, FR-602-FR-605, AD-8, AD-9.

Radene i src/demo_ki_tekster.json er laget én gang med Gemma (demo_ki.py).
Testene kaller aldri Ollama: nettsperren i conftest.py stopper et kall, og
testene som lager rader, gir en falsk modell. Demobasene ligger i tmp_path
(regel 22), fordi conftest.py peker DATA_KATALOG dit.
"""

import json
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from markupsafe import escape

import app as app_modul
import demo
import demo_ki
from hovedindeks import valgt_indeks
from ki_grunnlag import ki_grunnlag, lag_dagsbilde
from ki_kontroll import kontroller
from ki_modell import Modellsvar
from ki_prompt import PROMPTVERSJON
from ki_tekst import regeltekst
from kilogg import AKSJE, LOKAL, MASKINVARE
from lagring_sqlite import SqliteIndekslager, SqliteKILogg, SqliteKurslager, SqliteVurderingslager, demo_sti
from vurderingsdata import Vurdering

SRC = Path(demo_ki.__file__).resolve().parent


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    """Som i test_demo.py: datoene paa sidene haar aaret naar det er et annet."""
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(scope="module")
def radene():
    return demo_ki.les_radene()


@pytest.fixture(scope="module")
def uten_ki(tmp_path_factory):
    """En demobase uten KI-radene, saa vurderingene kan leses uten dem."""
    sti = tmp_path_factory.mktemp("demo-uten-ki") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None, med_ki=False)
    return sti


@pytest.fixture(scope="module")
def vurderingene(uten_ki):
    """Det demoen vurderer paa siste demodag, per symbol."""
    tilkobling = sqlite3.connect(uten_ki)
    try:
        lager = SqliteVurderingslager(tilkobling, demo._klokke_for(demo.SLUTTDATO), demo.DEMOUNIVERS)
        return {a.symbol: lager.les(a.symbol, demo.SLUTTDATO) for a in demo.DEMOUNIVERS}
    finally:
        tilkobling.close()


@pytest.fixture(scope="module")
def dagene(uten_ki, vurderingene):
    """Story 10.2e: dagsbildet for hver aksje med vurdering paa siste
    demodag, regnet fra kursene, indeksen og vurderingene i demobasen."""
    tilkobling = sqlite3.connect(uten_ki)
    try:
        lista = demo.DEMOUNIVERS
        lager = SqliteVurderingslager(tilkobling, demo._klokke_for(demo.SLUTTDATO), lista)
        kurser = SqliteKurslager(tilkobling, lista)
        serier = {a.symbol: kurser.serie(a.symbol) for a in lista}
        indekser = SqliteIndekslager(tilkobling)
        indeks = indekser.serie(valgt_indeks(indekser.symboler()))
        return {
            a.symbol: lag_dagsbilde(
                a,
                demo.SLUTTDATO,
                vurderingene[a.symbol],
                lager.les_periode(a.symbol, date.min, demo.SLUTTDATO),
                lista,
                serier,
                indeks,
            )
            for a in lista
            if isinstance(vurderingene[a.symbol], Vurdering)
        }
    finally:
        tilkobling.close()


@pytest.fixture
def klient(monkeypatch):
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    return app_modul.app.test_client()


class TestFila:
    def test_grunnlaget_stemmer_med_demodagen(self, radene, vurderingene, dagene):
        """FR-602: grunnlaget og regelen i hver rad er det demoen vurderer
        paa siste demodag. Ville feilet hvis demoen endret seg og tekstene ble
        staaende: da forklarer KI en annen dag enn siden viser, og testen er
        roed til tekstene lages paa nytt (uv run python src/demo_ki.py).
        Story 10.2e: ogsaa dagen fra versjon 3."""
        assert radene
        for rad in radene:
            assert rad.emne.slag == AKSJE and rad.emne.dato == demo.SLUTTDATO, rad.emne
            vurdering = vurderingene[rad.emne.symbol]
            assert isinstance(vurdering, Vurdering), rad.emne.symbol
            ventet = ki_grunnlag(vurdering, utenfor_maalingen=False, dagen=dagene[rad.emne.symbol])
            assert json.loads(rad.grunnlag_som_json()) == dict(ventet), rad.emne.symbol
            assert rad.regelen == regeltekst(vurdering), rad.emne.symbol

    def test_en_rad_per_aksje_med_vurdering_og_ingen_for_en_grunn(self, radene, vurderingene):
        """Ville feilet hvis en aksje med en vurdering manglet raden, eller en
        aksje med en grunn (VRDS og MTFJ) fikk en."""
        med_vurdering = {s for s, v in vurderingene.items() if isinstance(v, Vurdering)}
        symbolene = [r.emne.symbol for r in radene]
        assert len(symbolene) == len(set(symbolene)) == len(med_vurdering)
        assert set(symbolene) == med_vurdering
        for symbol in (demo.NYLIG_NOTERT, demo.UTEN_KURSER):
            assert not isinstance(vurderingene[symbol], Vurdering) and symbol not in symbolene

    def test_hver_tekst_demoen_viser_bestaar_kontrollen_slik_den_er_naa(self, radene):
        """FR-603: kontrollen kjoeres paa nytt paa hver tekst som er merket
        bestaatt. Ville feilet med en tekst som ikke bestaar, merket som
        bestaatt, eller hvis kontrollen ble strammet inn uten at tekstene ble
        laget paa nytt."""
        for rad in radene:
            if rad.besto:
                svar = kontroller(rad.tekst, rad.grunnlag)
                assert svar.besto, (rad.emne.symbol, svar.grunner)
            else:
                assert rad.grunn, rad.emne.symbol

    def test_hver_rad_har_tjenesten_modellen_og_hvordan_den_kjoerte(self, radene):
        """FR-604 og FR-605. Ville feilet med en rad uten tjenesten, modellen,
        modell-ID-en, seed, temperaturen, maskinvaren eller Ollama-versjonen."""
        from ki_lokal import MODELL, SEED, TEMPERATUR

        for rad in radene:
            assert rad.tjeneste == LOKAL and rad.modell == MODELL, rad.emne.symbol
            assert rad.promptversjon == PROMPTVERSJON, rad.emne.symbol
            assert rad.modell_id and rad.ollama_versjon, rad.emne.symbol
            assert rad.seed == SEED and rad.temperatur == TEMPERATUR, rad.emne.symbol
            assert rad.maskinvare in MASKINVARE, rad.emne.symbol

    def test_avtrykket_fanger_et_endret_grunnlag(self, tmp_path):
        """Ville feilet hvis noen endret grunnlaget i fila uten aa lage
        teksten paa nytt."""
        innhold = json.loads(demo_ki.FIL.read_text(encoding="utf-8"))
        innhold["radene"][0]["grunnlag"]["styrke"] += 1
        fil = tmp_path / "endret.json"
        fil.write_text(json.dumps(innhold, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(demo_ki.UgyldigDemoKI, match="avtrykket"):
            demo_ki.les_radene(fil)


class TestDemokommandoen:
    def test_skriver_radene_uten_nett_og_uten_ollama(self, tmp_path, monkeypatch, radene):
        """Nettsperren er paa (AD-8), og Ollama og requests feiler hvis de
        kalles. Ville feilet hvis demokommandoen kalte modellen, eller ikke
        skrev KI-radene i demobasen."""
        import ki_lokal

        def kalt(*_a, **_k):
            raise AssertionError("demokommandoen kalte modellen")

        monkeypatch.setattr(ki_lokal.OllamaModell, "lag_tekst", kalt)
        monkeypatch.setattr(ki_lokal.OllamaModell, "sjekk", kalt)
        monkeypatch.setattr(ki_lokal, "http", kalt)
        sti = tmp_path / "demo.db"
        demo.lag_demobase(sti, skriv=lambda _: None)
        tilkobling = sqlite3.connect(sti)
        try:
            i_basen = SqliteKILogg(tilkobling, demo._klokke_for(demo.SLUTTDATO)).les_alle()
        finally:
            tilkobling.close()
        # Hele raden, ikke bare emnet og teksten (gjennomgangen, BH8).
        assert i_basen == radene

    def test_importerer_verken_modellen_eller_requests(self, tmp_path):
        """Ville feilet hvis demo.py eller lesingen i demo_ki.py importerte
        requests, ki_lokal eller ki_tekst, saa demokommandoen kunne naa
        Ollama. Kjoeres i en egen prosess, saa andre tester ikke har lastet
        modulene foer, og prosessen lager ogsaa en demobase i tmp_path, saa
        modulene sjekkes etter at radene er skrevet (gjennomgangen, BH8).
        eodhd lastes fra foer 3.4b, gjennom lagring_sqlite og lagring_fil, og
        tolker bare et svar uten aa importere requests."""
        kode = (
            "import sys; sys.path.insert(0, sys.argv[1]); import demo; "
            "demo.lag_demobase(__import__('pathlib').Path(sys.argv[2]), skriv=lambda _: None); "
            "print(sorted(m for m in ('requests', 'ki_lokal', 'ki_tekst', 'fetch_prices') if m in sys.modules))"
        )
        svar = subprocess.run(
            [sys.executable, "-I", "-c", kode, str(SRC), str(tmp_path / "demo.db")],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert svar.returncode == 0, svar.stderr
        assert svar.stdout.strip() == "[]", svar.stdout
        tilkobling = sqlite3.connect(tmp_path / "demo.db")
        try:
            assert tilkobling.execute("SELECT COUNT(*) FROM ki_logg").fetchone()[0] == len(demo_ki.les_radene())
        finally:
            tilkobling.close()

    def test_en_oedelagt_fil_gir_en_demo_uten_ki_tekst(self, tmp_path, monkeypatch):
        """NFR-04 (gjennomgangen, BH2 og ECH3): kan fila ikke leses, eller
        stemmer den ikke med demoen, lages demobasen likevel, uten KI-rader,
        og kommandoen sier hvorfor. Ville feilet hvis en ødelagt fil stoppet
        hele demoen, ogsaa i compose."""
        tilfeller = {
            "mangler": None,
            "ikke JSON": "{",
            "feil format": json.dumps({"format": True, "radene": []}),
        }
        innhold = json.loads(demo_ki.FIL.read_text(encoding="utf-8"))
        annen_dag = json.loads(json.dumps(innhold))
        annen_dag["radene"][0]["dato"] = "2026-10-08"
        tilfeller["en annen dag"] = json.dumps(annen_dag)
        to_like = json.loads(json.dumps(innhold))
        to_like["radene"].append(to_like["radene"][0])
        tilfeller["to rader for en aksje"] = json.dumps(to_like)
        for navn, tekst in tilfeller.items():
            fil = tmp_path / f"{len(navn)}.json"
            if tekst is not None:
                fil.write_text(tekst, encoding="utf-8")
            monkeypatch.setattr(demo, "les_radene", lambda fil=fil: demo_ki.les_radene(fil))
            ut: list[str] = []
            sti = tmp_path / f"demo-{len(navn)}.db"
            demo.lag_demobase(sti, skriv=ut.append)
            assert any("Demoen lages uten KI-tekst" in u for u in ut), (navn, ut)
            tilkobling = sqlite3.connect(sti)
            try:
                assert tilkobling.execute("SELECT COUNT(*) FROM ki_logg").fetchone()[0] == 0, navn
            finally:
                tilkobling.close()

    def test_en_bom_i_fila_stopper_ikke_demoen(self, tmp_path):
        """ECH5: en editor kan legge en BOM foerst i fila."""
        fil = tmp_path / "bom.json"
        fil.write_bytes(b"\xef\xbb\xbf" + demo_ki.FIL.read_bytes())
        assert demo_ki.les_radene(fil) == demo_ki.les_radene()


class TestAksjesiden:
    def test_viser_teksten_med_merket_og_modellinja(self, klient, radene):
        """Uten Ollama og uten nett viser aksjesiden i demoen teksten med
        «Laget av KI» og modellen. Ville feilet hvis demobasen ikke hadde
        radene, eller siden ikke viste dem."""
        demo.lag_demobase(demo_sti(), skriv=lambda _: None)
        rad = next(r for r in radene if r.besto)
        side = klient.get(f"/aksje/{rad.emne.symbol}").data.decode("utf-8")
        assert "Eksempeltall" in side
        assert f'<p class="ki-tekst">{escape(rad.tekst)}</p>' in side
        assert f"Laget av KI · {rad.modell}, {rad.tjeneste}." in side

    def test_en_tekst_som_ikke_besto_vises_ikke(self, klient, radene, monkeypatch):
        """FR-604 (gjennomgangen, BH10 og ECH2): lages tekstene paa nytt, og
        en ikke bestaar, viser siden grunnen og ikke modellens tekst. Ville
        feilet hvis demoen viste en tekst som ikke besto kontrollen."""
        from dataclasses import replace

        rad = next(r for r in radene if r.besto)
        endret = [replace(r, besto=False, grunn="1: retningen") if r is rad else r for r in radene]
        monkeypatch.setattr(demo, "les_radene", lambda: endret)
        demo.lag_demobase(demo_sti(), skriv=lambda _: None)
        side = klient.get(f"/aksje/{rad.emne.symbol}").data.decode("utf-8")
        assert escape(rad.tekst) not in side and '<p class="ki-tekst">' not in side
        assert "teksten sa mer enn regelen" in side

    def test_modellens_tekst_escapes(self, klient, radene, monkeypatch):
        """Gjennomgangen, BH12: modellens tekst kommer fra en fil i repoet og
        vises med autoescape i malen. Ville feilet hvis teksten kom ut som
        HTML."""
        from dataclasses import replace

        rad = next(r for r in radene if r.besto)
        farlig = rad.tekst + " <script>x</script> & 'a'"
        endret = [replace(r, tekst=farlig) if r is rad else r for r in radene]
        monkeypatch.setattr(demo, "les_radene", lambda: endret)
        demo.lag_demobase(demo_sti(), skriv=lambda _: None)
        side = klient.get(f"/aksje/{rad.emne.symbol}").data.decode("utf-8")
        assert "<script>x</script>" not in side
        assert f'<p class="ki-tekst">{escape(farlig)}</p>' in side

    def test_knappen_skjuler_og_viser_teksten(self, klient, radene):
        """FR-601: «Skjul KI-teksten» tar teksten bort, og «Vis KI-teksten»
        gir den tilbake. Ville feilet hvis knappen ikke virket i demoen."""
        demo.lag_demobase(demo_sti(), skriv=lambda _: None)
        rad = next(r for r in radene if r.besto)
        adresse = f"/aksje/{rad.emne.symbol}"
        tekst = f'<p class="ki-tekst">{escape(rad.tekst)}</p>'
        paa = klient.get(adresse).data.decode("utf-8")
        assert tekst in paa and ">Skjul KI-teksten</button>" in paa
        svar = klient.post("/ki", data={"til": "av", "tilbake": adresse})
        assert svar.status_code == 303
        av = klient.get(adresse).data.decode("utf-8")
        assert tekst not in av and ">Vis KI-teksten</button>" in av
        klient.post("/ki", data={"til": "paa", "tilbake": adresse})
        assert tekst in klient.get(adresse).data.decode("utf-8")


class _Falsk:
    tjeneste = LOKAL
    modell = "gemma4:e4b"

    def __init__(self, tekst="Regelen gir dette signalet."):
        self.tekst = tekst
        self.kall = 0

    def sjekk(self):
        return None

    def lag_tekst(self, prompt):
        self.kall += 1
        return Modellsvar(
            tekst=self.tekst,
            modell=self.modell,
            modell_id="abcdef123456",
            seed=42,
            temperatur=0.0,
            maskinvare="gpu",
            ollama_versjon="0.0.0",
        )


class TestLagTekstene:
    def test_lager_en_rad_per_aksje_og_ingen_ny_runde(self, tmp_path, vurderingene):
        """FR-604: én runde. En tekst som ikke bestaar, staar som den ble, og
        modellen kalles én gang per aksje. Ville feilet hvis lag_tekstene
        proevde paa nytt for aa faa en bedre tekst."""
        modell = _Falsk("Dette er et kjøpssignal for aksjen.")
        fil = tmp_path / "radene.json"
        radene = demo_ki.lag_tekstene(modell, fil, skriv=lambda _: None)
        med_vurdering = [s for s, v in vurderingene.items() if isinstance(v, Vurdering)]
        assert modell.kall == len(radene) == len(med_vurdering)
        assert all(not r.besto and r.tekst == modell.tekst for r in radene)
        assert [r.emne for r in demo_ki.les_radene(fil)] == [r.emne for r in radene]

    def test_roerer_ikke_basene_i_data(self, tmp_path):
        """Regel 22: demobasen lages i en midlertidig mappe. Ville feilet hvis
        lag_tekstene skrev demo.db der webserveren leter."""
        demo_ki.lag_tekstene(_Falsk(), tmp_path / "radene.json", skriv=lambda _: None)
        assert not demo_sti().exists()

    def test_rundtur_gjennom_fila(self, radene):
        """Ville feilet hvis et felt falt bort mellom raden og fila: hvert
        felt i KIRad utenom emnet og grunnlaget staar i FELTENE, og radene
        skrevet paa nytt er de samme som det som staar i fila, tegn for tegn
        i JSON (gjennomgangen, BH7)."""
        from dataclasses import fields

        from kilogg import KIRad

        assert set(demo_ki.FELTENE) == {f.name for f in fields(KIRad)} - {"emne", "grunnlag"}
        i_fila = json.loads(demo_ki.FIL.read_text(encoding="utf-8"))["radene"]
        assert [demo_ki.til_json(r) for r in radene] == i_fila

    def test_en_kjoering_som_ikke_er_hel_skriver_ikke_fila(self, tmp_path):
        """Gjennomgangen, BH4, ECH1 og VG4: svarer ikke modellen, eller feiler
        den for en aksje, staar den gamle fila. Ville feilet hvis
        lag_tekstene skrev over fila med en tom eller avkortet liste."""
        from ki_modell import ModellFeilet

        class Feiler(_Falsk):
            def lag_tekst(self, prompt):
                self.kall += 1
                raise ModellFeilet("Ollama svarer ikke (kjører den?)")

        class IkkeKlar(_Falsk):
            def sjekk(self):
                return "Ollama svarer ikke (kjører den?)"

        fil = tmp_path / "radene.json"
        fil.write_text("den gamle", encoding="utf-8")
        for modell in (Feiler(), IkkeKlar()):
            with pytest.raises(demo_ki.UgyldigDemoKI, match="ikke endret"):
                demo_ki.lag_tekstene(modell, fil, skriv=lambda _: None)
            assert fil.read_text(encoding="utf-8") == "den gamle"
            assert not fil.with_name(fil.name + ".ny").exists()
