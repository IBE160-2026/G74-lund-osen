"""Børsometeret - story 8.6, FR-106, designregler.md §3 og §4.

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: aksjene, de to
kursene og vurderingen for dagen kommer inn som argumenter. Siden leser dem
gjennom portene som finnes (AD-3), og ingen ny tabell trengs.

Én rute per aksje i lista, ordnet etter bransje i rekkefølgen i
designregler.md §4 (avgjørelsen 22.10 kl. 23:19). Fargen er endringen fra
børsdagen før (FR-101, endring_i_prosent), størrelsen er volumforholdet i den
lagrede vurderingen, og rammen er signalet. Signalet regnes aldri her, det
leses (AD-7). Snittet per bransje er snittet av endringen for aksjene i
bransjen som har en endring, og en bransje med én aksje merkes «1 aksje»
(FR-106). Antallet bransjer og aksjer telles fra lista, aldri fra et fast tall
(føringen 30.09 under AD-21).

Rammen (designregler §3, gjennomgangen VG1): gult betyr 3 av 3 på siste
børsdag og står også når siden viser en annen dag, også en dag uten vurdering
eller uten kurs (gruppens svar 23.10 kl. 09:24, a). 2 av 3 merkes bare for
siste børsdag.

Story 8.6b (avgjørelsen 24.10 kl. 11:54): søylene står bare på oversikten,
og hovedindeksen står som et tall i linja «Mål mot børsen», med endringen
for dagen som vises. Rutene er et fylt kart i to nivåer, som på tavla:
bransjene som felt etter summen av vektene, og aksjene inne i feltet,
squarified og i prosent (kart og squarify nederst).

Gruppens svar 26.10 kl. 13:00 (a): i kartet står bransjene og rutene i den
rekkefølgen squarify legger dem, den største først, så Tab følger kartet.
Tabellen under beholder rekkefølgen i designregler §4 (bygg_boersometer).
"""

from dataclasses import dataclass
from datetime import date

from hjelpetekster import ANTALL_SJEKKER
from hovedindeks import indeksendring
from kursdata import Aksje, Kursrad
from markedsoversikt import IKKE_VURDERT, endring_i_prosent, grunn_med_tall, les_tilstand
from signalberegning import STANDARD, Parametre
from tallformat import avrundet, dato, desimaler_mot_grense, tall, ukedag
from tilstand import Art
from vurderingsdata import Grunn, Vurdering

# De 13 bransjene i designregler.md §4, i rekkefølgen tabellen står.
BRANSJER = (
    "Energi",
    "Finans",
    "Industri",
    "Materialer",
    "Shipping",
    "Telekom",
    "Sjømat",
    "Konsum",
    "Forbruk",
    "Teknologi",
    "Helse",
    "Eiendom",
    "Kraft",
)

# Størrelsen på ruta, etter volumforholdet (spesifikasjonen 8.6, «Avgjort»).
LAV, VANLIG, HOEY = "lav", "vanlig", "hoey"
# Ordet for størrelsen, i ruta for skjermleser og i tabellen.
VOLUMORD = {LAV: "lavt", VANLIG: "vanlig", HOEY: "høyt"}
# Rammen, etter styrken (designregler.md §3).
GUL, MOERK = "gul", "moerk"
UTEN_DATA = "Uten data"

# Story 8.6b, c: fem fargetrinn etter endringen slik den vises, med grensene i
# prosent. Navnene er klassene i malen og fargene i :root i stil.css.
GRENSE_LYS = 0.5
GRENSE_STERK = 2.0
NOEYTRAL, LYS_OPP, LYS_NED, STERK_OPP, STERK_NED = "noeytral", "lys-opp", "lys-ned", "opp", "ned"


