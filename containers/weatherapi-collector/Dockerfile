## Base layer
ARG UV_BASE=${UV_IMAGE_VER:-0.6.14}
ARG PYTHON_BASE=${PYTHON_IMG_VER:-3.12-slim}

FROM ghcr.io/astral-sh/uv:${UV_BASE} AS uv
FROM python:${PYTHON_BASE} AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        iputils-ping \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

## Stage layer: Copy files into the container for more efficient caching
FROM base AS stage

WORKDIR /app/collectors

## Copy WeatherAPI collector project files
COPY collectors/weatherapi-collector/pyproject.toml collectors/weatherapi-collector/uv.lock collectors/weatherapi-collector/README.md ./

## Copy WeatherAPI collector files
COPY collectors/weatherapi-collector/ ./weatherapi-collector/

WORKDIR /app/shared

## Copy Shared project files
COPY shared/ ./

## Build layer: Install dependencies from exported requirements
FROM base AS build

COPY --from=stage /app /app
COPY --from=uv /uv /usr/bin/uv

WORKDIR /app/collectors/weatherapi-collector

## Build project in container
RUN uv sync --all-extras \
    && uv build

## Runtime layer
FROM python:${PYTHON_BASE} AS runtime

COPY --from=build /app /app
COPY --from=uv /uv /usr/bin/uv

## Copy installed packages from build layer
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

WORKDIR /app/collectors/weatherapi_collector

## Set the command
CMD ["uv", "run", "weatherapi-collector"]
