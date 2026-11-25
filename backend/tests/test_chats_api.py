import threading

from conftest import FULL, FakeLLM, auth, make_mentor, make_user, use_llm
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.config import Settings, get_settings
from app.db import SessionLocal, engine
from app.main import app
from app.models import HelperMessage, IntakeMessage, IntakeProfile
from app.services.intake.llm import get_llm
from app.services.intake.scripted import ScriptedLLM

DONE = {"user_confirmed_summary": True}


def count(model) -> int:
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(model))


def say(client, user, text):
    return client.post("/api/intake/messages", json={"text": text}, headers=auth(user))


def complete(client, user, **extra):
    use_llm(FakeLLM([{**FULL, **extra}, DONE]))
    say(client, user, "everything")
    assert say(client, user, "yes").json()["done"]


def test_start_twice_stores_one_greeting(client):
    user = make_user()
    use_llm(FakeLLM())
    assert client.get("/api/intake", headers=auth(user)).json()["status"] == "not_started"
    client.post("/api/intake/start", headers=auth(user))
    body = client.post("/api/intake/start", headers=auth(user)).json()
    assert body["status"] == "in_progress" and len(body["messages"]) == 1


def test_no_database_connection_is_held_during_ai_calls(client):
    user = make_user()
    llm = use_llm(FakeLLM([FULL, DONE]))
    seen = []
    llm.before_call = lambda: seen.append(engine.pool.checkedout())
    say(client, user, "everything")
    say(client, user, "yes")
    client.post("/api/helper/messages", json={"text": "hi"}, headers=auth(user))
    assert len(seen) >= 6 and set(seen) == {0}


def test_concurrent_sends_one_wins(client):
    user = make_user()
    llm = use_llm(FakeLLM())
    started, finish = threading.Event(), threading.Event()

    def block():
        started.set()
        finish.wait(10)

    llm.before_call = block
    results = []
    thread = threading.Thread(target=lambda: results.append(say(TestClient(app), user, "one")))
    thread.start()
    assert started.wait(10)
    second = say(client, user, "two")
    deleted = client.delete("/api/intake", headers=auth(user))
    busy = client.get("/api/intake", headers=auth(user)).json()
    finish.set()
    thread.join(10)
    assert results[0].status_code == 200
    assert second.status_code == 409 and second.json()["detail"]["code"] == "intake_busy"
    assert deleted.status_code == 409
    assert busy["busy"] and not busy["can_retry"]
    texts = [m["content"] for m in client.get("/api/intake", headers=auth(user)).json()["messages"]]
    assert "two" not in texts
    llm.before_call = lambda: None
    assert say(client, user, "three").status_code == 200  # the lease was released


def test_failed_reply_can_be_retried(client):
    user = make_user()
    use_llm(FakeLLM()).fail_reply = 1
    assert say(client, user, "hello").json()["error"]
    assert client.get("/api/intake", headers=auth(user)).json()["can_retry"]
    assert not say(client, user, "hello").json()["error"]
    body = client.get("/api/intake", headers=auth(user)).json()
    assert not body["can_retry"] and len(body["messages"]) == 3


def test_missing_key_returns_503_and_stores_nothing(client):
    user = make_user()
    for response in (client.post("/api/intake/start", headers=auth(user)), say(client, user, "hi")):
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "ai_unavailable"
    assert count(IntakeProfile) == 0 and count(IntakeMessage) == 0
    assert client.get("/api/mentors").status_code == 200
    assert client.get("/api/config").json()["ai_available"] is False


def test_validation_and_roles(client):
    student, mentor = make_user(), make_mentor()
    use_llm(FakeLLM())
    assert say(client, student, "   ").status_code == 422
    assert say(client, student, "x" * 2001).status_code == 422
    assert say(client, mentor, "hi").status_code == 403
    assert client.get("/api/intake").status_code == 401
    other = make_user(name="Other")
    say(client, student, "private words")
    assert client.get("/api/intake", headers=auth(other)).json()["messages"] == []


