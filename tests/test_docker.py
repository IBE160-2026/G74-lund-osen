"""Story 3.1: Dockerfile, .dockerignore og compose.yaml.

Testene leser de tre filene som tekst og trenger verken Docker eller nett.
Selve imaget proeves i jobben docker i .github/workflows/tester.yml: ingen
data i imaget, Python 3.13, Oslo-tid, webserveren uten nett og hentingen uten
noekkel. Hvert kontrollpunkt er proevd med en mutant (spesifikasjonen,
Verification).

compose.yaml leses med en liten parser for akkurat denne fila, saa testene
ikke trenger en YAML-pakke. Den kjenner bare innrykk paa to og fire mellomrom
og lister med "- ".
"""

import re
import tomllib
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
DOCKERFILE = ROT / "Dockerfile"
DOCKERIGNORE = ROT / ".dockerignore"
COMPOSE = ROT / "compose.yaml"
CI = ROT / ".github" / "workflows" / "tester.yml"


def _linjer(sti: Path) -> list[str]:
    """Linjene uten kommentarer og tomme linjer, med innrykket."""
    ut = []
    for linje in sti.read_text(encoding="utf-8").splitlines():
        uten = linje.split(" #")[0].rstrip() if not linje.lstrip().startswith("#") else ""
        if uten.strip():
            ut.append(uten)
    return ut


def _instruksjoner() -> list[tuple[str, str]]:
    """Dockerfile som (INSTRUKSJON, resten), med linjer som fortsetter slaatt sammen."""
    samlet, ut = "", []
    for linje in _linjer(DOCKERFILE):
        samlet += linje.strip()
        if samlet.endswith("\\"):
            samlet = samlet[:-1] + " "
            continue
        navn, _, resten = samlet.partition(" ")
        ut.append((navn.upper(), resten.strip()))
        samlet = ""
    return ut


def _blokk(linjer: list[str], innrykk: int) -> dict[str, list[str]]:
    """Deler linjene i blokker etter noekler med akkurat dette innrykket."""
    blokker: dict[str, list[str]] = {}
    navn = None
    for linje in linjer:
        rom = len(linje) - len(linje.lstrip())
        if rom == innrykk:
            navn = linje.strip().split(":")[0]
            blokker[navn] = [linje]
        elif rom > innrykk and navn is not None:
            blokker[navn].append(linje)
        elif rom < innrykk:
            navn = None
    return blokker


def _toppnivaa() -> dict[str, list[str]]:
    return _blokk(_linjer(COMPOSE), 0)


def _tjenester() -> dict[str, dict[str, list[str]]]:
    tjenester = _blokk(_toppnivaa()["services"][1:], 2)
    return {navn: _blokk(linjer[1:], 4) for navn, linjer in tjenester.items()}


def _verdier(felt: list[str]) -> list[str]:
    """Verdien til et felt: listepunktene under det, eller verdien paa samme linje."""
    hode = felt[0].split(":", 1)[1].strip()
    punkter = [l.strip()[2:].strip().strip('"') for l in felt[1:] if l.strip().startswith("- ")]
    return punkter or ([hode] if hode else [])


class TestImaget:
    def test_python_er_313_som_ci(self):
        """Ville feilet hvis imaget brukte en annen Python enn CI."""
        fra = [r for i, r in _instruksjoner() if i == "FROM"]
        assert len(fra) == 1
        assert re.fullmatch(r"python:3\.13\.\d+-slim", fra[0]), fra
        assert re.search(r'python-version:\s*"3\.13"', CI.read_text(encoding="utf-8"))

    def test_avhengighetene_kommer_fra_uv_lock_uten_dev(self):
        """Ville feilet hvis imaget installerte pytest, eller ikke krevde at
        uv.lock stemmer."""
        kjoer = " ".join(r for i, r in _instruksjoner() if i == "RUN")
        assert "uv sync --locked --no-dev" in kjoer

    def test_uv_laster_aldri_ned_en_egen_python(self):
        """Ville feilet hvis uv kunne hente en annen Python under byggingen.
        Med python:3.12-slim lastet uv ned 3.13, og imaget kjoerte en Python
        Dockerfile ikke styrer (mutanten I5)."""
        miljoe = " ".join(r for i, r in _instruksjoner() if i == "ENV")
        assert "UV_PYTHON_DOWNLOADS=never" in miljoe

    def test_bare_koden_kopieres(self):
        """Ville feilet hvis hele mappa ble kopiert. Da er .dockerignore eneste
        vakt mot data/ og .env i imaget."""
        kopier = [r for i, r in _instruksjoner() if i == "COPY" and not r.startswith("--from")]
        assert kopier == ["pyproject.toml uv.lock ./", "src/ src/"]

    def test_ingen_noekkel_i_imaget(self):
        """AD-12: noekkelen kommer bare fra miljoeet naar hent kjoeres."""
        for instruksjon, resten in _instruksjoner():
            if instruksjon in ("ENV", "ARG", "LABEL"):
                assert "EODHD" not in resten.upper() and "KEY" not in resten.upper(), resten
        assert ".env" not in " ".join(r for i, r in _instruksjoner() if i in ("COPY", "ADD"))

    def test_ikke_root(self):
        bruker = [r for i, r in _instruksjoner() if i == "USER"]
        assert bruker and bruker[-1] not in ("root", "0")

    def test_webserveren_er_waitress_uten_debug(self):
        """Svar 1 fra gruppen 08.10: waitress, aldri Flasks egen server og
        aldri debug. Ville feilet med flask run eller app.run."""
        cmd = [r for i, r in _instruksjoner() if i == "CMD"]
        assert len(cmd) == 1
        assert cmd[0] == '["waitress-serve", "--listen=0.0.0.0:5000", "app:app"]'
        hele = "\n".join(_linjer(DOCKERFILE)).lower()
        assert "flask run" not in hele and "debug" not in hele

    def test_waitress_er_en_avhengighet_ikke_dev(self):
        prosjekt = tomllib.loads((ROT / "pyproject.toml").read_text(encoding="utf-8"))
        assert any(a.startswith("waitress") for a in prosjekt["project"]["dependencies"])

    def test_ingen_migrering_i_eget_steg(self):
        """Ville feilet hvis migrasjonene ble lagt i en egen kommando. Det ville
        sett ut som ryddig ansvarsdeling og brutt suksessmaalet «Drift»
        (story 3.1, 2.1b): begge inngangene migrerer gjennom aapne_base."""
        for instruksjon, resten in _instruksjoner():
            if instruksjon in ("RUN", "CMD", "ENTRYPOINT"):
                assert not re.search(r"migr|aapne_base", resten, re.I), resten
        assert "ENTRYPOINT" not in [i for i, _ in _instruksjoner()]
        for navn, felt in _tjenester().items():
            assert "entrypoint" not in felt, navn
            for verdi in _verdier(felt.get("command", ["command:"])):
                assert not re.search(r"migr|aapne_base", verdi, re.I), (navn, verdi)


