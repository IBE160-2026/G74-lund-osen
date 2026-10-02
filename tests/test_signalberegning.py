"""Tester for signalberegningen - FR-701 til FR-705.

Kursseriene er laget for haand, med tall vi vet svaret paa. Ingen av testene
gjoer et API-kall, og ingen av dem leser data/. Det er hele poenget: en feil
i signalet gir ikke en krasj, den gir et tall som ser plausibelt ut, og da er
haandlagde serier eneste maaten aa se feilen paa.
"""

from datetime import date, timedelta
from statistics import median, stdev

import pytest

from kursdata import Kursrad
from signalberegning import (
    BLANDET,
    INGEN,
    NEGATIV,
    POSITIV,
    STANDARD,
    Parametre,
    Sjekk,
    _bevegelsesforklaring,
    _interesseforklaring,
    _trendforklaring,
    beregn_signal,
    bevegelse,
    finn_retning,
    finn_styrke,
    interesse,
    trend,
    vurder,
)
from vurderingsdata import Grunn, Vurdering

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


def serie(
    kurser: list[float],
    volumer: list[int] | None = None,
    slutt: list[float] | None = None,
) -> list[Kursrad]:
    """Kursrader slik Kursleser gir dem: kronologisk, nyeste sist.

    kurser er den justerte serien signalet skal regnes paa. slutt er den
    ujusterte, og er lik den justerte naar testen ikke sier noe annet.
    """
    if volumer is None:
        volumer = [NORMALT_VOLUM] * len(kurser)
    if slutt is None:
        slutt = kurser
    return [
        Kursrad(
            dato=date(2026, 9, 1) + timedelta(days=nummer),
            slutt=ujustert,
            justert_slutt=kurs,
            volum=volum,
        )
        for nummer, (kurs, ujustert, volum) in enumerate(zip(kurser, slutt, volumer))
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


class TestStyrke:
    """Story 1.8 (G5): styrken regnes av finn_styrke, som
    vurderingsdata.Vurdering er bundet til i test_vurderingslager.py."""

    def test_styrke_er_summen_av_absoluttverdiene(self):
        sjekker = (Sjekk("A", 1, ""), Sjekk("B", -1, ""), Sjekk("C", -1, ""))

        assert finn_styrke(sjekker) == 3

    @pytest.mark.parametrize("endring", [-0.03, -0.09, 0.09], ids=["blandet", "ned", "opp"])
    def test_beregn_signal_gir_styrken_finn_styrke_gir(self, endring):
        """Minst én av seriene har en negativ sjekk. Ellers overlever en
        beregn_signal som summerer uten abs."""
        kurser = stigende_kurser(endring)
        signal = beregn_signal(serie(kurser, med_stort_volum_siste_dag(len(kurser))), KORT)

        assert signal.styrke == finn_styrke(signal.sjekker)
        if endring < 0:
            assert any(sjekk.verdi < 0 for sjekk in signal.sjekker)


class TestJustertKurs:
    """FR-701, AD-19: signalet regnes paa justert_slutt, aldri paa slutt."""

    def test_signalet_foelger_justert_ikke_ujustert_kurs(self):
        """Justert serie stiger og hopper paa stort volum: styrke 3, positiv.

        Den ujusterte serien ligger flatt paa 100 hele veien. Regnet paa den,
        ville alle tre sjekkene gitt 0. Faar signalet 3, er det regnet paa
        den justerte.
        """
        kurser = stigende_kurser(0.09)
        volumer = med_stort_volum_siste_dag(len(kurser))
        flat = [100.0] * len(kurser)

        signal = beregn_signal(serie(kurser, volumer, slutt=flat), KORT)

        assert verdier(signal) == {"Trend": 1, "Bevegelse": 1, "Interesse": 1}
        assert signal.styrke == 3

    def test_utbyttedag_gir_ikke_kursfall(self):
        """Utbyttedagen: slutt faller 6 %, justert kurs staar stille.

        Regnet paa slutt, ville bevegelsen og trenden sett et fall. Regnet
        paa den justerte serien, er dagen rolig.
        """
        kurser = [100.0, 100.5, 99.8, 100.2, 99.9, 100.3, 100.1, 99.7, 100.4, 100.0]
        kurser += [100.2, 99.9, 100.1]
        slutt = [kurs * 1.06 for kurs in kurser[:-1]] + [kurser[-1]]

        signal = beregn_signal(serie(kurser, slutt=slutt), KORT)

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
        """Grensen hoerer til sonen: 2,0 % fra snittet er fortsatt 0.

        `kurser_med_avvik(0.02)` gir et avvik paa 0.019999999999999928, som
        ligger innenfor sonen baade med `<=` og `<`, og proever derfor ikke
        grensen. Her er seriene valgt saa snittet blir noeyaktig 100,0 og
        avviket noeyaktig 0,02: (102 - 100) / 100 == 0.02 i flyttall. Samme
        nedover, med 98 og 102 byttet.
        """
        opp = [100.0] * 8 + [98.0, 102.0]
        ned = [100.0] * 8 + [102.0, 98.0]
        assert sum(opp) / KORT.ma_vindu == 100.0
        assert (opp[-1] - 100.0) / 100.0 == 0.02
        assert sum(ned) / KORT.ma_vindu == 100.0
        assert (ned[-1] - 100.0) / 100.0 == -0.02

        assert trend(opp, KORT).verdi == 0, "noeyaktig +2 % skal ligge i sonen"
        assert trend(ned, KORT).verdi == 0, "noeyaktig -2 % skal ligge i sonen"

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


class TestForklaringenPaaNorsk:
    """Story 8.0, regel 21: forklaringen bruker tallformat, og en maaling som
    ville blitt lik grensen etter avrunding, faar flere desimaler."""

    NB = "\u00a0"

    def test_feilmeldingen_har_aa(self):
        """NFR-05: teksten vises i begge skjermbildene."""
        with pytest.raises(ValueError, match="for å regne signal"):
            beregn_signal(serie([100.0] * 5), KORT)

    def test_bevegelse_naer_grensen_skilles(self):
        """Ville feilet hvis «-1,2 % mot 1,2 % standardavvik» sto ved en
        sjekk som ga -1."""
        tekst = _bevegelsesforklaring(-0.01214, 0.01212)
        assert tekst == f"-1,214{self.NB}% mot 1,212{self.NB}% standardavvik"

    def test_bevegelse_langt_fra_grensen_har_en_desimal(self):
        tekst = _bevegelsesforklaring(0.034, 0.012)
        assert tekst == f"+3,4{self.NB}% mot 1,2{self.NB}% standardavvik"

    def test_trend_like_over_sonen_skilles(self):
        assert _trendforklaring(0.02004, STANDARD) == f"+2,004{self.NB}% mot MA50"

    def test_trend_paa_sonen_har_en_desimal(self):
        """Matrisen i spesifikasjonen: noeyaktig paa grensen er riktig likt."""
        assert _trendforklaring(0.02, STANDARD) == f"+2,0{self.NB}% mot MA50"
        assert _trendforklaring(-0.02, STANDARD) == f"-2,0{self.NB}% mot MA50"

    def test_interesse_viser_forholdstallet(self):
        """Story 2.1c: teksten er tallet regelen avgjorde med (FR-706), ikke
        de to volumene. Erstatter de tre testene fra 8.0 for den gamle
        teksten (beslutning 1)."""
        assert _interesseforklaring(4.95, STANDARD) == "volum 4,95 × medianen"

    def test_interesse_paa_volumfaktoren_har_to_desimaler(self):
        """Noeyaktig paa grensen er det riktig at tallene er like."""
        assert _interesseforklaring(1.5, STANDARD) == "volum 1,50 × medianen"

    def test_interesse_naer_volumfaktoren_skilles(self):
        """Ville feilet hvis «1,50 × medianen» sto ved en sjekk som ga +1.
        desimaler_mot_grense gir flere desimaler, ikke fast to."""
        assert _interesseforklaring(1.5004, STANDARD) == "volum 1,5004 × medianen"
        assert _interesseforklaring(1.4996, STANDARD) == "volum 1,4996 × medianen"

    def test_interesse_uten_median_viser_strek_og_grunnen(self):
        """NFR-08: aldri 0 og aldri et anslag. Vinduet kommer fra
        parametrene, ikke fra teksten."""
        assert _interesseforklaring(None, STANDARD) == (
            "–, medianvolumet de 20 dagene før er 0"
        )
        assert _interesseforklaring(None, KORT) == "–, medianvolumet de 5 dagene før er 0"

    def test_interesse_gjennom_beregn_signal(self):
        """Den ekte kallveien, ikke bare hjelperen: like volumer gir
        forholdstallet 1 med to desimaler og komma (regel 21)."""
        signal = beregn_signal(serie([100.0] * 60 + [104.0]))
        interesse = next(s for s in signal.sjekker if s.navn == "Interesse")
        assert interesse.forklaring == "volum 1,00 × medianen"

    def test_forklaringene_i_et_signal_har_ikke_punktum(self):
        kurser = [100.0] * 60 + [104.0]
        signal = beregn_signal(serie(kurser))
        for sjekk in signal.sjekker:
            assert "." not in sjekk.forklaring, sjekk.forklaring


def sjekk(signal, navn: str) -> Sjekk:
    return next(s for s in signal.sjekker if s.navn == navn)


def fortegn(tall: float) -> int:
    return (tall > 0) - (tall < 0)


class TestMaalingen:
    """Story 2.1c: hver sjekk baerer tallet den ble avgjort av, uavrundet og
    i regelens enhet (broek, forholdstall for interesse). Forventningene
    regnes her for haand fra seriene og sammenlignes med ==, saa en maaling i
    prosent eller avrundet ikke slipper gjennom."""

    def test_trend_maaler_avviket_som_broek(self):
        kurser = stigende_kurser(0.002)
        snitt = sum(kurser[-KORT.ma_vindu :]) / KORT.ma_vindu
        forventet = (kurser[-1] - snitt) / snitt

        resultat = trend(kurser, KORT)

        assert resultat.maaling == forventet
        assert resultat.grense is None
        assert 0.02 < resultat.maaling < 1, "broek, ikke prosent"

    def test_trend_noeyaktig_paa_grensen(self):
        """Matrisen: avvik noeyaktig 0,02 gir 0, og teksten +2,0 %. Snittet av
        de 50 er noeyaktig 100,0, som i TestNoytralsone."""
        kurser = [100.0] * 48 + [98.0, 102.0]
        resultat = trend(kurser, STANDARD)

        assert resultat.maaling == 0.02
        assert resultat.verdi == 0
        assert resultat.forklaring == "+2,0 % mot MA50"

    def test_bevegelse_maaler_dagens_endring_mot_standardavviket(self):
        kurser = stigende_kurser(0.0123)
        endringer = [(ny - gammel) / gammel for gammel, ny in zip(kurser, kurser[1:])]

        resultat = bevegelse(kurser, KORT)

        assert resultat.maaling == endringer[-1]
        assert resultat.grense == stdev(endringer[-(KORT.volatilitet_vindu + 1) : -1])
        assert resultat.maaling < 1 and resultat.grense < 1, "broek, ikke prosent"

    def test_interesse_maaler_forholdstallet(self):
        """1 000 mot medianen 3 000 er en tredjedel, med alle desimalene."""
        kurser = stigende_kurser(0.002)
        volumer = [3_000] * (len(kurser) - 1) + [1_000]

        resultat = interesse(kurser, volumer, KORT)

        assert resultat.maaling == 1_000 / 3_000
        assert resultat.grense is None
        assert resultat.verdi == 0

    def test_forholdstallet_avgjoer_interesse(self):
        kurser = stigende_kurser(0.002)
        volumer = [1_000] * (len(kurser) - 1) + [4_950]

        resultat = interesse(kurser, volumer, KORT)

        assert resultat.maaling == 4.95
        assert resultat.verdi == 1
        assert resultat.forklaring == "volum 4,95 × medianen"

    def test_forholdstall_noeyaktig_paa_volumfaktoren_gir_null(self):
        """Matrisen: 1,5 er ikke over 1,5. Ville feilet med >=."""
        kurser = stigende_kurser(0.002)
        volumer = [1_000] * (len(kurser) - 1) + [1_500]

        resultat = interesse(kurser, volumer, KORT)

        assert resultat.maaling == KORT.volumfaktor
        assert resultat.verdi == 0

    def test_medianvolum_null_gir_ingen_maaling(self):
        """Matrisen: medianen 0 gir None, aldri 0,0, interesse 0 og «–» med
        grunnen, ogsaa naar dagens volum er stort."""
        kurser = stigende_kurser(0.09)
        volumer = [0] * (len(kurser) - 1) + [5_000]
        assert median(volumer[-(KORT.volum_vindu + 1) : -1]) == 0

        resultat = interesse(kurser, volumer, KORT)

        assert resultat.maaling is None
        assert resultat.verdi == 0
        assert resultat.forklaring == "–, medianvolumet de 5 dagene før er 0"

    SERIER = {
        "styrke 1": (0.002, False),
        "styrke 3": (0.09, True),
        "blandet": (-0.03, True),
        "ned": (-0.09, True),
        "lik volumfaktor": (0.002, None),
    }

    @pytest.mark.parametrize("navn", list(SERIER))
    def test_regelen_paa_maalingene_gir_verdien_sjekken_ga(self, navn):
        """Kriteriet: regelen brukt paa maaling og grense gir samme verdi som
        sjekken, for alle tre. Maalingen er da det regelen saa."""
        endring, stort = self.SERIER[navn]
        kurser = stigende_kurser(endring)
        if stort is None:
            volumer = [1_000] * (len(kurser) - 1) + [1_500]
        else:
            volumer = med_stort_volum_siste_dag(len(kurser)) if stort else None
        signal = beregn_signal(serie(kurser, volumer), KORT)
        t, b, i = (sjekk(signal, n) for n in ("Trend", "Bevegelse", "Interesse"))

        assert t.verdi == (0 if abs(t.maaling) <= KORT.noytralsone else fortegn(t.maaling))
        assert b.verdi == (fortegn(b.maaling) if abs(b.maaling) > b.grense else 0)
        assert i.verdi == (
            fortegn(b.maaling)
            if i.maaling is not None and i.maaling > KORT.volumfaktor
            else 0
        )

    def test_sjekk_uten_maaling_kan_fortsatt_lages(self):
        """maaling og grense har standardverdi, saa Sjekk(navn, verdi,
        forklaring) virker som foer."""
        assert Sjekk("A", 1, "").maaling is None
        assert Sjekk("A", 1, "").grense is None


class TestVurder:
    """Story 2.5: vurder er den ene omformingen fra Signal til det som lagres."""

    def rader(self, siste_endring: float = 0.05, volumer=None) -> list[Kursrad]:
        kurser = stigende_kurser(siste_endring)
        if volumer is None:
            volumer = med_stort_volum_siste_dag(len(kurser))
        # Ujustert kurs ulik den justerte, saa slutt og justert_slutt ikke byttes.
        return serie(kurser, volumer, slutt=[kurs * 1.1 for kurs in kurser])

    def test_vurderingen_har_signalets_verdier_og_maalinger(self):
        """Ville feilet hvis standardavvik og dagens_endring var byttet om."""
        rader = self.rader()
        signal = beregn_signal(rader, KORT)
        trend_sjekk, bevegelse_sjekk, interesse_sjekk = signal.sjekker

        svar = vurder(rader, rader[-1].dato, KORT)

        assert svar == Vurdering(
            styrke=signal.styrke,
            retning=signal.retning,
            trend=trend_sjekk.verdi,
            bevegelse=bevegelse_sjekk.verdi,
            interesse=interesse_sjekk.verdi,
            slutt=rader[-1].slutt,
            justert_slutt=rader[-1].justert_slutt,
            trend_avvik=trend_sjekk.maaling,
            dagens_endring=bevegelse_sjekk.maaling,
            standardavvik=bevegelse_sjekk.grense,
            volumforhold=interesse_sjekk.maaling,
        )
        assert svar.styrke == 3
        assert svar.dagens_endring != svar.standardavvik

    def test_standardparametrene_brukes_uten_p(self):
        """Uten p er det de laaste parametrene som gjelder, og 13 dager er for
        kort for MA50."""
        rader = self.rader()
        assert vurder(rader, rader[-1].dato) == Grunn.SIGNAL_IKKE_REGNET

    def test_nyeste_kurs_ikke_fra_dagen(self):
        """Ville feilet hvis vurderingen ble regnet av gaarsdagens kurs."""
        rader = self.rader()
        assert vurder(rader, rader[-1].dato + timedelta(days=1), KORT) == (
            Grunn.KURS_IKKE_FRA_DAGEN
        )
        assert vurder(rader, rader[-2].dato, KORT) == Grunn.KURS_IKKE_FRA_DAGEN

    def test_tom_serie_er_ikke_fra_dagen(self):
        assert vurder([], date(2026, 9, 22), KORT) == Grunn.KURS_IKKE_FRA_DAGEN

    def test_for_kort_serie_gir_signal_ikke_regnet(self):
        rader = self.rader()[:5]
        assert vurder(rader, rader[-1].dato, KORT) == Grunn.SIGNAL_IKKE_REGNET

    def test_medianvolum_0_gir_vurdering_uten_volumforhold(self):
        """Forholdstallet mangler, interesse er 0, og porten godtar raden."""
        rader = self.rader(volumer=[0] * 13)

        svar = vurder(rader, rader[-1].dato, KORT)

        assert isinstance(svar, Vurdering)
        assert svar.volumforhold is None
        assert svar.interesse == 0

    def test_porten_som_avviser_gir_signal_ikke_regnet(self, monkeypatch):
        """Godtar ikke porten tallene, lagres grunnen, ikke et unntak."""
        import signalberegning

        def avvis(**_):
            raise ValueError("avvist i testen")

        monkeypatch.setattr(signalberegning, "Vurdering", avvis)
        rader = self.rader()
        assert vurder(rader, rader[-1].dato, KORT) == Grunn.SIGNAL_IKKE_REGNET
