"""add_documents

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-03-28 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("uploaded_by", sa.String(36), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_org_id", "documents", ["org_id"])
    op.create_index("ix_documents_project_id", "documents", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_documents_project_id", table_name="documents")
    op.drop_index("ix_documents_org_id", table_name="documents")
    op.drop_table("documents")
