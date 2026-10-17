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
    # En siste linje som slutter med \ ville ellers forsvunnet uten at noen
    # test saa den (ECH10).
    assert not samlet, f"Dockerfile slutter midt i en instruksjon: {samlet!r}"
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


def _apptjenester() -> dict[str, dict[str, list[str]]]:
    """Tjenestene som kjoerer appen fra imaget ose-signal. Story 10.2 la til
    ollama, et ferdig image med sine egne regler (TestOllama)."""
    return {navn: felt for navn, felt in _tjenester().items() if navn != "ollama"}


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
        """Ville feilet med USER root, USER 0 eller USER root:root (ECH9)."""
        bruker = [r for i, r in _instruksjoner() if i == "USER"]
        assert bruker and bruker[-1].split(":")[0] not in ("root", "0")

    def test_mappene_til_volumene_eies_av_brukeren(self):
        """Et nytt navngitt volum faar eieren fra mappa i imaget. Ville feilet
        hvis data/raa manglet eller ikke ble eid av ose. Da kunne hent bruke
        dagens kall og saa feile naar oeyeblikksbildet skrives (VG2)."""
        kjoer = " ".join(r for i, r in _instruksjoner() if i == "RUN")
        assert "mkdir -p data/db data/raa" in kjoer
        assert re.search(r"chown -R ose:ose data(\s|$)", kjoer), kjoer
        assert [r for i, r in _instruksjoner() if i == "USER"][-1] == "ose"

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
        # Story 3.3, svar 2: hent har entrypoint. Ingen entrypoint eller
        # command i compose-fila migrerer.
        for navn, felt in _tjenester().items():
            for noekkel in ("entrypoint", "command"):
                linjer = felt.get(noekkel, [f"{noekkel}:"])
                verdi = " ".join([linjer[0].split(":", 1)[1], *linjer[1:]])
                assert not re.search(r"migr|aapne_base", verdi, re.I), (navn, noekkel, verdi)


class TestDockerignore:
    def test_data_noekler_og_lokale_baser_holdes_ute(self):
        """AD-9: ville feilet hvis data/ eller en base kunne komme med."""
        moenstre = set(_linjer(DOCKERIGNORE))
        for krav in ("data/", ".env", ".env.*", "_privat/", ".git", "*.db", "*-raa-*.json"):
            assert krav in moenstre, krav

    def test_filmoenstrene_gjelder_ogsaa_under_src(self):
        """Et moenster uten **/ gjelder bare roten av konteksten, og
        COPY src/ src/ tar med alt under src/. Ville feilet hvis en base,
        en raadatafil eller __pycache__ under src/ kunne komme med (ECH1)."""
        moenstre = set(_linjer(DOCKERIGNORE))
        for krav in (
            "**/.env",
            "**/*.db",
            "**/*-raa-*.json",
            "**/*-raw-*.json",
            "**/raadata-*.json",
            "**/newsweb-*.json",
            "**/__pycache__/",
        ):
            assert krav in moenstre, krav

    def test_env_example_er_unntaket(self):
        moenstre = _linjer(DOCKERIGNORE)
        assert "!.env.example" in moenstre
        assert moenstre.index("!.env.example") > moenstre.index(".env.*")


