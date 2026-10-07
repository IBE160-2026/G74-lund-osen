"""Henter sluttkurser for OSE Signal sitt aksjeunivers fra EODHD.

Dette scriptet er det eneste stedet i prosjektet som bruker API-kvote.
Ett kall per symbol, 15 symboler, altsaa 15 kall per kjoering. Gratisnivaaet
gir 20 kall i doegnet, saa det er plass til EN kjoering per dag og litt til.
Kjoer det bevisst - ikke i loekke, og aldri fra websiden.

Hvert kall henter et helt aar. Det koster noeyaktig det samme som aa hente
fjorten dager - ett kall per symbol uansett intervallengde, maalt og foert i
malinger.md §2 - og MA50 trenger 51 handelsdager foer signalet i det hele tatt
kan regnes. Aa hente kort ville derfor kostet like mye og gitt en tom
signalkolonne.

Resultatet skrives som et tidsstemplet oeyeblikksbilde som aldri skrives om
(FR-406, NFR-07), i formatet visningen leser gjennom lagring_fil.SnapshotLeser.

Story 2.1b: fila skrives foerst, i data/raa/ (AD-6), og deretter kursene til
basen i data/db/ose.db, med samme hentet. Feiler basen, staar fila, og den kan
leses inn senere uten kall: fetch_prices.py --les-inn <fil>. Innlesingen gaar
samme vei til basen, skriver bare kurs og kursserie (aldri vurdering, AD-7),
leser ingen noekkel og gjoer ingen kall.

Tid (AD-20, story 2.1): klokka leses en gang, i UTC, naar kjoeringen starter.
Datoen i filnavnet og i intervallet er norsk kalenderdato for det oeyeblikket,
og hentet er det samme oeyeblikket i UTC med offset. Ingen kode her leser
maskinens lokale sone.

Story 2.5: etter kursene skriver hentingen dagens vurdering for alle femten i
samme kjoering (AD-17), regnet av seriene den selv lagret, lest tilbake fra
basen. Kan en aksje ikke vurderes, skrives en rad med grunnen (punkt 24).
Boersdagen raden gjelder, regnes en gang, fra samme oeyeblikk som filnavnet.

Story 2.3 (FR-401, FR-402): foer foerste kall sjekker kjoer() i fast
rekkefoelge klokka, tidskontrollen, basen, filvakten, noekkelen og kvoten.
Hver sjekk som sier nei, gir 0 kall og en utskrift som sier hvorfor. Paa en
boersdag foer kl. 22:00 hentes ingenting uten --hent-foer-kl-22. Har basen
alt kursene for boersdagen for alle aksjene, hentes ingenting. Kvoten leses
med /api/user (gratis), den andre nettfunksjonen mot EODHD (AD-2).
"""

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import quote, quote_plus

import requests
from dotenv import load_dotenv

import lagring_fil
import lagring_sqlite
from boersdag import (
    OSLO,
    UtenforKalenderen,
    er_boersdag,
    innevaerende_boersdag,
    norsk_dato,
)
from eodhd import UgyldigSerie, serie_fra_eodhd
from kursdata import AKSJEUNIVERS, Kursrad
from lagring_fil import (
    KURSPREFIKS,
    PROSJEKTROT,
    SnapshotKilde,
    SnapshotLeser,
    _hentet_fra_tekst,
)
from lagring_sqlite import SqliteKurslager, SqliteVurderingslager, aapne_base
from migrering import MigrasjonsFeil
from signalberegning import vurder
from vurderingsdata import Grunn

BASE_URL = "https://eodhd.com/api/eod"
KVOTE_URL = "https://eodhd.com/api/user"

# Story 2.3: paa en boersdag hentes ingenting foer dette klokkeslettet i Oslo,
# uten flagget --hent-foer-kl-22. En kjoering som kommer for tidlig, bruker
# dagens kall uten aa faa dagens rad.
KL_22 = time(22, 0)

# Gratisnivaaet gir ett aars historikk. 364 dager holder seg innenfor med en
# dags margin - det var intervallet som faktisk svarte 2026-09-21, og det ga
# 249 handelsdager per symbol.
DAGER_TILBAKE = 364

# MA50 spiser 50 dager. Under dette kan ingen aksje faa et signal.
MINST_HANDELSDAGER = 51


@dataclass
class Resultat:
    """Hva en kjoering endte med. Kallene telles uansett om de lyktes."""

    serier: dict[str, list[dict]] = field(default_factory=dict)
    feil: dict[str, str] = field(default_factory=dict)
    kall_brukt: int = 0


