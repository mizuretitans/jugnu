import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.domain.fields import FIELD_LABELS
from app.models import MentorProfile, User
from app.schemas.api import MentorOut, OwnMentorOut


def mentor_out(profile: MentorProfile) -> MentorOut:
    return MentorOut(
        id=profile.user_id,
        name=profile.user.name,
        field=profile.field,
        field_label=FIELD_LABELS[profile.field],
        bio=profile.bio,
        hourly_rate_paise=profile.hourly_rate_paise,
    )


def own_mentor_out(profile: MentorProfile) -> OwnMentorOut:
    return OwnMentorOut(**mentor_out(profile).model_dump(), is_listed=profile.is_listed)


def _query():
    return (
        select(MentorProfile)
        .join(MentorProfile.user)
        .options(contains_eager(MentorProfile.user))
        .order_by(User.created_at, User.name)
    )


def listed_mentors(db: Session, fields: Sequence[str] | None = None) -> list[MentorProfile]:
    query = _query().where(MentorProfile.is_listed)
    if fields is not None:
        query = query.where(MentorProfile.field.in_(fields))
    return list(db.scalars(query))


def get_mentor(
    db: Session, mentor_id: uuid.UUID, *, listed_only: bool = True
) -> MentorProfile | None:
    query = _query().where(MentorProfile.user_id == mentor_id)
    if listed_only:
        query = query.where(MentorProfile.is_listed)
    return db.scalar(query)
