## Base layer
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

## Build layer: shared package
FROM base AS build-shared

WORKDIR /app

COPY shared/ ./shared/
COPY shared/requirements.txt ./shared/requirements.txt

## Install shared package in container environment
RUN pip install -e ./shared

## Build layer: weatherapi-collector package
FROM build-shared AS build-weatherapi

WORKDIR /app

COPY collectors/weatherapi-collector/requirements.txt ./collectors/weatherapi-collector/requirements.txt

## Install weatherapi-collector package in container environment
RUN pip install -r ./collectors/weatherapi-collector/requirements.txt
COPY collectors/weatherapi-collector/src/ ./collectors/weatherapi-collector/src/

## Runtime layer
FROM python:3.12-slim AS run

WORKDIR /app

## Copy Python site-packages & bins from build layer
COPY --from=build-weatherapi /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build-weatherapi /usr/local/bin /usr/local/bin

## Copy source dirs for packages
COPY shared/src/ ./shared/src/
COPY collectors/weatherapi-collector/src/ ./collectors/weatherapi-collector/src/

## Add build apps to path
ENV PYTHONPATH=/app/shared/src:/app/collectors/weatherapi-collector/src

CMD ["python3", "-m", "weatherapi_collector"]
