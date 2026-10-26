#!/bin/bash
# Story 3.5a: start med dobbeltklikk med uv, uten Docker (gruppens svar
# 23.10 kl. 16:16 og 16:37). Startes av «Start demoen.command» og «Start den
# ekte versjonen.command» i rota, med demo eller ekte. Skrevet for bash 3.2,
# som macOS har.
#
# Webserveren startes med waitress bare på 127.0.0.1:8000, aldri med debug,
# og aldri med src/app.py som skript (den har debug=True). Nøkkelen vises
# aldri og skrives bare til .env.
#
# OSE_START_SVAR_JA=1 svarer ja på spørsmålet om uv og venter ikke på Enter
# (CI). OSE_START_UTEN_NETTLESER=1 åpner ingen nettleser (CI).

set -u

ADRESSE="http://127.0.0.1:8000"
VERSJON="${1:-demo}"
SVAR_JA="${OSE_START_SVAR_JA:-}"
UTEN_NETTLESER="${OSE_START_UTEN_NETTLESER:-}"
# 3.5e: den andre versjonen fra mappa kjører fortsatt mens uv sync går.
ANDRE_VERSJON=""
# Forprøven 24.10 (funn 4): Python skriver æ, ø og å som UTF-8, også når
# utskriften går til en fil.
export PYTHONIOENCODING=utf-8

vent_paa_enter() {
    if [ "$SVAR_JA" != "1" ]; then
        read -r -p "Trykk Enter for å lukke vinduet. " _
    fi
}

stopp() {
    echo
    echo "Noe gikk galt: $1"
    echo "Står det fortsatt fast, er det mer hjelp under «Start med dobbeltklikk» i docs/hjelp.md i mappa."
    vent_paa_enter
    exit 1
}

svarer() {
    curl -fsS --max-time 2 -o /dev/null "$ADRESSE/" 2>/dev/null
}

# Svarer noe på porten, uansett hva (gjennomgangen, BH16 og ECH7). Med
# /dev/tcp i bash, så en manglende curl ikke ser ut som en opptatt port
# (spesifikasjonen 3.5d).
opptatt() {
    (exec 3<>/dev/tcp/127.0.0.1/8000) 2>/dev/null
}

# Forprøven 24.10 (funn 7, gruppens svar kl. 12:04): den andre versjonen av
# OSE Signal kjennes på kommandolinja fra skriptene, med waitress-serve,
# --listen=127.0.0.1:8000 og app:app. Alt annet stoppes aldri.
er_ose_signal() {
    case " $1 " in *" --listen=127.0.0.1:8000 "*) ;; *) return 1 ;; esac
    case " $1 " in *" app:app "*) ;; *) return 1 ;; esac
    # Gjennomgangen av 3.5d (BH3, ECH2): bare waitress-serve fra .venv i denne
    # mappa, så en annen app med app:app på porten aldri stoppes.
    for mappe in "$(pwd -P)" "$PWD"; do
        case " $1 " in *" $mappe/.venv/bin/waitress-serve "*) return 0 ;; esac
    done
    return 1
}

# Prosessene som lytter på port 8000. Uten lsof er de ukjente.
lyttere() {
    lsof_sti="$(command -v lsof 2>/dev/null)"
    [ -n "$lsof_sti" ] || { [ -x /usr/sbin/lsof ] && lsof_sti=/usr/sbin/lsof; }
    [ -n "$lsof_sti" ] || return 0
    "$lsof_sti" -nP -iTCP:8000 -sTCP:LISTEN -t 2>/dev/null | sort -u
}

