"""add_tenants_and_tenant_id_to_users

Revision ID: 257c98f95577
Revises: 9f336b4c00bb
Create Date: 2026-03-20 22:56:22.168572

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from src.infrastructure.persistence.sqlalchemy.types import TenantIdType  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "257c98f95577"
down_revision: Union[str, Sequence[str], None] = "9f336b4c00bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ── Create tenants table ──────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", TenantIdType(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=63), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"], unique=True)

    # ── Add tenant_id FK to users ─────────────────────────────────────────
    # batch_alter_table works on both PostgreSQL and SQLite (copy-and-move).
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("tenant_id", TenantIdType(length=36), nullable=True)
        )
        batch_op.create_index("ix_users_tenant_id", ["tenant_id"], unique=False)
        batch_op.create_index(
            "ix_users_tenant_id_email", ["tenant_id", "email"], unique=False
        )
        batch_op.create_foreign_key(
            "fk_users_tenant_id",
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ── PostgreSQL Row Level Security ────────────────────────────────────
    # Skipped on SQLite (used in tests). RLS enforces DB-level tenant
    # isolation as an additional layer on top of application-level filtering.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("ALTER TABLE users ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text("ALTER TABLE users FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text("""
                CREATE POLICY tenant_isolation ON users
                USING (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                )
            """)
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("DROP POLICY IF EXISTS tenant_isolation ON users"))
        op.execute(sa.text("ALTER TABLE users DISABLE ROW LEVEL SECURITY"))

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("fk_users_tenant_id", type_="foreignkey")
        batch_op.drop_index("ix_users_tenant_id_email")
        batch_op.drop_index("ix_users_tenant_id")
        batch_op.drop_column("tenant_id")
    op.drop_index(op.f("ix_tenants_slug"), table_name="tenants")
    op.drop_table("tenants")
