"""Markedsoversikten for OSE Signal.

Leser kursene fra basen i data/db/ose.db (story 2.2). Denne filen gjoer
aldri API-kall, saa en nettleseroppdatering kan ikke bruke av kvoten. Nye
kurser hentes med hentekommandoen, den andre inngangen mot samme kodebase:
HENTEKOMMANDO under (FR-401, AD-10).

Alt av regning ligger i markedsoversikt.py og aksjedetalj.py, og de leser
Kursrad gjennom Kursleser (AD-3, AD-19). Denne fila gir dem SqliteKurslager
paa forespoerselens tilkobling og sender resultatet til malen.
Tidsstemplene er sist_hentet per symbol fra Kursleser, i UTC, og blir norsk
tid foerst i malen (filteret norsk_tid, AD-20). Sidens tidsstempel er det
eldste blant radene som vises (story 1.4c).

Basen (story 2.2): foerste forespoersel i en prosess mot en gitt BASE_STI
kjoerer migrer() en gang, gjennom aapne_base, under en laas. Det virker likt
med python src/app.py, flask run og en WSGI-server, og ingen import av
modulen roerer basen. Hver forespoersel aapner sin egen tilkobling uten
migrering og lukker den naar forespoerselen er ferdig, fordi en
sqlite3-tilkobling ikke kan deles mellom traadene Flask kjoerer forespoerslene
i. Kan basen ikke aapnes eller leses, svarer siden 503 med feiltypen, uten
stier. Bare de to rutene roerer basen.
"""

import hashlib
import os
import re
import sqlite3
import sys
import threading
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from flask import Flask, abort, g, redirect, render_template, request

import lagring_sqlite
from aksjedetalj import bygg_dagen, bygg_detalj, normaliser_symbol
from boersdag import UtenforKalenderen, innevaerende_boersdag, norsk_dato
from boersometer import (
    bygg_boersometer,
    bygg_rute,
    dagen_foer,
    indeks_for_dagen,
    kart,
    trinnforklaringer,
    vis_dagen_foer,
)
from dagene import setning_om_dagene, tell_dagene
from demo import DEMOKOMMANDO, DEMOKOMMANDO_DOCKER, STARTDAG, gammel_demobase
from graf import bygg_graf
from historikk import PARAMETER, Maaned, adresse, bygg_maaned, les_maaned, maanedsnavn, perioden
from hjelpetekster import ANTALL_SJEKKER, Hjelp, hjelpetekster
from hovedindeks import Hovedindeksvisning, bygg_hovedindeks, valgt_indeks
from ki_visning import AV, KAPSEL, PAA, UKJENT, KIVisning, bygg_ki_visning, ki_paa
from kilogg import Emne, UgyldigKIRad
from kursdata import Kursleser, investorside
from lagring_sqlite import (
    DEMOMERKE,
    SqliteIndekslager,
    SqliteKILogg,
    SqliteKurslager,
    SqliteMinlistelager,
    SqliteOversiktsleser,
    SqliteVurderingslager,
    aapne_base,
    andre_aksjer_har_ki_rad,
    demo_sti,
    har_kurser,
    les_merket,
)
from markedsoversikt import (
    Sortering,
    antall_vurdert,
    bygg_oversikt,
    bygg_rad_for_dag,
    del_i_to,
    eldre_enn_nyeste,
    ingen_skilte_seg_ut,
    med_perioden,
    neste_orden,
    norsk_tid,
    oppdatert,
    rader_uten_data,
    sidens_dato,
    sidens_tidsstempel,
    sorter,
    sorter_fr102,
)
from migrering import MigrasjonsFeil
from minliste import UkjentAksje
from oversiktsdata import Oversiktsleser
from perioder import (
    AKSEMERKER,
    MAANEDSNAVN,
    OVERSKRIFT,
    PERIODENE,
    SISTE,
    VELG,
    Valg,
    foerste_kursdag,
    knappene,
    les_valg,
    startdag,
)
from perioder import OVERSIKTEN as OVERSIKTEN_VALG
from signalberegning import BLANDET, STANDARD
from tallformat import avrundet, dato, med_og, tall, ukedag
from vurderingsdata import Grunn

# Kommandoen den tomme siden ber brukeren kjoere. Den staar ogsaa i README, og
# en test krever at de to er like (story 3.3). Kommer kommandoen for Docker i
# 3.1, endres bare denne og README. Rettet 2026-10-09 (3.3): kommandoen for
# Docker kom i 3.3, som HENTEKOMMANDO_DOCKER under.
HENTEKOMMANDO = "uv run python src/fetch_prices.py"

# Story 3.3, gruppens svar 09.10 kl. 23:13: en konstant for hver maate aa
# kjoere paa. Dockerfile setter OSE_I_DOCKER=1, og da viser den tomme siden
# kommandoen for Docker. README har begge, og en test holder dem like.
HENTEKOMMANDO_DOCKER = "docker compose run --rm hent"
I_DOCKER = "OSE_I_DOCKER"


# Story 3.4 (FR-411): bryteren som velger demobasen. Med OSE_DEMO=1, eller
# --demo til python src/app.py, aapner webserveren demo.db ved siden av
# ose.db, og den lager den aldri selv. «Eksempeltall» paa sidene avgjoeres
# av merket i basen, ikke av bryteren.
I_DEMO = "OSE_DEMO"


def demo_paa() -> bool:
    """Om bryteren er paa, lest fra miljoeet (AD-12)."""
    return os.environ.get(I_DEMO) == "1"


def les_flagg(argv: list[str]) -> None:
    """--demo setter bryteren, saa kommandoen er lik i PowerShell og bash."""
    if "--demo" in argv:
        os.environ[I_DEMO] = "1"


def _base_sti() -> Path:
    """Basen bryteren velger: demo.db eller den ekte ose.db."""
    return Path(demo_sti() if demo_paa() else lagring_sqlite.BASE_STI).resolve()


def hentekommando() -> str:
    """Kommandoen for maaten appen kjoerer paa, lest fra miljoeet (AD-10, AD-12)."""
    return HENTEKOMMANDO_DOCKER if os.environ.get(I_DOCKER) == "1" else HENTEKOMMANDO


def demokommando() -> str:
    """Kommandoen som lager demobasen, valgt som hentekommandoen (story 3.4, ECH7)."""
    return DEMOKOMMANDO_DOCKER if os.environ.get(I_DOCKER) == "1" else DEMOKOMMANDO


# Feil som betyr at basen ikke kan aapnes eller migreres, som BASEFEIL i
# hentingen. Siden svarer da 503 med grunnen i stedet for en traceback.
BASEFEIL = (sqlite3.Error, OSError, MigrasjonsFeil, RuntimeError)

