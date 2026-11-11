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
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

from flask import Flask, abort, g, redirect, render_template, request

import ferdige_lister
import innstillinger
import lagring_sqlite
import valg
from aksjedetalj import bygg_dagen, bygg_detalj, normaliser_symbol
from boersdag import UtenforKalenderen, forrige_boersdag, innevaerende_boersdag, norsk_dato
from boersometer import (
    BRANSJER,
    GRENSE_STERK,
    UTEN_DATA,
    annen_grunn_i_kartet,
    bygg_boersometer,
    bygg_rute,
    dagen_foer,
    indeks_for_dagen,
    kart,
    skalagrenser,
    trinnforklaringer,
    vis_dagen_foer,
)
from boersometer import (
    med_perioden as rute_med_perioden,
)
from dagene import foerste_dag_i_rekka, lag_dagsbilde, setning_om_dagene, setning_om_samme_dag, tell_dagene
from dagsgrunnlag import dagsgrunnlag, min_liste_linje, vanlig_fra
from demo import DEMOKOMMANDO, DEMOKOMMANDO_DOCKER, STARTDAG, gammel_demobase
from demo import UTEN_KURSER as DEMO_UTEN_KURSER_SYMBOL
from etterpaa import brikkene, bygg_etterpaa, bygg_handelen
from graf import LAPPBREDDE, LAPPHOYDE, bygg_graf
from historikk import (
    PARAMETER,
    Maaned,
    adresse,
    alle_sjekkene_det_siste_aaret,
    bygg_maaned,
    les_maaned,
    maanedsnavn,
    perioden,
)
from hjelpetekster import (
    ANTALL_SJEKKER,
    DEMO_UTEN_KURSER,
    UTEN_KURSER_HVORFOR,
    Hjelp,
    hjelpetekster,
    omvisningen,
    rundturer,
)
from hovedindeks import Hovedindeksvisning, bygg_hovedindeks, er_bedre, valgt_indeks
from investorsider import demoside, eodhd_demoside
from justeringsdager import justeringsdager
from ki_visning import (
    AV,
    DAGEN_AV,
    DAGEN_UTEN,
    INGEN_I_DEMOEN,
    INGEN_RAD,
    KAPSEL,
    PAA,
    PERIODEN_UTEN,
    UKJENT,
    KIVisning,
    bygg_dagsvisning,
    bygg_ki_visning,
    ki_paa,
    ki_tekst,
    prikkede_tall,
)
from kilogg import Emne, UgyldigKIRad
from kursdata import Kursleser, investorside
from lagring_sqlite import (
    DEMOMERKE,
    SqliteIndekslager,
    SqliteKILogg,
    SqliteKurslager,
    SqliteMinlistelager,
    SqliteNotatlager,
    SqliteOversiktsleser,
    SqliteVurderingslager,
    aapne_base,
    andre_aksjer_har_ki_rad,
    demo_sti,
    har_kurser,
    les_merket,
)
from markedsoversikt import (
    UTEN_DATA_TEKST,
    Sortering,
    antall_vurdert,
    bygg_oversikt,
    bygg_rad_for_dag,
    bygg_sammenligning,
    del_i_to,
    egne_dager,
    eldre_enn_nyeste,
    ingen_skilte_seg_ut,
    med_perioden,
    neste_orden,
    norsk_tid,
    oppdatert,
    periodeendring,
    rader_som_venter,
    rader_uten_data,
    sidens_dato,
    sidens_tidsstempel,
    sorter,
    sorter_fr102,
)
from migrering import MigrasjonsFeil
from minliste import UkjentAksje
from notater import MAKS_TEGN, UgyldigNotat
from oversiktsdata import Oversiktsleser
from perioder import (
    AKSEMERKER,
    MAANEDSNAVN,
    OVERSKRIFT,
    PERIODENE,
    SISTE,
    VELG,
    Valg,
    dagen_i_feltet,
    foerste_kursdag,
    knappene,
    les_valg,
    pilene,
    startdag,
)
from perioder import BOERSOMETERET as BOERSOMETER_VALG
from perioder import MIN_LISTE as MIN_LISTE_VALG
from perioder import OVERSIKTEN as OVERSIKTEN_VALG
from signalberegning import BLANDET, STANDARD
from tallformat import avrundet, dato, med_og, tall, ukedag
from vurderingsdata import Grunn, Vurdering

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
# Story 8.2b, c (U67): tallene i en KI-tekst som vises, med prikket strek.
app.jinja_env.filters["prikkede_tall"] = prikkede_tall
# Story 8.20a (U88): og navnene paa sjekkene med fet skrift.
app.jinja_env.filters["ki_tekst"] = ki_tekst
# Story 2.7b: «oktober 2026» ved pilene i historikken.
app.jinja_env.filters["maanedsnavn"] = maanedsnavn
# Story 8.21 (tillegget kl. 14:44): sjekkene ved et tenkt kjøp eller salg.
app.jinja_env.filters["brikkene"] = brikkene
# Story 8.15: retningen et klikk på en kolonne gir.
app.jinja_env.globals["neste_orden"] = neste_orden
# Story 8.20a (del B): dagen i datofeltet og pilene ved den.
app.jinja_env.globals["dagen_i_feltet"] = dagen_i_feltet
app.jinja_env.globals["pilene"] = pilene
# Story 8.20a (del C): størrelsen på lappen ved musepekeren i grafen.
app.jinja_env.globals["lappbredde"] = LAPPBREDDE
app.jinja_env.globals["lapphoyde"] = LAPPHOYDE


def soeylestyrke(endring: float) -> str:
    """«sterk» fra GRENSE_STERK opp eller ned, slik endringen vises, ellers
    «lys». Gruppens svar 04.11 kl. 09:58: søylene under hovedindeksen er
    mørke fra samme grense som børsometeret (designregler §5, rettet
    04.11)."""
    return "sterk" if abs(avrundet(endring, "endring")) >= GRENSE_STERK else "lys"


app.jinja_env.filters["soeylestyrke"] = soeylestyrke
app.jinja_env.globals["soeylegrense"] = tall(GRENSE_STERK, "grense")
# Story 8.26 (tillegg 8): ordene og forklaringen for en aksje uten kurser,
# likt på alle sidene.
app.jinja_env.globals["uten_data_tekst"] = UTEN_DATA_TEKST
app.jinja_env.globals["uten_data_kort"] = UTEN_DATA
app.jinja_env.globals["uten_kurser_hvorfor"] = UTEN_KURSER_HVORFOR
app.jinja_env.globals["demo_uten_kurser"] = DEMO_UTEN_KURSER
# Gjennomgangen (BH4): setningen bare på siden for den aksjen.
app.jinja_env.globals["demo_uten_kurser_symbol"] = DEMO_UTEN_KURSER_SYMBOL
# Story 8.26 (tillegg 3): beskjeden når appen følger så mange aksjer den kan.
app.jinja_env.globals["full_tekst"] = valg.FULL
# Story 8.26 (tillegg 3): ønsket om å følge. Eget navn, fordi oversikten har
# en parameter som heter valg.
ONSKE_FOLG = valg.FOLG
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
# ikke. Story 8.3: Min liste og merkingen, som var den eneste ruta som skrev;
# fra 2.12, 8.10 og 8.10b skriver ogsaa oensket, innstillingene og bryteren.
# Story 3.4h: siden for et selskap i demoen leser demomerket i basen (PRAGMA
# application_id, DEMOMERKE), så den bare finnes i demoen. Rettet 2026-11-09
# (gjennomgangen av 3.4h, BH16): her sto «merket», som ogsaa er merkingen i
# Min liste, og at merkingen er den eneste ruta som skriver.
_RUTER_MED_BASE = {
    "markedsoversikt",
    "aksjedetalj",
    "min_liste",
    "merk",
    "boersometer",
    "demoselskap",
    # Story 8.26 (tillegg 12): siden for «Åpne eodhd.com» i demoen.
    "eodhd_demo",
    # Story 2.12: siden «Følg en aksje» og skjemaene for ønsket.
    "folg_side",
    # Tillegg 3 til 8.22: siden «Er du sikker?» før en ferdig liste.
    "ferdig_liste_side",
    # Story 8.10: «Innstillinger».
    "innstillinger_side",
    "lagre_innstilling",
    # Story 8.10b: bryteren ved KI-teksten skriver valget i basen.
    "ki_bryter",
    "folg",
    "fjern_egen",
    "angre",
    # Story 8.11: en ferdig liste.
    "bruk_ferdig_liste",
    # Story 8.21: «Mine notater» på aksjesiden.
    "skriv_notat",
    "slett_notat",
    # Tillegget kl. 14:44: tenkte kjøp og salg.
    "noter_tenkt_kjoep",
    "noter_tenkt_salg",
}

# Story 8.3: ruta som skriver merkingen. Bare den aapner en demobase for
# skriving, og bare tabellen min_liste skrives (AD-3, AD-10).
_SKRIVER = "merk"
# Story 2.12: rutene som skriver ønsket i oenske, og bare den tabellen (AD-3).
# Story 8.26 (tillegg 3, gjennomgangen VG7): «Følg» og «Angre» skriver også
# stjernen i min_liste, i samme transaksjon som ønsket (valg.py, 0013).
_SKRIVERE = frozenset((_SKRIVER, "folg", "fjern_egen", "angre", "bruk_ferdig_liste", "lagre_innstilling", "ki_bryter"))
# Story 8.21 (gruppens svar 10.11 kl. 14:32): rutene som skriver notatene, og
# bare tabellen notat (AD-3).
_SKRIVERE |= {"skriv_notat", "slett_notat", "noter_tenkt_kjoep", "noter_tenkt_salg"}


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
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False, skrivebeskyttet=request.endpoint not in _SKRIVERE)
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
            g.tilkobling = aapne_base(sti, kjoer_migrasjoner=False, skrivebeskyttet=request.endpoint not in _SKRIVERE)
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
def _utenfor_maalingen():
    """Story 2.12 (gjennomgangen, VG2, ECH10): «Utenfor målingen» ved navnet i
    oversikten, på aksjesiden og i børsometeret, med omsetningen og hva
    signalet er målt på når man peker på merket (utdraget 08.11 §2). Bare for
    egne aksjer; de 15 er målt (malinger.md §36). Bare lesing."""
    if request.endpoint not in _RUTER_MED_BASE:
        return {"utenfor": {}}
    egne = _egne()
    return {"utenfor": egne["utenfor_tekst"] if egne else {}}


@app.context_processor
def _omvisningen():
    """Story 8.25: stegene i «Spill av omvisningen», på hver side, som
    «Vis meg rundt»: borte når «Vis hjelp» er av i Innstillinger. Bare
    lesing, og lik i demoen og i den ekte versjonen."""
    if not innstillinger.les(g.get("tilkobling"))[innstillinger.VIS_HJELP]:
        return {"omvisning": None}
    return {"omvisning": omvisningen(STANDARD)}


@app.context_processor
def _innstillingene():
    """Story 8.10 (FR-110): valgene i «Innstillinger», på hver side. Bare
    lesing. Uten basen er alt på."""
    valgene = innstillinger.les(g.get("tilkobling"))
    # Story 8.21 (tillegget kl. 14:44): «Notater» skjuler notatene på
    # aksjesidene og i Min liste, men sletter ingenting.
    return {
        "valgene": valgene,
        "vis_hjelp": valgene[innstillinger.VIS_HJELP],
        "vis_notater": valgene[innstillinger.VIS_NOTATER],
    }


