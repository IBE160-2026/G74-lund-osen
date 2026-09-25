"""Tester for oversetteren og SnapshotLeser - story 1.4a, AD-15, AD-19, AD-20.

kursrad_fra_eodhd er det eneste stedet EODHDs feltnavn oversettes. Den fanger
ingenting selv: en rad som ikke kan oversettes, gir UgyldigKursrad, og et felt
som mangler, gir KeyError. SnapshotLeser fanger de to og behandler symbolet som
manglende: tom serie og sist_hentet None. De andre symbolene leses som vanlig.

Siden story 1.5 ligger oversetteren i eodhd.py og SnapshotLeser i lagring_fil.py.

Lesekontrakten SnapshotLeser deler med de to skrivbare lagrene, staar i
test_kurslager.py (fixturen leser).
"""

import json
from datetime import date, datetime, timedelta, timezone

import pytest

from eodhd import kursrad_fra_eodhd
from kursdata import Kursleser, Kurslager, Kursrad, UgyldigKursrad
from lagring_fil import SnapshotKilde, SnapshotLeser

HENTET = datetime(2026, 9, 23, 17, 4, 11, tzinfo=timezone.utc)


def raa(dato: str = "2026-09-21", close=100.0, adjusted_close=98.0, volume=1000) -> dict:
    return {"date": dato, "open": 99.0, "high": 101.0, "low": 97.0,
            "close": close, "adjusted_close": adjusted_close, "volume": volume}


def bilde(serier: dict, hentet=HENTET.isoformat()) -> SnapshotLeser:
    return SnapshotLeser(SnapshotKilde(hentet=hentet, serier=serier))


def er_manglende(leser: SnapshotLeser, symbol: str) -> bool:
    return leser.serie(symbol) == [] and leser.sist_hentet(symbol) is None


class TestOversetteren:
    def test_gyldig_rad(self):
        r = kursrad_fra_eodhd(raa("2026-09-21", 100.5, 98.25, 1234))

        assert r == Kursrad(dato=date(2026, 9, 21), slutt=100.5,
                            justert_slutt=98.25, volum=1234)
        assert type(r.dato) is date

    def test_close_gir_slutt_og_adjusted_close_gir_justert_slutt(self):
        """AD-19: beregningen bruker justert kurs, oversikten close. Byttes de,
        ser begge tallene riktige ut."""
        r = kursrad_fra_eodhd(raa(close=100.0, adjusted_close=80.0))

        assert r.slutt == 100.0
        assert r.justert_slutt == 80.0

    def test_mangler_adjusted_close_faller_ikke_tilbake_til_close(self):
        """Ville feilet hvis oversetteren falt tilbake fra adjusted_close til
        close - fallbacken AD-19 finnes for aa fjerne."""
        rad = raa()
        del rad["adjusted_close"]

        with pytest.raises(KeyError):
            kursrad_fra_eodhd(rad)

    @pytest.mark.parametrize("felt", ["date", "close", "adjusted_close", "volume"])
    def test_manglende_felt_gir_keyerror(self, felt):
        rad = raa()
        del rad[felt]

        with pytest.raises(KeyError):
            kursrad_fra_eodhd(rad)

    @pytest.mark.parametrize(
        ("felt", "verdi"),
        [
            ("close", float("nan")),
            ("adjusted_close", float("nan")),
            ("adjusted_close", float("inf")),
            ("close", None),
            ("adjusted_close", None),
            ("volume", None),
            ("close", "100.0"),
            ("volume", "1000"),
            ("close", 0),
            ("adjusted_close", -1.0),
            ("volume", -1),
            ("close", 10**400),
        ],
        ids=["close-nan", "justert-nan", "justert-inf", "close-none", "justert-none",
             "volum-none", "close-tekst", "volum-tekst", "close-null",
             "justert-negativ", "volum-negativt", "close-for-stort"],
    )
    def test_ugyldig_verdi_gir_ugyldig_kursrad(self, felt, verdi):
        with pytest.raises(UgyldigKursrad):
            kursrad_fra_eodhd(raa(**{felt: verdi}))

    @pytest.mark.parametrize(
        "dato",
        ["2026-9-1", "20260921", "2026-W39-1", "2026-09-31", 20260921, None,
         date(2026, 9, 21)],
        ids=["uten-nuller", "uten-streker", "ukedato", "umulig", "tall", "None",
             "date-objekt"],
    )
    def test_ugyldig_dato_gir_ugyldig_kursrad(self, dato):
        with pytest.raises(UgyldigKursrad):
            kursrad_fra_eodhd(raa(dato=dato))

    @pytest.mark.parametrize("rad", [[], ["2026-09-21", 100.0], 1, None],
                             ids=["tom-liste", "liste", "tall", "None"])
    def test_rad_som_ikke_er_et_objekt_gir_ugyldig_kursrad(self, rad):
        with pytest.raises(UgyldigKursrad):
            kursrad_fra_eodhd(rad)


