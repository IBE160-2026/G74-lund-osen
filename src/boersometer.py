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

import math
from dataclasses import dataclass, replace
from datetime import date

from hjelpetekster import ANTALL_SJEKKER
from hovedindeks import indeksendring
from kursdata import Aksje, Kursrad
from markedsoversikt import IKKE_VURDERT, endring_i_prosent, grunn_med_tall, les_tilstand, periodeendring
from signalberegning import STANDARD, Parametre
from tallformat import avrundet, dato, tall, ukedag
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
# Story 8.26 (gruppens ønske 11.11 kl. 17:44, tillegg 2): «Uten data» sa ikke
# hvorfor. Ruta sier «Ingen kurs», kort nok til grensen for store ruter
# (STOR), og tabellen og title sier «Ingen kurser ennå», som oversikten.
UTEN_DATA = "Ingen kurs"

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
    # Gjennomgangen av 8.26 (ECH4): uten en eneste kurs til og med dagen, ikke
    # bare uten kurs på dagen. Bare da sier tabellen «Ingen kurser ennå».
    aldri_kurs: bool = False
    siste_styrke: int | None = None
    er_siste: bool = True
    # Story 8.17b (gruppens svar 23.10 kl. 12:35, b): ved en periode er
    # endringen for perioden, og rutene er like store, fordi volumet mot
    # vanlig gjelder én dag. fra er dagen serien begynner, når den begynner
    # etter den første kursen i perioden.
    lik_stoerrelse: bool = False
    fra: date | None = None

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
    def uten_styrke(self) -> str | None:
        """«ikke vurdert» for en rute med kurs, men uten styrke, ellers None.
        Gruppens svar 04.11 kl. 20:53 og 20:56, 2: det står på linja der
        styrken ellers står. Ruter uten data er som før."""
        return IKKE_VURDERT if self.styrke is None and not self.uten_data else None

    @property
    def grunn(self) -> str | None:
        """Teksten under linja for styrken. Svar 2: «ikke vurdert» står bare
        én gang i ruta, så teksten står ikke når den er det samme."""
        if self.uten_data or self.ikke_vurdert:
            return None
        return self.tekst

    @property
    def annen_grunn(self) -> bool:
        """Ruta sier «ikke vurdert» av en annen grunn enn at signalet ikke
        er lagret, som for kort historikk, og siden får fotnoten om at
        grunnen står i tabellen og på aksjesiden (gruppens svar 05.11 kl.
        09:34, 1)."""
        return self.uten_styrke is not None and bool(self.grunn)

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

    @property
    def tillegg(self) -> str:
        """Linja under navnet i kartet (story 8.20b, U97): antallet og
        snittet, som i boersometer.html, og bare antallet uten snitt."""
        antall = f"{self.antall} {'aksje' if self.antall == 1 else 'aksjer'}"
        if self.antall == 1 or self.snitt is None:
            return antall
        return f"{antall} · snitt {tall(self.snitt, 'endring')}"


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


def _noeyaktig(grense: float) -> int:
    """Færrest desimaler, minst én, som viser grensen nøyaktig: 0,5 og 0,25."""
    return next((n for n in range(1, 7) if round(grense, n) == grense), 6)


def trinnforklaringer() -> list[tuple[str, str]]:
    """Trinnene til kortet «Slik leser du børsometeret» (story 8.20b), fra størst fall til størst
    stigning, med tallene fra grensene (regel 21). Begge grensene er
    prosent, så begge formateres som «grense» (gjennomgangen 26.10, BH7),
    med så mange desimaler at grensen står nøyaktig (ECH)."""
    lys, sterk = tall(GRENSE_LYS, "grense", desimaler=_noeyaktig(GRENSE_LYS)), tall(GRENSE_STERK, "grense")
    return [
        (STERK_NED, f"Ned {sterk} eller mer"),
        (LYS_NED, f"Ned fra {lys} til under {sterk}"),
        (NOEYTRAL, f"Under ±{tall(GRENSE_LYS, 'grense', desimaler=1)}"),
        (LYS_OPP, f"Opp fra {lys} til under {sterk}"),
        (STERK_OPP, f"Opp {sterk} eller mer"),
    ]


def skalagrenser() -> list[str]:
    """Grensene under skalaen i kortet «Slik leser du børsometeret» (story
    8.20b, U99), fra størst fall til størst stigning, med tallene fra
    grensene som i trinnforklaringer (regel 21)."""
    lys, sterk = tall(GRENSE_LYS, "grense", desimaler=_noeyaktig(GRENSE_LYS)), tall(GRENSE_STERK, "grense")
    return [f"-{sterk}", f"-{lys}", f"+{lys}", f"+{sterk}"]