app = Flask(__name__)
# Story 2.7a: all stilen paa sidene, lenket fra _ramme.html.
STILARK = Path(app.static_folder) / "stil.css"
# Story 8.0f: skriptet som gjoer hjelpen ved «?» til ett fast felt.
HJELPESKRIPT = Path(app.static_folder) / "hjelp.js"
# Story 8.0c: datoene og tidspunktene med aar bare naar aaret er et annet
# enn i dag. I dag kommer fra idag(), saa testene styrer det.
app.jinja_env.filters["norsk_tid"] = lambda tid: norsk_tid(tid, idag().year)
app.jinja_env.filters["dato"] = lambda dag: dato(dag, idag().year)
# Regel 21: tallene formateres ett sted, ikke med "%.2f" i malene (story 8.0).
app.jinja_env.filters["tall"] = tall
# Story 2.9: tallet slik det vises, til fargen ved endringen for indeksen.
app.jinja_env.filters["avrundet"] = avrundet
# Story 8.0e: ukedagen i overskriften og navnene i linja om «3 av 3».
app.jinja_env.filters["ukedag"] = ukedag
app.jinja_env.filters["med_og"] = med_og
# Story 2.7b: «oktober 2026» ved pilene i historikken.
app.jinja_env.filters["maanedsnavn"] = maanedsnavn
# Story 8.15: retningen et klikk på en kolonne gir.
app.jinja_env.globals["neste_orden"] = neste_orden
# Story 8.0d: «Oppdatert tirsdag 13.10 kl. 22.15» i stripa, i norsk tid.
app.jinja_env.filters["oppdatert"] = lambda tid: oppdatert(tid, idag().year)


def naa() -> datetime:
    """Klokka sidene regner dagens dato av, i UTC (AD-20). Egen funksjon, saa
    testene kan stille den."""
    return datetime.now(timezone.utc)


def idag() -> date:
    """Dagens dato i Oslo, som tilstand() maaler datoen til nyeste kurs mot."""
    return norsk_dato(naa())


_migrerte: set[Path] = set()
_migrerings_laas = threading.Lock()


def _migrer_en_gang(sti: Path) -> None:
    """migrer() en gang per prosess og per base, gjennom aapne_base.

    Lager basen hvis den mangler, som hentingen gjoer. Feiler det, blir ikke
    stien merket, saa neste forespoersel proever igjen.
    """
    with _migrerings_laas:
        if sti in _migrerte:
            return
        aapne_base(sti).close()
        _migrerte.add(sti)


# Rutene som leser basen. Andre forespoersler (404, statiske filer) roerer den
# ikke. Story 8.3: Min liste og merkingen, som er den eneste ruta som skriver.
_RUTER_MED_BASE = {"markedsoversikt", "aksjedetalj", "min_liste", "merk", "boersometer"}

# Story 8.3: ruta som skriver merkingen. Bare den aapner en demobase for
# skriving, og bare tabellen min_liste skrives (AD-3, AD-10).
_SKRIVER = "merk"


def _basefeil(feil: BaseException) -> str:
    """Feiltypen, uten teksten, som kan inneholde stier paa maskinen."""
    return type(feil).__name__


@app.before_request
def _aapne_basen() -> None:
    """Migrer en gang, og aapne forespoerselens egen tilkobling.

    Mangler basefila etter at stien er migrert, for eksempel fordi den er
    slettet, glemmes stien, og migreringen proeves en gang til, som lager en
    tom base.
    """
    g.tilkobling = None
    g.basefeil = None
    g.demo_mangler = False
    g.demo_gammel = False
    g.eksempeltall = False
    if request.endpoint not in _RUTER_MED_BASE:
        return
    sti = _base_sti()
    if demo_paa():
        # Story 3.4: demobasen migreres og lages aldri av webserveren.
        # Mangler den, viser siden kommandoen som lager den.
        if not sti.is_file():
            g.demo_mangler = True
            return
        try:
            # Story 8.3: stjernen virker ogsaa i demoen. Bare merkingen
            # aapner demobasen for skriving, og den migreres fortsatt ikke.
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False, skrivebeskyttet=request.endpoint != _SKRIVER)
            g.eksempeltall = les_merket(g.tilkobling) == DEMOMERKE
            # Story 3.4c: en demobase fra foer, med historikken fra 02.01,
            # vises ikke. Siden ber om at den lages paa nytt.
            if g.eksempeltall and gammel_demobase(g.tilkobling):
                g.tilkobling.close()
                g.tilkobling = None
                g.demo_mangler = g.demo_gammel = True
        except BASEFEIL as feil:
            g.basefeil = _basefeil(feil)
        return
    if lagring_sqlite.er_demobase(sti):
        # Gjennomgangen av PR 1 (BH6): en demobase der den ekte skal ligge,
        # migreres ikke. Den vises skrivebeskyttet, med «Eksempeltall».
        try:
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False, skrivebeskyttet=request.endpoint != _SKRIVER)
            g.eksempeltall = True
            # Story 3.4c (gjennomgangen, BH1): en demobase fra foer vises ikke
            # her heller.
            if gammel_demobase(g.tilkobling):
                g.tilkobling.close()
                g.tilkobling = None
                g.demo_mangler = g.demo_gammel = True
        except BASEFEIL as feil:
            g.basefeil = _basefeil(feil)
        return
    try:
        _migrer_en_gang(sti)
        try:
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False)
        except sqlite3.OperationalError:
            if sti.exists():
                raise
            with _migrerings_laas:
                _migrerte.discard(sti)
            _migrer_en_gang(sti)
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False)
        # Merket avgjoer «Eksempeltall», ogsaa uten bryteren (FR-411).
        g.eksempeltall = les_merket(g.tilkobling) == DEMOMERKE
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)


# Story 8.0c: merket staar ett sted, ikke kopiert i tre maler, og demoen
# sier «Demoversjon.» foran det (tillegget 11.10).
EKSEMPELTALL_MERKE = "Eksempeltall: oppdiktede selskaper og kurser, ikke data fra Oslo Børs."
# Story 3.3i (U51): demolinja lenker til stegene for den ekte versjonen i
# README-en paa GitHub. Den staar bare i demoen, i samme blokk som merket.
EKTE_VERSJONEN_URL = "https://github.com/IBE160-2026/G74-lund-osen#den-ekte-versjonen"

# Story 8.0c (tillegget 11.10, svar 4): linja nederst paa alle sidene. Én
# innstilling avgjoer den, og docs/innlevering.md §5 sier at den avgjoeres
# ved innleveringen.
UNDER_ARBEID = True
UNDER_ARBEID_TEKST = "Appen er under utvikling og ikke ferdig."


@app.context_processor
def _stilark():
    """Story 2.7a: adressen til stilarket, med de foerste 16 tegnene av sha256
    av fila. Regnes ved hver side, saa en endret fil gir ny adresse uten
    omstart, og nettleseren aldri bruker en gammel utgave. Kan fila ikke
    leses, staar lenken uten avtrykk, saa siden og feilsiden likevel vises
    (gjennomgangen, BH3). Story 8.0f: det samme for hjelpeskriptet, i
    _med_avtrykk."""
    return {"stilark": _med_avtrykk(STILARK), "hjelpeskript": _med_avtrykk(HJELPESKRIPT)}


def _med_avtrykk(fil: Path) -> str:
    """Adressen til en fil i src/static/ med avtrykket. Story 8.0f: ogsaa
    for hjelpeskriptet."""
    try:
        avtrykk = hashlib.sha256(fil.read_bytes()).hexdigest()[:16]
    except OSError:
        return f"/static/{fil.name}"
    return f"/static/{fil.name}?v={avtrykk}"


def demo_startdag() -> str:
    """Første dag med vurdering i demoen, som «mandag 21.09», regnet fra
    STARTDAG i demo.py (gruppens svar 22.10 kl. 20:11). Ukedagen og datoen
    kommer fra tallformat.py (regel 21, gjennomgangen VG2). Året står bare
    når det er et annet enn i år, som i de andre datoene på sidene
    (gjennomgangen 23.10, BH1 og ECH1)."""
    return f"{ukedag(STARTDAG)} {dato(STARTDAG, idag().year)}"


