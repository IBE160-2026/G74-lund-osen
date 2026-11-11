"""Story 2.11: lista leses fra basen - FR-412, FR-409, AD-3, AD-7, AD-16, AD-21.

Spesifikasjonen er spec-2-11-lista-leses-fra-basen.md. Hver test lager sin
egen base under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import shutil
import sqlite3
from datetime import date, datetime, timedelta

import pytest

import app as app_modul
import lagring_sqlite
from kursdata import AKSJEUNIVERS
from lagring_sqlite import MIGRASJONSKATALOG, SqliteOversiktsleser, aapne_base, les_lista
from markedsoversikt import IKKE_I_LISTA, IKKE_VURDERT, les_tilstand
from migrering import migrer
from test_fetch_prices import (
    ATTEN,
    OEYEBLIKK_22_09,
    TIRSDAG_22_09,
    antall_rader,
    base_med_atten,
    kjoer_23,
)
from tilstand import Art, tilstand

BRANSJENE = (
    "Energi",
    "Finans",
    "Industri",
    "Materialer",
    "Shipping",
    "Telekom",
    "Sjømat",
    "Konsum",
    "Forbruk",
    "Teknologi",
    "Helse",
    "Eiendom",
    "Kraft",
)


def til_versjon(tmp_path, versjon: int):
    katalog = tmp_path / f"til_{versjon}"
    katalog.mkdir()
    for fil in sorted(MIGRASJONSKATALOG.glob("*.sql"))[:versjon]:
        shutil.copy(fil, katalog / fil.name)
    return katalog


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


class TestMigrasjonen:
    """Del A."""

    def test_inn_er_den_foerste_raden_i_vurdering(self, tmp_path):
        """Spørsmål 1: ville feilet hvis inn var datoen for den første kursen,
        eller en aksje uten vurdering fikk en dato."""
        tilkobling = sqlite3.connect(tmp_path / "v8.db")
        try:
            assert migrer(tilkobling, til_versjon(tmp_path, 8)) == 8
            tilkobling.execute(
                "INSERT INTO kurs (symbol, dato, slutt, justert_slutt, volum) VALUES ('EQNR', '2025-09-01', 1, 1, 1)"
            )
            for dato in ("2026-10-01", "2026-09-28"):
                tilkobling.execute(
                    "INSERT INTO vurdering (symbol, dato, grunn) VALUES ('EQNR', ?, 'symbol_feilet')", (dato,)
                )
            tilkobling.commit()
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 13
            inn = dict(tilkobling.execute("SELECT symbol, inn FROM aksje"))
            assert inn["EQNR"] == "2026-09-28" and inn["DNB"] is None
            assert tilkobling.execute("SELECT count(*) FROM aksje WHERE ut IS NOT NULL").fetchone()[0] == 0
        finally:
            tilkobling.close()

    @pytest.mark.parametrize("bransje", ["Test", "energi", "Olje", ""])
    def test_en_bransje_utenfor_de_13_avvises(self, tmp_path, bransje):
        """Tillegget 13.10: ville feilet hvis en aksje kunne komme inn uten
        bransje, eller med en som ikke er blant de 13, også ved en endring."""
        tilkobling = sqlite3.connect(tmp_path / "ose.db")
        try:
            migrer(tilkobling, MIGRASJONSKATALOG)
            with pytest.raises(sqlite3.IntegrityError, match="bransjen er ikke en av de 13"):
                tilkobling.execute(
                    "INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES ('NY', 'NY.OL', 'Ny', ?)", (bransje,)
                )
            with pytest.raises(sqlite3.IntegrityError, match="bransjen er ikke en av de 13"):
                tilkobling.execute("UPDATE aksje SET sektor = ? WHERE symbol = 'EQNR'", (bransje,))
        finally:
            tilkobling.close()

    @pytest.mark.parametrize("bransje", BRANSJENE)
    def test_de_13_godtas(self, tmp_path, bransje):
        tilkobling = sqlite3.connect(tmp_path / "ose.db")
        try:
            migrer(tilkobling, MIGRASJONSKATALOG)
            tilkobling.execute(
                "INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES ('NY', 'NY.OL', 'Ny', ?)", (bransje,)
            )
        finally:
            tilkobling.close()

    def test_de_13_er_de_samme_som_i_boersometeret(self):
        """Ville feilet hvis migrasjonen og boersometer.py hadde ulike bransjer."""
        from boersometer import BRANSJER

        sql = (MIGRASJONSKATALOG / "0009_lista.sql").read_text(encoding="utf-8")
        assert BRANSJER == BRANSJENE and all(sql.count(f"'{b}'") == 2 for b in BRANSJER)

    def test_ut_kan_ikke_vaere_foer_inn(self, tmp_path):
        tilkobling = sqlite3.connect(tmp_path / "ose.db")
        try:
            migrer(tilkobling, MIGRASJONSKATALOG)
            tilkobling.execute("UPDATE aksje SET inn = '2026-10-01' WHERE symbol = 'EQNR'")
            with pytest.raises(sqlite3.IntegrityError):
                tilkobling.execute("UPDATE aksje SET ut = '2026-09-01' WHERE symbol = 'EQNR'")
        finally:
            tilkobling.close()


def sett(base, symbol, **datoer):
    tilkobling = aapne_base(base)
    try:
        for felt, verdi in datoer.items():
            tilkobling.execute(f"UPDATE aksje SET {felt} = ? WHERE symbol = ?", (verdi, symbol))
        tilkobling.commit()
    finally:
        tilkobling.close()


class TestLista:
    """Del B."""

    def test_lista_paa_en_dag(self, tmp_path):
        """Ville feilet hvis en aksje som er tatt ut, eller ennå ikke kommet
        inn, var i lista, eller rekkefølgen ikke var den i aksje."""
        base = tmp_path / "ose.db"
        sett(base, "DNB", ut="2026-10-01")
        sett(base, "KOG", inn="2026-10-05")
        tilkobling = aapne_base(base)
        try:
            assert [a.symbol for a in les_lista(tilkobling, date(2026, 9, 30))][:3] == ["EQNR", "DNB", "AKRBP"]
            paa = [a.symbol for a in les_lista(tilkobling, date(2026, 10, 1))]
            assert "DNB" not in paa and "KOG" not in paa and len(paa) == 13
            assert "KOG" in [a.symbol for a in les_lista(tilkobling, date(2026, 10, 5))]
        finally:
            tilkobling.close()

    def test_hentingen_henter_lista_i_basen(self, stier):
        """Ville feilet hvis en aksje som er tatt ut, ble hentet, eller kvoten
        ble regnet av 15 når lista hadde et annet antall."""
        raa, base = stier
        base_med_atten(base)
        sett(base, "TSTC", ut=TIRSDAG_22_09.isoformat())
        sett(base, "MPCC", ut=TIRSDAG_22_09.isoformat())
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09)
        assert fil is not None
        assert "TSTC.OL" not in kall and "MPCC.OL" not in kall and {"TSTA.OL", "TSTB.OL"} <= set(kall)
        assert len(kall) == 17 and "Dette koster 17 kall" in ut
        assert antall_rader(base, "vurdering") == 16

    def test_uten_base_er_lista_aksjeuniverset(self, stier):
        import fetch_prices as fp

        _, base = stier
        assert fp.lista_fra_basen(base, TIRSDAG_22_09) == AKSJEUNIVERS

    def test_en_base_foer_0009_leses_uten_migrering(self, tmp_path):
        """Ville feilet hvis hentingen migrerte basen før første kall, eller
        ikke kunne lese lista i en base en versjon bak (story 2.8)."""
        import fetch_prices as fp

        base = tmp_path / "ose.db"
        tilkobling = sqlite3.connect(base)
        try:
            migrer(tilkobling, til_versjon(tmp_path, 8))
            # Gjennomgangen (BH4, VG5): en aksje til, saa testen skiller «alle
            # aksjene i aksje» fra de 15 i AKSJEUNIVERS.
            tilkobling.execute("INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES ('NY', 'NY.OL', 'Ny', 'Kraft')")
            tilkobling.commit()
        finally:
            tilkobling.close()
        foer = base.read_bytes()
        lista = fp.lista_fra_basen(base, TIRSDAG_22_09)
        assert lista[:15] == AKSJEUNIVERS and [a.symbol for a in lista[15:]] == ["NY"]
        assert base.read_bytes() == foer


class TestTattUt:
    """Del C, AD-7 og AD-21."""

    def test_vurderingene_og_kursene_staar(self, stier):
        """Ville feilet hvis en aksje som ble tatt ut, mistet vurderingene sine."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        foer = antall_rader(base, "vurdering"), antall_rader(base, "kurs")
        sett(base, "DNB", ut=(TIRSDAG_22_09 + timedelta(days=1)).isoformat())
        assert (antall_rader(base, "vurdering"), antall_rader(base, "kurs")) == foer
        tilkobling = aapne_base(base)
        try:
            leser = SqliteOversiktsleser(tilkobling)
            assert "DNB" not in [p.aksje.symbol for p in leser.oversikt()]
            post = leser.post("DNB")
            assert post is not None and post.innhold is not None and post.ut == date(2026, 9, 23)
        finally:
            tilkobling.close()

    def test_en_dag_etter_ut_er_ikke_i_lista(self):
        """Ville feilet hvis dagene etter ble talt som dager vi ikke kjørte."""
        ut = date(2026, 9, 23)
        assert tilstand(None, date(2026, 9, 23), date(2026, 9, 30), ut).art is Art.IKKE_I_LISTA
        assert tilstand(None, date(2026, 9, 22), date(2026, 9, 30), ut).art is Art.IKKE_KJOERT
        # En helgedag er fortsatt ikke børsdag.
        assert tilstand(None, date(2026, 9, 26), date(2026, 9, 30), ut).art is Art.IKKE_BOERSDAG
        assert les_tilstand(None, date(2026, 9, 24), date(2026, 9, 30), ut)[1] == IKKE_I_LISTA
        assert les_tilstand(None, date(2026, 9, 24), date(2026, 9, 30))[1] == IKKE_VURDERT

    def test_aksjesiden_viser_en_aksje_som_er_tatt_ut(self, stier, monkeypatch):
        """Aksjedetaljen viser den fortsatt med historikken, og oversikten
        viser den ikke."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        sett(base, "DNB", ut="2026-09-23")
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 28, 12, 0).astimezone())
        app_modul.app.config["TESTING"] = True
        klient = app_modul.app.test_client()
        aksje = klient.get("/aksje/DNB?dag=2026-09-22")
        assert aksje.status_code == 200 and "DNB Bank" in aksje.data.decode("utf-8")
        historikk = klient.get("/aksje/DNB?maaned=2026-09").data.decode("utf-8")
        # Gjennomgangen (BH5): i cellen i historikken, ikke bare i hjelpen.
        assert f'<span class="tilstand">– {IKKE_I_LISTA}</span>' in historikk
        # Gjennomgangen (BH6, BH7, VG2): ikke på oversikten, i Min liste
        # eller i børsometeret, og sidene svarer 200.
        for adresse in ("/", "/min-liste?vis=alle", "/boersometer"):
            svar = klient.get(adresse)
            assert svar.status_code == 200 and "DNB Bank" not in svar.data.decode("utf-8"), adresse


def test_atten_i_basen_er_atten_i_lista(stier):
    """Ville feilet hvis lista i basen ble kuttet til de 15."""
    _, base = stier
    base_med_atten(base)
    tilkobling = aapne_base(base)
    try:
        assert les_lista(tilkobling, TIRSDAG_22_09) == ATTEN
    finally:
        tilkobling.close()


class TestEtterGjennomgangen:
    """Funnene fra gjennomgangen av 2.11."""

    def test_oversikten_foelger_regelen_i_les_lista(self, tmp_path):
        """BH1, ECH1, ECH2, VG2: ville feilet hvis en aksje med ut fram i tid
        forsvant fra oversikten, eller en med inn fram i tid sto der."""
        base = tmp_path / "ose.db"
        sett(base, "DNB", ut="2026-11-10")
        sett(base, "KOG", inn="2026-11-20")
        tilkobling = aapne_base(base)
        try:
            symboler = [p.aksje.symbol for p in SqliteOversiktsleser(tilkobling).oversikt(date(2026, 11, 9))]
            assert "DNB" in symboler and "KOG" not in symboler
            assert symboler == [a.symbol for a in les_lista(tilkobling, date(2026, 11, 9))]
        finally:
            tilkobling.close()

    def test_en_tom_liste_henter_ingenting(self, stier):
        """BH3, ECH3, VG3: ville feilet hvis en tom liste ble til de 15."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        for aksje in AKSJEUNIVERS:
            sett(base, aksje.symbol, ut="2026-09-23")
        fil, kall, ut = kjoer_23(raa, base, OEYEBLIKK_22_09 + timedelta(days=1))
        assert fil is None and kall == [] and "Lista i basen er tom" in ut

    def test_morgensjekken_bruker_lista_i_basen(self, stier):
        """VG1, ECH4 (høy): ville feilet hvis sjekken før steg 3 i
        kveldsjobben ventet på en aksje som er tatt ut, og aldri sa FERDIG."""
        import dagen_ferdig

        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        sett(base, "DNB", ut="2026-09-22")
        _, mangler = dagen_ferdig.mangler_for_dagen(base, OEYEBLIKK_22_09)
        assert not any("DNB" in m for m in mangler)

    def test_en_dato_som_ikke_finnes_avvises(self, tmp_path):
        """BH8, ECH7: ville feilet hvis basen godtok 2026-13-45."""
        tilkobling = sqlite3.connect(tmp_path / "ose.db")
        try:
            migrer(tilkobling, MIGRASJONSKATALOG)
            with pytest.raises(sqlite3.IntegrityError):
                tilkobling.execute("UPDATE aksje SET ut = '2026-13-45' WHERE symbol = 'EQNR'")
        finally:
            tilkobling.close()

    def test_en_aksje_som_er_tatt_ut_kan_ikke_merkes(self, tmp_path):
        """VG7: ville feilet hvis Min liste godtok en aksje som er tatt ut."""
        from lagring_sqlite import SqliteMinlistelager
        from minliste import UkjentAksje

        base = tmp_path / "ose.db"
        sett(base, "DNB", ut="2026-09-23")
        tilkobling = aapne_base(base)
        try:
            with pytest.raises(UkjentAksje):
                SqliteMinlistelager(tilkobling).merk("DNB")
        finally:
            tilkobling.close()
