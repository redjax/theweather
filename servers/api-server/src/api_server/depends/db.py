from loguru import logger as log
from api_server.db import SessionLocal
from sqlalchemy.orm import Session


__all__ = ["get_db"]


def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    except Exception as exc:
        log.error(f"Failed during database transaction ({type(exc)}): {exc}")
        raise
    finally:
        db.close()