def vis_volumforhold(volumforhold: float, p: Parametre = STANDARD) -> str:
    """Volumforholdet med to desimaler - story 8.23 (A4, brukertesten 10.11).

    Før stod flere desimaler når to ville rundet til en grense (1 og
    volumfaktor, gjennomgangen BH2/ECH4). Nå er det alltid to, og et tall
    som ville rundet til eller over en grense fra den andre siden, rundes
    mot siden det står på (1,4996 blir 1,49, og 0,998 blir 0,99), så tallet
    og ordet (stoerrelse) aldri sier ulikt."""
    vist = round(volumforhold, 2)
    # Gjennomgangen (BH11, ECH5): bare når ordet for det viste tallet ville
    # blitt et annet enn ordet for målingen, så 1,0004 står som 1,00 (vanlig).
    if stoerrelse(vist, p) != stoerrelse(volumforhold, p):
        vist = math.floor(volumforhold * 100) / 100 if volumforhold < vist else math.ceil(volumforhold * 100) / 100
    return tall(vist, "forhold", 2)


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
    aksje uten kurs på dato står med «Ingen kurs» (var «Uten data»), og med gult bare ved 3 av 3
    på siste børsdag."""
    if not kurser or kurser[-1].dato != dato:
        return Rute(
            aksje=aksje,
            endring=None,
            volumforhold=None,
            styrke=None,
            tekst=UTEN_DATA,
            uten_data=True,
            aldri_kurs=not kurser,
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


def med_perioden(rute: Rute, serie: list[Kursrad], start: date, siste: date) -> Rute:
    """Ruta ved en periode - story 8.17b (gruppens svar 23.10 kl. 12:35, b).
    Endringen er fra start, dagen den første kursen i perioden er fra, til
    siste børsdag, regnet som i oversikten (periodeendring), og ruta er like
    stor som de andre. Signalet og rammen er siste børsdag, som før. En rute
    uten kurs siste børsdag står med «Ingen kurs» (var «Uten data»)."""
    if rute.uten_data:
        return replace(rute, lik_stoerrelse=True)
    utfall = periodeendring(serie, start, siste)
    endring, fra = utfall if utfall is not None else (None, None)
    return replace(rute, endring=endring, fra=fra, lik_stoerrelse=True)


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
# Den krymper med kartet: ved 288 px er den 40 × 288/358 ≈ 32,2 px, og de to
# linjene i den er 16 og 14 px (gjennomgangen 26.10, BH, og
# test_overskriften_har_plass_til_linja). Story 8.20b (U97, spørsmål 14 d):
# antallet og snittet står på linje to og skjules aldri.
OVERSKRIFT = 40
# Gruppens svar 26.10 kl. 13:00 (b): navnet forsvinner aldri helt. Et felt er
# minst så bredt, ved den minste bredden flaten brukes på, at overskriften har
# plass til INNRYKK på hver side, symbolet, mellomrommet og MINSTE_NAVN, som er
# min-width for navnet i stil.css: én bokstav og «…».
INNRYKK = 2
SYMBOL = 14
MELLOMROM = 4
MINSTE_NAVN = 24
MINSTE_FELT = 2 * INNRYKK + SYMBOL + MELLOMROM + MINSTE_NAVN
# Story 8.20b (U97): linja med antallet og snittet er 12 px, og hvert felt er
# minst så bredt at hele linja står, med TILLEGG_EM per tegn. Tallene har
# like brede sifre, og 0,55 em er over det bredeste tegnet i linja målt i Edge.
TILLEGGSKRIFT = 12
TILLEGG_EM = 0.55


def tilleggsbredde(bransje: "Bransje") -> float:
    """Bredden feltet må ha for linja med antallet og snittet (U97)."""
    return 2 * INNRYKK + TILLEGG_EM * TILLEGGSKRIFT * len(bransje.tillegg)


# Høyden økes med 2 % til hver rute er stor nok og hvert felt minst
# MINSTE_FELT bredt. Grunnen er målt 26.10 med MINSTE_FELT (gjennomgangen,
# BH10): med 1,02 ble kartet under 2 % høyere enn nødvendig for 95 av 100
# dager, på under 2 ms. Tallene står i spesifikasjonen 8.6b, i linja om BH10
# under triagen.
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
    ingen, 1 symbolet, 2 også endringen, 3 også merket og grunnen). styrke
    er klassene der ruta står på nivå 2 og har plass til styrken under
    endringen (gruppens svar 04.11 kl. 19:21), og en annen dag ikke har gul
    ramme (svaret kl. 20:53 og 20:56, 1). For en rute uten styrke er det
    klassene der «ikke vurdert» har plass (svar 2). grunn er klassene der
    ruta står på nivå 3 og har plass til hele grunnen (gjennomgangen av
    svar 2, ECH1). Nivå 4 er en stor rute som i designforslaget (gruppens
    svar 04.11 kl. 22:23, 1): der står styrken, grunnen og merket i
    klassene i styrke, grunn og merke, og navnet i klassene i navn. En gul
    rute en annen dag viser merket i stedet for navnet når merket ikke får
    plass under det (gruppens svar 05.11 kl. 14:29, 1)."""

    rute: Rute
    vekt: float
    plass: dict[str, Plass]
    nivaa: dict[str, int]
    styrke: frozenset[str] = frozenset()
    grunn: frozenset[str] = frozenset()
    merke: frozenset[str] = frozenset()
    navn: frozenset[str] = frozenset()


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


