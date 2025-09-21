from __future__ import annotations

import datetime as dt
import typing as t

from shared.db import Base, annotated
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so
from sqlalchemy.types import JSON

__all__ = [
    "ForecastJSONModel",
]


class ForecastJSONModel(Base):
    __tablename__ = "weatherapi_forecast_json"

    id: so.Mapped[annotated.INT_PK]

    ## Automatically generate timestamp on creation
    created_at: so.Mapped[dt.datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=dt.datetime.now,
        nullable=False,
    )

    forecast_json: so.Mapped[dict] = so.mapped_column(JSON)
