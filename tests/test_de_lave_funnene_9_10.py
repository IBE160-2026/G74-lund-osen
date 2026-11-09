"""Story 9.10: de lave funnene fra 10.6, 8.8 og 8.11b (ekstravinduet 09.11).

Spesifikasjonen er spec-9-10-de-lave-funnene.md. Hver test lager sin egen
base under tmp_path (regel 22), og ingen test gjør nettkall (AD-8). Kursene
er oppdiktet, ingen tall fra kildene (regel 16).
"""

import inspect
import sqlite3
from datetime import datetime, timedelta

import pytest

import app as app_modul
import ferdige_lister
import lagring_sqlite
from ki_tekst import lag_ki_tekster
from lagring_sqlite import aapne_base
from test_ferdige_lister_8_11b import DNB_RADER, EQNR_RADER, _kurser, _median
from test_ki_dagen import _Teller, dagens_rad
from test_ki_tekst import OEYEBLIKK, TIRSDAG, kjoer
from test_valg import med_boersen


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


def _sql(sti, sql, *argumenter):
    t = sqlite3.connect(sti)
    try:
        with t:
            return t.execute(sql, argumenter).fetchall()
    finally:
        t.close()


class TestHovedindeksenForDagen:
    """10.6 ECH14: teksten om dagen venter til hovedindeksen har en rad for dagen."""

    def test_teksten_venter_paa_indeksen_og_lages_ved_neste_forsoek(self, stier):
        """Ville feilet hvis teksten om dagen ble laget med et grunnlag uten
        hovedindeksen når indeksen manglet raden for dagen, for da sto raden,
        og siden ville regnet et annet grunnlag når indeksen kom, og aldri vist
        teksten. Neste forsøk med indeksen lager den."""
        raa, base = stier
        kjoer(raa, base, None)
        raden = _sql(base, "SELECT * FROM indeks WHERE dato = ?", TIRSDAG.isoformat())
        assert raden, "testbasen skulle hatt hovedindeksen for dagen"
        _sql(base, "DELETE FROM indeks WHERE dato = ?", TIRSDAG.isoformat())
        modell, linjer = _Teller(), []
        lag_ki_tekster(base, TIRSDAG, lambda: OEYEBLIKK, modell, linjer.append, med_dagen=True)
        assert modell.dagkall == 0 and dagens_rad(base) is None
        assert "Teksten om dagen: venter til hovedindeksen har en rad for dagen." in "\n".join(linjer)
        plasser = ", ".join("?" * len(raden[0]))
        _sql(base, f"INSERT INTO indeks VALUES ({plasser})", *raden[0])
        neste = _Teller()
        lag_ki_tekster(base, TIRSDAG, lambda: OEYEBLIKK, neste, lambda _: None, med_dagen=True)
        assert neste.dagkall == 1 and dagens_rad(base) is not None

    def test_uten_hovedindeks_i_basen_lages_teksten_som_foer(self, stier):
        """Ville feilet hvis en base uten rader for hovedindeksen aldri fikk
        teksten om dagen; da står grunnlaget uten indeksen, som før."""
        raa, base = stier
        kjoer(raa, base, None)
        _sql(base, "DELETE FROM indeks")
        modell = _Teller()
        lag_ki_tekster(base, TIRSDAG, lambda: OEYEBLIKK, modell, lambda _: None, med_dagen=True)
        assert modell.dagkall == 1


class TestListaMedEtAnnetAntall:
    """10.6 VG10: hentingen og siden bruker samme liste når den ikke har 15."""

    def test_teksten_vises_med_14_aksjer_i_lista(self, stier, monkeypatch):
        """Ville feilet hvis hentingen regnet grunnlaget for dagen med en
        annen liste enn siden når lista ikke har 15 aksjer, for da ville
        siden aldri vist teksten."""
        raa, base = stier
        kjoer(raa, base, None)
        ut = _sql(base, "SELECT symbol FROM aksje WHERE ut IS NULL ORDER BY rowid DESC LIMIT 1")[0][0]
        _sql(base, "UPDATE aksje SET ut = ? WHERE symbol = ?", (TIRSDAG - timedelta(days=7)).isoformat(), ut)
        assert _sql(base, "SELECT count(*) FROM aksje WHERE ut IS NULL")[0][0] == 14
        # Hentingen igjen samme kveld: dagen er hentet, så den lager bare
        # KI-tekstene, med lista fra basen (fetch_prices.kjoer, 2.11).
        modell = _Teller()
        kjoer(raa, base, modell)
        rad = dagens_rad(base)
        assert modell.dagkall == 1 and rad is not None and rad.besto
        assert rad.grunnlag["aksjer"] == 14
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
        app_modul.app.config["TESTING"] = True
        side = app_modul.app.test_client().get("/").data.decode("utf-8")
        assert "Skrevet av gemma4:e4b" in side and "da kursene ble hentet." in side


