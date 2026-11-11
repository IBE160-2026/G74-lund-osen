"""Eksempeltekster uten modell - story 10.10, FR-602, FR-603, AD-8.

Ollama skulle ikke startes i 10.10, saa demotekstene i de nye formene
(promptversjon 6 og dag-2) lages av denne skriveren, ikke av Gemma
(spoersmaal 6 i spec-10-10-rikere-ki-tekster.md). Den oppfyller porten Modell
i ki_modell.py, leser opplysningene i prompten og skriver formene fra
reglene ordrett, med tallene og navnene fra opplysningene. Den finner
ingenting selv. Testene bruker den som falsk modell, og kontrollen (FR-603)
leser tekstene som om en modell hadde skrevet dem.

Merket paa siden er modellnavnet, MODELLNAVN, saa ingen tekst ser ut som
den er laget av Gemma (FR-602). Ingen nettkall, ingen fil og ingen klokke.
"""

import json
from collections.abc import Mapping

from ki_modell import Modellsvar
from ki_prompt import setning_om_retningene

MODELLNAVN = "eksempeltekst"
TJENESTE = "lokal"

_OPPLYSNINGENE = "\nOpplysningene:\n"
# UTENFOR i ki_prompt.py: aksjen er ikke blant dem grensene er maalt paa.
MERKET = "Grensene er ikke målt på denne aksjen."
_ORDLYDEN = "Ordlyden om hovedindeksen: "

SJEKKENE = {
    "trend": {
        1: "Trenden ga et positivt utslag fordi kursen ligger over snittet for de siste 50 børsdagene.",
        -1: "Trenden ga et negativt utslag fordi kursen ligger under snittet for de siste 50 børsdagene.",
        0: "Trenden ga ikke utslag fordi kursen ligger nær snittet for de siste 50 børsdagene.",
    },
    "bevegelse": {
        1: "Bevegelsen ga et positivt utslag fordi kursen steg mer enn den vanligvis svinger.",
        -1: "Bevegelsen ga et negativt utslag fordi kursen falt mer enn den vanligvis svinger.",
        0: "Bevegelsen ga ikke utslag fordi dagens endring ikke var stor.",
    },
    "interesse": {
        1: "Interessen ga et positivt utslag fordi det ble handlet mer enn vanlig på en dag kursen steg.",
        -1: "Interessen ga et negativt utslag fordi det ble handlet mer enn vanlig på en dag kursen falt.",
        0: "Interessen ga ikke utslag fordi det ikke ble handlet mye mer enn vanlig.",
    },
}


def opplysningene(prompt: str) -> tuple[dict, str | None]:
    """Opplysningene i prompten som dict, og ordlyden om hovedindeksen naar
    prompten har den."""
    _, _, etter = prompt.partition(_OPPLYSNINGENE)
    linjer = etter.split("\n")
    grunnlag = json.loads(linjer[0])
    ordlyd = next((linje[len(_ORDLYDEN) :] for linje in linjer[1:] if linje.startswith(_ORDLYDEN)), None)
    return grunnlag, ordlyd


def _og(deler: list[str]) -> str:
    """«a», «a og b», «a, b og c»."""
    return deler[0] if len(deler) == 1 else ", ".join(deler[:-1]) + " og " + deler[-1]


def tekst_om_aksjen(grunnlag: Mapping[str, object], ordlyd: str | None = None) -> str:
    """Formene i promptversjon 6 for én aksje: én setning per sjekk,
    ordlyden om hovedindeksen naar den finnes, og én setning per moenster,
    uten tall som er 0."""
    setninger = [SJEKKENE[navn][grunnlag[navn]] for navn in ("trend", "bevegelse", "interesse")]
    if grunnlag.get("merke"):
        setninger.append(MERKET)
    if ordlyd:
        setninger.append(ordlyd)
    # Story 10.10: den ferdige setningen appen gir i prompten (ki_prompt.py).
    setning = setning_om_retningene(grunnlag)
    if setning:
        setninger.append(setning)
    if grunnlag.get("siste_5_samme_vei"):
        setninger.append(
            f"Aksjen gikk samme vei som hovedindeksen {grunnlag['siste_5_samme_vei']} av de "
            f"{grunnlag['siste_5_kunne_telles']} dagene som kunne telles av de siste 5 børsdagene."
        )
    if grunnlag.get("siste_måned_skift"):
        minst = "minst " if grunnlag.get("siste_måned_merke") else ""
        setninger.append(f"Den siste måneden skiftet retningen {minst}{grunnlag['siste_måned_skift']} ganger.")
    return " ".join(setninger)


