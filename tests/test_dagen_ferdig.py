"""Story 2.3d, gruppens svar 05.11 kl. 12:33 og 19:33 (forslag a): sjekken
foer steg 3 i kveldsjobben, src/dagen_ferdig.py.

Basen lages i tmp_path av kjoer med en falsk EODHD og en falsk modell, som i
test_ki_tekst.py. Aldri den ekte basen, og ingen kall (AD-8).
"""

import hashlib
import sqlite3
from datetime import date, datetime, timezone

import pytest

import dagen_ferdig
from dagen_ferdig import FERDIG, main, mangler_for_dagen
from test_fetch_prices import serie_med_utslag
from test_ki_tekst import OEYEBLIKK, TIRSDAG, FalskModell, kjoer


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


def _sha(sti):
    return hashlib.sha256(sti.read_bytes()).hexdigest()


def _sjekk(base, capsys, oeyeblikk=OEYEBLIKK):
    kode = main(base, oeyeblikk)
    return kode, capsys.readouterr().out


def test_en_ferdig_dag_gir_ferdig_og_kode_0(stier, capsys):
    """Ville feilet hvis en dag med kursene, vurderingene, indeksen og
    KI-tekstene ikke ga FERDIG foerst paa linja og kode 0, som jobben krever
    for aa hoppe over Docker og Ollama."""
    raa, base = stier
    assert kjoer(raa, base, FalskModell())[0] == 0
    assert mangler_for_dagen(base, OEYEBLIKK) == (TIRSDAG, [])
    kode, ut = _sjekk(base, capsys)
    assert kode == 0
    assert ut.startswith(f"{FERDIG} {TIRSDAG.isoformat()}"), ut


def test_basen_er_lik_foer_og_etter_sjekken(stier, capsys):
    """Ville feilet hvis sjekken skrev til basen (migrering, journal eller
    rader): sha256 er den samme foer og etter, ogsaa naar noe mangler."""
    raa, base = stier
    kjoer(raa, base, None)
    foer = _sha(base)
    _sjekk(base, capsys)
    assert _sha(base) == foer
    assert not base.with_name(base.name + "-journal").exists()
    assert not base.with_name(base.name + "-wal").exists()


def test_en_dag_uten_ki_tekster_er_ikke_ferdig(stier, capsys):
    """Ville feilet hvis KI-tekstene ikke var med i sjekken: uten modell har
    hver aksje med en vurdering ingen rad i KI-loggen, og kjoeringen gaar som
    foer, med Ollama."""
    raa, base = stier
    kjoer(raa, base, None)
    dato, mangler = mangler_for_dagen(base, OEYEBLIKK)
    assert dato == TIRSDAG
    assert mangler and all(m.startswith("KI-tekst ") for m in mangler), mangler
    kode, ut = _sjekk(base, capsys)
    assert kode == 1 and FERDIG not in ut


def test_en_dag_uten_hovedindeksen_er_ikke_ferdig(stier, capsys):
    """Ville feilet hvis hovedindeksen ikke var med: kallet for OSEBX.OL
    feiler, saa indeks mangler raden, mens aksjene og KI-tekstene er der."""
    raa, base = stier

    def hent(ticker, *_):
        if ticker.startswith("OSEBX"):
            raise ConnectionError("nede")
        return serie_med_utslag(TIRSDAG)

    kjoer(raa, base, FalskModell(), hent=hent)
    _, mangler = mangler_for_dagen(base, OEYEBLIKK)
    assert mangler == ["indeks OSEBX"], mangler
    kode, ut = _sjekk(base, capsys)
    assert kode == 1 and FERDIG not in ut


def test_dagen_er_inneveerende_boersdag_fra_norsk_dato(stier, capsys):
    """Ville feilet hvis sjekken brukte kjoeredagen og ikke boersdagen
    hentingen gjelder: loerdag 26.09 er tirsdagen ikke ferdig, fordi
    inneveerende boersdag er fredag 25.09. Og kl. 00:30 norsk tid onsdag
    (22:30 UTC tirsdag) gjelder onsdagen, ikke tirsdagen."""
    raa, base = stier
    kjoer(raa, base, FalskModell())
    loerdag = datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc)
    assert mangler_for_dagen(base, loerdag)[0] == date(2026, 9, 25)
    assert mangler_for_dagen(base, loerdag)[1]
    etter_midnatt = datetime(2026, 9, 22, 22, 30, tzinfo=timezone.utc)
    assert mangler_for_dagen(base, etter_midnatt)[0] == date(2026, 9, 23)
    assert _sjekk(base, capsys, etter_midnatt)[0] == 1


