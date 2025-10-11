from shared.setup import setup_loguru_logging
from db_operator.config import DB_SETTINGS, LOGGING_SETTINGS
from db_operator.depends import db_depends
from db_operator.utils import db_utils
from db_operator import read_db_table_into_df

import pandas as pd
from loguru import logger as log

if __name__ == "__main__":
    setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LEVEL"), log_file_path="logs/db_operator_prototype.log")
    log.debug("DEBUG logging enabled")
    
    log.debug(f"DB_SETTINGS: {DB_SETTINGS}")
    
    engine = db_depends.return_engine()
    log.info("DB connected")
    
    table_names = db_utils.get_table_names(engine=engine)
    log.debug(f"DB table names:\n{table_names}")
    
    current_weather_json_df = read_db_table_into_df(table_name="weatherapi_current_json", engine=engine)
    print(current_weather_json_df.head(5))
    
    # for name in table_names:
    #     df = pd.read_sql_table(name, con=engine)
    #     print(df.head(5))
    
    # df = pd.read_sql_table("weatherapi_current_json", con=engine)
    # print(df.head(5))
