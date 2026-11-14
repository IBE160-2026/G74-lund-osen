"""Signalet regnet i ettertid - story 2.17, FR-408, FR-409, AD-7.

Gruppens svar 2026-11-14 kl. 05:41-05:49 (raadet anbefalte det): til slutt i
hver henting, etter kveldens vurderinger og KI-tekster, regnes signalet for
hver boersdag med kurser i basen, for aksjene i lista, naar dagen mangler rad
i vurdering og aksjen har nok kurser etter kveldens regel. Signalet regnes
bare med kursene til og med dagen, med vurder() fra kvelden, saa raden er den
kvelden ville skrevet med kursene som staar i basen.

- Aldri inneveerende boersdag: den er kveldens, og raden kan skrives helt
  til neste boersdag begynner (AD-7).
- En kveldsrad, ogsaa en rad med grunn, overskrives aldri. En dag med en
  rad i ettertid fra foer, regnes ikke paa nytt her. Det gjoer bare
  kommandoen som regner dem paa nytt (fetch_prices.py --regn-ettertid-paa-nytt).
- Nok kurser er kveldens regel: like mange kursdager som signalet trenger
  (nodvendige_dager, MINST_HANDELSDAGER i hentingen). En dag med faerre faar
  ingen rad, og en dag der signalet ikke kan regnes, heller ikke: en rad i
  ettertid har alltid en vurdering, aldri en grunn.
- En dag foer boerskalenderen (FOERSTE_AAR) faar ingen rad, fordi
  kalenderen ikke kan si om den var boersdag (story 2.16).
- Ingen KI-tekst for dem. KI-grunnlaget leser bare kveldsradene
  (vurderingsdata.kveldsradene).

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: serien, datoene som
har rad og inneveerende boersdag kommer inn som argumenter. fyll_i_ettertid
tar portene og gjoer det samme for en hel liste. Hentingen og demokommandoen
bruker samme funksjon.
"""

from collections.abc import Collection, Iterable
from dataclasses import dataclass, replace
from datetime import date
from typing import Protocol

from boersdag import dekker, er_boersdag
from kursdata import Aksje, Kursrad
from signalberegning import nodvendige_dager, vurder
from vurderingsdata import Vurdering


def regn_i_ettertid(serie: list[Kursrad], har_rad: Collection[date], dagens: date) -> list[tuple[date, Vurdering]]:
    """Radene i ettertid for en aksje, eldste foerst.

    serie er kursene i basen, kronologisk med nyeste sist, slik
    Kursleser.serie gir dem. har_rad er datoene som alt har en rad i
    vurdering, kveldsrad eller rad i ettertid. dagens er inneveerende
    boersdag. Hver rad er det vurder() gir med kursene til og med dagen, med
    ettertid satt.
    """
    nodvendig = nodvendige_dager()
    radene: list[tuple[date, Vurdering]] = []
    for nummer, kurs in enumerate(serie, start=1):
        dag = kurs.dato
        if dag >= dagens or dag in har_rad or nummer < nodvendig:
            continue
        if not dekker(dag.year) or not er_boersdag(dag):
            continue
        innhold = vurder(serie[:nummer], dag)
        if isinstance(innhold, Vurdering):
            radene.append((dag, replace(innhold, ettertid=True)))
    return radene


class _Kursleser(Protocol):
    def serie(self, symbol: str) -> list[Kursrad]: ...


class _Ettertidslager(Protocol):
    def datoer_med_rad(self, symbol: str) -> set[date]: ...

    def datoer_med_kveldsrad(self, symbol: str) -> set[date]: ...

    def skriv(self, symbol: str, radene: list[tuple[date, Vurdering]], *, erstatt: bool = False) -> int: ...


@dataclass(frozen=True)
class Fylt:
    """Hva fyll_i_ettertid skrev: dager per aksje, bare aksjene med minst en.
    feilet er (symbol, typen til feilen) for aksjene som feilet (gjennomgangen,
    ECH2): symbolene og typen, aldri en kurs (regel 16)."""

    dager: dict[str, int]
    feilet: tuple[tuple[str, str], ...] = ()

    @property
    def antall(self) -> int:
        return sum(self.dager.values())


def fyll_i_ettertid(
    kurser: _Kursleser, lager: _Ettertidslager, lista: Iterable[Aksje], dagens: date, *, paa_nytt: bool = False
) -> Fylt:
    """Radene i ettertid for hver aksje i lista, skrevet gjennom lageret.

    Aksjer utenfor lista roeres ikke. Hver aksje skrives for seg, i en
    transaksjon. Gjennomgangen (ECH2): en feil for en aksje stopper ikke de
    neste, og Fylt sier hvilke som feilet. Med paa_nytt regnes ogsaa dagene
    som har en rad i ettertid, og raden byttes ut (ECH1); en kveldsrad
    roeres aldri, og en rad som ikke kan regnes med kursene som staar, staar."""
    dager: dict[str, int] = {}
    feilet: list[tuple[str, str]] = []
    for aksje in lista:
        try:
            har_rad = lager.datoer_med_kveldsrad(aksje.symbol) if paa_nytt else lager.datoer_med_rad(aksje.symbol)
            radene = regn_i_ettertid(kurser.serie(aksje.symbol), har_rad, dagens)
            if radene:
                skrevet = lager.skriv(aksje.symbol, radene, erstatt=paa_nytt)
                if skrevet:
                    dager[aksje.symbol] = skrevet
        except Exception as feil:
            feilet.append((aksje.symbol, type(feil).__name__))
    return Fylt(dager, tuple(feilet))
