from __future__ import annotations

import typing as t

from shared.db.base import BaseRepository

from .models import (
    CurrentWeatherAirQualityModel,
    CurrentWeatherConditionModel,
    CurrentWeatherJSONModel,
    CurrentWeatherModel,
)

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = [
    "CurrentWeatherRepository",
    "CurrentWeatherJSONRepository",
    "CurrentWeatherConditionRepository",
    "CurrentWeatherAirQualityRepository",
]


class CurrentWeatherJSONRepository(BaseRepository):
    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherJSONModel)


class CurrentWeatherRepository(BaseRepository[CurrentWeatherModel]):
    """Repository for CurrentWeatherModel.

    Description:
        This class provides methods to interact with the CurrentWeatherModel table in the database.

    Attributes:
        session (so.Session): The database session.

    """

    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherModel)

    def create_with_related(
        self, weather_data: dict, condition_data: dict, air_quality_data: dict
    ) -> CurrentWeatherModel:
        """Create a new CurrentWeatherModel with related models.

        Description:
            This method creates a new CurrentWeatherModel with related models.

        Params:
            weather_data (dict): The data for the main weather model.
            condition_data (dict): The data for the condition model.
            air_quality_data (dict): The data for the air quality model.

        Returns:
            CurrentWeatherModel: The newly created CurrentWeatherModel.

        Raises:
            Exception: If there is an error creating the related models.

        """
        ## Create weather model objects
        weather = CurrentWeatherModel(**weather_data)
        condition = CurrentWeatherConditionModel(**condition_data)
        air_quality = CurrentWeatherAirQualityModel(**air_quality_data)

        ## Associate the related models with the main weather model
        weather.condition = condition
        weather.air_quality = air_quality

        ## Add and commit all models in one transaction
        self.session.add(weather)
        self.session.commit()

        ## Refresh with data from saving to database before returning
        self.session.refresh(weather)

        return weather

    def update_with_related(
        self,
        weather: CurrentWeatherModel,
        weather_data: dict,
        condition_data: dict = None,
        air_quality_data: dict = None,
    ) -> CurrentWeatherModel:
        """Update a CurrentWeatherModel with related models.

        Description:
            This method updates a CurrentWeatherModel with related models.

        Params:
            weather (CurrentWeatherModel): The CurrentWeatherModel to update.
            weather_data (dict): The data for the main weather model.
            condition_data (dict): The data for the condition model.
            air_quality_data (dict): The data for the air quality model.

        Returns:
            CurrentWeatherModel: The updated CurrentWeatherModel.

        Raises:
            Exception: If there is an error updating the related models.

        """
        ## Update main weather model
        self.update(weather, weather_data)

        ## Update condition if provided
        if condition_data and weather.condition:
            self.update(weather.condition, condition_data)

        ## Update air quality if provided
        if air_quality_data and weather.air_quality:
            self.update(weather.air_quality, air_quality_data)

        return weather

    def get_by_id(self, id: int):
        """Get a CurrentWeatherModel by its ID.

        Description:
            This method returns a CurrentWeatherModel by its ID.

        Params:
            id (int): The ID of the CurrentWeatherModel to retrieve.

        Returns:
            CurrentWeatherModel: The CurrentWeatherModel with the specified ID.

        Raises:
            Exception: If there is an error retrieving the CurrentWeatherModel.

        """
        return (
            self.session.query(CurrentWeatherModel)
            .filter(CurrentWeatherModel.id == id)
            .one_or_none()
        )

    def get_by_last_updated_epoch(self, last_updated_epoch: int):
        """Get a CurrentWeatherModel by its last updated epoch.

        Description:
            This method returns a CurrentWeatherModel by its last updated epoch.

        Params:
            last_updated_epoch (int): The last updated epoch of the CurrentWeatherModel to retrieve.

        Returns:
            CurrentWeatherModel: The CurrentWeatherModel with the specified last updated epoch.

        Raises:
            Exception: If there is an error retrieving the CurrentWeatherModel.

        """
        return (
            self.session.query(CurrentWeatherModel)
            .filter(CurrentWeatherModel.last_updated_epoch == last_updated_epoch)
            .one_or_none()
        )

    def get_by_last_updated(self, last_updated: str):
        """Get a CurrentWeatherModel by its last updated.

        Description:
            This method returns a CurrentWeatherModel by its last updated.

        Params:
            last_updated (str): The last updated of the CurrentWeatherModel to retrieve.

        Returns:
            CurrentWeatherModel: The CurrentWeatherModel with the specified last updated.

        Raises:
            Exception: If there is an error retrieving the CurrentWeatherModel.

        """
        return (
            self.session.query(CurrentWeatherModel)
            .filter(CurrentWeatherModel.last_updated == last_updated)
            .one_or_none()
        )

    def get_with_related(self, id: int):
        """Get a CurrentWeatherModel with related models.

        Description:
            This method returns a CurrentWeatherModel with related models.

        Params:
            id (int): The ID of the CurrentWeatherModel to retrieve.

        Returns:
            CurrentWeatherModel: The CurrentWeatherModel with the specified ID.

        Raises:
            Exception: If there is an error retrieving the CurrentWeatherModel.

        """
        try:
            ## Get weather with related models
            _weather: CurrentWeatherModel = (
                self.session.query(CurrentWeatherModel)
                .options(
                    so.joinedload(CurrentWeatherModel.condition),
                    so.joinedload(CurrentWeatherModel.air_quality),
                )
                .filter(CurrentWeatherModel.id == id)
                .one()
            )

            return _weather
        except Exception as exc:
            msg = f"({type(exc)}) Error retrieving related entities. Details: {exc}"
            log.error(msg)

            raise exc


class CurrentWeatherConditionRepository(BaseRepository[CurrentWeatherConditionModel]):
    """Repository for CurrentWeatherConditionModel.

    Description:
        This class provides methods to interact with the CurrentWeatherConditionModel table in the database.

    Attributes:
        session (so.Session): The database session.

    """

    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherConditionModel)


class CurrentWeatherAirQualityRepository(BaseRepository[CurrentWeatherAirQualityModel]):
    """Repository for CurrentWeatherAirQualityModel.

    Description:
        This class provides methods to interact with the CurrentWeatherAirQualityModel table in the database.

    Attributes:
        session (so.Session): The database session.

    """

    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherAirQualityModel)
