from __future__ import annotations

import json
import uuid

from sqlalchemy.dialects.mysql import JSON as MYSQL_JSON
from sqlalchemy.dialects.postgresql import (
    ARRAY as PG_ARRAY,
    UUID as PG_UUID,
)
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy.types import CHAR, TEXT, TypeDecorator

__all__ = ["StrList", "GUID"]


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

class GUID(TypeDecorator):
    """Platform-independent GUID/UUID.

    Uses PostgreSQL's UUID type, otherwise stores as stringified hex (CHAR(32)).
    """

    impl = CHAR

    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        if dialect.name == "postgresql":
            return str(value)
        return "%.32x" % value.int  # hex string, no dashes

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(str(value))
