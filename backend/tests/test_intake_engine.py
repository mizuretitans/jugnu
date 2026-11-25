"""The prototype's 13 intake tests, ported to PostgreSQL, plus fixes made while porting."""
import pytest
from conftest import FULL, FakeLLM, make_user

from app.db import SessionLocal
from app.services.intake import engine as ic
from app.services.intake.llm import parse_json_object
from app.services.intake.store import SqlProfileStore

store = SqlProfileStore(SessionLocal)
DONE = {"user_confirmed_summary": True}


@pytest.fixture
def user():
    return make_user()


def session(llm, user):
    store.ensure_started(user, ic.GREETING)
    return ic.IntakeSession(user, store, llm)


# ------------------------------------------------------------ ported tests
def test_full_flow(user):
    llm = FakeLLM([{"name": "Aarav", "age": 15},
                   {k: v for k, v in FULL.items() if k not in ("name", "age")}, DONE])
    s = session(llm, user)
    assert "what should I call you" in s.history()[0]["content"]
    r1 = s.send("Hi, I'm Aarav, 15")
    assert not r1.done and "STILL TO LEARN" in llm.last_system
    r2 = s.send("long answer with everything")
    assert s.status == "confirming" and "short, friendly summary" in llm.last_system
    r3 = s.send("yes, all correct")
    assert r3.done and r3.redirect_url == "/dashboard"
    rec = store.get_record(user)
    assert (rec["status"], rec["primary_field"]) == ("completed", "civil_services")
    assert rec["profile"]["name"] == "Aarav"
    calls = llm.reply_calls
    assert s.send("hello again").done
    assert llm.reply_calls == calls  # no extra model call after completion
    assert (r1.reply, r2.reply) == ("bot reply 1", "bot reply 2")


def test_merge_rules():
    p = ic.merge_profile({}, {"interests": ["Cricket"], "age": "15", "needs_human_followup": True, "bogus": 1})
    p = ic.merge_profile(p, {"interests": ["cricket", "chess"], "age": 400, "needs_human_followup": False})
    assert p["interests"] == ["Cricket", "chess"]
    assert p["age"] == 15
    assert p["needs_human_followup"] is True
    assert "bogus" not in p
    p = ic.merge_profile({"careers_considering": ["not sure yet"]}, {"careers_considering": ["defense"]})
    assert p["careers_considering"] == ["defense"]
    p = ic.merge_profile(p, {"goals": "  ", "constraints": None, "location": "Pune"})
    assert "goals" not in p and "constraints" not in p and p["location"] == "Pune"


def test_resume_after_closing_browser(user):
    session(FakeLLM([{"name": "Aarav"}]), user).send("I'm Aarav")
    s2 = session(FakeLLM(), user)
    assert s2.profile["name"] == "Aarav"
    assert len(s2.history()) == 3


def test_invalid_field_becomes_undecided(user):
    s = session(FakeLLM([FULL, DONE], route={"primary_field": "astronaut", "confidence": "??"}), user)
    s.send("everything")
    assert s.send("yes").done
    rec = store.get_record(user)
    assert rec["primary_field"] == "undecided" and rec["analysis"]["confidence"] == "low"


def test_extraction_failure_does_not_crash(user):
    llm = FakeLLM()
    llm.fail_extract = 1
    r = session(llm, user).send("hello")
    assert not r.error and r.reply == "bot reply 1"


def test_reply_failure_is_reported_and_not_stored(user):
    llm = FakeLLM()
    llm.fail_reply = 1
    s = session(llm, user)
    assert s.send("hello").error
    assert [m["role"] for m in s.history()] == ["assistant", "user"]
    assert not s.send("are you there?").error
    api = ic.to_api_messages(s.history())
    merged = [m for m in api if "hello" in m["content"]]
    assert len(merged) == 1 and "are you there?" in merged[0]["content"]


