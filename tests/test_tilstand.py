"""De tre tilstandene skilles - story 1.7, FR-409, punkt 24 i prd.md §8.

tilstand tar imot det Vurderingslager.les gir, datoen og dagens dato i Oslo,
og gir en av fire verdier, aldri None. Om en dag var boersdag, avgjoeres av
boersdag.er_boersdag, med samme liste som 1.6.

Hver test lager sin egen base i minnet der lageret er med. Ingen nett (AD-8).
"""

import sqlite3
from datetime import date, datetime, timezone

import pytest

from boersdag import UtenforKalenderen
from lagring_sqlite import MIGRASJONSKATALOG, SqliteVurderingslager
from migrering import migrer
from tilstand import Art, Tilstand, tilstand
from vurderingsdata import Grunn, Vurdering

# Onsdag 30.09.2026. Alle datoene under er foer den, om ikke annet er sagt.
IDAG = date(2026, 9, 30)


def vurdering(**endret) -> Vurdering:
    felt = dict(styrke=2, retning="Positiv", trend=1, bevegelse=1, interesse=0,
                slutt=300.0, justert_slutt=290.0)
    felt.update(endret)
    return Vurdering(**felt)


STYRKE_0 = vurdering(styrke=0, retning="Ingen", trend=0, bevegelse=0, interesse=0)


class TestUtfallene:
    def test_rad_med_styrke_0_er_et_svar(self):
        """Et gyldig svar, ikke fravaer: sjekkene ga ingen utslag den dagen."""
        assert tilstand(STYRKE_0, date(2026, 9, 25), IDAG) == Tilstand(Art.SVAR, STYRKE_0)

    def test_rad_med_vurdering_er_et_svar(self):
        assert tilstand(vurdering(), date(2026, 9, 25), IDAG) == Tilstand(Art.SVAR, vurdering())

    @pytest.mark.parametrize("grunn", list(Grunn))
    def test_rad_med_grunn_er_en_rad_med_grunn(self, grunn):
        """Kommandoen kjoerte, men kunne ikke vurdere aksjen (punkt 24).
        Verken styrke 0 eller fravaer."""
        assert tilstand(grunn, date(2026, 9, 25), IDAG) == Tilstand(Art.GRUNN, grunn)

    def test_ingen_rad_paa_en_boersdag_er_ikke_kjoert(self):
        assert tilstand(None, date(2026, 9, 25), IDAG) == Tilstand(Art.IKKE_KJOERT)

    @pytest.mark.parametrize("dag", [
        date(2026, 9, 26), date(2026, 9, 27), date(2026, 4, 3), date(2026, 12, 24),
    ], ids=["loerdag", "soendag", "langfredag", "julaften"])
    def test_ingen_rad_paa_en_dag_som_ikke_er_boersdag(self, dag):
        # Nyttaarsaften som dagens dato, saa julaften ogsaa har vaert.
        assert tilstand(None, dag, date(2026, 12, 31)) == Tilstand(Art.IKKE_BOERSDAG)

    def test_halv_handelsdag_er_boersdag(self):
        assert tilstand(None, date(2026, 4, 1), IDAG) == Tilstand(Art.IKKE_KJOERT)

    def test_de_fire_er_fire_forskjellige_verdier_og_ingen_er_none(self):
        """Ville feilet hvis svaret var None baade for ikke kjoert og ikke
        boersdag: da er de umulige aa skille, og skillet kan ikke gjenskapes."""
        utfall = [
            tilstand(STYRKE_0, date(2026, 9, 25), IDAG),
            tilstand(Grunn.SYMBOL_FEILET, date(2026, 9, 25), IDAG),
            tilstand(None, date(2026, 9, 25), IDAG),
            tilstand(None, date(2026, 9, 26), IDAG),
        ]
        assert None not in utfall
        assert all(isinstance(u, Tilstand) for u in utfall)
        assert len({u.art for u in utfall}) == 4