class TestSnapshotLeser:
    def test_er_en_kursleser_men_ikke_en_kurslager(self):
        """Et oeyeblikksbilde skrives aldri om (FR-406, NFR-07)."""
        leser = bilde({})

        assert isinstance(leser, Kursleser)
        assert not isinstance(leser, Kurslager)
        assert not hasattr(leser, "erstatt_serie")

    def test_snapshotkilde_har_ingen_skrivemetode(self):
        assert not hasattr(SnapshotKilde, "erstatt_serie")

    def test_gyldig_serie_leses(self):
        leser = bilde({"EQNR": [raa("2026-09-18"), raa("2026-09-21")]})

        assert [r.dato for r in leser.serie("EQNR")] == [date(2026, 9, 18), date(2026, 9, 21)]
        assert leser.sist_hentet("EQNR") == HENTET

    def test_usortert_serie_sorteres_nyeste_sist(self):
        leser = bilde({"EQNR": [raa("2026-09-21"), raa("2026-09-17"), raa("2026-09-18")]})

        assert [r.dato for r in leser.serie("EQNR")] == [
            date(2026, 9, 17), date(2026, 9, 18), date(2026, 9, 21),
        ]

    def test_mangler_adjusted_close_gjoer_symbolet_manglende(self):
        uten = raa("2026-09-21")
        del uten["adjusted_close"]
        leser = bilde({"EQNR": [raa("2026-09-18"), uten]})

        assert er_manglende(leser, "EQNR")

    @pytest.mark.parametrize(
        "daarlig",
        [raa(close=float("nan")), raa(adjusted_close=None), raa(close="100"),
         raa(close=0), raa(volume=-1), raa(close=10**400)],
        ids=["nan", "None", "tekst", "null", "negativt-volum", "for-stort"],
    )
    def test_ugyldig_verdi_gjoer_symbolet_manglende(self, daarlig):
        leser = bilde({"EQNR": [raa("2026-09-18"), daarlig]})

        assert er_manglende(leser, "EQNR")

    @pytest.mark.parametrize("dato", ["2026-9-1", "20260921", "2026-W39-1", "2026-09-31", 20260921])
    def test_ugyldig_dato_gjoer_symbolet_manglende(self, dato):
        leser = bilde({"EQNR": [raa("2026-09-18"), raa(dato=dato)]})

        assert er_manglende(leser, "EQNR")

    @pytest.mark.parametrize("rad", [[], 1, None], ids=["liste", "tall", "None"])
    def test_rad_som_ikke_er_et_objekt_gjoer_symbolet_manglende(self, rad):
        leser = bilde({"EQNR": [raa("2026-09-18"), rad]})

        assert er_manglende(leser, "EQNR")

    def test_to_rader_med_samme_dato_gjoer_symbolet_manglende(self):
        """Hvilken av dem er riktig? Det kan ikke avgjoeres uten aa gjette."""
        leser = bilde({"EQNR": [raa("2026-09-21", close=100.0), raa("2026-09-21", close=101.0)]})

        assert er_manglende(leser, "EQNR")

    def test_tom_serie_er_manglende(self):
        assert er_manglende(bilde({"EQNR": []}), "EQNR")

    def test_ukjent_symbol_er_manglende(self):
        assert er_manglende(bilde({"DNB": [raa()]}), "EQNR")

    def test_ett_daarlig_symbol_roerer_ikke_de_andre(self):
        """AD-15: ett symbol som ikke kan leses, stopper ikke de andre."""
        leser = bilde({
            "EQNR": [raa("2026-09-21", adjusted_close=float("nan"))],
            "DNB": [raa("2026-09-18"), raa("2026-09-21")],
            "KOG": [raa("2026-09-21")],
        })

        assert er_manglende(leser, "EQNR")
        assert len(leser.serie("DNB")) == 2
        assert leser.sist_hentet("DNB") == HENTET
        assert len(leser.serie("KOG")) == 1
        assert leser.sist_hentet("KOG") == HENTET

    @pytest.mark.parametrize("verdi", [None, 1, "tekst", {}],
                             ids=["None", "tall", "tekst", "objekt"])
    def test_serie_som_ikke_er_en_liste_gjoer_bare_det_symbolet_manglende(self, verdi):
        """AD-15: ogsaa en serie av feil type stopper ikke de andre."""
        leser = bilde({"EQNR": verdi, "DNB": [raa("2026-09-18"), raa("2026-09-21")]})

        assert er_manglende(leser, "EQNR")
        assert len(leser.serie("DNB")) == 2
        assert leser.sist_hentet("DNB") == HENTET

    @pytest.mark.parametrize("serier", [[], None], ids=["liste", "None"])
    def test_serier_som_ikke_er_et_objekt_gjoer_hele_bildet_manglende(self, serier):
        leser = bilde(serier)

        assert er_manglende(leser, "EQNR")
        assert er_manglende(leser, "DNB")

    @pytest.mark.parametrize(
        "hentet",
        [None, "i gaar", "23.09.2026 17:04", "2026-09-23T17:04:11", 1758647051],
        ids=["None", "tekst", "norsk-format", "uten-tidssone", "tall"],
    )
    def test_hentet_som_ikke_kan_leses_gjoer_hele_bildet_manglende(self, hentet):
        """Beslutning 24.09, alternativ B: en serie har alltid en tid, ogsaa her."""
        leser = bilde({"EQNR": [raa()], "DNB": [raa()]}, hentet=hentet)

        assert er_manglende(leser, "EQNR")
        assert er_manglende(leser, "DNB")

    def test_hentet_som_mangler_i_fila_gjoer_hele_bildet_manglende(self, tmp_path):
        sti = tmp_path / "kurser-raa-2026-09-23.json"
        sti.write_text(json.dumps({"serier": {"EQNR": [raa()]}}), encoding="utf-8")

        leser = SnapshotLeser(SnapshotKilde.fra_fil(sti))

        assert er_manglende(leser, "EQNR")

    def test_hentet_med_annen_sone_leveres_i_utc(self):
        oslo = HENTET.astimezone(timezone(timedelta(hours=2))).isoformat()

        tid = bilde({"EQNR": [raa()]}, hentet=oslo).sist_hentet("EQNR")

        assert tid == HENTET
        assert tid.utcoffset() == timedelta(0)

    def test_hentet_slik_fetch_prices_skriver_den(self):
        """Formen i kurser-raa-2026-09-23.json: isoformat med mikrosekunder."""
        leser = bilde({"EQNR": [raa()]}, hentet="2026-09-23T17:04:11.296504+00:00")

        assert leser.sist_hentet("EQNR") == datetime(
            2026, 9, 23, 17, 4, 11, 296504, tzinfo=timezone.utc)

    def test_utlevert_serie_er_en_kopi(self):
        leser = bilde({"EQNR": [raa("2026-09-18")]})

        leser.serie("EQNR").clear()

        assert len(leser.serie("EQNR")) == 1

    def test_oversetter_ved_oppretting(self):
        """Endringer i kildens lister etterpaa naar ikke leseren."""
        serier = {"EQNR": [raa("2026-09-18")]}
        leser = bilde(serier)

        serier["EQNR"].append(raa("2026-09-21"))
        serier["DNB"] = [raa()]

        assert len(leser.serie("EQNR")) == 1
        assert er_manglende(leser, "DNB")
