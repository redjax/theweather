from __future__ import annotations

import json
import typing as t

from shared import db
from weatherapi_collector.depends import db_depends
from shared.domain.weatherapi import location as domain_location
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = [
    "save_location",
    "count_locations",
]


def save_location(
    location: t.Union[domain_location.LocationIn, dict, str],
    engine: sa.Engine | None = None,
    echo: bool = False,
) -> domain_location.LocationOut:
    """Save a Location to the database.

    Params:
        location (LocationIn | dict | str): The Location to save. Can be a LocationIn domain object, dict, or JSON string.

    Returns:
        LocationOut: The saved Location.

    Raises:
        Exception: If Location cannot be saved, an `Exception` is raised.

    """
    if not location:
        raise ValueError("Missing Location to save")
    if isinstance(location, str):
        try:
            location: dict = json.loads(location)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing location string as JSON. Details: {exc}"
            log.error(msg)

            raise exc
    if isinstance(location, dict):
        try:
            location: domain_location.LocationIn = (
                domain_location.LocationIn.model_validate(location)
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing location dict as LocationIn domain object. Details: {exc}"
            log.error(msg)

            raise exc

    log.debug(f"Saving location to DB: {location}")

    if engine is None:
        engine = db_depends.get_db_engine(echo=echo)

    session_pool = db_depends.get_session_pool(engine=engine)

    with session_pool() as session:
        log.debug("Initializing LocationRepository instance")
        repo: domain_location.LocationRepository = domain_location.LocationRepository(
            session=session
        )

        log.debug("Converting Pydantic schema to LocationModel")
        try:
            location_model: domain_location.LocationModel = (
                domain_location.LocationModel(**location.model_dump())
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error converting location schema to LocationModel. Details: {exc}"
            log.error(msg)

            raise exc

        try:
            db_location: domain_location.LocationModel | None = repo.save(
                location_model
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error saving location to DB. Details: {exc}"
            log.error(msg)

            raise exc

    if not db_location:
        msg = f"No exceptions thrown while saving location ['{location.name}, {location.region} ({location.country})'], but database returned None from saved object, which should not have happened."
        log.error(msg)

        raise ValueError("location_out should be a LocationModel object, not None.")

    log.success(
        f"Saved location '{location.name}, {location.region} ({location.country})' to DB"
    )

    log.debug("Converting LocationModel to LocationOut")
    try:
        location_out: domain_location.LocationOut = (
            domain_location.LocationOut.model_validate(db_location.__dict__)
        )

        return location_out
    except Exception as exc:
        msg = f"({type(exc)}) Error converting LocationModel to LocationOut. Details: {exc}"
        log.error(msg)

        raise exc


def count_locations(engine: sa.Engine | None = None, echo: bool = False) -> int:
    """Return a count of the number of rows in the location table.

    Params:
        engine (Engine | None, optional): The database engine to use. If None, the default engine is used. Defaults to None.
        echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        int: The count of the number of rows in the location table.

    Raises:
        Exception: If there is an error counting the number of rows in the location table, an `Exception` is raised.

    """
    if engine is None:
        engine = db_depends.get_db_engine(echo=echo)

    session_pool = db_depends.get_session_pool(engine=engine)

    with session_pool() as session:
        repo = domain_location.LocationRepository(session=session)

        return repo.count()