@app.context_processor
def _hjelp():
    """Hjelpetekstene og parametrene paa hver side, laget av samme objekt.
    antall_sjekker er «3» i «N av 3» (story 8.0c), fra samme sted som hjelpen."""
    return {
        "hjelp": Hjelp(hjelpetekster(STANDARD)),
        # Story 8.9: stegene i «Vis meg rundt», fra samme fil.
        "rundturer": rundturer(STANDARD),
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


@app.context_processor
def _oppdatert_overalt():
    """Story 8.26 (tillegg 17): tidspunktet i linja «Oppdatert …» for sidene
    som ikke har sitt eget, som «Følg en aksje», «Er du sikker?»,
    Innstillinger og sidene i demoen: det eldste tidspunktet en aksje med
    kurser sist ble hentet, som på oversikten (FR-101). Bare lesing."""
    if request.endpoint not in _RUTER_MED_BASE or g.get("basefeil"):
        return {"hentet_felles": None}
    try:
        leser = hent_oversiktsleser()
        if leser is None:
            return {"hentet_felles": None}
        tider = [post.hentet for post in leser.oversikt(idag()) if post.nyeste is not None and post.hentet]
    except BASEFEIL:
        return {"hentet_felles": None}
    return {"hentet_felles": min(tider) if tider else None}


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
    slutt: date | None = None,
    start: date | None = None,
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
    seriene som alt er lest for tabellen, brukes paa nytt. slutt er
    tabellens dag, som soeylene og linja foelger (gruppens svar 30.10 kl.
    10:45, VG5), og start dagen den første kursen i perioden er fra, den
    samme som i linja over tabellen (gjennomgangen 30.10, BH3 og ECH1).
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
        return bygg_hovedindeks(symbol, lager.serie(symbol), aksjer, grunnlag, periode, dag, slutt, start), False
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


def _indeksen_for_perioden(start: date, siste: date) -> float | None:
    """Endringen i hovedindeksen fra start til siste børsdag, til linja «Mål
    mot børsen» ved en periode - story 8.17b, regnet som indekslinja i
    oversikten (periodeendring). None som _indeksen_for_dagen, og når
    indeksen begynner etter start, som indekslinja (gjennomgangen, ECH1)."""
    try:
        lager = SqliteIndekslager(g.tilkobling)
        symboler = lager.symboler()
        if not symboler:
            return None
        utfall = periodeendring(lager.serie(valgt_indeks(symboler)), start, siste)
        return utfall[0] if utfall is not None and utfall[1] is None else None
    except (*BASEFEIL, ValueError):
        return None


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
    # Story 8.26 (tillegg 2): teksten i en rute uten kurser, fra boersometer.py.
    felles = {"aktiv": BOERSOMETER, "uten_kurs_kort": UTEN_DATA}
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
    # Story 2.11 (gjennomgangen, BH1, ECH1): aksjene i lista i dag.
    poster = oversiktsleser.oversikt(idag())
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
    # Story 8.17b: periodevalget fra 8.16. Dagen leses som før (?dag=), og
    # perioden med les_valg uten dag. Ved en periode er dagen siste børsdag,
    # og periodestart dagen den første kursen i perioden er fra, som i
    # oversikten (gruppens svar 30.10 kl. 10:45, a).
    # En dag som ikke kan leses, har sin egen beskjed (ugyldig), og siste
    # børsdag valgt som dag er siste børsdag, som i oversikten (8.17a, BH5).
    if ugyldig or (oenske and dagen == siste):
        valg = Valg(SISTE)
    elif oenske:
        valg = Valg(VELG, dag=dagen)
    else:
        valg = les_valg(request.args.get("periode"), None, datoer[0], i_dag, siste, BOERSOMETER_VALG)
    periodestart = None
    if valg.periode not in (SISTE, VELG):
        start = startdag(valg.periode, siste)
        periodestart = foerste_kursdag(serier.values(), start, siste) or start
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
    if periodestart is not None:
        ruter = [rute_med_perioden(rute, serier[rute.aksje.symbol], periodestart, siste) for rute in ruter]
    bransjer = bygg_boersometer(ruter)
    ikke_vurdert = any(rute.ikke_vurdert for rute in ruter)
    # Story 8.6b, d: kartet regnes av de samme bransjene som tabellen.
    # Gjennomgangen 26.10 (BH, ECH): får rutene ikke plass, står tabellen
    # alene, som indeksen i linja (NFR-03).
    try:
        kartet = kart(bransjer)
    except ValueError:
        kartet = kart([])
    # Gruppens svar 05.11 kl. 09:34, 1: en egen fotnote når en rute sier
    # «ikke vurdert» av en annen grunn, ved siden av den gamle, regnet av
    # rutene i kartet (gjennomgangen, ECH1).
    annen_grunn = annen_grunn_i_kartet(kartet)
    indeks = _indeksen_for_dagen(dagen) if periodestart is None else _indeksen_for_perioden(periodestart, siste)
    # Story 8.20b (spørsmål 14 b): «N av M gikk bedre enn indeksen» i kortet
    # «Mål mot børsen», med aksjene som har en endring, slik tallene vises
    # (er_bedre, som oversikten). Gjennomgangen (BH1, ECH2): en aksje med
    # kortere serie i perioden («fra» en senere dag) telles ikke, fordi
    # endringen gjelder et annet tidsrom enn indeksen. ECH1: uten aksjer å
    # telle står ikke tallet.
    med_endring = [rute for rute in ruter if rute.endring is not None and rute.fra is None]
    bedre = sum(er_bedre(rute.endring, indeks) for rute in med_endring) if indeks is not None and med_endring else None
    return render_template(
        "boersometer.html",
        bransjer=bransjer,
        kart=kartet,
        antall_aksjer=len(ruter),
        ikke_vurdert=ikke_vurdert,
        annen_grunn=annen_grunn,
        **_fotnoten([dagen] if ikke_vurdert else [], i_dag),
        dagen=dagen,
        siste=siste,
        foerste=datoer[0],
        # Gjennomgangen av 8.20a (ECH2): pilene ved datoen går til dagene med kurs.
        kursdager=datoer,
        # Gjennomgangen 26.10 (ECH4): datoen når børsdagen før er mer enn 6 dager før.
        dagen_foer=vis_dagen_foer(dagen_foer(datoer, dagen), dagen, i_dag.year),
        volum_vindu=STANDARD.volum_vindu,
        indeksendring=indeks,
        bedre=bedre,
        med_endring=len(med_endring),
        fargetrinn=trinnforklaringer(),
        skalagrenser=skalagrenser(),
        # Story 8.17b: periodevalget, og perioden i adressen.
        valg=valg,
        knapper=knappene(siste, i_dag),
        periodestart=periodestart,
        periodenavn=OVERSKRIFT.get(valg.periode) if periodestart is not None else None,
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
    # Story 8.23 (tillegg 2): «Min liste» over «Aksjene» på oversikten.
    bare_min = not i_lista and request.args.get("vis") == BARE_MIN
    # De merkede alene: Min liste uten «Alle», eller oversikten med «Min liste».
    bare_merkede = (i_lista and not alle) or bare_min
    sti = MIN_LISTE if i_lista else OVERSIKTEN
    felles = {"aktiv": aktiv, "sidesti": sti, "alle": alle, "bare_min": bare_min}
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
    # Story 2.11 (gjennomgangen, BH1, ECH1): aksjene i lista i dag.
    poster = oversiktsleser.oversikt(idag())
    i_dag = idag()
    rader = bygg_oversikt(poster, i_dag, STANDARD, _dager_i_serien(leser, poster))
    # Story 8.15: linja om 3 av 3 og «N av M» bruker rader, som står i
    # FR-102 (svar 7). Story 8.2a, e (gruppens svar 24.10 kl. 11:39): uten
    # en valgt kolonne er tabellen delt i to, hver i FR-102-rekkefølgen, som
    # før. Med en kolonne valgt er den én liste, sortert under (sortert), og
    # ikke sortert innenfor hver del, som tillegget 13.10 sa.
    sortering = Sortering.fra_adressen(request.args.get("sorter"), request.args.get("orden"))
    tre_av_tre = frozenset(rad.aksje.symbol for rad in rader if rad.styrke == ANTALL_SJEKKER)
    # Story 8.17a: periodevalget i oversikten. Overskriften, linja om 3 av
    # 3 og tidspunktet gjelder siste børsdag, og vist er radene tabellen
    # viser: en periode gir endringen for perioden, og «Velg dag» radene for
    # dagen, lest og aldri regnet (AD-7).
    # Story 8.17b: i Min liste er periodevalget «Sammenlign med». Radene er
    # siste børsdag, og hver rad får linja under for dagen man sammenligner
    # med (beslutningen 08.10 kl. 21:48).
    serier = _seriene(leser, poster)
    valg = _valget(rader, serier, i_dag, MIN_LISTE_VALG if i_lista else OVERSIKTEN_VALG)
    vist = rader
    # Gruppens svar 30.10 kl. 10:45 (ECH1): én dag for linja, radene og
    # søylene, den første kursen i perioden.
    periodestart = _periodestart(valg, rader, serier)
    sammenligner = i_lista and valg is not None and valg.periode != SISTE and (valg.dag or periodestart)
    if sammenligner:
        dag = valg.dag if valg.periode == VELG else periodestart
        etter_symbol = {post.aksje.symbol: post for post in poster}
        vist = [
            replace(
                rad,
                under=bygg_sammenligning(
                    etter_symbol[rad.aksje.symbol],
                    serier.get(rad.aksje.symbol, []),
                    dag,
                    rad.dato,
                    partial(oversiktsleser.vurdering, rad.aksje.symbol),
                    i_dag,
                    valg.periode != VELG,
                ),
            )
            for rad in rader
        ]
    elif valg is not None and valg.periode == VELG:
        # Story 2.11 (gjennomgangen, BH2): aksjene i lista den valgte dagen,
        # også en som er tatt ut siden.
        poster_dagen = oversiktsleser.oversikt(valg.dag)
        vist = sorter_fr102(
            [
                bygg_rad_for_dag(
                    post,
                    serier[post.aksje.symbol] if post.aksje.symbol in serier else leser.serie(post.aksje.symbol),
                    valg.dag,
                    oversiktsleser.vurdering(post.aksje.symbol, valg.dag),
                    i_dag,
                    post.aksje.symbol in tre_av_tre,
                )
                for post in poster_dagen
                if post.nyeste is not None
            ]
        )
    elif periodestart is not None and not i_lista:
        vist = med_perioden(rader, serier, periodestart)
    annen_dag = not i_lista and valg is not None and valg.periode == VELG
    skilte_seg_ut, oevrige = del_i_to(rader if annen_dag else vist)
    # Story 8.26 (gruppens svar 11.11 kl. 22:04, tillegg 17): med «Vis dagen»
    # sier overskriften og linja om 3 av 3 dagen tabellen viser, ikke siste
    # børsdag. Radene for en annen dag merker ikke 2 av 3 (8.17a), så de som
    # skilte seg ut den dagen, regnes av styrken mot terskelen.
    dagens_rader = vist if annen_dag else rader
    if annen_dag:
        skilte_seg_ut = [rad for rad in vist if rad.styrke is not None and rad.styrke >= STANDARD.terskel]
    # Story 8.3: merkingen leses fra sin egen port, bare lesing her.
    minlista = _leser_eller_basefeil(lambda: SqliteMinlistelager(g.tilkobling))
    # Story 8.26 (tillegg 3): også stjernen på en aksje som venter.
    merkede = minlista.merkede() | minlista.merkede_som_venter()
    # Story 8.2a, b (U23): en aksje uten kurser har en rad nederst, ikke
    # bare navnet i en fotnote. Story 8.26 (gruppens svar 11.11 kl. 17:47,
    # tillegg 3): aksjene som venter på hentingen etter «Følg», står under
    # dem med «venter på henting», så de også synes under «Min liste». I
    # demoen står de der alltid, fordi demoen ikke henter.
    valglager = _valglager()
    venter = rader_som_venter(
        [(o.symbol, o.navn, o.sektor) for o in valglager.ventende() if o.handling == ONSKE_FOLG] if valglager else [],
        {post.aksje.symbol for post in poster},
    )
    # Gjennomgangen (ECH7): ikke med «Velg dag», som er en dag appen ikke
    # fulgte dem.
    annen_dag_valgt = not i_lista and valg is not None and valg.periode == VELG
    alle_uten_data = [*rader_uten_data(poster), *([] if annen_dag_valgt else venter)]
    mangler = alle_uten_data
    # Gjennomgangen (BH8, ECH2): antallet er de merkede som har en rad i
    # tabellen, saa knappen og tabellen sier det samme. Story 8.2a, b: ogsaa
    # en merket aksje uten kurser, som naa har en rad.
    antall_merket = sum(rad.aksje.symbol in merkede for rad in (*rader, *alle_uten_data))
    # Gjennomgangen av 8.2b (BH2, ECH8, VG6): tittelen i Min liste står med
    # tall bare når minst én merket aksje er vurdert.
    vurdert_i_lista = sum(1 for rad in rader if rad.aksje.symbol in merkede and rad.styrke is not None)
    # Story 8.2a, e: hele lista sortert på kolonnen, med radene uten data,
    # som står sist når kolonnen ikke har en verdi for dem. None uten
    # sortering. De som skilte seg ut, beholder kanten i malen.
    sortert = sorter([*vist, *alle_uten_data], sortering) if sortering else None
    # Story 8.17a: en valgt dag er én liste uten delene, fordi «Skilte seg
    # ut» gjelder siste børsdag (gruppens svar 23.10 kl. 12:35, a).
    if annen_dag and sortert is None:
        sortert = [*vist, *alle_uten_data]
    # Gjennomgangen av 8.23 (ECH1, BH2, VG1): overskriften på oversikten
    # gjelder alle aksjene, også med «Min liste», som bare filtrerer tabellen.
    alle_som_skilte_seg_ut = skilte_seg_ut
    if bare_merkede:
        skilte_seg_ut = [rad for rad in skilte_seg_ut if rad.aksje.symbol in merkede]
        oevrige = [rad for rad in oevrige if rad.aksje.symbol in merkede]
        mangler = [rad for rad in mangler if rad.aksje.symbol in merkede]
        if sortert is not None:
            sortert = [rad for rad in sortert if rad.aksje.symbol in merkede]
    # Story 8.26 (gruppens ønske 11.11 kl. 17:48, tillegg 4): filteret på
    # signalet fra 8.11 og 8.23 er tatt bort, fordi det ikke viste noe
    # tabellen ikke alt viser under «Skilte seg ut».
    overskrift_ut = alle_som_skilte_seg_ut if bare_min else skilte_seg_ut
    har_rader = bool(skilte_seg_ut or oevrige or mangler or sortert)
    hovedindeks, indeks_feilet = (
        (None, False)
        if i_lista
        else _hovedindeks(leser, poster, tre_av_tre, valg, serier, sidens_siste(rader), periodestart)
    )
    # Story 3.4e: datoene som er «ikke vurdert» i det siden viser, én gang.
    ikke_vurdert = [rad.dato for rad in (vist if annen_dag else (*skilte_seg_ut, *oevrige)) if rad.ikke_vurdert]
    # Story 8.17b: også dagen i linja under i Min liste.
    ikke_vurdert += [
        rad.under.dato for rad in (*skilte_seg_ut, *oevrige) if rad.under is not None and rad.under.ikke_vurdert
    ]
    ledd = periodeledd(valg)

    return render_template(
        "index.html",
        # Story 8.21 (tillegget kl. 14:44): alle notatene samlet nederst i Min
        # liste, nyeste først, med lenke til aksjen. Bare med bryteren på.
        alle_notater=_alle_notatene(valg is not None and valg.periode == VELG) if i_lista else None,
        alle_notater_tidligere_dag=valg is not None and valg.periode == VELG,
        alle_notater_indeks=_indeksen_for_grafen()[0] if i_lista else None,
        # Story 8.24: skjemaene ved notatene sender tilbake til samme liste.
        alle_notater_vis="min-liste-alle" if alle else "min-liste",
        rader=rader,
        hovedindeks=hovedindeks,
        indeks_feilet=indeks_feilet,
        dato=valg.dag if annen_dag else sidens_dato(rader),
        hentet=sidens_tidsstempel(rader),
        eget=eldre_enn_nyeste(rader),
        # Gruppens svar 03.11 kl. 14:28: en rad med eldre dag viser datoen sin.
        egne_dager=egne_dager(rader, sidens_siste(rader)),
        mangler=mangler,
        # Story 8.0d, PR 2b: M i «N av M aksjer» er alle aksjene i lista,
        # også de uten kurser (beslutningen 14.10). Story 8.2a, b (U23): det
        # er også antallet rader i tabellen, fordi hver aksje uten kurser nå
        # har en rad, så «7 av 15» stemmer med tabellen. Summen er lik
        # len(poster), og definisjonen fra 14.10 står (gjennomgangen, BH5).
        # Story 8.26 (tillegg 3, gjennomgangen ECH3): aksjene som venter, er
        # med, som radene, «Min liste N» og «appen følger 16 av 18».
        antall_aksjer=len(rader) + len(alle_uten_data),
        ikke_vurdert=bool(ikke_vurdert),
        **_fotnoten(ikke_vurdert, i_dag),
        # Gjennomgangen (BH7, ECH1): «Alle» i Min liste er samme tabell som
        # oversikten, ogsaa naar ingen skilte seg ut.
        ingen_skilte_seg_ut=ingen_skilte_seg_ut(dagens_rader) and not bare_merkede,
        antall_vurdert=antall_vurdert(dagens_rader),
        skilte_seg_ut=skilte_seg_ut,
        oevrige=oevrige,
        sortert=sortert,
        sortering=sortering,
        tre_av_tre=[rad.aksje.navn for rad in dagens_rader if rad.styrke == ANTALL_SJEKKER],
        hentekommando=hentekommando(),
        merkede=merkede,
        antall_merket=antall_merket,
        vurdert_i_lista=vurdert_i_lista,
        tilbake=side_adresse(sti, sortering, alle, ledd, bare_min),
        # Story 8.17a: periodevalget, og perioden og dagen i lenkene.
        valg=valg,
        knapper=knappene(sidens_siste(rader), i_dag) if valg else (),
        # Gjennomgangen (ECH9): navnet midt i en setning, «i år» med liten i.
        periodenavn=OVERSKRIFT.get(valg.periode) if valg and valg.periode not in (SISTE, VELG) else None,
        periodestart=periodestart,
        foerste_valgbare=_foerste_valgbare(serier),
        siste_dag=sidens_siste(rader),
        periodeledd=ledd,
        standard_adresse=side_adresse(sti, None, alle, ledd, bare_min),
        # Story 2.12: «Dine egne aksjer» på oversikten og «Din egen liste» i
        # Min liste, og merket «Egen» i tabellen.
        egne=_egne(),
        # Story 8.23 (tillegg 1): overskriften i Min liste med «Alle».
        antall_ut=len(overskrift_ut),
        overskrift_ut=overskrift_ut,
        har_rader=har_rader,
        # Story 10.6: «Børsdagen kort fortalt», bare paa oversikten.
        boersdagen=None
        if i_lista
        else _boersdagen(poster, serier, valg, sidens_siste(rader), oversiktsleser, ledd, sortering),
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


def _valget(rader: list, serier: dict[str, list], i_dag: date, side: str = OVERSIKTEN_VALG) -> Valg | None:
    """Perioden og dagen fra adressen til oversikten - story 8.17a - eller
    Min liste (8.17b). Siste børsdag uten noe i adressen og ved en feil, med
    beskjeden. None uten rader, for da er det ingen tabell å velge for."""
    siste = sidens_siste(rader)
    if siste is None:
        return None
    foerste = min((serie[0].dato for serie in serier.values() if serie), default=siste)
    valg = les_valg(request.args.get("periode"), request.args.get("dag"), foerste, i_dag, siste, side)
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
        # Story 3.4h (spørsmål 5): boblen nederst også her.
        return render_template(
            "aksje_uten_kurser.html",
            aksje=post.aksje,
            hentet=None,
            aktiv="aksje",
            investorside=investorside(post.aksje.symbol),
        )
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
        dagen = bygg_dagen(rader, slutt, innhold, i_dag, post.ut)
    else:
        detalj = bygg_detalj(post, rader, i_dag, STANDARD, start=start, slutt=slutt)
        if valg.periode == SISTE:
            dagen = bygg_dagen(rader, slutt, oversiktsleser.vurdering(post.aksje.symbol, slutt), i_dag, post.ut)
    if detalj is None:
        abort(404)

    # Story 10.3: KI-teksten under regelforklaringen, bare naar det er en
    # vurdering aa forklare og bryteren er paa (FR-601, FR-602).
    ki_er_paa = _ki_er_paa()
    ki = _ki_visning(post, detalj, rader[-1].dato) if ki_er_paa and detalj.sjekker else None
    # Gruppens svar 25.10 kl. 00:51: setningen om dagene under KI-teksten,
    # ogsaa naar KI er av eller teksten er stoppet. «I dag» bare naar dagen
    # siden viser, er i dag (gjennomgangen, BH1, ECH6, VG1).
    # Gruppens svar 5.11 kl. 19:13 og 23:36: setningen om samme dag rett under
    # setningen om dagene, av det samme dagsbildet som grunnlaget til modellen.
    # Gjennomgangen av 8.8 (BH8, ECH8): vurderingene leses én gang for
    # setningen om dagene og dagene i grafen.
    vurderingene = _vurderingene(post, rader[-1].dato)
    dagene, samme_dag = _setningene_om_dagen(
        post, detalj, leser, oversiktsleser, annen_dag=detalj.dato != i_dag, vurderingene=vurderingene
    )
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

    # Story 8.2c: den brede og den smale grafen av de samme valgene
    # (gjennomgangen, BH6).
    signal, signal_fra = _signaldagene(rader, vurderingene)
    # Story 8.14 (FR-407): justeringsdagene det siste året til dagen siden
    # viser, regnet av kursserien alene. Grafen får alle dagene i serien og
    # merker dem den har (gjennomgangen, BH1).
    justeringer = justeringsdager(rader, til=slutt)
    grafvalg = dict(
        justeringer=justeringsdager(rader),
        indeks=indeks,
        merker=AKSEMERKER.get(valg.periode, MAANEDSNAVN),
        merket=dagen.dato if dagen else None,
        signal=signal,
        alle=ANTALL_SJEKKER,
        # Story 8.7: baandet for sjekk 2 og volumet for sjekk 3.
        volumfaktor=STANDARD.volumfaktor,
    )
    svar = app.make_response(
        render_template(
            "aksje.html",
            # Story 8.2b, b (U2): siden hører til Markedsoversikt i stripa.
            aktiv="aksje",
            detalj=detalj,
            graf=bygg_graf(detalj.punkter, **grafvalg),
            # Story 8.2c: den samme grafen med egne mål, som stilarket viser
            # i stedet når figuren er smal.
            graf_smal=bygg_graf(detalj.punkter, smal=True, **grafvalg),
            # Story 8.8: dagen markeringene starter.
            signal_fra=signal_fra,
            justeringer=justeringer,
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
            samme_dag=samme_dag,
            ki_til=AV if ki_er_paa else PAA,
            # Story 10.5: lenken til investorsiden for aksjen siden viser,
            # slaatt opp paa symbolet. Siden henter ingenting derfra (AD-2).
            investorside=investorside(post.aksje.symbol),
            # Story 2.7b: maaneden for dagen siden viser, eller den i adressen.
            historikk=historikk,
            # Story 8.23 (tillegg 2): 3 av 3 det siste året, av radene som er lagret.
            alle_sjekkene=alle_sjekkene_det_siste_aaret(vurderingene, rader[-1].dato, ANTALL_SJEKKER),
            pil=pil,
            # Story 8.21: «Mine notater», med dagen et nytt notat får.
            # Tillegget kl. 14:44: bryteren «Notater» skjuler delen, og
            # notatene leses da ikke.
            notatene=_notatene(post, rader, indeks, indeks_feilet, vurderingene, i_dag)
            if innstillinger.les(g.get("tilkobling"))[innstillinger.VIS_NOTATER]
            else None,
            notatdag=slutt,
            # Tillegget kl. 14:44: et tenkt kjøp eller salg noteres bare fra
            # siden for siste dag med kurser, med sjekkene slik de står der.
            kan_handle=post.ut is None
            and bool(rader)
            and slutt == rader[-1].dato
            and post.aksje.symbol not in _fjernes_i_kveld(),
            # Gjennomgangen av tilleggene (ECH1, BH3): siden sier hvorfor.
            fjernes_i_kveld=post.aksje.symbol in _fjernes_i_kveld(),
            # Gjennomgangen (ECH1): «Vis dagen» godtar en dag uten kurs for
            # aksjen, som en lørdag. Da står ikke skjemaet, bare en linje.
            kan_skrive_notat=post.ut is None,
            notatdag_har_kurs=any(rad.dato == slutt for rad in rader),
            notat_visningen=_visningen(valg, slutt, periode),
            notat_maks=MAKS_TEGN,
            notat_anker=NOTATANKER,
            **_fotnoten([detalj.dato] if detalj.ikke_vurdert else [], i_dag),
        )
    )
    # Siden avhenger av bryteren (gjennomgangen av 10.3, BH10).
    svar.vary.add("Cookie")
    return svar


# --- Story 8.21: «Mine notater» på aksjesiden ------------------------------

NOTATANKER = "mine-notater"
# Gjennomgangen (BH3, ECH3): en id med flere sifre enn SQLite tar (int64),
# gir 400, ikke OverflowError og 500.
_NOTAT_ID = re.compile(r"[0-9]{1,18}")
# Gjennomgangen (ECH2, BH7): visningen skjemaet kom fra, så svaret går tilbake
# til samme periode eller dag. Bare en dag eller en periode siden kjenner.
_VISNINGEN = re.compile(r"dag=([0-9]{4}-[0-9]{2}-[0-9]{2})|periode=([a-z0-9-]+)")
# Story 8.24 (gruppens svar 10.11 kl. 22:59): fra «Mine notater» i Min liste,
# med eller uten «Alle». Bare disse to, så adressen aldri kommer fra skjemaet.
MIN_LISTE_TILBAKE = {"min-liste": "/min-liste", "min-liste-alle": "/min-liste?vis=alle"}


def _notatene(
    post, rader, indeks: dict | None, indeks_feilet: bool, vurderingene: dict | None, i_dag: date
) -> list | None:
    """Notatene for aksjen, hvert med «Etterpå» (etterpaa.py), den nyeste
    notatdagen først. Serien, indeksen og vurderingene er de siden alt har
    lest, hele serien til siste dag, også med «Vis dagen» og en periode, så
    ingenting leses to ganger, og signalet regnes aldri (AD-7). None når
    notatene ikke kan leses; da står delen uten skjema."""
    try:
        lager = SqliteNotatlager(g.tilkobling)
        notatene = lager.notater(post.aksje.symbol)
        kjoepene = lager.kjoepene()
    except (*BASEFEIL, ValueError) as feil:
        app.logger.warning("Notatene kunne ikke leses: %s", type(feil).__name__)
        return None
    # Tillegget kl. 14:44: høyst ett åpent tenkt kjøp per aksje.
    return [
        _Notatet(
            notat,
            bygg_etterpaa(
                notat, rader, indeks, vurderingene, i_dag, STANDARD.terskel, post.ut, indeks_feilet=indeks_feilet
            ),
            bygg_handelen(kjoepene[notat.id], rader, indeks, indeks_feilet=indeks_feilet)
            if notat.id in kjoepene
            else None,
            kan_kjoepe=_kan_kjoepe(notat, kjoepene, post),
            aksje=post.aksje,
        )
        for notat in notatene
    ]


def _kan_kjoepe(notat, kjoepene: dict, post) -> bool:
    """Regelen for «Noter et tenkt kjøp», lik på aksjesiden og i Min liste
    (story 8.24, gjennomgangen BH2): notatet har ikke et kjøp, aksjen har ikke
    et åpent kjøp, og aksjen står i lista. Om siden kan notere i det hele
    tatt (siste dag, ikke fjernet i kveld), avgjøres for siden."""
    aapent = any(k.aapent and k.symbol == notat.symbol for k in kjoepene.values())
    return notat.id not in kjoepene and not aapent and post.ut is None


@dataclass(frozen=True)
class _Notatet:
    """Et notat slik malen _notat.html viser det: «Etterpå», det tenkte
    kjøpet, om et kjøp kan noteres ved det, og aksjen, for Min liste."""

    notat: object
    etter: object
    handelen: object
    kan_kjoepe: bool
    aksje: object
    # Story 8.24 (gruppens svar 10.11 kl. 22:59): Min liste har de samme
    # knappene som aksjesiden, så hvert notat bærer siste dag med kurser for
    # aksjen, om et kjøp eller salg kan noteres, og om aksjen fjernes i kveld.
    siste_dag: date | None = None
    kan_handle: bool = False
    # Gjennomgangen av 8.24 (ECH3, ECH5): hvorfor knappene for kjøp og salg
    # mangler, én gang per aksje, ved det nyeste notatet.
    merknad: str | None = None


def _alle_notatene(tidligere_dag: bool = False) -> list | None:
    """Alle notatene i basen, for «Mine notater» nederst i Min liste, den
    nyeste notatdagen først, hvert med «Etterpå» og det tenkte kjøpet, som på
    aksjesiden. Serien og vurderingene leses én gang per aksje med notater.
    None når bryteren «Notater» er av, eller notatene ikke kan leses."""
    tilkobling = g.get("tilkobling")
    if tilkobling is None or not innstillinger.les(tilkobling)[innstillinger.VIS_NOTATER]:
        return None
    try:
        lager = SqliteNotatlager(tilkobling)
        notatene = lager.alle_notater()
        kjoepene = lager.kjoepene()
        if not notatene:
            return []
        _symbol, indeks, indeks_feilet = _indeksen_for_grafen()
        oversiktsleser = SqliteOversiktsleser(tilkobling)
        kursleser = SqliteKurslager(tilkobling)
        i_dag = idag()
        fjernes = _fjernes_i_kveld()
        per_aksje = {}
        for symbol in {n.symbol for n in notatene}:
            post = oversiktsleser.post(symbol)
            if post is None:
                continue
            rader = kursleser.serie(symbol)
            vurderingene = _vurderingene(post, rader[-1].dato) if rader else None
            per_aksje[symbol] = (post, rader, vurderingene)
    except (*BASEFEIL, ValueError) as feil:
        app.logger.warning("Notatene kunne ikke leses: %s", type(feil).__name__)
        return None
    # Story 8.24: de samme reglene som på aksjesiden. Høyst ett åpent kjøp per
    # aksje, bare for en aksje i lista som ikke fjernes i kveld, og bare med
    # sjekkene for siste dag med kurser. Gjennomgangen (ECH1): viser Min liste
    # en tidligere dag, står ingen knapper for kjøp og salg, som på aksjesiden.
    ut = []
    sett = set()
    for notat in notatene:
        if notat.symbol not in per_aksje:
            continue
        post, rader, vurderingene = per_aksje[notat.symbol]
        kan_handle = post.ut is None and bool(rader) and notat.symbol not in fjernes and not tidligere_dag
        merknad = None
        if notat.symbol not in sett:
            sett.add(notat.symbol)
            if notat.symbol in fjernes:
                merknad = f"{post.aksje.navn} fjernes fra lista ved hentingen i kveld og får ingen nye kurser, så et tenkt kjøp eller salg kan ikke noteres."
            elif post.ut is not None:
                merknad = f"{post.aksje.navn} er tatt ut av lista, så et tenkt kjøp eller salg kan ikke noteres."
            elif not rader:
                merknad = f"{post.aksje.navn} har ingen kurser ennå, så et tenkt kjøp eller salg kan ikke noteres."
        ut.append(
            _Notatet(
                notat,
                bygg_etterpaa(
                    notat, rader, indeks, vurderingene, i_dag, STANDARD.terskel, post.ut, indeks_feilet=indeks_feilet
                ),
                bygg_handelen(kjoepene[notat.id], rader, indeks, indeks_feilet=indeks_feilet)
                if notat.id in kjoepene
                else None,
                kan_kjoepe=_kan_kjoepe(notat, kjoepene, post),
                aksje=post.aksje,
                siste_dag=rader[-1].dato if rader else None,
                kan_handle=kan_handle,
                merknad=merknad,
            )
        )
    return ut


def _visningen(valg: Valg, slutt: date, periode: str | None) -> str:
    """Visningen siden har, som skjemaene sender med: dagen fra «Vis dagen»,
    en periode fra adressen, eller ingenting for standardvisningen."""
    if valg.periode == VELG:
        return f"dag={slutt.isoformat()}"
    return f"periode={periode}" if periode else ""


def _tilbake_til_notatene(symbol: str, visningen: str | None) -> str:
    """Samme side, med samme periode eller dag, ved «Mine notater» (del B).
    En visning siden ikke kjenner, gir standardvisningen."""
    # Story 8.24: skjemaene i Min liste sender tilbake dit, til «Mine notater».
    if visningen in MIN_LISTE_TILBAKE:
        return MIN_LISTE_TILBAKE[visningen] + f"#{NOTATANKER}"
    adresse_ = f"/aksje/{symbol}"
    treff = _VISNINGEN.fullmatch(visningen or "")
    if treff and treff.group(1) and _gyldig_dato(treff.group(1)):
        adresse_ += f"?dag={treff.group(1)}"
    elif treff and treff.group(2) in PERIODENE and treff.group(2) != VELG:
        adresse_ += f"?periode={treff.group(2)}"
    return adresse_ + f"#{NOTATANKER}"


def _notatsiden(symbol: str):
    """Aksjen og kursdagene for skjemaene, eller abort. Symbolet slås opp i
    aksje i basen, som aksjesiden (404 for et symbol utenfor lista)."""
    _samme_side()
    if g.get("basefeil"):
        return None, None, _basen_kan_ikke_aapnes()
    if g.get("tilkobling") is None:
        abort(404)
    try:
        post = SqliteOversiktsleser(g.tilkobling).post(normaliser_symbol(symbol))
        rader = SqliteKurslager(g.tilkobling).serie(post.aksje.symbol) if post else []
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)
        return None, None, _basen_kan_ikke_aapnes()
    if post is None:
        abort(404)
    return post, [rad.dato for rad in rader], None


def _skjemadag(verdi: str | None, kursdager: list[date]) -> date:
    """Dagen fra skjemaet, som må være en dag aksjen har kurs (del B). 400
    ellers, så et notat aldri får en dag siden ikke kunne vise."""
    if not verdi or not _DAG.fullmatch(verdi) or not _gyldig_dato(verdi):
        abort(400)
    dag = date.fromisoformat(verdi)
    if dag not in kursdager:
        abort(400)
    return dag


@app.post("/aksje/<symbol>/notat")
def skriv_notat(symbol: str):
    """Lagrer et notat med dagen siden viste (spørsmål 3), og sender tilbake
    til samme side og dag (303). Webserveren skriver bare tabellen notat her
    (AD-3), og henter aldri noe (AD-10)."""
    post, kursdager, feilside = _notatsiden(symbol)
    if feilside is not None:
        return feilside
    dag = _skjemadag(request.form.get("dag"), kursdager)
    try:
        SqliteNotatlager(g.tilkobling).skriv(post.aksje.symbol, dag, request.form.get("tekst", ""), naa())
    except UgyldigNotat:
        abort(400)
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)
        return _basen_kan_ikke_aapnes()
    return redirect(_tilbake_til_notatene(post.aksje.symbol, request.form.get("vis")), code=303)


@app.post("/aksje/<symbol>/notat/slett")
def slett_notat(symbol: str):
    """Sletter ett notat for aksjen (spørsmål 7), og sender tilbake til samme
    side og dag (303). Et notat for en annen aksje slettes ikke."""
    post, _kursdager, feilside = _notatsiden(symbol)
    if feilside is not None:
        return feilside
    notat_id = request.form.get("id", "")
    if not _NOTAT_ID.fullmatch(notat_id):
        abort(400)
    try:
        SqliteNotatlager(g.tilkobling).slett(post.aksje.symbol, int(notat_id))
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)
        return _basen_kan_ikke_aapnes()
    return redirect(_tilbake_til_notatene(post.aksje.symbol, request.form.get("vis")), code=303)