def _fotnoten(datoer: list[date], i_dag: date) -> dict[str, bool]:
    """Fotnoten for «ikke vurdert» etter datoene som er «ikke vurdert» på
    siden (story 3.4e). Demoteksten står bare i demoen, og bare når alle
    datoene er før STARTDAG. En dag fra STARTDAG uten vurdering får den
    ekte teksten, også i demoen, som en kveld uten henting. Med datoer både
    før og etter står den ekte teksten, fordi den dekker begge.
    fotnote_kan_lagres: en av datoene er inneværende børsdag, siste børsdag
    fram til i_dag, og fotnoten sier i tillegg at signalet fortsatt kan
    lagres før neste børsdag. Samme regel som lagringen bruker, så fredagen
    teller også lørdag, søndag og en helligdag (gruppens svar 23.10 kl.
    19:10, ECH1). Lagringen godtar i tillegg forrige børsdag ved første
    henting i en tom base (2.3c), men da finnes ingen rad «ikke vurdert»
    på sidene (gjennomgangen 23.10 kveld, ECH4). Kan kalenderen ikke
    avgjøre dagen, kan lagringen heller ikke skrive, og setningen står
    ikke. Ikke i demoen, der ingen henting skriver (gjennomgangen, BH1 og
    ECH3). i_dag er den samme dagen siden ellers er bygd med (ECH2)."""
    demo = bool(g.get("eksempeltall", False))
    return {
        "fotnote_demo": demo and bool(datoer) and all(d < STARTDAG for d in datoer),
        "fotnote_kan_lagres": not demo and bool(datoer) and _innevaerende(i_dag) in datoer,
    }


def _innevaerende(i_dag: date) -> date | None:
    """Inneværende børsdag for i_dag, eller None når kalenderen ikke dekker
    dagen (story 3.4e, svaret kl. 19:10)."""
    try:
        return innevaerende_boersdag(i_dag)
    except UtenforKalenderen:
        return None


@app.context_processor
def _eksempeltall():
    """«Eksempeltall» paa hver side som viser en base med demomerket, og
    linja om at appen er under arbeid."""
    return {
        "eksempeltall": g.get("eksempeltall", False),
        "eksempeltall_merke": EKSEMPELTALL_MERKE,
        "demo_startdag": demo_startdag(),
        "ekte_versjonen_url": EKTE_VERSJONEN_URL,
        "under_arbeid": UNDER_ARBEID_TEKST if UNDER_ARBEID else None,
    }


# Story 8.0b: tekstene bak «?», med tallene fra parametrene som gjelder i
# appen. Malene henter dem med hjelp.tekst(), og MA-vinduet i grafens
# tegnforklaring med parametre.ma_vindu. Tekstene, tegnforklaringen og
# beregningen paa sidene bruker samme Parametre (gjennomgangen av 8.0b).


@app.context_processor
def _hjelp():
    """Hjelpetekstene og parametrene paa hver side, laget av samme objekt.
    antall_sjekker er «3» i «N av 3» (story 8.0c), fra samme sted som hjelpen."""
    return {
        "hjelp": Hjelp(hjelpetekster(STANDARD)),
        "parametre": STANDARD,
        "antall_sjekker": ANTALL_SJEKKER,
        "blandet": BLANDET,
    }


@app.teardown_appcontext
def _lukk_basen(_unntak) -> None:
    tilkobling = g.pop("tilkobling", None)
    if tilkobling is not None:
        tilkobling.close()


def _basen_kan_ikke_aapnes():
    return (
        render_template(
            "basefeil.html",
            feil=g.basefeil,
            base=_base_sti().name,
            demokommando=demokommando() if demo_paa() else None,
        ),
        503,
    )


def hent_leser() -> Kursleser | None:
    """Kursleseren sidene leser gjennom, eller None hvis basen ikke har en
    eneste serie (story 2.2).

    Egen funksjon, saa en test kan montere en hvilken som helst Kursleser,
    for eksempel et MinneKurslager med ulike tider per symbol.
    """
    tilkobling = g.get("tilkobling")
    if tilkobling is None:
        return None
    if not har_kurser(tilkobling):
        return None
    return SqliteKurslager(tilkobling)


def hent_oversiktsleser() -> Oversiktsleser | None:
    """Porten sidene leser selskapene og vurderingene gjennom (story 2.2b).

    None naar forespoerselen ikke har en tilkobling. app.py har ingen SQL:
    spoerringen med join ligger i SqliteOversiktsleser.
    """
    tilkobling = g.get("tilkobling")
    if tilkobling is None:
        return None
    return SqliteOversiktsleser(tilkobling)


class _BasenFeilet(Exception):
    """En feil i basen etter at tilkoblingen ble aapnet, for eksempel en base
    som en nyere henting har migrert forbi koden. Gir 503, ikke 500."""


def _leser_eller_basefeil(
    hent: Callable[[], Kursleser | Oversiktsleser | None] | None = None,
) -> Kursleser | Oversiktsleser | None:
    """Leseren fra hent (som standard hent_leser), eller 503 ved basefeil."""
    try:
        return (hent or hent_leser)()
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)
        raise _BasenFeilet from feil


@app.errorhandler(_BasenFeilet)
def _basen_feilet_underveis(_feil):
    return _basen_kan_ikke_aapnes()


@app.errorhandler(sqlite3.Error)
def _basen_feilet_under_lesingen(feil):
    """En sqlite3-feil mens sidene leser, etter at leseren er laget, for
    eksempel en laast base. Gir 503 med feiltypen, som de andre basefeilene,
    ikke 500 og ikke en traceback (raadet 03.10)."""
    g.basefeil = _basefeil(feil)
    return _basen_kan_ikke_aapnes()


def _hovedindeks(
    kurslager: Kursleser,
    poster: list,
    tre_av_tre: frozenset[str],
    valg: Valg | None = None,
    serier: dict[str, list] | None = None,
) -> tuple[Hovedindeksvisning | None, bool]:
    """Hovedindeksen over tabellen - story 2.9, FR-104.

    Har basen HOVEDINDEKS (OSEBX), er det den. Ellers er det den basen sist
    hentet (SqliteIndekslager.symboler), som DEMIX i demobasen
    (gjennomgangen, BH13). Aksjene er de i aksje i basen, i samme
    rekkefoelge, med seriene fra kurslageret. Gir (visningen, feilet).
    Visningen er None naar basen ikke har en indeks. Kan indeksen ikke
    leses, ogsaa naar en rad ikke kan tolkes (ValueError, gjennomgangen ECH1
    og ECH5), er feilet True, og tabellen vises likevel (NFR-03). Ingen
    nettkall (AD-10).

    Story 2.9b: soeylene faar de samme seriene, og tre_av_tre er symbolene
    med 3 av 3 paa siste boersdag, fra radene i tabellen.

    Story 8.17a: soeylene og linja foelger perioden og dagen i valg, og
    seriene som alt er lest for tabellen, brukes paa nytt.
    """
    try:
        lager = SqliteIndekslager(g.tilkobling)
        symboler = lager.symboler()
        if not symboler:
            return None, False
        symbol = valgt_indeks(symboler)
        lest = serier or {}
        par = [
            (post.aksje, lest[post.aksje.symbol] if post.aksje.symbol in lest else kurslager.serie(post.aksje.symbol))
            for post in poster
        ]
        aksjer = [(aksje.navn, serie) for aksje, serie in par]
        grunnlag = [(aksje, serie, aksje.symbol in tre_av_tre) for aksje, serie in par]
        periode = valg.periode if valg is not None else SISTE
        dag = valg.dag if valg is not None else None
        return bygg_hovedindeks(symbol, lager.serie(symbol), aksjer, grunnlag, periode, dag), False
    except (*BASEFEIL, ValueError):
        return None, True


