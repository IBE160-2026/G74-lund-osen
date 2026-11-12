"""Hjelpetekstene bak «?» - story 8.0b.

Ren logikk. Fila leser ingen filer og gjoer ingen kall. Alle tekstene staar
her og ikke i malene, saa et ord kan endres ett sted. Min liste (8.3) skal
bruke de samme.

Tallene som er parametre, hentes fra Parametre og skrives med tall() (regel
21). Da kan ikke hjelpen si én ting mens koden gjoer en annen. Tallene som er
maalinger, staar som egne konstanter med kilden sin.

Hver tekst har kildene sine: en fil i repoet og et sted i den, ordrett, som en
test slaar opp. Teksten sier bare det koden gjoer og det kilden sier, og den
gir ikke raad (NFR-06). Retningen forklares med ordene og symbolene fra
RETNINGSVISNING (FR-704, FR-103), ikke med egne ord.

Tekstene ble godkjent av gruppen 11.10 kl. 11:33, med endringene i
spesifikasjonen. Story 8.0c (godkjent 13.10 kl. 15:36): hvert «?» staar ved
det det forklarer, hver tekst har hoeyst 3 setninger utenom grensene og
skjevhet, og retningen forklares med +1 og -1 (FR-704, rettet 13.10).
"""

from dataclasses import dataclass

from markedsoversikt import RETNINGSVISNING, UKJENT_RETNING, grensen_som_tekst
from signalberegning import (
    BLANDET,
    INGEN,
    NEGATIV,
    POSITIV,
    STANDARD,
    Parametre,
    nodvendige_dager,
)
from tallformat import HARDT_MELLOMROM, tall

# Kildene, som stier fra roten av repoet.
PRD = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md"
BEGRUNNELSER = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/begrunnelser.md"
MAALINGER = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md"
SIGNALBEREGNING = "src/signalberegning.py"
MARKEDSOVERSIKT = "src/markedsoversikt.py"
AKSJEDETALJ = "src/aksjedetalj.py"
APP = "src/app.py"
# Story 8.19: neste henting i stripa.
BOERSDAG = "src/boersdag.py"
INDEX_MAL = "src/templates/index.html"
# Story 8.6: hovedindeksen og søylene står i en delmal, som oversikten og
# børsometeret bruker.
HOVEDINDEKS_MAL = "src/templates/_hovedindeks.html"
BOERSOMETER = "src/boersometer.py"
HOVEDINDEKS = "src/hovedindeks.py"
GRAF = "src/graf.py"
AKSJE_MAL = "src/templates/aksje.html"
PERIODER = "src/perioder.py"
PERIODE_MAL = "src/templates/_perioder.html"
HISTORIKK = "src/historikk.py"
# Gruppens svar 04.11 kl. 22:23, 3: hjelpen ved KI-delen, slått opp her.
KI_GRUNNLAG = "src/ki_grunnlag.py"
DAGENE = "src/dagene.py"
KI_KONTROLL = "src/ki_kontroll.py"
KI_VISNING = "src/ki_visning.py"
MOENSTRENE = "src/moenstrene.py"
# Story 2.12: å velge og bytte aksjer.
VALG = "src/valg.py"
FERDIGE_LISTER = "src/ferdige_lister.py"
# Story 10.6: teksten om dagen paa forsiden.
DAGSGRUNNLAG = "src/dagsgrunnlag.py"
KI_DAGEN = "src/ki_dagen.py"

# FR-701: tre sjekker, ingen fjerde.
ANTALL_SJEKKER = 3

# Maalingene bak grensene (malinger.md §7.4 og §9). De er ikke parametre: de
# sier hva grensene ble kontrollert mot.
#
# Grensene som ble maalt, staar for seg og ikke fra Parametre: teksten om
# maalingen sier hvilke verdier som ble kontrollert, og det var disse. En test
# krever at STANDARD er lik dem, saa en ny grense i Parametre stopper testene
# til grensen er maalt og teksten rettet (gjennomgangen av 8.0b).
MAALTE_GRENSER = Parametre(
    noytralsone=0.02,
    volumfaktor=1.5,
    volatilitet_vindu=20,
    volum_vindu=20,
    terskel=2,
)
MAALTE_BOERSDAGER = 199
MAALTE_AKSJER = 15
MAALT_PERIODE = "fra desember 2025 til september 2026"

# Retningen over de 199 dagene, andel av aksjedagene med utslag
# (malinger.md §7.4, begrunnelser.md §6, rettet 03.10).
ANDEL_POSITIV = 60.0
ANDEL_NEGATIV = 29.5

# Betingelsen for hver retning, med ordene i FR-704 (rettet 13.10: +1 og -1,
# ikke «peker opp» og «peker ned»). Ordet og symbolet foran kommer fra
# RETNINGSVISNING.
_RETNINGSBETINGELSE = {
    POSITIV: "alle sjekkene som slo ut, ga +1.",
    NEGATIV: "alle sjekkene som slo ut, ga -1.",
    BLANDET: "noen av sjekkene som slo ut, ga +1, og noen -1.",
    INGEN: "ingen av sjekkene slo ut, og styrken er 0.",
}


@dataclass(frozen=True)
class Hjelpetekst:
    """En tekst i hjelpevinduet. tittel staar i fet skrift foran teksten,
    og er tom naar teksten er en hel setning.

    kilder er par av (fil, sted): fila fra roten av repoet, og tekst som
    staar ordrett i den.
    """

    tittel: str
    tekst: str
    kilder: tuple[tuple[str, str], ...]


def _retningstittel(retning: str) -> str:
    visning = RETNINGSVISNING[retning]
    return f"{visning.symbol} {visning.tekst}:"


def _vis(verdi: float, slag: str) -> str:
    """Tallet som tekst etter regel 21, eller ValueError hvis det ikke kan
    vises uten aa rundes av. Da ville hjelpen vist en annen grense enn den
    koden bruker, for eksempel «1,3» for en volumfaktor paa 1,25."""
    tekst = tall(verdi, slag)
    tilbake = float(tekst.replace(HARDT_MELLOMROM, "").removesuffix("%").replace(",", "."))
    if abs(tilbake - verdi) > 1e-9:
        raise ValueError(f"{verdi} vises som {tekst!r} med slaget {slag!r}. Rett desimalene i tallformat.py")
    return tekst


