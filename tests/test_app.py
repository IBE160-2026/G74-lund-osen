"""Tester for Flask-ruta. Ingen nettverk, og ingen avhengighet til data/.

data/ er gitignorert, saa den finnes ikke i et ferskt klon. Testene monterer
derfor sitt eget oeyeblikksbilde i stedet for aa lese fra katalogen. Det er en
ekte SnapshotKilde med EODHDs feltnavn, saa appen proeves gjennom den samme
oversettelsen til Kursrad (SnapshotLeser) som i drift. Testene av
tidsstemplene monterer i stedet et MinneKurslager bak hent_leser, fordi et
oeyeblikksbilde har samme tid for alle symbolene. Unntakene er TestHentLeser,
test_rutene_gjoer_ingen_nettverkskall og TestBasenIWebserveren, som leser en
base i tmp_path (BASE_STI, pekt dit av conftest.py) gjennom den ekte
hent_leser, aldri data/ (story 2.2).
"""

import json
import re
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest

import app as app_modul
import lagring_fil
import lagring_sqlite
from kursdata import Kursleser, Kursrad, MinneKurslager
from lagring_fil import SnapshotKilde, SnapshotLeser
from lagring_sqlite import SqliteKurslager, aapne_base

HENTET = "2026-09-21T15:40:00+00:00"


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def serie(kurser, volumer=None):
    volumer = volumer or [1000] * len(kurser)
    return [
        Kursrad(
            dato=date(2026, 9, 1) + timedelta(days=i),
            slutt=kurs,
            justert_slutt=kurs,
            volum=volum,
        )
        for i, (kurs, volum) in enumerate(zip(kurser, volumer))
    ]


def eodhd(rad: Kursrad) -> dict:
    """Raden slik den staar i oeyeblikksbildet, med EODHDs feltnavn."""
    return {
        "date": rad.dato.isoformat(),
        "close": rad.slutt,
        "adjusted_close": rad.justert_slutt,
        "volume": rad.volum,
    }


def snapshot(serier: dict[str, list], hentet: str | None = HENTET) -> SnapshotKilde:
    """Et oeyeblikksbilde i minnet. Kursrad skrives som EODHD-rader, og en
    rad som allerede er en dict, staar urort - slik kan en test legge inn en
    rad oversettelsen ikke godtar."""
    return SnapshotKilde(
        hentet=hentet,
        serier={
            symbol: [eodhd(r) if isinstance(r, Kursrad) else r for r in rader]
            for symbol, rader in serier.items()
        },
    )


def monter(monkeypatch, kilde):
    """Oeyeblikksbildet i en SnapshotLeser bak hent_leser, slik filadapteren
    gir det. None monterer ingen data, som en tom data/."""
    leser = SnapshotLeser(kilde) if kilde is not None else None
    monkeypatch.setattr(app_modul, "hent_leser", lambda: leser)


def monter_lager(monkeypatch, tider: dict[str, datetime]):
    """Et MinneKurslager bak hent_leser, med egen tid per symbol. Slik kan en
    test gi symbolene ulik sist_hentet, noe et oeyeblikksbilde ikke kan."""
    lager = MinneKurslager()
    for symbol, tid in tider.items():
        lager.erstatt_serie(symbol, serie([100.0] * 60 + [101.0]), tid)
    monkeypatch.setattr(app_modul, "hent_leser", lambda: lager)


def fyll_basen(serier: dict[str, list[Kursrad]], hentet: str = HENTET) -> None:
    """Seriene inn i basen i BASE_STI, som conftest.py peker mot tmp_path."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = SqliteKurslager(tilkobling)
        for symbol, rader in serier.items():
            lager.erstatt_serie(symbol, rader, datetime.fromisoformat(hentet))
    finally:
        tilkobling.close()


TOM_TILSTAND = "Ingen kurser i basen ennå"


def test_uten_kilde_viser_beskjed_i_stedet_for_aa_feile(klient, monkeypatch):
    monter(monkeypatch, None)

    svar = klient.get("/")

    assert svar.status_code == 200
    html = svar.data.decode("utf-8")
    assert TOM_TILSTAND in html
    assert app_modul.HENTEKOMMANDO in html


def test_tom_kilde_gir_ogsaa_beskjed(klient, monkeypatch):
    monter(monkeypatch, snapshot({}))

    svar = klient.get("/")

    assert svar.status_code == 200
    assert TOM_TILSTAND in svar.data.decode("utf-8")


def test_viser_selskapsnavn_og_de_fem_kolonnene(klient, monkeypatch):
    lang = serie([100.0] * 60 + [104.0])
    monter(monkeypatch, snapshot({"EQNR": lang}))

    html = klient.get("/").data.decode("utf-8")

    for overskrift in ("Selskap", "Sluttkurs", "Endring", "Signalstyrke", "Retning"):
        assert f"<th>{overskrift}</th>" in html or f">{overskrift}</th>" in html
    assert "Equinor" in html


def test_retningen_vises_med_baade_tekst_og_symbol(klient, monkeypatch):
    """FR-103: symbolet staar ved siden av teksten, ikke i stedet for den.

    Teksten er FR-704s ord uendret - Positiv, ikke Opp.
    """
    stigende = serie([100.0] * 60 + [110.0])
    monter(monkeypatch, snapshot({"EQNR": stigende}))

    html = klient.get("/").data.decode("utf-8")

    assert "Positiv" in html
    assert "↑" in html
    assert ">Opp<" not in html


def test_symbolet_er_skjult_for_skjermlesere(klient, monkeypatch):
    """Teksten er den baerende kanalen. Pilen skal ikke leses opp i tillegg."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [110.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert 'aria-hidden="true"' in html


