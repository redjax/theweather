## Base layer
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

## Build layer: install dependencies from exported requirements
FROM base AS build

WORKDIR /app

## ## Generated with: uv export --format requirements-txt --no-dev > requirements.txt
COPY servers/api-server/requirements.txt ./

RUN pip install -r requirements.txt

## Copy shared package source and install it
COPY shared/ ./shared/
RUN cd shared && pip install .

## Copy and install API server package
COPY servers/api-server/ ./api-server/
RUN cd api-server && pip install .

## Runtime layer
FROM python:3.12-slim AS runtime

WORKDIR /app

## Copy dependencies from build
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

## Copy API server source for runtime usage if necessary
COPY servers/api-server/ ./api-server/

ENV TZ=Etc/UTC

WORKDIR /app/api-server

## Set the command
CMD ["python3", "-m", "api_server"]