def hent_api_nokkel() -> str:
    load_dotenv(PROSJEKTROT / ".env")
    nokkel = os.getenv("EODHD_API_KEY")
    if not nokkel:
        sys.exit("EODHD_API_KEY mangler. Legg den i .env i prosjektroten.")
    return nokkel


def naa() -> datetime:
    """Klokka, i UTC. Leses en gang per kjoering, av main (AD-20).

    Egen funksjon, saa testene kan bytte den ut, slik SqliteVurderingslager
    tar klokka inn.
    """
    return datetime.now(timezone.utc)


def bygg_intervall(i_dag: date) -> tuple[str, str]:
    """Fra- og til-dato for hentingen. Begge inklusive, jf. malinger.md §2.

    i_dag er norsk kalenderdato (AD-20), regnet av kjoer.
    """
    return (i_dag - timedelta(days=DAGER_TILBAKE)).isoformat(), i_dag.isoformat()


def hent_ett_symbol(ticker: str, api_nokkel: str, fra: str, til: str) -> list[dict]:
    """Ett API-kall. Eneste funksjonen i prosjektet som roerer nettet.

    Noekkelen gaar som api_token i adressen, og requests tar med hele
    adressen i teksten til sine feil. Enhver feil fra kallet og
    raise_for_status() blir derfor en ny feil med en tekst uten adressen
    (story 2.0): statuskode og aarsak for en HTTP-feil, bare typenavnet for
    resten. from None kutter kjeden, saa heller ikke en traceback viser den
    gamle teksten. Den nye HTTPError faar ingen response, fordi response.url
    ogsaa har noekkelen. svar.json() ligger utenfor: en feil der er om
    innholdet, ikke adressen, og andre lag i hent_universet fanger resten.
    """
    try:
        svar = requests.get(
            f"{BASE_URL}/{ticker}",
            params={
                "api_token": api_nokkel,
                "fmt": "json",
                "period": "d",
                "from": fra,
                "to": til,
            },
            timeout=60,
        )
        svar.raise_for_status()
    except requests.HTTPError as feil:
        r = feil.response
        tekst = f"HTTP {r.status_code} {r.reason or ''}".strip() if r is not None else "HTTPError"
        raise requests.HTTPError(tekst) from None
    except requests.RequestException as feil:
        raise type(feil)(type(feil).__name__) from None
    return svar.json()


def hent_kvote(api_nokkel: str) -> object:
    """/api/user - story 2.3. Den andre nettfunksjonen mot EODHD (AD-2).

    Kallet er gratis og trekker ikke fra kvoten (regel 15). Feilene vaskes
    som i hent_ett_symbol (story 2.0), fordi noekkelen staar i adressen.
    Svaret gis tilbake uten tolkning; tolk_kvote leser det.
    """
    try:
        svar = requests.get(
            KVOTE_URL,
            params={"api_token": api_nokkel, "fmt": "json"},
            timeout=30,
        )
        svar.raise_for_status()
    except requests.HTTPError as feil:
        r = feil.response
        tekst = f"HTTP {r.status_code} {r.reason or ''}".strip() if r is not None else "HTTPError"
        raise requests.HTTPError(tekst) from None
    except requests.RequestException as feil:
        raise type(feil)(type(feil).__name__) from None
    return svar.json()


class UlesbarKvote(ValueError):
    """Svaret fra /api/user kan ikke leses. Teksten nevner bare feltnavn,
    aldri en verdi fra svaret."""


def tolk_kvote(svar: object, i_dag_gmt: date) -> tuple[int, int]:
    """(kall igjen av dagens, bonuskvoten extraLimit) - story 2.3, regel 15.

    Kvoten nullstilles ved midnatt GMT, men /api/user viser gaarsdagens tall
    til foerste kall etter det. Staar apiRequestsDate paa en tidligere dato
    enn i_dag_gmt, er det brukt 0 i dag. i_dag_gmt er dagens dato i GMT, ikke
    i Oslo (presisert 04.10). Bare de fire feltene leses; navn og e-post i
    svaret roeres ikke. Reiser UlesbarKvote hvis et felt mangler eller har
    feil form.
    """
    if not isinstance(svar, dict):
        raise UlesbarKvote("svaret er ikke et objekt")

    def heltall(navn: str) -> int:
        verdi = svar.get(navn)
        if isinstance(verdi, bool) or not isinstance(verdi, int):
            raise UlesbarKvote(f"{navn} mangler eller er ikke et heltall")
        return verdi

    brukt = heltall("apiRequests")
    grense = heltall("dailyRateLimit")
    bonus = heltall("extraLimit")
    try:
        dato = date.fromisoformat(svar.get("apiRequestsDate"))
    except (TypeError, ValueError):
        raise UlesbarKvote("apiRequestsDate mangler eller kan ikke leses") from None
    if dato < i_dag_gmt:
        brukt = 0
    return max(grense - brukt, 0), max(bonus, 0)