def annen_grunn_i_kartet(kartet: Kart) -> frozenset[str] | None:
    """Fotnoten for en annen grunn (gruppens svar 05.11 kl. 09:34, 1): None
    når ingen rute i kartet sier «ikke vurdert» av en annen grunn, også når
    kartet er tomt, og ellers klassene i Flate.tekst der minst én av dem
    viser det for øyet, på nivå 3 eller på nivå 2 med plass til linja.
    Gjennomgangen (ECH1): stilen skjuler fotnoten for øyet i de andre
    klassene, som teksten i en rute, så skjermleseren leser begge."""
    ruter = [r for felt in kartet.felt for r in felt.ruter if r.rute.annen_grunn]
    if not ruter:
        return None
    return frozenset(
        klasse
        for r in ruter
        for klasse, nivaa in r.nivaa.items()
        if nivaa == 3 or (nivaa in (2, 4) and klasse in r.styrke)
    )


def vekt(rute: Rute) -> float:
    """Volumforholdet, 1 uten, og mellom MINSTE_VEKT og STOERSTE_VEKT.
    Story 8.17b: 1 for alle ved en periode (lik_stoerrelse)."""
    if rute.lik_stoerrelse:
        return 1.0
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


def _nivaa_ved(
    flate: Flate, bredde: float, rb: float, rh: float, rute: Rute, stor: bool = True
) -> tuple[int, bool, bool, bool, bool]:
    """Tekstnivået for plassen rb × rh ved flate.bredde, regnet for den
    synlige ruta når kartet er bredde px bredt, om styrken står på nivå 2
    eller 4, om hele grunnen står på nivå 3 eller 4, om merket står på
    nivå 4, og om navnet står på nivå 4. Nivå 4 er en stor rute (gruppens
    svar 04.11 kl. 22:23, 1). Der står styrken en annen dag i en gul rute
    bare med merket, som på nivå 2 (svaret 04.11 kl. 20:53 og 20:56, 1), og
    merket står i stedet for navnet når det ikke får plass under det
    (gruppens svar 05.11 kl. 14:29, 1). Får merket ikke plass der heller,
    er ruta ikke stor. Med stor=False er ingen rute stor (svar 2 kl. 14:29:
    store ruter bare fra 1079 px, STORE_KLASSER)."""
    skala = bredde / flate.bredde
    b, h = rb * skala - 2 * KANT, rh * skala - 2 * KANT
    nivaa = tekstnivaa(b, h, rute.aksje.symbol)
    if stor and nivaa == 3 and storplass(rute, b, h):
        linjene = _stor_linjer(rute, b, h)
        if linjene is not None:
            navn, merke, grunn = linjene
            styrke = not rute.uten_data and (merke or not (rute.ramme == GUL and not rute.er_siste))
            return 4, styrke, grunn, merke, navn
    return nivaa, nivaa == 2 and styrkelinje(rute, b, h), nivaa == 3 and grunnplass(rute, b, h), False, False


