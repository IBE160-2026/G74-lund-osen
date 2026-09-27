"""Boersdagene - story 1.6, punkt 3 i prd.md §8, AD-20.

Inneveerende boersdag er siste boersdag paa eller foer dagens dato i
Europe/Oslo. En boersdag er mandag-fredag som ikke staar paa lista over dager
Oslo Boers er stengt. Halve handelsdager er boersdager. Lista dekker 2026, og
en dag funksjonen maa slaa opp utenfor 2026, gir en feil i stedet for en
gjetning.

Datoene i testene er valgt fordi de er kantene: helg, paasken, jul og
nyttaar, og halvdagen foer paaske.
"""

import re
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from boersdag import STENGT, UtenforKalenderen, innevaerende_boersdag, norsk_dato

KILDER = Path(__file__).resolve().parent.parent / "docs" / "kilder-og-rettigheter.md"


class TestInnevaerendeBoersdag:
    def test_vanlig_hverdag_er_seg_selv(self):
        assert innevaerende_boersdag(date(2026, 9, 22)) == date(2026, 9, 22)

    @pytest.mark.parametrize("dag", [date(2026, 9, 26), date(2026, 9, 27)])
    def test_helg_gir_fredagen_foer(self, dag):
        assert innevaerende_boersdag(dag) == date(2026, 9, 25)

    @pytest.mark.parametrize(
        "dag",
        [date(2026, 4, 2), date(2026, 4, 3), date(2026, 4, 4), date(2026, 4, 5), date(2026, 4, 6)],
    )
    def test_2_paaskedag_gir_onsdagen_foer_over_hele_paasken(self, dag):
        """Skjaertorsdag, langfredag og 2. paaskedag er stengt, og helgen
        imellom. Onsdagen foer er siste boersdag."""
        assert innevaerende_boersdag(dag) == date(2026, 4, 1)

    def test_halv_handelsdag_er_boersdag(self):
        """2026-04-01 er halv dag paa Oslo Boers og regnes som boersdag."""
        assert innevaerende_boersdag(date(2026, 4, 1)) == date(2026, 4, 1)

    @pytest.mark.parametrize(
        ("dag", "forventet"),
        [
            (date(2026, 12, 24), date(2026, 12, 23)),
            (date(2026, 12, 25), date(2026, 12, 23)),
            (date(2026, 12, 26), date(2026, 12, 23)),
            (date(2026, 12, 31), date(2026, 12, 30)),
        ],
    )
    def test_julaften_juledag_og_nyttaarsaften_er_stengt(self, dag, forventet):
        assert innevaerende_boersdag(dag) == forventet

    def test_1_januar_2026_krever_2025_og_reiser(self):
        """Nyttaarsdag er stengt, og dagen foer ligger i 2025, som lista ikke
        dekker. Uten vakten ville funksjonen svart 2025-12-31 uten aa vite det."""
        with pytest.raises(UtenforKalenderen, match="2025-12-31"):
            innevaerende_boersdag(date(2026, 1, 1))

    def test_2_januar_2026_er_boersdag_og_reiser_ikke(self):
        """Vakten gjelder dagene funksjonen faktisk slaar opp, ikke alle
        datoer naer nyttaar."""
        assert innevaerende_boersdag(date(2026, 1, 2)) == date(2026, 1, 2)

    @pytest.mark.parametrize("dag", [date(2027, 1, 4), date(2025, 12, 15)])
    def test_dag_utenfor_2026_reiser(self, dag):
        with pytest.raises(UtenforKalenderen, match=dag.isoformat()):
            innevaerende_boersdag(dag)

    def test_utenfor_kalenderen_er_en_valueerror(self):
        """Kallere som fanger ValueError for ugyldige datoer, fanger ogsaa denne."""
        assert issubclass(UtenforKalenderen, ValueError)

    def test_tidspunkt_avvises_som_dag(self):
        """datetime er en underklasse av date, men baerer et klokkeslett i en
        sone. Dagen skal vaere regnet om foer den kommer hit (norsk_dato)."""
        with pytest.raises(TypeError):
            innevaerende_boersdag(datetime(2026, 9, 22, 12, tzinfo=timezone.utc))


class TestStengteDager:
    def test_lista_er_de_ti_datoene_i_kilder_og_rettigheter(self):
        """Lista i koden og lista i seksjonen Handelskalenderen skal ikke gli
        fra hverandre. Den ene er ført for haand fra den andre."""
        tekst = KILDER.read_text(encoding="utf-8")
        seksjon = tekst.split("## Handelskalenderen", 1)[1].split("\n## ", 1)[0]
        linje = next(l for l in seksjon.splitlines() if l.startswith("Stengt i 2026"))
        # Bare foerste setning. Neste setning paa samme linje nevner halvdagen
        # 2026-04-01, som er boersdag.
        linje = linje.split(". ", 1)[0]
        dokumentert = {date.fromisoformat(d) for d in re.findall(r"\d{4}-\d{2}-\d{2}", linje)}

        assert len(dokumentert) == 10
        assert STENGT == dokumentert

    def test_alle_stengte_dager_er_hverdager_i_2026(self):
        assert all(dag.year == 2026 and dag.weekday() < 5 for dag in STENGT)


class TestNorskDato:
    def test_00_30_i_sommertid_er_dagen_etter_utc(self):
        """00:30 fredag 25.09 i Oslo er 22:30 torsdag i UTC (CEST, +2)."""
        assert norsk_dato(datetime(2026, 9, 24, 22, 30, tzinfo=timezone.utc)) == date(2026, 9, 25)

    def test_00_30_i_vintertid_er_dagen_etter_utc(self):
        """00:30 fredag 11.12 i Oslo er 23:30 torsdag i UTC (CET, +1)."""
        assert norsk_dato(datetime(2026, 12, 10, 23, 30, tzinfo=timezone.utc)) == date(2026, 12, 11)

    def test_tidspunkt_i_oslo_gir_samme_dato(self):
        oslo = datetime(2026, 9, 25, 0, 30, tzinfo=ZoneInfo("Europe/Oslo"))
        assert norsk_dato(oslo) == date(2026, 9, 25)

    def test_tidspunkt_uten_sone_avvises(self):
        """Uten sone vet ingen hvilken dag det er i Oslo."""
        with pytest.raises(ValueError, match="tidssone"):
            norsk_dato(datetime(2026, 9, 25, 0, 30))

    def test_dato_avvises_som_tidspunkt(self):
        with pytest.raises(TypeError):
            norsk_dato(date(2026, 9, 25))