def _sjekkene_paa_siden(post, dag: date):
    """Sjekkene som er lagret for dagen siden viste, (trend, bevegelse,
    interesse), eller None når dagen ikke var vurdert. Lest, aldri regnet
    (AD-7)."""
    innhold = SqliteVurderingslager(g.tilkobling, naa, (post.aksje,)).les_periode(post.aksje.symbol, dag, dag).get(dag)
    if isinstance(innhold, Vurdering):
        return (innhold.trend, innhold.bevegelse, innhold.interesse)
    return None


def _sluttkursen_etter(kursdager: list[date], i_dag: date) -> date:
    """Dagen sluttkursen for et tenkt kjøp eller salg må være etter: den
    siste dagen med kurs da brukeren trykket, eller børsdagen før i dag om
    den er senere. Kursen er da den første appen henter etter trykket
    (tillegget kl. 14:44, spørsmål 15)."""
    try:
        foer = forrige_boersdag(i_dag)
    except UtenforKalenderen:
        foer = None
    siste = kursdager[-1] if kursdager else None
    kandidater = [d for d in (siste, foer) if d is not None]
    if not kandidater:
        abort(400)
    return max(kandidater)


def _handelen(symbol: str, salg: bool):
    post, kursdager, feilside = _notatsiden(symbol)
    if feilside is not None:
        return feilside
    notat_id = request.form.get("id", "")
    if not _NOTAT_ID.fullmatch(notat_id):
        abort(400)
    # Bare fra siden for siste dag med kurser, så sjekkene er de siden viste.
    dag = _skjemadag(request.form.get("dag"), kursdager)
    if dag != kursdager[-1]:
        abort(400)
    # Gjennomgangen av tilleggene (ECH1, BH3): en aksje med et ønske om å
    # fjernes tas ut før kursene hentes i kveld, så et kjøp eller salg
    # ville aldri fått sluttkursen.
    if post.aksje.symbol in _fjernes_i_kveld():
        abort(400)
    try:
        lager = SqliteNotatlager(g.tilkobling)
        sjekkene = _sjekkene_paa_siden(post, dag)
        etter = _sluttkursen_etter(kursdager, idag())
        kjoep = lager.kjoepene().get(int(notat_id))
        if salg:
            # Gjennomgangen (ECH3): et salg som alt er notert (dobbeltklikk),
            # sender tilbake uten å skrive noe.
            if kjoep is not None and kjoep.solgt is not None:
                return redirect(_tilbake_til_notatene(post.aksje.symbol, request.form.get("vis")), code=303)
            # Salget først når kjøpet har fått sluttkursen (spørsmål 16).
            if kjoep is None or not any(d > kjoep.kjoep_etter for d in kursdager):
                abort(400)
            lager.noter_salg(post.aksje.symbol, int(notat_id), naa(), etter, sjekkene)
        elif kjoep is None:
            # Et kjøp som alt er notert ved notatet (dobbeltklikk), skrives
            # ikke på nytt.
            lager.noter_kjoep(post.aksje.symbol, int(notat_id), naa(), etter, sjekkene)
    except UgyldigNotat:
        abort(400)
    except BASEFEIL as feil:
        g.basefeil = _basefeil(feil)
        return _basen_kan_ikke_aapnes()
    return redirect(_tilbake_til_notatene(post.aksje.symbol, request.form.get("vis")), code=303)


