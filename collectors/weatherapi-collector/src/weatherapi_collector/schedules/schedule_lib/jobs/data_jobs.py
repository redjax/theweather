from __future__ import annotations

import typing as t

from weatherapi_collector import (
    client as weatherapi_client,
    db_client,
)
from weatherapi_collector.config import API_SERVER_SETTINGS
from weatherapi_collector.depends import get_db_engine
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

import httpx
from loguru import logger as log
from shared.depends import get_httpx_controller
import sqlalchemy as sa

__all__ = ["job_post_weather_readings"]


def job_post_weather_readings(echo: bool = False):
    log.info(f"Retrieving all WeatherAPI current weather responses from the DB")

    try:
        all_current_weather_models: list[CurrentWeatherJSONCollectorModel] = (
            db_client.get_all_current_weather_responses(echo=echo)
        )
    except Exception as exc:
        log.error(f"Error retrieving current weather responses from DB: {exc}")
        # return

    log.info(
        f"Retrieved {len(all_current_weather_models)} current weather response models"
    )

    log.info(
        f"POSTing current weather readings to API server at {API_SERVER_SETTINGS.base_url}/api/v1/collectors/weather"
    )
    http_controller = get_httpx_controller()

    POST_successes = []

    with http_controller as http:

        for m in all_current_weather_models:
            log.debug(f"Processing model ID {m.id}")
            output_schema = CurrentWeatherJSONCollectorOut(
                current_weather_json=m.current_weather_json,
                id=m.id,
                created_at=m.created_at,
                retain=m.retain,
            )

            url = f"{API_SERVER_SETTINGS.base_url}/api/v1/collectors/weather"
            data = {
                "source": "weatherapi",
                "label": "current",
                "data": output_schema.model_dump(
                    exclude={"id", "created_at", "retain"}
                ),
            }

            req: httpx.Request = httpx.Request("POST", url=url, json=data)

            try:
                res: httpx.Response = http.send_request(req)
                res.raise_for_status()

                log.info(
                    "Weather POSTed successfully. Setting db object's retain=False"
                )
                try:
                    success = db_client.set_current_weather_response_retention(
                        item_id=m.id, retain=False, echo=echo
                    )

                    POST_successes.append(m)
                except Exception as exc:
                    log.error(
                        f"Error updating current weather response retain flag: {exc}"
                    )
                    continue

            except Exception as exc:
                log.error(
                    f"Error POSTing current weather readings to API server: ({type(exc)}) {exc}"
                )
                continue

    log.info(
        f"POSTed {len(POST_successes)}/{len(all_current_weather_models)} current weather readings successfully."
    )

    # log.info(f"Retrieving all WeatherAPI forecast responses from the DB")
    # try:
    #     all_forecast_responses: list[ForecastJSONModel] = (
    #         db_client.get_all_forecast_responses(echo=echo)
    #     )
    # except Exception as exc:
    #     log.error(f"Error retrieving forecast responses from DB: {exc}")
    #     # return