def _uten_noekkel(tekst: str, api_nokkel: str) -> str:
    """Noekkelen byttet med *** - andre lag, for feil som ikke kom fra requests.

    Ogsaa slik den ser ut URL-kodet, fordi requests koder params."""
    if not api_nokkel:
        return tekst
    for form in {api_nokkel, quote(api_nokkel, safe=""), quote_plus(api_nokkel)}:
        tekst = tekst.replace(form, "***")
    return tekst


def hent_universet(
    api_nokkel: str,
    fra: str,
    til: str,
    hent: Callable[[str, str, str, str], list[dict]] = hent_ett_symbol,
    skriv: Callable[[str], None] = print,
) -> Resultat:
    """Ett kall per aksje i universet. Stopper aldri paa en enkelt feil.

    Hentingen er injisert saa testene kan kjoere hele loekka uten nett.

    Et symbol som feiler gir ingen ny sjanse - det ville kostet et kall til,
    og kvoten er for liten til aa brenne kall paa en feil vi ikke har
    forstaatt. De andre symbolene hentes likevel: en halv oversikt er bedre
    enn ingen, og NFR-03 sier at manglende data for en aksje ikke skal stoppe
    hovedflyten.
    """
    resultat = Resultat()

    for aksje in AKSJEUNIVERS:
        try:
            rader = hent(aksje.ticker, api_nokkel, fra, til)
            resultat.kall_brukt += 1
        except Exception as feil:  # noqa: BLE001 - alt som feiler har kostet kallet
            resultat.kall_brukt += 1
            resultat.feil[aksje.symbol] = _uten_noekkel(
                f"{type(feil).__name__}: {feil}", api_nokkel
            )
            skriv(f"  {aksje.symbol}: FEIL {_uten_noekkel(str(feil), api_nokkel)}")
            continue

        # Story 2.0, valg A: et svar med feil form skal ikke stoppe hele
        # hentingen etter at kallene er brukt (AD-15, NFR-03). Formen sjekkes
        # foerst, saa et tomt objekt eller None ikke fores som «tomt svar».
        # Story 1.8: formen er det SnapshotLeser kan lese, avgjort av samme
        # funksjon. En serie leseren ville droppet, lagres ikke som hentet.
        try:
            serie = serie_fra_eodhd(rader)
        except UgyldigSerie:
            resultat.feil[aksje.symbol] = "svar med feil form"
            skriv(f"  {aksje.symbol}: svar med feil form")
            continue

        if not serie:
            resultat.feil[aksje.symbol] = "tomt svar"
            skriv(f"  {aksje.symbol}: ingen data")
            continue

        # Raadataene lagres uendret. Oversettelsen er bare kontrollen.
        resultat.serier[aksje.symbol] = rader
        merknad = "" if len(serie) >= MINST_HANDELSDAGER else "  ← for kort for MA50"
        skriv(
            f"  {aksje.symbol}: {len(serie)} dager, "
            f"siste {serie[-1].dato.isoformat()}{merknad}"
        )

    return resultat


def lag_oyeblikksbilde(resultat: Resultat, fra: str, til: str, naa: str) -> dict:
    """Formatet visningen leser gjennom lagring_fil.SnapshotLeser. Skrives
    aldri om etterpaa."""
    return {
        "hentet": naa,
        "from": fra,
        "to": til,
        "kilde": "EODHD /api/eod",
        "serier": resultat.serier,
        "feil": resultat.feil,
    }


def filnavn(i_dag: date) -> str:
    """Datoen staar i navnet, saa oeyeblikksbilder aldri overskriver hverandre.

    i_dag er norsk kalenderdato (AD-20), regnet av kjoer.

    Prefikset kommer fra lagring_fil og skrives ikke av her. nyeste_snapshot lar
    nettopp dette prefikset vinne ved lik dato, saa de to maa ikke kunne gli
    fra hverandre.
    """
    return f"{KURSPREFIKS}-raa-{i_dag.isoformat()}.json"