class TestCompose:
    def test_alle_tjenestene_fra_samme_image(self):
        """Story 3.4 la til demo-lag og demo, fra samme image. Story 10.2 la
        til ollama, fra sitt eget image (TestOllama)."""
        assert set(_tjenester()) == {"app", "hent", "demo-lag", "demo", "ollama"}
        for navn, felt in _apptjenester().items():
            assert _verdier(felt["image"]) == ["ose-signal"], navn

    def test_begge_bygger_fra_repoet_og_henter_aldri_imaget(self):
        """Ville feilet hvis hent manglet build. Da ville docker compose run
        --rm hent paa en ny maskin hentet et image som heter ose-signal fra et
        register, og gitt det .env med noekkelen (BH2, ECH6)."""
        for navn, felt in _apptjenester().items():
            assert _verdier(felt["build"]) == ["."], navn
            assert _verdier(felt["pull_policy"]) == ["build"], navn

    def test_init_som_pid_1(self):
        """Ville feilet uten init. Da venter docker compose stop i 10 sekunder
        og dreper waitress midt i en forespoersel (ECH8)."""
        for navn, felt in _tjenester().items():
            assert _verdier(felt["init"]) == ["true"], navn

    def test_app_er_standard_og_hent_ligger_i_profilen(self):
        """Svar 2 og 3 fra gruppen 08.10: docker compose up starter bare
        webserveren. Ville feilet hvis hent startet med up og brukte kall."""
        tjenester = _tjenester()
        assert "profiles" not in tjenester["app"]
        assert "command" not in tjenester["app"]
        assert tjenester["hent"]["profiles"][0].split(":", 1)[1].strip() == '["hent"]'

    def test_hent_kjoerer_hentekommandoen(self):
        """Hentekommandoen kjoerer hentingen, uten ny kode (svar 2 og 3 i 3.1).
        Story 3.3, svar 2: som entrypoint og uten command, saa flagg legges
        til. Ville feilet med command, der flagget erstatter kommandoen (ECH7)."""
        hent = _tjenester()["hent"]
        assert hent["entrypoint"][0].split(":", 1)[1].strip() == '["python", "src/fetch_prices.py"]'
        assert "command" not in hent

    def test_bare_hent_har_noekkelen(self):
        """Svar 2 og 3: app har ingen noekkel og ingen env_file. hent har .env.
        Ville feilet hvis webserveren fikk noekkelen."""
        tjenester = _tjenester()
        assert "env_file" not in tjenester["app"] and "environment" not in tjenester["app"]
        for navn in ("demo-lag", "demo"):
            assert "env_file" not in tjenester[navn], navn
        assert _verdier(tjenester["hent"]["env_file"]) == [".env"]
        # Story 10.2 (svar 8): bare adressen til Ollama, ingen noekkel.
        assert [l.strip() for l in tjenester["hent"]["environment"][1:]] == ["OSE_KI_OLLAMA_URL: http://ollama:11434"]
        assert "env_file" not in tjenester["ollama"] and "environment" not in tjenester["ollama"]
        assert "EODHD" not in "\n".join(_linjer(COMPOSE)).upper()

    def test_porten_er_bare_paa_maskinen(self):
        """Betingelsen fra EODHD 21.09: lokalt, ikke publisert. Ville feilet
        med "5000:5000", som binder til alle adresser."""
        tjenester = _tjenester()
        porter = _verdier(tjenester["app"]["ports"])
        assert porter == ["127.0.0.1:5000:5000"]
        assert "ports" not in tjenester["hent"]
        # Story 3.4: demoen har samme port, saa app og demo kan ikke kjoere samtidig.
        assert _verdier(tjenester["demo"]["ports"]) == porter
        assert "ports" not in tjenester["demo-lag"]

    def test_navngitte_volumer_aldri_data_paa_maskinen(self):
        """Regel 22 og AD-11: ose-db og ose-raa er navngitte og atskilte. Ville
        feilet med ./data:/app/data, som rorer data/db/ose.db."""
        tjenester = _tjenester()
        assert _verdier(tjenester["hent"]["volumes"]) == ["ose-db:/app/data/db", "ose-raa:/app/data/raa"]
        assert _verdier(tjenester["app"]["volumes"]) == ["ose-db:/app/data/db"]
        toppvolumer = _blokk(_toppnivaa()["volumes"][1:], 2)
        assert set(toppvolumer) == {"ose-db", "ose-raa", "ose-demo", "ose-ki-ollama"}
        assert all(len(linjer) == 1 for linjer in toppvolumer.values()), "volumene skal ikke ha name:"

    def test_webserveren_har_ikke_oeyeblikksbildene(self):
        """Svar 1 i 3.2: app leser ikke ose-raa, saa den skal heller ikke kunne
        skrive der. Ville feilet hvis app fikk ose-raa tilbake."""
        assert not any("ose-raa" in v for v in _verdier(_tjenester()["app"]["volumes"]))

    def test_volumene_overlapper_ikke(self):
        """Story 3.2 og AD-11: ett volum over hele data/ tar med seg baade det
        som kan bygges opp igjen og det uerstattelige. Ville feilet med
        ose-data:/app/data, eller med to volumer paa samme mappe."""
        for navn, felt in _apptjenester().items():
            maal = [v.split(":")[1] for v in _verdier(felt["volumes"])]
            assert len(set(maal)) == len(maal), (navn, maal)
            for m in maal:
                assert m.rstrip("/") not in ("/app", "/app/data"), (navn, m)
                assert m.startswith("/app/data/"), (navn, m)
                andre = [a for a in maal if a != m]
                assert not any(a.startswith(m.rstrip("/") + "/") for a in andre), (navn, maal)

    def test_skrivebeskyttet_rot_med_tmp_som_tmpfs(self):
        """Svar 2 i 3.2: bare volumene og /tmp kan skrives. Ville feilet uten
        read_only, eller uten /tmp, som waitress trenger for svar over
        outbuf_overflow."""
        for navn, felt in _apptjenester().items():
            assert _verdier(felt["read_only"]) == ["true"], navn
            assert _verdier(felt["tmpfs"]) == ["/tmp"], navn

    def test_ci_proever_hent_med_de_samme_innstillingene(self):
        """Svar 2 i 3.2: prøven med skrivebeskyttet rot i CI bruker det
        compose.yaml gir hent. Ville feilet hvis compose-fila fikk en annen
        tmpfs, eller CI-steget mistet --read-only eller --tmpfs /tmp."""
        hent = _tjenester()["hent"]
        ci = CI.read_text(encoding="utf-8")
        steg = ci.split("- name: Hentingen med skrivebeskyttet rot", 1)[1].split("- name:", 1)[0]
        kjoeringer = [k for k in steg.split("docker run ")[1:] if "ose-signal:ci" in k]
        assert len(kjoeringer) == 2, len(kjoeringer)
        assert _verdier(hent["read_only"]) == ["true"]
        for kjoering in kjoeringer:
            flagg = kjoering.split("ose-signal:ci", 1)[0]
            assert "--read-only" in flagg
            for monteringspunkt in _verdier(hent["tmpfs"]):
                assert re.search(rf"--tmpfs {re.escape(monteringspunkt)}(\s|$)", flagg), monteringspunkt
            # Hvert volum i compose paa sin egen mappe, med samme navn bak ose-ci-ro-.
            for volum in _verdier(hent["volumes"]):
                navn, maal = volum.split(":")
                del_ = navn.removeprefix("ose-")
                assert re.search(rf"-v ose-ci-ro-{re.escape(del_)}:{re.escape(maal)}(\s|$)", flagg), volum

    def test_advarslene_om_basen_og_down_v(self):
        """Svar 3 i 3.2 og AD-7: «du kan slette basen» er feil raad. Ville
        feilet hvis kommentaren ved ose-db eller advarselen om down -v ble
        fjernet."""
        tekst = COMPOSE.read_text(encoding="utf-8")
        foer_db = tekst.split("\nvolumes:\n", 1)[1].split("\n  ose-db:", 1)[0]
        assert "vurdering" in foer_db and "AD-7" in foer_db
        assert "docker compose down -v" in tekst and "aldri -v" in tekst

    def test_demoen_har_bare_sitt_eget_volum(self):
        """Story 3.4: demoen roerer aldri den ekte basen eller oeyeblikksbildene.
        Ville feilet hvis demo eller demo-lag fikk ose-db eller ose-raa, eller
        ose-demo laa paa en annen mappe enn basen, der demo_sti() peker."""
        import lagring_sqlite

        assert lagring_sqlite.demo_sti().parent == Path(lagring_sqlite.BASE_STI).parent
        tjenester = _tjenester()
        mappe = _verdier(tjenester["app"]["volumes"])[0].split(":")[1]
        assert mappe == "/app/data/db"
        for navn in ("demo-lag", "demo"):
            assert _verdier(tjenester[navn]["volumes"]) == [f"ose-demo:{mappe}"], navn
        for navn in ("app", "hent"):
            assert not any("ose-demo" in v for v in _verdier(tjenester[navn]["volumes"])), navn

    def test_demoen_ligger_i_profilen_og_lager_basen_foerst(self):
        """Story 3.4: docker compose up starter ikke demoen, og demo venter til
        demo-lag har laget demobasen. Ville feilet uten profilen, eller med
        depends_on uten betingelsen, som starter demo foer basen finnes."""
        tjenester = _tjenester()
        for navn in ("demo-lag", "demo"):
            assert tjenester[navn]["profiles"][0].split(":", 1)[1].strip() == '["demo"]', navn
        avhengig = [l.strip() for l in tjenester["demo"]["depends_on"][1:]]
        assert avhengig == ["demo-lag:", "condition: service_completed_successfully"]
        assert "depends_on" not in tjenester["demo-lag"]

    def test_demo_lag_kjoerer_demokommandoen_og_demo_har_bryteren(self):
        """demo-lag kjoerer src/demo.py, og demo er webserveren med OSE_DEMO=1.
        Ville feilet hvis demo ikke hadde bryteren, og viste den ekte basen."""
        import app

        tjenester = _tjenester()
        assert tjenester["demo-lag"]["entrypoint"][0].split(":", 1)[1].strip() == '["python", "src/demo.py"]'
        assert "command" not in tjenester["demo-lag"]
        miljoe = [l.strip() for l in tjenester["demo"]["environment"][1:]]
        assert miljoe == [f'{app.I_DEMO}: "1"']
        assert "entrypoint" not in tjenester["demo"] and "command" not in tjenester["demo"]


class TestOllama:
    """Story 10.2, PR F: Ollama i compose som et eget valg (beslutningen
    05.10 kl. 16:53, svar 1 og 8 kl. 15:53). Erstatter testen fra 3.1 om at
    Ollama ikke var med ennaa."""

    def test_eget_valg_i_profilen_ki(self):
        """Ville feilet hvis docker compose up startet modellen."""
        ollama = _tjenester()["ollama"]
        assert ollama["profiles"][0].split(":", 1)[1].strip() == '["ki"]'

    def test_porten_bare_paa_maskinen(self):
        """Svar 8: porten publiseres bare paa 127.0.0.1."""
        assert _verdier(_tjenester()["ollama"]["ports"]) == ["127.0.0.1:11434:11434"]

    def test_modellen_i_eget_volum_aldri_i_imaget(self):
        """AD-9: modellen ligger i ose-ki-ollama."""
        ollama = _tjenester()["ollama"]
        assert _verdier(ollama["volumes"]) == ["ose-ki-ollama:/root/.ollama"]
        assert "build" not in ollama

    def test_versjonen_er_laast(self):
        """FR-605: Ollama-versjonen foeres i raden. Ville feilet med latest
        eller uten tag, saa versjonen kunne skifte uten at noen visste det."""
        bilde = _verdier(_tjenester()["ollama"]["image"])[0]
        assert re.fullmatch(r"ollama/ollama:\d+\.\d+\.\d+", bilde), bilde

    def test_grafikkortet(self):
        """Svar 1: alltid med grafikkort."""
        tekst = "\n".join(_tjenester()["ollama"]["deploy"])
        assert "driver: nvidia" in tekst and "capabilities: [gpu]" in tekst

    def test_hent_naar_ollama_paa_tjenestenavnet(self):
        miljoe = [l.strip() for l in _tjenester()["hent"]["environment"][1:]]
        assert miljoe == ["OSE_KI_OLLAMA_URL: http://ollama:11434"]

    def test_readme_lover_0_kall_bare_naar_basen_har_kursene(self):
        """Instruksjonen kl. 23:58: README-en sier det samme som utskriften
        fra hentingen, 0 kall bare naar basen har dagens kurs for alle."""
        tekst = README.read_text(encoding="utf-8")
        modell = tekst.split("<summary>Den lokale modellen (KI-teksten)</summary>", 1)[1].split("</details>", 1)[0]
        assert "uten nye kall til EODHD" not in modell
        assert "Har basen dagens kurs for alle aksjene, gir det 0 kall til EODHD." in modell
        assert (
            "Mangler noen aksjer dagens kurs, gjør samme kommando et nytt forsøk for dem, og det bruker kall." in modell
        )

    def test_ingen_noekkel_i_compose(self):
        """Gjennomgangen (BH7): ingen variabel i compose utenom adressen."""
        tekst = "\n".join(l for l in _linjer(COMPOSE) if not l.lstrip().startswith("#")).upper()
        for ord_ in ("EODHD", "NOEKKEL", "NØKKEL", "KEY", "TOKEN"):
            assert ord_ not in tekst, ord_
        for navn, felt in _tjenester().items():
            miljoe = [l.strip() for l in felt.get("environment", ["environment:"])[1:]]
            assert all(m.split(":", 1)[0] in ("OSE_DEMO", "OSE_KI_OLLAMA_URL") for m in miljoe), (navn, miljoe)


