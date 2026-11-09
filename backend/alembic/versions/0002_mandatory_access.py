"""mandatory access: clearance levels and resources

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-09
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

LEVELS_CHECK = "('public', 'internal', 'confidential', 'secret')"


def upgrade():
    op.add_column(
        "users",
        sa.Column("clearance", sa.String(16), nullable=False, server_default="public"),
    )
    op.create_check_constraint("ck_users_clearance", "users", f"clearance IN {LEVELS_CHECK}")

    resources = op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("classification", sa.String(16), nullable=False),
        sa.CheckConstraint(f"classification IN {LEVELS_CHECK}", name="ck_resources_classification"),
    )
    op.bulk_insert(
        resources,
        [
            {"title": "Расписание консультаций", "classification": "public",
             "content": "Консультации проходят по средам в 15:00."},
            {"title": "Регламент доступа в лабораторию", "classification": "internal",
             "content": "Пропуск выдаётся по служебной записке руководителя."},
            {"title": "Отчёт о тестировании на проникновение", "classification": "confidential",
             "content": "Найдено 3 уязвимости средней критичности, исправление до конца месяца."},
            {"title": "Ключи резервного копирования", "classification": "secret",
             "content": "Ключи хранятся в сейфе, доступ только у двух администраторов."},
        ],
    )


def downgrade():
    op.drop_table("resources")
    op.drop_constraint("ck_users_clearance", "users", type_="check")
    op.drop_column("users", "clearance")
