"""Boersdagene - story 1.6, punkt 3 i prd.md §8, AD-20.

Inneveerende boersdag er siste boersdag paa eller foer dagens dato i
Europe/Oslo. En boersdag er mandag-fredag som ikke staar paa lista over dager
Oslo Boers er stengt. Halve handelsdager er boersdager. Story 2.16: lista
regnes ut for hvert aar fra FOERSTE_AAR etter reglene Oslo Boers foelger, og
en dag funksjonen maa slaa opp foer FOERSTE_AAR, gir en feil i stedet for en
gjetning. Listene fra Euronext for 2026 og 2027 er tester regelen maa stemme
med (gruppens svar 07.11 kl. 11:05).

Datoene i testene er valgt fordi de er kantene: helg, paasken, jul og
nyttaar, og halvdagen foer paaske.
"""

import re
from datetime import date, datetime, timedelta, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import boersdag
from boersdag import (
    FOERSTE_AAR,
    UtenforKalenderen,
    er_boersdag,
    forrige_boersdag,
    innevaerende_boersdag,
    norsk_dato,
    paaskedag,
    stengte_dager,
)

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

    @pytest.mark.parametrize(
        ("dag", "forventet"),
        [
            (date(2026, 5, 1), date(2026, 4, 30)),
            (date(2026, 5, 14), date(2026, 5, 13)),
            (date(2026, 5, 25), date(2026, 5, 22)),
        ],
    )
    def test_1_mai_kristi_himmelfart_og_2_pinsedag_er_stengt(self, dag, forventet):
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

    @pytest.mark.parametrize("dag", [date(2025, 12, 15), date(2025, 1, 2)])
    def test_dag_foer_kalenderen_reiser(self, dag):
        with pytest.raises(UtenforKalenderen, match=dag.isoformat()):
            innevaerende_boersdag(dag)

    @pytest.mark.parametrize(
        ("dag", "forventet"),
        [
            (date(2027, 1, 1), date(2026, 12, 30)),
            (date(2027, 1, 4), date(2027, 1, 4)),
            (date(2027, 3, 29), date(2027, 3, 24)),
            (date(2028, 1, 1), date(2027, 12, 30)),
            (date(2028, 12, 26), date(2028, 12, 22)),
            (date(2041, 1, 1), date(2040, 12, 28)),
        ],
    )
    def test_aarene_etter_2026_er_med(self, dag, forventet):
        """Story 2.16. Ville feilet hvis kalenderen sluttet i 2026, som foer
        2.16: da reiste alle disse."""
        assert innevaerende_boersdag(dag) == forventet

    def test_feilmeldingen_sier_aaret_kalenderen_begynner_i(self):
        with pytest.raises(UtenforKalenderen, match=f"begynner i {FOERSTE_AAR}"):
            innevaerende_boersdag(date(2025, 12, 15))

    def test_utenfor_kalenderen_er_en_valueerror(self):
        """Kallere som fanger ValueError for ugyldige datoer, fanger ogsaa denne."""
        assert issubclass(UtenforKalenderen, ValueError)

    def test_tidspunkt_avvises_som_dag(self):
        """datetime er en underklasse av date, men baerer et klokkeslett i en
        sone. Dagen skal vaere regnet om foer den kommer hit (norsk_dato)."""
        with pytest.raises(TypeError):
            innevaerende_boersdag(datetime(2026, 9, 22, 12, tzinfo=timezone.utc))


