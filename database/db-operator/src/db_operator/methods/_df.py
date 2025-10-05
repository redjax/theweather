from db_operator.config import DB_SETTINGS, LOGGING_SETTINGS
from db_operator.depends import db_depends
from db_operator.utils import db_utils

import pandas as pd
from loguru import logger as log
import sqlalchemy as sa


__all__ = [
    "read_db_table_into_df"
]


def read_db_table_into_df(table_name: str, engine: sa.Engine | None = None) -> pd.DataFrame:
    if engine is None:
        engine = db_depends.get_engine()

    try:
        df: pd.DataFrame = pd.read_sql_table(table_name, con=engine)
        
        return df
    except Exception as exc:
        log.error(f"Failed to read table '{table_name}' into DataFrame ({type(exc)}): {exc}")
        raise
