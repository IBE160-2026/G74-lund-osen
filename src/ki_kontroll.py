"""Kontrollen i FR-603: KI-teksten sier ikke mer enn grunnlaget - story 10.2.

Én ren funksjon, som hentekommandoen kaller foer teksten logges som bestaatt
(story 10.2, PR F). Den bygger paa kjennetegn som kan observeres, ikke paa en
sikkerhetsscore fra modellen. Fire punkter:

1. Retning og styrke. Sier teksten hva retningen eller styrken er, skal det
   vaere regelens. Det sjekkes der teksten sier det («retningen er blandet»,
   «to av de tre sjekkene», «ingen sjekk ga utslag»), ikke som enkeltord:
   «positiv» og «negativ» staar naturlig i en tekst om retningen Blandet, og
   «ingen» er et vanlig ord. «Trendens retning er positiv» handler om én
   sjekk, ikke signalet, og sjekkes ikke.
   Story 10.2d: retningen leses ogsaa der teksten sier den om hele
   signalet, i formene Gemma skriver: «signalet er Negativt», «signalet er
   av typen Ingen», «Signalet for MOWI er positivt», «Dagens signal er
   blandet», med opptil to fyll- eller gradsord («signalet er altsaa
   positivt», «samlet sett», «klart»), i anfoerselstegn eller fet skrift
   («Positivt», **Negativt**), med omvendt ordstilling («Samlet er signalet
   positivt», «Derfor er retningen negativ»), «retningen paa signalet er
   blandet», og «et positivt signal» naar subjektet er signalet eller
   teksten begynner med «Dette er» eller «Det er». Andre steder kan «det er
   et positivt signal» vise til én sjekk, og da sjekkes det ikke.
   «Signalet er ingen» leses bare med «av typen» foran eller et skilletegn
   eller «fordi» etter, saa «Signalet er ingen garanti» ikke er en retning.
   Styrken leses ogsaa i «av styrke tre» og «av signalstyrke tre». Det som
   gjelder én sjekk, sjekkes fortsatt ikke: «Trenden ga et positivt utslag»
   eller «signal», «Trend-signalet», «Trendens bidrag til signalet er
   positivt», «Signalet er positivt for trenden» og «Hver sjekk er av
   styrke én». Det kjennes paa ordene trend, bevegelse, interesse, sjekk,
   kurs, volum og utslag i de tre ordene foran, eller etter «for» eller
   «paa» rett etter retningen.
2. Tallene. Bare antall fra grunnlaget (styrken) og regelens faste tall er
   lov: tre sjekker, 50 i MA50, 20 dager i vinduene og 2 i terskelen. Tall
   skrevet med ord sjekkes ogsaa, som «femti», «femdagssnittet» og
   «femtifem». Et desimaltall, en prosent, et beloep eller en mengde som
   «dobbelt» er aldri lov, fordi grunnlaget ikke har dem. Fortegnene (+1, 0
   og -1) er ikke antall, og prompten ber modellen skrive dem med ord.
   Story 10.2e: et tall er lov bare naar det er et av antallene i
   grunnlaget (ANTALLENE i ki_grunnlag.py: styrken, dagene og hvor mange
   aksjer som steg og falt) eller et av regelens faste tall.
3. Raad. Ingen ord som gir raad (NFR-06), ogsaa «alternativ for investorer»,
   «investerings-» og «raadgiver» fra malinger.md §19, og raad om aa holde.
4. Gjetning. Ingen ord som gjetter eller spaar, og ingen aarsak som ikke staar
   i grunnlaget, som nyheter eller kontrakter. En forklaring av regelen selv
   er lov, som «fordi ingen sjekk ga utslag» naar ingen ga det. «Resultat»
   staar ikke i lista (FR-603, 05.10), fordi det i §19 viste til sjekkene.

Story 10.2e, under punkt 1: sier teksten at hovedindeksen eller bransjen
steg, falt eller var uendret, skal det stemme med grunnlaget, og mangler
feltet, stoppes utsagnet. Det samme gjelder antallet aksjer som steg eller
falt («ni aksjer steg»), og dagene («tre børsdager på rad»).

Kontrollen er grov: den fanger ord, ikke mening (FR-603). Teksten
normaliseres (NFC, uten myk bindestrek og usynlige tegn) foer den leses, saa
et ord ikke slipper gjennom fordi det er skrevet med andre tegn.
"""

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass

from ki_grunnlag import ANTALLENE, FALT, STEG, UENDRET
from signalberegning import MA_VINDU, TERSKEL, VOLATILITET_VINDU, VOLUM_VINDU

ANTALL_SJEKKER = 3

