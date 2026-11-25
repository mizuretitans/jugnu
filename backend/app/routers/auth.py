from fastapi import APIRouter
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.deps import DbDep, IdentityDep, SettingsDep, find_user
from app.domain.demo import DEMO_USERS
from app.domain.fields import COMMUNITY_FIELDS, FIELD_LABELS, MENTOR_FIELDS
from app.errors import ApiError, not_found
from app.models import MentorProfile, User
from app.schemas.api import (
    ConfigOut, DemoIn, FieldOut, HealthOut, MeOut, OnboardingIn, TokenOut, UserOut,
)
from app.security import create_demo_token

router = APIRouter(tags=["account"])


@router.get("/health")
def health(db: DbDep) -> HealthOut:
    db.execute(text("SELECT 1"))
    return HealthOut(status="ok")


@router.get("/config")
def config(settings: SettingsDep) -> ConfigOut:
    """Public settings the browser needs. Nothing here is secret."""
    return ConfigOut(
        ai_mode=settings.ai_mode,
        ai_available=settings.ai_mode == "demo" or bool(settings.openrouter_api_key.get_secret_value()),
        demo_login=settings.demo_login,
        supabase_url=settings.supabase_url,
        supabase_publishable_key=settings.supabase_publishable_key,
        mentor_fields=[FieldOut(key=k, label=FIELD_LABELS[k]) for k in MENTOR_FIELDS],
        community_fields=[FieldOut(key=k, label=FIELD_LABELS[k]) for k in COMMUNITY_FIELDS],
    )


@router.post("/auth/demo")
def demo_login(data: DemoIn, settings: SettingsDep, db: DbDep) -> TokenOut:
    if not settings.demo_login:
        raise not_found()
    user_id = DEMO_USERS[data.account]
    if db.scalar(select(User.id).where(User.id == user_id, User.auth_subject.is_(None))) is None:
        raise ApiError(
            409, "not_seeded", "Demo accounts are missing. Run: python -m scripts.seed"
        )
    return TokenOut(access_token=create_demo_token(user_id, settings))


@router.get("/me")
def me(identity: IdentityDep) -> MeOut:
    user = find_user(identity)
    if user is not None:
        return MeOut(status="active", user=UserOut.model_validate(user))
    if identity.kind == "demo":
        raise ApiError(401, "unauthorized", "This demo account no longer exists.")
    return MeOut(status="onboarding_required", suggested_name=identity.suggested_name)


@router.post("/me/onboarding", status_code=201)
def onboarding(data: OnboardingIn, identity: IdentityDep, db: DbDep) -> MeOut:
    """First login: choose student or mentor. The role cannot be changed afterwards."""
    if identity.kind != "supabase":
        raise ApiError(403, "not_allowed", "Demo accounts are already set up.")
    user = User(
        auth_subject=identity.subject, email=identity.email, name=data.name, role=data.role
    )
    if data.role == "mentor":
        user.mentor_profile = MentorProfile(
            field=data.field, bio=data.bio, hourly_rate_paise=data.hourly_rate_rupees * 100
        )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # auth_subject is unique, so this account already exists.
        db.rollback()
        raise ApiError(409, "already_onboarded", "Your account is already set up.") from None
    return MeOut(status="active", user=UserOut.model_validate(user))