@app.post("/aksje/<symbol>/notat/kjoep")
def noter_tenkt_kjoep(symbol: str):
    """«Noter et tenkt kjøp» ved et notat (tillegget 10.11 kl. 14:44). Lagrer
    tidspunktet, sjekkene slik de sto på siden, og dagen sluttkursen må være
    etter. Bare tabellen tenkt_kjoep skrives (AD-3), og ingenting hentes
    (AD-10)."""
    return _handelen(symbol, salg=False)


@app.post("/aksje/<symbol>/notat/salg")
def noter_tenkt_salg(symbol: str):
    """«Noter et tenkt salg» ved et notat med et åpent tenkt kjøp som har
    fått sluttkursen. Som kjøpet."""
    return _handelen(symbol, salg=True)


def _gyldig_dato(verdi: str) -> bool:
    try:
        date.fromisoformat(verdi)
    except ValueError:
        return False
    return True


# Story 8.26 (gruppens svar 11.11 kl. 20:28, tillegg 12): registreringen hos
# EODHD, samme adresse som startskriptet åpner (start.ps1 og start.sh).
EODHD_REGISTRERING = "https://eodhd.com/register"
app.jinja_env.globals["eodhd_registrering"] = EODHD_REGISTRERING


@app.route("/eodhd-demo")
def eodhd_demo():
    """Story 8.26 (tillegg 12): siden «Åpne eodhd.com» i steg 1 går til i
    demoen, i samme oppsett som investorsidene. Bare i demoen: den ekte
    versjonen lenker til registreringen hos EODHD, og ruta svarer 404."""
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler") or not g.get("eksempeltall"):
        abort(404)
    return render_template("eodhd_demo.html", side=eodhd_demoside(), aktiv="min_liste")


