import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.deps import CurrentUser
from app.errors import ApiError, not_found
from app.models import Booking, MentorProfile
from app.schemas.api import BookingIn
from app.services.requests import ensure_accepted


def _with_people():
    return select(Booking).options(joinedload(Booking.student), joinedload(Booking.mentor))


def own_bookings(db: Session, user: CurrentUser) -> list[Booking]:
    column = Booking.mentor_id if user.role == "mentor" else Booking.student_id
    return list(
        db.scalars(_with_people().where(column == user.id).order_by(Booking.created_at.desc()))
    )


def _replay(db: Session, student_id: uuid.UUID, data: BookingIn) -> Booking | None:
    existing = db.scalar(
        _with_people().where(
            Booking.student_id == student_id, Booking.idempotency_key == data.idempotency_key
        )
    )
    if existing is None:
        return None
    same = (
        existing.mentor_id == data.mentor_id
        and existing.minutes == data.minutes
        and existing.topic == data.topic
        and existing.hourly_rate_paise == data.expected_rate_paise
    )
    if not same:
        raise ApiError(
            409, "idempotency_conflict", "This checkout was already used. Please start again."
        )
    return existing


def create_booking(db: Session, student: CurrentUser, data: BookingIn) -> Booking:
    # Replays first: a retry must succeed even if the mentor's rate changed since.
    if (existing := _replay(db, student.id, data)) is not None:
        return existing

    # FOR SHARE: the rate cannot change between this check and our commit.
    mentor = db.scalar(
        select(MentorProfile)
        .where(MentorProfile.user_id == data.mentor_id, MentorProfile.is_listed)
        .with_for_update(read=True)
    )
    if mentor is None:
        raise not_found("This mentor is not available.")
    if mentor.hourly_rate_paise != data.expected_rate_paise:
        raise ApiError(
            409, "rate_changed",
            "The hourly rate changed. Please review the new total before paying.",
            hourly_rate_paise=mentor.hourly_rate_paise,
        )

    # Rates are whole rupees (multiples of 100), so this division is always exact.
    total = mentor.hourly_rate_paise * data.minutes // 60
    db.execute(
        insert(Booking)
        .values(
            idempotency_key=data.idempotency_key,
            student_id=student.id,
            mentor_id=data.mentor_id,
            hourly_rate_paise=mentor.hourly_rate_paise,
            minutes=data.minutes,
            total_paise=total,
            topic=data.topic,
        )
        .on_conflict_do_nothing(index_elements=["student_id", "idempotency_key"])
    )
    db.commit()
    booking = _replay(db, student.id, data)
    assert booking is not None
    return booking


def confirm_booking(db: Session, mentor: CurrentUser, booking_id: uuid.UUID) -> Booking:
    booking = db.scalar(
        select(Booking)
        .where(Booking.id == booking_id, Booking.mentor_id == mentor.id)
        .with_for_update()
    )
    if booking is None:
        raise not_found("Booking not found.")
    if booking.status == "pending":
        booking.request_id = ensure_accepted(db, booking.student_id, booking.mentor_id)
        booking.status = "confirmed"
        booking.confirmed_at = func.now()
    db.commit()
    return db.scalars(_with_people().where(Booking.id == booking_id)).one()
