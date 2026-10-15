"""Prompten til modellen - story 10.2, FR-603, FR-605, NFR-05, NFR-06.

Promptversjonen lagres med hver tekst (FR-605). Endres teksten under, eller
reglene den gir modellen, faar den en ny versjon, saa eksempelsettet ikke
blir flere systemer som ser ut som ett.

Prompten sier at fortegnet for interessen foelger dagens kursendring og ikke
volumet. Det er laerdommen fra Gemma i C-med i malinger.md §19, der teksten
sa at interessen var negativ fordi volumet var lavt.
"""

import json
from collections.abc import Mapping

PROMPTVERSJON = "1"

_REGLER = """Du skriver en kort forklaring på norsk av et regelbasert signal for én aksje på Oslo Børs.
Forklaringen skal være lett å forstå for en som ikke kjenner reglene. Skriv to eller tre hele setninger.

Signalet bygger på tre sjekker. Hver gir +1, 0 eller -1:
- trend: om kursen ligger over eller under snittet for de siste 50 børsdagene.
- bevegelse: om dagens endring var stor sammenlignet med de siste 20 dagene.
- interesse: om det ble handlet mer enn vanlig. Fortegnet for interessen følger dagens kursendring, ikke volumet: +1 betyr stor handel på en dag kursen steg, og -1 stor handel på en dag kursen falt.
Styrken er hvor mange av sjekkene som ga utslag (0 til 3). Retningen er Positiv, Negativ, Blandet eller Ingen.

Regler for teksten:
- Bruk bare opplysningene under. Ikke nevn kurser, prosenter eller andre tall enn styrken og regelens faste tall.
- Ikke gi råd om å kjøpe, selge eller holde, og ikke si noe om hva som vil skje.
- Ikke gjett på årsaker, som nyheter, resultater eller kontrakter. Du kan forklare regelen, for eksempel at ingen sjekk ga utslag.
"""

_UTENFOR = "\nAksjen er utenfor de 15 aksjene grensene er målt på. Si at grensene ikke er målt på denne aksjen.\n"


def lag_prompt(grunnlag: Mapping[str, object]) -> str:
    """Reglene og grunnlaget som JSON. Ingenting annet kommer med."""
    prompt = _REGLER
    if grunnlag.get("merke"):
        prompt += _UTENFOR
    return prompt + "\nOpplysningene:\n" + json.dumps(dict(grunnlag), ensure_ascii=False, sort_keys=True) + "\n"
