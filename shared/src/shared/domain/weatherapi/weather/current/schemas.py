from __future__ import annotations

from decimal import Decimal
import typing as t
import datetime as dt

from loguru import logger as log
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

__all__ = [
    "CurrentWeatherConditionIn",
    "CurrentWeatherConditionOut",
    "CurrentWeatherAirQualityIn",
    "CurrentWeatherAirQualityOut",
    "CurrentWeatherIn",
    "CurrentWeatherOut",
    "CurrentWeatherJSONIn",
    "CurrentWeatherJSONOut"
]

class CurrentWeatherJSONIn(BaseModel):
    """Current weather request in raw JSON format.
    
    Attributes:
      current_weather_json (dict): The ccurrent weather in JSON format.
    
    """
    
    current_weather_json: dict
    

class CurrentWeatherJSONOut(CurrentWeatherJSONIn):
    """Current weather in JSON format, retrieved from database.
    
    Attributes:
      id (int): The ID of the current weather response.
      created_at (datetime): The creation date of the current weather response.

    """
    
    id: int
    
    created_at: dt.datetime

class CurrentWeatherConditionIn(BaseModel):
    """Current weather condition schema.
    
    Attributes:
        text (str): The text description of the current weather condition.
        icon (str): The icon representing the current weather condition.
        code (int): The code representing the current weather condition.

    """

    text: str
    icon: str
    code: int


class CurrentWeatherConditionOut(CurrentWeatherConditionIn):
    """Current weather condition schema from the database.
    
    Attributes:
        id (int): The unique identifier for the current weather condition.

    """

    id: int


class CurrentWeatherAirQualityIn(BaseModel):
    """Current weather air quality schema.
    
    Attributes:
        co (Decimal): The carbon monoxide concentration in the air.
        no2 (Decimal): The nitrogen dioxide concentration in the air.
        o3 (Decimal): The ozone concentration in the air.
        so2 (Decimal): The sulfur dioxide concentration in the air.
        pm2_5 (Decimal): The particulate matter 2.5 concentration in the air.
        pm10 (Decimal): The particulate matter 10 concentration in the air.
        us_epa_index (int): The United States Environmental Protection Agency index for air quality.
        gb_defra_index (int): The Great Britain Defra index for air quality.

    """
    
    co: Decimal
    no2: Decimal
    o3: Decimal
    so2: Decimal
    pm2_5: Decimal
    pm10: Decimal
    us_epa_index: int = Field(alias="us-epa-index", default=None)
    gb_defra_index: int = Field(alias="gb-defra-index", default=None)


class CurrentWeatherAirQualityOut(CurrentWeatherAirQualityIn):
    """Current weather air quality schema from the database.
    
    Attributes:
        id (int): The unique identifier for the current weather air quality.

    """
    
    id: int


class CurrentWeatherIn(BaseModel):
    """Current weather schema.
    
    Attributes:
        id (int): The unique identifier for the current weather.
        name (str): The name of the location.
        region (str): The region of the location.
        country (str): The country of the location.
        lat (Decimal): The latitude of the location.
        lon (Decimal): The longitude of the location.
        tz_id (str): The time zone ID of the location.
        localtime_epoch (int): The epoch time of the local time in the location.
        localtime (str): The local time in the location.
        last_updated_epoch (int): The epoch time of the last update.
        last_updated (str): The last update time.
        temp_c (Decimal): The temperature in Celsius.
        temp_f (Decimal): The temperature in Fahrenheit.
        is_day (int): The day or night indicator.
        condition (CurrentWeatherConditionIn): The current weather condition.
        wind_mph (Decimal): The wind speed in miles per hour.
        wind_kph (Decimal): The wind speed in kilometers per hour.    
        wind_degree (int): The wind direction in degrees.
        wind_dir (str): The wind direction.
        pressure_mb (Decimal): The pressure in millibars.
        pressure_in (Decimal): The pressure in inches of mercury.
        precip_mm (Decimal): The precipitation in millimeters.
        precip_in (Decimal): The precipitation in inches.
        humidity (int): The humidity percentage.
        cloud (int): The cloud coverage percentage.
        feelslike_c (Decimal): The feels-like temperature in Celsius.
        feelslike_f (Decimal): The feels-like temperature in Fahrenheit.    
        windchill_c (Decimal): The windchill temperature in Celsius.
        windchill_f (Decimal): The windchill temperature in Fahrenheit.
        heatindex_c (Decimal): The heat index temperature in Celsius.
        heatindex_f (Decimal): The heat index temperature in Fahrenheit.
        dewpoint_c (Decimal): The dew point temperature in Celsius.
        dewpoint_f (Decimal): The dew point temperature in Fahrenheit.
        vis_km (Decimal): The visibility in kilometers.
        uv (Decimal): The UV index
        gust_mph (Decimal): The gust speed in miles per hour.
        gust_kph (Decimal): The gust speed in kilometers per hour.
        air_quality (CurrentWeatherAirQualityIn | None): The current weather air quality.

    """
    
    last_updated_epoch: int
    last_updated: str
    temp_c: Decimal
    temp_f: Decimal
    is_day: int
    condition: CurrentWeatherConditionIn
    wind_mph: Decimal
    wind_kph: Decimal
    wind_degree: int
    wind_dir: str
    pressure_mb: Decimal
    pressure_in: Decimal
    precip_mm: Decimal
    precip_in: Decimal
    humidity: int
    cloud: int
    feelslike_c: Decimal
    feelslike_f: Decimal
    windchill_c: Decimal
    windchill_f: Decimal
    heatindex_c: Decimal
    heatindex_f: Decimal
    dewpoint_c: Decimal
    dewpoint_f: Decimal
    vis_km: Decimal
    uv: Decimal
    gust_mph: Decimal
    gust_kph: Decimal
    air_quality: CurrentWeatherAirQualityIn | None = Field(default=None)


class CurrentWeatherOut(CurrentWeatherIn):
    """Current weather schema from database.
    
    Attributes:
        id (int): The unique identifier for the current weather.

    """
    
    id: int