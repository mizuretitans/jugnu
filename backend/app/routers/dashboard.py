from fastapi import APIRouter

from app.deps import DbDep, UserDep
from app.domain.fields import FIELD_LABELS
from app.domain.roadmaps import roadmap_for
from app.models import IntakeProfile
from app.schemas.api import BookingOut, DashboardOut, RequestOut
from app.services.bookings import own_bookings
from app.services.mentors import get_mentor, listed_mentors, mentor_out, own_mentor_out
from app.services.requests import own_requests

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(user: UserDep, db: DbDep) -> DashboardOut:
    requests = [RequestOut.model_validate(r) for r in own_requests(db, user)]
    bookings = [BookingOut.model_validate(b) for b in own_bookings(db, user)]

    if user.role == "mentor":
        profile = get_mentor(db, user.id, listed_only=False)
        field = profile.field if profile else None
        return DashboardOut(
            role="mentor", field=field, field_label=FIELD_LABELS.get(field or ""),
            roadmap=roadmap_for(field), mentor=own_mentor_out(profile) if profile else None,
            requests=requests, bookings=bookings,
        )

    intake = db.get(IntakeProfile, user.id)
    completed = intake is not None and intake.status == "completed"
    field = intake.primary_field if completed else None
    secondary = (intake.analysis or {}).get("secondary_fields", []) if completed else []

    # Own field first, then the secondary fields, then everyone.
    own = listed_mentors(db, [field]) if field else []
    suggested = own or (listed_mentors(db, secondary) if secondary else []) or listed_mentors(db)
    return DashboardOut(
        role="student", field=field, field_label=FIELD_LABELS.get(field or ""),
        roadmap=roadmap_for(field), intake_status=intake.status if intake else "not_started",
        secondary_labels=[FIELD_LABELS[f] for f in secondary if f in FIELD_LABELS],
        field_has_mentors=bool(own), suggested_mentors=[mentor_out(m) for m in suggested[:3]],
        requests=requests, bookings=bookings,
    )
