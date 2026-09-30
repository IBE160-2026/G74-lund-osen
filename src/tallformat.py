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

# Desimaler per slag. Maaling er et minimum: desimaler_mot_grense kan gi
# flere. Endringen har to desimaler, som foer, saa rekkefoelgen i FR-102 kan
# leses av.
DESIMALER = {
    "kurs": 2,
    "endring": 2,
    "maaling": 1,
    "volum": 0,
    "akse": 0,
}

# Slagene som vises med fortegn og prosent.
MED_FORTEGN = {"endring", "maaling"}
PROSENT = {"endring", "maaling"}

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