def test_uten_base_mangler_alt(tmp_path, capsys):
    """Ville feilet hvis en base som ikke finnes, ble regnet som ferdig, eller
    ble laget av sjekken."""
    base = tmp_path / "db" / "ose.db"
    kode, ut = _sjekk(base, capsys)
    assert kode == 1 and FERDIG not in ut
    assert not base.exists()


def test_en_feil_i_sjekken_gir_kode_2_og_ikke_ferdig(stier, capsys, monkeypatch):
    """Ville feilet hvis en feil ved lesingen ga FERDIG eller kode 0: da
    hoppet jobben over Ollama for en dag som kanskje ikke er ferdig."""
    raa, base = stier
    kjoer(raa, base, FalskModell())

    def feiler(*_a, **_k):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(dagen_ferdig, "manglende_vurderinger", feiler)
    kode, ut = _sjekk(base, capsys)
    assert kode == 2 and FERDIG not in ut


def test_en_base_som_ikke_er_sqlite_gir_kode_2(tmp_path, capsys):
    """Ville feilet hvis en oedelagt base ga FERDIG."""
    base = tmp_path / "ose.db"
    base.write_bytes(b"ikke en base" * 100)
    foer = _sha(base)
    kode, ut = _sjekk(base, capsys)
    assert kode == 2 and FERDIG not in ut
    assert _sha(base) == foer


def test_sjekken_leser_ikke_env_og_kaller_ikke(stier, capsys, monkeypatch):
    """Ville feilet hvis sjekken leste noekkelen eller kalte EODHD: begge er
    byttet ut med noe som feiler testen."""
    import fetch_prices

    raa, base = stier
    kjoer(raa, base, FalskModell())

    def forbudt(*_a, **_k):
        raise AssertionError("sjekken skal verken lese .env eller kalle")

    monkeypatch.setattr(fetch_prices, "hent_api_nokkel", forbudt)
    monkeypatch.setattr(fetch_prices, "hent_ett_symbol", forbudt)
    monkeypatch.setattr(fetch_prices, "hent_kvote", forbudt)
    monkeypatch.setattr(fetch_prices, "load_dotenv", forbudt)
    assert _sjekk(base, capsys)[0] == 0


def test_basen_er_lik_foer_og_etter_ogsaa_for_en_ferdig_dag(stier, capsys):
    """Gjennomgangen (VG2). Ville feilet hvis banen for en ferdig dag, den
    eneste der jobben hopper over noe, skrev til basen."""
    raa, base = stier
    kjoer(raa, base, FalskModell())
    foer = _sha(base)
    assert _sjekk(base, capsys)[0] == 0
    assert _sha(base) == foer


def test_utskriften_passer_regexen_i_skriptet(stier, capsys):
    """Gjennomgangen (BH9, VG9). Ville feilet hvis utskriften fra sjekken og
    regexen i start/kveldshenting.ps1 ikke passet sammen: en ferdig dag gir
    noeyaktig én linje som passer (-cmatch, store bokstaver), og en dag som
    mangler noe, gir ingen."""
    import re

    from test_kveldshenting import JOBBEN

    skriptet = JOBBEN.read_text(encoding="utf-8-sig")
    funnet = re.search(r"-cmatch '([^']+)'", skriptet)
    assert funnet, "fant ikke -cmatch i skriptet"
    regex = re.compile(funnet.group(1))
    raa, base = stier
    kjoer(raa, base, FalskModell())
    kode, ut = _sjekk(base, capsys)
    assert kode == 0 and len([linje for linje in ut.splitlines() if regex.match(linje)]) == 1, ut
    kjoer(raa, base.with_name("annen.db"), None)
    kode, ut = _sjekk(base.with_name("annen.db"), capsys)
    assert kode == 1 and not any(regex.match(linje) for linje in ut.splitlines()), ut
