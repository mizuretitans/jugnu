"""PostgreSQL storage for the chats.

Every method opens and closes its own short transaction, so no database
connection is held while waiting for the AI.
"""
from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from app.models import HelperMessage, IntakeMessage, IntakeProfile

LEASE = timedelta(seconds=120)

# Never shown to the student or to the helper chatbot.
PRIVATE_KEYS = {"needs_human_followup"}


def clean(value: Any) -> Any:
    """PostgreSQL cannot store NUL characters in text or JSONB."""
    if isinstance(value, str):
        return value.replace("\x00", "")
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, dict):
        return {clean(k): clean(v) for k, v in value.items()}
    return value


class SqlProfileStore:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session = session_factory

    # ------------------------------------------------------------ messages
    def add_message(self, user_id: uuid.UUID, role: str, content: str) -> None:
        with self._session.begin() as db:
            db.add(IntakeMessage(user_id=user_id, role=role, content=clean(content)))

    def get_messages(self, user_id: uuid.UUID) -> List[Dict[str, str]]:
        with self._session() as db:
            rows = db.execute(
                select(IntakeMessage.role, IntakeMessage.content)
                .where(IntakeMessage.user_id == user_id)
                .order_by(IntakeMessage.id)
            ).all()
        return [{"role": r.role, "content": r.content} for r in rows]

    # ------------------------------------------------------------ profiles
    def get_record(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        with self._session() as db:
            row = db.get(IntakeProfile, user_id)
            if row is None:
                return None
            busy = db.scalar(
                select(IntakeProfile.busy_until > func.now()).where(IntakeProfile.user_id == user_id)
            )
            return {
                "status": row.status,
                "phase_turns": row.phase_turns,
                "route_failures": row.route_failures,
                "profile": row.profile,
                "primary_field": row.primary_field,
                "analysis": row.analysis,
                "needs_human_followup": row.needs_human_followup,
                "busy": bool(busy),
            }

    def ensure_started(self, user_id: uuid.UUID, greeting: str) -> None:
        """Create the profile and store the greeting exactly once, even if called twice."""
        with self._session.begin() as db:
            created = db.scalar(
                insert(IntakeProfile)
                .values(user_id=user_id)
                .on_conflict_do_nothing(index_elements=["user_id"])
                .returning(IntakeProfile.user_id)
            )
            if created is not None:
                db.add(IntakeMessage(user_id=user_id, role="assistant", content=greeting))

    def save_profile(
        self,
        user_id: uuid.UUID,
        profile: Dict[str, Any],
        status: str,
        phase_turns: int = 0,
        route_failures: int = 0,
        primary_field: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
    ) -> None:
        values = {
            "status": status,
            "phase_turns": phase_turns,
            "route_failures": route_failures,
            "profile": clean(profile),
            "primary_field": primary_field,
            "analysis": clean(analysis),
            "needs_human_followup": profile.get("needs_human_followup") is True,
        }
        statement = insert(IntakeProfile).values(user_id=user_id, **values)
        new = statement.excluded
        with self._session.begin() as db:
            db.execute(
                statement.on_conflict_do_update(
                    index_elements=["user_id"],
                    set_={
                        "status": new.status,
                        "phase_turns": new.phase_turns,
                        "route_failures": new.route_failures,
                        "profile": new.profile,
                        "primary_field": func.coalesce(
                            new.primary_field, IntakeProfile.primary_field
                        ),
                        "analysis": func.coalesce(new.analysis, IntakeProfile.analysis),
                        "needs_human_followup": new.needs_human_followup,
                        "updated_at": func.now(),
                    },
                )
            )

    # --------------------------------------------------------------- lease
    def acquire(self, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        """Claim the student's chat for one turn. None means another turn is running."""
        token = uuid.uuid4()
        with self._session.begin() as db:
            claimed = db.scalar(
                update(IntakeProfile)
                .where(
                    IntakeProfile.user_id == user_id,
                    or_(
                        IntakeProfile.busy_until.is_(None),
                        IntakeProfile.busy_until < func.now(),
                    ),
                )
                .values(busy_token=token, busy_until=func.now() + LEASE)
                .returning(IntakeProfile.user_id)
            )
        return token if claimed is not None else None

    def release(self, user_id: uuid.UUID, token: uuid.UUID) -> None:
        with self._session.begin() as db:
            db.execute(
                update(IntakeProfile)
                .where(IntakeProfile.user_id == user_id, IntakeProfile.busy_token == token)
                .values(busy_token=None, busy_until=None)
            )

    # ------------------------------------------------------ helper chatbot
    def get_student_context(self, user_id: uuid.UUID) -> str:
        """Readable text block for the helper chatbot's system prompt."""
        record = self.get_record(user_id)
        if record is None:
            return ""
        lines = ["STUDENT PROFILE (collected in the intake chat)"]
        for key, value in record["profile"].items():
            if key in PRIVATE_KEYS or value in (None, "", []):
                continue
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            lines.append(f"- {key.replace('_', ' ').capitalize()}: {value}")
        analysis = record["analysis"] or {}
        if record["primary_field"]:
            lines.append(
                f"- Best-fit field: {record['primary_field'].replace('_', ' ')} "
                f"(confidence: {analysis.get('confidence', 'unknown')})"
            )
        if analysis.get("secondary_fields"):
            lines.append("- Other fields to explore: " + ", ".join(analysis["secondary_fields"]))
        if analysis.get("summary"):
            lines.append(f"- Summary: {analysis['summary']}")
        return "\n".join(lines)

    def get_helper_messages(self, user_id: uuid.UUID, limit: int) -> List[Dict[str, str]]:
        with self._session() as db:
            rows = db.execute(
                select(HelperMessage.role, HelperMessage.content)
                .where(HelperMessage.user_id == user_id)
                .order_by(HelperMessage.id.desc())
                .limit(limit)
            ).all()
        return [{"role": r.role, "content": r.content} for r in reversed(rows)]

    def add_helper_exchange(self, user_id: uuid.UUID, question: str, answer: str) -> None:
        with self._session.begin() as db:
            db.add(HelperMessage(user_id=user_id, role="user", content=clean(question)))
            db.flush()
            db.add(HelperMessage(user_id=user_id, role="assistant", content=clean(answer)))

    # ------------------------------------------------------------- privacy
    def delete_user_data(self, user_id: uuid.UUID) -> bool:
        """Delete both chats and the profile. False if a chat turn is running."""
        with self._session.begin() as db:
            row = db.scalar(
                select(IntakeProfile).where(IntakeProfile.user_id == user_id).with_for_update()
            )
            if row is not None and row.busy_until is not None:
                if db.scalar(select(func.now() < row.busy_until)):
                    return False
            for model in (IntakeMessage, HelperMessage, IntakeProfile):
                db.execute(delete(model).where(model.user_id == user_id))
        return True