class TestIDag:
    def test_i_dag_uten_rad_er_ikke_kjoert(self):
        """Ikke et endelig hull: raden kan skrives til neste boersdag begynner."""
        assert tilstand(None, IDAG, IDAG) == Tilstand(Art.IKKE_KJOERT)

    def test_loerdag_fredagen_uten_rad_er_ikke_kjoert(self):
        assert tilstand(None, date(2026, 9, 25), date(2026, 9, 26)) == Tilstand(Art.IKKE_KJOERT)

    def test_loerdag_er_selv_ikke_boersdag(self):
        """Grensen er dagens dato, ikke inneveerende boersdag. Med fredagen som
        grense ville loerdagen regnes som fremtid."""
        assert tilstand(None, date(2026, 9, 26), date(2026, 9, 26)) == Tilstand(Art.IKKE_BOERSDAG)

    def test_boersdag_foer_foerste_kjoering_er_ikke_kjoert(self):
        """Startdatoen lagres ikke. Den er datoen til foerste rad i tabellen."""
        assert tilstand(None, date(2026, 3, 2), IDAG) == Tilstand(Art.IKKE_KJOERT)


class TestFremtid:
    @pytest.mark.parametrize("dag", [date(2026, 10, 1), date(2026, 10, 3)],
                             ids=["torsdag", "loerdag"])
    def test_dato_etter_i_dag_reiser(self, dag):
        with pytest.raises(ValueError, match="etter"):
            tilstand(None, dag, IDAG)

    def test_loerdag_i_morgen_reiser(self):
        """En fredag er loerdagen i morgen fremtid, selv om den ikke er boersdag."""
        with pytest.raises(ValueError, match="etter"):
            tilstand(None, date(2026, 10, 3), date(2026, 10, 2))

    def test_rad_med_dato_etter_i_dag_reiser_ogsaa(self):
        with pytest.raises(ValueError, match="etter"):
            tilstand(vurdering(), date(2026, 10, 1), IDAG)


class TestKalenderen:
    def test_rad_gaar_foran_kalenderen(self):
        """Finnes raden, er utfallet raden, uten oppslag i kalenderen. En rad
        paa en dag lista kaller stengt, er et faktum om kjoeringen."""
        assert tilstand(vurdering(), date(2026, 4, 3), IDAG) == Tilstand(Art.SVAR, vurdering())

    @pytest.mark.parametrize("dag, idag", [
        (date(2025, 12, 31), IDAG),
        (date(2027, 1, 4), date(2027, 1, 5)),
    ], ids=["2025", "2027"])
    def test_ingen_rad_utenfor_lista_reiser(self, dag, idag):
        with pytest.raises(UtenforKalenderen):
            tilstand(None, dag, idag)


class TestTyper:
    @pytest.mark.parametrize("dato, idag", [
        (datetime(2026, 9, 25, 10, tzinfo=timezone.utc), IDAG),
        (date(2026, 9, 25), datetime(2026, 9, 30, 10, tzinfo=timezone.utc)),
    ], ids=["dato", "idag"])
    def test_tidspunkt_avvises(self, dato, idag):
        with pytest.raises(TypeError, match="date"):
            tilstand(None, dato, idag)

    def test_feil_innhold_avvises(self):
        with pytest.raises(TypeError, match="Vurdering, Grunn eller None"):
            tilstand("symbol_feilet", date(2026, 9, 25), IDAG)


class TestGjennomLageret:
    """Samme utfall naar innholdet kommer fra SqliteVurderingslager.les."""

    @pytest.fixture
    def tilkobling(self):
        tilkobling = sqlite3.connect(":memory:")
        migrer(tilkobling, MIGRASJONSKATALOG)
        yield tilkobling
        tilkobling.close()

    def test_fire_utfall_fra_en_base(self, tilkobling):
        fredag = date(2026, 9, 25)
        klokke = datetime(2026, 9, 25, 18, tzinfo=timezone.utc)
        lager = SqliteVurderingslager(tilkobling, lambda: klokke)
        lager.skriv("EQNR", fredag, STYRKE_0)
        lager.skriv("DNB", fredag, Grunn.KURS_IKKE_FRA_DAGEN)

        assert tilstand(lager.les("EQNR", fredag), fredag, IDAG) == Tilstand(Art.SVAR, STYRKE_0)
        assert tilstand(lager.les("DNB", fredag), fredag, IDAG) == Tilstand(
            Art.GRUNN, Grunn.KURS_IKKE_FRA_DAGEN
        )
        assert tilstand(lager.les("KOG", fredag), fredag, IDAG) == Tilstand(Art.IKKE_KJOERT)
        loerdag = date(2026, 9, 26)
        assert tilstand(lager.les("EQNR", loerdag), loerdag, IDAG) == Tilstand(Art.IKKE_BOERSDAG)
