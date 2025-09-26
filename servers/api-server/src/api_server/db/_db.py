from shared.db import get_db_uri, get_engine, get_session_pool, create_base_metadata
from shared.db import Base
from api_server.config import DB_SETTINGS

from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = [
    "DATABASE_URL",
    "engine",
    "SessionLocal",
]


DATABASE_URL = get_db_uri(
    drivername=DB_SETTINGS.get("DB_DRIVERNAME"),
    host=DB_SETTINGS.get("DB_HOST"),
    port=DB_SETTINGS.get("DB_PORT"),
    username=DB_SETTINGS.get("DB_USERNAME"),
    password=DB_SETTINGS.get("DB_PASSWORD"),
    database=DB_SETTINGS.get("DB_DATABASE"),
)

engine_args = {}

match DB_SETTINGS.get("DB_TYPE"):
    case "sqlite":
        {"check_same_thread": False}
    case _:
        engine_args = {}

engine = get_engine(url=DATABASE_URL, echo=DB_SETTINGS.get("DB_ECHO", False))

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