@app.route("/investorside/<symbol>")
def demoselskap(symbol: str):
    """Story 3.4h: siden for et av de 15 oppdiktede selskapene, med logoen,
    tegningen laget av KI og boblen. Bare i demoen (spørsmål 1): i den ekte
    versjonen går boblen på aksjesiden til selskapets egen side, og ruta
    svarer 404. Et symbol utenfor de 15 gir 404."""
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    if g.get("demo_mangler") or not g.get("eksempeltall"):
        abort(404)
    side = demoside(normaliser_symbol(symbol))
    if side is None:
        abort(404)
    # Spørsmål 9: stripa som på aksjesiden, uten en fylt knapp.
    return render_template("investorside.html", side=side, aktiv="aksje")


def _vurderingene(post, til: date) -> dict | None:
    """Gjennomgangen av 8.8 (BH8, ECH8): radene i vurdering for aksjen til og
    med den siste dagen i grafen, lest én gang per side med les_periode fra
    2.7 (AD-3), aldri regnet (AD-7). None når de ikke kan leses."""
    try:
        return SqliteVurderingslager(g.tilkobling, naa, (post.aksje,)).les_periode(post.aksje.symbol, date.min, til)
    except (*BASEFEIL, ValueError) as feil:
        app.logger.warning("Vurderingene kunne ikke leses: %s: %s", type(feil).__name__, feil)
        return None


def _signaldagene(rader, radene: dict | None) -> tuple[dict[date, tuple[int, str]], date | None]:
    """Story 8.8 (FR-206): dagene aksjen skilte seg ut, {dato: (styrke,
    retning)}, og dagen den første raden i vurdering er fra, med vurdering
    eller grunn. Lest med les_periode fra 2.7, aldri regnet av kursene
    (AD-7). En dag med grunn eller uten rad er ikke med. Kan vurderingene
    ikke leses, er det ingen markeringer, og grafen vises som før."""
    if not rader or not radene:
        return {}, None
    signal = {
        dag: (rad.styrke, rad.retning)
        for dag, rad in radene.items()
        if isinstance(rad, Vurdering) and rad.styrke >= STANDARD.terskel
    }
    return signal, min(radene)


def _historikken(post, rader, dagen: date, i_dag: date) -> Maaned:
    """Story 2.7b: maaneden i historikken, lest gjennom Vurderingslager i en
    spoerring (AD-3). Lista er aksjen siden viser, fra aksje i basen, saa
    ogsaa demoselskapene kan leses. Signalet regnes aldri (AD-7)."""
    maaned, beskjed = les_maaned(request.args.get(PARAMETER), dagen, rader[0].dato, rader[-1].dato)
    lager = SqliteVurderingslager(g.tilkobling, naa, (post.aksje,))
    radene = lager.les_periode(post.aksje.symbol, *perioden(maaned))
    return bygg_maaned(maaned, [rad.dato for rad in rader], radene, i_dag, STANDARD.terskel, beskjed, ut=post.ut)


def _setningene_om_dagen(
    post, detalj, leser, oversiktsleser, annen_dag: bool, vurderingene: dict | None
) -> tuple[str | None, str | None]:
    """Gruppens svar 25.10 kl. 00:51: hvor lenge signalet har vaert slik, med
    tellingen fra svaret 24.10 kl. 16:15 a), lest fra vurdering (AD-3, AD-10).
    None uten en vurdering for dagen, eller naar basen ikke kan leses, ogsaa
    en base fra foer siste migrasjon, som i _ki_visning (gjennomgangen, BH7,
    ECH11).

    Story 10.2i, gruppens svar 5.11 kl. 19:13 og 23:36: ogsaa setningen om
    hva hovedindeksen, bransjen og antallene gjorde samme dag, regnet av
    lag_dagsbilde i dagene.py med lista, kursene og indeksen fra basen, som
    grunnlaget i ki_tekst.py. Kan indeksen ikke leses, staar setningen uten
    den, som i grunnlaget. Gir (dagene, samme_dag)."""
    if not detalj.vurdering or vurderingene is None:
        return None, None
    # Gjennomgangen av 8.8 (BH8, ECH8): vurderingene er lest én gang i
    # aksjedetalj, til siste dag i grafen. Her bare til og med dagen siden viser.
    tidligere = {dag: rad for dag, rad in vurderingene.items() if dag <= detalj.dato}
    try:
        indekser = SqliteIndekslager(g.tilkobling)
        symboler = indekser.symboler()
        indeksserie = indekser.serie(valgt_indeks(symboler)) if symboler else None
    except (sqlite3.Error, ValueError, RuntimeError):
        indeksserie = None
    try:
        # Story 2.11 (gjennomgangen, ECH5): lista den dagen, som grunnlaget.
        lista = tuple(p.aksje for p in oversiktsleser.oversikt(detalj.dato))
        serier = {aksje.symbol: leser.serie(aksje.symbol) for aksje in lista}
    except (sqlite3.Error, ValueError, RuntimeError) as feil:
        app.logger.warning("Dagen kunne ikke leses: %s: %s", type(feil).__name__, feil)
        lista, serier = None, None
    dager, minst = tell_dagene(detalj.dato, detalj.vurdering, tidligere)
    # Story 10.9, del A: med datoen for den foerste dagen i rekka. tell_dagene
    # har alt gaatt de samme dagene bakover, saa kalenderen dekker dem.
    fra = foerste_dag_i_rekka(detalj.dato, dager)
    dagene = setning_om_dagene(dager, minst, annen_dag=annen_dag, fra=fra, i_aar=idag().year)
    if lista is None:
        return dagene, None
    # Gjennomgangen (BH9, BH10, ECH12): en feil i utregningen av dagen, som en
    # dag utenfor kalenderen eller en kurs paa 0, gir siden uten setningen om
    # samme dag, ikke 500.
    try:
        bildet = lag_dagsbilde(post.aksje, detalj.dato, detalj.vurdering, tidligere, lista, serier, indeksserie)
        # Story 8.23 (tillegg 2): med antallet i lista den dagen.
        return dagene, setning_om_samme_dag(bildet, len(lista))
    except (UtenforKalenderen, ValueError, ArithmeticError) as feil:
        app.logger.warning("Dagen kunne ikke regnes: %s: %s", type(feil).__name__, feil)
        return dagene, None


