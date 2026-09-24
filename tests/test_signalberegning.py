"""Tester for signalberegningen - FR-701 til FR-705.

Kursseriene er laget for haand, med tall vi vet svaret paa. Ingen av testene
gjoer et API-kall, og ingen av dem leser data/. Det er hele poenget: en feil
i signalet gir ikke en krasj, den gir et tall som ser plausibelt ut, og da er
haandlagde serier eneste maaten aa se feilen paa.
"""

from datetime import date, timedelta

import pytest

from signalberegning import (
    BLANDET,
    INGEN,
    NEGATIV,
    POSITIV,
    Parametre,
    Sjekk,
    beregn_signal,
    finn_retning,
    trend,
)

# Korte vinduer, slik at hele serien faar plass paa skjermen og kan
# kontrolleres for haand. Logikken er den samme som med MA50.
KORT = Parametre(ma_vindu=10, volatilitet_vindu=5, volum_vindu=5)

NORMALT_VOLUM = 1_000
STORT_VOLUM = 5_000

# Ujevn stigning med vilje. En serie som stiger like mye hver dag har
# standardavvik 0, og da slaar bevegelsessjekken ut paa den minste
# bevegelse. Ekte kursserier ser ikke slik ut, og en test som bruker en
# slik serie tester noe annet enn den tror.
STIGNING = [1.015, 1.025, 1.018, 1.022]


def stigende_kurser(siste_endring: float) -> list[float]:
    """Tolv dager som stiger ujevnt, og en trettende dag vi bestemmer selv.

    Etter tolv dager ligger kursen godt over MA10, saa trendsjekken gir +1.
    Hva de to andre sjekkene gir, avgjoeres av `siste_endring` og volumet.
    """
    kurser = [100.0]
    for nummer in range(11):
        kurser.append(round(kurser[-1] * STIGNING[nummer % len(STIGNING)], 2))
    kurser.append(round(kurser[-1] * (1 + siste_endring), 2))
    return kurser


def serie(kurser: list[float], volumer: list[float] | None = None) -> list[dict]:
    """Bygger raader slik EODHD leverer dem: kronologisk, nyeste sist."""
    if volumer is None:
        volumer = [NORMALT_VOLUM] * len(kurser)
    return [
        {
            "date": (date(2026, 9, 1) + timedelta(days=nummer)).isoformat(),
            "close": kurs,
            "adjusted_close": kurs,
            "volume": volum,
        }
        for nummer, (kurs, volum) in enumerate(zip(kurser, volumer))
    ]


def med_stort_volum_siste_dag(antall_dager: int) -> list[float]:
    return [NORMALT_VOLUM] * (antall_dager - 1) + [STORT_VOLUM]


def verdier(signal) -> dict[str, int]:
    return {sjekk.navn: sjekk.verdi for sjekk in signal.sjekker}


class TestSignalstyrke:
    def test_kurs_over_snittet_alene_gir_styrke_1(self):
        """Trend slaar ut, de to andre tier: styrke 1, retning positiv.

        Siste dag stiger 0,2 % - godt innenfor det serien ellers beveger seg
        - og volumet er som alle andre dager.
        """
        kurser = stigende_kurser(0.002)

        signal = beregn_signal(serie(kurser), KORT)

        assert verdier(signal) == {"Trend": 1, "Bevegelse": 0, "Interesse": 0}
        assert signal.styrke == 1
        assert signal.retning == POSITIV

    def test_alle_tre_sjekkene_slaar_ut(self):
        """Stigende serie, kraftig hopp paa stort volum: styrke 3, positiv."""
        kurser = stigende_kurser(0.09)
        volumer = med_stort_volum_siste_dag(len(kurser))

        signal = beregn_signal(serie(kurser, volumer), KORT)

        assert verdier(signal) == {"Trend": 1, "Bevegelse": 1, "Interesse": 1}
        assert signal.styrke == 3
        assert signal.retning == POSITIV

    def test_sjekkene_spriker_gir_blandet(self):
        """Kursfall paa hoeyt volum i en aksje som fortsatt ligger over snittet.

        Dette er tilfellet PRD-en bruker som eksempel paa at blandet er et
        gyldig svar, ikke en feiltilstand: trend peker opp mens dagen peker
        ned. Styrken er 3 selv om retningene opphever hverandre - styrke
        maaler hvor kraftig sjekkene slaar ut, ikke hvor enige de er.
        """
        kurser = stigende_kurser(-0.03)
        volumer = med_stort_volum_siste_dag(len(kurser))

        signal = beregn_signal(serie(kurser, volumer), KORT)

        assert verdier(signal) == {"Trend": 1, "Bevegelse": -1, "Interesse": -1}
        assert signal.styrke == 3
        assert signal.retning == BLANDET

    def test_flat_serie_gir_styrke_0_og_ingen_retning(self):
        """Signalstyrke 0 er et gyldig svar, ikke mangel paa data (FR-702)."""
        kurser = [100.0, 100.5, 99.8, 100.2, 99.9, 100.3, 100.1, 99.7, 100.4, 100.0]
        kurser += [100.2, 99.9, 100.1]

        signal = beregn_signal(serie(kurser), KORT)

        assert signal.styrke == 0
        assert signal.retning == INGEN


