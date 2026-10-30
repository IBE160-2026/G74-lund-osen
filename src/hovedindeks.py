"""Hovedindeksen over tabellen paa forsiden - story 2.9, FR-104.

Ren logikk. Faar serien for indeksen og seriene for aksjene gjennom portene,
gjoer ingen nettkall (AD-10) og kjenner ingen HTML.

- Verdien er slutt for indeksens siste rad.
- Endringen regnes mot forrige boersdag etter kalenderen, ikke mot forrige
  rad, fordi indeksen kan ha datoer aksjene ikke har (malinger.md §14).
  Mangler raden for forrige boersdag, eller ligger dagen utenfor kalenderen,
  vises ingen endring.
- N er aksjene med kurs for indeksens dato, telt fra lista, aldri et fast
  antall (foeringen 30.09 under AD-21). En aksje som ikke er med, navngis.
- En aksjes endring for datoen er endringen fra FR-101, kursen den dagen mot
  raden foer, som i tabellen.
- «Bedre» avgjoeres paa endringene slik de vises (tallformat.avrundet), og
  lik er ikke bedre.
- Har ingen aksje kurs for indeksens dato, eller har indeksen ingen endring,
  er det ingen sammenligning.

Story 2.9b (FR-105): én soeyle per aksje med endringen for indeksens dato,
fra stoerst fall til stoerst stigning. Antallet telles. En aksje med kurs,
men uten rad foer dagen, faar ingen soeyle og navngis. Hoeyden og plassen
til indekslinja regnes her, i prosent av feltet, med null midt i det og den
stoerste endringen av soeylene og indeksen paa halve hoeyden.

Story 8.17a: soeylene og linja foelger periodevalget i oversikten. For en
periode er endringen fra den foerste kursen i perioden (perioder.foerste_kursdag
fra startdagen) til tabellens dag,
regnet med periodeendring som tabellen, og for «Velg dag» endringen for
dagen. Gult bransjesymbol er fortsatt 3 av 3 paa siste boersdag.
"""

from dataclasses import dataclass, replace
from datetime import date, timedelta

from boersdag import UtenforKalenderen, er_boersdag
from indeksdata import HOVEDINDEKS
from kursdata import Aksje, Kursrad
from markedsoversikt import endring_i_prosent, periodeendring
from perioder import SISTE, VELG, foerste_kursdag, startdag
from tallformat import avrundet

# Hoeyst saa mange dager tilbake leter forrige_boersdag. Den lengste stengte
# perioden ved Oslo Boers er paaskeuka med helgene rundt, under ti dager.
LETEDAGER = 14


@dataclass(frozen=True)
class Sammenligning:
    """«x av N gikk bedre enn indeksen», og aksjene som ikke er med."""

    bedre: int
    med: int
    uten: tuple[str, ...]


@dataclass(frozen=True)
class Soeyle:
    """En aksje under indeksen. endring er i prosent, uavrundet. hoeyde er
    lengden i prosent av feltet, fra null-linja midt i det."""

    symbol: str
    navn: str
    bransje: str
    endring: float
    tre_av_tre: bool
    hoeyde: float


@dataclass(frozen=True)
class Soeyler:
    """Soeylene under indeksen, fra stoerst fall til stoerst stigning.
    linje er toppen av den stiplede linja i prosent av feltet, og None naar
    indeksen ikke har en endring. uten_endring er aksjene med kurs for
    dagen, men uten rad foer den."""

    soeyler: tuple[Soeyle, ...]
    linje: float | None
    uten_endring: tuple[str, ...]
    # Story 8.17a: indeksens endring linja viser, dagen soeylene slutter paa,
    # startdagen for en periode (None for én dag), og aksjene der endringen
    # er regnet fra en senere dag fordi serien ikke har startdagen.
    indeks: float | None = None
    dag: date | None = None
    start: date | None = None
    kortere: tuple[str, ...] = ()
    # Gruppens svar 30.10 kl. 10:45 (VG5): indeksen har ingen kurs dagen
    # soeylene gjelder, saa siden sier det over soeylene.
    indeks_mangler: bool = False


@dataclass(frozen=True)
class Hovedindeksvisning:
    """Det forsiden viser om indeksen. endring er i prosent, uavrundet, og
    None naar den ikke kan regnes. sammenligning er None naar den ikke vises.
    Story 8.17a (gruppens svar 30.10 kl. 12:21, e): dato er tabellens dag, og
    verdi er None naar indeksen ikke har kurs den dagen."""

    symbol: str
    dato: date
    verdi: float | None
    endring: float | None
    sammenligning: Sammenligning | None
    soeyler: Soeyler | None = None

    @property
    def har_soeyler(self) -> bool:
        """Om minst én aksje har soeyle. Malen bruker den baade for soeylene
        og for teksten om dem bak «?» (gjennomgangen, BH13)."""
        return self.soeyler is not None and bool(self.soeyler.soeyler)