def _grensene(m: Parametre) -> str:
    """Grensene som ble maalt, i den rekkefoelgen teksten nevner dem."""
    if m.volatilitet_vindu == m.volum_vindu:
        vinduene = f"de to vinduene på {_vis(m.volatilitet_vindu, 'heltall')} børsdager"
    else:
        vinduene = f"vinduene på {_vis(m.volatilitet_vindu, 'heltall')} og {_vis(m.volum_vindu, 'heltall')} børsdager"
    return (
        f"{_vis(m.noytralsone * 100, 'grense')}, {_vis(m.volumfaktor, 'faktor')} ganger, "
        f"{vinduene} og terskelen {_vis(m.terskel, 'heltall')}"
    )


def hjelpetekster(p: Parametre = STANDARD) -> dict[str, Hjelpetekst]:
    """Alle hjelpetekstene, med tallene fra p. Teksten om maalingen bruker
    MAALTE_GRENSER, fordi den sier hva som ble maalt."""
    sone = _vis(p.noytralsone * 100, "grense")
    # Gruppens svar 04.11 kl. 09:58. Her, fordi boersometer.py importerer
    # denne modulen.
    from boersometer import GRENSE_STERK

    soeylegrense = _vis(GRENSE_STERK, "grense")
    faktor = _vis(p.volumfaktor, "faktor")
    ma = _vis(p.ma_vindu, "heltall")
    volatilitet = _vis(p.volatilitet_vindu, "heltall")
    volum = _vis(p.volum_vindu, "heltall")
    terskel = _vis(p.terskel, "heltall")
    dager = _vis(nodvendige_dager(p), "heltall")

    tekster = {
        "selskap": Hjelpetekst(
            "",
            # Story 8.15b (gjennomgangen, ECH2): «?» står ved en lenke som
            # sorterer, så teksten sier hva hvert klikk gjør.
            # Story 8.3: stjernen foran navnet, i samme celle.
            "Klikk på et selskapsnavn i tabellen for å se sjekkene, tallene bak og kursgrafen. "
            "Klikk på «Selskap» for å sortere A til Å, og en gang til for Å til A. "
            "Stjernen foran navnet legger aksjen i Min liste, og et nytt trykk tar den ut.",
            (
                (INDEX_MAL, '<a href="/aksje/{{ rad.aksje.symbol }}">'),
                (INDEX_MAL, 'class="stjerneknapp'),
                (INDEX_MAL, 'sorterlenke("selskap", "Selskap")'),
                (AKSJE_MAL, '<p class="maalt">Målt mot'),
                (AKSJE_MAL, 'class="kurslinje"'),
            ),
        ),
        # Story 8.6 (FR-106, avgjørelsen 22.10 kl. 23:19): børsometeret.
        # Story 8.20b (U95, svaret 06.11 kl. 23:07): høyst 60 ord i vinduet,
        # og resten i docs/hjelp.md, «Hva viser børsometeret?».
        "boersometeret": Hjelpetekst(
            "Børsometer:",
            "én rute per aksje, samlet etter bransje. Fargen er endringen, i fem trinn. "
            "Klikk på en rute for å se aksjen.",
            (
                (PRD, "#### FR-106 — Børsometeret"),
                (BOERSOMETER, "def fargetrinn("),
                (BOERSOMETER, "def bygg_boersometer("),
            ),
        ),
        # Story 8.20b (svaret 06.11 kl. 22:57): størrelsen og rammen.
        "boersometeret_ruta": Hjelpetekst(
            "",
            "For én dag følger størrelsen volumet mot vanlig, og for en periode er rutene like store. "
            f"Gul ramme er {ANTALL_SJEKKER} av {ANTALL_SJEKKER} og mørk {ANTALL_SJEKKER - 1} av "
            f"{ANTALL_SJEKKER}, begge siste børsdag.",
            (
                (BOERSOMETER, "def vekt("),
                (BOERSOMETER, "def ramme("),
            ),
        ),
        # Story 8.23 (tillegg 3, gruppens svar kl. 15:54): «?» ved «Endring» og
        # «Volum mot vanlig» i tabellen på Børsometeret, og snittet i bransjeraden.
        "boersometer_endring": Hjelpetekst(
            "Endring:",
            "endringen i sluttkursen fra børsdagen før, eller for perioden du har valgt, justert for utbytte. "
            "Snitt i raden for bransjen er gjennomsnittet av endringen for aksjene i bransjen som har kurs, "
            "uten vekt.",
            (
                (BOERSOMETER, "def snitt("),
                (BOERSOMETER, "endringer = [r.endring for r in ruter if r.endring is not None]"),
            ),
        ),
        "boersometer_volum": Hjelpetekst(
            "Volum mot vanlig:",
            f"dagens volum delt på medianen for de {p.volum_vindu} børsdagene før. Lavt er under 1, vanlig fra 1 "
            f"til og med {faktor}, og høyt over {faktor}, som gir utslag på interesse.",
            (
                (BOERSOMETER, "def stoerrelse("),
                (BOERSOMETER, "if volumforhold > p.volumfaktor:"),
                (BOERSOMETER, "if volumforhold < 1:"),
                (SIGNALBEREGNING, "volumfaktor"),
            ),
        ),
        # Story 2.9 (FR-104): delen over tabellen.
        "hovedindeksen": Hjelpetekst(
            "Hovedindeksen:",
            # Story 8.17a (gruppens svar 30.10 kl. 12:21, e): tabellens dag.
            # Story 8.2b, a (U26): kortere, og søylene i et eget vindu.
            # Gjennomgangen av 8.2b (VG2): «med kurs samme dag» står igjen.
            "verdien den dagen tabellen viser, og endringen i prosent fra "
            "børsdagen før. «Gikk bedre» teller aksjene med kurs samme dag og "
            "større endring enn indeksen, slik tallene vises, og lik teller ikke.",
            (
                (PRD, "#### FR-104 — Hovedindeksen i markedsoversikten"),
                (PRD, "«Bedre» avgjøres på endringen slik den vises, og lik er ikke bedre."),
                (HOVEDINDEKS, "def er_bedre("),
            ),
        ),
        # Story 2.9b (FR-105): søylene under indeksen. Story 8.2b, a (U26):
        # i et eget vindu, og kortere, fordi forklaringen under søylene
        # viser linja.
        "soeylene": Hjelpetekst(
            "Søylene:",
            "endringen for hver aksje, fra størst fall til venstre til størst stigning "
            # Gruppens svar 04.11 kl. 09:58: lys og mørk, som i børsometeret.
            f"til høyre, mørk fra {soeylegrense} opp eller ned, som i børsometeret, og lys under. "
            # Gjennomgangen av 8.2b (VG2): grå ved 0,00 % står igjen.
            "Den stiplede linja er indeksen, grønn når den steg, rød når den falt "
            "og grå ved 0,00 %. "
            # Story 8.2a, c (U20): symbolet over søyla er en lenke.
            "Et gult bransjesymbol betyr 3 av 3 siste børsdag, et klikk på symbolet viser aksjen, "
            # Gruppens svar 04.11 kl. 22:23, 2: lenken til børsometeret.
            # Gruppens svar 05.11 kl. 14:29, 3: «Se dagen» ved én dag.
            "og «Se dagen» eller «Se perioden» under søylene åpner børsometeret med samme dag eller periode.",
            (
                (PRD, "#### FR-105 — Søylene under hovedindeksen"),
                (HOVEDINDEKS_MAL, 'class="til-boersometer"'),
                (HOVEDINDEKS_MAL, '<a class="etikett'),
                (PRD, "Indeksens endring er en stiplet linje, grønn når indeksen steg og rød når den"),
                (HOVEDINDEKS, "def bygg_soeyler("),
                (HOVEDINDEKS_MAL, 'class="indekslinje'),
                (APP, "def soeylestyrke("),
                (BOERSOMETER, "GRENSE_STERK = "),
            ),
        ),
        "sluttkurs": Hjelpetekst(
            "Sluttkurs:",
            "kursen ved børsens stengning siste børsdag i dataene, uten utbyttejustering.",
            ((PRD, "| Sluttkurs | `close` for siste børsdag |"), (INDEX_MAL, "Sluttkursen er den ujusterte kursen")),
        ),
        # U5 i docs/ux-logg.md (story 2.7b): paa aksjesiden er sluttkursen for
        # dagen siden viser, ogsaa en dag valgt med «Velg dag» (8.16b).
        # Story 8.20a (del E og J): «Vis dagen», og teksten fra utkastet.
        "sluttkurs_aksje": Hjelpetekst(
            "Sluttkurs:",
            "kursen ved børsens stengning den dagen siden viser, uten utbyttejustering. "
            "Dagen står under navnet øverst: siste børsdag i dataene, eller dagen du valgte.",
            ((PRD, "| Sluttkurs | `close` for siste børsdag |"), (AKSJE_MAL, "{{ detalj.dato|dato }}")),
        ),
        # Story 2.7b: historikken nederst paa aksjesiden.
        "historikken": Hjelpetekst(
            "Signalet dag for dag:",
            # Story 8.2b, b (U16): det som er tatt ut av ingressen.
            # Story 8.20a (del E): hoeyst 60 ord. Pilene staar ved maaneden.
            "det appen skrev om aksjen hver børsdag, lest fra basen og aldri regnet på nytt. "
            f"Uka og måneden teller dagene med signalstyrke {terskel} eller mer, og "
            f"{ANTALL_SJEKKER} av {ANTALL_SJEKKER} har ring. "
            "Klikk på en dag med kurs for å se hele siden for den dagen.",
            (
                (AKSJE_MAL, "Signalet dag for dag"),
                (HISTORIKK, "Signalet regnes aldri her"),
                (AKSJE_MAL, "{% if uke.vurdert %}{{ uke.skilte_seg_ut }} av {{ uke.vurdert }}"),
            ),
        ),
        # Svar 32 i 8.0d (rettet kl. 13:05): én tekst for oversikten og
        # aksjesiden, og datoene står bare ved endringen på aksjesiden.
        "endring": Hjelpetekst(
            "Endring:",
            # Story 8.2b, b (U31): datoene står alltid på aksjesiden.
            # Story 8.20a (del J): «kursen justert for utbytte», som grafen.
            "endringen i prosent fra forrige dag med kurs, regnet på "
            "kursen justert for utbytte. På aksjesiden står de to dagene ved "
            "endringen, med ukedag og dato.",
            (
                (PRD, "| Endring | Endring i prosent, regnet på "),
                (MARKEDSOVERSIKT, "def endring_i_prosent("),
                (AKSJE_MAL, "fra {{ detalj.forrige_dato|ukedag }} {{ detalj.forrige_dato|dato }} til"),
            ),
        ),
        # Story 8.20a (del J, spoersmaal 10 i 8.20): tittelen som i grafen.
        "utbyttejustert": Hjelpetekst(
            "Kurs justert for utbytte:",
            "kilden regner kursen om bakover ved hvert nytt utbytte, så et "
            "ordinært utbytte ikke ser ut som et kursfall. Endringen, de "
            f"{ANTALL_SJEKKER} sjekkene og kursgrafen bruker den.",
            (
                (PRD, "#### FR-701"),
                (SIGNALBEREGNING, "Kildens justerte kurs regnes om bakover ved hvert nytt"),
                (AKSJE_MAL, "Begge linjene er tegnet på kursen justert for utbytte"),
            ),
        ),
        "data_hentet": Hjelpetekst(
            # Story 8.0d, PR 2, svar 5: tidspunktet heter «Oppdatert» i stripa.
            "Oppdatert:",
            "når kursene sist ble hentet, i norsk tid. Øverst står det eldste "
            "tidspunktet blant aksjene. En aksje som ble hentet tidligere enn "
            "de nyeste, har sitt eget tidspunkt under navnet.",
            (
                (PRD, "##### Hvor gamle dataene er"),
                (MARKEDSOVERSIKT, "def sidens_tidsstempel("),
                (MARKEDSOVERSIKT, "def eldre_enn_nyeste("),
            ),
        ),
        # Story 8.19 (U60): det som staar bak «Oppdatert …» i den ekte versjonen.
        # Grensen regnes av TIDSGRENSE, som i stripa (grensen_som_tekst).
        "neste_henting": Hjelpetekst(
            "Neste henting:",
            f"i den ekte versjonen står bak tidspunktet når nye kurser tidligst kan hentes, fra "
            f"{grensen_som_tekst()} en børsdag, men ikke om de blir hentet: det avhenger av at appen eller kveldsjobben kjører. "
            "Demoen henter ikke og viser det ikke.",
            (
                (BOERSDAG, "def neste_henting("),
                (MARKEDSOVERSIKT, "def neste_henting_tekst("),
                (APP, "def _neste_henting("),
            ),
        ),
        "data_hentet_aksje": Hjelpetekst(
            "Data hentet:",
            "når kursene for aksjen sist ble hentet, i norsk tid.",
            ((PRD, "##### Hvor gamle dataene er"), (APP, "hentet=post.hentet")),
        ),
        # Story 8.2a, b (U23): en aksje uten kurser har en rad nederst i
        # tabellen, ikke bare navnet under den.
        "uten_data": Hjelpetekst(
            "Uten data:",
            # Gjennomgangen 24.10 (BH7): nederst uten sortering. Sortert på
            # Selskap står den etter navnet.
            "en aksje uten en eneste kurs står nederst i tabellen uten sortering, med «–» i hver kolonne og "
            "«uten data» og med lenke til aksjesiden.",
            (
                # Gjennomgangen 24.10 (BH1): den daterte linja fra 8.2a.
                (PRD, "en aksje uten en eneste kursrad har en rad nederst i tabellen"),
                (MARKEDSOVERSIKT, "def uten_kurser("),
                (MARKEDSOVERSIKT, "class RadUtenData"),
            ),
        ),
        "signalstyrke": Hjelpetekst(
            "Signalstyrke:",
            # Story 8.20a (del J): «Skilte seg ut», som oversikten sier.
            f"hvor mange av de {ANTALL_SJEKKER} sjekkene som slo ut, fra 0 til "
            f"{ANTALL_SJEKKER}. Både +1 og -1 teller, så en sjekk med +1 og en "
            f"med -1 gir 2. Med {terskel} eller mer står aksjen under «Skilte seg ut» i oversikten.",
            (
                (PRD, "#### FR-703 — Signalstyrke"),
                (PRD, "#### FR-705"),
                (SIGNALBEREGNING, "def finn_styrke("),
                (INDEX_MAL, "Skilte seg ut <span"),
            ),
        ),
        # Story 8.20a (del E): det siste i vinduet for signalstyrken paa
        # aksjesiden, som ikke_raad i én setning.
        "ikke_raad_kort": Hjelpetekst(
            "",
            "Signalet er ikke en spådom og ikke et råd.",
            (
                (PRD, "### NFR-06 — Løsningen gir ikke investeringsråd"),
                (BEGRUNNELSER, "Om de sier noe om kursen videre, er ikke målt (FR-703)."),
            ),
        ),
        "uten_styrke": Hjelpetekst(
            "",
            "Står det «–» med en tekst under i stedet for et tall, finnes det "
            "ingen vurdering for dagen, og teksten sier hvorfor. "
            # Story 8.2a, d (gruppens svar 24.10 kl. 11:29): tallene ved en
            # kort kursserie, som på aksjesiden.
            "Er kursserien for kort, står hvor mange dager den har og hvor mange signalet trenger.",
            (
                (PRD, "| Signalstyrke | Tom |"),
                (MARKEDSOVERSIKT, "GRUNNTEKST"),
                (MARKEDSOVERSIKT, "def grunn_med_tall("),
                (MARKEDSOVERSIKT, 'IKKE_VURDERT = "ikke vurdert"'),
                (MARKEDSOVERSIKT, 'IKKE_BOERSDAG = "ikke børsdag"'),
                # Story 2.11: «ikke i lista» etter at aksjen gikk ut.
                (MARKEDSOVERSIKT, 'IKKE_I_LISTA = "ikke i lista"'),
            ),
        ),
        "retning": Hjelpetekst(
            "",
            "Retningen sier om sjekkene som slo ut, ga +1 eller -1, ikke hvor kursen går videre.",
            ((PRD, "#### FR-103"), (BEGRUNNELSER, "Om de sier noe om kursen videre, er ikke målt (FR-703).")),
        ),
        **{
            noekkel: Hjelpetekst(
                _retningstittel(retning),
                _RETNINGSBETINGELSE[retning],
                ((PRD, "#### FR-704 — Retning"), (MARKEDSOVERSIKT, "_SYMBOL_OG_KLASSE")),
            )
            for noekkel, retning in (
                ("positiv", POSITIV),
                ("negativ", NEGATIV),
                ("blandet", BLANDET),
                ("ingen", INGEN),
            )
        },
        "ukjent": Hjelpetekst(
            f"{UKJENT_RETNING.symbol} {UKJENT_RETNING.tekst}:",
            f"det finnes ingen vurdering for dagen, og grunnen står under "
            f"signalstyrken. Det er ikke en femte retning: «{INGEN}» betyr at "
            f"sjekkene ble regnet uten at noen slo ut.",
            ((PRD, "«Ukjent» er ikke en femte retning i FR-704"), (MARKEDSOVERSIKT, "UKJENT_RETNING")),
        ),
        # Story 8.20a (del E): vinduet for retningen paa aksjesiden, med
        # betingelsene kort, som i utkastet i spesifikasjonen for 8.20, og én
        # setning om hvorfor retningen oftere er positiv (gruppens svar 07.11
        # kl. 10:33, 2). Maalingen og grensene staar i docs/hjelp.md.
        "retning_aksje": Hjelpetekst(
            "Retning:",
            "om de sjekkene som slo ut, ga +1 eller -1, ikke hvor kursen går videre.",
            ((PRD, "#### FR-103"), (BEGRUNNELSER, "Om de sier noe om kursen videre, er ikke målt (FR-703).")),
        ),
        **{
            noekkel: Hjelpetekst(
                _retningstittel(retning),
                betingelse,
                ((PRD, "#### FR-704 — Retning"), (MARKEDSOVERSIKT, "_SYMBOL_OG_KLASSE")),
            )
            for noekkel, retning, betingelse in (
                ("positiv_aksje", POSITIV, "alle ga +1."),
                ("negativ_aksje", NEGATIV, "alle ga -1."),
                ("blandet_aksje", BLANDET, "noen +1 og noen -1."),
                ("ingen_aksje", INGEN, "ingen slo ut."),
            )
        },
        "ukjent_aksje": Hjelpetekst(
            f"{UKJENT_RETNING.symbol} {UKJENT_RETNING.tekst}:",
            # Gjennomgangen av 8.20a (BH1): at det ikke er en femte retning, staar i
            # docs/hjelp.md, «Hvorfor står det «ikke vurdert»?», fordi vinduet har 60 ord.
            "ingen vurdering for dagen, og grunnen står under kortene.",
            ((PRD, "«Ukjent» er ikke en femte retning i FR-704"), (AKSJE_MAL, '<p class="mangler">')),
        ),
        "oftere_positiv": Hjelpetekst(
            "",
            "Når kursene stiger, er retningen oftere positiv, fordi trenden kan vare i uker.",
            (
                (BEGRUNNELSER, "### Åpent punkt: skjevfordeling mot positiv retning"),
                (BEGRUNNELSER, "Det er en tilstand, som kan vare i uker."),
            ),
        ),
        "trend": Hjelpetekst(
            "Trend:",
            # Story 8.20a (del J): «kursen justert for utbytte».
            f"ligger kursen justert for utbytte mer enn {sone} over eller "
            f"under snittet av de siste {ma} børsdagene? Over gir +1, under "
            f"gir -1, og innenfor {sone} gir 0.",
            ((PRD, "#### FR-701"), (PRD, "#### FR-702"), (SIGNALBEREGNING, "def trend(")),
        ),
        "bevegelse": Hjelpetekst(
            "Bevegelse:",
            f"endringen fra børsdagen før, mot de vanlige svingningene de "
            f"{volatilitet} børsdagene før. Slår ut over 1 standardavvik: +1 når "
            f"kursen steg, -1 når den falt. Måles mot hvor mye akkurat denne "
            f"aksjen pleier å svinge.",
            (
                (PRD, "#### FR-701"),
                (SIGNALBEREGNING, "def bevegelse("),
                (BEGRUNNELSER, "så en rolig og en urolig aksje måles hver på sitt"),
            ),
        ),
        "interesse": Hjelpetekst(
            "Interesse:",
            f"volumet mot medianvolumet de {volum} børsdagene før. Slår ut over "
            f"{faktor} ganger medianen. Volum har ingen retning i seg selv, så "
            f"fortegnet følger dagens kursendring: +1 en dag kursen steg, -1 "
            f"en dag den falt, og 0 når kursen var uendret.",
            ((PRD, "#### FR-701"), (SIGNALBEREGNING, "def interesse(")),
        ),
        # Story 8.20a (del E, spoersmaal 2 i 8.20): «Ga», «Målt mot» og summen
        # forklares i vinduet ved «Hvorfor signalet ble …». Teksten om
        # grensene og maalingen staar i docs/hjelp.md, «Hvordan ble grensene
        # valgt?», med hvorfor det er disse tre sjekkene.
        "sjekkene": Hjelpetekst(
            "Hvorfor signalet ble:",
            f"{ANTALL_SJEKKER} sjekker, hver på sin del av dataene: kursnivå, endring og volum. "
            "«Ga» er det sjekken ga: +1, 0 eller -1, og «Målt mot» er tallet sjekken ble avgjort av, "
            "med prikken mot feltet der sjekken gir 0. Summen teller sjekkene som slo ut, uten vekting.",
            (
                (BEGRUNNELSER, "### Hvorfor akkurat disse tre sjekkene (FR-701)"),
                (PRD, "#### FR-706"),
                (AKSJE_MAL, '<span class="ga">Ga'),
                (AKSJE_MAL, '<p class="maalt">Målt mot'),
                (AKSJEDETALJ, "def bygg_skala("),
                (SIGNALBEREGNING, "def finn_styrke("),
            ),
        ),
        # Story 8.20a (del E): uten sjekker paa siden, naar signalet ikke
        # kunne regnes, sier vinduet ikke «Ga» og «Målt mot», men hvor mange
        # dager signalet trenger (gjennomgangen av 8.0b).
        "sjekkene_uten": Hjelpetekst(
            "Hvorfor signalet ble:",
            f"{ANTALL_SJEKKER} sjekker, hver på sin del av dataene: kursnivå, endring og volum. "
            f"Signalet trenger {dager} børsdager med kurser, og når det ikke kunne regnes, står grunnen "
            "under overskriften.",
            (
                (BEGRUNNELSER, "### Hvorfor akkurat disse tre sjekkene (FR-701)"),
                (PRD, "Signalet krever 51 handelsdager"),
                (SIGNALBEREGNING, "def nodvendige_dager("),
                (AKSJE_MAL, '<p class="mangler">'),
            ),
        ),
        # Story 8.20a (del E): én tekst om grafen, med snittet bare naar det
        # vises. Navnene staar ved linjene, saa teksten sier dem ikke.
        "grafen": Hjelpetekst(
            "Kursutvikling:",
            f"den tykke linja er kursen justert for utbytte, og den tynne snittet av de siste {ma} "
            "børsdagene, som trenden måler mot.",
            (
                (AKSJE_MAL, '"Kurs (justert for utbytte)"'),
                (AKSJEDETALJ, "glidende_snitt(kurser, p.ma_vindu)"),
            ),
        ),
        "grafen_uten_snitt": Hjelpetekst(
            "Kursutvikling:",
            "den tykke linja er kursen justert for utbytte.",
            ((AKSJE_MAL, '"Kurs (justert for utbytte)"'),),
        ),
        # Story 8.17a: periodevalget i oversikten, med søylene og linja.
        "perioden_oversikten": Hjelpetekst(
            "Periodene:",
            "knappene viser siste børsdag, endringen fra den første kursen i perioden til siste "
            "børsdag, eller en dag du velger, med signalet som er lagret for den. Ved en periode "
            "gjelder sluttkursen og signalet siste børsdag, og «fra» med en dato står under "
            "endringen når kursserien begynner senere. Søylene og den stiplede linja følger samme "
            "periode eller dag, og oransje strek viser 3 av 3 siste børsdag.",
            (
                (PERIODER, "def startdag("),
                (PERIODER, "def foerste_kursdag("),
                (MARKEDSOVERSIKT, "def periodeendring("),
                (MARKEDSOVERSIKT, "def bygg_rad_for_dag("),
                (HOVEDINDEKS, "def soeylene_for("),
                (INDEX_MAL, "Periode for oversikten"),
            ),
        ),
        # Story 8.17b: «Sammenlign med» i Min liste (beslutningen 08.10 kl. 21:48),
        # «Sammenlign siste børsdag med» fra 8.20c (U101, spørsmål 19 i 8.20).
        "sammenlign_med": Hjelpetekst(
            "Sammenlign siste børsdag med:",
            "knappene er de samme som i oversikten, og øverst i hver rad står alltid siste børsdag. "
            "Med en periode eller en dag du velger, står en linje under hver rad med sluttkursen den "
            "første dagen i perioden eller dagen du valgte, endringen derfra til siste børsdag og "
            "signalet som er lagret for dagen, som aldri regnes på nytt. Oransje strek og «3 av 3» "
            "gjelder siste børsdag.",
            (
                (MARKEDSOVERSIKT, "def bygg_sammenligning("),
                (APP, "def _periodestart("),
                (INDEX_MAL, '"Sammenlign siste børsdag med"'),
            ),
        ),
        # Story 8.17b: periodevalget i børsometeret (gruppens svar 23.10 kl. 12:35, b).
        "perioden_boersometeret": Hjelpetekst(
            "Periodene:",
            # Story 8.20b (U95): teksten fra utkastet i spesifikasjonen for 8.20.
            # Gjennomgangen (BH16): hvor perioden slutter, og at snittet følger den.
            "den første knappen viser siste børsdag, de andre endringen fra den første kursen i "
            "perioden til siste børsdag, i fargen og snittet, og datoen med «Vis dagen» en dag du "
            "velger. Ved en periode er rutene like store, fordi volumet mot vanlig gjelder én dag. "
            "Rammen er signalet siste børsdag.",
            (
                (BOERSOMETER, "def vekt("),
                (MARKEDSOVERSIKT, "def periodeendring("),
                (APP, "def _periodestart("),
                (PERIODE_MAL, 'class="periodevalg"'),
            ),
        ),
        # Story 8.16: periodene i kursgrafen og regelen for startdagen.
        # Story 8.20a (del E): regelen for startdagen staar i docs/hjelp.md,
        # «Hva gjør knappene over hovedindeksen?», og vinduet sier streken,
        # knappene og datoen.
        "perioden": Hjelpetekst(
            "",
            # Gjennomgangen av 8.20a (ECH5): streken staar for seg. At en dag viser
            # signalet som er lagret for den, staar i docs/hjelp.md (BH1).
            "Knappene velger hvor langt tilbake grafen går, og datoen med «Vis dagen» viser hele siden for en dag.",
            (
                (PERIODER, "def startdag("),
                (PERIODE_MAL, 'class="periodevalg"'),
                (AKSJE_MAL, 'class="dagstrek"'),
                # Story 8.16b: hele siden viser dagen, med merket øverst.
                (AKSJE_MAL, 'class="tidligere-dag"'),
            ),
        ),
        # Gjennomgangen av 8.20a (ECH5): streken med datoen, bare naar grafen
        # har den, det vil si ved den foerste knappen og en valgt dag.
        "streken": Hjelpetekst(
            "",
            "Streken med datoen er dagen siden viser.",
            ((AKSJE_MAL, 'class="dagstrek"'), (AKSJE_MAL, 'class="daglapp"')),
        ),
        # Story 2.9c: hovedindeksen som stiplet linje i kursgrafen.
        # Story 8.20a (del E): én setning. Resten staar under grafen.
        "indekslinja": Hjelpetekst(
            "",
            # Gjennomgangen av 8.20a (BH1): forbeholdet fra den lange teksten staar i
            # docs/hjelp.md, fordi vinduet har 60 ord.
            "Den stiplede er hovedindeksen, regnet om så den starter på aksjens kurs.",
            (
                (GRAF, "def indeksverdier("),
                (GRAF, "start.kurs * indeks[p.dato] / indeks[start.dato]"),
                (AKSJE_MAL, 'class="indekslinje"'),
            ),
        ),
        # Story 10.9, del D (spoersmaal 10, svaret 07.11 kl. 08:58): hjelpen
        # ved rammen «Signalet forklart» sier bare hva teksten er, hva
        # modellen fikk, og at tallene er sjekket, i hoeyst 60 ord med
        # tittelen (svaret 06.11 kl. 23:07). Resten staar i docs/hjelp.md.
        # Erstatter «kort fortalt» fra svaret 04.11 kl. 22:23, 3.
        "signalet_forklart": Hjelpetekst(
            "",
            "Først skriver appen hvor lenge signalet har vært slik og hva hovedindeksen, bransjen og lista "
            "gjorde samme dag. Med KI på kommer en tekst fra en språkmodell, merket «Laget av KI», som bare "
            "fikk det appen har regnet ut, som sjekkene og antall dager, aldri kurser, prosenter eller "
            "volumer. Tallene med prikket strek er sjekket før teksten vises.",
            (
                (DAGENE, "def setning_om_dagene("),
                (DAGENE, "def setning_om_samme_dag("),
                (KI_GRUNNLAG, "def ki_grunnlag("),
                (KI_GRUNNLAG, "kurser, volumer, prosenter eller forholdstall, og ingen maalinger"),
                (KI_GRUNNLAG, 'ANTALLENE = ("styrke",)'),
                (MOENSTRENE, "def lag_moenstrene("),
                (KI_VISNING, "def prikkede_tall("),
                (KI_KONTROLL, "def kontroller("),
                (AKSJE_MAL, "Laget av KI."),
            ),
        ),
        # Story 2.12 (utdraget 08.11 §1): hjelpen ved «Dine egne aksjer», med
        # ordene fra utdraget i tre setninger (story 8.0c).
        "dine_egne_aksjer": Hjelpetekst(
            "",
            "Lista kan ha opptil 18 aksjer, og aksjer du følger selv, står i tabellen sammen med de andre, merket "
            "«Egen». En ny aksje hentes ved neste henting om kvelden og bruker da 1 kall om dagen, og fjerner du den før det, "
            "brukes ingen kall; valget lagres på denne maskinen. Signalet er målt på aksjer som omsettes for over "
            "32 MNOK om dagen, og omsettes aksjen mindre, eller er omsetningen ikke målt, merkes den «Utenfor målingen».",
            (
                (VALG, "TAK = 18"),
                (VALG, "GRENSE_MNOK = 32.0"),
                (VALG, "def utenfor_maalingen("),
                (VALG, "def ta_i_bruk("),
            ),
        ),
        # Story 8.22: hjelpen ved «Følg en aksje», med lista, sorteringen og
        # merkene, i tre setninger (story 8.0c). Tillegg 3 (svarene 10.11 kl.
        # 22:44): sorteringen i stedet for forslagene, og at den ikke er en
        # rangering etter kursen (NFR-06).
        "foelg_en_aksje": Hjelpetekst(
            "",
            "Lista har alle aksjene på Oslo Børs som har en bransje og ikke er i lista di, og bransjen er fast "
            "for hver aksje, fra kontrollsjekken 10.11, så du velger den ikke selv. «Mest omsatt først» ordner "
            "etter median omsetning de 3 siste månedene og er ingen rangering etter kursen eller signalet. En "
            "aksje som ikke er målt, står med «ikke målt ennå», og en som omsettes for under 32 MNOK om dagen, "
            "eller ikke er målt, merkes «Utenfor målingen» når du velger den.",
            (
                (FERDIGE_LISTER, "def foelgbare("),
                (FERDIGE_LISTER, "def sorter("),
                (FERDIGE_LISTER, "def bransjen("),
                (VALG, "GRENSE_MNOK = 32.0"),
            ),
        ),
        # Story 10.6 (utdraget 08.11 §3): hjelpen ved «Børsdagen kort
        # fortalt», med ordene fra utdraget i tre setninger, fordi hver
        # hjelpetekst har hoeyst tre (story 8.0c). Utdraget har fem.
        "boersdagen_kort_fortalt": Hjelpetekst(
            "",
            "Et kort sammendrag av børsdagen, skrevet av en språkmodell (KI). Modellen fikk bare det appen "
            "regnet ut: om hovedindeksen steg eller falt, hvor mange aksjer som gjorde det bedre enn indeksen, "
            "hvor mange som skilte seg ut og med hvilken retning, med navnet, styrken og retningen for høyst "
            "fem, hvor mange som steg i hver bransje med minst to aksjer med en endring, bransjen som steg "
            "mest og den som falt mest i snitt, om flere eller færre enn vanlig skilte seg ut, og om "
            "hovedindeksen steg eller falt de siste fem børsdagene, med ukedagen og antallet aksjer i lista, og "
            "ingen prosenter, kurser eller nyheter. "
            "Teksten sjekkes før den vises: tall med prikket strek står i det modellen fikk, og den gir ikke råd.",
            (
                (DAGSGRUNNLAG, "def dagsgrunnlag("),
                (DAGSGRUNNLAG, "Ingen kurs, prosent, volum eller forholdstall"),
                (KI_DAGEN, "def kontroller_dagen("),
                (KI_VISNING, "def bygg_dagsvisning("),
                (KI_VISNING, "def prikkede_tall("),
            ),
        ),
        "ikke_raad": Hjelpetekst(
            "",
            "Signalet er ikke en spådom: om sjekkene sier noe om kursen "
            "videre, er ikke målt. Det er heller ikke et råd om å kjøpe eller "
            "selge.",
            (
                (PRD, "### NFR-06 — Løsningen gir ikke investeringsråd"),
                (BEGRUNNELSER, "Om de sier noe om kursen videre, er ikke målt (FR-703)."),
            ),
        ),
    }
    return tekster


