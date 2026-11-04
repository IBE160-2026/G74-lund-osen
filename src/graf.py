"""Skalering av kursgrafen til SVG-koordinater.

Ren regning. Ingen HTML og ingen tegnebibliotek - grafen er en SVG-polyline,
og malen setter bare tallene inn. Det holder for FR-201 og FR-202, og det
sparer oss for en frontend-avhengighet vi ellers maatte forsvart.

Aarsaken til at dette ligger i en egen fil, er at koordinatregning er lett aa
teste og vanskelig aa se feil i. En linje som ligger noen piksler galt, ser
riktig ut.

Story 2.9c: hovedindeksen er en stiplet linje i grafen. Den regnes om til
aksjens kurs: startdagen er den foerste dagen i grafen indeksen ogsaa har, og
hver dag indeksen har, faar kurs(start) x indeks(dag) / indeks(start). Saa
starter linja paa aksjens kurs, og aksjens linje over den betyr at aksjen
gikk bedre enn indeksen i perioden. Dager indeksen ikke har, faar ikke noe
punkt. Kursen, snittet og indeksen deler skala.

Story 8.2b, b (U41, U47): tegneflaten har et felt til venstre for tallene,
et nederst for datoene og et til hoeyre for navnene paa linjene, saa ingen
linje krysser en tekst. Navnene staar ved enden av linjene, i linjefargen
(utdraget §8), ogsaa «Hovedindeksen» ved den stiplede.
"""

from dataclasses import dataclass
from datetime import date

from aksjedetalj import Punkt
from boersdag import UtenforKalenderen, er_boersdag
from perioder import ANNENHVER_MAANED, DAGER, MAANEDSNAVN, UKER

BREDDE = 720
HOYDE = 260
MARG_Y = 12
# Story 8.2b, b (U41, U47): feltene rundt tegneflaten. VENSTRE har plass til
# tallene ved rutenettet («2 000» i 12 px), HOEYRE til det lengste navnet,
# «50-dagers snitt (sjekk 1)», og BUNN til datoene og maanedsnavnene. MARG_X
# paa 8 px til begge sider er borte.
VENSTRE = 44
HOEYRE = 170
BUNN = 22
# Avstanden fra enden av linja til navnet.
NAVNEMARG = 8

# Litt luft over og under, saa kurven ikke klistrer seg til kanten.
LUFT = 0.04


@dataclass(frozen=True)
class Rutelinje:
    y: float
    verdi: float


# Story 8.0c: fullt norsk maanedsnavn, smaa bokstaver (designregler §4).
MAANEDER = (
    "januar",
    "februar",
    "mars",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "desember",
)


# Plassen et maanedsnavn trenger med 10px skrift. Naermere hoeyre kant enn
# dette staar teksten til venstre for streken, saa den ikke kuttes (ECH1).
# Story 8.2b, b: tegneflaten slutter HOEYRE foer kanten, saa navnet ved det
# siste merket faar plass i feltet nederst til hoeyre, under navnene paa
# linjene. Det staar da til hoeyre for streken, ogsaa ved enden av flaten,
# og kommer ikke borti navnet ved merket foer.
NAVNEBREDDE = 60

# Gjennomgangen av 8.2b (ECH1): plassen en dato som «02.10» trenger. Et merke
# naermere det forrige enn dette faar streken, men ikke navnet, saa datoene
# ikke kommer borti hverandre paa den smalere tegneflaten.
DATOBREDDE = 36

# Story 8.16 (gjennomgangen, BH4): flere maanedsnavn enn dette faar ikke
# plass, saa da faar annenhver maaned navn.
MAKS_MAANEDSNAVN = 8


@dataclass(frozen=True)
class Maanedsmerke:
    x: float
    navn: str
    til_venstre: bool = False


# Story 8.0d, PR 3 (svar 19): navnene staar ved enden av linjene. Den
# hoeyeste linja faar navnet over seg og den laveste under, og under denne
# avstanden skyves de fra hverandre, saa de ikke ligger oppaa hverandre.
NAVNEAVSTAND = 16