# Regelens faste tall (punkt 2).
FASTE_TALL = frozenset({ANTALL_SJEKKER, MA_VINDU, VOLATILITET_VINDU, VOLUM_VINDU, TERSKEL})

TALLORD = {
    "null": 0,
    "to": 2,
    "tre": 3,
    "fire": 4,
    "fem": 5,
    "seks": 6,
    "sju": 7,
    "syv": 7,
    "åtte": 8,
    "ni": 9,
    "ti": 10,
    "elleve": 11,
    "tolv": 12,
    "tretten": 13,
    "fjorten": 14,
    "femten": 15,
    "seksten": 16,
    "sytten": 17,
    "atten": 18,
    "nitten": 19,
    "tjue": 20,
    "tyve": 20,
    "tretti": 30,
    "førti": 40,
    "femti": 50,
    "seksti": 60,
    "sytti": 70,
    "åtti": 80,
    "nitti": 90,
    "hundre": 100,
    "tusen": 1000,
}

# Ord som er et antall bare naar de staar i et utsagn om styrken (punkt 1),
# fordi de ellers er vanlige ord: «en», «ett», «én», «ingen», «alle», «begge».
STYRKEORD = {**TALLORD, "en": 1, "én": 1, "ett": 1, "ingen": 0, "alle": 3, "begge": 2}

_STAMMER = "|".join(sorted(TALLORD, key=len, reverse=True))

# Ett eller flere tallord som eget ord, eller foran «dag», «uke», «måned»,
# «år» eller «time» i et sammensatt ord («femdagssnittet», «femtifem»). Ikke
# inni andre ord, saa «trend», «tid» og «nivå» ikke regnes som tall.
_TALLORD_I_TEKST = re.compile(
    r"(?<![a-zæøå])((?:" + _STAMMER + r")+)(?=$|[^a-zæøå]|dag|uke|måned|år|time)",
    re.IGNORECASE,
)
_SIFFER = re.compile(r"\d+(?:[.,]\d+)?")
_LENGSTE_TALL = 6

# Enheter og mengder grunnlaget aldri har (punkt 2).
_ENHETER = re.compile(
    r"(?<![a-zæøå])(prosent\w*|promille|kroner|kr\b|nok\b|dobbel\w*|halvpart\w*|"
    r"tredobl\w*|firedobl\w*|(?:tredje|fjerde|femte|sjette|sjuende|syvende|åttende|niende|tiende)\b)",
    re.IGNORECASE,
)

_UTFYLLING = r"(?:altså\s+|derfor\s+|samlet\s+|dermed\s+)?"

# Story 10.2d: formene Gemma skriver om hele signalet.
# Opptil to fyll- eller gradsord mellom verbet og retningen.
_FYLLORD = (
    r"(?:(?:altså|derfor|samlet(?:\s+sett)?|totalt(?:\s+sett)?|dermed|nå|i\s+dag|"
    r"klart|tydelig|svakt|sterkt|overveiende)\s+){0,2}"
)
# Anfoerselstegn og markdown rundt retningen: «Ingen», "Negativt", **Positivt**.
_MERKE = r"[«»\"'*_]*"
# Ord etter retningen som sier at den gjelder én sjekk: «positivt for trenden».
_EN_SJEKK_ETTER = r"(?!(?:t|e)?" + _MERKE + r"\s+(?:for|på|i|fra|hos)\s+(?:trend|beveg|interess|sjekk|kurs|volum))"
_RETNINGSORD = r"(positiv|negativ|blandet)(?=(?:t|e)?" + _MERKE + r"(?![a-zæøå]))" + _EN_SJEKK_ETTER
_INGEN = r"(ingen)(?=" + _MERKE + r"\s*(?:[,.;:!?]|$|fordi(?![a-zæøå])))"
# Signalet som subjekt, ogsaa «Signalet for MOWI», «Signalet i dag» og
# «Dagens signal», men ikke «Trend-signalet» eller «Signalet for trenden».
_SIGNALET = (
    r"(?:(?<![\w-])signalet(?:\s+(?:for|i)\s+(?!trend|beveg|interess|sjekk|dag)(?:aksjen\s+)?[\w.-]+"
    r"(?:\s+[A-ZÆØÅ][\w.-]*)?|\s+i\s+dag)?|(?<![\w-])dagens\s+signal)"
)
# Inntil tre ord foran, i samme ledd, saa en sjekk foran kan kjennes igjen.
_FORAN = r"((?:[\w-]+\s+){0,3})"