class Hjelp:
    """Oppslaget malene bruker: hjelp.tekst("trend").

    En metode og ikke hjelp["trend"], fordi Jinja gjoer en manglende noekkel i
    [] om til en tom verdi. Her feiler siden i stedet, saa en test ser det.
    """

    def __init__(self, tekster: dict[str, Hjelpetekst]):
        self._tekster = dict(tekster)

    def tekst(self, noekkel: str) -> Hjelpetekst:
        try:
            return self._tekster[noekkel]
        except KeyError:
            raise KeyError(f"Ingen hjelpetekst med nøkkelen {noekkel!r} i hjelpetekster.py") from None


# Story 8.9 (FR-109): «Vis meg rundt», i samme fil som hjelpen (8.0b). Høyst
# 7 steg per side (endringsforslaget 13.10, punkt 4.1). Hvert steg peker på
# en id siden har, og tallene kommer fra Parametre. Stegene om signalstyrken,
# retningen og sjekkene bruker tekstene fra hjelpen over.
MAKS_STEG = 7

# Gjennomgangen av 8.9 (ECH5): stegene om retningen, styrken og sjekkene
# bruker tekstene fra tavla, ordrett fra «Kan tas som de står» i punkt 4.2 i
# endringsforslaget 13.10. Retningen uten den andre setningen, «Ikke et råd om
# å kjøpe eller selge.», som etter merknaden der ikke kan bli en vanlig
# hjelpetekst (RAADSORD).
ENDRINGSFORSLAGET_13_10 = "_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-13.md"
TAVLA_RETNING = "Om sjekkene som slo ut, ga +1 eller -1."
TAVLA_STYRKEN = "Styrken er hvor mange sjekker som slo ut. Ga noen +1 og noen -1, er retningen Blandet."
# Sjekkene uten den siste setningen, «Ingen vekting og ingen skjult formel.»:
# story 8.20a flyttet den fra aksjesiden til hjelpen, og en test krever at den
# ikke står på siden (test_fotnoten_under_summen_er_flyttet_til_hjelpen).
TAVLA_SJEKKENE = "Hver sjekk gir +1, 0 eller -1. Signalstyrken er hvor mange som slo ut."


