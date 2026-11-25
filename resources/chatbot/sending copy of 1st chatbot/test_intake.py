"""Offline tests: no API key or internet needed.  Run:  python -m unittest -v"""
import os
import tempfile
import unittest

import logging

import intake_chatbot as ic
from profile_store import ProfileStore

logging.disable(logging.CRITICAL)  # the bot logs expected failures; keep test output clean

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


class FakeLLM(ic.LLM):
    def __init__(self, extractions=(), route=ROUTE):
        self.extractions, self.route = list(extractions), route
        self.fail_reply = self.fail_route = self.fail_extract = 0
        self.reply_calls = 0
        self.last_system, self.last_messages = "", []

    def reply(self, system, messages):
        if self.fail_reply > 0:
            self.fail_reply -= 1
            raise RuntimeError("down")
        self.reply_calls += 1
        self.last_system, self.last_messages = system, messages
        return f"bot reply {self.reply_calls}"

    def extract_json(self, system, user_text):
        if "primary_field" in system:
            if self.fail_route > 0:
                self.fail_route -= 1
                raise RuntimeError("down")
            return self.route
        if self.fail_extract > 0:
            self.fail_extract -= 1
            raise RuntimeError("down")
        return self.extractions.pop(0) if self.extractions else {}


class IntakeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = ProfileStore(os.path.join(tmp.name, "test.db"))

    def session(self, llm, user="u1"):
        return ic.IntakeSession(user, self.store, llm)

    def test_full_flow(self):
        llm = FakeLLM([{"name": "Aarav", "age": 15}, {k: v for k, v in FULL.items() if k not in ("name", "age")},
                       {"user_confirmed_summary": True}])
        s = self.session(llm)
        self.assertIn("what should I call you", s.opening_message())
        r1 = s.send("Hi, I'm Aarav, 15")
        self.assertFalse(r1.done)
        self.assertIn("STILL TO LEARN", llm.last_system)
        r2 = s.send("long answer with everything")
        self.assertEqual(s.status, "confirming")
        self.assertIn("short, friendly summary", llm.last_system)
        r3 = s.send("yes, all correct")
        self.assertTrue(r3.done)
        self.assertEqual(r3.redirect_url, "/dashboard/civil_services/u1")
        rec = self.store.get_record("u1")
        self.assertEqual(rec["status"], "completed")
        self.assertEqual(rec["primary_field"], "civil_services")
        self.assertEqual(rec["profile"]["name"], "Aarav")
        calls = llm.reply_calls
        r4 = s.send("hello again")
        self.assertTrue(r4.done)
        self.assertEqual(llm.reply_calls, calls)  # no extra model call after completion
        self.assertEqual(r1.reply, "bot reply 1")
        self.assertEqual(r2.reply, "bot reply 2")

    def test_merge_rules(self):
        p = ic.merge_profile({}, {"interests": ["Cricket"], "age": "15", "needs_human_followup": True, "bogus": 1})
        p = ic.merge_profile(p, {"interests": ["cricket", "chess"], "age": 400, "needs_human_followup": False})
        self.assertEqual(p["interests"], ["Cricket", "chess"])
        self.assertEqual(p["age"], 15)
        self.assertTrue(p["needs_human_followup"])
        self.assertNotIn("bogus", p)
        p = ic.merge_profile({"careers_considering": ["not sure yet"]}, {"careers_considering": ["defense"]})
        self.assertEqual(p["careers_considering"], ["defense"])
        p = ic.merge_profile(p, {"goals": "  ", "constraints": None, "location": "Pune"})
        self.assertNotIn("goals", p)
        self.assertNotIn("constraints", p)
        self.assertEqual(p["location"], "Pune")

    def test_resume_after_closing_browser(self):
        llm = FakeLLM([{"name": "Aarav"}])
        s = self.session(llm)
        s.opening_message()
        s.send("I'm Aarav")
        s2 = self.session(FakeLLM(), "u1")
        self.assertEqual(s2.profile["name"], "Aarav")
        self.assertIn("Welcome back", s2.opening_message())
        self.assertEqual(len(s2.history()), 3)

    def test_invalid_field_becomes_undecided(self):
        llm = FakeLLM([FULL, {"user_confirmed_summary": True}], route={"primary_field": "astronaut", "confidence": "??"})
        s = self.session(llm)
        s.send("everything")
        r = s.send("yes")
        self.assertTrue(r.done)
        self.assertEqual(r.redirect_url, "/dashboard/undecided/u1")
        self.assertEqual(self.store.get_record("u1")["analysis"]["confidence"], "low")

    def test_extraction_failure_does_not_crash(self):
        llm = FakeLLM()
        llm.fail_extract = 1
        r = self.session(llm).send("hello")
        self.assertFalse(r.error)
        self.assertEqual(r.reply, "bot reply 1")

    def test_reply_failure_is_reported_and_not_stored(self):
        llm = FakeLLM()
        llm.fail_reply = 1
        s = self.session(llm)
        r = s.send("hello")
        self.assertTrue(r.error)
        self.assertEqual([m["role"] for m in s.history()], ["user"])
        r = s.send("are you there?")
        self.assertFalse(r.error)
        api = ic.to_api_messages(s.history())
        self.assertEqual([m["role"] for m in api], ["user", "assistant"])  # two user messages merged into one
        self.assertIn("hello", api[0]["content"])
        self.assertIn("are you there?", api[0]["content"])

    def test_routing_failure_retries_then_completes(self):
        llm = FakeLLM([FULL, {"user_confirmed_summary": True}])
        llm.fail_route = 1
        s = self.session(llm)
        s.send("everything")
        r = s.send("yes")
        self.assertTrue(r.error)
        self.assertFalse(r.done)
        self.assertEqual(self.store.get_record("u1")["status"], "ready_to_route")
        r = s.send("ok")
        self.assertTrue(r.done)

    def test_confirm_never_loops_forever(self):
        llm = FakeLLM([FULL])
        s = self.session(llm)
        s.send("everything")
        s.send("hmm")
        s.send("well")
        r = s.send("what")
        self.assertTrue(r.done)

    def test_turn_cap_forces_wrap_up(self):
        llm = FakeLLM()
        s = self.session(llm)
        for _ in range(ic.MAX_STUDENT_TURNS):
            s.send("ok")
        self.assertEqual(s.status, "confirming")

    def test_api_messages_shape(self):
        msgs = ic.to_api_messages([{"role": "assistant", "content": "hi"}, {"role": "user", "content": "a"},
                                   {"role": "user", "content": "b"}])
        self.assertEqual([m["role"] for m in msgs], ["user", "assistant", "user"])
        self.assertEqual(msgs[2]["content"], "a\n\nb")

    def test_json_parsing_and_url_quoting(self):
        self.assertEqual(ic.parse_json_object('Sure!\n```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(ic.parse_json_object("not json"), {})
        llm = FakeLLM([FULL, {"user_confirmed_summary": True}])
        s = self.session(llm, "a b/c")
        s.send("x")
        self.assertEqual(s.send("yes").redirect_url, "/dashboard/civil_services/a%20b%2Fc")

    def test_helper_context_and_delete(self):
        llm = FakeLLM([FULL, {"user_confirmed_summary": True}])
        s = self.session(llm)
        s.send("x")
        s.send("yes")
        ctx = self.store.get_student_context("u1")
        self.assertIn("Name: Aarav", ctx)
        self.assertIn("Best-fit field: civil services", ctx)
        self.assertIn("Student:", self.store.get_student_context("u1", include_transcript=True))
        self.store.delete_user_data("u1")
        self.assertIsNone(self.store.get_record("u1"))
        self.assertEqual(self.store.get_student_context("u1"), "")

    def test_unicode_roundtrip(self):
        llm = FakeLLM([{"name": "आरव", "interests": ["ক্রিকেট"]}])
        s = self.session(llm)
        s.send("मेरा नाम आरव है")
        self.assertEqual(self.store.get_record("u1")["profile"]["name"], "आरव")
        self.assertEqual(s.history()[0]["content"], "मेरा नाम आरव है")


if __name__ == "__main__":
    unittest.main()
