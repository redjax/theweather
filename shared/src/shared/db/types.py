from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.mysql import JSON as MYSQL_JSON
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
import json

__all__ = ["StrList"]


class StrList(TypeDecorator):
    """Custom type that stores a list of strings in a DB-compatible way."""

    impl = TEXT

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(TEXT))
        elif dialect.name == "mysql":
            return dialect.type_descriptor(MYSQL_JSON)
        else:  # SQLite and other dialects
            return dialect.type_descriptor(SQLITE_TEXT)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("Value must be a list of strings")

        if dialect.name == "postgresql":
            return value
        elif dialect.name == "mysql":
            return json.dumps(value)
        else:  # SQLite and other dialects
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []

        if dialect.name == "postgresql":
            return value
        elif dialect.name in ("mysql", "sqlite"):
            return json.loads(value)
        return value
