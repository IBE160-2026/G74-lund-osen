"""Historikken paa aksjesiden, «Signalet dag for dag» - story 2.7 (2.7b),
FR-408, FR-409, AD-7, designregler.md §3.

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: maaneden, datoene i
kursserien og radene i vurdering kommer inn som argumenter. Siden leser
radene gjennom Vurderingslager.les_periode, en spoerring per maaned (AD-3).

Hver dag gaar gjennom les_tilstand, som oversikten og aksjedetaljen, saa
styrke 0, en grunn, en manglende rad, en dag som ikke er boersdag og en dag
utenfor boerskalenderen aldri ser like ut. Signalet regnes aldri her:
historikken viser det hentekommandoen skrev, ikke det dagens parametre ville
gitt (AD-7). Story 2.17: en dag med signalet regnet i ettertid er merket
(Dag.ettertid), og uka og maaneden sier hvor mange av de vurderte dagene som
er i ettertid. Maalingene staar paa siden for dagen (8.16b), som hver dag med
kurs lenker til (avgjoerelsen 2026-10-21 under story 2.7).
"""

import calendar
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from graf import MAANEDER
from justeringsdager import aaret_foer
from markedsoversikt import RETNINGSVISNING, SJEKKBOKSTAVER, Retningsvisning, les_tilstand
from perioder import _gjentatt
from tallformat import fortegn
from tilstand import MED_SIGNAL, Tilstand
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
        if self.tilstand is not None and self.tilstand.art in MED_SIGNAL:
            return self.tilstand.innhold
        return None

    @property
    def ettertid(self) -> bool:
        """Story 2.17: signalet er regnet i ettertid."""
        return self.tilstand is not None and self.tilstand.ettertid

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
    av dem med styrken paa terskelen eller over. Story 2.17: ettertid er de
    vurderte dagene med signalet regnet i ettertid."""

    nummer: int
    dager: tuple[Dag | None, ...]
    vurdert: int
    skilte_seg_ut: int
    ettertid: int = 0

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
    # Story 2.17: de vurderte dagene med signalet regnet i ettertid.
    ettertid: int = 0

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
    ut: date | None = None,
) -> Dag:
    innhold = rader.get(dato)
    # Story 2.11: etter at aksjen gikk ut, har den ingen kurser, men dagene
    # til og med i dag sier «ikke i lista», ikke ingenting.
    tatt_ut = ut is not None and ut <= dato <= idag
    if (dato > siste or dato < foerste) and innhold is None and not tatt_ut:
        return Dag(dato, None, None, tom=True, lenke=False, skilte_seg_ut=False)
    tilstand_, tekst = les_tilstand(innhold, dato, idag, ut)
    skilte = isinstance(innhold, Vurdering) and innhold.styrke >= terskel
    return Dag(dato, tilstand_, tekst, tom=False, lenke=dato in kursdager and dato > foerste, skilte_seg_ut=skilte)


def bygg_maaned(
    maaned: date,
    kursdatoer: Sequence[date],
    rader: dict[date, Vurdering | Grunn],
    idag: date,
    terskel: int,
    beskjed: str | None = None,
    ut: date | None = None,
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
            _dag(dato, kursdager, foerste, siste, rader, idag, terskel, ut) if dato.month == maaned.month else None
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
                    ettertid=sum(dag.ettertid for dag in vurdert),
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
        ettertid=sum(uke.ettertid for uke in uker),
    )


@dataclass(frozen=True)
class AlleSjekkene:
    """Story 8.23 (tillegg 2, gruppens svar kl. 14:53 og 14:59): hvor ofte
    aksjen fikk utslag på alle sjekkene det siste året, og sist. fra er den
    første dagen med en rad når serien er kortere enn et år, ellers None.
    Bare antall og datoer, ingen avkastning (NFR-06)."""

    antall: int
    sist: date | None
    fra: date | None
    # Story 8.26 (gruppens svar 11.11 kl. 22:04, tillegg 17): om aksjen har
    # minst én vurdering. Uten en eneste sier siden at signalet ikke er
    # regnet ennå, ikke «3 av 3 aldri».
    vurdert: bool = True
    # Story 2.17: hvor mange av dagene med alle sjekkene som er regnet i ettertid.
    ettertid: int = 0


def alle_sjekkene_det_siste_aaret(
    vurderingene: dict[date, Vurdering | Grunn] | None, til: date, antall_sjekker: int
) -> AlleSjekkene | None:
    """Radene i vurdering fra samme dato året før (justeringsdager.aaret_foer,
    som «1 år» i grafen) til og med til, lest og aldri regnet (AD-7). None
    når vurderingene ikke kan leses eller ingen rad finnes."""
    if not vurderingene:
        return None
    start = aaret_foer(til)
    dagene = sorted(d for d in vurderingene if start <= d <= til)
    if not dagene:
        return None
    alle = [d for d in dagene if isinstance(vurderingene[d], Vurdering) and vurderingene[d].styrke == antall_sjekker]
    foerste = min(vurderingene)
    return AlleSjekkene(
        antall=len(alle),
        sist=alle[-1] if alle else None,
        fra=foerste if foerste > start else None,
        vurdert=any(isinstance(v, Vurdering) for v in vurderingene.values()),
        ettertid=sum(getattr(vurderingene[d], "ettertid", False) for d in alle),
    )
