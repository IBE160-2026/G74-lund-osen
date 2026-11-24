"""Story 2.14: eks.datoer føres inn for hånd (FR-414).

Spesifikasjonen er spec-2-14-eksdatoer.md. Symbolet, nettstedet og datoene i
testene er oppdiktet: ingen eks.dato fra en kilde står i en sporet fil
(regel 16). Hver test lager sin egen base under tmp_path (regel 22), og ingen
test gjør nettkall (AD-8). Klokka er fast: «i dag» gis som argument.
"""

import re
import sqlite3
from datetime import date
from pathlib import Path

import pytest

import eksdato
import ferdige_lister
import lagring_sqlite
from lagring_sqlite import MIGRASJONSKATALOG, aapne_base
from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23
from test_tatt_inn_9_28 import _foelg
from test_valg import FASTE, med_boersen

ROT = Path(__file__).resolve().parents[1]
IDAG = date(2026, 9, 23)
SJEKKET = "2026-09-23"
EKS = "2026-10-15"
FLYTTET = "2026-10-22"
NETTSTED = "nyaksje.example"
KILDE = f"https://www.{NETTSTED}/investor/utbytte"


@pytest.fixture(autouse=True)
def faste_bransjer(monkeypatch):
    for kode, bransje in FASTE.items():
        monkeypatch.setitem(ferdige_lister.BRANSJE, kode, bransje)


def _vilkaar(tmp_path: Path, *rader: str, overskrift: str = eksdato.OVERSKRIFT) -> Path:
    """En kilder-og-rettigheter.md med de oppgitte radene i tabellen."""
    fil = tmp_path / "kilder-og-rettigheter.md"
    fil.write_text(
        "# Kilder og rettigheter\n\n## Status per kilde\n\n| Kilde | Brukes til |\n|---|---|\n| NYA | noe annet |\n\n"
        f"{overskrift}\n\nTekst.\n\n| Symbol | Nettsted | Vilkår lest | Vurdering |\n|---|---|---|---|\n"
        + "".join(rad + "\n" for rad in rader)
        + "\n---\n\n## Neste del\n\n| NYB | nyb.example | 2026-09-01 | ja |\n",
        encoding="utf-8",
    )
    return fil


RAD = f"| NYA | {NETTSTED} | 2026-09-20 | Ja, lest av gruppen |"


@pytest.fixture
def base(tmp_path):
    """En base der den oppdiktede aksjen NYA er tatt inn i lista av hentingen."""
    raa, sti = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, sti, OEYEBLIKK_22_09)
    med_boersen(sti)
    _foelg(sti)
    kjoer_23(raa, sti, OEYEBLIKK_22_09.replace(day=23))
    return sti


def _rader(sti) -> list[tuple]:
    tilkobling = aapne_base(sti)
    try:
        return tilkobling.execute("SELECT symbol, eks_dato, sjekket, kilde FROM eksdato ORDER BY symbol").fetchall()
    finally:
        tilkobling.close()


def _kjoer(sti, vilkaar, symbol="NYA", eks=EKS, sjekket=SJEKKET, kilde=KILDE, idag=IDAG) -> tuple[int, str]:
    linjer: list[str] = []
    kode = eksdato.kjoer(sti, symbol, eks, sjekket, kilde, idag, linjer.append, vilkaar)
    return kode, "\n".join(linjer)


