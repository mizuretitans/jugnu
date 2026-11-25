from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

engine = create_engine(get_settings().database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Request-scoped session for ordinary endpoints.

    Chat endpoints must NOT use this: it would hold a pooled connection while
    waiting for the AI. They use SqlProfileStore, which opens one short
    transaction per operation.
    """
    with SessionLocal() as session:
        yield session