# Bredden og høyden ruta må ha for nivå 3, med teksten på 14 px.
NIVAA_3 = (126, 106)
# Gruppens svar 04.11 kl. 19:21: styrken har sin egen, lavere grense, plass
# til én linje til under symbolet og endringen. Regnet for 14 px med ringen
# («3 av 3» i pillen) og den gule rammen, og målt i Edge (spesifikasjonen
# 8.2b, «Rettet 04.11 kl. 19:21», og test_styrkens_grense_er_regnet_fra_stilen).
STYRKE = (81, 75)
# Gruppens svar 04.11 kl. 20:53 og 20:56, 2: «ikke vurdert» på linja der
# styrken ellers står, med en grense regnet for 14 px som STYRKE: den gule
# rammen, luften, symbolet, endringen og teksten uten ring
# (test_grensen_for_ikke_vurdert_er_regnet_fra_stilen).
IKKE_VURDERT_PLASS = (104, 69)
# Gjennomgangen av svar 2 (ECH1): tallene fra stil.css som grunnplass regner
# med: skriften i px, linjehøyden, mellomrommet, luften over og til siden,
# rammen og bredden per tegn i em (test_grunnplass_er_regnet_fra_stilen).
RUTESKRIFT, RUTELINJE, RUTEGAP, RUTELUFT, RUTERAMME, EM_PER_TEGN = 14, 1.2, 1, (4, 6), 4, 0.5
# Gruppens svar 04.11 kl. 22:23, 1: store ruter som i designforslaget, nivå 4.
# Symbolet 22 px halvfett og styrken øverst, navnet 12,5 px under, og
# endringen 28 px halvfett nederst, med luft 10 og 12 px og STORGAP mellom
# linjene og STORMELLOM mellom symbolet og styrken (stil.css). Grensen er
# regnet som NIVAA_3 og STYRKE for det bredeste: AKRBP, fem tegn, med
# «ikke vurdert» ved siden av, og «Uten data» i 28 px, med 0,62 em per tegn i
# halvfet skrift og EM_PER_TEGN ellers, og for høyden uten merket og grunnen
# (test_grensen_for_store_ruter_er_regnet_fra_stilen).
# Gruppens svar 05.11 kl. 14:29, 4: grensen regnes for hver rute (storplass),
# så høye, smale ruter blir store når alt deres får plass. STOR er nå
# høyden og den største bredden en rute med en endring på høyst ni tegn
# kan trenge.
STORSYMBOL, STORNAVN, STORENDRING, STORLUFT, STORGAP, STORMELLOM = 22, 12.5, 28, (10, 12), 2, 8
STOR = (207, 107)
# Gruppens svar 05.11 kl. 14:29, 2: store ruter bare fra 1079 px, som bygget,
# altså bare i klassen bredest i Flate.tekst.
STORE_KLASSER = frozenset({"bredest"})
# Ringen rundt «3 av 3» og «2 av 3»: luften til siden i px (0,45 rem) og den
# tykkeste kanten, som i test_styrkens_grense_er_regnet_fra_stilen.
PILLELUFT, PILLEKANT = 0.45 * 16, 2
# Bredden per tegn i halvfet skrift, i em, som i grensen over.
HALVFET_EM = 0.62
# Gjennomgangen av svar 4 (ECH1): symbolet i 22 px halvfett er bredere enn
# HALVFET_EM, fordi det bare har store bokstaver. Målt i Edge 05.11 med en
# Range: opptil 0,721 em per tegn (MOWI) for de 15 aksjene og demoen, så
# grensen per rute regnes med 0,75 em. STOR[0] er regnet med det (AKRBP med
# «ikke vurdert»: 206,5 px).
STORSYMBOL_EM = 0.75
# Merket for en annen dag i en gul rute, som i boersometer.html.
MERKET = f"{ANTALL_SJEKKER} av {ANTALL_SJEKKER} siste børsdag"


def stor_bredde(symbol: str, styrke: str | None, pille: bool, endring: str) -> float:
    """Bredden en stor rute trenger (gruppens svar 05.11 kl. 14:29, 4):
    øverst symbolet i 22 px halvfett og styrken ved siden av, med ringen
    når pille, og nederst endringen i 28 px halvfett, som den vises.
    Navnet kuttes med «…», så det trenger ingen bredde. Gjennomgangen av
    svarene 04.11 kl. 22:23 (BH3, ECH3): endringen kan ha flere tegn enn
    «Uten data»."""
    luft = 2 * RUTERAMME + 2 * STORLUFT[1]
    topp = luft + STORSYMBOL_EM * STORSYMBOL * len(symbol)
    if styrke is not None:
        topp += STORMELLOM + EM_PER_TEGN * RUTESKRIFT * len(styrke)
        if pille:
            topp += 2 * PILLEKANT + 2 * PILLELUFT
    return max(topp, luft + HALVFET_EM * STORENDRING * len(endring))


