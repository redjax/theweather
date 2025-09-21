from __future__ import annotations

import datetime as dt
from decimal import Decimal
import typing as t

from shared.db import Base, annotated
from shared.domain.weatherapi.location import WeatherAPILocationModel

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so
from sqlalchemy.types import JSON

__all__ = [
    "CurrentWeatherModel",
    "CurrentWeatherConditionModel",
    "CurrentWeatherAirQualityModel",
    "CurrentWeatherJSONModel",
]


class CurrentWeatherJSONModel(Base):
    __tablename__ = "weatherapi_current_json"

    id: so.Mapped[annotated.INT_PK]

    ## Automatically created when model is created in the database
    created_at: so.Mapped[dt.datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=dt.datetime.now,
        nullable=False,
    )

    ## Raw JSON from a WeatherAPI HTTP request
    current_weather_json: so.Mapped[dict] = so.mapped_column(JSON)


class CurrentWeatherModel(Base):
    """Current weather model.

    Attributes:
        id (int): The ID of the current weather record.
        last_updated_epoch (int): The last updated epoch time.
        last_updated (str): The last updated time.
        temp_c (Decimal): The temperature in Celsius.
        temp_f (Decimal): The temperature in Fahrenheit.
        is_day (int): The day or night indicator.
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
        uv (Decimal): The UV index.
        gust_mph (Decimal): The gust speed in miles per hour.
        gust_kph (Decimal): The gust speed in kilometers per hour.
        air_quality: The air quality model.
        location: The location model.

    Relationships:
        air_quality (CurrentWeatherAirQualityModel): The air quality model.
        location (WeatherAPILocationModel): The location model.

    """

    __tablename__ = "weatherapi_current_weather"
    __table_args__ = (sa.UniqueConstraint("last_updated_epoch"),)
    # __table_args__ = (sa.UniqueConstraint("last_updated_epoch", name="_last_updated_epoch_uc"),)

    id: so.Mapped[annotated.INT_PK]

    last_updated_epoch: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    last_updated: so.Mapped[str] = so.mapped_column(sa.TEXT)
    temp_c: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    temp_f: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    is_day: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    wind_mph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    wind_kph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    wind_degree: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    wind_dir: so.Mapped[str] = so.mapped_column(sa.TEXT)
    pressure_mb: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    pressure_in: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    precip_mm: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    precip_in: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    humidity: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    cloud: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    feelslike_c: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    feelslike_f: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    windchill_c: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    windchill_f: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    heatindex_c: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    heatindex_f: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    dewpoint_c: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    dewpoint_f: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    vis_km: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    uv: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    gust_mph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    gust_kph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))

    condition: so.Mapped["CurrentWeatherConditionModel"] = so.relationship(
        back_populates="weather"
    )
    air_quality: so.Mapped["CurrentWeatherAirQualityModel"] = so.relationship(
        back_populates="weather"
    )

    ## Foreign keys

    ## Relationship back to WeatherAPILocationModel
    location_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("weatherapi_location.id")
    )

    ## Relationship back to WeatherAPILocationModel using a string reference
    location: so.Mapped[WeatherAPILocationModel] = so.relationship(
        WeatherAPILocationModel, back_populates="current_weather_entries"
    )


class CurrentWeatherConditionModel(Base):
    """Current Weather Condition Model.

    Description:
        This model is used to represent the current weather condition of a location.

    Attributes:
        id (int): The unique identifier for the current weather condition.
        text (str): The text description of the current weather condition.
        icon (str): The icon representing the current weather condition.
        code (int): The code representing the current weather condition.
        weather_id (int): The unique identifier of the weather entry associated with the current weather condition.
        weather (CurrentWeatherModel): The weather entry associated with the current weather condition.

    Relationships:
        weather (CurrentWeatherModel): The weather entry associated with the current weather condition.

    """

    __tablename__ = "weatherapi_current_condition"

    id: so.Mapped[annotated.INT_PK]

    text: so.Mapped[str] = so.mapped_column(sa.TEXT)
    icon: so.Mapped[str] = so.mapped_column(sa.TEXT)
    code: so.Mapped[int] = so.mapped_column(sa.NUMERIC)

    ## Foreign keys

    ## Relationship back to CurrentWeatherModel
    weather_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("weatherapi_current_weather.id")
    )

    ## Relationship back to CurrentWeatherModel
    weather: so.Mapped["CurrentWeatherModel"] = so.relationship(
        back_populates="condition"
    )


class CurrentWeatherAirQualityModel(Base):
    """Current Weather Air Quality Model.

    Description:
        This model is used to represent the air quality of a location.

    Attributes:
        id (int): The unique identifier for the air quality.
        co (Decimal): The carbon monoxide concentration in the air.
        no2 (Decimal): The nitrogen dioxide concentration in the air.
        o3 (Decimal): The ozone concentration in the air.
        so2 (Decimal): The sulfur dioxide concentration in the air.
        pm2_5 (Decimal): The particulate matter 2.5 concentration in the air.
        pm10 (Decimal): The particulate matter 10 concentration in the air.
        us_epa_index (int): The United States Environmental Protection Agency index for air quality.
        gb_defra_index (int): The Great Britain Defra index for air quality.
        weather_id (int): The unique identifier of the weather entry associated with the air quality.
        weather (CurrentWeatherModel): The weather entry associated with the air quality.

    Relationships:
        weather (CurrentWeatherModel): The weather entry associated with the air quality.

    """

    __tablename__ = "weatherapi_air_quality"

    id: so.Mapped[annotated.INT_PK]

    co: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    no2: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    o3: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    so2: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    pm2_5: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    pm10: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    us_epa_index: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    gb_defra_index: so.Mapped[int] = so.mapped_column(sa.NUMERIC)

    ## Foreign keys

    ## Relationship back to CurrentWeatherModel
    weather_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("weatherapi_current_weather.id")
    )

    ## Relationship back to CurrentWeatherModel
    weather: so.Mapped["CurrentWeatherModel"] = so.relationship(
        back_populates="air_quality"
    )