README = ROT / "README.md"
# Spoersmaal og svar til «Kom i gang», flyttet fra README-en 11.10 kl. 22:32.
HJELP = ROT / "docs" / "hjelp.md"


def _hjelp() -> str:
    return HJELP.read_text(encoding="utf-8")


def _kom_i_gang() -> str:
    tekst = README.read_text(encoding="utf-8")
    return tekst.split("## Kom i gang\n", 1)[1].split("\n## ", 1)[0]


def _blokkene(tekst: str) -> list[tuple[str, str]]:
    """Kodeblokkene i teksten som (spraak, innhold). En blokk uten spraak er
    kommandoer. ```text er det terminalen viser (story 3.4, PR 3)."""
    return re.findall(r"^```(\w*)\n(.*?)^```$", tekst, re.MULTILINE | re.DOTALL)


def _kommandoene() -> list[str]:
    """Hver kommando i kodeblokkene uten spraak i «Kom i gang». Fra PR 3 har
    ingen linje kommentar med #, og testen for det staar for seg."""
    return [l.strip() for spraak, b in _blokkene(_kom_i_gang()) if not spraak for l in b.splitlines() if l.strip()]


class TestReadme:
    """Story 3.3: «Kom i gang» med Docker foerst og uv som alternativ."""

    def test_dockerfile_setter_variabelen_appen_leser(self):
        """Svar 1: ville feilet hvis Dockerfile ikke satte OSE_I_DOCKER=1, saa
        den tomme siden i containeren viste uv-kommandoen."""
        import app

        miljoe = " ".join(r for i, r in _instruksjoner() if i == "ENV")
        assert f"{app.I_DOCKER}=1" in miljoe

    def test_docker_foerst_og_uv_som_alternativ(self):
        """Rettelsen 05.10 og svaret fra hjelpelaereren. Ville feilet hvis uv
        kom foerst, eller en av kommandoene manglet."""
        del_ = _kom_i_gang()
        # Fra 3.4 PR 3 hentes koden med «Download ZIP», ikke git clone (svar 1 11.10).
        for kommando in (
            "«Download ZIP»",
            "cp .env.example .env",
            "docker compose up --build",
            "http://127.0.0.1:5000",
            "docker compose run --rm hent",
            "docker compose down",
        ):
            assert kommando in del_, kommando
        assert del_.index("docker compose up --build") < del_.index("uv run python src/app.py")

    def test_tjenestene_i_readme_finnes_i_compose(self):
        """Ville feilet hvis README-en viste en tjeneste compose.yaml ikke har."""
        # README-en og docs/hjelp.md, der demo-lag staar fra 22:32.
        tekst = README.read_text(encoding="utf-8") + _hjelp()
        # [\w-], saa demo-lag ikke leses som demo (story 3.4).
        brukt = set(re.findall(r"docker compose run --rm ([\w-]+)", tekst))
        brukt |= set(re.findall(r"docker compose up --build ([\w-]+)", tekst))
        assert {"hent", "demo-lag", "demo"} <= brukt
        assert brukt <= set(_tjenester())

    def test_advarselen_om_down_v_og_basen(self):
        """Story 3.2, svar 3, og AD-7: ville feilet hvis README-en ikke advarte
        mot docker compose down -v, eller sa at basen kan slettes."""
        del_ = _kom_i_gang()
        assert "**Skriv aldri `docker compose down -v`.**" in del_
        assert "vurderingene kan ikke lages på nytt" in del_
        # Detaljene om volumene staar i docs/hjelp.md fra 22:32.
        hjelp = _hjelp()
        assert "Bruk aldri `docker compose down -v`" in hjelp
        assert "ose-raa" in hjelp and "ose-db" in hjelp
        assert "Basen kan heller ikke slettes og bygges opp igjen" in hjelp

    def test_raadet_om_tidspunkt_uten_flagget(self):
        """Svar 3: README-en raader til kveld paa en boersdag eller helg, og
        viser ikke flagget som slipper forbi tidskontrollen, som kan laase
        dagen. Fra 19.10 heter det --uten-tidskontroll, og grensen er kl. 21
        (beslutningen 16.10 kl. 21:09). Det gamle navnet staar heller ikke."""
        import fetch_prices

        tekst = README.read_text(encoding="utf-8")
        for flagg in ("--uten-tidskontroll", "--hent-foer-kl-22"):
            assert flagg not in tekst and flagg not in _hjelp(), flagg
        # Gjennomgangen, BH5 og ECH3: tekstene sier hele timer, saa grensen
        # maa vaere en hel time, og timen staar med ordgrense.
        grense = fetch_prices.TIDSGRENSE
        assert grense.minute == 0
        assert re.search(rf"etter kl\. {grense.hour}\b(?![:.]\d)", _kom_i_gang()) and "helgen" in _hjelp()
        # BH4: bare tidspunktet for hentingen, ikke andre klokkeslett.
        for gammel in (r"etter kl\. 22\b(?![:.]\d)", r"før kl\. 22\b(?![:.]\d)"):
            assert not re.search(gammel, tekst) and not re.search(gammel, _hjelp()), gammel

    def test_du_trenger_versjonene(self):
        """3.3b, punkt e: Docker Desktop slik den er prøvd (spesifikasjonen
        for 3.4, 10.10), Python i imaget fra Dockerfile, at Mac ikke er
        prøvd (svar 3 11.10), og Python for veien uten Docker fra
        pyproject.toml."""
        trenger = [a for a in _kom_i_gang().split("\n\n") if a.startswith("**Du trenger**")]
        assert len(trenger) == 1
        trenger = trenger[0]
        assert "Vi prøvde 10.10 med Docker Desktop 4.91.0 (motor 29.8.0, Compose v5.5.1) på Windows" in trenger
        bilde = re.search(r"python:(\d+\.\d+\.\d+)-slim", (README.parent / "Dockerfile").read_text(encoding="utf-8"))
        assert bilde, "fant ikke python-imaget i Dockerfile"
        assert f"imaget bruker Python {bilde.group(1)}" in trenger
        assert "Mac er ikke prøvd ennå" in trenger
        # uv henter Python, så de to avsnittene sier det samme (BH1, ECH).
        assert f"bare [uv](https://docs.astral.sh/uv/), som henter Python {_python_krav()} eller nyere" in trenger
        assert "«Uten Docker, med uv»" in trenger
        assert "Uten Docker, med uv" in _detaljer(_seksjon("Mer for den som vil"))

    def test_demoen_paa_dagtid_og_helgen_i_steg_8(self):
        """3.3b, punkt d: på dagtid en børsdag er demoen veien for å se appen
        med en gang, og steg 8 og raden «Klar» nevner helgen, slik
        docs/hjelp.md gjør. Ville feilet hvis helgen falt ut av steg 8."""
        topp = _kom_i_gang().split("### Felles for begge", 1)[0]
        assert (
            "Første gang før kl. 21 på en børsdag, også på dagtid, er demoen veien for å se appen med en gang" in topp
        )
        klar = [l for l in topp.splitlines() if l.startswith("| Klar |")]
        assert len(klar) == 1 and "helgen" in klar[0] and "etter kl. 21" in klar[0]
        assert "andre dager børsen er stengt" in klar[0]
        steg8 = _steg("Den ekte versjonen (anbefalt)", 8)
        assert "Første gang går det også i helgen og andre dager børsen er stengt." in steg8
        assert "Første gang kan du også hente i helgen" in _hjelp()

    def test_ekte_versjonen_foerst_og_zip_foer_kommandoene(self):
        """Story 3.4: fra 11.10 kl. 22:32 anbefaler README-en den ekte
        versjonen, og den staar foerst. Demoen virker fortsatt uten .env.
        Koden hentes med «Download ZIP» foer den foerste kommandoen, ikke med
        git clone (svar 1 11.10). Het test_demoen_er_den_foerste_kommandoen
        fra PR 2 til gjennomgangen 11.10."""
        del_ = _kom_i_gang()
        kommandoer = _kommandoene()
        assert kommandoer[0] == "cp .env.example .env"
        assert del_.index("«Download ZIP»") < del_.index("cp .env.example .env")
        assert "git clone" not in del_.split("### Står du fast?", 1)[0]
        demo = _seksjon("Demoen")
        assert "docker compose up --build demo" in demo and "http://127.0.0.1:5000" in demo
        assert "Eksempeltall" in demo and ".env" not in demo

    def test_kommandoene_er_de_samme_som_i_koden_og_compose(self):
        """Story 3.4, PR 2: kommandoene siden viser, finnes i README-en, og
        flagget og profilen README-en bruker, finnes i koden og compose.yaml.
        Ville feilet hvis en av dem ble endret bare ett sted."""
        import app
        import demo

        tekst = README.read_text(encoding="utf-8")
        # Hele linjer i kodeblokkene, ikke bare tekst et sted (VG3).
        kommandoer = _kommandoene()
        for kommando in (app.HENTEKOMMANDO, app.HENTEKOMMANDO_DOCKER, demo.DEMOKOMMANDO):
            assert kommando in kommandoer, kommando
        # Kommandoen siden viser naar demobasen mangler, staar i docs/hjelp.md fra 22:32.
        assert f"`{demo.DEMOKOMMANDO_DOCKER}`" in _hjelp()
        # demo-lag kjoerer det DEMOKOMMANDO kjoerer, i containeren.
        lag = _tjenester()["demo-lag"]["entrypoint"][0].split(":", 1)[1].strip()
        assert lag == '["' + '", "'.join(demo.DEMOKOMMANDO.split()[2:]) + '"]'
        assert demo.DEMOKOMMANDO_DOCKER == "docker compose run --rm demo-lag"
        # Profilene README-en bruker, finnes i compose.yaml.
        profiler = {
            f[0].split(":", 1)[1].strip().strip('[]"')
            for f in (felt.get("profiles") for felt in _tjenester().values())
            if f
        }
        # Ogsaa docs/hjelp.md, der stoppkommandoen for demoen staar (VG).
        brukt = set(re.findall(r"docker compose --profile ([\w-]+)", tekst + _hjelp()))
        # Story 10.2: profilen ki for Ollama.
        assert brukt == {"demo", "ki"} and brukt <= profiler

    def test_uv_med_demo_flagget_som_appen_leser(self, monkeypatch):
        """uv-veien: README-en viser --demo, og det er flagget les_flagg kjenner."""
        import app

        tekst = _kom_i_gang()
        flagg = re.findall(r"uv run python src/app\.py (--[\w-]+)", tekst)
        assert flagg == ["--demo"]
        # setenv foerst, ellers lekker bryteren til testene etter (som i test_demo.py).
        monkeypatch.setenv(app.I_DEMO, "0")
        app.les_flagg(flagg)
        assert app.demo_paa()
        assert tekst.index("uv run python src/demo.py") < tekst.index("uv run python src/app.py --demo")

    def test_stoppkommandoen_for_demoen(self):
        """Proeven 10.10 med Compose v5.5.1: docker compose down uten profilen
        stopper ikke demoen. Ville feilet hvis README-en ga docker compose
        down som stoppkommando for demoen, eller CI proevde en annen kommando
        enn README-en viser."""
        demo = _seksjon("Demoen")
        bytte = _detaljer(_kom_i_gang())["Bytte mellom demoen og den ekte versjonen"]
        for avsnitt in (demo, bytte):
            assert "docker compose --profile demo down" in avsnitt
        assert "`docker compose down` stopper ikke demoen" in bytte
        steg = CI.read_text(encoding="utf-8").split("- name: Demoen med compose", 1)[1].split("- name:", 1)[0]
        assert "docker compose -f $f --profile demo down\n" in steg
        assert "docker compose -f $f up -d --build demo;" in steg
        # Ikke -p: med -p stopper docker compose down ogsaa demoen (proevd 10.10).
        assert "-p $p" not in steg and "docker compose -f $f down\n" in steg

    def test_tallene_om_demoen_er_de_samme_som_i_koden(self):
        """VG7: ville feilet hvis demo.py fikk en annen sluttdato eller et annet
        antall selskaper uten at README-en ble rettet."""
        import demo

        maaneder = (
            "januar",
            "februar",
            "mars",
            "april",
            "mai",
            "juni",
            "juli",
            "august",
            "september",
            "oktober",
            "november",
            "desember",
        )
        dag = demo.SLUTTDATO
        ukedag = ("mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag")[dag.weekday()]
        # «Hva er demoen?» staar i docs/hjelp.md fra 22:32.
        tekst = _hjelp()
        assert f"{len(demo.DEMOUNIVERS)} oppdiktede selskaper" in tekst
        assert f"til {ukedag} {dag.day}. {maaneder[dag.month - 1]} {dag.year}" in tekst
        assert "`ose-demo`" in tekst and "ose-demo" in _blokk(_toppnivaa()["volumes"][1:], 2)

    def test_readme_proeven_har_hver_kommando(self):
        """VG6: §9 i docs/kvalitetssikring.md sier at lista rettes naar
        README-en endres. Ville feilet hvis en kommando i «Kom i gang» manglet
        i tabellen for README-proeven. Fra PR 3 teller bare radene."""
        import demo

        tabell = _proevetabellen()
        for kommando in [*_kommandoene(), demo.DEMOKOMMANDO_DOCKER]:
            assert f"`{kommando}`" in tabell, kommando

    def test_siden_lastes_paa_nytt_etter_hentingen(self):
        """Story 3.4, PR 2: siden oppdateres ikke av seg selv."""
        assert "Last siden på nytt når hentingen er ferdig" in _steg("Den ekte versjonen (anbefalt)", 8)

    def test_testene_uten_docker(self):
        """3.3b, punkt c: hvordan testene kjøres på en ren maskin uten Docker,
        med Python-versjonen fra pyproject.toml, og hva man skal se. Ikke et
        fast testtall, som blir usant ved neste story."""
        tester = README.read_text(encoding="utf-8").split("\n## Tester\n", 1)[1].split("\n## ", 1)[0]
        assert f"Python {_python_krav()} eller nyere" in tester and "`requires-python`" in tester
        # Én rekkefølge: uv sync, så uv run pytest, og ingen annen blokk
        # foran (gjennomgangen, BH2).
        blokker = [b.strip() for _, b in _blokkene(tester)]
        assert blokker == ["uv sync", "uv run pytest"], blokker
        assert "uten Docker" in tester and "Alle testene skal bestå" in tester
        # Grunnene for det som hoppes over, slik testene sier dem (VG4).
        for grunn in ("time.tzset", "Unix-sokler", "`::1`", "uten git"):
            assert grunn in tester, grunn
        assert "hoppes over" in tester and "Windows" in tester
        # Ikke et fast testtall (gjennomgangen, BH3, VG3).
        assert not re.search(r"\b\d+\s+(tester|testene|hoppes|hoppet|består|bestått|passed|skipped)\b", tester)
        assert not re.search(r"\b(alle|de)\s+\d+\b", tester, re.IGNORECASE)

    def test_ingen_bilder_utenom_ci_merket(self):
        """Story 3.3: skjermbilder med ekte data publiserer dataene. Ville feilet
        med et bilde i README-en.

        Gruppen 16.10 kl. 21:38: skjermbildet av demoen fra 3.3b, punkt b, er
        tatt ut igjen, så testen godtar ingen bilder utenom CI-merket. Regelen
        står i dokumentene: bilder i README-en kommer bare fra
        docs/bilder/readme/ og viser aldri den ekte versjonen (svar 4 11.10,
        regelen 25.09 under story 3.3). Testen sjekker bare at det ikke er
        noen. Kommer det bilder i «Kom i gang», endres testen i samme PR, med
        stien og alt-teksten som sier at det er demoen (gjennomgangen, VG1, BH1)."""
        tekst = README.read_text(encoding="utf-8")
        bilder = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", tekst)
        assert all(b.endswith("tester.yml/badge.svg") for b in bilder), bilder
        # Ogsaa HTML-bilder og bilder med referanse (BH7).
        assert "<img" not in tekst.lower()
        assert not re.search(r"!\[[^\]]*\]\[", tekst)