def test_retake_clears_both_chats(client):
    user = make_user()
    complete(client, user)
    client.post("/api/helper/messages", json={"text": "hi"}, headers=auth(user))
    assert count(HelperMessage) == 2
    assert client.delete("/api/intake", headers=auth(user)).status_code == 204
    assert (count(IntakeProfile), count(IntakeMessage), count(HelperMessage)) == (0, 0, 0)


def test_helper_needs_completed_intake_and_gets_safe_context(client):
    user = make_user()
    make_mentor()
    llm = use_llm(FakeLLM())
    r = client.post("/api/helper/messages", json={"text": "hi"}, headers=auth(user))
    assert r.status_code == 409 and r.json()["detail"]["code"] == "intake_incomplete"
    complete(client, user, needs_human_followup=True)
    llm = use_llm(FakeLLM())
    r = client.post("/api/helper/messages", json={"text": "What next?"}, headers=auth(user))
    assert [m["role"] for m in r.json()["messages"]] == ["user", "assistant"]
    assert "Aarav" in llm.last_system and "Ananya Rao" in llm.last_system
    for private in ("followup", "UPSC foundation", "Interests match"):
        assert private not in llm.last_system


def test_failed_helper_reply_stores_nothing(client):
    user = make_user()
    complete(client, user)
    use_llm(FakeLLM()).fail_reply = 1
    r = client.post("/api/helper/messages", json={"text": "hi"}, headers=auth(user))
    assert r.status_code == 502 and count(HelperMessage) == 0


def test_student_responses_never_include_private_analysis(client):
    user = make_user()
    complete(client, user, needs_human_followup=True)
    for path in ("/api/dashboard", "/api/intake", "/api/helper/messages", "/api/me"):
        body = client.get(path, headers=auth(user)).text
        for private in ("followup", "UPSC foundation", "Interests match"):
            assert private not in body, path


def test_dashboard_for_fields_without_mentors(client):
    user = make_user()
    make_mentor("Meera Iyer", "teaching")
    make_mentor("Arjun Shah", "technology")
    use_llm(FakeLLM([FULL, DONE], route={"primary_field": "medical", "secondary_fields": ["teaching"]}))
    say(client, user, "everything")
    say(client, user, "yes")
    body = client.get("/api/dashboard", headers=auth(user)).json()
    assert body["field_label"] == "Medical" and body["field_has_mentors"] is False
    assert [m["name"] for m in body["suggested_mentors"]] == ["Meera Iyer"]
    assert len(body["roadmap"]) == 3


def test_scripted_guide_completes_a_whole_intake(client):
    """AI_MODE=demo must work end to end without any key."""
    user = make_user()
    make_mentor("Arjun Shah", "technology")
    app.dependency_overrides[get_settings] = lambda: Settings(ai_mode="demo")
    assert type(get_llm(Settings(ai_mode="demo"))) is ScriptedLLM
    client.post("/api/intake/start", headers=auth(user))
    answers = ["My name is Tara", "not telling", "I am 16", "Class 11", "Jaipur, Rajasthan",
               "coding and chess", "maths", "software engineer", "Build useful apps",
               "Where to start", "A study plan", "none"]
    for answer in answers:
        reply = say(client, user, answer).json()
        assert not reply["error"] and not reply["done"]
    assert "Tara" in reply["reply"] and "right" in reply["reply"]
    final = say(client, user, "yes").json()
    assert final["done"] and final["redirect_url"] == "/dashboard"
    body = client.get("/api/dashboard", headers=auth(user)).json()
    assert body["field"] == "technology" and body["field_has_mentors"]
    helper = client.post("/api/helper/messages", json={"text": "Which mentor?"}, headers=auth(user))
    assert "Arjun Shah" in helper.json()["messages"][-1]["content"]