class TestErBoersdag:
    """Story 1.7: samme liste som inneveerende_boersdag, ingen ny."""

    def test_vanlig_hverdag_er_boersdag(self):
        assert er_boersdag(date(2026, 9, 22)) is True

    @pytest.mark.parametrize("dag", [date(2026, 9, 26), date(2026, 9, 27)])
    def test_helg_er_ikke_boersdag(self, dag):
        assert er_boersdag(dag) is False

    @pytest.mark.parametrize("dag", sorted(stengte_dager(2026) | stengte_dager(2027)))
    def test_hver_stengte_dag_er_ikke_boersdag(self, dag):
        assert er_boersdag(dag) is False

    def test_halv_handelsdag_er_boersdag(self):
        assert er_boersdag(date(2026, 4, 1)) is True

    def test_1_januar_2026_reiser_ikke(self):
        """Dagen selv er i 2026. Ingen annen dag slaas opp, i motsetning til
        inneveerende_boersdag, som maa gaa til 2025-12-31."""
        assert er_boersdag(date(2026, 1, 1)) is False

    @pytest.mark.parametrize("dag", [date(2025, 12, 31), date(1999, 6, 1)])
    def test_dag_foer_kalenderen_reiser(self, dag):
        with pytest.raises(UtenforKalenderen, match=dag.isoformat()):
            er_boersdag(dag)

    def test_aaret_leses_fra_modulen(self, monkeypatch):
        """En test kan flytte FOERSTE_AAR, slik indeksdata og hentingen
        leser den. Ville feilet hvis grensen var skrevet fast i funksjonen."""
        monkeypatch.setattr(boersdag, "FOERSTE_AAR", 2027)
        with pytest.raises(UtenforKalenderen, match="begynner i 2027"):
            er_boersdag(date(2026, 9, 22))

    def test_tidspunkt_avvises_som_dag(self):
        with pytest.raises(TypeError, match="date"):
            er_boersdag(datetime(2026, 9, 22, 10, tzinfo=timezone.utc))

    def test_enig_med_innevaerende_boersdag_hver_dag_2026_til_2028(self):
        """Regelen staar to steder. En dag er boersdag hvis og bare hvis den er
        sin egen inneveerende boersdag. 1. januar 2026 hoppes over, fordi
        inneveerende_boersdag der maa slaa opp 2025. Story 2.16: hver dag i
        2027 og 2028 gir en boersdag uten feil."""
        dag = date(2026, 1, 2)
        while dag.year <= 2028:
            assert er_boersdag(dag) == (innevaerende_boersdag(dag) == dag), dag
            assert innevaerende_boersdag(dag) <= dag
            dag += timedelta(days=1)

    def test_forrige_boersdag_over_nyttaar_2027(self):
        assert forrige_boersdag(date(2027, 1, 4)) == date(2026, 12, 30)


# Gruppens svar 07.11 kl. 11:05 og 11:10: listene fra Euronext for 2026 og
# 2027, som de staar i docs/kilder-og-rettigheter.md, Handelskalenderen.
EURONEXT_2026 = {
    date(2026, 1, 1),
    date(2026, 4, 2),
    date(2026, 4, 3),
    date(2026, 4, 6),
    date(2026, 5, 1),
    date(2026, 5, 14),
    date(2026, 5, 25),
    date(2026, 12, 24),
    date(2026, 12, 25),
    date(2026, 12, 31),
}
EURONEXT_2027 = {
    date(2027, 1, 1),
    date(2027, 3, 25),
    date(2027, 3, 26),
    date(2027, 3, 29),
    date(2027, 5, 6),
    date(2027, 5, 17),
    date(2027, 12, 24),
    date(2027, 12, 31),
}


def _dokumentert(aar: int) -> set[date]:
    """Datoene i setningen «Stengt i ‹aar›» i seksjonen Handelskalenderen.
    Setningen kan brytes over flere linjer. Bare den setningen teller: neste
    nevner halvdagen, som er boersdag."""
    tekst = KILDER.read_text(encoding="utf-8")
    seksjon = tekst.split("## Handelskalenderen", 1)[1].split("\n## ", 1)[0]
    setning = " ".join(seksjon.split()).split(f"Stengt i {aar}", 1)[1].split(". ", 1)[0]
    return {date.fromisoformat(d) for d in re.findall(r"\d{4}-\d{2}-\d{2}", setning)}