@dataclass(frozen=True)
class Navn:
    x: float
    y: float


@dataclass(frozen=True)
class Graf:
    bredde: int
    hoyde: int
    kurslinje: str
    ma50linje: str
    lav: float
    hoy: float
    forste_dato: date
    siste_dato: date
    rutenett: tuple[Rutelinje, ...]
    maanedsmerker: tuple[Maanedsmerke, ...] = ()
    kursnavn: Navn | None = None
    snittnavn: Navn | None = None
    siste: Navn | None = None
    indekslinje: str = ""
    indeksstart: date | None = None
    indeksslutt: date | None = None
    # Story 8.16: punktet for dagen som er merket (siste boersdag og «Velg
    # dag»), None naar ingen dag er merket eller grafen ikke har den.
    merket: Navn | None = None
    # Story 8.2b, b (U47): navnet ved enden av den stiplede linja.
    indeksnavn: Navn | None = None

    # Story 8.2b, b (U41): kantene paa tegneflaten, som malen tegner
    # rutenettet og merkene etter.
    @property
    def venstre(self) -> float:
        return VENSTRE

    @property
    def hoeyre(self) -> float:
        return self.bredde - HOEYRE

    @property
    def topp(self) -> float:
        return MARG_Y

    @property
    def bunn(self) -> float:
        return self.hoyde - BUNN

    @property
    def har_ma50(self) -> bool:
        return bool(self.ma50linje)

    @property
    def har_indeks(self) -> bool:
        return bool(self.indekslinje)


def indeksverdier(punkter: tuple[Punkt, ...], indeks: dict[date, float] | None) -> dict[date, float]:
    """Indeksen regnet om til aksjens kurs, for hver dag i grafen indeksen
    har - story 2.9c. Tom naar indeksen har faerre enn to dager i grafen."""
    if not indeks:
        return {}
    felles = [p for p in punkter if p.dato in indeks]
    if len(felles) < 2:
        return {}
    start = felles[0]
    return {p.dato: start.kurs * indeks[p.dato] / indeks[start.dato] for p in felles}


def _spenn(punkter: tuple[Punkt, ...], ekstra: tuple[float, ...] = ()) -> tuple[float, float]:
    """Laveste og hoyeste verdi som skal faa plass - baade kurs og snitt, og
    indeksen regnet om (ekstra, story 2.9c).

    Snittet maa vaere med i regnestykket. Var det ikke det, kunne MA50-linja
    havnet utenfor tegneflaten uten at noe feilet, og sjekk 1 ville blitt
    usynlig akkurat naar den er mest interessant.
    """
    verdier = [p.kurs for p in punkter]
    verdier += [p.ma50 for p in punkter if p.ma50 is not None]
    verdier += list(ekstra)

    lav, hoy = min(verdier), max(verdier)
    if lav == hoy:
        # Flat serie. Uten dette blir hoyden null og alt deles paa null.
        return lav - 1.0, hoy + 1.0

    luft = (hoy - lav) * LUFT
    return lav - luft, hoy + luft


def _x(i: int, antall: int, bredde: int) -> float:
    """x for punkt nummer i av antall, innenfor tegneflaten (8.2b, b)."""
    return VENSTRE + (bredde - VENSTRE - HOEYRE) * i / (antall - 1)


def _y(verdi: float, lav: float, hoy: float, hoyde: int) -> float:
    """y for verdien, innenfor tegneflaten, over feltet nederst (8.2b, b)."""
    return MARG_Y + (hoyde - MARG_Y - BUNN) * (1 - (verdi - lav) / (hoy - lav))


def _koordinater(punkter, hent, lav, hoy, bredde, hoyde) -> str:
    """Punktstreng til SVG. Hopper over punkter der verdien mangler."""
    if len(punkter) < 2:
        return ""

    deler = []
    for i, punkt in enumerate(punkter):
        verdi = hent(punkt)
        if verdi is None:
            continue
        deler.append(f"{_x(i, len(punkter), bredde):.1f},{_y(verdi, lav, hoy, hoyde):.1f}")

    return " ".join(deler) if len(deler) >= 2 else ""


