"""Request and response models for every endpoint."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.schemas.common import (
    Bio, Body, ChatText, In, MentorField, Minutes, Name, Out, Role, Topic,
)

RateRupees = Annotated[int, Field(strict=True, ge=1, le=100_000)]


# ---------------------------------------------------------------- config/auth
class FieldOut(Out):
    key: str
    label: str


class ConfigOut(Out):
    ai_mode: Literal["openrouter", "demo"]
    ai_available: bool
    demo_login: bool
    supabase_url: str
    supabase_publishable_key: str
    mentor_fields: list[FieldOut]
    community_fields: list[FieldOut]


class HealthOut(Out):
    status: Literal["ok"]


class DemoIn(In):
    account: Literal["student", "student_almost", "student_done", "mentor"]


class TokenOut(Out):
    access_token: str


class UserOut(Out):
    id: uuid.UUID
    name: str
    role: Role


class MeOut(Out):
    status: Literal["active", "onboarding_required"]
    user: UserOut | None = None
    suggested_name: str = ""


class OnboardingIn(In):
    role: Role
    name: Name
    field: MentorField | None = None
    bio: Bio | None = None
    hourly_rate_rupees: RateRupees | None = None

    @model_validator(mode="after")
    def _mentor_details(self) -> OnboardingIn:
        details = (self.field, self.bio, self.hourly_rate_rupees)
        if self.role == "mentor" and any(d is None for d in details):
            raise ValueError("Mentors need a field, a short introduction and an hourly rate")
        if self.role == "student" and any(d is not None for d in details):
            raise ValueError("Students do not have mentor details")
        return self


# -------------------------------------------------------------------- mentors
class MentorOut(Out):
    id: uuid.UUID
    name: str
    field: str
    field_label: str
    bio: str
    hourly_rate_paise: int


class OwnMentorOut(MentorOut):
    is_listed: bool


class RateIn(In):
    hourly_rate_rupees: RateRupees


# ------------------------------------------------------- requests & messages
class PersonOut(Out):
    id: uuid.UUID
    name: str


class RequestOut(Out):
    id: uuid.UUID
    status: Literal["pending", "accepted"]
    student: PersonOut
    mentor: PersonOut
    created_at: datetime


class MessageIn(In):
    body: Body


class MessageOut(Out):
    id: int
    sender_name: str
    mine: bool
    body: str
    created_at: datetime


class ConversationOut(Out):
    request: RequestOut
    messages: list[MessageOut]


class StudentBriefOut(Out):
    name: str
    field_label: str | None
    summary: str
    goals: str
    guidance_needed: str
    interests: list[str]
    strengths: list[str]
    mentor_focus: str
    needs_human_followup: bool


class PostIn(In):
    body: Body


class PostOut(Out):
    id: int
    author_name: str
    author_role: Role
    body: str
    created_at: datetime


# ------------------------------------------------------------------- bookings
class BookingIn(In):
    idempotency_key: uuid.UUID
    mentor_id: uuid.UUID
    minutes: Minutes
    topic: Topic
    expected_rate_paise: int


class BookingOut(Out):
    id: uuid.UUID
    student: PersonOut
    mentor: PersonOut
    request_id: uuid.UUID | None
    hourly_rate_paise: int
    minutes: int
    total_paise: int
    topic: str
    status: Literal["pending", "confirmed"]
    created_at: datetime


# --------------------------------------------------------------------- chats
class ChatIn(In):
    text: ChatText


class ChatMessageOut(Out):
    role: Literal["user", "assistant"]
    content: str


class IntakeOut(Out):
    status: Literal["not_started", "in_progress", "confirming", "ready_to_route", "completed"]
    busy: bool = False
    can_retry: bool = False
    messages: list[ChatMessageOut] = []


class TurnOut(Out):
    reply: str
    done: bool
    error: bool
    redirect_url: str | None


class HelperOut(Out):
    messages: list[ChatMessageOut]


class CareerPathOut(Out):
    id: str
    title: str
    category: str
    streams: list[str]
    route: str
    overview: str


class CareerHistoryMessage(In):
    role: Literal["user", "assistant"]
    content: ChatText


class CareerExplorerIn(In):
    career_id: Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-z0-9_]+$")]
    history: list[CareerHistoryMessage] = Field(default_factory=list, max_length=12)
    text: ChatText


class CareerExplorerOut(Out):
    reply: str


# ------------------------------------------------------------------ dashboard
class RoadmapStep(Out):
    title: str
    text: str


class DashboardOut(Out):
    role: Role
    field: str | None
    field_label: str | None
    roadmap: list[RoadmapStep]
    # students
    intake_status: str | None = None
    secondary_labels: list[str] = []
    field_has_mentors: bool = False
    suggested_mentors: list[MentorOut] = []
    # mentors
    mentor: OwnMentorOut | None = None
    requests: list[RequestOut]
    bookings: list[BookingOut]
