from contextlib import contextmanager
import typing as t
from db_operator.config import DB_SETTINGS
from shared.db import get_db_uri, get_engine, get_session_pool

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.orm as so

__all__ = [
    "get_db",
    "return_engine"
]


def _get_db_uri() -> sa.URL:
    return get_db_uri(
        drivername=DB_SETTINGS.get("DB_DRIVERNAME"),
        username=DB_SETTINGS.get("DB_USERNAME"),
        password=DB_SETTINGS.get("DB_PASSWORD"),
        host=DB_SETTINGS.get("DB_HOST"),
        port=DB_SETTINGS.get("DB_PORT"),
        database=DB_SETTINGS.get("DB_DATABASE"),
    )
    

def _get_engine(db_uri: sa.URL | None = None, echo: bool = DB_SETTINGS.get("DB_ECHO") or False) -> sa.Engine:
    if not db_uri:
        db_uri = _get_db_uri()

    return get_engine(url=db_uri, echo=echo)


def return_engine(db_uri: sa.URL | None = None, echo: bool = DB_SETTINGS.get("DB_ECHO") or False) -> sa.Engine:
    log.debug(f"Database engine echo: {echo}")
    
    if not db_uri:
        db_uri = _get_db_uri()
        
    return _get_engine(db_uri=db_uri, echo=echo)


@contextmanager
def get_db(engine: sa.Engine | None = None) -> t.Generator[so.Session, None, None]:
    """Context manager to yield a database sesssion.
    
    Params:
        engine (sqlalchemy.Engine): SQLAlchemy engine to use. If none is provided, a default session will be used.
    
    Yields:
        sqlalchemy.orm.session.Session
        
    Raises:
        Exception
    """
    if not engine:
        engine = _get_engine()

    SessionLocal: so.sessionmaker[so.Session] = get_session_pool(engine)
    
    try:
        with SessionLocal() as session:
            yield session
    except Exception as exc:
        log.error(f"Failed during database transaction ({type(exc)}): {exc}")
        raise
    finally:
        engine.dispose(
                log.debug("DB connection closed")
            )
    