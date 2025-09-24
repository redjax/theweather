## Base layer
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

## Build layer: Build shared package wheel
FROM base AS build-shared

WORKDIR /app

# Copy shared package source
COPY shared/ ./shared/

# Build the shared package into a wheel
RUN cd shared && pip install build && python -m build

## Build layer: Build weatherapi-collector package
FROM base AS build-app

WORKDIR /app

# Copy the built shared package wheel from previous stage
COPY --from=build-shared /app/shared/dist/*.whl ./wheels/

# Install the shared package from wheel (no path dependency)
RUN pip install ./wheels/*.whl

# Copy and install weatherapi-collector
COPY collectors/weatherapi-collector/ ./weatherapi-collector/

# Build weatherapi-collector
RUN cd weatherapi-collector && pip install build && python -m build

# Install weatherapi-collector
RUN pip install ./weatherapi-collector/dist/*.whl

## Runtime layer
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from build layer
COPY --from=build-app /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build-app /usr/local/bin /usr/local/bin

# Set the command
CMD ["python3", "-m", "weatherapi_collector"]