# Feil som betyr at basen ikke kunne aapnes eller skrives. En ValueError fra
# erstatt_serie gjelder bare ett symbol og fanges for seg.
BASEFEIL = (sqlite3.Error, OSError, MigrasjonsFeil, RuntimeError)


def skriv_til_basen(
    base_sti: Path,
    serier: dict[str, list[Kursrad]],
    hentet: datetime,
    fil: Path,
    skriv: Callable[[str], None] = print,
) -> set[str] | None:
    """Kursene fra ett oeyeblikksbilde til basen - story 2.1b.

    Den ene veien til basen, for hentingen og for innlesingen. Hvert symbol i
    serier faar erstatt_serie med samme hentet som fila. Et symbol som ikke
    er med i serier (feilet i hentingen), roeres ikke (AD-15). Bare kurs og
    kursserie skrives, aldri vurdering (AD-7).

    Per symbol sammenlignes hentet med sist_hentet i basen (svar A, 29.09):
    er fila eldre, hoppes symbolet over med en melding som nevner fila,
    symbolet og begge tidene. Lik tid godtas, saa samme fil kan leses inn to
    ganger. Et symbol som avvises (ValueError, fra porten eller basen),
    nevnes, og de andre skrives. Feiler basen etter at noen serier er
    skrevet, sier meldingen hvor mange.

    Returnerer symbolene som ble skrevet (story 2.5). Alt ble skrevet naar
    alle symbolene i serier er med. Et symbol som ble hoppet over eller
    avvist, er ikke med. None hvis basen ikke kunne aapnes eller skrives; da
    staar fila, og meldingen sier hvordan den leses inn.
    """
    try:
        tilkobling = aapne_base(base_sti)
    except BASEFEIL as feil:
        _basen_feilet(feil, base_sti, fil, 0, skriv)
        return None

    skrevne: set[str] = set()
    try:
        lager = SqliteKurslager(tilkobling)
        for symbol, rader in serier.items():
            forrige = lager.sist_hentet(symbol)
            if forrige is not None and hentet < forrige:
                skriv(
                    f"  {symbol}: hoppet over. {fil.name} er hentet "
                    f"{hentet.isoformat()}, og basen har en serie hentet "
                    f"{forrige.isoformat()}. En eldre fil skriver ikke over en "
                    "nyere serie."
                )
                continue
            try:
                lager.erstatt_serie(symbol, rader, hentet)
            except ValueError as feil:
                skriv(f"  {symbol}: avvist og ikke skrevet: {feil}")
                continue
            skrevne.add(symbol)
    except BASEFEIL as feil:
        _basen_feilet(feil, base_sti, fil, len(skrevne), skriv)
        return None
    finally:
        tilkobling.close()

    skriv(f"Skrev {len(skrevne)} serier til basen {base_sti.name}.")
    return skrevne


def _basen_feilet(
    feil: BaseException, base_sti: Path, fil: Path, skrevet: int, skriv
) -> None:
    alt = (
        f"{skrevet} serier var alt skrevet; --les-inn skriver dem paa nytt.\n"
        if skrevet
        else ""
    )
    skriv(
        f"Basen {base_sti} kunne ikke skrives: {type(feil).__name__}: {feil}\n"
        f"{alt}"
        f"Fila {fil} staar. Les den inn uten kall med:\n"
        f"  uv run python src/fetch_prices.py --les-inn {fil}"
    )


def _kan_skrives_til(dato: date) -> str:
    return (
        f"En rad for {dato.isoformat()} kan bare skrives saa lenge den er "
        "inneveerende boersdag (AD-7)."
    )


def _stoppet_ved_midnatt(dato: date, skrevet: int, skriv, aarsak: str = "") -> None:
    skriv(
        f"Kjoeringen gikk over midnatt i Oslo. Vurderingene for {dato.isoformat()} "
        f"er stoppet etter {skrevet} rader, og datoen regnes ikke paa nytt."
        f"{' ' + aarsak if aarsak else ''} Kursene og fila staar. "
        f"{_kan_skrives_til(dato)}"
    )


