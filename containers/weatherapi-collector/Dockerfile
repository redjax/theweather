# Base layer: python slim image with build dependencies installed
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip


# Build layer: install dependencies for shared and weatherapi-collector
FROM base AS build

WORKDIR /app

# Copy shared source and requirements first
COPY shared/ ./shared/
COPY shared/requirements.txt ./shared/requirements.txt

# Install shared package (editable) so it is available for weatherapi-collector
RUN pip install -e ./shared

# Copy weatherapi-collector requirements next
COPY collectors/weatherapi-collector/requirements.txt ./collectors/weatherapi-collector/requirements.txt

# Install weatherapi-collector dependencies (which references shared)
RUN pip install -r ./collectors/weatherapi-collector/requirements.txt

# Copy weatherapi-collector source last
COPY collectors/weatherapi-collector/src/ ./collectors/weatherapi-collector/src/


# Run layer: final slim image with only runtime and your packages
FROM python:3.12-slim AS run

WORKDIR /app

# Copy installed packages from build layer
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application source for runtime
COPY shared/src/ ./shared/src/
COPY collectors/weatherapi-collector/src/ ./collectors/weatherapi-collector/src/

ENV PYTHONPATH=/app/shared/src:/app/collectors/weatherapi-collector/src

CMD ["python3", "-m", "weatherapi_collector"]