@dataclass(frozen=True)
class Steg:
    """Ett steg i «Vis meg rundt»: id-en på siden det peker på, et navn og
    en tekst."""

    anker: str
    tittel: str
    tekst: str


def rundturer(p: Parametre = STANDARD) -> dict[str, tuple[Steg, ...]]:
    """Stegene for hver side, med tallene fra p. Nøkkelen er siden, som
    malene gir til makroen i _rundtur.html."""
    ma = _vis(p.ma_vindu, "heltall")
    volatilitet = _vis(p.volatilitet_vindu, "heltall")
    volum = _vis(p.volum_vindu, "heltall")
    faktor = _vis(p.volumfaktor, "faktor")
    terskel = _vis(p.terskel, "heltall")
    styrke = Steg("aksjene", "Signalstyrken", TAVLA_STYRKEN)
    retning = Steg("aksjene", "Retningen", TAVLA_RETNING)
    sider = {
        "oversikt": (
            Steg(
                "velg-dag", "Dagen og perioden", "Knappene og datoen velger hvilken dag eller periode tabellen viser."
            ),
            Steg(
                "hovedindeks-tittel",
                "Hovedindeksen",
                "Søylene viser endringen for hver aksje, og den stiplede linja hovedindeksen.",
            ),
            Steg(
                "aksjene",
                "Tabellen",
                f"Aksjene, med kursen, endringen og signalet. For siste børsdag og uten sortering står de med "
                f"signalstyrke {terskel} eller mer øverst, under «Skilte seg ut».",
            ),
            styrke,
            retning,
            Steg("slik-leser", "Slik leser du tabellen", "Fargene, strekene og merkene forklart."),
        ),
        "min_liste": (
            Steg(
                "aksjene",
                "Aksjene dine",
                "Aksjene du har merket med stjernen ☆, eller alle med «Alle», med de samme kolonnene som i oversikten.",
            ),
            styrke,
            retning,
        ),
        "boersometer": (
            Steg("velg-dag", "Dagen og perioden", "Knappene og datoen velger hvilken dag eller periode rutene viser."),
            Steg(
                "maal-tittel", "Mål mot børsen", "Endringen i hovedindeksen, og hvor mange av aksjene som gikk bedre."
            ),
            Steg("slik-leser", "Slik leser du børsometeret", "Fargene, rammene og størrelsen på rutene forklart."),
            Steg(
                "bransje-1", "Bransjene", "Én rute per aksje, samlet etter bransje. Klikk på en rute for å se aksjen."
            ),
        ),
        "aksje": (
            Steg(
                "noekkeltallene",
                "Nøkkeltallene",
                "Sluttkursen, endringen, signalstyrken og retningen for dagen siden viser.",
            ),
            Steg("sjekkene", "Sjekkene", TAVLA_SJEKKENE),
            Steg(
                "sjekkene",
                "Tallene bak",
                f"Sjekk 1 måler kursen mot {ma}-dagers snitt, sjekk 2 endringen mot standardavviket for "
                f"{volatilitet} dager, og sjekk 3 volumet mot {faktor} × medianen for {volum} dager.",
            ),
            Steg(
                "kursgrafen",
                "Kursgrafen",
                f"Kursen justert for utbytte, med {ma}-dagers snitt og hovedindeksen når serien og indeksen har dem.",
            ),
            Steg(
                "signalet-dag-for-dag",
                # Ikke «Signalet dag for dag»: toppen står før delene, og
                # rekkefølgen på siden leses av overskriftene (test_ki_visning).
                "Dag for dag",
                "Det appen skrev om aksjen hver børsdag, en måned om gangen.",
            ),
        ),
        "innstillinger": (
            Steg("innstillinger-tittel", "Innstillinger", "Valgene her gjelder alle sidene og huskes på maskinen."),
            Steg("hjelp-valget", "Hjelp", "Slår spørsmålstegnene ved overskriftene av og på."),
            Steg("ki-valget", "KI-tekst", "Slår tekstene skrevet av KI av og på."),
        ),
        "folg": (
            Steg(
                "folg-tittel", "Følg en aksje", "Her velger du en aksje fra Oslo Børs som appen skal hente og vurdere."
            ),
            Steg("q", "Søk", "Skriv navnet eller symbolet for å finne aksjen."),
        ),
    }
    # Aksjesiden uten sjekker (signalet kunne ikke regnes, eller dagen er
    # ikke vurdert): stegene om sjekkene forklarer noe siden ikke viser.
    sider["aksje_uten_sjekker"] = tuple(s for s in sider["aksje"] if s.anker != "sjekkene")
    for side, steg in sider.items():
        assert len(steg) <= MAKS_STEG, side
    return sider


# Story 8.25 (gruppens svar 10.11 kl. 22:59): «Spill av omvisningen» går
# gjennom sidene i denne rekkefølgen, med stegene fra rundturer(). Svaret
# 11.11 kl. 14:33 (spørsmål 7): «Følg en aksje» etter Min liste, når del B
# (8.22) er flettet.
OMVISNINGEN_SIDER = ("oversikt", "aksje", "boersometer", "min_liste", "folg", "innstillinger")


def omvisningen(p: Parametre = STANDARD) -> list[dict[str, str]]:
    """Stegene i omvisningen, i rekkefølgen sidene står i OMVISNINGEN_SIDER,
    med de samme tekstene som «Vis meg rundt». Skriptet i hjelp.js leser dem
    fra rammen."""
    sider = rundturer(p)
    return [
        {"side": side, "anker": s.anker, "tittel": s.tittel, "tekst": s.tekst}
        for side in OMVISNINGEN_SIDER
        for s in sider[side]
    ]
