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
import threading

import pytest

import migrering
from lagring_sqlite import MIGRASJONSKATALOG
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

        assert not base.in_transaction

    def test_endret_innhold_i_en_kjoert_fil_avvises(self, base, katalog):
        """e: samme filnavn, annet innhold."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        migrer(base, katalog)
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE helt_annet (z TEXT);")

        with pytest.raises(MigrasjonsFeil, match="0001_a.sql er endret"):
            migrer(base, katalog)

        assert not base.in_transaction

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

        assert not base.in_transaction


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
        assert not base.in_transaction

    @pytest.mark.parametrize(
        "ord_", ["BEGIN", "COMMIT", "END", "ROLLBACK", "SAVEPOINT s", "RELEASE s"]
    )
    def test_alle_seks_transaksjonsordene_avvises(self, base, katalog, ord_):
        """Lista staar her som tekst, ikke som migrering.TRANSAKSJONSORD, saa
        et ord som faller ut av settet, faar testen til aa feile."""
        skriv_migrasjon(
            katalog,
            1,
            "ord",
            f"CREATE TABLE foer (x INTEGER);\n{ord_};\nCREATE TABLE etter (y INTEGER);",
        )

        with pytest.raises(MigrasjonsFeil, match=f"begynner med {ord_.split()[0]}"):
            migrer(base, katalog)

        assert alt_i_basen(base) == 0
        assert not base.in_transaction

    def test_hele_katalogen_sjekkes_foer_noe_kjoeres(self, base, katalog):
        """En COMMIT i 0002 stopper ogsaa 0001, som selv er i orden."""
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "commit", "CREATE TABLE b (y INTEGER);\nCOMMIT;")

        with pytest.raises(MigrasjonsFeil, match="0002_commit.sql.*begynner med COMMIT"):
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
        assert not base.in_transaction

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
        assert not base.in_transaction

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

        with pytest.raises(MigrasjonsFeil, match="avsluttet transaksjonen.*halvveis migrert"):
            migrer(base, katalog)

        # Setningen foer COMMIT er alt committet og kan ikke rulles tilbake.
        # Det er derfor forhaandssjekken finnes, og meldingen sier det.
        assert "foer" in tabeller(base)
        assert "etter" not in tabeller(base)
        assert versjon(base) == 0


class TestSamtidigMigrering:
    """Story 1.5b, f: hentekommandoen og webserveren kan migrere samtidig.

    De to foerste testene dekker luken mellom lesingen og BEGIN: den andre
    tilkoblingen migrerer ferdig foer den foerste starter transaksjonen. To
    transaksjoner som overlapper, og dermed forskjellen paa BEGIN IMMEDIATE
    og en utsatt BEGIN, ble utsatt fra 1.5b (deferred-work.md) og proeves i
    TestToMigratorerOverlapper under (story 2.1b)."""

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
        paa 1, og det er det meldingen skal si: versjonen lest inne i
        transaksjonen, ikke regnet ut fra en lesing foer den."""
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


