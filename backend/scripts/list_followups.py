"""List students the intake chat flagged for a human to check on.

    python -m scripts.list_followups

The flag is set by an AI and can miss students. It is not a safety system.
The output is sensitive: do not share or store it.
"""
from sqlalchemy import select

from app.db import SessionLocal
from app.models import IntakeProfile, User


def main() -> None:
    with SessionLocal() as db:
        rows = db.execute(
            select(User.id, User.name, User.email, IntakeProfile.updated_at)
            .join(IntakeProfile, IntakeProfile.user_id == User.id)
            .where(IntakeProfile.needs_human_followup)
            .order_by(IntakeProfile.updated_at)
        ).all()
    for row in rows:
        print(f"{row.id}  {row.name}  {row.email or '-'}  last chat {row.updated_at:%Y-%m-%d %H:%M}")
    print(f"{len(rows)} flagged")


if __name__ == "__main__":
    main()
