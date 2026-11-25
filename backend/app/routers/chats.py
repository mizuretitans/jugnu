"""Intake and helper chatbots.

These endpoints deliberately do not use DbDep: an AI call can take many seconds
and must not hold a database connection.
"""
from fastapi import APIRouter, Response

from app.db import SessionLocal
from app.deps import CurrentUser, StudentDep
from app.errors import ApiError
from app.schemas.api import ChatIn, HelperOut, IntakeOut, TurnOut
from app.services.helper import ask_helper
from app.services.intake.engine import GREETING, IntakeSession
from app.services.intake.llm import LlmDep
from app.services.intake.store import SqlProfileStore

router = APIRouter(tags=["chatbots"])
store = SqlProfileStore(SessionLocal)

HELPER_PAGE = 100


def _busy() -> ApiError:
    return ApiError(409, "intake_busy", "Your guide is still replying. Please wait a moment.")


def _intake_out(user: CurrentUser) -> IntakeOut:
    record = store.get_record(user.id)
    if record is None:
        return IntakeOut(status="not_started")
    messages = store.get_messages(user.id)
    unanswered = bool(messages) and messages[-1]["role"] == "user"
    return IntakeOut(
        status=record["status"],
        busy=record["busy"],
        can_retry=unanswered and not record["busy"] and record["status"] != "completed",
        messages=messages,
    )


@router.get("/intake")
def get_intake(user: StudentDep) -> IntakeOut:
    return _intake_out(user)


@router.post("/intake/start")
def start_intake(user: StudentDep, llm: LlmDep) -> IntakeOut:
    store.ensure_started(user.id, GREETING)
    return _intake_out(user)


@router.post("/intake/messages")
def send_intake(data: ChatIn, user: StudentDep, llm: LlmDep) -> TurnOut:
    store.ensure_started(user.id, GREETING)
    token = store.acquire(user.id)
    if token is None:
        raise _busy()
    try:
        # Built only after the lease is held, because it reads the stored state.
        result = IntakeSession(user.id, store, llm).send(data.text)
    finally:
        store.release(user.id, token)
    return TurnOut(
        reply=result.reply, done=result.done, error=result.error, redirect_url=result.redirect_url
    )


@router.delete("/intake", status_code=204)
def restart_intake(user: StudentDep) -> Response:
    """Delete the student's chats and profile so they can start again."""
    if not store.delete_user_data(user.id):
        raise _busy()
    return Response(status_code=204)


def _completed_field(user: CurrentUser) -> str | None:
    record = store.get_record(user.id)
    if record is None or record["status"] != "completed":
        raise ApiError(409, "intake_incomplete", "Finish the career guide first.")
    return record["primary_field"]


def _helper_out(user: CurrentUser) -> HelperOut:
    return HelperOut(messages=store.get_helper_messages(user.id, HELPER_PAGE))


@router.get("/helper/messages")
def get_helper(user: StudentDep) -> HelperOut:
    _completed_field(user)
    return _helper_out(user)


@router.post("/helper/messages")
def send_helper(data: ChatIn, user: StudentDep, llm: LlmDep) -> HelperOut:
    field = _completed_field(user)
    ask_helper(store, llm, user.id, field, data.text)
    return _helper_out(user)
