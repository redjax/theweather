from __future__ import annotations

import json
import typing as t

from shared import db
from weatherapi_collector.depends import db_depends
from weatherapi_collector.domain import (
    ForecastJSONCollectorModel,
    ForecastJSONCollectorOut,
    ForecastJSONCollectorRepository,
    ForecastJSONCollectorIn,
)
from loguru import logger as log

# from domain.weatherapi import location as domain_location
# from weather_client.apis.api_weatherapi.db_client.location import save_location
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = [
    "save_forecast",
    "count_weather_forecast",
]


def save_forecast(
    forecast_schema: t.Union[ForecastJSONCollectorModel, dict, str],
    engine: sa.Engine | None = None,
    echo: bool = False,
) -> ForecastJSONCollectorOut:
    """Save a Forecast (in JSON form) to the database.

    Params:
        forecast (ForecastJSONIn | dict | str): The Forecast to save. Can be a ForecastJSONIn domain object, dict, or JSON string.
        engine (Engine | None): The SQLAlchemy engine to use for the database connection. If None, a new engine will be created.
        echo (bool): Whether to echo SQL statements to the console.

    Returns:
        ForecastJSONOut: The saved Forecast.

    Raises:
        Exception: If Forecast cannot be saved, an `Exception` is raised.

    """
    if not forecast_schema:
        raise ValueError("Missing forecast to save")

    if isinstance(forecast_schema, str):
        try:
            forecast_schema: dict = json.loads(forecast_schema)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing forecast string as JSON. Details: {exc}"
            log.error(msg)

            raise exc

    if isinstance(forecast_schema, dict):
        log.debug(f"Coverting forecast dict to ForecastJSONCollectorIn domain object")
        try:
            forecast_schema: ForecastJSONCollectorIn = ForecastJSONCollectorIn(
                forecast_schema
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing forecast dict as ForecastJSONIn domain object. Details: {exc}"
            log.error(msg)

            raise exc

    if engine is None:
        engine = db_depends.get_db_engine(echo=echo)

    session_pool = db_depends.get_session_pool(engine=engine)

    with session_pool() as session:
        repo = ForecastJSONCollectorRepository(session=session)

        forecast_model = ForecastJSONCollectorModel(**forecast_schema.model_dump())

        try:
            db_forecast = repo.create(forecast_model)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving weather forecast JSON. Details: {exc}"
            log.error(msg)

            raise exc

    try:
        forecast_out: ForecastJSONCollectorOut = (
            ForecastJSONCollectorOut.model_validate(forecast_model.__dict__)
        )

        return forecast_out
    except Exception as exc:
        msg = f"({type(exc)}) Error converting JSON from database to ForecastJSONOut schema. Details: {exc}"
        log.error(msg)

        raise exc


def count_weather_forecast(engine: sa.Engine | None = None, echo: bool = False):
    """Return a count of the number of rows in the weather forecast table.

    Params:
        engine (Engine | None, optional): The database engine to use. If None, the default engine is used. Defaults to None.
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        int: The count of the number of rows in the weather forecast table.

    Raises:
        Exception: If there is an error counting the number of rows in the weather forecast table, an `Exception` is raised.

    """
    if engine is None:
        engine = db_depends.get_db_engine(echo=echo)

    session_pool = db_depends.get_session_pool(engine=engine)

    with session_pool() as session:
        repo = ForecastJSONCollectorRepository(session=session)

        return repo.count()