def skriv_vurderinger(
    base_sti: Path,
    dato: date,
    dag: date,
    skrevne: set[str],
    klokke: Callable[[], datetime],
    skriv: Callable[[str], None] = print,
) -> bool:
    """Dagens rad for hver aksje i universet - story 2.5, FR-408, AD-17.

    dato er boersdagen raden gjelder, regnet en gang av kjoer. dag er
    kalenderdagen kjoeringen startet, og er ulik dato bare naar boersen er
    stengt. Seriene leses tilbake fra basen etter at alle er skrevet, saa
    vurderingen er regnet av det basen har fra denne kjoeringen. Bare
    symbolene i skrevne vurderes; de andre faar SYMBOL_FEILET (AD-15). En
    kjoering som fullfoerer, gir aldri en aksje uten rad. Stopper den ved
    midnatt eller fordi basen feiler, mangler resten, og meldingen sier det.

    En dag boersen er stengt, staar en rad som finnes for dato fra foer
    (svar 1, 02.10). En grunn skriver aldri over en vurdering (punkt 24).
    Lageret avgjoer det, og raden nevnes som en som sto fra foer.

    Klokka gaar til lageret, som avviser en dato som ikke lenger er
    inneveerende boersdag. Skjer det midt i universet, stopper skrivingen og
    sier fra. Returnerer True hvis hver aksje fikk eller hadde en rad.
    Utskriften har ingen kurser og ingen maalinger (regel 16).
    """
    try:
        tilkobling = aapne_base(base_sti)
    except BASEFEIL as feil:
        skriv(
            f"Basen {base_sti} kunne ikke aapnes for vurderingene: "
            f"{type(feil).__name__}: {feil}. Ingen vurdering er skrevet for "
            f"{dato.isoformat()}. {_kan_skrives_til(dato)}"
        )
        return False

    skrevet = 0
    grunner: dict[str, Grunn] = {}
    sto_fra_foer: list[str] = []
    try:
        kurslager = SqliteKurslager(tilkobling)
        lager = SqliteVurderingslager(tilkobling, klokke)
        for aksje in AKSJEUNIVERS:
            symbol = aksje.symbol
            if dag != dato and lager.les(symbol, dato) is not None:
                sto_fra_foer.append(symbol)
                continue
            if symbol in skrevne:
                innhold = vurder(kurslager.serie(symbol), dato)
            else:
                innhold = Grunn.SYMBOL_FEILET
            try:
                ny = lager.skriv(symbol, dato, innhold)
            except ValueError as feil:
                _stoppet_ved_midnatt(dato, skrevet, skriv, f"Lageret sa: {feil}")
                return False
            if not ny:
                sto_fra_foer.append(symbol)
                continue
            skrevet += 1
            if isinstance(innhold, Grunn):
                grunner[symbol] = innhold
    except BASEFEIL as feil:
        skriv(
            f"Basen {base_sti} feilet etter {skrevet} vurderinger: "
            f"{type(feil).__name__}: {feil}. {_kan_skrives_til(dato)}"
        )
        return False
    finally:
        tilkobling.close()

    stengt = "" if dag == dato else f" (boersen er stengt {dag.isoformat()})"
    skriv(
        f"Skrev {skrevet} rader i vurdering for boersdagen {dato.isoformat()}"
        f"{stengt}: {skrevet - len(grunner)} vurderinger og "
        f"{len(grunner)} med grunn."
    )
    if grunner:
        skriv(
            "  Med grunn: "
            + ", ".join(f"{symbol} ({grunn.value})" for symbol, grunn in grunner.items())
        )
    if sto_fra_foer:
        skriv(
            f"  Raden for {dato.isoformat()} sto fra foer og er ikke skrevet over: "
            + ", ".join(sto_fra_foer)
        )
    return True


def manglende_i_basen(base_sti: Path, dato: date) -> list[str]:
    """Aksjene i universet som ikke har en kurs for dato i basen - story 2.3.

    Finnes ikke basen, mangler alle. Basen aapnes uten migrering, saa
    ingenting skrives. En base som ikke kan aapnes eller leses, gir en feil
    fra BASEFEIL; kjoer henter da likevel.
    """
    if not base_sti.exists():
        return [aksje.symbol for aksje in AKSJEUNIVERS]
    tilkobling = aapne_base(base_sti, kjoer_migrasjoner=False)
    try:
        lager = SqliteKurslager(tilkobling)
        return [
            aksje.symbol
            for aksje in AKSJEUNIVERS
            if not any(rad.dato == dato for rad in lager.serie(aksje.symbol))
        ]
    finally:
        tilkobling.close()


