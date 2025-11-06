from loguru import logger as log
from shared.setup import setup_loguru_logging
from weatherapi_collector.config import DB_SETTINGS
from weatherapi_collector.config import API_SERVER_SETTINGS
from weatherapi_collector import db_client, client
from shared import http_lib
from weatherapi_collector.depends import db_depends
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorIn,
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
    CurrentWeatherJSONCollectorRepository,
    ForecastJSONCollectorIn,
    ForecastJSONCollectorModel,
    ForecastJSONCollectorRepository,
    ForecastJSONCollectorOut,
)
import httpx


def set_retention():
    SessionLocal = db_depends.get_session_pool()
    http_controller = http_lib.get_http_controller()

    log.info(f"Database: {DB_SETTINGS.get('DB_DATABASE')}")

    with http_controller as http:
        with SessionLocal() as session:
            current_weather_repo = CurrentWeatherJSONCollectorRepository(session)
            forecast_repo = ForecastJSONCollectorRepository(session)

            db_current_weather_count = current_weather_repo.count()
            log.info(
                f"Found [{db_current_weather_count}] entit{'y' if db_current_weather_count == 1 else 'ies'} in database."
            )

            db_forecast_count = forecast_repo.count()
            log.info(
                f"Found [{db_forecast_count}] entit{'y' if db_forecast_count == 1 else 'ies'} in database."
            )

            db_current_weather_retain_items = (
                current_weather_repo.session.query(CurrentWeatherJSONCollectorModel)
                .filter(CurrentWeatherJSONCollectorModel.retain == True)
                .all()
            )
            log.info(
                f"Found [{len(db_current_weather_retain_items)}] item(s) marked retain=True"
            )

            db_forecast_retain_items = (
                forecast_repo.session.query(ForecastJSONCollectorModel)
                .filter(ForecastJSONCollectorModel.retain == True)
                .all()
            )
            log.info(
                f"Found [{len(db_forecast_retain_items)}] item(s) marked retain=True"
            )

            POST_current_successes = []
            POST_forecast_successes = []

            ## Current weather
            for e in db_current_weather_retain_items:
                output_schema = CurrentWeatherJSONCollectorOut(
                    current_weather_json=e.current_weather_json,
                    id=e.id,
                    created_at=e.created_at,
                    retain=e.retain,
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
                    # res.raise_for_status()

                    if res.status_code not in [200, 201]:
                        if res.status_code == 409:
                            log.warning(
                                f"Data entity already exists. Marking for deletion"
                            )
                            try:
                                success = (
                                    db_client.set_current_weather_response_retention(
                                        item_id=e.id,
                                        retain=False,
                                        echo=DB_SETTINGS.get("DB_ECHO"),
                                    )
                                )

                                log.success(f"Marked db entity '{e.id}' for deletion")
                                POST_current_successes.append(e)
                            except Exception as exc:
                                log.error(
                                    f"Error updating current weather response retain flag: {exc}"
                                )
                                continue

                        else:
                            log.error(
                                f"Non-200 response POSTing current weather readings: [{res.status_code}: {res.reason_phrase}] {res.text}"
                            )
                            continue

                        log.info(
                            "Weather POSTed successfully. Setting db object's retain=False"
                        )
                        try:
                            success = db_client.set_weather_forecast_response_retention(
                                item_id=e.id,
                                retain=False,
                                echo=DB_SETTINGS.get("DB_ECHO"),
                            )

                            POST_current_successes.append(e)
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

            ## Forecast weather
            for e in db_forecast_retain_items:
                output_schema = ForecastJSONCollectorOut(
                    forecast_json=e.forecast_json,
                    id=e.id,
                    created_at=e.created_at,
                    retain=e.retain,
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
                    # res.raise_for_status()

                    if res.status_code not in [200, 201]:
                        if res.status_code == 409:
                            log.warning(
                                f"Data entity already exists. Marking for deletion"
                            )
                            try:
                                success = (
                                    db_client.set_weather_forecast_response_retention(
                                        item_id=e.id,
                                        retain=False,
                                        echo=DB_SETTINGS.get("DB_ECHO"),
                                    )
                                )

                                log.success(f"Marked db entity '{e.id}' for deletion")
                                POST_current_successes.append(e)
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
                                item_id=e.id,
                                retain=False,
                                echo=DB_SETTINGS.get("DB_ECHO"),
                            )

                            POST_current_successes.append(e)
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


def clean_db():
    SessionLocal = db_depends.get_session_pool()

    with SessionLocal() as session:
        current_weather_repo = CurrentWeatherJSONCollectorRepository(session)
        forecast_weather_repo = ForecastJSONCollectorRepository(session)

        db_current_weather_retain_items = (
            current_weather_repo.session.query(CurrentWeatherJSONCollectorModel)
            .filter(CurrentWeatherJSONCollectorModel.retain == False)
            .all()
        )
        log.info(
            f"Found [{len(db_current_weather_retain_items)}] item(s) marked retain=False"
        )

        db_forecast_retain_items = (
            forecast_weather_repo.session.query(ForecastJSONCollectorModel)
            .filter(ForecastJSONCollectorModel.retain == False)
            .all()
        )
        log.info(f"Found [{len(db_forecast_retain_items)}] item(s) marked retain=False")

        ## Delete current weather
        for e in db_current_weather_retain_items:
            log.info(f"Deleting entity with id: {e.id}")

            try:
                current_weather_repo.delete(e)
                log.success(f"Deleted entity with id: {e.id}")
            except Exception as exc:
                log.error(f"Failed to delete entity with id: {e.id}. Details: {exc}")
                continue

        ## Delete forecast weather
        for e in db_forecast_retain_items:
            log.info(f"Deleting entity with id: {e.id}")

            try:
                forecast_weather_repo.delete(e)
                log.success(f"Deleted entity with id: {e.id}")
            except Exception as exc:
                log.error(f"Failed to delete entity with id: {e.id}. Details: {exc}")
                continue


def main():
    try:
        set_retention()
    except Exception as exc:
        log.error(f"Failed to set retention bool on database entities")
        return False

    try:
        clean_db()
    except Exception as exc:
        log.error(f"Failed cleaning database: {exc}")
        return False


if __name__ == "__main__":
    setup_loguru_logging()
    log.debug("DEBUG logging enabled")

    main()
