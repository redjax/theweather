from __future__ import annotations

import json
import typing as t

from weatherapi_collector.config import DB_SETTINGS
from weatherapi_collector.domain import (
    ForecastJSONCollectorModel,
    ForecastJSONCollectorOut,
    ForecastJSONCollectorRepository,
    ForecastJSONCollectorIn,
)
from weatherapi_collector.db_client.__methods import (
    get_db_engine,
    get_db_uri,
    get_session_pool,
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
    "get_all_forecast_responses",
]


def _get_engine(echo: bool = False) -> sa.Engine:
    """Get a SQLAlchemy engine using the default DB settings.

    Params:
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        sa.Engine: A SQLAlchemy engine.

    Raises:
        Exception: If there is an error creating the engine, an `Exception` is raised.

    """
    try:
        db_uri = get_db_uri(
            drivername=DB_SETTINGS.get("db_drivername"),
            username=DB_SETTINGS.get("db_username"),
            password=DB_SETTINGS.get("db_password"),
            host=DB_SETTINGS.get("db_host"),
            port=DB_SETTINGS.get("db_port"),
            database=DB_SETTINGS.get("db_database"),
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error constructing database URI. Details: {exc}"
        log.error(msg)

        raise exc

    try:
        engine = get_db_engine(db_uri=db_uri, echo=echo)
    except Exception as exc:
        msg = f"({type(exc)}) Error creating database engine. Details: {exc}"
        log.error(msg)

        raise exc

    return engine


def _get_session_pool(echo: bool = False) -> so.sessionmaker[so.Session]:
    """Get a SQLAlchemy session pool using the provided engine.

    Params:
        engine (sa.Engine): A SQLAlchemy engine.
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        so.sessionmaker[so.Session]: A SQLAlchemy session pool.

    Raises:
        Exception: If there is an error creating the session pool, an `Exception` is raised.

    """
    _engine = _get_engine(echo=echo)

    try:
        session_pool = get_session_pool(_engine)
    except Exception as exc:
        msg = f"({type(exc)}) Error creating database session pool. Details: {exc}"
        log.error(msg)

        raise exc

    return session_pool


def save_forecast(
    forecast_schema: t.Union[ForecastJSONCollectorModel, dict, str],
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
                forecast_json=forecast_schema
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing forecast dict as ForecastJSONIn domain object. Details: {exc}"
            log.error(msg)

            raise exc

    session_pool = _get_session_pool(echo=echo)

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


def count_weather_forecast(echo: bool = False):
    """Return a count of the number of rows in the weather forecast table.

    Params:
        engine (Engine | None, optional): The database engine to use. If None, the default engine is used. Defaults to None.
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        int: The count of the number of rows in the weather forecast table.

    Raises:
        Exception: If there is an error counting the number of rows in the weather forecast table, an `Exception` is raised.

    """
    session_pool = _get_session_pool(echo=echo)

    with session_pool() as session:
        repo = ForecastJSONCollectorRepository(session=session)

        return repo.count()


def get_all_forecast_responses(
    echo: bool = False,
) -> list[ForecastJSONCollectorOut]:
    """Get all weather forecast entries from the database.

    Params:
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        list[ForecastOut]: A list of all weather forecast entries in the database.

    Raises:
        Exception: If there is an error getting all weather forecast entries from the database, an `Exception` is raised.

    """

    SessionLocal = _get_session_pool(echo=echo)

    with SessionLocal() as session:
        repo = ForecastJSONCollectorRepository(session=session)

        all_models = repo.list() or []
        log.debug(f"Found {len(all_models)} weather forecast entries in the database.")

    return all_models