def valgt_indeks(symboler: tuple[str, ...]) -> str:
    """HOVEDINDEKS (OSEBX) naar basen har den, ellers den basen sist hentet,
    som DEMIX i demobasen. Forsiden, kursgrafen og KI-grunnlaget (story
    10.2e) bruker samme indeks."""
    return HOVEDINDEKS.symbol if HOVEDINDEKS.symbol in symboler else symboler[0]


def forrige_boersdag(dag: date) -> date | None:
    """Boersdagen foer dag etter kalenderen, eller None naar den ligger
    utenfor aarene kalenderen dekker."""
    for tilbake in range(1, LETEDAGER + 1):
        foer = dag - timedelta(days=tilbake)
        try:
            if er_boersdag(foer):
                return foer
        except UtenforKalenderen:
            return None
    return None


def indeksendring(serie: list[Kursrad]) -> float | None:
    """Endringen i prosent for siste rad mot forrige boersdag, paa justert
    kurs som for aksjene. None uten rad for forrige boersdag."""
    if not serie:
        return None
    siste = serie[-1]
    foer = forrige_boersdag(siste.dato)
    if foer is None:
        return None
    paa_dag = {rad.dato: rad for rad in serie}
    if foer not in paa_dag:
        return None
    return endring_i_prosent([paa_dag[foer], siste])