def _foerste_boersdag(aar: int, maaned: int) -> date | None:
    """Foerste boersdag i maaneden etter er_boersdag, eller None naar
    kalenderen ikke dekker aaret (boersdag.DEKKEDE_AAR)."""
    dag = date(aar, maaned, 1)
    try:
        while not er_boersdag(dag):
            dag = date.fromordinal(dag.toordinal() + 1)
    except UtenforKalenderen:
        return None
    return dag


def _maanedsmerker(punkter: tuple[Punkt, ...], bredde: int) -> tuple[Maanedsmerke, ...]:
    """Et merke ved foerste boersdag i hver maaned som finnes i serien - story
    8.0c. x er samme x som punktet for dagen, altsaa etter indeks og ikke
    etter kalenderen, fordi linja har lik avstand per boersdag. Mangler dagen
    i serien, faar maaneden ikke merke."""
    if len(punkter) < 2:
        return ()
    indeks = {p.dato: i for i, p in enumerate(punkter)}
    merker = []
    sett = set()
    for p in punkter:
        maaned = (p.dato.year, p.dato.month)
        if maaned in sett:
            continue
        sett.add(maaned)
        foerste = _foerste_boersdag(*maaned)
        if foerste is None or foerste not in indeks:
            continue
        x = _x(indeks[foerste], len(punkter), bredde)
        merker.append(Maanedsmerke(x=x, navn=MAANEDER[foerste.month - 1], til_venstre=x > bredde - NAVNEBREDDE))
    return tuple(merker)


def _dagmerker(punkter: tuple[Punkt, ...], bredde: int, hvilke: str) -> tuple[Maanedsmerke, ...]:
    """Story 8.16: merkene for de korte periodene. DAGER gir et merke ved
    hver dag (1 uke), UKER ved foerste dag i hver uke serien har (1 mnd).
    Navnet er datoen, som «02.10» (designregler §4)."""
    if len(punkter) < 2:
        return ()
    merker = []
    forrige_uke = None
    forrige_navn = None
    for i, p in enumerate(punkter):
        uke = p.dato.isocalendar()[:2]
        if hvilke == UKER and uke == forrige_uke:
            continue
        forrige_uke = uke
        x = _x(i, len(punkter), bredde)
        navn = f"{p.dato.day:02d}.{p.dato.month:02d}"
        if forrige_navn is not None and x - forrige_navn < DATOBREDDE:
            navn = ""
        else:
            forrige_navn = x
        merker.append(Maanedsmerke(x=x, navn=navn, til_venstre=x > bredde - NAVNEBREDDE))
    return tuple(merker)


def aksemerker(punkter: tuple[Punkt, ...], bredde: int, hvilke: str = MAANEDSNAVN) -> tuple[Maanedsmerke, ...]:
    """Merkene paa aksen etter perioden (story 8.16): dagene, ukene,
    maanedene, eller maanedene med navn paa annenhver for 1 aar og for alle
    perioder med flere enn MAKS_MAANEDSNAVN maaneder, som I aar fra september
    (gjennomgangen, BH4)."""
    if hvilke in (DAGER, UKER):
        return _dagmerker(punkter, bredde, hvilke)
    merker = _maanedsmerker(punkter, bredde)
    if hvilke == ANNENHVER_MAANED or len(merker) > MAKS_MAANEDSNAVN:
        merker = tuple(m if i % 2 == 0 else Maanedsmerke(m.x, "", m.til_venstre) for i, m in enumerate(merker))
    return merker


def _siste(punkter: str) -> tuple[float, float] | None:
    """Det siste punktet i en punktstreng, eller None naar den er tom."""
    if not punkter:
        return None
    x, y = punkter.split()[-1].split(",")
    return float(x), float(y)


