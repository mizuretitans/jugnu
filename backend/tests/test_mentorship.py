import threading
import uuid

import pytest
from conftest import FULL, FakeLLM, auth, make_mentor, make_user, use_llm
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.main import app
from app.models import Booking, MentorProfile, MentorshipRequest


def count(model) -> int:
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(model))


def ask(client, student, mentor):
    return client.post(f"/api/mentors/{mentor}/requests", headers=auth(student)).json()["id"]


def accepted(client, student, mentor):
    request_id = ask(client, student, mentor)
    client.post(f"/api/requests/{request_id}/accept", headers=auth(mentor))
    return request_id


def book(client, student, mentor, **changes):
    payload = {"idempotency_key": str(uuid.uuid4()), "mentor_id": str(mentor), "minutes": 90,
               "topic": "Essay practice", "expected_rate_paise": 60000, **changes}
    return client.post("/api/bookings", json=payload, headers=auth(student))


# ------------------------------------------------------- requests & messages
def test_request_accept_message(client):
    student, mentor = make_user(name="Asha"), make_mentor()
    request_id = ask(client, student, mentor)
    assert ask(client, student, mentor) == request_id  # asking again is harmless
    url = f"/api/requests/{request_id}/messages"
    assert client.get(url, headers=auth(student)).status_code == 404  # pending
    client.post(f"/api/requests/{request_id}/accept", headers=auth(mentor))
    sent = client.post(url, json={"body": " Hello! "}, headers=auth(student)).json()
    assert sent["sender_name"] == "Asha" and sent["mine"] and sent["body"] == "Hello!"
    client.post(url, json={"body": "Welcome"}, headers=auth(mentor))
    seen = client.get(url, headers=auth(mentor)).json()["messages"]
    assert [(m["body"], m["mine"]) for m in seen] == [("Hello!", False), ("Welcome", True)]


def test_access_matrix(client):
    student, mentor = make_user(), make_mentor()
    outsider, other_mentor = make_user(name="Out"), make_mentor("Kabir Singh", "defense")
    request_id = ask(client, student, mentor)
    accept = f"/api/requests/{request_id}/accept"
    assert client.post(accept, headers=auth(other_mentor)).status_code == 404
    assert client.post(accept, headers=auth(student)).status_code == 403
    assert client.post(accept).status_code == 401
    client.post(accept, headers=auth(mentor))
    url = f"/api/requests/{request_id}/messages"
    for who in (outsider, other_mentor):
        assert client.get(url, headers=auth(who)).status_code == 404
        assert client.post(url, json={"body": "hi"}, headers=auth(who)).status_code == 404
        assert client.get("/api/requests", headers=auth(who)).json() == []
    assert client.get(url).status_code == 401
    assert client.post(f"/api/mentors/{mentor}/requests", headers=auth(other_mentor)).status_code == 403
    brief = f"/api/requests/{request_id}/student-brief"
    assert client.get(brief, headers=auth(other_mentor)).status_code == 404
    assert client.get(brief, headers=auth(student)).status_code == 403


@pytest.mark.parametrize("body", ["", "   ", "\x00", "x" * 1501])
def test_message_validation(client, body):
    student, mentor = make_user(), make_mentor()
    url = f"/api/requests/{accepted(client, student, mentor)}/messages"
    assert client.post(url, json={"body": body}, headers=auth(student)).status_code == 422


def test_sender_name_cannot_be_forged(client):
    student, mentor = make_user(), make_mentor()
    url = f"/api/requests/{accepted(client, student, mentor)}/messages"
    r = client.post(url, json={"body": "hi", "sender_name": "Ananya Rao"}, headers=auth(student))
    assert r.status_code == 422


def test_student_brief_only_after_acceptance(client):
    student, mentor = make_user(name="Asha"), make_mentor()
    use_llm(FakeLLM([{**FULL, "needs_human_followup": True}, {"user_confirmed_summary": True}]))
    for text in ("everything", "yes"):
        client.post("/api/intake/messages", json={"text": text}, headers=auth(student))
    request_id = ask(client, student, mentor)
    url = f"/api/requests/{request_id}/student-brief"
    assert client.get(url, headers=auth(mentor)).status_code == 404
    client.post(f"/api/requests/{request_id}/accept", headers=auth(mentor))
    brief = client.get(url, headers=auth(mentor)).json()
    assert brief["goals"] == "Become an IAS officer" and brief["needs_human_followup"] is True
    assert "location" not in brief and "age" not in brief and "constraints" not in brief


