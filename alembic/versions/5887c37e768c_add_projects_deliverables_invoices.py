"""add_projects_deliverables_invoices

Revision ID: 5887c37e768c
Revises: b1c2d3e4f5a6
Create Date: 2026-03-22 14:20:06.808595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5887c37e768c'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('invoices',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('org_id', sa.String(length=36), nullable=False),
    sa.Column('tenant_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_org_id'), 'invoices', ['org_id'], unique=False)
    op.create_index(op.f('ix_invoices_tenant_id'), 'invoices', ['tenant_id'], unique=False)
    op.create_index('ix_invoices_tenant_id_org_id', 'invoices', ['tenant_id', 'org_id'], unique=False)
    op.create_table('projects',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('org_id', sa.String(length=36), nullable=False),
    sa.Column('tenant_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_org_id'), 'projects', ['org_id'], unique=False)
    op.create_index(op.f('ix_projects_tenant_id'), 'projects', ['tenant_id'], unique=False)
    op.create_index('ix_projects_tenant_id_org_id', 'projects', ['tenant_id', 'org_id'], unique=False)
    op.create_table('deliverables',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('url_link', sa.String(length=2048), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('tenant_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deliverables_project_id'), 'deliverables', ['project_id'], unique=False)
    op.create_index(op.f('ix_deliverables_tenant_id'), 'deliverables', ['tenant_id'], unique=False)
    op.create_index('ix_deliverables_tenant_id_project_id', 'deliverables', ['tenant_id', 'project_id'], unique=False)
    op.create_index(op.f('ix_invitations_inviter_id'), 'invitations', ['inviter_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_tenant_id'), 'refresh_tokens', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_refresh_tokens_tenant_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_invitations_inviter_id'), table_name='invitations')
    op.drop_index('ix_deliverables_tenant_id_project_id', table_name='deliverables')
    op.drop_index(op.f('ix_deliverables_tenant_id'), table_name='deliverables')
    op.drop_index(op.f('ix_deliverables_project_id'), table_name='deliverables')
    op.drop_table('deliverables')
    op.drop_index('ix_projects_tenant_id_org_id', table_name='projects')
    op.drop_index(op.f('ix_projects_tenant_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_org_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index('ix_invoices_tenant_id_org_id', table_name='invoices')
    op.drop_index(op.f('ix_invoices_tenant_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_org_id'), table_name='invoices')
    op.drop_table('invoices')
