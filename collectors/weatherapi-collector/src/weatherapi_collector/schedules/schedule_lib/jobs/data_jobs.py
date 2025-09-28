import typing as t

from shared.domain.weatherapi.weather import (
    ForecastJSONModel,
    ForecastJSONIn,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONIn,
)
from weatherapi_collector.depends import get_db_engine
from weatherapi_collector import db_client
from weatherapi_collector import client as weatherapi_client

from loguru import logger as log
import sqlalchemy as sa


__all__ = ["job_post_weather_readings"]


def job_post_weather_readings(engine: t.Optional[sa.Engine] = None):
    pass
