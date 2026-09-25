"""Filadapteren for oeyeblikksbildene - story 1.5, AD-1, AD-3 og AD-19.

Skall: alt som leser oeyeblikksbilder fra data/, ligger her. Foer 1.5 laa det
i portmodulen kursdata.py, som dermed gjorde I/O. Porten importerer ingen
adapter, saa SnapshotLeser flyttet hit sammen med SnapshotKilde: den tar en
SnapshotKilde, og ble den staaende i kursdata.py, ville avhengigheten pekt
feil vei.

EODHDs feltnavn oversettes ikke her, men i eodhd.py. Formatet er EODHDs og
ikke filens, og hentekommandoen i Epic 2 oversetter API-svaret med samme
funksjon uten aa gaa via fila.

Ingen funksjon her gjoer API-kall. Kvoten brukes bare av fetch_prices.py.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from eodhd import kursrad_fra_eodhd
from kursdata import Kursleser, Kursrad, UgyldigKursrad

PROSJEKTROT = Path(__file__).resolve().parent.parent
DATA_KATALOG = PROSJEKTROT / "data"


@dataclass(frozen=True)
class SnapshotKilde:
    """Leser et tidsstemplet oeyeblikksbilde slik signaltesten skrev det.

    Formatet er {"hentet": ..., "serier": {symbol: [rader]}}. Oeyeblikksbilder
    skrives aldri om (FR-406, NFR-07), saa denne kilden er bare lesende - det
    finnes med vilje ingen skrivemetode her.
    """

    hentet: str | None
    serier: dict[str, list[dict]]

    @classmethod
    def fra_fil(cls, sti: Path) -> "SnapshotKilde":
        innhold = json.loads(sti.read_text(encoding="utf-8"))
        return cls(
            hentet=innhold.get("hentet"),
            serier=innhold.get("serier", {}),
        )

    def tidsstempel(self) -> str | None:
        return self.hentet

    def serie(self, symbol: str) -> list[dict]:
        return self.serier.get(symbol, [])


def _hentet_fra_tekst(tekst: object) -> datetime | None:
    """ISO 8601 med tidssone, i UTC. None hvis tiden ikke kan leses."""
    if not isinstance(tekst, str):
        return None
    try:
        tid = datetime.fromisoformat(tekst)
    except ValueError:
        return None
    if tid.tzinfo is None or tid.utcoffset() is None:
        return None
    return tid.astimezone(timezone.utc)


class SnapshotLeser:
    """Kursleser over et oeyeblikksbilde - story 1.4a, AD-15, AD-19, AD-20.

    Pakker inn SnapshotKilde og gir Kursrad. Alt oversettes ved oppretting,
    og serie gir kopier ut. Den er med vilje ikke en Kurslager: et
    oeyeblikksbilde skrives aldri om.

    Et symbol med en rad som ikke kan oversettes, eller to rader med samme
    dato, behandles som manglende: tom serie og sist_hentet None. De andre
    leses som vanlig. Ingenting gjettes.

    Kan hentet ikke leses (mangler, ikke ISO 8601, uten tidssone), er hele
    oeyeblikksbildet manglende. En serie har alltid en tid i de andre
    lagrene, fordi erstatt_serie setter begge, og slik er det her ogsaa:
    sist_hentet(s) er None hvis og bare hvis serie(s) er tom.
    """

    def __init__(self, kilde: SnapshotKilde):
        self._serier: dict[str, tuple[Kursrad, ...]] = {}
        self._hentet = _hentet_fra_tekst(kilde.hentet)
        # serier som ikke er et objekt, kan ikke leses - som en uleselig hentet.
        if self._hentet is None or not isinstance(kilde.serier, dict):
            return
        for symbol, raa in kilde.serier.items():
            # En serie som ikke er en liste, gjoer bare dette symbolet manglende.
            if not isinstance(raa, list):
                continue
            try:
                rader = [kursrad_fra_eodhd(r) for r in raa]
            except (UgyldigKursrad, KeyError):
                continue
            datoer = {r.dato for r in rader}
            if not rader or len(datoer) != len(rader):
                continue
            self._serier[symbol] = tuple(sorted(rader, key=lambda r: r.dato))

    def serie(self, symbol: str) -> list[Kursrad]:
        return list(self._serier.get(symbol, ()))

    def sist_hentet(self, symbol: str) -> datetime | None:
        return self._hentet if symbol in self._serier else None


# Oeyeblikksbilder heter <prefiks>-raa-<ÅÅÅÅ-MM-DD>.json. fetch_prices skriver
# KURSPREFIKS; eksperimentene skrev signaltest-, volumsjekk-, nyhetstest-.
# Alle leses likt, men ved lik dato vinner kursfila - se nyeste_snapshot.
KURSPREFIKS = "kurser"

_SNAPSHOT_MONSTER = re.compile(r"-raa-(\d{4}-\d{2}-\d{2})\.json$")


def nyeste_snapshot(katalog: Path = DATA_KATALOG) -> Path | None:
    """Oeyeblikksbildet med nyeste dato i navnet, eller None hvis ingen finnes.

    Datoen leses ut av filnavnet, ikke av filtidsstempelet. Et oeyeblikksbilde
    som kopieres eller sjekkes ut paa nytt, faar ny mtime, men datoen i navnet
    er den som gjelder - det er den dagen dataene er fra.

    **Datoen avgjoer alene.** Prefikset er aldri med i sammenligningen av
    datoer. Det var feilen her foer: valget var `max` over tuplene
    (dato, sti), og ved LIK dato falt `max` tilbake paa stien - da vant
    "signaltest-" over "kurser-" fordi s kommer etter k. Docstringen lovet at
    prefikset ikke ble sortert med, og det holdt saa lenge datoene var ulike.

    **Ved lik dato gjelder denne regelen:** fila fetch_prices skriver
    (KURSPREFIKS) vinner over alle andre prefikser. De andre er engangsuttrekk
    fra maalingene - signaltest, volumsjekk, nyhetstest - og skal ikke kunne
    fortrenge dagens kurser. Er ingen av dem kursfila, velges den alfabetisk
    foerste, slik at svaret er det samme hver gang og ikke avhenger av hvilken
    rekkefoelge katalogen leses i.
    """
    if not katalog.is_dir():
        return None

    datert = [
        (treff.group(1), sti)
        for sti in katalog.glob("*-raa-*.json")
        if (treff := _SNAPSHOT_MONSTER.search(sti.name))
    ]
    if not datert:
        return None

    nyeste_dato = max(dato for dato, _ in datert)
    return min(
        (sti for dato, sti in datert if dato == nyeste_dato),
        key=lambda sti: (not sti.name.startswith(f"{KURSPREFIKS}-raa-"), sti.name),
    )


def nyeste_leser(katalog: Path | None = None) -> Kursleser | None:
    """Kursleser for det nyeste oeyeblikksbildet i katalogen, eller None.

    None betyr at katalogen mangler eller ikke har noe oeyeblikksbilde. Uten
    argument leses DATA_KATALOG naar funksjonen kalles, ikke naar den
    defineres, saa en test kan peke den mot en annen katalog.
    """
    fil = nyeste_snapshot(DATA_KATALOG if katalog is None else katalog)
    return SnapshotLeser(SnapshotKilde.fra_fil(fil)) if fil else None