class TestDockerignore:
    def test_data_noekler_og_lokale_baser_holdes_ute(self):
        """AD-9: ville feilet hvis data/ eller en base kunne komme med."""
        moenstre = set(_linjer(DOCKERIGNORE))
        for krav in ("data/", ".env", ".env.*", "_privat/", ".git", "*.db", "*-raa-*.json"):
            assert krav in moenstre, krav

    def test_env_example_er_unntaket(self):
        moenstre = _linjer(DOCKERIGNORE)
        assert "!.env.example" in moenstre
        assert moenstre.index("!.env.example") > moenstre.index(".env.*")


class TestCompose:
    def test_to_tjenester_fra_samme_image(self):
        tjenester = _tjenester()
        assert set(tjenester) == {"app", "hent"}
        assert _verdier(tjenester["app"]["image"]) == _verdier(tjenester["hent"]["image"]) == ["ose-signal"]

    def test_app_er_standard_og_hent_ligger_i_profilen(self):
        """Svar 2: docker compose up starter bare webserveren. Ville feilet
        hvis hent startet med up og brukte kall."""
        tjenester = _tjenester()
        assert "profiles" not in tjenester["app"]
        assert "command" not in tjenester["app"]
        assert tjenester["hent"]["profiles"][0].split(":", 1)[1].strip() == '["hent"]'

    def test_hent_kjoerer_hentekommandoen(self):
        """Hentekommandoen kjoerer hentingen, uten ny kode (svar 2)."""
        assert _tjenester()["hent"]["command"][0].split(":", 1)[1].strip() == (
            '["python", "src/fetch_prices.py"]'
        )

    def test_bare_hent_har_noekkelen(self):
        """Svar 3: app har ingen noekkel og ingen env_file. hent har .env.
        Ville feilet hvis webserveren fikk noekkelen."""
        tjenester = _tjenester()
        assert "env_file" not in tjenester["app"] and "environment" not in tjenester["app"]
        assert _verdier(tjenester["hent"]["env_file"]) == [".env"]
        assert "environment" not in tjenester["hent"]
        assert "EODHD" not in "\n".join(_linjer(COMPOSE)).upper()

    def test_porten_er_bare_paa_maskinen(self):
        """Betingelsen fra EODHD 21.09: lokalt, ikke publisert. Ville feilet
        med "5000:5000", som binder til alle adresser."""
        tjenester = _tjenester()
        porter = _verdier(tjenester["app"]["ports"])
        assert porter == ["127.0.0.1:5000:5000"]
        assert "ports" not in tjenester["hent"]

    def test_navngitte_volumer_aldri_data_paa_maskinen(self):
        """Regel 22 og AD-11: ose-db og ose-raa er navngitte og atskilte. Ville
        feilet med ./data:/app/data, som rorer data/db/ose.db."""
        forventet = ["ose-db:/app/data/db", "ose-raa:/app/data/raa"]
        for navn, felt in _tjenester().items():
            assert _verdier(felt["volumes"]) == forventet, navn
        toppvolumer = _blokk(_toppnivaa()["volumes"][1:], 2)
        assert set(toppvolumer) == {"ose-db", "ose-raa"}
        assert all(len(linjer) == 1 for linjer in toppvolumer.values()), "volumene skal ikke ha name:"

    def test_ingen_ollama_i_31(self):
        """Rettelsen 05.10 kl. 16:53: Ollama kommer i 10.2."""
        assert "ollama" not in "\n".join(_linjer(COMPOSE)).lower()
