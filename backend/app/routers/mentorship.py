import uuid

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.deps import DbDep, MentorDep, UserDep
from app.domain.fields import FIELD_LABELS
from app.errors import not_found
from app.models import CommunityPost, ConversationMessage, IntakeProfile, MentorshipRequest
from app.schemas.api import (
    ConversationOut, MessageIn, MessageOut, PostIn, PostOut, RequestOut, StudentBriefOut,
)
from app.schemas.common import CommunityField
from app.services.requests import (
    MESSAGE_LIMIT, get_conversation, latest_messages, load_request, message_out, own_requests,
)

router = APIRouter(tags=["mentorship"])


@router.get("/requests")
def requests(user: UserDep, db: DbDep) -> list[RequestOut]:
    return [RequestOut.model_validate(r) for r in own_requests(db, user)]


@router.post("/requests/{request_id}/accept")
def accept(request_id: uuid.UUID, user: MentorDep, db: DbDep) -> RequestOut:
    request = db.scalar(
        select(MentorshipRequest)
        .where(MentorshipRequest.id == request_id, MentorshipRequest.mentor_id == user.id)
        .with_for_update()
    )
    if request is None:
        raise not_found("Request not found.")
    if request.status == "pending":
        request.status = "accepted"
        request.accepted_at = func.now()
    db.commit()
    return RequestOut.model_validate(load_request(db, request_id))


@router.get("/requests/{request_id}/messages")
def conversation(request_id: uuid.UUID, user: UserDep, db: DbDep) -> ConversationOut:
    request = get_conversation(db, request_id, user)
    return ConversationOut(
        request=RequestOut.model_validate(request),
        messages=latest_messages(db, request_id, user),
    )


@router.post("/requests/{request_id}/messages", status_code=201)
def send_message(request_id: uuid.UUID, data: MessageIn, user: UserDep, db: DbDep) -> MessageOut:
    get_conversation(db, request_id, user)
    row = ConversationMessage(request_id=request_id, sender_id=user.id, body=data.body)
    db.add(row)
    db.commit()
    return message_out(row, user)


@router.get("/requests/{request_id}/student-brief")
def student_brief(request_id: uuid.UUID, user: MentorDep, db: DbDep) -> StudentBriefOut:
    """What an accepted mentor may see from the student's intake chat."""
    request = get_conversation(db, request_id, user)
    intake = db.get(IntakeProfile, request.student_id)
    if intake is None or intake.status != "completed":
        raise not_found("This student has not finished the career guide yet.")
    profile, analysis = intake.profile, intake.analysis or {}
    return StudentBriefOut(
        name=request.student.name,
        field_label=FIELD_LABELS.get(intake.primary_field or ""),
        summary=analysis.get("summary", ""),
        goals=profile.get("goals", ""),
        guidance_needed=profile.get("guidance_needed", ""),
        interests=profile.get("interests", []),
        strengths=profile.get("strengths", []),
        mentor_focus=analysis.get("mentor_focus", ""),
        needs_human_followup=intake.needs_human_followup,
    )


def _post_out(post: CommunityPost) -> PostOut:
    return PostOut(
        id=post.id,
        author_name=post.author.name,
        author_role=post.author.role,
        body=post.body,
        created_at=post.created_at,
    )


@router.get("/community/{field}/posts")
def posts(field: CommunityField, db: DbDep) -> list[PostOut]:
    rows = db.scalars(
        select(CommunityPost)
        .options(joinedload(CommunityPost.author))
        .where(CommunityPost.field == field)
        .order_by(CommunityPost.id.desc())
        .limit(MESSAGE_LIMIT)
    ).all()
    return [_post_out(p) for p in reversed(rows)]


@router.post("/community/{field}/posts", status_code=201)
def create_post(field: CommunityField, data: PostIn, user: UserDep, db: DbDep) -> PostOut:
    post = CommunityPost(field=field, author_id=user.id, body=data.body)
    db.add(post)
    db.commit()
    return _post_out(post)
