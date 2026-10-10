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
        for krav in ("**/.env", "**/*.db", "**/*-raa-*.json", "**/*-raw-*.json",
                     "**/raadata-*.json", "**/newsweb-*.json", "**/__pycache__/"):
            assert krav in moenstre, krav

    def test_env_example_er_unntaket(self):
        moenstre = _linjer(DOCKERIGNORE)
        assert "!.env.example" in moenstre
        assert moenstre.index("!.env.example") > moenstre.index(".env.*")


class TestCompose:
    def test_alle_tjenestene_fra_samme_image(self):
        """Story 3.4 la til demo-lag og demo, fra samme image."""
        tjenester = _tjenester()
        assert set(tjenester) == {"app", "hent", "demo-lag", "demo"}
        for navn, felt in tjenester.items():
            assert _verdier(felt["image"]) == ["ose-signal"], navn

    def test_begge_bygger_fra_repoet_og_henter_aldri_imaget(self):
        """Ville feilet hvis hent manglet build. Da ville docker compose run
        --rm hent paa en ny maskin hentet et image som heter ose-signal fra et
        register, og gitt det .env med noekkelen (BH2, ECH6)."""
        for navn, felt in _tjenester().items():
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
        assert "environment" not in tjenester["hent"]
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
        assert set(toppvolumer) == {"ose-db", "ose-raa", "ose-demo"}
        assert all(len(linjer) == 1 for linjer in toppvolumer.values()), "volumene skal ikke ha name:"

    def test_webserveren_har_ikke_oeyeblikksbildene(self):
        """Svar 1 i 3.2: app leser ikke ose-raa, saa den skal heller ikke kunne
        skrive der. Ville feilet hvis app fikk ose-raa tilbake."""
        assert not any("ose-raa" in v for v in _verdier(_tjenester()["app"]["volumes"]))

    def test_volumene_overlapper_ikke(self):
        """Story 3.2 og AD-11: ett volum over hele data/ tar med seg baade det
        som kan bygges opp igjen og det uerstattelige. Ville feilet med
        ose-data:/app/data, eller med to volumer paa samme mappe."""
        for navn, felt in _tjenester().items():
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
        for navn, felt in _tjenester().items():
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

    def test_ingen_ollama_i_31(self):
        """Rettelsen 05.10 kl. 16:53: Ollama kommer i 10.2."""
        assert "ollama" not in "\n".join(_linjer(COMPOSE)).lower()


README = ROT / "README.md"


def _kom_i_gang() -> str:
    tekst = README.read_text(encoding="utf-8")
    return tekst.split("## Kom i gang\n", 1)[1].split("\n## ", 1)[0]


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
        for kommando in ("git clone", "cp .env.example .env", "docker compose up --build",
                         "http://127.0.0.1:5000", "docker compose run --rm hent", "docker compose down"):
            assert kommando in del_, kommando
        assert del_.index("docker compose up --build") < del_.index("uv run python src/app.py")

    def test_tjenestene_i_readme_finnes_i_compose(self):
        """Ville feilet hvis README-en viste en tjeneste compose.yaml ikke har."""
        brukt = set(re.findall(r"docker compose run --rm (\w+)", README.read_text(encoding="utf-8")))
        assert brukt and brukt <= set(_tjenester())

    def test_advarselen_om_down_v_og_basen(self):
        """Story 3.2, svar 3, og AD-7: ville feilet hvis README-en ikke advarte
        mot docker compose down -v, eller sa at basen kan slettes."""
        del_ = _kom_i_gang()
        assert "Bruk aldri `docker compose down -v`" in del_
        assert "vurderingene" in del_ and "ose-raa" in del_ and "ose-db" in del_
        assert "Basen kan heller ikke slettes og bygges opp igjen" in del_

    def test_raadet_om_tidspunkt_uten_flagget(self):
        """Svar 3: README-en raader til kveld paa en boersdag eller helg, og
        viser ikke --hent-foer-kl-22, som kan laase dagen."""
        tekst = README.read_text(encoding="utf-8")
        assert "--hent-foer-kl-22" not in tekst
        assert "etter kl. 22" in _kom_i_gang() and "helgen" in _kom_i_gang()

    def test_ingen_bilder_utenom_ci_merket(self):
        """Story 3.3: skjermbilder med ekte data publiserer dataene. Ville feilet
        med et bilde i README-en."""
        tekst = README.read_text(encoding="utf-8")
        bilder = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", tekst)
        assert all(b.endswith("tester.yml/badge.svg") for b in bilder), bilder
        # Ogsaa HTML-bilder og bilder med referanse (BH7).
        assert "<img" not in tekst.lower()
        assert not re.search(r"!\[[^\]]*\]\[", tekst)
