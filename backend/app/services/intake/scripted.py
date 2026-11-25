"""Scripted stand-in for the AI (AI_MODE=demo), so the app runs without an API key.

It is not intelligent: it fills the profile one topic at a time, in order. It keeps
no state and works everything out from the prompt it is given. The UI labels it
"Demo guide".
"""
from __future__ import annotations

import json
import re
from typing import Any

from app.services.intake import engine
from app.services.intake.llm import LLM, parse_json_object

QUESTIONS = {
    "name": "First, what should I call you?",
    "age": "How old are you?",
    "class_or_education": "Which class or course are you in right now?",
    "location": "Which city and state do you live in?",
    "interests": "What do you enjoy doing in your free time?",
    "strengths": "What do people say you are good at?",
    "careers_considering": "Which careers have you thought about so far?",
    "goals": "What would you love to achieve in the future?",
    "challenges": "What confuses or worries you about your future?",
    "guidance_needed": "What kind of help would you like from a mentor?",
    "constraints": "Is there anything that limits your choices, like family, money or location?",
}

KEYWORDS = {
    "civil_services": ("upsc", "ias", "ips", "civil service", "government", "current affairs"),
    "defense": ("army", "navy", "air force", "nda", "cds", "defence", "defense", "police"),
    "teaching": ("teach", "teacher", "professor", "education"),
    "technology": ("code", "coding", "software", "engineer", "computer", "technology", "robot"),
    "medical": ("doctor", "medical", "medicine", "nurse", "neet", "hospital"),
    "business": ("business", "finance", "commerce", "startup", "accountant", "marketing"),
    "creative": ("design", "art", "music", "writing", "film", "media", "draw"),
}

YES = re.compile(
    r"\b(yes|yeah|yep|correct|right|perfect|ok|okay|sure|haan|han|sahi)\b|हाँ|हां|হ্যাঁ", re.IGNORECASE
)


def _between(text: str, start: str, end: str) -> str:
    _, found, rest = text.partition(start)
    return rest.partition(end)[0].strip() if found else ""


class ScriptedLLM(LLM):
    # ---- chat replies
    def reply(self, system: str, messages: list[dict[str, str]]) -> str:
        if system.startswith("HELPER CHATBOT"):
            return self._helper(system, messages)
        profile = parse_json_object(
            _between(system, "WHAT YOU ALREADY KNOW ABOUT THE STUDENT:\n", "\n\n")
        )
        name = profile.get("name", "")
        if "The chat is finished." in system:
            return (
                f"Thank you{', ' + name if name else ''}! I enjoyed getting to know you. I'm taking you "
                "to your personal dashboard now, where a mentor and your own guide are waiting."
            )
        if engine.CONFIRMING_RULES in system:
            return self._summary(profile)
        todo = _between(system, "STILL TO LEARN (most important first):\n", "\n\n")
        for key, topic in engine.REQUIRED_TOPICS.items():
            if f"- {topic}" in todo.splitlines():
                return f"Thanks{', ' + name if name else ''}! {QUESTIONS[key]}"
        return "Thanks! Is there anything else you would like to tell me?"

    @staticmethod
    def _summary(profile: dict[str, Any]) -> str:
        lines = ["Here is what I learned about you:"]
        for key in engine.REQUIRED_TOPICS:
            value = profile.get(key)
            if value not in (None, "", []):
                shown = ", ".join(value) if isinstance(value, list) else value
                lines.append(f"- {key.replace('_', ' ').capitalize()}: {shown}")
        return "\n".join(lines) + "\n\nIs this right, or would you like to change anything?"

    @staticmethod
    def _helper(system: str, messages: list[dict[str, str]]) -> str:
        question = messages[-1]["content"].lower() if messages else ""
        if "mentor" in question:
            return "These mentors are on Jugnu:\n" + _between(system, "MENTORS ON JUGNU:\n", "\n\n")
        return "Here is a good way to move forward:\n" + _between(system, "ROADMAP:\n", "\n\n")

    # ---- structured output
    def extract_json(self, system: str, user_text: str) -> dict[str, Any]:
        if system == engine.ROUTE_SYSTEM:
            return self._route(user_text)
        answer = user_text.rpartition("\nStudent: ")[2]
        answer = answer.removesuffix("\n\nReturn the JSON object now.").strip()
        if "The guide has just summarised" in user_text:
            return {"user_confirmed_summary": bool(YES.search(answer))}
        profile = parse_json_object(
            _between(user_text, "Current profile (JSON):\n", "\n\nConversation:")
        )
        missing = engine.missing_fields(profile)
        return {missing[0]: self._value(missing[0], answer)} if missing else {}

    @staticmethod
    def _value(key: str, answer: str) -> Any:
        kind = engine.PROFILE_SPEC[key][0]
        if kind == "integer":
            digits = re.search(r"\d+", answer)
            return int(digits.group()) if digits else None
        if kind == "list":
            return [part.strip() for part in re.split(r",|\band\b|\n", answer) if part.strip()]
        if key == "name":
            prefix = r"^(hi|hello|hey)?[,!. ]*(i am|i'm|my name is|call me|this is)?\s*"
            return re.sub(prefix, "", answer, flags=re.IGNORECASE).strip(" .!")[:60]
        return answer

    @staticmethod
    def _route(user_text: str) -> dict[str, Any]:
        profile = parse_json_object(
            _between(user_text, "STUDENT PROFILE (JSON):\n", "\n\nCONVERSATION:")
        )
        text = json.dumps(profile, ensure_ascii=False).lower()
        scores = {
            field: sum(1 for word in words if re.search(rf"\b{re.escape(word)}", text))
            for field, words in KEYWORDS.items()
        }
        ranked = [f for f in sorted(scores, key=lambda f: -scores[f]) if scores[f]]
        return {
            "primary_field": ranked[0] if ranked else "undecided",
            "secondary_fields": ranked[1:3],
            "confidence": "low",
            "summary": f"{profile.get('name', 'The student')} wants: {profile.get('goals', 'not stated')}",
            "reasoning": "Keyword match (demo mode).",
            "mentor_focus": str(profile.get("guidance_needed", "")),
        }