@dataclass(frozen=True)
class Rute:
    """Én aksje i børsometeret.

    styrke er fra vurderingen for dagen som vises, siste_styrke fra siste
    børsdag. er_siste sier om dagen som vises, er siste børsdag."""

    aksje: Aksje
    endring: float | None
    volumforhold: float | None
    styrke: int | None
    tekst: str | None
    uten_data: bool = False
    siste_styrke: int | None = None
    er_siste: bool = True

    @property
    def stoerrelse(self) -> str:
        return stoerrelse(self.volumforhold)

    @property
    def fargetrinn(self) -> str | None:
        return fargetrinn(self.endring)

    @property
    def volumord(self) -> str | None:
        return None if self.volumforhold is None else VOLUMORD[self.stoerrelse]

    @property
    def volum_vist(self) -> str | None:
        return None if self.volumforhold is None else vis_volumforhold(self.volumforhold)

    @property
    def ikke_vurdert(self) -> bool:
        """Ruta sier «ikke vurdert», og siden får fotnoten (story 3.4d,
        gruppens svar 23.10 kl. 11:44, b). En rute uten kurs sier «Uten
        data»."""
        return self.tekst == IKKE_VURDERT

    @property
    def ramme(self) -> str | None:
        if self.er_siste:
            return ramme(self.styrke)
        # Gruppens svar 23.10 kl. 09:24 (a): gult også en dag uten vurdering
        # eller uten kurs.
        return GUL if self.siste_styrke == ANTALL_SJEKKER else None


@dataclass(frozen=True)
class Bransje:
    """En bransje med rutene sine og snittet av endringen."""

    navn: str
    ruter: tuple[Rute, ...]

    @property
    def antall(self) -> int:
        return len(self.ruter)

    @property
    def snitt(self) -> float | None:
        return snitt(self.ruter)


def stoerrelse(volumforhold: float | None, p: Parametre = STANDARD) -> str:
    """Tre trinn: under 1, fra 1 til og med volumfaktor, og over volumfaktor,
    som gir utslag på interesse (signalberegning.interesse, «>»). Uten
    volumforhold vanlig størrelse."""
    if volumforhold is None:
        return VANLIG
    if volumforhold > p.volumfaktor:
        return HOEY
    if volumforhold < 1:
        return LAV
    return VANLIG


def fargetrinn(endring: float | None) -> str | None:
    """Fem trinn etter endringen slik den vises, to desimaler (8.6b, c):
    under GRENSE_LYS i tallverdi nøytral, fra GRENSE_LYS lys, og fra
    GRENSE_STERK sterk. 0,50 % er lys, og 2,00 % er sterk. None uten endring."""
    if endring is None:
        return None
    vist = avrundet(endring, "endring")
    if vist >= GRENSE_STERK:
        return STERK_OPP
    if vist <= -GRENSE_STERK:
        return STERK_NED
    if vist >= GRENSE_LYS:
        return LYS_OPP
    if vist <= -GRENSE_LYS:
        return LYS_NED
    return NOEYTRAL


def trinnforklaringer() -> list[tuple[str, str]]:
    """Trinnene til «Hva fargene betyr», fra størst fall til størst
    stigning, med tallene fra grensene (regel 21). Begge grensene er
    prosent, så begge formateres som «grense» (gjennomgangen 26.10, BH7)."""
    lys, sterk = tall(GRENSE_LYS, "grense", desimaler=1), tall(GRENSE_STERK, "grense")
    return [
        (STERK_NED, f"Ned {sterk} eller mer"),
        (LYS_NED, f"Ned fra {lys} til under {sterk}"),
        (NOEYTRAL, f"Under ±{tall(GRENSE_LYS, 'grense', desimaler=1)}"),
        (LYS_OPP, f"Opp fra {lys} til under {sterk}"),
        (STERK_OPP, f"Opp {sterk} eller mer"),
    ]


def vis_volumforhold(volumforhold: float, p: Parametre = STANDARD) -> str:
    """Volumforholdet med så mange desimaler, minst to, at det skilles fra
    grensene 1 og volumfaktor, som på aksjesiden (gjennomgangen, BH2/ECH4)."""
    antall = max(
        desimaler_mot_grense(volumforhold, 1, minst=2), desimaler_mot_grense(volumforhold, p.volumfaktor, minst=2)
    )
    return tall(volumforhold, "forhold", antall)


def ramme(styrke: int | None) -> str | None:
    """Gul ved 3 av 3, mørk ved 2 av 3, ellers ingen (designregler.md §3).
    Gjelder siste børsdag; Rute.ramme sier hva som gjelder en annen dag."""
    if styrke == ANTALL_SJEKKER:
        return GUL
    if styrke == ANTALL_SJEKKER - 1:
        return MOERK
    return None


