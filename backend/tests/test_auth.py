import time
import uuid

import httpx
import jwt
import pytest
from conftest import PRIVATE_KEY, auth, jwks_document, make_user, supabase_token
from cryptography.hazmat.primitives.asymmetric import ec
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.main import app
from app.security import JwksCache, create_demo_token, get_jwks


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def me(client, token):
    return client.get("/api/me", headers=bearer(token))


def test_new_google_user_onboards_once(client):
    subject = uuid.uuid4()
    token = supabase_token(subject)
    body = me(client, token).json()
    assert body == {"status": "onboarding_required", "user": None, "suggested_name": "Some One"}
    blocked = client.get("/api/dashboard", headers=bearer(token))
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "onboarding_required"

    created = client.post("/api/me/onboarding", json={"role": "student", "name": "Asha"}, headers=bearer(token))
    assert created.status_code == 201
    assert me(client, token).json()["user"]["role"] == "student"
    again = client.post("/api/me/onboarding", headers=bearer(token),
                        json={"role": "mentor", "name": "Asha", "field": "teaching",
                              "bio": "I teach physics.", "hourly_rate_rupees": 500})
    assert again.status_code == 409
    assert me(client, token).json()["user"]["role"] == "student"


def test_new_mentor_is_hidden_until_approved(client):
    token = supabase_token()
    r = client.post("/api/me/onboarding", headers=bearer(token),
                    json={"role": "mentor", "name": "Dr Sen", "field": "medical",
                          "bio": "I help with medical careers.", "hourly_rate_rupees": 700})
    mentor_id = r.json()["user"]["id"]
    assert client.get("/api/mentors").json() == []
    assert client.get(f"/api/mentors/{mentor_id}").status_code == 404
    student = make_user()
    assert client.post(f"/api/mentors/{mentor_id}/requests", headers=auth(student)).status_code == 404
    own = client.get("/api/dashboard", headers=bearer(token)).json()["mentor"]
    assert own["is_listed"] is False and own["hourly_rate_paise"] == 70000


@pytest.mark.parametrize("payload", [
    {"role": "mentor", "name": "X"},
    {"role": "student", "name": "X", "field": "teaching"},
    {"role": "admin", "name": "X"},
    {"role": "student", "name": "   "},
    {"role": "student", "name": "X", "is_listed": True},
    {"role": "mentor", "name": "X", "field": "undecided", "bio": "Ten letters.", "hourly_rate_rupees": 5},
    {"role": "mentor", "name": "X", "field": "teaching", "bio": "Ten letters.", "hourly_rate_rupees": 100001},
])
def test_onboarding_validation(client, payload):
    r = client.post("/api/me/onboarding", json=payload, headers=bearer(supabase_token()))
    assert r.status_code == 422


@pytest.mark.parametrize("token", [
    lambda: supabase_token(exp=int(time.time()) - 600),
    lambda: supabase_token(iss="https://evil.supabase.co/auth/v1"),
    lambda: supabase_token(aud="anon"),
    lambda: supabase_token(aud=None),
    lambda: supabase_token(exp=None),
    lambda: supabase_token(role="anon"),
    lambda: supabase_token(is_anonymous=True),
    lambda: supabase_token(subject="not-a-uuid"),
    lambda: supabase_token(key=ec.generate_private_key(ec.SECP256R1())),
    lambda: supabase_token(kid="unknown"),
    lambda: supabase_token(key="x" * 40, alg="HS256"),
    lambda: supabase_token(iss="jugnu-demo"),
    lambda: "garbage",
])
def test_bad_tokens_are_rejected(client, token):
    assert me(client, token()).status_code == 401


def test_unsigned_token_is_rejected(client):
    claims = jwt.decode(supabase_token(), options={"verify_signature": False})
    assert me(client, jwt.encode(claims, None, algorithm="none", headers={"kid": "test-key"})).status_code == 401


def test_role_in_token_metadata_is_ignored(client):
    subject = uuid.uuid4()
    make_user("student", auth_subject=subject)
    token = supabase_token(subject, user_metadata={"role": "mentor"}, app_metadata={"role": "mentor"})
    assert me(client, token).json()["user"]["role"] == "student"
    r = client.patch("/api/mentor/rate", json={"hourly_rate_rupees": 5}, headers=bearer(token))
    assert r.status_code == 403


def test_same_email_does_not_link_accounts(client):
    first = supabase_token(email="same@example.com")
    client.post("/api/me/onboarding", json={"role": "student", "name": "One"}, headers=bearer(first))
    assert me(client, supabase_token(email="same@example.com")).json()["status"] == "onboarding_required"


def test_demo_login_is_off_by_default(client):
    user = make_user()
    token = create_demo_token(user, get_settings())
    assert me(client, token).status_code == 200
    app.dependency_overrides[get_settings] = lambda: Settings(demo_login=False)
    assert me(client, token).status_code == 401
    assert client.post("/api/auth/demo", json={"account": "student"}).status_code == 404
    assert Settings.model_fields["demo_login"].default is False


def test_demo_token_cannot_act_as_a_real_account(client):
    user = make_user(auth_subject=uuid.uuid4())
    assert me(client, create_demo_token(user, get_settings())).status_code == 401


def test_unreachable_supabase_is_503_not_401(client):
    def down():
        raise httpx.ConnectError("down")

    app.dependency_overrides[get_jwks] = lambda: JwksCache(down)
    assert me(client, supabase_token()).status_code == 503


def test_unknown_key_ids_do_not_cause_a_fetch_each_time():
    calls = []
    cache = JwksCache(lambda: calls.append(1) or jwks_document())
    for _ in range(50):
        assert cache.get("nope") is None
    assert cache.get("test-key").key.public_numbers() == PRIVATE_KEY.public_key().public_numbers()
    assert len(calls) == 1


def test_settings_refuse_unsafe_values():
    with pytest.raises(ValidationError):
        Settings(supabase_publishable_key="sb_secret_abc")
    with pytest.raises(ValidationError):
        Settings(demo_login=True, demo_jwt_secret="short")
    assert Settings(supabase_url="https://x.supabase.co/").supabase_url == "https://x.supabase.co"


def test_config_exposes_no_secrets(client):
    body = client.get("/api/config").text
    assert get_settings().demo_jwt_secret.get_secret_value() not in body
    assert "password" not in body.lower()
