"""Tests run real migrations against a real PostgreSQL database named *_test."""
import os

# Must be set before the app is imported. Environment variables win over backend/.env.
os.environ.update(
    DB_NAME="jugnu_test",
    SUPABASE_URL="https://test-project.supabase.co",
    SUPABASE_PUBLISHABLE_KEY="sb_publishable_test",
    DEMO_LOGIN="true",
    DEMO_JWT_SECRET="test-only-secret-test-only-secret-123",
    AI_MODE="openrouter",
    OPENROUTER_API_KEY="",
)

import json  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402

import jwt  # noqa: E402
import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.config import BACKEND_DIR, get_settings  # noqa: E402
from app.db import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, MentorProfile, User  # noqa: E402
from app.security import JwksCache, create_demo_token, get_jwks  # noqa: E402
from app.services.intake.llm import LLM, get_llm  # noqa: E402

logging.getLogger("jugnu").setLevel(logging.CRITICAL)

KID = "test-key"
PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())


def jwks_document() -> dict:
    jwk = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(PRIVATE_KEY.public_key()))
    return {"keys": [{**jwk, "kid": KID, "alg": "ES256", "use": "sig"}]}


def supabase_token(subject=None, *, key=PRIVATE_KEY, kid=KID, alg="ES256", **overrides) -> str:
    claims = {
        "iss": "https://test-project.supabase.co/auth/v1",
        "aud": "authenticated",
        "role": "authenticated",
        "sub": str(subject or uuid.uuid4()),
        "exp": int(time.time()) + 3600,
        "email": "Someone@Example.com",
        "is_anonymous": False,
        "user_metadata": {"full_name": "Some One"},
        **overrides,
    }
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, key, algorithm=alg, headers={"kid": kid})


@pytest.fixture(scope="session", autouse=True)
def database():
    assert engine.url.database.endswith("_test"), "refusing to touch a non-test database"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    command.upgrade(config, "head")
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(database):
    names = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    app.dependency_overrides[get_jwks] = lambda: JwksCache(jwks_document)
    return TestClient(app)


def make_user(role="student", name="Asha", auth_subject=None) -> uuid.UUID:
    with SessionLocal.begin() as db:
        user = User(name=name, role=role, auth_subject=auth_subject)
        db.add(user)
        db.flush()
        return user.id


def make_mentor(name="Ananya Rao", field="civil_services", rate=60000, listed=True) -> uuid.UUID:
    user_id = make_user("mentor", name)
    with SessionLocal.begin() as db:
        db.add(MentorProfile(user_id=user_id, field=field, bio="Builds reading routines.",
                             hourly_rate_paise=rate, is_listed=listed))
    return user_id


def auth(user_id: uuid.UUID) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_demo_token(user_id, get_settings())}"}


FULL = {
    "name": "Aarav", "age": 15, "class_or_education": "Class 10, CBSE",
    "location": "Kolkata, West Bengal", "interests": ["debating", "reading newspapers"],
    "strengths": ["public speaking"], "careers_considering": ["civil services", "teaching"],
    "goals": "Become an IAS officer", "challenges": "Does not know how to start",
    "guidance_needed": "A study roadmap", "constraints": "none",
}
ROUTE = {
    "primary_field": "civil_services", "secondary_fields": ["teaching"], "confidence": "high",
    "summary": "Debater who follows current affairs.", "reasoning": "Interests match.",
    "mentor_focus": "UPSC foundation",
}


class FakeLLM(LLM):
    def __init__(self, extractions=(), route=ROUTE):
        self.extractions, self.route = list(extractions), route
        self.fail_reply = self.fail_route = self.fail_extract = 0
        self.reply_calls = 0
        self.last_system, self.last_messages = "", []
        self.before_call = lambda: None

    def reply(self, system, messages):
        self.before_call()
        if self.fail_reply > 0:
            self.fail_reply -= 1
            raise RuntimeError("down")
        self.reply_calls += 1
        self.last_system, self.last_messages = system, messages
        return f"bot reply {self.reply_calls}"

    def extract_json(self, system, user_text):
        self.before_call()
        if "primary_field" in system:
            if self.fail_route > 0:
                self.fail_route -= 1
                raise RuntimeError("down")
            return self.route
        if self.fail_extract > 0:
            self.fail_extract -= 1
            raise RuntimeError("down")
        return self.extractions.pop(0) if self.extractions else {}


def use_llm(llm: LLM) -> LLM:
    app.dependency_overrides[get_llm] = lambda: llm
    return llm
