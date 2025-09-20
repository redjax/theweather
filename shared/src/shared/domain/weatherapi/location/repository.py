from __future__ import annotations

import typing as t

from .models import WeatherAPILocationModel

from shared.db.base import BaseRepository
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = [
    "LocationRepository",
]


class LocationRepository(BaseRepository[WeatherAPILocationModel]):
    """Repository for WeatherAPILocationModel objects.

    Attributes:
        session (so.Session): The database session.

    """

    def __init__(self, session: so.Session):
        super().__init__(session, WeatherAPILocationModel)

    def get_by_id(self, id: int) -> WeatherAPILocationModel | None:
        """Get a location by its ID.

        Params:
            id (int): The ID of the location to retrieve.

        Returns:
            (WeatherAPILocationModel): A WeatherAPILocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(WeatherAPILocationModel)
            .filter(WeatherAPILocationModel.id == id)
            .one_or_none()
        )

    def get_by_country(self, country: str) -> list[WeatherAPILocationModel] | None:
        """Get a location by its country.

        Params:
            country (str): The country of the location.

        Returns:
            (WeatherAPILocationModel): A WeatherAPILocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(WeatherAPILocationModel)
            .filter(WeatherAPILocationModel.country == country)
            .all()
        )

    def get_by_country_and_region(
        self, region: str, country: str
    ) -> WeatherAPILocationModel | None:
        """Get a location by its country, and region/state.

        Params:
            region (str): The region/state of the location.
            country (str): The country of the location.

        Returns:
            (WeatherAPILocationModel): A WeatherAPILocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(WeatherAPILocationModel)
            .filter(
                WeatherAPILocationModel.country == country
                and WeatherAPILocationModel.region == region
            )
            .one_or_none()
        )

    def get_by_name_country_and_region(
        self, name: str, region: str, country: str
    ) -> WeatherAPILocationModel | None:
        """Get a location by its name, country, and region/state.

        Params:
            name (str): The name of the location.
            region (str): The region/state of the location.
            country (str): The country of the location.

        Returns:
            (WeatherAPILocationModel): A WeatherAPILocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(WeatherAPILocationModel)
            .filter(
                WeatherAPILocationModel.name == name
                and WeatherAPILocationModel.country == country
                and WeatherAPILocationModel.region == region
            )
            .one_or_none()
        )

    def save(self, location: WeatherAPILocationModel) -> WeatherAPILocationModel | None:
        """Save a location to the database.

        Params:
            location (WeatherAPILocationModel): The location to save.

        Returns:
            WeatherAPILocationModel: The saved location.

        Raises:
            Exception: If location cannot be saved, an `Exception` is raised.

        """
        ## Check if location already exists
        existing_location: WeatherAPILocationModel | None = (
            self.get_by_name_country_and_region(
                location.name, location.region, location.country
            )
        )

        if existing_location:
            log.info(
                f"Location already exists: {location.name}, {location.region}, {location.country}. Returning from database."
            )
            return self.get_by_name_country_and_region(
                location.name, location.region, location.country
            )

        try:
            self.session.add(location)
            self.session.commit()
            self.session.refresh(location)

            return location
        except sa_exc.IntegrityError as exc:
            msg = f"({type(exc)}) Error saving location. Details: {exc}"
            log.error(msg)
            raise
