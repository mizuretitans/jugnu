import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, false, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.fields import MENTOR_FIELDS, sql_in
from app.models.base import Base, CreatedAt


class User(CreatedAt, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('student', 'mentor')", name="role"),
        CheckConstraint("email = lower(email)", name="email_lower"),
        CheckConstraint("btrim(name) <> ''", name="name_not_blank"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    # Supabase user id (the token's "sub"). Null only for seeded demo users.
    auth_subject: Mapped[uuid.UUID | None] = mapped_column(unique=True)
    # Contact information only. Identity is auth_subject, never the email.
    email: Mapped[str | None] = mapped_column(String(320))
    name: Mapped[str] = mapped_column(String(60))
    role: Mapped[str] = mapped_column(String(10))

    mentor_profile: Mapped["MentorProfile | None"] = relationship(back_populates="user")


class MentorProfile(Base):
    __tablename__ = "mentor_profiles"
    __table_args__ = (
        CheckConstraint(sql_in("field", MENTOR_FIELDS), name="field"),
        CheckConstraint(
            "hourly_rate_paise BETWEEN 100 AND 10000000 AND mod(hourly_rate_paise, 100) = 0",
            name="rate_whole_rupees",
        ),
        Index(None, "field"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    field: Mapped[str] = mapped_column(String(20))
    bio: Mapped[str] = mapped_column(String(500))
    hourly_rate_paise: Mapped[int]
    # New mentors stay hidden until scripts/approve_mentor.py is run.
    is_listed: Mapped[bool] = mapped_column(server_default=false())

    user: Mapped[User] = relationship(back_populates="mentor_profile")
