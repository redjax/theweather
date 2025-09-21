from shared.http_lib import HttpxController
from shared.http_lib.config import HTTP_SETTINGS

__all__ = ["get_httpx_controller"]


def get_httpx_controller(
    cacheable_methods: list[str] = ["GET", "HEAD"],
    cacheable_status_codes: list[int] = [200, 201, 202, 301, 308],
    follow_redirects: bool = True,
):
    return HttpxController(
        follow_redirects=follow_redirects,
        cacheable_methods=cacheable_methods,
        cacheable_status_codes=cacheable_status_codes,
        use_cache=HTTP_SETTINGS.get("HTTP_USE_CACHE"),
        cache_type=HTTP_SETTINGS.get("HTTP_CACHE_TYPE"),
        cache_ttl=HTTP_SETTINGS.get("HTTP_CACHE_TTL"),
        cache_file_dir=HTTP_SETTINGS.get("HTTP_CACHE_FILE_DIR"),
        cache_db_file=HTTP_SETTINGS.get("HTTP_CACHE_DB_FILE"),
        check_ttl_every=HTTP_SETTINGS.get("HTTP_CACHE_CHECK_TTL_EVERY"),
    )