class TestStengteDager:
    @pytest.mark.parametrize(("aar", "euronext"), [(2026, EURONEXT_2026), (2027, EURONEXT_2027)])
    def test_regelen_stemmer_med_euronext(self, aar, euronext):
        """Story 2.16, svaret kl. 11:05. Ville feilet hvis en regel manglet
        eller var feil, for eksempel 2. pinsedag regnet fra feil dag: da gir
        2026 eller 2027 en annen liste enn Euronext."""
        assert stengte_dager(aar) == euronext

    @pytest.mark.parametrize(("aar", "euronext"), [(2026, EURONEXT_2026), (2027, EURONEXT_2027)])
    def test_listene_staar_i_kilder_og_rettigheter(self, aar, euronext):
        """Listene i testen og i seksjonen Handelskalenderen skal ikke gli fra
        hverandre."""
        assert _dokumentert(aar) == euronext

    @pytest.mark.parametrize("dag", [date(2026, 4, 1), date(2027, 3, 24)])
    def test_halv_handelsdag_foer_paaske_er_boersdag(self, dag):
        """Onsdagen foer skjaertorsdag er halv handelsdag hos Euronext og
        regnes som boersdag (svaret kl. 11:10 for 2027)."""
        assert dag not in stengte_dager(dag.year)
        assert er_boersdag(dag) is True

    def test_bare_hverdager_i_aaret(self):
        """En helligdag paa en helg er ikke med: 2027 har 1. mai paa en
        loerdag og 1. og 2. juledag i helgen."""
        for aar in range(FOERSTE_AAR, FOERSTE_AAR + 50):
            assert all(dag.year == aar and dag.weekday() < 5 for dag in stengte_dager(aar)), aar
        assert date(2027, 5, 1) not in stengte_dager(2027)

    def test_grensen_gjelder_ogsaa_et_aar_som_er_regnet_ut(self, monkeypatch):
        """Gjennomgangen av 2.16 (BH7, ECH3). Ville feilet hvis cachen ga
        lista for 2026 etter at FOERSTE_AAR er flyttet til 2027."""
        stengte_dager(2026)
        monkeypatch.setattr(boersdag, "FOERSTE_AAR", 2027)
        with pytest.raises(UtenforKalenderen):
            stengte_dager(2026)

    def test_aar_foer_kalenderen_reiser(self):
        with pytest.raises(UtenforKalenderen, match=f"begynner i {FOERSTE_AAR}"):
            stengte_dager(FOERSTE_AAR - 1)


class TestPaaskedag:
    @pytest.mark.parametrize(
        "forventet",
        [
            date(2025, 4, 20),
            date(2026, 4, 5),
            date(2027, 3, 28),
            date(2028, 4, 16),
            date(2038, 4, 25),
            date(2285, 3, 22),
        ],
    )
    def test_kjente_paaskedager(self, forventet):
        """2038 har den seneste mulige paasken og 2285 den tidligste."""
        assert paaskedag(forventet.year) == forventet

    def test_alltid_en_soendag_mellom_22_mars_og_25_april(self):
        for aar in range(1900, 2400):
            dag = paaskedag(aar)
            assert dag.weekday() == 6, aar
            assert date(aar, 3, 22) <= dag <= date(aar, 4, 25), aar


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

    def test_sone_uten_forskyvning_avvises(self):
        """En tzinfo som svarer None paa utcoffset, ville astimezone lest som
        maskinens lokale tid. Da avhenger datoen av maskinen."""

        class UtenForskyvning(tzinfo):
            def utcoffset(self, dt):
                return None

            def dst(self, dt):
                return None

        with pytest.raises(ValueError, match="tidssone"):
            norsk_dato(datetime(2026, 9, 25, 0, 30, tzinfo=UtenForskyvning()))

    def test_dato_avvises_som_tidspunkt(self):
        with pytest.raises(TypeError):
            norsk_dato(date(2026, 9, 25))