def kjoer(
    data_katalog: Path,
    base_sti: Path,
    oeyeblikk: datetime,
    api_nokkel: str | Callable[[], str],
    hent: Callable[[str, str, str, str], list[dict]] = hent_ett_symbol,
    skriv: Callable[[str], None] = print,
    klokke: Callable[[], datetime] | None = None,
    *,
    hent_foer_kl_22: bool = False,
    les_kvote: Callable[[str], object] = hent_kvote,
) -> Path | None:
    """En henting. Returnerer fila som ble skrevet, eller None hvis dagens fil
    fantes fra foer.

    Story 2.1b: fila skrives foerst (AD-6), saa kursene til basen i base_sti
    gjennom skriv_til_basen, med oeyeblikket som hentet. base_sti har ingen
    standardverdi, saa ingen test kan skrive til data/db/ ved et uhell; main
    gir BASE_STI. Feiler basen, eller blir et symbol hoppet over eller
    avvist, staar fila, og kjoeringen avslutter med kode 1.

    Et oeyeblikksbilde skrives aldri om (AD-6, story 2.0). Finnes fila for
    boersdagen, stopper kjoeringen foer foerste kall. Det er ingen feil. Fila
    skrives med modus "x", saa en fil som dukker opp mens kjoeringen paagaar,
    heller ikke skrives over. Da er kallene brukt og ingenting lagret, og
    kjoeringen avslutter med kode 1.

    Story 2.3: rekkefoelgen foer foerste kall er klokka (oeyeblikk),
    tidskontrollen, basen, filvakten, noekkelen og kvoten. Paa en boersdag
    foer kl. 22:00 i Oslo hentes ingenting uten hent_foer_kl_22. Har hver
    aksje en kurs for boersdagen i basen, hentes ingenting (FR-402); mangler
    noen, hentes det, ogsaa paa en dag som ikke er boersdag (AD-7). Kan basen
    ikke leses, hentes det. Fila heter etter boersdagen vurderingene skrives
    for (K8), og filvakten sjekker samme dato. api_nokkel kan vaere en
    funksjon, som main gir, saa noekkelen leses foerst etter filvakten.
    Kvoten leses med les_kvote: er det faerre enn 15 igjen av dagens kall,
    men bonusen dekker resten, hentes det; ellers 0 kall og kode 1. Kan
    svaret ikke leses, hentes det. Tidskontrollen, basen og filvakten gir
    kode 0.

    Alt om tid utledes av oeyeblikk, som maa ha sone (AD-20, story 2.1):
    dagen er norsk kalenderdato (boersdag.norsk_dato) og gir filnavnet og
    til-datoen i intervallet, og hentet er oeyeblikket i UTC med offset.
    hentet er altsaa starten paa kjoeringen, ikke tidspunktet da siste kall
    var ferdig, saa filnavn og hentet kan aldri havne paa hver sin dag, heller
    ikke naar kjoeringen gaar over midnatt. Et oeyeblikk uten sone gir
    ValueError foer vakten og foer noe kall.

    Story 2.5: boersdagen vurderingene gjelder, regnes her, en gang, fra
    oeyeblikket, foer vakten og foer noe kall. Dekker ikke lista over stengte
    dager aaret, stopper kjoeringen med 0 kall (NFR-08). Etter kursene
    skrives vurderingene med skriv_vurderinger. klokke er den ekte klokka
    (main gir naa); uten den leses oeyeblikket. Den leses en gang foer
    vurderingene: er det blitt en ny dag i Oslo, stopper kjoeringen og sier
    fra. Feiler basen, skrives ingen vurdering.
    """
    dag = norsk_dato(oeyeblikk)
    try:
        dato = innevaerende_boersdag(dag)
    except UtenforKalenderen as feil:
        skriv(
            f"{feil}. Foer inn dagene Oslo Boers er stengt for aaret som mangler, "
            "i boersdag.py, foer hentingen kjoeres. Hentingen gjetter ikke paa "
            "boersdagen (NFR-08). 0 kall brukt."
        )
        sys.exit(1)
    if klokke is None:
        def klokke():
            return oeyeblikk
    hentet_tid = oeyeblikk.astimezone(timezone.utc)
    hentet = hentet_tid.isoformat()

    # Tidskontrollen (story 2.3): bare paa en boersdag, bare foer kl. 22:00.
    if er_boersdag(dag) and oeyeblikk.astimezone(OSLO).time() < KL_22:
        if not hent_foer_kl_22:
            skriv(
                f"{dag.isoformat()} er boersdag, og klokka er ikke 22:00 i Oslo "
                "ennaa. En henting naa bruker dagens kall uten aa faa dagens "
                "rad. Kjoer etter kl. 22:00, eller med --hent-foer-kl-22 for aa "
                "hente likevel. 0 kall brukt."
            )
            return None
        skriv("Henter foer kl. 22:00 (--hent-foer-kl-22).")

    # Basen (FR-402): har den boersdagen for alle aksjene, er det ingenting aa hente.
    try:
        mangler = manglende_i_basen(base_sti, dato)
    except BASEFEIL as feil:
        skriv(
            f"Basen {base_sti.name} kunne ikke leses ({type(feil).__name__}). "
            "Henter likevel; fila skrives foerst og kan leses inn senere."
        )
    else:
        if not mangler:
            skriv(
                f"Basen har alt kursene for boersdagen {dato.isoformat()} for "
                f"alle {len(AKSJEUNIVERS)} aksjene. Ingenting aa hente (FR-402). "
                "0 kall brukt."
            )
            return None

    # Filvakten (AD-6, K8): fila heter etter boersdagen, ikke kjoeredagen.
    data_katalog.mkdir(parents=True, exist_ok=True)
    fil = data_katalog / filnavn(dato)
    if fil.exists():
        skriv(
            f"Oeyeblikksbildet for boersdagen {dato.isoformat()}, {fil.name}, "
            "finnes allerede og skrives aldri om (AD-6). Hentingen er stoppet "
            "foer noe kall er brukt. Et nytt forsoek for en dag som har fil, "
            "kommer med story 2.3b. 0 kall brukt."
        )
        return None

    # Noekkelen foerst naa, saa en kjoering som stoppet over, aldri leser den.
    if callable(api_nokkel):
        api_nokkel = api_nokkel()

    # Kvoten (regel 15): /api/user er gratis. Dagens dato regnes i GMT.
    behov = len(AKSJEUNIVERS)
    try:
        igjen, bonus = tolk_kvote(les_kvote(api_nokkel), hentet_tid.date())
    except UlesbarKvote as feil:
        skriv(f"Kvoten kunne ikke leses fra /api/user: {feil}. Henter likevel.")
    except Exception as feil:  # noqa: BLE001 - kvoten skal ikke stoppe hentingen
        skriv(
            f"Kvoten kunne ikke leses fra /api/user ({type(feil).__name__}). "
            "Henter likevel."
        )
    else:
        if igjen >= behov:
            skriv(f"Kvoten: {igjen} kall igjen av dagens.")
        elif igjen + bonus >= behov:
            skriv(
                f"Kvoten: {igjen} kall igjen av dagens. {behov - igjen} kall tas "
                f"fra bonuskvoten, som har {bonus}."
            )
        else:
            skriv(
                f"Kvoten: {igjen} kall igjen av dagens og {bonus} i bonuskvoten. "
                f"Hentingen trenger {behov}. 0 kall brukt."
            )
            sys.exit(1)

    fra, til = bygg_intervall(dag)
    skriv(f"Henter {len(AKSJEUNIVERS)} symboler, {fra} til {til}.")
    skriv(f"Dette koster {len(AKSJEUNIVERS)} av dagskvoten paa 20.\n")

    resultat = hent_universet(api_nokkel, fra, til, hent, skriv)

    tekst = json.dumps(lag_oyeblikksbilde(resultat, fra, til, hentet), ensure_ascii=False)
    try:
        with open(fil, "x", encoding="utf-8") as ut:
            ut.write(tekst)
    except FileExistsError:
        skriv(
            f"{fil.name} dukket opp mens hentingen paagikk, og er ikke skrevet "
            f"over (AD-6). {resultat.kall_brukt} kall er brukt, og ingenting er lagret."
        )
        sys.exit(1)

    skriv(f"\nLagret {fil.name} i {data_katalog.name}/")
    skriv(f"API-kall brukt: {resultat.kall_brukt}")
    if resultat.feil:
        skriv(f"Symboler uten data: {', '.join(sorted(resultat.feil))}")

    # Basen etter fila. Et symbol i feil er ikke med og roeres ikke (AD-15).
    serier = {symbol: serie_fra_eodhd(rader) for symbol, rader in resultat.serier.items()}
    skrevne = skriv_til_basen(base_sti, serier, hentet_tid, fil, skriv)
    if skrevne is None:
        skriv(
            f"Ingen vurdering er skrevet for {dato.isoformat()}, og --les-inn "
            f"skriver ingen. {_kan_skrives_til(dato)}"
        )
        sys.exit(1)

    # Vurderingene etter kursene (AD-17), med datoen fra oeyeblikket.
    if norsk_dato(klokke()) != dag:
        _stoppet_ved_midnatt(dato, 0, skriv)
        sys.exit(1)
    if not skriv_vurderinger(base_sti, dato, dag, skrevne, klokke, skriv):
        sys.exit(1)
    if skrevne != set(serier):
        sys.exit(1)
    return fil


