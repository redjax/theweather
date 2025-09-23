from shared.domain.weatherapi.weather import (
    CurrentWeatherJSONIn,
    ForecastJSONIn,
)
from pydantic import BaseModel, Field

__all__ = [
    "CurrentWeatherJSONCollectorIn",
    "CurrentWeatherJSONCollectorOut",
    "ForecastJSONCollectorIn",
    "ForecastJSONCollectorOut",
]


class CurrentWeatherJSONCollectorIn(CurrentWeatherJSONIn):
    retain: bool = Field(default=True)


class CurrentWeatherJSONCollectorOut(CurrentWeatherJSONIn):
    id: int


class ForecastJSONCollectorIn(ForecastJSONIn):
    retain: bool = Field(default=True)


class ForecastJSONCollectorOut(ForecastJSONIn):
    id: int