def snitt(ruter: tuple[Rute, ...] | list[Rute]) -> float | None:
    """Snittet av endringen for rutene som har en endring, None uten noen."""
    endringer = [r.endring for r in ruter if r.endring is not None]
    if not endringer:
        return None
    return sum(endringer) / len(endringer)


def bygg_rute(
    aksje: Aksje,
    kurser: list[Kursrad],
    innhold: Vurdering | Grunn | None,
    dato: date,
    idag: date,
    siste_styrke: int | None = None,
    er_siste: bool = True,
    p: Parametre = STANDARD,
) -> Rute:
    """Ruta for én aksje på dato. kurser er kursradene til og med dato. En
    aksje uten kurs på dato står med «Uten data», og med gult bare ved 3 av 3
    på siste børsdag."""
    if not kurser or kurser[-1].dato != dato:
        return Rute(
            aksje=aksje,
            endring=None,
            volumforhold=None,
            styrke=None,
            tekst=UTEN_DATA,
            uten_data=True,
            siste_styrke=siste_styrke,
            er_siste=er_siste,
        )
    utfall, tekst = les_tilstand(innhold, dato, idag)
    # Story 8.2a, d (gruppens svar 24.10 kl. 11:29): ruta sier hvorfor, med
    # samme tall som aksjesiden for dagen, regnet av kursene til og med dato.
    tekst = grunn_med_tall(utfall, tekst, len(kurser), p)
    vurdering = utfall.innhold if utfall is not None and utfall.art is Art.SVAR else None
    return Rute(
        aksje=aksje,
        endring=endring_i_prosent(kurser[-2:]),
        volumforhold=vurdering.volumforhold if vurdering else None,
        styrke=vurdering.styrke if vurdering else None,
        tekst=tekst,
        siste_styrke=siste_styrke,
        er_siste=er_siste,
    )


def bygg_boersometer(ruter: list[Rute]) -> list[Bransje]:
    """Rutene gruppert etter bransje, i rekkefølgen i designregler.md §4, og
    i lista sin rekkefølge inne i hver bransje. Bare bransjene som har en
    aksje i lista, og en ukjent bransje sist."""
    grupper: dict[str, list[Rute]] = {}
    for rute in ruter:
        grupper.setdefault(rute.aksje.sektor, []).append(rute)
    rekkefoelge = sorted(grupper, key=lambda navn: (BRANSJER.index(navn) if navn in BRANSJER else len(BRANSJER), navn))
    return [Bransje(navn=navn, ruter=tuple(grupper[navn])) for navn in rekkefoelge]


def dagen_foer(datoer: list[date], dag: date) -> date | None:
    """Datoen før dag blant kursdatoene for aksjene i lista, den endringen i
    rutene regnes fra (8.6b, b). None når dag er den første."""
    foer = [d for d in datoer if d < dag]
    return max(foer) if foer else None


# Gjennomgangen 26.10 (ECH4): ukedagen sier hvilken dag bare når den er i
# uka før dagen som vises. Er børsdagen før mer enn 6 dager før, står datoen.
UKEDAG_INNTIL = 6


def vis_dagen_foer(foer: date | None, dag: date, i_aar: int) -> str:
    """Børsdagen før i linja «Mål mot børsen»: ukedagen når den er høyst
    UKEDAG_INNTIL dager før dag, ellers datoen, og «børsdagen før» når dag
    er den første (8.6b, b)."""
    if foer is None:
        return "børsdagen før"
    if (dag - foer).days > UKEDAG_INNTIL:
        return dato(foer, i_aar)
    return ukedag(foer)


