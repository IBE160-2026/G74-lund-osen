"""KI-teksten i aksjedetaljen - story 10.3, FR-601, FR-602, NFR-04, NFR-05,
NFR-06.

Ren logikk: av raden i KILogg og vurderingen som vises, regnes det som skal
staa paa siden. Regelforklaringen (FR-706) staar alltid foerst, og
KI-teksten under den, merket som laget av KI, med modellnavnet og
tjenesten (FR-602). En dag uten KI-tekst sier det, og hvorfor, i stedet for
aa vise et tomt felt.

KI-teksten vises bare naar grunnlaget i raden stemmer med vurderingen som
vises: samme styrke, samme retning og samme fortegn for de tre sjekkene
(FR-602). Er vurderingen skrevet paa nytt samme dag, vises dagen uten
KI-tekst (svar 3 kl. 15:53).

En vakt paa vaar side (NFR-06): en tekst med «kjøp», «selg» eller «anbefal»
vises ikke, selv om den besto kontrollen i FR-603. Den staar i loggen.

Webserveren skriver aldri i loggen og kaller aldri en modell (AD-10), saa
denne fila importerer verken ki_modell eller ki_lokal.

Bryteren (FR-601, svar 4) er en informasjonskapsel. 8.10b flytter den til
innstillingene og bruker samme kapsel.
"""

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass

from kilogg import KIRad
from vurderingsdata import Vurdering

KAPSEL = "ose_ki"
PAA = "paa"
AV = "av"

# NFR-06: ordene vakten stopper, uansett boeyning og ogsaa inni et
# sammensatt ord («salgsanbefaling», «aksjekjøp»). Vakten er grov: den
# stopper ogsaa en beskrivelse som «mange kjøpere», og da er dagen uten
# KI-tekst, ikke feil (gjennomgangen av 10.3, BH3, ECH, VG4).
_VAKT = re.compile(r"(kjøp|kjop|selg|solg|salg|anbefal|tilr[åa]d)", re.IGNORECASE)
_USYNLIGE = dict.fromkeys(map(ord, "\u00ad\u200b\u200c\u200d\u2060\ufeff"))

VIST = "vist"
INGEN_RAD = "ingen_rad"
# Svar kl. 23:57: andre aksjer har rader for dagen, men ikke denne.
INGEN_FOR_AKSJEN = "ingen_for_aksjen"
MODELLEN_FEILET = "modellen_feilet"
BESTO_IKKE = "besto_ikke"
STEMMER_IKKE = "stemmer_ikke"
STOPPET_AV_VAKTEN = "stoppet_av_vakten"

GRUNNER = {
    # Svar kl. 23:57 15.10: siden sier hvorfor med det loggen kan vise. Den
    # noeyaktige grunnen staar i utskriften fra hentingen (FR-601).
    INGEN_RAD: "Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk.",
    INGEN_FOR_AKSJEN: "Ingen KI-tekst for denne aksjen: teksten ble ikke laget i hentingen.",
    MODELLEN_FEILET: "Ingen KI-tekst for denne dagen: modellen svarte ikke da hentingen gikk.",
    BESTO_IKKE: "Ingen KI-tekst for denne dagen: teksten sa mer enn regelen, og ble ikke vist.",
    STEMMER_IKKE: "Ingen KI-tekst for denne dagen: vurderingen er skrevet på nytt etter at teksten ble laget.",
    STOPPET_AV_VAKTEN: "Ingen KI-tekst for denne dagen: teksten ble stoppet, fordi den kunne leses som et råd.",
}


@dataclass(frozen=True)
class KIVisning:
    tilstand: str
    tekst: str | None = None
    modell: str | None = None

    @property
    def vist(self) -> bool:
        return self.tilstand == VIST

    @property
    def grunn(self) -> str | None:
        return GRUNNER.get(self.tilstand)


def stemmer(grunnlag: Mapping[str, object], vurdering: Vurdering) -> bool:
    """FR-602: samme styrke, samme retning og samme fortegn for de tre.
    Verdiene for de tre er fortegnene selv (-1, 0 eller 1), saa de
    sammenlignes som de er."""
    return all(grunnlag.get(navn) == getattr(vurdering, navn)
               for navn in ("trend", "bevegelse", "interesse", "styrke", "retning"))


def bygg_ki_visning(rad: KIRad | None, vurdering: object, dagen_har_rader: bool = False) -> KIVisning:
    """Det siden viser under regelforklaringen. dagen_har_rader sier om andre
    aksjer har rader i KI-loggen for dagen (svar kl. 23:57)."""
    if rad is None:
        return KIVisning(INGEN_FOR_AKSJEN if dagen_har_rader else INGEN_RAD)
    if rad.modellen_feilet:
        return KIVisning(MODELLEN_FEILET)
    if not rad.besto:
        return KIVisning(BESTO_IKKE)
    if not isinstance(vurdering, Vurdering):
        # Ingen vurdering aa forklare. Siden viser da ingen KI-del, men skulle
        # den, er dette den riktige grunnen (gjennomgangen, BH5).
        return KIVisning(INGEN_RAD)
    if not stemmer(rad.grunnlag, vurdering):
        return KIVisning(STEMMER_IKKE)
    tekst = unicodedata.normalize("NFC", rad.tekst).translate(_USYNLIGE)
    if _VAKT.search(tekst):
        return KIVisning(STOPPET_AV_VAKTEN)
    return KIVisning(VIST, tekst=rad.tekst, modell=f"{rad.modell}, {rad.tjeneste}")


def ki_paa(kapsel: str | None) -> bool:
    """Bryteren: paa naar kapselen mangler eller sier paa (FR-601)."""
    return kapsel != AV