def _indeksen_for_grafen() -> tuple[str | None, dict | None, bool]:
    """Indeksen for kursgrafen paa aksjesiden - story 2.9c.

    Gir (symbolet, {dato: justert_slutt}, feilet). Symbolet og serien er
    None naar basen ikke har en indeks. Kan indeksen ikke leses, er feilet
    True, og grafen vises uten linja (NFR-03). Bare det som er hentet, og
    ingen nettkall (AD-10).
    """
    try:
        lager = SqliteIndekslager(g.tilkobling)
        symboler = lager.symboler()
        if not symboler:
            return None, None, False
        symbol = valgt_indeks(symboler)
        return symbol, {rad.dato: float(rad.justert_slutt) for rad in lager.serie(symbol)}, False
    except (*BASEFEIL, ValueError):
        return None, None, True


def _indeksen_for_dagen(dag: date) -> float | None:
    """Endringen i hovedindeksen for dag, til linja «Mål mot børsen» -
    story 8.6b, b. None når basen ikke har en indeks, når indeksen ikke har
    endringen for dagen, og når den ikke kan leses: da står «–», og rutene
    vises som vanlig (NFR-03). Ingen nettkall (AD-10)."""
    try:
        lager = SqliteIndekslager(g.tilkobling)
        symboler = lager.symboler()
        if not symboler:
            return None
        return indeks_for_dagen(lager.serie(valgt_indeks(symboler)), dag)
    except (*BASEFEIL, ValueError):
        return None


@app.route("/")
def markedsoversikt():
    return _tabellsiden(OVERSIKT)


@app.route("/min-liste")
def min_liste():
    """Story 8.3, FR-101, FR-102: samme tabell som oversikten, i samme
    rekkefoelge, med bare de merkede, eller alle med ?vis=alle."""
    return _tabellsiden(MIN_LISTE_SIDE)


# Story 8.3: siden man staar paa, som knapperaden i stripa fyller.
OVERSIKT = "oversikt"
MIN_LISTE_SIDE = "min_liste"
# Story 8.6: børsometeret, mellom de to i stripa.
BOERSOMETER = "boersometer"
_DAG = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


@app.route("/boersometer")
def boersometer():
    """Story 8.6, FR-106: én rute per aksje i lista, ordnet etter bransje,
    for siste børsdag eller dagen fra «Velg dag» (?dag=ÅÅÅÅ-MM-DD). Kursene
    og vurderingene leses gjennom portene som finnes, uten ny tabell, og
    webserveren henter aldri (AD-10). En dag uten kurs gir den siste
    børsdagen med kurs før den. Story 8.6b, b: hovedindeksen står som et tall
    i linja «Mål mot børsen», for dagen som vises, og søylene står bare på
    oversikten."""
    felles = {"aktiv": BOERSOMETER}
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler"):
        return render_template(
            "boersometer.html",
            bransjer=[],
            dato=None,
            hentet=None,
            demokommando=demokommando(),
            demo_gammel=g.get("demo_gammel", False),
            **felles,
        )
    leser = _leser_eller_basefeil()
    if leser is None:
        return render_template(
            "boersometer.html",
            bransjer=[],
            dato=None,
            hentet=None,
            hentekommando=hentekommando(),
            demokommando=demokommando() if demo_paa() else None,
            **felles,
        )
    oversiktsleser = _leser_eller_basefeil(hent_oversiktsleser)
    poster = oversiktsleser.oversikt()
    serier = {post.aksje.symbol: leser.serie(post.aksje.symbol) for post in poster}
    datoer = sorted({rad.dato for serie in serier.values() for rad in serie})
    if not datoer:
        # Gjennomgangen (ECH6): som grenen uten kurser over, med demokommandoen
        # naar bryteren er paa.
        return render_template(
            "boersometer.html",
            bransjer=[],
            dato=None,
            hentet=None,
            hentekommando=hentekommando(),
            demokommando=demokommando() if demo_paa() else None,
            **felles,
        )
    siste = datoer[-1]
    oenske = request.args.get("dag", "")
    valgt, ugyldig = None, False
    if oenske:
        if _DAG.fullmatch(oenske):
            try:
                valgt = date.fromisoformat(oenske)
            except ValueError:
                ugyldig = True
        else:
            ugyldig = True
    dagen = siste
    # Gjennomgangen (BH3, VG3, ECH1): en dag foer foerste kurs gir foerste
    # boersdag med kurs, og siden sier at den kommer etter.
    foer_foerste = False
    if valgt is not None:
        foer = [d for d in datoer if d <= valgt]
        dagen = foer[-1] if foer else datoer[0]
        foer_foerste = not foer
    i_dag = idag()
    rader = bygg_oversikt(poster, i_dag, STANDARD)
    # Gjennomgangen (VG1): gult foelger 3 av 3 paa siste boersdag, ogsaa naar
    # siden viser en annen dag (designregler §3).
    # Gjennomgangen 23.10 (ECH1): bare en rad fra sidens siste boersdag,
    # saa en aksje der hentingen feilet den dagen, ikke faar gult fra
    # en eldre dag.
    siste_styrke = {rad.aksje.symbol: rad.styrke for rad in rader if rad.dato == siste}
    ruter = [
        bygg_rute(
            post.aksje,
            [rad for rad in serier[post.aksje.symbol] if rad.dato <= dagen],
            oversiktsleser.vurdering(post.aksje.symbol, dagen),
            dagen,
            i_dag,
            # Gjennomgangen 24.10 (ECH2, BH10): samme Parametre som oversikten.
            p=STANDARD,
            siste_styrke=siste_styrke.get(post.aksje.symbol),
            er_siste=dagen == siste,
        )
        for post in poster
    ]
    bransjer = bygg_boersometer(ruter)
    ikke_vurdert = any(rute.ikke_vurdert for rute in ruter)
    # Story 8.6b, d: kartet regnes av de samme bransjene som tabellen.
    # Gjennomgangen 26.10 (BH, ECH): får rutene ikke plass, står tabellen
    # alene, som indeksen i linja (NFR-03).
    try:
        kartet = kart(bransjer)
    except ValueError:
        kartet = kart([])
    return render_template(
        "boersometer.html",
        bransjer=bransjer,
        kart=kartet,
        antall_aksjer=len(ruter),
        ikke_vurdert=ikke_vurdert,
        **_fotnoten([dagen] if ikke_vurdert else [], i_dag),
        dagen=dagen,
        siste=siste,
        foerste=datoer[0],
        # Gjennomgangen 26.10 (ECH4): datoen når børsdagen før er mer enn 6 dager før.
        dagen_foer=vis_dagen_foer(dagen_foer(datoer, dagen), dagen, i_dag.year),
        volum_vindu=STANDARD.volum_vindu,
        indeksendring=_indeksen_for_dagen(dagen),
        fargetrinn=trinnforklaringer(),
        valgt=valgt,
        foer_foerste=foer_foerste,
        ugyldig=ugyldig,
        dato=dagen,
        hentet=sidens_tidsstempel(rader),
        **felles,
    )


