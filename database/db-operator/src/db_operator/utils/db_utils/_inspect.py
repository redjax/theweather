import sqlalchemy as sa

from loguru import logger as log


__all__ = ["get_table_names"]


def get_table_names(engine: sa.Engine) -> list[str]:
    if not engine:
        raise ValueError("No SQLAlchemy engine provided")

    inspector: sa.Inspector = sa.inspect(engine)
    
    try:
        table_names: list[str] = inspector.get_table_names()
        return table_names
    except Exception as exc:
        log.error(f"Failed to get table names ({type(exc)}): {exc}")
        raise
