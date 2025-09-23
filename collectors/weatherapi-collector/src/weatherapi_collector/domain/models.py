import datetime as dt

from weatherapi_collector.db_client.base import Base
from sqlalchemy import Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column

import sqlalchemy as sa

__all__ = [
    "CurrentWeatherJSONCollectorModel",
    "ForecastJSONCollectorModel",
    "LocationJSONCollectorModel",
]


class CurrentWeatherJSONCollectorModel(Base):
    __tablename__ = "current_weather_response"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[dt.datetime]
    current_weather_json: Mapped[dict] = mapped_column(sa.JSON)

    ## Marker for garbage collector, delete when False
    retain: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ForecastJSONCollectorModel(Base):
    __tablename__ = "forecast_response"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[dt.datetime]
    weather_forecast_json: Mapped[dict] = mapped_column(sa.JSON)

    ## Marker for garbage collector, delete when False
    retain: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LocationJSONCollectorModel(Base):
    __tablename__ = "location_response"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[dt.datetime]
    location_json: Mapped[dict] = mapped_column(sa.JSON)

    ## Marker for garbage collector, delete when False
    retain: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
