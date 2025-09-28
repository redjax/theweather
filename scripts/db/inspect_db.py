# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "dynaconf",
#     "hishel",
#     "httpx",
#     "psycopg2-binary",
#     "sqlalchemy",
#     "theweather-shared",
# ]
#
# [tool.uv.sources]
# theweather-shared = { path = "../../shared" }
# ///

from shared.setup import setup_loguru_logging