def test_aksje_uten_data_navngis_i_fotnoten(klient, monkeypatch):
    """Brukeren skal faa vite at oversikten er ufullstendig, ikke bare se faerre rader."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "Uten data i denne kilden" in html
    assert "DNB Bank" in html


def test_uleselig_symbol_navngis_i_fotnoten(klient, monkeypatch):
    """Et symbol med en rad oversettelsen ikke godtar, er manglende (1.4a).
    De andre vises som vanlig, og det manglende navngis."""
    ugyldig = [eodhd(r) for r in serie([100.0] * 61)]
    del ugyldig[30]["adjusted_close"]
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0]), "DNB": ugyldig}))

    html = klient.get("/").data.decode("utf-8")

    assert "Equinor" in html
    assert "Uten data i denne kilden" in html
    assert "DNB Bank" in html
    assert 'href="/aksje/DNB"' not in html


@pytest.mark.parametrize(
    "hentet", [None, "2026-09-21T15:40:00"], ids=["mangler", "uten-tidssone"]
)
def test_uleselig_hentet_gjoer_hele_oeyeblikksbildet_manglende(klient, monkeypatch, hentet):
    """SnapshotLeser (1.4a): kan hentet ikke leses, er hele oeyeblikksbildet
    manglende. Ingen rader vises, siden sier at kursdata mangler, og det
    staar ingen «data hentet». Detaljen gir 404."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}, hentet=hentet))

    html = klient.get("/").data.decode("utf-8")

    assert 'href="/aksje/EQNR"' not in html
    assert TOM_TILSTAND in html
    assert "data hentet" not in html
    assert klient.get("/aksje/EQNR").status_code == 404


def test_datoen_skrives_som_aaaa_mm_dd(klient, monkeypatch):
    """Datoen er en date i modellen, og malen skriver den som foer."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "Oslo Børs · 2026-10-31 ·" in html


def test_data_hentet_leses_fra_oeyeblikksbildet(klient, monkeypatch):
    """Sidens tidsstempel er oeyeblikksbildets hentet, lest som sist_hentet
    og vist i norsk tid: 15.40 UTC er 17.40 i Oslo i september."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "data hentet 2026-09-21 kl. 17.40" in html
    assert 'class="hentet"' not in html


def _selskapscelle(html: str, symbol: str) -> str:
    start = html.index(f'href="/aksje/{symbol}"')
    return html[start: html.index("</td>", start)]


