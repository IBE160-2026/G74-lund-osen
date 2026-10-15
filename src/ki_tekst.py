"""KI-teksten i hentekommandoen - story 10.2, PR F, FR-603, FR-604, FR-608,
NFR-04, AD-17.

Hentekommandoen kaller lag_ki_tekster etter at dagens vurderinger er skrevet
(AD-17), og bare da. For hver aksje med en vurdering for boersdagen og ingen
rad i KILogg kalles modellen én gang (lag_ki_rad i ki_modell.py), og raden
skrives. Finnes raden, staar den, ogsaa naar modellen feilet, og modellen
kalles ikke (FR-604, svar 2 kl. 15:53). En aksje med en grunn i stedet for
vurdering faar ingen KI-tekst: det er ingenting aa forklare.

Feiler modellen for én aksje, kalles den ikke for resten den kvelden. De
faar en rad om at den feilet, som FR-604 krever, uten aa vente paa en
tidsfrist til for hver (gjennomgangen av PR F, BH3).

Rekkefoelgen er vurdering, saa KI-rad, hver i sin transaksjon (punktet i
deferred-work.md fra 4.3). Stopper kjoeringen mellom dem, lager samme
kommando kjoert igjen radene som mangler: med 0 kall til EODHD naar basen har
kursene, og foer et nytt forsoek naar den ikke har det.

Ingenting her kan stoppe hentingen eller endre utgangskoden (NFR-04): en
feil skrives ut, med sporet paa stderr, og steget stopper. Er det blitt en
ny boersdag i Oslo, kalles ikke modellen, og steget stopper med beskjed
(punktet i deferred-work.md fra 4.2). Utskriften har antall, aldri teksten
eller tall fra kildene (regel 16).

Ingen kall til EODHD gaar herfra: steget leser bare basen.

velg_modell leser OSE_KI_TJENESTE og OSE_KI_OLLAMA_URL (svar 5 og 8):
«av» gir ingen modell, og uten variabelen gjelder «lokal» (FR-608). Det er
én tjeneste per kjoering, uten stille overgang til en annen.
"""

import sys
import traceback
from collections.abc import Callable, Mapping
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

from boersdag import innevaerende_boersdag, norsk_dato
from ki_grunnlag import ki_grunnlag
from ki_lokal import STANDARD_URL, OllamaModell
from ki_modell import Modell, lag_ki_rad
from kilogg import Emne, IkkeInnevaerendeBoersdag, KIRad
from kursdata import AKSJEUNIVERS, Aksje
from lagring_sqlite import SqliteKILogg, SqliteVurderingslager, aapne_base
from vurderingsdata import Vurdering

AV = "av"
LOKAL = "lokal"
# Tjenestene i FR-608 som kommer med egen noekkel i story 10.7.
SENERE = ("gemini", "anthropic", "openai")
# Adressene som er paa maskinen eller i compose. En annen adresse sender
# prompten dit, og hentingen sier fra (gjennomgangen av PR F, BH13).
LOKALE_VERTER = ("127.0.0.1", "localhost", "::1", "ollama")

_NOEKLER = ("OSE_KI_TJENESTE", "OSE_KI_OLLAMA_URL")


def ki_innstillinger(env_fil: Path, miljoe: Mapping[str, str]) -> dict[str, str]:
    """OSE_KI_* per noekkel: miljoeet foerst, saa .env. Bare de to noeklene
    tas med. Sier miljoeet «av», leses ikke fila, saa testene (conftest.py)
    aldri leser den."""
    innstillinger = {n: miljoe[n] for n in _NOEKLER if n in miljoe}
    if innstillinger.get("OSE_KI_TJENESTE", "").strip().lower() == AV:
        return innstillinger
    if env_fil.is_file():
        fra_fil = dotenv_values(env_fil)
        for n in _NOEKLER:
            if n not in innstillinger and fra_fil.get(n) is not None:
                innstillinger[n] = fra_fil[n]
    return innstillinger


