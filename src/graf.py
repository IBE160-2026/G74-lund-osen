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

Story 8.2c: kursgrafen har egne maal paa smal skjerm (bygg_graf med
smal=True). Den brede grafen skaleres ned med vinduet, saa teksten i den ble
om lag 5 px ved 390 px. Den smale er SMAL_BREDDE bred, har de samme dataene,
linjene og merkene, og navnene paa linjene staar i en forklaring under
datoene i stedet for i feltet til hoeyre, som ville tatt over halve flaten.
Navn paa aksen som ville kommet borti hverandre, faar streken, men ikke navnet.
"""

from dataclasses import dataclass
from datetime import date

from aksjedetalj import Punkt
from boersdag import UtenforKalenderen, er_boersdag
from perioder import ANNENHVER_MAANED, DAGER, MAANEDSNAVN, UKER

BREDDE = 720
HOYDE = 260
# Story 8.20b (BH9 i gjennomgangen av 8.20a): lappen med datoen på streken
# er 18 px høy og står over tegneflaten, 4 px over den (aksje.html), så den
# aldri dekker toppen av kurslinja. Tegneflaten begynner derfor ved 26, ikke 12.
MARG_Y = 26
# Story 8.2b, b (U41, U47): feltene rundt tegneflaten. VENSTRE har plass til
# tallene ved rutenettet («2 000» i 12 px), HOEYRE til det lengste navnet,
# «50-dagers snitt (sjekk 1)», og BUNN til datoene og maanedsnavnene. MARG_X
# paa 8 px til begge sider er borte.
VENSTRE = 44
HOEYRE = 170
BUNN = 22
# Avstanden fra enden av linja til navnet.
NAVNEMARG = 8

# Story 8.2c: maalene paa smal skjerm. Ved 390 px er grafen 312 px bred
# (maalt i Edge), saa teksten paa 12 blir 12 x 312 / 280, om lag 13,4 px, mer
# enn den minste teksten ellers paa siden (11,5 px). HOEYRE er bare plass til
# punktet ved enden, og navnene paa linjene staar i FORKLARING under datoene,
# en linje paa FORKLARINGSLINJE per navn.
SMAL_BREDDE = 280
SMAL_HOYDE = 250
SMAL_HOEYRE = 8
FORKLARING = 52
FORKLARINGSLINJE = 16
# Plassen et tegn i 12 px trenger, anslaatt litt romslig for IBM Plex Sans,
# og luften mellom to navn paa aksen.
TEGNBREDDE = 7
NAVNELUFT = 4

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


# Story 8.2c: en linje i forklaringen paa smal skjerm. klasse er kurs, snitt
# eller indeks, som navnene paa bred skjerm, og y er grunnlinja til navnet.
@dataclass(frozen=True)
class Forklaring:
    klasse: str
    y: float


# Story 8.20a (del C, gruppens svar 07.11 kl. 10:33, U92): lappen med
# verdiene ved musepekeren, i appens stil som i skissen aksjesiden-ki-paa.png,
# med CSS og uten skript. Hver dag faar et felt over hele hoeyden, like bredt
# som avstanden mellom to dager, og lappen vises naar musa er over feltet.
# LAPPBREDDE og LAPPHOYDE er lappen med dato, kurs og snitt, og LAPPLUFT
# avstanden fra punktet.
# Gjennomgangen av 8.20a (ECH8): bred nok til «Snitt 50 dager» og et tall med
# tusenskille, som «1 234,56», i 12 px. Var 132.
LAPPBREDDE = 176
LAPPHOYDE = 58
LAPPLUFT = 10


@dataclass(frozen=True)
class Dag:
    """En dag i grafen, med feltet musa treffer og der lappen staar.
    y_snitt og snitt er None foer snittet har nok historikk."""

    dato: date
    x: float
    y: float
    kurs: float
    snitt: float | None
    y_snitt: float | None
    felt_x: float
    felt_bredde: float
    lapp_x: float
    lapp_y: float


@dataclass(frozen=True)
class Signaldag:
    """Story 8.8 (FR-206): en dag aksjen skilte seg ut, slik vurderingen er
    lagret, med punktet på kurslinja. retning er Positiv, Negativ eller
    Blandet, og alle er sant ved 3 av 3."""

    dato: date
    x: float
    y: float
    retning: str
    styrke: int
    alle: bool


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
    # Story 8.2c: feltene til hoeyre og nederst, og forklaringen, som bare
    # den smale grafen har.
    hoeyrefelt: int = HOEYRE
    bunnfelt: int = BUNN
    forklaring: tuple[Forklaring, ...] = ()
    # Gjennomgangen av 8.2c (BH7, ECH4): et eget felt, ikke utledet av feltet
    # til hoeyre, saa klassen i malen ikke avhenger av maalene.
    smal: bool = False
    # Story 8.20a (del C): dagene med lappen ved musepekeren.
    dager: tuple[Dag, ...] = ()
    # Story 8.8: dagene aksjen skilte seg ut, lest og aldri regnet.
    signaldager: tuple[Signaldag, ...] = ()

    # Story 8.2b, b (U41): kantene paa tegneflaten, som malen tegner
    # rutenettet og merkene etter.
    @property
    def venstre(self) -> float:
        return VENSTRE

    @property
    def hoeyre(self) -> float:
        return self.bredde - self.hoeyrefelt

    @property
    def topp(self) -> float:
        return MARG_Y

    @property
    def bunn(self) -> float:
        return self.hoyde - self.bunnfelt

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


def _x(i: int, antall: int, bredde: int, hoeyre: int = HOEYRE) -> float:
    """x for punkt nummer i av antall, innenfor tegneflaten (8.2b, b)."""
    return VENSTRE + (bredde - VENSTRE - hoeyre) * i / (antall - 1)


def _y(verdi: float, lav: float, hoy: float, hoyde: int, bunn: int = BUNN) -> float:
    """y for verdien, innenfor tegneflaten, over feltet nederst (8.2b, b)."""
    return MARG_Y + (hoyde - MARG_Y - bunn) * (1 - (verdi - lav) / (hoy - lav))


def _koordinater(punkter, hent, lav, hoy, bredde, hoyde, hoeyre=HOEYRE, bunn=BUNN) -> str:
    """Punktstreng til SVG. Hopper over punkter der verdien mangler."""
    if len(punkter) < 2:
        return ""

    deler = []
    for i, punkt in enumerate(punkter):
        verdi = hent(punkt)
        if verdi is None:
            continue
        deler.append(f"{_x(i, len(punkter), bredde, hoeyre):.1f},{_y(verdi, lav, hoy, hoyde, bunn):.1f}")

    return " ".join(deler) if len(deler) >= 2 else ""


def _foerste_boersdag(aar: int, maaned: int) -> date | None:
    """Foerste boersdag i maaneden etter er_boersdag, eller None naar
    kalenderen ikke dekker aaret (foer boersdag.FOERSTE_AAR)."""
    dag = date(aar, maaned, 1)
    try:
        while not er_boersdag(dag):
            dag = date.fromordinal(dag.toordinal() + 1)
    except UtenforKalenderen:
        return None
    return dag


def _maanedsmerker(punkter: tuple[Punkt, ...], bredde: int, hoeyre: int = HOEYRE) -> tuple[Maanedsmerke, ...]:
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
        x = _x(indeks[foerste], len(punkter), bredde, hoeyre)
        merker.append(Maanedsmerke(x=x, navn=MAANEDER[foerste.month - 1], til_venstre=x > bredde - NAVNEBREDDE))
    return tuple(merker)


def _dagmerker(
    punkter: tuple[Punkt, ...], bredde: int, hvilke: str, hoeyre: int = HOEYRE, tynn: bool = True
) -> tuple[Maanedsmerke, ...]:
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
        x = _x(i, len(punkter), bredde, hoeyre)
        navn = f"{p.dato.day:02d}.{p.dato.month:02d}"
        if tynn and forrige_navn is not None and x - forrige_navn < DATOBREDDE:
            navn = ""
        else:
            forrige_navn = x
        merker.append(Maanedsmerke(x=x, navn=navn, til_venstre=x > bredde - NAVNEBREDDE))
    return tuple(merker)


def aksemerker(
    punkter: tuple[Punkt, ...],
    bredde: int,
    hvilke: str = MAANEDSNAVN,
    hoeyre: int = HOEYRE,
    tynn: bool = True,
) -> tuple[Maanedsmerke, ...]:
    """Merkene paa aksen etter perioden (story 8.16): dagene, ukene,
    maanedene, eller maanedene med navn paa annenhver for 1 aar og for alle
    perioder med flere enn MAKS_MAANEDSNAVN maaneder, som I aar fra september
    (gjennomgangen, BH4).

    Gjennomgangen av 8.2c (ECH1): tynn=False lar datoene staa, saa den smale
    grafen tynner dem i _uten_overlapp fra hoeyre, og datoen naermest
    dagen grafen slutter paa, ikke tas bort foerst."""
    if hvilke in (DAGER, UKER):
        return _dagmerker(punkter, bredde, hvilke, hoeyre, tynn)
    merker = _maanedsmerker(punkter, bredde, hoeyre)
    if hvilke == ANNENHVER_MAANED or len(merker) > MAKS_MAANEDSNAVN:
        merker = tuple(m if i % 2 == 0 else Maanedsmerke(m.x, "", m.til_venstre) for i, m in enumerate(merker))
    return merker


def navneplass(merke: Maanedsmerke) -> tuple[float, float]:
    """Story 8.2c: fra og til x for navnet ved merket, med TEGNBREDDE per
    tegn. Navnet staar 3 til hoeyre for streken, eller 3 til venstre naar
    det staar til venstre (malen)."""
    lengde = len(merke.navn) * TEGNBREDDE
    if merke.til_venstre:
        return merke.x - 3 - lengde, merke.x - 3
    return merke.x + 3, merke.x + 3 + lengde


def _uten_overlapp(merker: tuple[Maanedsmerke, ...], bredde: int) -> tuple[Maanedsmerke, ...]:
    """Story 8.2c: navnene paa aksen som ville kommet borti hverandre paa
    smal skjerm, mister navnet, men ikke streken. Det regnes fra hoeyre, saa
    det siste navnet, naermest dagen grafen slutter paa, alltid staar.

    Gjennomgangen av 8.2c (BH1, ECH2): et navn som ville gaatt forbi hoeyre
    kant, staar til venstre for streken. Grensen NAVNEBREDDE er for den
    brede grafen og holder ikke for «september» paa den smale."""
    ut = [Maanedsmerke(m.x, m.navn, m.x + 3 + len(m.navn) * TEGNBREDDE > bredde) if m.navn else m for m in merker]
    grense = None
    for i in range(len(ut) - 1, -1, -1):
        if not ut[i].navn:
            continue
        fra, til = navneplass(ut[i])
        if grense is not None and til + NAVNELUFT > grense:
            ut[i] = Maanedsmerke(ut[i].x, "", ut[i].til_venstre)
        else:
            grense = fra
    return tuple(ut)


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


def _rutenett(lav: float, hoy: float, hoyde: int, linjer: int = 3, bunn: int = BUNN) -> tuple[Rutelinje, ...]:
    ut = []
    for i in range(linjer):
        verdi = lav + (hoy - lav) * i / (linjer - 1)
        ut.append(Rutelinje(y=_y(verdi, lav, hoy, hoyde, bunn), verdi=verdi))
    return tuple(ut)


def _forklaringen(linjer: tuple[tuple[str, str], ...], hoyde: int) -> tuple[Forklaring, ...]:
    """Story 8.2c: en linje i forklaringen for hver linje grafen har, i
    samme rekkefoelge som navnene staar i malen, i feltet under datoene."""
    foerste = hoyde - FORKLARING + FORKLARINGSLINJE - 4
    klasser = [klasse for klasse, punkter in linjer if punkter]
    return tuple(Forklaring(klasse, foerste + FORKLARINGSLINJE * i) for i, klasse in enumerate(klasser))


def _dagene(punkter: tuple[Punkt, ...], lav, hoy, bredde, hoyde, hoeyre, bunn) -> tuple[Dag, ...]:
    """Story 8.20a (del C): feltet og lappen for hver dag. Feltet gaar
    halvveis til dagen foer og etter, og lappen staar til hoeyre for punktet,
    eller til venstre naar den ellers gaar ut over tegneflaten, og aldri over
    eller under den. Gjennomgangen av 8.20a (ECH3): faar den ikke plass paa
    noen av sidene, som i den smale grafen, staar den over eller under
    punktet, saa den aldri dekker punktet den gjelder."""
    antall = len(punkter)
    steg = (bredde - VENSTRE - hoeyre) / (antall - 1)
    hoeyrekant = bredde - hoeyre
    dager = []
    for i, p in enumerate(punkter):
        x = _x(i, antall, bredde, hoeyre)
        y = _y(p.kurs, lav, hoy, hoyde, bunn)
        venstre = max(VENSTRE, x - steg / 2)
        bunnkant = hoyde - bunn
        if x + LAPPLUFT + LAPPBREDDE <= hoeyrekant:
            lapp_x = x + LAPPLUFT
            lapp_y = min(max(MARG_Y, y + LAPPLUFT), bunnkant - LAPPHOYDE)
        elif x - LAPPLUFT - LAPPBREDDE >= VENSTRE:
            lapp_x = x - LAPPLUFT - LAPPBREDDE
            lapp_y = min(max(MARG_Y, y + LAPPLUFT), bunnkant - LAPPHOYDE)
        else:
            lapp_x = min(max(VENSTRE, x - LAPPBREDDE / 2), hoeyrekant - LAPPBREDDE)
            under = y + LAPPLUFT
            lapp_y = under if under + LAPPHOYDE <= bunnkant else y - LAPPLUFT - LAPPHOYDE
        dager.append(
            Dag(
                dato=p.dato,
                x=x,
                y=y,
                kurs=p.kurs,
                snitt=p.ma50,
                y_snitt=_y(p.ma50, lav, hoy, hoyde, bunn) if p.ma50 is not None else None,
                felt_x=venstre,
                felt_bredde=min(hoeyrekant, x + steg / 2) - venstre,
                lapp_x=lapp_x,
                lapp_y=lapp_y,
            )
        )
    return tuple(dager)


def bygg_graf(
    punkter: tuple[Punkt, ...],
    bredde: int = BREDDE,
    hoyde: int = HOYDE,
    indeks: dict[date, float] | None = None,
    merker: str = MAANEDSNAVN,
    merket: date | None = None,
    smal: bool = False,
    signal: dict[date, tuple[int, str]] | None = None,
    alle: int = 3,
) -> Graf | None:
    """Koordinatene for kurs og MA50, og for indeksen naar den er gitt som
    {dato: verdi} (story 2.9c). None naar det ikke er noe aa tegne.

    Story 8.16: merker sier hvilke merker aksen faar (aksemerker), og merket
    er dagen som merkes, naar grafen har den.

    Story 8.2c: smal gir grafen paa smal skjerm, med SMAL_BREDDE og
    SMAL_HOYDE, og navnene paa linjene i forklaringen under datoene. Da
    gjelder ikke bredde og hoyde (gjennomgangen, BH8, ECH3)."""
    if len(punkter) < 2:
        return None

    hoeyre, bunn = HOEYRE, BUNN
    if smal:
        bredde, hoyde = SMAL_BREDDE, SMAL_HOYDE
        hoeyre, bunn = SMAL_HOEYRE, BUNN + FORKLARING
    omregnet = indeksverdier(punkter, indeks)
    lav, hoy = _spenn(punkter, tuple(omregnet.values()))
    kurslinje = _koordinater(punkter, lambda p: p.kurs, lav, hoy, bredde, hoyde, hoeyre, bunn)
    ma50linje = _koordinater(punkter, lambda p: p.ma50, lav, hoy, bredde, hoyde, hoeyre, bunn)
    indekslinje = _koordinater(punkter, lambda p: omregnet.get(p.dato), lav, hoy, bredde, hoyde, hoeyre, bunn)
    if smal:
        kursnavn = snittnavn = indeksnavn = None
        forklaring = _forklaringen((("kurs", kurslinje), ("snitt", ma50linje), ("indeks", indekslinje)), hoyde)
        aksen = _uten_overlapp(aksemerker(punkter, bredde, merker, hoeyre, tynn=False), bredde)
    else:
        kursnavn, snittnavn, indeksnavn = _navnene((kurslinje, ma50linje, indekslinje), bredde, hoyde)
        forklaring = ()
        aksen = aksemerker(punkter, bredde, merker)
    siste = _siste(kurslinje)
    # Story 8.16: punktet for dagen, regnet fra indeksen som de andre
    # punktene (gjennomgangen, BH11).
    punktet = None
    datoene = [p.dato for p in punkter]
    if merket in datoene:
        i = datoene.index(merket)
        punktet = Navn(_x(i, len(punkter), bredde, hoeyre), _y(punkter[i].kurs, lav, hoy, hoyde, bunn))
    # Story 8.8: signal er {dato: (styrke, retning)} for dagene som skilte seg
    # ut, lest fra vurdering (les_periode). Bare dager grafen har, får en prikk.
    signaldager = tuple(
        Signaldag(
            dato=d,
            x=_x(i, len(punkter), bredde, hoeyre),
            y=_y(punkter[i].kurs, lav, hoy, hoyde, bunn),
            retning=signal[d][1],
            styrke=signal[d][0],
            alle=signal[d][0] >= alle,
        )
        for i, d in enumerate(datoene)
        if signal and d in signal
    )

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
        maanedsmerker=aksen,
        rutenett=_rutenett(lav, hoy, hoyde, bunn=bunn),
        indekslinje=indekslinje,
        indeksstart=min(omregnet) if omregnet else None,
        indeksslutt=max(omregnet) if omregnet else None,
        merket=punktet,
        indeksnavn=indeksnavn,
        hoeyrefelt=hoeyre,
        bunnfelt=bunn,
        forklaring=forklaring,
        smal=smal,
        dager=_dagene(punkter, lav, hoy, bredde, hoyde, hoeyre, bunn),
        signaldager=signaldager,
    )