def _dager_i_serien(leser: Kursleser, poster: list) -> dict[str, int]:
    """Story 8.2a, d (gruppens svar 24.10 kl. 11:29): dagene i kursserien,
    til og med dagen raden gjelder, for aksjene der signalet ikke kunne
    regnes, så raden sier hvorfor med samme tall som aksjesiden. Bare for
    dem, så siden ikke leser alle seriene.

    Gjennomgangen 24.10 (BH2): kan serien ikke leses, står aksjen uten tall,
    og raden sier grunnen uten dem, så tabellen vises likevel (NFR-03), som
    for hovedindeksen. (ECH1): bare radene til og med nyeste dato telles.
    """
    dager = {}
    for post in poster:
        if post.innhold is not Grunn.SIGNAL_IKKE_REGNET or post.nyeste is None:
            continue
        try:
            serie = leser.serie(post.aksje.symbol)
        except (*BASEFEIL, ValueError):
            continue
        dager[post.aksje.symbol] = sum(1 for rad in serie if rad.dato <= post.nyeste.dato)
    return dager


def _tabellsiden(aktiv: str):
    """Oversikten eller Min liste. Min liste filtrerer radene etter at de er
    delt eller sortert, og sorterer dem aldri paa nytt, saa rekkefoelgen er
    den samme som i oversikten, ogsaa sortert (FR-102, story 8.15)."""
    i_lista = aktiv == MIN_LISTE_SIDE
    alle = i_lista and request.args.get("vis") == ALLE
    sti = MIN_LISTE if i_lista else OVERSIKTEN
    felles = {"aktiv": aktiv, "sidesti": sti, "alle": alle}
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler"):
        return render_template(
            "index.html",
            rader=[],
            dato=None,
            hentet=None,
            mangler=[],
            eget=set(),
            demokommando=demokommando(),
            demo_gammel=g.get("demo_gammel", False),
            **felles,
        )
    leser = _leser_eller_basefeil()
    if leser is None:
        # Med bryteren er det demokommandoen som fyller basen, ikke hentingen
        # (gjennomgangen av PR 1, ECH6).
        return render_template(
            "index.html",
            rader=[],
            dato=None,
            hentet=None,
            mangler=[],
            eget=set(),
            hentekommando=hentekommando(),
            demokommando=demokommando() if demo_paa() else None,
            **felles,
        )

    oversiktsleser = _leser_eller_basefeil(hent_oversiktsleser)
    poster = oversiktsleser.oversikt()
    i_dag = idag()
    rader = bygg_oversikt(poster, i_dag, STANDARD, _dager_i_serien(leser, poster))
    # Story 8.15: linja om 3 av 3 og «N av M» bruker rader, som står i
    # FR-102 (svar 7). Story 8.2a, e (gruppens svar 24.10 kl. 11:39): uten
    # en valgt kolonne er tabellen delt i to, hver i FR-102-rekkefølgen, som
    # før. Med en kolonne valgt er den én liste, sortert under (sortert), og
    # ikke sortert innenfor hver del, som tillegget 13.10 sa.
    sortering = Sortering.fra_adressen(request.args.get("sorter"), request.args.get("orden"))
    tre_av_tre = frozenset(rad.aksje.symbol for rad in rader if rad.styrke == ANTALL_SJEKKER)
    # Story 8.17a: periodevalget i oversikten, ikke i Min liste (8.17b).
    # Overskriften, linja om 3 av 3 og tidspunktet gjelder siste børsdag,
    # og vist er radene tabellen viser: en periode gir endringen for
    # perioden, og «Velg dag» radene for dagen, lest og aldri regnet (AD-7).
    serier = {} if i_lista else _seriene(leser, poster)
    valg = None if i_lista else _valget(rader, serier, i_dag)
    vist = rader
    # Gruppens svar 30.10 kl. 10:45 (ECH1): én dag for linja, radene og
    # søylene, den første kursen i perioden.
    periodestart = _periodestart(valg, rader, serier)
    if valg is not None and valg.periode == VELG:
        vist = sorter_fr102(
            [
                bygg_rad_for_dag(
                    post,
                    serier.get(post.aksje.symbol, []),
                    valg.dag,
                    oversiktsleser.vurdering(post.aksje.symbol, valg.dag),
                    i_dag,
                    post.aksje.symbol in tre_av_tre,
                )
                for post in poster
                if post.nyeste is not None
            ]
        )
    elif periodestart is not None:
        vist = med_perioden(rader, serier, periodestart)
    annen_dag = valg is not None and valg.periode == VELG
    skilte_seg_ut, oevrige = del_i_to(rader if annen_dag else vist)
    # Story 8.3: merkingen leses fra sin egen port, bare lesing her.
    merkede = _leser_eller_basefeil(lambda: SqliteMinlistelager(g.tilkobling)).merkede()
    # Story 8.2a, b (U23): en aksje uten kurser har en rad nederst, ikke
    # bare navnet i en fotnote.
    alle_uten_data = rader_uten_data(poster)
    mangler = alle_uten_data
    # Gjennomgangen (BH8, ECH2): antallet er de merkede som har en rad i
    # tabellen, saa knappen og tabellen sier det samme. Story 8.2a, b: ogsaa
    # en merket aksje uten kurser, som naa har en rad.
    antall_merket = sum(rad.aksje.symbol in merkede for rad in (*rader, *alle_uten_data))
    # Story 8.2a, e: hele lista sortert på kolonnen, med radene uten data,
    # som står sist når kolonnen ikke har en verdi for dem. None uten
    # sortering. De som skilte seg ut, beholder kanten i malen.
    sortert = sorter([*vist, *alle_uten_data], sortering) if sortering else None
    # Story 8.17a: en valgt dag er én liste uten delene, fordi «Skilte seg
    # ut» gjelder siste børsdag (gruppens svar 23.10 kl. 12:35, a).
    if annen_dag and sortert is None:
        sortert = [*vist, *alle_uten_data]
    if i_lista and not alle:
        skilte_seg_ut = [rad for rad in skilte_seg_ut if rad.aksje.symbol in merkede]
        oevrige = [rad for rad in oevrige if rad.aksje.symbol in merkede]
        mangler = [rad for rad in mangler if rad.aksje.symbol in merkede]
        if sortert is not None:
            sortert = [rad for rad in sortert if rad.aksje.symbol in merkede]
    hovedindeks, indeks_feilet = (None, False) if i_lista else _hovedindeks(leser, poster, tre_av_tre, valg, serier)
    # Story 3.4e: datoene som er «ikke vurdert» i det siden viser, én gang.
    ikke_vurdert = [rad.dato for rad in (vist if annen_dag else (*skilte_seg_ut, *oevrige)) if rad.ikke_vurdert]
    ledd = periodeledd(valg)

    return render_template(
        "index.html",
        rader=rader,
        hovedindeks=hovedindeks,
        indeks_feilet=indeks_feilet,
        dato=sidens_dato(rader),
        hentet=sidens_tidsstempel(rader),
        eget=eldre_enn_nyeste(rader),
        mangler=mangler,
        # Story 8.0d, PR 2b: M i «N av M aksjer» er alle aksjene i lista,
        # også de uten kurser (beslutningen 14.10). Story 8.2a, b (U23): det
        # er også antallet rader i tabellen, fordi hver aksje uten kurser nå
        # har en rad, så «7 av 15» stemmer med tabellen. Summen er lik
        # len(poster), og definisjonen fra 14.10 står (gjennomgangen, BH5).
        antall_aksjer=len(rader) + len(alle_uten_data),
        ikke_vurdert=bool(ikke_vurdert),
        **_fotnoten(ikke_vurdert, i_dag),
        # Gjennomgangen (BH7, ECH1): «Alle» i Min liste er samme tabell som
        # oversikten, ogsaa naar ingen skilte seg ut.
        ingen_skilte_seg_ut=ingen_skilte_seg_ut(rader) and not (i_lista and not alle),
        antall_vurdert=antall_vurdert(rader),
        skilte_seg_ut=skilte_seg_ut,
        oevrige=oevrige,
        sortert=sortert,
        sortering=sortering,
        tre_av_tre=[rad.aksje.navn for rad in rader if rad.styrke == ANTALL_SJEKKER],
        hentekommando=hentekommando(),
        merkede=merkede,
        antall_merket=antall_merket,
        tilbake=side_adresse(sti, sortering, alle, ledd),
        # Story 8.17a: periodevalget, og perioden og dagen i lenkene.
        valg=valg,
        knapper=knappene(sidens_siste(rader), i_dag) if valg else (),
        # Gjennomgangen (ECH9): navnet midt i en setning, «i år» med liten i.
        periodenavn=OVERSKRIFT.get(valg.periode) if valg and valg.periode not in (SISTE, VELG) else None,
        periodestart=periodestart,
        foerste_valgbare=_foerste_valgbare(serier),
        siste_dag=sidens_siste(rader),
        periodeledd=ledd,
        standard_adresse=side_adresse(sti, None, alle, ledd),
        **felles,
    )


