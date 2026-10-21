"""Historikken paa aksjesiden, «Signalet dag for dag» - story 2.7 (2.7b),
FR-408, FR-409, AD-7, designregler.md §3.

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: maaneden, datoene i
kursserien og radene i vurdering kommer inn som argumenter. Siden leser
radene gjennom Vurderingslager.les_periode, en spoerring per maaned (AD-3).

Hver dag gaar gjennom les_tilstand, som oversikten og aksjedetaljen, saa
styrke 0, en grunn, en manglende rad, en dag som ikke er boersdag og en dag
utenfor boerskalenderen aldri ser like ut. Signalet regnes aldri her:
historikken viser det hentekommandoen skrev, ikke det dagens parametre ville
gitt (AD-7). Maalingene staar paa siden for dagen (8.16b), som hver dag med
kurs lenker til (avgjoerelsen 2026-10-21 under story 2.7).
"""

import calendar
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from graf import MAANEDER
from markedsoversikt import RETNINGSVISNING, SJEKKBOKSTAVER, Retningsvisning, les_tilstand
from perioder import _gjentatt
from tallformat import fortegn
from tilstand import Art, Tilstand
from vurderingsdata import Grunn, Vurdering

# Parameteren i adressen, og ankeret pilene gaar til, saa siden blir staaende
# ved avsnittet.
PARAMETER = "maaned"
ANKER = "signalet-dag-for-dag"

# Bare ÅÅÅÅ-MM med sifrene 0-9, som _DATO i perioder.py.
_MAANED = re.compile(r"[0-9]{4}-[0-9]{2}")

# Mandag til fredag.
HVERDAGER = 5


@dataclass(frozen=True)
class Dag:
    """En dag i historikken.

    tom er en dag etter siste kursrad uten rad i vurdering: raden er ikke
    skrevet ennaa, og dagen skal ikke se ut som et hull. Det samme gjelder en
    dag foer foerste kursrad, der aksjen ikke hadde kurs (gjennomgangen, BH2,
    ECH2, VG10). Da er tilstand og tekst None, og siden sier hvor langt
    kursserien gaar. Ellers er de det les_tilstand gir. lenke er om dagen lenker
    til siden for dagen: bare en dag med kurs, og ikke seriens foerste dag,
    som les_valg ikke godtar (8.16, BH3).
    """

    dato: date
    tilstand: Tilstand | None
    tekst: str | None
    tom: bool
    lenke: bool
    skilte_seg_ut: bool

    @property
    def vurdering(self) -> Vurdering | None:
        if self.tilstand is not None and self.tilstand.art is Art.SVAR:
            return self.tilstand.innhold
        return None

    @property
    def retning(self) -> Retningsvisning | None:
        return RETNINGSVISNING[self.vurdering.retning] if self.vurdering else None

    @property
    def brikker(self) -> tuple[tuple[str, str, str], ...]:
        """T, B og I som i oversikten, lest fra den lagrede vurderingen."""
        if not self.vurdering:
            return ()
        return tuple((bokstav, felt, fortegn(getattr(self.vurdering, felt))) for bokstav, felt in SJEKKBOKSTAVER)


@dataclass(frozen=True)
class Uke:
    """En uke etter ISO 8601. dager er mandag til fredag, None for en dag i
    en annen maaned. vurdert er dagene med en vurdering, og skilte_seg_ut de
    av dem med styrken paa terskelen eller over."""

    nummer: int
    dager: tuple[Dag | None, ...]
    vurdert: int
    skilte_seg_ut: int

    @property
    def tom(self) -> bool:
        """Alle dagene i maaneden er etter siste kursrad, uten rad. Da har
        uka ingen tekst, saa den ikke ser ut som et hull."""
        return all(dag.tom for dag in self.dager if dag is not None)


@dataclass(frozen=True)
class Maaned:
    """Maaneden i historikken. foerste er den 1. i maaneden. utslag er
    (navnet paa sjekken, dager med +1 eller -1) i rekkefoelgen paa siden.
    forrige og neste er den 1. i naermeste maaned foer og etter med en
    kursrad, None naar det ikke finnes en (gjennomgangen, VG9). kurs_fra og
    kurs_til er foerste og siste kursrad. beskjed er en kort tekst naar
    adressen hadde en maaned som ikke kunne vises."""

    foerste: date
    uker: tuple[Uke, ...]
    vurdert: int
    skilte_seg_ut: int
    utslag: tuple[tuple[str, int], ...]
    forrige: date | None
    neste: date | None
    kurs_fra: date
    kurs_til: date
    beskjed: str | None = None

    @property
    def har_tomme(self) -> bool:
        """Maaneden har dager utenfor kursserien, som staar tomme."""
        return any(dag is not None and dag.tom for uke in self.uker for dag in uke.dager)

    @property
    def navn(self) -> str:
        return MAANEDER[self.foerste.month - 1]

    @property
    def tittel(self) -> str:
        return maanedsnavn(self.foerste)


