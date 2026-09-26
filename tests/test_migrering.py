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

        # Story 1.5b, h: tabeller() filtrerer bort skjema_versjon, saa den
        # sjekken ville ikke sett en versjonstabell som ble staaende igjen.
        assert versjon(base) == 0
        assert base.execute("SELECT count(*) FROM sqlite_master").fetchone()[0] == 0

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


def alt_i_basen(tilkobling) -> int:
    return tilkobling.execute("SELECT count(*) FROM sqlite_master").fetchone()[0]


class TestAnvendteFiler:
    """Story 1.5b, a og e: basen husker hvilke filer som ble kjoert, og
    hvordan de saa ut."""

    def test_nytt_filnavn_paa_et_anvendt_nummer_avvises(self, base, katalog):
        """a: to av oss som skriver hver sin 0002, og den ene er alt kjoert."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "min", "CREATE TABLE b (y INTEGER);")
        migrer(base, katalog)
        (katalog / "0002_min.sql").rename(katalog / "0002_din.sql")

        with pytest.raises(MigrasjonsFeil, match="0002_min.sql.*0002_din.sql"):
            migrer(base, katalog)

    def test_endret_innhold_i_en_kjoert_fil_avvises(self, base, katalog):
        """e: samme filnavn, annet innhold."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        migrer(base, katalog)
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE helt_annet (z TEXT);")

        with pytest.raises(MigrasjonsFeil, match="0001_a.sql er endret"):
            migrer(base, katalog)

    def test_crlf_i_stedet_for_lf_gir_samme_hash(self, base, katalog):
        """e: en Windows-utsjekking med core.autocrlf=true gir CRLF. Samme fil
        skal ikke avvises for det."""
        katalog.mkdir()
        sti = katalog / "0001_a.sql"
        sti.write_bytes(b"CREATE TABLE a (x INTEGER);\nCREATE TABLE b (y INTEGER);\n")
        migrer(base, katalog)
        sti.write_bytes(b"CREATE TABLE a (x INTEGER);\r\nCREATE TABLE b (y INTEGER);\r\n")

        assert migrer(base, katalog) == 1

    def test_versjonstabell_uten_sha256_avvises(self, base, katalog):
        """e: en base fra foer 1.5b oppgraderes ikke stille."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        base.execute(
            "CREATE TABLE skjema_versjon ("
            "versjon INTEGER PRIMARY KEY, fil TEXT NOT NULL, anvendt TEXT NOT NULL)"
        )
        base.execute("CREATE TABLE a (x INTEGER)")
        base.execute(
            "INSERT INTO skjema_versjon VALUES (1, '0001_a.sql', '2026-09-23T00:00:00+00:00')"
        )
        base.commit()

        with pytest.raises(MigrasjonsFeil, match="laget foer 1.5b"):
            migrer(base, katalog)


class TestTransaksjonskontrollIFila:
    """Story 1.5b, b: en COMMIT i fila ville avsluttet loeperens transaksjon,
    og resten av fila ville kjoert uten den."""

    def test_commit_midt_i_fila_avvises_foer_noe_kjoeres(self, base, katalog):
        skriv_migrasjon(
            katalog,
            1,
            "commit",
            "CREATE TABLE foer (x INTEGER);\nCOMMIT;\n"
            "CREATE TABLE etter (y INTEGER);\nDETTE ER IKKE SQL;",
        )

        with pytest.raises(MigrasjonsFeil, match="begynner med COMMIT"):
            migrer(base, katalog)

        assert alt_i_basen(base) == 0

    def test_commit_etter_en_kommentar_avvises(self, base, katalog):
        skriv_migrasjon(
            katalog,
            1,
            "kommentar",
            "CREATE TABLE foer (x INTEGER);\n-- en kommentar\n/* og en til */ COMMIT;\n"
            "CREATE TABLE etter (y INTEGER);",
        )

        with pytest.raises(MigrasjonsFeil, match="begynner med COMMIT"):
            migrer(base, katalog)

        assert alt_i_basen(base) == 0

    def test_commit_med_smaa_bokstaver_avvises(self, base, katalog):
        skriv_migrasjon(
            katalog,
            1,
            "smaa",
            "CREATE TABLE foer (x INTEGER);\ncommit;\nCREATE TABLE etter (y INTEGER);",
        )

        with pytest.raises(MigrasjonsFeil, match="begynner med commit"):
            migrer(base, katalog)

        assert alt_i_basen(base) == 0

    def test_trigger_med_begin_og_end_kjoeres(self, base, katalog):
        """Vokter mot en for streng retting: BEGIN og END midt i en setning
        er ikke transaksjonskontroll."""
        skriv_migrasjon(
            katalog,
            1,
            "trigger",
            "CREATE TABLE t (x INTEGER);\nCREATE TABLE logg (x INTEGER);\n"
            "CREATE TRIGGER t_logg AFTER INSERT ON t BEGIN\n"
            "    INSERT INTO logg VALUES (NEW.x);\nEND;",
        )

        assert migrer(base, katalog) == 1
        assert "t_logg" in tabeller(base)

    def test_ekstra_sikring_stopper_fila_naar_forhaandssjekken_ikke_gjoer_det(
        self, base, katalog, monkeypatch
    ):
        """Sjekken av in_transaction etter hver setning, fra storyen, proeves
        alene: forhaandssjekken byttes ut med en som slipper alt gjennom."""
        monkeypatch.setattr(migrering, "_forhaandssjekk", lambda setninger, sti: None)
        skriv_migrasjon(
            katalog,
            1,
            "commit",
            "CREATE TABLE foer (x INTEGER);\nCOMMIT;\nCREATE TABLE etter (y INTEGER);",
        )

        with pytest.raises(MigrasjonsFeil, match="avsluttet transaksjonen"):
            migrer(base, katalog)

        assert "etter" not in tabeller(base)
        assert versjon(base) == 0


class TestSamtidigMigrering:
    """Story 1.5b, f: hentekommandoen og webserveren kan migrere samtidig."""

    @staticmethod
    def krok(handling):
        """En tilkoblingsklasse som kjoerer handling() rett foer sin foerste
        BEGIN, altsaa i luken mellom lesing og transaksjon."""

        class Krok(sqlite3.Connection):
            utloest = False

            def execute(self, sql, *args):
                if not Krok.utloest and sql.lstrip().upper().startswith("BEGIN"):
                    Krok.utloest = True
                    handling()
                return super().execute(sql, *args)

        return Krok

    def test_en_annen_tilkobling_migrerer_i_luken(self, tmp_path, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        sti = tmp_path / "ose.db"

        def den_andre():
            b = sqlite3.connect(sti)
            try:
                migrer(b, katalog)
            finally:
                b.close()

        a = sqlite3.connect(sti, factory=self.krok(den_andre))
        try:
            assert migrer(a, katalog) == 1
        finally:
            a.close()

    def test_feilmeldingen_leser_versjonen_fra_basen(self, tmp_path, katalog):
        """Den andre kjoerer 0001 og feiler paa 0002 i luken. Basen staar da
        paa 1, og det er det meldingen skal si."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "feiler", "DETTE ER IKKE SQL;")
        sti = tmp_path / "ose.db"

        def den_andre():
            b = sqlite3.connect(sti)
            try:
                with pytest.raises(MigrasjonsFeil):
                    migrer(b, katalog)
            finally:
                b.close()

        a = sqlite3.connect(sti, factory=self.krok(den_andre))
        try:
            with pytest.raises(MigrasjonsFeil, match="0002_feiler.sql.*versjon 1"):
                migrer(a, katalog)
            assert versjon(a) == 1
        finally:
            a.close()


class TestKatalogkontrollen:
    """Story 1.5b, g: tre hull i kontrollen av katalogen."""

    def test_stor_filendelse_avvises_likt_paa_alle_plattformer(self, base, katalog):
        """glob('*.sql') hoppet stille over .SQL paa Linux og avviste den paa
        Windows. Naa avvises den med samme melding begge steder."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        (katalog / "0002_ny.SQL").write_text("CREATE TABLE b (y INTEGER);", encoding="utf-8")

        with pytest.raises(MigrasjonsFeil, match="filendelsen .SQL"):
            migrer(base, katalog)

        assert versjon(base) == 0

    def test_nummer_0000_avvises_med_egen_melding(self, base, katalog):
        skriv_migrasjon(katalog, 0, "null", "CREATE TABLE n (x INTEGER);")
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")

        with pytest.raises(MigrasjonsFeil, match="0000 er ikke et gyldig nummer"):
            migrer(base, katalog)

    def test_tom_katalog_avvises(self, base, katalog):
        katalog.mkdir()

        with pytest.raises(MigrasjonsFeil, match="Ingen migrasjoner"):
            migrer(base, katalog)

        assert alt_i_basen(base) == 0


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
