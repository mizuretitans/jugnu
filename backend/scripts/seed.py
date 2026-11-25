"""Add the sample mentors and demo students. Safe to run again.

    python -m scripts.seed                add what is missing
    python -m scripts.seed --reset-demo   also clear everything the demo users did

Sample people are for development and demos. Do not seed a real deployment.
"""
import argparse
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.domain.demo import DEMO_USERS, seed_id
from app.domain.fields import FIELD_LABELS
from app.models import (
    Booking, CommunityPost, ConversationMessage, HelperMessage, IntakeMessage, IntakeProfile,
    MentorProfile, MentorshipRequest, User,
)
from app.services.intake.engine import GREETING
from app.services.intake.scripted import ScriptedLLM

MENTORS = [
    ("civil_services", "Ananya Rao", 60000,
     "Build a reading routine and turn a broad syllabus into weekly goals."),
    ("defense", "Kabir Singh", 50000,
     "Explore service careers and build a steady preparation routine."),
    ("teaching", "Meera Iyer", 45000,
     "Discover your teaching interests and practise planning your first lesson."),
    ("technology", "Arjun Shah", 80000,
     "Find your first project and build confidence with programming."),
]

STUDENTS = {"student": "Mizure", "student_almost": "Aarav", "student_done": "Diya"}

ALMOST_PROFILE = {
    "name": "Aarav", "age": 16, "class_or_education": "Class 11, CBSE",
    "location": "Kolkata, West Bengal", "interests": ["debating", "reading newspapers"],
    "strengths": ["public speaking"], "careers_considering": ["civil services", "teaching"],
    "goals": "Become an IAS officer", "challenges": "Does not know how to start",
    "guidance_needed": "A study roadmap", "constraints": "none",
}
DONE_PROFILE = {
    "name": "Diya", "age": 17, "class_or_education": "Class 12, science",
    "location": "Pune, Maharashtra", "interests": ["coding small games"],
    "strengths": ["problem solving"], "careers_considering": ["software engineering"],
    "goals": "Build useful apps", "challenges": "Unsure which college path to take",
    "guidance_needed": "Help choosing a first project", "constraints": "none",
}
DONE_ANALYSIS = {
    "primary_field": "technology", "secondary_fields": ["teaching"], "confidence": "high",
    "summary": "Class 12 student who enjoys coding and wants to build useful apps.",
    "reasoning": "Interests and goals point to software.",
    "mentor_focus": "Choosing and finishing a first project.",
}


def add_missing(db: Session, model, **values) -> None:
    db.execute(insert(model).values(**values).on_conflict_do_nothing())


def seed_people(db: Session) -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)  # fixed order in the directory
    for position, (field, name, rate, bio) in enumerate(MENTORS):
        user_id = seed_id(f"mentor:{field}")
        email = f"{name.lower().replace(' ', '.')}@example.com"
        add_missing(db, User, id=user_id, name=name, role="mentor", email=email,
                    created_at=start + timedelta(minutes=position))
        add_missing(db, MentorProfile, user_id=user_id, field=field, bio=bio,
                    hourly_rate_paise=rate, is_listed=True)
        if db.scalar(select(CommunityPost.id).where(CommunityPost.author_id == user_id).limit(1)) is None:
            topic = FIELD_LABELS[field].lower()
            db.add(CommunityPost(field=field, author_id=user_id,
                                 body=f"Welcome! What would you like to learn about {topic}?"))
    for key, name in STUDENTS.items():
        add_missing(db, User, id=DEMO_USERS[key], name=name, role="student")


def seed_intake(db: Session) -> None:
    rows = [
        ("student_almost", {"status": "confirming", "profile": ALMOST_PROFILE}),
        ("student_done", {"status": "completed", "profile": DONE_PROFILE,
                          "primary_field": "technology", "analysis": DONE_ANALYSIS}),
    ]
    for key, values in rows:
        user_id = DEMO_USERS[key]
        if db.get(IntakeProfile, user_id) is not None:
            continue
        db.add(IntakeProfile(user_id=user_id, **values))
        summary = ScriptedLLM._summary(values["profile"])
        for role, content in [("assistant", GREETING),
                              ("user", f"I'm {values['profile']['name']}."),
                              ("assistant", summary)]:
            db.add(IntakeMessage(user_id=user_id, role=role, content=content))
            db.flush()


def reset_demo(db: Session) -> None:
    """Only rows belonging to the seeded sample users (auth_subject is null)."""
    students = list(DEMO_USERS[key] for key in STUDENTS)
    mentors = [seed_id(f"mentor:{m[0]}") for m in MENTORS]
    for model in (IntakeMessage, HelperMessage, IntakeProfile):
        db.execute(delete(model).where(model.user_id.in_(students)))
    db.execute(delete(Booking).where(Booking.student_id.in_(students)))
    requests = select(MentorshipRequest.id).where(MentorshipRequest.student_id.in_(students))
    db.execute(delete(ConversationMessage).where(ConversationMessage.request_id.in_(requests)))
    db.execute(delete(MentorshipRequest).where(MentorshipRequest.student_id.in_(students)))
    db.execute(delete(CommunityPost).where(
        or_(CommunityPost.author_id.in_(students), CommunityPost.author_id.in_(mentors))))
    for field, _name, rate, _bio in MENTORS:
        db.execute(update(MentorProfile).where(MentorProfile.user_id == seed_id(f"mentor:{field}"))
                   .values(hourly_rate_paise=rate))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-demo", action="store_true")
    args = parser.parse_args()
    with SessionLocal.begin() as db:
        if args.reset_demo:
            reset_demo(db)
        seed_people(db)
        db.flush()
        seed_intake(db)
    print("Seeded 4 sample mentors and 3 demo students.")


if __name__ == "__main__":
    main()
