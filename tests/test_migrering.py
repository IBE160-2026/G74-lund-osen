"""Tester for migrasjonsloeperen - story 1.1, AD-16.

Hver test lager sin egen katalog med migrasjoner og sin egen basefil under
tmp_path. Ingen test roerer src/migrasjoner/ eller data/.

Den viktigste testen er TestFeilMidtveis. Den finnes fordi den naerliggende
maaten aa kjoere en .sql-fil paa - executescript() - gjoer en implisitt COMMIT
foer den kjoerer noe. Da blir skjemaet halvveis endret mens versjonsraden sier
at ingenting skjedde, og ingenting feiler.
"""

import inspect
import sqlite3

import pytest

import migrering
from migrering import MigrasjonsFeil, migrer, versjon


def skriv_migrasjon(katalog, nummer: int, navn: str, sql: str):
    katalog.mkdir(exist_ok=True)
    sti = katalog / f"{nummer:04d}_{navn}.sql"
    sti.write_text(sql, encoding="utf-8")
    return sti


def skjema(tilkobling) -> list[tuple]:
    """Alt som finnes i basen, uten versjonstabellen."""
    return tilkobling.execute(
        "SELECT type, name, sql FROM sqlite_master "
        "WHERE name != 'skjema_versjon' ORDER BY type, name"
    ).fetchall()


def tabeller(tilkobling) -> set[str]:
    return {navn for _, navn, _ in skjema(tilkobling)}


@pytest.fixture
def katalog(tmp_path):
    return tmp_path / "migrasjoner"


@pytest.fixture
def base(tmp_path):
    tilkobling = sqlite3.connect(tmp_path / "ose.db")
    yield tilkobling
    tilkobling.close()