_RETNING_UTSAGN = (
    re.compile(
        r"(?<![a-zæøå])((?:\w+\s+)?)retning(?:en)?\s+(?:er|var|blir|ble)\s+"
        + _UTFYLLING
        + r"(ikke\s+)?(positiv|negativ|blandet|ingen)",
        re.IGNORECASE,
    ),
    re.compile(r"(?<![a-zæøå])()()(positiv|negativ|blandet|ingen)\s+retning", re.IGNORECASE),
    # Story 10.2d: «Dette signalet er Negativt», «signalet er av typen Ingen»,
    # og «retningen på signalet er blandet», som leses som «signalet er».
    re.compile(
        _FORAN
        + _SIGNALET
        + r"\s+(?:er|var|blir|ble)[\s:]+"
        + _FYLLORD
        + r"(ikke\s+)?"
        + _MERKE
        + r"(?:av\s+typen\s+"
        + _MERKE
        + r"(positiv|negativ|blandet|ingen)|"
        + _RETNINGSORD
        + r"|"
        + _INGEN
        + r")",
        re.IGNORECASE,
    ),
    # Omvendt ordstilling: «Samlet er signalet positivt», «Derfor er retningen negativ».
    re.compile(
        r"()(?<![\w-])(?:altså|derfor|samlet(?:\s+sett)?|totalt(?:\s+sett)?|dermed|nå|i\s+dag)\s+"
        r"(?:er|var|blir|ble)\s+(?:signalet|retningen(?:\s+(?:på|til)\s+signalet)?)\s+"
        + _FYLLORD
        + r"(ikke\s+)?"
        + _MERKE
        + r"(?:"
        + _RETNINGSORD
        + r"|"
        + _INGEN
        + r")",
        re.IGNORECASE,
    ),
    # «et positivt signal» om hele signalet: med signalet som subjekt, eller
    # «Dette er» / «Det er» foerst i teksten. Ellers kan «det» vise til én sjekk.
    re.compile(
        r"()(?:\A\s*(?:dette|det)|(?<![\w-])signalet)\s+(?:er|var|blir|ble)\s+"
        + _FYLLORD
        + r"(ikke\s+)?et\s+(?:(?:svakt|sterkt|klart|tydelig)\s+)?"
        + _MERKE
        + r"(positiv|negativ|blandet)t?"
        + _MERKE
        + r"\s+signal(?![\w])(?!\s+(?:for|på|i|fra)\s+(?:trend|beveg|interess|sjekk|kurs|volum))",
        re.IGNORECASE,
    ),
)
# Et ord foran «retning» som sier at det gjelder én sjekk eller kursen.
_ANNEN_RETNING = re.compile(r"^(trendens|bevegelsens|interessens|kursens|dagens|sjekkens)\s+$", re.IGNORECASE)
# Story 10.2d: et ord i de tre ordene foran som sier at det gjelder én sjekk.
_EN_SJEKK_FORAN = re.compile(r"(?<![a-zæøå])(?:trend|beveg|interess|sjekk|kurs|volum|utslag)", re.IGNORECASE)

_STYRKE_UTSAGN = (
    re.compile(
        r"(?<![a-zæøå])(?:signal)?styrken?(?:\s+(?:på|til)\s+signalet)?\s+(?:er|var|blir|ble|på)\s+"
        + _UTFYLLING
        + r"(\w+)",
        re.IGNORECASE,
    ),
    re.compile(r"(?<![a-zæøå])(\w+)\s+av\s+(?:de\s+)?(?:tre|3)\s+sjekk", re.IGNORECASE),
    # Story 10.2d: «Dette signalet er av styrke tre», ikke «Hver sjekk er av styrke én».
    re.compile(_FORAN + r"(?<![a-zæøå])av\s+(?:signal)?styrke\s+(\w+)", re.IGNORECASE),
    re.compile(
        r"(?<![a-zæøå])(?<!de )(\w+)\s+(?:av\s+)?(?:(?:de\s+)?(?:tre|3)\s+)?sjekk\w*\s+(?:ga|slo|gir|slår)\b",
        re.IGNORECASE,
    ),
)

