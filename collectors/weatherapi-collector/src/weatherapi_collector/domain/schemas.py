import datetime as dt
from pydantic import BaseModel, Field

__all__ = [
    "CurrentWeatherJSONCollectorIn",
    "CurrentWeatherJSONCollectorOut",
    "ForecastJSONCollectorIn",
    "ForecastJSONCollectorOut",
]


class CurrentWeatherJSONCollectorIn(BaseModel):
    """Current weather request in raw JSON format.

    Attributes:
      current_weather_json (dict): The ccurrent weather in JSON format.

    """

    current_weather_json: dict

    retain: bool = Field(default=True)


class CurrentWeatherJSONCollectorOut(CurrentWeatherJSONCollectorIn):
    """Current weather in JSON format, retrieved from database.

    Attributes:
      id (int): The ID of the current weather response.
      created_at (datetime): The creation date of the current weather response.

    """

    id: int

    created_at: dt.datetime
    retain: bool = Field(default=True)


class ForecastJSONCollectorIn(BaseModel):
    """Weather forecast in JSON format.

    Attributes:
        forecast_json (dict): The forecast in JSON format.

    """

    forecast_json: dict
    retain: bool = Field(default=True)


class ForecastJSONCollectorOut(ForecastJSONCollectorIn):
    """Weather forecast in JSON format, retrieved from database.

    Attributes:
        id (int): The ID of the forecast.
        created_at (datetime): The creation date of the forecast.

    """

    id: int

    created_at: dt.datetime
    retain: bool = Field(default=True)
