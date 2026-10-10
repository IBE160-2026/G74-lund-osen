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

import os
import sqlite3
import sys
import threading
from collections.abc import Callable
from datetime import date, datetime, timezone
from pathlib import Path

from flask import Flask, abort, g, render_template, request

import lagring_sqlite
from aksjedetalj import bygg_detalj, normaliser_symbol
from boersdag import norsk_dato
from graf import bygg_graf
from kursdata import Kursleser
from demo import DEMOKOMMANDO
from lagring_sqlite import (
    DEMOMERKE,
    SqliteKurslager,
    SqliteOversiktsleser,
    aapne_base,
    demo_sti,
    har_kurser,
    les_merket,
)
from markedsoversikt import (
    bygg_oversikt,
    eldre_enn_nyeste,
    norsk_tid,
    sidens_dato,
    sidens_tidsstempel,
    uten_kurser,
)
from migrering import MigrasjonsFeil
from oversiktsdata import Oversiktsleser
from tallformat import tall

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


def _base_sti() -> Path:
    """Basen bryteren velger: demo.db eller den ekte ose.db."""
    return Path(demo_sti() if demo_paa() else lagring_sqlite.BASE_STI).resolve()


def hentekommando() -> str:
    """Kommandoen for maaten appen kjoerer paa, lest fra miljoeet (AD-10, AD-12)."""
    return HENTEKOMMANDO_DOCKER if os.environ.get(I_DOCKER) == "1" else HENTEKOMMANDO

# Feil som betyr at basen ikke kan aapnes eller migreres, som BASEFEIL i
# hentingen. Siden svarer da 503 med grunnen i stedet for en traceback.
BASEFEIL = (sqlite3.Error, OSError, MigrasjonsFeil, RuntimeError)

app = Flask(__name__)
app.jinja_env.filters["norsk_tid"] = norsk_tid
# Regel 21: tallene formateres ett sted, ikke med "%.2f" i malene (story 8.0).
app.jinja_env.filters["tall"] = tall

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
# ikke.
_RUTER_MED_BASE = {"markedsoversikt", "aksjedetalj"}


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
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False)
            g.eksempeltall = les_merket(g.tilkobling) == DEMOMERKE
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


@app.context_processor
def _eksempeltall():
    """«Eksempeltall» paa hver side som viser en base med demomerket."""
    return {"eksempeltall": g.get("eksempeltall", False)}


@app.teardown_appcontext
def _lukk_basen(_unntak) -> None:
    tilkobling = g.pop("tilkobling", None)
    if tilkobling is not None:
        tilkobling.close()


def _basen_kan_ikke_aapnes():
    return (
        render_template(
            "basefeil.html", feil=g.basefeil, base=_base_sti().name
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


@app.route("/")
def markedsoversikt():
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler"):
        return render_template(
            "index.html", rader=[], dato=None, hentet=None, mangler=[], eget=set(),
            demokommando=DEMOKOMMANDO,
        )
    leser = _leser_eller_basefeil()
    if leser is None:
        return render_template(
            "index.html",
            rader=[],
            dato=None,
            hentet=None,
            mangler=[],
            eget=set(),
            hentekommando=hentekommando(),
        )

    poster = _leser_eller_basefeil(hent_oversiktsleser).oversikt()
    rader = bygg_oversikt(poster, idag())

    return render_template(
        "index.html",
        rader=rader,
        dato=sidens_dato(rader),
        hentet=sidens_tidsstempel(rader),
        eget=eldre_enn_nyeste(rader),
        mangler=uten_kurser(poster),
        ikke_vurdert=any(rad.ikke_vurdert for rad in rader),
        hentekommando=hentekommando(),
    )


@app.route("/aksje/<symbol>")
def aksjedetalj(symbol: str):
    """Forklaringsdelen av aksjedetaljen.

    Meldinger og kommende hendelser er ikke med: Euronext ga ikke
    tillatelse innen fristen, saa plan B gjelder fra 28.09 (Epic 10 i
    epics.md). KI-forklaringen av signalet kommer med Epic 10.
    """
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler"):
        abort(404)
    leser = _leser_eller_basefeil()
    if leser is None:
        abort(404)

    # Aksjen slaas opp i aksje i basen, ikke i lista i kursdata.py (story 2.2b,
    # merknaden 03.10 under AD-21). 404 bare for et symbol som ikke staar der,
    # og for en aksje uten kursrader (FR-204).
    post = _leser_eller_basefeil(hent_oversiktsleser).post(normaliser_symbol(symbol))
    if post is None:
        abort(404)

    detalj = bygg_detalj(post, leser.serie(post.aksje.symbol), idag())
    if detalj is None:
        abort(404)

    return render_template(
        "aksje.html",
        detalj=detalj,
        graf=bygg_graf(detalj.punkter),
        hentet=post.hentet,
    )


if __name__ == "__main__":
    # Story 3.4: --demo setter bryteren, saa kommandoen er lik i PowerShell
    # og i bash.
    if "--demo" in sys.argv[1:]:
        os.environ[I_DEMO] = "1"
    app.run(debug=True, port=5000)
