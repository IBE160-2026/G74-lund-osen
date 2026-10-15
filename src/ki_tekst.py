"""KI-teksten i hentekommandoen - story 10.2, PR F, FR-603, FR-604, FR-608,
NFR-04, AD-17.

Hentekommandoen kaller lag_ki_tekster etter at dagens vurderinger er skrevet
(AD-17), og bare da. For hver aksje med en vurdering for boersdagen og ingen
rad i KILogg kalles modellen én gang (lag_ki_rad i ki_modell.py), og raden
skrives. Finnes raden, staar den, ogsaa naar modellen feilet, og modellen
kalles ikke (FR-604, svar 2 kl. 15:53). En aksje med en grunn i stedet for
vurdering faar ingen KI-tekst: det er ingenting aa forklare.

Rekkefoelgen er vurdering, saa KI-rad, hver i sin transaksjon (punktet i
deferred-work.md fra 4.3). Stopper kjoeringen mellom dem, staar vurderingen
uten KI-rad, og siden viser en dag uten KI-tekst (FR-602). Kjoeres samme
kommando igjen samme kveld, lages radene som mangler, med 0 kall til EODHD.

Ingenting her kan stoppe hentingen eller endre utgangskoden (NFR-04): en
feil skrives ut og steget stopper. Passerer kjoeringen midnatt i Oslo,
avviser KILogg datoen (IkkeInnevaerendeBoersdag), og steget stopper med
beskjed (punktet i deferred-work.md fra 4.2). Utskriften har antall, aldri
teksten eller tall fra kildene (regel 16).

Ingen kall til EODHD gaar herfra: steget leser bare basen.

velg_modell leser OSE_KI_TJENESTE og OSE_KI_OLLAMA_URL (svar 5 og 8):
«av» gir ingen modell, og uten variabelen gjelder «lokal» (FR-608). Det er
én tjeneste per kjoering, uten stille overgang til en annen.
"""

from collections.abc import Callable, Mapping
from datetime import date, datetime
from pathlib import Path

from dotenv import dotenv_values

from ki_grunnlag import ki_grunnlag
from ki_lokal import STANDARD_URL, OllamaModell
from ki_modell import Modell, lag_ki_rad
from kilogg import Emne, IkkeInnevaerendeBoersdag
from kursdata import AKSJEUNIVERS, Aksje
from lagring_sqlite import SqliteKILogg, SqliteVurderingslager, aapne_base
from vurderingsdata import Vurdering

AV = "av"
LOKAL = "lokal"
# Tjenestene i FR-608 som kommer med egen noekkel i story 10.7.
SENERE = ("gemini", "anthropic", "openai")

_NOEKLER = ("OSE_KI_TJENESTE", "OSE_KI_OLLAMA_URL")


def ki_innstillinger(env_fil: Path, miljoe: Mapping[str, str]) -> dict[str, str]:
    """OSE_KI_* fra miljoeet, ellers fra .env. Bare de to noeklene leses, og
    .env leses bare naar miljoeet ikke har OSE_KI_TJENESTE, saa en test som
    setter den, aldri leser fila."""
    if "OSE_KI_TJENESTE" in miljoe:
        return {n: miljoe[n] for n in _NOEKLER if n in miljoe}
    fra_fil = dotenv_values(env_fil) if env_fil.is_file() else {}
    innstillinger = {n: fra_fil[n] for n in _NOEKLER if fra_fil.get(n) is not None}
    innstillinger.update({n: miljoe[n] for n in _NOEKLER if n in miljoe})
    return innstillinger


def velg_modell(innstillinger: Mapping[str, str], skriv: Callable[[str], None] = print) -> Modell | None:
    """Modellen for kjoeringen, eller None naar KI er av eller ikke kan brukes."""
    tjeneste = (innstillinger.get("OSE_KI_TJENESTE") or LOKAL).strip().lower()
    if tjeneste == AV:
        return None
    if tjeneste == LOKAL:
        return OllamaModell(url=(innstillinger.get("OSE_KI_OLLAMA_URL") or STANDARD_URL).strip())
    if tjeneste in SENERE:
        skriv(f"OSE_KI_TJENESTE={tjeneste} er ikke bygget ennaa (story 10.7). Ingen KI-tekst i kveld.")
    else:
        skriv("OSE_KI_TJENESTE har en ukjent verdi. Bruk lokal eller av. Ingen KI-tekst i kveld.")
    return None


def regeltekst(vurdering: Vurdering) -> str:
    """Det regelen sa, med fortegnene, styrken og retningen (FR-604)."""
    def tegn(verdi: int) -> str:
        return f"+{verdi}" if verdi > 0 else str(verdi)

    return (
        f"Trend {tegn(vurdering.trend)}, bevegelse {tegn(vurdering.bevegelse)}, "
        f"interesse {tegn(vurdering.interesse)}. Styrke {vurdering.styrke}, "
        f"retning {vurdering.retning}."
    )


def lag_ki_tekster(
    base_sti: Path,
    dato: date,
    klokke: Callable[[], datetime],
    modell: Modell | None,
    skriv: Callable[[str], None] = print,
    lista: tuple[Aksje, ...] = AKSJEUNIVERS,
) -> None:
    """KI-raden for hver aksje som har en vurdering og mangler raden."""
    if modell is None:
        return
    try:
        tilkobling = aapne_base(base_sti)
    except Exception as feil:  # NFR-04: KI-laget stopper aldri hentingen.
        skriv(f"KI-teksten: basen kunne ikke aapnes ({type(feil).__name__}). Ingen KI-tekst i kveld.")
        return
    besto = stoppet = feilet = sto = 0
    try:
        vurderinger = SqliteVurderingslager(tilkobling, klokke, lista)
        logg = SqliteKILogg(tilkobling, klokke)
        for aksje in lista:
            vurdering = vurderinger.les(aksje.symbol, dato)
            if not isinstance(vurdering, Vurdering):
                continue
            emne = Emne.aksje(aksje.symbol, dato)
            if logg.les(emne) is not None:
                sto += 1
                continue
            rad = lag_ki_rad(emne, ki_grunnlag(vurdering, utenfor_maalingen=False),
                             regeltekst(vurdering), modell)
            if not logg.skriv(rad):
                sto += 1
                continue
            if rad.besto:
                besto += 1
            elif rad.modellen_feilet:
                feilet += 1
            else:
                stoppet += 1
    except IkkeInnevaerendeBoersdag:
        skriv(
            f"KI-teksten stoppet: det er blitt en ny boersdag siden kjoeringen startet, og "
            f"radene for {dato.isoformat()} kan ikke skrives lenger (AD-7). "
            f"{besto + stoppet + feilet} rader ble skrevet."
        )
        return
    except Exception as feil:  # NFR-04: KI-laget stopper aldri hentingen.
        skriv(f"KI-teksten stoppet etter {besto + stoppet + feilet} rader: {type(feil).__name__}.")
        return
    finally:
        tilkobling.close()
    skriv(
        f"KI-tekst for boersdagen {dato.isoformat()} ({modell.tjeneste}, {modell.modell}): "
        f"{besto} besto kontrollen, {stoppet} ble stoppet av kontrollen, og modellen feilet "
        f"for {feilet}." + (f" {sto} rader sto fra foer og er ikke laget paa nytt." if sto else "")
    )
