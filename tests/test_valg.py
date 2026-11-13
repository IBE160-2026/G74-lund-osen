"""Story 2.12: velge og bytte aksjer - FR-412, AD-3, AD-7, AD-10, AD-21, NFR-06.

Spesifikasjonen er spec-2-12-velge-og-bytte-aksjer.md. Hver test lager sin
egen base under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import json
import re
from datetime import datetime, timedelta, timezone

import pytest

import app as app_modul
import ferdige_lister
import lagring_sqlite
import valg
from lagring_sqlite import aapne_base, les_lista
from test_fetch_prices import OEYEBLIKK_22_09, TIRSDAG_22_09, antall_rader, kjoer_23, kjoer_23_kode
from valg import ListaErFull, UgyldigValg, Valglager

KLOKKE = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
BOERSEN = [("NYA", "Ny Aksje ASA"), ("NYB", "Ny B ASA"), ("NYC", "Ny C ASA"), ("NYD", "Ny D ASA")]


# Story 8.22: de oppdiktede tickerne har en fast bransje, som de 295 i
# ferdige_lister.BRANSJE, fordi brukeren ikke lenger velger den.
FASTE = {"NYA": "Kraft", "NYB": "Helse", "NYC": "Kraft", "NYD": "Kraft"}


@pytest.fixture(autouse=True)
def faste_bransjer(monkeypatch):
    for kode, bransje in FASTE.items():
        monkeypatch.setitem(ferdige_lister.BRANSJE, kode, bransje)


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


def med_boersen(base, koder=BOERSEN):
    base.parent.mkdir(parents=True, exist_ok=True)
    tilkobling = aapne_base(base)
    try:
        with tilkobling:
            tilkobling.executemany("INSERT INTO boersliste (kode, navn) VALUES (?, ?)", koder)
    finally:
        tilkobling.close()


def lager(base):
    return Valglager(aapne_base(base), lambda: KLOKKE)


class TestValget:
    def test_foelg_skriver_bare_oensket(self, tmp_path):
        """AD-3: ville feilet hvis et valg i nettsiden skrev i aksje."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        l = lager(base)
        foer = l._t.execute("SELECT count(*) FROM aksje").fetchone()[0]
        l.folg("NYA", "Kraft")
        assert l._t.execute("SELECT count(*) FROM aksje").fetchone()[0] == foer
        assert [(o.handling, o.symbol, o.sektor) for o in l.ventende()] == [("folg", "NYA", "Kraft")]

    def test_den_nittende_avvises(self, tmp_path):
        """Ville feilet hvis lista kunne få 19 aksjer, regnet med ønskene."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        l = lager(base)
        for kode, _ in BOERSEN[:3]:
            l.folg(kode, "Kraft")
        assert l.antall() == 18
        with pytest.raises(
            ListaErFull, match="Appen følger allerede 18 aksjer, som er taket. Fjern en for å følge en annen."
        ):
            l.folg("NYD", "Kraft")

    def test_et_bytte_gaar_ogsaa_med_full_liste(self, tmp_path):
        """Ville feilet hvis et bytte ble avvist med full liste: det endrer
        ikke antallet."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        l = lager(base)
        for kode, _ in BOERSEN[:3]:
            l.folg(kode, "Kraft")
        l.folg("NYD", "Teknologi", bytt_ut="DNB")
        assert l.antall() == 18

    @pytest.mark.parametrize(
        "kode, bransje",
        [("FINNES", "Kraft"), ("NYA", "Olje"), ("NYA", ""), ("EQNR", "Energi")],
    )
    def test_ugyldige_valg(self, tmp_path, kode, bransje):
        """Ville feilet hvis en kode utenfor lista over Oslo Børs, en bransje
        utenfor de 13, eller en aksje som alt følges, ble godtatt. Da kunne en
        ticker som ikke finnes, koste et kall (22.10 kl. 23:14)."""
        base = tmp_path / "ose.db"
        med_boersen(base, [*BOERSEN, ("EQNR", "Equinor ASA")])
        with pytest.raises(UgyldigValg):
            lager(base).folg(kode, bransje)

    def test_angre_sletter_et_oenske_som_venter(self, tmp_path):
        base = tmp_path / "ose.db"
        med_boersen(base)
        l = lager(base)
        l.folg("NYA", "Kraft")
        l.angre(l.ventende()[0].id)
        assert l.ventende() == []

    def test_soeket_viser_ikke_aksjer_i_lista(self, tmp_path):
        base = tmp_path / "ose.db"
        med_boersen(base, [*BOERSEN, ("EQNR", "Equinor ASA")])
        assert [a.kode for a in lager(base).sok("a")] == ["NYA", "NYB", "NYC", "NYD"]

    def test_kallene(self):
        """Utdraget §1: siste henting, neste og igjen til nye forsøk."""
        assert valg.kallene(15, 1, 0) == (16, 17, 3)
        assert valg.kallene(18, 0, 0) == (19, 19, 1)

    @pytest.mark.parametrize("median, utenfor", [(None, True), (31_999_999.0, True), (32_000_000.0, False)])
    def test_utenfor_maalingen(self, median, utenfor):
        assert valg.utenfor_maalingen(median) is utenfor


