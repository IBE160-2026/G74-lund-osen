"""Tester for Kursrad og Kurslager-porten - story 1.2, AD-19 og AD-3.

Kursrad er raden porten gir ut: norske feltnavn, og ingen av dem kan mangle.
Poenget er at en feilstavet noekkel blir en feil der dataene kommer inn, i
stedet for en None som forplanter seg inn i signalberegningen som et tall som
mangler.

Kurslager staar ved siden av Kurskilde til story 1.4. Det er et brudd paa AD-3
(en port per datasett) som varer til da, og TestKurskildeErPaaVeiUt holder det
fra aa vokse.
"""

import dataclasses
import inspect
import re
import typing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import kursdata
from kursdata import Kurslager, Kursrad, MinneKurslager

HENTET = datetime(2026, 9, 22, 8, 33, tzinfo=timezone.utc)


def rad(dato: str = "2026-09-21", slutt: float = 100.0, justert: float = 98.0,
        volum: int = 1000) -> Kursrad:
    return Kursrad(dato=date.fromisoformat(dato), slutt=slutt,
                   justert_slutt=justert, volum=volum)


class TestKursrad:
    def test_har_de_fire_norske_feltene(self):
        felter = [f.name for f in dataclasses.fields(Kursrad)]

        assert felter == ["dato", "slutt", "justert_slutt", "volum"]

    @pytest.mark.parametrize("mangler", ["dato", "slutt", "justert_slutt", "volum"])
    def test_avviser_aa_bli_konstruert_uten_et_felt(self, mangler):
        felt = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        del felt[mangler]

        with pytest.raises(TypeError):
            Kursrad(**felt)

    def test_feilstavet_noekkel_er_en_feil(self):
        """Det storyen finnes for. Med dict ville dette gitt None et sted senere."""
        with pytest.raises(TypeError):
            Kursrad(dato=date(2026, 9, 21), slutt=100.0, justert_slut=98.0, volum=1000)

    def test_eodhds_engelske_noekler_avvises(self):
        with pytest.raises(TypeError):
            Kursrad(date="2026-09-21", close=100.0, adjusted_close=98.0, volume=1000)

    @pytest.mark.parametrize("felt", ["slutt", "justert_slutt", "volum"])
    def test_none_avvises(self, felt):
        """Et felt som er der men tomt, er samme feil som et som mangler."""
        verdier = {"dato": date(2026, 9, 21), "slutt": 100.0, "justert_slutt": 98.0, "volum": 1000}
        verdier[felt] = None

        with pytest.raises(TypeError):
            Kursrad(**verdier)

    @pytest.mark.parametrize(
        "dato",
        ["2026-09-21", datetime(2026, 9, 21, 17, 30), None],
        ids=["tekst", "datetime", "None"],
    )
    def test_dato_maa_vaere_en_kalenderdato(self, dato):
        """AD-20: boersdagen er en kalenderdato. Tekst betyr at adapteren glemte
        aa oversette. datetime er en underklasse av date, men baerer et
        klokkeslett og kan gi feil dag - derfor avvises den eksplisitt."""
        with pytest.raises(TypeError):
            Kursrad(dato=dato, slutt=100.0, justert_slutt=98.0, volum=1000)

    def test_dato_er_date(self):
        assert rad("2026-09-21").dato == date(2026, 9, 21)

    def test_kan_ikke_endres_etter_konstruksjon(self):
        r = rad()

        with pytest.raises(dataclasses.FrozenInstanceError):
            r.slutt = 1.0


class TestKurslagerProtokollen:
    def test_har_erstatt_serie_serie_og_sist_hentet_og_ingenting_annet(self):
        metoder = {
            navn for navn, _ in inspect.getmembers(Kurslager, inspect.isfunction)
            if not navn.startswith("_")
        }

        assert metoder == {"erstatt_serie", "serie", "sist_hentet"}

    def test_har_ingen_legg_til_rad(self):
        """AD-5: serien skjoetes aldri paa."""
        assert not hasattr(Kurslager, "legg_til_rad")

    def test_serie_lover_kursrader_ikke_dict(self):
        """Ville feilet hvis porten returnerte list[dict] med EODHDs noekler."""
        retur = typing.get_type_hints(Kurslager.serie)["return"]

        assert retur == list[Kursrad]

    def test_erstatt_serie_tar_kursrader_og_hentetidspunkt(self):
        hint = typing.get_type_hints(Kurslager.erstatt_serie)

        assert hint["rader"] == list[Kursrad]
        assert hint["hentet"] is datetime
        assert list(inspect.signature(Kurslager.erstatt_serie).parameters) == [
            "self", "symbol", "rader", "hentet",
        ]

    def test_sist_hentet_lover_datetime_eller_none(self):
        assert typing.get_type_hints(Kurslager.sist_hentet)["return"] == datetime | None


