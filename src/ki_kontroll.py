"""Kontrollen i FR-603: KI-teksten sier ikke mer enn grunnlaget - story 10.2.

Én ren funksjon, som hentekommandoen kaller foer teksten logges som bestaatt
(story 10.2, PR F). Den bygger paa kjennetegn som kan observeres, ikke paa en
sikkerhetsscore fra modellen. Fire punkter:

1. Retning og styrke. Sier teksten hva retningen eller styrken er, skal det
   vaere regelens. Det sjekkes der teksten sier det («retningen er blandet»,
   «to av de tre sjekkene»), ikke som enkeltord: «positiv» og «negativ» staar
   naturlig i en tekst om retningen Blandet, og «ingen» er et vanlig ord.
2. Tallene. Bare antall fra grunnlaget (styrken) og regelens faste tall er
   lov: tre sjekker, 50 i MA50, 20 dager i vinduene og 2 i terskelen. Tall
   skrevet med ord sjekkes ogsaa, som «femti» eller «femdagssnittet». Et
   desimaltall eller en prosent er aldri lov, fordi grunnlaget ikke har dem.
3. Raad. Ingen ord som gir raad (NFR-06), ogsaa «alternativ for investorer»,
   «investerings-» og «raadgiver» fra malinger.md §19.
4. Gjetning. Ingen ord som gjetter eller spaar, og ingen aarsak som ikke staar
   i grunnlaget, som nyheter eller kontrakter. En forklaring av regelen selv
   er lov, som «fordi ingen sjekk ga utslag». «Resultat» staar ikke i lista,
   fordi det i §19 viste til sjekkene.

Kontrollen er grov: den fanger ord, ikke mening (FR-603).
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass

from signalberegning import MA_VINDU, TERSKEL, VOLATILITET_VINDU, VOLUM_VINDU

ANTALL_SJEKKER = 3

# Regelens faste tall (punkt 2).
FASTE_TALL = frozenset({ANTALL_SJEKKER, MA_VINDU, VOLATILITET_VINDU, VOLUM_VINDU, TERSKEL})

TALLORD = {
    "null": 0, "én": 1, "ett": 1, "to": 2, "tre": 3, "fire": 4, "fem": 5, "seks": 6,
    "sju": 7, "syv": 7, "åtte": 8, "ni": 9, "ti": 10, "elleve": 11, "tolv": 12,
    "tretten": 13, "fjorten": 14, "femten": 15, "seksten": 16, "sytten": 17,
    "atten": 18, "nitten": 19, "tjue": 20, "tyve": 20, "tretti": 30, "førti": 40,
    "femti": 50, "seksti": 60, "sytti": 70, "åtti": 80, "nitti": 90, "hundre": 100,
    "tusen": 1000, "ingen": 0,
}

# Et tallord som eget ord, eller foran «dag», «uke» eller «måned» i et
# sammensatt ord («femdagssnittet», «tjuedagers»). Ikke inni andre ord, saa
# «trend», «tid» og «nivå» ikke regnes som tall. «ingen» og «ett» regnes
# bare i punkt 1, der de staar foran «av», fordi de ellers er vanlige ord.
_TALLORD_I_TEKST = re.compile(
    r"(?<![a-zæøå])(" + "|".join(sorted((o for o in TALLORD if o not in ("ingen", "ett")), key=len, reverse=True))
    + r")(?=$|[^a-zæøå]|dag|uke|måned)",
    re.IGNORECASE,
)
_SIFFER = re.compile(r"\d+(?:[.,]\d+)?")

_RETNING_UTSAGN = (
    re.compile(r"retning(?:en)?\s+(?:er|var|blir|ble)\s+(?:altså\s+|derfor\s+|samlet\s+)?(positiv|negativ|blandet|ingen)", re.IGNORECASE),
    re.compile(r"(positiv|negativ|blandet)\s+retning", re.IGNORECASE),
)
_STYRKE_UTSAGN = (
    re.compile(r"(?:signal)?styrke(?:n)?\s+(?:er|var|på|blir|ble)\s+(\w+)", re.IGNORECASE),
    re.compile(r"(?<![a-zæøå])(\w+)\s+av\s+(?:de\s+)?tre\s+sjekk", re.IGNORECASE),
)

RAAD = (
    r"kjøp", r"selg", r"salgs", r"anbefal", r"bør\b",r"råd\b", r"rådgiv", r"investerings\w*",
    r"alternativ for investorer", r"kursmål",
)
GJETNING = (
    r"trolig", r"sannsynlig", r"kan tyde på", r"tyder på", r"forvent", r"antyde", r"skyldes",
    r"på grunn av", r"kanskje", r"muligens", r"vil fortsette", r"kommer til å", r"spår",
    r"prognose", r"neste (?:dag|uke|måned)",
)
AARSAKER = (
    r"nyhet", r"kontrakt", r"kvartal", r"rapport", r"oppkjøp", r"fusjon", r"emisjon",
    r"utbytte", r"børsmelding", r"rente", r"oljepris",
)

_RAAD = re.compile(r"(?<![a-zæøå])(" + "|".join(RAAD) + r")", re.IGNORECASE)
_GJETNING = re.compile(r"(?<![a-zæøå])(" + "|".join(GJETNING + AARSAKER) + r")", re.IGNORECASE)


@dataclass(frozen=True)
class Kontrollsvar:
    besto: bool
    grunner: tuple[str, ...]

    @property
    def grunn(self) -> str | None:
        """Grunnene som én tekst for KIRad.grunn, eller None."""
        return "; ".join(self.grunner) if self.grunner else None


def _som_tall(ord_: str) -> int | None:
    ord_ = ord_.lower()
    if ord_.isdigit():
        return int(ord_)
    return TALLORD.get(ord_)


def kontroller(tekst: str, grunnlag: Mapping[str, object]) -> Kontrollsvar:
    """De fire punktene i FR-603. Gir alle grunnene, ikke bare den foerste."""
    if not isinstance(tekst, str):
        raise TypeError("tekst maa vaere en tekst")
    styrke = grunnlag["styrke"]
    retning = str(grunnlag["retning"]).lower()
    grunner: list[str] = []

    # 1. Retning og styrke, der teksten sier dem.
    for moenster in _RETNING_UTSAGN:
        for treff in moenster.finditer(tekst):
            if treff.group(1).lower() != retning:
                grunner.append(f"1: retningen «{treff.group(0)}», regelen sier {grunnlag['retning']}")
    for moenster in _STYRKE_UTSAGN:
        for treff in moenster.finditer(tekst):
            tall = _som_tall(treff.group(1))
            if tall is not None and tall != styrke:
                grunner.append(f"1: styrken «{treff.group(0)}», regelen sier {styrke}")

    # 2. Tallene.
    lovlige = FASTE_TALL | {styrke}
    for treff in _SIFFER.finditer(tekst):
        tall = treff.group(0)
        if "," in tall or "." in tall or int(tall) not in lovlige:
            grunner.append(f"2: tallet «{tall}»")
    if "%" in tekst:
        grunner.append("2: en prosent")
    for treff in _TALLORD_I_TEKST.finditer(tekst):
        if TALLORD[treff.group(1).lower()] not in lovlige:
            grunner.append(f"2: tallet «{treff.group(0)}»")

    # 3. Raad.
    for treff in _RAAD.finditer(tekst):
        grunner.append(f"3: «{treff.group(0)}»")

    # 4. Gjetning og aarsaker utenfor grunnlaget.
    for treff in _GJETNING.finditer(tekst):
        grunner.append(f"4: «{treff.group(0)}»")

    return Kontrollsvar(besto=not grunner, grunner=tuple(grunner))