BILDEFILER = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def _python_krav() -> str:
    """Versjonen i requires-python i pyproject.toml, for eksempel «3.13»."""
    import tomllib

    krav = tomllib.loads((README.parent / "pyproject.toml").read_text(encoding="utf-8"))["project"]["requires-python"]
    treff = re.fullmatch(r">=(\d+\.\d+)", krav)
    assert treff, f"requires-python har en form testene ikke kjenner: {krav}"
    return treff.group(1)


class TestIngenBilderIDocs:
    def test_ingen_bilder_i_docs_bilder(self):
        """Gruppen 16.10 kl. 21:38: skjermbildet er tatt ut, og ingen
        bildefiler ligger under docs/bilder/, så ingen bilder med ekte data
        blir liggende. Mappa finnes ikke når den er tom, fordi git ikke sporer
        tomme mapper, og da er det heller ingen bilder (gjennomgangen, ECH,
        BH4). Testen sjekker at det ikke er noen, ikke hvor de ligger."""
        mappe = README.parent / "docs" / "bilder"
        # Bare bildefiler: Thumbs.db og .DS_Store fra Utforsker og Finder
        # skal ikke felle testen hos sensor (gjennomgangen av 3.3b, BH4, ECH).
        filer = sorted(
            p.relative_to(README.parent).as_posix()
            for p in mappe.rglob("*")
            if p.is_file() and p.suffix.lower() in BILDEFILER
        )
        assert filer == []