class TestMinneKurslager:
    def test_oppfyller_protokollen(self):
        assert isinstance(MinneKurslager(), Kurslager)
        for navn in ("erstatt_serie", "serie", "sist_hentet"):
            assert (
                inspect.signature(getattr(MinneKurslager, navn))
                == inspect.signature(getattr(Kurslager, navn))
            )

    def test_serie_gir_kursrader(self):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad("2026-09-18"), rad("2026-09-21")], HENTET)

        serie = lager.serie("EQNR")

        assert [r.dato for r in serie] == [date(2026, 9, 18), date(2026, 9, 21)]
        assert all(isinstance(r, Kursrad) for r in serie)

    def test_ukjent_symbol_gir_tom_liste(self):
        assert MinneKurslager().serie("EQNR") == []

    def test_erstatt_serie_erstatter_ikke_skjoeter(self):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad("2026-09-17"), rad("2026-09-18")], HENTET)

        lager.erstatt_serie("EQNR", [rad("2026-09-21")], HENTET)

        assert [r.dato for r in lager.serie("EQNR")] == [date(2026, 9, 21)]

    def test_erstatt_serie_roerer_ikke_andre_symboler(self):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad("2026-09-18")], HENTET)
        lager.erstatt_serie("DNB", [rad("2026-09-18")], HENTET)

        lager.erstatt_serie("EQNR", [rad("2026-09-21")], HENTET)

        assert [r.dato for r in lager.serie("DNB")] == [date(2026, 9, 18)]

    def test_dict_med_eodhds_noekler_avvises(self):
        """Porten slipper ikke inn det gamle formatet bakveien."""
        lager = MinneKurslager()

        with pytest.raises(TypeError):
            lager.erstatt_serie("EQNR", [{"date": "2026-09-21", "close": 100.0,
                                          "adjusted_close": 98.0, "volume": 1000}], HENTET)

        assert lager.serie("EQNR") == []

    def test_lagret_serie_foelger_ikke_endringer_i_kallerens_liste(self):
        lager = MinneKurslager()
        rader = [rad("2026-09-18")]
        lager.erstatt_serie("EQNR", rader, HENTET)

        rader.append(rad("2026-09-21"))

        assert len(lager.serie("EQNR")) == 1

    def test_utlevert_serie_kan_ikke_endre_lageret(self):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad("2026-09-18")], HENTET)

        lager.serie("EQNR").append(rad("2026-09-21"))

        assert len(lager.serie("EQNR")) == 1


class TestSistHentet:
    """sist_hentet settes av erstatt_serie i samme kall, per symbol, i UTC."""

    def test_ukjent_symbol_har_ingen_tid(self):
        assert MinneKurslager().sist_hentet("EQNR") is None

    def test_settes_av_erstatt_serie(self):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad()], HENTET)

        assert lager.sist_hentet("EQNR") == HENTET

    def test_er_per_symbol(self):
        """AD-15: ett symbol kan feile og beholde sin gamle serie - og da ogsaa
        sin gamle tid. Et globalt tidsstempel ville sagt at DNB er fersk."""
        lager = MinneKurslager()
        lager.erstatt_serie("DNB", [rad()], HENTET)
        senere = HENTET + timedelta(days=1)

        lager.erstatt_serie("EQNR", [rad()], senere)

        assert lager.sist_hentet("EQNR") == senere
        assert lager.sist_hentet("DNB") == HENTET

    def test_leveres_i_utc(self):
        """AD-20: tidsstempler i UTC. Et tidspunkt med annen sone regnes om,
        ikke kastes - oeyeblikket er det samme."""
        lager = MinneKurslager()
        oslo = HENTET.astimezone(timezone(timedelta(hours=2)))

        lager.erstatt_serie("EQNR", [rad()], oslo)

        tid = lager.sist_hentet("EQNR")
        assert tid == HENTET
        assert tid.utcoffset() == timedelta(0)

    def test_tid_uten_sone_avvises_og_ingenting_endres(self):
        """Et naivt tidspunkt kan ikke plasseres. Avvises foer serien roeres,
        saa serie og tid aldri kommer fra hvert sitt oeyeblikk."""
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad("2026-09-18")], HENTET)

        with pytest.raises(ValueError):
            lager.erstatt_serie("EQNR", [rad("2026-09-21")], datetime(2026, 9, 23, 8, 0))

        assert [r.dato for r in lager.serie("EQNR")] == [date(2026, 9, 18)]
        assert lager.sist_hentet("EQNR") == HENTET

    def test_avvist_serie_endrer_ikke_tiden(self):
        lager = MinneKurslager()
        lager.erstatt_serie("EQNR", [rad()], HENTET)

        with pytest.raises(TypeError):
            lager.erstatt_serie("EQNR", [{"date": "2026-09-21"}], HENTET + timedelta(days=1))

        assert lager.sist_hentet("EQNR") == HENTET


class TestKurskildeErPaaVeiUt:
    """Kurskilde og Kurslager er to porter for samme datasett til story 1.4.
    Det bryter AD-3. Denne testen hindrer at bruddet vokser: bare modulene som
    brukte Kurskilde da 1.2 ble bygget, faar importere den. Fjernes i 1.4,
    sammen med Kurskilde."""

    TILLATT = {"markedsoversikt.py", "aksjedetalj.py"}

    def test_ingen_ny_modul_importerer_kurskilde(self):
        src = Path(kursdata.__file__).parent
        brukere = {
            sti.name
            for sti in src.glob("*.py")
            if sti.name != "kursdata.py"
            and re.search(r"^from kursdata import .*\bKurskilde\b",
                          sti.read_text(encoding="utf-8"), re.MULTILINE)
        }

        assert brukere <= self.TILLATT, (
            f"Ny bruker av Kurskilde: {brukere - self.TILLATT}. "
            "Skriv mot Kurslager - Kurskilde fjernes i story 1.4."
        )

    def test_kurskilde_sier_selv_at_den_er_paa_vei_ut(self):
        assert "1.4" in (kursdata.Kurskilde.__doc__ or "")
