from shared.db.base import BaseRepository
from shared.domain.weatherapi.weather import (
    CurrentWeatherJSONModel as SharedCurrentWeatherJSONModel,
    ForecastJSONModel as SharedForecastJSONModel,
)

from .models import (
    CurrentWeatherJSONCollectorModel,
    ForecastJSONCollectorModel,
)

import sqlalchemy.orm as so


__all__ = [
    "CurrentWeatherJSONCollectorRepository",
    "ForecastJSONCollectorRepository",
]


class CurrentWeatherJSONCollectorRepository(BaseRepository):
    def __init__(self, session: so.Session):
        ## Override to use your local collector model instead of shared one
        super().__init__(session, CurrentWeatherJSONCollectorModel)


class ForecastJSONCollectorRepository(BaseRepository):
    def __init__(self, session: so.Session):
        ## Override to use your local collector model instead of shared one
        super().__init__(session, ForecastJSONCollectorModel)
