"""Tall slik sidene viser dem - regel 21, story 8.0.

Ren logikk og ingen import. Hvor mange desimaler hver type tall har,
bestemmes her og ikke i malene: filteret tall i app.py og forklaringene i
signalberegning.py bruker samme funksjon.

Det som vises: desimalkomma, hardt mellomrom som tusenskille og foran %, og
vanlig bindestrek som minus, saa tallet kan limes inn i et regneark. Et tall
som rundes til null, vises uten fortegn, saa «-0,00» aldri staar paa siden.
Tallet selv endres ikke: avrunding skjer bare her, der det vises.
"""

HARDT_MELLOMROM = "\u00a0"

# Desimaler per slag. Maaling og forhold er et minimum: desimaler_mot_grense
# kan gi flere. Endringen har to desimaler, som foer, saa rekkefoelgen i
# FR-102 kan leses av. Forhold er volumet som forholdstall mot medianen
# (story 2.1c), uten fortegn og uten %.
DESIMALER = {
    "kurs": 2,
    "endring": 2,
    "maaling": 1,
    "forhold": 2,
    "volum": 0,
    "akse": 0,
    # Story 8.0b: tallene i hjelpetekstene. Heltall er vinduer og terskelen,
    # faktor er volumfaktoren (1,5), grense er noeytralsonen i prosent (2 %),
    # og andel er en maalt andel i prosent (60,0 %). Ingen av dem har fortegn.
    "heltall": 0,
    "faktor": 1,
    "grense": 0,
    "andel": 1,
}

# Slagene som vises med fortegn og prosent.
MED_FORTEGN = {"endring", "maaling"}
PROSENT = {"endring", "maaling", "grense", "andel"}

MEST_DESIMALER = 6


def tall(
    verdi: float,
    slag: str,
    desimaler: int | None = None,
    fortegn: bool | None = None,
) -> str:
    """Tallet som tekst etter regel 21.

    desimaler overstyrer slagets antall. Det brukes naar en maaling maa vises
    med flere desimaler for aa skilles fra grensen sin. fortegn overstyrer om
    et positivt tall faar +, for eksempel for et standardavvik, som ikke har
    retning.
    """
    if slag not in DESIMALER:
        raise ValueError(f"Ukjent slag {slag!r}. Kjente slag: {', '.join(DESIMALER)}")
    antall = DESIMALER[slag] if desimaler is None else desimaler

    avrundet = f"{abs(verdi):,.{antall}f}"
    heltall, _, brok = avrundet.partition(".")
    tekst = heltall.replace(",", HARDT_MELLOMROM)
    if brok:
        tekst += "," + brok

    er_null = float(avrundet.replace(",", "")) == 0
    if verdi < 0 and not er_null:
        tekst = "-" + tekst
    elif (slag in MED_FORTEGN if fortegn is None else fortegn) and verdi > 0 and not er_null:
        tekst = "+" + tekst

    if slag in PROSENT:
        tekst += HARDT_MELLOMROM + "%"
    return tekst


def dato(dag, i_aar: int) -> str:
    """En dato slik sidene viser den - story 8.0c, ordlista i designregler §4.

    «22.09», uten punktum til slutt, og med aar bare naar aaret er et annet
    enn i_aar: «29.09.2025». i_aar er aaret i dag, fra app.idag(), saa
    testene styrer det. Funksjonen importerer ikke datetime: dag er en
    datetime.date eller noe med day, month og year.
    """
    tekst = f"{dag.day:02d}.{dag.month:02d}"
    if dag.year != i_aar:
        tekst += f".{dag.year}"
    return tekst


# Ukedagene paa norsk, i rekkefoelgen date.weekday() gir dem (mandag er 0).
UKEDAGER = ("mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag")


def ukedag(dag) -> str:
    """Ukedagen for en dato, som «tirsdag» - story 8.0e, svar 5.

    Smaa bokstaver, fordi den staar inne i overskriften: «4 av 15 aksjer
    skilte seg ut tirsdag». dag er en datetime.date eller noe med weekday().
    """
    return UKEDAGER[dag.weekday()]


def med_og(navn: list[str]) -> str:
    """Navnene bundet med komma og «og»: «A», «A og B», «A, B og C»."""
    if len(navn) < 2:
        return "".join(navn)
    return f"{', '.join(navn[:-1])} og {navn[-1]}"


def fortegn(verdi: int) -> str:
    """En sjekks verdi med fortegn: «+1», «0» eller «-1» - story 8.0e.

    Vanlig bindestrek som minus (regel 21), og 0 uten fortegn. Samme form
    i Ga-kolonnen paa aksjesiden og i T, B og I i oversikten.
    """
    return f"{verdi:+d}" if verdi else "0"


def desimaler_uten_null(verdi: float, minst: int = 1) -> int:
    """Faerrest desimaler, minst minst, som viser et tall over 0 som noe
    annet enn 0 - svaret kl. 12:15 (15.10, ECH3): en grense over 0 vises
    aldri som «0,0».

    Hoeyst MEST_DESIMALER, eller minst naar den er stoerre. Er tallet
    over 0, men 0 ogsaa da, gis det taket: da vises det som null med
    MEST_DESIMALER desimaler, ikke som «0,0» (gjennomgangen av svarene
    15.10, BH1, som gruppen avgjoer). 0, og et tall som ikke er endelig,
    faar minst.
    """
    a = abs(verdi)
    for antall in range(minst, MEST_DESIMALER + 1):
        if float(f"{a:.{antall}f}") != 0:
            return antall
    return max(minst, MEST_DESIMALER) if a > 0 else minst


def desimaler_mot_grense(maaling: float, grense: float, minst: int = 1) -> int:
    """Faerrest desimaler, minst minst, som skiller maalingen fra grensen.

    Sjekkene sammenligner absoluttverdier, saa det gjoer denne ogsaa. En
    maaling som er noeyaktig lik grensen, faar minst desimaler: da er det
    riktig at tallene er like. Ellers kunne «-1,2 % mot 1,2 %» staa ved en
    sjekk som ga -1, og brukeren kunne ikke se hvorfor.

    Er de like ogsaa med MEST_DESIMALER, er forskjellen avrundingsstoey fra
    flyttallene, og da gis minst: seks desimaler som er like, forklarer ikke
    mer enn én.
    """
    a, b = abs(maaling), abs(grense)
    if a == b:
        return minst
    for antall in range(minst, MEST_DESIMALER + 1):
        if f"{a:.{antall}f}" != f"{b:.{antall}f}":
            return antall
    return minst
