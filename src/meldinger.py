"""Deduplisering og kategorifilter for boersmeldinger - FR-501 til FR-503.

Ren logikk. Ingen API-kall, ingen filer. NewsWeb koster uansett ingen kvote,
men grovsorteringen her avgjoer hvor mye KI-laget faar aa gjoere: 121 hentede
meldinger over fire uker blir ca 35 til forklaring og ca 13 til
relevansvurdering.

Rekkefoelgen er bestemt: deduplisering foerst, kategorifilter etterpaa
(FR-501). Motsatt rekkefoelge ville talt dubletter som passerte filteret to
ganger.
"""

from dataclasses import dataclass

SLIPPER_GJENNOM = "slipper_gjennom"
KI_AVGJOER = "ki_avgjoer"
FILTRERES_BORT = "filtreres_bort"
UTBYTTEMERKING = "utbyttemerking"
UKJENT = "ukjent"

# Kategoriene slik de staar i FR-502. Hver kategori hoerer til noeyaktig
# en boette.
BOETTER: dict[str, str] = {
    "INNSIDEINFORMASJON": SLIPPER_GJENNOM,
    "HALVÅRSRAPPORT": SLIPPER_GJENNOM,
    "ANNEN INFORMASJONSPLIKTIG REGULATORISK INFORMASJON": SLIPPER_GJENNOM,
    "FLAGGING": SLIPPER_GJENNOM,
    "MELDEPLIKTIG HANDEL FOR PRIMÆRINNSIDERE": SLIPPER_GJENNOM,
    "IKKE-INFORMASJONSPLIKTIGE PRESSEMELDINGER": KI_AVGJOER,
    "UTSTEDERS MELDEPLIKT VED HANDEL I EGNE AKSJER": FILTRERES_BORT,
    "RENTEREGULERING": FILTRERES_BORT,
    "ENDRINGER I RETTIGHETENE TIL AKSJER/VERDIPAPIRER": FILTRERES_BORT,
    "EKS.DATO": UTBYTTEMERKING,
}

NORSK = "no"
ENGELSK = "en"
UAVKLART = ""

NORSKE_SPRAAKKODER = {"no", "nb", "nn", "nor", "norsk"}
ENGELSKE_SPRAAKKODER = {"en", "eng", "engelsk", "en-gb", "en-us"}

# Heuristikken under brukes bare naar meldingen ikke baerer en spraakkode.
NORSKE_BOKSTAVER = set("æøåÆØÅ")

NORSKE_ORD = {
    "aksjer",
    "aksjonaerer",
    "egne",
    "emisjon",
    "finansiell",
    "generalforsamling",
    "handel",
    "innkalling",
    "kvartal",
    "kvartalsrapport",
    "melding",
    "meldeplikt",
    "og",
    "resultat",
    "selskapet",
    "styret",
    "tildeling",
    "utbytte",
    "vedtak",
}

ENGELSKE_ORD = {
    "and",
    "announces",
    "awarded",
    "board",
    "contract",
    "dividend",
    "general",
    "meeting",
    "notice",
    "of",
    "quarter",
    "quarterly",
    "report",
    "results",
    "shares",
    "the",
    "trading",
}


@dataclass(frozen=True)
class Melding:
    """Feltene NewsWeb leverer, slik vi bruker dem.

    issuer er `issuerSign` - meldingen er allerede knyttet til utsteder av
    boersen, saa KI brukes aldri til aa avgjoere hvilket selskap en melding
    gjelder.
    """

    id: str
    issuer: str
    kategori: str
    publisert: str
    tittel: str
    spraak: str = ""


def _normaliser(kategori: str) -> str:
    return " ".join(kategori.strip().upper().split())


def _minutt(tidspunkt: str) -> str:
    """Kutter sekunder og finere opploesning bort.

    Dublettkjennetegnet er samme publiseringsminutt (FR-501). To oversettelser
    av samme melding legges ut samtidig, men ikke noedvendigvis i samme
    sekund.
    """
    return tidspunkt[:16]


def _ord(tittel: str) -> set[str]:
    renset = "".join(tegn.lower() if tegn.isalpha() else " " for tegn in tittel)
    return set(renset.split())


