import uuid

from fastapi import APIRouter

from app.deps import DbDep, MentorDep, StudentDep
from app.errors import not_found
from app.schemas.api import MentorOut, OwnMentorOut, RateIn, RequestOut
from app.services.mentors import get_mentor, listed_mentors, mentor_out, own_mentor_out
from app.services.requests import create_request

router = APIRouter(tags=["mentors"])


@router.get("/mentors")
def mentors(db: DbDep) -> list[MentorOut]:
    return [mentor_out(m) for m in listed_mentors(db)]


@router.get("/mentors/{mentor_id}")
def mentor(mentor_id: uuid.UUID, db: DbDep) -> MentorOut:
    found = get_mentor(db, mentor_id)
    if found is None:
        raise not_found("Mentor not found.")
    return mentor_out(found)


@router.patch("/mentor/rate")
def update_rate(data: RateIn, user: MentorDep, db: DbDep) -> OwnMentorOut:
    profile = get_mentor(db, user.id, listed_only=False)
    if profile is None:
        raise not_found("Mentor profile not found.")
    profile.hourly_rate_paise = data.hourly_rate_rupees * 100
    db.commit()
    return own_mentor_out(profile)


@router.post("/mentors/{mentor_id}/requests")
def request_mentorship(mentor_id: uuid.UUID, user: StudentDep, db: DbDep) -> RequestOut:
    if get_mentor(db, mentor_id) is None:
        raise not_found("This mentor is not available.")
    return RequestOut.model_validate(create_request(db, user.id, mentor_id))
