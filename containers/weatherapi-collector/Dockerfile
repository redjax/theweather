## Base layer
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

## Build layer: Install dependencies from exported requirements
FROM base AS build

WORKDIR /app

## Generated with: uv export --format requirements-txt --no-dev > requirements.txt
COPY collectors/weatherapi-collector/requirements.txt ./

RUN pip install -r requirements.txt

## Copy shared package source and install it
COPY shared/ ./shared/
RUN cd shared && pip install .

## Copy and install weatherapi-collector
COPY collectors/weatherapi-collector/ ./weatherapi-collector/
RUN cd weatherapi-collector && pip install .

## Runtime layer
FROM python:3.12-slim AS runtime

WORKDIR /app

## Copy installed packages from build layer
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

ENV TZ=Etc/UTC

## Set the command
CMD ["python3", "-m", "weatherapi_collector"]
