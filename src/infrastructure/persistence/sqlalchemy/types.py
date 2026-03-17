"""Custom SQLAlchemy TypeDecorators.

These live in infrastructure so the domain value objects stay pure.
Each decorator handles the round-trip:
  Python value object  ──►  DB primitive  (process_bind_param)
  DB primitive         ──►  Python value object  (process_result_value)
"""
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from src.domain.user.user import UserEmail, UserId, UserName


class UserIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, UserId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return UserId(value) if value is not None else None


class UserEmailType(TypeDecorator):
    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, UserEmail):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return UserEmail(value) if value is not None else None


class UserNameType(TypeDecorator):
    impl = String(100)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, UserName):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return UserName(value) if value is not None else None
