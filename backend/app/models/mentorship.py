import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Index, String,
    UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.fields import COMMUNITY_FIELDS, sql_in
from app.models.base import Base, CreatedAt
from app.models.user import User


class MentorshipRequest(CreatedAt, Base):
    __tablename__ = "mentorship_requests"
    __table_args__ = (
        UniqueConstraint("student_id", "mentor_id"),
        CheckConstraint("status IN ('pending', 'accepted')", name="status"),
        CheckConstraint("(status = 'accepted') = (accepted_at IS NOT NULL)", name="accepted_at"),
        Index(None, "mentor_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    mentor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(10), server_default="pending")
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped[User] = relationship(foreign_keys=[student_id])
    mentor: Mapped[User] = relationship(foreign_keys=[mentor_id])


class ConversationMessage(CreatedAt, Base):
    __tablename__ = "conversation_messages"
    __table_args__ = (
        CheckConstraint("btrim(body) <> ''", name="body_not_blank"),
        Index(None, "request_id", "id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mentorship_requests.id", ondelete="CASCADE")
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(String(1500))

    sender: Mapped[User] = relationship()


class CommunityPost(CreatedAt, Base):
    __tablename__ = "community_posts"
    __table_args__ = (
        CheckConstraint(sql_in("field", COMMUNITY_FIELDS), name="field"),
        CheckConstraint("btrim(body) <> ''", name="body_not_blank"),
        Index(None, "field", "id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    field: Mapped[str] = mapped_column(String(20))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(String(1500))

    author: Mapped[User] = relationship()


class Booking(CreatedAt, Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("student_id", "idempotency_key"),
        CheckConstraint("minutes IN (30, 60, 90, 120)", name="minutes"),
        CheckConstraint("status IN ('pending', 'confirmed')", name="status"),
        CheckConstraint("payment_mode = 'simulated'", name="payment_mode"),
        CheckConstraint(
            "total_paise::bigint * 60 = hourly_rate_paise::bigint * minutes", name="total"
        ),
        CheckConstraint(
            "(status = 'confirmed') = (request_id IS NOT NULL AND confirmed_at IS NOT NULL)",
            name="confirmed",
        ),
        Index(None, "mentor_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    idempotency_key: Mapped[uuid.UUID]
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    mentor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("mentorship_requests.id"))
    hourly_rate_paise: Mapped[int]
    minutes: Mapped[int]
    total_paise: Mapped[int]
    topic: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(10), server_default="pending")
    payment_mode: Mapped[str] = mapped_column(String(10), server_default="simulated")
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped[User] = relationship(foreign_keys=[student_id])
    mentor: Mapped[User] = relationship(foreign_keys=[mentor_id])