def maanedsnavn(dag: date) -> str:
    """«oktober 2026», maaneden og aaret, med smaa bokstaver (designregler §4)."""
    return f"{MAANEDER[dag.month - 1]} {dag.year}"


def perioden(foerste: date) -> tuple[date, date]:
    """Foerste og siste dag i maaneden."""
    return foerste, foerste.replace(day=calendar.monthrange(foerste.year, foerste.month)[1])


def les_maaned(verdi: str | None, dagen: date, foerste: date, siste: date) -> tuple[date, str | None]:
    """Maaneden fra adressen, som den 1. i maaneden, og en beskjed.

    dagen er dagen siden viser, og foerste og siste er foerste og siste
    kursrad. Uten verdi er maaneden den for dagen. En verdi som ikke kan
    leses, eller en maaned uten kursrad i serien, gir maaneden for dagen og
    en kort beskjed, aldri en feilside."""
    for_dagen = dagen.replace(day=1)
    if not verdi:
        return for_dagen, None
    try:
        if not _MAANED.fullmatch(verdi):
            raise ValueError(verdi)
        valgt = date(int(verdi[:4]), int(verdi[5:]), 1)
    except ValueError:
        return (
            for_dagen,
            f"Måneden «{_gjentatt(verdi)}» kunne ikke leses, så historikken viser {maanedsnavn(for_dagen)}.",
        )
    if not foerste.replace(day=1) <= valgt <= siste.replace(day=1):
        return for_dagen, (
            f"Kursserien går fra {maanedsnavn(foerste)} til {maanedsnavn(siste)}, "
            f"så historikken viser {maanedsnavn(for_dagen)}."
        )
    return valgt, None


def adresse(symbol: str, maaned: date, *, dag: date | None = None, periode: str | None = None) -> str:
    """Adressen til en pil: maaneden, og dagen eller perioden siden viser."""
    deler = [f"{PARAMETER}={maaned:%Y-%m}"]
    if dag is not None:
        deler.append(f"dag={dag.isoformat()}")
    elif periode:
        deler.append(f"periode={periode}")
    return f"/aksje/{symbol}?" + "&".join(deler) + f"#{ANKER}"


def _dag(
    dato: date,
    kursdager: frozenset[date],
    foerste: date,
    siste: date,
    rader: dict[date, Vurdering | Grunn],
    idag: date,
    terskel: int,
) -> Dag:
    innhold = rader.get(dato)
    if (dato > siste or dato < foerste) and innhold is None:
        return Dag(dato, None, None, tom=True, lenke=False, skilte_seg_ut=False)
    tilstand_, tekst = les_tilstand(innhold, dato, idag)
    ut = isinstance(innhold, Vurdering) and innhold.styrke >= terskel
    return Dag(dato, tilstand_, tekst, tom=False, lenke=dato in kursdager and dato > foerste, skilte_seg_ut=ut)


def bygg_maaned(
    maaned: date,
    kursdatoer: Sequence[date],
    rader: dict[date, Vurdering | Grunn],
    idag: date,
    terskel: int,
    beskjed: str | None = None,
) -> Maaned:
    """Maaneden med ukene, dagene og tallene.

    maaned er den 1. i maaneden, kursdatoer datoene i kursserien i stigende
    rekkefoelge, og rader det les_periode ga for maaneden. terskel er
    Parametre.terskel, som i oversikten."""
    foerste, siste = kursdatoer[0], kursdatoer[-1]
    kursdager = frozenset(kursdatoer)
    _, slutt = perioden(maaned)
    uker: list[Uke] = []
    mandag = maaned - timedelta(days=maaned.weekday())
    while mandag <= slutt:
        dager = tuple(
            _dag(dato, kursdager, foerste, siste, rader, idag, terskel) if dato.month == maaned.month else None
            for dato in (mandag + timedelta(days=i) for i in range(HVERDAGER))
        )
        if any(dag is not None for dag in dager):
            vurdert = [dag for dag in dager if dag is not None and dag.vurdering]
            uker.append(
                Uke(
                    nummer=mandag.isocalendar().week,
                    dager=dager,
                    vurdert=len(vurdert),
                    skilte_seg_ut=sum(dag.skilte_seg_ut for dag in vurdert),
                )
            )
        mandag += timedelta(days=7)
    vurderinger = [dag.vurdering for uke in uker for dag in uke.dager if dag is not None and dag.vurdering]
    maaneder = sorted({dag.replace(day=1) for dag in kursdatoer})
    forrige = [m for m in maaneder if m < maaned]
    neste = [m for m in maaneder if m > maaned]
    return Maaned(
        foerste=maaned,
        uker=tuple(uker),
        vurdert=len(vurderinger),
        skilte_seg_ut=sum(uke.skilte_seg_ut for uke in uker),
        utslag=tuple((felt, sum(getattr(v, felt) != 0 for v in vurderinger)) for _, felt in SJEKKBOKSTAVER),
        forrige=forrige[-1] if forrige else None,
        neste=neste[0] if neste else None,
        kurs_fra=foerste,
        kurs_til=siste,
        beskjed=beskjed,
    )
