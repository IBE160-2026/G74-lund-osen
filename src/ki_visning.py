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

from markupsafe import Markup, escape

from dagsgrunnlag import for_promptversjon
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
# Loggen kunne ikke leses, eller det er ingen vurdering aa forklare. Da vet
# siden ikke hvorfor, og sier ingen grunn (gjennomgangen av PR 2, BH3, ECH, VG3).
UKJENT = "ukjent"
MODELLEN_FEILET = "modellen_feilet"
BESTO_IKKE = "besto_ikke"
STEMMER_IKKE = "stemmer_ikke"
STOPPET_AV_VAKTEN = "stoppet_av_vakten"
# Story 8.2b, b (U6): demoen har KI-tekst bare for siste boersdag, saa grunnen
# i INGEN_RAD stemmer ikke der.
INGEN_I_DEMOEN = "ingen_i_demoen"
# Story 3.7 (tillegg 1, spoersmaal 8 i spesifikasjonen): i den ekte versjonen
# er en dag uten rad i KI-loggen en dag uten modell, slik siden kan se det
# uten ny migrasjon. En tekst kontrollen stoppet, har en rad. Siden lenker
# til installasjonen, og demoen er som foer.
INGEN_MODELL = "ingen_modell"

GRUNNER = {
    # Svar kl. 23:57 15.10: siden sier hvorfor med det loggen kan vise. Den
    # noeyaktige grunnen staar i utskriften fra hentingen (FR-601).
    INGEN_RAD: "Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk.",
    INGEN_FOR_AKSJEN: "Ingen KI-tekst for denne aksjen: teksten ble ikke laget i hentingen.",
    UKJENT: "Ingen KI-tekst for denne dagen.",
    MODELLEN_FEILET: "Ingen KI-tekst for denne dagen: modellen svarte ikke da hentingen gikk.",
    BESTO_IKKE: "Ingen KI-tekst for denne dagen: teksten sa mer enn regelen, og ble ikke vist.",
    STEMMER_IKKE: "Ingen KI-tekst for denne dagen: vurderingen er skrevet på nytt etter at teksten ble laget.",
    STOPPET_AV_VAKTEN: "Ingen KI-tekst for denne dagen: teksten ble stoppet, fordi den kunne leses som et råd.",
    INGEN_I_DEMOEN: "Ingen KI-tekst for denne dagen: demoen har KI-tekst bare for siste børsdag.",
    INGEN_MODELL: "Ingen KI-tekst for denne dagen. Den lages når kursene hentes, på en maskin med en språkmodell.",
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
    return all(
        grunnlag.get(navn) == getattr(vurdering, navn)
        for navn in ("trend", "bevegelse", "interesse", "styrke", "retning")
    )


def bygg_ki_visning(rad: KIRad | None, vurdering: object, *, andre_har_rader: bool) -> KIVisning:
    """Det siden viser under regelforklaringen. andre_har_rader sier om andre
    aksjer har rader i KI-loggen for dagen (svar kl. 23:57). Hver kaller maa
    si det (gjennomgangen av PR 2, BH6)."""
    if rad is None:
        return KIVisning(INGEN_FOR_AKSJEN if andre_har_rader else INGEN_RAD)
    if rad.modellen_feilet:
        return KIVisning(MODELLEN_FEILET)
    if not rad.besto:
        return KIVisning(BESTO_IKKE)
    if not isinstance(vurdering, Vurdering):
        # Ingen vurdering aa forklare. Siden viser da ingen KI-del, men skulle
        # den, sier den ingen grunn (gjennomgangen, BH5, og av PR 2, ECH).
        return KIVisning(UKJENT)
    if not stemmer(rad.grunnlag, vurdering):
        return KIVisning(STEMMER_IKKE)
    tekst = unicodedata.normalize("NFC", rad.tekst).translate(_USYNLIGE)
    if _VAKT.search(tekst):
        return KIVisning(STOPPET_AV_VAKTEN)
    return KIVisning(VIST, tekst=rad.tekst, modell=f"{rad.modell}, {rad.tjeneste}")


# Story 8.2b, c (U67): et tall i teksten, delt som kontrollen deler det
# (_SIFFER i ki_kontroll.py), saa tallet som er markert, er det som er proevd
# mot grunnlaget (designregler §4). En tekst som vises, har bare hele tall fra
# grunnlaget, uten prosent (FR-603, punkt 2). Gjennomgangen av 8.2b (BH4,
# ECH4, VG5): ikke fortegn, prosent eller tusenskille, som kontrollen.
_TALL = re.compile(r"\d+(?:[.,]\d+)?")


def prikkede_tall(tekst: str) -> Markup:
    """Teksten med hvert tall i <span class="tall">, som siden gir prikket
    strek i tekstfargen (designregler §4). Teksten er alt proevd mot
    grunnlaget (FR-603), og ingenting i den endres: delene escapes hver for
    seg, saa et tegn som & aldri blir en del av et tall."""
    # Gjennomgangen av 8.2b (VG5): samme deling som kontrollen.
    deler = []
    forrige = 0
    for treff in _TALL.finditer(tekst):
        deler.append(escape(tekst[forrige : treff.start()]))
        deler.append(Markup('<span class="tall">') + escape(treff.group()) + Markup("</span>"))
        forrige = treff.end()
    deler.append(escape(tekst[forrige:]))
    return Markup("").join(deler)


# Story 8.20a (U88, gruppens svar 07.11 kl. 12:32, 4): navnet paa hver sjekk
# med fet skrift første gang det staar i teksten, som i skissen
# aksjesiden-ki-paa.png. Ubestemt og bestemt form, med stor eller liten
# forbokstav, som versjon 5 skriver dem («Trenden ga …»).
# Gjennomgangen av 8.20a (ECH6): ogsaa «trendsjekken» og «trend-sjekken», som
# kontrollen godtar, hele ordet.
SJEKKNAVN = re.compile(
    r"\b(?:trend(?:en)?|bevegelsen?|interessen?)(?:-?sjekken)?(?![\w-])",
    re.IGNORECASE,
)


def ki_tekst(tekst: str) -> Markup:
    """Teksten med tallene som i prikkede_tall og navnet paa hver sjekk i
    <strong> første gang det staar. Ingenting i teksten endres: et navn som
    staar inni et tall eller et ord, blir ikke fett."""
    deler = []
    forrige = 0
    sett = set()
    for treff in SJEKKNAVN.finditer(tekst):
        sjekk = treff.group().lower()[:5]
        if sjekk in sett:
            continue
        sett.add(sjekk)
        deler.append(prikkede_tall(tekst[forrige : treff.start()]))
        deler.append(Markup("<strong>") + escape(treff.group()) + Markup("</strong>"))
        forrige = treff.end()
    deler.append(prikkede_tall(tekst[forrige:]))
    return Markup("").join(deler)


# Story 10.6 (FR-607, utdraget 08.11 §3): «Børsdagen kort fortalt» paa
# forsiden. Tekstene uten KI-tekst staar ordrett fra utdraget.
DAGEN_UTEN = "Dagen er uten KI-tekst."
# Story 3.7 (tillegg 1): dagen har ingen rad i KI-loggen, i den ekte versjonen.
DAGEN_UTEN_MODELL = "Dagen er uten KI-tekst. Den lages når kursene hentes, på en maskin med en språkmodell."
PERIODEN_UTEN = "Perioden er uten KI-tekst. Teksten skrives for én børsdag om gangen."
DAGEN_AV = "KI-teksten er slått av. Tabellen over viser bare det reglene har regnet ut."


@dataclass(frozen=True)
class Dagsvisning:
    """Teksten om dagen og modellen, eller ingen tekst (DAGEN_UTEN)."""

    tekst: str | None = None
    modell: str | None = None

    @property
    def vist(self) -> bool:
        return self.tekst is not None


def _vanlig(verdi):
    """Grunnlaget som vanlige dict paa alle nivaaer, saa et grunnlag lest fra
    loggen kan sammenlignes med et som er regnet naa. Story 10.10: en liste
    fra loggen er en tuple, og blir en liste."""
    if isinstance(verdi, Mapping):
        return {n: _vanlig(v) for n, v in verdi.items()}
    if isinstance(verdi, (list, tuple)):
        return [_vanlig(v) for v in verdi]
    return verdi


def bygg_dagsvisning(rad: KIRad | None, grunnlag: Mapping[str, object] | None) -> Dagsvisning:
    """Teksten om dagen vises bare naar den besto kontrollen, grunnlaget i
    raden er det samme som grunnlaget regnet av det siden viser (FR-607), og
    vakta ikke stopper den (NFR-06). Ellers er dagen uten KI-tekst.

    Story 10.10 (spoersmaal 5): en rad med promptversjon dag-1 sammenlignes
    med grunnlaget uten feltene dag-2 la til, saa tekstene fra foer
    flettingen fortsatt vises."""
    if rad is None or grunnlag is None or not rad.besto or rad.tekst is None:
        return Dagsvisning()
    grunnlag = for_promptversjon(grunnlag, rad.promptversjon)
    if rad.emne.slag != "dag" or _vanlig(rad.grunnlag) != _vanlig(grunnlag):
        return Dagsvisning()
    tekst = unicodedata.normalize("NFC", rad.tekst).translate(_USYNLIGE)
    if _VAKT.search(tekst):
        return Dagsvisning()
    # Gjennomgangen (VG5): modellen og tjenesten, som paa aksjesiden (FR-602).
    return Dagsvisning(tekst=rad.tekst, modell=f"{rad.modell} ({rad.tjeneste})")


def ki_paa(kapsel: str | None) -> bool:
    """Bryteren: paa naar kapselen mangler eller sier paa (FR-601)."""
    return kapsel != AV
