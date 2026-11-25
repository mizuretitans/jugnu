import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Index, String, Text, false,
    func, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.fields import FIELDS, sql_in
from app.models.base import Base, CreatedAt

INTAKE_STATUSES = ("in_progress", "confirming", "ready_to_route", "completed")


class IntakeProfile(CreatedAt, Base):
    __tablename__ = "intake_profiles"
    __table_args__ = (
        CheckConstraint(sql_in("status", INTAKE_STATUSES), name="status"),
        CheckConstraint(sql_in("primary_field", tuple(FIELDS)), name="primary_field"),
        Index(
            "ix_intake_profiles_followup", "updated_at",
            postgresql_where=text("needs_human_followup"),
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String(20), server_default="in_progress")
    phase_turns: Mapped[int] = mapped_column(server_default="0")
    route_failures: Mapped[int] = mapped_column(server_default="0")
    profile: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    primary_field: Mapped[str | None] = mapped_column(String(20))
    # none_as_null: Python None must become SQL NULL so COALESCE keeps the old analysis.
    analysis: Mapped[dict[str, Any] | None] = mapped_column(JSONB(none_as_null=True))
    needs_human_followup: Mapped[bool] = mapped_column(server_default=false())
    # Lease: only one chat turn per student runs at a time.
    busy_token: Mapped[uuid.UUID | None]
    busy_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class _ChatMessage(CreatedAt):
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(10))
    content: Mapped[str] = mapped_column(Text)


class IntakeMessage(_ChatMessage, Base):
    __tablename__ = "intake_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="role"),
        Index(None, "user_id", "id"),
    )


class HelperMessage(_ChatMessage, Base):
    __tablename__ = "helper_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="role"),
        Index(None, "user_id", "id"),
    )
