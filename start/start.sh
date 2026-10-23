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

vent_paa_enter() {
    if [ "$SVAR_JA" != "1" ]; then
        read -r -p "Trykk Enter for å lukke vinduet. " _
    fi
}

stopp() {
    echo
    echo "Noe gikk galt: $1"
    echo "Se «Står du fast?» i README-en, eller docs/hjelp.md. Du kan starte på nytt med et nytt dobbeltklikk."
    vent_paa_enter
    exit 1
}

svarer() {
    curl -fsS --max-time 2 -o /dev/null "$ADRESSE/" 2>/dev/null
}

aapne() {
    if [ "$UTEN_NETTLESER" != "1" ]; then
        open "$1" 2>/dev/null || xdg-open "$1" 2>/dev/null || true
    fi
}

# Til mappa skriptet ligger i, uansett hvor det ble startet fra.
cd "$(dirname "$0")/.." || stopp "fant ikke mappa til appen."

if [ "$VERSJON" = "demo" ]; then
    echo "OSE Signal: demoen, med oppdiktede selskaper og kurser."
else
    echo "OSE Signal: den ekte versjonen, med kurser fra EODHD."
fi
echo "Stopp appen ved å lukke dette vinduet, eller med Ctrl+C."
echo

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
        *) stopp "uv er ikke installert. Installer uv slik «Tester» i README-en sier, og start på nytt." ;;
    esac
    curl -LsSf https://astral.sh/uv/install.sh | sh || stopp "installasjonen av uv feilet."
    PATH="$HOME/.local/bin:$PATH"
    command -v uv >/dev/null 2>&1 || stopp "uv ble ikke funnet etter installasjonen. Lukk vinduet og start på nytt."
fi

if svarer; then
    stopp "noe svarer allerede på $ADRESSE. Stopp det først, for eksempel demoen i Docker med docker compose --profile demo down."
fi

echo "Installerer pakkene (uv sync). Første gang tar det noen minutter."
uv sync || stopp "uv sync feilet. Sjekk at maskinen er koblet til nettet."

if [ "$VERSJON" = "demo" ]; then
    echo "Lager demobasen."
    uv run python src/demo.py || stopp "demobasen kunne ikke lages."
    export OSE_DEMO=1
else
    unset OSE_DEMO
    [ -f .env ] || cp .env.example .env
    if ! grep -q '^EODHD_API_KEY=[^[:space:]]' .env; then
        echo "Første gang trenger den ekte versjonen en nøkkel fra EODHD. Registreringssiden åpnes nå."
        echo "Lag en gratis konto, kopier nøkkelen (API key), og lim den inn her."
        aapne "https://eodhd.com/register"
        read -r -s -p "Lim inn nøkkelen og trykk Enter (den vises ikke): " noekkel
        echo
        noekkel="$(printf '%s' "$noekkel" | tr -d '[:space:]')"
        [ -n "$noekkel" ] || stopp "ingen nøkkel ble limt inn."
        grep -v '^EODHD_API_KEY=' .env > .env.ny
        printf 'EODHD_API_KEY=%s\n' "$noekkel" >> .env.ny
        mv .env.ny .env
        unset noekkel
        echo "Nøkkelen er lagret i .env."
    fi
    echo "Henter kurser. Er alt hentet, brukes ingen kall."
    uv run python src/fetch_prices.py
    kode=$?
    if [ "$kode" != 0 ]; then
        echo "Hentingen gikk ut med kode $kode. Appen starter likevel, med det som er hentet før."
    fi
fi

echo "Starter appen på $ADRESSE."
PYTHONPATH=src uv run waitress-serve --listen=127.0.0.1:8000 app:app &
server=$!
trap 'kill "$server" 2>/dev/null' EXIT INT TERM

klar=0
i=0
while [ $i -lt 120 ]; do
    kill -0 "$server" 2>/dev/null || break
    if svarer; then klar=1; break; fi
    sleep 1
    i=$((i + 1))
done
[ "$klar" = 1 ] || stopp "appen svarte ikke på 127.0.0.1:8000."

echo
echo "Appen kjører på $ADRESSE."
echo "Lukk dette vinduet, eller trykk Ctrl+C, for å stoppe den."
aapne "$ADRESSE"
wait "$server"
