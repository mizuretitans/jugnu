"""Create the app and test databases if they do not exist.  Run: python -m scripts.create_db"""
import psycopg
from psycopg import sql

from app.config import get_settings


def main() -> None:
    s = get_settings()
    with psycopg.connect(
        host=s.db_host, port=s.db_port, user=s.db_user,
        password=s.db_password.get_secret_value() or None, dbname="postgres", autocommit=True,
    ) as conn:
        for name in (s.db_name, f"{s.db_name}_test"):
            if conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
                print(f"{name}: already exists")
                continue
            conn.execute(
                sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0").format(
                    sql.Identifier(name)
                )
            )
            print(f"{name}: created")


if __name__ == "__main__":
    main()