def _proevetabellen(proeve: str | None = None) -> str:
    """Radene i tabellene i §9, uten linjene under dem. Den daterte linja
    nevner kommandoer som ikke lenger er rader (gjennomgangen av PR 3, VG).
    Med proeve: bare tabellen under «### proeve» (Proeve 2 kom 13.10)."""
    kvalitet = (ROT / "docs" / "kvalitetssikring.md").read_text(encoding="utf-8")
    seksjon = kvalitet.split("## 9. README-prøven", 1)[1].split("\n## ", 1)[0]
    if proeve is not None:
        seksjon = seksjon.split(f"\n### {proeve}\n", 1)[1].split("\n### ", 1)[0]
    return "\n".join(l for l in seksjon.splitlines() if l.startswith("|"))


def _seksjon(navn: str) -> str:
    """Delen under «### navn» i «Kom i gang», til neste ###."""
    return _kom_i_gang().split(f"### {navn}\n", 1)[1].split("\n### ", 1)[0]


SEKSJONENE = {"Felles for begge": [1, 2, 3, 4], "Den ekte versjonen (anbefalt)": [5, 6, 7, 8, 9], "Demoen": [5, 6, 7]}


def _steg(seksjon: str, nummer: int) -> str:
    """Steg nummer i seksjonen, med boksene som hoerer til det."""
    deler = re.split(r"^(\d+)\. ", _seksjon(seksjon), flags=re.MULTILINE)
    return dict(zip(deler[1::2], deler[2::2]))[str(nummer)]


def _detaljer(tekst: str) -> dict[str, str]:
    """Hver <details> i teksten som {summary: svar}. Tomme linjer rundt svaret
    kreves, ellers viser ikke GitHub markdown i det."""
    return dict(re.findall(r"<details>\n<summary>(.+?)</summary>\n\n(.*?)\n\n</details>", tekst, re.DOTALL))


def _faq() -> str:
    return _seksjon("Står du fast?")


def _anker(overskrift: str) -> str:
    """Ankeret GitHub lager av en overskrift: smaa bokstaver, mellomrom blir
    bindestrek, og tegn som ikke er bokstav, tall, bindestrek eller
    understrek, faller bort."""
    return re.sub(r"[^\w\- ]", "", overskrift.strip().lower()).replace(" ", "-")


def _uten_bokser(tekst: str) -> str:
    return re.sub(r"^```.*?^```$", "", tekst, flags=re.MULTILINE | re.DOTALL)


def _ankrene(tekst: str) -> set[str]:
    return {_anker(o) for o in re.findall(r"^#+ (.+)$", _uten_bokser(tekst), re.MULTILINE)}


# Spoersmaalene i «Står du fast?» foer 22:32 (76b68cb), og punktene under den
# ekte versjonen som ble flyttet til docs/hjelp.md.
TEMAENE = (
    "Må jeg logge inn eller lage konto?",
    "Hvilken Docker Desktop skal jeg velge?",
    "Hva skjer under installasjonen?",
    "Installasjonen ber om administrator.",
    "Docker Desktop sier at virtualisering mangler.",
    "Docker Desktop ber om å oppdatere WSL (Windows).",
    "Det står ikke «Engine running» etter noen minutter.",
    "ZIP-fila ser ut som en vanlig mappe.",
    "Det er to mapper med samme navn.",
    "Jeg finner ikke ZIP-fila på Mac.",
    "Jeg har fått koden fra før.",
    "Mappa finnes fra før.",
    "Hvilket vindu skal jeg åpne?",
    "Ingenting skjer når jeg limer inn.",
    "Hva betyr cd, og hvordan ser jeg at det gikk?",
    "Mappa lar seg ikke dra inn i vinduet.",
    "Stien har mellomrom og fikk ikke anførselstegn.",
    "Terminal spør om tilgang til Nedlastinger (Mac).",
    "Hva skal jeg se etter i vinduet?",
    "«docker» er ikke gjenkjent, eller «command not found: docker».",
    "«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».",
    "To kommandoer havnet på samme linje.",
    "«no configuration file provided: not found».",
    "«toomanyrequests» fra Docker Hub.",
    "«port is already allocated», «address already in use» eller «ports are not available».",
    "Siden åpnes ikke.",
    "Hva er demoen?",
    "Hvordan starter jeg neste gang?",
    "Hva med nøkkelen?",
    "Når kan jeg hente?",
    "Oversikten er tom.",
    "Hvor ligger dataene?",
    "Kan appen nås fra nettet?",
)


