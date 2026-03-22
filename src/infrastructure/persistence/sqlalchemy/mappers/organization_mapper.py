"""Imperative mapping: organizations_table + memberships_table ──► domain classes.

Organization has a relationship to Membership loaded eagerly so the
aggregate's _memberships collection is always populated from DB.

Call start_mappers() exactly once at application startup, AFTER
start_tenant_mappers() and start_user_mappers() (FK dependencies).
"""
from sqlalchemy.orm import class_mapper, registry, relationship
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.organization.membership import Membership
from src.domain.organization.organization import Organization
from src.infrastructure.persistence.sqlalchemy.tables.memberships_table import memberships_table
from src.infrastructure.persistence.sqlalchemy.tables.organizations_table import organizations_table

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return

    # 1. Map Membership first (no relationship on its own — org holds the collection)
    try:
        class_mapper(Membership)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Membership, memberships_table)

    # 2. Map Organization with eager relationship to _memberships
    try:
        class_mapper(Organization)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(
            Organization,
            organizations_table,
            properties={
                "_memberships": relationship(
                    Membership,
                    # org_id on memberships_table is an OrganizationIdType (VO), and
                    # Organization.id is also an OrganizationIdType — SA resolves via FK.
                    primaryjoin=(
                        organizations_table.c.id == memberships_table.c.org_id
                    ),
                    foreign_keys=[memberships_table.c.org_id],
                    lazy="selectin",   # load memberships automatically with org
                    cascade="all, delete-orphan",
                )
            },
        )

    _mapped = True