# Story 10.2e: hovedindeksen og bransjen, og verbene for steg, falt og uendret.
_BEVEGELSESVERB = {
    "steg": STEG,
    "stiger": STEG,
    "økte": STEG,
    "øker": STEG,
    "gikk opp": STEG,
    "falt": FALT,
    "faller": FALT,
    "sank": FALT,
    "synker": FALT,
    "gikk ned": FALT,
    "var uendret": UENDRET,
    "er uendret": UENDRET,
    "sto stille": UENDRET,
    "endret seg ikke": UENDRET,
}
_VERB = "|".join(sorted((v.replace(" ", r"\s+") for v in _BEVEGELSESVERB), key=len, reverse=True))
_FELTET = {
    # «Aksjen på Oslo Børs steg» gjelder aksjen, ikke børsen.
    "hovedindeksen": r"(?:hovedindeks(?:en)?|indeksen|osebx|(?<!på\s)oslo\s+børs|børsen)",
    "bransjen": r"(?:bransjen|sektoren|aksjene\s+i\s+(?:samme\s+)?bransje(?:n)?(?:\s+som\s+denne)?)",
}
# Inntil fire ord mellom feltet og verbet: «Hovedindeksen på Oslo Børs steg»,
# «Bransjen i snitt falt». Ikke over et skilletegn.
_MELLOM = r"(?:\s+[\w-]+){0,4}?"
_BEVEGELSE_UTSAGN = {
    felt: (
        re.compile(
            r"(?<![\w-])" + uttrykk + _MELLOM + r"\s+(ikke\s+)?(" + _VERB + r")(?![\w-])(\s+ikke(?![\w-]))?",
            re.IGNORECASE,
        ),
        # Omvendt ordstilling: «I dag steg hovedindeksen», «falt også bransjen».
        re.compile(
            r"(?<![\w-])()(" + _VERB + r")\s+(?:(?:også|derimot|samtidig|i\s+dag)\s+)?" + uttrykk + r"(?![\w-])"
            r"(\s+ikke(?![\w-]))?",
            re.IGNORECASE,
        ),
    )
    for felt, uttrykk in _FELTET.items()
}
# «ni aksjer steg», «9 av aksjene i lista falt», og «tre børsdager på rad».
_AKSJER_UTSAGN = re.compile(
    r"(?<![\w-])(\w+)\s+(?:av\s+(?:de\s+)?(?:\w+\s+)?)?aksje(?:r|ne)?(?:\s+i\s+lista)?\s+(" + _VERB + r")(?![\w-])",
    re.IGNORECASE,
)
_DAGER_UTSAGN = re.compile(r"(?<![\w-])(\w+)\s+(?:børs)?dag(?:er)?\s+på\s+rad", re.IGNORECASE)


def _bevegelsen(verb: str) -> str:
    return _BEVEGELSESVERB[" ".join(verb.lower().split())]


RAAD = (
    r"kjøp",
    r"selg",
    r"salgs",
    r"anbefal",
    r"bør\b",
    r"råd\b",
    r"rådgiv",
    r"investerings\w*",
    r"alternativ for investorer",
    r"kursmål",
    r"behold",
    r"hold(?:e|er)?\b",
    r"oppside",
    r"nedside",
    r"undervurdert",
    r"overvurdert",
    r"attraktiv",
    r"buy\b",
    r"sell\b",
    r"should\b",
)
GJETNING = (
    r"trolig",
    r"sannsynlig",
    r"kan tyde på",
    r"tyder på",
    r"forvent",
    r"ventes",
    r"antyde",
    r"skyld(?:es|tes)",
    r"på grunn av",
    r"grunnet",
    r"som følge av",
    r"drevet av",
    r"kanskje",
    r"mulig",
    r"vil (?:fortsette|stige|falle|øke|synke)",
    r"kommer til å",
    r"spår",
    r"prognose",
    r"neste (?:dag|uke|måned|børsdag)",
    r"i morgen",
    r"fremover",
    r"framover",
    r"kommende",
    r"kan bety",
    r"indikerer",
    r"tegn på",
    r"likely\b",
    r"due to\b",
    r"expected\b",
)
AARSAKER = (
    r"nyhet",
    r"kontrakt",
    r"kvartal",
    r"rapport",
    r"oppkjøp",
    r"fusjon",
    r"emisjon",
    r"utbytte",
    r"børsmelding",
    r"rente",
    r"oljepris",
)

_RAAD = re.compile(r"(?<![a-zæøå])(" + "|".join(RAAD) + r")", re.IGNORECASE)
_GJETNING = re.compile(r"(?<![a-zæøå])(" + "|".join(GJETNING + AARSAKER) + r")", re.IGNORECASE)

_USYNLIGE = dict.fromkeys(map(ord, "­​‌‍⁠﻿"))


@dataclass(frozen=True)
class Kontrollsvar:
    besto: bool
    grunner: tuple[str, ...]

    @property
    def grunn(self) -> str | None:
        """Grunnene som én tekst for KIRad.grunn, eller None."""
        return "; ".join(self.grunner) if self.grunner else None


def _styrketall(ord_: str) -> int | None:
    ord_ = ord_.lower()
    if ord_.isdecimal() and len(ord_) <= _LENGSTE_TALL:
        return int(ord_)
    return STYRKEORD.get(ord_)