def velg_modell(innstillinger: Mapping[str, str], skriv: Callable[[str], None] = print) -> Modell | None:
    """Modellen for kjoeringen, eller None naar KI er av eller ikke kan brukes."""
    verdi = innstillinger.get("OSE_KI_TJENESTE")
    tjeneste = LOKAL if verdi is None else verdi.strip().lower()
    if tjeneste == AV:
        return None
    if tjeneste == LOKAL:
        url = (innstillinger.get("OSE_KI_OLLAMA_URL") or STANDARD_URL).strip()
        deler = urlsplit(url)
        if deler.scheme not in ("http", "https") or not deler.hostname:
            skriv("OSE_KI_OLLAMA_URL er ikke en adresse som http://127.0.0.1:11434. Ingen KI-tekst i kveld.")
            return None
        if deler.hostname not in LOKALE_VERTER:
            skriv(f"OSE_KI_OLLAMA_URL peker til {deler.hostname}, ikke til maskinen. Prompten sendes dit.")
        return OllamaModell(url=url)
    if tjeneste in SENERE:
        skriv(f"OSE_KI_TJENESTE={tjeneste} er ikke bygget ennaa (story 10.7). Ingen KI-tekst i kveld.")
    else:
        skriv("OSE_KI_TJENESTE har en ukjent eller tom verdi. Bruk lokal eller av. Ingen KI-tekst i kveld.")
    return None


def modell_fra_miljoeet(env_fil: Path, miljoe: Mapping[str, str],
                        skriv: Callable[[str], None] = print) -> Modell | None:
    """Det main kaller. Kan innstillingene ikke leses, blir det ingen KI-tekst,
    og hentingen gaar som foer (NFR-04)."""
    try:
        return velg_modell(ki_innstillinger(env_fil, miljoe), skriv)
    except Exception as feil:  # NFR-04: KI-laget stopper aldri hentingen.
        skriv(f"KI-teksten: innstillingene kunne ikke leses ({type(feil).__name__}). Ingen KI-tekst i kveld.")
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


def _rad_uten_kall(emne: Emne, vurdering: Vurdering, modell: Modell, foerste: str) -> KIRad:
    from ki_prompt import PROMPTVERSJON

    return KIRad(
        emne=emne, grunnlag=ki_grunnlag(vurdering, utenfor_maalingen=False),
        regelen=regeltekst(vurdering), tekst=None, besto=False,
        grunn=f"modellen feilet: ikke kalt, fordi den feilet for {foerste} i samme kjoering",
        promptversjon=PROMPTVERSJON, tjeneste=modell.tjeneste, modell=modell.modell,
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
    besto = stoppet = feilet = sto = 0

    def antall() -> str:
        tekst = f"{besto + stoppet + feilet} rader ble skrevet"
        return tekst + (f", og {sto} sto fra foer" if sto else "")

    try:
        tilkobling = aapne_base(base_sti)
    except Exception as feil:  # NFR-04: KI-laget stopper aldri hentingen.
        skriv(f"KI-teksten: basen kunne ikke aapnes ({type(feil).__name__}). Ingen KI-tekst i kveld.")
        return
    try:
        vurderinger = SqliteVurderingslager(tilkobling, klokke, lista)
        logg = SqliteKILogg(tilkobling, klokke)
        feilet_for: str | None = None
        for aksje in lista:
            vurdering = vurderinger.les(aksje.symbol, dato)
            if not isinstance(vurdering, Vurdering):
                continue
            emne = Emne.aksje(aksje.symbol, dato)
            if logg.les(emne) is not None:
                sto += 1
                continue
            if innevaerende_boersdag(norsk_dato(klokke())) != dato:
                raise IkkeInnevaerendeBoersdag(dato.isoformat())
            if feilet_for is None:
                rad = lag_ki_rad(emne, ki_grunnlag(vurdering, utenfor_maalingen=False),
                                 regeltekst(vurdering), modell)
                if rad.modellen_feilet:
                    feilet_for = aksje.symbol
            else:
                rad = _rad_uten_kall(emne, vurdering, modell, feilet_for)
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
            f"radene for {dato.isoformat()} kan ikke skrives lenger (AD-7). {antall()}."
        )
        return
    except AssertionError:
        # Nettsperren i testene (NettverkISTest) skal synes, ikke svelges.
        raise
    except Exception as feil:  # NFR-04: KI-laget stopper aldri hentingen.
        skriv(f"KI-teksten stoppet etter {besto + stoppet + feilet} rader: {type(feil).__name__}. {antall()}.")
        traceback.print_exc(file=sys.stderr)
        return
    finally:
        tilkobling.close()
    skriv(
        f"KI-tekst for boersdagen {dato.isoformat()} ({modell.tjeneste}, {modell.modell}): "
        f"{besto} besto kontrollen, {stoppet} ble stoppet av kontrollen, og modellen feilet "
        f"for {feilet}." + (f" {sto} rader sto fra foer og er ikke laget paa nytt." if sto else "")
    )