def _navnene(linjer: tuple[str, ...], bredde: int, hoyde: int) -> tuple[Navn | None, ...]:
    """Hvor navnene paa linjene staar, i samme rekkefoelge som linjene: i
    feltet til hoeyre, ved hoeyden linja ender paa, og minst NAVNEAVSTAND
    fra hverandre, saa de ikke ligger oppaa hverandre. Den hoeyeste linja
    har det oeverste navnet. Story 8.2b, b (U41, U47): ved siden av enden,
    ikke over eller under den, saa ingen linje krysser et navn. y er
    grunnlinja, 4 under enden, saa teksten i 12 px staar midt paa linja."""
    ender = sorted((ende[1], i) for i, ende in enumerate(map(_siste, linjer)) if ende is not None)
    if not ender:
        return tuple(None for _ in linjer)
    # Gjennomgangen av 8.0d (BH2, ECH1): innenfor tegneflaten, over datoene.
    oeverst, nederst = MARG_Y + 4, hoyde - BUNN
    plass = [max(oeverst, y + 4) for y, _ in ender]
    for j in range(1, len(plass)):
        plass[j] = max(plass[j], plass[j - 1] + NAVNEAVSTAND)
    if plass[-1] > nederst:
        plass[-1] = nederst
        for j in range(len(plass) - 2, -1, -1):
            plass[j] = min(plass[j], plass[j + 1] - NAVNEAVSTAND)
    x = bredde - HOEYRE + NAVNEMARG
    ut: list[Navn | None] = [None] * len(linjer)
    for (_, i), y in zip(ender, plass, strict=True):
        ut[i] = Navn(x, y)
    return tuple(ut)


def _rutenett(lav: float, hoy: float, hoyde: int, linjer: int = 3) -> tuple[Rutelinje, ...]:
    ut = []
    for i in range(linjer):
        verdi = lav + (hoy - lav) * i / (linjer - 1)
        ut.append(Rutelinje(y=_y(verdi, lav, hoy, hoyde), verdi=verdi))
    return tuple(ut)


def bygg_graf(
    punkter: tuple[Punkt, ...],
    bredde: int = BREDDE,
    hoyde: int = HOYDE,
    indeks: dict[date, float] | None = None,
    merker: str = MAANEDSNAVN,
    merket: date | None = None,
) -> Graf | None:
    """Koordinatene for kurs og MA50, og for indeksen naar den er gitt som
    {dato: verdi} (story 2.9c). None naar det ikke er noe aa tegne.

    Story 8.16: merker sier hvilke merker aksen faar (aksemerker), og merket
    er dagen som merkes, naar grafen har den."""
    if len(punkter) < 2:
        return None

    omregnet = indeksverdier(punkter, indeks)
    lav, hoy = _spenn(punkter, tuple(omregnet.values()))
    kurslinje = _koordinater(punkter, lambda p: p.kurs, lav, hoy, bredde, hoyde)
    ma50linje = _koordinater(punkter, lambda p: p.ma50, lav, hoy, bredde, hoyde)
    indekslinje = _koordinater(punkter, lambda p: omregnet.get(p.dato), lav, hoy, bredde, hoyde)
    kursnavn, snittnavn, indeksnavn = _navnene((kurslinje, ma50linje, indekslinje), bredde, hoyde)
    siste = _siste(kurslinje)
    # Story 8.16: punktet for dagen, regnet fra indeksen som de andre
    # punktene (gjennomgangen, BH11).
    punktet = None
    datoene = [p.dato for p in punkter]
    if merket in datoene:
        i = datoene.index(merket)
        punktet = Navn(_x(i, len(punkter), bredde), _y(punkter[i].kurs, lav, hoy, hoyde))

    return Graf(
        bredde=bredde,
        hoyde=hoyde,
        kurslinje=kurslinje,
        ma50linje=ma50linje,
        kursnavn=kursnavn,
        snittnavn=snittnavn,
        siste=Navn(*siste) if siste else None,
        lav=lav,
        hoy=hoy,
        forste_dato=punkter[0].dato,
        siste_dato=punkter[-1].dato,
        maanedsmerker=aksemerker(punkter, bredde, merker),
        rutenett=_rutenett(lav, hoy, hoyde),
        indekslinje=indekslinje,
        indeksstart=min(omregnet) if omregnet else None,
        indeksslutt=max(omregnet) if omregnet else None,
        merket=punktet,
        indeksnavn=indeksnavn,
    )