# Gruppens svar 24.10 kl. 20:00 (3.5e): før uv sjekkes porten, og et annet
# program stopper skriptet der. Den andre versjonen fra mappa stoppes først
# rett før webserveren, med stopp som argument, så den kjører videre hvis skriptet stopper før det, for eksempel fordi uv eller
# uv sync feiler. Feiler hentingen, starter appen likevel, og da stoppes den.
frigjoer_porten() {
    opptatt || return 0
    ider="$(lyttere)"
    # Gjennomgangen av 3.5d (ECH4): lytteren stoppet av seg selv i mellomtiden.
    if [ -z "$ider" ] && ! opptatt; then return 0; fi
    fremmede=""
    for id in $ider; do
        if ! er_ose_signal "$(ps -p "$id" -o command= 2>/dev/null)"; then
            navn="$(ps -p "$id" -o comm= 2>/dev/null)"
            # Gjennomgangen av 3.5d (BH7): prosessen er borte, eller er en annen brukers.
            [ -n "$navn" ] || navn="et program skriptet ikke fant navnet på"
            fremmede="$fremmede, ${navn##*/} (prosess $id)"
        fi
    done
    if [ -z "$ider" ] || [ -n "$fremmede" ]; then
        hvem="${fremmede#, }"
        [ -n "$hvem" ] || hvem="et program skriptet ikke fant navnet på"
        stopp "et annet program svarer allerede på $ADRESSE, og det er ikke OSE Signal fra denne mappa. Programmet er $hvem. Skriptet stopper aldri andre programmer. Er det demoen eller appen i Docker, stopper du den med docker compose --profile demo down i et terminalvindu i mappa med koden. Ellers lukker du programmet. Dobbeltklikk så på nytt."
    fi
    if [ "${1:-}" != "stopp" ]; then
        prosesser="$(echo $ider)"
        echo "Den andre versjonen av OSE Signal kjører allerede på $ADRESSE (prosess ${prosesser// /, }). Den stoppes rett før denne starter appen, så den kjører videre hvis skriptet stopper før det."
        ANDRE_VERSJON=1
        return 0
    fi
    for id in $ider; do
        echo "Den andre versjonen av OSE Signal kjører allerede på $ADRESSE (prosess $id). Den stoppes nå, så denne kan starte."
        kill "$id" 2>/dev/null
    done
    i=0
    while opptatt && [ $i -lt 30 ]; do
        sleep 1
        i=$((i + 1))
    done
    if opptatt; then
        stopp "porten $ADRESSE ble ikke ledig etter 30 sekunder. Lukk vinduet der den andre versjonen kjører, og dobbeltklikk på nytt."
    fi
    echo "Den andre versjonen er stoppet, og porten er ledig."
}

aapne() {
    if [ "$UTEN_NETTLESER" != "1" ]; then
        open "$1" 2>/dev/null || xdg-open "$1" 2>/dev/null || true
    fi
}

# Til mappa skriptet ligger i, uansett hvor det ble startet fra.
cd "$(dirname "$0")/.." || stopp "fant ikke mappa til appen. Pakk ut ZIP-fila på nytt, og dobbeltklikk på nytt."

if [ "$VERSJON" = "demo" ]; then
    echo "OSE Signal: demoen, med oppdiktede selskaper og kurser."
else
    echo "OSE Signal: den ekte versjonen, med kurser fra EODHD."
fi
echo "Vinduet må være åpent mens appen kjører. Stopp appen ved å lukke vinduet, eller med Ctrl+C."
echo

# Gruppens svar 23.10 kl. 23:31 (b): i en mappe med .git, en klon, stopper
# den ekte versjonen før uv, .env og hentingen, også på main, så et
# dobbeltklikk i en klon aldri henter med gruppens nøkkel. En ZIP-fil har
# ingen .git. Erstatter vernet «bare fra main» (VG1 og ECH9).
if [ "$VERSJON" = "ekte" ] && [ -e .git ]; then
    stopp "mappa har .git (en klon av repoet eller et eget git-repo), og der starter ikke den ekte versjonen. Last ned en egen kopi med «Download ZIP» på GitHub, pakk den ut, og bruk din egen nøkkel fra EODHD. Demoen kan startes herfra."
fi

# Porten før uv og hentingen (forprøven 24.10, funn 7): et annet program
# stopper skriptet her. Den andre versjonen stoppes rett før webserveren (3.5e).
frigjoer_porten sjekk

# uv: på PATH, i .local/bin i brukermappa, eller installert etter et ja.
if ! command -v uv >/dev/null 2>&1 && [ -x "$HOME/.local/bin/uv" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi
if ! command -v uv >/dev/null 2>&1; then
    echo "Appen trenger uv, som installerer Python og pakkene appen bruker."
    echo "uv er ikke installert. Den offisielle installasjonen fra astral.sh legger den i brukermappa di."
    if [ "$SVAR_JA" = "1" ]; then
        svar="j"
    else
        read -r -p "Installere uv nå? Skriv j og trykk Enter for ja: " svar
    fi
    case "$svar" in
        j|J|ja|Ja|JA|y|Y|yes) ;;
        *) stopp "uv er ikke installert, og appen kan ikke starte uten. Dobbeltklikk på nytt, og skriv j og trykk Enter når vinduet spør om uv." ;;
    esac
    curl -LsSf https://astral.sh/uv/install.sh | sh || stopp "installasjonen av uv feilet. Sjekk at maskinen er koblet til nettet, og dobbeltklikk på nytt."
    PATH="$HOME/.local/bin:$PATH"
    command -v uv >/dev/null 2>&1 || stopp "uv ble ikke funnet etter installasjonen. Lukk vinduet og dobbeltklikk på nytt."
