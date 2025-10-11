from __future__ import annotations

import asyncio

from weatherapi_collector import db_client
from weatherapi_collector.config import API_SERVER_SETTINGS
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
    ForecastJSONCollectorModel,
    ForecastJSONCollectorOut,
)

import httpx
from loguru import logger as log
from shared.depends import get_httpx_controller

__all__ = ["job_post_weather_readings"]


async def _post_current_weather(db_echo: bool = False):
    all_current_weather_models: list[CurrentWeatherJSONCollectorModel] = (
        await asyncio.to_thread(db_client.get_all_current_weather_responses, db_echo)
    )

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

                if res.status_code not in [200, 201]:
                    if res.status_code == 409:
                        log.warning(
                            f"Data entity already exists in DB, marking for deletion."
                        )
                        try:
                            success = db_client.set_current_weather_response_retention(
                                item_id=m.id, retain=False, echo=db_echo
                            )

                            POST_successes.append(m)
                        except Exception as exc:
                            log.error(
                                f"Error updating current weather response retain flag: {exc}"
                            )
                            continue
                    else:
                        log.error(
                            f"Error POSTing current weather readings to API server: ({res.status_code}) {res.text}"
                        )
                        continue

                log.info(
                    "Weather POSTed successfully. Setting db object's retain=False"
                )
                try:
                    success = db_client.set_current_weather_response_retention(
                        item_id=m.id, retain=False, echo=db_echo
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


async def _post_forecast_weather(db_echo: bool = False):
    forecast_models: list[ForecastJSONCollectorModel] = await asyncio.to_thread(
        db_client.get_all_forecast_responses, db_echo
    )

    log.info(f"Retrieved {len(forecast_models)} weather forecast response models")

    log.info(
        f"POSTing weather forecast readings to API server at {API_SERVER_SETTINGS.base_url}/api/v1/collectors/weather"
    )
    http_controller = get_httpx_controller()

    POST_successes = []

    with http_controller as http:

        for m in forecast_models:
            log.debug(f"Processing model ID {m.id}")
            output_schema = ForecastJSONCollectorOut(
                forecast_json=m.forecast_json,
                id=m.id,
                created_at=m.created_at,
                retain=m.retain,
            )

            url = f"{API_SERVER_SETTINGS.base_url}/api/v1/collectors/weather"
            data = {
                "source": "weatherapi",
                "label": "forecast",
                "data": output_schema.model_dump(
                    exclude={"id", "created_at", "retain"}
                ),
            }

            req: httpx.Request = httpx.Request("POST", url=url, json=data)

            try:
                res: httpx.Response = http.send_request(req)
                res.raise_for_status()

                if res.status_code not in [200, 201]:
                    if res.status_code == 409:
                        log.warning(f"Data entity already exists. Marking for deletion")
                        try:
                            success = db_client.set_current_weather_response_retention(
                                item_id=m.id, retain=False, echo=db_echo
                            )

                            POST_successes.append(m)
                        except Exception as exc:
                            log.error(
                                f"Error updating forecast weather response retain flag: {exc}"
                            )
                            continue

                    else:
                        log.error(
                            f"Non-200 response POSTing weather forecast readings: [{res.status_code}: {res.reason_phrase}] {res.text}"
                        )
                        continue

                log.info(
                    "Weather POSTed successfully. Setting db object's retain=False"
                )
                try:
                    success = db_client.set_weather_forecast_response_retention(
                        item_id=m.id, retain=False, echo=db_echo
                    )

                    POST_successes.append(m)
                except Exception as exc:
                    log.error(
                        f"Error updating forecast weather response retain flag: {exc}"
                    )
                    continue

            except Exception as exc:
                log.error(
                    f"Error POSTing weather forecast readings to API server: ({type(exc)}) {exc}"
                )
                continue


async def job_post_weather_readings(db_echo: bool = False):
    log.info("[APScheduler] POSTing weather readings to API server")

    ## Send current weather readings
    try:
        await _post_current_weather(db_echo)
    except Exception as e:
        log.error(f"Error POSTing current weather readings: {e}")

    ## Send forecast weather readings
    try:
        await _post_forecast_weather(db_echo)
    except Exception as e:
        log.error(f"Error POSTing forecast weather readings: {e}")
