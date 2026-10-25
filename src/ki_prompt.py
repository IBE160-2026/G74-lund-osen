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
ber derfor modellen forklare regelen med «fordi». Kontrollen ble ikke endret
i versjon 2.

Versjon 3 (story 10.2e, gruppens svar 21.10 kl. 22:57 og 23:51 og 24.10 kl.
15:50 og 16:15): opplysningene har ogsaa dagene, hovedindeksen, antallene
fra boersometeret og bransjen, og reglene forklarer dem med ord. Teksten
kan vise til tallene paa siden uten aa gjenta dem. Prompten nevner fortsatt
bare regelens faste tall, saa en modell som gjentar den, ikke stoppes av
punkt 2 i kontrollen.

Versjon 3 rettet (gruppens svar 24.10 kl. 21:49, malinger.md §43): én sjekk
omtales med navnet, «ingen sjekk» brukes bare naar styrken er 0, hver sjekk
beskrives slik fortegnet er, og «minst» om dagene brukes bare med merket, og
da alltid. Versjonen staar som 3, fordi versjon 3 ikke var flettet.

Versjon 3, tredje forsoek (gruppens svar 24.10 kl. 23:23, malinger.md §44):
modellen faar ferdig ordlyd for dagene, laget her av dagene og merket, og
nevner dagene bare med den, ordrett. «Minst» staar bare i ordlyden, ikke i
reglene. Kontrollen i FR-603 bruker den samme ordlyden (ordlyd_for_dagene),
saa prompten og kontrollen ikke kan si ulikt (tatt ut i fjerde forsoek). Ordlyden, og koden som velger
den og setter prompten sammen, er med i avtrykket (gjennomgangen 25.10, VG2).

Versjon 3, fjerde forsoek (gruppens svar 25.10 kl. 00:50 og 00:51,
malinger.md §46): modellen faar ikke dagene og nevner dem ikke. Ordlyden fra
tredje forsoek er tatt ut, og reglene sier at teksten ikke sier hvor lenge
signalet har vart. Appen skriver dagene selv, under KI-teksten paa
aksjesiden (setning_om_dagene i dagene.py). Versjonen staar som 3, og
avtrykket dekker reglene, merket og lag_prompt.

Versjon 3, grunnen i prompten (story 10.2f, gruppens svar 25.10 kl. 18:34
og 18:35): siden sier ikke lenger «for første gang» (svaret kl. 12:12 a), saa
grunnen er «Siden sier under teksten hvor lenge signalet har vart.» Regelen
for modellen staar. Versjonen staar som 3, og det er et unntak fra regelen
om ny versjon oeverst: ingen tekst i ose.db var laget med versjon 3 ennaa.
Avtrykket er satt paa nytt, og demotekstene og proevekjoeringen
(malinger.md §47) er laget paa nytt, saa alle tekster med versjon 3 i ose.db
og i demoen er laget med samme prompt. Tekstene med versjon 3 i
proevekjoeringene foer §47 (§43-§46) og i historikken til
demo_ki_tekster.json er laget med den gamle grunnen (gjennomgangen, BH1).
"""

import json
from collections.abc import Mapping

PROMPTVERSJON = "3"

REGLER = """Du skriver en kort forklaring på norsk av et regelbasert signal for én aksje på Oslo Børs.
Forklaringen skal være lett å forstå for en som ikke kjenner reglene. Skriv to eller tre hele setninger.

Signalet bygger på tre sjekker. Hver gir et positivt utslag, et negativt utslag eller ikke noe utslag:
- trend: om kursen ligger over eller under snittet for de siste 50 børsdagene.
- bevegelse: om dagens endring var stor sammenlignet med de siste 20 dagene.
- interesse: om det ble handlet mer enn vanlig. Fortegnet for interessen følger dagens kursendring, ikke volumet: et positivt utslag betyr stor handel på en dag kursen steg, og et negativt utslag stor handel på en dag kursen falt.
Styrken er hvor mange av sjekkene som ga utslag. Retningen er Positiv, Negativ, Blandet eller Ingen.
I opplysningene under står 1 for positivt utslag, -1 for negativt og 0 for ikke noe utslag.

Opplysningene sier også hvordan dagen var:
- hovedindeksen: om hovedindeksen på Oslo Børs steg, falt eller var uendret i dag. Mangler feltet, skal du ikke si noe om hovedindeksen.
- aksjer_steg og aksjer_falt: hvor mange av aksjene i lista som steg og som falt fra børsdagen før.
- bransjen: om aksjene i samme bransje som denne steg, falt eller var uendret i snitt. Mangler feltet, skal du ikke si noe om bransjen.

Regler for teksten:
- Beskriv hver sjekk slik fortegnet står i opplysningene: et positivt utslag, et negativt utslag eller ikke noe utslag. Ikke si at en sjekk ga utslag når den ikke ga det, eller at den ga et annet utslag enn det som står.
- Når du sier noe om én sjekk, bruk navnet på sjekken, for eksempel «interessen ga ikke utslag». Skriv «ingen sjekk» bare når styrken er 0.
- Bruk bare opplysningene under. Skriv utslagene med ord, ikke som tall. Ikke nevn kurser, prosenter eller andre tall enn antallene i opplysningene og regelens faste tall.
- Siden viser kursen, endringen og målingene. Du kan vise til dem, for eksempel «se endringen i tabellen», men ikke gjenta tallene.
- Hovedindeksen og bransjen er ikke en del av regelen. Ikke si at de forklarer signalet.
- Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier under teksten hvor lenge signalet har vart.
- Ikke gi råd om å kjøpe, selge eller holde, og ikke si noe om hva som vil skje.
- Ikke gjett på årsaker, som nyheter, resultater eller kontrakter. Du kan forklare regelen, for eksempel at en sjekk ikke ga utslag.
- Når du forklarer regelen, bruk «fordi». Ikke bruk «skyldes» eller «indikerer».
"""

UTENFOR = "\nAksjen er ikke blant aksjene grensene er målt på. Si at grensene ikke er målt på denne aksjen.\n"


def lag_prompt(grunnlag: Mapping[str, object]) -> str:
    """Reglene og grunnlaget som JSON. Ingenting annet kommer med."""
    prompt = REGLER
    if grunnlag.get("merke"):
        prompt += UTENFOR
    return prompt + "\nOpplysningene:\n" + json.dumps(dict(grunnlag), ensure_ascii=False, sort_keys=True) + "\n"