fi

echo "Installerer pakkene (uv sync). Første gang tar det noen minutter."
uv sync
if [ $? != 0 ]; then
    # Gjennomgangen av 3.5e (BH, ECH): den andre versjonen kan holde filer i
    # .venv åpne, og da er nettet feil grunn.
    [ -z "$ANDRE_VERSJON" ] || stopp "uv sync feilet. Den andre versjonen av OSE Signal kjører fra denne mappa og kan holde filene i .venv åpne. Lukk vinduet der den kjører, og dobbeltklikk på nytt."
    stopp "uv sync feilet. Sjekk at maskinen er koblet til nettet, og dobbeltklikk på nytt."
fi

if [ "$VERSJON" = "demo" ]; then
    echo "Lager demobasen."
    uv run python src/demo.py || stopp "demobasen kunne ikke lages. Grunnen står i linjene over. Lukk andre vinduer der demoen kjører, og dobbeltklikk på nytt."
    export OSE_DEMO=1
else
    unset OSE_DEMO
    [ -f .env ] || cp .env.example .env
    if ! grep -q '^EODHD_API_KEY=[^[:space:]]' .env; then
        echo "Første gang trenger den ekte versjonen en nøkkel fra EODHD. Registreringssiden åpnes nå."
        # Forprøven 24.10 (funn 1–3): hvor nøkkelen står, og hvordan den limes inn.
        echo "Lag en gratis konto. Nøkkelen står som «API token» under «Dashboard» hos EODHD, med kopiknappen til høyre."
        echo "Lim den inn her med Cmd+V. Den vises ikke mens du limer inn, men den kommer med."
        aapne "https://eodhd.com/register"
        read -r -s -p "Lim inn nøkkelen og trykk Enter: " noekkel
        echo
        noekkel="${noekkel//[[:space:]]/}"
        [ -n "$noekkel" ] || stopp "ingen nøkkel ble limt inn. Dobbeltklikk på nytt, og lim inn nøkkelen når vinduet spør."
        # Bare eieren kan lese .env.ny, som blir .env (gjennomgangen, BH6).
        (umask 077 && grep -v '^EODHD_API_KEY=' .env > .env.ny)
        printf 'EODHD_API_KEY=%s\n' "$noekkel" >> .env.ny
        mv .env.ny .env
        unset noekkel
        echo "Nøkkelen er lagret i .env."
    fi
    echo "Henter kurser. Er alt hentet, brukes ingen kall."
    uv run python src/fetch_prices.py
    kode=$?
    if [ "$kode" != 0 ]; then
        echo "Hentingen gikk ut med kode $kode. Grunnen står i linjene over. Appen starter likevel, med det som er hentet før."
        echo "Er nøkkelen feil, sletter du det som står etter EODHD_API_KEY= i .env, så spør vinduet etter den på nytt neste gang."
    fi
fi

# 3.5e: den andre versjonen stoppes først nå. Svarer et annet program på
# porten nå, stoppes det ikke, og vinduet sier hva man gjør.
frigjoer_porten stopp

echo "Starter appen på $ADRESSE."
# Forprøven 24.10 (funn 6): 8 tråder, så waitress ikke skriver «Task queue depth».
PYTHONPATH=src uv run waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app &
server=$!
trap 'kill "$server" 2>/dev/null' EXIT
# Gjennomgangen (BH5, ECH8): Ctrl+C og et lukket vindu stopper også skriptet.
trap 'exit 130' INT TERM HUP

klar=0
i=0
while [ $i -lt 120 ]; do
    kill -0 "$server" 2>/dev/null || break
    if svarer; then klar=1; break; fi
    sleep 1
    i=$((i + 1))
done
[ "$klar" = 1 ] || stopp "appen svarte ikke på 127.0.0.1:8000 etter 2 minutter. Grunnen står i linjene over. Lukk vinduet og dobbeltklikk på nytt."

echo
echo "Appen kjører på $ADRESSE."
echo "Lukk dette vinduet, eller trykk Ctrl+C, for å stoppe den."
aapne "$ADRESSE"
wait "$server"
kode=$?
# Gjennomgangen (BH2, VG2): stopper appen av seg selv, står beskjeden.
[ "$kode" = 0 ] || stopp "appen stoppet med kode $kode. Startet du demoen eller den ekte versjonen i et annet vindu, er det den som kjører nå, og dette vinduet kan lukkes. Ellers står grunnen i linjene over: lukk vinduet og dobbeltklikk på nytt."
