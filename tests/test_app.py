"""Tester for Flask-ruta. Ingen nettverk, og ingen avhengighet til data/.

data/ er gitignorert, saa den finnes ikke i et ferskt klon. Testene fyller
derfor sin egen base i tmp_path (BASE_STI, pekt dit av conftest.py), og
sidene leser den gjennom de ekte portene (story 2.2 og 2.2b). monter tar et
oeyeblikksbilde med EODHDs feltnavn, oversetter det med SnapshotLeser som i
drift, skriver kursene og skriver saa vurderingen vurder() gir for nyeste
dag, slik hentekommandoen gjoer. Vurderingen skrives med adapterens egen
upsert, uten datokontrollen i skriv, fordi testseriene ikke ligger paa
inneveerende boersdag. Klokka sidene regner dagens dato av, staar fast.
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
from kursdata import Kursleser, Kursrad
from lagring_fil import SnapshotKilde, SnapshotLeser
from lagring_sqlite import SqliteKurslager, aapne_base
from signalberegning import vurder
from vurderingsdata import Grunn, Vurdering

HENTET = "2026-09-21T15:40:00+00:00"

# Etter alle testseriene, saa ingen dato er etter i dag (tilstand).
NAA = datetime(2026, 12, 31, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: NAA)


@pytest.fixture(autouse=True)
def utenfor_docker(monkeypatch):
    """Testene kjoerer som med uv. En test som vil se Docker-kommandoen,
    setter OSE_I_DOCKER selv (story 3.3)."""
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)


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


def skriv_vurdering(symbol: str, dato: date, innhold: Vurdering | Grunn) -> None:
    """Raden i vurdering, med adapterens egen upsert og uten datokontrollen
    i skriv. Bare for testene: testseriene ligger ikke paa inneveerende
    boersdag."""
    if isinstance(innhold, Vurdering):
        verdier = (*(getattr(innhold, k) for k in lagring_sqlite.VURDERINGSKOLONNER), None)
    else:
        verdier = (*(None for _ in lagring_sqlite.VURDERINGSKOLONNER), innhold.value)
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        with tilkobling:
            tilkobling.execute(lagring_sqlite._UPSERT, (symbol, dato.isoformat(), *verdier))
    finally:
        tilkobling.close()


def skriv_serie(symbol: str, rader: list[Kursrad], hentet: datetime, vurdert: bool = True):
    """Kursene inn i basen, og vurderingen for nyeste dag slik hentekommandoen
    regner den (vurder, story 2.5). vurdert=False er som --les-inn."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        SqliteKurslager(tilkobling).erstatt_serie(symbol, rader, hentet)
    finally:
        tilkobling.close()
    if vurdert:
        skriv_vurdering(symbol, rader[-1].dato, vurder(rader, rader[-1].dato))


def monter(monkeypatch, kilde, vurdert: bool = True):
    """Oeyeblikksbildet inn i basen, oversatt med SnapshotLeser slik
    filadapteren gir det, med vurderingen for nyeste dag. None gir en tom
    base, som foer foerste henting."""
    if kilde is None:
        return
    leser = SnapshotLeser(kilde)
    for symbol in kilde.serier:
        rader = leser.serie(symbol)
        if rader:
            skriv_serie(symbol, rader, leser.sist_hentet(symbol), vurdert)


def monter_lager(monkeypatch, tider: dict[str, datetime]):
    """Hvert symbol i basen med sin egen tid. Slik kan en test gi symbolene
    ulik sist_hentet, noe et oeyeblikksbilde ikke kan."""
    for symbol, tid in tider.items():
        skriv_serie(symbol, serie([100.0] * 60 + [101.0]), tid)


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
        # Signalstyrke har «?» etter ordet fra story 8.0b, i samme celle.
        # Story 8.0d, PR 2: «NOK» bare under Sluttkurs (svar 2, BH9).
        nok = '(<span class="under">NOK</span>)' if overskrift == "Sluttkurs" else ""
        # Story 8.15: navnet er en lenke som sorterer, med en vinkel.
        # Gjennomgangen (BH5): lenken er påkrevd ved de fire som kan sorteres.
        lenke = r'<a class="sorter[^"]*" href="[^"]*">' if overskrift != "Selskap" else ""
        etter = (r'<span class="skjult">[^<]*</span><svg class="vinkel"[^>]*><path[^>]*/></svg></a>'
                 if overskrift != "Selskap" else "")
        assert re.search(rf"<th[^>]*>{lenke}{overskrift}{etter}( <button[^<]*>\?</button>)?{nok}</th>", html), overskrift
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


