from __future__ import annotations

import datetime as dt
import typing as t

from loguru import logger as log
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

__all__ = [
    "ForecastJSONIn",
    "ForecastJSONOut",
]

class ForecastJSONIn(BaseModel):
    """Weather forecast in JSON format.
    
    Attributes:
        forecast_json (dict): The forecast in JSON format.
        
    """
    
    forecast_json: dict


class ForecastJSONOut(ForecastJSONIn):
    """Weather forecast in JSON format, retrieved from database.
    
    Attributes:
        id (int): The ID of the forecast.
        created_at (datetime): The creation date of the forecast.
        
    """
    
    id: int

    created_at: dt.datetime