def _ki_visning(post, detalj, siste: date) -> KIVisning:
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
    visning = bygg_ki_visning(rad, detalj.vurdering, andre_har_rader=andre_har_rader)
    # Story 8.2b, b (U6): i demoen er grunnen at demoen bare har KI-tekst for
    # siste boersdag. Den ekte versjonen har teksten som foer. Gjennomgangen
    # av 8.2b (BH3, ECH3): bare for en dag foer siste dag i serien, saa en
    # demobase uten KI-tekstene ikke sier det om siste dag.
    if visning.tilstand == INGEN_RAD and g.get("eksempeltall") and detalj.dato < siste:
        return KIVisning(INGEN_I_DEMOEN)
    return visning


def _boersdagen(
    poster: list,
    serier: dict[str, list],
    valg: Valg | None,
    siste: date | None,
    oversiktsleser,
    ledd,
    sortering: Sortering | None = None,
):
    """«Børsdagen kort fortalt» - story 10.6, FR-607, FR-601.

    Teksten er raden i KI-loggen for dagen tabellen viser, og vises bare naar
    grunnlaget i raden er det samme som grunnlaget regnet her av det siden
    viser: vurderingene som er lagret, kursene og hovedindeksen, for aksjene
    i lista (dagsgrunnlag.py). Webserveren leser bare (AD-10). En periode har
    ingen tekst (spoersmaal 1), og med KI av staar bare linja om det.
    Gjennomgangen av 10.6 (BH7, ECH11): bryteren tar med sorteringen
    tilbake, som perioden og dagen.
    Story 8.10b (BH3, ECH3): paa eller av leses med _ki_er_paa(), som paa
    aksjesiden, saa valget i Innstillinger gjelder begge."""
    er_paa = _ki_er_paa()
    bryter = {
        "er_paa": er_paa,
        "til": AV if er_paa else PAA,
        "tilbake": side_adresse(OVERSIKTEN, sortering, False, ledd, request.args.get("vis") == BARE_MIN),
    }
    if not er_paa:
        return {**bryter, "uten": DAGEN_AV}
    if valg is not None and valg.periode not in (SISTE, VELG):
        return {**bryter, "uten": PERIODEN_UTEN}
    dag = valg.dag if valg is not None and valg.periode == VELG else siste
    if dag is None:
        return {**bryter, "uten": DAGEN_UTEN}
    try:
        rad = SqliteKILogg(g.tilkobling, naa).les(Emne.dagen(dag))
        if rad is None:
            return {**bryter, "uten": DAGEN_UTEN}
        lager = SqliteIndekslager(g.tilkobling)
        symboler = lager.symboler()
        indeksserie = lager.serie(valgt_indeks(symboler)) if symboler else None
        lista = tuple(post.aksje for post in poster)
        vurderinger = {a.symbol: oversiktsleser.vurdering(a.symbol, dag) for a in lista}
        # Story 10.10 (tillegget kl. 17:21): vurderingene foer dagen, lest som i hentingen.
        lageret = SqliteVurderingslager(g.tilkobling, naa, lista)
        tidligere = {a.symbol: lageret.les_periode(a.symbol, vanlig_fra(dag), dag) for a in lista}
        grunnlag = dagsgrunnlag(dag, lista, vurderinger, serier, indeksserie, tidligere=tidligere)
    except (RuntimeError, sqlite3.Error, UgyldigKIRad, ValueError) as feil:
        app.logger.warning("Teksten om dagen kunne ikke leses: %s: %s", type(feil).__name__, feil)
        return {**bryter, "uten": DAGEN_UTEN}
    visning = bygg_dagsvisning(rad, grunnlag)
    if not visning.vist:
        return {**bryter, "uten": DAGEN_UTEN}
    # Story 10.10, spoersmaal 10: Min liste er en linje appen skriver under
    # teksten, av lista slik den er naa, saa den aldri blir feil og teksten
    # ikke forsvinner naar lista endres (FR-607).
    try:
        merkede = SqliteMinlistelager(g.tilkobling).merkede()
    except (RuntimeError, sqlite3.Error, ValueError):
        merkede = set()
    min_liste = min_liste_linje(lista, vurderinger, merkede)
    return {**bryter, "tekst": visning.tekst, "modell": visning.modell, "min_liste": min_liste}


# Bare aksjesiden kan vaere maalet for bryteren. Alt annet gaar til /, ogsaa
# en adresse med tabulator eller linjeskift, som nettleseren ellers ville
# lest som en annen side (gjennomgangen, BH1, ECH).
# Story 8.16b: med en valgt dag ogsaa ?dag= og en dato. Datoen leses paa nytt
# av les_valg, saa en dag som ikke kan vises, gir 6 mnd og en beskjed.
_TILBAKE = re.compile(r"/aksje/[A-Za-z0-9.\-]{1,20}(\?dag=[0-9]{4}-[0-9]{2}-[0-9]{2})?")
# Story 10.6: ogsaa oversikten, med perioden eller dagen (periodeledd), til
# «Børsdagen kort fortalt».
# Gjennomgangen av 10.6 (BH7, ECH11): ogsaa sorteringen, sorter= og orden=.
_TILBAKE_OVERSIKTEN = re.compile(
    r"/(\?(periode=[a-z0-9\-]{1,10}(&dag=[0-9]{4}-[0-9]{2}-[0-9]{2})?(&sorter=[a-z_]{1,20}&orden=[a-z]{1,10})?"
    r"|sorter=[a-z_]{1,20}&orden=[a-z]{1,10}))?"
)
BOERSDAGEN_ANKER = "boersdagen-kort-fortalt"
# Story 8.2a, a (U35, U36, gruppens svar 24.10 kl. 11:21): knappene som
# endrer noe paa aksjesiden, holder plassen, som pilene i historikken.
# Periodeknappene og «Velg dag» gaar til kursgrafen, og bryteren til
# KI-teksten.
GRAFANKER = "kursgrafen"
# Story 8.26 (gruppens ønske 11.11 kl. 19:36, tillegg 6): periodevalget på
# oversikten, i Min liste og på børsometeret holder plassen på samme måte.
PERIODEANKER = "perioden"
INNSTILLINGSANKER = {
    innstillinger.VIS_HJELP: "hjelp-valget",
    innstillinger.VIS_KI_TEKST: "ki-valget",
    innstillinger.VIS_NOTATER: "notater-valget",
}
app.jinja_env.globals["periodeanker"] = PERIODEANKER
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
    # Story 8.10b (FR-110, FR-601): valget i basen, som Innstillinger viser,
    # så de to aldri viser hver sin verdi. Kapselen skrives fortsatt.
    # Gjennomgangen (BH1, ECH1, ECH2): kan valget ikke skrives i basen,
    # settes heller ikke kapselen, og siden sier at basen ikke kan brukes, så
    # bryteren og Innstillinger aldri viser hver sin verdi.
    if g.get("basefeil") or not _lagre_ki(til):
        return _basen_kan_ikke_aapnes()
    tilbake = request.form.get("tilbake", "/")
    # Gjennomgangen av 10.6 (ECH12): uten tilbake gaar bryteren til / som foer.
    if "tilbake" not in request.form:
        tilbake = ""
    if _TILBAKE.fullmatch(tilbake):
        tilbake += f"#{KI_ANKER}"
    elif _TILBAKE_OVERSIKTEN.fullmatch(tilbake):
        # Gjennomgangen av 10.6 (BH7, ECH11): ogsaa sorteringen. Adressen
        # bygges paa nytt av det som er kjent, som etter merkingen.
        tilbake = tilbake_etter_merking(tilbake) + f"#{BOERSDAGEN_ANKER}"
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
# Story 8.23 (tillegg 2, gruppens svar kl. 14:53 og 14:59): «Min liste» over
# «Aksjene» filtrerer tabellen på oversikten, med ?vis=min.
BARE_MIN = "min"
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
        deler.path == OVERSIKTEN and _ett(valg, "vis") == BARE_MIN,
    )


_DAG_I_ADRESSEN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _periodeledd_fra(sti: str, periode: str | None, dag: str | None) -> tuple[str, ...]:
    """Story 8.17a: perioden og dagen merkingen sender tilbake til, bare
    kjente koder. Siden leser dem på nytt. Story 8.17b: også Min liste."""
    if sti not in (OVERSIKTEN, MIN_LISTE) or periode not in PERIODENE or periode == SISTE:
        return ()
    if periode == VELG:
        return (f"periode={VELG}", f"dag={dag}") if dag and _DAG_I_ADRESSEN.fullmatch(dag) else ()
    return (f"periode={periode}",)


def _ett(valg: dict[str, list[str]], navn: str) -> str | None:
    verdier = valg.get(navn, [])
    return verdier[0] if len(verdier) == 1 else None


def side_adresse(
    sti: str, sortering: Sortering | None, alle: bool = False, periode: tuple[str, ...] = (), bare_min: bool = False
) -> str:
    """Adressen til oversikten eller Min liste, med «Alle», perioden og
    dagen (story 8.17a) og sorteringen. Story 8.23: med «Min liste» på
    oversikten (bare_min)."""
    valg = []
    if alle:
        valg.append(f"vis={ALLE}")
    if bare_min and sti == OVERSIKTEN:
        valg.append(f"vis={BARE_MIN}")
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
    adresse = tilbake_etter_merking(request.form.get("tilbake"))
    # Story 8.2b, a (U29): tas aksjen ut av Min liste uten «Alle», er raden
    # borte, saa siden sender tilbake til tabellen.
    deler = urlsplit(adresse)
    vis = _ett(parse_qs(deler.query), "vis")
    # Story 8.23: også oversikten med «Min liste», der raden forsvinner.
    borte = til == FJERN and (
        (deler.path == MIN_LISTE and vis != ALLE) or (deler.path == OVERSIKTEN and vis == BARE_MIN)
    )
    return redirect(adresse + ("#aksjene" if borte else f"#rad-{symbol}"), code=303)


# --- Story 2.12: velge og bytte aksjer -------------------------------------


