from __future__ import annotations

import json
import typing as t

from weatherapi_collector.config import DB_SETTINGS
from weatherapi_collector.db_client.__methods import (
    get_db_engine,
    get_db_uri,
    get_session_pool,
)
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorIn,
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
    CurrentWeatherJSONCollectorRepository,
    ForecastJSONCollectorIn,
    ForecastJSONCollectorModel,
    ForecastJSONCollectorOut,
    ForecastJSONCollectorRepository,
)

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = [
    "save_current_weather_response",
    "count_current_weather_responses",
    "get_all_current_weather_responses",
    "set_current_weather_response_retention",
    "vacuum_current_weather_json_responses",
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


def save_current_weather_response(
    current_weather_schema: t.Union[CurrentWeatherJSONCollectorIn, dict, str],
    echo: bool = False,
) -> CurrentWeatherJSONCollectorOut:
    """Save a current weather response (in JSON form) to the database.

    Params:
        current_weather_schema (CurrentWeatherJSONCollectorIn | dict | str): The current weather response to save. Can be a CurrentWeatherJSONCollectorIn domain object, dict, or JSON string.
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        CurrentWeatherJSONCollectorOut: The saved current weather response.

    Raises:
        Exception: If current weather response cannot be saved, an `Exception` is raised.

    """
    if not current_weather_schema:
        raise ValueError("Missing current weather response to save")

    SessionLocal = _get_session_pool(echo=echo)

    if isinstance(current_weather_schema, str):
        try:
            current_weather_schema: dict = json.loads(current_weather_schema)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing current weather response string as JSON. Details: {exc}"
            log.error(msg)

            raise exc

    if isinstance(current_weather_schema, dict):
        try:
            current_weather_schema: CurrentWeatherJSONCollectorIn = (
                CurrentWeatherJSONCollectorIn(
                    current_weather_json=current_weather_schema
                )
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing current weather response dict as CurrentWeatherJSONCollectorIn domain object. Details: {exc}"
            log.error(msg)

            raise exc

    with SessionLocal() as session:
        repo = CurrentWeatherJSONCollectorRepository(session=session)

        current_weather_model = CurrentWeatherJSONCollectorModel(
            **current_weather_schema.model_dump()
        )

        try:
            db_current_weather = repo.create(current_weather_model)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving current weather response JSON. Details: {exc}"
            log.error(msg)

            raise exc

    try:
        current_weather_out: CurrentWeatherJSONCollectorOut = (
            CurrentWeatherJSONCollectorOut.model_validate(
                current_weather_model.__dict__
            )
        )

        return current_weather_out
    except Exception as exc:
        msg = f"({type(exc)}) Error converting JSON from database to CurrentWeatherJSONCollectorOut schema. Details: {exc}"
        log.error(msg)

        raise exc


def count_current_weather_responses(echo: bool = False):
    """Return a count of the number of rows in the current weather table.

    Params:
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        int: The count of the number of rows in the current weather table.

    Raises:
        Exception: If there is an error counting the number of rows in the current weather table, an `Exception` is raised.

    """
    SessionLocal = _get_session_pool(echo=echo)

    with SessionLocal() as session:
        repo = CurrentWeatherJSONCollectorRepository(session=session)

        return repo.count()


def get_all_current_weather_responses(
    echo: bool = False,
) -> list[CurrentWeatherJSONCollectorOut]:
    """Get all current weather entries from the database.

    Params:
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        list[CurrentWeatherOut]: A list of all current weather entries in the database.

    Raises:
        Exception: If there is an error getting all current weather entries from the database, an `Exception` is raised.

    """
    SessionLocal = _get_session_pool(echo=echo)

    with SessionLocal() as session:
        repo = CurrentWeatherJSONCollectorRepository(session=session)

        all_models = repo.list() or []
        log.debug(f"Found {len(all_models)} current weather entries in the database.")

    return all_models


def set_current_weather_response_retention(
    item_id: int,
    retain: bool,
    echo: bool = False,
) -> bool:
    SessionLocal = _get_session_pool(echo=echo)

    with SessionLocal() as session:
        repo = CurrentWeatherJSONCollectorRepository(session=session)

        existing_model: CurrentWeatherJSONCollectorModel | None = repo.get(item_id)
        if not existing_model:
            raise ValueError(f"Current weather entry with ID {item_id} not found.")

        log.debug(
            f"Found current weather entry ID {item_id} with retain={existing_model.retain}."
        )

        if existing_model.retain == retain:
            log.info(
                f"Current weather entry with ID {item_id} already has retain={retain}. No update needed."
            )
            return True

        # existing_model.retain = retain
        repo.update(obj=existing_model, data={"retain": retain})

        log.debug(f"Updated current weather entry ID {item_id} to retain={retain}.")

        return True


def vacuum_current_weather_json_responses(echo: bool = False):
    """Remove records that are marked retain=False from the database.

    Params:
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False
    """
    SessionLocal = _get_session_pool(echo=echo)

    _deleted = []
    _errored = []

    with SessionLocal() as session:
        repo = CurrentWeatherJSONCollectorRepository(session=session)

        all_current_weather_items: list[CurrentWeatherJSONCollectorModel] = repo.list() or []

        if not all_current_weather_items:
            log.warning("No current weather items found in database, skipping vacuum.")
            return

        log.debug(
            f"Reviewing [{len(all_current_weather_items)}] current weather items for deletion."
        )

        for item in all_current_weather_items:
            if not item.retain:
                log.info(
                    f"Deleting current weather item ID {item.id} (retain={item.retain})."
                )

                try:
                    repo.delete(item)

                    _deleted.append(item.id)
                except Exception as exc:
                    log.error(
                        f"({type(exc)}) Error deleting current weather item ID {item.id}. Details: {exc}"
                    )

                    _errored.append(item.id)
                    continue

            else:
                log.debug(
                    f"Retaining current weather item ID {item.id} (retain={item.retain})."
                )

    log.info(
        f"Vacuum complete. Deleted {_deleted} ({len(_deleted)} items). Errors deleting ({len(_errored)} items)."
    )

    return _deleted