class TestHentingen:
    def test_oensket_tas_i_bruk_ved_neste_henting(self, stier):
        """Ville feilet hvis hentingen ikke tok ønsket i bruk, eller tok inn en
        aksje uten bransje."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
        med_boersen(base)
        l = lager(base)
        l.folg("NYA", "Kraft")
        l.fjern("DNB")
        l._t.close()
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert "NYA.OL" in kall and "DNB.OL" not in kall
        assert "NYA er tatt inn i lista fra 2026-09-22." in ut
        tilkobling = aapne_base(base)
        try:
            lista = les_lista(tilkobling, TIRSDAG_22_09)
            nya = next(a for a in lista if a.symbol == "NYA")
            assert nya.sektor == "Kraft" and "DNB" not in [a.symbol for a in lista]
            assert valg.egne_i_lista(tilkobling) == {"NYA"}
            assert tilkobling.execute("SELECT count(*) FROM oenske WHERE tatt_i_bruk IS NULL").fetchone()[0] == 0
        finally:
            tilkobling.close()

    def test_vurderingene_for_den_som_fjernes_staar(self, stier):
        """AD-7: ville feilet hvis en aksje som ble byttet ut, mistet radene."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
        foer = antall_rader(base, "vurdering")
        med_boersen(base)
        l = lager(base)
        l.fjern("DNB")
        l._t.close()
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert antall_rader(base, "vurdering") == foer + 14

    def test_en_ticker_uten_rader_tas_ut_igjen_kvelden_etter(self, stier):
        """Spørsmål 6: ville feilet hvis en aksje uten kurser ble stående i
        lista, og utskriften sier det."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
        med_boersen(base)
        l = lager(base)
        l.folg("NYA", "Kraft")
        l._t.close()

        def hent(ticker, *a):
            from test_fetch_prices import serie_til

            return [] if ticker == "NYA.OL" else serie_til(TIRSDAG_22_09)

        kode, _, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, hent)
        assert kode == 1
        onsdag = OEYEBLIKK_22_09 + timedelta(days=1)
        _, kall, ut = kjoer_23(raa, base, onsdag)
        assert "NYA.OL" not in kall and "NYA ga ingen kurser" in ut
        tilkobling = aapne_base(base)
        try:
            assert tilkobling.execute("SELECT avvist FROM oenske WHERE symbol = 'NYA'").fetchone()[0]
        finally:
            tilkobling.close()

    def test_les_boerslista_uten_kall(self, stier, tmp_path):
        """Spørsmål 2: ville feilet hvis lista over Oslo Børs kostet et kall,
        eller tok med andre typer enn «Common Stock»."""
        import fetch_prices as fp

        _, base = stier
        fil = tmp_path / "liste.json"
        fil.write_text(
            json.dumps(
                [
                    {"Code": "NYA", "Name": "Ny Aksje ASA", "Type": "Common Stock"},
                    {"Code": "FOND", "Name": "Et fond", "Type": "FUND"},
                ]
            ),
            encoding="utf-8",
        )
        linjer = []
        fp.les_boerslista(base, fil, linjer.append)
        tilkobling = aapne_base(base)
        try:
            assert tilkobling.execute("SELECT kode FROM boersliste").fetchall() == [("NYA",)]
        finally:
            tilkobling.close()
        assert "0 kall brukt" in linjer[-1]


@pytest.fixture
def klient(stier, monkeypatch):
    raa, base = stier
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    med_boersen(base)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


class TestSidene:
    def test_dine_egne_aksjer_paa_oversikten(self, klient):
        """Utdraget §1: ville feilet hvis delen eller «x av 18» manglet."""
        side = klient.get("/").data.decode("utf-8")
        assert "Dine egne aksjer" in side and "0 egne · appen følger 15 av 18" in side
        assert 'href="/folg"' in side

    def test_foelg_en_aksje_fra_siden(self, klient):
        """Ville feilet hvis et valg i nettsiden startet et kall (AD-10): siden
        skriver bare ønsket, og det står som «Venter på henting»."""
        side = klient.get("/folg?q=ny").data.decode("utf-8")
        assert "Ny Aksje ASA" in side
        bekreft = klient.get("/folg?kode=NYA").data.decode("utf-8")
        assert (
            "Følge Ny Aksje ASA?" in bekreft
            and "Omsetningen er ikke målt ennå, så den merkes «Utenfor målingen»." in bekreft
        )
        svar = klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft"})
        assert svar.status_code == 303
        side = klient.get("/").data.decode("utf-8")
        assert "Venter på henting i kveld etter kl. 22." in side and "appen følger 16 av 18" in side

    def test_bransjen_er_fast(self, klient, stier):
        """Story 8.22 (svaret 10.11 kl. 13:38, som erstatter spørsmål 4): ville
        feilet hvis siden lot brukeren velge bransjen, eller et felt i
        skjemaet bestemte den."""
        bekreft = klient.get("/folg?kode=NYA").data.decode("utf-8")
        # Story 8.27: valget av aksje i notatpanelet (<template>) er ikke
        # skjemaet for å følge en aksje.
        bekreft = re.sub(r'<template id="notatpanel-mal">.*?</template>', "", bekreft, flags=re.S)
        assert "<select" not in bekreft and "Velg bransje" not in bekreft
        assert "Aksje på Oslo Børs · NYA · " in bekreft and "</svg>Kraft</p>" in bekreft
        svar = klient.post("/folg", data={"kode": "NYA", "sektor": "Helse"})
        assert svar.status_code == 303 and "feil=" not in svar.headers["Location"]
        t = aapne_base(stier[1])
        try:
            assert t.execute("SELECT sektor FROM oenske WHERE symbol = 'NYA'").fetchone() == ("Kraft",)
        finally:
            t.close()

    def test_full_liste_sier_det(self, klient):
        for kode, _ in BOERSEN[:3]:
            klient.post("/folg", data={"kode": kode, "sektor": "Kraft"})
        side = klient.get("/").data.decode("utf-8")
        assert (
            "Appen følger allerede 18 aksjer, som er taket. Fjern en for å følge en annen." in side
            and 'href="/folg"' not in side
        )
        svar = klient.post("/folg", data={"kode": "NYD", "sektor": "Kraft"})
        assert svar.status_code == 303 and "feil=Appen+f%C3%B8lger+allerede+18+aksjer" in svar.headers["Location"]

    def test_din_egen_liste_i_min_liste(self, klient):
        """Utdraget §2: ville feilet hvis kallene ikke ble regnet av lista."""
        side = klient.get("/min-liste").data.decode("utf-8")
        assert "Din egen liste" in side and "15 kall: de 15 aksjene" in side and "4 kall: margin" in side
        assert 'href="/folg?bytt=EQNR"' in side

    def test_en_annen_side_kan_ikke_velge(self, klient):
        svar = klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft"}, headers={"Origin": "https://annen.no"})
        assert svar.status_code == 403

    def test_ingen_forslag_fra_ki(self, klient):
        """NFR-06: ville feilet hvis siden foreslo aksjer, eller importerte KI-laget."""
        import inspect

        kilde = inspect.getsource(valg)
        assert "ki_" not in kilde and "anbefal" not in klient.get("/folg?q=ny").data.decode("utf-8")


def test_webserveren_henter_aldri(tmp_path):
    """AD-10: ville feilet hvis valg.py kalte nett eller importerte fetch_prices."""
    import inspect

    kilde = inspect.getsource(valg)
    assert "requests" not in kilde and "fetch_prices" not in kilde and "eodhd" not in kilde


def test_demoen_virker_likt(tmp_path, monkeypatch):
    """Tillegget 16.10 og spørsmål 10: ville feilet hvis valget, «x av 18» og
    «Dine egne aksjer» ikke virket i demoen, eller demoen ikke sa at den
    aldri henter."""
    import shutil

    import demo
    from lagring_sqlite import demo_sti

    mal = tmp_path / "demo.db"
    demo.lag_demobase(mal, skriv=lambda _: None)
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0).astimezone())
    klient = app_modul.app.test_client()
    bekreft = klient.get("/folg?kode=HVLK").data.decode("utf-8")
    assert "Følge Havlys Kraft?" in bekreft and "Det er over de 32 MNOK signalet er målt på." in bekreft
    assert "så den merkes «Utenfor målingen»" in klient.get("/folg?kode=NRDE").data.decode("utf-8")
    assert klient.post("/folg", data={"kode": "SKRH", "sektor": "Helse"}).status_code == 303
    side = klient.get("/").data.decode("utf-8")
    assert "1 egne · appen følger 16 av 18" in side
    assert "Venter på henting i kveld etter kl. 22." in side and "Demoen henter ingenting" in side


class TestEtterGjennomgangen:
    """Funnene fra gjennomgangen av 2.12."""

    def test_angre_et_oenske_om_aa_fjerne_kan_ikke_gi_19(self, tmp_path):
        """BH1, ECH1, VG1 (høy): ville feilet hvis lista kunne få 19 aksjer ved
        å angre et ønske om å fjerne."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        l = lager(base)
        l.fjern("DNB")
        for kode, _ in BOERSEN:
            l.folg(kode, "Kraft")
        assert l.antall() == 18
        fjern = next(o for o in l.ventende() if o.handling == "fjern")
        with pytest.raises(ListaErFull):
            l.angre(fjern.id)
        assert l.antall() == 18

    def test_et_bytte_angres_helt(self, tmp_path):
        """BH3, ECH2: ville feilet hvis bare den ene halvdelen av et bytte ble angret."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        l = lager(base)
        l.folg("NYA", "Kraft", bytt_ut="DNB")
        folg = next(o for o in l.ventende() if o.handling == "folg")
        l.angre(folg.id)
        assert l.ventende() == []

    def test_hentingen_tar_aldri_inn_mer_enn_18(self, tmp_path):
        """BH1, VG1: ville feilet hvis ønskene kunne gi mer enn 18 i aksje."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        tilkobling = aapne_base(base)
        try:
            for kode, navn in BOERSEN:
                tilkobling.execute(
                    "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', ?, ?, 'Kraft', 'x')",
                    (kode, navn),
                )
            tilkobling.commit()
            linjer = valg.ta_i_bruk(tilkobling, TIRSDAG_22_09)
            assert tilkobling.execute("SELECT count(*) FROM aksje WHERE ut IS NULL").fetchone()[0] == 18
            assert any("lista har alt 18 aksjer" in linje for linje in linjer)
        finally:
            tilkobling.close()

    def test_en_aksje_med_rader_samme_dag_slettes_ikke(self, stier):
        """BH4, ECH4 (AD-7): ville feilet hvis hentingen slettet en aksje med
        kurser, eller alle ønskene ble rullet tilbake."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        tilkobling = aapne_base(base)
        try:
            tilkobling.execute("INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', 'DNB', 'x')")
            tilkobling.commit()
            valg.ta_i_bruk(tilkobling, TIRSDAG_22_09)
            assert tilkobling.execute("SELECT ut FROM aksje WHERE symbol = 'DNB'").fetchone()[0] == "2026-09-23"
            assert tilkobling.execute("SELECT count(*) FROM vurdering WHERE symbol = 'DNB'").fetchone()[0] == 1
        finally:
            tilkobling.close()

    def test_soeket_tar_prosent_som_et_tegn(self, tmp_path):
        """ECH6: ville feilet hvis % ga alle aksjene."""
        base = tmp_path / "ose.db"
        med_boersen(base)
        assert lager(base).sok("%") == []

    def test_rutene_skriver_bare_oensket(self, klient, stier):
        """VG8, BH11: ville feilet hvis /folg, /fjern eller /angre skrev i
        aksje, kurs eller vurdering."""
        _, base = stier

        def tellinger():
            t = aapne_base(base)
            try:
                return [
                    t.execute(f"SELECT count(*) FROM {tab}").fetchone()[0] for tab in ("aksje", "kurs", "vurdering")
                ]
            finally:
                t.close()

        foer = tellinger()
        klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft"})
        klient.post("/fjern", data={"symbol": "DNB"})
        klient.post("/folg", data={"kode": "NYB", "sektor": "Helse", "bytt": "EQNR"})
        assert tellinger() == foer

    @pytest.mark.parametrize("sti, data", [("/fjern", {"symbol": "DNB"}), ("/angre", {"id": "1"})])
    def test_en_annen_side_kan_ikke_fjerne_eller_angre(self, klient, sti, data):
        assert klient.post(sti, data=data, headers={"Origin": "https://annen.no"}).status_code == 403

    def test_bytte_fra_min_liste(self, klient):
        """VG11: ville feilet hvis byttet sa et annet antall enn lista har."""
        side = klient.get("/folg?kode=NYA&bytt=DNB").data.decode("utf-8")
        assert "Bytt ut DNB Bank" in side and "Etter byttet er Ny Aksje ASA en av de 15" in side
        assert klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft", "bytt": "DNB"}).status_code == 303
        assert "Fjernes ved hentingen i kveld etter kl. 22." in klient.get("/min-liste").data.decode("utf-8")

    def test_kalltallene_paa_siden(self, klient):
        """VG4: ville feilet hvis tallene i dialogen var regnet feil i malen."""
        side = klient.get("/folg?kode=NYA").data.decode("utf-8")
        assert "Siste henting brukte 16 av 20 kall. Med denne bruker neste henting 17, og 3 er igjen" in side

    def test_en_aksje_i_lista_kan_ikke_foelges_igjen(self, klient, stier):
        """ECH11: ville feilet hvis siden viste «Følge …?» for en aksje i lista."""
        med_boersen(stier[1], [("DNB", "DnB ASA")])
        side = klient.get("/folg?kode=DNB").data.decode("utf-8")
        assert "Appen følger alt" in side and "Følg aksjen" not in side

    def test_en_feil_beholder_byttet(self, klient):
        """BH9, ECH9: ville feilet hvis en avvist forespørsel mistet byttet."""
        klient.post("/fjern", data={"symbol": "DNB"})
        svar = klient.post("/folg", data={"kode": "NYA", "sektor": "Kraft", "bytt": "DNB"})
        assert (
            svar.status_code == 303
            and "bytt=DNB" in svar.headers["Location"]
            and "kode=NYA" in svar.headers["Location"]
        )


def test_en_egen_aksje_staar_i_tabellen_med_merket(stier, monkeypatch):
    """VG5 og utdraget §1: ville feilet hvis en egen aksje sto uten merket
    «Egen» i tabellen etter hentingen, eller manglet i «Dine egne aksjer»."""
    raa, base = stier
    kjoer_23(raa, base, OEYEBLIKK_22_09 - timedelta(days=1))
    med_boersen(base)
    l = lager(base)
    l.folg("NYA", "Kraft")
    l._t.close()
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    side = app_modul.app.test_client().get("/").data.decode("utf-8")
    assert '<a href="/aksje/NYA">Ny Aksje ASA</a> <span class="egenmerke">Egen</span>' in side
    assert "Hentet. Står i tabellen over." in side and "1 egne · appen følger 16 av 18" in side
    # Story 8.11c (spørsmål 9 i 8.11b): etter hentingen regnes medianen av
    # kursene, som i de ferdige listene. Her sto «Omsetningen er ikke målt ennå.»
    assert (
        'class="utenformerke" title="Median daglig omsetning de 3 siste månedene er 0,1 MNOK, '
        "regnet av kursene til 22.09.2026." in side
    )


def test_dine_egne_aksjer_staar_foer_boersdagen_kort_fortalt(tmp_path, monkeypatch):
    """Designutdraget 08.11 §1 (rekkefølgen i §11 i utdraget 13.10): tabellen,
    så «Dine egne aksjer», så «Børsdagen kort fortalt». Ville feilet hvis
    «Børsdagen kort fortalt» sto over «Dine egne aksjer» på oversikten, eller
    en av delene manglet i demoen."""
    import shutil

    import demo
    from lagring_sqlite import demo_sti

    mal = tmp_path / "demo.db"
    demo.lag_demobase(mal, skriv=lambda _: None)
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0).astimezone())
    side = app_modul.app.test_client().get("/").data.decode("utf-8")
    tabellen = side.index("</table>")
    egne = side.index('id="dine-egne-aksjer"')
    boersdagen = side.index('id="boersdagen-kort-fortalt"')
    assert tabellen < egne < boersdagen