class TestNoytralsone:
    """FR-702. Uten sonen kan styrke 0 ikke forekomme, og 64 % av
    aksjedagene havner paa styrke 1. Dette er kravet som stille forsvinner
    ved en omskriving, saa det har sin egen test."""

    @staticmethod
    def kurser_med_avvik(avvik: float) -> list[float]:
        """Ni dager paa 100, saa en dag som ligger `avvik` over snittet.

        Snittet over de ti siste inkluderer dagens kurs, saa dagens kurs maa
        loeses ut av likningen (k - snitt) / snitt = a, der snitt er
        (900 + k) / 10. Det gir k = 900 * (1 + a) / (9 - a).
        """
        siste = 900.0 * (1 + avvik) / (9 - avvik)
        return [100.0] * 9 + [siste]

    def test_en_prosent_over_snittet_gir_null(self):
        assert trend(self.kurser_med_avvik(0.01), KORT).verdi == 0

    def test_noeyaktig_paa_grensen_gir_null(self):
        """Grensen hoerer til sonen: 2,0 % over snittet er fortsatt 0."""
        assert trend(self.kurser_med_avvik(0.02), KORT).verdi == 0

    def test_utenfor_sonen_gir_utslag(self):
        assert trend(self.kurser_med_avvik(0.03), KORT).verdi == 1
        assert trend(self.kurser_med_avvik(-0.03), KORT).verdi == -1


class TestRetning:
    def test_alle_utslag_opp_er_positiv(self):
        assert finn_retning((Sjekk("A", 1, ""), Sjekk("B", 1, ""))) == POSITIV

    def test_alle_utslag_ned_er_negativ(self):
        assert finn_retning((Sjekk("A", -1, ""), Sjekk("B", 0, ""))) == NEGATIV

    def test_sprikende_utslag_er_blandet(self):
        assert finn_retning((Sjekk("A", 1, ""), Sjekk("B", -1, ""))) == BLANDET

    def test_ingen_utslag_er_ingen(self):
        assert finn_retning((Sjekk("A", 0, ""), Sjekk("B", 0, ""))) == INGEN


class TestTerskel:
    """FR-705. Terskelen styrer visning og sortering, ikke hentingen."""

    def test_styrke_under_terskel_skiller_seg_ikke_ut(self):
        signal = beregn_signal(serie(stigende_kurser(0.002)), KORT)

        assert signal.styrke == 1
        assert signal.skiller_seg_ut is False

    def test_styrke_paa_terskelen_skiller_seg_ut(self):
        kurser = stigende_kurser(0.09)

        signal = beregn_signal(serie(kurser), KORT)

        assert signal.styrke == 2
        assert signal.skiller_seg_ut is True


class TestForKorteSerier:
    def test_for_faa_dager_gir_feil_ikke_et_tall(self):
        """Et plausibelt tall fra for lite data er verre enn en feilmelding."""
        with pytest.raises(ValueError, match="Trenger"):
            beregn_signal(serie([100.0] * 5), KORT)

    def test_standardparametrene_krever_51_dager(self):
        """MA50 spiser 50 dager. Med 51 gaar det saa vidt."""
        with pytest.raises(ValueError):
            beregn_signal(serie([100.0] * 50))

        signal = beregn_signal(serie([100.0] * 51))
        assert signal.styrke == 0