class TestTabellen:
    def test_migrasjonen_lager_tabellen_uten_rader(self, tmp_path):
        """AD-16. Ville feilet hvis tabellen manglet en av de fire
        kolonnene, eller migrasjonen la inn en dato (regel 16)."""
        tilkobling = aapne_base(tmp_path / "db" / "ose.db")
        try:
            kolonner = [rad[1] for rad in tilkobling.execute("PRAGMA table_info(eksdato)")]
            assert kolonner == ["symbol", "eks_dato", "sjekket", "kilde"]
            assert tilkobling.execute("SELECT count(*) FROM eksdato").fetchone()[0] == 0
        finally:
            tilkobling.close()
        sql = (MIGRASJONSKATALOG / "0016_eksdato.sql").read_text(encoding="utf-8")
        assert "INSERT INTO" not in sql.upper().replace("BEFORE INSERT ON", "")
        assert not re.search(r"\d{4}-\d{2}-\d{2}", re.sub(r"(?m)^--.*$", "", sql))

    @pytest.mark.parametrize(
        ("rad", "hva"),
        [
            (("NYA", "2026-10-15", None, KILDE), "uten dato for sjekken"),
            (("NYA", "2026-10-15", "", KILDE), "tom dato for sjekken"),
            (("NYA", "2026-10-15", SJEKKET, None), "uten kilde"),
            (("NYA", "2026-10-15", SJEKKET, "   "), "tom kilde"),
            (("NYA", "2026-02-30", "2026-02-01", KILDE), "en dato som ikke finnes"),
            (("NYA", "15.10.2026", SJEKKET, KILDE), "en dato med annen form"),
            (("NYA", "2026-09-22", SJEKKET, KILDE), "eks.dato før sjekken"),
            (("FINSIKKE", "2026-10-15", SJEKKET, KILDE), "et symbol som ikke står i aksje"),
        ],
    )
    def test_basen_avviser(self, base, rad, hva):
        """Ville feilet hvis en dato kunne lagres uten dato for sjekken eller
        uten kilde, også av noe annet enn kommandoen."""
        tilkobling = aapne_base(base)
        try:
            with pytest.raises(sqlite3.IntegrityError), tilkobling:
                tilkobling.execute("INSERT INTO eksdato (symbol, eks_dato, sjekket, kilde) VALUES (?, ?, ?, ?)", rad)
        finally:
            tilkobling.close()

    def test_ett_symbol_har_hoeyst_en_rad(self, base):
        tilkobling = aapne_base(base)
        try:
            with tilkobling:
                tilkobling.execute("INSERT INTO eksdato VALUES ('NYA', ?, ?, ?)", (EKS, SJEKKET, KILDE))
            with pytest.raises(sqlite3.IntegrityError), tilkobling:
                tilkobling.execute("INSERT INTO eksdato VALUES ('NYA', ?, ?, ?)", (FLYTTET, SJEKKET, KILDE))
        finally:
            tilkobling.close()


