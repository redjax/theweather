from shared.depends.http import get_httpx_controller
import time

from temporalio import activity
from loguru import logger as log
import httpx

__all__ = [
    "poll_current_weather",
    "poll_weather_forecast",
]


@activity.defn
def poll_current_weather(api_key: str, location: str) -> dict:
    http_controller = get_httpx_controller()

    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": api_key,
        "q": location,
        "aqi": "yes",
    }

    req = httpx.Request("GET", url=url, params=params)

    try:
        with http_controller as http:
            res = http.send_request(req)
            res.raise_for_status()
    except httpx.ReadTimeout as timeout:
        log.warning(
            f"({type(timeout)}) Operation timed out while requesting current weather."
        )

        log.info(f"Retrying 5 time(s)")
        current_attempt = 0
        retry_sleep = 5
        _sleep = 3
        retry_stagger = 3
        max_retries = 5

        while current_attempt < max_retries:
            if current_attempt > 0:
                _sleep += retry_stagger

            log.info(f"[Retry {current_attempt}/{max_retries}]")

            try:
                res: httpx.Response = http.client.send(req)
                break
            except httpx.ReadTimeout as timeout_2:
                log.warning(f"ReadTimeout on attempt [{current_attempt}/{max_retries}]")

                current_attempt += 1

                time.sleep(retry_sleep)

                continue

    result = res.json()

    return result


@activity.defn
def poll_weather_forecast(api_key: str, location: str, days: int = 1):
    http_controller = get_httpx_controller()

    url = "https://api.weatherapi.com/v1/forecast.json"

    params = {
        "key": api_key,
        "q": location,
        "aqi": "yes",
        "alerts": "yes",
        "days": days,
    }

    req = httpx.Request("GET", url=url, params=params)

    try:
        with http_controller as http:
            res = http.send_request(req)
            res.raise_for_status()
    except httpx.ReadTimeout as timeout:
        log.warning(
            f"({type(timeout)}) Operation timed out while requesting current weather."
        )

        log.info(f"Retrying 5 time(s)")
        current_attempt = 0
        retry_sleep = 5
        _sleep = 3
        retry_stagger = 3
        max_retries = 5

        while current_attempt < max_retries:
            if current_attempt > 0:
                _sleep += retry_stagger

            log.info(f"[Retry {current_attempt}/{max_retries}]")

            try:
                res: httpx.Response = http.client.send(req)
                break
            except httpx.ReadTimeout as timeout_2:
                log.warning(f"ReadTimeout on attempt [{current_attempt}/{max_retries}]")

                current_attempt += 1

                time.sleep(retry_sleep)

                continue

    result = res.json()

    return result
