"""Tester for Flask-ruta. Ingen nettverk, og ingen avhengighet til data/.

data/ er gitignorert, saa den finnes ikke i et ferskt klon. Testene monterer
derfor sitt eget oeyeblikksbilde i stedet for aa lese fra katalogen. Det er en
ekte SnapshotKilde med EODHDs feltnavn, saa appen proeves gjennom den samme
oversettelsen til Kursrad (SnapshotLeser) som i drift. Testene av
tidsstemplene monterer i stedet et MinneKurslager bak hent_leser, fordi et
oeyeblikksbilde har samme tid for alle symbolene. Unntaket er TestHentLeser,
som leser en tmp_path-katalog gjennom lagring_fil, aldri data/.
"""

import json
from datetime import date, datetime, timedelta, timezone

import pytest

import app as app_modul
import lagring_fil
from kursdata import Kursleser, Kursrad, MinneKurslager
from lagring_fil import SnapshotKilde, SnapshotLeser

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


def test_uten_kilde_viser_beskjed_i_stedet_for_aa_feile(klient, monkeypatch):
    monter(monkeypatch, None)

    svar = klient.get("/")

    assert svar.status_code == 200
    assert "Ingen kursdata" in svar.data.decode("utf-8")


def test_tom_kilde_gir_ogsaa_beskjed(klient, monkeypatch):
    monter(monkeypatch, snapshot({}))

    svar = klient.get("/")

    assert svar.status_code == 200
    assert "Ingen kursdata" in svar.data.decode("utf-8")


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
    assert "Ingen kursdata" in html
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


def test_ruta_gjoer_ingen_nettverkskall(klient, monkeypatch):
    """Vakt mot at visningen en dag begynner aa hente selv og spiser kvoten."""
    import requests

    def eksploder(*_args, **_kwargs):
        raise AssertionError("Visningen skal aldri gjoere API-kall")

    monkeypatch.setattr(requests, "get", eksploder)
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    assert klient.get("/").status_code == 200


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
        assert "median" in html

    def test_tegner_baade_kurs_og_ma50(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "kurslinje" in html
        assert "ma50linje" in html
        assert "<polyline" in html

    def test_kort_serie_viser_kurs_men_sier_at_signalet_mangler(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0, 101.0, 102.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert klient.get("/aksje/EQNR").status_code == 200
        assert "kunne ikke regnes" in html

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
    """hent_leser uten montering: Kursleseren kommer fra filadapteren (1.5).

    DATA_KATALOG i lagring_fil pekes mot tmp_path, saa data/ ikke roeres.
    """

    def test_gir_kursleser_fra_en_katalog_med_en_fil(self, monkeypatch, tmp_path):
        (tmp_path / "kurser-raa-2026-09-21.json").write_text(
            json.dumps({"hentet": HENTET, "serier": {"EQNR": [eodhd(r) for r in serie([100.0])]}}),
            encoding="utf-8",
        )
        monkeypatch.setattr(lagring_fil, "DATA_KATALOG", tmp_path)

        leser = app_modul.hent_leser()

        assert isinstance(leser, Kursleser)
        assert len(leser.serie("EQNR")) == 1

    def test_gir_none_fra_en_tom_katalog(self, monkeypatch, tmp_path):
        monkeypatch.setattr(lagring_fil, "DATA_KATALOG", tmp_path)

        assert app_modul.hent_leser() is None