def gjett_spraak(tittel: str) -> str:
    """Gjetter spraak ut fra tittelen. Returnerer NORSK, ENGELSK eller UAVKLART.

    Brukes bare naar meldingen ikke baerer en spraakkode fra NewsWeb.

    AE, OE og AA avgjoer alene - de finnes ikke i engelske titler. Ellers
    telles kjente ord mot hverandre. Staar det likt, eller finnes ingen
    holdepunkter, er svaret UAVKLART, og da gjetter vi ikke.
    """
    if any(bokstav in NORSKE_BOKSTAVER for bokstav in tittel):
        return NORSK

    ord = _ord(tittel)
    norske = len(ord & NORSKE_ORD)
    engelske = len(ord & ENGELSKE_ORD)

    if norske > engelske:
        return NORSK
    if engelske > norske:
        return ENGELSK
    return UAVKLART


def spraak(melding: Melding) -> str:
    """Spraakkoden fra NewsWeb naar den finnes, ellers gjetning paa tittelen.

    [ANTAKELSE] At NewsWeb i det hele tatt leverer en spraakkode, er ikke
    verifisert mot et ekte svar. Feltene vi har dokumentert, er issuerSign,
    issuerName, category, publishedTime og title. Kontrollen koster ingen
    kvote og staar paa lista til 21.09.
    """
    kode = melding.spraak.strip().lower()
    if kode in NORSKE_SPRAAKKODER:
        return NORSK
    if kode in ENGELSKE_SPRAAKKODER:
        return ENGELSK
    return gjett_spraak(melding.tittel)


def er_norsk(melding: Melding) -> bool:
    return spraak(melding) == NORSK


def dedupliser(meldinger: list[Melding]) -> list[Melding]:
    """Fjerner spraakdubletter: samme utsteder, kategori og publiseringsminutt.

    32 av 121 meldinger (26 %) var samme melding paa norsk og engelsk.

    Den norske beholdes naar begge finnes, fordi grensesnittet og
    KI-forklaringene er paa norsk. Finnes bare en av dem, beholdes den.

    Kan ingen av dem avgjoeres som norske, beholdes den foerste. Da har vi
    ikke grunnlag for aa velge, og et vilkaarlig valg forkledd som en regel
    er verre enn en aapen foerstemann-regel.
    """
    beholdt: dict[tuple[str, str, str], Melding] = {}
    rekkefolge: list[tuple[str, str, str]] = []

    for melding in meldinger:
        nokkel = (
            melding.issuer.strip().upper(),
            _normaliser(melding.kategori),
            _minutt(melding.publisert),
        )
        if nokkel not in beholdt:
            beholdt[nokkel] = melding
            rekkefolge.append(nokkel)
        elif er_norsk(melding) and not er_norsk(beholdt[nokkel]):
            beholdt[nokkel] = melding

    return [beholdt[nokkel] for nokkel in rekkefolge]


def boette(melding: Melding) -> str:
    """Hvilken av boettene i FR-502 kategorien hoerer til.

    Ukjente kategorier gaar til UKJENT. De vises for brukeren merket «ukjent
    kategori» og loggfoeres, men de sendes ikke til KI-laget: prompten er
    skrevet for samlekategorien og ville gjettet paa noe den ikke er
    kalibrert for. Etter en ukes drift plasseres kategoriene som faktisk
    dukket opp - aapent punkt 15.
    """
    return BOETTER.get(_normaliser(melding.kategori), UKJENT)


def filtrer(meldinger: list[Melding]) -> dict[str, list[Melding]]:
    """Sorterer meldinger i boetter. Dedupliser foerst (FR-501).

    Returnerer alle boettene, ogsaa de tomme, slik at kallende kode kan telle
    hva som ble sortert vekk. Meldinger i EKS.DATO vises ikke i lista, men
    forkastes ikke - de er datakilden til utbyttemerkingen (FR-503).
    """
    resultat: dict[str, list[Melding]] = {
        SLIPPER_GJENNOM: [],
        KI_AVGJOER: [],
        FILTRERES_BORT: [],
        UTBYTTEMERKING: [],
        UKJENT: [],
    }
    for melding in meldinger:
        resultat[boette(melding)].append(melding)
    return resultat


def til_ki_vurdering(sortert: dict[str, list[Melding]]) -> list[Melding]:
    """Meldingene KI-laget skal relevansvurdere: bare samlekategorien.

    Egen funksjon fordi regelen er lett aa bryte ved et uhell. Ukjente
    kategorier ser ut som en naturlig kandidat - de er jo nettopp det vi ikke
    vet hva er - men de skal ikke dit.
    """
    return list(sortert[KI_AVGJOER])