def test_routing_failure_retries_then_completes(user):
    llm = FakeLLM([FULL, DONE])
    llm.fail_route = 1
    s = session(llm, user)
    s.send("everything")
    r = s.send("yes")
    assert r.error and not r.done
    assert store.get_record(user)["status"] == "ready_to_route"
    assert s.send("ok").done


def test_confirm_never_loops_forever(user):
    s = session(FakeLLM([FULL]), user)
    for text in ("everything", "hmm", "well"):
        s.send(text)
    assert s.send("what").done


def test_turn_cap_forces_wrap_up(user):
    s = session(FakeLLM(), user)
    for _ in range(ic.MAX_STUDENT_TURNS):
        s.send("ok")
    assert s.status == "confirming"


def test_api_messages_shape():
    msgs = ic.to_api_messages([{"role": "assistant", "content": "hi"}, {"role": "user", "content": "a"},
                               {"role": "user", "content": "b"}])
    assert [m["role"] for m in msgs] == ["user", "assistant", "user"]
    assert msgs[2]["content"] == "a\n\nb"


def test_json_parsing():
    assert parse_json_object('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json_object("not json") == {}


def test_helper_context_and_delete(user):
    s = session(FakeLLM([{**FULL, "needs_human_followup": True}, DONE]), user)
    s.send("x")
    s.send("yes")
    context = store.get_student_context(user)
    assert "Name: Aarav" in context and "Best-fit field: civil services" in context
    # private to mentors and the team
    assert "followup" not in context.lower() and "UPSC foundation" not in context
    assert store.get_record(user)["needs_human_followup"] is True
    assert store.delete_user_data(user)
    assert store.get_record(user) is None and store.get_student_context(user) == ""


def test_unicode_roundtrip(user):
    s = session(FakeLLM([{"name": "आरव", "interests": ["ক্রিকেট"]}]), user)
    s.send("मेरा नाम आरव है")
    assert store.get_record(user)["profile"] == {"name": "आरव", "interests": ["ক্রিকেট"]}
    assert s.history()[1]["content"] == "मेरा नाम आरव है"


# ---------------------------------------------------- fixes made in the port
def test_third_routing_failure_completes_across_rebuilt_sessions(user):
    """The prototype kept this counter in memory, so a web student could get stuck forever."""
    llm = FakeLLM([FULL, DONE])
    llm.fail_route = 99
    session(llm, user).send("everything")
    assert session(llm, user).send("yes").error
    assert session(llm, user).send("ok").error
    r = session(llm, user).send("hello?")
    assert r.done
    rec = store.get_record(user)
    assert rec["primary_field"] == "undecided" and "mentor should review" in rec["analysis"]["summary"]


def test_resending_after_failure_is_not_stored_twice(user):
    llm = FakeLLM()
    llm.fail_reply = 2
    for _ in range(3):
        session(llm, user).send("same text")
    assert [m["role"] for m in store.get_messages(user)] == ["assistant", "user", "assistant"]


def test_unseen_summary_cannot_be_confirmed(user):
    llm = FakeLLM([FULL, DONE, DONE])
    llm.fail_reply = 1
    s = session(llm, user)
    assert s.send("everything").error  # the summary failed to send
    r = session(llm, user).send("yes")
    assert not r.done
    assert session(llm, user).send("yes, right").done


def test_saving_without_analysis_keeps_the_old_one(user):
    store.save_profile(user, FULL, "completed", primary_field="teaching", analysis={"summary": "s"})
    store.save_profile(user, FULL, "completed")
    rec = store.get_record(user)
    assert rec["analysis"] == {"summary": "s"} and rec["primary_field"] == "teaching"


def test_nul_characters_from_the_model_do_not_break_storage(user):
    session(FakeLLM([{"name": "A\x00sha", "interests": ["x\x00y"]}]), user).send("hi")
    assert store.get_record(user)["profile"] == {"name": "Asha", "interests": ["xy"]}