def test_community(client):
    student = make_user(name="Asha")
    url = "/api/community/teaching/posts"
    assert client.post(url, json={"body": "hi"}).status_code == 401
    assert client.post(url, json={"body": "Hello all"}, headers=auth(student)).status_code == 201
    assert [p["author_name"] for p in client.get(url).json()] == ["Asha"]
    assert client.get("/api/community/technology/posts").json() == []
    assert client.get("/api/community/medical/posts").status_code == 422


# ------------------------------------------------------------------- bookings
def test_price_is_computed_on_the_server(client):
    student, mentor = make_user(), make_mentor()
    r = book(client, student, mentor)
    assert r.status_code == 201 and r.json()["total_paise"] == 90000
    assert book(client, student, mentor, total_paise=1).status_code == 422
    assert book(client, student, mentor, minutes=45).status_code == 422
    assert book(client, mentor, mentor).status_code == 403
    assert book(client, student, uuid.uuid4()).status_code == 404


def test_stale_rate_is_rejected_and_replay_still_works(client):
    student, mentor = make_user(), make_mentor()
    key = str(uuid.uuid4())
    first = book(client, student, mentor, idempotency_key=key).json()
    client.patch("/api/mentor/rate", json={"hourly_rate_rupees": 750}, headers=auth(mentor))
    stale = book(client, student, mentor)
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "rate_changed"
    assert stale.json()["detail"]["hourly_rate_paise"] == 75000
    assert book(client, student, mentor, idempotency_key=key).json()["id"] == first["id"]
    reused = book(client, student, mentor, idempotency_key=key, minutes=30)
    assert reused.status_code == 409 and reused.json()["detail"]["code"] == "idempotency_conflict"
    assert count(Booking) == 1
    other = make_user(name="Other")  # keys belong to one student
    assert book(client, other, mentor, idempotency_key=key, expected_rate_paise=75000).status_code == 201


def test_double_click_creates_one_booking(client):
    student, mentor, key = make_user(), make_mentor(), str(uuid.uuid4())
    barrier, results = threading.Barrier(5), []

    def go():
        own = TestClient(app)
        barrier.wait()
        results.append(book(own, student, mentor, idempotency_key=key).status_code)

    threads = [threading.Thread(target=go) for _ in range(5)]
    [t.start() for t in threads]
    [t.join(20) for t in threads]
    assert results == [201] * 5 and count(Booking) == 1


@pytest.mark.parametrize("already_requested", [False, True])
def test_confirm_opens_the_conversation_once(client, already_requested):
    student, mentor = make_user(), make_mentor()
    if already_requested:
        ask(client, student, mentor)
    booking = book(client, student, mentor).json()
    url = f"/api/bookings/{booking['id']}/confirm"
    assert client.post(url, headers=auth(make_mentor("Kabir Singh"))).status_code == 404
    assert client.post(url, headers=auth(student)).status_code == 403

    barrier, results = threading.Barrier(2), []

    def go():
        own = TestClient(app)
        barrier.wait()
        results.append(own.post(url, headers=auth(mentor)).json())

    threads = [threading.Thread(target=go) for _ in range(2)]
    [t.start() for t in threads]
    [t.join(20) for t in threads]
    assert {r["status"] for r in results} == {"confirmed"}
    assert results[0]["request_id"] == results[1]["request_id"]
    assert count(MentorshipRequest) == 1
    messages = f"/api/requests/{results[0]['request_id']}/messages"
    assert client.get(messages, headers=auth(student)).status_code == 200


def test_bookings_are_private(client):
    student, mentor = make_user(), make_mentor()
    book(client, student, mentor)
    assert len(client.get("/api/bookings", headers=auth(student)).json()) == 1
    assert len(client.get("/api/bookings", headers=auth(mentor)).json()) == 1
    assert client.get("/api/bookings", headers=auth(make_user(name="Out"))).json() == []


@pytest.mark.parametrize("rate", [0, -5, 100001, 10.5, "600", None, True])
def test_rate_validation(client, rate):
    mentor = make_mentor()
    r = client.patch("/api/mentor/rate", json={"hourly_rate_rupees": rate}, headers=auth(mentor))
    assert r.status_code == 422


def test_database_rejects_wrong_totals_and_rates():
    student, mentor = make_user(), make_mentor()
    with pytest.raises(IntegrityError), SessionLocal.begin() as db:
        db.add(Booking(idempotency_key=uuid.uuid4(), student_id=student, mentor_id=mentor,
                       hourly_rate_paise=60000, minutes=90, total_paise=1, topic="x"))
    with pytest.raises(IntegrityError), SessionLocal.begin() as db:
        db.get(MentorProfile, mentor).hourly_rate_paise = 60050
