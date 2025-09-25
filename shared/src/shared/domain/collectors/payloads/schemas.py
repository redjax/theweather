import typing as t

from pydantic import BaseModel, Field

__all__ = ["WeatherCollectorPayloadIn", "WeatherCollectorPayloadOut"]


class WeatherCollectorPayloadIn(BaseModel):
    source: str = Field(
        ..., description="The collector's source, i.e. weatherapi, openmeteo, etc"
    )
    label: str = Field(
        ..., description="Type of data collected, i.e. current, forecast, etc"
    )
    data: dict[str, t.Any] = Field(
        ..., description="Raw weather data payload from the source"
    )


class WeatherCollectorPayloadOut(WeatherCollectorPayloadIn):
    id: int

    class Config:
        orm_mode = True