class TestTidsstempler:
    """Story 1.4c, FR-101: sidens tidsstempel er det eldste, og en rad som er
    eldre enn den nyeste, viser sitt eget under selskapsnavnet."""

    FERSK = datetime(2026, 9, 24, 18, 5, tzinfo=timezone.utc)
    GAMMEL = datetime(2026, 9, 22, 18, 5, tzinfo=timezone.utc)

    def test_siden_viser_det_eldste(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        html = klient.get("/").data.decode("utf-8")

        assert "data hentet 2026-09-22 kl. 20.05" in html
        assert "data hentet 2026-09-24" not in html

    def test_den_eldste_raden_viser_sin_egen_tid_under_navnet(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        html = klient.get("/").data.decode("utf-8")

        assert "hentet 2026-09-22 kl. 20.05" in _selskapscelle(html, "DNB")
        assert "hentet" not in _selskapscelle(html, "EQNR")

    def test_alle_like_ferske_gir_ingen_egne(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.FERSK})

        html = klient.get("/").data.decode("utf-8")

        assert "data hentet 2026-09-24 kl. 20.05" in html
        assert 'class="hentet"' not in html

    def test_fortsatt_fem_kolonner(self, klient, monkeypatch):
        """Radens tid staar i selskapscellen, ikke i en sjette kolonne."""
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        html = klient.get("/").data.decode("utf-8")
        hode = html[html.index("<thead>"): html.index("</thead>")]
        kropp = html[html.index("<tbody>"): html.index("</tbody>")]

        assert hode.count("</th>") == 5
        rader = kropp.split("</tr>")[:-1]
        assert len(rader) == 2
        for rad in rader:
            assert rad.count("</td>") == 5

    def test_sommertid_over_midnatt(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": datetime(2026, 9, 24, 22, 30, tzinfo=timezone.utc)})

        html = klient.get("/").data.decode("utf-8")

        assert "data hentet 2026-09-25 kl. 00.30" in html

    def test_vintertid(self, klient, monkeypatch):
        """Demonstrasjonen er etter 25.10. Da er Oslo UTC+1, ikke +2."""
        monter_lager(monkeypatch, {"EQNR": datetime(2026, 11, 16, 22, 30, tzinfo=timezone.utc)})

        html = klient.get("/").data.decode("utf-8")

        assert "data hentet 2026-11-16 kl. 23.30" in html

    def test_detaljen_viser_symbolets_egen_tid(self, klient, monkeypatch):
        """Ikke sidens eldste: detaljen gjelder ett symbol."""
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        eqnr = klient.get("/aksje/EQNR").data.decode("utf-8")
        dnb = klient.get("/aksje/DNB").data.decode("utf-8")

        assert "data hentet 2026-09-24 kl. 20.05" in eqnr
        assert "data hentet 2026-09-22 kl. 20.05" in dnb

    def test_detaljen_i_vintertid(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": datetime(2026, 11, 16, 22, 30, tzinfo=timezone.utc)})

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "data hentet 2026-11-16 kl. 23.30" in html


def test_rutene_gjoer_ingen_nettverkskall(klient, monkeypatch, tmp_path):
    """Vakt mot at visningen en dag begynner aa hente selv og spiser kvoten.

    Het foer test_ruta_gjoer_ingen_nettverkskall. Den monterte hent_leser, saa
    lesingen ble aldri kjoert, og bare / ble proevd. Her monteres ingenting:
    basen i BASE_STI (tmp_path) har en serie, og begge rutene leser den
    gjennom den ekte hent_leser (story 2.2). requests.get byttes ut foer
    kallene, og sperren i conftest.py staar i tillegg.
    """
    import requests

    def eksploder(*_args, **_kwargs):
        raise AssertionError("Visningen skal aldri gjoere API-kall")

    monkeypatch.setattr(requests, "get", eksploder)
    fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})

    oversikt = klient.get("/")
    assert oversikt.status_code == 200
    assert 'href="/aksje/EQNR"' in oversikt.data.decode("utf-8"), "oversikten viser ikke dataene"

    detalj = klient.get("/aksje/EQNR")
    assert detalj.status_code == 200
    assert '<span class="verdi">101,00</span>' in detalj.data.decode("utf-8"), (
        "detaljen viser ikke dataene"
    )


class TestAksjedetalj:
    """Ruta /aksje/<symbol>. Egen kilde montert, aldri data/."""

    def test_ukjent_symbol_gir_404(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60)}))
        assert klient.get("/aksje/FINNESIKKE").status_code == 404

    def test_ticker_er_ikke_gyldig_i_ruta(self, klient, monkeypatch):
        """Ruta bruker vaart symbol, ikke EODHDs ticker."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60)}))
        assert klient.get("/aksje/EQNR.OL").status_code == 404

    def test_kjent_symbol_uten_data_gir_404(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({}))
        assert klient.get("/aksje/EQNR").status_code == 404

    def test_uten_kilde_gir_404(self, klient, monkeypatch):
        monter(monkeypatch, None)
        assert klient.get("/aksje/EQNR").status_code == 404

    def test_viser_de_tre_sjekkene_ved_navn(self, klient, monkeypatch):
        """FR-706: alle tre skal staa der, ogsaa de som ga 0."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        for navn in ("Trend", "Bevegelse", "Interesse"):
            assert navn in html

    def test_viser_maalingen_bak_hvert_fortegn(self, klient, monkeypatch):
        """Det som gjoer signalet etterproevbart: ikke bare +1, men mot hva."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "mot MA50" in html
        assert "standardavvik" in html
        assert "× medianen" in html

    def test_tegner_baade_kurs_og_ma50(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "kurslinje" in html
        assert "ma50linje" in html
        assert "<polyline" in html

    def test_kort_serie_viser_kurs_men_sier_at_signalet_mangler(self, klient, monkeypatch):
        """Kursen vises, og siden sier at signalet mangler. Sluttkursen er
        valgt saa den bare kan staa ett sted paa siden: i noekkeltallet."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0, 101.0, 123.45])}))

        svar = klient.get("/aksje/EQNR")
        html = svar.data.decode("utf-8")

        assert svar.status_code == 200
        assert html.count("123,45") == 1, "sluttkursen skal staa noeyaktig ett sted"
        assert '<span class="verdi">123,45</span>' in html, "sluttkursen vises ikke"
        assert "kunne ikke regnes" in html, "siden sier ikke at signalet mangler"

    def test_sier_hva_som_mangler_i_skjermbildet(self, klient, monkeypatch):
        """Meldinger og KI er ikke med enda. Det skal staa, ikke bare utebli."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "Børsmeldinger" in html
        assert "ikke med" in html

    def test_oversikten_lenker_til_detaljen(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/").data.decode("utf-8")

        assert 'href="/aksje/EQNR"' in html

    def test_detaljen_skriver_datoene_som_aaaa_mm_dd(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "Energi · 2026-11-19" in html
        assert "2026-09-01 til 2026-11-19" in html

    def test_uleselig_symbol_gir_404(self, klient, monkeypatch):
        ugyldig = [eodhd(r) for r in serie([100.0] * 61)]
        ugyldig[10]["date"] = "2026-9-11"
        monter(monkeypatch, snapshot({"EQNR": ugyldig}))

        assert klient.get("/aksje/EQNR").status_code == 404

    def test_detaljen_lenker_tilbake(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert 'href="/"' in html


class TestHentLeser:
    """hent_leser uten montering: Kursleseren er SqliteKurslager paa
    forespoerselens tilkobling (story 2.2). BASE_STI peker mot tmp_path."""

    @staticmethod
    def _i_en_forespoersel():
        with app_modul.app.test_request_context("/"):
            app_modul.app.preprocess_request()
            try:
                leser = app_modul.hent_leser()
                serie_lengde = len(leser.serie("EQNR")) if leser is not None else None
                return leser, serie_lengde
            finally:
                app_modul.app.do_teardown_appcontext()

    def test_gir_kursleser_fra_basen_med_en_serie(self):
        fyll_basen({"EQNR": serie([100.0])})

        leser, lengde = self._i_en_forespoersel()

        assert isinstance(leser, SqliteKurslager)
        assert isinstance(leser, Kursleser)
        assert lengde == 1

    def test_gir_none_fra_en_tom_base(self):
        assert self._i_en_forespoersel() == (None, None)


class TestBasenIWebserveren:
    """Story 2.2: webserveren leser kursene fra basen, migrerer en gang per
    prosess og base, og aapner en tilkobling per forespoersel."""

    def test_sidene_leser_basen_ikke_oeyeblikksbildet(self, klient, monkeypatch, tmp_path):
        """K5. Ville feilet hvis sidene fortsatt leste data/raa/ (M5)."""
        fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})
        (tmp_path / "kurser-raa-2026-09-21.json").write_text(
            json.dumps(
                {"hentet": HENTET, "serier": {"EQNR": [eodhd(r) for r in serie([200.0] * 60 + [202.0])]}}
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(lagring_fil, "RAA_KATALOG", tmp_path)

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert '<span class="verdi">101,00</span>' in html
        assert "202,00" not in html

    def test_tom_base_gir_tom_tilstand_med_kommandoen(self, klient):
        """K2 og K8. Basen finnes, men har ingen serie. Ville feilet med en
        feilside (M6) eller den gamle meldingen om data/ (M8)."""
        aapne_base(lagring_sqlite.BASE_STI).close()

        svar = klient.get("/")

        html = svar.data.decode("utf-8")
        assert svar.status_code == 200
        assert TOM_TILSTAND in html
        assert f"<code>{app_modul.HENTEKOMMANDO}</code>" in html
        assert "data/</code>" not in html
        assert "Ingen kursdata" not in html

    def test_basefil_som_mangler_lages_av_foerste_forespoersel(self, klient):
        """Matrisen: foerste forespoersel migrerer og lager en tom base, som
        hentingen gjoer. Siden viser tom tilstand, ikke en feil."""
        assert not lagring_sqlite.BASE_STI.exists()

        svar = klient.get("/")

        assert svar.status_code == 200
        assert TOM_TILSTAND in svar.data.decode("utf-8")
        assert lagring_sqlite.BASE_STI.is_file()

    def test_kommandoen_paa_den_tomme_siden_staar_i_readme(self):
        """Story 3.3: den tomme siden og README viser samme kommando, fra
        konstanten. Ville feilet hvis malen hadde sin egen kommando (M12)."""
        readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
        mal = (Path(app_modul.__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

        assert app_modul.HENTEKOMMANDO in readme
        assert "{{ hentekommando }}" in mal
        assert "fetch_prices" not in mal

    def test_migrer_kjoeres_en_gang_for_to_forespoersler(self, klient, monkeypatch):
        """K6. Ville feilet hvis migrer() ble kjoert ved hver forespoersel,
        fordi den alltid tar skrivelaas (M2)."""
        kall = []
        ekte = lagring_sqlite.migrer

        def spion(tilkobling, katalog):
            kall.append(katalog)
            return ekte(tilkobling, katalog)

        monkeypatch.setattr(lagring_sqlite, "migrer", spion)
        fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})
        kall.clear()

        assert klient.get("/").status_code == 200
        assert klient.get("/aksje/EQNR").status_code == 200

        assert len(kall) == 1

    def test_tilkoblingen_lukkes_etter_forespoerselen(self, klient, monkeypatch):
        """K7. Ville feilet hvis tilkoblingen ble staaende aapen (M3)."""
        aapnet = []
        ekte = app_modul.aapne_base

        def spion(sti, **navngitt):
            tilkobling = ekte(sti, **navngitt)
            if navngitt.get("kjoer_migrasjoner") is False:
                aapnet.append(tilkobling)
            return tilkobling

        monkeypatch.setattr(app_modul, "aapne_base", spion)
        fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})

        assert klient.get("/").status_code == 200
        assert klient.get("/aksje/EQNR").status_code == 200

        assert len(aapnet) == 2
        for tilkobling in aapnet:
            with pytest.raises(Exception, match="closed"):
                tilkobling.execute("SELECT 1")

    def test_en_forespoersel_i_en_annen_traad_faar_egen_tilkobling(self, klient):
        """K7 og forutsetningen i storyen: sqlite3 kan ikke dele en
        tilkobling mellom traader. Ville feilet hvis tilkoblingen laa paa
        modulnivaa (M4)."""
        import threading

        fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})
        assert klient.get("/").status_code == 200
        svar = []
        traad = threading.Thread(target=lambda: svar.append(klient.get("/aksje/EQNR").status_code))
        traad.start()
        traad.join()

        assert svar == [200]

    def test_basen_nyere_enn_koden_gir_503_med_grunnen(self, klient, tmp_path):
        """Matrisen: migreringen feiler. Siden svarer 503 med en beskjed, ikke
        en traceback. Ville feilet hvis feilen ble 500 (M10)."""
        import sqlite3

        katalog = tmp_path / "nyere"
        katalog.mkdir()
        for migrasjon in lagring_sqlite.MIGRASJONSKATALOG.glob("*.sql"):
            (katalog / migrasjon.name).write_bytes(migrasjon.read_bytes())
        neste = lagring_sqlite.siste_versjon(lagring_sqlite.MIGRASJONSKATALOG) + 1
        (katalog / f"{neste:04d}_ny.sql").write_text("CREATE TABLE ny (x INTEGER);", encoding="utf-8")
        lagring_sqlite.BASE_STI.parent.mkdir(parents=True, exist_ok=True)
        tilkobling = sqlite3.connect(lagring_sqlite.BASE_STI)
        lagring_sqlite.migrer(tilkobling, katalog)
        tilkobling.close()

        for rute in ("/", "/aksje/EQNR"):
            svar = klient.get(rute)
            html = svar.data.decode("utf-8")
            assert svar.status_code == 503, rute
            assert "kan ikke åpnes" in html
            assert "MigrasjonsFeil" in html
            assert "Traceback" not in html

    @staticmethod
    def _migrer_forbi_koden(tmp_path):
        """Basen i BASE_STI migreres med en migrasjon koden ikke har."""
        import sqlite3

        katalog = tmp_path / "nyere"
        katalog.mkdir(exist_ok=True)
        for migrasjon in lagring_sqlite.MIGRASJONSKATALOG.glob("*.sql"):
            (katalog / migrasjon.name).write_bytes(migrasjon.read_bytes())
        neste = lagring_sqlite.siste_versjon(lagring_sqlite.MIGRASJONSKATALOG) + 1
        (katalog / f"{neste:04d}_ny.sql").write_text("CREATE TABLE ny (x INTEGER);", encoding="utf-8")
        lagring_sqlite.BASE_STI.parent.mkdir(parents=True, exist_ok=True)
        tilkobling = sqlite3.connect(lagring_sqlite.BASE_STI)
        lagring_sqlite.migrer(tilkobling, katalog)
        tilkobling.close()

    def test_basen_migrert_forbi_koden_etter_oppstart_gir_503(self, klient, tmp_path):
        """Gjennomgangen (BH, ECH, VG): en nyere henting migrerer basen etter
        at webserveren har migrert den. Feilen kommer i hent_leser, og siden
        svarer 503, ikke 500. Ville feilet hvis rutene kalte hent_leser uten
        aa fange feilen (M13)."""
        fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})
        assert klient.get("/").status_code == 200
        self._migrer_forbi_koden(tmp_path)

        for rute in ("/", "/aksje/EQNR"):
            svar = klient.get(rute)
            html = svar.data.decode("utf-8")
            assert svar.status_code == 503, rute
            assert "RuntimeError" in html

    def test_feil_ved_aapning_per_forespoersel_gir_503(self, klient, monkeypatch):
        """VG: migreringen gaar, men aapningen per forespoersel feiler."""
        import sqlite3

        ekte = app_modul.aapne_base

        def laast(sti, **navngitt):
            if navngitt.get("kjoer_migrasjoner") is False:
                raise sqlite3.OperationalError("database is locked")
            return ekte(sti, **navngitt)

        monkeypatch.setattr(app_modul, "aapne_base", laast)

        for rute in ("/", "/aksje/EQNR"):
            svar = klient.get(rute)
            assert svar.status_code == 503, rute
            assert "OperationalError" in svar.data.decode("utf-8")

    def test_slettet_base_lages_paa_nytt(self, klient):
        """BH og ECH: basefila slettes mens webserveren kjoerer. Neste
        forespoersel migrerer paa nytt og viser tom tilstand, i stedet for 503
        til omstart. Ville feilet uten den nye migreringen (M14)."""
        assert klient.get("/").status_code == 200
        lagring_sqlite.BASE_STI.unlink()

        svar = klient.get("/")

        assert svar.status_code == 200
        assert TOM_TILSTAND in svar.data.decode("utf-8")
        assert lagring_sqlite.BASE_STI.is_file()

    def test_mislykket_migrering_proeves_igjen(self, klient, tmp_path):
        """BH: en migrering som feiler, merkes ikke, saa neste forespoersel
        proever igjen. Ville feilet hvis stien ble merket foer migreringen
        (M15)."""
        self._migrer_forbi_koden(tmp_path)
        assert klient.get("/").status_code == 503
        lagring_sqlite.BASE_STI.unlink()

        svar = klient.get("/")

        assert svar.status_code == 200
        assert TOM_TILSTAND in svar.data.decode("utf-8")

    def test_feilsiden_viser_ingen_stier(self, klient, tmp_path):
        """BH og ECH: 503-siden viser feiltypen og filnavnet, ikke stier paa
        maskinen, og ingen paastand om kvoten. Ville feilet med hele
        feilteksten (M16)."""
        self._migrer_forbi_koden(tmp_path)

        html = klient.get("/").data.decode("utf-8")

        assert "MigrasjonsFeil" in html
        assert str(tmp_path) not in html
        assert str(lagring_sqlite.MIGRASJONSKATALOG) not in html
        assert "kvote" not in html

    def test_feil_mens_sidene_leser_gir_503(self, klient, monkeypatch):
        """Raadet 03.10: en sqlite3-feil etter at leseren er laget, her en
        laast base i SqliteKurslager.serie, gir 503 med feiltypen paa begge
        rutene. Ville feilet uten haandteringen av sqlite3.Error (M18)."""
        import sqlite3

        fyll_basen({"EQNR": serie([100.0] * 60 + [101.0])})

        def laast(self, symbol):
            raise sqlite3.OperationalError("database is locked")

        monkeypatch.setattr(SqliteKurslager, "serie", laast)

        for rute in ("/", "/aksje/EQNR"):
            svar = klient.get(rute)
            html = svar.data.decode("utf-8")
            assert svar.status_code == 503, rute
            assert "kan ikke åpnes eller leses" in html
            assert "OperationalError" in html
            assert "database is locked" not in html

    def test_migrering_som_feiler_en_gang_proeves_igjen_uten_ny_fil(self, klient, monkeypatch):
        """Raadet 03.10: migrer() feiler en gang, og fila slettes ikke. Foerste
        forespoersel gir 503, neste gir 200, og migrer() er kalt to ganger.
        Ville feilet hvis stien ble merket foer migreringen (M15)."""
        from migrering import MigrasjonsFeil

        kall = []
        ekte = lagring_sqlite.migrer

        def spion(tilkobling, katalog):
            kall.append(katalog)
            if len(kall) == 1:
                raise MigrasjonsFeil("feiler en gang i testen")
            return ekte(tilkobling, katalog)

        monkeypatch.setattr(lagring_sqlite, "migrer", spion)

        assert klient.get("/").status_code == 503
        svar = klient.get("/")

        assert svar.status_code == 200
        assert TOM_TILSTAND in svar.data.decode("utf-8")
        assert len(kall) == 2

    def test_andre_ruter_roerer_ikke_basen(self, klient, monkeypatch):
        """BH: en 404 aapner ikke basen og lager ingen fil. Ville feilet hvis
        kroken gjaldt alle forespoersler (M17)."""
        kall = []
        monkeypatch.setattr(app_modul, "aapne_base", lambda *a, **k: kall.append(a))

        assert klient.get("/finnes-ikke").status_code == 404

        assert kall == []
        assert not lagring_sqlite.BASE_STI.exists()

    def test_oppstart_med_tom_base_gjoer_ingen_nettkall(self, klient, monkeypatch):
        """K1 og FR-401: foerste forespoersel, som migrerer, og sidene gjoer
        null nettkall, ogsaa med tom base. Ville feilet hvis oppstarten hentet
        (M1)."""
        import requests

        def eksploder(*_args, **_kwargs):
            raise AssertionError("Webserveren skal aldri gjoere nettkall")

        monkeypatch.setattr(requests, "get", eksploder)
        monkeypatch.setattr(requests, "request", eksploder)

        assert klient.get("/").status_code == 200
        assert klient.get("/aksje/EQNR").status_code == 404

    def test_import_av_app_roerer_ikke_basen(self):
        """Tillegget 18:05: ingen import av app kjoerer migrasjoner. En
        reload med en spion paa aapne_base gir null kall, og ingen fil."""
        import importlib

        kall = []
        try:
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(lagring_sqlite, "aapne_base", lambda *a, **k: kall.append(a))
                importlib.reload(app_modul)
                assert kall == []
                assert not lagring_sqlite.BASE_STI.exists()
        finally:
            importlib.reload(app_modul)


# --- Story 8.0: de rene feilene i de to skjermbildene -------------------------

NB = "\u00a0"


class _Tabell(HTMLParser):
    """Cellene i tbody, rad for rad, som tekst. Leser ikke stil eller farge."""

    def __init__(self):
        super().__init__()
        self.hode: list[str] = []
        self.rader: list[list[str]] = []
        self._i_kropp = False
        self._celle: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self._i_kropp = True
        elif tag == "tr" and self._i_kropp:
            self.rader.append([])
        elif tag in ("td", "th"):
            self._celle = []

    def handle_endtag(self, tag):
        if tag == "tbody":
            self._i_kropp = False
        elif tag in ("td", "th") and self._celle is not None:
            # Bare vanlige blanktegn slaas sammen. str.split() ville ogsaa
            # tatt det harde mellomrommet, som testene ser etter.
            tekst = re.sub(r"[ \t\r\n]+", " ", "".join(self._celle)).strip()
            if tag == "th":
                self.hode.append(tekst)
            elif self.rader:
                self.rader[-1].append(tekst)
            self._celle = None

    def handle_data(self, data):
        if self._celle is not None:
            self._celle.append(data)


def _tabell(html: str) -> _Tabell:
    tabell = _Tabell()
    tabell.feed(html)
    return tabell


def _stil(html: str) -> str:
    return html[html.index("<style>"): html.index("</style>")]


def _regel(stil: str, velger: str) -> str:
    treff = re.search(re.escape(velger) + r"\s*\{([^}]*)\}", stil)
    assert treff, f"ingen regel for {velger}"
    return treff.group(1)


class TestStory80:
    def test_tallene_i_oversikten_er_norske(self, klient, monkeypatch):
        """Regel 21: komma, hardt mellomrom, og aldri «-0,00»."""
        monter(monkeypatch, snapshot({"EQNR": serie([1234.5] * 60 + [1234.49])}))

        tabell = _tabell(klient.get("/").data.decode("utf-8"))
        selskap, kurs, endring, *_ = tabell.rader[0]

        assert kurs == f"1{NB}234,49"
        assert endring == f"0,00{NB}%", "en endring som rundes til null, har ikke fortegn"

    def test_ingen_tallcelle_har_punktum(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),
            "DNB": serie([200.0] * 60 + [197.5]),
        }))

        tabell = _tabell(klient.get("/").data.decode("utf-8"))

        assert len(tabell.rader) == 2
        for rad in tabell.rader:
            for celle in rad[1:4]:
                assert "." not in celle, celle
                assert "-0,00" not in celle, celle

    def test_aksjen_som_skiller_seg_ut_er_merket_med_tekst(self, klient, monkeypatch):
        """Ville feilet hvis en rad med styrke 2 og en med styrke 1 saa like ut
        for en som ikke ser farger. Testen leser bare teksten i cellene."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),   # styrke 2
            "DNB": serie([100.0] * 60 + [101.0]),    # styrke 1
        }))

        tabell = _tabell(klient.get("/").data.decode("utf-8"))
        styrke = {rad[0]: rad[3] for rad in tabell.rader}

        assert styrke["Equinor"] == "2 skiller seg ut"
        assert styrke["DNB Bank"] == "1"

    def test_fortsatt_noeyaktig_fem_kolonner(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),
            "DNB": serie([100.0] * 60 + [101.0]),
        }))

        tabell = _tabell(klient.get("/").data.decode("utf-8"))

        assert len(tabell.hode) == 5
        assert all(len(rad) == 5 for rad in tabell.rader)

    def test_selskapsnavnet_ser_ut_som_en_lenke_og_fokus_synes(self, klient, monkeypatch):
        """Leser stilen i malen, ikke hvordan nettleseren tegner den."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))
        stil = _stil(klient.get("/").data.decode("utf-8"))

        assert "text-decoration: none" not in _regel(stil, "td.selskap a")
        assert "underline" in _regel(stil, "td.selskap a")
        assert "outline" in _regel(stil, "td.selskap a:focus-visible")

    def test_veien_tilbake_er_like_tydelig(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))
        stil = _stil(klient.get("/aksje/EQNR").data.decode("utf-8"))

        assert "text-decoration: none" not in _regel(stil, "a.tilbake")
        assert "underline" in _regel(stil, "a.tilbake")
        assert "outline" in _regel(stil, "a.tilbake:focus-visible")

    def test_datoen_er_den_eldste_ikke_den_foerste_raden(self, klient, monkeypatch):
        """EQNR sorteres foerst (styrke 2), men DNB har eldre dato. Datoen
        velges etter samme prinsipp som «data hentet» (FR-101): den eldste."""
        # serie() starter 2026-09-01. EQNR har 61 rader og slutter 31.10,
        # DNB har 60 og slutter 30.10.
        lager = MinneKurslager()
        tid = datetime(2026, 9, 24, 18, 5, tzinfo=timezone.utc)
        lager.erstatt_serie("EQNR", serie([100.0] * 60 + [104.0]), tid)
        lager.erstatt_serie("DNB", serie([100.0] * 59 + [101.0]), tid)
        monkeypatch.setattr(app_modul, "hent_leser", lambda: lager)

        html = klient.get("/").data.decode("utf-8")

        assert [rad[0] for rad in _tabell(html).rader][0] == "Equinor"
        assert "Oslo Børs · 2026-10-30 ·" in html

    def test_fotnoten_sier_det_som_stemmer(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "under avklaring" not in html
        assert "kurs og volum" in html

    def test_tallene_i_detaljen_er_norske(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([1234.5] * 60 + [1250.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert f'<span class="verdi">1{NB}250,00</span>' in html
        regnestykker = re.findall(r'<td class="regnestykke">([^<]*)</td>', html)
        assert len(regnestykker) == 3
        for sjekk in regnestykker:
            assert "." not in sjekk, sjekk

        aksen = [t.strip() for t in re.findall(r'<text class="rutetekst"[^>]*>([^<]*)</text>', html)]
        assert aksen, "grafen har ingen tall paa aksen"
        for etikett in aksen:
            assert not re.search(r"\d{4}", etikett), etikett
            assert NB in etikett, etikett

    def test_endring_som_vises_som_null_har_ingen_farge(self, klient, monkeypatch):
        """+0,003 % vises som 0,00 %, og da skal cellen ikke vaere groenn."""
        monter(monkeypatch, snapshot({"EQNR": serie([1000.0] * 60 + [1000.03])}))

        html = klient.get("/").data.decode("utf-8")

        assert f"0,00{NB}%" in html
        assert 'class="tall opp"' not in html
        assert 'class="tall ned"' not in html

    def test_rad_uten_signal_er_ikke_merket(self, klient, monkeypatch):
        """Den andre veien av FR-705: uten signal staar ikke merket."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),   # styrke 2
            "DNB": serie([100.0, 101.0, 102.0]),     # for kort, uten signal
        }))

        tabell = _tabell(klient.get("/").data.decode("utf-8"))
        styrke = {rad[0]: rad[3] for rad in tabell.rader}

        assert "skiller seg ut" in styrke["Equinor"]
        assert "skiller seg ut" not in styrke["DNB Bank"]

    def test_manglende_signal_forklares_med_aa(self, klient, monkeypatch):
        """NFR-05: grunnen vises i begge skjermbildene."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0, 101.0, 102.0])}))

        assert "for å regne signal" in klient.get("/aksje/EQNR").data.decode("utf-8")
        assert "for å regne signal" in klient.get("/").data.decode("utf-8")
