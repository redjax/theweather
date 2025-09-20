from __future__ import annotations

from decimal import Decimal
import typing as t

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
    "LocationIn",
    "LocationOut",
]

class LocationIn(BaseModel):
    """Location schema.
    
    Attributes:
        name (str): The name of the location.
        region (str): The region of the location.
        country (str): The country of the location.
        lat (Decimal): The latitude of the location.
        lon (Decimal): The longitude of the location.
        tz_id (str): The time zone ID of the location.
        localtime_epoch (int): The local time epoch of the location.
        localtime (str): The local time of the location.

    """
    
    name: str
    region: str
    country: str
    lat: Decimal
    lon: Decimal
    tz_id: str
    localtime_epoch: int
    localtime: str


class LocationOut(LocationIn):
    """Location schema from the database.
    
    Attributes:
        id (int): The ID of the location.

    """

    id: int