def sidens_siste(rader: list) -> date | None:
    """Siste børsdag i oversikten: den nyeste datoen blant radene."""
    return max((rad.dato for rad in rader), default=None)


def _seriene(leser: Kursleser, poster: list) -> dict[str, list]:
    """Kursseriene for aksjene med kurser - story 8.17a, til perioden, «Velg
    dag» og søylene. Kan en serie ikke leses, står aksjen uten, og raden
    viser «–» for endringen (NFR-03), som _dager_i_serien."""
    serier = {}
    for post in poster:
        if post.nyeste is None:
            continue
        try:
            serier[post.aksje.symbol] = leser.serie(post.aksje.symbol)
        except (*BASEFEIL, ValueError):
            continue
    return serier


def _foerste_valgbare(serier: dict[str, list]) -> date | None:
    """Første dag «Velg dag» godtar: dagen etter den første dagen i
    seriene, fordi les_valg avviser seriens første dag (8.16, BH3), og
    godtar alle dager etter den (gjennomgangen, ECH6 og BH8)."""
    foerste = min((serie[0].dato for serie in serier.values() if serie), default=None)
    return foerste + timedelta(days=1) if foerste else None


def _valget(rader: list, serier: dict[str, list], i_dag: date) -> Valg | None:
    """Perioden og dagen fra adressen til oversikten - story 8.17a. Siste
    børsdag uten noe i adressen og ved en feil, med beskjeden. None uten
    rader, for da er det ingen tabell å velge for."""
    siste = sidens_siste(rader)
    if siste is None:
        return None
    foerste = min((serie[0].dato for serie in serier.values() if serie), default=siste)
    valg = les_valg(request.args.get("periode"), request.args.get("dag"), foerste, i_dag, siste, OVERSIKTEN_VALG)
    # Gjennomgangen (BH5, VG9): «Velg dag» på siste børsdag er siste børsdag,
    # med delene og 2 av 3, så samme dag aldri merkes på to måter.
    if valg.periode == VELG and valg.dag == siste:
        return Valg(SISTE)
    return valg


def _periodestart(valg: Valg | None, rader: list, serier: dict[str, list]) -> date | None:
    """Dagen den første kursen i perioden er fra, regnet fra siste børsdag,
    til linja over tabellen, radene og søylene. None for siste børsdag og
    «Velg dag». Gruppens svar 30.10 kl. 10:45 (ECH1): ikke startdagen fra
    perioder.startdag, som utenfor børskalenderen kan være en stengt dag.
    Uten en kurs i perioden er det startdagen."""
    siste = sidens_siste(rader)
    if valg is None or siste is None or valg.periode in (SISTE, VELG):
        return None
    start = startdag(valg.periode, siste)
    return foerste_kursdag(serier.values(), start, siste) or start


def periodeledd(valg: Valg | None) -> tuple[str, ...]:
    """Perioden og dagen som ledd i adressen - story 8.17a. Tomt for siste
    børsdag, som oversikten åpner med, og når adressen hadde en feil."""
    if valg is None or valg.beskjed or valg.periode == SISTE:
        return ()
    if valg.periode == VELG:
        return (f"periode={VELG}", f"dag={valg.dag.isoformat()}")
    return (f"periode={valg.periode}",)


