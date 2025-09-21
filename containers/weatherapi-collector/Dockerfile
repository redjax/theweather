FROM python:3.12-slim

WORKDIR /app

COPY ../../shared/ shared/
COPY ../../collectors/weatherapi-collector/ collectors/weatherapi-collector/

RUN pip install --upgrade pip uv

RUN pip install -e ./shared
RUN pip install -e ./collectors/weatherapi-collector

CMD ["python", "-m", "collectors.weatherapi-collector.main"]