def _valglager() -> valg.Valglager | None:
    """Valglageret for basen siden leser, eller None naar basen ikke har
    tabellene fra 0010 ennaa (en base en versjon bak). Bare lesing her."""
    tilkobling = g.get("tilkobling")
    if tilkobling is None or not valg.har_tabellene(tilkobling):
        return None
    return valg.Valglager(tilkobling, naa)


def _omsetningen(lager: valg.Valglager, medianene: dict, symbol: str) -> tuple[float | None, date | None, bool]:
    """Story 8.11c (spørsmål 9 i 8.11b): medianen for merket «Utenfor
    målingen», den samme som i de ferdige listene. For en aksje som regnes av
    kursene, er det medianen av kursene til den siste dagen med kurser;
    ellers den siste målingen i omsetning (2.13), som før. Gir (median i NOK
    eller None, dagen, regnet av kursene)."""
    if symbol in medianene:
        median, dag = medianene[symbol]
        return median, dag, True
    median, maalt = lager.omsetning(symbol)
    return median, maalt, False


def _medianene() -> dict:
    """Story 8.11c: medianene av kursene, regnet én gang per forespørsel
    (gjennomgangen, BH4, ECH2)."""
    if "medianene" not in g:
        g.medianene = ferdige_lister.medianene(g.get("tilkobling"))
    return g.medianene


def _egne() -> dict | None:
    """«Dine egne aksjer» og «Din egen liste», regnet én gang per forespørsel.
    Gjennomgangen av 8.11c (BH4, ECH2): siden og context processoren brukte
    hver sin utregning, med de ferdige listene og medianene to ganger."""
    if "egne" not in g:
        g.egne = _egne_regnet()
    return g.egne


def _egne_regnet() -> dict | None:
    """«Dine egne aksjer» og «Din egen liste» - story 2.12 (utdraget 08.11
    §1 og §2). Bare lesing (AD-10): aksjene i lista, ønskene som venter, og
    omsetningen fra 2.13."""
    lager = _valglager()
    if lager is None:
        return None
    try:
        lista = lager.i_lista()
        ventende = lager.ventende()
        egne = lager.egne()
        fjernes = {o.symbol: o.id for o in ventende if o.handling == valg.FJERN}
        medianene = _medianene()
        rader = []
        for aksje in lista:
            if aksje.symbol in egne:
                omsetningen = _omsetningen(lager, medianene, aksje.symbol)
                rader.append(
                    {
                        "symbol": aksje.symbol,
                        "navn": aksje.navn,
                        # Story 8.22 (spørsmål 3): den faste bransjen med en gang.
                        "sektor": ferdige_lister.fast_bransje(aksje.symbol) or aksje.sektor,
                        "status": "fjernes" if aksje.symbol in fjernes else "hentet",
                        "oenske": fjernes.get(aksje.symbol),
                        "utenfor": valg.utenfor_maalingen(omsetningen[0]),
                        "omsetningen": omsetningen,
                    }
                )
        for o in ventende:
            if o.handling == valg.FOLG:
                omsetningen = _omsetningen(lager, medianene, o.symbol)
                rader.append(
                    {
                        "symbol": o.symbol,
                        "navn": o.navn,
                        "sektor": ferdige_lister.fast_bransje(o.symbol) or o.sektor,
                        "status": "venter",
                        "oenske": o.id,
                        "utenfor": valg.utenfor_maalingen(omsetningen[0]),
                        "omsetningen": omsetningen,
                    }
                )
        folg = sum(o.handling == valg.FOLG for o in ventende)
        antall = len(lista) + folg - len(fjernes)
        sist, neste, igjen = valg.kallene(len(lista), folg, len(fjernes))
        # Gjennomgangen (VG4): neste henting med én aksje til, regnet her og
        # ikke i malen.
        _, med_en, igjen_med_en = valg.kallene(len(lista), folg + 1, len(fjernes))
        utenfor_tekst = {}
        for rad in rader:
            if rad["utenfor"]:
                # Gjennomgangen (BH6): omsetningen fra raden, ikke lest på nytt.
                median, maalt, kursene = rad["omsetningen"]
                utenfor_tekst[rad["symbol"]] = valg.utenfor_tekst(median, maalt, kursene=kursene)
        egne_i_lista = len(egne)
        # Story 8.11: de ferdige listene, med merket for omsetningen.
        ferdige = ferdige_lister.lister(g.tilkobling)
        # Story 8.26 (tillegg 14): aksjene appen følger, samlet etter bransje i
        # rekkefølgen på børsometeret; en ukjent bransje sist.
        rang = {b: i for i, b in enumerate(BRANSJER)}
        grupper: dict[str, list] = {}
        for aksje in lista:
            bransje = ferdige_lister.fast_bransje(aksje.symbol) or aksje.sektor or "Uten bransje"
            grupper.setdefault(bransje, []).append(aksje)
        return {
            "grupper": sorted(grupper.items(), key=lambda par: (rang.get(par[0], len(rang)), par[0])),
            "egne_symboler": frozenset(egne),
            "ferdige": ferdige,
            "ferdige_utenfor": frozenset(
                a.symbol for liste in ferdige.values() for a in liste if valg.utenfor_maalingen(a.median)
            ),
            "rader": rader,
            "symboler": frozenset(r["symbol"] for r in rader if r["status"] != "venter"),
            "utenfor": frozenset(r["symbol"] for r in rader if r["utenfor"]),
            "utenfor_tekst": utenfor_tekst,
            "antall_egne": sum(r["status"] != "fjernes" for r in rader),
            "antall": antall,
            "tak": valg.TAK,
            "full": antall >= valg.TAK,
            "lista": lista,
            "fjernes": fjernes,
            # Story 8.23 (tillegg 2): alle endringene som venter på hentingen,
            # også å fjerne en av de faste og en ferdig liste, til meldingen øverst.
            "ventende": len(ventende),
            "kall": {
                "faste": len(lista) - egne_i_lista,
                "egne": egne_i_lista,
                "indeks": valg.INDEKSKALL,
                "margin": valg.KVOTE - len(lista) - valg.INDEKSKALL,
                "sist": sist,
                "neste": neste,
                "igjen": igjen,
                "med_en": med_en,
                "igjen_med_en": igjen_med_en,
                # Tillegg 4 (gjennomgangen, BH3): kvoten i steg 2. Story 8.23 (A7): tallene i
                # «Følg flere aksjer» regnes av kvoten, taket og lista, ikke skrevet for hånd.
                "kvote": valg.KVOTE,
                "per_aksje": valg.KALL_PER_AKSJE,
                "igjen_med_taket": valg.KVOTE - valg.TAK * valg.KALL_PER_AKSJE - valg.INDEKSKALL,
            },
            # Story 8.22, tillegg 4 (svaret kl. 22:50): status for nøkkelen i
            # steg 2, regnet av siste henting, uten kall og uten .env (AD-10).
            "henting": valg.siste_henting(g.tilkobling),
        }
    except (*BASEFEIL, ValueError) as feil:
        app.logger.warning("Valget kunne ikke leses: %s: %s", type(feil).__name__, feil)
        return None


# Bare oversikten og Min liste er maal etter et valg.
VALG_TILBAKE = {"oversikten": "/#dine-egne-aksjer", "min_liste": "/min-liste#din-egen-liste"}


def _samme_side() -> None:
    """Som bryteren og stjernen: kommer forespoerselen med Origin, maa den
    vaere denne siden."""
    opphav = request.headers.get("Origin")
    if opphav is not None and opphav.rstrip("/") != request.host_url.rstrip("/"):
        abort(403)


# Story 8.22 (spørsmål 1): grunnen når en aksje ikke har en bransje i lista.
INGEN_BRANSJE = "Aksjen har ingen bransje i lista over Oslo Børs, så den kan ikke følges."


@app.route("/folg")
def folg_side():
    """«Følg en aksje» og «Bytt ut» - story 2.12, utdraget §1 og §2. En side
    med skjema, ikke en dialog med skript (spørsmål 8). Bare lesing.
    Story 8.22: alle aksjene som kan følges, med filter på bransje og
    omsetning. Tillegg 3: sorteringen i stedet for de tre forslagene."""
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    lager = _valglager()
    if lager is None:
        abort(404)
    egne = _egne()
    kode = (request.args.get("kode") or "").strip().upper()
    bytt = (request.args.get("bytt") or "").strip().upper() or None
    sok = (request.args.get("q") or "").strip()[:40]
    i_lista = {a.symbol: a for a in egne["lista"]} if egne else {}
    gammel = i_lista.get(bytt) if bytt else None
    valgt = lager.boersaksje(kode) if kode else None
    omsetning = None
    # Story 8.11c: samme median som i de ferdige listene og merket. Story
    # 8.22: lista viser omsetningen for alle, så den regnes alltid.
    medianene = _medianene()
    if valgt is not None:
        median, maalt, kursene = _omsetningen(lager, medianene, valgt.kode)
        omsetning = {
            "median": median / 1_000_000 if median is not None else None,
            "maalt": maalt,
            "kursene": kursene,
            "utenfor": valg.utenfor_maalingen(median),
        }
    # Story 8.22: hele lista og filteret på bransje og omsetning (spørsmål 6).
    # Tillegg 3 (svarene 10.11 kl. 22:44): sorteringen i stedet for de tre
    # forslagene. Et ukjent valg i adressen er «Alle», og en ukjent sortering
    # er «Mest omsatt først».
    # Tillegg 3: flere bransjer samtidig, i samme rekkefølge som brikkene.
    # Ukjente valg i adressen hoppes over. «Alle» er en lenke uten bransjene,
    # med søket, omsetningen, sorteringen og byttet.
    i_adressen = set(request.args.getlist("bransje"))
    valgte_bransjer = [b for b in valg.BRANSJENE if b in i_adressen]
    # Gjennomgangen (ECH4): ikke feil= eller ukjente parametre.
    uten_bransjer = urlencode(
        [(k, v) for k, v in request.args.items(multi=True) if k in ("q", "omsetning", "sorter", "bytt")]
    )
    valgt_omsetning = request.args.get("omsetning") or ""
    if valgt_omsetning not in {v for v, _ in ferdige_lister.OMSETNINGSFILTER}:
        valgt_omsetning = ""
    valgt_sortering = request.args.get("sorter") or ""
    if valgt_sortering not in {v for v, _ in ferdige_lister.SORTERINGER}:
        valgt_sortering = ferdige_lister.OMSATT
    alle, rader, treff, filtrert, per_bransje = [], [], set(), set(), Counter()
    if valgt is None:
        opptatt = set(i_lista) | {o.symbol for o in lager.ventende() if o.handling == valg.FOLG}
        alle = ferdige_lister.foelgbare(g.tilkobling, opptatt, medianene)
        # Story 8.26 (gruppens svar 11.11 kl. 22:04, tillegg 17): alle radene
        # står i siden, så skriptet kan filtrere og sortere med en gang;
        # filtrert og treff sier hvilke som vises uten skriptet.
        rader = ferdige_lister.sorter(alle, valgt_sortering)
        filtrert = {a.kode for a in ferdige_lister.filtrer(alle, "", valgte_bransjer, valgt_omsetning)}
        treff = {a.kode for a in ferdige_lister.filtrer(alle, sok, valgte_bransjer, valgt_omsetning)}
        per_bransje = Counter(a.bransje for a in alle)
    # Gjennomgangen (ECH11): en aksje som alt er i lista, eller venter, kan
    # ikke følges, og siden sier det før skjemaet sendes.
    alt_fulgt = valgt is not None and (
        valgt.kode in i_lista or any(o.symbol == valgt.kode and o.handling == valg.FOLG for o in lager.ventende())
    )
    # Story 8.22 (svaret 10.11 kl. 13:38): bransjen er fast, og en aksje uten
    # bransje kan ikke følges (spørsmål 1).
    bransje = ferdige_lister.bransjen(g.tilkobling, valgt.kode) if valgt is not None else None
    return render_template(
        "folg.html",
        aktiv="min_liste" if gammel else "oversikt",
        # Story 8.25 (spørsmål 7): siden i omvisningen er «Følg en aksje», ikke
        # oversikten, så omvisningen ikke tilbys her og stegene finner siden.
        omvisning_side="folg",
        sidesti="/folg",
        sok=sok,
        alle=alle,
        rader=rader,
        treff=treff,
        filtrert=filtrert,
        per_bransje=per_bransje,
        rang={b: i for i, b in enumerate(valg.BRANSJENE)},
        valgte_bransjer=valgte_bransjer,
        alle_bransjer="/folg" + (f"?{uten_bransjer}" if uten_bransjer else ""),
        valgt_sortering=valgt_sortering,
        sorteringer=ferdige_lister.SORTERINGER,
        omsatt=ferdige_lister.OMSATT,
        valgt_omsetning=valgt_omsetning,
        bransjene=valg.BRANSJENE,
        omsetningsfilter=ferdige_lister.OMSETNINGSFILTER,
        alt_fulgt=alt_fulgt,
        bransje=bransje,
        mill=1_000_000,
        valgt=valgt,
        omsetning=omsetning,
        gammel=gammel,
        egne=egne,
        grense=valg.GRENSE_MNOK,
        tilbake="min_liste" if gammel else "oversikten",
        feil=request.args.get("feil"),
    )