class TestKommandoen:
    def test_en_dato_for_ett_symbol_lagres(self, base, tmp_path):
        """Ville feilet hvis datoen, sjekkdatoen eller kilden ikke ble lagret."""
        kode, ut = _kjoer(base, _vilkaar(tmp_path, RAD))
        assert kode == 0, ut
        assert _rader(base) == [("NYA", EKS, SJEKKET, KILDE)]
        assert "NYA" in ut and "er lagret" in ut

    def test_symbolet_kan_skrives_med_smaa_bokstaver(self, base, tmp_path):
        assert _kjoer(base, _vilkaar(tmp_path, RAD), symbol=" nya ")[0] == 0
        assert _rader(base) == [("NYA", EKS, SJEKKET, KILDE)]

    def test_uten_vilkaar_faar_symbolet_ingen_dato(self, base, tmp_path):
        """FR-414. Ville feilet hvis et symbol fikk en dato uten at
        vilkårene for nettstedet er ført."""
        kode, ut = _kjoer(base, _vilkaar(tmp_path))
        assert kode == 1 and _rader(base) == []
        assert "Vilkårene for nettstedet til NYA er ikke ført" in ut and "kilder-og-rettigheter.md" in ut

    @pytest.mark.parametrize(
        "rad",
        [
            f"| NYA | {NETTSTED} | 2026-09-20 | nei, vilkårene forbyr det |",
            f"| NYA | {NETTSTED} | 2026-09-20 | uklart |",
            f"| NYA | {NETTSTED} | 2026-09-20 | javel |",
            f"| NYA | {NETTSTED} | 2026-09-20 |  |",
            f"| NYA | {NETTSTED} | ikke lest | ja |",
            f"| NYA | {NETTSTED} |  | ja |",
            f"| NYA | {NETTSTED} | 2026-02-30 | ja |",
            f"| NYA | {NETTSTED} | 2026-09-24 | ja |",
            "| NYA |  | 2026-09-20 | ja |",
            "| NYA | https://nyaksje.example/vilkaar | 2026-09-20 | ja |",
            f"| NYA | {NETTSTED} | 2026-09-20 |",
            f"| NYB | {NETTSTED} | 2026-09-20 | ja |",
        ],
    )
    def test_en_rad_som_ikke_er_i_orden_gir_ingen_dato(self, base, tmp_path, rad):
        """Ville feilet hvis en rad uten «ja», uten en dato vilkårene ble
        lest, med en dato etter i dag, uten nettsted, eller for et annet
        symbol, ga symbolet en dato."""
        kode, ut = _kjoer(base, _vilkaar(tmp_path, rad))
        assert kode == 1 and _rader(base) == [], ut

    def test_en_god_og_en_daarlig_rad_for_samme_symbol_gir_ingen_dato(self, base, tmp_path):
        """Ville feilet hvis en gammel «ja»-rad vant over en nyere «nei»."""
        nei = f"| NYA | {NETTSTED} | 2026-09-21 | nei |"
        for rader in ((RAD, nei), (nei, RAD), (RAD, "| NYA | annet.example | 2026-09-20 | ja |")):
            assert _kjoer(base, _vilkaar(tmp_path, *rader))[0] == 1
        assert _rader(base) == []

    def test_raden_maa_staa_under_overskriften(self, base, tmp_path):
        """Ville feilet hvis en rad i en annen tabell i dokumentet ga en dato:
        NYB står bare i delen etter, og NYA i «Status per kilde»."""
        fil = _vilkaar(tmp_path, RAD)
        assert eksdato.les_vilkaar(fil, IDAG) == {"NYA": NETTSTED}
        assert eksdato.les_vilkaar(_vilkaar(tmp_path, RAD, overskrift="## En annen del"), IDAG) == {}
        assert eksdato.les_vilkaar(tmp_path / "finnes-ikke.md", IDAG) == {}

    @pytest.mark.parametrize(
        "kilde",
        [
            "https://annet.example/utbytte",
            f"https://{NETTSTED}.annet.example/utbytte",
            f"https://ikke{NETTSTED}/utbytte",
            f"ftp://{NETTSTED}/utbytte",
            f"{NETTSTED}/utbytte",
            "investorsiden",
            "",
            "   ",
        ],
    )
    def test_kilden_maa_vaere_en_adresse_paa_nettstedet(self, base, tmp_path, kilde):
        """Ville feilet hvis en dato kunne føres inn uten kilde, eller med en
        kilde fra et nettsted vilkårene ikke er ført for."""
        kode, ut = _kjoer(base, _vilkaar(tmp_path, RAD), kilde=kilde)
        assert kode == 1 and _rader(base) == [], ut

    def test_kilden_kan_vaere_nettstedet_selv_eller_et_underdomene(self, base, tmp_path):
        for kilde in (f"https://{NETTSTED}/utbytte", f"https://IR.{NETTSTED.upper()}/"):
            assert _kjoer(base, _vilkaar(tmp_path, RAD), kilde=kilde)[0] == 0

    @pytest.mark.parametrize(
        ("eks", "sjekket", "del_av_grunnen"),
        [
            ("15.10.2026", SJEKKET, "ÅÅÅÅ-MM-DD"),
            ("2026-02-30", "2026-02-01", "ikke en dato som finnes"),
            (EKS, "i går", "ÅÅÅÅ-MM-DD"),
            (EKS, "2026-09-24", "etter i dag"),
            ("2026-09-22", SJEKKET, "ikke en kommende dato"),
        ],
    )
    def test_datoene_maa_kunne_leses_og_henge_sammen(self, base, tmp_path, eks, sjekket, del_av_grunnen):
        """Ville feilet hvis en dato som ikke finnes, en sjekk i framtiden,
        eller en eks.dato som alt er passert da den ble sjekket, ble lagret."""
        kode, ut = _kjoer(base, _vilkaar(tmp_path, RAD), eks=eks, sjekket=sjekket)
        assert kode == 1 and del_av_grunnen in ut and _rader(base) == []

    def test_eks_dato_samme_dag_som_sjekken_godtas(self, base, tmp_path):
        assert _kjoer(base, _vilkaar(tmp_path, RAD), eks=SJEKKET)[0] == 0

    def test_et_symbol_utenfor_lista_avvises(self, base, tmp_path):
        """Ville feilet hvis et symbol som ikke står i lista, eller som er
        tatt ut av den, fikk en dato."""
        rad_nyc = "| NYC | nyc.example | 2026-09-20 | ja |"
        kode, ut = _kjoer(base, _vilkaar(tmp_path, RAD, rad_nyc), symbol="NYC", kilde="https://nyc.example/")
        assert kode == 1 and "står ikke i lista" in ut
        tilkobling = aapne_base(base)
        try:
            with tilkobling:
                tilkobling.execute("UPDATE aksje SET ut = '2026-09-24' WHERE symbol = 'NYA'")
        finally:
            tilkobling.close()
        kode, ut = _kjoer(base, _vilkaar(tmp_path, RAD))
        assert kode == 1 and "står ikke i lista" in ut and _rader(base) == []