def indeks_for_dagen(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen i hovedindeksen for dag, mot børsdagen før etter kalenderen
    (hovedindeks.indeksendring). None når indeksen ikke har en rad for dag,
    eller ikke for børsdagen før (8.6b, b)."""
    til = [rad for rad in serie if rad.dato <= dag]
    if not til or til[-1].dato != dag:
        return None
    return indeksendring(til)


# --- Kartet (8.6b, d) --------------------------------------------------------

# En aksje uten volumforhold får vekten 1, det vanlige. Vekten holdes mellom
# MINSTE_VEKT og STOERSTE_VEKT, så hver aksje får en rute det går an å trykke
# på, uten at kartet blir mange skjermer høyt (målt 26.10, spesifikasjonen).
MINSTE_VEKT = 0.5
STOERSTE_VEKT = 3.0
# Ingen rute mindre enn 44 × 44 px, med 2 px hvitt på hver side.
MINSTE_RUTE = 44
KANT = 2
# Overskriften i feltet, i px ved bredden flaten regnes ved (Flate.bredde).
# Den krymper med kartet: ved 288 px er den 24 × 288/358 ≈ 19,3 px, og linja
# i den er 16 px (gjennomgangen 26.10, BH, og test_overskriften_har_plass_til_linja).
OVERSKRIFT = 24
# Gruppens svar 26.10 kl. 13:00 (b): navnet forsvinner aldri helt. Et felt er
# minst så bredt, ved den minste bredden flaten brukes på, at overskriften har
# plass til INNRYKK på hver side, symbolet, mellomrommet og MINSTE_NAVN, som er
# min-width for navnet i stil.css: én bokstav og «…».
INNRYKK = 2
SYMBOL = 14
MELLOMROM = 4
MINSTE_NAVN = 24
MINSTE_FELT = 2 * INNRYKK + SYMBOL + MELLOMROM + MINSTE_NAVN
# Høyden økes med 2 % til hver rute er stor nok. Målt 26.10 (gjennomgangen,
# BH10): 1,02 gir et kart om lag 1 % høyere enn å øke med 0,2 % i median,
# 1,05 om lag 2 %, og 1,01 under halvparten av 1,02 på nesten dobbelt så lang tid
# (spesifikasjonen 8.6b, linja om BH10 under triagen).
VEKST = 1.02
MEST_VEKST = 600


@dataclass(frozen=True)
class Flate:
    """Et oppsett av kartet. Kartet regnes ved bredde i px; forhold er høyden
    mot bredden ved start, og minste er den minste bredden flaten brukes på.
    tekst er klassen og bredden tekstnivået regnes ved, for hvert spenn av
    vinduer flaten brukes på (gruppens svar 26.10 kl. 13:00, c, og 13:07, e)."""

    navn: str
    bredde: float
    forhold: float
    minste: float
    tekst: tuple[tuple[str, float], ...]


# Bred for vinduer bredere enn 760 px (innholdet minst 729 px, og 712 px med
# et rullefelt på 17 px, gjennomgangen 26.10, ECH), og smal for
# 760 px og smalere, regnet ved 390 px (innholdet 358 px), som instruksjonen
# sier. Stilen velger med @media, og hver rute har plassen i begge.
# Tekstnivået regnes for den synlige ruta innenfor KANT (gjennomgangen 26.10,
# VG, ECH og BH), ved den minste bredden i hvert spenn av vinduer, med 16 px
# på hver side: 1008 px fra 1080 px, full bredde (svaret kl. 13:07, e), 712 px
# fra 761 px, 328 px fra 360 px (svaret kl. 13:00, c), og 288 px under det,
# et vindu 320 px bredt. Stilen velger klassen med @media.
BRED = Flate("bred", 712, 0.5, 712, (("bred", 712), ("bredest", 1008)))
SMAL = Flate("smal", 358, 1.2, 288, (("smal", 328), ("smalest", 288)))
FLATENE = (BRED, SMAL)


@dataclass(frozen=True)
class Plass:
    """Et rektangel i prosent av det som rommer det."""

    x: float
    y: float
    b: float
    h: float


@dataclass(frozen=True)
class Kartrute:
    """En rute i kartet: plassen i prosent av feltet under overskriften per
    flate, og hvor mye tekst som står synlig per klasse i Flate.tekst (0
    ingen, 1 symbolet, 2 også endringen, 3 også merket og grunnen)."""

    rute: Rute
    vekt: float
    plass: dict[str, Plass]
    nivaa: dict[str, int]


@dataclass(frozen=True)
class Kartfelt:
    """Feltet for en bransje: plassen i prosent av kartet, og høyden på
    overskriften i prosent av feltet, per flate."""

    bransje: Bransje
    vekt: float
    plass: dict[str, Plass]
    topp: dict[str, float]
    ruter: tuple[Kartrute, ...]


@dataclass(frozen=True)
class Kart:
    """Feltene, og rutene i hvert felt, i den rekkefølgen squarify legger
    dem (rekkefoelge), og høyden mot bredden per flate. Rekkefølgen er den
    samme på begge flatene, fordi den bare avhenger av vektene."""

    felt: tuple[Kartfelt, ...]
    forhold: dict[str, float]


def vekt(rute: Rute) -> float:
    """Volumforholdet, 1 uten, og mellom MINSTE_VEKT og STOERSTE_VEKT."""
    forhold = 1.0 if rute.volumforhold is None else rute.volumforhold
    return min(max(forhold, MINSTE_VEKT), STOERSTE_VEKT)


def _verste(arealer: list[float], side: float) -> float:
    """Det verste forholdet mellom sidene i en rad med arealene langs side."""
    sum_ = sum(arealer)
    return max(max(side * side * a / (sum_ * sum_), sum_ * sum_ / (side * side * a)) for a in arealer)


def rekkefoelge(vekter: list[float]) -> list[int]:
    """Indeksene i den rekkefølgen squarify legger dem: den største først,
    og ved lik vekt i rekkefølgen de kom (gruppens svar 26.10 kl. 13:00, a)."""
    return sorted(range(len(vekter)), key=lambda i: -vekter[i])


def squarify(
    vekter: list[float], x: float, y: float, b: float, h: float, minst: float = 0.0
) -> list[tuple[float, float, float, float]]:
    """Rektanglene for vektene i rektangelet (x, y, b, h), i samme rekkefølge
    som vektene, med areal etter vekten og uten overlapp (Bruls, Huizing og
    van Wijk, «Squarified Treemaps», 2000). Den største legges først, og en
    rad fylles langs den korteste siden så lenge sidene blir likere.

    Med minst tar raden også hensyn til minstemålet: en rad tynnere enn minst
    får neste med, neste kommer ikke med når den ville gjort en rute i raden
    kortere enn minst, og resten kommer med når det som er igjen etter raden,
    ville blitt tynnere enn minst."""
    if not vekter:
        return []
    totalt = sum(vekter)
    rest = [(i, vekter[i] / totalt * b * h) for i in rekkefoelge(vekter)]
    ut: list[tuple[float, float, float, float]] = [(0.0, 0.0, 0.0, 0.0)] * len(vekter)
    while rest:
        side = min(b, h)
        rad = [rest[0]]
        while len(rad) < len(rest):
            neste = rad + [rest[len(rad)]]
            arealer = [a for _, a in neste]
            # Blir det som er igjen etter raden tynnere enn minst, kommer
            # resten med i raden, så det ikke blir en tynn stripe til slutt.
            if minst and (b * h - sum(a for _, a in rad)) / side < minst:
                rad = neste
                continue
            if minst and min(arealer) / sum(arealer) * side < minst:
                break
            tynn = minst and sum(a for _, a in rad) / side < minst
            if not tynn and _verste(arealer, side) > _verste([a for _, a in rad], side):
                break
            rad = neste
        sum_ = sum(a for _, a in rad)
        if b >= h:
            bredde = b if len(rad) == len(rest) else sum_ / h
            yy = y
            for i, a in rad:
                ut[i] = (x, yy, bredde, a / sum_ * h)
                yy += a / sum_ * h
            x, b = x + bredde, b - bredde
        else:
            hoeyde = h if len(rad) == len(rest) else sum_ / b
            xx = x
            for i, a in rad:
                ut[i] = (xx, y, a / sum_ * b, hoeyde)
                xx += a / sum_ * b
            y, h = y + hoeyde, h - hoeyde
        rest = rest[len(rad) :]
    return ut


def _nivaa_ved(flate: Flate, bredde: float, rb: float, rh: float, symbol: str) -> int:
    """Tekstnivået for plassen rb × rh ved flate.bredde, regnet for den
    synlige ruta når kartet er bredde px bredt."""
    skala = bredde / flate.bredde
    return tekstnivaa(rb * skala - 2 * KANT, rh * skala - 2 * KANT, symbol)


def tekstnivaa(b: float, h: float, symbol: str) -> int:
    """Hvor mye tekst ruta har plass til, i px (spesifikasjonen 8.6b, «Navnet»)."""
    if b < 9 * len(symbol) + 10 or h < 40:
        return 0
    if b < 74 or h < 60:
        return 1
    if b < 96 or h < 88:
        return 2
    return 3


def _legg_ut(bransjer: list[Bransje], bredde: float, hoeyde: float, minste_felt: float = 0.0) -> list | None:
    """Feltene og rutene i px, eller None når en rute er mindre enn
    MINSTE_RUTE med KANT på hver side, et felt ikke har plass under
    overskriften, eller et felt er smalere enn minste_felt."""
    minst = MINSTE_RUTE + 2 * KANT
    feltbredde = max(minst, minste_felt)
    feltvekter = [sum(vekt(r) for r in bransje.ruter) for bransje in bransjer]
    ut = []
    for bransje, felt in zip(bransjer, squarify(feltvekter, 0, 0, bredde, hoeyde, feltbredde), strict=True):
        fx, fy, fb, fh = felt
        if fh - OVERSKRIFT < minst or fb < feltbredde:
            return None
        ruter = squarify([vekt(r) for r in bransje.ruter], fx, fy + OVERSKRIFT, fb, fh - OVERSKRIFT, minst)
        if any(rb < minst or rh < minst for _, _, rb, rh in ruter):
            return None
        ut.append((felt, ruter))
    return ut


def kart(bransjer: list[Bransje], flatene: tuple[Flate, ...] = FLATENE) -> Kart:
    """Kartet i to nivåer, regnet for hver flate ved den minste bredden, med
    høyden økt til hver rute er stor nok, og gjort om til prosent."""
    lagt: dict[str, list] = {}
    forhold: dict[str, float] = {}
    for flate in flatene:
        hoeyde = flate.bredde * flate.forhold
        for _ in range(MEST_VEKST):
            # MINSTE_FELT gjelder ved den minste bredden flaten brukes på.
            utlagt = _legg_ut(bransjer, flate.bredde, hoeyde, MINSTE_FELT * flate.bredde / flate.minste)
            if utlagt is not None:
                break
            hoeyde *= VEKST
        else:
            raise ValueError(f"Kartet fikk ikke plass til rutene på flaten {flate.navn}")
        lagt[flate.navn] = utlagt
        forhold[flate.navn] = hoeyde / flate.bredde
    felt = []
    for n, bransje in enumerate(bransjer):
        plass: dict[str, Plass] = {}
        topp: dict[str, float] = {}
        ruteplass: list[dict[str, Plass]] = [{} for _ in bransje.ruter]
        nivaa: list[dict[str, int]] = [{} for _ in bransje.ruter]
        for flate in flatene:
            hoeyde = forhold[flate.navn] * flate.bredde
            (fx, fy, fb, fh), ruter = lagt[flate.navn][n]
            plass[flate.navn] = Plass(
                fx / flate.bredde * 100, fy / hoeyde * 100, fb / flate.bredde * 100, fh / hoeyde * 100
            )
            topp[flate.navn] = OVERSKRIFT / fh * 100
            kropp = fh - OVERSKRIFT
            # Gjennomgangen 26.10 (ECH): rutene ble lagt fra fy + OVERSKRIFT,
            # så den summen trekkes fra. ry - fy - OVERSKRIFT kunne bli -2e-14,
            # og malen skrev da «-0.000%».
            start = fy + OVERSKRIFT
            for i, (rx, ry, rb, rh) in enumerate(ruter):
                ruteplass[i][flate.navn] = Plass(
                    (rx - fx) / fb * 100, (ry - start) / kropp * 100, rb / fb * 100, rh / kropp * 100
                )
                for klasse, bredde in flate.tekst:
                    nivaa[i][klasse] = _nivaa_ved(flate, bredde, rb, rh, bransje.ruter[i].aksje.symbol)
        kartruter = [
            Kartrute(rute=r, vekt=vekt(r), plass=ruteplass[i], nivaa=nivaa[i]) for i, r in enumerate(bransje.ruter)
        ]
        felt.append(
            Kartfelt(
                bransje=bransje,
                vekt=sum(vekt(r) for r in bransje.ruter),
                plass=plass,
                topp=topp,
                ruter=tuple(kartruter[i] for i in rekkefoelge([kr.vekt for kr in kartruter])),
            )
        )
    # Gruppens svar 26.10 kl. 13:00 (a): HTML-en følger kartet, så Tab gjør det.
    return Kart(felt=tuple(felt[i] for i in rekkefoelge([f.vekt for f in felt])), forhold=forhold)
