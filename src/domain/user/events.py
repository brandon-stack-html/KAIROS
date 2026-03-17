from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class UserRegistered(DomainEvent):
    user_id: str
    email: str


@dataclass(frozen=True, kw_only=True)
class UserDeactivated(DomainEvent):
    user_id: str