def les_inn(fil: Path, base_sti: Path, skriv: Callable[[str], None] = print) -> None:
    """Et oeyeblikksbilde som finnes, inn i basen uten kall - story 2.1b.

    Leser fila med SnapshotKilde og SnapshotLeser, og hentet kommer fra fila.
    Gaar samme vei som hentingen (skriv_til_basen), skriver bare kurs og
    kursserie, leser ingen noekkel og gjoer ingen kall. Skriver ingen kurser
    ut, bare antall serier, symbolene og datoene (regel 16).

    Avslutter med kode 1 hvis fila ikke kan leses, hvis hentet i fila ikke
    kan leses (da aapnes ikke basen), eller hvis ikke alt ble skrevet til
    basen. En serie som ikke kan leses, nevnes, de andre skrives, og
    kjoeringen ender med kode 1.
    """
    fil = Path(fil)
    try:
        kilde = SnapshotKilde.fra_fil(fil)
    except (OSError, ValueError, AttributeError) as feil:
        skriv(f"{fil} kan ikke leses: {type(feil).__name__}. Ingenting er lest inn.")
        sys.exit(1)

    # Samme regel som SnapshotLeser: uten en hentet som kan leses, er hele
    # oeyeblikksbildet manglende, og da sies aarsaken foer noe annet.
    hentet = _hentet_fra_tekst(kilde.hentet)
    if hentet is None:
        skriv(f"hentet i fila {fil.name} kan ikke leses. Ingenting er lest inn.")
        sys.exit(1)

    leser = SnapshotLeser(kilde)
    symboler = list(kilde.serier) if isinstance(kilde.serier, dict) else []
    serier: dict[str, list[Kursrad]] = {}
    alt_lest = True
    for symbol in symboler:
        rader = leser.serie(symbol)
        if rader:
            serier[symbol] = rader
        else:
            skriv(f"  {symbol}: serien i fila kan ikke leses, hoppet over")
            alt_lest = False
    if not serier:
        skriv(f"{fil.name} har ingen serie som kan leses inn. Ingenting er lest inn.")
        sys.exit(1)

    skriv(f"Leser inn {len(serier)} serier fra {fil.name}, hentet {hentet.isoformat()}.")
    for symbol, rader in serier.items():
        skriv(
            f"  {symbol}: {len(rader)} dager, "
            f"{rader[0].dato.isoformat()} til {rader[-1].dato.isoformat()}"
        )
    skrevne = skriv_til_basen(base_sti, serier, hentet, fil, skriv)
    if skrevne is None or skrevne != set(serier) or not alt_lest:
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    """Uten flagg: en henting. Med --les-inn <fil>: innlesing uten kall.
    Med --hent-foer-kl-22: en henting paa en boersdag foer kl. 22:00 (story
    2.3). Noekkelen gaar til kjoer som funksjon og leses etter filvakten.

    Stiene slaas opp her, naar main kalles (story 2.1b), saa fixturen i
    tests/conftest.py flytter dem.
    """
    parser = argparse.ArgumentParser(
        description="Henter sluttkurser fra EODHD.", allow_abbrev=False
    )
    parser.add_argument(
        "--les-inn",
        metavar="FIL",
        type=Path,
        help="les et oeyeblikksbilde som finnes, inn i basen, uten API-kall",
    )
    parser.add_argument(
        "--hent-foer-kl-22",
        action="store_true",
        help="hent paa en boersdag foer kl. 22:00 i Oslo (story 2.3)",
    )
    argumenter = parser.parse_args(argv)
    if argumenter.les_inn is not None:
        les_inn(argumenter.les_inn, lagring_sqlite.BASE_STI)
        return
    kjoer(
        lagring_fil.RAA_KATALOG,
        lagring_sqlite.BASE_STI,
        naa(),
        hent_api_nokkel,
        klokke=naa,
        hent_foer_kl_22=argumenter.hent_foer_kl_22,
    )


if __name__ == "__main__":
    main()
