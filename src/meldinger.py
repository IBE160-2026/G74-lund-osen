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

NORSKE_SPRAAKKODER = {"no", "nb", "nn", "nor", "norsk"}


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
    """Kutter sekunder og finere oppløsning bort.

    Dublettkjennetegnet er samme publiseringsminutt (FR-501). To oversettelser
    av samme melding legges ut samtidig, men ikke noedvendigvis i samme
    sekund.
    """
    return tidspunkt[:16]


def er_norsk(melding: Melding) -> bool:
    return melding.spraak.strip().lower() in NORSKE_SPRAAKKODER


def dedupliser(meldinger: list[Melding]) -> list[Melding]:
    """Fjerner spraakdubletter: samme utsteder, kategori og publiseringsminutt.

    32 av 121 meldinger (26 %) var samme melding paa norsk og engelsk.

    Den norske beholdes naar begge finnes, fordi grensesnittet og
    KI-forklaringene er paa norsk. Finnes bare en av dem, beholdes den.

    [ANTAKELSE] Spraaket leses av feltet `spraak`. Hvilket felt NewsWeb
    faktisk bruker, er ikke verifisert mot et ekte svar. Det koster ingen
    kvote aa kontrollere. Uten spraakinformasjon beholdes den foerste, slik at
    ingen melding forsvinner stille.
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

    Ukjente kategorier gaar til UKJENT, ikke til bortfiltrering. En kategori
    vi ikke har sett foer, kan vaere en ny meldingstype paa boersen, og den
    skal oppdages - ikke forsvinne. Hvor den skal ende, er ikke avgjort i
    PRD-en.
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