def normaliser(tekst: str) -> str:
    """NFC og uten myk bindestrek og usynlige tegn."""
    return unicodedata.normalize("NFC", tekst).translate(_USYNLIGE)


def kontroller(tekst: str, grunnlag: Mapping[str, object]) -> Kontrollsvar:
    """De fire punktene i FR-603. Gir alle grunnene, ikke bare den foerste."""
    if not isinstance(tekst, str):
        raise TypeError("tekst maa vaere en tekst")
    styrke = grunnlag["styrke"]
    if type(styrke) is not int:
        raise TypeError("styrke i grunnlaget maa vaere et heltall")
    retning = grunnlag["retning"]
    if type(retning) is not str:
        raise TypeError("retning i grunnlaget maa vaere en tekst")
    tekst = normaliser(tekst)
    grunner: list[str] = []

    # 1. Retning og styrke, der teksten sier dem.
    for moenster in _RETNING_UTSAGN:
        for treff in moenster.finditer(tekst):
            foran, ikke = treff.group(1), treff.group(2)
            verdi = next(v for v in treff.groups()[2:] if v).lower()
            if foran and (_ANNEN_RETNING.match(foran) or _EN_SJEKK_FORAN.search(foran)):
                continue
            if (verdi == retning.lower()) == bool(ikke):
                grunner.append(f"1: retningen «{treff.group(0)[len(foran) :].strip()}», regelen sier {retning}")
    for moenster in _STYRKE_UTSAGN:
        for treff in moenster.finditer(tekst):
            # Med foran-gruppen («av styrke N») er tallet den siste gruppen.
            if moenster.groups == 2 and _EN_SJEKK_FORAN.search(treff.group(1)):
                continue
            tall = _styrketall(treff.group(moenster.groups))
            if tall is not None and tall != styrke:
                start = len(treff.group(1)) if moenster.groups == 2 else 0
                grunner.append(f"1: styrken «{treff.group(0)[start:]}», regelen sier {styrke}")

    # Story 10.2e: hovedindeksen og bransjen, antallet aksjer og dagene.
    for felt, moenstrene in _BEVEGELSE_UTSAGN.items():
        for moenster in moenstrene:
            for treff in moenster.finditer(tekst):
                ikke, sagt = bool(treff.group(1) or treff.group(3)), _bevegelsen(treff.group(2))
                fasit = grunnlag.get(felt)
                if fasit is None or (sagt == fasit) == ikke:
                    grunner.append(f"1: {felt} «{treff.group(0)}», grunnlaget sier {fasit or 'ingenting'}")
    for treff in _AKSJER_UTSAGN.finditer(tekst):
        tall = _styrketall(treff.group(1))
        felt = {STEG: "aksjer_steg", FALT: "aksjer_falt"}.get(_bevegelsen(treff.group(2)))
        if tall is not None and (felt is None or tall != grunnlag.get(felt)):
            grunner.append(f"1: antallet «{treff.group(0)}», grunnlaget sier {grunnlag.get(felt, 'ingenting')}")
    for treff in _DAGER_UTSAGN.finditer(tekst):
        tall = _styrketall(treff.group(1))
        if tall is not None and tall != grunnlag.get("dager"):
            grunner.append(f"1: dagene «{treff.group(0)}», grunnlaget sier {grunnlag.get('dager', 'ingenting')}")

    # 2. Tallene.
    lovlige = FASTE_TALL | {grunnlag[navn] for navn in ANTALLENE if type(grunnlag.get(navn)) is int}
    for treff in _SIFFER.finditer(tekst):
        tall = treff.group(0)
        if "," in tall or "." in tall or len(tall) > _LENGSTE_TALL or int(tall) not in lovlige:
            grunner.append(f"2: tallet «{tall[: _LENGSTE_TALL + 1]}»")
    if "%" in tekst or "‰" in tekst:
        grunner.append("2: en prosent")
    for treff in _ENHETER.finditer(tekst):
        grunner.append(f"2: «{treff.group(0)}»")
    for treff in _TALLORD_I_TEKST.finditer(tekst):
        if TALLORD.get(treff.group(1).lower()) not in lovlige:
            grunner.append(f"2: tallet «{treff.group(0)}»")

    # 3. Raad.
    for treff in _RAAD.finditer(tekst):
        grunner.append(f"3: «{treff.group(0)}»")

    # 4. Gjetning og aarsaker utenfor grunnlaget.
    for treff in _GJETNING.finditer(tekst):
        grunner.append(f"4: «{treff.group(0)}»")

    return Kontrollsvar(besto=not grunner, grunner=tuple(grunner))