@app.post("/folg")
def folg():
    """Ønsket om å følge en aksje, eller et bytte. Webserveren skriver bare
    oenske (AD-3) og henter aldri (AD-10)."""
    _samme_side()
    lager = _valglager()
    if lager is None:
        abort(404)
    kode = (request.form.get("kode") or "").strip().upper()
    bytt = (request.form.get("bytt") or "").strip().upper() or None
    try:
        # Story 8.22 (svaret 10.11 kl. 13:38): bransjen er den faste, ikke et
        # felt i skjemaet. En aksje uten bransje avvises med grunnen.
        sektor = ferdige_lister.bransjen(g.tilkobling, kode)
        if sektor is None and lager.boersaksje(kode) is not None:
            raise valg.UgyldigValg(INGEN_BRANSJE)
        lager.folg(kode, sektor or "", bytt)
    except (valg.UgyldigValg, valg.ListaErFull) as feil:
        # Gjennomgangen (BH9, ECH9): samme side, med aksjen og byttet, og
        # grunnen. Kode og bytt er sjekket mot lista og tegnene foer de
        # settes i adressen.
        deler = {"feil": str(feil)}
        if lager.boersaksje(kode) is not None:
            deler["kode"] = kode
        if bytt and re.fullmatch(r"[A-Z0-9-]{1,20}", bytt):
            deler["bytt"] = bytt
        return redirect("/folg?" + urlencode(deler), code=303)
    return redirect(VALG_TILBAKE["min_liste" if bytt else "oversikten"], code=303)


@app.get("/ferdig-liste")
def ferdig_liste_side():
    """Tillegg 3 til 8.22 (svarene 10.11 kl. 22:44): «Er du sikker?» før en
    ferdig liste blir lista. Bare lesing; ingenting byttes før skjemaet
    sendes til POST /ferdig-liste. En bransje uten liste gir 404."""
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    egne = _egne()
    bransje = request.args.get("bransje", "")
    aksjene = egne["ferdige"].get(bransje) if egne else None
    if not aksjene:
        abort(404)
    return render_template(
        "ferdig_liste.html",
        aktiv="min_liste",
        sidesti="/ferdig-liste",
        egne=egne,
        bransje=bransje,
        aksjene=aksjene,
    )


@app.post("/ferdig-liste")
def bruk_ferdig_liste():
    """Story 8.11 (FR-108): en ferdig liste blir lista ved neste henting.
    Bare oenske skrives (AD-3), og ingenting hentes (AD-10)."""
    _samme_side()
    lager = _valglager()
    if lager is None:
        abort(404)
    lista = ferdige_lister.lister(g.tilkobling).get(request.form.get("bransje", ""))
    if not lista:
        abort(400)
    try:
        lager.bruk_liste([(a.symbol, request.form["bransje"]) for a in lista])
    except (valg.UgyldigValg, valg.ListaErFull):
        abort(400)
    return redirect(VALG_TILBAKE["min_liste"], code=303)


@app.post("/fjern")
def fjern_egen():
    """Ønsket om å fjerne en aksje fra lista ved neste henting."""
    _samme_side()
    lager = _valglager()
    if lager is None:
        abort(404)
    symbol = (request.form.get("symbol") or "").strip().upper()
    tilbake = request.form.get("tilbake")
    # Story 8.21 (tillegget kl. 14:44): har aksjen et åpent tenkt kjøp, sier
    # appen først at kursene for den stopper, og ingenting skrives før
    # «Fjern likevel».
    if symbol in _aapne_kjoep() and request.form.get("bekreftet") != "1":
        return render_template(
            "bekreft_fjern.html",
            symbol=symbol,
            tilbake=tilbake if tilbake in VALG_TILBAKE else "oversikten",
            tilbake_adresse=VALG_TILBAKE.get(tilbake, VALG_TILBAKE["oversikten"]),
        )
    try:
        lager.fjern(symbol)
    except valg.UgyldigValg:
        abort(400)
    return redirect(VALG_TILBAKE.get(tilbake, VALG_TILBAKE["oversikten"]), code=303)


def _aapne_kjoep() -> frozenset[str]:
    """Aksjene med et åpent tenkt kjøp, eller et salg som venter på
    sluttkursen (story 8.21, gjennomgangen BH6). Tom uten basen, og for en
    base fra før 0012."""
    tilkobling = g.get("tilkobling")
    if tilkobling is None:
        return frozenset()
    try:
        kjoepene = SqliteNotatlager(tilkobling).kjoepene().values()
        kursleser = SqliteKurslager(tilkobling)
        ut = set()
        for k in kjoepene:
            if k.aapent:
                ut.add(k.symbol)
            elif k.salg_etter is not None:
                serie = kursleser.serie(k.symbol)
                if not serie or serie[-1].dato <= k.salg_etter:
                    ut.add(k.symbol)
        return frozenset(ut)
    except (*BASEFEIL, ValueError):
        return frozenset()


def _fjernes_i_kveld() -> frozenset[str]:
    """Aksjene med et ønske om å fjernes som ikke er tatt i bruk. Hentingen
    tar ønsket i bruk før kursene hentes, så de får ingen kurs i kveld."""
    try:
        lager = _valglager()
        if lager is None:
            return frozenset()
        return frozenset(o.symbol for o in lager.ventende() if o.handling == valg.FJERN)
    except (*BASEFEIL, ValueError):
        return frozenset()


@app.context_processor
def _aapne_tenkte_kjoep():
    """Story 8.21: «Bytt ut» og de ferdige listene sier fra om en aksje som
    tas ut, har et åpent tenkt kjøp."""
    return {"aapne_kjoep": _aapne_kjoep()}


@app.post("/angre")
def angre():
    """Angrer et ønske som ikke er tatt i bruk: raden i oenske slettes."""
    _samme_side()
    lager = _valglager()
    if lager is None:
        abort(404)
    try:
        lager.angre(int(request.form.get("id", "")))
    except valg.ListaErFull as feil:
        return redirect("/folg?" + urlencode({"feil": str(feil)}), code=303)
    except (ValueError, valg.UgyldigValg):
        abort(400)
    return redirect(VALG_TILBAKE.get(request.form.get("tilbake"), VALG_TILBAKE["oversikten"]), code=303)


# --- Story 8.10: «Innstillinger» -----------------------------------------


def _ki_er_paa() -> bool:
    """Story 8.10b: KI-teksten er på når raden i innstilling sier det. Uten
    raden (en base fra før 8.10b, eller ingen base) gjelder kapselen fra
    bryteren, som før, så valget ikke går tapt (spørsmål 1)."""
    rader = innstillinger.les_rader(g.get("tilkobling"))
    if innstillinger.VIS_KI_TEKST in rader:
        return rader[innstillinger.VIS_KI_TEKST]
    return ki_paa(request.cookies.get(KAPSEL))


def _lagre_ki(til: str) -> bool:
    """Valget i basen når den har tabellen. Bryteren og Innstillinger
    skriver begge her (FR-110). Gir False bare når basen har tabellen og
    skrivingen feilet; uten tabellen gjelder kapselen alene, som før 8.10b."""
    tilkobling = g.get("tilkobling")
    if not innstillinger.har_tabellen(tilkobling):
        return True
    try:
        innstillinger.sett(tilkobling, innstillinger.VIS_KI_TEKST, til == PAA)
    except sqlite3.Error as feil:
        app.logger.warning("KI-valget kunne ikke lagres: %s", type(feil).__name__)
        return False
    return True


@app.route("/innstillinger")
def innstillinger_side():
    """«Innstillinger» med «Vis hjelp» (FR-110, utdraget 08.11 §4). Bare lesing."""
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    return render_template(
        "innstillinger.html",
        aktiv="innstillinger",
        kan_lagres=innstillinger.har_tabellen(g.get("tilkobling")),
        # Story 8.10b: samme verdi som bryteren ved KI-teksten.
        ki_er_paa=_ki_er_paa(),
        # Story 8.21: «Notater», i tabellen notatvalg fra 0012.
        notater_kan_lagres=innstillinger.har_tabellen(g.get("tilkobling"), "notatvalg"),
    )


@app.post("/innstillinger")
def lagre_innstilling():
    """Lagrer ett valg i tabellen innstilling, og sender tilbake til siden.
    Webserveren skriver bare den tabellen her (AD-3)."""
    _samme_side()
    if g.get("basefeil"):
        return _basen_kan_ikke_aapnes()
    tilkobling = g.get("tilkobling")
    if not innstillinger.har_tabellen(tilkobling):
        abort(404)
    navn = request.form.get("navn", "")
    til = request.form.get("til")
    # Gjennomgangen (BH7, ECH3): bare valgene siden viser. «Vis KI-tekst»
    # kommer i 8.10b.
    if navn not in innstillinger.PAA_SIDEN or til not in (PAA, AV):
        abort(400)
    # Story 8.21: «Notater» står i notatvalg, som en base fra før 0012 mangler.
    if not innstillinger.har_tabellen(tilkobling, innstillinger.TABELL[navn]):
        abort(404)
    # Story 8.26 (tillegg 6): tilbake til bryteren, så siden står i ro.
    # Gjennomgangen (ECH3): ankeret slås opp før noe skrives, med tittelen
    # for et valg uten anker.
    anker = INNSTILLINGSANKER.get(navn, "innstillinger-tittel")
    innstillinger.sett(tilkobling, navn, til == PAA)
    svar = redirect("/innstillinger#" + anker, code=303)
    if navn == innstillinger.VIS_KI_TEKST:
        # Story 8.10b: kapselen også, som bryteren ved teksten.
        svar.set_cookie(KAPSEL, til, max_age=365 * 24 * 3600, samesite="Lax", httponly=True, secure=request.is_secure)
    return svar


if __name__ == "__main__":
    # Story 3.4: --demo setter bryteren, saa kommandoen er lik i PowerShell
    # og i bash.
    les_flagg(sys.argv[1:])
    # Story 8.20c (U76, spoersmaal 20 i 8.20): uten debug, som skriptene og
    # Docker, som starter waitress.
    app.run(port=8000)