@app.route("/aksje/<symbol>")
def aksjedetalj(symbol: str):
    """Forklaringsdelen av aksjedetaljen.

    Meldinger og kommende hendelser er ikke med: Euronext ga ikke
    tillatelse innen fristen, saa plan B gjelder fra 28.09 (Epic 10 i
    epics.md). KI-forklaringen av signalet staar under regelforklaringen
    (story 10.3).
    """
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler"):
        abort(404)
    leser = _leser_eller_basefeil()
    if leser is None:
        abort(404)

    # Aksjen slaas opp i aksje i basen, ikke i lista i kursdata.py (story 2.2b,
    # merknaden 03.10 under AD-21). 404 bare for et symbol som ikke staar der.
    oversiktsleser = _leser_eller_basefeil(hent_oversiktsleser)
    post = oversiktsleser.post(normaliser_symbol(symbol))
    if post is None:
        abort(404)

    # Story 8.16: perioden i adressen. En feil gir 6 mnd og en kort beskjed,
    # aldri en feilside. Startdagen kommer fra perioder.startdag, regnet fra
    # siste dag i grafen: dagen for «Velg dag», ellers siste rad.
    rader = leser.serie(post.aksje.symbol)
    if not rader:
        # Gruppens svar 23.10 kl. 09:24 (b): en aksje i lista uten kurser
        # svarer 200 med en beskjed, ikke 404, som FR-204 for en aksje uten
        # gyldig signal. Rettet-linja 23.10 under siste avsnitt i FR-204 i
        # prd.md (gruppens svar kl. 11:44, a): 404 gjelder bare et symbol
        # utenfor lista, og en base uten en eneste kurs foer foerste henting,
        # naar ingen side lenker dit. Siden har ingen dag og ingen periode,
        # saa ?dag= og ?periode= leses ikke (gjennomgangen 23.10, BH6,
        # ECH3). En base uten en eneste kurs gir 404 over, foer foerste
        # henting.
        return render_template("aksje_uten_kurser.html", aksje=post.aksje, hentet=None)
    # Gjennomgangen, BH10: dagen leses én gang, saa alt i svaret gjelder samme dag.
    i_dag = idag()
    valg = les_valg(request.args.get("periode"), request.args.get("dag"), rader[0].dato, i_dag, rader[-1].dato)
    slutt = valg.dag if valg.periode == VELG else rader[-1].dato
    siste_i_grafen = max(rad.dato for rad in rader if rad.dato <= slutt)
    start = startdag(valg.periode, siste_i_grafen)

    # Siste boersdag og «Velg dag»: dagen er merket, med endringen og
    # signalet som er lagret for den. Signalet regnes aldri (AD-7).
    # Story 8.16b (gruppens svar 19.10 kl. 00:00): med «Velg dag» viser hele
    # siden dagen, med raden i vurdering lest én gang for kortene, sjekkene
    # og merket i grafen.
    dagen = None
    if valg.periode == VELG:
        innhold = oversiktsleser.vurdering(post.aksje.symbol, slutt)
        detalj = bygg_detalj(post, rader, i_dag, STANDARD, start=start, slutt=slutt, dag=slutt, innhold=innhold)
        dagen = bygg_dagen(rader, slutt, innhold, i_dag)
    else:
        detalj = bygg_detalj(post, rader, i_dag, STANDARD, start=start, slutt=slutt)
        if valg.periode == SISTE:
            dagen = bygg_dagen(rader, slutt, oversiktsleser.vurdering(post.aksje.symbol, slutt), i_dag)
    if detalj is None:
        abort(404)

    # Story 10.3: KI-teksten under regelforklaringen, bare naar det er en
    # vurdering aa forklare og bryteren er paa (FR-601, FR-602).
    ki_er_paa = ki_paa(request.cookies.get(KAPSEL))
    ki = _ki_visning(post, detalj) if ki_er_paa and detalj.sjekker else None
    # Gruppens svar 25.10 kl. 00:51: setningen om dagene under KI-teksten,
    # ogsaa naar KI er av eller teksten er stoppet. «I dag» bare naar dagen
    # siden viser, er i dag (gjennomgangen, BH1, ECH6, VG1).
    dagene = _setningen_om_dagene(post, detalj, annen_dag=detalj.dato != i_dag)
    # Story 8.16b: bryteren tar deg tilbake til den samme dagen.
    tilbake = f"/aksje/{post.aksje.symbol}"
    if valg.periode == VELG:
        tilbake += f"?dag={slutt.isoformat()}"
    indeks_symbol, indeks, indeks_feilet = _indeksen_for_grafen()
    historikk = _historikken(post, rader, slutt, i_dag)
    # Pilene beholder dagen, eller perioden naar adressen hadde en gyldig.
    periode = valg.periode if request.args.get("periode") and not valg.beskjed and valg.periode != VELG else None
    dag = slutt if valg.periode == VELG else None

    def pil(maaned: date) -> str:
        return adresse(post.aksje.symbol, maaned, dag=dag, periode=periode)

    svar = app.make_response(
        render_template(
            "aksje.html",
            detalj=detalj,
            graf=bygg_graf(
                detalj.punkter,
                indeks=indeks,
                merker=AKSEMERKER.get(valg.periode, MAANEDSNAVN),
                merket=dagen.dato if dagen else None,
            ),
            valg=valg,
            dagen=dagen,
            # Story 8.16b: merket øverst bare for en dag før siste børsdag.
            tidligere_dag=valg.periode == VELG and slutt != rader[-1].dato,
            # Linja over grafen bare for den første knappen: for en valgt dag
            # står endringen og signalet i kortene.
            dagen_i_linja=valg.periode == SISTE,
            ki_tilbake=tilbake,
            grafanker=GRAFANKER,
            ki_anker=KI_ANKER,
            overskrift=OVERSKRIFT[valg.periode],
            knapper=knappene(rader[-1].dato, i_dag),
            # 1 aar og de andre periodene viser bare det serien har (FR-201).
            kort_serie=rader[0].dato > start,
            serien_begynner=rader[0].dato,
            # Datofeltet: fra andre dag i serien til siste (gjennomgangen, BH1 og BH3).
            foerste_valgbare=rader[1].dato if len(rader) > 1 else rader[0].dato,
            siste_i_serien=rader[-1].dato,
            indeks_symbol=indeks_symbol,
            indeks_feilet=indeks_feilet,
            hentet=post.hentet,
            ki=ki,
            ki_er_paa=ki_er_paa,
            dagene=dagene,
            ki_til=AV if ki_er_paa else PAA,
            # Story 10.5: lenken til investorsiden for aksjen siden viser,
            # slaatt opp paa symbolet. Siden henter ingenting derfra (AD-2).
            investorside=investorside(post.aksje.symbol),
            # Story 2.7b: maaneden for dagen siden viser, eller den i adressen.
            historikk=historikk,
            pil=pil,
            **_fotnoten([detalj.dato] if detalj.ikke_vurdert else [], i_dag),
        )
    )
    # Siden avhenger av bryteren (gjennomgangen av 10.3, BH10).
    svar.vary.add("Cookie")
    return svar


def _historikken(post, rader, dagen: date, i_dag: date) -> Maaned:
    """Story 2.7b: maaneden i historikken, lest gjennom Vurderingslager i en
    spoerring (AD-3). Lista er aksjen siden viser, fra aksje i basen, saa
    ogsaa demoselskapene kan leses. Signalet regnes aldri (AD-7)."""
    maaned, beskjed = les_maaned(request.args.get(PARAMETER), dagen, rader[0].dato, rader[-1].dato)
    lager = SqliteVurderingslager(g.tilkobling, naa, (post.aksje,))
    radene = lager.les_periode(post.aksje.symbol, *perioden(maaned))
    return bygg_maaned(maaned, [rad.dato for rad in rader], radene, i_dag, STANDARD.terskel, beskjed)


def _setningen_om_dagene(post, detalj, annen_dag: bool) -> str | None:
    """Gruppens svar 25.10 kl. 00:51: hvor lenge signalet har vaert slik, med
    tellingen fra svaret 24.10 kl. 16:15 a), lest fra vurdering (AD-3, AD-10).
    None uten en vurdering for dagen, eller naar basen ikke kan leses, ogsaa
    en base fra foer siste migrasjon, som i _ki_visning (gjennomgangen, BH7,
    ECH11)."""
    if not detalj.vurdering:
        return None
    try:
        lager = SqliteVurderingslager(g.tilkobling, naa, (post.aksje,))
        tidligere = lager.les_periode(post.aksje.symbol, date.min, detalj.dato)
    except (sqlite3.Error, ValueError, RuntimeError) as feil:
        app.logger.warning("Dagene kunne ikke leses: %s: %s", type(feil).__name__, feil)
        return None
    dager, minst = tell_dagene(detalj.dato, detalj.vurdering, tidligere)
    return setning_om_dagene(dager, minst, annen_dag=annen_dag)


