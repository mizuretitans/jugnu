import uuid

from fastapi import APIRouter

from app.deps import DbDep, MentorDep, StudentDep, UserDep
from app.schemas.api import BookingIn, BookingOut
from app.services.bookings import confirm_booking, create_booking, own_bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("")
def bookings(user: UserDep, db: DbDep) -> list[BookingOut]:
    return [BookingOut.model_validate(b) for b in own_bookings(db, user)]


@router.post("", status_code=201)
def create(data: BookingIn, user: StudentDep, db: DbDep) -> BookingOut:
    """Payment is simulated: no money moves."""
    return BookingOut.model_validate(create_booking(db, user, data))


@router.post("/{booking_id}/confirm")
def confirm(booking_id: uuid.UUID, user: MentorDep, db: DbDep) -> BookingOut:
    return BookingOut.model_validate(confirm_booking(db, user, booking_id))
