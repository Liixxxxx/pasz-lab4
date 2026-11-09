from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

LEVELS_CHECK = "('public', 'internal', 'confidential', 'secret')"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(f"clearance IN {LEVELS_CHECK}", name="ck_users_clearance"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    clearance: Mapped[str] = mapped_column(String(16), server_default="public")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (
        CheckConstraint(f"classification IN {LEVELS_CHECK}", name="ck_resources_classification"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String(16))