def _ki_visning(post, detalj) -> KIVisning:
    """Raden i KILogg for aksjen og dagen, mot vurderingen som vises.

    Webserveren leser bare (AD-10). Kan loggen ikke leses, for eksempel i en
    base fra foer 0005, vises dagen uten KI-tekst (NFR-04).
    """
    try:
        logg = SqliteKILogg(g.tilkobling, naa)
        # Story 8.16b: dagen detaljen viser, ogsaa en valgt dag.
        rad = logg.les(Emne.aksje(post.aksje.symbol, detalj.dato))
        # Svar kl. 23:57: har andre aksjer rader for dagen? Bare lesing (AD-10),
        # og bare naar denne aksjen ikke har en rad.
        andre_har_rader = rad is None and andre_aksjer_har_ki_rad(g.tilkobling, detalj.dato, post.aksje.symbol)
    except (RuntimeError, sqlite3.Error, UgyldigKIRad, ValueError) as feil:
        # Siden vet ikke hvorfor, og sier ingen grunn. Loggen sier hvorfor
        # (gjennomgangen, BH6, BH19, og av PR 2, BH3, ECH, VG3).
        app.logger.warning("KI-loggen kunne ikke leses: %s: %s", type(feil).__name__, feil)
        return KIVisning(UKJENT)
    # Proevd mot vurderingen som vises, ikke den for siste boersdag (8.16b).
    return bygg_ki_visning(rad, detalj.vurdering, andre_har_rader=andre_har_rader)


# Bare aksjesiden kan vaere maalet for bryteren. Alt annet gaar til /, ogsaa
# en adresse med tabulator eller linjeskift, som nettleseren ellers ville
# lest som en annen side (gjennomgangen, BH1, ECH).
# Story 8.16b: med en valgt dag ogsaa ?dag= og en dato. Datoen leses paa nytt
# av les_valg, saa en dag som ikke kan vises, gir 6 mnd og en beskjed.
_TILBAKE = re.compile(r"/aksje/[A-Za-z0-9.\-]{1,20}(\?dag=[0-9]{4}-[0-9]{2}-[0-9]{2})?")
# Story 8.2a, a (U35, U36, gruppens svar 24.10 kl. 11:21): knappene som
# endrer noe paa aksjesiden, holder plassen, som pilene i historikken.
# Periodeknappene og «Velg dag» gaar til kursgrafen, og bryteren til
# KI-teksten.
GRAFANKER = "kursgrafen"
KI_ANKER = "ki-teksten"


@app.post("/ki")
def ki_bryter():
    """Bryteren for KI-teksten (FR-601, svar 4): en informasjonskapsel, og
    tilbake til siden den kom fra. Bare en sti paa samme side godtas."""
    # En annen side kan ikke slaa bryteren: kommer forespoerselen med Origin,
    # maa den vaere denne siden (gjennomgangen, BH2, ECH).
    opphav = request.headers.get("Origin")
    if opphav is not None and opphav.rstrip("/") != request.host_url.rstrip("/"):
        abort(403)
    til = AV if request.form.get("til") == AV else PAA
    tilbake = request.form.get("tilbake", "/")
    if _TILBAKE.fullmatch(tilbake):
        tilbake += f"#{KI_ANKER}"
    else:
        tilbake = "/"
    svar = redirect(tilbake, code=303)
    svar.set_cookie(KAPSEL, til, max_age=365 * 24 * 3600, samesite="Lax", httponly=True, secure=request.is_secure)
    return svar


# Story 8.3: bare oversikten og Min liste kan vaere maalet etter en merking,
# med sorteringen og «Alle» i Min liste. Adressen bygges paa nytt av det som
# er kjent, og alt annet gaar til samme side uten valg, eller til /. Tegnene
# sjekkes foerst, fordi urlsplit fjerner tabulator og linjeskift, som
# nettleseren ellers kunne lest som en annen side (som _TILBAKE over).
_TILBAKE_TEGN = re.compile(r"[A-Za-z0-9/?=&\-]{1,100}")
OVERSIKTEN = "/"
MIN_LISTE = "/min-liste"
ALLE = "alle"
# Det skjemaet sender i «til»: merk aksjen, eller ta merket bort.
MERK = "merk"
FJERN = "fjern"


def tilbake_etter_merking(tekst: str | None) -> str:
    """Adressen merkingen sender tilbake til: samme side med sorteringen."""
    if not tekst or not _TILBAKE_TEGN.fullmatch(tekst):
        return OVERSIKTEN
    deler = urlsplit(tekst)
    if deler.scheme or deler.netloc or deler.path not in (OVERSIKTEN, MIN_LISTE):
        return OVERSIKTEN
    valg = parse_qs(deler.query)
    return side_adresse(
        deler.path,
        Sortering.fra_adressen(_ett(valg, "sorter"), _ett(valg, "orden")),
        deler.path == MIN_LISTE and _ett(valg, "vis") == ALLE,
        _periodeledd_fra(deler.path, _ett(valg, "periode"), _ett(valg, "dag")),
    )


_DAG_I_ADRESSEN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _periodeledd_fra(sti: str, periode: str | None, dag: str | None) -> tuple[str, ...]:
    """Story 8.17a: perioden og dagen merkingen sender tilbake til, bare for
    oversikten og bare kjente koder. Oversikten leser dem på nytt."""
    if sti != OVERSIKTEN or periode not in PERIODENE or periode == SISTE:
        return ()
    if periode == VELG:
        return (f"periode={VELG}", f"dag={dag}") if dag and _DAG_I_ADRESSEN.fullmatch(dag) else ()
    return (f"periode={periode}",)


def _ett(valg: dict[str, list[str]], navn: str) -> str | None:
    verdier = valg.get(navn, [])
    return verdier[0] if len(verdier) == 1 else None


def side_adresse(sti: str, sortering: Sortering | None, alle: bool = False, periode: tuple[str, ...] = ()) -> str:
    """Adressen til oversikten eller Min liste, med «Alle», perioden og
    dagen (story 8.17a) og sorteringen."""
    valg = []
    if alle:
        valg.append(f"vis={ALLE}")
    valg += periode
    if sortering is not None:
        valg += [f"sorter={sortering.kolonne}", f"orden={sortering.orden}"]
    return sti + ("?" + "&".join(valg) if valg else "")


@app.post("/min-liste/merk")
def merk():
    """Stjernen - story 8.3, FR-101, AD-3, AD-10. Merker aksjen eller tar
    merket bort, og sender tilbake til samme side med sorteringen (303).

    Som bryteren for KI-teksten: kommer forespoerselen med Origin, maa den
    vaere denne siden. Webserveren skriver bare tabellen min_liste, gjennom
    porten, og henter aldri noe (AD-10).
    """
    opphav = request.headers.get("Origin")
    if opphav is not None and opphav.rstrip("/") != request.host_url.rstrip("/"):
        abort(403)
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("tilkobling") is None:
        abort(404)
    til = request.form.get("til")
    if til not in (MERK, FJERN):
        abort(400)
    symbol = request.form.get("symbol", "")
    try:
        lager = SqliteMinlistelager(g.tilkobling)
        (lager.merk if til == MERK else lager.fjern)(symbol)
    except UkjentAksje:
        abort(400)
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)
        return _basen_kan_ikke_aapnes()
    # Gjennomgangen (BH5): tilbake til raden, ikke til toppen av siden.
    # Symbolet er godtatt av porten, saa ankeret har bare kjente tegn.
    return redirect(tilbake_etter_merking(request.form.get("tilbake")) + f"#rad-{symbol}", code=303)


if __name__ == "__main__":
    # Story 3.4: --demo setter bryteren, saa kommandoen er lik i PowerShell
    # og i bash.
    les_flagg(sys.argv[1:])
    app.run(debug=True, port=8000)