class TestToMigratorerOverlapper:
    """Story 2.1b, K8: to traader, hver med sin tilkobling til samme fil.

    Den foerste holder transaksjonen aapen inne i migrasjonen til den andre
    har startet sin. Overlappen tvinges med hendelser, ikke med tilfeldig
    timing: den foerste venter til den andre er rett foer sin BEGIN, og gir
    den deretter inntil ett sekund til aa komme inn i en transaksjon. Med
    BEGIN IMMEDIATE kommer den ikke inn foer den foerste har committet, og
    begge lykkes uansett hvor lang ventetiden er. Med en utsatt BEGIN (M11)
    kommer den andre inn med en gang, leser versjon 0 mens den foerste ennaa
    ikke har committet, og proever 0001 paa nytt, og da feiler den."""

    VENT = 10  # sekunder foer testen gir opp en hendelse som aldri kommer

    def test_begge_lykkes_og_0001_kjoeres_en_gang(self, tmp_path, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        sti = tmp_path / "ose.db"
        foerste_i_migrasjonen = threading.Event()
        andre_startet = threading.Event()
        andre_i_transaksjon = threading.Event()
        vent = self.VENT

        class Foerste(sqlite3.Connection):
            pauset = False

            def execute(self, sql, *args):
                svar = super().execute(sql, *args)
                if not Foerste.pauset and sql.lstrip().startswith("CREATE TABLE a"):
                    # Inne i migrasjonen, med transaksjonen aapen.
                    Foerste.pauset = True
                    assert self.in_transaction
                    foerste_i_migrasjonen.set()
                    assert andre_startet.wait(vent), "den andre startet aldri"
                    andre_i_transaksjon.wait(1.0)
                return svar

        class Andre(sqlite3.Connection):
            begynt = False

            def execute(self, sql, *args):
                if not Andre.begynt and sql.lstrip().upper().startswith("BEGIN"):
                    Andre.begynt = True
                    andre_startet.set()
                    return super().execute(sql, *args)
                svar = super().execute(sql, *args)
                if Andre.begynt:
                    andre_i_transaksjon.set()
                return svar

        utfall: dict[str, object] = {}

        def migrator(navn, fabrikk, foer=None):
            try:
                if foer is not None:
                    assert foer.wait(vent), f"{navn} fikk aldri startsignalet"
                tilkobling = sqlite3.connect(sti, timeout=vent, factory=fabrikk)
                try:
                    utfall[navn] = migrer(tilkobling, katalog)
                finally:
                    tilkobling.close()
            except BaseException as feil:  # noqa: BLE001 - rapporteres under
                utfall[navn] = feil

        traader = [
            threading.Thread(target=migrator, args=("foerste", Foerste)),
            threading.Thread(target=migrator, args=("andre", Andre, foerste_i_migrasjonen)),
        ]
        for traad in traader:
            traad.start()
        for traad in traader:
            traad.join(3 * vent)
            assert not traad.is_alive(), "en migrator ble aldri ferdig"

        assert andre_startet.is_set()
        assert utfall == {"foerste": 1, "andre": 1}
        kontroll = sqlite3.connect(sti)
        try:
            assert kontroll.execute(
                "SELECT versjon, fil FROM skjema_versjon"
            ).fetchall() == [(1, "0001_a.sql")]
        finally:
            kontroll.close()


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

        assert alt_i_basen(base) == 0

    def test_tom_katalog_avvises(self, base, katalog):
        katalog.mkdir()

        with pytest.raises(MigrasjonsFeil, match="Ingen migrasjoner"):
            migrer(base, katalog)

        assert alt_i_basen(base) == 0
        assert not base.in_transaction


class TestSisteVersjon:
    """Story 1.5b, c: siste_versjon gjoer samme katalogkontroll som migrer()."""

    def test_gir_antall_migrasjoner_og_endrer_ingenting(self, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 2, "b", "CREATE TABLE b (y INTEGER);")
        foer = sorted(p.name for p in katalog.iterdir())

        assert migrering.siste_versjon(katalog) == 2
        assert sorted(p.name for p in katalog.iterdir()) == foer

    def test_avviser_en_katalog_migrer_avviser(self, katalog):
        skriv_migrasjon(katalog, 1, "a", "CREATE TABLE a (x INTEGER);")
        skriv_migrasjon(katalog, 3, "c", "CREATE TABLE c (z INTEGER);")

        with pytest.raises(MigrasjonsFeil, match="0002 mangler"):
            migrering.siste_versjon(katalog)


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

    def test_modulen_har_bare_tre_offentlige_funksjoner(self):
        """Story 1.5b, c, la til siste_versjon, fordi adapteren maa vite
        hvilken versjon katalogen gir uten aa gjenta katalogkontrollen eller
        kalle en privat funksjon. Den leser bare, og er ingen unntaksvei:
        den kan verken kjoere, hoppe over eller endre en migrasjon."""
        funksjoner = {
            navn
            for navn, obj in inspect.getmembers(migrering, inspect.isfunction)
            if obj.__module__ == "migrering" and not navn.startswith("_")
        }

        assert funksjoner == {"migrer", "siste_versjon", "versjon"}

    def test_migrer_tar_bare_tilkobling_og_katalog(self):
        assert list(inspect.signature(migrer).parameters) == ["tilkobling", "katalog"]


# Story 2.1c: 0004 legger maalingene til vurdering. Testene under leser de
# ekte migrasjonsfilene, men kopierer dem til tmp_path og skriver aldri i
# src/migrasjoner/.

FILENE_TIL_0003 = ("0001_kurs.sql", "0002_vurdering.sql", "0003_aksje.sql")
MAALINGENE = ("trend_avvik", "dagens_endring", "standardavvik", "volumforhold")

# Teksten i en CHECK-feil har varierert mellom SQLite-versjoner: uttrykket,
# kolonnen eller tabellen. Alle tre er godtatt, som i test_aksje.py. Uten
# hjelpetabellen ville ADD COLUMN feilet med en annen CHECK, og da ville
# meldingen ikke nevnt kontroll_0004.
KONTROLLFEIL_0004 = (
    r"0004_maalinger\.sql.*CHECK constraint failed.*(vurderinger_uten_grunn|kontroll_0004)"
)

VURDERING_UTEN_GRUNN = (
    "INSERT INTO vurdering (symbol, dato, styrke, retning, trend, bevegelse, "
    "interesse, slutt, justert_slutt) "
    "VALUES ('EQNR', '2026-09-23', 1, 'Positiv', 1, 0, 0, 300.0, 290.0)"
)
VURDERING_MED_GRUNN = (
    "INSERT INTO vurdering (symbol, dato, grunn) VALUES ('DNB', '2026-09-23', 'symbol_feilet')"
)


def base_paa_versjon_3(tmp_path) -> sqlite3.Connection:
    """En base migrert med 0001-0003, slik basen saa ut foer 2.1c."""
    til_0003 = tmp_path / "til_0003"
    til_0003.mkdir()
    for navn in FILENE_TIL_0003:
        (til_0003 / navn).write_bytes((MIGRASJONSKATALOG / navn).read_bytes())
    tilkobling = sqlite3.connect(tmp_path / "v3.db")
    assert migrer(tilkobling, til_0003) == 3
    return tilkobling


def kolonner(tilkobling, tabell: str) -> list[str]:
    return [rad[1] for rad in tilkobling.execute(f"PRAGMA table_info({tabell})")]


class TestMaalingene0004:
    def test_filen_bygger_ikke_om_vurdering(self):
        tekst = (MIGRASJONSKATALOG / "0004_maalinger.sql").read_text(encoding="utf-8")
        assert "DROP TABLE vurdering" not in tekst
        assert tekst.count("ALTER TABLE vurdering ADD COLUMN") == 4
        assert "DROP TABLE kontroll_0004" in tekst

    def test_rad_med_grunn_blir_staaende_uten_maalinger(self, tmp_path):
        """Matrisen: en rad med grunn i versjon 3 staar, og de fire
        kolonnene er NULL."""
        tilkobling = base_paa_versjon_3(tmp_path)
        try:
            tilkobling.execute(VURDERING_MED_GRUNN)
            tilkobling.commit()
            foer = tilkobling.execute("SELECT * FROM vurdering").fetchall()

            assert migrer(tilkobling, MIGRASJONSKATALOG) == 4

            assert kolonner(tilkobling, "vurdering")[-4:] == list(MAALINGENE)
            assert tilkobling.execute(
                "SELECT symbol, dato, grunn, " + ", ".join(MAALINGENE) + " FROM vurdering"
            ).fetchall() == [("DNB", "2026-09-23", "symbol_feilet", None, None, None, None)]
            assert tilkobling.execute(
                "SELECT * FROM vurdering"
            ).fetchall() == [rad + (None,) * 4 for rad in foer]
            assert "kontroll_0004" not in tabeller(tilkobling)
        finally:
            tilkobling.close()

    def test_vurdering_uten_grunn_stopper_migrasjonen(self, tmp_path):
        """Kriteriet: 0004 stopper med kontroll_0004 i feilen, rulles
        tilbake, og basen staar paa versjon 3 med radene uroert."""
        tilkobling = base_paa_versjon_3(tmp_path)
        try:
            tilkobling.execute(VURDERING_UTEN_GRUNN)
            tilkobling.execute(VURDERING_MED_GRUNN)
            tilkobling.commit()
            foer = tilkobling.execute("SELECT * FROM vurdering ORDER BY symbol").fetchall()
            kolonner_foer = kolonner(tilkobling, "vurdering")

            with pytest.raises(MigrasjonsFeil, match=KONTROLLFEIL_0004):
                migrer(tilkobling, MIGRASJONSKATALOG)

            assert versjon(tilkobling) == 3
            assert tilkobling.execute(
                "SELECT * FROM vurdering ORDER BY symbol"
            ).fetchall() == foer
            assert kolonner(tilkobling, "vurdering") == kolonner_foer
            assert "kontroll_0004" not in tabeller(tilkobling)
        finally:
            tilkobling.close()

    def test_triggerne_fra_0002_og_0003_virker_etter_0004(self, tmp_path):
        """Kriteriet: en rad for ukjent aksje eller med ukjent grunn avvises
        fortsatt, paa en ny tilkobling uten noe slaatt paa."""
        tilkobling = base_paa_versjon_3(tmp_path)
        try:
            assert migrer(tilkobling, MIGRASJONSKATALOG) == 4
        finally:
            tilkobling.close()
        ny = sqlite3.connect(tmp_path / "v3.db")
        try:
            gyldig = (
                "INSERT INTO vurdering (symbol, dato, styrke, retning, trend, bevegelse, "
                "interesse, slutt, justert_slutt, trend_avvik, dagens_endring, "
                "standardavvik, volumforhold) "
                "VALUES (?, '2026-09-23', 1, 'Positiv', 1, 0, 0, 300.0, 290.0, "
                "0.035, 0.001, 0.012, 1.2)"
            )
            with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje"):
                ny.execute(gyldig, ("EQNR.OL",))
            with pytest.raises(sqlite3.IntegrityError, match="ukjent grunn"):
                ny.execute(
                    "INSERT INTO vurdering (symbol, dato, grunn) "
                    "VALUES ('EQNR', '2026-09-23', 'noe_annet')"
                )
            ny.execute(gyldig, ("EQNR",))
            assert ny.execute("SELECT count(*) FROM vurdering").fetchone() == (1,)
        finally:
            ny.close()