def tekst_om_dagen(grunnlag: Mapping[str, object]) -> str:
    """Formene i promptversjon dag-2: hovedindeksen, bedre enn indeksen, de
    som skilte seg ut med retningene og navnene, og bransjene med hoeyest og
    lavest snitt. Bare feltene som finnes, og ingen retning med 0."""
    setninger = []
    ukedag = grunnlag["ukedag"]
    indeksen = grunnlag.get("hovedindeksen")
    if indeksen == "uendret":
        setninger.append(f"Hovedindeksen var uendret {ukedag}.")
    elif indeksen in ("steg", "falt"):
        setninger.append(f"Hovedindeksen {indeksen} {ukedag}.")
    if "bedre_enn_indeksen" in grunnlag:
        setninger.append(
            f"{grunnlag['bedre_enn_indeksen']} av {grunnlag['med_kurs']} aksjer gjorde det bedre enn indeksen."
        )
    ut = grunnlag["skilte_seg_ut"]
    if not ut:
        setninger.append("Ingen aksjer skilte seg ut.")
    else:
        retninger = []
        for felt, ord_ in (
            ("skilte_seg_ut_positiv", "positiv"),
            ("skilte_seg_ut_negativ", "negativ"),
            ("skilte_seg_ut_blandet", "blandet"),
        ):
            if grunnlag.get(felt):
                retninger.append(f"{grunnlag[felt]} {'med ' if not retninger else ''}{ord_}")
        retninger[0] += " retning"
        setninger.append(f"{ut} skilte seg ut: {_og(retninger)}.")
    navnene = [f"{n['navn']} ({n['styrke']} av 3, {n['retning']})" for n in grunnlag.get("skilte_seg_ut_navn") or ()]
    if navnene:
        if grunnlag.get("skilte_seg_ut_andre"):
            navnene.append(f"{grunnlag['skilte_seg_ut_andre']} andre")
        setninger.append(f"Blant dem var {_og(navnene)}.")
    if "bransje_mest_opp" in grunnlag:
        setninger.append(f"I snitt steg {str(grunnlag['bransje_mest_opp']).lower()} mest.")
    if "bransje_mest_ned" in grunnlag:
        setninger.append(f"I snitt falt {str(grunnlag['bransje_mest_ned']).lower()} mest.")
    # Tillegget kl. 17:21 (spoersmaal 11 og 12).
    if "skilte_seg_ut_vanlig" in grunnlag:
        mot = {"flere": "flere enn", "færre": "færre enn", "like mange": "like mange som"}[
            grunnlag["skilte_seg_ut_mot_vanlig"]
        ]
        setninger.append(f"Det var {mot} vanlig: snittet de siste 20 børsdagene er {grunnlag['skilte_seg_ut_vanlig']}.")
    uka = grunnlag.get("hovedindeksen_uka")
    if uka == "uendret":
        setninger.append("De siste fem børsdagene var hovedindeksen uendret.")
    elif uka in ("steg", "falt"):
        setninger.append(f"De siste fem børsdagene {uka} hovedindeksen.")
    return " ".join(setninger)


class EksempelModell:
    """Porten Modell uten modell: teksten er formene fra reglene, med
    opplysningene i prompten. Teksten om dagen kjennes paa feltet aksjer."""

    tjeneste = TJENESTE
    modell = MODELLNAVN

    def __init__(self) -> None:
        self.promptene: list[str] = []

    def lag_tekst(self, prompt: str) -> Modellsvar:
        self.promptene.append(prompt)
        grunnlag, ordlyd = opplysningene(prompt)
        tekst = tekst_om_dagen(grunnlag) if "aksjer" in grunnlag else tekst_om_aksjen(grunnlag, ordlyd)
        return Modellsvar(tekst=tekst, modell=MODELLNAVN)
