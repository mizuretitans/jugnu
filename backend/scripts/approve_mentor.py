"""Approve new mentors. Mentors stay hidden from students until approved.

    python -m scripts.approve_mentor                list mentors waiting for approval
    python -m scripts.approve_mentor <mentor id>    approve one
    python -m scripts.approve_mentor <id> --hide    hide one again
"""
import argparse
import sys
import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import SessionLocal
from app.models import MentorProfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mentor_id", nargs="?", type=uuid.UUID)
    parser.add_argument("--hide", action="store_true")
    args = parser.parse_args()
    with SessionLocal.begin() as db:
        query = select(MentorProfile).options(joinedload(MentorProfile.user))
        if args.mentor_id is None:
            waiting = db.scalars(query.where(MentorProfile.is_listed.is_(False))).all()
            for m in waiting:
                print(f"{m.user_id}  {m.user.name}  {m.user.email or '-'}  {m.field}\n    {m.bio}")
            print(f"{len(waiting)} waiting")
            return 0
        mentor = db.scalar(query.where(MentorProfile.user_id == args.mentor_id))
        if mentor is None:
            print("No mentor with that id.")
            return 1
        mentor.is_listed = not args.hide
        print(f"{mentor.user.name} is now {'hidden' if args.hide else 'listed'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
