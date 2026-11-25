from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import SessionLocal, get_db
from app.errors import ApiError
from app.models import User
from app.security import Identity, JwksCache, get_jwks, verify_token

bearer = HTTPBearer(auto_error=False)

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[Session, Depends(get_db)]


@dataclass(frozen=True)
class CurrentUser:
    """Plain data, not an ORM object, so it outlives the database session."""

    id: uuid.UUID
    name: str
    role: str


def find_user(identity: Identity) -> CurrentUser | None:
    # Own short session: chat endpoints must not hold a connection while the AI replies.
    column = User.auth_subject if identity.kind == "supabase" else User.id
    with SessionLocal() as db:
        user = db.scalar(select(User).where(column == identity.subject))
        if user is None or (identity.kind == "demo" and user.auth_subject is not None):
            return None
        return CurrentUser(id=user.id, name=user.name, role=user.role)


def get_identity(
    settings: SettingsDep,
    jwks: Annotated[JwksCache, Depends(get_jwks)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Identity:
    if credentials is None:
        raise ApiError(401, "unauthorized", "Please log in.")
    return verify_token(credentials.credentials, settings, jwks)


IdentityDep = Annotated[Identity, Depends(get_identity)]


def get_current_user(identity: IdentityDep) -> CurrentUser:
    user = find_user(identity)
    if user is None:
        if identity.kind == "demo":
            raise ApiError(401, "unauthorized", "This demo account no longer exists.")
        raise ApiError(403, "onboarding_required", "Finish creating your account first.")
    return user


UserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_student(user: UserDep) -> CurrentUser:
    if user.role != "student":
        raise ApiError(403, "students_only", "This is available to students only.")
    return user


def require_mentor(user: UserDep) -> CurrentUser:
    if user.role != "mentor":
        raise ApiError(403, "mentors_only", "This is available to mentors only.")
    return user


StudentDep = Annotated[CurrentUser, Depends(require_student)]
MentorDep = Annotated[CurrentUser, Depends(require_mentor)]