def test_datoen_skrives_som_dd_mm(klient, monkeypatch):
    """Datoen er en date i modellen, og malen skriver den som «31.10» (8.0c).
    Klokka i testene staar i 2026, saa aaret vises ikke."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "Oslo Børs · 31.10 ·" in html


def test_data_hentet_leses_fra_oeyeblikksbildet(klient, monkeypatch):
    """Sidens tidsstempel er oeyeblikksbildets hentet, lest som sist_hentet
    og vist i norsk tid: 15.40 UTC er 17.40 i Oslo i september."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    # Story 8.0d, PR 2: i stripa, som «Oppdatert» (svar 5).
    assert "Oppdatert mandag 21.09 kl. 17.40" in html
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

        assert "Oppdatert tirsdag 22.09 kl. 20.05" in html
        # BH8: det nyeste tidspunktet står ingen steder på siden.
        assert "24.09" not in _synlig(html)

    def test_den_eldste_raden_viser_sin_egen_tid_under_navnet(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        html = klient.get("/").data.decode("utf-8")

        assert "hentet 22.09 kl. 20.05" in _selskapscelle(html, "DNB")
        assert "hentet" not in _selskapscelle(html, "EQNR")

    def test_alle_like_ferske_gir_ingen_egne(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.FERSK})

        html = klient.get("/").data.decode("utf-8")

        assert "Oppdatert torsdag 24.09 kl. 20.05" in html
        assert 'class="hentet"' not in html

    def test_fortsatt_fem_kolonner(self, klient, monkeypatch):
        """Radens tid staar i selskapscellen, ikke i en sjette kolonne."""
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        html = klient.get("/").data.decode("utf-8")
        hode = html[html.index("<thead>"): html.index("</thead>")]
        # Story 8.0e: to tbody, og overskriften for hver del er en egen rad.
        kropp = html[html.index("<tbody>"): html.rindex("</tbody>")]

        assert hode.count("</th>") == 5
        rader = re.findall(r'<tr(?! class="del)[^>]*>.*?</tr>', kropp, re.DOTALL)
        assert len(rader) == 2
        for rad in rader:
            assert rad.count("</td>") == 5

    def test_sommertid_over_midnatt(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": datetime(2026, 9, 24, 22, 30, tzinfo=timezone.utc)})

        html = klient.get("/").data.decode("utf-8")

        assert "Oppdatert fredag 25.09 kl. 00.30" in html

    def test_vintertid(self, klient, monkeypatch):
        """Demonstrasjonen er etter 25.10. Da er Oslo UTC+1, ikke +2."""
        monter_lager(monkeypatch, {"EQNR": datetime(2026, 11, 16, 22, 30, tzinfo=timezone.utc)})

        html = klient.get("/").data.decode("utf-8")

        assert "Oppdatert mandag 16.11 kl. 23.30" in html

    def test_detaljen_viser_symbolets_egen_tid(self, klient, monkeypatch):
        """Ikke sidens eldste: detaljen gjelder ett symbol."""
        monter_lager(monkeypatch, {"EQNR": self.FERSK, "DNB": self.GAMMEL})

        eqnr = klient.get("/aksje/EQNR").data.decode("utf-8")
        dnb = klient.get("/aksje/DNB").data.decode("utf-8")

        # Story 8.0d, PR 3: tidspunktet står bare i stripa (ECH8 i PR 2).
        assert "Oppdatert torsdag 24.09 kl. 20.05" in eqnr and "data hentet" not in eqnr
        assert "Oppdatert tirsdag 22.09 kl. 20.05" in dnb and "data hentet" not in dnb

    def test_detaljen_i_vintertid(self, klient, monkeypatch):
        monter_lager(monkeypatch, {"EQNR": datetime(2026, 11, 16, 22, 30, tzinfo=timezone.utc)})

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "Oppdatert mandag 16.11 kl. 23.30" in html


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

    def test_detaljen_skriver_datoene_som_dd_mm(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        # Story 8.0d, PR 3 (svar 18): «Oslo Børs · dato» under h1.
        assert "Oslo Børs · 19.11" in html
        assert "01.09 til 19.11" in html

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
        assert app_modul.HENTEKOMMANDO_DOCKER in readme
        assert "{{ hentekommando }}" in mal
        assert "fetch_prices" not in mal and "docker compose" not in mal

    def test_den_tomme_siden_i_docker_viser_docker_kommandoen(self, klient, monkeypatch):
        """Story 3.3, svar 1: med OSE_I_DOCKER=1, som Dockerfile setter, viser
        den tomme siden kommandoen for Docker. Ville feilet hvis appen saa bort
        fra variabelen og viste uv-kommandoen i containeren."""
        monkeypatch.setenv(app_modul.I_DOCKER, "1")
        aapne_base(lagring_sqlite.BASE_STI).close()

        html = klient.get("/").data.decode("utf-8")

        assert f"<code>{app_modul.HENTEKOMMANDO_DOCKER}</code>" in html
        assert app_modul.HENTEKOMMANDO not in html

    def test_bare_verdien_1_gir_docker_kommandoen(self, monkeypatch):
        """Ville feilet hvis enhver verdi, ogsaa tom eller 0, ga Docker-kommandoen."""
        for verdi, forventet in (("1", app_modul.HENTEKOMMANDO_DOCKER), ("0", app_modul.HENTEKOMMANDO),
                                 ("", app_modul.HENTEKOMMANDO)):
            monkeypatch.setenv(app_modul.I_DOCKER, verdi)
            assert app_modul.hentekommando() == forventet, verdi
        monkeypatch.delenv(app_modul.I_DOCKER)
        assert app_modul.hentekommando() == app_modul.HENTEKOMMANDO

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
        # Story 2.2b: oversikten leser gjennom Oversiktsleser.
        monkeypatch.setattr(lagring_sqlite.SqliteOversiktsleser, "oversikt", lambda self: laast(self, None))
        # Gjennomgangen av 2.2b: ogsaa oppslaget i aksjedetaljen (post).
        monkeypatch.setattr(lagring_sqlite.SqliteOversiktsleser, "post", laast)

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
    """Cellene i tbody, rad for rad, som tekst. Leser ikke stil eller farge.

    Story 8.0e: en rad med class="del" er overskriften for en del av
    tabellen, eller setningene fra 8.0c. Den staar i deler og ikke i rader,
    og del_av sier hvilken del hver rad i rader staar under ("" uten).

    Story 8.0d, PR 2: linja under navnet (ticker og bransje), antallet og
    grensen i baandene og «NOK» under kolonnenavnet staar i ekstra, med
    klassen som noekkel, og ikke i cellen. Cellen er det den var foer."""

    EKSTRA = ("linje", "antall", "bak", "under")

    def __init__(self):
        super().__init__()
        self.hode: list[str] = []
        self.rader: list[list[str]] = []
        self.deler: list[str] = []
        self.del_av: list[str] = []
        self.ekstra: dict[str, list[str]] = {k: [] for k in self.EKSTRA}
        self._i_kropp = False
        self._i_del = False
        self._celle: list[str] | None = None
        self._ekstra: tuple[str, int, list[str]] | None = None

    def handle_starttag(self, tag, attrs):
        if self._ekstra:
            navn, dybde, tekst = self._ekstra
            self._ekstra = (navn, dybde + 1, tekst)
            return
        klasser = (dict(attrs).get("class") or "").split()
        ekstra = next((k for k in self.EKSTRA if k in klasser), None)
        if ekstra and self._celle is not None:
            self._ekstra = (ekstra, 1, [])
            return
        if tag == "tbody":
            self._i_kropp = True
        elif tag == "tr" and self._i_kropp:
            self._i_del = "del" in (dict(attrs).get("class") or "").split()
            if not self._i_del:
                self.rader.append([])
                self.del_av.append(self.deler[-1] if self.deler else "")
        elif tag in ("td", "th"):
            self._celle = []

    def handle_endtag(self, tag):
        if self._ekstra:
            navn, dybde, tekst = self._ekstra
            if dybde > 1:
                self._ekstra = (navn, dybde - 1, tekst)
            else:
                self.ekstra[navn].append(re.sub(r"[ \t\r\n]+", " ", "".join(tekst)).strip())
                self._ekstra = None
            return
        if tag == "tbody":
            self._i_kropp = False
        elif tag in ("td", "th") and self._celle is not None:
            # Bare vanlige blanktegn slaas sammen. str.split() ville ogsaa
            # tatt det harde mellomrommet, som testene ser etter.
            tekst = re.sub(r"[ \t\r\n]+", " ", "".join(self._celle)).strip()
            if self._i_kropp and self._i_del:
                self.deler.append(tekst)
            elif tag == "th":
                self.hode.append(tekst)
            elif self.rader:
                self.rader[-1].append(tekst)
            self._celle = None

    def handle_data(self, data):
        if self._ekstra:
            self._ekstra[2].append(data)
        elif self._celle is not None:
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

        assert styrke["Equinor"] == "2 av 3 T +1 B +1 I 0 skiller seg ut"
        assert styrke["DNB Bank"] == "1 av 3 T 0 B +1 I 0"

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
        tid = datetime(2026, 9, 24, 18, 5, tzinfo=timezone.utc)
        skriv_serie("EQNR", serie([100.0] * 60 + [104.0]), tid)
        skriv_serie("DNB", serie([100.0] * 59 + [101.0]), tid)

        html = klient.get("/").data.decode("utf-8")

        assert [rad[0] for rad in _tabell(html).rader][0] == "Equinor"
        assert "Oslo Børs · 30.10 ·" in html

    def test_fotnoten_sier_det_som_stemmer(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "under avklaring" not in html
        assert "kurs og volum" in html

    def test_tallene_i_detaljen_er_norske(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([1234.5] * 60 + [1250.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert f'<span class="verdi">1{NB}250,00</span>' in html
        regnestykker = re.findall(r'<p class="regnestykke">([^<]*)</p>', html)
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
        # Story 2.2b: oversikten viser grunnen fra raden i vurdering.
        assert "signalet kunne ikke regnes" in klient.get("/").data.decode("utf-8")


def _rader_per_selskap(html: str) -> dict[str, list[str]]:
    """Radene i oversikten, med selskapsnavnet (uten egen tid) som noekkel."""
    return {rad[0].split(" hentet ")[0]: rad for rad in _tabell(html).rader}


class TestVurderingenPaaOversikten:
    """Story 2.2b: oversikten viser raden i vurdering for datoen til nyeste
    kurs, gjennom tilstand(), og regner aldri signalet (FR-408, FR-409)."""

    def test_vurderingen_kommer_fra_raden_ikke_fra_kursene(self, klient):
        """En flat serie ville gitt styrke 0. Raden sier 3, og siden viser 3."""
        rader = serie([100.0] * 60 + [100.0])
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, Vurdering(
            styrke=3, retning="Negativ", trend=-1, bevegelse=-1, interesse=-1,
            slutt=100.0, justert_slutt=100.0, trend_avvik=-0.05,
            dagens_endring=-0.04, standardavvik=0.01, volumforhold=0.2,
        ))

        rad = _rader_per_selskap(klient.get("/").data.decode("utf-8"))["Equinor"]

        assert rad[3].startswith("3")
        assert "Negativ" in rad[4]

    def test_ikke_vurdert_med_fotnoten(self, klient, monkeypatch):
        """Kurser uten rad i vurdering, som etter --les-inn. Ville feilet hvis
        siden regnet signalet naar raden mangler (M1)."""
        # 60 rader slutter fredag 30.10, en boersdag.
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 59 + [110.0])}), vurdert=False)

        html = klient.get("/").data.decode("utf-8")
        rad = _rader_per_selskap(html)["Equinor"]

        assert rad[3] == "– ikke vurdert"
        assert "Ukjent" in rad[4]
        assert "hentekommandoen har ikke skrevet en vurdering" in html
        assert "--les-inn" in html

    def test_ingen_fotnote_naar_alle_er_vurdert(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [110.0])}))
        assert "hentekommandoen har ikke skrevet" not in klient.get("/").data.decode("utf-8")

    @pytest.mark.parametrize("grunn,tekst", [
        (Grunn.SYMBOL_FEILET, "hentingen feilet"),
        (Grunn.KURS_IKKE_FRA_DAGEN, "ingen kurs fra dagen"),
        (Grunn.SIGNAL_IKKE_REGNET, "signalet kunne ikke regnes"),
    ])
    def test_grunnen_staar_synlig_under_streken(self, klient, grunn, tekst):
        """Beslutning 3: synlig liten tekst under «–», ikke i title. Ville
        feilet hvis en rad med grunn ble vist som styrke 0 (M5)."""
        rader = serie([100.0] * 60 + [101.0])
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, grunn)

        rad = _rader_per_selskap(klient.get("/").data.decode("utf-8"))["Equinor"]

        assert rad[3] == f"– {tekst}"
        assert "Ukjent" in rad[4]

    def test_styrke_0_vises_som_0(self, klient, monkeypatch):
        """Ville feilet hvis styrke 0 ble vist som «–» (M6)."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))

        rad = _rader_per_selskap(klient.get("/").data.decode("utf-8"))["Equinor"]

        assert rad[3] == "0 av 3 T 0 B 0 I 0"
        assert "Ingen" in rad[4]

    def test_gaarsdagens_vurdering_naar_dagens_rad_har_grunn(self, klient):
        """Tillegget 22:30: hentingen feilet for aksjen i dag, saa nyeste
        kurs er fra i gaar, og dagens rad har grunnen. Siden viser
        gaarsdagens vurdering med gaarsdagens dato (FR-101). Ville feilet
        hvis raden ble lest for en annen dato enn nyeste kurs (M2)."""
        rader = serie([100.0] * 60 + [110.0])
        i_gaar = rader[-1].dato
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET))
        skriv_vurdering("EQNR", i_gaar + timedelta(days=1), Grunn.SYMBOL_FEILET)

        html = klient.get("/").data.decode("utf-8")
        rad = _rader_per_selskap(html)["Equinor"]

        assert rad[3].split()[0] == str(vurder(rader, i_gaar).styrke)
        assert "hentingen feilet" not in html
        assert f"Oslo Børs · {i_gaar:%d.%m} ·" in html

    def test_selskapene_og_lista_over_manglende_kommer_fra_aksje(self, klient):
        """AD-21, merknaden 03.10: siden leser selskapene fra aksje, ikke fra
        AKSJEUNIVERS, og antar aldri 15. Ville feilet hvis lista over aksjer
        som mangler, kom fra AKSJEUNIVERS (M4)."""
        skriv_serie("EQNR", serie([100.0] * 61), datetime.fromisoformat(HENTET))
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            with tilkobling:
                tilkobling.execute("DELETE FROM aksje WHERE symbol IN ('DNO', 'MPCC')")
                tilkobling.execute("UPDATE aksje SET navn = 'Bank fra basen' WHERE symbol = 'DNB'")
        finally:
            tilkobling.close()

        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            uten_kurser = [n for (n,) in tilkobling.execute(
                "SELECT navn FROM aksje WHERE symbol != 'EQNR' ORDER BY rowid"
            )]
        finally:
            tilkobling.close()

        html = klient.get("/").data.decode("utf-8")
        fotnote = html.split("Uten data i denne kilden:")[1].split("</p>")[0]
        # Story 8.0d, PR 2b (VG1): M telles fra aksje, ikke fast 15 eller
        # AKSJEUNIVERS. Basen har 13 aksjer igjen.
        assert "<mark>0 av 13 aksjer</mark>" in html and " · 13 aksjer" in _synlig(html)

        assert "Bank fra basen" in fotnote
        assert "DNO" not in fotnote
        assert "MPC Container Ships" not in fotnote
        # Like mange navn som aksje har uten kurser, ikke et fast tall
        # (gjennomgangen av 2.2b).
        assert fotnote.strip().rstrip(".") == ", ".join(uten_kurser)


class TestVurderingenIDetaljen:
    """Story 2.2b: aksjedetaljen tegner grafen av kurs og forklarer sjekkene
    med maalingene i raden (FR-706). Har raden ingen vurdering, er svaret 200
    med grafen og tilstanden (FR-204)."""

    LAGRET = Vurdering(
        styrke=3, retning="Blandet", trend=1, bevegelse=-1, interesse=-1,
        slutt=100.0, justert_slutt=100.0, trend_avvik=0.031,
        dagens_endring=-0.035, standardavvik=0.011, volumforhold=4.95,
    )

    def test_sjekkene_fra_raden_ikke_fra_kursene(self, klient):
        """En flat serie ville gitt tre nuller. Ville feilet hvis detaljen
        forklarte med et signal regnet av serien (M7)."""
        rader = serie([100.0] * 61)
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, self.LAGRET)

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "3 av 3" in html
        assert "Blandet" in html
        assert "volum 4,95 × medianen" in html
        assert "mot MA50" in html

    def test_rad_med_grunn_gir_200_med_grafen_og_grunnen(self, klient):
        rader = serie([100.0] * 61)
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, Grunn.KURS_IKKE_FRA_DAGEN)

        svar = klient.get("/aksje/EQNR")
        html = svar.data.decode("utf-8")

        assert svar.status_code == 200
        assert "<svg" in html
        assert f"Ingen vurdering for {rader[-1].dato:%d.%m}: ingen kurs fra dagen." in html
        # Tabellen, ikke hjelpeteksten om kolonnen (story 8.0b).
        assert "<th>Målt mot</th>" not in html

    def test_lang_serie_med_signal_ikke_regnet_sier_ikke_antall_dager(self, klient):
        """Raadet 03.10: signal_ikke_regnet paa en serie som er lang nok, for
        eksempel naar porten ikke godtar tallene. Siden sier bare at signalet
        ikke kunne regnes, ikke «Trenger N dager, fikk M» (M12)."""
        rader = serie([100.0] * 61)
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, Grunn.SIGNAL_IKKE_REGNET)

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert f"Ingen vurdering for {rader[-1].dato:%d.%m}: signalet kunne ikke regnes." in html
        assert "for å regne signal" not in html

    def test_ikke_vurdert_med_fotnoten(self, klient, monkeypatch):
        # 60 rader slutter fredag 30.10, en boersdag.
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 59 + [110.0])}), vurdert=False)

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "ikke vurdert" in html
        assert "hentekommandoen har ikke skrevet en vurdering" in html
        # Tabellen, ikke hjelpeteksten om kolonnen (story 8.0b).
        assert "<th>Målt mot</th>" not in html

    def test_feil_i_spoerringen_gir_503_paa_begge_rutene(self, klient):
        """Gjennomgangen av 2.2b: en sqlite3-feil i selve spoerringen, her en
        base uten tabellen vurdering, gir 503 og ikke 404 eller 500. Ville
        feilet hvis oppslaget i aksjedetaljen svelget feilen (M15)."""
        skriv_serie("EQNR", serie([100.0] * 61), datetime.fromisoformat(HENTET))
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            with tilkobling:
                tilkobling.execute("DROP TABLE vurdering")
        finally:
            tilkobling.close()

        for rute in ("/", "/aksje/EQNR"):
            svar = klient.get(rute)
            assert svar.status_code == 503, rute
            assert "OperationalError" in svar.data.decode("utf-8"), rute

    def test_aksjen_slaas_opp_i_basen(self, klient):
        """Merknaden 03.10 under AD-21. Ville feilet hvis aksjedetaljen slo
        opp i AKSJEUNIVERS (M8): da sto navnet derfra, og DNO ga ikke 404."""
        skriv_serie("EQNR", serie([100.0] * 61), datetime.fromisoformat(HENTET))
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            with tilkobling:
                tilkobling.execute("UPDATE aksje SET navn = 'Navn fra basen' WHERE symbol = 'EQNR'")
                tilkobling.execute("DELETE FROM aksje WHERE symbol = 'DNO'")
        finally:
            tilkobling.close()

        assert "Navn fra basen" in klient.get("/aksje/eqnr").data.decode("utf-8")
        assert klient.get("/aksje/DNO").status_code == 404


def test_app_har_ingen_sql_og_regner_ikke_signalet():
    """Story 2.2b: spoerringen ligger bak porten, ikke i app.py, og sidene
    leser selskapene fra basen. Ville feilet hvis spoerringen ble flyttet inn
    i app.py (M10), eller AKSJEUNIVERS, beregn_signal eller vurder ble tatt
    inn igjen."""
    kode = Path(app_modul.__file__).read_text(encoding="utf-8")
    for ord_ in ("SELECT", "AKSJEUNIVERS", "beregn_signal", "vurder("):
        assert ord_ not in kode, ord_
    for navn in ("AKSJEUNIVERS", "beregn_signal", "vurder"):
        assert not hasattr(app_modul, navn), navn


class TestStory80c:
    """Story 8.0c, PR 1: merkingen i oversikten."""

    def test_styrken_staar_som_n_av_3(self, klient, monkeypatch):
        """Ville feilet hvis oversikten viste bare tallet, som foer 8.0c."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),   # styrke 2
            "DNB": serie([100.0] * 60 + [100.0]),    # styrke 0
        }))
        styrke = {rad[0]: rad[3] for rad in _tabell(klient.get("/").data.decode("utf-8")).rader}
        assert styrke["Equinor"].startswith("2 av 3")
        assert styrke["DNB Bank"] == "0 av 3 T 0 B 0 I 0"

    def test_tre_av_tre_har_gul_ring_og_to_av_tre_ikke(self, klient, monkeypatch):
        """designregler §3. Ville feilet uten ringen, eller med gult ved 2 av 3."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0], [1000] * 60 + [5000]),  # 3 av 3
            "DNB": serie([100.0] * 60 + [104.0]),                              # 2 av 3
        }))
        html = klient.get("/").data.decode("utf-8")
        # Story 8.0e PR 2: pillen staar ogsaa i linja over tabellen.
        tabell = html[html.index("<table"):]
        assert tabell.count('class="pille tre-av-tre"') == 1
        assert '<span class="pille tre-av-tre">3 av 3</span>' in tabell
        # Story 8.0d, PR 3: hvit pille ved 2 av 3 (gruppen 14.10 kl. 19:59).
        assert '<span class="pille to-av-tre">2 av 3</span>' in html
        ring = _regel(_stil(html), ".pille.tre-av-tre")
        assert "oransje" not in _regel(_stil(html), ".pille.to-av-tre")
        # Story 8.0d, PR 2: ringen i sterk oransje (designregler §3, 14.10).
        assert "border" in ring and "var(--oransje)" in ring

    def test_to_av_tre_merkes_med_mer_enn_lys_bakgrunn(self, klient, monkeypatch):
        """Svar 2: fet skrift og en strek til venstre. Ville feilet hvis raden
        bare hadde #fafafa, som foer 8.0c.

        Story 8.0d, PR 2: streken er 4 px i lys oransje ved 2 av 3, og i
        sterk oransje bare ved 3 av 3 (designregler §3, 14.10)."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))
        html = klient.get("/").data.decode("utf-8")
        stil = _stil(html)
        assert '<tr class="utslag">' in html
        assert "font-weight: 600" in _regel(stil, "tr.utslag td")
        strek = _regel(stil, "tr.utslag td:first-child")
        assert "inset 4px 0 0 var(--lys-oransje)" in strek
        assert "#fafafa" not in stil
        assert "var(--oransje)" not in _regel(stil, "tr.utslag td") + strek

    def test_overskriftene_staar_over_tallene(self, klient, monkeypatch):
        """Tillegget 11.10. Ville feilet hvis th.tall ble venstrejustert av
        regelen for th, td, som foer 8.0c."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        stil = _stil(klient.get("/").data.decode("utf-8"))
        assert "text-align: right" in _regel(stil, "th.tall")
        assert stil.index("th.tall") > stil.index("th, td")

    def test_setningen_naar_ingen_skilte_seg_ut(self, klient, monkeypatch):
        """Tillegget 05.10. Ville feilet hvis setningen manglet en dag der alle
        hadde 0 eller 1."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [101.0]),   # styrke 1
            "DNB": serie([100.0] * 61),              # styrke 0
        }))
        html = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer." in html

    def test_setningen_staar_ikke_med_tre_av_tre_og_ingen_paa_to(self, klient, monkeypatch):
        """Presiseringen kl. 14:33: én aksje paa 3 av 3 og ingen paa 2. Ville
        feilet hvis setningen bare saa etter styrke 2."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0], [1000] * 60 + [5000]),  # 3 av 3
            "DNB": serie([100.0] * 61),                                        # 0
        }))
        html = klient.get("/").data.decode("utf-8")
        assert "3 av 3" in html
        assert "Ingen aksjer skilte seg ut" not in html

    def test_setningen_staar_ikke_uten_en_eneste_vurdering(self, klient, monkeypatch):
        """Tillegget 05.10: ikke naar ingen rad har en vurdering."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}), vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        assert "Equinor" in html
        assert "Ingen aksjer skilte seg ut" not in html

    def test_terskelen_i_setningen_kommer_fra_parametre(self, klient, monkeypatch):
        """Ville feilet hvis 2 sto fast i malen."""
        import dataclasses

        import app as app_modul
        andre = dataclasses.replace(app_modul.STANDARD, terskel=3)
        monkeypatch.setattr(app_modul, "STANDARD", andre)
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))  # 2 av 3
        html = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut: ingen fikk 3 av 3 eller mer." in html

    # Del b: aksjesiden og fotnotene.

    def test_ga_kolonnen_har_tallet_og_ordet(self, klient, monkeypatch):
        """Tillegget 05.10. Ville feilet hvis Ga viste bare fortegnet, eller
        sa opp eller ned."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        # Story 8.0d, PR 3: tallet og ordet i resultatpillen i hvert sjekkort.
        celler = re.findall(r'<span class="resultat fortegn [a-z]+">([^<]*) <span class="ord">([^<]*)</span></span>', html)
        assert len(celler) == 3, celler
        par = {(tall, ord_) for tall, ord_ in celler}
        assert ("+1", "positiv") in par
        assert ("0", "ingen utslag") in par
        assert not re.search(r'class="ord">\s*(opp|ned)\b', html)

    def test_sjekkene_som_slo_ut_merkes_som_i_oversikten(self, klient, monkeypatch):
        """Tillegget 11.10. Ville feilet hvis radene bare hadde #fafafa.
        Story 8.0d, PR 3: sjekkene står som kort, og resultatet står i en
        pille med farge etter fortegnet (utdraget §8)."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        stil = _stil(html)
        assert '<section class="sjekkort bidro"' in html
        assert "background: var(--opp-bakgrunn)" in _regel(stil, ".sjekkort .resultat.opp")
        assert "#fafafa" not in stil

    def test_fotnoten_i_oversikten_sier_hvor_mange_som_slo_ut(self, klient, monkeypatch):
        """Punkt 4.4 i endringsforslaget 13.10. Ville feilet med «hvor kraftig»."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        html = klient.get("/").data.decode("utf-8")
        assert "Signalstyrken sier hvor mange av de 3 sjekkene som slo ut, ikke om du bør kjøpe eller selge." in html
        assert "Sluttkursen er den ujusterte kursen" in html
        assert "hvor kraftig" not in html

    def test_fotnoten_paa_aksjesiden_har_forbeholdet(self, klient, monkeypatch):
        """Presiseringen kl. 14:33 og tillegget 11.10: forbeholdet staar
        synlig. Ville feilet med «summen av tallene uten fortegn»."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert "Signalstyrken er hvor mange sjekker som slo ut: 2 av 3 ga utslag." in html
        assert "Ga noen +1 og noen -1, er retningen Blandet." in html
        assert "Signalstyrken sier ikke om du bør kjøpe eller selge." in html
        assert "summen av tallene" not in html

    # Del c: linja nederst og linja over tabellen.

    def test_under_arbeid_staar_nederst_paa_begge_sidene(self, klient, monkeypatch):
        """Tillegget 11.10, svar 4. Ville feilet hvis linja manglet paa en side."""
        import app as app_modul
        monkeypatch.setattr(app_modul, "UNDER_ARBEID", True)
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        for sti in ("/", "/aksje/EQNR"):
            html = klient.get(sti).data.decode("utf-8")
            assert '<p class="under-arbeid">Appen er under utvikling og ikke ferdig.</p>' in html, sti
            # Story 8.0d, PR 3: aksjesiden har sjekkort, ikke en tabell.
            # Gjennomgangen 15.10 (BH18): merket finnes, så testen feiler med
            # en melding og ikke ValueError hvis grafen mangler.
            siste = "<table" if sti == "/" else "<figure"
            assert siste in html, sti
            assert html.index('class="under-arbeid"') > html.index(siste), sti

    def test_under_arbeid_styres_av_en_innstilling(self, klient, monkeypatch):
        """Ville feilet hvis linja sto fast i malene og ikke kom fra UNDER_ARBEID."""
        import app as app_modul
        monkeypatch.setattr(app_modul, "UNDER_ARBEID", False)
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        for sti in ("/", "/aksje/EQNR"):
            assert "<p class=\"under-arbeid\">" not in klient.get(sti).data.decode("utf-8"), sti

    def test_den_ekte_basen_sier_oslo_boers_over_tabellen(self, klient, monkeypatch):
        """4a gjelder bare demoen. Ville feilet hvis «Eksempeltall» sto over
        tabellen uten demomerket."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        html = klient.get("/").data.decode("utf-8")
        assert "Oslo Børs · " in html
        assert "Eksempeltall" not in html and "Demoversjon" not in html

    # Etter gjennomgangen av PR #35.

    def test_setningen_staar_ikke_med_to_av_tre(self, klient, monkeypatch):
        """VG1: med STANDARD og én aksje paa 2 av 3 staar ikke setningen.
        Ville feilet hvis funksjonen saa etter 3 av 3 i stedet for terskelen."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),   # 2 av 3
            "DNB": serie([100.0] * 61),              # 0
        }))
        html = klient.get("/").data.decode("utf-8")
        assert "2 av 3" in html
        assert "Ingen aksjer skilte seg ut" not in html

    def test_bare_radene_over_terskelen_er_merket(self, klient, monkeypatch):
        """VG2: en rad med 1 av 3 skal ikke ha merkingen. Ville feilet hvis
        alle rader fikk class="utslag"."""
        monter(monkeypatch, snapshot({
            "EQNR": serie([100.0] * 60 + [104.0]),   # 2 av 3
            "DNB": serie([100.0] * 60 + [101.0]),    # 1 av 3
        }))
        html = klient.get("/").data.decode("utf-8")
        assert html.count('<tr class="utslag">') == 1
        dnb = html.split("DNB Bank")[0].rsplit("<tr", 1)[1]
        assert "utslag" not in dnb

    def test_bare_sjekkene_som_slo_ut_er_merket(self, klient, monkeypatch):
        """VG2: like mange rader med class="bidro" som sjekker som slo ut."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))  # 2 av 3
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert html.count('<section class="sjekkort bidro"') == 2
        assert html.count('<section class="sjekkort"') == 1
        # Gjennomgangen 15.10 (BH12, ECH7): det som skiller kortene for synet,
        # er pillen med farge etter fortegnet (utdraget §8). Kortet uten
        # utslag har den grå pillen.
        kortene = re.findall(r'<section class="sjekkort( bidro)?"(.*?)</section>', html, re.DOTALL)
        assert len(kortene) == 3
        for bidro, innhold in kortene:
            klasse = re.search(r'class="resultat fortegn ([a-z]+)"', innhold).group(1)
            assert (klasse in ("opp", "ned")) == bool(bidro), (bidro, klasse)

    def test_ringen_er_sterk_oransje_og_teksten_sier_det_samme(self, klient, monkeypatch):
        """Story 8.0d, PR 2, designregler §3 (14.10): testen fra 8.0c for 3:1
        mot hvitt er byttet ut. Ringen er tavlas #F2B53A, og teksten «3 av 3»
        sier det samme (FR-103). Ville feilet med ringen i en annen farge."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        stil = _stil(klient.get("/").data.decode("utf-8"))
        assert re.search(r"--oransje:\s*#F2B53A", stil)
        assert "var(--oransje)" in _regel(stil, ".pille.tre-av-tre")

    def test_forbeholdet_staar_ogsaa_uten_tabellen(self, klient, monkeypatch):
        """VG6: forbeholdet staar synlig ogsaa naar sjekkene ikke vises."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0, 101.0])}))  # for kort serie
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert "Signalet kunne ikke regnes" in html
        assert "Signalstyrken sier ikke om du bør kjøpe eller selge." in html

    # Svar 3 paa BH1/ECH2 (13.10 kl. 16:42).

    def test_noen_mangler_vurdering_gir_begge_setningene(self, klient, monkeypatch):
        """Ville feilet hvis «N av M aksjer ble vurdert.» manglet."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))   # 1 av 3
        monter(monkeypatch, snapshot({"DNB": serie([100.0] * 61)}), vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer." in html
        # Story 8.0d, PR 2b: M er alle de 15 aksjene i lista (14.10).
        assert "1 av 15 aksjer ble vurdert." in html
        assert html.index("Ingen aksjer skilte seg ut") < html.index("1 av 15 aksjer ble vurdert.")

    def test_alle_vurdert_gir_bare_setningen_fra_0510(self, klient, monkeypatch):
        # Story 8.0d, PR 3: alle aksjene i lista har kurser og vurdering.
        from kursdata import AKSJEUNIVERS

        monter(monkeypatch, snapshot({a.symbol: serie([100.0] * 61) for a in AKSJEUNIVERS}))
        html = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut" in html
        assert "ble vurdert." not in html

    def test_ingen_ny_setning_naar_en_skiller_seg_ut_og_en_mangler(self, klient, monkeypatch):
        """VG paa svar 3: «ble vurdert.» staar bare under setningen fra 05.10.
        Ville feilet hvis den nye setningen ble flyttet ut av den ytre if-en."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))   # 2 av 3
        monter(monkeypatch, snapshot({"DNB": serie([100.0] * 61)}), vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        assert "2 av 3" in html
        assert "Ingen aksjer skilte seg ut" not in html
        assert "ble vurdert." not in html

    def test_ingen_vurdert_gir_ingen_av_setningene(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}), vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut" not in html
        assert "ble vurdert." not in html

    def test_antall_vurdert_teller_radene_med_styrke(self):
        """Enhetstest: 0, 1 og alle."""
        from types import SimpleNamespace

        from markedsoversikt import antall_vurdert

        rad = lambda s: SimpleNamespace(styrke=s)  # noqa: E731
        assert antall_vurdert([]) == 0
        assert antall_vurdert([rad(None), rad(1)]) == 1
        assert antall_vurdert([rad(0), rad(3)]) == 2

    # PR 2: datoene (beslutning 12).

    def test_aaret_vises_naar_det_er_et_annet_enn_i_aar(self, klient, monkeypatch):
        """Ville feilet hvis dato() aldri viste aaret, eller viste det i samme aar."""
        import app as app_modul
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 61)}))
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2027, 1, 4, 12, 0, tzinfo=timezone.utc))
        html = klient.get("/").data.decode("utf-8")
        assert re.search(r"Oslo Børs · \d\d\.\d\d\.2026 ·", html)
        assert re.search(r"Oppdatert [a-zø]+ \d\d\.\d\d\.2026 kl\. \d\d\.\d\d", html)
        # VG4: aksjesiden ogsaa, med datoen i meta-linja og grafens fra-til.
        detalj = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert re.search(r"Oslo Børs · \d\d\.\d\d\.2026", detalj)
        assert re.search(r"\d\d\.\d\d\.2026 til \d\d\.\d\d\.2026\.", detalj)

    def test_ingen_synlig_iso_dato_paa_sidene(self, klient, monkeypatch):
        """Beslutning 12: ingen synlig tekst har en dato som 2026-10-13.
        Ville feilet hvis en dato gikk utenom dato() eller norsk_tid."""
        from test_hjelpetekster import synlig_tekst
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0]),
                                      "DNB": serie([100.0, 101.0])}))
        # VG3: ulike tider, saa tidsstempelet under navnet ogsaa vises.
        monter_lager(monkeypatch, {"KOG": datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc),
                                   "TEL": datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)})
        assert 'class="hentet">hentet ' in klient.get("/").data.decode("utf-8")
        for sti in ("/", "/aksje/EQNR", "/aksje/DNB"):
            tekst = synlig_tekst(klient.get(sti).data.decode("utf-8"))
            assert not re.search(r"\b\d{4}-\d{2}-\d{2}\b", tekst), (sti, re.findall(r"\b\d{4}-\d{2}-\d{2}\b", tekst))

    def test_maanedsmerkene_staar_i_grafen(self, klient, monkeypatch):
        """Beslutning 13: et merke med fullt norsk maanedsnavn ved foerste
        boersdag i maaneden, i SVG-en."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        navn = re.findall(r'<text class="maanedstekst"[^>]*>([a-zæøå]+)</text>', html)
        assert navn and all(n in ("september", "oktober", "november") for n in navn), navn
        # BH9: en strek per navn, og streken under kurslinja (ECH7).
        assert html.count('<line class="maanedsstrek"') == len(navn)
        assert html.index('class="maanedsstrek"') < html.index('class="kurslinje" points')
        assert "01.09 til" in html


def _lagret(symbol: str, endring: float, trend: int, bevegelse: int, interesse: int,
            vurdert: bool = True, standardavvik: float = 0.01) -> None:
    """En flat serie der siste dag endrer seg med endring prosent, og en
    lagret vurdering med de tre fortegnene. Kursene ville gitt noe annet,
    saa siden viser bare det vurderingen sier. vurdert=False gir ingen rad i
    vurdering."""
    rader = serie([100.0] * 60 + [100.0 * (1 + endring / 100)])
    skriv_serie(symbol, rader, datetime.fromisoformat(HENTET), vurdert=False)
    if not vurdert:
        return
    utslag = [v for v in (trend, bevegelse, interesse) if v]
    retning = ("Ingen" if not utslag else "Positiv" if all(v > 0 for v in utslag)
               else "Negativ" if all(v < 0 for v in utslag) else "Blandet")
    skriv_vurdering(symbol, rader[-1].dato, Vurdering(
        styrke=len(utslag), retning=retning, trend=trend, bevegelse=bevegelse,
        interesse=interesse, slutt=rader[-1].slutt, justert_slutt=rader[-1].justert_slutt,
        trend_avvik=0.0, dagens_endring=endring / 100, standardavvik=standardavvik, volumforhold=1.0,
    ))


def _deler(html: str) -> dict[str, list[str]]:
    """Selskapene under hver del, i rekkefoelgen de staar."""
    tabell = _tabell(html)
    deler: dict[str, list[str]] = {}
    for rad, del_ in zip(tabell.rader, tabell.del_av):
        deler.setdefault(del_, []).append(rad[0].split(" hentet ")[0])
    return deler


class TestStory80e:
    """Story 8.0e, PR 1: tabellen i oversikten."""

    def test_t_b_og_i_staar_under_n_av_3_fra_vurderingen(self, klient):
        """Den flate serien ville gitt T 0, B 0 og I 0. Ville feilet hvis T, B
        og I ble regnet av kursene, eller stod over «N av 3»."""
        _lagret("EQNR", 0.0, 1, -1, 0)
        html = klient.get("/").data.decode("utf-8")
        rad = _rader_per_selskap(html)["Equinor"]
        assert rad[3] == "2 av 3 T +1 B -1 I 0 skiller seg ut"
        # VG1 i gjennomgangen: navnet staar ved bokstaven.
        for bokstav, navn in (("T", "trend"), ("B", "bevegelse"), ("I", "interesse")):
            assert f'<abbr title="{navn}">{bokstav}</abbr>' in html

    def test_rad_uten_vurdering_har_ikke_t_b_og_i(self, klient):
        """Ville feilet hvis en rad med en grunn eller uten vurdering viste T,
        B og I."""
        _lagret("EQNR", 0.0, 1, 0, 0)
        _lagret("DNB", 0.0, 0, 0, 0, vurdert=False)
        rader = serie([100.0] * 61)
        skriv_serie("KOG", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("KOG", rader[-1].dato, Grunn.SIGNAL_IKKE_REGNET)
        html = klient.get("/").data.decode("utf-8")
        celler = {rad[0]: rad[3] for rad in _tabell(html).rader}
        for navn in ("DNB Bank", "Kongsberg Gruppen"):
            assert celler[navn].startswith("–"), celler[navn]
            assert not re.search(r"\b[TBI] [+-]?\d", celler[navn]), celler[navn]
        assert "signalet kunne ikke regnes" in celler["Kongsberg Gruppen"]
        assert html.count('<span class="sjekker">') == 1

    def test_to_deler_hver_sortert_etter_fr_102(self, klient):
        """Styrke 2 er paa terskelen og staar under «Skilte seg ut». Ville
        feilet med > i stedet for >=, en rad med 1 av 3 under «Skilte seg
        ut», eller sorteringen snudd i én del."""
        _lagret("KOG", 0.5, 1, 1, 1)       # 3 av 3
        _lagret("EQNR", -5.0, 1, 1, 0)     # 2, stor endring
        _lagret("DNB", 1.0, -1, -1, 0)     # 2, liten endring
        _lagret("AKRBP", 0.2, 1, 0, 0)     # 1, liten endring
        _lagret("NHY", -3.0, 0, 1, 0)      # 1, stor endring
        _lagret("FRO", 10.0, 0, 0, 0)      # 0
        _lagret("VAR", 20.0, 0, 0, 0, vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        assert _tabell(html).deler == ["Skilte seg ut", "Øvrige aksjer"]
        assert _deler(html) == {
            "Skilte seg ut": ["Kongsberg Gruppen", "Equinor", "DNB Bank"],
            "Øvrige aksjer": ["Norsk Hydro", "Aker BP", "Frontline", "Vår Energi"],
        }

    def test_fortsatt_fem_kolonner_med_to_deler(self, klient):
        """FR-101. Overskriftene for delene gaar over alle fem kolonnene.
        Ville feilet med en sjette kolonne."""
        _lagret("EQNR", 1.0, 1, 1, 0)
        _lagret("DNB", 1.0, 0, 0, 0)
        html = klient.get("/").data.decode("utf-8")
        tabell = _tabell(html)
        assert len(tabell.hode) == 5 and len(tabell.rader) == 2
        assert all(len(rad) == 5 for rad in tabell.rader)
        assert html.count('<th colspan="5" scope="rowgroup">') == 2
        assert html.count('<td colspan="5">') == 0

    def test_delingen_bruker_terskelen_fra_parametre(self, klient, monkeypatch):
        """FR-705. Ville feilet hvis terskelen 2 sto fast i delingen."""
        import dataclasses

        monkeypatch.setattr(app_modul, "STANDARD", dataclasses.replace(app_modul.STANDARD, terskel=3))
        _lagret("KOG", 0.0, 1, 1, 1)
        _lagret("EQNR", 0.0, 1, 1, 0)
        html = klient.get("/").data.decode("utf-8")
        assert _deler(html) == {
            "Skilte seg ut": ["Kongsberg Gruppen"], "Øvrige aksjer": ["Equinor"],
        }
        # Story 8.0d, PR 2 (BH10): grensene i båndene følger terskelen.
        assert _tabell(html).ekstra["bak"] == ["signalstyrke 3 eller mer", "signalstyrke 0 til 2"]

    def test_setningene_fra_8_0c_der_skilte_seg_ut_ellers_staar(self, klient):
        """Svar 3. Ville feilet hvis «Skilte seg ut» stod sammen med
        setningen, eller setningen stod over tabellen."""
        _lagret("EQNR", 1.0, 1, 0, 0)
        _lagret("DNB", 1.0, 0, 0, 0, vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        tabell = _tabell(html)
        assert tabell.deler == [
            "Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer. 1 av 15 aksjer ble vurdert.",
            "Øvrige aksjer",
        ]
        assert set(tabell.del_av) == {"Øvrige aksjer"}
        assert "Skilte seg ut</th>" not in html
        assert html.index("Ingen aksjer skilte seg ut") > html.index("</thead>")

    def test_bare_setningen_fra_0510_naar_alle_er_vurdert(self, klient):
        """BH11: med alle vurdert staar bare den foerste setningen, og den
        staar i tabellen."""
        # Story 8.0d, PR 3: alle de 15 aksjene i lista er vurdert.
        from kursdata import AKSJEUNIVERS

        _lagret("EQNR", 1.0, 1, 0, 0)
        for aksje in AKSJEUNIVERS:
            if aksje.symbol != "EQNR":
                _lagret(aksje.symbol, 1.0, 0, 0, 0)
        assert _tabell(klient.get("/").data.decode("utf-8")).deler == [
            "Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer.", "Øvrige aksjer",
        ]

    def test_ble_vurdert_ogsaa_naar_en_aksje_mangler_kurser(self, klient):
        """Story 8.0d, PR 3 (BH1 i PR 2b, svar 8): alle radene er vurdert,
        men én aksje i lista har ingen kurser. Ville feilet hvis setningen
        ble regnet fra radene igjen."""
        from kursdata import AKSJEUNIVERS

        mangler, *med_kurser = AKSJEUNIVERS
        for aksje in med_kurser:
            _lagret(aksje.symbol, 1.0, 0, 0, 0)
        html = klient.get("/").data.decode("utf-8")
        m = len(AKSJEUNIVERS)
        assert _tabell(html).deler[0] == (
            f"Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer. {m - 1} av {m} aksjer ble vurdert.")
        assert f"Uten data i denne kilden: {mangler.navn}." in _synlig(html)

    def test_oevrige_sier_hvor_mange_som_er_uten_signal(self, klient):
        """Story 8.0d, PR 3 (BH2 i PR 2, svar 7): «og 1 uten signal» også når
        det er én, og pillen teller alle radene i båndet."""
        _lagret("KOG", 0.0, 1, 1, 0)
        _lagret("EQNR", 0.0, 1, 0, 0)
        _lagret("DNB", 0.0, 0, 0, 0, vurdert=False)
        tabell = _tabell(klient.get("/").data.decode("utf-8"))
        assert tabell.ekstra["bak"] == ["signalstyrke 2 eller mer", "signalstyrke 0 eller 1 og 1 uten signal"]
        assert tabell.ekstra["antall"] == ["1", "2"]
        _lagret("MOWI", 0.0, 0, 0, 0, vurdert=False)
        tabell = _tabell(klient.get("/").data.decode("utf-8"))
        assert tabell.ekstra["bak"][1] == "signalstyrke 0 eller 1 og 2 uten signal"
        assert tabell.ekstra["antall"] == ["1", "3"]

    def test_alle_over_terskelen_gir_bare_skilte_seg_ut(self, klient):
        _lagret("EQNR", 1.0, 1, 1, 0)
        _lagret("KOG", 1.0, 1, 1, 1)
        html = klient.get("/").data.decode("utf-8")
        assert _tabell(html).deler == ["Skilte seg ut"]
        assert "Øvrige aksjer" not in html

    def test_uten_en_eneste_vurdering_er_det_én_del_uten_overskrift(self, klient):
        _lagret("EQNR", 1.0, 0, 0, 0, vurdert=False)
        _lagret("DNB", 1.0, 0, 0, 0, vurdert=False)
        tabell = _tabell(klient.get("/").data.decode("utf-8"))
        assert tabell.deler == [] and len(tabell.rader) == 2

    def test_tre_av_tre_har_svart_fyll_og_hvit_tekst(self, klient):
        """Svar 8. Ville feilet uten fyllet, eller med fyll ogsaa paa 2 av 3."""
        _lagret("KOG", 0.0, 1, 1, 1)
        _lagret("EQNR", 0.0, 1, 1, 0)
        html = klient.get("/").data.decode("utf-8")
        stil = _stil(html)
        fyll = _regel(stil, ".pille.tre-av-tre")
        assert "var(--oransje)" in fyll and "background: var(--fyll)" in fyll
        # Story 8.0d: hvitt står som navn i rammen (designregler §5).
        assert "color: var(--hvit)" in fyll
        # Story 8.0d: fyllet er blekk (designregler §5), ikke rent svart.
        assert re.search(r"--fyll:\s*#16181D", stil)
        assert "background" not in _regel(stil, ".pille")
        assert '<span class="pille tre-av-tre">3 av 3</span>' in html
        # Story 8.0d, PR 3: hvit pille med tekst og kant i blekk ved 2 av 3.
        to = _regel(stil, ".pille.to-av-tre")
        assert "background: var(--hvit)" in to and "solid var(--blekk)" in to and "color: var(--blekk)" in to
        assert '<span class="pille to-av-tre">2 av 3</span>' in html

    def test_kontrasten_paa_pillen_med_fyll(self, klient):
        """WCAG 1.4.3: teksten mot fyllet minst 4,5:1. WCAG 1.4.11: den gule
        ringen mot fyllet minst 3:1, som mot hvitt i 8.0c. Begge fargene i
        teksten leses fra stilen (BH1 og BH2 i gjennomgangen)."""
        _lagret("KOG", 0.0, 1, 1, 1)
        stil = _stil(klient.get("/").data.decode("utf-8"))
        fyll = re.search(r"--fyll:\s*#([0-9a-fA-F]{6})", stil).group(1)
        gul = re.search(r"--oransje:\s*#([0-9a-fA-F]{6})", stil).group(1)
        navn = re.search(r"(?<!-)color:\s*var\(--([a-z-]+)\)", _regel(stil, ".pille.tre-av-tre")).group(1)
        tekst = re.search(rf"--{navn}:\s*#([0-9a-fA-F]{{6}})", stil).group(1)

        def lys(farge):
            def lin(c):
                c = c / 255
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            r, g, b = (int(farge[i:i + 2], 16) for i in (0, 2, 4))
            return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

        def kontrast(a, b):
            hoey, lav = sorted((lys(a), lys(b)), reverse=True)
            return (hoey + 0.05) / (lav + 0.05)

        assert kontrast(tekst, fyll) >= 4.5, (tekst, fyll)
        assert kontrast(gul, fyll) >= 3.0, (gul, fyll)


def _synlig(html: str) -> str:
    """Teksten paa siden uten stil, merker og ekstra blanktegn."""
    html = re.sub(r"<style>.*?</style>", "", html, flags=re.DOTALL)
    return re.sub(r"[ \t\r\n]+", " ", re.sub(r"<[^>]+>", "", html))


class TestStory80eTekst:
    """Story 8.0e, PR 2: teksten over tabellen."""

    def test_overskriften_teller_n_fra_radene_og_m_fra_lista(self, klient):
        """Svar 3: N telles fra radene. Story 8.0d, PR 2b: M er alle aksjene
        i lista, også de uten kurser (14.10). Testbasen har 15 aksjer, og 2
        har kurser."""
        _lagret("KOG", 0.0, 1, 1, 0)
        _lagret("EQNR", 0.0, 1, 0, 0)
        html = klient.get("/").data.decode("utf-8")
        # Story 8.0d, PR 2: h1, med markering og uten fet skrift (§4, 14.10).
        assert '<h1 class="overskrift"><mark>1 av 15 aksjer</mark> skilte seg ut lørdag</h1>' in html

    def test_aksjen_uten_kurser_telles_med(self, klient):
        """Story 8.0d, PR 2b (14.10). Ville feilet hvis M ble telt fra radene
        igjen: alle aksjene i lista utenom én har kurser, og den ene står
        under tabellen, ikke som rad, men telles i overskriften og linja."""
        from kursdata import AKSJEUNIVERS

        mangler, rolig, *med_kurser = AKSJEUNIVERS
        _lagret(rolig.symbol, 0.0, 0, 0, 0)
        for aksje in med_kurser:
            _lagret(aksje.symbol, 0.0, 1, 1, 0)
        html = klient.get("/").data.decode("utf-8")
        tekst = _synlig(html)
        m = len(AKSJEUNIVERS)
        assert len(_tabell(html).rader) == m - 1
        assert f"<mark>{m - 2} av {m} aksjer</mark>" in html
        # VG2: båndene teller radene sine som før.
        assert _tabell(html).ekstra["antall"] == [str(m - 2), "1"]
        assert f"Oslo Børs · 31.10 · {m} aksjer" in tekst
        assert f"Uten data i denne kilden: {mangler.navn}." in tekst

    def test_ukedagen_er_datoen_i_linja_over_tabellen(self, klient):
        """Svar 5: den eldste datoen, som linja over tabellen (story 8.0), og
        ikke dagen siden aapnes (klokka staar paa torsdag 31.12)."""
        _lagret("KOG", 0.0, 1, 1, 0)  # siste dag 31.10, lørdag
        rader = serie([100.0] * 60)    # siste dag 30.10, fredag
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        assert "Oslo Børs · 30.10 · 15 aksjer" in _synlig(html)
        assert "skilte seg ut fredag</h1>" in html

    def test_ingen_over_terskelen_gir_0_og_ingen_setning_hos(self, klient):
        _lagret("KOG", 0.0, 1, 0, 0)
        _lagret("EQNR", 0.0, 0, 0, 0)
        tekst = _synlig(klient.get("/").data.decode("utf-8"))
        assert "0 av 15 aksjer skilte seg ut lørdag" in tekst
        assert "Hos " not in tekst
        # Svar 3: setningen fra 8.0c staar fortsatt i tabellen (BH4).
        assert "Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer." in tekst
        assert "fikk utslag på alle" not in tekst

    def test_uten_en_eneste_vurdering_staar_ingen_overskrift(self, klient):
        _lagret("KOG", 0.0, 0, 0, 0, vurdert=False)
        html = klient.get("/").data.decode("utf-8")
        # Story 8.0d, PR 2, svar 3: «Markedsoversikt» uten tall.
        assert '<h1 class="overskrift">Markedsoversikt</h1>' in html
        assert "<mark>" not in html and "Hos " not in _synlig(html)

    def test_innledningen_med_én_aksje(self, klient):
        """Svar 4. Ville feilet med «Hos 1 aksjer»."""
        _lagret("KOG", 0.0, 1, 1, 0)
        _lagret("EQNR", 0.0, 0, 0, 0)
        assert ("OSE Signal er et regelbasert signal for aksjer på Oslo Børs: 3 faste sjekker "
                "måler kurs og volum mot aksjens egen historikk. Hos 1 aksje slo minst 2 av 3 ut. "
                "Det viser hvor du kan se nærmere, ikke hva du bør kjøpe eller selge."
                ) in _synlig(klient.get("/").data.decode("utf-8"))

    def test_innledningen_med_flere_og_terskelen_fra_parametre(self, klient, monkeypatch):
        import dataclasses

        _lagret("KOG", 0.0, 1, 1, 1)
        _lagret("EQNR", 0.0, -1, -1, -1)
        assert "Hos disse 2 slo minst 2 av 3 ut." in _synlig(klient.get("/").data.decode("utf-8"))
        monkeypatch.setattr(app_modul, "STANDARD", dataclasses.replace(app_modul.STANDARD, terskel=3))
        assert "Hos disse 2 slo minst 3 av 3 ut." in _synlig(klient.get("/").data.decode("utf-8"))

    def test_linja_om_3_av_3_med_navnene_fra_radene(self, klient):
        """Ville feilet hvis linja sto uten en aksje paa 3 av 3."""
        _lagret("KOG", 0.0, 1, 1, 1)
        _lagret("EQNR", 0.0, 1, 1, 0)
        tekst = _synlig(klient.get("/").data.decode("utf-8"))
        assert "3 av 3 Bare Kongsberg Gruppen fikk utslag på alle 3 sjekkene." in tekst
        _lagret("DNB", 5.0, -1, -1, -1)
        tekst = _synlig(klient.get("/").data.decode("utf-8"))
        assert "Bare DNB Bank og Kongsberg Gruppen fikk utslag på alle 3 sjekkene." in tekst

    def test_linja_om_3_av_3_ogsaa_naar_terskelen_er_over_3(self, klient, monkeypatch):
        """ECH3 i gjennomgangen: navnene tas fra alle radene, ikke bare fra
        «Skilte seg ut»."""
        import dataclasses

        monkeypatch.setattr(app_modul, "STANDARD", dataclasses.replace(app_modul.STANDARD, terskel=4))
        _lagret("KOG", 0.0, 1, 1, 1)
        assert "Bare Kongsberg Gruppen fikk utslag på alle 3 sjekkene." in _synlig(klient.get("/").data.decode("utf-8"))

    def test_ingen_linje_uten_3_av_3(self, klient):
        _lagret("KOG", 0.0, 1, 1, 0)
        html = klient.get("/").data.decode("utf-8")
        assert "fikk utslag på alle" not in html and 'class="alle-sjekkene"' not in html

    def test_slik_leser_du_tabellen_har_3_punkter(self, klient):
        """Svar 2 og tavlas tekster (endringsforslaget 13.10, punkt 4.2).
        Ville feilet med setningen om klikk paa T, B eller I. Svaret kl. 12:15
        (15.10, BH20): de to setningene om +1 og -1."""
        _lagret("KOG", 0.0, 1, 1, 0)
        html = klient.get("/").data.decode("utf-8")
        del_ = html.split('<section class="slik-leser"', 1)[1].split("</section>", 1)[0]
        # Story 8.0d, PR 2: symbolene er aria-hidden og ikke en del av teksten.
        del_ = re.sub(r'<span class="symbolfelt" aria-hidden="true">.*?</span></span>|'
                      r'<span class="symbolfelt" aria-hidden="true">.*?</svg></span>', "", del_, flags=re.DOTALL)
        punkter = [_synlig(p).strip() for p in re.findall(r"<li>(.*?)</li>", del_, re.DOTALL)]
        assert punkter == [
            "Signalstyrke 0–3 T, B og I er trend, bevegelse og interesse, og hver gir +1, 0 eller -1. "
            "Både +1 og -1 teller som utslag. "
            "Øverst i cellen står hvor mange som slo ut, fra 0 av 3 til 3 av 3.",
            "Retning Om sjekkene som slo ut, ga +1 eller -1. Ga noen +1 og noen -1, står det Blandet. "
            "Ikke et råd om å kjøpe eller selge.",
            "Selskapsnavnet Klikk for å se sjekkene, tallene bak og kursgrafen.",
        ]
        assert "Klikk på T" not in html
        assert html.index("Slik leser du tabellen") < html.index("<table")


def _med_siste(foer: date, siste: date) -> list[Kursrad]:
    """60 kursrader som ender på foer, og så én rad på siste (svar 29)."""
    rader = [Kursrad(dato=foer - timedelta(days=59 - i), slutt=100.0, justert_slutt=100.0, volum=1000)
             for i in range(60)]
    return rader + [Kursrad(dato=siste, slutt=101.0, justert_slutt=101.0, volum=1000)]


def _endringsforklaring(klient, symbol: str) -> str:
    svar = klient.get(f"/aksje/{symbol}")
    assert svar.status_code == 200
    endring = svar.data.decode("utf-8").split('<div class="noekkeltall endring">', 1)[1].split("</div>", 1)[0]
    return re.search(r'<span class="forklaring">(.*?)</span>', endring).group(1)


def _deler_i_rekkefoelge(html: str) -> tuple[list[str], list[str]]:
    """Symbolene i «Skilte seg ut» og i «Øvrige aksjer», i rekkefølgen de
    står - story 8.15."""
    tbody = html.split("</thead>", 1)[1].split("</table>", 1)[0]
    ut, oevrige = tbody.split("Øvrige aksjer", 1) if "Øvrige aksjer" in tbody else (tbody, "")
    finn = lambda del_: re.findall(r'<span class="linje">([A-Z0-9]+)', del_)
    return finn(ut), finn(oevrige)


class TestStory815Sortering:
    """Story 8.15: sortering ved klikk i kolonneraden, svarene på planen kl.
    13:44 (instruksjonen kl. 14:01)."""

    @pytest.fixture
    def tabell(self, klient):
        """Fem aksjer: tre som skilte seg ut og to øvrige, den ene uten
        vurdering."""
        _lagret("KOG", 1.0, 1, 1, 1)      # 3 Positiv
        _lagret("DNB", -4.0, -1, -1, 0)   # 2 Negativ
        _lagret("EQNR", 2.0, 1, -1, 0)    # 2 Blandet
        _lagret("MOWI", 3.0, 1, 0, 0)     # 1 Positiv
        _lagret("NHY", -1.0, 0, 0, 0, vurdert=False)
        return klient

    def _side(self, klient, adresse):
        svar = klient.get(adresse)
        assert svar.status_code == 200, adresse
        return svar.data.decode("utf-8")

    def test_uten_klikk_er_rekkefoelgen_fr_102(self, tabell):
        """Ville feilet hvis ukjent eller manglende parameter ga en annen
        rekkefølge eller en feil (S7)."""
        standard = _deler_i_rekkefoelge(self._side(tabell, "/"))
        assert standard == (["KOG", "DNB", "EQNR"], ["MOWI", "NHY"])
        for adresse in ("/?sorter=endring", "/?orden=stigende", "/?sorter=navn&orden=synkende",
                        "/?sorter=endring&orden=opp", "/?sorter=&orden="):
            assert _deler_i_rekkefoelge(self._side(tabell, adresse)) == standard, adresse

    @pytest.mark.parametrize("adresse, ut, oevrige", [
        ("/?sorter=endring&orden=synkende", ["EQNR", "KOG", "DNB"], ["MOWI", "NHY"]),
        ("/?sorter=endring&orden=stigende", ["DNB", "KOG", "EQNR"], ["NHY", "MOWI"]),
        ("/?sorter=signal&orden=stigende", ["DNB", "EQNR", "KOG"], ["MOWI", "NHY"]),
        ("/?sorter=retning&orden=stigende", ["EQNR", "DNB", "KOG"], ["MOWI", "NHY"]),
        ("/?sorter=retning&orden=synkende", ["KOG", "DNB", "EQNR"], ["MOWI", "NHY"]),
    ])
    def test_hver_del_sorteres_for_seg(self, tabell, adresse, ut, oevrige):
        """Tillegget 13.10: ingen rad flytter seg mellom delene (S1). Rader
        uten verdi står sist i begge retninger (S2), og endringen har
        fortegn (S4)."""
        assert _deler_i_rekkefoelge(self._side(tabell, adresse)) == (ut, oevrige)

    def test_lenken_snur_og_aria_sort_staar_paa_kolonnen(self, tabell):
        """Første klikk synkende, A til Å for Retning, og et nytt klikk
        snur (S5). aria-sort står bare på kolonnen som er valgt (S6)."""
        html = self._side(tabell, "/")
        thead = html.split("<thead>", 1)[1].split("</thead>", 1)[0]
        assert "aria-sort" not in thead
        lenker = dict(re.findall(r'href="/\?sorter=(\w+)&amp;orden=(\w+)"', thead))
        assert lenker == {"kurs": "synkende", "endring": "synkende", "signal": "synkende", "retning": "stigende"}
        valgt = self._side(tabell, "/?sorter=endring&orden=synkende")
        thead = valgt.split("<thead>", 1)[1].split("</thead>", 1)[0]
        assert re.findall(r'<th[^>]*aria-sort="(\w+)"[^>]*><a class="sorter valgt" href="/\?sorter=(\w+)&amp;orden=(\w+)"', thead) == [
            ("descending", "endring", "stigende")]
        stigende = self._side(tabell, "/?sorter=retning&orden=stigende")
        assert re.search(r'<th aria-sort="ascending"><a class="sorter valgt" href="/\?sorter=retning&amp;orden=synkende">', stigende)

    def test_skjermleseren_hoerer_kolonnen_og_retningen(self, tabell):
        """Kontrollpunktet og svar 2: «alfabetisk» for Retning."""
        valgt = self._side(tabell, "/?sorter=retning&orden=stigende")
        assert ('Retning<span class="skjult">, sortert alfabetisk, A til Å. Velg for alfabetisk, Å til A.</span>'
                in valgt)
        assert 'Endring<span class="skjult">, sorter synkende</span>' in valgt
        endring = self._side(tabell, "/?sorter=endring&orden=stigende")
        assert 'Endring<span class="skjult">, sortert stigende. Velg for synkende.</span>' in endring

    def test_linja_over_tabellen_bare_med_valg(self, tabell):
        """Svar 5. Ville feilet hvis linja sto også uten valg (S12)."""
        assert 'class="sortert"' not in self._side(tabell, "/")
        html = self._side(tabell, "/?sorter=signal&orden=stigende")
        assert '<p class="sortert">Sortert på signalstyrke, stigende. <a href="/">Standard rekkefølge</a></p>' in html
        assert html.index('<p class="sortert">') < html.index('<div class="tabellboks"')
        # Gjennomgangen (VG2): navnet for hver kolonne.
        for kolonne, navn in (("kurs", "sluttkurs"), ("endring", "endring"), ("retning", "retning")):
            html = self._side(tabell, f"/?sorter={kolonne}&orden=synkende")
            assert f'<p class="sortert">Sortert på {navn}, synkende.' in html, kolonne

    def test_vinkelen_peker_etter_retningen(self, tabell):
        """Gjennomgangen (VG1): den valgte kolonnen viser retningen som
        gjelder, og de andre retningen et klikk gir."""
        ned, opp = "M2.5 4.5 6 8l3.5-3.5", "M2.5 7.5 6 4l3.5 3.5"

        def vinkler(adresse):
            thead = self._side(tabell, adresse).split("<thead>", 1)[1].split("</thead>", 1)[0]
            return dict(re.findall(r'href="/\?sorter=(\w+)&amp;[^"]*">.*?<path d="([^"]+)"', thead))

        assert vinkler("/") == {"kurs": ned, "endring": ned, "signal": ned, "retning": opp}
        assert vinkler("/?sorter=endring&orden=synkende")["endring"] == ned
        assert vinkler("/?sorter=endring&orden=stigende")["endring"] == opp
        assert vinkler("/?sorter=retning&orden=synkende")["retning"] == ned

    def test_rad_uten_endring_sist_i_skilte_seg_ut(self, tabell, monkeypatch):
        """Gjennomgangen (BH14): en rad med vurdering, men bare én kursdag,
        står sist i «Skilte seg ut» i begge retninger."""
        rader = serie([100.0])
        skriv_serie("ORK", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("ORK", rader[-1].dato, Vurdering(
            styrke=2, retning="Positiv", trend=1, bevegelse=1, interesse=0, slutt=100.0,
            justert_slutt=100.0, trend_avvik=0.0, dagens_endring=0.0, standardavvik=0.01,
            volumforhold=1.0))
        for orden in ("synkende", "stigende"):
            ut, _ = _deler_i_rekkefoelge(self._side(tabell, f"/?sorter=endring&orden={orden}"))
            assert ut[-1] == "ORK" and len(ut) == 4, (orden, ut)

    def test_tre_av_tre_og_antallet_foelger_fr_102(self, tabell):
        """Svar 7: linja om 3 av 3 og «N av M aksjer» endres ikke av et klikk."""
        def topp(html):
            return html.split('<div class="tabellboks"', 1)[0].split("<main>", 1)[1]
        standard = topp(self._side(tabell, "/"))
        valgt = topp(self._side(tabell, "/?sorter=signal&orden=stigende"))
        assert valgt.split('<p class="sortert">', 1)[0].rstrip() == standard.rstrip()

    def test_tilbakelenken_paa_aksjesiden_gaar_til_standarden(self, tabell):
        """Svar 3."""
        html = self._side(tabell, "/aksje/KOG")
        assert '<a class="tilbake" href="/">Markedsoversikt</a>' in html


class TestStory80dAksjesiden:
    """Story 8.0d, PR 3: aksjesiden etter del C og svarene 14.10 kl. 22:50."""

    def test_overskriften_med_markering_naar_aksjen_skilte_seg_ut(self, klient):
        """Beslutning 7 og designregler §3 (14.10). Ville feilet uten
        markeringen, eller med «skilte seg ut» under terskelen."""
        _lagret("KOG", 0.0, 1, 1, 0)
        _lagret("EQNR", 0.0, 1, 0, 0)
        kog = klient.get("/aksje/KOG").data.decode("utf-8")
        assert '<h1 class="overskrift">Kongsberg Gruppen <mark>skilte seg ut lørdag</mark></h1>' in kog
        eqnr = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert '<h1 class="overskrift">Equinor</h1>' in eqnr
        assert "skilte seg ut" not in _synlig(eqnr)
        assert "linear-gradient(transparent 60%, var(--lys-oransje) 60%)" in _regel(_stil(kog), "h1.overskrift mark")
        # Gjennomgangen (VG3): 3 av 3 er også over terskelen.
        _lagret("DNB", 0.0, 1, 1, 1)
        assert "<mark>skilte seg ut lørdag</mark>" in klient.get("/aksje/DNB").data.decode("utf-8")

    def test_merkene_over_h1_og_linja_under(self, klient):
        """Svar 18: ticker og bransje i merkene over h1, og «Oslo Børs ·
        dato» under."""
        _lagret("EQNR", 0.0, 1, 0, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        merkene = html.index('<div class="merkene">')
        assert merkene < html.index("<h1") < html.index('<p class="meta">')
        assert re.search(r'<span class="merke">EQNR</span>\s*<span class="merke"><svg class="bransjesymbol"[^>]*aria-hidden="true"', html)
        assert '<p class="meta">Oslo Børs · 31.10</p>' in html
        assert "data hentet" not in html

    def test_demo_boers_paa_aksjesiden_i_demoen(self, klient, monkeypatch):
        """Svar 18 og FR-411 (gjennomgangen, VG1)."""
        from demo import lag_demobase
        from lagring_sqlite import demo_sti

        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        lag_demobase(sti, skriv=lambda *a: None)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/aksje/BRFE").data.decode("utf-8")
        assert re.search(r'<p class="meta">Demo Børs · \d\d\.\d\d</p>', html)
        assert "Oslo Børs ·" not in html

    def test_endringen_er_det_fjerde_kortet_med_ukedagene(self, klient):
        """Plan 8 og svar 21. Ville feilet uten endringskortet."""
        _lagret("EQNR", 2.0, 1, 0, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        kort = re.findall(r'<div class="noekkeltall[^"]*">\s*<span class="etikett">([A-Za-zæøå]+)', html)
        assert kort == ["Sluttkurs", "Endring", "Signalstyrke", "Retning"]
        endring = html.split('<div class="noekkeltall endring">', 1)[1].split("</div>", 1)[0]
        assert f'<span class="verdi opp">+2,00{NB}%</span>' in endring
        # Gjennomgangen (VG6): serien ender lørdag 31.10, og dagen før er
        # fredag. En nedgang er rød.
        assert "fra fredag til lørdag" in endring
        _lagret("DNB", -2.0, 1, 0, 0)
        ned = klient.get("/aksje/DNB").data.decode("utf-8")
        assert f'<span class="verdi ned">-2,00{NB}%</span>' in ned

    def test_endringen_med_datoene_naar_en_boersdag_ligger_mellom(self, klient, monkeypatch):
        """Svar 29 (15.10, BH6 og ECH2): datoene ved ukedagene når det ligger
        en børsdag mellom de to kursradene. Fredag til mandag og en uke med
        bare stengte dager har ingen. Ville feilet med alltid ukedager,
        alltid datoer, eller kalenderdager i stedet for børsdager."""
        monter(monkeypatch, snapshot({
            "EQNR": _med_siste(date(2026, 10, 2), date(2026, 10, 9)),
            "DNB": _med_siste(date(2026, 10, 2), date(2026, 10, 5)),
            "KOG": _med_siste(date(2026, 4, 1), date(2026, 4, 7)),
        }))
        assert _endringsforklaring(klient, "EQNR") == "fra fredag 02.10 til fredag 09.10"
        assert _endringsforklaring(klient, "DNB") == "fra fredag til mandag"
        assert _endringsforklaring(klient, "KOG") == "fra onsdag til tirsdag"

    def test_endringen_med_datoene_naar_kalenderen_ikke_dekker_dagene(self, klient, monkeypatch):
        """Svar 29: kan boersdag.py ikke avgjøre det (UtenforKalenderen),
        står datoene, og siden feiler ikke. 01.01.2027 er ikke i kalenderen."""
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2027, 1, 5, 12, 0, tzinfo=timezone.utc))
        monter(monkeypatch, snapshot({"EQNR": _med_siste(date(2026, 12, 30), date(2027, 1, 4))}))
        assert _endringsforklaring(klient, "EQNR") == "fra onsdag 30.12.2026 til mandag 04.01"

    def test_grensene_for_bevegelse_er_tallet_i_teksten(self, klient):
        """Svar 30 (15.10, ECH3): et standardavvik på 0,03 % står som 0,03
        både over skalaen og i teksten i kortet, ikke som 0,0."""
        _lagret("EQNR", 1.0, 0, 1, 0, standardavvik=0.0003)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        kort = html.split('aria-label="Sjekk 2: Bevegelse">', 1)[1].split("</section>", 1)[0]
        assert re.findall(r'<span class="grense"[^>]*>([^<]*)</span>', kort) == [f"-0,03{NB}%", f"+0,03{NB}%"]
        assert f"mot 0,03{NB}% standardavvik" in kort
        assert "0,0" + NB not in kort
        # Gjennomgangen av svarene 15.10 (VG1): gjennom ruten med en måling
        # som må skilles fra grensen med tre desimaler.
        _lagret("DNB", 1.23, 0, 1, 0, standardavvik=0.01234)
        html = klient.get("/aksje/DNB").data.decode("utf-8")
        kort = html.split('aria-label="Sjekk 2: Bevegelse">', 1)[1].split("</section>", 1)[0]
        assert re.findall(r'<span class="grense"[^>]*>([^<]*)</span>', kort) == [f"-1,234{NB}%", f"+1,234{NB}%"]
        assert f"mot 1,234{NB}% standardavvik" in kort

    def test_signalstyrken_har_brikkene(self, klient):
        _lagret("EQNR", 0.0, 1, -1, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        styrke = html.split('<span class="etikett">Signalstyrke', 1)[1].split("</div>", 1)[0]
        assert '<span class="sjekker stor">' in styrke
        assert re.findall(r'class="sjekk brikke ([a-z]+)"', styrke) == ["pluss", "minus", "null"]

    def test_sjekkene_staar_som_kort_foer_grafen(self, klient):
        """Del 5 og del G, mutant g: kortene med det grå feltet står foran
        grafen, og skalaen er skjult for skjermlesere."""
        _lagret("EQNR", 0.0, 1, 0, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        kort = re.findall(r'<section class="sjekkort[^"]*" aria-label="Sjekk (\d): (\w+)">', html)
        assert kort == [("1", "Trend"), ("2", "Bevegelse"), ("3", "Interesse")]
        assert html.index('class="sjekkort') < html.index("<figure")
        skalaer = re.findall(r'<div class="skala"([^>]*)>(.*?)</div>', html, re.DOTALL)
        assert len(skalaer) == 3
        for attr, innhold in skalaer:
            assert 'aria-hidden="true"' in attr
            assert "gir 0" in innhold
            prikk = re.search(r'class="prikk [a-z]+" style="left: ([\d.]+)%;"', innhold)
            assert prikk and 0.0 <= float(prikk.group(1)) <= 100.0
            # Gjennomgangen (VG5): feltet er like bredt som avstanden mellom
            # grensene, og den lave grensen står til venstre.
            felt = re.search(r'class="felt" style="left: ([\d.]+)%; width: ([\d.]+)%;"', innhold)
            grenser = [float(x) for x in re.findall(r'class="grense" style="left: ([\d.]+)%;"', innhold)]
            assert grenser[0] < grenser[1]
            assert abs(float(felt.group(1)) + float(felt.group(2)) - grenser[1]) < 0.15
        # Prikken har fargen til resultatet i samme kort.
        for kort in re.findall(r'<section class="sjekkort.*?</section>', html, re.DOTALL):
            klasse = re.search(r'class="resultat fortegn ([a-z]+)"', kort).group(1)
            assert f'class="prikk {klasse}"' in kort

    def test_det_graa_feltet_har_fargen_fra_designreglene(self, klient):
        """Del 5 og mutant k: feltet #8A847A på sporet #F1EFEA (3,23:1)."""
        _lagret("EQNR", 0.0, 1, 0, 0)
        stil = _stil(klient.get("/aksje/EQNR").data.decode("utf-8"))
        assert re.search(r"--felt:\s*#8A847A", stil) and re.search(r"--spor:\s*#F1EFEA", stil)
        assert "var(--felt)" in _regel(stil, ".skala .felt")
        assert "#D9D5CB" not in stil.upper()

    def test_grafen_har_heltrukket_snitt_og_navnene_ved_enden(self, klient):
        """Del G, mutant b, og svar 19: ingen stiplet linje, ingen
        tegnforklaring, og navnene står i linjefargen."""
        _lagret("EQNR", 0.0, 1, 0, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        stil = _stil(html)
        assert "dasharray" not in stil and "dashed" not in stil
        assert "stroke-width: 1.75" in _regel(stil, ".ma50linje")
        assert "stroke-width: 2.5" in _regel(stil, ".kurslinje")
        assert "tegnforklaring" not in html
        assert '<text class="linjenavn kurs" text-anchor="end"' in html
        assert '<text class="linjenavn snitt" text-anchor="end"' in html
        assert "var(--snitt)" in _regel(stil, ".linjenavn.snitt")
        assert "stipl" not in _synlig(html).lower()
        # Gjennomgangen 15.10 (VG4): prikken ved enden av kurslinja.
        assert '<circle class="sistepunkt"' in html
        # Gjennomgangen (VG4, BH5): etiketten sier hvilken linje som er hva,
        # med tykkelsen og ikke fargen.
        assert re.search(r'aria-label="Kursutvikling for Equinor: den tykke linja er utbyttejustert kurs, '
                         r'og den tynne er \d+-dagers snitt \(sjekk 1\)"', html)

    def test_tilbakelenken_er_markedsoversikt_uten_pil(self, klient):
        """Del C og mutant d."""
        _lagret("EQNR", 0.0, 1, 0, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert '<a class="tilbake" href="/">Markedsoversikt</a>' in html
        assert not re.search(r"[←→›]", _synlig(html))

    def test_terskelen_i_overskriften_kommer_fra_parametre(self, klient, monkeypatch):
        """Gjennomgangen 15.10 (VG1): med terskel 3 skiller 2 av 3 seg ikke ut
        på aksjesiden heller, og 3 av 3 gjør det. Ville feilet hvis terskelen
        sto fast eller falt tilbake til standarden."""
        import dataclasses

        monkeypatch.setattr(app_modul, "STANDARD", dataclasses.replace(app_modul.STANDARD, terskel=3))
        _lagret("EQNR", 0.0, 1, 1, 0)
        _lagret("KOG", 0.0, 1, 1, 1)
        eqnr = klient.get("/aksje/EQNR").data.decode("utf-8")
        assert '<h1 class="overskrift">Equinor</h1>' in eqnr
        assert "skilte seg ut" not in _synlig(eqnr)
        assert "<mark>skilte seg ut lørdag</mark>" in klient.get("/aksje/KOG").data.decode("utf-8")

    def test_hva_sjekken_maaler_og_regelen_kommer_fra_parametre(self, klient, monkeypatch):
        """Gjennomgangen 15.10 (VG2): kortene sier vinduene og grensene fra
        Parametre, i riktig kort. Ville feilet med faste tall, uten avsnittene
        eller med tekstene byttet mellom kortene."""
        import dataclasses

        from aksjedetalj import hva_den_maaler, regelen

        andre = dataclasses.replace(app_modul.STANDARD, ma_vindu=40, volatilitet_vindu=15, volum_vindu=25,
                                    noytralsone=0.03, volumfaktor=2.5)
        monkeypatch.setattr(app_modul, "STANDARD", andre)
        _lagret("EQNR", 0.0, 1, 0, 0)
        html = klient.get("/aksje/EQNR").data.decode("utf-8")
        kortene = re.findall(r'<section class="sjekkort[^"]*" aria-label="Sjekk \d: (\w+)">(.*?)</section>',
                             html, re.DOTALL)
        assert [navn for navn, _ in kortene] == ["Trend", "Bevegelse", "Interesse"]
        for navn, innhold in kortene:
            assert f'<p class="maaler">{hva_den_maaler(navn, andre)}</p>' in innhold, navn
            assert f'<p class="regel">{regelen(navn, andre)}</p>' in innhold, navn
        trend, bevegelse, interesse = (innhold for _, innhold in kortene)
        assert "de siste 40 børsdagene" in trend and f"Mer enn 3{NB}% over snittet gir +1" in trend
        assert "de siste 15 børsdagene" in bevegelse
        assert "de siste 25 børsdagene" in interesse and "Mer enn 2,5 × medianen" in interesse

    def test_endringen_uten_farge_naar_den_vises_som_null_og_strek_uten_dagen_foer(self, klient, monkeypatch):
        """Gjennomgangen 15.10 (VG3): en endring som vises som 0,00 % har
        ingen farge, som i oversikten, og med én kursdag står «–» uten
        «fra … til …»."""
        _lagret("EQNR", 0.003, 1, 0, 0)
        endring = klient.get("/aksje/EQNR").data.decode("utf-8").split(
            '<div class="noekkeltall endring">', 1)[1].split("</div>", 1)[0]
        assert re.search(rf'<span class="verdi\s*">0,00{NB}%</span>', endring)
        monter(monkeypatch, snapshot({"DNB": serie([100.0])}))
        html = klient.get("/aksje/DNB").data.decode("utf-8")
        en_dag = html.split('<div class="noekkeltall endring">', 1)[1].split("</div>", 1)[0]
        assert '<span class="verdi ">–</span>' in en_dag
        assert "fra " not in en_dag