class TestTomBase:
    def test_tom_base_har_versjon_null(self, base):
        assert versjon(base) == 0

    def test_aa_lese_versjonen_endrer_ikke_basen(self, base):
        versjon(base)

        assert base.execute("SELECT count(*) FROM sqlite_master").fetchone()[0] == 0

    def test_kjoeres_opp_til_nyeste_versjon(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "b", "CREATE TABLE b (y INTEGER);")
        skriv_migrasjon(katalog, 3, "c", "CREATE TABLE c (z INTEGER);")

        assert migrer(base, katalog) == 3
        assert versjon(base) == 3
        assert tabeller(base) == {"a", "b", "c"}

    def test_versjonen_overlever_en_ny_tilkobling(self, tmp_path, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        foerste = sqlite3.connect(tmp_path / "ose.db")
        migrer(foerste, katalog)
        foerste.close()

        andre = sqlite3.connect(tmp_path / "ose.db")
        try:
            assert versjon(andre) == 1
        finally:
            andre.close()

    def test_en_base_paa_versjon_to_faar_bare_den_tredje(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "b", "CREATE TABLE b (y INTEGER);")
        migrer(base, katalog)
        skriv_migrasjon(katalog, 3, "c", "CREATE TABLE c (z INTEGER);")

        assert migrer(base, katalog) == 3
        assert tabeller(base) == {"a", "b", "c"}

    def test_flere_setninger_i_en_fil(self, base, katalog):
        skriv_migrasjon(
            katalog,
            1,
            "to_tabeller",
            "CREATE TABLE a (x INTEGER);\n"
            "-- en kommentar med semikolon; midt i\n"
            "CREATE TABLE b (tekst TEXT DEFAULT 'a;b');\n",
        )

        migrer(base, katalog)

        assert tabeller(base) == {"a", "b"}


class TestToGanger:
    def test_andre_kjoering_endrer_ingenting(self, base, katalog):
        """Migrasjonen setter inn en rad. Kjoeres den paa nytt, blir det to."""
        skriv_migrasjon(
            katalog,
            1,
            "med_rad",
            "CREATE TABLE a (x INTEGER);\nINSERT INTO a VALUES (1);",
        )
        migrer(base, katalog)
        foer = skjema(base)

        assert migrer(base, katalog) == 1
        assert skjema(base) == foer
        assert base.execute("SELECT count(*) FROM a").fetchone()[0] == 1

    def test_to_kall_fra_samme_prosess_oppfoerer_seg_likt(self, tmp_path, katalog):
        """Ingen skjult tilstand i modulen: to baser i samme prosess faar
        samme resultat, og en fil lagt til mellom to kall blir sett."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        en = sqlite3.connect(tmp_path / "en.db")
        to = sqlite3.connect(tmp_path / "to.db")
        try:
            assert migrer(en, katalog) == migrer(to, katalog) == 1
            assert skjema(en) == skjema(to)

            skriv_migrasjon(katalog, 2, "b", "CREATE TABLE b (y INTEGER);")
            assert migrer(en, katalog) == 2
        finally:
            en.close()
            to.close()


class TestFeilMidtveis:
    """Ville feilet hvis loeperen brukte executescript()."""

    def test_versjonsraden_staar_paa_tallet_fra_foer(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        migrer(base, katalog)
        skriv_migrasjon(
            katalog,
            2,
            "feiler",
            "CREATE TABLE halvveis (x INTEGER);\nDETTE ER IKKE SQL;",
        )

        with pytest.raises(MigrasjonsFeil):
            migrer(base, katalog)

        assert versjon(base) == 1

    def test_skjemaet_er_ikke_halvveis_endret(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        migrer(base, katalog)
        foer = skjema(base)
        skriv_migrasjon(
            katalog,
            2,
            "feiler",
            "CREATE TABLE halvveis (x INTEGER);\nDETTE ER IKKE SQL;",
        )

        with pytest.raises(MigrasjonsFeil):
            migrer(base, katalog)

        assert "halvveis" not in tabeller(base)
        assert skjema(base) == foer

    def test_feil_i_foerste_migrasjon_lar_tom_base_vaere_tom(self, base, katalog):
        skriv_migrasjon(
            katalog,
            1,
            "feiler",
            "CREATE TABLE halvveis (x INTEGER);\nDETTE ER IKKE SQL;",
        )

        with pytest.raises(MigrasjonsFeil):
            migrer(base, katalog)

        assert versjon(base) == 0
        assert tabeller(base) == set()

    def test_migrasjoner_etter_den_som_feilet_kjoeres_ikke(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "feiler", "DETTE ER IKKE SQL;")
        skriv_migrasjon(katalog, 3, "c", "CREATE TABLE c (z INTEGER);")

        with pytest.raises(MigrasjonsFeil):
            migrer(base, katalog)

        assert versjon(base) == 1
        assert tabeller(base) == {"a"}

    def test_feilen_navngir_fila(self, base, katalog):
        skriv_migrasjon(katalog, 1, "feiler", "DETTE ER IKKE SQL;")

        with pytest.raises(MigrasjonsFeil, match="0001_feiler.sql"):
            migrer(base, katalog)

    def test_en_retting_av_fila_kan_kjoeres_etterpaa(self, base, katalog):
        """Tilbakerullingen er hele poenget: neste kjoering starter rent."""
        sti = skriv_migrasjon(
            katalog, 1, "a", "CREATE TABLE a (x INTEGER);\nDETTE ER IKKE SQL;"
        )
        with pytest.raises(MigrasjonsFeil):
            migrer(base, katalog)

        sti.write_text("CREATE TABLE a (x INTEGER);", encoding="utf-8")

        assert migrer(base, katalog) == 1
        assert tabeller(base) == {"a"}


class TestNummerering:
    """To av oss som lager hver sin 0002, er nettopp det storyen skal hindre."""

    def test_to_filer_med_samme_nummer_avvises(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "min", "CREATE TABLE b (y INTEGER);")
        skriv_migrasjon(katalog, 2, "din", "CREATE TABLE c (z INTEGER);")

        with pytest.raises(MigrasjonsFeil, match="0002"):
            migrer(base, katalog)

        assert versjon(base) == 0

    def test_hull_i_nummereringen_avvises(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 3, "c", "CREATE TABLE c (z INTEGER);")

        with pytest.raises(MigrasjonsFeil, match="0002"):
            migrer(base, katalog)

        assert versjon(base) == 0

    def test_base_nyere_enn_katalogen_avvises(self, base, katalog):
        """Basen er migrert av en nyere utgave av koden. Aa fortsette ville
        vaert aa lese et skjema koden ikke kjenner."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "b", "CREATE TABLE b (y INTEGER);")
        migrer(base, katalog)
        (katalog / "0002_b.sql").unlink()

        with pytest.raises(MigrasjonsFeil, match="versjon 2"):
            migrer(base, katalog)

    def test_andre_filer_i_katalogen_ignoreres(self, base, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        (katalog / "LESMEG.md").write_text("ikke en migrasjon", encoding="utf-8")

        assert migrer(base, katalog) == 1


class TestTransaksjonenEiesAvLoeperen:
    def test_aapen_transaksjon_hos_kalleren_avvises(self, base, katalog):
        """Loeperen styrer transaksjonen selv (AD-16). Har kalleren en aapen,
        ville loeperens COMMIT tatt med seg kallerens endringer."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        base.execute("CREATE TABLE kallerens (x INTEGER)")
        base.execute("INSERT INTO kallerens VALUES (1)")
        assert base.in_transaction

        with pytest.raises(MigrasjonsFeil, match="transaksjon"):
            migrer(base, katalog)

        assert versjon(base) == 0


class TestIngenUnntaksvei:
    """Storyen: ingen DROP TABLE-hjelper, ingen rebuild-mekanikk, ingen
    unntaksvei for lagre AD-7 verner. Trengs det, skal det besluttes synlig."""

    def test_modulen_har_bare_to_offentlige_funksjoner(self):
        funksjoner = {
            navn
            for navn, obj in inspect.getmembers(migrering, inspect.isfunction)
            if obj.__module__ == "migrering" and not navn.startswith("_")
        }

        assert funksjoner == {"migrer", "versjon"}

    def test_migrer_tar_bare_tilkobling_og_katalog(self):
        assert list(inspect.signature(migrer).parameters) == ["tilkobling", "katalog"]