def _stor_bredde(rute: Rute) -> float:
    """stor_bredde for ruta, med teksten og ringen som i boersometer.html."""
    if rute.endring is not None:
        endring = tall(rute.endring, "endring")
    else:
        endring = UTEN_DATA if rute.uten_data else "–"
    styrke = None if rute.uten_data else rute.uten_styrke or f"{rute.styrke} av {ANTALL_SJEKKER}"
    pille = rute.ramme == MOERK or (rute.ramme == GUL and rute.er_siste)
    return stor_bredde(rute.aksje.symbol, styrke, pille, endring)


def storplass(rute: Rute, b: float, h: float) -> bool:
    """Om ruta, som er b × h px, har plass til teksten som i designforslaget
    (gruppens svar 04.11 kl. 22:23, 1), med bredden regnet for ruta selv
    (svar 4 kl. 14:29)."""
    return b >= _stor_bredde(rute) and h >= STOR[1]


def _stor_linjer(rute: Rute, b: float, h: float) -> tuple[bool, bool, bool] | None:
    """Om navnet, merket og grunnen står i en stor rute, som er b × h px
    (svaret kl. 22:23, 1: «der de får plass»). Merket kommer først, og
    grunnen bare under det når merket står. Gruppens svar 05.11 kl. 14:29,
    1: en gul rute en annen dag uten plass til merket under navnet viser
    merket og styrken i stedet for navnet. Får merket ikke plass der
    heller, er svaret None, og ruta er ikke stor. Merket står i halvfet
    skrift (gjennomgangen, ECH1), så linjene regnes med HALVFET_EM."""
    bredde = b - 2 * RUTERAMME - 2 * STORLUFT[1]
    rest = h - STOR[1]
    linje = RUTESKRIFT * RUTELINJE
    navn, merke = True, False
    if rute.ramme == GUL and not rute.er_siste:
        trengs = _linjer(MERKET, bredde, HALVFET_EM) * linje + STORGAP
        if trengs > rest:
            rest += STORNAVN * RUTELINJE + STORGAP
            if trengs > rest:
                return None
            navn = False
        merke, rest = True, rest - trengs
    grunn = bool(rute.grunn) and _linjer(rute.grunn, bredde) * linje + STORGAP <= rest
    return navn, merke, grunn


def tekstnivaa(b: float, h: float, symbol: str) -> int:
    """Hvor mye tekst ruta har plass til, i px (spesifikasjonen 8.6b, «Navnet»).
    Gruppens svar 04.11 kl. 10:01 og 10:04: teksten er 14 px, ikke 13 og 12,
    og nivå 3 har styrken og merket for siste børsdag. Grensene er skalert
    med det og målt i Edge ved 1280, 1079, 900, 761, 760, 390, 360 og 320 px
    (spesifikasjonen 8.2b). Gjennomgangen av 8.2b (BH2, ECH2, VG1): nivå 3
    har plass til det lengste, en gul ramme en annen dag med navnet,
    endringen, styrken og merket på to linjer (test_nivaa_3_har_plass_til_det_lengste)."""
    if b < 10 * len(symbol) + 10 or h < 40:
        return 0
    if b < 80 or h < 65:
        return 1
    if b < NIVAA_3[0] or h < NIVAA_3[1]:
        return 2
    return 3


def styrkeplass(b: float, h: float) -> bool:
    """Om ruta har plass til styrken under symbolet og endringen, med ringen
    og rammen (gruppens svar 04.11 kl. 19:21). Merket for en annen dag og
    teksten står fortsatt bare på nivå 3."""
    return b >= STYRKE[0] and h >= STYRKE[1]


def ikke_vurdert_plass(b: float, h: float) -> bool:
    """Om ruta har plass til «ikke vurdert» under symbolet og endringen
    (gruppens svar 04.11 kl. 20:53 og 20:56, 2)."""
    return b >= IKKE_VURDERT_PLASS[0] and h >= IKKE_VURDERT_PLASS[1]


