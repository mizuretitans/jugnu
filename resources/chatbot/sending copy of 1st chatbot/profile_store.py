"""SQLite storage for the intake chatbot (Python standard library only).

Everything the first chatbot learns lives in ONE database file
(default: mentor_platform.db) with two tables:

  messages - the full chat transcript, one row per message
  profiles - one row per student: structured profile, status, chosen field,
             analysis summary and the dashboard URL

The dashboard and the second (helper) chatbot read from the same tables.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

DEFAULT_DB_PATH = "mentor_platform.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages (user_id, id);

CREATE TABLE IF NOT EXISTS profiles (
    user_id        TEXT PRIMARY KEY,
    status         TEXT NOT NULL DEFAULT 'in_progress',
    phase_turns    INTEGER NOT NULL DEFAULT 0,
    profile_json   TEXT NOT NULL DEFAULT '{}',
    primary_field  TEXT,
    analysis_json  TEXT,
    dashboard_url  TEXT,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ProfileStore:
    def __init__(self, path: str = DEFAULT_DB_PATH) -> None:
        self.path = path
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------ messages
    def add_message(self, user_id: str, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (user_id, role, content, created_at) "
                "VALUES (?, ?, ?, ?)",
                (user_id, role, content, _now()),
            )

    def get_messages(self, user_id: str) -> List[Dict[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE user_id = ? ORDER BY id",
                (user_id,),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    # ------------------------------------------------------------ profiles
    def get_record(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
            ).fetchone()
        if row is None:
            return None
        return {
            "user_id": row["user_id"],
            "status": row["status"],
            "phase_turns": row["phase_turns"],
            "profile": json.loads(row["profile_json"] or "{}"),
            "primary_field": row["primary_field"],
            "analysis": json.loads(row["analysis_json"]) if row["analysis_json"] else None,
            "dashboard_url": row["dashboard_url"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def save_profile(
        self,
        user_id: str,
        profile: Dict[str, Any],
        status: str,
        phase_turns: int = 0,
        primary_field: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
        dashboard_url: Optional[str] = None,
    ) -> None:
        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO profiles (user_id, status, phase_turns, profile_json,
                                      primary_field, analysis_json, dashboard_url,
                                      created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    status        = excluded.status,
                    phase_turns   = excluded.phase_turns,
                    profile_json  = excluded.profile_json,
                    primary_field = COALESCE(excluded.primary_field, profiles.primary_field),
                    analysis_json = COALESCE(excluded.analysis_json, profiles.analysis_json),
                    dashboard_url = COALESCE(excluded.dashboard_url, profiles.dashboard_url),
                    updated_at    = excluded.updated_at
                """,
                (
                    user_id,
                    status,
                    phase_turns,
                    json.dumps(profile, ensure_ascii=False),
                    primary_field,
                    json.dumps(analysis, ensure_ascii=False) if analysis else None,
                    dashboard_url,
                    now,
                    now,
                ),
            )

    # -------------------------------------------- for the dashboard / bot 2
    def get_student_context(self, user_id: str, include_transcript: bool = False) -> str:
        """Readable text block to put in the SECOND chatbot's system prompt."""
        record = self.get_record(user_id)
        if record is None:
            return ""
        lines = ["STUDENT PROFILE (collected in the intake chat)"]
        for key, value in record["profile"].items():
            if value in (None, "", []):
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
        if analysis.get("mentor_focus"):
            lines.append(f"- Mentor should focus on: {analysis['mentor_focus']}")
        if include_transcript:
            lines.append("\nORIGINAL INTAKE CONVERSATION")
            for m in self.get_messages(user_id):
                who = "Student" if m["role"] == "user" else "Guide"
                lines.append(f"{who}: {m['content']}")
        return "\n".join(lines)

    # ------------------------------------------------------------- privacy
    def delete_user_data(self, user_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
