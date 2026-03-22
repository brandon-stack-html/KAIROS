"""add_organizations

Creates: organizations, memberships, invitations tables.
Adds PostgreSQL RLS on organizations and memberships.

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-03-21 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── organizations ─────────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(63), nullable=False),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_tenant_id", "organizations", ["tenant_id"])
    op.create_index(
        "ix_organizations_tenant_id_slug",
        "organizations",
        ["tenant_id", "slug"],
        unique=True,
    )

    # ── memberships ───────────────────────────────────────────────────────
    op.create_table(
        "memberships",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column(
            "org_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id", "user_id", name="uq_memberships_org_user"),
    )
    op.create_index("ix_memberships_org_id", "memberships", ["org_id"])
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])
    op.create_index(
        "ix_memberships_org_id_user_id", "memberships", ["org_id", "user_id"]
    )

    # ── invitations ───────────────────────────────────────────────────────
    op.create_table(
        "invitations",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column(
            "org_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("invitee_email", sa.String(255), nullable=False),
        sa.Column(
            "inviter_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_accepted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invitations_org_id", "invitations", ["org_id"])
    op.create_index(
        "ix_invitations_org_id_email", "invitations", ["org_id", "invitee_email"]
    )

    # ── PostgreSQL RLS ────────────────────────────────────────────────────
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in ("organizations", "memberships"):
            op.execute(sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
            op.execute(sa.text(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"))

        op.execute(
            sa.text("""
                CREATE POLICY tenant_isolation ON organizations
                USING (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                )
            """)
        )
        op.execute(
            sa.text("""
                CREATE POLICY tenant_isolation ON memberships
                USING (
                    org_id IN (
                        SELECT id FROM organizations
                        WHERE tenant_id::text = current_setting('app.current_tenant_id', true)
                    )
                )
            """)
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("DROP POLICY IF EXISTS tenant_isolation ON memberships"))
        op.execute(sa.text("DROP POLICY IF EXISTS tenant_isolation ON organizations"))
        op.execute(sa.text("ALTER TABLE memberships DISABLE ROW LEVEL SECURITY"))
        op.execute(sa.text("ALTER TABLE organizations DISABLE ROW LEVEL SECURITY"))

    op.drop_index("ix_invitations_org_id_email", table_name="invitations")
    op.drop_index("ix_invitations_org_id", table_name="invitations")
    op.drop_table("invitations")

    op.drop_index("ix_memberships_org_id_user_id", table_name="memberships")
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_index("ix_memberships_org_id", table_name="memberships")
    op.drop_table("memberships")

    op.drop_index("ix_organizations_tenant_id_slug", table_name="organizations")
    op.drop_index("ix_organizations_tenant_id", table_name="organizations")
    op.drop_table("organizations")