def _linjer(tekst: str, bredde: float, em: float = EM_PER_TEGN) -> int:
    """Hvor mange linjer teksten brytes til i bredde px, ord for ord, med
    em per tegn, EM_PER_TEGN eller HALVFET_EM. Et ord som er bredere enn
    linja, får en linje."""
    per_linje = max(1, int(bredde // (em * RUTESKRIFT)))
    linjer, brukt = 1, 0
    for ord_ in tekst.split():
        if brukt and brukt + 1 + len(ord_) > per_linje:
            linjer, brukt = linjer + 1, len(ord_)
        else:
            brukt += (1 if brukt else 0) + len(ord_)
    return linjer


def grunnplass(rute: Rute, b: float, h: float) -> bool:
    """Om hele grunnen får plass i ruta, som er b × h px: under symbolet,
    endringen, «ikke vurdert» og merket for en annen dag på to linjer, med
    rammen. Gruppens svar 04.11 kl. 20:53 og 20:56, 2: hele grunnen der den
    får plass. Gjennomgangen (ECH1): med «ikke vurdert» i tillegg kunne
    grunnen kuttes på nivå 3 i en gul rute en annen dag."""
    if not rute.grunn:
        return False
    merke = 2 if rute.ramme == GUL and not rute.er_siste else 0
    linjer = 3 + merke + _linjer(rute.grunn, b - 2 * RUTERAMME - 2 * RUTELUFT[1])
    return 2 * RUTERAMME + 2 * RUTELUFT[0] + linjer * RUTESKRIFT * RUTELINJE + (linjer - 1) * RUTEGAP <= h


def styrkelinje(rute: Rute, b: float, h: float) -> bool:
    """Om styrken står på nivå 2 i ruta, som er b × h px. Gruppens svar
    04.11 kl. 20:53 og 20:56, 1 (ECH1 i spesifikasjonen 8.2b): en annen dag
    står styrken i en rute med gul ramme bare når merket «3 av 3 siste
    børsdag» også får plass, og merket står bare på nivå 3. Svar 2: en rute
    uten styrke har «ikke vurdert» på den linja, med sin egen grense, og en
    rute uten data har ingen linje."""
    if rute.uten_data or (rute.ramme == GUL and not rute.er_siste):
        return False
    if rute.uten_styrke:
        return ikke_vurdert_plass(b, h)
    return styrkeplass(b, h)


def _legg_ut(
    bransjer: list[Bransje], bredde: float, hoeyde: float, minste_felt: float = 0.0, skala: float = 1.0
) -> list | None:
    """Feltene og rutene i px, eller None når en rute er mindre enn
    MINSTE_RUTE med KANT på hver side, et felt ikke har plass under
    overskriften, eller et felt er smalere enn minste_felt eller enn linja
    med antallet og snittet ganger skala (story 8.20b, U97)."""
    minst = MINSTE_RUTE + 2 * KANT
    feltbredde = max(minst, minste_felt)
    feltvekter = [sum(vekt(r) for r in bransje.ruter) for bransje in bransjer]
    ut = []
    for bransje, felt in zip(bransjer, squarify(feltvekter, 0, 0, bredde, hoeyde, feltbredde), strict=True):
        fx, fy, fb, fh = felt
        if fh - OVERSKRIFT < minst or fb < max(feltbredde, tilleggsbredde(bransje) * skala):
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
            skala = flate.bredde / flate.minste
            utlagt = _legg_ut(bransjer, flate.bredde, hoeyde, MINSTE_FELT * skala, skala)
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
        styrke: list[set[str]] = [set() for _ in bransje.ruter]
        grunn: list[set[str]] = [set() for _ in bransje.ruter]
        merke: list[set[str]] = [set() for _ in bransje.ruter]
        navn: list[set[str]] = [set() for _ in bransje.ruter]
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
                    nivaa[i][klasse], med_styrke, med_grunn, med_merke, med_navn = _nivaa_ved(
                        flate, bredde, rb, rh, bransje.ruter[i], klasse in STORE_KLASSER
                    )
                    if med_styrke:
                        styrke[i].add(klasse)
                    if med_grunn:
                        grunn[i].add(klasse)
                    if med_merke:
                        merke[i].add(klasse)
                    if med_navn:
                        navn[i].add(klasse)
        kartruter = [
            Kartrute(
                rute=r,
                vekt=vekt(r),
                plass=ruteplass[i],
                nivaa=nivaa[i],
                styrke=frozenset(styrke[i]),
                grunn=frozenset(grunn[i]),
                merke=frozenset(merke[i]),
                navn=frozenset(navn[i]),
            )
            for i, r in enumerate(bransje.ruter)
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