def aksjeendring(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen fra FR-101 for dag: kursen den dagen mot raden foer. None
    naar aksjen ikke har kurs for dagen, eller ingen rad foer den."""
    for i, rad in enumerate(serie):
        if rad.dato == dag:
            return endring_i_prosent(serie[i - 1 : i + 1]) if i > 0 else None
    return None


def er_bedre(aksje: float | None, indeks: float) -> bool:
    """Om aksjens endring slik den vises er stoerre enn indeksens. Lik er
    ikke bedre, og en aksje uten endring er ikke bedre."""
    return aksje is not None and avrundet(aksje, "endring") > avrundet(indeks, "endring")


def sammenlign(dag: date, indeks: float | None, aksjer: list[tuple[str, list[Kursrad]]]) -> Sammenligning | None:
    """«x av N» for dag. aksjer er (navn, serie) for hver aksje i lista, i
    lista sin rekkefoelge. None naar indeksen ikke har en endring, eller
    ingen aksje har kurs for dagen."""
    if indeks is None:
        return None
    med = [(navn, serie) for navn, serie in aksjer if any(rad.dato == dag for rad in serie)]
    if not med:
        return None
    uten = tuple(navn for navn, serie in aksjer if not any(rad.dato == dag for rad in serie))
    bedre = sum(1 for _, serie in med if er_bedre(aksjeendring(serie, dag), indeks))
    return Sammenligning(bedre=bedre, med=len(med), uten=uten)


def bygg_soeyler(dag: date, indeks: float | None, aksjer: list[tuple[Aksje, list[Kursrad], bool]]) -> Soeyler | None:
    """Soeylene for dag. aksjer er (aksje, serie, 3 av 3) for hver aksje i
    lista, i lista sin rekkefoelge. None naar ingen aksje har kurs for dagen."""
    med_kurs = [(aksje, serie, tre) for aksje, serie, tre in aksjer if any(rad.dato == dag for rad in serie)]
    if not med_kurs:
        return None
    endringer = [(aksje, aksjeendring(serie, dag), tre) for aksje, serie, tre in med_kurs]
    return _soeyler(endringer, indeks, dag)


def bygg_soeyler_perioden(
    start: date, slutt: date, indeks: float | None, aksjer: list[tuple[Aksje, list[Kursrad], bool]]
) -> Soeyler | None:
    """Soeylene for perioden fra start til slutt - story 8.17a. Endringen
    er periodeendring, som i tabellen, og aksjer uten startdagen regnes fra
    foerste dag serien har og navngis. None naar ingen aksje har kurs for
    slutt."""
    med_kurs = [(aksje, serie, tre) for aksje, serie, tre in aksjer if any(rad.dato == slutt for rad in serie)]
    if not med_kurs:
        return None
    endringer, kortere = [], []
    for aksje, serie, tre in med_kurs:
        utfall = periodeendring(serie, start, slutt)
        endringer.append((aksje, utfall[0] if utfall else None, tre))
        if utfall and utfall[1] is not None:
            kortere.append(aksje.navn)
    return _soeyler(endringer, indeks, slutt, start, tuple(kortere))


def _soeyler(
    endringer: list[tuple[Aksje, float | None, bool]],
    indeks: float | None,
    dag: date,
    start: date | None = None,
    kortere: tuple[str, ...] = (),
) -> Soeyler:
    """Soeylene av endringene, sortert, med hoeyden og linja."""
    uten_endring = tuple(aksje.navn for aksje, endring, _ in endringer if endring is None)
    med = [(aksje, endring, tre) for aksje, endring, tre in endringer if endring is not None]
    # sorted er stabil, saa like endringer staar i rekkefoelgen fra lista.
    med.sort(key=lambda par: par[1])
    # Gjennomgangen (BH7, ECH6): hoeyden og linja regnes paa endringen slik
    # den vises, saa en soeyle som viser 0,00 % ikke har lengde, og retning,
    # farge og tall sier det samme.
    vist = {id(aksje): avrundet(endring, "endring") for aksje, endring, _ in med}
    vist_indeks = None if indeks is None else avrundet(indeks, "endring")
    skala = max([abs(v) for v in vist.values()] + [abs(vist_indeks or 0.0)]) or 1.0
    soeyler = tuple(
        Soeyle(
            symbol=aksje.symbol,
            navn=aksje.navn,
            bransje=aksje.sektor,
            endring=endring,
            tre_av_tre=tre,
            hoeyde=abs(vist[id(aksje)]) / skala * 50,
        )
        for aksje, endring, tre in med
    )
    linje = None if vist_indeks is None else 50 - vist_indeks / skala * 50
    return Soeyler(
        soeyler=soeyler,
        linje=linje,
        uten_endring=uten_endring,
        indeks=indeks,
        dag=dag,
        start=start,
        kortere=kortere,
    )


def soeylene_for(
    serie: list[Kursrad],
    grunnlag: list[tuple[Aksje, list[Kursrad], bool]],
    periode: str = SISTE,
    dag: date | None = None,
    slutt: date | None = None,
    start: date | None = None,
) -> Soeyler | None:
    """Soeylene for perioden eller dagen i oversikten - story 8.17a. serie
    er indeksen, og slutt er tabellens dag, siste boersdag i oversikten.
    Siste boersdag gir soeylene for slutt, en periode endringen fra
    startdagen til slutt, og «Velg dag» endringen den dagen. Linja er
    indeksens endring for samme dag eller periode.

    Gruppens svar 30.10 kl. 10:45 (VG5): soeylene og linja foelger tabellens
    dag, ikke indeksens siste dato. Mangler indeksen kurs den dagen, er det
    ingen linje, og indeks_mangler sier det. Uten slutt er det indeksens
    siste dato. start er dagen den foerste kursen i perioden er fra, regnet
    av siden for linja over tabellen, saa soeylene sier den samme dagen
    (gjennomgangen 30.10, BH3 og ECH1). Uten start regnes den her."""
    siste = slutt or serie[-1].dato
    paa = dag if periode == VELG and dag is not None else siste
    har_dagen = any(rad.dato == paa for rad in serie)
    if periode in (SISTE, VELG):
        foer = [rad for rad in serie if rad.dato <= paa]
        soeyler = bygg_soeyler(paa, indeksendring(foer) if har_dagen else None, grunnlag)
    else:
        # Gruppens svar 30.10 kl. 10:45 (ECH1): dagen den foerste kursen i
        # perioden er fra, som linja over tabellen, ikke en stengt startdag.
        if start is None:
            beregnet = startdag(periode, siste)
            start = foerste_kursdag((s for _, s, _ in grunnlag), beregnet, siste) or beregnet
        utfall = periodeendring(serie, start, siste)
        # Gjennomgangen (BH4, ECH4): begynner indeksen etter startdagen, er
        # det ingen linje, saa linja aldri gjelder en kortere tid enn soeylene.
        indeks = utfall[0] if utfall and utfall[1] is None else None
        soeyler = bygg_soeyler_perioden(start, siste, indeks, grunnlag)
    return replace(soeyler, indeks_mangler=not har_dagen) if soeyler else None


def bygg_hovedindeks(
    symbol: str,
    serie: list[Kursrad],
    aksjer: list[tuple[str, list[Kursrad]]],
    soeylegrunnlag: list[tuple[Aksje, list[Kursrad], bool]] | None = None,
    periode: str = SISTE,
    dag: date | None = None,
    slutt: date | None = None,
    start: date | None = None,
) -> Hovedindeksvisning | None:
    """Det forsiden viser, eller None naar indeksen ikke har en eneste rad.
    soeylegrunnlag er (aksje, serie, 3 av 3) for soeylene (story 2.9b), og
    uten det er det ingen soeyler. Story 8.17a: periode og dag fra
    periodevalget gjelder soeylene og linja, og slutt er tabellens dag
    (gruppens svar 30.10 kl. 10:45, VG5).

    Gruppens svar 30.10 kl. 12:21 (e): hele delen foelger tabellens dag,
    ogsaa verdien, endringen og «x av N»: slutt, eller dagen for «Velg dag».
    Uten slutt er det indeksens siste dato. Mangler indeksen kurs den dagen,
    er verdien None, og siden sier det der tallet ellers staar."""
    if not serie:
        return None
    vist = dag if periode == VELG and dag is not None else (slutt or serie[-1].dato)
    foer = [rad for rad in serie if rad.dato <= vist]
    paa_dagen = foer[-1] if foer and foer[-1].dato == vist else None
    endring = indeksendring(foer) if paa_dagen else None
    return Hovedindeksvisning(
        symbol=symbol,
        dato=vist,
        verdi=float(paa_dagen.slutt) if paa_dagen else None,
        endring=endring,
        sammenligning=sammenlign(vist, endring, aksjer),
        soeyler=soeylene_for(serie, soeylegrunnlag, periode, dag, slutt, start) if soeylegrunnlag is not None else None,
    )