class TestNySjekk:
    def test_samme_dato_sjekket_paa_nytt_oppdaterer_sjekken(self, base, tmp_path):
        """Ville feilet hvis en ny sjekk av samme dato ga to rader, eller
        lot den gamle sjekkdatoen stå."""
        vilkaar = _vilkaar(tmp_path, RAD)
        assert _kjoer(base, vilkaar, sjekket="2026-09-21")[0] == 0
        ny_kilde = f"https://{NETTSTED}/finanskalender"
        kode, ut = _kjoer(base, vilkaar, sjekket=SJEKKET, kilde=ny_kilde)
        assert kode == 0 and "står, og er nå sjekket" in ut
        assert _rader(base) == [("NYA", EKS, SJEKKET, ny_kilde)]

    def test_en_flyttet_dato_erstatter_den_gamle(self, base, tmp_path):
        """Ville feilet hvis den gamle datoen ble stående ved siden av den
        nye, eller den nye ble avvist."""
        vilkaar = _vilkaar(tmp_path, RAD)
        assert _kjoer(base, vilkaar, sjekket="2026-09-21")[0] == 0
        kode, ut = _kjoer(base, vilkaar, eks=FLYTTET)
        assert kode == 0 and "flyttet" in ut and EKS in ut and FLYTTET in ut
        assert _rader(base) == [("NYA", FLYTTET, SJEKKET, KILDE)]

    def test_en_eldre_sjekk_skriver_ikke_over_en_nyere(self, base, tmp_path):
        """Ville feilet hvis en sjekk fra en tidligere dag erstattet det som
        ble lest sist."""
        vilkaar = _vilkaar(tmp_path, RAD)
        assert _kjoer(base, vilkaar, eks=FLYTTET)[0] == 0
        kode, ut = _kjoer(base, vilkaar, sjekket="2026-09-21")
        assert kode == 1 and "sjekket senere" in ut
        assert _rader(base) == [("NYA", FLYTTET, SJEKKET, KILDE)]


