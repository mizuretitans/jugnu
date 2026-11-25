import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.deps import CurrentUser
from app.errors import not_found
from app.models import ConversationMessage, MentorshipRequest
from app.schemas.api import MessageOut

MESSAGE_LIMIT = 200


def _with_people():
    return select(MentorshipRequest).options(
        joinedload(MentorshipRequest.student), joinedload(MentorshipRequest.mentor)
    )


def own_requests(db: Session, user: CurrentUser) -> list[MentorshipRequest]:
    column = (
        MentorshipRequest.mentor_id if user.role == "mentor" else MentorshipRequest.student_id
    )
    return list(
        db.scalars(_with_people().where(column == user.id).order_by(MentorshipRequest.created_at))
    )


def load_request(db: Session, request_id: uuid.UUID) -> MentorshipRequest:
    return db.scalars(
        _with_people()
        .where(MentorshipRequest.id == request_id)
        .execution_options(populate_existing=True)
    ).one()


def create_request(db: Session, student_id: uuid.UUID, mentor_id: uuid.UUID) -> MentorshipRequest:
    """One request per student and mentor; asking again returns the existing one."""
    db.execute(
        insert(MentorshipRequest)
        .values(student_id=student_id, mentor_id=mentor_id)
        .on_conflict_do_nothing(index_elements=["student_id", "mentor_id"])
    )
    db.commit()
    return db.scalars(
        _with_people().where(
            MentorshipRequest.student_id == student_id, MentorshipRequest.mentor_id == mentor_id
        )
    ).one()


def ensure_accepted(db: Session, student_id: uuid.UUID, mentor_id: uuid.UUID) -> uuid.UUID:
    """Create or accept the conversation for this pair. The caller commits."""
    statement = insert(MentorshipRequest).values(
        student_id=student_id, mentor_id=mentor_id, status="accepted", accepted_at=func.now()
    )
    return db.execute(
        statement.on_conflict_do_update(
            index_elements=["student_id", "mentor_id"],
            set_={
                "status": "accepted",
                "accepted_at": func.coalesce(MentorshipRequest.accepted_at, func.now()),
            },
        ).returning(MentorshipRequest.id)
    ).scalar_one()


def get_conversation(db: Session, request_id: uuid.UUID, user: CurrentUser) -> MentorshipRequest:
    """Only participants of an accepted request. Everyone else gets the same 404."""
    request = db.scalar(
        _with_people().where(
            MentorshipRequest.id == request_id,
            MentorshipRequest.status == "accepted",
            or_(MentorshipRequest.student_id == user.id, MentorshipRequest.mentor_id == user.id),
        )
    )
    if request is None:
        raise not_found("This conversation is not available.")
    return request


def latest_messages(db: Session, request_id: uuid.UUID, user: CurrentUser) -> list[MessageOut]:
    rows = db.scalars(
        select(ConversationMessage)
        .options(joinedload(ConversationMessage.sender))
        .where(ConversationMessage.request_id == request_id)
        .order_by(ConversationMessage.id.desc())
        .limit(MESSAGE_LIMIT)
    ).all()
    return [message_out(row, user) for row in reversed(rows)]


def message_out(row: ConversationMessage, user: CurrentUser) -> MessageOut:
    return MessageOut(
        id=row.id,
        sender_name=row.sender.name,
        mine=row.sender_id == user.id,
        body=row.body,
        created_at=row.created_at,
    )