class TestReadmeForNybegynnere:
    """Story 3.4, PR 3: «Kom i gang» for en som aldri har brukt Docker eller
    et terminalvindu. Formen fra 11.10 kl. 22:32: to versjoner i en tabell,
    felles steg 1-4, den ekte versjonen (anbefalt) og demoen fra steg 5,
    høyst 8 spørsmål, og resten i docs/hjelp.md."""

    def test_ingen_kommentar_paa_kommandolinjene(self):
        """Linjene skal virke ogsaa i Ledetekst, der # ikke er en kommentar."""
        for spraak, blokk in _blokkene(_kom_i_gang()):
            assert "#" not in blokk, blokk

    def test_en_kommando_per_boks(self):
        """En av oss fikk to kommandoer paa samme linje 11.10."""
        for spraak, blokk in _blokkene(_kom_i_gang()):
            assert len([l for l in blokk.splitlines() if l.strip()]) == 1, blokk

    def test_bare_kommandoer_i_kom_i_gang(self):
        """En blokk med spraak slapp unna testene for # og én kommando. I
        «Kom i gang» er alle blokker kommandoer, og linja fra terminalen
        staar i docs/hjelp.md."""
        assert {spraak for spraak, _ in _blokkene(_kom_i_gang())} == {""}

    def test_ingen_bokser_testene_ikke_ser(self):
        """GitHub viser ogsaa ~~~ og ``` med innrykk som bokser."""
        for linje in _kom_i_gang().splitlines():
            assert not re.match(r"^ +```|^ *~~~", linje), linje

    def test_tabellen_nevner_begge_og_hvilken_som_er_anbefalt(self):
        """Kl. 22:21: to versjoner med forskjellen forklart, og vi
        anbefaler den ekte. Ville feilet hvis tabellen manglet en versjon,
        eller anbefalte demoen."""
        topp = _kom_i_gang().split("### Felles for begge", 1)[0]
        hode = [l for l in topp.splitlines() if l.startswith("|")][0]
        assert "Den ekte versjonen (anbefalt)" in hode and "| Demoen |" in hode
        assert "Vi anbefaler den ekte versjonen." in topp
        assert "(anbefalt)" not in hode.split("Den ekte versjonen (anbefalt)", 1)[1]

    def test_stegene_er_nummerert_og_har_hoeyst_65_ord(self):
        """Felles 1-4, så 5-9 i den ekte versjonen og 5-7 i demoen, hvert
        med hoeyst 65 ord utenom boksene og en sjekk paa at det gikk bra.

        Rettet 2026-10-13 (story 8.0e PR 2, svaret kl. 23:50): ordene telles
        slik leseren ser dem, med lenketeksten og uten adressen bak, og
        grensen er 65, ikke 60. Setningen fra docs/hjelp.md i steg 2 gjorde
        steget til 70 ord, 8 av dem i adressen til GitHub."""
        for seksjon, numre in SEKSJONENE.items():
            funnet = [int(n) for n in re.findall(r"^(\d+)\. ", _seksjon(seksjon), re.MULTILINE)]
            assert funnet == numre, (seksjon, funnet)
            for n in numre:
                tekst = re.sub(r"\]\([^)]*\)", "]", _uten_bokser(_steg(seksjon, n)))
                assert len(re.findall(r"\w+", tekst)) <= 65, (seksjon, n)
                assert "klar" in tekst.lower() or "Øverst står" in tekst, (seksjon, n)

    def test_stegene_nevner_powershell_og_terminal(self):
        steg = _steg("Felles for begge", 3)
        assert "PowerShell" in steg and "Terminal" in steg and "ikke ISE" in steg

    def test_zip_fila_maa_pakkes_ut(self):
        steg = _steg("Felles for begge", 2)
        assert "«Download ZIP»" in steg and "«Pakk ut alle»" in steg
        # Story 8.0e PR 2: setningen fra «Jeg har fått koden fra før» i
        # docs/hjelp.md staar ordrett til slutt i steg 2.
        svar = _hjelp().split("### Jeg har fått koden fra før.", 1)[1].strip().split("\n\n", 1)[0]
        assert svar == "Har du fått koden som mappe eller ZIP-fil, pakker du den ut og går til steg 3."
        assert steg.strip().endswith(svar)
        assert (
            _steg("Felles for begge", 4)
            .strip()
            .endswith("Har mappa et annet navn, drar du den mappa der README og compose ligger.")
        )
        assert "Du må pakke ut" in _detaljer(_faq())["ZIP-fila ser ut som en vanlig mappe."]

    def test_advarselen_mot_down_v_staar_synlig(self):
        """22:32: rett under stoppet i den ekte versjonen, synlig og ikke
        lukket. Ville feilet hvis advarselen sto i en <details>."""
        ekte = _seksjon("Den ekte versjonen (anbefalt)")
        advarsel = "**Skriv aldri `docker compose down -v`.**"
        assert advarsel in ekte
        assert ekte.index("docker compose down\n") < ekte.index(advarsel)
        uten_detaljer = re.sub(r"<details>.*?</details>", "", _kom_i_gang(), flags=re.DOTALL)
        assert advarsel in uten_detaljer

    def test_staar_du_fast_har_hoeyst_8_spoersmaal(self):
        """22:32: FAQ-en var for lang. Hoeyst 8 spoersmaal, hvert som
        <details> med <summary>, og en lenke til docs/hjelp.md."""
        faq = _faq()
        sporsmaal = _detaljer(faq)
        assert 1 <= len(sporsmaal) <= 8
        assert faq.count("<details>") == faq.count("</details>") == faq.count("<summary>") == len(sporsmaal)
        rest = re.sub(r"<details>.*?</details>", "", faq, flags=re.DOTALL)
        assert [l for l in rest.splitlines() if l.strip()] == [
            "Klikk på spørsmålet som passer.",
            "Flere spørsmål og svar står i [docs/hjelp.md](docs/hjelp.md).",
        ]

    def test_hvert_tema_staar_i_readme_eller_hjelp(self):
        """Ingenting falt bort da FAQ-en ble kortere: hvert spoersmaal fra
        «Står du fast?» og hvert punkt under den ekte versjonen foer 22:32
        staar som spoersmaal i README-en eller som overskrift i docs/hjelp.md."""
        i_readme = set(_detaljer(_faq()))
        i_hjelp = set(re.findall(r"^### (.+)$", _hjelp(), re.MULTILINE))
        for tema in TEMAENE:
            assert tema in i_readme or tema in i_hjelp, tema

    def test_lenkene_virker(self):
        """Lenker til en fil eller et avsnitt, i README-en og docs/hjelp.md."""
        readme = README.read_text(encoding="utf-8")
        for tekst, mappe, egne in ((readme, ROT, _ankrene(readme)), (_hjelp(), HJELP.parent, _ankrene(_hjelp()))):
            for maal in re.findall(r"\]\(([^)\s]+)\)", tekst):
                if maal.startswith(("http://", "https://", "mailto:")):
                    continue
                fil, _, anker = maal.partition("#")
                if fil:
                    assert (mappe / fil).exists(), maal
                if anker:
                    ankre = egne if not fil else _ankrene((mappe / fil).read_text(encoding="utf-8"))
                    assert anker in ankre, maal
        assert "](#står-du-fast)" in readme and "](docs/hjelp.md)" in _faq()

    def test_hjelp_har_frontmatter_og_er_nevnt_i_readme(self):
        """Regel 4 og 19."""
        topp = _hjelp().split("---\n", 2)[1]
        for felt in ("title:", "status: aktiv", "created: 2026-10-11", "updated: "):
            assert felt in topp, felt
        readme = README.read_text(encoding="utf-8")
        mappestruktur = readme.split("## Mappestruktur", 1)[1]
        assert "docs/hjelp.md" in mappestruktur
        dokumentene = readme.split("## Dokumentene", 1)[1].split("\n## ", 1)[0]
        assert "](docs/hjelp.md)" in dokumentene

    def test_merket_i_demoen_er_det_samme_som_i_malene(self):
        """Regel 19: 8.0c kan ikke endre merket uten at README-en rettes.
        Fra 8.0c staar merket ett sted, EKSEMPELTALL_MERKE i app.py, med
        «Demoversjon.» foran i malene (tillegget 11.10). Sitatet i README-en
        staar fortsatt ordrett oeverst paa siden."""
        import app as app_modul

        sitert = _steg("Demoen", 6).split("Øverst står «", 1)[1].split("»", 1)[0]
        assert sitert == app_modul.EKSEMPELTALL_MERKE
        # Story 8.0d: merket staar i rammen, som alle tre malene bruker.
        ramme = (ROT / "src" / "templates" / "_ramme.html").read_text(encoding="utf-8")
        assert re.findall(r'<p class="eksempeltall">([^<]+)</p>', ramme) == ["Demoversjon. {{ eksempeltall_merke }}"]
        for mal in ("index.html", "aksje.html", "basefeil.html"):
            tekst = (ROT / "src" / "templates" / mal).read_text(encoding="utf-8")
            assert tekst.startswith('{% extends "_ramme.html" %}'), mal

    def test_linja_som_viser_at_appen_er_klar(self):
        """Linja er kopiert fra en kjoering 11.10. Ville feilet hvis porten i
        Dockerfile ble endret, eller app eller demo fikk egen command."""
        kommando = dict(_instruksjoner())["CMD"]
        lytter = re.search(r"--listen=([\d.]+:\d+)", kommando).group(1)
        for tjeneste in ("app", "demo"):
            felt = _tjenester()[tjeneste]
            assert "command" not in felt and "entrypoint" not in felt, tjeneste
        assert f"`Serving on http://{lytter}`" in _steg("Demoen", 5)
        assert f"`Serving on http://{lytter}`" in _steg("Den ekte versjonen (anbefalt)", 7)
        tekst = [b for spraak, b in _blokkene(_hjelp()) if spraak == "text"]
        assert len(tekst) == 1
        assert tekst[0].strip() == f"demo-1  | INFO:waitress:Serving on http://{lytter}"

    def test_henvisningene_og_proevetabellen(self):
        """Hver «steg N» peker paa et steg som finnes, og §9 har stegene i
        rekkefoelge for begge versjonene (VG i gjennomgangen av PR 3)."""
        tekst = _kom_i_gang() + _hjelp()
        for n in re.findall(r"[Ss]teg (\d+)", tekst):
            assert 1 <= int(n) <= 9, n
        # «steg N i demoen» og «steg N i den ekte versjonen» peker paa et steg
        # som finnes i den versjonen (VG).
        for n in re.findall(r"steg (\d+) i demoen", tekst):
            assert int(n) in SEKSJONENE["Demoen"], n
        for n in re.findall(r"steg (\d+) i den ekte versjonen", tekst):
            assert int(n) in SEKSJONENE["Den ekte versjonen (anbefalt)"], n
        tabell = _proevetabellen("Prøve 1")
        assert [int(n) for n in re.findall(r"\| Steg (\d+):", tabell)] == [1, 2, 3, 4]
        assert [int(n) for n in re.findall(r"\| Den ekte versjonen, steg (\d+):", tabell)] == [5, 6, 7, 8, 9]
        assert [int(n) for n in re.findall(r"\| Demoen, steg (\d+):", tabell)] == [5, 6, 7]
        # Proeve 2 (13.10) er den ekte versjonen med egen noekkel, steg 5-9.
        tabell = _proevetabellen("Prøve 2: den ekte versjonen med egen nøkkel")
        assert re.findall(r"\| Steg (\d+):|\| Demoen, steg (\d+):", tabell) == []
        assert [int(n) for n in re.findall(r"\| Den ekte versjonen, steg (\d+):", tabell)] == [5, 6, 7, 8, 9]

    def test_stopp_i_begge_versjonene(self):
        assert [b.strip() for _, b in _blokkene(_steg("Den ekte versjonen (anbefalt)", 9))] == ["docker compose down"]
        assert [b.strip() for _, b in _blokkene(_steg("Demoen", 7))] == ["docker compose --profile demo down"]
        assert "Ctrl+C" in _steg("Demoen", 7) and "Ctrl+C" in _steg("Den ekte versjonen (anbefalt)", 9)

    def test_mer_for_den_som_vil_er_lukket(self):
        """22:32: Bytte og uv staar, lukket i <details> under én overskrift."""
        mer = _seksjon("Mer for den som vil")
        # Story 10.2: den lokale modellen, ogsaa lukket.
        assert set(_detaljer(mer)) == {
            "Bytte mellom demoen og den ekte versjonen",
            "Uten Docker, med uv",
            "Den lokale modellen (KI-teksten)",
        }

    def test_svarene_beholdt_innholdet(self):
        """Gjennomgangen 11.10 (VG): bare overskriftene ble sjekket etter
        flyttingen. Innholdet fra svarene foer 22:32 staar i README-en eller
        docs/hjelp.md. Ville feilet hvis et svar ble tomt eller mistet en del."""
        tekst = _faq() + _hjelp()
        for innhold in (
            "wsl --update",
            "AirPlay",
            "Quit Docker Desktop",
            "hvalen ved klokka",
            "AMD64",
            "Apple Silicon",
            "Safari",
            "administrator, og da sperrer Windows dra og slipp",
            "`.env` med nøkkelen",
            "port 5000",
            "Ledetekst",
            "Ikke velg «Windows PowerShell ISE»",
            "filene README og compose",
            "uten filendelsen",
            "virtualisering",
            "toomanyrequests",
            "samme IP-adresse",
            "Dataene ligger i to Docker-volumer",
            "20 kall i døgnet",
            "notepad .env",
            "open -e .env",
            "nano .env",
            "før midnatt",
            "helgen",
            "Appen kan ikke nås fra nettet",
            "lim inn stoppkommandoen",
            "Cmd+mellomrom",
            "Svar OK",
            "Pakk ut alle",
            "glidelås",
        ):
            assert innhold in tekst, innhold

    def test_like_spoersmaal_har_samme_svar(self):
        """Et spoersmaal som staar baade i README-en og i docs/hjelp.md, har
        samme svar begge steder. Svaret i docs/hjelp.md kan ha mer etter."""
        i_hjelp = dict(re.findall(r"^### ([^\n]+)\n\n(.*?)(?=\n\n### |\n\n## |\Z)", _hjelp(), re.MULTILINE | re.DOTALL))
        # Mutanten H13 overlevde foerst: (.+) med DOTALL slukte resten av fila,
        # saa bare ett spoersmaal ble lest, og ingen ble sammenlignet.
        assert len(i_hjelp) == len(re.findall(r"^### ", _hjelp(), re.MULTILINE))
        felles = [s for s in _detaljer(_faq()) if s in i_hjelp]
        assert len(felles) >= 7, felles
        for sporsmaal, svar in _detaljer(_faq()).items():
            if sporsmaal in i_hjelp:
                assert i_hjelp[sporsmaal].strip().startswith(svar.strip()), sporsmaal

    def test_boksene_i_hjelp_foelger_de_samme_reglene(self):
        """Gjennomgangen 11.10 (VG): docs/hjelp.md har ogsaa kommandoer.
        Ingen #, én kommando per boks, bare blokker uten spraak eller text, og
        ingen ~~~ eller ``` med innrykk."""
        hjelp = _hjelp()
        for spraak, blokk in _blokkene(hjelp):
            assert spraak in ("", "text"), spraak
            if not spraak:
                assert "#" not in blokk and len([l for l in blokk.splitlines() if l.strip()]) == 1, blokk
        for linje in hjelp.splitlines():
            assert not re.match(r"^ +```|^ *~~~", linje), linje

    def test_til_faglaerer_og_kom_i_gang_foer_status(self):
        """Kl. 23:41: beskrivelsen, så «Til faglærer», så «Kom i gang»,
        så «Status». Ville feilet hvis «Status» kom foerst igjen, eller noe
        kom mellom beskrivelsen og «Til faglærer»."""
        tekst = README.read_text(encoding="utf-8")
        for del_ in ("Til faglærer:", "\n## Kom i gang\n", "\n## Status\n", "\n## Tester\n"):
            assert del_ in tekst, del_
        assert (
            tekst.index("Til faglærer:")
            < tekst.index("\n## Kom i gang\n")
            < tekst.index("\n## Status\n")
            < tekst.index("\n## Tester\n")
        )
        topp = tekst.split("\n## Kom i gang\n", 1)[0]
        avsnitt = [a.strip() for a in topp.split("\n\n") if a.strip()]
        # Gruppen 16.10 kl. 21:38: skjermbildet under «Til faglærer» er tatt
        # ut, så «Til faglærer» er igjen siste avsnitt før «Kom i gang».
        assert avsnitt[-1].startswith("Til faglærer:"), avsnitt[-1]
        assert avsnitt[-2].startswith("OSE Signal viser"), avsnitt[-2]
        assert "\n## " not in topp

    def test_status_uten_storynumre_og_uten_kommando(self):
        """Kl. 23:41: «Status» i vanlige ord, uten storynumre og uten
        kommandoen, som sto uten stegene foer den. Datoer som «13.–16.10» er
        lov, storynumre i alle formene vi har brukt er ikke det."""
        tekst = README.read_text(encoding="utf-8")
        assert "\n## Status\n" in tekst
        status = tekst.split("\n## Status\n", 1)[1].split("\n## ", 1)[0]
        assert not re.search(r"\(\s*\d{1,2}[AB]?\.\d", status), status
        assert not re.search(r"\b\d{1,2}[AB]?\.\d{1,2}[a-z]\b", status), status
        assert not re.search(r"\b\d{1,2}-\d{1,2}[a-z]?\b", status), status
        assert not re.search(r"\b[Ss]tor(y|ies|yen)\b|PR #\d", status), status
        assert "```" not in status and "~~~" not in status and "`" not in status
        assert not re.search(r"docker[ -]compose|uv run", status, re.IGNORECASE)
        for innhold in (
            "Under arbeid",
            "Flettet til main:",
            "hentingen",
            "Docker",
            "demoen",
            "README-en",
            "kallene som er igjen",
            "hjelp bak «?»",
            "tydeligere merking",
            "utseendet fra designforslaget",
            "KI-laget",
            "Euronext",
            "og at hentingen lager teksten med en lokal modell",
            "aksjesiden viser bare tekster som besto kontrollen",
            "](_bmad-output/implementation-artifacts/sprint-status.yaml)",
        ):
            assert innhold in status, innhold
        # Gjennomgangen av flettingen 12.10 (VG): hver sak staar i riktig liste.
        # Ville feilet hvis noe som ikke er flettet, sto under «Flettet til
        # main», slik grenen 8-0b sa om 2.3b.
        flettet, neste = status.split("Flettet til main:", 1)[1].split("Neste:", 1)
        neste = neste.split("Det som bygges etter demoen", 1)[0]
        for sak in (
            "hentingen",
            "kallene som er igjen",
            "Docker",
            "demoen",
            "README-en",
            "hjelp bak «?»",
            "tydeligere merking",
            "datoene og månedsmerkene i grafen",
            "oversikten fra designforslaget",
            "utseendet fra designforslaget",
            "sortering ved klikk i kolonneraden",
            "den første delen av KI-laget",
            "en bryter som slår den av og på",
            "at hentingen lager teksten med en lokal modell",
            "at hovedindeksen hentes i samme kjøring",
            "vises over tabellen på forsiden",
        ):
            assert sak in flettet, sak
        # Story 8.0d, PR 3 (svar 9 kl. 22:50): «Neste:» følger rekkefølgen
        # etter 8.0d (gruppen 14.10 kl. 22:19 og 22:25).
        # Story 8.15: sorteringen er flyttet til «Flettet til main».
        # 3.3b, punkt a: resten av KI-laget først (svar 10 15.10 kl. 14:47),
        # så rekkefølgen fra 14.10.
        # PR #49 flettet 16.10: teksten fra hentingen er flyttet til «Flettet
        # til main», og «Neste:» begynner med hovedindeksen.
        # Story 2.8, PR 2: at indeksen hentes, er flettet, og visningen
        # («hovedindeksen på forsiden») står først under «Neste:».
        # Story 2.9: visningen er flettet, og «Neste:» begynner med Min liste.
        assert "resten av KI-laget" not in status and "Selve teksten lages ikke ennå" not in status
        saker = (
            "Min liste",
            "innstillingene",
            "periodene i kursgrafen",
            "historikken og signaldagene",
            "«Vis KI-tekst» i innstillingene",
            "KI-teksten om dagen",
            "velge og bytte aksjer",
        )
        for sak in saker:
            assert sak in neste and sak not in flettet, sak
        # Gjennomgangen (VG7): i den rekkefølgen, og det flettede står ikke i «Neste».
        assert [neste.index(s) for s in saker] == sorted(neste.index(s) for s in saker)
        assert "utseendet fra designforslaget" not in neste
        # Story 2.9: hovedindeksen står ikke lenger under «Neste:».
        assert "hovedindeksen" not in neste
        assert "sortering ved klikk i kolonneraden" not in neste

    def test_lenken_til_staar_du_fast_sier_lenger_ned(self):
        """Kl. 23:46: «se «Står du fast?» lenger ned»."""
        assert "se [«Står du fast?»](#står-du-fast) lenger ned." in _kom_i_gang()

    def test_beskrivelsen_foelger_koden_og_gir_ikke_raad(self):
        """Beskrivelsen som ble godkjent 11.10 kl. 23:50. Antallet aksjer er
        lengden av AKSJEUNIVERS, og antallet sjekker og navnene deres er de i
        signalberegning.py, saa README-en maa foelge naar lista endres (2.11
        og 2.12). Den sier at appen ikke gir raad (NFR-06)."""
        import kursdata

        tekst = README.read_text(encoding="utf-8")
        beskrivelse = tekst.split("Til faglærer:", 1)[0].strip().split("\n\n")[-1]
        assert beskrivelse.startswith("OSE Signal viser")
        assert f"viser {len(kursdata.AKSJEUNIVERS)} aksjer på Oslo Børs" in beskrivelse
        # Antallet sjekker telles fra navnene i koden, ikke fra returtypen til
        # sjekker_fra, som kan skrives tuple[Sjekk, ...] uten at noe endres
        # (gjennomgangen 12.10).
        navn = re.findall(r'navn="(\w+)"', (ROT / "src" / "signalberegning.py").read_text(encoding="utf-8"))
        navn = list(dict.fromkeys(navn))
        antall = len(navn)
        tall = {2: "To", 3: "Tre", 4: "Fire"}
        assert antall in tall, navn
        assert f"{tall[antall]} enkle sjekker" in beskrivelse
        # Styrken er summen av sjekkene uten fortegn (FR-703), saa den hoeyeste er antallet.
        assert f"signalstyrke fra 0 til {antall}" in beskrivelse
        assert (
            "– " + ", ".join(n.lower() for n in navn[: antall - 1]) + f" og {navn[antall - 1].lower()} –" in beskrivelse
        )
        assert "Appen gir ikke råd om å kjøpe eller selge." in beskrivelse
        # 12.10 kl. 11:12: at appen er under utvikling, staar ogsaa oeverst,
        # ikke bare i «Status» etter hele «Kom i gang».
        # Rett etter setningen om raad, som instruksjonen kl. 11:15 sier (VG 12.10).
        assert "selge. Den er under utvikling og ikke ferdig." in beskrivelse

    def test_hvorfor_bare_15_aksjer(self):
        """12.10 kl. 10:22: spoersmaalet staar i docs/hjelp.md under
        «Den ekte versjonen», rett etter «Hva med nøkkelen?». Tallet er
        lengden av AKSJEUNIVERS, saa hjelpen maa foelge naar lista endres
        (2.11 og 2.12)."""
        import kursdata

        antall = len(kursdata.AKSJEUNIVERS)
        hjelp = _hjelp()
        ekte = hjelp.split("\n## Den ekte versjonen\n", 1)[1].split("\n## ", 1)[0]
        overskrifter = re.findall(r"^### (.+)$", ekte, re.MULTILINE)
        sporsmaal = f"Hvorfor bare {antall} aksjer?"
        assert sporsmaal in overskrifter, overskrifter
        assert overskrifter.index(sporsmaal) == overskrifter.index("Hva med nøkkelen?") + 1
        svar = ekte.split(f"### {sporsmaal}\n\n", 1)[1].split("\n\n", 1)[0]
        assert f"med {antall} aksjer" in svar
        assert "20 kall i døgnet" in svar and "opptil 18" in svar
        # Gjennomgangen av PR #31, punkt 3 (12.10 kl. 10:38): svaret
        # rett over sier hvor mange kall en henting bruker, og det tallet
        # foelger ogsaa lista.
        nokkel = ekte.split("### Hva med nøkkelen?\n\n", 1)[1].split("\n\n", 1)[0]
        # Ordgrense etter tallet, saa 1 ikke godtar «15» (Verification Gap 12.10).
        # Story 2.8: en henting er aksjene og hovedindeksen.
        assert re.search(rf"en henting bruker {antall + 1}\b", nokkel), nokkel

    def test_til_faglaerer_lenker_til_briefen_med_gjeldende_tag(self):
        """12.10 kl. 12:12: briefen var gjemt langt nede. Lista under
        «Til faglærer:» lenker til den, og taggen er den CLAUDE.md sier er
        gjeldende (regel 17). Ville feilet med en eldre tag i lista."""
        tekst = README.read_text(encoding="utf-8")
        claude = (ROT / "CLAUDE.md").read_text(encoding="utf-8")
        # Regel 17 kan bryte linja mellom «er nå» og taggen.
        gjeldende = re.findall(r"[Gg]jeldende tag er(?:\s+nå)?\s+`([^`]+)`", claude)[-1]
        lista = tekst.split("Til faglærer:\n", 1)[1].split("\n\n", 1)[0]
        assert all(l.startswith("- ") for l in lista.splitlines()), lista
        brief = [l for l in lista.splitlines() if "](_bmad-output/planning-artifacts/product-brief.md)" in l]
        assert len(brief) == 1, lista
        assert re.findall(r"arbeidskrav-product-brief-v\d+", brief[0]) == [gjeldende], brief[0]
