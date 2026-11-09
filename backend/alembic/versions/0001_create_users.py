"""create users table

Revision ID: 0001
Revises:
Create Date: 2026-11-09
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("login", sa.String(32), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_login", "users", ["login"], unique=True)


def downgrade():
    op.drop_index("ix_users_login", table_name="users")
    op.drop_table("users")
