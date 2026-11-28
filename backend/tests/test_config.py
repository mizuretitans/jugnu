import pytest
from pydantic import ValidationError

from app.config import Settings
from app.db import engine


def settings(**values: object) -> Settings:
    return Settings(_env_file=None, **values)


def test_no_sslmode_by_default() -> None:
    assert settings().database_url().query == {}


def test_sslmode_is_passed_to_the_driver() -> None:
    url = settings(db_sslmode="require").database_url()
    assert url.query == {"sslmode": "require"}
    assert url.render_as_string(hide_password=True).endswith("?sslmode=require")


def test_unknown_sslmode_is_rejected() -> None:
    with pytest.raises(ValidationError):
        settings(db_sslmode="yes")


def test_engine_never_prepares_statements() -> None:
    # Transaction poolers (Neon, Supabase) break with server-side prepared statements.
    with engine.connect() as connection:
        assert connection.connection.driver_connection.prepare_threshold is None
