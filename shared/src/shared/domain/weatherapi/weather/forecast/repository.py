from __future__ import annotations

import typing as t

from shared.db.base import BaseRepository

from .models import ForecastJSONModel

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = ["ForecastJSONRepository"]


class ForecastJSONRepository(BaseRepository):
    def __init__(self, session: so.Session):
        super().__init__(session, ForecastJSONModel)
