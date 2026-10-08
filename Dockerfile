# OSE Signal - ett image med to innganger (story 3.1, AD-10, AD-17).
#
# Standard er webserveren med waitress paa port 5000. Den gjoer null API-kall
# og starter uten noekkel. Hentingen er et eget valg mot samme image:
#   docker compose run --rm hent
#
# Imaget har aldri data eller noekler (AD-9, AD-12). Basen og
# oeyeblikksbildene ligger i de navngitte volumene ose-db og ose-raa
# (compose.yaml), og migrasjonene kjoeres av aapne_base i begge inngangene,
# ikke i et eget steg (story 2.1b).

# Samme Python 3.13 som CI. Fast versjon, saa en ny bygging gir samme bilde.
FROM python:3.13.15-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.15 /uv /bin/uv

# UV_PYTHON_DOWNLOADS=never: uv bruker Pythonen i grunnbildet og laster aldri
# ned en egen. Uten den kunne et feil grunnbilde gitt et image med en Python
# uv hentet under byggingen (mutanten I5).
ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Avhengighetene fra uv.lock, uten dev-gruppen. --locked stopper byggingen
# hvis uv.lock ikke stemmer med pyproject.toml. tzdata kommer herfra, saa
# Europe/Oslo virker uten tidssonedatabase i bildet (AD-20).
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Bare koden. data/, .env og resten holdes ute av .dockerignore i tillegg.
COPY src/ src/

# En bruker som ikke er root. Mappene eies av den, saa volumene faar riktig
# eier foerste gang de monteres.
RUN useradd --create-home --uid 10001 ose \
    && mkdir -p data/db data/raa \
    && chown -R ose:ose data
USER ose

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/app/src

EXPOSE 5000

# waitress, aldri Flasks egen server og aldri debug. 0.0.0.0 gjelder inne i
# containeren; compose.yaml binder porten bare til 127.0.0.1 paa maskinen.
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "app:app"]