class TestGrensene:
    def test_kommandoen_krever_sjekket_og_kilde(self, capsys):
        """Ville feilet hvis --sjekket fikk dagens dato når den ikke ble
        gitt, eller --kilde kunne utelates."""
        for argumenter in (["NYA", EKS, "--kilde", KILDE], ["NYA", EKS, "--sjekket", SJEKKET], ["NYA", EKS]):
            with pytest.raises(SystemExit) as slutt:
                eksdato.main(argumenter)
            assert slutt.value.code == 2
        capsys.readouterr()

    def test_main_bruker_basen_og_dagens_dato(self, base, tmp_path, monkeypatch, capsys):
        """Ville feilet hvis main ikke ga basen, vilkårene og utgangskoden
        videre. Vilkårsfila i repoet har ingen rad for NYA, så den avvises."""
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        with pytest.raises(SystemExit) as slutt:
            eksdato.main(["NYA", EKS, "--sjekket", SJEKKET, "--kilde", KILDE])
        assert slutt.value.code == 1 and "Ikke lagret" in capsys.readouterr().out
        monkeypatch.setattr(eksdato, "VILKAAR", _vilkaar(tmp_path, RAD))
        with pytest.raises(SystemExit) as slutt:
            eksdato.main(["NYA", "2099-01-15", "--sjekket", SJEKKET, "--kilde", KILDE])
        assert slutt.value.code == 0 and "er lagret" in capsys.readouterr().out
        assert _rader(base) == [("NYA", "2099-01-15", SJEKKET, KILDE)]

    def test_en_base_som_ikke_finnes_lages_ikke(self, tmp_path):
        sti = tmp_path / "db" / "ose.db"
        kode, ut = _kjoer(sti, _vilkaar(tmp_path, RAD))
        assert kode == 1 and "finnes ikke" in ut and not sti.exists()

    def test_demobasen_faar_ingen_dato(self, tmp_path):
        """FR-411. Ville feilet hvis en demobase ble migrert eller skrevet."""
        import demo

        sti = tmp_path / "db" / "demo.db"
        demo.lag_demobase(sti)
        foer = sti.read_bytes()
        kode, ut = _kjoer(sti, _vilkaar(tmp_path, RAD))
        assert kode == 1 and "demobase" in ut and sti.read_bytes() == foer

    def test_kommandoen_gjoer_ingen_nettkall(self):
        """Ville feilet hvis programmet kunne hente en side fra et selskap:
        modulen importerer ingenting som kan gjøre et kall. conftest.py
        sperrer dessuten nettet i alle testene (AD-8)."""
        kilde = (ROT / "src" / "eksdato.py").read_text(encoding="utf-8")
        importert = set(re.findall(r"(?m)^(?:from|import)\s+([\w.]+)", kilde))
        assert importert == {
            "argparse",
            "re",
            "sqlite3",
            "sys",
            "datetime",
            "pathlib",
            "typing",
            "urllib.parse",
            "lagring_sqlite",
            "boersdag",
            "migrering",
        }
        for forbudt in ("requests", "urlopen", "socket", "http.client", "eodhd", "fetch_prices"):
            assert forbudt not in kilde

    def test_webserveren_skriver_ikke_tabellen(self):
        """AD-3, AD-10. Ville feilet hvis en annen modul i src/, eller en
        mal, skrev eller leste tabellen: kommandoen er eneste skriver, og
        visningen (FR-207) er ikke bygget."""
        for fil in sorted((ROT / "src").rglob("*")):
            if fil.suffix not in (".py", ".html", ".js") or fil.name == "eksdato.py":
                continue
            # Ordet for seg, så «indeksdato» i en mal ikke teller.
            assert not re.search(r"(?<![a-zæøå])eksdato", fil.read_text(encoding="utf-8").lower()), fil.name

    def test_ingen_eks_dato_staar_i_modulen_eller_vilkaarene(self):
        """Regel 16. Ville feilet hvis en dato sto skrevet inn i modulen,
        eller delen i kilder-og-rettigheter.md hadde en eks.dato."""
        kilde = (ROT / "src" / "eksdato.py").read_text(encoding="utf-8")
        assert not re.search(r"\d{4}-\d{2}-\d{2}", kilde)
        tekst = (ROT / "docs" / "kilder-og-rettigheter.md").read_text(encoding="utf-8")
        assert tekst.count(eksdato.OVERSKRIFT) == 1
        delen = tekst.split(eksdato.OVERSKRIFT, 1)[1].split("\n## ", 1)[0]
        assert "| " + " | ".join(eksdato.KOLONNER) + " |" in delen
        assert "src/eksdato.py" in delen and "eks.dato" in delen
        # Det som står i tabellen, leses uten feil. Gruppen fører radene selv.
        assert isinstance(eksdato.les_vilkaar(ROT / "docs" / "kilder-og-rettigheter.md", date(2100, 1, 1)), dict)
