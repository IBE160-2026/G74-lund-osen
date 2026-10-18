"""Story 8.16: regelen for startdagen i designregler.md §2 - FR-201, NFR-08.

Faste datoer rundt helger, helligdager og nyttaar. Stengte dager i 2026 fra
boersdag.STENGT: 01.01, 02.04, 03.04, 06.04, 01.05, 14.05, 25.05, 24.12,
25.12 og 31.12.
"""

from datetime import date

import pytest

from boersdag import er_boersdag
from perioder import (
    EN_MND,
    EN_UKE,
    ETT_AAR,
    I_AAR,
    PERIODENE,
    SEKS_MND,
    SISTE,
    TRE_MND,
    VELG,
    foerste_boersdag_fra,
    maaneder_tilbake,
    startdag,
)


class TestMaanederTilbake:
    @pytest.mark.parametrize(
        "dag, antall, ventet",
        [
            (date(2026, 3, 31), 1, date(2026, 2, 28)),  # februar har ikke 31
            (date(2026, 5, 31), 3, date(2026, 2, 28)),
            (date(2026, 8, 31), 6, date(2026, 2, 28)),
            (date(2026, 10, 9), 12, date(2025, 10, 9)),  # over nyttaar
            (date(2026, 1, 15), 1, date(2025, 12, 15)),
            (date(2028, 3, 31), 1, date(2028, 2, 29)),  # skuddaar
        ],
    )
    def test_samme_dato_eller_maanedens_siste_dag(self, dag, antall, ventet):
        """Ville feilet hvis en dato maaneden ikke har, ga en feil eller
        neste maaned i stedet for maanedens siste dag."""
        assert maaneder_tilbake(dag, antall) == ventet


class TestStartdagen:
    @pytest.mark.parametrize(
        "periode, siste, ventet",
        [
            # 1 uke: 7 dager bakover, og en helg eller paaske skyves fram.
            (EN_UKE, date(2026, 10, 9), date(2026, 10, 2)),
            (EN_UKE, date(2026, 10, 12), date(2026, 10, 5)),
            (EN_UKE, date(2026, 4, 9), date(2026, 4, 7)),  # 02.04, 03.04 og 06.04 stengt
            # 1 mnd: samme dato maaneden foer.
            (EN_MND, date(2026, 3, 10), date(2026, 2, 10)),
            (EN_MND, date(2026, 3, 31), date(2026, 3, 2)),  # 28.02 er loerdag
            (EN_MND, date(2026, 5, 4), date(2026, 4, 7)),  # 04.04 loerdag, 06.04 stengt
            (EN_MND, date(2026, 6, 1), date(2026, 5, 4)),  # 01.05 stengt, saa helg
            # 3 mnd og 6 mnd.
            (TRE_MND, date(2026, 4, 1), date(2026, 1, 2)),  # 01.01 stengt
            (SEKS_MND, date(2026, 10, 9), date(2026, 4, 9)),
            (SEKS_MND, date(2026, 8, 31), date(2026, 3, 2)),  # 28.02 loerdag
            # I aar: aarets foerste boersdag.
            (I_AAR, date(2026, 10, 9), date(2026, 1, 2)),
            (I_AAR, date(2026, 1, 2), date(2026, 1, 2)),
            # Siste boersdag og «Velg dag» viser 6 mnd fram til dagen.
            (SISTE, date(2026, 10, 9), date(2026, 4, 9)),
            (VELG, date(2026, 10, 1), date(2026, 4, 1)),  # halv handelsdag er boersdag
        ],
    )
    def test_faste_datoer(self, periode, siste, ventet):
        """Ville feilet hvis en periode regnet startdagen med en annen regel
        enn designregler.md §2, for eksempel 1 mnd som 30 dager (10.03 gir
        da 08.02, en soendag, og 09.02 i stedet for 10.02)."""
        assert startdag(periode, siste) == ventet

    @pytest.mark.parametrize("periode", [p for p in PERIODENE])
    def test_startdagen_er_en_boersdag(self, periode):
        """Ville feilet hvis en periode startet paa en helg eller en stengt dag."""
        for siste in (date(2026, 4, 9), date(2026, 6, 1), date(2026, 10, 9), date(2026, 12, 30)):
            dag = startdag(periode, siste)
            if dag.year == 2026:
                assert er_boersdag(dag), (periode, siste, dag)

    def test_siste_og_velg_bruker_regelen_for_6_mnd(self):
        """Gruppens svar 18.10 kl. 21:50. Ville feilet hvis to perioder som
        skal vise 6 mnd, regnet startdagen med hver sin regel."""
        for siste in (date(2026, 3, 31), date(2026, 8, 31), date(2026, 10, 9)):
            assert startdag(SISTE, siste) == startdag(VELG, siste) == startdag(SEKS_MND, siste)

    def test_1_aar_over_nyttaar_utenfor_kalenderen(self):
        """1 aar fra 09.10.2026 er 09.10.2025, et aar kalenderen ikke dekker.
        Da er startdagen foerste hverdag paa eller etter datoen."""
        assert startdag(ETT_AAR, date(2026, 10, 9)) == date(2025, 10, 9)
        assert startdag(ETT_AAR, date(2026, 10, 12)) == date(2025, 10, 13)  # 12.10.2025 er soendag

    def test_1_uke_over_nyttaar(self):
        """05.01.2026 minus 7 dager er 29.12.2025, utenfor kalenderen: en
        mandag, saa den er startdagen."""
        assert startdag(EN_UKE, date(2026, 1, 5)) == date(2025, 12, 29)

    def test_ukjent_periode_gir_valueerror(self):
        with pytest.raises(ValueError):
            startdag("2-aar", date(2026, 10, 9))


class TestFoersteBoersdag:
    def test_hopper_over_helg_og_helligdager(self):
        assert foerste_boersdag_fra(date(2026, 4, 2)) == date(2026, 4, 7)
        assert foerste_boersdag_fra(date(2026, 12, 24)) == date(2026, 12, 28)

    def test_en_boersdag_gis_tilbake(self):
        assert foerste_boersdag_fra(date(2026, 10, 9)) == date(2026, 10, 9)

    def test_utenfor_kalenderen_er_det_foerste_hverdag(self):
        assert foerste_boersdag_fra(date(2025, 10, 11)) == date(2025, 10, 13)