class TestSorteringenIBryteren:
    """10.6 BH7 og ECH11: bryteren på forsiden beholder sorteringen."""

    def test_skjemaet_har_sorteringen(self, stier, monkeypatch):
        """Ville feilet hvis bryteren ved «Børsdagen kort fortalt» sendte
        tilbake til forsiden uten sorteringen."""
        raa, base = stier
        kjoer(raa, base, None)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
        app_modul.app.config["TESTING"] = True
        side = app_modul.app.test_client().get("/?sorter=kurs&orden=stigende").data.decode("utf-8")
        assert 'name="tilbake" value="/?sorter=kurs&amp;orden=stigende"' in side

    @pytest.mark.parametrize(
        ("tilbake", "ventet"),
        [
            ("/?sorter=kurs&orden=stigende", "/?sorter=kurs&orden=stigende#boersdagen-kort-fortalt"),
            (
                "/?periode=1-mnd&sorter=endring&orden=synkende",
                "/?periode=1-mnd&sorter=endring&orden=synkende#boersdagen-kort-fortalt",
            ),
            ("/?sorter=ukjent&orden=stigende", "/#boersdagen-kort-fortalt"),
            ("/?periode=1-mnd", "/?periode=1-mnd#boersdagen-kort-fortalt"),
            ("/", "/#boersdagen-kort-fortalt"),
            ("/?sorter=kurs&orden=stigende&x=1", "/"),
            ("//annen.side/?sorter=kurs&orden=stigende", "/"),
        ],
    )
    def test_bryteren_sender_tilbake_med_sorteringen(self, stier, monkeypatch, tilbake, ventet):
        """Ville feilet hvis sorteringen ble borte etter bryteren, eller en
        ukjent sortering eller en annen adresse ble sluppet gjennom."""
        raa, base = stier
        kjoer(raa, base, None)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        app_modul.app.config["TESTING"] = True
        svar = app_modul.app.test_client().post("/ki", data={"til": "av", "tilbake": tilbake})
        assert svar.status_code == 303 and svar.headers["Location"] == ventet


class TestVurderingeneEnGang:
    """8.8 BH8 og ECH8: aksjesiden leser vurderingene én gang."""

    def test_en_lesing_av_hele_historikken(self, stier, monkeypatch):
        """Ville feilet hvis aksjesiden leste hele vurderingshistorikken to
        ganger, én for dagene i grafen og én for setningen om dagene."""
        raa, base = stier
        kjoer(raa, base, None)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
        app_modul.app.config["TESTING"] = True
        fra_starten = []
        ekte = lagring_sqlite.SqliteVurderingslager.les_periode

        def tell(self, symbol, fra, til):
            if fra.year == 1:
                fra_starten.append((symbol, til))
            return ekte(self, symbol, fra, til)

        monkeypatch.setattr(lagring_sqlite.SqliteVurderingslager, "les_periode", tell)
        symbol = _sql(base, "SELECT symbol FROM aksje WHERE ut IS NULL ORDER BY rowid LIMIT 1")[0][0]
        svar = app_modul.app.test_client().get(f"/aksje/{symbol}")
        assert svar.status_code == 200
        assert len(fra_starten) == 1, fra_starten

    def test_setningen_om_dagene_bare_til_dagen_siden_viser(self):
        """Ville feilet hvis setningen om dagene talte med vurderinger etter
        dagen siden viser, når hele historikken er lest til siste dag."""
        kilde = inspect.getsource(app_modul._setningene_om_dagen)
        assert "if dag <= detalj.dato" in kilde


class TestKurseneIEnSpoerring:
    """8.11b BH4 og ECH4: kursene i vinduet i én spørring, og siste dag med primærnøkkelen."""

    @pytest.fixture
    def base(self, tmp_path, monkeypatch):
        sti = tmp_path / "db" / "ose.db"
        med_boersen(sti, [("EQNR", "Equinor ASA"), ("DNB", "DnB ASA")])
        _kurser(sti, "EQNR", EQNR_RADER)
        _kurser(sti, "DNB", DNB_RADER)
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {})
        return sti

    def test_samme_medianer_med_faerre_spoerringer(self, base):
        """Ville feilet hvis bransjelistene fikk andre medianer, eller kursene
        ble lest med én spørring per aksje."""
        t = aapne_base(base)
        spoerringer = []
        t.set_trace_callback(spoerringer.append)
        try:
            lister = ferdige_lister.lister(t)
        finally:
            t.set_trace_callback(None)
            t.close()
        assert lister["Energi"][0].median == _median(EQNR_RADER)
        assert lister["Finans"][0].median == _median(DNB_RADER)
        assert sum("FROM kurs" in s for s in spoerringer) <= 2, spoerringer

    def test_den_siste_dagen_leses_ikke_av_hele_kurs(self):
        """Ville feilet hvis den siste dagen ble lest med max(dato) over hele
        kurs, som må lese hver rad, og ikke med primærnøkkelen per aksje."""
        kilde = inspect.getsource(ferdige_lister._aksjene_i_lista)
        assert '"SELECT max(dato) FROM kurs"' not in kilde
        assert "SELECT max(dato) FROM kurs WHERE symbol = a.symbol" in kilde
