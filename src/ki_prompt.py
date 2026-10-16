"""Prompten til modellen - story 10.2, FR-603, FR-605, NFR-05, NFR-06.

Promptversjonen lagres med hver tekst (FR-605). Endres teksten under, eller
reglene den gir modellen, faar den en ny versjon, saa eksempelsettet ikke
blir flere systemer som ser ut som ett. En test binder teksten til
versjonen med en sha256.

Prompten sier at fortegnet for interessen foelger dagens kursendring og ikke
volumet. Det er laerdommen fra Gemma i C-med i malinger.md §19, der teksten
sa at interessen var negativ fordi volumet var lavt.

Prompten bruker ingen tall kontrollen i FR-603 ville stoppe hvis modellen
gjentok dem: fortegnene beskrives med ord, og antallet aksjer i maalingen
nevnes ikke (gjennomgangen av PR E). Bare regelens faste tall (50 og 20)
staar der.

Versjon 2 (gruppens beslutning 16.10 kl. 22:33): i proevekjoeringen
(malinger.md §32) stoppet punkt 4 i kontrollen 9 av 15 tekster, paa
«skyldes» og «indikerer», ogsaa der ordet bare forklarte regelen. Prompten
ber derfor modellen forklare regelen med «fordi». Kontrollen er uendret.
"""

import json
from collections.abc import Mapping

PROMPTVERSJON = "2"

REGLER = """Du skriver en kort forklaring på norsk av et regelbasert signal for én aksje på Oslo Børs.
Forklaringen skal være lett å forstå for en som ikke kjenner reglene. Skriv to eller tre hele setninger.

Signalet bygger på tre sjekker. Hver gir et positivt utslag, et negativt utslag eller ikke noe utslag:
- trend: om kursen ligger over eller under snittet for de siste 50 børsdagene.
- bevegelse: om dagens endring var stor sammenlignet med de siste 20 dagene.
- interesse: om det ble handlet mer enn vanlig. Fortegnet for interessen følger dagens kursendring, ikke volumet: et positivt utslag betyr stor handel på en dag kursen steg, og et negativt utslag stor handel på en dag kursen falt.
Styrken er hvor mange av sjekkene som ga utslag. Retningen er Positiv, Negativ, Blandet eller Ingen.
I opplysningene under står 1 for positivt utslag, -1 for negativt og 0 for ikke noe utslag.

Regler for teksten:
- Bruk bare opplysningene under. Skriv utslagene med ord, ikke som tall. Ikke nevn kurser, prosenter eller andre tall enn styrken og regelens faste tall.
- Ikke gi råd om å kjøpe, selge eller holde, og ikke si noe om hva som vil skje.
- Ikke gjett på årsaker, som nyheter, resultater eller kontrakter. Du kan forklare regelen, for eksempel at ingen sjekk ga utslag.
- Når du forklarer regelen, bruk «fordi». Ikke bruk «skyldes» eller «indikerer».
"""

UTENFOR = "\nAksjen er ikke blant aksjene grensene er målt på. Si at grensene ikke er målt på denne aksjen.\n"


def lag_prompt(grunnlag: Mapping[str, object]) -> str:
    """Reglene og grunnlaget som JSON. Ingenting annet kommer med."""
    prompt = REGLER
    if grunnlag.get("merke"):
        prompt += UTENFOR
    return prompt + "\nOpplysningene:\n" + json.dumps(dict(grunnlag), ensure_ascii=False, sort_keys=True) + "\n"
